#!/usr/bin/env python3
"""Synthetic original-index/RGB/cache parity against the exact published base."""
import argparse,importlib.util,os,re,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE='56efa26181cd342347f8645f1c9adefc1e45d4ef'
sys.path.insert(0,str(HERE.parent/'gameplay-hud'));from test_renderer import extract,INDICATOR_FUNCTIONS,FIXED_FUNCTIONS
spec=importlib.util.spec_from_file_location('hut_fixture',HERE.parent/'gameplay-hud-typography/test_renderer.py');hut=importlib.util.module_from_spec(spec);spec.loader.exec_module(hut)
def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');a=p.parse_args()
 names=['components_owned','components_source_matches','components_cached_indices_match','components_clear_cached','components_reset','components_check_mode','components_start','components_begin','render_mirror_hud_shield_wiped','render_mirror_hud_shield_drawn','components_compose','hud_source_matches','hud_cached_indices_match','hud_clear_cached','hud_frame_reset','render_mirror_hud_reset','render_mirror_hud_shutdown','hud_runtime_compatible','hud_check_mode','render_mirror_hud_start','render_mirror_hud_suspend','hud_begin','hud_compose','render_mirror_begin','render_mirror_finish','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','render_mirror_release_texture']
 with tempfile.TemporaryDirectory(prefix='hum2-absent-') as t:
  d=Path(t);flags=hut.fixtures(d);results={}
  for variant in ('baseline','candidate'):
   source=subprocess.check_output(['git','show',BASE+':src/render_mirror.c'],cwd=ROOT,text=True) if variant=='baseline' else (ROOT/'src/render_mirror.c').read_text()
   (d/'production.inc').write_text('\n'.join(extract(source,n) for n in ['palette_rgb','upscale','render_mirror_unsupported']+FIXED_FUNCTIONS+INDICATOR_FUNCTIONS+names))
   cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Wno-unused-function','-Wno-misleading-indentation','-I'+str(d),'-I'+str(ROOT/'src')]+flags+[str(HERE/'test_no_meters.c')]+[str(ROOT/'src'/n) for n in ('gameplay_hud.c','gameplay_hud_components.c','gameplay_hud_meters.c','gameplay_hud_indicators.c','gameplay_hud_fixed_text.c','gameplay_hud_font.c')]+['-o',str(d/variant)]
   if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
   subprocess.run(cmd,check=True);results[variant]=subprocess.check_output([str(d/variant),str(d)],text=True,timeout=180,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'));print(variant+': '+results[variant].strip())
  assert results['baseline']==results['candidate']
 print('PASS exact56efa261 no-HUM2 indexed/RGB/state/fingerprint/ownership/cache/fade synthetic parity at densities4+8; no game run.')
if __name__=='__main__':main()
