/* Private exact-origin long-face adapter. Default OFF. No HdRegion draw or restore.
 * Art is written only on actual native indexed writer callbacks. */
static const char *longface573_root(void){const char *p=getenv("LONGFACE573_FAMILY_ASSET_DIR");return p?p:"";}
static uint64_t longface573_blend_retirements;
static bool longface573_native;
static unsigned char longface573_owned[64000];
static bool longface573_cell(unsigned off){return off<64000&&longface573_owned[off];}
static void longface573_clear(unsigned off){if(off<64000)longface573_owned[off]=0;}
static unsigned longface573_image,longface573_part,longface573_pixels;
static int longface573_x,longface573_y;
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private E1 physical2 exact-event reuse. Never an asteroid/manual-campaign lease.
 * All hooks below write sidecar state only, never actor, event, palette or RNG.
 * LONGFACE573_FAMILY_CANVAS_ENABLE=1 enables only the ordered canvas adapter.
 * LONGFACE573_LATER230240_ENABLE=1 separately adds original events230/240;
 * it defaults OFF, requires that family flag, and latches for the level.
 * No environment flag means no new draws and no trace. Assets remain immutable
 * for a selected-root lifetime: disk hot reload is deliberately not supported.
 */
static const struct {unsigned actor,base,role;uint64_t rgba;} private_longface573_images[8]={
 {573,165,108,UINT64_C(0xf1e60dfb0ccd762f)}, {573,167,108,UINT64_C(0xcb44f1e48d92c67d)}, {574,127,135,UINT64_C(0xa9057ac4821643f4)}, {574,129,135,UINT64_C(0x4a5207799653f980)}, {575,155,108,UINT64_C(0xa25e104386a24adc)}, {575,163,108,UINT64_C(0x48657f8bf8706fd9)}, {576,123,135,UINT64_C(0x344dbc6bd1a8f57a)}, {576,125,135,UINT64_C(0x51e102be6dc30175)},
};
#include "longface573_native.inc"

static struct {
 uint64_t generation,witness,epoch,token;bool exhausted,pending,initialized,live;
 unsigned event;Sprite2_array *bank;const Uint8 *data;size_t bytes;
} private_longface573_slots[100];
static struct {
 uint64_t epoch,serial;bool exhausted,loaded,later230240;unsigned consumed[3],mode;char root[1024];
 const struct JE_EventRecType *events; /* Read-only actual table supplied at load. */
 struct {bool live;uint64_t token,epoch,generation;unsigned event,component;int slot;} call;
} private_longface573_life;
static struct {bool checked,valid;char root[1024];Asset member[8];} private_longface573_resources;
static struct {
 bool contributed,fault,quartet,accepted;unsigned slot,base,next,used;int x,y;
 uint64_t generation,epoch;unsigned mask[100],cycles[100],bases[100],gates[100];int xs[100],ys[100];bool shot[100];uint64_t generations[100];
} private_longface573_frame;
static unsigned private_longface573_mode(void)
{
 const char *v=getenv("LONGFACE573_FAMILY_CANVAS_ENABLE");
 const char *f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&f&&!strcmp(f,"1")&&v&&!strcmp(v,"1")?2:0;
}
static bool private_longface573_later_requested(void)
{
 const char *v=getenv("LONGFACE573_LATER230240_ENABLE");return v&&!strcmp(v,"1");
}
/* Zero-based script indices. All three native type12 rows choose pool75 with
 * dat6=4, then clear it to0 before the existing component hooks. */
static const struct {unsigned index,time,x,link;} private_longface573_origins[3]={
 {105,1084,42,19},{229,1616,138,19},{239,1750,138,18}
};
static unsigned private_longface573_origin(unsigned index)
{
 for(unsigned k=0;k<(private_longface573_life.later230240?3u:1u);k++)
  if(index==private_longface573_origins[k].index)return k;
 return UINT_MAX;
}
static bool private_longface573_level_scope(void)
{
 return private_longface573_mode()&&episodeNum==1&&lvlFileNum==2&&
  ((!play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&mainLevel==6&&!strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' '))||
   (game_probe_enabled&&asset_debug_enabled&&play_demo&&!demo_file&&!strcmp(levelName,"ASSET DBG ")))&&
  !manual_hd_enabled&&!asteroid_hd_enabled&&!xmas&&!isNetworkGame&&!twoPlayerMode&&
  !twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&!constantPlay&&!constantDie&&!richMode&&
  !onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&!timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}

