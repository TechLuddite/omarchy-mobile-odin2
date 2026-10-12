#!/bin/bash
set -euo pipefail
echo odin2portal > /etc/hostname
ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime
sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
echo LANG=en_US.UTF-8 > /etc/locale.conf
echo KEYMAP=us > /etc/vconsole.conf
cat > /etc/fstab <<'EOF'
PARTLABEL=OMARCHY_ROOT / ext4 rw,relatime 0 1
PARTLABEL=OMARCHY_BOOT /boot vfat rw,noatime,fmask=0137,dmask=0027 0 2
LABEL=OMARCHY_RECOV /recovery ext4 ro,nofail,nodev,nosuid,noexec 0 2
EOF
install -d -m700 /recovery
cat > /etc/skel/.config/hypr/monitors.lua <<'EOF'
-- Portal display settings; validate the connector and rotation on hardware.
hl.monitor({ output = "DSI-1", mode = "preferred", position = "0x0", scale = 1.5, transform = 1 })
EOF
cat >> /etc/skel/.config/hypr/input.lua <<'EOF'

-- Portal touchscreen follows the landscape panel.
hl.config({ input = { touchdevice = { output = "DSI-1", transform = 1 } } })
EOF
if ! grep -q 'require("hypr.mobile")' /etc/skel/.config/hypr/hyprland.lua; then
    printf '\nrequire("hypr.mobile")\n' >> /etc/skel/.config/hypr/hyprland.lua
fi
python3 - <<'PY'
import json,pathlib
p=pathlib.Path('/etc/skel/.config/omarchy/shell.json')
d=json.loads(p.read_text());d.setdefault('bar',{})['id']='mobile.shell';p.write_text(json.dumps(d,indent=2)+'\n')
PY
systemd-sysusers
systemd-tmpfiles --create || true
if ! id techluddite >/dev/null 2>&1; then
    useradd -m -G wheel,video,input,audio,storage -s /bin/bash techluddite
fi
password=$(cat /root/native-user-password)
printf 'techluddite:%s\n' "$password" | chpasswd
passwd -l root
install -d -m700 -o techluddite -g techluddite /home/techluddite/.ssh
install -m600 -o techluddite -g techluddite /root/bootstrap-client.pub /home/techluddite/.ssh/authorized_keys
echo '%wheel ALL=(ALL:ALL) ALL' > /etc/sudoers.d/wheel
chmod 440 /etc/sudoers.d/wheel
install -d /etc/systemd/system/getty@tty1.service.d
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf <<'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin techluddite --noclear %I $TERM
EOF
cat > /home/techluddite/.bash_profile <<'EOF'
[[ -f ~/.bashrc ]] && . ~/.bashrc
if uwsm check may-start >/dev/null 2>&1; then
  exec uwsm start -- hyprland-uwsm.desktop
fi
EOF
chown techluddite:techluddite /home/techluddite/.bash_profile
cat > /etc/ssh/sshd_config.d/10-native.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
EOF
systemctl enable NetworkManager sshd systemd-timesyncd
systemctl enable seatd power-profiles-daemon avahi-daemon
systemctl enable bluetooth
if ! grep -q '^\[moarchy\]' /etc/pacman.conf; then
    cat >> /etc/pacman.conf <<'EOF'

[moarchy]
SigLevel = Required DatabaseOptional
Server = https://github.com/SimonSchubert/moarchy/releases/download/repo
EOF
fi
systemctl mask NetworkManager-wait-online
install -d /etc/NetworkManager/conf.d
cat > /etc/NetworkManager/conf.d/90-omarchy-usb.conf <<'EOF'
[keyfile]
unmanaged-devices=interface-name:usb0
EOF
cat > /etc/systemd/system/omarchy-usb-gadget.service <<'EOF'
[Unit]
Description=Odin2 Portal USB Ethernet access
After=systemd-udev-settle.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/omarchy-usb-gadget
RemainAfterExit=yes
TimeoutStartSec=90

[Install]
WantedBy=multi-user.target
EOF
systemctl enable omarchy-usb-gadget
# True suspend is a separate hardware acceptance milestone.
systemctl mask suspend.target hibernate.target hybrid-sleep.target
install -d /etc/omarchy-mobile /etc/omarchy-native
cat > /etc/omarchy-mobile/release <<'EOF'
VERSION=0.1.0-odin2portal
OMARCHY_VERSION=v4.0.3
OMARCHY_REF=0534987009061cbe2dacdde4ad564092ab698d12
EOF
echo 'AYN Odin 2 Portal' > /etc/omarchy-native/model
install -d /etc/skel/.local/state/omarchy/current
sudo -u techluddite bash -lc 'omarchy-theme-set tokyo-night' || true
