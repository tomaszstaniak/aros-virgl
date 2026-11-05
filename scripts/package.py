#!/usr/bin/env python3
"""Assemble the AROS release ZIP from a matching build."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "VirGL-0.1.0-exp1-aros-x86_64-abiv1-pc"
LIBRARIES = ("stdc.library", "stdcio.library", "posixc.library", "fd.library",
             "gallium.library", "mesa3dgl26-2.library", "softpipe.hidd", "virgl.hidd")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aros", required=True, type=Path)
    parser.add_argument("--source", type=Path, default=ROOT / "work/aros")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    upstreams = json.loads((ROOT / "upstreams.json").read_text())
    with tempfile.TemporaryDirectory() as scratch:
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(Path(scratch) / "index")
        git = ["git", "-C", str(args.source.resolve())]
        subprocess.run([*git, "read-tree", "HEAD"], env=env, check=True)
        subprocess.run([*git, "add", "-A"], env=env, check=True)
        tree = subprocess.check_output([*git, "write-tree"], env=env, text=True).strip()
        if tree != upstreams["aros"]["result_tree"]:
            raise SystemExit("The source tree does not match upstreams.json")
        package = Path(scratch) / "VirGL"
        shutil.copytree(ROOT / "package", package)
        for directory in ("Libs", "Examples", "Source"):
            (package / directory).mkdir()
        for name in LIBRARIES:
            source = args.aros / ("Devs/Drivers" if name.endswith(".hidd") else "Libs") / name
            data = source.read_bytes()
            if data[:6] != b"\x7fELF\x02\x01" or int.from_bytes(data[18:20], "little") != 62:
                raise SystemExit("Not an x86_64 ELF binary: " + str(source))
            shutil.copy2(source, package / "Libs" / name)
        for name in ("glsimplerendering", "glclear"):
            shutil.copy2(args.aros / "Developer/Debug/Tests/graphics/gl" / name,
                         package / "Examples" / name)
        shutil.copy2(args.aros / "Developer/Debug/Tests/hidds/gfx/virglglprobe",
                     package / "Examples/virgl-check")
        shutil.copytree(ROOT / "host", package / "Host",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        host_doc = (ROOT / "docs/build-host.md").read_text().replace("host/", "Host/")
        (package / "Host/README.txt").write_text(host_doc)
        shutil.copytree(ROOT / "patches/aros", package / "Source/patches/aros")
        shutil.copytree(ROOT / "licenses", package / "Source/licenses")
        (package / "Source/upstreams.json").write_text(json.dumps(upstreams, indent=2) + "\n")
        (package / "Source/README.txt").write_text(
            "AROS source patches and licenses\n\n"
            "Apply patches/aros/series to the AROS base in upstreams.json.\n"
            "Build instructions: https://github.com/tomaszstaniak/aros-virgl/blob/main/docs/build-guest.md\n"
        )
        files = {str(p.relative_to(package)): sha(p) for p in sorted(package.rglob("*")) if p.is_file()}
        manifest = {"package": NAME, "status": "experimental", "guest": "x86_64 ABIv1 nightly 2026-10-31",
                    "source_base": upstreams["aros"]["base_commit"], "source_tree": tree,
                    "compiler": "Clang 23.1.0", "mesa": "26.2.5",
                    "host_source": upstreams["qemu"]["base_commit"], "files": files}
        (package / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        files["manifest.json"] = sha(package / "manifest.json")
        (package / "SHA256SUMS").write_text("".join(f"{v}  {n}\n" for n, v in sorted(files.items())))
        args.output.mkdir(parents=True, exist_ok=True)
        archive = args.output / (NAME + ".zip")
        if archive.exists():
            raise SystemExit("Output already exists: " + str(archive))
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as output:
            for path in sorted(package.rglob("*")):
                if path.is_file():
                    output.write(path, "VirGL/" + str(path.relative_to(package)))
        with zipfile.ZipFile(archive) as check:
            if check.testzip() is not None:
                raise SystemExit("ZIP integrity check failed")
        digest = sha(archive)
        archive.with_suffix(".zip.sha256").write_text(digest + "  " + archive.name + "\n")
        print(digest + "  " + str(archive))


if __name__ == "__main__":
    main()
