/* Private first-event gray device adapter. Default OFF. No HdRegion draw or restore.
 * Art is written only on actual native indexed writer callbacks. */
static const char *gray325_root(void){const char *p=getenv("GRAY325_FAMILY_ASSET_DIR");return p?p:"";}
static uint64_t gray325_blend_retirements;
static bool gray325_native;
static unsigned char gray325_owned[64000];
static bool gray325_cell(unsigned off){return off<64000&&gray325_owned[off];}
static void gray325_clear(unsigned off){if(off<64000)gray325_owned[off]=0;}
static unsigned gray325_image,gray325_part,gray325_pixels;
static int gray325_x,gray325_y;
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private E1 physical2 first-event reuse. Never an asteroid/manual-campaign lease.
 * All hooks below write sidecar state only, never actor, event, palette or RNG.
 * GRAY325_FAMILY_CANVAS_ENABLE=1 enables only the ordered canvas adapter.
 * No environment flag means no new draws and no trace. Assets remain immutable
 * for a selected-root lifetime: disk hot reload is deliberately not supported.
 */
static const struct {unsigned base;uint64_t rgba;} private_gray325_images[3]={
 {11,UINT64_C(0x88265ed397c18d7c)},{125,UINT64_C(0xec456f91753ce5b4)},
 {277,UINT64_C(0x698376c61e837dd6)}
};
static const struct {unsigned index,rgb;} private_gray325_palette[]={
 {1,0x0c0c0c},{2,0x181818},{3,0x282828},{4,0x343434},{5,0x454545},{6,0x515151},{7,0x5d5d5d},{8,0x696d69},{9,0x797979},{10,0x8e8e8e},{11,0xa2a6a2},{12,0xbababa},{13,0xcfcfcf},{14,0xe7e7e7},{32,0x000804},{33,0x001404},{34,0x001c08},{192,0x003000},{193,0x004100},{194,0x005100},{195,0x005d00},{198,0x008e00},{199,0x009a04},{201,0x08b614},{202,0x0cc320},{203,0x10cf30},{205,0x20e749},{207,0x2cff69}
};

static struct {
 uint64_t generation,witness,epoch;bool exhausted,pending,initialized,live;
 unsigned event;Sprite2_array *bank;const Uint8 *data;size_t bytes;
} private_gray325_slots[100];
static struct {
 uint64_t epoch,serial;bool exhausted,loaded;unsigned consumed,mode;char root[1024];
 const struct JE_EventRecType *events; /* Read-only actual table supplied at load. */
 struct {bool live;uint64_t token,epoch,generation;unsigned event;int slot;} call;
} private_gray325_life;
static struct {bool checked,valid;char root[1024];Asset member[3];} private_gray325_resources;
static struct {
 bool contributed,fault,quartet,accepted;unsigned slot,base,next,used;int x,y;
 uint64_t generation,epoch;unsigned mask[100],cycles[100],bases[100],gates[100];int xs[100],ys[100];bool shot[100];uint64_t generations[100];
} private_gray325_frame;
static unsigned private_gray325_mode(void)
{
 const char *v=getenv("GRAY325_FAMILY_CANVAS_ENABLE");
 const char *f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&f&&!strcmp(f,"1")&&v&&!strcmp(v,"1")?2:0;
}
static bool private_gray325_level_scope(void)
{
 return private_gray325_mode()&&episodeNum==1&&lvlFileNum==2&&
  ((!play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&mainLevel==6&&!strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' '))||
   (game_probe_enabled&&asset_debug_enabled&&play_demo&&!demo_file&&!strcmp(levelName,"ASSET DBG ")))&&
  !manual_hd_enabled&&!asteroid_hd_enabled&&!xmas&&!isNetworkGame&&!twoPlayerMode&&
  !twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&!constantPlay&&!constantDie&&!richMode&&
  !onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&!timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}

static bool private_gray325_scope(void)
{
 return private_gray325_life.loaded&&!private_gray325_life.exhausted&&private_gray325_level_scope()&&
  terrain_file=='z'&&private_gray325_mode()==private_gray325_life.mode&&
  gray325_root()&&
  !strcmp(private_gray325_life.root,gray325_root());
}
static int private_gray325_slot(const void *ptr)
{
 uintptr_t p=(uintptr_t)ptr,b=(uintptr_t)enemy;
 if(p<b||p-b>=sizeof(enemy)||(p-b)%sizeof(enemy[0]))return -1;
 return (int)((p-b)/sizeof(enemy[0]));
}
/* Complete deterministic live-field witness; pointers are diagnostic only.
 * Acceptance compares exact objects and generation, never these textual values. */
