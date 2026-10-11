"""Pixel/ownership oracle for actual layer3 NORMAL row and original indexed writes."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from importlib.machinery import SourceFileLoader

HERE=Path(__file__).resolve().parent
helper=SourceFileLoader('gray_binder',str(HERE/'test-layer3-gray-binder.py')).load_module()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,default=HERE.parents[1])
p.add_argument('--report',type=Path)
a=p.parse_args()
sources={n:(a.source/'src'/n).read_text() for n in ['render_mirror.c','backgrnd.c']}
s=sources['render_mirror.c']
t=Path(tempfile.mkdtemp(prefix='layer3-gray-alpha-'))
patterns=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'static Asset assets\[\d+\];',r'static struct \{const Uint8 \*data;unsigned int id;\} terrain_sources\[\d+\];']
(t/'production-types.inc').write_text('\n'.join(re.search(q,s,re.S).group() for q in patterns))
names=['blend_rgba','cloud_asset','darken_rgba','draw_asset_filtered','draw_asset','read_asset','scene_asset',
       'render_mirror_map_begin','cloud_terrain_slot','ground_terrain_slot','plateau_terrain_slot','underlay_terrain_slot',
       'road_terrain_slot','terrain_holes_slot','stone_foundation_slot','layer3_gray_slot','render_mirror_bind_terrain',
       'render_mirror_terrain_row','render_mirror_pixel','render_mirror_terrain_pixel']
(t/'production-helpers.inc').write_text('\n'.join(helper.extract(s,n) for n in names)+'\n'+helper.extract(sources['backgrnd.c'],'blit_background_row'))
command=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(t),str(HERE/'test-layer3-gray-alpha.c'),'-o',str(t/'test')]
build=subprocess.run(command,text=True,capture_output=True);(t/'build.log').write_text(build.stdout+build.stderr)
if build.returncode:raise RuntimeError(build.stderr)
run=subprocess.run([str(t/'test')],text=True,capture_output=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'))
print(run.stdout,end='');print(run.stderr,end='')
report={'status':'passed' if run.returncode==0 else 'failed','sanitize':'address,undefined','source_sha256':{n:hashlib.sha256(v.encode()).hexdigest() for n,v in sources.items()},'source_stable':all(v==(a.source/'src'/n).read_text() for n,v in sources.items()),'command':command,'work':str(t),'stdout':run.stdout,'stderr':run.stderr,'exit_code':run.returncode,'scope':'All18 IDs; actual binder/row/compositor/original NORMAL indexed blitter and per-pixel callbacks,2x/4x/8x, binary/fractional alpha, clipped and null/partial rows, exact RGBA/ownership/indexed writes, missing/invalid fallback, non-NORMAL styles skip without draw/restore. Pure synthetic fixture input; no game/art/capture.'}
out=a.report or t/'result.json';out.write_text(json.dumps(report,indent=2)+'\n');print('Report:',out)
run.check_returncode();assert report['source_stable']
