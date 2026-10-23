#!/usr/bin/env python3
"""Independent 21-identity large-sprite contracts; synthetic art is test-only."""
import copy
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import build_current_art as b
from current_art_policy import PROFILES, profile

# Independent semantic ordering, filenames, and geometry: never inferred from policy.
TALON = (90229,1090001,90231,1090003,1090004,1090005,90233,1090007,1090008,1090009,90235,1090011,90237)
ROTOR = (1010229,1010231,1010233,1010235,1010237,1010239,1010241,1010243)
IDS = {'talon': TALON, 'rotor': ROTOR}
NAMES = {'talon': ('ship-229-8.hda','talon-bank-1-8.hda','ship-231-8.hda','talon-bank-3-8.hda','talon-bank-4-8.hda','talon-bank-5-8.hda','ship-233-8.hda','talon-bank-7-8.hda','talon-bank-8-8.hda','talon-bank-9-8.hda','ship-235-8.hda','talon-bank-11-8.hda','ship-237-8.hda'),
         'rotor': tuple(f'enemy-newsh2-{i}-8.hda' for i in (229,231,233,235,237,239,241,243))}
ANCHORS = {'talon': (5,7), 'rotor': (6,7)}
ALL = TALON+ROTOR


def sha(raw): return hashlib.sha256(raw).hexdigest()


