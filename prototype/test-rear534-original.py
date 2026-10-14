#!/usr/bin/env python3
"""Small exact-source rear534 units; no game build or run, no repository writes."""
import argparse,hashlib,json,os,re,shutil,struct,subprocess
from pathlib import Path
BASE='ee2b90cfaf9f227ca394ecd01f2403e55dbf2ea0'
sha=lambda b:hashlib.sha256(b).hexdigest()
DATA_SHA256={'tyrian.hdt': 'fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b', 'tyrian1.lvl': '54cbb00b57b84aa992a70cfcb170cb1edeb59507873723630d60080ba8351352'}
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,required=True);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();R=a.repo.resolve();D=a.out.resolve();S=Path(__file__).resolve().parent
assert not D.exists() and D!=R and R not in D.parents
assert shutil.disk_usage(D.parent).free>=4*1024**3,'4GiB free-space floor'
files=['src/tyrian2.c','src/mainint.c','src/player.c','src/varz.c','src/varz.h','src/player.h','src/opentyr.h','src/config.h','src/episodes.h','src/episodes.c','src/lvlmast.h','src/shots.h']
b={f:subprocess.check_output(['git','-C',str(R),'show',BASE+':'+f]) for f in files};c={f:(R/f).read_bytes() for f in files}
assert b==c,'Original-source files changed from exact published baseline'
for n,h in DATA_SHA256.items():assert sha((a.data/n).read_bytes())==h,'Original data pin changed: '+n
for n in ['prototype/test-gem100-original.c','prototype/test-gem100-original.h']:
 assert (R/n).read_bytes()==subprocess.check_output(['git','-C',str(R),'show',BASE+':'+n]),'Historical scaffold changed: '+n
D.mkdir();manifest=[]
def extract(out,f,start,end,inc=False):
 s=b[f].index(start);e=b[f].index(end,s)+(len(end) if inc else 0);raw=b[f][s:e];(D/out).write_bytes(raw);manifest.append({'file':out,'source':f,'start_line':b[f][:s].count(b'\n')+1,'end_line':b[f][:e].count(b'\n')+1,'sha256':sha(raw),'bytes':len(raw),'byte_exact':True});return raw

def braces(out,f,start):
 s=b[f].index(start);e=b[f].index(b'{',s)+1;depth=1
 while depth:depth+=(b[f][e:e+1]==b'{')-(b[f][e:e+1]==b'}');e+=1
 raw=b[f][s:e];(D/out).write_bytes(raw);manifest.append({'file':out,'source':f,'start_line':b[f][:s].count(b'\n')+1,'end_line':b[f][:e].count(b'\n')+1,'sha256':sha(raw),'bytes':len(raw),'byte_exact':True});return raw
for out,f,start,end,inc in [
 ('setup_explosion.inc','src/varz.c',b'void JE_setupExplosion(\n',b'\nvoid JE_setupExplosionLarge(',False),
 ('new_enemy.inc','src/tyrian2.c',b'Sint16 JE_newEnemy(',b'\nuint JE_makeEnemy(',False),
 ('make_enemy.inc','src/tyrian2.c',b'uint JE_makeEnemy(',b'\nvoid JE_createNewEventEnemy(',False),
 ('spawn_enemy.inc','src/tyrian2.c',b'void JE_createNewEventEnemy(',b'\nvoid JE_eventJump(',False),
 ('scoreitem.inc','src/mainint.c',b'\t\t\t\telse if (enemy[z].scoreitem)',b'\t\t\t\telse if (this_player->invulnerable_ticks',False),
 ('collision_envelope.inc','src/mainint.c',b'\tfor (int z = 0; z < 100; z++)\n',b'\t\t\t\tif (evalue > 29999)',False),
 ('link_normalization.inc','src/tyrian2.c',b'\t\t\t\t\t\ttemp = enemy[b].linknum;',b'\t\t\t\t\t\tif (enemy[b].armorleft < 255)',False),
 ('reward.inc','src/tyrian2.c',b'\tint tempValue = 0;\n',b'\n\tint tempArmor = 1;',False),
 ('movement.inc','src/tyrian2.c',b'\t\t\tenemy[i].mapoffset = tempMapXOfs;',b'\t\t\tenemy[i].ey += tempBackMove;',True),
 ('enemy_type.inc','src/varz.h',b'struct JE_SingleEnemyType\n',b'\ntypedef struct JE_SingleEnemyType JE_MultiEnemyType',False),
 ('enemy_data_type.inc','src/episodes.h',b'/* EnemyData */\n',b'\nextern JE_WeaponPortType',False),
 ('enemy_num.inc','src/lvlmast.h',b'#define ENEMY_NUM',b'\n',False),
 ('shot_limit.inc','src/shots.h',b'#define MAX_PWEAPON',b'\n',False),
 ('explosion_type.inc','src/varz.h',b'typedef struct {\n\tJE_byte ttl;',b'} Explosion;',True),
 ('player_types.inc','src/player.h',b'typedef struct\n',b'\nextern Player player[2];',False),
 ('event_type.inc','src/varz.h',b'struct JE_EventRecType\n',b'\nstruct JE_MegaDataType1',False),
 ('difficulty_type.inc','src/config.h',b'enum\n{\n\tDIFFICULTY_WIMP',b'\n};',True),
 ('super_specials.inc','src/varz.c',b'const JE_byte superTyrianSpecials[4]',b';',True),
 ('power_up.inc','src/player.c',b'void calc_purple_balls_needed(',b'\nvoid handle_got_purple_ball(',False)]:extract(out,f,start,end,inc)
