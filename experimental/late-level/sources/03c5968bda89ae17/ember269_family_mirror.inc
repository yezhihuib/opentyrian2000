/* Private exact-origin ember adapter. Default OFF. No HdRegion draw or restore.
 * Art is written only on actual native indexed writer callbacks. */
static const char *private_ember269_root(void){const char *p=getenv("EMBER269_FAMILY_ASSET_DIR");return p?p:"";}
static uint64_t private_ember269_blend_retirements;
static bool private_ember269_native;
static unsigned char private_ember269_owned[64000];
static bool private_ember269_cell(unsigned off){return off<64000&&private_ember269_owned[off];}
static void private_ember269_clear(unsigned off){if(off<64000)private_ember269_owned[off]=0;}
static unsigned private_ember269_image,private_ember269_part,private_ember269_pixels;
static int private_ember269_x,private_ember269_y;
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private E1 physical2 original plus independently gated later reuse. Never an asteroid/manual-campaign lease.
 * All hooks below write sidecar state only, never actor, event, palette or RNG.
 * EMBER269_FAMILY_CANVAS_ENABLE=1 enables only the ordered canvas adapter.
 * No environment flag means no new draws and no trace. Assets remain immutable
 * for a selected-root lifetime: disk hot reload is deliberately not supported.
 */
#include "ember269_native.inc"
static const struct {unsigned base;uint64_t rgba;} private_ember269_images[4]={
 {267,UINT64_C(0xd0e4ab5ba04e3363)},{269,UINT64_C(0xb685e8af26bab976)},
 {271,UINT64_C(0x54d5868a234306d5)},{273,UINT64_C(0xd45268a1da451f08)}
};
/* Ordinals, never raw event shifts: one consumed byte per finite origin. */
static const struct {unsigned event,time;int x;} private_ember269_origins[6]={
 {157,1252,114},
 {349,3128,114},
 {351,3128,186},
 {479,4668,42},
 {480,4668,66},
 {485,4668,258}
};
static int private_ember269_origin(unsigned event)
{
 unsigned lo=0,hi=COUNTOF(private_ember269_origins);
 while(lo<hi){unsigned mid=lo+(hi-lo)/2;
  if(private_ember269_origins[mid].event<event)lo=mid+1;else hi=mid;
 }
 return lo<COUNTOF(private_ember269_origins)&&private_ember269_origins[lo].event==event?(int)lo:-1;
}
static struct {
 uint64_t generation,witness,epoch;bool exhausted,pending,initialized,live;
 unsigned event;Sprite2_array *bank;const Uint8 *data;size_t bytes;
} private_ember269_slots[100];
static struct {
 uint64_t epoch,serial;bool exhausted,loaded;unsigned char consumed[6];unsigned mode;char root[1024];
 const struct JE_EventRecType *events; /* Read-only actual table supplied at load. */
 struct {bool live;uint64_t token,epoch,generation;unsigned event;int slot;} call;
} private_ember269_life;
static struct {bool checked,valid;char root[1024];Asset member[4];} private_ember269_resources;
static struct {
 bool contributed,fault,quartet,accepted;unsigned slot,base,next,used;int x,y;
 uint64_t generation,epoch;unsigned mask[100];uint64_t generations[100];
} private_ember269_frame;
static unsigned private_ember269_mode(void)
{
 const char *v=getenv("EMBER269_FAMILY_CANVAS_ENABLE");
 const char *f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&f&&!strcmp(f,"1")?
  ((v&&!strcmp(v,"1")?2u:0u)|(late_reuse_requested()?4u:0u)):0;
}
static bool private_ember269_level_scope(void)
{
 return private_ember269_mode()&&episodeNum==1&&lvlFileNum==2&&
  ((!play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&mainLevel==6&&!strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' '))||
   (game_probe_enabled&&asset_debug_enabled&&play_demo&&!demo_file&&!strcmp(levelName,"ASSET DBG ")))&&
  !manual_hd_enabled&&!asteroid_hd_enabled&&!xmas&&!isNetworkGame&&!twoPlayerMode&&
  !twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&!constantPlay&&!constantDie&&!richMode&&
  !onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&!timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}

