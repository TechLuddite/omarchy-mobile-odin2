# Boot recovery investigation — October 12, 2026

After the first native internal boot, both ABL slots and raw boot slots were
changed to native files. That later redundant boot-chain state had not received
a fresh reboot acceptance test. The microphone test reboot exposed an error.

The microphone candidate used exactly the proven kernel, ramdisk and command
line. A decompiled DTB comparison shows only WCD DMIC2/3 board route additions.
Candidate SHA256:
`b48f0d1beb49cb9c2ee8970c43de98d603c9e48f0fe27ce46a9c62ff5562bc57`.
It was installed in the ESP's `KERNEL`; `KERNEL.bak`, both raw boot slots and the
read-only recovery copy retained the proven image. The UCM probe was backed up
as `/root/odin-hifi-before-wcd-test.conf`. The reboot reported “error booting.”

This does not establish that the DTB route change caused the error. Fastboot
also rejected the unchanged previously booted native image and RAM bootstrap
with `Failed to load/authenticate boot image: Load Error`. Both slots initially
reported unbootable; A reported unsuccessful. Resetting A, then both slots,
and restarting the loader removed the unbootable flags but did not resolve
image rejection. Reflashing the same proven `boot_a` also did not resolve it.

[Linaro's SM8550 guidance](https://devboardsforandroid.linaro.org/en/latest/devices/sm8x50.html)
describes loader recovery and stale Android boot metadata. The original slot-A
vendor-boot v4 image was extracted from verified `lun4.img` before erasing
`vendor_boot_a`; its 96 MiB SHA256 is
`222dd72553b325b28fc9229cd42a1f5d4043e807d5fbc2ce965793b5943b9828`.
That diagnostic alone did not resolve rejection. B's vendor boot was unchanged.

`scripts/build-esp-recovery.py` creates a 512 MiB FAT32 recovery image with the
proven `KERNEL`, identical `KERNEL.bak`, and saved RAM `RECOVERY.img`. It verifies
source digests and reads all three files back through mtools. Fastboot recognizes
`OMARCHY_BOOT` with the expected 512 MiB size. The ESP image flashed successfully,
removing the microphone candidate without replacing the installed root or GPT.
Its SHA256 is `71774e7c4cc365cf68431252b9722356969611cce2a54c2d1013744cf41f1bb5`.
Fastboot `continue` still reported a partition load error afterward.

Stock AVB metadata still describes the removed Android system. An empty
unsigned 64 KiB native vbmeta image with flags 3 and no descriptors was made
with upstream AOSP avbtool 1.3.0 and installed in `vbmeta_a` for the unlocked
Linux boot. Original `vbmeta_a` was extracted before the write, SHA256
`bd0540e9becf4108f15de490999b353fbb521e44144a7cd9af59aaeedfc727ca`.
After the vbmeta change and loader restart, fastboot accepted the unchanged
proven native image (`Booting OKAY`). USB ECM/SSH has not yet reappeared, so this
is loader acceptance, not a successful running-system acceptance. Bootloader
mode/source/model and the physical screen still need confirmation. Slot B's
verification metadata is unchanged. `scripts/build-native-vbmeta.py` records
the exact AOSP source and verifies it before reproducing this host artifact.

Qualcomm boot-success handling needs a permanent fix before repeated reboot
tests. [linux-msm/qbootctl](https://github.com/linux-msm/qbootctl), pin
`39a6e6daaf029fb0a083777679a15ea2c18f72de`, implements GPT-based slot attributes.
It is a research checkout, not yet installed or tested on this Portal. This
layout differs from generic Android `misc` metadata; do not write an assumed
`misc` boot-control structure as a fix.

Evidence and images remain under ignored `private/` and `build/`. The verified
base backup and GPT recovery evidence were retained throughout. Boot stability
and cold-start acceptance remain open until recovery is complete.
