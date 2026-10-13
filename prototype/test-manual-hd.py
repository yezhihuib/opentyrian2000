#!/usr/bin/env python3
"""Build real-source units, never run the game. Requires a prior Linux make build."""
import argparse, hashlib, json, os, re, shlex, shutil, subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=a.out.resolve();assert not out.exists();out.mkdir(parents=True)
base='2b36d6cae801881e31a5791aa2864b0b2d08614c'
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(cmd,**kw):
    r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,**kw)
    if r.returncode:raise AssertionError(' '.join(map(str,cmd))+'\n'+r.stdout+r.stderr)
    return r.stdout+r.stderr
# Exact-file preservation for all unapproved production files and every asset.
allowed={'src/game_probe.c','src/game_probe.h','src/opentyr.c','src/params.c','src/render_mirror.c'}
changed=run(['git','-C',root,'diff',base,'--name-only','--','src','assets']).splitlines()
assert set(changed)<=allowed,changed
baseline=lambda f:subprocess.check_output(['git','-C',root,'show',base+':'+f]).decode()
def function(source,name):
    m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',source,re.M);assert m,name
    pos=source.index('{',m.start())+1;depth=1
    while depth:depth+=(source[pos]=='{')-(source[pos]=='}');pos+=1
    return source[m.start():pos]
probe=(root/'src/game_probe.c').read_text();mirror=(root/'src/render_mirror.c').read_text()
for name in ['game_probe_start','game_probe_level','game_probe_input','game_probe_end_tick']:
    assert function(probe,name)==function(baseline('src/game_probe.c'),name),name
# All rendering/art/load/fallback helpers except the finite activation sites stay byte-identical.
modified={'render_mirror_hud_reset','render_mirror_hud_start','render_mirror_begin','render_mirror_player_pose','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','render_mirror_ground101_layer1'}
old=baseline('src/render_mirror.c');names=re.findall(r'^(?:static\s+)?(?:bool|void|int|Uint32|Asset\s*\*)\s+(\w+)\([^;{}]*\)\s*\{',old,re.M)
# The later Data fix admits exactly its original warm glyph. Keep the original
# manual-mode preservation gate exact after projecting only that bounded edit.
data_addition=' /* The original Data pickup is fixed sprite266 with a warm0x70 glyph,\n  * unlike the blue/gray cash values. Keep it under the same source/Talon/\n  * monotone-ramp checks instead of restoring the connected HD scene. */\n bool data=index==266&&hue==0x70;\n'
assert mirror.count(data_addition)==1
preserved_mirror=mirror.replace(data_addition,'').replace('||(value&&(hue==0x80||hue==0x90))||data;', '||(value&&(hue==0x80||hue==0x90));')
for name in names:
    if name not in modified:assert function(old,name)==function(preserved_mirror,name),name
opentyr=(root/'src/opentyr.c').read_text();start=opentyr.index('\tif (manual_hd_enabled &&');end=opentyr.index('\n\tif (!override_xmas)',start)
validation=opentyr[start:end] # Includes exact existing startup release/network validation.
only_manual=opentyr[start:opentyr.index('\tif (startup_logos_configured())',start)]
assert opentyr.replace(only_manual,'',1)==baseline('src/opentyr.c')
assert '-DGROUND101_MATERIAL_TRACE' not in (root/'Makefile').read_text()
assert 'GROUND101_MATERIAL_TRACE' not in (root/'visualc/opentyrian.vcxproj').read_text()
cc=shlex.split(os.environ.get('CC','cc'));cflags=shlex.split(run(['pkg-config','--cflags','sdl2','SDL2_net']))
libs=shlex.split(run(['pkg-config','--libs','sdl2','SDL2_net']))+['-lm']
common=cc+['-std=c99','-DTARGET_UNIX','-DWITH_NETWORK','-DNDEBUG','-O1','-g','-I'+str(root/'src')]+cflags
# Existing engine objects are linked only as dependencies; original main is renamed and never called.
run(common+['-Dmain=unused_original_main','-c',root/'src/opentyr.c','-o',out/'opentyr.o'])
for kind in ['render','probe']:
    run(common+['-UNDEBUG','-c',root/f'prototype/test-manual-hd-{kind}.c','-o',out/f'{kind}.o'])
