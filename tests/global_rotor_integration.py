#!/usr/bin/env python3
"""Verify the rotor observer changes no original gameplay statements."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='d418bc85e3033936a1f8d263679aeaba0e3640b7'
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'src'],cwd=ROOT,text=True).splitlines()
ignored={'src/render_mirror.c','src/render_mirror.h','src/global_asset_registry.h'}
lines=[b'\t\t\t\trender_mirror_rotor_enemy_animated(i);\n',b'\trender_mirror_rotor_enemy_allocated(enemy,eDatI,uniqueShapeTableI);\n',b'\trender_mirror_rotor_enemy_initialized(enemy,eDatI,avail);\n']
checked={}
for name in paths:
 if name in ignored:continue
 prior=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT);now=(ROOT/name).read_bytes()
 if name=='src/tyrian2.c':
  for line in lines:
   assert now.count(line)==1,(name,line)
   now=now.replace(line,b'')
 if name.startswith('src/global_') and name.endswith('_mirror.inc'):
  line=b'  if(global_rotor_owner)global_rotor_owner[n]=global_rotor_foreign[n]=0;\n'
  assert now.count(line)==1,name
  now=now.replace(line,b'')
 assert now==prior,name
 checked[name]=hashlib.sha256(prior).hexdigest()
print(json.dumps({'status':'PASS','base':BASE,'protected_files':len(checked),'source_sha256':checked},indent=2))
