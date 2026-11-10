/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private, default OFF, four sparse four-part native-callback materials. This adapter writes
 * only renderer sidecars and RGB canvas. No gameplay/RNG/event writes.
 * RANDOM_PROPS_ENABLE=1 plus RANDOM_PROPS_ASSET_DIR explicitly opts in. It cannot
 * admit a frame: only the existing actor or surviving terrain lease can.
 * Types135/136,260/261,263/265,266/268; every exact witnessed random lifetime,
 * never a scene/frame allowlist. No sibling137/262/264 or sibling267 admission.
 */
#include "random_props_native.inc"
/* Existing engine-owned table, inspected read-only. */
extern JE_word levelEnemyMax,levelEnemy[40];
static const unsigned rp_table[33]={317,318,319,320,321,322,323,324,317,318,319,320,321,322,323,324,317,318,319,320,321,322,323,324,462,260,261,263,265,266,268,135,136};
static struct {uint64_t generation,epoch,token,witness;bool exhausted,pending,initialized,live;
 unsigned record;RandomPropsBirth birth;Sprite2_array *bank;const Uint8 *data;size_t bytes;} rp_slots[100];
static struct {uint64_t epoch,serial;bool exhausted,loaded;char root[1024];
 struct {bool live;uint64_t token,epoch,generation;unsigned record;int slot;} call;} rp_life;
static struct {bool checked,valid;char root[1024];Asset member[4];} rp_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,image,part,pixels,used;
 RandomPropsDraw draw[25];RandomPropsWrite writes[25][672];} rp_frame;
