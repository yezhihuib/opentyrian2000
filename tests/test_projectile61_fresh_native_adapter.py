#!/usr/bin/env python3
"""Pure fresh61 build/oracle adapter contracts; never starts compiler or game."""
from pathlib import Path
import ast,hashlib,importlib.util,inspect,json,os,sys,unittest
HERE=Path(__file__).resolve().parent
DEFAULT_ROOT=HERE.parent if (HERE.parent/'src').is_dir() else HERE.parents[1]/'projectile61-private-sparse'
ROOT=Path(os.environ.get('PROJECTILE61_STATIC_ROOT',str(DEFAULT_ROOT)))
spec=importlib.util.spec_from_file_location('projectile61_fresh_under_test',HERE/'projectile61_fresh_native_validation.py')
fresh=importlib.util.module_from_spec(spec);spec.loader.exec_module(fresh)
OLD_STDOUT='PASS inherited91 native lifecycle: 37 cases 81611 assertions\n145_TO_TALON copied=376 cached=0\n145_TO_TALON copied=376 cached=1\nPASS shared145 native lifecycle: 70 new cases 141992 new assertions; internal8 only; not gameplay/full build\n'
NEW_STDOUT='61_TO_TALON copied=267 cached=0\n61_TO_TALON copied=267 cached=1\nPASS shared61 native lifecycle: 157 cases 822291 assertions; internal8 only; not gameplay/full build\n'

