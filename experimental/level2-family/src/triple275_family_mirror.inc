/* Private first-event triple-lamp adapter. Default OFF. No HdRegion draw or restore.
 * Art is written only on actual native indexed writer callbacks. */
static const char *triple275_root(void){const char *p=getenv("TRIPLE275_FAMILY_ASSET_DIR");return p?p:"";}
static uint64_t triple275_blend_retirements;
static bool triple275_native;
static unsigned char triple275_owned[64000];
static bool triple275_cell(unsigned off){return off<64000&&triple275_owned[off];}
static void triple275_clear(unsigned off){if(off<64000)triple275_owned[off]=0;}
static unsigned triple275_image,triple275_part,triple275_pixels;
static int triple275_x,triple275_y;
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private E1 physical2 first-event reuse. Never an asteroid/manual-campaign lease.
 * All hooks below write sidecar state only, never actor, event, palette or RNG.
 * TRIPLE275_FAMILY_CANVAS_ENABLE=1 enables only the ordered canvas adapter.
 * No environment flag means no new draws and no trace. Assets remain immutable
 * for a selected-root lifetime: disk hot reload is deliberately not supported.
 */
#include "triple275_native.inc"
static const struct {unsigned base;uint64_t rgba;} private_triple275_images[6]={
 {153,UINT64_C(0xd18a4aef60739d9c)},{155,UINT64_C(0xc3ad0a413839574f)},
 {157,UINT64_C(0x88262ba9d6ddc180)},{159,UINT64_C(0x10b801d1a503d951)},
 {161,UINT64_C(0xa6a0478233b9ff2b)},{163,UINT64_C(0xcaf3a3760e161829)}
};
static struct {
 uint64_t generation,witness,epoch;bool exhausted,pending,initialized,live;
 unsigned event;Sprite2_array *bank;const Uint8 *data;size_t bytes;
} private_triple275_slots[100];
static struct {
 uint64_t epoch,serial;bool exhausted,loaded;unsigned consumed,mode;char root[1024];
 const struct JE_EventRecType *events; /* Read-only actual table supplied at load. */
 struct {bool live;uint64_t token,epoch,generation;unsigned event;int slot;} call;
} private_triple275_life;
static struct {bool checked,valid;char root[1024];Asset member[6];} private_triple275_resources;
static struct {
 bool contributed,fault,quartet,accepted;unsigned slot,base,next,used;int x,y;
 uint64_t generation,epoch;unsigned mask[100];uint64_t generations[100];
} private_triple275_frame;
static unsigned private_triple275_mode(void)
{
 const char *v=getenv("TRIPLE275_FAMILY_CANVAS_ENABLE");
 const char *f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&f&&!strcmp(f,"1")&&v&&!strcmp(v,"1")?2:0;
}
static bool private_triple275_level_scope(void)
{
 return private_triple275_mode()&&episodeNum==1&&lvlFileNum==2&&
  ((!play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&mainLevel==6&&!strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' '))||
   (game_probe_enabled&&asset_debug_enabled&&play_demo&&!demo_file&&!strcmp(levelName,"ASSET DBG ")))&&
  !manual_hd_enabled&&!asteroid_hd_enabled&&!xmas&&!isNetworkGame&&!twoPlayerMode&&
  !twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&!constantPlay&&!constantDie&&!richMode&&
  !onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&!timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}

static bool private_triple275_scope(void)
{
 return private_triple275_life.loaded&&!private_triple275_life.exhausted&&private_triple275_level_scope()&&
  terrain_file=='z'&&private_triple275_mode()==private_triple275_life.mode&&
  triple275_root()&&
  !strcmp(private_triple275_life.root,triple275_root());
}
static int private_triple275_slot(const void *ptr)
{
 uintptr_t p=(uintptr_t)ptr,b=(uintptr_t)enemy;
 if(p<b||p-b>=sizeof(enemy)||(p-b)%sizeof(enemy[0]))return -1;
 return (int)((p-b)/sizeof(enemy[0]));
}
/* Complete deterministic live-field witness; pointers are diagnostic only.
 * Acceptance compares exact objects and generation, never these textual values. */
