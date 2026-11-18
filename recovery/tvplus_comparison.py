#!/usr/bin/env python3
"""Default local plan; four owner-operated A/A/B/B TV Plus comparison reboots."""
import argparse
import concurrent.futures
import json
import math
import os
from pathlib import Path
import statistics
import tempfile
import time

import boot_observer as observer
from privacy_profile import Profile as Api

PRIVATE = Path(__file__).resolve().parents[2] / "recovery/private/startup-analysis"
IDS = ("com.samsung.tv.tvplus", "com.samsung.tv.tvPlusDeeplinker")
FIELDS = ("disabled", "onboot", "autorestart")
SEQUENCE = (("A", 1), ("A", 2), ("B", 1), ("B", 2))


def command(key, disabled):
    if key not in IDS or type(disabled) is not bool:
        raise ValueError("Only reviewed TV Plus components may be changed")
    return "pkgcmd %s -t app -n %s --global" % ("-D" if disabled else "-A", key)


def decision(runs):
    if any(r.get("phase") == "B" and r.get("tvPlusOffVerified") is not True for r in runs):
        raise ValueError("TV Plus programme shutdown must be independently verified; app flags are insufficient")
    a = [x["launcherStartBootSeconds"] for x in runs if x["phase"] == "A"]
    b = [x["launcherStartBootSeconds"] for x in runs if x["phase"] == "B"]
    if len(a) != 2 or len(b) != 2:
        raise ValueError("Two valid samples per state are required")
    gain = statistics.mean(a) - statistics.mean(b)
    # Practical predeclared rule, not a statistical significance test.
    threshold = max(2.0, max(a) - min(a), max(b) - min(b))
    return {"meanOnSeconds": round(statistics.mean(a), 3),
            "meanOffSeconds": round(statistics.mean(b), 3),
            "gainSeconds": round(gain, 3), "practicalThresholdSeconds": round(threshold, 3),
            "clearPracticalGain": gain > threshold,
            "limitations": "Two runs per state; process start, not user-visible readiness; not statistical proof."}


