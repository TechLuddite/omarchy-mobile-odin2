# Omarchy dictation on the Odin2 Portal

Working directory: `/srv/projects/odin2-omarchy`.

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