static void private_triple275_log(const char *phase,int slot,unsigned event,unsigned base,int part,int ok)
{
 if(!private_triple275_mode())return;
 fprintf(stderr,"TRIPLE275\ttick=%u\tlogic=%llu\tepoch=%llu\tphase=%s\tevent=%u\tslot=%d\tbase=%u\tpart=%d\tok=%d",
  game_probe_tick,(unsigned long long)mirror_logic_tick,(unsigned long long)private_triple275_life.epoch,phase,event,slot,base,part,ok);
 fprintf(stderr,"\tepisode=%u\tphysical=%u\tprobe=%d\tasset_debug=%d\tplay_demo=%d\tdemo_file=%p\tstopped=%d\tconstant=%d,%d,%d\teventLoc=%u\tcurLoc=%u",
  episodeNum,lvlFileNum,game_probe_enabled,asset_debug_enabled,play_demo,(void *)demo_file,stopped_demo,constantPlay,constantDie,richMode,eventLoc,curLoc);
 if(private_triple275_life.events&&event==150){const struct JE_EventRecType *r=private_triple275_life.events+event;
  fprintf(stderr,"\torigin=%u,%u,%d,%d,%d,%u,%d,%d",r->eventtime,r->eventtype,r->eventdat,r->eventdat2,r->eventdat3,r->eventdat4,r->eventdat5,r->eventdat6);}
 if(slot>=0&&slot<100){const struct JE_SingleEnemyType *e=enemy+slot;
  fprintf(stderr,"\tgen=%llu\twitness=%llu\tlive=%d\tavail=%u\ttype=%u\trecord275=%d\tbank_object=%p\tbank_data=%p\tbank_bytes=%lu\tsize=%u\tani=%u,%u,%u,%u,%u,%u\tarmor=%u\tfilter=%u\tflags=%d,%d,%d,%d\tlink_death=%u,%u\tpos=%d,%d,%u\tmotion=%d,%d,%d,%d,%d,%u,%u\taccel_aux=%d,%d,%d,%d,%d,%d,%u,%u\trev=%d,%d\tground_explode=%d,%u\ttur=%u,%u,%u\tfreq=%u,%u,%u\tlaunch=%u,%u,%u,%u\tdamage=%u,%d,%d\ticed=%u\tegr=",
   (unsigned long long)private_triple275_slots[slot].generation,(unsigned long long)private_triple275_slots[slot].witness,
   private_triple275_slots[slot].live,enemyAvail[slot],e->enemytype,e->enemydatofs==&enemyDat[275],(void *)e->sprite2s,
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
static void private_triple275_fail(void)
{
 private_triple275_frame.accepted=false;private_triple275_frame.fault=true;private_triple275_frame.quartet=false;
 if(private_triple275_frame.contributed){
  ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;
  family_fault(FC_SOURCE);
 }
}
void render_mirror_triple275_retired(unsigned slot)
{
 if(slot>=100)return;
 if(private_triple275_slots[slot].live||private_triple275_slots[slot].pending){
  private_triple275_log("retired",(int)slot,private_triple275_slots[slot].event,0,-1,0);
  if(private_triple275_frame.mask[slot])private_triple275_fail();
 }
 private_triple275_slots[slot].live=private_triple275_slots[slot].pending=private_triple275_slots[slot].initialized=false;
}
static void private_triple275_reset(void)
{
 private_triple275_frame.accepted=false;
 if(private_triple275_frame.contributed||private_triple275_frame.quartet)private_triple275_fail();
 for(unsigned i=0;i<100;i++)render_mirror_triple275_retired(i);
 private_triple275_life.call.live=false;
 if(private_triple275_life.epoch==UINT64_MAX)private_triple275_life.exhausted=true;
 else ++private_triple275_life.epoch;
 /* Consumed event bits survive renderer/bank changes. Only a real level load
  * may authorize a fresh first event; returning to an event never rearms it. */
}
static bool private_triple275_event_matches(unsigned index)
{
 if(!private_triple275_life.events||index!=150)return false;
 const struct JE_EventRecType *r=private_triple275_life.events+index;
 return maxEvent==731&&r->eventtime==1224&&r->eventtype==6&&r->eventdat==275&&
  r->eventdat2==114&&!r->eventdat3&&!r->eventdat4&&!r->eventdat5&&!r->eventdat6;
}
void render_mirror_triple275_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 private_triple275_reset();private_triple275_life.loaded=false;private_triple275_life.consumed=0;
 private_triple275_life.mode=private_triple275_mode();private_triple275_life.events=events;
 if(!private_triple275_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||
  !private_triple275_event_matches(150)||
  !triple275_root()||!triple275_root()[0]||strlen(triple275_root())>=sizeof(private_triple275_life.root)){private_triple275_life.events=NULL;return;}
 strcpy(private_triple275_life.root,triple275_root());private_triple275_life.loaded=true;
 private_triple275_log("level-load",-1,0,0,-1,1);
}
static bool private_triple275_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=46566)return false;
 bool found=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==23&&bank.data==enemySpriteSheets[i].data&&bank.size==enemySpriteSheets[i].size)found=true;
 return found&&asteroid1_stamp(bank.data,bank.size)==UINT64_C(0xf22ec1295ced5d11)&&
  asteroid1_record_stamp(275)==UINT64_C(0x17f7fe80fc8c2adf);
}
static bool private_triple275_colors(void)
{
 /* Complete used-index union across all six native states. Unrelated
  * animated palette ramps are not dependencies of this family. */
 for(unsigned i=1;i<=14;i++)
  if((rgb_palette[i]&0xffffffu)!=private_triple275_palette[i])return false;
 for(unsigned i=112;i<=120;i++)
  if((rgb_palette[i]&0xffffffu)!=private_triple275_palette[i])return false;
 return true;
}
static bool private_triple275_shape(unsigned slot,bool birth)
{
 if(slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 if(e->enemytype!=275||e->enemydatofs!=&enemyDat[275]||!e->sprite2s)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==23&&e->sprite2s==enemySpriteSheets+i)bound=true;
 if(!bound||!private_triple275_source(*e->sprite2s)||e->size!=1||e->scoreitem||e->special||e->edamaged||
  !e->armorleft||e->evalue||e->linknum||e->enemydie||e->filter||e->ani!=18||e->animin!=1||e->animax||
  e->aniwhenfire||e->aniactive!=1||(birth?e->enemycycle!=0:(e->enemycycle<1||e->enemycycle>18))||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=2||
  e->tur[0]||e->tur[1]||e->tur[2]||e->freq[0]||e->freq[1]||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 static const unsigned sequence[20]={153,153,155,155,153,153,157,157,159,159,157,157,161,161,163,163,161,161,0,0};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 return true;
}
uint64_t render_mirror_triple275_event_begin(unsigned eventloc,unsigned typeofs,unsigned pool,int unique)
{
 /* Called only at the actual case6 direct call site, not inferred in make. */
 if(private_triple275_life.call.live){private_triple275_life.call.live=false;private_triple275_fail();return 0;}
 if(!private_triple275_scope()||eventloc!=eventLoc||eventloc<1||typeofs||pool!=25||unique||
  curLoc!=1224||!private_triple275_event_matches(eventloc-1))return 0;
 unsigned index=eventloc-1,bit=1u;
 if(private_triple275_life.consumed&bit)return 0;
 private_triple275_life.consumed|=bit; /* Allocation failure also consumes origin. */
 if(private_triple275_life.serial==UINT64_MAX){private_triple275_life.exhausted=true;return 0;}
 private_triple275_life.call.live=true;private_triple275_life.call.token=++private_triple275_life.serial;
 private_triple275_life.call.epoch=private_triple275_life.epoch;private_triple275_life.call.event=index;
 private_triple275_life.call.slot=-1;private_triple275_life.call.generation=0;
 private_triple275_log("event-begin",-1,index,0,-1,1);
 return private_triple275_life.call.token;
}
void render_mirror_triple275_enemy_allocated(void *ptr,unsigned record,int unique)
{
 int slot=private_triple275_slot(ptr);if(slot<0)return;
 render_mirror_triple275_retired((unsigned)slot);
 if(private_triple275_slots[slot].generation==UINT64_MAX){private_triple275_slots[slot].exhausted=true;return;}
 if(private_triple275_slots[slot].exhausted)return;
 ++private_triple275_slots[slot].generation;
 if(private_triple275_life.call.live&&private_triple275_scope()&&record==275&&!unique&&slot>=25&&slot<50&&
  enemyAvail[slot]==1&&private_triple275_life.call.slot==-1){
  private_triple275_slots[slot].pending=true;private_triple275_slots[slot].event=private_triple275_life.call.event;
  private_triple275_life.call.slot=slot;private_triple275_life.call.generation=private_triple275_slots[slot].generation;
 }
 /* No preconstruction pointer dereference: a reused object may hold freed data. */
 if(private_triple275_mode()&&(record==275||record==275))
  fprintf(stderr,"TRIPLE275\ttick=%u\tphase=allocated\tslot=%d\trecord=%u\tgen=%llu\tpending=%d\n",game_probe_tick,slot,record,(unsigned long long)private_triple275_slots[slot].generation,private_triple275_slots[slot].pending);
}
void render_mirror_triple275_enemy_initialized(void *ptr,unsigned record,unsigned avail)
{
 int slot=private_triple275_slot(ptr);if(slot<0)return;
 private_triple275_slots[slot].initialized=private_triple275_slots[slot].pending&&private_triple275_life.call.live&&
  private_triple275_life.call.slot==slot&&private_triple275_life.call.generation==private_triple275_slots[slot].generation&&
  record==275&&avail==0&&enemyAvail[slot]==1&&private_triple275_shape((unsigned)slot,true);
 if(private_triple275_scope()&&(record==275||record==275))private_triple275_log("initialized",slot,
  private_triple275_slots[slot].pending?private_triple275_slots[slot].event:UINT_MAX,0,-1,private_triple275_slots[slot].initialized);
}
void render_mirror_triple275_event_commit(uint64_t token,unsigned allocated_one_based)
{
 if(!token)return;
 int slot=private_triple275_life.call.slot;
 bool ok=private_triple275_life.call.live&&token==private_triple275_life.call.token&&
  private_triple275_life.call.epoch==private_triple275_life.epoch&&private_triple275_scope()&&
  slot>=25&&slot<50&&allocated_one_based==(unsigned)slot+1&&eventLoc==private_triple275_life.call.event+1&&
  private_triple275_event_matches(private_triple275_life.call.event)&&curLoc==1224;
 if(ok)ok=private_triple275_slots[slot].pending&&private_triple275_slots[slot].initialized&&
  private_triple275_life.call.generation==private_triple275_slots[slot].generation&&enemyAvail[slot]==0&&
  private_triple275_shape((unsigned)slot,true)&&enemy[slot].ey==-28&&
  enemy[slot].ex==private_triple275_life.events[eventLoc-1].eventdat2-(mapX-1)*24-12;
 if(slot>=0&&slot<100){
  private_triple275_slots[slot].live=ok;private_triple275_slots[slot].pending=false;private_triple275_slots[slot].initialized=false;
  if(ok){private_triple275_slots[slot].witness=private_triple275_slots[slot].generation;private_triple275_slots[slot].epoch=private_triple275_life.epoch;
   private_triple275_slots[slot].bank=enemy[slot].sprite2s;private_triple275_slots[slot].data=enemy[slot].sprite2s->data;private_triple275_slots[slot].bytes=enemy[slot].sprite2s->size;}
 }
 private_triple275_log(ok?"event-commit":"event-abort",slot,private_triple275_life.call.event,0,-1,ok);
 private_triple275_life.call.live=false;
}
void render_mirror_triple275_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(private_triple275_slots[i].live&&private_triple275_slots[i].bank==bank)
  render_mirror_triple275_retired(i);
 if(private_triple275_life.call.live){private_triple275_life.call.live=false;private_triple275_fail();}
}
static bool private_triple275_witness(unsigned slot)
{
 return slot>=25&&slot<50&&private_triple275_slots[slot].live&&!private_triple275_slots[slot].exhausted&&
  private_triple275_slots[slot].epoch==private_triple275_life.epoch&&
  private_triple275_slots[slot].generation==private_triple275_slots[slot].witness&&
  private_triple275_slots[slot].event==150&&enemyAvail[slot]==0&&
  private_triple275_slots[slot].bank==enemy[slot].sprite2s&&enemy[slot].sprite2s&&
  private_triple275_slots[slot].data==enemy[slot].sprite2s->data&&private_triple275_slots[slot].bytes==enemy[slot].sprite2s->size;
}
static void private_triple275_lifecycle(void)
{
 if(private_triple275_life.loaded&&!private_triple275_scope()){
  private_triple275_reset();private_triple275_life.loaded=false;private_triple275_life.events=NULL;return;
 }
 for(unsigned i=0;i<100;i++)if(private_triple275_slots[i].live&&
  (!private_triple275_witness(i)||!enemy[i].armorleft||enemy[i].enemytype!=275||enemy[i].enemydatofs!=&enemyDat[275]))render_mirror_triple275_retired(i);
}
static void private_triple275_tick(void)
{
 triple275_native=false;memset(triple275_owned,0,sizeof triple275_owned);
 /* A new tick cannot inherit cached lamp pixels across an early-return path. */
 if(private_triple275_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 /* Discard previous frame contribution before observing new-tick retirement. */
 memset(&private_triple275_frame,0,sizeof(private_triple275_frame));
 private_triple275_lifecycle();
}
static bool private_triple275_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;Uint8 *rgba=NULL;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshs-%u-8.hda",private_triple275_resources.root,private_triple275_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==1370000+private_triple275_images[k].base&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==private_triple275_images[k].rgba;
 if(ok)for(size_t i=3;i<bytes;i+=4)if(rgba[i]!=255){ok=false;break;}
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 private_triple275_resources.member[k]=(Asset){true,true,ASSET_ASTEROID1_TRIPLE275,(int)private_triple275_images[k].base,24,28,0,0,8,rgba};
 return true;
}
static bool private_triple275_ready(void)
{
 if(!private_triple275_scope()||private_triple275_mode()!=2||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!private_triple275_resources.checked){private_triple275_resources.checked=true;private_triple275_resources.valid=true;
  strcpy(private_triple275_resources.root,private_triple275_life.root);
  for(unsigned i=0;i<6;i++)if(!private_triple275_load(i))private_triple275_resources.valid=false;}
 if(!private_triple275_resources.valid||strcmp(private_triple275_resources.root,triple275_root()))return false;
 /* All six cached resources are checked at every accepted quadrant/output,
  * never only the chosen phase. Cold failures leave terrain and other actors. */
 for(unsigned i=0;i<6;i++){const Asset *a=private_triple275_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_TRIPLE275||a->index!=(int)private_triple275_images[i].base||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,172032)!=private_triple275_images[i].rgba){private_triple275_resources.valid=false;return false;}}
 return true;
}
static void private_triple275_shutdown(void)
{
 private_triple275_reset();private_triple275_life.loaded=false;private_triple275_life.events=NULL;
 for(unsigned i=0;i<6;i++)free(private_triple275_resources.member[i].rgba);
 memset(&private_triple275_resources,0,sizeof(private_triple275_resources));
}
static bool private_triple275_dependencies(void)
{
 if(!private_triple275_scope()||!private_triple275_colors()||!private_triple275_ready())return false;
 for(unsigned i=0;i<100;i++)if(private_triple275_frame.mask[i]&&
  (!private_triple275_witness(i)||private_triple275_frame.generations[i]!=private_triple275_slots[i].generation||
   !private_triple275_source(*enemy[i].sprite2s)))return false;
 return true;
}
/* Pure accepted-frame guard: never loads assets, retires actors or faults. */
static bool triple275_resources_current(void)
{
 if(!private_triple275_resources.checked||!private_triple275_resources.valid||
    strcmp(private_triple275_resources.root,triple275_root()))return false;
 for(unsigned i=0;i<6;i++){
  const Asset *a=private_triple275_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_TRIPLE275||
     a->index!=(int)private_triple275_images[i].base||a->w!=24||a->h!=28||
     a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
     asteroid1_stamp(a->rgba,172032)!=private_triple275_images[i].rgba)return false;
 }
 return true;
}
static bool private_triple275_finish(void)
{
 if(!private_triple275_frame.contributed)return true;
 if(private_triple275_frame.fault||private_triple275_frame.quartet||!private_triple275_scope()||
  !private_triple275_colors()||!triple275_resources_current())return false;
 for(unsigned i=0;i<100;i++)if(private_triple275_frame.mask[i]&&
  (private_triple275_frame.mask[i]!=15||!private_triple275_witness(i)||!private_triple275_shape(i,false)||
   private_triple275_frame.generations[i]!=private_triple275_slots[i].generation||
   !private_triple275_source(*enemy[i].sprite2s)))return false;
 return true;
}

