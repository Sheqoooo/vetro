"""Offline checks; fixtures stay inside this project's recovery directory."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

import backup_exports as kit


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.original = kit.ROOT
        self.temp = tempfile.TemporaryDirectory(prefix=".test-", dir=str(self.original))
        kit.ROOT = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(setattr, kit, "ROOT", self.original)
        (kit.ROOT / "inbox").mkdir()
        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)

    def exports(self):
        for name in kit.NAMES:
            payload = {"fixture": True}
            if name == "device.json":
                payload = {"model": "TEST-DEVICE", "firmware": "TEST-FIRMWARE",
                           "source_revision": "a" * 40,
                           "stage": "after-install-before-user-changes"}
            (kit.ROOT / "inbox" / name).write_text(json.dumps(payload))

    def snapshot(self):
        kit.capture()
        return next((kit.ROOT / "private").iterdir())

    def test_roundtrip_and_private_permissions(self):
        self.exports()
        snap = self.snapshot()
        kit.verify(str(snap.relative_to(kit.ROOT)))
        self.assertEqual((snap / "status.json").stat().st_mode & 0o777, 0o600)
        self.assertEqual(snap.stat().st_mode & 0o777, 0o700)

    def test_missing_export_creates_no_snapshot(self):
        self.exports()
        (kit.ROOT / "inbox/status.json").unlink()
        with self.assertRaises(ValueError):
            kit.capture()
        self.assertFalse((kit.ROOT / "private").exists())

    def test_error_response_is_not_a_backup(self):
        self.exports()
        (kit.ROOT / "inbox/status.json").write_text('{"error":"no-root-agent"}')
        with self.assertRaises(ValueError):
            kit.capture()

    def test_symlink_refused(self):
        self.exports()
        path = kit.ROOT / "inbox/status.json"
        path.unlink()
        path.symlink_to(kit.ROOT / "inbox/dock.json")
        with self.assertRaises(ValueError):
            kit.capture()

    def test_path_escape_refused(self):
        with self.assertRaises(ValueError):
            kit.verify("../outside")

    def test_detects_valid_json_changed_after_capture(self):
        self.exports()
        snap = self.snapshot()
        (snap / "dock.json").write_text('{"fixture":false}')
        with self.assertRaises(ValueError):
            kit.verify(str(snap.relative_to(kit.ROOT)))

    def test_incomplete_manifest_refused(self):
        self.exports()
        snap = self.snapshot()
        p = snap / "manifest.json"
        manifest = json.loads(p.read_text())
        del manifest["files"]["dock.json"]
        p.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            kit.verify(str(snap.relative_to(kit.ROOT)))

    def test_wont_overwrite_backup(self):
        target = kit.ROOT / "existing.json"
        target.write_bytes(b"original")
        with self.assertRaises(FileExistsError):
            kit.private_write(target, b"replacement")
        self.assertEqual(target.read_bytes(), b"original")

    def test_pre_root_claim_refused(self):
        self.exports()
        p = kit.ROOT / "inbox/device.json"
        d = json.loads(p.read_text())
        d["stage"] = "before-root"
        p.write_text(json.dumps(d))
        with self.assertRaises(ValueError):
            kit.capture()

    def test_oversize_export_refused(self):
        self.exports()
        (kit.ROOT / "inbox/status.json").write_bytes(b" " * (kit.LIMIT + 1))
        with self.assertRaises(ValueError):
            kit.capture()


if __name__ == "__main__":
    unittest.main()
