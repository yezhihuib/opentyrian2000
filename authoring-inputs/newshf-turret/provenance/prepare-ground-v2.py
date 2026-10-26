from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image,ImageDraw,ImageFilter
b=Path('/workspace/scratch/f67dd347fa0a/opentyrian-recovery-20261026');d=b/'turret39-art-v2';d.mkdir(exist_ok=True)
old=Image.open(b/'next-art-audit-turret39/original-newshf-base39-native.png').convert('RGBA');gen=Image.open(b/'turret39-art-draft/turret-cold-registered-v1.png').convert('RGBA');hot=Image.open(b/'turret39-art-draft/turret-aperture-overlay-v1.png').convert('RGBA')
# Geometric silhouette registered to generated pod, not rectangular image feather.
S=4;m=Image.new('L',(192*S,224*S));p=ImageDraw.Draw(m)
def box(v):return tuple(round(x*S) for x in v)
p.ellipse(box((13,28,163,176)),fill=255)
p.ellipse(box((123,20,157,66)),fill=255)
p.polygon([(round(x*S),round(y*S)) for x,y in [(76,149),(105,149),(105,188),(92,198),(79,191)]],fill=255)
# Blend outward without changing fully opaque body interior.
m=m.filter(ImageFilter.MaxFilter(33)).filter(ImageFilter.GaussianBlur(2*S)).resize((192,224),Image.Resampling.LANCZOS)
a=np.asarray(m).copy();a[a<3]=0;a[a>252]=255
# Two native cells at each outside boundary are exact original peripheral ground.
a[:16,:]=0;a[-16:,:]=0;a[:,:8]=0;a[:,-16:]=0
m=Image.fromarray(a);m.save(d/'pod-composition-mask8x.png')
orig=np.asarray(old);support=(a.reshape(28,8,24,8).min(axis=(1,3))<255)
periph=orig.copy();periph[~support]=0;Image.fromarray(periph).save(d/'native-peripheral-source.png')
expanded=np.repeat(np.repeat(orig,8,0),8,1).astype(np.uint32);g=np.asarray(gen).astype(np.uint32);w=a.astype(np.uint32)[:,:,None]
result=((g*w+expanded*(255-w)+127)//255).astype(np.uint8);result[:,:,3]=255
cold=Image.fromarray(result);fired=Image.alpha_composite(cold,hot)
cold.save(d/'turret-cold-v2.png');fired.save(d/'turret-hot-v2.png');preview=Image.new('RGBA',(384,224));preview.paste(cold);preview.paste(fired,(192,0));preview.save(d/'turret-cold-hot-v2.png')
print('original peripheral nativecells',int(support.sum()),'zero matte pixels',int((a==0).sum()),'mixed',int(((a>0)&(a<255)).sum()))
