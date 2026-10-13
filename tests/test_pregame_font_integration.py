#!/usr/bin/env python3
"""Two-context source boundary, unchanged art and exactly-once C inventory."""
from pathlib import Path
import argparse,hashlib,json,subprocess,xml.etree.ElementTree as ET
from pregame_font_projection import ROOT,BASE,EDITS,ADDED_SOURCE,git,project,verify
p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args()
production=verify();unchanged=0;asset_bytes=0;changed=[];negative=0
# A frozen exact reverse projection admits only the finite observer edits.
for row in git('ls-tree','-rz',BASE).split(b'\0'):
 if not row:continue
 meta,name=row.split(b'\t',1);name=name.decode();mode,kind,blob=meta.decode().split();path=ROOT/name
 assert kind=='blob' and path.is_file() and not path.is_symlink(),name
 raw=path.read_bytes();same=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob
 if same:
  unchanged+=1
  if name.startswith('assets/'):asset_bytes+=len(raw)
 else:
  assert name in EDITS,name;project(name,raw);changed.append(name)
assert set(changed)==set(EDITS)
for name in EDITS:
 raw=(ROOT/name).read_bytes()
 for offset in {0,len(raw)//2,len(raw)-1}:
  try:project(name,raw[:offset]+bytes([raw[offset]^1])+raw[offset+1:])
  except AssertionError:negative+=1
  else:raise AssertionError((name,'unrelated mutation admitted',offset))
menu=(ROOT/'src/game_menu.c').read_text()
assert menu.count('pregame_font_begin(')==1
assert '!twoPlayerMode && !onePlayerAction && !isNetworkGame && !superTyrian && superArcadeMode == SA_NONE && !constantPlay && !timedBattleMode' in menu
assert menu.index('pregame_font_begin(')>menu.index('memcpy(VGAScreen->pixels, VGAScreen2->pixels, VGAScreen->pitch * VGAScreen->h);')
assert 'fade_black(10);\n\t\t\t\t\tpregame_font_end();\n\t\t\t\t\tJE_helpSystem(2);' in menu
for name in ('src/fonthand.c','src/selector_font.c','src/selector_font_output.c','src/settings_font.c','src/load_font.c','src/menus.c','src/title_menu_font.inc','src/player.c','src/config.c','src/tyrian2.c'):
 assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'};tree=ET.parse(ROOT/'visualc/opentyrian.vcxproj')
c=[x.attrib['Include']for x in tree.findall('.//m:ClCompile',ns)if 'Include'in x.attrib]
h=[x.attrib['Include']for x in tree.findall('.//m:ClInclude',ns)if 'Include'in x.attrib]
assert len(c)==len(set(c)) and c.count('..\\src\\pregame_font.c')==1 and h.count('..\\src\\pregame_font.h')==1
assert {Path(x.replace('\\','/')).name for x in c}=={x.name for x in (ROOT/'src').glob('*.c')}
report={'result':'PASS','base':BASE,'exact_existing_file_projections':sorted(changed),'unchanged_prior_files':unchanged,'unchanged_asset_bytes':asset_bytes,'mutation_rejections':negative,'production_delta':sorted(production),'two_context_only':True,'original_draw_input_state_save_sound_tokens_and_bytes_preserved':True,'selector_output_and_existing_fonts_exact':True,'windows':'source inventory only; no Windows build/runtime claim','game_runs':False}
if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
