#!/bin/bash
# Portal Bluetooth integration: BlueZ/Blueman authentication and Simon's panel.
set -euo pipefail
assets=$(cd -- "$(dirname -- "$0")" && pwd)
[[ $(id -u) == 0 && $(uname -m) == aarch64 ]]
[[ $(tr -d '\0' < /sys/firmware/devicetree/base/model) == 'AYN Odin 2 Portal' ]]
if ! pacman -Q blueman >/dev/null 2>&1; then
    # The running Portal kernel cannot provide pacman's filesystem sandbox.
    # Keep this exception per invocation rather than changing global policy.
    pacman -S --disable-sandbox-filesystem --needed --noconfirm blueman
fi
install -Dm755 "$assets/odin-bluetooth-device" /usr/local/bin/odin-bluetooth-device
python3 "$assets/fix-bluetooth-pairing.py" \
    /home/techluddite/.config/omarchy/plugins/mobile.shell/BluetoothScreen.qml
systemctl enable --now bluetooth
# The packaged unit is static/D-Bus activated; tie it to the desktop session.
runuser -u techluddite -- env XDG_RUNTIME_DIR=/run/user/1000 \
    DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
    systemctl --user add-wants graphical-session.target blueman-applet.service
runuser -u techluddite -- env XDG_RUNTIME_DIR=/run/user/1000 \
    DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
    systemctl --user start blueman-applet.service
# Keep pairing codes/confirmation in a visible GTK dialog for touch use.
runuser -u techluddite -- env XDG_RUNTIME_DIR=/run/user/1000 \
    DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
    gsettings set org.blueman.general notification-daemon false
runuser -u techluddite -- env XDG_RUNTIME_DIR=/run/user/1000 \
    DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus python3 - <<'PY'
from gi.repository import Gio
settings = Gio.Settings.new('org.blueman.general')
plugins = [item for item in settings.get_strv('plugin-list')
           if item.lstrip('!') != 'ConnectionNotifier']
plugins.append('!ConnectionNotifier')
assert settings.set_strv('plugin-list', plugins)
Gio.Settings.sync()
PY
echo 'BlueZ authentication dialogs available through Blueman; no bond checks disabled'
