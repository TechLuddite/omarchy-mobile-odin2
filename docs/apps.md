# Omarchy application bring up inventory

Initial inventory checked October 13, 2026: **92 standard app and web-launcher entries**, grouped by estimated remaining work on the **AYN Odin 2 Portal**. Developer installers and Portal additions have separate sections. Installation and functional acceptance are tracked separately.

The source baseline is the installed Omarchy tree pinned in this project as **v4.0.3**, commit `0534987009061cbe2dacdde4ad564092ab698d12`. The shipped `version` file still reads `4.0.0.alpha`; use the source pin rather than that stale string to identify this inventory. Readback hashes for the package list, installer menu and mise setup match the builder copy.

The Portal builder installed a session subset plus Epiphany, Nautilus, GNOME Text Editor and plain Neovim. It did **not** install the full upstream app tier or run all user-provisioning steps. An installer or app tile being present therefore does not imply the app is installed. Live command checks found no mise, Node/npm, yay, Docker, Chromium or OBS on the Odin.

This covers standard GUI apps, recognizable terminal apps, named optional app installers, shipped browser launchers and a developer appendix. Libraries, fonts, kernel/drivers, compositor/session plumbing and generic package-store contents are outside the app count. The list is a first triage; difficulty can change after the next check.

## Work levels

| Level | Meaning | Standard entries |
|---|---|---:|
| 0 | Already installed or present | 5 |
| 1 | Ordinary ARM package installation | 20 |
| 2 | Native packaging or integration changes | 44 |
| 3 | Substantial runtime or hardware work | 23 |
| 4 | Blocked stock route | 0 |

- **0:** Binary/package already present; verify ordinary workflows and polish. Presence is not a pass.
- **1:** Native ARM package listed in configured catalogs; ordinary install, desktop integration and functional checks expected.
- **2:** Native packaging, bootstrap, account/service setup or Omarchy/touch integration changes needed.
- **3:** Runtime translation, hardware support, or substantial architecture investigation needed. This does not assert that upstream lacks ARM support.
- **4:** The stock route is blocked or outside the native objective; record a replacement/remote route before attempting it.

ARM catalog listings come from the device's existing sync databases, without a refresh or installation transaction. Missing listings mean “absent from these catalogs,” not “impossible on ARM.” Availability, dependencies and signatures must be rechecked when installing.

## Native releases that change earlier omission assumptions

The mobile reference's older omission notes are not current app support verdicts. Official sources now provide native candidates:

