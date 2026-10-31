"""Focused authoring/transport checks only; no executed C or gameplay claim."""
from pathlib import Path
import ast,contextlib,copy,io,json,os,struct,sys,tempfile,unittest
from unittest import mock
from PIL import Image
CODE_ROOT=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get('STATICS_TEST_ROOT',str(CODE_ROOT)))
sys.path.insert(0,str(CODE_ROOT/'scripts'))
import current_projectile_statics_compatibility as c
import build_current_projectile_statics as build

class StaticsAuthoring(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.selected=json.loads((ROOT/c.SELECTION).read_bytes());cls.contract=c.coverage(ROOT);cls.products=build.products(ROOT)
 def rows(self):return [dict(r,group='gameplay',revision=c.REVISION)for r in c.rows_for(self.selected,{(i,8):(ROOT/c.ROOT/c.name(i)).read_bytes()for i in c.IDS})]
 def payload(self,s):return (ROOT/c.ROOT/c.name(1540000+s)).read_bytes()[28:]
 def test_two_sources_three_prompts_are_fixed_distinct(self):
  self.assertEqual(c.SELECTORS,(162,260));self.assertEqual(c.IDS,(1540162,1540260));self.assertEqual(len(c.SOURCES),2);self.assertEqual(len(c.PROMPTS),3)
  self.assertEqual([s['source_size']for s in c.SOURCES],[[1254,1254],[887,1774]]);self.assertEqual(len({s['source_sha256']for s in c.SOURCES}),2)
 def test_six_products_exact_bytes_and_header(self):
  self.assertEqual(len(self.products),6)
  for name,b in self.products.items():self.assertEqual((ROOT/name).read_bytes(),b)
  self.assertEqual(len(c.load(ROOT)),2)
 def test_exact_registered_PNG_HDA_RGBA(self):
  for i,s in zip(c.IDS,c.SELECTORS):
   raw=(ROOT/c.ROOT/c.name(i)).read_bytes();self.assertEqual(struct.unpack('<4s6I',raw[:28]),(b'HDR1',i,8,12,14,0,0));self.assertEqual(len(raw),43036)
   with Image.open(ROOT/c.png(i))as im:self.assertEqual((im.mode,im.size),('RGBA',(96,112)));self.assertEqual(im.tobytes(),raw[28:])
 def test_all_matrices_support_soft_opaque_and_native_zero(self):
  for s,cells,dist,nonzero,soft,opaque,zero in [(162,24,(24,0,0),1392,1380,12,144),(260,86,(83,3,0),5217,5216,1,287)]:
   p=self.payload(s);m=c.validate_payload(ROOT,s,p);a=p[3::4];mask=c.MASKS[s];self.assertEqual(mask.count('1'),cells);self.assertEqual(m,self.contract['members'][str(s)]['max_alpha_matrix'])
   vals=[m[y][x]for y in range(14)for x in range(12)if mask[y*12+x]=='1'];self.assertEqual((sum(v>=200 for v in vals),sum(0<v<200 for v in vals),vals.count(0)),dist)
   self.assertEqual((sum(v>0 for v in a),sum(0<v<255 for v in a),a.count(255),max(a)),(nonzero,soft,opaque,255));self.assertEqual(sum(a[y*96+x]==0 for y in range(112)for x in range(96)if mask[y//8*12+x//8]=='1'),zero)
 def test_every_zero_pixel_is_canonical(self):
  for s in c.SELECTORS:
   p=self.payload(s)
   for n in range(10752):
    q=p[n*4:n*4+4]
    if c.MASKS[s][n//96//8*12+n%96//8]=='0'or not q[3]:self.assertEqual(q,b'\0'*4)
 def test_162_identical_separated_lobes_and_260_static_recipe(self):
  p=self.payload(162)
  for y in range(32):self.assertEqual(p[((16+y)*96+32)*4:((16+y)*96+64)*4],p[((56+y)*96+32)*4:((56+y)*96+64)*4])
  self.assertEqual(c.MEMBERS[0]['placements'],[[32,16],[32,56]]);self.assertEqual(c.MEMBERS[1]['placements'],[[16,0]]);self.assertEqual(c.MEMBERS[1]['resize'],[56,112])
 def test_standard_fnv_four_known_vectors_and_production(self):
  for b,pin in [(b'','cbf29ce484222325'),(b'a','af63dc4c8601ec8c'),(b'foobar','85944171f73967e8'),(b'hello','a430d84680aabd0b')]:self.assertEqual(c.fnv(b),pin)
  body=(ROOT/'src/asteroid1_ten_mirror.inc').read_text().split('static uint64_t asteroid1_stamp(const Uint8 *p,size_t n)\n{',1)[1].split('\n}',1)[0]
  self.assertEqual(''.join(body.split()),'uint64_th=UINT64_C(0xcbf29ce484222325);while(n--){h^=*p++;h*=UINT64_C(0x100000001b3);}returnh;')
 def test_both_payload_fnv_sha_and_wrong_seed_rejection(self):
  for s,pin in [(162,'97621110c318d6a5'),(260,'fa2ac27b3212b610')]:
   p=self.payload(s);self.assertEqual(c.fnv(p),pin);self.assertEqual(c.sha(p),self.contract['members'][str(s)]['payload_sha256'])
   h=1469598103934665603
   for v in p:h=((h^v)*1099511628211)&((1<<64)-1)
   self.assertNotEqual(f'{h:016x}',pin)
 def test_full_payload_mutations_rejected(self):
  for s in c.SELECTORS:
   raw=self.payload(s)
   offsets=[0,3,43007,next(i for i,a in enumerate(raw[3::4])if a==255)*4+3,next(i for i,a in enumerate(raw[3::4])if 0<a<255)*4+3]
   for n in offsets:
    b=bytearray(raw);b[n]^=1
    with self.subTest(s=s,n=n),self.assertRaises(ValueError):c.validate_payload(ROOT,s,b)
 def test_coverage_contract_mutations_rejected(self):
  for key in ('native_mask','native_occupied_cells','max_alpha_matrix','cell_distribution','pixels','payload_sha256','payload_fnv','palette_indices'):
   bad=copy.deepcopy(self.contract);bad['members']['162'][key]=None
   with self.subTest(key=key),self.assertRaises(ValueError):c.validate_payload(ROOT,162,self.payload(162),bad)
 def test_identity_density_and_payload_types_closed(self):
  for i,d in [(162,8),(1540161,8),(True,8),(1540162,True),(1540162,4),(1540162,8.0),('1540162',8)]:
   with self.assertRaises(ValueError):c.name(i,d)
  for s,p in [(True,self.payload(162)),(163,self.payload(162)),(162,b''),(162,self.payload(162)[:-1]),(162,list(self.payload(162)))]:
   with self.assertRaises(ValueError):c.validate_payload(ROOT,s,p)
 def test_all_header_fields_lengths_and_payload_rejected(self):
  for i in c.IDS:
   raw=(ROOT/c.ROOT/c.name(i)).read_bytes()
   for offset in (0,4,8,12,16,20,24,128):
    b=bytearray(raw);b[offset]^=1
    with self.assertRaises(ValueError):c.validate_hda(ROOT,i,bytes(b))
   for b in (raw[:-1],raw+b'x',bytearray(raw)):
    with self.assertRaises(ValueError):c.validate_hda(ROOT,i,b)
 def test_selection_missing_extra_reversed_and_candidate(self):
  for key in self.selected:
   bad=copy.deepcopy(self.selected);del bad[key]
   with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(bad).encode())
  for value in ({**self.selected,'extra':1},{**self.selected,'sources':list(reversed(c.SOURCES))},{**self.selected,'members':list(reversed(c.MEMBERS))},{**self.selected,'historical_prompts':c.PROMPTS[:2]}):
   with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(value).encode())
  candidate=dict(self.selected,schema=c.CANDIDATE_SCHEMA);self.assertEqual(c.selection(ROOT,json.dumps(candidate).encode(),True),candidate)
  with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(candidate).encode())
  with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(self.selected).encode(),1)
 def test_strict_json_duplicate_nonfinite_oversize_types(self):
  for raw in [b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":Infinity}',b' '*131073,'{}']:
   with self.assertRaises(ValueError):c.parse(raw)
 def test_source_recipe_fields_bool_float_path_drift(self):
  for key,value in [('source_png','../private.png'),('source_png','/tmp/raw.png'),('source_size',[True,1254]),('source_size',[1254.0,1254]),('source_sha256','0'*64)]:
   j=copy.deepcopy(self.selected);j['sources'][0][key]=value
   with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(j).encode())
  for key,value in [('selector',True),('crop',[False,0,1254,1254]),('resize',[32.0,32]),('placements',[[32,16]]),('png_compress_level',9)]:
   j=copy.deepcopy(self.selected);j['members'][0][key]=value
   with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(j).encode())
 def test_each_fixed_input_byte_change_fails(self):
  names=[s['source_png']for s in c.SOURCES]+[p['path']for p in c.PROMPTS]+[c.REGISTRATION,c.COVERAGE];read=c.read
  for name in names:
   def changed(root,p,*args):
    raw=read(root,p,*args);return raw+b'x'if p==name else raw
   with mock.patch.object(c,'read',side_effect=changed),self.assertRaises(ValueError):c.selection(ROOT,(ROOT/c.SELECTION).read_bytes())
 def test_path_absolute_parent_separator_control_rejected(self):
  for name in ('','/a','../a','a/../b','a//b','./a','a\\b','C:a','a\0b'):
   with self.subTest(name=name),self.assertRaises(ValueError):c.path(ROOT,name)
 def test_actual_missing_symlink_hardlink_and_directory_rejected(self):
  with tempfile.TemporaryDirectory()as td:
   t=Path(td);p=t/'input';p.write_bytes(b'fixed');pin=c.sha(b'fixed');self.assertEqual(c.single_input(t,'input',pin),b'fixed')
   with self.assertRaises(OSError):c.read(t,'missing')
   q=t/'link';q.symlink_to(p)
   with self.assertRaises(ValueError):c.read(t,'link')
   q.unlink();os.link(p,q)
   with self.assertRaises(ValueError):c.read(t,'input')
   q.unlink();d=t/'dir';d.mkdir()
   with self.assertRaises(ValueError):c.read(t,'dir')
   link=t/'dirlink';link.symlink_to(d,target_is_directory=True)
   with self.assertRaises(ValueError):c.path(t,'dirlink/x')
 def test_wrong_Pillow_and_raw_image_metadata_rejected(self):
  with mock.patch.object(c,'PILLOW_VERSION','13.0.0'),self.assertRaises(ValueError):c.generate(ROOT,(ROOT/c.SELECTION).read_bytes())
  for attr,value in [('format','JPEG'),('mode','RGB'),('size',(1253,1254)),('n_frames',2)]:
   image=mock.MagicMock();image.format='PNG';image.mode='RGBA';image.size=(1254,1254);image.n_frames=1;setattr(image,attr,value);ctx=mock.MagicMock();ctx.__enter__.return_value=image
   with mock.patch.object(c.Image,'open',return_value=ctx),self.assertRaises(ValueError):c.generate(ROOT,(ROOT/c.SELECTION).read_bytes())
 def test_rows_for_changed_or_partial_transports_rejected(self):
  blobs={(i,8):(ROOT/c.ROOT/c.name(i)).read_bytes()for i in c.IDS}
  for b in ({},dict(list(blobs.items())[:1]),{**blobs,(c.IDS[0],8):blobs[(c.IDS[0],8)]+b'x'}):
   with self.assertRaises(ValueError):c.rows_for(self.selected,b)
 def test_rows_for_exact_container_tuple_and_integer_key_types(self):
  blobs={(i,8):(ROOT/c.ROOT/c.name(i)).read_bytes()for i in c.IDS}
  expected=c.rows_for(self.selected,blobs)
  class DictSubclass(dict):pass
  class TupleSubclass(tuple):pass
  class IntSubclass(int):pass
  aliases=[{(float(i),float(d)):b for (i,d),b in blobs.items()},
           {(float(i),d):b for (i,d),b in blobs.items()},
           {(i,float(d)):b for (i,d),b in blobs.items()},
           {TupleSubclass((i,d)):b for (i,d),b in blobs.items()},
           {(IntSubclass(i),d):b for (i,d),b in blobs.items()},
           {(i,IntSubclass(d)):b for (i,d),b in blobs.items()}]
  for alias in aliases:
   self.assertEqual(set(alias),set(c.PAIRS))
   with self.assertRaises(ValueError):c.rows_for(self.selected,alias)
  for bad in (DictSubclass(blobs),list(blobs.items()),{(i,8,0):b for (i,_),b in blobs.items()},{(i,True):b for (i,_),b in blobs.items()}):
   with self.assertRaises(ValueError):c.rows_for(self.selected,bad)
  self.assertEqual(c.rows_for(self.selected,blobs),expected)
 def test_complete_current_package_and_unrelated_extra(self):
  rows=self.rows();c.validate_runtime_rows(ROOT,{'files':rows},True);c.validate_runtime_rows(ROOT,{'files':rows+[{'source_path':'other','destination':'other'}]},False)
 def test_missing_duplicate_unknown_alias_and_case_rejected(self):
  rows=self.rows()
  for bad in ([],rows[:1],rows+rows[:1]):
   with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':bad},True)
  for source in ('other/enemy-projectile-statics-999-8.hda','other/ENEMY-PROJECTILE-STATICS-162-8.HDA','other/enemy-projectile-statics-162-4.hda'):
   with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':rows+[{'source_path':source,'destination':source}]},False)
 def test_package_fields_identity_density_and_revision_closed(self):
  rows=self.rows()
  for key,value in [('source_path',rows[0]['source_path'].upper()),('destination',rows[0]['destination'].upper()),('sha256','0'*64),('group','old'),('revision','old'),('identity',True),('density',4)]:
   bad=copy.deepcopy(rows);bad[0][key]=value
   with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':bad},True)
 def test_unrelated_historical_manifest_does_not_read_new_inputs(self):
  with mock.patch.object(c,'load',side_effect=AssertionError('unexpected new input read')):
   c.validate_runtime_rows(Path('unused'),{'files':[]},False);c.validate_runtime_rows(Path('unused'),{'files':[{'source_path':'old','destination':'old'}]},False)
 def test_manifest_container_types_rejected(self):
  for j in (None,{}, {'files':True},{'files':[True]},{'files':[{'source_path':True,'destination':'x'}]}):
   with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,j,True)
  with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':[]},1)
 def test_mapping_and_pin_header_mutations_rejected(self):
  pins={(i,8):c.fnv(self.payload(s))for i,s in zip(c.IDS,c.SELECTORS)};self.assertEqual(c.payload_header(pins),(ROOT/c.HEADER).read_bytes())
  for bad in ({},dict(list(pins.items())[:1]),{**pins,(1540999,8):'0'*16},dict.fromkeys(c.PAIRS,True),dict.fromkeys(c.PAIRS,'0'*16)):
   with self.assertRaises(ValueError):c.payload_header(bad)
  original=c.read
  for name in (c.MAPPING,c.HEADER,c.png(c.IDS[0]),c.ROOT+'/'+c.name(c.IDS[1])):
   def changed(root,p,*args):
    b=original(root,p,*args)
    if p!=name:return b
    if p==c.MAPPING:return json.dumps(dict(json.loads(b),version='changed')).encode()
    return b+b'\n'
   with mock.patch.object(c,'read',side_effect=changed),self.assertRaises(ValueError):c.load(ROOT)
 def test_builder_output_set_is_six_and_no_link_target_overwrite(self):
  with tempfile.TemporaryDirectory()as td:
   t=Path(td);target=t/'outside';target.write_bytes(b'retain');p=t/c.HEADER;p.parent.mkdir();p.symlink_to(target)
   with mock.patch.object(build,'products',return_value={c.HEADER:b'replace'}),mock.patch.object(sys,'argv',['builder','--root',str(t),'--write']),self.assertRaises(ValueError):build.main()
   self.assertEqual(target.read_bytes(),b'retain')
 def test_builder_hardlink_output_refused(self):
  with tempfile.TemporaryDirectory()as td:
   t=Path(td);target=t/'outside';target.write_bytes(b'retain');p=t/c.HEADER;p.parent.mkdir();os.link(target,p)
   with mock.patch.object(build,'products',return_value={c.HEADER:b'replace'}),mock.patch.object(sys,'argv',['builder','--root',str(t),'--write']),self.assertRaises(ValueError):build.main()
   self.assertEqual(target.read_bytes(),b'retain')
 def test_no_original_data_private_paths_or_dynamic_generator(self):
  for name in ('current_projectile_statics_compatibility.py','build_current_projectile_statics.py'):
   text=(CODE_ROOT/'scripts'/name).read_text()
   for token in ('/workspace/','libfile_','PRIVATE-native','tyrian.shp','palette.dat','subprocess','eval('):self.assertNotIn(token,text)
  self.assertEqual(len(c.SOURCES),2)
 def test_sanitized_evidence_accurate_pending_and_failure(self):
  p=ROOT/c.INPUT_ROOT/'runtime-evidence.json';text=p.read_text();j=json.loads(text)
  for token in ('/workspace/','libfile_','PRIVATE-native','tool_raw_path'):self.assertNotIn(token,text)
  self.assertEqual(j['native']['cases'],1329);self.assertEqual(j['native']['old_cases'],880);self.assertEqual(j['native']['new_cases'],449);self.assertEqual(j['gameplay']['runs'],6);self.assertEqual(j['gameplay']['ticks_per_run'],120);self.assertEqual(j['gameplay']['captured_ticks'],{'162':59,'260':69});self.assertEqual(j['historical_registration01']['empty_native_cells'],9)
  self.assertIn('PENDING',j['fresh_four_configs']);self.assertIn('PENDING',j['ordered558_suffix_QA']);self.assertIn('overlap',j['gameplay']['visual_scope'])
 def test_actual_shared_palette_sets_not_fake_isolation(self):
  a=self.contract['members']['162']['palette_indices'];b=self.contract['members']['260']['palette_indices'];self.assertEqual(a,[122,123,125,126,127]);self.assertEqual(b,[113,116,117,119,120,121,122,123,124,125,126]);self.assertEqual(set(a)&set(b),{122,123,125,126})
if __name__=='__main__':unittest.main()
