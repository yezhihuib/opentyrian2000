"""One Plasma projectile master; isolated synthetic edits, not new acceptance.

Frozen art and gameplay qualification remain independent of mutable selections.
These tests do not extend level/weapon eligibility or qualify Windows/GPU output.
"""
import contextlib
import copy
import hashlib
import io
import json
import os
import struct
import subprocess
import sys
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import build_current_plasma_projectile as b
import current_plasma_projectile_compatibility as c
import build_current_craft267 as craft
import build_current_sidekick_body as body
import current_sidekick_body_compatibility as bodies
import package_runtime as pack
from current_art_policy import PROFILES, profile

# Independent scope, not copied from the implementation's generation policy.
EXPECTED = {(1300022,4):(62,24), (1300022,8):(62,24),
            (1300023,4):(65,28), (1300023,8):(65,28),
            (1300024,4):(62,23), (1300024,8):(62,23)}
ART = 'assets/hd/artwork/option-plasma-projectile-art-v1'
MASTER_SHA = 'de7d4bd38f70e4f19405c5349535f790729b469f1c4e7df9df1afaec186dccb4'
CANDIDATE_SCHEMA = 'opentyrian-current-plasma-projectile-candidate-v1'
INSTALLED_SCHEMA = 'opentyrian-current-plasma-projectile-authoring-v1'


def filename(identity,density):
    return f'option-plasma-projectile-{identity-1300000}-{density}.hda'


def png(size=(1167,1347), mode='RGBA', animated=False):
    stream=io.BytesIO()
    image=Image.new(mode,size,(31,53,71,127) if mode=='RGBA' else (31,53,71))
    if animated:
        image.save(stream,format='PNG',save_all=True,
                   append_images=[Image.new(mode,size,(11,13,17,255))],duration=10)
    else:image.save(stream,format='PNG')
    return stream.getvalue()


def png16():
    def chunk(kind,raw):
        return struct.pack('>I',len(raw))+kind+raw+struct.pack('>I',zlib.crc32(kind+raw)&0xffffffff)
    scanlines=(b'\0'+struct.pack('>4H',31,53,71,65535)*1167)*1347
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1167,1347,16,6,0,0,0))+chunk(b'IDAT',zlib.compress(scanlines))+chunk(b'IEND',b'')


