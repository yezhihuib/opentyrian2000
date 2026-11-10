/* SPDX-License-Identifier: GPL-2.0-or-later
 * Independent same-frame normal tank194 patches. No rejected scene pixels,
 * legacy draw/cache permission, historical pixels or recursive actor underlay.
 */
enum {KF_CONTEXT=1,KF_PHASE=2,KF_IDENTITY=3,KF_GEOMETRY=4,KF_ART=5,
 KF_ORDER=6,KF_WRITE=7,KF_END=8,KF_FINAL=9,KF_PRESENT=10,KF_SHARED=11};
typedef struct {
 bool seen,valid,active,complete,ready;
 Tank194Draw draw,origin;
 unsigned part,pixels,reason;
 uint64_t patch_stamp,mask_stamp,origin_stamp,draw_stamp;
 Uint8 native[672],mask[672];
 Uint32 patch[43008];
} KfDraw;
static struct {
 bool enabled,valid,phase_seen,phase_open,phase_closed;
 uint64_t frame,session,generation;
 uint32_t presenting_slots;
 KfDraw draw[25];
} kf;
/* Lifetime denial deliberately survives frame/reset/release/renderer changes.
 * Only a different fully verified birth identity can replace this receipt. */
static struct {bool valid;uint64_t epoch,generation,token,closed_epoch;} kf_denied[25];
static struct {bool checked,valid;char root[1024];Uint8 *rgba[8];const Uint8 *identity[8];} kf_art;
static B313TankFallbackStatus kf_status;
static bool kf_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *v=getenv("BUILDING313_TANK_FALLBACK_ENABLE");
 return v&&!strcmp(v,"1")&&tf_requested()&&t194_enabled();
#else
 return false;
