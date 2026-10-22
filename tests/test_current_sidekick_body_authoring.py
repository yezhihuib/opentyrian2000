"""Six-source propagation and failure contracts, with independent synthetic PNGs."""
import copy,hashlib,json,os,shutil,struct,subprocess,sys,tempfile,unittest,zlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_current_sidekick_body as b
import current_sidekick_body_compatibility as compat
import verify_current_production as production
from current_art_policy import PROFILES,profile

# Deliberately independent of the implementation allowlist/name formatter.
EXPECTED={1260152:'option-marlo-bank9-152-8.hda',1290224:'option-plasma-bank9-224-8.hda',1290243:'option-plasma-bank9-243-8.hda',1290262:'option-plasma-bank9-262-8.hda',1290281:'option-plasma-bank9-281-8.hda',1290300:'option-plasma-bank9-300-8.hda'}


def png(value,width=96,height=112):
    def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    data=(b'\0'+bytes((value,17,31,127))*width)*height
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(data))+chunk(b'IEND',b'')


class CurrentSidekickBodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent=ROOT.parent/'sidekick-test-fixtures';parent.mkdir(exist_ok=True)
        cls.tmp=tempfile.TemporaryDirectory(prefix='six-',dir=parent);cls.base=Path(cls.tmp.name).resolve()
        assert cls.base.is_relative_to(parent.resolve())
        cls.root=cls.base/'repo';cls.root.mkdir();names=set(b.BUILD_INPUTS)
        for manifest in (b.RUNTIME,'packaging/runtime-assets-public63a89b3.json'):
            names.update(e['source_path']for e in json.loads((ROOT/manifest).read_text())['files'])
        for folder in ('src','scripts','packaging','assets/hd/authoring'):
            names.update(p.relative_to(ROOT).as_posix()for p in (ROOT/folder).rglob('*')if p.is_file() and '__pycache__'not in p.parts)
        for family in PROFILES:
            names.update(e['source_png']for e in json.loads((ROOT/profile(family)['selection']).read_text())['resources'])
        names.update(e['source_png']for e in json.loads((ROOT/b.SELECTION).read_text())['resources'])
        # Other legacy check() calls decode their selected PNGs and support masks.
        # The runtime inventories contain their generated HDA, not these inputs.
        for selected in ('assets/hd/authoring/tank-shell-current.json','assets/hd/authoring/enemy-energy-current.json'):
            names.update(e['source_png']for e in json.loads((ROOT/selected).read_text())['resources'])
        from current_enemy_energy_compatibility import MASK_POLICY
        names.update(spec[0]for spec in MASK_POLICY.values())
        import current_hud_recipe
        hud=json.loads((ROOT/'assets/hd/authoring/hud/current.json').read_text())
        names.update(e['path']for rows in hud['resources'].values()for e in rows)
        names.update(e['path']for e in current_hud_recipe.FIXED_INPUTS.values())
        cls.initial={n:(ROOT/n).read_bytes()for n in names}
        cls.art_hashes={p.relative_to(ROOT).as_posix():b.sha(p.read_bytes())for p in (ROOT/'assets/hd/packs').rglob('*')if p.is_file()}
        cls.serial=0

    @classmethod
    def tearDownClass(cls):
        # Entire tree is test-owned and verified inside this task's fixture root.
        assert cls.base.is_relative_to((ROOT.parent/'sidekick-test-fixtures').resolve())
        cls.tmp.cleanup()

    def setUp(self):
        for p in self.root.rglob('*'):
            if p.is_file() and p.relative_to(self.root).as_posix()not in self.initial:p.unlink()
        for n,data in self.initial.items():
            p=self.root/n
            if not p.exists()or p.read_bytes()!=data:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)

    def selected(self):return json.loads((self.root/b.SELECTION).read_text())
    def snapshot(self):return {p.relative_to(self.root).as_posix():b.sha(p.read_bytes())for p in self.root.rglob('*')if p.is_file()}
    def synthetic(self,index=0,value=27):
        j=self.selected();j['version']=f'synthetic-{index}-{value}';row=j['resources'][index]
        p=f'assets/hd/authoring/synthetic-sidekick-{index}.png';raw=png(value);(self.root/p).write_bytes(raw)
        row.update(source_png=p,source_sha256=b.sha(raw));return j
    def stage(self,j):
        type(self).serial+=1;n=type(self).serial;p=self.base/f'draft-{n}.json';p.write_bytes(b.encoded(j));dest=self.base/f'stage-{n}';b.stage(self.root,p,dest);return dest
    def nonmutating_failure(self,fn):
        before=self.snapshot()
        with self.assertRaises((ValueError,OSError)):fn()
        self.assertEqual(before,self.snapshot())

    def test_approved_bytes_and_no_runtime_source_change(self):
        self.assertEqual(b.check(self.root)['resources'],6)
        manifest=json.loads((ROOT/'assets/hd/manifest.json').read_text());old=manifest['packs'][manifest['default_preview_pack']]['files']
        mapping=compat.load(self.root)
        for identity,n in EXPECTED.items():
            row=mapping['assets/gameplay/'+n];raw=(self.root/row['source_path']).read_bytes()
            self.assertEqual(b.sha(raw),old[n]['sha256'])
            self.assertEqual(raw[:28],struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0))
        # Original C, source-bank guards, animation, ammo and fallback are byte-exact.
        tracked=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only','775b6b77163723c6cae727bafce1d53746a5bd60','--','src'],text=True).splitlines()
        for n in tracked:
            raw=subprocess.check_output(['git','-C',str(ROOT),'show','775b6b77163723c6cae727bafce1d53746a5bd60:'+n])
            self.assertEqual((ROOT/n).read_bytes(),raw,n)
        self.assertEqual(len(json.loads((self.root/b.REGISTRY).read_text())['resources']),120)

    def test_each_source_changes_only_its_declared_transport_and_pin(self):
        for index,identity in enumerate(EXPECTED):
            with self.subTest(identity=identity):
                j=self.synthetic(index,40+index);before=self.snapshot();old_runtime=json.loads((self.root/b.RUNTIME).read_text());oldmap=compat.load(self.root)
                staged=self.stage(j);self.assertEqual(before,self.snapshot());b.apply(self.root,staged)
                self.assertEqual(b.check(self.root)['status'],'PASS');mapping=compat.load(self.root);now=self.snapshot()
                dest='assets/gameplay/'+EXPECTED[identity];changed_hda=mapping[dest]['source_path']
                allowed={b.SELECTION,b.MAPPING,b.HEADER,b.BINDING,b.RUNTIME,changed_hda}
                self.assertEqual({p for p in before if before[p]!=now[p]},allowed)
                raw=(self.root/changed_hda).read_bytes()
                self.assertEqual(raw,struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0)+bytes((40+index,17,31,127))*96*112)
                for other,n in EXPECTED.items():
                    if other!=identity:self.assertEqual(now[mapping['assets/gameplay/'+n]['source_path']],before[oldmap['assets/gameplay/'+n]['source_path']])
                old_rows={e['destination']:e for e in old_runtime['files']};new_rows={e['destination']:e for e in json.loads((self.root/b.RUNTIME).read_text())['files']}
                self.assertEqual(set(old_rows),set(new_rows));self.assertEqual(len(new_rows),1006)
                self.assertEqual({p for p in old_rows if old_rows[p]!=new_rows[p]},{dest,'CURRENT-PRODUCTION-VALIDATION.json'})
                # Reset changed state without touching source repository or historical packs.
                for p in allowed:(self.root/p).write_bytes(self.initial[p])
        self.assertEqual(self.art_hashes,{p.relative_to(ROOT).as_posix():b.sha(p.read_bytes())for p in (ROOT/'assets/hd/packs').rglob('*')if p.is_file()})

    def test_global_hud_and_both_legacy_authoring_workflows_compose(self):
        j=self.synthetic();b.apply(self.root,self.stage(j))
        import build_current_art,build_current_hud,build_current_tank_shell,build_current_enemy_energy
        self.assertEqual(build_current_art.check(self.root,'pulse')['status'],'PASS')
        for module in (build_current_hud,build_current_tank_shell,build_current_enemy_energy):self.assertEqual(module.check(self.root)['status'],'PASS')

    def test_wrong_identity_shape_schema_and_order(self):
        for case in ('duplicate','missing','extra','order','global','bool','geometry','schema'):
            j=self.selected()
            if case=='duplicate':j['resources'][1]=copy.deepcopy(j['resources'][0])
            if case=='missing':j['resources'].pop()
            if case=='extra':j['resources'].append(copy.deepcopy(j['resources'][0]))
            if case=='order':j['resources'].reverse()
            if case=='global':j['resources'][0]['identity']=90229
            if case=='bool':j['resources'][0]['identity']=True
            if case=='geometry':j['resources'][0]['anchor']=[1,0]
            if case=='schema':j['schema']='opentyrian-current-pulse-authoring-v1'
            with self.subTest(case=case),self.assertRaises(ValueError):b.selection(self.root,b.encoded(j))

    def test_bad_png_dimensions_modes_hash_and_corruption(self):
        from PIL import Image
        for case in ('width','height','rgb','gif','truncated','hash'):
            j=self.synthetic();row=j['resources'][0];p=self.root/row['source_png']
            if case=='width':p.write_bytes(png(23,95,112))
            if case=='height':p.write_bytes(png(23,96,111))
            if case=='rgb':Image.new('RGB',(96,112)).save(p)
            if case=='gif':Image.new('RGBA',(96,112)).save(p,format='GIF')
            if case=='truncated':p.write_bytes(b'\x89PNG\r\n\x1a\nBAD')
            row['source_sha256']='0'*64 if case=='hash'else b.sha(p.read_bytes())
            with self.subTest(case=case):self.nonmutating_failure(lambda:b.derive(self.root,b.encoded(j)))

    def test_escape_paths_and_inside_stage_rejected(self):
        j=self.selected()
        for path in ('../outside.png','C:/outside.png','/outside.png','assets\\escape.png','assets/../escape.png','assets/CON.png'):
            j['resources'][0]['source_png']=path
            with self.subTest(path=path),self.assertRaises(ValueError):b.selection(self.root,b.encoded(j))
        with self.assertRaises(ValueError):b.stage(self.root,self.root/b.SELECTION,self.root/'inside-stage')

    def test_reparse_attributes_and_path_guards_without_link_creation(self):
        import package_runtime,build_current_art
        with patch.object(Path,'lstat',return_value=SimpleNamespace(st_file_attributes=1024)):
            self.assertTrue(package_runtime.reparse_point(Path('fixture')))
        with patch.object(Path,'lstat',return_value=SimpleNamespace(st_file_attributes=16)):
            self.assertFalse(package_runtime.reparse_point(Path('fixture')))
        with patch.object(Path,'lstat',side_effect=FileNotFoundError):
            self.assertFalse(package_runtime.reparse_point(Path('fixture')))
        relative=b.HEADER;leaf=self.root/relative
        for target in (self.root,leaf.parent,leaf):
            with self.subTest(target=str(target)),patch.object(package_runtime,'reparse_point',side_effect=lambda p:p==target):
                with self.assertRaisesRegex(ValueError,'Reparse'):package_runtime.contained_file(self.root,relative)
        stage=self.stage(self.synthetic());temporary=self.root/(b.HEADER+'.sidekick-body-tmp')
        with patch.object(package_runtime,'reparse_point',side_effect=lambda p:p==temporary):
            self.nonmutating_failure(lambda:b.apply(self.root,stage))
        with patch.object(build_current_art,'reparse_point',side_effect=lambda p:p==self.base):
            with self.assertRaisesRegex(ValueError,'Reparse'):b.stage(self.root,self.root/b.SELECTION,self.base/'blocked-stage')
        self.assertFalse((self.base/'blocked-stage').exists())

    @unittest.skipUnless(os.name=='nt' and os.environ.get('OPENTYRIAN_TEST_NTFS_JUNCTIONS')=='1','Actual junction test requires explicit opt-in and mklink /J permission')
    def test_windows_junction_input_and_output_rejected(self):
        outside=self.base/'outside';outside.mkdir(exist_ok=True);(outside/'source.png').write_bytes(png(31))
        link=self.root/'assets/hd/authoring/junction'
        command=['cmd','/c','mklink','/J',str(link),str(outside)]
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        try:
            j=self.selected();j['resources'][0].update(source_png='assets/hd/authoring/junction/source.png',source_sha256=b.sha(png(31)))
            with self.assertRaisesRegex(ValueError,'Reparse|Symlink|outside'):b.selection(self.root,b.encoded(j))
            from package_runtime import contained_file
            with self.assertRaisesRegex(ValueError,'Reparse|Symlink|outside'):contained_file(self.root,'assets/hd/authoring/junction/new-output.hda')
            self.assertEqual((outside/'source.png').read_bytes(),png(31));self.assertFalse((outside/'new-output.hda').exists())
        finally:os.rmdir(link)  # Remove the test-owned junction itself, never its target.
        stage=self.stage(self.synthetic())
        original=self.root/'assets/hd/current-compat/sidekick-body'
        held=original.with_name('held-sidekick-body');original.rename(held)
        result=subprocess.run(['cmd','/c','mklink','/J',str(original),str(outside)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        try:
            with self.assertRaisesRegex(ValueError,'Reparse|Symlink|outside'):b.apply(self.root,stage)
            self.assertEqual(sorted(p.name for p in outside.iterdir()),['source.png'])
        finally:
            os.rmdir(original);held.rename(original)
        stage_parent=self.base/'stage-junction'
        result=subprocess.run(['cmd','/c','mklink','/J',str(stage_parent),str(outside)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        try:
            with self.assertRaisesRegex(ValueError,'Reparse|Symlink'):b.stage(self.root,self.root/b.SELECTION,stage_parent/'new-stage')
            self.assertFalse((outside/'new-stage').exists())
        finally:os.rmdir(stage_parent)

    def test_stage_source_plan_and_current_output_tampering_rejected(self):
        for kind in ('staged','plan','source','current'):
            self.setUp();j=self.synthetic();stage=self.stage(j)
            p=stage/'files'/b.HEADER
            if kind=='staged':p.write_bytes(p.read_bytes()+b'bad')
            if kind=='plan':
                p=stage/'plan.json';x=json.loads(p.read_text());x['files'][0]['after_sha256']='0'*64;p.write_bytes(b.encoded(x))
            if kind=='source':(self.root/j['resources'][0]['source_png']).write_bytes(png(98))
            if kind=='current':
                p=self.root/b.HEADER;p.write_bytes(p.read_bytes()+b'bad')
            with self.subTest(kind=kind):self.nonmutating_failure(lambda:b.apply(self.root,stage))

    def test_old_plan_and_temporary_collision_rejected(self):
        j=self.synthetic();stage=self.stage(j);other=self.selected();other['version']='new-current';b.apply(self.root,self.stage(other))
        self.nonmutating_failure(lambda:b.apply(self.root,stage))
        stage=self.stage(j);p=self.root/(b.HEADER+'.sidekick-body-tmp');p.write_bytes(b'occupied')
        self.nonmutating_failure(lambda:b.apply(self.root,stage))

    def test_bad_compatibility_headers_lengths_mapping_and_pins(self):
        mapping=json.loads((self.root/b.MAPPING).read_text());row=mapping['files'][0];p=self.root/row['source_path'];approved=p.read_bytes()
        for offset,value in ((4,1290152),(8,4),(12,13),(16,15),(20,1),(24,1)):
            raw=bytearray(approved);struct.pack_into('<I',raw,offset,value);p.write_bytes(raw);row['sha256']=b.sha(raw);(self.root/b.MAPPING).write_bytes(b.encoded(mapping))
            with self.subTest(offset=offset),self.assertRaises(ValueError):compat.load(self.root)
        for raw in (approved[:-1],approved+b'X',b'BAD!'+approved[4:]):
            p.write_bytes(raw);row['sha256']=b.sha(raw);(self.root/b.MAPPING).write_bytes(b.encoded(mapping))
            with self.assertRaises(ValueError):compat.load(self.root)
        self.setUp();p=self.root/b.HEADER;p.write_bytes(p.read_bytes()+b'bad')
        with self.assertRaises(ValueError):compat.load(self.root)
        self.setUp();mapping=json.loads((self.root/b.MAPPING).read_text());mapping['files'].append(copy.deepcopy(mapping['files'][0]));(self.root/b.MAPPING).write_bytes(b.encoded(mapping))
        with self.assertRaises(ValueError):compat.load(self.root)

    def test_actual_source_binding_rejects_omitted_new_header_and_other_drift(self):
        receipt=json.loads((self.root/b.BINDING).read_text());self.assertEqual(production.verify(self.root,receipt),252)
        self.assertIn(b.HEADER,receipt['source_sha256']);omitted=copy.deepcopy(receipt);del omitted['source_sha256'][b.HEADER]
        omitted['production_source_manifest_sha256']=production.source_manifest_digest(omitted['source_sha256'])
        with self.assertRaisesRegex(ValueError,'Production source mismatch'):production.verify(self.root,omitted)
        p=self.root/b.HEADER;raw=p.read_bytes();p.write_bytes(raw+b'bad')
        with self.assertRaisesRegex(ValueError,'Production source mismatch'):production.verify(self.root,receipt)
        p.write_bytes(raw);extra=self.root/'src/unexpected.inc';extra.write_bytes(b'bad')
        with self.assertRaisesRegex(ValueError,'Production source mismatch'):production.verify(self.root,receipt)

    def test_missing_consumers_and_missing_staged_file_reject_before_writes(self):
        for name in EXPECTED.values():
            p=self.root/compat.ROOT/name;raw=p.read_bytes();p.unlink()
            try:
                with self.subTest(name=name),self.assertRaises(ValueError):compat.load(self.root)
            finally:p.write_bytes(raw)
        stage=self.stage(self.synthetic());(stage/'files'/b.HEADER).unlink()
        self.nonmutating_failure(lambda:b.apply(self.root,stage))

    def test_mapping_wrong_identity_destination_and_source_rejected(self):
        for field,value in [('identity',1290152),('destination','assets/gameplay/unrelated.hda'),('source_path','../outside.hda')]:
            self.setUp();j=json.loads((self.root/b.MAPPING).read_text());j['files'][0][field]=value;(self.root/b.MAPPING).write_bytes(b.encoded(j))
            with self.subTest(field=field),self.assertRaises(ValueError):compat.load(self.root)

    def test_generated_global_header_remains_exact_lf(self):
        dest=self.base/'global-header.h'
        subprocess.run([sys.executable,str(ROOT/'scripts/build_global_registry_header.py'),'--registry',str(self.root/b.REGISTRY),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
        self.assertEqual(dest.read_bytes(),self.initial['src/global_asset_registry.h'])
        self.assertNotIn(b'\r\n',dest.read_bytes())

if __name__=='__main__':unittest.main()
