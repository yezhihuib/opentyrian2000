/* Independent persistent HUF1 text: actual level/message semantic calls,
 * exact glyph/store order, captured native underlay and current final source.
 * This never uses legacy scene text/canvas leases or guesses scene underlay. */
#include "gameplay_hud_font.h"
enum { FHF_CELLS=2208,FHF_COMMANDS=128 };
typedef struct {int x,y;unsigned id,hue;int value;} FhfCommand;
typedef struct {
 bool valid,active,waiting,blank,seen,poison;
 unsigned count,next;
 FhfCommand commands[FHF_COMMANDS];
} FhfRun;
static const SDL_Rect fhf_rects[2]={{268,118,52,8},{20,190,224,8}};
static const unsigned fhf_offsets[2]={0,416};
static FhfRun fhf_runs[2];
static Uint8 fhf_before[FHF_CELLS],fhf_after[FHF_CELLS],fhf_owned[FHF_CELLS];
static Uint32 *fhf_rgba;
static SDL_Surface *fhf_surface;
static void *fhf_pixels;
static SDL_PixelFormat *fhf_format;
static bool fhf_captured,fhf_suspended,fhf_prepared,fhf_glyph_active;
static int fhf_context=-1;
static unsigned fhf_store_count,fhf_store_next;
static struct {unsigned cell;Uint8 index;} fhf_stores[48];
static bool fhf_requested(void)
{
 const char *e=getenv("BUILDING313_FAMILY_FONT_ENABLE");
 return family_static_hud_requested()&&e&&!strcmp(e,"1");
}
static bool fhf_runtime_source(void)
{
 if(sprite_table[TINY_FONT].count!=127)return false;
 HudFontGlyph glyphs[127];
 for(unsigned i=0;i<127;i++){
  const Sprite *s=&sprite_table[TINY_FONT].sprite[i];
  glyphs[i]=(HudFontGlyph){s->width,s->height,s->size,s->data};
 }
 return hud_font_source_matches(font_ascii,glyphs);
}
static void fhf_reset(void)
{
 if(fhf_captured)hud_font_forget_source();
 fhf_captured=fhf_prepared=fhf_suspended=fhf_glyph_active=false;
 fhf_surface=NULL;fhf_pixels=NULL;fhf_format=NULL;fhf_context=-1;
 memset(fhf_runs,0,sizeof fhf_runs);memset(fhf_owned,0,sizeof fhf_owned);
}
static bool fhf_current(void)
{
 if(!fhf_captured)return false;
 if(!fhf_requested()||!family_scope()||!family_indexed(VGAScreenSeg)||
    VGAScreenSeg!=fhf_surface||VGAScreenSeg->pixels!=fhf_pixels||
    VGAScreenSeg->format!=fhf_format||!fhf_runtime_source()){
  fhf_reset();return false;
 }
 return true;
}
static void fhf_copy(unsigned which,Uint8 *to)
{
 SDL_Rect r=fhf_rects[which];unsigned off=fhf_offsets[which];
 for(int y=0;y<r.h;y++)memcpy(to+off+y*r.w,(Uint8 *)VGAScreenSeg->pixels+(r.y+y)*320+r.x,(size_t)r.w);
}
static bool fhf_equal(unsigned which,const Uint8 *to)
{
 SDL_Rect r=fhf_rects[which];unsigned off=fhf_offsets[which];
 for(int y=0;y<r.h;y++)if(memcmp(to+off+y*r.w,(Uint8 *)VGAScreenSeg->pixels+(r.y+y)*320+r.x,(size_t)r.w))return false;
 return true;
}
static void fhf_fail(unsigned which)
{
 fhf_runs[which].valid=fhf_runs[which].active=fhf_runs[which].waiting=false;
 fhf_runs[which].blank=false;fhf_prepared=false;
 if(fhf_context==(int)which){fhf_context=-1;fhf_glyph_active=false;}
 memset(fhf_owned+fhf_offsets[which],0,(size_t)fhf_rects[which].w*fhf_rects[which].h);
}
static void fhf_start(SDL_Surface *source)
{
 fhf_reset();if(!fhf_requested()||source!=VGAScreenSeg||!family_indexed(source)||
  !hud_font_load("assets/hd/shared-ui-v1")||sprite_table[TINY_FONT].count!=127)return;
 HudFontGlyph glyphs[127];for(unsigned i=0;i<127;i++){
  const Sprite *s=&sprite_table[TINY_FONT].sprite[i];glyphs[i]=(HudFontGlyph){s->width,s->height,s->size,s->data};
 }
 if(!hud_font_capture(source->pixels,source->pitch,font_ascii,glyphs))return;
 if(!fhf_rgba)fhf_rgba=calloc(FHF_CELLS*64,sizeof *fhf_rgba);
 if(!fhf_rgba){hud_font_forget_source();return;}
 fhf_surface=source;fhf_pixels=source->pixels;fhf_format=source->format;fhf_captured=true;
 for(unsigned i=0;i<2;i++){fhf_copy(i,fhf_before);fhf_copy(i,fhf_after);fhf_runs[i].blank=true;}
}
static void fhf_shutdown(void)
{fhf_reset();hud_font_shutdown();free(fhf_rgba);fhf_rgba=NULL;}
static void fhf_begin(void)
{
 fhf_prepared=false;fhf_suspended=false;
 if(fhf_context>=0)fhf_fail((unsigned)fhf_context);
}
static void fhf_suspend(void)
{
 fhf_prepared=false;fhf_suspended=true;
 if(fhf_context>=0)fhf_fail((unsigned)fhf_context);
}
static bool fhf_plan(unsigned which,const char *text)
{
 FhfRun *r=fhf_runs+which;SDL_Rect box=fhf_rects[which];
 if(!text)return false;
 r->count=r->next=0;unsigned limit=which?255:10;int x=box.x,bright=0;
 for(unsigned n=0;n<=limit;n++){
  unsigned c=(unsigned char)text[n];if(!c)return true;
  if(n==limit||c>=128)return false;
  if(c==' '){x+=6;if(x>box.x+box.w+1)return false;continue;}
  if(c=='~'){bright=bright?0:4;continue;}
  int id=font_ascii[c];if(id<0)continue;
  unsigned w=hud_font_width((unsigned)id),h=hud_font_height((unsigned)id);
  if(id>=86||!w||!h||h>(unsigned)box.h||x<box.x||x+(int)w>box.x+box.w||r->count>=FHF_COMMANDS)return false;
  r->commands[r->count++]=(FhfCommand){x,box.y,(unsigned)id,which?0u:12u,4+bright};x+=(int)w+1;
 }
 return false;
}
static bool fhf_erase_matches(bool completed)
{
 if(sprite_table[OPTION_SHAPES].count<=36||sprite_table[OPTION_SHAPES].count>SPRITES_PER_TABLE_MAX)return false;
 const Sprite *s=&sprite_table[OPTION_SHAPES].sprite[36];
 if(s->width!=228||s->height!=9||s->size!=2052||!s->data)return false;
 uint64_t stamp=UINT64_C(14695981039346656037);
 for(unsigned i=0;i<s->size;i++)stamp=(stamp^s->data[i])*UINT64_C(1099511628211);
 if(stamp!=UINT64_C(0x029ec9ec39f694b1))return false;
 Uint8 indices[2052],opaque[2052];if(!hud_sprite_decode(OPTION_SHAPES,36,228,9,indices,opaque))return false;
 for(unsigned i=0;i<2052;i++)if(opaque[i]!=255)return false;
 if(completed)for(int y=0;y<9;y++)if(memcmp(indices+y*228,(Uint8 *)VGAScreenSeg->pixels+(189+y)*320+16,228))return false;
 return true;
}
static void fhf_run_begin(unsigned which,const char *text,bool erase)
{
 if(!fhf_current())return;
 if(fhf_context>=0)fhf_fail((unsigned)fhf_context);
 FhfRun *r=fhf_runs+which;bool blank=r->blank;
 fhf_fail(which);
 if(r->poison||(!which&&r->seen)||!fhf_plan(which,text)||
    (erase&&!fhf_erase_matches(false))||(!erase&&(!blank||!fhf_equal(which,fhf_before)))){
  r->poison=true;return;
 }
 r->seen=true;r->waiting=erase;r->active=!erase;
 if(!erase){fhf_copy(which,fhf_before);fhf_copy(which,fhf_after);fhf_context=(int)which;}
}
static void fhf_level_begin(SDL_Surface *surface,const char *text)
{if(surface!=VGAScreenSeg){if(fhf_captured)fhf_fail(0);return;}fhf_run_begin(0,text,false);}
static void fhf_message_begin(const char *text,bool erase)
{fhf_run_begin(1,text,erase);}
static void fhf_message_backdrop(void)
{
 if(!fhf_current())return;
 FhfRun *r=fhf_runs+1;
 if(r->waiting){
  if(!fhf_erase_matches(true)){fhf_fail(1);r->poison=true;return;}
  fhf_copy(1,fhf_before);fhf_copy(1,fhf_after);r->waiting=false;r->active=true;fhf_context=1;
 }
}
static void fhf_glyph_begin(SDL_Surface *surface,int x,int y,unsigned table,unsigned id,bool black,unsigned hue,int value)
{
 if(fhf_context<0||!fhf_current())return;
 unsigned which=(unsigned)fhf_context;FhfRun *r=fhf_runs+which;
 if(fhf_glyph_active||!r->active||r->next>=r->count||surface!=VGAScreenSeg||table!=TINY_FONT||black){fhf_fail(which);return;}
 FhfCommand c=r->commands[r->next];
 if(x!=c.x||y!=c.y||id!=c.id||hue!=c.hue||value!=c.value){fhf_fail(which);return;}
 Uint8 indices[48],opaque[48];if(!hud_sprite_decode(TINY_FONT,id,6,8,indices,opaque)){fhf_fail(which);return;}
 unsigned w=(unsigned)hud_font_width(id),h=(unsigned)hud_font_height(id);SDL_Rect box=fhf_rects[which];
 fhf_store_count=fhf_store_next=0;
 for(unsigned yy=0;yy<h;yy++)for(unsigned xx=0;xx<w;xx++)if(opaque[yy*w+xx]){
  unsigned cell=fhf_offsets[which]+(unsigned)(y+(int)yy-box.y)*box.w+(unsigned)(x+(int)xx-box.x);
  fhf_stores[fhf_store_count].cell=cell;
  fhf_stores[fhf_store_count++].index=(Uint8)((hue<<4)|((indices[yy*w+xx]&15)+value));
 }
 fhf_glyph_active=true;r->next++;
}
static void fhf_pixel(SDL_Surface *surface,Uint8 *address,int style)
{
 /* Almost every callback belongs to the world surface. Reject by saved
  * identities and integer coordinates BEFORE hashing all127 glyph sources.
  * No saved allocation is dereferenced here. Actual HUD writes and every
  * prepare/post-lock paint still perform the complete current-source proof. */
 if(!fhf_captured)return;
 if(surface!=fhf_surface){if(fhf_context>=0)fhf_fail((unsigned)fhf_context);return;}
 uintptr_t p=(uintptr_t)address,b=(uintptr_t)fhf_pixels;
 if(p<b||p-b>=64000){if(fhf_context>=0)fhf_fail((unsigned)fhf_context);return;}
 int x=(int)((p-b)%320),y=(int)((p-b)/320);
 if(fhf_context>=0){SDL_Rect box=fhf_rects[fhf_context];
  if(x<box.x||x>=box.x+box.w||y<box.y||y>=box.y+box.h){fhf_fail((unsigned)fhf_context);return;}}
 bool relevant=false;
 for(unsigned i=0;i<2;i++){SDL_Rect box=fhf_rects[i];
  if(x>=box.x&&x<box.x+box.w&&y>=box.y&&y<box.y+box.h)relevant=true;}
 if(!relevant||!fhf_current())return;
 for(unsigned which=0;which<2;which++){
  SDL_Rect box=fhf_rects[which];FhfRun *r=fhf_runs+which;
  if(x<box.x||x>=box.x+box.w||y<box.y||y>=box.y+box.h||r->waiting)continue;
  unsigned cell=fhf_offsets[which]+(unsigned)(y-box.y)*box.w+(unsigned)(x-box.x);
  if(fhf_context!=(int)which||!r->active||!fhf_glyph_active||style!=MIRROR_NORMAL||
    fhf_store_next>=fhf_store_count||cell!=fhf_stores[fhf_store_next].cell||*address!=fhf_stores[fhf_store_next].index){fhf_fail(which);continue;}
  fhf_after[cell]=*address;fhf_store_next++;
 }
}
static void fhf_glyph_end(void)
{
 if(fhf_context<0)return;
 if(!fhf_glyph_active||fhf_store_next!=fhf_store_count){fhf_fail((unsigned)fhf_context);return;}
 fhf_glyph_active=false;
}
static void fhf_rect(SDL_Surface *surface,const SDL_Rect *rect)
{
 if(!fhf_current()||surface!=VGAScreenSeg)return;
 SDL_Rect q=rect?*rect:(SDL_Rect){0,0,320,200};
 if(q.w<=0||q.h<=0)return;
 for(unsigned i=0;i<2;i++){
  SDL_Rect r=fhf_rects[i];
  if(!fhf_runs[i].waiting&&q.x<(int64_t)r.x+r.w&&(int64_t)q.x+q.w>r.x&&
    q.y<(int64_t)r.y+r.h&&(int64_t)q.y+q.h>r.y)fhf_fail(i);
 }
}
static void fhf_run_end(unsigned which)
{
 if(!fhf_current())return;
 FhfRun *r=fhf_runs+which;
 if(fhf_context!=(int)which||!r->active||fhf_glyph_active||r->next!=r->count||!fhf_equal(which,fhf_after)){fhf_fail(which);return;}
 r->active=false;r->valid=true;r->blank=false;fhf_context=-1;
}
static void fhf_message_erase_begin(void)
{if(fhf_captured){fhf_fail(1);fhf_runs[1].waiting=true;}}
static void fhf_message_erased(bool help_prompt)
{
 if(!fhf_current())return;
 bool valid=fhf_erase_matches(true);fhf_fail(1);
 if(!valid){fhf_runs[1].poison=true;return;}
 fhf_copy(1,fhf_before);fhf_copy(1,fhf_after);fhf_runs[1].blank=!help_prompt;
}
static Uint32 fhf_blend(Uint32 lower,Uint32 color,unsigned alpha)
{
 Uint32 out=0xff000000u;for(unsigned shift=0;shift<24;shift+=8)
  out|=((((color>>shift)&255)*alpha+((lower>>shift)&255)*(255-alpha)+127)/255)<<shift;
 return out;
}
static bool fhf_prepare(void)
{
 fhf_prepared=false;memset(fhf_owned,0,sizeof fhf_owned);
 if(!fhf_current()||fhf_suspended||!hud_font_palette_matches(rgb_palette))return false;
 for(unsigned which=0;which<2;which++){
  FhfRun *r=fhf_runs+which;SDL_Rect box=fhf_rects[which];unsigned off=fhf_offsets[which];
  if(!r->valid||r->poison)continue;
  if(!fhf_equal(which,fhf_after)){fhf_fail(which);continue;}
  for(unsigned k=0;k<(unsigned)(box.w*box.h);k++)for(unsigned sub=0;sub<64;sub++)fhf_rgba[(off+k)*64+sub]=palette_rgb(fhf_before[off+k]);
  for(unsigned n=0;n<r->count;n++){
   FhfCommand c=r->commands[n];Uint8 opaque[48];unsigned w=(unsigned)hud_font_width(c.id),h=(unsigned)hud_font_height(c.id);
   if(!hud_sprite_decode(TINY_FONT,c.id,6,8,NULL,opaque)){fhf_fail(which);break;}
   Uint32 color=palette_rgb((Uint8)((c.hue<<4)|(7+c.value)));
   for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){
    unsigned cell=off+(unsigned)(c.y+(int)y-box.y)*box.w+(unsigned)(c.x+(int)x-box.x);
    if(opaque[y*w+x])fhf_owned[cell]=1;
    for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
     unsigned alpha=hud_font_alpha(c.id,(int)(x*8+sx),(int)(y*8+sy),8);
     if(alpha){unsigned at=cell*64+sy*8+sx;fhf_owned[cell]=1;fhf_rgba[at]=fhf_blend(fhf_rgba[at],color,alpha);}
    }
   }
  }
 }
 fhf_prepared=true;return true;
}
static const Uint32 *fhf_sample(int x,int y,int sx,int sy,Uint8 index)
{
 if(!fhf_prepared||sx<0||sx>=8||sy<0||sy>=8)return NULL;
 for(unsigned which=0;which<2;which++){
  SDL_Rect r=fhf_rects[which];if(x<r.x||x>=r.x+r.w||y<r.y||y>=r.y+r.h)continue;
  unsigned cell=fhf_offsets[which]+(unsigned)(y-r.y)*r.w+(unsigned)(x-r.x);
  if(fhf_runs[which].valid&&fhf_owned[cell]&&fhf_after[cell]==index)return fhf_rgba+cell*64+(unsigned)sy*8+(unsigned)sx;
 }
 return NULL;
}

/* Readback-only receipt for the current prepared output. No mutation or grant. */
const uint32_t *render_mirror_family_hud_font_sample(int x,int y,int sx,int sy,uint8_t index)
{
 if(!fhf_captured||!fhf_prepared||fhf_suspended||!fhf_requested()||!family_scope()||
    !family_indexed(VGAScreenSeg)||VGAScreenSeg!=fhf_surface||VGAScreenSeg->pixels!=fhf_pixels||
    VGAScreenSeg->format!=fhf_format||x<0||x>=320||y<0||y>=200||
    ((const Uint8 *)VGAScreenSeg->pixels)[y*320+x]!=index)return NULL;
 return fhf_sample(x,y,sx,sy,index);
}
