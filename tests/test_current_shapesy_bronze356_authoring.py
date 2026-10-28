"""Finite opaque356 authoring tests; synthetic edits are never production art."""
import json,shutil,struct,tempfile,sys,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_shapesy_bronze356_compatibility as c
import build_current_shapesy_bronze356 as b
class Bronze356Authoring(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'root';self.root.mkdir()
        for n in c.INPUTS:
            p=self.root/c.INPUT_ROOT/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/c.INPUT_ROOT/n,p)
        self.refresh()
    def refresh(self):
        self.raw=json.dumps(dict(schema=c.SCHEMA,version='synthetic-test-only',inputs={c.INPUT_ROOT+'/'+n:c.sha((self.root/c.INPUT_ROOT/n).read_bytes()) for n in c.INPUTS})).encode()
    def master(self):return self.root/c.INPUT_ROOT/'raw/generated-master-03.png'
    def stage(self):
        request=Path(self.tmp.name)/'request.json';request.write_bytes(self.raw)
        dest=Path(self.tmp.name)/'stage';b.stage(self.root,request,dest);return dest
    def test_exact_whole_opaque_resource(self):
        _,pngs,blobs,rows=c.generate(self.root,self.raw);self.assertEqual(tuple(blobs),(356,))
        self.assertEqual(struct.unpack('<4s6I',blobs[356][:28]),(b'HDR1',2020356,8,24,28,0,0))
        expected=Image.open(self.master()).convert('RGBA').resize((192,224),Image.Resampling.LANCZOS).tobytes()
        self.assertEqual(blobs[356][28:],expected);self.assertEqual(set(expected[3::4]),{255})
        self.assertEqual(rows[0]['source_layer'],1);self.assertEqual(rows[0]['source_bank'],'shapesy.dat')
        self.assertEqual(rows[0]['source_png_sha256'],c.sha(pngs[c.png(356)]))
    def test_generated_master_is_only_pixel_source(self):
        before=c.generate(self.root,self.raw)[2][356]
        im=Image.open(self.master()).convert('RGB');im.paste((91,80,43),(0,0,64,64));im.save(self.master());self.refresh()
        after=c.generate(self.root,self.raw)[2][356];self.assertNotEqual(before,after)
        self.assertEqual(set(after[31::4]),{255})
    def test_unselected_master_edit_rejected(self):
        self.master().write_bytes(b'bad')
        with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_fixed_recipe_changes_rejected(self):
        path=self.root/c.INPUT_ROOT/'registration-runtime.json'
        for key,value in [('role',203),('identity',2020357),('density',4),('anchor',[1,0]),('crop',[1,0,1161,1354]),('native_data_needed',True),('alpha','object-only')]:
            recipe=dict(c.RECIPE);recipe[key]=value;path.write_text(json.dumps(recipe));self.refresh()
            with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_extra_input_duplicate_json_and_unknown_id_rejected(self):
        selected=json.loads(self.raw);selected['inputs']['native-rgb.png']='0'*64
        with self.assertRaises(ValueError):c.generate(self.root,json.dumps(selected).encode())
        with self.assertRaises(ValueError):c.generate(self.root,b'{"schema":1,"schema":2}')
        for i in (True,355,357,'356'):
            with self.assertRaises(ValueError):c.name(i)
    def test_alpha_and_wrong_canvas_rejected(self):
        for mode,size in [('RGBA',(1161,1354)),('RGB',(1160,1354)),('L',(1161,1354))]:
            Image.new(mode,size).save(self.master());self.refresh()
            with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_trailing_crc_and_truncated_png_rejected(self):
        raw=self.master().read_bytes()
        for malformed in (raw+b'x',raw[:33]+bytes([raw[33]^1])+raw[34:],raw[:-12]):
            self.master().write_bytes(malformed);self.refresh()
            with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_symlink_master_rejected(self):
        saved=Path(self.tmp.name)/'saved.png';shutil.copyfile(self.master(),saved);self.master().unlink();self.master().symlink_to(saved)
        with self.assertRaises(ValueError):c.generate(self.root,self.raw)
    def test_stage_apply_and_load(self):
        dest=self.stage();b.apply(self.root,dest);self.assertEqual(len(c.load(self.root)),1)
        (self.root/c.HEADER).write_bytes(b'bad')
        with self.assertRaises(ValueError):c.load(self.root)
    def test_tampered_stage_has_no_writes(self):
        dest=self.stage();(dest/'files'/c.HEADER).write_bytes(b'bad')
        with self.assertRaises(ValueError):b.apply(self.root,dest)
        self.assertFalse((self.root/c.HEADER).exists())
    def test_stale_input_has_no_writes(self):
        dest=self.stage();self.master().write_bytes(b'bad')
        with self.assertRaises(ValueError):b.apply(self.root,dest)
        self.assertFalse((self.root/c.HEADER).exists())
    def test_changed_transport_and_mapping_rejected(self):
        dest=self.stage();b.apply(self.root,dest);p=self.root/c.ROOT/c.name(356);raw=p.read_bytes();p.write_bytes(raw+b'x')
        with self.assertRaises(ValueError):c.load(self.root)
        p.write_bytes(raw);p=self.root/c.MAPPING;spec=json.loads(p.read_bytes());spec['files'][0]['base']=355;p.write_text(json.dumps(spec))
        with self.assertRaises(ValueError):c.load(self.root)
if __name__=='__main__':unittest.main()
