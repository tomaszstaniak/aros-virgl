# Build the AROS libraries

The source base is `c9459cd9be0d2958765a60fd07324bd161632c9b`. Applying the series gives tree `72d98d081d93298117a7e0dd06bb28623ea823b3`. Use that base rather than current master.

From this repository:

```sh
git clone https://github.com/aros-development-team/AROS.git work/aros
git -C work/aros checkout --detach c9459cd9be0d2958765a60fd07324bd161632c9b
while IFS= read -r patch; do
    git -C work/aros apply "$PWD/patches/aros/$patch"
done < patches/aros/series
```

The release uses **Clang 23.1.0 with the AROS patches**, the x86_64 ABIv1 target, and the nightly build profile. A generic host Clang is not a replacement for the AROS cross compiler. GNU make, GNU sed, gawk, bison, flex, CMake, Ninja, Python and the normal AROS host prerequisites must be available. See the pinned AROS source for its toolchain prerequisites.

Create an out-of-tree build and choose permanent locations for the cross toolchain and downloaded port sources. On macOS, put Homebrew's GNU tools on `PATH` first; the build used `SED=gsed`, `PYTHON=python3`, `CC=clang` and `CXX=clang++`. The `ac_cv_prog_cc_c23=no` and `ac_cv_prog_cc_c11=no` settings avoid a host configure mismatch in this profile.

```sh
mkdir -p build/aros
cd build/aros
env SED=gsed PYTHON=python3 CC=clang CXX=clang++ \
    ac_cv_prog_cc_c23=no ac_cv_prog_cc_c11=no \
    ../../work/aros/configure \
    --target=pc-x86_64 \
    --with-toolchain=llvm \
    --with-llvm-version=23.1.0 \
    --enable-build-type=nightly \
    --with-aros-toolchain-install="$HOME/aros-llvm23" \
    --with-portssources="$HOME/aros-port-sources"
gmake -j4 crosstools
```

`crosstools` builds the configured cross tools if they are not already installed at the selected path. On a host where GNU sed is named `sed`, use `SED=sed` instead. The command above does not install a system image or modify a guest disk.

Build the guest components in order:

```sh
gmake -j4 includes
for target in compiler-stdc compiler-stdcio compiler-posixc workbench-libs-fd \
    workbench-libs-gallium hidd-softpipe mesa3dgl-library hidd-virgl-prototype \
    test-gl test-virgl-gl; do
    gmake -j4 "$target" || exit
done
```

The Mesa port fetches version 26.2.5 through the AROS build rules. Runtime output is under `bin/pc-x86_64/AROS/`: the six `.library` files are in `Libs/`, and the two `.hidd` files are in `Devs/Drivers/`.

The patch also contains native regression sources under `developer/debug/test`. They are development tools and are not run by installing the release.

To assemble a ZIP from this build, return to the repository root:

```sh
python3 scripts/package.py --aros build/aros/bin/pc-x86_64/AROS --output dist
```

The package contains the installer, all eight runtime libraries, the cube/clear examples, the finite GL check, source patches, host recipe and licenses. It leaves `z1.library` and the boot `gallium.hidd` alone. Rebuilding may change binary hashes; the release manifest identifies the shipped binaries.