class Trial:
    def __init__(self, tv, folder):
        self.folder = folder
        self.api = Api(tv, folder)
        self.base = "http://%s:8099" % tv
        self.state = {"format": 1, "original": {}, "attempted": [], "runs": [], "complete": False}
        observer.recorder.request = observer.managed_request

    def save(self):
        (self.folder / "comparison.json").write_text(json.dumps(self.state, indent=2) + "\n")

    def check_cancel(self):
        if (self.folder / "CANCEL").exists():
            raise RuntimeError("Comparison cancelled")

    def validate_resume(self):
        if self.state.get("format") != 1 or self.state.get("complete"):
            raise ValueError("Unrecognized or completed comparison")
        if set(self.state.get("original", {})) != set(IDS):
            raise ValueError("Unexpected original identities")
        if any(type(self.state["original"][k].get(f)) is not bool for k in IDS for f in FIELDS):
            raise ValueError("Unknown original flags")
        runs = self.state.get("runs")
        if not isinstance(runs, list) or len(runs) > len(SEQUENCE):
            raise ValueError("Unexpected run count")
        for run, expected in zip(runs, SEQUENCE):
            if (run.get("phase"), run.get("run")) != expected or run.get("newKernelBootConfirmed") is not True:
                raise ValueError("Unexpected run order or missing boot evidence")
            value = run.get("launcherStartBootSeconds")
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError("Invalid process timing")

    def rows(self):
        return self.api.rows()

    def initialize(self):
        rows = self.rows()
        for key in IDS:
            if key not in rows or any(type(rows[key].get(f)) is not bool for f in FIELDS):
                raise RuntimeError("Original TV Plus flags unavailable")
            if rows[key]["disabled"]:
                raise RuntimeError("TV Plus is not fully enabled; do not overwrite an unexpected baseline")
            self.state["original"][key] = {f: rows[key][f] for f in FIELDS}
        self.state["allFlagsBefore"] = {k: {f: r[f] for f in FIELDS} for k, r in rows.items()}
        dns = self.api.request("/dns")
        self.state["dnsBefore"] = {k: dns[k] for k in ("enabled", "domains")}
        self.save()

    def set_disabled(self, disabled):
        for key in IDS:
            self.check_cancel()
            self.state["attempted"].append({"appId": key, "disabled": disabled})
            self.save()
            self.api.request("/exec", {"cmd": command(key, disabled)})
            if self.rows()[key]["disabled"] is not disabled:
                raise RuntimeError("TV Plus flag not confirmed")

    def verify_controls(self, disabled):
        rows = self.rows()
        for key, old in self.state["allFlagsBefore"].items():
            if key not in rows:
                raise RuntimeError("Inventory changed during comparison")
            for field in FIELDS:
                expected = disabled if key in IDS and field == "disabled" else old[field]
                if rows[key][field] != expected:
                    raise RuntimeError("Another registry flag changed; comparison must stop")
        dns = self.api.request("/dns")
        if any(dns[k] != self.state["dnsBefore"][k] for k in ("enabled", "domains")) or (dns["enabled"] and not dns["applied"]):
            raise RuntimeError("Filter configuration or application differs")

    def recover_pending_boot(self):
        """Use only after the collector has ended: late proc timings remain valid."""
        self.validate_resume()
        if len(self.state["runs"]) >= len(SEQUENCE):
            raise ValueError("No pending sample")
        phase, number = SEQUENCE[len(self.state["runs"])]
        pending = self.state.get("pendingReboot") or {}
        if (pending.get("phase"), pending.get("number")) != (phase, number):
            raise ValueError("No matching pending owner-operated reboot")
        out = self.folder / (phase + str(number))
        baseline = json.loads((out / "baseline.json").read_text())
        rec = observer.recorder
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            row = rec.sample(self.base, pool, False, 3)
        old_boot = rec.data_at(baseline, "/telemetry").get("boot_id")
        new_boot = rec.data_at(row, "/telemetry").get("boot_id")
        status = rec.data_at(row, "/status")
        if not old_boot or not new_boot or old_boot == new_boot or not status.get("agent", {}).get("connected"):
            raise RuntimeError("A new ready kernel boot is not confirmed")
        self.verify_controls(phase == "B")
        service = rec.process_snapshot(self.base, status.get("pid"))
        dock = rec.dock_snapshot(self.base)
        if "processStartBootSeconds" not in service or service.get("parseError") or not dock.get("dockRunning") or dock.get("parseError"):
            raise RuntimeError("Late process timing is not ready")
        (out / "late-recovery.json").write_text(json.dumps({"row": row, "service": service, "dock": dock}, indent=2))
        result = {"phase": phase, "run": number, "newKernelBootConfirmed": True,
                  "serviceStartBootSeconds": service["processStartBootSeconds"],
                  "launcherStartBootSeconds": dock["dockStartBootSeconds"],
                  "firstServiceObservationUptimeSeconds": None,
                  "observationMode": "late proc/stat snapshot after owner reboot; original preboot UUID differs",
                  "bootTimelineCaptureComplete": False}
        self.state["runs"].append(result)
        self.state["pendingReboot"] = None
        self.save()
        print(json.dumps(result), flush=True)

    def restore(self):
        original = self.state.get("original")
        if not isinstance(original, dict) or set(original) != set(IDS):
            raise ValueError("Unrecognized original TV Plus identities")
        for key in IDS:
            if any(type(original[key].get(f)) is not bool for f in FIELDS):
                raise ValueError("Invalid original flags")
        self.state["restoreAttempted"] = True
        self.save()
        for key in reversed(IDS):
            self.api.request("/exec", {"cmd": command(key, original[key]["disabled"])})
        rows = self.rows()
        if any(rows[k][f] != original[k][f] for k in IDS for f in FIELDS):
            raise RuntimeError("Original effective TV Plus state not restored")
        self.state["restored"] = True
        self.save()

    def boot(self, phase, number):
        self.check_cancel()
        rec = observer.recorder
        out = self.folder / (phase + str(number))
        out.mkdir()
        rows = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            baseline = rec.sample(self.base, pool, True, 3)
            if not rec.baseline_valid(baseline) or not rec.data_at(baseline, "/status").get("agent", {}).get("connected"):
                raise RuntimeError("TV is not ready for a controlled reboot")
            (out / "baseline.json").write_text(json.dumps(baseline, indent=2))
            self.state["pendingReboot"] = {"phase": phase, "number": number, "intent": True}
            self.save()
            print("WAIT_FOR_OWNER_REBOOT " + phase + str(number), flush=True)
            start = time.monotonic()
            snapshot = None
            dock = None
            connected_at = None
            with (out / "events.jsonl").open("x", buffering=1) as log:
                while time.monotonic() - start < 900:
                    self.check_cancel()
                    row = rec.sample(self.base, pool, False, 0.8)
                    rows.append(row)
                    log.write(json.dumps(row) + "\n")
                    summary = rec.summarize(baseline, rows, [], "passive")
                    if summary["distinctNewBoots"] > 1:
                        raise RuntimeError("Unexpected extra reboot")
                    if summary["captureComplete"]:
                        if connected_at is None:
                            connected_at = time.monotonic()
                            print("New boot and root confirmed for " + phase + str(number), flush=True)
                        if time.monotonic() - connected_at >= 20:
                            pid = rec.data_at(row, "/status").get("pid")
                            snapshot = rec.process_snapshot(self.base, pid)
                            dock = rec.dock_snapshot(self.base)
                            if dock.get("dockRunning") and not dock.get("parseError"):
                                break
                    time.sleep(1)
                else:
                    raise RuntimeError("No complete owner-operated boot within 900 seconds; inspect")
        if not snapshot or snapshot.get("parseError") or "processStartBootSeconds" not in snapshot:
            raise RuntimeError("Service process timing unavailable")
        (out / "process.json").write_text(json.dumps(snapshot, indent=2))
        (out / "dock.json").write_text(json.dumps(dock, indent=2))
        (out / "summary.json").write_text(json.dumps(summary, indent=2))
        result = {"phase": phase, "run": number, "newKernelBootConfirmed": True,
                  "serviceStartBootSeconds": snapshot["processStartBootSeconds"],
                  "launcherStartBootSeconds": dock["dockStartBootSeconds"],
                  "firstServiceObservationUptimeSeconds": summary.get("firstServiceObservationUptimeSeconds")}
        self.state["runs"].append(result)
        self.state["pendingReboot"] = None
        self.save()
        self.verify_controls(phase == "B")
        print(json.dumps(result), flush=True)
        # Equal minimum uptime before the next reboot limits recovery/background-load asymmetry.
        uptime = dock["snapshotUptimeSeconds"]
        wait = max(0, 100 - uptime)
        if wait:
            print("Settling for %.0f seconds" % wait, flush=True)
        while wait > 0:
            self.check_cancel()
            part = min(5, wait)
            time.sleep(part)
            wait -= part

    def run(self, resume=False):
        if resume:
            self.validate_resume()
        else:
            self.initialize()
        try:
            for phase, number in SEQUENCE[len(self.state["runs"]):]:
                self.check_cancel()
                rows = self.rows()
                flags = [rows[k]["disabled"] for k in IDS]
                if flags not in ([False, False], [True, True]):
                    raise RuntimeError("Partial TV Plus state; inspect before resuming")
                if phase == "A" and any(flags):
                    raise RuntimeError("TV Plus must be on for the baseline")
                if phase == "B" and not any(flags):
                    self.set_disabled(True)
                self.verify_controls(phase == "B")
                self.boot(phase, number)
            result = decision(self.state["runs"])
            self.state["decision"] = result
            if not result["clearPracticalGain"]:
                self.restore()
            self.state["finalTvPlusDisabled"] = result["clearPracticalGain"]
            self.state["complete"] = True
            self.save()
            print(json.dumps(result), flush=True)
        except BaseException:
            # Preserve comparison and intents. A restoration is safe only while the TV responds;
            # if it fails, leave an explicit unresolved record, never claim success.
            if self.state["attempted"]:
                try:
                    self.restore()
                except Exception as e:
                    self.state["restoreUnconfirmed"] = type(e).__name__
                    self.save()
            raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("plan", "run", "resume", "recover", "restore"), nargs="?", default="plan")
    p.add_argument("--tv")
    p.add_argument("--journal")
    p.add_argument("--owner-approved", action="store_true")
    a = p.parse_args()
    if a.action == "plan":
        print(json.dumps({"components": IDS, "sequence": ["A1 on", "A2 on", "B1 off", "B2 off"],
                          "rebootsOperatedByOwner": True, "hostReboot": False,
                          "sharedAdFrameworkChanged": False,
                          "experimentBlocked": True,
                          "reason": "Owner observed TV Plus programme still playing with these app flags disabled; native deactivation required",
                          "fallback": "Restore original app flags; do not infer an off-state speed gain"}, indent=2))
        return
    if a.action in ("run", "resume"):
        p.error("This component-only experiment is invalid: TV Plus programme continued. Use native deactivation before a new experiment.")
    import ipaddress
    if not a.owner_approved or not a.tv or ipaddress.ip_address(a.tv).version != 4:
        p.error("Explicit approval and the one approved TV IPv4 are required")
    os.umask(0o077)
    if a.action == "run":
        folder = Path(tempfile.mkdtemp(prefix="tvplus-comparison-", dir=PRIVATE))
        t = Trial(a.tv, folder)
        print("Private comparison journal: " + str(folder / "comparison.json"), flush=True)
        t.run()
    else:
        if not a.journal:
            p.error("Original comparison journal required")
        path = Path(a.journal).resolve()
        if PRIVATE.resolve() not in path.parents or path.name != "comparison.json":
            p.error("Journal must be inside the private comparison folder")
        t = Trial(a.tv, path.parent)
        t.state = json.loads(path.read_text())
        if a.action == "resume":
            t.run(resume=True)
        elif a.action == "recover":
            t.recover_pending_boot()
        else:
            t.restore()


if __name__ == "__main__":
    main()
