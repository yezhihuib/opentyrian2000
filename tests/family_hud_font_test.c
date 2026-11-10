/* Isolated family persistent-font transaction with original PIC/font/OPTION
 * bytes on stdin. Native startup/scene admission is not claimed by this test. */
#define main static_hud_baseline_main
#include "family_static_hud_test.c"
#undef main

static void font_reset_source(void)
{
 reset_source();
}
/* The same original hue/value equation and row-order stores as
 * blit_sprite_hv_unsafe, with the production adapter notified after each store. */
static void native_glyph(int x,int y,unsigned id,unsigned hue,int value)
{
 Uint8 indices[48],opaque[48];CHECK(hud_sprite_decode(TINY_FONT,id,6,8,indices,opaque));
 unsigned w=sprite_table[TINY_FONT].sprite[id].width,h=sprite_table[TINY_FONT].sprite[id].height;
 fhf_glyph_begin(VGAScreenSeg,x,y,TINY_FONT,id,false,hue,value);
 for(unsigned yy=0;yy<h;yy++)for(unsigned xx=0;xx<w;xx++)if(opaque[yy*w+xx]){
  Uint8 *p=(Uint8 *)VGAScreenSeg->pixels+(y+(int)yy)*320+x+xx;
  *p=(Uint8)((hue<<4)|((indices[yy*w+xx]&15)+value));fhf_pixel(VGAScreenSeg,p,MIRROR_NORMAL);
 }
 fhf_glyph_end();
}
static void native_text(int x,int y,const char *text,unsigned hue)
{
 int bright=0;
 for(unsigned i=0;text[i];i++){
  unsigned c=(unsigned char)text[i];if(c==' '){x+=6;continue;}
  if(c=='~'){bright=bright?0:4;continue;}
  int id=font_ascii[c];if(id<0)continue;
  native_glyph(x,y,(unsigned)id,hue,4+bright);
  x+=sprite_table[TINY_FONT].sprite[id].width+1;
 }
}
static void native_erase(void)
{
 Uint8 indices[2052],opaque[2052];CHECK(hud_sprite_decode(OPTION_SHAPES,36,228,9,indices,opaque));
 for(int y=0;y<9;y++)for(int x=0;x<228;x++){
  Uint8 *p=(Uint8 *)VGAScreenSeg->pixels+(189+y)*320+16+x;
  *p=indices[y*228+x];fhf_pixel(VGAScreenSeg,p,MIRROR_NORMAL);
 }
}
static void message(const char *text,bool erase)
{
 fhf_message_begin(text,erase);if(erase)native_erase();fhf_message_backdrop();
 native_text(20,190,text,0);fhf_run_end(1);
}
static void verify_samples(unsigned which)
{
 CHECK(fhf_prepare());CHECK(fhf_runs[which].valid);
 SDL_FillRect(output,NULL,0x12345678);family_static_hud_compose();
 SDL_Rect r=fhf_rects[which];unsigned count=0;
 for(int y=r.y;y<r.y+r.h;y++)for(int x=r.x;x<r.x+r.w;x++){
  Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[y*320+x];
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
   const Uint32 *p=fhf_sample(x,y,sx,sy,index);
   /* Independently reconstruct ordered original-color alpha-over samples. */
   unsigned cell=fhf_offsets[which]+(unsigned)(y-r.y)*r.w+(unsigned)(x-r.x);
   Uint32 expected=palette_rgb(fhf_before[cell]);bool owned=false;
   for(unsigned n=0;n<fhf_runs[which].count;n++){
    FhfCommand c=fhf_runs[which].commands[n];
    int dx=x-c.x,dy=y-c.y,w=hud_font_width(c.id),h=hud_font_height(c.id);
    if(dx<0||dx>=w||dy<0||dy>=h)continue;
    Uint8 mask[48];CHECK(hud_sprite_decode(TINY_FONT,c.id,6,8,NULL,mask));
    owned=owned||mask[dy*w+dx]!=0;
    for(int ay=0;ay<4;ay++)for(int ax=0;ax<4;ax++)owned=owned||hud_font_alpha(c.id,dx*4+ax,dy*4+ay,4)!=0;
    unsigned alpha=hud_font_alpha(c.id,dx*8+sx,dy*8+sy,8);Uint32 color=palette_rgb((Uint8)((c.hue<<4)|(7+c.value)));
    Uint32 rgb=0xff000000u;
    for(unsigned shift=0;shift<24;shift+=8)rgb|=((((color>>shift)&255)*alpha+((expected>>shift)&255)*(255-alpha)+127)/255)<<shift;
    expected=rgb;
   }
   CHECK((p!=NULL)==owned);
   if(p){CHECK(*p==expected);count++;
    CHECK(((Uint32 *)((Uint8 *)output->pixels+(y*8+sy)*output->pitch))[x*8+sx]==expected);}
  }
 }
 CHECK(count>64);CHECK(!fhf_sample(0,0,0,0,0));CHECK(!fhf_sample(r.x,r.y,-1,0,0));
}
static void verify_presentation(void)
{
 for(int scale=2;scale<=4;scale+=2){
  SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,320*scale,200*scale,32,SDL_PIXELFORMAT_ARGB8888);CHECK(target);
  SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(target);CHECK(renderer);
  SDL_Rect dst={0,0,320*scale,200*scale};
  family_static_hud_begin();family_static_hud_finish(MIRROR_OUTPUT_ORDINARY,false);
  CHECK(family_static_hud_present(renderer,VGAScreenSeg,&dst));
  for(int y=0;y<200*scale;y++)for(int x=0;x<320*scale;x++){
   int lx=x/scale,ly=y/scale,sx=(x%scale)*(8/scale)+4/scale,sy=(y%scale)*(8/scale)+4/scale;
   Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[ly*320+lx];
   const Uint32 *font=render_mirror_family_hud_font_sample(lx,ly,sx,sy,index);
   Uint32 expected=font?*font:sample_expected(lx,ly,sx,sy);
   CHECK(((Uint32 *)((Uint8 *)target->pixels+y*target->pitch))[x]==expected);
  }
  CHECK(!family_static_hud_present(renderer,VGAScreenSeg,&dst));
  family_static_hud_release_texture();SDL_DestroyRenderer(renderer);SDL_FreeSurface(target);
 }
}
int main(int argc,char **argv)
{
 CHECK(argc==2);load_original();CHECK(SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 output=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);
 CHECK(VGAScreenSeg&&output);
 SDL_setenv("BUILDING313_FAMILY_HUD_ENABLE","1",1);SDL_setenv("BUILDING313_FAMILY_FONT_ENABLE","1",1);
 font_reset_source();
 if(strcmp(argv[1],"valid")){CHECK(!fhf_captured);goto done;}
 CHECK(fhf_captured&&fhf_runtime_source());
 fhf_level_begin(VGAScreenSeg,"ASTEROID2");native_text(268,118,"ASTEROID2",12);fhf_run_end(0);verify_samples(0);
 message("~Welcome~ pilot!",false);verify_samples(1);
 verify_presentation();
 for(unsigned i=0;i<3;i++){message(i&1?"A":"Armor ~28~",true);verify_samples(1);}
 /* Native same-value writes must retire stale text, not pass by pixel equality. */
 Uint8 *p=(Uint8 *)VGAScreenSeg->pixels+190*320+20;fhf_pixel(VGAScreenSeg,p,MIRROR_NORMAL);
 CHECK(!fhf_runs[1].valid);CHECK(fhf_prepare());CHECK(!fhf_sample(20,190,0,0,*p));
 message("New message",true);verify_samples(1);
 /* Genuine erase restores a verified blank message source. */
 fhf_message_erase_begin();native_erase();fhf_message_erased(false);CHECK(fhf_runs[1].blank);
 message("Fresh",false);verify_samples(1);
 rgb_palette[255]^=1;CHECK(!fhf_prepare());rgb_palette[255]^=1;verify_samples(1);
 fhf_suspend();CHECK(!fhf_prepare());fhf_begin();verify_samples(1);
 /* An unobserved final-index mutation retires the entire affected run. */
 *p^=1;CHECK(fhf_prepare());CHECK(!fhf_runs[1].valid);*p^=1;CHECK(fhf_prepare());CHECK(!fhf_runs[1].valid);
 /* Wrong glyph, missing stores, and extra out-of-footprint stores fail closed. */
 font_reset_source();fhf_level_begin(VGAScreenSeg,"A");fhf_glyph_begin(VGAScreenSeg,269,118,TINY_FONT,(unsigned)font_ascii['A'],false,12,4);CHECK(fhf_context<0);
 font_reset_source();fhf_level_begin(VGAScreenSeg,"A");fhf_glyph_begin(VGAScreenSeg,268,118,TINY_FONT,(unsigned)font_ascii['A'],false,12,4);fhf_glyph_end();CHECK(fhf_context<0);
 font_reset_source();fhf_level_begin(VGAScreenSeg,"A");fhf_glyph_begin(VGAScreenSeg,268,118,TINY_FONT,(unsigned)font_ascii['A'],false,12,4);fhf_pixel(VGAScreenSeg,VGAScreenSeg->pixels,MIRROR_NORMAL);CHECK(fhf_context<0);
 font_reset_source();fhf_level_begin(VGAScreenSeg,"A");fhf_glyph_begin(VGAScreenSeg,268,118,TINY_FONT,(unsigned)font_ascii['A'],false,12,4);fhf_pixel(output,output->pixels,MIRROR_NORMAL);CHECK(fhf_context<0);
 /* Reject an in-footprint store with the wrong value, then a valid-value
  * store at the wrong ordered cell. Neither can earn output ownership. */
 for(unsigned wrong_order=0;wrong_order<2;wrong_order++){
  font_reset_source();fhf_level_begin(VGAScreenSeg,"A");
  fhf_glyph_begin(VGAScreenSeg,268,118,TINY_FONT,(unsigned)font_ascii['A'],false,12,4);
  CHECK(fhf_store_count>1);
  unsigned at=wrong_order?1:0,cell=fhf_stores[at].cell;
  Uint8 *store=(Uint8 *)VGAScreenSeg->pixels+(118+cell/52)*320+268+cell%52;
  *store=(Uint8)(fhf_stores[at].index^(wrong_order?0:1));
  fhf_pixel(VGAScreenSeg,store,MIRROR_NORMAL);CHECK(fhf_context<0);
  fhf_run_end(0);CHECK(!fhf_runs[0].valid);
 }
 /* An extra in-footprint store after the glyph and an interrupted frame
  * must fail even when the native glyph itself was complete. */
 font_reset_source();fhf_level_begin(VGAScreenSeg,"A");native_text(268,118,"A",12);
 fhf_pixel(VGAScreenSeg,(Uint8 *)VGAScreenSeg->pixels+118*320+268,MIRROR_NORMAL);
 fhf_run_end(0);CHECK(!fhf_runs[0].valid);
 font_reset_source();fhf_level_begin(VGAScreenSeg,"A");native_text(268,118,"A",12);
 fhf_begin();fhf_run_end(0);CHECK(!fhf_runs[0].valid);
 font_reset_source();message("Unknown",false);verify_samples(1);
 SDL_Rect same_value={20,190,1,1};fhf_rect(VGAScreenSeg,&same_value);CHECK(!fhf_runs[1].valid);
 Uint8 *source=sprite_table[TINY_FONT].sprite[0].data;CHECK(source);source[0]^=1;CHECK(!fhf_prepare());source[0]^=1;CHECK(!fhf_captured);
 /* Irrelevant world/HUD-outside writes deliberately avoid glyph hashing, but
  * cannot hide a source mutation from the next actual output preparation. */
 font_reset_source();message("Still guarded",false);verify_samples(1);
 source[0]^=1;fhf_pixel(output,output->pixels,MIRROR_NORMAL);
 fhf_pixel(VGAScreenSeg,VGAScreenSeg->pixels,MIRROR_NORMAL);CHECK(fhf_captured);
 CHECK(!fhf_prepare());CHECK(!fhf_captured);source[0]^=1;
 font_reset_source();sprite_table[TINY_FONT].count=126;CHECK(!fhf_prepare());sprite_table[TINY_FONT].count=127;
 font_reset_source();sprite_table[TINY_FONT].sprite[0].data=NULL;CHECK(!fhf_prepare());sprite_table[TINY_FONT].sprite[0].data=source;
 font_reset_source();unsigned option_count=sprite_table[OPTION_SHAPES].count;
 sprite_table[OPTION_SHAPES].count=36;CHECK(!fhf_erase_matches(false));sprite_table[OPTION_SHAPES].count=option_count;
 Uint8 *erase_source=sprite_table[OPTION_SHAPES].sprite[36].data;sprite_table[OPTION_SHAPES].sprite[36].data=NULL;
 CHECK(!fhf_erase_matches(false));sprite_table[OPTION_SHAPES].sprite[36].data=erase_source;
 font_reset_source();scope=false;CHECK(!fhf_prepare());scope=true;CHECK(!fhf_prepare());
 font_reset_source();SDL_setenv("BUILDING313_FAMILY_FONT_ENABLE","0",1);CHECK(!fhf_prepare());SDL_setenv("BUILDING313_FAMILY_FONT_ENABLE","1",1);CHECK(!fhf_prepare());
 font_reset_source();void *old=VGAScreenSeg->pixels;VGAScreenSeg->pixels=malloc(64000);CHECK(VGAScreenSeg->pixels);memcpy(VGAScreenSeg->pixels,old,64000);
 CHECK(!fhf_prepare());free(VGAScreenSeg->pixels);VGAScreenSeg->pixels=old;CHECK(!fhf_captured);
done:
 family_static_hud_reset();gameplay_hud_shutdown();fhf_shutdown();SDL_FreeSurface(VGAScreenSeg);SDL_FreeSurface(output);
 for(unsigned t=0;t<8;t++)for(unsigned i=0;i<sprite_table[t].count;i++)free(sprite_table[t].sprite[i].data);
 SDL_Quit();printf("PASS family persistent font %s: %u checks\n",argv[1],checks);return 0;
}
