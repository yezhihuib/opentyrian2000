#!/usr/bin/env python3
"""Prepare an isolated instrumented copy. This script never launches the game."""
import argparse,hashlib,json,pathlib,shutil,subprocess
p=argparse.ArgumentParser();p.add_argument('--repo',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();here=pathlib.Path(__file__).resolve().parent
commit=subprocess.check_output(['git','-C',str(a.repo),'rev-parse','HEAD'],text=True).strip()
if subprocess.check_output(['git','-C',str(a.repo),'status','--porcelain'],text=True).strip():raise SystemExit('Checkpoint must be clean.')
if a.out.exists():raise SystemExit('Use a fresh output directory; no overwrite.')
a.out.mkdir(parents=True);shutil.copytree(a.repo/'src',a.out/'src')
for n in ['Makefile','COPYING']:shutil.copy2(a.repo/n,a.out/n)
for n in ['settings_fixture.c','settings_fixture.h']:shutil.copy2(here/n,a.out/'src'/n)
def edit(n,fn):
 q=a.out/'src'/n;s=q.read_text();s=fn(s);q.write_text(s)
def replace_one(s,old,new):
 if s.count(old)!=1:raise ValueError((old,s.count(old)))
 return s.replace(old,new,1)
def inc(s):return '#include "settings_fixture.h"\n'+s
for n in ['opentyr.c','tyrian2.c','settings_font.c','startup_logos.c','title_layers.c','render_mirror.c','video.c','palette.c','nortsong.c']:edit(n,inc)
def setup(s):
 s=replace_one(s,'mt_srand(time(NULL));','sf_fixture_init();\n\tmt_srand(32402394); /* deterministic A/B fixture seed */')
 anchor='settings_font_frame_begin(currentMenu, selectedMenuItemIndexes[currentMenu], currentPicker == MENU_ITEM_NONE ? 0 : currentPicker - MENU_ITEM_DISPLAY + 1);'
 s=replace_one(s,anchor,anchor+'\n\t\tsf_fixture_frame(currentMenu, selectedMenuItemIndexes[currentMenu], currentPicker == MENU_ITEM_NONE ? 0 : currentPicker - MENU_ITEM_DISPLAY + 1, pickerSelectedIndex);')
 s=replace_one(s,'settings_font_cursor_done();','settings_font_cursor_done();\n\t\tsf_fixture_ready();')
 s=replace_one(s,'settings_font_cursor_erased();','settings_font_cursor_erased();\n\t\tsf_fixture_advance();')
 s=replace_one(s,'settings_font_end();\n\t\t\t\treturn;','settings_font_end();\n\t\t\t\tsf_fixture_exit();\n\t\t\t\treturn;')
 s=replace_one(s,'\t\t\tSDL_Delay(16);','\t\t\tsf_fixture_wait("menu-poll",16);\n\t\t\tSDL_Delay(16);')
 return s
edit('opentyr.c',setup)
edit('tyrian2.c',lambda s:replace_one(s,'title_layers_cursor_erased();','title_layers_cursor_erased();\n\t\tsf_fixture_title(selectedIndex);'))
for n,owner in [('settings_font.c','settings'),('startup_logos.c','startup'),('title_layers.c','title'),('render_mirror.c','gameplay'),('video.c','classic')]:
 def fn(s,n=n,owner=owner):
  if n=='settings_font.c':
   target='bool settings_font_present(SDL_Renderer *renderer,SDL_Surface *surface,const SDL_Rect *destination,bool foreign_owner)\n{'
   s=replace_one(s,target,target+'\n sf_fixture_lease(sf.active,sf.frame,sf.count,sf.generation);')
  # Every module has one final frame-present; video also initializes a black frame.
  if n=='video.c':s=s.replace('SDL_RenderPresent(main_window_renderer);','sf_fixture_present(main_window_renderer,"classic"); SDL_RenderPresent(main_window_renderer);')
  else:s=s.replace('SDL_RenderPresent(renderer);',f'sf_fixture_present(renderer,"{owner}"); SDL_RenderPresent(renderer);')
  return s
 edit(n,fn)
edit('render_mirror.c',lambda s:replace_one(replace_one(s,'settings_font_pixel(surface,address,style);','sf_fixture_pixel(surface,address,style);\n settings_font_pixel(surface,address,style);'),'settings_font_rect(s,rect);','sf_fixture_rect(s,rect);\n settings_font_rect(s,rect);'))
edit('palette.c',lambda s:replace_one(s,'settings_font_fade_step(steps,first_color,last_color);','settings_font_fade_step(steps,first_color,last_color);\n\tsf_fixture_fade(steps,first_color,last_color);'))
edit('nortsong.c',lambda s:replace_one(replace_one(s,'void setDelay(int delay)  // FKA NortSong.frameCount\n{','void setDelay(int delay)  // FKA NortSong.frameCount\n{\n\tsf_fixture_wait("setDelay",delay);'),'void service_wait_delay(void)\n{','void service_wait_delay(void)\n{\n\tsf_fixture_wait("service_wait_delay",0);'))
manifest={'source_commit':commit,'source_gate':'PENDING; preparation only','game_launches':0,'fixture_seed':32402394,'files':{str(q.relative_to(a.out)):hashlib.sha256(q.read_bytes()).hexdigest() for q in (a.out/'src').glob('*') if q.is_file()}}
(a.out/'FIXTURE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');print(a.out)
