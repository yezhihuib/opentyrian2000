#include "lamp272_bottom_clip_contract.h"
#include "lamp272_later16_scope.inc"
static void lamp272_top_clip_reset(void),lamp272_top_clip_tick(void);
static void lamp272_bottom_clip_reset(void),lamp272_bottom_clip_tick(void);
/* Private exact-origin lamp adapter. Default OFF. No HdRegion draw or restore.
 * Art is written only on actual native indexed writer callbacks. */
static const char *lamp272_root(void){const char *p=getenv("LAMP272_FAMILY_ASSET_DIR");return p?p:"";}
static uint64_t lamp272_blend_retirements;
static bool lamp272_native;
static unsigned char lamp272_owned[64000];
static bool lamp272_cell(unsigned off){return off<64000&&lamp272_owned[off];}
static void lamp272_clear(unsigned off){if(off<64000)lamp272_owned[off]=0;}
static unsigned lamp272_image,lamp272_part,lamp272_pixels;
static int lamp272_x,lamp272_y;
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private E1 physical2 first-pair plus three later and two middle origins. Never an
 * asteroid/manual-campaign lease.
 * LAMP272_LATER_SIXTEEN_ENABLE=1 independently admits the appended 16 origins.
 * All hooks below write sidecar state only, never actor, event, palette or RNG.
 * LAMP272_FAMILY_CANVAS_ENABLE=1 enables only the ordered canvas adapter.
 * LAMP272_LATER_THREE_ENABLE=1 additionally admits only the three listed later
 * origins. LAMP272_MIDDLE_PAIR_ENABLE=1 independently admits only origins 50/51
 * (one-based). Both are pinned at level/frame begin; changes cannot enlarge a lease.
 * No environment flag means no new draws and no trace. Assets remain immutable
 * for a selected-root lifetime: disk hot reload is deliberately not supported.
 */
static const struct {unsigned base;uint64_t rgba;} private_lamp272_images[4]={
 {229,UINT64_C(0x380d60ca088b66cb)},{231,UINT64_C(0xa93168621d007ae5)},
 {233,UINT64_C(0xfd9c43c2ba04eef7)},{235,UINT64_C(0x9301528dceb12189)}
};
/* Compact ordinals, not event indexes, own the bounded23 consumed-once bits.
 * Preserve the original five bits; append middle origins and independently gated later16 origins. */
static const struct {unsigned event,time;int x;} private_lamp272_origins[23]={
 {22,356,66},{23,356,138},{137,1168,138},{146,1196,138},{147,1196,114},
 {49,440,138},{50,440,66},
 {267,2176,114},
 {268,2176,138},
 {481,4668,114},
 {482,4668,138},
 {483,4668,162},
 {484,4668,186},
 {486,4696,114},
 {487,4696,138},
 {488,4696,162},
 {489,4696,186},
 {572,6124,162},
 {573,6124,138},
 {586,6152,162},
 {587,6152,138},
 {604,6208,186},
 {605,6208,114}
};
static int private_lamp272_origin(unsigned event)
{
 for(unsigned i=0;i<COUNTOF(private_lamp272_origins);i++)
  if(private_lamp272_origins[i].event==event)return (int)i;
 return -1;
}
static bool private_lamp272_later_requested(void)
{
 const char *v=getenv("LAMP272_LATER_THREE_ENABLE");
 return v&&!strcmp(v,"1");
}
static bool private_lamp272_middle_requested(void)
{
 const char *v=getenv("LAMP272_MIDDLE_PAIR_ENABLE");
 return v&&!strcmp(v,"1");
}
static const struct {unsigned index,rgb;} private_lamp272_palette[]={
 {1,0x0c0c0c},{2,0x181818},{3,0x282828},{4,0x343434},{5,0x454545},
 {6,0x515151},{7,0x5d5d5d},{8,0x696d69},{9,0x797979},{10,0x8e8e8e},{11,0xa2a6a2},
 {112,0x200000},{113,0x380000},{114,0x510000},{115,0x6d0400},{116,0x860400},
 {117,0x9e0800},{118,0xba0c00},{119,0xd31400},{120,0xdf3c00},{121,0xe7610c},
 {122,0xeb8a18},{123,0xf3ae24},{124,0xfbcb30},{125,0xffe73c},{126,0xfffb96},{127,0xfffff3}
};
static struct {
 uint64_t generation,witness,epoch;bool exhausted,pending,initialized,live;
 unsigned event;Sprite2_array *bank;const Uint8 *data;size_t bytes;
} private_lamp272_slots[100];
static struct {
 uint64_t epoch,serial;bool exhausted,loaded,later_three,middle_pair;unsigned consumed,mode;char root[1024];
 const struct JE_EventRecType *events; /* Read-only actual table supplied at load. */
 struct {bool live;uint64_t token,epoch,generation;unsigned event;int slot;} call;
} private_lamp272_life;
static struct {bool checked,valid;char root[1024];Asset member[4];} private_lamp272_resources;
static struct {
 bool contributed,fault,quartet,accepted,later_three,middle_pair;unsigned slot,base,next,used;int x,y;
 uint64_t generation,epoch;unsigned mask[100];int completed_bottom_tail_y[100];uint64_t generations[100];
} private_lamp272_frame;
static unsigned private_lamp272_mode(void)
{
 const char *v=getenv("LAMP272_FAMILY_CANVAS_ENABLE");
 const char *f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&f&&!strcmp(f,"1")?
  ((v&&!strcmp(v,"1")?2u:0u)|(lamp272_later16_requested()?4u:0u)):0;
}
static bool private_lamp272_level_scope(void)
{
 return private_lamp272_mode()&&episodeNum==1&&lvlFileNum==2&&
  ((!play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&mainLevel==6&&!strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' '))||
   (game_probe_enabled&&asset_debug_enabled&&play_demo&&!demo_file&&!strcmp(levelName,"ASSET DBG ")))&&
  !manual_hd_enabled&&!asteroid_hd_enabled&&!xmas&&!isNetworkGame&&!twoPlayerMode&&
  !twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&!constantPlay&&!constantDie&&!richMode&&
  !onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&!timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}

