#!/usr/bin/env python3
"""Use the proven Portal kernel and RAM recovery to build the internal boot image."""
import gzip
import hashlib
import json
import pathlib
import shutil
import subprocess

root = pathlib.Path(__file__).resolve().parents[1]
build = root / 'build/bootstrap'
stage = root / 'build/native-initramfs'
if stage.exists():
    shutil.rmtree(stage)
source = root / 'build/ramroot'
def skip_runtime(path, names):
    # Host chroot checks can leave device nodes here; never read /dev/zero
    # as a regular file. The target mounts fresh pseudo filesystems in /init.
    return names if pathlib.Path(path).relative_to(source).as_posix() in {
        'dev', 'proc', 'sys', 'run'
    } else []
shutil.copytree(source, stage, symlinks=True, ignore=skip_runtime)
shutil.copyfile(root / 'bootstrap/init', stage / 'bootstrap-init')
(stage / 'bootstrap-init').chmod(0o755)
shutil.copyfile(root / 'native/init', stage / 'init')
(stage / 'init').chmod(0o755)
names = subprocess.check_output(['find', '.', '-print0'], cwd=stage)
archive = subprocess.run(['cpio', '--null', '-o', '-H', 'newc', '--owner=0:0'],
                         cwd=stage, input=names, capture_output=True, check=True).stdout
ramdisk = build / 'native-initramfs.cpio.gz'
ramdisk.write_bytes(gzip.compress(archive, compresslevel=6, mtime=0))
manifest = json.loads((build / 'manifest.json').read_text())
cmdline = manifest['cmdline'].replace('loglevel=7 panic=30', 'loglevel=4 panic=30')
image = build / 'portal-omarchy-native.img'
subprocess.run(['python3', str(root / 'tools/android-tools/usr/share/android-tools/mkbootimg/mkbootimg.py'),
                '--kernel', str(build / 'Image.gz-dtb'), '--ramdisk', str(ramdisk),
                '--cmdline', cmdline, '--base', '0x0', '--kernel_offset', '0x8000',
                '--ramdisk_offset', '0x1000000', '--tags_offset', '0x100',
                '--pagesize', '4096', '--header_version', '0', '--os_version', '13.0.0',
                '--os_patch_level', '2026-10', '-o', str(image)], check=True)
assert image.stat().st_size < 96 * 1024**2
result = {'file': image.name, 'bytes': image.stat().st_size,
          'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
          'root_gpt_label': 'OMARCHY_ROOT', 'ram_recovery_fallback': True,
          'kernel_source': manifest['source_url'], 'source_digest': manifest['source_digest']}
(build / 'native-manifest.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
