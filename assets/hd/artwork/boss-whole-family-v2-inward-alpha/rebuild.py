from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,gaussian_filter
import numpy as np,json,hashlib,struct
import sys,subprocess,tempfile
SOURCE=Path(__file__).resolve().parent
P=Path(sys.argv[1]).absolute()
if P.exists():raise SystemExit('Output must not exist')
P.mkdir(parents=True)
V=SOURCE/'base-v1'
I=json.load(open(SOURCE/'inventory.json'))
for rel,h in I['inputs'].items():assert hashlib.sha256((SOURCE/rel).read_bytes()).hexdigest()==h,rel
scratch=tempfile.TemporaryDirectory(prefix='boss-v2-rebuild-')
B=Path(scratch.name)/'v1-output'
subprocess.run([sys.executable,str(V/'rebuild.py'),str(B)],check=True)
C=json.load(open(V/'proof/source-contract.json'))
R=json.load(open(V/'proof/intact-registration.json'))
O=P/'output'; O.mkdir(exist_ok=True)
M=P/'coverage'; M.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def registered(name):
 im=Image.open(V/'sources'/name).convert('RGBA');s=R['source_bbox'];g=R['generated_bbox']
 a=Image.new('RGBA',(960,896));a.alpha_composite(im.crop(g).resize(((s[2]-s[0])*8,(s[3]-s[1])*8),Image.Resampling.LANCZOS),(s[0]*8,s[1]*8));return a
gi=registered('generated-intact-v2.png')
gd=Image.composite(registered('generated-damage.png'),gi,Image.open(V/'masks/damage-change-mask8x.png').convert('L'))
fields={}
for name,generated in [('intact',gi),('damage',gd)]:
 s=np.asarray(Image.open(V/f'masks/{name}-alpha.png').resize((960,896),Image.Resampling.NEAREST))>0
 g=np.asarray(generated.getchannel('A'),dtype=float)/255
 distance=distance_transform_edt(s)
 curve=np.clip((gaussian_filter(s.astype(float),4)-.60)/.15,0,1)
 blend=np.clip((distance-12)/4,0,1)
 a=np.where(s,np.round(255*(np.minimum(g,curve)*(1-blend)+blend)),0).astype('uint8');a[distance>16]=255
 fields[name]=(a,s&(distance<=16),s&(distance>16))
 Image.fromarray(a).save(M/f'{name}-whole-alpha.png')
alphas={};bands={};locks={}
for co in C['components']:
 x,y=co['assembly_origin'];box=np.s_[y*8:(y+28)*8,x*8:(x+24)*8]
 for name,b in [('intact',co['intact_base']),('damage',co.get('damage_base'))]:
  if b is None or (name=='damage' and b==co['intact_base']):continue
  alphas[b],bands[b],locks[b]=[z[box].copy() for z in fields[name]]
for b in [3,5,7,39,41,43,45]:
 alphas[b]=alphas[1].copy();bands[b]=bands[1].copy();locks[b]=locks[1].copy()
alphas[280]=alphas[128].copy();bands[280]=bands[128].copy();locks[280]=locks[128].copy()
for b in [238,278,282]:
 alphas[b]=np.zeros((224,192),dtype='uint8');bands[b]=locks[b]=np.zeros((224,192),bool)
rows=[]
for b in sorted(alphas):
 old=np.array(Image.open(B/f'enemy-newsh4-{b}-8.png').convert('RGBA'));a=alphas[b];new=old.copy();new[:,:,3]=a
 assert not np.any((a>0)&(old[:,:,3]==0)),b
 assert np.all(a[locks[b]]==old[:,:,3][locks[b]]),b
 assert np.all((a==old[:,:,3])|bands[b]),b
 Image.fromarray(bands[b].astype('uint8')*255).save(M/f'editable-{b}.png')
 Image.fromarray(locks[b].astype('uint8')*255).save(M/f'locked-{b}.png')
 im=Image.fromarray(new);path=O/f'enemy-newsh4-{b}-8.png';im.save(path)
 hda=b'HDR1'+struct.pack('<6I',1020000+b,8,24,28,6,7)+im.tobytes();(O/f'enemy-newsh4-{b}-8.hda').write_bytes(hda)
 rows.append({'base':b,'RGB_identical':True,'outside_support':0,'protected_interior_exact':True,'changed_alpha':int((a!=old[:,:,3]).sum()),'fractional':int(((a>0)&(a<255)).sum()),'old_mass':int(old[:,:,3].sum()),'new_mass':int(a.sum()),'RGBA_SHA256':sha(im.tobytes()),'PNG_SHA256':sha(path.read_bytes()),'HDA_SHA256':sha(hda)})
assert len(rows)==43
assert (O/'enemy-newsh4-128-8.png').read_bytes()==(O/'enemy-newsh4-280-8.png').read_bytes()
for z in [2,4]:
 cw=120*z+16;ch=112*z+28;sheet=Image.new('RGB',(cw*3,ch*7),(37,48,40));d=ImageDraw.Draw(sheet)
 for k,state in enumerate(C['states']):
  a=Image.new('RGBA',(960,896),(37,48,40,255))
  for rec in C['draw_order_if_all_allocations_succeed']:
   b=state['record_to_base'].get(str(rec));co=next(c for c in C['components']if c['record']==rec)
   if b is not None:a.alpha_composite(Image.open(O/f'enemy-newsh4-{b}-8.png'),tuple(v*8 for v in co['assembly_origin']))
  x=k%3*cw+8;y=k//3*ch;sheet.paste(a.resize((120*z,112*z),Image.Resampling.NEAREST),(x,y+24));d.text((x,y+3),state['name'],fill='white')
 sheet.save(P/f'all21-inward-alpha-native{z}x.png')
(P/'alpha-proof.json').write_text(json.dumps({'status':'OFFLINE_CANDIDATE_REQUIRES_FRESH_RUNTIME','RGB_byte_identical_to_V1':True,'outside_original_support':0,'band_density8':16,'protected_distance_gt':16,'empty':[238,278,282],'identical_alias':[128,280],'center_eight_alpha_identical':True,'whole_field_before_partition':True,'outputs':rows},indent=2)+'\n')
print('PASS 43 outputs, RGB unchanged, all edits inside edge bands')

for r in rows:
 e=next(x for x in I["outputs"] if x["base"]==r["base"])
 for key in ["PNG_SHA256","RGBA_SHA256","HDA_SHA256"]:assert r[key]==e[key],(r["base"],key)
print("PASS exact43 revised PNG/RGBA/HDA reproducibility")
