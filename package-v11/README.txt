VirGL for AROS x86_64 ABIv11, internal test package 0.2.0-test3
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
   The replaced file is first copied to SYS:VirGL-rollback-0.2.0-test3.
   Installing over 0.2.0-test1 or test2 is fine: Install takes over the
   system files saved by the earlier package, so Rollback still brings
   back the original ones.
3. Shut down and start QEMU with the second adapter.

Checks
------
    Tools/glcheck virgl

prints GL_RENDERER (expected "virgl"), checks a clear, a triangle and a
texture by reading pixels back, draws 60 frames and prints the time per
frame, then PASS or FAIL. Without the second adapter "Tools/glcheck
softpipe" checks the software renderer the same way.

ENV:VirGL-Status says which renderer the last OpenGL program got:
"virgl", or "softpipe:" followed by the reason VirGL could not be used,
for example "card has no 3D". glcheck prints it too. When VirGL cannot
start, programs now get the software renderer instead of no OpenGL at
all.

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
  every command waits for the host. Measured under software CPU emulation
  for a 256x256 window: about 5 ms per frame (test1: about 100 ms).
- One VirtIO-GPU adapter, and it must be the second card, not the one the
  desktop runs on.

Changes since 0.2.0-test1
-------------------------
- Software renderer instead of "no GL context" when the host cannot run
  VirGL, with the reason in ENV:VirGL-Status (test2).
- Much faster. Commands are sent without a fence: QEMU answers a fenced
  command only when it polls fences, every 10 ms, so every command cost
  about 10 ms. The driver also no longer sleeps a whole timer tick when the
  host takes longer than a very short wait (test2). In our test (no KVM):
  about 5 ms per frame instead of 100, and 64 textures load in 0.2 s
  instead of 9.7 s.

Source
------
Patch against deadwood2/AROS in github.com/tomaszstaniak/aros-virgl,
patches/aros-v11 (not pushed yet). Build targets: hidd-virgl,
workbench-libs-gallium. AROS parts are under the AROS Public License; the
driver core is Mesa 20.0.8 (MIT).
