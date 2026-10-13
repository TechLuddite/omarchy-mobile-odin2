# Boot recovery investigation — October 12, 2026

Current result: normal internal boot is restored and slot A is marked successful.
The [repaired checkpoint](#repaired-installed-boot-checkpoint) records the
verified outcome. Earlier sections below are the chronological investigation;
their pending checks were resolved where described later in the record.

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

`scripts/build-qbootctl.sh` successfully compiled the unchanged pinned source
against the staged ARM userspace. The output is an AArch64 ELF, SHA256
`c8781410e4514d3f86c385944e28e3ee72396f85f4e688a46677ef41a3437b27`.
The exact original sources and notices are packaged beside it. Compilation is
not a hardware test; neither this binary nor a boot-success service has been
deployed. Inspect read-only slot information first after Linux access returns.

When access returns, restore the pre-WCD UCM probe from
`/root/odin-hifi-before-wcd-test.conf` before ordinary capture tests. The ESP
rollback restored the kernel files, not the root's experimental UCM file.
Do not claim that all microphone configuration was reverted. Test normal
internal reboot after the boot metadata fix before trying another candidate.

Evidence and images remain under ignored `private/` and `build/`. The verified
base backup and GPT recovery evidence were retained throughout. Boot stability
and cold-start acceptance remain open until recovery is complete.

## Fresh physical check after the camera returned

At 17:17 UTC, the Razer Kiyo Pro enumerated again as `1532:0e05` with a usable
V4L2 capture node. A fresh photograph confirmed Linux mode, Auto source and
AYN Odin 2 Portal selected in ROCKNIX 1.1.8. Fastboot reported active slot A
and unbootable=no. A normal `fastboot reboot` was issued with the restored ESP
and slot-A native vbmeta in place. Later camera frames show the Linux penguins
and a text console, establishing progress beyond the loader. USB ECM has not
yet appeared. The console's left/bottom edges are outside the camera framing;
the exact stop message still needs a legible physical capture. Do not infer a
desktop boot pass from the console alone. Photographs and command logs are
saved under ignored `private/bootstrap/`.

The user repositioned the Odin and new captures include the whole console.
Focus/exposure adjustments were tried, but the failure text remains too soft
to transcribe reliably. There are visible Linux console messages and no USB
ECM device. The next step is the verified RAM bootstrap (header v0, digest
`129125049bba685380ced3c186c2f75eb8942954c7f09c9b18646f1875d1a259`),
which starts USB diagnostics without depending on the installed system's
mounts or desktop services. Read the installed boot logs there before choosing
a repair. Do not report an inferred mount error as a confirmed diagnosis.

## Confirmed mount failure and 4 KiB ESP repair

The verified header-v0 RAM bootstrap booted successfully and exposed USB ECM
and SSH. The installed root was first mounted read-only with `noload`. Its saved
system journal was copied privately to the host for reading. The latest normal
boot confirms `FAT-fs (sda17): logical sector size too small for device (logical
sector size = 512)`, followed by `Failed to mount /boot` and a failed Local File
Systems dependency. This is the confirmed console stop, separate from the
earlier stock AVB loader rejection.

The host-file recovery image builder had used mkfs.fat's 512-byte sector default.
The Portal's UFS logical sector size is 4096. This recovery-builder error was
introduced during the ESP rollback; the original device-formatted boot volume
used the device geometry. `scripts/build-esp-recovery.py` now specifies
`-S 4096` and checks the FAT BPB sector-size field before copying files.

The corrected 512 MiB image passed host fsck.fat and mtools file readbacks.
Observed SHA256: `0da2325bab3c0677030de1f1b0417d659cb4d21f5dccf5b778c99c254720ece4`.
`native/repair-esp.py` checked the Portal model, expected partition label,
unmounted target, physical size/sector geometry and image digest before writing
only sda17 from RAM recovery. It flushed and invalidated the block cache, then
verified the full physical-device readback against that digest. The corrected
volume mounts successfully on the Odin. KERNEL, KERNEL.bak and RECOVERY.img
match their previously verified digests, and the fstab verification passes.

The experimental WCD UCM was preserved as `/root/odin-hifi-wcd-experiment.conf`.
The pre-WCD probe was restored from `/root/odin-hifi-before-wcd-test.conf`, with
digest `7f1e20c3ef62b3351c301138da87cbe441ccc19a9b4cb1433057944816f84777`.
This restores the previous microphone configuration; actual speech capture
remains unverified. All recovery mounts were cleanly unmounted before restarting
into the installed system. Record the resulting desktop/USB acceptance below.

## Repaired installed boot checkpoint

The minimal RAM image lacks a reboot applet. After confirming that the ESP and
all installed-root/bind mounts were unmounted and syncing, its supported SysRq
restart was used. The following normal internal boot reached the installed
system: `/boot` mounts sda17 as vfat, `/` is the native root, USB SSH is available,
Hyprland and Quickshell run, and systemd reports zero failed services. A fresh
camera frame and a direct Wayland screenshot confirm the landscape desktop.
Firefox `157.0.1-1` remains installed. This is a normal reboot pass, not a cold
power-off/on or alternate-slot pass.

The previously prepared, unchanged upstream qbootctl binary was installed and
its digest verified. Read-only inspection confirmed A active/bootable but not
successful. Both GPT headers/tables on all six UFS LUNs were CRC-checked and
backed up under `/root/native-transition/boot-success-gpt-before/` before
`qbootctl -m a` marked the now-validated installed boot successful. Readback
reports slot A successful and bootable. The exact source archive and notices
are installed alongside the tool under `/usr/local/share/odin2-omarchy/`.
After marking success, both GPT header/table CRCs and matching primary/secondary
tables passed on all six LUNs. Comparison with the pre-write snapshots confirms
only slot-A boot-success bits and their GPT checksums changed; partition geometry,
names, GUIDs and other attributes are unchanged.
There is no automatic boot-success service yet. B's AVB metadata remains stock
and still needs a separate tested native recovery plan.

## Microphone V3 warm-boot checkpoint — October 13

After a further unchanged-baseline warm reboot passed, the microphone
investigation found actual speech on codec DMIC3/SWR_MIC7. V2 booted but failed
speech acceptance. A revised **V3** image adds only two audio route pairs to the
proven DTB; the decompressed kernel, ramdisk, boot fields and command line
match the proven image. [Dictation notes](dictation.md) record the failed probes,
working channel, credit and measured controlled-speech acceptance.

V3 `/boot/KERNEL` SHA256:
`3c6b2569a964ec8c04b5bc96950df3921d58b016b77d40fd72fa597c10986763`.
The guarded ESP installer checked Portal identity, mounted sda17 vfat,
4096-byte sectors, slot-A success and exact image/config digests before the
write. Normal internal reboot returned Wi-Fi SSH, desktop/audio services and
zero failed units; slot A remains active, bootable and successful. The normal
PipeWire touch app then captured and transcribed the controlled external video
source. This is a warm reboot and acoustic speech pass, not cold-boot or
slot-B acceptance.

KERNEL.bak remains the proven image
`e8b2e3cb289c7db5ef6a430bcb598c78a0b3ea685566138e6fbc7af641409f07`;
RECOVERY.img and raw boot slots were not changed. The ESP still uses its repaired
4096-byte FAT geometry. No AVB/GPT/slot writes were needed for these audio tests.
Earlier candidate build directories remain separate and private.

The pre-V3 UCM is `/root/odin-hifi-before-wcd-v3-test.conf`; it is the temporary
slot7 diagnostic probe, **not** the pre-WCD baseline. For a complete baseline
rollback, verify and restore KERNEL.bak plus
`/root/odin-hifi-before-wcd-v2-test.conf` (SHA256
`7f1e20c3ef62b3351c301138da87cbe441ccc19a9b4cb1433057944816f84777`),
then sync and reboot. Do not use the old recovery-builder image with 512-byte
FAT sectors. The installed V3 full HiFi digest is
`501d382a7d91853ff421dc6111792e63d2ed7b78dbb31c3e5238ee424b5125f8`.
