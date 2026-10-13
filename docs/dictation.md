# Omarchy dictation on the Odin2 Portal

Working directory: `/srv/projects/odin2-omarchy`.

Current result (October 13): the onboard **DMIC3/SWR_MIC7** path captures and
transcribes controlled speech, including after a warm reboot. The user's own
voice/dictation and 3.5 mm headset tests remain pending. The latest evidence
and paired boot/UCM rollback are recorded at the end of this file and in
`boot-recovery.md`; earlier sections describe the failed probes chronologically.

The requested feature is Omarchy's standard Voxtype integration. Its pinned
installer assumes the `voxtype-bin` package, which is absent from the device's
ARM repositories. A native upstream ARM64 release is installed instead.

## Installed and checked on October 12, 2026

- Voxtype 1.1.0, upstream `voxtype-1.1.0-linux-aarch64-cpu`, installed as
  `/usr/local/bin/voxtype` on the Odin.
- Binary SHA256: `2fcf0945d424a116c1947ea738da1afa9f83abbae66cebb53f06189111a6f392`.
- Detached release signature verifies against the upstream CI signing key
  `9CCF7915B750CAE8B095ED1AA3FC9F33FD209279`, pinned from upstream's release
  workflow. Verification used a private throwaway keyring, not the host keyring.
- Omarchy's stock Voxtype configuration copied to the device user's config;
  the base English Whisper model downloaded and loaded by the native daemon.
- The user service is enabled and running. With the Wayland environment,
  `voxtype setup check` passes; `wtype` and `wl-copy` are installed.
- Hyprland reload/configerrors pass. Omarchy's conditional F9 start/stop and
  Super+Ctrl+X toggle bindings now load because Voxtype is present. Refresh the
  Gamepad Mapping shortcut list to select Toggle dictation.

## Microphone investigation — functional acceptance is pending

Before this change ALSA exposed MultiMedia3 Capture (`hw:0,2`), but the installed
AYN UCM profile contained only playback devices. The running Portal DTB provides
a WCD/SoundWire capture link and the headset analog route. AYN's current upstream
SM8550 UCM adds headset capture; it does not define an internal microphone.

The device's saved Android mixer configuration describes a digital handset path:
DMIC1 through DEC2. `native/odin-capture.conf` is a candidate UCM addition using
that path, plus the upstream headset route. The kernel capture PCM requires
48000 Hz, S16_LE and two channels; mono UCM capture declarations caused the
whole HiFi profile to disappear. Two-channel declarations restore both playback
sinks and expose an Internal microphone source in PipeWire.

Exposure of that source is not a capture pass. A direct ALSA stream failed with
an I/O error. A five-second PipeWire test produced only 314 zero-valued samples,
which is not valid real-time microphone audio. The existing capture link combines
WCD, SoundWire and TX macro components; the direct digital microphone may need
a different link or DSP topology. Investigate this before claiming dictation
works or packaging the candidate microphone configuration as validated support.

LPASS GPIO6/7 were unclaimed in the running pinctrl state. A reversible runtime
test selected `dmic1_clk` and `dmic1_data` through pinctrl debugfs; it did not
resolve capture. These writes are not persistent. No new boot image, DTB, kernel
or boot-partition write has been performed for this investigation.

Raw evidence stays private: `private/bootstrap/dictation-inventory.txt`,
`voxtype-release.json`, `voxtype-model.log`, `voxtype-service.log`,
`microphone-probe.log`, `capture-probe-2ch.log`, `capture-current.txt`,
`dmic-pin-test.log`, `dmic-kernel.log`, and `mic-test.wav`. Android XML extracted
from the verified base backup also remains private. The original UCM file is
saved on the device as `/root/odin-hifi-before-capture.conf`.

