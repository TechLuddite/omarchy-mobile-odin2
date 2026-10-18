# AYN Odin 2 Portal gamepad classification

The physical `AYN Odin2 Gamepad` can be classified as a mouse by udev because
its dedicated `BTN_BACK` is in the mouse-button range. On the tested Portal,
udev reported `ID_INPUT_MOUSE=1` without `ID_INPUT_JOYSTICK`; SDL omitted the
main pad and Steam listed only the separate rear paddles. Device permissions
already allowed access, so this was not a permissions failure.

`native/60-odin2-gamepad-joystick.rules` sets `ID_INPUT_JOYSTICK=1` and removes
`ID_INPUT_MOUSE` for event/js nodes matching all of:

- Name: `AYN Odin2 Gamepad`
- Bus: `0003`
- Vendor: `2020`
- Product: `3001`

The filename places it after `60-input-id.rules` and before
`60-persistent-input.rules`, so persistent by-path links also use joystick
classification. The rule does not depend on an event/js index. Rear paddles,
touchscreen and virtual mouse do not match it.

`native/install-gamepad.sh` installs the rule into `/etc/udev/rules.d/` during
rootfs setup. On an existing system, back up any pre-existing file at that
destination and install this rule alone; rerunning the complete gamepad
installer can overwrite unrelated plugin files. Reload udev rules and trigger
a change only on the matched physical gamepad event/js nodes, or allow the
rule to take effect on device re-add or the next boot. Games must also have
access to the pad without an exclusive desktop-input grab.

## Validation on October 18, 2026

- `udevadm test --extra-rules-dir` gives joystick-only classification for the
  physical event/js nodes. The separate rear-paddle nodes, touchscreen and
  virtual mouse retain their prior classifications.
- Installed readback confirms `ID_INPUT_JOYSTICK=1`, no `ID_INPUT_MOUSE` and
  corrected joystick by-path links. An earlier later-numbered trial corrected
  the properties but left the mouse symlink; the final rule order fixes both.
- Native SDL2 enumeration changes from rear paddles only to including
  `AYN Odin2 Gamepad`, GUID `0300b605202000000130000001000000`, with
  `SDL_IsGameController` true. The descriptor probe does not open controller
  handles, poll game input, send rumble or inject events.
- The user confirms controller input works in The Expendabros after applying
  the rule in Game mode. Subsequent game crashes remain unresolved; this
  acceptance establishes input detection, not sustained game stability.
- Shell syntax and diff checks pass. No other Odin model, reconnect or next-boot
  acceptance is claimed, and no controller plugin or saved mapping is changed
  by this rule.

To roll back, restore the previous rule if one existed, otherwise remove only
`/etc/udev/rules.d/60-odin2-gamepad-joystick.rules`. Reload udev rules and apply
the change to the matched device nodes, or on device re-add/next boot. Reopen
Steam/games as needed so their device lists refresh.

The relevant classification behavior is implemented by
[systemd's input_id](https://github.com/systemd/systemd/blob/main/src/udev/udev-builtin-input_id.c)
and consumed by [SDL's Linux udev backend](https://github.com/libsdl-org/SDL/blob/main/src/core/linux/SDL_udev.c).
This device policy does not modify either project or Parminder Klair's
Controller Control plugin.
