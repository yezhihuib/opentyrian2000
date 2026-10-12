#!/usr/bin/env python3
"""Reconstruct the reviewed six overlapping craft sprites from selected V2 art."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,json,struct,io
P=Path(__file__).resolve().parent
PLACEMENTS=[(123,48,24),(81,0,0),(83,24,0),(85,48,0),(119,0,24),(121,24,24)]
def sha(b):return hashlib.sha256(b).hexdigest()
def safe_output(value):
 raw=Path(value).expanduser()
 if not raw.is_absolute():raise ValueError('absolute external output required')
 if any(x.is_symlink()for x in [raw,*raw.parents]):raise ValueError('output symlinks forbidden')
 out=raw.resolve()
 if out.exists():raise ValueError('output must not exist')
 if not out.parent.is_dir():raise ValueError('output parent must exist')
 if out==P or P in out.parents or out in P.parents:raise ValueError('output must be outside source package')
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args();out=safe_output(args.output);stamps=json.loads((P/'expected-hashes.json').read_text())
 for name,expected in stamps['inputs'].items():
  f=P/name
  if f.is_symlink()or any(x.is_symlink()for x in f.parents if x!=P.parent)or sha(f.read_bytes())!=expected:raise ValueError('source identity mismatch: '+name)
 master=Image.open(P/'sources/generated-whole-selected-v2.png').convert('RGBA');assert master.size==(1330,1182)
 art=Image.new('RGBA',(576,416),(12,8,0,255));layer=master.crop((204,259,1034,965)).resize((448,384),Image.Resampling.LANCZOS);art.alpha_composite(layer,(24,16))
 union=Image.new('L',(72,52));rejoin=Image.new('RGBA',art.size);expected={r['base']:r for r in stamps['outputs']};prepared=[];count=0
 for base,x,y in PLACEMENTS:
  logical=Image.open(P/f'masks/alpha-{base}-logical.png').convert('L');assert logical.size==(24,28)and set(logical.tobytes())<={0,255};count+=sum(v!=0 for v in logical.tobytes());union.paste(255,(x,y,x+24,y+28),logical)
  tile=art.crop((x*8,y*8,(x+24)*8,(y+28)*8));mask=logical.resize(tile.size,Image.Resampling.NEAREST);tile.putalpha(mask);b=bytearray(tile.tobytes())
  for i in range(0,len(b),4):
   if b[i+3]==0:b[i:i+4]=b'\0'*4
  tile=Image.frombytes('RGBA',tile.size,bytes(b));rgba=tile.tobytes();hda=b'HDR1'+struct.pack('<6I',1020000+base,8,24,28,6,7)+rgba;e=expected[base];buf=io.BytesIO();tile.save(buf,format='PNG');png=buf.getvalue()
  assert len(hda)==172060 and sha(rgba)==e['rgba_sha256']and sha(hda)==e['hda_sha256']and sha(png)==e['png_sha256'];assert sha(tile.getchannel('A').tobytes())==e['alpha_sha256'];assert tile.getchannel('A').tobytes()==mask.tobytes();prepared.append((e,png,hda));rejoin.alpha_composite(tile,(x*8,y*8))
 assert count==1768 and sum(v!=0 for v in union.tobytes())==1635
 art.putalpha(union.resize(art.size,Image.Resampling.NEAREST));b=bytearray(art.tobytes())
 for i in range(0,len(b),4):
  if b[i+3]==0:b[i:i+4]=b'\0'*4
 assert rejoin.tobytes()==bytes(b)
 out.mkdir()
 for e,png,hda in prepared:(out/e['png']).write_bytes(png);(out/e['hda']).write_bytes(hda)
 receipt={'status':'PASS','outputs':stamps['outputs'],'source_order_rejoin_byte_exact':True,'whole_assembly_rgba_sha256':sha(bytes(b)),'summed_opaque_logical_cells':count,'union_opaque_logical_cells':1635,'overlap_opaque_logical_cells':133,'alpha_exact_source_support':True,'transparent_RGB_zero':True,'source_only_build':True,'runtime_claims':'None. Original avail2 entry motion and exit require separate actual verification; no forced combat state.'}
 (out/'rebuild-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS exact6 RGBA, PNG, HDR1, independent masks, anchors and ordered overlap rejoin')
if __name__=='__main__':main()
