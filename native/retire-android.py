#!/usr/bin/env python3
"""Finish the verified Portal installation; never run on an unverified target.

This is a one-time, destructive Android retirement for the captured 1 TB Portal.
Checks must all pass before any block writes. Preserve platform/calibration
partitions and the verified PC-side original images.
"""
import fcntl
import hashlib
import json
import os
import pathlib
import stat
import struct
import subprocess
import sys

BOOT_SHA = 'e8b2e3cb289c7db5ef6a430bcb598c78a0b3ea685566138e6fbc7af641409f07'
ABL_SHA = '5f1018211feaa109563d5890ab52dccfb31db90f4bbe9e6b7fb39e94f860f8d4'
ORIGINAL_ABL_B = 'b55a6feed59469e373bf8286d7ae06a17e020a95efa01db42bc3929956f8f449'

def run(*args):
    return subprocess.check_output(args, text=True).strip()

def digest(path, count=None):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        while count is None or count > 0:
            data = stream.read(min(count, 4 * 1024**2) if count is not None else 4 * 1024**2)
            if not data:
                break
            h.update(data)
            if count is not None:
                count -= len(data)
    if count is not None and count != 0:
        raise RuntimeError(f'short read: {path}')
    return h.hexdigest()

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def block(name, size):
    path = pathlib.Path('/dev/disk/by-partlabel') / name
    require(stat.S_ISBLK(path.stat().st_mode), f'{name} is not a block device')
    with path.open('rb') as stream:
        actual = struct.unpack('Q', fcntl.ioctl(stream.fileno(), 0x80081272, bytes(8)))[0]
    require(actual == size, f'{name}: unexpected partition size {actual}')
    return path

def write_file(source, destination):
    with source.open('rb') as src, destination.open('r+b', buffering=0) as dst:
        while data := src.read(4 * 1024**2):
            view = memoryview(data)
            while view:
                written = dst.write(view)
                require(written > 0, f'short write: {destination}')
                view = view[written:]
        os.fsync(dst.fileno())
    require(digest(destination, source.stat().st_size) == digest(source),
            f'readback mismatch: {destination}')
    print(f'Wrote and verified {destination.name}', flush=True)

def zero(destination, size):
    with destination.open('r+b', buffering=0) as stream:
        for _ in range(size // (1024**2)):
            view = memoryview(bytes(1024**2))
            while view:
                written = stream.write(view)
                require(written > 0, f'short zero write: {destination}')
                view = view[written:]
        os.fsync(stream.fileno())
    require(digest(destination, size) == hashlib.sha256(bytes(size)).hexdigest(),
            f'zero readback mismatch: {destination}')
    print(f'Cleared and verified {destination.name}', flush=True)

require(os.geteuid() == 0, 'must run as root')
require(pathlib.Path('/proc/device-tree/model').read_bytes().rstrip(b'\0') == b'AYN Odin 2 Portal',
        'wrong device model')
require(run('findmnt', '-nro', 'SOURCE', '/') == '/dev/sda18', 'not booted from installed root')
require(pathlib.Path('/sys/class/block/sda/size').read_text().strip() == '1973878784',
        'wrong disk capacity')
boot = pathlib.Path('/boot/KERNEL')
abl = pathlib.Path(sys.argv[1])
require(digest(boot) == BOOT_SHA, 'native boot image hash mismatch')
require(digest(abl) == ABL_SHA, 'ABL image hash mismatch')
parts = {name: block(name, size) for name, size in {
    'boot_a': 96 * 1024**2, 'boot_b': 96 * 1024**2, 'abl_b': 1024**2,
    'dtbo_b': 24 * 1024**2, 'init_boot_b': 8 * 1024**2,
    'super': 5679575040,
}.items()}
require(digest(parts['abl_b']) == ORIGINAL_ABL_B, 'inactive ABL is not the saved original')
before = json.loads(run('sfdisk', '--json', '/dev/sda'))['partitiontable']
require(len(before['partitions']) == 18, 'unexpected partition count')
old_super = before['partitions'][13]
require(old_super['name'] == 'super' and old_super['start'] == 571144
        and old_super['size'] == 1386615, 'unexpected Android super geometry')
require(not run('findmnt', '-rn', '-o', 'SOURCE').splitlines().count(str(parts['super'].resolve())),
        'super is mounted')
backup = pathlib.Path('/root/native-transition')
backup.mkdir(mode=0o700)
(backup / 'lun0-before.json').write_text(json.dumps(before, indent=2))
with parts['abl_b'].open('rb') as stream:
    (backup / 'original-abl_b.img').write_bytes(stream.read())

write_file(boot, parts['boot_a'])
write_file(boot, parts['boot_b'])
zero(parts['init_boot_b'], 8 * 1024**2)
zero(parts['dtbo_b'], 24 * 1024**2)
write_file(abl, parts['abl_b'])
subprocess.run(['mkfs.ext4', '-F', '-L', 'OMARCHY_RECOV', '-m', '0', '-E', 'nodiscard',
                str(parts['super'])], check=True)
for option, value in [('part-type', '0FC63DAF-8483-4772-8E79-3D69D8477DE4'),
                       ('part-label', 'OMARCHY_RECOVERY')]:
    subprocess.run(['sfdisk', '--no-reread', '--no-tell-kernel', f'--{option}',
                    '/dev/sda', '14', value], check=True)
after = json.loads(run('sfdisk', '--json', '/dev/sda'))['partitiontable']
for index, (old, new) in enumerate(zip(before['partitions'], after['partitions'])):
    if index == 13:
        for key in ('node', 'start', 'size', 'uuid'):
            require(old[key] == new[key], f'recovery {key} changed')
    else:
        require(old == new, f'unexpected GPT change in partition {index + 1}')
(backup / 'lun0-after.json').write_text(json.dumps(after, indent=2))
pathlib.Path('/recovery').mkdir(mode=0o700, exist_ok=True)
subprocess.run(['mount', str(parts['super']), '/recovery'], check=True)
os.sync()
print('Both boot slots are native. Former Android super is recovery storage.', flush=True)
