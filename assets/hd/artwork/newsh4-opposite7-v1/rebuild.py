#!/usr/bin/env python3
"""Rebuild seven frozen, separately addressed pieces from one generated assembly."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,json,struct
P=Path(__file__).resolve().parent
BASES=[231,233,235,267,269,271,273]
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
  if f.is_symlink()or sha(f.read_bytes())!=expected:raise ValueError('source identity mismatch: '+name)
 master=Image.open(P/'sources/generated-whole.png').convert('RGBA');bbox=master.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox();assert bbox==(122,196,2050,507)
 raw=Image.new('RGBA',(1344,224));raw.paste(master.crop(bbox).resize((1328,200),Image.Resampling.LANCZOS),(16,8))
 logical=Image.open(P/'masks/alpha-assembly-logical.png').convert('L');assert logical.size==(168,28);assert set(logical.tobytes())<={0,255};assert sum(v!=0 for v in logical.tobytes())==2027
 mask=logical.resize((1344,224),Image.Resampling.NEAREST);art=Image.new('RGBA',raw.size,(12,8,0,255));art.alpha_composite(raw);art.putalpha(mask);b=bytearray(art.tobytes())
 for i in range(0,len(b),4):
  if b[i+3]==0:b[i:i+3]=b'\0\0\0'
 art=Image.frombytes('RGBA',art.size,bytes(b));prepared=[]
 for k,base in enumerate(BASES):
  tile=art.crop((k*192,0,(k+1)*192,224));rgba=tile.tobytes();header=b'HDR1'+struct.pack('<6I',1020000+base,8,24,28,6,7);hda=header+rgba;expected=stamps['outputs'][k]
  assert len(hda)==172060 and sha(rgba)==expected['rgba_sha256']and sha(hda)==expected['hda_sha256']
  assert tile.getchannel('A').tobytes()==mask.crop((k*192,0,(k+1)*192,224)).tobytes()
  prepared.append((base,tile,hda,expected))
 out.mkdir();rows=[];rejoined=Image.new('RGBA',art.size)
 for k,(base,tile,hda,expected)in enumerate(prepared):
  png=out/expected['png'];tile.save(png);assert sha(png.read_bytes())==expected['png_sha256'];(out/expected['hda']).write_bytes(hda);rejoined.paste(tile,(k*192,0));rows.append(expected)
 assert rejoined.tobytes()==art.tobytes()
 receipt={'status':'PASS','outputs':rows,'partition_rejoin_byte_exact':True,'opaque_logical_cells':2027,'alpha_exact_source_support':True,'transparent_RGB_zero':True,'source_only_build':True,'runtime_claims':'None; actual link2 moving/hit/ice/removal and source-count verification are separate.'}
 (out/'rebuild-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS exact seven RGBA, PNG, HDR1, anchors and support masks')
if __name__=='__main__':main()
