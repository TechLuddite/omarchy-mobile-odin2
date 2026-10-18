#!/bin/bash
set -euo pipefail
# Run as root with this directory and the vendored plugin as arguments.
assets=$1
plugin=$2
install -Dm755 "$assets/omarchy-gamepad-mapping" /usr/local/bin/omarchy-gamepad-mapping
install -Dm755 "$assets/omarchy-mobile-toggle-keyboard" /usr/local/bin/omarchy-mobile-toggle-keyboard
install -Dm644 "$assets/90-omarchy-uinput.rules" /etc/udev/rules.d/90-omarchy-uinput.rules
install -Dm644 "$assets/60-odin2-gamepad-joystick.rules" /etc/udev/rules.d/60-odin2-gamepad-joystick.rules
install -Dm644 "$assets/gamepad-mapping.desktop" /usr/local/share/applications/gamepad-mapping.desktop
echo uinput > /etc/modules-load.d/omarchy-gamepad.conf
for user_home in /etc/skel /home/techluddite; do
    dest="$user_home/.config/omarchy/plugins/co.klair.controller-control"
    install -d "$dest"
    tar -C "$plugin" --exclude=.git --exclude=__pycache__ -cf - . | tar -C "$dest" -xf -
    if [[ ! -e "$user_home/.config/controller-control/config.json" ]]; then
        install -Dm644 "$assets/controller-control.json" "$user_home/.config/controller-control/config.json"
    fi
    python3 - "$user_home/.config/omarchy/shell.json" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text())
plugin_id = 'co.klair.controller-control'
entries = d.setdefault('plugins', [])
if not any((e.get('id') if isinstance(e, dict) else e) == plugin_id for e in entries):
    entries.append({'id': plugin_id})
d['disabledPlugins'] = [e for e in d.get('disabledPlugins', []) if e != plugin_id]
p.write_text(json.dumps(d, indent=2) + '\n')
PY
done
chown -R root:root /etc/skel/.config/omarchy/plugins/co.klair.controller-control /etc/skel/.config/controller-control
chown -R techluddite:techluddite /home/techluddite/.config/omarchy/plugins/co.klair.controller-control /home/techluddite/.config/controller-control
