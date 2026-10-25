"""Finite SVG authoring; synthetic edits prove propagation, not visual approval.
Transaction mocks isolate handled-error rollback, not crash/concurrent atomicity.
"""
import copy
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_rear_p7_compatibility as c
import build_current_rear_p7 as b
import build_current_craft267 as craft
from build_current_art import fnv
BASE='525de2b9d5b4605dd6bf997cee644c9ac39546c1'
ART='assets/hd/artwork/player-rear-multicannon-p7-mode2-twins-v1'
def frozen(name): return subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
def encode(value): return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()

class CurrentRearP7Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='rear-p7-focused-');self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.root=self.base/'root';self.root.mkdir()
        self.master_paths={294:c.INPUT_ROOT+'/master-294.svg'};self.recipe_path=c.INPUT_ROOT+'/recipe.json'
        self.master=frozen(ART+'/sources/rear-multi-294.svg')
        self.write(self.master_paths[294],self.master);self.write(self.recipe_path,encode(c.RECIPE))
        # The shared payload table now validates the independent six-output family.
        import current_rear39_compatibility as rear39
        for name in rear39.input_paths(ROOT) | {rear39.MAPPING}:
            self.write(name,(ROOT/name).read_bytes())
        import current_rear1_compatibility as rear1
        for name in rear1.input_paths(ROOT) | {rear1.MAPPING}:
            self.write(name,(ROOT/name).read_bytes())
        import current_rear_lobes_compatibility as rear_lobes
        for name in rear_lobes.input_paths(ROOT) | {rear_lobes.MAPPING}:
            self.write(name,(ROOT/name).read_bytes())
        import current_rear281_compatibility as rear281
        for name in rear281.input_paths(ROOT) | {rear281.MAPPING}:
            self.write(name, (ROOT/name).read_bytes())
        self.request=dict(schema=c.CANDIDATE_SCHEMA,version='fixture',masters=[dict(selector=294,source_svg=self.master_paths[294],source_sha256=c.sha(self.master))],recipe=dict(path=self.recipe_path,sha256=c.sha(encode(c.RECIPE))))
    def write(self,name,raw):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);return p
    def generate(self): return c.generate(self.root,encode(self.request),candidate=True)
    def change_master(self,selector=294):
        raw=self.master.replace(b'#fffaa1',b'#a1faff');self.assertNotEqual(raw,self.master)
        self.write(self.master_paths[294],raw);self.request['masters'][0]['source_sha256']=c.sha(raw)
    def snapshot(self):return {p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
    def install(self):
        selected,pngs,blobs=self.generate();self.write(c.SELECTION,encode(selected))
        for name,raw in pngs.items():self.write(name,raw)
        rows=[]
        for pair,raw in blobs.items():
            name=c.ROOT+'/'+c.name(*pair);self.write(name,raw)
            rows.append(dict(identity=pair[0],density=pair[1],source_path=name,destination='assets/gameplay/'+c.name(*pair),sha256=c.sha(raw)))
        self.write(c.MAPPING,encode(dict(schema='opentyrian-current-rear-p7-compatibility-v1',selection=c.SELECTION,version=selected['version'],files=rows)))
        self.write(c.HEADER,c.payload_header({p:fnv(raw[28:]) for p,raw in blobs.items()}))
        return selected,pngs,blobs
    def test_bootstrap_matches_public_png_hda_and_geometry(self):
        selected,pngs,blobs=self.generate();contract=json.loads(frozen(ART+'/pins.json'))
        for row in contract['outputs']:
            pair=(row['key'],row['density']);raw=blobs[pair]
            self.assertEqual(c.sha(raw),row['hda_sha256']);self.assertEqual(c.sha(pngs[c.png(*pair)]),row['png_sha256'])
            self.assertEqual(struct.unpack('<4s6I',raw[:28]),(b'HDR1',*pair,12,14,0,0))
        self.assertEqual(len(selected['resources']),4)
    def test_one_edit_changes_four_outputs_and_exact_flips(self):
        _,_,before=self.generate();self.change_master();_,_,after=self.generate()
        self.assertEqual({p for p in c.PAIRS if after[p]!=before[p]},set(c.PAIRS))
        for density in (4,8):
            a=after[(1310294,density)][28:];z=after[(1310295,density)][28:];w=12*density
            expected=b''.join(a[(y*w+x)*4:(y*w+x+1)*4] for y in range(14*density) for x in reversed(range(w)))
            self.assertEqual(z,expected)
            self.assertTrue(all(not any(a[p:p+3]) for p in range(0,len(a),4) if a[p+3]==0))
        self.assertIn('for(const d of [4,8])',c.DRIVER);self.assertIn('density:72*d/8',c.DRIVER)
        self.assertNotIn('.resize(',c.DRIVER)
    def test_only_four_of_fifty_header_cells_editable_and_fixture_guard(self):
        _,_,blobs=self.generate();before=c.payload_header({p:fnv(raw[28:]) for p,raw in blobs.items()})
        old=frozen('src/rear_multi_p1_pins.h').decode();line=next(x for x in old.splitlines() if x.startswith('#define REAR_P1_RGBA_PINS '))
        self.assertIn(line.encode(),before)
        self.change_master();_,_,blobs=self.generate();after=c.payload_header({p:fnv(raw[28:]) for p,raw in blobs.items()})
        vals=lambda raw:re.findall(rb'UINT64_C\(0x([a-f0-9]{16})\)',raw)
        self.assertEqual([i for i,(a,z) in enumerate(zip(vals(before),vals(after))) if a!=z],[34,35,36,37])
        self.assertEqual(vals(after)[18],b'0000000000000000');self.assertEqual(vals(after)[20],b'0000000000000000')
        self.assertIn(b'#ifndef REAR_P1_RGBA_PINS',after)
        with self.assertRaises(ValueError):c.payload_header({})
    def test_derived_and_mapping_header_tamper_rejected(self):
        selected,pngs,blobs=self.install();self.assertEqual(len(c.load(self.root)),4)
        for name in [c.HEADER,c.MAPPING,*pngs,c.ROOT+'/'+c.name(*c.PAIRS[0])]:
            raw=(self.root/name).read_bytes();self.write(name,raw+b'bad')
            with self.subTest(name=name),self.assertRaises(ValueError):c.load(self.root)
            self.write(name,raw)
        self.assertEqual(len(c.input_paths(self.root)),11)
    def test_svg_external_script_entity_geometry_and_bounds_rejected(self):
        for raw in (*['<!DOCTYPE svg [<!ENTITY x "test">]><svg/>'.encode(enc) for enc in ('utf-16','utf-32','utf-16-le','utf-32-le')], b'<!DOCTYPE svg><svg/>',b'<?xml version="1.0"?><svg/>',self.master.replace(b'<defs>',b'<defs><script/>'),self.master.replace(b'<defs>',b'<defs><image href="file:///etc/passwd"/>'),self.master.replace(b'url(#streak)',b'url(https://evil)'),self.master.replace(b'width="96"',b'width="192"'),self.master.replace(b'translate(3 3)',b'translate(1e999 3)'),self.master.replace(b'translate(3 3)',b'translate(10001 3)'),b'x'*65537):
            with self.subTest(raw=raw[:50]),self.assertRaises(ValueError):c.svg(raw)
    def test_svg_literal_nonfinite_tokens_rejected(self):
        for raw in (self.master.replace(b'translate(3 3)', b'translate(NaN 3)'),
                    self.master.replace(b'translate(3 3)', b'translate(Infinity 3)'),
                    self.master.replace(b'cx="0"', b'cx="NaN"'),
                    self.master.replace(b'M1.4 11', b'MInfinity 11'),
                    self.master.replace(b'translate(3 3)', b'translate(nAn 3)'),
                    self.master.replace(b'translate(3 3)', b'translate(InFiNiTy 3)'),
                    self.master.replace(b'cx="0"', b'cx="iNf"')):
            self.assertNotEqual(raw, self.master)
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                c.svg(raw)

    def test_strict_selection_json_recipe_and_path(self):
        for value in (True,294.0,295):
            bad=copy.deepcopy(self.request);bad['masters'][0]['selector']=value
            with self.assertRaises(ValueError):c.selection(self.root,encode(bad),True)
        for value in ('../outside.svg',ART+'/sources/rear-multi-294.svg'):
            bad=copy.deepcopy(self.request);bad['masters'][0]['source_svg']=value
            with self.assertRaises(ValueError):c.selection(self.root,encode(bad),True)
        for raw in (b'{"a":1,"a":2}',b'{"a":NaN}',b' '*131073):
            with self.assertRaises(ValueError):c.parse(raw)
        bad=copy.deepcopy(c.RECIPE);bad['densities']=[8,4]
        with self.assertRaises(ValueError):c.recipe(encode(bad))
        target=self.root/self.master_paths[294];target.unlink();target.symlink_to(ROOT/c.INPUT_ROOT/'master-294.svg')
        with self.assertRaises(ValueError):self.generate()
    def test_tool_profile_golden_failure_timeout_output_bounds(self):
        c.check_tool()
        with patch.object(c,'NODE_VERSION','v0'):
            with self.assertRaises(ValueError):self.generate()
        with patch.object(c,'GOLDEN_HASHES',{}):
            with self.assertRaisesRegex(ValueError,'golden'):self.generate()
        before=self.snapshot()
        for error in (FileNotFoundError(),subprocess.TimeoutExpired('node',30)):
            with patch.object(c.subprocess,'run',side_effect=error),self.assertRaises(ValueError):self.generate()
        def oversized(argv,**kw):
            kw['stdout'].write(b'x'*(1024*1024+1));return subprocess.CompletedProcess(argv,0)
        with patch.object(c.subprocess,'run',side_effect=oversized),self.assertRaises(ValueError):self.generate()
        self.assertEqual(self.snapshot(),before)
    def test_fixed_argv_stdin_no_inherited_node_options(self):
        calls=[];real=c.subprocess.run
        def record(argv,**kw):calls.append((argv,kw));return real(argv,**kw)
        with patch.dict(os.environ,{'NODE_OPTIONS':'--require=/untrusted'}),patch.object(c.subprocess,'run',side_effect=record):self.generate()
        self.assertEqual(len(calls),2)
        for argv,kw in calls:
            self.assertEqual(argv,[c.NODE,'--max-old-space-size=128','-e',c.DRIVER,c.SHARP]);self.assertNotIn('NODE_OPTIONS',kw['env']);self.assertNotIn('shell',kw);self.assertEqual(kw['timeout'],30)
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
            self.change_master(294)
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

    def test_handled_write_failure_rolls_back_and_success_installs_one_hda(self):
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


if __name__=='__main__': unittest.main()
