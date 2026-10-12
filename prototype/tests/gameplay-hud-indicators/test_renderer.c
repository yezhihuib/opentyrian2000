#define main static_hud_legacy_main
#include "../gameplay-hud/test_renderer.c"
#undef main
static Uint8 source_pic[64000],mode_sprites[2][80];
static void activate_indicators(const char *path,int d,bool has_frame,bool has_indicator)
{
 setup(d,path);expanded_test=false;
 read_fixture(path,"indicator-source.indices",source_pic,64000);memcpy(VGAScreenSeg->pixels,source_pic,64000);
 read_fixture(path,"indicator-modes.indices",mode_sprites,160);
 memset(sprite_table,0,sizeof(sprite_table));memset(font_ascii,255,sizeof(font_ascii));memset(options,0,sizeof(options));memset(shields,0,sizeof(shields));memset(player,0,sizeof(player));memset(levelName,0,sizeof(levelName));power=lastPower=0;
 sprite_table[OPTION_SHAPES].count=20;
 for(int i=0;i<2;i++)sprite_table[OPTION_SHAPES].sprite[18+i]=(Sprite){10,8,80,mode_sprites[i]};
 render_mirror_hud_start(VGAScreenSeg);
 assert(hud_gameplay==has_frame&&component_gameplay&&indicator_gameplay==has_indicator);
}
static void mode_original(int mode,bool stamp)
{
 for(int side=0;side<2;side++)for(int y=0;y<8;y++)
  memcpy((Uint8 *)VGAScreenSeg->pixels+(44+y)*320+285+17*side,mode_sprites[(mode-1)^side]+10*y,10);
 if(stamp)render_mirror_hud_mode_drawn(VGAScreenSeg,mode);
}
static unsigned owner_count(const Uint8 *p,size_t size)
{unsigned result=0;for(size_t i=0;i<size;i++)result+=p[i]!=0;return result;}
static void verify_visible(bool top,bool mode)
{
 int d=game_probe_density;
 for(unsigned int cell=0;cell<237;cell++) {
  int x,y;indicator_position(cell,&x,&y);bool owned=cell<21?top:mode;assert(indicator_output_owner[cell]==(owned?(cell<21?1:2):0));
  Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[y*320+x];
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   Uint32 want=palette_rgb(index);
   if(hud_output_owner[y*320+x])want=authored(x,y,sx,sy,d);
   if(owned) {const Uint8 *p=hud_indicators_sample(x,y,sx,sy,d,index);assert(p);want=0xff000000u|((Uint32)p[0]<<16)|((Uint32)p[1]<<8)|p[2];}
   assert(*pixel(output,x*d+sx,y*d+sy)==want);
  }
 }
}
static Uint32 *snapshot(SDL_Surface *s)
{size_t bytes=(size_t)s->pitch*s->h;Uint32 *result=malloc(bytes);assert(result);memcpy(result,s->pixels,bytes);return result;}
static void same_surface(SDL_Surface *s,const Uint32 *want)
{assert(memcmp(s->pixels,want,(size_t)s->pitch*s->h)==0);}
static void restore_target(SDL_Color target[256],const Uint32 palette[256])
{for(int i=0;i<256;i++)target[i]=(SDL_Color){palette[i]>>16,palette[i]>>8,palette[i],255};}
/* Exact whole-image counterfactual: compose/fade with no upper layer, then
 * repeat with HUL1 and remove it at any intermediate black/white/restore step. */