- [Obsidian](https://obsidian.md/download): ARM64 AppImage.
- [LocalSend 1.18.2](https://github.com/localsend/localsend/releases/tag/v1.18.2): Linux ARM64 tar archive and deb.
- [Cursor](https://cursor.com/download), [Zed](https://zed.dev/docs/linux) and [Sublime Text](https://www.sublimetext.com/download): Linux ARM64 artifacts.
- [Brave](https://brave.com/linux/) and [Zen](https://github.com/zen-browser/desktop/releases/tag/1.23.2b): ARM64 browser routes.
- [1Password](https://support.1password.com/install-linux/) and [Bitwarden](https://github.com/bitwarden/clients/releases/tag/desktop-v2026.9.1): ARM64 desktop artifacts.
- [LM Studio](https://lmstudio.ai/docs/app/system-requirements), [Ollama](https://github.com/ollama/ollama/releases/tag/v0.40.3) and [Sunshine](https://github.com/LizardByte/Sunshine/releases/tag/v2026.914.233613): ARM64 candidates; Portal model performance and video/GPU acceleration remain separate checks.

Signal Desktop is listed as `aarch64` in the checked ARM repository. The earlier blanket “no ARM app” assumptions should not be reused for these rows. These are source/artifact observations, not Odin launch acceptance.

## Level 0 Already installed or present

| App | Omarchy inclusion | Odin status | Remaining work |
|---|---|---|---|
| Btop | Default package | Installed; function unverified; `btop` 1.4.7-1 | Verify interactive display, CPU/GPU fields and readable touch-scale layout. |
| Fastfetch | Default package | Installed; function unverified; `fastfetch` 2.69.0-1 | Check report on the Portal; package presence alone is not an app test. |
| Firefox | Optional installer | Installed; function unverified; `firefox` 157.0.1-1 | Installed ARM package; verify browsing, touch/OSK, downloads and any required DRM/video features. |
| Foot | Default package | Terminal and physical keyboard accepted; `foot` 1.28.0-2 | Terminal opening and physical keyboard use accepted; check OSK and sizing for longer work. |
| Nautilus | Default package | Installed; function unverified; `nautilus` 51.0.1-2 | Verify file browsing, copy, file dialogs and touch layout; package is installed. Upstream nautilus-python companion is absent; assess whether enabled integrations need it. |

## Level 1 Ordinary ARM package installation

| App | Omarchy inclusion | Odin status | Remaining work |
|---|---|---|---|
| Alacritty | Optional installer | Not installed | Install native package; verify font/theme, scaling and terminal launch integration. |
| Chromium | Default package | Not installed | Install native package; test Turnip/Wayland, app windows and Omarchy browser helpers. |
| Disk Usage | Default package | Not installed | Install native package and shipped TUI launcher; verify navigation. |
| Evince | Default package | Not installed | Install native package; open a test PDF and check zoom, scrolling and file associations. |
| GNOME Disks | Default package | Not installed | Install native utility; verify read-only device display. Storage editing is separate work. |
| Helix | Optional installer | Not installed | Install native package; verify editing, theme and optional language servers. |
| Image Viewer | Default package | Not installed | Install native package and shipped launcher; test image open, zoom and touch use. |
| Kdenlive | Default package | Not installed | Native package listed; test small clip import/edit/export and resource use. |
| Kitty | Optional installer | Not installed | Install native package; verify GPU rendering, fonts, scaling and terminal selection. |
| Lazygit | Default package | Not installed | Install native package; verify Git UI in a disposable test repository. |
| LibreOffice | Default package | Not installed | Install native package; create, save and reopen a document; test OSK and file dialogs. |
| Media Player | Default package | Not installed | Install player and MPRIS package; test video/audio, media controls and software versus hardware decode. |
| Nautilus preview | Default package | Not installed | Install ARM previewer; check preview on selected files with keyboard and touch access. |
| Print Settings | Default package | Not installed | Install native UI; printer discovery/printing needs an actual printer. |
| Signal | Optional installer | Not installed | Native ARM package listed; install, launch and later link a user-approved phone/account. |
| Tesseract OCR | Default package | Not installed | Install engine and English data; recognize a nonprivate fixture and verify Omarchy OCR helper. |
| Tmux | Default package | Not installed | Install native package; create/attach a test session and verify key/OSK usability. |
| Vim | Optional installer | Not installed | Install native package and test basic edit/save/quit in the terminal. |
| Xournal++ | Default package | Not installed | Install native package; test annotation/save/reopen and touchscreen use. No stylus pass inferred. |
| yt-dlp | Default package | Not installed | Install native/architecture-neutral package; test authorized public media metadata/download. |

## Level 2 Native packaging or integration changes

| App | Omarchy inclusion | Odin status | Remaining work |
|---|---|---|---|
| [1Password](https://support.1password.com/install-linux/) | Optional installer | Not installed | Vendor ARM64 desktop archive exists; adapt package/CLI and verify keyring/browser integration with user login later. |
| Aether | Default package | Not installed | Audit ARM build/package; test mail setup, keyring and touch layout. |
| Basecamp web app | Default web launcher | Launcher absent | Restore/verify browser launcher and test touch/OSK, user login and ordinary service flow. |
| [Bitwarden](https://github.com/bitwarden/clients/releases/tag/desktop-v2026.9.1) | Optional installer | Not installed | Official Linux ARM64 desktop archive exists; adapt CLI/launcher and verify vault/browser integration with user login later. |
| [Brave](https://brave.com/linux/) | Optional installer | Not installed | Vendor confirms Linux ARM64; adapt packaging, policies and Omarchy browser helpers. |
| Chromium Account | Optional installer | Not installed | Browser helper rather than standalone app; requires Chromium and explicit account sign-in acceptance. |
| Cliamp | Default package | Not installed | Inspect ARM release/build recipe; test music playback and terminal controls. |
| [Cursor](https://cursor.com/download) | Optional installer | Not installed | Official Linux ARM64 AppImage exists; adapt launcher/theme and check bundled helpers/extensions. |
| Discord web app | Default web launcher | Launcher present; service unverified | Restore/verify browser launcher and test touch/OSK, user login and ordinary service flow. Calls/media/device linking require separate acceptance. |
| Docker and Compose | Default package | Not installed | Install ARM packages; check daemon/kernel features and run a disposable ARM container. |
| Emacs | Optional installer | Not installed | Native emacs package exists; adapt Omarchy AUR config/package and check theme/launch/editing. |
| Ghostty | Optional installer | Not installed | No package in checked ARM catalogs; inspect source/native build and integrate terminal selection/theme. |
| Google Contacts web app | Default web launcher | Launcher absent | Restore/verify browser launcher and test touch/OSK, user login and ordinary service flow. |
| Google Maps web app | Default web launcher | Launcher absent | Restore/verify browser launcher and test touch/OSK, user login and ordinary service flow. |
| Google Messages web app | Default web launcher | Launcher absent | Restore/verify browser launcher and test touch/OSK, user login and ordinary service flow. Calls/media/device linking require separate acceptance. |
| Google Photos web app | Default web launcher | Launcher absent | Restore/verify browser launcher and test touch/OSK, user login and ordinary service flow. |
| Herdr | Default package | Not installed | Audit ARM build and service/session integration before claiming agent/remote features work. |
| HEY web app | Default web launcher | Launcher absent | Restore/verify browser launcher and test touch/OSK, user login and ordinary service flow. Also verify the shipped URL handler. |
| Lazydocker | Default package | Not installed | Install native TUI after Docker; verify daemon access and container controls. |
| [LM Studio](https://lmstudio.ai/docs/app/system-requirements) | Optional installer | Not installed | Vendor documents Linux ARM64 AppImage; integrate launcher, then measure a small model. Adreno acceleration is unverified. |
| [LocalSend](https://github.com/localsend/localsend/releases/tag/v1.18.2) | Default package | Not installed | Use official Linux ARM64 archive; package launcher and test a LAN transfer both ways. |
| Moonlight | Default package | Not installed | Install ARM package; test pairing, video decode, audio, touch/gamepad and stream latency. |
| [Obsidian](https://obsidian.md/download) | Default package | Not installed | Official ARM64 AppImage exists; integrate launcher/update path and test a disposable vault. |
| [Ollama](https://github.com/ollama/ollama/releases/tag/v0.40.3) | Optional installer | Not installed | Official Linux ARM64 archive exists; package/service setup and small-model CPU verification first. GPU support is separate. |
| OmaCalc | Default package | Not installed | Inspect architecture-neutral/ARM build recipe and install; verify calculation and touch UI. |
| OmaCut | Default package | Not installed | Audit ARM package and clipboard/shortcut integration; test without replacing personal shortcuts. |
| Omarchy Neovim distribution | Default package | Not installed | Plain neovim is installed; port the Omarchy config package and inspect plugin/tool downloads for ARM. |
| OmaWrite | Default package | Not installed | Audit ARM package/build; verify create/save/reopen and touch/OSK behavior. |
| OpenClaw | Optional installer | Not installed | Audit npm/native dependencies on ARM; package gateway and browser UI, then user-owned onboarding/service test. |
| [Pinta](https://www.pinta-project.com/howto/installing-pinta/) | Default package | Not installed | No package in checked catalogs; inspect native .NET/Flatpak route and image editing. |
| RetroArch | Optional installer | Not installed | Native frontend listed; stock installer requests many unavailable/git cores. Select ARM cores and verify BIOS/ROM, shaders and controls. |
| RetroArch Game Launcher | Optional installer | Not installed | Included launcher creator requires installed working ARM core and ROM; validate after RetroArch setup. |
| [Sublime Text](https://www.sublimetext.com/download) | Optional installer | Not installed | Official Linux ARM64 archive exists; adapt package/desktop integration and verify editing. |
| Tailscale | Optional installer | Not installed | Native package exists; configure service and verify tunnel/routing after user-owned account setup. |
| Tensaku | Default package | Not installed | Inspect ARM package/build and clarify user-visible text workflow; test selected operations. |
| Tobi Try | Default package | Not installed | Audit ARM package/build and scratch-project workflow. |
| [VSCode](https://code.visualstudio.com/download) | Optional installer | Not installed | Select vendor Linux ARM64 artifact; adapt package/theme/keyring integration and audit ARM extension binaries. |
| WhatsApp web app | Default web launcher | Launcher absent | Restore/verify browser launcher and test touch/OSK, user login and ordinary service flow. Calls/media/device linking require separate acceptance. |
| X web app | Default web launcher | Launcher present; service unverified | Restore/verify browser launcher and test touch/OSK, user login and ordinary service flow. |
| Xbox Cloud Gaming | Optional installer | Not installed | Browser launcher; test service/account, browser codecs/network and controller mapping separately. |
| YouTube web app | Default web launcher | Launcher absent | Restore/verify browser launcher and test touch/OSK, user login and ordinary service flow. |
| [Zed](https://zed.dev/docs/linux) | Optional installer | Not installed | Official aarch64 build exists; integrate Omarchy companion/theme and validate Turnip Vulkan on the Portal. |
| [Zen](https://github.com/zen-browser/desktop/releases/tag/1.23.2b) | Optional installer | Not installed | Official aarch64 AppImage/archive exists; adapt installer/policies and verify browser/touch behavior. |
| Zoom web app | Default web launcher | Launcher absent | Restore/verify browser launcher and test touch/OSK, user login and ordinary service flow. Calls/media/device linking require separate acceptance. Also verify the shipped URL handler. |

## Level 3 Substantial runtime or hardware work

| App | Omarchy inclusion | Odin status | Remaining work |
|---|---|---|---|
| Battle.net | Optional installer | Not installed | Stock installer expects Wine/GE-Proton and lib32 GPU setup; requires ARM/FEX runtime adaptation and per-game validation. |
| Brave Origin | Optional installer | Not installed | Audit Origin-specific ARM release/licensing and packaging; ordinary Brave ARM support does not prove this variant. |
| ChatGPT Desktop | Optional installer | Not installed | Stock desktop package absent; audit Linux ARM artifacts and companion integration. Web app/CLI are separate alternatives. |
| Chrome | Optional installer | Not installed | Stock AUR route absent; verify current Linux ARM artifact before choosing native packaging or a browser alternative. |
| Dictation | Optional installer | Partial functional acceptance | Native Voxtype and controlled speech accepted; own voice, headset, sustained capture and Back mapping remain pending. |
| Dropbox | Optional installer | Not installed | Audit daemon architecture and sync integration; browser access does not establish desktop sync support. |
| Edge | Optional installer | Not installed | Stock package absent; audit Linux ARM availability. Chromium/Firefox are native alternatives. |
| GPU Screen Recorder | Default package | Not installed | ARM package exists; hardware encoder and capture support on Adreno remain separate engineering checks. |
| Grok Bot | Optional installer | Not installed | Audit desktop/helper architecture and ARM packaging; no native route established here. |
| Hermes Desktop | Optional installer | Not installed | Installer assumes prebuilt desktop payload plus Python runtime; audit both ARM dependencies and updater before installation. |
| Heroic (Epic Games) | Optional installer | Not installed | Audit ARM frontend and download helpers, then integrate usable ARM/FEX runners; launcher opening is not game acceptance. |
| Lutris | Optional installer | Not installed | Native launcher exists, but Wine/umu stack is missing; ARM/FEX runner integration and per-game tests are substantial work. |
| Minecraft | Optional installer | Not installed | Stock launcher absent; inspect ARM launcher route and Java/native game libraries. Compare native alternative before translation. |
| NordVPN | Optional installer | Not installed | Audit daemon/CLI ARM artifacts and TUN/service/firewall integration; avoid changing the working SSH route during first checks. |
| NVIDIA GeForce NOW | Optional installer | Not installed | Stock installer downloads vendor setup; verify ARM payload or browser route, DRM, decode and physical controls. |
| OBS Studio on the Odin | Default package | Not installed | Not in ARM catalogs checked; evaluate ARM build and Wayland capture/encoding. Host OBS feed is separate. |
| ONCE | Optional installer | Not installed | Audit current ARM binary/container support and service dependencies; no supported route accepted yet. |
| Perplexity | Optional installer | Not installed | Audit desktop ARM artifact/support; web access is a separate fallback. |
| Spotify | Optional installer | Not installed | Stock package absent; verify native desktop availability and DRM. Web player is an alternative to desktop acceptance. |
| Steam | Optional installer | Partial functional acceptance | Native client and games run through custom ARM/FEX integration; startup, performance and wider game/controller acceptance remain open. |
| [Sunshine](https://github.com/LizardByte/Sunshine/releases/tag/v2026.914.233613) | Optional installer | Not installed | Official ARM artifacts exist; package service and validate Wayland capture, encoder, input, pairing and stream performance on the Portal. |
| T3 Code | Optional installer | Not installed | Audit desktop ARM assets and bundled native tools; adapt theme/backend integration if supported. |
| Xbox Controllers | Optional installer | Not installed | Installer targets stock linux-headers; Portal needs matching custom kernel headers/driver and physical controller test. |

## Portal additions

| Entry | Level | Odin status | Remaining work |
|---|---:|---|---|
| Epiphany | 0 | Installed; function unverified | Portal browser substitute; verify real browsing, app windows, OSK and media. |
| GNOME Text Editor | 0 | Installed; function unverified | Verify edit/save/reopen and touch/OSK; this is a Portal addition. |
| Plain Neovim | 0 | Installed; function unverified | Native editor present; this does not establish the Omarchy Neovim distribution. |
| EasyEffects | 2 | Launch accepted; processing unverified | Native GUI launched; user voice, preset processing and sustained audio behavior remain pending. |
| Omakade | 2 | Launch accepted; optional overlay disabled | Native library GUI opens; pinned-shell guide overlay compatibility and game integration remain open. |

## Developer installers and lazy CLI tools

| Entry | Level | Odin status | Remaining work |
|---|---:|---|---|
| .NET | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| Bun | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| claude (`claude`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| Clojure | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| codex (`codex`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| copilot (`copilot`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| crush (`crush`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| Deno | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| Docker DB | 2 | Not installed | Docker first; verify ARM image manifests, kernel/container support and local test connection. SQL Server is separate. |
| Elixir | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| gemini (`gemini`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| gh (`gh`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| ghui (`npm:@kitlangton/ghui`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| Go | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| grok (`npm:@xai-official/grok`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| Hermes CLI (`hermes-cli`) | 2 | Not installed | Audit ARM runtime/bootstrap and verify CLI independently of the desktop app. |
| hunk (`aqua:modem-dev/hunk`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| Java | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| Laravel | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| MariaDB Docker database (`mariadb:11.8`) | 2 | Not installed | Check this exact image tag includes linux/arm64; run a disposable container and verify a local query after Docker works. |
| MongoDB Docker database (`mongo:noble`) | 2 | Not installed | Check this exact image tag includes linux/arm64; run a disposable container and verify a local query after Docker works. |
| Muse CLI (`muse`) | 2 | Not installed | Audit ARM runtime/bootstrap and verify CLI independently of the desktop app. |
| MySQL Docker database (`mysql:8.4`) | 2 | Not installed | Check this exact image tag includes linux/arm64; run a disposable container and verify a local query after Docker works. |
| Node.js | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| OCaml | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| omp (`github:can1357/oh-my-pi`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| opencode (`opencode`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| Phoenix | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| PHP | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| pi (`pi`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| playwright (`npm:playwright`) | 2 | Not installed | Install mise/Node as required, create wrapper, verify native downloads and a small real command; authentication later. |
| PostgreSQL Docker database (`postgres:18`) | 2 | Not installed | Check this exact image tag includes linux/arm64; run a disposable container and verify a local query after Docker works. |
| Python | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| Redis Docker database (`redis:7`) | 2 | Not installed | Check this exact image tag includes linux/arm64; run a disposable container and verify a local query after Docker works. |
| Ruby on Rails | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| Rust | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| Scala | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| Symfony | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| Zig | 2 | Not installed | Install missing mise/bootstrap tools, verify native runtime/downloads, then compile or run a small sample. |
| [SQL Server Docker database](https://learn.microsoft.com/en-us/sql/linux/install-upgrade/setup?view=sql-server-ver17) | 4 | Not installed | Microsoft documents x64-only Linux processors; stock image is not a native ARM route. Prefer a remote SQL Server or another database. |

## Other included setup routes

| Entry | Level | Odin status | Remaining work |
|---|---:|---|---|
| Chromium Copy URL integration | 2 | Not installed | Verify native messaging host, extension and browser profile paths after a Chromium-family browser is accepted. |
| Chromium yt-dlp integration | 2 | Not installed | Verify native messaging host, extension and native yt-dlp path after browser setup. |
| Generic TUI installer | 2 | Not installed | Verify terminal wrapper, desktop creation and selected native command. |
| Generic Web App installer | 2 | Not installed | Verify browser selection and desktop creation; browser UI/service behavior is per app. |
| OpenClaw CLI installer | 2 | Not installed | Audit native npm dependencies and command setup; CLI presence does not establish gateway/UI acceptance. |
| Stock lib32 GPU helper | 3 | Not installed | Stock helper selects Intel/AMD/NVIDIA lib32 drivers. Use the Portal ARM/FEX guest-graphics route for translated games instead. |
| Windows VM | 4 | Not installed | Stock Windows/Docker recipe needs a separate architecture/KVM investigation and is outside the native-Omarchy objective; do not treat it as a normal ARM app install. |

## Installation order

1. Verify existing browser, file manager, text editor and terminal workflows; establish a small repeatable fixture for each.
2. Fill routine app gaps: Evince, imv, mpv, LibreOffice, Xournal++, Lazygit and a preferred additional terminal/editor. Check touch/OSK and associations alongside ordinary function.
3. Add native ARM packages for Obsidian and LocalSend; then desired editors/password managers. Keep each original vendor notice and verify downloaded artifacts.
4. Install mise/Node/bootstrap tools before promising the shipped AI CLIs or developer installers. Inspect ARM native downloads and distinguish lazy wrappers from installed runtimes.
5. Continue Voxtype live-voice/headset acceptance, Steam startup/performance, and capture/streaming work separately from routine app coverage.

Every acceptance result should record install route/version, launch result, one real core workflow, touch/OSK behavior, and material GPU/audio/portal limitations. User account sign-in and physical peripherals remain explicit later checks. Do not promote “installed” to “working” from package queries alone.

## Sources and maintenance

- [Upstream default packages](https://github.com/basecamp/omarchy/blob/0534987009061cbe2dacdde4ad564092ab698d12/install/omarchy-base.packages), [installer menu](https://github.com/basecamp/omarchy/blob/0534987009061cbe2dacdde4ad564092ab698d12/default/omarchy/omarchy-menu.jsonc), [lazy CLI setup](https://github.com/basecamp/omarchy/blob/0534987009061cbe2dacdde4ad564092ab698d12/install/user/mise.sh), and the named `bin/omarchy-install-*` scripts at the same pin.
- [Portal builder](../native/build-rootfs.sh), Simon Schubert's [omarchy-mobile reference](https://github.com/SimonSchubert/omarchy-mobile), and [project source ledger](../sources.json). The VM/mobile omission list is a research input, not this Portal's acceptance list.
- Live read-only package, command, launcher and source-hash checks; existing configured ARM repository catalogs. Raw snapshots stay in ignored `private/app-inventory/`.
- [Dictation acceptance](dictation.md), [Steam acceptance](steam.md), [hardware acceptance](hardware.md) and [OBS host feed](obs-stream.md). OBS running on the project host does not mean OBS is installed on the Odin.

The [structured inventory](apps.json) keeps per-entry packages, source paths/hashes, vendor links, estimated level, installer route and status. All named app/developer/helper leaves in the pinned Install menu are covered, plus the included Sunshine script and browser/CLI helpers. Fonts/theme/background and generic package/AUR/preinstall bulk actions are excluded deliberately. This is not an inventory of every package Omarchy can install.

Existing project-wide credits to Omarchy, Simon Schubert, Arch Linux ARM, app authors and reused integration projects apply. No vendor installers, application source or private account state were copied into this document. When implementing a new installer, update the project credit/source records and preserve the original notices.
