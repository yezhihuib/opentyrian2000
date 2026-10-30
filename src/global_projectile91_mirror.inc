/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite shared normal bank8/{91,145,61,101,120,139,168,169} enemy-shot owner; independent payloads.
 * Included after decode_tile; no level/episode/map predicate grants this owner. */
static bool global_projectile91_cached;
/* Survives ownership transfer (for example to antialiased HUD glyphs). */
static bool global_projectile91_contributed;
/* Contribution provenance persists even after all pixels transfer to another
 * owner. Optional members never gate a different, unused member's admission. */
static unsigned global_projectile91_used_members;
static unsigned global_projectile91_member(unsigned index)
{return index==91?1u:index==145?2u:index==61?4u:index==101?8u:index==120?16u:index==139?32u:index==168?64u:index==169?128u:0u;}
static Asset *global_projectile91_member_resource(unsigned index)
{return index==91?projectile91_resource(global_asset_directory):index==145?projectile145_resource(global_asset_directory):index==61?projectile61_resource(global_asset_directory):(index==168||index==169)?projectile_gold_pulse_resource(global_asset_directory,index):projectile_blue_triplet_resource(global_asset_directory,index);}
static bool global_projectile91_member_palette(unsigned index)
{return index==91?projectile91_palette_matches():index==145?projectile145_palette_matches():index==61?projectile61_palette_matches():(index==168||index==169)?projectile_gold_pulse_palette_matches(index):projectile_blue_triplet_palette_matches(index);}
static bool global_projectile91_member_source(Sprite2_array bank,unsigned index)
{return index==91?projectile91_source(bank,index):index==145?projectile145_source(bank,index):index==61?projectile61_source(bank,index):(index==168||index==169)?projectile_gold_pulse_source(bank,index):projectile_blue_triplet_source(bank,index);}

static size_t global_projectile91_capacity;
static Uint32 global_projectile91_output_palette[256],global_projectile91_underlay_palette[256];
static Uint8 global_projectile91_used_colors[256];
static struct {SDL_Surface *surface;void *pixels;SDL_PixelFormat *format;int pitch;} global_projectile91_fade_lease;
static struct {
 SDL_Surface *surface,*final_surface,*canvas_surface,*output_surface;
 void *pixels,*final_pixels,*canvas_pixels,*output_pixels;
 SDL_PixelFormat *format,*final_format,*canvas_format,*output_format;
 int pitch,final_pitch,canvas_pitch,output_pitch,density;
} global_projectile91_source_lease;
static bool global_projectile91_talon_dependency;
static struct {bool live;int x,y,style,filter;unsigned left;Uint8 source[168],mask[168],seen[168];} global_projectile91_call;

static bool global_projectile91_requested(void)
{return global_asset_directory[0]&&game_probe_density==8&&!xmas&&!game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid;}
static bool global_projectile91_palette_matches(void)
{return (!(global_projectile91_used_members&1u)||projectile91_palette_matches())&&
        (!(global_projectile91_used_members&2u)||projectile145_palette_matches())&&
        (!(global_projectile91_used_members&4u)||projectile61_palette_matches())&&
        (!(global_projectile91_used_members&8u)||projectile_blue_triplet_palette_matches(101))&&
        (!(global_projectile91_used_members&16u)||projectile_blue_triplet_palette_matches(120))&&
        (!(global_projectile91_used_members&32u)||projectile_blue_triplet_palette_matches(139))&&
        (!(global_projectile91_used_members&64u)||projectile_gold_pulse_palette_matches(168))&&
        (!(global_projectile91_used_members&128u)||projectile_gold_pulse_palette_matches(169));}
