"""Pure fresh-driver contracts. No compiler, Makefile, native process or main().
Temporary fixtures are tiny; a mocked process is never an actual subprocess.
The sibling installed helper is the only native-helper source, no fallback.
"""
from pathlib import Path
import ast,hashlib,importlib.util,inspect,io,json,os,subprocess,tempfile,unittest
from unittest.mock import patch
HERE=Path(__file__).resolve().parent

def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

d=module(HERE/'projectile_statics_fresh_native_validation.py','fresh_statics_driver_pure')
h=module(HERE/'projectile_statics_native_validation.py','fresh_statics_native_pure')

OLD_STDOUT={'inherited107_stdout': b'PASS inherited91 native lifecycle: 37 cases 81611 assertions\n145_TO_TALON copied=376 cached=0\n145_TO_TALON copied=376 cached=1\nPASS shared145 native lifecycle: 70 new cases 141992 new assertions; internal8 only; not gameplay/full build\n', 'inherited61_stdout': b'61_TO_TALON copied=267 cached=0\n61_TO_TALON copied=267 cached=1\nPASS shared61 native lifecycle: 157 cases 822291 assertions; internal8 only; not gameplay/full build\n', 'new_blue_stdout': b'BLUE101_ZERO_NATIVE pattern=0 draw=384 finish=384 cache=384\nBLUE101_ZERO_NATIVE pattern=1 draw=384 finish=384 cache=384\nBLUE101_ZERO_HD prior=120 draw=384 finish=384 cache=384\nBLUE_TO_TALON selector=101 copied=1756 soft=1721 cached=0\nBLUE_TO_TALON selector=101 copied=1756 soft=1721 cached=1\nBLUE_TO_TALON selector=120 copied=1864 soft=1864 cached=0\nBLUE_TO_TALON selector=120 copied=1864 soft=1864 cached=1\nBLUE_TO_TALON selector=139 copied=1481 soft=1454 cached=0\nBLUE_TO_TALON selector=139 copied=1481 soft=1454 cached=1\nPASS blue triplet native lifecycle: 365 cases 11162937 assertions; internal8 only; not gameplay/full build\n', 'gold251_stdout': b'GOLD_GROUP name=full_tile_native_patterns cases=4\nGOLD_GROUP name=bounds cases=18\nGOLD_GROUP name=pair_orders cases=26\nGOLD_GROUP name=all8_early_dependency cases=16\nGOLD_GROUP name=missing_bad cases=32\nGOLD_GROUP name=singletons_oldonly cases=4\nGOLD_GROUP name=malformed_gold cases=6\nGOLD_GROUP name=unused_memory_payload_ready cases=8\nGOLD_GROUP name=palette cases=40\nGOLD_GROUP name=used_resource_shared cases=64\nGOLD_GROUP name=callbacks cases=8\nGOLD_GROUP name=cold_scope cases=10\nGOLD_TO_TALON selector=168 copied=974 soft=974 alpha0=86 cached=0\nGOLD_TO_TALON selector=168 copied=974 soft=974 alpha0=86 cached=1\nGOLD_TO_TALON selector=169 copied=735 soft=735 alpha0=85 cached=0\nGOLD_TO_TALON selector=169 copied=735 soft=735 alpha0=85 cached=1\nGOLD_GROUP name=Talon_transfer cases=4\nGOLD_GROUP name=lifecycle cases=5\nGOLD_GROUP name=controlled_animation cases=6\nPASS gold pulse native lifecycle: 251 cases 38046959 assertions; internal8 only; not gameplay/full build\n'}

def source_fixture():
 names=['entity_draw.c','tyrian2.c','render_mirror.c']+[f'unit{i}.c' for i in range(83)]+['global_projectile91_mirror.inc']+[f'header{i}.h' for i in range(227)]
 old={n:'0'*64 for n in names};return old,{**old,**d.PRODUCTION6}