static void private_gray325_log(const char *phase,int slot,unsigned event,unsigned base,int part,int ok)
{
 if(!private_gray325_mode())return;
 fprintf(stderr,"GRAY325 phase=%s frame=%llu event=%u slot=%d base=%u part=%d ok=%d\n",phase,(unsigned long long)fc_frame,event,slot,base,part,ok);
}

static void private_gray325_fail(void)
{
 private_gray325_frame.accepted=false;private_gray325_frame.fault=true;private_gray325_frame.quartet=false;
 if(private_gray325_frame.contributed){
  ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;
  family_fault(FC_SOURCE);
 }
}
void render_mirror_gray325_retired(unsigned slot)
{
 if(slot>=100)return;
 if(private_gray325_slots[slot].live||private_gray325_slots[slot].pending){
  private_gray325_log("retired",(int)slot,private_gray325_slots[slot].event,0,-1,0);
  if(private_gray325_frame.mask[slot])private_gray325_fail();
 }
 private_gray325_slots[slot].live=private_gray325_slots[slot].pending=private_gray325_slots[slot].initialized=false;
}
static void private_gray325_reset(void)
{
 private_gray325_frame.accepted=false;
 if(private_gray325_frame.contributed||private_gray325_frame.quartet)private_gray325_fail();
 for(unsigned i=0;i<100;i++)render_mirror_gray325_retired(i);
 private_gray325_life.call.live=false;
 if(private_gray325_life.epoch==UINT64_MAX)private_gray325_life.exhausted=true;
 else ++private_gray325_life.epoch;
 /* Consumed event bits survive renderer/bank changes. Only a real level load
  * may authorize a fresh first event; returning to an event never rearms it. */
}
static bool private_gray325_event_matches(unsigned index)
{
 if(!private_gray325_life.events||index!=138)return false;
 const struct JE_EventRecType *r=private_gray325_life.events+index;
 return maxEvent==731&&r->eventtime==1168&&r->eventtype==6&&r->eventdat==325&&
  r->eventdat2==210&&!r->eventdat3&&!r->eventdat4&&!r->eventdat5&&!r->eventdat6;
}
void render_mirror_gray325_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 private_gray325_reset();private_gray325_life.loaded=false;private_gray325_life.consumed=0;
 private_gray325_life.mode=private_gray325_mode();private_gray325_life.events=events;
 if(!private_gray325_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||
  !private_gray325_event_matches(138)||
  !gray325_root()||!gray325_root()[0]||strlen(gray325_root())>=sizeof(private_gray325_life.root)){private_gray325_life.events=NULL;return;}
 strcpy(private_gray325_life.root,gray325_root());private_gray325_life.loaded=true;
 private_gray325_log("level-load",-1,0,0,-1,1);
}
static bool private_gray325_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=46566)return false;
 bool found=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==23&&bank.data==enemySpriteSheets[i].data&&bank.size==enemySpriteSheets[i].size)found=true;
 return found&&asteroid1_stamp(bank.data,bank.size)==UINT64_C(0xf22ec1295ced5d11)&&
  asteroid1_record_stamp(325)==UINT64_C(0x521b35b127dbdc53);
}
static bool private_gray325_colors(void)
{
 for(unsigned i=0;i<COUNTOF(private_gray325_palette);i++)
  if((rgb_palette[private_gray325_palette[i].index]&0xffffffu)!=private_gray325_palette[i].rgb)return false;
 return true;
}
/* Stage 0 is allocation, 1 is original draw, 2 is post-draw validation.
 * A successful shot may resume the held cycle8 after its pixels were drawn. */