static bool private_lamp272_scope(void)
{
 return private_lamp272_life.loaded&&!private_lamp272_life.exhausted&&private_lamp272_level_scope()&&
  terrain_file=='z'&&private_lamp272_mode()==private_lamp272_life.mode&&
  private_lamp272_later_requested()==private_lamp272_life.later_three&&
  private_lamp272_middle_requested()==private_lamp272_life.middle_pair&&
  lamp272_root()&&
  !strcmp(private_lamp272_life.root,lamp272_root());
}
static bool private_lamp272_frame_scope(void)
{
 return private_lamp272_scope()&&
  private_lamp272_frame.later_three==private_lamp272_life.later_three&&
  private_lamp272_frame.middle_pair==private_lamp272_life.middle_pair;
}
static bool private_lamp272_origin_enabled(int origin)
{
 return origin>=0&&origin<(int)COUNTOF(private_lamp272_origins)&&
  (origin>=7?(private_lamp272_life.mode&4u):
   ((private_lamp272_life.mode&2u)&&(origin<2||(origin<5?private_lamp272_life.later_three:private_lamp272_life.middle_pair))));
}
static int private_lamp272_slot(const void *ptr)
{
 uintptr_t p=(uintptr_t)ptr,b=(uintptr_t)enemy;
 if(p<b||p-b>=sizeof(enemy)||(p-b)%sizeof(enemy[0]))return -1;
 return (int)((p-b)/sizeof(enemy[0]));
}
/* Complete deterministic live-field witness; pointers are diagnostic only.
 * Acceptance compares exact objects and generation, never these textual values. */
