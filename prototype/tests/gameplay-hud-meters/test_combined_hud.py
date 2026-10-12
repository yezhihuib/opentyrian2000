#!/usr/bin/env python3
"""Simultaneous HUF/HUM source oracle and exact pre-meter HUF no-HUM parity."""
import argparse,ast,importlib.util,os,shutil,struct,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];FONT=HERE.parent/'gameplay-hud-font'
BASE='280e100a7204c907709a04f4186ec3b72d5542f2'
sys.path.insert(0,str(HERE.parent/'gameplay-hud'))
from test_renderer import extract,fnv,INDICATOR_FUNCTIONS,FIXED_FUNCTIONS
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
huf=module('huf_fixture',FONT/'fixtures.py');hum=module('hum_fixture',HERE/'test_renderer.py')
def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');a=p.parse_args()
 # Font implementation/source hooks must be byte-exact to the selected HUF base.
 for name in ('gameplay_hud_font.c','gameplay_hud_font.h','gameplay_hud_font_mirror.inc','fonthand.c','sprite.c','mainint.c'):
  assert (ROOT/'src'/name).read_bytes()==subprocess.check_output(['git','show',BASE+':src/'+name],cwd=ROOT)
 assignments={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse((FONT/'test_renderer.py').read_text()).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('base','writers')}
 with tempfile.TemporaryDirectory(prefix='combined-hud-') as t:
  d=Path(t);source_dir=d/'source';source_dir.mkdir();font_pins,_=huf.make(source_dir);meter_flags=hum.fixtures(source_dir)
  source=(source_dir/'meter-source.indices').read_bytes();(source_dir/'source.bin').write_bytes(source);font_pins['PIC3']=fnv(source)
  raw=bytearray((source_dir/'gameplay-hud-font-v1.hda').read_bytes());struct.pack_into('<Q',raw,48,font_pins['PIC3']);(source_dir/'gameplay-hud-font-v1.hda').write_bytes(raw)
  for variant in ('both','no-meter','no-font'):
   v=d/variant;v.mkdir()
   for name in ('source.bin','map.bin','glyphs.bin'):shutil.copyfile(source_dir/name,v/name)
   for name,enabled in [('gameplay-hud-font-v1.hda',variant!='no-font'),('gameplay-hud-meters-v2.hda',variant!='no-meter')]:
    if enabled:shutil.copyfile(source_dir/name,v/name)
  # Reuse unchanged test helper bodies; only omit their existing main entry.
  helper=(FONT/'test_renderer.c').read_text();assert helper.count('int main(int argc,char **argv)')==1
  (d/'huf_suite.inc').write_text(helper.split('int main(int argc,char **argv)')[0])
  results={}
  for variant in ('baseline','candidate'):
   src=subprocess.check_output(['git','show',BASE+':src/render_mirror.c'],cwd=ROOT,text=True) if variant=='baseline' else (ROOT/'src/render_mirror.c').read_text()
   names=['palette_rgb','upscale','render_mirror_unsupported']+FIXED_FUNCTIONS+INDICATOR_FUNCTIONS+assignments['base']+assignments['writers']
   if variant=='candidate':names+=['render_mirror_hud_meter_begin','render_mirror_hud_meter_end']
   parts=[(FONT/'writer_scaffold.inc').read_text()]+[extract(src,n) for n in names]
   parts+=[extract((ROOT/'src/sprite.c').read_text(),n) for n in ('blit_sprite','blit_sprite_hv_unsafe','blit_sprite_dark')]
   parts+=[extract((ROOT/'src/fonthand.c').read_text(),n) for n in ('JE_outText','JE_textShade')]
   parts+=[extract((ROOT/'src/mainint.c').read_text(),'JE_drawTextWindow')];(d/'production.inc').write_text('\n'.join(parts))
   cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Wno-unused-function','-Wno-misleading-indentation','-I'+str(d),'-I'+str(FONT),'-I'+str(ROOT/'src')]+huf.flags(font_pins)+meter_flags
   if variant=='baseline':cmd+=['-DCOMBINED_BASELINE']
   if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
   cmd+=[str(HERE/'test_combined_hud.c')]+[str(ROOT/'src'/n) for n in ('gameplay_hud.c','gameplay_hud_components.c','gameplay_hud_meters.c','gameplay_hud_indicators.c','gameplay_hud_fixed_text.c','gameplay_hud_font.c')]+['-o',str(d/variant)]
   subprocess.run(cmd,check=True);env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
   results[variant]=subprocess.check_output([str(d/variant),str(d),'parity'],text=True,timeout=300,env=env);print(variant+': '+results[variant].strip())
   if variant=='candidate':subprocess.run([str(d/variant),str(d),'combined'],check=True,timeout=300,env=env)
  assert results['baseline']==results['candidate']
 print('PASS exact280e100 active HUF1/no-HUM2 indexed/RGB/hidden-owner/cache/fade parity, unchanged HUF implementation and actual source writers; no game run.')
if __name__=='__main__':main()