def png(value, width=192, height=224):
    def chunk(kind, data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    rows = (b'\0'+bytes((value,17,31,255))*width)*height
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')


def fnv(raw):
    value=14695981039346656037
    for byte in raw: value=((value^byte)*1099511628211)&((1<<64)-1)
    return f'{value:016x}'


class CurrentLargeSpriteAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp_root=Path(os.environ.get('TMPDIR',str(ROOT.parent/'large-sprite-authoring-tmp')))
        temp_root.mkdir(parents=True,exist_ok=True)
        if shutil.disk_usage(temp_root).free < 4*1024**3:
            raise RuntimeError('Large-sprite tests require a 4 GiB free-space reserve')
        cls.temp=tempfile.TemporaryDirectory(prefix='large-independent-',dir=temp_root)
        cls.base=Path(cls.temp.name); cls.root=cls.base/'repo'; cls.counter=0
        names=set(b.BUILD_INPUTS)
        from current_sidekick_body_compatibility import charge_input_paths
        names.update(charge_input_paths(ROOT))
        for manifest in ('packaging/runtime-assets-v1.json','packaging/runtime-assets-public63a89b3.json'):
            names.update(r['source_path'] for r in json.loads((ROOT/manifest).read_text())['files'])
        for folder in ('src','scripts','packaging','assets/hd/authoring'):
            names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        for family in PROFILES:
            names.update(r['source_png'] for r in json.loads((ROOT/profile(family)['selection']).read_text())['resources'])
        import current_hud_recipe
        hud=json.loads((ROOT/'assets/hd/authoring/hud/current.json').read_text())
        names.update(r['path'] for rows in hud['resources'].values() for r in rows)
        names.update(r['path'] for r in current_hud_recipe.FIXED_INPUTS.values())
        cls.initial={name:(ROOT/name).read_bytes() for name in names}

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def setUp(self):
        if shutil.disk_usage(self.base).free < 4*1024**3: raise RuntimeError('4 GiB reserve exhausted')
        if self.root.exists(): shutil.rmtree(self.root)  # Only this test-owned sandbox.
        self.root.mkdir(); subprocess.run(['git','init','-q',str(self.root)],check=True)
        for name,data in self.initial.items():
            p=self.root/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
        type(self).counter+=1; self.sequence=0

    def tearDown(self):
        # All children belong exclusively to this test instance; retain no large
        # sandbox or staged build between cases (other workers share disk space).
        for path in self.base.iterdir():
            if path.is_symlink() or path.is_file(): path.unlink()
            else: shutil.rmtree(path)

    def selected(self,family): return json.loads((self.root/profile(family)['selection']).read_text())
    def registry(self): return json.loads((self.root/b.REGISTRY).read_text())
    def snapshot(self): return {p.relative_to(self.root).as_posix():sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}

    def synthetic(self,family,ids=None,same=False):
        selected=self.selected(family); selected['version']='independent-large-v2'
        for index,row in enumerate(selected['resources']):
            if ids is not None and row['identity'] not in ids: continue
            name=f'assets/hd/authoring/independent-large/{family}-{index}.png'; raw=png(91 if same else 20+index)
            p=self.root/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(raw)
            row.update(source_png=name,source_sha256=sha(raw))
        return selected

    def stage(self,family,selected):
        self.sequence+=1
        draft=self.base/f'draft-{self.counter}-{self.sequence}.json'; draft.write_bytes(b.encoded(selected))
        stage=self.base/f'stage-{self.counter}-{self.sequence}'; b.stage(self.root,draft,stage,family)
        return stage

    def apply(self,family,selected): b.apply(self.root,self.stage(family,selected),family)

    def assert_current(self):
        for family in PROFILES:
            with self.subTest(family=family): self.assertEqual(b.check(self.root,family)['status'],'PASS')
        import build_current_hud
        self.assertEqual(build_current_hud.check(self.root)['status'],'PASS')

    def assert_propagated(self,family,changed=()):
        resources={r['identity']:r for r in self.registry()['resources']}
        mapping=json.loads((self.root/profile(family)['mapping']).read_text())['files']
        runtime=json.loads((self.root/b.RUNTIME).read_text())['files']
        self.assertEqual(tuple(r['identity'] for r in mapping),IDS[family])
        for index,(identity,name) in enumerate(zip(IDS[family],NAMES[family])):
            r=resources[identity]; raw=(self.root/'assets/hd/global-assets-v1'/r['path']).read_bytes()
            header=b'HDR1'+struct.pack('<6I',identity,8,24,28,*ANCHORS[family])
            self.assertEqual(raw[:28],header)
            if identity in changed: self.assertEqual(raw,header+bytes((20+index,17,31,255))*(192*224))
            self.assertEqual(r['payload_fnv64'],fnv(raw[28:])); self.assertEqual(r['sha256'],sha(raw))
            row=mapping[index]
            self.assertEqual(row['source_path'],f'assets/hd/current-compat/{family}/{name}')
            self.assertEqual(row['destination'],f'assets/gameplay/{name}')
            self.assertEqual((self.root/row['source_path']).read_bytes(),raw)
            for destination in (row['destination'],'assets/global/'+r['path']):
                selected=[x for x in runtime if x['destination']==destination]
                self.assertEqual(len(selected),1); self.assertEqual(selected[0]['sha256'],sha(raw))
                if destination==row['destination']: self.assertEqual(selected[0]['source_path'],row['source_path'])
            self.assertIn(r['payload_fnv64'],(self.root/b.HEADER).read_text())
        macros=(self.root/b.LEGACY_HEADER).read_text()
        self.assertNotIn('CURRENT_TALON_',macros); self.assertNotIn('CURRENT_ROTOR_',macros)

    def test_approved_21_exact_geometry_pixels_and_consumer_scope(self):
        for family in IDS:
            self.assertEqual(PROFILES[family]['ids'],IDS[family])
            for row in self.selected(family)['resources']:
                resource=next(r for r in self.registry()['resources'] if r['identity']==row['identity'])
                data,_=b.source_blob(self.root,row)
                self.assertEqual(data,(self.root/'assets/hd/global-assets-v1'/resource['path']).read_bytes())
            self.assert_propagated(family)
        self.assert_current()

    def test_all_21_synthetic_sources_propagate_without_history_or_authority_changes(self):
        before=self.registry()
        for family in IDS:
            self.apply(family,self.synthetic(family)); self.assert_propagated(family,IDS[family])
        after=self.registry()
        self.assertEqual(before['families'],after['families'])
        self.assertEqual([r for r in before['resources'] if r['identity'] not in ALL],[r for r in after['resources'] if r['identity'] not in ALL])
        self.assert_current()
        for name,data in self.initial.items():
            if name.startswith(('assets/hd/packs/','assets/hd/artwork/','assets/hd/source/')) or name in ('packaging/runtime-assets-public63a89b3.json','packaging/frontend-validation.json','packaging/global-validation.json') or (name.startswith('src/') and name!=b.HEADER):
                self.assertEqual((self.root/name).read_bytes(),data,name)

    def test_neutral_talon_and_reverse_rotor_endpoint_change_only_exact_identity(self):
        for family,identity in (('talon',90233),('rotor',1010243)):
            before=self.registry(); self.apply(family,self.synthetic(family,(identity,))); after=self.registry()
            self.assertEqual([r for r in before['resources'] if r['identity']!=identity],[r for r in after['resources'] if r['identity']!=identity])
            self.assert_propagated(family,(identity,))
        shop=(self.root/'src/shop_ship_render.inc').read_text()
        self.assertIn('identity==90233',shop); self.assertIn('player[0].items.ship!=1',shop)
        self.assertEqual((self.root/'src/shop_ship_render.inc').read_bytes(),self.initial['src/shop_ship_render.inc'])

    def test_equal_pixels_do_not_merge_21_semantic_identities(self):
        for family in IDS: self.apply(family,self.synthetic(family,same=True))
        rows=[r for r in self.registry()['resources'] if r['identity'] in ALL]
        self.assertEqual(len(rows),21); self.assertEqual(len({r['payload_fnv64'] for r in rows}),1)
        self.assertEqual(len({r['path'] for r in rows}),21); self.assertEqual(len({r['sha256'] for r in rows}),21)

    def test_scope_order_duplicates_cross_profile_and_selector_geometry_rejected(self):
        for family in IDS:
            for kind in ('missing','reordered','duplicate','extra','cross','bool','anchor','dimensions','density','top_geometry'):
                selected=self.selected(family); rows=selected['resources']
                if kind=='missing': rows.pop()
                elif kind=='reordered': rows[0],rows[1]=rows[1],rows[0]
                elif kind=='duplicate': rows[0]['identity']=rows[1]['identity']
                elif kind=='extra': rows.append(copy.deepcopy(rows[-1]))
                elif kind=='cross': rows[0]['identity']=ROTOR[0] if family=='talon' else TALON[0]
                elif kind=='bool': rows[0]['identity']=True
                elif kind=='top_geometry': selected['geometry']=[8,24,28,0,0]
                else: rows[0][kind]=[0,0] if kind=='anchor' else 8
                with self.subTest(family=family,kind=kind),self.assertRaises(ValueError): b.derive(self.root,b.encoded(selected),family)

    def test_wrong_png_dimensions_hash_path_and_symlink_rejected(self):
        for family in IDS:
            for size in ((96,112),(191,224),(192,223),(224,192)):
                selected=self.synthetic(family,(IDS[family][0],)); row=selected['resources'][0]
                raw=png(88,*size); (self.root/row['source_png']).write_bytes(raw); row['source_sha256']=sha(raw)
                with self.subTest(family=family,size=size),self.assertRaises(ValueError): b.derive(self.root,b.encoded(selected),family)
            for key,value in (('source_sha256','0'*64),('source_png','../outside.png')):
                selected=self.selected(family); selected['resources'][0][key]=value
                with self.assertRaises(ValueError): b.derive(self.root,b.encoded(selected),family)
            selected=self.synthetic(family,(IDS[family][0],)); row=selected['resources'][0]; path=self.root/row['source_png']
            outside=self.base/f'outside-{self.counter}-{family}.png'; outside.write_bytes(path.read_bytes()); path.unlink(); path.symlink_to(outside)
            with self.assertRaises(ValueError): b.derive(self.root,b.encoded(selected),family)

    def test_fixed_registry_geometry_source_role_and_cross_profile_provenance_rejected(self):
        for family in IDS:
            for kind in ('width','density','anchor','family_authority','provenance','gameplay'):
                registry=self.registry(); row=next(r for r in registry['resources'] if r['identity']==IDS[family][0])
                if kind in ('width','density','anchor'): row['header_u32'][{'width':2,'density':1,'anchor':4}[kind]]+=1
                elif kind=='family_authority': registry['families'][0]['draw_semantics']['role']='unrelated'
                elif kind=='provenance': next(r for r in registry['resources'] if r['identity']==80067)['provenance']={'invented':'unauthorized'}
                else: (self.root/'src/render_mirror.c').write_bytes(self.initial['src/render_mirror.c']+b'\n/* drift */\n')
                (self.root/b.REGISTRY).write_bytes(b.encoded(registry))
                with self.subTest(family=family,kind=kind),self.assertRaises(ValueError): b.derive(self.root,b.encoded(self.selected(family)),family)
                (self.root/b.REGISTRY).write_bytes(self.initial[b.REGISTRY]); (self.root/'src/render_mirror.c').write_bytes(self.initial['src/render_mirror.c'])

    def test_stage_tamper_cross_profile_stale_source_destination_and_collision_are_atomic(self):
        family='talon'; selected=self.synthetic(family); before=self.snapshot(); stage=self.stage(family,selected)
        self.assertEqual(self.snapshot(),before)
        with self.assertRaises(ValueError): b.apply(self.root,stage,'rotor')
        mapping=stage/'files'/profile(family)['mapping']; saved=mapping.read_bytes(); mapping.write_bytes(saved+b' ')
        with self.assertRaises(ValueError): b.apply(self.root,stage,family)
        self.assertEqual(self.snapshot(),before); mapping.write_bytes(saved)
        for path,replacement in ((self.root/selected['resources'][0]['source_png'],png(99)),(self.root/profile(family)['mapping'],b'{}')):
            saved=path.read_bytes(); path.write_bytes(replacement); stale=self.snapshot()
            with self.assertRaises(ValueError): b.apply(self.root,stage,family)
            self.assertEqual(self.snapshot(),stale); path.write_bytes(saved)
        plan=json.loads((stage/'plan.json').read_text()); collision=self.root/(plan['files'][-1]['path']+'.pulse-tmp')
        collision.parent.mkdir(parents=True,exist_ok=True); collision.write_bytes(b'occupied'); occupied=self.snapshot()
        with self.assertRaises(ValueError): b.apply(self.root,stage,family)
        self.assertEqual(self.snapshot(),occupied)

    def test_stage_unsafe_path_and_plan_injection_rejected(self):
        family='rotor'
        with self.assertRaises(ValueError): b.stage(self.root,self.root/profile(family)['selection'],self.root/'forbidden',family)
        link=self.base/f'link-{self.counter}'; link.symlink_to(self.base,target_is_directory=True)
        with self.assertRaises(ValueError): b.stage(self.root,self.root/profile(family)['selection'],link/'stage',family)
        stage=self.stage(family,self.synthetic(family)); before=self.snapshot(); p=stage/'plan.json'; plan=json.loads(p.read_text())
        plan['files'].append(dict(path='../../escape',before_sha256=None,after_sha256='0'*64,bytes=0)); p.write_bytes(b.encoded(plan))
        with self.assertRaises(ValueError): b.apply(self.root,stage,family)
        self.assertEqual(self.snapshot(),before)

    def test_corrupt_missing_outputs_and_selected_version_drift_detected(self):
        for family in IDS:
            path=self.root/f'assets/hd/current-compat/{family}/{NAMES[family][0]}'; original=path.read_bytes()
            path.write_bytes(original+b'drift')
            with self.assertRaises(ValueError): b.check(self.root,family)
            path.unlink()
            with self.assertRaises((ValueError,FileNotFoundError)): b.check(self.root,family)
            path.write_bytes(original)
        # Approved provenance has no revision field. Metadata-only drift is
        # detected by its own generated mapping, not unrelated-family authority.
        selected=self.selected('talon'); original=copy.deepcopy(selected)
        selected['version']='unapplied-approved-version'
        (self.root/profile('talon')['selection']).write_bytes(b.encoded(selected))
        with self.assertRaises(ValueError): b.check(self.root,'talon')
        (self.root/profile('talon')['selection']).write_bytes(b.encoded(original))
        # Generated provenance does bind revision, exactly as Green's contract.
        self.apply('talon',self.synthetic('talon'))
        selected=self.selected('talon'); selected['version']='unapplied-version-drift'; (self.root/profile('talon')['selection']).write_bytes(b.encoded(selected))
        for family in PROFILES:
            with self.subTest(family=family),self.assertRaises(ValueError): b.check(self.root,family)
        import build_current_hud
        with self.assertRaises(ValueError): build_current_hud.check(self.root)


if __name__=='__main__': unittest.main()
