#!/usr/bin/env python3
"""Finite byte-exact original-source units; never builds or runs the game."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

BASE = '96be433c41a5042121102510d862446385105381'
FIXTURE_SHA = '985442ebe5a020f8610fc91eccef0dbd85072b7642254eb34881df7ce7659a46'
ROOT = Path(__file__).resolve().parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', '--out', dest='output', type=Path, required=True)
parser.add_argument('--packet', type=Path, help='Optional recheck against original selected75 source packet')
parser.add_argument('--tables', type=Path, help='Optional recheck against original decoded tables')
parser.add_argument('--plan', type=Path, help='Optional recheck against the frozen plan')
args = parser.parse_args()
D = args.output.resolve()
assert D != ROOT and ROOT not in D.parents, 'Evidence must be outside production checkout'
D.mkdir(parents=True, exist_ok=False)  # Never overwrite prior evidence
files = ['src/tyrian2.c','src/mainint.c','src/varz.c','src/varz.h','src/player.h','src/opentyr.h','src/config.h']
b = {p: subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+p]) for p in files}
c = {p: (ROOT/p).read_bytes() for p in files}
hook25 = (b'\t\t\t\t/* Display-only eligibility for this original fixed value draw. */\n'
          b'\t\t\t\trender_mirror_coin25_value_begin(explosions[j].fixedPosition && !explosions[j].followPlayer &&\n'
          b'\t\t\t\t                                explosions[j].deltaY == 0 && explosions[j].sprite == 184 && explosions[j].ttl <= 8);\n')
hook75 = (b'\t\t\t\trender_mirror_coin75_value_begin(explosions[j].fixedPosition && !explosions[j].followPlayer &&\n'
          b'\t\t\t\t                                explosions[j].deltaY == 0 && explosions[j].sprite == 222 && explosions[j].ttl <= 8);\n')
assert b['src/tyrian2.c'].count(hook25) == 1
assert c['src/tyrian2.c'].count(hook25) == c['src/tyrian2.c'].count(hook75) == 1
assert c['src/tyrian2.c'].replace(hook75,b'') == b['src/tyrian2.c'], 'Only the exact additive75 call may change tyrian2.c'
for p in files[1:]:
    assert b[p] == c[p], p+' changed from baseline'
manifest = []
def extract(out, p, start, end, include_end=False):
    s = b[p].index(start); e = b[p].index(end,s) + (len(end) if include_end else 0)
    v = b[p][s:e]
    assert v in c[p], out+' not byte-exact in candidate'
    (D/out).write_bytes(v)
    manifest.append(dict(file=out,source=p,start_line=b[p][:s].count(b'\n')+1,end_line=b[p][:e].count(b'\n')+1,bytes=len(v),sha256=sha(v),candidate_exactly_unchanged=True))
    return v
extract('setup_explosion.inc','src/varz.c',b'void JE_setupExplosion(\n',b'\nvoid JE_setupExplosionLarge(')
extract('new_enemy.inc','src/tyrian2.c',b'Sint16 JE_newEnemy(',b'\nuint JE_makeEnemy(')
extract('scoreitem.inc','src/mainint.c',b'\t\t\t\telse if (enemy[z].scoreitem)',b'\t\t\t\telse if (this_player->invulnerable_ticks')
extract('drop_release.inc','src/tyrian2.c',b'\t\t\t\t\t\t\t\t\t\tif ((enemy[temp2].enemydie > 0)',b'\t\t\t\t\t\t\t\t\t\tif (enemyDat[enemy[temp2].enemytype].esize == 1)')
extract('reward.inc','src/tyrian2.c',b'\tint tempValue = 0;\n',b'\n\tint tempArmor = 1;')
extract('event33.inc','src/tyrian2.c',b'\tcase 33: /* Enemy From other Enemies */',b'\n\tcase 34:')
extract('event45.inc','src/tyrian2.c',b'\tcase 45: /* arcade-only enemy from other enemies */',b'\n\tcase 46:')
extract('enemy_type.inc','src/varz.h',b'struct JE_SingleEnemyType\n',b'\ntypedef struct JE_SingleEnemyType JE_MultiEnemyType')
extract('explosion_type.inc','src/varz.h',b'typedef struct {\n\tJE_byte ttl;',b'} Explosion;',True)
extract('player_types.inc','src/player.h',b'typedef struct\n',b'\nextern Player player[2];')
extract('event_type.inc','src/varz.h',b'struct JE_EventRecType\n',b'\nstruct JE_MegaDataType1')
extract('difficulty_type.inc','src/config.h',b'enum\n{\n\tDIFFICULTY_WIMP',b'\n};',True)
extract('super_specials.inc','src/varz.c',b'const JE_byte superTyrianSpecials[4]',b';',True)
start = b'\t/*---------------------------- Draw Explosions ----------------------------*/'
end = b'\n\tif (!portConfigChange)'
def draw_span(source):
    s=source.index(start);e=source.index(end,s)
    return s,e,source[s:e]
s,e,baseline_draw=draw_span(b['src/tyrian2.c'])
s2,e2,candidate_draw=draw_span(c['src/tyrian2.c'])
original_draw=baseline_draw.replace(hook25,b'')
assert candidate_draw.replace(hook75,b'').replace(hook25,b'') == original_draw
for name,content,projection in [('draw_original.inc',original_draw,'Baseline minus exact existing25 display hook'),('draw_candidate.inc',candidate_draw,'Candidate including both exact display-only hooks')]:
    (D/name).write_bytes(content)
    manifest.append(dict(file=name,source='src/tyrian2.c',bytes=len(content),sha256=sha(content),projection=projection))
fixture_bytes=(ROOT/'docs/cash75-seven-v1/original-data-fixture.json').read_bytes()
assert sha(fixture_bytes)==FIXTURE_SHA, 'Compact data fixture changed'
fixture=json.loads(fixture_bytes)
assert fixture['baseline_commit']==BASE
assert fixture['baseline_source_sha256']=={p:sha(b[p]) for p in files}
records=fixture['records'];events=fixture['events']
assert set(records)=={'391','393','628'} and len(events)==5
verification={'compact_fixture_sha256_pinned':True,'packet_rechecked':False,'tables_rechecked':False,'plan_rechecked':False}
if args.packet:
    packet_bytes=args.packet.read_bytes();assert sha(packet_bytes)==fixture['original_packet_sha256']
    packet=json.loads(packet_bytes)
    assert packet['selected75']['record']==records['393']
    assert [e for a in packet['selected75']['assignments'][:3] for e in a['same_time_link_drop_events']]==events
    assert packet['retained_tables']['sha256']==fixture['original_decoded_tables_sha256']
    verification['packet_rechecked']=True
if args.tables:
    tables_bytes=args.tables.read_bytes();assert sha(tables_bytes)==fixture['original_decoded_tables_sha256']
    tables=json.loads(tables_bytes)
    assert {rid:tables['enemies'][rid] for rid in records}==records
    verification['tables_rechecked']=True
if args.plan:
    assert sha(args.plan.read_bytes())==fixture['frozen_plan_sha256']
    verification['plan_rechecked']=True
# These generated constants are exactly the compact pinned decoded-data fixture.
fixture_lines=[]
for rid,value,effect in [(391,25,36),(393,75,38),(628,30000,None)]:
    r=records[str(rid)]
    assert r['value']==value
    if effect is not None: assert r['explosiontype']==effect
    fixture_lines.append(f'enemyDat[{rid}].value={value}; enemyDat[{rid}].explosiontype={r["explosiontype"]};')
(D/'record_fixture.inc').write_text('\n'.join(fixture_lines)+'\n')
assert [(e['index'],e['eventtime'],e['type'],e['dat'],e['dat4']) for e in events]==[(29,240,33,393,10),(43,340,33,393,5),(44,340,45,628,5),(60,440,33,393,10),(61,440,45,628,10)]
(D/'event_fixture.inc').write_text('static const struct JE_EventRecType fixture_events[] = {\n'+''.join(' {.eventtime=%d,.eventtype=%d,.eventdat=%d,.eventdat2=%d,.eventdat3=%d,.eventdat4=%d,.eventdat5=%d,.eventdat6=%d},\n'%(e['eventtime'],e['type'],e['dat'],e['dat2'],e['dat3'],e['dat4'],e['dat5'],e['dat6']) for e in events)+'};\n')
for src,dst in [('test-cash75-original.c','driver.c'),('test-cash75-original.h','unit.h')]:
    shutil.copyfile(ROOT/'prototype'/src,D/dst)
(D/'new_enemy.c').write_text('#include "unit.h"\n#include "new_enemy.inc"\n')
harness_files={str(Path('prototype')/name):sha((ROOT/'prototype'/name).read_bytes()) for name in ['test-cash75-original.py','test-cash75-original.c','test-cash75-original.h']}
source_manifest=dict(harness_files_sha256=harness_files,baseline_commit=BASE,candidate_commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip(),candidate_is_working_tree=True,fixture_sha256=FIXTURE_SHA,verification=verification,plan_sha256=fixture['frozen_plan_sha256'],packet_sha256=fixture['original_packet_sha256'],decoded_tables_sha256=fixture['original_decoded_tables_sha256'],files={p:dict(baseline_sha256=sha(b[p]),candidate_sha256=sha(c[p])) for p in files},excerpts=manifest,whole_tyrian2_inverse75_exact=True,all_other_source_files_exact=True,candidate_effect_loop_original_projection_byte_exact=True,mode_events=events)
(D/'source-manifest.json').write_text(json.dumps(source_manifest,indent=2)+'\n')
base_cmd=['gcc','-std=c11','-Wall','-Wextra','-Werror','-g','driver.c','new_enemy.c','-Wl,--wrap=JE_newEnemy']
runs={}
for name,flags in [('optimized',['-O2']),('sanitized',['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
    exe='test-'+name
    with (D/('compile-'+name+'.log')).open('wb') as log:
        subprocess.run(base_cmd+flags+['-o',exe],cwd=D,stdout=log,stderr=subprocess.STDOUT,check=True)
    import os
    env=os.environ.copy();env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    with (D/('result-'+name+'.log')).open('wb') as log:
        subprocess.run([str(D/exe)],cwd=D,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    output=(D/('result-'+name+'.log')).read_text();print(output,end='')
    runs[name]=json.loads(re.search(r'^RESULT (.*)$',output,re.M).group(1))
assert runs['optimized']==runs['sanitized']
for p in files: assert (ROOT/p).read_bytes()==c[p],p+' changed during unit run'
limitations=['Extracted branches and source-derived constants; not a full game, natural collection, original-input run or mode runtime matrix.', 'The complete original JE_makeEnemy reward block is executed; the rest of the constructor is not. A labeled constructor stub is used only for allocator positive controls and mode drop observations.', 'Full-pool negative allocation never reaches that stub. No allocator, collection, drop, reward, setup, draw-loop or mode-condition body is hand-reimplemented.', 'Renderer and eligibility functions are observation stubs; moving223 rejection means original draw-site eligibility is false, not renderer/pixel proof.', 'LeakSanitizer is disabled because executor ptrace is incompatible; AddressSanitizer and UBSan remain enabled.']
gates={name:'PASS' for name in ['normal75_and_linked37_plus37','preserved25_and_linked12_plus12','full_sky_pool_all25_positions_before_release','full200_effect_pool','setup_y_bounds_and187_to189_cancel','fixed223_and185_exact_eight_draws_and_clear','original_candidate_all200_explosion_bytes_and_indexed_calls','moving_types45_and49_callsite_ineligible_at223','mixed185_and223_callsite_gate_independence','all_reward_difficulties_and_threshold_cap_cases','packet_exact_event33_event45_mode_matrix','super_tyrian_exception_and_link0_isolation','super_arcade628_drop_suppression']}
receipt=dict(gates=gates,status='PASS',evidence_kind='byte-exact-original-source-unit',gameplay_runs=0,production_edits=0,baseline_commit=BASE,scenarios_per_build=runs['optimized']['scenarios'],assertions_per_build=runs['optimized']['checks'],builds=runs,limitations=limitations,source_manifest='source-manifest.json',toolchain=subprocess.check_output(['gcc','--version']).decode().splitlines()[0])
(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(D/'README.md').write_text('# Finite 75 original-source units\n\nPASS: %d scenarios and %d assertions per optimized and ASan/UBSan build. No game runs.\n\n'%(receipt['scenarios_per_build'],receipt['assertions_per_build'])+'\n'.join('- '+x for x in limitations)+'\n\nFull source/excerpt pins: source-manifest.json. Logs: result-optimized.log and result-sanitized.log. Both display hooks are removed only for the original projection; unchanged original indexed draw calls and Explosion bytes are compared after every loop step. Mode fixtures preserve event index29/type33 at240 link10, index43/type33 then44/type45 at340 link5, index60/type33 then61/type45 at440 link10. Original source remains GPL-2.0-or-later. The initial harness compile found signed/unsigned comparison warnings under -Werror; those test-only expressions were corrected before any unit execution. Historical initial-compile logs in the parent evidence directory document that diagnostic iteration; both final builds have empty warning logs.\n\nReproduce from the checkout using a fresh external directory: python3 prototype/test-cash75-original.py --out /tmp/cash75-original-new\n\nDefault execution uses only pinned Git source, the three small harness files and docs/cash75-seven-v1/original-data-fixture.json. It has no sibling-directory dependency. Existing output directories are rejected without changing their files. Optional --packet, --tables and --plan paths recheck original audit sources.\n')
(D/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in sorted(D.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))
print(json.dumps({'status':'PASS','receipt':str(D/'receipt.json'),'gameplay_runs':0}))
