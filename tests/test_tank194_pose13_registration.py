"""Finite public-only deliberate13 adaptation registration tests, without native or art work."""
import copy,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(os.environ.get('TANK194_TEST_SOURCE_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import current_tank194_body_registration as B
import current_tank194_extra_registration as X
import current_tank194_poses15_17_registration as Y
import current_tank194_pose89_registration as Z
import current_tank194_pose13_registration as E

class Pose13Registration(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'source';self.root.mkdir()
        old=B.object_bytes(B.regular(ROOT,B.PROOF));extra=B.object_bytes(B.regular(ROOT,X.PROOF));third=B.object_bytes(B.regular(ROOT,Y.PROOF));single=B.object_bytes(B.regular(ROOT,Z.PROOF));self.proof=B.object_bytes(B.regular(ROOT,E.PROOF))
        names={B.PROOF,X.PROOF,Y.PROOF,Z.PROOF,E.PROOF,*[r['path'] for r in old['public_sources'].values()],*[r['manual_row']['source_path'] for r in old['resources']],*[m['canonical_material']['path'] for m in self.proof['members']],*[m['canonical_material']['path'] for m in extra['members']],*[m['canonical_material']['path'] for m in third['members']],*[m['canonical_material']['path'] for m in single['members']]}
        for name in names:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(B.regular(ROOT,name))
        self.old_outputs=B.generate(self.root);self.extra_outputs=X.generate(self.root);self.third_outputs=Y.generate(self.root);self.single_outputs=Z.generate(self.root);self.outputs=E.generate(self.root)
        for name,raw in {**self.old_outputs,**self.extra_outputs,**self.third_outputs,**self.single_outputs,**self.outputs}.items():
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        self.rows=E.rows_for(self.root);self.old_rows=B.rows_for(self.root);self.extra_rows=X.rows_for(self.root);self.third_rows=Y.rows_for(self.root);self.single_rows=Z.rows_for(self.root)
    def tearDown(self):self.tmp.cleanup()
    def check(self,rows=None,required=True):E.validate_runtime_rows(self.root,{'files':self.rows if rows is None else rows},required)
    def cli(self,*args):
        script=Path(E.__file__).with_name('build_tank194_body_registration.py')
        return subprocess.run([sys.executable,str(script),'--root',str(self.root),*map(str,args)],capture_output=True,text=True)
    def test_public_only_exact_two_outputs(self):
        self.assertEqual(self.outputs,E.generate(self.root));self.assertEqual(len(self.outputs),2)
        self.assertEqual(B.sha(self.outputs[E.HEADER]),'bfb184c7ad6cad417cfef935f5dca915c644fbdd32ccd870efa6e1a6636442e9')
        self.assertEqual(self.outputs[E.HEADER],B.regular(ROOT,E.HEADER))
        self.assertEqual(sum(len(v) for k,v in self.outputs.items() if k.endswith('.hda')),172060)
        member=self.proof['members'][0];adapt=self.proof['adaptation']
        self.assertIs(adapt['exact_native_alias'],False);self.assertIs(member['exact_native_alias'],False)
        self.assertEqual(adapt['difference_counts'],{'added_coverage':7,'removed_coverage':2,'changed_index':3});self.assertEqual(len(adapt['differing_cells']),12)
        self.assertNotEqual(member['indices_sha256'],adapt['canonical_indices_sha256']);self.assertNotEqual(member['mask_sha256'],adapt['canonical_mask_sha256'])
        self.assertEqual([t['index'] for t in member['source_tiles']],[13,14,32,33]);self.assertEqual(self.proof['additional_palette'],[{'index':116,'rgb':'860400'}])
        self.assertIs(self.proof['base_is_unpublished'],True);self.assertIsNone(self.proof['base_commit'])
        self.assertFalse((self.root/'newshp.shp').exists());self.assertFalse((self.root/'tyrian.hdt').exists())
    def test_input_paths_public_authority_and_canonical_only(self):
        paths=E.input_paths(self.root);self.assertEqual(len(paths),5);self.assertEqual(paths,sorted(set(paths)))
        for name in paths:B.regular(self.root,name)
        self.assertNotIn(E.HEADER,paths);self.assertTrue(all(not p.startswith(E.PREFIX) for p in paths))
    def test_exact_union_and_original_gameplay_rows(self):
        rows=self.rows+self.old_rows+self.extra_rows+self.third_rows+self.single_rows+list(E.gameplay_rows(self.proof).values())
        self.check(rows);B.validate_runtime_rows(self.root,{'files':rows},required=True);X.validate_runtime_rows(self.root,{'files':rows},required=True);Y.validate_runtime_rows(self.root,{'files':rows},required=True);Z.validate_runtime_rows(self.root,{'files':rows},required=True)
        self.assertEqual(len(E.load(self.root)),1);self.assertEqual(B.generate(self.root),self.old_outputs)
        self.assertEqual({r['identity'] for r in self.rows},{1010091})
    def test_optional_and_required_absent(self):
        self.check([],False)
        with self.assertRaises(ValueError):self.check([],True)
    def test_missing_duplicate_and_extra_rows(self):
        for rows in [self.rows[:0],self.rows+[self.rows[0]],self.rows+[dict(self.rows[0],destination='assets/global/extra.hda')]]:
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
        self.assertEqual(B.load(self.root),{r['destination']:r for r in self.old_rows});self.assertEqual(X.load(self.root),{r['destination']:r for r in self.extra_rows});self.assertEqual(Y.load(self.root),{r['destination']:r for r in self.third_rows});self.assertEqual(Z.load(self.root),{r['destination']:r for r in self.single_rows})
    def test_header_missing_and_drift(self):
        p=self.root/E.HEADER;raw=p.read_bytes();p.unlink()
        with self.assertRaises((ValueError,OSError)):self.check()
        p.write_bytes(raw+b'\n')
        with self.assertRaises(ValueError):self.check()
    def test_canonical_corruption(self):
        p=self.root/self.rows[0]['canonical_source'];raw=p.read_bytes();p.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
        with self.assertRaises(ValueError):E.generate(self.root)
    def test_changed_adaptation_source_and_difference_authority_rejected(self):
        p=self.root/E.PROOF;raw=p.read_bytes();p.write_bytes(raw+b'\n')
        with self.assertRaises(ValueError):E.generate(self.root)
        p.write_bytes(raw)
        changes=[('exact_alias',lambda q:q['adaptation'].update(exact_native_alias=True)),
                 ('donor_substitution',lambda q:q['members'][0].update(indices_sha256=q['adaptation']['canonical_indices_sha256'])),
                 ('native_tile',lambda q:q['members'][0]['source_tiles'][0].update(decoded_indices_then_coverage_fnv='0'*16)),
                 ('delta_cell',lambda q:q['adaptation']['differing_cells'][0].update(new_covered=True)),
                 ('delta_count',lambda q:q['adaptation']['difference_counts'].update(added_coverage=6)),
                 ('palette116',lambda q:q['additional_palette'][0].update(rgb='000000'))]
        for name,change in changes:
            q=copy.deepcopy(self.proof);change(q);altered=json.dumps(q).encode();p.write_bytes(altered)
            # Bypass only outer hash in this negative to exercise the semantic gate itself.
            with self.subTest(name=name),patch.object(E,'PROOF_SHA256',B.sha(altered)),self.assertRaises(ValueError):E.authority(self.root)
        p.write_bytes(raw)
        q=copy.deepcopy(self.proof);q['adaptation']['differing_cells'][0]['existing_HD_alpha_nonzero']+=1
        with self.assertRaises(ValueError):E.canonical(self.root,q)
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
    def test_old_cli_modes_unchanged_and_single_explicit(self):
        for args,count in [(('--check',),2),(('--extra-poses','--check'),2),(('--poses15-17','--check'),2),(('--pose89','--check'),1),(('--pose13-adaptation','--check'),1)]:
            r=self.cli(*args);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout)['aliases'],count)
        self.assertEqual(B.generate(self.root),self.old_outputs)
    def test_single_cli_generates_exact_isolated_outputs(self):
        out=Path(self.tmp.name)/'output';r=self.cli('--pose13-adaptation','--output',out);self.assertEqual(r.returncode,0,r.stderr)
        files={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()};self.assertEqual(files,self.outputs)
        self.assertNotEqual(self.cli('--pose13-adaptation','--output',out).returncode,0)
    def test_cli_invalid_modes_do_not_write(self):
        before={p.relative_to(self.root).as_posix():B.sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
        for args in [('--pose13-adaptation',),('--pose13-adaptation','--verify-original-data',self.root),('--pose13-adaptation','--check','--output',Path(self.tmp.name)/'invalid'),('--extra-poses','--pose13-adaptation','--check'),('--poses15-17','--pose13-adaptation','--check'),('--pose89','--pose13-adaptation','--check')]:
            with self.subTest(args=args):self.assertNotEqual(self.cli(*args).returncode,0)
        after={p.relative_to(self.root).as_posix():B.sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()};self.assertEqual(before,after)
    def test_proof_root_and_unsafe_source_paths(self):
        self.assertEqual(E.generate(self.root,self.root),self.outputs)
        for source in ['../outside.hda','/tmp/outside.hda','bad\\path.hda']:
            with self.subTest(source=source),self.assertRaises(ValueError):self.check(self.rows+[{'source_path':source}])

if __name__=='__main__':unittest.main(verbosity=2)
