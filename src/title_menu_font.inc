/* SPDX-License-Identifier: GPL-2.0-or-later
 * Title-only source witness, optional legacy TMF1, and reconstructed MAIN7.
 * Included by title_layers.c; no shared-font replacement or indexed writes.
 * The complete original 35+1 runs remain mandatory with either resource.
 */
#ifndef TITLE_MENU_MAP_FNV
#define TITLE_MENU_MAP_FNV UINT64_C(0x845b16939661b466)
#endif
#ifndef TITLE_MENU_METRICS_FNV
#define TITLE_MENU_METRICS_FNV UINT64_C(0xf0dec0f37828f1c4)
#endif
#ifndef TITLE_MENU_ENCODED_FNV
#define TITLE_MENU_ENCODED_FNV UINT64_C(0x96f0e4e668876f23)
#endif
#ifndef TITLE_MENU_INK_FNV
#define TITLE_MENU_INK_FNV UINT64_C(0xa3861b64f710cb1f)
#endif

enum {
 TM_GLYPHS=85, TM_INK=76, TM_AW=896, TM_AH=384, TM_CW=56, TM_CH=64,
 TM_INSET=4, TM_MAX_W=12, TM_MAX_H=13, TM_PLANE=344064,
 TM_PAYLOAD=688128, TM_HEADER=128, TM_TEXT=64,
 TM_COMMANDS=36*TM_TEXT, TM_EVENTS=TM_TEXT*TM_MAX_W*TM_MAX_H,
 TM_SAMPLE_Y=103*TL_D, TM_SAMPLE_H=(196-103)*TL_D,
 TM_SAMPLE_W=TL_W*TL_D, TM_SAMPLE_BYTES=TL_OUT_BYTES
};
enum TmPhase { TM_LOADED, TM_BASE, TM_BASE_DONE, TM_SAVED, TM_HIGHLIGHT, TM_READY };
struct TmGlyph {
 const Uint8 *rle;
 unsigned size,w,h;
 Uint8 source[TM_MAX_W*TM_MAX_H]; /* 255 is transparent, otherwise low nibble */
 bool ink;
};
struct TmCommand { Uint16 x,y; Uint8 id; Sint8 value; };
struct TmEvent { Uint16 offset; Uint8 index; };
static struct {
 Uint8 *payload;
 Uint32 *samples;
 struct TmGlyph glyph[TM_GLYPHS];
 struct TmCommand command[TM_COMMANDS];
 struct TmEvent event[TM_EVENTS];
 char text[7][TM_TEXT];
 unsigned count,base_count,runs,event_count,event_next;
 unsigned natural_id[7];
 uint64_t natural_generation;
 int phase,selected;
 bool in_run,source_ready,natural_ready;
} menu_font;
static const char *const tm_natural_text[7]={
 "Start New Game","Load Game","High Scores","Instructions","Setup","Demo","Quit"
};

static uint64_t tm_hash_more(uint64_t h,const Uint8 *p,size_t n)
{ while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h; }
static uint64_t tm_hash_u16(uint64_t h,unsigned v)
{ const Uint8 p[2]={(Uint8)v,(Uint8)(v>>8)};return tm_hash_more(h,p,2); }
static uint64_t tm_map_hash(void)
{
 uint64_t h=UINT64_C(14695981039346656037);
 for(unsigned i=0;i<256;i++) {
  uint32_t v=(uint32_t)font_ascii[i];
  const Uint8 p[4]={(Uint8)v,(Uint8)(v>>8),(Uint8)(v>>16),(Uint8)(v>>24)};
  h=tm_hash_more(h,p,4);
 }
 return h;
}
static void tm_end(void)
{ free(menu_font.payload);free(menu_font.samples);memset(&menu_font,0,sizeof(menu_font)); }

/* Metadata and encoded bytes are independently pinned, never trusted because
 * the optional file says they match. Source pointers are captured per lease. */