static bool private_ember269_scope(void)
{
 return private_ember269_life.loaded&&!private_ember269_life.exhausted&&private_ember269_level_scope()&&
  terrain_file=='z'&&private_ember269_mode()==private_ember269_life.mode&&
  private_ember269_root()&&
  !strcmp(private_ember269_life.root,private_ember269_root());
}
static bool private_ember269_origin_enabled(int origin)
{
 return origin>=0&&origin<(int)COUNTOF(private_ember269_origins)&&
  (private_ember269_life.mode&(origin==0?2u:4u));
}
static int private_ember269_slot(const void *ptr)
{
 uintptr_t p=(uintptr_t)ptr,b=(uintptr_t)enemy;
 if(p<b||p-b>=sizeof(enemy)||(p-b)%sizeof(enemy[0]))return -1;
 return (int)((p-b)/sizeof(enemy[0]));
}
/* Complete deterministic live-field witness; pointers are diagnostic only.
 * Acceptance compares exact objects and generation, never these textual values. */
static void private_ember269_log(const char *phase,int slot,unsigned event,unsigned base,int part,int ok)
{
 if(!private_ember269_mode())return;
 fprintf(stderr,"EMBER269\ttick=%u\tlogic=%llu\tepoch=%llu\tphase=%s\tevent=%u\tslot=%d\tbase=%u\tpart=%d\tok=%d",
  game_probe_tick,(unsigned long long)mirror_logic_tick,(unsigned long long)private_ember269_life.epoch,phase,event,slot,base,part,ok);
 fprintf(stderr,"\tepisode=%u\tphysical=%u\tprobe=%d\tasset_debug=%d\tplay_demo=%d\tdemo_file=%p\tstopped=%d\tconstant=%d,%d,%d\teventLoc=%u\tcurLoc=%u",
  episodeNum,lvlFileNum,game_probe_enabled,asset_debug_enabled,play_demo,(void *)demo_file,stopped_demo,constantPlay,constantDie,richMode,eventLoc,curLoc);
 if(private_ember269_life.events&&event==157){const struct JE_EventRecType *r=private_ember269_life.events+event;
  fprintf(stderr,"\torigin=%u,%u,%d,%d,%d,%u,%d,%d",r->eventtime,r->eventtype,r->eventdat,r->eventdat2,r->eventdat3,r->eventdat4,r->eventdat5,r->eventdat6);}
 if(slot>=0&&slot<100){const struct JE_SingleEnemyType *e=enemy+slot;
  fprintf(stderr,"\tgen=%llu\twitness=%llu\tlive=%d\tavail=%u\ttype=%u\trecord269=%d\tbank_object=%p\tbank_data=%p\tbank_bytes=%lu\tsize=%u\tani=%u,%u,%u,%u,%u,%u\tarmor=%u\tfilter=%u\tflags=%d,%d,%d,%d\tlink_death=%u,%u\tpos=%d,%d,%u\tmotion=%d,%d,%d,%d,%d,%u,%u\taccel_aux=%d,%d,%d,%d,%d,%d,%u,%u\trev=%d,%d\tground_explode=%d,%u\ttur=%u,%u,%u\tfreq=%u,%u,%u\tlaunch=%u,%u,%u,%u\tdamage=%u,%d,%d\ticed=%u\tegr=",
   (unsigned long long)private_ember269_slots[slot].generation,(unsigned long long)private_ember269_slots[slot].witness,
   private_ember269_slots[slot].live,enemyAvail[slot],e->enemytype,e->enemydatofs==&enemyDat[269],(void *)e->sprite2s,
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
static void private_ember269_fail(void)
{
 private_ember269_frame.accepted=false;private_ember269_frame.fault=true;private_ember269_frame.quartet=false;
 if(private_ember269_frame.contributed){
  ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;
  family_fault(FC_SOURCE);
 }
}
void render_mirror_ember269_retired(unsigned slot)
{
 if(slot>=100)return;
 if(private_ember269_slots[slot].live||private_ember269_slots[slot].pending){
  private_ember269_log("retired",(int)slot,private_ember269_slots[slot].event,0,-1,0);
  if(private_ember269_frame.mask[slot])private_ember269_fail();
 }
 private_ember269_slots[slot].live=private_ember269_slots[slot].pending=private_ember269_slots[slot].initialized=false;
}
static void private_ember269_reset(void)
{
 private_ember269_frame.accepted=false;
 if(private_ember269_frame.contributed||private_ember269_frame.quartet)private_ember269_fail();
 for(unsigned i=0;i<100;i++)render_mirror_ember269_retired(i);
 private_ember269_life.call.live=false;
 if(private_ember269_life.epoch==UINT64_MAX)private_ember269_life.exhausted=true;
 else ++private_ember269_life.epoch;
 /* Consumed event bits survive renderer/bank changes. Only a real level load
  * may authorize a fresh first event; returning to an event never rearms it. */
}
static bool private_ember269_event_matches(unsigned index)
{
 int origin=private_ember269_origin(index);
 if(!private_ember269_life.events||maxEvent!=731||origin<0)return false;
 const struct JE_EventRecType *r=private_ember269_life.events+index;
 return r->eventtime==private_ember269_origins[origin].time&&r->eventtype==6&&r->eventdat==269&&
  r->eventdat2==private_ember269_origins[origin].x&&!r->eventdat3&&!r->eventdat4&&!r->eventdat5&&!r->eventdat6;
}
void render_mirror_ember269_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 private_ember269_reset();private_ember269_life.loaded=false;memset(private_ember269_life.consumed,0,sizeof private_ember269_life.consumed);
 private_ember269_life.mode=private_ember269_mode();private_ember269_life.events=events;
 if(!private_ember269_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||
  !private_ember269_event_matches(157)||
  ((private_ember269_life.mode&4u)&&!late_reuse_stream_matches(events))||
  !private_ember269_root()||!private_ember269_root()[0]||strlen(private_ember269_root())>=sizeof(private_ember269_life.root)){private_ember269_life.events=NULL;return;}
 strcpy(private_ember269_life.root,private_ember269_root());private_ember269_life.loaded=true;
 private_ember269_log("level-load",-1,0,0,-1,1);
}
static bool private_ember269_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=42012)return false;
 bool found=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank.data==enemySpriteSheets[i].data&&bank.size==enemySpriteSheets[i].size)found=true;
 return found&&asteroid1_stamp(bank.data,bank.size)==UINT64_C(0x913975450e0fc00d)&&
  asteroid1_record_stamp(269)==UINT64_C(0x587e8cbe02db82e2);
}
static bool private_ember269_colors(void)
{
 /* Exact used-index union derived from all 2688 occupied source cells. */
 for(unsigned i=0;i<COUNTOF(private_ember269_palette);i++)
  if((rgb_palette[private_ember269_palette[i].index]&0xffffffu)!=private_ember269_palette[i].rgb)return false;
 return true;
}
/* Preserve native semantics: positive current armor; evalue, iced and inactive
 * countdowns are intentionally not pinned. Native birth cycle0 preincrements. */
