# Omarchy Mobile Odin2

Native Omarchy bring-up for the **AYN Odin 2 Portal**, on internal UFS storage.

This project builds on the work of the following people and projects:

- **David Heinemeier Hansson and Omarchy contributors** — [Omarchy](https://github.com/basecamp/omarchy): the desktop, shell, themes, bindings and dictation integration.
- **Simon Schubert and contributors** — [omarchy-mobile](https://github.com/SimonSchubert/omarchy-mobile), [moarchy](https://github.com/SimonSchubert/moarchy) and [moarchy-keyboard](https://github.com/SimonSchubert/moarchy-keyboard): ARM userspace, mobile shell, touch interaction and on-screen keyboard.
- **ROCKNIX contributors** — [ROCKNIX](https://github.com/ROCKNIX/distribution) and [ROCKNIX ABL](https://github.com/ROCKNIX/abl): the running kernel, Portal device tree, firmware/modules and Linux bootloader.
- **Shuuri Labs and contributors** — [Pocknix](https://github.com/shuuri-labs/pocknix-os): related handheld integration, hardware recipes, audio and power research.
- **Teguh Sobirin, Philippe Simons, Luke Johnson and fellow handheld kernel contributors** — Portal board/peripheral work, RSInput support and WCD microphone research; **AYN contributors** — [AYN ALSA UCM](https://github.com/AYNTechnologies/alsa-ucm-conf): the codec and speaker/headphone/headset routes.
- **Parminder Klair** — [Controller Control](https://github.com/perminder-klair/omarchy-controller-control): the evdev/uinput mapper engine and original editor/tests, adapted in [our touch-focused fork](https://github.com/TechLuddite/omarchy-gamepad-mapping).
- **Peter Jackson and Voxtype contributors** — [Voxtype](https://github.com/peteonrails/voxtype): the native ARM64 dictation engine, model setup and service.
- **Tyler South and Omakade contributors** — [Omakade](https://github.com/btsouth/omakade): the native game-library application and signed ARM repository.
- **BlueZ and Blueman contributors** — [BlueZ](https://github.com/bluez/bluez), [Blueman](https://github.com/blueman-project/blueman): Bluetooth device handling and visible authentication dialogs for handheld pairing.
- **bkerler and EDL contributors** — [edl](https://github.com/bkerler/edl); **Renegade contributors** — [Renegade Project](https://renegade-project.tech/): device recovery and earlier native Odin installation work.
- **Armbian and Armada contributors** — [Armbian](https://github.com/armbian/build), [Armada](https://github.com/armada-os/armada): related Odin boot-image, installation and hardware integration prior art.
- **Caleb Connolly, The Linux Foundation and linux-msm contributors** — [qbootctl](https://github.com/linux-msm/qbootctl); **Linaro and Collabora contributors** — Qualcomm boot-success and loader recovery research; **Android Open Source Project contributors** — [AVB](https://android.googlesource.com/platform/external/avb/): boot verification tooling.
- **Menci and contributors** — [docker-archlinuxarm](https://github.com/Menci/docker-archlinuxarm): the pinned ARM base image; **Docker and QEMU contributors** — host build tooling.
- **Linux/V4L2, Arch Linux ARM, Mesa/Freedreno/Turnip, ALSA, PipeWire/WirePlumber, Hyprland, Quickshell, Qt, GTK/PyGObject, FFmpeg, BusyBox, OpenSSH, NetworkManager, Avahi, dosfstools and mtools contributors** — the kernel, distribution, graphics, audio, desktop, network access, recovery and verification foundations.
- **TechLuddite** — [SeeFix](https://github.com/TechLuddite/SeeFix): the evidence-driven verification workflow; this project supplies the Portal installation/recovery process and integration.

The [full credits ledger](CREDITS.md), [source revisions](sources.json) and
[repository tracking](docs/repositories.md) record contributions and provenance.
Keep upstream copyright and license notices with reused code. Hardware research
leads listed here are credited without claiming they all pass on this device.

For a new agent session, open this project root. [AGENTS.md](AGENTS.md) records
the reference files, working directories, accepted checkpoint and remaining work.

Current checkpoint: the installed native desktop boots again from internal UFS.
The confirmed AVB and FAT-sector recovery issues are corrected; `/boot` mounts,
USB SSH works, Hyprland/the mobile shell run, and systemd reports no failed
services. The desktop was checked through both the camera and a native screenshot.
Slot A is marked boot-successful. Microphone speech capture, cold power-cycle
acceptance, slot-B recovery and the wider hardware checklist remain open. See
the [recovery record](docs/boot-recovery.md).

Key-only user and full root SSH access also pass over Wi-Fi, with local discovery
at `odin2portal.local`. See [maintenance access](docs/access.md) for configuration,
host aliases and verification limits.

Bluetooth mouse input, ThinkPad keyboard typing and TrackPoint movement now
pass after pairing through Blueman's visible authentication dialog. Saved bonds
and input interfaces are verified, and keyboard off/on reconnect passes without
another code. Mouse off/on, sustained use and Odin cold-boot checks remain open.
See [Bluetooth acceptance](docs/bluetooth.md).

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

The handheld [Gamepad Mapping adaptation](https://github.com/TechLuddite/omarchy-gamepad-mapping/blob/main/PORTAL.md)
uses Controller Control's evdev/uinput engine and starts with empty assignments.
Its 52 tests, including 44 upstream tests, pass on the ARM device. Omakade 1.16.1 is installed from
the signed btsouth ARM64 repository and opens in the native Wayland desktop.

- [Prior art and installation routes](docs/prior-art.md)
- [Hardware acceptance checklist](docs/hardware.md)
- [Current device access and next steps](docs/bring-up.md)
- [Verified base image backup](docs/backup.md)
- [Omarchy dictation bring-up](docs/dictation.md)
- [Bluetooth input diagnosis and pairing repair](docs/bluetooth.md)
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

Clone the main repository with its linked mapper source:

```bash
git clone --recurse-submodules https://github.com/TechLuddite/omarchy-mobile-odin2.git
```

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
