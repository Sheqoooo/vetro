#!/usr/bin/env python3
"""Bounded performance profile. Default plan is local; apply/restore need approval."""
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
PRIVATE = HERE.parents[1] / "recovery/private/startup-analysis"
NAME = "vetro-native-start-trial"
ACR = ["com.samsung.tv.acr", "com.samsung.tv.canalysis-service",
       "com.samsung.tv.vision-data-recognition-service", "com.samsung.tv.contents-recognition-dbmgr",
       "com.samsung.tv.nvision-analysis-dbmgr"]
VOICE = ["com.samsung.tv.alexa-client", "com.samsung.tv.alexa-fullscreen-app",
         "com.samsung.tv.alexa-jump-starter", "com.samsung.tv.wakeup-engine-alexa",
         "com.samsung.tv.google-assistant", "com.samsung.tv.google-fullscreen-app",
         "com.samsung.tv.bixby-context-client", "com.samsung.tv.bixby-prov",
         "com.samsung.tv.bixbycapsuleviewer", "com.samsung.tv.mybixby", "com.samsung.tv.wakeup-engine-bixby"]
IDS = ACR + VOICE
FLAG = "/home/owner/apps_rw/com.samsung.tv.multiscreen/data/disable_preloading"


def timing_script(restore=False):
    q = shlex.quote
    source, target = ("fast-start", "baseline-30s") if restore else ("baseline-30s", "fast-start")
    user = "/home/owner/.config/systemd/user"
    lines = ["set -eu", "umask 077"]
    for directory in ("/home/owner/.config", "/home/owner/.config/systemd", user):
        lines.append("[ -d %s ] && [ ! -L %s ] || exit 20" % (q(directory), q(directory)))
    # Check both originals before changing either file. All content is repo-owned.
    for suffix in ("service", "timer"):
        path = user + "/" + NAME + "." + suffix
        original = (HERE / "early-start" / source / (NAME + "." + suffix)).read_bytes()
        lines += ["[ -f %s ] && [ ! -L %s ] || exit 21" % (q(path), q(path)),
                  "[ \"$(sha256sum %s | cut -d' ' -f1)\" = %s ] || exit 22" %
                  (q(path), q(hashlib.sha256(original).hexdigest())),
                  "[ ! -e %s ] && [ ! -L %s ] || exit 23" % (q(path + ".performance-new"), q(path + ".performance-new"))]
    for suffix in ("service", "timer"):
        path = user + "/" + NAME + "." + suffix
        data = (HERE / "early-start" / target / (NAME + "." + suffix)).read_bytes()
        temp = path + ".performance-new"
        lines += ["(set -C; printf '%%s' %s | base64 -d > %s)" % (q(base64.b64encode(data).decode()), q(temp)),
                  "chmod 600 %s" % q(temp), "chown 5001:100 %s" % q(temp),
                  "[ \"$(sha256sum %s | cut -d' ' -f1)\" = %s ] || exit 24" % (q(temp), q(hashlib.sha256(data).hexdigest())),
                  "mv %s %s" % (q(temp), q(path))]
    lines.append("echo TIMING_FILES_VERIFIED")
    return "\n".join(lines)


