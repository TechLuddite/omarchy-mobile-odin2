# Bluetooth input diagnosis — October 12, 2026

The user reported that a Razer Basilisk X and a ThinkPad Compact Bluetooth
Keyboard with TrackPoint appeared to pair but repeatedly failed to stay usable.
Diagnosis and configuration work used the verified Wi-Fi SSH connection.

Current acceptance: the user confirms ThinkPad keyboard typing and TrackPoint
pointer movement after a fresh six-digit passcode pairing through the normal
Pair flow. Both the ThinkPad and Basilisk X report Paired, Bonded, Trusted and
Connected, with their corresponding input interfaces. The user also confirms
keyboard typing and TrackPoint reconnect after off/on without another code.
Mouse off/on and Odin cold-boot acceptance remain separate checks. BlueZ, Blueman, the upstream
kernel's generic HID driver, Simon Schubert's panel and Omarchy supplied the
working components; no new keyboard driver was needed for this input pass.

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
pass. The keyboard was still unpaired/unbonded and disconnected at this point.

A subsequent keyboard attempt briefly reported Paired yes/Connected yes but
Bonded no. Its private state file contains only General and DeviceID sections,
with no stored LinkKey section, and BlueZ rejects its unbonded HID connection.
The user saw repeated connect/disconnect screens and no passcode, and suspected
the keyboard needed charging. Battery state is not confirmed. Attempts were
deferred until the user returned; no keyboard typing pass is claimed. This also
exposed that temporary Paired alone is insufficient, so the panel/helper now
require a saved bond rather than either Paired or Bonded.
The panel labels that temporary state "Pairing incomplete" and directs the
user to Forget and fresh pairing instead of starting another doomed connection.

When the user returned with the keyboard powered on and "half connected", a
fresh snapshot again showed Paired/Bonded/Connected all no and Trusted yes,
with no keyboard input interfaces. Only that unbonded keyboard record was
cleared, after checking its Bonded property. Discovery found it again. The next
pair attempt waited for the keyboard's fresh pairing mode.
Selected HCI security-event and agent method-name monitors exclude key values,
pairing arguments and ordinary input reports; their private pre-pair output does
not establish a completed authentication exchange.

## Keyboard passcode and reconnect checkpoint

A controlled attempt subsequently negotiated local DisplayYesNo and remote
KeyboardOnly capabilities, with Dedicated Bonding and MITM required locally.
The controller issued a passkey notification; without timely entry the keyboard
ended pairing roughly 30 seconds later. This establishes an authentication
exchange, rather than a requirement to disable bonding or replace a HID driver.

A temporary GTK4 display showed one large six-digit passcode on the handheld.
The user liked the presentation and requested that it be part of the normal Pair
flow after testing. The initial observer could receive a later retry's code;
the subsequent diagnostic stopped after the first code and used a separate GTK
application instance. Codes, key values and ordinary input reports are not
saved in the diagnostic logs or this repository.

After the user entered the last displayed code, BlueZ reported Paired and Bonded
yes, and the root-only device state had a LinkKey section with key type 5. This
is a saved **local** bond, not a typing pass. The next connection failed with
`br-connection-key-missing`; another attempt reported
`br-connection-create-socket` with an authentication disconnect. No ThinkPad or
TrackPoint input interfaces appeared. After the user attempted off/on, one
reconnect still failed and a later trace recorded a page timeout. The keyboard's
power state and whether it retains the same key remain unresolved. The saved
keyboard bond has been preserved, and the working mouse bond was not removed.

These failures exposed another helper problem: `bluetoothctl` can print a failed
Connect while returning zero. The deployed helper now uses synchronous BlueZ
D-Bus calls for trust, Connect, Disconnect and Forget, and verifies Connected
after Connect. The observed failed keyboard reconnect now returns a nonzero
status. This corrects error reporting; it does not fix the keyboard itself.

`native/odin-bluetooth-pair` is a **candidate**, not yet wired into the mobile
panel or installed by `install-bluetooth.sh`. It combines the large GTK4 display
with an application-owned BlueZ Agent1 on the same bus connection as Pair.
DisplayPasskey progress updates stay in the same window; confirmation and code
entry requests also have touch controls. It requires neither root nor HCI
capture and leaves Blueman as the default agent. Pair completion requires Bonded;
the subsequent Connect must actually succeed. Source compilation, actual
AgentManager registration/unregistration on the Odin, and the GTK saved-bond
guard passed. No fresh Pair or keyboard-input acceptance is claimed for it.
The diagnostic passcode display is retained privately, rather than installed
as a permanent controller observer.

The user went away and could not enter codes, so no fresh pairing was started
while they were away. The planned next test was a controlled pairing through
the candidate wizard. If reconnect still fails,
collect a security-event trace with wide btmon columns so command names are not
truncated; keep keys and input reports excluded.

## Successful normal pairing and physical input

When the user returned, the keyboard still had a saved local bond but was
disconnected and had no input interfaces. The mouse was connected. The failed
keyboard state was backed up privately in a root-only directory on the Odin,
then only that keyboard record was removed for fresh pairing. Discovery found
the keyboard again. The candidate wizard was staged at
`/usr/local/bin/odin-bluetooth-pair`, but no candidate Pair call was started.

The user paired again through the normal dialog, saw its six-digit code, typed
it on the ThinkPad keyboard and pressed Enter. The installed mobile helper
still uses Blueman's default agent; this success does not validate the candidate
wizard. Readback verified Paired/Bonded/Trusted/Connected all yes for both
peripherals. The kernel exposed ThinkPad Keyboard, Mouse, Wireless Radio Control
and additional HID interfaces through UHID and `hid-generic` (17EF:6048).
The user explicitly confirmed both terminal typing (`echo bluetooth-ok`) and
TrackPoint pointer movement. Ordinary keystrokes were not captured.

The user then powered the ThinkPad keyboard off for three seconds and back on
for one second, without Fn+Delete. They confirmed that typing and TrackPoint
both reconnected without a code. Follow-up readback again reports all four
pairing/connection flags yes for both peripherals and exposes the ThinkPad
input interfaces. This accepts one keyboard power-cycle reconnect, not a
Bluetooth-service restart, mouse power cycle, sustained-use or Odin cold-boot test.

Keep the working normal Pair flow. The experimental wizard remains separate
until its own real pairing test is accepted; replacing a working default agent
is not required to make pairing part of the normal connection process.

## Next acceptance

1. Keyboard passcode entry, actual typing and TrackPoint input passed through
   the normal Pair flow.
   [Lenovo's guide](https://download.lenovo.com/pccbbs/options/0b40361.pdf) describes
   Fn+Delete for switching a previously connected keyboard into pairing mode
   and entering the displayed passcode followed by Enter on the keyboard.
2. Keyboard off/on reconnect without Fn+Delete or re-pairing passed. Test
   mouse off/on and sustained connection. Restart
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
