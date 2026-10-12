#!/usr/bin/env python3
"""HUL1 production renderer oracle, synthetic original data and authored RGBA."""
from pathlib import Path
import argparse,importlib.util,os,struct,subprocess,sys,tempfile,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'gameplay-hud'))
from test_renderer import extract,fnv,INDICATOR_FUNCTIONS,FIXED_FUNCTIONS
spec=importlib.util.spec_from_file_location('huc_fixture',HERE.parent/'gameplay-hud-components/test_renderer.py');huc=importlib.util.module_from_spec(spec);spec.loader.exec_module(huc)
RIM={44:[285,286,289,292,293,294,302,303,306,309,310,311],45:[293,310],49:[302],50:[292,293,303,309,310],51:[286,293,294,302,303,310]}
OVERLAP={(x,y) for y in range(44,52) for x in range(295,302)}|{(x,y) for y,xs in RIM.items() for x in xs}
assert len(OVERLAP)==82

def fixtures(path):
 huc.fixtures(path);source=bytearray((path/'component-source.indices').read_bytes())
 for x,count in [(285,6),(296,5)]:
  for y in range(138,138+count*6,6):
   for yy in range(y-1,y+6):
    for xx in range(x-1,x+6):
     if not (x<=xx<x+5 and y<=yy<y+5):source[yy*320+xx]=0
 local={10*(y-44)+(x-(285 if x<295 else 302)) for y,xs in RIM.items() for x in xs}
 modes=[bytes(7 if i in local else 31+k*40+i%7 for i in range(80)) for k in range(2)]
 states=[]
 for mode in range(2):
  out=bytearray(source[y*320+x] for y in range(44,52) for x in range(285,312))
  for side in range(2):
   for y in range(8):out[y*27+17*side:y*27+17*side+10]=modes[mode^side][y*10:y*10+10]
  states.append(out)
 top=bytes(source[y*320+x] for y in range(4,7) for x in range(269,276))
 palette=bytes(c for i in range(256) for c in (i*5%256,i*11%256,i*17%256))
 values=dict(PIC3=fnv(source),PALETTE=fnv(palette),TOP=fnv(top),MODE1=fnv(states[0]),MODE2=fnv(states[1]),OPTION18=fnv(modes[0]),OPTION19=fnv(modes[1]))
 payload=bytearray()
 for tile,(w,h) in enumerate(((28,12),(108,32),(108,32))):
  for y in range(h):
   for x in range(w):payload+=bytes(((x*3+tile*37+19)%256,(y*7+tile*61+83)%256,(x+y*3+tile*51+3)%256,255))
 header=struct.pack('<4s7I6Q',b'HUL1',1,4,28,12,108,32,len(payload),*[values[k] for k in ('PIC3','PALETTE','TOP','MODE1','MODE2')],fnv(payload))
 (path/'gameplay-hud-indicators-v1.hda').write_bytes(header+payload)
 (path/'indicator-source.indices').write_bytes(source);(path/'indicator-modes.indices').write_bytes(b''.join(modes))
 data=bytearray((path/'gameplay-hud-components-v1.hda').read_bytes());struct.pack_into('<Q',data,32,fnv(source));(path/'gameplay-hud-components-v1.hda').write_bytes(data)
 data=bytearray((path/'gameplay-hud-v1.hda').read_bytes());mask=data[64:64064]
 for x,y in OVERLAP:mask[y*320+x]=255
 data[64:64064]=mask
 for y in range(200):
  for x in range(320):
   for sy in range(4):
    for sx in range(4):data[64064+4*((y*4+sy)*1280+x*4+sx)+3]=mask[y*320+x]
 struct.pack_into('<3Q',data,36,fnv(source),fnv(mask),fnv(data[64064:]));(path/'gameplay-hud-v1.hda').write_bytes(data)
 for name in ('missing','corrupt','no-frame'):
  d=path/name;d.mkdir()
  for file in path.iterdir():
   if file.is_file() and not (name=='no-frame' and file.name=='gameplay-hud-v1.hda') and not (name=='missing' and file.name=='gameplay-hud-indicators-v1.hda'):shutil.copyfile(file,d/file.name)
  if name=='corrupt':
   file=d/'gameplay-hud-indicators-v1.hda';data=bytearray(file.read_bytes());data[0]^=1;file.write_bytes(data)
 return ['-DHUD_INDICATORS_'+k+'_FNV=UINT64_C(0x%016x)'%v for k,v in values.items()]

def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');a=p.parse_args()
 source=(ROOT/'src/render_mirror.c').read_text()
 # Same real bodies as both existing HUD oracles, with no alternate renderer.
 huc_names=['components_owned','components_source_matches','components_cached_indices_match','components_clear_cached','components_reset','components_check_mode','components_start','components_begin','render_mirror_hud_shield_wiped','render_mirror_hud_shield_drawn','components_compose','hud_source_matches','hud_cached_indices_match','hud_clear_cached','hud_frame_reset','render_mirror_hud_reset','render_mirror_hud_shutdown','hud_runtime_compatible','hud_check_mode','render_mirror_hud_start','render_mirror_hud_suspend','hud_begin','hud_compose','render_mirror_begin','render_mirror_finish','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','render_mirror_release_texture']
 with tempfile.TemporaryDirectory(prefix='hul-renderer-') as directory:
  d=Path(directory);flags=fixtures(d)
  (d/'production.inc').write_text('\n'.join(extract(source,n) for n in ['palette_rgb','upscale','render_mirror_unsupported']+FIXED_FUNCTIONS+INDICATOR_FUNCTIONS+huc_names))
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Wno-unused-function','-Wno-misleading-indentation','-I'+str(d),'-I'+str(ROOT/'src')]+flags+[str(HERE/'test_renderer.c')]+[str(ROOT/'src'/n) for n in ('gameplay_hud.c','gameplay_hud_components.c','gameplay_hud_indicators.c','gameplay_hud_fixed_text.c')]+['-o',str(d/'test')]
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  subprocess.run(cmd,check=True);subprocess.run([str(d/'test'),str(d)],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
if __name__=='__main__':main()