static bool private_longface573_scope(void)
{
 return private_longface573_life.loaded&&!private_longface573_life.exhausted&&private_longface573_level_scope()&&
  terrain_file=='z'&&private_longface573_mode()==private_longface573_life.mode&&
  private_longface573_later_requested()==private_longface573_life.later230240&&
  longface573_root()&&
  !strcmp(private_longface573_life.root,longface573_root());
}
static int private_longface573_slot(const void *ptr)
{
 uintptr_t p=(uintptr_t)ptr,b=(uintptr_t)enemy;
 if(p<b||p-b>=sizeof(enemy)||(p-b)%sizeof(enemy[0]))return -1;
 return (int)((p-b)/sizeof(enemy[0]));
}
/* Complete deterministic live-field witness; pointers are diagnostic only.
 * Acceptance compares exact objects and generation, never these textual values. */
static void private_longface573_log(const char *phase,int slot,unsigned event,unsigned base,int part,int ok)
{
 if(!private_longface573_mode())return;
 fprintf(stderr,"LONGFACE573 phase=%s frame=%llu event=%u slot=%d base=%u part=%d ok=%d\n",phase,(unsigned long long)fc_frame,event,slot,base,part,ok);
}

static void private_longface573_fail(void)
{
 private_longface573_frame.accepted=false;private_longface573_frame.fault=true;private_longface573_frame.quartet=false;
 if(private_longface573_frame.contributed){
  ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;
  family_fault(FC_SOURCE);
 }
}
void render_mirror_longface573_retired(unsigned slot)
{
 if(slot>=100)return;
 if(private_longface573_slots[slot].live||private_longface573_slots[slot].pending){
  private_longface573_log("retired",(int)slot,private_longface573_slots[slot].event,0,-1,0);
  if(private_longface573_frame.mask[slot])private_longface573_fail();
 }
 private_longface573_slots[slot].live=private_longface573_slots[slot].pending=private_longface573_slots[slot].initialized=false;
}
static void private_longface573_reset(void)
{
 private_longface573_frame.accepted=false;
 if(private_longface573_frame.contributed||private_longface573_frame.quartet)private_longface573_fail();
 for(unsigned i=0;i<100;i++)render_mirror_longface573_retired(i);
 private_longface573_life.call.live=false;
 if(private_longface573_life.epoch==UINT64_MAX)private_longface573_life.exhausted=true;
 else ++private_longface573_life.epoch;
 /* Consumed event bits survive renderer/bank changes. Only a real level load
  * may authorize fresh origins; returning to any event never rearms it. */
}
static bool private_longface573_event_matches(unsigned index)
{
 unsigned k=private_longface573_origin(index);
 if(!private_longface573_life.events||k==UINT_MAX)return false;
 const struct JE_EventRecType *r=private_longface573_life.events+index;
 return maxEvent==731&&r->eventtime==private_longface573_origins[k].time&&r->eventtype==12&&r->eventdat==573&&
  r->eventdat2==private_longface573_origins[k].x&&!r->eventdat3&&r->eventdat4==private_longface573_origins[k].link&&
  !r->eventdat5&&(r->eventdat6==4||r->eventdat6==0);
}
void render_mirror_longface573_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 private_longface573_reset();private_longface573_life.loaded=false;
 memset(private_longface573_life.consumed,0,sizeof(private_longface573_life.consumed));
 private_longface573_life.later230240=private_longface573_later_requested();
 private_longface573_life.mode=private_longface573_mode();private_longface573_life.events=events;
 if(!private_longface573_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||
  !private_longface573_event_matches(105)||events[105].eventdat6!=4||
  (private_longface573_life.later230240&&
   (!private_longface573_event_matches(229)||events[229].eventdat6!=4||
    !private_longface573_event_matches(239)||events[239].eventdat6!=4))||
  !longface573_root()||!longface573_root()[0]||strlen(longface573_root())>=sizeof(private_longface573_life.root)){private_longface573_life.events=NULL;return;}
 strcpy(private_longface573_life.root,longface573_root());private_longface573_life.loaded=true;
 private_longface573_log("level-load",-1,0,0,-1,1);
}
static bool private_longface573_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data)return false;
 bool found=false;
 for(unsigned i=0;i<4;i++)if(((enemySpriteSheetIds[i]==8&&bank.size==42012&&asteroid1_stamp(bank.data,bank.size)==UINT64_C(0x913975450e0fc00d))||
 (enemySpriteSheetIds[i]==20&&bank.size==46204&&asteroid1_stamp(bank.data,bank.size)==UINT64_C(0xe2413e3aeab4d908)))&&bank.data==enemySpriteSheets[i].data&&bank.size==enemySpriteSheets[i].size)found=true;
 static const uint64_t pins[4]={UINT64_C(0x9e2db2c15d08d7cf),UINT64_C(0xa7e9369ab5711593),UINT64_C(0x002426ddfd74e431),UINT64_C(0xeacc4d90197966b3)};
 for(unsigned i=0;i<4;i++)if(asteroid1_record_stamp(573+i)!=pins[i])return false;
 return found;
}
static bool private_longface573_colors(void)
{
 /* Complete union used by all eight native states; unrelated animated ramps are not dependencies. */
 for(unsigned i=1;i<=13;i++)if((rgb_palette[i]&0xffffffu)!=private_longface573_palette[i])return false;
 return true;
}
static bool private_longface573_shape(unsigned slot,unsigned stage)
{
 if(slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 if(e->enemytype<573||e->enemytype>576||e->enemydatofs!=&enemyDat[e->enemytype]||!e->sprite2s)return false;
 unsigned component=e->enemytype-573,bank=(component&1)?20:8;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==bank&&e->sprite2s==enemySpriteSheets+i)bound=true;
 static const unsigned normal[4]={165,127,155,123},damaged[4]={167,129,163,125};
 if(!bound||!private_longface573_source(*e->sprite2s)||e->size!=1||e->scoreitem||e->special||!e->armorleft||e->filter||
 e->ani!=1||e->enemycycle!=1||e->animin!=1||e->animax||e->aniactive||e->aniwhenfire||
 e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||e->exrev!=100||e->eyrev!=100||
 e->enemyground||e->explonum!=12||e->tur[0]||e->tur[1]||e->tur[2]||e->freq[0]||e->freq[1]||e->freq[2]||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr!=damaged[component]||e->edlevel!=10||e->edani)return false;
 if(stage==0&&(e->edamaged||e->linknum||e->enemydie))return false;
 if(stage!=0){
  unsigned origin=private_longface573_origin(private_longface573_slots[slot].event);
  if(origin==UINT_MAX||e->linknum!=private_longface573_origins[origin].link||
     (e->enemydie!=0&&e->enemydie!=628))return false;
 }
 if(e->egr[0]!=(e->edamaged?damaged[component]:normal[component]))return false;
 for(unsigned i=1;i<20;i++)if(e->egr[i])return false;
 return true;
}

