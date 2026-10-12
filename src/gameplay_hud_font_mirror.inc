/* Private HUF1 ordered gameplay contexts. Included only by render_mirror.c.
 * Original font routines and indexed writes remain the source of authority. */
enum { FONT_SCENE_CELLS=2218,FONT_PIXELS=FONT_SCENE_CELLS*64,FONT_PERSIST_CELLS=2208,
 FONT_HISTORY_BYTES=FONT_PIXELS*20+FONT_SCENE_CELLS+FONT_PERSIST_CELLS*4 };
typedef struct {Sint16 x,y;Uint8 id,black,hue;Sint8 value;} FontCommand;
typedef struct {
 SDL_Rect rect;SDL_Surface *surface;void *pixels;SDL_PixelFormat *format;int pitch;
 unsigned offset,logical_offset,used;bool canvas_live,output_live;
} FontScene;
typedef struct {bool valid,poison,seen,blank,inflight,expect_erase;char text[256];} FontPersistent;
static FontScene font_scenes[2];
static FontPersistent font_persistent[2];
static FontCommand font_commands[100];
static unsigned font_command_count,font_command_next;
static int font_context=-1;
static bool font_glyph_active,font_gameplay,font_suspended;
static SDL_Surface *font_source_surface;
static void *font_source_pixels;
static SDL_PixelFormat *font_source_format;
static int font_source_pitch,font_density;
static uint64_t font_generation,font_output_generation,font_saved_generation;
static Uint32 font_output_palette[256];
static Uint8 *font_history;
static Uint32 *font_under,*font_saved_under,*font_green_under;
static Uint16 *font_green_first;
static Uint8 *font_lower_owner,*font_saved_lower_owner,*font_owner,*font_saved_owner;
static Uint8 *font_cloud,*font_green_owner,*font_selected;
static Uint8 *font_pre,*font_post,*font_powner,*font_psaved_owner;
static const SDL_Rect font_prects[2]={{268,118,52,8},{20,190,224,8}};
static const unsigned font_poffset[2]={0,416};
static bool fixed_text_owned(void);
static bool components_owned(void);
static bool indicators_owned(void);
static bool hud_sprite_decode(unsigned int table,unsigned int index,unsigned int max_w,unsigned int max_h,Uint8 *indices,Uint8 *opaque);
static bool font_runtime_source(void)
{
 HudFontGlyph glyphs[127];
 if(sprite_table[TINY_FONT].count!=127)return false;
 for(unsigned i=0;i<127;i++){const Sprite *s=&sprite_table[TINY_FONT].sprite[i];glyphs[i]=(HudFontGlyph){s->width,s->height,s->size,s->data};}
 return hud_font_source_matches(font_ascii,glyphs);
}
static bool font_source_matches(void)
{
 return VGAScreenSeg&&VGAScreenSeg==font_source_surface&&VGAScreenSeg->pixels&&VGAScreenSeg->pixels==font_source_pixels&&
  VGAScreenSeg->format&&VGAScreenSeg->format==font_source_format&&VGAScreenSeg->pitch==font_source_pitch&&
  VGAScreenSeg->w==320&&VGAScreenSeg->h==200&&VGAScreenSeg->format->BitsPerPixel==8&&VGAScreenSeg->format->BytesPerPixel==1;
}
static bool font_scene_source(const FontScene *r)
{
 return game_screen&&game_screen==r->surface&&game_screen->pixels&&game_screen->pixels==r->pixels&&
  game_screen->format&&game_screen->format==r->format&&game_screen->pitch==r->pitch&&
  game_screen->w==320&&game_screen->h==200&&game_screen->format->BitsPerPixel==8&&game_screen->format->BytesPerPixel==1;
}
static bool font_intersects(SDL_Rect a,SDL_Rect b)
{return a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y;}
static bool font_scene_owned(const FontScene *r,const Uint8 *owners)
{return r->used&&memchr(owners+r->offset,1,r->used)!=NULL;}
static bool font_owned(void)
{
 if(!font_history)return false;
 for(unsigned i=0;i<2;i++)if(font_scene_owned(font_scenes+i,font_owner))return true;
 return memchr(font_powner,1,FONT_PERSIST_CELLS)!=NULL;
}
static bool font_allocate(void)
{
 if(font_history)return true;
 font_history=calloc(1,FONT_HISTORY_BYTES);if(!font_history)return false;
 Uint8 *p=font_history;
 font_under=(Uint32 *)p;p+=FONT_PIXELS*4;font_saved_under=(Uint32 *)p;p+=FONT_PIXELS*4;
 font_green_under=(Uint32 *)p;p+=FONT_PIXELS*4;font_green_first=(Uint16 *)p;p+=FONT_PIXELS*2;
 font_lower_owner=p;p+=FONT_PIXELS;font_saved_lower_owner=p;p+=FONT_PIXELS;
 font_owner=p;p+=FONT_PIXELS;font_saved_owner=p;p+=FONT_PIXELS;
 font_cloud=p;p+=FONT_PIXELS;font_green_owner=p;p+=FONT_PIXELS;
 font_selected=p;p+=FONT_SCENE_CELLS;font_pre=p;p+=FONT_PERSIST_CELLS;font_post=p;p+=FONT_PERSIST_CELLS;
 font_powner=p;p+=FONT_PERSIST_CELLS;font_psaved_owner=p;
 font_scenes[0].offset=0;font_scenes[0].logical_offset=0;
 font_scenes[1].offset=808*64;font_scenes[1].logical_offset=808;
 return true;
}
/* Text is deliberately outside regions[]. Stripping cannot enlarge the original
 * local-restore closure or revoke a neighboring scene region. */
