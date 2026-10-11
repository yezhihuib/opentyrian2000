from PIL import Image
from pathlib import Path
P=Path(__file__).parent;im=Image.open(P/'earth-corrected-assembly.png').convert('RGBA').resize((384,448),Image.Resampling.LANCZOS);im.save(P/'assembly8x.png');(P/'components8x').mkdir(exist_ok=True);(P/'tiles8x').mkdir(exist_ok=True)
for b,(x,y) in zip([81,83,119,121],[(0,0),(192,0),(0,224),(192,224)]):
 c=im.crop((x,y,x+192,y+224));c.save(P/f'components8x/newsh2-base-{b}-192x224.png')
 for sid,(tx,ty) in zip([b,b+1,b+19,b+20],[(0,0),(96,0),(0,112),(96,112)]):c.crop((tx,ty,tx+96,ty+112)).save(P/f'tiles8x/newsh2-id{sid}-96x112.png')