static void private_lamp272_log(const char *phase,int slot,unsigned event,unsigned base,int part,int ok)
{
 if(!private_lamp272_mode())return;
 fprintf(stderr,"LAMP272\ttick=%u\tlogic=%llu\tepoch=%llu\tphase=%s\tevent=%u\tslot=%d\tbase=%u\tpart=%d\tok=%d",
  game_probe_tick,(unsigned long long)mirror_logic_tick,(unsigned long long)private_lamp272_life.epoch,phase,event,slot,base,part,ok);
 fprintf(stderr,"\tepisode=%u\tphysical=%u\tprobe=%d\tasset_debug=%d\tplay_demo=%d\tdemo_file=%p\tstopped=%d\tconstant=%d,%d,%d\teventLoc=%u\tcurLoc=%u",
  episodeNum,lvlFileNum,game_probe_enabled,asset_debug_enabled,play_demo,(void *)demo_file,stopped_demo,constantPlay,constantDie,richMode,eventLoc,curLoc);
 fprintf(stderr,"\tlater_level=%d\tlater_frame=%d\tconsumed=%u\torigin_ordinal=%d",
  private_lamp272_life.later_three,private_lamp272_frame.later_three,private_lamp272_life.consumed,private_lamp272_origin(event));
 if(private_lamp272_life.events&&maxEvent==731&&private_lamp272_origin(event)>=0){const struct JE_EventRecType *r=private_lamp272_life.events+event;
  fprintf(stderr,"\torigin=%u,%u,%d,%d,%d,%u,%d,%d",r->eventtime,r->eventtype,r->eventdat,r->eventdat2,r->eventdat3,r->eventdat4,r->eventdat5,r->eventdat6);}
 if(slot>=0&&slot<100){const struct JE_SingleEnemyType *e=enemy+slot;
  fprintf(stderr,"\tgen=%llu\twitness=%llu\tlive=%d\tavail=%u\ttype=%u\trecord272=%d\tbank_object=%p\tbank_data=%p\tbank_bytes=%lu\tsize=%u\tani=%u,%u,%u,%u,%u,%u\tarmor=%u\tfilter=%u\tflags=%d,%d,%d,%d\tlink_death=%u,%u\tpos=%d,%d,%u\tmotion=%d,%d,%d,%d,%d,%u,%u\taccel_aux=%d,%d,%d,%d,%d,%d,%u,%u\trev=%d,%d\tground_explode=%d,%u\ttur=%u,%u,%u\tfreq=%u,%u,%u\tlaunch=%u,%u,%u,%u\tdamage=%u,%d,%d\ticed=%u\tegr=",
   (unsigned long long)private_lamp272_slots[slot].generation,(unsigned long long)private_lamp272_slots[slot].witness,
   private_lamp272_slots[slot].live,enemyAvail[slot],e->enemytype,e->enemydatofs==&enemyDat[272],(void *)e->sprite2s,
   e->sprite2s?(void *)e->sprite2s->data:NULL,e->sprite2s?(unsigned long)e->sprite2s->size:0,e->size,
   e->ani,e->animin,e->animax,e->aniwhenfire,e->aniactive,e->enemycycle,e->armorleft,e->filter,
   e->scoreitem,e->special,e->edamaged,e->evalue,e->linknum,e->enemydie,e->ex,e->ey,e->mapoffset,
   e->exc,e->eyc,e->fixedmovey,e->excc,e->eycc,e->xaccel,e->yaccel,
   e->exca,e->eyca,e->exccw,e->eyccw,e->exccadd,e->eyccadd,e->exccwmax,e->eyccwmax,e->exrev,e->eyrev,
   e->enemyground,e->explonum,e->tur[0],e->tur[1],e->tur[2],e->freq[0],e->freq[1],e->freq[2],
   e->launchfreq,e->launchtype,e->launchspecial,e->launchwait,e->edgr,e->edlevel,e->edani,e->iced);
  for(unsigned i=0;i<20;i++)fprintf(stderr,"%s%u",i?",":"",e->egr[i]);
 }
 fputc('\n',stderr);
}
static void private_lamp272_fail(void)
{
 private_lamp272_frame.accepted=false;private_lamp272_frame.fault=true;private_lamp272_frame.quartet=false;
 if(private_lamp272_frame.contributed){
  ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;
  family_fault(FC_SOURCE);
 }
}
void render_mirror_lamp272_retired(unsigned slot)
{
 if(slot>=100)return;
 if(private_lamp272_slots[slot].live||private_lamp272_slots[slot].pending){
  private_lamp272_log("retired",(int)slot,private_lamp272_slots[slot].event,0,-1,0);
  if(private_lamp272_frame.mask[slot])private_lamp272_fail();
 }
 private_lamp272_slots[slot].live=private_lamp272_slots[slot].pending=private_lamp272_slots[slot].initialized=false;
}
static void private_lamp272_reset(void)
{
 lamp272_top_clip_reset();
 lamp272_bottom_clip_reset();
 private_lamp272_frame.accepted=false;
 if(private_lamp272_frame.contributed||private_lamp272_frame.quartet)private_lamp272_fail();
 for(unsigned i=0;i<100;i++)render_mirror_lamp272_retired(i);
 private_lamp272_life.call.live=false;
 if(private_lamp272_life.epoch==UINT64_MAX)private_lamp272_life.exhausted=true;
 else ++private_lamp272_life.epoch;
 /* Consumed event bits survive renderer/bank changes. Only a real level load
  * may authorize fresh listed origins; returning to an event never rearms it. */
}
static bool private_lamp272_event_matches(unsigned index)
{
 int origin=private_lamp272_origin(index);
 if(!private_lamp272_life.events||maxEvent!=731||origin<0)return false;
 const struct JE_EventRecType *r=private_lamp272_life.events+index;
 return r->eventtime==private_lamp272_origins[origin].time&&r->eventtype==6&&r->eventdat==272&&
  r->eventdat2==private_lamp272_origins[origin].x&&!r->eventdat3&&!r->eventdat4&&!r->eventdat5&&!r->eventdat6;
}
static bool private_lamp272_origins_match(void)
{
 for(unsigned i=0;i<COUNTOF(private_lamp272_origins);i++)
  if(private_lamp272_origin_enabled((int)i)&&
   !private_lamp272_event_matches(private_lamp272_origins[i].event))return false;
 return true;
}
void render_mirror_lamp272_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 private_lamp272_reset();private_lamp272_life.loaded=false;private_lamp272_life.consumed=0;
 private_lamp272_life.mode=private_lamp272_mode();private_lamp272_life.events=events;
 private_lamp272_life.later_three=private_lamp272_later_requested();
 private_lamp272_life.middle_pair=private_lamp272_middle_requested();
 if(!private_lamp272_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||
  !private_lamp272_origins_match()||
  ((private_lamp272_life.mode&4u)&&!lamp272_later16_stream_matches(events))||
  !lamp272_root()||!lamp272_root()[0]||strlen(lamp272_root())>=sizeof(private_lamp272_life.root)){private_lamp272_life.events=NULL;return;}
 strcpy(private_lamp272_life.root,lamp272_root());private_lamp272_life.loaded=true;
 private_lamp272_log("level-load",-1,0,0,-1,1);
}
static bool private_lamp272_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=46566)return false;
 bool found=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==23&&bank.data==enemySpriteSheets[i].data&&bank.size==enemySpriteSheets[i].size)found=true;
 return found&&asteroid1_stamp(bank.data,bank.size)==UINT64_C(0xf22ec1295ced5d11)&&
  asteroid1_record_stamp(272)==UINT64_C(0x2f2c9491d2030153);
}
static bool private_lamp272_colors(void)
{
 for(unsigned i=0;i<COUNTOF(private_lamp272_palette);i++)
  if((rgb_palette[private_lamp272_palette[i].index]&0xffffffu)!=private_lamp272_palette[i].rgb)return false;
 return true;
}
static bool private_lamp272_shape(unsigned slot,bool birth)
{
 if(slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 if(e->enemytype!=272||e->enemydatofs!=&enemyDat[272]||!e->sprite2s)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==23&&e->sprite2s==enemySpriteSheets+i)bound=true;
 if(!bound||!private_lamp272_source(*e->sprite2s)||e->size!=1||e->scoreitem||e->special||e->edamaged||
  !e->armorleft||e->evalue||e->linknum||e->enemydie||e->filter||e->ani!=18||e->animin!=1||e->animax||
  e->aniwhenfire||e->aniactive!=1||(birth?e->enemycycle!=0:(e->enemycycle<1||e->enemycycle>18))||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=2||
  e->tur[0]||e->tur[1]||e->tur[2]||e->freq[0]||e->freq[1]||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 static const unsigned sequence[20]={229,229,229,233,233,233,235,235,235,233,233,233,231,231,231,229,229,229,0,0};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 return true;
}
uint64_t render_mirror_lamp272_event_begin(unsigned eventloc,unsigned typeofs,unsigned pool,int unique)
{
 /* Called only at the actual case6 direct call site, not inferred in make. */
 if(private_lamp272_life.call.live){private_lamp272_life.call.live=false;private_lamp272_fail();return 0;}
 if(!private_lamp272_scope()||eventloc!=eventLoc||eventloc<1||typeofs||pool!=25||unique)return 0;
 unsigned index=eventloc-1;int origin=private_lamp272_origin(index);
 if(!private_lamp272_origin_enabled(origin)||!private_lamp272_event_matches(index)||
  curLoc!=private_lamp272_origins[origin].time)return 0;
 unsigned bit=1u<<(unsigned)origin; /* bounded compact ordinal0..22, never raw event index. */
 if(private_lamp272_life.consumed&bit)return 0;
 private_lamp272_life.consumed|=bit; /* Allocation failure also consumes origin. */
 if(private_lamp272_life.serial==UINT64_MAX){private_lamp272_life.exhausted=true;return 0;}
 private_lamp272_life.call.live=true;private_lamp272_life.call.token=++private_lamp272_life.serial;
 private_lamp272_life.call.epoch=private_lamp272_life.epoch;private_lamp272_life.call.event=index;
 private_lamp272_life.call.slot=-1;private_lamp272_life.call.generation=0;
 private_lamp272_log("event-begin",-1,index,0,-1,1);
 return private_lamp272_life.call.token;
}
void render_mirror_lamp272_enemy_allocated(void *ptr,unsigned record,int unique)
{
 int slot=private_lamp272_slot(ptr);if(slot<0)return;
 render_mirror_lamp272_retired((unsigned)slot);
 if(private_lamp272_slots[slot].generation==UINT64_MAX){private_lamp272_slots[slot].exhausted=true;return;}
 if(private_lamp272_slots[slot].exhausted)return;
 ++private_lamp272_slots[slot].generation;
 if(private_lamp272_life.call.live&&private_lamp272_scope()&&record==272&&!unique&&slot>=25&&slot<50&&
  enemyAvail[slot]==1&&private_lamp272_life.call.slot==-1){
  private_lamp272_slots[slot].pending=true;private_lamp272_slots[slot].event=private_lamp272_life.call.event;
  private_lamp272_life.call.slot=slot;private_lamp272_life.call.generation=private_lamp272_slots[slot].generation;
 }
 /* No preconstruction pointer dereference: a reused object may hold freed data. */
 if(private_lamp272_mode()&&(record==272||record==274))
  fprintf(stderr,"LAMP272\ttick=%u\tphase=allocated\tslot=%d\trecord=%u\tgen=%llu\tpending=%d\n",game_probe_tick,slot,record,(unsigned long long)private_lamp272_slots[slot].generation,private_lamp272_slots[slot].pending);
}
void render_mirror_lamp272_enemy_initialized(void *ptr,unsigned record,unsigned avail)
{
 int slot=private_lamp272_slot(ptr);if(slot<0)return;
 private_lamp272_slots[slot].initialized=private_lamp272_slots[slot].pending&&private_lamp272_life.call.live&&
  private_lamp272_life.call.slot==slot&&private_lamp272_life.call.generation==private_lamp272_slots[slot].generation&&
  record==272&&avail==0&&enemyAvail[slot]==1&&private_lamp272_shape((unsigned)slot,true);
 if(private_lamp272_scope()&&(record==272||record==274))private_lamp272_log("initialized",slot,
  private_lamp272_slots[slot].pending?private_lamp272_slots[slot].event:UINT_MAX,0,-1,private_lamp272_slots[slot].initialized);
}
void render_mirror_lamp272_event_commit(uint64_t token,unsigned allocated_one_based)
{
 if(!token)return;
 int slot=private_lamp272_life.call.slot;
 int origin=private_lamp272_origin(private_lamp272_life.call.event);
 bool ok=private_lamp272_life.call.live&&token==private_lamp272_life.call.token&&
  private_lamp272_life.call.epoch==private_lamp272_life.epoch&&private_lamp272_scope()&&
  slot>=25&&slot<50&&allocated_one_based==(unsigned)slot+1&&eventLoc==private_lamp272_life.call.event+1&&
  private_lamp272_origin_enabled(origin)&&private_lamp272_event_matches(private_lamp272_life.call.event)&&
  curLoc==private_lamp272_origins[origin].time;
 if(ok)ok=private_lamp272_slots[slot].pending&&private_lamp272_slots[slot].initialized&&
  private_lamp272_life.call.generation==private_lamp272_slots[slot].generation&&enemyAvail[slot]==0&&
  private_lamp272_shape((unsigned)slot,true)&&enemy[slot].ey==-28&&
  enemy[slot].ex==private_lamp272_life.events[eventLoc-1].eventdat2-(mapX-1)*24-12;
 if(slot>=0&&slot<100){
  private_lamp272_slots[slot].live=ok;private_lamp272_slots[slot].pending=false;private_lamp272_slots[slot].initialized=false;
  if(ok){private_lamp272_slots[slot].witness=private_lamp272_slots[slot].generation;private_lamp272_slots[slot].epoch=private_lamp272_life.epoch;
   private_lamp272_slots[slot].bank=enemy[slot].sprite2s;private_lamp272_slots[slot].data=enemy[slot].sprite2s->data;private_lamp272_slots[slot].bytes=enemy[slot].sprite2s->size;}
 }
 private_lamp272_log(ok?"event-commit":"event-abort",slot,private_lamp272_life.call.event,0,-1,ok);
 private_lamp272_life.call.live=false;
}
void render_mirror_lamp272_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(private_lamp272_slots[i].live&&private_lamp272_slots[i].bank==bank)
  render_mirror_lamp272_retired(i);
 if(private_lamp272_life.call.live){private_lamp272_life.call.live=false;private_lamp272_fail();}
}
static bool private_lamp272_witness(unsigned slot)
{
 if(slot>=100)return false;
 int origin=private_lamp272_origin(private_lamp272_slots[slot].event);
 return slot>=25&&slot<50&&private_lamp272_slots[slot].live&&!private_lamp272_slots[slot].exhausted&&
  private_lamp272_slots[slot].epoch==private_lamp272_life.epoch&&
  private_lamp272_slots[slot].generation==private_lamp272_slots[slot].witness&&
  private_lamp272_origin_enabled(origin)&&private_lamp272_event_matches(private_lamp272_slots[slot].event)&&
  (private_lamp272_life.consumed&(1u<<(unsigned)origin))&&enemyAvail[slot]==0&&
  private_lamp272_slots[slot].bank==enemy[slot].sprite2s&&enemy[slot].sprite2s&&
  private_lamp272_slots[slot].data==enemy[slot].sprite2s->data&&private_lamp272_slots[slot].bytes==enemy[slot].sprite2s->size;
}
static void private_lamp272_lifecycle(void)
{
 if(private_lamp272_life.loaded&&!private_lamp272_scope()){
  private_lamp272_reset();private_lamp272_life.loaded=false;private_lamp272_life.events=NULL;return;
 }
 for(unsigned i=0;i<100;i++)if(private_lamp272_slots[i].live&&
  (!private_lamp272_witness(i)||!enemy[i].armorleft||enemy[i].enemytype!=272||enemy[i].enemydatofs!=&enemyDat[272]))render_mirror_lamp272_retired(i);
}
static void private_lamp272_tick(void)
{
 lamp272_top_clip_tick();
 lamp272_bottom_clip_tick();
 lamp272_native=false;memset(lamp272_owned,0,sizeof lamp272_owned);
 /* A new tick cannot inherit cached lamp pixels across an early-return path. */
 if(private_lamp272_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 /* Discard previous frame contribution before observing new-tick retirement. */
 memset(&private_lamp272_frame,0,sizeof(private_lamp272_frame));
 private_lamp272_frame.later_three=private_lamp272_later_requested();
 private_lamp272_frame.middle_pair=private_lamp272_middle_requested();
 private_lamp272_lifecycle();
}
static bool private_lamp272_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;Uint8 *rgba=NULL;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshs-%u-8.hda",private_lamp272_resources.root,private_lamp272_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==1360000+private_lamp272_images[k].base&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==private_lamp272_images[k].rgba;
 if(ok)for(size_t i=3;i<bytes;i+=4)if(rgba[i]!=255){ok=false;break;}
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 private_lamp272_resources.member[k]=(Asset){true,true,ASSET_ASTEROID1_NEWSHS,(int)private_lamp272_images[k].base,24,28,0,0,8,rgba};
 return true;
}
static bool private_lamp272_ready(void)
{
 if(!private_lamp272_scope()||!private_lamp272_mode()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!private_lamp272_resources.checked){private_lamp272_resources.checked=true;private_lamp272_resources.valid=true;
  strcpy(private_lamp272_resources.root,private_lamp272_life.root);
  for(unsigned i=0;i<4;i++)if(!private_lamp272_load(i))private_lamp272_resources.valid=false;}
 if(!private_lamp272_resources.valid||strcmp(private_lamp272_resources.root,lamp272_root()))return false;
 /* All four cached resources are checked at every accepted quadrant/output,
  * never only the chosen phase. Cold failures leave terrain and other actors. */
 for(unsigned i=0;i<4;i++){const Asset *a=private_lamp272_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_NEWSHS||a->index!=(int)private_lamp272_images[i].base||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,172032)!=private_lamp272_images[i].rgba){private_lamp272_resources.valid=false;return false;}}
 return true;
}
static void private_lamp272_shutdown(void)
{
 private_lamp272_reset();private_lamp272_life.loaded=false;private_lamp272_life.events=NULL;
 for(unsigned i=0;i<4;i++)free(private_lamp272_resources.member[i].rgba);
 memset(&private_lamp272_resources,0,sizeof(private_lamp272_resources));
}
static bool private_lamp272_dependencies(void)
{
 if(!private_lamp272_frame_scope()||!private_lamp272_colors()||!private_lamp272_ready())return false;
 for(unsigned i=0;i<100;i++)if(private_lamp272_frame.mask[i]&&
  (!private_lamp272_witness(i)||private_lamp272_frame.generations[i]!=private_lamp272_slots[i].generation||
   !private_lamp272_source(*enemy[i].sprite2s)))return false;
 return true;
}
/* Pure accepted-frame guard: never loads assets, retires actors or faults. */
static bool lamp272_resources_current(void)
{
 if(!private_lamp272_resources.checked||!private_lamp272_resources.valid||
    strcmp(private_lamp272_resources.root,lamp272_root()))return false;
 for(unsigned i=0;i<4;i++){
  const Asset *a=private_lamp272_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_NEWSHS||
     a->index!=(int)private_lamp272_images[i].base||a->w!=24||a->h!=28||
     a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
     asteroid1_stamp(a->rgba,172032)!=private_lamp272_images[i].rgba)return false;
 }
 return true;
}
static bool private_lamp272_full_finish(void)
{
 if(!private_lamp272_frame.contributed)return true;
 if(private_lamp272_frame.fault||private_lamp272_frame.quartet||!private_lamp272_frame_scope()||
  !private_lamp272_colors()||!lamp272_resources_current())return false;
 for(unsigned i=0;i<100;i++)if(private_lamp272_frame.mask[i]&&
  (!lamp272_bottom_clip_complete(private_lamp272_frame.mask[i],private_lamp272_frame.completed_bottom_tail_y[i])||!private_lamp272_witness(i)||!private_lamp272_shape(i,false)||
   private_lamp272_frame.generations[i]!=private_lamp272_slots[i].generation||
   !private_lamp272_source(*enemy[i].sprite2s)))return false;
 return true;
}

