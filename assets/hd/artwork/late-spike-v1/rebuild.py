#!/usr/bin/env python3
"""Reconstruct six reviewed sprites from two continuous generated triplets."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,json,struct,io
P=Path(__file__).resolve().parent
REGISTRATIONS=[('a',[1,3,5],(124,116,1412,348),(0,40,552,168)),('b',[7,9,11],(110,644,1436,861),(16,40,576,168))]
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
 master=Image.open(P/'sources/generated-two-triplets.png').convert('RGBA');assert master.size==(1536,1024);expected={r['base']:r for r in stamps['outputs']};prepared=[];assemblies=[];count=0
 for name,bases,crop,dest in REGISTRATIONS:
  art=Image.new('RGBA',(576,224),(8,8,8,255));layer=master.crop(crop).resize((dest[2]-dest[0],dest[3]-dest[1]),Image.Resampling.LANCZOS);art.alpha_composite(layer,(dest[0],dest[1]))
  logical=Image.open(P/f'masks/alpha-triplet-{name}-logical.png').convert('L');assert logical.size==(72,28)and set(logical.tobytes())<={0,255};count+=sum(v!=0 for v in logical.tobytes());mask=logical.resize(art.size,Image.Resampling.NEAREST);art.putalpha(mask);b=bytearray(art.tobytes())
  for i in range(0,len(b),4):
   if b[i+3]==0:b[i:i+4]=b'\0'*4
  art=Image.frombytes('RGBA',art.size,bytes(b));rejoin=Image.new('RGBA',art.size)
  for k,base in enumerate(bases):
   tile=art.crop((k*192,0,(k+1)*192,224));rgba=tile.tobytes();hda=b'HDR1'+struct.pack('<6I',1010000+base,8,24,28,6,7)+rgba;e=expected[base];buf=io.BytesIO();tile.save(buf,format='PNG');png=buf.getvalue()
   assert len(hda)==172060 and sha(rgba)==e['rgba_sha256']and sha(hda)==e['hda_sha256']and sha(png)==e['png_sha256']
   assert sha(tile.getchannel('A').tobytes())==e['alpha_sha256'];assert tile.getchannel('A').tobytes()==mask.crop((k*192,0,(k+1)*192,224)).tobytes();prepared.append((e,png,hda));rejoin.paste(tile,(k*192,0))
  assert rejoin.tobytes()==art.tobytes();assemblies.append({'triplet':name,'rgba_sha256':sha(art.tobytes()),'partition_rejoin_exact':True})
 assert count==1482
 out.mkdir()
 for e,png,hda in prepared:(out/e['png']).write_bytes(png);(out/e['hda']).write_bytes(hda)
 receipt={'status':'PASS','outputs':stamps['outputs'],'assemblies':assemblies,'opaque_logical_cells':count,'alpha_exact_source_support':True,'transparent_RGB_zero':True,'source_only_build':True,'runtime_claims':'None; actual motion, hit/ice, link7/8/9/10 removal, full exposure and source counts require a separate bounded trial.'}
 (out/'rebuild-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS exact6 RGBA, PNG, HDR1, anchors, support masks and two triplet rejoins')
if __name__=='__main__':main()
