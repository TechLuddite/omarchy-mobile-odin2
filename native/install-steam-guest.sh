#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# RootFS/Turnip overlay adapted from Shuuri Labs / pocknix-os fex-rootfs
# ba1de097fb0e0df07bcb32f05dc8e957d62090bc. Retain licenses/pocknix-GPL-2.0.txt.
# No host distro packages or Steam game files are replaced.
set -euo pipefail
[[ $EUID == 0 && $(uname -m) == aarch64 ]] || { echo 'Run as root on ARM64' >&2; exit 1; }
[[ $(tr -d '\0' </sys/firmware/devicetree/base/model) == 'AYN Odin 2 Portal' ]] || exit 1
[[ $# == 1 ]] || { echo 'Usage: install-steam-guest.sh VERIFIED_DOWNLOAD_DIRECTORY' >&2; exit 2; }
cd "$1"
sha256sum --check <<'HASHES'
cb059973b7953ad9165845529655189b96f9a174b14a6a149c87ec884b0c5e90  ArchLinux-2026-01-08.sqsh
da30385afabfee1fba0456ff03e1a4f9d8168dc12679323f90bd496e5259e435  vulkan-freedreno-26.2.4-1-x86_64.pkg.tar.zst
07ab1479ec5e70aea174e2d0e340bd9364b507ed74f2df3bfd51b3c6f40e5787  libdisplay-info-0.3.0-1-x86_64.pkg.tar.zst
312213911881c0742e2a825432feac761e863945b74bb3a6daca97a99778d35e  xcb-util-keysyms-0.4.1-5-x86_64.pkg.tar.zst
HASHES
guest_base=/usr/local/share/odin-steam/guest
[[ ! -e "$guest_base" && ! -e /usr/share/guestos/fex-mesa ]] || { echo 'Existing guest runtime found; inspect before replacing' >&2; exit 1; }
install -d "$guest_base/overlay"
install -m 644 ArchLinux-2026-01-08.sqsh "$guest_base/ArchLinux.sqsh"
tar --zstd -xf vulkan-freedreno-26.2.4-1-x86_64.pkg.tar.zst -C "$guest_base/overlay" usr/lib/libvulkan_freedreno.so usr/share/licenses
tar --zstd --wildcards -xf libdisplay-info-0.3.0-1-x86_64.pkg.tar.zst -C "$guest_base/overlay" 'usr/lib/libdisplay-info.so*' 'usr/share/licenses/*'
tar --zstd --wildcards -xf xcb-util-keysyms-0.4.1-5-x86_64.pkg.tar.zst -C "$guest_base/overlay" 'usr/lib/libxcb-keysyms.so*' 'usr/share/licenses/*'
# Match the original Arch image's suffixed ICDs; adding another ICD would
# enumerate the same GPU twice. Only its library and missing dependencies change.
cat > "$guest_base/overlay/graphics_provider.json" <<'JSON'
{
  "graphics_provider_v0": {
    "architectures": ["x86_64-linux-gnu", "i386-linux-gnu"]
  }
}
JSON
echo 'Verified x86 runtime installed; install and enable odin-steam-guest.service.'
