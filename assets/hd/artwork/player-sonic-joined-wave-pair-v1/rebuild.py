#!/usr/bin/env python3
"""Rebuild frozen whole-wave143/144 R3 from generated master only."""
from pathlib import Path
from PIL import Image,ImageOps,__version__ as pillow_version
import argparse,hashlib,json,struct
SHA=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parent;c=json.loads((root/'contract.json').read_text());out=a.output.resolve()
 assert not out.exists() and out.parent.is_dir() and not any(q.is_symlink() for q in [out,*out.parents])
 assert root not in out.parents and out not in root.parents
 assert pillow_version==c['reconstruction']['version']
 source=root/c['source'];assert root in source.resolve().parents and SHA(source.read_bytes())==c['source_sha256']
 im=Image.open(source).convert('RGBA');assert list(im.size)==c['source_size'];r=c['reconstruction']
 assert round((r['crop'][2]-r['crop'][0])*r['resize'][1]/(r['crop'][3]-r['crop'][1]))==r['resize'][0]
 piece=im.crop(r['crop']).resize(r['resize'],Image.Resampling.LANCZOS);whole=Image.new('RGBA',tuple(r['canvas']));whole.paste(piece,tuple(r['paste']))
 assert not any(whole.tobytes()[104*192*4+3::4])
 images={e['id']:whole.crop(tuple(e['split_box'])) for e in c['entries']}
 assert ImageOps.mirror(images[143]).tobytes()!=images[144].tobytes()
 joined=Image.new('RGBA',(192,112));joined.paste(images[143],(0,0));joined.paste(images[144],(96,0));assert joined.tobytes()==whole.tobytes()
 out.mkdir();whole.save(out/'whole-wave-8.png');assert SHA((out/'whole-wave-8.png').read_bytes())==c['whole_output']['PNG_sha256'] and SHA(whole.tobytes())==c['whole_output']['RGBA_sha256']
 for e in c['entries']:
  i=e['id'];pic=images[i];raw=pic.tobytes();hda=struct.pack('<4s6I',b'HDR1',*e['header_u32'])+raw
  assert SHA(raw)==e['RGBA_sha256'] and SHA(hda)==e['HDA_sha256'];pic.save(out/f'bullet-{i}-8.png');(out/f'bullet-{i}-8.hda').write_bytes(hda);assert SHA((out/f'bullet-{i}-8.png').read_bytes())==e['PNG_sha256']
 print('PASS exact generated143/144 R3 crop/proportional whole registration and asymmetric split; no original-data input')
if __name__=='__main__':main()