class Projectile61FreshAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=Path(fresh.__file__).read_text()
        cls.units=sorted(p.stem for p in (ROOT/'src').glob('*.c'))
        cls.accepted_driver=ROOT/'tests/projectile61_native_validation.py'
        assert fresh.SHA(cls.accepted_driver)==fresh.PRIOR61_DRIVER_SHA,'Current checkout native driver differs from acceptedv3; no external fallback'
        cls.accepted_companion=cls.accepted_driver.with_name('projectile61_native_additions.c.inc')

    def log(self,mode):
        flags=' -MD -DNDEBUG '+fresh.MODES[mode]
        if mode=='hd-on-asan-ubsan':flags+=' '+' '.join(fresh.SAN)
        return '\n'.join('cc'+flags+' -c -o obj/'+n+'.o src/'+n+'.c' for n in self.units)

    def test_fixed_four_serial_make_modes_and_exact_budget(self):
        self.assertEqual(list(fresh.MODES),['default-off','hd-on','mirror-disabled','hd-on-asan-ubsan'])
        self.assertEqual((fresh.PEAK,fresh.RESERVE,fresh.START_REQUIRED),(268435456,262144000,530579456))
        self.assertTrue(fresh.budget_ok(fresh.PEAK,fresh.RESERVE))
        self.assertFalse(fresh.budget_ok(fresh.PEAK+1,fresh.RESERVE))
        self.assertFalse(fresh.budget_ok(fresh.PEAK,fresh.RESERVE-1))
        for mode in fresh.MODES:
            argv=fresh.make_command(mode,Path('/sysroot'),Path('/tools/cc'),Path('/tools/pkg-config'))
            self.assertEqual(argv[:2],['make','-j2'])
            self.assertIn('CC=/tools/cc',argv)
            self.assertIn('PKG_CONFIG=/tools/pkg-config',argv)
            cpp=next(x for x in argv if x.startswith('CPPFLAGS='))
            self.assertIn('-MD -DNDEBUG',cpp)
            self.assertEqual('-DNEWSHF_HD_COMPOSITOR=1' in cpp,mode!='default-off')
            self.assertEqual('-DRENDER_MIRROR_DISABLED' in cpp,mode=='mirror-disabled')
            cflags=next(x for x in argv if x.startswith('CFLAGS='))
            ldflags=next(x for x in argv if x.startswith('LDFLAGS='))
            self.assertEqual('-fsanitize=address,undefined' in cflags,mode=='hd-on-asan-ubsan')
            self.assertEqual('-fsanitize=address,undefined' in ldflags,mode=='hd-on-asan-ubsan')

    def test_exact86_compile_contract_all_modes_and_no_duplicate_units(self):
        self.assertEqual(len(self.units),86)
        for mode in fresh.MODES:self.assertEqual(len(fresh.compile_contract(self.log(mode),self.units,mode)),86)
        mode='hd-on-asan-ubsan';lines=self.log(mode).splitlines()
        for changed in ('\n'.join(lines[:-1]),'\n'.join(lines+[lines[0]]),'\n'.join(lines[:-1]+[lines[0]])):
            with self.assertRaises(AssertionError):fresh.compile_contract(changed,self.units,mode)
        for flag in fresh.SAN:
            changed=self.log(mode).replace(flag,'',1)
            with self.assertRaises(AssertionError):fresh.compile_contract(changed,self.units,mode)

    def test_compile_contract_rejects_wrong_feature_macros_and_input(self):
        for mode in fresh.MODES:
            changed=self.log(mode).replace('src/'+self.units[0]+'.c','src/wrong.c',1)
            with self.assertRaises(AssertionError):fresh.compile_contract(changed,self.units,mode)
        with self.assertRaises(AssertionError):fresh.compile_contract(self.log('hd-on'),self.units,'default-off')
        with self.assertRaises(AssertionError):fresh.compile_contract(self.log('mirror-disabled'),self.units,'hd-on')
        with self.assertRaises(AssertionError):fresh.compile_contract(self.log('hd-on-asan-ubsan'),self.units,'hd-on')

    def test_exact107_legacy_harness_and_accepted_v3_wrapper_companion(self):
        self.assertEqual(hashlib.sha256(fresh.legacy_harness(ROOT)).hexdigest(),fresh.LEGACY_SHA)
        self.assertEqual(fresh.SHA(self.accepted_companion),fresh.COMPANION_SHA)
        wrapper=fresh.accepted_wrapper(self.accepted_driver)
        self.assertEqual(hashlib.sha256(wrapper).hexdigest(),fresh.WRAPPER_SHA)
        self.assertIn(b'return inherited145_main(argc-1,argv+1);',wrapper)
        self.assertIn(b'CHECK(argc==10',wrapper)
        self.assertIn(b'CHECK(fgetc(stdin)==EOF);',wrapper)
        self.assertNotIn(b'free(livebank)',wrapper)

    def test_264_counts_and_stdout_require_byte_equivalent_original_oracles(self):
        prior={'inherited107_stdout':OLD_STDOUT,'new61_stdout':NEW_STDOUT}
        counts=fresh.verify_stdout(OLD_STDOUT,NEW_STDOUT,prior)
        self.assertEqual(counts,dict(inherited_cases=107,inherited_assertions=223603,new_cases=157,new_assertions=822291,total_cases=264,total_assertions=1045894))
        for new in (NEW_STDOUT.replace('267','0',1),NEW_STDOUT.replace('822291','822290'),NEW_STDOUT+'\n'):
            with self.assertRaises(AssertionError):fresh.verify_stdout(OLD_STDOUT,new,prior)
        with self.assertRaises(AssertionError):fresh.verify_stdout(OLD_STDOUT.replace('81611','81610'),NEW_STDOUT,prior)

    def test_eight_finite_packs_and_current_root_content_only(self):
        self.assertEqual([row[0] for row in fresh.PACKS],['valid','missing91','missing145','bad145','bad91','missing61','bad61','only61'])
        self.assertEqual(fresh.PACKS[-1],('only61',(91,145),None))
        self.assertIn("content=r/'assets/hd/global-assets-v1/content'",self.text)
        self.assertIn("run([exe,'--inherited107',*packs[:5]]",self.text)
        self.assertIn("run([exe,'--projectile61',*packs]",self.text)
        self.assertNotIn('os.link(',self.text)
        self.assertNotIn("a.legacy_fresh/'hd-on",self.text)

    def test_prelaunch_full_hydration_and_actual_raw_index_bytes_snapshot(self):
        hydrated=inspect.getsource(fresh.hydrated_manifest)
        self.assertIn("row.startswith(b'S ')",hydrated)
        self.assertIn("--cached','--others','--exclude-standard",hydrated)
        self.assertIn('stat.S_ISREG(s.st_mode) and s.st_nlink==1',hydrated)
        self.assertIn('raw=index.read_bytes()',inspect.getsource(fresh.identity))
        self.assertIn("(q/'root-index-before.bin').write_bytes(raw_index)",self.text)
        self.assertIn("(q/'root-index-semantic-before.bin').write_bytes(semantic_index)",self.text)
        self.assertIn("(q/'root-index-after.bin').write_bytes(after_raw)",self.text)
        self.assertIn("'raw_index_unchanged':lambda:after_raw==raw_index",self.text)
        self.assertIn("'complete_hydrated_root_unchanged':lambda:hydrated_manifest(r)==root_files",self.text)

    def test_actual_semantic_after_bytes_are_retained_pinned_and_checked(self):
        self.assertIn('after_identity,after_raw,after_semantic=identity(r)',self.text)
        self.assertIn("(q/'root-index-semantic-after.bin').write_bytes(after_semantic)",self.text)
        self.assertIn('semantic_index_after_snapshot_sha256=hashlib.sha256(after_semantic).hexdigest() if after_semantic is not None else None',self.text)
        self.assertIn("'semantic_after_snapshot_intact':lambda:after_identity is not None and SHA(q/'root-index-semantic-after.bin')==after_identity['semantic_sha256']",self.text)
        self.assertNotIn('after_identity,after_raw,_=identity(r)',self.text)

    def test_no_old_object_reuse_and_all310_current_sources_bound(self):
        for required in ('len(source)==310 and len(units)==86',"prior['source_sha256']==source","shutil.copytree(r/'src',build/'src')","assert not (build/'obj').exists()",'reused_project_objects=0',"build=q/'hd-on-asan-ubsan-build'",'assert len(objects)==84',"assert all(Path(p).is_relative_to(build)","inv(build/'src')==source"):
            self.assertIn(required,self.text)
        self.assertNotIn('reused82',self.text)
        self.assertNotIn('reuse_proof',self.text)
        self.assertNotIn('borrowed=',self.text)

    def test_actual_fresh_dependencies_including_system_headers_are_bound(self):
        self.assertIn("header_roots=(a.sysroot/'usr/include',Path('/usr/include'),builtin)",self.text)
        self.assertIn("system_headers[str(p.resolve())]=SHA(p)",self.text)
        self.assertIn("assert expected==h,('Unbound or changed actual dependency'",self.text)
        self.assertIn("assert len(report['fresh_dependency_file_sha256'])==4*86+2",self.text)
        self.assertIn("'-MD','-MF',renamed_dep",self.text)
        self.assertIn("'-MD','-MF',harness_dep",self.text)
        self.assertEqual(fresh.dependency_tokens('obj/a.o: src/a.c \\\n /path/a\\ b.h\n'),['src/a.c','/path/a b.h'])
        with self.assertRaises(ValueError):fresh.dependency_tokens('no colon')

    def test_threaded_stdin_allows_continuous_budget_monitor_without_raw_persistence(self):
        self.assertIn('threading.Thread(target=feed,daemon=True)',self.text)
        self.assertIn('if feeder:feeder.start()',self.text)
        self.assertIn('while proc.poll() is None:measure()',self.text)
        self.assertIn('time.sleep(.25)',self.text)
        self.assertIn('if feeder:feeder.join(timeout=2)',self.text)
        self.assertIn('original_stdin_persisted=False',self.text)
        for payload in ('payload','old_stdin','new_stdin'):
            self.assertNotIn('write_bytes('+payload+')',self.text)
        for name in ('tyrian.shp','tyrianc.shp','palette.dat'):self.assertIn(name,fresh.DATA_SHA)
        self.assertEqual(fresh.OLD_STDIN_SHA,'7dedf7066696fc278f5fbb8dfb1462e7b6ac290cb5d08ae5260a6cdabc1ecca7')
        self.assertEqual(fresh.NEW_STDIN_SHA,'a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b')

    def test_preserves_historical_failure_and_final_receipt_budget_guards(self):
        for required in ("legacy['status']=='FAIL_BINDING_RETAINED'","disposition['status']=='ACCEPTED_FUNCTIONAL_RESULTS_WITH_RAW_INDEX_STAT_CACHE_DEVIATION'","status_before_final_checks=report['status']","budget_ok(used+4096,free-4096)","if not budget_ok(allocated(q),shutil.disk_usage(q).free)","'FAIL_BUDGET_AFTER_RECEIPT'","'FAIL_BINDING_RETAINED'"):
            self.assertIn(required,self.text)
        self.assertEqual(fresh.PRIOR61_SHA,'3fc0b94f0d3fbea059ecda7ec565ef573ac6d7ad88ec481c2b1ac4e1b80d94aa')

    def test_missing_final_input_records_false_instead_of_hiding_original_failure(self):
        checks={};errors={}
        def vanished():raise FileNotFoundError('bound input disappeared')
        self.assertFalse(fresh.guarded_check(checks,errors,'input',vanished))
        self.assertFalse(checks['input'])
        self.assertIn('FileNotFoundError',errors['input'])
        self.assertTrue(fresh.guarded_check(checks,errors,'good',lambda:True))
        self.assertNotIn('good',errors)
        self.assertIn('not q.is_relative_to(r)',self.text)
        for name in ('index_before_snapshot_intact','semantic_before_snapshot_intact','root_manifest_before_snapshot_intact','final_check_errors'):
            self.assertIn(name,self.text)

    def test_sanitized_environment_scrubs_controls_and_build_overrides(self):
        parent={'AIRCRAFT170_DIFFERENTIAL_POSE':'3','PROJECTILE61_POSE':'1','SHARED_GUARD':'1','TYRIAN_GAME_PROBE_ANY':'1','TYRIAN_CYAN_BORROW':'1','OT_SOURCE':'x','CFLAGS':'-DCHANGE','MAKEFLAGS':'-j99','CPATH':'/unsafe','KEEP':'yes'}
        before=dict(parent);env=fresh.sanitized_env(parent,Path('/sysroot'),Path('/tmpdir'))
        self.assertEqual(parent,before)
        for name in parent:
            if name!='KEEP':self.assertNotIn(name,env)
        self.assertEqual(env['KEEP'],'yes')
        self.assertEqual(env['ASAN_OPTIONS'],'detect_leaks=0:halt_on_error=1')
        self.assertEqual(env['UBSAN_OPTIONS'],'halt_on_error=1:print_stacktrace=1')
        self.assertIn('External SDL/system',fresh.__doc__)
        self.assertIn('No game loop or full gate claim.',fresh.__doc__)

if __name__=='__main__':unittest.main()
