#!/usr/bin/env python3
"""Explicit-input extracted-production record545 binding and integrity tests.

Reads the named ten-family harness, named production renderer/family/struct
sources, fourteen named peer preflight includes, one HDA and external
tyrian.hdt/newshd.shp. No test discovery, broad repository scan, private projection input, game launch or external upload.
Generated outputs are bounded to 8 MiB. Runtime is bounded to 512 MiB RSS;
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
OUTPUT_LIMIT = 8 * MIB
DEFAULT_REPO = Path(__file__).resolve().parents[1]
PEERS = [('ten', 'asteroid1'), ('four', 'asteroid4'),
         ('common4', 'asteroid_common4'), ('random5', 'asteroid_random5'),
         ('goldwing', 'goldwing'), ('random43', 'asteroid_random43'),
         ('random85', 'asteroid_random85'), ('random123', 'asteroid_random123'),
         ('random95', 'asteroid_random95'), ('random114', 'asteroid_random114'),
         ('random133', 'asteroid_random133'), ('random152', 'asteroid_random152'),
         ('random286', 'asteroid_random286'), ('fork284', 'fork284')]

MAIN = r'''
static unsigned cold_record_mutations,warm_record_mutations;
static G101EnemyContext context(unsigned slot)
{
 return (G101EnemyContext){545,slot,0,1,false,false,true,true};
}
static void actor(Sprite2_array *bank,unsigned slot,unsigned link)
{
 struct JE_SingleEnemyType *e=&enemy[slot];memset(e,0,sizeof(*e));enemyAvail[slot]=0;
 e->enemytype=545;e->enemydatofs=&enemyDat[545];e->sprite2s=bank;e->size=1;
 e->linknum=link;e->armorleft=6;e->ani=1;e->animin=1;e->enemycycle=1;
 memcpy(e->egr,enemyDat[545].egraphic,sizeof(e->egr));e->eyc=2;
 e->ex=106;e->ey=87;e->mapoffset=0;
}
static bool draw(Sprite2_array source,const G101EnemyContext *c)
{return capsule545_draw(&surface,100,80,source,77,0,0,c);}
static void exact_record_guards(Sprite2_array source)
{
 G101EnemyContext c=context(75);actor(&source,75,1);unsigned t=545;
 /* Each of all 77 serialized bytes is independently changed both before any
  * accepted quadrant in a new tick, and after a valid first quadrant. */
#define MUTATE(v) do { \
  for(unsigned bit_=1;bit_<=(sizeof(enemyDat[t].v)==2?256U:1U);bit_*=256U) { \
   mirror_logic_tick++;unsigned a_=accepted,r_=rejected; \
   enemyDat[t].v^=bit_;assert(!capsule545_source(source));assert(!draw(source,&c)); \
   assert(accepted==a_&&rejected==r_&&!reject_reason); \
   enemyDat[t].v^=bit_;assert(capsule545_source(source));cold_record_mutations++; \
   assert(draw(source,&c));a_=accepted;r_=rejected; \
   enemyDat[t].v^=bit_;assert(!capsule545_draw(&surface,112,80,source,77,1,0,&c)); \
   assert(accepted==a_&&rejected==r_+1&&reject_reason&&strstr(reject_reason,"integrity")); \
   enemyDat[t].v^=bit_;assert(capsule545_source(source));assert(!draw(source,&c)); \
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
 assert(cold_record_mutations==77&&warm_record_mutations==77);
}
static void source_guards(Sprite2_array source)
{
 Uint8 *raw=source.data,*rebound=malloc(source.size);assert(rebound);memcpy(rebound,raw,source.size);
 Sprite2_array alternate={source.size,rebound};G101EnemyContext c=context(75);
 assert(source.data!=asteroid1_source_snapshot.bytes);
 assert(!capsule545_source((Sprite2_array){source.size,NULL}));
 assert(!capsule545_source((Sprite2_array){source.size-1,raw}));
 assert(!capsule545_source((Sprite2_array){source.size+1,raw}));
 assert(!capsule545_source(alternate));
 spriteSheet8=alternate;assert(!capsule545_source(alternate));
 enemySpriteSheets[0]=alternate;assert(!capsule545_source(alternate));
 memset(&spriteSheet8,0,sizeof(spriteSheet8));assert(capsule545_source(alternate));
 assert(!capsule545_source(source));actor(&alternate,75,1);
 const unsigned offsets[]={0,200,42011};
 for(unsigned i=0;i<3;i++) {
  mirror_logic_tick++;unsigned before=rejected;
  rebound[offsets[i]]^=1;assert(!capsule545_source(alternate));assert(!draw(alternate,&c));assert(rejected==before&&!reject_reason);
  rebound[offsets[i]]^=1;assert(draw(alternate,&c));before=rejected;
  rebound[offsets[i]]^=1;assert(!capsule545_draw(&surface,112,80,alternate,77,1,0,&c));
  assert(rejected==before+1&&reject_reason);rebound[offsets[i]]^=1;reject_reason=NULL;
 }
 enemySpriteSheets[0]=source;actor(&source,75,1);free(rebound);assert(capsule545_source(source));
 for(unsigned slot=0;slot<4;slot++) {
  memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
  enemySpriteSheets[slot]=source;enemySpriteSheetIds[slot]=8;assert(capsule545_source(source));
  enemySpriteSheetIds[slot]=17;assert(!capsule545_source(source));enemySpriteSheetIds[slot]=8;
  enemySpriteSheets[slot].size--;assert(!capsule545_source(source));enemySpriteSheets[slot].size++;
 }
 memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
 enemySpriteSheets[0]=source;enemySpriteSheetIds[0]=8;
 spriteSheet8=source;assert(!capsule545_source(source));memset(&spriteSheet8,0,sizeof(spriteSheet8));
 /* Same-address live mutation must not inherit snapshot or previous-draw trust. */
 for(unsigned i=0;i<3;i++) {
  mirror_logic_tick++;unsigned before=rejected;raw[offsets[i]]^=1;
  assert(!capsule545_source(source));assert(!draw(source,&c));assert(rejected==before&&!reject_reason);
  raw[offsets[i]]^=1;assert(draw(source,&c));before=rejected;raw[offsets[i]]^=1;
  assert(!capsule545_draw(&surface,112,80,source,77,1,0,&c));assert(rejected==before+1&&reject_reason);
  raw[offsets[i]]^=1;reject_reason=NULL;assert(capsule545_source(source));
 }
 /* A cold corrupt source cannot initialize a trusted private snapshot. */
 asteroid1_source_snapshot.valid=false;raw[200]^=1;assert(!capsule545_source(source));assert(!asteroid1_source_snapshot.valid);
 raw[200]^=1;assert(capsule545_source(source));assert(asteroid1_source_snapshot.valid);
}
static void geometry_and_motion(Sprite2_array source)
{
 const unsigned slots[]={75,99},links[]={1,9};const int parts[]={0,1,19,20};
 unsigned a=accepted,l=logged;
 assert(sizeof(capsule545_pins)/sizeof(*capsule545_pins)==1);
 assert(capsule545_pins[0].type==545&&capsule545_pins[0].base==77&&capsule545_pins[0].size==1);
 for(unsigned s=0;s<2;s++) {
  actor(&source,slots[s],links[s]);G101EnemyContext c=context(slots[s]);enemy[slots[s]].filter=17;
  for(unsigned p=0;p<4;p++) {
   int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
   assert(capsule545_draw(&surface,100+px,80+py,source,77,part,17,&c));
   assert(last_x==100&&last_y==80&&last_part_x==px&&last_part_y==py&&last_filter==17);
   assert(last_asset==&capsule545_resources.member[0]);
  }
 }
 assert(accepted-a==8&&logged-l==8);
 actor(&source,75,1);G101EnemyContext c=context(75);struct JE_SingleEnemyType *e=&enemy[75];
 /* Original event19 supplies zero, down6/down3, left4 and right4 motion.
  * Later event20/27 and other engine changes remain authoritative. */
 const int motion[][4]={{0,0,0,0},{0,6,0,0},{0,3,0,0},{-4,0,0,0},{4,0,0,0},
  {-8,2,-1,0},{8,-6,0,-1},{7,2,7,-9},{-7,3,-7,-6},{9,-1,9,6},{-9,0,-9,6}};
 for(unsigned i=0;i<sizeof(motion)/sizeof(*motion);i++) {
  e->exc=motion[i][0];e->eyc=motion[i][1];e->excc=motion[i][2];e->eycc=motion[i][3];
  c.independent_motion=(bool)(e->exc||e->eyc||e->excc||e->eycc);assert(draw(source,&c));
 }
 c.independent_motion=true;
 e->exc=-128;e->eyc=127;e->excc=-128;e->eycc=127;e->fixedmovey=-32768;e->xaccel=255;e->yaccel=255;
 e->exrev=-128;e->eyrev=127;e->exccw=-128;e->eyccw=127;e->exccwmax=255;e->eyccwmax=255;
 e->exccadd=-32768;e->eyccadd=32767;assert(draw(source,&c));
 e->exc=127;e->eyc=-128;e->excc=127;e->eycc=-128;e->fixedmovey=32767;assert(draw(source,&c));
 actor(&source,75,1);e=&enemy[75];e->eyc=0;c.independent_motion=false;assert(draw(source,&c));
 actor(&source,75,1);c=context(75);
 for(unsigned armor=1;armor<=255;armor++){enemy[75].armorleft=armor;assert(draw(source,&c));}
 actor(&source,75,1);
 for(unsigned link=1;link<=9;link++){enemy[75].linknum=link;assert(draw(source,&c));}
 actor(&source,75,1);
}
static void partial_geometry(Sprite2_array source)
{
 const int origins[][2]={{-6,80},{302,80},{100,-20},{100,-13},{100,190},{100,199}};
 const int parts[]={0,1,19,20};
 for(unsigned i=0;i<sizeof(origins)/sizeof(*origins);i++) {
  actor(&source,75,1);G101EnemyContext c=context(75);
  enemy[75].ex=origins[i][0]+6;enemy[75].ey=origins[i][1]+7;
  /* Preserve the original quadrant-local scope at partially clipped edges. */
  for(unsigned f=0;f<3;f++) {
   const int filters[]={0,17,255};enemy[75].filter=filters[f];
   for(unsigned p=0;p<4;p++) {
    int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
    int x=origins[i][0]+px,y=origins[i][1]+py;
    bool expected=x>=0&&x<=308&&y>=-13&&y<=199;
    unsigned a=accepted,l=logged;
    assert(capsule545_draw(&surface,x,y,source,77,part,filters[f],&c)==expected);
    assert(accepted-a==(unsigned)expected&&logged-l==(unsigned)expected);
    if(expected)assert(last_x==origins[i][0]&&last_y==origins[i][1]&&
     last_part_x==px&&last_part_y==py&&last_filter==filters[f]);
   }
  }
 }
 actor(&source,75,1);
}
static void warm_frame_guard(Sprite2_array source)
{
 actor(&source,75,1);G101EnemyContext c=context(75);mirror_logic_tick++;
 assert(draw(source,&c));unsigned a=accepted,r=rejected;
 enemyDat[545].value^=1;
 assert(!capsule545_draw(&surface,112,80,source,77,1,0,&c));
 assert(accepted==a&&rejected==r+1&&reject_reason&&!strcmp(reject_reason,"capsule545-family-integrity"));
 enemyDat[545].value^=1;assert(capsule545_source(source));
 const int parts[]={0,1,19,20};
 for(unsigned p=0;p<4;p++) {
  int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
  assert(!capsule545_draw(&surface,100+px,80+py,source,77,part,0,&c));
 }
 assert(accepted==a&&rejected==r+1);
 /* The renderer clears its frame rejection before the next display frame. */
 mirror_logic_tick++;reject_reason=NULL;assert(draw(source,&c));
}
static void peer_state(bool expected)
{
 for(unsigned i=0;i<14;i++)assert(peer_ready[i]()==expected);
}
static void independent_fallback(void)
{
 peer_state(true);assert(capsule545_family_ready());
 mirror_logic_tick++;capsule545_resources.member[0].rgba[10]^=1;
 assert(!capsule545_family_ready());peer_state(true);
 capsule545_resources.member[0].rgba[10]^=1;assert(!capsule545_family_ready());
 capsule545_shutdown();assert(capsule545_family_ready());peer_state(true);
 for(unsigned i=0;i<14;i++)peer_asset[i]->rgba[10]^=1;
 mirror_logic_tick++;peer_state(false);assert(capsule545_family_ready());
 for(unsigned i=0;i<14;i++)peer_asset[i]->rgba[10]^=1;
 peer_state(false);assert(capsule545_family_ready());
 for(unsigned i=0;i<14;i++)peer_shutdown[i]();
 peer_state(true);assert(capsule545_family_ready());
 for(unsigned i=0;i<14;i++)peer_shutdown[i]();
}
static void actor_guards(Sprite2_array source)
{
 G101EnemyContext c=context(75);actor(&source,75,1);
#define DECLINE assert(!draw(source,&c))
#define LIVE(field,value) do{struct JE_SingleEnemyType old=enemy[75];enemy[75].field=value;DECLINE;enemy[75]=old;}while(0)
#define CTX(field,value) do{G101EnemyContext old=c;c.field=value;DECLINE;c=old;}while(0)
 for(unsigned i=0;i<20;i++){unsigned old=enemy[75].egr[i];enemy[75].egr[i]=999;DECLINE;enemy[75].egr[i]=old;}
 LIVE(enemytype,282);LIVE(enemytype,286);LIVE(enemydatofs,NULL);LIVE(enemydatofs,&enemyDat[283]);LIVE(sprite2s,NULL);
 LIVE(size,0);LIVE(size,2);LIVE(scoreitem,true);LIVE(edamaged,true);LIVE(armorleft,0);
 LIVE(ani,0);LIVE(ani,2);LIVE(enemycycle,0);LIVE(enemycycle,2);LIVE(aniactive,1);LIVE(aniactive,2);
 LIVE(animin,0);LIVE(animin,2);LIVE(animax,1);LIVE(aniwhenfire,2);LIVE(filter,1);
 LIVE(tur[0],59);LIVE(tur[1],1);LIVE(tur[2],1);LIVE(freq[0],1);LIVE(freq[1],1);LIVE(freq[2],1);
 LIVE(launchfreq,1);LIVE(launchtype,532);LIVE(launchspecial,1);LIVE(edgr,1);LIVE(edlevel,1);LIVE(edani,1);
 LIVE(linknum,0);LIVE(linknum,10);LIVE(linknum,255);LIVE(enemydie,1);LIVE(enemydie,512);LIVE(enemydie,611);
 LIVE(ex,107);LIVE(ey,88);LIVE(mapoffset,1);
 Sprite2_array wrong={source.size-1,source.data};LIVE(sprite2s,&wrong);
 wrong=(Sprite2_array){source.size,asteroid1_source_snapshot.bytes};LIVE(sprite2s,&wrong);
 CTX(type,282);CTX(type,285);CTX(pool_slot,0);CTX(pool_slot,24);CTX(pool_slot,25);CTX(pool_slot,49);CTX(pool_slot,50);CTX(pool_slot,74);
 CTX(pool_slot,100);CTX(pool_slot,UINT_MAX);CTX(availability,1);CTX(availability,2);CTX(availability,UINT_MAX);
 CTX(size,0);CTX(size,2);CTX(score_item,true);CTX(damaged,true);CTX(static_animation,false);CTX(independent_motion,false);
 enemyAvail[75]=1;DECLINE;enemyAvail[75]=2;DECLINE;enemyAvail[75]=0;
 assert(!draw(source,NULL));
 for(unsigned slot=25;slot<=49;slot+=24) {
  actor(&source,slot,0);c=context(slot);DECLINE;
  enemy[slot].linknum=1;DECLINE;enemy[slot].enemydie=512;DECLINE;
 }
 actor(&source,75,1);c=context(75);
 assert(!capsule545_draw(&surface,100,80,source,76,0,0,&c));
 assert(!capsule545_draw(&surface,100,80,source,78,0,0,&c));
 const int badparts[]={INT_MIN,-1,2,18,21,INT_MAX};
 for(unsigned i=0;i<sizeof(badparts)/sizeof(*badparts);i++)assert(!capsule545_draw(&surface,100,80,source,77,badparts[i],0,&c));
 assert(!capsule545_draw(&surface,100,80,source,77,0,-1,&c));assert(!capsule545_draw(&surface,100,80,source,77,0,256,&c));
 const int badx[]={INT_MIN,-1,309,INT_MAX},bady[]={INT_MIN,-14,200,INT_MAX};
 for(unsigned i=0;i<4;i++){assert(!capsule545_draw(&surface,badx[i],80,source,77,0,0,&c));assert(!capsule545_draw(&surface,100,bady[i],source,77,0,0,&c));}
#undef CTX
#undef LIVE
#undef DECLINE
}
static void display_guards(Sprite2_array source)
{
 G101EnemyContext c=context(75);actor(&source,75,1);
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
 assert(!capsule545_draw(NULL,100,80,source,77,0,0,&c));assert(!capsule545_draw(&other,100,80,source,77,0,0,&c));
 /* Probe lease bypass is restricted to the same exact level scope. */
 game_probe_enabled=true;asteroid_hd_lease=false;assert(draw(source,&c));
 lvlFileNum=2;DECLINE;lvlFileNum=1;game_probe_enabled=false;asteroid_hd_lease=true;
 assert(draw(source,&c));
#undef DECLINE
}
static void resource_guards(void)
{
 const char *root=game_probe_assets;
 game_probe_assets=NULL;assert(!capsule545_family_ready());game_probe_assets="";assert(!capsule545_family_ready());
 char longroot[1025];memset(longroot,'x',sizeof(longroot)-1);longroot[sizeof(longroot)-1]=0;
 game_probe_assets=longroot;assert(!capsule545_family_ready());game_probe_assets="/foreign-capsule545-root";assert(!capsule545_family_ready());game_probe_assets=root;
 game_probe_density=4;assert(!capsule545_family_ready());game_probe_density=0;assert(!capsule545_family_ready());game_probe_density=8;
 game_probe_missing=true;assert(!capsule545_family_ready());game_probe_missing=false;
 game_probe_invalid=true;assert(!capsule545_family_ready());game_probe_invalid=false;
 game_probe_original_reference=true;assert(!capsule545_family_ready());game_probe_original_reference=false;
 assert(capsule545_family_ready());
#define BAD_ASSET(field,value) do{Asset old=capsule545_resources.member[0];mirror_logic_tick++;capsule545_resources.member[0].field=value;assert(!capsule545_family_ready());capsule545_resources.member[0]=old;assert(!capsule545_family_ready());capsule545_shutdown();assert(capsule545_family_ready());}while(0)
 BAD_ASSET(initialized,false);BAD_ASSET(valid,false);BAD_ASSET(bank,101);BAD_ASSET(index,123);BAD_ASSET(w,12);BAD_ASSET(h,14);
 BAD_ASSET(anchor_x,1);BAD_ASSET(anchor_y,1);BAD_ASSET(density,4);BAD_ASSET(rgba,NULL);
#undef BAD_ASSET
 mirror_logic_tick++;capsule545_resources.member[0].rgba[10]^=1;assert(!capsule545_family_ready());
 capsule545_resources.member[0].rgba[10]^=1;assert(!capsule545_family_ready());capsule545_shutdown();assert(capsule545_family_ready());
}
int main(int argc,char **argv)
{
 assert(argc==5);game_probe_assets=argv[3];records(argv[2]);
 FILE *f=fopen(argv[1],"rb");assert(f);Uint8 *raw=malloc(42012);
 assert(raw&&fread(raw,1,42012,f)==42012&&fgetc(f)==EOF);fclose(f);
 enemySpriteSheets[0]=(Sprite2_array){42012,raw};enemySpriteSheetIds[0]=8;Sprite2_array source=enemySpriteSheets[0];
 assert(capsule545_source(source)&&asteroid1_scope());actor(&source,75,1);G101EnemyContext c=context(75);
 if(!strcmp(argv[4],"reject")||!strcmp(argv[4],"peers-only")) {
  if(!strcmp(argv[4],"peers-only"))peer_state(true);
  assert(!capsule545_family_ready());assert(!draw(source,&c));assert(!accepted&&!rejected);
  capsule545_shutdown();for(unsigned i=0;i<14;i++)peer_shutdown[i]();
  free(raw);puts("capsule545 invalid resource remains classic; peer families independent");return 0;
 }
 assert(!strcmp(argv[4],"accept")||!strcmp(argv[4],"own-only"));assert(capsule545_family_ready());
 if(!strcmp(argv[4],"accept"))independent_fallback();else {peer_state(false);for(unsigned i=0;i<14;i++)peer_shutdown[i]();}
 exact_record_guards(source);source_guards(source);geometry_and_motion(source);partial_geometry(source);warm_frame_guard(source);actor_guards(source);display_guards(source);resource_guards();
 capsule545_shutdown();free(raw);
 puts("capsule545 all77 cold+warm bytes; exact loaded bank; pool75-99 four-part geometry; live/static/display/loader integrity passed");return 0;
}
'''


def source_support(bank):
    if len(bank) != 42012:
        raise RuntimeError('Unexpected original bank size')
    support = set()
    for tile, ox, oy in [(77, 0, 0), (78, 12, 0), (96, 0, 14), (97, 12, 14)]:
        cursor = struct.unpack_from('<H', bank, (tile - 1) * 2)[0]
        position = 0
        while True:
            control = bank[cursor]
            cursor += 1
            if control == 15:
                break
            position += control & 15
            count = control >> 4
            for _ in range(count):
                if not 0 <= position < 12 * 14:
                    raise RuntimeError('Original quadrant escaped its footprint')
                support.add((ox + position % 12, oy + position // 12))
                position += 1
                cursor += 1
    xs, ys = zip(*support)
    bbox = [min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1]
    if len(support) != 255 or bbox != [6, 3, 13, 25]:
        raise RuntimeError('Unexpected original record545 occupied support')
    return support


def check_payload_support(payload, support):
    visible = set()
    for y in range(28 * 8):
        for x in range(24 * 8):
            if payload[28 + (y * 24 * 8 + x) * 4 + 3]:
                cell = (x // 8, y // 8)
                if cell not in support:
                    raise RuntimeError('HD alpha escaped original occupied support')
                visible.add(cell)
    if not visible:
        raise RuntimeError('Empty capsule545 payload')
    return len(visible)


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
            raise RuntimeError('Generated output exceeds 8 MiB')
        return total

    helper = root / 'tests/test_asteroid1_ten_assets.py'
    source_path = root / 'src/render_mirror.c'
    family_path = root / 'src/asteroid1_capsule545_mirror.inc'
    shared_path = root / 'src/asteroid1_ten_mirror.inc'
    struct_path = root / 'src/varz.h'
    snapshot_path = root / 'src/asteroid1_source_snapshot.inc'
    pack = root / 'assets/hd/packs/asteroid1-ten-v1'
    art = pack / 'enemy-newshd-77-8.hda'
    peer_paths = [root / 'src' / f'asteroid1_{name}_mirror.inc' for name, _ in PEERS]
    allowlist = {helper, source_path, family_path, shared_path, struct_path, snapshot_path,
                 art, a.data / 'tyrian.hdt', a.data / 'newshd.shp', *peer_paths}

    def read(path, binary=False):
        if path not in allowlist:
            raise RuntimeError('Input outside explicit allowlist')
        return path.read_bytes() if binary else path.read_text()

    payload = read(art, True)
    if len(payload) != 172060 or struct.unpack_from('<4s6I', payload) != (b'HDR1',1080077,8,24,28,0,0):
        raise RuntimeError('Unexpected capsule545 asset header or size')
    support = source_support(read(a.data / 'newshd.shp', True))
    occupied_hd_cells = check_payload_support(payload, support)
    spec = importlib.util.spec_from_file_location('capsule545_named_ten_harness', helper)
    ten = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ten)
    source, family, shared, varz = read(source_path), read(family_path), read(shared_path), read(struct_path)
    start = varz.index('struct JE_SingleEnemyType\n{')
    end = varz.index('\n};', start) + 3
    structcode = varz[start:end] + '\nstatic struct JE_SingleEnemyType enemy[100];\nstatic unsigned char enemyAvail[100];\n'
    prefix = ten.HARNESS.split('int main(int argc', 1)[0].replace('t=444;t<=453', 't=545;t<=545')
    prefix = prefix.replace('static Uint8 last_filter;', 'static Uint8 last_filter;static Asset *last_asset;')
    prefix = prefix.replace('accepted++;last_x=x;', 'last_asset=a;accepted++;last_x=x;')
    prefix = prefix.replace('assert(a&&a->bank==108', 'assert(a&&a->index==77&&a->w==24&&a->h==28&&part&&part->w==12&&part->h==14&&a->bank==108')
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
    if len(peer_bases) != 34 or 77 in peer_bases:
        raise RuntimeError('Unexpected existing peer image closure')
    peer_code += 'static bool (*peer_ready[])(void)={' + ','.join(peer + '_family_ready' for _, peer in PEERS) + '};\n'
    peer_code += 'static void (*peer_shutdown[])(void)={' + ','.join(peer + '_shutdown' for _, peer in PEERS) + '};\n'
    peer_code += 'static Asset *peer_asset[]={' + ','.join('&' + peer + '_resources.member[0]' for _, peer in PEERS) + '};\n'
    code = prefix.replace('@SCOPE@', scopes).replace('@FAMILY@', structcode + common + family + peer_code) + MAIN
    harness = remember(a.out / 'harness.c')
    harness.write_text(code)
    raw = read(a.data / 'tyrian.hdt', True)
    off = struct.unpack_from('<i', raw)[0] + 14 + 1638*80 + 61*82 + 55*37 + 7*37 + 19*41 + 38*86 + 12*37
    record = remember(a.out / 'original545-record.bin')
    record.write_bytes(raw[off+545*77:off+546*77])
    if record.stat().st_size != 77:
        raise RuntimeError('Short original record545')
    fixtures = a.out / 'fixtures'
    fixtures.mkdir()
    variants = []
    kinds = ['missing','payload','magic','role','foreign-base','density','width','height',
             'anchor-x','anchor-y','header-short','short','extra','fifo','directory','broken-symlink']
    for n, kind in enumerate(kinds):
        d = fixtures / f'{n:02d}-{kind}'
        d.mkdir()
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
    result = dict(record=545,base=77,logical_size=[24,28],density=8,
                  cold_source_record_byte_mutations=77,warm_source_record_byte_mutations=77,
                  boundary_pool_slots=[75,99],ordered_quadrants=8,fixture_count=len(variants),
                  accepted_links={'75-99':list(range(1,10))},allowed_drop=0,
                  movement='Unrestricted; event19 zero/down/left/right, event20/27 and field-range extremes tested',
                  positive_armor_values=255,source_occupied_cells=255,source_occupied_bbox=[6,3,13,25],
                  hd_occupied_cells=occupied_hd_cells,clipping_origins=6,clipping_filters=[0,17,255],
                  independent_peer_families=14,sticky_whole_frame=True,
                  compiler_peak_rss_bytes=compiler_peak,runtime_peak_rss_bytes=runtime_peak,
                  compiler_address_space_limit_bytes=1024*MIB,runtime_rss_limit_bytes=512*MIB,
                  output_limit_bytes=OUTPUT_LIMIT,output_bytes=output_bound(),runs=runs,
                  source_sha256=hashlib.sha256(family.encode()).hexdigest(),leak_sanitizer=False,
                  scope='Extracted production functions and full live struct. Separate actual-engine pixel pairs required.')
    receipt = remember(a.out / 'receipt.json')
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    output_bound()
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
