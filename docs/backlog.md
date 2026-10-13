# Portal integration backlog

October 13, 2026 checkpoint. Keep user observations separate from source support
and package enumeration. The linked acceptance records contain the recovery
constraints and evidence needed before continuing each item.

| Item | Current result | Remaining work |
|---|---|---|
| Passwordless theme changes | The user reports changing an Omarchy theme requested their desktop password. | **Note only for now.** Theme changes should be passwordless. Identify the exact privileged command/authorization prompt and correct the narrow theme operation; preserve ordinary sudo/account policy. No fix or reproduction has been attempted. |
| Scavland startup | Gameplay is user-accepted; an ordinary Steam launch took about 82 seconds to the main menu. Saved-map logs show roughly 30–35 seconds, mainly scene/terrain work. | Compare one change at a time while preserving the working prefix/saves. Native ARM64 Proton is staged for comparison, not accepted. No measured startup improvement yet. [Steam notes](steam.md). |
| OBS fullscreen game capture | Landscape desktop feed and reconnect pass. Scavland fullscreen is black in the feed while a native screenshot shows its menu. | Localize sender versus relay/player behavior. The `--no-dmabuf` diagnostic attempt did not fix the issue. Measure capture cost/latency and validate gameplay after a fix. [OBS notes](obs-stream.md). |
| Own voice and dictation | Onboard DMIC3/SWR_MIC7 captures controlled external speech, including after warm reboot. | User voice accuracy, sustained use and Back-button dictation mapping. No unattended ambient recording. [Dictation](dictation.md). |
| 3.5 mm headset | Separate analog headset route retained; physical acceptance pending. | Insertion detection, source selection, recognizable speech, headphone playback and onboard-source return after unplug. [Hardware](hardware.md). |
| Standard apps and installers | Initial list has 92 standard app/web-launcher entries, with developer/setup appendices. | Work through native package gaps, mise/Node/bootstrap prerequisites and app-specific acceptance. [App inventory](apps.md). |
| Road to Vostok performance | User confirms it runs with low FPS; hardware Turnip rendering is established. | Repeatable scene/resolution/frame-time comparisons; no optimization accepted yet. [Steam notes](steam.md). |
| Cold boot and recovery | Internal boot and warm reboot accepted; proven baseline/recovery artifacts retained. | Cold power cycle and slot-B recovery acceptance. [Recovery constraints](boot-recovery.md). |
| Bluetooth persistence | Mouse input and ThinkPad typing/TrackPoint work; keyboard off/on reconnect passed. | Mouse power cycle, sustained use and Odin cold-boot reconnect. [Bluetooth](bluetooth.md). |
| Wider hardware integration | Display/touch/Wi-Fi/native GPU acceptance documented; wider peripherals vary. | Paddles, haptics, fan/LED controls, speaker/headphone audible tests, charging, real sleep and docks. [Hardware checklist](hardware.md). |

## Source-only commit boundary

Backups, recovery images, firmware/device dumps, runtime archives, recordings,
screenshots, logs, account/session state, passwords, private SSH keys and Bluetooth
pairing keys remain outside public Git. Local X drafts remain on disk, excluded
from this engineering checkpoint. Public documents may reference private paths
and artifact hashes without embedding the artifacts or credential values.

Run `python3 scripts/audit-public-tree.py` against the exact staged tree before
every checkpoint. `--history` also checks reachable historical blobs. The local
pre-commit hook invokes the staged-tree guard; `.gitignore` additionally blocks
common artifact formats. A clone needs its own local hook installed. These checks
supplement explicit file staging and review; never use a broad force-add or stage
the ignored directories.
