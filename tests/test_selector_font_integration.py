#!/usr/bin/env python3
"""Finite selector observer additions project to the exact approved base tokens."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess, xml.etree.ElementTree as ET, runpy
ROOT=Path(__file__).resolve().parents[1]
PREGAME=runpy.run_path(str(ROOT/'tests/pregame_font_projection.py'))
pregame_project=PREGAME['project_legacy']
BASE='4c03d538fd5b2c03fdc6e983511f04c3695cc118'
DOCUMENTATION_ONLY={'README.md','README.zh-CN.md'}
CHANGED=DOCUMENTATION_ONLY|{'src/load_font.c','src/menus.c','src/palette.c','src/params.c','src/picload.c','src/render_mirror.c','src/settings_font.c','src/sprite.c','src/video.c','visualc/opentyrian.vcxproj','tests/run_settings_font_tests.sh','tests/run_load_font_tests.sh','prototype/test-manual-hd.py','prototype/test-datacube-blend.py'}
def git(*a):return subprocess.check_output(['git','-C',str(ROOT),*a])
def tokens(s):
 p=r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*[\s\S]*?\*/|//[^\n]*|\s+|[A-Za-z_]\w*|(?:0[xX][0-9a-fA-F]+|\d+)(?:[uUlLfF]*)|<<=?|>>=?|\+\+|--|->|&&|\|\||[+*/%&|^!=<>-]=|.'
 return [x for x in re.findall(p,s) if not x.isspace() and not x.startswith(('/*','//'))]
def project(name,s):
 s=pregame_project(name,s.encode()).decode()
 s=s.replace('\r\n','\n').replace('#include "selector_font.h"\n','')
 if name=='src/video.c':
  s='\n'.join(l for l in s.split('\n') if not l.strip().startswith(('if(selector_font_present(', 'if(selector_font_owns_display()')))
  s=s.replace(' || selector_font_owns_display()','')
 allowed={'set_directory','begin','end','invalidate','table_reset','frame_begin','run_begin','run_end','glyph_begin','glyph_end','frame_end','pixel','rect','cursor_begin','cursor_done','cursor_sprite_begin','cursor_sprite_end','cursor_erased','fade_declare','fade_start','fade_step'}
 for m in reversed(list(re.finditer(r'\bselector_font_(\w+)\(',s))):
  assert m[1] in allowed,(name,m[1]);pos=m.end();depth=1
  while depth:
   if s[pos]=='(':depth+=1
   if s[pos]==')':depth-=1
   pos+=1
  assert s[pos]==';';s=s[:m.start()]+s[pos+1:]
 return tokens(s)
def regression_projection():
 # Historical gameplay regressions admit only this bounded selector delta.
 # Prove every changed original source still projects to the approved base;
 # new modules are finite; published B/C files have exact whole-file pins.
 pregame_sources=PREGAME['verify']()
 published=PREGAME['verify_published_delta']()
 selector_sources={name for name in CHANGED if name.startswith('src/')} | {
  'src/selector_font.c','src/selector_font.h','src/selector_font_output.c','src/selector_font_output.h'}
 assert set(git('diff',BASE,'--name-only','--','src','assets').decode().splitlines())==selector_sources|pregame_sources|published
 for name in sorted(selector_sources):
  if name in CHANGED:
   assert project(name,(ROOT/name).read_bytes().decode())==tokens(git('show',BASE+':'+name).decode()),name
 # Renderer helper comparisons are byte-exact after just these three hooks.
 mirror=pregame_project('src/render_mirror.c',(ROOT/'src/render_mirror.c').read_bytes()).decode()
 for hook in ('#include "selector_font.h"\n',' selector_font_pixel(surface,address,style);\n',' selector_font_rect(s,rect);\n'):
  assert mirror.count(hook)==1,hook
  mirror=mirror.replace(hook,'')
 assert mirror==git('show',BASE+':src/render_mirror.c').decode()
 return selector_sources|pregame_sources|published,mirror

def main():
 PREGAME['PORTABLE']['verify']()
 PREGAME['verify_published_delta']()  # qualify actual files before idempotent legacy passes
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args();changed=[];unchanged=0;assets=0;proofs=0
 for line in git('ls-tree','-rz',BASE).split(b'\0'):
  if not line:continue
  meta,name=line.split(b'\t',1);name=name.decode();_,kind,blob=meta.decode().split();path=ROOT/name;assert path.is_file() and not path.is_symlink(),name
  raw=pregame_project(name,path.read_bytes());current=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
  if current==blob:
   unchanged+=1
   if name.startswith('assets/'):assets+=len(raw)
  else:
   assert name in CHANGED,name;changed.append(name)
   if name.startswith('tests/run_'):
    assert raw.decode().replace('src/selector_font.c src/selector_font_output.c ', '').replace('$(pkg-config --libs sdl2) -lm -o','$(pkg-config --libs sdl2) -o')==git('show',BASE+':'+name).decode()
   if name.startswith('src/'):
    assert project(name,raw.decode())==tokens(git('show',BASE+':'+name).decode()),(name,'original C tokens changed');proofs+=1
 assert set(changed)==CHANGED
 menu=(ROOT/'src/menus.c').read_text();assert menu.count('selector_font_begin(')==4 and menu.count('selector_font_end();')==8
 for name in ('gameplaySelect','episodeSelect','difficultySelect','timedBattleSelect'):
  start=menu.index('bool '+name+'(');end=menu.find('\nbool ',start+5);part=menu[start:end if end>=0 else len(menu)]
  assert part.index('JE_loadPic(')<part.index('selector_font_begin(')<part.index('draw_font_hv_shadow(VGAScreen2')
  assert part.index('selector_font_frame_end();')<part.index('fade_palette(colors, 10')
  assert re.search(r'fade_black\(10\);\s*selector_font_end\(\);',part)
  assert re.search(r'fade_black\(15\);\s*selector_font_end\(\);',part)
 assert 'selector_font_frame_begin(selectedIndex, menuItemsVisibleCount)' in menu
 ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'};tree=ET.parse(ROOT/'visualc/opentyrian.vcxproj')
 files=[x.attrib['Include'] for x in tree.findall('.//m:ClCompile',ns) if 'Include'in x.attrib]
 assert len(files)==len(set(files)) and {Path(x.replace('\\','/')).name for x in files}=={x.name for x in (ROOT/'src').glob('*.c')}
 report={'result':'PASS','baseline':BASE,'portable_parent':PREGAME['PORTABLE']['BASE'],'source_token_projections':proofs,'documentation_only_exceptions':sorted(DOCUMENTATION_ONLY),'changed_existing_files':sorted(changed),'unchanged_prior_files':unchanged,'unchanged_asset_bytes':assets,'all_four_menu_input_state_draw_fade_tokens_preserved':True,'windows':'project inventory verified; no Windows runtime','game_runs':False}
 if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
