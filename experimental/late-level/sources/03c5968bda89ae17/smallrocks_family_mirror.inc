/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private, default OFF, sparse native-callback materials. This adapter writes
 * only renderer sidecars and RGB canvas. No gameplay/RNG/event writes.
 * SMALLROCKS_ENABLE=1 plus SMALLROCKS_ASSET_DIR explicitly opts in. It cannot
 * admit a frame: only the existing actor or surviving terrain lease can.
 */
#include "smallrocks_native.inc"
/* Existing engine-owned table, inspected read-only. */
extern JE_word levelEnemyMax,levelEnemy[40];
static const unsigned sr_table[33]={317,318,319,320,321,322,323,324,317,318,319,320,321,322,323,324,317,318,319,320,321,322,323,324,462,260,261,263,265,266,268,135,136};
static const int sr_speeds[8]={2,4,3,5,4,6,3,5};
static struct {uint64_t generation,epoch,token,witness;bool exhausted,pending,initialized,live;
 unsigned record;Sprite2_array *bank;const Uint8 *data;size_t bytes;} sr_slots[100];
static struct {uint64_t epoch,serial;bool exhausted,loaded;char root[1024];
 struct {bool live;uint64_t token,epoch,generation;unsigned record;int slot;} call;} sr_life;
static struct {bool checked,valid;char root[1024];Asset member[4];} sr_resources;
static struct {bool contributed,fault,active,accepted;unsigned slot,image,pixels,used;
 SmallRocksDraw draw[25];SmallRocksWrite writes[25][153];} sr_frame;