static bool tm_source(bool capture)
{
 if(sprite_table[SMALL_FONT_SHAPES].count!=TM_GLYPHS||tm_map_hash()!=TITLE_MENU_MAP_FNV)return false;
 uint64_t metrics=UINT64_C(14695981039346656037),encoded=metrics,ink=metrics;
 for(unsigned id=0;id<TM_GLYPHS;id++) {
  const Sprite *s=sprite(SMALL_FONT_SHAPES,id);
  struct TmGlyph *g=&menu_font.glyph[id];
  if(!s->data||!s->size||!s->width||s->width>TM_MAX_W||!s->height||s->height>TM_MAX_H||s->size>TM_MAX_W*TM_MAX_H*2+TM_MAX_H)return false;
  if(!capture&&(s->data!=g->rle||s->size!=g->size||s->width!=g->w||s->height!=g->h))return false;
  metrics=tm_hash_u16(tm_hash_u16(tm_hash_u16(metrics,s->width),s->height),s->width+1);
  encoded=tm_hash_u16(tm_hash_u16(tm_hash_u16(encoded,s->width),s->height),s->size);
  encoded=tm_hash_more(encoded,s->data,s->size);
  if(capture) {
   g->rle=s->data;g->size=s->size;g->w=s->width;g->h=s->height;
   memset(g->source,255,sizeof(g->source));
   unsigned x=0,y=0;
   for(unsigned k=0;k<s->size;k++) {
    Uint8 v=s->data[k];
    if(y>=s->height)return false;
    if(v==255){if(++k>=s->size)return false;x+=s->data[k];}
    else if(v==254)x=s->width;
    else if(v==253)++x;
    else {
     if(x>=s->width)return false;
     g->source[y*TM_MAX_W+x]=v&15;g->ink=true;++x;
    }
    if(x>s->width)return false;
    if(x==s->width){x=0;++y;}
   }
   if(y>s->height||x)return false;
  }
  Uint8 present=g->ink?255:0;
  ink=tm_hash_more(ink,&present,1);
 }
 return metrics==TITLE_MENU_METRICS_FNV&&encoded==TITLE_MENU_ENCODED_FNV&&ink==TITLE_MENU_INK_FNV;
}
static bool tm_check(void)
{
 if(!menu_font.source_ready)return false;
 if(!tm_source(false)){tm_end();return false;}
 return true;
}
static bool tm_padding(const Uint8 *data)
{
 const Uint8 *roles=data+TM_PLANE;
 unsigned ink_count=0;
 for(unsigned id=0;id<96;id++) {
  const struct TmGlyph *g=id<TM_GLYPHS?&menu_font.glyph[id]:NULL;
  bool seen=false;
  for(unsigned y=0;y<TM_CH;y++)for(unsigned x=0;x<TM_CW;x++) {
   unsigned p=((id/16)*TM_CH+y)*TM_AW+(id%16)*TM_CW+x;
   Uint8 alpha=data[p],role=roles[p];
   bool allowed=g&&g->ink&&x>=TM_INSET&&y>=TM_INSET&&x<TM_INSET+g->w*TL_D&&y<TM_INSET+g->h*TL_D;
   if((!allowed&&(alpha||role))||(!alpha&&role)||(alpha&&(role<12||role>15)))return false;
   if(alpha)seen=true;
  }
  if(g&&seen!=g->ink)return false;
  ink_count+=seen;
 }
 return ink_count==TM_INK;
}
static void tm_load_legacy(const char *directory)
{
 if(!directory||!*directory)return;
 char path[1024];Uint8 header[TM_HEADER],extra;TL_STAT st;
 int n=snprintf(path,sizeof(path),"%s/title-menu-font-v1.hda",directory);
 if(n<0||(size_t)n>=sizeof(path))return;
 int fd=TL_OPEN(path);if(fd<0)return;
 Uint8 *data=NULL;bool valid=false;
 static const unsigned fields[15]={1,4,TM_AW,TM_AH,TM_GLYPHS,TM_INK,TM_CW,TM_CH,TM_INSET,1,TM_PLANE,TM_PLANE,12,15,0};
 if(TL_FSTAT(fd,&st)||!TL_REGULAR(st.st_mode)||st.st_size!=TM_HEADER+TM_PAYLOAD||TL_READ(fd,header,TM_HEADER)!=TM_HEADER||memcmp(header,"TMF1",4))goto done;
 for(unsigned i=0;i<15;i++)if(tl_u32(header+4+4*i)!=fields[i])goto done;
 if(tl_u64(header+64)!=TITLE_MENU_MAP_FNV||tl_u64(header+72)!=TITLE_MENU_METRICS_FNV||
    tl_u64(header+80)!=TITLE_MENU_ENCODED_FNV||tl_u64(header+88)!=TITLE_MENU_INK_FNV||
    tl_u64(header+96)!=TITLE_PAL_FNV||tl_u64(header+112)||tl_u64(header+120))goto done;
 data=malloc(TM_PAYLOAD);
 if(!data||TL_READ(fd,data,TM_PAYLOAD)!=TM_PAYLOAD||TL_READ(fd,&extra,1)!=0||
    tl_hash(data,TM_PAYLOAD)!=tl_u64(header+104)||!tm_padding(data))goto done;
 valid=true;
done:
 if(TL_CLOSE(fd))valid=false;
 if(!valid){free(data);return;}
 menu_font.payload=data;
}
/* Family invalidation never retires the independent legacy atlas or source
 * witness. A missing old TMF must likewise not disable an accepted MAIN7. */
