import copy
import json
from pathlib import Path
import tempfile
import unittest

import privacy_profile as trial


class Fake(trial.Profile):
    def __init__(self, folder):
        super().__init__("192.0.2.1", folder)
        self.live = {k: {"appId": k, "disabled": False, "onboot": True, "autorestart": True}
                     for k in trial.IDS[:2] + ["org.tizen.tv-viewer"]}
        self.dns = {"enabled": False, "applied": False, "domains": []}
        self.fail = None
        self.changes = []

    def request(self, route, payload=None):
        if route == "/apps?refresh=1":
            return {"apps": copy.deepcopy(list(self.live.values()))}
        if route == "/dns":
            if payload is not None:
                self.dns = {"enabled": payload["enabled"], "applied": payload["enabled"],
                            "domains": payload["domains"], "namespaceWarnings": []}
            return copy.deepcopy(self.dns)
        args = payload["cmd"].split()
        key = args[5]
        self.live[key]["disabled"] = args[1] == "-D"
        self.changes.append(key)
        if self.fail == key:
            self.fail = None
            raise RuntimeError("lost reply after mutation")
        return {"ok": True, "exit_code": 0}


class Tests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[2] / "recovery/private/tool-tmp"
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.p = Fake(Path(self.temp.name))

    def test_roundtrip_preserves_disabled_and_protected(self):
        self.p.live[trial.IDS[0]]["disabled"] = True
        self.p.apply()
        self.p.restore()
        self.assertTrue(self.p.live[trial.IDS[0]]["disabled"])
        self.assertFalse(self.p.live[trial.IDS[1]]["disabled"])
        self.assertFalse(self.p.live["org.tizen.tv-viewer"]["disabled"])
        self.assertFalse(self.p.dns["applied"])

    def test_ambiguous_mutation_is_journalled_for_rollback(self):
        self.p.fail = trial.IDS[1]
        with self.assertRaises(RuntimeError):
            self.p.apply()
        self.p.journal = json.loads((self.p.folder / "journal.json").read_text())
        self.p.restore()
        self.assertTrue(all(not x["disabled"] for x in self.p.live.values()))

    def test_existing_dns_filter_is_untouched(self):
        self.p.dns = {"enabled": True, "applied": True, "domains": ["example.org"]}
        with self.assertRaises(RuntimeError):
            self.p.apply()
        self.assertEqual(self.p.changes, [])
        self.assertEqual(self.p.dns["domains"], ["example.org"])

    def test_protected_or_forged_target_rejected(self):
        for key in ("com.samsung.tv.coba.adagent", "com.samsung.tv.ad-web-framework", "org.tizen.tv-viewer", "x;reboot"):
            with self.assertRaises(ValueError):
                trial.toggle_command(key, True)
        self.p.journal["attempted"] = ["org.tizen.tv-viewer"]
        with self.assertRaises(ValueError):
            self.p.restore()
        self.assertEqual(self.p.changes, [])


if __name__ == "__main__":
    unittest.main()
