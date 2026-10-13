# Odin display feed for OBS — October 13, 2026

The Portal display is available on the project host as a live OBS **Media Source**.
OBS already running on this machine has a dedicated **Odin 2 Portal** scene and
**Odin 2 Portal - Live Video** source. A private source screenshot confirmed the
upright landscape desktop, bar, keyboard toggle and gesture strip.

Media Source input:

```text
http://127.0.0.1:17855/odin.ts
```

To use the same feed in another OBS scene, add the existing source, or add a
Media Source with Local File unchecked, that Input URL and Input Format
`mpegts`. Closing the source while inactive allows capture to stop when no
viewer remains. The profile is **H.264, 1280×720, 30 FPS, video only**.

## Use and lifecycle

Host controls:

```bash
odin-obs-stream start
odin-obs-stream stop
odin-obs-stream restart
odin-obs-stream status
```

The host's `odin-obs-stream.service` is enabled for desktop login. The relay
listens only on loopback. Connecting a player or OBS starts the sender through
the existing key-only `ssh odin2` alias; the last viewer disconnecting stops
capture after a short grace period. OBS retries interrupted network input.
The Odin must be awake, on Wi-Fi and running its normal Wayland session.
`http://127.0.0.1:17855/status` reports viewer count, capture state and bytes
relayed. The HTTP URL is local to this host; the device-to-host connection uses
authenticated SSH and needs no new device network listener.

## Installed integration

- On the Odin, signed ARM package **wf-recorder 0.6.0-2** supplies Wayland
  display capture. Existing **FFmpeg 9.0.2-2** and **x264
  0.165.r3222.b35605a-2** provide encoding. Pacman used the previously documented
  per-command Landlock workaround; it installed only wf-recorder.
- `native/odin-obs-capture` is deployed as `/usr/local/bin/odin-obs-capture`.
  The host starts it in the live desktop user manager with
  `systemd-run --user --quiet --wait --pipe --collect --unit=odin-obs-capture`.
  This imports the actual Wayland environment and presents a start notification.
- The sender selects `DSI-1`, captures continuously at 30 FPS, scales the raw
  input to 720p and relies on wf-recorder's output-transform correction. Portal
  buffers are 1080×1920 with a 90-degree output transform, so scaling before
  that transform must respect the portrait buffer. The first fixed 1280×720
  filter produced portrait 720×1280 output; the corrected filter chooses dimensions
  from the input aspect, producing the verified landscape 1280×720 output.
- The libx264 profile uses `ultrafast`, `zerolatency`, CRF 25, two encoding
  threads and repeated headers/keyframes about once per second. Encoder stdout
  diagnostics go to stderr; MPEG-TS has a separate inherited file descriptor so
  SSH stdout carries video bytes only. No audio source is opened.
- `scripts/odin-obs-relay.py` is deployed as
  `~/.local/bin/odin-obs-relay` on the host. Its standard-library HTTP server
  shares one sender between viewers, caps each viewer queue, disconnects slow
  viewers and reconnects capture on the next request. Video is relayed in
  memory. `scripts/odin-obs-stream` and `native/odin-obs-stream.service` provide
  the host controls and user service.
- `scripts/odin-obs-setup.py` used OBS's existing authenticated WebSocket server
  to create the dedicated scene and network media source, fit it to the existing
  canvas and display it when no live output was active. OBS settings use
  `is_local_file=false`, `input_format=mpegts`, buffering 0 MB and reconnect
  delay 2 seconds. The API password is read from its existing local configuration
  and is never printed or copied into this project. No stream or recording was
  started. The host's existing OBS scene files were backed up privately before
  the source was added.

Reproduction: install wf-recorder on the Portal and the sender at its path,
install the relay/control scripts under the host's `~/.local/bin/` and the user
service under `~/.config/systemd/user/`, then reload and enable/start that user
service. Add the Media Source manually, or run the setup helper in a Python
environment containing `websocket-client` while OBS's authenticated local API
is enabled. The local setup environment is ignored `tools/obs-stream-venv/`.

## Verification and limits

- ffprobe readback confirms **H.264, 1280×720, 30/1 FPS**.
- After a probe disconnect, the relay reported zero viewers and no active
  capture. A later OBS connection started a new capture.
- OBS reports **OBS_MEDIA_STATE_PLAYING**. Its own source screenshot shows
  the correct Portal display; verification frames stay in ignored
  `private/obs-stream/`.
- A second client joined the active OBS stream and decoded 90 frames without
  starting a second wf-recorder process. The host user service validates with
  `systemd-analyze --user verify`.
- The late-joining decoder emitted initial missing-PPS messages while waiting
  for repeated H.264 headers, then completed its 90-frame decode. OBS recovered
  automatically after a deliberate host-relay restart and reported playing;
  another private source screenshot verified the restored feed.
- A short readback on the idle desktop showed about **106% process CPU**
  (roughly one CPU core) and about **46 MB** service memory on the Odin.
  This is software encoding. Hardware encode support, gameplay FPS impact,
  end-to-end latency, audio and sustained-session performance are unverified.
- The device briefly disappeared from mDNS during setup; the user restored its
  connection, and subsequent deployment/streaming succeeded. No SSH keys or
  authentication policy were changed.

Host sender diagnostics are under `~/.local/state/odin-obs-stream/capture.log`;
staged device files are under
`~/.local/state/odin2-omarchy/obs-stream/`. Raw OBS configuration backups and
captured frames remain private. Removing the dedicated OBS scene/source and
stopping/disabling the host relay undoes the integration; remove the local
sender and installed helpers only after capture has stopped.

## Credits and sources

- [wf-recorder](https://github.com/ammen99/wf-recorder) — ammen99 and
  contributors: capture, transform correction, filters and muxing. Its MIT
  notice stays with the installed package; no recorder code was copied.
- [FFmpeg](https://ffmpeg.org/) and [x264](https://www.videolan.org/developers/x264.html)
  contributors: encoding, MPEG-TS, probing and decode verification. Original
  package notices remain installed on both machines.
- [OBS Studio](https://obsproject.com/) and
  [obs-websocket](https://github.com/obsproject/obs-websocket) contributors:
  media playback, scene composition and the authenticated setup protocol.
  [Media Source documentation](https://obsproject.com/kb/media-sources) and the
  official WebSocket protocol informed the integration.
- [websocket-client](https://github.com/websocket-client/websocket-client)
  contributors: Python WebSocket transport for the setup helper, version 1.9.2
  in the isolated local environment, with its Apache-2.0 notice retained there.
- OpenSSH, Wayland/Hyprland, Omarchy and Python contributors: authenticated
  transport, compositor capture and host service/HTTP foundations. The relay,
  sender profile and setup helper are this project's integration work.

Package versions and inspected protocol/source hashes are recorded in
`sources.json`, with project-wide attribution in README and CREDITS.

## Fullscreen capture investigation checkpoint

During the later Scavland startup test, OBS showed a nearly black game feed while
a native screenshot showed Scavland's main menu. The desktop feed and reconnect
results above remain valid; **fullscreen game capture has not passed**.

The sender currently includes `--no-dmabuf` as a diagnostic candidate, deployed
after this failure. Restarting the relay with that option did not establish a
fix. Hyprland readback showed direct scanout already disabled and blocked while
recording; no direct-scanout rule was changed. Continue by comparing native
frames, the sender stream and relay/OBS decoding to locate the discrepancy.
Do not count a playing media status alone as visual acceptance. Verification
frames stay under ignored `private/scavland-startup/`.
