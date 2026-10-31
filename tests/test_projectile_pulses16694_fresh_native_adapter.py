"""Pure fresh-driver contracts. No compiler, Makefile, native process or main().
Temporary fixtures are tiny; a mocked process is never an actual subprocess.
The sibling installed helper is the only native-helper source, no fallback.
"""
from pathlib import Path
import ast,hashlib,importlib.util,inspect,io,json,os,subprocess,tempfile,unittest,stat
from types import SimpleNamespace
from unittest.mock import patch
HERE=Path(__file__).resolve().parent

def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

d=module(HERE/'projectile_pulses16694_fresh_native_validation.py','fresh_pulses_driver_pure')
h=module(HERE/'projectile_pulses16694_native_validation.py','fresh_pulses_native_pure')

OLD_STDOUT={'inherited107_stdout': b'PASS inherited91 native lifecycle: 37 cases 81611 assertions\n145_TO_TALON copied=376 cached=0\n145_TO_TALON copied=376 cached=1\nPASS shared145 native lifecycle: 70 new cases 141992 new assertions; internal8 only; not gameplay/full build\n', 'inherited61_stdout': b'61_TO_TALON copied=267 cached=0\n61_TO_TALON copied=267 cached=1\nPASS shared61 native lifecycle: 157 cases 822291 assertions; internal8 only; not gameplay/full build\n', 'new_blue_stdout': b'BLUE101_ZERO_NATIVE pattern=0 draw=384 finish=384 cache=384\nBLUE101_ZERO_NATIVE pattern=1 draw=384 finish=384 cache=384\nBLUE101_ZERO_HD prior=120 draw=384 finish=384 cache=384\nBLUE_TO_TALON selector=101 copied=1756 soft=1721 cached=0\nBLUE_TO_TALON selector=101 copied=1756 soft=1721 cached=1\nBLUE_TO_TALON selector=120 copied=1864 soft=1864 cached=0\nBLUE_TO_TALON selector=120 copied=1864 soft=1864 cached=1\nBLUE_TO_TALON selector=139 copied=1481 soft=1454 cached=0\nBLUE_TO_TALON selector=139 copied=1481 soft=1454 cached=1\nPASS blue triplet native lifecycle: 365 cases 11162937 assertions; internal8 only; not gameplay/full build\n', 'gold251_stdout': b'GOLD_GROUP name=full_tile_native_patterns cases=4\nGOLD_GROUP name=bounds cases=18\nGOLD_GROUP name=pair_orders cases=26\nGOLD_GROUP name=all8_early_dependency cases=16\nGOLD_GROUP name=missing_bad cases=32\nGOLD_GROUP name=singletons_oldonly cases=4\nGOLD_GROUP name=malformed_gold cases=6\nGOLD_GROUP name=unused_memory_payload_ready cases=8\nGOLD_GROUP name=palette cases=40\nGOLD_GROUP name=used_resource_shared cases=64\nGOLD_GROUP name=callbacks cases=8\nGOLD_GROUP name=cold_scope cases=10\nGOLD_TO_TALON selector=168 copied=974 soft=974 alpha0=86 cached=0\nGOLD_TO_TALON selector=168 copied=974 soft=974 alpha0=86 cached=1\nGOLD_TO_TALON selector=169 copied=735 soft=735 alpha0=85 cached=0\nGOLD_TO_TALON selector=169 copied=735 soft=735 alpha0=85 cached=1\nGOLD_GROUP name=Talon_transfer cases=4\nGOLD_GROUP name=lifecycle cases=5\nGOLD_GROUP name=controlled_animation cases=6\nPASS gold pulse native lifecycle: 251 cases 38046959 assertions; internal8 only; not gameplay/full build\n'}

OLD_STDOUT['statics449_stdout']=b'STATICS_GROUP name=full_tile_native_patterns cases=4\nSTATICS_GROUP name=full_tile_hd_underlay cases=2\nSTATICS_GROUP name=bounds cases=22\nSTATICS_GROUP name=pair_orders_zero_isolation cases=34\nSTATICS_GROUP name=all10_same_origin_dependency cases=20\nSTATICS_GROUP name=all10_two_row_dependency cases=20\nSTATICS_GROUP name=missing_bad cases=40\nSTATICS_GROUP name=singletons_oldonly cases=4\nSTATICS_GROUP name=malformed_headers_lengths cases=18\nSTATICS_GROUP name=readiness_root_epochs cases=4\nSTATICS_GROUP name=unused_memory_payload_ready cases=8\nSTATICS_GROUP name=palette_admission_shared cases=24\nSTATICS_GROUP name=palette_direct_final_cache cases=38\nSTATICS_GROUP name=palette_composite_preflight cases=12\nSTATICS_GROUP name=used_resource_direct_final_cache cases=52\nSTATICS_GROUP name=source_scope_direct_final_cache cases=24\nSTATICS_GROUP name=layout_direct_final_cache cases=32\nSTATICS_GROUP name=callbacks cases=12\nSTATICS_GROUP name=cold_warm_scope cases=44\nSTATICS_TO_TALON selector=162 copied=526 soft=521 alpha0=35 cached=0\nSTATICS_TO_TALON selector=162 copied=526 soft=521 alpha0=35 cached=1\nSTATICS_TO_TALON selector=260 copied=1122 soft=1122 alpha0=6 cached=0\nSTATICS_TO_TALON selector=260 copied=1122 soft=1122 alpha0=6 cached=1\nSTATICS_GROUP name=Talon_transfer cases=4\nSTATICS_GROUP name=Talon_underlay_direct cases=8\nSTATICS_GROUP name=lifecycle cases=7\nSTATICS_GROUP name=later_native_final_writers cases=8\nSTATICS_GROUP name=fade_high_bits cases=8\nPASS enemy statics native lifecycle: 449 cases 91342858 assertions; internal8 only; not gameplay/full build\n'
PULSES_ACTUAL_STDOUT=b'PULSES16694_GROUP name=full_tile_native_patterns cases=4\nPULSES16694_GROUP name=full_tile_hd_underlay cases=2\nPULSES16694_GROUP name=bounds cases=22\nPULSES16694_GROUP name=pair_orders_zero_isolation cases=42\nPULSES16694_GROUP name=all12_same_origin_dependency cases=24\nPULSES16694_GROUP name=all12_two_row_dependency cases=24\nPULSES16694_GROUP name=missing_bad cases=48\nPULSES16694_GROUP name=singletons_oldonly cases=4\nPULSES16694_GROUP name=malformed_headers_lengths cases=18\nPULSES16694_GROUP name=readiness_root_epochs cases=4\nPULSES16694_GROUP name=unused_memory_payload_ready cases=8\nPULSES16694_GROUP name=palette_admission_shared cases=60\nPULSES16694_GROUP name=palette_direct_final_cache cases=66\nPULSES16694_GROUP name=palette_composite_preflight cases=29\nPULSES16694_GROUP name=used_resource_direct_final_cache cases=52\nPULSES16694_GROUP name=source_scope_direct_final_cache cases=24\nPULSES16694_GROUP name=layout_direct_final_cache cases=32\nPULSES16694_GROUP name=callbacks cases=12\nPULSES16694_GROUP name=cold_warm_scope cases=44\nPULSES16694_TO_TALON selector=166 copied=1176 soft=1176 alpha0=133 cached=0\nPULSES16694_TO_TALON selector=166 copied=1176 soft=1176 alpha0=133 cached=1\nPULSES16694_TO_TALON selector=94 copied=1081 soft=1081 alpha0=56 cached=0\nPULSES16694_TO_TALON selector=94 copied=1081 soft=1081 alpha0=56 cached=1\nPULSES16694_GROUP name=Talon_transfer cases=4\nPULSES16694_GROUP name=Talon_underlay_direct cases=8\nPULSES16694_GROUP name=lifecycle cases=7\nPULSES16694_GROUP name=later_native_final_writers cases=8\nPULSES16694_GROUP name=fade_high_bits cases=8\nPULSES16694_GROUP name=player_generic_aliases cases=8\nPULSES16694_GROUP name=all12_fade_lease cases=4\nPULSES16694_LEGACY context=0 selector=166 mixed=0 kept=6208 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=0 selector=166 mixed=1 kept=3008 dropped=3200 opaque_clears=0\nPULSES16694_LEGACY context=0 selector=94 mixed=0 kept=6912 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=0 selector=94 mixed=1 kept=3409 dropped=3503 opaque_clears=17\nPULSES16694_LEGACY context=1 selector=166 mixed=0 kept=6208 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=1 selector=166 mixed=1 kept=3008 dropped=3200 opaque_clears=0\nPULSES16694_LEGACY context=1 selector=94 mixed=0 kept=6912 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=1 selector=94 mixed=1 kept=3409 dropped=3503 opaque_clears=17\nPULSES16694_LEGACY context=2 selector=166 mixed=0 kept=6208 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=2 selector=166 mixed=1 kept=3008 dropped=3200 opaque_clears=0\nPULSES16694_LEGACY context=2 selector=94 mixed=0 kept=6912 dropped=0 opaque_clears=0\nPULSES16694_LEGACY context=2 selector=94 mixed=1 kept=3409 dropped=3503 opaque_clears=17\nPULSES16694_GROUP name=legacy_reject_own_foreign cases=12\nPASS enemy pulses16694 native lifecycle: 578 cases 143860156 assertions; internal8 only; not gameplay/full build\n'

