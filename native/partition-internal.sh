#!/bin/sh
# Concrete Portal-only plan: replace userdata with an ESP and native ext4 root.
set -eu
tool() { chroot /run/install-tools "/usr/bin/$@"; }
test "$(cat /proc/device-tree/model | tr -d '\000')" = 'AYN Odin 2 Portal'
test "$(cat /sys/class/block/sda/size)" = 1973878784
test "$(cat /sys/class/block/sda/queue/logical_block_size)" = 4096
test "$(cat /sys/class/block/sda17/start)" = 15662328
test "$(cat /sys/class/block/sda17/size)" = 1958216416
test "$(sed -n 's/^PARTNAME=//p' /sys/class/block/sda17/uevent)" = userdata
! awk '$1 ~ /^\/dev\/sd/ {found=1} END {exit !found}' /proc/mounts
tool sfdisk --dump /dev/sda > /run/lun0-before.sfdisk
tool parted -s /dev/sda rm 17
tool parted -s -a optimal /dev/sda mkpart OMARCHY_BOOT fat32 7648MiB 8160MiB
tool parted -s /dev/sda set 17 esp on
tool parted -s -a optimal /dev/sda mkpart OMARCHY_ROOT ext4 8160MiB 100%
tool partprobe /dev/sda
# BLKPG-created live partition nodes may omit PARTNAME until the next boot.
test "$(tool sfdisk --part-label /dev/sda 17)" = OMARCHY_BOOT
test "$(tool sfdisk --part-label /dev/sda 18)" = OMARCHY_ROOT
test "$(tool blockdev --getsize64 /dev/sda17)" = 536870912
tool sfdisk --json /dev/sda > /run/lun0-after.json
echo 'Partition table prepared; filesystems are not formatted yet.'
