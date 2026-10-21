#!/usr/bin/env python3
"""Explicit five-head revision, exact approved normalization and unchanged roles."""
import copy,hashlib,json,struct,subprocess,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
from approved_pulse_art_revision import approval,project_previous_art,IDS
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/hd/artwork/pulse-family-v2-simple'
def sha(b):return hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for v in b:h=((h^v)*1099511628211)&((1<<64)-1)
 return f'{h:016x}'
class PulseArtRevisionTests(unittest.TestCase):
 def setUp(self):
  self.a=approval();self.r=json.loads((ROOT/'assets/hd/global-assets-v1/registry.json').read_text());self.m=json.loads((ART/'candidate-manifest.json').read_text())
 def test_only_five_art_rows_changed(self):
  b=json.loads(subprocess.check_output(['git','show',self.a['baseline_commit']+':assets/hd/global-assets-v1/registry.json'],cwd=ROOT))
  projected=copy.deepcopy(self.r);projected['resources']=project_previous_art(projected['resources']);self.assertEqual(projected,b)
  for change in self.a['revisions']:
   old=change['previous'];p=ROOT/'assets/hd/global-assets-v1'/old['path'];self.assertEqual(sha(p.read_bytes()),old['sha256']);self.assertEqual(sha((ROOT/old['provenance']['source_png']).read_bytes()),old['provenance']['source_png_sha256'])
 def test_exact_approved_whole_image_transforms(self):
  self.assertEqual(tuple(f['identity'] for f in self.m['frames']),IDS)
  for f in self.m['frames']:
   p=ART/f['master'];self.assertEqual(sha(p.read_bytes()),f['master_sha256']);im=Image.open(p).convert('RGBA');self.assertEqual(list(im.size),f['master_size']);crop=im.crop(f['crop']);w,h=f['resize'];self.assertEqual(crop.width,10*w);self.assertEqual(crop.height,10*h)
   out=Image.new('RGBA',(96,112));out.paste(crop.resize((w,h),Image.Resampling.LANCZOS),tuple(f['paste']));saved=Image.open(ART/f['source_png']).convert('RGBA');self.assertEqual(saved.tobytes(),out.tobytes());self.assertEqual(sha((ART/f['source_png']).read_bytes()),f['source_png_sha256'])
   b=(ART/f['hda']).read_bytes();self.assertEqual(len(b),43036);self.assertEqual(b[:4],b'HDR1');self.assertEqual(list(struct.unpack('<6I',b[4:28])),f['header_u32']);self.assertEqual(b[28:],out.tobytes());self.assertEqual(sha(b),f['sha256']);self.assertEqual(fnv(b[28:]),f['payload_fnv64']);self.assertEqual(f['max_outer_alpha'],0)
   row=next(r for r in self.r['resources'] if r['identity']==f['identity']);self.assertEqual(b,(ROOT/'assets/hd/global-assets-v1'/row['path']).read_bytes());self.assertEqual(row['sha256'],f['sha256']);self.assertEqual(row['payload_fnv64'],f['payload_fnv64']);self.assertEqual(row['header_u32'],f['header_u32'])
 def test_exact_new_rows_required_not_blanket_skip(self):
  for identity in IDS:
   for key in ('sha256','payload_fnv64','path','identity','header_u32','provenance'):
    r=copy.deepcopy(self.r['resources']);row=next(x for x in r if x['identity']==identity)
    if key=='identity':row[key]=99999 # remains visible to full baseline comparison
    elif key=='header_u32':row[key][4]=123
    elif key=='provenance':row[key]['source_png']='evil'
    else:row[key]='bad'
    if key=='identity':self.assertNotEqual(project_previous_art(r),project_previous_art(self.r['resources']))
    else:
     with self.assertRaises(ValueError):project_previous_art(r)
 def test_generated_header_exact(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'generated.h';subprocess.run([sys.executable,str(ROOT/'scripts/build_global_registry_header.py'),'--registry',str(ROOT/'assets/hd/global-assets-v1/registry.json'),'--output',str(p)],check=True,capture_output=True);self.assertEqual(p.read_bytes(),(ROOT/'src/global_asset_registry.h').read_bytes())
 def test_historical_receipts_unchanged(self):
  names=['packaging/global-validation.json','packaging/frontend-validation.json','assets/hd/manifest.json','docs/PULSE_UPGRADE_VALIDATION.json','docs/PULSE_UPGRADE_VALIDATION.md','tests/global_talon_validation.json']
  for n in names:self.assertEqual((ROOT/n).read_bytes(),subprocess.check_output(['git','show',self.a['baseline_commit']+':'+n],cwd=ROOT))
if __name__=='__main__':unittest.main()
