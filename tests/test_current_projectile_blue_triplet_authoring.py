"""Pure authoring/package checks, not sparse inventory or runtime admission proof."""
from pathlib import Path
import contextlib,copy,hashlib,importlib.util,io,json,os,shutil,struct,sys,tempfile,unittest
from unittest import mock
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_projectile_blue_triplet_compatibility as c
import current_projectile91_compatibility as old91
import current_projectile145_compatibility as old145
import current_projectile61_compatibility as old61
import build_current_projectile_blue_triplet as build
from build_current_art import fnv

PAYLOADS={1520101:'b143b168b2eb5270c092980f760d6f5f7c47b852c7c6ef378b0ca1e11360b991',
          1520120:'61df8e476bd503aa0f0e9f83285fc38c081fa62fdf59a784b52f0679e7167bd6',
          1520139:'b7e5646f32dbbf5c4a0167003c4111f0450282473c3af7999d09b509bb307923'}

def copy_inputs(target,paths):
    for name in paths:
        p=target/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)

class ProjectileBlueTripletAuthoring(unittest.TestCase):
    def selected(self):return json.loads((ROOT/c.SELECTION).read_text())
    def synthetic_rows(self):
        # Intentionally independent of packaging/runtime-assets-v1.json, whose
        # current epoch is integrated separately by the runtime/package owner.
        return [dict(r,group='gameplay',revision=c.REVISION) for r in c.load(ROOT).values()]

    def test_exact_three_role_geometry_and_independent_payloads(self):
        rows=c.load(ROOT);self.assertEqual(len(rows),3);self.assertEqual(c.IDS,(1520101,1520120,1520139))
        for identity in c.IDS:
            blob=(ROOT/c.ROOT/c.name(identity)).read_bytes()
            self.assertEqual(len(blob),43036)
            self.assertEqual(struct.unpack('<4s6I',blob[:28]),(b'HDR1',identity,8,12,14,0,0))
            self.assertEqual(hashlib.sha256(blob[28:]).hexdigest(),PAYLOADS[identity])
        self.assertEqual(len(set(PAYLOADS.values())),3)

    def test_png_exact_approved_candidate_and_transport(self):
        for identity,selector in zip(c.IDS,c.SELECTORS):
            p=ROOT/c.png(identity);self.assertEqual(p.read_bytes(),(ROOT/c.INPUT_ROOT/f'candidate-{selector}-96x112.png').read_bytes())
            self.assertEqual(c.sha(p.read_bytes()),c.APPROVED_PNG_SHA256[selector])
            with Image.open(p) as im:
                self.assertEqual(im.mode,'RGBA');self.assertEqual(im.size,(96,112))
                self.assertEqual(im.tobytes(),(ROOT/c.ROOT/c.name(identity)).read_bytes()[28:])

    def test_exact_coverage_matrices_and_canonical_transparent_pixels(self):
        contract=c.coverage(ROOT)
        for identity,selector,count in zip(c.IDS,c.SELECTORS,(164,168,130)):
            raw=(ROOT/c.ROOT/c.name(identity)).read_bytes()[28:];self.assertEqual(c.MASKS[selector].count('1'),count)
            expected=contract['members'][str(selector)]
            for y in range(112):
                for x in range(96):
                    pixel=raw[(y*96+x)*4:(y*96+x)*4+4]
                    if c.MASKS[selector][(y//8)*12+x//8]=='0' or pixel[3]==0:self.assertEqual(pixel,b'\0'*4)
            matrix=[[max(raw[((y*8+dy)*96+x*8+dx)*4+3] for dy in range(8) for dx in range(8)) for x in range(12)] for y in range(14)]
            self.assertEqual(matrix,expected['max_alpha_per_native_cell']);self.assertEqual(c.validate_payload(ROOT,selector,raw),matrix)
            used=[matrix[y][x] for y in range(14) for x in range(12) if c.MASKS[selector][y*12+x]=='1']
            actual=(sum(a>=200 for a in used),sum(0<a<200 for a in used),used.count(0))
            self.assertEqual(actual,{101:(132,26,6),120:(107,61,0),139:(130,0,0)}[selector])
            zero=[(y,x) for y in range(14) for x in range(12) if c.MASKS[selector][y*12+x]=='1' and matrix[y][x]==0]
            self.assertEqual(zero,list(c.ZERO_CELLS_101) if selector==101 else [])

    def test_real_generated_detail_not_native_nearest(self):
        for identity in c.IDS:
            raw=(ROOT/c.ROOT/c.name(identity)).read_bytes()[28:];varied=0
            for y in range(14):
                for x in range(12):
                    colors={raw[((y*8+dy)*96+x*8+dx)*4:((y*8+dy)*96+x*8+dx)*4+4] for dy in range(8) for dx in range(8)}
                    varied+=len(colors)>2
            self.assertGreater(varied,90);self.assertGreater(sum(0<a<255 for a in raw[3::4]),1000)

    def test_independent_fixed_sources_crops_and_exact_alpha_endpoints(self):
        self.assertEqual([c.CROPS[s] for s in c.SELECTORS],[(0,0,1160,1355),(350,0,810,1355),(224,1550,502,1870)])
        self.assertEqual(len({r['source_png'] for r in c.SOURCES}),3)
        self.assertEqual([r['source_size'] for r in c.SOURCES],[[1160,1355],[1160,1355],[725,2168]])
        contract=c.coverage(ROOT)
        for selector,identity in zip(c.SELECTORS,c.IDS):
            raw=(ROOT/c.ROOT/c.name(identity)).read_bytes()[28:];m=contract['members'][str(selector)]
            self.assertEqual(list(raw[3:384:4]),m['first_row_alpha']);self.assertEqual(list(raw[-381::4]),m['last_row_alpha'])
        # v2 deliberately does NOT assert shared-master contiguous seams; exact
        # selected endpoints/matrices/payload replace that old design premise.

    def test_rebuild_exact_eight_outputs(self):
        outputs=build.products(ROOT);self.assertEqual(len(outputs),8)
        for name,data in outputs.items():self.assertEqual((ROOT/name).read_bytes(),data)

    def test_identity_density_closed_including_bools(self):
        for identity,density in [(101,8),(1510061,8),(1520138,8),(True,8),(1520101,True),(1520101,4),(1520101,8.0),('1520101',8)]:
            with self.subTest(identity=identity,density=density):
                with self.assertRaises(ValueError):c.name(identity,density)
                with self.assertRaises(ValueError):c.png(identity,density)

    def test_selection_closed_schema_version_and_three_sources(self):
        original=self.selected();cases=[]
        for key,value in [('schema',c.CANDIDATE_SCHEMA),('schema','opentyrian-current-projectile-blue-triplet-authoring-v1'),('version',True),('version',''),('version','x'*129),('sources',[]),('sources',original['sources'][:2]),('sources',original['sources']+[original['sources'][0]]),('sources',{}),('sources',[True]*3),('sources',list(reversed(original['sources'])))]:
            j=copy.deepcopy(original);j[key]=value;cases.append(j)
        for i in range(3):
            j=copy.deepcopy(original);j['sources'][i]=copy.deepcopy(j['sources'][(i+1)%3]);cases.append(j)
        j=copy.deepcopy(original);j['extra']=0;cases.append(j)
        for j in cases:
            with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(j).encode())
        candidate=copy.deepcopy(original);candidate['schema']=c.CANDIDATE_SCHEMA
        self.assertEqual(c.selection(ROOT,json.dumps(candidate).encode(),True)['sources'],original['sources'])
        with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(original).encode(),1)

    def test_selection_duplicate_keys_rejected(self):
        raw=(ROOT/c.SELECTION).read_bytes();raw=raw.replace(b'"version":',b'"version":"shadow", "version":',1)
        with self.assertRaises(ValueError):c.selection(ROOT,raw)

    def test_each_source_selector_path_hash_size_crop_and_encoding_negatives(self):
        original=self.selected()
        for i,source in enumerate(c.SOURCES):
            cases=[('selector',True),('selector',float(source['selector'])),('selector',61),('source_png','../private-reference.png'),('source_png',source['source_png'].upper()),('source_png','/tmp/master.png'),('source_png',c.INPUT_ROOT+'/raw/../raw/'+source['source_png'].split('/')[-1]),('source_png',True),('source_sha256','0'*64),('source_sha256',source['source_sha256'].upper()),('source_sha256',True),('source_size',[True,1355]),('source_size',[float(source['source_size'][0]),source['source_size'][1]]),('source_size',{}),('source_size',source['source_size']+[1]),('crop',[False,0,1160,1355]),('crop',[float(v) for v in source['crop']]),('crop',source['crop'][:-1]),('crop',[0,0,1,1]),('png_compress_level',True),('png_compress_level',float(source['png_compress_level'])),('png_compress_level',0)]
            for key,value in cases:
                j=copy.deepcopy(original);j['sources'][i][key]=value
                with self.subTest(member=i,key=key,value=value):
                    with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(j).encode())
            for key in source:
                j=copy.deepcopy(original);del j['sources'][i][key]
                with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(j).encode())
            j=copy.deepcopy(original);j['sources'][i]['extra']=1
            with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(j).encode())

    def test_each_missing_changed_symlink_hardlink_source_registration_coverage_rejected(self):
        raw=(ROOT/c.SELECTION).read_bytes();paths={r['source_png'] for r in c.SOURCES}|{c.REGISTRATION,c.COVERAGE}
        with tempfile.TemporaryDirectory() as td:
            t=Path(td)
            with self.assertRaises((ValueError,OSError)):c.selection(t,raw)
            copy_inputs(t,paths)
            for name in sorted(paths):
                p=t/name;original=p.read_bytes()
                with self.subTest(path=name):
                    p.unlink()
                    with self.assertRaises((ValueError,OSError)):c.selection(t,raw)
                    p.write_bytes(original+b'changed')
                    with self.assertRaises(ValueError):c.selection(t,raw)
                    p.unlink();p.symlink_to(ROOT/name)
                    with self.assertRaises(ValueError):c.selection(t,raw)
                    p.unlink();p.write_bytes(original);link=t/'extra-input-link';os.link(p,link)
                    with self.assertRaises(ValueError):c.selection(t,raw)
                    link.unlink();self.assertEqual(c.selection(t,raw)['sources'],self.selected()['sources'])

    def test_complete_synthetic_three_consumer_package_accepts(self):
        rows=self.synthetic_rows();c.validate_runtime_rows(ROOT,{'files':rows},True)
        c.validate_runtime_rows(ROOT,{'files':rows},False)
        c.validate_runtime_rows(ROOT,{'files':rows+[dict(source_path='unrelated/file',destination='unrelated/file')]},True)

    def test_missing_duplicate_or_aliased_package_member_rejected(self):
        original=self.synthetic_rows();cases=[[],original+original[:1]]
        for i in range(3):
            cases.append(original[:i]+original[i+1:])
            for key,value in [('destination',original[i]['destination'].upper()),('source_path',original[i]['source_path'].upper()),('source_path','elsewhere/'+c.name(c.IDS[i]))]:
                rows=copy.deepcopy(original);rows[i][key]=value;cases.append(rows)
        for rows in cases:
            with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':rows},True)

    def test_each_stale_package_member_and_foreign_alias_rejected(self):
        original=self.synthetic_rows()
        for i in range(3):
            for key,value in [('sha256','0'*64),('group','old'),('revision','old'),('revision',c.REVISION.upper())]:
                rows=copy.deepcopy(original);rows[i][key]=value
                with self.subTest(member=i,key=key):
                    with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':rows},True)
        for suffix in ['999-8.hda','101-4.hda']:
            alias=dict(source_path='elsewhere/enemy-projectile-blue-triplet-'+suffix,destination='elsewhere/enemy-projectile-blue-triplet-'+suffix)
            with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':original+[alias]},False)

    def test_manifest_container_and_path_types_rejected(self):
        for manifest in [None,{}, {'files':True},{'files':[True]},{'files':[{'source_path':True,'destination':'x'}]}]:
            with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,manifest,True)
        with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':[]},1)

    def test_unrelated_historical_manifest_does_not_consume_new_inputs(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.object(c,'load',side_effect=AssertionError('Unexpected new input read')):
            c.validate_runtime_rows(Path(td),{'files':[]},False)
            c.validate_runtime_rows(Path(td),{'files':[{'source_path':'old/source','destination':'old/output'}]},False)

    def test_mapping_and_each_pin_are_closed(self):
        selected,pngs,blobs=c.generate(ROOT,(ROOT/c.SELECTION).read_bytes());pins={p:fnv(b[28:]) for p,b in blobs.items()}
        header=c.payload_header(pins);self.assertEqual(len(set(pins.values())),3)
        for identity in c.IDS:self.assertIn(f'CURRENT_PROJECTILE_BLUE_TRIPLET_{identity}_PAYLOAD_FNV'.encode(),header)
        for broken in [{},dict(list(pins.items())[:2]),{**pins,(1510061,8):'0'*16},dict.fromkeys(c.PAIRS,True)]:
            with self.assertRaises(ValueError):c.payload_header(broken)
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);copy_inputs(t,c.input_paths(ROOT));mapping=json.loads((t/c.MAPPING).read_text())
            for i in range(3):
                j=copy.deepcopy(mapping);j['files'][i]['identity']=True;(t/c.MAPPING).write_text(json.dumps(j))
                with self.assertRaises(ValueError):c.load(t)

    def test_missing_and_bad_members_do_not_touch_old_authoring(self):
        # Authoring independence only, not C admission. Each unchanged old
        # family is tested against every bad new member using bounded copies;
        # no links and no need to materialize all old masters simultaneously.
        for module in (old91,old145,old61):
            with self.subTest(old_family=module.__name__), tempfile.TemporaryDirectory() as td:
                t=Path(td);copy_inputs(t,module.input_paths(ROOT));expected=module.load(t)
                with self.assertRaises((ValueError,OSError)):c.load(t)
                copy_inputs(t,c.input_paths(ROOT));c.load(t)
                for identity in c.IDS:
                    p=t/c.ROOT/c.name(identity);original=p.read_bytes();p.unlink()
                    with self.assertRaises((ValueError,OSError)):c.load(t)
                    self.assertEqual(module.load(t),expected)
                    p.write_bytes(original+b'bad')
                    with self.assertRaises(ValueError):c.load(t)
                    self.assertEqual(module.load(t),expected);p.write_bytes(original)
                self.assertEqual(module.load(ROOT),expected)

    def test_old91_145_61_selected_bytes_remain_pinned(self):
        expected=['2940279a66281c16838d4e070421a581ea0e4b5bb91cf85a1cbc532902933e4c',
                  'e4863397d4d7e9874e96e642ce6596c90e99009014b746491016c0423e099c83',
                  '3530c27302a2cb3d26830711cd4b94a01aacbfad748c91aea219bbc81b0c5c29']
        for module,pin in zip((old91,old145,old61),expected):
            self.assertEqual(next(iter(module.load(ROOT).values()))['sha256'],pin)

    def test_builder_refuses_linked_derivative_without_changing_target(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);copy_inputs(t,c.input_paths(ROOT));p=t/c.png(c.IDS[0]);outside=t/'outside.png';outside.write_bytes(b'retain-target');p.unlink();p.symlink_to(outside)
            with mock.patch.object(sys,'argv',['builder','--root',str(t),'--write']),contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(ValueError):build.main()
            self.assertEqual(outside.read_bytes(),b'retain-target')


    def test_each_zero_cell_alpha_promotion_is_rejected(self):
        original=(ROOT/c.ROOT/c.name(1520101)).read_bytes()[28:]
        for y,x in c.ZERO_CELLS_101:
            raw=bytearray(original);raw[((y*8)*96+x*8)*4+3]=1
            with self.subTest(row=y,column=x):
                with self.assertRaises(ValueError):c.validate_payload(ROOT,101,raw)

    def test_low_cell_matrix_and_color_changes_rejected(self):
        for selector,identity in zip(c.SELECTORS,c.IDS):
            original=(ROOT/c.ROOT/c.name(identity)).read_bytes()[28:]
            # Same alpha distribution cannot authorize changed color/payload.
            raw=bytearray(original);p=next(i for i in range(0,len(raw),4) if raw[i+3]);raw[p]^=1
            with self.assertRaises(ValueError):c.validate_payload(ROOT,selector,raw)
            raw=bytearray(original);p=next(i for i in range(0,len(raw),4) if raw[i+3]>1);raw[p+3]-=1
            self.assertNotEqual(raw,original)
            with self.assertRaises(ValueError):c.validate_payload(ROOT,selector,raw)
        raw=bytearray((ROOT/c.ROOT/c.name(1520101)).read_bytes()[28:]);raw[0]=1
        with self.assertRaises(ValueError):c.validate_payload(ROOT,101,raw)
        with self.assertRaises(ValueError):c.validate_payload(ROOT,True,raw)
        with self.assertRaises(ValueError):c.validate_payload(ROOT,101,raw[:-1])

    def test_duplicate_keys_rejected_inside_each_source(self):
        original=(ROOT/c.SELECTION).read_bytes()
        for source in c.SOURCES:
            marker=('"selector": '+str(source['selector'])).encode()
            raw=original.replace(marker,b'"selector": 0, '+marker,1)
            with self.assertRaises(ValueError):c.selection(ROOT,raw)

    def test_139_original_source_registered_png_hda_remain_exact(self):
        self.assertEqual(c.SOURCES[2]['source_sha256'],'0904cafbedf92ca30f3bc132a7f39eb8febc44a69e4cbdac6f85ff00c511ca57')
        self.assertEqual(c.sha((ROOT/c.SOURCES[2]['source_png']).read_bytes()),c.SOURCES[2]['source_sha256'])
        self.assertEqual(c.sha((ROOT/c.png(1520139)).read_bytes()),'f8e674afbea3148ed6b72f703c68b935e33731f35723da902caa0ff5000d162c')
        self.assertEqual(c.sha((ROOT/c.ROOT/c.name(1520139)).read_bytes()),'47a6941988a2e2a4835859dfc1cf12f2481b2bf29bab18be94307b408cf34942')

    def test_standalone_rebuild_exact_candidates_and_pins_without_game_data(self):
        path=ROOT/c.INPUT_ROOT/'rebuild.py';spec=importlib.util.spec_from_file_location('blue_selected_rebuild',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        outputs=m.products(ROOT/c.INPUT_ROOT);self.assertEqual(set(outputs),{'candidate-101-96x112.png','candidate-120-96x112.png','candidate-139-96x112.png','payload-pins.json'})
        for name,data in outputs.items():self.assertEqual((ROOT/c.INPUT_ROOT/name).read_bytes(),data)
        with tempfile.TemporaryDirectory() as td:
            t=Path(td)
            for name in ['registration.json','coverage-contract.json']+[r['source_png'].removeprefix(c.INPUT_ROOT+'/') for r in c.SOURCES]:
                p=t/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/c.INPUT_ROOT/name,p)
            self.assertEqual(m.products(t),outputs)

    def test_builder_refuses_hardlinked_derivative_without_changing_target(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);copy_inputs(t,c.input_paths(ROOT));p=t/c.png(c.IDS[0]);outside=t/'outside.png';os.link(p,outside);before=outside.read_bytes()
            with mock.patch.object(sys,'argv',['builder','--root',str(t),'--write']),contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(ValueError):build.main()
            self.assertEqual(outside.read_bytes(),before)

if __name__=='__main__':unittest.main()
