"""Finite executable inverse for the one reviewed soft-alpha underlay guard."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import accepted_later_changes as proof
class SoftSourceBoundary(unittest.TestCase):
 def test_exact_one_module_inverse_retains_old_pin(self):
  name='src/global_newshf_mirror.inc';ledger=proof.load('newshf168-soft-alpha-source.json')
  self.assertEqual(set(ledger['files']),{name})
  self.assertEqual(ledger['integration_base'],'0112ec8d3c3fd0b6145463b85a713a79ccd01ac5')
  raw=(proof.ROOT/name).read_bytes();old=proof._project_source_once('newshf168-soft-alpha',name,raw)
  self.assertEqual(proof.sha(old),proof.load('newshf-compositor-source.json')['added_sources'][name])
  self.assertIn(b'if(!a[3]&&foreign)',old)
  self.assertIn(b'if(a[3]<255&&foreign)',raw)
 def test_current_guard_mutation_rejected(self):
  name='src/global_newshf_mirror.inc';raw=(proof.ROOT/name).read_bytes()
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'src').mkdir();path=root/name
   for invalid in (raw+b'\n',raw.replace(b'a[3]<255&&foreign',b'!a[3]&&foreign')):
    path.write_bytes(invalid)
    with self.assertRaisesRegex(AssertionError,'compositor module'):proof.verified_newshf_compositor_sources(root)
   path.write_bytes(raw);self.assertEqual(proof.verified_newshf_compositor_sources(root),proof.verified_newshf_compositor_sources())
 def test_extra_soft_executable_scope_rejected(self):
  original=proof.load;ledger=copy.deepcopy(original('newshf168-soft-alpha-source.json'))
  ledger['files']['src/unapproved.c']=copy.deepcopy(next(iter(ledger['files'].values())))
  with patch.object(proof,'load',side_effect=lambda name:ledger if name=='newshf168-soft-alpha-source.json' else original(name)):
   with self.assertRaisesRegex(AssertionError,'soft-alpha module scope'):proof.verified_newshf_compositor_sources()
if __name__=='__main__':unittest.main()
