#!/usr/bin/env python3
"""Independent HUD authoring tests using diagnostic pixels, never edited artwork."""
import copy
import hashlib
import json
import shutil
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_current_hud as b
import current_hud_recipe as recipe
from current_art_policy import PROFILES,profile

EXPECTED=('gameplay-hud-v1.hda','gameplay-hud-meters-v2.hda','gameplay-hud-font-v1.hda',
          'gameplay-hud-components-v1.hda','gameplay-hud-indicators-v1.hda','gameplay-hud-fixed-text-v1.hda')

def png(w,h,pixel):
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    raw=(b'\0'+bytes(pixel)*w)*h
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')

class CurrentHudAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='hud-independent-')
        cls.base=Path(cls.temp.name);cls.root=cls.base/'repo'
        names=set(b.BUILD_INPUTS)
        for name in ('packaging/runtime-assets-v1.json','packaging/runtime-assets-public63a89b3.json'):
            names.update(r['source_path'] for r in json.loads((ROOT/name).read_text())['files'])
        for folder in ('src','scripts','packaging','assets/hd/authoring'):
            names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        for family in PROFILES:
            names.update(r['source_png'] for r in json.loads((ROOT/profile(family)['selection']).read_text())['resources'])
        selected=json.loads((ROOT/b.SELECTION).read_text())
        names.update(r['path'] for rows in selected['resources'].values() for r in rows)
        names.update(r['path'] for r in recipe.FIXED_INPUTS.values())
        cls.initial={name:(ROOT/name).read_bytes() for name in names}
        cls.counter=0
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):
        if self.root.exists():shutil.rmtree(self.root)
        for name,data in self.initial.items():
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        self.__class__.counter+=1;self.stagepath=self.base/f'stage-{self.counter}'
        self.selected=json.loads((self.root/b.SELECTION).read_text())
    def snapshot(self):
        return {p.relative_to(self.root).as_posix():b.sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
    def stage(self,selection=None):
        path=self.base/f'selected-{self.counter}.json';path.write_bytes(b.encoded(selection or self.selected))
        return b.stage(self.root,path,self.stagepath)
    def synthetic(self):
        selected=copy.deepcopy(self.selected);selected['version']='independent-diagnostic-v2'
        name='assets/hd/authoring/fixtures/front-diagnostic.png'
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(png(96,20,(23,41,89,255)))
        selected['resources']['components'][0]={'path':name,'sha256':b.sha(p.read_bytes())}
        name='assets/hd/authoring/fixtures/meter-diagnostic.json';p=self.root/name
        rgb=json.loads((self.root/selected['resources']['meters'][0]['path']).read_text());rgb['firepower']['116']=[123,5,1]
        p.write_bytes(b.encoded(rgb));selected['resources']['meters'][0]={'path':name,'sha256':b.sha(p.read_bytes())}
        return selected
    def test_current_and_deterministic(self):
        self.assertEqual(b.check(self.root)['status'],'PASS')
        self.assertEqual(b.derive(self.root,b.encoded(self.selected)),b.derive(self.root,b.encoded(self.selected)))
    def test_synthetic_sources_propagate_both_routes_and_preserve_history(self):
        before=self.snapshot();selection=self.synthetic();plan=self.stage(selection)
        for name,digest in before.items():self.assertEqual(b.sha((self.root/name).read_bytes()),digest)
        b.apply(self.root,self.stagepath);self.assertEqual(b.check(self.root)['status'],'PASS')
        runtime=json.loads((self.root/b.RUNTIME).read_text());mapping=json.loads((self.root/b.MAPPING).read_text())
        self.assertEqual(len(mapping['files']),6)
        for name in EXPECTED:
            rows=[r for r in runtime['files'] if r['destination'] in ('assets/shared-ui/'+name,'assets/gameplay/'+name)]
            self.assertEqual(len(rows),2);self.assertEqual({r['source_path'] for r in rows},{'assets/hd/shared-ui-v1/'+name})
            raw=(self.root/rows[0]['source_path']).read_bytes()
            self.assertEqual({r['sha256'] for r in rows},{b.sha(raw)})
            self.assertEqual({r['bytes'] for r in rows},{len(raw)})
        components=(self.root/'assets/hd/shared-ui-v1/gameplay-hud-components-v1.hda').read_bytes()
        self.assertEqual(components[64:64+96*20*4],bytes((23,41,89,255))*96*20)
        self.assertNotEqual(components,self.initial['assets/hd/shared-ui-v1/gameplay-hud-components-v1.hda'])
        self.assertNotEqual((self.root/b.HEADER).read_bytes(),self.initial[b.HEADER])
        meters=(self.root/'assets/hd/shared-ui-v1/gameplay-hud-meters-v2.hda').read_bytes()
        baseline=self.initial['assets/hd/shared-ui-v1/gameplay-hud-meters-v2.hda']
        self.assertEqual(meters[:64],baseline[:64]);self.assertEqual(meters[177008:],baseline[177008:])
        for name,data in self.initial.items():
            if name.startswith(('assets/hd/packs/','assets/hd/artwork/')) or name=='packaging/runtime-assets-public63a89b3.json':self.assertEqual((self.root/name).read_bytes(),data)
        import build_current_art
        for family in PROFILES:self.assertEqual(build_current_art.check(self.root,family)['status'],'PASS')
    def test_missing_and_stale_consumers_detected(self):
        name='assets/hd/shared-ui-v1/'+EXPECTED[3];p=self.root/name;p.unlink()
        with self.assertRaises((ValueError,FileNotFoundError)):b.check(self.root)
        p.write_bytes(self.initial[name][:-1]+b'X')
        with self.assertRaises(ValueError):b.check(self.root)
    def test_stale_plan_and_modified_stage_rejected_without_writes(self):
        self.stage();p=self.root/b.MAPPING;p.write_bytes(p.read_bytes()+b' ');before=self.snapshot()
        with self.assertRaises(ValueError):b.apply(self.root,self.stagepath)
        self.assertEqual(before,self.snapshot())
        p.write_bytes(self.initial[b.MAPPING]);p=self.stagepath/'files'/b.MAPPING;p.write_bytes(p.read_bytes()+b' ');before=self.snapshot()
        with self.assertRaises(ValueError):b.apply(self.root,self.stagepath)
        self.assertEqual(before,self.snapshot())
    def test_late_temporary_collision_preflights_every_output(self):
        self.stage(self.synthetic());p=self.root/(b.RUNTIME+'.hud-tmp');p.write_bytes(b'occupied');before=self.snapshot()
        with self.assertRaises(ValueError):b.apply(self.root,self.stagepath)
        self.assertEqual(before,self.snapshot())
    def test_source_changed_after_stage_rejected(self):
        selected=self.synthetic();self.stage(selected);p=self.root/selected['resources']['components'][0]['path'];p.write_bytes(png(96,20,(24,41,89,255)));before=self.snapshot()
        with self.assertRaises(ValueError):b.apply(self.root,self.stagepath)
        self.assertEqual(before,self.snapshot())
    def test_source_hash_and_paths_rejected(self):
        for key,value in [('sha256','0'*64),('path','../outside.png'),('path','/tmp/outside.png')]:
            selected=copy.deepcopy(self.selected);selected['resources']['static'][0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):b.derive(self.root,b.encoded(selected))
    def test_source_symlink_rejected(self):
        record=self.selected['resources']['static'][0];p=self.root/record['path'];raw=p.read_bytes();p.unlink();outside=self.base/'outside.png';outside.write_bytes(raw);p.symlink_to(outside)
        with self.assertRaises(ValueError):b.derive(self.root,b.encoded(self.selected))
    def test_geometry_rejected(self):
        selected=self.synthetic();p=self.root/selected['resources']['components'][0]['path'];p.write_bytes(png(95,20,(23,41,89,255)));selected['resources']['components'][0]['sha256']=b.sha(p.read_bytes())
        with self.assertRaises(ValueError):b.derive(self.root,b.encoded(selected))
    def test_build_and_gameplay_authority_rejected(self):
        for name in ('Makefile','src/tyrian2.c'):
            p=self.root/name;p.write_bytes(self.initial[name]+b'\n');before=self.snapshot()
            with self.subTest(name=name),self.assertRaises(ValueError):b.derive(self.root,b.encoded(self.selected))
            self.assertEqual(before,self.snapshot());p.write_bytes(self.initial[name])
    def test_immutable_recipe_and_mask_authority_rejected(self):
        for key in ('meter_recipe','mask'):
            name=recipe.FIXED_INPUTS[key]['path'];p=self.root/name;p.write_bytes(self.initial[name]+b'\n')
            with self.subTest(key=key),self.assertRaises(ValueError):b.derive(self.root,b.encoded(self.selected))
            p.write_bytes(self.initial[name])
    def test_duplicate_or_unknown_semantics_rejected(self):
        selected=copy.deepcopy(self.selected);selected['resources']['extra']=selected['resources']['static']
        with self.assertRaises(ValueError):b.derive(self.root,b.encoded(selected))
        selected=copy.deepcopy(self.selected);selected['resources']['components']=selected['resources']['static']
        with self.assertRaises(ValueError):b.derive(self.root,b.encoded(selected))
    def test_stage_paths_and_plan_injection_rejected(self):
        with self.assertRaises(ValueError):b.stage(self.root,self.root/b.SELECTION,self.root/'forbidden')
        link=self.base/f'link-{self.counter}';link.symlink_to(self.base,target_is_directory=True)
        with self.assertRaises(ValueError):b.stage(self.root,self.root/b.SELECTION,link/'escaped')
        self.stage();p=self.stagepath/'plan.json';j=json.loads(p.read_text());j['files'][0]['path']='../escaped';p.write_bytes(b.encoded(j));before=self.snapshot()
        with self.assertRaises(ValueError):b.apply(self.root,self.stagepath)
        self.assertEqual(before,self.snapshot())
    def test_cross_family_generated_headers_cannot_be_rebound(self):
        import build_current_art
        for name in ('src/global_asset_registry.h','src/current_art_payload_pins.h'):
            p=self.root/name;p.write_bytes(self.initial[name]+b'/* drift */')
            with self.subTest(name=name),self.assertRaises(ValueError):b.derive(self.root,b.encoded(self.selected))
            p.write_bytes(self.initial[name])
        p=self.root/b.HEADER;p.write_bytes(self.initial[b.HEADER]+b'/* drift */')
        selected=(self.root/profile('pulse')['selection']).read_bytes()
        with self.assertRaises((ValueError, __import__('subprocess').CalledProcessError)):
            build_current_art.derive(self.root,selected,'pulse')

    def test_mapping_destination_tamper_rejected(self):
        from current_hud_compatibility import load
        p=self.root/b.MAPPING;j=json.loads(p.read_text());j['files'][0]['destinations'][1]='assets/gameplay/wrong.hda';p.write_bytes(b.encoded(j))
        with self.assertRaises(ValueError):load(self.root)

if __name__=='__main__':unittest.main()