static bool lamp272_full_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!private_lamp272_mode()||slot>=100||enemy[slot].enemytype!=272)return false;
 if(!fc.frame_active||fc.frame_failed||!private_lamp272_witness(slot))return false;
 if(private_lamp272_frame.contributed&&!private_lamp272_dependencies()){private_lamp272_fail();return false;}
 if(x<0||x>308||y<0||y>186||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=(part==1||part==20)?12:0,py=part>=19?14:0;
 /* Entire body must be visible; native clipping remains classic. */
 if(x-px<24||x-px>264||y-py<0||y-py>156)return false;
 if((int64_t)x-px!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||
    (int64_t)y-py!=(int64_t)enemy[slot].ey-7)return false;
 if(!private_lamp272_frame_scope()||sheet!=enemy[slot].sprite2s||!sheet||filter||
    !private_lamp272_shape(slot,false)||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||
    !private_lamp272_source(*sheet)||!private_lamp272_colors()||!private_lamp272_ready())return false;
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||lamp272_native||suppress||surface!=game_screen||surface!=VGAScreen||
    !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
    !b313_family_writer_draw_ready(fc_frame)||!family_prepare_canvas()){family_fault(FC_SOURCE);return false;}
 static const int parts[4]={0,1,19,20};
 if(!private_lamp272_frame.quartet){
  if(part||private_lamp272_frame.mask[slot]){family_fault(FC_ORDER);return false;}
  private_lamp272_frame.quartet=true;private_lamp272_frame.slot=slot;private_lamp272_frame.base=base;
  private_lamp272_frame.x=x;private_lamp272_frame.y=y;private_lamp272_frame.next=0;
 }
 if(private_lamp272_frame.slot!=slot||private_lamp272_frame.base!=base||
    private_lamp272_frame.next>=4||part!=parts[private_lamp272_frame.next]||
    x-px!=private_lamp272_frame.x||y-py!=private_lamp272_frame.y){family_fault(FC_ORDER);return false;}
 unsigned k=0;while(k<4&&private_lamp272_images[k].base!=base)++k;
 if(k==4){family_fault(FC_SOURCE);return false;}
 lamp272_native=true;lamp272_image=k;lamp272_part=part;lamp272_x=x;lamp272_y=y;lamp272_pixels=0;
 private_lamp272_frame.contributed=true;
 private_lamp272_frame.generations[slot]=private_lamp272_slots[slot].generation;
 private_lamp272_frame.used|=1u<<k;
 return true;
}
static bool lamp272_full_pixel(unsigned x,unsigned y,int style)
{
 if(!lamp272_native)return false;
 if(style!=MIRROR_NORMAL||x!=(unsigned)lamp272_x+lamp272_pixels%12||
    y!=(unsigned)lamp272_y+lamp272_pixels/12||lamp272_pixels>=168){family_fault(FC_ORDER);return true;}
 const Asset *a=private_lamp272_resources.member+lamp272_image;
 unsigned px=(lamp272_part==1||lamp272_part==20)?12:0,py=lamp272_part>=19?14:0;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;
  const Uint8 *p=a->rgba+(((py+y-lamp272_y)*8+sy)*192+(px+x-lamp272_x)*8+sx)*4;
  ((Uint32 *)canvas->pixels)[n]=0xff000000u|((Uint32)p[0]<<16)|((Uint32)p[1]<<8)|p[2];
  hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 longface573_clear(y*320+x);gray325_clear(y*320+x);lamp272_owned[y*320+x]=1;triple275_clear(y*320+x);private_ember269_clear(y*320+x);selected[y*320+x]=1;++lamp272_pixels;return true;
}
static void lamp272_full_end(void)
{
 if(!lamp272_native)return;
 if(lamp272_pixels!=168||!b313_family_writer_draw_ready(fc_frame)){family_fault(FC_ORDER);lamp272_native=false;return;}
 unsigned slot=private_lamp272_frame.slot;
 private_lamp272_frame.mask[slot]|=1u<<private_lamp272_frame.next;
 if(++private_lamp272_frame.next==4)private_lamp272_frame.quartet=false;
 lamp272_native=false;
}

