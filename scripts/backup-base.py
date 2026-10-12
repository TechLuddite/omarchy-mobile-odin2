#!/usr/bin/env python3
"""Capture UFS base-image extents through EDL; never writes to the device."""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKUP = ROOT / 'private/base-backup'


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def plan(storage):
    sector = storage['sector_size']
    assert sector == 4096, 'Reinspect unexpected sector size'
    luns = {lun['lun']: lun for lun in storage['luns']}
    assert set(luns) == set(range(6)), 'Expected six inspected UFS LUNs'
    regions = []
    for number in [1, 2, 3, 5, 4]:
        lun = luns[number]
        assert lun['size'] == lun['sectors'] * sector
        regions.append({'lun': number, 'start_sector': 0,
                        'sectors': lun['sectors'], 'file': f'lun{number}.img'})
    lun = luns[0]
    userdata = [p for p in lun['partitions'] if p['name'] == 'userdata']
    assert len(userdata) == 1
    userdata = userdata[0]
    assert max(p['offset'] + p['size'] for p in lun['partitions']) == userdata['offset'] + userdata['size']
    end = userdata['offset'] + userdata['size']
    assert userdata['offset'] % sector == 0 and end % sector == 0
    regions.extend([
        {'lun': 0, 'start_sector': 0, 'sectors': userdata['offset'] // sector,
         'file': 'lun0-base-prefix.img'},
        {'lun': 0, 'start_sector': end // sector,
         'sectors': lun['sectors'] - end // sector, 'file': 'lun0-tail.img'},
    ])
    assert all(r['sectors'] > 0 for r in regions)
    return regions, userdata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--read', action='store_true', help='perform device reads; default prints the plan')
    args = parser.parse_args()
    os.umask(0o077)
    storage = json.loads((BACKUP / 'storage-map.json').read_text())
    regions, userdata = plan(storage)
    sector = storage['sector_size']
    print(json.dumps({'regions': regions, 'omitted_userdata': userdata}, indent=2), flush=True)
    if not args.read:
        return
    needed = sum(r['sectors'] * sector for r in regions)
    assert shutil.disk_usage(BACKUP).free > needed + 2 * 1024**3, 'Insufficient backup storage'
    reader = ROOT / 'tools/edl-venv/bin/python'
    loader = ROOT / 'downloads/xbl_s_devprg_ns.melf'
    assert sha256(loader) == 'c522842dcb2a02a2230d4d12301e36e6ddeae7e44aeaa79851234ab65e4f8d9e'
    manifest = {
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'all UFS bytes except the userdata partition payload; split raw image extents',
        'full_device_clone': False, 'device_storage_writes': False,
        'sector_size': sector, 'omitted_userdata': userdata,
        'reader_revision': subprocess.check_output(
            ['git', '-C', str(ROOT / 'references/edl'), 'rev-parse', 'HEAD'], text=True).strip(),
        'loader_sha256': sha256(loader), 'regions': [], 'complete': False,
    }
    manifest_path = BACKUP / 'manifest.json'
    def save_manifest():
        temp = manifest_path.with_suffix('.json.tmp')
        temp.write_text(json.dumps(manifest, indent=2) + '\n')
        temp.replace(manifest_path)
    save_manifest()
    environment = dict(os.environ, PYTHONPATH=str(ROOT / 'references/edl'))
    for region in regions:
        target = BACKUP / region['file']
        assert not target.exists(), f'Refusing to overwrite {target}'
        partial = target.with_suffix('.img.partial')
        assert not partial.exists(), f'Partial backup needs inspection: {partial}'
        count = region['sectors'] * sector
        print(f"Reading {region['file']}: {count / 1024**2:.2f} MiB", flush=True)
        command = [str(reader), '-m', 'edlclient.edl', 'rs',
                   str(region['start_sector']), str(region['sectors']), str(partial),
                   f"--lun={region['lun']}", '--memory=ufs', f'--loader={loader}']
        log_path = BACKUP / (region['file'] + '.log')
        with log_path.open('w') as log:
            result = subprocess.run(command, cwd=BACKUP, env=environment,
                                    stdout=log, stderr=subprocess.STDOUT, timeout=1800)
        assert result.returncode == 0, f'Reader failed: inspect {log_path}'
        assert partial.is_file() and partial.stat().st_size == count, f'Incomplete read: {partial}'
        log_text = log_path.read_text(errors='replace')
        assert 'Dumped sector' in log_text, f'No read completion recorded: {log_path}'
        checksum = sha256(partial)
        partial.rename(target)
        manifest['regions'].append(dict(region, bytes=count, sha256=checksum))
        save_manifest()
        print(f"Verified size and checksum: {region['file']}", flush=True)
    manifest['complete'] = True
    manifest['completed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_manifest()
    print('All base image extents captured. GPT and independent reread validation still required.', flush=True)


if __name__ == '__main__':
    main()
