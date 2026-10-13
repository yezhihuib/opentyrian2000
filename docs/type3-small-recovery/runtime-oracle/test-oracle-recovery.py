"""Synthetic unit tests of regenerated helper; no game invocation or capture claim."""
from pathlib import Path
import sys,re,struct,hashlib,json
import numpy as np
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parent/'type3-small-recovery-20261013'
import text_oracle as oracle
D=oracle.D;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(D/'tyrian.shp')=='80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0'
assert sha(D/'palette.dat')=='f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0'
f=(R/'src/fonthand.c').read_text();fontmap=re.search(r'const int font_ascii\[256\]\s*=\s*\{(.*?)\};',f,re.S).group(1);fontmap=re.sub(r'/\*.*?\*/','',fontmap,flags=re.S);fontmap=re.sub(r'//[^\n]*','',fontmap);fontmap=list(map(int,re.findall(r'-?\d+',fontmap)));assert len(fontmap)==256
for ch in oracle.TEXT.replace(' ',''):assert fontmap[ord(ch)]==ord(ch)-ord('A')
for fragment in ['const int defaultBrightness = -3;','blit_sprite_dark(screen, x + 2, y + 2, font, sprite_id, false);','blit_sprite_hv_unsafe(screen, x, y, font, sprite_id, 0xf, defaultBrightness + bright);']:assert fragment in f
assert 'JE_dString(VGAScreen, 115, 10, miscText[7], SMALL_FONT_SHAPES);'in(R/'src/mainint.c').read_text()
assert '*(510-alpha)+255)/510)'in(R/'src/render_mirror.c').read_text()
# Independent address-stream decoder: emulate original Sprite data advances,
# rather than using the helper's predecoded glyph arrays or numpy masks.
raw=(D/'tyrian.shp').read_bytes();p=struct.unpack_from('<i',raw,6)[0];count=struct.unpack_from('<H',raw,p)[0];p+=2;stream={}
for i in range(count):
 exists=raw[p];p+=1
 if not exists:continue
 w,h,size=struct.unpack_from('<HHH',raw,p);p+=6;stream[i]=(w,h,raw[p:p+size]);p+=size
pal=list((D/'palette.dat').read_bytes()[5*768:6*768]);rgb=[tuple(((v<<2)|(v>>4))for v in pal[i:i+3])for i in range(0,768,3)]
assert np.array_equal(np.array(rgb,np.uint8),oracle.PALETTE)
def reference(a,s,scale):
 pen=115
 for ch in 'INSERT COIN':
  if ch==' ':pen+=6;continue
  w,h,code=stream[fontmap[ord(ch)]]
  for shadow in [True,False]:
   off=2 if shadow else 0;addr=(10+off)*320+pen+off;col=0;k=0
   while k<len(code):
    op=code[k];k+=1
    if op==255:n=code[k];k+=1;addr+=n;col+=n
    elif op==254:addr+=w-col;col=w
    elif op==253:addr+=1;col+=1
    else:
     gy,gx=divmod(addr,320)
     if 24<=gx<288 and 0<=gy<184:
      for sy in range(scale):
       for sx in range(scale):
        y=gy*scale+sy;x=(gx-24)*scale+sx
        if s[y,x]:
         if shadow:
          for c in range(3):a[y,x,c]=(int(a[y,x,c])+1)//2
         else:a[y,x,:3]=rgb[(240|((op&15)-3))&255]
     addr+=1;col+=1
    if col>=w:addr+=320-col;col=0
  pen+=w+1
rng=np.random.default_rng(155);checks=[]
for scale in [2,4]:
 shape=(200*scale,320*scale)
 for kind in ['all','none','random']:
  a=rng.integers(0,256,(*shape,4),dtype=np.uint8);a[:,:,3]=255;b=a.copy();s=np.ones(shape,bool)if kind=='all'else np.zeros(shape,bool)if kind=='none'else rng.integers(0,2,shape,dtype=np.uint8).astype(bool)
  oracle.apply_insert_coin(a,s,scale);reference(b,s,scale);assert np.array_equal(a,b);checks.append({'scale':scale,'support':kind,'pixels_compared':shape[0]*shape[1],'mismatches':0})
report={'status':'PASS synthetic independent oracle tests; no game/capture verification','helper_origin':'Regenerated from fully retained late-spike text_oracle.py text. Exact historical entry-craft helper byte identity is unproven.','changes_from_retained_text':'Only original-data directory path changed to recovered source-identical data.','retained_text_sha256':sha(O/'text_oracle-retained.py'),'adapted_helper_sha256':sha(O/'text_oracle.py'),'api':['apply_insert_coin','PALETTE','glyphs','TEXT','XY'],'data_pins':{n:sha(D/n)for n in ['tyrian.shp','palette.dat']},'production_source_pins':{n:sha(R/'src'/n)for n in ['fonthand.c','sprite.c','mainint.c','render_mirror.c']},'independent_reference':'Original sprite byte-command stream interpreted with linear320-wide framebuffer address increments and scalar per-subpixel writes; no use of helper glyph arrays/masks.','synthetic_checks':checks,'test_script_sha256':sha(O/'test-oracle-recovery.py'),'fresh_captures_checked':0}
(O/'oracle-recovery-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
