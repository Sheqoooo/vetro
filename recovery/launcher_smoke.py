#!/usr/bin/env python3
"""Owner-authorized launcher on/off test; private post-root baseline first."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tv")
    parser.add_argument("--confirm-on-off", action="store_true", required=True)
    args = parser.parse_args()
    import ipaddress
    if ipaddress.ip_address(args.tv).version != 4:
        parser.error("One approved TV IPv4 required")
    repo = Path(__file__).resolve().parents[1]
    private = repo.parent / "recovery/private/launcher-tests"
    private.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory = Path(tempfile.mkdtemp(prefix="on-off-", dir=str(private)))
    directory.chmod(0o700)
    os.umask(0o077)
    def save(name, data):
        with (directory / name).open("x") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
    def request(endpoint, body=None, port=8099, timeout=35):
        command = ["/usr/bin/curl", "--noproxy", "", "--silent", "--show-error", "--fail",
                   "--connect-timeout", "3", "--max-time", str(timeout),
                   "http://%s:%s%s" % (args.tv, port, endpoint)]
        if body is not None:
            command.extend(["-H", "Content-Type: application/json", "--data-binary", "@-"])
        result = subprocess.run(command, input=json.dumps(body) if body is not None else None,
                                capture_output=True, text=True, timeout=timeout + 3)
        if result.returncode:
            raise RuntimeError("HTTP request failed: %s (curl %d); remote state may be unknown" % (endpoint, result.returncode))
        data = json.loads(result.stdout)
        if not isinstance(data, dict) or data.get("error"):
            raise RuntimeError("Endpoint reported an error: " + endpoint)
        return data
    def execute(command):
        result = request("/exec", {"cmd": command})
        if not result.get("ok") or result.get("timed_out"):
            raise RuntimeError("TV read command failed")
        return result.get("output", "")
    autorun_cmd = "vconftool get db/menu/smart_hub/ontvsetting/auto_start 2>&1"
    def autorun():
        output = execute(autorun_cmd)
        found = re.search(r"value = (\d+)", output)
        if not found or int(found[1]) not in (0, 1):
            raise RuntimeError("Original Samsung autorun value cannot be determined")
        return int(found[1])
    def launcher_running():
        # Independent read-only process check. Upstream status can be unknown
        # before the native launcher's log exists, even when its PID is absent.
        command = r'''p=$(cat /home/owner/tvlauncher.pid 2>/dev/null); case "$p" in ''|*[!0-9]*) echo STOPPED;; *) if tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | grep -q tvlauncher-dotnet.dll; then echo RUNNING; else echo STOPPED; fi;; esac'''
        value = execute(command).strip()
        if value not in ("RUNNING", "STOPPED"):
            raise RuntimeError("Independent process check is unknown")
        return value == "RUNNING"
    status = request("/status")
    if not (status.get("agent") or {}).get("connected"):
        raise RuntimeError("Root agent not connected; no launcher change allowed")
    save("status-before.json", status)
    save("device-after-root.json", request("/api/v2/", port=8001))
    original_autorun = autorun()
    # Capture exact app state before GET /dock's preview can update its catalog.
    files = {}
    for name in ("vetro-dock.json", "vetro-dock-apps.tsv"):
        filename = "/opt/usr/home/owner/share/" + name
        output = execute("if [ -f '%s' ]; then echo PRESENT; base64 '%s'; "
                         "elif [ ! -e '%s' ]; then echo ABSENT; else exit 2; fi" % (filename, filename, filename))
        if output.startswith("PRESENT\n"):
            encoded = output.split("\n", 1)[1]
            base64.b64decode(encoded, validate=False)
            files[name] = {"present": True, "base64": encoded}
        elif output.strip() == "ABSENT":
            files[name] = {"present": False}
        else:
            raise RuntimeError("Cannot capture original launcher files")
    save("launcher-files-before.json", files)
    save("samsung-autorun-before.json", {"value": original_autorun})
    before = request("/dock")
    save("dock-before.json", before)
    original_running = launcher_running()
    save("launcher-process-before.json", {"running": original_running})
    if before.get("enabled") is not False or original_running or before.get("busy"):
        raise RuntimeError("Launcher is not confirmed off/idle; preserve existing state")
    if not before.get("installed") or before.get("autorunSwitchedOff"):
        raise RuntimeError("Launcher unavailable or earlier restore still pending")
    print(json.dumps({"stage": "baseline-saved", "originalSamsungAutorun": original_autorun, "launcherBefore": "off"}), flush=True)
    on_error = None
    changed_autorun = None
    try:
        print(json.dumps({"stage": "enabling"}), flush=True)
        enabled = request("/dock", {"action": "enable"}, timeout=100)
        save("dock-enabled.json", enabled)
        changed_autorun = autorun()
        save("samsung-autorun-enabled.json", {"value": changed_autorun})
        if enabled.get("enabled") is not True or enabled.get("running") is not True or enabled.get("error"):
            raise RuntimeError("Launcher enable did not reach a clean running state")
        if changed_autorun != 0:
            raise RuntimeError("Samsung autorun was not switched off as intended")
        print(json.dumps({"stage": "enabled-verified", "running": True, "SamsungAutorun": changed_autorun}), flush=True)
    except Exception as error:
        on_error = error
        save("enable-error.json", {"error": str(error)})
    finally:
        # Roll back even when enable timed out: the TV may have accepted the change.
        print(json.dumps({"stage": "disabling-for-restore"}), flush=True)
        disabled = request("/dock", {"action": "disable"}, timeout=45)
        save("dock-disabled.json", disabled)
        restored_autorun = autorun()
        save("samsung-autorun-after.json", {"value": restored_autorun})
        stopped = not launcher_running()
        save("launcher-process-after.json", {"running": not stopped})
        if disabled.get("enabled") is not False or not stopped or disabled.get("error") or disabled.get("autorunSwitchedOff"):
            raise RuntimeError("Launcher stop/restore incomplete; preserve baseline and inspect")
        if restored_autorun != original_autorun:
            raise RuntimeError("Samsung autorun differs from original; stop further changes")
        result = {"enableSucceeded": on_error is None, "launcherOff": True,
                  "launcherProcessStopped": True, "SamsungAutorunMatchesOriginal": True,
                  "SamsungAutorunChangedDuringTest": changed_autorun is not None and changed_autorun != original_autorun,
                  "originalSamsungAutorun": original_autorun,
                  "fullStateFileRestoreClaimed": False, "fullRootRollbackClaimed": False}
        save("RESULT.json", result)
        print(json.dumps(result), flush=True)
    if on_error:
        raise on_error


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"stopped": True, "error": str(error)}), flush=True)
        raise SystemExit(1)
