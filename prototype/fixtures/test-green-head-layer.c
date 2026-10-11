/* Isolated harness: production functions are extracted by the Python runner.
 * The oracle defers head samples and flushes them at unrelated writes, rather
 * than implementing production's saved-underlay/restart-index algorithm. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef uint8_t Uint8;
typedef uint16_t Uint16;
typedef uint32_t Uint32;
typedef struct { int x,y,w,h; } SDL_Rect;
typedef struct { int w,h,pitch; void *pixels; } SDL_Surface;
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
enum { MIRROR_NORMAL, MIRROR_BLEND, MIRROR_SHADOW };
enum { ASSET_NEWSH2=101, ASSET_EXPLOSION=106, ASSET_SHAPESZ=201 };
#include "production-types.inc"

static SDL_Surface *canvas,*game_screen;
static int game_probe_density;
static bool game_probe_original_reference,game_probe_local_blend,game_probe_known_blend;
static bool active=true,suppress,suppress_green_smoke;
static const char *reject_reason;
static Uint32 rgb_palette[256];
static Uint8 expected[320*200],selected[320*200];
static Uint8 *hd_owner,*green_under_owner,*cloud_owner;
static bool suppress_cloud;
static Uint16 *green_first;
static Uint32 *green_under;
static GreenHead green_heads[256];
static unsigned int green_head_count,region_count,local_entities,draws,occlusions,brightness_blocks;
static HdRegion regions[256];
static unsigned int local_regions,local_blocks,expanded_regions,boundary_crossings,blend_source_index;
static Uint8 restored_mask[320*200];

static void render_mirror_unsupported(const char *reason)
{ fprintf(stderr,"Unexpected unsupported renderer path: %s\n",reason); exit(1); }
static void game_probe_restore_region(unsigned int source,SDL_Rect requested,SDL_Rect restored,unsigned int groups,unsigned int blocks)
{ (void)source;(void)requested;(void)restored;(void)groups;(void)blocks; }
#include "production-helpers.inc"

enum { WIDTH=20, HEIGHT=18, MAX_EVENTS=100 };
enum { HEAD, SMOKE, OTHER, INDEXED, BRIGHTNESS, RESTORE, STAMP_SMOKE, STAMP_OTHER };
typedef struct {
 int kind,x,y,style,value;
 Asset *asset;
 unsigned int head_id;
} Event;
static Event events[MAX_EVENTS];
static unsigned int event_count;
static Uint32 *initial;
static Uint8 initial_owner;
static unsigned long pixels_checked,overlap_checks,restart_checks,transparent_checks;

/* Independent byte-channel operator, with explicit integer round-to-nearest. */
static Uint32 reference_alpha(Uint32 destination,const Uint8 source[4])
{
 unsigned int channels[3];
 for(int channel=0;channel<3;channel++) {
  unsigned int previous=(destination/(1u<<((2-channel)*8)))%256u;
  unsigned int numerator=previous*(255u-source[3])+source[channel]*source[3];
  channels[channel]=numerator/255u+(numerator%255u>=128u);
 }
 return 0xff000000u+channels[0]*65536u+channels[1]*256u+channels[2];
}
static Uint32 reference_brightness(Uint32 color,int value)
{
 unsigned int r=(color>>16)&255,g=(color>>8)&255,b=color&255;
 unsigned int peak=r>g?r:g;if(b>peak)peak=b;
 int next=(int)peak+value*17;if(next<0)next=0;if(next>255)next=255;
 unsigned int channels[]={r,g,b};Uint32 result=0xff000000u;
 for(int i=0;i<3;i++) {
  unsigned int numerator=channels[i]*(unsigned int)next;
  unsigned int v=peak?(numerator+peak/2)/peak:(unsigned int)next;
  result+=v*(1u<<((2-i)*8));
 }
 return result;
}
static Uint32 reference_smoke(Uint32 color,const Uint8 source[4],int style)
{
 if(style==MIRROR_NORMAL)return reference_alpha(color,source);
 unsigned int high=source[0];
 if(source[1]>high)high=source[1];
 if(source[2]>high)high=source[2];
 unsigned int low=(color>>16)&255;
 if(((color>>8)&255)>low)low=(color>>8)&255;
 if((color&255)>low)low=color&255;
 unsigned int value=(high+low+1)/2;
 Uint8 adjusted[4];
 for(int i=0;i<3;i++)adjusted[i]=high?(source[i]*value+high/2)/high:0;
 adjusted[3]=source[3];return reference_alpha(color,adjusted);
}
/* Locate samples using global half-open rectangles, separately from production's
 * local coordinate checks; authored density deliberately differs from output. */
