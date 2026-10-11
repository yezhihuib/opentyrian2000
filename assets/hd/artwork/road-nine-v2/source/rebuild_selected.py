#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,struct,argparse,shutil
p=argparse.ArgumentParser();p.add_argument('--base-pack',type=Path,required=True);p.add_argument('--output-root',type=Path,required=True);a=p.parse_args();S=Path(__file__).resolve().parent;O=a.output_root;assert not O.exists(),O
for d in ['', 'work','input-registered','output','runtime-overlay']:(O/d).mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest();c=json.loads((S/'rebuild-contract.json').read_text());color=json.loads((S/'color-registration.json').read_text())
for k,h in c['generated_rgba'].items():
 i=int(k);src=S/'generated-crops'/f'terrain-shapesz-{i}-8.png';im=Image.open(src).convert('RGBA');assert im.size==(192,224) and im.getchannel('A').getextrema()==(255,255) and sha(im.tobytes())==h
 dst=O/'input-registered'/src.name
 if i in color['targets']:
  cmd=['convert',str(src)]
  for channel,g,b in zip('RGB',color['gain'],color['offset_0_255']):cmd+=['-channel',channel,'-evaluate','Multiply',str(g),'-evaluate','Add',str(b/255*100)+'%']
  subprocess.run(cmd+['+channel','PNG32:'+str(dst)],check=True)
 else:shutil.copy2(src,dst)
 if i==47:
  native=O/'work/47-periodic.png';subprocess.run(['/usr/bin/python3',str(S/'periodize_fill.py'),str(dst),str(native)],check=True);dst=native
 b=Image.open(dst).convert('RGBA').tobytes();(O/'work'/f'{i}.rgba').write_bytes(b)
for k,h in c['frozen_hda'].items():
 b=(a.base_pack/f'terrain-shapesz-{k}-8.hda').read_bytes();assert len(b)==172060 and b[:4]==b'HDR1' and sha(b)==h;(O/'work'/f'{k}.rgba').write_bytes(b[28:])
subprocess.run(['c++','-std=c++17','-O2',str(S/'register_road_edges.cpp'),'-o',str(O/'register_road_edges')],check=True)
subprocess.run([str((O/'register_road_edges').resolve()),str(O/'work'),str(S/'registered-edge-pairs.txt')],check=True)
result=[]
for k,expected in c['selected'].items():
 i=int(k);b=(O/'work'/f'{i}-registered.rgba').read_bytes();im=Image.frombytes('RGBA',(192,224),b);assert im.getchannel('A').getextrema()==(255,255);png=O/'output'/f'terrain-shapesz-{i}-8.png';im.save(png);hda=O/'runtime-overlay'/f'terrain-shapesz-{i}-8.hda';hda.write_bytes(b'HDR1'+struct.pack('<6I',2010000+i,8,24,28,0,0)+b);r={'id':i,'rgba_sha256':sha(b),'png_sha256':sha(png.read_bytes()),'hda_sha256':sha(hda.read_bytes())};assert r['rgba_sha256']==expected['rgba_sha256'] and r['hda_sha256']==expected['hda_sha256'],r;r['png_file_exact']=r['png_sha256']==expected['png_sha256'];result.append(r)
(O/'rebuild-verification.json').write_text(json.dumps({'status':'passed','decoded_rgba_and_hda_exact':True,'items':result},indent=2)+'\n');print(json.dumps(result,indent=2))
