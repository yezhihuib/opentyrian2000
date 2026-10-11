"""Reproduce authored modular components; original alpha exceptions are mapping data."""
from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent
IDS=[279,281,283,245,169,207,273,275,277]
def export(out):
 out.mkdir(parents=True,exist_ok=True);master=Image.open(P/'generated-intact-master.png').convert('RGBA').resize((576,672),Image.Resampling.LANCZOS);holes=json.loads((P/'original-alpha-contract.json').read_text());result={}
 for j,k in enumerate(IDS):
  im=master.crop((j%3*192,j//3*224,j%3*192+192,j//3*224+224));mask=Image.new('L',(24,28),255)
  for xy in holes[str(k)]:mask.putpixel(tuple(xy),0)
  im.putalpha(mask.resize((192,224),Image.Resampling.NEAREST));p=out/f'newsh2-base{k}-8.png';im.save(p);result[k]=hashlib.sha256(p.read_bytes()).hexdigest()
 return result
if __name__=='__main__':print(json.dumps(export(P/'frames8x'),indent=2))
