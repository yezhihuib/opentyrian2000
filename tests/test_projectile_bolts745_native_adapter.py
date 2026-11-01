"""Pure preparatory tests only: never compile, launch a process or run a game."""
from pathlib import Path
import ast,copy,importlib.util,os,struct,tempfile,unittest
P=Path(__file__).parent
spec=importlib.util.spec_from_file_location('bolts745_native',P/'projectile_bolts745_native_validation.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
ROOT=Path(os.environ.get('BOLTS745_TEST_ROOT',str(P.parent)))
class Bolts745NativeAdapter(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=h.pulses_helper(ROOT);cls.sources,cls.wrapper=h.source_bundle(ROOT);cls.hdas=h.registered_hdas(ROOT)
 def bad(self,fn,*args):
  with self.assertRaises((ValueError,AssertionError,TypeError,KeyError)):fn(*args)
 def test_inherited_six_sources_exact(self):
  self.assertEqual(len(self.sources),6)
  self.assertEqual({n:h.sha(b)for n,b in self.sources.items()},self.old.SOURCE_PINS)
 def test_wrapper_exact_inverse(self):
  old=self.old.source_bundle(ROOT)[1];self.assertEqual(h.reverse_shim(self.wrapper),old);self.assertEqual(h.outer_shim(old),self.wrapper)
 def test_wrapper_tail_and_inner_mutations_rejected(self):
  self.bad(h.reverse_shim,self.wrapper+b' ')
  self.bad(h.reverse_shim,self.wrapper.replace(b'inherited_pulses_dispatch',b'other_dispatch',1))
  self.bad(h.outer_shim,h.reverse_shim(self.wrapper)+b' ')
 def test_wrapper_only_new_main_dispatches_new_option(self):
  self.assertEqual(self.wrapper.count(b'int main('),1)
  self.assertIn(b'--enemy-bolts745',h.TAIL);self.assertIn(b'return inherited_pulses_dispatch(argc,argv);',h.TAIL)
 def test_no_self_approved_companion(self):
  self.bad(h.companion_bytes,ROOT,None);self.bad(h.companion_bytes,ROOT,'0'*64)
 def test_old12_current_payload_pins(self):
  self.assertEqual(tuple(h.OLD_HDA),h.IDS[:12])
  for i,row in h.OLD_HDA.items():self.assertEqual(h.sha(self.hdas[i]),row['sha256'])
  self.assertEqual(self.old.registered_hdas(ROOT),{i:self.hdas[i]for i in (166,94)})
 def test_new2_indexed_transport(self):
  c=h.authoring_helper(ROOT)
  for i in (7,45):
   self.assertTrue(c.validate_hda(ROOT,1560000+i,self.hdas[i]));self.assertEqual(self.hdas[i][31::4].count(255),4029)
 def test_exact14_selector_keys(self):
  self.assertEqual(tuple(self.hdas),h.IDS);self.assertTrue(h.validate_hdas(ROOT,self.hdas))
 def test_forged_old_and_new_payload_rejected(self):
  for i in (91,166,7,45):
   d=dict(self.hdas);p=bytearray(d[i]);p[128]^=1;d[i]=bytes(p);self.bad(h.validate_hdas,ROOT,d)
 def test_selector_float_bool_extra_missing_rejected(self):
  for key in (7.0,True,'7'):
   d=dict(self.hdas);d.pop(7);d[key]=self.hdas[7];self.bad(h.validate_hdas,ROOT,d)
  d=dict(self.hdas);d[8]=d[7];self.bad(h.validate_hdas,ROOT,d)
  d=dict(self.hdas);d.pop(45);self.bad(h.validate_hdas,ROOT,d)
 def test_fixture35_packs_476_files(self):
  schema=h.fixture_schema();self.assertEqual(len(schema),35);self.assertEqual(sum(map(len,schema.values())),476)
  fixtures=h.fixture_payloads(ROOT,self.hdas);self.assertEqual(len(fixtures),476);self.assertEqual(sum(map(len,fixtures.values())),476*43036)
 def test_fixture_missing_only_target(self):
  for i in (7,45):
   self.assertEqual(h.fixture_schema()['missing'+str(i)],tuple(k for k in h.IDS if k!=i))
   self.assertIsNone(h.fixture_bytes(self.hdas[i],i,'missing'+str(i)))
 def test_fixture_non_target_bytes_unchanged(self):
  for leaf in h.PACK_NAMES:
   for i in h.IDS:
    if leaf=='valid' or not leaf.endswith(str(i)):self.assertEqual(h.fixture_bytes(self.hdas[i],i,leaf),self.hdas[i])
 def test_missing_each_old_keeps_new_pair(self):
  schema=h.fixture_schema()
  for i in h.IDS[:12]:
   leaf='missing'+str(i);self.assertEqual(schema[leaf],tuple(j for j in h.IDS if j!=i));self.assertIsNone(h.fixture_bytes(self.hdas[i],i,leaf))
   for new in (7,45):self.assertEqual(h.fixture_bytes(self.hdas[new],new,leaf),self.hdas[new])
 def test_fixture_bad_one_byte(self):
  for i in (7,45):
   raw=self.hdas[i];changed=h.fixture_bytes(raw,i,'bad'+str(i));self.assertEqual([j for j,(a,b)in enumerate(zip(raw,changed))if a!=b],[128])
 def test_fixture_each_header_field(self):
  c=h.authoring_helper(ROOT)
  for i in (7,45):
   for kind,off in (('header',4),('magic',0),('density',8),('width',12),('height',16),('anchorx',20),('anchory',24)):
    changed=h.fixture_bytes(self.hdas[i],i,kind+str(i));self.assertNotEqual(changed,self.hdas[i]);self.assertEqual(changed[28:],self.hdas[i][28:]);self.bad(c.validate_hda,ROOT,1560000+i,changed)
 def test_fixture_short_trailing(self):
  for i in (7,45):
   self.assertEqual(h.fixture_bytes(self.hdas[i],i,'short'+str(i)),self.hdas[i][:-1]);self.assertEqual(h.fixture_bytes(self.hdas[i],i,'trailing'+str(i)),self.hdas[i]+b'!')
 def test_fixture_unbounded_unknown_and_wrong_types_rejected(self):
  for leaf in ('../valid','VALID','valid/..','missing8',b'valid'):
   self.bad(h.fixture_bytes,self.hdas[7],7,leaf)
  for selector in (7.0,True,'7',8):self.bad(h.fixture_bytes,self.hdas[7],selector,'valid')
  for raw in (self.hdas[7][:-1],bytearray(self.hdas[7])):self.bad(h.fixture_bytes,raw,7,'valid')
 def test_inherited1241_fixture_bytes_unchanged(self):
  current=h.inherited_fixture_payloads(ROOT,self.hdas);old=self.old.fixture_payloads(ROOT,{i:self.hdas[i]for i in self.old.IDS},self.old.registration(ROOT));self.assertEqual(current,old);self.assertEqual(len(current),1241)
 def test_preparation_metadata_not_native_pass(self):
  m=h.preparation_metadata(ROOT,self.hdas);self.assertEqual(m['status'],'PREPARED_ONLY_NOT_EXECUTED');self.assertEqual(m['new_fixture_count'],476);self.assertEqual(m['encoding'],h.ENCODING);self.assertIn('not self-approved',m['companion_status'])
 def test_pure_helper_has_no_process_or_write_calls(self):
  raw=(ROOT/'tests/projectile_bolts745_native_validation.py').read_text();tree=ast.parse(raw)
  forbidden={'subprocess','Popen','system','run','write_bytes','write_text','unlink','mkdir','open'}
  calls={getattr(n.func,'attr',getattr(n.func,'id',None))for n in ast.walk(tree)if isinstance(n,ast.Call)}
  self.assertFalse(calls&forbidden);self.assertFalse(any(isinstance(n,(ast.For,ast.While,ast.With))for n in tree.body))
 def test_input_adapter_delegates_unchanged_palette5_recipe(self):
  raw=(ROOT/'tests/projectile_bolts745_native_validation.py').read_text();self.assertIn('old.pulses_native_input(root,data,new)',raw);self.assertIn('old.native_inputs(root,data)',raw);self.assertIn("len(current)!=98980",raw)
 def test_checked_file_rejects_symlink_hardlink_mutation(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'a';p.write_bytes(b'abc');self.assertEqual(h.checked_file(p,h.sha(b'abc')),b'abc');self.bad(h.checked_file,p,'0'*64)
   q=Path(d)/'b';q.symlink_to(p);self.bad(h.checked_file,q);q.unlink();os.link(p,q);self.bad(h.checked_file,p)

if __name__=='__main__':unittest.main()
