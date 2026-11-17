import json
from pathlib import Path
import tempfile
import unittest

import performance_trial as trial


class FakeProfile(trial.Profile):
    def __init__(self, folder):
        super().__init__("192.0.2.1", folder)
        self.live = {k: {"appId": k, "disabled": False, "onboot": True, "autorestart": False}
                     for k in trial.IDS[:2]}
        self.fail_once = None
        self.changes = []

    def request(self, route, payload=None):
        if route == "/apps":
            return {"apps": list(self.live.values())}
        if route == "/exec":
            return {"ok": True, "exit_code": 0, "output": "ABSENT\n"}
        key = payload["appIds"][0]
        # Model a timeout AFTER the mutation, the dangerous ambiguous case.
        self.live[key]["disabled"] = payload["action"] == "disable"
        self.changes.append(key)
        if self.fail_once == key:
            self.fail_once = None
            raise RuntimeError("lost reply")
        return {"verified": True, "disabled": self.live[key]["disabled"]}


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[2] / "recovery/private/tool-tmp"
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.profile = FakeProfile(Path(self.temp.name))

    def test_roundtrip_preserves_originally_disabled(self):
        p = self.profile
        p.live[trial.IDS[1]]["disabled"] = True
        p.apply()
        p.restore()
        self.assertFalse(p.live[trial.IDS[0]]["disabled"])
        self.assertTrue(p.live[trial.IDS[1]]["disabled"])
        self.assertNotIn(trial.IDS[1], p.changes)

    def test_lost_reply_retains_intent_and_can_restore(self):
        p = self.profile
        p.fail_once = trial.IDS[1]
        with self.assertRaises(RuntimeError):
            p.apply()
        j = json.loads((p.folder / "journal.json").read_text())
        self.assertIn(trial.IDS[1], j["attempted"])
        p.journal = j
        p.restore()
        self.assertTrue(all(not r["disabled"] for r in p.live.values()))

    def test_unknown_original_state_prevents_any_change(self):
        p = self.profile
        p.live[trial.IDS[1]]["disabled"] = None
        with self.assertRaises(RuntimeError):
            p.apply()
        self.assertEqual(p.changes, [])

    def test_forged_restore_id_is_never_executed(self):
        p = self.profile
        p.journal["attempted"] = ["org.tizen.tv-viewer"]
        with self.assertRaises(ValueError):
            p.restore()
        self.assertEqual(p.changes, [])


if __name__ == "__main__":
    unittest.main()
