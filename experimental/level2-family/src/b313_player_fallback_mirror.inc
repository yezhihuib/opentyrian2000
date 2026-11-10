/* SPDX-License-Identifier: GPL-2.0-or-later
 * Independent current-frame normal Talon transaction. Never imports legacy
 * ship admission, actor canvas, previous-frame pixels or building witnesses.
 * The shared native writer is consumed only by tf_pixel, before our callback.
 */
enum {PF_CONTEXT=1,PF_POSE=2,PF_BODY=3,PF_SOURCE=4,PF_ART=5,PF_WRITE=6,
 PF_END=7,PF_FINAL=8,PF_PRESENT=9,PF_SHARED=10};
static struct {
 bool enabled,valid,pose_seen,active,complete,ready,presenting;
 uint64_t frame,session,generation,patch_stamp,mask_stamp;
 unsigned index,count,part_mask,reason;
 int x,y;
 uintptr_t bank_data;
 size_t bank_bytes;
 const Uint8 *art;
 Uint8 native[672],mask[672];
 Uint32 patch[43008];
} pf;
static struct {bool checked,valid;char root[1024];Uint8 *rgba[5];} pf_art;
static B313PlayerFallbackStatus pf_status;
static bool pf_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *v=getenv("BUILDING313_PLAYER_FALLBACK_ENABLE");
 return v&&!strcmp(v,"1")&&tf_requested()&&ps_requested();
#else
 return false;
#endif
}
static void pf_fail(unsigned reason)
{
 if(!pf.enabled)return;
 if(pf.valid){++pf_status.rejected;if(!pf_status.first_reason)pf_status.first_reason=reason;}
 if(!pf.reason)pf.reason=reason;
 pf.valid=pf.active=pf.ready=pf.presenting=false;
 memset(pf.mask,0,sizeof pf.mask);
}
static void pf_shared_fail(void){pf_fail(PF_SHARED);}
static void pf_reset(void){memset(&pf,0,sizeof pf);}
static void pf_begin(void)
{
 pf_reset();
 if(!pf_requested()||!tf_geometry())return;
 pf.enabled=pf.valid=true;pf.frame=fc_frame;pf.session=fc_session;pf.generation=fc_generation;
 ++pf_status.frames;
}
/* A separate immutable asset cache avoids any dependence on ps.draw.index,
 * ps.active or the old scene's failure/acceptance state. */
