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
import subprocess
import sys

PROVEN = "e8b2e3cb289c7db5ef6a430bcb598c78a0b3ea685566138e6fbc7af641409f07"
CANDIDATE = "3c6b2569a964ec8c04b5bc96950df3921d58b016b77d40fd72fa597c10986763"
V2 = "8e91711bbced456c197afaa1a8216279f0a3ac104abc9c24bf51c5b3d9774fc8"
FRAGMENT = "56052faa39b2255c5a4f2e2301efe8f98003cea7ec91bf7e71f2980e2d77aab3"
PREVIOUS_UCM = "7f1e20c3ef62b3351c301138da87cbe441ccc19a9b4cb1433057944816f84777"
SLOT7_PROBE_UCM = "a09a56292e7d9f18c75c22a642abf5102c6c1637b83b9923575e2e90169fc7c2"
ORIGINAL_UCM = "5dd466384c50e926695051a5508a1f026d6346ab3a79891692d61cbfcba64fb9"


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
    current_kernel = digest(kernel)
    if current_kernel not in (PROVEN, V2) or digest(backup) != PROVEN:
        raise SystemExit("Expected reviewed baseline/V2 and proven KERNEL.bak; installation has not started")
    if digest(image) != CANDIDATE or image.stat().st_size >= 96 * 1024**2:
        raise SystemExit("Candidate digest or image size mismatch")
    if not os.path.ismount("/boot"):
        raise SystemExit("ESP is not mounted")
    mount = subprocess.check_output(
        ["findmnt", "-n", "-o", "SOURCE,FSTYPE", "/boot"], text=True).split()
    if mount != ["/dev/sda17", "vfat"]:
        raise SystemExit("Expected the installed Portal ESP at /dev/sda17")
    if subprocess.check_output(["blockdev", "--getss", "/dev/sda17"], text=True).strip() != "4096":
        raise SystemExit("Unexpected ESP sector geometry")
    slots = subprocess.check_output(["qbootctl"], text=True)
    slot_a = slots.split("SLOT _a:", 1)[1].split("SLOT _b:", 1)[0]
    values = {key.strip(): value.strip() for line in slot_a.splitlines()
              if ":" in line for key, value in [line.split(":", 1)]}
    if any(values.get(field) != "1" for field in ("Active", "Successful", "Bootable")):
        raise SystemExit("Slot A must be active, bootable and successful before this test")
    hifi = Path("/usr/share/alsa/ucm2/AYN/Odin2/HiFi.conf")
    original = Path("/root/odin-hifi-before-capture.conf")
    saved = Path("/root/odin-hifi-before-wcd-v3-test.conf")
    expected_ucm = PREVIOUS_UCM if current_kernel == PROVEN else SLOT7_PROBE_UCM
    if digest(hifi) != expected_ucm or digest(original) != ORIGINAL_UCM or digest(fragment) != FRAGMENT:
        raise SystemExit("UCM baseline or reviewed fragment changed")
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
    if digest(kernel) != CANDIDATE or digest(backup) != PROVEN:
        raise SystemExit("Final boot-image readback failed; restore the proven image before reboot")
    print(f"ESP KERNEL installed: {digest(kernel)}")
    print("KERNEL.bak and both raw boot partitions retain the proven image.")
    print("Reboot separately, inspect audio routes and complete the visible speech test.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: install-microphone-candidate.py CANDIDATE_IMG UCM_FRAGMENT")
    main()
