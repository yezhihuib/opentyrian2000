"""Reproduce four authored sprites. No original game data required."""
from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent
RECTS={49:(140.83333333333334,105.12616822429906,492.83333333333337,524.8644859813083),51:(762.1666666666666,105.12616822429906,1114.1666666666665,524.8644859813083),89:(128.84065934065933,721.0631067961165,494.9065934065934,1154.9271844660193),127:(752.7912087912088,721.0765765765766,1119.9120879120878,1151.9234234234234)}
def export(out):
 out.mkdir(parents=True,exist_ok=True);im=Image.open(P/'generated-atlas.png');result={}
 for k,r in RECTS.items():
  p=out/f'newsh2-base{k}-8.png';im.transform((192,224),Image.Transform.EXTENT,r,Image.Resampling.BICUBIC).save(p);result[k]=hashlib.sha256(p.read_bytes()).hexdigest()
 return result
if __name__=='__main__':print(json.dumps(export(P/'frames8x'),indent=2))