static void font_strip_scene(unsigned which)
{
 FontScene *r=font_scenes+which;
 if(!font_history||!r->canvas_live)return;
 if(!font_scene_source(r)||!canvas||font_density!=game_probe_density){ready=false;last_output_valid=false;r->canvas_live=false;
  if(font_context==(int)which){font_context=-1;font_glyph_active=false;}
  memset(font_owner+r->offset,0,r->used);render_mirror_unsupported("font-scene-lease");return;}
 int d=font_density;
 for(int y=0;y<r->rect.h;y++)for(int x=0;x<r->rect.w;x++) {
  unsigned logical=(unsigned)(y*r->rect.w+x),base=r->offset+logical*d*d;bool owned=false;
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   unsigned k=base+(unsigned)(sy*d+sx);if(!font_owner[k])continue;owned=true;
   int px=(r->rect.x+x)*d+sx,py=(r->rect.y+y)*d+sy,n=py*canvas->w+px;
   ((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px]=font_under[k];hd_owner[n]=font_lower_owner[k];
   cloud_owner[n]=font_cloud[k];green_first[n]=font_green_first[k];
   if(font_green_first[k]){green_under[n]=font_green_under[k];green_under_owner[n]=font_green_owner[k];}
   font_owner[k]=0;
  }
  if(owned)selected[(r->rect.y+y)*320+r->rect.x+x]=font_selected[r->logical_offset+logical];
 }
 r->canvas_live=false;
 if(font_context==(int)which){font_context=-1;font_glyph_active=false;}
}
static void font_before_effect(SDL_Rect footprint)
{
 if(!font_gameplay||!font_history)return;
 for(unsigned i=0;i<2;i++)if(font_scenes[i].canvas_live&&font_intersects(font_scenes[i].rect,footprint))font_strip_scene(i);
}
static bool font_pixel(int x,int y,Uint8 index,int style)
{
 if(!font_gameplay||!font_history)return false;
 if(font_context>=0&&font_glyph_active) {
  FontScene *r=font_scenes+font_context;int dx=x-r->rect.x,dy=y-r->rect.y,d=font_density;
  if(style!=MIRROR_NORMAL||dx<0||dy<0||dx>=r->rect.w||dy>=r->rect.h){font_strip_scene((unsigned)font_context);return false;}
  unsigned logical=(unsigned)(dy*r->rect.w+dx),base=r->offset+logical*d*d;
  font_selected[r->logical_offset+logical]=0;
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   unsigned k=base+(unsigned)(sy*d+sx);int n=(y*d+sy)*canvas->w+x*d+sx;
   font_under[k]=palette_rgb(index);font_lower_owner[k]=0;font_cloud[k]=0;font_green_first[k]=0;
   font_owner[k]=1;hd_owner[n]=1;
  }
  selected[y*320+x]=1;return true;
 }
 if(style!=MIRROR_NORMAL){font_before_effect((SDL_Rect){x,y,1,1});return false;}
 for(unsigned i=0;i<2;i++) {
  FontScene *r=font_scenes+i;if(!r->canvas_live||x<r->rect.x||x>=r->rect.x+r->rect.w||y<r->rect.y||y>=r->rect.y+r->rect.h)continue;
  unsigned logical=(unsigned)((y-r->rect.y)*r->rect.w+x-r->rect.x),base=r->offset+logical*font_density*font_density;
  memset(font_owner+base,0,(size_t)font_density*font_density);font_selected[r->logical_offset+logical]=0;
 }
 return false;
}
static Uint32 font_blend(Uint32 lower,Uint32 color,unsigned alpha)
{
 Uint32 out=0xff000000u;for(int shift=0;shift<24;shift+=8)
  out|=((((color>>shift)&255)*alpha+((lower>>shift)&255)*(255-alpha)+127)/255)<<shift;
 return out;
}
static bool font_plan(int x,int y,const char *text,unsigned hue,int value,unsigned maxbytes,bool full,SDL_Rect *box)
{
 font_command_count=font_command_next=0;
 if(!text)return false;
 unsigned len=0;
 for(;len<=maxbytes&&text[len];len++)if((unsigned char)text[len]>=128)return false;
 if(len>maxbytes)return false;
 int left=320,top=200,right=0,bottom=0;
 for(unsigned pass=0;pass<(full?5u:1u);pass++) {
  int px=x,py=y,bright=0;bool black=full&&pass<4;
  if(black){if(pass==0)px--;if(pass==1)px++;if(pass==2)py--;if(pass==3)py++;}
  for(unsigned i=0;i<len;i++) {
   unsigned c=(unsigned char)text[i];if(c==' '){px+=6;continue;}if(c=='~'){bright=bright?0:4;continue;}
   int id=font_ascii[c];if(id<0)continue;if(id>=86)return false;
   unsigned w=hud_font_width((unsigned)id),h=hud_font_height((unsigned)id);if(!w||!h||font_command_count>=100)return false;
   font_commands[font_command_count++]=(FontCommand){(Sint16)px,(Sint16)py,(Uint8)id,(Uint8)black,(Uint8)(black?0:hue),(Sint8)(black?-1:value+bright)};
   left=MIN(left,px);top=MIN(top,py);right=MAX(right,px+(int)w);bottom=MAX(bottom,py+(int)h);px+=(int)w+1;
  }
 }
 *box=font_command_count?(SDL_Rect){left,top,right-left,bottom-top}:(SDL_Rect){x,y,0,0};return true;
}
void render_mirror_text_begin(SDL_Surface *surface,unsigned kind,int x,int y,const char *text,unsigned hue,int value)
{
 if(font_context>=0)font_strip_scene((unsigned)font_context);
 if(!font_gameplay||font_suspended||!hud_font_ready()||!active||reject_reason||surface!=game_screen||suppress||
  game_probe_original_reference||!font_source_matches()||!font_runtime_source()||!hud_font_palette_matches(rgb_palette)||kind>1)return;
 if((kind==0&&(x!=30||y!=175||hue!=2||value!=4))||(kind==1&&(x!=28||(y!=8&&y!=28)||hue!=2||value!=6)))return;
 if(kind==0)for(unsigned i=0;i<=20&&text&&text[i];i++)if(text[i]<'0'||text[i]>'9')return;
 FontScene *r=font_scenes+kind;if(r->canvas_live)font_strip_scene(kind);
 SDL_Rect box;if(!font_plan(x,y,text,hue,value,20,true,&box)||!box.w||box.x<24||box.y<0||box.x+box.w>288||box.y+box.h>184||
  box.w>(kind?141:101)||box.h>(kind?10:8))return;
 if(!font_allocate())return;
 r->rect=box;r->surface=surface;r->pixels=surface->pixels;r->format=surface->format;r->pitch=surface->pitch;
 r->used=(unsigned)(box.w*box.h*font_density*font_density);r->canvas_live=true;r->output_live=false;
 memset(font_owner+r->offset,0,r->used);memset(font_saved_owner+r->offset,0,r->used);
 int d=font_density;
 for(int yy=0;yy<box.h;yy++)for(int xx=0;xx<box.w;xx++) {
  unsigned logical=(unsigned)(yy*box.w+xx),base=r->offset+logical*d*d;
  font_selected[r->logical_offset+logical]=selected[(box.y+yy)*320+box.x+xx];
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   unsigned k=base+(unsigned)(sy*d+sx);int px=(box.x+xx)*d+sx,py=(box.y+yy)*d+sy,n=py*canvas->w+px;
   font_under[k]=((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px];font_lower_owner[k]=hd_owner[n];
   font_cloud[k]=cloud_owner[n];font_green_first[k]=green_first[n];
   font_green_under[k]=green_first[n]?green_under[n]:0;font_green_owner[k]=green_first[n]?green_under_owner[n]:0;
  }
 }
 font_context=(int)kind;font_glyph_active=false;
}
void render_mirror_text_glyph_begin(SDL_Surface *surface,int x,int y,unsigned table,unsigned id,bool black,unsigned hue,int value)
{
 if(font_context<0)return;
 FontScene *r=font_scenes+font_context;
 if(font_glyph_active||font_command_next>=font_command_count||surface!=r->surface||!font_scene_source(r)){font_strip_scene((unsigned)font_context);return;}
 FontCommand c=font_commands[font_command_next];
 if(table!=TINY_FONT||id!=c.id||x!=c.x||y!=c.y||black!=(c.black!=0)||hue!=c.hue||value!=c.value){font_strip_scene((unsigned)font_context);return;}
 font_command_next++;font_glyph_active=true;int d=font_density;
 Uint8 index=black?0:(Uint8)(((Uint8)hue<<4)|(7+(Sint8)value));Uint32 color=palette_rgb(index);
 for(unsigned yy=0;yy<hud_font_height(id)*(unsigned)d;yy++)for(unsigned xx=0;xx<hud_font_width(id)*(unsigned)d;xx++) {
  Uint8 alpha=hud_font_alpha(id,(int)xx,(int)yy,d);if(!alpha)continue;
  int px=x*d+(int)xx,py=y*d+(int)yy,n=py*canvas->w+px;
  unsigned logical=(unsigned)((py/d-r->rect.y)*r->rect.w+px/d-r->rect.x),k=r->offset+logical*d*d+(py%d)*d+px%d;
  Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch)+px;*p=font_blend(*p,color,alpha);
  font_owner[k]=1;hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;selected[(py/d)*320+px/d]=1;
 }
}
void render_mirror_text_glyph_end(void){font_glyph_active=false;}
void render_mirror_text_end(void)
{
 if(font_context>=0){if(font_glyph_active||font_command_next!=font_command_count)font_strip_scene((unsigned)font_context);font_context=-1;}
 font_glyph_active=false;
}
static int font_pcell(int x,int y)
{
 if(x>=268&&x<320&&y>=118&&y<126)return (y-118)*52+x-268;
 if(x>=20&&x<244&&y>=190&&y<198)return 416+(y-190)*224+x-20;
 return -1;
}
static bool font_cached(void)
{
 return font_history&&(font_output_generation||font_saved_generation||font_scenes[0].output_live||font_scenes[1].output_live||
  memchr(font_powner,1,FONT_PERSIST_CELLS)||memchr(font_psaved_owner,1,FONT_PERSIST_CELLS));
}
static bool font_cached_indices_match(void)
{
 if(!font_source_matches()||font_density!=game_probe_density||(font_density!=4&&font_density!=8)||
  font_output_generation!=font_generation||(font_saved_generation&&font_saved_generation!=font_generation))return false;
 /* Saved ownership cannot outlive its generation, including a lost zero. */
 if(have_fade_saved&&(font_saved_generation!=font_generation||memcmp(font_powner,font_psaved_owner,FONT_PERSIST_CELLS)))return false;
 for(unsigned i=0;i<2;i++)if(font_scenes[i].output_live) {
  const FontScene *r=font_scenes+i;int d=font_density;
  if(have_fade_saved&&memcmp(font_owner+r->offset,font_saved_owner+r->offset,r->used))return false;
  if(!font_scene_source(r)||!canvas||!canvas->pixels||!hd_owner||canvas->w!=320*d||canvas->h!=200*d)return false;
  for(int y=0;y<r->rect.h;y++)for(int x=0;x<r->rect.w;x++)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   unsigned k=r->offset+(unsigned)((y*r->rect.w+x)*d*d+sy*d+sx);
   if(font_owner[k]&&hd_owner[((r->rect.y+y)*d+sy)*canvas->w+(r->rect.x+x)*d+sx]!=1)return false;
  }
 }
 for(int y=0;y<200;y++)if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320))return false;
 return true;
}
static void font_cache_retained(void)
{
 bool scene=false;
 if(hd_owner&&canvas)scene=memchr(hd_owner,1,(size_t)canvas->w*canvas->h)||memchr(hd_owner,2,(size_t)canvas->w*canvas->h);
 last_output_scene_hd=scene;
 bool retained=scene||memchr(hud_output_owner,1,sizeof(hud_output_owner))||components_owned()||indicators_owned()||fixed_text_owned()||font_owned();
 last_output_valid=last_output_valid&&retained;
 if(!retained){have_fade_saved=false;fade_mode=0;}
}
/* bits1=level,2=message,4=cash,8=name. Never remove another field's history. */
static void font_clear_cached(unsigned bits)
{
 if(!font_cached())return;
 int d=font_density;
 bool verified=(d==4||d==8)&&output&&output->w==320*d&&output->h==200*d&&font_output_generation==font_generation&&
  (!font_saved_generation||font_saved_generation==font_generation)&&font_cached_indices_match()&&
  memcmp(font_output_palette,rgb_palette,sizeof(font_output_palette))==0&&
  (!have_fade_saved||(fade_saved&&fade_saved->w==output->w&&fade_saved->h==output->h));
 if(!verified){ready=false;last_output_valid=false;have_fade_saved=false;fade_mode=0;}
 for(unsigned which=0;which<2;which++) {
  FontScene *r=font_scenes+which;if(!(bits&(4u<<which))||!r->output_live)continue;
  for(int y=0;y<r->rect.h;y++)for(int x=0;x<r->rect.w;x++)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   unsigned k=r->offset+(unsigned)((y*r->rect.w+x)*d*d+sy*d+sx);
   int px=(r->rect.x+x-24)*d+sx,py=(r->rect.y+y)*d+sy;
   if(verified&&font_owner[k]){((Uint32 *)((Uint8 *)output->pixels+py*output->pitch))[px]=font_under[k];hd_owner[py*canvas->w+px+24*d]=font_lower_owner[k];}
   if(verified&&font_saved_owner[k]&&have_fade_saved)((Uint32 *)((Uint8 *)fade_saved->pixels+py*fade_saved->pitch))[px]=font_saved_under[k];
   font_owner[k]=font_saved_owner[k]=0;
  }
  r->output_live=false;
 }
 for(unsigned which=0;which<2;which++)if(bits&(1u<<which)) {
  SDL_Rect r=font_prects[which];unsigned off=font_poffset[which];
  for(int y=0;y<r.h;y++)for(int x=0;x<r.w;x++) {
   unsigned k=off+(unsigned)(y*r.w+x);if(!font_powner[k]&&!font_psaved_owner[k])continue;
   Uint8 index=last_output_indices[(r.y+y)*320+r.x+x];
   if(verified)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
    if(font_powner[k])((Uint32 *)((Uint8 *)output->pixels+((r.y+y)*d+sy)*output->pitch))[(r.x+x)*d+sx]=palette_rgb(index);
    if(font_psaved_owner[k]&&have_fade_saved)((Uint32 *)((Uint8 *)fade_saved->pixels+((r.y+y)*d+sy)*fade_saved->pitch))[(r.x+x)*d+sx]=0xff000000u|(fade_saved_palette[index]&0xffffffu);
   }
   font_powner[k]=font_psaved_owner[k]=0;
  }
 }
 if(!font_owned())font_output_generation=0;
 bool saved=memchr(font_psaved_owner,1,FONT_PERSIST_CELLS)!=NULL;
 for(unsigned i=0;i<2;i++)saved=saved||font_scene_owned(font_scenes+i,font_saved_owner);
 if(!saved)font_saved_generation=0;
 if(verified)font_cache_retained();
}
static void font_reset(void)
{
 if(font_history)for(unsigned i=0;i<2;i++)font_strip_scene(i);
 font_clear_cached(15);font_gameplay=font_suspended=false;font_context=-1;font_glyph_active=false;
 ++font_generation;if(!font_generation)++font_generation;
 font_source_surface=NULL;font_source_pixels=NULL;font_source_format=NULL;font_source_pitch=0;
 memset(font_persistent,0,sizeof(font_persistent));hud_font_forget_source();
}
static void font_shutdown(void)
{font_reset();hud_font_shutdown();free(font_history);font_history=NULL;memset(font_scenes,0,sizeof(font_scenes));}
static void font_check_mode(void)
{
 if(font_gameplay&&(twoPlayerMode||galagaMode||font_density!=game_probe_density||!font_source_matches()||!font_runtime_source()))font_reset();
}
static void font_copy_indices(unsigned which,Uint8 *destination)
{
 SDL_Rect r=font_prects[which];unsigned off=font_poffset[which];
 for(int y=0;y<r.h;y++)memcpy(destination+off+y*r.w,(Uint8 *)VGAScreenSeg->pixels+(r.y+y)*VGAScreenSeg->pitch+r.x,(size_t)r.w);
}
static bool font_indices_equal(unsigned which,const Uint8 *reference)
{
 SDL_Rect r=font_prects[which];unsigned off=font_poffset[which];
 for(int y=0;y<r.h;y++)if(memcmp(reference+off+y*r.w,(Uint8 *)VGAScreenSeg->pixels+(r.y+y)*VGAScreenSeg->pitch+r.x,(size_t)r.w))return false;
 return true;
}
static void font_start(SDL_Surface *source)
{
 if(!hud_font_load(game_probe_assets)||sprite_table[TINY_FONT].count!=127)return;
 HudFontGlyph glyphs[127];for(unsigned i=0;i<127;i++){const Sprite *s=&sprite_table[TINY_FONT].sprite[i];glyphs[i]=(HudFontGlyph){s->width,s->height,s->size,s->data};}
 if(!hud_font_capture(source->pixels,source->pitch,font_ascii,glyphs)||!font_allocate())return;
 font_source_surface=source;font_source_pixels=source->pixels;font_source_format=source->format;font_source_pitch=source->pitch;
 font_gameplay=true;font_density=game_probe_density;
 for(unsigned i=0;i<2;i++){font_copy_indices(i,font_pre);font_persistent[i].blank=true;}
}
static void font_begin(void)
{
 if(!font_history||!font_gameplay)return;
 font_suspended=false;
 font_context=-1;font_glyph_active=false;font_output_generation=font_saved_generation=0;
 for(unsigned i=0;i<2;i++) {
  FontScene *r=font_scenes+i;
  if(r->used){memset(font_owner+r->offset,0,r->used);memset(font_saved_owner+r->offset,0,r->used);}
  r->used=0;r->canvas_live=r->output_live=false;
 }
 memset(font_powner,0,FONT_PERSIST_CELLS);memset(font_psaved_owner,0,FONT_PERSIST_CELLS);
}
static void font_suspend(void)
{
 if(font_history)for(unsigned i=0;i<2;i++)font_strip_scene(i);
 font_clear_cached(15);if(font_gameplay)font_suspended=true;
}
static bool font_ptext(unsigned which,const char *text)
{
 if(!text)return false;
 SDL_Rect r=font_prects[which];unsigned limit=which?255:10,len=0;int x=r.x;
 for(;len<=limit&&text[len];len++) {
  unsigned c=(unsigned char)text[len];if(c>=128)return false;
  if(c==' '){x+=6;continue;}if(c=='~')continue;
  int id=font_ascii[c];if(id<0)continue;if(id>=86)return false;
  unsigned w=hud_font_width((unsigned)id),h=hud_font_height((unsigned)id);
  if(!w||!h||x<r.x||x+(int)w>r.x+r.w||h>(unsigned)r.h)return false;
  x+=(int)w+1;
 }
 if(len>limit||x>r.x+r.w+1)return false;
 memcpy(font_persistent[which].text,text,len+1);return true;
}
void render_mirror_text_level_begin(SDL_Surface *surface,const char *text)
{
 if(!font_gameplay)return;
 FontPersistent *p=font_persistent;
 font_clear_cached(1);
 if(surface!=VGAScreenSeg||p->seen||!font_source_matches()||!font_runtime_source()){p->valid=false;p->poison=true;return;}
 p->seen=true;p->valid=false;
 if(p->poison||!font_indices_equal(0,font_pre)||!font_ptext(0,text)){p->poison=true;return;}
 p->inflight=true;
}
void render_mirror_text_level_end(void)
{
 FontPersistent *p=font_persistent;if(!font_gameplay||!p->inflight)return;p->inflight=false;
 if(!font_source_matches()){p->poison=true;return;}font_copy_indices(0,font_post);p->valid=true;p->blank=false;
}
/* Actual OPTION36 erase, complete opaque footprint and post-write verification. */
static bool font_message_erase_matches(bool completed)
{
 Uint8 indices[228*9],opaque[228*9];
 if(!hud_sprite_decode(OPTION_SHAPES,36,228,9,indices,opaque)||
  sprite_table[OPTION_SHAPES].sprite[36].width!=228||sprite_table[OPTION_SHAPES].sprite[36].height!=9)return false;
 for(unsigned i=0;i<228*9;i++)if(opaque[i]!=255)return false;
 if(completed)for(int y=0;y<9;y++)
  if(memcmp(indices+y*228,(Uint8 *)VGAScreenSeg->pixels+(189+y)*VGAScreenSeg->pitch+16,228))return false;
 return true;
}
void render_mirror_text_message_begin(const char *text,bool will_erase)
{
 if(!font_gameplay)return;
 FontPersistent *p=font_persistent+1;font_clear_cached(2);
 p->valid=p->inflight=false;p->expect_erase=will_erase;
 if(!font_source_matches()||!font_runtime_source()||p->poison||(will_erase&&!font_message_erase_matches(false))||(!will_erase&&(!p->blank||!font_indices_equal(1,font_pre)))||!font_ptext(1,text)){p->poison=true;return;}
 p->inflight=true;p->blank=false;
}
void render_mirror_text_message_backdrop(void)
{
 FontPersistent *p=font_persistent+1;if(!font_gameplay||!p->inflight)return;
 if(!font_source_matches()||(p->expect_erase&&!font_message_erase_matches(true))){p->inflight=false;p->poison=true;return;}
 font_copy_indices(1,font_pre);
}
void render_mirror_text_message_end(void)
{
 FontPersistent *p=font_persistent+1;if(!font_gameplay||!p->inflight)return;p->inflight=false;
 if(!font_source_matches()){p->poison=true;return;}font_copy_indices(1,font_post);p->valid=true;
}
void render_mirror_text_message_erase_begin(void)
{
 if(!font_gameplay)return;
 font_clear_cached(2);font_persistent[1].valid=font_persistent[1].inflight=false;font_persistent[1].blank=false;
}
void render_mirror_text_message_erased(bool help_prompt)
{
 if(!font_gameplay||!font_source_matches())return;
 if(!font_message_erase_matches(true)){font_persistent[1].poison=true;return;}
 font_copy_indices(1,font_pre);font_persistent[1].blank=!help_prompt;
}
static bool font_compose_persistent(unsigned which)
{
 FontPersistent *p=font_persistent+which;SDL_Rect r=font_prects[which];unsigned off=font_poffset[which];int d=font_density;
 if(!p->valid||p->poison||!font_indices_equal(which,font_post))return false;
 int x=r.x;
 for(unsigned i=0;p->text[i];i++) {
  unsigned c=(unsigned char)p->text[i];if(c==' '){x+=6;continue;}if(c=='~')continue;int id=font_ascii[c];if(id<0)continue;
  unsigned w=hud_font_width((unsigned)id),h=hud_font_height((unsigned)id);Uint8 opaque[48];
  if(!hud_sprite_decode(TINY_FONT,(unsigned)id,6,8,NULL,opaque)){memset(font_powner+off,0,(size_t)r.w*r.h);p->valid=false;return false;}
  for(unsigned y=0;y<h;y++)for(unsigned xx=0;xx<w;xx++) {
   bool owns=opaque[y*w+xx]!=0;
   for(int sy=0;sy<4&&!owns;sy++)for(int sx=0;sx<4;sx++)if(hud_font_alpha((unsigned)id,(int)xx*4+sx,(int)y*4+sy,4))owns=true;
   if(owns)font_powner[off+y*r.w+(unsigned)(x-r.x)+xx]=1;
  }
  x+=(int)w+1;
 }
 for(int y=0;y<r.h;y++)for(int xx=0;xx<r.w;xx++)if(font_powner[off+y*r.w+xx])
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)((Uint32 *)((Uint8 *)output->pixels+((r.y+y)*d+sy)*output->pitch))[(r.x+xx)*d+sx]=palette_rgb(font_pre[off+y*r.w+xx]);
 x=r.x;int bright=0;
 for(unsigned i=0;p->text[i];i++) {
  unsigned c=(unsigned char)p->text[i];if(c==' '){x+=6;continue;}if(c=='~'){bright=bright?0:4;continue;}int id=font_ascii[c];if(id<0)continue;
  Uint32 color=palette_rgb((Uint8)((which?0:12<<4)|(7+4+bright)));
  for(unsigned y=0;y<hud_font_height((unsigned)id)*(unsigned)d;y++)for(unsigned xx=0;xx<hud_font_width((unsigned)id)*(unsigned)d;xx++) {
   Uint8 alpha=hud_font_alpha((unsigned)id,(int)xx,(int)y,d);if(!alpha)continue;
   Uint32 *dst=(Uint32 *)((Uint8 *)output->pixels+(r.y*d+(int)y)*output->pitch)+x*d+xx;*dst=font_blend(*dst,color,alpha);
  }
  x+=(int)hud_font_width((unsigned)id)+1;
 }
 return memchr(font_powner+off,1,(size_t)r.w*r.h)!=NULL;
}
/* Must run before finish copies canvas into output, including defensive aborts. */
static void font_prepare_finish(void)
{if(font_context>=0)font_strip_scene((unsigned)font_context);}
static bool font_finish(bool accepted)
{
 if(!font_gameplay||!font_history)return false;
 bool retained=false;
 for(unsigned i=0;i<2;i++) {
  FontScene *r=font_scenes+i;r->output_live=accepted&&r->canvas_live&&font_scene_owned(r,font_owner);r->canvas_live=false;
  if(!r->output_live&&r->used)memset(font_owner+r->offset,0,r->used);
  retained=retained||r->output_live;
 }
 if(accepted&&!font_suspended&&hud_font_palette_matches(rgb_palette))for(unsigned i=0;i<2;i++)retained=font_compose_persistent(i)||retained;
 if(retained){font_output_generation=font_generation;memcpy(font_output_palette,rgb_palette,sizeof(font_output_palette));}
 return retained;
}
static void font_fade_save(void)
{
 if(!font_history||!font_output_generation)return;
 for(unsigned i=0;i<2;i++){FontScene *r=font_scenes+i;if(!r->output_live)continue;
  memcpy(font_saved_under+r->offset,font_under+r->offset,r->used*4);memcpy(font_saved_lower_owner+r->offset,font_lower_owner+r->offset,r->used);memcpy(font_saved_owner+r->offset,font_owner+r->offset,r->used);}
 memcpy(font_psaved_owner,font_powner,FONT_PERSIST_CELLS);font_saved_generation=font_output_generation;
}
static void font_fade_underlay(int steps)
{
 if(!font_history||!font_output_generation)return;
 int d=font_density;
 for(unsigned which=0;which<2;which++) {
  FontScene *r=font_scenes+which;if(!r->output_live)continue;
  for(int y=0;y<r->rect.h;y++)for(int x=0;x<r->rect.w;x++)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   unsigned k=r->offset+(unsigned)((y*r->rect.w+x)*d*d+sy*d+sx);if(!font_owner[k]||!font_saved_owner[k])continue;
   if(!font_lower_owner[k]){font_under[k]=palette_rgb(last_output_indices[(r->rect.y+y)*320+r->rect.x+x-24]);continue;}
   Uint32 target=fade_mode==1?0:fade_mode==2?0xffffffu:font_saved_under[k],color=0xff000000u;
   for(int shift=0;shift<24;shift+=8){int old=(font_under[k]>>shift)&255,want=(target>>shift)&255;color|=(Uint32)(old+(want-old)/steps)<<shift;}
   font_under[k]=color;
  }
 }
 memcpy(font_output_palette,rgb_palette,sizeof(font_output_palette));
}
