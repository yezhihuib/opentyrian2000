"""Eight independent approved Front Multi sources; synthetic mutations stay in fixtures.

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
import build_current_front_multi as b
import build_current_sidekick_body as body
import current_sidekick_body_compatibility as bodies
import build_current_plasma_projectile as plasma_builder
import current_plasma_projectile_compatibility as plasma
import current_front_multi_compatibility as c
import build_current_craft267 as craft
import package_runtime as pack
from current_art_policy import PROFILES, profile

# Independent literal scope; do not derive expectations from the production policy.
EXPECTED = {
    80121: ('bullet-121-8.hda', 524), 80122: ('bullet-122-8.hda', 525),
    80163: ('bullet-163-8.hda', 526), 80164: ('bullet-164-8.hda', 527),
    80201: ('bullet-201-8.hda', 528), 80202: ('bullet-202-8.hda', 529),
    80279: ('bullet-279-8.hda', 530), 80280: ('bullet-280-8.hda', 531),
}
ART = 'assets/hd/artwork/player-front-multi-eight-v1'
INVENTORY_SHA = 'b14abd722c64358ab3d465ad213d64eb6c9ab39a57cefc4c907ddbd0818f1084'


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


class FrontMultiAuthoringTests(unittest.TestCase):
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
        return json.loads((self.root/c.SELECTION).read_bytes())

    def write(self,name,data):
        path=self.root/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        return path

    def stage(self,request=None):
        type(self).serial+=1
        ordinal=type(self).serial
        draft=self.base/f'front-multi-request-{ordinal}.json'
        draft.write_bytes(b.encoded(request or self.selected()))
        target=self.base/f'front-multi-stage-{ordinal}'
        b.stage(self.root,draft,target)
        return target

    def outputs(self,shared=True):
        names={c.SELECTION,c.MAPPING,c.HEADER}
        if shared:names|={b.RUNTIME,b.BINDING}
        names|={c.ROOT+'/'+row[0] for row in EXPECTED.values()}
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
        name=f'authoring-inputs/front-multi-tests/bullet-{index}.png'
        self.write(name,raw)
        row.update(source_png=name,source_sha256=b.sha(raw))
        selected['version']=f'synthetic-independent-front-multi-{index}'
        return selected

    def package(self,*extra):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=pack.main(['--source-root',str(self.root),*map(str,extra)])
        return code,json.loads(output.getvalue())

    def frozen_bootstrap(self):
        request = dict(schema='opentyrian-current-front-multi-authoring-v1',
                       version='frozen-front-multi-bootstrap-test-only', resources=[])
        for identity, (name, _) in EXPECTED.items():
            source = 'authoring-inputs/front-multi-bootstrap-test/' + name.replace('.hda', '.png')
            raw = (ROOT/ART/'output'/name.replace('.hda', '.png')).read_bytes()
            self.write(source, raw)
            request['resources'].append(dict(identity=identity, source_png=source, source_sha256=b.sha(raw)))
        b.apply(self.root, self.stage(request))

    def test_approved_bootstrap_eight_independent_exact_sources_geometry_and_pins(self):
        raw=(ROOT/ART/'inventory.json').read_bytes()
        self.assertEqual(b.sha(raw),INVENTORY_SHA)
        inventory=json.loads(raw)
        self.frozen_bootstrap()
        self.assertEqual(tuple(c.IDS),tuple(EXPECTED))
        self.assertEqual(len(c.input_paths(self.root)),9)
        self.assertEqual(b.check(self.root)['resources'],8)
        selected=self.selected()
        self.assertEqual([row['identity'] for row in selected['resources']],list(EXPECTED))
        self.assertEqual(len({row['source_png'] for row in selected['resources']}),8)
        self.assertEqual(len({row['source_sha256'] for row in selected['resources']}),8)
        pins={}
        for expected,row in zip(inventory['outputs'],selected['resources']):
            name,slot=EXPECTED[row['identity']]
            self.assertEqual((expected['key'],expected['slot'],expected['role']), (row['identity'],slot,8))
            raw=(self.root/row['source_png']).read_bytes()
            self.assertEqual(b.sha(raw),expected['PNG_SHA256'])
            self.assertEqual(raw,(ROOT/ART/'output'/name.replace('.hda','.png')).read_bytes())
            with Image.open(io.BytesIO(raw)) as image:
                self.assertEqual((image.mode,image.size),('RGBA',(96,112)))
                payload=image.tobytes()
            hda=(self.root/c.ROOT/name).read_bytes()
            self.assertEqual(hda,struct.pack('<4s6I',b'HDR1',row['identity'],8,12,14,0,0)+payload)
            self.assertEqual(hda,(ROOT/ART/'output'/name).read_bytes())
            self.assertEqual(b.sha(hda),expected['HDA_SHA256'])
            self.assertEqual(b.sha(payload),expected['RGBA_SHA256'])
            value=14695981039346656037
            for byte in payload:value=((value^byte)*1099511628211)&((1<<64)-1)
            pins[row['identity']]=f'{value:016x}'
            self.assertEqual(pins[row['identity']],expected['RGBA_FNV1a64'])
        header=(self.root/c.HEADER).read_bytes()
        self.assertEqual(header,c.payload_header(pins))
        for identity,value in pins.items():
            self.assertIn(f'#define HD_FRONT_MULTI_CURRENT_PAYLOAD_{identity}_HASH UINT64_C(0x{value})'.encode(),header)
        self.assertEqual(sum(b'_HASH UINT64_C' in line for line in header.splitlines()),8)
        from verify_current_production import verify
        self.assertEqual(verify(self.root,json.loads((self.root/b.BINDING).read_bytes())),255)
        self.assertEqual(len(json.loads((self.root/b.REGISTRY).read_bytes())['resources']),120)

    def test_each_source_edit_changes_only_its_transport_and_runtime_row(self):
        for index,identity in enumerate(EXPECTED):
            self.fixture.setUp()
            before=self.outputs()
            runtime_before=json.loads(before[b.RUNTIME])
            request=self.changed_source(index)
            snapshot=self.fixture.snapshot()
            stage=self.stage(request)
            self.assertEqual(self.fixture.snapshot(),snapshot,'stage mutated repository')
            b.apply(self.root,stage)
            self.assertEqual(b.check(self.root)['status'],'PASS')
            after=self.outputs()
            changed=[name for name in before if name.endswith('.hda') and before[name]!=after[name]]
            self.assertEqual(changed,[c.ROOT+'/'+EXPECTED[identity][0]])
            current=json.loads(after[b.RUNTIME])
            old={row['destination']:row for row in runtime_before['files']}
            new={row['destination']:row for row in current['files']}
            self.assertEqual(set(old),set(new))
            self.assertEqual(sorted(name for name in old if old[name]!=new[name]),sorted(['CURRENT-PRODUCTION-VALIDATION.json','assets/gameplay/'+EXPECTED[identity][0]]))
            allowed={c.SELECTION,c.MAPPING,c.HEADER,b.BINDING,b.RUNTIME,c.ROOT+'/'+EXPECTED[identity][0]}
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
        with self.assertRaises(ValueError):c.load(self.root)
        with self.assertRaises(ValueError):self.package()
        stage=self.stage(request)
        self.assertEqual(self.outputs(),before)
        b.apply(self.root,stage)
        self.assertEqual(b.check(self.root)['status'],'PASS')
        after=self.outputs()
        self.assertEqual([name for name in before if name.endswith('.hda') and before[name]!=after[name]],
                         [c.ROOT+'/'+EXPECTED[80122][0]])
        installed=self.selected()['resources'][1]
        self.assertEqual((installed['source_png'],installed['source_sha256']),(original_path,b.sha(raw)))

    def test_eight_edits_propagate_to_both_views_and_1024_file_runtime(self):
        for index in range(8):
            b.apply(self.root,self.stage(self.changed_source(index)))
        mapping=c.load(self.root)
        for kind in ('preview','debug'):
            target=self.base/('front-multi-updated-'+kind)
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
        target=self.base/'front-multi-runtime-copy'
        evidence=os.environ.get('FRONT_MULTI_REAL_COPY_OUTPUT')
        if evidence:
            # Real cloud copy acceptance keeps filesystem, permission and space guards.
            # Never retry a denied operation under a different target.
            target=Path(evidence)
            command=[sys.executable,'-B',str(self.root/'scripts/package_runtime.py'),
                     '--source-root',str(self.root),'--build','--output',str(target)]
            result=subprocess.run(command,capture_output=True,text=True)
            receipt=dict(command=command,returncode=result.returncode,stdout=result.stdout,
                         stderr=result.stderr,selection=self.selected(),mapping=list(mapping.values()),
                         scope='Eight independent synthetic source updates, two650-file views and real1024-file CLI copy; no game/Windows execution')
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
        for value in (True,80121.0,80123,80281):
            row=copy.deepcopy(original);row['resources'][0]['identity']=value;mutants.append(row)
        for value in ('',None,128,'x'*129):
            row=copy.deepcopy(original);row['version']=value;mutants.append(row)
        for value in ([],original['resources'][:7],list(reversed(original['resources']))):
            row=copy.deepcopy(original);row['resources']=value;mutants.append(row)
        for key,value in [('schema','unknown'),('geometry',[24,28]),('generator','arbitrary.py')]:
            row=copy.deepcopy(original);row[key]=value;mutants.append(row)
        row=copy.deepcopy(original);row['resources'][1]['source_png']=row['resources'][0]['source_png'];row['resources'][1]['source_sha256']=row['resources'][0]['source_sha256'];mutants.append(row)
        for value in ('../escape.png','authoring-inputs/../../escape.png','/tmp/outside.png',
                      'authoring-inputs/../escape.png','authoring-inputs\\escape.png',
                      'authoring-inputs/a:b.png','assets/hd/current-compat/fake.png',
                      'assets/hd/source/bullet-121-8-2f890a93f8e6.png',
                      'authoring-inputs/body.PNG',None):
            row=copy.deepcopy(original);row['resources'][0]['source_png']=value;mutants.append(row)
        for value in ('x'*64,'A'*64,None):
            row=copy.deepcopy(original);row['resources'][0]['source_sha256']=value;mutants.append(row)
        for ordinal,request in enumerate(mutants):
            with self.subTest(case=ordinal),self.assertRaises(ValueError):
                c.generate(self.root,b.encoded(request))

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
                with self.subTest(identity=identity,path=source),self.assertRaisesRegex(ValueError,'[Gg]enerated'):
                    c.generate(self.root,b.encoded(selected))
        self.assertEqual(self.outputs(),before)

    def test_duplicate_nonfinite_and_oversized_selection_rejected(self):
        for raw in (b'{"schema":"a","schema":"b"}',b'{"schema":NaN}',b' '*131073):
            with self.subTest(raw=raw[:64]),self.assertRaises(ValueError):
                c.generate(self.root,raw)

    def test_png_dimensions_mode_crc_animation_trailing_and_16bit_rejected(self):
        valid=png()
        corrupt=bytearray(valid);corrupt[-1]^=1
        critical=valid[:33]+struct.pack('>I',0)+b'EVIL'+struct.pack('>I',zlib.crc32(b'EVIL')&0xffffffff)+valid[33:]
        for ordinal,raw in enumerate((b'not PNG',png((192,224)),png(mode='RGB'),
                                      png(animated=True),valid+b'trailing',bytes(corrupt),
                                      valid[:-4],png16(),critical,b'\0'*(16*1024*1024+1))):
            request=self.selected()
            name='authoring-inputs/front-multi-tests/invalid.png'
            self.write(name,raw)
            request['resources'][0].update(source_png=name,source_sha256=b.sha(raw))
            with self.subTest(case=ordinal),self.assertRaises(ValueError):
                c.generate(self.root,b.encoded(request))

    def test_png_chunk_order_names_palette_and_deflate_stream_are_strict(self):
        def chunk(kind,body):
            return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff)
        signature=b'\x89PNG\r\n\x1a\n'
        ihdr=chunk(b'IHDR',struct.pack('>IIBBBBB',96,112,8,6,0,0,0))
        pixels=(b'\0'+bytes((31,53,71,127))*96)*112
        compressed=zlib.compress(pixels)
        idat=chunk(b'IDAT',compressed);iend=chunk(b'IEND',b'')
        palette=chunk(b'PLTE',bytes((1,2,3)))
        cases={
            'duplicate_palette':signature+ihdr+palette+palette+idat+iend,
            'late_palette':signature+ihdr+idat+palette+iend,
            'partial_palette_entry':signature+ihdr+chunk(b'PLTE',b'1')+idat+iend,
            'malformed_phys':signature+ihdr+chunk(b'pHYs',b'1')+idat+iend,
            'nonletter_chunk_name':signature+ihdr+chunk(b'aB1D',b'')+idat+iend,
            'reserved_bit_chunk_name':signature+ihdr+chunk(b'aBcD',b'')+idat+iend,
            'deflate_trailing_garbage':signature+ihdr+chunk(b'IDAT',compressed+b'garbage')+iend,
            'deflate_extra_scanline':signature+ihdr+chunk(b'IDAT',zlib.compress(pixels+b'\0'+bytes(384)))+iend,
            'unknown_scanline_filter':signature+ihdr+chunk(b'IDAT',zlib.compress(b'\5'+pixels[1:]))+iend,
            'deflate_second_stream':signature+ihdr+chunk(b'IDAT',compressed+zlib.compress(b'extra'))+iend,
            'noncontiguous_idat':signature+ihdr+chunk(b'IDAT',compressed[:8])+chunk(b'tEXt',b'note\0x')+chunk(b'IDAT',compressed[8:])+iend,
        }
        for case,raw in cases.items():
            selected=self.selected();source='authoring-inputs/front-multi-tests/malformed-chunks.png'
            self.write(source,raw);selected['resources'][0].update(source_png=source,source_sha256=b.sha(raw))
            with self.subTest(case=case),self.assertRaises(ValueError):c.generate(self.root,b.encoded(selected))

    def test_changed_selected_source_is_rejected_by_check_view_and_package(self):
        row=self.selected()['resources'][0]
        path=self.root/row['source_png'];path.write_bytes(path.read_bytes()+b'\n')
        for name,action in [('check',lambda:b.check(self.root)),
                            ('stage',lambda:self.stage()),
                            ('view',lambda:craft.view(self.root,'preview',self.base/'bad-mf-view')),
                            ('package',lambda:self.package())]:
            with self.subTest(entry=name),self.assertRaises(ValueError):action()
        self.assertFalse((self.base/'bad-mf-view').exists())

    def test_rehashed_source_without_derived_rebuild_is_rejected(self):
        selected=self.changed_source()
        (self.root/c.SELECTION).write_bytes(b.encoded(selected))
        for action in (lambda:b.check(self.root),lambda:c.load(self.root),lambda:self.package(),
                       lambda:craft.current_overlays(self.root)):
            with self.assertRaises(ValueError):action()

    def test_coherently_rehashed_hda_mapping_and_manifest_still_rejected(self):
        mapping=json.loads((self.root/c.MAPPING).read_bytes())
        row=mapping['files'][0];path=self.root/row['source_path']
        data=bytearray(path.read_bytes());data[-1]^=1;path.write_bytes(data)
        row['sha256']=b.sha(data)
        (self.root/c.MAPPING).write_bytes(b.encoded(mapping))
        pins={}
        for entry in mapping['files']:
            value=14695981039346656037
            for byte in (self.root/entry['source_path']).read_bytes()[28:]:value=((value^byte)*1099511628211)&((1<<64)-1)
            pins[entry['identity']]=f'{value:016x}'
        (self.root/c.HEADER).write_bytes(c.payload_header(pins))
        runtime=json.loads((self.root/b.RUNTIME).read_bytes())
        target=next(r for r in runtime['files'] if r['destination']==row['destination'])
        target['sha256']=b.sha(data)
        target['git_blob']=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        (self.root/b.RUNTIME).write_bytes(b.encoded(runtime))
        with self.assertRaises(ValueError):self.package()
        with self.assertRaises(ValueError):craft.current_overlays(self.root)

    def test_mapping_strict_identity_paths_fields_and_order(self):
        path=self.root/c.MAPPING;original=path.read_bytes()
        for mode in ('float','bool','source','destination','missing','order','extra','version'):
            mapping=json.loads(original)
            if mode=='float':mapping['files'][0]['identity']=80121.0
            elif mode=='bool':mapping['files'][0]['identity']=True
            elif mode=='source':mapping['files'][0]['source_path']='assets/hd/packs/elsewhere.hda'
            elif mode=='destination':mapping['files'][0]['destination']='assets/gameplay/bullet-999-8.hda'
            elif mode=='missing':mapping['files'].pop()
            elif mode=='order':mapping['files'].reverse()
            elif mode=='extra':mapping['files'][0]['option']=22
            elif mode=='version':mapping['version']='mismatched-version'
            path.write_bytes(b.encoded(mapping))
            with self.subTest(mode=mode),self.assertRaises(ValueError):c.load(self.root)
        path.write_bytes(original)

    def test_partial_uppercase_unknown_and_relabelled_package_refused(self):
        manifest=json.loads((self.root/b.RUNTIME).read_bytes())
        rows=[row for row in manifest['files'] if Path(row['destination']).name in {r[0] for r in EXPECTED.values()}]
        self.assertEqual(len(rows),8)
        for mode in ('partial','uppercase','unknown','relabelled'):
            mutant=copy.deepcopy(manifest);mutant['files']=copy.deepcopy(rows)
            if mode=='partial':mutant['files']=mutant['files'][:1]
            if mode=='uppercase':mutant['files'][0]['destination']=mutant['files'][0]['destination'].upper()
            if mode=='unknown':mutant['files'][0]['destination']='assets/gameplay/bullet-281-8.hda'
            if mode=='relabelled':mutant['files'][0]['destination']='assets/gameplay/not-a-bullet.hda'
            path=self.base/('front-multi-package-'+mode+'.json');path.write_bytes(b.encoded(mutant))
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.package('--manifest',path)
        # Generic manifests with none of the body family keep their old meaning.
        generic=copy.deepcopy(manifest)
        generic['files']=[next(row for row in manifest['files'] if row['destination']=='README.txt')]
        path=self.base/'front-multi-generic-manifest.json';path.write_bytes(b.encoded(generic))
        code,report=self.package('--manifest',path)
        self.assertEqual((code,report['verified_files']),(0,1))

    def test_default_and_explicit_current_manifest_cannot_drop_entire_family(self):
        path=self.root/b.RUNTIME;original=path.read_bytes();manifest=json.loads(original)
        names={row[0] for row in EXPECTED.values()}
        manifest['files']=[row for row in manifest['files']
                           if Path(row['destination']).name not in names]
        self.assertEqual(len(manifest['files']),1007)
        path.write_bytes(b.encoded(manifest))
        before=self.outputs()
        try:
            for extra in ((),('--manifest',path)):
                with self.subTest(explicit=bool(extra)),self.assertRaises(ValueError):
                    self.package(*extra)
                self.assertEqual(self.outputs(),before)
        finally:path.write_bytes(original)

    def test_explicit_historical_eight_bullet_manifest_needs_no_current_selection(self):
        historical=json.loads((self.root/'packaging/runtime-assets-public63a89b3.json').read_bytes())
        names={row[0] for row in EXPECTED.values()}
        historical['files']=[row for row in historical['files']
                             if Path(row['destination']).name in names]
        self.assertEqual(len(historical['files']),8)
        for row in historical['files']:
            self.assertTrue(row['source_path'].startswith('assets/hd/packs/'))
            self.assertNotEqual(row.get('revision'),'current-single-source-front-multi')
        manifest=self.base/'front-multi-historical-eight-manifest.json'
        manifest.write_bytes(b.encoded(historical))
        removed={name:(self.root/name).read_bytes() for name in (c.SELECTION,c.MAPPING,c.HEADER)}
        for name in removed:(self.root/name).unlink()
        try:
            code,report=self.package('--manifest',manifest)
            self.assertEqual((code,report['verified_files']),(0,8))
            for name in removed:self.assertFalse((self.root/name).exists())
        finally:
            for name,data in removed.items():(self.root/name).write_bytes(data)

    def test_isolated_packager_accepts_explicit_historical_and_generic_manifests(self):
        isolated=self.base/'front-multi-isolated-packager';isolated.mkdir()
        script=isolated/'package_runtime.py'
        script.write_bytes((self.root/'scripts/package_runtime.py').read_bytes())
        historical=json.loads((self.root/'packaging/runtime-assets-public63a89b3.json').read_bytes())
        names={row[0] for row in EXPECTED.values()}
        historical['files']=[row for row in historical['files'] if Path(row['destination']).name in names]
        self.assertEqual(len(historical['files']),8)
        generic=json.loads((self.root/b.RUNTIME).read_bytes())
        generic['files']=[next(row for row in generic['files'] if row['destination']=='README.txt')]
        environment=dict(os.environ)
        environment.pop('PYTHONPATH',None);environment.pop('PYTHONHOME',None)
        for kind,manifest,count in (('historical',historical,8),('generic',generic,1)):
            path=self.base/f'front-multi-isolated-{kind}.json';path.write_bytes(b.encoded(manifest))
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
            elif mode=='tool':target=self.root/'scripts/build_current_front_multi.py'
            elif mode=='old_output':target=self.root/c.ROOT/EXPECTED[80121][0]
            elif mode in ('staged_hda','missing_staged'):target=stage/'files'/c.ROOT/EXPECTED[80121][0]
            elif mode=='request':target=stage/'request.json'
            else:target=stage/'plan.json'
            if mode=='missing_staged':target.unlink()
            else:target.write_bytes(target.read_bytes()+b'changed')
            before=self.outputs()
            with self.subTest(mode=mode),self.assertRaises((ValueError,OSError)):
                b.apply(self.root,stage)
            self.assertEqual(self.outputs(),before)

    def test_plan_duplicate_nonfinite_oversize_and_numeric_type_rejected(self):
        stage=self.stage();path=stage/'plan.json';original=path.read_bytes();before=self.outputs()
        plans=[b'{"schema":"a","schema":"b"}',b'{"x":NaN}',b' '*131073]
        numeric=json.loads(original);numeric['files'][0]['bytes']=float(numeric['files'][0]['bytes']);plans.append(b.encoded(numeric))
        for ordinal,raw in enumerate(plans):
            path.write_bytes(raw)
            with self.subTest(case=ordinal),self.assertRaises(ValueError):b.apply(self.root,stage)
            self.assertEqual(self.outputs(),before)
        path.write_bytes(original)

    def test_temporary_collision_and_stage_symlink_fail_before_writes(self):
        stage=self.stage(self.changed_source())
        temporary=self.root/(c.MAPPING+craft.SUFFIX)
        temporary.write_bytes(b'occupied temporary output')
        before=self.fixture.snapshot()
        with self.assertRaises(ValueError):b.apply(self.root,stage)
        self.assertEqual(self.fixture.snapshot(),before)
        temporary.unlink()
        linked=self.base/'front-multi-stage-link'
        linked.symlink_to(stage,target_is_directory=True)
        before=self.outputs()
        try:
            with self.assertRaises(ValueError):b.apply(self.root,linked)
            self.assertEqual(self.outputs(),before)
        finally:linked.unlink()

    def test_handled_replace_failure_rolls_back_all_changed_outputs(self):
        stage=self.stage(self.changed_source());before=self.fixture.snapshot()
        replace=os.replace;calls=0
        def failing(source,target):
            nonlocal calls
            calls+=1
            if calls==4:raise OSError('synthetic fourth replacement failure')
            return replace(source,target)
        with patch.object(craft.os,'replace',side_effect=failing):
            with self.assertRaisesRegex(OSError,'synthetic fourth'):b.apply(self.root,stage)
        self.assertGreaterEqual(calls,7,'expected rollback for three completed replacements')
        self.assertEqual(self.fixture.snapshot(),before)

    def test_casefold_and_hardlink_source_aliases_are_rejected(self):
        selected=self.selected();source=selected['resources'][0]['source_png']
        raw=(self.root/source).read_bytes()
        case_alias=Path(source).with_name(Path(source).stem.upper()+'.png').as_posix()
        self.write(case_alias,raw)
        selected['resources'][1].update(source_png=case_alias,source_sha256=b.sha(raw))
        with self.assertRaises(ValueError):c.generate(self.root,b.encoded(selected))
        for generated in (False,True):
            selected=self.selected()
            source=('authoring-inputs/charge-body-current/derived/bank9-id258.png'
                    if generated else selected['resources'][0]['source_png'])
            alias=f'authoring-inputs/front-multi-tests/hardlink-{generated}.png'
            path=self.root/alias;path.parent.mkdir(parents=True,exist_ok=True)
            os.link(self.root/source,path)
            selected['resources'][1].update(source_png=alias,source_sha256=b.sha(path.read_bytes()))
            try:
                with self.subTest(generated=generated),self.assertRaises(ValueError):
                    c.generate(self.root,b.encoded(selected))
            finally:path.unlink()

    def test_hardlink_to_frozen_art_is_not_an_editable_source(self):
        # Model frozen approved input inside the owned fixture; never alter the
        # real frozen file's inode/link count while other checks are reading it.
        relative=ART+'/output/bullet-121-8.png'
        source=self.write(relative,(ROOT/relative).read_bytes())
        alias='authoring-inputs/front-multi-tests/frozen-hardlink.png'
        target=self.root/alias;target.parent.mkdir(parents=True,exist_ok=True)
        os.link(source,target)
        selected=self.selected()
        selected['resources'][0].update(source_png=alias,source_sha256=b.sha(target.read_bytes()))
        try:
            with self.assertRaises(ValueError):c.generate(self.root,b.encoded(selected))
        finally:target.unlink()

    def test_unrelated_global_header_cannot_be_rebound_by_front_multi_apply(self):
        request=self.changed_source()
        header=self.root/'src/global_asset_registry.h'
        header.write_bytes(header.read_bytes()+b'\n/* synthetic unrelated global pin drift */\n')
        before=self.fixture.snapshot()
        with self.assertRaisesRegex(ValueError,'[Gg]lobal'):
            self.stage(request)
        self.assertEqual(self.fixture.snapshot(),before)

    def test_generated_plasma_pieces_and_casefold_aliases_are_not_independent_sources(self):
        before=self.outputs()
        for identity,density in ((1300022,4),(1300022,8),(1300023,4),(1300023,8),(1300024,4),(1300024,8)):
            original=f'authoring-inputs/plasma-projectile-current/derived/option-plasma-projectile-{identity-1300000}-{density}.png'
            raw=(self.root/original).read_bytes()
            alias=Path(original).with_name(Path(original).stem.upper()+'.png').as_posix()
            self.write(alias,raw)
            for source in (original,alias):
                selected=self.selected()
                selected['resources'][0].update(source_png=source,source_sha256=b.sha(raw))
                with self.subTest(identity=identity,density=density,path=source),self.assertRaisesRegex(ValueError,'[Gg]enerated'):
                    c.generate(self.root,b.encoded(selected))
        self.assertEqual(self.outputs(),before)

    def test_historical_rear_multi_derivatives_stay_frozen_after_163_164_edits(self):
        # Rear Multi 1310182/183 were derived from the frozen original 163/164.
        # They do not acquire live dependencies on the newly editable front art.
        runtime=json.loads((self.root/b.RUNTIME).read_bytes())
        rear={row['destination']:row for row in runtime['files']
              if Path(row['destination']).name in ('rear-multicannon-p1-bank8-182-8.hda','rear-multicannon-p1-bank8-183-8.hda')}
        self.assertEqual(len(rear),2)
        frozen={row['source_path']:(self.root/row['source_path']).read_bytes() for row in rear.values()}
        for index in (2,3):b.apply(self.root,self.stage(self.changed_source(index)))
        current={row['destination']:row for row in json.loads((self.root/b.RUNTIME).read_bytes())['files']}
        self.assertEqual(rear,{destination:current[destination] for destination in rear})
        self.assertEqual(frozen,{name:(self.root/name).read_bytes() for name in frozen})
        for kind in ('preview','debug'):
            target=self.base/('front-multi-rear-frozen-'+kind)
            craft.view(self.root,kind,target)
            for destination,row in rear.items():
                self.assertEqual((target/Path(destination).name).read_bytes(),frozen[row['source_path']])

    def test_all_twenty_two_existing_workflows_preserve_changed_front_multi(self):
        import build_current_art as art
        import build_current_hud as hud
        import build_current_tank_shell as tank
        import build_current_enemy_energy as energy
        b.apply(self.root,self.stage(self.changed_source(2)))
        before=self.outputs();count=0
        for family in PROFILES:
            target=self.base/('front-multi-coexist-'+family)
            art.stage(self.root,self.root/profile(family)['selection'],target,family)
            art.apply(self.root,target,family);count+=1
            with self.subTest(family=family):self.assertEqual(self.outputs(),before)
        for name,stage_fn,apply_fn,selection in (
                ('hud',hud.stage,hud.apply,hud.SELECTION),
                ('tank',tank.stage,tank.apply,tank.SELECTION),
                ('energy',energy.stage,energy.apply,energy.SELECTION),
                ('sidekick',body.stage,body.apply,body.SELECTION),
                ('craft267',craft.stage,craft.apply,craft.SELECTION),
                ('charge',body.charge_stage,body.charge_apply,bodies.CHARGE_SELECTION),
                ('mint-front',body.mf_stage,body.mf_apply,bodies.MF_SELECTION),
                ('plasma',plasma_builder.stage,plasma_builder.apply,plasma.SELECTION)):
            target=self.base/('front-multi-coexist-'+name)
            stage_fn(self.root,self.root/selection,target);apply_fn(self.root,target);count+=1
            with self.subTest(family=name):self.assertEqual(self.outputs(),before)
        self.assertEqual(count,22)

    def test_front_multi_source_drift_invalidates_every_dependent_workflow_plan(self):
        import build_current_art as art
        import build_current_hud as hud
        import build_current_tank_shell as tank
        import build_current_enemy_energy as energy
        workflows=[('art',art.stage,art.apply,profile('pulse')['selection']),
                   ('hud',hud.stage,hud.apply,hud.SELECTION),('tank',tank.stage,tank.apply,tank.SELECTION),
                   ('energy',energy.stage,energy.apply,energy.SELECTION),
                   ('sidekick',body.stage,body.apply,body.SELECTION),
                   ('craft267',craft.stage,craft.apply,craft.SELECTION),
                   ('charge',body.charge_stage,body.charge_apply,bodies.CHARGE_SELECTION),
                   ('mint-front',body.mf_stage,body.mf_apply,bodies.MF_SELECTION),
                   ('plasma',plasma_builder.stage,plasma_builder.apply,plasma.SELECTION)]
        for name,stage_fn,apply_fn,selection in workflows:
            self.fixture.setUp();target=self.base/('front-multi-dependent-'+name)
            stage_fn(self.root,self.root/selection,target)
            selected=self.selected();source=self.root/selected['resources'][0]['source_png']
            source.write_bytes(source.read_bytes()+b'\n')
            before=self.fixture.snapshot()
            with self.subTest(family=name),self.assertRaises(ValueError):apply_fn(self.root,target)
            self.assertEqual(self.fixture.snapshot(),before)

    def test_new_front_multi_tools_are_bound_and_invalidate_legacy_plan(self):
        names=('scripts/build_current_front_multi.py','scripts/current_front_multi_compatibility.py')
        fingerprints=bodies.authoring_input_fingerprints(self.root)
        for name in names:self.assertEqual(fingerprints[name],b.sha((self.root/name).read_bytes()))
        target=self.base/'front-multi-tool-drift-legacy-stage'
        body.stage(self.root,self.root/body.SELECTION,target)
        for name in names:
            path=self.root/name;original=path.read_bytes()
            path.write_bytes(original+b'\n# synthetic fixed Front Multi tool drift\n')
            before=self.fixture.snapshot()
            try:
                with self.subTest(tool=name),self.assertRaisesRegex(ValueError,'Stale or modified'):
                    body.apply(self.root,target)
                self.assertEqual(self.fixture.snapshot(),before)
            finally:path.write_bytes(original)

    def test_changed_charge_plasma_mint_front_and_front_multi_compose(self):
        def family_outputs(selection,mapping,root,filenames):
            selected=json.loads((self.root/selection).read_bytes())
            names={selection,mapping}|{root+'/'+filename for filename in filenames}
            if 'master' in selected:names|={row['source_png'] for row in selected['resources']}
            return {name:(self.root/name).read_bytes() for name in names}
        def mutate_png(source,output,increment=3,charge=False,whole=False):
            with Image.open(self.root/source) as original:image=original.copy()
            coordinates=((x,y) for y in range(80,110) for x in range(1,95)) if charge else (
                (x,y) for y in range(image.height) for x in range(image.width))
            xy=next(xy for xy in coordinates if image.getpixel(xy)[3]>0)
            if whole:
                channels=image.split()
                colored=Image.merge('RGBA',(channels[0].point(lambda value:(value+increment)%256),*channels[1:]))
                image=Image.composite(colored,image,channels[3].point(lambda value:255 if value else 0))
            else:
                rgba=image.getpixel(xy);image.putpixel(xy,((rgba[0]+increment)%256,*rgba[1:]))
            stream=io.BytesIO();image.save(stream,format='PNG');raw=stream.getvalue()
            self.write(output,raw)
            return dict(source_png=output,source_sha256=b.sha(raw))
        def apply_family(label,request,stage_fn,apply_fn):
            draft=self.base/('front-multi-compose-'+label+'.json');draft.write_bytes(b.encoded(request))
            target=self.base/('front-multi-compose-'+label)
            stage_fn(self.root,draft,target);apply_fn(self.root,target)
        front_before=self.outputs(shared=False)
        selected=json.loads((self.root/bodies.CHARGE_SELECTION).read_bytes())
        master=mutate_png(selected['master']['source_png'],'authoring-inputs/front-multi-cross/charge.png',charge=True)
        recipe=json.loads((self.root/selected['recipe']['path']).read_bytes());recipe['master_sha256']=master['source_sha256']
        recipe_raw=b.encoded(recipe);recipe_path='authoring-inputs/front-multi-cross/charge.json';self.write(recipe_path,recipe_raw)
        request=dict(schema=bodies.CHARGE_CANDIDATE_SCHEMA,version='synthetic-front-multi-charge',
                     master=master,recipe=dict(path=recipe_path,sha256=b.sha(recipe_raw)))
        apply_family('charge',request,body.charge_stage,body.charge_apply)
        self.assertEqual(self.outputs(shared=False),front_before)
        charge_before=family_outputs(bodies.CHARGE_SELECTION,bodies.CHARGE_MAPPING,bodies.CHARGE_ROOT,
                                     [bodies.charge_name(i) for i in bodies.CHARGE_IDS])
        b.apply(self.root,self.stage(self.changed_source(0)))
        self.assertEqual(charge_before,family_outputs(bodies.CHARGE_SELECTION,bodies.CHARGE_MAPPING,bodies.CHARGE_ROOT,
                                                     [bodies.charge_name(i) for i in bodies.CHARGE_IDS]))
        front_before=self.outputs(shared=False)
        selected=json.loads((self.root/plasma.SELECTION).read_bytes())
        request=dict(schema=plasma.CANDIDATE_SCHEMA,version='synthetic-front-multi-plasma',
                     master=mutate_png(selected['master']['source_png'],'authoring-inputs/front-multi-cross/plasma.png',whole=True),
                     recipe=copy.deepcopy(selected['recipe']))
        apply_family('plasma',request,plasma_builder.stage,plasma_builder.apply)
        self.assertEqual(self.outputs(shared=False),front_before)
        plasma_before=family_outputs(plasma.SELECTION,plasma.MAPPING,plasma.ROOT,[plasma.name(i,d) for i,d in plasma.PAIRS])
        b.apply(self.root,self.stage(self.changed_source(2)))
        self.assertEqual(plasma_before,family_outputs(plasma.SELECTION,plasma.MAPPING,plasma.ROOT,
                                                     [plasma.name(i,d) for i,d in plasma.PAIRS]))
        front_before=self.outputs(shared=False)
        selected=json.loads((self.root/bodies.MF_SELECTION).read_bytes());row=selected['resources'][3]
        row.update(mutate_png(row['source_png'],'authoring-inputs/front-multi-cross/frontblaster.png'))
        selected['version']='synthetic-front-multi-frontblaster'
        apply_family('mint-front',selected,body.mf_stage,body.mf_apply)
        self.assertEqual(self.outputs(shared=False),front_before)
        mint_before=family_outputs(bodies.MF_SELECTION,bodies.MF_MAPPING,bodies.MF_ROOT,
                                  [bodies.mf_name(i) for i in bodies.MF_IDS])
        b.apply(self.root,self.stage(self.changed_source(7)))
        self.assertEqual(mint_before,family_outputs(bodies.MF_SELECTION,bodies.MF_MAPPING,bodies.MF_ROOT,
                                                   [bodies.mf_name(i) for i in bodies.MF_IDS]))
        self.assertEqual(charge_before,family_outputs(bodies.CHARGE_SELECTION,bodies.CHARGE_MAPPING,bodies.CHARGE_ROOT,
                                                     [bodies.charge_name(i) for i in bodies.CHARGE_IDS]))
        self.assertEqual(plasma_before,family_outputs(plasma.SELECTION,plasma.MAPPING,plasma.ROOT,
                                                     [plasma.name(i,d) for i,d in plasma.PAIRS]))
        for check in (b.check,body.charge_check,body.mf_check,plasma_builder.check):
            self.assertEqual(check(self.root)['status'],'PASS')
        code,report=self.package();self.assertEqual((code,report['verified_files']),(0,1024))

    def test_sources_and_output_paths_reject_symlinks_and_stage_inside_repo(self):
        selected=self.selected();source=self.root/selected['resources'][0]['source_png']
        linked=self.root/'authoring-inputs/front-multi-tests/linked.png'
        linked.parent.mkdir(parents=True,exist_ok=True)
        linked.symlink_to(source)
        selected['resources'][0]['source_png']=linked.relative_to(self.root).as_posix()
        try:
            with self.assertRaises(ValueError):c.generate(self.root,b.encoded(selected))
        finally:linked.unlink()
        with self.assertRaises(ValueError):b.stage(self.root,self.root/c.SELECTION,self.root/'forbidden-stage')
        self.assertFalse((self.root/'forbidden-stage').exists())
        stage=self.stage(self.changed_source());path=self.root/c.ROOT/EXPECTED[80121][0]
        held=path.with_name('original-held.hda');path.rename(held);path.symlink_to(held)
        try:
            with self.assertRaises(ValueError):b.apply(self.root,stage)
        finally:path.unlink();held.rename(path)


if __name__=='__main__':
    unittest.main(verbosity=2)
