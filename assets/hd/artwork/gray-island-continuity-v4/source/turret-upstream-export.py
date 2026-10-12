"""Source-preserving extraction and assembly of one authored turret and three cores."""
from pathlib import Path
from PIL import Image
import hashlib,json
P=Path(__file__).resolve().parent
CORE=(72,96,120,144)
def export(out):
 out.mkdir(parents=True,exist_ok=True);master=Image.open(P/'generated-turret-atlas.png');back=Image.open(P/'frozen144-8.png').convert('RGBA');layers=[];result={}
 for j in range(3):
  x=j*master.width/3;layers.append(master.transform((192,224),Image.Transform.EXTENT,(x+40,32,x+630,720),Image.Resampling.BICUBIC))
 for j,k in enumerate([153,155,157]):
  body=layers[0].copy()
  if j:body.paste(layers[j].crop(CORE),CORE[:2])
  final=Image.alpha_composite(back,body);p=out/f'newsh2-base{k}-8.png';final.save(p);result[k]=hashlib.sha256(p.read_bytes()).hexdigest()
 return result
if __name__=='__main__':print(json.dumps(export(P/'frames8x'),indent=2))
