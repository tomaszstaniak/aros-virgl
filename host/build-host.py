#!/usr/bin/env python3
"""Rebuild the pinned experimental macOS VirGL H1 host in a new directory.

No global installation. Keep the complete output directory for runtime use.
This does not provision or launch a VM.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", type=Path,
                        help="Explicit source/download identities; defaults to the bundled pinned manifest")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    out = args.output.absolute()
    out.mkdir(parents=False, exist_ok=False)
    manifest_path = args.manifest or root / "host-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    env = os.environ.copy()
    env["PIP_NO_CACHE_DIR"] = "1"

    with (out / "host-build.log").open("w") as log:
        def run(command, **kwargs):
            return subprocess.run([str(x) for x in command], check=True,
                                  stdout=log, stderr=subprocess.STDOUT, **kwargs)

        for item in manifest["downloads"][:3]:
            archive = out / item["file"]
            cached = root / "downloads" / item["file"]
            if cached.is_file():
                shutil.copy2(cached, archive)
            else:
                urllib.request.urlretrieve(item["url"], archive)
            if hashlib.sha256(archive.read_bytes()).hexdigest() != item["sha256"]:
                raise RuntimeError("Download checksum mismatch: " + archive.name)
            with tarfile.open(archive) as tar:
                tar.extractall(out / "bottles", filter="data")

        prefix = out / "prefix"
        prefix.mkdir()
        for folder in ("libangle/main", "libepoxy-angle/master", "virglrenderer/main"):
            for leaf in ("include", "lib"):
                source = out / "bottles" / folder / leaf
                if source.exists():
                    shutil.copytree(source, prefix / leaf, dirs_exist_ok=True, symlinks=True)
        for pc in (prefix / "lib/pkgconfig").glob("*.pc"):
            text = pc.read_text()
            for folder in ("virglrenderer/main", "libepoxy-angle/master"):
                text = text.replace("@@HOMEBREW_CELLAR@@/" + folder, str(prefix))
            pc.write_text(text)
        for lib in (prefix / "lib").glob("*.dylib"):
            if lib.is_symlink():
                continue
            deps = subprocess.check_output(["otool", "-L", str(lib)], text=True)
            command = ["install_name_tool", "-id", str(lib)]
            for line in deps.splitlines()[1:]:
                dep = line.strip().split(" (")[0]
                if "@@HOMEBREW" in dep:
                    command += ["-change", dep, str(prefix / "lib" / Path(dep).name)]
            run(command + [lib])
            run(["codesign", "--force", "--sign", "-", lib])

        def checkout(path, url, revision):
            path.mkdir(exist_ok=True)
            run(["git", "init", path])
            run(["git", "-C", path, "fetch", "--depth", "1", url, revision])
            run(["git", "-C", path, "checkout", "--detach", "FETCH_HEAD"])

        source = out / "source"
        checkout(source, manifest["sources"]["qemu_url"], manifest["sources"]["qemu_revision"])
        for entry in manifest["patches"]:
            patch = root / entry["file"]
            if hashlib.sha256(patch.read_bytes()).hexdigest() != entry["sha256"]:
                raise RuntimeError("Patch checksum mismatch: " + patch.name)
            run(["git", "-C", source, "apply", "--check", patch])
            run(["git", "-C", source, "apply", patch])
        checkout(source / "subprojects/keycodemapdb", "https://gitlab.com/qemu-project/keycodemapdb.git",
                 manifest["sources"]["keycodemapdb_revision"])
        venv = out / "venv"
        run(["python3", "-m", "venv", venv])
        packages = ("meson==1.12.1", "packaging==26.3", "pycotap==1.3.1", "setuptools==84.2.1",
                    "qemu.qmp==0.0.6", "wheel==0.48.0", "pip==26.2.2")
        run([venv / "bin/pip", "install", *packages], env=env)
        recipe = json.loads((root / "host-recipe.json").read_text())
        old = "@HOST@"
        env.update({key: value.replace(old, str(out)) for key, value in recipe["environment"].items()})
        env["PATH"] = str(venv / "bin") + ":" + env["PATH"]
        build = out / "build"
        build.mkdir()
        command = [value.replace(old, str(out)) for value in recipe["command"]]
        run(command, cwd=build, env=env)
        run(["ninja", "-j4", "qemu-system-x86_64"], cwd=build, env=env)
        binary = build / "qemu-system-x86_64"
        (out / "BUILD.json").write_text(json.dumps({
            "sources": manifest["sources"], "patches": manifest["patches"],
            "downloads": manifest["downloads"], "configure": command,
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "build_exit": 0, "scope": "macOS ARM64 host with Cocoa/ANGLE and VirGL"
        }, indent=2) + "\n")
    print("HOST_BUILD_RC=0", out)


if __name__ == "__main__":
    main()