#endif
}
static unsigned kf_cells(const KfDraw *d)
{unsigned n=0;for(unsigned i=0;i<672;i++)n+=d->mask[i]!=0;return n;}
static void kf_fail_slot(unsigned slot,unsigned reason)
{
 if(slot<75||slot>=100)return;
 KfDraw *d=kf.draw+slot-75;
 d->seen=true;
 if(!d->reason){++kf_status.rejected;if(!kf_status.first_reason)kf_status.first_reason=reason;d->reason=reason;}
 d->valid=d->active=d->ready=false;
 memset(d->mask,0,sizeof d->mask);
 kf.presenting_slots&=~(UINT32_C(1)<<(slot-75));
}
static void kf_shared_fail(void)
{
 if(!kf.enabled)return;
 kf.valid=false;kf.phase_open=false;kf.presenting_slots=0;
 for(unsigned i=0;i<25;i++)if(kf.draw[i].seen)kf_fail_slot(i+75,KF_SHARED);
}
static void kf_reset(void){memset(&kf,0,sizeof kf);}
static void kf_begin(void)
{
 kf_reset();
 if(!kf_requested()||!tf_geometry())return;
 kf.enabled=kf.valid=true;kf.frame=fc_frame;kf.session=fc_session;kf.generation=fc_generation;
 ++kf_status.frames;
}
static bool kf_context(void)
{
 return kf.enabled&&kf.valid&&kf_requested()&&tf_geometry()&&
  kf.frame==fc_frame&&kf.session==fc_session&&kf.generation==fc_generation;
}
static bool kf_denial_matches(unsigned slot)
{
 const unsigned i=slot-75;
 /* Keep the high-water even after a verified replacement makes valid=false.
  * Returning to an older receipt can never resurrect that denied lifetime. */
 return (kf_denied[i].epoch||kf_denied[i].generation||kf_denied[i].token)&&
  ((kf_denied[i].closed_epoch&&t194_slots[slot].birth.epoch<=kf_denied[i].closed_epoch)||
   t194_slots[slot].birth.epoch<kf_denied[i].epoch||
   t194_slots[slot].generation<=kf_denied[i].generation||t194_slots[slot].birth.token<=kf_denied[i].token);
}
static bool kf_known_birth(unsigned slot)
{
 /* Negative-only evidence. No particular identity field must survive for us
  * to notice a broken existing witness. Ordinary allocations alone are not
  * tank births; their generation counter does not select this observer. */
 return t194_slots[slot].witness||t194_slots[slot].live||t194_slots[slot].initialized||
  t194_slots[slot].birth.live||t194_slots[slot].birth.initialized||
  t194_slots[slot].birth.epoch||t194_slots[slot].birth.generation||t194_slots[slot].birth.token;
}
static void kf_deny(unsigned slot)
{
 const unsigned i=slot-75;
 const KfDraw *d=kf.draw+i;const Tank194Draw *draw=&d->origin;
 uint64_t epoch=0,generation=0,token=0;
 if(draw->token&&draw->epoch&&draw->generation&&
    d->origin_stamp==asteroid1_stamp((const Uint8 *)draw,sizeof *draw)){
  epoch=draw->epoch;generation=draw->generation;token=draw->token;
 }else{
  /* A witnessed birth may have lost one identity field before its first
   * body. Preserve remaining denial axes; an absent token is never promoted
   * into a valid receipt. Restoring that same generation cannot re-admit it. */
  epoch=t194_slots[slot].birth.epoch;generation=t194_slots[slot].generation;
  if(t194_slots[slot].birth.generation>generation)generation=t194_slots[slot].birth.generation;
  if(t194_slots[slot].witness>generation)generation=t194_slots[slot].witness;
  token=t194_slots[slot].birth.token;
 }
 if(epoch||generation||token){
  /* Malformed, stale or partially rolled-back observations may tighten but
   * must never weaken any component of an established lifetime denial. */
  if(epoch>kf_denied[i].epoch)kf_denied[i].epoch=epoch;
  if(generation>kf_denied[i].generation)kf_denied[i].generation=generation;
  if(token>kf_denied[i].token)kf_denied[i].token=token;
  /* With only an epoch left, a different birth inside that same epoch cannot
   * be distinguished from restoration. Refuse it until a verified new epoch;
   * this negative-only fence never supplies missing identity permission. */
  if(epoch&&!generation&&!token&&epoch>kf_denied[i].closed_epoch)kf_denied[i].closed_epoch=epoch;
  kf_denied[i].valid=true;
 }
 kf_fail_slot(slot,KF_IDENTITY);
}
static bool kf_lifetime(unsigned slot)
{
 if(slot<75||slot>=100||!t194_scope()||!t194_witness(slot)||!t194_shape(slot,0))return false;
 const Tank194Birth *b=&t194_slots[slot].birth;
 return b->live&&b->initialized&&b->slot==slot&&b->record==194&&b->epoch&&b->epoch==t194_life.epoch&&
  b->token&&b->generation&&b->generation==t194_slots[slot].generation&&b->bank_role==20&&b->bank_bytes==46204&&
  b->bank_object==(uintptr_t)enemy[slot].sprite2s&&b->bank_data==(uintptr_t)enemy[slot].sprite2s->data;
}
static bool kf_terrain_current(void)
{
 return tf.captured&&tf.terrain&&tf.terrain==tf.terrain_surface&&family_rgb(tf.terrain)&&
  tf.terrain->pixels==tf.terrain_pixels&&tf.terrain->format==tf.terrain_format&&tf_ground_current();
}
static bool kf_art_current(void)
{
 if(!kf_art.checked||!kf_art.valid||strcmp(kf_art.root,t194_root()))return false;
 for(unsigned p=0;p<8;p++)if(!kf_art.rgba[p]||kf_art.rgba[p]!=kf_art.identity[p]||
  asteroid1_stamp(kf_art.rgba[p],172032)!=t194_art_stamp[p])return false;
 return true;
}
static bool kf_load(void)
{
 if(kf_art.checked)return kf_art_current();
 kf_art.checked=true;
 if(!t194_root()[0]||strlen(t194_root())>=sizeof kf_art.root)return false;
 strcpy(kf_art.root,t194_root());bool all=true;
 for(unsigned p=0;p<8&&all;p++){
  char path[1200];Uint8 header[28],extra;REAR_STAT st;
  int n=snprintf(path,sizeof path,"%s/enemy-newsh2-%u-8.hda",kf_art.root,t194_art[p]);
  if(n<0||(size_t)n>=sizeof path){all=false;break;}
  int fd=REAR_OPEN(path);if(fd<0){all=false;break;}
  bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==172060&&
   REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
  uint32_t v[6]={0};const uint32_t wanted[6]={1010000+t194_art[p],8,24,28,6,7};
  if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
   for(unsigned i=0;i<6;i++)if(v[i]!=wanted[i])ok=false;}
  if(ok){kf_art.rgba[p]=malloc(172032);ok=kf_art.rgba[p]!=NULL;}
  if(ok)ok=REAR_READ(fd,kf_art.rgba[p],172032)==172032&&REAR_READ(fd,&extra,1)==0&&
   asteroid1_stamp(kf_art.rgba[p],172032)==t194_art_stamp[p];
  if(REAR_CLOSE(fd))ok=false;
  if(ok)kf_art.identity[p]=kf_art.rgba[p];
  all=ok;
 }
 if(!all)for(unsigned p=0;p<8;p++){free(kf_art.rgba[p]);kf_art.rgba[p]=NULL;}
 kf_art.valid=all;return kf_art_current();
}
static bool kf_actor_current(const KfDraw *d)
{
 const Tank194Draw *v=&d->draw;unsigned s=v->slot;
 if(!d->valid||!v->token||!kf_lifetime(s)||kf_denial_matches(s)||
  v->pose>=8||v->base!=t194_bases[v->pose]||v->pose+1!=enemy[s].enemycycle)return false;
 return v->epoch==t194_life.epoch&&v->token==t194_slots[s].birth.token&&
  v->generation==t194_slots[s].generation&&v->event==t194_slots[s].birth.event&&
  v->script_serial==t194_slots[s].script_serial&&v->script_event==t194_slots[s].script_event&&
  v->bank_object==(uintptr_t)enemy[s].sprite2s&&v->bank_data==(uintptr_t)enemy[s].sprite2s->data&&
  v->bank_bytes==enemy[s].sprite2s->size;
}
static bool kf_metadata_current(const KfDraw *d)
{
 const Tank194Draw *v=&d->draw,*b=&d->origin;
 return d->origin_stamp==asteroid1_stamp((const Uint8 *)b,sizeof *b)&&t194_geometry(v->x,v->y)&&
  v->frame==b->frame&&v->epoch==b->epoch&&v->token==b->token&&v->generation==b->generation&&
  v->script_serial==b->script_serial&&v->slot==b->slot&&v->event==b->event&&v->record==b->record&&
  v->base==b->base&&v->pose==b->pose&&v->cur_loc==b->cur_loc&&v->bank_role==b->bank_role&&
  v->bank_bytes==b->bank_bytes&&v->script_event==b->script_event&&v->bank_object==b->bank_object&&
  v->bank_data==b->bank_data&&v->x==b->x&&v->y==b->y;
}
static bool kf_identity(const KfDraw *d)
{return kf_context()&&d->draw.frame==kf.frame&&t194_colors()&&kf_metadata_current(d)&&kf_actor_current(d);}
/* These phase hooks bracket only the genuine ground-pool JE_drawEnemy(100).
 * No dispatcher request or building observer can manufacture this authority. */
