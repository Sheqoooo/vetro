#!/usr/bin/env python3
"""Install only the repository's locked signing dependencies; no npm/hooks/global files."""
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
from urllib.parse import urlsplit

REVISION = "45b00106149d0c8eff74ead4a979c909dd80efd6"


def archive_files(archive):
    """Return checked regular files below one tar root; reject links and traversal."""
    result = {}
    roots = set()
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        if sum(m.size for m in members) > 50 * 1024 * 1024:
            raise ValueError("Archive expands beyond 50 MiB")
        for member in members:
            p = PurePosixPath(member.name)
            if p.is_absolute() or ".." in p.parts or "\\" in member.name:
                raise ValueError("Unsafe archive path")
            if not (member.isdir() or member.isfile()):
                raise ValueError("Links/special files are not accepted")
            if not p.parts:
                continue
            roots.add(p.parts[0])
            if member.isdir():
                continue
            relative = PurePosixPath(*p.parts[1:])
            if not relative.parts or str(relative) in result:
                raise ValueError("Invalid or duplicate archive file")
            with tar.extractfile(member) as source:
                result[str(relative)] = source.read()
    if len(roots) != 1:
        raise ValueError("Archive must have exactly one top-level directory")
    return result


def main():
    repo = Path(__file__).resolve().parents[1]
    project = repo.parent
    tools = repo / "rooting/on-boot-probe"
    destination = tools / "node_modules"
    if destination.exists():
        raise SystemExit("node_modules already exists; preserve/review it instead of overwriting")
    lock = json.loads((tools / "package-lock.json").read_text())
    tree = json.loads((repo / "recovery/tizen-signer-tree.json").read_text())
    assert tree["sha"] == REVISION and not tree.get("truncated")
    cache = project / "tools/downloads/signing-deps"
    cache.mkdir(parents=True, exist_ok=True)
    staging = project / "tools/signing-deps-staging"
    staging.mkdir(exist_ok=False)
    packages = [(k, v) for k, v in lock["packages"].items() if k]

    def fetch(item):
        location, spec = item
        parts = PurePosixPath(location).parts
        if parts[0] != "node_modules" or ".." in parts or location.count("node_modules") != 1:
            raise ValueError("Only this flat lockfile layout is supported")
        name = "/".join(parts[1:])
        if spec.get("hasInstallScript"):
            raise ValueError("Package declares an install script")
        is_tizen = name == "tizen"
        if is_tizen:
            if spec["resolved"] != "git+ssh://git@github.com/reisxd/tizen.js.git#" + REVISION:
                raise ValueError("Unexpected tizen revision")
            url = "https://codeload.github.com/reisxd/tizen.js/tar.gz/" + REVISION
        else:
            url = spec["resolved"]
            parsed = urlsplit(url)
            if parsed.scheme != "https" or parsed.hostname != "registry.npmjs.org" or parsed.username:
                raise ValueError("Unexpected dependency download origin")
        archive = cache / (name.replace("/", "__") + "-" + spec["version"] + ".tgz")
        if not archive.exists():
            subprocess.run(["/usr/bin/curl", "--noproxy", "", "--fail", "--location",
                            "--proto", "=https", "--proto-redir", "=https", "--silent", "--show-error",
                            "--connect-timeout", "10", "--max-time", "60", "--output", str(archive), url], check=True)
        if not is_tizen:
            algorithm, encoded = spec["integrity"].split("-", 1)
            if algorithm not in ("sha512", "sha256"):
                raise ValueError("Unsupported integrity algorithm")
            if hashlib.new(algorithm, archive.read_bytes()).digest() != base64.b64decode(encoded):
                raise ValueError("Dependency integrity mismatch: " + name)
        files = archive_files(archive)
        if is_tizen:
            expected = {e["path"]: e["sha"] for e in tree["tree"] if e["type"] == "blob"}
            if set(expected) != set(files):
                raise ValueError("Git archive file set mismatch")
            for path, data in files.items():
                blob = b"blob " + str(len(data)).encode() + b"\0" + data
                if hashlib.sha1(blob).hexdigest() != expected[path]:
                    raise ValueError("Git blob mismatch: " + path)
        metadata = json.loads(files["package.json"])
        if metadata["name"] != name or metadata["version"] != spec["version"]:
            raise ValueError("Package identity differs from lockfile")
        target = staging.joinpath(*parts[1:])
        for path, data in files.items():
            out = target / path
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open("xb") as f:
                f.write(data)
        return {"name": name, "version": spec["version"],
                "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "verification": "pinned Git blob hashes" if is_tizen else "lockfile integrity"}

    with ThreadPoolExecutor(max_workers=4) as pool:
        installed = list(pool.map(fetch, packages))
    # No lifecycle scripts, CLI binaries, or downloaded JavaScript were executed.
    shutil.move(str(staging), str(destination))
    receipt = {"lockfile_sha256": hashlib.sha256((tools / "package-lock.json").read_bytes()).hexdigest(),
               "packages": sorted(installed, key=lambda p: p["name"]), "lifecycle_scripts_executed": False}
    (cache / "RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("Installed %d locked packages in the project; no hooks executed" % len(installed))


if __name__ == "__main__":
    main()
