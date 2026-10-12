#!/bin/bash
# Build upstream linux-msm/qbootctl against our staged ARM userspace.
# qbootctl: Caleb Connolly, The Linux Foundation and contributors (see its notices).
# This prepares files only. It does not inspect or change device slot metadata.
set -euo pipefail
task_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
source_dir="$task_root/references/qbootctl"
rootfs_dir="$task_root/build/native-rootfs/rootfs"
output_dir="$task_root/build/qbootctl"
expected_ref=39a6e6daaf029fb0a083777679a15ea2c18f72de
[[ $(git -C "$source_dir" rev-parse HEAD) == "$expected_ref" ]]
[[ -z $(git -C "$source_dir" status --porcelain) ]]
[[ -x "$rootfs_dir/usr/bin/gcc" ]]
mkdir -p "$output_dir"
scratch=$(sudo -n mktemp -d "$rootfs_dir/tmp/odin-qbootctl.XXXXXXXX")
trap 'sudo -n rm -rf -- "$scratch"' EXIT
tar -C "$source_dir" --exclude=.git -cf - . | sudo -n tar -C "$scratch" -xf -
inside=${scratch#"$rootfs_dir"}
sudo -n chroot "$rootfs_dir" /usr/bin/gcc -O2 -std=gnu11 -I "$inside" \
    "$inside/qbootctl.c" "$inside/bootctrl_impl.c" "$inside/gpt-utils.c" \
    "$inside/ufs-bsg.c" "$inside/crc32.c" -o "$inside/qbootctl"
sudo -n install -m755 "$scratch/qbootctl" "$output_dir/qbootctl"
# Ship the exact unmodified sources and notices alongside the binary artifact.
tar -C "$source_dir" --exclude=.git -czf "$output_dir/qbootctl-source.tar.gz" .
printf '%s\n' "$expected_ref" > "$output_dir/source-ref"
file "$output_dir/qbootctl"
sha256sum "$output_dir/qbootctl" "$output_dir/qbootctl-source.tar.gz"
echo 'Prepared only; no Portal slot-metadata mutation has been performed.'
