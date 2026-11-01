"""Finite runtime-row admission and explicit metadata propagation checks."""
import pathlib,sys,copy,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import current_projectile_animated153_compatibility as c
class Rows(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.expected=c.load(ROOT)
 def manifest(self):return {'files':[dict(r,group='gameplay',revision=c.REVISION)for r in self.expected.values()]}
 def check(self,m,required=True):
  # Derivation separately tested once; matrix isolates admission without
  # re-running expensive Pillow regeneration for every metadata mutation.
  with patch.object(c,'load',return_value=self.expected):return c.validate_runtime_rows(ROOT,m,required)
 def test_valid(self):self.check(self.manifest())
 def test_absent_optional_not_canonical(self):self.check({'files':[]},False)
 def test_membership(self):
  m=self.manifest()
  for rows in ([],m['files'][:-1],m['files']+[m['files'][0]],m['files']+[dict(m['files'][0],destination='extra.hda')]):
   with self.assertRaises(ValueError):self.check({'files':rows})
 def test_required_metadata(self):
  for key in ('identity','density','encoding'):
   m=self.manifest();del m['files'][0][key]
   with self.assertRaises(ValueError):self.check(m)
 def test_wrong_metadata(self):
  for key,values in {'identity':[True,False,1570152,1560007,'1570153'],'density':[True,4,'8'],'encoding':['rgba',None],'revision':['other',None],'source_path':['elsewhere.hda'],'destination':['elsewhere.hda'],'sha256':['0'*64],'group':['other']}.items():
   for value in values:
    m=self.manifest();m['files'][0][key]=value
    with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.check(m)
 def test_hidden_namespace_collision(self):
  for ident in (1570000,1570153,1579999):
   m=self.manifest();m['files'].append(dict(identity=ident,source_path='unrelated.hda',destination='unrelated.hda'))
   with self.assertRaises(ValueError):self.check(m)
  with self.assertRaises(ValueError):self.check({'files':[dict(identity=1570153,source_path='hidden.hda',destination='hidden.hda')]},False)
 def test_rebuilder_copies_metadata(self):
  s=(ROOT/'scripts/rebuild_recovered_runtime_manifest.py').read_text();self.assertIn("rows[destination].update(animated153_metadata(row))",s)
  self.assertTrue((ROOT/'scripts/package_runtime.py').stat().st_mode&0o100)
if __name__=='__main__':unittest.main()
