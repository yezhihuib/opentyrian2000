/* Family-only HUD material adapter. Native semantic writers remain the sole
 * authority for meter history, shield state and paired mode draws. No scene
 * lease, text-glyph lease or indexed pixel is changed by this adapter. */
#include "gameplay_hud_components.h"
#include "gameplay_hud_meters.h"
#include "gameplay_hud_indicators.h"
#include "gameplay_hud_fixed_text.h"
static bool family_static_hud_current(void);
static bool fdh_captured,fdh_words,fdh_meters,fdh_indicators,fdh_text;
static bool fdh_labels,fdh_shield,fdh_top,fdh_mode,fdh_groups[3];
static unsigned fdh_meter_bits;
static bool fdh_requested(void)
{
 const char *e=getenv("BUILDING313_FAMILY_DYNAMIC_HUD_ENABLE");
 return family_static_hud_requested()&&e&&!strcmp(e,"1");
}
static void fdh_reset(void)
{
 if(fdh_captured){hud_components_forget_source();hud_meters_forget_source();
  hud_indicators_forget_source();hud_fixed_text_forget_source();}
 fdh_captured=fdh_words=fdh_meters=fdh_indicators=fdh_text=false;
 fdh_labels=fdh_shield=fdh_top=fdh_mode=false;fdh_meter_bits=0;
 memset(fdh_groups,0,sizeof fdh_groups);
}
static bool fdh_modes(void)
{
 Uint8 indices[2][80],opaque[2][80];
 for(unsigned i=0;i<2;i++)if(!hud_sprite_decode(OPTION_SHAPES,18+i,10,8,indices[i],opaque[i])||
  sprite_table[OPTION_SHAPES].sprite[18+i].width!=10||sprite_table[OPTION_SHAPES].sprite[18+i].height!=8)return false;
 return hud_indicators_verify_modes((const Uint8 (*)[80])indices,(const Uint8 (*)[80])opaque);
}
static void fdh_start(SDL_Surface *source)
{
 fdh_reset();if(!fdh_requested())return;
 const char *root="assets/hd/shared-ui-v1";
 fdh_words=hud_components_load(root)&&hud_components_capture(source->pixels,source->pitch);
 fdh_meters=hud_meters_load(root)&&hud_meters_capture(source->pixels,source->pitch);
 fdh_text=hud_fixed_text_load(root)&&hud_fixed_text_capture(source->pixels,source->pitch);
 Uint8 indices[2][80],opaque[2][80];bool modes=true;
 for(unsigned i=0;i<2;i++)if(!hud_sprite_decode(OPTION_SHAPES,18+i,10,8,indices[i],opaque[i])||
  sprite_table[OPTION_SHAPES].sprite[18+i].width!=10||sprite_table[OPTION_SHAPES].sprite[18+i].height!=8)modes=false;
 fdh_indicators=modes&&hud_indicators_load(root)&&hud_indicators_capture(source->pixels,source->pitch,
  (const Uint8 (*)[80])indices,(const Uint8 (*)[80])opaque);
 fdh_captured=fdh_words||fdh_meters||fdh_text||fdh_indicators;
}
static bool fdh_current(void)
{
 if(!fdh_captured)return false;
 if(!fdh_requested()||!family_scope()||!family_static_hud_captured||
    !family_indexed(VGAScreenSeg)||VGAScreenSeg!=family_static_hud_surface||
    VGAScreenSeg->pixels!=family_static_hud_pixels||VGAScreenSeg->format!=family_static_hud_format||
    !hud_runtime_compatible(true)){fdh_reset();return false;}
 return true;
}
static void fdh_mode_drawn(SDL_Surface *s,unsigned mode)
{
 if(!fdh_current()||!fdh_indicators)return;
 if(s!=VGAScreenSeg||!fdh_modes()||(mode!=1&&mode!=2)){hud_indicators_mode_wiped();return;}
 hud_indicators_mode_drawn((int)mode);
}
static void fdh_shield_wiped(SDL_Surface *s)
{(void)s;if(fdh_captured)hud_components_shield_wiped();}
static void fdh_shield_drawn(SDL_Surface *s,unsigned value,unsigned maximum)
{
 if(!fdh_current()||!fdh_words)return;
 if(s!=VGAScreenSeg||value>maximum||maximum>28){hud_components_shield_wiped();return;}
 hud_components_shield_drawn((int)value,(int)maximum);
}
static void fdh_meter_begin(SDL_Surface *s,SDL_Surface *draw,unsigned kind,unsigned a,unsigned b)
{
 if(!fdh_current()||!fdh_meters)return;
 unsigned bits=hud_meters_event_bits(kind);if(!bits)bits=HUD_METERS_ALL;
 if(s!=VGAScreenSeg||draw!=VGAScreenSeg){hud_meters_revoke(bits);return;}
 hud_meters_write_begin(kind,a,b);
}
static void fdh_meter_end(SDL_Surface *s,unsigned kind)
{
 if(!fdh_current()||!fdh_meters)return;
 unsigned bits=hud_meters_event_bits(kind);if(!bits)bits=HUD_METERS_ALL;
 if(s!=VGAScreenSeg){hud_meters_revoke(bits);return;}
 hud_meters_write_end(kind,s->pixels,s->pitch);
}
static bool fdh_prepare(void)
{
 fdh_labels=fdh_shield=fdh_top=fdh_mode=false;fdh_meter_bits=0;memset(fdh_groups,0,sizeof fdh_groups);
 if(!fdh_current())return false;
 fdh_labels=fdh_words&&hud_components_palette_matches(rgb_palette);
 if(fdh_labels){
  fdh_shield=hud_components_shield_matches(VGAScreenSeg->pixels,VGAScreenSeg->pitch);
  if(!fdh_shield)hud_components_shield_wiped();
 }
 if(fdh_meters&&hud_meters_palette_matches(rgb_palette))fdh_meter_bits=hud_meters_prepare(VGAScreenSeg->pixels,VGAScreenSeg->pitch);
 if(fdh_indicators&&hud_indicators_palette_matches(rgb_palette)&&fdh_modes()){
  fdh_top=hud_indicators_top_matches(VGAScreenSeg->pixels,VGAScreenSeg->pitch);
  fdh_mode=hud_indicators_mode_matches(VGAScreenSeg->pixels,VGAScreenSeg->pitch);
  if(!fdh_mode)hud_indicators_mode_wiped();
 }
 if(fdh_text&&hud_fixed_text_palette_matches(rgb_palette))for(unsigned i=0;i<3;i++)fdh_groups[i]=hud_fixed_text_group_matches(i,VGAScreenSeg->pixels,VGAScreenSeg->pitch);
 return true;
}
static const Uint8 *fdh_sample(int x,int y,int sx,int sy,Uint8 index)
{
 const Uint8 *p=NULL;
 if(fdh_labels){
  p=hud_components_label_sample(x,y,sx,sy,8,index);
  if(!p&&fdh_shield)p=hud_components_shield_sample(x,y,sx,sy,8,index);
 }
 if(!p&&fdh_meter_bits)p=hud_meters_sample(x,y,sx,sy,8,index);
 if(!p&&((fdh_top&&x>=269&&x<276&&y>=4&&y<7)||
         (fdh_mode&&x>=285&&x<312&&y>=44&&y<52)))p=hud_indicators_sample(x,y,sx,sy,8,index);
 int cell=hud_fixed_text_cell(x,y);
 if(!p&&cell>=0&&fdh_groups[cell<95?0:cell<245?1:2])p=hud_fixed_text_sample((unsigned)cell,sx,sy,8);
 return p;
}

/* Read-only receipt for observers. No preparation, acquisition or renewal. */
const uint8_t *render_mirror_family_dynamic_hud_sample(int x,int y,int sx,int sy,uint8_t index)
{
 if(!fdh_captured||!fdh_requested()||!family_static_hud_captured||
    family_static_hud_suspended||!family_scope()||!family_indexed(VGAScreenSeg)||
    VGAScreenSeg!=family_static_hud_surface||VGAScreenSeg->pixels!=family_static_hud_pixels||
    VGAScreenSeg->format!=family_static_hud_format||x<0||x>=320||y<0||y>=200||sx<0||sx>=8||sy<0||sy>=8||
    ((const Uint8 *)VGAScreenSeg->pixels)[y*320+x]!=index)return NULL;
 return fdh_sample(x,y,sx,sy,index);
}
