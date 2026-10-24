"""Actual current Guided stage/apply -> complete runtime export, not gameplay QA.

Uses isolated copies of the builder's declared inputs. No native renderer or
natural gameplay result is inferred from these packaging-only tests.
"""
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import build_current_guided as build
import current_guided_compatibility as guided
import package_runtime as package

BASE = 'e5fac6ce2a739ad2e0d6e8f99edaec56411e6e7a'
MANIFEST = 'packaging/runtime-assets-v1.json'
EXACT = {f'assets/gameplay/bullet-{i}-8.hda' for i in (19,171,20,21)}


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def by_destination(value):
    return {r['destination']:r for r in value['files']}


class GuidedRuntimePackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT/MANIFEST).read_bytes())
        cls.public = json.loads(subprocess.check_output(['git','show',BASE+':'+MANIFEST],cwd=ROOT))
        selected = json.loads((ROOT/guided.SELECTION).read_bytes())
        old = json.loads((ROOT/'packaging/runtime-assets-public63a89b3.json').read_bytes())
        cls.inputs = build.dependencies(ROOT,selected) | {
            row['source_path'] for row in cls.manifest['files']+old['files']}
        # The root-level authority check also reads the legacy current-source
        # selections, whereas the rebuild scratch uses their verified HDA map.
        from current_art_policy import PROFILES, profile
        for family in PROFILES:
            selection=profile(family)['selection']
            cls.inputs.add(selection)
            cls.inputs.update(r['source_png'] for r in json.loads((ROOT/selection).read_bytes())['resources'])

        # Sidekick's own six source PNGs are needed only for its true check,
        # beyond the Guided builder's consumer-only compatibility closure.
        import current_sidekick_body_compatibility as sidekick
        cls.inputs.add(sidekick.SELECTION)
        cls.inputs.update(r['source_png'] for r in json.loads((ROOT/sidekick.SELECTION).read_bytes())['resources'])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='guided-runtime-package-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base/'root'
        self.root.mkdir()
        for name in sorted(self.inputs):
            target=self.root/name; target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/name,target)

    def pack(self, root=None, *extra):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=package.main(['--source-root',str(root or self.root),*map(str,extra)])
        return code,json.loads(output.getvalue())

    def write_manifest(self, value):
        (self.root/MANIFEST).write_bytes(encoded(value))

    def test_cross_family_declared_inputs_and_real_checks(self):
        import importlib
        from current_sidekick_body_compatibility import independent_input_paths
        required=guided.input_paths(self.root)|{guided.MAPPING}
        self.assertTrue(required <= independent_input_paths(self.root))
        for family in ('sonic','protron','plasma_projectile','front_multi'):
            module=importlib.import_module('build_current_'+family)
            compat=importlib.import_module('current_'+family+'_compatibility')
            selected=json.loads((self.root/compat.SELECTION).read_bytes())
            with self.subTest(family=family):
                self.assertTrue(required <= module.dependencies(self.root,selected))
                self.assertEqual(module.check(self.root)['status'],'PASS')
        import build_current_sidekick_body as sidekick
        for check in (sidekick.check,sidekick.charge_check,sidekick.mf_check):
            with self.subTest(check=check.__name__):
                self.assertEqual(check(self.root)['status'],'PASS')

    def test_exact_replacement_and_real_linux_windows_asset_exports(self):
        before=by_destination(self.public); after=by_destination(self.manifest)
        self.assertEqual(len(before),1029); self.assertEqual(len(after),1029)
        self.assertEqual(set(after),set(before))
        for key,row in before.items():
            if key not in EXACT|{'CURRENT-PRODUCTION-VALIDATION.json'}:
                self.assertEqual(after[key],row)
            elif key in EXACT:
                self.assertEqual({k:v for k,v in row.items() if k not in ('source_path','revision')},
                                 {k:v for k,v in after[key].items() if k not in ('source_path','revision')})
        current_meta={k:copy.deepcopy(v) for k,v in self.manifest.items() if k!='files'}
        previous_meta={k:copy.deepcopy(v) for k,v in self.public.items() if k!='files'}
        binding=json.loads((self.root/'packaging/current-production-validation.json').read_bytes())
        self.assertEqual(current_meta['source_revision']['current_production_source_manifest_sha256'],
                         binding['production_source_manifest_sha256'])
        for meta in (current_meta,previous_meta):
            meta['source_revision'].pop('current_production_source_manifest_sha256')
        self.assertEqual(current_meta,previous_meta)
        selected=guided.load(self.root)
        self.assertEqual(set(selected),EXACT)
        for key,row in selected.items():
            self.assertEqual(after[key]['source_path'],row['source_path'])
            self.assertEqual(after[key]['sha256'],row['sha256'])
            self.assertEqual(after[key]['group'],'gameplay')
            self.assertEqual(after[key]['revision'],'current-single-source-guided')
        for platform in ('linux','windows'):
            destination=self.base/('export-'+platform)
            code,report=self.pack(None,'--platform',platform,'--build','--output',destination)
            self.assertEqual(code,0); self.assertTrue(report['assets_complete'])
            self.assertEqual(report['verified_files'],1029)
            self.assertFalse(report['runtime_ready'])
            self.assertFalse(report['executable_included'])
            for row in self.manifest['files']:
                self.assertEqual((destination/row['destination']).read_bytes(),
                                 (self.root/row['source_path']).read_bytes())
            for i in (20,21,105,106,124,125):
                self.assertTrue((destination/f'assets/gameplay/bullet-{i}-8.hda').is_file())

    def test_actual_master_edits_stage_apply_and_export_only_own_identity(self):
        pristine={name:(self.root/name).read_bytes() for name in self.inputs}
        protected={name:raw for name,raw in pristine.items() if name.startswith('src/') or
                   name=='assets/hd/global-assets-v1/registry.json'}
        for selector,expected in ((19,{19}),(171,{171}),(20,{20}),(21,{21})):
            with self.subTest(selector=selector):
                for name,raw in pristine.items(): (self.root/name).write_bytes(raw)
                selected=json.loads((self.root/guided.SELECTION).read_bytes())
                selected.pop('resources'); selected['schema']=guided.CANDIDATE_SCHEMA
                selected['version']='runtime-pair-edit-'+str(selector)
                row=next(r for r in selected['masters'] if r['selector']==selector)
                master=self.root/row['source_png']
                with Image.open(master) as image:
                    channels=image.split()
                    edited=Image.merge('RGBA',(channels[0].point(lambda x:(x+37)%256),*channels[1:]))
                edited.save(master)
                row['source_sha256']=sha(master.read_bytes())
                request=self.base/f'candidate-{selector}.json';request.write_bytes(encoded(selected))
                stage=self.base/f'stage-{selector}'
                build.stage(self.root,request,stage)
                build.apply(self.root,stage)
                self.assertEqual(build.check(self.root)['status'],'PASS')
                now=json.loads((self.root/MANIFEST).read_bytes())
                before=by_destination(self.manifest);after=by_destination(now)
                self.assertEqual(set(before),set(after))
                expected_paths={f'assets/gameplay/bullet-{i}-8.hda' for i in expected}
                self.assertEqual({k for k in before if before[k]!=after[k]},
                                 expected_paths|({'CURRENT-PRODUCTION-VALIDATION.json'} if selector in (20,21) else set()))
                for key in EXACT:
                    a=(self.root/after[key]['source_path']).read_bytes()
                    b=pristine[before[key]['source_path']]
                    self.assertEqual(a!=b,key in expected_paths)
                for name,raw in protected.items():
                    if name!=guided.HEADER:self.assertEqual((self.root/name).read_bytes(),raw)
                self.assertEqual((self.root/guided.HEADER).read_bytes()!=protected[guided.HEADER], selector in (20,21))
                destination=self.base/f'edited-export-{selector}'
                code,report=self.pack(None,'--build','--output',destination)
                self.assertEqual(code,0);self.assertEqual(report['verified_files'],1029)
                for row in now['files']:
                    self.assertEqual((destination/row['destination']).read_bytes(),
                                     (self.root/row['source_path']).read_bytes())

    def test_default_manifest_missing_any_or_all_quartet_fails_before_output(self):
        for absent in ({name} for name in sorted(EXACT)):
            candidate=copy.deepcopy(self.manifest)
            candidate['files']=[r for r in candidate['files'] if r['destination'] not in absent]
            self.write_manifest(candidate)
            with self.assertRaisesRegex(ValueError,'exactly four'):
                self.pack(None,'--build','--output',self.base/'forbidden')
            self.assertFalse((self.base/'forbidden').exists())
        candidate=copy.deepcopy(self.manifest)
        candidate['files']=[r for r in candidate['files'] if r['destination'] not in EXACT]
        self.write_manifest(candidate)
        with self.assertRaisesRegex(ValueError,'exactly four'): self.pack()

    def test_current_rows_reject_fifth_marker_or_stale_metadata(self):
        variants=[]
        for field,value in [('source_path','assets/hd/current-compat/guided/other.hda'),
                            ('destination','assets/gameplay/bullet-107-8.hda'),
                            ('group','unrelated'),('revision','unrelated'),('sha256','0'*64)]:
            candidate=copy.deepcopy(self.manifest)
            next(r for r in candidate['files'] if r['destination'] in EXACT)[field]=value
            variants.append(candidate)
        extra=copy.deepcopy(next(r for r in self.manifest['files'] if r['destination'] not in EXACT))
        extra['destination']='extra-generic.bin'
        generic=copy.deepcopy(self.manifest);generic['files'].append(extra)
        self.write_manifest(generic)
        code,report=self.pack();self.assertEqual(code,0);self.assertEqual(report['verified_files'],1030)
        marked=copy.deepcopy(generic);marked['files'][-1]['revision']='current-single-source-guided'
        variants.append(marked)
        for candidate in variants:
            with self.subTest(candidate=candidate['files'][-1]['destination']):
                self.write_manifest(candidate)
                with self.assertRaises(ValueError):self.pack()

    def test_source_missing_and_self_consistent_transport_corruption_rejected(self):
        source=next(r for r in self.manifest['files'] if r['destination'] in EXACT)
        file=self.root/source['source_path']; original=file.read_bytes()
        file.unlink()
        with self.assertRaises(ValueError):self.pack()
        for offset in (4,28,100):
            changed=bytearray(original);changed[offset]^=1;raw=bytes(changed)
            file.write_bytes(raw)
            candidate=copy.deepcopy(self.manifest)
            row=next(r for r in candidate['files'] if r['destination']==source['destination'])
            row.update(bytes=len(raw),sha256=sha(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
            self.write_manifest(candidate)
            with self.assertRaises(ValueError):self.pack()
        file.write_bytes(original)

    def test_historical_custom_manifest_without_current_contract_remains_generic(self):
        old=copy.deepcopy(next(r for r in self.manifest['files'] if r['destination']=='assets/gameplay/bullet-19-8.hda'))
        raw=(self.root/old['source_path']).read_bytes()
        old['source_path']='historical/bullet-19-8.hda';old['revision']='frozen-reproducer'
        historical=self.root/old['source_path'];historical.parent.mkdir();historical.write_bytes(raw)
        custom={'schema':'opentyrian-runtime-package-v1','source_revision':{},
                'external_dependencies':{},'files':[old]}
        path=self.base/'historical-custom.json';path.write_bytes(encoded(custom))
        # No Guided inputs are required by this historical, explicitly selected
        # Guided manifest. Its basename alone does not grant a current contract.
        for name in guided.input_paths(self.root)|{guided.MAPPING,guided.HEADER}:
            (self.root/name).unlink()
        with patch.object(guided,'load',side_effect=AssertionError('Historical manifest must not load current inputs')):
            code,report=self.pack(None,'--manifest',path)
        self.assertEqual(code,0);self.assertEqual(report['verified_files'],1)

    def test_real_transaction_tamper_stale_and_manifest_write_rollback(self):
        selected=json.loads((self.root/guided.SELECTION).read_bytes())
        selected.pop('resources');selected['schema']=guided.CANDIDATE_SCHEMA
        selected['version']='real-rollback-fixture'
        row=selected['masters'][0];master=self.root/row['source_png']
        with Image.open(master) as image:
            channels=image.split()
            edited=Image.merge('RGBA',(channels[0].point(lambda x:(x+17)%256),*channels[1:]))
        edited.save(master);row['source_sha256']=sha(master.read_bytes())
        request=self.base/'rollback-request.json';request.write_bytes(encoded(selected))
        stage=self.base/'rollback-stage';build.stage(self.root,request,stage)
        def snapshot():return {name:sha((self.root/name).read_bytes()) for name in self.inputs}
        before=snapshot()
        staged=stage/'files'/MANIFEST;raw=staged.read_bytes();staged.write_bytes(raw+b'junk')
        with self.assertRaisesRegex(ValueError,'Modified staged Guided bytes'):build.apply(self.root,stage)
        staged.write_bytes(raw);self.assertEqual(snapshot(),before)
        master_raw=master.read_bytes();master.write_bytes(master_raw+b'changed-after-stage')
        stale=snapshot()
        with self.assertRaises(ValueError):build.apply(self.root,stage)
        self.assertEqual(snapshot(),stale);master.write_bytes(master_raw)
        real=os.replace;reached=[]
        def failing(source,destination):
            if Path(destination)==self.root/MANIFEST:
                reached.append(str(destination));raise OSError('injected runtime manifest write failure')
            return real(source,destination)
        with patch('build_current_craft267.os.replace',side_effect=failing):
            with self.assertRaisesRegex(OSError,'injected runtime manifest'):build.apply(self.root,stage)
        self.assertEqual(len(reached),1);self.assertEqual(snapshot(),before)
        self.assertFalse(list(self.root.rglob('*'+build.SUFFIX)))
        build.apply(self.root,stage)
        self.assertEqual(build.check(self.root)['status'],'PASS')


if __name__=='__main__':unittest.main()