#include "lamp272_top_clip_mirror.inc"

Lamp272FamilyStatus render_mirror_lamp272_family_status(void)
{
 Lamp272FamilyStatus out={0};out.requested=private_lamp272_mode()!=0;out.frame=fc_frame;
 out.loaded=private_lamp272_life.loaded;out.contributed=private_lamp272_frame.contributed;
 out.failed=fc.frame_failed||private_lamp272_frame.fault;out.state_mask=private_lamp272_frame.used;
 out.blend_retirements=lamp272_blend_retirements;
 out.later_requested=private_lamp272_later_requested();out.later_level_enabled=private_lamp272_life.later_three;
 out.later_frame_enabled=private_lamp272_frame.later_three;out.consumed_origins=private_lamp272_life.consumed;
 out.middle_requested=private_lamp272_middle_requested();out.middle_level_enabled=private_lamp272_life.middle_pair;
 out.middle_frame_enabled=private_lamp272_frame.middle_pair;
 for(unsigned i=0;i<100;i++)if(private_lamp272_slots[i].live||private_lamp272_frame.mask[i])
  out.origin_event[i]=private_lamp272_slots[i].event+1;
 for(unsigned i=0;i<100;i++)if(private_lamp272_frame.mask[i]){
  out.slot_mask[i]=private_lamp272_frame.mask[i];out.base[i]=(enemy[i].enemycycle>=1&&enemy[i].enemycycle<=18)?enemy[i].egr[enemy[i].enemycycle-1]:0;
  out.cycle[i]=enemy[i].enemycycle;out.x[i]=enemy[i].ex+enemy[i].mapoffset-6;out.y[i]=enemy[i].ey-7;
 }
 for(unsigned i=0;i<64000;i++)out.surviving_cells+=lamp272_owned[i]!=0;
 return out;
}
bool render_mirror_lamp272_family_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=64000||!private_lamp272_frame.accepted||fc.frame_active||fc.frame_failed||!private_lamp272_frame.contributed||!private_lamp272_finish())return false;
 memcpy(out,lamp272_owned,64000);return true;
}
static void lamp272_blend_retired(void){++lamp272_blend_retirements;}

static void lamp272_accept(void){private_lamp272_frame.accepted=fc.ready&&!fc.frame_failed;}
