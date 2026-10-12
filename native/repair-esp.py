#!/usr/bin/env python3
"""Write a reviewed 4 KiB-sector ESP image to this Portal's unmounted sda17.

Run from RAM recovery with IMAGE and its SHA256. Only OMARCHY_BOOT is written;
model, partition, size, sector geometry and digest checks precede all writes.
"""
import fcntl
import hashlib
import os
from pathlib import Path
import stat
import struct
import sys


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(4 * 1024**2):
            checksum.update(chunk)
    return checksum.hexdigest()


def main():
    if os.geteuid() != 0 or os.uname().machine != "aarch64":
        raise SystemExit("Run as root on the ARM64 Portal")
    if Path("/sys/firmware/devicetree/base/model").read_bytes().rstrip(b"\0") != b"AYN Odin 2 Portal":
        raise SystemExit("Unexpected device model")
    image = Path(sys.argv[1])
    expected = sys.argv[2]
    device = Path("/dev/sda17")
    metadata = dict(line.split("=", 1) for line in Path("/sys/class/block/sda17/uevent").read_text().splitlines())
    if metadata.get("PARTNAME") != "OMARCHY_BOOT":
        raise SystemExit("sda17 is not the expected ESP")
    info = device.stat()
    if not stat.S_ISBLK(info.st_mode):
        raise SystemExit("Target is not a block device")
    number = f"{os.major(info.st_rdev)}:{os.minor(info.st_rdev)}"
    if any(line.split()[2] == number for line in Path("/proc/self/mountinfo").read_text().splitlines()):
        raise SystemExit("ESP must be unmounted")
    with device.open("rb", buffering=0) as target:
        size = struct.unpack("Q", fcntl.ioctl(target.fileno(), 0x80081272, bytes(8)))[0]
        sector = struct.unpack("I", fcntl.ioctl(target.fileno(), 0x1268, bytes(4)))[0]
    if size != 512 * 1024**2 or sector != 4096 or image.stat().st_size != size:
        raise SystemExit("Unexpected image or device geometry")
    with image.open("rb") as source:
        header = source.read(512)
    if struct.unpack_from("<H", header, 11)[0] != sector:
        raise SystemExit("FAT sector size does not match UFS")
    if digest(image) != expected:
        raise SystemExit("Reviewed image digest mismatch")
    with image.open("rb") as source, device.open("r+b", buffering=0) as target:
        fcntl.flock(target, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while chunk := source.read(4 * 1024**2):
            pending = memoryview(chunk)
            while pending:
                count = target.write(pending)
                if not count:
                    raise RuntimeError("Short ESP write")
                pending = pending[count:]
        os.fsync(target.fileno())
        # Invalidate block cache so the digest verifies a device readback.
        fcntl.ioctl(target.fileno(), 0x1261)
    actual = digest(device)
    if actual != expected:
        raise RuntimeError("ESP device readback digest mismatch")
    print(f"OMARCHY_BOOT write and device readback verified: {actual}")
    print(f"FAT/UFS sector size: {sector}; bytes: {size}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: repair-esp.py IMAGE SHA256")
    main()
