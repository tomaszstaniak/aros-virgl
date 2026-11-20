VirGL for AROS x86_64 ABIv11, internal test package 0.2.0-test1
===============================================================

Not a public release. For checking OpenGL through VirGL in an ABIv11 system
that runs inside a QEMU/KVM virtual machine. It does nothing on real
graphics hardware.

What it does
------------
- virgl.hidd is an OpenGL renderer that sends drawing commands to the host
  GPU through a second, VirtIO-GPU adapter. It is built from the VirGL
  driver of Mesa 20.0.8, the same Mesa the system's mesa3dgl.library has.
  Mesa itself is not replaced.
- gallium.library is replaced by a build that prefers virgl.hidd when that
  adapter is present and otherwise uses the software renderer as before.
- The desktop stays on the usual display card (VGA/VESA). Finished frames
  are read back from the host and copied into the window.

Requirements
------------
Guest: an x86_64 ABIv11 system with Mesa 20.0.8 (mesa3dgl.library 21.5).
Built from deadwood2/AROS master of 2026-11 (commit 5376f09b), tested on
the ABIv11 2026.09 release.

Host: QEMU with virglrenderer and an OpenGL display (gtk,gl=on or
sdl,gl=on), a working host OpenGL driver, KVM. Keep the display card the
system already uses and add one adapter:

    -vga std -device virtio-gpu-gl-pci

Host/run-qemu-linux.sh holds a complete command line. It has not been run
on a Linux host yet; the package was tested with QEMU on macOS (software
CPU emulation).

Files
-----
Libs/gallium.library            replaces the system file
Devs/Drivers/virgl.hidd         new
Tools/glcheck                   test program
Install, Rollback               AROS Shell scripts
Host/run-qemu-linux.sh          QEMU command line for a Linux host

No boot loader change is needed.

Installation
------------
1. Copy this drawer to the AROS disk, open a Shell and CD into it.
2. Execute Install
   The replaced file is first copied to SYS:VirGL-rollback-0.2.0-test1.
3. Shut down and start QEMU with the second adapter.

Checks
------
    Tools/glcheck virgl

prints GL_RENDERER (expected "virgl"), checks a clear, a triangle and a
texture by reading pixels back, draws 60 frames and prints the time per
frame, then PASS or FAIL. Without the second adapter "Tools/glcheck
softpipe" checks the software renderer the same way.

Then start any OpenGL program.

Removal
-------
    Execute Rollback

restores gallium.library and removes virgl.hidd. Close OpenGL programs
first and cold reboot afterwards.

Known limits
------------
- OpenGL 2.1 is what this Mesa's VirGL driver reports here.
- Each frame is read back from the host and copied into the window, and
  every command waits for the host. Measured under software CPU emulation:
  about 100 ms per frame for a 256x256 window, slower than the software
  renderer for a trivial scene there. Speed under KVM is not measured yet.
- One VirtIO-GPU adapter, and it must be the second card, not the one the
  desktop runs on.

Source
------
Patch against deadwood2/AROS in github.com/tomaszstaniak/aros-virgl,
patches/aros-v11 (not pushed yet). Build targets: hidd-virgl,
workbench-libs-gallium. AROS parts are under the AROS Public License; the
driver core is Mesa 20.0.8 (MIT).