static uint8_t sr_owned[64000],sr_shadows[64000];
static uint64_t sr_blend_retirements,sr_normal_retirements,sr_shadow_writes;
static uint64_t sr_clipped,sr_unwitnessed,sr_lifetime_losses,sr_bank_losses,sr_contract_faults;
static unsigned sr_first_reason;
static const char *sr_root(void){const char *p=getenv("SMALLROCKS_ASSET_DIR");return p?p:"";}
static bool sr_enabled(void)
{
 const char *e=getenv("SMALLROCKS_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
}
static bool sr_level_scope(void)
{
 return sr_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static bool sr_table_current(void)
{
 if(levelEnemyMax!=33)return false;
 for(unsigned i=0;i<33;i++)if(levelEnemy[i]!=sr_table[i])return false;
 return true;
}
static bool sr_scope(void)
{
 return sr_life.loaded&&!sr_life.exhausted&&sr_level_scope()&&terrain_file=='z'&&
 sr_table_current()&&!strcmp(sr_life.root,sr_root());
}
static void sr_fail(unsigned reason)
{
 if(!sr_first_reason)sr_first_reason=reason;
 sr_frame.fault=true;sr_frame.accepted=false;sr_frame.active=false;
 if(sr_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_smallrocks_retired(unsigned slot)
{
 if(slot>=100)return;
 if(sr_slots[slot].live||sr_slots[slot].pending){
  ++sr_lifetime_losses;
  if(slot<25&&sr_frame.draw[slot].token)sr_fail(1);
 }
 sr_slots[slot].live=sr_slots[slot].pending=sr_slots[slot].initialized=false;
}
static void smallrocks_reset(void)
{
 if(sr_frame.contributed||sr_frame.active)sr_fail(2);
 for(unsigned i=0;i<100;i++)render_mirror_smallrocks_retired(i);
 sr_life.call.live=false;
 if(sr_life.epoch==UINT64_MAX)sr_life.exhausted=true;else ++sr_life.epoch;
}
void render_mirror_smallrocks_level_begin(char map,char shape)
{
 smallrocks_reset();sr_life.loaded=false;
 if(!sr_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||!sr_table_current()||
 !sr_root()[0]||strlen(sr_root())>=sizeof sr_life.root)return;
 strcpy(sr_life.root,sr_root());sr_life.loaded=true;
}
static int sr_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static bool sr_source(Sprite2_array *bank)
{
 if(!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data||bank->size!=42012)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank==enemySpriteSheets+i)bound=true;
 if(!bound||asteroid1_stamp(bank->data,bank->size)!=UINT64_C(0x913975450e0fc00d))return false;
 for(unsigned i=0;i<8;i++)if(asteroid1_record_stamp(317+i)!=sr_records[i])return false;
 return true;
}
static bool sr_colors(void)
{
 for(unsigned i=0;i<COUNTOF(sr_palette);i++)if((rgb_palette[sr_palette[i].index]&0xffffffu)!=sr_palette[i].rgb)return false;
 return true;
}
static bool sr_shape(unsigned slot,bool birth)
{
 if(slot>=25)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 unsigned r=sr_slots[slot].record;
 if(r<317||r>324||e->enemytype!=r||e->enemydatofs!=enemyDat+r||!sr_source(e->sprite2s)||
 e->size||e->filter||e->enemycycle!=1||e->ani!=1||e->animin!=1||e->animax||e->aniwhenfire||e->aniactive||
 e->scoreitem||e->special||e->edamaged||!e->armorleft||e->linknum||e->enemydie||
 e->exc||e->eyc!=sr_speeds[r-317]||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||!e->enemyground||e->explonum!=2||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 for(unsigned i=0;i<3;i++)if(e->tur[i]||e->freq[i])return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=(i?0:sr_images[(r-317)/2].base))return false;
 /* Constructor-only fields may count down later. Positions are checked only
  * at birth and draw; finish deliberately uses the recorded draw position. */
 if(birth&&(e->mapoffset||e->ey!=-12||e->ex<6||e->ex>255||e->iced||e->launchwait||
 e->exccw||e->eyccw||e->exccwmax||e->eyccwmax||e->exccadd!=-1||e->eyccadd!=-1||
 e->exca!=-1||e->eyca!=-1||e->xminbounce!=-10000||e->xmaxbounce!=10000||
 e->yminbounce!=-10000||e->ymaxbounce!=10000))return false;
 if(birth)for(unsigned i=0;i<3;i++)if(e->eshotmultipos[i]||e->eshotwait[i]!=255)return false;
 return true;
}
uint64_t render_mirror_smallrocks_spawn_begin(unsigned record,unsigned pool,int unique)
{
 if(sr_life.call.live){sr_life.call.live=false;sr_fail(3);return 0;}
 if(!sr_scope()||record<317||record>324||pool||unique||!enemiesActive)return 0;
 if(sr_life.serial==UINT64_MAX){sr_life.exhausted=true;return 0;}
 sr_life.call.live=true;sr_life.call.token=++sr_life.serial;sr_life.call.epoch=sr_life.epoch;
 sr_life.call.record=record;sr_life.call.slot=-1;sr_life.call.generation=0;
 return sr_life.call.token;
}
void render_mirror_smallrocks_enemy_allocated(void *p,unsigned record,int unique)
{
 int s=sr_slot(p);if(s<0)return;
 render_mirror_smallrocks_retired((unsigned)s);
 if(sr_slots[s].generation==UINT64_MAX){sr_slots[s].exhausted=true;return;}
 if(sr_slots[s].exhausted)return;
 ++sr_slots[s].generation; /* Every allocation, including unrelated records. */
 if(sr_life.call.live&&sr_scope()&&s<25&&enemyAvail[s]==1&&!unique&&
 record==sr_life.call.record&&sr_life.call.slot==-1){
  sr_slots[s].pending=true;sr_slots[s].record=record;sr_life.call.slot=s;
  sr_life.call.generation=sr_slots[s].generation;
 }
}
void render_mirror_smallrocks_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 int s=sr_slot(p);if(s<0)return;
 sr_slots[s].initialized=sr_slots[s].pending&&sr_life.call.live&&sr_scope()&&s<25&&
 sr_life.call.slot==s&&sr_life.call.generation==sr_slots[s].generation&&
 record==sr_life.call.record&&avail==0&&enemyAvail[s]==1&&sr_shape((unsigned)s,true);
}
void render_mirror_smallrocks_spawn_commit(uint64_t token,unsigned one_based)
{
 if(!token)return;
 int s=sr_life.call.slot;
 bool ok=sr_life.call.live&&token==sr_life.call.token&&sr_life.call.epoch==sr_life.epoch&&sr_scope()&&
 s>=0&&s<25&&one_based==(unsigned)s+1;
 if(ok)ok=sr_slots[s].pending&&sr_slots[s].initialized&&sr_life.call.generation==sr_slots[s].generation&&
 enemyAvail[s]==0&&sr_slots[s].record==sr_life.call.record&&sr_shape((unsigned)s,true);
 if(s>=0&&s<100){
  sr_slots[s].live=ok;sr_slots[s].pending=sr_slots[s].initialized=false;
  if(ok){sr_slots[s].witness=sr_slots[s].generation;sr_slots[s].epoch=sr_life.epoch;sr_slots[s].token=token;
   sr_slots[s].bank=enemy[s].sprite2s;sr_slots[s].data=enemy[s].sprite2s->data;sr_slots[s].bytes=enemy[s].sprite2s->size;}
 }
 sr_life.call.live=false; /* Allocation failure closes rather than rearms token. */
}
void render_mirror_smallrocks_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(sr_slots[i].live&&sr_slots[i].bank==bank){++sr_bank_losses;render_mirror_smallrocks_retired(i);}
 if(sr_life.call.live){sr_life.call.live=false;sr_fail(4);}
}
static bool sr_witness(unsigned s)
{
 return s<25&&sr_slots[s].live&&!sr_slots[s].exhausted&&sr_slots[s].epoch==sr_life.epoch&&
 sr_slots[s].generation==sr_slots[s].witness&&enemyAvail[s]==0&&
 enemy[s].sprite2s&&sr_slots[s].bank==enemy[s].sprite2s&&sr_slots[s].data==enemy[s].sprite2s->data&&
 sr_slots[s].bytes==enemy[s].sprite2s->size;
}
static void smallrocks_tick(void)
{
 if(sr_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&sr_frame,0,sizeof sr_frame);memset(sr_owned,0,sizeof sr_owned);memset(sr_shadows,0,sizeof sr_shadows);sr_first_reason=0;
 if(sr_life.loaded&&!sr_scope()){smallrocks_reset();sr_life.loaded=false;return;}
 for(unsigned i=0;i<25;i++)if(sr_slots[i].live&&(!sr_witness(i)||!enemy[i].armorleft||
 enemy[i].enemytype!=sr_slots[i].record||enemy[i].enemydatofs!=enemyDat+sr_slots[i].record))render_mirror_smallrocks_retired(i);
}
static bool sr_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-newshd-%u-8.hda",sr_resources.root,sr_images[k].base);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=43008;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==1080000+sr_images[k].base&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==sr_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 sr_resources.member[k]=(Asset){true,true,ASSET_ASTEROID1,(int)sr_images[k].base,12,14,0,0,8,rgba};return true;
}
static bool sr_resources_current(void)
{
 if(!sr_resources.checked||!sr_resources.valid||strcmp(sr_resources.root,sr_root()))return false;
 for(unsigned i=0;i<4;i++){const Asset *a=sr_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)sr_images[i].base||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,43008)!=sr_images[i].rgba)return false;
 }return true;
}
static bool sr_ready(void)
{
 if(!sr_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!sr_resources.checked){sr_resources.checked=true;sr_resources.valid=true;strcpy(sr_resources.root,sr_life.root);
 for(unsigned i=0;i<4;i++)if(!sr_load(i))sr_resources.valid=false;}
 if(!sr_resources_current()){sr_resources.valid=false;return false;}return true;
}
static void smallrocks_shutdown(void)
{
 smallrocks_reset();sr_life.loaded=false;
 for(unsigned i=0;i<4;i++)free(sr_resources.member[i].rgba);
 memset(&sr_resources,0,sizeof sr_resources);
}
static bool smallrocks_finish(void)
{
 if(!sr_frame.contributed)return true;
 if(sr_frame.fault||sr_frame.active||!sr_scope()||!sr_colors()||!sr_resources_current())return false;
 for(unsigned i=0;i<25;i++)if(sr_frame.draw[i].token){const SmallRocksDraw *d=sr_frame.draw+i;
  if(!d->complete||!sr_witness(i)||!sr_shape(i,false)||d->generation!=sr_slots[i].generation||
  d->token!=sr_slots[i].token||d->epoch!=sr_life.epoch||d->record!=sr_slots[i].record||
  d->callback_count!=sr_counts[(d->record-317)/2])return false;
 }return true;
}
static bool smallrocks_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!sr_enabled()||slot>=25||enemy[slot].enemytype<317||enemy[slot].enemytype>324)return false;
 if(!fc.frame_active||fc.frame_failed||!sr_witness(slot)){++sr_unwitnessed;return false;}
 /* Prior contributors remain dependencies even if all their pixels retire. */
 if(sr_frame.contributed&&!smallrocks_finish()){sr_fail(5);return false;}
 if(part||filter||x<24||x>276||y<0||y>170){++sr_clipped;return false;}
 if((int64_t)x!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset||(int64_t)y!=enemy[slot].ey)return false;
 if(!sr_scope()||sheet!=enemy[slot].sprite2s||!sr_shape(slot,false)||base!=sr_images[(sr_slots[slot].record-317)/2].base||
 !sr_colors()||!sr_ready())return false;
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||sr_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++sr_contract_faults;family_fault(FC_SOURCE);return false;}
 /* A 12x14 local consistency guard before any native rock store. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++sr_contract_faults;family_fault(FC_WRITER);return false;}
 if(sr_frame.draw[slot].token){++sr_contract_faults;family_fault(FC_ORDER);return false;}
 unsigned k=(sr_slots[slot].record-317)/2;
 SmallRocksDraw *d=sr_frame.draw+slot;
 *d=(SmallRocksDraw){.frame=fc_frame,.epoch=sr_life.epoch,.token=sr_slots[slot].token,.generation=sr_slots[slot].generation,
 .slot=slot,.record=sr_slots[slot].record,.base=base,.cur_loc=curLoc,.bank_role=8,.bank_bytes=(unsigned)sheet->size,
 .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=x,.y=y};
 sr_frame.slot=slot;sr_frame.image=k;sr_frame.pixels=0;sr_frame.active=true;sr_frame.contributed=true;sr_frame.used|=1u<<k;
 return true;
}
/* Called before any other private pixel hook. Later writers revoke this owner
 * even when they return early. Keep the prior-owned result for generic blend.
 * An active rock replaces old rock ownership in its own exact callback. */