static bool global_projectile91_underlay_matches(void)
{
 for(unsigned i=0;i<256;i++)if(global_projectile91_used_colors[i]&&
  (rgb_palette[i]&0xffffffu)!=global_projectile91_underlay_palette[i])return false;
 return true;
}
static void global_projectile91_use_color(unsigned i)
{if(!global_projectile91_used_colors[i]){global_projectile91_used_colors[i]=1;global_projectile91_underlay_palette[i]=rgb_palette[i]&0xffffffu;}}
static bool global_projectile91_source_matches(Sprite2_array bank)
{return projectile91_source(bank,91)&&
        (!(global_projectile91_used_members&1u)||projectile91_resource(global_asset_directory)!=NULL)&&
        (!(global_projectile91_used_members&2u)||projectile145_resource(global_asset_directory)!=NULL)&&
        (!(global_projectile91_used_members&4u)||projectile61_resource(global_asset_directory)!=NULL)&&
        (!(global_projectile91_used_members&8u)||projectile_blue_triplet_resource(global_asset_directory,101)!=NULL)&&
        (!(global_projectile91_used_members&16u)||projectile_blue_triplet_resource(global_asset_directory,120)!=NULL)&&
        (!(global_projectile91_used_members&32u)||projectile_blue_triplet_resource(global_asset_directory,139)!=NULL)&&
        (!(global_projectile91_used_members&64u)||projectile_gold_pulse_resource(global_asset_directory,168)!=NULL)&&
        (!(global_projectile91_used_members&128u)||projectile_gold_pulse_resource(global_asset_directory,169)!=NULL);}
static bool global_projectile91_disjoint(const SDL_Surface *a,const SDL_Surface *b)
{
 uintptr_t x=(uintptr_t)a->pixels,y=(uintptr_t)b->pixels;
 return x<y?y-x>=(size_t)a->pitch*a->h:x-y>=(size_t)b->pitch*b->h;
}
static bool global_projectile91_layout(void)
{
 int d=game_probe_density;
 if(d!=8||!game_screen||!game_screen->pixels||!game_screen->format||
  game_screen->w!=320||game_screen->h!=200||game_screen->pitch!=320||game_screen->format->format!=SDL_PIXELFORMAT_INDEX8||
  game_screen->format->BitsPerPixel!=8||game_screen->format->BytesPerPixel!=1)return false;
 SDL_Surface *surfaces[2]={canvas,output};
 for(unsigned i=0;i<2;i++) {SDL_Surface *v=surfaces[i];if(!v||!v->pixels||!v->format||v->w!=320*d||v->h!=200*d||
  v->pitch<v->w*4||v->pitch%4||(uintptr_t)v->pixels%sizeof(Uint32)||
  v->format->format!=SDL_PIXELFORMAT_ARGB8888||v->format->BitsPerPixel!=32||v->format->BytesPerPixel!=4)return false;}
 SDL_Surface *f=VGAScreenSeg;
 if(!f||!f->pixels||!f->format||f->w!=320||f->h!=200||f->pitch<320||
  f->format->format!=SDL_PIXELFORMAT_INDEX8||f->format->BitsPerPixel!=8||f->format->BytesPerPixel!=1)return false;
 SDL_Surface *all[4]={game_screen,f,canvas,output};
 for(unsigned i=0;i<4;i++)for(unsigned j=0;j<i;j++)if(!global_projectile91_disjoint(all[i],all[j]))return false;
 return true;
}
static bool global_projectile91_final_surface_matches(void)
{
 SDL_Surface *s=VGAScreenSeg;
 return s&&s==global_projectile91_source_lease.final_surface&&s->pixels&&s->pixels==global_projectile91_source_lease.final_pixels&&
  s->format&&s->format==global_projectile91_source_lease.final_format&&s->w==320&&s->h==200&&s->pitch>=320&&s->pitch==global_projectile91_source_lease.final_pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1;
}
static bool global_projectile91_surface_matches(void)
{
 SDL_Surface *s=game_screen;
 return global_projectile91_layout()&&canvas==global_projectile91_source_lease.canvas_surface&&output==global_projectile91_source_lease.output_surface&&
  canvas->pixels==global_projectile91_source_lease.canvas_pixels&&output->pixels==global_projectile91_source_lease.output_pixels&&
  canvas->format==global_projectile91_source_lease.canvas_format&&output->format==global_projectile91_source_lease.output_format&&
  canvas->pitch==global_projectile91_source_lease.canvas_pitch&&output->pitch==global_projectile91_source_lease.output_pitch&&
  s&&s==global_projectile91_source_lease.surface&&s->pixels&&s->pixels==global_projectile91_source_lease.pixels&&
  s->format&&s->format==global_projectile91_source_lease.format&&s->w==320&&s->h==200&&s->pitch==320&&s->pitch==global_projectile91_source_lease.pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&
  game_probe_density==global_projectile91_source_lease.density;
}