static unsigned rp_witnessed_records;
static uint64_t rp_witnessed_count[8];
static bool rp_resources_current(void);
static int rp_record_index(unsigned record)
{
 for(unsigned i=0;i<8;i++)if(rp_records[i].record==record)return (int)i;
 return -1;
}
static uint8_t rp_owned[64000],rp_shadows[64000];
static uint64_t rp_blend_retirements,rp_normal_retirements,rp_shadow_writes;
static uint64_t rp_clipped,rp_unwitnessed,rp_lifetime_losses,rp_bank_losses,rp_contract_faults;
static unsigned rp_first_reason;
static const char *rp_root(void){const char *p=getenv("RANDOM_PROPS_ASSET_DIR");return p?p:"";}
static bool rp_enabled(void)
{
 const char *e=getenv("RANDOM_PROPS_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
}
static bool rp_level_scope(void)
{
 return rp_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static bool rp_table_current(void)
{
 if(levelEnemyMax!=33)return false;
 for(unsigned i=0;i<33;i++)if(levelEnemy[i]!=rp_table[i])return false;
 return true;
}
static bool rp_scope(void)
{
 return rp_life.loaded&&!rp_life.exhausted&&rp_level_scope()&&terrain_file=='z'&&
 rp_table_current()&&!strcmp(rp_life.root,rp_root());
}
static void rp_fail(unsigned reason)
{
 if(!rp_first_reason)rp_first_reason=reason;
 rp_frame.fault=true;rp_frame.accepted=false;rp_frame.active=rp_frame.pending=false;
 if(rp_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_random_props_retired(unsigned slot)
{
 if(slot>=100)return;
 if(rp_slots[slot].live||rp_slots[slot].pending){
  ++rp_lifetime_losses;
  if(slot<25&&rp_frame.draw[slot].token)rp_fail(1);
 }
 rp_slots[slot].live=rp_slots[slot].pending=rp_slots[slot].initialized=false;
 rp_slots[slot].birth.live=false;
}
static void rp_reset(void)
{
 if(rp_frame.contributed||rp_frame.active||rp_frame.pending)rp_fail(2);
 for(unsigned i=0;i<100;i++)render_mirror_random_props_retired(i);
 rp_life.call.live=false;
 if(rp_life.epoch==UINT64_MAX)rp_life.exhausted=true;else ++rp_life.epoch;
}
void render_mirror_random_props_level_begin(char map,char shape)
{
 rp_reset();rp_life.loaded=false;rp_witnessed_records=0;memset(rp_witnessed_count,0,sizeof rp_witnessed_count);
 for(unsigned i=0;i<100;i++)memset(&rp_slots[i].birth,0,sizeof rp_slots[i].birth);
 if(!rp_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||!rp_table_current()||
 !rp_root()[0]||strlen(rp_root())>=sizeof rp_life.root)return;
 strcpy(rp_life.root,rp_root());rp_life.loaded=true;
}
static int rp_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static bool rp_source(Sprite2_array *bank)
{
 if(!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data||bank->size!=42012)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank==enemySpriteSheets+i)bound=true;
 if(!bound||asteroid1_stamp(bank->data,bank->size)!=UINT64_C(0x913975450e0fc00d))return false;
 for(unsigned i=0;i<8;i++)if(asteroid1_record_stamp(rp_records[i].record)!=rp_records[i].stamp)return false;
 return true;
}
static bool rp_colors(void)
{
 for(unsigned i=0;i<COUNTOF(rp_palette);i++)if((rgb_palette[rp_palette[i].index]&0xffffffu)!=rp_palette[i].rgb)return false;
 return true;
}
static bool rp_shape(unsigned slot,bool birth)
{
 if(slot>=25)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 unsigned r=rp_slots[slot].record;int ri=rp_record_index(r);
 if(ri<0||e->enemytype!=r||e->enemydatofs!=enemyDat+r||!rp_source(e->sprite2s)||
 e->size!=1||e->filter||e->enemycycle!=1||e->ani!=1||e->animin!=1||e->animax||e->aniwhenfire||e->aniactive||
 e->scoreitem||e->special||e->edamaged||!e->armorleft||e->linknum||e->enemydie||
 e->exc||e->eyc!=rp_records[ri].speed||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||!e->enemyground||e->explonum!=2||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 for(unsigned i=0;i<3;i++)if(e->tur[i]||e->freq[i])return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=(i?0:rp_images[rp_records[ri].image].base))return false;
 /* Constructor-only fields may count down later. Positions are checked only
  * at birth and draw; finish deliberately uses the recorded draw position. */
 if(birth&&(e->mapoffset||e->ey!=-12||e->ex<6||e->ex>255||e->iced||e->launchwait||
 e->exccw||e->eyccw||e->exccwmax||e->eyccwmax||e->exccadd!=-1||e->eyccadd!=-1||
 e->exca!=-1||e->eyca!=-1||e->xminbounce!=-10000||e->xmaxbounce!=10000||
 e->yminbounce!=-10000||e->ymaxbounce!=10000))return false;
 if(birth)for(unsigned i=0;i<3;i++)if(e->eshotmultipos[i]||e->eshotwait[i]!=255)return false;
 return true;
}
uint64_t render_mirror_random_props_spawn_begin(unsigned record,unsigned pool,int unique)
{
 if(rp_life.call.live){rp_life.call.live=false;rp_fail(3);return 0;}
 if(!rp_scope()||rp_record_index(record)<0||pool||unique||!enemiesActive)return 0;
 if(rp_life.serial==UINT64_MAX){rp_life.exhausted=true;return 0;}
 rp_life.call.live=true;rp_life.call.token=++rp_life.serial;rp_life.call.epoch=rp_life.epoch;
 rp_life.call.record=record;rp_life.call.slot=-1;rp_life.call.generation=0;
 return rp_life.call.token;
}
void render_mirror_random_props_enemy_allocated(void *p,unsigned record,int unique)
{
 int s=rp_slot(p);if(s<0)return;
 render_mirror_random_props_retired((unsigned)s);
 if(rp_slots[s].generation==UINT64_MAX){rp_slots[s].exhausted=true;return;}
 if(rp_slots[s].exhausted)return;
 ++rp_slots[s].generation; /* Every allocation, including unrelated records. */
 if(rp_life.call.live&&rp_scope()&&s<25&&enemyAvail[s]==1&&!unique&&
 record==rp_life.call.record&&rp_life.call.slot==-1){
  rp_slots[s].pending=true;rp_slots[s].record=record;rp_life.call.slot=s;
  rp_life.call.generation=rp_slots[s].generation;
 }
}
void render_mirror_random_props_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 int s=rp_slot(p);if(s<0)return;
 rp_slots[s].initialized=rp_slots[s].pending&&rp_life.call.live&&rp_scope()&&s<25&&
 rp_life.call.slot==s&&rp_life.call.generation==rp_slots[s].generation&&
 record==rp_life.call.record&&avail==0&&enemyAvail[s]==1&&rp_shape((unsigned)s,true);
}
void render_mirror_random_props_spawn_commit(uint64_t token,unsigned one_based)
{
 if(!token)return;
 int s=rp_life.call.slot;
 bool ok=rp_life.call.live&&token==rp_life.call.token&&rp_life.call.epoch==rp_life.epoch&&rp_scope()&&
 s>=0&&s<25&&one_based==(unsigned)s+1;
 if(ok)ok=rp_slots[s].pending&&rp_slots[s].initialized&&rp_life.call.generation==rp_slots[s].generation&&
 enemyAvail[s]==0&&rp_slots[s].record==rp_life.call.record&&rp_shape((unsigned)s,true);
 if(s>=0&&s<100){
  rp_slots[s].live=ok;rp_slots[s].pending=rp_slots[s].initialized=false;
  if(ok){rp_slots[s].witness=rp_slots[s].generation;rp_slots[s].epoch=rp_life.epoch;rp_slots[s].token=token;
   rp_slots[s].bank=enemy[s].sprite2s;rp_slots[s].data=enemy[s].sprite2s->data;rp_slots[s].bytes=enemy[s].sprite2s->size;
   unsigned ri=(unsigned)rp_record_index(rp_slots[s].record);rp_witnessed_records|=1u<<ri;++rp_witnessed_count[ri];
   rp_slots[s].birth=(RandomPropsBirth){.epoch=rp_life.epoch,.token=token,.generation=rp_slots[s].generation,
    .slot=(unsigned)s,.record=rp_slots[s].record,.bank_role=8,.bank_bytes=42012,
    .bank_stamp=UINT64_C(0x913975450e0fc00d),.record_stamp=rp_records[ri].stamp,
    .bank_object=(uintptr_t)rp_slots[s].bank,.bank_data=(uintptr_t)rp_slots[s].data,
    .birth_time=curLoc,.birth_x=enemy[s].ex,.birth_y=enemy[s].ey,.birth_eyc=enemy[s].eyc,.live=true,.initialized=true};
  }
 }
 rp_life.call.live=false; /* Allocation failure closes rather than rearms token. */
}
void render_mirror_random_props_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(rp_slots[i].live&&rp_slots[i].bank==bank){++rp_bank_losses;render_mirror_random_props_retired(i);}
 if(rp_life.call.live){rp_life.call.live=false;rp_fail(4);}
}
static bool rp_witness(unsigned s)
{
 return s<25&&rp_slots[s].live&&!rp_slots[s].exhausted&&rp_slots[s].epoch==rp_life.epoch&&
 rp_slots[s].generation==rp_slots[s].witness&&enemyAvail[s]==0&&
 enemy[s].sprite2s&&rp_slots[s].bank==enemy[s].sprite2s&&rp_slots[s].data==enemy[s].sprite2s->data&&
 rp_slots[s].bytes==enemy[s].sprite2s->size;
}
static void rp_tick(void)
{
 if(rp_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&rp_frame,0,sizeof rp_frame);memset(rp_owned,0,sizeof rp_owned);memset(rp_shadows,0,sizeof rp_shadows);rp_first_reason=0;
 if(rp_life.loaded&&!rp_scope()){rp_reset();rp_life.loaded=false;return;}
 for(unsigned i=0;i<25;i++)if(rp_slots[i].live&&(!rp_witness(i)||!enemy[i].armorleft||
 enemy[i].enemytype!=rp_slots[i].record||enemy[i].enemydatofs!=enemyDat+rp_slots[i].record))render_mirror_random_props_retired(i);
}
static bool rp_material_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-newshd-%u-8.hda",rp_resources.root,rp_images[k].base);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==1080000+rp_images[k].base&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==rp_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 rp_resources.member[k]=(Asset){true,true,ASSET_ASTEROID1,(int)rp_images[k].base,24,28,0,0,8,rgba};return true;
}
static bool rp_resources_current(void)
{
 if(!rp_resources.checked||!rp_resources.valid||strcmp(rp_resources.root,rp_root()))return false;
 for(unsigned i=0;i<4;i++){const Asset *a=rp_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)rp_images[i].base||
  a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,172032)!=rp_images[i].rgba)return false;
 }return true;
}
static bool rp_ready(void)
{
 if(!rp_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!rp_resources.checked){rp_resources.checked=true;rp_resources.valid=true;strcpy(rp_resources.root,rp_life.root);
 for(unsigned i=0;i<4;i++)if(!rp_material_load(i))rp_resources.valid=false;}
 if(!rp_resources_current()){rp_resources.valid=false;return false;}return true;
}
static void rp_shutdown(void)
{
 rp_reset();rp_life.loaded=false;
 for(unsigned i=0;i<4;i++)free(rp_resources.member[i].rgba);
 memset(&rp_resources,0,sizeof rp_resources);
}
static bool rp_dependencies(bool partial)
{
 if(!rp_frame.contributed)return true;
 if(rp_frame.fault||!rp_scope()||!rp_colors()||!rp_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned i=0;i<25;i++)if(rp_frame.draw[i].token){const RandomPropsDraw *d=rp_frame.draw+i;unsigned s=i;
  if(!rp_witness(s)||!rp_shape(s,false)||d->generation!=rp_slots[s].generation||
  d->token!=rp_slots[s].birth.token||d->epoch!=rp_life.epoch||d->record!=rp_slots[s].record||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data)return false;
  if(!d->complete){if(!partial||!rp_frame.pending||rp_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->callback_count!=rp_totals[rp_records[rp_record_index(d->record)].image])return false;
 }
 return partial||(!rp_frame.active&&!rp_frame.pending);
}
/* Pure predicate shared by diagnostic snapshots. */
static bool rp_finish(void){return rp_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool rp_guard(void)
{
 if(rp_finish())return true;
 rp_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool rp_before_tile(unsigned slot,int part)
{
 if(rp_frame.contributed&&!rp_dependencies(true)){rp_fail(5);return false;}
 if(rp_frame.pending&&(rp_frame.active||slot!=rp_frame.slot||
 rp_frame.draw[slot].next>=4||part!=(int)rp_parts[rp_frame.draw[slot].next])){rp_fail(6);return false;}
 return true;
}
static bool rp_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool rp_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!rp_enabled()||slot>=25||rp_record_index(enemy[slot].enemytype)<0)return false;
 if(!fc.frame_active||fc.frame_failed||!rp_witness(slot)){++rp_unwitnessed;return false;}
 unsigned k;for(k=0;k<4&&part!=(int)rp_parts[k];k++);
 if(k==4){if(rp_frame.contributed)rp_fail(7);return false;}
 int64_t ox=(int64_t)x-rp_px[k],oy=(int64_t)y-rp_py[k];
 RandomPropsDraw *d=rp_frame.draw+slot;
 if(!rp_geometry(ox,oy)){++rp_clipped;if(d->token)rp_fail(8);return false;}
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter||
 !rp_scope()||sheet!=enemy[slot].sprite2s||!rp_shape(slot,false)||base!=rp_images[rp_records[rp_record_index(rp_slots[slot].record)].image].base||!rp_colors()||!rp_ready()){
  if(d->token)rp_fail(9);
  return false;
 }
 if(k==0){if(d->token||rp_frame.pending){rp_fail(10);return false;}}
 else if(!rp_frame.pending||rp_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||rp_frame.pending)rp_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||rp_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++rp_contract_faults;rp_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++rp_contract_faults;rp_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  *d=(RandomPropsDraw){.frame=fc_frame,.epoch=rp_life.epoch,.token=rp_slots[slot].birth.token,
   .generation=rp_slots[slot].generation,.slot=slot,.record=rp_slots[slot].record,
   .base=base,.cur_loc=curLoc,.bank_role=8,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  rp_frame.pending=true;rp_frame.slot=slot;rp_frame.image=rp_records[rp_record_index(d->record)].image;rp_frame.used|=1u<<rp_frame.image;
 }
 d->part_order[k]=(unsigned)part;
 rp_frame.part=k;rp_frame.pixels=0;rp_frame.active=true;rp_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool rp_retire(unsigned off,int style)
{
 bool owned=off<64000&&rp_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++rp_blend_retirements;else ++rp_normal_retirements;
 rp_owned[off]=rp_shadows[off]=0;}
 return owned;
}
static bool rp_pixel(unsigned x,unsigned y,int style)
{
 if(!rp_frame.active){if(rp_frame.pending){rp_fail(14);return true;}return false;}
 RandomPropsDraw *d=rp_frame.draw+rp_frame.slot;
 unsigned k=rp_frame.part;
 if(k>=4||rp_frame.pixels>=rp_counts[rp_frame.image][k]){++rp_contract_faults;rp_fail(15);return true;}
 const RandomPropsWrite *w=rp_native[rp_frame.image][k]+rp_frame.pixels;
 unsigned lx=rp_px[k]+w->x,ly=rp_py[k]+w->y;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=w->index||expected[y*320+x]!=w->index){
 ++rp_contract_faults;rp_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=&rp_resources.member[rp_frame.image];
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  /* Actual current canvas underlay. Alpha0 retains RGB but gains native
   * ownership; native holes never call here and remain entirely untouched. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  OHS_SURVIVAL_WRITE(canvas,dst,RANDOM_PROPS_HD_STORE_TAG);
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 rp_owned[off]=(uint8_t)(rp_frame.slot+1);rp_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=672){rp_fail(17);return true;}
 rp_frame.writes[rp_frame.slot][d->callback_count++]=(RandomPropsWrite){(uint8_t)lx,(uint8_t)ly,w->index};
 ++rp_frame.pixels;d->part_count[k]=rp_frame.pixels;return true;
}
static void rp_shadow(unsigned off)
{
 if(off<64000&&rp_owned[off]){if(rp_shadows[off]<255)++rp_shadows[off];++rp_shadow_writes;}
}
static void rp_end(void)
{
 if(!rp_frame.active)return;
 unsigned k=rp_frame.part;RandomPropsDraw *d=rp_frame.draw+rp_frame.slot;
 if(k>=4||d->next!=k||d->mask!=(1u<<k)-1||rp_frame.pixels!=rp_counts[rp_frame.image][k]||!b313_family_writer_draw_ready(fc_frame)){
 ++rp_contract_faults;rp_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;rp_frame.active=false;
 if(k==3){d->complete=d->mask==15&&d->callback_count==rp_totals[rp_frame.image];rp_frame.pending=false;if(!d->complete)rp_fail(19);}
}
static void rp_accept(void){rp_frame.accepted=fc.ready&&!fc.frame_failed&&rp_finish();}
RandomPropsFamilyStatus render_mirror_random_props_family_status(void)
{
 RandomPropsFamilyStatus s={0};s.requested=rp_enabled();s.loaded=rp_life.loaded;s.contributed=rp_frame.contributed;
 s.failed=fc.frame_failed||rp_frame.fault;s.accepted=rp_frame.accepted;s.frame=fc_frame;
 s.active=rp_frame.active;s.pending=rp_frame.pending;s.active_slot=rp_frame.slot;
 s.active_part=rp_frame.part<4?rp_parts[rp_frame.part]:UINT_MAX;s.material_mask=rp_frame.used;s.witnessed_records=rp_witnessed_records;
 memcpy(s.witnessed_count,rp_witnessed_count,sizeof s.witnessed_count);
 s.blend_retirements=rp_blend_retirements;s.normal_retirements=rp_normal_retirements;s.shadow_writes=rp_shadow_writes;
 s.clipped=rp_clipped;s.unwitnessed=rp_unwitnessed;s.lifetime_losses=rp_lifetime_losses;s.bank_losses=rp_bank_losses;
 s.contract_faults=rp_contract_faults;s.first_reason=rp_first_reason;
 for(unsigned i=0;i<25;i++)s.births[i]=rp_slots[i].birth;
 memcpy(s.draw,rp_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=rp_owned[i]!=0;s.shadowed_cells+=rp_owned[i]&&rp_shadows[i];}return s;
}
bool render_mirror_random_props_pre_draw(RandomPropsDraw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!rp_frame.active||rp_frame.part||rp_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=rp_frame.draw[rp_frame.slot];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_random_props_pre_part(RandomPropsDraw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!rp_frame.active||rp_frame.pixels||
 rp_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=rp_frame.draw[rp_frame.slot];unsigned k=rp_frame.part;*part=rp_parts[k];
 unsigned x=(unsigned)d->x+rp_px[k],y=(unsigned)d->y+rp_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_random_props_callbacks(unsigned slot,RandomPropsWrite *out,size_t capacity)
{
 if(slot>=25||!out||capacity<rp_frame.draw[slot].callback_count)return 0;
 unsigned n=rp_frame.draw[slot].callback_count;memcpy(out,rp_frame.writes[slot],n*sizeof *out);return n;
}
bool render_mirror_random_props_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!rp_frame.accepted||fc.frame_active||fc.frame_failed||
 !rp_frame.contributed||!rp_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,rp_owned,64000);memcpy(shadows,rp_shadows,64000);return true;
}