static bool private_ember269_shape(unsigned slot,bool birth)
{
 if(slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 if(e->enemytype!=269||e->enemydatofs!=&enemyDat[269]||!e->sprite2s)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&e->sprite2s==enemySpriteSheets+i)bound=true;
 if(!bound||!private_ember269_source(*e->sprite2s)||e->size!=1||e->scoreitem||e->special||e->edamaged||
  !e->armorleft||e->linknum||e->enemydie||e->filter||e->ani!=20||e->animin!=1||e->animax||
  e->aniwhenfire||e->aniactive!=1||(birth?e->enemycycle!=0:(e->enemycycle<1||e->enemycycle>20))||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=2||
  e->tur[0]||e->tur[1]||e->tur[2]||e->freq[0]||e->freq[1]||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 static const unsigned sequence[20]={267,267,269,269,271,271,273,273,271,271,269,269,267,267,267,267,267,267,267,267};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 return true;
}
uint64_t render_mirror_ember269_event_begin(unsigned eventloc,unsigned typeofs,unsigned pool,int unique)
{
 /* Called only at the actual case6 direct call site, not inferred in make. */
 if(private_ember269_life.call.live){private_ember269_life.call.live=false;private_ember269_fail();return 0;}
 if(!private_ember269_scope()||eventloc!=eventLoc||eventloc<1||typeofs||pool!=25||unique||
  !private_ember269_event_matches(eventloc-1))return 0;
 unsigned index=eventloc-1;int origin=private_ember269_origin(index);
 if(!private_ember269_origin_enabled(origin)||curLoc!=private_ember269_origins[origin].time||private_ember269_life.consumed[origin])return 0;
 private_ember269_life.consumed[origin]=1; /* Allocation failure also consumes origin. */
 if(private_ember269_life.serial==UINT64_MAX){private_ember269_life.exhausted=true;return 0;}
 private_ember269_life.call.live=true;private_ember269_life.call.token=++private_ember269_life.serial;
 private_ember269_life.call.epoch=private_ember269_life.epoch;private_ember269_life.call.event=index;
 private_ember269_life.call.slot=-1;private_ember269_life.call.generation=0;
 private_ember269_log("event-begin",-1,index,0,-1,1);
 return private_ember269_life.call.token;
}
void render_mirror_ember269_enemy_allocated(void *ptr,unsigned record,int unique)
{
 int slot=private_ember269_slot(ptr);if(slot<0)return;
 render_mirror_ember269_retired((unsigned)slot);
 if(private_ember269_slots[slot].generation==UINT64_MAX){private_ember269_slots[slot].exhausted=true;return;}
 if(private_ember269_slots[slot].exhausted)return;
 ++private_ember269_slots[slot].generation;
 if(private_ember269_life.call.live&&private_ember269_scope()&&record==269&&!unique&&slot>=25&&slot<50&&
  enemyAvail[slot]==1&&private_ember269_life.call.slot==-1){
  private_ember269_slots[slot].pending=true;private_ember269_slots[slot].event=private_ember269_life.call.event;
  private_ember269_life.call.slot=slot;private_ember269_life.call.generation=private_ember269_slots[slot].generation;
 }
 /* No preconstruction pointer dereference: a reused object may hold freed data. */
 if(private_ember269_mode()&&record==269)
  fprintf(stderr,"EMBER269\ttick=%u\tphase=allocated\tslot=%d\trecord=%u\tgen=%llu\tpending=%d\n",game_probe_tick,slot,record,(unsigned long long)private_ember269_slots[slot].generation,private_ember269_slots[slot].pending);
}
void render_mirror_ember269_enemy_initialized(void *ptr,unsigned record,unsigned avail)
{
 int slot=private_ember269_slot(ptr);if(slot<0)return;
 private_ember269_slots[slot].initialized=private_ember269_slots[slot].pending&&private_ember269_life.call.live&&
  private_ember269_life.call.slot==slot&&private_ember269_life.call.generation==private_ember269_slots[slot].generation&&
  record==269&&avail==0&&enemyAvail[slot]==1&&private_ember269_shape((unsigned)slot,true);
 if(private_ember269_scope()&&record==269)private_ember269_log("initialized",slot,
  private_ember269_slots[slot].pending?private_ember269_slots[slot].event:UINT_MAX,0,-1,private_ember269_slots[slot].initialized);
}
void render_mirror_ember269_event_commit(uint64_t token,unsigned allocated_one_based)
{
 if(!token)return;
 int slot=private_ember269_life.call.slot;int origin=private_ember269_origin(private_ember269_life.call.event);
 bool ok=private_ember269_life.call.live&&token==private_ember269_life.call.token&&
  private_ember269_life.call.epoch==private_ember269_life.epoch&&private_ember269_scope()&&
  slot>=25&&slot<50&&allocated_one_based==(unsigned)slot+1&&eventLoc==private_ember269_life.call.event+1&&
  private_ember269_origin_enabled(origin)&&private_ember269_event_matches(private_ember269_life.call.event)&&
  private_ember269_life.consumed[origin]&&curLoc==private_ember269_origins[origin].time;
 if(ok)ok=private_ember269_slots[slot].pending&&private_ember269_slots[slot].initialized&&
  private_ember269_life.call.generation==private_ember269_slots[slot].generation&&enemyAvail[slot]==0&&
  private_ember269_shape((unsigned)slot,true)&&enemy[slot].ey==-28&&
  enemy[slot].ex==private_ember269_life.events[eventLoc-1].eventdat2-(mapX-1)*24-12;
 if(slot>=0&&slot<100){
  private_ember269_slots[slot].live=ok;private_ember269_slots[slot].pending=false;private_ember269_slots[slot].initialized=false;
  if(ok){private_ember269_slots[slot].witness=private_ember269_slots[slot].generation;private_ember269_slots[slot].epoch=private_ember269_life.epoch;
   private_ember269_slots[slot].bank=enemy[slot].sprite2s;private_ember269_slots[slot].data=enemy[slot].sprite2s->data;private_ember269_slots[slot].bytes=enemy[slot].sprite2s->size;}
 }
 private_ember269_log(ok?"event-commit":"event-abort",slot,private_ember269_life.call.event,0,-1,ok);
 private_ember269_life.call.live=false;
}
void render_mirror_ember269_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(private_ember269_slots[i].live&&private_ember269_slots[i].bank==bank)
  render_mirror_ember269_retired(i);
 if(private_ember269_life.call.live){private_ember269_life.call.live=false;private_ember269_fail();}
}
static bool private_ember269_witness(unsigned slot)
{
 if(slot>=100)return false;
 int origin=private_ember269_origin(private_ember269_slots[slot].event);
 return slot>=25&&slot<50&&private_ember269_slots[slot].live&&!private_ember269_slots[slot].exhausted&&
  private_ember269_slots[slot].epoch==private_ember269_life.epoch&&
  private_ember269_slots[slot].generation==private_ember269_slots[slot].witness&&
  private_ember269_origin_enabled(origin)&&private_ember269_event_matches(private_ember269_slots[slot].event)&&
  private_ember269_life.consumed[origin]&&enemyAvail[slot]==0&&
  private_ember269_slots[slot].bank==enemy[slot].sprite2s&&enemy[slot].sprite2s&&
  private_ember269_slots[slot].data==enemy[slot].sprite2s->data&&private_ember269_slots[slot].bytes==enemy[slot].sprite2s->size;
}
static void private_ember269_lifecycle(void)
{
 if(private_ember269_life.loaded&&!private_ember269_scope()){
  private_ember269_reset();private_ember269_life.loaded=false;private_ember269_life.events=NULL;return;
 }
 for(unsigned i=0;i<100;i++)if(private_ember269_slots[i].live&&
  (!private_ember269_witness(i)||!enemy[i].armorleft||enemy[i].enemytype!=269||enemy[i].enemydatofs!=&enemyDat[269]))render_mirror_ember269_retired(i);
}
static void private_ember269_tick(void)
{
 private_ember269_native=false;memset(private_ember269_owned,0,sizeof private_ember269_owned);
 /* A new tick cannot inherit cached ember pixels across an early-return path. */
 if(private_ember269_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 /* Discard previous frame contribution before observing new-tick retirement. */
 memset(&private_ember269_frame,0,sizeof(private_ember269_frame));
 private_ember269_lifecycle();
}
static bool private_ember269_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;Uint8 *rgba=NULL;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshd-%u-8.hda",private_ember269_resources.root,private_ember269_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==1080000+private_ember269_images[k].base&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==private_ember269_images[k].rgba;
 if(ok)for(size_t i=3;i<bytes;i+=4)if(rgba[i]!=255){ok=false;break;}
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 private_ember269_resources.member[k]=(Asset){true,true,ASSET_ASTEROID1,(int)private_ember269_images[k].base,24,28,0,0,8,rgba};
 return true;
}
static bool private_ember269_ready(void)
{
 if(!private_ember269_scope()||!private_ember269_mode()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!private_ember269_resources.checked){private_ember269_resources.checked=true;private_ember269_resources.valid=true;
  strcpy(private_ember269_resources.root,private_ember269_life.root);
  for(unsigned i=0;i<4;i++)if(!private_ember269_load(i))private_ember269_resources.valid=false;}
 if(!private_ember269_resources.valid||strcmp(private_ember269_resources.root,private_ember269_root()))return false;
 /* All four cached resources are checked at every accepted quadrant/output,
  * never only the chosen phase. Cold failures leave terrain and other actors. */
 for(unsigned i=0;i<4;i++){const Asset *a=private_ember269_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)private_ember269_images[i].base||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,172032)!=private_ember269_images[i].rgba){private_ember269_resources.valid=false;return false;}}
 return true;
}
static void private_ember269_shutdown(void)
{
 private_ember269_reset();private_ember269_life.loaded=false;private_ember269_life.events=NULL;
 for(unsigned i=0;i<4;i++)free(private_ember269_resources.member[i].rgba);
 memset(&private_ember269_resources,0,sizeof(private_ember269_resources));
}
static bool private_ember269_dependencies(void)
{
 if(!private_ember269_scope()||!private_ember269_colors()||!private_ember269_ready())return false;
 for(unsigned i=0;i<100;i++)if(private_ember269_frame.mask[i]&&
  (!private_ember269_witness(i)||private_ember269_frame.generations[i]!=private_ember269_slots[i].generation||
   !private_ember269_source(*enemy[i].sprite2s)))return false;
 return true;
}
/* Pure accepted-frame guard: never loads assets, retires actors or faults. */
static bool private_ember269_resources_current(void)
{
 if(!private_ember269_resources.checked||!private_ember269_resources.valid||
    strcmp(private_ember269_resources.root,private_ember269_root()))return false;
 for(unsigned i=0;i<4;i++){
  const Asset *a=private_ember269_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||
     a->index!=(int)private_ember269_images[i].base||a->w!=24||a->h!=28||
     a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
     asteroid1_stamp(a->rgba,172032)!=private_ember269_images[i].rgba)return false;
 }
 return true;
}
static bool private_ember269_finish(void)
{
 if(!private_ember269_frame.contributed)return true;
 if(private_ember269_frame.fault||private_ember269_frame.quartet||!private_ember269_scope()||
  !private_ember269_colors()||!private_ember269_resources_current())return false;
 for(unsigned i=0;i<100;i++)if(private_ember269_frame.mask[i]&&
  (private_ember269_frame.mask[i]!=15||!private_ember269_witness(i)||!private_ember269_shape(i,false)||
   private_ember269_frame.generations[i]!=private_ember269_slots[i].generation||
   !private_ember269_source(*enemy[i].sprite2s)))return false;
 return true;
}

