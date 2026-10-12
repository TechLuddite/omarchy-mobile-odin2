# Account setup and maintenance

The native desktop user is `techluddite`, with ordinary password-protected wheel
sudo. The builder used a generated setup password held in the ignored local
`private/native-user-password` file. No password belongs in Git or public notes.
The user wants to choose a replacement directly on the Odin. This was deferred
when they left to rest; do not assume a replacement has been entered.

For the later change, open a visible terminal on the user's Wayland session and
run `passwd techluddite` as root over the authorized maintenance connection.
This lets the user enter the new password twice with the OSK, without needing
the old password. Do not capture the password window, ask for the password in
chat, or save the new password on the host. The builder's initial-password file
ceases to describe the live account after that change.

During bring-up, `native/usb-maintenance-ssh.conf` permits root key login only
for source `192.168.77.1` and local endpoint `192.168.77.2`. The existing private
bootstrap client key is used; no password-based root login was enabled.
The global configuration keeps root prohibited outside that match and disables
password and keyboard-interactive SSH. Root's password remains locked.

Verified with `sshd -t`, an actual USB root key connection, and `sshd -T -C`:
the matching USB addresses yield `PermitRootLogin prohibit-password` and
`PasswordAuthentication no`; a different source yields `PermitRootLogin no`.
This is bring-up access, separate from the base filesystem builder. Review
its retirement at handover after hardware work.

Firefox `157.0.1-1` is installed from the native ARM repository and confirmed
with `pacman -Q firefox`. The running kernel lacks the filesystem download
sandbox support expected by current pacman; installation used the per-command
`--disable-sandbox-filesystem` flag. The live pacman configuration was not
globally changed for this installation.
