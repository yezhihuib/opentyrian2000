"""Finite pure authoring/package checks; not runtime admission or full inventory."""
from pathlib import Path
import ast,contextlib,copy,hashlib,io,json,os,shutil,struct,sys,tempfile,unittest
from unittest import mock
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_projectile_gold_pulse_compatibility as c
import build_current_projectile_gold_pulse as build
from build_current_art import fnv

def copy_inputs(target,paths):
 for name in paths:
  p=target/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
class GoldAuthoring(unittest.TestCase):
 def selected(self):return json.loads((ROOT/c.SELECTION).read_text())
 def rows(self):return [dict(r,group='gameplay',revision=c.REVISION) for r in c.load(ROOT).values()]
 def test_01_two_identity_geometry_and_payload(self):
  self.assertEqual(c.IDS,(1530168,1530169));self.assertEqual(len(c.load(ROOT)),2)
  contract=c.coverage(ROOT)
  for i,s in zip(c.IDS,c.SELECTORS):
   b=(ROOT/c.ROOT/c.name(i)).read_bytes();self.assertEqual(len(b),43036);self.assertEqual(struct.unpack('<4s6I',b[:28]),(b'HDR1',i,8,12,14,0,0));self.assertEqual(c.sha(b[28:]),contract['members'][str(s)]['payload_sha256'])
 def test_02_exact_png_hda_rgba(self):
  for i,s in zip(c.IDS,c.SELECTORS):
   p=ROOT/c.png(i);self.assertEqual(c.sha(p.read_bytes()),c.APPROVED_PNG_SHA256[s])
   with Image.open(p) as im:self.assertEqual((im.mode,im.size),('RGBA',(96,112)));self.assertEqual(im.tobytes(),(ROOT/c.ROOT/c.name(i)).read_bytes()[28:])
 def test_03_full_matrix_and_soft_zero_counts(self):
  for i,s,count,dist,soft,zero in [(1530168,168,97,(72,25,0),5894,314),(1530169,169,69,(45,24,0),3575,841)]:
   raw=(ROOT/c.ROOT/c.name(i)).read_bytes()[28:];matrix=c.validate_payload(ROOT,s,raw);mask=c.MASKS[s];self.assertEqual(mask.count('1'),count)
   vals=[matrix[y][x] for y in range(14) for x in range(12) if mask[y*12+x]=='1'];self.assertEqual((sum(x>=200 for x in vals),sum(0<x<200 for x in vals),vals.count(0)),dist)
   alpha=raw[3::4];self.assertEqual(sum(0<x<255 for x in alpha),soft);self.assertEqual(alpha.count(255),0);self.assertEqual(max(alpha),253)
   self.assertEqual(sum(alpha[y*96+x]==0 for y in range(112) for x in range(96) if mask[(y//8)*12+x//8]=='1'),zero)
 def test_04_canonical_zero_and_mutation_rejection(self):
  for i,s in zip(c.IDS,c.SELECTORS):
   raw=(ROOT/c.ROOT/c.name(i)).read_bytes()[28:]
   for pixel in range(10752):
    q=raw[pixel*4:pixel*4+4]
    if not q[3] or c.MASKS[s][(pixel//96//8)*12+(pixel%96)//8]=='0':self.assertEqual(q,b'\0'*4)
   for offset in [0,3,4*500+3,43007]:
    b=bytearray(raw);b[offset]^=1
    with self.assertRaises(ValueError):c.validate_payload(ROOT,s,b)
 def test_05_fixed_one_master_two_registrations(self):
  self.assertEqual(c.MASTER['source_size'],[1774,887]);self.assertEqual([r['crop'] for r in c.MEMBERS],[[0,0,887,887],[887,0,1774,887]])
  self.assertEqual([r['resize'] for r in c.MEMBERS],[[88,88],[72,72]]);self.assertEqual([r['paste'] for r in c.MEMBERS],[[0,8],[8,16]])
 def test_06_rebuild_exact_six_products(self):
  out=build.products(ROOT);self.assertEqual(len(out),6)
  for name,b in out.items():self.assertEqual((ROOT/name).read_bytes(),b)
 def test_07_fnv_known_vectors_and_production_body(self):
  for b,h in [(b'','cbf29ce484222325'),(b'a','af63dc4c8601ec8c'),(b'foobar','85944171f73967e8'),(b'hello','a430d84680aabd0b')]:self.assertEqual(fnv(b),h)
  body=(ROOT/'src/asteroid1_ten_mirror.inc').read_text().split('static uint64_t asteroid1_stamp(const Uint8 *p,size_t n)\n{',1)[1].split('\n}',1)[0]
  self.assertEqual(''.join(body.split()),'uint64_th=UINT64_C(0xcbf29ce484222325);while(n--){h^=*p++;h*=UINT64_C(0x100000001b3);}returnh;')
 def test_08_previous_wrong_seed_rejected(self):
  for i,s,bad,want in [(1530168,168,'3c67e6ba5df9969b','d35eb01e52fbf3a5'),(1530169,169,'1466e2a48aaea145','28baab1d924b1433')]:
   payload=(ROOT/c.ROOT/c.name(i)).read_bytes()[28:];self.assertEqual(fnv(payload),want);self.assertNotEqual(fnv(payload),bad)
   contract=copy.deepcopy(c.coverage(ROOT));contract['members'][str(s)]['payload_fnv']=bad
   with self.assertRaises(ValueError):c.validate_payload(ROOT,s,payload,contract)
 def test_09_identity_density_closed(self):
  for i,d in [(168,8),(1530167,8),(True,8),(1530168,True),(1530168,4),(1530168,8.0),('1530168',8)]:
   with self.subTest(i=i,d=d),self.assertRaises(ValueError):c.name(i,d)
 def test_10_schema_extra_missing_and_candidate(self):
  j=self.selected()
  for k in j:
   bad=copy.deepcopy(j);del bad[k]
   with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(bad).encode())
  bad=copy.deepcopy(j);bad['extra']=1
  with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(bad).encode())
  bad=copy.deepcopy(j);bad['schema']=c.CANDIDATE_SCHEMA
  self.assertEqual(c.selection(ROOT,json.dumps(bad).encode(),True)['members'],j['members'])
  with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(bad).encode())
  with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(j).encode(),1)
 def test_11_duplicate_nan_oversize_rejected(self):
  b=(ROOT/c.SELECTION).read_bytes()
  for bad in [b.replace(b'"version":',b'"version":"shadow","version":',1),b.replace(b'1774',b'NaN'),b' '*131073]:
   with self.assertRaises(ValueError):c.selection(ROOT,bad)
 def test_12_master_path_sha_type_drift(self):
  for key,value in [('source_png','../private-reference.png'),('source_png','/tmp/raw.png'),('source_png',c.MASTER['source_png'].upper()),('source_sha256','0'*64),('prompt_sha256',True),('source_size',[True,887]),('source_size',[1774.0,887])]:
   j=self.selected();j['master'][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):c.selection(ROOT,json.dumps(j).encode())
 def test_13_member_cardinality_order_and_field_types(self):
  for value in [[],{},[True,True],list(reversed(c.MEMBERS)),c.MEMBERS[:1],c.MEMBERS+c.MEMBERS[:1]]:
   j=self.selected();j['members']=value
   with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(j).encode())
  for n in range(2):
   for key,value in [('selector',True),('selector',float(c.SELECTORS[n])),('crop',[False,0,887,887]),('resize',[88.0,88]),('paste',[0]),('png_compress_level',True),('png_compress_level',9)]:
    j=self.selected();j['members'][n][key]=value
    with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(j).encode())
 def test_14_fixed_inputs_missing_changed_symlink_hardlink(self):
  paths={c.MASTER['source_png'],c.MASTER['prompt_path'],c.REGISTRATION,c.COVERAGE};raw=(ROOT/c.SELECTION).read_bytes()
  with tempfile.TemporaryDirectory() as td:
   t=Path(td);copy_inputs(t,paths)
   for name in sorted(paths):
    p=t/name;original=p.read_bytes();p.unlink()
    with self.assertRaises((ValueError,OSError)):c.selection(t,raw)
    p.write_bytes(original+b'x')
    with self.assertRaises(ValueError):c.selection(t,raw)
    p.unlink();p.symlink_to(ROOT/name)
    with self.assertRaises(ValueError):c.selection(t,raw)
    p.unlink();p.write_bytes(original);link=t/'linked';os.link(p,link)
    with self.assertRaises(ValueError):c.selection(t,raw)
    link.unlink();c.selection(t,raw)
 def test_15_complete_two_consumer_package(self):
  rows=self.rows();c.validate_runtime_rows(ROOT,{'files':rows},True);c.validate_runtime_rows(ROOT,{'files':rows},False)
  c.validate_runtime_rows(ROOT,{'files':rows+[{'source_path':'other','destination':'other'}]},True)
 def test_16_missing_duplicate_and_alias_package(self):
  rows=self.rows()
  for bad in [[],rows[:1],rows+rows[:1]]:
   with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':bad},True)
  for n in range(2):
   for key,value in [('destination',rows[n]['destination'].upper()),('source_path','elsewhere/'+c.name(c.IDS[n])),('sha256','0'*64),('group','old'),('revision','old')]:
    bad=copy.deepcopy(rows);bad[n][key]=value
    with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':bad},True)
 def test_17_foreign_alias_and_container_types(self):
  for suffix in ['999-8.hda','168-4.hda']:
   alias={'source_path':'elsewhere/enemy-projectile-gold-pulse-'+suffix,'destination':'elsewhere/enemy-projectile-gold-pulse-'+suffix}
   with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':self.rows()+[alias]},False)
  for bad in [None,{}, {'files':True},{'files':[True]},{'files':[{'source_path':True,'destination':'x'}]}]:
   with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,bad,True)
 def test_18_unrelated_historical_manifest_no_new_reads(self):
  with tempfile.TemporaryDirectory() as td,mock.patch.object(c,'load',side_effect=AssertionError('unexpected input read')):
   c.validate_runtime_rows(Path(td),{'files':[]},False);c.validate_runtime_rows(Path(td),{'files':[{'source_path':'old','destination':'old'}]},False)
 def test_19_mapping_and_payload_header_closed(self):
  selected,pngs,blobs=c.generate(ROOT,(ROOT/c.SELECTION).read_bytes());pins={p:fnv(b[28:]) for p,b in blobs.items()};self.assertEqual(len(set(pins.values())),2)
  self.assertEqual(c.payload_header(pins),(ROOT/c.HEADER).read_bytes())
  for bad in [{},dict(list(pins.items())[:1]),{**pins,(1520101,8):'0'*16},dict.fromkeys(c.PAIRS,True)]:
   with self.assertRaises(ValueError):c.payload_header(bad)
 def test_20_linked_builder_output_refused(self):
  with tempfile.TemporaryDirectory() as td:
   t=Path(td);copy_inputs(t,c.input_paths(ROOT));p=t/c.png(c.IDS[0]);outside=t/'outside';outside.write_bytes(b'retain');p.unlink();p.symlink_to(outside)
   with mock.patch.object(sys,'argv',['builder','--root',str(t),'--write']),contextlib.redirect_stdout(io.StringIO()):
    with self.assertRaises(ValueError):build.main()
   self.assertEqual(outside.read_bytes(),b'retain')
 def test_21_no_original_data_or_dynamic_recipe_in_generator(self):
  source=(ROOT/'scripts/current_projectile_gold_pulse_compatibility.py').read_text()
  for s in ('tyrian.shp','palette.dat','/workspace/','subprocess','eval('):self.assertNotIn(s,source)
  self.assertEqual(len({c.MASTER['source_png']}),1);self.assertNotIn('stage',ast.get_docstring(ast.parse((ROOT/'scripts/build_current_projectile_gold_pulse.py').read_text())) or '')
 def test_22_exact_legacy_six_hda_unchanged(self):
  sys.path.insert(0,str(ROOT/'tests'));import projectile_blue_triplet_native_validation as b
  for i in b.SELECTORS:
   family='projectile-blue-triplet' if i in b.BLUE else f'projectile{i}'
   p=ROOT/'assets/hd/current-compat'/family/b.HDA_NAMES[i]
   self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),b.HDA_SHA[i])
 def test_23_evidence_scope_is_reference_not_runtime_runner(self):
  j=json.loads((ROOT/c.INPUT_ROOT/'runtime-evidence.json').read_text());self.assertEqual(j['native']['cases'],880);self.assertEqual(j['gameplay']['captured_ticks'],[364,365]);self.assertEqual(j['gameplay']['collision_rows'],28)
  self.assertEqual(j['historical_original_gold'],'UNKNOWN');self.assertEqual(j['fresh_full_gate'],'NOT_CLAIMED_BY_THIS_REFERENCE')
 def test_24_generator_and_coverage_are_current_root_only(self):
  for p in [ROOT/'scripts/current_projectile_gold_pulse_compatibility.py',ROOT/'scripts/build_current_projectile_gold_pulse.py']:
   self.assertNotIn('/workspace/',p.read_text());self.assertNotIn('fallback',p.read_text().replace('no game data or external fallback',''))
  self.assertEqual(c.coverage(ROOT)['members']['168']['pixels']['native_alpha0'],314)
if __name__=='__main__':unittest.main()
