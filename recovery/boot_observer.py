#!/usr/bin/env python3
"""Use Vetro's existing read-only boot recorder through the managed HTTP proxy.

No TV reboot, launch, settings write, or extra binary. Raw results stay private.
"""
import importlib.util
import ipaddress
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("vetro_boot_recorder", REPO / "app/scripts/boot-test.py")
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)


def managed_request(base, route, timeout=0.8, command=None):
    result = {"route": route, "start": recorder.stamp()}
    try:
        if route not in ("/status", "/telemetry", "/probe", "/exec"):
            raise ValueError("Unexpected recorder route")
        if (command is None) != (route != "/exec"):
            raise ValueError("Only existing read-only process snapshots may use exec")
        call = ["/usr/bin/curl", "--noproxy", "", "--silent", "--show-error", "--fail",
                "--connect-timeout", str(timeout), "--max-time", str(timeout), base + route]
        if command is not None:
            call += ["-H", "Content-Type: application/json", "--data-binary", "@-"]
        completed = subprocess.run(call, input=json.dumps({"cmd": command}) if command is not None else None,
                                   capture_output=True, text=True, timeout=timeout + 2)
        if completed.returncode:
            raise RuntimeError("curl exit %d" % completed.returncode)
        data = json.loads(completed.stdout)
        result.update(ok=True, data=recorder.compact(route, data) if route in recorder.ROUTES else data)
    except Exception as error:
        result.update(ok=False, error=type(error).__name__ + ": " + str(error))
    result["end"] = recorder.stamp()
    result["durationSeconds"] = result["end"]["monotonic"] - result["start"]["monotonic"]
    return result


def main():
    argv = sys.argv[1:]
    if "--base" not in argv:
        raise SystemExit("Pass the one approved TV URL explicitly with --base")
    base = urlsplit(argv[argv.index("--base") + 1])
    if base.scheme != "http" or base.port != 8099 or base.username or base.password or base.query or base.fragment or base.path not in ("", "/"):
        raise SystemExit("Expected an uncredentialed TV HTTP URL on port 8099")
    if ipaddress.ip_address(base.hostname).version != 4:
        raise SystemExit("Use the one approved TV IPv4 address; no discovery")
    if "record" in argv:
        if "--out" not in argv:
            raise SystemExit("Capture needs an explicit private output directory")
        output = Path(argv[argv.index("--out") + 1]).resolve()
        private = (REPO.parent / "recovery/private/startup-analysis").resolve()
        if private not in output.parents:
            raise SystemExit("Capture output must be under the project's private startup-analysis folder")
    os.umask(0o077)
    recorder.request = managed_request
    recorder.main()


if __name__ == "__main__":
    main()
