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
| [docs/apps.md](docs/apps.md), [docs/apps.json](docs/apps.json) | Standard Omarchy apps and included installers, ARM candidates, estimated remaining work and separate installation/acceptance status |
| [docs/backlog.md](docs/backlog.md) | Open engineering work, including user-requested passwordless theme changes; theme issue is note-only until resumed |
| [docs/steam.md](docs/steam.md) | Native ARM64 Steam installation, Valve download hashes, Pocknix recipe credits and desktop acceptance |
| [docs/obs-stream.md](docs/obs-stream.md) | User-requested display feed to this host, OBS scene, local URL, capture lifecycle and verification |
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

## October 12 hardware baseline

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

Internal microphone capture was unresolved at that checkpoint. The October 13
follow-up below supersedes that state. Read the latest dictation and recovery
sections before device operations; EasyEffects installation alone is not voice
capture acceptance.

## October 13 integration checkpoint

- The onboard codec **DMIC3/SWR_MIC7** path captured and transcribed controlled
  speech from an external video in direct ALSA and normal PipeWire tests. The
  V3 board route also passed after a warm reboot. Credit Luke Johnson's Pocknix
  Thor route and the SteamOS ARM prior art; pins and findings are recorded here.
- Current ESP KERNEL is V3, SHA256
  `3c6b2569a964ec8c04b5bc96950df3921d58b016b77d40fd72fa597c10986763`.
  KERNEL.bak and recovery retain the proven baseline. Read the newest
  `docs/boot-recovery.md` section for the paired boot/UCM rollback; the pre-V3
  UCM backup is a diagnostic probe, not the pre-WCD baseline.
- The user's own voice/dictation accuracy, sustained use, cold boot and a
  physical 3.5 mm headset microphone remain pending. The user explicitly asks
  to test headset detection, speech, playback and unplug source return later.
  Back's dictation mapping remains pending that live-voice acceptance.
- EasyEffects 8.3.0 and LSP LV2 1.2.35 are installed. The controlled capture
  result does not depend on processing. Recent SteamOS control/PWM findings,
  credits and exact source revisions are in the prior-art and source records.
- Native ARM64 Steam (`steamdeck_publicbeta`) is installed in the desktop
  user's home. Its updater completed and the desktop launcher reaches a
  visually checked sign-in window through XWayland. The user-owned Hyprland
  sign-in rule avoids clipped controls; the runtime launch service runs.
  The user subsequently signed in and installed Dead Cells and Road to Vostok.
  Dead Cells now renders an in-game scene through Steam/FEX after installing
  the verified x86 guest runtime (`odin-steam-guest.service`, read-only mount)
  and preserving ARM library paths in its backed-up game launcher. That patch
  is specific to the inspected game build and may be reset by a game update.
  Sustained play, frame rate and physical gamepad behavior remain unverified;
  Road to Vostok is user-confirmed running/working with low FPS. Its log shows
  Godot 4.6.3, Vulkan Forward+ and Turnip Adreno 740; the installed Proton
  Experimental Wine is x86-64 under FEX. Numeric FPS and optimization remain
  pending. Source pins, installation steps and GPL notices are recorded in
  `docs/steam.md`.
- Scavland app `3373500`, build `25355838`, is user-confirmed installed,
  running and working great. Its x86-64 Windows executable uses Steam's FEX
  tool and Proton Experimental. Numeric FPS and separate audio/controller
  observations were not supplied; no further game tweaks were needed for this
  reported run. The acceptance entry is in `docs/steam.md`.
  Subsequent startup diagnosis identified Unity 6000.3.7f1/Mono and D3D11 via
  DXVK/Turnip. An ordinary launch took about 82 seconds to MainMenu; saved-map
  loads logged about 30–35 seconds. No startup improvement is accepted. A native
  CachyOS Proton ARM64 candidate is extracted but not selected or tested. The
  original prefix/saves have a private tar backup; do not follow Wine `z:` links
  or replace the working prefix during comparisons.
- The user-requested OBS display feed is installed. Host
  `odin-obs-stream.service` serves `http://127.0.0.1:17855/odin.ts`, starting
  capture via `ssh odin2` only when a viewer connects. The dedicated OBS scene
  **Odin 2 Portal** and source **Odin 2 Portal - Live Video** render the verified
  1280×720 / 30 FPS H.264 video. The host relay is enabled at login; capture
  stops after the last viewer leaves. Software encode uses about one CPU core
  on an idle desktop; game FPS impact and latency are unmeasured. Video only;
  no microphone capture was authorized or added by this screen-feed request.
  Desktop capture passed; Scavland fullscreen later showed a black feed while
  native screenshots showed the game. `--no-dmabuf` is currently a deployed
  diagnostic candidate and did not fix it. Do not describe gameplay capture as
  accepted. See the latest `docs/obs-stream.md` section and backlog.
- The standard app inventory has 92 main entries and 144 including appendices,
  based on live package/command/catalog checks and pinned Omarchy sources.
  Installed versus working and estimated remaining effort are separate fields.
  mise, Node/npm, yay, Docker, Chromium and OBS are absent from the Odin.
- User-reported theme changes requested a password. The requested behavior is
  passwordless theme switching. This is **backlog only**; no authorization or
  desktop policy change has been made. Read `docs/backlog.md` before resuming.

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
  Run `python3 scripts/audit-public-tree.py` on the exact staged tree before
  committing. The local pre-commit guard must pass; never bypass it or force-add
  private artifacts. Review `--history` at publication/checkpoint audits.
- Microphone tests need the user present and visible recording feedback. Do not
  record unattended unless the user explicitly authorizes a controlled audio
  source. The October 12–13 external-video tests had that explicit authorization
  and were each bounded to 20 seconds with visible feedback; this does not
  authorize future ambient recordings. Do not capture ordinary user keystrokes
  for diagnostics.
- Record actual physical observations separately from enumeration, source
  support claims, fixtures and synthetic tests. Run checks appropriate to changes;
  maintain the current hardware acceptance and recovery notes at checkpoints.
- Preserve the existing untracked X draft files (`docs/x-post-draft.txt` and
  `docs/x-handle-sources.json`) unless the user asks to change/publish them. Stage
  checkpoint files explicitly so unrelated drafts and private evidence stay out.
