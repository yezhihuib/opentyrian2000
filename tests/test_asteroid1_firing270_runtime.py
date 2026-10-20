#!/usr/bin/env python3
"""Bounded extracted-production NEWSHD270 lifecycle and material141 tests.

Only explicitly named production sources, the named ten/ember/linked harness
helpers, three NEWSHD HDR1 members and original tyrian.hdt/tyrian1.lvl/newshd.shp
are read. No discovery, projection input, game launch, publication or edits to
originals. Compiler AS<=1GiB, runtime RSS<=512MiB, logs<=16MiB, reserve>=5GB.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASES=(127,129,131)
MIB=1024**2
OUTPUT_LIMIT=64*MIB

EVENTS=r'''
static void load_events(const char *path)
{
 FILE *f=fopen(path,"rb");assert(f);
 for(unsigned k=0;k<2;k++){
  Uint8 raw[11];assert(fread(raw,1,11,f)==11);
  eventRec[k]=(struct JE_EventRecType){word(raw),raw[2],(int16_t)word(raw+3),(int16_t)word(raw+5),(int8_t)raw[7],(int8_t)raw[8],(int8_t)raw[9],raw[10]};
  const struct JE_EventRecType *e=&eventRec[k];assert(e->eventtype==6);
  if(!k)assert(e->eventtime==6320&&e->eventdat==270&&e->eventdat2==234&&!e->eventdat3&&!e->eventdat4&&!e->eventdat5&&!e->eventdat6);
  else assert(e->eventdat==269);
 }
 assert(fgetc(f)==EOF);fclose(f);
}
static void install(unsigned site)
{assert(site==0);eventLoc=1;engine_event();}
'''



WEAPON=r'''
static void weapon_record(const char *path)
{
 FILE *f=fopen(path,"rb");assert(f);Uint8 b[80];for(unsigned weapon=145;weapon<=146;weapon++){assert(fread(b,1,80,f)==80);
 assert(asteroid1_stamp(b,80)==(weapon==145?UINT64_C(0x387b219ee9cab017):UINT64_C(0x4623a676db5268a8)));
 JE_WeaponType *w=&weapons[weapon];unsigned p=0;
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
 assert(p==80&&w->sg[0]==112&&w->multi==1&&w->max==1&&w->weapani==2&&w->aim==weapon-142&&w->sound==13);
 }assert(fgetc(f)==EOF);fclose(f);
}

static unsigned cold_weapon_mutations,warm_weapon_mutations;
static void exact_weapon_guards(Sprite2_array source)
{
 actor(&source,25,270,0);enemy[25].aniactive=1;G101EnemyContext c=context(25,270);for(unsigned weapon=145;weapon<=146;weapon++){JE_WeaponType *w=&weapons[weapon];
#define MUTATE(v) do{for(unsigned bit_=1;bit_<=(sizeof(w->v)==2?256U:1U);bit_*=256U){ \
 mirror_logic_tick++;unsigned a_=accepted,r_=rejected;w->v^=bit_; \
 for(unsigned m=0;m<3;m++){enemy[25].enemycycle=(unsigned[]){1,2,3}[m];assert(!firing270_source(source)&&!draw(source,&c));}enemy[25].enemycycle=1; \
 assert(accepted==a_&&rejected==r_&&!reject_reason);w->v^=bit_;assert(firing270_source(source));cold_weapon_mutations++; \
 assert(draw(source,&c));a_=accepted;r_=rejected;w->v^=bit_;assert(!checked_draw(&surface,112,80,source,127,1,0,&c)); \
 assert(accepted==a_&&rejected==r_+1&&reject_reason);for(unsigned m=0;m<3;m++){enemy[25].enemycycle=(unsigned[]){1,2,3}[m];assert(!draw(source,&c));}enemy[25].enemycycle=1;w->v^=bit_;assert(firing270_source(source)&&!draw(source,&c));reject_reason=NULL;warm_weapon_mutations++;}}while(0)
 MUTATE(drain);MUTATE(shotrepeat);MUTATE(multi);MUTATE(weapani);MUTATE(max);MUTATE(tx);MUTATE(ty);MUTATE(aim);
 for(unsigned i=0;i<8;i++){MUTATE(attack[i]);MUTATE(del[i]);MUTATE(sx[i]);MUTATE(sy[i]);MUTATE(bx[i]);MUTATE(by[i]);MUTATE(sg[i]);}
 MUTATE(acceleration);MUTATE(accelerationx);MUTATE(circlesize);MUTATE(sound);MUTATE(trail);MUTATE(shipblastfilter);
#undef MUTATE
 }assert(cold_weapon_mutations==160&&warm_weapon_mutations==160);
}
'''

CHECKS=r'''
static void actor_guards(Sprite2_array source)
{
 const int parts[]={0,1,19,20};const unsigned slots[]={25,49};
 assert(sizeof(firing270_pins)/sizeof(*firing270_pins)==1&&sizeof(firing270_images)/sizeof(*firing270_images)==3);
 for(unsigned s=0;s<2;s++)for(unsigned cycle=1;cycle<=6;cycle++){
  actor(&source,slots[s],270,0);G101EnemyContext c=context(slots[s],270);enemy[slots[s]].enemycycle=cycle;enemy[slots[s]].aniactive=cycle==6?2:1;enemy[slots[s]].filter=17;
  for(unsigned p=0;p<4;p++){int px=p%2?12:0,py=p>=2?14:0;
   assert(checked_draw(&surface,100+px,80+py,source,selected_base(&c),parts[p],17,&c));
   assert(last_asset->bank==141&&last_asset->index==(int)selected_base(&c)&&last_x==100&&last_y==80&&last_part_x==px&&last_part_y==py&&last_filter==17);
  }
 }
 for(unsigned slot=25;slot<50;slot++){actor(&source,slot,270,0);G101EnemyContext all=context(slot,270);assert(draw(source,&all));}
 actor(&source,25,270,0);G101EnemyContext c=context(25,270);
#define DECLINE assert(!draw(source,&c))
#define LIVE(field,value) do{struct JE_SingleEnemyType old=enemy[25];enemy[25].field=value;DECLINE;enemy[25]=old;}while(0)
#define CTX(field,value) do{G101EnemyContext old=c;c.field=value;DECLINE;c=old;}while(0)
 for(unsigned i=0;i<20;i++)LIVE(egr[i],999);
 LIVE(enemytype,275);LIVE(enemydatofs,NULL);LIVE(enemydatofs,&enemyDat[275]);LIVE(sprite2s,NULL);LIVE(size,0);LIVE(size,2);LIVE(scoreitem,true);LIVE(edamaged,true);LIVE(special,true);LIVE(armorleft,0);
 LIVE(ani,0);LIVE(ani,5);LIVE(enemycycle,0);LIVE(enemycycle,7);LIVE(aniactive,0);LIVE(aniactive,3);
 LIVE(animin,0);LIVE(animin,2);LIVE(animax,0);LIVE(animax,5);LIVE(aniwhenfire,0);LIVE(aniwhenfire,1);LIVE(filter,1);LIVE(edgr,1);LIVE(edlevel,-1);LIVE(edlevel,1);LIVE(edani,1);
 LIVE(launchfreq,1);LIVE(launchtype,532);LIVE(launchspecial,1);LIVE(enemydie,1);LIVE(enemyground,true);LIVE(explonum,3);
 LIVE(exc,1);LIVE(eyc,-1);LIVE(fixedmovey,1);LIVE(excc,1);LIVE(eycc,-1);LIVE(xaccel,1);LIVE(yaccel,1);LIVE(exrev,0);LIVE(eyrev,0);LIVE(ex,107);LIVE(ey,88);LIVE(mapoffset,1);
 for(unsigned i=0;i<3;i++){LIVE(tur[i],1);LIVE(freq[i],1);}LIVE(tur[0],0);LIVE(freq[0],0);
 for(unsigned link=1;link<=255;link++)LIVE(linknum,link);
 Sprite2_array wrong={source.size-1,source.data};LIVE(sprite2s,&wrong);wrong=(Sprite2_array){source.size,asteroid1_source_snapshot.bytes};LIVE(sprite2s,&wrong);
 wrong=(Sprite2_array){source.size,source.data};LIVE(sprite2s,&wrong); /* copied object with otherwise identical fields */
 CTX(type,269);CTX(type,272);CTX(type,275);CTX(type,277);CTX(type,286);CTX(type,325);CTX(type,341);CTX(type,342);
 for(unsigned s=0;s<100;s++)if(s<25||s>=50)CTX(pool_slot,s);CTX(pool_slot,100);CTX(pool_slot,UINT_MAX);
 CTX(availability,1);CTX(availability,2);CTX(availability,UINT_MAX);CTX(size,0);CTX(size,2);CTX(score_item,true);CTX(damaged,true);CTX(static_animation,true);CTX(independent_motion,true);
 enemyAvail[25]=1;DECLINE;enemyAvail[25]=2;DECLINE;enemyAvail[25]=0;assert(!draw(source,NULL));
 for(unsigned state=0;state<4;state++)for(unsigned cycle=0;cycle<=7;cycle++){
  struct JE_SingleEnemyType old=enemy[25];enemy[25].aniactive=state;enemy[25].enemycycle=cycle;
  bool legal=(state==1&&cycle>=1&&cycle<6)||(state==2&&(cycle==1||cycle==6));assert(draw(source,&c)==legal);
  if(legal)for(unsigned b=0;b<3;b++)if(BASES[b]!=selected_base(&c))assert(!checked_draw(&surface,100,80,source,BASES[b],0,0,&c));enemy[25]=old;
 }
 for(unsigned armor=1;armor<=255;armor++){enemy[25].armorleft=armor;assert(draw(source,&c));}
 for(unsigned v=0;v<=255;v++){enemy[25].iced=v;for(unsigned j=0;j<3;j++){enemy[25].eshotwait[j]=v;enemy[25].eshotmultipos[j]=v;}enemy[25].launchwait=v;assert(draw(source,&c));}
 const int values[]={-32758,-1,0,20,32757};for(unsigned k=0;k<5;k++){enemy[25].evalue=values[k];assert(draw(source,&c)==(values[k]==0));}
 enemy[25].evalue=0;const int bounce[]={-32758,-1,0,1,32757};for(unsigned k=0;k<5;k++){enemy[25].xminbounce=bounce[k];enemy[25].xmaxbounce=bounce[k];enemy[25].yminbounce=bounce[k];enemy[25].ymaxbounce=bounce[k];assert(draw(source,&c));}
 const int badparts[]={INT_MIN,-1,2,18,21,INT_MAX};for(unsigned k=0;k<6;k++)assert(!checked_draw(&surface,100,80,source,127,badparts[k],0,&c));
 assert(!checked_draw(&surface,100,80,source,127,0,-1,&c));assert(!checked_draw(&surface,100,80,source,127,0,256,&c));
#undef CTX
#undef LIVE
#undef DECLINE
 actor(&source,25,270,0);
}
static void production_animation(Sprite2_array source)
{
 static struct Trace traces[2][96];const unsigned seq[]={127,129,131,129,129,127};
 for(unsigned d=0;d<=10;d++)for(unsigned scenario=0;scenario<22;scenario++){
  uint64_t initial_rng=0;
  for(unsigned run=0;run<2;run++){
   clear_engine();difficultyLevel=d;mt_srand(0x270145UL);mirror_calls=run;initial_rng=mt_state_fingerprint();
   assert(engine_new_enemy(25,270,0)==26);struct JE_SingleEnemyType *e=&enemy[25];assert(mt_state_fingerprint()==initial_rng);
   assert(e->sprite2s==&enemySpriteSheets[0]&&e->enemytype==270&&e->enemydatofs==&enemyDat[270]&&e->ex==1&&e->ey==1&&e->enemycycle==1&&e->aniactive==2&&e->ani==6&&e->animax==6&&e->aniwhenfire==2&&e->animin==1&&!e->enemyground&&e->explonum==2&&e->armorleft>0&&!e->evalue);
   assert(e->tur[0]==145&&e->tur[1]==146&&!e->tur[2]&&e->freq[0]==40&&e->freq[1]==41&&!e->freq[2]&&e->eshotwait[0]==20&&e->eshotwait[1]==20&&e->eshotwait[2]==255&&!e->eshotmultipos[0]&&!e->eshotmultipos[1]);
   e->ex=106;e->ey=87;
   if(scenario==1){memset(enemyShotAvail,0,sizeof(enemyShotAvail));e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==2){e->iced=3;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==3){e->iced=255;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==4)e->eshotwait[0]=e->eshotwait[1]=1;
   if(scenario==5){memset(enemyShotAvail,0,sizeof(enemyShotAvail));enemyShotAvail[59]=1;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==6){memset(enemyShotAvail,0,sizeof(enemyShotAvail));enemyShotAvail[2]=enemyShotAvail[17]=1;e->eshotwait[0]=e->eshotwait[1]=1;e->eshotmultipos[0]=e->eshotmultipos[1]=1;}
   if(scenario==7){e->ex=-29;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==8){e->ex=-28;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==9){e->ey=-30;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==10){e->ex=300;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==11){e->ex=299;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==12){e->ex=263;tempMapXOfs=19;tempBackMove=1;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==13)e->eshotwait[0]=e->eshotwait[1]=0;
   if(scenario==14){e->enemycycle=6;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==15){player[0].x=31;player[0].y=1;player[0].is_alive=false;e->eshotwait[0]=e->eshotwait[1]=1;e->filter=17;}
   if(scenario==16){e->eshotwait[0]=1;e->eshotwait[1]=255;}
   if(scenario==17){e->eshotwait[0]=255;e->eshotwait[1]=1;}
   if(scenario==18){e->aniactive=1;e->iced=255;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==19){e->aniactive=1;e->enemycycle=5;e->iced=3;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==20){e->ex=-47;tempMapXOfs=19;e->eshotwait[0]=e->eshotwait[1]=1;}
   if(scenario==21){e->aniactive=1;e->enemycycle=6;e->eshotwait[0]=e->eshotwait[1]=255;}
   for(unsigned tick=0;tick<96;tick++){
    unsigned cycle=e->enemycycle,state=e->aniactive;bool in_x=e->ex+tempMapXOfs>-29&&e->ex+tempMapXOfs<300;
    if(in_x&&state==1){cycle++;if(cycle==6)state=2;else if(cycle>6)cycle=1;}
    unsigned free_before=0;for(unsigned j=0;j<60;j++)free_before+=enemyShotAvail[j];
    mirror_logic_tick++;engine_draw_enemy(50);trace(&traces[run][tick]);
    unsigned free_after=0;for(unsigned j=0;j<60;j++)free_after+=enemyShotAvail[j];
    if(free_after<free_before&&state==2)state=1;
    assert(e->enemycycle==cycle&&e->aniactive==state&&e->egr[cycle-1]==seq[cycle-1]);
    if(run){assert(!memcmp(&traces[0][tick],&traces[1][tick],sizeof(struct Trace)));animation_comparisons++;}
    if(scenario==1||scenario==3||scenario==7||scenario==8||scenario==10||scenario==11||scenario==13||scenario==20)assert(e->enemycycle==1&&e->aniactive==2&&traces[run][tick].rng==initial_rng);
    if(scenario==18)assert(e->enemycycle==(tick<5?tick+2:6)&&e->aniactive==(tick<4?1:2));
   }
  }
  const struct Trace *first=&traces[1][0];const struct JE_SingleEnemyType *e=&first->actors[25];
  unsigned cooldown0=d<=2?40:d<=7?21:11,cooldown1=d<=2?41:d<=7?21:11;
  if(scenario==0){assert(e->eshotwait[0]==19&&e->eshotwait[1]==19&&first->rng==initial_rng);assert(traces[1][18].actors[25].aniactive==2&&traces[1][19].actors[25].aniactive==1&&traces[1][19].actors[25].enemycycle==1);for(unsigned j=0;j<2;j++)assert(!traces[1][19].shot_avail[j]&&traces[1][19].shots[j].sgr==112);}
  if(scenario==1)assert(e->eshotwait[0]==1&&e->eshotwait[1]==cooldown1&&!e->eshotmultipos[0]&&!e->eshotmultipos[1]&&e->aniactive==2); /* reverse slot order and full-pool early exit */
  if(scenario==2||scenario==3)assert(e->eshotwait[0]==1&&e->eshotwait[1]==1&&e->iced==(scenario==2?2:254)&&first->rng==initial_rng);
  if(scenario==3)assert(traces[1][95].actors[25].iced==159&&traces[1][95].actors[25].eshotwait[0]==1&&traces[1][95].actors[25].eshotwait[1]==1);
  if(scenario==7||scenario==8||scenario==10||scenario==11||scenario==20)assert(e->eshotwait[0]==1&&e->eshotwait[1]==1&&first->rng==initial_rng);
  if(scenario==13)assert(e->eshotwait[0]==255&&e->eshotwait[1]==255&&traces[1][95].actors[25].eshotwait[0]==160);
  if(scenario==5)assert(!e->eshotmultipos[0]&&e->eshotmultipos[1]==1&&!first->shot_avail[59]&&e->aniactive==1);
  if(scenario==6)assert(e->eshotmultipos[0]==1&&e->eshotmultipos[1]==1&&!first->shot_avail[2]&&!first->shot_avail[17]);
  if(scenario==14)assert(e->enemycycle==6&&e->aniactive==1&&traces[1][1].actors[25].enemycycle==1); /* rearmed terminal idle wraps next draw */
  if(scenario==4||scenario==5||scenario==6||scenario==9||scenario==12||scenario==14||scenario==15||scenario==16||scenario==17){
   unsigned count=scenario==5||scenario==16||scenario==17?1:2;assert(first->rng!=initial_rng&&e->aniactive==1);
   if(scenario!=17)assert(e->eshotwait[0]==cooldown0);if(scenario!=16)assert(e->eshotwait[1]==cooldown1);
   for(unsigned j=0;j<count;j++){
    unsigned slot=scenario==5?59:scenario==6?(unsigned[]){2,17}[j]:j;
    unsigned weapon=scenario==16?145:146-j;const JE_WeaponType *w=&weapons[weapon];const EnemyShotType *shot=&first->shots[slot];
    assert(!first->shot_avail[slot]&&shot->sgr==112&&!shot->animate&&shot->animax==2&&shot->sdmg==2&&shot->duration==255&&!shot->tx&&!shot->ty);
    assert(shot->sx==e->ex+w->bx[0]+(scenario==12?19:0)&&shot->sy==e->ey+w->by[0]&&!shot->sxc&&!shot->syc);
    int target_x=scenario==15?31:160,target_y=scenario==15?1:140;
    int ax=target_x-e->ex-(scenario==12?19:0)-4,ay=target_y-e->ey;if(!ax)ax=1;if(!ay)ay=1;int mag=MAX(abs(ax),abs(ay));unsigned aim=w->aim+(d>2?d-2:0);
    assert(shot->sxm==roundf((float)ax/mag*aim)&&shot->sym==roundf((float)ay/mag*aim));
   }
   bool sound=false;for(unsigned j=0;j<8;j++){assert(first->sounds[j]==0||first->sounds[j]==13);sound|=first->sounds[j]==13;}assert(sound&&!first->sounds[3]);
  }
 }
 const unsigned armor[]={7,10,12,14,18,21,24,36,48,96,96};
 for(difficultyLevel=0;difficultyLevel<=10;difficultyLevel++){
  struct JE_SingleEnemyType made;memset(&made,0,sizeof(made));uint64_t rng=mt_state_fingerprint();
  assert(engine_make_enemy(&made,270,0)==0&&made.armorleft==armor[difficultyLevel]&&made.ex==1&&made.ey==1&&made.enemycycle==1&&made.aniactive==2&&mt_state_fingerprint()==rng);
 }
 assert(animation_comparisons==11*22*96&&hd_cycles==63&&hd_bases==7);mirror_calls=false;actor(&source,25,270,0);
}

static void production_allocations(void)
{
 const unsigned holes[]={25,34,49};
 for(unsigned n=0;n<=3;n++)for(unsigned gap=0;gap<2;gap++)for(unsigned scroll=0;scroll<3;scroll++){
  clear_engine();memset(enemyAvail,0,sizeof(enemyAvail));for(unsigned j=0;j<n;j++)enemyAvail[gap?holes[j]:25+j]=1;
  mapX=scroll+1;difficultyLevel=2;mt_srand(270);uint64_t rng=mt_state_fingerprint();struct JE_EventRecType raw[6];memcpy(raw,eventRec,sizeof(raw));install(0);
  unsigned expected=n?1:0;assert(totalEnemy==expected&&mt_state_fingerprint()==rng&&!memcmp(raw,eventRec,sizeof(raw)));
  if(expected){unsigned slot=gap?holes[0]:25;struct JE_SingleEnemyType *e=&enemy[slot];
   assert(enemyAvail[slot]==0&&e->enemytype==270&&e->ex==234-(int)scroll*24-12&&e->ey==-28&&!e->linknum&&!e->fixedmovey&&e->enemycycle==1&&e->aniactive==2);}
  allocation_cases++;
 }
 static struct Trace lifecycle[2][120];
 for(unsigned run=0;run<2;run++){
  clear_engine();difficultyLevel=2;mt_srand(270);mirror_calls=run;uint64_t rng=mt_state_fingerprint();install(0);
  assert(totalEnemy==1&&mt_state_fingerprint()==rng&&enemy[25].enemytype==270);
  tempBackMove=2;for(unsigned tick=0;tick<120;tick++){mirror_logic_tick++;engine_draw_enemy(50);trace(&lifecycle[run][tick]);if(run)assert(!memcmp(&lifecycle[0][tick],&lifecycle[1][tick],sizeof(struct Trace)));}
  assert(enemyAvail[25]==1&&totalEnemy==1&&!enemyKilled);
 }
 /* Exactly one scheduled actor. Repeated direct allocations below are synthetic
  * allocator pressure, not an invented second event or additional gameplay. */
 clear_engine();difficultyLevel=2;uint64_t rng=mt_state_fingerprint();install(0);
 assert(totalEnemy==1&&enemyAvail[26]==1&&mt_state_fingerprint()==rng&&enemy[25].enemytype==270);
 clear_engine();difficultyLevel=2;rng=mt_state_fingerprint();
 for(unsigned i=25;i<50;i++)assert(engine_new_enemy(25,270,0)==(int)i+1);
 assert(!engine_new_enemy(25,270,0)&&totalEnemy==25&&mt_state_fingerprint()==rng);
 clear_engine();memset(enemyAvail,0,sizeof(enemyAvail));enemyAvail[49]=1;rng=mt_state_fingerprint();assert(engine_new_enemy(25,270,0)==50&&engine_new_enemy(25,270,0)==0&&mt_state_fingerprint()==rng);
 mirror_calls=false;assert(allocation_cases==24);
}

static void production_damage(Sprite2_array source)
{
 static struct Trace result[2][8];
 for(unsigned scenario=0;scenario<5;scenario++)for(unsigned run=0;run<2;run++){
  clear_engine();difficultyLevel=2;mt_srand(0x27025UL);mirror_calls=run;
  if(scenario==3){memset(enemyAvail,0,sizeof(enemyAvail));enemyAvail[49]=1;}
  install(0);unsigned victim=scenario==3?49:25;
  if(scenario==3)for(unsigned i=25;i<49;i++)enemyAvail[i]=1;
  tempBackMove=2;for(unsigned tick=0;tick<50;tick++){mirror_logic_tick++;engine_draw_enemy(50);}tempBackMove=0;
  /* A real unrelated269 event remains hidden so it cannot intercept the shot.
   * Positive link23 mutation tests original independent destruction isolation. */
  eventLoc=2;engine_event();unsigned other=(unsigned)b-1;assert(enemy[other].enemytype==269);enemy[other].linknum=23;
  struct JE_SingleEnemyType before[100];memcpy(before,enemy,sizeof(before));unsigned char av[100];memcpy(av,enemyAvail,100);
  unsigned killed=enemyKilled,hits=collision_hits;int cash=player[0].cash;uint64_t rng=mt_state_fingerprint();
  int damage=scenario==0?1:scenario==1?99:enemy[victim].armorleft;shotAvail[0]=1;playerShotData[0].shotDmg=damage;
  engine_player_collision(enemy[victim].ex+enemy[victim].mapoffset,enemy[victim].ey-6,damage);
  assert(collision_hits==hits+1&&mt_state_fingerprint()==rng&&!memcmp(&enemy[other],&before[other],sizeof(before[other]))&&player[0].cash==cash&&!cubeMax);
  for(unsigned i=0;i<100;i++){struct JE_SingleEnemyType expected=before[i];if(i==victim&&scenario==0)expected.armorleft--;if(i==victim&&scenario==1)expected.iced=40;
   assert(!memcmp(&expected,&enemy[i],sizeof(expected)));assert(enemyAvail[i]==(i==victim&&scenario>=2?1:av[i]));}
  assert(enemyKilled==killed+(scenario>=2));
  if(scenario<2){/* Observe at the next actual callback, not a post-fire state. */
   mirror_logic_tick++;engine_draw_enemy(50);assert(!enemy[victim].edamaged&&enemy[victim].ani==6);G101EnemyContext c=context(victim,270);
   assert(checked_draw(&surface,enemy[victim].ex+enemy[victim].mapoffset-6,enemy[victim].ey-7,source,selected_base(&c),0,0,&c));}
  else {assert(rep_explosions[0].ttl==2&&rep_explosions[0].delay==2&&!rep_explosions[0].big&&rep_explosions[0].x==(unsigned)before[victim].ex&&rep_explosions[0].y==(unsigned)before[victim].ey);
   assert(explosions[0].sprite==1&&explosions[1].sprite==39&&explosions[2].sprite==20&&explosions[3].sprite==58);}
  trace(&result[run][0]);if(run)assert(!memcmp(&result[0][0],&result[1][0],sizeof(struct Trace)));
  for(unsigned tick=1;tick<8;tick++){engine_repeating();trace(&result[run][tick]);if(run)assert(!memcmp(&result[0][tick],&result[1][tick],sizeof(struct Trace)));}
  if(run)damage_cases++;
 }
 assert(damage_cases==5);mirror_calls=false;
 clear_engine();install(0);tempBackMove=2;for(unsigned tick=0;tick<50;tick++)engine_draw_enemy(50);tempBackMove=0;
 for(unsigned armor=1;armor<=255;armor++)for(unsigned ice=0;ice<=255;ice++){
  enemy[25].armorleft=armor;enemy[25].iced=ice;struct Trace before,after;trace(&before);engine_ram(25);trace(&after);assert(!memcmp(&before,&after,sizeof(before))&&!ram_damage_calls);
 }
 enemy[25].armorleft=12;enemyDat[270].explosiontype^=1;engine_ram(25);assert(ram_damage_calls==1&&enemy[25].armorleft==8);enemyDat[270].explosiontype^=1;
}

static void afteraccepted_resource_guards(Sprite2_array source)
{
 for(unsigned member=0;member<3;member++){
  firing270_shutdown();assert(firing270_family_ready());actor(&source,25,270,0);enemy[25].enemycycle=(unsigned[]){1,2,3}[member];enemy[25].aniactive=1;
  G101EnemyContext c=context(25,270);mirror_logic_tick++;reject_reason=NULL;assert(draw(source,&c));unsigned a=accepted,r=rejected;
  firing270_resources.member[member].valid=false;firing270_resources.valid=false;
  assert(!checked_draw(&surface,112,80,source,selected_base(&c),1,0,&c)&&accepted==a&&rejected==r+1&&reject_reason);
  firing270_resources.member[member].valid=true;firing270_resources.valid=true;assert(!draw(source,&c)&&accepted==a&&rejected==r+1);
  firing270_shutdown();mirror_logic_tick++;reject_reason=NULL;assert(firing270_family_ready()&&draw(source,&c));
  firing270_resources.member[member].rgba[10]^=1;mirror_logic_tick++;assert(!draw(source,&c)&&!reject_reason); /* next frame cold failure */
  firing270_resources.member[member].rgba[10]^=1;assert(!draw(source,&c));firing270_shutdown();assert(firing270_family_ready()&&draw(source,&c));
 }
}
static void exhaustive_source_bytes(Sprite2_array source)
{
 /* Every current byte is checked, including offset table and dormant tiles.
  * Cold corrupt initialization must never bless a source snapshot; a warm
  * snapshot never inherits trust from pointer identity or a prior callback. */
 for(unsigned i=0;i<42012;i++){
  asteroid1_source_snapshot.valid=false;source.data[i]^=1;
  assert(!firing270_source(source)&&!asteroid1_source_snapshot.valid);
  source.data[i]^=1;
 }
 assert(firing270_source(source)&&asteroid1_source_snapshot.valid);
 for(unsigned i=0;i<42012;i++){
  source.data[i]^=1;assert(!firing270_source(source));source.data[i]^=1;assert(firing270_source(source));
 }
}

static void source_bank_independence(Sprite2_array source)
{
 assert(firing270_source(source)&&ember269_source(source));
 enemyDat[269].value^=1;assert(firing270_source(source)&&!ember269_source(source));enemyDat[269].value^=1;
 enemyDat[270].value^=1;assert(!firing270_source(source)&&ember269_source(source));enemyDat[270].value^=1;
 for(unsigned weapon=145;weapon<=146;weapon++){weapons[weapon].sound^=1;assert(!firing270_source(source)&&ember269_source(source));weapons[weapon].sound^=1;}
 const unsigned offsets[]={0,200,42011};for(unsigned k=0;k<3;k++){source.data[offsets[k]]^=1;assert(!firing270_source(source)&&!ember269_source(source));source.data[offsets[k]]^=1;assert(firing270_source(source)&&ember269_source(source));}
 asteroid1_source_snapshot.valid=false;source.data[200]^=1;assert(!firing270_source(source)&&!asteroid1_source_snapshot.valid);source.data[200]^=1;assert(firing270_source(source));
 firing270_shutdown();assert(firing270_family_ready()&&ember269_source(source));
}

'''

MAIN_END=r'''
int main(int argc,char **argv)
{
 assert(argc==9);game_probe_assets=argv[3];records(argv[2]);weapon_record(argv[8]);load_events(argv[5]);FILE *f=fopen(argv[1],"rb");assert(f);Uint8 *raw=malloc(42012);assert(raw&&fread(raw,1,42012,f)==42012&&fgetc(f)==EOF);fclose(f);
 enemySpriteSheets[0]=(Sprite2_array){42012,raw};enemySpriteSheetIds[0]=8;Sprite2_array source=enemySpriteSheets[0];assert(firing270_source(source)&&asteroid1_scope());actor(&source,25,270,0);G101EnemyContext c=context(25,270);
 if(!strcmp(argv[4],"reject")){
  assert(!firing270_family_ready()&&!draw(source,&c)&&!accepted&&!rejected);game_probe_assets=argv[6];assert(!firing270_family_ready()&&!draw(source,&c));
  firing270_shutdown();assert(firing270_family_ready()&&draw(source,&c));firing270_shutdown();free(raw);puts("firing270 all-three classic fallback; sticky until shutdown");return 0;
 }
 assert(!strcmp(argv[4],"accept")&&firing270_family_ready());production_identity_checks(argv[7]);production_projectile_classic();exact_record_guards(source);exact_weapon_guards(source);actor_guards(source);partial_geometry(source);production_animation(source);production_allocations();production_damage(source);
 source_guards(source);exhaustive_source_bytes(source);source_bank_independence(source);warm_frame_guard(source);afteraccepted_resource_guards(source);display_guards(source);resource_guards();
 assert(hd_cycles==63&&hd_bases==7);printf("firing270 production admissions=%u cycles=%u images=%u; animation comparisons=%u; allocation cases=%u; damage cases=%u; canonical cold=%u warm=%u; INDEX8 exact; ram armor255 x ice256\n",hd_calls,hd_cycles,hd_bases,animation_comparisons,allocation_cases,damage_cases,cold_record_mutations,warm_record_mutations);
 firing270_shutdown();free(raw);return 0;
}
'''


def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--sdl-include',action='append',default=[]);p.add_argument('--sanitize',action='store_true');a=p.parse_args();root=a.repo.resolve();a.out=a.out.resolve()
    a.out.mkdir(parents=True,exist_ok=True)
    if any(a.out.iterdir()):raise RuntimeError('Select a new empty output directory')
    if shutil.disk_usage(a.out).free<5_000_000_000:raise RuntimeError('At least5GB free required')
    ten=module(root/'tests/test_asteroid1_ten_assets.py','triple_named_ten');ember=module(root/'tests/test_asteroid1_ember269_runtime.py','triple_named_ember');linked=module(root/'tests/test_asteroid1_linked338_runtime.py','triple_named_linked')
    names=('render_mirror.c','asteroid1_firing270_mirror.inc','asteroid1_source_snapshot.inc','asteroid1_ten_mirror.inc','varz.h','varz.c','tyrian2.c','mtrand.c','config.h','shots.h','mainint.c','sprite.c','game_probe.c')
    source={name:(root/'src'/name).read_text() for name in names};extract=ten.extract;renderer=source['render_mirror.c'];engine=source['tyrian2.c'];varz=source['varz.h'];family=source['asteroid1_firing270_mirror.inc']
    assert 'firing270_shutdown();' in extract(renderer,'render_mirror_hud_shutdown')
    assert 'return firing270_draw(' in extract(renderer,'render_mirror_enemy_tile')
    assert 'ASSET_ASTEROID1_FIRING270' in extract(renderer,'draw_asset_filtered')
    assert re.search(r'if\(a->bank==ASSET_ASTEROID1_FIRING270\)return false;',extract(renderer,'read_asset'))
    assert '(enemyDat[enemy[z].enemytype].explosiontype & 1) == 0' in source['mainint.c']
    assert 'asteroid1_source_snapshot.valid=false;' in extract(source['asteroid1_ten_mirror.inc'],'asteroid1_shutdown')
    assert 'asteroid1_source_bytes_match' in extract(family,'firing270_source') and 'firing270_weapon_stamp' in extract(family,'firing270_source')
    struct_start=varz.index('struct JE_SingleEnemyType\n{');struct_end=varz.index('\n};',struct_start)+3
    structcode=varz[struct_start:struct_end]+'\nstatic struct JE_SingleEnemyType enemy[100];\nstatic unsigned char enemyAvail[100];\n'
    prefix=ten.HARNESS.split('int main(int argc',1)[0].replace('for(unsigned t=444;t<=453;t++)','const unsigned types[]={270,269};for(unsigned n=0;n<2;n++) {unsigned t=types[n];')
    # The replacement adds one scope; close it immediately before EOF check.
    prefix=prefix.replace(' assert(fgetc(f)==EOF);fclose(f);',' }assert(fgetc(f)==EOF);fclose(f);')
    prefix=prefix.replace('#define ASSET_ASTEROID1 108','#define ASSET_ASTEROID1 108\n#define ASSET_ASTEROID1_TRIPLE275 137\n#define ASSET_ASTEROID1_ENEMY_ORB112113 142\n#define ASSET_ASTEROID1_FIRING270 141\n#define ASSET_ASTEROID1_FIRING285 143\n#define ASSET_ASTEROID1_TERRAIN144 144\n#define ASSET_ASTEROID1_TURRET273 139\n#define ASSET_ASTEROID1_PROJECTILE304 140\n#define ASSET_ASTEROID1_COLUMNS276 138\n#define ASSET_ASTEROID1_NEWSHS 136')
    prefix=prefix.replace('static Uint8 last_filter;','static Uint8 last_filter;static Asset *last_asset;').replace('accepted++;last_x=x;','last_asset=a;accepted++;last_x=x;').replace('a->bank==108','a->bank==141').replace('assert(role==108&&mirrored)','assert(role==141&&mirrored)')
    prefix=prefix.replace('static SDL_PixelFormat format=', 'static const Asset *terrain144_draw_lease,*firing285_draw_lease,*firing270_draw_lease,*pulsing272_draw_lease,*triple275_draw_lease,*columns276_draw_lease,*enemy_orb112113_draw_lease,*projectile304_draw_lease,*turret273_draw_lease;\nstatic SDL_PixelFormat format=')
    prefix=prefix.replace('assert(a&&a->bank==141&&a->rgba', 'assert(a&&a==firing270_draw_lease&&a->bank==141&&a->rgba')
    scopes=extract(renderer,'asteroid1_level_scope')+extract(renderer,'asteroid1_scope')
    common=extract(source['asteroid1_ten_mirror.inc'],'asteroid1_stamp')+extract(source['asteroid1_ten_mirror.inc'],'asteroid1_record_stamp')
    shared='#include "asteroid1_source_snapshot.inc"\n'
    shared+=renderer[renderer.index('static const struct {unsigned type;uint64_t record;} ember269_pins'):renderer.index('/* One complete occupied housing')]+extract(renderer,'ember269_source')
    constructor=extract(engine,'JE_makeEnemy').replace('uint JE_makeEnemy(','static uint engine_make_enemy(')
    allocator=extract(engine,'JE_newEnemy').replace('Sint16 JE_newEnemy(','static Sint16 engine_new_enemy(').replace('JE_makeEnemy(','engine_make_enemy(')
    create=extract(engine,'JE_createNewEventEnemy').replace('void JE_createNewEventEnemy(','static void engine_create_event_enemy(').replace('JE_makeEnemy(','engine_make_enemy(')
    event6=re.search(r'\tcase 6: /\* Ground Enemy \*/.*?\t\tbreak;',engine,re.S);assert event6
    event6_body=event6.group(0).replace('JE_createNewEventEnemy(','engine_create_event_enemy(')
    events=create+'static void engine_event(void){assert(eventRec[eventLoc-1].eventtype==6);switch(eventRec[eventLoc-1].eventtype){'+event6_body+'}}\n'
    draw=extract(engine.replace('void JE_drawEnemy(int enemyOffset) // actually does a whole lot more than just drawing','void JE_drawEnemy(int enemyOffset)'),'JE_drawEnemy')
    draw=draw[:draw.index('\t\t\t/* Enemy Launch Routine */')]+'\n draw_enemy_end:;\n }\n }\n player[0].x +=25;\n}\n';draw=draw.replace('void JE_drawEnemy(','static void engine_draw_enemy(')
    shot_end=varz.index('} EnemyShotType;')+len('} EnemyShotType;');shot_start=varz.rindex('typedef struct {',0,shot_end)
    expl_end=varz.index('} rep_explosion_type;')+len('} rep_explosion_type;');expl_start=varz.rindex('typedef struct {',0,varz.index('} Explosion;'))
    event_start=varz.index('struct JE_EventRecType\n{');event_end=varz.index('\n};',event_start)+3
    config=source['config.h'];difficulty=config[config.rindex('enum\n{',0,config.index('DIFFICULTY_WIMP')):config.index('};',config.index('DIFFICULTY_WIMP'))+2]
    collision_start=engine.index('\t\t\tfor (b = 0; b < 100; b++)',engine.index('/* Player Shot Images */'));collision_end=engine.index('\ndraw_player_shot_loop_end:',collision_start)
    collision=engine[collision_start:collision_end].replace('JE_newEnemy(','engine_new_enemy(')
    repeat_start=engine.index('\tenemyStillExploding = false;',engine.index('/*-------------------------- Sequenced Explosions'));repeat_end=engine.index('\n\t/*---------------------------- Draw Explosions',repeat_start)
    repeating='static void engine_repeating(void){bool enemyStillExploding;'+engine[repeat_start:repeat_end]+'(void)enemyStillExploding;}\n'
    ram_start=source['mainint.c'].index('else if (this_player->invulnerable_ticks == 0 && enemyAvail[z] == 0 &&');ram_open=source['mainint.c'].index('{',ram_start);end=ram_open+1;depth=1
    while depth:depth+=(source['mainint.c'][end]=='{')-(source['mainint.c'][end]=='}');end+=1
    ram='static unsigned ram_damage_calls;static void JE_playerDamage(int damage,struct PlayerStub *p){(void)p;assert(damage>0);ram_damage_calls++;}\nstatic void engine_ram(unsigned z){struct PlayerStub *this_player=&player[0];int damageRate=4;'+source['mainint.c'][ram_start:end].replace('else if','if',1)+'}\n'
    # Extract exact indexed tile write paths. Unrelated debug/text hooks are
    # observational no-ops; source decode, row wrap and clipping are unchanged.
    indexed=extract(source['sprite.c'],'blit_sprite2')+extract(source['sprite.c'],'blit_sprite2_filter')
    indexed=re.sub(r'\b(?:load_font_arrow_sprite_begin|pregame_font_sprite2_begin|asset_debug_effect|load_font_arrow_sprite_end|pregame_font_sprite2_end|render_mirror_pixel)\([^;]*\);','',indexed)
    indexed=indexed.replace('void blit_sprite2(', 'static void engine_blit_sprite2(').replace('void blit_sprite2_filter(', 'static void engine_blit_sprite2_filter(')
    # Finite executable identity proof: exact production admission guards,
    # region registration and command serialization, without the unrelated
    # pixel compositor. All compared geometry/style/base values are equal.
    asset_draw=extract(renderer,'draw_asset_filtered')
    gate=asset_draw[asset_draw.index(' if(a->bank==ASSET_ASTEROID1_NEWSHS'):asset_draw.index(' render_mirror_shadow_end();')]
    region=asset_draw[asset_draw.index(' bool region_present=false;'):asset_draw.index(' bool cloud=')]
    reader=extract(renderer,'read_asset');generic=reader[reader.index(' if(a->bank==ASSET_ASTEROID1_NEWSHP'):reader.index(' char name[1024];')]
    identity=r'''
#define ASSET_ASTEROID1_NEWSHP 135
typedef struct { SDL_Rect rect; int bank,index,style; bool live; } HdRegion;
static HdRegion regions[16];static unsigned region_count;
static bool production_region_admission(int x,int y,Asset *a,int style)
{
 const SDL_Rect *part=NULL; unsigned filter=0; const void *material=NULL,*cap=NULL,*forest=NULL;
@GATE@
@REGION@
 return true;
}
static bool production_generic_admission(Asset *a)
{
@GENERIC@
 return true;
}
static FILE *scene_draw_commands;static unsigned game_probe_tick=270;
@SCENE_DRAW@
static void production_identity_checks(const char *path)
{
 Uint8 sample[4]={1,2,3,255};Asset identities[16];const int roles[]={108,135,136,137,138,139,140,141};
 const Asset **leases[]={&pulsing272_draw_lease,&triple275_draw_lease,&columns276_draw_lease,&turret273_draw_lease,&projectile304_draw_lease,&firing270_draw_lease};
 scene_draw_commands=fopen(path,"w+");assert(scene_draw_commands);bool old_probe=game_probe_enabled;game_probe_enabled=true;
 memset(regions,0,sizeof(regions));region_count=0;
 for(unsigned b=0;b<2;b++)for(unsigned r=0;r<8;r++){
  unsigned k=b*8+r;identities[k]=(Asset){true,true,roles[r],(int)(127+2*b),24,28,0,0,8,sample};Asset *a=&identities[k];
  for(unsigned j=0;j<6;j++)*leases[j]=NULL;unsigned before=region_count;
  assert(production_region_admission(100,80,a,MIRROR_NORMAL)==(roles[r]<136));
  if(roles[r]>=136){assert(region_count==before);
   /* Every other family's lease, and a copied asset object, are insufficient
    * even when source base, dimensions, position and style all match. */
   for(unsigned j=0;j<6;j++)if(j!=r-2){*leases[j]=a;assert(!production_region_admission(100,80,a,MIRROR_NORMAL));*leases[j]=NULL;}
   *leases[r-2]=a;
   assert(production_region_admission(100,80,a,MIRROR_NORMAL));Asset copied=*a;assert(!production_region_admission(100,80,&copied,MIRROR_NORMAL));}
  assert(region_count==before+1);assert(production_region_admission(100,80,a,MIRROR_NORMAL)&&region_count==before+1);
  production_scene_identity_draw(a->bank,(unsigned)a->index,100,80,0,MIRROR_NORMAL,true);
  if(roles[r]>=136){assert(!production_generic_admission(a));asteroid_hd_enabled=false;assert(!production_generic_admission(a)&&!production_region_admission(100,80,a,MIRROR_NORMAL));asteroid_hd_enabled=true;}
  for(unsigned j=0;j<6;j++)*leases[j]=NULL;
 }
 assert(region_count==16);for(unsigned k=0;k<16;k++){
  assert(regions[k].bank==identities[k].bank&&regions[k].index==identities[k].index&&regions[k].style==MIRROR_NORMAL&&regions[k].rect.x==100&&regions[k].rect.y==80&&regions[k].live);
  for(unsigned j=0;j<k;j++)assert(regions[j].bank!=regions[k].bank||regions[j].index!=regions[k].index);
 }
 fflush(scene_draw_commands);rewind(scene_draw_commands);
 for(unsigned k=0;k<16;k++){unsigned tick,index;int role,x,y,part,style,mirrored;
  assert(fscanf(scene_draw_commands,"%u\t%d\t%u\t%d\t%d\t%d\t%d\t%d",&tick,&role,&index,&x,&y,&part,&style,&mirrored)==8);
  assert(tick==270&&role==identities[k].bank&&index==(unsigned)identities[k].index&&x==100&&y==80&&!part&&style==MIRROR_NORMAL&&mirrored==1);
 }
 (void)fscanf(scene_draw_commands," ");assert(fgetc(scene_draw_commands)==EOF);assert(!fclose(scene_draw_commands));scene_draw_commands=NULL;game_probe_enabled=old_probe;
}

'''
    identity=identity.replace('@GATE@',gate).replace('@REGION@',region).replace('@GENERIC@',generic).replace('@SCENE_DRAW@',extract(source['game_probe.c'],'game_probe_scene_draw').replace('void game_probe_scene_draw(','static void production_scene_identity_draw('))
    projectile=r'''
/* Keep this body-only test on deliberately invalid two-byte112/113 sources.
 * Their sibling runtime suite executes the complete private142 guard.
 * Ordinary non-opt-in role8 dispatch remains eligible. */
static bool enemy_orb112113_draw(SDL_Surface *s,int x,int y,Sprite2_array b,unsigned i){(void)s;(void)x;(void)y;assert(b.size==2&&(i==112||i==113));return false;}
static bool projectile304_draw(SDL_Surface *s,int x,int y,Sprite2_array bank,unsigned index)
{(void)s;(void)x;(void)y;(void)bank;(void)index;assert(!"unexpected304 route");return false;}
static Asset assets[567];static unsigned generic_loads,projectile_draw_attempts;
static void render_mirror_shadow_end(void){}
static bool enemy_tank_shell_family_ready(void){assert(!"unexpected shell loading");return false;}
static bool enemy_energy_family_ready(void){assert(!"unexpected energy loading");return false;}
static bool read_asset(Asset *a,int density){assert(a->bank==8&&(a->index==112||a->index==113)&&(density==8||density==4));generic_loads++;if(!production_generic_admission(a))return false;a->density=density;return true;}
static bool draw_asset(int x,int y,Asset *a,int style,const SDL_Rect *part)
{assert(a->bank==8&&(a->index==112||a->index==113)&&!part);projectile_draw_attempts++;return production_region_admission(x,y,a,style);}
@ENERGY_SLOT@
@SHOT_DISPATCH@
static void production_projectile_classic(void)
{
 Uint8 dummy[2]={0};Sprite2_array old=spriteSheet8;bool old_hd=asteroid_hd_enabled;
 spriteSheet8=(Sprite2_array){sizeof(dummy),dummy};region_count=0;
 for(unsigned hd=0;hd<2;hd++)for(unsigned christmas=0;christmas<2;christmas++)for(unsigned cold=0;cold<2;cold++)for(unsigned index=112;index<=113;index++){
  asteroid_hd_enabled=hd;xmas=christmas;assets[218+index-112]=(Asset){true,true,8,(int)index,12,14,0,0,8,NULL};if(cold)memset(&assets[218+index-112],0,sizeof(Asset));
  unsigned loads=generic_loads,draws=projectile_draw_attempts;
  assert(enemy_energy_slot(index)<0);
  assert(render_mirror_enemy_shot(&surface,100,80,spriteSheet8,index)==(!hd&&!christmas));
  assert(projectile_draw_attempts==draws+(!christmas&&!hd));if(christmas)assert(generic_loads==loads);
 }
 assert(generic_loads&&projectile_draw_attempts==4);
 spriteSheet8=old;asteroid_hd_enabled=old_hd;xmas=false;region_count=0;
}
'''
    projectile=projectile.replace('@ENERGY_SLOT@',extract(renderer,'enemy_energy_slot')).replace('@SHOT_DISPATCH@',extract(renderer,'render_mirror_enemy_shot'))
    scaffolding=linked.MAIN[:linked.MAIN.index('static void exact_record_guards')].replace('linked338','firing270')
    scaffolding=scaffolding.replace('static struct {int x,y,x_velocity,cash;bool is_alive;} player[2];','struct PlayerStub {int x,y,x_velocity,y_velocity,cash,invulnerable_ticks;bool is_alive;};static struct PlayerStub player[2];')
    scaffolding=scaffolding.replace('c->type>=338&&c->type<=342','c->type==270').replace('return 115;','return 127;')
    scaffolding=scaffolding.replace(' uint64_t rng=mt_state_fingerprint();bool result=', ' Uint8 indexed_before[sizeof(pixels)];memcpy(indexed_before,pixels,sizeof(pixels));uint64_t rng=mt_state_fingerprint();bool result=')
    scaffolding=scaffolding.replace('mt_state_fingerprint()==rng);return result;','mt_state_fingerprint()==rng&&!memcmp(indexed_before,pixels,sizeof(pixels)));return result;')
    bstart=scaffolding.index('static void blit_enemy(');bend=scaffolding.index('@ENGINE_DRAW@',bstart)
    blit=r'''static const unsigned BASES[3]={127,129,131};
static uint64_t callback_hash;
@INDEXED@
static void blit_enemy(SDL_Surface *screen,int i,int dx,int dy,int part)
{
 unsigned base=enemy[i].egr[enemy[i].enemycycle-1];int x=enemy[i].ex+tempMapXOfs+dx,y=enemy[i].ey+dy;classic_calls++;
 int identity[]={enemy[i].enemytype,i,x,y,(int)base,part,enemy[i].filter,enemy[i].enemycycle};
 callback_hash^=asteroid1_stamp((const Uint8*)identity,sizeof(identity));callback_hash*=UINT64_C(1099511628211);
 if(mirror_calls){G101EnemyContext c=context((unsigned)i,enemy[i].enemytype);bool expected=c.type==270&&x>=0&&x<=308&&y>=-13&&y<=199;
  assert(checked_draw(screen,x,y,*enemy[i].sprite2s,base,part,enemy[i].filter,&c)==expected);assert(!reject_reason);
  if(expected){hd_calls++;hd_cycles|=1U<<(enemy[i].enemycycle-1);for(unsigned k=0;k<3;k++)if(base==BASES[k])hd_bases|=1U<<k;}}
 if(enemy[i].filter)engine_blit_sprite2_filter(screen,x,y,*enemy[i].sprite2s,base+part,enemy[i].filter);else engine_blit_sprite2(screen,x,y,*enemy[i].sprite2s,base+part);
}
'''.replace('@INDEXED@',indexed)
    scaffolding=scaffolding[:bstart]+blit+scaffolding[bend:]
    scaffolding=scaffolding.replace('@ENGINE_HOMING@','@ENGINE_RAM@')
    scaffolding=scaffolding.replace('mapX=1;','memset(pixels,0xa5,sizeof(pixels));callback_hash=UINT64_C(14695981039346656037);ram_damage_calls=0;mapX=1;')
    estart=scaffolding.index('static void load_events(');eend=scaffolding.index('struct Trace {',estart);scaffolding=scaffolding[:estart]+EVENTS+scaffolding[eend:]
    scaffolding=scaffolding.replace(' uint64_t rng;unsigned total,',' Uint8 indexed[sizeof(pixels)];struct JE_EventRecType events[6];uint64_t callbacks;uint64_t rng;unsigned total,')
    scaffolding=scaffolding.replace(' t->rng=mt_state_fingerprint();',' memcpy(t->indexed,pixels,sizeof(pixels));memcpy(t->events,eventRec,sizeof(eventRec));t->callbacks=callback_hash;t->rng=mt_state_fingerprint();')
    reused=''
    for name in ('exact_record_guards','source_guards','partial_geometry','warm_frame_guard','display_guards','resource_guards'):
        block=extract(ember.MAIN,name).replace('ember269','firing270').replace('269','270').replace('267','127')
        if name=='source_guards':
            block=block.replace('enemySpriteSheets[slot]=source;enemySpriteSheetIds[slot]=8;assert(firing270_source(source));','enemySpriteSheets[slot]=source;enemySpriteSheetIds[slot]=8;assert(firing270_source(source));actor(&source,25,270,0);c=context(25,270);assert(draw(source,&c));')
            block=block.replace('enemySpriteSheets[0]=source;enemySpriteSheetIds[0]=8;','enemySpriteSheets[0]=source;enemySpriteSheetIds[0]=8;actor(&source,25,270,0);c=context(25,270);')
            block=block.replace('enemySpriteSheetIds[slot]=17;assert(!firing270_source(source));enemySpriteSheetIds[slot]=8;', 'for(unsigned logical=0;logical<=255;logical++)if(logical!=8){enemySpriteSheetIds[slot]=logical;assert(!firing270_source(source)&&!draw(source,&c));}enemySpriteSheetIds[slot]=8;')
        if name=='exact_record_guards':
            block=block.replace('actor(&source,25,270,0);','actor(&source,25,270,0);enemy[25].aniactive=1;')
            # Verify every member, not only the current127 pose, while record trust
            # is broken. A cold frame must not count as an unsupported HD frame.
            block=block.replace('assert(!firing270_source(source));assert(!draw(source,&c));','assert(!firing270_source(source));for(unsigned m=0;m<3;m++){enemy[25].enemycycle=(unsigned[]){1,2,3}[m];assert(!draw(source,&c));}enemy[25].enemycycle=1;')
            block=block.replace('enemyDat[t].v^=bit_;assert(firing270_source(source));assert(!draw(source,&c));', 'for(unsigned m=0;m<3;m++){enemy[25].enemycycle=(unsigned[]){1,2,3}[m];assert(!draw(source,&c));}enemy[25].enemycycle=1;enemyDat[t].v^=bit_;assert(firing270_source(source));assert(!draw(source,&c));')
        if name=='partial_geometry':
            block=block.replace('const int origins[][2]={{-6,80},{302,80},{100,-20},{100,-13},{100,190},{100,199}};', 'const int origins[][2]={{-35,80},{-34,80},{-13,80},{-12,80},{-6,80},{0,80},{293,80},{294,80},{296,80},{302,80},{100,-34},{100,-33},{100,-32},{100,-27},{100,-26},{100,-20},{100,-13},{100,174},{100,175},{100,190},{100,199},{100,200}};')
            block=block.replace('bool expected=x>=0&&x<=308&&y>=-13&&y<=199;', 'bool expected=x>=0&&x<=308&&y>=-13&&y<=199&&enemy[25].ex+enemy[25].mapoffset>-29&&enemy[25].ex+enemy[25].mapoffset<300&&(!py?enemy[25].ey>-13:(enemy[25].ey>-26&&enemy[25].ey<182));')
        if name=='resource_guards':block=block.replace('member<4','member<3').replace('BAD_ASSET(bank,101);','BAD_ASSET(bank,108);BAD_ASSET(bank,135);BAD_ASSET(bank,136);BAD_ASSET(bank,137);BAD_ASSET(bank,138);BAD_ASSET(bank,139);BAD_ASSET(bank,140);')
        reused+=block+'\n'
    playershots=source['shots.h'];ps_end=playershots.index('} PlayerShotDataType;')+len('} PlayerShotDataType;');ps_start=playershots.rindex('typedef struct {',0,ps_end)
    replacements={'@PLAYER_SHOT_STRUCT@':playershots[ps_start:ps_end],'@SHOT_STRUCT@':varz[shot_start:shot_end],'@EXPLOSION_STRUCTS@':varz[expl_start:expl_end],
      '@EVENT_STRUCT@':varz[event_start:event_end],'@EXPLOSIONS@':extract(source['varz.c'],'JE_setupExplosion')+extract(source['varz.c'],'JE_setupExplosionLarge'),
      '@ENGINE_CONSTRUCTOR@':difficulty+'\n'+constructor+allocator,'@ENGINE_EVENTS@':events,'@ENGINE_DRAW@':draw,'@ENGINE_COLLISION@':collision,'@ENGINE_RAM@':ram,'@ENGINE_REPEATING@':repeating}
    maincode=scaffolding+identity+projectile+WEAPON+CHECKS+reused+MAIN_END
    for key,value in replacements.items():maincode=maincode.replace(key,value)
    code=prefix.replace('@SCOPE@',scopes).replace('@FAMILY@',structcode+common+shared+family+source['mtrand.c'])+maincode
    assert not re.search(r'@[A-Z_]+@',code)
    harness=a.out/'harness.c';harness.write_text(code)
    raw=(a.data/'tyrian.hdt').read_bytes();off=struct.unpack_from('<i',raw)[0]+14+1638*80+61*82+55*37+7*37+19*41+38*86+12*37
    assert hashlib.sha256(raw[off+270*77:off+271*77]).hexdigest()=='2734919844cbddb2751d2ebfbaf525ac19fcdb57e2ad8b039cf231e67f42db92'
    record=a.out/'original270-269-records.bin';record.write_bytes(b''.join(raw[off+t*77:off+(t+1)*77] for t in (270,269)));assert record.stat().st_size==154
    weapon=a.out/'original145-146-weapons.bin';wo=struct.unpack_from('<i',raw)[0]+14+145*80;weapon.write_bytes(raw[wo:wo+160]);assert [hashlib.sha256(weapon.read_bytes()[i*80:(i+1)*80]).hexdigest() for i in range(2)]==['7f27225dadd5c28dfb18be9166c6f75122eaf24de7ddf9b1dccfde47a10c1ea9','e0f2b49e0cd4bf20f24e7deac7b50bf09a20b2036443d05d7ac70510f1926e25']
    lvl=(a.data/'tyrian1.lvl').read_bytes();pos=struct.unpack_from('<i',lvl,2)[0];assert lvl[pos:pos+2]==b'EZ';nr=struct.unpack_from('<H',lvl,pos+8)[0];assert nr==21;pos+=10+nr*2;n=struct.unpack_from('<H',lvl,pos)[0];assert n==481;pos+=2
    ordinals=[377]
    neighbors=[i+1 for i in range(n) if struct.unpack_from('<Bh',lvl,pos+11*i+2)==(6,269)];assert neighbors
    selected=[lvl[pos+11*(i-1):pos+11*i] for i in ordinals+[neighbors[0]]]
    assert [x.hex() for x in selected[:1]]==['b018060e01ea0000000000']
    assert [i+1 for i in range(n) if struct.unpack_from('<Bh',lvl,pos+11*i+2)==(6,270)]==ordinals
    events_file=a.out/'original1-record270-and-neighbor269-events.bin';events_file.write_bytes(b''.join(selected))
    pack=root/'assets/hd/packs/asteroid1-ten-v1';arts=[pack/f'enemy-newshd-{base}-8.hda' for base in BASES];payloads=[x.read_bytes() for x in arts]
    for base,payload in zip(BASES,payloads):assert len(payload)==172060 and struct.unpack_from('<4s6I',payload)==(b'HDR1',1410000+base,8,24,28,0,0)
    fixtures=a.out/'fixtures';fixtures.mkdir();variants=[]
    kinds=('missing','payload','magic','role108','role135','role136','role137','role138','role139','role140','foreign-base','density','width','height','anchor-x','anchor-y','header-short','short','extra','fifo','directory','broken-symlink')
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
            elif kind.startswith('role'):struct.pack_into('<I',data,4,int(kind[4:])*10000+BASES[arts.index(art)])
            elif kind=='foreign-base':struct.pack_into('<I',data,4,1410123)
            elif kind=='header-short':data=data[:12]
            elif kind=='short':data=data[:-1]
            elif kind=='extra':data+=b'X'
            else:struct.pack_into('<I',data,dict(density=8,width=12,height=16,**{'anchor-x':20,'anchor-y':24})[kind],1)
            dest.write_bytes(data)
        variants.append(d)
    flags=['-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I'+str(root/'src')]+['-I'+x for x in a.sdl_include]
    if not a.sdl_include:flags+=subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True).split()
    outputs=[harness,record,events_file,weapon];compiler_peak=runtime_peak=0;runs=[]
    for mode in ['optimized']+(['asan-ubsan'] if a.sanitize else []):
        exe=a.out/mode;log=a.out/(mode+'-compile.log');compiler=['cc',*flags,'-O2']+(['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g'] if mode=='asan-ubsan' else [])
        compiler_peak=max(compiler_peak,linked.run_bounded([*compiler,str(harness),'-lm','-o',str(exe)],log,compiler=True));outputs += [exe,log]
        for i,(directory,expected) in enumerate([(pack,'accept')]+[(d,'reject') for d in variants]):
            log=a.out/f'{mode}-{i:03d}.log';runtime_peak=max(runtime_peak,linked.run_bounded([str(exe),str(a.data/'newshd.shp'),str(record),str(directory),expected,str(events_file),str(pack),str(a.out/f'identity-{mode}.tsv'),str(weapon)],log,sanitize=mode=='asan-ubsan'));outputs.append(log)
        match=re.search(r'admissions=(\d+) cycles=(\d+) images=(\d+); animation comparisons=(\d+); allocation cases=(\d+); damage cases=(\d+); canonical cold=(\d+) warm=(\d+)',(a.out/f'{mode}-000.log').read_text())
        assert match and tuple(map(int,match.groups()[1:]))==(63,7,23232,24,5,77,77)
        outputs.append(a.out/f'identity-{mode}.tsv')
        runs.append(dict(mode=mode,positive=1,negative=len(variants),production_HD_admissions=int(match[1]),binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    output_bytes=sum(x.stat().st_size for x in outputs)+sum(x.stat().st_size for d in variants for x in d.iterdir() if x.is_file() and not x.is_symlink())
    if output_bytes>OUTPUT_LIMIT:raise RuntimeError('Generated output exceeds64MiB')
    receipt=dict(records=[270],bases=BASES,material_role=141,source_bank=8,original_animation=2,
      original_sequence=[127,129,131,129,129,127],callback_animation_states={'active1':[1,2,3,4,5],'idle2':[1,6]},
      original_weapon_ids=[145,146],original_weapon_frequencies=[40,41],weapon_fnv64=['387b219ee9cab017','4623a676db5268a8'],
      cold_weapon_bytes=160,warm_weapon_bytes=160,cold_source_byte_mutations=42012,warm_source_byte_mutations=42012,cold_record_bytes=77,warm_record_bytes=77,canonical_mutation_member_callbacks=3,
      original_enemy_shot_dispatch=True,valid_generic112_113_decline_under_asteroid_optin=True,ordinary112_113_dispatch_unchanged=True,
      body_only=True,projectiles112_113='original indexed sprites, not HD closure',
      production_constructor=True,original_event_ordinals=ordinals,neighbor269_ordinal=neighbors[0],raw_events_unchanged=True,
      original_event_bytes=[x.hex() for x in selected[:1]],original_event_times=[6320],original_event_x=[234],actors_per_event=1,
      allocation_cases=24,allocation_free_slots=[0,1,2,3],allocation_holes=[25,34,49],synthetic_allocator_pool_limit=25,
      site_lifecycle_comparisons=120,production_animation_comparisons=23232,cycles=list(range(1,7)),firing_triggered=True,
      full_shot_pool_does_not_trigger=True,reverse_weapon_slot_order=True,successful_partial_pool_triggers=True,ice_retains_original_animation=True,
      production_damage_cases=5,normal_ice_and_lethal=True,independent_link0_death=True,original_explosion_allocation=True,original_repeating_explosion_RNG=True,
      production_ram_predicate_and_body=True,ram_positive_armor_values=255,ram_ice_values=256,INDEX8_byte_equality=True,classic_callback_trace_equality=True,
      source_bank269_record_independence=True,production_identity_equal_bases=[127,129],production_identity_materials=[108,135,136,137,138,139,140,141],
      production_distinct_regions=16,production_distinct_command_identities=16,private_role_generic_rejection=True,private_lease_cross_rejection=True,
      strict_sprite_object_binding=True,admitted_pool_slots=list(range(25,50)),source_logical_bank_exclusions=255,resource_role_rejections=[108,135,136,137,138,139,140],fixture_count=len(variants),
      compiler_peak_rss_bytes=compiler_peak,runtime_peak_rss_bytes=runtime_peak,compiler_address_space_limit_bytes=1024*MIB,runtime_rss_limit_bytes=512*MIB,
      runtime_timeout_seconds=120,compiler_timeout_seconds=90,output_limit_bytes=OUTPUT_LIMIT,output_bytes=output_bytes,runs=runs,leak_sanitizer=False,
      source_sha256={name:hashlib.sha256(text.encode()).hexdigest() for name,text in source.items()},
      harness_sha256=hashlib.sha256(harness.read_bytes()).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      original_record270_fnv64='eac063d6afea8edd',original_record270_sha256=hashlib.sha256(raw[off+270*77:off+271*77]).hexdigest(),
      original_weapon_sha256=[hashlib.sha256(weapon.read_bytes()[i*80:(i+1)*80]).hexdigest() for i in range(2)],
      original_level_sha256=hashlib.sha256(lvl).hexdigest(),original_NEWSHD_sha256=hashlib.sha256((a.data/'newshd.shp').read_bytes()).hexdigest(),
      identity_scope='Exact production admission guards, region registration, generic loading exclusion guards and complete scene-command serializer; compositor rasterization is separate.',
      scope='Body-only extracted production constructor, allocation, event6, draw including both original weapon firing paths, indexed tile writes, ordinary player-shot destruction, ram condition/body, explosion allocation and repeating effects with production MT RNG. Shared112/113 stay classic under asteroid opt-in. Real-engine evidence is separate.')
    (a.out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
