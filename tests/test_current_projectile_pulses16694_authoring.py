"""Focused authoring/transport checks only; no executed C or gameplay claim."""
from pathlib import Path
import ast,contextlib,copy,io,json,os,struct,sys,tempfile,unittest
from unittest import mock
from PIL import Image
CODE_ROOT=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get('PULSES16694_TEST_ROOT',str(CODE_ROOT)))
sys.path.insert(0,str(CODE_ROOT/'scripts'))
import current_projectile_pulses16694_compatibility as c
import build_current_projectile_pulses16694 as build

class Pulses16694Authoring(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.selected=json.loads((ROOT/c.SELECTION).read_bytes());cls.contract=c.coverage(ROOT);cls.products=build.products(ROOT)
 def rows(self):return [dict(r,group='gameplay',revision=c.REVISION)for r in c.rows_for(self.selected,{(i,8):(ROOT/c.ROOT/c.name(i)).read_bytes()for i in c.IDS})]
 def payload(self,s):return (ROOT/c.ROOT/c.name(1550000+s)).read_bytes()[28:]
 def test_two_sources_three_prompts_are_fixed_distinct(self):
  self.assertEqual(c.SELECTORS,(166,94));self.assertEqual(c.IDS,(1550166,1550094));self.assertEqual(len(c.SOURCES),2);self.assertEqual(len(c.PROMPTS),3)
  self.assertEqual([s['source_size']for s in c.SOURCES],[[1254,1254],[1060,1484]]);self.assertEqual(len({s['source_sha256']for s in c.SOURCES}),2)
 def test_six_products_exact_bytes_and_header(self):
  self.assertEqual(len(self.products),6)
  for name,b in self.products.items():self.assertEqual((ROOT/name).read_bytes(),b)
  self.assertEqual(len(c.load(ROOT)),2)
 def test_exact_registered_PNG_HDA_RGBA(self):
  for i,s in zip(c.IDS,c.SELECTORS):
   raw=(ROOT/c.ROOT/c.name(i)).read_bytes();self.assertEqual(struct.unpack('<4s6I',raw[:28]),(b'HDR1',i,8,12,14,0,0));self.assertEqual(len(raw),43036)
   with Image.open(ROOT/c.png(i))as im:self.assertEqual((im.mode,im.size),('RGBA',(96,112)));self.assertEqual(im.tobytes(),raw[28:])
 def test_all_matrices_support_soft_opaque_and_native_zero(self):
  for s,cells,dist,nonzero,soft,opaque,zero,max_alpha in [(166,97,(69,28,0),5788,5788,0,420,253),(94,108,(103,5,0),6488,6448,40,424,255)]:
   p=self.payload(s);m=c.validate_payload(ROOT,s,p);a=p[3::4];mask=c.MASKS[s];self.assertEqual(mask.count('1'),cells);self.assertEqual(m,self.contract['members'][str(s)]['max_alpha_matrix'])
   vals=[m[y][x]for y in range(14)for x in range(12)if mask[y*12+x]=='1'];self.assertEqual((sum(v>=200 for v in vals),sum(0<v<200 for v in vals),vals.count(0)),dist)
   self.assertEqual((sum(v>0 for v in a),sum(0<v<255 for v in a),a.count(255),max(a)),(nonzero,soft,opaque,max_alpha));self.assertEqual(sum(a[y*96+x]==0 for y in range(112)for x in range(96)if mask[y//8*12+x//8]=='1'),zero)
 def test_every_zero_pixel_is_canonical(self):
  for s in c.SELECTORS:
   p=self.payload(s)
   for n in range(10752):
    q=p[n*4:n*4+4]
    if c.MASKS[s][n//96//8*12+n%96//8]=='0'or not q[3]:self.assertEqual(q,b'\0'*4)
 def test_162_identical_separated_lobes_and_260_static_recipe(self):
  # Historical method ID retained; these are two SINGLE components, not162 lobes.
  self.assertEqual(c.MEMBERS[0]['placements'],[[8,8]]);self.assertEqual(c.MEMBERS[0]['resize'],[88,88])
  self.assertEqual(c.MEMBERS[1]['placements'],[[8,0]]);self.assertEqual(c.MEMBERS[1]['resize'],[80,112])
  self.assertEqual(c.MEMBERS[0]['crop'],[0,0,1254,1254]);self.assertEqual(c.MEMBERS[1]['crop'],[0,0,1060,1484])
  self.assertEqual([c.MASKS[s].count('1')for s in c.SELECTORS],[97,108])
 def test_standard_fnv_four_known_vectors_and_production(self):
  for b,pin in [(b'','cbf29ce484222325'),(b'a','af63dc4c8601ec8c'),(b'foobar','85944171f73967e8'),(b'hello','a430d84680aabd0b')]:self.assertEqual(c.fnv(b),pin)
  body=(ROOT/'src/asteroid1_ten_mirror.inc').read_text().split('static uint64_t asteroid1_stamp(const Uint8 *p,size_t n)\n{',1)[1].split('\n}',1)[0]
  self.assertEqual(''.join(body.split()),'uint64_th=UINT64_C(0xcbf29ce484222325);while(n--){h^=*p++;h*=UINT64_C(0x100000001b3);}returnh;')
 def test_both_payload_fnv_sha_and_wrong_seed_rejection(self):
  for s,pin in [(166,'80c10783a6cabbe2'),(94,'131a3be7ed56665d')]:
   p=self.payload(s);self.assertEqual(c.fnv(p),pin);self.assertEqual(c.sha(p),self.contract['members'][str(s)]['payload_sha256'])
   h=1469598103934665603
   for v in p:h=((h^v)*1099511628211)&((1<<64)-1)
   self.assertNotEqual(f'{h:016x}',pin)
 def test_full_payload_mutations_rejected(self):
  for s in c.SELECTORS:
   raw=self.payload(s)
   offsets=[0,3,43007,next(i for i,a in enumerate(raw[3::4])if 0<a<255)*4+3]
   #166 has no opaque pixel; test its actual soft/zero data, not an invented opaque.
   if 255 in raw[3::4]:offsets.append(next(i for i,a in enumerate(raw[3::4])if a==255)*4+3)
   for n in offsets:
    b=bytearray(raw);b[n]^=1
    with self.subTest(s=s,n=n),self.assertRaises(ValueError):c.validate_payload(ROOT,s,b)
 def test_coverage_contract_mutations_rejected(self):
  for key in ('native_mask','native_occupied_cells','max_alpha_matrix','cell_distribution','pixels','payload_sha256','payload_fnv','palette_indices'):
   bad=copy.deepcopy(self.contract);bad['members']['166'][key]=None
   with self.subTest(key=key),self.assertRaises(ValueError):c.validate_payload(ROOT,166,self.payload(166),bad)
 def test_identity_density_and_payload_types_closed(self):
  for i,d in [(166,8),(1550165,8),(True,8),(1550166,True),(1550166,4),(1550166,8.0),('1550166',8)]:
   with self.assertRaises(ValueError):c.name(i,d)
  for s,p in [(True,self.payload(166)),(163,self.payload(166)),(166,b''),(166,self.payload(166)[:-1]),(166,list(self.payload(166)))]:
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
  for source in ('other/enemy-projectile-pulses16694-999-8.hda','other/ENEMY-PROJECTILE-PULSES16694-166-8.HDA','other/enemy-projectile-pulses16694-166-4.hda'):
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
  for bad in ({},dict(list(pins.items())[:1]),{**pins,(1550999,8):'0'*16},dict.fromkeys(c.PAIRS,True),dict.fromkeys(c.PAIRS,'0'*16)):
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
  for name in ('current_projectile_pulses16694_compatibility.py','build_current_projectile_pulses16694.py'):
   text=(CODE_ROOT/'scripts'/name).read_text()
   for token in ('/workspace/','libfile_','PRIVATE-native','tyrian.shp','palette.dat','subprocess','eval('):self.assertNotIn(token,text)
  self.assertEqual(len(c.SOURCES),2)
 def test_sanitized_evidence_accurate_pending_and_failure(self):
  p=ROOT/c.INPUT_ROOT/'runtime-evidence.json';text=p.read_text();j=json.loads(text)
  for token in ('/workspace/','libfile_','PRIVATE-native','tool_raw_path'):self.assertNotIn(token,text)
  self.assertEqual(j['native']['cases'],1907);self.assertEqual(j['native']['old_cases'],1329);self.assertEqual(j['native']['new_cases'],578)
  self.assertEqual(j['native']['assertions'],285458804);self.assertEqual(j['native']['process_cases'],[107,157,365,251,449,578])
  self.assertEqual(j['gameplay']['runs'],6);self.assertEqual(j['gameplay']['ticks_per_run_by_site'],{'166':241,'94':161});self.assertEqual(j['gameplay']['total_ticks'],1206);self.assertEqual(j['gameplay']['captured_ticks'],{'166':220,'94':127})
  self.assertEqual(j['historical_registration01']['empty_native_cells'],4);self.assertEqual(j['registration']['corrected94_registered_pixels_changed'],6574)
  self.assertEqual(j['gameplay']['natural_foreign_pixels'],0);self.assertFalse(j['gameplay']['natural_foreign_drop_positive']);self.assertFalse(j['gameplay']['night'])
  self.assertEqual(j['gameplay']['legacy94_rejections'],['normal15-output-scope','normal15-scene-font'])
  self.assertIn('PENDING',j['fresh_four_configs']);self.assertIn('PENDING',j['ordered716_suffix_QA']);self.assertIn('not continuous',j['gameplay']['visual_scope'])
  self.assertEqual([r['status']for r in j['native']['historical_runs']],['FAIL_RETAINED','FAIL_CAPTURE_POSTCONDITION'])
 def test_actual_shared_palette_sets_not_fake_isolation(self):
  #Historical method ID:these two NEW resources have genuinely disjoint native colors.
  a=self.contract['members']['166']['palette_indices'];b=self.contract['members']['94']['palette_indices']
  self.assertEqual(a,[33,*range(144,160)]);self.assertEqual(b,[114,115,116,117,119,120,121,122,123,124,125,126,127]);self.assertEqual(set(a)&set(b),set())
  self.assertEqual(len(set(a)|set(b)),30)

 def test_new_166_zero_opaque_and_zero_bottom_rows(self):
  raw=self.payload(166);self.assertNotIn(255,raw[3::4]);self.assertEqual(max(raw[3::4]),253)
  self.assertEqual(c.MASKS[166][-24:],'0'*24);self.assertEqual(raw[96*96*4:],b'\0'*(16*96*4))
 def test_new_94_corrected_shoulders_retain_low_alpha(self):
  matrix=self.contract['members']['94']['max_alpha_matrix'];self.assertEqual([matrix[y][x]for y,x in [(3,2),(3,9),(5,1),(5,10)]],[56,68,252,251])
  self.assertEqual(self.contract['members']['94']['cell_distribution'],{'high_ge200':103,'low_1_199':5,'zero':0});self.assertEqual(self.payload(94)[3::4].count(255),40)
 def test_new_payload_header_rejects_alias_key_types(self):
  pins={(i,8):c.fnv(self.payload(s))for i,s in zip(c.IDS,c.SELECTORS)}
  class TupleSubclass(tuple):pass
  class IntSubclass(int):pass
  class DictSubclass(dict):pass
  for bad in (DictSubclass(pins),{(float(i),float(d)):p for (i,d),p in pins.items()},{TupleSubclass((i,d)):p for (i,d),p in pins.items()},{(IntSubclass(i),d):p for (i,d),p in pins.items()}):
   with self.assertRaises(ValueError):c.payload_header(bad)
 def test_new_actual_raw_second_read_still_checks_hard_pin(self):
  original=c.read;target=c.SOURCES[0]['source_png'];counts={'raw':0}
  def changed(root,path,*args):
   raw=original(root,path,*args)
   if path==target:
    counts['raw']+=1
    if counts['raw']==2:return raw+b'changed'
   return raw
  with mock.patch.object(c,'read',side_effect=changed),mock.patch.object(c.Image,'open',side_effect=AssertionError('Unpinned raw reached decoder')),self.assertRaises(ValueError):c.generate(ROOT,(ROOT/c.SELECTION).read_bytes())
  self.assertEqual(counts['raw'],2)
 def test_new_coverage_nested_numeric_type_aliases_rejected(self):
  for key,value in [('native_occupied_cells',97.0),('palette_indices',[33.0,*range(144,160)]),('pixels',dict(self.contract['members']['166']['pixels'],opaque255=False))]:
   bad=copy.deepcopy(self.contract);bad['members']['166'][key]=value
   with self.assertRaises(ValueError):c.validate_payload(ROOT,166,self.payload(166),bad)
  bad=copy.deepcopy(self.contract);bad['members']['166']['max_alpha_matrix'][0][0]=False
  with self.assertRaises(ValueError):c.validate_payload(ROOT,166,self.payload(166),bad)
 def test_new_registration_is_fixed_single_resample_and_unmasked_paste(self):
  text=(CODE_ROOT/'scripts/current_projectile_pulses16694_compatibility.py').read_text();tree=ast.parse(text)
  generate=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='generate')
  calls=[n for n in ast.walk(generate)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)]
  self.assertEqual(len([n for n in calls if n.func.attr=='resize']),1)
  paste=[n for n in calls if n.func.attr=='paste'];self.assertEqual(len(paste),1);self.assertEqual(len(paste[0].args),2);self.assertEqual(paste[0].keywords,[])
  self.assertNotIn('getbbox',text);self.assertNotIn('alpha_composite',text)
 def test_new_registration_metadata_root_only_and_exact_geometry(self):
  registration=json.loads((ROOT/c.REGISTRATION).read_bytes());self.assertEqual(registration['schema'],'enemy-pulses16694-fixed-registration-v1');self.assertEqual(registration['pillow'],'12.3.0')
  self.assertEqual(registration['sources'],c.SOURCES);self.assertEqual(registration['members'],c.MEMBERS);self.assertEqual(registration['historical_prompts'],c.PROMPTS)
  for p in (c.REGISTRATION,c.COVERAGE,c.INPUT_ROOT+'/README.md'):
   text=(ROOT/p).read_text()
   for token in ('/workspace/','libfile_','PRIVATE-native'):self.assertNotIn(token,text)

if __name__=='__main__':unittest.main()