def fnv(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&((1<<64)-1)
    return f'{value:016x}'


class PlasmaProjectileAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_current_sidekick_body_authoring import CurrentSidekickBodyTests
        cls.fixture_class=CurrentSidekickBodyTests
        cls.fixture_class.setUpClass()
        cls.fixture=CurrentSidekickBodyTests()
        cls.root=cls.fixture_class.root
        cls.base=cls.fixture_class.base
        for name in craft.BASES.values():
            for path in (ROOT/'assets/hd/packs'/name).rglob('*'):
                if path.is_file():cls.fixture_class.initial[path.relative_to(ROOT).as_posix()]=path.read_bytes()
        cls.serial=0

    @classmethod
    def tearDownClass(cls):cls.fixture_class.tearDownClass()

    def setUp(self):self.fixture.setUp()

    def selected(self):return json.loads((self.root/c.SELECTION).read_bytes())

    def write(self,name,data):
        path=self.root/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        return path

    def stage(self,request=None):
        type(self).serial+=1
        ordinal=type(self).serial
        draft=self.base/f'plasma-projectile-request-{ordinal}.json'
        draft.write_bytes(b.encoded(request or self.selected()))
        target=self.base/f'plasma-projectile-stage-{ordinal}'
        b.stage(self.root,draft,target)
        return target

    def outputs(self,shared=True):
        names={c.SELECTION,c.MAPPING,c.HEADER}
        if shared:names|={b.RUNTIME,b.BINDING}
        names|={row['source_png'] for row in self.selected()['resources']}
        names|={c.ROOT+'/'+filename(*pair) for pair in EXPECTED}
        return {name:(self.root/name).read_bytes() for name in names}

    def candidate(self):
        selected=self.selected()
        return dict(schema=CANDIDATE_SCHEMA,version=selected['version'],
                    master=copy.deepcopy(selected['master']),recipe=copy.deepcopy(selected['recipe']))

    def changed_master(self,ordinal=1):
        request=self.candidate()
        with Image.open(self.root/request['master']['source_png']) as original:image=original.copy()
        # Change the whole visible master, so all three simultaneous pieces and
        # both density transports must change; never turn generated pieces into inputs.
        channels=image.split()
        changed=Image.merge('RGBA',(channels[0].point(lambda v:(v+7+ordinal)%256),*channels[1:]))
        image=Image.composite(changed,image,channels[3].point(lambda v:255 if v else 0))
        stream=io.BytesIO();image.save(stream,format='PNG');raw=stream.getvalue()
        name=f'authoring-inputs/plasma-projectile-tests/master-{ordinal}.png'
        self.write(name,raw)
        request['master']=dict(source_png=name,source_sha256=b.sha(raw))
        request['version']=f'synthetic-plasma-single-master-{ordinal}'
        return request

    def package(self,*extra):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=pack.main(['--source-root',str(self.root),*map(str,extra)])
        return code,json.loads(output.getvalue())

    def frozen_bootstrap(self):
        # Recreate the historical approval only inside this test-owned root.
        # Legitimate future current selections must not be forced back to old art.
        raw=(ROOT/ART/'sources/generated-plasma-storm9-r1.png').read_bytes()
        self.assertEqual(b.sha(raw),MASTER_SHA)
        master='authoring-inputs/plasma-bootstrap-test/frozen-master.png'
        self.write(master,raw)
        recipe=dict(schema='plasma-projectile-fixed-recipe-v1',master_size=[1167,1347],
                    resize_to=[520,600],resample='Pillow-LANCZOS-RGBA',
                    pieces=[dict(identity=identity,logical_size=[w,h],logical_y=y,anchor=[0,0])
                            for identity,w,h,y in ((1300022,62,24,0),(1300023,65,28,24),(1300024,62,23,52))],
                    densities=[4,8],density4='resize-each-density8-piece-by-half')
        recipe_raw=b.encoded(recipe);recipe_path='authoring-inputs/plasma-bootstrap-test/fixed-recipe.json'
        self.write(recipe_path,recipe_raw)
        request=dict(schema=CANDIDATE_SCHEMA,version='frozen-approved-bootstrap-test-only',
                     master=dict(source_png=master,source_sha256=b.sha(raw)),
                     recipe=dict(path=recipe_path,sha256=b.sha(recipe_raw)))
        b.apply(self.root,self.stage(request))

    def test_approved_bootstrap_master_six_exact_png_hda_and_pins(self):
        self.frozen_bootstrap()
        selected=self.selected()
        raw=(self.root/selected['master']['source_png']).read_bytes()
        self.assertEqual(b.sha(raw),MASTER_SHA)
        self.assertEqual(raw,(ROOT/ART/'sources/generated-plasma-storm9-r1.png').read_bytes())
        self.assertEqual(tuple(c.PAIRS),tuple(EXPECTED))
        self.assertEqual(len(c.input_paths(self.root)),9)
        self.assertEqual(b.check(self.root)['resources'],6)
        binding_raw=(ROOT/ART/'binding.json').read_bytes()
        self.assertEqual(b.sha(binding_raw),'95c493c07c270efaa996db27a39c67a94cd713a9e2f36dca3b30eca62279f426')
        binding=json.loads(binding_raw)
        expected={(row['resource_id'],row['density']):row for row in binding['entries']}
        pins={}
        for row in selected['resources']:
            pair=(row['identity'],row['density']);identity,density=pair;w,h=EXPECTED[pair]
            self.assertEqual(row['source_png'],c.png(*pair))
            encoded=(self.root/row['source_png']).read_bytes()
            frozen=expected[pair]
            self.assertEqual(b.sha(encoded),frozen['PNG_sha256'])
            self.assertEqual(encoded,(ROOT/ART/frozen['output_png']).read_bytes())
            with Image.open(io.BytesIO(encoded)) as image:
                self.assertEqual((image.mode,image.size),('RGBA',(w*density,h*density)))
                payload=image.tobytes()
            raw=(self.root/c.ROOT/filename(*pair)).read_bytes()
            self.assertEqual(raw,struct.pack('<4s6I',b'HDR1',identity,density,w,h,0,0)+payload)
            self.assertEqual(raw,(ROOT/ART/frozen['output_hda']).read_bytes())
            self.assertEqual(b.sha(raw),frozen['HDA_sha256'])
            pins[pair]=fnv(payload)
            self.assertEqual(pins[pair],frozen['RGBA_fnv1a64'])
        header=(self.root/c.HEADER).read_bytes()
        self.assertEqual(header,c.payload_header(pins))
        for (identity,density),digest in pins.items():
            self.assertIn(f'#define CURRENT_PLASMA_PROJECTILE_{identity}_D{density}_PAYLOAD_FNV UINT64_C(0x{digest})'.encode(),header)
        self.assertEqual(len([line for line in header.splitlines() if b'PAYLOAD_FNV UINT64_C' in line]),6)

    def test_frozen_bootstrap_preserves_current_runtime_outside_six_and_binding(self):
        before=json.loads((self.root/b.RUNTIME).read_bytes())
        self.frozen_bootstrap()
        current=json.loads((self.root/b.RUNTIME).read_bytes())
        old={row['destination']:row for row in before['files']}
        new={row['destination']:row for row in current['files']}
        self.assertEqual((len(old),len(new)),(1024,1024))
        self.assertEqual(set(old),set(new))
        destinations={'assets/gameplay/'+filename(*pair) for pair in EXPECTED}
        changed={name for name in old if old[name]!=new[name]}
        self.assertTrue(changed <= destinations|{'CURRENT-PRODUCTION-VALIDATION.json'})
        frozen=json.loads((ROOT/ART/'binding.json').read_bytes())
        for row in frozen['entries']:
            destination='assets/gameplay/'+row['resource_name']
            raw=(ROOT/ART/row['output_hda']).read_bytes()
            self.assertEqual(new[destination]['bytes'],row['HDA_bytes'])
            self.assertEqual(new[destination]['sha256'],row['HDA_sha256'])
            self.assertEqual(new[destination]['git_blob'],hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
            self.assertEqual(new[destination]['source_path'],c.ROOT+'/'+row['resource_name'])
            self.assertEqual(new[destination]['revision'],'current-single-source-plasma-projectile')
            self.assertEqual(new[destination]['group'],'gameplay')
        for destination in set(old)-destinations-{'CURRENT-PRODUCTION-VALIDATION.json'}:
            self.assertEqual(old[destination],new[destination])
        self.assertEqual(len(json.loads((self.root/b.REGISTRY).read_bytes())['resources']),120)
        from verify_current_production import verify
        self.assertEqual(verify(self.root,json.loads((self.root/b.BINDING).read_bytes())),255)

    def test_master_edit_updates_six_outputs_pins_views_and_complete_runtime(self):
        before=self.outputs()
        body_before={row['source_path']:(self.root/row['source_path']).read_bytes() for row in bodies.load(self.root).values()}
        request=self.changed_master()
        snapshot=self.fixture.snapshot()
        stage=self.stage(request)
        self.assertEqual(self.fixture.snapshot(),snapshot,'stage mutated repository')
        b.apply(self.root,stage)
        self.assertEqual(b.check(self.root)['status'],'PASS')
        after=self.outputs()
        self.assertEqual(sum(before[name]!=after[name] for name in before if name.endswith('.hda')),6)
        self.assertEqual(sum(before[name]!=after[name] for name in before if name.endswith('.png')),6)
        self.assertNotEqual(before[c.HEADER],after[c.HEADER])
        self.assertEqual(body_before,{name:(self.root/name).read_bytes() for name in body_before})
        self.assertEqual({name for name in snapshot if b.sha((self.root/name).read_bytes())!=snapshot[name]},set(after))
        old={row['destination']:row for row in json.loads(before[b.RUNTIME])['files']}
        new={row['destination']:row for row in json.loads(after[b.RUNTIME])['files']}
        self.assertEqual(set(old),set(new))
        self.assertEqual({name for name in old if old[name]!=new[name]},
                         {'assets/gameplay/'+filename(*pair) for pair in EXPECTED}|{'CURRENT-PRODUCTION-VALIDATION.json'})
        mapping=c.load(self.root)
        with Image.open(self.root/request['master']['source_png']) as master:
            fitted=master.resize((520,600),Image.Resampling.LANCZOS)
        for identity,y in ((1300022,0),(1300023,24),(1300024,52)):
            w,h=EXPECTED[(identity,8)]
            full=fitted.crop((0,y*8,w*8,(y+h)*8))
            for density in (4,8):
                image=full if density==8 else full.resize((w*4,h*4),Image.Resampling.LANCZOS)
                expected=struct.pack('<4s6I',b'HDR1',identity,density,w,h,0,0)+image.tobytes()
                self.assertEqual((self.root/c.ROOT/filename(identity,density)).read_bytes(),expected)
                with Image.open(self.root/c.png(identity,density)) as derived:
                    self.assertEqual(derived.tobytes(),image.tobytes())
        for kind in ('preview','debug'):
            target=self.base/('plasma-projectile-updated-'+kind)
            report=craft.view(self.root,kind,target)
            self.assertEqual((report['files'],len(report['current_overlays'])),(650,171))
            frozen=self.root/'assets/hd/packs'/craft.BASES[kind]
            nonoverlays=[path for path in frozen.rglob('*') if path.is_file()
                         and path.relative_to(frozen).as_posix() not in report['current_overlays']]
            self.assertEqual(len(nonoverlays),481)
            for path in nonoverlays:self.assertEqual(path.read_bytes(),(target/path.relative_to(frozen)).read_bytes())
            for destination,row in mapping.items():
                self.assertEqual((target/Path(destination).name).read_bytes(),(self.root/row['source_path']).read_bytes())
        code,report=self.package()
        self.assertEqual((code,report['verified_files']),(0,1024))
        target=self.base/'plasma-projectile-runtime-copy'
        evidence=os.environ.get('PLASMA_PROJECTILE_REAL_COPY_OUTPUT')
        if evidence:
            # Explicit cloud copy acceptance retains permission, source, output
            # and free-space guards. Never retry a denied copy elsewhere.
            target=Path(evidence)
            command=[sys.executable,'-B',str(self.root/'scripts/package_runtime.py'),
                     '--source-root',str(self.root),'--build','--output',str(target)]
            result=subprocess.run(command,capture_output=True,text=True)
            receipt=dict(command=command,returncode=result.returncode,stdout=result.stdout,
                         stderr=result.stderr,selection=self.selected(),mapping=list(mapping.values()),
                         scope='Synthetic one-master/six-piece update; two650-file views and real1024-file CLI copy; no game/Windows acceptance')
            with target.with_name(target.name+'-receipt.json').open('xb') as stream:stream.write(b.encoded(receipt))
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            code=result.returncode;report=json.loads(result.stdout)
        else:
            # Portable content-only copy. Real permission acceptance uses opt-in above.
            with patch.object(Path,'chmod',return_value=None):code,report=self.package('--build','--output',target)
        self.assertEqual((code,report['verified_files']),(0,1024))
        self.assertEqual(len(json.loads((target/'RUNTIME-INVENTORY.json').read_bytes())['files']),1024)
        for destination,row in mapping.items():
            self.assertEqual((target/destination).read_bytes(),(self.root/row['source_path']).read_bytes())

    def test_in_place_master_edit_requires_explicit_updated_candidate(self):
        original=self.selected()['master']['source_png'];before=self.outputs()
        request=self.changed_master()
        raw=(self.root/request['master']['source_png']).read_bytes()
        (self.root/original).write_bytes(raw)
        request['master']['source_png']=original
        for action in (lambda:c.load(self.root),lambda:self.package(),lambda:craft.current_overlays(self.root)):
            with self.assertRaises(ValueError):action()
        stage=self.stage(request)
        self.assertEqual(self.outputs(),before)
        b.apply(self.root,stage)
        self.assertEqual(b.check(self.root)['status'],'PASS')
        self.assertEqual(self.selected()['master'],dict(source_png=original,source_sha256=b.sha(raw)))
        self.assertEqual(sum(before[name]!=(self.root/name).read_bytes() for name in before if name.endswith('.hda')),6)

    def test_candidate_cannot_supply_generated_resources_or_executable_recipe(self):
        request=self.candidate()
        for key,value in [('resources',self.selected()['resources']),('generator','candidate.py'),
                          ('geometry',[65,75]),('outputs',[]),('unknown',None)]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                c.generate(self.root,b.encoded(dict(request,**{key:value})),candidate=True)
        installed=self.selected();del installed['resources']
        with self.assertRaises(ValueError):c.generate(self.root,b.encoded(installed))
        with self.assertRaises(ValueError):c.generate(self.root,b.encoded(request))
        with self.assertRaises(ValueError):c.generate(self.root,b.encoded(self.selected()),candidate=True)

    def test_selection_strict_schema_order_identity_density_version_and_hashes(self):
        original=self.selected();mutants=[]
        for key,values in [('identity',(True,1300022.0,1300021)),('density',(True,4.0,2,16))]:
            for value in values:
                row=copy.deepcopy(original);row['resources'][0][key]=value;mutants.append(row)
        for value in ('',None,128,'x'*129):
            row=copy.deepcopy(original);row['version']=value;mutants.append(row)
        for value in ([],original['resources'][:5],list(reversed(original['resources']))):
            row=copy.deepcopy(original);row['resources']=value;mutants.append(row)
        for value in ('x'*64,'A'*64,None):
            for key in ('master','recipe'):
                row=copy.deepcopy(original);row[key]['source_sha256' if key=='master' else 'sha256']=value;mutants.append(row)
        row=copy.deepcopy(original);row['resources'][0]['source_png']='authoring-inputs/independent-piece.png';mutants.append(row)
        row=copy.deepcopy(original);row['resources'][0]['source_sha256']='0'*64;mutants.append(row)
        row=copy.deepcopy(original);row['resources'][0]['anchor']=[0,0];mutants.append(row)
        for ordinal,request in enumerate(mutants):
            with self.subTest(case=ordinal),self.assertRaises(ValueError):c.generate(self.root,b.encoded(request))

    def test_master_and_recipe_paths_are_bounded_regular_independent_inputs(self):
        for key,path_key,suffix in (('master','source_png','.png'),('recipe','path','.json')):
            paths=['../escape'+suffix,'authoring-inputs/../../escape'+suffix,'/tmp/outside'+suffix,
                   'authoring-inputs/../escape'+suffix,'authoring-inputs\\escape'+suffix,
                   'authoring-inputs/a:b'+suffix,'assets/hd/current-compat/fake'+suffix,
                   'authoring-inputs/a/./master'+suffix,'authoring-inputs/CON'+suffix,None]
            if key=='master':paths+=['assets/hd/source/frozen.png','authoring-inputs/master.PNG']
            for source in paths:
                request=self.candidate();request[key][path_key]=source
                with self.subTest(key=key,path=source),self.assertRaises(ValueError):
                    c.generate(self.root,b.encoded(request),candidate=True)
        source=self.root/self.selected()['master']['source_png']
        linked=self.root/'authoring-inputs/plasma-projectile-tests/linked.png'
        linked.parent.mkdir(parents=True,exist_ok=True);linked.symlink_to(source)
        request=self.candidate();request['master']['source_png']=linked.relative_to(self.root).as_posix()
        try:
            with self.assertRaises(ValueError):c.generate(self.root,b.encoded(request),candidate=True)
        finally:linked.unlink()

    def test_generated_pieces_and_casefold_aliases_are_not_editable_sources(self):
        for pair in EXPECTED:
            original=c.png(*pair);raw=(self.root/original).read_bytes()
            alias=Path(original).with_name(Path(original).stem.upper()+'.png').as_posix()
            self.write(alias,raw)
            for source in (original,alias):
                request=self.candidate();request['master']=dict(source_png=source,source_sha256=b.sha(raw))
                with self.subTest(pair=pair,path=source),self.assertRaises(ValueError):
                    c.selection(self.root,b.encoded(request),candidate=True)
        request=self.candidate()
        raw=(self.root/request['master']['source_png']).read_bytes()
        for relative in (c.INPUT_ROOT+'/derived/not-independent.png',
                         c.INPUT_ROOT+'/DERIVED/not-independent.png'):
            self.write(relative,raw)
            request['master']=dict(source_png=relative,source_sha256=b.sha(raw))
            with self.subTest(derived_directory=relative),self.assertRaises(ValueError):
                c.selection(self.root,b.encoded(request),candidate=True)
        # A destination that happens to look like a regular source is still not
        # allowed to turn a generated projectile piece into a body master.
        for pair in EXPECTED:
            source=c.png(*pair);raw=(self.root/source).read_bytes()
            selected=json.loads((self.root/bodies.MF_SELECTION).read_bytes())
            selected['resources'][0].update(source_png=source,source_sha256=b.sha(raw))
            with self.subTest(body_alias=pair),self.assertRaises(ValueError):
                bodies.mf_selection(self.root,b.encoded(selected))

    def test_fixed_data_only_recipe_rejects_every_changed_field_and_json_alias(self):
        request=self.candidate();recipe=json.loads((self.root/request['recipe']['path']).read_bytes())
        for key in recipe:
            mutant=copy.deepcopy(recipe)
            value=mutant[key]
            if isinstance(value,str):mutant[key]=value+'changed'
            elif isinstance(value,list):mutant[key]=list(reversed(value))+[0]
            elif isinstance(value,dict):mutant[key]['injected']=True
            elif isinstance(value,bool):mutant[key]=not value
            elif isinstance(value,(int,float)):mutant[key]=value+1
            else:mutant[key]='changed'
            raw=b.encoded(mutant);name='authoring-inputs/plasma-projectile-tests/recipe.json'
            self.write(name,raw);candidate=copy.deepcopy(request);candidate['recipe']=dict(path=name,sha256=b.sha(raw))
            with self.subTest(field=key),self.assertRaises(ValueError):c.generate(self.root,b.encoded(candidate),candidate=True)
        for raw in (b'{"schema":"a","schema":"b"}',b'{"schema":NaN}',b' '*131073,
                    b.encoded(dict(recipe,generator='untrusted.py'))):
            name='authoring-inputs/plasma-projectile-tests/recipe.json';self.write(name,raw)
            candidate=copy.deepcopy(request);candidate['recipe']=dict(path=name,sha256=b.sha(raw))
            with self.subTest(raw=raw[:48]),self.assertRaises(ValueError):c.generate(self.root,b.encoded(candidate),candidate=True)
        # Type-equal Python values must not bypass the exact integer recipe.
        def replace_first_int(value,replacement):
            if isinstance(value,dict):
                for key,child in value.items():
                    if type(child) is int:value[key]=replacement(child);return True
                    if replace_first_int(child,replacement):return True
            elif isinstance(value,list):
                for index,child in enumerate(value):
                    if type(child) is int:value[index]=replacement(child);return True
                    if replace_first_int(child,replacement):return True
            return False
        mutant=copy.deepcopy(recipe)
        self.assertTrue(replace_first_int(mutant,float))
        raw=b.encoded(mutant);name='authoring-inputs/plasma-projectile-tests/recipe.json';self.write(name,raw)
        request['recipe']=dict(path=name,sha256=b.sha(raw))
        with self.assertRaises(ValueError):c.generate(self.root,b.encoded(request),candidate=True)

    def test_selection_duplicate_nonfinite_and_oversize_rejected(self):
        for raw in (b'{"schema":"a","schema":"b"}',b'{"schema":NaN}',b' '*131073):
            with self.subTest(raw=raw[:48]),self.assertRaises(ValueError):c.generate(self.root,raw,candidate=True)

    def test_png_wrong_geometry_mode_crc_animation_trailing_16bit_and_oversize_rejected(self):
        valid=png();corrupt=bytearray(valid);corrupt[-1]^=1
        unknown=b'EVIL'
        critical=valid[:33]+struct.pack('>I',0)+unknown+struct.pack('>I',zlib.crc32(unknown)&0xffffffff)+valid[33:]
        for ordinal,raw in enumerate((b'not PNG',png((520,600)),png(mode='RGB'),png(animated=True),
                                      valid+b'trailing',bytes(corrupt),valid[:-4],png16(),critical,b'\0'*(16*1024*1024+1))):
            request=self.candidate();name='authoring-inputs/plasma-projectile-tests/invalid.png'
            self.write(name,raw);request['master']=dict(source_png=name,source_sha256=b.sha(raw))
            with self.subTest(case=ordinal),self.assertRaises(ValueError):c.generate(self.root,b.encoded(request),candidate=True)

    def test_rehashed_hand_edited_derived_png_is_rejected_by_all_consumers(self):
        selected=self.selected();row=selected['resources'][0];path=self.root/row['source_png']
        with Image.open(path) as original:image=original.copy()
        image.putpixel((10,10),(7,11,13,255));image.save(path)
        row['source_sha256']=b.sha(path.read_bytes());(self.root/c.SELECTION).write_bytes(b.encoded(selected))
        for entry,action in [('check',lambda:b.check(self.root)),('stage',lambda:self.stage(selected)),
                             ('view',lambda:craft.view(self.root,'preview',self.base/'plasma-forged-view')),
                             ('package',lambda:self.package())]:
            with self.subTest(entry=entry),self.assertRaises(ValueError):action()
        self.assertFalse((self.base/'plasma-forged-view').exists())

    def test_coherently_rehashed_hda_mapping_pins_and_manifest_are_not_source_authority(self):
        mapping=json.loads((self.root/c.MAPPING).read_bytes());row=mapping['files'][0]
        path=self.root/row['source_path'];raw=bytearray(path.read_bytes());raw[-1]^=1;path.write_bytes(raw)
        row['sha256']=b.sha(raw);(self.root/c.MAPPING).write_bytes(b.encoded(mapping))
        pins={(r['identity'],r['density']):fnv((self.root/r['source_path']).read_bytes()[28:]) for r in mapping['files']}
        (self.root/c.HEADER).write_bytes(c.payload_header(pins))
        runtime=json.loads((self.root/b.RUNTIME).read_bytes())
        target=next(r for r in runtime['files'] if r['destination']==row['destination'])
        target['sha256']=b.sha(raw);target['git_blob']=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        (self.root/b.RUNTIME).write_bytes(b.encoded(runtime))
        for action in (lambda:c.load(self.root),lambda:self.package(),lambda:craft.current_overlays(self.root)):
            with self.assertRaises(ValueError):action()

    def test_mapping_requires_exact_identity_density_order_paths_and_version(self):
        path=self.root/c.MAPPING;original=path.read_bytes()
        for mode in ('identity_float','identity_bool','density_float','density_bool','source','destination','missing','order','extra','version'):
            mapping=json.loads(original)
            if mode=='identity_float':mapping['files'][0]['identity']=1300022.0
            elif mode=='identity_bool':mapping['files'][0]['identity']=True
            elif mode=='density_float':mapping['files'][0]['density']=4.0
            elif mode=='density_bool':mapping['files'][0]['density']=True
            elif mode=='source':mapping['files'][0]['source_path']='assets/hd/packs/elsewhere.hda'
            elif mode=='destination':mapping['files'][0]['destination']='assets/gameplay/option-plasma-projectile-25-4.hda'
            elif mode=='missing':mapping['files'].pop()
            elif mode=='order':mapping['files'].reverse()
            elif mode=='extra':mapping['files'][0]['weapon']=88
            else:mapping['version']='not-the-installed-selection'
            path.write_bytes(b.encoded(mapping))
            with self.subTest(mode=mode),self.assertRaises(ValueError):c.load(self.root)
        path.write_bytes(original)

    def test_partial_uppercase_unknown_relabelled_and_dropped_current_package_rejected(self):
        manifest=json.loads((self.root/b.RUNTIME).read_bytes())
        names={filename(*pair) for pair in EXPECTED}
        rows=[row for row in manifest['files'] if Path(row['destination']).name in names]
        self.assertEqual(len(rows),6)
        for mode in ('partial','uppercase','unknown','relabelled'):
            mutant=copy.deepcopy(manifest);mutant['files']=copy.deepcopy(rows)
            if mode=='partial':mutant['files']=mutant['files'][:1]
            elif mode=='uppercase':mutant['files'][0]['destination']=mutant['files'][0]['destination'].upper()
            elif mode=='unknown':mutant['files'][0]['destination']='assets/gameplay/option-plasma-projectile-25-4.hda'
            else:mutant['files'][0]['destination']='assets/gameplay/not-projectile.hda'
            path=self.base/f'plasma-package-{mode}.json';path.write_bytes(b.encoded(mutant))
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.package('--manifest',path)
        manifest['files']=[row for row in manifest['files'] if Path(row['destination']).name not in names]
        path=self.root/b.RUNTIME;original=path.read_bytes();path.write_bytes(b.encoded(manifest))
        try:
            for extra in ((),('--manifest',path)):
                with self.subTest(explicit=bool(extra)),self.assertRaises(ValueError):self.package(*extra)
        finally:path.write_bytes(original)

    def test_explicit_historical_and_generic_packages_need_no_current_family(self):
        names={filename(*pair) for pair in EXPECTED}
        historical=json.loads((self.root/'packaging/runtime-assets-public63a89b3.json').read_bytes())
        historical['files']=[row for row in historical['files'] if Path(row['destination']).name in names]
        self.assertEqual(len(historical['files']),6)
        generic=json.loads((self.root/b.RUNTIME).read_bytes())
        generic['files']=[next(row for row in generic['files'] if row['destination']=='README.txt')]
        isolated=self.base/'plasma-isolated-packager';isolated.mkdir()
        script=isolated/'package_runtime.py';script.write_bytes((self.root/'scripts/package_runtime.py').read_bytes())
        removed={name:(self.root/name).read_bytes() for name in (c.SELECTION,c.MAPPING,c.HEADER)}
        for name in removed:(self.root/name).unlink()
        environment=dict(os.environ);environment.pop('PYTHONPATH',None);environment.pop('PYTHONHOME',None)
        try:
            for kind,manifest,count in (('historical',historical,6),('generic',generic,1)):
                path=self.base/f'plasma-isolated-{kind}.json';path.write_bytes(b.encoded(manifest))
                command=[sys.executable,'-I','-B',str(script),'--source-root',str(self.root),'--manifest',str(path)]
                result=subprocess.run(command,cwd=isolated,env=environment,capture_output=True,text=True)
                with self.subTest(kind=kind):
                    self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                    self.assertEqual(json.loads(result.stdout)['verified_files'],count)
            for name in removed:self.assertFalse((self.root/name).exists())
        finally:
            for name,raw in removed.items():(self.root/name).write_bytes(raw)

    def test_stale_inputs_tool_outputs_request_and_staged_bytes_fail_before_writes(self):
        for mode in ('master','recipe','tool','old_output','mapping','staged_png','staged_hda','missing_staged','request','plan'):
            self.fixture.setUp();request=self.changed_master();stage=self.stage(request)
            if mode=='master':target=self.root/request['master']['source_png']
            elif mode=='recipe':target=self.root/request['recipe']['path']
            elif mode=='tool':target=self.root/'scripts/current_plasma_projectile_compatibility.py'
            elif mode=='old_output':target=self.root/c.ROOT/filename(1300022,4)
            elif mode=='mapping':target=self.root/c.MAPPING
            elif mode=='staged_png':target=stage/'files'/c.png(1300022,4)
            elif mode in ('staged_hda','missing_staged'):target=stage/'files'/c.ROOT/filename(1300022,4)
            elif mode=='request':target=stage/'request.json'
            else:target=stage/'plan.json'
            if mode=='missing_staged':target.unlink()
            elif mode=='tool':target.write_bytes(target.read_bytes()+b'\n# changed fixed Plasma tool\n')
            else:target.write_bytes(target.read_bytes()+b'changed')
            before=self.fixture.snapshot()
            with self.subTest(mode=mode),self.assertRaises((ValueError,OSError)):b.apply(self.root,stage)
            self.assertEqual(self.fixture.snapshot(),before)

    def test_unrelated_global_header_rejected_before_stage_or_binding(self):
        request=self.changed_master()
        header=self.root/'src/global_asset_registry.h'
        header.write_bytes(header.read_bytes()+b'\n#error synthetic unrelated global header drift\n')
        draft=self.base/'plasma-global-header-request.json';draft.write_bytes(b.encoded(request))
        destination=self.base/'plasma-global-header-stage'
        before=self.fixture.snapshot()
        with patch.object(b,'source_inventory',wraps=b.source_inventory) as inventory:
            with self.assertRaisesRegex(ValueError,'Unrelated global pins changed'):
                b.stage(self.root,draft,destination)
            inventory.assert_not_called()
        self.assertFalse(destination.exists())
        self.assertEqual(self.fixture.snapshot(),before)

    def test_unrelated_global_header_after_stage_rejected_before_apply_or_binding(self):
        stage=self.stage(self.changed_master())
        header=self.root/'src/global_asset_registry.h'
        header.write_bytes(header.read_bytes()+b'\n#error synthetic unrelated global header drift\n')
        before=self.fixture.snapshot()
        staged={path.relative_to(stage):path.read_bytes() for path in stage.rglob('*') if path.is_file()}
        with patch.object(b,'source_inventory',wraps=b.source_inventory) as inventory:
            with self.assertRaisesRegex(ValueError,'Unrelated global pins changed'):
                b.apply(self.root,stage)
            inventory.assert_not_called()
        self.assertEqual(self.fixture.snapshot(),before)
        self.assertEqual(staged,{path.relative_to(stage):path.read_bytes() for path in stage.rglob('*') if path.is_file()})

    def test_current_selection_stage_apply_check_is_idempotent(self):
        before=self.fixture.snapshot()
        stage=self.stage()
        self.assertEqual(self.fixture.snapshot(),before)
        b.apply(self.root,stage)
        self.assertEqual(b.check(self.root)['status'],'PASS')
        self.assertEqual(self.fixture.snapshot(),before)

    def test_changed_global_family_composes_with_plasma_without_reverting_pins(self):
        import build_current_art as art
        selected=json.loads((self.root/profile('pulse')['selection']).read_bytes())
        row=selected['resources'][0]
        with Image.open(self.root/row['source_png']) as original:size=original.size
        raw=png(size);source='assets/hd/authoring/plasma-global-family.png';self.write(source,raw)
        row.update(source_png=source,source_sha256=b.sha(raw));selected['version']='synthetic-plasma-global-family'
        draft=self.base/'plasma-global-family-request.json';draft.write_bytes(b.encoded(selected))
        stage=self.base/'plasma-global-family-stage'
        original=(self.root/'src/global_asset_registry.h').read_bytes()
        art.stage(self.root,draft,stage,'pulse');art.apply(self.root,stage,'pulse')
        global_names=(b.REGISTRY,'src/global_asset_registry.h',b.LEGACY_HEADER,profile('pulse')['selection'],profile('pulse')['mapping'])
        global_before={name:(self.root/name).read_bytes() for name in global_names}
        self.assertNotEqual(global_before['src/global_asset_registry.h'],original)
        b.apply(self.root,self.stage(self.changed_master()))
        self.assertEqual(b.check(self.root)['status'],'PASS')
        self.assertEqual(art.check(self.root,'pulse')['status'],'PASS')
        self.assertEqual(global_before,{name:(self.root/name).read_bytes() for name in global_names})
        self.assertEqual(len(json.loads((self.root/b.REGISTRY).read_bytes())['resources']),120)
        from verify_current_production import verify
        self.assertEqual(verify(self.root,json.loads((self.root/b.BINDING).read_bytes())),255)
        code,report=self.package();self.assertEqual((code,report['verified_files']),(0,1024))

    def test_plan_duplicate_nonfinite_oversize_and_numeric_type_rejected(self):
        stage=self.stage();path=stage/'plan.json';original=path.read_bytes();before=self.outputs()
        plans=[b'{"schema":"a","schema":"b"}',b'{"x":NaN}',b' '*131073]
        numeric=json.loads(original);numeric['files'][0]['bytes']=float(numeric['files'][0]['bytes']);plans.append(b.encoded(numeric))
        for ordinal,raw in enumerate(plans):
            path.write_bytes(raw)
            with self.subTest(case=ordinal),self.assertRaises(ValueError):b.apply(self.root,stage)
            self.assertEqual(self.outputs(),before)
        path.write_bytes(original)

    def test_temporary_collision_symlink_output_and_internal_stage_rejected(self):
        stage=self.stage(self.changed_master())
        temporary=self.root/(c.MAPPING+craft.SUFFIX);temporary.write_bytes(b'occupied')
        before=self.fixture.snapshot()
        with self.assertRaises(ValueError):b.apply(self.root,stage)
        self.assertEqual(self.fixture.snapshot(),before);temporary.unlink()
        linked=self.base/'plasma-stage-link';linked.symlink_to(stage,target_is_directory=True)
        try:
            with self.assertRaises(ValueError):b.apply(self.root,linked)
        finally:linked.unlink()
        with self.assertRaises(ValueError):b.stage(self.root,self.root/c.SELECTION,self.root/'forbidden-stage')
        self.assertFalse((self.root/'forbidden-stage').exists())
        path=self.root/c.ROOT/filename(1300022,4);held=path.with_name('held-original.hda')
        path.rename(held);path.symlink_to(held)
        try:
            with self.assertRaises(ValueError):b.apply(self.root,stage)
        finally:path.unlink();held.rename(path)

    def test_handled_replace_failure_rolls_back_all_changed_outputs(self):
        stage=self.stage(self.changed_master());before=self.fixture.snapshot()
        replace=os.replace;calls=0
        def failing(source,target):
            nonlocal calls
            calls+=1
            if calls==4:raise OSError('synthetic fourth replacement failure')
            return replace(source,target)
        with patch.object(craft.os,'replace',side_effect=failing):
            with self.assertRaisesRegex(OSError,'synthetic fourth'):b.apply(self.root,stage)
        self.assertGreaterEqual(calls,7,'expected rollback for all three preceding replacements')
        self.assertEqual(self.fixture.snapshot(),before)

    def test_all_twenty_one_existing_checks_accept_changed_plasma_without_mutation(self):
        import build_current_art as art
        import build_current_hud as hud
        import build_current_tank_shell as tank
        import build_current_enemy_energy as energy
        b.apply(self.root,self.stage(self.changed_master()))
        before=self.outputs();count=0
        for family in PROFILES:
            with self.subTest(family=family):self.assertEqual(art.check(self.root,family)['status'],'PASS')
            count+=1
        for name,check in [('hud',hud.check),('tank',tank.check),('energy',energy.check),
                           ('sidekick',body.check),('craft267',craft.check),
                           ('charge',body.charge_check),('mint-front',body.mf_check)]:
            with self.subTest(family=name):self.assertEqual(check(self.root)['status'],'PASS')
            count+=1
        self.assertEqual(count,21)
        self.assertEqual(self.outputs(),before)

    def test_changed_charge_plasma_mint_front_plasma_roundtrip_is_isolated(self):
        def family_outputs(selection,mapping,root,name,ids):
            selected=json.loads((self.root/selection).read_bytes())
            paths={selection,mapping}|{root+'/'+name(identity) for identity in ids}
            if 'master' in selected:paths|={row['source_png'] for row in selected['resources']}
            return {path:(self.root/path).read_bytes() for path in paths}
        charge_selected=json.loads((self.root/bodies.CHARGE_SELECTION).read_bytes())
        with Image.open(self.root/charge_selected['master']['source_png']) as original:image=original.copy()
        xy=next((x,y) for y in range(80,110) for x in range(1,95) if image.getpixel((x,y))[3]>0)
        rgba=image.getpixel(xy);image.putpixel(xy,((rgba[0]+3)%256,*rgba[1:]))
        stream=io.BytesIO();image.save(stream,format='PNG');raw=stream.getvalue()
        master='authoring-inputs/plasma-cross-family/charge-master.png';self.write(master,raw)
        recipe=json.loads((self.root/charge_selected['recipe']['path']).read_bytes());recipe['master_sha256']=b.sha(raw)
        recipe_raw=b.encoded(recipe);recipe_path='authoring-inputs/plasma-cross-family/charge-recipe.json';self.write(recipe_path,recipe_raw)
        request=dict(schema=bodies.CHARGE_CANDIDATE_SCHEMA,version='synthetic-plasma-cross-charge',
                     master=dict(source_png=master,source_sha256=b.sha(raw)),recipe=dict(path=recipe_path,sha256=b.sha(recipe_raw)))
        draft=self.base/'plasma-cross-charge.json';draft.write_bytes(b.encoded(request));stage=self.base/'plasma-cross-charge-stage'
        before=self.outputs(shared=False)
        body.charge_stage(self.root,draft,stage);body.charge_apply(self.root,stage)
        self.assertEqual(self.outputs(shared=False),before)
        charge_before=family_outputs(bodies.CHARGE_SELECTION,bodies.CHARGE_MAPPING,bodies.CHARGE_ROOT,bodies.charge_name,bodies.CHARGE_IDS)
        b.apply(self.root,self.stage(self.changed_master(1)))
        self.assertEqual(charge_before,family_outputs(bodies.CHARGE_SELECTION,bodies.CHARGE_MAPPING,bodies.CHARGE_ROOT,bodies.charge_name,bodies.CHARGE_IDS))
        plasma_before=self.outputs(shared=False)
        selected=json.loads((self.root/bodies.MF_SELECTION).read_bytes());row=selected['resources'][3]
        with Image.open(self.root/row['source_png']) as original:image=original.copy()
        xy=next((x,y) for y in range(image.height) for x in range(image.width) if image.getpixel((x,y))[3]>0)
        rgba=image.getpixel(xy);image.putpixel(xy,((rgba[0]+3)%256,*rgba[1:]))
        stream=io.BytesIO();image.save(stream,format='PNG');raw=stream.getvalue()
        source='authoring-inputs/plasma-cross-family/front.png';self.write(source,raw)
        row.update(source_png=source,source_sha256=b.sha(raw));selected['version']='synthetic-plasma-cross-front'
        draft=self.base/'plasma-cross-front.json';draft.write_bytes(b.encoded(selected));stage=self.base/'plasma-cross-front-stage'
        body.mf_stage(self.root,draft,stage);body.mf_apply(self.root,stage)
        self.assertEqual(self.outputs(shared=False),plasma_before)
        mf_before=family_outputs(bodies.MF_SELECTION,bodies.MF_MAPPING,bodies.MF_ROOT,bodies.mf_name,bodies.MF_IDS)
        b.apply(self.root,self.stage(self.changed_master(2)))
        self.assertEqual(mf_before,family_outputs(bodies.MF_SELECTION,bodies.MF_MAPPING,bodies.MF_ROOT,bodies.mf_name,bodies.MF_IDS))
        self.assertEqual(charge_before,family_outputs(bodies.CHARGE_SELECTION,bodies.CHARGE_MAPPING,bodies.CHARGE_ROOT,bodies.charge_name,bodies.CHARGE_IDS))
        self.assertEqual(body.charge_check(self.root)['status'],'PASS')
        self.assertEqual(body.mf_check(self.root)['status'],'PASS')
        self.assertEqual(b.check(self.root)['status'],'PASS')
        code,report=self.package();self.assertEqual((code,report['verified_files']),(0,1024))

    def test_new_plasma_tools_are_fingerprinted_and_invalidate_legacy_plan(self):
        tools=('scripts/current_plasma_projectile_compatibility.py',
               'scripts/build_current_plasma_projectile.py')
        fingerprints=bodies.authoring_input_fingerprints(self.root)
        for name in tools:
            self.assertEqual(fingerprints[name],b.sha((self.root/name).read_bytes()))
        # One representative legacy transport workflow uses the shared finite
        # fingerprint helper; reuse one unchanged stage for both tool drifts.
        stage=self.base/'plasma-tool-drift-legacy-stage'
        body.stage(self.root,self.root/body.SELECTION,stage)
        for name in tools:
            path=self.root/name;original=path.read_bytes()
            path.write_bytes(original+b'\n# synthetic fixed Plasma tool drift\n')
            before=self.fixture.snapshot()
            try:
                with self.subTest(tool=name),self.assertRaisesRegex(ValueError,'Stale or modified'):
                    body.apply(self.root,stage)
                self.assertEqual(self.fixture.snapshot(),before)
            finally:path.write_bytes(original)

    def test_plasma_input_drift_invalidates_legacy_charge_and_mint_front_plans(self):
        import build_current_art as art
        import build_current_hud as hud
        import build_current_tank_shell as tank
        import build_current_enemy_energy as energy
        workflows=[('art',art.stage,art.apply,profile('pulse')['selection']),
                   ('hud',hud.stage,hud.apply,hud.SELECTION),('tank',tank.stage,tank.apply,tank.SELECTION),
                   ('energy',energy.stage,energy.apply,energy.SELECTION),('sidekick',body.stage,body.apply,body.SELECTION),
                   ('craft267',craft.stage,craft.apply,craft.SELECTION),
                   ('charge',body.charge_stage,body.charge_apply,bodies.CHARGE_SELECTION),
                   ('mint-front',body.mf_stage,body.mf_apply,bodies.MF_SELECTION)]
        for name,stage_fn,apply_fn,selection in workflows:
            self.fixture.setUp();stage=self.base/('plasma-dependent-'+name)
            stage_fn(self.root,self.root/selection,stage)
            selected=self.selected();source=self.root/selected['master']['source_png']
            source.write_bytes(source.read_bytes()+b'\n')
            before=self.fixture.snapshot()
            with self.subTest(family=name),self.assertRaises(ValueError):apply_fn(self.root,stage)
            self.assertEqual(self.fixture.snapshot(),before)


if __name__=='__main__':unittest.main(verbosity=2)