uint64_t render_mirror_longface573_event_begin(unsigned eventloc,unsigned typeofs,unsigned pool,int unique)
{
 /* Called only at the actual case12 component call sites, not inferred in make. */
 if(private_longface573_life.call.live){private_longface573_life.call.live=false;private_longface573_fail();return 0;}
 if(!private_longface573_scope()||eventloc!=eventLoc||eventloc<1||typeofs>3||pool!=75||unique||
  !private_longface573_event_matches(eventloc-1)||private_longface573_life.events[eventloc-1].eventdat6!=0||
  curLoc!=private_longface573_life.events[eventloc-1].eventtime)return 0;
 unsigned index=eventloc-1,origin=private_longface573_origin(index),bit=1u<<typeofs;
 if(private_longface573_life.consumed[origin]&bit)return 0;
 private_longface573_life.consumed[origin]|=bit; /* Allocation failure also consumes this component origin. */
 if(private_longface573_life.serial==UINT64_MAX){private_longface573_life.exhausted=true;return 0;}
 private_longface573_life.call.live=true;private_longface573_life.call.token=++private_longface573_life.serial;
 private_longface573_life.call.epoch=private_longface573_life.epoch;private_longface573_life.call.event=index;private_longface573_life.call.component=typeofs;
 private_longface573_life.call.slot=-1;private_longface573_life.call.generation=0;
 private_longface573_log("event-begin",-1,index,0,-1,1);
 return private_longface573_life.call.token;
}
void render_mirror_longface573_enemy_allocated(void *ptr,unsigned record,int unique)
{
 int slot=private_longface573_slot(ptr);if(slot<0)return;
 render_mirror_longface573_retired((unsigned)slot);
 if(private_longface573_slots[slot].generation==UINT64_MAX){private_longface573_slots[slot].exhausted=true;return;}
 if(private_longface573_slots[slot].exhausted)return;
 ++private_longface573_slots[slot].generation;
 if(private_longface573_life.call.live&&private_longface573_scope()&&record==573+private_longface573_life.call.component&&!unique&&slot>=75&&slot<100&&
  enemyAvail[slot]==1&&private_longface573_life.call.slot==-1){
  private_longface573_slots[slot].pending=true;private_longface573_slots[slot].event=private_longface573_life.call.event;
  private_longface573_life.call.slot=slot;private_longface573_life.call.generation=private_longface573_slots[slot].generation;
 }
 /* No preconstruction pointer dereference: a reused object may hold freed data. */
 if(private_longface573_mode()&&record==573+private_longface573_life.call.component)
  fprintf(stderr,"LONGFACE573\ttick=%u\tphase=allocated\tslot=%d\trecord=%u\tgen=%llu\tpending=%d\n",game_probe_tick,slot,record,(unsigned long long)private_longface573_slots[slot].generation,private_longface573_slots[slot].pending);
}
void render_mirror_longface573_enemy_initialized(void *ptr,unsigned record,unsigned avail)
{
 int slot=private_longface573_slot(ptr);if(slot<0)return;
 private_longface573_slots[slot].initialized=private_longface573_slots[slot].pending&&private_longface573_life.call.live&&
  private_longface573_life.call.slot==slot&&private_longface573_life.call.generation==private_longface573_slots[slot].generation&&
  record==573+private_longface573_life.call.component&&avail==0&&enemyAvail[slot]==1&&private_longface573_shape((unsigned)slot,0);
 if(private_longface573_scope()&&record==573+private_longface573_life.call.component)private_longface573_log("initialized",slot,
  private_longface573_slots[slot].pending?private_longface573_slots[slot].event:UINT_MAX,0,-1,private_longface573_slots[slot].initialized);
}
void render_mirror_longface573_event_commit(uint64_t token,unsigned allocated_one_based)
{
 if(!token)return;
 int slot=private_longface573_life.call.slot;
 bool ok=private_longface573_life.call.live&&token==private_longface573_life.call.token&&
  private_longface573_life.call.epoch==private_longface573_life.epoch&&private_longface573_scope()&&
  slot>=75&&slot<100&&allocated_one_based==(unsigned)slot+1&&eventLoc==private_longface573_life.call.event+1&&
  private_longface573_event_matches(private_longface573_life.call.event)&&
  private_longface573_life.events[private_longface573_life.call.event].eventdat6==0&&
  curLoc==private_longface573_life.events[private_longface573_life.call.event].eventtime;
 if(ok)ok=private_longface573_slots[slot].pending&&private_longface573_slots[slot].initialized&&
  private_longface573_life.call.generation==private_longface573_slots[slot].generation&&enemyAvail[slot]==0&&
  private_longface573_shape((unsigned)slot,1)&&enemy[slot].enemytype==573+private_longface573_life.call.component&&enemy[slot].ey==-28-(private_longface573_life.call.component>=2?28:0)&&
  enemy[slot].ex==private_longface573_life.events[eventLoc-1].eventdat2-(mapX-1)*24-12+(private_longface573_life.call.component%2?24:0);
 if(slot>=0&&slot<100){
  private_longface573_slots[slot].live=ok;private_longface573_slots[slot].pending=false;private_longface573_slots[slot].initialized=false;
  if(ok){private_longface573_slots[slot].token=token;private_longface573_slots[slot].witness=private_longface573_slots[slot].generation;private_longface573_slots[slot].epoch=private_longface573_life.epoch;
   private_longface573_slots[slot].bank=enemy[slot].sprite2s;private_longface573_slots[slot].data=enemy[slot].sprite2s->data;private_longface573_slots[slot].bytes=enemy[slot].sprite2s->size;}
 }
 private_longface573_log(ok?"event-commit":"event-abort",slot,private_longface573_life.call.event,0,-1,ok);
 private_longface573_life.call.live=false;
}
void render_mirror_longface573_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(private_longface573_slots[i].live&&private_longface573_slots[i].bank==bank)
  render_mirror_longface573_retired(i);
 if(private_longface573_life.call.live){private_longface573_life.call.live=false;private_longface573_fail();}
}
static bool private_longface573_witness(unsigned slot)
{
 return slot>=75&&slot<100&&private_longface573_slots[slot].live&&!private_longface573_slots[slot].exhausted&&
  private_longface573_slots[slot].epoch==private_longface573_life.epoch&&
  private_longface573_slots[slot].generation==private_longface573_slots[slot].witness&&
  private_longface573_event_matches(private_longface573_slots[slot].event)&&
  private_longface573_life.events[private_longface573_slots[slot].event].eventdat6==0&&enemyAvail[slot]==0&&
  private_longface573_slots[slot].bank==enemy[slot].sprite2s&&enemy[slot].sprite2s&&
  private_longface573_slots[slot].data==enemy[slot].sprite2s->data&&private_longface573_slots[slot].bytes==enemy[slot].sprite2s->size;
}
static void private_longface573_lifecycle(void)
{
 if(private_longface573_life.loaded&&!private_longface573_scope()){
  private_longface573_reset();private_longface573_life.loaded=false;private_longface573_life.events=NULL;return;
 }
 for(unsigned i=0;i<100;i++)if(private_longface573_slots[i].live&&
  (!private_longface573_witness(i)||!enemy[i].armorleft||enemy[i].enemytype<573||enemy[i].enemytype>576||enemy[i].enemydatofs!=&enemyDat[enemy[i].enemytype]))render_mirror_longface573_retired(i);
}
static void private_longface573_tick(void)
{
 longface573_native=false;memset(longface573_owned,0,sizeof longface573_owned);
 /* A new tick cannot inherit cached long-face pixels across an early-return path. */
 if(private_longface573_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 /* Discard previous frame contribution before observing new-tick retirement. */
 memset(&private_longface573_frame,0,sizeof(private_longface573_frame));
 private_longface573_lifecycle();
}
static bool private_longface573_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;Uint8 *rgba=NULL;
 int n=snprintf(path,sizeof(path),"%s/enemy-%s-%u-8.hda",private_longface573_resources.root,private_longface573_images[k].role==108?"newshd":"newshp",private_longface573_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==10000*private_longface573_images[k].role+private_longface573_images[k].base&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==private_longface573_images[k].rgba;
 if(ok)for(unsigned y=0;y<224;y++)for(unsigned x=0;x<192;x++)
  if(rgba[(y*192+x)*4+3]!=(private_longface573_indices[k][(y/8)*24+x/8]?255:0)){ok=false;break;}
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 private_longface573_resources.member[k]=(Asset){true,true,(int)private_longface573_images[k].role,(int)private_longface573_images[k].base,24,28,0,0,8,rgba};
 return true;
}
static bool private_longface573_ready(void)
{
 if(!private_longface573_scope()||private_longface573_mode()!=2||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!private_longface573_resources.checked){private_longface573_resources.checked=true;private_longface573_resources.valid=true;
  strcpy(private_longface573_resources.root,private_longface573_life.root);
  for(unsigned i=0;i<8;i++)if(!private_longface573_load(i))private_longface573_resources.valid=false;}
 if(!private_longface573_resources.valid||strcmp(private_longface573_resources.root,longface573_root()))return false;
 /* All eight cached resources are checked at every accepted quadrant/output,
  * never only the chosen phase. Cold failures leave terrain and other actors. */
 for(unsigned i=0;i<8;i++){const Asset *a=private_longface573_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=(int)private_longface573_images[i].role||a->index!=(int)private_longface573_images[i].base||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,172032)!=private_longface573_images[i].rgba){private_longface573_resources.valid=false;return false;}}
 return true;
}
static void private_longface573_shutdown(void)
{
 private_longface573_reset();private_longface573_life.loaded=false;private_longface573_life.events=NULL;
 for(unsigned i=0;i<8;i++)free(private_longface573_resources.member[i].rgba);
 memset(&private_longface573_resources,0,sizeof(private_longface573_resources));
}
static bool private_longface573_dependencies(void)
{
 if(!private_longface573_scope()||!private_longface573_colors()||!private_longface573_ready())return false;
 for(unsigned i=0;i<100;i++)if(private_longface573_frame.mask[i]&&
  (!private_longface573_witness(i)||private_longface573_frame.generations[i]!=private_longface573_slots[i].generation||
   enemy[i].enemycycle!=private_longface573_frame.cycles[i]||
   (enemy[i].edamaged!=private_longface573_frame.gates[i]||enemy[i].egr[0]!=private_longface573_frame.bases[i])||
   !private_longface573_source(*enemy[i].sprite2s)))return false;
 return true;
}
/* Pure accepted-frame guard: never loads assets, retires actors or faults. */
static bool longface573_resources_current(void)
{
 if(!private_longface573_resources.checked||!private_longface573_resources.valid||
    strcmp(private_longface573_resources.root,longface573_root()))return false;
 for(unsigned i=0;i<8;i++){
  const Asset *a=private_longface573_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=(int)private_longface573_images[i].role||
     a->index!=(int)private_longface573_images[i].base||a->w!=24||a->h!=28||
     a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
     asteroid1_stamp(a->rgba,172032)!=private_longface573_images[i].rgba)return false;
 }
 return true;
}
static bool private_longface573_finish(void)
{
 if(!private_longface573_frame.contributed)return true;
 if(private_longface573_frame.fault||private_longface573_frame.quartet||!private_longface573_scope()||
  !private_longface573_colors()||!longface573_resources_current())return false;
 for(unsigned i=0;i<100;i++)if(private_longface573_frame.mask[i]&&
  (private_longface573_frame.mask[i]!=15||!private_longface573_witness(i)||!private_longface573_shape(i,2)||
   private_longface573_frame.generations[i]!=private_longface573_slots[i].generation||
   enemy[i].enemycycle!=private_longface573_frame.cycles[i]||
   (enemy[i].edamaged!=private_longface573_frame.gates[i]||enemy[i].egr[0]!=private_longface573_frame.bases[i])||
   !private_longface573_source(*enemy[i].sprite2s)))return false;
 return true;
}

