"""Finite approved168 soft-alpha revision; native source identity stays frozen."""
import copy,hashlib,importlib.util,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / 'scripts'))
import portable_history_baselines as history
SOURCE=ROOT/'authoring-inputs/enemies/newshf-phase-a'
DOC=ROOT/'docs/newshf168-v4-soft-alpha'
SELECTION_SHA='343c5ba7875a2b729f018be02cb626afbcf995fa106bb7d670849bca94df75ec'
BASE='0112ec8d3c3fd0b6145463b85a713a79ccd01ac5'
sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('newshf_v4_check',ROOT/'scripts/check_newshf_phase_a.py')
check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
def selection():
 raw=(DOC/'selection.json').read_bytes();assert sha(raw)==SELECTION_SHA,'unreviewed168 selection authority'
 return json.loads(raw)
def verify_assignments(manifest,blobs):
 selected=selection()
 assert manifest['schema']==2 and manifest['art_policy']==selected['art_policy'],'unapproved soft-alpha policy'
 assert manifest['identity']==selected['identity'],'changed immutable identity'
 assert len(manifest['art'])==len(selected['sources'])==9
 for a,s in zip(manifest['art'],selected['sources']):
  assert a==s and sha(blobs[a['file']])==s['art_sha256'],'unapproved physical-column assignment'
class Selected168V4(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.source=Path(self.tmp.name)/'source';shutil.copytree(SOURCE,self.source)
  self.manifest=json.loads((self.source/'manifest.json').read_bytes())
 def write(self):
  (self.source/'manifest.json').write_text(json.dumps(self.manifest))
 def repin(self,index):
  a=self.manifest['art'][index];a['art_sha256']=sha((self.source/a['file']).read_bytes());self.write()
  p=json.loads((self.source/'provenance.json').read_bytes())
  next(pose for g in p['groups'] for pose in g['poses'] if pose['base']==a['base'])['selected_png_sha256']=a['art_sha256']
  (self.source/'provenance.json').write_text(json.dumps(p))
 def reject(self):
  with self.assertRaises((ValueError,OSError,TypeError,KeyError)):check.check(self.source)
 def test_exact_selection_and_soft_counts(self):
  verify_assignments(self.manifest,{a['file']:(self.source/a['file']).read_bytes() for a in self.manifest['art']})
  self.assertEqual(check.check(self.source),json.loads((self.source/'report.json').read_bytes()))
  for a,count,soft in zip(self.manifest['art'][6:],(242,244,243),(2951,3458,3648)):
   with Image.open(self.source/a['file']) as im:
    values=list(im.getchannel('A').getdata());self.assertEqual(len(set(values)),count);self.assertEqual(sum(0<v<255 for v in values),soft)
 def test_soft_alpha_not_permitted_for163_or167(self):
  for index in (0,3):
   a=self.manifest['art'][index];p=self.source/a['file'];original=p.read_bytes()
   with Image.open(p) as im:im.putpixel((30,30),(10,20,30,2));im.save(p)
   self.repin(index);self.reject();p.write_bytes(original);self.repin(index)
 def test_unknown_revision_record_base_policy_and_schema_rejected(self):
  original=copy.deepcopy(self.manifest)
  for key,value in [('revision','unselected'),('record',167),('bases',[17,55,93]),('alpha','any-alpha'),('selected_png_sha256',{})]:
   self.manifest=copy.deepcopy(original);self.manifest['art_policy'][key]=value;self.write();self.reject()
  self.manifest=copy.deepcopy(original);self.manifest['schema']=1;del self.manifest['art_policy'];self.write();self.reject()
 def test_repin_soft_payload_or_swap_cannot_redefine_selected_revision(self):
  a=self.manifest['art'][6];p=self.source/a['file']
  with Image.open(p) as im:im.putpixel((30,30),(10,20,30,127));im.save(p)
  self.repin(6);self.reject()
  m=json.loads((SOURCE/'manifest.json').read_bytes());b={a['file']:(SOURCE/a['file']).read_bytes() for a in m['art']};x,y=m['art'][7:9];b[x['file']],b[y['file']]=b[y['file']],b[x['file']]
  for a in (x,y):a['art_sha256']=sha(b[a['file']])
  with self.assertRaisesRegex(AssertionError,'physical-column assignment'):verify_assignments(m,b)
 def test_prior_binary_bundle_exact_and_still_valid(self):
  previous=DOC/'previous-binary-revision'
  for p in previous.iterdir():
   self.assertEqual(p.read_bytes(),history.preimage(BASE, 'authoring-inputs/enemies/newshf-phase-a/'+p.name, ROOT))
  old=check.check(previous)
  self.assertEqual(old,json.loads((previous/'report.json').read_bytes()))
  self.assertEqual(old['source_identity_sha256'],check.check(self.source)['source_identity_sha256'])
 def test_raw_and_quantized_transforms_reproduce_selected_rgba(self):
  # Python round uses ties-to-even, as numpy.rint in the archived normalizer.
  s=selection();raw=next(DOC.glob('enemy-168-v4-three-poses-imagegen-*.png'))
  self.assertEqual(sha(raw.read_bytes()),s['raw_sha256'])
  self.assertEqual(sha((DOC/'normalize-max-canvas.py').read_bytes()),s['normalizer_sha256'])
  with Image.open(raw) as im:
   clean=im.convert('RGBA');pixels=[]
   for r,g,b,a in clean.getdata():
    alpha=min(255,round(a*255/253));pixels.append((r,g,b,alpha) if alpha>=2 else (0,0,0,0))
   clean.putdata(pixels)
  p=json.loads((SOURCE/'provenance.json').read_bytes())['groups'][2]
  for pose in p['poses']:
   self.assertEqual(pose['source_bbox'][1::2],[0,783])
   tile=clean.crop(pose['source_bbox']).resize(pose['resize'],Image.Resampling.LANCZOS)
   out=Image.new('RGBA',(192,224));out.paste(tile,pose['paste']);out.putdata([(r,g,b,a) if a else (0,0,0,0) for r,g,b,a in out.getdata()])
   with Image.open(SOURCE/f"enemy-168-v1-bbox-fit-base{pose['base']}.png") as selected:self.assertEqual(out.tobytes(),selected.tobytes())
if __name__=='__main__':unittest.main()
