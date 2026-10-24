"""Finite aircraft authoring proof. Synthetic edits are not art approval.

Transaction tests isolate derivation to exercise rollback and stale plans;
full production derive/export is covered separately by integration validation.
"""
import copy
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_newshf_compatibility as c
import build_current_newshf as b
import build_current_craft267 as craft
BASE='a2b1bb5b6648fe835cd719d1764411a1773800ec'
enc=lambda x:(json.dumps(x,indent=2,sort_keys=True)+'\n').encode()

def old(path):
 return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)

class CurrentAircraftTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.masters={i:(ROOT/c.INPUT_ROOT/f'master-{i}.png').read_bytes() for i in c.SELECTORS}
  cls.legacy={name:old(name) for name in c.legacy.input_paths(ROOT)}
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='aircraft-focused-');self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)/'root';self.root.mkdir()
  for name,raw in self.legacy.items():self.write(name,raw)
  for i,raw in self.masters.items():self.write(c.INPUT_ROOT+f'/master-{i}.png',raw)
  recipe=enc(c.RECIPE);self.write(c.INPUT_ROOT+'/recipe.json',recipe)
  self.request=dict(schema=c.CANDIDATE_SCHEMA,version='test',masters=[dict(selector=i,source_png=c.INPUT_ROOT+f'/master-{i}.png',source_sha256=c.sha(self.masters[i])) for i in c.SELECTORS],recipe=dict(path=c.INPUT_ROOT+'/recipe.json',sha256=c.sha(recipe)))
 def write(self,name,raw):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);return p
 def generate(self):return c.generate(self.root,enc(self.request),True)
 def outputs(self,raw=None):
  req=raw or enc(self.request);candidate=json.loads(req)['schema']==c.CANDIDATE_SCHEMA
  selected,pngs,blobs=c.generate(self.root,req,candidate)
  rows=c.resource_rows(self.root,selected,blobs)
  return {c.SELECTION:b.encoded(selected),**pngs,**{c.ROOT+'/'+c.name(i):raw for i,raw in blobs.items()},c.HEADER:c.payload_header(rows),c.MAPPING:b.encoded(dict(schema='opentyrian-current-newshf-compatibility-v1',selection=c.SELECTION,version=selected['version'],files=rows))}
 def install(self):
  outputs=self.outputs()
  for name,raw in outputs.items():self.write(name,raw)
  return outputs
 def edit(self,selector):
  with Image.open(io.BytesIO(self.masters[selector])) as im:
   channels=im.split();im=Image.merge('RGBA',(channels[0].point(lambda x:(x+37)%256),*channels[1:]))
  s=io.BytesIO();im.save(s,format='PNG');raw=s.getvalue()
  self.write(c.INPUT_ROOT+f'/master-{selector}.png',raw)
  for row in self.request['masters']:
   if row['selector']==selector:row['source_sha256']=c.sha(raw)
 def snapshot(self):return {p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
 def test_bootstrap_all_six_png_rgba_hda_byteexact(self):
  _,pngs,blobs=self.generate()
  for i,spec in zip(c.EDIT_IDS,c.RECIPE['pieces']):
   self.assertEqual(blobs[i],old(c.legacy.OUTPUT+'/'+c.name(i)))
   self.assertEqual(pngs[c.png(i)],old(c.legacy.INPUT+f'/enemy-{spec["selector"]}-v1-bbox-fit-base{spec["base"]}.png'))
   self.assertEqual(struct.unpack('<4s6I',blobs[i][:28]),(b'HDR1',i,8,24,28,6,7))
 def test_current_full_nine_and_frozen_168_rows_exact(self):
  self.install();rows=c.load(self.root);oldrows=c.legacy.load(self.root)
  self.assertEqual(len(rows),9)
  for dest,row in rows.items():
   if row['record']==168:self.assertEqual(row,oldrows[dest])
  self.assertEqual({r['record'] for r in rows.values()},{163,167,168})
 def test_each_master_changes_only_its_three_roles(self):
  _,_,before=self.generate()
  for selector in c.SELECTORS:
   for row in self.request['masters']:self.write(row['source_png'],self.masters[row['selector']]);row['source_sha256']=c.sha(self.masters[row['selector']])
   self.edit(selector);_,_,after=self.generate()
   self.assertEqual({i for i in before if before[i]!=after[i]},{s['identity'] for s in c.RECIPE['pieces'] if s['selector']==selector})
 def test_fixed_physical_order_not_filenames_or_velocity(self):
  self.assertEqual([(s['selector'],s['base']) for s in c.RECIPE['pieces']],[(163,125),(163,123),(163,127),(167,3),(167,1),(167,5)])
  self.assertEqual(c.SELECTORS,(163,167));self.assertNotIn(168,c.SELECTORS)
 def test_recipe_cannot_change_even_coherently_rehashed(self):
  recipe=copy.deepcopy(c.RECIPE);recipe['pieces'][0]['xy'][0]+=1
  raw=enc(recipe);self.write(self.request['recipe']['path'],raw);self.request['recipe']['sha256']=c.sha(raw)
  with self.assertRaises(ValueError):self.generate()
 def test_selected_master_hash_stale_rejected(self):
  self.write(c.INPUT_ROOT+'/master-163.png',self.masters[163]+b'x')
  with self.assertRaises(ValueError):self.generate()
 def test_wrong_size_and_trailing_png_rejected(self):
  for raw in (self.masters[167],self.masters[163]+b'x'):
   self.write(c.INPUT_ROOT+'/master-163.png',raw);self.request['masters'][0]['source_sha256']=c.sha(raw)
   with self.assertRaises(ValueError):self.generate()
 def test_identity_order_alias_extra_bool_rejected(self):
  original=copy.deepcopy(self.request)
  for change in ('reverse','extra','alias','bool','168'):
   self.request=copy.deepcopy(original)
   if change=='reverse':self.request['masters'].reverse()
   elif change=='extra':self.request['masters'].append(copy.deepcopy(self.request['masters'][0]))
   elif change=='alias':self.request['masters'][0]['source_png']='../escape.png'
   elif change=='bool':self.request['masters'][0]['selector']=True
   else:self.request['masters'][0]['selector']=168
   with self.assertRaises(ValueError):self.generate()
 def test_stale_derived_hda_mapping_header_rejected_then_restored(self):
  outputs=self.install()
  for name in (c.png(c.EDIT_IDS[0]),c.ROOT+'/'+c.name(c.EDIT_IDS[0]),c.MAPPING,c.HEADER):
   original=(self.root/name).read_bytes();self.write(name,original+b'x')
   with self.assertRaises((ValueError,json.JSONDecodeError)):c.load(self.root)
   self.write(name,original);self.assertEqual(len(c.load(self.root)),9)
 def test_extra_output_rejected(self):
  self.install();self.write(c.ROOT+'/extra.hda',b'x')
  with self.assertRaises(ValueError):c.load(self.root)
 def test_symlink_master_and_parent_rejected(self):
  path=self.root/c.INPUT_ROOT/'master-163.png';external=Path(self.temp.name)/'outside.png';external.write_bytes(path.read_bytes());path.unlink();path.symlink_to(external)
  with self.assertRaises(ValueError):self.generate()
  path.unlink();path.write_bytes(external.read_bytes());folder=path.parent;other=Path(self.temp.name)/'outside';folder.rename(other);folder.symlink_to(other,target_is_directory=True)
  with self.assertRaises(ValueError):self.generate()
 def test_frozen168_tamper_not_hidden_by_current_layer(self):
  self.install();name=c.legacy.INPUT+'/enemy-168-v1-bbox-fit-base55.png';self.write(name,(self.root/name).read_bytes()+b'x')
  with self.assertRaises(ValueError):c.load(self.root)
 def test_coherent_legacy_repin_cannot_be_blessed_by_current_layer(self):
  self.install();name=c.legacy.INPUT+'/enemy-163-v1-bbox-fit-base125.png'
  with Image.open(self.root/name) as im:
   raw=bytearray(im.tobytes());offset=next(i for i in range(0,len(raw),4) if raw[i+3]);raw[offset]=(raw[offset]+1)%256
   image=Image.frombytes('RGBA',im.size,bytes(raw))
  stream=io.BytesIO();image.save(stream,format='PNG');self.write(name,stream.getvalue());digest=c.sha(stream.getvalue())
  manifest=json.loads((self.root/c.legacy.INPUT/'manifest.json').read_bytes());manifest['art'][0]['art_sha256']=digest
  self.write(c.legacy.INPUT+'/manifest.json',enc(manifest))
  provenance=json.loads((self.root/c.legacy.INPUT/'provenance.json').read_bytes());provenance['groups'][0]['poses'][0]['selected_png_sha256']=digest
  self.write(c.legacy.INPUT+'/provenance.json',enc(provenance))
  for name,raw in c.legacy.derive(self.root).items():self.write(name,raw)
  self.assertEqual(len(c.legacy.load(self.root)),9)
  with self.assertRaisesRegex(ValueError,'Frozen NEWSHF legacy evidence'):c.load(self.root)
 def test_duplicate_json_and_nonfinite_rejected(self):
  for raw in (b'{"schema":1,"schema":2}',b'{"schema":NaN}'):
   with self.assertRaises(ValueError):c.generate(self.root,raw,True)
 def test_input_closure_contains_legacy_and_current(self):
  self.install();paths=c.input_paths(self.root)
  self.assertTrue(set(self.legacy)<=paths)
  self.assertTrue({c.SELECTION,c.MAPPING,c.HEADER}|c.generated_paths()<=paths)
 def test_stage_readonly_apply_and_stale_plan(self):
  self.install();request=Path(self.temp.name)/'request.json';request.write_bytes(enc(self.request));stage=Path(self.temp.name)/'stage'
  deps=lambda root,selected:c.input_paths(root)
  with patch.object(b,'derive',side_effect=lambda root,raw:self.outputs(raw)),patch.object(b,'dependencies',side_effect=deps):
   before=self.snapshot();b.stage(self.root,request,stage);self.assertEqual(before,self.snapshot());b.apply(self.root,stage)
   plan=json.loads((stage/'plan.json').read_bytes());plan['files'][0]['bytes']+=1;(stage/'plan.json').write_bytes(enc(plan))
   with self.assertRaises(ValueError):b.apply(self.root,stage)
 def test_staged_bytes_tamper_and_write_failure_rollback(self):
  self.install();fixed_paths=c.input_paths(self.root);self.edit(163)
  request=Path(self.temp.name)/'request.json';request.write_bytes(enc(self.request));stage=Path(self.temp.name)/'stage'
  with patch.object(b,'derive',side_effect=lambda root,raw:self.outputs(raw)),patch.object(b,'dependencies',side_effect=lambda root,selected:fixed_paths):
   b.stage(self.root,request,stage);first=next(iter(self.outputs()));p=stage/'files'/first;raw=p.read_bytes();p.write_bytes(raw+b'x')
   before=self.snapshot()
   with self.assertRaises(ValueError):b.apply(self.root,stage)
   self.assertEqual(before,self.snapshot());p.write_bytes(raw)
   original=os.replace;calls=[0]
   def fail(src,dst):
    calls[0]+=1
    if calls[0]==3:raise OSError('injected write failure')
    return original(src,dst)
   with patch.object(craft.os,'replace',side_effect=fail):
    with self.assertRaises(OSError):b.apply(self.root,stage)
   self.assertEqual(before,self.snapshot())

if __name__=='__main__':unittest.main()
