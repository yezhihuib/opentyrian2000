#!/usr/bin/env python3
"""Finite byte-exact original-source units for gem250; never builds/runs the game."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

BASE = '93008cc051b4b00c512dc9f8599849f6db1132e3'
FIXTURE_SHA = 'd4336c2f3bcfc28388ce08d5be9b2a86468bac88a72f91efd57630ecbc9a4fb5'
ROOT = Path(__file__).resolve().parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', '--out', dest='output', type=Path, required=True)
args = parser.parse_args()
D = args.output.resolve()
assert D != ROOT and ROOT not in D.parents, 'Evidence must be outside checkout'
D.mkdir(parents=True, exist_ok=False)
files = ['src/tyrian2.c','src/mainint.c','src/varz.c','src/varz.h','src/player.h','src/opentyr.h','src/config.h','src/episodes.h','src/lvlmast.h','src/shots.h']
b = {p: subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+p]) for p in files}
c = {p: (ROOT/p).read_bytes() for p in files}
hook25 = (b'\t\t\t\t/* Display-only eligibility for this original fixed value draw. */\n'
          b'\t\t\t\trender_mirror_coin25_value_begin(explosions[j].fixedPosition && !explosions[j].followPlayer &&\n'
          b'\t\t\t\t                                explosions[j].deltaY == 0 && explosions[j].sprite == 184 && explosions[j].ttl <= 8);\n')
def hook(family, stored):
    return ('\t\t\t\trender_mirror_coin%d_value_begin(explosions[j].fixedPosition && !explosions[j].followPlayer &&\n'
            '\t\t\t\t                                explosions[j].deltaY == 0 && explosions[j].sprite == %d && explosions[j].ttl <= 8);\n' % (family, stored)).encode()
hook75, hook50 = hook(75,222), hook(50,203)
hook100 = hook(100,168).replace(b'coin100', b'gem100')
hook250 = hook(250,187).replace(b'coin250', b'gem250')
assert all(b['src/tyrian2.c'].count(h)==1 for h in (hook25,hook75,hook50,hook100))
assert all(c['src/tyrian2.c'].count(h)==1 for h in (hook25,hook75,hook50,hook100,hook250))
assert c['src/tyrian2.c'].replace(hook250,b'') == b['src/tyrian2.c'], 'Only exact additive250 hook may change tyrian2.c'
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
extract('shot_limit.inc','src/shots.h',b'#define MAX_PWEAPON',b'\n')
extract('shot_collision_prefix.inc','src/tyrian2.c',b'\t\t\tfor (b = 0; b < 100; b++)',b'\t\t\t\t\tif (collided)')
extract('link_normalization.inc','src/tyrian2.c',b'\t\t\t\t\t\ttemp = enemy[b].linknum;',b'\t\t\t\t\t\tif (enemy[b].armorleft < 255)')
extract('reward.inc','src/tyrian2.c',b'\tint tempValue = 0;\n',b'\n\tint tempArmor = 1;')
for n,end in [(7,8),(15,16),(19,20),(33,34),(45,46)]:
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
original_draw=baseline_draw.replace(hook25,b'').replace(hook75,b'').replace(hook50,b'').replace(hook100,b'')
assert candidate_draw.replace(hook25,b'').replace(hook75,b'').replace(hook50,b'').replace(hook100,b'').replace(hook250,b'')==original_draw
for name,content,projection in [('draw_original.inc',original_draw,'Baseline minus exact existing25/75/50/100 display hooks'),('draw_candidate.inc',candidate_draw,'Candidate including all five exact display-only hooks')]:
    (D/name).write_bytes(content);manifest.append(dict(file=name,source='src/tyrian2.c',bytes=len(content),sha256=sha(content),projection=projection))
fixture_bytes=(ROOT/'docs/gem250-six-v1/original-data-fixture.json').read_bytes()
assert sha(fixture_bytes)==FIXTURE_SHA
fixture=json.loads(fixture_bytes);assert fixture['baseline_commit']==BASE
assert fixture['baseline_source_sha256']=={p:sha(b[p]) for p in files}
records,events=fixture['records'],fixture['events']
assert set(records)=={'17','30','31','391','392','393','394','395','509','628'}
assert [(e['index'],e['eventtime'],e['type'],e['dat'],e['dat4']) for e in events]==[(316,2100,33,394,182),(325,2130,33,394,143),(334,2330,33,394,163)]
# Re-decode each tiny 77-byte original record; the fixture is not an editable oracle.
import struct
def decode_record(raw,rid):
    i=0;r={'id':rid}
    def take(fmt):
        nonlocal i
        size=struct.calcsize('<'+fmt);v=struct.unpack_from('<'+fmt,raw,i);i+=size
        return list(v) if len(v)>1 else v[0]
    for field,fmt in [('ani','B'),('tur','3B'),('freq','3B'),('xmove','b'),('ymove','b'),('xaccel','b'),('yaccel','b'),('xcaccel','b'),('ycaccel','b'),('startx','h'),('starty','h'),('startxc','b'),('startyc','b'),('armor','B'),('esize','B'),('egraphic','20H'),('explosiontype','B'),('animate','B'),('shapebank','B'),('xrev','b'),('yrev','b'),('dgr','H'),('dlevel','b'),('dani','b'),('elaunchfreq','B'),('elaunchtype','H'),('value','h'),('eenemydie','H')]:r[field]=take(fmt)
    assert i==len(raw)==77
    return r
for rid,source in fixture['record_sources'].items():
    raw=bytes.fromhex(source['hex']);assert sha(raw)==source['sha256'] and decode_record(raw,int(rid))==records[rid]
for row in fixture['record509_by_table'].values():
    raw=bytes.fromhex(row['source']['hex']);assert sha(raw)==row['source']['sha256'] and decode_record(raw,509)==row['record']
for event in events+fixture['spawn_events']+fixture['earlier_link82_candidates']+fixture['red250']['events']:
    raw=bytes.fromhex(event['source_bytes_hex']);assert sha(raw)==event['source_sha256']
    assert list(struct.unpack('<HBhhbbbB',raw))==[event[x] for x in ('eventtime','type','dat','dat2','dat3','dat5','dat6','dat4')]
verification={'compact_fixture_sha256_pinned':True,'tiny_record_and_event_bytes_redecoded':True,'packet_rechecked':False,'plan_rechecked':False}
assert sha((ROOT/'docs/gem100-six-v1/original-data-fixture.json').read_bytes())==fixture['historical100_fixture_sha256']
for table in fixture['red250']['full_original_enemy_table_reuse']:
    assert table['record395']==records['395'] and table['record395_source']['hex']==fixture['record_sources']['395']['hex']
    assert table['effect40_all_record_users']==[395] and table['effect40_collectible_users']==[395]
    for users in table['selected_body_users'].values():assert users=={'direct_users':[395],'composite_quadrant_users':[]}
control_bytes=(ROOT/'docs/cash50-seven-v1/original-data-fixture.json').read_bytes()
assert sha(control_bytes)==fixture['historical_control_fixture_sha256']
control=json.loads(control_bytes)
for rid in ('391','392','393','628'):assert records[rid]==control['records'][rid]
fixture_lines=[]
for rid,r in records.items():
    for field,value in r.items():
        if field=='id':continue
        if isinstance(value,list):fixture_lines += [f'enemyDat[{rid}].{field}[{i}]={v};' for i,v in enumerate(value)]
        else:fixture_lines.append(f'enemyDat[{rid}].{field}={value};')
(D/'record_fixture.inc').write_text('\n'.join(fixture_lines)+'\n')
for key,name in [('events','fixture_events'),('spawn_events','fixture_spawns')]:
    (D/(key+'_fixture.inc')).write_text('static const struct JE_EventRecType '+name+'[] = {\n'+''.join(' {.eventtime=%d,.eventtype=%d,.eventdat=%d,.eventdat2=%d,.eventdat3=%d,.eventdat4=%d,.eventdat5=%d,.eventdat6=%d},\n'%(e['eventtime'],e['type'],e['dat'],e['dat2'],e['dat3'],e['dat4'],e['dat5'],e['dat6']) for e in fixture[key])+'};\n')
for table,out in [('tyrian.hdt','record509_shared.inc'),('tyrian4.lvl','record509_ep4.inc'),('tyrian5.lvl','record509_ep5.inc')]:
    r=fixture['record509_by_table'][table]['record'];lines=[]
    for field,value in r.items():
        if field=='id':continue
        if isinstance(value,list):lines += [f'enemyDat[509].{field}[{i}]={v};' for i,v in enumerate(value)]
        else:lines.append(f'enemyDat[509].{field}={value};')
    (D/out).write_text('\n'.join(lines)+'\n')
shutil.copyfile(ROOT/'prototype/test-gem100-original.h',D/'unit.h')
driver=(ROOT/'prototype/test-gem100-original.c').read_text()
driver=driver.replace('gates100[256];','gates100[256],gates250[256];').replace('gate_count100;','gate_count100,gate_count250;')
needle='void render_mirror_gem100_value_begin(bool e){CHECK(gate_count100<(int)COUNTOF(gates100));gates100[gate_count100++]=e;}'
assert driver.count(needle)==1;driver=driver.replace(needle,needle+'\n'+needle.replace('gem100','gem250').replace('count100','count250').replace('gates100','gates250'))
driver=driver.replace('memset(gates100,0,sizeof(gates100));','memset(gates100,0,sizeof(gates100));memset(gates250,0,sizeof(gates250));').replace('gate_count100=carrier_count=0','gate_count100=gate_count250=carrier_count=0')
driver=driver.replace('gate_count100==count);','gate_count100==count && gate_count250==count);').replace('CHECK(gates100[i]==(fixed && draws[i].id==169));','CHECK(gates100[i]==(fixed && draws[i].id==169));CHECK(gates250[i]==(fixed && draws[i].id==188));')
driver=driver.replace('#include "event7.inc"','#include "event7.inc"\n#include "event15.inc"')
driver=driver.replace('rid==393?222:168','rid==393?222:rid==395?187:168')
red_events='static const struct JE_EventRecType red_events[] = {\n'+''.join(' {.eventtime=%d,.eventtype=%d,.eventdat=%d,.eventdat2=%d,.eventdat3=%d,.eventdat4=%d,.eventdat5=%d,.eventdat6=%d},\n'%(e['eventtime'],e['type'],e['dat'],e['dat2'],e['dat3'],e['dat4'],e['dat5'],e['dat6']) for e in fixture['red250']['events'])+'};\n'
extra=red_events+(ROOT/'prototype/test-gem250-original.c').read_text();driver=driver.replace('int main(void)',extra+'\nint main(void)').replace(' test_collection();',' test_red250();test_collection();')
(D/'driver.c').write_text(driver)
(D/'new_enemy.c').write_text('#include "unit.h"\n#include "new_enemy.inc"\n')
(D/'make_enemy.c').write_text('#include "unit.h"\n#include "make_enemy.inc"\n')
harness_files={str(Path('prototype')/n):sha((ROOT/'prototype'/n).read_bytes()) for n in ['test-gem250-original.py','test-gem250-original.c','test-gem100-original.c','test-gem100-original.h']}
source_manifest=dict(harness_files_sha256=harness_files,baseline_commit=BASE,candidate_commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip(),candidate_is_working_tree=True,fixture_sha256=FIXTURE_SHA,verification=verification,packet_sha256=fixture['original_packet_sha256'],files={p:dict(baseline_sha256=sha(b[p]),candidate_sha256=sha(c[p])) for p in files},excerpts=manifest,whole_tyrian2_inverse250_exact=True,all_other_selected_source_files_exact=True,candidate_effect_loop_original_projection_byte_exact=True,mode_events=events)
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
limitations=['Byte-exact extracted original source and pinned tiny records/events, not a game run, natural collection, replay, or runtime mode matrix.', 'Full original constructor, allocator, spawn function and lethal linked traversal execute; mt_rand is a deterministic counted stream, not the original RNG engine/state.', 'Large-explosion and renderer sinks only observe; effect state and draw arguments are compared, not actual renderer pixels.', 'Exact collection envelope/scoreitem branch, ordinary-shot ascending avail0 collision prefix/predicate and movement through background-y execute. The first-shot-match observer returns its first match; weapon movement, damage aftermath, piercing/special-shot behavior and enemy shooting branches are not simulated.', 'Earlier link82 actors are not assumed absent: exact caller link0-to255 normalization and lethal-sweep match/link-minus100/lower-equal20 eligibility are tested. First-collision tests cover lower-slot side actor at dx12 and lead31 at exact dy15 without asserting runtime actor presence.', 'LeakSanitizer is disabled for executor compatibility; AddressSanitizer and UBSan remain enabled.']
gates={n:'PASS' for n in ['red250_held16_original_animation_and_movement','red250_fixed40_moving36_exclusion','red250_difficulty_linked_collection_and_full_effect_pool','red250_sky_event15_allocation_before_release_copy_and_full_pool','all16_held394_body_states_and_five_source_ids','shared_fixed169_from394_and_all509_variants','shared123_509_nominal250_display100_mismatch_preserved','moving35_reaches169_but_all_cash_gates_false','all_four_families_mixed_gate_isolation','fixed169_eight_draws_and_clear_steps','full200_effect_pool_and_setup_y_bounds','top25_drop_pool_full_omission_and_reuse_after_release','allocation_before_own_release_coordinate_copy_and_rng','exact_linked_sweep_match_minus100_lower_equal20_and_zero_to255','original_normal_shot_ascending_avail0_first_collision_and_strict_boundaries','normal15_carrier_reward_separate_from100_gem','difficulty_scaling_linked75_to37_plus37','strict_original_collection_dx12_dy14_boundary','all200_explosion_bytes_and_draw_calls_unchanged','event313_320_331_original_top_spawn_and316_325_334_assignments','original_body_draw_filter_clear_motion_and_removal_order','event33_mode_guards_and_arcade30000_suppression']}
receipt=dict(gates=gates,status='PASS',evidence_kind='byte-exact-original-source-unit',gameplay_runs=0,production_edits=0,baseline_commit=BASE,scenarios_per_build=runs['optimized']['scenarios'],assertions_per_build=runs['optimized']['checks'],builds=runs,limitations=limitations,source_manifest='source-manifest.json',toolchain=subprocess.check_output(['gcc','--version']).decode().splitlines()[0])
(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(D/'README.md').write_text('# Finite 250 original-source units with historical100 regressions\n\nPASS: %d scenarios and %d assertions per optimized and ASan/UBSan build. No game runs.\n\n'%(receipt['scenarios_per_build'],receipt['assertions_per_build'])+'\n'.join('- '+x for x in limitations)+'\n\nReproduce in a fresh external directory: python3 prototype/test-gem250-original.py --out /tmp/gem250-original-new\n\nDefault execution uses pinned Git source, the additive and historical harness files and compact fixture, with no sibling-directory dependency. Existing evidence directories are rejected. Only the additive250 hook is removed to restore the published baseline; all five display hooks are removed solely for the original effect-loop reference. Original source remains GPL-2.0-or-later.\n')
(D/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in sorted(D.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))
print(json.dumps({'status':'PASS','receipt':str(D/'receipt.json'),'gameplay_runs':0}))
