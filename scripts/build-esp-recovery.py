#!/usr/bin/env python3
"""Build a verified 512 MiB Portal ESP recovery image for fastboot.

Restores only OMARCHY_BOOT, using the previously booted native KERNEL and
the saved RAM recovery. Does not recreate the root or change the GPT.
Requires dosfstools and mtools on the host. This program only creates a file.
"""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build/bootstrap"
FILES = {
    "KERNEL": ("portal-omarchy-native.img", "e8b2e3cb289c7db5ef6a430bcb598c78a0b3ea685566138e6fbc7af641409f07"),
    "KERNEL.bak": ("portal-omarchy-native.img", "e8b2e3cb289c7db5ef6a430bcb598c78a0b3ea685566138e6fbc7af641409f07"),
    "RECOVERY.img": ("portal-bootstrap-v0.img", "129125049bba685380ced3c186c2f75eb8942954c7f09c9b18646f1875d1a259"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for file, (source, expected) in FILES.items():
        if sha(BUILD / source) != expected:
            raise SystemExit(f"Unexpected source digest: {source}")
    image = BUILD / "portal-esp-recovery.img"
    with image.open("wb") as output:
        output.truncate(512 * 1024**2)
    # UFS exposes 4096-byte logical sectors. A host-file mkfs default of 512
    # creates a FAT image Linux refuses to mount on this physical device.
    subprocess.run(["mkfs.vfat", "-S", "4096", "-F", "32", "-n", "OMARCHYBOOT", str(image)], check=True)
    with image.open("rb") as source:
        header = source.read(512)
    if struct.unpack_from("<H", header, 11)[0] != 4096:
        raise SystemExit("FAT logical sector size must match Portal UFS: 4096")
    for file, (source, expected) in FILES.items():
        subprocess.run(["mcopy", "-i", str(image), str(BUILD / source), f"::{file}"], check=True)
    with tempfile.TemporaryDirectory(dir=BUILD) as temp:
        for file, (source, expected) in FILES.items():
            copy = Path(temp) / file
            subprocess.run(["mcopy", "-i", str(image), f"::{file}", str(copy)], check=True)
            if sha(copy) != expected:
                raise SystemExit(f"FAT readback mismatch: {file}")
    result = {
        "file": image.name, "bytes": image.stat().st_size, "sha256": sha(image),
        "target_partition": "OMARCHY_BOOT", "target_bytes": 512 * 1024**2,
        "logical_sector_bytes": 4096,
        "file_readbacks": {name: value[1] for name, value in FILES.items()},
        "scope": "ESP files only; root and GPT excluded",
    }
    (BUILD / "esp-recovery-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
