#!/usr/bin/env python3
"""Rebuild selected Mint27 import from the generated master; never paints artwork."""
from pathlib import Path
from PIL import Image, __version__ as pillow_version
import argparse, hashlib, json, struct
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 root=Path(__file__).resolve().parent;c=json.loads((root/'contract.json').read_text());out=a.output.resolve()
 assert not out.exists() and not any(x.is_symlink()for x in [out,*out.parents])
 assert root not in out.parents and out not in root.parents
 assert pillow_version==c['reconstruction']['version']
 source=root/c['source'];assert root in source.resolve().parents and sha(source.read_bytes())==c['source_sha256']
 im=Image.open(source).convert('RGBA');r=c['reconstruction'];piece=im.crop(r['crop']).resize(r['resize'],Image.Resampling.LANCZOS)
 result=Image.new('RGBA',(96,112));result.alpha_composite(piece,tuple(r['paste']));raw=result.tobytes()
 hda=b'HDR1'+struct.pack('<6I',*c['header_u32'])+raw
 assert sha(raw)==c['RGBA_sha256'] and sha(hda)==c['HDA_sha256']
 out.mkdir(parents=True);result.save(out/'bullet-27-8.png');(out/'bullet-27-8.hda').write_bytes(hda)
 assert sha((out/'bullet-27-8.png').read_bytes())==c['PNG_sha256']
 print('PASS generated master crop/resize/registration: exact PNG, RGBA and HDA; no repaint, recolor or alpha rewrite')
if __name__=='__main__':main()
