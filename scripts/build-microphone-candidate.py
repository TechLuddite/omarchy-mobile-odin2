#!/usr/bin/env python3
"""Stage the Portal DMIC3/SWR_MIC7 candidate without changing proven images.

The saved SM8550/0x1001f Android QRD audio configuration routes handset capture
through codec DMIC2, with MIC BIAS3 powering codec DMIC2/3. The existing native
DTB omits these board routes. Luke Johnson's WCD DMIC input patch (Pocknix)
is already present in the running ROCKNIX kernel. Luke Johnson's Pocknix Thor
route supplied the DMIC3/SWR_MIC7 lead confirmed by controlled speech on this
Portal. This adds two board route pairs only and never flashes the device.
"""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "build/bootstrap"
OUTPUT = ROOT / "build/microphone-candidate-v3"
# Direct capture establishes voice on SoundWire DMIC3 / TX input7. The
# DMIC3 DAPM widget powers the shared clock pair containing that data channel,
# as in Luke Johnson's Pocknix Thor route. Keep earlier artifacts intact.
ROUTES = [
    "DMIC3", "MIC BIAS3", "TX SWR_INPUT7", "DMIC3_OUTPUT",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_dtb = BASE / "odin2portal.dtb"
    model = subprocess.check_output(["fdtget", str(source_dtb), "/", "model"], text=True).strip()
    if model != "AYN Odin 2 Portal":
        raise SystemExit(f"Unexpected board: {model}")
    baseline = BASE / "portal-omarchy-native.img"
    baseline_sha = "e8b2e3cb289c7db5ef6a430bcb598c78a0b3ea685566138e6fbc7af641409f07"
    if sha(baseline) != baseline_sha:
        raise SystemExit("The proven native image has changed; review the candidate's base first")
    for name, expected in {
        "Image": "286c9d215c2e859886f737ffee49b8d04ce8c324d14df7b3b9cc4d87b1162bf9",
        "native-initramfs.cpio.gz": "b37bddcafe84e4f06937192ea810b3f9743c25616ea547121af62a29a9c9a3fa",
        "odin2portal.dtb": "57aedc7331a1dbcb53e44f37eebb518838cbc04c40607e6181c63a9d88054b9b",
    }.items():
        if sha(BASE / name) != expected:
            raise SystemExit(f"Baseline component changed: {name}")
    OUTPUT.mkdir(exist_ok=True)
    dtb = OUTPUT / "odin2portal-wcd-mic.dtb"
    shutil.copyfile(source_dtb, dtb)
    # fdtget prints strings separated by spaces, which also occur inside widget
    # names. Read the property bytes directly rather than splitting that output.
    raw = subprocess.check_output(["fdtget", "-t", "bx", str(dtb), "/sound", "audio-routing"], text=True)
    strings = bytes(int(value, 16) for value in raw.split()).decode().rstrip("\0").split("\0")
    if len(strings) % 2 or "ADC2_OUTPUT" not in strings:
        raise SystemExit("Unexpected baseline sound routing")
    new = strings + ROUTES
    subprocess.run(["fdtput", "-t", "s", str(dtb), "/sound", "audio-routing", *new], check=True)
    # Decompilation makes a reviewable change alongside the binary candidate.
    for name, path in [("baseline", source_dtb), ("candidate", dtb)]:
        with (OUTPUT / f"{name}.dts").open("w") as output:
            subprocess.run(["dtc", "-I", "dtb", "-O", "dts", str(path)],
                           stdout=output, stderr=subprocess.DEVNULL, check=True)
    kernel = OUTPUT / "Image.gz-dtb"
    kernel.write_bytes(gzip.compress((BASE / "Image").read_bytes(), compresslevel=6, mtime=0) + dtb.read_bytes())
    image = OUTPUT / "portal-omarchy-wcd-mic.img"
    manifest = json.loads((BASE / "manifest.json").read_text())
    cmdline = manifest["cmdline"].replace("loglevel=7 panic=30", "loglevel=4 panic=30")
    subprocess.run([
        "python3", str(ROOT / "tools/android-tools/usr/share/android-tools/mkbootimg/mkbootimg.py"),
        "--kernel", str(kernel), "--ramdisk", str(BASE / "native-initramfs.cpio.gz"),
        "--cmdline", cmdline, "--base", "0x0", "--kernel_offset", "0x8000",
        "--ramdisk_offset", "0x1000000", "--tags_offset", "0x100", "--pagesize", "4096",
        "--header_version", "0", "--os_version", "13.0.0", "--os_patch_level", "2026-10",
        "-o", str(image),
    ], check=True)
    if image.stat().st_size >= 96 * 1024**2:
        raise SystemExit("Candidate exceeds the boot image size limit")
    result = {
        "board": model, "candidate": image.name, "sha256": sha(image),
        "bytes": image.stat().st_size, "baseline_sha256": baseline_sha,
        "kernel_image_sha256": sha(BASE / "Image"),
        "ramdisk_sha256": sha(BASE / "native-initramfs.cpio.gz"),
        "baseline_dtb_sha256": sha(source_dtb), "candidate_dtb_sha256": sha(dtb),
        "added_audio_routes": ROUTES, "status": "staged; not a hardware acceptance pass",
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
