VirGL for AROS mainline x86_64, internal test package 0.2.0-test1
=================================================================

Not a public release. For checking how AROS behaves on a VirtIO-GPU adapter
with VirGL inside a QEMU/KVM virtual machine. It does nothing on real
graphics hardware.

What it does
------------
- virtiogfx.hidd drives the desktop on QEMU's VirtIO-GPU adapter.
- OpenGL programs (gl.library, Mesa 26.2.7) render on the host GPU through
  VirGL. No per-program setting is needed: on the VirtIO-GPU screen Mesa
  picks VirGL, on other screens it keeps using the software renderer.

Requirements
------------
Guest: AROS mainline x86_64 (ABIv1) close to master of 2026-11-19 (commit
b6dcaeea). Tested on a nightly system of 2026-11-13. Three system libraries
are replaced, so a much older or newer system may not match.

Host: QEMU with virglrenderer and an OpenGL display (gtk,gl=on or
sdl,gl=on), a working host OpenGL driver, KVM. The guest needs exactly this
adapter setup:

    -vga none -device virtio-vga-gl,xres=1280,yres=720

Host/run-qemu-linux.sh holds a complete command line. It has not been run
on a Linux host yet; the package was tested with QEMU on macOS (software
CPU emulation).

Files
-----
Libs/gallium.library            replaces the system file
Libs/gl.library                 replaces the system file
Libs/mesa3dgl26-2.library       replaces the system file
Devs/Drivers/gallium.hidd       replaces the system file
Devs/Drivers/virgl.hidd         new
Devs/Drivers/virtiogfx.hidd     new
Tools/virglglprobe              test program
Install, Rollback               AROS Shell scripts
grub-entry.txt                  the boot loader line
Host/run-qemu-linux.sh          QEMU command line for a Linux host

Installation
------------
1. Copy this drawer to the AROS disk, open a Shell and CD into it.
2. Execute Install
   The replaced files are first copied to SYS:VirGL-rollback-0.2.0-test1.
   The originals stay there after Rollback, so the package can be installed
   and removed repeatedly.
3. Add the line from grub-entry.txt to boot/grub/grub.cfg. The driver has
   to be loaded by the boot loader; it does not work from Devs/Monitors.
4. Shut down, start QEMU with the VirtIO-GPU adapter, pick the entry with
   the added line.

Checks
------
    Tools/virglglprobe virgl

prints GL_RENDERER (expected to contain "virgl") and PASS or FAIL for clear,
triangle, texture, blend, depth and stencil tests. On a boot without the
VirtIO-GPU adapter "Tools/virglglprobe softpipe" checks the software
renderer the same way.

Then start any OpenGL program, for example LibreSprite with
GUI_RENDERER=GPU.

Removal
-------
    Execute Rollback

restores the saved files and removes the two new drivers. Remove the
virtiogfx.hidd line from grub.cfg as well: an entry that names a missing
module does not boot.

Known limits
------------
- Each frame of an OpenGL window is read back from the host and copied to
  the screen by the guest, so OpenGL windows are slower than the host GPU
  allows. Full-screen scan-out without the copy is not done yet.
- The mouse pointer is drawn by the guest.
- One screen resolution, set on the QEMU command line (xres, yres).
- The driver must be the only display adapter (-vga none).

Source
------
github.com/tomaszstaniak/AROS, branch virgl-mainline (commit e398066e).
Display driver base and gl.library drawable additions by John Knipper;
VirGL client, Mesa glue and tests continue github.com/tomaszstaniak/aros-virgl.
AROS parts are under the AROS Public License, Mesa under its own licences
(see the mainline tree).
