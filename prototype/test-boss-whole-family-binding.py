#!/usr/bin/env python3
"""Finite extracted boss40 loader/route/RLE units. Never launches the game."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess

BASE = '5629b3dda05b2aa77af3c624841320d05c0f7130'
SOURCE_SHA = 'ab8881b4a26e723650780b19d5aed4ebfe410ea450d4bf7b80840628d61fd89b'
IDS = [1,3,5,7,10,12,14,16,18,39,41,43,45,48,50,54,56,86,88,90,92,94,124,126,128,130,132,162,164,168,170,200,202,206,208,240,242,244,246,280]
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--original-data', type=Path, required=True)
a = p.parse_args()
repo = Path(__file__).resolve().parents[1]
given = a.out.absolute(); out = given.resolve()
assert not out.exists() and not any(q.is_symlink() for q in [given,*given.parents]), 'Fresh nonsymlink output required'
assert out != repo and out not in repo.parents and repo not in out.parents, 'External output required'
assert sha(a.original_data.read_bytes()) == SOURCE_SHA
assert re.findall(r'game_probe_assets\s*=', (repo/'src/game_probe.c').read_text()) == ['game_probe_assets=']
assert 'reload-fresh-process' in (repo/'src/asset_debug.c').read_text()
out.mkdir(parents=True)
git = lambda *args: subprocess.check_output(['git','-C',str(repo),*args])
base = git('show', BASE+':src/render_mirror.c').decode()
current = (repo/'src/render_mirror.c').read_text(); sprite = (repo/'src/sprite.c').read_text()
source_pins = {}
for name in git('ls-tree','-r','--name-only',BASE,'src').decode().splitlines():
    raw = (repo/name).read_bytes()
    if name != 'src/render_mirror.c': assert raw == git('show',BASE+':'+name), 'Original source changed: '+name
    source_pins[name] = sha(raw)
recorder_pins = {n:sha((repo/n).read_bytes()) for n in ['prototype/test-boss-whole-family-binding.py','prototype/test-boss-whole-family-binding.c']}
manifest = json.loads((repo/'assets/hd/manifest.json').read_text())
pack = repo/'assets/hd/packs'/manifest['default_preview_pack']; debug = repo/'assets/hd/packs'/manifest['default_debug_pack']
env = dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
functions, traces, results = {}, {}, []
for label, source in [('baseline',base),('candidate',current)]:
    d=out/label;d.mkdir()
    declarations='\n'.join(re.search(pattern,source,re.S).group() for pattern in [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'static Asset assets\[\d+\];',r'static struct \{const Uint8 \*data;unsigned int id;\} terrain_sources\[\d+\];'])
    families=['linked31','newsh4_long7','newsh4_opposite7','type15_eightheading','late_spike','newsh4_entry6','type3_small']
    if label=='candidate': families+=['boss_whole']
    declarations+=''.join('\nstatic bool '+f+'_checked,'+f+'_valid;\n' for f in families)
    (d/'production-types.inc').write_text(declarations)
    names=['read_asset','scene_asset']+[f+'_family_ready' for f in families]
    if label=='candidate': names+=['boss_whole_base_allowed']
    names+=['render_mirror_enemy_tile','render_mirror_map_begin']+re.findall(r'static int (\w+_slot)\(unsigned int id\)',source)+['render_mirror_bind_terrain','render_mirror_terrain_row']
    helpers={name:extract(source,name) for name in names}
    functions[label]={n:sha(v.encode()) for n,v in helpers.items()}
    (d/'production-helpers.inc').write_text('\n'.join(helpers.values()))
    (d/'production-original.inc').write_text(extract(sprite,'blit_sprite2')+extract(sprite,'blit_sprite2_filter'))
    command=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-DBASELINE='+str(int(label=='baseline')),'-I'+str(d),str(repo/'prototype/test-boss-whole-family-binding.c'),'-o',str(d/'test')]
    r=subprocess.run(command,capture_output=True,text=True);(d/'compile.log').write_text(r.stdout+r.stderr);r.check_returncode()
    traces[label]={}
    for kind,directory in [('preview',pack),('debug',debug)]:
        r=subprocess.run([str(d/'test'),str(directory),'trace','1'],env=env,capture_output=True,text=True,timeout=180)
        (d/(kind+'-trace.log')).write_text(r.stdout+r.stderr);r.check_returncode();traces[label][kind]=r.stdout
for name,digest in functions['baseline'].items():
    if name!='render_mirror_enemy_tile': assert functions['candidate'][name]==digest,'Changed earlier helper: '+name
assert traces['baseline']==traces['candidate'], 'Earlier namespaces changed for nonboss context'

def check(directory,mode,arg,label):
    r=subprocess.run([str(out/'candidate/test'),str(directory),mode,str(arg)],env=env,capture_output=True,text=True,timeout=240)
    (out/(label+'.log')).write_text(r.stdout+r.stderr);r.check_returncode();results.append(label);return r.stdout.strip()
check(pack,'test',1,'complete-preview40')
check(debug,'test',1,'complete-debug40')
check(pack,'geometry',1,'physical-layout-extremes')
original_log=check(pack,'original',a.original_data.resolve(),'original-rle')
check(out/'absent-pack','unavailable',0,'absent-pack')
names=[f'enemy-newsh4-{i}-8.hda' for i in IDS]
families={
 'long7':[f'enemy-newsh4-{i}-8.hda' for i in [153,155,157,159,191,193,195]],
 'opposite7':[f'enemy-newsh4-{i}-8.hda' for i in [231,233,235,267,269,271,273]],
 'spike':[f'enemy-newsh2-{i}-8.hda' for i in [1,3,5,7,9,11]],
 'type15':[f'enemy-newsh2-{i}-8.hda' for i in [39,41,43,45,91,93,129,131]],
 'entry6':[f'enemy-newsh4-{i}-8.hda' for i in [81,83,85,119,121,123]],
 'type3':[f'enemy-newsh2-{i}-8.hda' for i in [171,190,209,228,247,266]],
 'linked31':[f'enemy-newsh2-{i}-8.hda' for i in [15,17,53,55]]+[f'terrain-shapesz-{i}-8.hda' for i in [161,162,171,172]],
}
all_files=names+['enemy-newsh2-153-8.hda']+[n for fs in families.values() for n in fs]
assert len(all_files)==len(set(all_files))
before={n:sha((pack/n).read_bytes()) for n in all_files}
fixtures=out/'fixtures';fixtures.mkdir()
def fixture(target,replacement):
    d=fixtures/'current'
    if d.exists(): shutil.rmtree(d)
    d.mkdir()
    # Unmodified members are read-only hardlinks; replaced member always has
    # its own inode. No harness path writes a linked member.
    for n in all_files:
        if n!=target: os.link(pack/n,d/n)
    if replacement is not None:(d/target).write_bytes(replacement)
    return d
four=fixtures/'four-only';four.mkdir()
for name in names:
    raw=(pack/name).read_bytes();rgba=raw[28:]
    pixels=b''.join(rgba[(y*2*192+x*2)*4:(y*2*192+x*2)*4+4] for y in range(112) for x in range(96))
    h=list(struct.unpack('<6I',raw[4:28]));h[1]=4
    (four/name.replace('-8.hda','-4.hda')).write_bytes(b'HDR1'+struct.pack('<6I',*h)+pixels)
check(four,'unavailable',0,'four-only-no-retry')
for name in names:
    raw=(pack/name).read_bytes()
    invalid={'missing':None,'magic':b'BAD!'+raw[4:],'truncated':raw[:-1],'trailing':raw+b'\0','alpha':raw[:31]+bytes([raw[31]^255])+raw[32:],'partial-alpha':raw[:31]+b'\x7f'+raw[32:],'rgb':raw[:28]+bytes([raw[28]^1])+raw[29:]}
    for field in range(6):
        bad=bytearray(raw);struct.pack_into('<I',bad,4+field*4,struct.unpack_from('<I',bad,4+field*4)[0]+1);invalid['header-'+str(field)]=bytes(bad)
    for kind,replacement in invalid.items():check(fixture(name,replacement),'failure',0,name+'-'+kind)
    print('Failure matrix passed:',name,flush=True)
for family,targets in families.items():
    for target in targets:
        raw=(pack/target).read_bytes()
        for kind,replacement in [('missing',None),('integrity',raw[:31]+b'\x7f'+raw[32:])]:check(fixture(target,replacement),'independent',family,'independent-'+target+'-'+kind)
for name in names:
    good=(pack/name).read_bytes()
    for kind,bad in [('missing',None),('rgb',good[:28]+bytes([good[28]^1])+good[29:])]:
        for present in [0,1]:
            label='cache-'+name+'-'+kind+'-'+str(present);d=fixture(name,good if present else bad)
            proc=subprocess.Popen([str(out/'candidate/test'),str(d),'cache',str(present)],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            ready=proc.stdout.readline()
            if ready!='READY\n':
                stdout,stderr=proc.communicate(timeout=180);(out/(label+'.log')).write_text(ready+stdout+stderr);raise AssertionError(label)
            target=d/name;replacement=bad if present else good
            if replacement is None:target.unlink()
            else:target.write_bytes(replacement)
            stdout,stderr=proc.communicate('\n',timeout=180);(out/(label+'.log')).write_text(ready+stdout+stderr);assert proc.returncode==0,label;results.append(label)
shutil.rmtree(fixtures)
assert before=={n:sha((pack/n).read_bytes()) for n in all_files},'Source pack mutated'
assert source_pins=={n:sha((repo/n).read_bytes()) for n in source_pins},'Source changed during test'
assert recorder_pins=={n:sha((repo/n).read_bytes()) for n in recorder_pins},'Recorder changed during test'
receipt={'status':'PASS','unit_only_no_game_or_capture':True,'baseline':BASE,'source_pins':source_pins,'recorder_source_sha256':recorder_pins,'functions_sha256':functions,'sanitizers':['AddressSanitizer','UndefinedBehaviorSanitizer'],'leak_detection':False,'original_newsh4_sha256':SOURCE_SHA,'original_rle_result':original_log,'new_bindings':40,'slot_range':[422,461],'transparent_audit_assets_never_loaded':[238,278,282],'unchanged_namespace_trace_sha256':{k:sha(v.encode()) for k,v in traces['baseline'].items()},'coverage':{'V2_alpha':'Exact pinned assets; zero/fractional/opaque coverage stays inside independently decoded original RLE support','all40x4x256_filters':True,'first_member_orders':40,'allocation_failure_positions':40,'invalid_resource_variants_per_member':13,'failure_cases':520,'disk_cache_mutation_cases':160,'record_base_cross_product_types':[0,1701],'context_flags':'all16 boolean combinations x availability0..2; pool_slot UINT_MAX','independent_prior_families':list(families),'physical_layout':'320x200 pitch320 indexed8; x0..308 y-13..199; INT_MIN/MAX and all four parts; invalid layout does not poison type15','selected_pack_density_and_debug_gates':True,'absent_and4x_only':True},'case_labels':results,'limitations':['Extracted source unit only, no game execution, lifecycle simulation, capture, visual acceptance, native presentation or UI/runtime claim','Draw recorder checks ordered arguments and full preflight; actual RGB/ownership are covered by the separate pixel unit','LeakSanitizer disabled; reset explicitly frees every Asset allocation']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS:',out/'receipt.json')
