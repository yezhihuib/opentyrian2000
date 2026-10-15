#!/usr/bin/env python3
"""Rebuild frozen Sonic oblique223/224 generated import; never paints or reads game data."""
from pathlib import Path
from PIL import Image,ImageOps,__version__ as pillow_version
import argparse,hashlib,json,struct
SHA=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parent;c=json.loads((root/'contract.json').read_text());out=a.output.resolve()
 assert not out.exists()and out.parent.is_dir()and not any(q.is_symlink()for q in [out,*out.parents])
 assert root not in out.parents and out not in root.parents
 assert pillow_version==c['reconstruction']['version']
 source=root/c['source'];assert root in source.resolve().parents and SHA(source.read_bytes())==c['source_sha256']
 im=Image.open(source).convert('RGBA');assert list(im.size)==c['source_size'];r=c['reconstruction'];piece=im.crop(r['crop']).resize(r['resize'],Image.Resampling.LANCZOS)
 result=Image.new('RGBA',tuple(r['canvas']));result.paste(piece,tuple(r['paste']));images={223:result,224:ImageOps.mirror(result)}
 out.mkdir()
 for e in c['entries']:
  i=e['id'];pic=images[i];raw=pic.tobytes();hda=struct.pack('<4s6I',b'HDR1',*e['header_u32'])+raw
  assert SHA(raw)==e['RGBA_sha256']and SHA(hda)==e['HDA_sha256'];pic.save(out/f'bullet-{i}-8.png');(out/f'bullet-{i}-8.hda').write_bytes(hda);assert SHA((out/f'bullet-{i}-8.png').read_bytes())==e['PNG_sha256']
 print('PASS exact generated223/224 master crop/proportional registration:2 PNG/RGBA/HDA identities and exact full-canvas flipX; no paint,recolor,threshold or original-mask input')
if __name__=='__main__':main()
