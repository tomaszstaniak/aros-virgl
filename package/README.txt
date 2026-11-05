VirGL 0.1.0-exp1 for AROS x86_64 ABIv1

OpenGL through Mesa 26.2.5 and a secondary VirtIO GPU. The desktop stays on
standard VGA. This release uses CPU readback for presentation.

Requirements
------------
AROS x86_64 ABIv1, official nightly 2026-10-31, with Core, Extras and Developer
files installed. guest-baseline.json gives the ISO URL and hashes. Use a copy
of the VM disk, 2 GiB RAM and two virtual CPUs.

The macOS ARM64 QEMU build is described in Host/README.txt. Build it once and
keep its complete output directory. Standard Linux QEMU supports VirGL, but
this AROS package has not yet been checked on Linux x86_64. Windows and Intel
macOS configurations are unverified.

Install
-------
1. Back up the disk, close GL applications, and extract into SYS:VirGL.
   Use a directory without spaces. Host/README.txt includes a CD transfer method.
2. Run:
   Execute SYS:VirGL/Install SYS:VirGL
   Execute SYS:VirGL/EnableVirGL
3. Shut AROS down, close QEMU and start it again.

Install backs up all destinations and both Gallium settings under
SYS:VirGL-rollback-0.1.0-exp1 before replacing any library. It refuses an existing
backup directory. If installation fails after BACKUP_COMPLETE was written,
run Rollback; otherwise restore the disk backup.

Install all eight libraries together: stdc.library 0.52, stdcio.library 0.11,
posixc.library 0.41, fd.library 51.0, gallium.library 26.2,
mesa3dgl26-2.library 26.13, softpipe.hidd 26.3 and virgl.hidd 26.9.
The manifest and SHA256SUMS identify the patched binaries; versions alone do not.
Keep the original z1.library and boot gallium.hidd.

EnableVirGL writes virgl to ENV:SYS/Gallium.default and
ENVARC:SYS/Gallium.default. Set the backend before opening GL clients. Keep the
normal boot LIBS: assignment. Do not use Avail FLUSH to reload libraries while
installing or replacing them.

Try it
------
SYS:VirGL/Examples/virgl-check virgl single >RAM:virgl-result.txt
Type RAM:virgl-result.txt

Require GL_RENDERER: virgl, GL_ERROR: 0 and final PASS. The window closes itself.
Examples/glsimplerendering shows a rotating cube; Examples/glclear shows dark red.
Escape or the close button exits those examples.

Restore
-------
Close GL applications, then:
Execute SYS:VirGL/Rollback

Shut down, close QEMU and start it again. Rollback restores original files and
both Gallium settings, removing files that were originally absent. Keep the
backup until the restored system boots. Archive it elsewhere before reinstalling.

Limits
------
This package covers the documented ABIv1 PC configuration. ABIv11, other CPUs,
Venus/Vulkan, Wine and native scanout are outside its scope. OpenSWOS menu and
tactics-editor use does not establish full game support.

After a rejected command or transfer, close and reopen the GL client. Uncertain
device completion can affect peers too; restart the guest after a transport
failure. Reset with live GL clients is unverified.

Shutdown reaches AROS's manual-poweroff screen. Close QEMU afterward.

Source and reports
------------------
Source patches, licenses and host build files are included.
Guest build instructions: https://github.com/tomaszstaniak/aros-virgl/blob/main/docs/build-guest.md
Issues: https://github.com/tomaszstaniak/aros-virgl/issues

Include the release checksum, AROS ABI/nightly, host OS/GPU, QEMU command,
BUILD.json, reproduction steps, virgl-result.txt and a screenshot when relevant.
Say whether close/reopen helps and whether a second client survives. Do not
attach commercial game data.
