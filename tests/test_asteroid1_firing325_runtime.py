#!/usr/bin/env python3
"""Explicit-input extracted-production record325 binding and integrity tests.

Reads the named ten-family harness, named production renderer/family/struct
sources, sixteen named peer preflight includes, three HDAs and external
tyrian.hdt/newshs.shp and production mtrand.c/config.h. No test discovery, broad repository scan, private projection input, game launch or external upload.
Generated outputs are bounded to 16 MiB. Runtime is bounded to 512 MiB RSS;
ASan's large virtual shadow is permitted, while compiler address space is 1 GiB.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import resource
import re
import signal
import struct
import subprocess
import time

MIB = 1024 ** 2
OUTPUT_LIMIT = 16 * MIB
DEFAULT_REPO = Path(__file__).resolve().parents[1]
PEERS = [('ten', 'asteroid1'), ('four', 'asteroid4'),
         ('common4', 'asteroid_common4'), ('random5', 'asteroid_random5'),
         ('goldwing', 'goldwing'), ('random43', 'asteroid_random43'),
         ('random85', 'asteroid_random85'), ('random123', 'asteroid_random123'),
         ('random95', 'asteroid_random95'), ('random114', 'asteroid_random114'),
         ('random133', 'asteroid_random133'), ('random152', 'asteroid_random152'),
         ('random286', 'asteroid_random286'), ('fork284', 'fork284'), ('capsule545', 'capsule545'), ('paired287_288', 'paired287_288')]

MAIN = r'''

static unsigned cold_record_mutations,warm_record_mutations;
static G101EnemyContext context(unsigned slot,unsigned type)
{return (G101EnemyContext){type,slot,0,1,false,false,false,false};}
static void actor(Sprite2_array *bank,unsigned slot,unsigned type,unsigned link)
{
 struct JE_SingleEnemyType *e=&enemy[slot];memset(e,0,sizeof(*e));enemyAvail[slot]=0;
 e->enemytype=type;e->enemydatofs=&enemyDat[type];e->sprite2s=bank;e->size=1;
 e->linknum=link;e->armorleft=10;e->ani=8;e->animin=1;e->enemycycle=1;
 e->aniactive=2;e->animax=8;e->aniwhenfire=2;e->exrev=e->eyrev=100;e->explonum=12;
 e->tur[0]=145;e->freq[0]=28;e->eshotwait[0]=20;e->eshotwait[1]=e->eshotwait[2]=255;
 e->xminbounce=e->yminbounce=-10000;e->xmaxbounce=e->ymaxbounce=10000;
 memcpy(e->egr,enemyDat[type].egraphic,sizeof(e->egr));e->ex=106;e->ey=87;
}
static unsigned selected_base(const G101EnemyContext *c)
{
 if(c&&c->type==325&&c->pool_slot<100) {
  unsigned cycle=enemy[c->pool_slot].enemycycle;
  if(cycle>=1&&cycle<=8)return enemy[c->pool_slot].egr[cycle-1];
 }
 return 277;
}
static bool draw(Sprite2_array source,const G101EnemyContext *c)
{return firing325_draw(&surface,100,80,source,selected_base(c),0,0,c);}

#include <math.h>
#define ENEMY_SHOT_MAX 60
@SHOT_STRUCT@
JE_WeaponType weapons[WEAP_NUM+1];
static EnemyShotType enemyShot[ENEMY_SHOT_MAX];
static JE_boolean enemyShotAvail[ENEMY_SHOT_MAX];
static JE_byte soundQueue[8],temp,temp2,temp3;
static int b,tempMapXOfs,tempBackMove,backMove,difficultyLevel;
static unsigned galagaShotFreq;
static unsigned enemyOnScreen;
static struct {int x,y,x_velocity;bool is_alive;} player[2];
static bool mirror_calls;
static unsigned classic_calls,fire_comparisons,hd_fire_calls,hd_cycles,hd_holds,hd_bases;
static void JE_setupExplosion(int x,int y,int dy,int kind,bool fixed,bool follow)
{(void)x;(void)y;(void)dy;(void)kind;(void)fixed;(void)follow;assert(!"unexpected non-record325 explosion");}
static void blit_enemy(SDL_Surface *screen,int i,int dx,int dy,int part)
{
 struct JE_SingleEnemyType before=enemy[i];EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(shots,enemyShot,sizeof(shots));
 JE_boolean avail[ENEMY_SHOT_MAX];memcpy(avail,enemyShotAvail,sizeof(avail));JE_byte sounds[8];memcpy(sounds,soundQueue,8);
 uint64_t rng_before=mt_state_fingerprint();unsigned base=enemy[i].egr[enemy[i].enemycycle-1];classic_calls++;
 if(mirror_calls) {
  G101EnemyContext c=context((unsigned)i,325);
  int x=enemy[i].ex+enemy[i].mapoffset+dx,y=enemy[i].ey+dy;
  bool expected=x>=0&&x<=308&&y>=-13&&y<=199;
  assert(firing325_draw(screen,x,y,*enemy[i].sprite2s,base,part,enemy[i].filter,&c)==expected);assert(!reject_reason);
  if(expected){hd_fire_calls++;hd_cycles|=1U<<(enemy[i].enemycycle-1);if(enemy[i].aniactive==2)hd_holds|=1U<<(enemy[i].enemycycle-1);
   hd_bases|=base==11?1U:base==125?2U:4U;}
 }
 assert(!memcmp(&before,&enemy[i],sizeof(before))&&!memcmp(shots,enemyShot,sizeof(shots))&&
  !memcmp(avail,enemyShotAvail,sizeof(avail))&&!memcmp(sounds,soundQueue,8)&&mt_state_fingerprint()==rng_before);
}
@ENGINE_DRAW@
static void weapon_record(const char *path)
{
 FILE *f=fopen(path,"rb");assert(f);Uint8 b[80];assert(fread(b,1,80,f)==80&&fgetc(f)==EOF);fclose(f);
 assert(asteroid1_stamp(b,80)==UINT64_C(0x387b219ee9cab017));
 JE_WeaponType *w=&weapons[145];unsigned p=0;
#define B(v) w->v=b[p++]
#define S(v) w->v=(int8_t)b[p++]
#define W(v) do{w->v=b[p]|((unsigned)b[p+1]<<8);p+=2;}while(0)
 W(drain);B(shotrepeat);B(multi);W(weapani);B(max);B(tx);B(ty);B(aim);
 for(unsigned i=0;i<8;i++){B(attack[i]);}for(unsigned i=0;i<8;i++){B(del[i]);}
 for(unsigned i=0;i<8;i++){S(sx[i]);}for(unsigned i=0;i<8;i++){S(sy[i]);}
 for(unsigned i=0;i<8;i++){S(bx[i]);}for(unsigned i=0;i<8;i++){S(by[i]);}
 for(unsigned i=0;i<8;i++){W(sg[i]);}S(acceleration);S(accelerationx);B(circlesize);B(sound);B(trail);B(shipblastfilter);
#undef B
#undef S
#undef W
 assert(p==80&&w->multi==1&&w->max==1&&w->weapani==2&&w->sg[0]==112&&w->aim==3&&w->sound==13);
}
struct FireTrace {
 struct JE_SingleEnemyType actor;
 EnemyShotType shots[ENEMY_SHOT_MAX];JE_boolean available[ENEMY_SHOT_MAX];JE_byte sounds[8];
 uint64_t rng;unsigned onscreen,calls;
};
static struct FireTrace traces[2][36];
static void original_fire_checks(Sprite2_array source)
{
 /* Two complete executions of the extracted original draw/fire path: original
  * classic calls versus those same calls with observational production mirror. */
 for(unsigned difficulty=0;difficulty<=10;difficulty++)for(unsigned scenario=0;scenario<13;scenario++) {
  for(unsigned run=0;run<2;run++) {
   memset(traces[run],0,sizeof(traces[run]));memset(enemyAvail,1,sizeof(enemyAvail));actor(&source,25,325,0);
   memset(enemyShot,0,sizeof(enemyShot));memset(enemyShotAvail,1,sizeof(enemyShotAvail));memset(soundQueue,0,sizeof(soundQueue));
   memset(player,0,sizeof(player));player[0].x=160;player[0].y=140;player[0].is_alive=true;
   temp=temp2=temp3=0;b=0;tempMapXOfs=0;tempBackMove=0;backMove=0;galagaShotFreq=0;difficultyLevel=difficulty;
   enemyOnScreen=classic_calls=0;mirror_calls=run;mt_srand(0x325145UL);reject_reason=NULL;
   struct JE_SingleEnemyType *e=&enemy[25];
   if(scenario==1){memset(enemyShotAvail,0,sizeof(enemyShotAvail));e->eshotwait[0]=1;}
   if(scenario==2){e->iced=3;e->eshotwait[0]=1;}
   if(scenario==3){e->aniactive=1;e->enemycycle=3;e->iced=3;e->eshotwait[0]=1;}
   if(scenario==4){e->aniactive=1;e->enemycycle=3;e->eshotwait[0]=1;}
   if(scenario==5){e->enemycycle=8;e->eshotwait[0]=1;}
   if(scenario==6){e->ex=-29;e->eshotwait[0]=1;}
   if(scenario==7){e->ex=-28;e->aniactive=1;e->eshotwait[0]=1;}
   if(scenario==8){e->ey=-30;e->aniactive=1;e->eshotwait[0]=1;}
   if(scenario==9){e->ex=300;e->aniactive=1;e->eshotwait[0]=1;}
   if(scenario==10){memset(enemyShotAvail,0,sizeof(enemyShotAvail));enemyShotAvail[59]=1;e->eshotwait[0]=1;}
   if(scenario==12){e->ex=299;e->aniactive=1;e->eshotwait[0]=1;}
   if(scenario==11){tempMapXOfs=19;tempBackMove=1;e->ex=263;e->aniactive=1;e->eshotwait[0]=1;}
   for(unsigned tick=0;tick<36;tick++) {
    mirror_logic_tick++;engine_draw_enemy(50);struct FireTrace *t=&traces[run][tick];
    t->actor=enemy[25];memcpy(t->shots,enemyShot,sizeof(enemyShot));memcpy(t->available,enemyShotAvail,sizeof(enemyShotAvail));
    memcpy(t->sounds,soundQueue,8);t->rng=mt_state_fingerprint();t->onscreen=enemyOnScreen;t->calls=classic_calls;
    if(run){assert(!memcmp(t,&traces[0][tick],sizeof(*t)));fire_comparisons++;}
   }
  }
  struct FireTrace *first=&traces[1][0];unsigned cooldown=difficulty<=2?28:difficulty<=7?15:8;
  if(scenario==0){assert(first->actor.aniactive==2&&first->actor.enemycycle==1&&first->actor.eshotwait[0]==19);
   assert(traces[1][19].actor.aniactive==1&&traces[1][19].actor.enemycycle==1);
   assert(traces[1][20].actor.enemycycle==2&&traces[1][26].actor.enemycycle==8&&traces[1][26].actor.aniactive==2);}
  if(scenario==1){assert(first->actor.aniactive==2&&first->actor.enemycycle==1&&first->actor.eshotwait[0]==cooldown&&first->rng==traces[1][35].rng);}
  if(scenario==2){assert(first->actor.aniactive==2&&first->actor.enemycycle==1&&first->actor.eshotwait[0]==1&&first->actor.iced==2);}
  if(scenario==3){assert(first->actor.aniactive==1&&first->actor.enemycycle==4&&first->actor.eshotwait[0]==1);}
  if(scenario==4){assert(first->actor.aniactive==1&&first->actor.enemycycle==4&&first->actor.eshotwait[0]==cooldown);}
  if(scenario==5){assert(first->actor.aniactive==1&&first->actor.enemycycle==8&&traces[1][1].actor.enemycycle==1);}
  if(scenario==6||scenario==9){assert(first->actor.enemycycle==1&&first->actor.eshotwait[0]==1&&first->calls==0);}
  if(scenario==7){assert(first->actor.enemycycle==2&&first->actor.eshotwait[0]==1);}
  if(scenario==12){assert(first->actor.enemycycle==2&&first->actor.eshotwait[0]==1&&first->calls==4);}
  if(scenario==8){assert(first->actor.enemycycle==2&&first->calls==0&&first->actor.eshotwait[0]==cooldown);}
  if(scenario==10){assert(!first->available[59]&&first->shots[59].sgr==112&&first->shots[59].animax==2&&first->shots[59].sdmg==2&&first->shots[59].duration==255);}
  if(scenario==4||scenario==5||scenario==8||scenario==10||scenario==11) {
   unsigned shot=scenario==10?59:0;assert(first->shots[shot].sgr==112&&first->shots[shot].animax==2);
   assert(first->shots[shot].sy==first->actor.ey-10&&first->shots[shot].sx==first->actor.ex+tempMapXOfs);
  }
 }
 assert(fire_comparisons==11*13*36&&hd_fire_calls>0&&hd_cycles==255&&hd_holds==129&&hd_bases==7);
 printf("production HD callback admissions: %u; cyclemask=%u; heldmask=%u; basemask=%u\n",hd_fire_calls,hd_cycles,hd_holds,hd_bases);mirror_calls=false;actor(&source,25,325,0);
 printf("production fire comparisons: %u ticks, 11 difficulties, 13 hold/full-pool/ice/running/wrap/offscreen/last-slot/scroll scenarios; exact actor/cooldown/multipos/shot/sound/MT RNG equality\n",fire_comparisons);
}

static void exact_record_guards(Sprite2_array source)
{
 G101EnemyContext c=context(25,325);actor(&source,25,325,0);
 /* Each of all 77 serialized bytes is independently changed both before any
  * accepted quadrant in a new tick, and after a valid first quadrant. */
 for(unsigned t=325;t<=325;t++) {
#define MUTATE(v) do { \
  for(unsigned bit_=1;bit_<=(sizeof(enemyDat[t].v)==2?256U:1U);bit_*=256U) { \
   mirror_logic_tick++;unsigned a_=accepted,r_=rejected; \
   enemyDat[t].v^=bit_;assert(!firing325_source(source));assert(!draw(source,&c)); \
   assert(accepted==a_&&rejected==r_&&!reject_reason); \
   enemyDat[t].v^=bit_;assert(firing325_source(source));cold_record_mutations++; \
   assert(draw(source,&c));a_=accepted;r_=rejected; \
   enemyDat[t].v^=bit_;assert(!firing325_draw(&surface,112,80,source,277,1,0,&c)); \
   assert(accepted==a_&&rejected==r_+1&&reject_reason&&strstr(reject_reason,"integrity")); \
   enemyDat[t].v^=bit_;assert(firing325_source(source));assert(!draw(source,&c)); \
   assert(accepted==a_&&rejected==r_+1);reject_reason=NULL;warm_record_mutations++; \
  } \
 } while(0)
 MUTATE(ani);for(unsigned i=0;i<3;i++)MUTATE(tur[i]);for(unsigned i=0;i<3;i++)MUTATE(freq[i]);
 MUTATE(xmove);MUTATE(ymove);MUTATE(xaccel);MUTATE(yaccel);MUTATE(xcaccel);MUTATE(ycaccel);
 MUTATE(startx);MUTATE(starty);MUTATE(startxc);MUTATE(startyc);MUTATE(armor);MUTATE(esize);
 for(unsigned i=0;i<20;i++)MUTATE(egraphic[i]);
 MUTATE(explosiontype);MUTATE(animate);MUTATE(shapebank);MUTATE(xrev);MUTATE(yrev);MUTATE(dgr);
 MUTATE(dlevel);MUTATE(dani);MUTATE(elaunchfreq);MUTATE(elaunchtype);MUTATE(value);MUTATE(eenemydie);
#undef MUTATE
 }
 assert(cold_record_mutations==77&&warm_record_mutations==77);
}
static void source_guards(Sprite2_array source)
{
 Uint8 *raw=source.data,*rebound=malloc(source.size);assert(rebound);memcpy(rebound,raw,source.size);
 Sprite2_array alternate={source.size,rebound};G101EnemyContext c=context(25,325);
 assert(source.data!=firing325_source_snapshot.bytes);
 assert(!firing325_source((Sprite2_array){source.size,NULL}));
 assert(!firing325_source((Sprite2_array){source.size-1,raw}));
 assert(!firing325_source((Sprite2_array){source.size+1,raw}));
 assert(!firing325_source(alternate));
 spriteSheet8=alternate;assert(!firing325_source(alternate));
 enemySpriteSheets[0]=alternate;assert(!firing325_source(alternate));
 memset(&spriteSheet8,0,sizeof(spriteSheet8));assert(firing325_source(alternate));
 assert(!firing325_source(source));actor(&alternate,25,325,0);
 const unsigned offsets[]={0,200,46565};
 for(unsigned i=0;i<3;i++) {
  mirror_logic_tick++;unsigned before=rejected;
  rebound[offsets[i]]^=1;assert(!firing325_source(alternate));assert(!draw(alternate,&c));assert(rejected==before&&!reject_reason);
  rebound[offsets[i]]^=1;assert(draw(alternate,&c));before=rejected;
  rebound[offsets[i]]^=1;assert(!firing325_draw(&surface,112,80,alternate,277,1,0,&c));
  assert(rejected==before+1&&reject_reason);rebound[offsets[i]]^=1;reject_reason=NULL;
 }
 enemySpriteSheets[0]=source;actor(&source,25,325,0);free(rebound);assert(firing325_source(source));
 for(unsigned slot=0;slot<4;slot++) {
  memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
  enemySpriteSheets[slot]=source;enemySpriteSheetIds[slot]=23;assert(firing325_source(source));
  enemySpriteSheetIds[slot]=17;assert(!firing325_source(source));enemySpriteSheetIds[slot]=23;
  enemySpriteSheets[slot].size--;assert(!firing325_source(source));enemySpriteSheets[slot].size++;
 }
 memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
 enemySpriteSheets[0]=source;enemySpriteSheetIds[0]=23;
 spriteSheet8=source;assert(!firing325_source(source));memset(&spriteSheet8,0,sizeof(spriteSheet8));
 /* Same-address live mutation must not inherit snapshot or previous-draw trust. */
 for(unsigned i=0;i<3;i++) {
  mirror_logic_tick++;unsigned before=rejected;raw[offsets[i]]^=1;
  assert(!firing325_source(source));assert(!draw(source,&c));assert(rejected==before&&!reject_reason);
  raw[offsets[i]]^=1;assert(draw(source,&c));before=rejected;raw[offsets[i]]^=1;
  assert(!firing325_draw(&surface,112,80,source,277,1,0,&c));assert(rejected==before+1&&reject_reason);
  raw[offsets[i]]^=1;reject_reason=NULL;assert(firing325_source(source));
 }
 /* A cold corrupt source cannot initialize a trusted private snapshot. */
 firing325_source_snapshot.valid=false;raw[200]^=1;assert(!firing325_source(source));assert(!firing325_source_snapshot.valid);
 raw[200]^=1;assert(firing325_source(source));assert(firing325_source_snapshot.valid);
}


static void geometry_and_animation(Sprite2_array source)
{
 const int parts[]={0,1,19,20};const unsigned slots[]={25,49};
 assert(sizeof(firing325_pins)/sizeof(*firing325_pins)==1);
 assert(sizeof(firing325_images)/sizeof(*firing325_images)==3);
 for(unsigned s=0;s<2;s++)for(unsigned active_state=1;active_state<=2;active_state++)for(unsigned cycle=1;cycle<=8;cycle++) {
  actor(&source,slots[s],325,0);G101EnemyContext c=context(slots[s],325);
  struct JE_SingleEnemyType *e=&enemy[slots[s]];e->filter=17;e->enemycycle=cycle;e->aniactive=active_state;
  bool valid=(active_state==1&&cycle<8)||(active_state==2&&(cycle==1||cycle==8));
  unsigned base=selected_base(&c);
  for(unsigned p=0;p<4;p++) {
   int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
   assert(firing325_draw(&surface,100+px,80+py,source,base,part,17,&c)==valid);
   if(valid){assert(last_x==100&&last_y==80&&last_part_x==px&&last_part_y==py&&last_filter==17);
    assert(last_asset==&firing325_resources.member[base==11?0:base==125?1:2]);}
  }
 }
 actor(&source,25,325,0);G101EnemyContext c=context(25,325);struct JE_SingleEnemyType *e=&enemy[25];
 for(unsigned armor=1;armor<=255;armor++){e->armorleft=armor;assert(draw(source,&c));}
 const int values[]={-32768,-1,0,20,32767};for(unsigned i=0;i<5;i++){e->evalue=values[i];assert(draw(source,&c));}
 for(unsigned ice=0;ice<=255;ice++){e->iced=ice;assert(draw(source,&c));}
 for(unsigned wait=0;wait<=255;wait++){e->eshotwait[0]=wait;e->eshotmultipos[0]=wait;assert(draw(source,&c));}
 const unsigned scrolls[]={0,1,12,125};for(unsigned i=0;i<4;i++){e->mapoffset=scrolls[i];e->ex=106-(int)scrolls[i];assert(draw(source,&c));}
 /* Neither failed neighbor allocation nor independent culling changes admission. */
 memset(enemyAvail,1,sizeof(enemyAvail));actor(&source,49,325,0);c=context(49,325);assert(draw(source,&c));
 enemy[25].ey=-80;assert(draw(source,&c));actor(&source,25,325,0);
}
static void partial_geometry(Sprite2_array source)
{
 const int origins[][2]={{-6,80},{302,80},{100,-20},{100,-13},{100,190},{100,199}};
 const int parts[]={0,1,19,20};
 for(unsigned type=325;type<=325;type++)for(unsigned i=0;i<sizeof(origins)/sizeof(*origins);i++) {
  actor(&source,25,type,0);G101EnemyContext c=context(25,type);
  enemy[25].ex=origins[i][0]+6;enemy[25].ey=origins[i][1]+7;
  /* Preserve the original quadrant-local scope at partially clipped edges. */
  for(unsigned f=0;f<3;f++) {
   const int filters[]={0,17,255};enemy[25].filter=filters[f];
   for(unsigned p=0;p<4;p++) {
    int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
    int x=origins[i][0]+px,y=origins[i][1]+py;
    bool expected=x>=0&&x<=308&&y>=-13&&y<=199;
    unsigned a=accepted,l=logged;
    assert(firing325_draw(&surface,x,y,source,selected_base(&c),part,filters[f],&c)==expected);
    assert(accepted-a==(unsigned)expected&&logged-l==(unsigned)expected);
    if(expected)assert(last_x==origins[i][0]&&last_y==origins[i][1]&&
     last_part_x==px&&last_part_y==py&&last_filter==filters[f]);
   }
  }
 }
 actor(&source,25,325,0);
}
static void warm_frame_guard(Sprite2_array source)
{
 const int parts[]={0,1,19,20};
 for(unsigned type=325;type<=325;type++) {
  actor(&source,25,type,0);G101EnemyContext c=context(25,type);mirror_logic_tick++;
  assert(draw(source,&c));unsigned a=accepted,r=rejected,base=selected_base(&c);
  enemyDat[325].value^=1;
  assert(!firing325_draw(&surface,112,80,source,base,1,0,&c));
  assert(accepted==a&&rejected==r+1&&reject_reason&&!strcmp(reject_reason,"firing325-family-integrity"));
  enemyDat[325].value^=1;assert(firing325_source(source));
  for(unsigned p=0;p<4;p++) {
   int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
   assert(!firing325_draw(&surface,100+px,80+py,source,base,part,0,&c));
  }
  assert(accepted==a&&rejected==r+1);
  mirror_logic_tick++;reject_reason=NULL;assert(draw(source,&c));
  /* A resource-selection failure after an accepted component invalidates the
   * frame, including its previously accepted partner/quadrants. */
  const char *root=game_probe_assets;game_probe_assets="/foreign-firing325-resource-root";
  a=accepted;r=rejected;assert(!draw(source,&c));assert(accepted==a&&rejected==r+1&&reject_reason);
  game_probe_assets=root;assert(!draw(source,&c));
  mirror_logic_tick++;reject_reason=NULL;assert(draw(source,&c));
 }
 actor(&source,25,325,0);
}

static void peer_state(bool expected)
{for(unsigned i=0;i<16;i++)assert(peer_ready[i]()==expected);}
static void independent_fallback(void)
{
 peer_state(true);assert(firing325_family_ready());
 for(unsigned member=0;member<3;member++) {
  mirror_logic_tick++;firing325_resources.member[member].rgba[10]^=1;
  assert(!firing325_family_ready());peer_state(true);
  firing325_resources.member[member].rgba[10]^=1;assert(!firing325_family_ready());
  firing325_shutdown();assert(firing325_family_ready());peer_state(true);
 }
 for(unsigned i=0;i<16;i++)peer_asset[i]->rgba[10]^=1;
 mirror_logic_tick++;peer_state(false);assert(firing325_family_ready());
 for(unsigned i=0;i<16;i++)peer_asset[i]->rgba[10]^=1;
 peer_state(false);assert(firing325_family_ready());
 for(unsigned i=0;i<16;i++)peer_shutdown[i]();
 peer_state(true);assert(firing325_family_ready());
 for(unsigned i=0;i<16;i++)peer_shutdown[i]();
}
static void actor_guards(Sprite2_array source)
{
 for(unsigned type=325;type<=325;type++) {
 G101EnemyContext c=context(25,type);actor(&source,25,type,0);
#define DECLINE assert(!draw(source,&c))
#define LIVE(field,value) do{struct JE_SingleEnemyType old=enemy[25];enemy[25].field=value;DECLINE;enemy[25]=old;}while(0)
#define CTX(field,value) do{G101EnemyContext old=c;c.field=value;DECLINE;c=old;}while(0)
 for(unsigned i=0;i<20;i++){unsigned old=enemy[25].egr[i];enemy[25].egr[i]=999;DECLINE;enemy[25].egr[i]=old;}
 LIVE(enemytype,324);LIVE(enemydatofs,NULL);LIVE(enemydatofs,&enemyDat[286]);LIVE(sprite2s,NULL);
 LIVE(size,0);LIVE(size,2);LIVE(scoreitem,true);LIVE(edamaged,true);LIVE(armorleft,0);
 LIVE(ani,0);LIVE(ani,7);LIVE(enemycycle,0);LIVE(enemycycle,9);
 LIVE(aniactive,0);LIVE(aniactive,3);LIVE(animin,0);LIVE(animin,2);LIVE(animax,7);LIVE(aniwhenfire,1);LIVE(filter,1);
 LIVE(tur[0],59);LIVE(tur[1],1);LIVE(tur[2],1);LIVE(freq[0],27);LIVE(freq[1],1);LIVE(freq[2],1);
 LIVE(launchfreq,1);LIVE(launchtype,532);LIVE(launchspecial,1);LIVE(edgr,1);LIVE(edlevel,1);LIVE(edani,1);
 LIVE(enemydie,1);LIVE(enemydie,512);LIVE(enemydie,611);LIVE(enemyground,true);LIVE(explonum,13);
 LIVE(exc,1);LIVE(eyc,-1);LIVE(fixedmovey,1);LIVE(excc,1);LIVE(eycc,-1);LIVE(xaccel,1);LIVE(yaccel,1);
 LIVE(exrev,0);LIVE(eyrev,0);LIVE(ex,107);LIVE(ey,88);LIVE(mapoffset,1);
 for(unsigned link=1;link<=255;link++)LIVE(linknum,link);
 Sprite2_array wrong={source.size-1,source.data};LIVE(sprite2s,&wrong);
 wrong=(Sprite2_array){source.size,firing325_source_snapshot.bytes};LIVE(sprite2s,&wrong);
 CTX(type,324);CTX(type,326);
 const unsigned badslots[]={0,24,50,74,75,99,100,UINT_MAX};
 for(unsigned s=0;s<sizeof(badslots)/sizeof(*badslots);s++)CTX(pool_slot,badslots[s]);
 CTX(availability,1);CTX(availability,2);CTX(availability,UINT_MAX);CTX(size,0);CTX(size,2);
 CTX(score_item,true);CTX(damaged,true);CTX(static_animation,true);CTX(independent_motion,true);
 enemyAvail[25]=1;DECLINE;enemyAvail[25]=2;DECLINE;enemyAvail[25]=0;assert(!draw(source,NULL));
 unsigned base=selected_base(&c);
 const unsigned badbases[]={0,10,12,124,126,276,278,112,113};
 for(unsigned i=0;i<sizeof(badbases)/sizeof(*badbases);i++)assert(!firing325_draw(&surface,100,80,source,badbases[i],0,0,&c));
 for(unsigned state=0;state<=3;state++)for(unsigned cycle=0;cycle<=9;cycle++) {
  enemy[25].aniactive=state;enemy[25].enemycycle=cycle;
  bool legal=(state==1&&cycle>=1&&cycle<=7)||(state==2&&(cycle==1||cycle==8));
  assert(draw(source,&c)==legal);
  if(legal)for(unsigned wrong=0;wrong<3;wrong++) {
   const unsigned bases[]={11,125,277};if(bases[wrong]!=selected_base(&c))
    assert(!firing325_draw(&surface,100,80,source,bases[wrong],0,0,&c));
  }
 }
 actor(&source,25,325,0);base=selected_base(&c);
 const int badparts[]={INT_MIN,-1,2,18,21,INT_MAX};
 for(unsigned i=0;i<sizeof(badparts)/sizeof(*badparts);i++)assert(!firing325_draw(&surface,100,80,source,base,badparts[i],0,&c));
 assert(!firing325_draw(&surface,100,80,source,base,0,-1,&c));assert(!firing325_draw(&surface,100,80,source,base,0,256,&c));
 const int badx[]={INT_MIN,-1,309,INT_MAX},bady[]={INT_MIN,-14,200,INT_MAX};
 for(unsigned i=0;i<4;i++){assert(!firing325_draw(&surface,badx[i],80,source,base,0,0,&c));assert(!firing325_draw(&surface,100,bady[i],source,base,0,0,&c));}
#undef CTX
#undef LIVE
#undef DECLINE
 }
 actor(&source,25,325,0);
}
static void display_guards(Sprite2_array source)
{
 G101EnemyContext c=context(25,325);actor(&source,25,325,0);
#define DECLINE assert(!draw(source,&c))
 bool *excluded[]={&xmas,&isNetworkGame,&twoPlayerMode,&galagaMode,&twoPlayerLinked,&record_demo,&onePlayerAction,&superTyrian,&timedBattleMode,&bonusLevel,&normalBonusLevelCurrent,&bonusLevelCurrent,&play_demo};
 for(unsigned i=0;i<sizeof(excluded)/sizeof(*excluded);i++){*excluded[i]=true;DECLINE;*excluded[i]=false;}
 lvlFileNum=2;DECLINE;lvlFileNum=9;DECLINE;lvlFileNum=15;DECLINE;lvlFileNum=1;episodeNum=2;DECLINE;episodeNum=1;
 asteroid_hd_enabled=false;DECLINE;asteroid_hd_enabled=true;asteroid_hd_lease=false;DECLINE;asteroid_hd_lease=true;
 superArcadeMode=1;DECLINE;superArcadeMode=0;active=false;DECLINE;active=true;
 reject_reason="other-render-rejection";DECLINE;reject_reason=NULL;game_probe_scene_assets=0;DECLINE;game_probe_scene_assets=1;
 SDL_Surface old=surface,other=surface;SDL_PixelFormat oldf=format;
 surface.pixels=NULL;DECLINE;surface=old;surface.w=321;DECLINE;surface=old;surface.h=201;DECLINE;surface=old;
 surface.pitch=321;DECLINE;surface=old;surface.format=NULL;DECLINE;surface=old;
 format.format=SDL_PIXELFORMAT_RGBA8888;DECLINE;format=oldf;format.BitsPerPixel=32;DECLINE;format=oldf;format.BytesPerPixel=4;DECLINE;format=oldf;
 game_screen=NULL;DECLINE;game_screen=&surface;VGAScreen=NULL;DECLINE;VGAScreen=&surface;
 assert(!firing325_draw(NULL,100,80,source,277,0,0,&c));assert(!firing325_draw(&other,100,80,source,277,0,0,&c));
 /* Probe lease bypass is restricted to the same exact level scope. */
 game_probe_enabled=true;asteroid_hd_lease=false;assert(draw(source,&c));
 lvlFileNum=2;DECLINE;lvlFileNum=1;game_probe_enabled=false;asteroid_hd_lease=true;
 assert(draw(source,&c));
#undef DECLINE
}
static void resource_guards(void)
{
 const char *root=game_probe_assets;
 game_probe_assets=NULL;assert(!firing325_family_ready());game_probe_assets="";assert(!firing325_family_ready());
 char longroot[1025];memset(longroot,'x',sizeof(longroot)-1);longroot[sizeof(longroot)-1]=0;
 game_probe_assets=longroot;assert(!firing325_family_ready());game_probe_assets="/foreign-firing325-root";assert(!firing325_family_ready());game_probe_assets=root;
 game_probe_density=4;assert(!firing325_family_ready());game_probe_density=0;assert(!firing325_family_ready());game_probe_density=8;
 game_probe_missing=true;assert(!firing325_family_ready());game_probe_missing=false;
 game_probe_invalid=true;assert(!firing325_family_ready());game_probe_invalid=false;
 game_probe_original_reference=true;assert(!firing325_family_ready());game_probe_original_reference=false;
 assert(firing325_family_ready());
 for(unsigned member=0;member<3;member++) {
#define BAD_ASSET(field,value) do{Asset old=firing325_resources.member[member];mirror_logic_tick++;firing325_resources.member[member].field=value;assert(!firing325_family_ready());firing325_resources.member[member]=old;assert(!firing325_family_ready());firing325_shutdown();assert(firing325_family_ready());}while(0)
 BAD_ASSET(initialized,false);BAD_ASSET(valid,false);BAD_ASSET(bank,101);BAD_ASSET(index,123);BAD_ASSET(w,12);BAD_ASSET(h,14);
 BAD_ASSET(anchor_x,1);BAD_ASSET(anchor_y,1);BAD_ASSET(density,4);BAD_ASSET(rgba,NULL);
#undef BAD_ASSET
 mirror_logic_tick++;firing325_resources.member[member].rgba[10]^=1;assert(!firing325_family_ready());
 firing325_resources.member[member].rgba[10]^=1;assert(!firing325_family_ready());firing325_shutdown();assert(firing325_family_ready());
 }
}

int main(int argc,char **argv)
{
 assert(argc==6);assert(sizeof(paired287_288_pins)/sizeof(*paired287_288_pins)==2);assert(!asteroid1_source_bytes_match(NULL,0));game_probe_assets=argv[3];records(argv[2]);weapon_record(argv[5]);
 FILE *f=fopen(argv[1],"rb");assert(f);Uint8 *raw=malloc(46566);
 assert(raw&&fread(raw,1,46566,f)==46566&&fgetc(f)==EOF);fclose(f);
 enemySpriteSheets[0]=(Sprite2_array){46566,raw};enemySpriteSheetIds[0]=23;Sprite2_array source=enemySpriteSheets[0];
 assert(firing325_source(source)&&asteroid1_scope());actor(&source,25,325,0);G101EnemyContext c=context(25,325);
 if(!strcmp(argv[4],"reject")||!strcmp(argv[4],"peers-only")) {
  if(!strcmp(argv[4],"peers-only"))peer_state(true);
  assert(!firing325_family_ready());assert(!draw(source,&c));assert(!accepted&&!rejected);
  for(unsigned type=325;type<=325;type++) {
   actor(&source,25,type,0);c=context(25,type);assert(!draw(source,&c));
  }
  firing325_shutdown();for(unsigned i=0;i<16;i++)peer_shutdown[i]();
  free(raw);puts("firing325 invalid member keeps whole family classic; peers independent");return 0;
 }
 assert(!strcmp(argv[4],"accept")||!strcmp(argv[4],"own-only"));assert(firing325_family_ready());
 if(!strcmp(argv[4],"accept"))independent_fallback();else {peer_state(false);for(unsigned i=0;i<16;i++)peer_shutdown[i]();}
 exact_record_guards(source);original_fire_checks(source);source_guards(source);geometry_and_animation(source);
 partial_geometry(source);warm_frame_guard(source);actor_guards(source);display_guards(source);resource_guards();
 firing325_shutdown();free(raw);
 puts("firing325 all77 cold+warm bytes; pool25-49 link0; all callback states; production fire/RNG; geometry, live/display/loader integrity passed");return 0;
}
'''


def run_bounded(command, log, *, compiler=False, sanitize=False):
    ceiling = (1024 if compiler else 512) * MIB

    def limits():
        resource.setrlimit(resource.RLIMIT_FSIZE, (OUTPUT_LIMIT, OUTPUT_LIMIT))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        if compiler or not sanitize:
            resource.setrlimit(resource.RLIMIT_AS, (ceiling, ceiling))

    with log.open('wb') as stream:
        proc = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=0',
                                     'UBSAN_OPTIONS': 'halt_on_error=1:print_stacktrace=1'},
                                preexec_fn=limits, start_new_session=True)
        peak = 0
        deadline = time.monotonic() + (90 if compiler else 15)
        try:
            while True:
                pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
                if pid:
                    proc.returncode = os.waitstatus_to_exitcode(status)
                    peak = max(peak, usage.ru_maxrss * 1024)
                    if peak > ceiling:
                        raise RuntimeError('subprocess exceeded RSS bound')
                    break
                if time.monotonic() > deadline:
                    raise RuntimeError('bounded subprocess timed out')
                statusfile = Path('/proc') / str(proc.pid) / 'status'
                try:
                    for line in statusfile.read_text().splitlines():
                        if line.startswith('VmRSS:'):
                            peak = max(peak, int(line.split()[1]) * 1024)
                            if peak > ceiling:
                                raise RuntimeError('subprocess exceeded RSS bound')
                            break
                except FileNotFoundError:
                    pass
                if log.stat().st_size > OUTPUT_LIMIT:
                    raise RuntimeError('subprocess log exceeded output bound')
                time.sleep(0.01)
            if proc.returncode:
                raise RuntimeError(f'Command failed ({proc.returncode}); inspect {log}')
        finally:
            if proc.returncode is None:
                os.killpg(proc.pid, signal.SIGKILL)
                _, status, _ = os.wait4(proc.pid, 0)
                proc.returncode = os.waitstatus_to_exitcode(status)
    return peak


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=DEFAULT_REPO)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--sdl-include', action='append', default=[])
    p.add_argument('--sanitize', action='store_true', help='Also compile and run ASan+UBSan')
    a = p.parse_args()
    root = a.repo.resolve()
    a.out = a.out.resolve()
    a.out.mkdir(parents=True, exist_ok=True)
    if any(a.out.iterdir()):
        raise RuntimeError('Select a new, empty output directory')
    output_files = []

    def remember(path):
        output_files.append(path)
        return path

    def output_bound():
        total = sum(path.stat().st_size for path in output_files if path.is_file() and not path.is_symlink())
        if total > OUTPUT_LIMIT:
            raise RuntimeError('Generated output exceeds 16 MiB')
        return total

    helper = root / 'tests/test_asteroid1_ten_assets.py'
    source_path = root / 'src/render_mirror.c'
    family_path = root / 'src/asteroid1_firing325_mirror.inc'
    shared_path = root / 'src/asteroid1_ten_mirror.inc'
    struct_path = root / 'src/varz.h'
    engine_path = root / 'src/tyrian2.c'
    rng_path = root / 'src/mtrand.c'
    config_path = root / 'src/config.h'
    snapshot_path = root / 'src/asteroid1_source_snapshot.inc'
    pack = root / 'assets/hd/packs/asteroid1-ten-v1'
    arts = [pack / f'enemy-newshs-{base}-8.hda' for base in (11,125,277)]
    peer_paths = [root / 'src' / f'asteroid1_{name}_mirror.inc' for name, _ in PEERS]
    allowlist = {helper, source_path, family_path, shared_path, struct_path, snapshot_path, engine_path, rng_path, config_path,
                 *arts, a.data / 'tyrian.hdt', a.data / 'newshs.shp', *peer_paths}

    def read(path, binary=False):
        if path not in allowlist:
            raise RuntimeError('Input outside explicit allowlist')
        return path.read_bytes() if binary else path.read_text()

    import shutil
    if shutil.disk_usage(a.out).free < 5_000_000_000:
        raise RuntimeError('At least 5 GB free is required')
    payloads = [read(art, True) for art in arts]
    for base, payload in zip((11,125,277), payloads):
        if len(payload) != 172060 or struct.unpack_from('<4s6I', payload) != (b'HDR1',1080000+base,8,24,28,0,0):
            raise RuntimeError('Unexpected firing installation resource header or size')
    spec = importlib.util.spec_from_file_location('firing325_named_ten_harness', helper)
    ten = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ten)
    source, family, shared, varz = read(source_path), read(family_path), read(shared_path), read(struct_path)
    assert 'firing325_shutdown();' in ten.extract(source, 'render_mirror_hud_shutdown')
    assert 'return firing325_draw(' in ten.extract(source, 'render_mirror_enemy_tile')
    start = varz.index('struct JE_SingleEnemyType\n{')
    end = varz.index('\n};', start) + 3
    structcode = varz[start:end] + '\nstatic struct JE_SingleEnemyType enemy[100];\nstatic unsigned char enemyAvail[100];\n'
    prefix = ten.HARNESS.split('int main(int argc', 1)[0].replace('t=444;t<=453', 't=325;t<=325')
    prefix = prefix.replace('static Uint8 last_filter;', 'static Uint8 last_filter;static Asset *last_asset;')
    prefix = prefix.replace('accepted++;last_x=x;', 'last_asset=a;accepted++;last_x=x;')
    prefix = prefix.replace('assert(a&&a->bank==108', 'assert(a&&(a->index==11||a->index==125||a->index==277)&&a->w==24&&a->h==28&&part&&part->w==12&&part->h==14&&a->bank==108')
    scopes = ten.extract(source, 'asteroid1_level_scope') + ten.extract(source, 'asteroid1_scope')
    common = ten.extract(shared, 'asteroid1_stamp') + '#include "asteroid1_source_snapshot.inc"\n' + ten.extract(shared, 'asteroid1_record_stamp')
    peer_code, peer_bases = '', set()
    for (_, peer), path in zip(PEERS, peer_paths):
        text = read(path)
        pins = re.search(r'static const struct \{[^\n]+\} ' + peer + r'_pins\[\d+\]=\{.*?\n\};', text, re.S)
        resources = re.search(r'static struct \{[^\n]+\} ' + peer + r'_resources;', text)
        if not pins or not resources:
            raise RuntimeError('Unexpected peer preflight declarations: ' + peer)
        images = re.search(r'static const struct \{[^\n]+\} ' + peer + r'_images\[\d+\]=\{.*?\n\};', text, re.S)
        peer_code += pins.group() + '\n' + (images.group()+'\n' if images else '') + resources.group() + '\n'
        for function in ['shutdown', 'load', 'family_ready']:
            peer_code += ten.extract(text, peer + '_' + function)
        peer_bases.update(int(base) for base in (re.findall(r'\{(\d+),', images.group()) if images else re.findall(r'\{\d+,(\d+),', pins.group())))
    if len(peer_bases) != 38:
        raise RuntimeError('Unexpected existing peer image closure')
    peer_code += 'static bool (*peer_ready[])(void)={' + ','.join(peer + '_family_ready' for _, peer in PEERS) + '};\n'
    peer_code += 'static void (*peer_shutdown[])(void)={' + ','.join(peer + '_shutdown' for _, peer in PEERS) + '};\n'
    peer_code += 'static Asset *peer_asset[]={' + ','.join('&' + peer + '_resources.member[0]' for _, peer in PEERS) + '};\n'
    engine = read(engine_path)
    engine_draw = ten.extract(engine.replace('void JE_drawEnemy(int enemyOffset) // actually does a whole lot more than just drawing', 'void JE_drawEnemy(int enemyOffset)'), 'JE_drawEnemy')
    engine_draw = engine_draw[:engine_draw.index('\t\t\t/* Enemy Launch Routine */')] + '\n draw_enemy_end:;\n }\n }\n player[0].x += 25;\n}\n'
    engine_draw = engine_draw.replace('void JE_drawEnemy(', 'static void engine_draw_enemy(')
    shot_end = varz.index('} EnemyShotType;') + len('} EnemyShotType;')
    shot_start = varz.rindex('typedef struct {', 0, shot_end)
    config = read(config_path)
    difficulty = config[config.rindex('enum\n{',0,config.index('DIFFICULTY_WIMP')):config.index('};',config.index('DIFFICULTY_WIMP'))+2]
    original = MAIN.replace('@SHOT_STRUCT@', varz[shot_start:shot_end]).replace('@ENGINE_DRAW@', difficulty+'\n'+engine_draw)
    # Entire production MT implementation is used; no mock RNG substitutions.
    code = prefix.replace('@SCOPE@', scopes).replace('@FAMILY@', structcode + common + family + peer_code + read(rng_path)) + original
    harness = remember(a.out / 'harness.c')
    harness.write_text(code)
    raw = read(a.data / 'tyrian.hdt', True)
    off = struct.unpack_from('<i', raw)[0] + 14 + 1638*80 + 61*82 + 55*37 + 7*37 + 19*41 + 38*86 + 12*37
    weapon = remember(a.out / 'original145-weapon.bin')
    weapon_off = struct.unpack_from('<i', raw)[0] + 14 + 145*80
    weapon.write_bytes(raw[weapon_off:weapon_off+80])
    record = remember(a.out / 'original325-record.bin')
    record.write_bytes(raw[off+325*77:off+326*77])
    if record.stat().st_size != 77:
        raise RuntimeError('Short original record325')
    fixtures = a.out / 'fixtures'
    fixtures.mkdir()
    variants = []
    kinds = ['missing','payload','magic','role','foreign-base','density','width','height',
             'anchor-x','anchor-y','header-short','short','extra','fifo','directory','broken-symlink']
    for n, (art, payload, kind) in enumerate((art,payload,kind) for art,payload in zip(arts,payloads) for kind in kinds):
        d = fixtures / f'{n:02d}-{art.stem}-{kind}'
        d.mkdir()
        for sibling in arts:
            if sibling != art:
                (d / sibling.name).symlink_to(sibling)
        dest = d / art.name
        if kind == 'missing':
            pass
        elif kind == 'fifo':
            os.mkfifo(dest)
        elif kind == 'directory':
            dest.mkdir()
        elif kind == 'broken-symlink':
            dest.symlink_to(d / 'absent.hda')
        else:
            b = bytearray(payload)
            if kind == 'payload': b[40] ^= 1
            elif kind == 'magic': b[:4] = b'NOPE'
            elif kind == 'foreign-base': struct.pack_into('<I', b, 4, 1080123)
            elif kind == 'header-short': b = b[:12]
            elif kind == 'short': b = b[:-1]
            elif kind == 'extra': b += b'X'
            else: struct.pack_into('<I', b, dict(role=4,density=8,width=12,height=16,**{'anchor-x':20,'anchor-y':24})[kind], 1)
            remember(dest).write_bytes(b)
        variants.append(d)
    isolated = fixtures / 'isolated-own-family'
    isolated.mkdir()
    for art in arts:
        (isolated / art.name).symlink_to(art)
    peer_only = fixtures / 'isolated-previous-families'
    peer_only.mkdir()
    for base in sorted(peer_bases):
        name = f'enemy-newshd-{base}-8.hda'
        (peer_only / name).symlink_to(pack / name)
    flags = ['-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I'+str(root/'src')]
    flags += ['-I'+x for x in a.sdl_include]
    if not a.sdl_include:
        flags += subprocess.check_output(['pkg-config','--cflags','sdl2'], text=True).split()
    runs = []
    compiler_peak = runtime_peak = 0
    output_bound()
    for mode in ['optimized'] + (['asan-ubsan'] if a.sanitize else []):
        exe = remember(a.out / mode)
        compiler = ['cc',*flags,'-O2'] + (['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g'] if mode == 'asan-ubsan' else [])
        compiler_peak = max(compiler_peak, run_bounded([*compiler,str(harness),'-lm','-o',str(exe)], remember(a.out / f'{mode}-compile.log'), compiler=True))
        output_bound()
        for i, (directory, expected) in enumerate([(pack,'accept'),(isolated,'own-only'),(peer_only,'peers-only')] + [(d,'reject') for d in variants]):
            runtime_peak = max(runtime_peak, run_bounded([str(exe),str(a.data/'newshs.shp'),str(record),str(directory),expected,str(weapon)], remember(a.out / f'{mode}-{i:02d}.log'), sanitize=mode == 'asan-ubsan'))
            output_bound()
        admission = re.search(r'production HD callback admissions: (\d+); cyclemask=(\d+); heldmask=(\d+); basemask=(\d+)', (a.out/f'{mode}-00.log').read_text())
        if not admission or tuple(map(int,admission.groups()[1:])) != (255,129,7):
            raise RuntimeError('Missing complete original-fire HD admission coverage')
        runs.append(dict(mode=mode,positive=2,peer_independence=1,negative=len(variants),original_fire_HD_admissions=int(admission[1]),binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    result = dict(records=[325],bases=[11,125,277],logical_size=[24,28],density=8,
                  cold_source_record_byte_mutations=77,warm_source_record_byte_mutations=77,
                  boundary_pool_slots=[25,49],accepted_links=[0],
                  cycles=list(range(1,9)),held_cycles=[1,8],bright125_cycles=[4,5],
                  original_fire_tick_comparisons=5148,original_fire_scenarios=13,original_fire_HD_accepted_all_cycles=True,difficulties=list(range(11)),
                  independent_actors=True,positive_armor_values=255,ice_values=256,
                  clipping_origins=6,clipping_filters=[0,17,255],fixture_count=len(variants),
                  independent_peer_families=16,sticky_whole_frame=True,
                  compiler_peak_rss_bytes=compiler_peak,runtime_peak_rss_bytes=runtime_peak,
                  compiler_address_space_limit_bytes=1024*MIB,runtime_rss_limit_bytes=512*MIB,
                  output_limit_bytes=OUTPUT_LIMIT,output_bytes=output_bound(),runs=runs,
                  source_sha256=hashlib.sha256(family.encode()).hexdigest(),
                  engine_draw_sha256=hashlib.sha256(engine_draw.encode()).hexdigest(),
                  production_rng_sha256=hashlib.sha256(read(rng_path).encode()).hexdigest(),leak_sanitizer=False,
                  scope='Extracted production guards and JE_drawEnemy pre-launch animation/fire block with production MT RNG. Actual-engine event/destruction validation remains separate.')
    receipt = remember(a.out / 'receipt.json')
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    output_bound()
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