static void global_projectile91_fail(void);
static void global_projectile91_reset(void)
{
 /* Retire the actual RGB contribution before its proof bits. A still-active
  * legacy composition must not copy a disabled global owner's stale pixels. */
 if(global_projectile91_frame) {
  bool safe=global_projectile91_surface_matches();global_projectile91_fail();
  if(!safe){active=shared_hud_frame=ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 }
 if(global_projectile91_contributed){active=shared_hud_frame=ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 if(global_projectile91_cached){ready=last_output_valid=have_fade_saved=false;fade_mode=0;}
 global_projectile91_frame=global_projectile91_cached=global_projectile91_fault=global_projectile91_contributed=false;global_projectile91_used_members=0;global_projectile91_call.live=false;
 global_projectile91_talon_dependency=false;memset(&global_projectile91_source_lease,0,sizeof(global_projectile91_source_lease));
 memset(&global_projectile91_fade_lease,0,sizeof(global_projectile91_fade_lease));
 if(global_projectile91_owner)memset(global_projectile91_owner,0,global_projectile91_capacity);
 if(global_projectile91_foreign)memset(global_projectile91_foreign,0,global_projectile91_capacity);
}
static void global_projectile91_shutdown(void)
{
 global_projectile91_reset();
 projectile91_shutdown();projectile145_shutdown();projectile61_shutdown();projectile_blue_triplet_shutdown();projectile_gold_pulse_shutdown();
 free(global_projectile91_owner);free(global_projectile91_foreign);global_projectile91_owner=global_projectile91_foreign=NULL;global_projectile91_capacity=0;
}
static void global_projectile91_frame_begin(void)
{
 global_projectile91_frame=global_projectile91_cached=global_projectile91_fault=global_projectile91_contributed=false;global_projectile91_used_members=0;global_projectile91_call.live=false;
 memset(global_projectile91_used_colors,0,sizeof(global_projectile91_used_colors));global_projectile91_talon_dependency=false;
 if(!global_projectile91_requested()||!global_projectile91_layout()||!VGAScreenSeg||!VGAScreenSeg->pixels||!VGAScreenSeg->format||
  VGAScreenSeg->w!=320||VGAScreenSeg->h!=200||VGAScreenSeg->pitch<320||VGAScreenSeg->format->format!=SDL_PIXELFORMAT_INDEX8)return;
 size_t n=(size_t)canvas->w*canvas->h;
 if(global_projectile91_capacity!=n) {
  Uint8 *owner=calloc(n,1),*foreign=calloc(n,1);
  if(!owner||!foreign){free(owner);free(foreign);return;}
  free(global_projectile91_owner);free(global_projectile91_foreign);global_projectile91_owner=owner;global_projectile91_foreign=foreign;global_projectile91_capacity=n;
 }
 memset(global_projectile91_owner,0,n);memset(global_projectile91_foreign,0,n);
 global_projectile91_source_lease.final_surface=VGAScreenSeg;global_projectile91_source_lease.final_pixels=VGAScreenSeg->pixels;
 global_projectile91_source_lease.final_format=VGAScreenSeg->format;global_projectile91_source_lease.final_pitch=VGAScreenSeg->pitch;
 global_projectile91_source_lease.canvas_surface=canvas;global_projectile91_source_lease.canvas_pixels=canvas->pixels;
 global_projectile91_source_lease.canvas_format=canvas->format;global_projectile91_source_lease.canvas_pitch=canvas->pitch;
 global_projectile91_source_lease.output_surface=output;global_projectile91_source_lease.output_pixels=output->pixels;
 global_projectile91_source_lease.output_format=output->format;global_projectile91_source_lease.output_pitch=output->pitch;
 global_projectile91_source_lease.surface=game_screen;global_projectile91_source_lease.pixels=game_screen->pixels;
 global_projectile91_source_lease.format=game_screen->format;global_projectile91_source_lease.pitch=game_screen->pitch;global_projectile91_source_lease.density=game_probe_density;
 global_projectile91_frame=true;
}

static void global_projectile91_fail(void)
{
 global_projectile91_fault=true;global_projectile91_call.live=false;
 if(!global_projectile91_surface_matches()||!canvas||!global_projectile91_owner)return;
 int d=game_probe_density;
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++) {
  size_t n=(size_t)y*canvas->w+x;if(!global_projectile91_owner[n])continue;
  ((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch))[x]=palette_rgb(((Uint8 *)game_screen->pixels)[(y/d)*320+x/d]);
  global_projectile91_owner[n]=global_projectile91_foreign[n]=hd_owner[n]=cloud_owner[n]=0;
 }
}
static void global_projectile91_observed_preflight(void)
{
 if(global_projectile91_contributed&&(!global_projectile91_requested()||!global_projectile91_surface_matches()||
    !global_projectile91_final_surface_matches()||!global_projectile91_source_matches(spriteSheet8)||
    !global_projectile91_palette_matches()||!global_projectile91_underlay_matches()))global_projectile91_fail();
}
static int global_projectile91_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index)
{
 unsigned member=global_projectile91_member(index);
 if(!member)return 0;
 if(!global_projectile91_requested()||!global_projectile91_frame||global_projectile91_fault||surface!=game_screen||
  !global_projectile91_surface_matches()||surface!=VGAScreen||
  !global_projectile91_source_matches(spriteSheet8)||!global_projectile91_palette_matches()||!global_projectile91_underlay_matches()){
  if(global_projectile91_contributed)global_projectile91_fail();return 0;}
 /* A missing/corrupt/unmatched optional member which has not contributed must
  * not disable the other member. A used dependency still fails closed. */
 Asset *resource=global_projectile91_member_resource(index);
 if(!global_projectile91_member_source(bank,index)||!global_projectile91_member_palette(index)||!resource){
  if(global_projectile91_used_members&member)global_projectile91_fail();return 0;}
 /* Native quadrant visibility is actor-based and can still issue an entirely
  * clipped top tile. Keep it classic without poisoning other valid quadrants.
  * Physical-row wrapping is likewise deliberately not reinterpreted as HD. */
 if(x<0||x>308||y<-13||y>=200)return 0;
 if(global_projectile91_call.live){global_projectile91_fail();return 0;}
 memset(&global_projectile91_call,0,sizeof(global_projectile91_call));
 if(!decode_tile(bank,index,global_projectile91_call.source,global_projectile91_call.mask,12,0,0))return 0;
 for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(global_projectile91_call.mask[yy*12+xx]&&y+yy>=0&&y+yy<200)++global_projectile91_call.left;
 global_projectile91_call.x=x;global_projectile91_call.y=y;global_projectile91_call.style=MIRROR_NORMAL;global_projectile91_call.filter=0;global_projectile91_call.live=true;
 font_before_effect((SDL_Rect){x,y,12,14});
 int d=game_probe_density;const Uint8 *rgba=resource->rgba;
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++) {
  int dx=x*d+ax,dy=y*d+ay;if(dy<0||dy>=canvas->h)continue;
  size_t n=(size_t)dy*canvas->w+dx;const Uint8 *a=rgba+4*(ay*96+ax);
  bool native=global_projectile91_call.mask[(ay/d)*12+ax/d]!=0;
  if(!a[3]&&!native)continue;
  bool foreign=global_projectile91_owner[n]?global_projectile91_foreign[n]:hd_owner[n]!=0;
  Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+dy*canvas->pitch)+dx;
  if(!hd_owner[n]) {Uint8 v=((Uint8 *)game_screen->pixels)[(dy/d)*320+dx/d];*p=palette_rgb(v);global_projectile91_use_color(v);}
  else if(foreign)for(unsigned i=0;i<256;i++)global_projectile91_use_color(i);
  if(global_talon_owner&&global_talon_owner[n])global_projectile91_talon_dependency=true;
  if(a[3]) {unsigned alpha=a[3];
   *p=blend_rgba(*p,a,(int)alpha);
   if(alpha==255)foreign=false;
  }
  if(global_talon_owner)global_talon_owner[n]=global_talon_foreign[n]=0;
  if(global_rotor_owner)global_rotor_owner[n]=global_rotor_foreign[n]=0;
  global_projectile91_contributed=true;global_projectile91_used_members|=member;
  global_newshf_clear(n);
  if(global_pulse_owner)global_pulse_owner[n]=global_pulse_foreign[n]=0;
  if(global_shield_owner)global_shield_owner[n]=global_shield_foreign[n]=0;
  if(global_vulcan_owner)global_vulcan_owner[n]=global_vulcan_foreign[n]=0;
  if(global_hitflare_owner)global_hitflare_owner[n]=global_hitflare_foreign[n]=0;
  if(global_smoke_owner)global_smoke_owner[n]=global_smoke_foreign[n]=0;
  if(global_green_owner)global_green_owner[n]=global_green_foreign[n]=0;
  if(global_small_explosion_owner)global_small_explosion_owner[n]=global_small_explosion_foreign[n]=0;
  if(global_cash25_owner)global_cash25_owner[n]=global_cash25_foreign[n]=0;
  global_projectile91_owner[n]=1;global_projectile91_foreign[n]=foreign;hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  selected[(dy/d)*320+dx/d]=1;
 }
 ++draws;return 1;
}
static bool global_projectile91_pixel(int x,int y,Uint8 before,Uint8 after,int style)
{
 if(!global_projectile91_frame||!global_projectile91_owner)return false;
 if(!global_projectile91_surface_matches()){global_projectile91_fail();render_mirror_unsupported("global-source-layout");return false;}
 int d=game_probe_density;
 if(global_projectile91_call.live) {
  int dx=x-global_projectile91_call.x,dy=y-global_projectile91_call.y;
  if(dx<0||dx>=12||dy<0||dy>=14){global_projectile91_fail();return false;}
  unsigned n=(unsigned)(dy*12+dx);Uint8 source=global_projectile91_call.source[n];
  Uint8 want=style==MIRROR_NORMAL?(global_projectile91_call.filter?(Uint8)(global_projectile91_call.filter|(source&15)):source):style==MIRROR_BLEND?(Uint8)((source&240)|(((source&15)+(before&15))/2)):(Uint8)((before&240)|((before&15)/2));
  if(style!=global_projectile91_call.style||!global_projectile91_call.mask[n]||global_projectile91_call.seen[n]||after!=want){global_projectile91_fail();return false;}
  global_projectile91_call.seen[n]=1;--global_projectile91_call.left;return true;
 }
 bool shadow=style==MIRROR_SHADOW&&after==(Uint8)((before&240)|((before&15)/2));
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
  size_t n=(size_t)(y*d+sy)*canvas->w+x*d+sx;
  if(!global_projectile91_owner[n]||(!suppress&&shadow))continue;
  global_projectile91_owner[n]=global_projectile91_foreign[n]=0;
  if(!suppress&&style!=MIRROR_NORMAL){hd_owner[n]=0;cloud_owner[n]=0;}
 }
 return false;
}
static void global_projectile91_end(void)
{if(global_projectile91_call.live&&global_projectile91_call.left)global_projectile91_fail();global_projectile91_call.live=false;}
/* A later owner may have copied our RGB. Fail the complete current Present,
 * not merely the pixels that still bear our owner bit. */
