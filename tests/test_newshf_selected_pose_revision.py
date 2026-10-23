"""Reviewed physical-column authority, independent of mutable authoring hashes."""
import copy, hashlib, json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/newshf-fine-v2-corrected-poses'
SOURCE=ROOT/'authoring-inputs/enemies/newshf-phase-a'
PREVIOUS=ROOT/'docs/newshf168-v4-soft-alpha/previous-binary-revision'
SELECTION_SHA='24e7bc7556426a203cb0fb0e29aca01746fb4c550b77c389fc8a4971d1248074'
sha=lambda b:hashlib.sha256(b).hexdigest()
def selection():
 raw=(DOC/'selection.json').read_bytes()
 assert sha(raw)==SELECTION_SHA,'unreviewed selection authority'
 return json.loads(raw)
def verify_assignments(manifest,blobs):
 approved=selection()
 assert manifest['identity']==approved['identity'],'changed immutable identity'
 for row,art in zip(approved['sources'],manifest['art']):
  assert (art['record'],art['base'])==(row['record'],row['physical_base']),'physical base mismatch'
  assert art['file']==row['selected_png'],'editable path mismatch'
  assert art['art_sha256']==sha(blobs[art['file']])==row['selected_sha256'],'unapproved physical-column assignment'
 assert len(manifest['art'])==len(approved['sources'])==9
class PhysicalSelection(unittest.TestCase):
 def inputs(self):
  m=json.loads((PREVIOUS/'manifest.json').read_bytes())
  return m,{a['file']:(PREVIOUS/a['file']).read_bytes() for a in m['art']}
 def test_previous_selection_and_unchanged_current_six(self):
  m,b=self.inputs();verify_assignments(m,b)
  for art in m['art'][:6]:
   self.assertEqual((SOURCE/art['file']).read_bytes(),b[art['file']])
 def test_repinned_swap_is_rejected(self):
  for record in (167,168):
   m,b=self.inputs();rows=[a for a in m['art'] if a['record']==record];x,y=rows[:2]
   b[x['file']],b[y['file']]=b[y['file']],b[x['file']]
   for a in (x,y):a['art_sha256']=sha(b[a['file']])
   with self.assertRaisesRegex(AssertionError,'physical-column assignment'):verify_assignments(m,b)
 def test_column_authority_and_historical_bundle(self):
  a=json.loads((DOC/'physical-column-audit.json').read_bytes())['columns'];s=selection()['sources']
  historical=DOC/'historical-mislabeled-v1';m=json.loads((historical/'manifest.json').read_bytes())
  for row,col in zip(s,a):
   self.assertTrue(col['strip_crop_rgba_equals_individual_reference'])
   self.assertEqual((row['record'],row['physical_base'],row['column_zero_based']),(col['record'],col['physical_base'],col['column_zero_based']))
   self.assertEqual(row['original_reference_rgba_sha256'],col['reference_rgba_sha256'])
   h=next(x for x in m['art'] if x['record']==row['record'] and x['base']==col['old_and_fine_filename_base'])
   self.assertEqual(sha((historical/h['file']).read_bytes()),col['old_sha256'])
   self.assertEqual(row['selected_sha256'],col['old_sha256'] if row['record']==168 else col['fine_sha256'])
 def test_fine_raw_crop_transform_reproduces_all_six_pixels(self):
  from PIL import Image
  provenance=json.loads((SOURCE/'provenance.json').read_bytes())
  def clean(image):
   out=Image.new('RGBA',image.size)
   out.putdata([(r,g,b,255) if a>=128 else (0,0,0,0) for r,g,b,a in image.getdata()])
   return out
  for group in provenance['groups'][:2]:
   raw=next(DOC.glob(f"enemy-{group['record']}-fine-v2-imagegen-*.png"))
   self.assertEqual(sha(raw.read_bytes()),group['ai_raw_sha256'])
   self.assertEqual(sha((DOC/'fine-v2-normalizer.py').read_bytes()),group['normalization_script_sha256'])
   with Image.open(raw) as image:source=clean(image.convert('RGBA'))
   for pose in group['poses']:
    tile=clean(source.crop(pose['source_bbox']).resize(pose['resize'],Image.Resampling.LANCZOS))
    result=Image.new('RGBA',(192,224));result.paste(tile,pose['paste'])
    with Image.open(SOURCE/f"enemy-{group['record']}-v1-bbox-fit-base{pose['base']}.png") as selected:
     self.assertEqual(result.tobytes(),selected.tobytes())
 def test_retained168_pixels_are_only_reassigned(self):
  m,b=self.inputs();old=DOC/'historical-mislabeled-v1'
  for base,mislabel in ((55,17),(17,55),(93,93)):
   self.assertEqual(b[f'enemy-168-v1-bbox-fit-base{base}.png'],(old/f'enemy-168-v1-bbox-fit-base{mislabel}.png').read_bytes())
if __name__=='__main__':unittest.main()
