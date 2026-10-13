# Bluetooth input diagnosis — October 12, 2026

The user reported that a Razer Basilisk X and a ThinkPad Compact Bluetooth
Keyboard with TrackPoint appeared to pair but repeatedly failed to stay usable.
Diagnosis and configuration work used the verified Wi-Fi SSH connection.

## Confirmed before repair

- The WCN7850 Bluetooth firmware loads; hci0 is powered and not rfkill-blocked.
  The generated public address is identical across the two recorded controller
  initializations in this boot. This does not establish persistence across boots.
- Both peripherals are `Trusted: yes` but `Paired: no` and `Bonded: no`.
  The mouse temporarily reports Connected without producing an input device.
- BlueZ 5.87-2 repeatedly logs `No agent available for request type 2` and
  `device_confirm_passkey: Operation not permitted`. Classic keyboard attempts
  include rejection of an unbonded device. These are observed authentication
  failures, not proof of radio instability or a firmware defect.
- The pinned mobile panel uses `(paired || bonded || trusted)` for its remembered
  state, labels remembered devices "Paired", and chooses Connect instead of Pair.
  The installed Omarchy helper suppresses pairing errors, trusts even after a
  failed pair attempt, and has no persistent graphical authentication agent.
- The kernel has UHID built in and HIDP as a loadable module. `/dev/uhid` exists.
  Loading the existing hidp module succeeded. Generic HID support exists, but
  device-specific Lenovo/Razer kernel options are absent; functional input still
  needs testing before deciding whether those options matter.

## Repair applied

Blueman 2.4.6-2 and python-cairo were installed from the signed Arch Linux ARM
repository. Its standard desktop applet registers a default KeyboardDisplay
BlueZ agent for passcode and confirmation requests. The packaged static user
service is attached to `graphical-session.target.wants` and running. X11-only
wakelock and optional plugin warnings do not establish an agent failure; tray
warnings and a ShowConnected bookkeeping exception are retained in private logs.
The user's Blueman `notification-daemon` setting is false so authentication uses
its standard GTK dialog, keeping passcodes and confirmation buttons visible on
the handheld. The previous setting was saved privately; this does not change
Omarchy's general notification preferences.
Because that setting also turned routine connect/disconnect notifications into
dialogs, the optional ConnectionNotifier plugin is disabled. Authentication
dialogs remain available. The applet was restarted to clear old status dialogs;
Bluetooth itself was not restarted.

`native/fix-bluetooth-pairing.py` adapts only the user-owned mobile
BluetoothScreen.qml. It keeps remembered/trusted state for listing/forgetting,
but requires a stored bond for the Pair/Connect choice and labels.
A temporary pairing or unbonded connection no longer counts as completion. Pairing
gets time for the user to respond to an authentication prompt.

`native/odin-bluetooth-device` starts the applet when needed, pairs unbonded
devices even if trusted, verifies a stored bond before trusting, and
propagates command failures. It leaves BlueZ's bond requirements enabled.
If BlueZ already reports a temporary Pair without a saved bond, it requires
Forget followed by fresh pairing rather than silently deleting an active record.
`native/install-bluetooth.sh` records the deployment. Upstream shell/package
source is unchanged; the panel backup is beside the user-owned file.

The default agent is active and repeated "No agent available" errors stopped
after it started. The first mouse retry outside fresh pairing mode timed out
without a prompt. New mouse logs also contain GATT descriptor/Protocol Mode
read errors; these still need a valid new bond before interpretation.

The user put the mouse into fresh pairing mode: BT slider,
both side buttons plus DPI for three seconds, repeating double-blink indicator.
See [Razer's instructions](https://mysupport.razer.com/app/answers/detail/a_id/5387).
The user then confirmed that the mouse works. Readback reports
`Basilisk X HyperSpeed` Paired/Bonded/Trusted/Connected all yes, and the kernel
exposes the mouse and its associated HID consumer/system/keyboard interfaces.
This is a physical pointer-input pass, not yet an off/on or cold-boot reconnect
pass. The keyboard still reports unpaired/unbonded and disconnected.

A subsequent keyboard attempt briefly reported Paired yes/Connected yes but
Bonded no. Its private state file contains only General and DeviceID sections,
with no stored LinkKey section, and BlueZ rejects its unbonded HID connection.
The user saw repeated connect/disconnect screens and no passcode, and suspects
the keyboard needs charging. Battery state is not confirmed. Keyboard attempts
are deferred until it is charged; no keyboard typing pass is claimed. This also
exposed that temporary Paired alone is insufficient, so the panel/helper now
require a saved bond rather than either Paired or Bonded.
The panel labels that temporary state "Pairing incomplete" and directs the
user to Forget and fresh pairing instead of starting another doomed connection.

## Next acceptance

1. Pair the keyboard with its displayed passcode entered on the keyboard,
   then verify actual typing and TrackPoint input.
   [Lenovo's guide](https://download.lenovo.com/pccbbs/options/0b40361.pdf) describes
   Fn+Delete for switching a previously connected keyboard into pairing mode
   and entering the displayed passcode followed by Enter on the keyboard.
2. Test reconnect after peripheral off/on, then sustained connection. Restart
   the Bluetooth service or controller only after the working bond is saved
   and a concrete reconnection test is ready. A later cold boot remains separate.

Raw logs, pairing material and peripheral/controller identifiers stay under
ignored `private/bootstrap/` and the device's root-only BlueZ state directory.
Do not publish `/var/lib/bluetooth` or capture ordinary user keystrokes for a
diagnostic report.

Credits: [BlueZ](https://github.com/bluez/bluez),
[Blueman](https://github.com/blueman-project/blueman), Arch Linux ARM,
Simon Schubert's mobile panel and Omarchy's Bluetooth controls. See BlueZ's
[agent API](https://github.com/bluez/bluez/blob/5.87/doc/org.bluez.Agent.rst)
and [agent-manager API](https://github.com/bluez/bluez/blob/5.87/doc/org.bluez.AgentManager.rst)
for the authentication callbacks and default-agent behavior.
