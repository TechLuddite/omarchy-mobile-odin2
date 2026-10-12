#!/bin/bash
set -euo pipefail
root=/out/rootfs
reference=/input/references/omarchy-mobile
omarchy_ref=0534987009061cbe2dacdde4ad564092ab698d12
key=3CA83612E7F3108F442006B418305B893569BAD3
mkdir -p /out /work/moarchy-keyring
tar -xf /input/downloads/moarchy-keyring-20260906-1-any.pkg.tar.xz -C /work/moarchy-keyring
keyfile=/work/moarchy-keyring/usr/share/pacman/keyrings/moarchy.gpg
gpg --show-keys --with-colons "$keyfile" | awk -F: '$1=="fpr" {print $10}' | grep -qx "$key"
pacman-key --add "$keyfile"
pacman-key --lsign-key "$key"
pacman-key --verify /input/downloads/moarchy-keyring-20260906-1-any.pkg.tar.xz.sig /input/downloads/moarchy-keyring-20260906-1-any.pkg.tar.xz
cat >> /etc/pacman.conf <<'EOF'

[moarchy]
SigLevel = Required DatabaseOptional
Server = https://github.com/SimonSchubert/moarchy/releases/download/repo
EOF
pacman -Sy --noconfirm
mapfile -t packages < <(sed 's/#.*//; /^[[:space:]]*$/d' "$reference/vm/packages/session" |
    grep -vxE 'linux-aarch64|vulkan-swrast|moarchy-keyring|moarchy-keyboard')
packages+=(vulkan-freedreno epiphany nautilus gnome-text-editor neovim inputplumber python bluez bluez-utils)
printf '%s\n' "${packages[@]}" > /out/requested-packages.txt
if [[ ! -f "$root/etc/os-release" ]]; then
    mkdir -p "$root"
    chown 0:0 "$root"
    pacstrap -K -M "$root" "${packages[@]}"
else
    # QEMU user emulation cannot provide Landlock for pacman's downloader.
    grep -q '^DisableSandbox' "$root/etc/pacman.conf" || sed -i '/^\[options\]/a DisableSandbox' "$root/etc/pacman.conf"
    sed -i 's/^CheckSpace$/#CheckSpace/' "$root/etc/pacman.conf"
    arch-chroot "$root" pacman -Syu --needed --noconfirm "${packages[@]}"
fi
sed -i 's/^CheckSpace$/#CheckSpace/' "$root/etc/pacman.conf"
install -Dm644 /etc/pacman.d/mirrorlist "$root/etc/pacman.d/mirrorlist"
mkdir -p "$root/root/local-packages"
cp /input/downloads/moarchy-keyring-20260906-1-any.pkg.tar.xz{,.sig} "$root/root/local-packages/"
cp /input/downloads/moarchy-keyboard-0.1.0-5-aarch64.pkg.tar.xz{,.sig} "$root/root/local-packages/"
cp /input/downloads/xdg-terminal-exec-0.14.3-1-any.pkg.tar.xz{,.sig} "$root/root/local-packages/"
install -Dm644 "$keyfile" "$root/root/moarchy.gpg"
arch-chroot "$root" pacman-key --add /root/moarchy.gpg
arch-chroot "$root" pacman-key --lsign-key "$key"
arch-chroot "$root" /bin/bash -c 'pacman -U --needed --noconfirm /root/local-packages/*.pkg.tar.xz'

mkdir -p /work/omarchy
curl -fL --retry 2 "https://github.com/basecamp/omarchy/archive/$omarchy_ref.tar.gz" -o /work/omarchy.tar.gz
tar -xf /work/omarchy.tar.gz -C /work/omarchy --strip-components=1
for patch in "$reference"/patches/*.patch; do
    patch -d /work/omarchy -p1 --fuzz=0 < "$patch"
done
mkdir -p "$root/usr/share/omarchy" "$root/usr/bin" "$root/etc/skel/.config"
for directory in shell config default themes applications migrations install; do
    cp -a "/work/omarchy/$directory" "$root/usr/share/omarchy/"
done
for file in version icon.png icon.txt logo.svg logo.txt LICENSE; do
    [[ ! -f /work/omarchy/$file ]] || cp "/work/omarchy/$file" "$root/usr/share/omarchy/"
done
install -m755 /work/omarchy/bin/* "$root/usr/bin/"
install -Dm644 /work/omarchy/etc/profile.d/omarchy.sh "$root/etc/profile.d/omarchy.sh"
cp -a /work/omarchy/config/. "$root/etc/skel/.config/"
cp -a "$reference/default/." "$root/"
python /input/native/fix-qt-color.py "$root/usr/share/omarchy/shell" "$root/etc/skel/.config/omarchy/plugins"
find "$root" -path "$root/home/techluddite" -prune -o -uid 1000 -exec chown -h 0:0 {} +
cp /input/native/configure-rootfs.sh "$root/root/configure-native.sh"
install -Dm755 /input/native/usb-gadget.sh "$root/usr/local/sbin/omarchy-usb-gadget"
cp /input/private/bootstrap/client.pub "$root/root/bootstrap-client.pub"
cp /input/private/native-user-password "$root/root/native-user-password"
arch-chroot "$root" /bin/bash /root/configure-native.sh
mkdir -p "$root/root/gamepad-assets" "$root/root/controller-control"
cp -a /input/native/. "$root/root/gamepad-assets/"
cp -a /input/plugins/controller-control/. "$root/root/controller-control/"
arch-chroot "$root" /bin/bash /root/gamepad-assets/install-gamepad.sh /root/gamepad-assets /root/controller-control
rm -rf "$root/root/gamepad-assets" "$root/root/controller-control"
rm -f "$root/root/native-user-password" "$root/root/bootstrap-client.pub" "$root/root/configure-native.sh"
arch-chroot "$root" pacman -Q > /out/installed-packages.txt
sed -i '/^DisableSandbox$/d; s/^#CheckSpace$/CheckSpace/' "$root/etc/pacman.conf"
echo 'Native Omarchy rootfs assembled; device kernel/firmware and boot files are staged separately.'