braces('linked_death.inc','src/tyrian2.c',b'\t\t\t\t\t\t\tfor (temp2 = 0; temp2 < 100; temp2++)')
for n,end in [(15,16),(20,21),(33,34)]:extract(f'event{n}.inc','src/tyrian2.c',f'\tcase {n}:'.encode(),f'\n\tcase {end}:'.encode())
loop=extract('draw_candidate.inc','src/tyrian2.c',b'\t/*---------------------------- Draw Explosions ----------------------------*/',b'\n\tif (!portConfigChange)')
original=loop.replace(b'\t\t\t\t/* Display-only eligibility for this original fixed value draw. */\n',b'')
for fam,stored in [('coin25',184),('coin75',222),('coin50',203),('gem100',168),('gem250',187)]:
 h=(f'\t\t\t\trender_mirror_{fam}_value_begin(explosions[j].fixedPosition && !explosions[j].followPlayer &&\n'+f'\t\t\t\t                                explosions[j].deltaY == 0 && explosions[j].sprite == {stored} && explosions[j].ttl <= 8);\n').encode();assert original.count(h)==1;original=original.replace(h,b'')
(D/'draw_original.inc').write_bytes(original)
# Fresh original byte decode using unchanged loader schema. No game-data copy.
h=(a.data/'tyrian.hdt').read_bytes();ptr=struct.unpack_from('<i',h)[0]+14;src=b['src/episodes.c'].decode();bounds={k:int(v) for k,v in re.findall(r'#define\s+(\w+)\s+(\d+)',b['src/lvlmast.h'].decode())};fm={'u8':'B','s8':'b','u16':'H','s16':'h'}
def schema(var):return [(name,fm[fmt],int(n)) for fmt,name,n in re.findall(r'fread_(u8|s8|u16|s16)_die\(\s*&?'+var+r'\[i\]\.(\w+),\s*(\d+),\s*f\)',src)]
def records(sc,ids):
 global ptr
 out={};spans={}
 for rid in ids:
  start=ptr;rec={}
  for name,f,n in sc:
   v=list(struct.unpack_from('<'+str(n)+f,h,ptr));ptr+=n*struct.calcsize(f);rec[name]=v[0] if n==1 else v
  out[rid]=rec;spans[rid]={'offset':start,'bytes':ptr-start,'sha256':sha(h[start:ptr]),'hex':h[start:ptr].hex()}
 return out,spans
records(schema('weapons'),list(range(bounds['WEAP_END1']+1))+list(range(bounds['WEAP_START2'],bounds['WEAP_NUM']+1)))
for n,z in [('PORT_NUM',82),('SPECIAL_NUM',37),('POWER_NUM',37),('SHIP_NUM',41),('OPTION_NUM',86),('SHIELD_NUM',37)]:ptr+=(bounds[n]+1)*z
recs,spans=records(schema('enemyDat'),list(range(bounds['ENEMY_END1']+1))+list(range(bounds['ENEMY_START2'],bounds['ENEMY_NUM']+1)))
selected=[10,533,534,535,800,801];lines=[]
for rid in selected:
 for f,v in recs[rid].items():
  lines += [f'enemyDat[{rid}].{f}[{i}]={x};' for i,x in enumerate(v)] if isinstance(v,list) else [f'enemyDat[{rid}].{f}={v};']
(D/'record_fixture.inc').write_text('\n'.join(lines)+'\n')
assert recs[534]['value']==-2 and recs[534]['egraphic'][:12]==[203]*3+[205]*3+[207]*3+[205]*3
# Exact first-level event bytes, not an editable event oracle.
lvl=(a.data/'tyrian1.lvl').read_bytes();n=struct.unpack_from('<H',lvl)[0];p0=struct.unpack_from('<'+str(n)+'i',lvl,2)[16]+8;n=struct.unpack_from('<H',lvl,p0)[0];p0+=2+2*n;n=struct.unpack_from('<H',lvl,p0)[0];p0+=2;events=[]
for index in [6,16,17]:
 raw=lvl[p0+11*(index-1):p0+11*index];v=struct.unpack('<HBhhbbbB',raw);d=dict(zip(['eventtime','eventtype','eventdat','eventdat2','eventdat3','eventdat5','eventdat6','eventdat4'],v));events.append({'index':index,'fields':d,'hex':raw.hex(),'sha256':sha(raw)})
