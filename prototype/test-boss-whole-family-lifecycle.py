#!/usr/bin/env python3
"""Extracted original lifecycle branch fixture, not an engine/gameplay run."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();o=a.out.resolve();assert not o.exists();o.mkdir(parents=True)
s=(R/'src/tyrian2.c').read_text();m=(R/'src/mainint.c').read_text();v=(R/'src/varz.c').read_text()
def balanced(text,start):
 b=text.index('{',start);depth=1;i=b+1
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[start:i]
pstart=s.index('\t\t\t\t\t\tif (armorleft > damage)');projectile=s[pstart:s.index('\n\t\t\t\t\t\tif (infiniteShot)',pstart)]
ram=balanced(m,m.index('\t\t\t\telse if (this_player->invulnerable_ticks == 0 && enemyAvail[z] == 0'))
cycle=balanced(s,s.index('\t\t\t\tif (enemy[i].aniactive == 1)'))
large=balanced(v,v.index('void JE_setupExplosionLarge('))
j=json.loads((R/'assets/hd/artwork/boss-whole-family-v1/proof/source-contract.json').read_text());cs={c['record']:c for c in j['components']};order=j['draw_order_if_all_allocations_succeed']
init=[]
for slot,n in enumerate(order):
 c=cs[n];d=c['source'];pairs={'enemytype':n,'size':d['esize'],'enemyground':1,'explonum':d['explosiontype']>>1,'armorleft':d['armor'] or 255,'edgr':d['dgr'],'edlevel':d['dlevel'],'edani':d['dani'],'edamaged':int(d['dani']<0),'ani':d['ani'],'enemycycle':1,'animin':1,'aniactive':2 if d['animate']==2 else 0,'animax':d['ani']if d['animate']==2 else 0,'aniwhenfire':2 if d['animate']==2 else 0,'linknum':c['spawn_event']['dat4'],'evalue':d['value'],'enemydie':d['eenemydie'],'ex':90+c['assembly_origin'][0],'ey':30+c['assembly_origin'][1]}
 init.append(f' slot_of[{n}]={slot}; enemyAvail[{slot}]={0 if d["armor"] else 2};')
 for k,val in pairs.items():init.append(f' enemy[{slot}].{k}={val};')
 for k,val in enumerate(d['egraphic']):init.append(f' enemy[{slot}].egr[{k}]={val};')
 init.append(f' enemyDat[{n}].esize=1; enemyDat[{n}].explosiontype=36; enemyDat[{n}].value={d["value"]};')
header=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "varz.h"
#include "episodes.h"
#include "player.h"
#include "shots.h"
#define enemy unit_enemy
#define enemyAvail unit_avail
#define enemyDat unit_data
#define player unit_player
#define rep_explosions unit_rep
#define JE_setupExplosion unit_small
#define JE_setupExplosionLarge unit_large
#define JE_playerDamage unit_damage
#define JE_doSP unit_superpixel
#define JE_newEnemy unit_new_enemy
#define JE_eventJump unit_event_jump
#define enemyContinualDamage unit_continual
#define globalFlags unit_flags
#define soundQueue unit_sounds
#define enemyKilled unit_killed
#define cubeMax unit_cubes
#define superEnemy254Jump 0
#define superArcadeMode 0
#define galagaMode false
#define SA_NONE 0
#define S_ENEMY_HIT 1
#define S_EXPLOSION_9 2
#define S_EXPLOSION_8 3
#define S_EXPLOSION_4 4
static JE_MultiEnemyType enemy;
static JE_byte enemyAvail[100];
static JE_EnemyDatType enemyDat;
static Player player[2];
static rep_explosion_type rep_explosions[MAX_REPEATING_EXPLOSIONS];
static int globalFlags[100],soundQueue[8],enemyKilled,cubeMax,small_calls;
static bool enemyContinualDamage;
static int slot_of[66];
static void unit_small(int x,int y,int dy,int type,bool fixed,bool follow)
{(void)x;(void)y;(void)dy;(void)type;(void)fixed;(void)follow;small_calls++;}
static void unit_damage(int amount,Player*p){assert(p->armor>amount);p->armor-=amount;}
static void unit_superpixel(int x,int y,int a,int b,int c){(void)x;(void)y;(void)a;(void)b;(void)c;assert(false);}
static int unit_new_enemy(int a,int b,int c){(void)a;(void)b;(void)c;assert(false);return0;}
static void unit_event_jump(int a){(void)a;assert(false);}
'''.replace('return0','return 0')
wrappers='''
static void projectile_hit(int b,int damage)
{
 assert(enemyAvail[b]==0&&damage>=0&&damage<250&&damage!=99);
 int armorleft=enemy[b].armorleft,temp=enemy[b].linknum?enemy[b].linknum:255;
 int temp2=0,temp3=0,z=0,tempW=0,superArcadePowerUp=0,playerNum=1;
 int tempShotX=enemy[b].ex,tempShotY=enemy[b].ey;
'''+projectile+'''
}
static void body_contact(int z)
{
 Player*this_player=&player[0];int damageRate=2,temp=0,temp2=0,temp3=0,b=0;
 if(false){}
'''+ram+'''
}
static void advance(int i)
{
'''+cycle+'''
}
static void reset(void)
{
 memset(enemy,0,sizeof(enemy));memset(enemyAvail,1,sizeof(enemyAvail));
 memset(enemyDat,0,sizeof(enemyDat));memset(player,0,sizeof(player));
 memset(rep_explosions,0,sizeof(rep_explosions));memset(globalFlags,0,sizeof(globalFlags));
 memset(soundQueue,0,sizeof(soundQueue));enemyKilled=0;cubeMax=0;small_calls=0;
 enemyContinualDamage=true;player[0].armor=255;
'''+ '\n'.join(init)+'''
}
static unsigned visible(int n){int i=slot_of[n];assert(enemy[i].enemycycle>0);return enemy[i].egr[enemy[i].enemycycle-1];}
static void side(int which,int state)
{
 int target=slot_of[which==0?57:59];
 if(state==1)projectile_hit(target,100);
 if(state==2){projectile_hit(target,98);body_contact(target);}
}
'''
tests=r'''
int main(void)
{
 unsigned threshold_cases=0;
 for(int left=0;left<3;left++)for(int right=0;right<3;right++){
  reset();side(0,left);side(1,right);
  assert(enemyAvail[slot_of[61]]==(left?1:2));
  assert(enemyAvail[slot_of[65]]==(right?1:2));
  projectile_hit(slot_of[53],214);
  for(int n=46;n<=65;n++){
   int i=slot_of[n];bool l=n==56||n==57||n==61||n==62;
   bool r=n==59||n==60||n==64||n==65;
   int st=l?left:r?right:0;
   if((l||r)&&st==2){assert(enemyAvail[i]==1);continue;}
   if(n==61||n==65){assert(enemyAvail[i]==1);continue;}
   if(l||r){assert(enemyAvail[i]==(st==1?2:0));assert(enemy[i].edamaged==(st==0));}
   else {assert(enemy[i].armorleft==40);assert(enemy[i].edamaged==(n!=52&&n!=54));}
  }
  assert(enemy[slot_of[52]].enemycycle==2&&enemy[slot_of[54]].enemycycle==2);
  advance(slot_of[52]);advance(slot_of[54]);
  assert(visible(52)==202&&visible(54)==206&&visible(53)==1);
  assert(enemy[slot_of[53]].aniactive==0&&enemy[slot_of[53]].aniwhenfire==0);
  projectile_hit(slot_of[53],40);
  for(int n=46;n<=65;n++)assert(enemyAvail[slot_of[n]]==1);
  assert(cubeMax==1&&player[0].cash==250);threshold_cases++;
 }
 reset();enemyContinualDamage=false;projectile_hit(slot_of[53],214);
 for(int n=56;n<=62;n++)if(n==56||n==57||n==61||n==62){assert(!enemy[slot_of[n]].edamaged);assert(enemyAvail[slot_of[n]]==(n==61?2:0));}
 assert(visible(57)==88&&visible(59)==244&&enemyAvail[slot_of[65]]==1);
 reset();projectile_hit(slot_of[53],212);assert(enemy[slot_of[53]].armorleft==42);
 body_contact(slot_of[53]);assert(enemy[slot_of[53]].armorleft==40&&!enemy[slot_of[53]].edamaged&&visible(52)==50);
 projectile_hit(slot_of[53],1);assert(enemy[slot_of[53]].armorleft==39&&enemy[slot_of[53]].edamaged);
 projectile_hit(slot_of[53],38);assert(enemy[slot_of[53]].armorleft==1);
 bool active_before[100];for(int i=0;i<100;i++)active_before[i]=enemyAvail[i]!=1;
 body_contact(slot_of[53]);for(int n=46;n<=65;n++){assert(enemyAvail[slot_of[n]]==1);if(active_before[slot_of[n]])assert(enemy[slot_of[n]].linknum==0);}
 assert(cubeMax==0&&player[0].cash==0);
 reset();int center=slot_of[53];assert(visible(53)==1&&enemy[center].aniactive==2);
 enemy[center].aniactive=1;for(int k=2;k<=8;k++){advance(center);assert(enemy[center].enemycycle==k);}
 assert(enemy[center].aniactive==2);advance(center);assert(enemy[center].enemycycle==8);
 enemy[center].aniactive=1;advance(center);assert(enemy[center].enemycycle==1);
 /* Explicit partial-spawn fixture: only the first lower row is available.
  * Other source records occupy fixture storage but are marked unavailable;
  * the extracted branch must not touch them. Actual construction/event
  * scheduling and JE_makeEnemy are deliberately outside this unit. */
 reset();for(int i=5;i<20;i++)enemyAvail[i]=1;enemyContinualDamage=false;
 struct JE_SingleEnemyType before[100];memcpy(before,enemy,sizeof(enemy));
 projectile_hit(slot_of[63],214);assert(enemy[slot_of[63]].edamaged);
 for(int i=5;i<100;i++){assert(enemyAvail[i]==1);assert(memcmp(&before[i],&enemy[i],sizeof(enemy[i]))==0);}
 puts("PASS original extracted projectile/ram/cycle/large-admission branches: nine side-state thresholds, main linked removals, early continual-damage asymmetry, partial allocation active-only scope, negative-dani and center pause/wrap");
 printf("threshold_cases=%u; game_runs=0; captures=0; large_effect_creation_original=true; child_effect_tick_loop_not_executed=true\n",threshold_cases);
 return0;
}
'''.replace('return0','return 0')
source=header+large+'\n'+wrappers+tests;(o/'lifecycle.c').write_text(source)
flags=subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True).split()
cmd=['cc','-std=c99','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(R/'src'),*flags,str(o/'lifecycle.c'),'-o',str(o/'lifecycle')]
build=subprocess.run(cmd,capture_output=True,text=True);(o/'build.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
run=subprocess.run([str(o/'lifecycle')],capture_output=True,text=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'});(o/'run.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout+run.stderr
sha=lambda b:hashlib.sha256(b).hexdigest()
receipt={'status':'PASS','unit_kind':'Extracted original source blocks with synthetic source-record fixtures; no game run','threshold_combinations':9,'partial_spawn_guard':'All unavailable fixture records byte-equal before/after; constructor/event scheduler not executed','sanitizers':'ASan+UBSan; leak detection disabled for ptrace environment (fixture uses static storage)','source_fragments_sha256':{k:sha(x.encode())for k,x in{'projectile':projectile,'ram':ram,'cycle':cycle,'large_explosion_creation':large}.items()},'source_files_sha256':{n:sha((R/'src'/n).read_bytes())for n in['tyrian2.c','mainint.c','varz.c']},'harness_sha256':sha(source.encode()),'game_runs':0,'captures':0,'limits':['JE_makeEnemy and original event scheduler not executed; normal-difficulty record initialization is explicit','JE_playerDamage/JE_setupExplosion leaves are recorders; no claim about player-death or full effect tick lifecycle','Shot decode/flight/collision targeting/filter setup are outside extracted branch; no artificial input authorization inferred','Center triggers are explicit fixture inputs; launch success/failure remains source review and later census']};(o/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(run.stdout);print(json.dumps(receipt,indent=2))
