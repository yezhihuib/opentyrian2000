#!/usr/bin/env python3
"""Finite Christmas enemy admission units; never launches the game.

Original data stays external. Only two bank8 slices and the named test HD assets
are copied into a fresh external output directory, never a full pack. Source-only
performs no compilation. Full checks compile extracted production functions with
-O2 and ASan/UBSan, plus a baseline witness using the same fixtures and harness.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import struct

ROOT = Path(__file__).resolve().parents[1]
TREE = '2a60deb74b1a677e3d3cd6c5ea0c251e8ac54028'
SHA = lambda raw: hashlib.sha256(raw).hexdigest()
IDS = [77,58,182,163,1,183,164,112,113,146,147,59,67,70,121,122,201,202,279,280,225,244,226]
PLAYERS = [58,59,67,70,121,122,163,164,201,202,279,280,225,244,226]
DATA_PINS = ['80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0',
             'e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d']
BANK_PINS = ['9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68',
             '26eb4fe91672bcef4bc88d7162d5f531144ad98eba64f5c0314e35fec85241e4']
ADDITION = ''' /* These nine enemy IDs use different Christmas originals. Decline before
  * even a warm normal-art cache; byte-identical shell146/147 stay eligible. */
 if(xmas&&bank.data==spriteSheet8.data&&
    (enemy_energy_slot(index)>=0||index==112||index==113))return false;
'''
FUNCTIONS = ['manual_hd_scope','vulcan_shadow_member','decode_tile','read_asset',
             'explosion_asset_slot','get_asset','talon_frame','render_mirror_entity',
             'enemy_energy_slot','enemy_energy_family_ready','enemy_tank_shell_family_ready',
             'render_mirror_enemy_shot']


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args])


def original(name):
    return git('show',TREE+':'+name)


def extract(source,name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',source,re.M)
    assert match,name
    pos = source.index('{',match.start())+1
    depth = 1
    while depth:
        depth += (source[pos]=='{')-(source[pos]=='}')
        pos += 1
    return source[match.start():pos]+'\n'


def source_scope():
    assert git('cat-file','-t',TREE).decode().strip()=='tree'
    paths = git('ls-tree','-r','--name-only',TREE,'--','src').decode().splitlines()
    assert {str(path.relative_to(ROOT)) for path in (ROOT/'src').rglob('*') if path.is_file()}==set(paths),'Unexpected production inventory'
    sources = {name:(ROOT/name).read_bytes() for name in paths}
    previous = {name:original(name) for name in paths}
    exact = runpy.run_path(str(ROOT/'prototype/test-normal15-source.py'))['verify_source'](ROOT)
    assert [name for name in paths if sources[name]!=previous[name]]==exact['changed_files']
    text = sources['src/render_mirror.c'].decode()
    before = previous['src/render_mirror.c'].decode()
    assert text.count(ADDITION)==1 and exact['combined_delta_inverse_exact'],'Exact two-patch production inverse'
    old_hook = extract(before,'render_mirror_enemy_shot')
    new_hook = extract(text,'render_mirror_enemy_shot')
    assert new_hook.replace(ADDITION,'',1)==old_hook
    assert new_hook.index(ADDITION)<new_hook.index('if(index==146')<new_hook.index('enemy_energy_family_ready()')
    assert extract(text,'enemy_energy_slot').count('{77,58,182,163,1,183,164}')==1
    opener = sources['src/opentyr.c'].decode()
    load_line = 'JE_loadMainShapeTables(xmas ? "tyrianc.shp" : "tyrian.shp");'
    assert load_line in opener
    params = sources['src/params.c'].decode()
    assert 'xmas = true;' in params and 'xmas = false;' in params
    assert (ROOT/'assets/hd/manifest.json').read_bytes()==original('assets/hd/manifest.json')
    assert not git('diff',TREE,'--','assets'), 'Asset edit outside scope'
    inventory = '\n'.join(name+' '+SHA(raw) for name,raw in sources.items()).encode()
    return sources,before,{
        'status':'PASS','public_baseline_commit':exact['public_baseline_commit'],'baseline_tree':TREE,
        'production_files_checked':len(paths),'changed_production_files':exact['changed_files'],
        'production_change':'Exact approved three-file night delta plus four-line Christmas guard, including two comment lines',
        'complete_production_inverse':True,'combined_delta_inverse_exact':exact['combined_delta_inverse_exact'],'christmas_guard_exact':True,'source_inventory_sha256':SHA(inventory),
        'renderer_sha256':SHA(sources['src/render_mirror.c']),
        'manifest_sha256':SHA(original('assets/hd/manifest.json')),
        'real_mode_loader':load_line,
        'scope':'Enemy-only bank8 role111 IDs77/58/182/163/1/183/164 and orb IDs112/113 (trace role108); shells146/147 role122 stay eligible',
        'mode_vs_bank':'Real normal=false/normal data and Xmas=true/Christmas data are tested separately from both deliberately mismatched controls. This guard does not hash source content.',
        'unchanged':'Every production byte outside the two exact approved deltas; original player/gameplay/indexed writes, physical-level9 eligibility, loaders and assets',
    }


def read_bank(path,pin,bpin):
    raw = path.read_bytes()
    assert SHA(raw)==pin,'Unexpected original input '+path.name
    count = struct.unpack_from('<H',raw)[0]
    offsets = list(struct.unpack_from('<'+str(count)+'I',raw,2))+[len(raw)]
    assert count>=9 and offsets==sorted(offsets)
    bank = raw[offsets[7]:offsets[8]]
    assert SHA(bank)==bpin
    return bank


def encoded_sprite(bank,index):
    start = pos = struct.unpack_from('<H',bank,2*(index-1))[0]
    while bank[pos]!=15:
        pos += 1+(bank[pos]>>4)
    return bank[start:pos+1]


def decode(bank,index):
    # Independent linear-cell oracle; production uses an x/y tile decoder and
    # original screen-pointer RLE. A row opcode has no extra linear-cell stride.
    pos = struct.unpack_from('<H',bank,2*(index-1))[0]
    cell = 0
    indices,mask = bytearray(168),bytearray(168)
    while bank[pos]!=15:
        code = bank[pos]
        pos += 1
        cell += code&15
        for _ in range(code>>4):
            assert 0<=cell<168 and not mask[cell]
            indices[cell],mask[cell] = bank[pos],255
            cell += 1
            pos += 1
    return bytes(indices+mask)


def extract_units(folder,renderer,sources):
    patterns = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
                r'enum \{ ASSET_NEWSH2=.*?\};',r'static Asset assets\[\d+\];',
                r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',
                r'static Asset talon_frames\[13\];',
                r'static const struct \{unsigned int index;.*?\} vulcan_shadow_pins\[13\]=\{.*?\n\};',
                r'static struct \{const Uint8 \*rgba;char path\[1024\];\} vulcan_shadow_resource\[13\];',
                r'static struct \{const Uint8 \*rgba;char path\[1024\];\} vulcan_shadow_coverage_resource\[3\];',
                r'static bool enemy_energy_checked,enemy_energy_valid;',
                r'static bool enemy_tank_shell_checked,enemy_tank_shell_valid;']
    chunks = []
    for pattern in patterns:
        match = re.search(pattern,renderer,re.S)
        assert match,pattern
        chunks.append(match.group())
    (folder/'types.inc').write_text('\n'.join(chunks)+'\n')
    names = (['normal15_scope'] if 'static bool normal15_scope(void)' in renderer else [])+FUNCTIONS
    helpers = [extract(renderer,name) for name in names]
    (folder/'functions.inc').write_text('\n'.join(s[:s.index('{')].strip()+';' for s in helpers)+'\n'+''.join(helpers))
    (folder/'blitters.inc').write_text(''.join(extract(sources['src/sprite.c'].decode(),name) for name in ['blit_sprite2','blit_sprite2_darken']))
    (folder/'wrappers.inc').write_text(''.join(extract(sources['src/entity_draw.c'].decode(),name) for name in ['draw_entity_sprite2','draw_enemy_shot_sprite2']))
    (folder/'ids.inc').write_text('enum {NID='+str(len(IDS))+'};\nstatic const unsigned ids[NID]={'+','.join(map(str,IDS))+'};\n')


def run(command,log,env=None):
    result = subprocess.run(command,capture_output=True,text=True,env=env,timeout=120)
    log.write_text(result.stdout+result.stderr)
    assert result.returncode==0,log.name+' failed: '+result.stderr[-3000:]
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only',action='store_true')
    parser.add_argument('--normal-data',type=Path)
    parser.add_argument('--xmas-data',type=Path)
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    sources,before,scope = source_scope()
    if args.source_only:
        print(json.dumps(scope,indent=2));return
    assert args.out and args.normal_data and args.xmas_data,'Supply both explicit original inputs and --out'
    out = args.out.resolve()
    assert not out.exists() and out!=ROOT and ROOT not in out.parents and out not in ROOT.parents,'Fresh external output required'
    banks = [read_bank(path,pin,bpin) for path,pin,bpin in zip([args.normal_data,args.xmas_data],DATA_PINS,BANK_PINS)]
    references = [[decode(bank,index) for index in IDS] for bank in banks]
    for k in range(11):
        assert (references[0][k]==references[1][k])==(k>=9)
    proof = {'original_sha256':dict(zip(['normal','christmas'],DATA_PINS)),
             'bank8_sha256':dict(zip(['normal','christmas'],BANK_PINS)),'sprites':{}}
    for k,index in enumerate(IDS[:11]):
        pair = [row[k] for row in references]
        encoded = [encoded_sprite(bank,index) for bank in banks]
        assert (encoded[0]==encoded[1])==(k>=9)
        proof['sprites'][str(index)] = {
            'index_equal':pair[0][:168]==pair[1][:168],'mask_equal':pair[0][168:]==pair[1][168:],
            'compressed_rle_equal':encoded[0]==encoded[1],
            'normal_rle_sha256':SHA(encoded[0]),'christmas_rle_sha256':SHA(encoded[1]),
            'normal_index_sha256':SHA(pair[0][:168]),'christmas_index_sha256':SHA(pair[1][:168]),
            'normal_mask_sha256':SHA(pair[0][168:]),'christmas_mask_sha256':SHA(pair[1][168:]),
        }
    manifest = json.loads(original('assets/hd/manifest.json'))
    names = [f'enemy-energy-{i}-8.hda' for i in IDS[:7]]+[f'bullet-{i}-8.hda' for i in [112,113]+PLAYERS]+[f'enemy-tank-shell-{i}-8.hda' for i in [146,147]]
    payloads = {}
    for kind in ['preview','debug']:
        pack = manifest['default_'+kind+'_pack']
        current = {}
        for name in names:
            data = original('assets/hd/packs/'+pack+'/'+name)
            assert SHA(data)==manifest['packs'][pack]['files'][name]['sha256']
            current[name]=data
        payloads[kind]=current
    assert payloads['preview']==payloads['debug'],'Bounded default-pack resources differ'
    out.mkdir();fixtures=out/'fixtures';fixtures.mkdir();pack=fixtures/'assets';pack.mkdir()
    for name,data in payloads['preview'].items():(pack/name).write_bytes(data)
    for i,bank in enumerate(banks):(fixtures/f'bank-{i}.bin').write_bytes(bank)
    (fixtures/'reference.bin').write_bytes(b''.join(item for row in references for item in row))
    (out/'source-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    harness = (ROOT/'prototype/test-christmas-enemy-fallback.c').read_bytes()
    results = {}
    env = dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    for label,renderer,flags in [
        ('baseline-optimized',before,['-O2','-DBASELINE=1']),
        ('candidate-optimized',sources['src/render_mirror.c'].decode(),['-O2']),
        ('candidate-sanitized',sources['src/render_mirror.c'].decode(),['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
        folder=out/label;folder.mkdir();extract_units(folder,renderer,sources)
        (folder/'driver.c').write_bytes(harness)
        command=[os.environ.get('CC','cc'),'-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',*flags,'-I'+str(folder),str(folder/'driver.c'),'-o',str(folder/'unit')]
        run(command,folder/'compile.log')
        results[label]=json.loads(run([str(folder/'unit'),str(pack),str(fixtures)],folder/'run.log',env))
    assert source_scope()[2]==scope,'Source changed during test'
    report={**scope,'original_source_proof':proof,'resource_files':len(names),
            'resource_sha256':{name:SHA(data) for name,data in payloads['preview'].items()},
            'preview_debug_resources_equal':True,'harness_sha256':SHA(harness),
            'function_sha256':{name:SHA(extract(sources['src/render_mirror.c'].decode(),name).encode()) for name in ['normal15_scope']+FUNCTIONS},
            'results':results,'game_runs':0,'full_game_builds':0,'unit_compilations':3,
            'coverage':['Real normal and real Christmas sources','Separate synthetic mismatched mode/bank controls','Cold and normal-warmed caches','Normal to Christmas to normal','No load/cache mutation on nine-ID Christmas fallback','Shell146/147 HD preserved','Player shared-ID/head/shadow isolation','Unrelated bank/ID and old negative guards','Original indexed writes execute once with exact ordered values and final full-screen bytes','Physical9 eligibility unchanged; physical15 admits normal-data ordinary Hard+ only and excludes Christmas/special modes'],
            'limitations':['LeakSanitizer is disabled because this executor cannot run LSan under its tracing environment; ASan and UBSan remain enabled','Extracted production units, not a game run or native2x/4x render acceptance','HD draw_asset is an observing stub: this validates admission, cache and indexed writes, not RGB composition','No whole-bank content validation; mismatched mode/bank fixtures intentionally prove that boundary','Unrelated font hooks are no-ops; unused cash/Vulcan-shadow/quad paths fail if entered']}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','renderer_sha256','resource_files','results','game_runs','full_game_builds']},indent=2))

if __name__=='__main__':main()