static bool tm_natural_check(void)
{
 if(menu_font.natural_ready&&(game_probe_original_reference||
    !common_menu_runs_ready(COMMON_MENU_MAIN)||
    common_menu_runs_generation(COMMON_MENU_MAIN)!=menu_font.natural_generation))
  menu_font.natural_ready=false;
 return menu_font.natural_ready;
}
static void tm_load(const char *directory)
{
 tm_end();
 if(!tm_source(true))return;
 menu_font.source_ready=true;menu_font.phase=TM_LOADED;menu_font.selected=-1;
 tm_load_legacy(directory);
 if(!game_probe_original_reference&&common_menu_runs_load(COMMON_MENU_MAIN)&&
    common_menu_runs_count(COMMON_MENU_MAIN)==7) {
  menu_font.natural_ready=true;
  menu_font.natural_generation=common_menu_runs_generation(COMMON_MENU_MAIN);
  for(unsigned row=0;row<7;row++) {
   int id=common_menu_runs_find(COMMON_MENU_MAIN,tm_natural_text[row]);
   if(id<0){menu_font.natural_ready=false;break;}
   menu_font.natural_id[row]=(unsigned)id;
  }
 }
 if(menu_font.payload||menu_font.natural_ready) {
  menu_font.samples=malloc(TM_SAMPLE_BYTES);
  if(!menu_font.samples)tm_end();
 }
}
static void tm_base_begin(void)
{
 if(!tm_check())return;
 if(menu_font.phase!=TM_LOADED){tm_end();return;}
 menu_font.phase=TM_BASE;
}
static void tm_base_done(void)
{
 if(!tm_check())return;
 if(menu_font.phase!=TM_BASE||menu_font.in_run||menu_font.runs!=35){tm_end();return;}
 menu_font.phase=TM_BASE_DONE;
}
static void tm_save(void)
{
 if(!tm_check())return;
 if(menu_font.phase!=TM_BASE_DONE||menu_font.in_run){tm_end();return;}
 /* Base commands are immutable. The count snapshots their exact prefix. */
 menu_font.base_count=menu_font.count;menu_font.phase=TM_SAVED;
}
static void tm_restore(void)
{
 if(!tm_check())return;
 if((menu_font.phase!=TM_SAVED&&menu_font.phase!=TM_READY)||menu_font.in_run){tm_end();return;}
 menu_font.count=menu_font.base_count;menu_font.runs=0;
 menu_font.selected=-1;
 menu_font.event_count=menu_font.event_next=0;menu_font.phase=TM_HIGHLIGHT;
}
static void tm_highlight_done(void)
{
 if(!tm_check())return;
 if(menu_font.phase!=TM_HIGHLIGHT||menu_font.in_run||menu_font.runs!=1){tm_end();return;}
 menu_font.phase=TM_READY;
}
static Uint8 tm_index(unsigned role,int value)
{ int v=(int)role+value;if(v<0)v=0;if(v>15)v=15;return (Uint8)(240|v); }

/* Called only by the six explicit title draw sites. Whole-menu fallback is
 * permanent for this title epoch, including when an unsupported byte appears. */
