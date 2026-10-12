#!/bin/bash
set -euo pipefail
mountpoint -q /sys/kernel/config || mount -t configfs configfs /sys/kernel/config
g=/sys/kernel/config/usb_gadget/omarchy
if [[ ! -d "$g" ]]; then
    mkdir -p "$g"
    echo 0x1d6b > "$g/idVendor"
    echo 0x0104 > "$g/idProduct"
    echo 0x0200 > "$g/bcdUSB"
    mkdir -p "$g/strings/0x409" "$g/configs/c.1/strings/0x409"
    echo omarchy-odin2portal > "$g/strings/0x409/serialnumber"
    echo Omarchy > "$g/strings/0x409/manufacturer"
    echo 'Odin2 Portal native Omarchy' > "$g/strings/0x409/product"
    echo 'USB Ethernet' > "$g/configs/c.1/strings/0x409/configuration"
    echo 250 > "$g/configs/c.1/MaxPower"
    mkdir -p "$g/functions/ecm.usb0"
    echo 02:00:00:77:00:02 > "$g/functions/ecm.usb0/dev_addr"
    echo 02:00:00:77:00:01 > "$g/functions/ecm.usb0/host_addr"
    ln -s "$g/functions/ecm.usb0" "$g/configs/c.1/ecm.usb0"
fi
for attempt in {1..60}; do
    controller=$(ls /sys/class/udc | head -n 1)
    if [[ -n "$controller" ]]; then
        [[ -n $(cat "$g/UDC") ]] || echo "$controller" > "$g/UDC"
        ip link set usb0 up
        ip addr replace 192.168.77.2/30 dev usb0
        exit 0
    fi
    sleep 1
done
echo 'No USB device controller appeared' >&2
exit 1
