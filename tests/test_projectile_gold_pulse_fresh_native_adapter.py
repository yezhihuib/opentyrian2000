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

d=module(HERE/'projectile_gold_pulse_fresh_native_validation.py','fresh_gold_driver_pure')
h=module(HERE/'projectile_gold_pulse_native_validation.py','fresh_gold_native_pure')

def source_fixture():
 names=['entity_draw.c','tyrian2.c','render_mirror.c']+[f'unit{i}.c' for i in range(83)]+['global_projectile91_mirror.inc']+[f'header{i}.h' for i in range(225)]
 old={n:'0'*64 for n in names};return old,{**old,**d.PRODUCTION6}

def compile_log(mode):
 units=[f'unit{i}' for i in range(86)];flags=['cc','-MD','-DNDEBUG']+d.MODES[mode].split()
 flags+=(['-O1','-g',*d.SAN] if mode=='hd-on-asan-ubsan' else ['-O2'])
 lines=[' '.join([*flags,'-c','-o','obj/'+u+'.o','src/'+u+'.c']) for u in units]
 lines.append(' '.join(['cc',*(['-fsanitize=address,undefined','-no-pie'] if mode=='hd-on-asan-ubsan' else []),'-o','opentyrian2000',*('obj/'+u+'.o' for u in units)]))
 return '\n'.join(lines)+'\n',units

class FreshGoldPure(unittest.TestCase):
 def test_01_budgets_peak_final_reserve(self):
  self.assertTrue(d.budget_ok(384*1024**2,250*1024**2))
  self.assertFalse(d.budget_ok(384*1024**2+1,250*1024**2))
  self.assertFalse(d.budget_ok(1,250*1024**2-1))
  self.assertTrue(d.budget_ok(256*1024**2,250*1024**2,True))
  self.assertFalse(d.budget_ok(256*1024**2+1,250*1024**2,True))
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
   self.assertIn(str(out/'gold-wrapper.c'),link)
   for flag in (*d.SAN,'-O1','-g'):self.assertIn(flag,link)

 def test_10_source314_exact_six_overlays(self):
  old,new=source_fixture();self.assertTrue(d.check_source_epoch(new,old))
  bad=dict(new);bad['entity_draw.c']='f'*64
  with self.assertRaises(AssertionError):d.check_source_epoch(bad,old)
  bad=dict(new);bad['header0.h']='f'*64
  with self.assertRaises(AssertionError):d.check_source_epoch(bad,old)
  del bad['enemy_gold_pulse_mirror.inc']
  with self.assertRaises(AssertionError):d.check_source_epoch(bad,old)

 def test_11_original629_full_stdout_bytes_and_crlf_rejected(self):
  outputs={k:v.encode() for k,v in h.LEGACY_STDOUT.items()};self.assertTrue(d.validate_stdout_bytes(outputs))
  for name in outputs:
   bad=dict(outputs);bad[name]=bad[name].replace(b'\n',b'\r\n')
   with self.assertRaises(AssertionError):d.validate_stdout_bytes(bad)
   bad=dict(outputs);bad[name]+=b' '
   with self.assertRaises(AssertionError):d.validate_stdout_bytes(bad)

 def test_12_all_six_source_and_262_shim_constants(self):
  self.assertEqual(d.SOURCE_PINS,h.SOURCE_PINS)
  # Synthetic pure inverse test; actual six source bytes are enforced by installed main/native source tests.
  raw=b'int main(int argc,char **argv)\n{ return 0; }\n'
  wrapper=h.outer_shim(raw);self.assertEqual(h.reverse_shim(wrapper),raw);self.assertNotEqual(wrapper,raw)

 def test_13_current_root_only_helper_and_no_fallback(self):
  self.assertRegex(d.NATIVE_HELPER_SHA,r'^[0-9a-f]{64}$')
  self.assertEqual(d.SHA(HERE/'projectile_gold_pulse_native_validation.py'),d.NATIVE_HELPER_SHA)
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

 def test_26_all880_counts_and_byte_read_contract(self):
  body=inspect.getsource(d.main)
  for text in ('len(report[\'fresh_dependency_file_sha256\'])==346',"counts['cases']==251", "counts['assertions']==38046959",'total_cases=880,total_assertions=50255790','digest(gold)==GOLD_STDOUT_SHA'):
   self.assertIn(text,body)
  self.assertIn(".read_bytes()",inspect.getsource(d.run_process));self.assertNotIn('.read_text()',inspect.getsource(d.run_process))

 def test_27_real_companion_output_schema_kept(self):
  p=HERE/'projectile_gold_pulse_native_additions.c.inc';self.assertEqual(d.SHA(p),d.GOLD_COMPANION_SHA)
  text=p.read_text();self.assertIn('GOLD_GROUP name=%s cases=%u',text);self.assertIn('GOLD_TO_TALON selector=%u copied=%u soft=%u alpha0=%u cached=%u',text)
  self.assertEqual(sum(n for _,n in h.GROUPS),251);self.assertEqual(len(h.GROUPS),15);self.assertEqual(h.TRANSFER,{168:(974,974,86),169:(735,735,85)})

 def test_28_current_compiler_runtime_targets_and_script_are_bound(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'actual-libgcc_s.so.1').write_bytes(b'\x7fELFshared')
   for name in d.COMPILER_LINK_NAMES:
    path=root/name
    if name=='libgcc_s.so.1':path.symlink_to('actual-libgcc_s.so.1')
    else:path.write_bytes(b'\x7fELFstartup')
   (root/'libgcc.a').write_bytes(b'!<arch>\narchive')
   (root/'libgcc_s.so').write_bytes(b'/* GNU ld script */ GROUP ( libgcc_s.so.1 -lgcc )\n')
   links={};calls=[]
   def query(argv,env):
    calls.append(argv);return str(root/argv[1].split('=',1)[1]).encode()+b'\n'
   with patch.object(d.subprocess,'check_output',side_effect=query):pins,records=d.compiler_link_inputs(Path('/current/cc'),{},links)
   self.assertEqual(len(calls),12);self.assertEqual(set(records),set(d.COMPILER_LINK_NAMES))
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
    with self.assertRaisesRegex(AssertionError,'Unrecognized libgcc linker-script'):d.compiler_link_inputs(Path('/cc'),{}, {})
   body=inspect.getsource(d.main)
   self.assertIn('tools.update(compiler_link_pins)',body)
   self.assertIn("'compiler_link_inputs':compiler_link_records",body)
   self.assertIn("all(SHA(p)==v for p,v in bound.items())",body)

if __name__=='__main__':unittest.main()
