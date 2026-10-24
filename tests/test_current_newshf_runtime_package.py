"""Actual current aircraft stage/apply -> complete runtime export, not gameplay QA.

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
import build_current_newshf as build
import current_newshf_compatibility as aircraft
import package_runtime as package

BASE = 'a2b1bb5b6648fe835cd719d1764411a1773800ec'
MANIFEST = 'packaging/runtime-assets-v1.json'
EXACT = {'assets/global/newshf/'+aircraft.name(i) for i in aircraft.IDS}


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def by_destination(value):
    return {r['destination']:r for r in value['files']}


class AircraftRuntimePackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT/MANIFEST).read_bytes())
        cls.public = json.loads(subprocess.check_output(['git','show',BASE+':'+MANIFEST],cwd=ROOT))
        selected = json.loads((ROOT/aircraft.SELECTION).read_bytes())
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
        self.temp = tempfile.TemporaryDirectory(prefix='aircraft-runtime-package-')
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
        required=aircraft.input_paths(self.root)|{aircraft.MAPPING}
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

    def test_bootstrap_nine_same_destinations_and_full_exports(self):
        before=by_destination(self.public);after=by_destination(self.manifest)
        self.assertEqual(len(before),1029);self.assertEqual(set(before),set(after))
        six={'assets/global/newshf/'+aircraft.name(i) for i in aircraft.EDIT_IDS}
        self.assertEqual({key for key in before if before[key]!=after[key]},six|{'CURRENT-PRODUCTION-VALIDATION.json'})
        for key in six:
            self.assertEqual({k:v for k,v in before[key].items() if k!='source_path'}, {k:v for k,v in after[key].items() if k!='source_path'})
        for platform in ('linux','windows'):
            output=self.base/('export-'+platform)
            code,report=self.pack(None,'--platform',platform,'--build','--output',output)
            self.assertEqual(code,0);self.assertEqual(report['verified_files'],1029)
            self.assertFalse(report['runtime_ready']);self.assertFalse(report['executable_included'])
            for row in self.manifest['files']:
                self.assertEqual((output/row['destination']).read_bytes(),(self.root/row['source_path']).read_bytes())

    def test_actual_master_edits_apply_export_exact_three_and_frozen168(self):
        pristine={name:(self.root/name).read_bytes() for name in self.inputs}
        for selector in aircraft.SELECTORS:
            with self.subTest(selector=selector):
                for name,raw in pristine.items():(self.root/name).write_bytes(raw)
                selected=json.loads((self.root/aircraft.SELECTION).read_bytes())
                selected.pop('resources');selected['schema']=aircraft.CANDIDATE_SCHEMA;selected['version']='edited-'+str(selector)
                row=next(r for r in selected['masters'] if r['selector']==selector)
                master=self.root/row['source_png']
                with Image.open(master) as im:
                    channels=im.split();edited=Image.merge('RGBA',(channels[0].point(lambda x:(x+37)%256),*channels[1:]))
                edited.save(master);row['source_sha256']=sha(master.read_bytes())
                request=self.base/f'candidate-{selector}.json';request.write_bytes(encoded(selected));stage=self.base/f'stage-{selector}'
                build.stage(self.root,request,stage);build.apply(self.root,stage)
                self.assertEqual(build.check(self.root)['status'],'PASS')
                before=by_destination(self.manifest);now=json.loads((self.root/MANIFEST).read_bytes());after=by_destination(now)
                changed={'assets/global/newshf/'+aircraft.name(s['identity']) for s in aircraft.RECIPE['pieces'] if s['selector']==selector}
                self.assertEqual({key for key in before if before[key]!=after[key]},changed|{'CURRENT-PRODUCTION-VALIDATION.json'})
                for name,raw in pristine.items():
                    if name.startswith(('src/','authoring-inputs/enemies/newshf-phase-a/','assets/hd/newshf-v1/')) and name!=aircraft.HEADER:
                        self.assertEqual((self.root/name).read_bytes(),raw,name)
                self.assertNotEqual((self.root/aircraft.HEADER).read_bytes(),pristine[aircraft.HEADER])
                output=self.base/f'edited-export-{selector}'
                code,report=self.pack(None,'--build','--output',output)
                self.assertEqual(code,0);self.assertEqual(report['verified_files'],1029)
                for row in now['files']:
                    self.assertEqual((output/row['destination']).read_bytes(),(self.root/row['source_path']).read_bytes())

if __name__=='__main__':unittest.main()
