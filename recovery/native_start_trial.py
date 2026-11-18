#!/usr/bin/env python3
"""A local plan by default; install/remove only with explicit owner approval."""
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
NAME = "vetro-native-start-trial"
FILES = {NAME + ".service": (HERE / "early-start" / (NAME + ".service")).read_bytes(),
         NAME + ".timer": (HERE / "early-start" / (NAME + ".timer")).read_bytes(),
         "." + NAME: b"vetro-native-start-trial-v1\n"}


def build(action, prefix=""):
    # Test-only prefix is never accepted from the CLI.
    q = shlex.quote
    parent = prefix + "/home/owner/.config"
    root = parent + "/systemd"
    user = root + "/user"
    wants = user + "/default.target.wants"
    link = wants + "/" + NAME + ".timer"
    lines = ["set -eu", "umask 077",
             "[ -d %s ] && [ ! -L %s ] || exit 20" % (q(parent), q(parent))]
    if action == "apply":
        lines += ["[ ! -e %s ] && [ ! -L %s ] || exit 21" % (q(root), q(root))]
        for directory in (root, user, wants):
            lines.append("mkdir -m 700 %s" % q(directory))
        for name, content in FILES.items():
            lines.append("printf '%%s' %s | base64 -d > %s" %
                         (q(base64.b64encode(content).decode()), q(user + "/" + name)))
        lines.append("ln -s ../%s.timer %s" % (NAME, q(link)))
        if not prefix:
            # Numeric identity verified on this TV; never rely on a name alias.
            lines.append("chown 5001:100 " + " ".join(q(p) for p in
                         (root, user, wants) + tuple(user + "/" + n for n in FILES)))
        lines.append("echo NATIVE_START_TRIAL_INSTALLED_NOT_STARTED")
    elif action == "remove":
        for directory in (root, user, wants):
            lines.append("[ -d %s ] && [ ! -L %s ] || exit 22" % (q(directory), q(directory)))
        for name, content in FILES.items():
            target = q(user + "/" + name)
            lines += ["[ -f %s ] && [ ! -L %s ] || exit 23" % (target, target),
                      "[ \"$(sha256sum %s | cut -d' ' -f1)\" = %s ] || exit 24" %
                      (target, q(hashlib.sha256(content).hexdigest()))]
        lines += ["[ -L %s ] || exit 25" % q(link),
                  "[ \"$(readlink %s)\" = ../%s.timer ] || exit 25" % (q(link), NAME)]
        bus = "XDG_RUNTIME_DIR=/run/user/5001 DBUS_SESSION_BUS_ADDRESS=kernel:path=/sys/fs/kdbus/5001-user/bus systemctl --user "
        if not prefix:
            lines.append(bus + "stop " + NAME + ".timer")
        lines.append("rm -f " + " ".join(q(p) for p in (link,) + tuple(user + "/" + n for n in FILES)))
        for directory in (wants, user, root):
            lines.append("rmdir %s 2>/dev/null || true" % q(directory))
        if not prefix:
            lines.append(bus + "daemon-reload")
        # The actual Vetro application is never stopped by this operation.
        lines.append("echo NATIVE_START_TRIAL_FILES_REMOVED")
    else:
        raise ValueError("Unknown action")
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("plan", "apply", "remove"), nargs="?", default="plan")
    p.add_argument("--tv")
    p.add_argument("--owner-approved", action="store_true")
    a = p.parse_args()
    if a.action == "plan":
        print(json.dumps({"installed": False, "nativeProgram": "/usr/bin/app_launcher",
                          "onlyApp": "vetrotvapp.svc", "attemptBootSeconds": [30, 50, 70],
                          "successSuppressesLaterAttempts": True, "liveLaunch": False,
                          "fallbackChanged": False, "hardwareBootValidated": False}, indent=2))
        return
    if not a.owner_approved or not a.tv:
        p.error("Explicit approval and the one TV address are required")
    if ipaddress.ip_address(a.tv).version != 4:
        p.error("One approved TV IPv4 required")
    os.umask(0o077)
    folder = HERE.parents[1] / "recovery/private/startup-analysis"
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    out = Path(tempfile.mkdtemp(prefix="native-start-%s-" % a.action, dir=folder))
    command = build(a.action)
    (out / "submitted.sh").write_text(command)
    result = subprocess.run(["/usr/bin/curl", "--noproxy", "", "--silent", "--show-error", "--fail",
                             "--connect-timeout", "3", "--max-time", "35", "-H", "Content-Type: application/json",
                             "--data-binary", "@-", "http://%s:8099/exec" % a.tv],
                            input=json.dumps({"cmd": command}), capture_output=True, text=True, timeout=38)
    (out / "response.txt").write_text(result.stdout)
    if result.returncode:
        raise SystemExit("Request failed; inspect partial state before retrying")
    response = json.loads(result.stdout)
    marker = "NATIVE_START_TRIAL_" + ("INSTALLED_NOT_STARTED" if a.action == "apply" else "FILES_REMOVED")
    if not response.get("ok") or response.get("exit_code") != 0 or response.get("timed_out") or marker not in response.get("output", ""):
        raise SystemExit("Action incomplete; preserve journal and inspect before retrying")
    print(json.dumps({"action": a.action, "completed": True, "liveLaunch": False, "rebootRequested": False}))


if __name__ == "__main__":
    main()
