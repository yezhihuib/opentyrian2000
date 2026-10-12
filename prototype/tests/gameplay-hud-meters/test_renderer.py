#!/usr/bin/env python3
"""Actual extracted compositor/lease/fade bodies with finite synthetic HUM2/HUC1."""
import argparse,importlib.util,os,struct,subprocess,sys,tempfile,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'gameplay-hud'));from test_renderer import extract,fnv,INDICATOR_FUNCTIONS,FIXED_FUNCTIONS
spec=importlib.util.spec_from_file_location('huc_fixture',HERE.parent/'gameplay-hud-components/test_renderer.py');huc=importlib.util.module_from_spec(spec);spec.loader.exec_module(huc)
BOXES=[(289,17,311,20),(289,38,311,41),(269,12,277,104),(307,137,316,195)]
def fixtures(d):
 huc.fixtures(d);source=bytearray((d/'component-source.indices').read_bytes())
 for l,t,r,b in BOXES:
  for y in range(t,b):source[320*y+l:320*y+r]=bytes(r-l)
 (d/'meter-source.indices').write_bytes(source)
 for name,off in [('gameplay-hud-v1.hda',36),('gameplay-hud-components-v1.hda',32)]:
  raw=bytearray((d/name).read_bytes());struct.pack_into('<Q',raw,off,fnv(source));(d/name).write_bytes(raw)
 rgba=bytes(c for i in range(176896//4) for c in (i*7%251,i*11%253,i*17%255,255))
 lookup=b''.join(struct.pack('<H',(i*17+11)%944) for i in range(222456));payload=rgba+lookup
 palette=bytes(c for i in range(256) for c in (i*5%256,i*11%256,i*17%256))
 pins=[fnv(source),fnv(palette),fnv(payload[:4224]),fnv(payload[4224:56064]),fnv(payload[56064:176896]),fnv(lookup),fnv(payload)]
 raw=struct.pack('<4s11I8Q',b'HUM2',2,112,4,320,200,4224,51840,120832,444912,944,222456,*pins,0)+payload
 (d/'gameplay-hud-meters-v2.hda').write_bytes(raw)
 for variant in ('meter-only','no-meter','bad-meter','no-words'):
  v=d/variant;v.mkdir()
  for f in list(d.iterdir()):
   if not f.is_file():continue
   if variant=='meter-only' and f.suffix=='.hda' and f.name!='gameplay-hud-meters-v2.hda':continue
   if variant=='no-meter' and f.name=='gameplay-hud-meters-v2.hda':continue
   if variant=='no-words' and f.name=='gameplay-hud-components-v1.hda':continue
   shutil.copyfile(f,v/f.name)
  if variant=='bad-meter':r=bytearray(raw);r[0]^=1;(v/'gameplay-hud-meters-v2.hda').write_bytes(r)
 return ['-DHUD_METERS_'+k+'_FNV=UINT64_C(0x%016x)'%v for k,v in zip(('PIC','PALETTE','FIRE','ARMOR','ROWS','LOOKUP','PAYLOAD'),pins)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');a=p.parse_args();source=(ROOT/'src/render_mirror.c').read_text()
 names=['components_owned','components_source_matches','components_cached_indices_match','components_clear_cached','components_reset','components_check_mode','components_start','components_begin','render_mirror_hud_shield_wiped','render_mirror_hud_shield_drawn','render_mirror_hud_meter_begin','render_mirror_hud_meter_end','components_compose','hud_source_matches','hud_cached_indices_match','hud_clear_cached','hud_frame_reset','render_mirror_hud_reset','render_mirror_hud_shutdown','hud_runtime_compatible','hud_check_mode','render_mirror_hud_start','render_mirror_hud_suspend','hud_begin','hud_compose','render_mirror_begin','render_mirror_finish','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','render_mirror_release_texture']
 with tempfile.TemporaryDirectory(prefix='hum2-renderer-') as temp:
  d=Path(temp);flags=fixtures(d);(d/'production.inc').write_text('\n'.join(extract(source,n) for n in ['palette_rgb','upscale','render_mirror_unsupported']+FIXED_FUNCTIONS+INDICATOR_FUNCTIONS+names))
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Wno-unused-function','-Wno-misleading-indentation','-I'+str(d),'-I'+str(ROOT/'src')]+flags+[str(HERE/'test_renderer.c')]+[str(ROOT/'src'/n) for n in ('gameplay_hud.c','gameplay_hud_components.c','gameplay_hud_meters.c','gameplay_hud_indicators.c','gameplay_hud_fixed_text.c','gameplay_hud_font.c')]+['-o',str(d/'test')]
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
  subprocess.run(cmd,check=True);subprocess.run([str(d/'test'),str(d)],check=True,timeout=240,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
if __name__=='__main__':main()
