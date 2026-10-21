#!/usr/bin/env python3
"""Reverse-project the two observation-only hooks to the accepted local base."""
from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[1]
BASE='6595608e85808a061e31399ab66ca5184894578b'
def original(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=R)
s=(R/'src/sprite.c').read_text()
for line in ('\tpregame_font_quad_begin(surface,x,y,sprite2s.data,sprite2s.size,index);\n','\tpregame_font_quad_end();\n'):
 assert s.count(line)==1
 s=s.replace(line,'')
assert s.encode()==original('src/sprite.c')
protected=['src/game_menu.c','src/shots.c','src/player.c','src/episodes.c','src/tyrian2.c','src/shop_pulse_proof.inc','src/shop_pulse_render.inc']
for path in protected:
 current=(R/path).read_bytes().decode()
 if path=='src/game_menu.c':
  for hook in ('\tpregame_shop_ship_begin(player[0].items.ship, player[0].x - 5, player[0].y - 7);\n','\tpregame_shop_ship_end();\n'):
   assert current.count(hook)==1;current=current.replace(hook,'')
 assert current.encode()==original(path),path
print(json.dumps({'result':'PASS','base':BASE,'original_quad_blitter_reverse_projection':True,'protected_state_and_pulse_sources_unchanged':protected}))
