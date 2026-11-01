"""Finite byte-copy alias checks, no artwork generation or native execution."""
from pathlib import Path
import copy,hashlib,importlib.util,json,struct,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('orb_protron_aliases',ROOT/'scripts/current_enemy_orb_protron_aliases.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class AliasContract(unittest.TestCase):
 def manifest(self):return {'files':a.rows_for(ROOT)}
 def test_exact_four_bytes_headers_paths(self):
  blobs=a.generate(ROOT);self.assertEqual(len(blobs),4);self.assertEqual(sum(map(len,blobs.values())),172144)
  for i,pin in a.SPECS.items():
   raw=blobs[a.PREFIX+pin+'.hda'];self.assertEqual(raw,(ROOT/a.canonical_source(i)).read_bytes());self.assertEqual(raw,(ROOT/(a.PREFIX+pin+'.hda')).read_bytes());self.assertEqual(struct.unpack('<4s6I',raw[:28]),(b'HDR1',a.IDENTITIES[i],8,12,14,0,0))
 def test_deterministic_byte_copy_rows(self):
  self.assertEqual(a.generate(ROOT),a.generate(ROOT));self.assertEqual(a.rows_for(ROOT),a.rows_for(ROOT));self.assertEqual([r['destination']for r in a.rows_for(ROOT)],sorted(r['destination']for r in a.rows_for(ROOT)))
 def test_valid_exact_rows(self):a.validate_runtime_rows(ROOT,self.manifest(),True)
 def test_missing_each_rejected(self):
  for n in range(4):
   m=self.manifest();m['files'].pop(n)
   with self.subTest(n=n),self.assertRaises(ValueError):a.validate_runtime_rows(ROOT,m,True)
 def test_duplicate_each_rejected(self):
  for n in range(4):
   m=self.manifest();m['files'].append(dict(m['files'][n]))
   with self.subTest(n=n),self.assertRaises(ValueError):a.validate_runtime_rows(ROOT,m,True)
 def test_extra_family_row_rejected(self):
  m=self.manifest();r=dict(m['files'][0]);r.update(destination='assets/global/content/extra.hda',source_path='extra.hda',identity=80126);m['files'].append(r)
  with self.assertRaises(ValueError):a.validate_runtime_rows(ROOT,m,True)
 def test_strict_metadata_mutations(self):
  values={'identity':[True,False,80022,'80020',None],'density':[True,4,'8',None],'encoding':['indexed',None],'source_path':['other.hda'],'destination':['assets/global/content/extra.hda'],'canonical_source':['other.hda'],'revision':['other',None],'group':['gameplay'],'sha256':['0'*64],'git_blob':['0'*40],'bytes':[True,43035]}
  for key,vals in values.items():
   for value in vals:
    m=self.manifest();m['files'][0][key]=value
    with self.subTest(key=key,value=value),self.assertRaises(ValueError):a.validate_runtime_rows(ROOT,m,True)
 def test_missing_metadata_fields_rejected(self):
  for key in self.manifest()['files'][0]:
   m=self.manifest();del m['files'][0][key]
   with self.subTest(key=key),self.assertRaises(ValueError):a.validate_runtime_rows(ROOT,m,True)
 def test_extra_metadata_rejected(self):
  m=self.manifest();m['files'][0]['unknown']=1
  with self.assertRaises(ValueError):a.validate_runtime_rows(ROOT,m,True)
 def test_hidden_identity_collision(self):
  for i in a.SPECS:
   m=self.manifest();m['files'].append(dict(identity=a.IDENTITIES[i],source_path='unrelated.hda',destination='unrelated.hda'))
   with self.subTest(i=i),self.assertRaises(ValueError):a.validate_runtime_rows(ROOT,m,True)
 def fixture(self,root):
  for i,pin in a.SPECS.items():
   for name in (a.canonical_source(i),a.PREFIX+pin+'.hda'):
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
 def test_hidden_header_collision_without_metadata(self):
  with tempfile.TemporaryDirectory()as td:
   r=Path(td);self.fixture(r);p=r/'hidden.hda';p.write_bytes((ROOT/a.canonical_source(112)).read_bytes());m=self.manifest();m['files'].append(dict(source_path='hidden.hda',destination='elsewhere.hda',sha256='0'*64))
   with self.assertRaises(ValueError):a.validate_runtime_rows(r,m,True)
 def test_corrupt_alias_or_canonical_source_rejected(self):
  with tempfile.TemporaryDirectory()as td:
   r=Path(td);self.fixture(r)
   for i,pin in a.SPECS.items():
    for name in (a.canonical_source(i),a.PREFIX+pin+'.hda'):
     p=r/name;raw=p.read_bytes();bad=bytearray(raw);bad[-1]^=1;p.write_bytes(bad)
     with self.subTest(name=name),self.assertRaises(ValueError):a.load(r)
     p.write_bytes(raw)
 def test_optional_absent_and_required_absent(self):
  a.validate_runtime_rows(ROOT,{'files':[]},False)
  with self.assertRaises(ValueError):a.validate_runtime_rows(ROOT,{'files':[]},True)
 def test_manual_consumers_unmodified_and_collision_closed(self):
  m=self.manifest();old=json.loads((ROOT/'packaging/runtime-assets-v1.json').read_text());manual=[r for r in old['files']if r['source_path']in {a.canonical_source(i)for i in a.SPECS}];self.assertEqual(len(manual),2);m['files']+=manual;a.validate_runtime_rows(ROOT,m,True)
  for key,val in [('identity',80020),('destination','elsewhere.hda')]:
   bad=copy.deepcopy(m);bad['files'][4][key]=val
   with self.assertRaises(ValueError):a.validate_runtime_rows(ROOT,bad,True)
 def test_no_image_conversion_and_explicit_integration(self):
  s=(ROOT/'scripts/current_enemy_orb_protron_aliases.py').read_text();self.assertNotIn('PIL',s);self.assertNotIn('Image',s)
  self.assertIn('from current_enemy_orb_protron_aliases import validate_runtime_rows',(ROOT/'scripts/package_runtime.py').read_text());self.assertIn('from current_enemy_orb_protron_aliases import load',(ROOT/'scripts/rebuild_recovered_runtime_manifest.py').read_text())
if __name__=='__main__':unittest.main()