driver='''#include "game_probe.h"
#include "asset_debug.h"
#include "params.h"
#include "network.h"
#include "varz.h"
#include "startup_logos.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int manual_render_test(const char *,int,int);int manual_probe_test(void);
int main(int argc,char **argv){
 if(argc>1&&!strcmp(argv[1],"unit-render"))return manual_render_test(argv[2],atoi(argv[3]),atoi(argv[4]));
 if(argc>1&&!strcmp(argv[1],"unit-probe"))return manual_probe_test();
 game_probe_parse(&argc,argv);JE_paramCheck(argc,argv);
'''+validation+'''
 printf("RESULT %d %d %d %d %d %d %u %u %d %s\\n",manual_hd_enabled,game_probe_enabled,asset_debug_enabled,game_probe_density,game_probe_local_blend,game_probe_known_blend,game_probe_scene_assets,game_probe_tick,startup_logos_configured(),game_probe_assets?game_probe_assets:"-");return 0;}
'''
(out/'driver.c').write_text(driver)
objects=[str(f) for f in sorted((root/'obj').glob('*.o')) if f.stem not in ['opentyr','render_mirror','game_probe']]+[str(out/f'{k}.o') for k in ['opentyr','render','probe']]
for kind,extra in [('release',[]),('debug',['-UNDEBUG'])]:
    run(common+extra+[out/'driver.c']+objects+libs+['-Wl,--wrap=forest13_policy_check','-o',out/kind])
results=[]
def check(args,expected=0,contains=None,binary='release'):
    d=out/('case-%03d'%len(results));d.mkdir()
    r=subprocess.run([str(out/binary)]+args,cwd=d,capture_output=True,text=True)
    (d/'result.txt').write_text(r.stdout+r.stderr)
    assert r.returncode==expected,(args,r.returncode,r.stdout,r.stderr)
    if contains:assert contains in r.stdout+r.stderr,(args,contains,r.stdout,r.stderr)
    assert sorted(f.name for f in d.iterdir())==['result.txt'],list(d.iterdir())
    results.append(dict(args=args,result='passed',exit=expected));return r.stdout
manual='--manual-hd-assets=/absolute/assets with spaces'
check([],contains='RESULT 0 0 0 1 0 0 0 0 0 -')
check([manual],contains='RESULT 1 0 0 8 1 1 3 0 0 /absolute/assets with spaces')
check(['--manual-hd-assets=relative/assets'],contains='RESULT 1 0 0 8 1 1 3 0 0 relative/assets')
check(['--manual-hd-assets='],2,'nonempty')
for flag in ['--render-test=8','--render-assets=x','--render-ticks=600','--render-scene=v1','--render-front-port=1','--render-no-capture','--render-unknown','--asset-debug=custom','--asset-debug-running','--asset-debug-unknown']:
    for args in [[manual,flag],[flag,manual]]:check(args,2,'cannot be combined')
for flag in ['--net=localhost','--record','--constant','--death','--loot','-nlocalhost','-r','-c','-k','-l','RECORD','CONSTANT','DEATH','LOOT','record','constant','death','loot']:
    for args in [[manual,flag],[flag,manual]]:check(args,2,'cannot be combined')
check([manual,'--startup-assets=/absolute/startup'],contains='RESULT 1 0 0 8 1 1 3 0 1')
check([manual,'--startup-assets=/absolute/startup'],2,'release/NDEBUG',binary='debug')
check(['--render-test=8','--render-assets=x'],contains='RESULT 0 1 0 8')
check(['--asset-debug=custom','--render-assets=x'],contains='RESULT 0 1 1 8')
check(['--render-assets=x'],contains='RESULT 0 0 0 1')
check(['unit-probe'],contains='probe regression units passed')
pack=root/'assets/hd/packs/packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test'
# Small isolated fixtures: no HUD or material files. Missing HUD/material does not own scene eligibility.
fixture=out/'scene-only';fixture.mkdir()
for f in list(pack.glob('ship-*-8.hda'))+list(pack.glob('talon-bank-*-8.hda'))+[pack/'bullet-59-8.hda']:
    shutil.copy2(f,fixture/f.name)
check(['unit-render',str(fixture),'1','1'],contains='banking units passed')
check(['unit-render',str(out/'absent'),'0','0'],contains='banking units passed')
bad=out/'invalid';shutil.copytree(fixture,bad);(bad/'bullet-59-8.hda').write_bytes(b'BAD!');(bad/'talon-bank-1-8.hda').unlink()
check(['unit-render',str(bad),'0','0'],contains='banking units passed')
report={'status':'passed','base':base,'cases':len(results),'results':results,'unchanged_render_helpers':len(names)-len(modified),'source_sha256':{f:sha((root/f).read_bytes()) for f in sorted(allowed)},'scope':'Real-source units only. No game launch, native input or Windows runtime claim.'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
