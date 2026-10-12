#!/usr/bin/env python3
"""Read-only Android/fastboot inspection; never changes boot or storage state."""
import argparse
import datetime
import json
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]


def locate(name):
    bundled = ROOT / 'tools/android-tools/usr/bin' / name
    return str(bundled) if bundled.is_file() else shutil.which(name)


def run(argv):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=12)
        return {'returncode': result.returncode,
                'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {'error': 'query timed out'}
    except OSError as error:
        return {'error': str(error)}


def redact(value, serials):
    if isinstance(value, str):
        for serial in serials:
            value = value.replace(serial, '<transport-serial>')
        return value
    if isinstance(value, dict):
        return {k: redact(v, serials) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v, serials) for v in value]
    return value


def inspect():
    report = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'device_writes': False}
    edl_devices = []
    for node in pathlib.Path('/sys/bus/usb/devices').iterdir():
        try:
            vendor = (node / 'idVendor').read_text().strip()
            product = (node / 'idProduct').read_text().strip()
        except OSError:
            continue
        if (vendor, product) == ('05c6', '9008'):
            edl_devices.append({'vendor': vendor, 'product': product})
    report['edl_usb_devices'] = edl_devices
    transports = []
    serials = []
    for mode, args in [('adb', ['devices']), ('fastboot', ['devices'])]:
        executable = locate(mode)
        if not executable:
            report[mode] = {'error': 'tool unavailable'}
            continue
        listing = run([executable, *args])
        report[mode] = {'listing': listing}
        for line in listing.get('stdout', '').splitlines():
            parts = line.split()
            if len(parts) >= 2 and not line.startswith('List of devices'):
                # Tool stdout lists one serial and state per transport.
                serials.append(parts[0])
                transports.append((mode, executable, parts[0], parts[1]))
    if len(transports) != 1:
        report['status'] = ('No device transport; enable USB debugging and authorize '
                            'this computer, or enter the bootloader.' if not transports
                            else 'Multiple transports; disconnect other devices before inspecting.')
        if not transports and edl_devices:
            report['status'] = ('Qualcomm EDL detected. ADB/fastboot are unavailable in this mode; '
                                'use the separate EDL reader for storage inspection.')
        return redact(report, serials)
    mode, executable, serial, state = transports[0]
    if mode == 'adb' and state not in ('device', 'recovery'):
        report['status'] = f'ADB state is {state}; no shell queries performed.'
        return redact(report, serials)
    queries = {}
    if mode == 'adb':
        properties = [
            'ro.product.manufacturer', 'ro.product.model', 'ro.product.device',
            'ro.board.platform', 'ro.product.cpu.abi', 'ro.build.display.id',
            'ro.build.version.release', 'ro.build.version.security_patch',
            'ro.boot.slot_suffix', 'ro.boot.verifiedbootstate',
            'ro.boot.flash.locked', 'ro.boot.vbmeta.device_state',
        ]
        for prop in properties:
            queries[prop] = run([executable, '-s', serial, 'shell', 'getprop', prop])
        for name, command in {
            'kernel': ['uname', '-a'],
            'shell_identity': ['id'],
            'block_devices': ['cat', '/proc/partitions'],
            'partition_names': ['ls', '-l', '/dev/block/by-name'],
            'input_devices': ['cat', '/proc/bus/input/devices'],
        }.items():
            queries[name] = run([executable, '-s', serial, 'shell', *command])
    else:
        for variable in ['product', 'current-slot', 'unlocked', 'secure',
                         'version-bootloader', 'is-userspace', 'slot-count']:
            queries[variable] = run([executable, '-s', serial, 'getvar', variable])
    report[mode]['queries'] = queries
    report['status'] = 'Inspection finished; unsupported/denied queries are recorded individually.'
    return redact(report, serials)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(inspect(), indent=2))


if __name__ == '__main__':
    main()
