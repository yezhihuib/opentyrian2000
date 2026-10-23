"""Single-master Charge tests. Synthetic changes stay in isolated cloud fixtures."""
import contextlib,copy,hashlib,io,json,os,struct,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_current_sidekick_body as b
import current_sidekick_body_compatibility as c
import build_current_craft267 as craft
import package_runtime as pack
from current_art_policy import PROFILES,profile
EXPECTED=(258,259,260,277,278,279,296,297,298)
BOOTSTRAP_SHA='71d2a06af1cd548f91918f478006fe70a9fca87ec08cbdd22ad2faf9dc1723aa'


class ChargeAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_current_sidekick_body_authoring import CurrentSidekickBodyTests
        cls.fixture_class=CurrentSidekickBodyTests;cls.fixture_class.setUpClass()
        cls.fixture=CurrentSidekickBodyTests();cls.root=cls.fixture_class.root;cls.base=cls.fixture_class.base
        for name in craft.BASES.values():
            for path in (ROOT/'assets/hd/packs'/name).rglob('*'):
                if path.is_file():cls.fixture_class.initial[path.relative_to(ROOT).as_posix()]=path.read_bytes()
        cls.serial=0
    @classmethod
    def tearDownClass(cls):cls.fixture_class.tearDownClass()
    def setUp(self):self.fixture.setUp()
    def selected(self):return json.loads((self.root/c.CHARGE_SELECTION).read_bytes())
    def write(self,name,data):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);return path
    def stage(self,request=None):
        type(self).serial+=1;ordinal=type(self).serial
        draft=self.base/f'charge-request-{ordinal}.json';draft.write_bytes(b.encoded(request or self.selected()))
        target=self.base/f'charge-stage-{ordinal}';b.charge_stage(self.root,draft,target);return target
    def outputs(self):
        names={c.CHARGE_SELECTION,c.CHARGE_MAPPING,b.RUNTIME}|{r['source_png'] for r in self.selected()['resources']}|{c.CHARGE_ROOT+'/'+c.charge_name(i) for i in c.CHARGE_IDS}
        return {name:(self.root/name).read_bytes() for name in names}
    def changed_master(self):
        selected=self.selected();master=Image.open(self.root/selected['master']['source_png']).copy()
        # Independent one-pixel diagnostic modification to an opaque, non-core body pixel.
        xy=next((x,y) for y in range(80,110) for x in range(1,95) if master.getpixel((x,y))[3]>0 and master.getpixel((x,y))[0]<250)
        rgb=master.getpixel(xy);master.putpixel(xy,(rgb[0]+3,*rgb[1:]))
        stream=io.BytesIO();master.save(stream,format='PNG');raw=stream.getvalue()
        name='authoring-inputs/charge-test/new-master.png';self.write(name,raw)
        recipe=json.loads((self.root/selected['recipe']['path']).read_bytes());recipe['master_sha256']=b.sha(raw)
        recipe_name='authoring-inputs/charge-test/new-recipe.json';recipe_raw=b.encoded(recipe);self.write(recipe_name,recipe_raw)
        return dict(schema=c.CHARGE_CANDIDATE_SCHEMA,version='synthetic-single-master-edit',master=dict(source_png=name,source_sha256=b.sha(raw)),recipe=dict(path=recipe_name,sha256=b.sha(recipe_raw)))
    def package(self,*extra):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):code=pack.main(['--source-root',str(self.root),*map(str,extra)])
        return code,json.loads(output.getvalue())

    def test_frozen_bootstrap_nine_geometry_and_twelve_inputs(self):
        raw=(ROOT/'tests/fixtures/charge-body-bootstrap-v1.json').read_bytes();self.assertEqual(b.sha(raw),BOOTSTRAP_SHA)
        fixture=json.loads(raw);self.assertEqual(tuple(i-1450000 for i in c.CHARGE_IDS),EXPECTED)
        self.assertEqual(len(c.charge_input_paths(self.root)),12)
        self.assertEqual(b.charge_check(self.root)['resources'],9)
        for expected,row in zip(fixture['files'],self.selected()['resources']):
            self.assertEqual(expected['identity'],row['identity']);self.assertEqual(expected['png_sha256'],row['source_sha256'])
            data=(self.root/c.CHARGE_ROOT/c.charge_name(row['identity'])).read_bytes()
            self.assertEqual(data[:28],struct.pack('<4s6I',b'HDR1',row['identity'],8,12,14,0,0))
            self.assertEqual(b.sha(data),expected['hda_sha256'])
            self.assertEqual(b.sha(data[28:]),expected['rgba_sha256'])

    def test_master_edit_propagates_nine_two_views_and_1015_runtime(self):
        before=self.outputs();six={r['source_path']:(self.root/r['source_path']).read_bytes() for r in c.load(self.root).values()}
        request=self.changed_master();stage=self.stage(request);self.assertEqual(self.outputs(),before)
        b.charge_apply(self.root,stage);self.assertEqual(b.charge_check(self.root)['status'],'PASS')
        now=self.outputs();derived={r['source_png'] for r in self.selected()['resources']}
        self.assertEqual(sum(before[p]!=now[p] for p in derived),9)
        self.assertEqual(sum(before[p]!=now[p] for p in before if p.endswith('.hda')),9)
        self.assertEqual(six,{name:(self.root/name).read_bytes() for name in six})
        mapping=c.charge_load(self.root)
        for kind in ('preview','debug'):
            target=self.base/('master-update-'+kind);report=craft.view(self.root,kind,target)
            self.assertEqual((report['files'],len(report['current_overlays'])),(650,169))
            frozen=self.root/'assets/hd/packs'/craft.BASES[kind]
            nonoverlays=[p for p in frozen.rglob('*') if p.is_file() and p.relative_to(frozen).as_posix() not in report['current_overlays']]
            self.assertEqual(len(nonoverlays),481)
            for path in nonoverlays:self.assertEqual(path.read_bytes(),(target/path.relative_to(frozen)).read_bytes())
            for destination,row in mapping.items():self.assertEqual((target/Path(destination).name).read_bytes(),(self.root/row['source_path']).read_bytes())
        code,report=self.package();self.assertEqual((code,report['verified_files']),(0,1015))
        target=self.base/'charge-runtime-copy'
        evidence=os.environ.get('CHARGE_REAL_COPY_OUTPUT')
        if evidence:
            # Explicit cloud-only acceptance path. Keep every real filesystem,
            # permission and free-space guard. Never retry a rejected copy.
            target=Path(evidence)
            args=[sys.executable,'-B',str(self.root/'scripts/package_runtime.py'),'--source-root',str(self.root),'--build','--output',str(target)]
            result=subprocess.run(args,capture_output=True,text=True)
            receipt=dict(command=args,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,selection=self.selected(),charge_mapping=list(mapping.values()),scope='Synthetic one-master update, nine derived frames, two650-file views and real1015-file CLI copy; no game/Windows execution')
            receipt_path=target.with_name(target.name+'-receipt.json')
            with receipt_path.open('xb') as stream:stream.write(b.encoded(receipt))
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads(result.stdout);code=result.returncode
        else:
            # Isolated content test only; not real permission/setup acceptance.
            with patch.object(Path,'chmod',return_value=None):code,report=self.package('--build','--output',target)
        self.assertEqual((code,report['verified_files']),(0,1015))
        for destination,row in mapping.items():self.assertEqual((target/destination).read_bytes(),(self.root/row['source_path']).read_bytes())
        self.assertEqual(len(json.loads((target/'RUNTIME-INVENTORY.json').read_bytes())['files']),1015)

    def test_candidate_cannot_supply_or_hide_derived_fields(self):
        request=self.changed_master()
        for key,value in [('resources',self.selected()['resources']),('generator','candidate-script.py'),('unknown',0)]:
            mutant=dict(request,**{key:value})
            with self.subTest(key=key),self.assertRaises(ValueError):b.charge_derive(self.root,b.encoded(mutant))
        installed=self.selected();del installed['resources']
        with self.assertRaises(ValueError):b.charge_derive(self.root,b.encoded(installed))

    def test_rehashed_hand_edited_derived_png_rejected_everywhere(self):
        selected=self.selected();row=selected['resources'][0];path=self.root/row['source_png']
        image=Image.open(path).copy();image.putpixel((48,80),(7,11,13,255));image.save(path)
        row['source_sha256']=b.sha(path.read_bytes());(self.root/c.CHARGE_SELECTION).write_bytes(b.encoded(selected))
        for name,fn in [('check',lambda:b.charge_check(self.root)),('stage',lambda:self.stage(selected)),('preview',lambda:craft.view(self.root,'preview',self.base/'bad-view')),('package',lambda:self.package())]:
            with self.subTest(entry=name),self.assertRaisesRegex(ValueError,'does not match master'):
                fn()
        self.assertFalse((self.base/'bad-view').exists())

    def test_coherently_rehashed_hda_mapping_and_manifest_still_rejected(self):
        mapping=json.loads((self.root/c.CHARGE_MAPPING).read_bytes());row=mapping['files'][0];path=self.root/row['source_path'];data=bytearray(path.read_bytes());data[-1]^=1;path.write_bytes(data);row['sha256']=b.sha(data)
        (self.root/c.CHARGE_MAPPING).write_bytes(b.encoded(mapping))
        runtime=json.loads((self.root/b.RUNTIME).read_bytes());target=next(r for r in runtime['files'] if r['destination']==row['destination']);target['sha256']=b.sha(data);target['git_blob']=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();(self.root/b.RUNTIME).write_bytes(b.encoded(runtime))
        with self.assertRaisesRegex(ValueError,'HDA does not match master'):self.package()

    def test_mapping_identity_float_and_bool_rejected(self):
        path=self.root/c.CHARGE_MAPPING;original=path.read_bytes()
        for value in (1450258.0,True):
            mapping=json.loads(original);mapping['files'][0]['identity']=value;path.write_bytes(b.encoded(mapping))
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'compatibility mapping'):c.charge_load(self.root)
        path.write_bytes(original)

    def test_partial_uppercase_and_unknown_charge_package_refused(self):
        manifest=json.loads((self.root/b.RUNTIME).read_bytes());charge=[r for r in manifest['files'] if 'option-charge-' in r['destination']]
        for mode in ('partial','uppercase','unknown'):
            mutant=copy.deepcopy(manifest);mutant['files']=copy.deepcopy(charge[:1])
            if mode=='uppercase':mutant['files'][0]['destination']='assets/gameplay/OPTION-CHARGE-BANK9-258-8.HDA';mutant['files'][0]['source_path']='generic-custom.hda'
            if mode=='unknown':mutant['files'][0]['destination']='assets/gameplay/option-charge-bank9-999-8.hda'
            path=self.base/('package-'+mode+'.json');path.write_bytes(b.encoded(mutant))
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'exactly nine'):self.package('--manifest',path,'--platform','windows')

    def test_schema_id_geometry_and_path_guards(self):
        selected=self.selected()
        for mode in ('bool','missing','order','path','master_escape','recipe_escape'):
            mutant=copy.deepcopy(selected)
            if mode=='bool':mutant['resources'][0]['identity']=True
            if mode=='missing':mutant['resources'].pop()
            if mode=='order':mutant['resources'].reverse()
            if mode=='path':mutant['resources'][0]['source_png']='authoring-inputs/unapproved.png'
            if mode=='master_escape':mutant['master']['source_png']='authoring-inputs/../../escape.png'
            if mode=='recipe_escape':mutant['recipe']['path']='authoring-inputs/../escape.json'
            with self.subTest(mode=mode),self.assertRaises(ValueError):c.charge_generate(self.root,b.encoded(mutant))
        recipe=json.loads((self.root/selected['recipe']['path']).read_bytes())
        for key,value in [('output_size',[192,224]),('spark_footprint',[[0,0,255]]*30),('highlight_strength',float('nan')),('arbitrary_code','evil.py')]:
            mutant=dict(recipe,**{key:value})
            with self.subTest(key=key),self.assertRaises(ValueError):c._charge_recipe(b.encoded(mutant),selected['master']['source_sha256'])
        for raw in [b'{}', (self.root/selected['master']['source_png']).read_bytes()+b'trailing']:
            with self.assertRaises(ValueError):c._charge_image(raw)

    def test_stale_stage_inputs_tools_and_staged_png_fail_before_writes(self):
        for mode in ('master','recipe_tool','staged_png'):
            self.fixture.setUp();request=self.changed_master();stage=self.stage(request);before=self.outputs()
            target=(self.root/request['master']['source_png'] if mode=='master' else self.root/'scripts/current_charge_body_recipe.py' if mode=='recipe_tool' else stage/'files'/c.charge_png(c.CHARGE_IDS[0]))
            target.write_bytes(target.read_bytes()+b'\n')
            with self.subTest(mode=mode),self.assertRaises(ValueError):b.charge_apply(self.root,stage)
            self.assertEqual(self.outputs(),before)

    def test_charge_plan_duplicate_nonfinite_oversize_and_numeric_types_rejected(self):
        stage=self.stage();path=stage/'plan.json';original=path.read_bytes();before=self.outputs()
        plans=[b'{"schema":"a","schema":"b"}',b'{"x":NaN}',b' '*131073]
        numeric=json.loads(original);numeric['files'][0]['bytes']=float(numeric['files'][0]['bytes']);plans.append(b.encoded(numeric))
        for ordinal,raw in enumerate(plans):
            path.write_bytes(raw)
            with self.subTest(case=ordinal),self.assertRaises(ValueError):b.charge_apply(self.root,stage)
            self.assertEqual(self.outputs(),before)
        path.write_bytes(original)

    def test_all_nineteen_existing_authoring_stages_preserve_charge(self):
        import build_current_art as art,build_current_hud as hud,build_current_tank_shell as tank,build_current_enemy_energy as energy
        before=self.outputs();count=0
        for family in PROFILES:
            stage=self.base/('coexist-'+family);art.stage(self.root,self.root/profile(family)['selection'],stage,family);art.apply(self.root,stage,family);count+=1
            self.assertEqual(self.outputs(),before)
        for name,module,selection in [('hud',hud,hud.SELECTION),('tank',tank,tank.SELECTION),('energy',energy,energy.SELECTION),('sidekick',b,b.SELECTION),('craft267',craft,craft.SELECTION)]:
            stage=self.base/('coexist-'+name);module.stage(self.root,self.root/selection,stage);module.apply(self.root,stage);count+=1
            self.assertEqual(self.outputs(),before)
        self.assertEqual(count,19)

    def test_new_charge_recipe_comment_invalidates_each_legacy_builder_plan(self):
        import build_current_art as art,build_current_hud as hud,build_current_tank_shell as tank,build_current_enemy_energy as energy
        for name,module,selection in [('art',art,profile('pulse')['selection']),('hud',hud,hud.SELECTION),('tank',tank,tank.SELECTION),('energy',energy,energy.SELECTION),('sidekick',b,b.SELECTION),('craft267',craft,craft.SELECTION)]:
            self.fixture.setUp();stage=self.base/('tool-drift-'+name);module.stage(self.root,self.root/selection,stage)
            tool=self.root/'scripts/current_charge_body_recipe.py';tool.write_bytes(tool.read_bytes()+b'\n# changed fixed Charge tool\n')
            with self.subTest(family=name),self.assertRaisesRegex(ValueError,'Stale or modified'):module.apply(self.root,stage)


if __name__=='__main__':unittest.main(verbosity=2)
