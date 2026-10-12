#!/usr/bin/env python3
"""Install the reviewed WCD route candidate on this Portal's ESP only.

Run on the Odin as root with the candidate image and UCM fragment as arguments.
Refuses a different model or baseline. Preserves KERNEL.bak, boot_a/boot_b and
the read-only recovery image. Reboot separately after reviewing the result.
"""
import hashlib
import os
from pathlib import Path
import shutil
import sys

PROVEN = "e8b2e3cb289c7db5ef6a430bcb598c78a0b3ea685566138e6fbc7af641409f07"
CANDIDATE = "b48f0d1beb49cb9c2ee8970c43de98d603c9e48f0fe27ce46a9c62ff5562bc57"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if os.geteuid() != 0 or os.uname().machine != "aarch64":
        raise SystemExit("Run as root on the ARM64 Portal")
    model = Path("/sys/firmware/devicetree/base/model").read_bytes().rstrip(b"\0")
    if model != b"AYN Odin 2 Portal":
        raise SystemExit("Unexpected device model")
    image, fragment = map(Path, sys.argv[1:])
    kernel = Path("/boot/KERNEL")
    backup = Path("/boot/KERNEL.bak")
    if digest(kernel) != PROVEN or digest(backup) != PROVEN:
        raise SystemExit("Expected proven KERNEL and KERNEL.bak; installation has not started")
    if digest(image) != CANDIDATE or image.stat().st_size >= 96 * 1024**2:
        raise SystemExit("Candidate digest or image size mismatch")
    if not os.path.ismount("/boot"):
        raise SystemExit("ESP is not mounted")
    hifi = Path("/usr/share/alsa/ucm2/AYN/Odin2/HiFi.conf")
    original = Path("/root/odin-hifi-before-capture.conf")
    saved = Path("/root/odin-hifi-before-wcd-test.conf")
    if saved.exists():
        raise SystemExit("A prior candidate backup exists; review its state first")
    temporary = Path("/boot/KERNEL.wcd-candidate")
    shutil.copyfile(image, temporary)
    if digest(temporary) != CANDIDATE:
        temporary.unlink()
        raise SystemExit("ESP copy failed verification")
    shutil.copyfile(hifi, saved)
    saved.chmod(0o600)
    contents = original.read_text() + "\n" + fragment.read_text()
    config_temp = hifi.with_suffix(".conf.next")
    config_temp.write_text(contents)
    config_temp.chmod(0o644)
    os.sync()
    config_temp.replace(hifi)
    temporary.replace(kernel)
    os.sync()
    print(f"ESP KERNEL installed: {digest(kernel)}")
    print("KERNEL.bak and both raw boot partitions retain the proven image.")
    print("Reboot separately, inspect audio routes and complete the visible speech test.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: install-microphone-candidate.py CANDIDATE_IMG UCM_FRAGMENT")
    main()
