"""Exercise actual Windows path formatting on every host, without executing games."""
import importlib.util,json,unittest
from pathlib import Path,PureWindowsPath
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('family_paths',ROOT/'scripts/launch_level2_family.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class FamilyManifestPaths(unittest.TestCase):
 def test_windows_path_constants_match_exact_posix_manifest(self):
  document=json.loads((ROOT/module.MANIFEST).read_text())
  expected={entry['path'] for entry in document['files']}
  self.assertEqual(len(expected),52)
  # This really emits backslashes with str(), unlike host Path on Linux.
  windows_family=PureWindowsPath(module.FAMILY_ROOT.as_posix())
  windows_reused=PureWindowsPath(module.REUSED_ROOT.as_posix())
  self.assertIn('\\',str(windows_family))
  with patch.object(module,'FAMILY_ROOT',windows_family),patch.object(module,'REUSED_ROOT',windows_reused):
   actual=module.expected_asset_paths()
   self.assertEqual(actual,expected)
   self.assertFalse(any('\\' in name for name in actual))
   # Real asset hashes and exact-set check still run; only constants use Windows paths.
   self.assertEqual(module.verify_assets(ROOT),52)
 def test_native_path_constants_still_match_exact_manifest(self):
  expected={entry['path'] for entry in json.loads((ROOT/module.MANIFEST).read_text())['files']}
  self.assertEqual(module.expected_asset_paths(),expected)
  self.assertEqual(module.verify_assets(ROOT),52)
if __name__=='__main__':unittest.main()