static void fade_counterfactual(const char *path,int d,int solid,int removal,bool lower_first,bool frame_present)
{
 Uint32 *want_current=NULL,*want_saved=NULL;Uint32 palette[256];
 for(int upper=0;upper<2;upper++) {
  activate_indicators(path,d,frame_present,true);mode_original(2,true);
  if(!upper)indicators_reset();
  frame(true,true);memcpy(palette,rgb_palette,sizeof(palette));
  if(upper)assert(owner_count(indicator_under_owner,82)==(frame_present?82u:0u));
  SDL_Color target={(Uint8)solid,(Uint8)solid,(Uint8)solid,255};render_mirror_fade_start(NULL,&target,0,255);
  int phase=0;
  for(int step=7;step>=1;step--) {
   palette_step(solid,step,NULL);render_mirror_fade_step(step);++phase;
   if(phase==removal)break;
  }
  if(removal>7) {
   SDL_Color restore[256];restore_target(restore,palette);render_mirror_fade_start(restore,NULL,0,255);
   for(int step=5;step>=1;step--) {palette_step(0,step,palette);render_mirror_fade_step(step);++phase;if(phase==removal)break;}
  }
  if(lower_first)hud_frame_reset();
  if(upper) {
   unsigned alloc=allocations;indicators_reset();indicators_reset();assert(allocations==alloc);
   assert(!indicators_owned());same_surface(output,want_current);same_surface(fade_saved,want_saved);
   assert(last_output_valid&&have_fade_saved);
   if(fade_mode){palette_step(solid,1,NULL);render_mirror_fade_step(1);assert(ready);}
  } else {want_current=snapshot(output);want_saved=snapshot(fade_saved);}
 }
 free(want_current);free(want_saved);
}
static void lifecycle(const char *path,int d)
{
 activate_indicators(path,d,true,true);frame(true,true);verify_visible(true,false);assert(!hud_indicators_mode_ready());
 mode_original(1,false);frame(true,true);verify_visible(true,false); /* pixels cannot grant event */
 render_mirror_hud_mode_drawn(VGAScreenSeg,1);frame(true,true);verify_visible(true,true);
 assert(owner_count(indicator_under_owner,82)==82);unsigned alloc=allocations;
 for(int mode=1;mode<=2;mode++){mode_original(mode,true);frame(true,true);verify_visible(true,true);assert(allocations==alloc);}
 /* One changed index rejects the entire corresponding finite group. */
 ((Uint8 *)VGAScreenSeg->pixels)[44*320+300]^=1;frame(true,true);verify_visible(true,false);assert(!hud_indicators_mode_ready());
 memcpy((Uint8 *)VGAScreenSeg->pixels+44*320+300,source_pic+44*320+300,1);mode_original(2,false);frame(true,true);verify_visible(true,false);
 mode_original(2,true);frame(true,true);verify_visible(true,true);
 ((Uint8 *)VGAScreenSeg->pixels)[4*320+269]^=1;frame(true,true);verify_visible(false,true);
 ((Uint8 *)VGAScreenSeg->pixels)[4*320+269]^=1;frame(true,true);verify_visible(true,true);
 for(int modal=0;modal<3;modal++) {
  uint64_t gen=indicator_generation;render_mirror_hud_suspend();render_mirror_hud_suspend();assert(indicator_suspended&&gen==indicator_generation&&!indicators_owned()&&hud_indicators_mode_ready());
  render_mirror_present(NULL,VGAScreenSeg,NULL);frame(true,true);verify_visible(true,true);
 }
 render_mirror_release_texture();assert(indicator_suspended&&indicator_gameplay);frame(true,true);verify_visible(true,true);
 /* Partial lower ownership captured exactly rather than assuming all82. */
 render_mirror_begin();scene_pixel();upscale(output,VGAScreenSeg);assert(hud_compose());
 unsigned n=0;for(int y=44;y<52;y++)for(int x=285;x<312;x++)if(indicator_overlap(x,y)>=0&&n++%2==0){hud_output_owner[y*320+x]=0;for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)*pixel(output,x*d+sx,y*d+sy)=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[y*320+x]);}
 assert(indicators_compose());assert(owner_count(indicator_under_owner,82)==41);
 memcpy(last_output_indices,VGAScreenSeg->pixels,64000);memcpy(indicator_output_palette,rgb_palette,sizeof(rgb_palette));indicators_clear_cached(3);verify_visible(false,false);
 /* Modes revoke until a fresh grant. */
 for(int m=0;m<2;m++){activate_indicators(path,d,true,true);mode_original(1,true);frame(true,true);if(m)galagaMode=true;else twoPlayerMode=true;render_mirror_present(NULL,VGAScreenSeg,NULL);assert(!indicator_gameplay&&!hud_indicators_ready());twoPlayerMode=galagaMode=false;frame(true,true);assert(!indicator_gameplay);}
 activate_indicators(path,d,true,true);mode_original(1,true);frame(true,true);render_mirror_hud_mode_drawn(VGAScreenSeg,3);assert(!hud_indicators_mode_ready());frame(true,true);verify_visible(true,false);
 activate_indicators(path,d,true,true);mode_original(1,true);frame(true,false);assert(!indicators_owned());
 activate_indicators(path,d,true,true);mode_original(1,true);rgb_palette[68]^=1;frame(true,true);assert(!indicators_owned()&&hud_gameplay);
 activate_indicators(path,d,true,true);mode_original(1,true);frame(true,true);render_mirror_hud_reset();assert(!indicator_gameplay&&!hud_indicators_ready());frame(true,true);assert(!indicators_owned());
}
static void distrust(const char *path)
{
 for(int f=0;f<17;f++) {
  activate_indicators(path,4,true,true);mode_original(1,true);frame(true,true);
  SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);palette_step(0,3,NULL);render_mirror_fade_step(3);
  SDL_Surface *old=VGAScreenSeg;void *pixels=old->pixels;SDL_PixelFormat *format=old->format;int pitch=old->pitch;
  if(f==0){VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,0);memcpy(VGAScreenSeg->pixels,old->pixels,64000);SDL_FreeSurface(old);}
  if(f==1){old->pixels=malloc(64000);memcpy(old->pixels,pixels,64000);free(pixels);}
  if(f==2){old->format=malloc(sizeof(*format));*old->format=*format;free(format);}
  if(f==3)old->pitch++;
  if(f==4)old->w--;
  if(f==5)old->h--;
  if(f==6)old->format->BitsPerPixel=4;
  if(f==7)old->format->BytesPerPixel=4;
  if(f==8)VGAScreenSeg=NULL;
  if(f==9)((Uint8 *)old->pixels)[0]^=1;
  if(f==10)rgb_palette[0]^=1;
  if(f==11)indicator_under_generation++;
  if(f==12)indicator_under_density=8;
  if(f==13)hud_output_owner[indicator_overlap_positions[0]]=0;
  if(f==14)hud_saved_owner[indicator_overlap_positions[0]]=0;
  if(f==15)indicator_output_generation++;
  if(f==16)indicator_saved_generation++;
  indicators_reset();assert(!ready&&!last_output_valid&&!have_fade_saved&&!fade_mode&&!indicator_source_surface);
  if(f>=3&&f<=7){old->pitch=pitch;old->w=320;old->h=200;old->format->BitsPerPixel=8;old->format->BytesPerPixel=1;}
  if(f==8)VGAScreenSeg=old;
 }
 /* Mutated runtime sprite source is independently revoked, even if screen
  * pixels still coincide. No lower static/HUC1 guard relaxation is required. */
 activate_indicators(path,4,true,true);mode_original(1,true);frame(true,true);mode_sprites[0][12]^=1;render_mirror_present(NULL,VGAScreenSeg,NULL);assert(!indicator_gameplay&&component_gameplay);
}
int main(int argc,char **argv)
{
 assert(argc==2);char path[1024];
 for(int d=4;d<=8;d+=4) {
  lifecycle(argv[1],d);
  for(int solid=0;solid<=255;solid+=255)for(int removal=1;removal<=12;removal++)for(int lower=0;lower<2;lower++)fade_counterfactual(argv[1],d,solid,removal,lower,true);
  snprintf(path,sizeof(path),"%s/no-frame",argv[1]);for(int solid=0;solid<=255;solid+=255)for(int removal=1;removal<=12;removal++)fade_counterfactual(path,d,solid,removal,false,false);
  for(int bad=0;bad<2;bad++){snprintf(path,sizeof(path),"%s/%s",argv[1],bad?"corrupt":"missing");activate_indicators(path,d,true,false);mode_original(1,true);frame(true,true);verify_visible(false,false);assert(hud_gameplay&&component_gameplay);}
 }
 distrust(argv[1]);cleanup();puts("PASS HUL1 production renderer: 82 exact current/saved underlays, 144 rounded-fade counterfactuals, independent fallbacks, event/lease/mode/modal guards and no per-frame allocation");return 0;
}
