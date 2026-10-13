#!/usr/bin/env python3
"""Correct pairing state in Simon Schubert's pinned mobile Bluetooth panel.

Trust and temporary pairing are not a saved bond. Use the visible Blueman/BlueZ
agent, and keep pairing pending until bonding and connection complete. Apply to
the user-owned BluetoothScreen.qml; original authorship/comments are retained.
"""
from pathlib import Path
import sys

CONNECT_GUARD = '''if (row.connected && row.paired) return
    if (row.temporaryPair) {
      root.errorAddress = row.address
      root.errorText = "Pairing was not saved. Tap Forget, then put the device in pairing mode and Pair again."
      return
    }'''

CHANGES = {
    'known: !!(d.paired || d.bonded || d.trusted),':
        'known: !!(d.paired || d.bonded || d.trusted),\n        paired: !!d.bonded,\n        temporaryPair: !!d.paired && !d.bonded,',
    'Quickshell.execDetached(["omarchy-bluetooth-device", verb, row.address])':
        'Quickshell.execDetached(["odin-bluetooth-device", verb, row.address])',
    'if (row.connected) return': CONNECT_GUARD,
    'root.runAction(row, row.known ? "connect" : "pair", row.known ? "Connecting" : "Pairing")':
        'root.runAction(row, row.paired ? "connect" : "pair", row.paired ? "Connecting" : "Pairing")',
    'else done = !!(found && found.connected)':
        'else done = !!(found && found.connected && found.paired)',
    'interval: 25000': 'interval: root.busyVerb === "Pairing" ? 115000 : 25000',
    ': rowItem.modelData.connected ? "Connected"':
        ': rowItem.modelData.connected && rowItem.modelData.paired ? "Connected"',
    ': rowItem.modelData.known ? "Paired"':
        ': rowItem.modelData.temporaryPair ? "Pairing incomplete"\n                    : rowItem.modelData.paired ? "Paired"',
    'visible: !rowItem.modelData.connected':
        'visible: !rowItem.modelData.connected || !rowItem.modelData.paired',
    'text: rowItem.modelData.known ? "Connect" : "Pair"':
        'text: rowItem.modelData.paired ? "Connect" : "Pair"',
}


def main():
    path = Path(sys.argv[1])
    text = path.read_text()
    if '// Portal pairing-state and visible-agent fix' in text:
        earlier = 'paired: !!(d.paired || d.bonded),'
        original = text
        if earlier in text:
            if text.count(earlier) != 1:
                raise SystemExit('Unexpected earlier Portal pairing-state fix')
            text = text.replace(earlier, 'paired: !!d.bonded,', 1)
        elif 'paired: !!d.bonded,' in text:
            pass
        else:
            raise SystemExit('Unexpected Portal pairing-state fix version')
        if 'temporaryPair:' not in text:
            upgrades = {
                'paired: !!d.bonded,': 'paired: !!d.bonded,\n        temporaryPair: !!d.paired && !d.bonded,',
                'if (row.connected && row.paired) return': CONNECT_GUARD,
                ': rowItem.modelData.paired ? "Paired"':
                    ': rowItem.modelData.temporaryPair ? "Pairing incomplete"\n                    : rowItem.modelData.paired ? "Paired"',
            }
            for before, after in upgrades.items():
                if text.count(before) != 1:
                    raise SystemExit(f'Unexpected Portal bond-state panel: {before}')
                text = text.replace(before, after, 1)
        if text != original:
            path.with_suffix('.qml.before-bond-required').write_bytes(path.read_bytes())
            path.write_text(text)
            print('Bluetooth completion requires a stored bond; incomplete pairing has visible recovery instructions')
        else:
            print('Bluetooth bond-state fix already applied')
        return
    for before, after in CHANGES.items():
        if text.count(before) != 1:
            raise SystemExit(f'Unexpected pinned Bluetooth panel: {before}')
        text = text.replace(before, after, 1)
    path.with_suffix('.qml.before-portal-pairing').write_bytes(path.read_bytes())
    path.write_text('// Portal pairing-state and visible-agent fix\n' + text)
    print('Bluetooth panel now requires a stored bond before pairing completion')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: fix-bluetooth-pairing.py USER_BluetoothScreen.qml')
    main()
