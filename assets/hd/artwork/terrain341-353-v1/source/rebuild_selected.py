from pathlib import Path
from PIL import Image
import argparse,json,hashlib,struct,subprocess
p=argparse.ArgumentParser();p.add_argument('--output-root',type=Path,required=True);a=p.parse_args();S=Path(__file__).resolve().parent;O=a.output_root;assert not O.exists()
for d in ['work','output','runtime-overlay']:(O/d).mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest();c=json.loads((S/'rebuild-contract.json').read_text())
for k,h in c['generated_rgba'].items():
 im=Image.open(S/'generated-crops'/f'terrain-shapesz-{k}-8.png').convert('RGBA');assert im.size==(192,224) and sha(im.tobytes())==h and min(im.tobytes()[3::4])==255;(O/'work'/f'{k}.rgba').write_bytes(im.tobytes())
for k,e in c['frozen_edges'].items():
 im=Image.new('RGBA',(192,224),(0,0,0,255));px=im.load()
 for x in range(192):px[x,0]=(*e['top'][x],255);px[x,223]=(*e['bottom'][x],255)
 for y in range(224):px[0,y]=(*e['left'][y],255);px[191,y]=(*e['right'][y],255)
 (O/'work'/f'{k}.rgba').write_bytes(im.tobytes())
subprocess.run(['c++','-O2','-std=c++17',str(S/'register_terrain_edges.cpp'),'-o',str(O/'register_edges')],check=True)
subprocess.run([str((O/'register_edges').resolve()),str(O/'work'),str(S/'registered-edge-pairs.txt')],check=True)
result=[]
for k,v in c['selected'].items():
 b=(O/'work'/f'{k}-registered.rgba').read_bytes();assert len(b)==172032 and min(b[3::4])==255
 im=Image.frombytes('RGBA',(192,224),b);png=O/'output'/f'terrain-shapesz-{k}-8.png';im.save(png);hda=O/'runtime-overlay'/f'terrain-shapesz-{k}-8.hda';hda.write_bytes(b'HDR1'+struct.pack('<6I',2010000+int(k),8,24,28,0,0)+b)
 r={'id':int(k),'png_sha256':sha(png.read_bytes()),'rgba_sha256':sha(b),'hda_sha256':sha(hda.read_bytes())};assert r['rgba_sha256']==v['rgba_sha256'] and r['hda_sha256']==v['hda_sha256'];r['regenerated_png_file_exact']=r['png_sha256']==v['png_sha256'];assert sha((S.parent/'output'/png.name).read_bytes())==v['png_sha256'];result.append(r)
report={'status':'PASS','decoded_rgba_and_hda_exact':True,'committed_png_file_hashes_verified':True,'frozen_dependency':'Only exact accepted perimeter RGB values; no base checkout needed','items':result};(O/'rebuild-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
