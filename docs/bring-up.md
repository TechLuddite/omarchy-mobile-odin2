# Device access and next steps

Current session: a later reboot exposed a boot-chain failure after Android
retirement. The proven ESP files are restored; slot-A AVB metadata correction
allows fastboot image acceptance again, but a running desktop/USB connection
has not yet returned. Follow [the recovery record](boot-recovery.md) before
resuming microphone or further boot tests. Observations below are historical
acceptance of the earlier state, not a claim that the current reboot passed.

Initial inspection found an AYN device with only an MTP interface (`18d1:4ee1`).
Subsequent camera and USB checks on October 12 confirmed bootloader fastboot
(`18d1:d00d`), product `kalama`, active slot B, two slots, `unlocked: yes` and
`secure: no`. Both slots reported successful and bootable. Fastboot partition
fetch is unsupported. The captured Android vendor filesystem reports
`ro.product.vendor.model=Odin2 Portal`, manufacturer AYN, Android 13, and vendor
build date March 19, 2026. Use the Portal-specific board and firmware configuration.

Selecting **Reboot to emergency mode** on the physical bootloader menu exposed
Qualcomm EDL (`05c6:9008`). The Odin programmer successfully loaded into RAM and
read six UFS GPTs. The device has Samsung UFS with 4096-byte sectors; the large
LUN is about 941 GiB and `userdata` occupies about 934 GiB. The PC-side command
`fastboot oem edl` was rejected; the menu transition worked.

The user has authorized proceeding without preserving personal data. Base
recovery images have been captured before any storage or bootloader writes. All
seven image extents passed SHA256 verification; primary and secondary GPT CRCs
and maps passed on all six LUNs. Independent rereads of both ABL partitions and
`persist` match the images. See [Base image backup](backup.md) for scope and files.

## Read only inspection

If Android boots, enable USB debugging in Developer options and authorize this
computer. Run `python3 scripts/inspect-device.py` from the project root. It reads
named device/build/boot properties, the running kernel and visible partition
information. A shell without root may deny some queries; preserve those results
instead of interpreting missing data as an absent partition.

If only recovery is reachable, record its actual title/options. Fastboot queries
require entering the bootloader, rather than stock Android recovery or its
sideload mode. The inspection helper reads product, slot and security variables
when fastboot is present. These queries do not establish whether custom images
will boot. EDL acceptance also needs separate inspection and compatible tooling.

## Milestones

1. Confirm original Odin 2 vs Mini/Portal, capacity and installed firmware.
   Determine whether Android/root-script access, ADB, fastboot and EDL are usable.
2. Capture the real UFS LUN/GPT map and both A/B boot chains. Save required
   boot/calibration backups off-device with checksums, and identify a recovery
   route that does not depend on an SD card.
3. Choose USB storage, host mass-storage access or a RAM installer. Assemble a
   device-specific kernel/DTB/firmware and prove native boot plus UFS access.
4. Build the ALARM/Omarchy rootfs and native boot files. Replace VM assumptions,
   configure USB access, and adapt the touch UI to the physical landscape panel.
5. Prepare a concrete single-OS partition/installation plan from the observed
   layout. Reclaim Android userspace while preserving required platform firmware
   and calibration. Install and validate internal cold boot.
6. Work through `hardware.md`, recording each subsystem's observed behavior and
   remaining defects. Package kernel/BSP updates and verify recovery/rollback.

## Native bring-up observed on October 12

ROCKNIX ABL 1.1.8 from the checksum-verified September 1 release was written to
`abl_a`. Slot A's original ABL, init_boot and dtbo are saved privately; init_boot_a
and dtbo_a were cleared and slot A selected. Stock fastboot RAM boots did not
produce a running Linux system. The same Portal-specific header-v0 RAM image
booted successfully after installing ROCKNIX ABL. Linux 7.2.0 reports the correct
Portal model, CPUs 0–7 and approximately 15 GiB usable RAM. USB ECM networking,
HTTP diagnostics and SSH are functional. DRM exposes DSI-1 and renderD128; the
camera shows a native Linux console. Touch, gamepad, haptics, brightness, LEDs
and thermal devices enumerate, but their functional acceptance remains open.

