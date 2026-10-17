#!/usr/bin/env python3
"""Generated-only P7 mode2 payload, binding, native geometry and rebuild checks."""
from pathlib import Path
import hashlib,json,re,shutil,struct,subprocess,tempfile
from PIL import Image
from rear_multi_p7_mode2_asset_projection import project_p7_mode2,PACKAGE
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/PACKAGE
sha=lambda b:hashlib.sha256(b).hexdigest()
from rear_multi_p9_mode2_asset_projection import project_p9_mode2
catalog=json.loads((ROOT/'assets/hd/manifest.json').read_text());catalog,newerpaths=project_p9_mode2(ROOT,catalog);baseline,newpaths=project_p7_mode2(ROOT,catalog)
assert len(newpaths)==37
old={str(p.relative_to(ROOT)):sha(p.read_bytes())for p in(ROOT/'assets').rglob('*')if p.is_file()and str(p.relative_to(ROOT))not in newpaths|newerpaths|{'assets/hd/manifest.json'}}
assert len(old)==7150
assert sha(''.join(n+'\0'+h+'\n'for n,h in sorted(old.items())).encode())=='815f9d31db1504784db46475a8ef8267b398a3b6f2c6cfb107a050ad942e7ebf'
binding=json.loads((ART/'binding.json').read_text());pins=json.loads((ART/'pins.json').read_text())
assert binding['phase_sequence']==[277,278,295,294,77] and binding['logical_size']==[12,14] and binding['anchor']==[0,0]
for name,pin in pins['inputs'].items():assert sha((ART/name).read_bytes())==pin
payloads={};fnvs=[]
def sample(raw,d,scale):
 return bytes(c for y in range(14*scale)for x in range(12*scale)for c in raw[4*(((2*y+1)*d//(2*scale))*12*d+(2*x+1)*d//(2*scale)):4*(((2*y+1)*d//(2*scale))*12*d+(2*x+1)*d//(2*scale))+4])
def components(raw,w):
 pending={(i%w,i//w)for i,a in enumerate(raw[3::4])if a>=128};sizes=[]
 while pending:
  queue=[pending.pop()];count=0
  while queue:
   x,y=queue.pop();count+=1
   for dx in[-1,0,1]:
    for dy in[-1,0,1]:
     p=x+dx,y+dy
     if p in pending:pending.remove(p);queue.append(p)
  sizes.append(count)
 return sizes
for row in binding['resources']:
 i,d=row['source_id'],row['density'];raw=(ART/row['rgba']).read_bytes();png=(ART/row['png']).read_bytes();hda=(ART/row['package_hda']).read_bytes();w,h=12*d,14*d
 assert len(raw)==w*h*4 and sha(raw)==row['rgba_sha256'] and sha(png)==row['png_sha256']
 assert hda==struct.pack('<4s6I',b'HDR1',1310000+i,d,12,14,0,0)+raw and sha(hda)==row['hda_sha256']
 with Image.open(ART/row['png'])as im:assert im.mode=='RGBA'and im.size==(w,h)and im.tobytes()==raw
 assert all(raw[p+3]or raw[p:p+3]==bytes(3)for p in range(0,len(raw),4))
 assert not any(raw[3:4*w*d:4]),'Top logical row must stay empty'
 fnv=14695981039346656037
 for v in raw:fnv=((fnv^v)*1099511628211)&((1<<64)-1)
 assert f'0x{fnv:016x}'==row['rgba_fnv1a64'];fnvs.append(fnv);payloads[i,d]=raw
 for scale in[2,4]:
  sizes=components(sample(raw,d,scale),12*scale);assert len(sizes)==2 and min(sizes)>100
for d in[4,8]:
 a,b=payloads[294,d],payloads[295,d];w,h=12*d,14*d
 assert all(a[4*(y*w+x):4*(y*w+x+1)]==b[4*(y*w+w-1-x):4*(y*w+w-x)]for y in range(h)for x in range(w))
macro=(ROOT/'src/rear_multi_p1_pins.h').read_text().split('#define REAR_P1_RGBA_PINS ',1)[1].split('\n',1)[0]
assert[int(s,16)for s in re.findall(r'UINT64_C\(0x([0-9a-f]+)\)',macro)][34:38]==fnvs
for p in ART.rglob('*'):
 if p.is_file()and p.suffix in['.json','.cjs','.md','.svg']:
  assert not re.search(r'/workspace/|/home/agent/|sediment://|libfile_|file_000000|ghp_|github_pat_',p.read_text()),p
for p in (ART/'sources').glob('*.svg'):
 s=p.read_text();assert all(x not in s for x in['<image','<filter','<mask','data:image','href=','stroke='])
 assert all(c in s for c in ['#fffaa1','#fff06b','#ffd338','#ff9e1c','#ff680a','#ef3904','#cd2102'])
with tempfile.TemporaryDirectory(prefix='rear-p7m2-generated-only-')as temp:
 t=Path(temp);r=t/'core';r.mkdir()
 for name in list(pins['inputs'])+['pins.json']:
  q=r/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ART/name,q)
 out=t/'output';subprocess.run(['node',str(r/'build.cjs'),str(out)],check=True)
 assert {p.name for p in out.iterdir()}=={p.name for p in(ART/'output').iterdir()}
 for p in out.iterdir():assert p.read_bytes()==(ART/'output'/p.name).read_bytes(),p.name
 assert subprocess.run(['node',str(r/'build.cjs'),str(out)],capture_output=True).returncode!=0
 authored=t/'reauthored';subprocess.run(['node',str(r/'author-geometry.cjs'),str(authored)],check=True)
 for p in authored.rglob('*'):
  if p.is_file():assert p.read_bytes()==(ART/p.relative_to(authored)).read_bytes()
 q=r/'sources/rear-multi-294.svg';q.write_text(q.read_text()+'\n');bad=t/'bad'
 assert subprocess.run(['node',str(r/'build.cjs'),str(bad)],capture_output=True).returncode!=0 and not bad.exists()
print('Rear P7 mode2 assets PASS:37 additive paths;7150 old assets exact;catalog inverse;four exact RGBA/PNG/HDR1 payloads;full-canvas reflection;native twin topology;isolated source-only rebuild/reauthor/tamper controls. Runtime qualification is separate.')
