"""Finite current Guided tests; synthetic edits do not qualify new artwork.

Bootstrap expectations come from the frozen public Git tree. Transaction tests
use isolated derivation and dependency mocks, not the aggregate runtime build;
they prove handled-error rollback, not process-crash/power-loss atomicity.
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
import zlib

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import current_guided_compatibility as c
import build_current_guided as b
import build_current_craft267 as craft
from build_current_art import fnv

BASE = 'e5fac6ce2a739ad2e0d6e8f99edaec56411e6e7a'
ART = 'assets/hd/artwork/guided-bomb-family-v1'
PAIRS = ((80019,8),(80171,8),(80020,8),(80021,8))
SELECTORS=(19,171,20,21)
CONTRACT=json.loads(subprocess.check_output(['git','show',BASE+':'+ART+'/candidate-manifest.json'],cwd=ROOT))
MASTER_SHA={f['sprite_id']:f['master_sha256'] for f in CONTRACT['frames']}
SIZES={19:(1160,1355),171:(1160,1355),20:(1060,1484),21:(938,1677)}


def frozen(name):
    return subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)


def encode(value):
    return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()


class CurrentGuidedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.masters={f['sprite_id']:frozen(ART+'/'+f['master']) for f in CONTRACT['frames']}
        cls.historical={pair:frozen('assets/hd/packs/packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test/'+c.name(*pair)) for pair in PAIRS}
        cls.contract=CONTRACT

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='guided-focused-')
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.root=self.base/'root';self.root.mkdir()
        self.master_paths={i:c.INPUT_ROOT+f'/master-{i}.png' for i in SELECTORS}
        for i,raw in self.masters.items():self.write(self.master_paths[i],raw)
        self.recipe_path=c.INPUT_ROOT+'/recipe.json'
        recipe=encode(c.RECIPE);self.write(self.recipe_path,recipe)
        self.request=dict(schema=c.CANDIDATE_SCHEMA,version='bootstrap-fixture',
            masters=[dict(selector=i,source_png=self.master_paths[i],source_sha256=c.sha(self.masters[i])) for i in SELECTORS],
            recipe=dict(path=self.recipe_path,sha256=c.sha(recipe)))

    def write(self,name,raw):
        target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        return target

    def generate(self,request=None):
        return c.generate(self.root,encode(request or self.request),candidate=True)

    def install(self):
        selected,pngs,blobs=self.generate();self.write(c.SELECTION,encode(selected))
        for name,raw in pngs.items():self.write(name,raw)
        rows=[]
        for pair,raw in blobs.items():
            name=c.ROOT+'/'+c.name(*pair);self.write(name,raw)
            rows.append(dict(identity=pair[0],density=pair[1],source_path=name,
                destination='assets/gameplay/'+c.name(*pair),sha256=c.sha(raw)))
        self.write(c.MAPPING,encode(dict(schema='opentyrian-current-guided-compatibility-v1',
            selection=c.SELECTION,version=selected['version'],files=rows)))
        self.write(c.HEADER,c.payload_header({pair:fnv(raw[28:]) for pair,raw in blobs.items()}))
        return selected,pngs,blobs

    def change_master(self,selector):
        with Image.open(io.BytesIO(self.masters[selector])) as original:
            channels=original.split()
            image=Image.merge('RGBA',(channels[0].point(lambda x:(x+37)%256),*channels[1:]))
        stream=io.BytesIO();image.save(stream,format='PNG');raw=stream.getvalue()
        self.write(self.master_paths[selector],raw)
        for row in self.request['masters']:
            if row['selector']==selector:row['source_sha256']=c.sha(raw)

    def snapshot(self):
        return {p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def test_bootstrap_exact_png_rgba_hda_geometry_and_alpha(self):
        selected,pngs,blobs=self.generate()
        self.assertEqual(c.PAIRS,PAIRS)
        for i,raw in self.masters.items():self.assertEqual(c.sha(raw),MASTER_SHA[i])
        for pair,raw in blobs.items():
            old_hda=self.historical[pair]
            entry=next(f for f in self.contract['frames'] if f['runtime_asset_key']==pair[0])
            self.assertEqual(raw,old_hda);self.assertEqual(raw[28:],old_hda[28:])
            self.assertEqual(c.sha(raw),entry['hda_sha256'])
            self.assertEqual(c.sha(pngs[c.png(*pair)]),entry['source_png_sha256'])
            self.assertEqual(struct.unpack('<4s6I',raw[:28]),(b'HDR1',pair[0],8,12,14,0,0))
            with Image.open(io.BytesIO(pngs[c.png(*pair)])) as im:self.assertEqual(im.tobytes(),raw[28:])
        self.assertEqual(len(selected['resources']),4)

    def test_four_independent_static_fixed_crop_and_placement(self):
        _,_,blobs=self.generate()
        for spec in c.RECIPE['pieces']:
            with Image.open(io.BytesIO(self.masters[spec['selector']])) as master:
                piece=Image.new('RGBA',(96,112))
                piece.paste(master.crop(tuple(spec['crop'])).resize(tuple(spec['size']),Image.Resampling.LANCZOS),tuple(spec['xy']))
            self.assertEqual(piece.tobytes(),blobs[(spec['identity'],8)][28:])
        self.assertEqual(len(set(blobs.values())),4)
        self.assertNotIn((80022,8),blobs)

    def test_each_master_edit_propagates_only_to_own_static_identity(self):
        _,_,before=self.generate()
        for selector in SELECTORS:
            with self.subTest(selector=selector):
                for i,raw in self.masters.items():self.write(self.master_paths[i],raw)
                for row in self.request['masters']:row['source_sha256']=c.sha(self.masters[row['selector']])
                self.change_master(selector);_,_,after=self.generate()
                self.assertEqual({pair for pair in PAIRS if before[pair]!=after[pair]},{(80000+selector,8)})

    def test_alpha_is_preserved_not_historical_occupancy_or_threshold_clipped(self):
        for row in self.request['masters']:
            image=Image.new('RGBA',SIZES[row['selector']],(10,20,30,127))
            stream=io.BytesIO();image.save(stream,format='PNG');raw=stream.getvalue()
            self.write(row['source_png'],raw);row['source_sha256']=c.sha(raw)
        _,_,blobs=self.generate()
        for pair,raw in blobs.items():
            alpha=raw[31::4];spec=next(p for p in c.RECIPE['pieces'] if p['identity']==pair[0]);occupied=spec['size'][0]*spec['size'][1]
            self.assertEqual(alpha.count(127),occupied)
            self.assertEqual(set(alpha),{0,127})
            self.assertNotEqual(raw,self.historical[pair])

    def test_installed_derived_bytes_are_rederived_not_merely_rehashed(self):
        selected,pngs,_=self.install()
        self.assertEqual(c.generate(self.root,encode(selected))[0],selected)
        name=next(iter(pngs));self.write(name,pngs[name]+b'junk')
        for row in selected['resources']:
            if row['source_png']==name:row['source_sha256']=c.sha(pngs[name]+b'junk')
        with self.assertRaises(ValueError):c.generate(self.root,encode(selected))

    def test_selection_strict_identity_density_order_path_and_fields(self):
        selected,_,_=self.install()
        for field,value in (('identity',80022),('identity',True),('identity',80019.0),('density',4),('density',True),('density',8.0),('source_png',self.master_paths[19]),('role',146)):
            bad=copy.deepcopy(selected);bad['resources'][0][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):c.selection(self.root,encode(bad))
        for collection in ('resources','masters'):
            bad=copy.deepcopy(selected);bad[collection].reverse()
            with self.assertRaises(ValueError):c.selection(self.root,encode(bad))
        for field,value in (('selector',True),('selector',19.0),('selector',22),('source_png',ART+'/sources/generated-guided19-r3.png'),('source_png','../master.png'),('source_sha256','0'*64),('unknown',0)):
            bad=copy.deepcopy(self.request);bad['masters'][0][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):c.selection(self.root,encode(bad),candidate=True)
        for value in ('',True,123,'x'*129):
            bad=copy.deepcopy(self.request);bad['version']=value
            with self.assertRaises(ValueError):c.selection(self.root,encode(bad),candidate=True)

    def test_fixed_recipe_rejects_geometry_alpha_static_and_numeric_type_changes(self):
        for key,value in (('anchor',[1,0]),('density',8.0),('density',True),('relationship','mirrors'),('alpha','threshold'),('extra','x')):
            bad=copy.deepcopy(c.RECIPE);bad[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):c.recipe(encode(bad))
        for key,value in (('xy',[0,15]),('size',[96,95]),('source_size',[1253,1254]),('identity',80022),('crop',[75,180,1086,1173])):
            bad=copy.deepcopy(c.RECIPE);bad['pieces'][0][key]=value
            with self.assertRaises(ValueError):c.recipe(encode(bad))

    def test_duplicate_nonfinite_and_oversize_json_rejected(self):
        for raw in (b'{"schema":"x","schema":"y"}',b'{"nested":{"x":1,"x":2}}',
                    b'{"x":NaN}',b'{"x":Infinity}',b'{"x":-Infinity}',b' '*131073):
            with self.subTest(raw=raw[:50]),self.assertRaises(ValueError):c.parse(raw)

    def test_png_crc_truncation_trailing_mode_dimensions_and_animation_rejected(self):
        raw=self.masters[19];crc_bad=bytearray(raw);crc_bad[29]^=1
        cases=[raw+b'trailing',raw[:-8],bytes(crc_bad),b'not png']
        for picture in (Image.new('RGB',SIZES[19]),Image.new('RGBA',(1253,1254))):
            stream=io.BytesIO();picture.save(stream,format='PNG');cases.append(stream.getvalue())
        stream=io.BytesIO()
        Image.new('RGBA',SIZES[19]).save(stream,format='PNG',save_all=True,
            append_images=[Image.new('RGBA',SIZES[19],(1,2,3,4))],duration=10)
        cases.append(stream.getvalue())
        for raw in cases:
            with self.subTest(length=len(raw)),self.assertRaises(ValueError):c.image(raw,SIZES[19])

    def test_input_symlink_and_stale_master_hash_rejected(self):
        self.change_master(19)
        stale=copy.deepcopy(self.request);stale['masters'][0]['source_sha256']=MASTER_SHA[19]
        with self.assertRaises(ValueError):self.generate(stale)
        original=self.root/self.master_paths[19];original.unlink()
        target=self.base/'external.png';target.write_bytes(self.masters[19]);original.symlink_to(target)
        self.request['masters'][0]['source_sha256']=MASTER_SHA[19]
        with self.assertRaises(ValueError):self.generate()

    def test_load_rejects_stale_transport_mapping_and_header(self):
        selected,pngs,blobs=self.install()
        self.assertEqual(len(c.load(self.root)),4)
        for name in (c.HEADER,c.MAPPING,c.ROOT+'/'+c.name(80019,8)):
            raw=(self.root/name).read_bytes();self.write(name,raw+b'bad')
            with self.subTest(name=name),self.assertRaises(ValueError):c.load(self.root)
            self.write(name,raw)
        mapping=json.loads((self.root/c.MAPPING).read_bytes());mapping['files'][0]['destination']='assets/gameplay/other.hda'
        self.write(c.MAPPING,encode(mapping))
        with self.assertRaises(ValueError):c.load(self.root)
        self.assertEqual(c.input_paths(self.root), {
            'assets/hd/authoring/guided-current.json',
            'authoring-inputs/guided-current/recipe.json',
            *{f'authoring-inputs/guided-current/master-{n}.png' for n in SELECTORS},
            *{f'authoring-inputs/guided-current/derived/bullet-{n}-8.png' for n in SELECTORS},
            *{f'assets/hd/current-compat/guided/bullet-{n}-8.hda' for n in SELECTORS},
        })
        self.assertFalse(any(name.startswith(ART) for name in c.input_paths(self.root)))

    def test_header_has_only_existing_enemy_20_21_pins(self):
        _,_,blobs=self.install()
        header=(self.root/c.HEADER).read_text()
        self.assertIn('CURRENT_GUIDED_80020_D8_PAYLOAD_FNV',header)
        self.assertIn('CURRENT_GUIDED_80021_D8_PAYLOAD_FNV',header)
        self.assertNotIn('80019_D8',header);self.assertNotIn('80171_D8',header)
        with self.assertRaises(ValueError):c.payload_header({p:fnv(raw[28:]) for p,raw in blobs.items() if p[0]!=80019})

    def test_actual_dependency_closure_allows_edited_masters_with_stale_installed_hashes(self):
        self.install();self.change_master(19)
        # The aircraft migration replaced the old NEWSHF closure. Copy only its
        # finite validated inputs; keep the real current closure in this test.
        import current_newshf_compatibility as aircraft
        aircraft.load(ROOT)
        aircraft_names=aircraft.input_paths(ROOT)
        self.assertEqual(len(aircraft_names),41)
        for name in aircraft_names:self.write(name,(ROOT/name).read_bytes())
        aircraft.load(self.root)
        import current_rear_p7_compatibility as rear_p7
        rear_p7.load(ROOT)
        rear_names=rear_p7.input_paths(ROOT)
        self.assertEqual(len(rear_names),11)
        for name in rear_names:self.write(name,(ROOT/name).read_bytes())
        rear_p7.input_paths(self.root)
        # Mint27 adds one independent finite family; retain its real closure.
        import current_missile_compatibility as missile
        missile.load(ROOT)
        missile_names=missile.input_paths(ROOT)
        self.assertEqual(len(missile_names),11)
        for name in missile_names:self.write(name,(ROOT/name).read_bytes())
        missile.input_paths(self.root)
        import current_mint27_compatibility as mint27
        mint27.load(ROOT)
        mint27_names=mint27.input_paths(ROOT)
        self.assertEqual(len(mint27_names),5)
        for name in mint27_names:self.write(name,(ROOT/name).read_bytes())
        mint27.input_paths(self.root)
        # Other unrelated family closures are stubbed; this builder's own Guided
        # closure must accept proposed sources without validating old selection.
        unrelated=('current_sidekick_body_compatibility.charge_input_paths',
            'current_sidekick_body_compatibility.mf_input_paths','build_enemy_protron_p09.input_paths',
            'current_enemy_orb_compatibility.input_paths',
            'current_front_multi_compatibility.input_paths','current_plasma_projectile_compatibility.input_paths',
            'current_protron_compatibility.input_paths','current_sonic_compatibility.input_paths')
        with ExitStack() as stack:
            for target in unrelated:stack.enter_context(patch(target,return_value=set()))
            names=b.dependencies(self.root,self.request)
        self.assertTrue({*self.master_paths.values(),self.recipe_path}.issubset(names))
        self.assertTrue(aircraft_names.issubset(names))
        self.assertTrue(rear_names.issubset(names))
        self.assertTrue(mint27_names.issubset(names))
        self.assertTrue(missile_names.issubset(names))

    def isolated_derive(self,root,raw):
        selected,pngs,blobs=c.generate(root,raw,candidate=True)
        return {c.SELECTION:encode(selected),**pngs,
                **{c.ROOT+'/'+c.name(*pair):blob for pair,blob in blobs.items()}}

    def isolated_dependencies(self,root,selected):
        return {*self.master_paths.values(),self.recipe_path}

    def stage(self):
        draft=self.base/'request.json';draft.write_bytes(encode(self.request))
        destination=self.base/'stage';b.stage(self.root,draft,destination)
        return destination

    def test_stage_tamper_and_stale_source_rejected_without_writes(self):
        with patch.object(b,'derive',self.isolated_derive),patch.object(b,'dependencies',self.isolated_dependencies):
            stage=self.stage();before=self.snapshot()
            staged=next((stage/'files'/c.INPUT_ROOT/'derived').glob('*.png'))
            raw=staged.read_bytes();staged.write_bytes(raw+b'bad')
            with self.assertRaises(ValueError):b.apply(self.root,stage)
            staged.write_bytes(raw);self.assertEqual(before,self.snapshot())
            self.change_master(19)
            with self.assertRaises(ValueError):b.apply(self.root,stage)

    def test_stage_path_plan_symlink_and_temporary_rejections(self):
        with patch.object(b,'derive',self.isolated_derive),patch.object(b,'dependencies',self.isolated_dependencies):
            draft=self.base/'request.json';draft.write_bytes(encode(self.request))
            with self.assertRaises(ValueError):b.stage(self.root,draft,self.root/'stage')
            occupied=self.base/'occupied';occupied.mkdir()
            with self.assertRaises(ValueError):b.stage(self.root,draft,occupied)
            stage=self.stage();plan_path=stage/'plan.json';raw=plan_path.read_bytes()
            plan=json.loads(raw);plan['files'].append(dict(path='../escape',before_sha256=None,after_sha256='0'*64,bytes=0))
            plan_path.write_bytes(encode(plan))
            with self.assertRaises(ValueError):b.apply(self.root,stage)
            plan_path.write_bytes(raw)
            output=self.root/c.SELECTION;output.parent.mkdir(parents=True,exist_ok=True)
            external=self.base/'target';external.write_bytes(b'unchanged');output.symlink_to(external)
            with self.assertRaises(ValueError):b.apply(self.root,stage)
            self.assertEqual(external.read_bytes(),b'unchanged');output.unlink()
            temporary=output.with_name(output.name+craft.SUFFIX);temporary.write_bytes(b'occupied')
            with self.assertRaises(ValueError):b.apply(self.root,stage)
            self.assertEqual(temporary.read_bytes(),b'occupied');self.assertFalse(output.exists())

    def test_handled_write_failure_rolls_back_and_success_installs_four_hda(self):
        with patch.object(b,'derive',self.isolated_derive),patch.object(b,'dependencies',self.isolated_dependencies):
            stage=self.stage();before=self.snapshot();real=os.replace;calls=[]
            def failing(source,destination):
                calls.append(destination)
                if len(calls)==2:raise OSError('injected bounded write failure')
                return real(source,destination)
            with patch.object(craft.os,'replace',side_effect=failing):
                with self.assertRaises(OSError):b.apply(self.root,stage)
            self.assertEqual(before,self.snapshot());self.assertFalse(list(self.root.rglob('*'+craft.SUFFIX)))
            b.apply(self.root,stage)
            self.assertEqual(len(list((self.root/c.ROOT).glob('*.hda'))),4)
            selected=json.loads((self.root/c.SELECTION).read_bytes())
            self.assertEqual(len(selected['resources']),4)


if __name__=='__main__':unittest.main()
