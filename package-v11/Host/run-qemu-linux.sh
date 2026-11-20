#!/bin/sh
# Starts an AROS x86_64 disk image with its usual VGA card and a second
# VirtIO-GPU adapter with VirGL. Needs QEMU built with virglrenderer and an
# OpenGL display, and KVM.
# usage: run-qemu-linux.sh <disk image>
DISK=${1:?usage: run-qemu-linux.sh <disk image>}
exec qemu-system-x86_64 -enable-kvm -machine pc -cpu host -smp 2 -m 2048 \
    -drive file="$DISK",if=ide,index=0,media=disk \
    -vga std -device virtio-gpu-gl-pci \
    -display "${AROS_QEMU_DISPLAY:-gtk,gl=on}" \
    -netdev user,id=net0 -device rtl8139,netdev=net0 \
    -usb -device usb-tablet -rtc base=localtime
