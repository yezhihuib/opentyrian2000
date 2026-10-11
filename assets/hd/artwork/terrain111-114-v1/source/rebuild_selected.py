from pathlib import Path
from PIL import Image
import argparse,json,hashlib,struct,subprocess
p=argparse.ArgumentParser();p.add_argument('--base-pack',type=Path,required=True);p.add_argument('--output-root',type=Path,required=True);a=p.parse_args();S=Path(__file__).resolve().parent;O=a.output_root;assert not O.exists()
for d in ['work','output','runtime-overlay']:(O/d).mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest();c=json.loads((S/'rebuild-contract.json').read_text())
for k,h in c['generated_rgba'].items():
 im=Image.open(S/'generated-crops'/f'terrain-shapesz-{k}-8.png').convert('RGBA');assert im.size==(192,224) and sha(im.tobytes())==h;(O/'work'/f'{k}.rgba').write_bytes(im.tobytes())
for k,h in c['frozen_hda'].items():
 b=(a.base_pack/f'terrain-shapesz-{k}-8.hda').read_bytes();assert b[:4]==b'HDR1' and len(b)==172060 and sha(b)==h;(O/'work'/f'{k}.rgba').write_bytes(b[28:])
for src,name in [('register_terrain_edges.cpp','register_edges'),('feather_occupied_alpha.cpp','feather_alpha')]:subprocess.run(['c++','-O2','-std=c++17',str(S/src),'-o',str(O/name)],check=True)
subprocess.run([str((O/'register_edges').resolve()),str(O/'work'),str(S/'registered-edge-pairs.txt')],check=True)
subprocess.run([str((O/'feather_alpha').resolve()),str(O/'work/111-registered.rgba'),str(O/'work/111-selected.rgba')],check=True)
result=[]
for k,v in c['selected'].items():
 name=f'{k}-selected.rgba' if k=='111' else f'{k}-registered.rgba'
 b=(O/'work'/name).read_bytes()
 im=Image.frombytes('RGBA',(192,224),b);png=O/'output'/f'terrain-shapesz-{k}-8.png';im.save(png);hda=O/'runtime-overlay'/f'terrain-shapesz-{k}-8.hda';hda.write_bytes(b'HDR1'+struct.pack('<6I',2010000+int(k),8,24,28,0,0)+b);r={'id':int(k),'png_sha256':sha(png.read_bytes()),'rgba_sha256':sha(b),'hda_sha256':sha(hda.read_bytes())};assert r['rgba_sha256']==v['rgba_sha256'] and r['hda_sha256']==v['hda_sha256'];r['png_file_exact']=r['png_sha256']==v['png_sha256'];result.append(r)
(O/'rebuild-verification.json').write_text(json.dumps({'status':'passed','decoded_rgba_and_hda_exact':True,'items':result},indent=2)+'\n');print(result)
