#!/usr/bin/env python3
"""Prove shared cash25/50/75 only adds display-observer hooks to original game sources.
No original game data is read or stored; comparison uses prior Git source.
"""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
BASE='ee1e98cfc6b8c00cb9a1837e4aa2c3a9aca2b0e5'
changes={
 'src/varz.c':[(b'\t\t\t\trender_mirror_cash25_value_allocated(i,type,x,y,deltaY,fixedPosition,followPlayer);\n',b''),(b'\t\t\t\trender_mirror_cash25_value_initialized(i, type);\n',b'')],
 'src/tyrian2.c':[(b'\t\trender_mirror_cash25_enemy_animated(i);\n\n',b''),(b'\trender_mirror_cash25_enemy_allocated(enemy,eDatI,uniqueShapeTableI);\n',b''),(b'\trender_mirror_cash25_enemy_initialized(enemy,eDatI,avail);\n',b'')],
 'src/entity_draw.c':[(b'int admitted=render_mirror_global_cash25_value(target,x,y,bank,index,style,slot);\n if(admitted<0)admitted=render_mirror_global_small_explosion(target,x,y,bank,index,style,slot);',b'int admitted=render_mirror_global_small_explosion(target,x,y,bank,index,style,slot);')]
}
# Keep exact indentation of the observer line outside of the native statements.
changes['src/tyrian2.c'][0]=(b'\t\t\t\trender_mirror_cash25_enemy_animated(i);\n\n',b'')
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'src'],cwd=ROOT,text=True).splitlines()
checked={}
for name in paths:
 if name in ['src/render_mirror.c','src/render_mirror.h','src/global_asset_registry.h'] or name.startswith('src/global_') and name.endswith('_mirror.inc'):continue
 prior=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
 now=(ROOT/name).read_bytes()
 for a,b in changes.get(name,[]):
  assert now.count(a)==1,(name,a)
  now=now.replace(a,b)
 assert now==prior,name
 checked[name]=hashlib.sha256(now).hexdigest()
print(json.dumps({'status':'PASS','base':BASE,'protected_files':len(checked),'source_sha256':checked},indent=2))
