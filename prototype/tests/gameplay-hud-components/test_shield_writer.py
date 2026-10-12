#!/usr/bin/env python3
"""Independent original-writer oracle; synthetic indices only, no game assets."""
from pathlib import Path
import argparse,os,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'gameplay-hud'))
from test_writers import extract,require

def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');a=p.parse_args()
 varz=(ROOT/'src/varz.c').read_text();nort=(ROOT/'src/nortvars.c').read_text();game=(ROOT/'src/tyrian2.c').read_text();mainint=(ROOT/'src/mainint.c').read_text()
 draw=extract(varz,'JE_drawShield');wipe=extract(varz,'JE_wipeShieldArmorBars')
 require(draw,'JE_dBar3(VGAScreen,270,194,player[0].shield,144);','const uint y=193-(player[0].shield_max*2);','JE_rectangle(VGAScreen,270,y,278,y,68);')
 assert draw.index('render_mirror_hud_shield_drawn')>draw.index('JE_rectangle')
 assert wipe.index('render_mirror_hud_shield_wiped')<wipe.index('fill_rectangle_xy')
 require(game,'player[i].shield=shields[player[i].items.shield].mpwr;','player[i].shield_max=player[i].shield*2;','if(!endLevel) // draw HUD','++player[0].shield;')
 for writer in ('JE_playerDamage','JE_doSpecialShot'):
  text=extract(varz,writer);require(text,'JE_wipeShieldArmorBars();','JE_drawShield();')
 require(mainint,'this_player->shield=this_player->shield_max/2;')
 constant=mainint.split('else if (constantDie)',1)[1].split('if (!this_player->is_alive)',1)[0]
 require(constant,'this_player->shield=0;','JE_wipeShieldArmorBars();','JE_drawArmor();');assert 'JE_drawShield' not in constant
 # These finite rectangles do not include any weapon power/mode/sidekick writer.
 labels=[(285,5,309,10),(285,11,299,16),(285,26,303,31),(285,32,299,37)]
 live=[(289,17,311,20),(289,38,311,41),(285,44,295,52),(302,44,312,52),(284,64,313,80),(284,82,313,98),(269,12,277,104)]
 assert sum((x1-x0)*(y1-y0) for x0,y0,x1,y1 in labels)==350
 for x0,y0,x1,y1 in labels:
  for a0,b0,a1,b1 in live:assert max(x0,a0)>=min(x1,a1) or max(y0,b0)>=min(y1,b1)
 with tempfile.TemporaryDirectory(prefix='huc-writer-') as d:
  d=Path(d);(d/'writers.inc').write_text('\n'.join([extract(nort,'JE_dBar3'),draw,wipe]))
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-I'+str(d),str(HERE/'test_shield_writer.c'),'-lm','-o',str(d/'test')]
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  subprocess.run(cmd,check=True);env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
  subprocess.run([str(d/'test')],check=True,env=env)
 print('PASS source callsites and four350-pixel labels remain separate from all adjacent live fields; no original assets.')
if __name__=='__main__':main()
