#define main static_hud_legacy_main
#include "../gameplay-hud/test_renderer.c"
#undef main
static Uint8 fixed_source[64000],modes[160];
static void activate_fixed(const char *path,int d,bool fixed,bool others)
{
 setup(d,path);expanded_test=false;
 read_fixture(path,"indicator-source.indices",fixed_source,64000);memcpy(VGAScreenSeg->pixels,fixed_source,64000);
 read_fixture(path,"indicator-modes.indices",modes,160);
 memset(sprite_table,0,sizeof(sprite_table));memset(font_ascii,255,sizeof(font_ascii));memset(options,0,sizeof(options));memset(shields,0,sizeof(shields));memset(player,0,sizeof(player));memset(levelName,0,sizeof(levelName));power=lastPower=0;
 sprite_table[OPTION_SHAPES].count=20;
 for(int i=0;i<2;i++)sprite_table[OPTION_SHAPES].sprite[18+i]=(Sprite){10,8,80,modes+i*80};
 /* PIC3 grant precedes ordinary palette installation. */
 Uint32 normal=rgb_palette[0];rgb_palette[0]^=1;render_mirror_hud_start(VGAScreenSeg);rgb_palette[0]=normal;
 assert(fixed_text_gameplay==fixed&&hud_gameplay==others&&component_gameplay==others&&indicator_gameplay==others);
 for(int side=0;side<2;side++)for(int y=0;y<8;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+(44+y)*320+285+17*side,modes+80*side+10*y,10);
 render_mirror_hud_mode_drawn(VGAScreenSeg,1);
}
static unsigned fixed_count(void)
{unsigned n=0;for(unsigned i=0;i<370;i++)n+=fixed_text_output_owner[i]!=0;return n;}
static void verify_fixed(unsigned groups)
{
 for(unsigned i=0;i<370;i++) {
  int x,y;assert(hud_fixed_text_position(i,&x,&y));unsigned g=i<95?0:i<245?1:2;bool owned=(groups&(1u<<g))!=0;assert(fixed_text_output_owner[i]==owned);
  for(int sy=0;sy<game_probe_density;sy++)for(int sx=0;sx<game_probe_density;sx++) {
   Uint32 want=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[y*320+x]);
   if(owned){const Uint8 *p=hud_fixed_text_sample(i,sx,sy,game_probe_density);assert(p);want=0xff000000u|((Uint32)p[0]<<16)|((Uint32)p[1]<<8)|p[2];}
   assert(*pixel(output,x*game_probe_density+sx,y*game_probe_density+sy)==want);
  }
 }
}
static Uint32 *save_surface(SDL_Surface *s)
{size_t size=(size_t)s->pitch*s->h;Uint32 *p=malloc(size);assert(p);memcpy(p,s->pixels,size);return p;}
static void assert_surface(SDL_Surface *s,Uint32 *p)
{assert(memcmp(s->pixels,p,(size_t)s->pitch*s->h)==0);}
static void counterfactual(const char *path,int d,int solid,int removal)
{
 Uint32 *want=NULL,*saved=NULL,normal[256];
 for(int with=0;with<2;with++) {
  activate_fixed(path,d,true,true);if(!with)fixed_text_reset();frame(true,true);memcpy(normal,rgb_palette,sizeof(normal));
  SDL_Color color={(Uint8)solid,(Uint8)solid,(Uint8)solid,255};render_mirror_fade_start(NULL,&color,0,255);int phase=0;
  for(int step=7;step;step--){palette_step(solid,step,NULL);render_mirror_fade_step(step);if(++phase==removal)break;}
  if(removal>7){SDL_Color target[256];for(int i=0;i<256;i++)target[i]=(SDL_Color){normal[i]>>16,normal[i]>>8,normal[i],255};render_mirror_fade_start(target,NULL,0,255);for(int step=5;step;step--){palette_step(0,step,normal);render_mirror_fade_step(step);if(++phase==removal)break;}}
  if(with){fixed_text_reset();fixed_text_reset();assert_surface(output,want);assert_surface(fade_saved,saved);assert(last_output_valid&&have_fade_saved&&!fixed_count());}
  else {want=save_surface(output);saved=save_surface(fade_saved);}
 }
 free(want);free(saved);
}
static void suite(const char *path,int d)
{
 activate_fixed(path,d,true,true);frame(true,true);assert(fixed_count()==370);verify_fixed(7);unsigned allocations_before=allocations;
 for(unsigned g=0;g<3;g++){int x,y;hud_fixed_text_position(g==0?0:g==1?95:245,&x,&y);((Uint8 *)VGAScreenSeg->pixels)[y*320+x]^=1;frame(true,true);verify_fixed(7^(1u<<g));((Uint8 *)VGAScreenSeg->pixels)[y*320+x]^=1;frame(true,true);verify_fixed(7);assert(allocations==allocations_before);}
 /* Removing any other family cannot discard an independently valid HUT1 cache. */
 indicators_reset();components_reset();hud_frame_reset();assert(last_output_valid&&fixed_count()==370);verify_fixed(7);
 for(int modal=0;modal<3;modal++){uint64_t gen=fixed_text_generation;render_mirror_hud_suspend();render_mirror_hud_suspend();assert(fixed_text_gameplay&&fixed_text_suspended&&fixed_text_generation==gen&&!fixed_count());frame(true,true);verify_fixed(7);}
 render_mirror_release_texture();assert(fixed_text_gameplay&&fixed_text_suspended);frame(true,true);verify_fixed(7);
 for(int mode=0;mode<2;mode++){activate_fixed(path,d,true,true);frame(true,true);if(mode)galagaMode=true;else twoPlayerMode=true;render_mirror_present(NULL,VGAScreenSeg,NULL);assert(!fixed_text_gameplay&&!hud_fixed_text_ready());twoPlayerMode=galagaMode=false;frame(true,true);assert(!fixed_count());}
 activate_fixed(path,d,true,true);rgb_palette[68]^=1;frame(true,true);assert(!fixed_count()&&hud_gameplay);
 activate_fixed(path,d,true,true);frame(true,false);assert(!fixed_count());
 activate_fixed(path,d,true,true);frame(true,true);render_mirror_hud_reset();assert(!fixed_text_gameplay&&!hud_fixed_text_ready());frame(true,true);assert(!fixed_count());
 for(int bad=0;bad<3;bad++){char p[1200];snprintf(p,sizeof(p),"%s/%s",path,bad==0?"no-fixed":bad==1?"bad-fixed":"fixed-only");activate_fixed(p,d,bad==2,bad!=2);frame(true,true);assert(fixed_count()==(bad==2?370:0));verify_fixed(bad==2?7:0);}
}
static void distrust(const char *path)
{
 for(int fault=0;fault<13;fault++) {
  activate_fixed(path,4,true,true);frame(true,true);SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);palette_step(0,3,NULL);render_mirror_fade_step(3);
  SDL_Surface *old=VGAScreenSeg;void *pixels=old->pixels;SDL_PixelFormat *format=old->format;int pitch=old->pitch;
  if(fault==0){VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,0);memcpy(VGAScreenSeg->pixels,pixels,64000);SDL_FreeSurface(old);}
  if(fault==1){old->pixels=malloc(64000);memcpy(old->pixels,pixels,64000);free(pixels);}
  if(fault==2){old->format=malloc(sizeof(*format));*old->format=*format;free(format);}
  if(fault==3)old->pitch++;
  if(fault==4)old->w--;
  if(fault==5)old->h--;
  if(fault==6)old->format->BitsPerPixel=4;
  if(fault==7)old->format->BytesPerPixel=4;
  if(fault==8)VGAScreenSeg=NULL;
  if(fault==9)((Uint8 *)old->pixels)[0]^=1;
  if(fault==10)rgb_palette[0]^=1;
  if(fault==11)fixed_text_output_generation++;
  if(fault==12)fixed_text_saved_generation++;
  fixed_text_reset();assert(!ready&&!last_output_valid&&!have_fade_saved&&!fade_mode&&!fixed_text_source_surface);
  if(fault>=3&&fault<=7){old->pitch=pitch;old->w=320;old->h=200;old->format->BitsPerPixel=8;old->format->BytesPerPixel=1;}
  if(fault==8)VGAScreenSeg=old;
 }
}
int main(int argc,char **argv)
{
 assert(argc==2);
 for(int d=4;d<=8;d+=4){suite(argv[1],d);for(int solid=0;solid<=255;solid+=255)for(int removal=1;removal<=12;removal++)counterfactual(argv[1],d,solid,removal);}
 distrust(argv[1]);cleanup();puts("PASS HUT1 production renderer:370 exact cells,3 coherent groups,48 whole-image fade/removal counterfactuals,independent missing/corrupt/fixed-only fallbacks,source/palette timing,lease/mode/modal/recreation guards,no per-frame allocation.");
}
