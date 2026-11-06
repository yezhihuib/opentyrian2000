#include "b313_family_writer.h"
#include "b313_terrain_context.h"
#if B313_FAMILY_CANVAS_DIAGNOSTIC
#include <limits.h>
#include <string.h>

enum { FW_WIDTH=320,FW_HEIGHT=200,FW_BYTES=320*200,FW_COPY_ROWS=184,FW_COPY_BYTES=264 };
typedef struct {
 SDL_Surface *surface;
 void *pixels;
 SDL_PixelFormat *format;
 SDL_Rect clip;
 Uint32 flags;
 int locked;
} FwSurface;
typedef struct {
 uint64_t token,frame;
 unsigned slot,old_rows,consumed;
 enum NwoWriter writer;
 bool has_rect;
 SDL_Rect requested,effective;
} FwFill;
static B313FamilyWriterStatus fw;
static FwSurface bound[2];
static FwFill fill;
static struct {bool present;unsigned slot;size_t offset,bytes;enum NwoWriter writer;} span;
/* Ordinary stores are one pending physical span. A bit clears exactly once.
 * Fill pixels use the separately validated rectangle and strict row order. */
static unsigned char pending[FW_BYTES/8];
static uint64_t token_serial;

static bool fail(unsigned reason)
{
 if(fw.active){
  if(!fw.reasons)fw.first_reason=reason;
  fw.reasons|=reason;fw.valid=false;
 }
 return false;
}
static bool rect_equal(const SDL_Rect *a,const SDL_Rect *b)
{return a->x==b->x&&a->y==b->y&&a->w==b->w&&a->h==b->h;}
static bool endpoint(int origin,int extent)
{int64_t end=(int64_t)origin+extent;return end>=INT_MIN&&end<=INT_MAX;}
static bool surface_shape(SDL_Surface *s)
{
 if(!s||!s->pixels||!s->format||s->w!=FW_WIDTH||s->h!=FW_HEIGHT||s->pitch!=FW_WIDTH||
    s->format->format!=SDL_PIXELFORMAT_INDEX8||s->format->BitsPerPixel!=8||s->format->BytesPerPixel!=1||
    s->locked||SDL_MUSTLOCK(s)||(uintptr_t)s->pixels>UINTPTR_MAX-FW_BYTES)return false;
 const SDL_Rect *c=&s->clip_rect;
 return c->x>=0&&c->y>=0&&c->w>=0&&c->h>=0&&
        (int64_t)c->x+c->w<=FW_WIDTH&&(int64_t)c->y+c->h<=FW_HEIGHT;
}
static bool context(void)
{
 for(unsigned i=0;i<2;i++){
  const FwSurface *b=&bound[i];SDL_Surface *s=b->surface;
  if(!surface_shape(s)||s->pixels!=b->pixels||s->format!=b->format||
     s->flags!=b->flags||s->locked!=b->locked||!rect_equal(&s->clip_rect,&b->clip))
   return fail(B313FW_CONTEXT|B313FW_SURFACE);
 }
 return true;
}
static bool open_frame(void)
{
 if(!fw.active)return false;
 if(fw.sealed)return fail(B313FW_AFTER_SEAL);
 return fw.valid&&context();
}
static bool idle(void)
{
 if(fw.fill_pending||fw.rect_pending||fw.rect_active||fw.pending_pixels)
  return fail(B313FW_PENDING);
 return true;
}
static int locate(SDL_Surface *s,const void *address,size_t bytes,size_t *offset)
{
 unsigned slot;
 if(s==bound[0].surface)slot=0;
 else if(s==bound[1].surface)slot=1;
 else {fail(B313FW_SURFACE);return -1;}
 uintptr_t a=(uintptr_t)address,b=(uintptr_t)bound[slot].pixels;
 if(!address||!bytes||a<b||a-b>=FW_BYTES||bytes>FW_BYTES-(size_t)(a-b)){
  fail(B313FW_RANGE);return -1;
 }
 *offset=(size_t)(a-b);return (int)slot;
}
static bool sdl_writer(enum NwoWriter w)
{return w==NWO_SDL_BACKGROUND_CLEAR||w==NWO_SDL_VGA_FILL||w==NWO_SDL_VIDEO_CLEAR;}
static bool effective_rect(const SDL_Rect *requested,const SDL_Rect *clip,SDL_Rect *out)
{
 SDL_Rect r=requested?*requested:*clip;
 if(!endpoint(r.x,r.w)||!endpoint(r.y,r.h))return fail(B313FW_RANGE|B313FW_FILL);
 *out=(SDL_Rect){0,0,0,0};
 if(r.w<=0||r.h<=0||clip->w<=0||clip->h<=0)return true;
 int64_t left=r.x>clip->x?r.x:clip->x,top=r.y>clip->y?r.y:clip->y;
 int64_t right=(int64_t)r.x+r.w,bottom=(int64_t)r.y+r.h;
 if(right>(int64_t)clip->x+clip->w)right=(int64_t)clip->x+clip->w;
 if(bottom>(int64_t)clip->y+clip->h)bottom=(int64_t)clip->y+clip->h;
 if(right>left&&bottom>top)*out=(SDL_Rect){(int)left,(int)top,(int)(right-left),(int)(bottom-top)};
 return true;
}
static bool increment(uint64_t *counter)
{if(*counter==UINT64_MAX)return fail(B313FW_OVERFLOW);++*counter;return true;}

