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
| Luke Johnson — Pocknix's WCD938x DMIC input patch | The missing input-widget fix and related Thor routes provide microphone research leads. The running ROCKNIX kernel already has the DMIC input widgets; Portal board routing still needs verification. |
| Teguh Sobirin, Philippe Simons and other Qualcomm handheld kernel contributors | Portal board definitions, peripheral support and RSInput gamepad work represented in the upstream kernel patches and device trees used by this port. Preserve file-level notices when adopting changes. |
| [AYN ALSA UCM](https://github.com/AYNTechnologies/alsa-ucm-conf) — Teguh Sobirin and AYN contributors | The SM8550 speaker/headphone/headset configuration and codec routes used in audio bring-up. Internal microphone acceptance remains a separate test. |
| [Controller Control](https://github.com/perminder-klair/omarchy-controller-control) — Parminder Klair | The mapper's Python evdev/uinput engine, chord/hold/repeat handling, recorder, original QML editor and 44 upstream tests. Its MIT notice is retained in the public fork. |
| [Voxtype](https://github.com/peteonrails/voxtype) — Peter Jackson and contributors | Omarchy's dictation engine, native ARM64 build, model setup and recording/output service. The release binary was signature-verified before installation. |
| [Omakade](https://github.com/btsouth/omakade) — Tyler South and contributors | Native ARM64 game-library application and signed package repository. Its optional guide overlay needs compatibility work with the pinned Omarchy shell. |
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

The AYN-derived headset UCM fragments retain Teguh Sobirin's authorship and the
ALSA project's BSD 3-Clause notice in [licenses/alsa-ucm-conf-LICENSE](licenses/alsa-ucm-conf-LICENSE).
The mapper retains its upstream MIT notices in its own repository. The compiled
qbootctl artifact is accompanied by the exact original sources and notices on
the device; build outputs and device firmware are excluded from this repository.