void title_layers_menu_text_begin(SDL_Surface *surface,int x,int y,const char *text,int font,int alignment,Uint8 hue,Sint8 value)
{
 if(!state.active||!tm_check())return;
 bool base=state.stage==ST_MENU&&menu_font.phase==TM_BASE;
 bool selected=state.stage==ST_HIGHLIGHT&&menu_font.phase==TM_HIGHLIGHT;
 if(surface!=state.screen||!tl_layout()||(!base&&!selected)||menu_font.in_run||!text||font!=normal_font||hue!=15||
    (base&&(alignment!=left_aligned||menu_font.runs>=35))||
    (selected&&(alignment!=centered||menu_font.runs!=0))){tm_end();return;}
 unsigned length=0,width=0;
 for(;length<TM_TEXT&&text[length];length++) {
  unsigned ch=(unsigned char)text[length];
  if(ch==' '){width+=6;continue;}
  if(ch=='~')continue;
  int id=font_ascii[ch];
  if(ch>=128||id<0||id>=TM_GLYPHS){tm_end();return;}
  width+=menu_font.glyph[id].w+1;
 }
 if(!length||length==TM_TEXT||width>318){tm_end();return;}
 unsigned row,pass;
 static const int dx[5]={-1,1,1,-1,0},dy[5]={-1,1,-1,1,0};
 if(base) {
  row=menu_font.runs/5;pass=menu_font.runs%5;
  if(value!=(pass==4?-3:-10)||x!=160-(int)width/2+dx[pass]||y!=104+13*(int)row+dy[pass]){tm_end();return;}
  if(!pass)memcpy(menu_font.text[row],text,length+1);
  else if(strcmp(menu_font.text[row],text)){tm_end();return;}
  if(strcmp(tm_natural_text[row],text))menu_font.natural_ready=false;
 } else {
  if(x!=160||y<104||y>182||(y-104)%13||value!=-1){tm_end();return;}
  row=(unsigned)(y-104)/13;
  if(strcmp(menu_font.text[row],text)){tm_end();return;}
  menu_font.selected=(int)row;
  x-=(int)width/2;
 }
 menu_font.event_count=menu_font.event_next=0;
 bool highlight=false;
 int brightness=value;
 for(unsigned i=0;i<length;i++) {
  unsigned ch=(unsigned char)text[i];
  if(ch==' '){x+=6;continue;}
  if(ch=='~'){highlight=!highlight;brightness+=highlight?4:-4;continue;}
  unsigned id=(unsigned)font_ascii[ch];const struct TmGlyph *g=&menu_font.glyph[id];
  if(x<0||y<0||x+(int)g->w>TL_W||y+(int)g->h>TL_H||
     y*TL_D<TM_SAMPLE_Y||(y+(int)g->h)*TL_D>TM_SAMPLE_Y+TM_SAMPLE_H||menu_font.count==TM_COMMANDS){tm_end();return;}
  struct TmCommand *command=&menu_font.command[menu_font.count++];
  command->x=(Uint16)x;command->y=(Uint16)y;command->id=(Uint8)id;command->value=(Sint8)brightness;
  for(unsigned sy=0;sy<g->h;sy++)for(unsigned sx=0;sx<g->w;sx++)if(g->source[sy*TM_MAX_W+sx]!=255) {
   if(menu_font.event_count==TM_EVENTS){tm_end();return;}
   struct TmEvent *event=&menu_font.event[menu_font.event_count++];
   event->offset=(Uint16)((y+(int)sy)*TL_W+x+(int)sx);event->index=tm_index(g->source[sy*TM_MAX_W+sx],brightness);
  }
  x+=(int)g->w+1;
 }
 menu_font.in_run=true;
}
static void tm_pixel(unsigned offset,Uint8 index)
{
 if(!menu_font.source_ready)return;
 if(!menu_font.in_run||menu_font.event_next>=menu_font.event_count||
    menu_font.event[menu_font.event_next].offset!=offset||menu_font.event[menu_font.event_next].index!=index){tm_end();return;}
 ++menu_font.event_next;
}
void title_layers_menu_text_done(void)
{
 if(!state.active||!tm_check())return;
 if(!menu_font.in_run||menu_font.event_next!=menu_font.event_count){tm_end();return;}
 menu_font.in_run=false;++menu_font.runs;
}
static bool tm_render(const SDL_Rect *destination)
{
 if(!tm_check()||(menu_font.phase!=TM_SAVED&&menu_font.phase!=TM_READY)||menu_font.in_run)return false;
 if(tm_natural_check()||!menu_font.payload)return false;
 /* The bounded trial has exactly two output sizes. Other scales use the
  * original menu plane, leaving title artwork's existing sampling untouched. */
 bool reduce=destination->w==640&&destination->h==400;
 if(!reduce&&(destination->w!=1280||destination->h!=800))return false;
 if(reduce) {
  /* Preserve the same nearest title-underlay sample for all four independent
   * canonical histories. Never average the artwork or each glyph pass first. */
  for(unsigned y=0;y<TM_SAMPLE_H;y+=2)for(unsigned x=0;x<TM_SAMPLE_W;x+=2) {
   Uint32 base=state.output[(TM_SAMPLE_Y+y+1)*TM_SAMPLE_W+x+1];
   menu_font.samples[y*TM_SAMPLE_W+x]=menu_font.samples[y*TM_SAMPLE_W+x+1]=base;
   menu_font.samples[(y+1)*TM_SAMPLE_W+x]=menu_font.samples[(y+1)*TM_SAMPLE_W+x+1]=base;
  }
 }
 const Uint8 *roles=menu_font.payload+TM_PLANE;
 for(unsigned c=0;c<menu_font.count;c++) {
  const struct TmCommand *command=&menu_font.command[c];
  const struct TmGlyph *g=&menu_font.glyph[command->id];
  unsigned ax=(command->id%16)*TM_CW+TM_INSET,ay=(command->id/16)*TM_CH+TM_INSET;
  for(unsigned y=0;y<g->h*TL_D;y++)for(unsigned x=0;x<g->w*TL_D;x++) {
   unsigned p=(ay+y)*TM_AW+ax+x,a=menu_font.payload[p];if(!a)continue;
   SDL_Color color=state.expected_palette[tm_index(roles[p],command->value)];
   Uint32 src=((Uint32)color.r<<16)|((Uint32)color.g<<8)|color.b;
   unsigned ox=command->x*TL_D+x,oy=command->y*TL_D+y;
   Uint32 *out=reduce?&menu_font.samples[(oy-TM_SAMPLE_Y)*TM_SAMPLE_W+ox]:&state.output[oy*TM_SAMPLE_W+ox];
   Uint32 dst=*out,result=UINT32_C(0xff000000);
   for(unsigned shift=0;shift<=16;shift+=8)result|=((((src>>shift)&255)*a+((dst>>shift)&255)*(255-a)+127)/255)<<shift;
   *out=result;
  }
 }
 if(reduce) {
  for(unsigned y=0;y<TM_SAMPLE_H;y+=2)for(unsigned x=0;x<TM_SAMPLE_W;x+=2) {
   const Uint32 *q=&menu_font.samples[y*TM_SAMPLE_W+x];
   Uint32 result=UINT32_C(0xff000000);
   for(unsigned shift=0;shift<=16;shift+=8) {
    unsigned sum=((q[0]>>shift)&255)+((q[1]>>shift)&255)+
                 ((q[TM_SAMPLE_W]>>shift)&255)+((q[TM_SAMPLE_W+1]>>shift)&255);
    result|=((sum+2)/4)<<shift;
   }
   /* Only the original native2x nearest-sampled texel is replaced. Cells with
    * zero font coverage reproduce their exact original underlay sample. */
   state.output[(TM_SAMPLE_Y+y+1)*TM_SAMPLE_W+x+1]=result;
  }
 }
 return true;
}

