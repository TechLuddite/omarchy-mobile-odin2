# Credits and upstream work

This port is assembled from substantial work by the projects and people below.
Credit belongs with each reused component and adaptation, not only in this
ledger. Keep upstream license/copyright notices with copied code. Record the
specific source revision in `sources.json` and the actual device observations
in `docs/`. Add entries as more work is incorporated.

| Project / people | Contribution to this port |
|---|---|
| [Omarchy](https://github.com/basecamp/omarchy) — David Heinemeier Hansson and contributors | The operating environment, shell, themes, Lua desktop integration and standard dictation workflow. The mapper retains Omarchy's MIT notice for its adapted picker UI. |
| [omarchy-mobile](https://github.com/SimonSchubert/omarchy-mobile), [moarchy](https://github.com/SimonSchubert/moarchy), [moarchy-keyboard](https://github.com/SimonSchubert/moarchy-keyboard) — Simon Schubert and contributors | ARM userspace recipes/packages, the mobile shell, touch interaction and on-screen keyboard. These supplied the starting userspace for the native device. |
| [ROCKNIX distribution](https://github.com/ROCKNIX/distribution) and [ABL](https://github.com/ROCKNIX/abl) — ROCKNIX contributors | The running SM8550 kernel, Portal DTB, modules/firmware packaging and Linux-capable bootloader. The loader implementation is not public; this port does not claim to have inspected that private source. |
| [Pocknix](https://github.com/shuuri-labs/pocknix-os) — Shuuri Labs and contributors | Related native SM8550 board work, hardware recipes, audio configuration and power/sleep research. Its experimental features are not automatically accepted as working here. |
| Luke Johnson — Pocknix's WCD938x DMIC input patch | The missing input-widget fix and related Thor routes provide microphone research leads. The running ROCKNIX kernel already has the DMIC input widgets. The DMIC3/SWR_MIC7 board route led to confirmed controlled-speech capture on the Portal; user voice and headset acceptance remain pending. |
| [SteamOS-ARM-SM8550](https://github.com/MaSieS4Fun/SteamOS-ARM-SM8550) — MaSi / MaSieS4Fun; [SteamOS ARM Port](https://github.com/hashtagbasit/SteamOS-ARM-Port) — Basit / hashtagbasit and contributors | Inspected recent SM8550 fixes, Odin audio profiles and Decky hardware controls. Research only: no distro overlays, kernels, firmware or controllers from these trees are deployed here. Their credits retain the SteamOS-Ubuntu/MaSi-OS, ROCKNIX, Armbian, Valve and device-author lineage. |
| [Panel de Control](https://github.com/Hooandee/panel-de-control), [decky-colores](https://github.com/Hooandee/decky-colores) — Hooandee; [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) contributors | Upstream UI designs and plugin platform credited by the inspected SM8550-Power/LED implementations. No plugin code copied into this port. |
| Teguh Sobirin, Philippe Simons and other Qualcomm handheld kernel contributors | Portal board definitions, peripheral support and RSInput gamepad work represented in the upstream kernel patches and device trees used by this port. Preserve file-level notices when adopting changes. |
| [AYN ALSA UCM](https://github.com/AYNTechnologies/alsa-ucm-conf) — Teguh Sobirin and AYN contributors | The SM8550 speaker/headphone/headset configuration and codec routes used in audio bring-up. Internal microphone acceptance remains a separate test. |
| [Controller Control](https://github.com/perminder-klair/omarchy-controller-control) — Parminder Klair | The mapper's Python evdev/uinput engine, chord/hold/repeat handling, recorder, original QML editor and 44 upstream tests. Its MIT notice is retained in the public fork. |
| [Voxtype](https://github.com/peteonrails/voxtype) — Peter Jackson and contributors | Omarchy's dictation engine, native ARM64 build, model setup and recording/output service. The release binary was signature-verified before installation. |
| [Steam](https://store.steampowered.com/about/) and [Steam Runtime](https://github.com/ValveSoftware/steam-runtime) — Valve and runtime contributors; [Pocknix](https://github.com/shuuri-labs/pocknix-os) — Shuuri Labs and contributors | Valve's hash-verified native ARM64 client and steamrt3c runtime. The home-directory layout, channel selection, relative libibus link, working directory and desktop launcher are adapted from Pocknix's pinned Steam recipes. The Steam icon comes from that package. Adapted glue retains GPL-2.0-or-later with the original license in `licenses/pocknix-GPL-2.0.txt`; Valve's proprietary client and runtime notices remain on-device. See `docs/steam.md` and `sources.json`. |
| [FEX-Emu/FEX](https://github.com/FEX-Emu/FEX), [FEX-Emu/RootFS](https://github.com/FEX-Emu/RootFS), Mesa/Freedreno/Turnip, libdisplay-info and XCB contributors; Shuuri Labs / Pocknix contributors | Steam downloads FEX's native ARM translation engine and thunks. The verified Arch x86 rootfs provides its guest libraries. The guest mount and Turnip 26.2.4 overlay are adapted from Pocknix's pinned `pocknix-guestos-mount`, `graphics_provider.json` and `fex-rootfs/PKGBUILD`; glue retains GPL-2.0-or-later. FEX retains MIT, and original library/runtime licenses remain inside the read-only image and overlay. Actual game acceptance belongs in `docs/steam.md`. |
| [Proton](https://github.com/ValveSoftware/Proton) — Valve, Wine and bundled component contributors; [Godot](https://godotengine.org/) contributors | Proton Experimental's x86 Wine runs Road to Vostok through FEX. The game reports Godot 4.6.3 and Vulkan Forward+ on Turnip Adreno 740. Valve's ARM64-build documentation and Godot's resolution/renderer documentation are credited research leads for future performance comparisons; no speedup is yet measured. Original component licenses stay with the Steam-provided tool and game. |
| [CachyOS Proton](https://github.com/CachyOS/proton-cachyos) contributors; Valve/Wine/component authors; Shuuri Labs/Pocknix packaging contributors | Verified native ARM64 Proton `cachyos-11.0-20261005-slr` archive extracted as a separate Scavland startup candidate, following the pinned Pocknix package recipe. Original archive notices remain on-device. Candidate not selected or tested; no performance improvement is attributed to it. |
| [EasyEffects](https://github.com/wwmm/easyeffects) — Wellington Wallace and contributors; [Linux Studio Plugins](https://github.com/lsp-plugins/lsp-plugins) contributors | EasyEffects 8.3.0 and LSP LV2 1.2.35 installed from signed Arch Linux ARM packages for later audio processing. Installation does not establish a working internal microphone. Their GPL-3.0-only and LGPL-3.0-or-later package notices remain installed. |
| [DougDoug](https://www.youtube.com/@DougDoug) and the team behind [We built 3 deranged Ai and had them play D&D](https://www.youtube.com/watch?v=TpYVyJBmH0g) | The user played this AI D&D comedy on another device as the authorized controlled speech source for the first successful onboard microphone capture and post-reboot transcription. The video credits CyVoltage for editing, Tolekk for assistant editing and Wafferscotch for thumbnail/video art. Creator attribution only; no video, captured audio or transcript is distributed with the project. |
| [Omakade](https://github.com/btsouth/omakade) — Tyler South and contributors | Native ARM64 game-library application and signed package repository. Its optional guide overlay needs compatibility work with the pinned Omarchy shell. |
| [BlueZ](https://github.com/bluez/bluez) and [Blueman](https://github.com/blueman-project/blueman) contributors | The Bluetooth stack and a persistent graphical KeyboardDisplay agent for PIN/passcode/confirmation dialogs. The mobile panel's trusted-versus-bonded handling is adapted locally; peripheral acceptance is recorded separately. |
| [wf-recorder](https://github.com/ammen99/wf-recorder) — ammen99 and contributors; FFmpeg/x264, [OBS Studio](https://obsproject.com/), [obs-websocket](https://github.com/obsproject/obs-websocket), [websocket-client](https://github.com/websocket-client/websocket-client) and OpenSSH contributors | Capture, encoding, MPEG-TS transport over SSH, local OBS playback and authenticated scene setup for the user's Portal video feed. wf-recorder's MIT and websocket-client's Apache-2.0 notices remain with their installed packages; FFmpeg/x264 and OBS retain their original component notices. This project supplies the relay, sender profile and setup scripts. Versions, protocol references and actual checks are in `sources.json` and `docs/obs-stream.md`. |
| [bkerler/edl](https://github.com/bkerler/edl) and related Odin/Renegade recovery work | EDL reading and programmer/tooling leads used for the verified pre-install UFS backup. The private backup records the exact tool/programmer inputs. |
| [linux-msm/qbootctl](https://github.com/linux-msm/qbootctl) — Caleb Connolly, The Linux Foundation and contributors; [Linaro](https://devboardsforandroid.linaro.org/en/latest/devices/sm8x50.html) and Collabora | The unchanged ARM tool used to mark the verified native boot successful, plus SM8550 slot metadata and loader recovery research. Its original sources and notices accompany the installed binary. |
| [Android Open Source Project AVB](https://android.googlesource.com/platform/external/avb/) | The upstream avbtool used to replace stale Android verification descriptors during single-OS boot recovery. |
| [Armbian](https://github.com/armbian/build), [Armada](https://github.com/armada-os/armada) and [Renegade Project](https://renegade-project.tech/) | Related native Odin installation, boot-image and hardware integration prior art inspected during planning. |
| [Menci/docker-archlinuxarm](https://github.com/Menci/docker-archlinuxarm), Docker and QEMU contributors | The pinned ARM base container and host-side build tools. The Odin runs the installed native kernel and ARM userspace directly. |
| Linux/V4L2, Arch Linux ARM, Mesa/Freedreno/Turnip, ALSA, PipeWire/WirePlumber, Hyprland, Quickshell, Qt, GTK/PyGObject, FFmpeg, BusyBox, OpenSSH, NetworkManager, Avahi, dosfstools and mtools contributors | The kernel, ARM distribution, accelerated graphics, audio, desktop/runtime, key-only maintenance access, local network discovery, recovery and physical verification foundations. |
| [SeeFix](https://github.com/TechLuddite/SeeFix) — TechLuddite | The evidence-driven workflow: reusable code plus physical observations, raw logs and visual verification, with private device evidence excluded from published source. |

TechLuddite's work here is the Portal installation/recovery process, integration,
touch-oriented mapper adaptation, and device verification. It does not replace
the authorship or licensing of the components above. Firmware, device images,
private keys, audio recordings and raw device captures stay under ignored
directories and are not part of the public mapper repository.

The public mapper's [credits](https://github.com/TechLuddite/omarchy-gamepad-mapping/blob/main/CREDITS.md)
and [adaptation notes](https://github.com/TechLuddite/omarchy-gamepad-mapping/blob/main/PORTAL.md) track its
specific copied code and changes. [Repository tracking](docs/repositories.md)
links external work back to this working directory.

The [standard application inventory](docs/apps.md) credits Omarchy's app lists
and installer scripts, Simon Schubert's mobile packaging research, Arch Linux
ARM package metadata, and application authors' own ARM release/documentation
pages. Its [structured source record](docs/apps.json) retains the inspected
Omarchy pin, source hashes and vendor links. Research candidates are separate
from deployed code and accepted app behavior.

The AYN-derived headset UCM fragments retain Teguh Sobirin's authorship and the
ALSA project's BSD 3-Clause notice in [licenses/alsa-ucm-conf-LICENSE](licenses/alsa-ucm-conf-LICENSE).
The mapper retains its upstream MIT notices in its own repository. The compiled
qbootctl artifact is accompanied by the exact original sources and notices on
the device; build outputs and device firmware are excluded from this repository.
