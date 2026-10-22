#!/usr/bin/env python3
"""Independent Green11 authoring contracts; synthetic pixels are diagnostic only."""
import copy
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_current_art as b
from current_art_policy import PROFILES, profile

IDS = (80214,80215,80216,80217,1060078,1060079,1060080,1060081,1060082,1060083,1060084)
HEADS = (80214,80215,80216,80217)
NAMES = ('bullet-214-8.hda','bullet-215-8.hda','bullet-216-8.hda','bullet-217-8.hda',
         'explosion-newsh6-78-8.hda','explosion-newsh6-79-8.hda','explosion-newsh6-80-8.hda',
         'explosion-newsh6-81-8.hda','explosion-newsh6-82-8.hda','explosion-newsh6-83-8.hda',
         'explosion-newsh6-84-8.hda')
APPROVED_HEADS = ('a1bc11025ec02c94','71db2412311dc9af','62a2f5619503960f','4c366cbc9efc7cef')
SOURCE_PINS = ((214,182,'17da292b54af394c'),(215,183,'46b4c47c5e741b0f'),
               (216,184,'cb04c4fc86a8cbb7'),(217,185,'fab1a11e30972f37'))


def png(value, width=96, height=112):
    def chunk(kind, data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    rows = (b'\0'+bytes((value,0,0,255))*width)*height
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))
            +chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b''))


def fnv(raw):
    result = 14695981039346656037
    for value in raw:
        result = ((result ^ value)*1099511628211)&((1<<64)-1)
    return f'{result:016x}'


class CurrentGreenAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp_root = Path(os.environ.get('TMPDIR',str(ROOT.parent/'green-authoring-tmp')))
        temp_root.mkdir(parents=True,exist_ok=True)
        if shutil.disk_usage(temp_root).free < 4*1024**3:
            raise RuntimeError('Green authoring tests require the 4 GiB free-space reserve')
        cls.temp = tempfile.TemporaryDirectory(prefix='green-independent-',dir=temp_root)
        cls.base = Path(cls.temp.name)
        cls.root = cls.base/'repo'
        names = set(b.BUILD_INPUTS)
        for manifest in ('packaging/runtime-assets-v1.json','packaging/runtime-assets-public63a89b3.json'):
            names.update(r['source_path'] for r in json.loads((ROOT/manifest).read_text())['files'])
        for folder in ('src','scripts','packaging','assets/hd/authoring'):
            names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*')
                         if p.is_file() and '__pycache__' not in p.parts)
        for family in PROFILES:
            names.update(r['source_png'] for r in json.loads((ROOT/profile(family)['selection']).read_text())['resources'])
        import current_hud_recipe
        hud = json.loads((ROOT/'assets/hd/authoring/hud/current.json').read_text())
        names.update(r['path'] for rows in hud['resources'].values() for r in rows)
        names.update(r['path'] for r in current_hud_recipe.FIXED_INPUTS.values())
        cls.initial = {name:(ROOT/name).read_bytes() for name in names}
        cls.counter = 0

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        # Only this test-owned sandbox is reset; never the live checkout.
        if self.root.exists(): shutil.rmtree(self.root)
        self.root.mkdir()
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        for name,data in self.initial.items():
            p = self.root/name
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(data)
        self.__class__.counter += 1
        self.sequence = 0

    def selected(self):
        return json.loads((self.root/profile('green')['selection']).read_text())

    def registry(self):
        return json.loads((self.root/b.REGISTRY).read_text())

    def snapshot(self):
        return {p.relative_to(self.root).as_posix():b.sha(p.read_bytes())
                for p in self.root.rglob('*') if p.is_file()}

    def synthetic(self, ids=IDS, same=False):
        selected = self.selected()
        selected['version'] = 'independent-green-v2'
        for index,row in enumerate(selected['resources']):
            if row['identity'] not in ids: continue
            name = f'assets/hd/authoring/independent-fixtures/green-{index}.png'
            raw = png(91 if same else 10+index)
            p = self.root/name
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(raw)
            row.update(source_png=name,source_sha256=b.sha(raw))
        return selected

    def stage(self, selected):
        self.sequence += 1
        draft = self.base/f'draft-{self.counter}-{self.sequence}.json'
        draft.write_bytes(b.encoded(selected))
        stage = self.base/f'stage-{self.counter}-{self.sequence}'
        b.stage(self.root,draft,stage,'green')
        return stage

    def apply(self, selected):
        b.apply(self.root,self.stage(selected),'green')

    def assert_current(self):
        for family in PROFILES:
            with self.subTest(family=family): self.assertEqual(b.check(self.root,family)['status'],'PASS')
        import build_current_hud
        self.assertEqual(build_current_hud.check(self.root)['status'],'PASS')

    def assert_propagated(self, ids):
        resources = {r['identity']:r for r in self.registry()['resources']}
        mapping = json.loads((self.root/profile('green')['mapping']).read_text())
        self.assertEqual(tuple(r['identity'] for r in mapping['files']),IDS)
        runtime = json.loads((self.root/b.RUNTIME).read_text())['files']
        header = (self.root/b.LEGACY_HEADER).read_text()
        for index,(identity,name) in enumerate(zip(IDS,NAMES)):
            resource = resources[identity]
            data = (self.root/'assets/hd/global-assets-v1'/resource['path']).read_bytes()
            if identity in ids:
                expected = b'HDR1'+struct.pack('<6I',identity,8,12,14,0,0)+bytes((10+index,0,0,255))*(96*112)
                self.assertEqual(data,expected)
            self.assertEqual(resource['payload_fnv64'],fnv(data[28:]))
            consumer = mapping['files'][index]
            self.assertEqual(consumer['source_path'],f'assets/hd/current-compat/green/{name}')
            self.assertEqual(consumer['destination'],f'assets/gameplay/{name}')
            self.assertEqual((self.root/consumer['source_path']).read_bytes(),data)
            for destination in (consumer['destination'],'assets/global/'+resource['path']):
                rows = [r for r in runtime if r['destination']==destination]
                self.assertEqual(len(rows),1)
                self.assertEqual(rows[0]['sha256'],b.sha(data))
                if destination==consumer['destination']: self.assertEqual(rows[0]['source_path'],consumer['source_path'])
            self.assertIn(resource['payload_fnv64'],(self.root/b.HEADER).read_text())
            if identity in HEADS:
                self.assertIn(f'#define CURRENT_GREEN_{identity}_RGBA UINT64_C(0x{fnv(data[28:])})',header)
        self.assertEqual(set(re.findall(r'#define CURRENT_GREEN_(\d+)_RGBA',header)),set(map(str,HEADS)))

    def test_exact_approved_scope_initial_macros_and_current_checks(self):
        self.assertEqual(PROFILES['green']['ids'],IDS)
        selected = self.selected()
        self.assertEqual(tuple(r['identity'] for r in selected['resources']),IDS)
        resources = {r['identity']:r for r in self.registry()['resources']}
        for row in selected['resources']:
            data,payload = b.source_blob(self.root,row)
            self.assertEqual(data,(self.root/'assets/hd/global-assets-v1'/resources[row['identity']]['path']).read_bytes())
            self.assertEqual(struct.unpack('<6I',data[4:28]),(row['identity'],8,12,14,0,0))
        for identity,expected in zip(HEADS,APPROVED_HEADS):
            self.assertEqual(resources[identity]['payload_fnv64'],expected)
        source = (self.root/'src/render_mirror.c').read_text()
        for index,slot,source_hash in SOURCE_PINS:
            self.assertIn(f'{{{index},{slot},UINT64_C(0x{source_hash}),CURRENT_GREEN_{80000+index}_RGBA,0,0}}',source)
        self.assert_propagated(())
        self.assert_current()

    def test_all_eleven_propagate_preserving_authority_history_and_other_profiles(self):
        before = self.registry()
        self.apply(self.synthetic())
        after = self.registry()
        self.assertEqual(before['families'],after['families'])
        self.assertEqual([r for r in before['resources'] if r['identity'] not in IDS],
                         [r for r in after['resources'] if r['identity'] not in IDS])
        self.assert_propagated(IDS)
        self.assert_current()
        for name,data in self.initial.items():
            if name.startswith(('assets/hd/packs/','assets/hd/artwork/')) or name=='packaging/runtime-assets-public63a89b3.json':
                self.assertEqual((self.root/name).read_bytes(),data)
        self.assertEqual((self.root/'src/render_mirror.c').read_bytes(),self.initial['src/render_mirror.c'])

    def test_head_only_then_trail_only_change_exact_selected_identity(self):
        before = self.registry()
        self.apply(self.synthetic(ids=(80214,)))
        middle = self.registry()
        self.assertEqual([r for r in before['resources'] if r['identity']!=80214],
                         [r for r in middle['resources'] if r['identity']!=80214])
        self.assert_propagated((80214,))
        head_header = (self.root/b.LEGACY_HEADER).read_bytes()
        self.apply(self.synthetic(ids=(1060084,)))
        after = self.registry()
        self.assertEqual([r for r in middle['resources'] if r['identity']!=1060084],
                         [r for r in after['resources'] if r['identity']!=1060084])
        self.assertEqual((self.root/b.LEGACY_HEADER).read_bytes(),head_header)
        self.assert_propagated((80214,1060084))
        self.assert_current()

    def test_equal_pixels_preserve_eleven_semantic_identities(self):
        self.apply(self.synthetic(same=True))
        rows = [r for r in self.registry()['resources'] if r['identity'] in IDS]
        self.assertEqual(len({r['payload_fnv64'] for r in rows}),1)
        self.assertEqual(len({r['path'] for r in rows}),11)
        self.assertEqual(len({r['sha256'] for r in rows}),11)
        for r in rows:
            raw = (self.root/'assets/hd/global-assets-v1'/r['path']).read_bytes()
            self.assertEqual(struct.unpack('<6I',raw[4:28]),(r['identity'],8,12,14,0,0))
        self.assert_current()

    def test_scope_mutations_and_wrong_roles_rejected(self):
        for kind in ('missing','reordered','duplicate','bool','extra',80213,80218,1060077,1060085,80078,1060214):
            selected = self.selected()
            rows = selected['resources']
            if kind=='missing': rows.pop()
            elif kind=='reordered': rows[0],rows[4]=rows[4],rows[0]
            elif kind=='duplicate': rows[0]['identity']=rows[1]['identity']
            elif kind=='bool': rows[0]['identity']=True
            elif kind=='extra': rows.append(copy.deepcopy(rows[-1]))
            else: rows[0]['identity']=kind
            with self.subTest(kind=kind),self.assertRaises(ValueError): b.derive(self.root,b.encoded(selected),'green')

    def test_authority_and_cross_family_provenance_rejected(self):
        for kind in ('geometry','source','role','provenance','gameplay'):
            registry = self.registry()
            family = next(f for f in registry['families'] if f['name']=='green-energy-head-and-trail')
            if kind=='geometry': next(r for r in registry['resources'] if r['identity']==80214)['header_u32'][4]=1
            elif kind=='source': family['source_identity']['head_source']['logical_bank']=6
            elif kind=='role': family['draw_semantics']['head_contract']['origin']='other'
            elif kind=='provenance': next(r for r in registry['resources'] if r['identity']==80067)['provenance']={'invented':'not-approved'}
            else: (self.root/'src/render_mirror.c').write_bytes(self.initial['src/render_mirror.c']+b'\n/* unrelated */\n')
            (self.root/b.REGISTRY).write_bytes(b.encoded(registry))
            with self.subTest(kind=kind),self.assertRaises(ValueError): b.derive(self.root,b.encoded(self.selected()),'green')
            (self.root/b.REGISTRY).write_bytes(self.initial[b.REGISTRY])
            (self.root/'src/render_mirror.c').write_bytes(self.initial['src/render_mirror.c'])

    def test_bad_source_hash_path_geometry_and_symlink_rejected(self):
        for key,value in (('source_sha256','0'*64),('source_png','../outside.png')):
            selected = self.selected()
            selected['resources'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError): b.derive(self.root,b.encoded(selected),'green')
        selected = self.synthetic(ids=(80214,))
        row = selected['resources'][0]
        path = self.root/row['source_png']
        raw = png(80,width=95)
        path.write_bytes(raw)
        row['source_sha256']=b.sha(raw)
        with self.assertRaises(ValueError): b.derive(self.root,b.encoded(selected),'green')
        target = self.base/f'outside-{self.counter}.png'
        target.write_bytes(raw)
        path.unlink()
        path.symlink_to(target)
        with self.assertRaises(ValueError): b.derive(self.root,b.encoded(selected),'green')

    def test_stage_path_and_plan_injection_rejected(self):
        with self.assertRaises(ValueError): b.stage(self.root,self.root/profile('green')['selection'],self.root/'forbidden','green')
        link = self.base/f'link-{self.counter}'
        link.symlink_to(self.base,target_is_directory=True)
        with self.assertRaises(ValueError): b.stage(self.root,self.root/profile('green')['selection'],link/'stage','green')
        stage = self.stage(self.synthetic())
        before = self.snapshot()
        with self.assertRaises(ValueError): b.apply(self.root,link/stage.name,'green')
        p = stage/'plan.json'
        plan = json.loads(p.read_text())
        plan['files'].append(dict(path='../../escape',before_sha256=None,after_sha256='0'*64,bytes=0))
        p.write_bytes(b.encoded(plan))
        with self.assertRaises(ValueError): b.apply(self.root,stage,'green')
        self.assertEqual(self.snapshot(),before)

    def test_stage_tampering_stale_source_destination_and_late_collision_no_partial_writes(self):
        selected = self.synthetic()
        before = self.snapshot()
        stage = self.stage(selected)
        self.assertEqual(self.snapshot(),before)
        with self.assertRaises(ValueError): b.apply(self.root,stage,'hitflare')
        mapping = stage/'files'/profile('green')['mapping']
        saved = mapping.read_bytes()
        mapping.write_bytes(saved+b' ')
        with self.assertRaises(ValueError): b.apply(self.root,stage,'green')
        self.assertEqual(self.snapshot(),before)
        mapping.write_bytes(saved)
        source = self.root/selected['resources'][0]['source_png']
        saved_source = source.read_bytes()
        source.write_bytes(png(99))
        stale = self.snapshot()
        with self.assertRaises(ValueError): b.apply(self.root,stage,'green')
        self.assertEqual(self.snapshot(),stale)
        source.write_bytes(saved_source)
        destination = self.root/profile('green')['mapping']
        old_destination = destination.read_bytes()
        destination.write_bytes(old_destination+b' ')
        stale = self.snapshot()
        with self.assertRaises(ValueError): b.apply(self.root,stage,'green')
        self.assertEqual(self.snapshot(),stale)
        destination.write_bytes(old_destination)
        plan = json.loads((stage/'plan.json').read_text())
        collision = self.root/(plan['files'][-1]['path']+'.pulse-tmp')
        collision.parent.mkdir(parents=True,exist_ok=True)
        collision.write_bytes(b'occupied')
        occupied = self.snapshot()
        with self.assertRaises(ValueError): b.apply(self.root,stage,'green')
        self.assertEqual(self.snapshot(),occupied)

    def test_version_only_change_and_cross_profile_hud_drift_detection(self):
        selected = self.synthetic()
        self.apply(selected)
        before = self.registry()
        selected['version']='green-version-only-v3'
        self.apply(selected)
        after = self.registry()
        for old,new in zip(before['resources'],after['resources']):
            for key in ('identity','path','sha256','payload_fnv64','header_u32'): self.assertEqual(old[key],new[key])
        self.assert_current()
        selected['version']='unapplied-drift'
        (self.root/profile('green')['selection']).write_bytes(b.encoded(selected))
        for family in PROFILES:
            with self.subTest(family=family),self.assertRaises(ValueError): b.check(self.root,family)
        import build_current_hud
        with self.assertRaises(ValueError): build_current_hud.check(self.root)

    def test_corrupt_or_missing_consumer_and_macro_drift_detected(self):
        for name in ('assets/hd/current-compat/green/bullet-214-8.hda',
                     'assets/hd/current-compat/green/explosion-newsh6-84-8.hda',b.LEGACY_HEADER):
            path = self.root/name
            original = path.read_bytes()
            path.write_bytes(original+b'drift')
            with self.subTest(name=name),self.assertRaises(ValueError): b.check(self.root,'green')
            path.write_bytes(original)
        path = self.root/'assets/hd/current-compat/green/bullet-214-8.hda'
        path.unlink()
        with self.assertRaises((ValueError,FileNotFoundError)): b.check(self.root,'green')


if __name__=='__main__':
    unittest.main()