static bool global_projectile91_finish_proof(void)
{
 if(!global_projectile91_contributed)return true;
 return global_projectile91_requested()&&!global_projectile91_fault&&!global_projectile91_call.live&&
  global_projectile91_surface_matches()&&global_projectile91_final_surface_matches()&&
  global_projectile91_source_matches(spriteSheet8)&&global_projectile91_palette_matches()&&
  global_projectile91_underlay_matches()&&(!global_projectile91_talon_dependency||
   (!global_talon_fault&&global_talon_source_matches(spriteSheet9)&&global_talon_palette_matches()));
}
static bool global_projectile91_compose(MirrorOutputKind kind,int lightx,int lighty)
{
 global_projectile91_end();
 if(!global_projectile91_frame||!global_projectile91_owner)return false;
 if(!global_projectile91_surface_matches()||!global_projectile91_final_surface_matches()) {
  global_projectile91_frame=global_projectile91_cached=false;return false;
 }
 bool valid=global_projectile91_requested()&&!global_projectile91_fault&&global_projectile91_surface_matches()&&global_projectile91_source_matches(spriteSheet8)&&
  global_projectile91_palette_matches()&&global_projectile91_underlay_matches()&&(!global_projectile91_talon_dependency||(!global_talon_fault&&global_talon_source_matches(spriteSheet9)&&global_talon_palette_matches()))&&(kind==MIRROR_OUTPUT_ORDINARY||kind==MIRROR_OUTPUT_NORMAL15_LOW_DETAIL||kind==MIRROR_OUTPUT_NORMAL15_NIGHT)&&
  VGAScreenSeg&&VGAScreenSeg->pixels&&VGAScreenSeg->w==320&&VGAScreenSeg->h==200&&VGAScreenSeg->pitch>=320&&
  VGAScreenSeg->format&&VGAScreenSeg->format->format==SDL_PIXELFORMAT_INDEX8;
 if(valid)for(int y=0;y<200;y++)if(memcmp(expected+y*320,(Uint8 *)game_screen->pixels+y*320,320)){valid=false;break;}
 /* Night is a native output operation, never a level or scene permission.
  * Its exact palette and complete final INDEX8 mapping are independently proven. */
 if(valid&&kind==MIRROR_OUTPUT_NORMAL15_NIGHT)valid=VGAScreenSeg->pitch==320&&normal15_palette()&&normal15_indices_match(kind,lightx,lighty);
 int d=game_probe_density;bool retained=false;
 for(int y=0;y<184;y++)for(int x=24;x<288;x++) {
  Uint8 before=((Uint8 *)game_screen->pixels)[y*320+x],after=((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x-24];
  bool night=kind==MIRROR_OUTPUT_NORMAL15_NIGHT;
  bool cell=valid&&after==(night?normal15_index(before,x-24,y,lightx,lighty):before);
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   int px=x*d+sx,py=y*d+sy;size_t n=(size_t)py*canvas->w+px;if(!global_projectile91_owner[n])continue;
   bool keep=cell&&(!reject_reason||!global_projectile91_foreign[n]);
   Uint32 *p=(Uint32 *)((Uint8 *)output->pixels+py*output->pitch)+px-24*d;
   if(keep){Uint32 color=((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px];
    *p=night?normal15_rgba(color,before,after,normal15_branch(x-24,y,lightx,lighty)<0):color;hd_owner[n]=1;retained=true;}
   else {*p=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x-24]);global_projectile91_owner[n]=hd_owner[n]=0;}
  }
 }
 if(retained||global_projectile91_contributed)memcpy(global_projectile91_output_palette,rgb_palette,sizeof(global_projectile91_output_palette));
 global_projectile91_cached=retained||(valid&&global_projectile91_contributed);global_projectile91_frame=false;return retained;
}
static bool global_projectile91_cache_source_matches(void)
{
 bool valid=!global_projectile91_fault&&global_projectile91_requested()&&global_projectile91_surface_matches()&&global_projectile91_final_surface_matches()&&global_projectile91_source_matches(spriteSheet8)&&(!global_projectile91_talon_dependency||(!global_talon_fault&&global_talon_source_matches(spriteSheet9)));
 if(valid)for(int y=0;y<200;y++)if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)){valid=false;break;}
 return valid;
}
static bool global_projectile91_cache_decline(void)
{ready=last_output_valid=have_fade_saved=false;fade_mode=0;global_projectile91_cached=false;return false;}
static void global_projectile91_check_cache(void)
{
 if(global_projectile91_cached&&(!global_projectile91_cache_source_matches()||
  memcmp(global_projectile91_output_palette,rgb_palette,sizeof(global_projectile91_output_palette))))global_projectile91_cache_decline();
}
static bool global_projectile91_fade_buffer_layout(void)
{
 SDL_Surface *s=fade_saved;int d=game_probe_density;
 if(!s||!s->pixels||!s->format||s->w!=320*d||s->h!=200*d||s->pitch<s->w*4||s->pitch%4||
  (uintptr_t)s->pixels%sizeof(Uint32)||s->format->format!=SDL_PIXELFORMAT_ARGB8888||
  s->format->BitsPerPixel!=32||s->format->BytesPerPixel!=4)return false;
 SDL_Surface *others[4]={game_screen,VGAScreenSeg,canvas,output};
 for(unsigned i=0;i<4;i++)if(!global_projectile91_disjoint(s,others[i]))return false;
 return true;
}
static bool global_projectile91_fade_buffer_safe(void)
{
 if(!global_projectile91_cached)return true;
 return (global_projectile91_cache_source_matches()&&global_projectile91_fade_buffer_layout())||global_projectile91_cache_decline();
}
static bool global_projectile91_fade_lease_matches(void)
{
 return global_projectile91_fade_buffer_layout()&&fade_saved==global_projectile91_fade_lease.surface&&
  fade_saved->pixels==global_projectile91_fade_lease.pixels&&fade_saved->format==global_projectile91_fade_lease.format&&fade_saved->pitch==global_projectile91_fade_lease.pitch;
}
static bool global_projectile91_fade_capture(void)
{
 if(!global_projectile91_cached)return true;
 if(!global_projectile91_cache_source_matches()||!global_projectile91_fade_buffer_layout()||
  (fade_mode==3&&!global_projectile91_fade_lease_matches()))return global_projectile91_cache_decline();
 global_projectile91_fade_lease.surface=fade_saved;global_projectile91_fade_lease.pixels=fade_saved->pixels;
 global_projectile91_fade_lease.format=fade_saved->format;global_projectile91_fade_lease.pitch=fade_saved->pitch;
 return true;
}
static bool global_projectile91_fade_step_valid(int steps)
{
 if(!global_projectile91_cached)return true;
 if(steps<=0||fade_mode<1||fade_mode>3||!have_fade_saved||!global_projectile91_cache_source_matches()||!global_projectile91_fade_lease_matches())return global_projectile91_cache_decline();
 /* The engine updates the indexed palette before this callback. Prove that
  * actual integer step, not equality with the deliberately older palette. */
 for(unsigned i=0;i<256;i++)for(int shift=0;shift<24;shift+=8) {
  int before=(global_projectile91_output_palette[i]>>shift)&255;
  int target=fade_mode==1?0:fade_mode==2?255:(int)((fade_saved_palette[i]>>shift)&255);
  if((int)((rgb_palette[i]>>shift)&255)!=before+(target-before)/steps)return global_projectile91_cache_decline();
 }
 return true;
}

