import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_linked_newshf_compatibility as c
import build_current_linked_newshf as b

class LinkedAuthoring(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'root'; self.root.mkdir()
        for n in c.MASKS+c.CHANGE_MASKS:
            target=self.root/c.INPUT_ROOT/n; target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/c.INPUT_ROOT/n,target)
        Image.new('RGBA',(192,672),(30,80,120,255)).save(self.root/c.INPUT_ROOT/c.INPUTS[0])
        for n in c.INPUTS[1:]: Image.new('RGBA',(192,224)).save(self.root/c.INPUT_ROOT/n)
        self.refresh()
    def refresh(self):
        self.raw=json.dumps(dict(schema=c.SCHEMA,version='synthetic-test-only',inputs={c.INPUT_ROOT+'/'+n:c.sha((self.root/c.INPUT_ROOT/n).read_bytes()) for n in c.INPUTS+c.MASKS+c.CHANGE_MASKS})).encode()
    def test_six_order_and_shared_top(self):
        _,pngs,blobs,rows=c.generate(self.root,self.raw)
        self.assertEqual(tuple((r['record'],r['base']) for r in rows),c.PAIRS)
        self.assertEqual(blobs[c.IDS[0]][28:],blobs[c.IDS[1]][28:])
        self.assertEqual(len(pngs),6)
        for row in rows:
            im=Image.open(self.root/c.INPUT_ROOT/f"mask-{row['base']}.png").convert('L').resize((192,224),Image.Resampling.NEAREST)
            self.assertEqual(blobs[row['identity']][31::4],im.tobytes())
    def test_edit_propagates_both_states(self):
        before=c.generate(self.root,self.raw)[2]
        Image.new('RGBA',(192,672),(99,80,120,255)).save(self.root/c.INPUT_ROOT/c.INPUTS[0]); self.refresh()
        after=c.generate(self.root,self.raw)[2]
        self.assertTrue(all(before[i]!=after[i] for i in c.IDS))
    def test_overlay_outside_change_mask_rejected(self):
        Image.new('RGBA',(192,224),(255,0,0,255)).save(self.root/c.INPUT_ROOT/c.INPUTS[1]); self.refresh()
        with self.assertRaises(ValueError): c.generate(self.root,self.raw)
    def test_changed_master_rejected(self):
        (self.root/c.INPUT_ROOT/c.INPUTS[0]).write_bytes(b'bad')
        with self.assertRaises(ValueError): c.generate(self.root,self.raw)
    def test_rehashed_mutated_mask_rejected(self):
        Image.new('L',(24,28),255).save(self.root/c.INPUT_ROOT/c.MASKS[0]); self.refresh()
        with self.assertRaises(ValueError): c.generate(self.root,self.raw)
    def test_partial_alpha_rejected(self):
        Image.new('RGBA',(192,224),(255,0,0,127)).save(self.root/c.INPUT_ROOT/c.INPUTS[1]); self.refresh()
        with self.assertRaises(ValueError): c.generate(self.root,self.raw)
    def test_tampered_stage_is_read_only(self):
        request=Path(self.tmp.name)/'request.json'; request.write_bytes(self.raw)
        dest=Path(self.tmp.name)/'stage'; b.stage(self.root,request,dest)
        target=dest/'files'/c.HEADER; target.write_bytes(b'tampered')
        with self.assertRaises(ValueError): b.apply(self.root,dest)
        self.assertFalse((self.root/c.HEADER).exists())
    def test_stage_apply(self):
        request=Path(self.tmp.name)/'request.json'; request.write_bytes(self.raw)
        dest=Path(self.tmp.name)/'stage'; b.stage(self.root,request,dest); b.apply(self.root,dest)
        self.assertEqual((self.root/c.HEADER).read_bytes(),b.derive(self.root,self.raw)[c.HEADER])
        self.assertEqual(len(c.load(self.root)),6)
        (self.root/c.HEADER).write_bytes(b'corrupt')
        with self.assertRaises(ValueError): c.load(self.root)
if __name__=='__main__': unittest.main()