(D/'events_fixture.inc').write_text('static const struct JE_EventRecType rear_events[]={\n'+''.join(' {'+','.join('.'+k+'='+str(v) for k,v in e['fields'].items())+'},\n' for e in events)+'};\n')
# Reuse only the published narrow scaffold; replace unselected reward sinks.
harness=R/'prototype/test-gem100-original.c';driver=harness.read_text().split('static void test_collection(void)')[0]
driver=driver.replace('void JE_drawTextWindow(const char *p) {(void)p;unexpected();}', 'static int text_calls;static char last_text[256];\nvoid JE_drawTextWindow(const char *p) {text_calls++;snprintf(last_text,sizeof(last_text),"%s",p);}')
driver=driver.replace('bool power_up_weapon(Player *p,uint w) {(void)p;(void)w;unexpected();return false;}','#include "power_up.inc"')
driver=driver.replace('#include "spawn_events_fixture.inc"','').replace('#include "event7.inc"\n#include "event19.inc"','#include "event15.inc"\n#include "event20.inc"').replace('#include "event45.inc"','')
driver=driver.replace('enemy[slot].enemytype==394','enemy[slot].enemytype==534')
driver=driver.replace('gates100[256];','gates100[256],gates250[256];').replace('gate_count100;','gate_count100,gate_count250;')
needle='void render_mirror_gem100_value_begin(bool e){CHECK(gate_count100<(int)COUNTOF(gates100));gates100[gate_count100++]=e;}'
assert driver.count(needle)==1;driver=driver.replace(needle,needle+'\n'+needle.replace('gem100','gem250').replace('count100','count250').replace('gates100','gates250'))
driver=driver.replace('memset(gates100,0,sizeof(gates100));','memset(gates100,0,sizeof(gates100));memset(gates250,0,sizeof(gates250));text_calls=0;last_text[0]=0;miscText[43]="P2";miscText[45]="rear power";')
driver=driver.replace('gate_count100=carrier_count=0','gate_count100=gate_count250=carrier_count=0')
driver=driver.replace('gate_count100==count);','gate_count100==count && gate_count250==count);').replace('CHECK(gates100[i]==(fixed && draws[i].id==169));','CHECK(gates100[i]==(fixed && draws[i].id==169));CHECK(gates250[i]==(fixed && draws[i].id==188));')
# Remove irrelevant unused shared509/expectation helpers, preserving other scaffold text.
s=driver.index('static int sprite_for(');e=driver.index('static void check_gates(',s);driver=driver[:s]+driver[e:]
(D/'driver.c').write_text(driver+(S/'test-rear534-original.c').read_text());shutil.copyfile(R/'prototype/test-gem100-original.h',D/'unit.h')
(D/'new_enemy.c').write_text('#include "unit.h"\n#include "new_enemy.inc"\n');(D/'make_enemy.c').write_text('#include "unit.h"\n#include "make_enemy.inc"\n')
basecmd=['gcc','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function','-g','driver.c','new_enemy.c','make_enemy.c','-Wl,--wrap=JE_newEnemy','-Wl,--wrap=JE_makeEnemy'];runs={}
for name,flags in [('optimized',['-O2']),('sanitized',['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
 cmd=basecmd+flags+['-o','unit-'+name];cp=subprocess.run(cmd,cwd=D,capture_output=True);(D/('compile-'+name+'.log')).write_bytes(cp.stdout+cp.stderr);cp.check_returncode()
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1');cp=subprocess.run([str(D/('unit-'+name))],cwd=D,env=env,capture_output=True,timeout=120);(D/('result-'+name+'.log')).write_bytes(cp.stdout+cp.stderr);print(cp.stdout.decode(),end='');cp.check_returncode();runs[name]=json.loads(re.search(r'^RESULT (.*)$',cp.stdout.decode(),re.M)[1])
assert runs['optimized']==runs['sanitized'];assert all((R/f).read_bytes()==c[f] for f in files)
receipt={'status':'PASS','baseline':BASE,'gameplay_runs':0,'production_edits':0,'unit_only':True,'runs':runs,'source_sha256':{f:sha(c[f]) for f in files},'excerpts':manifest,'effect_loop_reference_projection':'remove only five exact existing cash/gem display hooks; selected fixed145 has none','original_data_sha256':{'tyrian.hdt':sha(h),'tyrian1.lvl':sha(lvl)},'selected_record_sources':{str(i):spans[i] for i in selected},'selected_events':events,'scaffold_sha256':{harness.relative_to(R).as_posix():sha(harness.read_bytes()),'prototype/test-gem100-original.h':sha((R/'prototype/test-gem100-original.h').read_bytes())},'unit_source_sha256':{p.name:sha(p.read_bytes()) for p in [S/'test-rear534-original.py',S/'test-rear534-original.c']},'limitations':['Exact extracted original-source unit, not engine/replay/natural runtime proof.','mt_rand uses a counted deterministic stream, not original RNG state.','Text/large explosion/renderer are observation sinks; original power-up, allocation, constructor, collection, event, movement and small-effect logic executes.','Movement extraction ends after original background-y addition; enemy shooting branches are not executed.','No actual rendered pixels, natural projectile dynamics, ancillary hit or source-predicted schedule is tested here.','LeakSanitizer disabled; ASan/UBSan enabled.']}
(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(D/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in sorted(D.iterdir()) if p.is_file() and p.name!='SHA256SUMS'));print('PASS',D/'receipt.json',sha((D/'receipt.json').read_bytes()))
