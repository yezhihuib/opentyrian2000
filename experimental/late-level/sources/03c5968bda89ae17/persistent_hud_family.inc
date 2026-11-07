/* Separate lifetime from the frame-only world canvas. All native stores still
 * execute unchanged. Only completed, ordered original operations can renew a
 * field. Equality is a currentness check, never an operation grant. */
#include "persistent_hud_family.h"
#include "native_writer_observer.h"
#include <sys/stat.h>
static bool family_scope(void);
static bool hud_sprite_decode(unsigned,unsigned,unsigned,unsigned,Uint8 *,Uint8 *);
enum { PH_NONE,PH_FRONT,PH_REAR,PH_GENERATOR,PH_WIPE,PH_ARMOR,PH_SHIELD,PH_MODE,PH_LEVEL,PH_MESSAGE,PH_ERASE };
enum { PH_STORE=1,PH_PIXEL,PH_RECT,PH_FILL_BEFORE,PH_FILL_AFTER,PH_SPRITE_BEGIN,PH_SPRITE_END,PH_GLYPH_BEGIN,PH_GLYPH_END,PH_BACKDROP };
typedef struct {int type,x,y,w,h,value,writer;} PhOp;
typedef struct {int x,y,id,value;} PhGlyph;
typedef struct {bool valid,blank;unsigned count;PhGlyph glyph[100];Uint8 pre[1792],post[1792];} PhText;
static struct {
 PersistentHudStatus status;
 SDL_Surface *surface;void *pixels;SDL_PixelFormat *format;Uint32 flags;
 const void *option_data[3],*font_data[127];
 char root[1024];bool attempted,resources_ok,live,suspended,bad,fill,composed,restore_pending,corner;
 unsigned kind,n,next,a,b,wipe_shield,fill_rows,fill_color;uint64_t serial,composed_serial;
 PhOp ops[8192];SDL_Rect fill_rect;
 Uint8 pristine[64000],observed[64000],static_ok[64000],touched[64000],owned[64000],snapshot[64000];
 Uint32 palette[256];PhText text[2];
} ph;
static const SDL_Rect ph_text_rect[2]={{268,118,52,8},{20,190,224,8}};
static bool ph_exterior(unsigned i){return i%320>=264||i/320>=184;}
static bool ph_requested(void)
{
 const char *e=getenv("PERSISTENT_HUD_ENABLE"),*d=getenv("PERSISTENT_HUD_ASSET_DIR");
 return e&&!strcmp(e,"1")&&d&&d[0]=='/'&&strlen(d)<sizeof ph.root;
}
static bool ph_surface(void)
{
 SDL_Surface *s=ph.surface;
 return ph.live&&s&&s==VGAScreenSeg&&s->pixels==ph.pixels&&s->format==ph.format&&s->flags==ph.flags&&
 s->w==320&&s->h==200&&s->pitch==320&&s->format&&s->format->format==SDL_PIXELFORMAT_INDEX8&&
 s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&!s->locked&&!SDL_MUSTLOCK(s)&&
 !s->clip_rect.x&&!s->clip_rect.y&&s->clip_rect.w==320&&s->clip_rect.h==200;
}
static bool ph_context(void)
{
 const char *d=getenv("PERSISTENT_HUD_ASSET_DIR");
 return ph_surface()&&ph_requested()&&d&&!strcmp(d,ph.root)&&render_mirror_family_requested()&&family_scope();
}
static void ph_reset(void)
{
 ph.restore_pending=ph.restore_pending||ph.composed;
 ph.live=ph.suspended=ph.composed=ph.fill=false;ph.kind=PH_NONE;ph.n=ph.next=0;
 ph.status.captured=ph.status.composed=false;ph.status.text_valid=ph.status.meters=ph.status.mode=0;
 ++ph.status.generation;++ph.serial;memset(ph.owned,0,sizeof ph.owned);memset(ph.text,0,sizeof ph.text);
}
static bool ph_fonts(void)
{
 HudFontGlyph g[127];if(sprite_table[TINY_FONT].count!=127)return false;
 for(unsigned i=0;i<127;i++){const Sprite *s=&sprite_table[TINY_FONT].sprite[i];if(ph.live&&s->data!=ph.font_data[i])return false;g[i]=(HudFontGlyph){s->width,s->height,s->size,s->data};}
 return hud_font_source_matches(font_ascii,g);
}
static bool ph_options(void)
{
 static const unsigned ids[3]={18,19,36},width[3]={10,10,228},height[3]={8,8,9},size[3]={80,80,2052};
 static const uint64_t hashes[3]={UINT64_C(0xd36b9afd4df898cf),UINT64_C(0xac3fca9154ec0310),UINT64_C(0x029ec9ec39f694b1)};
 if(sprite_table[OPTION_SHAPES].count!=47)return false;
 for(unsigned i=0;i<3;i++){
  const Sprite *s=&sprite_table[OPTION_SHAPES].sprite[ids[i]];
  if(!s->data||s->width!=width[i]||s->height!=height[i]||s->size!=size[i]||
     (ph.live&&s->data!=ph.option_data[i])||gameplay_hud_fnv64(s->data,s->size)!=hashes[i])return false;
 }
 return true;
}
static bool ph_modes(Uint8 p[2][80],Uint8 o[2][80])
{
 if(!ph_options())return false;
 for(unsigned i=0;i<2;i++)if(!hud_sprite_decode(OPTION_SHAPES,18+i,10,8,p[i],o[i])||
 sprite_table[OPTION_SHAPES].sprite[18+i].width!=10||sprite_table[OPTION_SHAPES].sprite[18+i].height!=8)return false;
 return hud_indicators_verify_modes((const Uint8 (*)[80])p,(const Uint8 (*)[80])o);
}
static bool ph_resources(const char *root)
{
 static const struct {const char *name;size_t bytes;uint64_t hash;} pins[]={
#include "persistent_hud_asset_pins.inc"
 };
 for(unsigned i=0;i<sizeof pins/sizeof *pins;i++){
  char path[1200];if(snprintf(path,sizeof path,"%s/%s",root,pins[i].name)>=(int)sizeof path)return false;
  struct stat st;if(stat(path,&st)||!S_ISREG(st.st_mode)||(uint64_t)st.st_size!=pins[i].bytes)return false;
  FILE *f=fopen(path,"rb");if(!f)return false;
  Uint8 buf[8192];uint64_t h=UINT64_C(14695981039346656037);size_t total=0,n;
  while((n=fread(buf,1,sizeof buf,f))!=0){total+=n;if(total>pins[i].bytes)break;for(size_t k=0;k<n;k++)h=(h^buf[k])*UINT64_C(1099511628211);}
  bool ok=!ferror(f)&&total==pins[i].bytes&&h==pins[i].hash;fclose(f);if(!ok)return false;
 }
 return true;
}
static void ph_copy_field(unsigned which,Uint8 *dest)
{SDL_Rect r=ph_text_rect[which];for(int y=0;y<r.h;y++)memcpy(dest+y*r.w,(Uint8 *)ph.pixels+(r.y+y)*320+r.x,(size_t)r.w);}
static bool ph_field_equal(unsigned which,const Uint8 *p)
{SDL_Rect r=ph_text_rect[which];for(int y=0;y<r.h;y++)if(memcmp(p+y*r.w,(Uint8 *)ph.pixels+(r.y+y)*320+r.x,(size_t)r.w))return false;return true;}
static void ph_start(SDL_Surface *s)
{
 if(!ph_requested()||!render_mirror_family_requested()||!family_scope())return;
 if(ph.attempted&&strcmp(ph.root,getenv("PERSISTENT_HUD_ASSET_DIR")))return;
 if(!ph.attempted){ph.attempted=true;strcpy(ph.root,getenv("PERSISTENT_HUD_ASSET_DIR"));ph.resources_ok=ph_resources(ph.root);}
 if(!ph.resources_ok)return;
 if(!s||s!=VGAScreenSeg||!s->pixels||!s->format||s->w!=320||s->h!=200||s->pitch!=320)return;
 if(!gameplay_hud_load(ph.root)||!hud_components_load(ph.root)||!hud_meters_load(ph.root)||!hud_indicators_load(ph.root)||!hud_fixed_text_load(ph.root)||!hud_font_load(ph.root))return;
 Uint8 modes[2][80],opaque[2][80];HudFontGlyph glyphs[127];
 if(!ph_modes(modes,opaque)||sprite_table[TINY_FONT].count!=127)return;
 for(unsigned i=0;i<127;i++){const Sprite *q=&sprite_table[TINY_FONT].sprite[i];glyphs[i]=(HudFontGlyph){q->width,q->height,q->size,q->data};}
 if(!gameplay_hud_capture(s->pixels,s->pitch)||!gameplay_hud_verify_modes((const Uint8 (*)[80])modes,(const Uint8 (*)[80])opaque)||
 !hud_components_capture(s->pixels,s->pitch)||!hud_meters_capture(s->pixels,s->pitch)||
 !hud_indicators_capture(s->pixels,s->pitch,(const Uint8 (*)[80])modes,(const Uint8 (*)[80])opaque)||
 !hud_fixed_text_capture(s->pixels,s->pitch)||!hud_font_capture(s->pixels,s->pitch,font_ascii,glyphs))return;
 ph.surface=s;ph.pixels=s->pixels;ph.format=s->format;ph.flags=s->flags;
 ph.option_data[0]=sprite_table[OPTION_SHAPES].sprite[18].data;
 ph.option_data[1]=sprite_table[OPTION_SHAPES].sprite[19].data;
 ph.option_data[2]=sprite_table[OPTION_SHAPES].sprite[36].data;
 for(unsigned i=0;i<127;i++)ph.font_data[i]=sprite_table[TINY_FONT].sprite[i].data;
 ph.live=true;
 if(!ph_context()){ph_reset();return;}
 memcpy(ph.pristine,s->pixels,64000);memcpy(ph.observed,s->pixels,64000);memset(ph.static_ok,1,64000);ph.corner=true;
 for(unsigned i=0;i<2;i++){ph_copy_field(i,ph.text[i].pre);ph.text[i].blank=true;}
 ph.status.captured=true;
}
static void ph_revoke_cell(unsigned i)
{
 ph.static_ok[i]=0;
 if(i%320>=248&&i%320<269&&i/320>=184)ph.corner=false;
 int x=(int)(i%320),y=(int)(i/320);
 for(unsigned k=0;k<2;k++){SDL_Rect r=ph_text_rect[k];if(x>=r.x&&x<r.x+r.w&&y>=r.y&&y<r.y+r.h){ph.text[k].valid=false;ph.text[k].blank=false;}}
 if(x>=270&&x<279&&y>=137&&y<195)hud_components_shield_wiped();
 if(x>=285&&x<312&&y>=44&&y<52){hud_indicators_mode_wiped();ph.status.mode=0;}
 unsigned bit=0;if(x>=289&&x<311){if(y>=17&&y<20)bit=HUD_METER_FRONT;if(y>=38&&y<41)bit=HUD_METER_REAR;}
 if(x>=269&&x<277&&y>=12&&y<104)bit=HUD_METER_GENERATOR;
 if(x>=307&&x<316&&y>=137&&y<195)bit=HUD_METER_ARMOR;
 if(bit)hud_meters_revoke(bit);
}
static void ph_touch(size_t off,size_t n)
{
 if(!ph_context()){ph_reset();return;}
 ++ph.serial;
 for(size_t i=off;i<off+n;i++)if(ph_exterior((unsigned)i)){
  if(ph.kind){ph.touched[i]=1;ph.static_ok[i]=0;}
  else ph_revoke_cell((unsigned)i);
  ph.observed[i]=((Uint8 *)ph.pixels)[i];
 }
}
static void ph_add(int type,int x,int y,int w,int h,int value,int writer)
{
 if(ph.n>=sizeof ph.ops/sizeof *ph.ops){ph.bad=true;return;}
 ph.ops[ph.n++]=(PhOp){type,x,y,w,h,value,writer};
}
static void ph_event(int type,int x,int y,int w,int h,int value,int writer)
{
 if(!ph.kind)return;
 PhOp op={type,x,y,w,h,value,writer};
 if(ph.next>=ph.n){ph.bad=true;return;}
 const PhOp *p=ph.ops+ph.next;
 if(op.type!=p->type||op.x!=p->x||op.y!=p->y||op.w!=p->w||op.h!=p->h||op.value!=p->value||op.writer!=p->writer){ph.bad=true;return;}
 ++ph.next;
}
static void ph_rect_plan(int x,int y,int w,int h,int c)
{
 ph_add(PH_STORE,x,y,w,1,c,NWO_RECT_SPAN);ph_add(PH_RECT,x,y,w,1,0,0);
 ph_add(PH_STORE,x,y+h-1,w,1,c,NWO_RECT_SPAN);ph_add(PH_RECT,x,y+h-1,w,1,0,0);
 for(int j=1;j<h-1;j++){ph_add(PH_STORE,x,y+j,1,1,c,NWO_RECT_SIDE);ph_add(PH_PIXEL,x,y+j,1,1,c,MIRROR_NORMAL);}
 for(int j=1;j<h-1;j++){ph_add(PH_STORE,x+w-1,y+j,1,1,c,NWO_RECT_SIDE);ph_add(PH_PIXEL,x+w-1,y+j,1,1,c,MIRROR_NORMAL);}
}
static void ph_fill_plan(int x,int y,int w,int h,int c)
{ph_add(PH_FILL_BEFORE,x,y,w,h,c,NWO_SDL_VGA_FILL);ph_add(PH_FILL_AFTER,x,y,w,h,0,0);ph_add(PH_RECT,x,y,w,h,0,0);}
static void ph_bar_plan(int x,unsigned n,int base)
{
 int y=194,c=base+2,wait=2;
 for(unsigned z=0;z<=n;z++){ph_rect_plan(x,y-1,9,2,c);if(wait>0)--wait;else{++c;wait=1;}y-=2;}
}
static bool ph_sprite_plan(int x,int y,unsigned table,unsigned id,int hue,int value)
{
 Uint8 p[228*9],o[228*9];unsigned mw=table==TINY_FONT?6:228,mh=table==TINY_FONT?8:9;
 if(!hud_sprite_decode(table,id,mw,mh,p,o))return false;
 const Sprite *s=&sprite_table[table].sprite[id];
 if(x<0||y<0||x+s->width>320||y+s->height>200)return false;
 if(table==TINY_FONT)ph_add(PH_GLYPH_BEGIN,x,y,(int)id,hue,value,0);
 else ph_add(PH_SPRITE_BEGIN,x,y,(int)table,(int)id,0,0);
 for(unsigned yy=0;yy<s->height;yy++)for(unsigned xx=0;xx<s->width;xx++)if(o[yy*s->width+xx]){
  unsigned c=p[yy*s->width+xx];if(table==TINY_FONT)c=(unsigned)((hue<<4)|((c&15)+value));
  ph_add(PH_STORE,x+(int)xx,y+(int)yy,1,1,(Uint8)c,table==TINY_FONT?NWO_SPRITE1_HV_UNSAFE:NWO_SPRITE1);
  ph_add(PH_PIXEL,x+(int)xx,y+(int)yy,1,1,(Uint8)c,MIRROR_NORMAL);
 }
 ph_add(table==TINY_FONT?PH_GLYPH_END:PH_SPRITE_END,0,0,0,0,0,0);return !ph.bad;
}
static void ph_abort(void)
{
 if(ph.kind){++ph.status.rejected;for(unsigned i=0;i<64000;i++)if(ph.touched[i])ph_revoke_cell(i);}
 ph.kind=0;ph.fill=false;ph.bad=false;ph.n=ph.next=0;
}
static bool ph_begin(unsigned kind,SDL_Surface *s)
{
 if(!ph.live)return false;
 if(ph.kind){ph_abort();return false;}
 if(!ph_context()||ph.suspended||s!=ph.surface)return false;
 ph.kind=kind;ph.bad=false;ph.n=ph.next=0;memset(ph.touched,0,64000);++ph.status.transactions;return true;
}
static bool ph_end(unsigned kind,SDL_Surface *s)
{
 if(!ph.live||!ph.kind)return false;
 bool ok=ph.kind==kind&&s==ph.surface&&ph_context()&&!ph.bad&&!ph.fill&&ph.next==ph.n;
 if(ok)for(unsigned i=0;i<64000;i++)if(ph_exterior(i)&&ph.observed[i]!=((Uint8 *)ph.pixels)[i]){ok=false;break;}
 if(!ok){ph_abort();return false;}
 /* Only these known original non-text writes may restore identical PIC3 rims. */
 if(kind<=PH_MODE)for(unsigned i=0;i<64000;i++)if(ph.touched[i]&&ph.observed[i]==ph.pristine[i])ph.static_ok[i]=1;
 ph.kind=0;++ph.status.accepted;return true;
}
void render_mirror_persistent_store(SDL_Surface *s,const void *address,size_t n,unsigned writer)
{
 if(!ph.live||s!=ph.surface)return;
 uintptr_t p=(uintptr_t)address,b=(uintptr_t)ph.pixels;if(!address||p<b||p-b>=64000||n>64000-(p-b)){ph_reset();return;}
 size_t off=(size_t)(p-b);
 if(ph.fill){/* Optional old NWO fill rows are not duplicate physical writes. */
  SDL_Rect r=ph.fill_rect;if(writer!=NWO_SDL_VGA_FILL||r.w<=0||r.h<=0||n!=(size_t)r.w||ph.fill_rows>=(unsigned)r.h||off!=(size_t)(r.y+(int)ph.fill_rows)*320+(unsigned)r.x)ph.bad=true;
  else ++ph.fill_rows;
  return;
 }
 ++ph.status.stores;
 int c=n?((const Uint8 *)address)[0]:0;bool uniform=true;for(size_t i=1;i<n;i++)if(((const Uint8 *)address)[i]!=c)uniform=false;
 if(ph.kind){if(!uniform||n>320||off%320+n>320)ph.bad=true;ph_event(PH_STORE,(int)(off%320),(int)(off/320),(int)n,1,c,(int)writer);}
 ph_touch(off,n);
}
void render_mirror_persistent_unknown(SDL_Surface *s,const void *p,size_t n)
{
 if(!ph.live||s!=ph.surface)return;
 if(ph.kind)ph.bad=true;
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)ph.pixels;
 if(a<b||a-b>=64000||n>64000-(a-b)){ph_reset();return;}
 for(size_t i=a-b;i<a-b+n;i++)if(ph_exterior((unsigned)i))ph_revoke_cell((unsigned)i);
 ++ph.serial;
}
void render_mirror_persistent_fill_before(SDL_Surface *s,const SDL_Rect *r,Uint8 c)
{
 if(!ph.live||s!=ph.surface)return;
 if(!r||ph.fill||!ph_context()){ph_reset();return;}
 ph_event(PH_FILL_BEFORE,r->x,r->y,r->w,r->h,c,NWO_SDL_VGA_FILL);ph.fill=true;ph.fill_rect=*r;ph.fill_rows=0;ph.fill_color=c;
}
void render_mirror_persistent_fill_after(SDL_Surface *s,const SDL_Rect *r,int result)
{
 if(!ph.live||s!=ph.surface)return;
 if(!ph.fill||!r||(r->x!=ph.fill_rect.x||r->y!=ph.fill_rect.y||r->w!=ph.fill_rect.w||r->h!=ph.fill_rect.h)||!ph_context()){ph_reset();return;}
 ph.fill=false;ph_event(PH_FILL_AFTER,r->x,r->y,r->w,r->h,result,0);
 if(result){ph.bad=true;return;}
 if(ph.fill_rows&&ph.fill_rows!=(unsigned)(r->h>0?r->h:0))ph.bad=true;
 if(r->w<=0||r->h<=0)return;
 if(r->x<0||r->y<0||r->x+r->w>320||r->y+r->h>200){ph_reset();return;}
 for(int y=0;y<r->h;y++){
  for(int x=0;x<r->w;x++)if(((Uint8 *)ph.pixels)[(r->y+y)*320+r->x+x]!=ph.fill_color)ph.bad=true;
  ph_touch((size_t)(r->y+y)*320+(unsigned)r->x,(size_t)r->w);
 }
}
static void ph_pixel(SDL_Surface *s,Uint8 *address,int style)
{
 if(!ph.live||s!=ph.surface)return;
 uintptr_t a=(uintptr_t)address,b=(uintptr_t)ph.pixels;if(a<b||a-b>=64000){ph.bad=true;return;}
 if(!ph.kind){ph_touch((size_t)(a-b),1);return;}
 ++ph.status.callbacks;ph_event(PH_PIXEL,(int)((a-b)%320),(int)((a-b)/320),1,1,*address,style);
}
static void ph_rect(SDL_Surface *s,const SDL_Rect *r)
{
 if(!ph.live||s!=ph.surface)return;
 if(ph.kind){if(!r){ph.bad=true;return;}++ph.status.callbacks;ph_event(PH_RECT,r->x,r->y,r->w,r->h,0,0);return;}
 if(!ph_context()){ph_reset();return;}
 int x=r?r->x:0,y=r?r->y:0,w=r?r->w:320,h=r?r->h:200;
 if(w<=0||h<=0)return;
 int64_t right=(int64_t)x+w,bottom=(int64_t)y+h;
 for(int yy=MAX(0,y);yy<200&&yy<bottom;yy++)for(int xx=MAX(0,x);xx<320&&xx<right;xx++)ph_touch((size_t)yy*320+(unsigned)xx,1);
}
void render_mirror_persistent_sprite_begin(SDL_Surface *s,int x,int y,unsigned table,unsigned id)
{if(ph.live&&s==ph.surface){if(ph.kind&&!ph_options())ph.bad=true;ph_event(PH_SPRITE_BEGIN,x,y,(int)table,(int)id,0,0);}}
void render_mirror_persistent_sprite_end(void){ph_event(PH_SPRITE_END,0,0,0,0,0,0);}
static void ph_glyph_begin(SDL_Surface *s,int x,int y,unsigned table,unsigned id,bool black,unsigned hue,int value)
{if(ph.live&&ph.kind&&s==ph.surface){if(table!=TINY_FONT||black)ph.bad=true;ph_event(PH_GLYPH_BEGIN,x,y,(int)id,(int)hue,value,0);}}
static void ph_glyph_end(void){ph_event(PH_GLYPH_END,0,0,0,0,0,0);}
void render_mirror_persistent_wipe_begin(SDL_Surface *s,unsigned shield)
{if(ph.live&&s==ph.surface){ph.wipe_shield=shield;hud_components_shield_wiped();}}
static void ph_meter_begin(SDL_Surface *s,SDL_Surface *draw,unsigned kind,unsigned a,unsigned b)
{
 if(!ph.live)return;
 unsigned k=kind==HUD_WRITE_FRONT?PH_FRONT:kind==HUD_WRITE_REAR?PH_REAR:kind==HUD_WRITE_GENERATOR?PH_GENERATOR:kind==HUD_WRITE_ARMOR_WIPE?PH_WIPE:kind==HUD_WRITE_ARMOR_DRAW?PH_ARMOR:PH_NONE;
 if(!k||draw!=s||!ph_begin(k,s)){hud_meters_revoke(hud_meters_event_bits(kind));return;}
 ph.a=a;ph.b=b;hud_meters_write_begin(kind,a,b);
 if(k==PH_FRONT||k==PH_REAR){if(a>11){ph.bad=true;return;}int y=k==PH_FRONT?17:38;ph_fill_plan(289,y,22,3,0);for(unsigned j=1;j<=a;j++)ph_rect_plan(287+(int)j*2,y,2,3,115+(int)j);}
 if(k==PH_GENERATOR){if(a>90||b>90||a==b){ph.bad=true;return;}if(b>a)ph_fill_plan(269,102-(int)b,8,2+(int)b-(int)a,113+(int)b/7);else ph_fill_plan(269,102-(int)a,8,2+(int)a-(int)b,0);}
 if(k==PH_WIPE){if(a>28||ph.wipe_shield>28){ph.bad=true;return;}ph_fill_plan(270,137,9,58-(int)ph.wipe_shield*2,0);ph_fill_plan(307,137,9,58-(int)a*2,0);}
 if(k==PH_ARMOR){if(a>28){ph.bad=true;return;}ph_bar_plan(307,a,224);}
}
static void ph_meter_end(SDL_Surface *s,unsigned kind)
{
 unsigned k=kind==HUD_WRITE_FRONT?PH_FRONT:kind==HUD_WRITE_REAR?PH_REAR:kind==HUD_WRITE_GENERATOR?PH_GENERATOR:kind==HUD_WRITE_ARMOR_WIPE?PH_WIPE:kind==HUD_WRITE_ARMOR_DRAW?PH_ARMOR:PH_NONE;
 if(!ph.live)return;
 if(ph_end(k,s)){if(!hud_meters_write_end(kind,ph.pixels,320))hud_meters_revoke(hud_meters_event_bits(kind));}
 else hud_meters_revoke(hud_meters_event_bits(kind));
}
void render_mirror_persistent_shield_begin(SDL_Surface *s,unsigned shield,unsigned maximum)
{if(ph_begin(PH_SHIELD,s)){ph.a=shield;ph.b=maximum;hud_components_shield_wiped();if(shield>maximum||maximum>28){ph.bad=true;return;}ph_bar_plan(270,shield,144);if(shield!=maximum)ph_rect_plan(270,193-(int)maximum*2,9,1,68);}}
static void ph_shield_end(SDL_Surface *s,unsigned shield,unsigned maximum)
{if(!ph.live)return;if(ph.a!=shield||ph.b!=maximum)ph.bad=true;if(ph_end(PH_SHIELD,s))hud_components_shield_drawn((int)shield,(int)maximum);else hud_components_shield_wiped();}
void render_mirror_persistent_mode_begin(SDL_Surface *s,unsigned mode)
{
 if(!ph_begin(PH_MODE,s))return;
 ph.a=mode;ph.status.mode=0;hud_indicators_mode_wiped();Uint8 p[2][80],o[2][80];if((mode!=1&&mode!=2)||!ph_modes(p,o)){ph.bad=true;return;}
 if(!ph_sprite_plan(285,44,OPTION_SHAPES,mode==1?18:19,0,0)||!ph_sprite_plan(302,44,OPTION_SHAPES,mode==1?19:18,0,0))ph.bad=true;
}
static void ph_mode_end(SDL_Surface *s,unsigned mode)
{if(!ph.live)return;if(ph.a!=mode)ph.bad=true;if(ph_end(PH_MODE,s)){hud_indicators_mode_drawn((int)mode);ph.status.mode=mode;}else hud_indicators_mode_wiped();}
static bool ph_backdrop_plan(void)
{
 if(!ph_options())return false;
 Uint8 p[2052],o[2052];if(!hud_sprite_decode(OPTION_SHAPES,36,228,9,p,o))return false;
 const Sprite *s=&sprite_table[OPTION_SHAPES].sprite[36];if(s->width!=228||s->height!=9||gameplay_hud_fnv64(p,2052)!=UINT64_C(0x029ec9ec39f694b1))return false;
 for(unsigned i=0;i<2052;i++)if(o[i]!=255)return false;
 return ph_sprite_plan(16,189,OPTION_SHAPES,36,0,0);
}
static bool ph_text_plan(unsigned which,const char *text)
{
 PhText *t=&ph.text[which];SDL_Rect r=ph_text_rect[which];int x=r.x,bright=0;t->count=0;
 if(!text||!ph_fonts())return false;
 unsigned i=0,limit=which?255:10;
 for(;i<=limit&&text[i];i++){
  unsigned c=(unsigned char)text[i];if(c>=128)return false;if(c==' '){x+=6;continue;}if(c=='~'){bright=bright?0:4;continue;}
  int id=font_ascii[c];if(id<0)continue;if(id>=86||t->count>=100)return false;
  int w=hud_font_width((unsigned)id),h=hud_font_height((unsigned)id);if(!w||!h||x<r.x||x+w>r.x+r.w||h>r.h)return false;
  t->glyph[t->count++]=(PhGlyph){x,r.y,id,4+bright};
  if(!ph_sprite_plan(x,r.y,TINY_FONT,(unsigned)id,which?0:12,4+bright))return false;
  x+=w+1;
 }
 return i<=limit&&x<=r.x+r.w+1;
}
static void ph_text_begin(unsigned which,SDL_Surface *s,const char *text,bool erase)
{
 if(!ph.live)return;
 PhText *t=&ph.text[which];
 if(!ph_begin(which?PH_MESSAGE:PH_LEVEL,s)){t->valid=false;return;}
 t->valid=false;
 if(!ph_fonts()||(!erase&&(!t->blank||!ph_field_equal(which,t->pre))))ph.bad=true;
 if(erase&&!ph_backdrop_plan())ph.bad=true;
 if(which)ph_add(PH_BACKDROP,0,0,0,0,0,0);
 if(!ph_text_plan(which,text))ph.bad=true;
 t->blank=false;
}
static void ph_text_backdrop(void)
{if(ph.kind==PH_MESSAGE){ph_event(PH_BACKDROP,0,0,0,0,0,0);if(ph_context()&&!ph.bad)ph_copy_field(1,ph.text[1].pre);}}
static void ph_text_end(unsigned which)
{
 if(!ph.live)return;
 PhText *t=&ph.text[which];
 if(ph_end(which?PH_MESSAGE:PH_LEVEL,VGAScreenSeg)){ph_copy_field(which,t->post);t->valid=true;}
 else t->valid=false;
}
static void ph_erase_begin(void)
{if(!ph.live)return;ph.text[1].valid=ph.text[1].blank=false;if(ph_begin(PH_ERASE,VGAScreenSeg)&&!ph_backdrop_plan())ph.bad=true;}
static void ph_erase_end(bool help)
{
 if(!ph.live)return;
 if(ph_end(PH_ERASE,VGAScreenSeg)){ph_copy_field(1,ph.text[1].pre);ph.text[1].blank=!help;}
}
static bool ph_static_rect(int x,int y,int w,int h)
{for(int yy=y;yy<y+h;yy++)for(int xx=x;xx<x+w;xx++)if(!ph.static_ok[yy*320+xx])return false;return true;}
static void ph_scan(void)
{
 if(!ph_context()){ph_reset();return;}
 if(ph.kind)ph_abort();
 for(unsigned i=0;i<64000;i++)if(ph_exterior(i)&&ph.observed[i]!=((Uint8 *)ph.pixels)[i]){ph_revoke_cell(i);ph.observed[i]=((Uint8 *)ph.pixels)[i];++ph.serial;}
}
static void ph_frame_begin(void)
{if(ph.live){ph_scan();ph.suspended=false;ph.composed=false;ph.status.composed=false;memset(ph.owned,0,64000);}}
static void ph_suspend(void){if(ph.live){ph_abort();ph.suspended=true;++ph.serial;}}
static Uint32 ph_blend(Uint32 lower,Uint32 color,unsigned alpha)
{Uint32 out=0xff000000u;for(int s=0;s<24;s+=8)out|=((((color>>s)&255)*alpha+((lower>>s)&255)*(255-alpha)+127)/255)<<s;return out;}
static void ph_store_rgba(int x,int y,const Uint8 *p,int sx,int sy,unsigned writer)
{
 Uint32 *to=(Uint32 *)((Uint8 *)output->pixels+(y*8+sy)*output->pitch)+x*8+sx;
 *to=0xff000000u|((Uint32)p[0]<<16)|((Uint32)p[1]<<8)|p[2];
 OHS_SURVIVAL_WRITE(output,to,writer);
}
/* Non-inlined entry is the read-only pre-HUD capture boundary for the external
 * harness: output still contains the unchanged native upscale + world copy. */