void b313_family_writer_reset(void)
{
 memset(&fw,0,sizeof(fw));memset(bound,0,sizeof(bound));
 memset(&fill,0,sizeof(fill));memset(&span,0,sizeof(span));memset(pending,0,sizeof(pending));
}
bool b313_family_writer_begin(uint64_t frame,SDL_Surface *game,SDL_Surface *output)
{
 const uint64_t previous=fw.frame;
 const bool unfinished=fw.active&&(fw.fill_pending||fw.rect_pending||fw.rect_active||fw.pending_pixels||(!fw.sealed&&fw.valid));
 b313_family_writer_reset();
 fw.diagnostic_enabled=true;fw.active=true;fw.valid=true;fw.frame=frame;
 if(!frame||frame<=previous||unfinished)return fail(B313FW_FRAME|B313FW_PENDING);
 if(game==output||!surface_shape(game)||!surface_shape(output))return fail(B313FW_SURFACE);
 uintptr_t a=(uintptr_t)game->pixels,b=(uintptr_t)output->pixels;
 if(a<b+FW_BYTES&&b<a+FW_BYTES)return fail(B313FW_SURFACE|B313FW_RANGE);
 SDL_Surface *s[2]={game,output};
 for(unsigned i=0;i<2;i++)bound[i]=(FwSurface){s[i],s[i]->pixels,s[i]->format,s[i]->clip_rect,s[i]->flags,s[i]->locked};
 return true;
}
void b313_family_writer_store(SDL_Surface *s,const void *address,size_t bytes,enum NwoWriter writer)
{
 if(!open_frame())return;
 if(writer<=0||writer>=NWO_WRITER_LIMIT){fail(B313FW_WRITER);return;}
 size_t off=0;int slot=locate(s,address,bytes,&off);if(slot<0)return;
 if(fw.fill_pending){
  /* Old NWO may emit these rows after the original SDL call. They are the
   * same fill, not additional writes. Zero rows is valid when NWO is off. */
  const SDL_Rect *e=&fill.effective;
  if((unsigned)slot!=fill.slot||writer!=fill.writer||fill.old_rows>=(unsigned)e->h||
     bytes!=(size_t)e->w||off!=(size_t)(e->y+(int)fill.old_rows)*FW_WIDTH+(size_t)e->x){
   fail(B313FW_FILL|B313FW_PENDING);return;
  }
  ++fill.old_rows;increment(&fw.fill_rows_suppressed);return;
 }
 if(sdl_writer(writer)){fail(B313FW_FILL|B313FW_TOKEN);return;}
 if(fw.crop_started){fail(B313FW_COPY);return;}
 if(!idle())return;
 if(bytes>UINT64_MAX-fw.store_bytes||!increment(&fw.stores)){fail(B313FW_OVERFLOW);return;}
 fw.store_bytes+=bytes;
 /* Output native base needs no game-canvas pixel pairing. RECT_SPAN is kept
  * only to validate the matching ordinary render_mirror_rect callback. */
 if(slot==1&&writer!=NWO_RECT_SPAN)return;
 span.present=true;span.slot=(unsigned)slot;span.offset=off;span.bytes=bytes;span.writer=writer;
 for(size_t i=off;i<off+bytes;i++)pending[i/8]|=(unsigned char)(1u<<(i%8));
 fw.pending_pixels=(unsigned)bytes;
}
void b313_family_writer_copy(SDL_Surface *dst,const void *to,SDL_Surface *src,const void *from,size_t bytes)
{
 if(!open_frame()||!idle())return;
 size_t d=0,s=0;
 int ds=locate(dst,to,bytes,&d),ss=locate(src,from,bytes,&s);
 if(ds<0||ss<0)return;
 unsigned row=fw.copy_rows;
 if(ds!=1||ss!=0||row>=FW_COPY_ROWS||bytes!=FW_COPY_BYTES||
    s!=(size_t)row*FW_WIDTH+24||d!=(size_t)row*FW_WIDTH){fail(B313FW_COPY);return;}
 fw.crop_started=true;++fw.copy_rows;
}
void b313_family_writer_gap(unsigned reason)
{(void)reason;if(fw.active)fail(B313FW_GAP|(fw.sealed?B313FW_AFTER_SEAL:0u));}
void b313_family_writer_unknown(SDL_Surface *s,const void *p,size_t n,unsigned reason)
{(void)s;(void)p;(void)n;(void)reason;if(fw.active)fail(B313FW_UNKNOWN|(fw.sealed?B313FW_AFTER_SEAL:0u));}

