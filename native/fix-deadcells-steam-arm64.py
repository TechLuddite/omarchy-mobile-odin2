#!/usr/bin/env python3
"""Preserve pressure-vessel's ARM library paths in the inspected game launcher.

Game build 23762174: its two LD_LIBRARY_PATH=. assignments prevent Valve's
FEX executable loading libstdc++.so.6 after container startup. Game-owned code
is not redistributed here. Back up the original privately before changing it.
Steam file verification or an update may restore the original launcher.
"""
import hashlib
from pathlib import Path
import shutil

ORIGINAL_SHA256 = "5132161d5c1479b1a8221a73d44a5558e9fd0766ab7278aeb45f0bf024b49519"
OLD = b"LD_LIBRARY_PATH=. ./deadcells"
NEW = b'LD_LIBRARY_PATH=."${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" ./deadcells'


def main():
    game = Path.home() / ".local/share/Steam/steamapps/common/Dead Cells/deadcells.sh"
    data = game.read_bytes()
    state = Path.home() / ".local/state/odin2-omarchy/steam-guest-install"
    backup = state / "deadcells.sh.before-library-path-fix"
    if backup.exists() and data == backup.read_bytes().replace(OLD, NEW):
        print("Dead Cells library-path fix already applied")
        return
    if hashlib.sha256(data).hexdigest() != ORIGINAL_SHA256 or data.count(OLD) != 2:
        raise SystemExit("Unreviewed game launcher; inspect before changing it")
    if backup.exists():
        raise SystemExit("Existing backup found; inspect before replacing it")
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    shutil.copy2(game, backup)
    game.write_bytes(data.replace(OLD, NEW))
    print("Dead Cells launcher preserves the container's ARM64 library paths")
    print(f"Original saved privately: {backup}")


if __name__ == "__main__":
    main()
