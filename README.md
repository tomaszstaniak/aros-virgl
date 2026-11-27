# VirGL for AROS

Experimental OpenGL acceleration for AROS x86_64 ABIv1 under QEMU. The guest uses Mesa 26.2.5 and a secondary VirtIO GPU. Standard VGA displays the desktop; rendered frames are copied back to it.

[Download 0.1.0-exp1](https://github.com/tomaszstaniak/aros-virgl/releases/tag/v0.1.0-exp1) · [Build the guest libraries](docs/build-guest.md) · [Build and run QEMU](docs/build-host.md)

Test packages 0.2.0 revision 7 for mainline x86_64 (nightlies from 2026-11-24) and for ABIv11 distributions: [v0.2.0-r7](https://github.com/tomaszstaniak/aros-virgl/releases/tag/v0.2.0-r7). They replace the 0.1.0 layout described below; each archive has its own README.

## Requirements

- AROS x86_64 ABIv1, official nightly **2026-10-31**, with Core, Extras and Developer files installed. [ISO URL and checksums](package/guest-baseline.json).
- A copy of the system disk, 2 GiB guest RAM and two virtual CPUs.
- QEMU with VirGL and an OpenGL display backend. This release was used with the pinned macOS ARM64 build described in [the host instructions](docs/build-host.md).

The release replaces eight files in `SYS:Libs`: `stdc.library` 0.52, `stdcio.library` 0.11, `posixc.library` 0.41, `fd.library` 51.0, `gallium.library` 26.2, `mesa3dgl26-2.library` 26.13, `softpipe.hidd` 26.3 and `virgl.hidd` 26.9. Install them together. Keep the system's original `z1.library` and boot `gallium.hidd`.

## Install

1. Back up the VM disk and close all GL applications.
2. Extract the release ZIP into `SYS:VirGL`. Use a directory without spaces. You can also extract it on the host and transfer the `VirGL` directory to AROS.
3. In an AROS Shell, run:

   ```text
   Execute SYS:VirGL/Install SYS:VirGL
   Execute SYS:VirGL/EnableVirGL
   ```

4. Shut AROS down, close QEMU and start the VM again.

`Install` saves the original files and Gallium settings under `SYS:VirGL-rollback-0.1.0-exp1` before copying any library. It stops if that backup directory already exists. If installation fails after `BACKUP_COMPLETE` was written, run `Rollback`; otherwise restore your disk backup.

`EnableVirGL` sets `ENV:SYS/Gallium.default` and `ENVARC:SYS/Gallium.default` to `virgl`. Keep the normal boot `LIBS:` assignment. Set the backend before opening GL applications and restart clients after changing it. Do not use `Avail FLUSH` to reload libraries during installation.

## Try it

```text
SYS:VirGL/Examples/virgl-check virgl single >RAM:virgl-result.txt
Type RAM:virgl-result.txt
```

The output should contain `GL_RENDERER: virgl`, `GL_ERROR: 0` and a final `PASS`. The window closes automatically.

`Examples/glsimplerendering` displays a rotating cube. `Examples/glclear` displays a dark red window. Press Escape or close the window to exit.

## Restore the original libraries

Close GL applications, then run:

```text
Execute SYS:VirGL/Rollback
```

Shut down, close QEMU and start it again. The script restores the original files and both Gallium settings, and removes files that were absent before installation. Keep the backup until the restored system has booted. Archive that backup elsewhere before a later reinstallation.

## Host systems

QEMU only needs to be built once. Keep its complete output directory: the executable also needs its libraries and BIOS files.

- **macOS ARM64:** the included recipe builds the host used with this release. It needs Cocoa/ANGLE support and two QEMU patches.
- **Linux x86_64:** standard QEMU supports [VirGL](https://www.qemu.org/docs/master/system/devices/virtio/virtio-gpu.html) when built with `virglrenderer` and an OpenGL display backend. This AROS package has not yet been checked on that host.
- **Windows x86_64 and Intel macOS:** no working configuration is documented here.

`qemu-system-x86_64` names the guest architecture. The macOS ARM64 host runs that executable to emulate an x86_64 AROS machine.

## Limits

This release covers the documented ABIv1 PC configuration. Other architectures and ABIv11 are not supported by this package. Vulkan/Venus, Wine and native display scanout are outside its scope. OpenSWOS was used through its menu and tactics editor and reopened; this is not a full OpenSWOS support claim.

A rejected command or transfer makes the affected GL client unusable; close and reopen it. Uncertain device completion can invalidate other clients too. After a transport failure, restart the guest. Reset with live GL clients is unverified.

In this setup, `Shutdown` reaches AROS's manual-poweroff screen. Close QEMU afterward to finish shutting down. Audio output uses a WAV file in the supplied launch command.

## Report a problem

Open an [issue](https://github.com/tomaszstaniak/aros-virgl/issues) with the release checksum, AROS version/ABI, host OS/GPU, QEMU command and `BUILD.json`, the steps to reproduce, and `virgl-result.txt`. Add a screenshot if the image is wrong. Say whether closing and reopening the application helps, and whether another client keeps working. Do not attach commercial game data.

## Source and licenses

The AROS changes are an [ordered patch series](patches/aros/series) against a pinned upstream revision. They include the already merged [stdcio ownership fix, PR #2028](https://github.com/aros-development-team/AROS/pull/2028). Build instructions and source identities are in [docs/build-guest.md](docs/build-guest.md) and [upstreams.json](upstreams.json).

AROS code uses the [AROS Public License](LICENSE), with component-specific terms listed under [licenses](licenses/). Mesa and the host dependencies retain their own licenses. The QEMU patches are distributed under QEMU's license. No AROS system image or game data is included.