static bool private_gray325_shape(unsigned slot,unsigned stage)
{
 if(slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 if(e->enemytype!=325||e->enemydatofs!=&enemyDat[325]||!e->sprite2s)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==23&&e->sprite2s==enemySpriteSheets+i)bound=true;
 if(!bound||!private_gray325_source(*e->sprite2s)||e->size!=1||e->scoreitem||e->special||e->edamaged||
  !e->armorleft||e->linknum||e->enemydie||e->filter||e->ani!=8||e->animin!=1||e->animax!=8||e->aniwhenfire!=2||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=12||
  e->tur[0]!=145||e->tur[1]||e->tur[2]||e->freq[0]!=28||e->freq[1]||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 if(stage==0){if(e->enemycycle!=1||e->aniactive!=2)return false;}
 else if(e->enemycycle<1||e->enemycycle>8||
  !((e->aniactive==1&&(stage==2||e->enemycycle<8))||
    (e->aniactive==2&&(e->enemycycle==1||e->enemycycle==8))))return false;
 static const unsigned sequence[20]={277,277,277,125,125,277,277,11};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 return true;
}

uint64_t render_mirror_gray325_event_begin(unsigned eventloc,unsigned typeofs,unsigned pool,int unique)
{
 /* Called only at the actual case6 direct call site, not inferred in make. */
 if(private_gray325_life.call.live){private_gray325_life.call.live=false;private_gray325_fail();return 0;}
 if(!private_gray325_scope()||eventloc!=eventLoc||eventloc<1||typeofs||pool!=25||unique||
  curLoc!=1168||!private_gray325_event_matches(eventloc-1))return 0;
 unsigned index=eventloc-1,bit=1u;
 if(private_gray325_life.consumed&bit)return 0;
 private_gray325_life.consumed|=bit; /* Allocation failure also consumes origin. */
 if(private_gray325_life.serial==UINT64_MAX){private_gray325_life.exhausted=true;return 0;}
 private_gray325_life.call.live=true;private_gray325_life.call.token=++private_gray325_life.serial;
 private_gray325_life.call.epoch=private_gray325_life.epoch;private_gray325_life.call.event=index;
 private_gray325_life.call.slot=-1;private_gray325_life.call.generation=0;
 private_gray325_log("event-begin",-1,index,0,-1,1);
 return private_gray325_life.call.token;
}
void render_mirror_gray325_enemy_allocated(void *ptr,unsigned record,int unique)
{
 int slot=private_gray325_slot(ptr);if(slot<0)return;
 render_mirror_gray325_retired((unsigned)slot);
 if(private_gray325_slots[slot].generation==UINT64_MAX){private_gray325_slots[slot].exhausted=true;return;}
 if(private_gray325_slots[slot].exhausted)return;
 ++private_gray325_slots[slot].generation;
 if(private_gray325_life.call.live&&private_gray325_scope()&&record==325&&!unique&&slot>=25&&slot<50&&
  enemyAvail[slot]==1&&private_gray325_life.call.slot==-1){
  private_gray325_slots[slot].pending=true;private_gray325_slots[slot].event=private_gray325_life.call.event;
  private_gray325_life.call.slot=slot;private_gray325_life.call.generation=private_gray325_slots[slot].generation;
 }
 /* No preconstruction pointer dereference: a reused object may hold freed data. */
 if(private_gray325_mode()&&record==325)
  fprintf(stderr,"GRAY325\ttick=%u\tphase=allocated\tslot=%d\trecord=%u\tgen=%llu\tpending=%d\n",game_probe_tick,slot,record,(unsigned long long)private_gray325_slots[slot].generation,private_gray325_slots[slot].pending);
}
void render_mirror_gray325_enemy_initialized(void *ptr,unsigned record,unsigned avail)
{
 int slot=private_gray325_slot(ptr);if(slot<0)return;
 private_gray325_slots[slot].initialized=private_gray325_slots[slot].pending&&private_gray325_life.call.live&&
  private_gray325_life.call.slot==slot&&private_gray325_life.call.generation==private_gray325_slots[slot].generation&&
  record==325&&avail==0&&enemyAvail[slot]==1&&private_gray325_shape((unsigned)slot,0);
 if(private_gray325_scope()&&record==325)private_gray325_log("initialized",slot,
  private_gray325_slots[slot].pending?private_gray325_slots[slot].event:UINT_MAX,0,-1,private_gray325_slots[slot].initialized);
}
void render_mirror_gray325_event_commit(uint64_t token,unsigned allocated_one_based)
{
 if(!token)return;
 int slot=private_gray325_life.call.slot;
 bool ok=private_gray325_life.call.live&&token==private_gray325_life.call.token&&
  private_gray325_life.call.epoch==private_gray325_life.epoch&&private_gray325_scope()&&
  slot>=25&&slot<50&&allocated_one_based==(unsigned)slot+1&&eventLoc==private_gray325_life.call.event+1&&
  private_gray325_event_matches(private_gray325_life.call.event)&&curLoc==1168;
 if(ok)ok=private_gray325_slots[slot].pending&&private_gray325_slots[slot].initialized&&
  private_gray325_life.call.generation==private_gray325_slots[slot].generation&&enemyAvail[slot]==0&&
  private_gray325_shape((unsigned)slot,0)&&enemy[slot].ey==-28&&
  enemy[slot].ex==private_gray325_life.events[eventLoc-1].eventdat2-(mapX-1)*24-12;
 if(slot>=0&&slot<100){
  private_gray325_slots[slot].live=ok;private_gray325_slots[slot].pending=false;private_gray325_slots[slot].initialized=false;
  if(ok){private_gray325_slots[slot].witness=private_gray325_slots[slot].generation;private_gray325_slots[slot].epoch=private_gray325_life.epoch;
   private_gray325_slots[slot].bank=enemy[slot].sprite2s;private_gray325_slots[slot].data=enemy[slot].sprite2s->data;private_gray325_slots[slot].bytes=enemy[slot].sprite2s->size;}
 }
 private_gray325_log(ok?"event-commit":"event-abort",slot,private_gray325_life.call.event,0,-1,ok);
 private_gray325_life.call.live=false;
}
void render_mirror_gray325_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(private_gray325_slots[i].live&&private_gray325_slots[i].bank==bank)
  render_mirror_gray325_retired(i);
 if(private_gray325_life.call.live){private_gray325_life.call.live=false;private_gray325_fail();}
}
static bool private_gray325_witness(unsigned slot)
{
 return slot>=25&&slot<50&&private_gray325_slots[slot].live&&!private_gray325_slots[slot].exhausted&&
  private_gray325_slots[slot].epoch==private_gray325_life.epoch&&
  private_gray325_slots[slot].generation==private_gray325_slots[slot].witness&&
  private_gray325_slots[slot].event==138&&enemyAvail[slot]==0&&
  private_gray325_slots[slot].bank==enemy[slot].sprite2s&&enemy[slot].sprite2s&&
  private_gray325_slots[slot].data==enemy[slot].sprite2s->data&&private_gray325_slots[slot].bytes==enemy[slot].sprite2s->size;
}
static void private_gray325_lifecycle(void)
{
 if(private_gray325_life.loaded&&!private_gray325_scope()){
  private_gray325_reset();private_gray325_life.loaded=false;private_gray325_life.events=NULL;return;
 }
 for(unsigned i=0;i<100;i++)if(private_gray325_slots[i].live&&
  (!private_gray325_witness(i)||!enemy[i].armorleft||enemy[i].enemytype!=325||enemy[i].enemydatofs!=&enemyDat[325]))render_mirror_gray325_retired(i);
}
static void private_gray325_tick(void)
{
 gray325_native=false;memset(gray325_owned,0,sizeof gray325_owned);
 /* A new tick cannot inherit cached gray pixels across an early-return path. */
 if(private_gray325_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 /* Discard previous frame contribution before observing new-tick retirement. */
 memset(&private_gray325_frame,0,sizeof(private_gray325_frame));
 private_gray325_lifecycle();
}
static bool private_gray325_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;Uint8 *rgba=NULL;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshs-%u-8.hda",private_gray325_resources.root,private_gray325_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==1080000+private_gray325_images[k].base&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==private_gray325_images[k].rgba;
 if(ok)for(size_t i=3;i<bytes;i+=4)if(rgba[i]!=255){ok=false;break;}
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 private_gray325_resources.member[k]=(Asset){true,true,ASSET_ASTEROID1,(int)private_gray325_images[k].base,24,28,0,0,8,rgba};
 return true;
}
static bool private_gray325_ready(void)
{
 if(!private_gray325_scope()||private_gray325_mode()!=2||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!private_gray325_resources.checked){private_gray325_resources.checked=true;private_gray325_resources.valid=true;
  strcpy(private_gray325_resources.root,private_gray325_life.root);
  for(unsigned i=0;i<3;i++)if(!private_gray325_load(i))private_gray325_resources.valid=false;}
 if(!private_gray325_resources.valid||strcmp(private_gray325_resources.root,gray325_root()))return false;
 /* All three cached resources are checked at every accepted quadrant/output,
  * never only the chosen phase. Cold failures leave terrain and other actors. */
 for(unsigned i=0;i<3;i++){const Asset *a=private_gray325_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)private_gray325_images[i].base||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,172032)!=private_gray325_images[i].rgba){private_gray325_resources.valid=false;return false;}}
 return true;
}
static void private_gray325_shutdown(void)
{
 private_gray325_reset();private_gray325_life.loaded=false;private_gray325_life.events=NULL;
 for(unsigned i=0;i<3;i++)free(private_gray325_resources.member[i].rgba);
 memset(&private_gray325_resources,0,sizeof(private_gray325_resources));
}
static bool private_gray325_dependencies(void)
{
 if(!private_gray325_scope()||!private_gray325_colors()||!private_gray325_ready())return false;
 for(unsigned i=0;i<100;i++)if(private_gray325_frame.mask[i]&&
  (!private_gray325_witness(i)||private_gray325_frame.generations[i]!=private_gray325_slots[i].generation||
   enemy[i].enemycycle!=private_gray325_frame.cycles[i]||
   !(enemy[i].aniactive==private_gray325_frame.gates[i]||
     (private_gray325_frame.gates[i]==2&&enemy[i].aniactive==1&&private_gray325_frame.shot[i]))||
   !private_gray325_source(*enemy[i].sprite2s)))return false;
 return true;
}
/* Pure accepted-frame guard: never loads assets, retires actors or faults. */
static bool gray325_resources_current(void)
{
 if(!private_gray325_resources.checked||!private_gray325_resources.valid||
    strcmp(private_gray325_resources.root,gray325_root()))return false;
 for(unsigned i=0;i<3;i++){
  const Asset *a=private_gray325_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||
     a->index!=(int)private_gray325_images[i].base||a->w!=24||a->h!=28||
     a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
     asteroid1_stamp(a->rgba,172032)!=private_gray325_images[i].rgba)return false;
 }
 return true;
}
static bool private_gray325_finish(void)
{
 if(!private_gray325_frame.contributed)return true;
 if(private_gray325_frame.fault||private_gray325_frame.quartet||!private_gray325_scope()||
  !private_gray325_colors()||!gray325_resources_current())return false;
 for(unsigned i=0;i<100;i++)if(private_gray325_frame.mask[i]&&
  (private_gray325_frame.mask[i]!=15||!private_gray325_witness(i)||!private_gray325_shape(i,2)||
   private_gray325_frame.generations[i]!=private_gray325_slots[i].generation||
   enemy[i].enemycycle!=private_gray325_frame.cycles[i]||
   !(enemy[i].aniactive==private_gray325_frame.gates[i]||
     (private_gray325_frame.gates[i]==2&&enemy[i].aniactive==1&&private_gray325_frame.shot[i]))||
   !private_gray325_source(*enemy[i].sprite2s)))return false;
 return true;
}

