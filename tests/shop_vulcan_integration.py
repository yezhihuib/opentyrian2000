#!/usr/bin/env python3
"""Observer-only byte reverse projection; not native navigation evidence."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='e9aaf5f362c53b70babebaab5a1c5793da3d3eb2'
def original(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
# Each allowlisted addition is a presentation observer; remove exactly these
# bytes and require the complete original source, including line endings.
additions={
 'src/shots.c':['#include "shop_vulcan.h"','\t\t\t\t\t\tpregame_shop_vulcan_head_begin(z, anim_frame, tempShotX+1, tempShotY);','\t\t\t\t\t\tpregame_shop_vulcan_head_end();','\t\tshop_vulcan_allocated(shot_id, PX, PY, mouseX, mouseY);','\t\tshop_vulcan_initialized(shot_id, portNum, bay_i, wpNum, playerNum, shotMultiPos[bay_i]);'],
 'src/game_menu.c':['#include "shop_vulcan.h"','\tpregame_shop_vulcan_preview_begin();','\t\t\tshop_vulcan_front_begin(item, i, item_power, item_mode, 1, weaponPort[item].op[item_mode][item_power]);','\t\t\tshop_vulcan_front_end();','\tpregame_shop_vulcan_preview_end();'],
 'src/episodes.c':['#include "shop_vulcan.h"','\t\tshop_vulcan_port_name(i, nameLen, weaponPort[i].name);','\t\tshop_vulcan_port_loaded(i);'],
 'src/render_mirror.c':['#include "shop_vulcan.h"',' pregame_shop_vulcan_set_directory(NULL);',' pregame_shop_vulcan_set_directory(global_asset_directory);']}
for path,lines in additions.items():
 s=(ROOT/path).read_bytes();newline=b'\r\n' if path=='src/shots.c' else b'\n'
 for line in lines:
  b=line.encode()+newline;assert s.count(b)==1,(path,line,s.count(b));s=s.replace(b,b'')
 assert s==original(path),path
protected=['src/sprite.c','src/player.c','src/tyrian2.c','src/shop_pulse.h','src/shop_pulse_proof.inc','src/shop_pulse_render.inc','src/shop_ship_render.inc','src/shop_static_render.inc','src/global_asset_registry.h']+[f'src/global_{f}_mirror.inc' for f in ('talon','shield','pulse','hitflare','vulcan')]
for path in protected:assert (ROOT/path).read_bytes()==original(path),path
assets=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'assets'],cwd=ROOT,text=True).splitlines()
for path in assets:assert (ROOT/path).read_bytes()==original(path),path
print(json.dumps({'result':'PASS','base':BASE,'complete_sources_reverse_projected':list(additions),'protected_sources_unchanged':protected,'unchanged_asset_files':len(assets),'scope':'Source-only evidence; no native or runtime parity claim'},sort_keys=True))
