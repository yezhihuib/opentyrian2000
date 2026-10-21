#!/usr/bin/env python3
"""Small-explosion observer-only source projection; not runtime/native evidence."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='c94acb347c610a0320386dc3a2ee83c1f273a776'
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
changes={
 'src/varz.c':[(b'\t\t\t\trender_mirror_small_explosion_allocated(i,type,x,y,deltaY,fixedPosition,followPlayer);\n',b''),(b'\t\t\t\trender_mirror_small_explosion_initialized(i, type);\n',b'')],
 'src/entity_draw.c':[(b'int admitted=render_mirror_global_small_explosion(target,x,y,bank,index,style,slot);\n if(admitted<0)admitted=render_mirror_global_smoke(target,x,y,bank,index,style,slot);',b'int admitted=render_mirror_global_smoke(target,x,y,bank,index,style,slot);')]}
for family in ['talon','shield','pulse','hitflare','vulcan','smoke']:
 changes['src/global_'+family+'_mirror.inc']=[(b'  if(global_small_explosion_owner)global_small_explosion_owner[n]=global_small_explosion_foreign[n]=0;\n',b'')]
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
