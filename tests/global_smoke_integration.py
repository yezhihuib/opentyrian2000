#!/usr/bin/env python3
"""White-smoke observer-only source projection; not runtime/native evidence."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='624acc3c46773c7c1a089997deb2b00d8cc6d1ea'
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
changes={
 'src/varz.c':[(b'\t\t\t\trender_mirror_smoke_explosion_allocated(i,type,x,y,deltaY,fixedPosition,followPlayer);\n',b''),(b'\t\t\t\trender_mirror_smoke_explosion_initialized(i, type);\n',b'')],
 'src/entity_draw.c':[(b'int admitted=render_mirror_global_smoke(target,x,y,bank,index,style,slot);\n if(admitted<0)admitted=render_mirror_global_hitflare(target,x,y,bank,index,style,slot);',b'int admitted=render_mirror_global_hitflare(target,x,y,bank,index,style,slot);')]}
for family in ['talon','shield','pulse','hitflare','vulcan']:
 changes['src/global_'+family+'_mirror.inc']=[(b'  if(global_smoke_owner)global_smoke_owner[n]=global_smoke_foreign[n]=0;\n',b'')]
for path,replacements in changes.items():
 b=(ROOT/path).read_bytes()
 for added,replaced in replacements:
  assert b.count(added)==1,(path,added)
  b=b.replace(added,replaced)
 assert b==old(path),path
files=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'src'],cwd=ROOT,text=True).splitlines()
allowed=set(changes)|{'src/render_mirror.c','src/render_mirror.h','src/global_asset_registry.h'}
protected=[p for p in files if p not in allowed]
for path in protected:assert (ROOT/path).read_bytes()==old(path),path
print(json.dumps({'status':'PASS','base':BASE,'reverse_projected':sorted(changes),'protected_original_sources':len(protected),'no_original_logic_changes':True,'scope':'Source projection only, not runtime proof'},indent=2))
