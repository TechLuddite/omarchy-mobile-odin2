# Repository tracking

`/srv/projects/odin2-omarchy` is the working directory and the record for the
whole device port. External forks do not replace the notes here. Keep rationale,
source revisions, installation steps, checks, failures and remaining hardware
gaps in this project; keep raw device evidence under its ignored `private/`.

The main public repository is [TechLuddite/omarchy-mobile-odin2](https://github.com/TechLuddite/omarchy-mobile-odin2),
branch `main`. The session working directory remains `/srv/projects/odin2-omarchy`.
Clone with `--recurse-submodules` to obtain the mapper checkout at its recorded
revision. The main repo owns the device port, recovery tools, hardware status
and project-wide credits; the mapper keeps its separately published fork.

## Touch-focused gamepad mapper

- Public fork: [TechLuddite/omarchy-gamepad-mapping](https://github.com/TechLuddite/omarchy-gamepad-mapping).
- Parent: [Parminder Klair's Controller Control](https://github.com/perminder-klair/omarchy-controller-control),
  original pin `d5ac4cb41926fc93d2516a4f54bc5ec300d7838e`.
- Checkout: `plugins/controller-control/`, inside this working directory.
- Branch: `main`, also the fork's default branch.
- First adaptation commit: `ba34545` (record the full pin in `sources.json`).
- Compatible plugin ID remains `co.klair.controller-control`; the backend
  keeps `~/.config/controller-control/config.json` so assignments survive.
- Published changes: normal-window editor, touch selection, searchable live
  Omarchy shortcut list, automatic descriptions, Qt 6.12 compatibility,
  dedicated Odin Back token and native verification.
- Checks: 52 tests passed on the ARM Odin, including 44 upstream tests. A source
  diff whitespace check passed before publishing. Hardware rear-paddle checks
  are still pending; the native device port is the hardware acceptance record.
- Credits are prominent in the fork's README, `CREDITS.md`, copied-source header,
  original `LICENSE`, and `OMARCHY-LICENSE`. [Project-wide credits](../CREDITS.md)
  cover the rest of the port.

Device access setup, app-drawer integration, requested Home/Back defaults and
kernel/audio bring-up belong to `native/` and `docs/` in this parent project.
They are not silently assumed to be part of a generic Omarchy plugin install.

Home is assigned to Terminal (`MODE` → `SUPER+RETURN`) on the live device. The
dedicated Back event is now `BACK_BUTTON`, distinct from Select. The requested
Back → Toggle dictation assignment waits for successful microphone acceptance.

For any subsequent fork, add its upstream owner, URL, source pin, checkout path,
purpose, license/provenance and tested revision here and in `sources.json`.

## Recent SteamOS handheld research

These are ignored source references, not our forks or deployed components:

| Repository / owner | Inspected commit / checkout | Purpose and provenance |
|---|---|---|
| [MaSieS4Fun/SteamOS-ARM-SM8550](https://github.com/MaSieS4Fun/SteamOS-ARM-SM8550) — MaSi | `3548c401e6d2193a8a9ba7ef08add7074ea53f9e`, `references/steamos-arm-sm8550/` | October 8 source: Odin audio setup, SM8550-Power/LED, kernel leads. Original glue GPL-2.0; vendor components retain their licenses. Credits trace SteamOS-Ubuntu, MaSi-OS Kernel Updater, ROCKNIX/Armbian and Hooandee. Portal is explicitly untested in its README. |
| [hashtagbasit/SteamOS-ARM-Port](https://github.com/hashtagbasit/SteamOS-ARM-Port) — Basit and contributors | `4673fa6bfc8b6a598ef799ed0e88f98a9b045285`, `references/steamos-arm-port/` | October 9 source plus October 2 `v1.3-beta10` release: Portal input fixes, current SM8550 patches and device controls. Inherits MaSi's base and attribution; glue GPL-2.0, Decky components retain their separate notices. |

Sparse checkouts fetch selected text/source files, avoiding bundled firmware,
images and unrelated binary plugins. [Prior-art notes](prior-art.md) distinguish
release claims from our own Portal tests. File hashes and URLs are recorded in
`sources.json`. No installation, UFS migration or fan-control scripts from these
repositories were run on the Odin.

## Native Steam integration

Valve's ARM64 client/runtime are downloaded directly from Valve, with initial
archive hashes recorded in `sources.json`. The bootstrap layout and launcher
are adapted from the existing Pocknix reference at
`ba1de097fb0e0df07bcb32f05dc8e957d62090bc`, package
`packages/shared/pocknix-steam/`. This is the native desktop Steam client;
SteamOS overlays, sessions, CPU affinity and device-control plugins from the
research trees were not installed. The adapted installer, launcher, desktop
entry and sign-in sizing fragment live in `native/`, with steps and actual
acceptance in [docs/steam.md](steam.md). The original Pocknix GPL notice is
retained under `licenses/` and alongside the on-device launcher.

Game follow-up adapts Pocknix's `fex-rootfs/PKGBUILD`, guest mount/service and
graphics-provider manifest at the same pin. The official FEX Arch guest image
and x86 Turnip packages remain ignored artifacts; `native/install-steam-guest.sh`
and the guest mount/service provide the read-only library tree Valve's own FEX
tool requires. The inspected Dead Cells launcher has a separate, backed-up
library-path fix in `native/fix-deadcells-steam-arm64.py`. Its original game
code is not redistributed. Actual startup/rendering acceptance and remaining
gameplay checks are recorded in the Steam document.

## OBS display feed

The screen-feed integration lives here: sender and user service in `native/`,
relay/control/setup helpers in `scripts/`, and [acceptance/use notes](obs-stream.md)
in `docs/`. wf-recorder is installed from the signed ARM repository, and the
setup helper uses the existing host OBS WebSocket API. Read-only upstream
protocol/manpage snapshots are under ignored `references/obs-stream/`; hashes
and dependency versions are in `sources.json`. No third-party recorder or OBS
code was copied into the project. Raw video frames, OBS configuration backups
and device/host logs remain private.

## Standard application inventory

[docs/apps.md](apps.md) groups standard apps and included installers by estimated
remaining work on the Portal. [docs/apps.json](apps.json) records package names,
installed state, native catalog candidates, source paths/hashes and vendor links.
The baseline is the project's pinned Omarchy source, with readback of the live
app list, menu and installer scripts. Developer setup and Portal additions stay
separate from the stock app count. Package enumeration is not functional acceptance.
Raw read-only package/catalog/source snapshots are ignored under
`private/app-inventory/`. This inventory does not install apps or change services.

## October 13 checkpoint boundary

The agent context and [backlog](backlog.md) record microphone, Steam, Scavland,
OBS and app-inventory state, including pending theme-password diagnosis. The
parent and mapper are both on `main`; the mapper's clean recorded revision
requires no merge. Engineering source/documents are staged explicitly. Private
backups/artifacts and local X drafts are excluded by ignores and a local
pre-commit invocation of `scripts/audit-public-tree.py`; history auditing and
the exact committed tree are verified at the checkpoint. This is a local Git
checkpoint, not an instruction to publish X posts or upload device backups.
