#!/bin/bash
# Configure persistent key-only maintenance on this Portal, with Wi-Fi mDNS.
# Uses OpenSSH, NetworkManager and Avahi; preserves their upstream configuration.
set -euo pipefail
assets=$(cd -- "$(dirname -- "$0")" && pwd)
public_key=${1:?Usage: install-maintenance-ssh.sh CLIENT_PUBLIC_KEY}
[[ $(id -u) == 0 && $(uname -m) == aarch64 ]] || {
    echo 'Run as root on the ARM64 Portal' >&2; exit 1;
}
[[ $(tr -d '\0' < /sys/firmware/devicetree/base/model) == 'AYN Odin 2 Portal' ]]
[[ -f "$public_key" && -f "$assets/maintenance-ssh.conf" ]]
ssh-keygen -l -f "$public_key" >/dev/null
python3 - "$public_key" <<'PY'
from pathlib import Path
import sys
lines = Path(sys.argv[1]).read_text().strip().splitlines()
assert len(lines) == 1 and lines[0].startswith('ssh-ed25519 '), 'Expected one Ed25519 public key'
PY
backup=/root/native-transition/ssh-maintenance-$(date -u +%Y%m%dT%H%M%SZ)
install -d -m700 "$backup" /root/.ssh
cp -a /etc/ssh/sshd_config.d "$backup/sshd_config.d"
cp -a /etc/avahi/avahi-daemon.conf "$backup/avahi-daemon.conf"
if [[ -f /root/.ssh/authorized_keys_maintenance ]]; then
    cp -a /root/.ssh/authorized_keys_maintenance "$backup/authorized_keys_maintenance"
fi
install -m600 "$public_key" /root/.ssh/authorized_keys_maintenance
install -m644 "$assets/maintenance-ssh.conf" /etc/ssh/sshd_config.d/20-maintenance.conf
# The new key-only root rule replaces the earlier USB-address-only rule.
rm -f /etc/ssh/sshd_config.d/20-usb-maintenance.conf
if ! sshd -t; then
    rm -f /etc/ssh/sshd_config.d/20-maintenance.conf
    cp -a "$backup/sshd_config.d/." /etc/ssh/sshd_config.d/
    echo "Invalid SSH configuration; restored previous drop-ins from $backup" >&2
    exit 1
fi
# Advertise only Wi-Fi so .local cannot resolve to the disconnected USB link.
python3 - <<'PY'
from pathlib import Path
path = Path('/etc/avahi/avahi-daemon.conf')
lines = path.read_text().splitlines()
output, section = [], None
for line in lines:
    stripped = line.strip()
    if stripped.startswith('[') and stripped.endswith(']'):
        section = stripped
        output.append(line)
        if section == '[server]':
            output.extend(['host-name=odin2portal', 'allow-interfaces=wlp1s0'])
        continue
    if section == '[server]' and stripped.split('=', 1)[0] in ('host-name', 'allow-interfaces'):
        continue
    output.append(line)
assert '[server]' in output
path.write_text('\n'.join(output) + '\n')
PY
systemctl enable --now sshd avahi-daemon
systemctl reload sshd
systemctl restart avahi-daemon
echo "Key-only root maintenance enabled; configuration backup: $backup"
echo 'Wi-Fi hostname: odin2portal.local; desktop account and sudo password unchanged'
