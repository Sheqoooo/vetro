import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import native_start_trial as trial


class NativeTrialTests(unittest.TestCase):
    def setUp(self):
        project = Path(__file__).resolve().parents[2]
        self.temp = tempfile.TemporaryDirectory(dir=project / "recovery/private/tool-tmp")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "home/owner/.config"
        self.config.mkdir(parents=True)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        shim = self.bin / "sha256sum"
        shim.write_text("#!/Library/Developer/CommandLineTools/usr/bin/python3\nimport hashlib,sys\nfrom pathlib import Path\nprint(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()+'  '+sys.argv[1])\n")
        shim.chmod(0o700)
        self.env = dict(os.environ, PATH=str(self.bin) + ":/usr/bin:/bin")

    def run_action(self, action):
        return subprocess.run(["/bin/sh"], input=trial.build(action, str(self.root)),
                              capture_output=True, text=True, env=self.env)

    def test_roundtrip(self):
        self.assertEqual(self.run_action("apply").returncode, 0)
        user = self.config / "systemd/user"
        for name, content in trial.FILES.items():
            self.assertEqual((user / name).read_bytes(), content)
        self.assertEqual(os.readlink(user / ("default.target.wants/" + trial.NAME + ".timer")),
                         "../" + trial.NAME + ".timer")
        self.assertEqual(self.run_action("remove").returncode, 0)
        self.assertEqual(list(self.config.iterdir()), [])

    def test_refuses_existing_config(self):
        root = self.config / "systemd"
        root.mkdir()
        (root / "foreign").write_text("preserve")
        self.assertNotEqual(self.run_action("apply").returncode, 0)
        self.assertEqual(list(root.iterdir()), [root / "foreign"])

    def test_changed_file_prevents_any_removal(self):
        self.assertEqual(self.run_action("apply").returncode, 0)
        user = self.config / "systemd/user"
        (user / (trial.NAME + ".timer")).write_text("changed")
        self.assertNotEqual(self.run_action("remove").returncode, 0)
        self.assertTrue((user / ("." + trial.NAME)).exists())

    def test_foreign_file_survives(self):
        self.assertEqual(self.run_action("apply").returncode, 0)
        foreign = self.config / "systemd/user/foreign.service"
        foreign.write_text("preserve")
        self.assertEqual(self.run_action("remove").returncode, 0)
        self.assertEqual(foreign.read_text(), "preserve")

    def test_parent_link_refuses_apply(self):
        target = self.root / "elsewhere"
        target.mkdir()
        (self.config / "systemd").symlink_to(target)
        self.assertNotEqual(self.run_action("apply").returncode, 0)
        self.assertEqual(list(target.iterdir()), [])

    def test_swapped_link_refuses_remove(self):
        self.assertEqual(self.run_action("apply").returncode, 0)
        original = self.config / "systemd"
        moved = self.root / "moved"
        original.rename(moved)
        original.symlink_to(moved)
        self.assertNotEqual(self.run_action("remove").returncode, 0)
        self.assertTrue((moved / "user" / ("." + trial.NAME)).exists())


if __name__ == "__main__":
    unittest.main()
