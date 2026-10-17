#!/usr/bin/env python3
"""Exact generated-only reflection, additive binding, relocation and old-art proof."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,shutil,struct,subprocess,sys,tempfile
from PIL import Image
from rear_multi_p7_asset_projection import project_p7,FAMILY,PACKAGE,BASE
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/PACKAGE
SHA=lambda b:hashlib.sha256(b).hexdigest()
catalog=json.loads((ROOT/'assets/hd/manifest.json').read_text());baseline,newpaths=project_p7(ROOT,catalog)
assert len(newpaths)==28
binding=json.loads((ART/'binding.json').read_text());inputs=json.loads((ART/'inputs.json').read_text());outputs=json.loads((ART/'outputs.json').read_text())
assert binding['phase_sequence']==[277,278,297,296] and binding['logical_size']==[12,14] and binding['anchor']==[0,0]
old={str(p.relative_to(ROOT)):SHA(p.read_bytes())for p in(ROOT/'assets').rglob('*')if p.is_file()and str(p.relative_to(ROOT))not in newpaths|{'assets/hd/manifest.json'}}
assert len(old)==7122
assert SHA(''.join(n+'\0'+h+'\n'for n,h in sorted(old.items())).encode())=='3393a599abb256ae14366dc095b11cca003a924db60f7384f0cf80d9635e97c9'
source=ROOT/inputs['source_family_repo_path'];pins=[]
for inp,row in zip(inputs['resources'],binding['resources']):
 i,d=row['source_id'],row['density'];assert (inp['accepted_id'],inp['target_id'],inp['density'])==(277 if i==296 else 278,i,d)
 for kind in ['png','rgba']:assert SHA((source/inp[kind+'_name']).read_bytes())==inp[kind+'_sha256']
 src=(source/inp['rgba_name']).read_bytes();raw=(ART/row['rgba']).read_bytes();stride=12*d*4
 expected=b''.join(src[y*stride:(y+1)*stride]for y in range(14*d-1,-1,-1));assert raw==expected
 assert Counter(src[n:n+4]for n in range(0,len(src),4))==Counter(raw[n:n+4]for n in range(0,len(raw),4))
 with Image.open(ART/row['png'])as im:assert im.mode=='RGBA'and im.size==(12*d,14*d)and im.tobytes()==raw
 fnv=14695981039346656037
 for b in raw:fnv=((fnv^b)*1099511628211)&((1<<64)-1)
 assert f'0x{fnv:016x}'==row['rgba_fnv1a64']==outputs[f'{i}-{d}']['rgba_fnv1a64'];pins.append(fnv)
 assert sum(a>0 for a in raw[3::4])=={4:989,8:3739}[d]
macro=(ROOT/'src/rear_multi_p1_pins.h').read_text().split('#define REAR_P1_RGBA_PINS ',1)[1].split('\n',1)[0]
assert [int(s,16)for s in re.findall(r'UINT64_C\(0x([0-9a-f]+)\)',macro)][-4:]==pins
for p in ART.rglob('*'):
 if p.is_file()and p.suffix in['.json','.py','.md']:
  assert not re.search(r'/workspace/|/home/agent/|sediment://|libfile_|file_000000|ghp_|github_pat_',p.read_text()),p
with tempfile.TemporaryDirectory(prefix='rear-p7-art-')as temp:
 t=Path(temp);a=t/ART.name;s=t/'player-rear-multicannon-p5-mode2-twins-v1/output';a.mkdir();s.mkdir(parents=True)
 for n in['build.py','inputs.json','outputs.json']:shutil.copy2(ART/n,a/n)
 for row in inputs['resources']:
  for kind in ['png','rgba']:shutil.copy2(source/row[kind+'_name'],s/row[kind+'_name'])
 def command(out,hda,explicit=False):return[sys.executable,'-I','-B',str(a/'build.py'),'--output',str(out),'--hda-output',str(hda)]+(['--source',str(s)]if explicit else[])
 for n in range(2):
  out,hda=t/f'out{n}',t/f'hda{n}';subprocess.run(command(out,hda,bool(n)),check=True)
  assert {p.name for p in out.iterdir()}=={p.name for p in(ART/'output').iterdir()}
  for p in out.iterdir():assert p.read_bytes()==(ART/'output'/p.name).read_bytes()
  for row in binding['resources']:assert(hda/row['filename']).read_bytes()==(ROOT/row['pack_paths'][0]).read_bytes()
  assert subprocess.run(command(out,hda),capture_output=True).returncode!=0
 for kind in['png','rgba']:
  p=s/inputs['resources'][-1][kind+'_name'];saved=p.read_bytes();p.write_bytes(bytes([saved[0]^1])+saved[1:]);out,hda=t/f'bad-{kind}',t/f'bad-hda-{kind}'
  assert subprocess.run(command(out,hda),capture_output=True).returncode!=0 and not out.exists()and not hda.exists();p.write_bytes(saved)
 for out,hda in[(s/'nested',t/'hda-nested'),(t/'same',t/'same'),(t/'outer',t/'outer/inner')]:
  assert subprocess.run(command(out,hda),capture_output=True).returncode!=0 and not out.exists()and not hda.exists()
 assert not any(p.name=='__pycache__'or p.suffix=='.pyc'for p in t.rglob('*'))
print('Rear P7 mode1 assets PASS: four exact full-canvas reflections; sample/alpha/color preservation; native-density payload pins; eight HDR1 copies;28 additive paths;7122 old assets byte-exact; catalog inverse; two relocated rebuilds and bounded negative cases. Runtime qualification is separate.')
