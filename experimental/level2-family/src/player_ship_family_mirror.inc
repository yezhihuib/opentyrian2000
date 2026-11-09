/* SPDX-License-Identifier: GPL-2.0-or-later
 * Five-pose intact player ship family. Invulnerability is separately opt-in.
 * Original pose -> original body call ->
 * four original tiles -> ordered physical-store callbacks -> original end.
 * No actor admission, gameplay write, new lifetime, or native-hole ownership.
 * Unchanged HDA bytes, affine turn texture coordinates only. Neutral233 is
 * bit-identical. Every store remains inside the exact original pose callbacks.
 */
#include "player_ship_native.inc"
static struct {PlayerShipDraw draw;bool active,blend_callback;Uint8 blend_after;unsigned count,reason;PlayerShipWrite writes[266];} ps;
static struct {bool checked,valid;char root[1024];Uint8 *rgba[5];} ps_art;
static uint8_t ps_owned[64000],ps_shadows[64000];
static uint64_t ps_normal_retirements,ps_blend_retirements,ps_shadow_writes;
static const char *ps_root(void){const char *e=getenv("PLAYER_SHIP_FAMILY_ASSET_DIR");return e?e:"";}
static bool ps_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("PLAYER_SHIP_FAMILY_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
#else
 return false;
#endif
}
/* The established public preset stays normal-only. This gate never grants
 * parent family admission or changes the original invulnerability countdown. */
static bool ps_invulnerable_requested(void)
{
 const char *e=getenv("PLAYER_SHIP_FAMILY_INVULNERABLE_ENABLE");
 return ps_requested()&&e&&!strcmp(e,"1");
}
static bool ps_scope(void)
{
 return ps_requested()&&family_scope()&&mainLevel==6&&terrain_file=='z'&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&player[0].items.ship==1&&ships[1].shipgraphic==233&&
 shipGr==233&&shipGrPtr==&spriteSheet9&&player[0].is_alive&&!player[0].is_dragonwing&&
 !player[0].exploding_ticks&&player[0].armor&&!endLevel;
}
static bool ps_source(Sprite2_array bank)
{
 return bank.data&&bank.data==spriteSheet9.data&&bank.size==33484&&bank.size==spriteSheet9.size&&
 asteroid1_stamp(bank.data,bank.size)==UINT64_C(0x3c9578d713f73930);
}
static void ps_fail(unsigned reason)
{
 if(!ps.reason)ps.reason=reason;
 ps.draw.failed=true;ps.draw.accepted=false;ps.active=false;ps.blend_callback=false;
 if(ps.draw.contributed)family_fault(FC_SOURCE);
}
static void ps_reset(void)
{
 if(ps.draw.contributed||ps.active)ps_fail(1);
 memset(&ps,0,sizeof ps);memset(ps_owned,0,sizeof ps_owned);memset(ps_shadows,0,sizeof ps_shadows);
}
static void ps_tick(void)
{
 if(ps.draw.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&ps,0,sizeof ps);memset(ps_owned,0,sizeof ps_owned);memset(ps_shadows,0,sizeof ps_shadows);
}
static bool ps_art_current(void)
{
 const PlayerShipSpec *spec=ps_spec(ps.draw.index);
 return spec&&ps_art.checked&&ps_art.valid&&!strcmp(ps_art.root,ps_root())&&
 ps_art.rgba[(spec->index-229)/2]&&asteroid1_stamp(ps_art.rgba[(spec->index-229)/2],172032)==spec->stamp;
}
static bool ps_load(void)
{
 if(ps_art.checked)return ps_art_current();
 ps_art.checked=true;
 if(!ps_root()[0]||strlen(ps_root())>=sizeof ps_art.root)return false;
 strcpy(ps_art.root,ps_root());bool all=true;
 for(unsigned pose=0;pose<5&&all;pose++){
  const PlayerShipSpec *spec=ps_specs+pose;char path[1200];Uint8 header[28],extra;REAR_STAT st;
  int n=snprintf(path,sizeof path,"%s/ship-%u-8.hda",ps_art.root,spec->index);
  if(n<0||(size_t)n>=sizeof path){all=false;break;}
  int fd=REAR_OPEN(path);if(fd<0){all=false;break;}
  bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==172060&&
  REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
  uint32_t v[6]={0};const uint32_t wanted[6]={90000+spec->index,8,24,28,5,7};
  if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
   for(unsigned i=0;i<6;i++)if(v[i]!=wanted[i])ok=false;}
  if(ok){ps_art.rgba[pose]=malloc(172032);ok=ps_art.rgba[pose]!=NULL;}
  if(ok)ok=REAR_READ(fd,ps_art.rgba[pose],172032)==172032&&REAR_READ(fd,&extra,1)==0&&
   asteroid1_stamp(ps_art.rgba[pose],172032)==spec->stamp;
  if(REAR_CLOSE(fd))ok=false;
  all=ok;
 }
 if(!all)for(unsigned i=0;i<5;i++){free(ps_art.rgba[i]);ps_art.rgba[i]=NULL;}
 ps_art.valid=all;return all;
}
static void ps_shutdown(void)
{ps_reset();for(unsigned i=0;i<5;i++)free(ps_art.rgba[i]);memset(&ps_art,0,sizeof ps_art);}
/* Sampling changes texture coordinates, never callback coordinates or ownership.
 * Positive integer division is floor. Out-of-range texture samples are transparent.
 * Neutral uses the original pointer calculation without a resampling operation. */
