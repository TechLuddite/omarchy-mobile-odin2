#!/bin/bash
# Offline install of Peter Jackson's signature-verified Voxtype 1.1.0 ARM64 CPU release.
# Run as root: install-dictation.sh /path/to/voxtype-1.1.0-linux-aarch64-cpu /path/to/native
# Then run configure-dictation.sh as the desktop user inside its active session.
set -euo pipefail
if (( EUID != 0 )) || [[ $(uname -m) != aarch64 ]]; then
    echo 'Run on the ARM64 Odin as root.' >&2
    exit 1
fi
binary=${1:?Provide the verified Voxtype binary}
assets=${2:?Provide this project\'s native asset directory}
python3 - "$binary" <<'PY'
import hashlib, pathlib, sys
expected = '2fcf0945d424a116c1947ea738da1afa9f83abbae66cebb53f06189111a6f392'
actual = hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest()
if actual != expected:
    raise SystemExit('Voxtype digest does not match the verified ARM64 release')
PY
install -Dm755 "$binary" /usr/local/bin/voxtype
install -Dm755 "$assets/odin-microphone-check" /usr/local/bin/odin-microphone-check
install -Dm644 "$assets/microphone-check.desktop" /usr/local/share/applications/microphone-check.desktop
update-desktop-database /usr/local/share/applications
/usr/local/bin/voxtype --version
echo 'Next: run configure-dictation.sh as the desktop user. See docs/dictation.md.'
