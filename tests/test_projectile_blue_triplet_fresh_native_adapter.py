#!/usr/bin/env python3
"""Pure fresh629 adapter checks. No compiler, Makefile, native or game execution."""
from pathlib import Path
import ast,hashlib,importlib.util,inspect,json,os,stat,tempfile,unittest,types,time,signal,subprocess
from unittest import mock
HERE=Path(__file__).resolve().parent
DEFAULT_ROOT=HERE.parent
ROOT=Path(os.environ.get('BLUE_STATIC_ROOT',str(DEFAULT_ROOT)))
spec=importlib.util.spec_from_file_location('blue_fresh_under_test',HERE/'projectile_blue_triplet_fresh_native_validation.py');fresh=importlib.util.module_from_spec(spec);spec.loader.exec_module(fresh)


class BlueTripletFreshAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=Path(fresh.__file__).read_text();cls.tree=ast.parse(cls.text)
        cls.units=sorted(p.stem for p in (ROOT/'src').glob('*.c'));assert len(cls.units)==86

    def log(self,mode):
        flags=' -MD -DNDEBUG '+fresh.MODES[mode]+(' -O1 -g '+' '.join(fresh.SAN) if mode=='hd-on-asan-ubsan' else ' -O2')
        rows=['cc'+flags+' -c -o obj/'+u+'.o src/'+u+'.c' for u in self.units]
        rows.append('cc'+(' -fsanitize=address,undefined -no-pie' if mode=='hd-on-asan-ubsan' else '')+' -o opentyrian2000 '+' '.join('obj/'+u+'.o' for u in self.units)+' -lm -lSDL2')
        return '\n'.join(rows)

    def test_four_modes_serial_j2_flags_and_peak_final_reserve(self):
        self.assertEqual(list(fresh.MODES),['default-off','hd-on','mirror-disabled','hd-on-asan-ubsan'])
        self.assertEqual((fresh.PEAK,fresh.FINAL_CAP,fresh.RESERVE,fresh.START_REQUIRED),(268435456,201326592,262144000,530579456))
        for mode in fresh.MODES:
            args=fresh.make_command(mode,Path('/sysroot'),Path('/cc'),Path('/pkg'))
            self.assertEqual(args[:2],['make','-j2']);self.assertIn('CC=/cc',args);self.assertIn('PKG_CONFIG=/pkg',args)
            cpp=next(x for x in args if x.startswith('CPPFLAGS='));cf=next(x for x in args if x.startswith('CFLAGS='));ld=next(x for x in args if x.startswith('LDFLAGS='))
            self.assertIn('-MD -DNDEBUG',cpp)
            self.assertEqual('-DNEWSHF_HD_COMPOSITOR=1' in cpp,mode!='default-off')
            self.assertEqual('-DRENDER_MIRROR_DISABLED' in cpp,mode=='mirror-disabled')
            self.assertEqual('-fsanitize=address,undefined' in cf,mode=='hd-on-asan-ubsan');self.assertEqual('-fsanitize=address,undefined' in ld,mode=='hd-on-asan-ubsan')
            self.assertIn('-O1 -g' if mode=='hd-on-asan-ubsan' else '-O2',cf)
        for final,cap in ((False,fresh.PEAK),(True,fresh.FINAL_CAP)):
            self.assertTrue(fresh.budget_ok(cap,fresh.RESERVE,final));self.assertFalse(fresh.budget_ok(cap+1,fresh.RESERVE,final));self.assertFalse(fresh.budget_ok(cap,fresh.RESERVE-1,final))

    def test_exact86_compiles_and_link_contract_all_modes(self):
        for mode in fresh.MODES:
            rows,link=fresh.compile_contract(self.log(mode),self.units,mode);self.assertEqual(len(rows),86);self.assertIn('opentyrian2000',link)
            lines=self.log(mode).splitlines()
            for bad in ('\n'.join(lines[1:]),'\n'.join(lines[:85]+[lines[0],lines[-1]]),'\n'.join(lines+[lines[-1]])):
                with self.assertRaises(AssertionError):fresh.compile_contract(bad,self.units,mode)
        for flag in (*fresh.SAN,'-O1','-g'):
            with self.assertRaises(AssertionError):fresh.compile_contract(self.log('hd-on-asan-ubsan').replace(flag,'',1),self.units,'hd-on-asan-ubsan')
        with self.assertRaises(AssertionError):fresh.compile_contract(self.log('hd-on'),self.units,'default-off')
        with self.assertRaises(AssertionError):fresh.compile_contract(self.log('hd-on').replace('obj/'+self.units[0]+'.o','obj/wrong.o',1),self.units,'hd-on')
        with self.assertRaises(AssertionError):fresh.compile_contract(self.log('hd-on-asan-ubsan').rsplit(' -fsanitize=address,undefined',1)[0]+' -o opentyrian2000 '+' '.join('obj/'+u+'.o' for u in self.units),self.units,'hd-on-asan-ubsan')

    def test_full_hydration_rejects_skip_unmerged_missing_and_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'good').write_bytes(b'good')
            def git(*args):
                if args==('ls-files','-t','-z'):return b'H good\0'
                if args==('ls-files','--stage','-z'):return b'100644 '+b'a'*40+b' 0\tgood\0'
                return b'good\0'
            with mock.patch.object(fresh,'git',side_effect=lambda r,*a:git(*a)):
                self.assertEqual(set(fresh.hydrated_manifest(root)),{'good'})
            for skip,stage in ((True,False),(False,True)):
                def badgit(r,*args):
                    if args==('ls-files','-t','-z') and skip:return b'S good\0'
                    if args==('ls-files','--stage','-z') and stage:return b'100644 '+b'a'*40+b' 1\tgood\0'
                    return git(*args)
                with mock.patch.object(fresh,'git',side_effect=badgit),self.assertRaises(AssertionError):fresh.hydrated_manifest(root)
            (root/'good').unlink();(root/'outside').write_bytes(b'x');(root/'good').symlink_to(root/'outside')
            with mock.patch.object(fresh,'git',side_effect=lambda r,*a:git(*a)),self.assertRaises(AssertionError):fresh.hydrated_manifest(root)

    def test_actual_raw_semantic_snapshots_no_refresh(self):
        self.assertIn('raw=index.read_bytes()',inspect.getsource(fresh.identity));self.assertIn('index.read_bytes()==raw',inspect.getsource(fresh.identity))
        self.assertNotIn('update-index',self.text);self.assertNotIn('--refresh',self.text)
        for name in ('root-index-before.bin','root-index-semantic-before.bin','root-index-after.bin','root-index-semantic-after.bin'):self.assertIn(name,self.text)
        self.assertIn('after==ri',self.text)
        self.assertEqual(fresh.snapshot_allocation(b'x'*4097,b'y'),12288)

    def test_allocated_counts_root_directories_and_link_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'dir').mkdir();(root/'dir/f').write_bytes(b'x'*4097);(root/'link').symlink_to(root/'dir/f')
            expected=sum(p.lstat().st_blocks*512 for p in [root,*root.rglob('*')]);self.assertEqual(fresh.allocated(root),expected)
        self.assertIn('except FileNotFoundError',inspect.getsource(fresh.allocated))

    def test_four_historical_files_exact_allowlist_no_object_or_dep_read(self):
        self.assertEqual(fresh.HISTORICAL61_FILES,('receipt.json','inherited107.stdout','native61.stdout'));self.assertEqual(fresh.HISTORICAL_BLUE_FILES,('receipt.json',))
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);f=root/'fresh';b=root/'blue';f.mkdir();b.mkdir()
            accepted={'status':'PASS_FOUR_FRESH_CONFIGS_AND_FULL_PROJECT_SANITIZED264','checks':{'ok':True},'inherited107_stdout':'old\n','new61_stdout':'61\n'}
            prior={'status':'PASS_ORIGINAL264_AND_BLUE_TRIPLET_PRODUCTION_TU','checks':{'ok':True}}
            (f/'receipt.json').write_text(json.dumps(accepted));(f/'inherited107.stdout').write_text('old\n');(f/'native61.stdout').write_text('61\n');(b/'receipt.json').write_text(json.dumps(prior))
            allowed={f/n for n in fresh.HISTORICAL61_FILES}|{b/'receipt.json'};reads=[]
            def pin(p):
                p=Path(p);self.assertIn(p,allowed);reads.append(p)
                return fresh.FRESH61_SHA if p==f/'receipt.json' else fresh.PRIOR_BLUE_SHA if p==b/'receipt.json' else hashlib.sha256(p.read_bytes()).hexdigest()
            with mock.patch.object(fresh,'SHA',side_effect=pin):
                a,c,bindings=fresh.historical_inputs(f,b);self.assertEqual(a,accepted);self.assertEqual(c,prior);self.assertEqual(set(map(Path,bindings)),allowed)
            self.assertEqual(set(reads),allowed)
            (f/'native61.stdout').write_text('changed')
            with mock.patch.object(fresh,'SHA',side_effect=pin),self.assertRaises(AssertionError):fresh.historical_inputs(f,b)
        fn=inspect.getsource(fresh.historical_inputs);self.assertNotIn('.rglob(',fn);self.assertNotIn('.glob(',fn)
        for token in ('fresh_dependency_sha256','native_linked_objects_sha256','binary_sha256','build/src'):
            self.assertNotIn(token,fn)

    def test_old_source_map_changes_exactly_two_payload_constants_header(self):
        self.assertIn("{p for p in source if source[p]!=priorblue['source_sha256'][p]}=={PAYLOAD_HEADER}",self.text)
        self.assertEqual(fresh.PAYLOAD_HEADER_SHA,'857978d85a52b73a8c0a8bd9ba318a13da715db12d3ffd168e22f35a778874c8')
        self.assertEqual(set(fresh.HDA_SHA),{101,120,139});self.assertIn('len(source)==312 and len(units)==86',self.text)

    def test_historical_dependencies_are_not_reused_even_indirectly(self):
        tree=self.tree
        for node in ast.walk(tree):
            if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='a':
                self.assertIn(node.attr,{'root','out','accepted61_fresh','prior_blue_native','protection_snapshot','data','sysroot'})
        main=inspect.getsource(fresh.main)
        self.assertNotIn("a.accepted61_fresh/",main);self.assertNotIn("a.prior_blue_native/",main)
        self.assertIn("historical_inputs(a.accepted61_fresh,a.prior_blue_native)",main)
        self.assertIn("'reused_project_objects':0",main);self.assertIn("'historical_objects_consumed':0",main)
        self.assertNotIn('os.link(',main)

    def test_new_native_helper_exact_current_root_no_fallback(self):
        source=inspect.getsource(fresh.load_native)
        self.assertIn("root/'tests/projectile_blue_triplet_native_validation.py'",source)
        self.assertIn('SHA(path)==NATIVE_HELPER_SHA',source)
        self.assertIn("re.fullmatch('[0-9a-f]{64}',NATIVE_HELPER_SHA)",source)
        self.assertNotIn('except',source);self.assertNotIn('parent/',source)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'tests').mkdir();p=root/'tests/projectile_blue_triplet_native_validation.py';p.write_text('PURE_VALUE=1\n')
            pin=hashlib.sha256(p.read_bytes()).hexdigest()
            with mock.patch.object(fresh,'NATIVE_HELPER_SHA',pin):
                self.assertEqual(fresh.load_native(root).PURE_VALUE,1);p.write_text('PURE_VALUE=2\n')
                with self.assertRaises(AssertionError):fresh.load_native(root)

    def test_protected_five_original_roots_exact_source_prefix_and_pin(self):
        self.assertEqual(set(fresh.PROTECTED_NAMES),{'projectile61-private-sparse','projectile145-private-sparse','newshf166-private','newshf169-private','shared170-bronze356-private'})
        self.assertEqual(fresh.PROTECTION_SHA,'ecda303ffb05dd6b9a33e011233092b06141ead9c2e034f7c4fdeca7b3df3e20')
        source=inspect.getsource(fresh.protected_roots)
        self.assertIn('set(rows)==set(PROTECTED_NAMES)',source);self.assertIn("{'src/'+k:v for k,v in inv(p/'src').items()}==expected",source);self.assertIn('identity(p)[0]',source)
        self.assertNotIn('assets',source)

    def test_fresh84_main_renderer_inputs_and_actual346_dependencies(self):
        for text in ("p.stem not in ('render_mirror','opentyr')","assert len(objects)==84","'-Dmain=unused_game_main'","q/'harness.c',renamed,*objects", "==346", "Path(p).is_relative_to(build)"):
            self.assertIn(text,self.text)
        self.assertIn("assert not build.exists()",self.text);self.assertIn("assert not (build/'obj').exists()",self.text)
        self.assertIn('Unbound actual dependency',self.text);self.assertIn('generated.get(str(path),system.get(str(path)))',self.text)
        self.assertIn("inv(build/'src')==source",self.text)

    def test_three_fresh_process_modes_264_exact_and_new365(self):
        for marker in ("[exe,'--inherited107',*legacy[:5]]","[exe,'--projectile61',*legacy]","[exe,'--blue-triplet',q/'blue-packs']"):
            self.assertIn(marker,self.text)
        self.assertIn("oldout==prior61['inherited107_stdout'] and newout==prior61['new61_stdout']",self.text)
        self.assertIn("inherited_counts['total_cases']==264 and blue_counts['new_cases']==365",self.text)
        self.assertIn('total_cases=629',self.text);self.assertIn('native.parse_blue_stdout(blueout)',self.text)
        self.assertIn("native.fixture_payloads({i:p.read_bytes() for i,p in hdas.items()})",self.text)
        self.assertIn('len(leaves)==34',self.text);self.assertIn('len(fixtures)==151',self.text)
        self.assertIn('Native harness must actually consume new renderer and payload pins',self.text)

    def test_guarded_final_error_does_not_discard_original_failure(self):
        checks={};errors={}
        def bad():raise OSError('read blocked')
        self.assertFalse(fresh.guarded_check(checks,errors,'binding',bad));self.assertIn('read blocked',errors['binding'])
        self.assertIn("report['status_before_final_checks']=report['status']",self.text)
        self.assertIn("report.update(status='FAIL_RETAINED',error=repr(error))",self.text)
        self.assertIn("errors['save_original_outcome']",self.text)
        self.assertIn("guard('final_identity_read_and_match',capture_identity)",self.text)
        self.assertIn("guard('after_snapshot_budget_write_and_hash',snapshots)",self.text)
        self.assertIn("guard('final_observed_allocation_and_free',observed_budget)",self.text)
        self.assertIn("row['terminal_save_error']=repr(write_error)",self.text)

    def test_save_failure_before_feeder_start_preserves_error_and_kills_process(self):
        # Execute only the isolated run wrapper under synthetic process/thread
        # objects. No child process, signal or native program is started.
        run_node=next(n for n in ast.walk(self.tree) if isinstance(n,ast.FunctionDef) and n.name=='run')
        class Process:
            pid=2468
            stdin=None
            returncode=None
            def poll(self):return self.returncode
            def wait(self,timeout=None):self.returncode=-15;return -15
        class Feeder:
            ident=None
            started=False
            joined=False
            def start(self):self.started=True;self.ident=123
            def join(self,timeout=None):
                self.joined=True
                if self.ident is None:raise RuntimeError('cannot join thread before it is started')
            def is_alive(self):return False
        process=Process();feeder=Feeder();report={'commands':[]};saves=[];kills=[]
        def save():
            saves.append(1)
            if len(saves)==2:raise OSError('receipt write failed before feeder start')
        with tempfile.TemporaryDirectory() as td:
            q=Path(td)
            fake_subprocess=types.SimpleNamespace(Popen=lambda *a,**k:process,PIPE=-1,DEVNULL=-3,TimeoutExpired=subprocess.TimeoutExpired)
            env={'q':q,'report':report,'save':save,'measure':lambda:None,'env':{},'no_core':lambda:None,'subprocess':fake_subprocess,'threading':types.SimpleNamespace(Thread=lambda **kw:feeder),'time':time,'signal':signal,'os':types.SimpleNamespace(killpg=lambda pid,sig:kills.append((pid,sig))),'SHA':fresh.SHA,'Path':Path}
            exec(compile(ast.fix_missing_locations(ast.Module(body=[run_node],type_ignores=[])),'<pure isolated run>','exec'),env)
            with self.assertRaisesRegex(OSError,'receipt write failed before feeder start'):
                env['run'](['never-executed'],'synthetic',q,b'input')
        self.assertFalse(feeder.started);self.assertFalse(feeder.joined)
        self.assertEqual(kills,[(2468,signal.SIGTERM)])
        self.assertTrue(report['commands'][0]['stopped']);self.assertEqual(report['commands'][0]['returncode'],-15)
        self.assertEqual(len(saves),3)

    def test_snapshot_preallocation_and_two_postreceipt_budget_guards(self):
        main=inspect.getsource(fresh.main)
        self.assertLess(main.index('measure(extra+131072,True)'),main.index("(q/'root-index-after.bin').write_bytes"))
        self.assertIn('measure(131072,True)',main)
        self.assertIn("guard('postwrite_actual_budget'",main);self.assertIn("guard('last_actual_budget'",main)
        self.assertIn('FAIL_BUDGET_AFTER_RECEIPT_RETAINED',main)
        self.assertIn('native_binary_unchanged',main);self.assertIn("assert SHA(exe)==report['native_binary_sha256']",main)

    def test_environment_clears_injection_and_labels_scope(self):
        env=fresh.sanitized_env({'CPATH':'bad','MAKEFLAGS':'bad','LD_PRELOAD':'bad','TYRIAN_GAME_PROBE_TEST':'bad','PROJECTILE_OLD':'bad','PATH':'keep'},Path('/sysroot'),Path('/tmp'))
        for key in ('CPATH','MAKEFLAGS','LD_PRELOAD','TYRIAN_GAME_PROBE_TEST','PROJECTILE_OLD'):self.assertNotIn(key,env)
        self.assertEqual(env['PATH'],'keep');self.assertEqual(env['SDL_VIDEODRIVER'],'dummy')
        self.assertIn('detect_leaks=0',env['ASAN_OPTIONS']);self.assertIn('halt_on_error=1',env['UBSAN_OPTIONS'])
        self.assertIn('not a\nnew gameplay capture',fresh.__doc__)
        self.assertIn('LSan is disabled',fresh.__doc__)


if __name__=='__main__':unittest.main(verbosity=2)
