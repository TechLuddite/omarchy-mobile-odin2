# Odin 2 prior art and installation routes

## Reusable foundations

| Project | Reuse | Important boundary |
|---|---|---|
| [SeeFix](https://github.com/TechLuddite/SeeFix) | Inspect existing state, reproduce the fault, make small fixes, verify the physical result, record provenance; evdev and Omarchy action mappings | Stream Deck support is not an Odin kernel or boot port. Existing shortcut codes must be checked against the target's bindings. |
| [omarchy-mobile](https://github.com/SimonSchubert/omarchy-mobile) | ARM64 package selection/builds, Omarchy integration, Hyprland mobile overrides, touch shell, keyboard, settings, theme hooks | Its disk, virtio initramfs, software GPU settings, portrait geometry, password policy, and macOS VM scripts need replacement for native hardware. |
| [ROCKNIX SM8550](https://github.com/ROCKNIX/distribution/tree/next/projects/ROCKNIX/devices/SM8550) | Device trees, kernel patches/config, firmware requirements, controller/haptics, thermal and display support | A mainline-derived kernel with device patches is different from assuming a generic upstream kernel supports every peripheral. |
| [ROCKNIX ABL](https://github.com/ROCKNIX/abl) | Direct native Linux boot, internal/SD/USB source selection, recovery menu | Identify the installed version and exact device image first. The repository inspected contains release/update tooling, not the complete bootloader implementation. |
| [Armbian Odin 2](https://github.com/armbian/build/blob/main/config/boards/ayn-odin2.csc) | Independent board integration, LinuxLoader/Android boot-image generation, USB networking, UCM audio and firmware loading | Debian package hooks must be adapted to pacman/mkinitcpio. Its board configuration masks suspend. |
| [Pocknix](https://github.com/shuuri-labs/pocknix-os) | Mutable ALARM base, pacman kernel/BSP packages, SM8550 boot-image construction, internal UFS installer, rear buttons and experimental sleep | Its shipped session is Plasma/Steam. Reuse the board layer while retaining Omarchy's session; its current installer preserves Android. |
| [Armada](https://github.com/armada-os/armada) | Current handheld integration, InputPlumber, internal installer and recovery experience | Fedora/bootc and Steam/KDE are separate from the intended Arch/Omarchy userspace. |
| [Renegade Odin 2](https://renegade-project.tech/en/ayn-odin2/install/dev), [strongtz useful files](https://github.com/strongtz/linux-next/releases/tag/odin2-release) | Earlier native ALARM port, firmware extraction, EDL loader, USB mass-storage boot and fastboot boot-image route | The 2024 instructions include destructive slot/partition operations and outdated graphics workarounds. Treat them as historical engineering evidence, not a script to run unchanged. |

Use `sources.json` for the actual revisions inspected. The projects' default
branches and their compatibility requirements change over time.

## Omarchy userspace

The inspected `omarchy-mobile/manifest.toml` pins Omarchy v4.0.3 and supplies
ARM64 builds for missing or incompatible packages, including a Hyprland rebuild
for an Aquamarine ABI change. Its `vm/packages/session`, `apps`, and `omitted`
files explain the package split. Start from those concrete recipes and recheck
the current ALARM repositories before building.

Keep the Odin-specific kernel, modules, DTBs, firmware and update hooks together.
A generic `linux-aarch64` package must not replace the device kernel during an
update. The native build needs UFS, Qualcomm display/GPU, USB and board firmware
available at the appropriate boot stage; the VM's virtio modules do not cover
this. Decide between a real mkinitcpio ramdisk and Pocknix's built-in storage/root
drivers when choosing the boot-image format.

The mobile shell can remain a user overlay. Adapt it for the actual landscape
screen, touch coordinates and scaling, then add gamepad navigation. Use SeeFix's
workflow to verify actual button events separately from their desktop actions.

## Installation without an SD card

Three routes were investigated. The RAM installer is verified on this device;
USB storage and host mass-storage remain alternative research routes.

1. **USB storage bootstrap.** Current ROCKNIX ABL documents USB boot. With a
   compatible bootloader and USB-C storage/OTG hardware, an Odin-specific Linux
   environment could run from USB and install the prepared Omarchy rootfs to
   internal storage. USB boot capability does not establish that an existing
   SD-only installer accepts a USB source: inspect and adapt its assumptions.
2. **Host connection and mass storage.** Renegade documents a fastboot-loaded
   `msd.img-odin2` exposing storage over USB and an EDL programmer used for
   partition reads/backups. A compatible mass-storage environment would let the
   host populate native boot/root filesystems. Identify the correct UFS LUN,
   sector size and GPT first. The old instructions require changes to slot
   metadata/boot partitions; do not assume temporary image loading is harmless.
3. **RAM installer via fastboot.** Armbian and Renegade demonstrate native
   Android-format Linux boot images. A custom kernel/initramfs with USB networking
   could boot an installer from RAM and receive the rootfs from this PC. This is
   an engineering option, not an existing verified Omarchy installation path.

Recovery-button access alone does not prove that fastboot accepts `boot` or
`flash`, or that Qualcomm EDL accepts the available programmer. Stock recovery,
ABL fastboot and EDL are distinct environments.

## Internal storage and single OS completion

ROCKNIX, Armada and Pocknix document internal Linux installations, but their
normal walkthroughs first boot from SD and reserve Android storage. Running
those installers unchanged would not meet this project's single-OS requirement.

Pocknix's inspected SM8550 path uses an Android-format `KERNEL` with appended
DTBs, plus `KERNEL.md5`, on an ESP-typed FAT boot partition. Its internal installer
uses 512 MiB for boot and explicitly accommodates 4 KiB UFS sectors when
formatting FAT32. These are useful concrete boot/layout constraints, not a reason
to replace the entire device GPT with a generic PC disk image.

The proposed final state is native Omarchy boot/root storage with Android's
userspace removed and its reclaimable space assigned to Linux. Preserve the
Qualcomm boot chain, per-device calibration/security partitions and required
firmware. Their exact layout and the treatment of Android `super`, `userdata`,
AVB and A/B metadata depend on the inspected device and boot route. A single OS
does not mean deleting every partition bearing an Android-origin name.

Before storage changes, capture the actual partition map and sector sizes,
back up both ABL slots and required boot/calibration partitions off-device, and
establish a usable recovery path. Then prepare the exact per-device storage plan
and boot artifacts. The first milestone is a RAM/native boot and working UFS
access; the endpoint is Omarchy cold-booting from internal storage with no card,
USB storage or Android session involved.

## Further related work

- [SimonSchubert/moarchy](https://github.com/SimonSchubert/moarchy) and
  [moarchy-keyboard](https://github.com/SimonSchubert/moarchy-keyboard): related
  native handheld UX and keyboard implementation. The PinePhone's Sway/GLES2
  constraints do not describe the Odin's GPU.
- [AYNTechnologies/alsa-ucm-conf](https://github.com/AYNTechnologies/alsa-ucm-conf):
  audio routes referenced by Armbian's board integration.
- [bkerler/edl](https://github.com/bkerler/edl): Qualcomm EDL tooling referenced by
  the native Odin installation work; programmer acceptance needs device testing.
- [MaSieS4Fun kernel updater](https://github.com/MaSieS4Fun/ayn-sm8550-easy-kernel-updater):
  source-discovery lead for performance and dock behavior, rather than a baseline
  to execute or accept without inspecting its claims and configuration.
- [LineageOS device trees](https://github.com/LineageOS/android_kernel_ayn_qcs8550-devicetrees-ack):
  related Android hardware descriptions for comparison if native drivers differ.

The Renegade hardware table is dated June 2024. Its old claims about unavailable
native OpenGL and unfinished peripherals must be checked against today's kernel,
Mesa and handheld sources. In particular, do not carry its forced Zink settings
or manually assigned Bluetooth address into a new build by default.

## Gamepad editing and game library

[Controller Control](https://github.com/perminder-klair/omarchy-controller-control)
provides a pure-Python evdev/uinput engine with chord, hold and repeat handling
and an Omarchy QML recorder/editor. The Portal adaptation retains that engine,
uses a normal window to allow the mobile keyboard, and adds an app launcher.
The default device filter selects only the built-in pad; no default bindings
are assigned. InputPlumber remains disabled to avoid two remapping layers.

[Omakade](https://github.com/btsouth/omakade) supplies a native ARM64 package in
its signed btsouth repository. Version 1.16.1 is installed and renders under
Wayland. Installing a library launcher does not establish compatibility of
individual games or emulators on ARM.

## Recent SteamOS work and on-screen device management — October 12

The latest user request prompted inspection of two community SteamOS ARM ports.
These use Valve's ARM userspace, while Pocknix is ALARM and Armada is Fedora
bootc. None replaces this project's native Omarchy installation. Exact source
commits, selected file hashes, owners and licenses are in `sources.json` and
[repository tracking](repositories.md); the new trees remain ignored research
checkouts. No upstream installation, partitioning or hardware-control scripts
were executed on the Portal.

| Source | Useful findings | Portal boundary |
|---|---|---|
| [MaSi's SteamOS-ARM-SM8550](https://github.com/MaSieS4Fun/SteamOS-ARM-SM8550/tree/3548c401e6d2193a8a9ba7ef08add7074ea53f9e), October 8 commit | SM8550-Power/LED panels; CPU/GPU governors and caps, fan curves, thermal/battery telemetry and RGB control. Odin audio setup repairs playback-clock/UCM discovery. | README marks the original Odin 2 tested and Portal untested. Its Odin HiFi lacks an internal microphone device. Power backend hard-codes `hwmon40` and several GPU/UFS paths; do not copy those assumptions. |
| [Basit's SteamOS ARM Port](https://github.com/hashtagbasit/SteamOS-ARM-Port/tree/4673fa6bfc8b6a598ef799ed0e88f98a9b045285), October 9 commit; [beta 10](https://github.com/hashtagbasit/SteamOS-ARM-Port/releases/tag/v1.3-beta10), October 2 | Release reports Portal/Mini A/B fixes, experimental real sleep, charging/Wi-Fi changes and Decky 3.2.10. Source retains MaSi's SM8550 panels and adds runtime `pwmfan` discovery. Thor/Pocket DS lower-screen panel integrates stats, fan/profile/brightness/volume, lighting, trackpad and keyboard. | Dual-screen UI is a design reference, not a Portal display feature. Current Odin2 HiFi still has no internal Mic; headset capture is commented out. Thor HiFi selects codec DMIC3 through SWR_MIC7. The Portal's controlled source tests found useful speech on that hardware slot; this needs Portal-specific board routing and acceptance. |
| [Pocknix Control](https://github.com/shuuri-labs/pocknix-os/blob/ba1de097fb0e0df07bcb32f05dc8e957d62090bc/docs/pocknix-control.md) and `pocknix-fancontrol` | Decky QAM UI for per-game fan/scheduler/audio/FEX settings, calibration and RGB. Fan service changes curves from a mode file with hysteresis and per-game overrides. | Avoid its first-`pwm1` discovery assumption. Do not let two controllers write the fan simultaneously. Its comments about "automatic" PWM mode need checking against this driver. |
| [Armada Control](https://armadaos.dev/using-armada/) | A device-control plugin in Steam's Quick Access Menu and a useful UI reference; Armada derives its board support from ROCKNIX. | Keep Fedora/session assumptions separate from the Omarchy host. No additional Armada microphone fix was established by this review. |

Two current kernel patches are worth keeping for the later **3.5 mm headset**
test: `0044-ASoC-wcd93xx-failed-zdet-ramp-is-a-floating-reading.patch` avoids
classifying a failed impedance measurement as a short, and
`0046-ASoC-wcd-mbhc-clear-stale-jack-report-on-mechanical-removal.patch` clears
a stale inserted state on unplug. The latter credits the KONKR Pocket FIT
Elite port. They are candidates to compare against our kernel, not fixes we
have deployed or physically accepted on the Portal.

The port also carries Armada-derived AudioReach patches `0026` and `0027`:
report DSP graph-open rejection correctly and release/rebuild graphs across
suspend. Pocknix carries related `1058`/`1059` changes. This is relevant to future
capture/reconnect/sleep diagnosis; it does not establish the source of today's
silence and is not grounds to replace the proven kernel blindly.

Our **read-only** hardware inventory finds `pwmfan` at
`/sys/class/hwmon/hwmon43`, with `pwm1=70`, `pwm1_enable=1` and one observed
tachometer reading of 1964 RPM. This confirms useful control/readback interfaces,
not a tested fan curve. Discover the hwmon device by its `name`, rather than
pinning an index. [Linux's pwm-fan documentation](https://docs.kernel.org/hwmon/pwm-fan.html)
defines `pwm1` as 0–255 and `pwm1_enable` as behavior at zero duty; **2 does not
mean a temperature-based automatic fan curve** for this driver. An Omarchy
control panel should use one deliberate controller, driver-aware modes and
thermal protection, with visible RPM/temperature readback. CPU/GPU profiles,
lighting, battery/charging, brightness and calibration can follow the same
separation between a touch UI and a narrowly scoped hardware backend.

Credit follows the source chain: MaSi/SteamOS-Ubuntu and Basit; Hooandee's
Panel de Control/decky-colores designs; Decky Loader; ROCKNIX/Armbian and device
authors; Luke Johnson/Shuuri Labs for the Thor DMIC lead; Armada for the graph
patches. These research notes do not claim ownership of upstream code.
