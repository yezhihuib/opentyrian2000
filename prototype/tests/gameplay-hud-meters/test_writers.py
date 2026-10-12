#!/usr/bin/env python3
"""Compile original source-extracted writers with/without only meter observers."""
import argparse,os,re,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE='56efa26181cd342347f8645f1c9adefc1e45d4ef'
sys.path.insert(0,str(HERE.parent/'gameplay-hud'));from test_writers import extract,normalized

def pieces(texts):
 game=texts['tyrian2.c'];a=game.index('/*---------------------Weapon Display');b=game.index('/*------------------------Power Bar',a);c=game.index('oldMapX3Ofs = mapX3Ofs;',b)
 return [extract(texts['varz.c'],'JE_wipeShieldArmorBars'),extract(texts['varz.c'],'JE_drawArmor'),
         'static void weapon_display(void) {\n'+game[a:b]+'\n}',
         'static void generator_display(void) {\n'+game[b:c]+'\n}']
def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');p.add_argument('--leak-check',action='store_true');a=p.parse_args()
 source={n:(ROOT/'src'/n).read_text() for n in ('varz.c','tyrian2.c','vga256d.c','nortvars.c')}
 baseline={n:subprocess.check_output(['git','show',BASE+':src/'+n],cwd=ROOT,text=True) for n in source}
 old,new=pieces(baseline),pieces(source)
 for before,after in zip(old,new):
  stripped=re.sub(r'\brender_mirror_hud_meter_(?:begin|end)\([^;]*\);','',after)
  assert normalized(stripped)==normalized(before),'Non-observer writer change'
 assert new[0].index('HUD_WRITE_ARMOR_WIPE')<new[0].index('fill_rectangle_xy')
 assert new[1].index('player[i].armor = 28')<new[1].index('HUD_WRITE_ARMOR_DRAW')<new[1].index('JE_dBar3')
 assert new[2].index('render_mirror_hud_meter_begin')<new[2].index('fill_rectangle_xy')<new[2].index('render_mirror_hud_meter_end')
 assert new[3].index('render_mirror_hud_meter_begin')<new[3].index('fill_rectangle_xy')<new[3].index('render_mirror_hud_meter_end')<new[3].index('lastPower = temp')
 helper='\n'.join(extract(source['vga256d.c'],n) for n in ('JE_rectangle','fill_rectangle_xy'))+'\n'+extract(source['nortvars.c'],'JE_dBar3')
 for n in ('JE_rectangle','fill_rectangle_xy'):assert normalized(extract(source['vga256d.c'],n))==normalized(extract(baseline['vga256d.c'],n))
 assert normalized(extract(source['nortvars.c'],'JE_dBar3'))==normalized(extract(baseline['nortvars.c'],'JE_dBar3'))
 with tempfile.TemporaryDirectory(prefix='hum2-writer-') as t:
  d=Path(t)
  renamed='\n'.join(re.sub(r'\b(JE_wipeShieldArmorBars|JE_drawArmor|weapon_display|generator_display)\b',lambda m:'baseline_'+m.group(),s) for s in old)
  (d/'writers.inc').write_text(helper+'\n'+renamed+'\n'+'\n'.join(new))
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1' if a.sanitize else '-O2','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-misleading-indentation','-I'+str(ROOT/'src'),'-I'+str(d),str(HERE/'test_writers.c'),'-lm','-o',str(d/'test')]
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
  subprocess.run(cmd,check=True);subprocess.run([str(d/'test'),str(d)],check=True,timeout=180,env=dict(os.environ,ASAN_OPTIONS=f'detect_leaks={int(a.leak_check)}:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
 print('PASS exact original writer bodies after removing only4 observer pairs; original draw/erase/clamp/update order retained.')
if __name__=='__main__':main()
