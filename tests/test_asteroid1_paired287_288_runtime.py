#!/usr/bin/env python3
"""Explicit-input extracted-production records287/288 binding and integrity tests.

Reads the named ten-family harness, named production renderer/family/struct
sources, fifteen named peer preflight includes, three HDAs and external
tyrian.hdt/newshd.shp. No test discovery, broad repository scan, private projection input, game launch or external upload.
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
         ('random286', 'asteroid_random286'), ('fork284', 'fork284'), ('capsule545', 'capsule545')]

MAIN = r'''

static unsigned cold_record_mutations,warm_record_mutations;
static G101EnemyContext context(unsigned slot,unsigned type)
{return (G101EnemyContext){type,slot,0,1,false,false,false,type==287};}
static void actor(Sprite2_array *bank,unsigned slot,unsigned type,unsigned link)
{
 struct JE_SingleEnemyType *e=&enemy[slot];memset(e,0,sizeof(*e));enemyAvail[slot]=0;
 e->enemytype=type;e->enemydatofs=&enemyDat[type];e->sprite2s=bank;e->size=1;
 e->linknum=link;e->armorleft=6;e->ani=type==287?1:20;e->animin=1;e->enemycycle=1;
 e->aniactive=type==287?0:1;e->exrev=e->eyrev=100;e->explonum=13;
 memcpy(e->egr,enemyDat[type].egraphic,sizeof(e->egr));
 e->ex=106;e->ey=87;
}
static unsigned selected_base(const G101EnemyContext *c)
{
 if(c&&c->type==288&&c->pool_slot<100) {
  unsigned cycle=enemy[c->pool_slot].enemycycle;
  if(cycle>=1&&cycle<=20)return enemy[c->pool_slot].egr[cycle-1];
  return 283;
 }
 return 245;
}
static bool draw(Sprite2_array source,const G101EnemyContext *c)
{return paired287_288_draw(&surface,100,80,source,selected_base(c),0,0,c);}
static void exact_record_guards(Sprite2_array source)
{
 G101EnemyContext c=context(25,287);actor(&source,25,287,24);
 /* Each of all 77 serialized bytes is independently changed both before any
  * accepted quadrant in a new tick, and after a valid first quadrant. */
 for(unsigned t=287;t<=288;t++) {
#define MUTATE(v) do { \
  for(unsigned bit_=1;bit_<=(sizeof(enemyDat[t].v)==2?256U:1U);bit_*=256U) { \
   mirror_logic_tick++;unsigned a_=accepted,r_=rejected; \
   enemyDat[t].v^=bit_;assert(!paired287_288_source(source));assert(!draw(source,&c)); \
   assert(accepted==a_&&rejected==r_&&!reject_reason); \
   enemyDat[t].v^=bit_;assert(paired287_288_source(source));cold_record_mutations++; \
   assert(draw(source,&c));a_=accepted;r_=rejected; \
   enemyDat[t].v^=bit_;assert(!paired287_288_draw(&surface,112,80,source,245,1,0,&c)); \
   assert(accepted==a_&&rejected==r_+1&&reject_reason&&strstr(reject_reason,"integrity")); \
   enemyDat[t].v^=bit_;assert(paired287_288_source(source));assert(!draw(source,&c)); \
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
 assert(cold_record_mutations==154&&warm_record_mutations==154);
}
static void source_guards(Sprite2_array source)
{
 Uint8 *raw=source.data,*rebound=malloc(source.size);assert(rebound);memcpy(rebound,raw,source.size);
 Sprite2_array alternate={source.size,rebound};G101EnemyContext c=context(25,287);
 assert(source.data!=asteroid1_source_snapshot.bytes);
 assert(!paired287_288_source((Sprite2_array){source.size,NULL}));
 assert(!paired287_288_source((Sprite2_array){source.size-1,raw}));
 assert(!paired287_288_source((Sprite2_array){source.size+1,raw}));
 assert(!paired287_288_source(alternate));
 spriteSheet8=alternate;assert(!paired287_288_source(alternate));
 enemySpriteSheets[0]=alternate;assert(!paired287_288_source(alternate));
 memset(&spriteSheet8,0,sizeof(spriteSheet8));assert(paired287_288_source(alternate));
 assert(!paired287_288_source(source));actor(&alternate,25,287,24);
 const unsigned offsets[]={0,200,42011};
 for(unsigned i=0;i<3;i++) {
  mirror_logic_tick++;unsigned before=rejected;
  rebound[offsets[i]]^=1;assert(!paired287_288_source(alternate));assert(!draw(alternate,&c));assert(rejected==before&&!reject_reason);
  rebound[offsets[i]]^=1;assert(draw(alternate,&c));before=rejected;
  rebound[offsets[i]]^=1;assert(!paired287_288_draw(&surface,112,80,alternate,245,1,0,&c));
  assert(rejected==before+1&&reject_reason);rebound[offsets[i]]^=1;reject_reason=NULL;
 }
 enemySpriteSheets[0]=source;actor(&source,25,287,24);free(rebound);assert(paired287_288_source(source));
 for(unsigned slot=0;slot<4;slot++) {
  memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
  enemySpriteSheets[slot]=source;enemySpriteSheetIds[slot]=8;assert(paired287_288_source(source));
  enemySpriteSheetIds[slot]=17;assert(!paired287_288_source(source));enemySpriteSheetIds[slot]=8;
  enemySpriteSheets[slot].size--;assert(!paired287_288_source(source));enemySpriteSheets[slot].size++;
 }
 memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
 enemySpriteSheets[0]=source;enemySpriteSheetIds[0]=8;
 spriteSheet8=source;assert(!paired287_288_source(source));memset(&spriteSheet8,0,sizeof(spriteSheet8));
 /* Same-address live mutation must not inherit snapshot or previous-draw trust. */
 for(unsigned i=0;i<3;i++) {
  mirror_logic_tick++;unsigned before=rejected;raw[offsets[i]]^=1;
  assert(!paired287_288_source(source));assert(!draw(source,&c));assert(rejected==before&&!reject_reason);
  raw[offsets[i]]^=1;assert(draw(source,&c));before=rejected;raw[offsets[i]]^=1;
  assert(!paired287_288_draw(&surface,112,80,source,245,1,0,&c));assert(rejected==before+1&&reject_reason);
  raw[offsets[i]]^=1;reject_reason=NULL;assert(paired287_288_source(source));
 }
 /* A cold corrupt source cannot initialize a trusted private snapshot. */
 asteroid1_source_snapshot.valid=false;raw[200]^=1;assert(!paired287_288_source(source));assert(!asteroid1_source_snapshot.valid);
 raw[200]^=1;assert(paired287_288_source(source));assert(asteroid1_source_snapshot.valid);
}

static void geometry_and_animation(Sprite2_array source)
{
 const unsigned slots[]={25,49},links[]={24,25,28,30,31,34,35};const int parts[]={0,1,19,20};
 assert(sizeof(paired287_288_pins)/sizeof(*paired287_288_pins)==2);
 assert(sizeof(paired287_288_images)/sizeof(*paired287_288_images)==3);
 for(unsigned type=287;type<=288;type++)for(unsigned s=0;s<2;s++)for(unsigned l=0;l<7;l++) {
  actor(&source,slots[s],type,links[l]);G101EnemyContext c=context(slots[s],type);
  struct JE_SingleEnemyType *e=&enemy[slots[s]];e->filter=17;
  for(unsigned cycle=1;cycle<=(type==287?1:20);cycle++) {
   e->enemycycle=cycle;unsigned base=type==287?245:cycle==7||cycle==10?281:283;
   assert(selected_base(&c)==base);
   for(unsigned p=0;p<4;p++) {
    int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
    assert(paired287_288_draw(&surface,100+px,80+py,source,base,part,17,&c));
    assert(last_x==100&&last_y==80&&last_part_x==px&&last_part_y==py&&last_filter==17);
    assert(last_asset==&paired287_288_resources.member[base==245?0:base==281?1:2]);
   }
  }
 }
 /* Replay original pre-increment/wrap selection; the guard never advances it. */
 actor(&source,25,288,24);G101EnemyContext c=context(25,288);struct JE_SingleEnemyType *e=&enemy[25];
 e->enemycycle=0;
 for(unsigned n=0;n<61;n++) {
  if(++e->enemycycle>e->ani)e->enemycycle=e->animin;
  unsigned cycle=e->enemycycle;assert(draw(source,&c));assert(e->enemycycle==cycle);
 }
 for(unsigned type=287;type<=288;type++) {
  actor(&source,25,type,24);c=context(25,type);e=&enemy[25];
  for(unsigned armor=1;armor<=255;armor++){e->armorleft=armor;assert(draw(source,&c));}
  const int values[]={-32768,-1,0,50,32767};
  for(unsigned i=0;i<5;i++){e->evalue=values[i];assert(draw(source,&c));}
  for(unsigned ice=0;ice<=255;ice++){e->iced=ice;assert(draw(source,&c));}
  /* Actual scrolling changes screen origin without intrinsic motion. */
  const unsigned scrolls[]={0,1,12,125};
  for(unsigned i=0;i<4;i++){e->mapoffset=scrolls[i];e->ex=106-(int)scrolls[i];assert(draw(source,&c));}
 }
 actor(&source,25,287,24);
}
static void independent_actors(Sprite2_array source)
{
 memset(enemyAvail,1,sizeof(enemyAvail));
 for(unsigned type=287;type<=288;type++) {
  actor(&source,25,type,24);G101EnemyContext c=context(25,type);assert(draw(source,&c));
  enemyAvail[25]=1;
 }
 /* Reverse allocation ordering is legal; neither draw inspects the other slot. */
 actor(&source,49,288,35);actor(&source,25,287,35);
 G101EnemyContext upper=context(25,287),lower=context(49,288);
 assert(draw(source,&upper)&&draw(source,&lower));
 enemyAvail[49]=1;assert(draw(source,&upper)); /* Failed lower allocation or independent lower cull. */
 enemyAvail[49]=0;enemy[49].ey=220;assert(draw(source,&upper));
 assert(!paired287_288_draw(&surface,100,213,source,283,0,0,&lower));
 actor(&source,49,288,35);enemyAvail[25]=1;assert(draw(source,&lower));
 enemy[25].ey=-80;assert(draw(source,&lower));
 actor(&source,25,287,24);
}
static void partial_geometry(Sprite2_array source)
{
 const int origins[][2]={{-6,80},{302,80},{100,-20},{100,-13},{100,190},{100,199}};
 const int parts[]={0,1,19,20};
 for(unsigned type=287;type<=288;type++)for(unsigned i=0;i<sizeof(origins)/sizeof(*origins);i++) {
  actor(&source,25,type,24);G101EnemyContext c=context(25,type);
  enemy[25].ex=origins[i][0]+6;enemy[25].ey=origins[i][1]+7;
  /* Preserve the original quadrant-local scope at partially clipped edges. */
  for(unsigned f=0;f<3;f++) {
   const int filters[]={0,17,255};enemy[25].filter=filters[f];
   for(unsigned p=0;p<4;p++) {
    int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
    int x=origins[i][0]+px,y=origins[i][1]+py;
    bool expected=x>=0&&x<=308&&y>=-13&&y<=199;
    unsigned a=accepted,l=logged;
    assert(paired287_288_draw(&surface,x,y,source,selected_base(&c),part,filters[f],&c)==expected);
    assert(accepted-a==(unsigned)expected&&logged-l==(unsigned)expected);
    if(expected)assert(last_x==origins[i][0]&&last_y==origins[i][1]&&
     last_part_x==px&&last_part_y==py&&last_filter==filters[f]);
   }
  }
 }
 actor(&source,25,287,24);
}
static void warm_frame_guard(Sprite2_array source)
{
 const int parts[]={0,1,19,20};
 for(unsigned type=287;type<=288;type++) {
  actor(&source,25,type,24);G101EnemyContext c=context(25,type);mirror_logic_tick++;
  assert(draw(source,&c));unsigned a=accepted,r=rejected,other=type==287?288:287,base=selected_base(&c);
  enemyDat[other].value^=1;
  assert(!paired287_288_draw(&surface,112,80,source,base,1,0,&c));
  assert(accepted==a&&rejected==r+1&&reject_reason&&!strcmp(reject_reason,"paired287_288-family-integrity"));
  enemyDat[other].value^=1;assert(paired287_288_source(source));
  for(unsigned p=0;p<4;p++) {
   int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
   assert(!paired287_288_draw(&surface,100+px,80+py,source,base,part,0,&c));
  }
  assert(accepted==a&&rejected==r+1);
  mirror_logic_tick++;reject_reason=NULL;assert(draw(source,&c));
  /* A resource-selection failure after an accepted component invalidates the
   * frame, including its previously accepted partner/quadrants. */
  const char *root=game_probe_assets;game_probe_assets="/foreign-paired-resource-root";
  a=accepted;r=rejected;assert(!draw(source,&c));assert(accepted==a&&rejected==r+1&&reject_reason);
  game_probe_assets=root;assert(!draw(source,&c));
  mirror_logic_tick++;reject_reason=NULL;assert(draw(source,&c));
 }
 actor(&source,25,287,24);
}

static void peer_state(bool expected)
{for(unsigned i=0;i<15;i++)assert(peer_ready[i]()==expected);}
static void independent_fallback(void)
{
 peer_state(true);assert(paired287_288_family_ready());
 for(unsigned member=0;member<3;member++) {
  mirror_logic_tick++;paired287_288_resources.member[member].rgba[10]^=1;
  assert(!paired287_288_family_ready());peer_state(true);
  paired287_288_resources.member[member].rgba[10]^=1;assert(!paired287_288_family_ready());
  paired287_288_shutdown();assert(paired287_288_family_ready());peer_state(true);
 }
 for(unsigned i=0;i<15;i++)peer_asset[i]->rgba[10]^=1;
 mirror_logic_tick++;peer_state(false);assert(paired287_288_family_ready());
 for(unsigned i=0;i<15;i++)peer_asset[i]->rgba[10]^=1;
 peer_state(false);assert(paired287_288_family_ready());
 for(unsigned i=0;i<15;i++)peer_shutdown[i]();
 peer_state(true);assert(paired287_288_family_ready());
 for(unsigned i=0;i<15;i++)peer_shutdown[i]();
}
static void actor_guards(Sprite2_array source)
{
 for(unsigned type=287;type<=288;type++) {
 G101EnemyContext c=context(25,type);actor(&source,25,type,24);
#define DECLINE assert(!draw(source,&c))
#define LIVE(field,value) do{struct JE_SingleEnemyType old=enemy[25];enemy[25].field=value;DECLINE;enemy[25]=old;}while(0)
#define CTX(field,value) do{G101EnemyContext old=c;c.field=value;DECLINE;c=old;}while(0)
 for(unsigned i=0;i<20;i++){unsigned old=enemy[25].egr[i];enemy[25].egr[i]=999;DECLINE;enemy[25].egr[i]=old;}
 LIVE(enemytype,type==287?288:287);LIVE(enemydatofs,NULL);LIVE(enemydatofs,&enemyDat[286]);LIVE(sprite2s,NULL);
 LIVE(size,0);LIVE(size,2);LIVE(scoreitem,true);LIVE(edamaged,true);LIVE(armorleft,0);
 LIVE(ani,0);LIVE(ani,type==287?20:1);LIVE(enemycycle,0);LIVE(enemycycle,type==287?2:21);
 LIVE(aniactive,type==287?1:0);LIVE(aniactive,2);LIVE(animin,0);LIVE(animin,2);LIVE(animax,1);LIVE(aniwhenfire,2);LIVE(filter,1);
 LIVE(tur[0],59);LIVE(tur[1],1);LIVE(tur[2],1);LIVE(freq[0],1);LIVE(freq[1],1);LIVE(freq[2],1);
 LIVE(launchfreq,1);LIVE(launchtype,532);LIVE(launchspecial,1);LIVE(edgr,1);LIVE(edlevel,1);LIVE(edani,1);
 LIVE(enemydie,1);LIVE(enemydie,512);LIVE(enemydie,611);LIVE(enemyground,true);LIVE(explonum,12);
 LIVE(exc,1);LIVE(eyc,-1);LIVE(fixedmovey,1);LIVE(excc,1);LIVE(eycc,-1);LIVE(xaccel,1);LIVE(yaccel,1);
 LIVE(exrev,0);LIVE(eyrev,0);LIVE(ex,107);LIVE(ey,88);LIVE(mapoffset,1);
 const unsigned badlinks[]={0,1,23,26,27,29,32,33,36,255};
 for(unsigned l=0;l<sizeof(badlinks)/sizeof(*badlinks);l++)LIVE(linknum,badlinks[l]);
 Sprite2_array wrong={source.size-1,source.data};LIVE(sprite2s,&wrong);
 wrong=(Sprite2_array){source.size,asteroid1_source_snapshot.bytes};LIVE(sprite2s,&wrong);
 CTX(type,286);CTX(type,289);CTX(type,type==287?288:287);
 const unsigned badslots[]={0,24,50,74,75,99,100,UINT_MAX};
 for(unsigned s=0;s<sizeof(badslots)/sizeof(*badslots);s++)CTX(pool_slot,badslots[s]);
 CTX(availability,1);CTX(availability,2);CTX(availability,UINT_MAX);CTX(size,0);CTX(size,2);
 CTX(score_item,true);CTX(damaged,true);CTX(static_animation,type!=287);CTX(independent_motion,true);
 enemyAvail[25]=1;DECLINE;enemyAvail[25]=2;DECLINE;enemyAvail[25]=0;assert(!draw(source,NULL));
 unsigned base=selected_base(&c);
 const unsigned badbases[]={0,244,246,280,282,284};
 for(unsigned i=0;i<sizeof(badbases)/sizeof(*badbases);i++)assert(!paired287_288_draw(&surface,100,80,source,badbases[i],0,0,&c));
 if(type==287)assert(!paired287_288_draw(&surface,100,80,source,283,0,0,&c));
 else {
  for(unsigned cycle=1;cycle<=20;cycle++) {
   enemy[25].enemycycle=cycle;unsigned other=cycle==7||cycle==10?283:281;
   assert(!paired287_288_draw(&surface,100,80,source,other,0,0,&c));
  }
  enemy[25].enemycycle=1;
 }
 const int badparts[]={INT_MIN,-1,2,18,21,INT_MAX};
 for(unsigned i=0;i<sizeof(badparts)/sizeof(*badparts);i++)assert(!paired287_288_draw(&surface,100,80,source,base,badparts[i],0,&c));
 assert(!paired287_288_draw(&surface,100,80,source,base,0,-1,&c));assert(!paired287_288_draw(&surface,100,80,source,base,0,256,&c));
 const int badx[]={INT_MIN,-1,309,INT_MAX},bady[]={INT_MIN,-14,200,INT_MAX};
 for(unsigned i=0;i<4;i++){assert(!paired287_288_draw(&surface,badx[i],80,source,base,0,0,&c));assert(!paired287_288_draw(&surface,100,bady[i],source,base,0,0,&c));}
#undef CTX
#undef LIVE
#undef DECLINE
 }
 actor(&source,25,287,24);
}
static void display_guards(Sprite2_array source)
{
 G101EnemyContext c=context(25,287);actor(&source,25,287,24);
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
 assert(!paired287_288_draw(NULL,100,80,source,245,0,0,&c));assert(!paired287_288_draw(&other,100,80,source,245,0,0,&c));
 /* Probe lease bypass is restricted to the same exact level scope. */
 game_probe_enabled=true;asteroid_hd_lease=false;assert(draw(source,&c));
 lvlFileNum=2;DECLINE;lvlFileNum=1;game_probe_enabled=false;asteroid_hd_lease=true;
 assert(draw(source,&c));
#undef DECLINE
}
static void resource_guards(void)
{
 const char *root=game_probe_assets;
 game_probe_assets=NULL;assert(!paired287_288_family_ready());game_probe_assets="";assert(!paired287_288_family_ready());
 char longroot[1025];memset(longroot,'x',sizeof(longroot)-1);longroot[sizeof(longroot)-1]=0;
 game_probe_assets=longroot;assert(!paired287_288_family_ready());game_probe_assets="/foreign-paired287_288-root";assert(!paired287_288_family_ready());game_probe_assets=root;
 game_probe_density=4;assert(!paired287_288_family_ready());game_probe_density=0;assert(!paired287_288_family_ready());game_probe_density=8;
 game_probe_missing=true;assert(!paired287_288_family_ready());game_probe_missing=false;
 game_probe_invalid=true;assert(!paired287_288_family_ready());game_probe_invalid=false;
 game_probe_original_reference=true;assert(!paired287_288_family_ready());game_probe_original_reference=false;
 assert(paired287_288_family_ready());
 for(unsigned member=0;member<3;member++) {
#define BAD_ASSET(field,value) do{Asset old=paired287_288_resources.member[member];mirror_logic_tick++;paired287_288_resources.member[member].field=value;assert(!paired287_288_family_ready());paired287_288_resources.member[member]=old;assert(!paired287_288_family_ready());paired287_288_shutdown();assert(paired287_288_family_ready());}while(0)
 BAD_ASSET(initialized,false);BAD_ASSET(valid,false);BAD_ASSET(bank,101);BAD_ASSET(index,123);BAD_ASSET(w,12);BAD_ASSET(h,14);
 BAD_ASSET(anchor_x,1);BAD_ASSET(anchor_y,1);BAD_ASSET(density,4);BAD_ASSET(rgba,NULL);
#undef BAD_ASSET
 mirror_logic_tick++;paired287_288_resources.member[member].rgba[10]^=1;assert(!paired287_288_family_ready());
 paired287_288_resources.member[member].rgba[10]^=1;assert(!paired287_288_family_ready());paired287_288_shutdown();assert(paired287_288_family_ready());
 }
}

int main(int argc,char **argv)
{
 assert(argc==5);game_probe_assets=argv[3];records(argv[2]);
 FILE *f=fopen(argv[1],"rb");assert(f);Uint8 *raw=malloc(42012);
 assert(raw&&fread(raw,1,42012,f)==42012&&fgetc(f)==EOF);fclose(f);
 enemySpriteSheets[0]=(Sprite2_array){42012,raw};enemySpriteSheetIds[0]=8;Sprite2_array source=enemySpriteSheets[0];
 assert(paired287_288_source(source)&&asteroid1_scope());actor(&source,25,287,24);G101EnemyContext c=context(25,287);
 if(!strcmp(argv[4],"reject")||!strcmp(argv[4],"peers-only")) {
  if(!strcmp(argv[4],"peers-only"))peer_state(true);
  assert(!paired287_288_family_ready());assert(!draw(source,&c));assert(!accepted&&!rejected);
  for(unsigned type=287;type<=288;type++) {
   actor(&source,25,type,24);c=context(25,type);assert(!draw(source,&c));
  }
  paired287_288_shutdown();for(unsigned i=0;i<15;i++)peer_shutdown[i]();
  free(raw);puts("paired287/288 invalid member keeps whole family classic; peers independent");return 0;
 }
 assert(!strcmp(argv[4],"accept")||!strcmp(argv[4],"own-only"));assert(paired287_288_family_ready());
 if(!strcmp(argv[4],"accept"))independent_fallback();else {peer_state(false);for(unsigned i=0;i<15;i++)peer_shutdown[i]();}
 exact_record_guards(source);source_guards(source);geometry_and_animation(source);independent_actors(source);
 partial_geometry(source);warm_frame_guard(source);actor_guards(source);display_guards(source);resource_guards();
 paired287_288_shutdown();free(raw);
 puts("paired287/288 all154 cold+warm bytes; pool25-49 all7 links; all20 lower cycles; independent actors; geometry, live/display/loader integrity passed");return 0;
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
    family_path = root / 'src/asteroid1_paired287_288_mirror.inc'
    shared_path = root / 'src/asteroid1_ten_mirror.inc'
    struct_path = root / 'src/varz.h'
    snapshot_path = root / 'src/asteroid1_source_snapshot.inc'
    pack = root / 'assets/hd/packs/asteroid1-ten-v1'
    arts = [pack / f'enemy-newshd-{base}-8.hda' for base in (245,281,283)]
    peer_paths = [root / 'src' / f'asteroid1_{name}_mirror.inc' for name, _ in PEERS]
    allowlist = {helper, source_path, family_path, shared_path, struct_path, snapshot_path,
                 *arts, a.data / 'tyrian.hdt', a.data / 'newshd.shp', *peer_paths}

    def read(path, binary=False):
        if path not in allowlist:
            raise RuntimeError('Input outside explicit allowlist')
        return path.read_bytes() if binary else path.read_text()

    import shutil
    if shutil.disk_usage(a.out).free < 5_000_000_000:
        raise RuntimeError('At least 5 GB free is required')
    payloads = [read(art, True) for art in arts]
    for base, payload in zip((245,281,283), payloads):
        if len(payload) != 172060 or struct.unpack_from('<4s6I', payload) != (b'HDR1',1080000+base,8,24,28,0,0):
            raise RuntimeError('Unexpected paired installation resource header or size')
    spec = importlib.util.spec_from_file_location('paired287_288_named_ten_harness', helper)
    ten = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ten)
    source, family, shared, varz = read(source_path), read(family_path), read(shared_path), read(struct_path)
    assert 'paired287_288_shutdown();' in ten.extract(source, 'render_mirror_hud_shutdown')
    assert 'return paired287_288_draw(' in ten.extract(source, 'render_mirror_enemy_tile')
    start = varz.index('struct JE_SingleEnemyType\n{')
    end = varz.index('\n};', start) + 3
    structcode = varz[start:end] + '\nstatic struct JE_SingleEnemyType enemy[100];\nstatic unsigned char enemyAvail[100];\n'
    prefix = ten.HARNESS.split('int main(int argc', 1)[0].replace('t=444;t<=453', 't=287;t<=288')
    prefix = prefix.replace('static Uint8 last_filter;', 'static Uint8 last_filter;static Asset *last_asset;')
    prefix = prefix.replace('accepted++;last_x=x;', 'last_asset=a;accepted++;last_x=x;')
    prefix = prefix.replace('assert(a&&a->bank==108', 'assert(a&&(a->index==245||a->index==281||a->index==283)&&a->w==24&&a->h==28&&part&&part->w==12&&part->h==14&&a->bank==108')
    scopes = ten.extract(source, 'asteroid1_level_scope') + ten.extract(source, 'asteroid1_scope')
    common = ten.extract(shared, 'asteroid1_stamp') + '#include "asteroid1_source_snapshot.inc"\n' + ten.extract(shared, 'asteroid1_record_stamp')
    peer_code, peer_bases = '', set()
    for (_, peer), path in zip(PEERS, peer_paths):
        text = read(path)
        pins = re.search(r'static const struct \{[^\n]+\} ' + peer + r'_pins\[\d+\]=\{.*?\n\};', text, re.S)
        resources = re.search(r'static struct \{[^\n]+\} ' + peer + r'_resources;', text)
        if not pins or not resources:
            raise RuntimeError('Unexpected peer preflight declarations: ' + peer)
        peer_code += pins.group() + '\n' + resources.group() + '\n'
        for function in ['shutdown', 'load', 'family_ready']:
            peer_code += ten.extract(text, peer + '_' + function)
        peer_bases.update(int(base) for base in re.findall(r'\{\d+,(\d+),', pins.group()))
    if len(peer_bases) != 35 or peer_bases.intersection({245,281,283}):
        raise RuntimeError('Unexpected existing peer image closure')
    peer_code += 'static bool (*peer_ready[])(void)={' + ','.join(peer + '_family_ready' for _, peer in PEERS) + '};\n'
    peer_code += 'static void (*peer_shutdown[])(void)={' + ','.join(peer + '_shutdown' for _, peer in PEERS) + '};\n'
    peer_code += 'static Asset *peer_asset[]={' + ','.join('&' + peer + '_resources.member[0]' for _, peer in PEERS) + '};\n'
    code = prefix.replace('@SCOPE@', scopes).replace('@FAMILY@', structcode + common + family + peer_code) + MAIN
    harness = remember(a.out / 'harness.c')
    harness.write_text(code)
    raw = read(a.data / 'tyrian.hdt', True)
    off = struct.unpack_from('<i', raw)[0] + 14 + 1638*80 + 61*82 + 55*37 + 7*37 + 19*41 + 38*86 + 12*37
    record = remember(a.out / 'original287-288-records.bin')
    record.write_bytes(raw[off+287*77:off+289*77])
    if record.stat().st_size != 154:
        raise RuntimeError('Short original records287/288')
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
        compiler_peak = max(compiler_peak, run_bounded([*compiler,str(harness),'-o',str(exe)], remember(a.out / f'{mode}-compile.log'), compiler=True))
        output_bound()
        for i, (directory, expected) in enumerate([(pack,'accept'),(isolated,'own-only'),(peer_only,'peers-only')] + [(d,'reject') for d in variants]):
            runtime_peak = max(runtime_peak, run_bounded([str(exe),str(a.data/'newshd.shp'),str(record),str(directory),expected], remember(a.out / f'{mode}-{i:02d}.log'), sanitize=mode == 'asan-ubsan'))
            output_bound()
        runs.append(dict(mode=mode,positive=2,peer_independence=1,negative=len(variants),binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    result = dict(records=[287,288],bases=[245,281,283],logical_size=[24,28],density=8,
                  cold_source_record_byte_mutations=154,warm_source_record_byte_mutations=154,
                  boundary_pool_slots=[25,49],accepted_links=[24,25,28,30,31,34,35],
                  lower_cycles=list(range(1,21)),lower_lamp281_cycles=[7,10],
                  independent_actors=True,positive_armor_values=255,ice_values=256,
                  clipping_origins=6,clipping_filters=[0,17,255],fixture_count=len(variants),
                  independent_peer_families=15,sticky_whole_frame=True,
                  compiler_peak_rss_bytes=compiler_peak,runtime_peak_rss_bytes=runtime_peak,
                  compiler_address_space_limit_bytes=1024*MIB,runtime_rss_limit_bytes=512*MIB,
                  output_limit_bytes=OUTPUT_LIMIT,output_bytes=output_bound(),runs=runs,
                  source_sha256=hashlib.sha256(family.encode()).hexdigest(),leak_sanitizer=False,
                  scope='Extracted production functions and full live struct. Independent actor admission and original cycle selection tested; actual engine event/RNG/destruction validation is separate.')
    receipt = remember(a.out / 'receipt.json')
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    output_bound()
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
