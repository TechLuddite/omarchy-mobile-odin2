# Odin 2 Portal hardware acceptance

Upstream code or a distro's support claim establishes a candidate implementation.
The table records acceptance criteria for this device under the selected
kernel, firmware and Omarchy session; the evidence below records current progress. Record versions, physical observations,
logs and remaining limits using the SeeFix method; keep raw captures private.

Latest native session evidence (October 12): normal internal ESP boot reaches
Omarchy with root on sda18 and boot on sda17. Freedreno FD740 EGL and Turnip
Adreno 740 Vulkan report hardware rendering. The display is upright at transform
1, and the user confirmed opening/closing gestures after touch transform 1,
keyboard dismissal and joining Wi-Fi. HTTPS works over Wi-Fi. Bluetooth powers
on; pairing is pending. Speaker/headphone sinks enumerate; audible output and
microphone recording remain pending. The controller mapper recognizes the AYN
gamepad and passes 44 native tests, including synthetic-pad integration tests;
physical button and rear-paddle checks await the user. The running Portal DTB
only advertises volume-up on gpio-keys; independent rear-paddle events are not
yet established. Do not copy the original Odin 2's paddle GPIO assignments.

Bluetooth input diagnosis found that the mouse and keyboard were trusted but
unpaired/unbonded, with repeated missing-agent authentication errors. Blueman's
visible agent is now running and attached to the desktop session, and the mobile
panel distinguishes trust from actual pairing. The user confirms mouse pointer
input after fresh pairing; its bond and HID interfaces are verified. Keyboard
pairing/typing, sustained connection and peripheral off/on reconnect remain
pending. See [Bluetooth diagnosis](bluetooth.md).

| Hardware or behavior | Candidate prior art | Acceptance on this device |
|---|---|---|
| Boot and recovery | ROCKNIX ABL, Renegade/Armbian boot images | Cold boot, warm reboot and shutdown; internal boot without removable media; repeatable bootloader/recovery entry |
| CPU and memory | SM8550 kernel config/DT, qcom cpufreq | All expected cores/RAM, frequency changes and stable sustained operation |
| UFS | ufshcd-qcom and board DT | Correct capacity/GPT/4 KiB sector handling; boot/root reads and writes; clean reboot after filesystem sync |
| GPU | msm DRM, Freedreno OpenGL, Turnip Vulkan | Hardware renderer rather than llvmpipe; Hyprland acceleration; EGL/Vulkan applications, artifacts and GPU-reset checks |
| Internal display and brightness | Portal Chipone ICNA3512 panel and its supplies | Actual panel mode/orientation, brightness range, screen blank/unblank and readable landscape UI; use the Portal DTB |
| Touchscreen | Portal FocalTech FT5426 node/driver | All corners/edges, multitouch, gestures and keyboard with scaling/rotation applied |
| Gamepad | RSInput/AYN MCU, InputPlumber/SDL mappings | Buttons, d-pad, sticks, clicks and analog triggers; calibration/dead zones; games and desktop navigation |
| Rear M1/M2 | Portal board/MCU and InputPlumber mappings | Separate events and chosen action mapping; no duplicate input; do not assume the original Odin 2's GPIO57/58 implementation applies |
| Power and volume keys | PMIC keys, userspace policy | Correct press/hold behavior; volume/OSD; usable recovery combinations |
| Haptics | Qualcomm haptics/RSInput force feedback | Requested effects, stop behavior and no stuck rumble |
| LEDs | Portal HEROIC HTR3212 and board multicolor nodes | Power/charge indication and stick/side lighting; brightness and off state |
| Fan and thermals | pwm-fan, thermal cooling maps | Fan responds to load/temperature; stable automatic control and safe thermal throttling |
| Wi-Fi | ath12k WCN7850 and board firmware | Scan/connect/reconnect, throughput, correct device identity; reconnect after sleep |
| Bluetooth | QCA firmware and board identity fixes | Pair/reconnect, controller and audio profiles; unique address preserved |
| Speakers and headphone jack | Qualcomm AudioReach/LPASS, AW amps, UCM | Left/right channels, volume, jack routing, mute and no pops after reboot/resume |
| Microphone | Codec/audio UCM and DSP firmware | Actual recording and source selection; do not infer success from speaker playback |
| USB device/host roles | DWC3/QCOM, gadget networking | PC connection, recovery access, host devices, role changes and disconnect handling |
| Battery and charging | PMIC GLINK, UCSI/power supply | Accurate charge state, percentage and charging current; USB-C negotiation; powered-off charging |
| Sleep and wake | Pocknix experimental s2idle stack | Repeated wake cycles with UFS/GPU/Wi-Fi/audio/input intact; measured battery drain; distinguish true sleep from screen-off fake suspend |
| USB-C DisplayPort and dock outputs | msm/gpio SBU mux and actual attached dock | Plug/unplug, boot docked, external modes/audio and return to internal display; original Odin 2 HDMI bridge assumptions require separate confirmation |
| Motion sensors and rotation | Android hardware baseline, Qualcomm sensor work | Identify actual sensors; events and explicit rotation behavior; unverified support |
| Video decode/encode | Qualcomm Iris and userspace support | Supported codecs with actual hardware acceleration, playback and recording |
| microSD reader | SDHCI board support | Defer until a card is available; lack of installation media does not count as a hardware pass |
| Optional peripherals | Exact model inventory | Only add fingerprint/camera/etc. tests if the physical variant contains them |
| Omarchy usability | omarchy-mobile, SeeFix controls | Launcher, settings, keyboard, lock/unlock, touch/gamepad navigation, themes, external keyboard and terminal access |
| Updates and rollback | Pacman kernel/BSP packaging | Kernel/modules/DTB/firmware stay compatible; regenerate boot image/checksum; reboot after update; usable recovery after failure |

Start with boot/UFS, display/GPU/touch, and USB access. Then enable network,
audio, input and thermal/power management. Sleep, docks and update recovery need
separate acceptance before calling hardware support complete.

October 12 RAM-bootstrap evidence: native kernel 7.2.0 boots with the Portal DTB;
all eight CPUs and approximately 15 GiB usable RAM are visible. UFS reads, GPT
updates, filesystem creation and a 4.3 GiB installation copy completed. USB ECM,
HTTP and SSH work. The DSI panel draws a Linux console; modes list 1080×1920
(two refresh rates). Adreno firmware loads and renderD128 exists. The FocalTech
touchscreen, AYN gamepad, haptics, power/volume keys, multicolor LEDs, backlight
and thermal cooling devices enumerate. These observations do not establish
touch accuracy, GPU userspace acceleration, audio, networking or power support.
