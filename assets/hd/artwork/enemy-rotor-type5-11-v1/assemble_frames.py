from PIL import Image
from pathlib import Path
import json,hashlib
P=Path(__file__).parent;core=Image.open(P/'generated-fixed-core.png').resize((72,72),Image.Resampling.LANCZOS);centers=[(12.5,12.5),(11.5,13.5),(11.5,13.5),(12.5,12.5),(12.5,13.5),(12.5,13.5),(12.5,13.5),(11.5,13.5)];m=[]
for b,c in zip(range(229,244,2),centers):
 im=Image.open(P/f'arc-renders8x/newsh2-base-{b}-192x224.png');im.alpha_composite(core,(round((c[0]-4.5)*8),round((c[1]-4.5)*8)));f=P/f'frames8x/newsh2-base-{b}-192x224.png';im.save(f);m.append({'base':b,'center':c,'core_box':[round((c[0]-4.5)*8),round((c[1]-4.5)*8),72,72],'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'assembly.json').write_text(json.dumps(m,indent=2))