static bool gray325_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!private_gray325_mode()||slot>=100||enemy[slot].enemytype!=325)return false;
 if(!fc.frame_active||fc.frame_failed||!private_gray325_witness(slot))return false;
 if(private_gray325_frame.contributed&&!private_gray325_dependencies()){private_gray325_fail();return false;}
 if(x<0||x>308||y<0||y>186||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=(part==1||part==20)?12:0,py=part>=19?14:0;
 /* Entire body must be visible; native clipping remains classic. */
 if(x-px<24||x-px>264||y-py<0||y-py>156)return false;
 if((int64_t)x-px!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||
    (int64_t)y-py!=(int64_t)enemy[slot].ey-7)return false;
 if(!private_gray325_scope()||sheet!=enemy[slot].sprite2s||!sheet||filter||
    !private_gray325_shape(slot,1)||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||
    !private_gray325_source(*sheet)||!private_gray325_colors()||!private_gray325_ready())return false;
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||gray325_native||suppress||surface!=game_screen||surface!=VGAScreen||
    !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
    !b313_family_writer_draw_ready(fc_frame)||!family_prepare_canvas()){family_fault(FC_SOURCE);return false;}
 static const int parts[4]={0,1,19,20};
 if(!private_gray325_frame.quartet){
  if(part||private_gray325_frame.mask[slot]){family_fault(FC_ORDER);return false;}
  private_gray325_frame.quartet=true;private_gray325_frame.slot=slot;private_gray325_frame.base=base;
  private_gray325_frame.x=x;private_gray325_frame.y=y;private_gray325_frame.next=0;
  private_gray325_frame.cycles[slot]=enemy[slot].enemycycle;private_gray325_frame.bases[slot]=base;
  private_gray325_frame.gates[slot]=enemy[slot].aniactive;private_gray325_frame.xs[slot]=x;private_gray325_frame.ys[slot]=y;
 }
 if(private_gray325_frame.slot!=slot||private_gray325_frame.base!=base||
    private_gray325_frame.next>=4||part!=parts[private_gray325_frame.next]||
    x-px!=private_gray325_frame.x||y-py!=private_gray325_frame.y){family_fault(FC_ORDER);return false;}
 unsigned k=0;while(k<3&&private_gray325_images[k].base!=base)++k;
 if(k==3){family_fault(FC_SOURCE);return false;}
 gray325_native=true;gray325_image=k;gray325_part=part;gray325_x=x;gray325_y=y;gray325_pixels=0;
 private_gray325_frame.contributed=true;
 private_gray325_frame.generations[slot]=private_gray325_slots[slot].generation;
 private_gray325_frame.used|=1u<<k;
 return true;
}
static bool gray325_pixel(unsigned x,unsigned y,int style)
{
 if(!gray325_native)return false;
 if(style!=MIRROR_NORMAL||x!=(unsigned)gray325_x+gray325_pixels%12||
    y!=(unsigned)gray325_y+gray325_pixels/12||gray325_pixels>=168){family_fault(FC_ORDER);return true;}
 const Asset *a=private_gray325_resources.member+gray325_image;
 unsigned px=(gray325_part==1||gray325_part==20)?12:0,py=gray325_part>=19?14:0;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;
  const Uint8 *p=a->rgba+(((py+y-gray325_y)*8+sy)*192+(px+x-gray325_x)*8+sx)*4;
  ((Uint32 *)canvas->pixels)[n]=0xff000000u|((Uint32)p[0]<<16)|((Uint32)p[1]<<8)|p[2];
  hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 longface573_clear(y*320+x);lamp272_clear(y*320+x);gray325_owned[y*320+x]=1;triple275_clear(y*320+x);private_ember269_clear(y*320+x);selected[y*320+x]=1;++gray325_pixels;return true;
}
static void gray325_end(void)
{
 if(!gray325_native)return;
 if(gray325_pixels!=168||!b313_family_writer_draw_ready(fc_frame)){family_fault(FC_ORDER);gray325_native=false;return;}
 unsigned slot=private_gray325_frame.slot;
 private_gray325_frame.mask[slot]|=1u<<private_gray325_frame.next;
 if(++private_gray325_frame.next==4)private_gray325_frame.quartet=false;
 gray325_native=false;
}