static bool triple275_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!private_triple275_mode()||slot>=100||enemy[slot].enemytype!=275)return false;
 if(!fc.frame_active||fc.frame_failed||!private_triple275_witness(slot))return false;
 if(private_triple275_frame.contributed&&!private_triple275_dependencies()){private_triple275_fail();return false;}
 if(x<0||x>308||y<0||y>186||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=(part==1||part==20)?12:0,py=part>=19?14:0;
 /* Entire body must be visible; native clipping remains classic. */
 if(x-px<24||x-px>264||y-py<0||y-py>156)return false;
 if((int64_t)x-px!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||
    (int64_t)y-py!=(int64_t)enemy[slot].ey-7)return false;
 if(!private_triple275_scope()||sheet!=enemy[slot].sprite2s||!sheet||filter||
    !private_triple275_shape(slot,false)||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||
    !private_triple275_source(*sheet)||!private_triple275_colors()||!private_triple275_ready())return false;
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||triple275_native||suppress||surface!=game_screen||surface!=VGAScreen||
    !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
    !b313_family_writer_draw_ready(fc_frame)||!family_prepare_canvas()){family_fault(FC_SOURCE);return false;}
 static const int parts[4]={0,1,19,20};
 if(!private_triple275_frame.quartet){
  if(part||private_triple275_frame.mask[slot]){family_fault(FC_ORDER);return false;}
  private_triple275_frame.quartet=true;private_triple275_frame.slot=slot;private_triple275_frame.base=base;
  private_triple275_frame.x=x;private_triple275_frame.y=y;private_triple275_frame.next=0;
 }
 if(private_triple275_frame.slot!=slot||private_triple275_frame.base!=base||
    private_triple275_frame.next>=4||part!=parts[private_triple275_frame.next]||
    x-px!=private_triple275_frame.x||y-py!=private_triple275_frame.y){family_fault(FC_ORDER);return false;}
 unsigned k=0;while(k<6&&private_triple275_images[k].base!=base)++k;
 if(k==6){family_fault(FC_SOURCE);return false;}
 triple275_native=true;triple275_image=k;triple275_part=part;triple275_x=x;triple275_y=y;triple275_pixels=0;
 private_triple275_frame.contributed=true;
 private_triple275_frame.generations[slot]=private_triple275_slots[slot].generation;
 private_triple275_frame.used|=1u<<k;
 return true;
}
static bool triple275_pixel(unsigned x,unsigned y,int style)
{
 if(!triple275_native)return false;
 unsigned px=(triple275_part==1||triple275_part==20)?12:0,py=triple275_part>=19?14:0;
 while(triple275_pixels<168&&!private_triple275_indices[triple275_image][(py+triple275_pixels/12)*24+px+triple275_pixels%12])++triple275_pixels;
 if(style!=MIRROR_NORMAL||triple275_pixels>=168||x!=(unsigned)triple275_x+triple275_pixels%12||y!=(unsigned)triple275_y+triple275_pixels/12||
 expected[y*320+x]!=private_triple275_indices[triple275_image][(py+triple275_pixels/12)*24+px+triple275_pixels%12]){family_fault(FC_ORDER);return true;}
 const Asset *a=private_triple275_resources.member+triple275_image;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;
  const Uint8 *p=a->rgba+(((py+y-triple275_y)*8+sy)*192+(px+x-triple275_x)*8+sx)*4;
  ((Uint32 *)canvas->pixels)[n]=0xff000000u|((Uint32)p[0]<<16)|((Uint32)p[1]<<8)|p[2];
  hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 lamp272_clear(y*320+x);gray325_clear(y*320+x);longface573_clear(y*320+x);triple275_owned[y*320+x]=1;private_ember269_clear(y*320+x);selected[y*320+x]=1;++triple275_pixels;return true;
}
static void triple275_end(void)
{
 if(!triple275_native)return;
 unsigned px=(triple275_part==1||triple275_part==20)?12:0,py=triple275_part>=19?14:0;
 while(triple275_pixels<168&&!private_triple275_indices[triple275_image][(py+triple275_pixels/12)*24+px+triple275_pixels%12])++triple275_pixels;
 if(triple275_pixels!=168||!b313_family_writer_draw_ready(fc_frame)){family_fault(FC_ORDER);triple275_native=false;return;}
 unsigned slot=private_triple275_frame.slot;
 private_triple275_frame.mask[slot]|=1u<<private_triple275_frame.next;
 if(++private_triple275_frame.next==4)private_triple275_frame.quartet=false;
 triple275_native=false;
}