static bool private_ember269_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!private_ember269_mode()||slot>=100||enemy[slot].enemytype!=269)return false;
 if(!fc.frame_active||fc.frame_failed||!private_ember269_witness(slot))return false;
 if(private_ember269_frame.contributed&&!private_ember269_dependencies()){private_ember269_fail();return false;}
 if(x<0||x>308||y<0||y>186||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=(part==1||part==20)?12:0,py=part>=19?14:0;
 /* Entire body must be visible; native clipping remains classic. */
 if(x-px<24||x-px>264||y-py<0||y-py>156)return false;
 if((int64_t)x-px!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||
    (int64_t)y-py!=(int64_t)enemy[slot].ey-7)return false;
 if(!private_ember269_scope()||sheet!=enemy[slot].sprite2s||!sheet||filter||
    !private_ember269_shape(slot,false)||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||
    !private_ember269_source(*sheet)||!private_ember269_colors()||!private_ember269_ready())return false;
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||private_ember269_native||suppress||surface!=game_screen||surface!=VGAScreen||
    !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
    !b313_family_writer_draw_ready(fc_frame)||!family_prepare_canvas()){family_fault(FC_SOURCE);return false;}
 static const int parts[4]={0,1,19,20};
 if(!private_ember269_frame.quartet){
  if(part||private_ember269_frame.mask[slot]){family_fault(FC_ORDER);return false;}
  private_ember269_frame.quartet=true;private_ember269_frame.slot=slot;private_ember269_frame.base=base;
  private_ember269_frame.x=x;private_ember269_frame.y=y;private_ember269_frame.next=0;
 }
 if(private_ember269_frame.slot!=slot||private_ember269_frame.base!=base||
    private_ember269_frame.next>=4||part!=parts[private_ember269_frame.next]||
    x-px!=private_ember269_frame.x||y-py!=private_ember269_frame.y){family_fault(FC_ORDER);return false;}
 unsigned k=0;while(k<4&&private_ember269_images[k].base!=base)++k;
 if(k==4){family_fault(FC_SOURCE);return false;}
 private_ember269_native=true;private_ember269_image=k;private_ember269_part=part;private_ember269_x=x;private_ember269_y=y;private_ember269_pixels=0;
 private_ember269_frame.contributed=true;
 private_ember269_frame.generations[slot]=private_ember269_slots[slot].generation;
 private_ember269_frame.used|=1u<<k;
 return true;
}
static bool private_ember269_pixel(unsigned x,unsigned y,int style)
{
 if(!private_ember269_native)return false;
 unsigned px=(private_ember269_part==1||private_ember269_part==20)?12:0,py=private_ember269_part>=19?14:0;
 while(private_ember269_pixels<168&&!private_ember269_indices[private_ember269_image][(py+private_ember269_pixels/12)*24+px+private_ember269_pixels%12])++private_ember269_pixels;
 if(style!=MIRROR_NORMAL||private_ember269_pixels>=168||x!=(unsigned)private_ember269_x+private_ember269_pixels%12||y!=(unsigned)private_ember269_y+private_ember269_pixels/12||
 expected[y*320+x]!=private_ember269_indices[private_ember269_image][(py+private_ember269_pixels/12)*24+px+private_ember269_pixels%12]){family_fault(FC_ORDER);return true;}
 const Asset *a=private_ember269_resources.member+private_ember269_image;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;
  const Uint8 *p=a->rgba+(((py+y-private_ember269_y)*8+sy)*192+(px+x-private_ember269_x)*8+sx)*4;
  ((Uint32 *)canvas->pixels)[n]=0xff000000u|((Uint32)p[0]<<16)|((Uint32)p[1]<<8)|p[2];
  hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 lamp272_clear(y*320+x);triple275_clear(y*320+x);gray325_clear(y*320+x);longface573_clear(y*320+x);private_ember269_owned[y*320+x]=1;selected[y*320+x]=1;++private_ember269_pixels;return true;
}
static void private_ember269_end(void)
{
 if(!private_ember269_native)return;
 unsigned px=(private_ember269_part==1||private_ember269_part==20)?12:0,py=private_ember269_part>=19?14:0;
 while(private_ember269_pixels<168&&!private_ember269_indices[private_ember269_image][(py+private_ember269_pixels/12)*24+px+private_ember269_pixels%12])++private_ember269_pixels;
 if(private_ember269_pixels!=168||!b313_family_writer_draw_ready(fc_frame)){family_fault(FC_ORDER);private_ember269_native=false;return;}
 unsigned slot=private_ember269_frame.slot;
 private_ember269_frame.mask[slot]|=1u<<private_ember269_frame.next;
 if(++private_ember269_frame.next==4)private_ember269_frame.quartet=false;
 private_ember269_native=false;
}

