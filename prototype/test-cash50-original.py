#!/usr/bin/env python3
"""Finite byte-exact original-source units for cash50; never builds/runs the game."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

BASE = '8fc7a3b2638ed765d7aadc0a345d2c23cd036bfa'
FIXTURE_SHA = '6f7d1dfb5ec72de5f4919ce77e7bda862c650e70813aae9247ae91b9e4deaa7d'
ROOT = Path(__file__).resolve().parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', '--out', dest='output', type=Path, required=True)
parser.add_argument('--packet', type=Path, help='Optional recheck against selected50 source packet')
parser.add_argument('--plan', type=Path, help='Optional recheck against frozen source-only plan')
args = parser.parse_args()
D = args.output.resolve()
assert D != ROOT and ROOT not in D.parents, 'Evidence must be outside checkout'
D.mkdir(parents=True, exist_ok=False)
files = ['src/tyrian2.c','src/mainint.c','src/varz.c','src/varz.h','src/player.h','src/opentyr.h','src/config.h','src/episodes.h','src/lvlmast.h']
b = {p: subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+p]) for p in files}
c = {p: (ROOT/p).read_bytes() for p in files}
hook25 = (b'\t\t\t\t/* Display-only eligibility for this original fixed value draw. */\n'
          b'\t\t\t\trender_mirror_coin25_value_begin(explosions[j].fixedPosition && !explosions[j].followPlayer &&\n'
          b'\t\t\t\t                                explosions[j].deltaY == 0 && explosions[j].sprite == 184 && explosions[j].ttl <= 8);\n')
def hook(family, stored):
    return ('\t\t\t\trender_mirror_coin%d_value_begin(explosions[j].fixedPosition && !explosions[j].followPlayer &&\n'
            '\t\t\t\t                                explosions[j].deltaY == 0 && explosions[j].sprite == %d && explosions[j].ttl <= 8);\n' % (family, stored)).encode()
hook75, hook50 = hook(75,222), hook(50,203)
assert b['src/tyrian2.c'].count(hook25) == b['src/tyrian2.c'].count(hook75) == 1
assert all(c['src/tyrian2.c'].count(h)==1 for h in (hook25,hook75,hook50))
assert c['src/tyrian2.c'].replace(hook50,b'') == b['src/tyrian2.c'], 'Only exact additive50 hook may change tyrian2.c'
for p in files[1:]: assert b[p] == c[p], p+' changed from baseline'
manifest = []
def save_excerpt(out,p,s,e):
    v=b[p][s:e];assert v in c[p],out+' not byte-exact in candidate'
    (D/out).write_bytes(v)
    manifest.append(dict(file=out,source=p,start_line=b[p][:s].count(b'\n')+1,end_line=b[p][:e].count(b'\n')+1,bytes=len(v),sha256=sha(v),candidate_exactly_unchanged=True))
    return v
def extract(out,p,start,end,include_end=False):
    s=b[p].index(start);e=b[p].index(end,s)+(len(end) if include_end else 0)
    return save_excerpt(out,p,s,e)
def brace_excerpt(out,p,start):
    s=b[p].index(start);a=b[p].index(b'{',s);depth=1;e=a+1
    while depth:
        depth+=(b[p][e:e+1]==b'{')-(b[p][e:e+1]==b'}');e+=1
    return save_excerpt(out,p,s,e)
extract('setup_explosion.inc','src/varz.c',b'void JE_setupExplosion(\n',b'\nvoid JE_setupExplosionLarge(')
extract('new_enemy.inc','src/tyrian2.c',b'Sint16 JE_newEnemy(',b'\nuint JE_makeEnemy(')
extract('make_enemy.inc','src/tyrian2.c',b'uint JE_makeEnemy(',b'\nvoid JE_createNewEventEnemy(')
extract('spawn_enemy.inc','src/tyrian2.c',b'void JE_createNewEventEnemy(',b'\nvoid JE_eventJump(')
extract('scoreitem.inc','src/mainint.c',b'\t\t\t\telse if (enemy[z].scoreitem)',b'\t\t\t\telse if (this_player->invulnerable_ticks')
extract('collision_envelope.inc','src/mainint.c',b'\tfor (int z = 0; z < 100; z++)\n',b'\t\t\t\tif (evalue > 29999)')
brace_excerpt('linked_death.inc','src/tyrian2.c',b'\t\t\t\t\t\t\tfor (temp2 = 0; temp2 < 100; temp2++)')
extract('reward.inc','src/tyrian2.c',b'\tint tempValue = 0;\n',b'\n\tint tempArmor = 1;')
for n,end in [(6,7),(19,20),(33,34),(45,46)]:
    extract('event%d.inc'%n,'src/tyrian2.c',('\tcase %d:'%n).encode(),('\n\tcase %d:'%end).encode())
extract('movement.inc','src/tyrian2.c',b'\t\t\tenemy[i].mapoffset = tempMapXOfs;',b'\t\t\tenemy[i].ey += tempBackMove;',True)
extract('enemy_type.inc','src/varz.h',b'struct JE_SingleEnemyType\n',b'\ntypedef struct JE_SingleEnemyType JE_MultiEnemyType')
extract('enemy_data_type.inc','src/episodes.h',b'/* EnemyData */\n',b'\nextern JE_WeaponPortType')
extract('enemy_num.inc','src/lvlmast.h',b'#define ENEMY_NUM',b'\n')
extract('explosion_type.inc','src/varz.h',b'typedef struct {\n\tJE_byte ttl;',b'} Explosion;',True)
extract('player_types.inc','src/player.h',b'typedef struct\n',b'\nextern Player player[2];')
extract('event_type.inc','src/varz.h',b'struct JE_EventRecType\n',b'\nstruct JE_MegaDataType1')
extract('difficulty_type.inc','src/config.h',b'enum\n{\n\tDIFFICULTY_WIMP',b'\n};',True)
extract('super_specials.inc','src/varz.c',b'const JE_byte superTyrianSpecials[4]',b';',True)
start=b'\t/*---------------------------- Draw Explosions ----------------------------*/';end=b'\n\tif (!portConfigChange)'
def draw_span(source):
    s=source.index(start);return source[s:source.index(end,s)]
baseline_draw,candidate_draw=draw_span(b['src/tyrian2.c']),draw_span(c['src/tyrian2.c'])
original_draw=baseline_draw.replace(hook25,b'').replace(hook75,b'')
assert candidate_draw.replace(hook25,b'').replace(hook75,b'').replace(hook50,b'')==original_draw
for name,content,projection in [('draw_original.inc',original_draw,'Baseline minus exact existing25/75 display hooks'),('draw_candidate.inc',candidate_draw,'Candidate including all three exact display-only hooks')]:
    (D/name).write_bytes(content);manifest.append(dict(file=name,source='src/tyrian2.c',bytes=len(content),sha256=sha(content),projection=projection))
fixture_bytes=(ROOT/'docs/cash50-seven-v1/original-data-fixture.json').read_bytes()
assert sha(fixture_bytes)==FIXTURE_SHA
fixture=json.loads(fixture_bytes);assert fixture['baseline_commit']==BASE
assert fixture['baseline_source_sha256']=={p:sha(b[p]) for p in files}
records,events=fixture['records'],fixture['events']
assert set(records)=={'13','14','391','392','393','628'}
assert [(e['index'],e['eventtime'],e['type'],e['dat'],e['dat4']) for e in events]==[(139,970,33,392,2),(149,1000,33,392,4),(150,1010,33,392,6)]
verification={'compact_fixture_sha256_pinned':True,'packet_rechecked':False,'plan_rechecked':False}
if args.packet:
    pb=args.packet.read_bytes();assert sha(pb)==fixture['original_packet_sha256'];p=json.loads(pb)
    assert p['selected_record']==records['392'] and p['first_pair_records']=={k:records[k] for k in ('13','14')}
    assert [a['assignment'] for a in p['assignments']]==events
    assert [e for e in p['events_context'] if e['index'] in (135,136)]==fixture['spawn_events']
    assert [e for e in p['events_context'] if e['type']==19 and e['dat4']==2 and 1050<=e['eventtime']<=1077]==fixture['movement_events']
    verification['packet_rechecked']=True
if args.plan:
    assert sha(args.plan.read_bytes())==fixture['frozen_plan_sha256'];verification['plan_rechecked']=True
assert sha((ROOT/'docs/cash75-seven-v1/original-data-fixture.json').read_bytes())==fixture['historical_control_fixture_sha256']
fixture_lines=[]
for rid,r in records.items():
    for field,value in r.items():
        if field=='id':continue
        if isinstance(value,list):fixture_lines += [f'enemyDat[{rid}].{field}[{i}]={v};' for i,v in enumerate(value)]
        else:fixture_lines.append(f'enemyDat[{rid}].{field}={value};')
(D/'record_fixture.inc').write_text('\n'.join(fixture_lines)+'\n')
for key,name in [('events','fixture_events'),('spawn_events','fixture_spawns'),('movement_events','fixture_moves')]:
    (D/(key+'_fixture.inc')).write_text('static const struct JE_EventRecType '+name+'[] = {\n'+''.join(' {.eventtime=%d,.eventtype=%d,.eventdat=%d,.eventdat2=%d,.eventdat3=%d,.eventdat4=%d,.eventdat5=%d,.eventdat6=%d},\n'%(e['eventtime'],e['type'],e['dat'],e['dat2'],e['dat3'],e['dat4'],e['dat5'],e['dat6']) for e in fixture[key])+'};\n')
for src,dst in [('test-cash50-original.c','driver.c'),('test-cash50-original.h','unit.h')]:shutil.copyfile(ROOT/'prototype'/src,D/dst)
(D/'new_enemy.c').write_text('#include "unit.h"\n#include "new_enemy.inc"\n')
(D/'make_enemy.c').write_text('#include "unit.h"\n#include "make_enemy.inc"\n')
harness_files={str(Path('prototype')/n):sha((ROOT/'prototype'/n).read_bytes()) for n in ['test-cash50-original.py','test-cash50-original.c','test-cash50-original.h']}
source_manifest=dict(harness_files_sha256=harness_files,baseline_commit=BASE,candidate_commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip(),candidate_is_working_tree=True,fixture_sha256=FIXTURE_SHA,verification=verification,plan_sha256=fixture['frozen_plan_sha256'],packet_sha256=fixture['original_packet_sha256'],files={p:dict(baseline_sha256=sha(b[p]),candidate_sha256=sha(c[p])) for p in files},excerpts=manifest,whole_tyrian2_inverse50_exact=True,all_other_selected_source_files_exact=True,candidate_effect_loop_original_projection_byte_exact=True,mode_events=events)
(D/'source-manifest.json').write_text(json.dumps(source_manifest,indent=2)+'\n')
base_cmd=['gcc','-std=c11','-Wall','-Wextra','-Werror','-g','driver.c','new_enemy.c','make_enemy.c','-Wl,--wrap=JE_newEnemy','-Wl,--wrap=JE_makeEnemy']
runs={}
for name,flags in [('optimized',['-O2']),('sanitized',['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
    exe='test-'+name
    with (D/('compile-'+name+'.log')).open('wb') as log:subprocess.run(base_cmd+flags+['-o',exe],cwd=D,stdout=log,stderr=subprocess.STDOUT,check=True)
    env=os.environ.copy();env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    with (D/('result-'+name+'.log')).open('wb') as log:subprocess.run([str(D/exe)],cwd=D,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    output=(D/('result-'+name+'.log')).read_text();print(output,end='');runs[name]=json.loads(re.search(r'^RESULT (.*)$',output,re.M).group(1))
assert runs['optimized']==runs['sanitized']
for p in files:assert (ROOT/p).read_bytes()==c[p],p+' changed during unit run'
limitations=['Byte-exact extracted original source and pinned tiny records/events, not a full game, natural collection, original-input replay or runtime mode matrix.', 'The complete original JE_makeEnemy constructor, allocator, spawn function and linked-death traversal execute. mt_rand is a deterministic counted test stream, not the production RNG engine/state.', 'Carrier release is observed at its original immediately following large-explosion call, after its reward and release and before the next death-loop allocation. The large-explosion function is an observation stub; full loop statements are unmodified.', 'Collection envelope/predicate and scoreitem branch are exact excerpts; unrelated collision branches are omitted. Movement excerpt ends after background y addition; original enemy shooting logic is not executed.', 'Renderer, indexed-draw sink and eligibility functions are observation stubs; this proves draw-call/Explosion-state equality and call-site eligibility, not actual renderer pixels.', 'LeakSanitizer is disabled for executor compatibility; AddressSanitizer and UBSan remain enabled.']
gates={n:'PASS' for n in ['ascending_two_carrier_original_traversal','zero_one_multiple_initial_free_pool_slots','full_pool_first_fail_second_reuses_released_carrier','allocation_before_own_release_and_exact_coordinate_copy','full_original_constructor_counted_rng_and_no_rng_on_failure','normal50_linked25_plus25_separate_carrier25_each','strict_original_collection_dx12_dy14_boundary','full200_effect_pool_and_setup_y_bounds','fixed204_eight_draws_and_moving48_final204_ineligible','all_three_families_mixed_gate_isolation','original_candidate_all200_explosion_bytes_and_draw_calls','difficulty_scaling_threshold_cap_and_carrier_rewards','exact_events139_149_150_and_mode_guard_controls','later_link2_moves_leave_link0_coins_unchanged','original_body_animation_draw_y_and_removal_order','event135_136_original_spawn_coordinates_and_fields','super_arcade30000_suppression_preserves25_50_75']}
receipt=dict(gates=gates,status='PASS',evidence_kind='byte-exact-original-source-unit',gameplay_runs=0,production_edits=0,baseline_commit=BASE,scenarios_per_build=runs['optimized']['scenarios'],assertions_per_build=runs['optimized']['checks'],builds=runs,limitations=limitations,source_manifest='source-manifest.json',toolchain=subprocess.check_output(['gcc','--version']).decode().splitlines()[0])
(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(D/'README.md').write_text('# Finite 50 original-source units\n\nPASS: %d scenarios and %d assertions per optimized and ASan/UBSan build. No game runs.\n\n'%(receipt['scenarios_per_build'],receipt['assertions_per_build'])+'\n'.join('- '+x for x in limitations)+'\n\nReproduce using a fresh external directory: python3 prototype/test-cash50-original.py --out /tmp/cash50-original-new\n\nDefault execution uses only pinned Git source, the three new harness files and the compact fixture. No sibling-directory dependency. Existing evidence directories are rejected. Optional --packet and --plan recheck audit inputs. Only the added50 hook is removed to restore the published baseline; all three display hooks are removed solely for the original effect-loop reference. Original source remains GPL-2.0-or-later.\n')
(D/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in sorted(D.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))
print(json.dumps({'status':'PASS','receipt':str(D/'receipt.json'),'gameplay_runs':0}))
