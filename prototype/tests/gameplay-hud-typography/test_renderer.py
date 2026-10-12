#!/usr/bin/env python3
"""HUT1 actual production functions; synthetic assets and source only."""
from pathlib import Path
import argparse,importlib.util,os,struct,subprocess,sys,tempfile,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'gameplay-hud'))
from test_renderer import extract,fnv,INDICATOR_FUNCTIONS,FIXED_FUNCTIONS
spec=importlib.util.spec_from_file_location('hul_fixture',HERE.parent/'gameplay-hud-indicators/test_renderer.py');hul=importlib.util.module_from_spec(spec);spec.loader.exec_module(hul)
sys.path.insert(0,str(HERE));from test_fixed_contract import HEADER,PAYLOAD,select

def fixtures(d):
 flags=hul.fixtures(d);source=(d/'indicator-source.indices').read_bytes();palette=bytes(v for i in range(256) for v in (i*5%256,i*11%256,i*17%256))
 rgba=bytes(c for i in range(PAYLOAD//4) for c in (i*7%256,i//13%256,i//37%256,255));guards=[fnv(source),fnv(palette),fnv(select(source))]
 (d/'gameplay-hud-fixed-text-v1.hda').write_bytes(HEADER.pack(b'HUT1',1,4,12,370,PAYLOAD,1,0,*guards,fnv(rgba))+rgba)
 for name in ('no-fixed','bad-fixed','fixed-only'):
  p=d/name;p.mkdir()
  for f in d.iterdir():
   if f.is_file() and not(name=='no-fixed' and f.name=='gameplay-hud-fixed-text-v1.hda') and not(name=='fixed-only' and f.suffix=='.hda' and f.name!='gameplay-hud-fixed-text-v1.hda'):shutil.copyfile(f,p/f.name)
  if name=='bad-fixed':f=p/'gameplay-hud-fixed-text-v1.hda';raw=bytearray(f.read_bytes());raw[0]^=1;f.write_bytes(raw)
 return flags+['-DHUD_FIXED_'+k+'_FNV=UINT64_C(0x%016x)'%v for k,v in zip(('PIC3','PALETTE','SOURCE'),guards)]

def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');a=p.parse_args();source=(ROOT/'src/render_mirror.c').read_text()
 names=['components_owned','components_source_matches','components_cached_indices_match','components_clear_cached','components_reset','components_check_mode','components_start','components_begin','render_mirror_hud_shield_wiped','render_mirror_hud_shield_drawn','components_compose','hud_source_matches','hud_cached_indices_match','hud_clear_cached','hud_frame_reset','render_mirror_hud_reset','render_mirror_hud_shutdown','hud_runtime_compatible','hud_check_mode','render_mirror_hud_start','render_mirror_hud_suspend','hud_begin','hud_compose','render_mirror_begin','render_mirror_finish','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','render_mirror_release_texture']
 with tempfile.TemporaryDirectory(prefix='hut-renderer-') as tmp:
  d=Path(tmp);flags=fixtures(d);(d/'production.inc').write_text('\n'.join(extract(source,n) for n in ['palette_rgb','upscale','render_mirror_unsupported']+FIXED_FUNCTIONS+INDICATOR_FUNCTIONS+names))
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Wno-unused-function','-Wno-misleading-indentation','-I'+str(d),'-I'+str(ROOT/'src')]+flags+[str(HERE/'test_renderer.c')]+[str(ROOT/'src'/n) for n in ('gameplay_hud.c','gameplay_hud_components.c','gameplay_hud_meters.c','gameplay_hud_indicators.c','gameplay_hud_fixed_text.c','gameplay_hud_font.c')]+['-o',str(d/'test')]
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  subprocess.run(cmd,check=True);subprocess.run([str(d/'test'),str(d)],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
if __name__=='__main__':main()
