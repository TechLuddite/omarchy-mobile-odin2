#!/usr/bin/env python3
"""Keep Omarchy's Color singleton visible under Qt 6.12's new QtQuick.Color.

Pinned Omarchy 4.0.3 and omarchy-mobile use qs.Commons.Color. Restrict only
unversioned QtQuick imports in files using that singleton to the 6.11 API.
See https://doc.qt.io/qt-6.12/qml-qtquick-color.html .
"""
import pathlib
import re
import sys

changed = 0
for directory in sys.argv[1:]:
    for path in pathlib.Path(directory).rglob('*.qml'):
        text = path.read_text()
        if not re.search(r'\bColor\.', text):
            continue
        updated = re.sub(r'^import QtQuick[ \t]*$', 'import QtQuick 6.11', text,
                         flags=re.MULTILINE)
        if text != updated:
            path.write_text(updated)
            changed += 1
print(f'Updated QtQuick imports in {changed} QML files.')