static bool pf_art_current(void)
{
 const PlayerShipSpec *spec=ps_spec(pf.index);
 return spec&&pf_art.checked&&pf_art.valid&&!strcmp(pf_art.root,ps_root())&&
  pf.art&&pf.art==pf_art.rgba[(spec->index-229)/2]&&
  asteroid1_stamp(pf.art,172032)==spec->stamp;
}
static bool pf_load(void)
{
 if(pf_art.checked){pf.art=ps_spec(pf.index)?pf_art.rgba[(pf.index-229)/2]:NULL;return pf_art_current();}
 pf_art.checked=true;
 if(!ps_root()[0]||strlen(ps_root())>=sizeof pf_art.root)return false;
 strcpy(pf_art.root,ps_root());bool all=true;
 for(unsigned pose=0;pose<5&&all;pose++){
  const PlayerShipSpec *spec=ps_specs+pose;char path[1200];Uint8 header[28],extra;REAR_STAT st;
  int n=snprintf(path,sizeof path,"%s/ship-%u-8.hda",pf_art.root,spec->index);
  if(n<0||(size_t)n>=sizeof path){all=false;break;}
  int fd=REAR_OPEN(path);if(fd<0){all=false;break;}
  bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==172060&&
   REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
  uint32_t v[6]={0};const uint32_t wanted[6]={90000+spec->index,8,24,28,5,7};
  if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
   for(unsigned i=0;i<6;i++)if(v[i]!=wanted[i])ok=false;}
  if(ok){pf_art.rgba[pose]=malloc(172032);ok=pf_art.rgba[pose]!=NULL;}
  if(ok)ok=REAR_READ(fd,pf_art.rgba[pose],172032)==172032&&REAR_READ(fd,&extra,1)==0&&
   asteroid1_stamp(pf_art.rgba[pose],172032)==spec->stamp;
  if(REAR_CLOSE(fd))ok=false;
  all=ok;
 }
 if(!all)for(unsigned i=0;i<5;i++){free(pf_art.rgba[i]);pf_art.rgba[i]=NULL;}
 pf_art.valid=all;pf.art=ps_spec(pf.index)?pf_art.rgba[(pf.index-229)/2]:NULL;
 return pf_art_current();
}
static bool pf_context(void)
{
 return pf.enabled&&pf.valid&&pf_requested()&&tf_geometry()&&
  pf.frame==fc_frame&&pf.session==fc_session&&pf.generation==fc_generation;
}
static bool pf_identity(void)
{
 return pf_context()&&pf.pose_seen&&ps_spec(pf.index)&&ps_scope()&&
  !player[0].invulnerable_ticks&&player[0].x-5==pf.x&&player[0].y-7==pf.y&&
  pf.bank_data==(uintptr_t)spriteSheet9.data&&pf.bank_bytes==spriteSheet9.size&&
  ps_source(spriteSheet9)&&global_talon_palette_matches();
}
static bool pf_terrain_current(void)
{
 return tf.captured&&tf.terrain&&tf.terrain==tf.terrain_surface&&family_rgb(tf.terrain)&&
  tf.terrain->pixels==tf.terrain_pixels&&tf.terrain->format==tf.terrain_format&&tf_ground_current();
}
static void pf_pose(unsigned pnum,Sprite2_array bank,int base,int index,unsigned invulnerable)
{
 if(!pf.enabled||!pf.valid)return;
 if(pf.pose_seen){pf_fail(PF_POSE);return;}
 /* An unsupported original pose is terminal, including invulnerability1->0. */
 pf.pose_seen=true;++pf_status.poses;
 if(!pf_context()||!fc.frame_active||!ps_scope()||pnum!=1||base!=233||invulnerable||
  player[0].invulnerable_ticks||!ps_spec((unsigned)index)||!ps_source(bank)||!global_talon_palette_matches()){
  pf_fail(PF_POSE);return;
 }
 pf.index=(unsigned)index;pf.x=player[0].x-5;pf.y=player[0].y-7;
 pf.bank_data=(uintptr_t)bank.data;pf.bank_bytes=bank.size;
}
static const Uint8 *pf_sample(const PlayerShipSpec *spec,unsigned x,unsigned y)
{
 static const Uint8 transparent[4]={0};
 if(spec->index==233)return pf.art+(y*192+x)*4;
 int nx=(int)x*100+spec->offset_x,ny=(int)y*100+spec->offset_y;
 if(nx<0||ny<0)return transparent;
 unsigned sx=(unsigned)(nx/spec->scale_x),sy=(unsigned)(ny/spec->scale_y);
 return sx<192&&sy<224?pf.art+(sy*192+sx)*4:transparent;
}
static void pf_body(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index,int style,unsigned pnum,int base)
{
 if(!pf.enabled||!pf.valid||style!=MIRROR_NORMAL||pnum!=1||base!=233)return;
 if(pf.active||pf.complete||!fc.frame_active||!pf_identity()||index!=pf.index||x!=pf.x||y!=pf.y||
  x<24||x>264||y<0||y>156||surface!=fc_source||surface!=game_screen||surface!=VGAScreen||
  !ps_source(bank)||bank.data!=(Uint8 *)pf.bank_data||bank.size!=pf.bank_bytes||
  !b313_family_writer_draw_ready(pf.frame)||!pf_terrain_current()||memcmp(tf.expected,fc_source_pixels,64000)){
  pf_fail(PF_BODY);return;
 }
 if(!pf_load()){pf_fail(PF_ART);return;}
 for(unsigned ly=0;ly<28;ly++)for(unsigned lx=0;lx<24;lx++){
  unsigned off=(unsigned)(y+(int)ly)*320+(unsigned)x+lx;
  pf.native[ly*24+lx]=tf.expected[off];
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
   unsigned n=(ly*8+sy)*192+lx*8+sx;
   pf.patch[n]=tf.mask[off]?((const Uint32 *)tf.terrain->pixels)[((unsigned)y*8+ly*8+sy)*2560+(unsigned)x*8+lx*8+sx]:palette_rgb(tf.expected[off]);
  }
 }
 pf.active=true;++pf_status.bodies;
}
/* tf_pixel calls this after consuming physical proof, before modifying the
 * old native index or terrain mask. No old scene state participates. */
