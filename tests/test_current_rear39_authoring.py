"""Finite data-only geometry authoring; synthetic edits prove propagation, not visual approval.
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
import current_rear39_compatibility as c
import build_current_rear39 as b
import build_current_craft267 as craft
from build_current_art import fnv
P7PINS={(1310294,4):'fe4f61938de0c031',(1310294,8):'60735166b4a9ea50',(1310295,4):'73bdb95e757a0f29',(1310295,8):'826ac5b753ea8b84'}
BASE='525de2b9d5b4605dd6bf997cee644c9ac39546c1'
ART='assets/hd/artwork/player-rear-multicannon-p7-mode2-twins-v1'
def frozen(name): return subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
def encode(value): return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()

class CurrentRear39Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='rear39-focused-');self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.root=self.base/'root';self.root.mkdir()
        self.master_paths={39:c.INPUT_ROOT+'/master-39.json'};self.recipe_path=c.INPUT_ROOT+'/recipe.json'
        self.master=c.GOLDEN_MASTER
        self.write(self.master_paths[39],self.master);self.write(self.recipe_path,encode(c.RECIPE))
        self.request=dict(schema=c.CANDIDATE_SCHEMA,version='fixture',masters=[dict(selector=39,source_json=self.master_paths[39],source_sha256=c.sha(self.master))],recipe=dict(path=self.recipe_path,sha256=c.sha(encode(c.RECIPE))))
    def write(self,name,raw):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);return p
    def generate(self): return c.generate(self.root,encode(self.request),candidate=True)
    def change_master(self,selector=39):
        raw=self.master.replace(b'11 5.25',b'10.9 5.25');self.assertNotEqual(raw,self.master)
        self.write(self.master_paths[39],raw);self.request['masters'][0]['source_sha256']=c.sha(raw)
    def snapshot(self):return {p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
    def install(self):
        selected,pngs,blobs=self.generate();self.write(c.SELECTION,encode(selected))
        for name,raw in pngs.items():self.write(name,raw)
        rows=[]
        for pair,raw in blobs.items():
            name=c.ROOT+'/'+c.name(*pair);self.write(name,raw)
            rows.append(dict(identity=pair[0],density=pair[1],source_path=name,destination='assets/gameplay/'+c.name(*pair),sha256=c.sha(raw)))
        self.write(c.MAPPING,encode(dict(schema='opentyrian-current-rear39-compatibility-v1',selection=c.SELECTION,version=selected['version'],files=rows)))
        self.write(c.HEADER,c.payload_header({p:fnv(raw[28:]) for p,raw in blobs.items()},P7PINS))
        return selected,pngs,blobs
    def test_bootstrap_six_exact_and_generated_single_path(self):
        selected,pngs,blobs=self.generate()
        actual,svg=c.render(self.master,include_svg=True)
        self.assertEqual(c.sha(svg),'cb7f4493d3b72280f04579632236a5f4a179473460a913ab1c4739593570e112')
        self.assertEqual(svg.count(c.geometry(self.master)['geometry']['path'].encode()),34)
        for pair,(png,rgba) in actual.items():
            self.assertEqual((c.sha(png),c.sha(rgba)),c.GOLDEN_HASHES[pair])
            self.assertEqual(struct.unpack('<4s6I',blobs[pair][:28]),(b'HDR1',*pair,12,14,0,0))
            old='assets/hd/packs/packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test/'+c.name(*pair)
            self.assertEqual(blobs[pair],frozen(old))
    def test_true_geometry_edit_changes_exactly_six_and_only_six_table_cells(self):
        _,_,before=self.generate();self.change_master();_,_,after=self.generate()
        self.assertEqual({p for p in c.PAIRS if after[p]!=before[p]},set(c.PAIRS))
        header=lambda rows:c.payload_header({p:fnv(raw[28:]) for p,raw in rows.items()},P7PINS)
        vals=lambda raw:re.findall(rb'UINT64_C\(0x([a-f0-9]{16})\)',raw)
        a,z=vals(header(before)),vals(header(after))
        self.assertEqual([i for i in range(50) if a[i]!=z[i]],[0,1,12,13,26,27])
        self.assertEqual(a[34:38],z[34:38]);self.assertEqual(z[18],b'0'*16);self.assertEqual(z[20],b'0'*16)
        for d in (4,8):
            raw=after[(1310039,d)][28:]
            for target in (40,41):self.assertEqual(c.compose(raw,d,target)[0],after[(1310000+target,d)][28:])
        self.assertIn('for(const d of [4,8])',c.DRIVER);self.assertNotIn('.resize(',c.DRIVER)
    def test_geometry_schema_finite_path_and_stops_fail_closed(self):
        valid=json.loads(self.master)
        mutations=[('path','M0 0 C1 1 2 2 Z'),('path','M0 0 A1 1 0 0 1 2 2Z'),('path','M0 0 LNaN 2Z'),('path','M0 0 L1e999 2Z'),('path','M0 0 L15 2Z'),('path','M0 0 L1 2Z<script/>')]
        for key,value in mutations:
            bad=copy.deepcopy(valid);bad['geometry'][key]=value
            with self.subTest(value=value),self.assertRaises(ValueError):c.geometry(encode(bad))
        for n in [True,float('inf'),float('nan'),1e300,0]:
            bad=copy.deepcopy(valid);bad['geometry']['heat']['L']=n
            with self.subTest(n=n),self.assertRaises(ValueError):c.geometry(encode(bad))
        for bad in [dict(valid,external='file:///tmp/a'),dict(valid,geometry=dict(valid['geometry'],extra=1)),dict(valid,gradient={'type':'elliptical-radial','stops':[['0','#ffffff'],['0','#000000']]})]:
            with self.assertRaises(ValueError):c.geometry(encode(bad))
        for raw in [b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":1e999}',self.master.decode().encode('utf-16'),self.master+b'\0',b' '*131073]:
            with self.assertRaises(ValueError):c.parse(raw)
    def test_fixed_recipe_selection_and_paths(self):
        for value in (True,39.0,40):
            bad=copy.deepcopy(self.request);bad['masters'][0]['selector']=value
            with self.assertRaises(ValueError):c.selection(self.root,encode(bad),True)
        for value in ('../outside.json',c.INPUT_ROOT+'/other.json'):
            bad=copy.deepcopy(self.request);bad['masters'][0]['source_json']=value
            with self.assertRaises(ValueError):c.selection(self.root,encode(bad),True)
        bad=copy.deepcopy(c.RECIPE);bad['derived']['40']['parts'][0][2]=-3
        with self.assertRaises(ValueError):c.recipe(encode(bad))
        target=self.root/self.master_paths[39];target.unlink();target.symlink_to(ROOT/c.INPUT_ROOT/'master-39.json')
        with self.assertRaises(ValueError):self.generate()
    def test_overlap_clipping_hidden_rgb_and_invalid_density_rejected(self):
        for d in (4,8):
            data=bytearray(12*14*d*d*4);data[-1]=255
            with self.assertRaises(ValueError):c.compose(data,d,40)
            data=bytearray(b'\xff'*len(data))
            with self.assertRaises(ValueError):c.compose(data,d,41)
            data=bytearray(len(data));data[0]=1
            with self.assertRaises(ValueError):c.compose(data,d,40)
        with self.assertRaises(ValueError):c.compose(b'',True,40)
    def test_golden_profile_timeout_and_output_limits(self):
        c.check_tool()
        with patch.object(c,'NODE_VERSION','v0'),self.assertRaises(ValueError):self.generate()
        with patch.object(c,'GOLDEN_HASHES',{}),self.assertRaisesRegex(ValueError,'golden'):self.generate()
        for error in (FileNotFoundError(),subprocess.TimeoutExpired('node',30)):
            with patch.object(c.subprocess,'run',side_effect=error),self.assertRaises(ValueError):self.generate()
        def oversized(argv,**kw):
            kw['stdout'].write(b'x'*(1024*1024+1));return subprocess.CompletedProcess(argv,0)
        with patch.object(c.subprocess,'run',side_effect=oversized),self.assertRaises(ValueError):self.generate()
    def test_fixed_argv_no_inherited_node_options(self):
        calls=[];real=c.subprocess.run
        def record(argv,**kw):calls.append((argv,kw));return real(argv,**kw)
        with patch.dict(os.environ,{'NODE_OPTIONS':'--require=/untrusted'}),patch.object(c.subprocess,'run',side_effect=record):self.generate()
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
            self.change_master(39)
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
            self.assertEqual(len(list((self.root/c.ROOT).glob('*.hda'))),6)
            selected=json.loads((self.root/c.SELECTION).read_bytes())
            self.assertEqual(len(selected['resources']),6)


if __name__=='__main__': unittest.main()
