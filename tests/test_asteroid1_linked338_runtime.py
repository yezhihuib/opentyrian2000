#!/usr/bin/env python3
"""Bounded extracted-production NEWSHP338..342 installation lifecycle tests.

Reads only explicitly named renderer/engine sources, the named ten/ember harness
helpers, eight NEWSHP HDR1 files and tyrian.hdt/tyrian1.lvl/newshp.shp inputs.
No discovery, private projection, game launch, publication or original edits.
Compiler AS<=1GiB, runtime RSS<=512MiB, each log<=16MiB, free reserve>=5GB.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import resource
import signal
import time
import shutil
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASES=(115,117,119,121,229,231,267,269)
MIB=1024**2
OUTPUT_LIMIT=32*MIB

MAIN=r'''
#include <math.h>
@PLAYER_SHOT_STRUCT@
#define MAX_PWEAPON 81
#include "sndmast.h"
#define ENEMY_SHOT_MAX 60
#define MAX_EXPLOSIONS 200
#define MAX_REPEATING_EXPLOSIONS 20
@SHOT_STRUCT@
@EXPLOSION_STRUCTS@
JE_WeaponType weapons[WEAP_NUM+1];
static EnemyShotType enemyShot[ENEMY_SHOT_MAX];
static JE_boolean enemyShotAvail[ENEMY_SHOT_MAX];
static PlayerShotDataType playerShotData[MAX_PWEAPON+1];
static JE_byte shotAvail[MAX_PWEAPON];
static Explosion explosions[MAX_EXPLOSIONS];
static rep_explosion_type rep_explosions[MAX_REPEATING_EXPLOSIONS];
static JE_byte soundQueue[8],temp,temp2,temp3,doIced;
static int b,tempMapXOfs,tempBackMove,backMove,backMove2,backMove3,difficultyLevel;
static int mapX,mapX3,background3x1,background3x1b;
static bool smallEnemyAdjust,infiniteShot,enemyContinualDamage;
static unsigned galagaShotFreq,enemyOnScreen,totalEnemy,enemyKilled,cubeMax;
static unsigned superEnemy254Jump,superArcadePowerUp,tempW;
static struct {unsigned link_num,color;} boss_bar[2];
static bool globalFlags[10];
static struct {int x,y,x_velocity,cash;bool is_alive;} player[2];
Sprite2_array spriteSheet10,spriteSheet11;
@EVENT_STRUCT@
static struct JE_EventRecType eventRec[6];
static unsigned eventLoc;
static bool mirror_calls;
static unsigned classic_calls,hd_calls,hd_cycles,hd_bases,animation_comparisons,allocation_cases,damage_cases,collision_hits;
static unsigned cold_record_mutations,warm_record_mutations;
@EXPLOSIONS@
@ENGINE_CONSTRUCTOR@
@ENGINE_EVENTS@
static G101EnemyContext context(unsigned slot,unsigned type)
{struct JE_SingleEnemyType *e=&enemy[slot];return (G101EnemyContext){type,slot,enemyAvail[slot],e->size,e->scoreitem,e->edamaged,
 e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel,
 e->ani==1&&e->enemycycle==1&&e->aniactive==0};}
static void actor(Sprite2_array *bank,unsigned slot,unsigned type,unsigned link)
{
 memset(&enemy[slot],0,sizeof(enemy[slot]));enemyAvail[slot]=engine_make_enemy(&enemy[slot],type,0);
 struct JE_SingleEnemyType *e=&enemy[slot];(void)bank;e->linknum=link;e->ex=106;e->ey=87;e->enemycycle=1;
}
static unsigned selected_base(const G101EnemyContext *c)
{if(c&&c->type>=338&&c->type<=342&&c->pool_slot<100&&enemy[c->pool_slot].enemycycle>=1&&enemy[c->pool_slot].enemycycle<=20)
 return enemy[c->pool_slot].egr[enemy[c->pool_slot].enemycycle-1];return 115;}
static bool checked_draw(SDL_Surface *screen,int x,int y,Sprite2_array source,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 struct JE_SingleEnemyType actors[100];memcpy(actors,enemy,sizeof(actors));
 unsigned char avail[100];memcpy(avail,enemyAvail,sizeof(avail));
 EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(shots,enemyShot,sizeof(shots));
 JE_boolean shot_avail[ENEMY_SHOT_MAX];memcpy(shot_avail,enemyShotAvail,sizeof(shot_avail));
 PlayerShotDataType pshots[MAX_PWEAPON+1];memcpy(pshots,playerShotData,sizeof(pshots));
 JE_byte pavail[MAX_PWEAPON],sounds[8];memcpy(pavail,shotAvail,sizeof(pavail));memcpy(sounds,soundQueue,8);
 uint64_t rng=mt_state_fingerprint();bool result=linked338_draw(screen,x,y,source,base,part,filter,c);
 assert(!memcmp(actors,enemy,sizeof(actors))&&!memcmp(avail,enemyAvail,sizeof(avail))&&!memcmp(shots,enemyShot,sizeof(shots))&&
 !memcmp(shot_avail,enemyShotAvail,sizeof(shot_avail))&&!memcmp(pshots,playerShotData,sizeof(pshots))&&
 !memcmp(pavail,shotAvail,sizeof(pavail))&&!memcmp(sounds,soundQueue,8)&&mt_state_fingerprint()==rng);return result;
}
static bool draw(Sprite2_array source,const G101EnemyContext *c)
{return checked_draw(&surface,100,80,source,selected_base(c),0,0,c);}
static void blit_enemy(SDL_Surface *screen,int i,int dx,int dy,int part)
{
 unsigned base=enemy[i].egr[enemy[i].enemycycle-1];classic_calls++;
 if(mirror_calls) {
  G101EnemyContext c=context((unsigned)i,enemy[i].enemytype);int x=enemy[i].ex+tempMapXOfs+dx,y=enemy[i].ey+dy;
  bool expected=x>=0&&x<=308&&y>=-13&&y<=199;
  assert(checked_draw(screen,x,y,*enemy[i].sprite2s,base,part,enemy[i].filter,&c)==expected);assert(!reject_reason);
  if(expected){hd_calls++;if(c.type==338&&enemyAvail[i]==0)hd_cycles|=1U<<(enemy[i].enemycycle-1);
   for(unsigned k=0;k<8;k++)if(base==(unsigned)linked338_images[k].base)hd_bases|=1U<<k;}
 }
}
@ENGINE_DRAW@
static void game_probe_collision(const char *kind,int shot,int slot,int damage)
{(void)kind;(void)shot;(void)slot;(void)damage;collision_hits++;}
static void JE_eventJump(unsigned jump){(void)jump;assert(!"unexpected link254 jump");}
static void JE_doSP(int x,int y,int a,int z,int filter){(void)x;(void)y;(void)a;(void)z;(void)filter;assert(!"unexpected invulnerable actor");}
#define SHOT_MISC 0
static unsigned shotMultiPos[1];static int mouseX,mouseY;
static JE_integer player_shot_create(JE_word portnum,uint bay,JE_word x,JE_word y,JE_word mx,JE_word my,JE_word weapon,JE_byte playernum)
{(void)portnum;(void)bay;(void)x;(void)y;(void)mx;(void)my;(void)weapon;(void)playernum;assert(!"unexpected drop or chain");return 0;}
static void engine_player_collision(int tempShotX,int tempShotY,int damage)
{
 int z=0;bool is_special=false;JE_byte chain=0,playerNum=1;JE_word tempX2=0,tempY2=0;int zinglonDuration=0;
 @ENGINE_COLLISION@
 draw_player_shot_loop_end:;
}
@ENGINE_HOMING@
@ENGINE_REPEATING@
static void clear_engine(void)
{
 memset(enemy,0,sizeof(enemy));memset(enemyAvail,1,sizeof(enemyAvail));memset(enemyShot,0,sizeof(enemyShot));memset(enemyShotAvail,1,sizeof(enemyShotAvail));
 memset(playerShotData,0,sizeof(playerShotData));memset(shotAvail,0,sizeof(shotAvail));memset(explosions,0,sizeof(explosions));memset(rep_explosions,0,sizeof(rep_explosions));
 memset(soundQueue,0,sizeof(soundQueue));memset(player,0,sizeof(player));memset(boss_bar,0,sizeof(boss_bar));memset(globalFlags,0,sizeof(globalFlags));
 player[0].x=160;player[0].y=140;player[0].is_alive=true;temp=temp2=temp3=doIced=0;b=0;tempMapXOfs=tempBackMove=backMove=backMove2=backMove3=0;
 mapX=1;mapX3=0;background3x1=background3x1b=0;smallEnemyAdjust=false;galagaShotFreq=0;enemyOnScreen=classic_calls=totalEnemy=enemyKilled=cubeMax=collision_hits=0;
 infiniteShot=enemyContinualDamage=false;superEnemy254Jump=superArcadePowerUp=tempW=0;reject_reason=NULL;mirror_logic_tick++;
}
static void load_events(const char *path)
{
 FILE *f=fopen(path,"rb");assert(f);
 for(unsigned k=0;k<6;k++){Uint8 raw[11];assert(fread(raw,1,11,f)==11);eventRec[k]=(struct JE_EventRecType){word(raw),raw[2],(int16_t)word(raw+3),(int16_t)word(raw+5),(int8_t)raw[7],(int8_t)raw[8],(int8_t)raw[9],raw[10]};}
 assert(fgetc(f)==EOF);fclose(f);
 const unsigned times[]={3968,3968,5256,5256,6488,6488},xs[]={66,66,42,42,162,162},links[]={23,23,29,29,33,33};
 for(unsigned k=0;k<6;k++)assert(eventRec[k].eventtime==times[k]&&eventRec[k].eventtype==(k%2?12:6)&&eventRec[k].eventdat==(k%2?339:338)&&eventRec[k].eventdat2==(int)xs[k]&&eventRec[k].eventdat4==links[k]&&eventRec[k].eventdat5==(k%2?0:-56)&&!eventRec[k].eventdat3&&!eventRec[k].eventdat6);
}
static void install(unsigned site)
{assert(site<3);eventLoc=site*2+1;engine_event();eventLoc++;engine_event();}
struct Trace {
 struct JE_SingleEnemyType actors[100];unsigned char avail[100];EnemyShotType shots[ENEMY_SHOT_MAX];JE_boolean shot_avail[ENEMY_SHOT_MAX];
 PlayerShotDataType player_shots[MAX_PWEAPON+1];JE_byte player_avail[MAX_PWEAPON],sounds[8];Explosion explosions[MAX_EXPLOSIONS];rep_explosion_type repeating[MAX_REPEATING_EXPLOSIONS];
 uint64_t rng;unsigned total,killed,onscreen,calls,hits;int cash;
};
static void trace(struct Trace *t)
{
 memset(t,0,sizeof(*t));memcpy(t->actors,enemy,sizeof(enemy));memcpy(t->avail,enemyAvail,sizeof(enemyAvail));memcpy(t->shots,enemyShot,sizeof(enemyShot));memcpy(t->shot_avail,enemyShotAvail,sizeof(enemyShotAvail));
 memcpy(t->player_shots,playerShotData,sizeof(playerShotData));memcpy(t->player_avail,shotAvail,sizeof(shotAvail));memcpy(t->sounds,soundQueue,8);memcpy(t->explosions,explosions,sizeof(explosions));memcpy(t->repeating,rep_explosions,sizeof(rep_explosions));
 t->rng=mt_state_fingerprint();t->total=totalEnemy;t->killed=enemyKilled;t->onscreen=enemyOnScreen;t->calls=classic_calls;t->hits=collision_hits;t->cash=player[0].cash;
}
static void exact_record_guards(Sprite2_array source)
{
 struct JE_SingleEnemyType fixtures[8];const unsigned types[]={338,338,338,338,341,342,339,340},cycles[]={1,4,7,1,1,1,1,1};
 for(unsigned k=0;k<8;k++){actor(&source,25,types[k],23);enemy[25].enemycycle=cycles[k];fixtures[k]=enemy[25];}
 clear_engine();difficultyLevel=2;install(0);tempBackMove=1;for(unsigned tick=0;tick<120;tick++)engine_draw_enemy(50);tempBackMove=0;
 shotAvail[0]=1;engine_player_collision(enemy[26].ex+enemy[26].mapoffset,enemy[26].ey-6,enemy[26].armorleft);assert(enemyAvail[25]==2);fixtures[3]=enemy[25];
 fixtures[3].ex=106;fixtures[3].ey=87;fixtures[3].mapoffset=0;
 for(unsigned k=0;k<8;k++){enemy[25]=fixtures[k];enemyAvail[25]=k==3?2:0;G101EnemyContext c=context(25,types[k]);assert(draw(source,&c));}
 for(unsigned t=338;t<=342;t++) {
#define MUTATE(v) do {for(unsigned bit_=1;bit_<=(sizeof(enemyDat[t].v)==2?256U:1U);bit_*=256U) { \
 mirror_logic_tick++;unsigned a_=accepted,r_=rejected;enemyDat[t].v^=bit_;assert(!linked338_source(source)); \
 for(unsigned member_=0;member_<8;member_++){enemy[25]=fixtures[member_];enemyAvail[25]=member_==3?2:0;G101EnemyContext c_=context(25,types[member_]);assert(!draw(source,&c_));} \
 assert(accepted==a_&&rejected==r_&&!reject_reason);enemyDat[t].v^=bit_;assert(linked338_source(source));cold_record_mutations++; \
 actor(&source,25,338,23);G101EnemyContext c_=context(25,338);assert(draw(source,&c_));a_=accepted;r_=rejected;enemyDat[t].v^=bit_; \
 assert(!checked_draw(&surface,112,80,source,115,1,0,&c_));assert(accepted==a_&&rejected==r_+1&&reject_reason&&strstr(reject_reason,"integrity")); \
 for(unsigned member_=0;member_<8;member_++){enemy[25]=fixtures[member_];enemyAvail[25]=member_==3?2:0;c_=context(25,types[member_]);assert(!draw(source,&c_));} \
 enemyDat[t].v^=bit_;assert(linked338_source(source));assert(!draw(source,&c_));assert(accepted==a_&&rejected==r_+1);reject_reason=NULL;warm_record_mutations++;}}while(0)
 MUTATE(ani);for(unsigned i=0;i<3;i++)MUTATE(tur[i]);for(unsigned i=0;i<3;i++)MUTATE(freq[i]);
 MUTATE(xmove);MUTATE(ymove);MUTATE(xaccel);MUTATE(yaccel);MUTATE(xcaccel);MUTATE(ycaccel);MUTATE(startx);MUTATE(starty);MUTATE(startxc);MUTATE(startyc);MUTATE(armor);MUTATE(esize);
 for(unsigned i=0;i<20;i++)MUTATE(egraphic[i]);MUTATE(explosiontype);MUTATE(animate);MUTATE(shapebank);MUTATE(xrev);MUTATE(yrev);MUTATE(dgr);MUTATE(dlevel);MUTATE(dani);MUTATE(elaunchfreq);MUTATE(elaunchtype);MUTATE(value);MUTATE(eenemydie);
#undef MUTATE
 }
 assert(cold_record_mutations==385&&warm_record_mutations==385);
}
static void actor_guards(Sprite2_array source)
{
 const unsigned slots[]={25,49},links[]={23,29,33};
 for(unsigned type=338;type<=342;type++)for(unsigned s=0;s<2;s++)for(unsigned l=0;l<3;l++){
  actor(&source,slots[s],type,links[l]);G101EnemyContext c=context(slots[s],type);assert(draw(source,&c));
  for(unsigned cycle=1;cycle<=(type==338?12U:1U);cycle++){enemy[slots[s]].enemycycle=cycle;assert(draw(source,&c));}
 }
 for(unsigned type=338;type<=342;type++) {
 actor(&source,25,type,23);G101EnemyContext c=context(25,type);
#define DECLINE assert(!draw(source,&c))
#define LIVE(field,value) do{struct JE_SingleEnemyType old=enemy[25];enemy[25].field=value;DECLINE;enemy[25]=old;}while(0)
#define CTX(field,value) do{G101EnemyContext old=c;c.field=value;DECLINE;c=old;}while(0)
 for(unsigned i=0;i<20;i++)LIVE(egr[i],999);
 LIVE(enemytype,337);LIVE(enemydatofs,NULL);LIVE(enemydatofs,&enemyDat[337]);LIVE(sprite2s,NULL);LIVE(size,0);LIVE(size,2);LIVE(scoreitem,true);LIVE(special,true);LIVE(edamaged,true);LIVE(armorleft,0);
 LIVE(ani,0);LIVE(ani,type==338?11:2);LIVE(enemycycle,0);LIVE(enemycycle,type==338?13:2);LIVE(aniactive,type==338?0:1);LIVE(aniactive,2);LIVE(aniactive,3);
 LIVE(animin,0);LIVE(animin,2);LIVE(animax,1);LIVE(aniwhenfire,1);LIVE(filter,1);LIVE(edgr,type==338?120:121);LIVE(edlevel,type==338?0:-1);LIVE(edani,1);
 LIVE(launchfreq,1);LIVE(launchtype,532);LIVE(launchspecial,1);LIVE(enemydie,1);LIVE(enemyground,true);LIVE(explonum,13);
 LIVE(exc,1);LIVE(eyc,-1);LIVE(fixedmovey,1);LIVE(excc,1);LIVE(eycc,-1);LIVE(xaccel,1);LIVE(yaccel,1);LIVE(exrev,0);LIVE(eyrev,0);LIVE(ex,107);LIVE(ey,88);LIVE(mapoffset,1);
 for(unsigned i=0;i<3;i++){LIVE(tur[i],1);LIVE(freq[i],1);}
 for(unsigned link=0;link<=255;link++)if(link!=23&&link!=29&&link!=33)LIVE(linknum,link);
 Sprite2_array wrong={source.size-1,source.data};LIVE(sprite2s,&wrong);wrong=(Sprite2_array){source.size,linked338_source_snapshot.bytes};LIVE(sprite2s,&wrong);wrong=(Sprite2_array){source.size,source.data};LIVE(sprite2s,&wrong);
 CTX(type,337);CTX(type,343);const unsigned badslots[]={0,24,50,74,75,99,100,UINT_MAX};for(unsigned s=0;s<8;s++)CTX(pool_slot,badslots[s]);
 CTX(availability,1);CTX(availability,2);CTX(availability,UINT_MAX);CTX(size,0);CTX(size,2);CTX(score_item,true);CTX(damaged,true);CTX(static_animation,type==338);CTX(independent_motion,true);
 enemyAvail[25]=1;DECLINE;enemyAvail[25]=2;DECLINE;enemyAvail[25]=0;assert(!draw(source,NULL));

 for(unsigned state=0;state<4;state++)for(unsigned cycle=0;cycle<=13;cycle++){
  struct JE_SingleEnemyType saved=enemy[25];enemy[25].aniactive=state;enemy[25].enemycycle=cycle;
  bool legal=type==338?(state==1&&cycle>=1&&cycle<=12):(state==0&&cycle==1);assert(draw(source,&c)==legal);enemy[25]=saved;
 }
 if(type!=338){struct JE_SingleEnemyType saved=enemy[25];G101EnemyContext old=c;enemyAvail[25]=2;enemy[25].edamaged=true;c.availability=2;c.damaged=true;DECLINE;enemy[25]=saved;enemyAvail[25]=0;c=old;}
 for(unsigned armor=1;armor<=255;armor++){enemy[25].armorleft=armor;assert(draw(source,&c));}
 const int values[]={-32768,-1,0,20,32767};for(unsigned k=0;k<5;k++){enemy[25].evalue=values[k];assert(draw(source,&c));}
 for(unsigned v=0;v<=255;v++){enemy[25].iced=v;enemy[25].eshotwait[0]=v;enemy[25].eshotmultipos[0]=v;enemy[25].launchwait=v;assert(draw(source,&c));}
 unsigned base=selected_base(&c);for(unsigned k=0;k<8;k++)if(base!=(unsigned)linked338_images[k].base)assert(!checked_draw(&surface,100,80,source,linked338_images[k].base,0,0,&c));
 const int badparts[]={INT_MIN,-1,2,18,21,INT_MAX};for(unsigned k=0;k<6;k++)assert(!checked_draw(&surface,100,80,source,base,badparts[k],0,&c));
 assert(!checked_draw(&surface,100,80,source,base,0,-1,&c));assert(!checked_draw(&surface,100,80,source,base,0,256,&c));
#undef CTX
#undef LIVE
#undef DECLINE
 }
}
static void production_animation(Sprite2_array source)
{
 static struct Trace traces[2][32];const unsigned seq[]={115,115,115,117,117,117,119,119,119,117,117,117};
 const int xs[]={106,-29,-28,299,300,-48,-47,280,281};const int ys[]={87,-27,-26,-25,-14,-13,-12,181,182,190,191,-113,-112};
 for(unsigned type=338;type<=342;type++)for(unsigned scenario=0;scenario<31;scenario++)for(unsigned run=0;run<2;run++) {
  clear_engine();difficultyLevel=2;mt_srand(0x338UL);mirror_calls=run;uint64_t before=mt_state_fingerprint();
  assert(engine_new_enemy(25,type,0)==26);struct JE_SingleEnemyType *e=&enemy[25];assert(before!=mt_state_fingerprint());uint64_t rng=mt_state_fingerprint();
  assert(e->enemytype==type&&e->enemydatofs==&enemyDat[type]&&e->sprite2s==&enemySpriteSheets[0]&&e->ey==-12&&!e->enemyground&&e->explonum==12&&e->armorleft==30);
  assert(e->enemycycle==(type==338?0:1)&&e->aniactive==(type==338?1:0));e->linknum=23;e->ex=106;e->ey=87;
  if(scenario<9)e->ex=xs[scenario];if(scenario>=5&&scenario<=8)tempMapXOfs=19;
  if(scenario>=9&&scenario<=21)e->ey=ys[scenario-9];
  if(scenario==22)e->iced=1;if(scenario==23)e->iced=3;if(scenario==24)e->iced=255;
  if(scenario==25){e->ex=263;tempMapXOfs=19;tempBackMove=1;}
  if(scenario==26){e->filter=17;e->eshotwait[0]=7;e->eshotwait[1]=99;e->eshotwait[2]=0;e->launchwait=113;}
  if(scenario==27&&type==338)e->enemycycle=12;if(scenario==28)e->ey=-84;if(scenario==29)e->ex=0;if(scenario==30)e->ex=1;
  for(unsigned tick=0;tick<32;tick++) {
   mirror_logic_tick++;engine_draw_enemy(50);trace(&traces[run][tick]);assert(mt_state_fingerprint()==rng);
   if(run){assert(!memcmp(&traces[0][tick],&traces[1][tick],sizeof(struct Trace)));animation_comparisons++;}
   if(scenario==0||scenario==22||scenario==23||scenario==24||scenario==26||scenario==27||scenario==28){
    assert(e->enemycycle==(type==338?tick%12+1:1));assert(e->egr[e->enemycycle-1]==(type==338?seq[tick%12]:enemyDat[type].egraphic[0]));}
  }
  if(scenario==1||scenario==4||scenario==5||scenario==8)assert(traces[run][0].actors[25].enemycycle==(type==338?0:1)&&!traces[run][0].calls);
  if(scenario==28)assert(traces[run][0].actors[25].enemycycle==(type==338?1:1)&&!traces[run][0].calls);
  if(scenario==26)assert(e->eshotwait[0]==7&&e->eshotwait[1]==99&&e->eshotwait[2]==0&&e->launchwait==113);
 }
 for(difficultyLevel=0;difficultyLevel<=10;difficultyLevel++)for(unsigned type=338;type<=342;type++) {
  struct JE_SingleEnemyType made;memset(&made,0,sizeof(made));mt_srand(338+type);unsigned expected_x=130+(mt_rand()%250)-125+1;uint64_t rng=mt_state_fingerprint();mt_srand(338+type);
  assert(engine_make_enemy(&made,type,0)==0&&made.ex==(int)expected_x&&made.ey==-12&&made.armorleft>0&&made.evalue==(type==338?made.evalue:0)&&mt_state_fingerprint()==rng);
 }
 assert(animation_comparisons==5*31*32&&hd_calls>0&&hd_cycles==4095);mirror_calls=false;actor(&source,25,338,23);
}
static void production_allocations(void)
{
 const unsigned holes[]={25,29,34,43,49};const int dx[]={0,0,24,0,24},ys[]={-84,-28,-28,-56,-56};
 for(unsigned site=0;site<3;site++)for(unsigned n=0;n<=5;n++)for(unsigned gap=0;gap<2;gap++)for(unsigned scroll=0;scroll<3;scroll++){
  clear_engine();memset(enemyAvail,0,sizeof(enemyAvail));for(unsigned j=0;j<n;j++)enemyAvail[gap?holes[j]:25+j]=1;
  mapX=scroll+1;difficultyLevel=2;mt_srand(338);for(unsigned j=0;j<n;j++)(void)mt_rand();uint64_t expected_rng=mt_state_fingerprint();mt_srand(338);install(site);
  assert(totalEnemy==n&&mt_state_fingerprint()==expected_rng);unsigned created=0;
  for(unsigned j=0;j<n;j++){unsigned slot=gap?holes[j]:25+j;struct JE_SingleEnemyType *e=&enemy[slot];assert(enemyAvail[slot]==0&&e->enemytype==338+j&&e->ex==eventRec[site*2].eventdat2-(int)scroll*24-12+dx[j]&&e->ey==ys[j]&&e->linknum==eventRec[site*2].eventdat4&&!e->fixedmovey);created++;}
  assert(created==n&&!eventRec[site*2+1].eventdat6);allocation_cases++;
 }
 /* Full three-site replay establishes independent15 original actors, then
  * scrolling naturally exposes platform rows before cap and culls separately. */
 for(unsigned run=0;run<2;run++){
  clear_engine();difficultyLevel=2;mt_srand(338);mirror_calls=run;for(unsigned s=0;s<3;s++)install(s);assert(totalEnemy==15);
  unsigned seen[5]={0},gone[5]={0};tempBackMove=1;
  for(unsigned tick=0;tick<280;tick++){mirror_logic_tick++;engine_draw_enemy(50);for(unsigned j=0;j<5;j++){
   if(enemyAvail[25+j]!=1&&enemy[25+j].ey>-26)seen[j]=1;if(enemyAvail[25+j]==1)gone[j]=1;
   if(tick==10)assert(!seen[0]&&seen[1]&&seen[2]&&!seen[3]&&!seen[4]);
  }}for(unsigned j=0;j<5;j++)assert(seen[j]&&gone[j]);
 }
 mirror_calls=false;
}
static void production_damage(Sprite2_array source)
{
 static struct Trace result[2][7];const unsigned holes[]={25,29,34,43,49};
 /* Each exact type, all links, partial/absent-cap groups and allocation holes;
  * the struck actor and every sibling originate in real events/constructors. */
 for(unsigned site=0;site<3;site++)for(unsigned target=0;target<5;target++)for(unsigned scenario=0;scenario<6;scenario++){
  for(unsigned run=0;run<2;run++){
   clear_engine();difficultyLevel=2;mt_srand(0x33825UL);mirror_calls=run;
   if(scenario==4){memset(enemyAvail,0,sizeof(enemyAvail));for(unsigned j=0;j<5;j++)enemyAvail[holes[j]]=1;}
   install(site);unsigned slots[5];for(unsigned j=0;j<5;j++)slots[j]=scenario==4?holes[j]:25+j;
   if(scenario==4)for(unsigned i=25;i<50;i++){bool own=false;for(unsigned j=0;j<5;j++)if(i==slots[j])own=true;if(!own)enemyAvail[i]=1;}
   mirror_calls=false;tempBackMove=1;for(unsigned tick=0;tick<120;tick++){mirror_logic_tick++;engine_draw_enemy(50);}tempBackMove=0;mirror_calls=run;
   unsigned other_site=(site+1)%3;install(other_site);
   if(scenario==3&&target!=0){enemy[slots[0]].ex=-81;engine_draw_enemy(50);assert(enemyAvail[slots[0]]==1);}
   if(scenario==5){for(unsigned j=1;j<5;j++)if(j!=target){enemy[slots[j]].ex=-81;engine_draw_enemy(50);assert(enemyAvail[slots[j]]==1);}}
   /* An independent link is created through its own original event pair. */
   struct JE_SingleEnemyType other[5];unsigned other_slots[5],k=0;
   for(unsigned i=25;i<50;i++)if(enemyAvail[i]!=1&&enemy[i].linknum==eventRec[other_site*2].eventdat4){assert(k<5);other_slots[k]=i;other[k++]=enemy[i];}assert(k==5);
   unsigned victim=slots[target];assert(enemyAvail[victim]==0);int damage=scenario==0?1:scenario==1?99:enemy[victim].armorleft;
   struct JE_SingleEnemyType before[100];memcpy(before,enemy,sizeof(before));unsigned char before_avail[100];memcpy(before_avail,enemyAvail,100);
   unsigned killed=enemyKilled,hits=collision_hits;int cash=player[0].cash;uint64_t rng=mt_state_fingerprint();shotAvail[0]=1;playerShotData[0].shotDmg=damage;
   engine_player_collision(enemy[victim].ex+enemy[victim].mapoffset,enemy[victim].ey-6,damage);
   assert(collision_hits==hits+1&&mt_state_fingerprint()==rng);for(unsigned j=0;j<5;j++)assert(!memcmp(&other[j],&enemy[other_slots[j]],sizeof(other[j])));
   if(scenario<=1){
    for(unsigned i=0;i<100;i++){struct JE_SingleEnemyType expected=before[i];if(i==victim){if(scenario==0)expected.armorleft--;else expected.iced=40;}assert(!memcmp(&expected,&enemy[i],sizeof(expected))&&enemyAvail[i]==before_avail[i]);}
    assert(enemyKilled==killed&&player[0].cash==cash);G101EnemyContext c=context(victim,338+target);
    assert(checked_draw(&surface,enemy[victim].ex+enemy[victim].mapoffset-6,enemy[victim].ey-7,source,selected_base(&c),0,enemy[victim].filter,&c));
   } else {
    unsigned removed=0,effect=0;bool cap=before_avail[slots[0]]!=1;
    for(unsigned j=0;j<5;j++)if(before_avail[slots[j]]!=1){unsigned i=slots[j];if(j==0){
     struct JE_SingleEnemyType expected=before[i];expected.edlevel=0;expected.egr[0]=121;expected.ani=1;expected.aniactive=0;expected.animax=0;expected.animin=1;expected.edamaged=true;expected.enemycycle=1;
     assert(enemyAvail[i]==2&&!memcmp(&expected,&enemy[i],sizeof(expected)));G101EnemyContext c=context(i,338);assert(checked_draw(&surface,enemy[i].ex+enemy[i].mapoffset-6,enemy[i].ey-7,source,121,0,enemy[i].filter,&c));
    }else{assert(enemyAvail[i]==1);removed++;}
     assert(rep_explosions[effect].x==(unsigned)(before[i].ex+before[i].mapoffset)&&rep_explosions[effect].y==(unsigned)before[i].ey&&rep_explosions[effect].ttl==2&&rep_explosions[effect].delay==2&&rep_explosions[effect].big);effect++;
    }
    assert(enemyKilled==killed+removed&&player[0].cash==cash+(cap?before[slots[0]].evalue:0));
    if(cap){unsigned i=slots[0];unsigned oldhits=collision_hits;struct JE_SingleEnemyType wreck=enemy[i];shotAvail[0]=1;engine_player_collision(wreck.ex+wreck.mapoffset,wreck.ey-6,200);assert(collision_hits==oldhits&&!memcmp(&wreck,&enemy[i],sizeof(wreck)));
     PlayerShotDataType guided;memset(&guided,0,sizeof(guided));guided.shotX=wreck.ex-1;guided.shotY=wreck.ey-1;engine_homing_select(&guided,8);assert(guided.aimAtEnemy==i+1);guided.aimDelay=1;engine_homing_follow(&guided);assert(guided.shotXM==1&&guided.shotYM==1);
    }
    for(unsigned tick=0;tick<6;tick++)engine_repeating();
   }
   trace(&result[run][0]);if(run)assert(!memcmp(&result[0][0],&result[1][0],sizeof(struct Trace)));
  }
  damage_cases++;
 }
 mirror_calls=false;assert(damage_cases==90);
 /* Ordinary background culling cannot create a linked wreck. */
 clear_engine();install(0);enemy[25].ex=-81;engine_draw_enemy(50);assert(enemyAvail[25]==1&&!enemy[25].edamaged&&enemy[25].egr[0]==115);for(unsigned i=26;i<30;i++)assert(enemyAvail[i]==0);
 for(unsigned t=338;t<=342;t++)assert((enemyDat[t].explosiontype&1)!=0); /* exact original ram predicate excludes source25 */
}
static void wreck_guards(Sprite2_array source)
{
 clear_engine();difficultyLevel=2;mt_srand(338);install(0);tempBackMove=1;for(unsigned tick=0;tick<120;tick++)engine_draw_enemy(50);tempBackMove=0;
 shotAvail[0]=1;engine_player_collision(enemy[26].ex+enemy[26].mapoffset,enemy[26].ey-6,enemy[26].armorleft);assert(enemyAvail[25]==2);
 enemy[25].ex=106;enemy[25].ey=87;enemy[25].mapoffset=0;G101EnemyContext c=context(25,338);assert(c.availability==2&&c.damaged&&c.static_animation&&draw(source,&c));mirror_logic_tick++;mirror_calls=true;engine_draw_enemy(50);mirror_calls=false;
#define WRECK_BAD(field,value) do{struct JE_SingleEnemyType old=enemy[25];enemy[25].field=value;assert(!draw(source,&c));enemy[25]=old;}while(0)
 for(unsigned i=0;i<20;i++)WRECK_BAD(egr[i],999);
 WRECK_BAD(edamaged,false);WRECK_BAD(edgr,120);WRECK_BAD(edlevel,-1);WRECK_BAD(edani,1);WRECK_BAD(ani,12);WRECK_BAD(aniactive,1);WRECK_BAD(enemycycle,0);WRECK_BAD(enemycycle,2);WRECK_BAD(animin,0);WRECK_BAD(animax,12);WRECK_BAD(aniwhenfire,1);WRECK_BAD(armorleft,0);
 for(unsigned field=0;field<3;field++){G101EnemyContext old=c;if(field==0)c.availability=0;if(field==1)c.damaged=false;if(field==2)c.static_animation=false;assert(!draw(source,&c));c=old;}
 enemyAvail[25]=0;assert(!draw(source,&c));enemyAvail[25]=1;assert(!draw(source,&c));enemyAvail[25]=2;
 for(unsigned ice=0;ice<=255;ice++){enemy[25].iced=ice;assert(draw(source,&c));}
 for(unsigned armor=1;armor<=255;armor++){enemy[25].armorleft=armor;assert(draw(source,&c));}
 enemy[25].ey=190;tempBackMove=1;engine_draw_enemy(50);assert(enemyAvail[25]==2&&enemy[25].ey==191);engine_draw_enemy(50);assert(enemyAvail[25]==1&&enemy[25].egr[0]==121);
#undef WRECK_BAD
}
@REUSED_GUARDS@
int main(int argc,char **argv)
{
 assert(argc==6);game_probe_assets=argv[3];records(argv[2]);load_events(argv[5]);FILE *f=fopen(argv[1],"rb");assert(f);Uint8 *raw=malloc(46204);assert(raw&&fread(raw,1,46204,f)==46204&&fgetc(f)==EOF);fclose(f);
 enemySpriteSheets[0]=(Sprite2_array){46204,raw};enemySpriteSheetIds[0]=20;Sprite2_array source=enemySpriteSheets[0];assert(linked338_source(source)&&asteroid1_scope());actor(&source,25,338,23);G101EnemyContext c=context(25,338);
 if(!strcmp(argv[4],"reject")){assert(!linked338_family_ready()&&!draw(source,&c)&&!accepted&&!rejected);linked338_shutdown();free(raw);puts("linked338 all-family classic fallback");return 0;}
 assert(!strcmp(argv[4],"accept"));assert(linked338_family_ready());exact_record_guards(source);actor_guards(source);production_animation(source);production_allocations();production_damage(source);wreck_guards(source);source_guards(source);warm_frame_guard(source);display_guards(source);resource_guards();
 assert(hd_cycles==4095&&hd_bases==255);printf("linked338 production admissions=%u cycles=%u images=%u; animation comparisons=%u; allocation cases=%u; damage cases=%u; canonical cold=%u warm=%u\n",hd_calls,hd_cycles,hd_bases,animation_comparisons,allocation_cases,damage_cases,cold_record_mutations,warm_record_mutations);
 linked338_shutdown();free(raw);return 0;
}
'''


def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def run_bounded(command,log,*,compiler=False,sanitize=False):
    ceiling=(1024 if compiler else 512)*MIB
    def limits():
        resource.setrlimit(resource.RLIMIT_FSIZE,(16*MIB,16*MIB));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        if compiler or not sanitize:resource.setrlimit(resource.RLIMIT_AS,(ceiling,ceiling))
    with log.open('wb') as stream:
        proc=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'},preexec_fn=limits,start_new_session=True)
        peak=0;deadline=time.monotonic()+(90 if compiler else 120)
        try:
            while True:
                pid,status,usage=os.wait4(proc.pid,os.WNOHANG)
                if pid:
                    proc.returncode=os.waitstatus_to_exitcode(status);peak=max(peak,usage.ru_maxrss*1024)
                    if peak>ceiling:raise RuntimeError('Subprocess exceeded RSS bound')
                    break
                if time.monotonic()>deadline:raise RuntimeError('Bounded subprocess timed out')
                try:
                    for line in (Path('/proc')/str(proc.pid)/'status').read_text().splitlines():
                        if line.startswith('VmRSS:'):
                            peak=max(peak,int(line.split()[1])*1024)
                            if peak>ceiling:raise RuntimeError('Subprocess exceeded RSS bound')
                            break
                except FileNotFoundError:pass
                if log.stat().st_size>16*MIB:raise RuntimeError('Subprocess log exceeded16MiB')
                time.sleep(.01)
            if proc.returncode:raise RuntimeError(f'Command failed({proc.returncode}); inspect{log}')
        finally:
            if proc.returncode is None:
                os.killpg(proc.pid,signal.SIGKILL);_,status,_=os.wait4(proc.pid,0);proc.returncode=os.waitstatus_to_exitcode(status)
    return peak


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--sdl-include',action='append',default=[]);p.add_argument('--sanitize',action='store_true');a=p.parse_args();root=a.repo.resolve();a.out=a.out.resolve()
    a.out.mkdir(parents=True,exist_ok=True)
    if any(a.out.iterdir()):raise RuntimeError('Select a new empty output directory')
    if shutil.disk_usage(a.out).free<5_000_000_000:raise RuntimeError('At least5GB free required')
    ten=module(root/'tests/test_asteroid1_ten_assets.py','linked_named_ten');ember=module(root/'tests/test_asteroid1_ember269_runtime.py','linked_named_ember')
    paths={name:root/'src'/name for name in ('render_mirror.c','render_mirror_asteroid_linked338.inc','asteroid1_ten_mirror.inc','asteroid1_source_snapshot.inc','varz.h','varz.c','tyrian2.c','mtrand.c','config.h','shots.c','shots.h','mainint.c')}
    source={name:path.read_text() for name,path in paths.items()}
    family=source['render_mirror_asteroid_linked338.inc'];renderer=source['render_mirror.c'];engine=source['tyrian2.c'];varz=source['varz.h'];extract=ten.extract
    assert 'linked338_shutdown();' in extract(renderer,'render_mirror_hud_shutdown')
    assert 'return linked338_draw(' in extract(renderer,'render_mirror_enemy_tile')
    assert 'ASSET_ASTEROID1_NEWSHP' in extract(renderer,'draw_asset_filtered')
    assert re.search(r'if\(a->bank==ASSET_ASTEROID1_NEWSHP\)return false;',extract(renderer,'read_asset'))
    assert '(enemyDat[enemy[z].enemytype].explosiontype & 1) == 0' in source['mainint.c']
    struct_start=varz.index('struct JE_SingleEnemyType\n{');struct_end=varz.index('\n};',struct_start)+3
    structcode=varz[struct_start:struct_end]+'\nstatic struct JE_SingleEnemyType enemy[100];\nstatic unsigned char enemyAvail[100];\n'
    prefix=ten.HARNESS.split('int main(int argc',1)[0].replace('t=444;t<=453','t=338;t<=342')
    prefix=prefix.replace('#define ASSET_ASTEROID1 108','#define ASSET_ASTEROID1 108\n#define ASSET_ASTEROID1_NEWSHP 135')
    prefix=prefix.replace('static Uint8 last_filter;','static Uint8 last_filter;static Asset *last_asset;').replace('accepted++;last_x=x;','last_asset=a;accepted++;last_x=x;')
    prefix=prefix.replace('a->bank==108','a->bank==135').replace('assert(role==108&&mirrored)','assert(role==135&&mirrored)')
    scopes=extract(renderer,'asteroid1_level_scope')+extract(renderer,'asteroid1_scope')
    common=extract(source['asteroid1_ten_mirror.inc'],'asteroid1_stamp')+extract(source['asteroid1_ten_mirror.inc'],'asteroid1_record_stamp')
    constructor=extract(engine,'JE_makeEnemy').replace('uint JE_makeEnemy(','static uint engine_make_enemy(')
    allocator=extract(engine,'JE_newEnemy').replace('Sint16 JE_newEnemy(','static Sint16 engine_new_enemy(').replace('JE_makeEnemy(','engine_make_enemy(')
    create=extract(engine,'JE_createNewEventEnemy').replace('void JE_createNewEventEnemy(','static void engine_create_event_enemy(').replace('JE_makeEnemy(','engine_make_enemy(')
    event12=engine[engine.index('\tcase 12: /* Custom 4x4 Ground Enemy */'):engine.index('\tcase 13:',engine.index('\tcase 12: /* Custom 4x4 Ground Enemy */'))]
    event12=event12.replace('JE_createNewEventEnemy(','engine_create_event_enemy(')
    events=create+'static void engine_event(void){switch(eventRec[eventLoc-1].eventtype){case 6:engine_create_event_enemy(0,25,0);break;\n'+event12+'default:assert(0);}}\n'
    draw=extract(engine.replace('void JE_drawEnemy(int enemyOffset) // actually does a whole lot more than just drawing','void JE_drawEnemy(int enemyOffset)'),'JE_drawEnemy')
    draw=draw[:draw.index('\t\t\t/* Enemy Launch Routine */')]+'\n draw_enemy_end:;\n }\n }\n player[0].x +=25;\n}\n'
    draw=draw.replace('void JE_drawEnemy(','static void engine_draw_enemy(')
    shot_end=varz.index('} EnemyShotType;')+len('} EnemyShotType;');shot_start=varz.rindex('typedef struct {',0,shot_end)
    expl_end=varz.index('} rep_explosion_type;')+len('} rep_explosion_type;');expl_start=varz.rindex('typedef struct {',0,varz.index('} Explosion;'))
    event_start=varz.index('struct JE_EventRecType\n{');event_end=varz.index('\n};',event_start)+3
    config=source['config.h'];difficulty=config[config.rindex('enum\n{',0,config.index('DIFFICULTY_WIMP')):config.index('};',config.index('DIFFICULTY_WIMP'))+2]
    collision_start=engine.index('\t\t\tfor (b = 0; b < 100; b++)',engine.index('/* Player Shot Images */'));collision_end=engine.index('\ndraw_player_shot_loop_end:',collision_start)
    collision=engine[collision_start:collision_end].replace('JE_newEnemy(','engine_new_enemy(')
    shots=source['shots.c'];start=shots.index('\t\tif (shot->aimAtEnemy != 0)');end=shots.index('\n\t\tJE_word sprite_frame',start)
    follow='static void engine_homing_follow(PlayerShotDataType *shot){'+shots[start:end]+'}\n'
    start=shots.index('\t\t\tuint best_dist = 65000;',shots.index('if (weapon->aim > 5)'));end=shots.index('\n\t\t}',start)
    select='static void engine_homing_select(PlayerShotDataType *shot,unsigned aim){unsigned x,y;JE_WeaponType w={0},*weapon=&w;weapon->aim=aim;'+shots[start:end]+'}\n'
    repeat_start=engine.index('\tenemyStillExploding = false;',engine.index('/*-------------------------- Sequenced Explosions'));repeat_end=engine.index('\n\t/*---------------------------- Draw Explosions',repeat_start)
    repeating='static void engine_repeating(void){bool enemyStillExploding;'+engine[repeat_start:repeat_end]+'(void)enemyStillExploding;}\n'
    # Keep the old rigorously bounded loader/display/current-byte test bodies,
    # renamed to the independently keyed eight-resource135 NEWSHP family.
    reused=''
    for name in ('source_guards','warm_frame_guard','display_guards','resource_guards'):
        block=extract(ember.MAIN,name).replace('ember269','linked338').replace('269','338')
        block=block.replace('for(unsigned type=338;type<=338;type++)','for(unsigned type=338;type<=342;type++)')
        block=block.replace('actor(&source,25,type,0)','actor(&source,25,type,23)').replace('actor(&source,25,338,0)','actor(&source,25,338,23)').replace('actor(&alternate,25,338,0)','actor(&alternate,25,338,23)')
        block=block.replace('context(25,338)','context(25,338)').replace('42011','46203').replace('asteroid1_source_snapshot','linked338_source_snapshot').replace('enemySpriteSheetIds[slot]=8','enemySpriteSheetIds[slot]=20').replace('enemySpriteSheetIds[0]=8','enemySpriteSheetIds[0]=20')
        block=block.replace('member<4','member<8').replace('source,267','source,115').replace('alternate,267','alternate,115')
        block=block.replace('assert(!linked338_source(source));actor(&alternate,25,338,23);','assert(!linked338_source(source));actor(&alternate,25,338,23);c=context(25,338);')
        block=block.replace('G101EnemyContext c=context(25,338);actor(&source,25,338,23);','actor(&source,25,338,23);G101EnemyContext c=context(25,338);')
        # Warm frame fixture uses all five types and their original base.
        block=block.replace('source,338,1,0,&c','source,selected_base(&c),1,0,&c')
        block=block.replace('BAD_ASSET(bank,101)','BAD_ASSET(bank,108)')
        if name=='source_guards':
            block=block.replace('enemySpriteSheets[slot]=source;enemySpriteSheetIds[slot]=20;assert(linked338_source(source));','enemySpriteSheets[slot]=source;enemySpriteSheetIds[slot]=20;assert(linked338_source(source));actor(&source,25,338,23);c=context(25,338);assert(draw(source,&c));')
            block=block.replace('enemySpriteSheets[0]=source;enemySpriteSheetIds[0]=20;','enemySpriteSheets[0]=source;enemySpriteSheetIds[0]=20;actor(&source,25,338,23);c=context(25,338);')
        reused+=block+'\n'
    # The reused source guard has explicit old42012 sizes only as inherited
    # zero-less constants; assert the named replacement reaches all offsets.
    reused=reused.replace('42012','46204')
    playershots=source['shots.h'];ps_end=playershots.index('} PlayerShotDataType;')+len('} PlayerShotDataType;');ps_start=playershots.rindex('typedef struct {',0,ps_end)
    replacements={'@PLAYER_SHOT_STRUCT@':playershots[ps_start:ps_end],'@SHOT_STRUCT@':varz[shot_start:shot_end],'@EXPLOSION_STRUCTS@':varz[expl_start:expl_end],
      '@EVENT_STRUCT@':varz[event_start:event_end],'@EXPLOSIONS@':extract(source['varz.c'],'JE_setupExplosion')+extract(source['varz.c'],'JE_setupExplosionLarge'),
      '@ENGINE_CONSTRUCTOR@':difficulty+'\n'+constructor+allocator,'@ENGINE_EVENTS@':events,'@ENGINE_DRAW@':draw,'@ENGINE_COLLISION@':collision,
      '@ENGINE_HOMING@':select+follow,'@ENGINE_REPEATING@':repeating,'@REUSED_GUARDS@':reused}
    maincode=MAIN
    for key,value in replacements.items():maincode=maincode.replace(key,value)
    code=prefix.replace('@SCOPE@',scopes).replace('@FAMILY@',structcode+common+family+source['mtrand.c'])+maincode
    harness=a.out/'harness.c';harness.write_text(code)
    raw=(a.data/'tyrian.hdt').read_bytes();off=struct.unpack_from('<i',raw)[0]+14+1638*80+61*82+55*37+7*37+19*41+38*86+12*37
    record=a.out/'original338-342-records.bin';record.write_bytes(raw[off+338*77:off+343*77]);assert record.stat().st_size==385
    lvl=(a.data/'tyrian1.lvl').read_bytes();pos=struct.unpack_from('<i',lvl,2)[0];nr=struct.unpack_from('<H',lvl,pos+8)[0];pos+=10+nr*2;n=struct.unpack_from('<H',lvl,pos)[0];pos+=2
    selected=[];ordinals=[]
    for i in range(n):
        ev=lvl[pos+11*i:pos+11*(i+1)];_,kind,typ=struct.unpack_from('<HBh',ev)
        if kind in (6,12) and typ in (338,339):selected.append(ev);ordinals.append(i+1)
    assert ordinals==[229,230,327,328,382,383]
    events_file=a.out/'original-six-events.bin';events_file.write_bytes(b''.join(selected))
    pack=root/'assets/hd/packs/asteroid1-ten-v1';arts=[pack/f'enemy-newshp-{base}-8.hda' for base in BASES]
    payloads=[x.read_bytes() for x in arts]
    for base,payload in zip(BASES,payloads):assert len(payload)==172060 and struct.unpack_from('<4s6I',payload)==(b'HDR1',1350000+base,8,24,28,0,0)
    fixtures=a.out/'fixtures';fixtures.mkdir();variants=[]
    kinds=('missing','payload','magic','role','foreign-base','density','width','height','anchor-x','anchor-y','header-short','short','extra','fifo','directory','broken-symlink')
    for number,(art,payload,kind) in enumerate((art,payload,kind) for art,payload in zip(arts,payloads) for kind in kinds):
        d=fixtures/f'{number:03d}-{art.stem}-{kind}';d.mkdir()
        for sibling in arts:
            if sibling!=art:(d/sibling.name).symlink_to(sibling)
        dest=d/art.name
        if kind=='missing':pass
        elif kind=='fifo':os.mkfifo(dest)
        elif kind=='directory':dest.mkdir()
        elif kind=='broken-symlink':dest.symlink_to(d/'absent.hda')
        else:
            data=bytearray(payload)
            if kind=='payload':data[40]^=1
            elif kind=='magic':data[:4]=b'NOPE'
            elif kind=='role':struct.pack_into('<I',data,4,1080000+BASES[arts.index(art)])
            elif kind=='foreign-base':struct.pack_into('<I',data,4,1350123)
            elif kind=='header-short':data=data[:12]
            elif kind=='short':data=data[:-1]
            elif kind=='extra':data+=b'X'
            else:struct.pack_into('<I',data,dict(density=8,width=12,height=16,**{'anchor-x':20,'anchor-y':24})[kind],1)
            dest.write_bytes(data)
        variants.append(d)
    flags=['-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I'+str(root/'src')]+['-I'+x for x in a.sdl_include]
    if not a.sdl_include:flags+=subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True).split()
    outputs=[harness,record,events_file];compiler_peak=runtime_peak=0;runs=[]
    for mode in ['optimized']+(['asan-ubsan'] if a.sanitize else []):
        exe=a.out/mode;log=a.out/(mode+'-compile.log');compiler=['cc',*flags,'-O2']+(['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g'] if mode=='asan-ubsan' else [])
        compiler_peak=max(compiler_peak,run_bounded([*compiler,str(harness),'-lm','-o',str(exe)],log,compiler=True));outputs += [exe,log]
        for i,(directory,expected) in enumerate([(pack,'accept')]+[(d,'reject') for d in variants]):
            log=a.out/f'{mode}-{i:03d}.log';runtime_peak=max(runtime_peak,run_bounded([str(exe),str(a.data/'newshp.shp'),str(record),str(directory),expected,str(events_file)],log,sanitize=mode=='asan-ubsan'));outputs.append(log)
        match=re.search(r'admissions=(\d+) cycles=(\d+) images=(\d+); animation comparisons=(\d+); allocation cases=(\d+); damage cases=(\d+); canonical cold=(\d+) warm=(\d+)',(a.out/f'{mode}-000.log').read_text())
        assert match and tuple(map(int,match.groups()[1:]))==(4095,255,4960,108,90,385,385)
        runs.append(dict(mode=mode,positive=1,negative=len(variants),production_HD_admissions=int(match[1]),binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    output_bytes=sum(x.stat().st_size for x in outputs)+sum(x.stat().st_size for d in variants for x in d.iterdir() if x.is_file() and not x.is_symlink())
    if output_bytes>OUTPUT_LIMIT:raise RuntimeError('Generated output exceeds32MiB')
    receipt=dict(records=list(range(338,343)),bases=BASES,material_role=135,source_bank=20,cold_record_bytes=385,warm_record_bytes=385,all_member_dependency_rejections=True,canonical_mutation_member_callbacks=8,
      production_constructor=True,original_event_ordinals=ordinals,allocation_cases=108,allocation_free_slots=list(range(6)),allocation_holes=[25,29,34,43,49],
      production_animation_comparisons=4960,cap_cycles=list(range(1,13)),production_damage_cases=90,links=[23,29,33],homing_wreck=True,original_explosion_allocation=True,
      original_repeating_explosion_RNG=True,nonlethal_all_types=True,ice_all_types=True,lethal_all_types=True,partial_and_absent_cap=True,ordinary_collision_skips_wreck=True,
      fixture_count=len(variants),compiler_peak_rss_bytes=compiler_peak,runtime_peak_rss_bytes=runtime_peak,compiler_address_space_limit_bytes=1024*MIB,runtime_rss_limit_bytes=512*MIB,runtime_timeout_seconds=120,compiler_timeout_seconds=90,
      output_limit_bytes=OUTPUT_LIMIT,output_bytes=output_bytes,runs=runs,leak_sanitizer=False,source_sha256={name:hashlib.sha256(text.encode()).hexdigest() for name,text in source.items()},
      scope='Extracted original constructor, allocation, event6/event12, draw prelaunch, ordinary player-shot linked destruction, explosion allocation, repeating explosion and homing blocks with production MT RNG. Real-engine evidence is separate.')
    (a.out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