static bool smallrocks_retire(unsigned off,int style)
{
 bool owned=off<64000&&sr_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++sr_blend_retirements;else ++sr_normal_retirements;
 sr_owned[off]=sr_shadows[off]=0;}
 return owned;
}
static bool smallrocks_pixel(unsigned x,unsigned y,int style)
{
 if(!sr_frame.active)return false;
 SmallRocksDraw *d=sr_frame.draw+sr_frame.slot;
 unsigned k=sr_frame.image,native_count=sr_counts[k];
 const SmallRocksWrite *w=sr_native[k]+sr_frame.pixels;
 if(style!=MIRROR_NORMAL||sr_frame.pixels>=native_count||x!=(unsigned)d->x+w->x||y!=(unsigned)d->y+w->y||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=w->index||expected[y*320+x]!=w->index){
 ++sr_contract_faults;sr_fail(6);family_fault(FC_ORDER);return true;}
 const Asset *a=sr_resources.member+k;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
 size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
 const Uint8 *art=a->rgba+(((unsigned)w->y*8+sy)*96+(unsigned)w->x*8+sx)*4;
 /* Even alpha0 is a witnessed native write: preserve live canvas RGB while
  * assigning all64 subpixels this identity. Native holes never call here. */
 *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 sr_owned[off]=(uint8_t)(sr_frame.slot+1);sr_shadows[off]=0;selected[off]=1;
 sr_frame.writes[sr_frame.slot][sr_frame.pixels]=(SmallRocksWrite){(uint8_t)(x-d->x),(uint8_t)(y-d->y),((const Uint8 *)fc_source_pixels)[off]};
 ++sr_frame.pixels;d->callback_count=sr_frame.pixels;return true;
}
static void smallrocks_shadow(unsigned off)
{
 if(off<64000&&sr_owned[off]){if(sr_shadows[off]<255)++sr_shadows[off];++sr_shadow_writes;}
}
static void smallrocks_end(void)
{
 if(!sr_frame.active)return;
 if(sr_frame.pixels!=sr_counts[sr_frame.image]||!b313_family_writer_draw_ready(fc_frame)){
 ++sr_contract_faults;sr_fail(7);family_fault(FC_ORDER);return;}
 sr_frame.draw[sr_frame.slot].complete=true;sr_frame.active=false;
}
static void smallrocks_accept(void){sr_frame.accepted=fc.ready&&!fc.frame_failed&&smallrocks_finish();}
SmallRocksFamilyStatus render_mirror_smallrocks_family_status(void)
{
 SmallRocksFamilyStatus s={0};s.requested=sr_enabled();s.loaded=sr_life.loaded;s.contributed=sr_frame.contributed;
 s.failed=fc.frame_failed||sr_frame.fault;s.accepted=sr_frame.accepted;s.frame=fc_frame;s.material_mask=sr_frame.used;
 s.blend_retirements=sr_blend_retirements;s.normal_retirements=sr_normal_retirements;s.shadow_writes=sr_shadow_writes;
 s.clipped=sr_clipped;s.unwitnessed=sr_unwitnessed;s.lifetime_losses=sr_lifetime_losses;s.bank_losses=sr_bank_losses;
 s.contract_faults=sr_contract_faults;s.first_reason=sr_first_reason;
 memcpy(s.draw,sr_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=sr_owned[i]!=0;s.shadowed_cells+=sr_owned[i]&&sr_shadows[i];}return s;
}
bool render_mirror_smallrocks_pre_draw(SmallRocksDraw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=10752||!native||bytes!=168||!sr_frame.active||sr_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=sr_frame.draw[sr_frame.slot];
 for(unsigned y=0;y<112;y++)memcpy(argb+y*96,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,96*sizeof *argb);
 for(unsigned y=0;y<14;y++)memcpy(native+y*12,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,12);
 return true;
}
unsigned render_mirror_smallrocks_callbacks(unsigned slot,SmallRocksWrite *out,size_t capacity)
{
 if(slot>=25||!out||capacity<sr_frame.draw[slot].callback_count)return 0;
 unsigned n=sr_frame.draw[slot].callback_count;memcpy(out,sr_frame.writes[slot],n*sizeof *out);return n;
}
bool render_mirror_smallrocks_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!sr_frame.accepted||fc.frame_active||fc.frame_failed||
 !sr_frame.contributed||!smallrocks_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,sr_owned,64000);memcpy(shadows,sr_shadows,64000);return true;
}
