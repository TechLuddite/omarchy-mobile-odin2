#!/usr/bin/env python3
"""Build empty AVB metadata for the unlocked, single-OS Portal boot chain.

Uses the Android Open Source Project's avbtool, downloaded separately under
ignored tools/. This creates a host artifact only; it never flashes a device.
See docs/boot-recovery.md for the actual test and retained original images.
"""
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TOOL_SHA = "e5a664a38db623da00f080219bc0ee60a640a9dc4a872803616fae4938ac749b"
SOURCE = "https://android.googlesource.com/platform/external/avb/+/761178607206f4cb2af79ed9eec52d8cbd814adb/avbtool.py?format=TEXT"


def main():
    tool = ROOT / "tools/avbtool.py"
    if hashlib.sha256(tool.read_bytes()).hexdigest() != TOOL_SHA:
        raise SystemExit(f"Obtain the reviewed AOSP avbtool source: {SOURCE}")
    output = ROOT / "build/bootstrap/vbmeta-native-unlocked.img"
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["python3", str(tool), "make_vbmeta_image", "--flags", "3",
                    "--padding_size", "65536", "--output", str(output)], check=True)
    data = output.read_bytes()
    if len(data) != 65536 or data[:4] != b"AVB0" or struct.unpack_from(">I", data, 120)[0] != 3:
        raise SystemExit("Unexpected AVB output")
    result = {"file": output.name, "bytes": len(data),
              "sha256": hashlib.sha256(data).hexdigest(),
              "source_url": SOURCE, "tool_sha256": TOOL_SHA,
              "flags": 3, "descriptors": [], "requires_unlocked_bootloader": True}
    output.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
