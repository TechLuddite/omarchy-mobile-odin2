#!/bin/sh
echo 'Content-Type: text/plain'
echo
echo 'Omarchy Odin2 Portal native bootstrap'
uname -a
echo
cat /proc/cmdline
echo
cat /proc/partitions
echo
cat /run/bootstrap.log
echo
cat /run/sshd.log 2>/dev/null
echo
dmesg | tail -100
