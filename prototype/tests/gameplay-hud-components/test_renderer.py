#!/usr/bin/env python3
"""Synthetic production component compositor/lease/fade oracle."""
from pathlib import Path
import argparse,os,struct,subprocess,sys,tempfile,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'gameplay-hud'))
from test_renderer import extract,fnv,fixture,INDICATOR_FUNCTIONS,FIXED_FUNCTIONS
BOXES=[(285,5,24),(285,11,14),(285,26,18),(285,32,14)]

def fixtures(path):
 source=bytearray([7])*64000
 for y in range(137,195):source[y*320+270:y*320+279]=bytes(9)
 for x,y,w in BOXES:
  for yy in range(y,y+5):
   for xx in range(x,x+w):source[yy*320+xx]=0 if (xx+yy)%2 else 7
 labels=bytearray()
 for box,(_,_,w) in enumerate(BOXES):
  for y in range(20):
   for x in range(w*4):labels+=bytes((20+box*30,x+40,y+70,255))
 bands=bytearray()
 for role in range(14):
  for y in range(8):
   for x in range(36):bands+=bytes((10+role,x+60,y+130,255))
 palette=bytes(c for i in range(256) for c in (i*5%256,i*11%256,i*17%256))
 header=struct.pack('<4s7I4Q',b'HUC1',1,4,4,22400,14,36,8,fnv(source),fnv(labels),fnv(bands),fnv(palette))
 (path/'gameplay-hud-components-v1.hda').write_bytes(header+labels+bands)
 (path/'component-source.indices').write_bytes(source)
 # Independent existing sparse static HUD resource sharing this runtime PIC3.
 fixture(path);old=bytearray((path/'gameplay-hud-v1.hda').read_bytes());struct.pack_into('<Q',old,36,fnv(source));(path/'gameplay-hud-v1.hda').write_bytes(old)

def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');a=p.parse_args()
 source=(ROOT/'src/render_mirror.c').read_text()
 names=['palette_rgb','upscale','render_mirror_unsupported','components_owned','components_source_matches','components_cached_indices_match','components_clear_cached','components_reset','components_check_mode','components_start','components_begin','render_mirror_hud_shield_wiped','render_mirror_hud_shield_drawn','components_compose','hud_source_matches','hud_cached_indices_match','hud_clear_cached','hud_frame_reset','render_mirror_hud_reset','render_mirror_hud_shutdown','hud_sprite_decode','hud_runtime_compatible','hud_check_mode','render_mirror_hud_start','render_mirror_hud_suspend','hud_begin','hud_compose','render_mirror_begin','render_mirror_finish','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','render_mirror_release_texture']
 with tempfile.TemporaryDirectory(prefix='huc-renderer-') as temp:
  temp=Path(temp);fixtures(temp)
  for variant in ('missing','corrupt'):
   d=temp/variant;d.mkdir()
   for name in ('gameplay-hud-v1.hda','component-source.indices'):shutil.copyfile(temp/name,d/name)
   if variant=='corrupt':
    data=bytearray((temp/'gameplay-hud-components-v1.hda').read_bytes());data[0]^=1;(d/'gameplay-hud-components-v1.hda').write_bytes(data)
  (temp/'production.inc').write_text('\n'.join(extract(source,n) for n in names[:3]+FIXED_FUNCTIONS+INDICATOR_FUNCTIONS+[v for v in names[3:] if v!='hud_sprite_decode']))
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Wno-unused-function','-Wno-misleading-indentation','-I'+str(temp),'-I'+str(ROOT/'src'),str(HERE/'test_renderer.c'),str(ROOT/'src/gameplay_hud.c'),str(ROOT/'src/gameplay_hud_components.c'),str(ROOT/'src/gameplay_hud_meters.c'),str(ROOT/'src/gameplay_hud_indicators.c'),str(ROOT/'src/gameplay_hud_fixed_text.c'),str(ROOT/'src/gameplay_hud_font.c'),'-o',str(temp/'test')]
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  subprocess.run(cmd,check=True);subprocess.run([str(temp/'test'),str(temp)],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
if __name__=='__main__':main()