static void global_projectile91_fade_palette(void)
{if(global_projectile91_cached)memcpy(global_projectile91_output_palette,rgb_palette,sizeof(global_projectile91_output_palette));}
static void global_projectile91_final_pixel(SDL_Surface *s,Uint8 *address)
{
 if((!global_projectile91_frame&&!global_projectile91_cached)||s!=VGAScreenSeg||!s||!s->pixels||!s->format||
  s->format->format!=SDL_PIXELFORMAT_INDEX8||s->w!=320||s->h!=200||s->pitch<320||!global_projectile91_surface_matches()||!global_projectile91_final_surface_matches()||!global_projectile91_owner)return;
 if(global_projectile91_cached&&have_fade_saved&&!global_projectile91_fade_lease_matches()){global_projectile91_cache_decline();return;}
 intptr_t offset=(intptr_t)address-(intptr_t)s->pixels;if(offset<0||offset>=(intptr_t)s->pitch*200)return;
 int y=(int)(offset/s->pitch),x=(int)(offset%s->pitch),d=game_probe_density;if(x>=264||y>=184)return;
 bool changed=false;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
  int px=(x+24)*d+sx,py=y*d+sy;size_t n=(size_t)py*canvas->w+px;if(!global_projectile91_owner[n])continue;
  global_projectile91_owner[n]=global_projectile91_foreign[n]=hd_owner[n]=cloud_owner[n]=0;changed=true;
  ((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px]=palette_rgb(*address);
  if(global_projectile91_cached) {
   ((Uint32 *)((Uint8 *)output->pixels+py*output->pitch))[px-24*d]=palette_rgb(*address);
   if(have_fade_saved&&fade_saved)
    ((Uint32 *)((Uint8 *)fade_saved->pixels+py*fade_saved->pitch))[px-24*d]=0xff000000u|(fade_saved_palette[*address]&0xffffffu);
  }
 }
 if(changed&&global_projectile91_cached)last_output_indices[y*320+x]=*address;
}
static void global_projectile91_final_rect(SDL_Surface *s,const SDL_Rect *r)
{
 if((!global_projectile91_frame&&!global_projectile91_cached)||s!=VGAScreenSeg||!s||!s->pixels)return;
 int64_t x=r?r->x:0,y=r?r->y:0,right=r?x+r->w:320,bottom=r?y+r->h:200;
 x=MAX(MAX(x,s->clip_rect.x),0);y=MAX(MAX(y,s->clip_rect.y),0);
 right=MIN(MIN(right,(int64_t)s->clip_rect.x+s->clip_rect.w),264);bottom=MIN(MIN(bottom,(int64_t)s->clip_rect.y+s->clip_rect.h),184);
 for(int yy=(int)y;yy<bottom;yy++)for(int xx=(int)x;xx<right;xx++)global_projectile91_final_pixel(s,(Uint8 *)s->pixels+yy*s->pitch+xx);
}

static bool global_projectile91_observe_blend(SDL_Surface *s,Uint8 *address)
{
 if(!global_projectile91_frame||s!=game_screen)return false;
 if(global_projectile91_call.live||!active)return true;
 if(!global_projectile91_surface_matches())return true;
 intptr_t off=(intptr_t)address-(intptr_t)s->pixels;if(off<0||off>=64000)return true;
 int x=(int)(off%320),y=(int)(off/320),d=game_probe_density;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)if(global_projectile91_owner[(y*d+sy)*canvas->w+x*d+sx])return true;
 return false;
}
