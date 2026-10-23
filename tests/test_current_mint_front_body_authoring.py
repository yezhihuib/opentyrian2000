"""Four independent approved body sources; synthetic mutations stay in fixtures.

This authoring suite is not new-art, gameplay, Windows or GPU qualification.
Frozen approval evidence remains separate from current mutable selections.
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
import build_current_sidekick_body as b
import current_sidekick_body_compatibility as c
import build_current_craft267 as craft
import package_runtime as pack
from current_art_policy import PROFILES, profile

# Independent literal scope; do not derive expectations from the production policy.
EXPECTED = {
    1270112: ('option-mint-bank9-112-8.hda', 12, 14),
    1270131: ('option-mint-bank9-131-8.hda', 12, 14),
    1270150: ('option-mint-bank9-150-8.hda', 12, 14),
    1280083: ('option-frontblaster-bank10-83-8.hda', 24, 28),
}
BOOTSTRAP_SHA = 'e399731f7d724c7b8f6cf65f2da91528fe9256f1ccfce984d37024d848c138ca'


def png(size=(96,112), mode='RGBA', animated=False):
    stream = io.BytesIO()
    image = Image.new(mode, size, (31,53,71,127) if mode=='RGBA' else (31,53,71))
    if animated:
        image.save(stream, format='PNG', save_all=True,
                   append_images=[Image.new(mode, size, (11,13,17,255))], duration=10)
    else:
        image.save(stream, format='PNG')
    return stream.getvalue()


def png16(size=(96,112)):
    def chunk(kind, body):
        return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff)
    w,h=size
    scanlines=(b'\0'+struct.pack('>4H',31,53,71,65535)*w)*h
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,16,6,0,0,0))+chunk(b'IDAT',zlib.compress(scanlines))+chunk(b'IEND',b'')


class MintFrontBodyAuthoringTests(unittest.TestCase):
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
                if path.is_file():
                    cls.fixture_class.initial[path.relative_to(ROOT).as_posix()]=path.read_bytes()
        cls.serial=0

    @classmethod
    def tearDownClass(cls):
        cls.fixture_class.tearDownClass()

    def setUp(self):
        self.fixture.setUp()

    def selected(self):
        return json.loads((self.root/c.MF_SELECTION).read_bytes())

    def write(self,name,data):
        path=self.root/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        return path

    def stage(self,request=None):
        type(self).serial+=1
        ordinal=type(self).serial
        draft=self.base/f'mint-front-request-{ordinal}.json'
        draft.write_bytes(b.encoded(request or self.selected()))
        target=self.base/f'mint-front-stage-{ordinal}'
        b.mf_stage(self.root,draft,target)
        return target

    def outputs(self):
        names={c.MF_SELECTION,c.MF_MAPPING,b.RUNTIME}
        names|={c.MF_ROOT+'/'+row[0] for row in EXPECTED.values()}
        return {name:(self.root/name).read_bytes() for name in names}

    def changed_source(self,index=0):
        selected=self.selected()
        row=selected['resources'][index]
        with Image.open(self.root/row['source_png']) as original:
            image=original.copy()
        xy=next((x,y) for y in range(image.height) for x in range(image.width)
                if image.getpixel((x,y))[3]>0)
        rgba=image.getpixel(xy)
        image.putpixel(xy,((rgba[0]+1)%256,*rgba[1:]))
        stream=io.BytesIO()
        image.save(stream,format='PNG')
        raw=stream.getvalue()
        name=f'authoring-inputs/mint-front-tests/body-{index}.png'
        self.write(name,raw)
        row.update(source_png=name,source_sha256=b.sha(raw))
        selected['version']=f'synthetic-independent-body-{index}'
        return selected

    def package(self,*extra):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=pack.main(['--source-root',str(self.root),*map(str,extra)])
        return code,json.loads(output.getvalue())

    def test_approved_bootstrap_four_independent_exact_sources_and_geometry(self):
        raw=(ROOT/'tests/fixtures/mint-front-body-bootstrap-v1.json').read_bytes()
        self.assertEqual(b.sha(raw),BOOTSTRAP_SHA)
        fixture=json.loads(raw)
        self.assertEqual(tuple(c.MF_IDS),tuple(EXPECTED))
        self.assertEqual(len(c.mf_input_paths(self.root)),5)
        self.assertEqual(b.mf_check(self.root)['resources'],4)
        selected=self.selected()
        self.assertEqual([row['identity'] for row in selected['resources']],list(EXPECTED))
        self.assertEqual(len({row['source_png'] for row in selected['resources']}),4)
        self.assertEqual(len({row['source_sha256'] for row in selected['resources'][:3]}),3)
        for expected,row in zip(fixture['files'],selected['resources']):
            name,w,h=EXPECTED[row['identity']]
            self.assertEqual(expected['identity'],row['identity'])
            raw=(self.root/row['source_png']).read_bytes()
            self.assertEqual(b.sha(raw),expected['png_sha256'])
            self.assertEqual(raw,(ROOT/expected['historical_png']).read_bytes())
            with Image.open(io.BytesIO(raw)) as image:
                self.assertEqual((image.mode,image.size),('RGBA',(w*8,h*8)))
                payload=image.tobytes()
            hda=(self.root/c.MF_ROOT/name).read_bytes()
            self.assertEqual(hda,struct.pack('<4s6I',b'HDR1',row['identity'],8,w,h,0,0)+payload)
            self.assertEqual(hda,(ROOT/expected['historical_hda']).read_bytes())
            self.assertEqual(b.sha(hda),expected['hda_sha256'])
            self.assertEqual(b.sha(payload),expected['rgba_sha256'])
        self.assertEqual(tuple(c.IDS),(1260152,1290224,1290243,1290262,1290281,1290300))
        self.assertEqual(len(c.CHARGE_IDS),9)

    def test_each_source_edit_changes_only_its_transport_and_runtime_row(self):
        for index,identity in enumerate(EXPECTED):
            self.fixture.setUp()
            before=self.outputs()
            runtime_before=json.loads(before[b.RUNTIME])
            request=self.changed_source(index)
            snapshot=self.fixture.snapshot()
            stage=self.stage(request)
            self.assertEqual(self.fixture.snapshot(),snapshot,'stage mutated repository')
            b.mf_apply(self.root,stage)
            self.assertEqual(b.mf_check(self.root)['status'],'PASS')
            after=self.outputs()
            changed=[name for name in before if name.endswith('.hda') and before[name]!=after[name]]
            self.assertEqual(changed,[c.MF_ROOT+'/'+EXPECTED[identity][0]])
            current=json.loads(after[b.RUNTIME])
            old={row['destination']:row for row in runtime_before['files']}
            new={row['destination']:row for row in current['files']}
            self.assertEqual(set(old),set(new))
            self.assertEqual([name for name in old if old[name]!=new[name]],['assets/gameplay/'+EXPECTED[identity][0]])
            allowed={c.MF_SELECTION,c.MF_MAPPING,b.RUNTIME,c.MF_ROOT+'/'+EXPECTED[identity][0]}
            self.assertEqual({name for name,digest in snapshot.items()
                              if b.sha((self.root/name).read_bytes())!=digest},allowed)
            self.assertEqual(len(json.loads((self.root/b.REGISTRY).read_bytes())['resources']),120)

    def test_in_place_source_edit_stages_updated_hash_without_replacing_selection_first(self):
        selected=self.selected();original_path=selected['resources'][1]['source_png']
        before=self.outputs();request=self.changed_source(1)
        raw=(self.root/request['resources'][1]['source_png']).read_bytes()
        (self.root/original_path).write_bytes(raw)
        request['resources'][1]['source_png']=original_path
        # Until explicit apply, installed hash/output authority remains stale.
        with self.assertRaises(ValueError):c.mf_load(self.root)
        with self.assertRaises(ValueError):self.package()
        stage=self.stage(request)
        self.assertEqual(self.outputs(),before)
        b.mf_apply(self.root,stage)
        self.assertEqual(b.mf_check(self.root)['status'],'PASS')
        after=self.outputs()
        self.assertEqual([name for name in before if name.endswith('.hda') and before[name]!=after[name]],
                         [c.MF_ROOT+'/'+EXPECTED[1270131][0]])
        installed=self.selected()['resources'][1]
        self.assertEqual((installed['source_png'],installed['source_sha256']),(original_path,b.sha(raw)))

    def test_four_edits_propagate_to_both_views_and_1024_file_runtime(self):
        for index in range(4):
            b.mf_apply(self.root,self.stage(self.changed_source(index)))
        mapping=c.mf_load(self.root)
        for kind in ('preview','debug'):
            target=self.base/('mint-front-updated-'+kind)
            report=craft.view(self.root,kind,target)
            self.assertEqual((report['files'],len(report['current_overlays'])),(650,171))
            frozen=self.root/'assets/hd/packs'/craft.BASES[kind]
            nonoverlays=[p for p in frozen.rglob('*') if p.is_file()
                         and p.relative_to(frozen).as_posix() not in report['current_overlays']]
            self.assertEqual(len(nonoverlays),481)
            for path in nonoverlays:
                self.assertEqual(path.read_bytes(),(target/path.relative_to(frozen)).read_bytes())
            for destination,row in mapping.items():
                self.assertEqual((target/Path(destination).name).read_bytes(),(self.root/row['source_path']).read_bytes())
        code,report=self.package()
        self.assertEqual((code,report['verified_files']),(0,1024))
        target=self.base/'mint-front-runtime-copy'
        evidence=os.environ.get('MINT_FRONT_REAL_COPY_OUTPUT')
        if evidence:
            # Real cloud copy acceptance keeps filesystem, permission and space guards.
            # Never retry a denied operation under a different target.
            target=Path(evidence)
            command=[sys.executable,'-B',str(self.root/'scripts/package_runtime.py'),
                     '--source-root',str(self.root),'--build','--output',str(target)]
            result=subprocess.run(command,capture_output=True,text=True)
            receipt=dict(command=command,returncode=result.returncode,stdout=result.stdout,
                         stderr=result.stderr,selection=self.selected(),mapping=list(mapping.values()),
                         scope='Four independent synthetic source updates, two650-file views and real1024-file CLI copy; no game/Windows execution')
            with target.with_name(target.name+'-receipt.json').open('xb') as stream:
                stream.write(b.encoded(receipt))
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            code=result.returncode
            report=json.loads(result.stdout)
        else:
            # Content-only portable test. Real-copy acceptance is the opt-in above.
            with patch.object(Path,'chmod',return_value=None):
                code,report=self.package('--build','--output',target)
        self.assertEqual((code,report['verified_files']),(0,1024))
        self.assertEqual(len(json.loads((target/'RUNTIME-INVENTORY.json').read_bytes())['files']),1024)
        for destination,row in mapping.items():
            self.assertEqual((target/destination).read_bytes(),(self.root/row['source_path']).read_bytes())

    def test_schema_order_identity_version_and_independent_path_contract(self):
        original=self.selected()
        mutants=[]
        for value in (True,1270112.0,1270113,1280084):
            row=copy.deepcopy(original);row['resources'][0]['identity']=value;mutants.append(row)
        for value in ('',None,128,'x'*129):
            row=copy.deepcopy(original);row['version']=value;mutants.append(row)
        for value in ([],original['resources'][:3],list(reversed(original['resources']))):
            row=copy.deepcopy(original);row['resources']=value;mutants.append(row)
        for key,value in [('schema','unknown'),('geometry',[24,28]),('generator','arbitrary.py')]:
            row=copy.deepcopy(original);row[key]=value;mutants.append(row)
        row=copy.deepcopy(original);row['resources'][1]['source_png']=row['resources'][0]['source_png'];row['resources'][1]['source_sha256']=row['resources'][0]['source_sha256'];mutants.append(row)
        for value in ('../escape.png','authoring-inputs/../../escape.png','/tmp/outside.png',
                      'authoring-inputs/../escape.png','authoring-inputs\\escape.png',
                      'authoring-inputs/a:b.png','assets/hd/current-compat/fake.png',
                      'assets/hd/source/option-mint-bank9-112-8-ddbfe03b540b.png',
                      'authoring-inputs/body.PNG',None):
            row=copy.deepcopy(original);row['resources'][0]['source_png']=value;mutants.append(row)
        for value in ('x'*64,'A'*64,None):
            row=copy.deepcopy(original);row['resources'][0]['source_sha256']=value;mutants.append(row)
        for ordinal,request in enumerate(mutants):
            with self.subTest(case=ordinal),self.assertRaises(ValueError):
                c.mf_generate(self.root,b.encoded(request))

    def test_generated_charge_frames_and_casefold_aliases_are_not_independent_sources(self):
        before=self.outputs()
        for identity in (1450258,1450259,1450260,1450277,1450278,1450279,1450296,1450297,1450298):
            original=f'authoring-inputs/charge-body-current/derived/bank9-id{identity-1450000}.png'
            raw=(self.root/original).read_bytes()
            alias=Path(original).with_name(Path(original).stem.upper()+'.png').as_posix()
            self.write(alias,raw)
            for source in (original,alias):
                selected=self.selected()
                selected['resources'][0].update(source_png=source,source_sha256=b.sha(raw))
                self.assertEqual(b.sha((self.root/source).read_bytes()),selected['resources'][0]['source_sha256'])
                with self.subTest(identity=identity,path=source),self.assertRaisesRegex(ValueError,'Generated Charge frame'):
                    c.mf_generate(self.root,b.encoded(selected))
        self.assertEqual(self.outputs(),before)

    def test_duplicate_nonfinite_and_oversized_selection_rejected(self):
        for raw in (b'{"schema":"a","schema":"b"}',b'{"schema":NaN}',b' '*131073):
            with self.subTest(raw=raw[:64]),self.assertRaises(ValueError):
                c.mf_generate(self.root,raw)

    def test_png_dimensions_mode_crc_animation_trailing_and_16bit_rejected(self):
        valid=png()
        corrupt=bytearray(valid);corrupt[-1]^=1
        for ordinal,raw in enumerate((b'not PNG',png((192,224)),png(mode='RGB'),
                                      png(animated=True),valid+b'trailing',bytes(corrupt),
                                      valid[:-4],png16(),b'\0'*(16*1024*1024+1))):
            request=self.selected()
            name='authoring-inputs/mint-front-tests/invalid.png'
            self.write(name,raw)
            request['resources'][0].update(source_png=name,source_sha256=b.sha(raw))
            with self.subTest(case=ordinal),self.assertRaises(ValueError):
                c.mf_generate(self.root,b.encoded(request))
        request=self.selected();raw=png();name='authoring-inputs/mint-front-tests/wrong-front.png'
        self.write(name,raw);request['resources'][3].update(source_png=name,source_sha256=b.sha(raw))
        with self.assertRaises(ValueError):c.mf_generate(self.root,b.encoded(request))

    def test_changed_selected_source_is_rejected_by_check_view_and_package(self):
        row=self.selected()['resources'][0]
        path=self.root/row['source_png'];path.write_bytes(path.read_bytes()+b'\n')
        for name,action in [('check',lambda:b.mf_check(self.root)),
                            ('stage',lambda:self.stage()),
                            ('view',lambda:craft.view(self.root,'preview',self.base/'bad-mf-view')),
                            ('package',lambda:self.package())]:
            with self.subTest(entry=name),self.assertRaises(ValueError):action()
        self.assertFalse((self.base/'bad-mf-view').exists())

    def test_rehashed_source_without_derived_rebuild_is_rejected(self):
        selected=self.changed_source()
        (self.root/c.MF_SELECTION).write_bytes(b.encoded(selected))
        for action in (lambda:b.mf_check(self.root),lambda:c.mf_load(self.root),lambda:self.package(),
                       lambda:craft.current_overlays(self.root)):
            with self.assertRaises(ValueError):action()

    def test_coherently_rehashed_hda_mapping_and_manifest_still_rejected(self):
        mapping=json.loads((self.root/c.MF_MAPPING).read_bytes())
        row=mapping['files'][0];path=self.root/row['source_path']
        data=bytearray(path.read_bytes());data[-1]^=1;path.write_bytes(data)
        row['sha256']=b.sha(data)
        (self.root/c.MF_MAPPING).write_bytes(b.encoded(mapping))
        runtime=json.loads((self.root/b.RUNTIME).read_bytes())
        target=next(r for r in runtime['files'] if r['destination']==row['destination'])
        target['sha256']=b.sha(data)
        target['git_blob']=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        (self.root/b.RUNTIME).write_bytes(b.encoded(runtime))
        with self.assertRaises(ValueError):self.package()
        with self.assertRaises(ValueError):craft.current_overlays(self.root)

    def test_mapping_strict_identity_paths_fields_and_order(self):
        path=self.root/c.MF_MAPPING;original=path.read_bytes()
        for mode in ('float','bool','source','destination','missing','order','extra','version'):
            mapping=json.loads(original)
            if mode=='float':mapping['files'][0]['identity']=1270112.0
            elif mode=='bool':mapping['files'][0]['identity']=True
            elif mode=='source':mapping['files'][0]['source_path']='assets/hd/packs/elsewhere.hda'
            elif mode=='destination':mapping['files'][0]['destination']='assets/gameplay/option-mint-bank9-999-8.hda'
            elif mode=='missing':mapping['files'].pop()
            elif mode=='order':mapping['files'].reverse()
            elif mode=='extra':mapping['files'][0]['option']=22
            elif mode=='version':mapping['version']='mismatched-version'
            path.write_bytes(b.encoded(mapping))
            with self.subTest(mode=mode),self.assertRaises(ValueError):c.mf_load(self.root)
        path.write_bytes(original)

    def test_partial_uppercase_unknown_and_relabelled_package_refused(self):
        manifest=json.loads((self.root/b.RUNTIME).read_bytes())
        rows=[row for row in manifest['files'] if Path(row['destination']).name in {r[0] for r in EXPECTED.values()}]
        self.assertEqual(len(rows),4)
        for mode in ('partial','uppercase','unknown','relabelled'):
            mutant=copy.deepcopy(manifest);mutant['files']=copy.deepcopy(rows)
            if mode=='partial':mutant['files']=mutant['files'][:1]
            if mode=='uppercase':mutant['files'][0]['destination']=mutant['files'][0]['destination'].upper()
            if mode=='unknown':mutant['files'][0]['destination']='assets/gameplay/option-frontblaster-bank10-84-8.hda'
            if mode=='relabelled':mutant['files'][0]['destination']='assets/gameplay/not-a-body.hda'
            path=self.base/('mint-front-package-'+mode+'.json');path.write_bytes(b.encoded(mutant))
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.package('--manifest',path)
        # Generic manifests with none of the body family keep their old meaning.
        generic=copy.deepcopy(manifest)
        generic['files']=[next(row for row in manifest['files'] if row['destination']=='README.txt')]
        path=self.base/'mint-front-generic-manifest.json';path.write_bytes(b.encoded(generic))
        code,report=self.package('--manifest',path)
        self.assertEqual((code,report['verified_files']),(0,1))

    def test_default_and_explicit_current_manifest_cannot_drop_entire_family(self):
        path=self.root/b.RUNTIME;original=path.read_bytes();manifest=json.loads(original)
        names={row[0] for row in EXPECTED.values()}
        manifest['files']=[row for row in manifest['files']
                           if Path(row['destination']).name not in names]
        self.assertEqual(len(manifest['files']),1011)
        path.write_bytes(b.encoded(manifest))
        before=self.outputs()
        try:
            for extra in ((),('--manifest',path)):
                with self.subTest(explicit=bool(extra)),self.assertRaises(ValueError):
                    self.package(*extra)
                self.assertEqual(self.outputs(),before)
        finally:path.write_bytes(original)

    def test_explicit_historical_four_body_manifest_needs_no_current_selection(self):
        historical=json.loads((self.root/'packaging/runtime-assets-public63a89b3.json').read_bytes())
        names={row[0] for row in EXPECTED.values()}
        historical['files']=[row for row in historical['files']
                             if Path(row['destination']).name in names]
        self.assertEqual(len(historical['files']),4)
        for row in historical['files']:
            self.assertTrue(row['source_path'].startswith('assets/hd/packs/'))
            self.assertNotEqual(row.get('revision'),'current-single-source-mint-front-body')
        manifest=self.base/'mint-front-historical-four-manifest.json'
        manifest.write_bytes(b.encoded(historical))
        removed={name:(self.root/name).read_bytes() for name in (c.MF_SELECTION,c.MF_MAPPING)}
        for name in removed:(self.root/name).unlink()
        try:
            code,report=self.package('--manifest',manifest)
            self.assertEqual((code,report['verified_files']),(0,4))
            for name in removed:self.assertFalse((self.root/name).exists())
        finally:
            for name,data in removed.items():(self.root/name).write_bytes(data)

    def test_isolated_packager_accepts_explicit_historical_and_generic_manifests(self):
        isolated=self.base/'mint-front-isolated-packager';isolated.mkdir()
        script=isolated/'package_runtime.py'
        script.write_bytes((self.root/'scripts/package_runtime.py').read_bytes())
        historical=json.loads((self.root/'packaging/runtime-assets-public63a89b3.json').read_bytes())
        names={row[0] for row in EXPECTED.values()}
        historical['files']=[row for row in historical['files'] if Path(row['destination']).name in names]
        self.assertEqual(len(historical['files']),4)
        generic=json.loads((self.root/b.RUNTIME).read_bytes())
        generic['files']=[next(row for row in generic['files'] if row['destination']=='README.txt')]
        environment=dict(os.environ)
        environment.pop('PYTHONPATH',None);environment.pop('PYTHONHOME',None)
        for kind,manifest,count in (('historical',historical,4),('generic',generic,1)):
            path=self.base/f'mint-front-isolated-{kind}.json';path.write_bytes(b.encoded(manifest))
            command=[sys.executable,'-I','-B',str(script),'--source-root',str(self.root),'--manifest',str(path)]
            result=subprocess.run(command,cwd=isolated,env=environment,capture_output=True,text=True)
            with self.subTest(kind=kind):
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertEqual(json.loads(result.stdout)['verified_files'],count)
        self.assertEqual([path.name for path in isolated.iterdir()],['package_runtime.py'])

    def test_stale_inputs_tools_old_outputs_and_tampered_stage_fail_before_writes(self):
        for mode in ('source','tool','old_output','staged_hda','missing_staged','request','plan'):
            self.fixture.setUp();request=self.changed_source();stage=self.stage(request)
            if mode=='source':target=self.root/request['resources'][0]['source_png']
            elif mode=='tool':target=self.root/'scripts/build_current_sidekick_body.py'
            elif mode=='old_output':target=self.root/c.MF_ROOT/EXPECTED[1270112][0]
            elif mode in ('staged_hda','missing_staged'):target=stage/'files'/c.MF_ROOT/EXPECTED[1270112][0]
            elif mode=='request':target=stage/'request.json'
            else:target=stage/'plan.json'
            if mode=='missing_staged':target.unlink()
            else:target.write_bytes(target.read_bytes()+b'changed')
            before=self.outputs()
            with self.subTest(mode=mode),self.assertRaises((ValueError,OSError)):
                b.mf_apply(self.root,stage)
            self.assertEqual(self.outputs(),before)

    def test_plan_duplicate_nonfinite_oversize_and_numeric_type_rejected(self):
        stage=self.stage();path=stage/'plan.json';original=path.read_bytes();before=self.outputs()
        plans=[b'{"schema":"a","schema":"b"}',b'{"x":NaN}',b' '*131073]
        numeric=json.loads(original);numeric['files'][0]['bytes']=float(numeric['files'][0]['bytes']);plans.append(b.encoded(numeric))
        for ordinal,raw in enumerate(plans):
            path.write_bytes(raw)
            with self.subTest(case=ordinal),self.assertRaises(ValueError):b.mf_apply(self.root,stage)
            self.assertEqual(self.outputs(),before)
        path.write_bytes(original)

    def test_temporary_collision_and_stage_symlink_fail_before_writes(self):
        stage=self.stage(self.changed_source())
        temporary=self.root/(c.MF_MAPPING+craft.SUFFIX)
        temporary.write_bytes(b'occupied temporary output')
        before=self.fixture.snapshot()
        with self.assertRaises(ValueError):b.mf_apply(self.root,stage)
        self.assertEqual(self.fixture.snapshot(),before)
        temporary.unlink()
        linked=self.base/'mint-front-stage-link'
        linked.symlink_to(stage,target_is_directory=True)
        before=self.outputs()
        try:
            with self.assertRaises(ValueError):b.mf_apply(self.root,linked)
            self.assertEqual(self.outputs(),before)
        finally:linked.unlink()

    def test_handled_replace_failure_rolls_back_all_changed_outputs(self):
        stage=self.stage(self.changed_source());before=self.fixture.snapshot()
        replace=os.replace;calls=0
        def failing(source,target):
            nonlocal calls
            calls+=1
            if calls==2:raise OSError('synthetic second replacement failure')
            return replace(source,target)
        with patch.object(craft.os,'replace',side_effect=failing):
            with self.assertRaisesRegex(OSError,'synthetic second'):b.mf_apply(self.root,stage)
        self.assertGreaterEqual(calls,3,'expected a handled rollback replacement')
        self.assertEqual(self.fixture.snapshot(),before)

    def test_all_twenty_existing_workflows_preserve_four_current_bodies(self):
        import build_current_art as art
        import build_current_hud as hud
        import build_current_tank_shell as tank
        import build_current_enemy_energy as energy
        b.mf_apply(self.root,self.stage(self.changed_source(1)))
        before=self.outputs();count=0
        for family in PROFILES:
            stage=self.base/('mint-front-coexist-'+family)
            art.stage(self.root,self.root/profile(family)['selection'],stage,family)
            art.apply(self.root,stage,family);count+=1
            self.assertEqual(self.outputs(),before)
        for name,module,selection in [('hud',hud,hud.SELECTION),('tank',tank,tank.SELECTION),
                                      ('energy',energy,energy.SELECTION),('sidekick',b,b.SELECTION),
                                      ('craft267',craft,craft.SELECTION)]:
            stage=self.base/('mint-front-coexist-'+name)
            module.stage(self.root,self.root/selection,stage);module.apply(self.root,stage);count+=1
            self.assertEqual(self.outputs(),before)
        stage=self.base/'mint-front-coexist-charge'
        b.charge_stage(self.root,self.root/c.CHARGE_SELECTION,stage)
        b.charge_apply(self.root,stage);count+=1
        self.assertEqual(self.outputs(),before)
        self.assertEqual(count,20)

    def test_changed_charge_front_charge_roundtrip_preserves_other_current_family(self):
        def charge_outputs():
            selected=json.loads((self.root/c.CHARGE_SELECTION).read_bytes())
            names={c.CHARGE_SELECTION,c.CHARGE_MAPPING}
            names|={row['source_png'] for row in selected['resources']}
            names|={c.CHARGE_ROOT+'/'+c.charge_name(identity) for identity in c.CHARGE_IDS}
            return {name:(self.root/name).read_bytes() for name in names}
        def change_charge(ordinal):
            selected=json.loads((self.root/c.CHARGE_SELECTION).read_bytes())
            with Image.open(self.root/selected['master']['source_png']) as original:
                master=original.copy()
            xy=next((x,y) for y in range(80,110) for x in range(1,95)
                    if master.getpixel((x,y))[3]>0)
            rgba=master.getpixel(xy);master.putpixel(xy,((rgba[0]+3)%256,*rgba[1:]))
            stream=io.BytesIO();master.save(stream,format='PNG');raw=stream.getvalue()
            name=f'authoring-inputs/mint-front-charge-tests/master-{ordinal}.png'
            self.write(name,raw)
            recipe=json.loads((self.root/selected['recipe']['path']).read_bytes())
            recipe['master_sha256']=b.sha(raw)
            recipe_name=f'authoring-inputs/mint-front-charge-tests/recipe-{ordinal}.json'
            recipe_raw=b.encoded(recipe);self.write(recipe_name,recipe_raw)
            request=dict(schema=c.CHARGE_CANDIDATE_SCHEMA,version=f'synthetic-roundtrip-{ordinal}',
                         master=dict(source_png=name,source_sha256=b.sha(raw)),
                         recipe=dict(path=recipe_name,sha256=b.sha(recipe_raw)))
            draft=self.base/f'mint-front-charge-draft-{ordinal}.json';draft.write_bytes(b.encoded(request))
            stage=self.base/f'mint-front-charge-stage-{ordinal}'
            b.charge_stage(self.root,draft,stage);b.charge_apply(self.root,stage)
        before={name:data for name,data in self.outputs().items() if name!=b.RUNTIME}
        change_charge(1)
        self.assertEqual(before,{name:data for name,data in self.outputs().items() if name!=b.RUNTIME})
        charge_before=charge_outputs()
        b.mf_apply(self.root,self.stage(self.changed_source(3)))
        self.assertEqual(charge_outputs(),charge_before)
        self.assertEqual(b.charge_check(self.root)['status'],'PASS')
        changed_front={name:data for name,data in self.outputs().items() if name!=b.RUNTIME}
        self.assertNotEqual(changed_front[c.MF_ROOT+'/'+EXPECTED[1280083][0]],before[c.MF_ROOT+'/'+EXPECTED[1280083][0]])
        change_charge(2)
        self.assertEqual(changed_front,{name:data for name,data in self.outputs().items() if name!=b.RUNTIME})
        charge_after=charge_outputs()
        self.assertEqual(sum(charge_before[name]!=charge_after[name] for name in charge_before if name.endswith('.hda')),9)
        self.assertEqual(b.mf_check(self.root)['status'],'PASS')
        self.assertEqual(b.charge_check(self.root)['status'],'PASS')
        code,report=self.package();self.assertEqual((code,report['verified_files']),(0,1024))

    def test_mint_front_source_drift_invalidates_each_legacy_and_charge_plan(self):
        import build_current_art as art
        import build_current_hud as hud
        import build_current_tank_shell as tank
        import build_current_enemy_energy as energy
        for name,module,selection in [('art',art,profile('pulse')['selection']),
                                      ('hud',hud,hud.SELECTION),('tank',tank,tank.SELECTION),
                                      ('energy',energy,energy.SELECTION),('sidekick',b,b.SELECTION),
                                      ('craft267',craft,craft.SELECTION),('charge',b,c.CHARGE_SELECTION)]:
            self.fixture.setUp();stage=self.base/('mint-front-drift-'+name)
            if name=='charge':b.charge_stage(self.root,self.root/selection,stage)
            else:module.stage(self.root,self.root/selection,stage)
            row=self.selected()['resources'][0];source=self.root/row['source_png']
            source.write_bytes(source.read_bytes()+b'\n')
            before=self.outputs()
            with self.subTest(family=name),self.assertRaises(ValueError):
                if name=='charge':b.charge_apply(self.root,stage)
                else:module.apply(self.root,stage)
            self.assertEqual(self.outputs(),before)

    def test_sources_and_output_paths_reject_symlinks_and_stage_inside_repo(self):
        selected=self.selected();source=self.root/selected['resources'][0]['source_png']
        linked=self.root/'authoring-inputs/mint-front-tests/linked.png'
        linked.parent.mkdir(parents=True,exist_ok=True)
        linked.symlink_to(source)
        selected['resources'][0]['source_png']=linked.relative_to(self.root).as_posix()
        try:
            with self.assertRaises(ValueError):c.mf_generate(self.root,b.encoded(selected))
        finally:linked.unlink()
        with self.assertRaises(ValueError):b.mf_stage(self.root,self.root/c.MF_SELECTION,self.root/'forbidden-stage')
        self.assertFalse((self.root/'forbidden-stage').exists())
        stage=self.stage(self.changed_source());path=self.root/c.MF_ROOT/EXPECTED[1270112][0]
        held=path.with_name('original-held.hda');path.rename(held);path.symlink_to(held)
        try:
            with self.assertRaises(ValueError):b.mf_apply(self.root,stage)
        finally:path.unlink();held.rename(path)


if __name__=='__main__':
    unittest.main(verbosity=2)