The native RAM installer replaced only the former userdata GPT entry with a
512 MiB FAT32 ESP named OMARCHY_BOOT and an ext4 OMARCHY_ROOT using the remaining
space. The preceding 16 GPT entries match the original exactly. The 32-entry
GPT table was retained; growing it would overlap the first stock partition.
There is no retained Android userdata partition. About 917 GiB is available in
the formatted root filesystem before installing files. After the internal boot succeeded, Android super was replaced by the native
recovery filesystem. Both boot partitions now hold the verified native image,
and both ABL partitions hold ROCKNIX 1.1.8. Slot B init_boot/dtbo were cleared.
The per-device firmware and calibration partitions remain intact.

The Arch Linux ARM filesystem contains pinned Omarchy 4.0.3 with the pinned
omarchy-mobile patches/overlay, native Freedreno/Turnip userspace, the matching
ROCKNIX modules and firmware, USB SSH access, and Portal display configuration.
It was copied with numeric ownership, ACLs and extended attributes. The package
database consistency check and Hyprland's configuration parser pass on the
physical ARM device. KERNEL, KERNEL.bak and RECOVERY.img are staged on the ESP;
on-device SHA256 checks match the host. Uploading the native boot image through
fastboot starts systemd and the installed Omarchy desktop, with `/` on sda18 and
`/boot` on sda17. Hyprland and Quickshell run, and systemd reports no failed
services. Normal internal ESP boot subsequently succeeded without uploading a kernel
from the PC. Cold power-off/on and the later redundant boot-chain changes still
need a boot acceptance check.

The first normal internal boot reached ROCKNIX's "device model not set" error.
The installed 1.1.8 menu offers Auto, SD and USB as boot sources, rather than
the newer documentation's explicit Internal option. Auto is selected for the
internal test. SM8550 requires selecting AYN Odin 2 Portal in the bootloader's
device-model menu, independently of the model shown in its hardware inventory.
The image contains only the Portal DTB. The user selected the Portal model,
and the normal internal boot reached the installed Omarchy session.

The panel's initial transform=3 was physically upside down. The user reported
this, and transform=1 now rotates the output by 180 degrees relative to that
setting. Hyprland reload/configerrors pass, and this correction is in the builder.
The selected mode is 1080×1920 at 120 Hz, rotated to landscape, with scale 1.5.

Qt 6.12 introduced a QtQuick.Color singleton that shadows the pinned shell's
qs.Commons.Color. This produced undefined color roles and an invisible bar.
`native/fix-qt-color.py` caps relevant QtQuick imports at API 6.11 in the pinned
shell and mobile overlay. After restart the bar, time, network and battery are
visible, and the color-role warnings are gone. The port remains on its pinned
Omarchy/mobile revisions. See [Qt's Color type](https://doc.qt.io/qt-6.12/qml-qtquick-color.html).

Native EGL reports Freedreno FD740 on Wayland/GBM; Vulkan reports Turnip Adreno
740. The user joined Wi-Fi from the mobile UI; native HTTPS requests work. Battery percentage and charging state are visible.
WirePlumber exposes speaker and headphone sinks; audible playback is not yet
verified. Bluetooth powers on after adding bluez/bluez-utils. Microphone capture,
pairing, physical gamepad controls, power policy and suspend remain open. The
user confirmed touch gestures and keyboard dismissal after input transform 1.
Controller Control is adapted as a normal-window Gamepad Mapping editor, with
blank initial bindings and nonexclusive access. Its 44 upstream tests pass on
the ARM device; physical recording awaits user input. Omakade 1.16.1 is installed
from the signed btsouth ARM64 repository, renders in the native Wayland desktop,
and has its session service enabled. The initial SSH invocation without display
environment aborted during Qt platform initialization; a Wayland launch works.
Its optional `omakade.guide` overlay requires an OverlayWindow type absent from
the pinned Omarchy shell. That overlay is disabled until compatibility is fixed;
the library UI and session service remain functional. Two additional device
selection tests and five shortcut-catalog tests pass on ARM, for 51 total mapper tests.
Step 2 now reads all 223 live Omarchy shortcuts into a touch dropdown; saving
fills the description automatically and requires no typing. Independent paddle input
is still pending: the running Portal GPIO node only advertises volume-up.
Idle lock is temporarily inhibited during bring-up and must be restored when
the device is handed over. Raw logs, images and device identifiers remain under
the ignored private directory.