/* Translate an entire shaped run once, in units of 1/512 canonical pixel.
 * Interpolate alpha and premultiplied color together, then perform one over
 * operation per destination pixel. Splitting the fractional translation into
 * two independently blended passes would change both coverage and overlaps. */
static void tm_natural_pass(const CommonMenuRun *run,unsigned row,bool contour,int value)
{
 int left512=160*TL_D*512-(int)run->advance256+run->dx*512;
 int left=left512/512,phase=left512%512;
 if(phase<0){phase+=512;--left;}
 int top=(104+13*(int)row)*TL_D+run->dy;
 const Uint8 *mask=contour?run->stroke:run->alpha;
 for(unsigned y=0;y<run->height;y++)for(unsigned x=0;x<run->width+(phase!=0);x++) {
  unsigned alpha=0,premul[3]={0,0,0};
  for(unsigned side=0;side<2;side++) {
   if((side&&x==0)||x-side>=run->width)continue;
   unsigned weight=side?(unsigned)phase:512-(unsigned)phase;
   if(!weight)continue;
   unsigned p=y*run->pitch+x-side,a=mask[p];if(!a)continue;
   SDL_Color color=state.expected_palette[tm_index(contour?13:run->roles[p],value)];
   alpha+=a*weight;
   premul[0]+=color.b*a*weight;premul[1]+=color.g*a*weight;premul[2]+=color.r*a*weight;
  }
  unsigned a=(alpha+256)/512;if(!a)continue;
  unsigned pos=(unsigned)(top+(int)y)*TM_SAMPLE_W+(unsigned)(left+(int)x);
  Uint32 dst=menu_font.samples[pos],result=(a+(((dst>>24)*(255-a)+127)/255))<<24;
  for(unsigned c=0;c<3;c++) {
   unsigned v=(premul[c]+255*256)/(255*512)+(((dst>>(8*c))&255)*(255-a)+127)/255;
   result|=v<<(8*c);
  }
  menu_font.samples[pos]=result;
 }
}
static bool tm_render_natural(void)
{
 if(!tm_natural_check())return false;
 CommonMenuRun run[7];
 for(unsigned row=0;row<7;row++) {
  CommonMenuRun *r=&run[row];
  if(!common_menu_runs_get(COMMON_MENU_MAIN,menu_font.natural_id[row],r)||
     !r->text||strcmp(r->text,tm_natural_text[row])||!r->alpha||!r->roles||!r->stroke||
     !r->width||r->width>TM_SAMPLE_W||!r->height||r->height>TM_SAMPLE_H||r->pitch!=r->width||
     r->role_min!=13||r->role_max!=15||r->advance256>TM_SAMPLE_W*256||
     r->dx < -TM_SAMPLE_W||r->dx>TM_SAMPLE_W||r->dy < -TM_SAMPLE_H||r->dy>TM_SAMPLE_H)
   goto invalid;
  int left512=160*TL_D*512-(int)r->advance256+r->dx*512;
  int top=(104+13*(int)row)*TL_D+r->dy;
  if(left512<0||left512+(int)r->width*512>TM_SAMPLE_W*512||
     top<TM_SAMPLE_Y||top+(int)r->height>TM_SAMPLE_Y+TM_SAMPLE_H)goto invalid;
 }
 if(!tm_natural_check())return false;
 /* Rebuild the immutable 14-operation base on every Present. In particular,
  * do not erase a selected row's rectangle: adjacent contours can overlap. */
 memset(menu_font.samples,0,TM_SAMPLE_BYTES);
 for(unsigned row=0;row<7;row++) {
  tm_natural_pass(&run[row],row,true,-10);
  tm_natural_pass(&run[row],row,false,-3);
 }
 if(menu_font.phase==TM_READY&&menu_font.selected>=0&&menu_font.selected<7)
  tm_natural_pass(&run[menu_font.selected],(unsigned)menu_font.selected,false,-1);
 return true;
invalid:
 menu_font.natural_ready=false;return false;
}

