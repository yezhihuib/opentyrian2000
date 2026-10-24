"""Finite current Protron source tests; synthetic edits are not art acceptance.

Small independent fixtures never copy the full asset tree. Transaction tests
isolate source derivation from the separately tested aggregate packaging build;
they assert handled-error rollback, not power-loss atomicity.
"""
import copy
from contextlib import ExitStack
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import portable_history_baselines as history
import current_protron_compatibility as c
import build_current_protron as b
import build_current_craft267 as craft

ART = 'assets/hd/artwork/player-protron-three-v1'
PAIRS = ((80225, 8), (80244, 8), (80226, 8), (1470227, 8))
CELLS = {80225:(187,272,458,544), 80244:(651,38,1373,762),
         80226:(1498,234,1839,569)}
MASTER_SHA = '81ae61eaa6d151d333c819d9bcbeaa1f1c299a2ab709ce817738f0527a517479'


def frozen(name):
    return history.preimage('3c084d6226b8e8241fa7986b976f926669bcb909', name, ROOT)


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True)+'\n').encode()


class CurrentProtronTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.master = frozen(ART+'/sources/generated-master.png')
        cls.masks = {ART+f'/masks/mask-bank8-{i}.png': frozen(ART+f'/masks/mask-bank8-{i}.png')
                     for i in (225,244,226)}
        cls.historical = {}
        for identity, density in PAIRS:
            if identity == 1470227:
                prefix='assets/hd/enemy-protron-p09-v1/'
                png, hda=prefix+'source227.png', prefix+'enemy-protron-p09-227-8.hda'
            else:
                prefix=ART+f'/output/bullet-{identity-80000}-8'
                png,hda=prefix+'.png',prefix+'.hda'
            cls.historical[(identity,density)] = frozen(png),frozen(hda)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='protron-focused-')
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.root=self.base/'root'; self.root.mkdir()
        self.master_path=c.INPUT_ROOT+'/master.png'
        self.recipe_path=c.INPUT_ROOT+'/recipe.json'
        self.write(self.master_path,self.master)
        for name,raw in self.masks.items(): self.write(name,raw)
        recipe=encode(c.RECIPE); self.write(self.recipe_path,recipe)
        self.request=dict(schema=c.CANDIDATE_SCHEMA,version='bootstrap-fixture',
            master=dict(source_png=self.master_path,source_sha256=c.sha(self.master)),
            recipe=dict(path=self.recipe_path,sha256=c.sha(recipe)))

    def write(self,name,raw):
        target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        return target

    def generate(self,request=None):
        return c.generate(self.root,encode(request or self.request),candidate=True)

    def install(self):
        selected,pngs,blobs=self.generate()
        self.write(c.SELECTION,encode(selected))
        for name,raw in pngs.items():self.write(name,raw)
        return selected,pngs,blobs

    def change_cell(self,identity):
        with Image.open(io.BytesIO(self.master)) as im: image=im.copy()
        box=CELLS[identity]
        piece=image.crop(box); channels=piece.split()
        piece=Image.merge('RGBA',(channels[0].point(lambda x:(x+37)%256),*channels[1:]))
        image.paste(piece,box)
        buf=io.BytesIO();image.save(buf,format='PNG');raw=buf.getvalue()
        self.write(self.master_path,raw)
        self.request['master']['source_sha256']=c.sha(raw)

    def test_bootstrap_exact_png_rgba_hda_geometry_and_private_identity(self):
        selected,pngs,blobs=self.generate()
        self.assertEqual(c.sha(self.master),MASTER_SHA)
        self.assertEqual(tuple(c.PAIRS),PAIRS)
        self.assertEqual(set(blobs),set(PAIRS))
        for pair,blob in blobs.items():
            expected_png,expected_hda=self.historical[pair]
            self.assertEqual(blob,expected_hda)
            self.assertEqual(blob[28:],expected_hda[28:])
            self.assertEqual(pngs[c.png(*pair)],expected_png)
            self.assertEqual(struct.unpack('<4s6I',blob[:28]),(b'HDR1',pair[0],8,12,14,0,0))
        alpha=blobs[(1470227,8)][31::4]
        self.assertEqual(sum(0<x<255 for x in alpha),2552) # Bootstrap evidence only.
        self.assertNotIn((80227,8),blobs)
        self.assertEqual(len(selected['resources']),4)

    def test_cell_propagation_matrix_and_unmasked_private_derivative(self):
        _,_,base=self.generate()
        for identity,changed in ((80225,{(80225,8)}),(80244,{(80244,8),(1470227,8)}),(80226,{(80226,8)})):
            with self.subTest(identity=identity):
                self.change_cell(identity)
                _,_,edited=self.generate()
                self.assertEqual({key for key in base if base[key]!=edited[key]},changed)
                if identity == 80244:
                    # Prove the edited shared cell feeds 227 directly, rather
                    # than resizing the already-masked player 244 derivative.
                    with Image.open(self.root/self.master_path) as master:
                        direct=Image.new('RGBA',(96,112))
                        direct.alpha_composite(master.crop(CELLS[80244]).resize(
                            (56,56),Image.Resampling.LANCZOS),(16,24))
                    self.assertEqual(edited[(1470227,8)][28:],direct.tobytes())
                    masked=Image.frombytes('RGBA',(96,112),edited[(80244,8)][28:])
                    wrong=Image.new('RGBA',(96,112))
                    wrong.alpha_composite(masked.crop((0,8,88,96)).resize(
                        (56,56),Image.Resampling.LANCZOS),(16,24))
                    self.assertNotEqual(edited[(1470227,8)][28:],wrong.tobytes())

    def test_installed_derived_bytes_rederived_not_just_rehashed(self):
        selected,pngs,_=self.install()
        self.assertEqual(c.generate(self.root,encode(selected))[0],selected)
        name=next(iter(pngs)); altered=pngs[name]+b'junk'
        self.write(name,altered)
        for row in selected['resources']:
            if row['source_png']==name:row['source_sha256']=c.sha(altered)
        with self.assertRaises(ValueError):c.generate(self.root,encode(selected))

    def test_selection_rejects_wrong_identity_density_role_private_and_paths(self):
        selected,_,_=self.install()
        for field,value in (('identity',80227),('identity',1460227),('identity',True),('density',4),('density',8.0),('source_png',self.master_path)):
            with self.subTest(field=field,value=value):
                bad=copy.deepcopy(selected);bad['resources'][-1][field]=value
                with self.assertRaises(ValueError):c.selection(self.root,encode(bad))
        for field,value in (('role',147),('anchor',[1,0])):
            bad=copy.deepcopy(selected);bad['resources'][-1][field]=value
            with self.assertRaises(ValueError):c.selection(self.root,encode(bad))
        for value in (ART+'/sources/generated-master.png',c.INPUT_ROOT+'/derived/master.png','authoring-inputs/other/master.png','../master.png'):
            bad=copy.deepcopy(self.request);bad['master']['source_png']=value
            with self.assertRaises(ValueError):c.selection(self.root,encode(bad),candidate=True)

    def test_fixed_recipe_rejects_geometry_crop_mask_or_extra_fields(self):
        for key,value in (('anchor',[1,0]),('density',4),('private_identity',80227),('alpha_operation','mask-all')):
            bad=copy.deepcopy(c.RECIPE);bad[key]=value
            with self.assertRaises(ValueError):c.recipe(encode(bad))
        raw=encode(c.RECIPE)
        # One actual coordinate change, not only unknown top-level keys.
        changed=raw.replace(b'187',b'188',1)
        self.assertNotEqual(raw,changed)
        with self.assertRaises(ValueError):c.recipe(changed)
        for name,raw in self.masks.items():
            self.write(name,raw+b'junk')
            with self.assertRaises(ValueError):self.generate()
            self.write(name,raw)

    def test_json_png_and_symlink_fail_closed(self):
        with self.assertRaises(ValueError):c.parse(b'{"schema":"x","schema":"y"}')
        with self.assertRaises(ValueError):c.parse(b'{"number":NaN}')
        for raw in (self.master+b'trailing', self.master[:-8],b'not png'):
            self.write(self.master_path,raw);self.request['master']['source_sha256']=c.sha(raw)
            with self.assertRaises(ValueError):self.generate()
        self.write(self.master_path,self.master)
        self.request['master']['source_sha256']=c.sha(self.master)
        original=self.root/self.master_path;original.unlink()
        target=self.base/'external.png';target.write_bytes(self.master);original.symlink_to(target)
        with self.assertRaises(ValueError):self.generate()

    def test_png_dimensions_mode_animation_and_hash_rejected(self):
        cases=[Image.new('RGBA',(2010,782)),Image.new('RGB',(2011,782))]
        for image in cases:
            stream=io.BytesIO();image.save(stream,format='PNG');raw=stream.getvalue()
            self.write(self.master_path,raw);self.request['master']['source_sha256']=c.sha(raw)
            with self.assertRaises(ValueError):self.generate()
        stream=io.BytesIO()
        Image.new('RGBA',(2011,782)).save(stream,format='PNG',save_all=True,
            append_images=[Image.new('RGBA',(2011,782),(1,2,3,4))],duration=10)
        raw=stream.getvalue();self.write(self.master_path,raw)
        self.request['master']['source_sha256']=c.sha(raw)
        with self.assertRaises(ValueError):self.generate()
        self.write(self.master_path,self.master)
        with self.assertRaises(ValueError):self.generate() # Stale hash is not repinned.

    def test_private_alpha_statistics_are_not_permanent_bootstrap_pins(self):
        with Image.open(io.BytesIO(self.master)) as master:image=master.copy()
        image.paste((10,20,30,127),CELLS[80244])
        stream=io.BytesIO();image.save(stream,format='PNG');raw=stream.getvalue()
        self.write(self.master_path,raw);self.request['master']['source_sha256']=c.sha(raw)
        _,_,blobs=self.generate()
        alpha=blobs[(1470227,8)][31::4]
        self.assertEqual(sum(0<x<255 for x in alpha),56*56)
        self.assertNotEqual(sum(0<x<255 for x in alpha),2552)
        self.assertEqual(alpha[24*96+16],127)

    def test_candidate_dependency_closure_allows_editing_the_single_current_master(self):
        self.install()
        self.change_cell(80244)
        # Only unrelated families are stubbed: exercise this builder's actual
        # current-Protron closure against its now-stale installed selection.
        unrelated=(
            'current_sidekick_body_compatibility.charge_input_paths',
            'current_sidekick_body_compatibility.mf_input_paths',
            'build_enemy_protron_p09.input_paths',
            'build_newshf_hd.input_paths',
            'current_enemy_orb_compatibility.input_paths',
            'current_front_multi_compatibility.input_paths',
            'current_plasma_projectile_compatibility.input_paths',
            'current_sonic_compatibility.input_paths',
            'current_guided_compatibility.input_paths',
        )
        with ExitStack() as stack:
            for target in unrelated:stack.enter_context(patch(target,return_value=set()))
            names=b.dependencies(self.root,self.request)
        self.assertTrue({self.master_path,self.recipe_path,*self.masks}.issubset(names))

    def isolated_derive(self,root,raw):
        selected,pngs,blobs=c.generate(root,raw,candidate=True)
        return {c.SELECTION:encode(selected),**pngs,
                **{c.ROOT+'/'+c.name(*key):value for key,value in blobs.items()}}

    def isolated_dependencies(self,root,selected):
        return {self.master_path,self.recipe_path,*self.masks}

    def stage(self):
        draft=self.base/'request.json';draft.write_bytes(encode(self.request))
        destination=self.base/'stage'
        b.stage(self.root,draft,destination)
        return destination

    def test_stage_tamper_and_stale_source_rejected_without_writes(self):
        with patch.object(b,'derive',self.isolated_derive),patch.object(b,'dependencies',self.isolated_dependencies):
            stage=self.stage()
            before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
            staged=next((stage/'files'/c.INPUT_ROOT/'derived').glob('*.png'))
            original=staged.read_bytes();staged.write_bytes(original+b'bad')
            with self.assertRaises(ValueError):b.apply(self.root,stage)
            staged.write_bytes(original)
            self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
            self.change_cell(80244)
            with self.assertRaises(ValueError):b.apply(self.root,stage)

    def test_plan_changes_output_symlinks_and_preexisting_temporaries_rejected(self):
        with patch.object(b,'derive',self.isolated_derive),patch.object(b,'dependencies',self.isolated_dependencies):
            stage=self.stage()
            plan_path=stage/'plan.json';original=plan_path.read_bytes()
            plan=json.loads(original);plan['files'].append(dict(path='../escape',before_sha256=None,
                after_sha256='0'*64,bytes=0));plan_path.write_bytes(encode(plan))
            with self.assertRaises(ValueError):b.apply(self.root,stage)
            plan_path.write_bytes(original)
            output=self.root/c.SELECTION;output.parent.mkdir(parents=True,exist_ok=True)
            external=self.base/'target.json';external.write_bytes(b'unchanged')
            output.symlink_to(external)
            with self.assertRaises(ValueError):b.apply(self.root,stage)
            self.assertEqual(external.read_bytes(),b'unchanged');output.unlink()
            temporary=output.with_name(output.name+craft.SUFFIX);temporary.write_bytes(b'occupied')
            with self.assertRaises(ValueError):b.apply(self.root,stage)
            self.assertEqual(temporary.read_bytes(),b'occupied')
            self.assertFalse(output.exists())

    def test_handled_write_failure_rolls_back_and_success_updates_four_outputs(self):
        with patch.object(b,'derive',self.isolated_derive),patch.object(b,'dependencies',self.isolated_dependencies):
            stage=self.stage()
            before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
            real=os.replace;calls=[]
            def failing(source,destination):
                calls.append(destination)
                if len(calls)==2:raise OSError('injected bounded write failure')
                return real(source,destination)
            with patch.object(craft.os,'replace',side_effect=failing):
                with self.assertRaises(OSError):b.apply(self.root,stage)
            self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
            self.assertFalse(list(self.root.rglob('*'+craft.SUFFIX)))
            b.apply(self.root,stage)
            self.assertEqual(len(list((self.root/c.ROOT).glob('*.hda'))),4)


if __name__=='__main__':unittest.main()
