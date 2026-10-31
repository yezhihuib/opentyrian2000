"""New-helper-only pure/schema/readback tests. Never compile or invoke C/game."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,re,struct,tempfile,unittest,os,inspect,types
from unittest import mock
P=Path(__file__).parent
spec=importlib.util.spec_from_file_location('pulses_helper',P/'projectile_pulses16694_native_validation.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
N=Path(os.environ.get('OPENTYRIAN_PULSES_TEST_ROOT',str(P.parent)))
A=N
EXPECTED_OLD_STDOUT = {'inherited107_stdout': b'PASS inherited91 native lifecycle: 37 cases 81611 assertions\n145_TO_TALON copied=376 cached=0\n145_TO_TALON copied=376 cached=1\nPASS shared145 native lifecycle: 70 new cases 141992 new assertions; internal8 only; not gameplay/full build\n', 'inherited61_stdout': b'61_TO_TALON copied=267 cached=0\n61_TO_TALON copied=267 cached=1\nPASS shared61 native lifecycle: 157 cases 822291 assertions; internal8 only; not gameplay/full build\n', 'new_blue_stdout': b'BLUE101_ZERO_NATIVE pattern=0 draw=384 finish=384 cache=384\nBLUE101_ZERO_NATIVE pattern=1 draw=384 finish=384 cache=384\nBLUE101_ZERO_HD prior=120 draw=384 finish=384 cache=384\nBLUE_TO_TALON selector=101 copied=1756 soft=1721 cached=0\nBLUE_TO_TALON selector=101 copied=1756 soft=1721 cached=1\nBLUE_TO_TALON selector=120 copied=1864 soft=1864 cached=0\nBLUE_TO_TALON selector=120 copied=1864 soft=1864 cached=1\nBLUE_TO_TALON selector=139 copied=1481 soft=1454 cached=0\nBLUE_TO_TALON selector=139 copied=1481 soft=1454 cached=1\nPASS blue triplet native lifecycle: 365 cases 11162937 assertions; internal8 only; not gameplay/full build\n', 'gold251_stdout': b'GOLD_GROUP name=full_tile_native_patterns cases=4\nGOLD_GROUP name=bounds cases=18\nGOLD_GROUP name=pair_orders cases=26\nGOLD_GROUP name=all8_early_dependency cases=16\nGOLD_GROUP name=missing_bad cases=32\nGOLD_GROUP name=singletons_oldonly cases=4\nGOLD_GROUP name=malformed_gold cases=6\nGOLD_GROUP name=unused_memory_payload_ready cases=8\nGOLD_GROUP name=palette cases=40\nGOLD_GROUP name=used_resource_shared cases=64\nGOLD_GROUP name=callbacks cases=8\nGOLD_GROUP name=cold_scope cases=10\nGOLD_TO_TALON selector=168 copied=974 soft=974 alpha0=86 cached=0\nGOLD_TO_TALON selector=168 copied=974 soft=974 alpha0=86 cached=1\nGOLD_TO_TALON selector=169 copied=735 soft=735 alpha0=85 cached=0\nGOLD_TO_TALON selector=169 copied=735 soft=735 alpha0=85 cached=1\nGOLD_GROUP name=Talon_transfer cases=4\nGOLD_GROUP name=lifecycle cases=5\nGOLD_GROUP name=controlled_animation cases=6\nPASS gold pulse native lifecycle: 251 cases 38046959 assertions; internal8 only; not gameplay/full build\n', 'statics449_stdout': b'STATICS_GROUP name=full_tile_native_patterns cases=4\nSTATICS_GROUP name=full_tile_hd_underlay cases=2\nSTATICS_GROUP name=bounds cases=22\nSTATICS_GROUP name=pair_orders_zero_isolation cases=34\nSTATICS_GROUP name=all10_same_origin_dependency cases=20\nSTATICS_GROUP name=all10_two_row_dependency cases=20\nSTATICS_GROUP name=missing_bad cases=40\nSTATICS_GROUP name=singletons_oldonly cases=4\nSTATICS_GROUP name=malformed_headers_lengths cases=18\nSTATICS_GROUP name=readiness_root_epochs cases=4\nSTATICS_GROUP name=unused_memory_payload_ready cases=8\nSTATICS_GROUP name=palette_admission_shared cases=24\nSTATICS_GROUP name=palette_direct_final_cache cases=38\nSTATICS_GROUP name=palette_composite_preflight cases=12\nSTATICS_GROUP name=used_resource_direct_final_cache cases=52\nSTATICS_GROUP name=source_scope_direct_final_cache cases=24\nSTATICS_GROUP name=layout_direct_final_cache cases=32\nSTATICS_GROUP name=callbacks cases=12\nSTATICS_GROUP name=cold_warm_scope cases=44\nSTATICS_TO_TALON selector=162 copied=526 soft=521 alpha0=35 cached=0\nSTATICS_TO_TALON selector=162 copied=526 soft=521 alpha0=35 cached=1\nSTATICS_TO_TALON selector=260 copied=1122 soft=1122 alpha0=6 cached=0\nSTATICS_TO_TALON selector=260 copied=1122 soft=1122 alpha0=6 cached=1\nSTATICS_GROUP name=Talon_transfer cases=4\nSTATICS_GROUP name=Talon_underlay_direct cases=8\nSTATICS_GROUP name=lifecycle cases=7\nSTATICS_GROUP name=later_native_final_writers cases=8\nSTATICS_GROUP name=fade_high_bits cases=8\nPASS enemy statics native lifecycle: 449 cases 91342858 assertions; internal8 only; not gameplay/full build\n'}
ACTUAL_PULSES_STDOUT = b'PULSES16694_GROUP name=full_tile_native_patterns cases=4\nPULSES16694_GROUP name=full_tile_hd_underlay cases=2\nPULSES16694_GROUP name=bounds cases=22\nPULSES16694_GROUP name=pair_orders_zero_isolation cases=42\nPULSES16694_GROUP name=all12_same_origin_dependency cases=24\nPULSES16694_GROUP name=all12_two_row_dependency cases=24\nPULSES16694_GROUP name=missing_bad cases=48\nPULSES16694_GROUP name=singletons_oldonly cases=4\nPULSES16694_GROUP name=malformed_headers_lengths cases=18\nPULSES16694_GROUP name=readiness_root_epochs cases=4\nPULSES16694_GROUP name=unused_memory_payload_ready cases=8\nPULSES16694_GROUP name=palette_admission_shared cases=60\nPULSES16694_GROUP name=palette_direct_final_cache cases=66\nPULSES16694_GROUP name=palette_composite_preflight cases=29\nPULSES16694_GROUP name=used_resource_direct_final_cache cases=52\nPULSES16694_GROUP name=source_scope_direct_final_cache cases=24\nPULSES16694_GROUP name=layout_direct_final_cache cases=32\nPULSES16694_GROUP name=callbacks cases=12\nPULSES16694_GROUP name=cold_warm_scope cases=44\nPULSES16694_TO_TALON selector=166 copied=1176 soft=1176 alpha0=133 cached=0\nPULSES16694_TO_TALON selector=166 copied=1176 soft=1176 alpha0=133 cached=1\nPULSES16694_TO_TALON selector=94 copied=1081 soft=1081 alpha0=56 cached=0\nPULSES16694_TO_TALON selector=94 copied=1081 soft=1081 alpha0=56 cached=1\nPULSES16694_GROUP name=Talon_transfer cases=4\nPULSES16694_GROUP name=Talon_underlay_direct cases=8\nPULSES16694_GROUP name=lifecycle cases=7\nPULSES16694_GROUP name=later_native_final_writers cases=8\nPULSES16694_GROUP name=fade_high_bits cases=8\nPULSES16694_GROUP name=player_generic_aliases cases=8\nPULSES16694_GROUP name=all12_fade_lease cases=4\nPULSES16694_LEGACY context=0 selector=166 mixed=0 kept=6208 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=0 selector=166 mixed=1 kept=3008 dropped=3200 opaque_clears=0\nPULSES16694_LEGACY context=0 selector=94 mixed=0 kept=6912 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=0 selector=94 mixed=1 kept=3409 dropped=3503 opaque_clears=17\nPULSES16694_LEGACY context=1 selector=166 mixed=0 kept=6208 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=1 selector=166 mixed=1 kept=3008 dropped=3200 opaque_clears=0\nPULSES16694_LEGACY context=1 selector=94 mixed=0 kept=6912 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=1 selector=94 mixed=1 kept=3409 dropped=3503 opaque_clears=17\nPULSES16694_LEGACY context=2 selector=166 mixed=0 kept=6208 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=2 selector=166 mixed=1 kept=3008 dropped=3200 opaque_clears=0\nPULSES16694_LEGACY context=2 selector=94 mixed=0 kept=6912 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=2 selector=94 mixed=1 kept=3409 dropped=3503 opaque_clears=17\nPULSES16694_GROUP name=legacy_reject_own_foreign cases=12\nPASS enemy pulses16694 native lifecycle: 578 cases 143860156 assertions; internal8 only; not gameplay/full build\n'
class Pure(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=(P/'projectile_pulses16694_native_additions.c.inc').read_text();cls.reg=h.registration(A);cls.hdas=h.registered_hdas(A)
  cls.body=h.expected_body_lines();cls.stdout=('\n'.join(cls.body)+f'\nPASS enemy pulses16694 native lifecycle: {sum(n for _,n in h.GROUPS)} cases 123456 assertions; internal8 only; not gameplay/full build\n').encode()
  cls.wrapper=h.statics_helper(N).source_bundle(N)[1]
 def bad(self,fn,*args):
  with self.assertRaises((AssertionError,UnicodeError,ValueError,KeyError,TypeError)):fn(*args)
 def test_fnv_vectors(self):
  for raw,want in ((b'',0xcbf29ce484222325),(b'a',0xaf63dc4c8601ec8c),(b'foobar',0x85944171f73967e8),(b'hello',0xa430d84680aabd0b)):self.assertEqual(h.fnv1a64(raw),want)
 def test_fnv_reject_mutable(self):self.bad(h.fnv1a64,bytearray(b'a'))
 def test_full_registered_statistics(self):
  for i,row in zip(h.PULSES,self.reg['members']):
   self.assertEqual(row['selector'],i);self.assertEqual(row['statistics']['native_cells'],97 if i==166 else 108)
 def test_actual_hda_pins(self):
  for i,raw in self.hdas.items():self.assertTrue(h.validate_hda(raw,i));self.assertEqual(len(raw),43036)
 def test_hda_wrong_identity(self):
  for i,raw in self.hdas.items():self.bad(h.validate_hda,raw[:4]+struct.pack('<I',1550000+h.PULSES[1-h.PULSES.index(i)])+raw[8:],i)
 def test_hda_wrong_fields(self):
  for offset in (8,12,16,20,24):
   raw=bytearray(self.hdas[94]);raw[offset]^=1;self.bad(h.validate_hda,bytes(raw),94)
 def test_hda_short_trailing(self):
  for raw in (self.hdas[94][:-1],self.hdas[94]+b'!'):self.bad(h.validate_hda,raw,94)
 def test_hda_bad_payload(self):
  raw=bytearray(self.hdas[166]);raw[128]^=1;self.bad(h.validate_hda,bytes(raw),166)
 def test_hda_selector_float_bool(self):
  for i in (166.0,True,'166'):self.bad(h.validate_hda,self.hdas[166],i)
 def test_payload_actual_rgba(self):
  for i in h.PULSES:self.assertEqual(h.hda_payload(i,h.registered_rgba(i,A)),self.hdas[i])
 def test_payload_false_type(self):self.bad(h.hda_payload,94,bytearray(self.hdas[94][28:]))
 def test_no_alpha_rewrite(self):
  self.assertEqual(self.hdas[166][31::4].count(255),0);self.assertEqual(self.hdas[94][31::4].count(255),40)
 def test_native_alpha0(self):
  self.assertEqual([r['statistics']['native_alpha0'] for r in self.reg['members']],[420,424])
 def test_mask_zeros_and_hidden_rgb(self):
  self.assertTrue(all(r['statistics']['outside_nonzero']==r['statistics']['alpha0_rgb_nonzero']==0 for r in self.reg['members']))
 def test_full_matrix(self):
  for row in self.reg['members']:self.assertEqual(row['statistics']['max_alpha_matrix'],h.PINS[row['selector']]['max_alpha_matrix'])
 def test_fixture_46_516(self):
  schema=h.fixture_schema();self.assertEqual(len(schema),46);self.assertEqual(sum(map(len,schema.values())),516)
 def test_fixture_sets(self):
  schema=h.fixture_schema();self.assertEqual(schema['valid'],h.IDS);self.assertEqual(schema['old-only'],h.IDS[:10]);self.assertEqual(schema['only166'],(166,));self.assertEqual(schema['only94'],(94,))
 def test_fixture_missing_bad(self):
  schema=h.fixture_schema()
  for i in h.IDS:self.assertEqual(schema['missing'+str(i)],tuple(j for j in h.IDS if j!=i));self.assertEqual(schema['bad'+str(i)],h.IDS)
 def test_fixture_516_lengths(self):
  total=0;raw=bytes(43036)
  for leaf in h.PACK_NAMES:
   for i in h.IDS:
    out=h.fixture_bytes(raw,i,leaf)
    if out is not None:total+=len(out)
  self.assertEqual(total,22206576)
 def test_fixture_only_named_mutates(self):
  raw=self.hdas[166]
  for leaf in h.PACK_NAMES:
   if leaf.endswith('94') and not leaf.startswith('only'):self.assertEqual(h.fixture_bytes(raw,166,leaf),raw)
 def test_fixture_bad_one_byte(self):
  raw=self.hdas[166];other=h.fixture_bytes(raw,166,'bad166');self.assertEqual([i for i,(a,b) in enumerate(zip(raw,other)) if a!=b],[128])
 def test_fixture_each_header(self):
  for name,off in (('header',4),('magic',0),('density',8),('width',12),('height',16),('anchorx',20),('anchory',24)):
   raw=h.fixture_bytes(self.hdas[94],94,name+'94');self.assertNotEqual(raw,self.hdas[94]);self.assertEqual(raw[28:],self.hdas[94][28:]);self.bad(h.validate_hda,raw,94)
 def test_fixture_types(self):
  for i in (166.0,True,'166'):self.bad(h.fixture_bytes,self.hdas[166],i,'valid')
  for leaf in (b'valid','../valid','valid/..','VALID'):self.bad(h.fixture_bytes,self.hdas[166],166,leaf)
 def test_fixture_map_float_key(self):
  m={i:bytes(43036) for i in h.IDS};m.pop(166);m[166.0]=self.hdas[166];m[94]=self.hdas[94];self.bad(h.validate_fixture_arguments,m,self.reg)
 def test_fixture_map_bool_key(self):
  m={i:bytes(43036) for i in h.IDS};m[True]=bytes(43036);self.bad(h.validate_fixture_arguments,m,self.reg)
 def test_fixture_meta_float_selector(self):
  m={i:bytes(43036) for i in h.IDS};m.update(self.hdas);reg=copy.deepcopy(self.reg);reg['members'][0]['selector']=166.0;self.bad(h.validate_fixture_arguments,m,reg)
 def test_fixture_meta_false_stats(self):
  m={i:bytes(43036) for i in h.IDS};m.update(self.hdas);reg=copy.deepcopy(self.reg);reg['members'][0]['statistics']['native_cells']=97.0;self.bad(h.validate_fixture_arguments,m,reg)
 def test_fixture_metadata_order(self):
  m={i:bytes(43036) for i in h.IDS};m.update(self.hdas);reg=copy.deepcopy(self.reg);reg['members'].reverse();self.bad(h.validate_fixture_arguments,m,reg)
 def test_fixture_good_arguments(self):
  m={i:bytes(43036) for i in h.IDS};m.update(self.hdas);self.assertTrue(h.validate_fixture_arguments(m,self.reg))
 def test_fixture_producer_inert(self):
  tree=ast.parse((P/'projectile_pulses16694_native_validation.py').read_text());self.assertNotIn('subprocess',(P/'projectile_pulses16694_native_validation.py').read_text());self.assertFalse(any(isinstance(n,(ast.With,ast.For,ast.While)) for n in tree.body))
 def test_wrapper_exact_inverse(self):self.assertEqual(h.reverse_shim(h.outer_shim(self.wrapper)),self.wrapper)
 def test_wrapper_nonmatching_old(self):self.bad(h.outer_shim,self.wrapper+b' ')
 def test_wrapper_inverse_tail(self):self.bad(h.reverse_shim,h.outer_shim(self.wrapper)+b'\n')
 def test_wrapper_inverse_body(self):self.bad(h.reverse_shim,h.outer_shim(self.wrapper).replace(b'--enemy-statics',b'--enemy-STATIC'))
 def test_inherited_sources_bytes(self):
  sources,_=h.statics_helper(N).source_bundle(N)
  for name,pin in h.SOURCE_PINS.items():self.assertEqual(h.SHA(sources[name]),pin)
 def test_old_statics_helper_pin(self):self.assertEqual(h.SHA((N/'tests/projectile_statics_native_validation.py').read_bytes()),h.STATICS_HELPER_SHA)
 def test_old_five_stdout(self):
  self.assertEqual(h.verify_legacy_stdout(EXPECTED_OLD_STDOUT)['cases'],1329)
 def test_old_stdout_schema_missing(self):self.bad(h.verify_legacy_stdout,{})
 def test_stdout_positive_schema(self):self.assertEqual(h.parse_pulses_stdout(self.stdout)['cases'],578)
 def test_stdout_not_runtime_result(self):self.assertEqual(h.parse_pulses_stdout(self.stdout)['assertions'],123456)
 def test_stdout_no_crlf(self):self.bad(h.parse_pulses_stdout,self.stdout.replace(b'\n',b'\r\n'))
 def test_stdout_no_trailing_extra(self):self.bad(h.parse_pulses_stdout,self.stdout+b'noise\n')
 def test_stdout_no_missing_line(self):self.bad(h.parse_pulses_stdout,b'\n'.join(self.stdout.split(b'\n')[1:]))
 def test_stdout_wrong_group_count(self):self.bad(h.parse_pulses_stdout,self.stdout.replace(b'cases=60',b'cases=61',1))
 def test_stdout_zero_assertions(self):self.bad(h.parse_pulses_stdout,self.stdout.replace(b'123456 assertions',b'0 assertions'))
 def test_stdout_bad_transfer(self):self.bad(h.parse_pulses_stdout,self.stdout.replace(b'copied=1176',b'copied=1175',1))
 def test_stdout_bad_legacy(self):self.bad(h.parse_pulses_stdout,self.stdout.replace(b'opaque_clears=17',b'opaque_clears=16',1))
 def test_stdout_wrong_case_total(self):self.bad(h.parse_pulses_stdout,self.stdout.replace(b'578 cases',b'577 cases'))
 def test_stdout_bytes_only(self):self.bad(h.parse_pulses_stdout,self.stdout.decode())
 def test_strict_json(self):
  with self.assertRaises(AssertionError):json.loads('{"a":1,"a":2}',object_pairs_hook=h.unique_object)
  with self.assertRaises(AssertionError):json.loads('{"a":NaN}',parse_constant=h.reject_constant)
 def test_exact_types(self):
  for x,y in ((True,1),(166.0,166),([1],(1,)),({'a':1.0},{'a':1})):self.bad(h.exact_equal,x,y)
 def test_no_symlink_or_hardlink_reads(self):
  with tempfile.TemporaryDirectory(dir=os.environ.get('OPENTYRIAN_TEST_TMPDIR')) as d:
   p=Path(d);(p/'a').write_bytes(b'a');(p/'s').symlink_to(p/'a');self.bad(h.regular_bytes,p/'s');(p/'b').hardlink_to(p/'a');self.bad(h.regular_bytes,p/'a')
 def test_path_escape(self):
  for name in ('../foo','/foo','foo/../bar','foo//bar'):self.bad(h.installed_path,N,name)
 def test_fulltile_loop_bound(self):
  self.assertNotIn('12752',self.c);self.assertTrue(all(x=='10752' for x in re.findall(r'for\(unsigned i=0;i<(\d{5});i\+\+\)',self.c)))
 def test_groups_c_exact(self):
  groups=tuple((n,int(c)) for n,c in re.findall(r'pulses16694_group\("([^"]+)",b,(\d+)\)',self.c));self.assertEqual(groups,h.GROUPS);self.assertEqual(len(groups),27);self.assertEqual(sum(c for _,c in groups),578)
 def test_unsigned_members(self):
  self.assertIn('pulses16694_ids[12]={91,145,61,101,120,139,168,169,162,260,166,94}',self.c);self.assertIn('return 1u<<k',self.c);self.assertIn('4095u&~',self.c);self.assertIn('s?2048u:1024u',self.c)
 def test_direct_first_final_does_not_preflight(self):
  body=self.c.split('static void pulses16694_used_resource_direct(void)',1)[1].split('static void ',1)[0]
  tail=body.split('switch(mode)',1)[1];self.assertNotIn('pulses16694_draw(',tail);self.assertIn('if(cached)global_projectile91_check_cache();else finish();',tail)
 def test_actual_legacy_finish_not_reject_assignment(self):
  body=self.c.split('static void pulses16694_legacy_final(void)',1)[1].split('static void pulses16694_group(',1)[0]
  self.assertIn('finish();CHECK(ready',body);self.assertNotRegex(body,r'reject_reason\s*=[^=]');self.assertIn('font_context=-1',body);self.assertIn('game_probe_enabled=true',body)
 def test_opaque_foreign_separate(self):self.assertIn('clears==(s?17u:0u)',self.c);self.assertIn('soft_expected[2]={1176,1081}',self.c);self.assertIn('opaque==40',self.c)
 def test_fixed_two_rows_no_search(self):self.assertIn('40+40*(int)(k%6)',self.c);self.assertIn('60+40*(int)(k/6)',self.c);self.assertIn('alpha_common==0&&native_common==0',self.c)
 def test_complete_talon_owner_read(self):self.assertIn('prior_talon[i]=mixed&&global_talon_owner',self.c);self.assertIn('talon_before[i]=global_talon_owner',self.c)
 def test_original_companion_untouched(self):self.assertEqual(h.SHA((N/'tests/projectile_statics_native_additions.c.inc').read_bytes()),h.STATICS_COMPANION_SHA)
class PortableContracts(unittest.TestCase):
 def test_import_inert_no_io(self):
  raw=(P/'projectile_pulses16694_native_validation.py').read_bytes();module=types.ModuleType('__main__');module.__file__=str(P/'projectile_pulses16694_native_validation.py')
  with mock.patch.object(Path,'read_bytes',side_effect=AssertionError('read')),mock.patch.object(Path,'write_bytes',side_effect=AssertionError('write')):exec(compile(raw,module.__file__,'exec'),module.__dict__)
 def test_portable_no_private_fallback(self):
  raw=(P/'projectile_pulses16694_native_validation.py').read_text()
  for token in ('/workspace/','ART_INDEX_SHA','REGISTRATION_RECEIPT_SHA','CORRECTION/','P3/','subprocess','__main__'):self.assertNotIn(token,raw)
  for name in ('native_inputs','pulses_native_input','registration','registered_rgba','registered_hdas','source_bundle'):
   self.assertTrue(all(p.default is p.empty for p in inspect.signature(getattr(h,name)).parameters.values()))
 def test_companion_exact_exercised_bytes(self):self.assertEqual(h.SHA((P/'projectile_pulses16694_native_additions.c.inc').read_bytes()),h.PULSES_COMPANION_SHA)
 def test_installed_hda_bytes_not_regenerated(self):
  for i,raw in h.registered_hdas(N).items():self.assertEqual(raw,(N/h.ASSET_DIRECTORY/h.HDA_NAMES[i]).read_bytes())
 def test_coverage_actual_sha_and_schema(self):
  raw=(N/h.COVERAGE_PATH).read_bytes();self.assertEqual(h.SHA(raw),h.COVERAGE_SHA);h.exact_equal(json.loads(raw),h.COVERAGE_SPEC)
 def test_coverage_reject_float_bool_unknown(self):
  for mutate in ('float','bool','unknown'):
   c=copy.deepcopy(h.COVERAGE_SPEC)
   if mutate=='float':c['members']['166']['native_occupied_cells']=97.0
   elif mutate=='bool':c['members']['94']['pixels']['outside_nonzero']=False
   else:c['other']=0
   with self.assertRaises(AssertionError):h.exact_equal(c,h.COVERAGE_SPEC)
 def test_all_twelve_identity_bits_exact(self):
  self.assertEqual(len(h.IDS),12);self.assertEqual(h.PULSES,(166,94));self.assertEqual(h.STATICS,(162,260));self.assertEqual(h.GOLD,(168,169));self.assertEqual(sum(1<<i for i in range(12)),4095)
 def test_capture_exact_successful_wrapper(self):
  _,final=h.source_bundle(N);self.assertEqual((len(final),h.SHA(final)),(3728,h.CAPTURE_WRAPPER_SHA));self.assertIn(b'--render-no-capture',final)
 def test_capture_four_layer_inverse(self):
  original,final=h.source_bundle(N);s=h.statics_helper(N);p=h.reverse_capture_wrapper(final);st=h.reverse_shim(p);g=s.reverse_shim(st);last=s.gold_helper(N).reverse_shim(g)
  self.assertEqual([len(x) for x in (final,p,st,g,last)],[3728,979,729,497,262]);self.assertEqual(last,original['harness.c'])
 def test_capture_reject_wrongflag_or_guard(self):
  _,final=h.source_bundle(N)
  for bad in (final.replace(b'--render-no-capture',b'--render-no-capturX'),final.replace(b'||!game_probe_capture_tick())abort();',b')abort();',1),final+b'\n'):
   self.assertNotEqual(bad,final)
   with self.assertRaises(AssertionError):h.reverse_capture_wrapper(bad)
 def test_capture_reject_double_wrapper(self):
  _,final=h.source_bundle(N)
  with self.assertRaises(AssertionError):h.capture_wrapper(final)
 def test_capture_real_parser_contract(self):
  self.assertEqual(set(h.capture_production_contract(N)),{'src/asset_debug.c','src/game_probe.c'})
  self.assertIn(b'game_probe_parse(&positive_argc,positive_argv)',h.CAPTURE_NEW);self.assertIn(b'game_probe_parse(&capture_argc,capture_argv)',h.CAPTURE_NEW)
  self.assertIn('asset_debug_parse(argc,argv)',h.CAPTURE_PRODUCTION_FILES['src/game_probe.c']['functions']['void game_probe_parse(int *argc, char **argv)']['body'])
 def test_capture_default_positive_and_disable_negative(self):
  self.assertIn(b'||game_probe_capture_disabled()||!game_probe_capture_tick())abort();',h.CAPTURE_NEW)
  self.assertIn(b'||!game_probe_capture_disabled()||game_probe_capture_tick())abort();',h.CAPTURE_NEW)
 def test_capture_contract_reject_mutated_actual_consumer(self):
  real=h.regular_bytes
  def altered(path,*args):
   raw=real(path,*args)
   return raw+b' ' if Path(path).name=='game_probe.c' else raw
  with mock.patch.object(h,'regular_bytes',side_effect=altered),self.assertRaises(AssertionError):h.capture_production_contract(N)
 def test_capture_old_five_dispatch_unchanged(self):
  _,final=h.source_bundle(N)
  self.assertEqual(final.replace(h.CAPTURE_NEW,h.CAPTURE_OLD,1),h.reverse_capture_wrapper(final))
  self.assertEqual(final.count(b' return inherited_statics_dispatch(argc,argv);'),1)
 def test_palette_actual_production_definition(self):
  self.assertEqual(h.production_palette_contract(N),h.SHA(h.NORMAL15_PALETTE_FUNCTION))
  self.assertIn(b'0x5e80e83992be2927',h.NORMAL15_PALETTE_FUNCTION)
 def test_palette_complete256_no_sample_shortcut(self):
  self.assertEqual(len(h.NORMAL15_PALETTE_FUNCTION)>100,True)
  source=inspect.getsource(h.pulses_native_input)
  self.assertIn('palette[3840:4608]',source);self.assertIn('range(0,768,3)',source);self.assertIn('range(0,1024,4)',source)
  for raw in (b'',bytes(767),bytes(769),bytearray(768)):
   with self.assertRaises(AssertionError):h.checked_palette5_rgb(raw)
 def test_fullpalette_unused_index208_detected(self):
  a=bytes(768);b=bytearray(a);b[208*3]=1
  self.assertNotEqual(h.fnv_rgb24(a),h.fnv_rgb24(bytes(b)))
  with self.assertRaises(AssertionError):h.checked_palette5_rgb(bytes(b))
 def test_sixth_input_rejects_unpinned_old_stream(self):
  for bad in (bytes(98980),b'',bytearray(98980)):
   with self.assertRaises(AssertionError):h.pulses_native_input(N,N,bad)
 def test_original_data_explicit_no_private_default(self):
  blue=h.statics_helper(N).gold_helper(N).blue_helper(N)
  self.assertEqual(h.DATA_PINS,blue.DATA_SHA)
  self.assertEqual(blue.NEW_STDIN_SHA,'a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b')
  self.assertEqual(h.PULSES_STDIN_SHA,'723d7a7a431b202419c12cce25e7298c2db9e9c5d88ac42cb7dc95fe51fcb463')
  with tempfile.TemporaryDirectory(dir=os.environ.get('OPENTYRIAN_TEST_TMPDIR')) as tmp:
   with self.assertRaises(OSError):h.native_inputs(N,Path(tmp))
 def test_sixth_stdout_exact_actual_result(self):
  result=h.verify_pulses_stdout(ACTUAL_PULSES_STDOUT);self.assertEqual((result['cases'],result['assertions']),(578,143860156))
  self.assertEqual(h.verify_legacy_stdout(EXPECTED_OLD_STDOUT)['assertions']+result['assertions'],285458804)
 def test_sixth_stdout_exact_rejects_synthetic_positive(self):
  wrong=ACTUAL_PULSES_STDOUT.replace(b'143860156 assertions',b'143860157 assertions')
  self.assertEqual(h.parse_pulses_stdout(wrong)['assertions'],143860157)
  with self.assertRaises(AssertionError):h.verify_pulses_stdout(wrong)
 def test_coverage_must_be_present_in_explicit_root(self):
  with tempfile.TemporaryDirectory(dir=os.environ.get('OPENTYRIAN_TEST_TMPDIR')) as tmp:
   with self.assertRaises(OSError):h.registration(Path(tmp))

if __name__=='__main__':unittest.main(verbosity=2)