class Profile:
    def __init__(self, tv, folder):
        self.tv, self.folder = tv, folder
        self.journal = {"format": 1, "attempted": [], "baseline": {}, "timingAttempted": False,
                        "flagAttempted": False, "complete": False}

    def save(self):
        (self.folder / "journal.json").write_text(json.dumps(self.journal, indent=2) + "\n")

    def request(self, route, payload=None):
        if route not in ("/apps", "/debloat", "/exec"):
            raise ValueError("Unexpected route")
        args = ["/usr/bin/curl", "--noproxy", "", "--silent", "--show-error", "--fail",
                "--connect-timeout", "3", "--max-time", "45", "http://%s:8099%s" % (self.tv, route)]
        if payload is not None:
            args += ["-H", "Content-Type: application/json", "--data-binary", "@-"]
        p = subprocess.run(args, input=json.dumps(payload) if payload is not None else None,
                           capture_output=True, text=True, timeout=48)
        if p.returncode:
            raise RuntimeError("Request uncertain; inspect journal, do not retry blindly")
        d = json.loads(p.stdout)
        if d.get("error") or d.get("ok") is False or d.get("timed_out"):
            raise RuntimeError("TV operation failed; inspect journal")
        if route == "/exec" and d.get("exit_code") != 0:
            raise RuntimeError("TV command incomplete; inspect journal")
        return d

    def rows(self):
        d = self.request("/apps")
        if d.get("registryError") or not d.get("apps"):
            raise RuntimeError("Registry unavailable")
        return {r["appId"]: r for r in d["apps"]}

    def apply(self):
        rows = self.rows()
        for key in IDS:
            if key not in rows:
                continue
            r = rows[key]
            if any(type(r.get(k)) is not bool for k in ("disabled", "onboot", "autorestart")):
                raise RuntimeError("Unknown original flag")
            self.journal["baseline"][key] = {k: r[k] for k in ("disabled", "onboot", "autorestart")}
        # A current nonempty flag is outside this profile's ownership: refuse it.
        d = self.request("/exec", {"cmd": "if [ -e " + FLAG + " ] || [ -L " + FLAG + " ]; then echo PRESENT; else echo ABSENT; fi"})
        if d.get("output", "").strip() != "ABSENT":
            raise RuntimeError("Preload flag already exists; preserve it")
        self.save()
        for key, r in self.journal["baseline"].items():
            if r["disabled"]:
                continue
            self.journal["attempted"].append(key)
            self.save()  # Intent before request: timeout is not proof of no change.
            d = self.request("/debloat", {"action": "disable", "appIds": [key]})
            if d.get("disabled") is not True or not d.get("verified"):
                raise RuntimeError("Disable not verified")
            print("Disabled and verified: " + key, flush=True)
        self.journal["flagAttempted"] = True
        self.save()
        parent = str(Path(FLAG).parent)
        script = "set -eu\n[ -d %s ] && [ ! -L %s ] || exit 20\n[ ! -e %s ] && [ ! -L %s ] || exit 21\n(set -C; : > %s)\nchown 5001:system_share %s\nchmod 664 %s\necho PRELOAD_FLAG_CREATED" % (parent, parent, FLAG, FLAG, FLAG, FLAG, FLAG)
        self.request("/exec", {"cmd": script})
        self.journal["timingAttempted"] = True
        self.save()
        self.request("/exec", {"cmd": timing_script()})
        after = self.rows()
        for key, old in self.journal["baseline"].items():
            if after[key]["disabled"] is not True or any(after[key][k] != old[k] for k in ("onboot", "autorestart")):
                raise RuntimeError("Profile validation failed")
        self.journal["complete"] = True
        self.save()

    def restore(self):
        # Never accept app IDs or shell instructions outside the fixed allowlist.
        j = self.journal
        if j.get("format") != 1 or not isinstance(j.get("attempted"), list) or not isinstance(j.get("baseline"), dict):
            raise ValueError("Invalid journal")
        for key in j["attempted"]:
            if key not in IDS or key not in j["baseline"] or any(type(j["baseline"][key].get(k)) is not bool for k in ("disabled", "onboot", "autorestart")):
                raise ValueError("Invalid restoration entry")
        if j.get("timingAttempted"):
            self.request("/exec", {"cmd": timing_script(restore=True)})
        if j.get("flagAttempted"):
            # Empty regular file only. No directory traversal or recursive removal.
            self.request("/exec", {"cmd": "set -eu\n[ -f " + FLAG + " ] && [ ! -L " + FLAG + " ] && [ ! -s " + FLAG + " ] || exit 22\nrm " + FLAG})
        for key in reversed(j["attempted"]):
            desired = j["baseline"][key]["disabled"]
            d = self.request("/debloat", {"action": "disable" if desired else "enable", "appIds": [key]})
            if d.get("disabled") is not desired or not d.get("verified"):
                raise RuntimeError("Restore not verified")
        rows = self.rows()
        if any(any(rows[key][k] != old[k] for k in ("disabled", "onboot", "autorestart")) for key, old in j["baseline"].items()):
            raise RuntimeError("Restored effective flags not confirmed")
        j["restored"] = True
        self.save()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("plan", "apply", "restore"), nargs="?", default="plan")
    p.add_argument("--tv")
    p.add_argument("--journal")
    p.add_argument("--owner-approved", action="store_true")
    a = p.parse_args()
    if a.action == "plan":
        print(json.dumps({"firstAttemptBootSeconds": 12, "fallbackSeconds": [30, 50, 70],
                          "optionalIds": IDS, "multiviewPreloadOnly": True,
                          "liveProcessesStopped": False, "uninstall": False}, indent=2))
        return
    if not a.owner_approved or not a.tv or ipaddress.ip_address(a.tv).version != 4:
        p.error("Explicit approval and the one approved TV IPv4 are required")
    os.umask(0o077)
    if a.action == "apply":
        folder = Path(tempfile.mkdtemp(prefix="performance-run-", dir=PRIVATE))
        profile = Profile(a.tv, folder)
        print("Private journal: " + str(folder / "journal.json"), flush=True)
        profile.apply()
    else:
        if not a.journal:
            p.error("Pass the original private journal")
        journal = Path(a.journal).resolve()
        if PRIVATE.resolve() not in journal.parents or journal.name != "journal.json":
            p.error("Journal must be inside the private project startup-analysis folder")
        profile = Profile(a.tv, journal.parent)
        profile.journal = json.loads(journal.read_text())
        profile.restore()
    print(json.dumps({"completed": True, "action": a.action, "rebootRequested": False}))


if __name__ == "__main__":
    main()
