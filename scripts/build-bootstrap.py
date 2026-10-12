#!/usr/bin/env python3
"""Build native Portal RAM boot images from the verified ROCKNIX release."""
import gzip
import hashlib
import json
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build/bootstrap'
STAGE = ROOT / 'build/ramroot'
RUNTIME = ROOT / 'build/rocknix-runtime'
PRIVATE = ROOT / 'private/bootstrap'


def sha256(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        while data := stream.read(8 * 1024 * 1024):
            result.update(data)
    return result.hexdigest()


def copy(source, destination, mode=None):
    destination = STAGE / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        destination.unlink()
    shutil.copyfile(source, destination)
    destination.chmod(mode if mode is not None else source.stat().st_mode & 0o777)


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    PRIVATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    asset = json.loads((ROOT / 'downloads/rocknix-selected-asset.json').read_text())
    source = ROOT / 'downloads' / asset['name']
    assert 'sha256:' + sha256(source) == asset['digest'], 'Release archive checksum mismatch'
    assert sha256(BUILD / 'Image') == '286c9d215c2e859886f737ffee49b8d04ce8c324d14df7b3b9cc4d87b1162bf9'
    assert sha256(BUILD / 'odin2portal.dtb') == '57aedc7331a1dbcb53e44f37eebb518838cbc04c40607e6181c63a9d88054b9b'
    for directory in ['usr/bin', 'usr/sbin', 'usr/lib', 'etc/ssh', 'root/.ssh',
                      'var/empty', 'run', 'proc', 'sys', 'dev', 'tmp', 'www/cgi-bin']:
        (STAGE / directory).mkdir(parents=True, exist_ok=True)
    for name, target in [('lib', 'usr/lib'), ('bin', 'usr/bin'), ('sbin', 'usr/sbin')]:
        link = STAGE / name
        if not link.is_symlink():
            link.symlink_to(target)
    copy(RUNTIME / 'usr/bin/busybox', 'usr/bin/busybox', 0o755)
    for name in ['ld-linux-aarch64.so.1', 'libc.so.6', 'libm.so.6', 'libcrypto.so.3',
                 'libz.so.1.3.2', 'libcrypt.so.2.0.0']:
        copy(RUNTIME / 'usr/lib' / name, 'usr/lib/' + name)
    apps = subprocess.check_output(['qemu-aarch64-static', '-L', str(STAGE),
                                   str(STAGE / 'usr/bin/busybox'), '--list'], text=True).splitlines()
    for app in apps:
        target = STAGE / 'usr/bin' / app
        if not target.exists() and not target.is_symlink():
            target.symlink_to('busybox')
    for alias, real in [('libz.so.1', 'libz.so.1.3.2'), ('libcrypt.so.2', 'libcrypt.so.2.0.0')]:
        link = STAGE / 'usr/lib' / alias
        if not link.is_symlink():
            link.symlink_to(real)
    copy(RUNTIME / 'usr/sbin/sshd', 'usr/sbin/sshd', 0o755)
    copy(RUNTIME / 'usr/lib/openssh/sshd-session', 'usr/lib/openssh/sshd-session', 0o755)
    for name in ['client', 'host']:
        key = PRIVATE / name
        if not key.exists():
            subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(key)], check=True)
    copy(PRIVATE / 'client.pub', 'root/.ssh/authorized_keys', 0o600)
    copy(PRIVATE / 'host', 'etc/ssh/ssh_host_ed25519_key', 0o600)
    copy(PRIVATE / 'host.pub', 'etc/ssh/ssh_host_ed25519_key.pub', 0o644)
    (STAGE / 'etc/passwd').write_text('root:*:0:0:root:/root:/bin/sh\n'
                                     'sshd:*:74:74:sshd:/var/empty:/bin/false\n'
                                     'nobody:*:65534:65534:nobody:/var/empty:/bin/false\n')
    (STAGE / 'etc/group').write_text('root:x:0:\nsshd:x:74:\nnobody:x:65534:\n')
    (STAGE / 'etc/nsswitch.conf').write_text('passwd: files\ngroup: files\nhosts: files dns\n')
    (STAGE / 'etc/ssh/sshd_config').write_text(
        'Port 22\nListenAddress 192.168.77.2\nHostKey /etc/ssh/ssh_host_ed25519_key\n'
        'AuthorizedKeysFile /root/.ssh/authorized_keys\nPermitRootLogin prohibit-password\n'
        'PasswordAuthentication no\nKbdInteractiveAuthentication no\n'
        'StrictModes no\nPidFile /run/sshd.pid\n')
    overlay = RUNTIME / 'usr/lib/kernel-overlays/base/lib'
    shutil.copytree(overlay / 'firmware', STAGE / 'usr/lib/firmware', dirs_exist_ok=True)
    modules = ['qcom_sysmon', 'qcom_q6v5', 'qcom_common', 'qcom_pil_info', 'qcom_q6v5_pas']
    for name in modules:
        path = pathlib.Path('modules/7.2.0/kernel/drivers/remoteproc') / (name + '.ko')
        copy(overlay / path, 'usr/lib/' + str(path))
    copy(ROOT / 'bootstrap/init', 'init', 0o755)
    copy(ROOT / 'bootstrap/status.cgi', 'www/cgi-bin/status.cgi', 0o755)
    (STAGE / 'www/index.html').write_text('Omarchy native Portal bootstrap: /cgi-bin/status.cgi\n')
    names = subprocess.check_output(['find', '.', '-print0'], cwd=STAGE)
    result = subprocess.run(['cpio', '--null', '-o', '-H', 'newc', '--owner=0:0'],
                            input=names, cwd=STAGE, capture_output=True, check=True)
    ramdisk = BUILD / 'initramfs.cpio.gz'
    ramdisk.write_bytes(gzip.compress(result.stdout, compresslevel=6, mtime=0))
    kernel = BUILD / 'Image.gz-dtb'
    kernel.write_bytes(gzip.compress((BUILD / 'Image').read_bytes(), compresslevel=6, mtime=0)
                       + (BUILD / 'odin2portal.dtb').read_bytes())
    cmdline = ('rdinit=/init console=tty0 loglevel=7 panic=30 clk_ignore_unused '
               'pd_ignore_unused allow_mismatched_32bit_el0 fw_devlink.strict=1 '
               'pcie_ports=compat irqaffinity=0-2 mem_sleep_default=s2idle')
    images = []
    tool = ROOT / 'tools/android-tools/usr/share/android-tools/mkbootimg/mkbootimg.py'
    for version in [1, 0]:
        image = BUILD / f'portal-bootstrap-v{version}.img'
        subprocess.run(['python3', str(tool), '--kernel', str(kernel), '--ramdisk', str(ramdisk),
                        '--cmdline', cmdline, '--base', '0x0', '--kernel_offset', '0x8000',
                        '--ramdisk_offset', '0x1000000', '--tags_offset', '0x100',
                        '--pagesize', '4096', '--header_version', str(version),
                        '--os_version', '13.0.0', '--os_patch_level', '2026-10', '-o', str(image)], check=True)
        images.append({'file': image.name, 'bytes': image.stat().st_size, 'sha256': sha256(image)})
    (BUILD / 'manifest.json').write_text(json.dumps({
        'model': 'AYN Odin 2 Portal', 'kernel': 'ROCKNIX 7.2.0 (20261001)',
        'source_url': asset['browser_download_url'], 'source_digest': asset['digest'],
        'dtb_sha256': sha256(BUILD / 'odin2portal.dtb'), 'cmdline': cmdline,
        'userdata_or_storage_mounts': False, 'images': images,
    }, indent=2) + '\n')
    print(json.dumps(images, indent=2))


if __name__ == '__main__':
    main()