uint64_t b313_family_writer_fill_before(SDL_Surface *s,const SDL_Rect *rect,enum NwoWriter writer)
{
 if(!open_frame())return 0;
 if(!idle())return 0;
 if(fw.crop_started){fail(B313FW_COPY);return 0;}
 if(!sdl_writer(writer)){fail(B313FW_WRITER|B313FW_FILL);return 0;}
 unsigned slot;
 if(s==bound[0].surface)slot=0;
 else if(s==bound[1].surface)slot=1;
 else {fail(B313FW_SURFACE);return 0;}
 SDL_Rect effective;
 if(!effective_rect(rect,&bound[slot].clip,&effective))return 0;
 if(token_serial==UINT64_MAX||!increment(&fw.fills)){fail(B313FW_OVERFLOW);return 0;}
 memset(&fill,0,sizeof(fill));fill.token=++token_serial;fill.frame=fw.frame;
 fill.slot=slot;fill.writer=writer;fill.has_rect=rect!=NULL;
 if(rect)fill.requested=*rect;
 fill.effective=effective;fw.fill_pending=true;
 return fill.token;
}
void b313_family_writer_fill_after(uint64_t token,int original_result)
{
 if(!open_frame())return;
 if(!fw.fill_pending||!token||token!=fill.token||fill.frame!=fw.frame){fail(B313FW_TOKEN|B313FW_FILL);return;}
 if(original_result!=0){fail(B313FW_FILL);return;}
 if(fill.old_rows&&fill.old_rows!=(unsigned)fill.effective.h){fail(B313FW_FILL|B313FW_PENDING);return;}
 fw.fill_pending=false;fw.rect_pending=true;
}
bool b313_family_writer_rect_begin(SDL_Surface *s,const SDL_Rect *rect)
{
 if(!open_frame())return false;
 if(fw.fill_pending||fw.rect_active||fw.crop_started)
  return fail(B313FW_FILL|B313FW_PENDING);
 if(!fw.rect_pending){
  /* JE_rectangle uses an ordinary one-row memset, not SDL_FillRect. It must
   * name exactly the still-unconsumed registered RECT_SPAN, including clip. */
  if(!span.present||span.writer!=NWO_RECT_SPAN||s!=bound[span.slot].surface||
     fw.pending_pixels!=span.bytes)return fail(B313FW_PENDING|B313FW_FILL);
  SDL_Rect e;
  if(!effective_rect(rect,&bound[span.slot].clip,&e))return false;
  if(e.h!=1||e.w<=0||(size_t)e.w!=span.bytes||
     (size_t)e.y*FW_WIDTH+(unsigned)e.x!=span.offset)return fail(B313FW_RANGE|B313FW_FILL);
  memset(&fill,0,sizeof(fill));fill.slot=span.slot;fill.frame=fw.frame;fill.effective=e;
  for(size_t i=span.offset;i<span.offset+span.bytes;i++)pending[i/8]&=(unsigned char)~(1u<<(i%8));
  memset(&span,0,sizeof(span));fw.rect_active=true;return true;
 }
 if(fw.pending_pixels||span.present)return fail(B313FW_FILL|B313FW_PENDING);
 if(s!=bound[fill.slot].surface||fill.frame!=fw.frame||fill.has_rect!=(rect!=NULL)||
    (rect&&!rect_equal(rect,&fill.requested)))return fail(B313FW_FILL|B313FW_CONTEXT);
 SDL_Rect e;
 if(!effective_rect(rect,&bound[fill.slot].clip,&e)||!rect_equal(&e,&fill.effective))return fail(B313FW_FILL|B313FW_CONTEXT);
 fw.rect_pending=false;fw.rect_active=true;fill.consumed=0;
 fw.pending_pixels=(unsigned)e.w*(unsigned)e.h;
 return true;
}
bool b313_family_writer_pixel(SDL_Surface *s,const void *address)
{
 if(!open_frame())return false;
 if(fw.fill_pending||fw.rect_pending)return fail(B313FW_PENDING|B313FW_FILL);
 if(fw.crop_started)return fail(B313FW_COPY);
 size_t off=0;int slot=locate(s,address,1,&off);if(slot<0)return false;
 if(fw.rect_active){
  const SDL_Rect *e=&fill.effective;
  if(!fw.pending_pixels||e->w<=0||(unsigned)slot!=fill.slot)return fail(B313FW_DUPLICATE|B313FW_FILL);
  size_t wanted=(size_t)(e->y+(int)(fill.consumed/(unsigned)e->w))*FW_WIDTH+
                (unsigned)e->x+fill.consumed%(unsigned)e->w;
  if(off!=wanted)return fail(B313FW_RANGE|B313FW_FILL);
  ++fill.consumed;--fw.pending_pixels;
 }else{
  if(slot==1&&!span.present)return idle();
  unsigned char mask=(unsigned char)(1u<<(off%8));
  if(!span.present||(unsigned)slot!=span.slot||!fw.pending_pixels||!(pending[off/8]&mask))
   return fail(B313FW_DUPLICATE|B313FW_PENDING);
  pending[off/8]&=(unsigned char)~mask;--fw.pending_pixels;
  if(!fw.pending_pixels)memset(&span,0,sizeof(span));
 }
 return increment(&fw.pixels);
}
bool b313_family_writer_rect_end(SDL_Surface *s)
{
 if(!open_frame())return false;
 if(!fw.rect_active||fw.fill_pending||fw.rect_pending||fw.pending_pixels||s!=bound[fill.slot].surface||
    fill.consumed!=(unsigned)fill.effective.w*(unsigned)fill.effective.h)
  return fail(B313FW_PENDING|B313FW_FILL);
 fw.rect_active=false;memset(&fill,0,sizeof(fill));return true;
}
bool b313_family_writer_draw_ready(uint64_t frame)
{
 if(!open_frame())return false;
 if(!frame||frame!=fw.frame)return fail(B313FW_FRAME);
 if(fw.crop_started)return fail(B313FW_COPY);
 return idle();
}
bool b313_family_writer_seal(uint64_t frame)
{
 if(!open_frame())return false;
 if(!frame||frame!=fw.frame)return fail(B313FW_FRAME);
 if(!idle())return false;
 if(!fw.crop_started||fw.copy_rows!=FW_COPY_ROWS)return fail(B313FW_COPY);
 fw.sealed=true;return true;
}
bool b313_family_writer_current(uint64_t frame)
{
 if(!fw.active||!fw.valid)return false;
 if(!frame||frame!=fw.frame)return fail(B313FW_FRAME);
 return context()&&idle()&&fw.sealed&&fw.crop_started&&fw.copy_rows==FW_COPY_ROWS;
}
B313FamilyWriterStatus b313_family_writer_status(void){return fw;}
/* Pure receipt guard. Keep every existing writer function unchanged. */
bool b313_family_writer_peek_current(uint64_t frame)
{
 if(!fw.active||!fw.valid||!frame||frame!=fw.frame||fw.fill_pending||fw.rect_pending||
    fw.rect_active||fw.pending_pixels||!fw.sealed||!fw.crop_started||fw.copy_rows!=FW_COPY_ROWS)return false;
 for(unsigned i=0;i<2;i++){
  const FwSurface *b=&bound[i];SDL_Surface *s=b->surface;
  if(!surface_shape(s)||s->pixels!=b->pixels||s->format!=b->format||
     s->flags!=b->flags||s->locked!=b->locked||!rect_equal(&s->clip_rect,&b->clip))return false;
 }
 return true;
}
#else
bool b313_family_writer_peek_current(uint64_t frame){(void)frame;return false;}
#endif
