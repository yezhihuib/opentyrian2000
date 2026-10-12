#define main static_hud_legacy_main
#include "../gameplay-hud/test_renderer.c"
#undef main
static Uint8 component_source[64000];
static void activate_components(const char *directory,int density)
{
 expanded_test=false;setup(density,directory);
 read_fixture(directory,"component-source.indices",component_source,64000);
 memcpy(VGAScreenSeg->pixels,component_source,64000);
 render_mirror_hud_start(VGAScreenSeg);
 assert(hud_gameplay&&component_gameplay&&hud_components_ready()&&!hud_components_shield_ready());
}
static void shield_original(unsigned s,unsigned m,bool stamp)
{
 for(int y=137;y<195;y++)for(int x=270;x<279;x++) {
  unsigned band=(unsigned)(194-y)/2;
  Uint8 value=band>s?0:(Uint8)(146+(band<3?0:1+(band-3)/2));
  if(s!=m&&y==193-(int)(2*m))value=68;
  ((Uint8 *)VGAScreenSeg->pixels)[y*320+x]=value;
 }
 if(stamp)render_mirror_hud_shield_drawn(VGAScreenSeg,s,m);
}
static unsigned component_count(unsigned type)
{unsigned n=0;for(int i=0;i<64000;i++)n+=component_output_owner[i]==type;return n;}
static Uint32 rgba_rgb(const Uint8 *p)
{return 0xff000000u|((Uint32)p[0]<<16)|((Uint32)p[1]<<8)|p[2];}
static void verify_components(bool labels,bool bar,bool scene)
{
 int d=game_probe_density;
 for(int y=0;y<200;y++)for(int x=0;x<320;x++) {
  Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[y*320+x];
  const Uint8 *label=labels?hud_components_label_sample(x,y,0,0,d,index):NULL;
  const Uint8 *fill=bar?hud_components_shield_sample(x,y,0,0,d,index):NULL;
  unsigned kind=label?1:fill?2:0;assert(component_output_owner[y*320+x]==kind);
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   Uint32 want=palette_rgb(index);
   if(x<264&&y<184)want=palette_rgb(7);
   const Uint8 *p=gameplay_hud_sample(x,y,sx,sy,d,index);
   if(hud_output_owner[y*320+x]){assert(p);want=rgba_rgb(p);}
   if(kind==1)want=rgba_rgb(hud_components_label_sample(x,y,sx,sy,d,index));
   if(kind==2)want=rgba_rgb(hud_components_shield_sample(x,y,sx,sy,d,index));
   if(scene&&x==30&&y==20&&sx==0&&sy==0)want=0xffdc51a3u;
   assert(*pixel(output,x*d+sx,y*d+sy)==want);
  }
 }
}
static void suite(const char *directory,int d)
{
 activate_components(directory,d);frame(true,true);assert(component_count(1)==350&&component_count(2)==0);verify_components(true,false,true);
 unsigned alloc=allocations;
 for(unsigned s=0;s<=28;s++){
  render_mirror_hud_shield_wiped(VGAScreenSeg);shield_original(s,28,true);frame(true,true);
  assert(component_count(1)==350&&component_count(2)==18*(s+1));assert(alloc==allocations);
  if(s==0||s==14||s==28)verify_components(true,true,true);
 }
 /* Foreign bar writes revoke only the bar; frame and labels remain owned. */
 ((Uint8 *)VGAScreenSeg->pixels)[150*320+270]^=1;frame(true,true);
 assert(!hud_components_shield_ready()&&component_count(1)==350&&component_count(2)==0&&hud_gameplay);verify_components(true,false,true);
 shield_original(10,10,false);frame(true,true);assert(component_count(2)==0);
 render_mirror_hud_shield_drawn(VGAScreenSeg,10,10);frame(true,true);verify_components(true,true,true);
 /* Label source-index changes leave that whole logical block original. */
 ((Uint8 *)VGAScreenSeg->pixels)[5*320+285]^=1;frame(true,true);assert(component_count(1)==349);
 memcpy((Uint8 *)VGAScreenSeg->pixels+5*320+285,component_source+5*320+285,1);frame(true,true);
 /* No notification means no newly manufactured fill, including stale display. */
 render_mirror_hud_shield_wiped(VGAScreenSeg);
 for(int y=137;y<195;y++)memset((Uint8 *)VGAScreenSeg->pixels+y*320+270,0,9);
 frame(true,true);assert(component_count(2)==0);verify_components(true,false,true);
 shield_original(0,10,true);frame(true,true);assert(component_count(2)==18);
 player[0].shield=10;frame(true,true);assert(component_count(2)==18); /* displayed stamp stays zero */
 /* Three real modal entry types share this suspension path; only begin resumes. */
 for(int modal=0;modal<3;modal++){
  uint64_t generation=component_generation;render_mirror_hud_suspend();assert(component_suspended&&component_generation==generation&&hud_components_shield_ready());
  assert(component_count(1)==0&&component_count(2)==0);render_mirror_present(NULL,VGAScreenSeg,NULL);
  frame(true,true);assert(!component_suspended&&component_count(1)==350&&component_count(2)==18);
 }
 for(unsigned solid=0;solid<=255;solid+=255){
  Uint32 palette[256];memcpy(palette,rgb_palette,sizeof(palette));
  SDL_Color target={solid,solid,solid,255};render_mirror_fade_start(NULL,&target,0,255);
  for(int step=3;step;step--){
   Uint32 label=*pixel(output,285*d,5*d),bar=*pixel(output,270*d,193*d),want=solid?0xffffffffu:0xff000000u;
   palette_step(solid,step,NULL);render_mirror_fade_step(step);
   assert(*pixel(output,285*d,5*d)==channel_step(label,want,step));assert(*pixel(output,270*d,193*d)==channel_step(bar,want,step));
   assert(render_mirror_present(NULL,VGAScreenSeg,NULL));assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));
  }
  SDL_Color restore[256];for(int i=0;i<256;i++)restore[i]=(SDL_Color){palette[i]>>16,palette[i]>>8,palette[i],255};
  render_mirror_fade_start(restore,NULL,0,255);
  for(int step=3;step;step--){palette_step(0,step,palette);render_mirror_fade_step(step);}
  verify_components(true,true,true);if(solid==255)break;
 }
 /* Wipe midway through a fade removes bar in both caches, not labels/frame. */
 SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);palette_step(0,3,NULL);render_mirror_fade_step(3);
 Uint32 scene=*pixel(output,30*d,20*d),label=*pixel(output,285*d,5*d),frame_rgb=*pixel(output,264*d,0);
 Uint32 saved_scene=*pixel(fade_saved,30*d,20*d),saved_label=*pixel(fade_saved,285*d,5*d);
 render_mirror_hud_shield_wiped(VGAScreenSeg);render_mirror_hud_shield_wiped(VGAScreenSeg);
 assert(*pixel(output,30*d,20*d)==scene&&*pixel(output,285*d,5*d)==label&&*pixel(output,264*d,0)==frame_rgb);
 assert(*pixel(fade_saved,30*d,20*d)==saved_scene&&*pixel(fade_saved,285*d,5*d)==saved_label);
 assert(component_count(1)==350&&component_count(2)==0&&have_fade_saved);
 assert(*pixel(output,270*d,194*d)==palette_rgb(146));
 /* Component-only reset never strips the independent frame or scene. */
 components_reset();assert(!component_gameplay&&hud_gameplay&&last_output_valid&&have_fade_saved);
 assert(*pixel(output,264*d,0)==frame_rgb&&*pixel(output,30*d,20*d)==scene);
 activate_components(directory,d);shield_original(5,10,true);frame(true,true);
 hud_frame_reset();assert(component_gameplay&&!hud_gameplay&&last_output_valid);verify_components(true,true,true);
 /* Mode/PIC/lease revocation needs a fresh grant, not coincident index values. */
 for(int mode=0;mode<2;mode++){
  activate_components(directory,d);shield_original(5,10,true);frame(true,true);
  if(mode)galagaMode=true;else twoPlayerMode=true;render_mirror_present(NULL,VGAScreenSeg,NULL);
  assert(!component_gameplay&&!hud_components_ready());twoPlayerMode=galagaMode=false;frame(true,true);assert(!component_gameplay);
 }
 activate_components(directory,d);shield_original(5,10,true);frame(true,true);
 SDL_Surface *old=VGAScreenSeg;VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,0);memcpy(VGAScreenSeg->pixels,old->pixels,64000);SDL_FreeSurface(old);
 render_mirror_hud_suspend();assert(!component_gameplay&&!ready&&!last_output_valid);
 activate_components(directory,d);shield_original(5,10,true);frame(true,true);
 uint64_t gen=component_generation;render_mirror_release_texture();assert(component_gameplay&&component_suspended&&component_generation==gen);
 frame(true,true);verify_components(true,true,true);
 render_mirror_hud_reset();assert(!component_gameplay&&!hud_components_ready());frame(true,true);assert(!component_count(1)&&!component_count(2));
 /* Initial palette incompatibility is component-only, even with static frame. */
 activate_components(directory,d);rgb_palette[68]^=1;frame(true,true);assert(hud_output_generation&&component_count(1)==0&&component_count(2)==0&&component_gameplay);
 activate_components(directory,d);shield_original(5,10,true);frame(true,false);assert(!component_count(1)&&!component_count(2));
 activate_components(directory,d);shield_original(5,10,true);frame(true,true);render_mirror_hud_shutdown();assert(!component_gameplay&&!hud_components_ready());
}
static void component_lease_and_fallback(const char *directory)
{
 for(int field=0;field<9;field++) {
  activate_components(directory,4);shield_original(5,10,true);frame(true,true);
  SDL_Surface *old=VGAScreenSeg;void *pixels=old->pixels;SDL_PixelFormat *format=old->format;
  int pitch=old->pitch;
  if(field==0){VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,0);memcpy(VGAScreenSeg->pixels,old->pixels,64000);SDL_FreeSurface(old);}
  if(field==1){old->pixels=malloc(64000);memcpy(old->pixels,pixels,64000);free(pixels);}
  if(field==2){old->format=malloc(sizeof(*format));*old->format=*format;free(format);}
  if(field==3)old->pitch++;
  if(field==4)old->w--;
  if(field==5)old->h--;
  if(field==6)old->format->BitsPerPixel=4;
  if(field==7)old->format->BytesPerPixel=4;
  if(field==8)VGAScreenSeg=NULL;
  render_mirror_hud_suspend();assert(!component_gameplay&&!component_source_surface&&!hud_components_ready()&&!ready&&!last_output_valid);
  if(field>=3&&field<=7){old->pitch=pitch;old->w=320;old->h=200;old->format->BitsPerPixel=8;old->format->BytesPerPixel=1;}
  if(field==8)VGAScreenSeg=old;
 }
 for(int i=0;i<2;i++) {
  char path[1024];snprintf(path,sizeof(path),"%s/%s",directory,i?"corrupt":"missing");setup(4,path);expanded_test=false;
  read_fixture(path,"component-source.indices",VGAScreenSeg->pixels,64000);render_mirror_hud_start(VGAScreenSeg);
  assert(hud_gameplay&&!component_gameplay);frame(true,true);verify_components(false,false,true);
 }
}
int main(int argc,char **argv)
{assert(argc==2);component_lease_and_fallback(argv[1]);for(int d=4;d<=8;d+=4)suite(argv[1],d);cleanup();puts("PASS component production compositor: exact label/fill ownership, finite states, independent fallback, no allocation, lifecycle and black/white/restore caches");return 0;}