#if defined(__GNUC__)
__attribute__((noinline))
#endif
void render_mirror_persistent_hud_compose(void)
{
 ph.composed=false;ph.restore_pending=false;ph.status.composed=false;memset(ph.owned,0,64000);memset(ph.status.layer_cells,0,sizeof ph.status.layer_cells);
 if(!ph.live||ph.suspended)return;
 ph_scan();
 if(!ph.live||!output||output->w!=2560||output->h!=1600||output->pitch!=10240)return;
 bool palette=hud_components_palette_matches(rgb_palette),font=palette&&ph_fonts();Uint8 mi[2][80],mo[2][80];bool modes=palette&&ph_modes(mi,mo);
 bool shield=palette&&hud_components_shield_matches(ph.pixels,320);unsigned meters=palette?hud_meters_prepare(ph.pixels,320):0;
 ph.status.meters=meters;
 bool top=modes&&ph_static_rect(269,4,7,3)&&hud_indicators_top_matches(ph.pixels,320);
 bool mode=modes&&hud_indicators_mode_matches(ph.pixels,320);
 bool labels[4]={ph_static_rect(285,5,24,5),ph_static_rect(285,11,14,5),ph_static_rect(285,26,18,5),ph_static_rect(285,32,14,5)};
 bool fixed[3]={true,true,true};for(unsigned i=0;i<370;i++){int x,y;hud_fixed_text_position(i,&x,&y);if(!ph.static_ok[y*320+x])fixed[i<95?0:i<245?1:2]=false;}
 for(unsigned g=0;g<3;g++)fixed[g]=fixed[g]&&palette&&hud_fixed_text_group_matches(g,ph.pixels,320);
 gameplay_hud_prepare_corner(ph.pixels,320);
 uint64_t hp=UINT64_C(14695981039346656037);for(unsigned i=0;i<256;i++)if(i<=30||i==108||(i>=160&&i<=175))for(int s=16;s>=0;s-=8)hp=(hp^((rgb_palette[i]>>s)&255))*UINT64_C(1099511628211);
 bool frame=hp==UINT64_C(0xb2f37eb3eccb6866);
 for(int y=0;y<200;y++)for(int x=0;x<320;x++){
  unsigned n=(unsigned)(y*320+x);if(!ph_exterior(n))continue;Uint8 index=((Uint8 *)ph.pixels)[n];
  bool f=frame&&ph.static_ok[n]&&(!(x>=248&&x<269&&y>=184)||ph.corner);
  int label=y>=5&&y<10?0:y>=11&&y<16?1:y>=26&&y<31?2:y>=32&&y<37?3:-1;
  int fi=hud_fixed_text_cell(x,y);unsigned bits=0;
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
   const Uint8 *p=f?gameplay_hud_sample(x,y,sx,sy,8,index):NULL;
   if(p){ph_store_rgba(x,y,p,sx,sy,93);bits|=1;}
   p=palette&&label>=0&&labels[label]?hud_components_label_sample(x,y,sx,sy,8,index):NULL;
   if(!p&&shield)p=hud_components_shield_sample(x,y,sx,sy,8,index);
   if(p){ph_store_rgba(x,y,p,sx,sy,91);bits|=2;}
   p=meters?hud_meters_sample(x,y,sx,sy,8,index):NULL;if(p){ph_store_rgba(x,y,p,sx,sy,90);bits|=4;}
   p=((y>=4&&y<7&&top)||(y>=44&&y<52&&mode))?hud_indicators_sample(x,y,sx,sy,8,index):NULL;
   if(p){ph_store_rgba(x,y,p,sx,sy,89);bits|=8;}
   p=fi>=0&&fixed[fi<95?0:fi<245?1:2]?hud_fixed_text_sample((unsigned)fi,sx,sy,8):NULL;
   if(p){ph_store_rgba(x,y,p,sx,sy,87);bits|=16;}
  }
  ph.owned[n]=(Uint8)bits;for(unsigned k=0;k<5;k++)if(bits&(1u<<k))++ph.status.layer_cells[k];
 }
 ph.status.text_valid=0;
 for(unsigned k=0;k<2;k++)if(font&&ph.text[k].valid&&ph_field_equal(k,ph.text[k].post)){
  PhText *t=&ph.text[k];SDL_Rect r=ph_text_rect[k];ph.status.text_valid|=1u<<k;
  for(unsigned g=0;g<t->count;g++){
   PhGlyph q=t->glyph[g];unsigned w=(unsigned)hud_font_width((unsigned)q.id),h=(unsigned)hud_font_height((unsigned)q.id);Uint8 opaque[48];
   if(!hud_sprite_decode(TINY_FONT,(unsigned)q.id,6,8,NULL,opaque))continue;
   Uint32 color=palette_rgb((Uint8)((k?0:192)|(7+q.value)));
   for(unsigned yy=0;yy<h;yy++)for(unsigned xx=0;xx<w;xx++){
    bool owns=opaque[yy*w+xx]!=0;
    for(int sy=0;sy<8&&!owns;sy++)for(int sx=0;sx<8;sx++)if(hud_font_alpha((unsigned)q.id,(int)xx*8+sx,(int)yy*8+sy,8))owns=true;
    if(!owns)continue;
    int x=q.x+(int)xx,y=q.y+(int)yy;unsigned n=(unsigned)(y*320+x);if(!ph_exterior(n))continue;
    if(!(ph.owned[n]&32))++ph.status.layer_cells[5];
    ph.owned[n]|=32;
    Uint32 lower=palette_rgb(t->pre[(y-r.y)*r.w+x-r.x]);
    for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
     unsigned alpha=hud_font_alpha((unsigned)q.id,(int)xx*8+sx,(int)yy*8+sy,8);
     Uint32 *to=(Uint32 *)((Uint8 *)output->pixels+(y*8+sy)*output->pitch)+x*8+sx;
     *to=lower;OHS_SURVIVAL_WRITE(output,to,97);
     if(alpha){*to=ph_blend(*to,color,alpha);OHS_SURVIVAL_WRITE(output,to,98);}
    }
   }
  }
 }
 memcpy(ph.snapshot,ph.pixels,64000);memcpy(ph.palette,rgb_palette,sizeof ph.palette);ph.composed_serial=ph.serial;ph.composed=true;ph.status.composed=true;++ph.status.composes;
}
static void ph_present(void)
{
 if(!ph.composed&&!ph.restore_pending)return;
 bool ok=!ph.restore_pending&&ph_context()&&!ph.suspended&&!ph.kind&&ph.serial==ph.composed_serial&&!memcmp(ph.palette,rgb_palette,sizeof ph.palette);
 if(ok)for(unsigned i=0;i<64000;i++)if(ph_exterior(i)&&ph.snapshot[i]!=((Uint8 *)ph.pixels)[i]){ok=false;break;}
 if(ok&&ph.status.text_valid&&!ph_fonts())ok=false;
 Uint8 p[2][80],o[2][80];if(ok&&ph.status.layer_cells[3]&&!ph_modes(p,o))ok=false;
 if(ok)return;
 /* Never fault or promote the existing world frame. If its normal geometry
  * guard accepts the current output, native exterior is always authoritative. */
 SDL_Surface *s=VGAScreenSeg;
 if(s&&s->pixels&&s->pitch==320&&s->w==320&&s->h==200&&s->format&&s->format->format==SDL_PIXELFORMAT_INDEX8&&output&&output->pixels&&output->format&&output->format->format==SDL_PIXELFORMAT_ARGB8888&&output->w==2560&&output->h==1600&&output->pitch==10240&&!output->locked&&!SDL_MUSTLOCK(output))
 for(unsigned i=0;i<64000;i++)if(ph_exterior(i))for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
  Uint32 *to=(Uint32 *)((Uint8 *)output->pixels+((int)(i/320)*8+sy)*output->pitch)+(i%320)*8+(unsigned)sx;
  *to=palette_rgb(((Uint8 *)s->pixels)[i]);OHS_SURVIVAL_WRITE(output,to,92);
 }
 memset(ph.owned,0,64000);ph.composed=false;ph.restore_pending=false;ph.status.composed=false;++ph.status.restores;
}
PersistentHudStatus render_mirror_persistent_hud_status(void)
{PersistentHudStatus s=ph.status;s.requested=ph_requested();s.active_kind=ph.kind;s.expected_ops=ph.n;s.observed_ops=ph.next;return s;}
bool render_mirror_persistent_hud_owners(uint8_t *out,size_t n)
{if(!out||n!=64000||!ph.composed)return false;memcpy(out,ph.owned,n);return true;}

void render_mirror_persistent_source_reset(unsigned table)
{if(table==TINY_FONT||table==OPTION_SHAPES)ph_reset();}