def compile_log(mode):
 units=[f'unit{i}' for i in range(86)];flags=['cc','-MD','-DNDEBUG']+d.MODES[mode].split()
 flags+=(['-O1','-g',*d.SAN] if mode=='hd-on-asan-ubsan' else ['-O2'])
 lines=[' '.join([*flags,'-c','-o','obj/'+u+'.o','src/'+u+'.c']) for u in units]
 lines.append(' '.join(['cc',*(['-fsanitize=address,undefined','-no-pie'] if mode=='hd-on-asan-ubsan' else []),'-o','opentyrian2000',*('obj/'+u+'.o' for u in units)]))
 return '\n'.join(lines)+'\n',units

class FreshStaticsPure(unittest.TestCase):
 def test_01_budgets_peak_final_reserve(self):
  self.assertTrue(d.budget_ok(384*1024**2,250*1024**2))
  self.assertFalse(d.budget_ok(384*1024**2+1,250*1024**2))
  self.assertFalse(d.budget_ok(1,250*1024**2-1))
  self.assertTrue(d.budget_ok(288*1024**2,250*1024**2,True))
  self.assertFalse(d.budget_ok(288*1024**2+1,250*1024**2,True))
  self.assertEqual(d.START_REQUIRED,664797184)

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
   self.assertIn(str(out/'statics-wrapper.c'),link)
   for flag in (*d.SAN,'-O1','-g'):self.assertIn(flag,link)

 def test_10_source316_exact_six_overlays(self):
  old,new=source_fixture();self.assertTrue(d.check_source_epoch(new,old))
  bad=dict(new);bad['entity_draw.c']='f'*64
  with self.assertRaises(AssertionError):d.check_source_epoch(bad,old)
  bad=dict(new);bad['header0.h']='f'*64
  with self.assertRaises(AssertionError):d.check_source_epoch(bad,old)
  del bad['enemy_statics_mirror.inc']
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
  old,wrapper=h.source_bundle(HERE.parent);gold_wrapper=h.reverse_shim(wrapper)
  self.assertEqual(d.digest(gold_wrapper),d.GOLD_WRAPPER_SHA)
  self.assertEqual(h.gold_helper(HERE.parent).reverse_shim(gold_wrapper),old['harness.c'])
  self.assertEqual(len(old['harness.c']),262);self.assertNotEqual(wrapper,gold_wrapper)

 def test_13_current_root_only_helper_and_no_fallback(self):
  self.assertRegex(d.NATIVE_HELPER_SHA,r'^[0-9a-f]{64}$')
  self.assertEqual(d.SHA(HERE/'projectile_statics_native_validation.py'),d.NATIVE_HELPER_SHA)
  with patch.object(d,'SHA',return_value='0'*64):
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
  for text in ("len(report['fresh_dependency_file_sha256'])==346", "counts['cases']==449", "counts['assertions']==91342858",'total_cases=1329,total_assertions=141598648',"legacy_counts['cases']==880","legacy_counts['assertions']==50255790"):
   self.assertIn(text,body)
  self.assertIn(".read_bytes()",inspect.getsource(d.run_process));self.assertNotIn('.read_text()',inspect.getsource(d.run_process))
  self.assertIn("('gold251','gold251_stdout'",body);self.assertIn("[exe,'--enemy-statics'",body)

 def test_27_real_companion_output_schema_kept(self):
  p=HERE/'projectile_statics_native_additions.c.inc';self.assertEqual(d.SHA(p),d.STATICS_COMPANION_SHA)
  text=p.read_text();self.assertIn('STATICS_GROUP name=%s cases=%u',text);self.assertIn('STATICS_TO_TALON selector=%u copied=%u soft=%u alpha0=%u cached=%u',text)
  self.assertEqual(sum(n for _,n in h.GROUPS),449);self.assertEqual(len(h.GROUPS),24);self.assertEqual(h.TRANSFER,{162:(526,521,35),260:(1122,1122,6)})
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
  self.assertEqual(d.FINAL_CAP,301989888);self.assertEqual(d.PROTECTED_IDENTITY['head'],'f64a7ddc6bbf11a0667665f4faf5b6db6c9ea6bc')
  self.assertEqual(d.PROTECTED_IDENTITY['raw_sha256'],'e579802d832d2be0ba6628927c175377e1d71ec2eb04cf93a6ad0758e6606d56')
  self.assertIn("len(profile)==9800",inspect.getsource(d.protected_manifest))

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
  lines=[]
  for name,count in h.GROUPS:
   if name=='Talon_transfer':
    for selector in h.STATICS:
     copied,soft,zero=h.TRANSFER[selector]
     for cached in (0,1):lines.append(f'STATICS_TO_TALON selector={selector} copied={copied} soft={soft} alpha0={zero} cached={cached}')
   lines.append(f'STATICS_GROUP name={name} cases={count}')
  lines.append('PASS enemy statics native lifecycle: 449 cases 91342858 assertions; internal8 only; not gameplay/full build')
  raw=('\n'.join(lines)+'\n').encode();self.assertEqual(h.parse_statics_stdout(raw)['assertions'],91342858)
  self.assertEqual((d.digest(raw),len(raw)),('fc00c7f5120d9670fc500e8692e418798b93029c7af261ae0f3629ce50f92aef',1577))
  for bad in (raw.replace(b'\n',b'\r\n'),raw[:-1],raw+b'\n',raw.replace(b'91342858',b'91342859')):
   with self.assertRaises(AssertionError):h.parse_statics_stdout(bad)

 def test_36_fixture102_and725_no_evidence_deletion(self):
  schema=h.fixture_schema();self.assertEqual(len(schema),42);self.assertEqual(sum(map(len,schema.values())),390)
  body=inspect.getsource(d.main)
  for text in ('len(old_fixtures)==335 and len(fixtures)==725','len(leaves)==len(set(leaves))==102','all(fixtures[k]==v for k,v in old_fixtures.items())',"len(report['fixture_sha256'])==725 and len(report['fixture_links'])==102"):
   self.assertIn(text,body)
  for text in ('unlink(', 'rmtree(', 'os.remove(', 'shutil.copytree('):self.assertNotIn(text,body)

 def test_37_initial_mkdir_failure_is_guarded_no_save_or_process(self):
  import sys
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);paths={n:root/n for n in ('root','data','sysroot','protected','stage')}
   for name,p in paths.items():
    if name!='stage':p.mkdir()
   argv=['driver','--root',str(paths['root']),'--stage',str(paths['stage']),'--data',str(paths['data']),'--sysroot',str(paths['sysroot']),'--protected-qualifiedgold',str(paths['protected']),'--protected-profile',str(root/'profile'),'--root-snapshot',str(root/'snapshot'),'--root-snapshot-sha256','0'*64]
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
   argv=['driver','--root',str(root/'root'),'--stage',str(root/'stage'),'--data',str(root/'data'),'--sysroot',str(root/'sysroot'),'--protected-qualifiedgold',str(root/'protected'),'--protected-profile',str(root/'profile'),'--root-snapshot',str(root/'snapshot'),'--root-snapshot-sha256','0'*64]
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
  self.assertIn("len(generated)==10",body);self.assertIn("'harness.c','gold-wrapper.c'",body)
  self.assertLess(body.index('for name,b in generated.items()'),body.index('output=run(argv'))
  self.assertIn('assert ready',body);self.assertIn("report['preflight_complete']=True",body)

 def test_42_statics_source_pins_are_exact_and_no_observers(self):
  self.assertEqual(len(d.PRODUCTION6),6)
  self.assertEqual(d.PRODUCTION6['enemy_statics_mirror.inc'],'2aca7e11a03882eea6543640b735a0919fec82462165c24476c2dd231a027c18')
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

if __name__=='__main__':unittest.main(verbosity=2)

