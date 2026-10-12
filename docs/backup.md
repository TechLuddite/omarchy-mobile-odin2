# Odin base image backup

The backup preserves the device's existing base system and platform data before
the native Omarchy installation. Personal data is not required. Capture is
read-only through the Odin-compatible Qualcomm EDL programmer; loading that
programmer into RAM does not flash it to UFS.

Files live under `private/base-backup/`, outside published source:

- `lun1.img` through `lun5.img`: full raw images of the five smaller UFS LUNs,
  including both boot slots, firmware, calibration/state and their GPTs.
- `lun0-base-prefix.img`: every byte before the `userdata` partition on LUN 0,
  including primary GPT, `persist`, metadata, Android `super` and both system
  vbmeta partitions. This also retains the rawdump region.
- `lun0-tail.img`: bytes after `userdata`, including the actual secondary GPT.
- `storage-map.json`: observed sector size and each LUN's partition offsets,
  sizes and total length.
- `manifest.json`: exact image extents, sizes, SHA256 hashes, programmer hash,
  reader revision, omitted range and capture completion state.
- `verification.json`: created only after checking the image hashes and both
  GPT headers/entry arrays on every LUN against their CRCs and the observed map.
- `independent-reread.json`: matches from separate EDL reads of `abl_a`, `abl_b`
  and `persist` against their corresponding bytes in the captured images.

Completed October 12, 2026: seven image extents total 11.57 GiB. All image
checksums, both GPT copies across six LUNs, 115 partition entries and the three
independent rereads passed. The image set and metadata are packaged as
`private/odin-base-20261012.tar.zst` (approximately 2.7 GiB), with a sibling
SHA256 file. The compressed archive passed its integrity check and contains all
seven images and the capture/verification metadata. A restore has not been tested.

A second copy of the archive and checksum is on the native device under
`/recovery/base/`, replacing the original Android `super` filesystem. Its SHA256
was recalculated on the device and matched the off-device archive. Native KERNEL
and RECOVERY.img are under `/recovery/native/`. The recovery filesystem is mounted
read-only by default. This duplicate does not replace the off-device backup and
does not establish that restoration works.

This is a base-image set, not a complete clone of personal data. The approximately
934 GiB `userdata` payload is explicitly omitted. LUN 0's two files are split
extents: the tail belongs at the offset in the manifest, not immediately after
the prefix. Do not flash a prefix file as though it were the entire device disk.

The host currently has enough space for the approximately 11.6 GiB captured
extents, but not a raw copy of the whole 1 TB device. UFS presents six separate
regions, so one generic PC disk image would not represent the boot hardware.

`python3 scripts/backup-base.py` prints the read plan from the observed map.
`--read` performs the EDL reads without device writes and refuses to overwrite
existing image files. `python3 scripts/verify-base.py` verifies a completed
capture. A failed or interrupted read keeps an `.img.partial` file and does not
mark that region complete. Logs and a successful tool exit alone do not qualify
as a verified backup.

Restoring the images has not been tested. Any later recovery procedure must use
the recorded LUNs/offsets and the same hardware, account for omitted userdata,
and separately handle security state such as RPMB that ordinary LUN reads do not
capture. Keep these device-specific images private.
