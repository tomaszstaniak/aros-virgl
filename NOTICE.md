# Third-party code

AROS source changes apply to the repository and revision in [upstreams.json](upstreams.json). The stdcio change includes upstream PR #2028. AROS licenses and component exceptions are in [licenses/aros](licenses/aros).

Mesa 26.2.5 uses component-specific licenses, including MIT. Its license texts and copyright guide are in [licenses/mesa](licenses/mesa). The AROS build rules fetch its source.

The macOS host archives come from [milesbuckton/homebrew-qemu-virgl](https://github.com/milesbuckton/homebrew-qemu-virgl) at the recorded revisions. Their hashes and source identities are in [host/host-manifest.json](host/host-manifest.json), and their license notices are in [host/licenses](host/licenses). The QEMU recipe fetches its corresponding source and applies the included patches. QEMU's COPYING and COPYING.LIB are included there as well.