static const Uint8 *ps_sample(const PlayerShipSpec *spec,unsigned x,unsigned y)
{
 static const Uint8 transparent[4]={0};const Uint8 *rgba=ps_art.rgba[(spec->index-229)/2];
 if(spec->index==233)return rgba+(y*192+x)*4;
 int nx=(int)x*100+spec->offset_x,ny=(int)y*100+spec->offset_y;
 if(nx<0||ny<0)return transparent;
 unsigned sx=(unsigned)(nx/spec->scale_x),sy=(unsigned)(ny/spec->scale_y);
 return sx<192&&sy<224?rgba+(sy*192+sx)*4:transparent;
}
static void ps_pose(unsigned pnum,Sprite2_array bank,int base,int index,unsigned invulnerable)
{
 if(!ps_requested())return;
 if(ps.draw.pose_seen||ps.draw.contributed){ps_fail(2);return;}
 if(!fc.frame_active||fc.frame_failed||!ps_scope()||pnum!=1||base!=233||(invulnerable&&!ps_invulnerable_requested())||!ps_spec((unsigned)index)||invulnerable!=player[0].invulnerable_ticks||
 !family_geometry(false)||!ps_source(bank)||!global_talon_palette_matches())return;
 ps.draw=(PlayerShipDraw){.frame=fc_frame,.session=fc_session,.generation=fc_generation,
 .bank_data=(uintptr_t)bank.data,.bank_bytes=(unsigned)bank.size,.ship_record=1,.index=(unsigned)index,
 .invulnerable_ticks=invulnerable,.style=invulnerable?MIRROR_BLEND:MIRROR_NORMAL,
 .x=player[0].x-5,.y=player[0].y-7,.pose_seen=true};
}
static bool ps_current(void)
{
 return !ps.draw.failed&&(!ps.draw.invulnerable_ticks||ps_invulnerable_requested())&&ps.draw.pose_seen&&ps_spec(ps.draw.index)&&ps_scope()&&ps_source(spriteSheet9)&&global_talon_palette_matches()&&
 ps.draw.frame==fc_frame&&ps.draw.session==fc_session&&ps.draw.generation==fc_generation&&
 ps.draw.bank_data==(uintptr_t)spriteSheet9.data&&ps.draw.bank_bytes==spriteSheet9.size&&
 ps.draw.x==player[0].x-5&&ps.draw.y==player[0].y-7&&
 /* mainint decrements once after pose, before the blended body, including1->0. */
 player[0].invulnerable_ticks==(ps.draw.invulnerable_ticks?ps.draw.invulnerable_ticks-1:0);
}
static int ps_body(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index,int style,unsigned pnum,int base)
{
 /* Unsupported/shadow calls retain their exact existing path. */
 if(!ps_requested()||base!=233||!ps_spec(index)||(style!=MIRROR_NORMAL&&(style!=MIRROR_BLEND||!ps_invulnerable_requested()))||pnum!=1)return -1;
 if(!fc.frame_active||fc.frame_failed||!ps_current()||style!=ps.draw.style||index!=ps.draw.index||!ps_source(bank)||x!=ps.draw.x||y!=ps.draw.y||
 x<24||x>264||y<0||y>156||surface!=game_screen||surface!=VGAScreen||!ps_load())return 0;
 if(ps.active||ps.draw.contributed){ps_fail(3);return 0;}
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||suppress||!family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
 !b313_family_writer_draw_ready(fc_frame)||!family_prepare_canvas()){ps_fail(4);family_fault(FC_SOURCE);return 0;}
 for(int row=0;row<28;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,24)){
 ps_fail(5);family_fault(FC_WRITER);return 0;}
 ps.active=true;ps.draw.contributed=true;return 1;
}
static bool ps_retire(unsigned off,int style)
{
 bool owned=off<64000&&ps_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++ps_blend_retirements;else ++ps_normal_retirements;
 ps_owned[off]=ps_shadows[off]=0;}
 return owned;
}
static bool ps_pixel(unsigned x,unsigned y,int style)
{
 if(!ps.active)return false;
 const PlayerShipSpec *spec=ps_spec(ps.draw.index);
 if(!spec||ps.count>=spec->count){ps_fail(6);family_fault(FC_ORDER);return true;}
 const PlayerShipWrite *w=spec->writes+ps.count;
 if(style!=ps.draw.style||(style==MIRROR_BLEND&&!ps.blend_callback)||x!=(unsigned)ps.draw.x+w->x||y!=(unsigned)ps.draw.y+w->y||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=(style==MIRROR_BLEND?ps.blend_after:w->index)||
 expected[y*320+x]!=(style==MIRROR_BLEND?ps.blend_after:w->index)){
 ps_fail(6);family_fault(FC_ORDER);return true;}
 ps.blend_callback=false;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
 size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
 const Uint8 *art=ps_sample(spec,(unsigned)w->x*8+sx,(unsigned)w->y*8+sy);
 /* Existing Talon HD operator: half authored coverage, no new blink. */
 *dst=blend_rgba(*dst,art,style==MIRROR_BLEND?(art[3]+1)/2:art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;green_under_owner[n]=0;
 OHS_SURVIVAL_WRITE(canvas,dst,PLAYER_SHIP_HD_STORE_TAG);
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 ps_owned[off]=1;ps_shadows[off]=0;selected[off]=1;ps.writes[ps.count]=*w;
 ++ps.count;ps.draw.callback_count=ps.count;
 for(unsigned part=0;part<4;part++)if(ps.count==spec->ends[part])ps.draw.part_mask|=1u<<part;
 return true;
}
/* Validate the actual original blend before family_pixel updates expected.
 * No source inference from the resulting index: check actual callback source,
 * tile, origin, order and address; family_pixel still requires physical proof.
 * The one-callback token cannot authorize generic blend/shadow writers. */
static void ps_sprite2_blend_pixel(SDL_Surface *surface,Uint8 *address,Uint8 source,
 Sprite2_array bank,unsigned index,int origin_x,int origin_y)
{
 if(ps.active){
  const PlayerShipSpec *spec=ps_spec(ps.draw.index);
  unsigned part=0;while(spec&&part<4&&ps.count>=spec->ends[part])++part;
  static const unsigned parts[4]={0,1,19,20};
  if(!spec||part>=4||ps.blend_callback||ps.draw.style!=MIRROR_BLEND||surface!=fc_source||
   bank.data!=(Uint8 *)ps.draw.bank_data||bank.size!=ps.draw.bank_bytes||index!=ps.draw.index+parts[part]||
   origin_x!=ps.draw.x+(int)(part%2)*12||origin_y!=ps.draw.y+(int)(part/2)*14){
   ps_fail(6);family_fault(FC_ORDER);
  }else{
   const PlayerShipWrite *w=spec->writes+ps.count;
   unsigned off=(ps.draw.y+w->y)*320+ps.draw.x+w->x;
   if(address!=(Uint8 *)fc_source_pixels+off||source!=w->index||
    *address!=(Uint8)((source&240)|(((source&15)+(expected[off]&15))/2))){
    ps_fail(6);family_fault(FC_ORDER);
   }else{ps.blend_after=*address;ps.blend_callback=true;}
  }
 }
 family_pixel(surface,address,MIRROR_BLEND);
 if(ps.blend_callback){ps.blend_callback=false;ps_fail(6);family_fault(FC_ORDER);}
}
static void ps_shadow(unsigned off)
{if(off<64000&&ps_owned[off]){if(ps_shadows[off]<255)++ps_shadows[off];++ps_shadow_writes;}}
static void ps_end(void)
{
 if(!ps.active)return;
 const PlayerShipSpec *spec=ps_spec(ps.draw.index);
 if(!spec||ps.blend_callback||ps.count!=spec->count||ps.draw.part_mask!=15||!b313_family_writer_draw_ready(fc_frame)||!ps_current()){
 ps_fail(7);family_fault(FC_ORDER);return;}
 ps.draw.complete=true;ps.active=false;
}
static bool ps_finish(void)
{
 const PlayerShipSpec *spec=ps_spec(ps.draw.index);
 return !ps.draw.contributed||(spec&&!ps.active&&!ps.blend_callback&&ps.draw.complete&&ps.draw.callback_count==spec->count&&ps.draw.part_mask==15&&
 ps_current()&&ps_art_current());
}
static void ps_accept(void){ps.draw.accepted=ps.draw.contributed&&fc.ready&&!fc.frame_failed&&ps_finish();}
PlayerShipFamilyStatus render_mirror_player_ship_family_status(void)
{
 PlayerShipFamilyStatus s={0};s.requested=ps_requested();s.loaded=ps_art.valid;s.first_reason=ps.reason;s.draw=ps.draw;
 s.draw.failed|=fc.frame_failed;s.normal_retirements=ps_normal_retirements;s.blend_retirements=ps_blend_retirements;s.shadow_writes=ps_shadow_writes;
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=ps_owned[i]!=0;s.shadowed_cells+=ps_owned[i]&&ps_shadows[i];}return s;
}
bool render_mirror_player_ship_pre_draw(PlayerShipDraw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!ps.active||ps.count||fc.frame_failed||!family_geometry(true))return false;
 *d=ps.draw;
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
unsigned render_mirror_player_ship_callbacks(PlayerShipWrite *out,size_t capacity)
{if(!out||capacity<ps.count)return 0;memcpy(out,ps.writes,ps.count*sizeof *out);return ps.count;}
bool render_mirror_player_ship_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!ps.draw.accepted||fc.frame_active||fc.frame_failed||
 !ps_finish()||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,ps_owned,64000);memcpy(shadows,ps_shadows,64000);return true;
}