Ember269FamilyStatus render_mirror_ember269_family_status(void)
{
 Ember269FamilyStatus out={0};out.requested=private_ember269_mode()!=0;out.frame=fc_frame;
 out.loaded=private_ember269_life.loaded;out.contributed=private_ember269_frame.contributed;
 out.failed=fc.frame_failed||private_ember269_frame.fault;out.state_mask=private_ember269_frame.used;
 out.blend_retirements=private_ember269_blend_retirements;
 for(unsigned i=0;i<100;i++)if(private_ember269_frame.mask[i]){
  out.slot_mask[i]=private_ember269_frame.mask[i];out.base[i]=(enemy[i].enemycycle>=1&&enemy[i].enemycycle<=20)?enemy[i].egr[enemy[i].enemycycle-1]:0;
  out.cycle[i]=enemy[i].enemycycle;out.x[i]=enemy[i].ex+enemy[i].mapoffset-6;out.y[i]=enemy[i].ey-7;
 }
 for(unsigned i=0;i<64000;i++)out.surviving_cells+=private_ember269_owned[i]!=0;
 return out;
}
bool render_mirror_ember269_family_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=64000||!private_ember269_frame.accepted||fc.frame_active||fc.frame_failed||!private_ember269_frame.contributed||!private_ember269_finish())return false;
 memcpy(out,private_ember269_owned,64000);return true;
}
static void private_ember269_blend_retired(void){++private_ember269_blend_retirements;}

static void private_ember269_accept(void){private_ember269_frame.accepted=fc.ready&&!fc.frame_failed;}
