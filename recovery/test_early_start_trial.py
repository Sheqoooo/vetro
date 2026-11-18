import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import early_start_trial as trial


class TrialFilesTests(unittest.TestCase):
    def setUp(self):
        project = Path(__file__).resolve().parents[2]
        self.temp = tempfile.TemporaryDirectory(dir=project / "recovery/private/tool-tmp")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "home/owner/.config"
        self.share = self.root / "home/owner/share"
        self.config.mkdir(parents=True)
        self.share.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        shim = self.bin / "sha256sum"
        shim.write_text("#!/Library/Developer/CommandLineTools/usr/bin/python3\nimport hashlib,sys\nfrom pathlib import Path\nprint(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()+'  '+sys.argv[1])\n")
        shim.chmod(0o700)
        self.env = dict(os.environ, PATH=str(self.bin) + ":/usr/bin:/bin")

    def run_action(self, action):
        return subprocess.run(["/bin/sh"], input=trial.build(action, str(self.root)),
                              capture_output=True, text=True, env=self.env)

    def test_roundtrip_leaves_original_directories(self):
        self.assertEqual(self.run_action("apply").returncode, 0)
        unit = self.config / "systemd/user/vetro-early-start-trial.service"
        self.assertEqual(unit.read_bytes(), trial.UNIT)
        self.assertTrue((unit.parent / "default.target.wants/vetro-early-start-trial.service").is_symlink())
        self.assertEqual(self.run_action("remove").returncode, 0)
        self.assertEqual(list(self.config.iterdir()), [])
        self.assertEqual(list(self.share.iterdir()), [])

    def test_existing_config_not_overwritten(self):
        systemd = self.config / "systemd"
        systemd.mkdir()
        sentinel = systemd / "someone-elses-file"
        sentinel.write_text("preserve")
        self.assertNotEqual(self.run_action("apply").returncode, 0)
        self.assertEqual(sentinel.read_text(), "preserve")
        self.assertEqual(list(self.share.iterdir()), [])

    def test_changed_trial_refuses_removal(self):
        self.assertEqual(self.run_action("apply").returncode, 0)
        unit = self.config / "systemd/user/vetro-early-start-trial.service"
        unit.write_text("owner changed this")
        self.assertNotEqual(self.run_action("remove").returncode, 0)
        self.assertEqual(unit.read_text(), "owner changed this")
        self.assertTrue((self.share / "vetro-early-start-trial/.trial-owned").exists())

    def test_other_added_unit_survives_removal(self):
        self.assertEqual(self.run_action("apply").returncode, 0)
        other = self.config / "systemd/user/other.service"
        other.write_text("preserve")
        self.assertEqual(self.run_action("remove").returncode, 0)
        self.assertEqual(other.read_text(), "preserve")

    def test_symlink_config_is_refused(self):
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        (self.config / "systemd").symlink_to(elsewhere, target_is_directory=True)
        self.assertNotEqual(self.run_action("apply").returncode, 0)
        self.assertEqual(list(elsewhere.iterdir()), [])
        self.assertEqual(list(self.share.iterdir()), [])

    def test_changed_parent_symlink_stops_removal(self):
        self.assertEqual(self.run_action("apply").returncode, 0)
        original = self.config / "systemd"
        moved = self.root / "moved-config"
        original.rename(moved)
        original.symlink_to(moved, target_is_directory=True)
        self.assertNotEqual(self.run_action("remove").returncode, 0)
        self.assertTrue((moved / "user/vetro-early-start-trial.service").exists())
        self.assertTrue((self.share / "vetro-early-start-trial/.trial-owned").exists())


if __name__ == "__main__":
    unittest.main()
