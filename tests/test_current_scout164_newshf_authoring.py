"""Finite authoring tests; synthetic mutations never become production artwork."""
import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_scout164_newshf_compatibility as c
import build_current_scout164_newshf as b

class Scout164Authoring(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'root';self.root.mkdir()
        for name in c.INPUTS:
            path=self.root/c.INPUT_ROOT/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/c.INPUT_ROOT/name,path)
        self.refresh()
    def refresh(self):
        self.raw=json.dumps(dict(schema=c.SCHEMA,version='synthetic-test-only',inputs={c.INPUT_ROOT+'/'+name:c.sha((self.root/c.INPUT_ROOT/name).read_bytes()) for name in c.INPUTS})).encode()
    def master(self,base=11):return self.root/c.INPUT_ROOT/f'master-base{base}.png'
    def stage(self):
        request=Path(self.tmp.name)/'request.json';request.write_bytes(self.raw)
        destination=Path(self.tmp.name)/'stage';b.stage(self.root,request,destination);return destination
    def test_exact_resources_and_consumers(self):
        _,pngs,blobs,rows=c.generate(self.root,self.raw)
        self.assertEqual(tuple(blobs),c.IDS);self.assertEqual(tuple(r['base'] for r in rows),c.BASES)
        for identity,base,row in zip(c.IDS,c.BASES,rows):
            self.assertEqual(row['records'],[164]);self.assertEqual(struct.unpack('<4s6I',blobs[identity][:28]),(b'HDR1',identity,8,24,28,6,7))
            self.assertEqual(blobs[identity][28:],Image.open(self.master(base)).tobytes())
            self.assertEqual(row['sha256'],c.sha(blobs[identity]));self.assertEqual(row['source_png_sha256'],c.sha(pngs[c.png(identity)]))
    def test_native_zero_and_soft_alpha_preserved(self):
        blobs=c.generate(self.root,self.raw)[2]
        for identity,base in zip(c.IDS,c.BASES):
            mask=Image.open(self.root/c.INPUT_ROOT/f'native-mask-base{base}.png').resize((192,224),Image.Resampling.NEAREST).tobytes();raw=blobs[identity][28:]
            self.assertTrue(any(0<a<255 for a in raw[3::4]),base)
            for n,covered in enumerate(mask):
                if not covered:self.assertEqual(raw[n*4:n*4+4],b'\0'*4)
    def test_one_master_edit_changes_only_one_pose(self):
        before=c.generate(self.root,self.raw)[2];path=self.master();im=Image.open(path).convert('RGBA')
        point=next((x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3]);pixel=im.getpixel(point)
        im.putpixel(point,((pixel[0]+1)%256,*pixel[1:]));im.save(path);self.refresh();after=c.generate(self.root,self.raw)[2]
        self.assertNotEqual(before[c.IDS[0]],after[c.IDS[0]])
        self.assertEqual([before[i] for i in c.IDS[1:]],[after[i] for i in c.IDS[1:]])
    def test_unselected_edit_rejected(self):
        self.master().write_bytes(b'bad')
        with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_rehashed_mask_mutation_rejected(self):
        Image.new('L',(24,28),255).save(self.root/c.INPUT_ROOT/c.MASK_NAMES[0]);self.refresh()
        with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_external_support_rejected(self):
        im=Image.open(self.master()).convert('RGBA');im.putpixel((0,0),(255,0,0,1));im.save(self.master());self.refresh()
        with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_hidden_rgb_rejected(self):
        im=Image.open(self.master()).convert('RGBA');im.putpixel((0,0),(255,0,0,0));im.save(self.master());self.refresh()
        with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_empty_wrong_canvas_and_rgb_rejected(self):
        for mode,size in [('RGBA',(192,224)),('RGBA',(191,224)),('RGB',(192,224))]:
            Image.new(mode,size).save(self.master());self.refresh()
            with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_trailing_png_and_crc_rejected(self):
        original=self.master().read_bytes()
        for raw in [original+b'x',original[:33]+bytes([original[33]^1])+original[34:]]:
            self.master().write_bytes(raw);self.refresh()
            with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_extra_input_duplicate_json_and_identity_rejected(self):
        selected=json.loads(self.raw);selected['inputs']['bad']='0'*64
        with self.assertRaises(ValueError):c.generate(self.root,json.dumps(selected).encode())
        with self.assertRaises(ValueError):c.generate(self.root,b'{"schema":1,"schema":2}')
        for identity in [True,2100027,2100031,'2100028']:
            with self.assertRaises(ValueError):c.name(identity)
    def test_symlink_master_rejected(self):
        saved=Path(self.tmp.name)/'master.png';shutil.copyfile(self.master(),saved);self.master().unlink();self.master().symlink_to(saved)
        with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_stage_apply_and_load(self):
        destination=self.stage();b.apply(self.root,destination);self.assertEqual(len(c.load(self.root)),3)
        (self.root/c.HEADER).write_bytes(b'bad')
        with self.assertRaises(ValueError):c.load(self.root)
    def test_tampered_stage_has_no_writes(self):
        destination=self.stage();(destination/'files'/c.HEADER).write_bytes(b'tampered')
        with self.assertRaises(ValueError):b.apply(self.root,destination)
        self.assertFalse((self.root/c.HEADER).exists())
    def test_stale_input_has_no_writes(self):
        destination=self.stage();self.master().write_bytes(b'bad')
        with self.assertRaises(ValueError):b.apply(self.root,destination)
        self.assertFalse((self.root/c.HEADER).exists())
    def test_changed_derived_or_mapping_rejected(self):
        destination=self.stage();b.apply(self.root,destination)
        path=self.root/c.ROOT/c.name(c.IDS[0]);raw=path.read_bytes();path.write_bytes(raw+b'x')
        with self.assertRaises(ValueError):c.load(self.root)
        path.write_bytes(raw);mapping=self.root/c.MAPPING;selected=json.loads(mapping.read_bytes());selected['files'][0]['base']=13;mapping.write_text(json.dumps(selected))
        with self.assertRaises(ValueError):c.load(self.root)

if __name__=='__main__':unittest.main()
