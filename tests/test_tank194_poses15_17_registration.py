"""Finite public-only 15/17 registration tests, without native or art work."""
import copy,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(os.environ.get('TANK194_TEST_SOURCE_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import current_tank194_body_registration as B
import current_tank194_extra_registration as X
import current_tank194_poses15_17_registration as E

class Poses15_17Registration(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'source';self.root.mkdir()
        old=B.object_bytes(B.regular(ROOT,B.PROOF));extra=B.object_bytes(B.regular(ROOT,X.PROOF));self.proof=B.object_bytes(B.regular(ROOT,E.PROOF))
        names={B.PROOF,X.PROOF,E.PROOF,*[r['path'] for r in old['public_sources'].values()],*[r['manual_row']['source_path'] for r in old['resources']],*[m['canonical_material']['path'] for m in self.proof['members']],*[m['canonical_material']['path'] for m in extra['members']]}
        for name in names:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(B.regular(ROOT,name))
        self.old_outputs=B.generate(self.root);self.extra_outputs=X.generate(self.root);self.outputs=E.generate(self.root)
        for name,raw in {**self.old_outputs,**self.extra_outputs,**self.outputs}.items():
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        self.rows=E.rows_for(self.root);self.old_rows=B.rows_for(self.root);self.extra_rows=X.rows_for(self.root)
    def tearDown(self):self.tmp.cleanup()
    def check(self,rows=None,required=True):E.validate_runtime_rows(self.root,{'files':self.rows if rows is None else rows},required)
    def cli(self,*args):
        script=Path(E.__file__).with_name('build_tank194_body_registration.py')
        return subprocess.run([sys.executable,str(script),'--root',str(self.root),*map(str,args)],capture_output=True,text=True)
    def test_public_only_exact_three_outputs(self):
        self.assertEqual(self.outputs,E.generate(self.root));self.assertEqual(len(self.outputs),3)
        self.assertEqual(B.sha(self.outputs[E.HEADER]),'7e46b4e006e94c08af040f4bdeca0aed3ffb7cf4b8da364f45b3ab4f5386faea')
        self.assertEqual(self.outputs[E.HEADER],B.regular(ROOT,E.HEADER))
        self.assertEqual(sum(len(v) for k,v in self.outputs.items() if k.endswith('.hda')),344120)
        self.assertFalse((self.root/'newshp.shp').exists());self.assertFalse((self.root/'tyrian.hdt').exists())
    def test_input_paths_public_authority_and_canonical_only(self):
        paths=E.input_paths(self.root);self.assertEqual(len(paths),6);self.assertEqual(paths,sorted(set(paths)))
        for name in paths:B.regular(self.root,name)
        self.assertNotIn(E.HEADER,paths);self.assertTrue(all(not p.startswith(E.PREFIX) for p in paths))
    def test_exact_union_and_original_gameplay_rows(self):
        rows=self.rows+self.old_rows+self.extra_rows+list(E.gameplay_rows(self.proof).values())
        self.check(rows);B.validate_runtime_rows(self.root,{'files':rows},required=True);X.validate_runtime_rows(self.root,{'files':rows},required=True)
        self.assertEqual(len(E.load(self.root)),2);self.assertEqual(B.generate(self.root),self.old_outputs)
        self.assertEqual({r['identity'] for r in self.rows},{1010045,1010093})
    def test_optional_and_required_absent(self):
        self.check([],False)
        with self.assertRaises(ValueError):self.check([],True)
    def test_missing_duplicate_and_extra_rows(self):
        for rows in [self.rows[:1],self.rows+[self.rows[0]],self.rows+[dict(self.rows[0],destination='assets/global/extra.hda')]]:
            with self.subTest(rows=len(rows)),self.assertRaises(ValueError):self.check(rows)
    def test_metadata_omission_and_boolean_types(self):
        for key in self.rows[0]:
            rows=copy.deepcopy(self.rows);del rows[0][key]
            with self.subTest(key=key),self.assertRaises(ValueError):self.check(rows)
        for key in ['identity','density','bytes']:
            rows=copy.deepcopy(self.rows);rows[0][key]=True
            with self.subTest(key=key),self.assertRaises(ValueError):self.check(rows)
    def test_alias_missing_and_same_size_corruption(self):
        p=self.root/self.rows[0]['source_path'];raw=p.read_bytes();p.unlink()
        with self.assertRaises((ValueError,OSError)):self.check()
        p.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
        with self.assertRaises(ValueError):self.check()
        self.assertEqual(B.load(self.root),{r['destination']:r for r in self.old_rows});self.assertEqual(X.load(self.root),{r['destination']:r for r in self.extra_rows})
    def test_header_missing_and_drift(self):
        p=self.root/E.HEADER;raw=p.read_bytes();p.unlink()
        with self.assertRaises((ValueError,OSError)):self.check()
        p.write_bytes(raw+b'\n')
        with self.assertRaises(ValueError):self.check()
    def test_canonical_corruption(self):
        p=self.root/self.rows[0]['canonical_source'];raw=p.read_bytes();p.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
        with self.assertRaises(ValueError):E.generate(self.root)
    def test_changed_third_authority_rejected(self):
        p=self.root/E.PROOF;p.write_bytes(p.read_bytes()+b'\n')
        with self.assertRaises(ValueError):E.generate(self.root)
    def test_changed_legacy_authorities_rejected(self):
        old=B.object_bytes(B.regular(self.root,B.PROOF))
        for name in [B.PROOF,*[r['path'] for r in old['public_sources'].values()]]:
            p=self.root/name;raw=p.read_bytes();p.write_bytes(raw+b'\n')
            with self.subTest(name=name),self.assertRaises(ValueError):E.generate(self.root)
            p.write_bytes(raw)
    def test_original_gameplay_changed_or_duplicate(self):
        manual=list(E.gameplay_rows(self.proof).values())
        with self.assertRaises(ValueError):self.check(self.rows+manual+manual[:1])
        for key,value in [('destination','assets/gameplay/hidden.hda'),('bytes',True),('revision','other')]:
            changed=copy.deepcopy(manual);changed[0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.check(self.rows+changed)
    def test_hidden_header_identity_collision(self):
        (self.root/'hidden.hda').write_bytes(B.regular(self.root,self.rows[0]['canonical_source']))
        with self.assertRaises(ValueError):self.check(self.rows+[{'source_path':'hidden.hda','destination':'assets/other.hda'}])
    def test_alias_and_canonical_symlinks_rejected(self):
        for key in ['source_path','canonical_source']:
            p=self.root/self.rows[0][key];raw=p.read_bytes();p.unlink();other=self.root/'other.hda';other.write_bytes(raw);p.symlink_to(other)
            with self.subTest(key=key),self.assertRaises(ValueError):self.check()
            p.unlink();p.write_bytes(raw)
    def test_old_cli_modes_unchanged_and_third_explicit(self):
        for args in [('--check',),('--extra-poses','--check'),('--poses15-17','--check')]:
            r=self.cli(*args);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout)['aliases'],2)
        self.assertEqual(B.generate(self.root),self.old_outputs)
    def test_third_cli_generates_exact_isolated_outputs(self):
        out=Path(self.tmp.name)/'output';r=self.cli('--poses15-17','--output',out);self.assertEqual(r.returncode,0,r.stderr)
        files={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()};self.assertEqual(files,self.outputs)
        self.assertNotEqual(self.cli('--poses15-17','--output',out).returncode,0)
    def test_cli_invalid_modes_do_not_write(self):
        before={p.relative_to(self.root).as_posix():B.sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
        for args in [('--poses15-17',),('--poses15-17','--verify-original-data',self.root),('--poses15-17','--check','--output',Path(self.tmp.name)/'invalid'),('--extra-poses','--poses15-17','--check')]:
            with self.subTest(args=args):self.assertNotEqual(self.cli(*args).returncode,0)
        after={p.relative_to(self.root).as_posix():B.sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()};self.assertEqual(before,after)
    def test_proof_root_and_unsafe_source_paths(self):
        self.assertEqual(E.generate(self.root,self.root),self.outputs)
        for source in ['../outside.hda','/tmp/outside.hda','bad\\path.hda']:
            with self.subTest(source=source),self.assertRaises(ValueError):self.check(self.rows+[{'source_path':source}])

if __name__=='__main__':unittest.main(verbosity=2)
