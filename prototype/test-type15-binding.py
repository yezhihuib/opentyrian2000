#!/usr/bin/env python3
"""Exact current-source C-v2 route/loader/filter units; no game is launched.

The immutable native-tested pregame source baseline is reversed by the finite C compatibility
projection. Both trace lanes use their matching, pinned C artwork. Only draw,
material and telemetry boundaries are substituted in the compiled recorder.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import runpy
import struct
import subprocess
import type15_source_projection as projection

BASE = projection.BASE
IDS = projection.IDS
ORDER = [91,45,93,39,43,129,41,131]
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--baseline',default=BASE,help='Must resolve to fixed current-source baseline c9232d5')
    args = p.parse_args()
    repo,given = args.repo.resolve(),args.out.absolute()
    out = given.resolve()
    if out.exists() or any(q.is_symlink() for q in [given,*given.parents]) or out==repo or out in repo.parents or repo in out.parents:
        p.error('Fresh output outside repository, without symlink components, required')
    git = lambda *x: subprocess.check_output(['git','-C',str(repo),*x])
    assert git('rev-parse',args.baseline+'^{commit}').decode().strip()==BASE, 'Wrong baseline'
    source_bytes,baseline_bytes,version = projection.audit_sources(repo)
    assert version=='v2', 'C-v2 units require the exact approved current C-v2 pins/comment'
    negative_source_tests = projection.rejection_tests(baseline_bytes)
    source_pins = {n:sha(b) for n,b in source_bytes.items()}
    recorder_names = ['prototype/test-type15-binding.py','prototype/test-type15-binding.c',
                      'prototype/type15_source_projection.py','prototype/test-type4-binding.py']
    recorder_pins = {n:sha((repo/n).read_bytes()) for n in recorder_names}
    assert re.findall(r'game_probe_assets\s*=\s*([^;]+);',source_bytes['src/game_probe.c'].decode())==['argv[i]+19','argv[i]+16'], 'Reassess cache lifetime: selected-pack reload writer added'
    assert 'reload-fresh-process' in (repo/'src/asset_debug.c').read_text() and 'asset_debug_exit_code=75' in (repo/'src/asset_debug.c').read_text()
    proof_name = 'assets/hd/artwork/type15-eightheading-v1/proof/type15-source-proof.json'
    proof_raw = (repo/proof_name).read_bytes()
    assert proof_raw==git('show',BASE+':'+proof_name), 'Historical original-source proof changed'
    record = json.loads(proof_raw)['record15']
    assert record['egraphic']==ORDER+[0]*12 and record['ani']==8
    assert record['esize']==1 and record['shapebank']==1 and record['animate']==0
    caller = source_bytes['src/tyrian2.c'].decode()
    block = re.search(r'if \(enemy\[i\]\.size == 1\) // 2x2 enemy(.*?)\n\s*else',caller,re.S).group(1)
    quadrants = [tuple(map(int,x)) for x in re.findall(r'blit_enemy\(VGAScreen, i,\s*(-?\d+),\s*(-?\d+),\s*(\d+)\);',block)]
    assert quadrants==[(-6,-7,0),(6,-7,1),(-6,7,19),(6,7,20)]
    assert 'enemy[i].ey > -13' in block and 'enemy[i].ey > -26 && enemy[i].ey < 182' in block
    common = runpy.run_path(str(repo/'prototype/test-type4-binding.py'))
    families,extract = common['FAMILIES'],common['extract']
    functions = common['FUNCTIONS']+['render_mirror_map_begin']
    current = source_bytes['src/render_mirror.c'].decode()
    functions += re.findall(r'static int (\w+_slot)\(unsigned int id\)',current)
    functions += ['render_mirror_bind_terrain','render_mirror_terrain_row']
    assert len(functions)==len(set(functions))
    manifest = json.loads((repo/'assets/hd/manifest.json').read_text())
    packs = {kind:repo/'assets/hd/packs'/manifest['default_'+kind+'_pack'] for kind in ('preview','debug')}
    art_pins = {kind:projection.validate_pack(pack,'v2') for kind,pack in packs.items()}
    pack_pins = {kind:{q.name:sha(q.read_bytes()) for q in sorted(pack.glob('*.hda'))} for kind,pack in packs.items()}
    for pack in packs.values():
        for sprite_id in IDS:assert not (pack/f'enemy-newsh2-{sprite_id}-4.hda').exists(), 'Unexpected C 4x asset'
    out.mkdir(parents=True)
    baseline_packs = {kind:projection.baseline_pack(repo,pack,out/('baseline-'+kind+'-pack')) for kind,pack in packs.items()}
    env = dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    commands,runs,traces,cases = [],[],{},[]
    def run(command,label):
        commands.append(command)
        result = subprocess.run(command,env=env,capture_output=True,text=True,timeout=240)
        (out/(label+'.log')).write_text(result.stdout+result.stderr)
        result.check_returncode()
        return result.stdout
    for label,raw in [('baseline',baseline_bytes['src/render_mirror.c']),('candidate',source_bytes['src/render_mirror.c'])]:
        source = raw.decode()
        directory = out/label;directory.mkdir()
        patterns = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
                    r'enum \{ ASSET_NEWSH2=.*?\};',r'static Asset assets\[\d+\];',
                    r'static struct \{const Uint8 \*data;unsigned int id;\} terrain_sources\[\d+\];']
        declarations = '\n'.join(re.search(pattern,source,re.S).group() for pattern in patterns)
        declarations += '\n'+'\n'.join(re.search(r'static bool '+f+r'_checked,'+f+r'_valid;',source).group() for f in families)
        declarations += '\n'+re.search(r'typedef struct \{\s*unsigned type,pool_slot,availability,size;.*?\} G101EnemyContext;',source_bytes['src/ground101_material.h'].decode(),re.S).group()
        helpers = {name:extract(source,name) for name in functions}
        (directory/'production-types.inc').write_text(declarations+'\n')
        (directory/'production-helpers.inc').write_text('\n'.join(helpers.values()))
        (directory/'production-reset.inc').write_text('\n'.join(f'{f}_checked={f}_valid=false;' for f in families)+'\n')
        command = [os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror',
                   '-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer',
                   '-fno-pie','-no-pie','-I'+str(directory),str(repo/'prototype/test-type15-binding.c'),'-o',str(directory/'test')]
        run(command,label+'/compile')
        lane_packs = baseline_packs if label=='baseline' else packs
        traces[label] = {kind:run([str(directory/'test'),str(pack),'trace','1'],label+'/'+kind+'-trace') for kind,pack in lane_packs.items()}
        for kind,trace in traces[label].items():
            rows = {tuple(line.split()) for line in trace.splitlines()}
            assert all(('a','1',str(sprite_id),str(396+k)) in rows for k,sprite_id in enumerate(IDS)), 'C missing from trace '+label+'/'+kind
        runs.append({'label':label,'functions_sha256':{n:sha(t.encode()) for n,t in helpers.items()},
                     'declarations_sha256':sha(declarations.encode()),'source_sha256':sha(raw),'C_art_revision':'v1' if label=='baseline' else 'v2'})
    assert traces['baseline']==traces['candidate'], 'Actor/pickup/terrain namespace drift'
    projected = projection.project_render(source_bytes['src/render_mirror.c'],baseline_bytes['src/render_mirror.c'])[0].decode()
    assert runs[0]['functions_sha256']=={name:sha(extract(projected,name).encode()) for name in functions}
    executable = str(out/'candidate/test')
    def check(pack,present,label,good,mode='test'):
        text = run([executable,str(pack),mode,str(present),str(good)],label)
        cases.append({'label':label,'all_C_present':bool(present),'mode':mode,'result':text.strip()})
    fixtures = out/'fixtures';fixtures.mkdir()
    mutations = 0
    for kind,pack in packs.items():
        check(pack,1,kind+'-complete-eight',pack)
        check(pack,1,kind+'-all-byte-filters',pack,'filter')
        directory = fixtures/kind;directory.mkdir()
        for name in pack_pins[kind]:(directory/name).symlink_to(pack/name)
        for sprite_id in IDS:
            name = f'enemy-newsh2-{sprite_id}-8.hda'
            raw = (pack/name).read_bytes()
            invalid = {'missing':None,'magic':b'BAD!'+raw[4:],'short-header':raw[:27],
                       'truncated':raw[:-1],'trailing':raw+b'\0',
                       'RGB':raw[:28]+bytes([raw[28]^1])+raw[29:],
                       'alpha':raw[:31]+bytes([raw[31]^255])+raw[32:],
                       'partial-alpha':raw[:31]+bytes([127 if raw[31]!=127 else 126])+raw[32:],
                       'mixed-v1-v2':(repo/'assets/hd/artwork/type15-eightheading-v1/output'/name).read_bytes()}
            for field in range(6):
                bad=bytearray(raw);struct.pack_into('<I',bad,4+field*4,struct.unpack_from('<I',bad,4+field*4)[0]+1)
                invalid['header-'+str(field)]=bytes(bad)
            for why,data in invalid.items():
                target=directory/name
                if target.exists() or target.is_symlink():target.unlink()
                if data is not None:target.write_bytes(data)
                check(directory,0,f'{kind}-{sprite_id}-{why}',pack);mutations+=1
            target.unlink();target.symlink_to(pack/name)
        # A fully valid lower-density file is insufficient even when its 8x
        # counterpart is absent. No 4x file may be read by the C family latch.
        for sprite_id in IDS:
            raw=(pack/f'enemy-newsh2-{sprite_id}-8.hda').read_bytes()
            rgba=raw[28:];pixels=bytearray()
            for y in range(28*4):
                for x in range(24*4):
                    offset=((y*2)*(24*8)+x*2)*4;pixels.extend(rgba[offset:offset+4])
            target=directory/f'enemy-newsh2-{sprite_id}-8.hda';target.unlink()
            (directory/f'enemy-newsh2-{sprite_id}-4.hda').write_bytes(b'HDR1'+struct.pack('<6I',1010000+sprite_id,4,24,28,6,7)+pixels)
            check(directory,0,f'{kind}-{sprite_id}-density4-only',pack,'density4');mutations+=1
            target.symlink_to(pack/target.name)
        for sprite_id in IDS:(directory/f'enemy-newsh2-{sprite_id}-8.hda').unlink()
        check(directory,0,kind+'-all-density4-only',pack,'density4')
        missing_trace=run([executable,str(directory),'trace','0'],kind+'-missing-C-namespace')
        expected='\n'.join(line for line in traces['candidate'][kind].splitlines()
                           if not (line.split()[0]=='a' and line.split()[1]=='1' and int(line.split()[2]) in IDS))+'\n'
        assert missing_trace==expected, 'C fallback affected a neighbor, alias, pickup or terrain namespace'
    assert source_pins=={n:sha((repo/n).read_bytes()) for n in source_pins}, 'Production changed during units'
    assert set(source_bytes)=={str(q.relative_to(repo)) for q in (repo/'src').rglob('*') if q.is_file() or q.is_symlink()}
    assert recorder_pins=={n:sha((repo/n).read_bytes()) for n in recorder_names}, 'Recorder changed during units'
    assert pack_pins=={kind:{q.name:sha(q.read_bytes()) for q in sorted(pack.glob('*.hda'))} for kind,pack in packs.items()}, 'Input pack changed during units'
    report={'status':'PASS','baseline':BASE,'unit_only_no_game_or_capture':True,
            'production_source_exact_after_finite_C_projection':True,'source_sha256':source_pins,
            'projection_rejection_tests':negative_source_tests,'recorder_sha256':recorder_pins,
            'historical_source_proof_sha256':sha(proof_raw),'record15_order':ORDER,'source_quadrants':quadrants,
            'sanitizers':['AddressSanitizer','UndefinedBehaviorSanitizer'],'leak_detection':False,
            'runs':runs,'commands':commands,'case_count':len(cases),'cases':cases,'per_member_rejection_cases':mutations,
            'C_art_sha256':art_pins,'asset_input_sha256':pack_pins,
            'namespace_trace_sha256':{k:sha(t.encode()) for k,t in traces['candidate'].items()},
            'namespace_trace_records':{k:len(t.splitlines()) for k,t in traces['candidate'].items()},
            'coverage':{'ids':IDS,'slots':list(range(396,404)),'namespace':101,'dimensions':[24,28],
                        'anchor':[6,7],'density':8,'first_member_orders':8,'quadrants':4,'filters':256,
                        'both_defaults_full_matrix':True,'preflight_allocation_failure_positions':list(range(8)),
                        'failed_cache_reset_recovery':True,'successful_cache_until_reset':True,'valid_4x_payloads_probed':True,'mixed_v1_v2_rejected':True,'density4_no_read':True,
                        'all_sheet_identities':list(range(37)),'neighbor_and_alias_preservation':True,
                        'terrain_registry_capacity':199,'source_pack_content_unchanged':True},
            'fixture_policy':'Read-only symlinks for unmodified inputs; unlink before writing each independent fixture. No hardlink or source-target writes.',
            'limitations':['Extracted current-source unit recorder only; no game runs or rendered/native/Windows acceptance.',
                           'Material eligibility, telemetry and draw boundary are stubbed; loader, all family gates, routes and filter helper are exact production text.',
                           'Selector and quadrant proofs are source checks, not natural game lifecycle coverage.',
                           'LeakSanitizer disabled under executor ptrace; reset frees all loaded Asset allocations.']}
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:',out/'receipt.json')


if __name__=='__main__':main()
