VirGL for AROS mainline x86_64, internal test package 0.2.0-test5
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
Tools/glcheck                   short test with time per frame
Tools/glstress                  loads textures, draws, can end without
                                closing OpenGL
Tools/StressLoop                script: glstress ten times, then a report
Install, Rollback               AROS Shell scripts
grub-entry.txt                  the boot loader line
Host/run-qemu-linux.sh          QEMU command line for a Linux host

Installation
------------
1. Copy this drawer to the AROS disk, open a Shell and CD into it.
2. Execute Install
   The replaced files are first copied to SYS:VirGL-rollback-0.2.0-test5.
   The originals stay there after Rollback, so the package can be installed
   and removed repeatedly. Installing over 0.2.0-test1 or test2 is fine:
   Install takes over the system files saved by the earlier package.
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

ENV:VirGL-Status says which renderer the last OpenGL program got:
"virgl", or "softpipe:" followed by the reason VirGL could not be used,
for example "card has no 3D". glcheck prints it too. When VirGL cannot
start, programs get the software renderer instead of no OpenGL at all.
While a program waits more than 3 seconds for the host it says "virgl:
waiting for the host (more than 3 s)", and goes back to "virgl" when the
host has answered.

A program that crashes or quits without closing OpenGL used to leave its
textures and buffers on the host until the guest was restarted. The
driver now releases them within about a second. ENV:VirGL-Released counts
what was released this way (contexts, resources, kilobytes). To try it:

    CD Tools
    Execute StressLoop

It runs a program ten times that ends without closing OpenGL, then
prints VirGL-Released (expected: contexts=10), VirGL-Status and a glcheck
result.

Then start any OpenGL program, for example LibreSprite with
GUI_RENDERER=GPU.

For a slow program, the driver prints the time it spent per kind of work
to the debug output when a program closes OpenGL (the serial log when the
system boots with debug=serial on the GRUB line): lines that begin with
[virgl-stats] (commands, submits, uploads, downloads, frame
readback and copy). Please add them to a report about speed.

When reporting, please send the output of

    GetEnv VirGL-Status
    GetEnv VirGL-Released

after the program you tried, and frames per second if the program shows
them.

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
- Release after a program has ended covers what is on the host. The
  memory Mesa itself allocated inside the guest for that program stays
  until reboot.
- A drawing command may take the host up to 120 seconds, other OpenGL
  commands 30 seconds. If the host takes longer, that program keeps
  running without a picture and VirGL-Status says "virgl: stopped, the
  host did not answer"; programs started meanwhile use the software
  renderer, and VirGL works again once the host has answered. A different
  limit can be set for a test with SetEnv VirGL-Timeout <milliseconds>
  (rounded up to whole seconds).

Changes since 0.2.0-test1
-------------------------
- Much faster: commands are sent without a fence. QEMU answers a fenced
  command only when it polls fences, every 10 ms, so every command cost
  about 10 ms. In our test (no KVM): 4 to 9 ms per frame instead of 73 to
  92, and 64 textures load in 0.06 s instead of 2.6 s.
- What a program leaves behind when it ends without closing OpenGL is
  released on the host.
- The driver waits much longer for a slow host (before: one second), says
  so in ENV:VirGL-Status, and recovers when the host answers late.

Changes in 0.2.0-test5
----------------------
- Software renderer instead of no OpenGL when the card offers VirGL but
  it cannot start (for example the host refuses a context), with the
  reason in ENV:VirGL-Status. A card without 3D gives the reason too.
- ENV:VirGL-Timeout sets the wait for the host, as in the ABIv11 package.
- The mainline and ABIv11 packages now share the version number and
  have the same features (ABIv11 test3 and test4 had no mainline
  counterpart).

Source
------
github.com/tomaszstaniak/AROS, branch virgl-mainline (commit 93d12ba2).
Display driver base and gl.library drawable additions by John Knipper;
VirGL client, Mesa glue and tests continue github.com/tomaszstaniak/aros-virgl.
AROS parts are under the AROS Public License, Mesa under its own licences
(see the mainline tree).