static const Uint8 *reference_sample(const Event *event,int px,int py)
{
 int d=game_probe_density;
 int left=event->x*d,top=event->y*d;
 if(px<left||py<top||px>=(event->x+event->asset->w)*d||py>=(event->y+event->asset->h)*d)return NULL;
 size_t sx=(size_t)(px-left)*(size_t)event->asset->density/(size_t)d;
 size_t sy=(size_t)(py-top)*(size_t)event->asset->density/(size_t)d;
 return &event->asset->rgba[4*(sy*(size_t)event->asset->w*(size_t)event->asset->density+sx)];
}
static Uint32 flush_heads(Uint32 color,const Uint8 **pending,unsigned int count)
{ for(unsigned int i=0;i<count;i++)color=reference_alpha(color,pending[i]);return color; }

static void check_scene(const char *label)
{
 int d=game_probe_density;
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++) {
  size_t n=(size_t)y*canvas->w+x;
  Uint32 base=initial[n];Uint8 owner=initial_owner;
  const Uint8 *pending[MAX_EVENTS];unsigned int pending_count=0,first=0;
  for(unsigned int k=0;k<event_count;k++) {
   const Event *event=&events[k];
   if(event->kind==RESTORE) {
    base=0xff000000u;owner=0;pending_count=0;first=0;continue;
   }
   if(event->kind==STAMP_SMOKE||event->kind==STAMP_OTHER) {
    if(x/d==event->x&&y/d==event->y&&(!pending_count||event->kind==STAMP_SMOKE))owner=1;
    continue;
   }
   if(event->kind==INDEXED||event->kind==BRIGHTNESS) {
    if(x/d!=event->x||y/d!=event->y)continue;
    base=flush_heads(base,pending,pending_count);if(pending_count)owner=1;pending_count=0;first=0;
    if(event->kind==INDEXED){base=0xff000000u|rgb_palette[event->value];owner=0;}
    else if(owner)base=reference_brightness(base,event->value);
    continue;
   }
   const Uint8 *sample=reference_sample(event,x,y);
   if(!sample)continue;
   if(!sample[3]){if(pending_count)++transparent_checks;continue;}
   if(event->kind==HEAD) {
    if(!pending_count)first=event->head_id;
    pending[pending_count++]=sample;
   } else if(event->kind==SMOKE) {
    base=reference_smoke(base,sample,event->style);owner=1;
   } else {
    base=flush_heads(base,pending,pending_count);pending_count=0;first=0;
    base=reference_alpha(base,sample);owner=1;
   }
  }
  Uint32 want=flush_heads(base,pending,pending_count);
  Uint32 got=*(Uint32 *)((Uint8 *)canvas->pixels+(size_t)y*canvas->pitch+x*4);
  Uint8 wanted_owner=pending_count?1:owner;
  if(got!=want||green_first[n]!=first||hd_owner[n]!=wanted_owner||
     (first&&(green_under[n]!=base||green_under_owner[n]!=owner))) {
   fprintf(stderr,"%s: d=%d x=%d y=%d events=%u color=%08x/%08x first=%u/%u owner=%u/%u under=%08x/%08x under-owner=%u/%u\n",
    label,d,x,y,event_count,got,want,green_first[n],first,hd_owner[n],wanted_owner,green_under[n],base,green_under_owner[n],owner);exit(1);
  }
  if(pending_count>1)++overlap_checks;
  if(first>1)++restart_checks;
  ++pixels_checked;
 }
 /* Pixel pitch padding must never be touched by drawing or replay. */
 for(int y=0;y<canvas->h;y++)for(int i=canvas->w*4;i<canvas->pitch;i++)
  assert(((Uint8 *)canvas->pixels)[(size_t)y*canvas->pitch+i]==0xcd);
}
static void draw_event(int kind,Asset *asset,int x,int y,int style)
{
 assert(event_count<MAX_EVENTS);
 Event event={kind,x,y,style,0,asset,0};
 if(kind==HEAD)event.head_id=green_head_count+1;
 events[event_count++]=event;
 assert(draw_asset_filtered(x,y,asset,style,NULL,0));
 check_scene("draw");
}
static void original_write(int kind,int x,int y,int value)
{
 assert(event_count<MAX_EVENTS);
 events[event_count++]=(Event){kind,x,y,0,value,NULL,0};
 Uint8 *address=(Uint8 *)game_screen->pixels+y*game_screen->pitch+x;
 suppress=false;
 if(kind==INDEXED){*address=(Uint8)value;render_mirror_pixel(game_screen,address,*address,MIRROR_NORMAL);}
 else render_mirror_brightness_pixel(game_screen,address,value);
 check_scene(kind==INDEXED?"indexed invalidation":"brightness invalidation");
}
static void stamp_original(int x,int y,bool smoke)
{
 events[event_count++]=(Event){smoke?STAMP_SMOKE:STAMP_OTHER,x,y,0,0,NULL,0};
 assert(suppress&&suppress_green_smoke==smoke);
 Uint8 *address=(Uint8 *)game_screen->pixels+y*game_screen->pitch+x;
 render_mirror_pixel(game_screen,address,*address,MIRROR_NORMAL);
 check_scene(smoke?"suppressed smoke ownership":"suppressed non-smoke ownership");
}
static void restore_scene(void)
{
 events[event_count++]=(Event){RESTORE,0,0,0,0,NULL,0};
 restore_classic_rect((SDL_Rect){0,0,WIDTH,HEIGHT});
 check_scene("classic region restoration");
}
static void reset_scene(bool original_owned)
{
 size_t count=(size_t)canvas->w*canvas->h;
 initial_owner=original_owned?0:1;event_count=green_head_count=region_count=0;
 memset(hd_owner,initial_owner,count);memset(cloud_owner,0,count);memset(green_first,0,count*sizeof(*green_first));
 memset(green_under,0,count*sizeof(*green_under));memset(green_under_owner,0,count);
 memset(canvas->pixels,0xcd,(size_t)canvas->pitch*canvas->h);
 memset(selected,0,sizeof(selected));suppress=false;
 memset(game_screen->pixels,0,(size_t)game_screen->pitch*game_screen->h);
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++) {
  size_t n=(size_t)y*canvas->w+x;
  /* Original-owned case is uniform so the separate brightness interpolator
   * must equal its uniform input; this test isolates head-layer behavior. */
  Uint32 color=original_owned?0xff21374bu:0xff000000u|((x*31u+y*17u)%256u)<<16|((x*3u+y*47u)%256u)<<8|((x*71u+y*13u)%256u);
  initial[n]=color;*(Uint32 *)((Uint8 *)canvas->pixels+(size_t)y*canvas->pitch+x*4)=color;
 }
}
static Asset make_asset(int bank,int index,int density,int salt,int w,int h)
{
 Asset a={true,true,bank,index,w,h,0,0,density,NULL};
 a.rgba=malloc((size_t)w*h*density*density*4);assert(a.rgba);
 const Uint8 alphas[]={0,1,17,63,127,128,191,254,255};
 for(int y=0;y<h*density;y++)for(int x=0;x<w*density;x++) {
  Uint8 *pixel=a.rgba+4*(y*w*density+x);
  pixel[0]=(Uint8)(salt*43+x*17+y*3);pixel[1]=(Uint8)(salt*13+x*7+y*31);
  pixel[2]=(Uint8)(salt*71+x*11+y*19);pixel[3]=alphas[(x+y*3+salt)%9];
 }
 return a;
}
static void direct_replay_test(Asset *a,Asset *b,Asset *c)
{
 GreenHead heads[]={{a,-1,-1},{b,0,0},{c,1,1}};
 memcpy(green_heads,heads,sizeof(heads));green_head_count=3;
 int d=game_probe_density;
 for(unsigned int first=1;first<=4;first++)for(int y=-2*d;y<7*d;y++)for(int x=-2*d;x<8*d;x++) {
  Uint32 color=0xff3762a1u,want=color;
  for(unsigned int i=first;i<=3;i++) {
   Event event={HEAD,heads[i-1].x,heads[i-1].y,0,0,heads[i-1].asset,i};
   const Uint8 *sample=reference_sample(&event,x,y);
   if(sample)want=reference_alpha(want,sample);
  }
  Uint32 got=green_head_composite(x,y,first,color);
  if(got!=want){fprintf(stderr,"Direct replay mismatch d=%d first=%u x=%d y=%d\n",d,first,x,y);exit(1);}
  ++pixels_checked;
 }
}
int main(void)
{
 for(unsigned int i=0;i<256;i++)rgb_palette[i]=i*0x010101u;
 Asset h1=make_asset(8,214,2,1,5,4),h2=make_asset(8,215,4,2,5,4);
 Asset h3=make_asset(8,217,8,3,5,4),smoke=make_asset(ASSET_EXPLOSION,78,4,4,12,14);
 Asset other=make_asset(7,11,4,5,4,3);
 Asset empty_smoke=make_asset(ASSET_EXPLOSION,79,4,6,12,14);
 Asset empty_other=make_asset(7,12,4,7,4,3);
 for(int i=0;i<empty_smoke.w*empty_smoke.h*16;i++)empty_smoke.rgba[4*i+3]=0;
 for(int i=0;i<empty_other.w*empty_other.h*16;i++)empty_other.rgba[4*i+3]=0;
 for(int d=2;d<=8;d*=2) {
  game_probe_density=d;
  SDL_Surface surface={WIDTH*d,HEIGHT*d,WIDTH*d*4+16,NULL};canvas=&surface;
  SDL_Surface original={WIDTH,HEIGHT,WIDTH,NULL};game_screen=&original;
  size_t count=(size_t)surface.w*surface.h;
  surface.pixels=malloc((size_t)surface.pitch*surface.h);original.pixels=calloc(WIDTH*HEIGHT,1);
  initial=malloc(count*sizeof(*initial));hd_owner=malloc(count);cloud_owner=malloc(count);green_first=calloc(count,sizeof(*green_first));
  green_under=malloc(count*sizeof(*green_under));green_under_owner=malloc(count);
  assert(surface.pixels&&original.pixels&&initial&&hd_owner&&green_first&&green_under&&green_under_owner);
  direct_replay_test(&h1,&h2,&h3);
  for(int edge=0;edge<2;edge++)for(int blend=0;blend<2;blend++) {
   int x=edge?WIDTH-3:-1,y=edge?HEIGHT-3:-1;
   reset_scene(false);
   draw_event(HEAD,&h1,x,y,MIRROR_NORMAL);draw_event(HEAD,&h2,x+1,y+1,MIRROR_NORMAL);
   draw_event(SMOKE,&smoke,x,y,blend?MIRROR_BLEND:MIRROR_NORMAL);
   draw_event(HEAD,&h3,x+2,y+1,MIRROR_NORMAL);
   draw_event(SMOKE,&smoke,x+1,y,blend?MIRROR_BLEND:MIRROR_NORMAL);
   draw_event(OTHER,&other,x+1,y+1,MIRROR_NORMAL);
   draw_event(HEAD,&h1,x+1,y+1,MIRROR_NORMAL);
   draw_event(SMOKE,&smoke,x,y,blend?MIRROR_BLEND:MIRROR_NORMAL);
   if(!blend) {
    int ix=edge?WIDTH-2:1,iy=edge?HEIGHT-2:1;
    original_write(INDEXED,ix,iy,37);
    draw_event(HEAD,&h2,x+1,y+1,MIRROR_NORMAL);
    draw_event(SMOKE,&smoke,x,y,MIRROR_NORMAL);
    original_write(BRIGHTNESS,ix,iy,3);
    draw_event(HEAD,&h3,x+1,y+1,MIRROR_NORMAL);
    draw_event(SMOKE,&smoke,x,y,MIRROR_NORMAL);
   }
  }
  /* Fully clipped heads still consume a command index; restarting must use
   * the next real head, and transparent samples must never create a layer. */
  reset_scene(false);
  draw_event(HEAD,&h1,-20,-20,MIRROR_NORMAL);draw_event(HEAD,&h2,WIDTH,HEIGHT,MIRROR_NORMAL);
  draw_event(HEAD,&h3,2,2,MIRROR_NORMAL);draw_event(SMOKE,&smoke,1,1,MIRROR_NORMAL);
  /* A first head over classic scenery must snapshot owner=0 and let green
   * smoke use that saved ownership rather than the head's owner=1. */
  reset_scene(true);
  draw_event(HEAD,&h1,2,2,MIRROR_NORMAL);draw_event(HEAD,&h2,3,2,MIRROR_NORMAL);
  draw_event(SMOKE,&smoke,1,1,MIRROR_BLEND);
  /* Suppressed original coverage for transparent smoke changes only saved
   * ownership; non-smoke suppression must not claim the saved underlay. */
  reset_scene(true);
  draw_event(HEAD,&h1,2,2,MIRROR_NORMAL);
  draw_event(SMOKE,&empty_smoke,1,1,MIRROR_NORMAL);stamp_original(3,3,true);
  draw_event(OTHER,&empty_other,2,2,MIRROR_NORMAL);stamp_original(4,3,false);
  draw_event(SMOKE,&smoke,1,1,MIRROR_NORMAL);
  /* The real restoration helper invalidates all protected pixels. Old heads
   * must not reappear after a subsequent head establishes a new layer. */
  reset_scene(false);
  draw_event(HEAD,&h1,2,2,MIRROR_NORMAL);draw_event(HEAD,&h2,3,2,MIRROR_NORMAL);
  draw_event(SMOKE,&smoke,1,1,MIRROR_NORMAL);restore_scene();
  draw_event(HEAD,&h3,2,2,MIRROR_NORMAL);draw_event(SMOKE,&smoke,1,1,MIRROR_NORMAL);
  printf("PASS: head-layer exact replay, clipping, transparency, ownership and invalidation at density %d\n",d);
  free(surface.pixels);free(original.pixels);free(initial);free(hd_owner);
  free(green_first);free(green_under);free(green_under_owner);free(cloud_owner);
 }
 free(h1.rgba);free(h2.rgba);free(h3.rgba);free(smoke.rgba);free(other.rgba);
 free(empty_smoke.rgba);free(empty_other.rgba);
 assert(overlap_checks&&restart_checks&&transparent_checks);
 printf("PASS: %lu pixel comparisons; %lu overlapping-head, %lu later-start-index, %lu transparent-preservation checks\n",
  pixels_checked,overlap_checks,restart_checks,transparent_checks);
 return 0;
}