References: [Voxtype](https://github.com/peteonrails/voxtype),
[ARM64 installation](https://github.com/peteonrails/voxtype/blob/dev/docs/INSTALL.md),
[AYN UCM](https://github.com/AYNTechnologies/alsa-ucm-conf/blob/52b6ae98b7cd01e35ab6d193f953394dcefe5c0e/ucm2/AYN/SM8550/HiFi.conf).

## Further capture checks

The digital DMIC1/DEC2 path alone could not start a valid stream through the
existing WCD/SoundWire capture link. Enabling the upstream headset route alongside
it allowed a full two-second stereo capture. Channel 0 carried low-level noise
(peak 87, RMS 16.68); channel 1 was entirely zero. This does not prove an internal
microphone works. The GPIO6/7 test mux settings were restored to GPIO.

The first analog candidate UCM used the known SoundWire route for both its
always-available Mic device and jack-gated Headset device. A 20-second mono
PipeWire recording produced 322,533 frames at 16 kHz, peak 37 and RMS 6.77;
Voxtype returned an empty transcript. The user reports speaking during the
window but saw no clear feedback. They later used the touch test app and also
reported no words detected. Neither test is a transcription acceptance pass.
The original unmodified UCM remains available for rollback. A later WCD board
route candidate and its boot recovery are recorded below and in the recovery
notes. Home is mapped to Terminal; Back's requested dictation assignment
is pending microphone acceptance.

The mapper's public fork is recorded in [repositories.md](repositories.md), with
upstream credits retained in the fork and [the project ledger](../CREDITS.md).

## Visible testing and reproducible dictation setup

`native/odin-microphone-check` is a GTK4 touch app in the device app drawer as
**Microphone Check**. It requires no keyboard. Start opens the default PipeWire
input, shows a red recording message, countdown and live peak/RMS meter, and
stops automatically after 20 seconds. Stop ends capture early and displays the
Voxtype transcript. Opening the app does not record. Closing it stops recording.
Recordings remain mode 0600 in the device user's private state directory;
no audio is part of Git. The app's `--transcribe WAV` option tests a saved file
without opening a microphone.

An upstream Voxtype speech fixture produced **Hello world!** in the native CLI
and the touch app. This checks the ARM binary, model and visible transcript
path independently of hardware capture. The app was visually inspected on the
landscape desktop. Live speech acceptance is still pending.

`native/install-dictation.sh` installs only the pinned, previously
signature-verified ARM64 release after checking its exact SHA256. It also
installs the microphone app and launcher. Prerequisites are PipeWire tools,
Python/PyGObject/GTK4, wtype and wl-clipboard, all present on the current device.
`native/configure-dictation.sh` runs as the desktop user, backs up the existing
config, preserves the stock Omarchy binding approach, downloads the model and
enables the Voxtype user service. Recording-start and recording-stop
notifications are now enabled for visible normal dictation feedback; transcript
notifications remain disabled.

EasyEffects was suggested by the user and is a useful later processing lead.
Noise processing does not establish that the currently selected hardware input
captures a voice; resolve capture routing before treating it as a fix.

The earlier source labelled **Internal microphone** is a probe using the
headphone-jack **ADC2** enable sequence. That name does not establish onboard
wiring. The user explicitly requests a later independent test with a 3.5 mm
headset that has a microphone: verify headphone/mic jack detection, automatic
source selection, recognizable speech, headphone playback, and source return
after unplugging. No physical headset-microphone test has passed yet. Keep that
acceptance separate from the current digital onboard-microphone investigation.

## WCD digital microphone route lead

The saved Android overlay matching SM8550 `0x25b` and board `0x1001f,0` names
the QRD sound card. Its saved QRD audio XML maps handset capture to codec DMIC2
over SoundWire, enabling codec DMIC2/3 and MIC BIAS3. That differs from the
generic MTP XML's direct LPASS DMIC route used in the first probe. This is a
stronger board-specific lead, but the original Android runtime selection was
not captured and actual Portal voice capture remains unverified.

The native DTB lacks the corresponding codec DMIC2/3 board routes. The running
kernel already exposes the DMIC input widgets added by
[Luke Johnson's Pocknix patch](https://github.com/shuuri-labs/pocknix-os/blob/ba1de097fb0e0df07bcb32f05dc8e957d62090bc/kernel/sm8550/patches/30-sm8550/0200-ASoC-wcd938x-add-DMIC-DAPM-inputs.patch).
`scripts/build-microphone-candidate.py` adds only four route pairs to a separate
DTB/boot artifact, preserving the proven image. A decompiled DTB diff verifies
that sole change; kernel, ramdisk and command line match the proven boot image.
`native/odin-wcd-capture-candidate.conf` is a separate stereo WCD/SoundWire UCM
probe. It is experimental, not an accepted default microphone configuration.

The test reboot exposed a loader failure that also rejected the unchanged
baseline. The stock slot-A AVB metadata was replaced, and a subsequent ESP
rollback-image sector-size error was diagnosed and corrected. Normal internal
boot now reaches the desktop again with the proven kernel and pre-WCD UCM probe.
Actual microphone speech capture remains unverified. See
[boot recovery](boot-recovery.md) for the operations and accepted checkpoint.

## Resumed WCD route investigation — October 12

Fresh Wi-Fi inspection confirmed the proven ESP image and pre-WCD UCM digest
from the recovery record. A normal reboot with those unchanged files passed:
Wi-Fi/root SSH returned, Hyprland and the shell run, no services failed, and
slot A remains active, successful and bootable. This is another warm reboot,
not cold-boot acceptance.

The first WCD candidate raised a numbering hypothesis: DAPM widget names and
SoundWire port switches use different conventions. Linux's [WCD938x SoundWire channel table](https://github.com/torvalds/linux/blob/24a19b953e2a3d0ea5a8c4951a0ab8f32720c907/sound/soc/codecs/wcd938x-sdw.c)
assigns `DMIC1 Switch` and `DMIC2 Switch` to port 3 bits 1 and 2. The matching
DAPM ADC widgets are `DMIC2` and `DMIC3`; their event shifts are 1 and 2.
With this board's unchanged `qcom,tx-port-mapping = <2 2 3 4>`, the corresponding
TX inputs are 5 and 6. The revised probe routes `DMIC2_OUTPUT` to
`TX SWR_INPUT5` and `DMIC3_OUTPUT` to `TX SWR_INPUT6`, powers both through
MIC BIAS3, and selects the matching zero-based port switches. It also clears
the previous analog port switches and stale direct-DMIC DEC2 enable.
This was a source-backed routing hypothesis, not proof of physical wiring.
The later slot7 result below supersedes it: the DAPM widget controls a shared
clock pair, so its ordinal is not a reliable physical data-channel identity.

The builder now preserves the original candidate under `build/microphone-candidate/`
and writes the corrected version under `build/microphone-candidate-v2/`.
V2 image SHA256: `8e91711bbced456c197afaa1a8216279f0a3ac104abc9c24bf51c5b3d9774fc8`.
Independent boot-image unpacking verified identical decompressed kernel,
ramdisk, command line and remaining boot fields; only payload size/digest and
the appended DTB differ. The decompiled DTB diff changes only four route pairs.
The installer checks the image and UCM digests, Portal identity, mounted sda17
ESP, 4096-byte geometry and slot-A success before writing. Current UCM is saved
as `/root/odin-hifi-before-wcd-v2-test.conf`; older backups remain intact.

The V2 candidate was installed on the ESP and booted successfully. Root SSH,
the ALSA card, PipeWire's WCD candidate source and both playback sinks return;
systemd reports no failed services. Live DAPM inspection confirms both new
TX input connections and both MIC BIAS3 supply routes. Microphone Check was
opened without recording for a user-started visible speech test; acceptance
is pending the result. Do not treat routing enumeration as voice capture.

Rollback uses the proven `/boot/KERNEL.bak` and
`/root/odin-hifi-before-wcd-v2-test.conf`, checking their documented digests
before restoring `/boot/KERNEL` and the deployed HiFi UCM. Raw boot slots,
KERNEL.bak and RECOVERY.img were not changed. Sync before rebooting; a UCM-only
rollback requires restarting the desktop user's audio services. Private
diagnostics are in `private/bootstrap/microphone-resume-inventory.txt` and
`microphone-v2-visible-test-routes.txt`.

## First controlled onboard speech capture — October 13

The user reported the visible V2 tests did not work. Their recordings contain
a repeatable startup transient, then exact zeros after two seconds. A full
20-second trace confirmed DMIC2, DMIC3 and MIC BIAS3 were powered throughout
capture; the frontend was stereo/48 kHz and the WCD backend selected one
channel. Source enumeration, widget power and a meter flash were insufficient.

The user explicitly left a video playing on another device and authorized
measurement while away. Subsequent captures used the visible GTK app, each
bounded to 20 seconds, rather than ordinary unattended ambient recording.
The user later identified the source as DougDoug's
[We built 3 deranged Ai and had them play D&D](https://www.youtube.com/watch?v=TpYVyJBmH0g).
YouTube's creator metadata confirms DougDoug; its description credits editor
CyVoltage, assistant editor Tolekk and thumbnail/video artist Wafferscotch.
Their entertaining AI D&D speech helped establish actual acoustic capture and
transcription on this Portal. The README, credits ledger and `sources.json`
record that contribution; the media and test transcripts remain private.
The app now supports explicit `--record-once` and `--alsa-device hw:0,2`
diagnostic options; the ordinary app-drawer launch still waits for Start.
WAVs and recorder logs stay mode 0600 inside the user's private state directory.

Direct ALSA tests of TX slots 5 and 6 remained silent after the startup
transient. Slot **7**, using **DMIC3 Switch**, captured sustained audio on
channel 0; channel 1 was zero. With the V2 DTB, DEC1 on the existing input6
temporarily kept the shared DMIC clock and MIC BIAS3 powered while DEC0 selected
slot7. The 19.89-second recording's channel-0 RMS after two seconds was 568.55,
peak 7116. After conversion to 16 kHz mono, native Voxtype produced coherent
video narration. A repeated normal PipeWire test captured 20.20 seconds and
also transcribed narration, with RMS 267.62 after two seconds. One immediately
after an audio restart failed with `no target node available`; this was a source
discovery race, not a test of a silent microphone. The repeat waited for source
enumeration first.

This result matches Luke Johnson's
[Pocknix Thor UCM](https://github.com/shuuri-labs/pocknix-os/blob/ba1de097fb0e0df07bcb32f05dc8e957d62090bc/devices/sm8550/packages/pocknix-bsp-sm8550/HiFi-Thor.conf)
and board route, also present in Basit's SteamOS ARM port. Keep their credit:
it supplied the working **DMIC3/SWR_MIC7** lead. The one-based DAPM ADC controls
a shared physical clock pair; changing its ordinal to match the zero-based
SoundWire port switch was an incorrect basis for choosing the voice channel.
The board-specific observation supersedes the V2 numbering hypothesis.

V3 adds only `DMIC3 ← MIC BIAS3` and
`TX SWR_INPUT7 ← DMIC3_OUTPUT` to the proven DTB. Its UCM enables the DMIC3
port/mixer and DEC0/SWR_MIC7, disables DEC1/DEC2 and the earlier analog ADC
switches, and keeps the required stereo frontend declaration. It no longer
needs the diagnostic DEC1 keepalive. Existing playback and jack-gated headset
devices remain in the profile.

- V3 image SHA256: `3c6b2569a964ec8c04b5bc96950df3921d58b016b77d40fd72fa597c10986763`.
- DTB SHA256: `89582150c9c9e1047e02d15c304b9a3cc3aa890563276064674f5bf47036d61e`.
- UCM fragment SHA256: `56052faa39b2255c5a4f2e2301efe8f98003cea7ec91bf7e71f2980e2d77aab3`.
- Full installed HiFi SHA256: `501d382a7d91853ff421dc6111792e63d2ed7b78dbb31c3e5238ee424b5125f8`.

Independent unpacking verified the proven decompressed kernel, ramdisk and
boot fields/command line; the decompiled DTB diff changes only those two route
pairs. The guarded installer accepts only the documented proven or V2 state,
checks the corresponding UCM digest, saves the pre-V3 UCM separately, and
preserves KERNEL.bak and the raw boot/recovery images.

The V3 normal reboot passed: Wi-Fi SSH returned, slot A remains successful and
bootable, ALSA/desktop/audio services returned and systemd reports no failed
services. The normal PipeWire app then recorded **20.24 seconds** of the video,
RMS **328.31** after two seconds, and displayed coherent transcription. A
private desktop screenshot verifies the finished app, meter and transcript.
This establishes **controlled external speech captured acoustically through
the onboard digital path**, including after a warm reboot. It does not yet
establish the user's own voice/dictation accuracy, cold boot, long use or
headset-microphone behavior. Back's requested dictation mapping still awaits
the user's live-voice acceptance.

Private evidence: `microphone-v2-full-test-registers.txt`,
`microphone-single-slot6-test.txt`, `microphone-v3-result.png`, and the device's
private microphone WAV/log/transcript files. No video audio/transcript is
published here. Earlier failed candidates remain under their separate build
directories.

### EasyEffects installation

At the user's request, signed ARM packages **easyeffects 8.3.0-1** and
**lsp-plugins-lv2 1.2.35-1** are installed. Omarchy's package wrapper first hit
the kernel's missing Landlock support; the documented per-command
`--disable-sandbox-filesystem` workaround was used. Stale KDE package URLs
returned 404, so repository catalogs were refreshed and the reviewed
EasyEffects dependency transaction installed. No general OS/kernel upgrade
was run. LSP supplies the built-in delay module missing on the first launch.

An SSH-only `easyeffects --version` attempt aborted in Qt platform setup with
`could not connect to display`; coredump/journal evidence confirms the missing
graphical environment, not memory exhaustion. Launch through the user's live
Wayland manager succeeds. EasyEffects was stopped during raw capture tests;
the microphone result does not rely on its processing. It remains available
for gain/noise processing after live-voice acceptance.

Two further EasyEffects aborts occurred while its PipeWire connection was
stopped during diagnostics. Both journals report `Broken pipe` followed by
`No connection to PipeWire. Aborting!`; the cores point through the PipeWire
callback to Qt's fatal logger. Stop EasyEffects and wait for it to exit before
restarting audio services. The final post-reboot launch remains running,
renders on the desktop and has no missing-LSP warnings. Its input capture is
idle, and no recording process or active DSP capture link remains at readback.
Private evidence is `easyeffects-session-check.txt` and
`easyeffects-installed.png`.
