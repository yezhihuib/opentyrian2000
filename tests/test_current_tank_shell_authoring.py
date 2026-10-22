#!/usr/bin/env python3
"""Independent two-resource legacy authoring contracts; synthetic PNGs only."""
import copy,json,os,shutil,struct,subprocess,sys,tempfile,unittest,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_current_tank_shell as b
import build_current_art as global_builder
from current_art_policy import PROFILES,profile
from current_tank_shell_compatibility import load
IDS=(1220146,1220147)

def png(value,width=96,height=112):
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    data=(b'\0'+bytes((value,17,31,127))*width)*height
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(data))+chunk(b'IEND',b'')

class CurrentTankShellAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tmp=Path(os.environ.get('TMPDIR',str(ROOT.parent/'tank-authoring-tmp')));tmp.mkdir(parents=True,exist_ok=True)
        if shutil.disk_usage(tmp).free<4*1024**3:raise RuntimeError('4 GiB reserve required')
        cls.temp=tempfile.TemporaryDirectory(prefix='tank-independent-',dir=tmp);cls.base=Path(cls.temp.name);cls.root=cls.base/'repo'
        names=set(b.BUILD_INPUTS)
        for manifest in ('packaging/runtime-assets-v1.json','packaging/runtime-assets-public63a89b3.json'):
            names.update(r['source_path'] for r in json.loads((ROOT/manifest).read_text())['files'])
        for folder in ('src','scripts','packaging','assets/hd/authoring'):
            names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        for family in PROFILES:names.update(r['source_png'] for r in json.loads((ROOT/profile(family)['selection']).read_text())['resources'])
        names.update(r['source_png'] for r in json.loads((ROOT/b.SELECTION).read_text())['resources'])
        import current_hud_recipe
        hud=json.loads((ROOT/'assets/hd/authoring/hud/current.json').read_text());names.update(r['path'] for rows in hud['resources'].values() for r in rows);names.update(r['path'] for r in current_hud_recipe.FIXED_INPUTS.values())
        cls.initial={n:(ROOT/n).read_bytes() for n in names}
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):
        if shutil.disk_usage(self.base).free<4*1024**3:raise RuntimeError('4 GiB reserve required')
        self.root.mkdir();subprocess.run(['git','init','-q',str(self.root)],check=True)
        for n,data in self.initial.items():
            p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        self.count=0
    def tearDown(self):
        for p in self.base.iterdir():
            if p.is_file() or p.is_symlink():p.unlink()
            else:shutil.rmtree(p) # Exclusively test-owned fixtures.
    def selected(self):return json.loads((self.root/b.SELECTION).read_text())
    def synthetic(self,index=0):
        j=self.selected();j['version']='synthetic-v2';row=j['resources'][index];name=f'assets/hd/authoring/test-{index}.png';data=png(23+index)
        (self.root/name).write_bytes(data);row.update(source_png=name,source_sha256=b.sha(data));return j
    def stage(self,j):
        self.count+=1;draft=self.base/f'draft-{self.count}.json';draft.write_bytes(b.encoded(j));stage=self.base/f'stage-{self.count}';b.stage(self.root,draft,stage);return stage
    def snapshot(self):return {p.relative_to(self.root).as_posix():b.sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
    def test_initial_pair_exact_and_global_scope_unchanged(self):
        self.assertEqual(b.check(self.root)['resources'],2)
        registry=json.loads((self.root/b.REGISTRY).read_text());self.assertEqual(len(registry['resources']),120)
        self.assertFalse(set(IDS)&{r['identity'] for r in registry['resources']})
        mapping=load(self.root)
        for row in self.selected()['resources']:
            raw,payload=b.source_blob(self.root,row);i=row['identity'];entry=mapping[f'assets/gameplay/enemy-tank-shell-{i-1220000}-8.hda']
            self.assertEqual(raw,(self.root/entry['source_path']).read_bytes());self.assertEqual(raw[:28],b'HDR1'+struct.pack('<6I',i,8,12,14,0,0))
            self.assertEqual(b.fnv(payload),{1220146:'8a02233c02993d45',1220147:'6786d727d8d42fbf'}[i])
    def test_each_source_propagates_only_to_exact_current_consumers(self):
        original=self.snapshot();old_runtime=json.loads((self.root/b.RUNTIME).read_text())
        for index in range(2):
            j=self.synthetic(index);before=self.snapshot();stage=self.stage(j);self.assertEqual(before,self.snapshot());b.apply(self.root,stage)
            self.assertEqual(b.check(self.root)['status'],'PASS');mapping=load(self.root)
            for row in j['resources']:
                data,payload=b.source_blob(self.root,row);dest=f'assets/gameplay/enemy-tank-shell-{row["identity"]-1220000}-8.hda';entry=mapping[dest]
                self.assertEqual((self.root/entry['source_path']).read_bytes(),data);self.assertIn(b.fnv(payload),(self.root/b.HEADER).read_text())
                runtime=json.loads((self.root/b.RUNTIME).read_text());runtime_row=next(r for r in runtime['files'] if r['destination']==dest);self.assertEqual(runtime_row['sha256'],b.sha(data))
            self.assertEqual((self.root/b.REGISTRY).read_bytes(),self.initial[b.REGISTRY])
            allowed={b.SELECTION,b.MAPPING,b.HEADER,b.BINDING,b.RUNTIME}|{r['source_path'] for r in mapping.values()}
            now=self.snapshot()
            for path,digest in original.items():
                if path not in allowed:self.assertEqual(now[path],digest,path)
            self.assertEqual(len(runtime['files']),1006)
            for r in runtime['files']:
                if r['destination'] not in mapping and r['destination']!='CURRENT-PRODUCTION-VALIDATION.json':self.assertEqual(r,next(x for x in old_runtime['files'] if x['destination']==r['destination']))
    def test_global_and_hud_workflows_remain_composable(self):
        j=self.synthetic();b.apply(self.root,self.stage(j))
        self.assertEqual(global_builder.check(self.root,'pulse')['status'],'PASS')
        import build_current_hud
        self.assertEqual(build_current_hud.check(self.root)['status'],'PASS')
    def test_selection_authority_rejects_wrong_scope_and_fields(self):
        cases=[];j=self.selected()
        for change in ('duplicate','extra','missing','reordered','global','bool','geometry','schema'):
            x=copy.deepcopy(j)
            if change=='duplicate':x['resources'][1]=copy.deepcopy(x['resources'][0])
            if change=='extra':x['resources'].append(copy.deepcopy(x['resources'][0]))
            if change=='missing':x['resources'].pop()
            if change=='reordered':x['resources'].reverse()
            if change=='global':x['resources'][0]['identity']=1060146
            if change=='bool':x['resources'][0]['identity']=True
            if change=='geometry':x['resources'][0]['anchor']=[1,1]
            if change=='schema':x['schema']='opentyrian-current-pulse-authoring-v1'
            with self.subTest(change=change),self.assertRaises(ValueError):b.selection(self.root,b.encoded(x))
    def test_geometry_and_source_hash_rejected(self):
        j=self.synthetic();row=j['resources'][0];p=self.root/row['source_png'];p.write_bytes(png(23,95,112));row['source_sha256']=b.sha(p.read_bytes())
        with self.assertRaises(ValueError):b.derive(self.root,b.encoded(j))
        j=self.selected();j['resources'][0]['source_sha256']='0'*64
        with self.assertRaises(ValueError):b.selection(self.root,b.encoded(j))
    def test_path_escape_and_symlinks_rejected(self):
        j=self.selected();row=j['resources'][0];raw=(self.root/row['source_png']).read_bytes();outside=self.base/'outside.png';outside.write_bytes(raw)
        for path in ('../outside.png',str(outside)):
            row['source_png']=path
            with self.subTest(path=path),self.assertRaises(ValueError):b.selection(self.root,b.encoded(j))
        link=self.root/'assets/hd/authoring/link.png';link.symlink_to(outside);row['source_png']=link.relative_to(self.root).as_posix()
        with self.assertRaises(ValueError):b.selection(self.root,b.encoded(j))
        with self.assertRaises(ValueError):b.stage(self.root,self.root/b.SELECTION,self.root/'bad-stage')
    def test_stage_tampering_and_stale_source_are_nonmutating(self):
        j=self.synthetic();stage=self.stage(j);p=stage/'files'/b.HEADER;p.write_bytes(p.read_bytes()+b'bad');before=self.snapshot()
        with self.assertRaises(ValueError):b.apply(self.root,stage)
        self.assertEqual(before,self.snapshot())
        stage=self.stage(j);p=self.root/j['resources'][0]['source_png'];p.write_bytes(png(87));before=self.snapshot()
        with self.assertRaises(ValueError):b.apply(self.root,stage)
        self.assertEqual(before,self.snapshot())
    def test_stale_old_plan_and_collision_are_nonmutating(self):
        j=self.synthetic();stage=self.stage(j);other=self.selected();other['version']='new-current';b.apply(self.root,self.stage(other));before=self.snapshot()
        with self.assertRaises(ValueError):b.apply(self.root,stage)
        self.assertEqual(before,self.snapshot())
        stage=self.stage(j);collision=self.root/(b.HEADER+'.tank-shell-tmp');collision.write_bytes(b'occupied');before=self.snapshot()
        with self.assertRaises(ValueError):b.apply(self.root,stage)
        self.assertEqual(before,self.snapshot())
    def test_corrupt_missing_and_extra_mapping_rejected(self):
        path=self.root/b.MAPPING;original=path.read_bytes();j=json.loads(original);j['files'].append(copy.deepcopy(j['files'][0]));path.write_bytes(b.encoded(j))
        with self.assertRaises(ValueError):load(self.root)
        path.write_bytes(original);p=self.root/j['files'][0]['source_path'];original=p.read_bytes();p.write_bytes(original[:-1])
        with self.assertRaises(ValueError):load(self.root)
        p.unlink()
        with self.assertRaises(ValueError):load(self.root)
    def test_unrelated_source_and_header_changes_rejected(self):
        p=self.root/'src/render_mirror.c';p.write_bytes(p.read_bytes()+b'\n/* drift */\n')
        with self.assertRaises(ValueError):b.derive(self.root,b.encoded(self.selected()))
        p.write_bytes(self.initial['src/render_mirror.c']);p=self.root/b.LEGACY_HEADER;p.write_bytes(p.read_bytes()+b'bad')
        with self.assertRaises(ValueError):b.derive(self.root,b.encoded(self.selected()))

if __name__=='__main__':unittest.main()
