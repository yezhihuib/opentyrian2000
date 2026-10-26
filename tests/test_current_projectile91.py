"""Fixed registration/finite single-master tests, not in-game evidence."""
import copy, io, json, struct, sys, tempfile, unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_projectile91_compatibility as c
from build_current_art import encoded
class Projectile91ArtTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.selected=json.loads((ROOT/c.SELECTION).read_bytes())
        for n in c.input_paths(ROOT):
            p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/n).read_bytes())
    def generate(self,j=None):return c.generate(self.root,encoded(j or self.selected))
    def test_exact_deterministic_registration(self):
        a=self.generate();b=self.generate();self.assertEqual(a,b);self.assertEqual(c.load(self.root),c.load(ROOT))
        payload=a[2][c.PAIRS[0]][28:];self.assertEqual(len(payload),96*112*4)
        self.assertEqual(a[2][c.PAIRS[0]][:28],struct.pack('<4s6I',b'HDR1',1490091,8,12,14,0,0))
        self.assertTrue(any(0<x<255 for x in payload[3::4]))
        for y in range(112):
            for x in range(96):
                if c.MASK[y//8*12+x//8]=='0':self.assertEqual(payload[(y*96+x)*4:(y*96+x)*4+4],b'\0'*4)
    def test_finite_identity(self):
        for key,value in [('selector',92),('selector',True),('source_png','../foreign.png'),('source_sha256','0'*64)]:
            j=copy.deepcopy(self.selected);j['masters'][0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.generate(j)
        for i,d in [(80091,8),(1490091,4),(True,8),(1490092,8)]:
            with self.assertRaises(ValueError):c.name(i,d)
    def test_duplicate_or_foreign_master_rejected(self):
        for edit in ('extra','duplicate','schema'):
            j=copy.deepcopy(self.selected)
            if edit=='extra':j['extra']=0
            elif edit=='duplicate':j['masters']*=2
            else:j['schema']='foreign'
            with self.assertRaises(ValueError):self.generate(j)
    def test_tampered_outputs_rejected(self):
        for n in [c.HEADER,c.MAPPING,c.PREVIEW,c.ROOT+'/'+c.name(c.IDS[0])]:
            p=self.root/n;old=p.read_bytes();p.write_bytes(old+b'\0')
            with self.subTest(path=n),self.assertRaises((ValueError,json.JSONDecodeError)):c.load(self.root)
            p.write_bytes(old)
    def test_master_changed_or_wrong_dimensions_rejected(self):
        p=self.root/self.selected['masters'][0]['source_png'];p.write_bytes(p.read_bytes()+b'bad')
        with self.assertRaises(ValueError):self.generate()
        im=Image.new('RGBA',(96,112));b=io.BytesIO();im.save(b,format='PNG');p.write_bytes(b.getvalue())
        j=copy.deepcopy(self.selected);j['masters'][0]['source_sha256']=c.sha(b.getvalue())
        with self.assertRaises(ValueError):self.generate(j)
if __name__=='__main__':unittest.main()