static bool longface573_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!private_longface573_mode()||slot>=100||(enemy[slot].enemytype<573||enemy[slot].enemytype>576))return false;
 /* Public source candidate: damaged-state art remains unqualified. */
 if(enemy[slot].edamaged)return false;
 if(!fc.frame_active||fc.frame_failed||!private_longface573_witness(slot))return false;
 if(private_longface573_frame.contributed&&!private_longface573_dependencies()){private_longface573_fail();return false;}
 if(x<0||x>308||y<0||y>186||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=(part==1||part==20)?12:0,py=part>=19?14:0;
 /* Entire body must be visible; native clipping remains classic. */
 if(x-px<24||x-px>264||y-py<0||y-py>156)return false;
 if((int64_t)x-px!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||
    (int64_t)y-py!=(int64_t)enemy[slot].ey-7)return false;
 if(!private_longface573_scope()||sheet!=enemy[slot].sprite2s||!sheet||filter||
    !private_longface573_shape(slot,1)||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||
    !private_longface573_source(*sheet)||!private_longface573_colors()||!private_longface573_ready())return false;
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||longface573_native||suppress||surface!=game_screen||surface!=VGAScreen||
    !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
    !b313_family_writer_draw_ready(fc_frame)||!family_prepare_canvas()){family_fault(FC_SOURCE);return false;}
 static const int parts[4]={0,1,19,20};
 if(!private_longface573_frame.quartet){
  if(part||private_longface573_frame.mask[slot]){family_fault(FC_ORDER);return false;}
  private_longface573_frame.quartet=true;private_longface573_frame.slot=slot;private_longface573_frame.base=base;
  private_longface573_frame.x=x;private_longface573_frame.y=y;private_longface573_frame.next=0;
  private_longface573_frame.cycles[slot]=enemy[slot].enemycycle;private_longface573_frame.bases[slot]=base;
  private_longface573_frame.gates[slot]=enemy[slot].edamaged;private_longface573_frame.xs[slot]=x;private_longface573_frame.ys[slot]=y;
 }
 if(private_longface573_frame.slot!=slot||private_longface573_frame.base!=base||
    private_longface573_frame.next>=4||part!=parts[private_longface573_frame.next]||
    x-px!=private_longface573_frame.x||y-py!=private_longface573_frame.y){family_fault(FC_ORDER);return false;}
 unsigned k=0;while(k<8&&(private_longface573_images[k].base!=base||private_longface573_images[k].actor!=enemy[slot].enemytype))++k;
 if(k==8){family_fault(FC_SOURCE);return false;}
 longface573_native=true;longface573_image=k;longface573_part=part;longface573_x=x;longface573_y=y;longface573_pixels=0;
 private_longface573_frame.contributed=true;
 private_longface573_frame.generations[slot]=private_longface573_slots[slot].generation;
 private_longface573_frame.used|=1u<<k;
 return true;
}
static bool longface573_pixel(unsigned x,unsigned y,int style)
{
 if(!longface573_native)return false;
 unsigned px=(longface573_part==1||longface573_part==20)?12:0,py=longface573_part>=19?14:0;
 while(longface573_pixels<168&&!private_longface573_indices[longface573_image][(py+longface573_pixels/12)*24+px+longface573_pixels%12])++longface573_pixels;
 if(style!=MIRROR_NORMAL||longface573_pixels>=168||x!=(unsigned)longface573_x+longface573_pixels%12||y!=(unsigned)longface573_y+longface573_pixels/12||
 expected[y*320+x]!=private_longface573_indices[longface573_image][(py+longface573_pixels/12)*24+px+longface573_pixels%12]){family_fault(FC_ORDER);return true;}
 const Asset *a=private_longface573_resources.member+longface573_image;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;
  const Uint8 *p=a->rgba+(((py+y-longface573_y)*8+sy)*192+(px+x-longface573_x)*8+sx)*4;
  ((Uint32 *)canvas->pixels)[n]=0xff000000u|((Uint32)p[0]<<16)|((Uint32)p[1]<<8)|p[2];
  hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  OHS_SURVIVAL_WRITE(canvas,(Uint32 *)canvas->pixels+n,LONGFACE573_HD_STORE_TAG);
 }
 lamp272_clear(y*320+x);gray325_clear(y*320+x);longface573_owned[y*320+x]=1;triple275_clear(y*320+x);private_ember269_clear(y*320+x);selected[y*320+x]=1;++longface573_pixels;return true;
}
static void longface573_end(void)
{
 if(!longface573_native)return;
 unsigned px=(longface573_part==1||longface573_part==20)?12:0,py=longface573_part>=19?14:0;
 while(longface573_pixels<168&&!private_longface573_indices[longface573_image][(py+longface573_pixels/12)*24+px+longface573_pixels%12])++longface573_pixels;
 if(longface573_pixels!=168||!b313_family_writer_draw_ready(fc_frame)){family_fault(FC_ORDER);longface573_native=false;return;}
 unsigned slot=private_longface573_frame.slot;
 private_longface573_frame.mask[slot]|=1u<<private_longface573_frame.next;
 if(++private_longface573_frame.next==4)private_longface573_frame.quartet=false;
 longface573_native=false;
}

