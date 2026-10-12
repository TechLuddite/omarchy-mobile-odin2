# Repository tracking

`/srv/projects/odin2-omarchy` is the working directory and the record for the
whole device port. External forks do not replace the notes here. Keep rationale,
source revisions, installation steps, checks, failures and remaining hardware
gaps in this project; keep raw device evidence under its ignored `private/`.

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
