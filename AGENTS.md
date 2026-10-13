# Omarchy Mobile Odin2 — agent context

## Workspace and objective

The session working directory is `/srv/projects/odin2-omarchy`, the main record
for [TechLuddite/omarchy-mobile-odin2](https://github.com/TechLuddite/omarchy-mobile-odin2),
branch `main`. The device is the **AYN Odin 2 Portal**, not the original Odin 2
or Mini. The user's goal is native Omarchy on internal UFS, with no VM, Android
dual boot or required SD card, followed by complete hardware integration.

Keep code, reasoning, installation steps, failures, acceptance results and
credits here even when implementation lives in another fork. Follow the newest
user request; the checkpoint below records past observations, not live state.

## Start a session

Read [README.md](README.md) and [docs/hardware.md](docs/hardware.md) for the
overview and current acceptance. Read [docs/repositories.md](docs/repositories.md)
before working across the parent repo and mapper fork. Inspect `git status` and
the latest commit in both repositories before editing; preserve existing work.
Consult the relevant references below before device operations. Older sections
of the investigation logs are chronological; use their latest accepted result.

| Reference | Context to load |
|---|---|
| [docs/access.md](docs/access.md) | Passwordless Wi-Fi/root SSH, host aliases, account handling and verification limits |
| [docs/dictation.md](docs/dictation.md) | Voxtype, Microphone Check, microphone routing experiments and rollback state |
| [docs/boot-recovery.md](docs/boot-recovery.md) | Proven boot image, AVB/ESP repair, slot state and recovery constraints; read before boot/kernel/DTB writes |
| [docs/bluetooth.md](docs/bluetooth.md) | Pairing diagnosis, working Blueman flow, keyboard/TrackPoint acceptance and remaining reconnect checks |
| [docs/backup.md](docs/backup.md) | Base backup scope, verification, omissions and recovery copies |
| [docs/bring-up.md](docs/bring-up.md) | Device identification, installation chronology, display/touch and remaining bring-up work |
| [docs/prior-art.md](docs/prior-art.md) | Related native handheld work and candidate installation/hardware approaches |
| [CREDITS.md](CREDITS.md), [sources.json](sources.json) | Contributors, licenses, pinned revisions and provenance; consult when reusing/updating supporting work |
| [plugins/controller-control/PORTAL.md](plugins/controller-control/PORTAL.md) | Touch-focused mapper adaptation, device-specific behavior and validation |

## Directory map

- `native/`: Portal integration, installers, device configuration and touch apps.
- `bootstrap/`, `scripts/`: RAM bootstrap, builders, inspection and recovery tooling.
- `plugins/controller-control/`: Git submodule and separate public fork,
  [TechLuddite/omarchy-gamepad-mapping](https://github.com/TechLuddite/omarchy-gamepad-mapping).
  Its upstream is Parminder Klair's Controller Control. Keep device-wide notes
  and credits in this parent project as well as appropriate fork documentation.
- `references/`: local upstream checkouts and source snapshots, excluded from Git.
- `/srv/projects/SeeFix`: separate prior-art project and evidence-driven workflow.
- `private/`: ignored backups, device captures, logs and sensitive setup state.
- `build/`, `downloads/`, `tools/`: ignored local artifacts and tooling.

On the Odin, `/` is the installed native root, `/boot` is the ESP, and
`/recovery/base` and `/recovery/native` contain private recovery copies. The
desktop account is `techluddite`; deployed shell plugins are under
`/home/techluddite/.config/omarchy/plugins/`.

## Last accepted hardware checkpoint

Recorded October 12, 2026, in commit `54a7883` and the linked documentation:

- Native Omarchy boots from internal UFS with the proven kernel; root is sda18,
  ESP is sda17, and slot A is marked boot-successful. AVB and 4096-byte FAT
  sector issues were repaired. Cold power-cycle and slot-B acceptance remain open.
- Landscape display/touch orientation, mobile gestures, on-screen keyboard
  dismissal, Wi-Fi and native Freedreno/Turnip graphics have been checked.
- Wi-Fi maintenance aliases `ssh odin2` and `ssh odin2-root` provide key-only
  desktop and full root access via `odin2portal.local`. Use these aliases;
  verify reachability before making remote changes.
- Basilisk X mouse input works. ThinkPad keyboard typing and TrackPoint input
  work, and both keyboard functions reconnect after keyboard off/on without a
  code. Both peripherals had saved bonds and were connected at final readback.
  Mouse off/on, sustained use and Odin cold-boot reconnect remain untested.
- Successful keyboard pairing used the normal Pair flow with **Blueman's
  default graphical agent**. `native/odin-bluetooth-pair` is a separate candidate
  wizard, manually staged on-device but not wired into the normal helper or
  installer. Its registration/guard checks passed; its actual Pair flow did not
  receive a physical acceptance test. Do not confuse the two implementations.
- The mapper's 52 ARM tests pass. Home launches Terminal. Back is a dedicated
  `BACK_BUTTON`, distinct from Select; the requested dictation mapping awaits
  successful microphone acceptance. Independent rear-paddle input is unresolved.
- Voxtype and Microphone Check transcribe a known speech fixture, but **live
  internal microphone speech capture has not passed**. The current system uses
  the proven boot image and pre-WCD UCM probe after rollback. Omakade is installed;
  its optional guide overlay is disabled due to pinned-shell incompatibility.

Internal microphone capture is the main unresolved engineering topic. Read the
latest dictation and boot-recovery sections before continuing it. EasyEffects is
a later processing lead; it has not established a working hardware voice route.

## Project constraints

- Credit supporting projects early and high in the README. Update the credits
  ledger, source pins and repository tracking when adopting work or adding forks;
  preserve upstream copyright/license notices, including copied ALSA UCM notices.
- Preserve the proven boot/recovery artifacts. The one-time partitioning and
  Android-retirement scripts have already been applied; do not rerun them as
  routine setup. Do not reinstall an old microphone boot candidate blindly.
  Review the actual device layout and documented rollback before storage writes.
- Use user-owned Omarchy configuration/plugin paths and the applicable Omarchy
  skill for desktop customization. Packaged `/usr/share/omarchy/` is read-only
  for these customizations. Obtain the live user-manager Wayland/Hyprland
  environment for graphical launches or `hyprctl`; an SSH shell may lack it.
- Keep backups, firmware/device dumps, raw captures, account/session data,
  passwords, SSH private keys and Bluetooth pairing keys out of public Git.
  Base images are private and are not certified free of original sensitive
  state. Credentials are described by location in `docs/access.md`, never values.
- Microphone tests need the user present and visible recording feedback. Do not
  record unattended or capture ordinary user keystrokes for diagnostics.
- Record actual physical observations separately from enumeration, source
  support claims, fixtures and synthetic tests. Run checks appropriate to changes;
  maintain the current hardware acceptance and recovery notes at checkpoints.
- Preserve the existing untracked X draft files (`docs/x-post-draft.txt` and
  `docs/x-handle-sources.json`) unless the user asks to change/publish them. Stage
  checkpoint files explicitly so unrelated drafts and private evidence stay out.