Triple275FamilyStatus render_mirror_triple275_family_status(void)
{
 Triple275FamilyStatus out={0};out.requested=private_triple275_mode()!=0;out.frame=fc_frame;
 out.loaded=private_triple275_life.loaded;out.contributed=private_triple275_frame.contributed;
 out.failed=fc.frame_failed||private_triple275_frame.fault;out.state_mask=private_triple275_frame.used;
 out.blend_retirements=triple275_blend_retirements;
 for(unsigned i=0;i<100;i++)if(private_triple275_frame.mask[i]){
  out.slot_mask[i]=private_triple275_frame.mask[i];out.base[i]=(enemy[i].enemycycle>=1&&enemy[i].enemycycle<=18)?enemy[i].egr[enemy[i].enemycycle-1]:0;
  out.cycle[i]=enemy[i].enemycycle;out.x[i]=enemy[i].ex+enemy[i].mapoffset-6;out.y[i]=enemy[i].ey-7;
 }
 for(unsigned i=0;i<64000;i++)out.surviving_cells+=triple275_owned[i]!=0;
 return out;
}
bool render_mirror_triple275_family_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=64000||!private_triple275_frame.accepted||fc.frame_active||fc.frame_failed||!private_triple275_frame.contributed||!private_triple275_finish())return false;
 memcpy(out,triple275_owned,64000);return true;
}
static void triple275_blend_retired(void){++triple275_blend_retirements;}

static void triple275_accept(void){private_triple275_frame.accepted=fc.ready&&!fc.frame_failed;}
