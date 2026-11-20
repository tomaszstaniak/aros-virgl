#!/bin/sh
# Starts an AROS x86_64 disk image with one VirtIO-GPU adapter and VirGL.
# Needs QEMU built with virglrenderer and OpenGL display support, and KVM.
# usage: run-qemu-linux.sh <disk image> [width height]
DISK=${1:?usage: run-qemu-linux.sh <disk image> [width height]}
W=${2:-1280}
H=${3:-720}
exec qemu-system-x86_64 -enable-kvm -machine pc -cpu host -smp 2 -m 2048 \
    -drive file="$DISK",if=ide,index=0,media=disk \
    -vga none -device virtio-vga-gl,xres="$W",yres="$H" \
    -display "${AROS_QEMU_DISPLAY:-gtk,gl=on}" \
    -netdev user,id=net0 -device rtl8139,netdev=net0 \
    -usb -device usb-tablet -rtc base=localtime \
    -serial file:serial.log
