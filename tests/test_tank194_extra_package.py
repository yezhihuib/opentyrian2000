"""Bounded package gates, source metadata and finite rebuild-hook checks.

No full producer, full package, artwork derivation, compiler or native execution.
Optional TANK194_EXTRA_PACKAGE_ROOT supplies a repository-layout current fixture;
TANK194_OLD_PACKAGE_ROOT supplies the actual frozen prior331-source public tree.
"""
import ast,builtins,copy,json,os,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(os.environ.get('TANK194_EXTRA_PACKAGE_ROOT',Path(__file__).resolve().parents[1]))
OLD_ROOT=os.environ.get('TANK194_OLD_PACKAGE_ROOT')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import package_runtime as PACK
import verify_current_production as V
import check_runtime_source_binding as C
import current_tank194_body_registration as B
import current_tank194_extra_registration as E
import current_tank194_source_bridge as BR

class ReachedDownstream(Exception):pass

class ExtraPackage(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'source';shutil.copytree(ROOT,self.root)
        self.path=self.root/BR.RUNTIME;self.manifest=json.loads(self.path.read_bytes())
        self.receipt=json.loads((self.root/C.SOURCE).read_bytes())
    def tearDown(self):self.tmp.cleanup()
    def save(self,manifest,path=None):(path or self.path).write_text(json.dumps(manifest))
    def package_boundary(self,root=None,manifest=None,success=True):
        root=root or self.root;output=Path(self.tmp.name)/'package-output';original=builtins.__import__;seen=[]
        def monitored(name,*args,**kwargs):
            if name=='current_projectile145_compatibility':seen.append(name);raise ReachedDownstream
            return original(name,*args,**kwargs)
        argv=['--source-root',str(root),'--build','--output',str(output)]
        if manifest is not None:argv+=['--manifest',str(manifest)]
        with patch('builtins.__import__',side_effect=monitored):
            with self.assertRaises(ReachedDownstream if success else (ValueError,OSError)):PACK.main(argv)
        self.assertEqual(seen,['current_projectile145_compatibility'] if success else [])
        self.assertFalse(output.exists())
    def test_actual332_raw_metadata_and_source_pins(self):
        self.assertEqual(V.verify(self.root,self.receipt),332)
        self.assertEqual(C.check(self.root,self.path)['declared_source_files'],332)
        self.assertEqual(self.receipt['production_source_manifest_sha256'],'155c01a82f047251a49b358aa9cbbfde9abc2bb3695d29e98a744e90cc777aa8')
        self.assertEqual(V.source_inventory(self.root),BR.extra_proof(self.root)['source_sha256'])
        binding=next(r for r in self.manifest['files'] if r['destination']==C.DESTINATION);raw=(self.root/C.SOURCE).read_bytes()
        self.assertEqual((binding['bytes'],binding['sha256'],binding['git_blob']),(len(raw),B.sha(raw),B.blob(raw)))
        for name in ['src/global_tank194_body_mirror.inc',E.HEADER]:
            p=self.root/name;raw=p.read_bytes();p.write_bytes(raw+b'\n')
            with self.subTest(name=name),self.assertRaises(ValueError):V.verify(self.root,self.receipt)
            p.write_bytes(raw)
    def test_all1130_unrelated_rows_match_prior_public_digest(self):
        projected=BR.project_extra_runtime_rows(self.root,self.manifest)
        fixed=[r for r in projected if r['source_path']!=BR.BINDING]
        self.assertEqual(len(self.manifest['files']),1135);self.assertEqual(len(projected),1131);self.assertEqual(len(fixed),1130)
        old=BR.proof(self.root);extra=BR.extra_proof(self.root)
        self.assertEqual(V.source_manifest_digest(fixed),old['projected_nonbinding_rows_sha256'])
        self.assertEqual(extra['projected_nonbinding_rows_sha256'],old['projected_nonbinding_rows_sha256'])
        self.assertEqual(self.manifest['closure']['global_tank194_body_alias_files'],4)
        self.assertEqual(self.manifest['closure']['global_content_hda_files'],137)
        self.assertEqual(self.manifest['closure']['global_shared_enemy_tank_alias_files'],2)
        changed=copy.deepcopy(self.manifest);row=next(r for r in changed['files'] if r['source_path']!=BR.BINDING and r.get('revision') not in (B.REVISION,E.REVISION));row['bytes']+=1
        with self.assertRaises(ValueError):BR.project_extra_runtime_rows(self.root,changed)
    def test_default_explicit_and_renamed_actual_package_gate(self):
        self.package_boundary();self.package_boundary(manifest=self.path)
        renamed=self.root/'renamed-runtime.json';self.save(self.manifest,renamed);self.package_boundary(manifest=renamed)
        alias=self.root/E.rows_for(self.root)[0]['source_path'];alias.unlink()
        for path in [None,self.path,renamed]:
            with self.subTest(path=str(path)):self.package_boundary(manifest=path,success=False)
    def test_wrong_epoch_count_and_absent_new_pair_cannot_fallback(self):
        cases=[]
        bad=copy.deepcopy(self.manifest);bad['source_revision'][C.DIGEST]=BR.CURRENT_DIGEST;cases.append(bad)
        for count in [None,True,2,3,5]:
            bad=copy.deepcopy(self.manifest);bad['closure']['global_tank194_body_alias_files']=count;cases.append(bad)
        bad=copy.deepcopy(self.manifest);bad['files']=[r for r in bad['files'] if r.get('revision')!=E.REVISION];cases.append(bad)
        for i,manifest in enumerate(cases):
            for name in [BR.RUNTIME,'renamed-runtime.json']:
                path=self.root/name;self.save(manifest,path)
                with self.subTest(case=i,path=name):self.package_boundary(manifest=path,success=False)
        self.save(self.manifest)
    def test_actual_finite_rebuilder_hook_collision_and_counts(self):
        script=self.root/'scripts/rebuild_recovered_runtime_manifest.py';tree=ast.parse(script.read_text())
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        start=next(i for i,n in enumerate(main.body) if isinstance(n,ast.ImportFrom) and n.module=='current_tank194_source_bridge')
        nodes=main.body[start:start+3];self.assertIsInstance(nodes[1],ast.Assign);self.assertIsInstance(nodes[2],ast.If)
        self.assertTrue(any(isinstance(n,ast.For) for n in nodes[2].body))
        keys={'global_content_hda_files','global_tank194_body_alias_files','global_shared_enemy_tank_alias_files'}
        counts=[n for n in main.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Subscript) and isinstance(n.targets[0].slice,ast.Constant) and n.targets[0].slice.value in keys]
        self.assertEqual(len(counts),3)
        code=compile(ast.fix_missing_locations(ast.Module(body=nodes+counts,type_ignores=[])),str(script),'exec')
        env={'root':self.root,'current':self.receipt,'rows':{},'j':{'closure':{}}};exec(code,env)
        self.assertEqual(env['rows'],E.load(self.root));self.assertEqual(len(env['rows']),2)
        self.assertEqual(env['j']['closure'],{'global_content_hda_files':137,'global_tank194_body_alias_files':4,'global_shared_enemy_tank_alias_files':2})
        with self.assertRaisesRegex(ValueError,'collision'):exec(code,env)
        old={'root':self.root,'current':{'production_source_manifest_sha256':BR.CURRENT_DIGEST},'rows':{},'j':{'closure':{}}};exec(code,old)
        self.assertEqual(old['rows'],{});self.assertEqual(old['j']['closure'],{'global_content_hda_files':135,'global_tank194_body_alias_files':2,'global_shared_enemy_tank_alias_files':2})
    @unittest.skipUnless(OLD_ROOT,'Set TANK194_OLD_PACKAGE_ROOT to the actual frozen prior public tree')
    def test_actual_prior331_package_stays_old_pair(self):
        old=Path(self.tmp.name)/'prior';shutil.copytree(Path(OLD_ROOT),old)
        receipt=json.loads((old/C.SOURCE).read_bytes());manifest=json.loads((old/BR.RUNTIME).read_bytes())
        self.assertEqual(V.verify(old,receipt),331);self.assertEqual(C.check(old,old/BR.RUNTIME)['declared_source_files'],331)
        self.assertEqual(receipt['production_source_manifest_sha256'],BR.CURRENT_DIGEST)
        self.assertEqual(len(manifest['files']),1133);self.assertEqual(manifest['closure']['global_tank194_body_alias_files'],2)
        self.assertEqual(len(B.load(old)),2);self.assertFalse((old/E.HEADER).exists())
        self.package_boundary(root=old);self.package_boundary(root=old,manifest=old/BR.RUNTIME)

if __name__=='__main__':unittest.main(verbosity=2)
