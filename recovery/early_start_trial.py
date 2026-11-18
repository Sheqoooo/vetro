#!/usr/bin/env python3
"""Prepare/apply/remove a bounded, owner-user startup trial; no vendor units/remounts.

Default action is plan, without network. Apply/remove require separate owner approval.
"""
import argparse
import base64
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
UNIT = (HERE / "early-start/vetro-early-start-trial.service").read_bytes()
SCRIPT = (HERE / "early-start/start.sh").read_bytes()
MARKER = b"vetro-early-start-trial-v1\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build(action, prefix=""):
    # prefix is used only by filesystem tests, never accepted from command-line input.
    q = shlex.quote
    config = prefix + "/home/owner/.config"
    systemd = config + "/systemd"
    user = systemd + "/user"
    wants = user + "/default.target.wants"
    base = prefix + "/home/owner/share/vetro-early-start-trial"
    unit = user + "/vetro-early-start-trial.service"
    link = wants + "/vetro-early-start-trial.service"
    script = base + "/start.sh"
    marker = base + "/.trial-owned"
    log = base + "/attempt.log"
    contents = [(marker, MARKER), (unit, UNIT), (script, SCRIPT)]
    lines = ["set -eu", "umask 077"]
    if action == "apply":
        lines += ["[ -d %s ] && [ ! -L %s ] || exit 20" % (q(config), q(config)),
                  "[ -d %s ] && [ ! -L %s ] || exit 20" % (q(prefix + "/home/owner/share"), q(prefix + "/home/owner/share"))]
        for target in (systemd, base):
            lines.append("[ ! -e %s ] && [ ! -L %s ] || exit 21" % (q(target), q(target)))
        for directory in (base, systemd, user, wants):
            lines.append("mkdir -m 700 %s" % q(directory))
        for target, data in contents:
            lines.append("printf '%%s' %s | base64 -d > %s" % (q(base64.b64encode(data).decode()), q(target)))
        lines += ["chmod 700 %s" % q(script), "chmod 600 %s %s" % (q(unit), q(marker)),
                  "ln -s ../vetro-early-start-trial.service %s" % q(link)]
        if not prefix:
            lines.append("chown owner:users " + " ".join(q(p) for p in (base, systemd, user, wants, marker, unit, script)))
        lines.append("echo EARLY_START_TRIAL_INSTALLED_NOT_STARTED")
    elif action == "remove":
        lines += ["[ -d %s ] && [ ! -L %s ] || exit 20" % (q(base), q(base)),
                  "[ -f %s ] && [ ! -L %s ] || exit 20" % (q(marker), q(marker))]
        for directory in (systemd, user, wants):
            lines.append("if [ -e %s ] || [ -L %s ]; then [ -d %s ] && [ ! -L %s ] || exit 26; fi" %
                         (q(directory), q(directory), q(directory), q(directory)))
        # Verify all remaining owned files before deleting any. Changed files stop removal.
        for target, data in contents:
            lines.append("if [ -e %s ] || [ -L %s ]; then [ -f %s ] && [ ! -L %s ] || exit 22; [ \"$(sha256sum %s | cut -d' ' -f1)\" = %s ] || exit 23; fi" %
                         (q(target), q(target), q(target), q(target), q(target), q(digest(data))))
        lines.append("if [ -e %s ] || [ -L %s ]; then [ -L %s ] || exit 24; [ \"$(readlink %s)\" = ../vetro-early-start-trial.service ] || exit 24; fi" % (q(link), q(link), q(link), q(link)))
        lines.append("if [ -e %s ] || [ -L %s ]; then [ -f %s ] && [ ! -L %s ] || exit 25; fi" % (q(log), q(log), q(log), q(log)))
        # No recursive deletion, no service stop, no broad staging cleanup.
        lines.append("rm -f " + " ".join(q(p) for p in (marker, link, unit, script, log)))
        for directory in (wants, user, systemd, base):
            lines.append("rmdir %s 2>/dev/null || true" % q(directory))
        lines.append("echo EARLY_START_TRIAL_FILES_REMOVED")
    else:
        raise ValueError("Unknown action")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["plan", "apply", "remove"], nargs="?", default="plan")
    parser.add_argument("--tv")
    parser.add_argument("--owner-approved", action="store_true")
    args = parser.parse_args()
    if args.action == "plan":
        print(json.dumps({"scope": "TV owner-user startup trial", "systemPartitionChanged": False,
                          "newSystemRootService": False, "currentSessionLaunched": False,
                          "newPaths": ["/home/owner/.config/systemd", "/home/owner/share/vetro-early-start-trial"],
                          "launchesOnly": "vetrotvapp.svc", "hardwareValidated": False,
                          "originalVetroOnbootLeftEnabled": True}, indent=2))
        return
    if not args.owner_approved or not args.tv:
        parser.error("An explicit owner-approved action and one TV address are required")
    if ipaddress.ip_address(args.tv).version != 4:
        parser.error("One approved TV IPv4 required")
    private = HERE.parents[1] / "recovery/private/startup-analysis"
    private.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory = Path(tempfile.mkdtemp(prefix="early-start-%s-" % args.action, dir=private))
    os.umask(0o077)
    command = build(args.action)
    (directory / "submitted.sh").write_text(command)
    result = subprocess.run(["/usr/bin/curl", "--noproxy", "", "--silent", "--show-error", "--fail",
                             "--connect-timeout", "3", "--max-time", "35", "-H", "Content-Type: application/json",
                             "--data-binary", "@-", "http://%s:8099/exec" % args.tv],
                            input=json.dumps({"cmd": command}), capture_output=True, text=True, timeout=38)
    (directory / "response.txt").write_text(result.stdout)
    if result.returncode:
        raise SystemExit("Request failed; preserve partial state and inspect before retrying")
    response = json.loads(result.stdout)
    if not response.get("ok") or response.get("timed_out"):
        raise SystemExit("Action incomplete; preserve private journal and do not retry blindly")
    print(json.dumps({"action": args.action, "completed": True, "rebootRequested": False,
                      "currentAppStartedOrStopped": False}))


if __name__ == "__main__":
    main()
