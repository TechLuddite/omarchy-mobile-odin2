#!/usr/bin/env python3
"""Stage ARM filesystem tools and their ELF dependencies for the RAM installer."""
import pathlib
import re
import shutil
import subprocess

project = pathlib.Path(__file__).resolve().parents[1]
root = project / 'build/native-rootfs/rootfs'
stage = project / 'build/install-tools'
stage.mkdir(parents=True, exist_ok=True)
for name in ('lib', 'lib64'):
    if not (stage / name).is_symlink():
        (stage / name).symlink_to('usr/lib')
queue = [pathlib.Path('usr/bin') / name for name in
         ('mkfs.ext4', 'mkfs.fat', 'parted', 'partprobe', 'sfdisk', 'blockdev',
          'blkid', 'wipefs', 'lsblk', 'findmnt', 'tar', 'gzip')]
queue.append(pathlib.Path('usr/lib/ld-linux-aarch64.so.1'))
done = set()
while queue:
    relative = queue.pop()
    if relative in done:
        continue
    done.add(relative)
    source = root / relative
    if not source.is_file():
        raise FileNotFoundError(source)
    target = stage / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    target.chmod(source.stat().st_mode & 0o777)
    dynamic = subprocess.check_output(['readelf', '-d', str(source)], text=True)
    for name in re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic):
        queue.append(pathlib.Path('usr/lib') / name)
for name in ('dev', 'proc', 'sys', 'run', 'tmp'):
    (stage / name).mkdir(exist_ok=True)
print(f'{len(done)} ARM binaries/libraries staged in {stage}')