void render_mirror_tank_fallback_phase_begin(void)
{
 if(!kf.enabled)return;
 if(kf.phase_seen||!kf_context()||!fc.frame_active||!kf_terrain_current()||
    !b313_family_writer_draw_ready(kf.frame)){kf_shared_fail();return;}
 kf.phase_seen=kf.phase_open=true;
}
void render_mirror_tank_fallback_phase_end(void)
{
 if(!kf.enabled)return;
 if(!kf.phase_open){kf_shared_fail();return;}
 for(unsigned i=0;i<25;i++)if(kf.draw[i].valid&&!kf.draw[i].complete)kf_fail_slot(i+75,KF_END);
 kf.phase_open=false;kf.phase_closed=true;
}
/* Called only immediately before the original blit_enemy native tile, before
 * the old family dispatcher may return because its scene already failed. */
void render_mirror_tank_fallback_tile_begin(SDL_Surface *surface,unsigned slot,int x,int y,
 Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!kf.enabled)return;
 unsigned k;for(k=0;k<4&&part!=(int)t194_parts[k];k++);
 for(unsigned i=0;i<25;i++)if(kf.draw[i].valid&&!kf.draw[i].complete){
  KfDraw *p=kf.draw+i;
  if(p->active||slot!=i+75||k!=p->draw.next)kf_fail_slot(i+75,KF_ORDER);
 }
 if(slot<75||slot>=100)return;
 KfDraw *d=kf.draw+slot-75;
 bool witnessed=d->origin.token||kf_known_birth(slot);
 if(!witnessed&&enemy[slot].enemytype!=194)return;
 /* Genuine semantic observations outlive a local frame rejection. In
  * particular native filter clearing or a temporary type change must not
  * erase evidence just because an earlier part/order/material already failed. */
 if(!kf_lifetime(slot)||k==4){kf_deny(slot);return;}
 int64_t ox=(int64_t)x-t194_px[k],oy=(int64_t)y-t194_py[k];
 if(filter||sheet!=enemy[slot].sprite2s||!sheet||!t194_source(sheet)||
    base!=t194_bases[enemy[slot].enemycycle-1]||
    ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7){kf_deny(slot);return;}
 if(d->seen&&!d->valid)return;
 d->seen=true;
 if(!kf_context()||!kf.phase_open||kf.phase_closed||!fc.frame_active){kf_fail_slot(slot,KF_PHASE);return;}
 if(kf_denial_matches(slot)){
  kf_fail_slot(slot,KF_IDENTITY);return;
 }
 /* Replacing an old denial requires an actual new fully verified identity,
  * not a counter/pointer change, a frame reset or renderer reconstruction. */
 kf_denied[slot-75].valid=false;
 if(!t194_geometry(ox,oy)){kf_fail_slot(slot,KF_GEOMETRY);return;}
 if(d->complete||(k==0&&d->draw.token)||(k!=0&&(!d->valid||!d->draw.token||d->draw.next!=k||d->draw.x!=ox||d->draw.y!=oy))){kf_fail_slot(slot,KF_ORDER);return;}
 if(pf.active||surface!=fc_source||surface!=game_screen||surface!=VGAScreen||!t194_colors()||
    !b313_family_writer_draw_ready(kf.frame)||!kf_terrain_current()||memcmp(tf.expected,fc_source_pixels,64000)){
  kf_fail_slot(slot,KF_CONTEXT);return;
 }
 if(!kf_load()){kf_fail_slot(slot,KF_ART);return;}
 if(k==0){
  d->valid=true;
  d->draw=(Tank194Draw){.frame=kf.frame,.epoch=t194_life.epoch,.token=t194_slots[slot].birth.token,
   .generation=t194_slots[slot].generation,.slot=slot,.event=t194_slots[slot].birth.event,.record=194,
   .base=base,.pose=enemy[slot].enemycycle-1,.script_serial=t194_slots[slot].script_serial,
   .script_event=t194_slots[slot].script_event,.cur_loc=curLoc,.bank_role=20,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  d->origin=d->draw;d->origin_stamp=asteroid1_stamp((const Uint8 *)&d->origin,sizeof d->origin);
  for(unsigned ly=0;ly<28;ly++)for(unsigned lx=0;lx<24;lx++){
   unsigned off=((unsigned)oy+ly)*320+(unsigned)ox+lx;
   d->native[ly*24+lx]=tf.expected[off];
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    unsigned n=(ly*8+sy)*192+lx*8+sx;
    d->patch[n]=tf.mask[off]?((const Uint32 *)tf.terrain->pixels)[((unsigned)oy*8+ly*8+sy)*2560+(unsigned)ox*8+lx*8+sx]:palette_rgb(tf.expected[off]);
   }
  }
  ++kf_status.draws;
 }else if(!kf_identity(d)){kf_deny(slot);return;}
 d->part=k;d->pixels=0;d->draw.part_order[k]=(unsigned)part;d->active=true;
}
static void kf_pixel(unsigned off,int style)
{
 if(!kf.enabled)return;
 if(!kf_context()||off>=64000){kf_shared_fail();return;}
 unsigned x=off%320,y=off/320;
 /* Retire EVERY prior tank before any acquisition, including same-value
  * stores and failed/foreign actors. Never restore a superseded owner. */
 for(unsigned i=0;i<25;i++){
  KfDraw *d=kf.draw+i;
  if(!d->valid)continue;
  const Tank194Draw *v=&d->draw;
  if((int)x>=v->x&&(int)x<v->x+24&&(int)y>=v->y&&(int)y<v->y+28){
   unsigned n=(y-(unsigned)v->y)*24+x-(unsigned)v->x;
   if(d->mask[n]){d->mask[n]=0;++kf_status.retired;}
  }
 }
 for(unsigned i=0;i<25;i++){
  KfDraw *d=kf.draw+i;
  if(!d->valid||d->complete)continue;
  if(pf.active){kf_fail_slot(i+75,KF_ORDER);continue;}
  if(!d->active){kf_fail_slot(i+75,KF_ORDER);continue;}
  Tank194Draw *v=&d->draw;unsigned k=d->part;
  if(!kf.phase_open||k>=4||v->pose>=8||d->pixels>=t194_counts[v->pose][k]){kf_fail_slot(i+75,KF_WRITE);continue;}
  const Tank194Write *w=t194_native[v->pose][k]+d->pixels;
  unsigned lx=t194_px[k]+w->x,ly=t194_py[k]+w->y;
  if(style!=MIRROR_NORMAL||x!=(unsigned)v->x+lx||y!=(unsigned)v->y+ly||
     ((const Uint8 *)fc_source_pixels)[off]!=w->index||tf.expected[off]!=d->native[ly*24+lx]){
   kf_fail_slot(i+75,KF_WRITE);continue;
  }
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
   unsigned n=(ly*8+sy)*192+lx*8+sx;const Uint8 *art=kf_art.rgba[v->pose]+n*4;
   d->patch[n]=blend_rgba(d->patch[n],art,art[3]);
  }
  d->mask[ly*24+lx]=1;++d->pixels;++v->callback_count;v->part_count[k]=d->pixels;
 }
}
static void kf_end(void)
{
 if(!kf.enabled)return;
 for(unsigned i=0;i<25;i++)if(kf.draw[i].active){
  KfDraw *d=kf.draw+i;Tank194Draw *v=&d->draw;unsigned k=d->part;
  if(!kf_context()||!t194_colors()){kf_fail_slot(i+75,KF_CONTEXT);continue;}
  if(!kf_metadata_current(d)){kf_fail_slot(i+75,KF_CONTEXT);continue;}
  if(!kf_actor_current(d)){kf_deny(i+75);continue;}
  if(!kf.phase_open||k>=4||v->next!=k||v->mask!=(1u<<k)-1||d->pixels!=t194_counts[v->pose][k]||
     !kf_art_current()||!b313_family_writer_draw_ready(kf.frame)){kf_fail_slot(i+75,KF_END);continue;}
  v->mask|=1u<<k;v->next=k+1;d->active=false;
  if(k==3){d->complete=v->complete=v->mask==15&&v->callback_count==t194_totals[v->pose];
   if(!d->complete)kf_fail_slot(i+75,KF_END);else ++kf_status.completed;}
 }
}
static bool kf_draw_current(const KfDraw *d)
{
 return d->complete&&!d->active&&d->draw.complete&&d->draw.mask==15&&d->draw.next==4&&
  d->draw.pose<8&&d->draw.callback_count==t194_totals[d->draw.pose]&&
  kf.phase_seen&&kf.phase_closed&&!kf.phase_open&&kf_identity(d)&&kf_art_current()&&kf_terrain_current();
}
static void kf_finish(void)
{
 if(!kf.enabled||!kf.valid)return;
 for(unsigned i=0;i<25;i++)if(kf.draw[i].valid){
  KfDraw *d=kf.draw+i;
  if(!kf_context()||!t194_colors()){kf_fail_slot(i+75,KF_CONTEXT);continue;}
  if(!kf_metadata_current(d)){kf_fail_slot(i+75,KF_FINAL);continue;}
  if(!kf_actor_current(d)){kf_deny(i+75);continue;}
  if(!kf_draw_current(d)||!tf_current()){kf_fail_slot(i+75,KF_FINAL);continue;}
  if(!kf_cells(d))continue;
  d->patch_stamp=asteroid1_stamp((const Uint8 *)d->patch,sizeof d->patch);
  d->draw_stamp=asteroid1_stamp((const Uint8 *)&d->draw,sizeof d->draw);
  d->mask_stamp=asteroid1_stamp(d->mask,sizeof d->mask);d->ready=true;++kf_status.prepared;
 }
}
static bool kf_sealed_current(const KfDraw *d)
{
 return kf_draw_current(d)&&tf_current()&&kf_cells(d)&&
  d->draw_stamp==asteroid1_stamp((const Uint8 *)&d->draw,sizeof d->draw)&&
  d->patch_stamp==asteroid1_stamp((const Uint8 *)d->patch,sizeof d->patch)&&
  d->mask_stamp==asteroid1_stamp(d->mask,sizeof d->mask);
}
static uint32_t kf_compose(void)
{
 uint32_t used=0;
 for(unsigned i=0;i<25;i++)if(kf.draw[i].ready){
  KfDraw *d=kf.draw+i;
  if(!kf_context()||!t194_colors()){kf_fail_slot(i+75,KF_CONTEXT);continue;}
  if(!kf_metadata_current(d)){kf_fail_slot(i+75,KF_PRESENT);continue;}
  if(!kf_actor_current(d)){kf_deny(i+75);continue;}
  if(!kf_sealed_current(d)){kf_fail_slot(i+75,KF_PRESENT);continue;}
  const Tank194Draw *v=&d->draw;
  for(unsigned ly=0;ly<28;ly++)for(unsigned lx=0;lx<24;lx++)if(d->mask[ly*24+lx])
   for(unsigned sy=0;sy<8;sy++)memcpy((Uint32 *)tf.result->pixels+((unsigned)v->y*8+ly*8+sy)*2560+((unsigned)v->x-24)*8+lx*8,d->patch+(ly*8+sy)*192+lx*8,32);
  used|=UINT32_C(1)<<i;
 }
 return used;
}
static void kf_present_begin(uint32_t used)
{kf.presenting_slots=used;for(unsigned i=0;i<25;i++)kf.draw[i].ready=false;}
static void kf_present_end(void)
{if(kf.presenting_slots)++kf_status.presents;kf.presenting_slots=0;}
static void kf_release(void)
{
 kf_reset();for(unsigned p=0;p<8;p++)free(kf_art.rgba[p]);memset(&kf_art,0,sizeof kf_art);
 /* kf_denied is lifetime evidence, not renderer storage. Do not clear it. */
}
B313TankFallbackStatus render_mirror_tank_fallback_status(void)
{
 B313TankFallbackStatus s=kf_status;s.requested=kf_requested();s.active=kf.enabled&&kf.valid;
 s.presenting=kf.presenting_slots!=0;s.presented_slots=kf.presenting_slots;s.phase_open=kf.phase_open;s.frame=kf.frame;
 for(unsigned i=0;i<25;i++){
  const KfDraw *d=kf.draw+i;const Tank194Draw *v=&d->draw;
  s.draw[i]=(B313TankFallbackDrawStatus){.seen=d->seen,.valid=d->valid,.active=d->active,.complete=d->complete,
   .ready=d->ready,.presenting=(kf.presenting_slots&(UINT32_C(1)<<i))!=0,.denied=kf_denial_matches(i+75),
   .current=d->valid&&kf_draw_current(d)&&tf_current(),.epoch=v->epoch,.token=v->token,.generation=v->generation,
   .script_serial=v->script_serial,.slot=i+75,.event=v->event,.base=v->base,.pose=v->pose,
   .callback_count=v->callback_count,.part_mask=v->mask,.reason=d->reason,.surviving_cells=kf_cells(d),.x=v->x,.y=v->y};
 }
 return s;
}
bool render_mirror_tank_fallback_sample(unsigned slot,uint8_t *owners,size_t owner_bytes,uint32_t *argb,size_t pixels)
{
 if(slot<75||slot>=100||!owners||owner_bytes!=672||!argb||pixels!=43008||!tf.presenting||
    !(kf.presenting_slots&(UINT32_C(1)<<(slot-75)))||!kf_sealed_current(kf.draw+slot-75))return false;
 memcpy(owners,kf.draw[slot-75].mask,672);memcpy(argb,kf.draw[slot-75].patch,172032);return true;
}
