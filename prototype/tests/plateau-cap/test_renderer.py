#!/usr/bin/env python3
"""Extract actual Layer1/cap wiring and test finite gates with strict mocks."""
from pathlib import Path
import argparse,hashlib,json,os,re,shlex,subprocess
p=argparse.ArgumentParser();p.add_argument('--src',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--sanitize',action='store_true');a=p.parse_args()
src=a.src.resolve();out=a.output.resolve()
if a.output.is_symlink() or out==src or src in out.parents or out in src.parents:raise SystemExit('output must be outside source')
out.mkdir(parents=True,exist_ok=False);here=Path(__file__).resolve().parent
source=(src/'render_mirror.c').read_text()
def extract(name):
    m=re.search(r'^.*\b'+name+r'\([^\n]*\)\s*\{',source,re.M);assert m,name
    start=source.index('{',m.start());depth=1;end=start+1
    while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[m.start():end]+'\n'
functions=['cloud_terrain_slot','ground_terrain_slot','plateau_terrain_slot','underlay_terrain_slot','road_terrain_slot','terrain_holes_slot','stone_foundation_slot','layer3_gray_slot','layer3_purple_slot','grass_sand_slot','render_mirror_bind_terrain','plateau_cap_selected_source','render_mirror_ground101_layer1','render_mirror_terrain_row']
(out/'wiring.inc').write_text('\n'.join(extract(n) for n in functions))
# Verify no additional cap scope was slipped into actor or generic rendering.
assert 'part,0,NULL,NULL)' in extract('draw_asset')
assert '&quadrant,(Uint8)filter,material,NULL)' in extract('render_mirror_enemy_tile')
body=extract('draw_asset_filtered')
assert body.index('ground101_select(')<body.index('plateau_cap_select(')<body.index('enemy_filter_rgba(')<body.index('blend_rgba(*p,src,')
assert 'int dx=x*d+ax,dy=y*d+ay;' in body and 'if(dx<0||dy<0||dx>=canvas->w||dy>=canvas->h)continue;' in body
cc=shlex.split(os.environ.get('CC','cc'));flags=['-std=c11','-O2','-Wall','-Wextra','-Werror','-I'+str(src),'-I'+str(out)]
if a.sanitize:flags+=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
exe=out/'test-renderer';subprocess.run(cc+flags+[str(here/'test_renderer.c'),'-o',str(exe)],check=True)
env=dict(os.environ);env.setdefault('ASAN_OPTIONS','detect_leaks=0:halt_on_error=1');env.setdefault('UBSAN_OPTIONS','halt_on_error=1')
scenarios=['valid','lower-missing','lower-mismatch','preflight-failure','cap-missing','cap-mismatch','density4','wrong-surface','inactive','wrong-map','missing-assets','invalid-assets','original-reference','no-assets','wrong-scene-bits','already-rejected']
results={}
for case in scenarios:
    r=subprocess.run([str(exe),case],text=True,capture_output=True,env=env)
    assert r.returncode==0,(case,r.stdout,r.stderr)
    results[case]=r.stdout
(out/'renderer-checks.json').write_text(json.dumps({'status':'passed','renderer_sha256':hashlib.sha256(source.encode()).hexdigest(),'scenarios':results,'actor_generic_caps_disabled':True,'composition_order_exact':True},indent=2)+'\n')
print('PASS',len(results),'actual renderer gating scenarios; selected shape checks; finite IDs/layers/styles; actor/generic cap off; lower->cap->filter ordering')
