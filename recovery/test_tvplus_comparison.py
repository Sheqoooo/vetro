import copy
from pathlib import Path
import tempfile
import unittest

import tvplus_comparison as trial


class Tests(unittest.TestCase):
    def test_small_or_noisy_improvement_is_not_claimed(self):
        for times in ((40, 41, 39.5, 40), (40, 46, 39, 41)):
            runs = [{"phase": "A" if i < 2 else "B", "launcherStartBootSeconds": v}
                    for i, v in enumerate(times)]
            self.assertFalse(trial.decision(runs)["clearPracticalGain"])

    def test_clear_consistent_improvement_is_reported(self):
        runs = [{"phase": p, "launcherStartBootSeconds": v}
                for p, v in (("A", 45), ("A", 46), ("B", 35), ("B", 36))]
        self.assertTrue(trial.decision(runs)["clearPracticalGain"])

    def test_missing_repetitions_refused(self):
        with self.assertRaises(ValueError):
            trial.decision([])

    def test_unrelated_components_cannot_be_toggled(self):
        for key in ("org.tizen.tv-viewer", "com.samsung.tv.ad-web-framework", "x;reboot"):
            with self.assertRaises(ValueError):
                trial.command(key, True)

    def test_restore_refuses_forged_identity_before_api(self):
        root = Path(__file__).resolve().parents[2] / "recovery/private/tool-tmp"
        with tempfile.TemporaryDirectory(dir=root) as folder:
            t = trial.Trial("192.0.2.1", Path(folder))
            t.state["original"] = {"org.tizen.tv-viewer": {"disabled": False}}
            t.api.request = lambda *args: self.fail("Must not reach TV")
            with self.assertRaises(ValueError):
                t.restore()

    def test_restore_preserves_exact_effective_originals(self):
        root = Path(__file__).resolve().parents[2] / "recovery/private/tool-tmp"
        with tempfile.TemporaryDirectory(dir=root) as folder:
            t = trial.Trial("192.0.2.1", Path(folder))
            t.state["original"] = {k: {"disabled": False, "onboot": False, "autorestart": False} for k in trial.IDS}
            live = copy.deepcopy(t.state["original"])
            for row in live.values():
                row["disabled"] = True
            def request(route, payload):
                key = payload["cmd"].split()[5]
                live[key]["disabled"] = payload["cmd"].split()[1] == "-D"
                return {"ok": True, "exit_code": 0}
            t.api.request = request
            t.rows = lambda: copy.deepcopy(live)
            t.restore()
            self.assertEqual(live, t.state["original"])
            self.assertTrue(t.state["restored"])


if __name__ == "__main__":
    unittest.main()
