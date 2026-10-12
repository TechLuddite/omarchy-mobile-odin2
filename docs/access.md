# Account setup and maintenance

The native desktop user is `techluddite`, with ordinary password-protected wheel
sudo. The builder initially used a generated setup password. On October 12,
the user requested a specific temporary replacement until better device input
is available. It was applied to `techluddite` through root Wi-Fi maintenance and
verified against the resulting account hash. The ignored local
`private/native-user-password` file now reflects that requested temporary
password. No password or account hash belongs in Git or public notes. The user
plans to replace it directly on the Odin later; that later change has not occurred.

For the later change, open a visible terminal on the user's Wayland session and
run `passwd techluddite` as root over the authorized maintenance connection.
This lets the user enter the new password twice with the OSK, without needing
the old password. Do not capture the password window, ask for the password in
chat, or save the new password on the host. The builder's initial-password file
ceases to describe the live account after that later on-device change. SSH remains
key-only; changing the desktop password does not enable SSH password login.

The initial bring-up used `native/usb-maintenance-ssh.conf` to permit root key login only
for source `192.168.77.1` and local endpoint `192.168.77.2`. The existing private
bootstrap client key is used; no password-based root login was enabled.
The global configuration keeps root prohibited outside that match and disables
password and keyboard-interactive SSH. Root's password remains locked.

Verified with `sshd -t`, an actual USB root key connection, and `sshd -T -C`:
the matching USB addresses yield `PermitRootLogin prohibit-password` and
`PasswordAuthentication no`; a different source yields `PermitRootLogin no`.
That initial USB-only rule has now been replaced by the requested persistent
Wi-Fi maintenance setup below. The source fragment remains as a record of the
earlier configuration, not an additional live rule.

## Persistent passwordless Wi-Fi maintenance

At the user's request, OpenSSH permits full root maintenance with the existing
project Ed25519 client key over reachable network connections, including Wi-Fi.
`native/maintenance-ssh.conf` replaces the USB-address-only rule. For root it
requires public-key authentication and uses only
`/root/.ssh/authorized_keys_maintenance`; systemd's additional authorized-key
command is disabled for that match. SSH password and keyboard-interactive
authentication remain disabled. Root's password remains locked, and the desktop
user's password and ordinary wheel sudo policy are unchanged.

`native/install-maintenance-ssh.sh CLIENT_PUBLIC_KEY` installs the reviewed
configuration on the ARM64 Portal. It validates the model and public key, saves
the existing SSH/Avahi configuration privately under
`/root/native-transition/ssh-maintenance-TIMESTAMP/`, checks `sshd -t` before
reloading, and enables sshd and Avahi for future boots. This is a separate
post-install setup; the base filesystem builder still uses its initial policy.

Avahi advertises `odin2portal.local` only on `wlp1s0`, preventing name resolution
from selecting the USB gadget address after disconnection. The current Wi-Fi
profile already has NetworkManager autoconnect enabled. The hostname follows
DHCP address changes on a local network that supports mDNS; this setup does not
create an Internet tunnel or configure a router port forward.

The host has two aliases, recorded in `native/maintenance-ssh-client.conf`:

```bash
ssh odin2       # desktop user: techluddite
ssh odin2-root  # root: full maintenance, no sudo/password prompt
```

The host's private client key is mode 0600 at `~/.ssh/odin2-omarchy`; trusted
device host keys are pinned in `~/.ssh/odin2-known_hosts`. These files remain
outside the public repo. The Wi-Fi/hostname host key was obtained through the
already trusted USB connection before the first Wi-Fi test. Client aliases use
strict host-key checking, key-only noninteractive login and keepalive probes.

Verified on October 12: both aliases authenticate without passwords; root
returns UID 0, the user returns UID 1000, and route inspection confirms the
connections use `wlp1s0`. The Wi-Fi hostname resolves to the Wi-Fi IPv4 address.
Root SFTP upload, download and removal pass with byte-for-byte readback; the
temporary probe file was removed.
sshd and Avahi are enabled/active, `sshd -t` passes, and effective root settings
require public keys with both password methods disabled. Both aliases also
passed fresh connections while the USB gadget was unbound in software, with
readback confirming the gadget remained disconnected throughout each test.
The gadget was restored over Wi-Fi afterward, with an automatic timed fallback.
Physical cable removal remains a separate optional check; boot persistence is
configured but has not been tested by another reboot.

Firefox `157.0.1-1` is installed from the native ARM repository and confirmed
with `pacman -Q firefox`. The running kernel lacks the filesystem download
sandbox support expected by current pacman; installation used the per-command
`--disable-sandbox-filesystem` flag. The live pacman configuration was not
globally changed for this installation.
