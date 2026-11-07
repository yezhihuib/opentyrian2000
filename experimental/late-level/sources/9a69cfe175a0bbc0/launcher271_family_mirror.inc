/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private, independent exact1 default-OFF normal launcher271 + child463.
 * Consumes the production lineage value API; never creates or infers births.
 * Actual native draw hook supplies phase and origin. No gameplay/RNG writes.
 */
#include "launcher271_family_pins.inc"
static struct {bool valid;uint64_t frame;Launcher271Birth birth;
 unsigned cycle,gate,base;int x,y;Sprite2_array *bank;const Uint8 *data;size_t bytes;} lpf_seen[100];
static struct {bool loaded;uint64_t session;char root[1024];const struct JE_EventRecType *events;} lpf_life;
static struct {bool checked,valid;char root[1024];Asset member[4];} lpf_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,part,pixels,image;
 Launcher271Draw draw[100];Launcher271Write writes[100][672];} lpf_frame;
static uint8_t lpf_owned[64000],lpf_shadows[64000];
/* Parent native support is the full rectangle. Child native support is sparse;
 * authored alpha outside it receives only exact per-subpixel extra ownership. */
static uint8_t lpf_extra_owner[4096000],lpf_extra_cell[64000];
static uint64_t lpf_extra_retirements,lpf_phase_observations,lpf_shot_resumptions;
static uint64_t lpf_blend_retirements,lpf_normal_retirements,lpf_shadow_writes;
static uint64_t lpf_clipped,lpf_unwitnessed,lpf_lifetime_losses,lpf_bank_losses,lpf_contract_faults;
static unsigned lpf_first_reason;
static bool lpf_resources_current(void);
static bool lpf_extra(size_t n){return lpf_frame.contributed&&n<4096000&&lpf_extra_owner[n]!=0;}
static const char *lpf_root(void){const char *p=getenv("LAUNCHER271_FAMILY_ASSET_DIR");return p?p:"";}
static bool lpf_enabled(void)
{
 const char *a=getenv("LAUNCHER271_FAMILY_ENABLE"),*b=getenv("LAUNCHER271_LINEAGE_ENABLE"),*c=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&a&&!strcmp(a,"1")&&b&&!strcmp(b,"1")&&c&&!strcmp(c,"1");
}
static bool lpf_level_scope(void)
{
 return lpf_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static int lpf_image(unsigned b){for(unsigned i=0;i<4;i++)if(lpf_images[i].base==b)return (int)i;return -1;}
static bool lpf_events(void)
{
 static const int x[4]={42,66,234,258};
 if(!lpf_life.events||lpf_life.events!=eventRec||maxEvent!=731)return false;
 for(unsigned k=0;k<4;k++){
  const struct JE_EventRecType *r=eventRec+492+k;
  if(r->eventtime!=4920||r->eventtype!=6||r->eventdat!=271||r->eventdat2!=x[k]||
   r->eventdat3||r->eventdat4||r->eventdat5||r->eventdat6)return false;
 }
 return true;
}
static bool lpf_scope(void)
{
 if(!lpf_life.loaded||!lpf_level_scope()||terrain_file!='z'||!lpf_events()||strcmp(lpf_life.root,lpf_root()))return false;
 Launcher271Status s=launcher271_lineage_status();
 return s.enabled&&s.loaded&&!s.exhausted&&s.session==lpf_life.session;
}
static void lpf_fail(unsigned reason)
{
 if(!lpf_first_reason)lpf_first_reason=reason;
 lpf_frame.fault=true;lpf_frame.accepted=false;lpf_frame.active=lpf_frame.pending=false;
 if(lpf_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
static void lpf_reset(void)
{
 if(!lpf_life.loaded&&!lpf_frame.contributed&&!lpf_frame.pending)return;
 if(lpf_frame.contributed||lpf_frame.pending)lpf_fail(2);
 memset(lpf_seen,0,sizeof lpf_seen);
}
static void lpf_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 lpf_reset();lpf_life.loaded=false;
 if(!lpf_level_scope())return; /* OFF does not query lineage, scan, hash or load assets. */
 lpf_life.events=events;Launcher271Status s=launcher271_lineage_status();
 if(map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||!lpf_events()||
 !s.enabled||!s.loaded||s.exhausted||!lpf_root()[0]||strlen(lpf_root())>=sizeof lpf_life.root)return;
 lpf_life.session=s.session;strcpy(lpf_life.root,lpf_root());lpf_life.loaded=true;
}
/* Only mapper-authorized normal record fields. No damaged-source decoding. */
static bool lpf_record(unsigned r)
{
 if(r!=271&&r!=463)return false;
 bool child=r==463;static const unsigned sequence[2][20]={{275,277,279,277,275},{191}};
 if(enemyDat[r].ani!=(child?1:5)||enemyDat[r].esize!=1||enemyDat[r].animate!=(child?0:2)||
 enemyDat[r].shapebank!=8||enemyDat[r].xmove||enemyDat[r].ymove!=(child?4:0)||
 enemyDat[r].xaccel||enemyDat[r].yaccel||enemyDat[r].xcaccel||enemyDat[r].ycaccel||
 enemyDat[r].startx||enemyDat[r].starty||enemyDat[r].startxc||enemyDat[r].startyc||
 enemyDat[r].xrev||enemyDat[r].yrev||enemyDat[r].elaunchfreq!=(child?0:40)||
 enemyDat[r].elaunchtype!=(child?0:463))return false;
 for(unsigned j=0;j<3;j++)if(enemyDat[r].tur[j]||enemyDat[r].freq[j])return false;
 for(unsigned j=0;j<20;j++)if(enemyDat[r].egraphic[j]!=sequence[child][j])return false;
 return true;
}
static bool lpf_shape(unsigned slot)
{
 if(slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;unsigned r=e->enemytype;
 bool child=r==463;
 if(!lpf_record(r)||(child?(slot<75||slot>=100):(slot<25||slot>=50))||
 enemyAvail[slot]==1||e->enemydatofs!=enemyDat+r||e->sprite2s!=enemySpriteSheets||
 enemySpriteSheetIds[0]!=8||e->sprite2s==&spriteSheet8||!e->sprite2s->data||
 e->sprite2s->data==spriteSheet8.data||e->sprite2s->size!=42012||
 asteroid1_stamp(e->sprite2s->data,e->sprite2s->size)!=UINT64_C(0x913975450e0fc00d)||
 e->size!=1||e->filter||e->edamaged||e->scoreitem||e->special||e->iced||
 e->exc||e->eyc!=(child?4:0)||e->excc||e->eycc||e->xaccel||e->yaccel||e->fixedmovey||
 e->linknum||e->launchspecial||e->launchfreq!=(child?0:40)||e->launchtype!=(child?0:463)||
 e->ani!=(child?1:5)||e->animin!=1||e->animax!=(child?0:5)||e->aniwhenfire!=(child?0:2)||
 (child?(e->enemycycle!=1||e->aniactive):(e->enemycycle<1||e->enemycycle>5||(e->aniactive!=1&&e->aniactive!=2))))return false;
 for(unsigned k=1;k<4;k++)if(enemySpriteSheetIds[k]==8)return false;
 for(unsigned j=0;j<3;j++)if(e->tur[j]||e->freq[j])return false;
 for(unsigned j=0;j<20;j++)if(e->egr[j]!=enemyDat[r].egraphic[j])return false;
 return true;
}
static bool lpf_colors(void)
{ for(unsigned i=0;i<COUNTOF(lpf_palette);i++)if((rgb_palette[lpf_palette[i].index]&0xffffffu)!=lpf_palette[i].rgb)return false;return true; }
static bool lpf_birth_valid(const Launcher271Receipt *r,unsigned s)
{
 const Launcher271Birth *b=&r->birth;
 return r->present&&r->current&&b->session==lpf_life.session&&b->token&&b->generation&&b->slot==s&&
 b->event>=493&&b->event<=496&&b->bank==8&&!b->physical_bank&&!b->unique_shape&&
 b->allocation_result==(int)s+1&&b->record==enemy[s].enemytype&&
 (b->record==271?(s>=25&&s<50&&b->parent_slot==100&&!b->parent_token):
 (b->record==463&&s>=75&&s<100&&b->parent_slot>=25&&b->parent_slot<50&&b->parent_token&&b->parent_generation));
}
static bool lpf_witness(unsigned s)
{
 if(s>=100||!lpf_seen[s].valid)return false;
 Launcher271Receipt r=launcher271_lineage_receipt(s);const Launcher271Birth *b=&lpf_seen[s].birth;
 return lpf_birth_valid(&r,s)&&r.birth.token==b->token&&r.birth.generation==b->generation&&
 r.birth.resource_epoch==b->resource_epoch&&r.birth.event==b->event&&r.birth.record==b->record&&
 r.birth.parent_token==b->parent_token&&r.birth.parent_generation==b->parent_generation&&
 r.birth.parent_slot==b->parent_slot&&enemy[s].sprite2s==lpf_seen[s].bank&&
 enemy[s].sprite2s->data==lpf_seen[s].data&&enemy[s].sprite2s->size==lpf_seen[s].bytes;
}
/* This hook is already immediately AFTER native animate2/animate0 handling
 * and BEFORE the original four blits. It captures values, not a clock or loop.
 * Consequently waiting1, first277,279,277,275/wait5, later275... and a same-
 * iteration newly allocated child's unmoved191 follow actual native writes. */
static void lpf_enemy_animated(unsigned slot)
{
 if(!lpf_life.loaded||slot>=100||(enemy[slot].enemytype!=271&&enemy[slot].enemytype!=463))return;
 if(!lpf_scope()||!lpf_shape(slot)||enemy[slot].ex+tempMapXOfs<=-29||enemy[slot].ex+tempMapXOfs>=300)return;
 Launcher271Receipt r=launcher271_lineage_receipt(slot);if(!lpf_birth_valid(&r,slot)){++lpf_unwitnessed;return;}
 if(lpf_seen[slot].valid&&lpf_seen[slot].frame==fc_frame){lpf_fail(3);return;}
 lpf_seen[slot].valid=true;lpf_seen[slot].frame=fc_frame;lpf_seen[slot].birth=r.birth;
 lpf_seen[slot].cycle=enemy[slot].enemycycle;lpf_seen[slot].gate=enemy[slot].aniactive;
 lpf_seen[slot].base=enemy[slot].egr[enemy[slot].enemycycle-1];
 lpf_seen[slot].x=enemy[slot].ex+enemy[slot].mapoffset-6;lpf_seen[slot].y=enemy[slot].ey-7;
 lpf_seen[slot].bank=enemy[slot].sprite2s;lpf_seen[slot].data=enemy[slot].sprite2s->data;
 lpf_seen[slot].bytes=enemy[slot].sprite2s->size;++lpf_phase_observations;
}
static void lpf_tick(void)
{
 if(!lpf_life.loaded&&!lpf_frame.contributed&&!lpf_frame.pending)return;
 if(lpf_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&lpf_frame,0,sizeof lpf_frame);memset(lpf_seen,0,sizeof lpf_seen);
 memset(lpf_owned,0,sizeof lpf_owned);memset(lpf_shadows,0,sizeof lpf_shadows);
 memset(lpf_extra_owner,0,sizeof lpf_extra_owner);memset(lpf_extra_cell,0,sizeof lpf_extra_cell);lpf_first_reason=0;
 if(!lpf_scope()){lpf_life.loaded=false;return;}
}
static bool lpf_load(unsigned image)
{
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-newshd-%u-8.hda",lpf_resources.root,lpf_images[image].base);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==lpf_images[image].id&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==lpf_images[image].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 lpf_resources.member[image]=(Asset){true,true,ASSET_ASTEROID1,lpf_images[image].base,24,28,0,0,8,rgba};return true;
}
static bool lpf_resources_current(void)
{
 if(!lpf_resources.checked||!lpf_resources.valid||strcmp(lpf_resources.root,lpf_root()))return false;
 for(unsigned image=0;image<4;image++){
 const Asset *a=lpf_resources.member+image;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)lpf_images[image].base||a->w!=24||a->h!=28||
 a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||asteroid1_stamp(a->rgba,172032)!=lpf_images[image].rgba)return false;
 }
 return true;
}
static bool lpf_ready(void)
{
 if(!lpf_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!lpf_resources.checked){lpf_resources.checked=true;strcpy(lpf_resources.root,lpf_life.root);lpf_resources.valid=true;for(unsigned i=0;i<4;i++)if(!lpf_load(i))lpf_resources.valid=false;}
 if(!lpf_resources_current()){lpf_resources.valid=false;return false;}
 return true;
}
static void lpf_shutdown(void)
{
 lpf_reset();lpf_life.loaded=false;for(unsigned i=0;i<4;i++)free(lpf_resources.member[i].rgba);memset(&lpf_resources,0,sizeof lpf_resources);
}
static bool lpf_dependencies(bool partial)
{
 if(!lpf_frame.contributed)return true;
 if(lpf_frame.fault||!lpf_scope()||!lpf_colors()||!lpf_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned s=0;s<100;s++)if(lpf_frame.draw[s].token){const Launcher271Draw *d=lpf_frame.draw+s;
  if(!lpf_witness(s)||!lpf_shape(s)||d->frame!=fc_frame||d->generation!=lpf_seen[s].birth.generation||
  d->token!=lpf_seen[s].birth.token||d->epoch!=lpf_life.session||d->event!=lpf_seen[s].birth.event||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data||
  d->record!=lpf_seen[s].birth.record||lpf_image(d->base)<0||d->cycle!=lpf_seen[s].cycle||
  d->draw_gate!=lpf_seen[s].gate||d->base!=lpf_seen[s].base)return false;
  /* The draw snapshot is immutable. Native movement and the launch-triggered
   * gate change occur AFTER the draw and must not invalidate this receipt. */
  if(!d->complete){if(!partial||!lpf_frame.pending||lpf_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->callback_count!=lpf_totals[lpf_image(d->base)]||
    (!partial&&d->extra_stores!=lpf_images[lpf_image(d->base)].extra))return false;
 }
 return partial||(!lpf_frame.active&&!lpf_frame.pending);
}
/* Pure predicate shared by diagnostic snapshots. */
static bool lpf_finish(void){return lpf_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool lpf_guard(void)
{
 if(lpf_finish())return true;
 lpf_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool lpf_before_tile(unsigned slot,int part)
{
 if(lpf_frame.contributed&&!lpf_dependencies(true)){lpf_fail(5);return false;}
 if(lpf_frame.pending&&(lpf_frame.active||slot!=lpf_frame.slot||
 lpf_frame.draw[slot].next>=4||part!=(int)lpf_parts[lpf_frame.draw[slot].next])){lpf_fail(6);return false;}
 return true;
}
static bool lpf_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool lpf_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!lpf_life.loaded||slot>=100||(enemy[slot].enemytype!=271&&enemy[slot].enemytype!=463))return false;
 if(!fc.frame_active||fc.frame_failed||!lpf_witness(slot)){++lpf_unwitnessed;return false;}
 unsigned k;for(k=0;k<4&&part!=(int)lpf_parts[k];k++);
 if(k==4){if(lpf_frame.contributed)lpf_fail(7);return false;}
 int64_t ox=(int64_t)x-lpf_px[k],oy=(int64_t)y-lpf_py[k];
 Launcher271Draw *d=lpf_frame.draw+slot;
 if(!lpf_geometry(ox,oy)){++lpf_clipped;if(d->token)lpf_fail(8);return false;}
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter||
 !lpf_scope()||sheet!=enemy[slot].sprite2s||!lpf_shape(slot)||lpf_seen[slot].frame!=fc_frame||base!=lpf_seen[slot].base||
 enemy[slot].enemycycle!=lpf_seen[slot].cycle||enemy[slot].aniactive!=lpf_seen[slot].gate||
 ox!=lpf_seen[slot].x||oy!=lpf_seen[slot].y||lpf_image(base)<0||!lpf_colors()||!lpf_ready()){
  if(d->token||lpf_frame.contributed)lpf_fail(9);
  return false;
 }
 if(k==0){if(d->token||lpf_frame.pending){lpf_fail(10);return false;}}
 else if(!lpf_frame.pending||lpf_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||lpf_frame.pending)lpf_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||lpf_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++lpf_contract_faults;lpf_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++lpf_contract_faults;lpf_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  *d=(Launcher271Draw){.frame=fc_frame,.epoch=lpf_life.session,.token=lpf_seen[slot].birth.token,
   .generation=lpf_seen[slot].birth.generation,.slot=slot,.event=lpf_seen[slot].birth.event,.record=lpf_seen[slot].birth.record,.cycle=enemy[slot].enemycycle,.draw_gate=enemy[slot].aniactive,
   .base=base,.cur_loc=curLoc,.bank_role=8,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  lpf_frame.pending=true;lpf_frame.slot=slot;lpf_frame.image=(unsigned)lpf_image(base);
 }
 d->part_order[k]=(unsigned)part;
 lpf_frame.part=k;lpf_frame.pixels=0;lpf_frame.active=true;lpf_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool lpf_retire(unsigned off,int style)
{
 if(!lpf_frame.contributed)return false;
 bool owned=off<64000&&lpf_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++lpf_blend_retirements;else ++lpf_normal_retirements;
 lpf_owned[off]=lpf_shadows[off]=0;}
 if(off<64000&&style!=MIRROR_SHADOW&&lpf_extra_cell[off]){
  unsigned x=off%320,y=off/320;
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
   size_t n=(y*8+sy)*2560+x*8+sx;lpf_extra_retirements+=lpf_extra_owner[n]!=0;lpf_extra_owner[n]=0;
  }
  lpf_extra_cell[off]=0;
 }
 return owned;
}
static bool lpf_pixel(unsigned x,unsigned y,int style)
{
 if(!lpf_frame.active){if(lpf_frame.pending){lpf_fail(14);return true;}return false;}
 Launcher271Draw *d=lpf_frame.draw+lpf_frame.slot;
 unsigned k=lpf_frame.part;
 if(k>=4||lpf_frame.pixels>=lpf_counts[lpf_frame.image][k]){++lpf_contract_faults;lpf_fail(15);return true;}
 const Launcher271Write *w=lpf_native[lpf_frame.image][k]+lpf_frame.pixels;
 unsigned lx=lpf_px[k]+w->x,ly=lpf_py[k]+w->y;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=w->index||expected[y*320+x]!=w->index){
 ++lpf_contract_faults;lpf_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=&lpf_resources.member[lpf_frame.image];
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  /* Actual current canvas underlay. Alpha0 retains RGB but gains native
   * ownership; native holes never call here and remain entirely untouched. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 lpf_owned[off]=(uint8_t)(lpf_frame.slot+1);lpf_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=672){lpf_fail(17);return true;}
 lpf_frame.writes[lpf_frame.slot][d->callback_count++]=(Launcher271Write){(uint8_t)lx,(uint8_t)ly,w->index};
 ++lpf_frame.pixels;d->part_count[k]=lpf_frame.pixels;return true;
}
static void lpf_shadow(unsigned off)
{
 if(off<64000&&lpf_owned[off]){if(lpf_shadows[off]<255)++lpf_shadows[off];++lpf_shadow_writes;}
}
/* Same narrow authored-support policy as firing_rock462: exact nonzero-alpha
 * native-hole subpixels only, after a complete observed native quartet. No
 * native INDEX, selected[], native owner, global permission or cached underlay. */
static void lpf_authored_support(Launcher271Draw *d)
{
 
 const Asset *a=lpf_resources.member+lpf_frame.image;
 for(unsigned i=0;i<lpf_images[lpf_frame.image].extra;i++){
  unsigned ax=lpf_extras[lpf_frame.image][i].x,ay=lpf_extras[lpf_frame.image][i].y;
  const Uint8 *art=a->rgba+(ay*192+ax)*4;
  unsigned off=((unsigned)d->y+ay/8)*320+(unsigned)d->x+ax/8;
  if(lpf_native_mask[lpf_frame.image][(ay/8)*24+ax/8]||!art[3]||expected[off]!=((const Uint8 *)fc_source_pixels)[off]){
   lpf_fail(21);family_fault(FC_ORDER);return;
  }
  size_t n=((unsigned)d->y*8+ay)*2560+(unsigned)d->x*8+ax;
  Uint32 *dst=(Uint32 *)canvas->pixels+n;*dst=blend_rgba(*dst,art,art[3]);
  lpf_extra_owner[n]=(uint8_t)(d->slot+1);lpf_extra_cell[off]=1;++d->extra_stores;
 }
 if(d->extra_stores!=lpf_images[lpf_frame.image].extra){lpf_fail(21);family_fault(FC_ORDER);}
}
static void lpf_end(void)
{
 if(!lpf_frame.active)return;
 unsigned k=lpf_frame.part;Launcher271Draw *d=lpf_frame.draw+lpf_frame.slot;
 if(k>=4||d->next!=k||d->mask!=(1u<<k)-1||lpf_frame.pixels!=lpf_counts[lpf_frame.image][k]||!b313_family_writer_draw_ready(fc_frame)){
 ++lpf_contract_faults;lpf_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;lpf_frame.active=false;
 if(k==3){
  d->complete=d->mask==15&&d->callback_count==lpf_totals[lpf_frame.image];lpf_frame.pending=false;
  if(!d->complete){lpf_fail(19);return;}
  if(!lpf_dependencies(true)||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){
   lpf_fail(22);family_fault(FC_SOURCE);return;
  }
  lpf_authored_support(d);
 }
}
static void lpf_accept(void){lpf_frame.accepted=fc.ready&&!fc.frame_failed&&lpf_finish();}
Launcher271FamilyStatus render_mirror_launcher271_family_status(void)
{
 Launcher271FamilyStatus s={0};s.requested=lpf_enabled();s.loaded=lpf_life.loaded;s.contributed=lpf_frame.contributed;
 s.failed=fc.frame_failed||lpf_frame.fault;s.accepted=lpf_frame.accepted;s.frame=fc_frame;
 s.active=lpf_frame.active;s.pending=lpf_frame.pending;s.active_slot=lpf_frame.slot;
 s.active_part=lpf_frame.part<4?lpf_parts[lpf_frame.part]:UINT_MAX;s.consumed_events=launcher271_lineage_status().event_consumed;
 s.blend_retirements=lpf_blend_retirements;s.normal_retirements=lpf_normal_retirements;s.shadow_writes=lpf_shadow_writes;
 s.clipped=lpf_clipped;s.unwitnessed=lpf_unwitnessed;s.lifetime_losses=lpf_lifetime_losses;s.bank_losses=lpf_bank_losses;
 s.contract_faults=lpf_contract_faults;s.first_reason=lpf_first_reason;
 s.phase_observations=lpf_phase_observations;s.shot_resumptions=lpf_shot_resumptions;s.extra_retirements=lpf_extra_retirements;
 for(unsigned i=0;i<4096000;i++)s.extra_pixels+=lpf_extra_owner[i]!=0;
 for(unsigned i=0;i<100;i++)s.births[i]=launcher271_lineage_receipt(i).birth;
 memcpy(s.draw,lpf_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=lpf_owned[i]!=0;s.shadowed_cells+=lpf_owned[i]&&lpf_shadows[i];}return s;
}
bool render_mirror_launcher271_pre_draw(Launcher271Draw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!lpf_frame.active||lpf_frame.part||lpf_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=lpf_frame.draw[lpf_frame.slot];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_launcher271_pre_part(Launcher271Draw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!lpf_frame.active||lpf_frame.pixels||
 lpf_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=lpf_frame.draw[lpf_frame.slot];unsigned k=lpf_frame.part;*part=lpf_parts[k];
 unsigned x=(unsigned)d->x+lpf_px[k],y=(unsigned)d->y+lpf_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_launcher271_callbacks(unsigned slot,Launcher271Write *out,size_t capacity)
{
 if(slot>=100||!out||capacity<lpf_frame.draw[slot].callback_count)return 0;
 unsigned n=lpf_frame.draw[slot].callback_count;memcpy(out,lpf_frame.writes[slot],n*sizeof *out);return n;
}
bool render_mirror_launcher271_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!lpf_frame.accepted||fc.frame_active||fc.frame_failed||
 !lpf_frame.contributed||!lpf_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,lpf_owned,64000);memcpy(shadows,lpf_shadows,64000);return true;
}
bool render_mirror_launcher271_extra_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=4096000||!lpf_frame.accepted||fc.frame_active||fc.frame_failed||
 !lpf_frame.contributed||!lpf_finish()||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
 !b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(out,lpf_extra_owner,bytes);return true;
}
