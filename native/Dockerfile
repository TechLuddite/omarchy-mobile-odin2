FROM --platform=linux/arm64 menci/archlinuxarm@sha256:f7c6f64c0f246f41775e01793340c49f8e9abf3991141c25405361d56b100ccb
RUN sed -i '/^\[options\]/a DisableSandbox' /etc/pacman.conf && \
    printf 'Server = https://ca.us.mirror.archlinuxarm.org/$arch/$repo\n' > /etc/pacman.d/mirrorlist && \
    pacman-key --init && pacman-key --populate archlinuxarm && \
    pacman -Syu --noconfirm arch-install-scripts git patch jq dosfstools e2fsprogs
COPY --chmod=755 native/build-rootfs.sh /usr/local/bin/build-rootfs
COPY plugins /input/plugins
ENTRYPOINT ["/usr/local/bin/build-rootfs"]
