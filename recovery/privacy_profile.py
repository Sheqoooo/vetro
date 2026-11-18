#!/usr/bin/env python3
"""Exact reviewed TV privacy targets, with a private intent journal and rollback."""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
PRIVATE = HERE.parents[1] / "recovery/private"
IDS = ["com.samsung.tizen.samsung-analytics", "com.samsung.tv.cis",
       "com.samsung.tv.cis-api-service-app", "content-grab-service",
       "com.samsung.tv.targeted-ad-service", "com.samsung.tv.pisa-service",
       "com.samsung.tv.adagent-service", "org.tizen.pisa-control-service",
       "com.samsung.tv.adplayer", "adplatform.ADPlayer"]
DOMAINS = ["dc.di.atlas.samsung.com", "regi.di.atlas.samsung.com", "regi.bigdata.samsung.com",
           "lcprd1.samsungcloudsolution.net", "fc.samsungcloud.tv", "www.samsungrm.net",
           "devicelog.samsungcloudsolution.net"]


def toggle_command(key, disabled):
    if key not in IDS or type(disabled) is not bool:
        raise ValueError("Unreviewed component or state")
    return "pkgcmd %s -t app -n %s --global" % ("-D" if disabled else "-A", key)


class Profile:
    def __init__(self, tv, folder):
        self.tv, self.folder = tv, folder
        self.journal = {"format": 1, "baseline": {}, "attempted": [], "dnsAttempted": False, "complete": False}

    def save(self):
        (self.folder / "journal.json").write_text(json.dumps(self.journal, indent=2) + "\n")

    def request(self, route, payload=None):
        if route not in ("/apps?refresh=1", "/exec", "/dns"):
            raise ValueError("Unexpected route")
        args = ["/usr/bin/curl", "--noproxy", "", "--silent", "--show-error", "--fail",
                "--connect-timeout", "3", "--max-time", "45", "http://%s:8099%s" % (self.tv, route)]
        if payload is not None:
            args += ["-H", "Content-Type: application/json", "--data-binary", "@-"]
        p = subprocess.run(args, input=json.dumps(payload) if payload is not None else None,
                           capture_output=True, text=True, timeout=48)
        if p.returncode:
            raise RuntimeError("Request uncertain; inspect private journal before retry")
        d = json.loads(p.stdout)
        if d.get("error") or d.get("ok") is False or d.get("timed_out"):
            raise RuntimeError("TV operation incomplete; inspect journal")
        if route == "/exec" and d.get("exit_code") != 0:
            raise RuntimeError("TV command failed; inspect journal")
        return d

    def rows(self):
        d = self.request("/apps?refresh=1")
        if d.get("registryError") or not d.get("apps"):
            raise RuntimeError("Registry unavailable")
        return {r["appId"]: r for r in d["apps"]}

    def set_flag(self, key, disabled):
        self.request("/exec", {"cmd": toggle_command(key, disabled)})
        row = self.rows().get(key, {})
        if row.get("disabled") is not disabled:
            raise RuntimeError("Component flag not confirmed")

    def apply(self):
        before = self.rows()
        (self.folder / "before-apps.json").write_text(json.dumps(before))
        for key in IDS:
            if key not in before:
                continue
            row = before[key]
            if any(type(row.get(k)) is not bool for k in ("disabled", "onboot", "autorestart")):
                raise RuntimeError("Unknown original component state")
            self.journal["baseline"][key] = {k: row[k] for k in ("disabled", "onboot", "autorestart")}
        dns = self.request("/dns")
        # This profile only owns a new, initially absent filter. Never overwrite another one.
        if dns.get("enabled") is not False or dns.get("applied") is not False or dns.get("domains") != []:
            raise RuntimeError("An existing domain filter must be preserved")
        self.journal["dnsBefore"] = {"enabled": False, "domains": []}
        self.save()
        for key, old in self.journal["baseline"].items():
            if old["disabled"]:
                continue
            self.journal["attempted"].append(key)
            self.save()
            self.set_flag(key, True)
            print("Disabled and read back: " + key, flush=True)
        self.journal["dnsAttempted"] = True
        self.save()
        dns = self.request("/dns", {"action": "apply", "enabled": True, "domains": DOMAINS})
        (self.folder / "filter-response.json").write_text(json.dumps(dns))
        if dns.get("enabled") is not True or dns.get("applied") is not True or dns.get("namespaceWarnings") or set(dns.get("domains", [])) != set(DOMAINS):
            raise RuntimeError("Filter not fully confirmed; inspect or roll back")
        after = self.rows()
        for key, old in before.items():
            if key not in after:
                raise RuntimeError("Component disappeared unexpectedly")
            expected = True if key in self.journal["baseline"] else old["disabled"]
            if after[key]["disabled"] is not expected or any(after[key][k] != old[k] for k in ("onboot", "autorestart")):
                raise RuntimeError("Unexpected registry change")
        self.journal["complete"] = True
        self.save()

    def restore(self):
        j = self.journal
        if j.get("format") != 1 or not isinstance(j.get("baseline"), dict) or not isinstance(j.get("attempted"), list):
            raise ValueError("Invalid journal")
        for key in j["attempted"]:
            if key not in IDS or key not in j["baseline"] or type(j["baseline"][key].get("disabled")) is not bool:
                raise ValueError("Unreviewed restoration entry")
        if j.get("dnsAttempted"):
            current = self.request("/dns")
            if current.get("domains") not in ([], DOMAINS):
                raise RuntimeError("Filter was changed by someone else; preserve it")
            d = self.request("/dns", {"action": "apply", "enabled": False, "domains": []})
            if d.get("enabled") is not False or d.get("applied") is not False or d.get("namespaceWarnings"):
                raise RuntimeError("Filter removal not confirmed")
        for key in reversed(j["attempted"]):
            self.set_flag(key, j["baseline"][key]["disabled"])
        after = self.rows()
        for key, old in j["baseline"].items():
            if any(after[key][k] != old[k] for k in ("disabled", "onboot", "autorestart")):
                raise RuntimeError("Effective original flags not restored")
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
        print(json.dumps({"componentIds": IDS, "exactAnalyticsLogHosts": DOMAINS,
                          "uninstall": False, "protectedAdLibraryDisabled": False,
                          "tvPlusAdPlaybackDisabled": False, "guaranteesNoTracking": False}, indent=2))
        return
    if not a.owner_approved or not a.tv or ipaddress.ip_address(a.tv).version != 4:
        p.error("Explicit approval and one approved TV IPv4 required")
    os.umask(0o077)
    if a.action == "apply":
        folder = Path(tempfile.mkdtemp(prefix="privacy-run-", dir=PRIVATE))
        profile = Profile(a.tv, folder)
        print("Private journal: " + str(folder / "journal.json"), flush=True)
        profile.apply()
    else:
        if not a.journal:
            p.error("Original private journal required")
        path = Path(a.journal).resolve()
        if PRIVATE.resolve() not in path.parents or path.name != "journal.json":
            p.error("Journal must be inside the private project folder")
        profile = Profile(a.tv, path.parent)
        profile.journal = json.loads(path.read_text())
        profile.restore()
    print(json.dumps({"action": a.action, "complete": True, "rebootRequested": False}))


if __name__ == "__main__":
    main()
