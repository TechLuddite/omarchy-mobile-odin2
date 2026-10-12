# Native Omarchy on AYN Odin 2 Portal

Built on David Heinemeier Hansson's Omarchy, Simon Schubert's mobile Omarchy work,
ROCKNIX's native hardware support, and many other contributors. See the early
[credits ledger](CREDITS.md) and [repository tracking](docs/repositories.md).

Current session status: the later reboot exposed a boot-chain failure. The
microphone candidate has been removed from the ESP, and corrected slot-A AVB
metadata lets fastboot accept the proven image again. A running desktop/USB
connection after that recovery is still unconfirmed. See the [recovery record](docs/boot-recovery.md).

Target: Omarchy and Hyprland running directly on the Odin 2 Portal, with the operating
system on internal UFS storage and no Android dual boot. Installation must work
without a microSD card. The saved Android vendor image identifies the device as
`Odin2 Portal`. Fastboot and EDL access work, and the UFS layout and existing base
system have been captured and verified. Native Omarchy boots from internal UFS
without a PC-supplied kernel. Its landscape desktop, hardware GPU acceleration,
touch gestures, keyboard and Wi-Fi work. Android userspace has been removed;
the full hardware checklist remains in progress.

The proposed stack is Arch Linux ARM, a patched Odin-specific Linux kernel and
firmware, and upstream Omarchy with adapted handheld controls. Existing projects
provide substantial hardware support. The USB RAM installer replaced Android
userdata with a FAT32 boot partition and native ext4 root, preserving the earlier
firmware/calibration GPT entries exactly.

The former Android `super` partition is now a recovery filesystem holding a
verified copy of the original base backup and the native boot/recovery images.
Both ABL slots contain ROCKNIX 1.1.8; both boot slots contain the native image.
The bootloader uses Linux mode, Auto source and the AYN Odin 2 Portal model.
Keep the off-device backup as the primary recovery copy.

The handheld [Gamepad Mapping adaptation](plugins/controller-control/PORTAL.md)
uses Controller Control's evdev/uinput engine and starts with empty assignments.
Its 52 tests, including 44 upstream tests, pass on the ARM device. Omakade 1.16.1 is installed from
the signed btsouth ARM64 repository and opens in the native Wayland desktop.

- [Prior art and installation routes](docs/prior-art.md)
- [Hardware acceptance checklist](docs/hardware.md)
- [Current device access and next steps](docs/bring-up.md)
- [Verified base image backup](docs/backup.md)
- [Omarchy dictation bring-up](docs/dictation.md)
- [Account setup and USB maintenance access](docs/access.md)
- [Boot recovery investigation](docs/boot-recovery.md)
- [Inspected source revisions](sources.json)

`references/` contains local upstream checkouts and pinned source snapshots.
`tools/android-tools/usr/bin/` contains locally extracted ADB and fastboot from
Arch's `android-tools` package. Its archive was checked against the SHA256 in the
host's pacman sync database. `bootstrap/`, `native/` and `scripts/` contain the
Portal RAM bootstrap, filesystem builder and internal bring-up tooling. This is
an actively tested device port; installation scripts are specific to the captured
Portal layout and are not a general installer for arbitrary Odin models.

Run the inspection helper from this directory:

```bash
python3 scripts/inspect-device.py
```

It uses read-only device queries and redacts transport serials. It refuses to
select a device if more than one ADB or fastboot transport is present. It never
reboots, unlocks, erases, flashes, or changes slots. Enable USB debugging and
authorize this computer on the Odin to inspect Android; fastboot inspection
requires the actual bootloader screen, which differs from Android recovery.

Keep partition dumps, firmware extracted from the device, personal logs, and
captured media under `private/`, outside published source. Keep upstream license
and copyright notices with any reused code. `sources.json` records research
revisions; it does not assert that their combination has been tested.