Longface573FamilyStatus render_mirror_longface573_family_status(void)
{
 Longface573FamilyStatus out={0};out.requested=private_longface573_mode()!=0;out.frame=fc_frame;
 out.loaded=private_longface573_life.loaded;out.contributed=private_longface573_frame.contributed;
 out.accepted=private_longface573_frame.accepted;out.later_requested=private_longface573_life.later230240;
 for(unsigned i=0;i<100;i++){out.live[i]=private_longface573_slots[i].live;
  out.event[i]=private_longface573_slots[i].event+1;out.generation[i]=private_longface573_slots[i].generation;
  out.token[i]=private_longface573_slots[i].token;}
 out.failed=fc.frame_failed||private_longface573_frame.fault;out.state_mask=private_longface573_frame.used;
 out.blend_retirements=longface573_blend_retirements;
 for(unsigned i=0;i<100;i++)if(private_longface573_frame.mask[i]){
  out.slot_mask[i]=private_longface573_frame.mask[i];out.base[i]=private_longface573_frame.bases[i];
  out.cycle[i]=private_longface573_frame.cycles[i];out.x[i]=private_longface573_frame.xs[i];out.y[i]=private_longface573_frame.ys[i];
  out.draw_gate[i]=private_longface573_frame.gates[i];out.final_gate[i]=enemy[i].edamaged;out.shot_resumed[i]=private_longface573_frame.shot[i];
 }
 for(unsigned i=0;i<64000;i++)out.surviving_cells+=longface573_owned[i]!=0;
 return out;
}
bool render_mirror_longface573_family_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=64000||!private_longface573_frame.accepted||fc.frame_active||fc.frame_failed||!private_longface573_frame.contributed||!private_longface573_finish())return false;
 memcpy(out,longface573_owned,64000);return true;
}
static void longface573_blend_retired(void){++longface573_blend_retirements;}

static void longface573_accept(void){private_longface573_frame.accepted=fc.ready&&!fc.frame_failed;}

