# Build and run the QEMU host

The macOS ARM64 host uses QEMU `b33a6bab8b945745810b07c98826aba1ce018873`, ANGLE, epoxy and virglrenderer. The included patches attach a GL context to the secondary GPU and backport asynchronous VirtIO reset. Source revisions and archive hashes are in [host-manifest.json](../host/host-manifest.json).

This configuration was used on macOS 27.2, Apple M5 Pro, with Apple Clang 21.0.0. Other host configurations need their own checks.

## Build once

Install Apple's command-line tools and Homebrew under `/opt/homebrew`, then:

```sh
brew install dtc glib libslirp ninja pixman pkgconf python
python3 host/build-host.py --output "$HOME/virgl-h1"
```

Use a new output directory without spaces. The build needs several GB and network access. The dependency versions used were dtc 1.8.1, glib 2.90.1, libslirp 4.9.7, ninja 1.13.2, pixman 0.46.4, pkgconf 3.0.10 and Python 3.15.2. Different versions can change the result.

The script verifies the bundled ARM64 dependency archives, relocates and signs their libraries, fetches the pinned QEMU and keymap sources, applies both patches, installs the pinned Python build dependencies in a local environment, and builds `qemu-system-x86_64`. It writes `BUILD.json` and `host-build.log` in the output directory. It does not replace a system QEMU installation.

Keep the complete output at its original path. The executable needs `prefix/lib` and `source/pc-bios`; library paths are embedded during the build. You do not rebuild it when starting another AROS session.

## Start AROS

Use a copy of your installed AROS disk. From this repository:

```sh
sh host/run-qemu "$HOME/virgl-h1" \
    -name aros-virgl \
    -machine pc,accel=tcg -cpu qemu64 -smp 2 -m 2048 \
    -drive file=/absolute/path/aros-copy.qcow2,format=qcow2,if=ide,index=0 \
    -vga std -global VGA.vgamem_mb=64 -device virtio-gpu-gl-pci \
    -display cocoa,gl=es \
    -netdev user,id=net0 -device e1000,netdev=net0 \
    -usb -device usb-tablet -rtc base=localtime -boot c \
    -audiodev wav,id=snd0,path=audio.wav -device AC97,audiodev=snd0 \
    -serial file:serial.log
```

`run-qemu` also works from the release ZIP as `Host/run-qemu`. Set `DYLD_LIBRARY_PATH` and the BIOS directory through that wrapper rather than copying only the QEMU executable. The audio device writes a WAV file; it does not play host audio. Audio-input warnings can appear.

After AROS reaches the manual-poweroff screen, close QEMU. Stop the VM before replacing its disk or restoring a snapshot. Quiescent restart/reset works in this configuration; reset with active GL clients is unverified.

## Transfer the package by CD

Extract the release ZIP on macOS and put its `VirGL` directory inside a staging directory:

```sh
hdiutil makehybrid -iso -joliet -default-volume-name VIRGLPKG \
    -o /absolute/path/VirGL.iso /absolute/path/staging
```

Add this to the launch command:

```text
-drive file=/absolute/path/VirGL.iso,format=raw,if=ide,index=2,media=cdrom,readonly=on
```

In the AROS Shell:

```text
Copy VIRGLPKG:VirGL SYS:VirGL ALL
Execute SYS:VirGL/Install SYS:VirGL
Execute SYS:VirGL/EnableVirGL
```

Use the volume name shown by AROS if it differs. Shut down, close QEMU and start it again before using GL.

## Other hosts

Standard Linux QEMU can provide VirGL when its package includes `virglrenderer` and an OpenGL display backend, such as GTK with GL enabled. This release has not been checked on Linux x86_64, Windows or Intel macOS. The bundled dependency archives are macOS ARM64 binaries.

QEMU's [VirtIO GPU documentation](https://www.qemu.org/docs/master/system/devices/virtio/virtio-gpu.html) describes the standard VirGL backend. The AROS guest remains x86_64 regardless of the host CPU.
