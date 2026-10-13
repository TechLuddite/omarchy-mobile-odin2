# Native ARM64 Steam — October 13, 2026

Valve's native AArch64 Steam client is installed for `techluddite` on the Odin
2 Portal. Its updater completed, and the graphical **Sign in to Steam** window
rendered in the existing Hyprland/Omarchy session through XWayland. A private
screenshot confirmed the account fields and sign-in controls. The user later
signed in and installed Dead Cells and Road to Vostok. Dead Cells initially
failed to launch; the follow-up below separates that failure from client UI
acceptance. Native client acceptance does not establish x86 game compatibility.

Current game acceptance on the Portal:

| Game | Observed route | Acceptance |
|---|---|---|
| Dead Cells | Linux x86-64 → FEX → soldier/scout | Launch and in-game rendering visually checked after the runtime and launcher fixes; measured performance remains pending. |
| Road to Vostok | Windows x86-64 → FEX + Proton Experimental | User confirms running/working with low FPS; performance optimization remains open. |
| Scavland | Windows x86-64 → FEX + Proton Experimental | User confirms installed, ran and worked great; numeric FPS remains unmeasured. |

## Sources and credit

- **Valve and Steam Runtime contributors** supply the native client and runtime
  directly from Valve's servers. The inspected
  [ARM64 client manifest](https://client-update.steamstatic.com/steam_client_steamdeck_publicbeta_linuxarm64)
  has version `1791856936`, channel `steamdeck_publicbeta`. The downloaded seed
  was checked against the manifest's SHA256 before installation.
- **Shuuri Labs and Pocknix contributors** supply the working home-directory
  layout, channel choice, libibus link and desktop wrapper contract. Adapted
  from `shuuri-labs/pocknix-os` at
  `ba1de097fb0e0df07bcb32f05dc8e957d62090bc`, particularly
  [pocknix-steam-install](https://github.com/shuuri-labs/pocknix-os/blob/ba1de097fb0e0df07bcb32f05dc8e957d62090bc/packages/shared/pocknix-steam/pocknix-steam-install)
  and its adjacent `steam`, `steam.desktop`, `PKGBUILD` and icon. Recipe/icon
  hashes are in `sources.json`. Adapted glue retains GPL-2.0-or-later; the
  original license is in `licenses/pocknix-GPL-2.0.txt` and is installed at
  `/usr/local/share/licenses/odin-steam-arm64/LICENSE`.
- The [Valve ARM64 steamrt3c runtime](https://repo.steampowered.com/steamrt3c/images/3c.0.20260824.257593/)
  is pinned to `3c.0.20260824.257593`, checked against its published
  [SHA256SUMS](https://repo.steampowered.com/steamrt3c/images/3c.0.20260824.257593/SHA256SUMS).
  Client/runtime binaries and their original notices remain on-device or in
  ignored downloads; this repository does not redistribute those binaries.

| Download | SHA256 |
|---|---|
| `bins_linuxarm64_linuxarm64.zip.1aa8d441995b889cdf503b9162d4d459c3c4f553` | `9a83661b1d254596d680d64bb36f777d523cb59495c224307b5313276b586129` |
| `steam-runtime-steamrt-arm64.tar.xz` | `2f2be461b6a4360828e200e1644e18cd957eedc36a38e5a1e13a39276320b6e2` |

## Installation and desktop integration

The active Arch Linux ARM repositories provide no native Steam package.
`native/install-steam-arm64.py` verifies the two pinned archives, checks board
and architecture, refuses existing Steam state and extracts as the desktop
user. The seed has Windows-style separators in some paths and three relative
library symlinks; extraction normalizes separators and accepts only those
reviewed symlinks. Its ZIP records binaries without execute permissions, so
ELFs and shebang scripts receive executable permissions.

Installed host dependencies: `openal 1.25.2-2`, `libibus 1.5.34-2`,
`lsof 4.99.7-1`, `xorg-xauth 1.1.5-1`, `xorg-server-xvfb 21.1.25-1` and
`libxmu 1.3.1-1`; libcups was already installed. Packages came from signed ARM
repositories. Xvfb is available for diagnostics; acceptance used the live
desktop. Pacman used the documented per-command
`--disable-sandbox-filesystem` workaround for this kernel's missing Landlock
support. No distribution replacement, kernel write or broad OS update occurred.

On-device layout:

- `~/.local/share/Steam/steamrtarm64/`: native client and bundled libraries.
- `~/.local/share/Steam/steam-runtime-steamrt-arm64/`: verified Valve runtime.
- `~/.local/share/Steam/lib/aarch64-linux-gnu/`: relative links to runtime
  libibus, GTK2 and GDK2; host glibc and Mesa remain in use.
- `~/.steam/`: relative root, steam and SDK links following the upstream recipe.
- `/usr/local/bin/steam`: `native/steam-arm64`, with client directory first on
  `LD_LIBRARY_PATH`, pressure-vessel tools on `PATH`, correct working directory
  and the pinned beta channel. It uses the live session's XWayland display.
- `/usr/local/share/applications/steam.desktop`: application launcher and
  `steam://` handler; the default MIME association reads `steam.desktop`.
  The desktop entry validates and Gio resolves it to `/usr/local/bin/steam`;
  its icon is under the local hicolor icon directory.
- `~/.config/hypr/steam-arm64.lua`: `native/steam-arm64-window.lua`, loaded after
  Omarchy defaults. Only the sign-in window receives a centered 900×560 logical
  size so both password and QR controls fit at Portal display scaling.

For reproduction, download the exact artifacts listed above into a private
staging directory and run as the desktop user:

```bash
python3 native/install-steam-arm64.py CLIENT_ZIP RUNTIME_TAR
```

Install the wrapper, desktop entry, icon and original license at the paths
above; copy the Lua fragment into the user's Hyprland directory and add
`require("hypr.steam-arm64")` once to `hyprland.lua`. Validate with
`hyprctl reload` and `hyprctl configerrors` in the actual desktop environment.
Launch Steam from the app drawer to let Valve finish downloading its payload.
The first update exited successfully; launching again loaded the updated UI.
Valve's updater continues to manage the installed client, so these hashes pin
the initial seed/runtime rather than every future self-update.

## Findings and checks

- Initial launch downloaded and installed the remaining 666,784 KB client
  update and wrote `steam_client_steamdeck_publicbeta_linuxarm64.installed`.
- Updated `steam`, `steamui.so` and the running web helper are AArch64 ELFs.
  The UI renders through XWayland on the native ARM desktop.
- The first updated-client launch failed to load `libgtk-x11-2.0.so.0`.
  Current ALARM has no `gtk2`; `gtk2-compat` only attempts GTK3 substitution.
  Valve's verified runtime already contains actual ARM64 GTK2/GDK2. Relative
  links to just those missing libraries resolved the failure without adding
  the full runtime library directory ahead of host libraries.
- The first successful UI launch could not find
  `steam-runtime-launcher-service` on PATH. The wrapper now includes the
  ARM64 pressure-vessel tools directory; its launcher reports version
  `0.20260824.0`. A fresh launch through the desktop entry starts that service
  successfully and restores the full sign-in window at 900×560.
- The initial 466×294 logical sign-in window clipped the QR area. A live Lua
  resize confirmed 900×560 fits. The user-owned sign-in rule loads with no
  Hyprland configuration errors; packaged Omarchy files were only read.
- Steam GPU enumeration reports **Turnip Adreno 740**, Mesa **26.2.4**. This
  establishes device detection, not game rendering performance.
- The client logs optional missing ARM32 GPU-query binaries and an XRandR
  output-info warning. They did not prevent sign-in rendering; no game launch
  acceptance is claimed.

Private launch logs, screenshots, staged archives and the pre-Steam user
Hyprland configuration are under
`~/.local/state/odin2-omarchy/steam-install/` on-device. Host visual evidence
is under ignored `private/steam-install/`. No account credentials were entered.
Removal can undo the local wrapper/desktop/icon and the single Lua require,
then archive the user's Steam tree and links; inspect and preserve account/game
state before touching them.

## First game-launch investigation

The user reported Dead Cells failing to launch while Road to Vostok downloaded.
Steam's launch records show three Dead Cells attempts, each ending within about
two seconds. Dead Cells app `588650`, build `23762174`, is the native **Linux
x86-64** build (`deadcells.sh` and x86-64 ELF `deadcells`). Steam selected its
FEX compatibility tool, then Steam Linux Runtime soldier/scout. It never reached
a game window in these attempts.

Steam had automatically downloaded FEX app `3127680`, build `24136555`, version
`FEX-2607-76-g37265b1` / `37265b109a4bba9e10241972dfcb3d1fdb8f3f9a`.
Its `fex-compat-tool` defaults to `/usr/share/guestos/fex-mesa`, but that guest
tree was absent. All three private FEX logs reported the missing
`graphics_provider.json`. The tool's own `rootfs/` directory was empty. An ARM
Steam client and a downloaded FEX binary alone do not supply the x86 libraries.

The missing-runtime fix follows Pocknix at the existing source pin:

- Official FEX Arch guest image, `ArchLinux/2026-01-08/ArchLinux.sqsh`, SHA256
  `cb059973b7953ad9165845529655189b96f9a174b14a6a149c87ec884b0c5e90`.
- Pocknix's `packages/shared/fex-rootfs/PKGBUILD` pins that image and overlays
  x86 Turnip **26.2.4-1**, libdisplay-info **0.3.0-1** and xcb-util-keysyms
  **0.4.1-5**, avoiding the older image's Vulkan feature limitations. Only those
  libraries and their original license files are extracted from the verified
  Arch packages; hashes and download URLs are recorded in `sources.json`.
- `native/install-steam-guest.sh` checks board, architecture and all four hashes
  before creating `/usr/local/share/odin-steam/guest/`. It refuses existing guest
  state. The base image remains intact; the small overlay carries the updated
  libraries and the two-architecture graphics-provider manifest.
- `native/odin-steam-guest-mount` and `native/odin-steam-guest.service` present
  the image plus overlay as a **read-only** library filesystem at the exact
  path Valve's tool expects. The kernel already supports squashfs, loop devices
  and overlayfs. The service supplies the mount on subsequent boots without
  changing boot artifacts or restarting Steam.
- This uses the **Steam-provided** FEX engine and thunks. No system-wide binfmt
  translator, alternate host OS or VM is required for this route. The mount
  layout and graphics-provider contract are adapted from Pocknix with its GPL
  notice retained. FEX, RootFS, Mesa and dependency authors are credited early
  in the README and in the source ledger.

Road to Vostok app `1963610` completed its download (4,103,426,944 bytes) during
the investigation. Its installed state was read back; no game launch acceptance
is implied. Steam launched its Windows `RTV.exe` through FEX and Proton
Experimental; this is separate from Dead Cells' Linux route. No Steam account
settings or cloud-save conflict choices were edited. Staged artifacts and private diagnostics
live under `~/.local/state/odin2-omarchy/steam-guest-install/`.

The guest mount passed hash verification, systemd service validation and readback
as an active read-only overlay. Valve's FEX ran the guest `/usr/bin/uname -m` and
printed `x86_64`. No Steam restart was needed. The first game retry proceeded
further but still exited; an isolated container launch captured the next error:
the ARM FEX executable could not load `libstdc++.so.6`.

This second failure is caused by Dead Cells' Linux launcher assigning
`LD_LIBRARY_PATH=.` before each game invocation. A controlled container test
confirmed that the ARM library exists under
`/overrides/lib/aarch64-linux-gnu/`, that pressure-vessel includes its directories
in the environment, and that clearing that path reproduces the FEX loader error.

`native/fix-deadcells-steam-arm64.py` accepts only the inspected launcher SHA256
`5132161d5c1479b1a8221a73d44a5558e9fd0766ab7278aeb45f0bf024b49519`
from build `23762174`. It saves the original privately, then changes only its
two path assignments to prepend the local directory while keeping the inherited
container paths. The original launcher is not redistributed. Bash syntax
validation passed after the patch. Steam file verification or a game update
may restore the original; inspect any changed launcher before reapplying.

After the launcher fix, an ordinary Steam launch tracked the game process and
created its `deadcells` window. A private screenshot first showed the loading
screen, then a later screenshot showed a rendered **in-game scene**, character
and HUD. This is a successful startup/rendering observation. No diagnostic
keyboard/gamepad input was injected to reach that scene; frame rate, sustained
play, audio and physical controller behavior remain separate acceptance checks.
The game was left running. The read-only guest service is enabled and active;
boot persistence is configured but has not received another reboot test.

Rollback the per-game patch by restoring the saved
`deadcells.sh.before-library-path-fix` to the game's original launcher path.
Stop/remove the guest service only after translated games exit, then unmount
the guest tree before removing its files. A busy runtime must not be forcibly
unmounted. The device's host kernel, boot images and microphone route were not
changed in this investigation.


## Road to Vostok acceptance and optimization leads

The user subsequently reports **RTV ran and worked**, with **low FPS**, and
considers playable performance a plausible optimization target. Record this
as physical startup/gameplay acceptance with a performance limitation, not as a
measured playable frame rate. No numeric FPS, graphics-preset labels, sustained
session duration or separate controller/audio observations were supplied.

Read-only checks after that report establish:

- `Road to Vostok/logs/godot.log` identifies **Godot 4.6.3 stable**,
  **Vulkan 1.4.354**, the **Forward+** renderer and **Turnip Adreno 740**.
  The game is using the hardware GPU rather than a software renderer.
- Installed Proton Experimental is
  `1791480010 experimental-11.0-20261008-x86_64`. Both its Wine and wineserver
  are x86-64 ELFs, consistent with Steam's FEX-wrapped launch record. Native
  ARM64 Steam does not make this installed Wine build native ARM64.
- The game's `Preferences.tres` contains graphics-related enum values, but
  their label mappings were not established. They were not blindly changed.
  No game settings, compatibility tool, CPU/GPU clocks or fan policy were
  changed during this acceptance update.

Useful controlled comparisons, with improvement still unmeasured:

1. Measure the same short scene with the current route and settings, recording
   FPS/frame times and resolution. Keep the accepted route available for rollback.
2. Lower the game's 3D render scale/resolution and shadow/antialiasing load one
   change at a time, then repeat that scene. Godot documents
   [resolution scaling](https://docs.godotengine.org/en/4.6/tutorials/rendering/multiple_resolutions.html)
   as useful when GPU load limits performance. A resolution reduction also helps
   distinguish GPU load from translation/CPU limits.
3. Compare a separately installed native ARM64 Proton build against the working
   x86 Proton/FEX route, preserving the working prefix and saves. Valve documents
   [ARM64 builds](https://github.com/ValveSoftware/Proton#arm64-builds), and our
   Steam client already runs natively on ARM64. This is a candidate comparison,
   not an installed or accepted optimization or a guaranteed speedup.
4. Consider Godot's Mobile rendering method only as a separate compatibility
   test after the simple settings comparisons. Its
   [renderer documentation](https://docs.godotengine.org/en/4.6/tutorials/rendering/renderers.html)
   identifies lower rendering cost and fewer features; an exported game's
   lighting/effects may rely on Forward+ and need separate visual acceptance.

The exact performance bottleneck and attainable frame rate remain unknown.
Godot and Valve are credited for these documented research leads; the runtime
and handheld adaptation credits remain in the README, CREDITS and source ledger.

## Scavland acceptance

The user reports **installed and ran Scavland, worked great**. Record successful
physical gameplay and a positive qualitative performance result. No numeric
frame rate, settings, long-session duration or separate audio/controller
observations were supplied.

Read-only verification identifies Steam app **3373500**, installed build
**25355838**, and `Scavland/Scavland.exe` as a Windows **x86-64 PE32+** executable.
Steam's launch log selects its FEX compatibility tool, Steam Linux Runtime 4
and **Proton Experimental** before the game executable. This confirms another
working Windows game through the existing translation route; the game's
executable is not a native ARM64 binary. No game settings, launch options or
hardware policies were changed, and the game was not relaunched for diagnostics.
The FEX, Valve/Proton, runtime and Pocknix credits already recorded apply to
this run as well. The game engine and renderer were not independently identified.

## Scavland startup investigation checkpoint

After the user saved and closed Scavland, they authorized timed startup tests.
An ordinary Steam IPC launch reached the **MainMenu** log event in **81.90
seconds**. Unity initialization appeared at about 52.81 seconds, assemblies at
61.34 seconds and the first unload marker at 70.60 seconds. That earlier unload
marker was not the main-menu acceptance event; a native screenshot confirmed
the actual menu. The game log identifies **Unity 6000.3.7f1**, Mono and D3D11 via
DXVK/Turnip on Adreno 740.

Earlier Steam records show approximately 45–48 seconds before starting the game
process. The game's saved-map timing records show **29.862** and **35.057
seconds** for the Continue-to-map operation. Scene loading, settling and terrain
chunk creation dominate; opening the save takes under a second. These are
separate observations, not measurements of one simultaneous run.

An isolated FEX/Steam Runtime readiness comparison took approximately 7.00
seconds for `en_US.UTF-8`, 6.84 for `C.UTF-8` and 6.33 for `C`; it did not justify
a deployed locale change. CPU governors were already performance. The observed
high-capacity cores are **3–7**, so a future affinity comparison must not assume
the big cores start at CPU4. FEX's MonoHacks and multiblock settings were already
enabled; no unsafe TSO or experimental code-cache change was applied.

The original compatibility prefix and saves were privately archived with tar,
excluding the transient FEX server socket. Verification compared **33 regular
user files** with the archive. Earlier directory-copy attempts were incomplete;
the verified tar is the recovery copy. Preserve Wine symlinks without following
them, especially `z:` pointing at `/`.

A separate native ARM64 Proton candidate is extracted under the desktop user's
`Steam/compatibilitytools.d/`: **CachyOS Proton
`cachyos-11.0-20261005-slr-arm64`**, version `1791145021`. Its archive SHA256 is
`e59b646e73de4af21ff2f6c795b28e7b6c889214b3c6daf8e65a56634cd06c37`;
the published SHA512 matches the pinned Pocknix package recipe. Credit
[CachyOS Proton contributors](https://github.com/CachyOS/proton-cachyos/releases/tag/cachyos-11.0-20261005-slr),
Valve/Wine/component authors and [Pocknix's packaging recipe](https://github.com/shuuri-labs/pocknix-os/blob/ba1de097fb0e0df07bcb32f05dc8e957d62090bc/packages/shared/proton-cachyos/PKGBUILD).
All original archive notices remain on-device. This candidate has **not** been
selected or launch-tested; the accepted route remains x86 Proton Experimental
through Steam's FEX tool. Its runtime-manifest requirements must be resolved
before a comparison, using an isolated prefix and preserving the working saves.

**No measured startup improvement is accepted.** Startup comparisons were
interrupted by documentation/checkpoint work. Signed `xdotool` and `strace` were
installed for scoped diagnostics; no ordinary keystrokes were captured. Raw logs,
frames, compatibility data, downloads and user state remain private. The OBS
source was black during fullscreen while a native screenshot showed the menu;
use native evidence until that [capture issue](obs-stream.md) is resolved.
