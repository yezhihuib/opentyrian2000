#!/usr/bin/env python3
"""Observer-only reverse projection; this is source evidence, not native navigation."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[1]
BASE='3d8f3b28a74e919b2e584a84ff1fa17a0e78888f'
def original(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=R)
s=(R/'src/game_menu.c').read_text()
for line in ('\tpregame_shop_ship_begin(player[0].items.ship, player[0].x - 5, player[0].y - 7);\n','\tpregame_shop_ship_end();\n'):
 assert s.count(line)==1,line
 s=s.replace(line,'')
assert s.encode()==original('src/game_menu.c')
s=(R/'src/render_mirror.c').read_text()
for line in (' pregame_shop_ship_set_directory(NULL);\n',' pregame_shop_ship_set_directory(global_asset_directory);\n'):
 assert s.count(line)==1,line
 s=s.replace(line,'')
assert s.encode()==original('src/render_mirror.c')
protected=['src/sprite.c','src/shots.c','src/player.c','src/episodes.c','src/tyrian2.c','src/shop_pulse_proof.inc','src/shop_pulse_render.inc','src/global_asset_registry.h','src/global_talon_mirror.inc','src/global_shield_mirror.inc','src/global_pulse_mirror.inc','src/global_hitflare_mirror.inc','src/global_vulcan_mirror.inc']
for path in protected:assert (R/path).read_bytes()==original(path),path
assets=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'assets'],cwd=R,text=True).splitlines()
for path in assets:assert (R/path).read_bytes()==original(path),path
p='assets/hd/global-assets-v1/content/d1fe9bfe2dd84207fceb2f453c862eeaea802d9832fd14c1e1c3290622a53964.hda'
print(json.dumps({'result':'PASS','base':BASE,'shop_simulation_and_global_root_reverse_projection':True,'original_quad_blitter_unchanged':True,'protected_sources_unchanged':protected,'unchanged_asset_files':len(assets),'resource90233_sha256':hashlib.sha256((R/p).read_bytes()).hexdigest()}))