def source_fixture():
 names=['entity_draw.c','tyrian2.c','render_mirror.c']+[f'unit{i}.c' for i in range(83)]+['global_projectile91_mirror.inc']+[f'header{i}.h' for i in range(229)]
 old={n:'0'*64 for n in names};return old,{**old,**d.PRODUCTION6}

def compile_log(mode):
 units=[f'unit{i}' for i in range(86)];flags=['cc','-MD','-DNDEBUG']+d.MODES[mode].split()
 flags+=(['-O1','-g',*d.SAN] if mode=='hd-on-asan-ubsan' else ['-O2'])
 lines=[' '.join([*flags,'-c','-o','obj/'+u+'.o','src/'+u+'.c']) for u in units]
 lines.append(' '.join(['cc',*(['-fsanitize=address,undefined','-no-pie'] if mode=='hd-on-asan-ubsan' else []),'-o','opentyrian2000',*('obj/'+u+'.o' for u in units)]))
 return '\n'.join(lines)+'\n',units

class FreshPulsesPure(unittest.TestCase):
 def test_01_budgets_peak_final_reserve(self):
  self.assertTrue(d.budget_ok(448*1024**2,250*1024**2))
  self.assertFalse(d.budget_ok(448*1024**2+1,250*1024**2))
  self.assertFalse(d.budget_ok(1,250*1024**2-1))
  self.assertTrue(d.budget_ok(320*1024**2,250*1024**2,True))
  self.assertFalse(d.budget_ok(320*1024**2+1,250*1024**2,True))
  self.assertEqual(d.START_REQUIRED,731906048)

 def test_02_actual_snapshot_allocation(self):
  self.assertEqual(d.snapshot_allocation(b'',b'a',b'b'*4096,b'c'*4097),16384)

 def test_03_allocated_includes_root_and_directories(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'nested').mkdir();(root/'nested/a').write_bytes(b'a');(root/'link').symlink_to('nested/a')
   self.assertEqual(d.allocated(root),sum(p.lstat().st_blocks*512 for p in (root,*root.rglob('*'))))

 def test_04_four_mode_flags_serial_j2(self):
  self.assertEqual(tuple(d.MODES),('default-off','hd-on','mirror-disabled','hd-on-asan-ubsan'))
  for name in d.MODES:
   argv=d.make_command(name,Path('/sysroot'),Path('/cc'),Path('/pkg'))
   self.assertEqual(argv[:2],['make','-j2']);cpp=next(a for a in argv if a.startswith('CPPFLAGS='))
   self.assertIn('-MD',cpp);self.assertIn('-DNDEBUG',cpp)
   self.assertEqual('-DNEWSHF_HD_COMPOSITOR=1' in cpp,name!='default-off')
   self.assertEqual('-DRENDER_MIRROR_DISABLED' in cpp,name=='mirror-disabled')
   cflags=next(a for a in argv if a.startswith('CFLAGS='))
   self.assertEqual('-fsanitize=address,undefined' in cflags,name=='hd-on-asan-ubsan')
   if name=='hd-on-asan-ubsan':
    for f in ('-O1','-g',*d.SAN):self.assertIn(f,cflags)

 def test_05_actual86_compile_and_link_contract(self):
  for mode in d.MODES:
   log,units=compile_log(mode);compiles,link=d.compile_contract(log,units,mode)
   self.assertEqual(len(compiles),86);self.assertEqual(len([a for a in link if a.endswith('.o')]),86)

 def test_06_reject_duplicate_or_missing_compile(self):
  log,units=compile_log('hd-on');lines=log.splitlines()
  for bad in ('\n'.join(lines[1:]),'\n'.join([lines[0],*lines[2:],lines[0]])):
   with self.assertRaises(AssertionError):d.compile_contract(bad,units,'hd-on')

 def test_07_reject_wrong_sanitizer_and_macros(self):
  log,units=compile_log('hd-on-asan-ubsan')
  for token in ('-g ','-fno-omit-frame-pointer ','-fsanitize=address,undefined ','-DNEWSHF_HD_COMPOSITOR=1 '):
   with self.subTest(token=token):
    with self.assertRaises(AssertionError):d.compile_contract(log.replace(token,'',1),units,'hd-on-asan-ubsan')
  log,units=compile_log('mirror-disabled')
  with self.assertRaises(AssertionError):d.compile_contract(log.replace('-DRENDER_MIRROR_DISABLED ',''),units,'mirror-disabled')

 def test_08_no_extra_or_external_link_object(self):
  log,units=compile_log('hd-on')
  for bad in (log.replace(' -o opentyrian2000 ',' -o opentyrian2000 /old/cold.o '),log.replace('obj/unit0.o\n','/old/unit0.o\n')):
   # The second mutation must target the link rather than a compilation path.
   if bad==log:bad=log.rsplit('obj/unit0.o',1)[0]+'/old/unit0.o'+log.rsplit('obj/unit0.o',1)[1]
   with self.assertRaises(AssertionError):d.compile_contract(bad,units,'hd-on')

 def test_09_native_link_only84new_plus_fresh_main(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);build=out/'hd-on-asan-ubsan-build';(build/'obj').mkdir(parents=True)
   names=['render_mirror','opentyr']+[f'unit{i}' for i in range(84)]
   for name in names:(build/'obj'/(name+'.o')).write_bytes(b'')
   cc,link,objects=d.native_compile_commands(Path('/cc'),build,out,[],['-lSDL2'])
   self.assertEqual(len(objects),85);self.assertEqual(len([p for p in link if str(p).endswith('.o')]),85)
   self.assertNotIn(str(build/'obj/render_mirror.o'),link);self.assertNotIn(str(build/'obj/opentyr.o'),link)
   self.assertTrue(all(p.is_relative_to(build) for p in objects));self.assertIn('-Dmain=unused_game_main',cc)
   self.assertIn(str(out/'pulses16694-wrapper.c'),link)
   for flag in (*d.SAN,'-O1','-g'):self.assertIn(flag,link)

 def test_10_source316_exact_six_overlays(self):
  old,new=source_fixture();self.assertTrue(d.check_source_epoch(new,old))
  bad=dict(new);bad['entity_draw.c']='f'*64
  with self.assertRaises(AssertionError):d.check_source_epoch(bad,old)
  bad=dict(new);bad['header0.h']='f'*64
  with self.assertRaises(AssertionError):d.check_source_epoch(bad,old)
  del bad['enemy_pulses16694_mirror.inc']
  with self.assertRaises(AssertionError):d.check_source_epoch(bad,old)

 def test_11_original880_full_stdout_bytes_and_crlf_rejected(self):
  outputs=dict(OLD_STDOUT);self.assertTrue(d.validate_stdout_bytes(outputs))
  for name in outputs:
   bad=dict(outputs);bad[name]=bad[name].replace(b'\n',b'\r\n')
   with self.assertRaises(AssertionError):d.validate_stdout_bytes(bad)
   bad=dict(outputs);bad[name]+=b' '
   with self.assertRaises(AssertionError):d.validate_stdout_bytes(bad)

 def test_12_all_six_source_and_262_shim_constants(self):
  self.assertEqual(d.SOURCE_PINS,h.SOURCE_PINS)
  old,wrapper=h.source_bundle(HERE.parent);middle=h.reverse_capture_wrapper(wrapper);statics_wrapper=h.reverse_shim(middle);statics=h.statics_helper(HERE.parent);gold_wrapper=statics.reverse_shim(statics_wrapper)
  self.assertEqual(d.digest(gold_wrapper),d.GOLD_WRAPPER_SHA);self.assertEqual(d.digest(statics_wrapper),d.STATICS_WRAPPER_SHA)
  self.assertEqual(statics.gold_helper(HERE.parent).reverse_shim(gold_wrapper),old['harness.c'])
  self.assertEqual(len(old['harness.c']),262);self.assertNotEqual(wrapper,gold_wrapper)

 def test_13_current_root_only_helper_and_no_fallback(self):
  self.assertRegex(d.NATIVE_HELPER_SHA,r'^[0-9a-f]{64}$')
  self.assertEqual(d.SHA(HERE/'projectile_pulses16694_native_validation.py'),d.NATIVE_HELPER_SHA)
  with patch.object(d,'read_bound',side_effect=AssertionError('actual helper mismatch')):
   with self.assertRaises(AssertionError):d.load_native(Path('/not-an-external-fallback'))
  body=inspect.getsource(d.load_native);self.assertNotIn('.parent',body);self.assertNotIn('try:',body)

 def test_14_no_historical_build_inputs_in_main(self):
  body=inspect.getsource(d.main)
  for forbidden in ('accepted61-fresh','prior-blue-native','restored_deps','native-preparation-v2','hd-on-build/obj','recovered-native-dependency-closure','Q/','OLD_Q'):
   self.assertNotIn(forbidden,body)
  self.assertIn("'historical_consumers':{}",body);self.assertIn("'historical_objects_consumed':0",body);self.assertIn("'historical_depfiles_consumed':0",body)

 def test_15_dependency_tokens_spaces_and_continuation(self):
  self.assertEqual(d.dependency_tokens('a.o: src/a.c \\\n dir/b\\ c.h\n'),['src/a.c','dir/b c.h'])
  with self.assertRaises(AssertionError):d.dependency_tokens('no rule')

 def test_16_actual_symlink_target_and_text_bound(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'include').mkdir();(p/'real.h').write_bytes(b'yes');(p/'include/alias.h').symlink_to('../real.h');links={}
   self.assertEqual(d.resolve_traced(p/'include/alias.h',links),p/'real.h');self.assertEqual(links,{str(p/'include/alias.h'):'../real.h'})
   (p/'include/alias.h').unlink();(p/'include/alias.h').symlink_to('../absent.h')
   with self.assertRaises(AssertionError):d.resolve_traced(p/'include/alias.h',links)

 def test_17_inventory_no_symlinks_or_hardlinks(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'a').write_bytes(b'a');good=d.inventory(p);self.assertEqual(set(good),{'a'})
   (p/'b').symlink_to('a')
   with self.assertRaises(AssertionError):d.inventory(p)
   (p/'b').unlink();os.link(p/'a',p/'b')
   with self.assertRaises(AssertionError):d.inventory(p)

 def test_18_full_hydration_and_stage0_required(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'a').write_bytes(b'a')
   def git(root,*args):
    if args==('ls-files','-t','-z'):return b'S a\0'
    raise AssertionError('Should reject before another query')
   with patch.object(d,'git',git):
    with self.assertRaises(AssertionError):d.hydrated_manifest(p)
   def git(root,*args):
    return b'H a\0' if args==('ls-files','-t','-z') else b'100644 abc 2\ta\0'
   with patch.object(d,'git',git):
    with self.assertRaises(AssertionError):d.hydrated_manifest(p)

 def test_19_environment_no_compiler_or_test_inheritance(self):
  with patch.dict(os.environ,{'CFLAGS':'BAD','LD_PRELOAD':'BAD','GOLD_INVUL':'2000','MAKEFLAGS':'-j99'}):env=d.environment(Path('/sysroot'),Path('/tmpx'),Path('/homex'))
  for key in ('CFLAGS','LD_PRELOAD','GOLD_INVUL','MAKEFLAGS'):self.assertNotIn(key,env)
  self.assertEqual(env['ASAN_OPTIONS'],'detect_leaks=0:halt_on_error=1');self.assertEqual(env['TMPDIR'],'/tmpx')

 def test_20_initialization_inside_guard_and_postreceipt_budget(self):
  tree=ast.parse(inspect.getsource(d.main));main=tree.body[0]
  owner=next(n for n in main.body if isinstance(n,ast.Try) and any(isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Attribute) and x.value.func.attr=='mkdir' for x in n.body))
  self.assertTrue(owner.handlers);text=ast.get_source_segment(inspect.getsource(d.main),owner)
  self.assertIn("report['status_before_final_checks']",text);self.assertIn('save();measure(final=True)',text);self.assertIn('last_actual_budget(',text)

 def test_21_guarded_final_error_does_not_raise_or_replace_original(self):
  checks={};errors={}
  def fail():raise OSError('original-source-read')
  self.assertFalse(d.guarded_check(checks,errors,'one',fail));self.assertIn('original-source-read',errors['one'])

 def test_22_last_budget_read_failure_preserves_error(self):
  report={'status':'FAIL_RETAINED','error':'first-error'};errors={};calls=[]
  with patch.object(d,'allocated',side_effect=OSError('final disk read')):result=d.last_actual_budget(Path('/any'),report,errors,lambda:calls.append(1))
  self.assertFalse(result['last_budget_ok']);self.assertEqual(report['error'],'first-error');self.assertIn('final disk read',errors['last_actual_budget']);self.assertEqual(len(calls),1)

 def test_23_exited_between_poll_and_kill_is_reaped(self):
  class Fake:
   pid=7
   def poll(self):return None
   def wait(self,timeout):self.timeout=timeout;return 0
  proc=Fake();row={}
  with patch.object(d.os,'killpg',side_effect=ProcessLookupError()):d.stop_process(proc,row)
  self.assertEqual(row['cleanup_errors'],[]);self.assertEqual(proc.timeout,5)

 def test_24_kill_failures_bounded_and_secondary(self):
  class Fake:
   pid=7
   calls=0
   def poll(self):return None
   def wait(self,timeout):self.calls+=1;raise subprocess.TimeoutExpired('mock',timeout)
  proc=Fake();row={}
  with patch.object(d.os,'killpg',side_effect=PermissionError('fake-kill')):d.stop_process(proc,row)
  self.assertEqual(proc.calls,2);self.assertEqual(len(row['cleanup_errors']),3)

 def test_25_save_failure_before_feeder_start_not_masked(self):
  class FakeProc:
   pid=7;returncode=None;stdin=io.BytesIO()
   def poll(self):return self.returncode
   def wait(self,timeout=None):self.returncode=-15;return self.returncode
  class FakeThread:
   ident=None
   def __init__(self,**kwargs):pass
   def start(self):raise AssertionError('Must not start after save error')
   def join(self,**kwargs):raise AssertionError('Must not join unstarted thread')
  count=[0]
  def save():
   count[0]+=1
   if count[0]==2:raise OSError('first-save-error')
  with tempfile.TemporaryDirectory() as tmp,patch.object(d.subprocess,'Popen',return_value=FakeProc()),patch.object(d.threading,'Thread',FakeThread),patch.object(d.os,'killpg'):
   report={'commands':[]}
   with self.assertRaisesRegex(OSError,'first-save-error'):d.run_process(['/no-execute'],'fake',Path(tmp),Path(tmp),report,save,lambda:None,{},b'data')
   self.assertIn('first-save-error',report['commands'][0]['original_error'])

 def test_26_all1329_counts_and_byte_read_contract(self):
  body=inspect.getsource(d.main)
  for text in ("len(report['fresh_dependency_file_sha256'])==346", "counts['cases']==578", "counts['assertions']==143860156",'total_cases=1907,total_assertions=285458804',"legacy_counts['cases']==1329","legacy_counts['assertions']==141598648"):
   self.assertIn(text,body)
  self.assertIn(".read_bytes()",inspect.getsource(d.run_process));self.assertNotIn('.read_text()',inspect.getsource(d.run_process))
  self.assertIn("('gold251','gold251_stdout'",body);self.assertIn("[exe,'--enemy-statics'",body)

 def test_27_real_companion_output_schema_kept(self):
  p=HERE/'projectile_statics_native_additions.c.inc';self.assertEqual(d.SHA(p),d.STATICS_COMPANION_SHA)
  text=p.read_text();self.assertIn('STATICS_GROUP name=%s cases=%u',text);self.assertIn('STATICS_TO_TALON selector=%u copied=%u soft=%u alpha0=%u cached=%u',text)
  old=h.statics_helper(HERE.parent);self.assertEqual(sum(n for _,n in old.GROUPS),449);self.assertEqual(len(old.GROUPS),24);self.assertEqual(old.TRANSFER,{162:(526,521,35),260:(1122,1122,6)})
  self.assertEqual(d.SHA(HERE/'projectile_gold_pulse_native_additions.c.inc'),d.GOLD_COMPANION_SHA)

 def test_28_current_compiler_runtime_targets_and_script_are_bound(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'actual-libgcc_s.so.1').write_bytes(b'\x7fELFshared')
   for name in d.COMPILER_LINK_NAMES:
    path=root/name
    if name=='libgcc_s.so.1':path.symlink_to('actual-libgcc_s.so.1')
    else:path.write_bytes(b'\x7fELFstartup')
   for name in ('libgcc.a','libc_nonshared.a'):(root/name).write_bytes(b'!<arch>\narchive')
   for name,text in d.SCRIPT_TEXT.items():(root/name).write_text('/* GNU ld script */ '+text)
   links={};calls=[]
   def query(argv,env):
    calls.append(argv);return str(root/argv[1].split('=',1)[1]).encode()+b'\n'
   resolve=d.resolve_traced
   def traced(path,links):return resolve(root/path.name if str(path).startswith(('/lib/','/lib64/','/usr/lib/')) else path,links)
   with patch.object(d.subprocess,'check_output',side_effect=query),patch.object(d,'resolve_traced',side_effect=traced):pins,records=d.compiler_link_inputs(Path('/current/cc'),{},links)
   self.assertEqual(len(calls),21);self.assertEqual(set(records),set(d.COMPILER_LINK_NAMES))
   self.assertEqual(records['libgcc_s.so']['script_targets'],['libgcc_s.so.1','libgcc.a'])
   self.assertEqual(pins[str(root/'actual-libgcc_s.so.1')],d.SHA(root/'actual-libgcc_s.so.1'))
   self.assertEqual(links,{str(root/'libgcc_s.so.1'):'actual-libgcc_s.so.1'})
   for row in records.values():self.assertEqual(pins[row['resolved_path']],row['sha256'])

 def test_29_unresolved_compiler_runtime_input_rejected(self):
  with patch.object(d.subprocess,'check_output',return_value=b'crt1.o\n'):
   with self.assertRaisesRegex(AssertionError,'Unresolved compiler link input'):d.compiler_link_inputs(Path('/cc'),{}, {})

 def test_30_unknown_linker_script_dependency_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   for name in d.COMPILER_LINK_NAMES:(root/name).write_bytes(b'\x7fELF')
   (root/'libgcc_s.so').write_bytes(b'GROUP ( libgcc_s.so.1 -lgcc -lUNBOUND )')
   def query(argv,env):return str(root/argv[1].split('=',1)[1]).encode()
   with patch.object(d.subprocess,'check_output',side_effect=query):
    with self.assertRaisesRegex(AssertionError,'Unrecognized libgcc_s linker-script'):d.compiler_link_inputs(Path('/cc'),{}, {})
   body=inspect.getsource(d.main)
   self.assertIn('tools.update(compiler_link_pins)',body)
   self.assertIn("compiler_link_inputs=compiler_link_records",body)
   self.assertIn("all(SHA(p)==v for p,v in bound.items())",body)

 def test_31_log_cap_and_true_qualified_gold_identity(self):
  self.assertTrue(d.budget_ok(1,d.RESERVE,logs=48*1024**2))
  self.assertFalse(d.budget_ok(1,d.RESERVE,logs=48*1024**2+1))
  self.assertEqual(d.FINAL_CAP,335544320);self.assertEqual(d.PROTECTED_IDENTITY['head'],'5e73a699a2028ad3cb49b15435b6dde24bb2392f')
  self.assertEqual(d.PROTECTED_IDENTITY['raw_sha256'],'89d76b29a089596b22b7abb5bc7c80c6517ae9dbab437e6b8507059a942f6281')
  self.assertIn("len(profile['worktree'])==9830",inspect.getsource(d.protected_manifest))

 def test_32_only_new_stage_tmp_enoent_is_tolerated_and_recorded(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   with self.assertRaises(FileNotFoundError):d.allocated(root/'absent')
   (root/'tmp').mkdir();(root/'tmp/transient').write_bytes(b'a');original=Path.lstat;races=[]
   def lstat(path,*args,**kwargs):
    if path==root/'tmp/transient':raise FileNotFoundError(str(path))
    return original(path,*args,**kwargs)
   with patch.object(Path,'lstat',lstat):d.allocated(root,races)
   self.assertEqual(races[0]['path'],str(root/'tmp/transient'));self.assertGreater(races[0]['utc_ns'],0)
   with patch.object(Path,'lstat',lstat),self.assertRaises(FileNotFoundError):d.allocated(root)
   (root/'evidence').write_bytes(b'a')
   def lstat(path,*args,**kwargs):
    if path==root/'evidence':raise FileNotFoundError(str(path))
    return original(path,*args,**kwargs)
   with patch.object(Path,'lstat',lstat),self.assertRaises(FileNotFoundError):d.allocated(root,[])

 def test_33_all_three_scripts_targets_and_archive_format_required(self):
  self.assertEqual(set(d.SCRIPT_TEXT),{'libgcc_s.so','libc.so','libm.so'})
  self.assertEqual({n for n,_ in d.SCRIPT_TARGETS['libc.so']},{'libc.so.6','libc_nonshared.a','ld-linux-x86-64.so.2'})
  self.assertEqual({n for n,_ in d.SCRIPT_TARGETS['libm.so']},{'libm.so.6','libmvec.so.1'})
  body=inspect.getsource(d.compiler_link_inputs)
  self.assertIn("startswith(b'!<arch>",body);self.assertIn('Script target differs from compiler query',body)
  self.assertIn('resolved_script_targets',body)

 def test_34_sdl_order_and_sysroot_shadows_rejected(self):
  with patch.object(d.subprocess,'check_output',return_value=b'-L/sys/usr/lib/x86_64-linux-gnu -lSDL2 -lSDL2_net'):
   with self.assertRaisesRegex(AssertionError,'link flags/order'):d.sdl_link_inputs(Path('/pkg'),Path('/sys'),{}, {})
  body=inspect.getsource(d.sdl_link_inputs);self.assertIn("'pkgconfig/sdl2.pc','pkgconfig/SDL2_net.pc'",body)
  self.assertIn("for name in ('c','m','asan','ubsan','gcc_s','gcc')",body)
  self.assertIn('not os.path.lexists(p)',body)

 def test_35_fifth_stdout_strict_actual_pin_and_counts(self):
  old=h.statics_helper(HERE.parent);lines=[]
  for name,count in old.GROUPS:
   if name=='Talon_transfer':
    for selector in old.STATICS:
     copied,soft,zero=old.TRANSFER[selector]
     for cached in (0,1):lines.append(f'STATICS_TO_TALON selector={selector} copied={copied} soft={soft} alpha0={zero} cached={cached}')
   lines.append(f'STATICS_GROUP name={name} cases={count}')
  lines.append('PASS enemy statics native lifecycle: 449 cases 91342858 assertions; internal8 only; not gameplay/full build')
  raw=('\n'.join(lines)+'\n').encode();self.assertEqual(old.parse_statics_stdout(raw)['assertions'],91342858)
  self.assertEqual((d.digest(raw),len(raw)),('fc00c7f5120d9670fc500e8692e418798b93029c7af261ae0f3629ce50f92aef',1577))
  for bad in (raw.replace(b'\n',b'\r\n'),raw[:-1],raw+b'\n',raw.replace(b'91342858',b'91342859')):
   with self.assertRaises(AssertionError):old.parse_statics_stdout(bad)

 def test_36_fixture102_and725_no_evidence_deletion(self):
  schema=h.fixture_schema();self.assertEqual(len(schema),46);self.assertEqual(sum(map(len,schema.values())),516)
  body=inspect.getsource(d.main)
  for text in ('len(old_fixtures)==725 and len(fixtures)==1241','len(leaves)==len(set(leaves))==148','all(fixtures[k]==v for k,v in old_fixtures.items())',"len(report['fixture_sha256'])==1241 and len(report['fixture_links'])==148"):
   self.assertIn(text,body)
  for text in ('unlink(', 'rmtree(', 'os.remove(', 'shutil.copytree('):self.assertNotIn(text,body)

 def test_37_initial_mkdir_failure_is_guarded_no_save_or_process(self):
  import sys
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);paths={n:root/n for n in ('root','data','sysroot','protected','stage')}
   for name,p in paths.items():
    if name!='stage':p.mkdir()
   argv=['driver','--root',str(paths['root']),'--stage',str(paths['stage']),'--data',str(paths['data']),'--sysroot',str(paths['sysroot']),'--protected-qualifiedstatics',str(paths['protected']),'--protected-profile',str(root/'profile'),'--root-snapshot',str(root/'snapshot'),'--root-snapshot-sha256','0'*64]
   original=Path.mkdir
   def mkdir(path,*args,**kwargs):
    if path==paths['stage']:raise OSError('first-mkdir-failure')
    return original(path,*args,**kwargs)
   with patch.object(sys,'argv',argv),patch.object(Path,'mkdir',mkdir),patch.object(d.shutil,'disk_usage',return_value=type('Usage',(),{'free':d.START_REQUIRED})()),patch.object(d.subprocess,'Popen',side_effect=AssertionError('No process')),patch('builtins.print'):
    with self.assertRaisesRegex(OSError,'first-mkdir-failure'):d.main()
   self.assertFalse(paths['stage'].exists())

 def test_38_existing_stage_never_overwritten_or_retried(self):
  import sys
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   for name in ('root','data','sysroot','protected','stage'):(root/name).mkdir()
   evidence=root/'stage/receipt.json';evidence.write_bytes(b'old FAIL')
   argv=['driver','--root',str(root/'root'),'--stage',str(root/'stage'),'--data',str(root/'data'),'--sysroot',str(root/'sysroot'),'--protected-qualifiedstatics',str(root/'protected'),'--protected-profile',str(root/'profile'),'--root-snapshot',str(root/'snapshot'),'--root-snapshot-sha256','0'*64]
   with patch.object(sys,'argv',argv),patch.object(d.subprocess,'Popen',side_effect=AssertionError('No process')),patch('builtins.print'):
    with self.assertRaises(AssertionError):d.main()
   self.assertEqual(evidence.read_bytes(),b'old FAIL')

 def test_39_postprocess_hash_error_preserves_first_process_error(self):
  class Fake:
   pid=7;returncode=None
   def poll(self):raise RuntimeError('first-poll-error')
   def wait(self,timeout=5):self.returncode=-9;return -9
  with tempfile.TemporaryDirectory() as tmp,patch.object(d.subprocess,'Popen',return_value=Fake()),patch.object(d.os,'killpg'),patch.object(d,'SHA',side_effect=OSError('secondary-hash-error')):
   report={'commands':[]}
   with self.assertRaisesRegex(RuntimeError,'first-poll-error'):d.run_process(['/fake'],'fake',Path(tmp),Path(tmp),report,lambda:None,lambda:None,{})
   self.assertIn('first-poll-error',report['commands'][0]['original_error']);self.assertIn('secondary-hash-error',str(report['commands'][0]['secondary_errors']))

 def test_40_unreaped_cleanup_is_unknown_and_not_success(self):
  class Fake:
   pid=7
   def wait(self,timeout):raise subprocess.TimeoutExpired('fake',timeout)
  row={}
  with patch.object(d.os,'killpg'):self.assertFalse(d.stop_process(Fake(),row))
  self.assertTrue(row['cleanup_incomplete']);self.assertIn('UNKNOWN_PROCESS_CLEANUP_RETAINED',inspect.getsource(d.main))

 def test_41_generated_sources_readback_before_any_compile(self):
  body=inspect.getsource(d.main)
  self.assertIn("SHA(p)==digest(b)",body);self.assertIn("'gold-wrapper.c':gold_wrapper",body)
  self.assertIn("len(generated)==12",body);self.assertIn("'harness.c','gold-wrapper.c','statics-wrapper.c'",body)
  self.assertLess(body.index('for name,b in generated.items()'),body.index('output=run(argv'))
  self.assertIn('assert ready',body);self.assertIn("report['preflight_complete']=True",body)

 def test_42_statics_source_pins_are_exact_and_no_observers(self):
  self.assertEqual(len(d.PRODUCTION6),6)
  self.assertEqual(d.PRODUCTION6['enemy_pulses16694_mirror.inc'],'e6d0a7ff0e8dbc28fae4a5225e22ee56ddd318765638476c03f0a9bb537205bd')
  body=inspect.getsource(d.main)
  for name in ('statics-alpha.tsv','STATICS_SELECTOR','game_observation.py','FINAL-PINS.json','registered-02','native-run-01'):
   self.assertNotIn(name,body)

 def test_43_actual_mapped_runtime_closure_and_deleted_input_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'actual.so';path.write_bytes(b'ELF fixture');links={}
   maps='1000-2000 r-xp 00000000 00:00 1 '+str(path)+'\n2000-3000 rw-p 00000000 00:00 0 [heap]\n'
   with patch.object(Path,'read_text',return_value=maps):self.assertEqual(d.loaded_runtime_inputs(links),{str(path):d.SHA(path)})
   with patch.object(Path,'read_text',return_value=maps.replace(str(path),str(path)+' (deleted)')):
    with self.assertRaisesRegex(AssertionError,'Deleted mapped runtime'):d.loaded_runtime_inputs({})

 def test_44_last_budget_failure_cannot_relabel_cleanup_unknown(self):
  report={'status':'UNKNOWN_PROCESS_CLEANUP_RETAINED','error':'first-error'};errors={}
  with patch.object(d,'allocated',side_effect=OSError('budget read')):d.last_actual_budget(Path('/any'),report,errors,lambda:None)
  self.assertEqual(report['status'],'UNKNOWN_PROCESS_CLEANUP_RETAINED');self.assertEqual(report['error'],'first-error')


 def test_45_single_helper_owns_final3728_wrapper_not_double_wrapped(self):
  old,wrapper=h.source_bundle(HERE.parent);self.assertEqual((len(wrapper),d.digest(wrapper)),(3728,d.PULSES_WRAPPER_SHA))
  middle=h.reverse_capture_wrapper(wrapper);self.assertEqual((len(middle),d.digest(middle)),(979,d.PULSES_MIDDLE_SHA))
  self.assertEqual(d.digest(h.reverse_shim(middle)),d.STATICS_WRAPPER_SHA)
  body=inspect.getsource(d.main);calls=[n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id if isinstance(n.func,ast.Name) else None for n in ast.walk(ast.parse(body)) if isinstance(n,ast.Call)]
  self.assertNotIn('capture_wrapper',calls);self.assertIn('reverse_capture_wrapper',calls);self.assertIn('native.source_bundle(r)',body)
  with self.assertRaises(AssertionError):h.capture_wrapper(wrapper)
 def test_46_actual_sixth_stdout_578_and143860156_strict(self):
  self.assertEqual((d.digest(PULSES_ACTUAL_STDOUT),len(PULSES_ACTUAL_STDOUT)),(d.PULSES_STDOUT_SHA,2907))
  result=h.verify_pulses_stdout(PULSES_ACTUAL_STDOUT);self.assertEqual((result['cases'],result['assertions']),(578,143860156))
  for bad in (PULSES_ACTUAL_STDOUT+b' ',PULSES_ACTUAL_STDOUT.replace(b'\n',b'\r\n'),PULSES_ACTUAL_STDOUT.replace(b'143860156',b'143860157')):
   with self.assertRaises(AssertionError):h.verify_pulses_stdout(bad)
 def test_47_palette_adapter_delegated_and_sixth_input_separate(self):
  body=inspect.getsource(d.main);self.assertIn('native.pulses_native_input(r,data,new_stdin)',body);self.assertIn("'pulses578',out,pulses_stdin,True",body)
  self.assertNotIn('32060',body);self.assertNotIn('3840',body);self.assertNotIn('game_probe_parse',body)
  self.assertEqual(d.PULSES_STDIN_SHA,h.PULSES_STDIN_SHA)
  loops=[n for n in ast.walk(ast.parse(body)) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and len(n.target.elts)==4]
  native_loop=next(n for n in loops if isinstance(n.iter,ast.List) and len(n.iter.elts)==5)
  self.assertEqual([n.elts[-1].id for n in native_loop.iter.elts],['old_stdin','new_stdin','new_stdin','new_stdin','new_stdin'])
 def test_48_actual_consumed_helper_bytes_pinned(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'payload';p.write_bytes(b'old');pin=d.SHA(p)
   with patch.object(Path,'read_bytes',return_value=b'new'):
    with self.assertRaises(AssertionError):d.read_bound(p,pin)
  body=inspect.getsource(d.load_native);self.assertIn('raw=read_bound(path,NATIVE_HELPER_SHA)',body);self.assertIn('compile(raw',body)
 def test_49_old_three_scripts_targets_are_still_complete(self):
  self.assertEqual(len(d.COMPILER_LINK_NAMES),21);self.assertEqual(len(d.SCRIPT_TEXT),3)
  self.assertEqual(set(d.SCRIPT_TARGETS),set(d.SCRIPT_TEXT))
 def test_50_reaped_leader_denied_final_group_stop_is_unknown(self):
  class Fake:
   pid=7
   def wait(self,timeout):return 0
  row={}
  with patch.object(d.os,'killpg',side_effect=[None,PermissionError('denied')]):self.assertFalse(d.stop_process(Fake(),row))
  self.assertTrue(row['cleanup_incomplete']);self.assertFalse(row['group_stop_confirmed'])
 def test_51_category_bounds_fit_approved_caps(self):
  self.assertEqual(d.FINAL_CLASS_BOUND,316*1024**2);self.assertEqual(d.PEAK_CLASS_BOUND,444*1024**2)
  self.assertLess(d.FINAL_CLASS_BOUND,d.FINAL_CAP);self.assertLess(d.PEAK_CLASS_BOUND,d.PEAK)
  self.assertEqual(d.CLASS_CAPS['logs'],d.LOG_CAP)
 def test_52_each_known_regular_link_directory_exactly_once(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);files={'hd-on-build/obj/a.o':'objects_elf','hd-on-build/obj/a.d':'maps_deps_snapshots','hd-on-build/opentyrian2000':'objects_elf','enemy-pulses16694-fresh-test':'objects_elf','pulses16694-packs/valid/x.hda':'hda_fixtures','root-index-before.bin':'maps_deps_snapshots','pulses578.stdout':'logs','hd-on-build/src/a.c':'sources_headers','hd-on-build/src/third_party/dr_mp3-LICENSE':'sources_headers','hd-on-build/Makefile':'sources_headers','tmp/cc.tmp':'compiler_tmp'}
   for name,kind in files.items():
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'x');self.assertEqual(d.artifact_class(p,root,p.lstat()),kind)
   p=root/'pulses16694-packs/valid/content';p.symlink_to('/nonexistent-content');self.assertEqual(d.artifact_class(p,root,p.lstat()),'directories_links')
   counts=d.classified_allocation(root);self.assertEqual(sum(counts.values()),d.allocated(root))
 def test_53_unknown_regular_and_symlink_refused_not_dropped(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);p=root/'unexpected';p.write_bytes(b'x')
   with self.assertRaises(AssertionError):d.classified_allocation(root)
   p.unlink();p.symlink_to('/not-real')
   with self.assertRaises(AssertionError):d.classified_allocation(root)
 def test_54_category_overflow_and_final_tmp_retained(self):
  counts={k:0 for k in d.CLASS_CAPS};self.assertTrue(d.check_class_budget(counts,True))
  counts['compiler_tmp']=4096;self.assertTrue(d.check_class_budget(counts))
  with self.assertRaises(AssertionError):d.check_class_budget(counts,True)
  counts['compiler_tmp']=0;counts['objects_elf']=d.CLASS_CAPS['objects_elf']+1
  with self.assertRaises(AssertionError):d.check_class_budget(counts)
 def test_55_exact318_and9856_snapshot_status_no_old_epoch(self):
  body=inspect.getsource(d.main);self.assertIn('FROZEN_PULSES16694_SOURCE_BEFORE_FRESH',body);self.assertIn('len(files)==9856',body)
  self.assertEqual(d.PROTECTED_PROFILE_SHA,'40fbaa92fe7867cc218a7fa051fd4898e31f2cb65a038bc3d0f7fefa22ee23a1')
 def test_56_complete_inverse_and_capture_guard_finalizers_required(self):
  body=inspect.getsource(d.main)
  for name in ('original_ten_and_complete_four_layer_inverse','no_game_captures','compiler_tmp_empty','native.reverse_capture_wrapper','native.reverse_shim','statics.reverse_shim','gold.reverse_shim'):self.assertIn(name,body)
  self.assertIn('pulses16694-wrapper.c',inspect.getsource(d.native_compile_commands))
 def test_57_new_production_includes_and_original12_consumers(self):
  body=inspect.getsource(d.main)
  for name in ('enemy_pulses16694_mirror.inc','current_projectile_pulses16694_payload_pins.h','projectile_pulses16694_native_additions.c.inc'):self.assertIn(name,body)
  self.assertIn("len(generated)==12",body);self.assertIn("'harness.c','gold-wrapper.c','statics-wrapper.c'",body)
 def test_58_full_protected_profile_schema_not_old_flat_gold(self):
  body=inspect.getsource(d.protected_manifest)
  for token in ("profile['worktree']","profile['staged_entries']","PROTECTED_IDENTITY['semantic_sha256']","profile['raw_index']"):self.assertIn(token,body)
  self.assertEqual(d.PROTECTED_TREE,'75abdf4f5ef1a5e23c1c96dc337224e864ee16f1')

 def test_59_nonzero_leader_cleanup_denial_keeps_unknown(self):
  class Fake:
   pid=7;returncode=3
   def poll(self):return self.returncode
   def wait(self,timeout=5):return self.returncode
  with tempfile.TemporaryDirectory() as tmp,patch.object(d.subprocess,'Popen',return_value=Fake()),patch.object(d.os,'killpg',side_effect=[None,PermissionError('denied')]):
   report={'commands':[]}
   with self.assertRaises(AssertionError) as caught:d.run_process(['/fake'],'fake',Path(tmp),Path(tmp),report,lambda:None,lambda:None,{})
   self.assertIn('Command failed',str(caught.exception));self.assertTrue(report['commands'][0]['cleanup_incomplete']);self.assertFalse(report['commands'][0]['group_stop_confirmed'])

 def test_60_actual_makefile_and_headers_consumer_bytes_bound(self):
  body=inspect.getsource(d.main);calls=[ast.unparse(n) for n in ast.walk(ast.parse(body)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='read_bound']
  self.assertIn("read_bound(r / 'Makefile', files['Makefile']['sha256'])",calls);self.assertIn('read_bound(p, assets[str(p)])',calls)
  names=('Makefile','reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h')
  with tempfile.TemporaryDirectory() as tmp:
   for name in names:
    p=Path(tmp)/name;raw=('original '+name).encode();p.write_bytes(raw);pin=d.digest(raw);self.assertEqual(d.read_bound(p,pin),raw)
    p.write_bytes(raw+b' actual swapped bytes')
    with self.assertRaises(AssertionError):d.read_bound(p,pin)
    p.write_bytes(raw);self.assertEqual(d.read_bound(p,pin),raw)

 def fifo_owner(self,pid=77):
  return {'pid':pid,'label':'default-off-build','make_path':'/usr/bin/make'}
 def fifo_stat(self,p,**changes):
  st=p.lstat();values={k:getattr(st,k) for k in ('st_mode','st_nlink','st_size','st_uid','st_dev','st_ino','st_blocks')};values.update(changes);return SimpleNamespace(**values)
 def test_61_actual_jobserver_fifo_direct_owned_singlelink_zero_size_counted(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'tmp').mkdir();p=root/'tmp/GMfifo77';os.mkfifo(p,0o600);seen={}
   self.assertEqual(d.artifact_class(p,root,p.lstat(),self.fifo_owner(),seen),'compiler_tmp')
   counts=d.classified_allocation(root,jobserver_owner=self.fifo_owner(),fifo_observations=seen);self.assertEqual(sum(counts.values()),d.allocated(root));self.assertEqual(counts['compiler_tmp'],p.lstat().st_blocks*512)
   row=seen[str(p)];self.assertEqual(row['identity']['type'],'FIFO');self.assertEqual(row['identity']['owner'],self.fifo_owner());self.assertEqual(row['sample_count'],2)
 def test_62_actual_active_make_owner_all_four_modes_only(self):
  for mode in d.MODES:
   row={'label':mode+'-build','argv':['/usr/bin/make','-j2','CC=/bound/cc'],'pid':77};report={'preflight_complete':True,'commands':[row],'jobserver_make_path':'/usr/bin/make'}
   self.assertEqual(d.active_make_owner(report),{'pid':77,'label':mode+'-build','make_path':'/usr/bin/make'})
 def test_63_no_preflight_wrong_argv_completed_or_unreaped_cannot_admit_fifo(self):
  base={'label':'default-off-build','argv':['/usr/bin/make','-j2'],'pid':77}
  variants=[{**base,'pid':True},{**base,'pid':0},{**base,'returncode':None},{**base,'returncode':0},{**base,'cleanup_incomplete':True},{**base,'label':'pulses578'},{**base,'argv':['/different/make','-j2']},{**base,'argv':['/usr/bin/make','-j3']}]
  for row in variants:self.assertIsNone(d.active_make_owner({'preflight_complete':True,'commands':[row],'jobserver_make_path':'/usr/bin/make'}))
  self.assertIsNone(d.active_make_owner({'preflight_complete':False,'commands':[base],'jobserver_make_path':'/usr/bin/make'}));self.assertIsNone(d.active_make_owner({'preflight_complete':True,'commands':[]}))
 def test_64_actual_other_fifo_paths_and_pids_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);root=base/'stage';root.mkdir()
   for rel in ('tmp/GMfifo78','tmp/GMfifo077','tmp/other','tmp/nested/GMfifo77','home/GMfifo77','default-off-build/GMfifo77','GMfifo77'):
    p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);os.mkfifo(p,0o600)
    with self.assertRaises(AssertionError):d.artifact_class(p,root,p.lstat(),self.fifo_owner(),{})
   p=base/'GMfifo77';os.mkfifo(p,0o600)
   with self.assertRaises(ValueError):d.artifact_class(p,root,p.lstat(),self.fifo_owner(),{})
 def test_65_actual_fifo_hardlink_is_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'tmp').mkdir();p=root/'tmp/GMfifo77';os.mkfifo(p,0o600);os.link(p,root/'tmp/alias');self.assertEqual(p.lstat().st_nlink,2)
   with self.assertRaises(AssertionError):d.artifact_class(p,root,p.lstat(),self.fifo_owner(),{})
 def test_66_wrong_fifo_uid_and_nonzero_size_metadata_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'tmp').mkdir();p=root/'tmp/GMfifo77';os.mkfifo(p,0o600)
   for changes in ({'st_uid':os.geteuid()+1},{'st_size':1},{'st_nlink':0},{'st_blocks':-1},{'st_mode':stat.S_IFIFO|0o644},{'st_mode':stat.S_IFIFO|0o1600}):
    with self.assertRaises(AssertionError):d.artifact_class(p,root,self.fifo_stat(p,**changes),self.fifo_owner(),{})
 def test_67_other_nonregular_device_socket_and_tmp_symlink_remain_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'tmp').mkdir();p=root/'tmp/GMfifo77';os.mkfifo(p,0o600)
   for kind in (stat.S_IFCHR,stat.S_IFBLK,stat.S_IFSOCK):
    with self.assertRaises(AssertionError):d.artifact_class(p,root,self.fifo_stat(p,st_mode=kind|0o600),self.fifo_owner(),{})
   link=root/'tmp/GMfifo78';link.symlink_to(p)
   with self.assertRaises(AssertionError):d.artifact_class(link,root,link.lstat(),self.fifo_owner(78),{})
   # Actual AF_UNIX creation is EPERM in this environment; S_IFSOCK rejection above is retained.
 def test_68_actual_fifo_identity_replacement_recorded_and_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'tmp').mkdir();p=root/'tmp/GMfifo77';os.mkfifo(p,0o600);seen={};d.artifact_class(p,root,p.lstat(),self.fifo_owner(),seen);p.rename(root/'tmp/held-original');os.mkfifo(p,0o600)
   with self.assertRaisesRegex(AssertionError,'identity changed'):d.artifact_class(p,root,p.lstat(),self.fifo_owner(),seen)
   self.assertEqual(len(seen[str(p)]['identity_mismatches']),1);self.assertNotEqual(seen[str(p)]['identity']['ino'],seen[str(p)]['identity_mismatches'][0]['actual_identity']['ino'])
 def test_69_zero_block_fifo_retained_fails_last_budget_without_delete(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'tmp').mkdir();p=root/'tmp/GMfifo77';os.mkfifo(p,0o600);report={'status':'PRETEND_SUCCESS'};errors={}
   result=d.last_actual_budget(root,report,errors,lambda:None);self.assertFalse(result['last_budget_ok']);self.assertIn('last_actual_budget',errors);self.assertTrue(p.exists());self.assertFalse(not list((root/'tmp').iterdir()))
 def test_70_fifo_nonzero_blocks_counted_not_assumed_free(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'tmp').mkdir();p=root/'tmp/GMfifo77';os.mkfifo(p,0o600);orig=Path.lstat;st=self.fifo_stat(p,st_blocks=8);seen={};expected=d.allocated(root)+4096-p.lstat().st_blocks*512
   def lstat(path,*args,**kwargs):return st if path==p else orig(path,*args,**kwargs)
   with patch.object(Path,'lstat',lstat):counts=d.classified_allocation(root,jobserver_owner=self.fifo_owner(),fifo_observations=seen)
   self.assertEqual(counts['compiler_tmp'],4096);self.assertEqual(sum(counts.values()),expected);self.assertEqual(seen[str(p)]['maximum_allocated_bytes'],4096)
 def test_71_fifo_observation_never_opens_fifo_and_aggregates_identity(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'tmp').mkdir();p=root/'tmp/GMfifo77';os.mkfifo(p,0o600);seen={}
   with patch.object(Path,'open',side_effect=AssertionError('FIFO must not be opened')):
    for _ in range(3):d.artifact_class(p,root,p.lstat(),self.fifo_owner(),seen)
   row=seen[str(p)];self.assertEqual(len(seen),1);self.assertEqual(row['sample_count'],3);self.assertLessEqual(row['first_utc_ns'],row['last_utc_ns']);self.assertNotIn('identity_mismatches',row)
 def test_72_fifo_default_no_owner_or_no_observations_refuses_and_final_guards_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'tmp').mkdir();p=root/'tmp/GMfifo77';os.mkfifo(p,0o600)
   for owner,seen in ((None,{}),(self.fifo_owner(),None)):
    with self.assertRaises(AssertionError):d.artifact_class(p,root,p.lstat(),owner,seen)
   with self.assertRaises(AssertionError):d.classified_allocation(root)
  body=inspect.getsource(d.main);self.assertIn("None if final else active_make_owner(report)",body);self.assertIn("'compiler_tmp_empty',lambda:not list((out/'tmp').iterdir())",body);self.assertIn('classified_allocation(out)',inspect.getsource(d.last_actual_budget))

 def synthetic_actual_measure(self,counts,report=None,free=None):
  node=next(n for n in ast.parse(inspect.getsource(d.main)).body[0].body if isinstance(n,ast.FunctionDef) and n.name=='measure')
  if report is None:report={'tmp_enoent_races':[],'jobserver_fifos':{},'commands':[],'preflight_complete':False,'peak_allocated':0,'minimum_free':None}
  namespace=dict(d.__dict__);namespace.update(report=report,out=Path('/synthetic-stage'),created=False,classified_allocation=lambda *args:dict(counts),shutil=SimpleNamespace(disk_usage=lambda path:SimpleNamespace(free=d.START_REQUIRED if free is None else free)))
  exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),d.__file__,'exec'),namespace)
  return namespace['measure'],report,namespace
 def test_73_exact128_temp_and448_peak_boundaries(self):
  counts={k:0 for k in d.CLASS_CAPS};counts['compiler_tmp']=128*1024**2;self.assertTrue(d.check_class_budget(counts));counts['compiler_tmp']+=1
  with self.assertRaises(AssertionError):d.check_class_budget(counts)
  self.assertTrue(d.budget_ok(448*1024**2,d.RESERVE));self.assertFalse(d.budget_ok(448*1024**2+1,d.RESERVE));self.assertEqual(d.START_REQUIRED,731906048)
  self.assertEqual(d.CLASS_CAPS['compiler_tmp'],134217728);self.assertEqual(d.PEAK_CLASS_BOUND,465567744)
 def test_74_actual_measure_overcap_still_rejects_and_records_failed_sample(self):
  counts={k:0 for k in d.CLASS_CAPS};counts['objects_elf']=1024;counts['compiler_tmp']=128*1024**2+512;measure,report,ns=self.synthetic_actual_measure(counts)
  with self.assertRaisesRegex(AssertionError,'Classified fresh budget'):measure()
  self.assertEqual(report['peak_allocated'],sum(counts.values()));self.assertEqual(report['last_classified_allocation'],counts);self.assertEqual(report['class_highwater'],counts);self.assertEqual(report['minimum_free'],d.START_REQUIRED)
  counts['compiler_tmp']=0;measure();self.assertEqual(report['peak_allocated'],128*1024**2+1536);self.assertEqual(report['class_highwater']['compiler_tmp'],128*1024**2+512);self.assertEqual(report['last_classified_allocation']['compiler_tmp'],0)
 def test_75_known_failed64_sample_now_fits_but_is_not_a_build_pass(self):
  counts={'objects_elf':102084608,'sources_headers':27566080,'hda_fixtures':0,'maps_deps_snapshots':14614528,'logs':376832,'directories_links':192512,'compiler_tmp':76718080};self.assertEqual(sum(counts.values()),221552640)
  measure,report,_=self.synthetic_actual_measure(counts);measure();self.assertEqual(report['peak_allocated'],221552640);self.assertEqual(report['class_highwater']['compiler_tmp'],76718080)
  self.assertGreater(counts['compiler_tmp'],64*1024**2);self.assertLess(counts['compiler_tmp'],128*1024**2)
 def test_76_444_class_sum_global448_extra_guard_not_bypassed(self):
  counts=dict(d.CLASS_CAPS);self.assertEqual(sum(counts.values()),444*1024**2);measure,report,_=self.synthetic_actual_measure(counts);measure(extra=4*1024**2)
  with self.assertRaises(AssertionError):measure(extra=4*1024**2+1)
  self.assertEqual(report['peak_allocated'],444*1024**2);self.assertEqual(report['last_classified_allocation'],counts)
  counts['compiler_tmp']=0;measure(extra=4*1024**2,final=True)
  with self.assertRaises(AssertionError):measure(extra=4*1024**2+1,final=True)
 def test_77_final_tmp_empty_and_reserve_remain_immediate_failure(self):
  counts={k:0 for k in d.CLASS_CAPS};counts['compiler_tmp']=1;measure,report,_=self.synthetic_actual_measure(counts)
  with self.assertRaisesRegex(AssertionError,'Compiler temporary bytes retained'):measure(final=True)
  self.assertEqual(report['peak_allocated'],1);self.assertEqual(report['class_highwater']['compiler_tmp'],1)
  counts['compiler_tmp']=0;measure,report,_=self.synthetic_actual_measure(counts,free=d.RESERVE-1)
  with self.assertRaises(AssertionError):measure()
  self.assertEqual(report['minimum_free'],d.RESERVE-1)

if __name__=='__main__':unittest.main(verbosity=2)

