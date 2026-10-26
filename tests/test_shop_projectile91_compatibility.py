"""Newest finite render extension cannot bless unrelated SHOP or source changes."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
import tempfile
import shutil
from unittest.mock import patch
import shop_current_acceptance as shop
import accepted_later_changes as a

class ShopProjectile91Compatibility(unittest.TestCase):
 def test_positive_without_git_or_private_objects(self):
  with patch.object(subprocess,'Popen',side_effect=AssertionError('No Git/subprocess proof dependency')):
   shop.check_current_inventory()
  raw=shop.INVENTORY.read_bytes()
  self.assertEqual(hashlib.sha256(raw).hexdigest(),'26b7e3b33cba2adfe6fee1aa19f887ff09aa1ed6d438491a3f8c737b738fc102')
  self.assertEqual(len(json.loads(raw)['files']),6404)

 def reject_bytes(self,name,mutate):
  original=Path.read_bytes
  def read(path):
   raw=original(path)
   return mutate(raw) if path==shop.ROOT/name else raw
  with patch.object(Path,'read_bytes',read),self.assertRaises((AssertionError,ValueError)):
   shop.check_current_inventory()

 def test_every_current_source_inverse_rejects_partial_and_newline(self):
  for name,pin in a.current_projectile91_ledger()['files'].items():
   with self.subTest(name=name):
    self.reject_bytes(name,lambda raw:raw+b'\n')
    edit=pin['hunks'][0]
    def partial(raw):
     lines=raw.splitlines(keepends=True);start,end=edit['after_lines']
     lines[start:end]=edit['before'].encode().splitlines(keepends=True)
     return b''.join(lines)
    self.reject_bytes(name,partial)

 def test_new_modules_header_assets_and_master_cannot_hide_drift(self):
  proof=a.verified_current_projectile91()
  names=set(proof['added_sources'])|set(proof['assets'])|{a.CURRENT_PROJECTILE91_HEADER,
    'authoring-inputs/projectile91-current/projectile91-silver-v2-concept.png'}
  self.assertEqual(len(names),7)
  for name in names:
   with self.subTest(name=name):
    self.reject_bytes(name,lambda raw:raw+b'\n')
  self.reject_bytes('assets/hd/authoring/projectile91-current.json',lambda raw:raw.replace(b'"selector": 91',b'"selector": 92'))
  # A semantic role/eligibility mutation is rejected by the whole module pin.
  self.reject_bytes('src/enemy_projectile91_mirror.inc',lambda raw:raw.replace(b'91',b'92',1))

 def test_unknown_and_missing_paths_fail_complete_gate(self):
  original_glob=Path.rglob;original_file=Path.is_file
  for name in ('src/unreviewed.c','assets/unreviewed.hda'):
   extra=shop.ROOT/name
   def paths(path,pattern):
    yield from original_glob(path,pattern)
    if path==extra.parent:yield extra
   with patch.object(Path,'rglob',paths),patch.object(Path,'is_file',lambda p:p==extra or original_file(p)):
    with self.subTest(name=name),self.assertRaisesRegex(AssertionError,'current path inventory drift'):
     shop.check_current_inventory()
  for name in ('src/player.c','assets/hd/manifest.json'):
   def paths(path,pattern):
    yield from (p for p in original_glob(path,pattern) if p!=shop.ROOT/name)
   with patch.object(Path,'rglob',paths):
    with self.subTest(name=name),self.assertRaisesRegex(AssertionError,'current path inventory drift'):
     shop.check_current_inventory()

 def test_unrelated_source_and_original_asset_remain_exact(self):
  for name in ('src/player.c','assets/hd/manifest.json','tests/shop_front_source_delta.json','tests/fixtures/shop_current_acceptance/projectile91-qualified-extension.json'):
   with self.subTest(name=name):self.reject_bytes(name,lambda raw:raw+b'\n')

 def test_real_private_files_mutate_remove_restore_and_reject_symlinks(self):
  proof=a.verified_current_projectile91()
  import current_projectile91_compatibility as c
  from linked_newshf_projection import verified as linked_verified
  names=set(json.loads(shop.INVENTORY.read_bytes())['files'])|proof['paths']|{c.MAPPING}|linked_verified()['paths']
  with tempfile.TemporaryDirectory(prefix='shop91-real-negative-') as tmp:
   root=Path(tmp)
   for name in names:
    destination=root/name;destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(shop.ROOT/name,destination)
   shop.check_current_inventory(root)
   for name in ('src/unreviewed.c','assets/unreviewed.hda'):
    path=root/name;path.write_bytes(b'unapproved')
    with self.subTest(extra=name),self.assertRaises(AssertionError):shop.check_current_inventory(root)
    path.unlink()
   selected=('src/enemy_projectile91_mirror.inc',c.HEADER,c.ROOT+'/'+c.name(c.IDS[0]),
             'src/player.c','authoring-inputs/projectile91-current/projectile91-silver-v2-concept.png')
   for name in selected:
    path=root/name;raw=path.read_bytes()
    path.write_bytes(raw+b'\n')
    with self.subTest(mutated=name),self.assertRaises((AssertionError,ValueError)):shop.check_current_inventory(root)
    path.unlink()
    with self.subTest(missing=name),self.assertRaises((AssertionError,ValueError,FileNotFoundError)):shop.check_current_inventory(root)
    path.write_bytes(raw)
   name='src/global_projectile91_mirror.inc';path=root/name;raw=path.read_bytes();path.unlink()
   path.symlink_to(shop.ROOT/name)
   with self.assertRaises((AssertionError,ValueError)):shop.check_current_inventory(root)
   path.unlink();path.write_bytes(raw)
   # Header role field mutation in the actual generated HDA, not a mocked predicate.
   path=root/(c.ROOT+'/'+c.name(c.IDS[0]));raw=path.read_bytes()
   path.write_bytes(raw[:4]+bytes([raw[4]^1])+raw[5:])
   with self.assertRaises((AssertionError,ValueError)):shop.check_current_inventory(root)
   path.write_bytes(raw);shop.check_current_inventory(root)


if __name__=='__main__':unittest.main()
