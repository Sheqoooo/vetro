import io
from pathlib import Path
import tarfile
import tempfile
import unittest

from install_locked_signer import archive_files


class ArchiveTests(unittest.TestCase):
    def run_archive(self, name, kind=tarfile.REGTYPE):
        project = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(dir=project / "recovery/private/tool-tmp") as tmp:
            archive = Path(tmp) / "fixture.tgz"
            with tarfile.open(archive, "w:gz") as t:
                entry = tarfile.TarInfo(name)
                entry.type = kind
                if kind == tarfile.SYMTYPE:
                    entry.linkname = "../../outside"
                entry.size = 2 if kind == tarfile.REGTYPE else 0
                t.addfile(entry, io.BytesIO(b"ok") if entry.size else None)
            return archive_files(archive)

    def test_regular_file(self):
        self.assertEqual(self.run_archive("package/lib/a.js"), {"lib/a.js": b"ok"})

    def test_traversal(self):
        with self.assertRaises(ValueError):
            self.run_archive("package/../../outside")

    def test_absolute_path(self):
        with self.assertRaises(ValueError):
            self.run_archive("/absolute/outside")

    def test_symlink(self):
        with self.assertRaises(ValueError):
            self.run_archive("package/link", tarfile.SYMTYPE)

    def test_device_node(self):
        with self.assertRaises(ValueError):
            self.run_archive("package/device", tarfile.CHRTYPE)


if __name__ == "__main__":
    unittest.main()
