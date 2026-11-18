#!/usr/bin/env python3
"""Start the ORIGINAL installer with offline-only choices and project-local data.

This helper is not a security boundary. Run it with the existing managed file
and network restrictions. It does not support scanning, TV access or installation.
"""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess

EXPECTED = "a4a6557427b6dfd6b00399f24f04f3651e30f955eb21dc90e1826d0f604a914a"
VERSION = "3.1.0"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["version", "help", "cert-status", "install-help"], default="help", nargs="?")
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[2]
    archive = project / "tools/downloads/Apps2Samsung-cli-v3.1.0-osx-arm64.tar.gz"
    binary = project / "tools/apps2samsung/apps2samsung-cli"
    if not archive.is_file() or not binary.is_file():
        parser.error("Installer files missing; use the documented TVBuild/vetro directory layout.")
    if hashlib.sha256(archive.read_bytes()).hexdigest() != EXPECTED:
        parser.error("Downloaded archive checksum differs from the pinned release.")
    # Verify that the executable still matches the original archive, not just its filename.
    import tarfile
    with tarfile.open(archive, "r:gz") as bundle:
        with bundle.extractfile("./apps2samsung-cli") as original:
            expected_binary = hashlib.sha256(original.read()).digest()
    if hashlib.sha256(binary.read_bytes()).digest() != expected_binary:
        parser.error("Executable differs from the original release archive.")
    data = project / "recovery/private/apps2samsung"
    temp = project / "recovery/private/tool-tmp"
    for directory in (data, temp):
        directory.mkdir(parents=True, exist_ok=True)
        directory.chmod(0o700)
    # Preserve the real HOME, never substitute it. Private-file protection comes
    # from the managed runtime, not these environment variables.
    env = {key: value for key, value in os.environ.items()
           if key in ("HOME", "LANG", "LC_ALL", "__CF_USER_TEXT_ENCODING")}
    env.update({
        "PATH": "/Library/Developer/CommandLineTools/usr/bin:/usr/bin:/bin",
        "APPS2SAMSUNG_DATA_DIR": str(data),
        "TMPDIR": str(temp),
        "DOTNET_BUNDLE_EXTRACT_BASE_DIR": str(data / "dotnet-bundle"),
        "DOTNET_CLI_HOME": str(data / "dotnet-cli"),
        "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
    })
    commands = {"version": ["--version"], "help": ["--help"],
                "cert-status": ["cert", "--json"], "install-help": ["install", "--help"]}
    result = subprocess.run([str(binary)] + commands[args.action], cwd=str(project), env=env, timeout=30)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
