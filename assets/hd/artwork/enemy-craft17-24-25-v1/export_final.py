from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
import json,hashlib
import numpy as np
P=Path(__file__).resolve().parent;a=Image.open(P/'generated-atlas.png').convert('RGBA');F=P/'frames8x';F.mkdir(exist_ok=True)
records=[]
for j,n in enumerate([267,269,271]):
 if n==271:im=ImageOps.mirror(Image.open(F/'newsh2-base-269-192x224.png'))
 else:
  box=(119,213,479,633) if n==267 else (726,213,1116,633)
  im=a.crop(box).resize((192,224),Image.Resampling.LANCZOS)
 f=F/f'newsh2-base-{n}-192x224.png';im.save(f);ar=np.array(im)[:,:,3]
 records.append({'id':n,'file':str(f.relative_to(P)),'logical_size':[24,28],'anchor':[6,7],'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bbox_alpha16':list(Image.fromarray((ar>16).astype('uint8')*255).getbbox()),'edge_alpha_max':int(max(ar[0].max(),ar[-1].max(),ar[:,0].max(),ar[:,-1].max()))})
assert ImageOps.mirror(Image.open(F/'newsh2-base-269-192x224.png')).tobytes()==Image.open(F/'newsh2-base-271-192x224.png').tobytes()
manifest={'identity':'enemy17-24-25-newsh2-hd-v1','namespace':'newsh2.shp','static_designs':True,'animation_frames_per_enemy':1,'records':records,'transform':{'source_windows':{'267':[119,213,479,633],'269':[726,213,1116,633]},'export':[192,224],'resampling':'LANCZOS','271':'exact horizontal flip of exported269, matching byte-exact original relation'},'classification':'Physical silver/gray hull, restrained ochre support arms, orange-red center. Defined metal edges.','limits':['Original source identity trace is private survival plus weapon71 injection; not ordinary gameplay proof.','Actual runtime hit filter/placement review pending.']}
(P/'candidate-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(records,indent=2))
if not (P/'original-267.png').exists(): raise SystemExit(0)
board=Image.new('RGB',(760,390),(30,30,30));d=ImageDraw.Draw(board)
for j,n in enumerate([267,269,271]):
 o=Image.open(P/f'original-{n}.png').convert('RGBA');im=Image.open(F/f'newsh2-base-{n}-192x224.png');x=j*250+5;d.text((x,5),str(n)+' original / HD',fill='white')
 for y,s in [(25,4),(150,2)]:
  for k,z in enumerate([o,im]):
   u=z.resize((24*s,28*s),Image.Resampling.NEAREST);board.paste(u,(x+110*k,y),u)
 earth=Image.open(P.parent/'installation125-128-v1/accepted-ground-style.png').convert('RGBA').resize((192,224));earth.alpha_composite(im)
 for k,s in enumerate([4,2]):board.paste(earth.resize((24*s,28*s),Image.Resampling.NEAREST),(x+110*k,230))
board.save(P/'review-final-native4x2x.png')
