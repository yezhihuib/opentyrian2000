#!/usr/bin/env python3
"""Reproduce the four selected terrain assets from generated-only crops and frozen HD edges."""
from pathlib import Path
from PIL import Image
import argparse,subprocess,json,hashlib,struct
p=argparse.ArgumentParser();p.add_argument('--base-pack',type=Path,required=True);p.add_argument('--output-root',type=Path,required=True);a=p.parse_args()
S=Path(__file__).resolve().parent;O=a.output_root;assert not O.exists(),O;O.mkdir(parents=True);(O/'work').mkdir();(O/'output').mkdir();(O/'runtime-overlay').mkdir()
contract=json.loads((S/'rebuild-contract.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
for i in [96,97,98,108]:
 f=S/'generated-crops'/f'terrain-shapesz-{i}-8.png';im=Image.open(f).convert('RGBA');assert im.size==(192,224) and im.getchannel('A').getextrema()==(255,255);assert sha(im.tobytes())==contract['generated_rgba'][str(i)];(O/'work'/f'{i}.rgba').write_bytes(im.tobytes())
for i,h in contract['frozen_hda'].items():
 b=(a.base_pack/f'terrain-shapesz-{i}-8.hda').read_bytes();assert sha(b)==h,(i,'frozen HDA changed');assert len(b)==172060 and b[:4]==b'HDR1';(O/'work'/f'{i}.rgba').write_bytes(b[28:])
subprocess.run(['c++','-std=c++17','-O2',str(S/'register_plateau_edges.cpp'),'-o',str(O/'register_plateau_edges')],check=True)
subprocess.run([str((O/'register_plateau_edges').resolve()),str(O/'work'),str(S/'registered-edge-pairs.txt')],check=True)
result=[]
for i in [96,97,98,108]:
 b=(O/'work'/f'{i}-registered.rgba').read_bytes();im=Image.frombytes('RGBA',(192,224),b);png=O/'output'/f'terrain-shapesz-{i}-8.png';im.save(png);hda=O/'runtime-overlay'/f'terrain-shapesz-{i}-8.hda';hda.write_bytes(b'HDR1'+struct.pack('<6I',2010000+i,8,24,28,0,0)+b);expected=contract['selected'][str(i)];r={'id':i,'rgba_sha256':sha(b),'png_sha256':sha(png.read_bytes()),'hda_sha256':sha(hda.read_bytes())};assert r['rgba_sha256']==expected['rgba_sha256'] and r['hda_sha256']==expected['hda_sha256'];r['png_file_exact']=r['png_sha256']==expected['png_sha256'];result.append(r)
(O/'rebuild-verification.json').write_text(json.dumps({'status':'passed','decoded_rgba_and_hda_exact':True,'items':result},indent=2)+'\n');print(json.dumps(result,indent=2))