/* Other output geometry uses the same accepted atlas and original command
 * order. Resolve live palette roles into one premultiplied canonical layer;
 * only this font layer is integrated, never title artwork or palette indices.
 * The two accepted native paths above retain their exact per-pass rounding. */
static bool tm_render_portable(void)
{
 if(!tm_check()||(menu_font.phase!=TM_SAVED&&menu_font.phase!=TM_READY)||menu_font.in_run)return false;
 if(tm_render_natural())return true;
 if(!menu_font.payload)return false;
 memset(menu_font.samples,0,TL_OUT_BYTES);
 const Uint8 *roles=menu_font.payload+TM_PLANE;
 for(unsigned c=0;c<menu_font.count;c++) {
  const struct TmCommand *command=&menu_font.command[c];
  const struct TmGlyph *g=&menu_font.glyph[command->id];
  unsigned ax=(command->id%16)*TM_CW+TM_INSET,ay=(command->id/16)*TM_CH+TM_INSET;
  for(unsigned y=0;y<g->h*TL_D;y++)for(unsigned x=0;x<g->w*TL_D;x++) {
   unsigned p=(ay+y)*TM_AW+ax+x,a=menu_font.payload[p];if(!a)continue;
   SDL_Color color=state.expected_palette[tm_index(roles[p],command->value)];
   Uint32 src=((Uint32)color.r<<16)|((Uint32)color.g<<8)|color.b;
   unsigned pos=(command->y*TL_D+y)*TM_SAMPLE_W+command->x*TL_D+x;
   Uint32 dst=menu_font.samples[pos],result=(a+(((dst>>24)*(255-a)+127)/255))<<24;
   for(unsigned shift=0;shift<=16;shift+=8)result|=((((src>>shift)&255)*a+((dst>>shift)&255)*(255-a)+127)/255)<<shift;
   menu_font.samples[pos]=result;
  }
 }
 return true;
}
