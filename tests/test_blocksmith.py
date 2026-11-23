import tempfile
import unittest
from pathlib import Path
from blocksmith import generate, safe_name


class BlockSmithTests(unittest.TestCase):
    def test_name_validation(self):
        self.assertEqual(safe_name("Copper Tools"), "copper_tools")
        with self.assertRaises(ValueError):
            safe_name("../bad")

    def test_generates_linked_manifests(self):
        with tempfile.TemporaryDirectory() as folder:
            bp, rp = generate("demo", Path(folder))
            self.assertTrue((bp / "manifest.json").exists())
            self.assertTrue((rp / "manifest.json").exists())
            self.assertTrue((bp / "items" / "sample_item.json").exists())


if __name__ == "__main__":
    unittest.main()