Gray325FamilyStatus render_mirror_gray325_family_status(void)
{
 Gray325FamilyStatus out={0};out.requested=private_gray325_mode()!=0;out.frame=fc_frame;
 out.loaded=private_gray325_life.loaded;out.contributed=private_gray325_frame.contributed;
 out.failed=fc.frame_failed||private_gray325_frame.fault;out.state_mask=private_gray325_frame.used;
 out.blend_retirements=gray325_blend_retirements;
 for(unsigned i=0;i<100;i++)if(private_gray325_frame.mask[i]){
  out.slot_mask[i]=private_gray325_frame.mask[i];out.base[i]=private_gray325_frame.bases[i];
  out.cycle[i]=private_gray325_frame.cycles[i];out.x[i]=private_gray325_frame.xs[i];out.y[i]=private_gray325_frame.ys[i];
  out.draw_gate[i]=private_gray325_frame.gates[i];out.final_gate[i]=enemy[i].aniactive;out.shot_resumed[i]=private_gray325_frame.shot[i];
 }
 for(unsigned i=0;i<64000;i++)out.surviving_cells+=gray325_owned[i]!=0;
 return out;
}
bool render_mirror_gray325_family_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=64000||!private_gray325_frame.accepted||fc.frame_active||fc.frame_failed||!private_gray325_frame.contributed||!private_gray325_finish())return false;
 memcpy(out,gray325_owned,64000);return true;
}
static void gray325_blend_retired(void){++gray325_blend_retirements;}

static void gray325_accept(void){private_gray325_frame.accepted=fc.ready&&!fc.frame_failed;}

/* This read-only sidecar is called only immediately after the original
 * successful-shot allocation changes an actor from held to active. */
void render_mirror_gray325_shot_fired(unsigned slot)
{
 if(slot<100&&private_gray325_frame.mask[slot]==15&&private_gray325_witness(slot)&&
    private_gray325_frame.generations[slot]==private_gray325_slots[slot].generation&&
    enemy[slot].enemycycle==private_gray325_frame.cycles[slot]&&
    private_gray325_frame.gates[slot]==2&&enemy[slot].aniactive==1)
  private_gray325_frame.shot[slot]=true;
}
