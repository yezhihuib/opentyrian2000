#!/usr/bin/env python3
"""Extracted boss40 draw/ownership/filter pixels. Unit only, never game/capture."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess

BASE='5629b3dda05b2aa77af3c624841320d05c0f7130'
IDS=[1,3,5,7,10,12,14,16,18,39,41,43,45,48,50,54,56,86,88,90,92,94,124,126,128,130,132,162,164,168,170,200,202,206,208,240,242,244,246,280,238,278,282]
SOURCE_SHA='ab8881b4a26e723650780b19d5aed4ebfe410ea450d4bf7b80840628d61fd89b'
FREEZE_SHA='d82f610c48592b712907c0532fb50853bb2fc1e51a93f2fa8dc5511666612374'
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def extract(source,name):
    m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',source,re.M);assert m,name
    end=source.index('{',m.start())+1;depth=1
    while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[m.start():end]+'\n'

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--original-data',type=Path,required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[1];given=a.out.absolute();out=given.resolve()
assert not out.exists() and not any(q.is_symlink() for q in [given,*given.parents]),'Fresh nonsymlink output required'
assert out!=repo and repo not in out.parents and out not in repo.parents,'External output required'
original=a.original_data.read_bytes();assert sha(original)==SOURCE_SHA
source=(repo/'src/render_mirror.c').read_text();sprite=(repo/'src/sprite.c').read_text()
source_pins={n:sha((repo/n).read_bytes()) for n in ['src/render_mirror.c','src/sprite.c','src/ground101_material.c','prototype/test-boss-whole-family-pixels.c','prototype/test-boss-whole-family-pixels.py']}
art=repo/'assets/hd/artwork/boss-whole-family-v2-inward-alpha';assert sha((art/'inventory.json').read_bytes())==FREEZE_SHA
inventory=json.loads((art/'inventory.json').read_text());entries={e['base']:e for e in inventory['outputs']}
manifest=json.loads((repo/'assets/hd/manifest.json').read_text());reference=bytearray();asset_pins={};opaque=0;alpha_classes={"zero_inside_source":0,"fractional":0,"opaque":0}
for base in IDS:
    name=f'enemy-newsh4-{base}-8.hda';raw=(art/'output'/name).read_bytes()
    assert len(raw)==172060 and raw[:28]==b'HDR1'+struct.pack('<6I',1020000+base,8,24,28,6,7)
    assert sha(raw)==entries[base]['HDA_SHA256'];asset_pins[name]=sha(raw)
    if base not in [238,278,282]:
        for pack in [manifest['default_preview_pack'],manifest['default_debug_pack']]:assert (repo/'assets/hd/packs'/pack/name).read_bytes()==raw
    else:
        for pack in [manifest['default_preview_pack'],manifest['default_debug_pack']]:assert not (repo/'assets/hd/packs'/pack/name).exists()
    for q,part in enumerate([0,1,19,20]):
        pos=struct.unpack_from('<H',original,(base+part-1)*2)[0];cell=0;mask=bytearray(168);indices=bytearray(168)
        while original[pos]!=15:
            code=original[pos];pos+=1;cell+=code&15
            for _ in range(code>>4):
                assert 0<=cell<168 and not mask[cell];mask[cell]=255;indices[cell]=original[pos];pos+=1;cell+=1
        opaque+=sum(bool(v) for v in mask);px=96 if q&1 else 0;py=112 if q&2 else 0
        rgba=b''.join(raw[28+((py+y)*192+px)*4:28+((py+y)*192+px+96)*4] for y in range(112))
        for y in range(112):
            for x in range(96):
                alpha=rgba[(y*96+x)*4+3];support=mask[(y//8)*12+x//8]
                assert not alpha or support, 'V2 alpha expanded original RLE support'
                if support:alpha_classes['zero_inside_source' if not alpha else 'opaque' if alpha==255 else 'fractional']+=1
        if base in [238,278,282]:assert not any(mask)
        reference.extend(indices+mask+rgba)
assert all(alpha_classes.values()), 'Actual frozen V2 must exercise zero/fractional/opaque inside source support'
families=['linked31','newsh4_long7','newsh4_opposite7','type15_eightheading','late_spike','newsh4_entry6','type3_small','boss_whole']
names=['palette_rgb','blend_rgba','cloud_shadow_rgba','cloud_asset','darken_rgba','explosion_asset_slot','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','render_mirror_pixel','render_mirror_entity_end','read_asset','scene_asset']+[f+'_family_ready' for f in families]+['boss_whole_base_allowed','render_mirror_enemy_tile']
helpers={'ground101_enemy_eligible':extract((repo/'src/ground101_material.c').read_text(),'ground101_enemy_eligible')};helpers.update({name:extract(source,name) for name in names});helpers.update({name:extract(sprite,name) for name in ['blit_sprite2','blit_sprite2_filter']})
crop=re.search(r'  int d=game_probe_density;\n  for\(int y=0;y<184\*d;y\+\+\) memcpy\([^\n]+;',extract(source,'render_mirror_finish')).group()
helpers['production_crop_excerpt']='static void production_crop_excerpt(void) {\n'+crop+'\n}\n'
declarations='\n'.join(re.search(pattern,source,re.S).group() for pattern in [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'static Asset assets\[\d+\];'])+''.join('\nstatic bool '+f+'_checked,'+f+'_valid;\n' for f in families)
out.mkdir(parents=True);(out/'production-types.inc').write_text(declarations);(out/'production-functions.inc').write_text('\n'.join(helpers.values()));(out/'reference-data.bin').write_bytes(reference)
command=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(out),str(repo/'prototype/test-boss-whole-family-pixels.c'),'-o',str(out/'test')]
r=subprocess.run(command,capture_output=True,text=True);(out/'compile.log').write_text(r.stdout+r.stderr);r.check_returncode()
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');results={}
for kind in ['preview','debug']:
    pack=repo/'assets/hd/packs'/manifest['default_'+kind+'_pack'];r=subprocess.run([str(out/'test'),str(pack),str(a.original_data.resolve()),str(out/'reference-data.bin')],capture_output=True,text=True,env=env,timeout=900)
    (out/(kind+'.log')).write_text(r.stdout+r.stderr);r.check_returncode();results[kind]=r.stdout.strip();print(kind+': '+r.stdout.strip(),flush=True)
assert source_pins=={n:sha((repo/n).read_bytes()) for n in source_pins},'Source/test changed during run'
receipt={'status':'PASS','unit_only_no_game_or_capture':True,'baseline':BASE,'original_newsh4_sha256':SOURCE_SHA,'source_inventory_sha256':FREEZE_SHA,'source_pins':source_pins,'asset_sha256':asset_pins,'extracted_production_functions_sha256':{n:sha(v.encode()) for n,v in helpers.items()},'sanitizers':['AddressSanitizer','UndefinedBehaviorSanitizer'],'results':results,'coverage':{'source_alpha':{'coverage':'inward-only authored alpha within original RLE support','actual_density8_alpha_classes':alpha_classes,'bases':43,'quadrants':172,'logical_opaque_cells':opaque,'subpixels_per_cell':64,'empty_bases':[238,278,282]},'filters':'43x4x256 actual routes/draws + independent integer operator256 filters x256 peaks x6 alpha values x3 nonmonotonic palettes','blend':'Independent exact ordered local-underlay RGB for zero/fractional/opaque coverage; exhaustive 256 alpha values x256 source x256 destination operator cases',
'ownership':'Mixed pre-existing0/1/2 ownership; cloud provenance; green markers; exact source RLE indexed writes, RGB and selection per ordered call','order':'600 sequential overlapping two-actor/four-quadrant sequences with prior blended local RGB retained per pack, including mixed classic/HD physical geometry','geometry':'All43x4 for partial top/bottom clipping, physical x0/308, unsupported row wrap fallback and wholly-offscreen y; original RLE differential separately exhausts43x4','crop':'320 exact production ordinary crop cases per pack','memory':'Padded indexed storage and allocation canaries per transaction; all64 subpixels/ownership of affected ROI per transaction; full-frame RGB/index/selection/ownership every64 transactions and at phase boundaries; immutable under-layer full comparison at phase boundaries'},'limitations':['Extracted-source unit only; no game/lifecycle simulation, native capture, visual or runtime UI acceptance','LeakSanitizer disabled; every harness/asset allocation freed','Unrelated material/font/local-blend branches are fail-if-entered stubs; actual draw/filter/pixel/RLE functions exact production source; crop exact production excerpt wrapped for unit use','Whole-frame comparisons are periodic and at phase boundaries, not after every transaction']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
