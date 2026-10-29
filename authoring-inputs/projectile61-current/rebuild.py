"""Generated pixels only: deterministic61 registration, no game-data input."""
from pathlib import Path
import hashlib,json
from PIL import Image, __version__

ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def fnv(b):
 v=14695981039346656037
 for c in b:v=((v^c)*1099511628211)&((1<<64)-1)
 return f'{v:016x}'

def main():
 r=json.loads((ROOT/'registration.json').read_text())
 assert __version__==r['pillow_version']
 p=ROOT/r['master'];assert sha(p.read_bytes())==r['master_sha256']
 with Image.open(p) as im:
  assert im.mode=='RGBA' and list(im.size)==r['master_size']
  out=Image.new('RGBA',(96,112))
  for l in r['lobes']:
   tile=im.crop(tuple(l['crop'])).resize(tuple(l['resize']),Image.Resampling.LANCZOS)
   out.paste(tile,tuple(l['paste']))
 raw=bytearray(out.tobytes());mask=r['native_binary_support'];assert len(mask)==168 and mask.count('1')==74
 for y in range(112):
  for x in range(96):
   i=(y*96+x)*4
   if mask[(y//8)*12+x//8]=='0' or not raw[i+3]:raw[i:i+4]=b'\0'*4
 out=Image.frombytes('RGBA',(96,112),bytes(raw));out.save(ROOT/r['output'],format='PNG',compress_level=9)
 empty=[]
 for y in range(14):
  for x in range(12):
   alpha=out.crop((x*8,y*8,x*8+8,y*8+8)).getchannel('A').tobytes()
   if mask[y*12+x]=='1' and not any(alpha):empty.append([x,y])
 assert not empty
 assert not any(out.crop((32,0,64,112)).tobytes())
 a=bytes(raw[3::4]);pins={'status':'AUTHORING_REBUILD_ONLY_NOT_RUNTIME_QUALIFIED','png':r['output'],'png_sha256':sha((ROOT/r['output']).read_bytes()),'rgba_sha256':sha(raw),'rgba_fnv1a64':fnv(raw),'rgba_bytes':len(raw),'canvas':[96,112],'native_occupied_cells':74,'occupied_cells_with_empty_generated_art':empty,'nonzero_alpha_pixels':sum(v>0 for v in a),'opaque_pixels':a.count(255),'soft_pixels':sum(0<v<255 for v in a),'transparent_pixels':a.count(0),'central_32_pixel_channel_RGBA_all_zero':True,'master_sha256':r['master_sha256'],'registration_sha256':sha((ROOT/'registration.json').read_bytes()),'generated_RGB_only':True,'original_game_data_required_for_rebuild':False}
 (ROOT/'payload-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
 print(json.dumps(pins,indent=2))

if __name__=='__main__':main()
