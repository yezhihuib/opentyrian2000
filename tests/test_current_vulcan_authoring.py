#!/usr/bin/env python3
"""Independent single-source tests. Synthetic PNG fixtures never edit approved art."""
import copy, hashlib, importlib, json, shutil, struct, sys, tempfile, unittest, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_current_vulcan as b

def synthetic_png(value):
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    # Synthetic diagnostic pixels, not a transformation of any user's image.
    data=b''.join(b'\0'+bytes([value,0,0,255])*96 for _ in range(112))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',96,112,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(data))+chunk(b'IEND',b'')

class CurrentVulcanAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='vulcan-independent-');cls.base=Path(cls.temp.name);cls.root=cls.base/'repo';cls.root.mkdir()
        names=set()
        from current_sidekick_body_compatibility import charge_input_paths
        names.update(charge_input_paths(ROOT))
        for m in ('packaging/runtime-assets-v1.json','packaging/runtime-assets-public63a89b3.json'):
            names|={r['source_path'] for r in json.loads((ROOT/m).read_text())['files']}
        for folder in ('src','scripts','packaging','assets/hd/authoring'):
            names|={p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        names|=set(b.BUILD_INPUTS)
        for selection_path in (ROOT/'assets/hd/authoring').glob('*-current.json'):
            sel=json.loads(selection_path.read_text());names|={r['source_png'] for r in sel['resources']}
        for n in sorted(names):
            p=cls.root/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,p)
        cls.initial={n:(cls.root/n).read_bytes() for n in names}
        cls.selected=(cls.root/b.SELECT).read_bytes()
        cls.counter=0
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):
        # Restore only sandbox fixture, never the live repository.
        for p in self.root.rglob('*'):
            if p.is_symlink():p.unlink()
        for n,data in self.initial.items():
            p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        for p in self.root.rglob('*.pulse-tmp'):p.unlink()
        self.__class__.counter+=1;self.stagepath=self.base/f'stage-{self.counter}'
    def stage(self,raw=None):
        selection=self.base/f'selection-{self.counter}.json';selection.write_bytes(raw or self.selected)
        return b.stage(self.root,selection,self.stagepath)
    def fixture_selection(self):
        sel=json.loads(self.selected);sel['version']='synthetic-fixture'
        for index,row in enumerate(sel['resources']):
            n=f'assets/hd/authoring/test-fixtures/{row["identity"]}.png';p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);raw=synthetic_png(10+index);p.write_bytes(raw)
            row['source_png']=n;row['source_sha256']=b.sha(raw)
        return json.dumps(sel,indent=2).encode()+b'\n'
    def test_current_check_and_repeat_determinism(self):
        self.assertEqual(b.check(self.root)['status'],'PASS')
        self.assertEqual(b.derive(self.root,self.selected),b.derive(self.root,self.selected))
    def test_stage_does_not_mutate_inputs(self):
        before={n:b.sha((self.root/n).read_bytes()) for n in self.initial};self.stage()
        self.assertEqual(before,{n:b.sha((self.root/n).read_bytes()) for n in self.initial})
    def test_synthetic_version_propagates_all_consumers(self):
        raw=self.fixture_selection();old=json.loads((self.root/b.REGISTRY).read_text());self.stage(raw);b.apply(self.root,self.stagepath);self.assertEqual(b.check(self.root)['status'],'PASS')
        now=json.loads((self.root/b.REGISTRY).read_text());self.assertEqual(now['families'],old['families'])
        self.assertEqual([r for r in old['resources'] if r['identity'] not in b.IDS],[r for r in now['resources'] if r['identity'] not in b.IDS])
        runtime=json.loads((self.root/b.RUNTIME).read_text());compat=json.loads((self.root/b.MAPPING).read_text())
        for r in now['resources']:
            if r['identity'] not in b.IDS:continue
            expected=b'HDR1'+struct.pack('<6I',*r['header_u32'])+bytes([10+b.IDS.index(r['identity']),0,0,255])*(96*112)
            self.assertEqual((self.root/'assets/hd/global-assets-v1'/r['path']).read_bytes(),expected)
            c=next(x for x in compat['files'] if x['identity']==r['identity']);self.assertEqual((self.root/c['source_path']).read_bytes(),expected)
            row=next(x for x in runtime['files'] if x['destination']==c['destination']);self.assertEqual(row['sha256'],r['sha256']);self.assertEqual(row['source_path'],c['source_path'])
            self.assertIn(r['payload_fnv64'],(self.root/b.HEADER).read_text())
        for n in self.initial:
            if n.startswith('assets/hd/artwork/') or n.startswith('assets/hd/packs/') or n=='packaging/runtime-assets-public63a89b3.json':self.assertEqual((self.root/n).read_bytes(),self.initial[n])
    def test_staged_bytes_tamper_rejected(self):
        self.stage();p=self.stagepath/'files'/b.MAPPING;p.write_bytes(p.read_bytes()+b' ')
        with self.assertRaises(ValueError):b.apply(self.root,self.stagepath)
    def test_plan_path_injection_rejected(self):
        self.stage();p=self.stagepath/'plan.json';j=json.loads(p.read_text());j['files'].append(dict(path='../../escape',before_sha256=None,after_sha256='0'*64,bytes=0));p.write_text(json.dumps(j))
        with self.assertRaises(ValueError):b.apply(self.root,self.stagepath)
    def test_stale_destination_rejected_before_write(self):
        self.stage();p=self.root/b.MAPPING;p.write_bytes(p.read_bytes()+b' ');before=(self.root/b.SELECT).read_bytes()
        with self.assertRaises(ValueError):b.apply(self.root,self.stagepath)
        self.assertEqual(before,(self.root/b.SELECT).read_bytes())
    def test_missing_consumer_detected(self):
        (self.root/f'{b.COMPAT}/bullet-67-8.hda').unlink()
        with self.assertRaises((ValueError,FileNotFoundError)):b.check(self.root)
    def test_corrupt_consumer_detected(self):
        p=self.root/f'{b.COMPAT}/bullet-67-8.hda';raw=bytearray(p.read_bytes());raw[-1]^=1;p.write_bytes(raw)
        with self.assertRaises(ValueError):b.check(self.root)
    def test_duplicate_identity_rejected(self):
        s=json.loads(self.selected);s['resources'][1]=copy.deepcopy(s['resources'][0])
        with self.assertRaises(ValueError):b.derive(self.root,json.dumps(s).encode())
    def test_bool_identity_rejected(self):
        s=json.loads(self.selected);s['resources'][0]['identity']=True
        with self.assertRaises(ValueError):b.derive(self.root,json.dumps(s).encode())
    def test_source_symlink_rejected(self):
        s=json.loads(self.selected);r=s['resources'][0];p=self.root/r['source_png'];original=p.read_bytes();p.unlink();target=self.base/'symlink-target.png';target.write_bytes(original);p.symlink_to(target)
        with self.assertRaises(ValueError):b.derive(self.root,self.selected)
    def test_source_path_traversal_rejected(self):
        s=json.loads(self.selected);s['resources'][0]['source_png']='../outside.png'
        with self.assertRaises(ValueError):b.derive(self.root,json.dumps(s).encode())
    def test_source_hash_change_rejected(self):
        s=json.loads(self.selected);s['resources'][0]['source_sha256']='0'*64
        with self.assertRaises(ValueError):b.derive(self.root,json.dumps(s).encode())
    def test_wrong_image_geometry_rejected(self):
        s=json.loads(self.selected);p=self.root/'bad.png';p.write_bytes(b'not png');s['resources'][0].update(source_png='bad.png',source_sha256=b.sha(p.read_bytes()))
        with self.assertRaises(Exception):b.derive(self.root,json.dumps(s).encode())
    def test_unrelated_gameplay_mutation_rejected(self):
        p=self.root/'src/tyrian2.c';p.write_bytes(p.read_bytes()+b'\n/* accidental edit */\n')
        with self.assertRaises(ValueError):b.derive(self.root,self.selected)
    def test_source_authority_mutation_rejected(self):
        p=self.root/b.REGISTRY;j=json.loads(p.read_text());j['families'][2]['source_identity']['bank_bytes']+=1;p.write_text(json.dumps(j,indent=2)+'\n')
        with self.assertRaises(ValueError):b.derive(self.root,self.selected)
    def test_stage_inside_repository_rejected(self):
        with self.assertRaises(ValueError):b.stage(self.root,self.root/b.SELECT,self.root/'assets/hd/artwork/forbidden-stage')
    def test_stage_parent_symlink_rejected(self):
        target=self.base/f'realstage-{self.counter}';target.mkdir();link=self.base/f'linkstage-{self.counter}';link.symlink_to(target,target_is_directory=True)
        with self.assertRaises(ValueError):b.stage(self.root,self.root/b.SELECT,link/'new')
    def test_late_temp_collision_no_partial_writes(self):
        raw=self.fixture_selection();self.stage(raw);plan=json.loads((self.stagepath/'plan.json').read_text());last=plan['files'][-1]['path'];p=self.root/(last+'.pulse-tmp');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'occupied')
        before={n:(self.root/n).read_bytes() for n in self.initial}
        with self.assertRaises(ValueError):b.apply(self.root,self.stagepath)
        self.assertEqual(before,{n:(self.root/n).read_bytes() for n in self.initial})
    def test_unrelated_registry_resource_rejected(self):
        p=self.root/b.REGISTRY;j=json.loads(p.read_text());r=next(r for r in j['resources'] if r['identity'] not in b.IDS);r['sha256']='0'*64;p.write_text(json.dumps(j))
        with self.assertRaises(ValueError):b.derive(self.root,self.selected)
    def test_vulcan_geometry_mutation_rejected(self):
        p=self.root/b.REGISTRY;j=json.loads(p.read_text());r=next(r for r in j['resources'] if r['identity'] in b.IDS);r['header_u32'][2]+=1;p.write_text(json.dumps(j))
        with self.assertRaises(ValueError):b.derive(self.root,self.selected)
    def test_build_input_mutation_rejected(self):
        p=self.root/next(iter(b.BUILD_INPUTS));p.write_bytes(p.read_bytes()+b'\n')
        with self.assertRaises(ValueError):b.derive(self.root,self.selected)
    def test_apply_stage_parent_symlink_rejected(self):
        self.stage();link=self.base/f'apply-link-{self.counter}';link.symlink_to(self.base,target_is_directory=True)
        with self.assertRaises(ValueError):b.apply(self.root,link/self.stagepath.name)
    def test_selected_source_stale_after_stage_rejected(self):
        raw=self.fixture_selection();self.stage(raw);s=json.loads(raw);p=self.root/s['resources'][0]['source_png'];p.write_bytes(synthetic_png(77))
        with self.assertRaises(ValueError):b.apply(self.root,self.stagepath)
    def test_non_source_temp_collision_no_partial_writes(self):
        raw=self.fixture_selection();self.stage(raw);(self.root/(b.RUNTIME+'.pulse-tmp')).write_bytes(b'occupied')
        before={n:(self.root/n).read_bytes() for n in self.initial}
        with self.assertRaises(ValueError):b.apply(self.root,self.stagepath)
        self.assertEqual(before,{n:(self.root/n).read_bytes() for n in self.initial})
    def test_synthetic_version_updates_legacy_payload_pins(self):
        self.stage(self.fixture_selection());b.apply(self.root,self.stagepath)
        registry=json.loads((self.root/b.REGISTRY).read_text())
        header=(self.root/b.LEGACY_HEADER).read_text()
        for row in registry['resources']:
            if row['identity'] in b.IDS:self.assertIn('CURRENT_VULCAN_%s_RGBA UINT64_C(0x%s)' % (row['identity']-80000,row['payload_fnv64']),header)
        # Shared generation must leave the independent Pulse family current too.
        import build_current_pulse
        self.assertEqual(build_current_pulse.check(self.root)['status'],'PASS')
    def test_pulse_then_vulcan_remain_independent(self):
        import build_current_pulse as pulse
        selected=json.loads((self.root/pulse.SELECT).read_text());selected['version']='synthetic-pulse-cross-family'
        for index,row in enumerate(selected['resources']):
            p=self.root/f'assets/hd/authoring/test-fixtures/pulse-{index}.png';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(synthetic_png(40+index));row.update(source_png=p.relative_to(self.root).as_posix(),source_sha256=b.sha(p.read_bytes()))
        selection=self.base/f'pulse-selection-{self.counter}.json';selection.write_text(json.dumps(selected))
        pulse.stage(self.root,selection,self.stagepath);pulse.apply(self.root,self.stagepath)
        self.assertEqual(b.check(self.root)['status'],'PASS')
        self.stagepath=self.base/f'vulcan-after-pulse-{self.counter}';self.stage(self.fixture_selection());b.apply(self.root,self.stagepath)
        self.assertEqual(pulse.check(self.root)['status'],'PASS');self.assertEqual(b.check(self.root)['status'],'PASS')
    def test_version_only_after_generated_art_stays_consistent(self):
        raw=self.fixture_selection();self.stage(raw);b.apply(self.root,self.stagepath)
        selected=json.loads(raw);selected['version']='synthetic-renamed-version'
        self.stagepath=self.base/f'version-only-{self.counter}';self.stage(json.dumps(selected).encode());b.apply(self.root,self.stagepath)
        import build_current_pulse
        self.assertEqual(build_current_pulse.check(self.root)['status'],'PASS')
        self.assertEqual(b.check(self.root)['status'],'PASS')
    def test_active_family_provenance_tamper_rejected(self):
        p=self.root/b.REGISTRY;j=json.loads(p.read_text())
        next(r for r in j['resources'] if r['identity']==80067)['provenance']['invented']='untrusted'
        p.write_text(json.dumps(j))
        with self.assertRaises(ValueError):b.derive(self.root,self.selected)
    def test_other_family_provenance_tamper_rejected(self):
        p=self.root/b.REGISTRY;j=json.loads(p.read_text())
        next(r for r in j['resources'] if r['identity']==80058)['provenance']={'invented':'untrusted'}
        p.write_text(json.dumps(j))
        with self.assertRaises(ValueError):b.derive(self.root,self.selected)
    def test_legacy_header_tamper_detected(self):
        p=self.root/b.LEGACY_HEADER;p.write_bytes(p.read_bytes()+b'/* drift */')
        with self.assertRaises(ValueError):b.check(self.root)
if __name__=='__main__':unittest.main()
