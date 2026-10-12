#!/usr/bin/env python3
"""Validate captured image extents, GPT CRCs, and both partition-table copies."""
import datetime
import hashlib
import json
import pathlib
import struct
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKUP = ROOT / 'private/base-backup'


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        while data := stream.read(8 * 1024 * 1024):
            result.update(data)
    return result.hexdigest()


def main():
    manifest = json.loads((BACKUP / 'manifest.json').read_text())
    storage = json.loads((BACKUP / 'storage-map.json').read_text())
    assert manifest['complete'], 'Capture is incomplete'
    sector = manifest['sector_size']
    regions = manifest['regions']
    for region in regions:
        path = BACKUP / region['file']
        assert path.stat().st_size == region['bytes'] == region['sectors'] * sector
        assert digest(path) == region['sha256'], f'Checksum mismatch: {path}'
    def read(lun, offset, length):
        for region in regions:
            start = region['start_sector'] * sector
            if region['lun'] == lun and start <= offset and offset + length <= start + region['bytes']:
                with (BACKUP / region['file']).open('rb') as stream:
                    stream.seek(offset - start)
                    data = stream.read(length)
                    assert len(data) == length
                    return data
        raise AssertionError(f'Uncaptured range: LUN {lun}, offset {offset}, length {length}')
    def gpt(lun, lba):
        header = read(lun, lba * sector, sector)
        assert header[:8] == b'EFI PART', f'No GPT header: LUN {lun}, LBA {lba}'
        size, checksum = struct.unpack_from('<II', header, 12)
        assert 92 <= size <= sector
        crc_header = bytearray(header[:size])
        struct.pack_into('<I', crc_header, 16, 0)
        assert zlib.crc32(crc_header) == checksum, f'GPT header CRC mismatch: LUN {lun}'
        current, alternate, first, last = struct.unpack_from('<QQQQ', header, 24)
        array_lba, count, entry_size, array_crc = struct.unpack_from('<QIII', header, 72)
        assert current == lba and entry_size >= 128 and count <= 4096
        table = read(lun, array_lba * sector, count * entry_size)
        assert zlib.crc32(table) == array_crc, f'GPT entry CRC mismatch: LUN {lun}'
        parts = []
        for number in range(count):
            entry = table[number * entry_size:(number + 1) * entry_size]
            if entry[:16] == bytes(16):
                continue
            start, end = struct.unpack_from('<QQ', entry, 32)
            assert first <= start <= end <= last
            name = entry[56:128].decode('utf-16-le').split('\0', 1)[0]
            parts.append({'name': name, 'offset': start * sector, 'size': (end - start + 1) * sector})
        return {'alternate': alternate, 'guid': header[56:72], 'table': table, 'partitions': parts}
    verified = []
    for lun in storage['luns']:
        number = lun['lun']
        primary = gpt(number, 1)
        assert primary['alternate'] == lun['sectors'] - 1
        secondary = gpt(number, primary['alternate'])
        assert secondary['alternate'] == 1
        assert primary['guid'] == secondary['guid'] and primary['table'] == secondary['table']
        assert primary['partitions'] == lun['partitions'], f'GPT differs from inspected map: LUN {number}'
        verified.append({'lun': number, 'partitions': len(primary['partitions']),
                         'primary_and_secondary_gpt_crc': 'pass', 'partition_map_comparison': 'pass'})
        print(f"LUN {number}: both GPT copies, CRCs and {len(primary['partitions'])} partitions verified")
    report = {'verified_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'image_sha256_checks': 'pass', 'luns': verified,
              'restore_test': 'not performed', 'userdata_payload': 'excluded'}
    (BACKUP / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Backup image checksums and all GPT checks passed. No restore has been attempted.')


if __name__ == '__main__':
    main()
