#!/usr/bin/env python3
"""Reject private artifacts/credential formats in Git's index and optional history.

Run before committing, and from a local pre-commit hook. Only filenames/rule
labels are printed on failure; matched values are never printed. A successful
scan supplements explicit source-file review, not arbitrary file publication.
"""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

PRIVATE_COMPONENTS = {
    'private', 'build', 'downloads', 'references', 'tools', 'backups',
    '.ssh', '.steam', '.gnupg', '.config', '.local',
    'base-backup', 'native-transition', 'steamapps', 'compatdata',
}
PUBLIC_BACKUP_TOOLS = {'docs/backup.md', 'scripts/backup-base.py'}
ARTIFACT = re.compile(
    r'\.(?:img|dtb|bin|raw|dump|qcow2|vhdx?|vmdk|log|sqsh|cpio|tar|zip|7z|gz|xz|zst|wav|flac|mp3|mp4|mkv|webm|'
    r'png|jpe?g|sqlite(?:3)?|db|dmp|core|bak|backup|pem|key)(?:\.|$)', re.I)
SENSITIVE_NAME = re.compile(
    r'(?:^|[._-])(?:passwords?|credentials?|tokens?|secrets?|backup|backups|'
    r'known_hosts|authorized_keys|id_rsa|id_ed25519)(?:[._-]|$)|\.before-|'
    r'^\.env(?:\.|$)|^edl_config\.json$', re.I)
SECRET_PATTERNS = {
    'private key': re.compile(rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----'),
    'GitHub token': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'AWS access key': re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'OpenAI-style secret': re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}\b'),
    'password hash': re.compile(rb'\$(?:y|6|5)\$[A-Za-z0-9./$]{20,}'),
    'Bluetooth pairing key': re.compile(rb'(?im)^\s*(?:LinkKey|LongTermKey|IRK|LTK|Key)\s*=\s*[A-Fa-f0-9]{32}\s*$'),
    'credential URL': re.compile(rb'https?://[^\s/:@]{2,}:[^\s/@]{4,}@'),
}
LIMIT = 1024 * 1024


def git(*args):
    return subprocess.check_output(['git', *args])


def path_reason(name):
    path = PurePosixPath(name)
    if any(part.lower() in PRIVATE_COMPONENTS for part in path.parts):
        return 'private/artifact directory'
    if name.startswith('docs/x-post-') or name == 'docs/x-handle-sources.json':
        return 'unpublished local draft'
    if ARTIFACT.search(path.name):
        return 'backup/capture/binary artifact extension'
    if name not in PUBLIC_BACKUP_TOOLS and SENSITIVE_NAME.search(path.name):
        return 'sensitive/backup filename'
    return None


def known_secrets(root):
    # Read only explicitly known secret locations; never scan huge backups.
    result = []
    for relative in ['private/native-user-password', 'private/bootstrap/user-password']:
        path = root / relative
        if path.is_file():
            value = path.read_bytes().strip()
            if 6 <= len(value) <= 512:
                result.append(('known local password', value))
    obs = Path.home() / '.config/obs-studio/plugin_config/obs-websocket/config.json'
    if obs.is_file():
        config = json.loads(obs.read_text())
        value = config.get('server_password', '')
        if isinstance(value, str) and len(value) >= 6:
            result.append(('known OBS credential', value.encode()))
    return result


def content_reasons(data, secrets):
    if len(data) > LIMIT:
        return ['oversized source blob']
    if b'\0' in data:
        return ['binary blob in source-only tree']
    try:
        data.decode('utf-8')
    except UnicodeDecodeError:
        return ['non-UTF-8 blob in source-only tree']
    failures = [label for label, pattern in SECRET_PATTERNS.items() if pattern.search(data)]
    failures += [label for label, value in secrets if value in data]
    return failures


def index_records():
    for item in git('ls-files', '--stage', '-z').split(b'\0'):
        if not item:
            continue
        metadata, name = item.split(b'\t', 1)
        mode, oid, stage = metadata.decode().split()
        yield name.decode(), mode, oid, stage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', action='store_true', help='Also audit all reachable historical blobs')
    args = parser.parse_args()
    root = Path(git('rev-parse', '--show-toplevel').decode().strip())
    secrets = known_secrets(root)
    failures = []
    seen = set()
    records = list(index_records())
    for name, mode, oid, stage in records:
        if stage != '0':
            failures.append((name, 'unmerged index'))
        reason = path_reason(name)
        if reason:
            failures.append((name, reason))
            continue
        if mode == '160000':
            if name != 'plugins/controller-control':
                failures.append((name, 'unreviewed submodule'))
            continue
        if mode not in {'100644', '100755'}:
            failures.append((name, 'nonregular file or symlink'))
            continue
        if int(git('cat-file', '-s', oid)) > LIMIT:
            failures.append((name, 'oversized source blob'))
            continue
        data = git('cat-file', 'blob', oid)
        failures.extend((name, reason) for reason in content_reasons(data, secrets))
        seen.add(oid)
    historical = 0
    if args.history:
        for line in git('rev-list', '--objects', '--all').decode().splitlines():
            oid, _, name = line.partition(' ')
            if git('cat-file', '-t', oid).strip() != b'blob':
                continue
            historical += 1
            if name and path_reason(name):
                failures.append((name, 'historical ' + path_reason(name)))
                continue
            if oid in seen:
                continue
            if int(git('cat-file', '-s', oid)) > LIMIT:
                failures.append((name or oid, 'historical oversized source blob'))
                continue
            data = git('cat-file', 'blob', oid)
            failures.extend((name or oid, 'historical ' + reason) for reason in content_reasons(data, secrets))
            seen.add(oid)
    if failures:
        for name, reason in sorted(set(failures)):
            print(f'REJECT: {name}: {reason}', file=sys.stderr)
        print('Public-tree audit failed. No matched credential values were printed.', file=sys.stderr)
        return 1
    print(f'Public-tree audit passed: {len(records)} index entries; {historical} historical blobs; '
          f'{len(secrets)} known-secret comparisons. Source text only; no private artifact paths.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
