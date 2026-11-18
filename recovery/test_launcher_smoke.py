import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import launcher_smoke


class SmokeTests(unittest.TestCase):
    def simulate(self, original, fail_enable=False):
        state = {"enabled": False, "running": False, "autorun": original, "disable_calls": 0}
        def fake_run(command, **kwargs):
            url = next(item for item in command if item.startswith("http://"))
            endpoint = url.split(":8099")[-1]
            body = json.loads(kwargs["input"]) if kwargs.get("input") else None
            if endpoint == "/status":
                value = {"agent": {"connected": True}}
            elif ":8001/" in url:
                value = {"device": {"model": "TEST_FIXTURE"}}
            elif endpoint == "/exec":
                cmd = body["cmd"]
                if cmd.startswith("vconftool get"):
                    output = "value = %d" % state["autorun"]
                elif cmd.startswith("p=$(cat"):
                    output = "RUNNING\n" if state["running"] else "STOPPED\n"
                else:
                    output = "ABSENT\n"
                value = {"ok": True, "output": output}
            elif endpoint == "/dock":
                if body and body["action"] == "enable":
                    state.update(enabled=True, running=True, autorun=0)
                    if fail_enable:
                        raise subprocess.TimeoutExpired(command, 1)
                elif body and body["action"] == "disable":
                    state.update(enabled=False, running=False, autorun=original)
                    state["disable_calls"] += 1
                value = {"installed": True, "enabled": state["enabled"], "running": state["running"],
                         "busy": False, "error": None, "autorunSwitchedOff": False}
            else:
                raise AssertionError("Unexpected fake endpoint")
            return subprocess.CompletedProcess(command, 0, json.dumps(value), "")
        project = Path(__file__).resolve().parents[2]
        real_mkdtemp = tempfile.mkdtemp
        with tempfile.TemporaryDirectory(dir=project / "recovery/private/tool-tmp") as tmp:
            with patch.object(launcher_smoke.subprocess, "run", side_effect=fake_run), \
                 patch.object(launcher_smoke.tempfile, "mkdtemp", side_effect=lambda **kw: real_mkdtemp(dir=tmp)), \
                 patch("sys.argv", ["launcher_smoke", "192.0.2.1", "--confirm-on-off"]), \
                 contextlib.redirect_stdout(io.StringIO()):
                if fail_enable:
                    with self.assertRaises(subprocess.TimeoutExpired):
                        launcher_smoke.main()
                else:
                    launcher_smoke.main()
            self.assertEqual(state["disable_calls"], 1)
            self.assertFalse(state["enabled"])
            self.assertFalse(state["running"])
            self.assertEqual(state["autorun"], original)

    def test_original_zero(self):
        self.simulate(0)

    def test_original_one(self):
        self.simulate(1)

    def test_enable_timeout_still_disables(self):
        self.simulate(1, fail_enable=True)


if __name__ == "__main__":
    unittest.main()
