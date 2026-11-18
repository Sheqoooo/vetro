#!/usr/bin/env python3
"""Archive existing JSON exports locally; no networking or TV commands.

This is an integrity-checked configuration archive, NOT a firmware backup or
an automatic TV restore tool. Run with Python 3.8+; no dependencies required.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
NAMES = ("device.json", "status.json", "dock.json", "remap.json", "input.json", "startup.json")
LIMIT = 2 * 1024 * 1024


def contained(path):
    path = Path(path)
    # Refuse symlinks even when they point back inside this directory.
    absolute = path.absolute()
    try:
        parts = absolute.relative_to(ROOT).parts
    except ValueError:
        raise ValueError("Path must be inside the recovery directory")
    current = ROOT
    for part in parts:
        if part in (".", ".."):
            raise ValueError("Path traversal is not allowed")
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlinks are not allowed")
    if os.path.commonpath((str(ROOT), str(absolute.resolve()))) != str(ROOT):
        raise ValueError("Path escapes the recovery directory")
    return absolute


def read_json(path):
    path = contained(path)
    if not path.is_file() or path.stat().st_size > LIMIT:
        raise ValueError("Missing file or file exceeds 2 MiB: " + path.name)
    data = path.read_bytes()
    obj = json.loads(data)
    if not isinstance(obj, dict) or not obj or "error" in obj:
        raise ValueError("Expected a non-empty JSON object without a top-level error: " + path.name)
    return data, obj


def private_write(path, data):
    path = contained(path)
    # Exclusive creation: never overwrite an existing backup.
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def capture():
    source = contained(ROOT / "inbox")
    files = {}
    # Validate ALL exports before creating any snapshot.
    for name in NAMES:
        files[name] = read_json(source / name)[0]
    device = json.loads(files["device.json"])
    for key in ("model", "firmware", "source_revision", "stage"):
        if not isinstance(device.get(key), str) or not device[key].strip():
            raise ValueError("device.json needs a non-empty " + key)
    if device["stage"] != "after-install-before-user-changes":
        raise ValueError("Exports must be marked after-install-before-user-changes")
    private = contained(ROOT / "private")
    private.mkdir(mode=0o700, exist_ok=True)
    if private.stat().st_mode & 0o077:
        raise ValueError("private directory must have permissions 0700")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = contained(private / stamp)
    target.mkdir(mode=0o700)
    records = {}
    for name, data in files.items():
        private_write(target / name, data)
        records[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    manifest = {"schema": 1, "created_utc": stamp, "files": records,
                "scope": "Post-install JSON exports only; no firmware or pre-root backup",
                "tv_restore_tested": False}
    # Written last. An interrupted capture without this file is invalid.
    private_write(target / "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())
    print(str(target.relative_to(ROOT)))
    print("Archive created. No claim of TV recoverability; restore has NOT been tested.")


def verify(directory):
    directory = contained(ROOT / directory)
    if directory.parent != contained(ROOT / "private"):
        raise ValueError("Expected a snapshot directly under private/")
    _, manifest = read_json(directory / "manifest.json")
    if manifest.get("schema") != 1 or set(manifest.get("files", {})) != set(NAMES):
        raise ValueError("Invalid manifest or incomplete export set")
    for name in NAMES:
        data, _ = read_json(directory / name)
        record = manifest["files"][name]
        if record != {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}:
            raise ValueError("Integrity check failed: " + name)
    print("All six exports match their manifest.")
    print("Checksums detect accidental changes, not an attacker replacing files and manifest.")
    print("This does NOT validate API completeness, device identity or a working TV restore.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("capture", help="Archive the six existing inbox/*.json exports")
    check = sub.add_parser("verify", help="Check a local snapshot; no TV access")
    check.add_argument("snapshot", help="Path relative to this script, e.g. private/20260101T...")
    args = parser.parse_args()
    try:
        if args.command == "capture":
            capture()
        else:
            verify(args.snapshot)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
