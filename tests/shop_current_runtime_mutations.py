#!/usr/bin/env python3
"""Three fresh behavioral negatives: compile mutated production copies and require
runtime REQUIRE failures. Never accept compile failure as a killed mutant.
Run after run_shop_current_acceptance.sh has prepared EXTERNAL_OUTPUT_DIR.
"""
import argparse,json,os,shlex,shutil,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MUTATIONS={
'classic_3_rows':('for(unsigned yy=0;yy<4;yy++)for(unsigned xx=0;xx<4;xx++)sf.output[((p/SF_W)*4+yy)*SF_OW+(p%SF_W)*4+xx]=0;','for(unsigned yy=0;yy<3;yy++)for(unsigned xx=0;xx<4;xx++)sf.output[((p/SF_W)*4+yy)*SF_OW+(p%SF_W)*4+xx]=0;'),
'sprite_overwrite_alpha':('sf.output[out]=over(sf.output[out],color,a);sf.owner[(c->y+y/4)*SF_W+c->x+x/4]=1;','sf.output[out]=over(0,color,a);sf.owner[(c->y+y/4)*SF_W+c->x+x/4]=1;'),
'idle_static_merge':('if(sf.count&&(!sf.updating||sf.count>sf.static_count)&&sf.commands[sf.count-1].kind==C_CLASSIC)','if(sf.count&&sf.commands[sf.count-1].kind==C_CLASSIC)')}
EXPECTED_FAILURES={
 'classic_3_rows':'!sf.output[((p/320)*4+yy)*1280+(p%320)*4+xx]',
 'sprite_overwrite_alpha':'sf.output[y*1280+x]==oracle(x,y)',
 'idle_static_merge':'sf.count==2&&sf.event_count==2'}
SOURCES='src/hd_cursor.c src/common_menu_runs.c src/selector_font_output.c src/settings_font.c src/load_font.c src/selector_font.c src/helptext.c tests/load_font_globals.c src/font.c src/sprite.c src/data_text.c src/fonthand.c src/nortvars.c src/vga256d.c src/video_scale.c src/video_scale_hqNx.c'.split()
def build_limits():
 import resource
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(1048576*1024,1048576*1024))
def limits():
 import resource
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(524288*1024,524288*1024))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('data',type=Path);p.add_argument('output',type=Path);a=p.parse_args();o=a.output.resolve();raw=(R/'src/pregame_font.c').read_text();results=[]
 for name,(old,new) in MUTATIONS.items():
  assert raw.count(old)==1,name
  d=o/'mutants'/name;d.mkdir(parents=True,exist_ok=True);shutil.copytree(R/'src',d/'src',dirs_exist_ok=True);(d/'tests').mkdir(exist_ok=True)
  if not (d/'assets').exists():(d/'assets').symlink_to(R/'assets',target_is_directory=True)
  for f in (R/'tests').glob('*.c'):shutil.copy2(f,d/'tests'/f.name)
  (d/'src/pregame_font.c').write_text(raw.replace(old,new));(d/'shop_current_fixture.inc').write_text((o/'shop_current_fixture.inc').read_text().replace(str(R),str(d)))
  cmd=shlex.split(os.environ.get('CC','cc'))+['-std=c99','-O1','-g','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',*shlex.split(os.environ['SDL_CFLAGS']),'-Isrc','-I.','tests/shop_current_runtime.c',*SOURCES,'-Wl,--gc-sections',*shlex.split(os.environ['SDL_LIBS']),'-lm','-o','mutant']
  with (o/f'mutation-{name}-build.log').open('w') as log:subprocess.run(cmd,cwd=d,stdout=log,stderr=subprocess.STDOUT,timeout=180,check=True,preexec_fn=build_limits)
  args=[str(d/'mutant'),'--core',str(a.data.resolve()),*[str(o/'resources'/x) for x in ('fonts','metal','talon','front','generator')]]
  run=subprocess.run(args,cwd=d,capture_output=True,text=True,timeout=180,env={**os.environ,'SDL_VIDEODRIVER':'dummy'},preexec_fn=limits)
  (o/f'mutation-{name}.log').write_text(run.stdout+run.stderr)
  semantic=run.returncode!=0 and 'FAIL ' in run.stderr and '(stage=' in run.stderr and EXPECTED_FAILURES[name] in run.stderr
  results.append({'name':name,'returncode':run.returncode,'runtime_assertion_rejected':semantic,'stderr':run.stderr})
 receipt={'status':'PASS' if all(x['runtime_assertion_rejected'] for x in results) else 'FAIL','scope':'isolated current-source semantic mutants; no historical proof or game loop','mutations':results};(o/'mutation-results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));assert receipt['status']=='PASS'
if __name__=='__main__':main()