static void pf_pixel(unsigned off,int style)
{
 if(!pf.enabled||!pf.valid)return;
 if(!pf_context()||off>=64000){pf_fail(PF_CONTEXT);return;}
 unsigned x=off%320,y=off/320;
 bool inside=(int)x>=pf.x&&(int)x<pf.x+24&&(int)y>=pf.y&&(int)y<pf.y+28;
 unsigned local=inside?(y-(unsigned)pf.y)*24+x-(unsigned)pf.x:0;
 if(inside&&pf.mask[local]){pf.mask[local]=0;++pf_status.retired;}
 if(!pf.active)return;
 const PlayerShipSpec *spec=ps_spec(pf.index);
 if(!spec||pf.count>=spec->count){pf_fail(PF_WRITE);return;}
 const PlayerShipWrite *w=spec->writes+pf.count;
 if(style!=MIRROR_NORMAL||x!=(unsigned)pf.x+w->x||y!=(unsigned)pf.y+w->y||
  ((const Uint8 *)fc_source_pixels)[off]!=w->index||tf.expected[off]!=pf.native[w->y*24+w->x]){
  pf_fail(PF_WRITE);return;
 }
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  unsigned n=((unsigned)w->y*8+sy)*192+(unsigned)w->x*8+sx;
  const Uint8 *art=pf_sample(spec,(unsigned)w->x*8+sx,(unsigned)w->y*8+sy);
  pf.patch[n]=blend_rgba(pf.patch[n],art,art[3]);
 }
 pf.mask[w->y*24+w->x]=1;++pf.count;
 for(unsigned part=0;part<4;part++)if(pf.count==spec->ends[part])pf.part_mask|=1u<<part;
}
static bool pf_draw_current(void)
{
 const PlayerShipSpec *spec=ps_spec(pf.index);
 return spec&&pf.complete&&!pf.active&&pf.count==spec->count&&pf.part_mask==15&&
  pf_identity()&&pf_art_current()&&pf_terrain_current();
}
static unsigned pf_cells(void)
{unsigned cells=0;for(unsigned i=0;i<672;i++)cells+=pf.mask[i]!=0;return cells;}
static void pf_end(void)
{
 if(!pf.active)return;
 const PlayerShipSpec *spec=ps_spec(pf.index);
 if(!spec||pf.count!=spec->count||pf.part_mask!=15||!pf_identity()||!pf_art_current()||
  !b313_family_writer_draw_ready(pf.frame)){pf_fail(PF_END);return;}
 pf.active=false;pf.complete=true;++pf_status.completed;
}
static void pf_finish(void)
{
 if(!pf.enabled||!pf.valid)return;
 if(!pf_draw_current()||!tf_current()){pf_fail(PF_FINAL);return;}
 if(!pf_cells())return;
 pf.patch_stamp=asteroid1_stamp((const Uint8 *)pf.patch,sizeof pf.patch);
 pf.mask_stamp=asteroid1_stamp(pf.mask,sizeof pf.mask);
 pf.ready=true;++pf_status.prepared;
}
static bool pf_sealed_current(void)
{
 return pf_draw_current()&&tf_current()&&pf_cells()&&
  pf.patch_stamp==asteroid1_stamp((const Uint8 *)pf.patch,sizeof pf.patch)&&
  pf.mask_stamp==asteroid1_stamp(pf.mask,sizeof pf.mask);
}
static bool pf_compose(void)
{
 if(!pf.ready)return false;
 if(!pf_sealed_current()){pf_fail(PF_PRESENT);return false;}
 for(unsigned ly=0;ly<28;ly++)for(unsigned lx=0;lx<24;lx++)if(pf.mask[ly*24+lx])
  for(unsigned sy=0;sy<8;sy++)memcpy((Uint32 *)tf.result->pixels+((unsigned)pf.y*8+ly*8+sy)*2560+((unsigned)pf.x-24)*8+lx*8,pf.patch+(ly*8+sy)*192+lx*8,32);
 return true;
}
static void pf_present_begin(bool used){pf.presenting=used&&pf.ready;pf.ready=false;}
static void pf_present_end(void){if(pf.presenting)++pf_status.presents;pf.presenting=false;}
static void pf_release(void)
{pf_reset();for(unsigned i=0;i<5;i++)free(pf_art.rgba[i]);memset(&pf_art,0,sizeof pf_art);}
B313PlayerFallbackStatus render_mirror_player_fallback_status(void)
{
 B313PlayerFallbackStatus s=pf_status;
 s.requested=pf_requested();s.active=pf.enabled&&pf.valid;s.complete=pf.complete;
 s.ready=pf.ready;s.presenting=pf.presenting;s.frame=pf.frame;s.index=pf.index;
 s.callback_count=pf.count;s.surviving_cells=pf_cells();s.reason=pf.reason;s.x=pf.x;s.y=pf.y;
 return s;
}
bool render_mirror_player_fallback_sample(uint8_t *owners,size_t owner_bytes,uint32_t *argb,size_t pixels)
{
 if(!owners||owner_bytes!=672||!argb||pixels!=43008||!pf.presenting||!tf.presenting||!pf_sealed_current())return false;
 memcpy(owners,pf.mask,sizeof pf.mask);memcpy(argb,pf.patch,sizeof pf.patch);return true;
}
