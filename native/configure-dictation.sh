#!/bin/bash
# Run as the desktop user after installing the verified ARM64 Voxtype binary.
# Omarchy: David Heinemeier Hansson and contributors; Voxtype: Peter Jackson.
set -euo pipefail
if (( EUID == 0 )); then
    echo 'Run this configuration step as the desktop user.' >&2
    exit 1
fi
export OMARCHY_PATH=${OMARCHY_PATH:-/usr/share/omarchy}
config_dir=${XDG_CONFIG_HOME:-$HOME/.config}/voxtype
install -d "$config_dir"
if [[ ! -f "$config_dir/config.toml" ]]; then
    install -m600 "$OMARCHY_PATH/default/voxtype/config.toml" "$config_dir/config.toml"
fi
cp -p "$config_dir/config.toml" "$config_dir/config.toml.before-portal-$(date -u +%Y%m%dT%H%M%S%N)"
# Let the compositor and mapper handle controls, preserving normal Omarchy keys.
voxtype config set hotkey.enabled false
# Visible feedback; completed transcripts stay in the focused application.
voxtype config set output.notification.on_recording_start true
voxtype config set output.notification.on_recording_stop true
voxtype config set output.notification.on_transcription false
voxtype setup --download --no-post-install
voxtype setup systemd
systemctl --user restart voxtype.service
echo 'Dictation configured. A real microphone speech test is still required.'
