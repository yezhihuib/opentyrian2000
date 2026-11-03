"""Finite pure registration tests. No originals, compiler, native run or art derivation.
Point TANK194_TEST_SOURCE_ROOT at a repository-layout authority fixture if needed.
"""
import copy,hashlib,json,os,re,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(os.environ.get('TANK194_TEST_SOURCE_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import current_tank194_body_registration as B
QUALIFIED_HEADER_BODY_SHA256='8107806b5df9211c7bf31e165a08c7879bb052bb7fdf03960c55afb57c44d33f'
class Registration(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'source';self.root.mkdir()
        proof=B.object_bytes(B.regular(ROOT,B.PROOF));names=[B.PROOF]+[r['path']for r in proof['public_sources'].values()]+[r['manual_row']['source_path']for r in proof['resources']]
        for name in names:
            dst=self.root/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(B.regular(ROOT,name))
        self.outputs=B.generate(self.root)
        for name,raw in self.outputs.items():
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        self.rows=B.rows_for(self.root);self.proof=proof
    def tearDown(self):self.tmp.cleanup()
    def check(self,rows=None,required=True):B.validate_runtime_rows(self.root,{'files':self.rows if rows is None else rows},required)
    def test_public_only_deterministic_three_outputs(self):
        self.assertEqual(self.outputs,B.generate(self.root));self.assertEqual(len(self.outputs),3)
        self.assertFalse((self.root/'newshp.shp').exists());self.assertFalse((self.root/'tyrian.hdt').exists())
        for r in self.proof['resources']:
            raw=B.regular(self.root,r['manual_row']['source_path']);self.assertEqual(self.outputs[B.PREFIX+B.sha(raw)+'.hda'],raw)
    def test_comment_only_header_bridge(self):
        raw=self.outputs[B.HEADER];body=re.sub(rb'\A/\*.*?\*/\n',b'',raw,count=1,flags=re.S)
        self.assertEqual(hashlib.sha256(body).hexdigest(),QUALIFIED_HEADER_BODY_SHA256)
        self.assertIn(B.PROOF.encode(),raw);self.assertIn(B.PROOF_SHA256.encode(),raw)
        self.assertNotIn(b'REBUILT-MATERIAL',raw);self.assertNotIn(b'/workspace/',raw)
    def test_exact_rows_and_old_gameplay_preserved(self):
        self.check();self.check(self.rows+[copy.deepcopy(r['manual_row'])for r in self.proof['resources']]);self.assertEqual(len(B.load(self.root)),2)
    def test_no_new_unique_art_content(self):
        for r in self.rows:self.assertEqual(B.sha(B.regular(self.root,r['canonical_source'])),r['sha256'])
        self.assertEqual(sum(r['bytes']for r in self.rows),344120)
    def test_optional_and_required_absent(self):
        self.check([],False)
        with self.assertRaises(ValueError):self.check([],True)
    def test_missing_duplicate_extra(self):
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
    def test_header_missing_and_drift(self):
        p=self.root/B.HEADER;raw=p.read_bytes();p.unlink()
        with self.assertRaises((ValueError,OSError)):self.check()
        p.write_bytes(raw+b'\n')
        with self.assertRaises(ValueError):self.check()
    def test_canonical_corruption(self):
        p=self.root/self.rows[0]['canonical_source'];raw=p.read_bytes();p.write_bytes(raw[:4]+bytes([raw[4]^1])+raw[5:])
        with self.assertRaises(ValueError):B.generate(self.root)
    def test_changed_public_registry_rejected(self):
        p=self.root/self.proof['public_sources']['legacy_global_registry']['path'];p.write_bytes(p.read_bytes()+b'\n')
        with self.assertRaises(ValueError):B.generate(self.root)
    def test_changed_public_legacy_proof_rejected(self):
        p=self.root/self.proof['public_sources']['legacy_source_proof']['path'];p.write_bytes(p.read_bytes()+b'\n')
        with self.assertRaises(ValueError):B.generate(self.root)
    def test_changed_finite_authority_rejected(self):
        p=self.root/B.PROOF;obj=json.loads(p.read_bytes());obj['original_source']['bank']['bytes']+=1;p.write_text(json.dumps(obj))
        with self.assertRaises(ValueError):B.generate(self.root)
    def test_old_gameplay_row_changed(self):
        r=copy.deepcopy(self.proof['resources'][0]['manual_row']);r['destination']='assets/gameplay/hidden.hda'
        with self.assertRaises(ValueError):self.check(self.rows+[r])
    def test_hidden_header_identity_collision(self):
        (self.root/'hidden.hda').write_bytes(B.regular(self.root,self.rows[0]['canonical_source']))
        with self.assertRaises(ValueError):self.check(self.rows+[{'source_path':'hidden.hda','destination':'assets/other.hda'}])
    def test_source_symlink_rejected(self):
        p=self.root/self.rows[0]['source_path'];raw=p.read_bytes();p.unlink();(self.root/'other.hda').write_bytes(raw);p.symlink_to(self.root/'other.hda')
        with self.assertRaises(ValueError):self.check()
    def test_optional_original_verifier_needs_caller_data(self):
        with self.assertRaises((ValueError,OSError)):B.verify_original_data(self.root,self.root)
        self.assertEqual(self.outputs,B.generate(self.root))
    def test_cli_missing_output_does_not_write(self):
        before={p.relative_to(self.root).as_posix():B.sha(p.read_bytes())for p in self.root.rglob('*')if p.is_file()}
        script=Path(B.__file__).with_name('build_tank194_body_registration.py')
        result=subprocess.run([sys.executable,str(script),'--root',str(self.root)],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);after={p.relative_to(self.root).as_posix():B.sha(p.read_bytes())for p in self.root.rglob('*')if p.is_file()};self.assertEqual(before,after)
if __name__=='__main__':unittest.main(verbosity=2)
