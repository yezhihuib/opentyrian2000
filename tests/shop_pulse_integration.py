#!/usr/bin/env python3
"""SHOP observer reverse projection: original simulation and shop control flow.
No original game data is loaded or distributed by this source-only check.
"""
from pathlib import Path
import hashlib,json,subprocess
from global_talon_reconstruction import extract
ROOT=Path(__file__).resolve().parents[1]
BASE='167cc10386a927fb84c3a053eeb7e6478a763e5f'
def old(path):
 return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT).decode().replace('\r\n','\n')
def current(path):return (ROOT/path).read_text()
def strip(s,lines):
 for line in lines:
  assert s.count(line)==1,(line,s.count(line));s=s.replace(line,'')
 return s
cases=0
for name in ('player_shot_create','simulate_player_shots'):
 before=extract(old('src/shots.c'),name);after=extract(current('src/shots.c'),name)
 if name=='player_shot_create':
  after=strip(after,['\n\t\tshop_pulse_allocated(shot_id);','\n\t\tshop_pulse_initialized(shot_id, portNum, bay_i, wpNum, playerNum, shotMultiPos[bay_i]);'])
 else:
  bracket='\t\t\t\t\t{\n\t\t\t\t\t\tpregame_shop_pulse_head_begin(z, anim_frame, tempShotX+1, tempShotY);\n\t\t\t\t\t\tblit_sprite2(VGAScreen, tempShotX+1, tempShotY, spriteSheet8, anim_frame);\n\t\t\t\t\t\tpregame_shop_pulse_head_end();\n\t\t\t\t\t}'
  assert after.count(bracket)==1;after=after.replace(bracket,'\t\t\t\t\t\tblit_sprite2(VGAScreen, tempShotX+1, tempShotY, spriteSheet8, anim_frame);')
 assert after==before,name;cases+=1
before=extract(old('src/game_menu.c'),'JE_weaponViewFrame');after=extract(current('src/game_menu.c'),'JE_weaponViewFrame')
after=strip(after,['\n\tpregame_shop_pulse_preview_begin();','\n\t\t\tshop_pulse_front_begin(item, i, item_power, item_mode, 1, weaponPort[item].op[item_mode][item_power]);','\n\t\t\tshop_pulse_front_end();','\n\tpregame_shop_pulse_preview_end();'])
assert after==before;cases+=1
# No accepted art (or battle family ownership implementation) was modified.
protected=['src/global_pulse_mirror.inc','src/global_vulcan_mirror.inc','src/global_shield_mirror.inc','src/global_talon_mirror.inc','src/global_hitflare_mirror.inc','src/global_asset_registry.h']
assert not subprocess.check_output(['git','diff',BASE,'--']+protected,cwd=ROOT)
# Static shop icons were independently accepted after the Pulse slice.
ASSET_BASE='3d8f3b28a74e919b2e584a84ff1fa17a0e78888f'
assert not subprocess.check_output(['git','diff',ASSET_BASE,'--','assets'],cwd=ROOT)
print(json.dumps({'result':'PASS','reverse_projected_functions':cases,'base':BASE,'asset_base':ASSET_BASE,'protected_assets_and_battle_owners_unchanged':True},sort_keys=True))
