"""Bounded current orb authoring regression; no new gameplay/platform acceptance.

Generation fixtures copy only two PNGs. Integration fixtures hardlink the finite
build closure, then replace mutated files (never write shared inodes), avoiding a
second full asset copy. Builder scratch directories are reclaimed each call.
"""
import copy
import contextlib
import hashlib
import io
import json
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import build_current_enemy_orb as b
import current_enemy_orb_compatibility as c
import package_runtime as pack
import build_current_craft267 as craft
from current_art_policy import PROFILES, profile

EXPECTED = {80112: 'bullet-112-8.hda', 80113: 'bullet-113-8.hda',
            1420112: 'enemy-orb112113-112-8.hda', 1420113: 'enemy-orb112113-113-8.hda'}
SOURCES = {112: ('assets/hd/source/bullet-112-8-22e2be2903bc.png', 'c28da6740c5827bab6e2ab44faf0e5218fb8f033af7c6bc500d80167cf47405b'),
           113: ('assets/hd/source/bullet-113-8-185ae48dcc14.png', '49a4ef3fe0c25cb5cabe153a83d4cf72fc204c45872af83178521d33a902d412')}


def write(root, name, data):
    """Copy-on-write: shared fixture inodes are never modified."""
    target = root/name
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name+'.test-write')
    temporary.write_bytes(data)
    os.replace(temporary, target)
    return target


def png(color=(31, 53, 71, 127), size=(96, 112), mode='RGBA'):
    stream = io.BytesIO()
    Image.new(mode, size, color if mode == 'RGBA' else color[:3]).save(stream, format='PNG')
    return stream.getvalue()


class OrbGenerationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='orb-generation-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.selected = dict(schema=c.CANDIDATE_SCHEMA, version='fixture', masters=[])
        for selector in (112, 113):
            source, digest = SOURCES[selector]
            raw = (ROOT/source).read_bytes()
            self.assertEqual(c.sha(raw), digest)
            target = f'authoring-inputs/enemy-orb-current/orb-{selector}.png'
            write(self.root, target, raw)
            self.selected['masters'].append(dict(selector=selector, source_png=target, source_sha256=digest))

    def generate(self, selected=None):
        return c.generate(self.root, b.encoded(selected or self.selected), candidate=True)[2]

    def test_bootstrap_exact_both_historical_contracts(self):
        blobs = self.generate()
        self.assertEqual(set(blobs), {(i, 8) for i in EXPECTED})
        for identity, filename in EXPECTED.items():
            raw = blobs[(identity, 8)]
            self.assertEqual(struct.unpack('<4s6I', raw[:28]), (b'HDR1', identity, 8, 12, 14, 0, 0))
            if identity > 1000000:
                expected = (ROOT/'assets/hd/packs/asteroid1-ten-v1'/filename).read_bytes()
                self.assertEqual(raw, expected)
            else:
                with Image.open(ROOT/SOURCES[identity-80000][0]) as image:
                    self.assertEqual(raw[28:], image.tobytes())

    def test_each_master_independently_reaches_both_contracts(self):
        original = self.generate()
        for ordinal, selector in enumerate((112, 113)):
            row = self.selected['masters'][ordinal]
            saved = (self.root/row['source_png']).read_bytes()
            raw = png((31+ordinal, 53, 71, 127))
            write(self.root, row['source_png'], raw)
            row['source_sha256'] = c.sha(raw)
            changed = self.generate()
            for identity in EXPECTED:
                if identity in (80000+selector, 1420000+selector):
                    self.assertNotEqual(changed[(identity, 8)], original[(identity, 8)])
                else:
                    self.assertEqual(changed[(identity, 8)], original[(identity, 8)])
            write(self.root, row['source_png'], saved)
            row['source_sha256'] = c.sha(saved)

    def test_mask_zeros_all_rgba_outside_exact_public_support(self):
        raw = png()
        for row in self.selected['masters']:
            write(self.root, row['source_png'], raw); row['source_sha256'] = c.sha(raw)
        blobs = self.generate()
        for selector in (112, 113):
            ordinary, masked = blobs[(80000+selector, 8)][28:], blobs[(1420000+selector, 8)][28:]
            with Image.open(ROOT/f'assets/hd/artwork/asteroid1-orb112113-v1/enemy-orb112113-{selector}-8.png') as reference:
                alpha = reference.getchannel('A')
                cells = {(x//8, y//8) for y in range(112) for x in range(96) if alpha.getpixel((x,y))}
            self.assertEqual(len(cells), 45)
            for y in range(112):
                for x in range(96):
                    p = (y*96+x)*4
                    self.assertEqual(masked[p:p+4], ordinary[p:p+4] if (x//8,y//8) in cells else b'\0'*4)

    def test_strict_selection_authority(self):
        variants=[]
        for field, value in [('selector', True), ('selector', 113), ('source_sha256', '0'*64),
                             ('source_png', SOURCES[112][0]), ('source_png', 'authoring-inputs/enemy-orb-current/../orb-112.png')]:
            variant=copy.deepcopy(self.selected); variant['masters'][0][field]=value; variants.append(variant)
        variant=copy.deepcopy(self.selected); variant['masters'].reverse(); variants.append(variant)
        variant=copy.deepcopy(self.selected); variant['masters'][0]['geometry']=[12,14]; variants.append(variant)
        variant=copy.deepcopy(self.selected); variant['extra']=1; variants.append(variant)
        for variant in variants:
            with self.subTest(variant=variant), self.assertRaises(ValueError): self.generate(variant)
        with self.assertRaises(ValueError): c.parse(b'{"schema":1,"schema":2}')
        with self.assertRaises(ValueError): c.parse(b'{"x":NaN}')

    def test_invalid_pngs_and_uncovered_cells(self):
        row=self.selected['masters'][0]
        for raw in (png(size=(97,112)), png(mode='RGB'), png()+b'extra', png(color=(0,0,0,0)), b'not PNG'):
            write(self.root,row['source_png'],raw); row['source_sha256']=c.sha(raw)
            with self.subTest(length=len(raw)), self.assertRaises(ValueError): self.generate()

    def test_hardlinked_masters_rejected(self):
        row=self.selected['masters'][0]
        os.link(self.root/row['source_png'],self.root/'alias.png')
        with self.assertRaises(ValueError): self.generate()

    def test_symlink_input_rejected(self):
        row=self.selected['masters'][0]; source=self.root/row['source_png']
        original=source.read_bytes(); source.unlink()
        target=write(self.root,'target.png',original); source.symlink_to(target)
        with self.assertRaises(ValueError): self.generate()


class OrbIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='orb-integration-', dir=ROOT.parent)
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name); self.root=self.base/'repo'; self.root.mkdir()
        self.selected=c.parse((ROOT/c.SELECTION).read_bytes())
        names=b.dependencies(ROOT,self.selected)
        for family in PROFILES:
            selected_path=profile(family)['selection']; names.add(selected_path)
            names |= {row['source_png'] for row in json.loads((ROOT/selected_path).read_bytes())['resources']}
        registry=json.loads((ROOT/b.REGISTRY).read_bytes())
        names |= {'assets/hd/global-assets-v1/'+row['path'] for row in registry['resources']}
        for manifest in (b.RUNTIME,'packaging/runtime-assets-public63a89b3.json'):
            names |= {r['source_path'] for r in b.parse_manifest((ROOT/manifest).read_bytes())['files']}
        self.frozen={}
        for name in sorted(names):
            source=ROOT/name; target=self.root/name; target.parent.mkdir(parents=True,exist_ok=True)
            if name.startswith('authoring-inputs/'):
                target.write_bytes(source.read_bytes())
            else:
                os.link(source,target)
        # Preserve explicit frozen historical art plus both original approval records.
        for directory in ('assets/hd/artwork/enemy-orb112-113-v1','assets/hd/artwork/asteroid1-orb112113-v1'):
            for source in (ROOT/directory).rglob('*'):
                if source.is_file(): self.frozen[source.relative_to(ROOT).as_posix()]=source.read_bytes()
        for source in SOURCES.values(): self.frozen[source[0]]=(ROOT/source[0]).read_bytes()
        for name,data in self.frozen.items():
            if not (self.root/name).exists(): write(self.root,name,data)

    def stage(self,selected=None):
        request=write(self.base,'request.json',b.encoded(selected or self.selected))
        destination=self.base/'stage'
        plan=b.stage(self.root,request,destination)
        return destination,plan

    def snapshot(self):
        return {name:b.fingerprint(self.root,name) for name in c.input_paths(self.root)|{b.RUNTIME,b.BINDING}}

    def test_stage_apply_check_and_frozen_history(self):
        before=self.snapshot()
        destination,plan=self.stage()
        self.assertEqual(before,self.snapshot())
        self.assertEqual(len(plan['files']),9)
        b.apply(self.root,destination)
        self.assertEqual(b.check(self.root)['editable_masters'],2)
        for name,data in self.frozen.items(): self.assertEqual((self.root/name).read_bytes(),data)
        runtime=b.parse_manifest((self.root/b.RUNTIME).read_bytes())
        destinations={r['destination'] for r in runtime['files']}
        self.assertIn('assets/gameplay/bullet-112-8.hda',destinations)
        self.assertNotIn('assets/gameplay/enemy-orb112113-112-8.hda',destinations)

    def test_changed_master_candidate_apply_and_current_views(self):
        before=c.load(self.root)
        row=self.selected['masters'][0]; raw=png()
        write(self.root,row['source_png'],raw); row['source_sha256']=c.sha(raw)
        self.selected['schema']=c.CANDIDATE_SCHEMA
        destination,_=self.stage(self.selected); b.apply(self.root,destination)
        after=c.load(self.root)
        for identity,filename in EXPECTED.items():
            dest='assets/gameplay/'+filename
            self.assertEqual(before[dest]['sha256']==after[dest]['sha256'], identity in (80113,1420113))
        out=self.base/'contracts'
        result=craft.enemy_orb_contract_view(self.root,out)
        self.assertEqual(result['files'],4)
        for identity,filename in EXPECTED.items(): self.assertEqual((out/filename).read_bytes(),(self.root/c.ROOT/filename).read_bytes())
        for name,data in self.frozen.items(): self.assertEqual((self.root/name).read_bytes(),data)

    def test_tampered_stage_and_stale_plan_rejected_without_writes(self):
        destination,plan=self.stage(); before=self.snapshot()
        originals={name:(destination/name).read_bytes() for name in ('plan.json','request.json','files/'+c.ROOT+'/'+EXPECTED[80112])}
        variants=[('plan.json',b.encoded(dict(plan,request_sha256='0'*64))),
                  ('request.json',b.encoded(dict(self.selected,version='tampered'))),
                  ('files/'+c.ROOT+'/'+EXPECTED[80112],b'bad')]
        for name,bad in variants:
            write(destination,name,bad)
            with self.subTest(path=name),self.assertRaises(ValueError): b.apply(self.root,destination)
            self.assertEqual(before,self.snapshot()); write(destination,name,originals[name])
        write(self.root,c.MAPPING,(self.root/c.MAPPING).read_bytes()+b' ')
        with self.assertRaises(ValueError): b.apply(self.root,destination)

    def test_temporary_output_preflight_and_handled_failure_rollback(self):
        selected=copy.deepcopy(self.selected); selected['version']='rollback-fixture'
        destination,_=self.stage(selected)
        before=self.snapshot()
        temporary=write(self.root,c.SELECTION+b.SUFFIX,b'occupied')
        with self.assertRaises(ValueError): b.apply(self.root,destination)
        self.assertEqual(before,self.snapshot()); temporary.unlink()
        real_replace=os.replace
        calls=0
        def fail_second(source,target):
            nonlocal calls
            calls+=1
            if calls==2: raise OSError('injected handled replacement failure')
            return real_replace(source,target)
        with patch.object(craft.os,'replace',side_effect=fail_second):
            with self.assertRaisesRegex(OSError,'injected'): b.apply(self.root,destination)
        self.assertGreaterEqual(calls,3)
        self.assertEqual(before,self.snapshot())
        self.assertFalse(list(self.root.rglob('*'+b.SUFFIX)))

    def test_source_authority_and_header_guards(self):
        raw=b.encoded(self.selected)
        for name in ('src/render_mirror.c','src/asteroid1_enemy_orb112113_mirror.inc','src/global_asset_registry.h','src/current_art_payload_pins.h'):
            original=(self.root/name).read_bytes(); write(self.root,name,original+b'\n/* forbidden drift */\n')
            with self.subTest(path=name),self.assertRaises(ValueError): b.derive(self.root,raw)
            write(self.root,name,original)


class OrbPackagingTests(unittest.TestCase):
    def test_current_pair_optin_closure_and_tampering(self):
        selected=c.load(ROOT)
        rows=[]
        for identity,filename in EXPECTED.items():
            row=dict(selected['assets/gameplay/'+filename])
            raw=(ROOT/row['source_path']).read_bytes()
            row.update(bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
                       group='gameplay',revision='current-single-source-enemy-orb')
            rows.append(row)
        with tempfile.TemporaryDirectory(prefix='orb-package-') as tmp:
            manifest=Path(tmp)/'selection.json'
            def run(chosen):
                manifest.write_bytes(b.encoded(dict(schema='opentyrian-runtime-package-v1',files=chosen,external_dependencies=[])))
                with contextlib.redirect_stdout(io.StringIO()):
                    return pack.main(['--source-root',str(ROOT),'--manifest',str(manifest)])
            self.assertEqual(run(rows[:2]),0)
            self.assertEqual(run(rows),0)
            for chosen in (rows[:1], rows[:3], rows[2:]):
                with self.subTest(count=len(chosen)),self.assertRaises(ValueError): run(chosen)
            stale=copy.deepcopy(rows); stale[0]['sha256']='0'*64
            with self.assertRaises(ValueError): run(stale)
            wrong=copy.deepcopy(rows); wrong[2]['revision']='historical'
            with self.assertRaises(ValueError): run(wrong)


if __name__=='__main__': unittest.main()
