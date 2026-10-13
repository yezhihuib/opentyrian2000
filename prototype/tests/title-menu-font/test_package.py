#!/usr/bin/env python3
"""Finite TMF1 packaging/source reproduction gates; never launches the game."""
from pathlib import Path
import hashlib,json,shutil,struct,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'prototype'))
import title_menu_font_bundle as bundle
class Package(unittest.TestCase):
 def test_aggregate_block_outputs_only_six(self):
  from types import SimpleNamespace
  text=(ROOT/'prototype/build-hd-assets.py').read_text()
  block=text[text.index('title_menu_count=0\n'):text.index('type4_count=0\n')]
  with tempfile.TemporaryDirectory(prefix='tmf1-aggregate-block-') as tmp:
   namespace={'repo':ROOT,'manifest':json.loads((ROOT/'assets/hd/manifest.json').read_text()),'a':SimpleNamespace(output=True),'output':Path(tmp)}
   exec(compile(block,'build-hd-assets.py:title-menu-only','exec'),namespace)
   self.assertEqual(namespace['title_menu_count'],6);self.assertEqual(namespace['title_menu_source_count'],17)
   self.assertEqual({p.name for p in Path(tmp).iterdir()},{'startup-title-menu-v1'})
   for name,(raw,_) in bundle.build_bundles(ROOT).items():self.assertEqual((Path(tmp)/'startup-title-menu-v1'/name).read_bytes(),raw)
 def test_frozen_source_and_six_resources(self):
  result=bundle.build_bundles(ROOT);self.assertEqual(len(result),6)
  raw,_=result['title-menu-font-v1.hda'];self.assertEqual(len(raw),688256)
  h=struct.unpack('<4s15I8Q',raw[:128]);self.assertEqual(h[:16],(b'TMF1',1,4,896,384,85,76,56,64,4,1,344064,344064,12,15,0))
  self.assertEqual(hashlib.sha256(raw).hexdigest(),'26e4f9eabed4f90bfe74896e04ee59e647e445ffd44a9feaf003c91444275a4d')
  for name,(data,_) in result.items():
   if name!='title-menu-font-v1.hda':self.assertEqual(data,(ROOT/'assets/hd/packs/startup-title-v1'/name).read_bytes())
 def test_manifest_preservation(self):
  actual=json.loads((ROOT/'assets/hd/manifest.json').read_text())
  from type3_small_coexistence import project_type3_small_family
  from settings_font_coexistence import project_settings_family
  project_settings_family(self, actual)
  project_type3_small_family(self,actual)
  family=actual.pop('startup_title_menu_v1')
  before=json.loads(subprocess.check_output(['git','show','e6fd18a8d53c31f90d15c0ac1bce9d0e927336ac:assets/hd/manifest.json'],cwd=ROOT))
  self.assertEqual(actual,before);self.assertEqual(family['runtime_bytes'],15994352)
 def test_relocated_vector_only_rebuild(self):self.assertTrue(bundle.verify_source_rebuild(ROOT))
 def test_changed_source_rejected(self):
  with tempfile.TemporaryDirectory(prefix='tmf1-package-') as tmp:
   source=Path(tmp)/'source';shutil.copytree(ROOT/bundle.SOURCE,source)
   file=source/'canonical/title-menu-font-v1.hda';raw=bytearray(file.read_bytes());raw[-1]^=1;file.write_bytes(raw)
   with self.assertRaises(ValueError):bundle.build_resource(source)
 def test_inventory_and_paths_rejected(self):
  with tempfile.TemporaryDirectory(prefix='tmf1-inventory-') as tmp:
   source=Path(tmp)/'source';shutil.copytree(ROOT/bundle.SOURCE,source);(source/'unexpected.txt').write_text('reject')
   with self.assertRaises(ValueError):bundle.source_receipts(source)
   with self.assertRaises(ValueError):bundle.checked_file(source,'../outside')
   with self.assertRaises(ValueError):bundle.checked_file(source,'/outside')
   (source/'unexpected.txt').unlink();(source/'alias').symlink_to(source/'README.md')
   with self.assertRaises(ValueError):bundle.source_receipts(source)
if __name__=='__main__':unittest.main()
