#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Native client layout/bootstrap adapted from Shuuri Labs' pocknix-steam-install.
# Upstream: shuuri-labs/pocknix-os, ba1de097fb0e0df07bcb32f05dc8e957d62090bc.
# Retain licenses/pocknix-GPL-2.0.txt. Valve owns Steam and its distributed client.
"""Extract the verified Valve ARM64 Steam seed/runtime as the desktop user.

Does not install a distro, kernel, compositor, gamepad mapper or translation
layer. Launch Steam separately in the live desktop to let its updater finish.
"""
import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import struct
import tarfile
import zipfile

CLIENT_SHA256 = "9a83661b1d254596d680d64bb36f777d523cb59495c224307b5313276b586129"
RUNTIME_SHA256 = "2f2be461b6a4360828e200e1644e18cd957eedc36a38e5a1e13a39276320b6e2"
CHANNEL = "steamdeck_publicbeta"


def verify(path, expected):
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != expected:
        raise SystemExit(f"Unreviewed download: {path.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("client_zip", type=Path)
    parser.add_argument("runtime_tar", type=Path)
    args = parser.parse_args()
    if os.geteuid() == 0 or platform.machine() != "aarch64":
        raise SystemExit("Run as the desktop user on the ARM64 Portal")
    model = Path("/sys/firmware/devicetree/base/model").read_bytes().rstrip(b"\0")
    if model != b"AYN Odin 2 Portal":
        raise SystemExit("Unexpected board")
    verify(args.client_zip, CLIENT_SHA256)
    verify(args.runtime_tar, RUNTIME_SHA256)
    root = Path.home() / ".local/share/Steam"
    dot = Path.home() / ".steam"
    if root.exists() or dot.exists():
        raise SystemExit("Existing Steam state found; inspect it rather than overwriting it")
    with zipfile.ZipFile(args.client_zip) as archive:
        executable = archive.read("steamrtarm64/steam")
        if executable[:5] != b"\x7fELF\x02" or struct.unpack_from("<H", executable, 18)[0] != 183:
            raise SystemExit("Seed is not an AArch64 ELF client")
        members = []
        for member in archive.infolist():
            name = PurePosixPath(member.filename.replace("\\", "/"))
            if name.is_absolute() or ".." in name.parts or name.parts[0] != "steamrtarm64":
                raise SystemExit("Unexpected client archive path")
            if stat.S_ISLNK(member.external_attr >> 16):
                expected_links = {
                    "steamrtarm64/libs/libcurl.so": b"libcurl.so.4.8.0",
                    "steamrtarm64/libs/libnghttp2.so": b"libnghttp2.so.14.20.1",
                    "steamrtarm64/libs/libnghttp2.so.14": b"libnghttp2.so.14.20.1",
                }
                if archive.read(member) != expected_links.get(str(name)):
                    raise SystemExit("Unexpected client archive symlink")
            members.append((member, name))
        root.mkdir(parents=True, mode=0o700)
        for member, name in members:
            target = root / name
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            data = archive.read(member)
            if stat.S_ISLNK(member.external_attr >> 16):
                target.symlink_to(data.decode("ascii"))
                continue
            target.write_bytes(data)
            # Valve's zip declares 0666 for binaries; mark native executables
            # and its launcher scripts executable, as the updater expects.
            target.chmod(0o755 if data.startswith((b"\x7fELF", b"#!")) else 0o644)
    with tarfile.open(args.runtime_tar) as archive:
        archive.extractall(root, filter="data")
    lib = root / "lib/aarch64-linux-gnu"
    lib.mkdir(parents=True)
    # Current ALARM no longer packages GTK2. Use only the missing legacy
    # libraries from Valve's verified runtime, preserving the host's Mesa,
    # glibc and other libraries rather than prepending the entire runtime.
    for soname in ("libibus-1.0.so.5", "libgtk-x11-2.0.so.0", "libgdk-x11-2.0.so.0"):
        candidates = list(root.glob(f"steam-runtime-steamrt-arm64/steamrt3c_platform_*/files/lib/aarch64-linux-gnu/{soname}.*"))
        if len(candidates) != 1:
            raise SystemExit(f"Unexpected runtime {soname} layout; inspect extracted files")
        (lib / soname).symlink_to(os.path.relpath(candidates[0], lib))
    (root / "package").mkdir()
    (root / "package/beta").write_text(CHANNEL + "\n")
    dot.mkdir(mode=0o700)
    for name, target in {
        "steam": root, "root": root, "sdk32": root / "linux32",
        "sdk64": root / "linux64", "sdkarm64": root / "linuxarm64",
        "bin32": root / "ubuntu12_32", "bin64": root / "ubuntu12_64",
    }.items():
        (dot / name).symlink_to(os.path.relpath(target, dot))
    print(f"Verified ARM64 Steam seed and runtime installed at {root}")
    print("Launch steam in the live desktop to complete Valve's update and sign in.")


if __name__ == "__main__":
    main()
