/* Private bounded actual-menu fixture. SDL inputs, observation and capture only. */
#include "settings_fixture.h"
#include "video.h"
#include "video_scale.h"
#include "palette.h"
#include "nortsong.h"
#include "loudness.h"
#include "keyboard.h"
#include "mouse.h"
#include "mtrand.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define FNV UINT64_C(14695981039346656037)
struct Action {int menu,selected,picker,pick_selected;char input[16];int a,b;char capture[40];};
static struct Action actions[128];static unsigned n_actions,action,frame,total_present,settings_present,captures;
static unsigned title_present,startup_present;
static bool entered,inside,ready;static int menu,selected,picker,pick_selected;
static bool lease_active,lease_frame;static unsigned lease_commands,lease_generation;
static Uint32 readback[1600*1200]; /* fixture evidence only, never product allocation */
static uint64_t writes=FNV;static unsigned write_count;static FILE *trace,*indexed,*semantics;static const char *output;
static void fail(const char *s){fprintf(stderr,"SETTINGS FIXTURE FAIL: %s\n",s);exit(90);}
static uint64_t bytes(uint64_t h,const void *data,size_t n){const Uint8 *p=data;while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
static FILE *out(const char *name){char p[1200];if(snprintf(p,sizeof(p),"%s/%s",output,name)>=(int)sizeof(p))fail("output path");FILE *f=fopen(p,"wb");if(!f)fail("open output");return f;}
void sf_fixture_init(void)
{
 output=getenv("SF_FIXTURE_OUTPUT");const char *script=getenv("SF_FIXTURE_SCRIPT");if(!output||!script)fail("private output and action script required");FILE *f=fopen(script,"r");if(!f)fail("open actions");char line[256];
 while(fgets(line,sizeof(line),f)){if(line[0]=='#'||line[0]=='\n')continue;if(n_actions==128)fail("action cap");struct Action *a=&actions[n_actions++];if(sscanf(line,"%d %d %d %d %15s %d %d %39s",&a->menu,&a->selected,&a->picker,&a->pick_selected,a->input,&a->a,&a->b,a->capture)!=8)fail("action syntax");}fclose(f);if(!n_actions)fail("empty actions");
 trace=out("presentations.tsv");indexed=out("indexed-palette-stream.bin");semantics=out("semantics.tsv");
 fprintf(trace,"settings_present\tframe\taction\tmenu\tselected\tpicker\tpicker_selected\tscaler\tscaling_mode\tfullscreen\tmusic\tfx\tmusic_muted\tfx_muted\tRNG\twrites\twrite_count\towner\tlease_active\tlease_frame\tcommands\tgeneration\twidth\theight\timage\tmouse_x\tmouse_y\tmouse_inactive\thas_mouse\tdisplays\tframebuffer_fnv64\n");
 fprintf(semantics,"fixed_seed\t32402394\n");fflush(semantics);
}
static void key(SDL_Scancode scan,SDL_Keymod mod)
{
 SDL_Event e;memset(&e,0,sizeof(e));e.type=SDL_KEYDOWN;e.key.state=SDL_PRESSED;e.key.keysym.scancode=scan;e.key.keysym.sym=SDL_GetKeyFromScancode(scan);e.key.keysym.mod=mod;if(SDL_PushEvent(&e)!=1)fail("key down");e.type=SDL_KEYUP;e.key.state=SDL_RELEASED;if(SDL_PushEvent(&e)!=1)fail("key up");
}
void sf_fixture_title(size_t current)
{
 fprintf(semantics,"outside_owners\t%u\t%u\n",title_present,startup_present);fflush(semantics);
 if(!entered)key(current==4?SDL_SCANCODE_RETURN:SDL_SCANCODE_DOWN,KMOD_NONE);
 else {if(inside||action!=n_actions)fail("early title return");fprintf(semantics,"title_return\t%zu\n",current);fflush(semantics);key(SDL_SCANCODE_ESCAPE,KMOD_NONE);}
}
void sf_fixture_frame(unsigned m,size_t s,unsigned p,size_t ps)
{
 if(++frame>128)fail("frame cap");entered=inside=true;ready=false;menu=m;selected=s;picker=p;pick_selected=ps;writes=FNV;write_count=0;
 fprintf(semantics,"frame\t%u\t%d\t%d\t%d\t%d\n",frame,menu,selected,picker,pick_selected);fflush(semantics);
}
void sf_fixture_ready(void)
{
 if(action>=n_actions)fail("actions exhausted");struct Action *a=&actions[action];
 if(menu!=a->menu||selected!=a->selected||picker!=a->picker||(picker&&pick_selected!=a->pick_selected))fail("unexpected original menu state");ready=true;
}
void sf_fixture_advance(void)
{
 if(!ready||action>=n_actions)fail("advance order");struct Action *a=&actions[action];fprintf(semantics,"input\t%u\t%s\t%d\t%d\n",action,a->input,a->a,a->b);fflush(semantics);ready=false;action++;
 if(!strcmp(a->input,"key")){key((SDL_Scancode)a->a,KMOD_NONE);return;}
 if(!strcmp(a->input,"alt_enter")){key(SDL_SCANCODE_RETURN,KMOD_ALT);return;}
 if(!strcmp(a->input,"resize")){SDL_SetWindowSize(main_window,a->a,a->b);key(SDL_SCANCODE_F12,KMOD_NONE);return;}
 if(!strcmp(a->input,"move")||!strcmp(a->input,"left")||!strcmp(a->input,"right")){
  Sint32 x=a->a,y=a->b;mapScreenPointToWindow(&x,&y);SDL_Event e;memset(&e,0,sizeof(e));e.type=SDL_MOUSEMOTION;e.motion.x=x;e.motion.y=y;e.motion.xrel=1;e.motion.yrel=1;if(SDL_PushEvent(&e)!=1)fail("mouse motion");
  if(strcmp(a->input,"move")){e.type=SDL_MOUSEBUTTONDOWN;e.button.state=SDL_PRESSED;e.button.button=!strcmp(a->input,"left")?SDL_BUTTON_LEFT:SDL_BUTTON_RIGHT;e.button.x=x;e.button.y=y;if(SDL_PushEvent(&e)!=1)fail("mouse down");e.type=SDL_MOUSEBUTTONUP;e.button.state=SDL_RELEASED;if(SDL_PushEvent(&e)!=1)fail("mouse up");}return;
 }
 fail("unknown input");
}
void sf_fixture_exit(void){if(action!=n_actions)fail("incomplete actions");inside=false;fprintf(semantics,"settings_exit\t%u\n",action);fflush(semantics);}
void sf_fixture_lease(bool a,bool f,unsigned c,unsigned g){lease_active=a;lease_frame=f;lease_commands=c;lease_generation=g;}
void sf_fixture_pixel(SDL_Surface *s,Uint8 *p,int style)
{
 if(!inside||s!=VGAScreen)return;uintptr_t off=(uintptr_t)p-(uintptr_t)s->pixels;if(off>=64000)fail("indexed write bounds");Uint8 event[4]={(Uint8)off,(Uint8)(off>>8),*p,(Uint8)style};writes=bytes(writes,event,4);write_count++;
}
void sf_fixture_rect(SDL_Surface *s,const SDL_Rect *r)
{if(!inside||s!=VGAScreen)return;int x=r?r->x:0,y=r?r->y:0,w=r?r->w:s->w,h=r?r->h:s->h;for(int yy=y;yy<y+h;yy++)for(int xx=x;xx<x+w;xx++)if(xx>=0&&yy>=0&&xx<320&&yy<200)sf_fixture_pixel(s,(Uint8 *)s->pixels+yy*s->pitch+xx,0);}
void sf_fixture_fade(int remaining,unsigned first,unsigned last){if(inside){fprintf(semantics,"fade\t%d\t%u\t%u\n",remaining,first,last);fflush(semantics);}}
void sf_fixture_wait(const char *kind,int argument){if(inside){fprintf(semantics,"wait\t%s\t%d\n",kind,argument);fflush(semantics);}}
void sf_fixture_present(SDL_Renderer *renderer,const char *owner)
{
 if(++total_present>512)fail("presentation cap");if(!inside){if(!strcmp(owner,"title"))title_present++;if(!strcmp(owner,"startup"))startup_present++;return;}if(++settings_present>256)fail("settings presentation cap");int w,h;if(SDL_GetRendererOutputSize(renderer,&w,&h))fail("output dimensions");
 if(fwrite(VGAScreen->pixels,1,64000,indexed)!=64000||fwrite(rgb_palette,1,1024,indexed)!=1024)fail("indexed stream write");fflush(indexed);
 if(w<1||h<1||w>1600||h>1200||SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,readback,w*4))fail("bounded framebuffer hash readback");uint64_t framebuffer_hash=bytes(FNV,readback,(size_t)w*h*4);
 const char *capture=ready?actions[action].capture:"-";
 if(strcmp(capture,"-")&&!getenv("SF_FIXTURE_HASH_ONLY")){
  if(++captures>10)fail("capture cap");if(w<=0||h<=0||w>1280||h>800)fail("capture dimensions");SDL_Surface *image=SDL_CreateRGBSurfaceWithFormat(0,w,h,32,SDL_PIXELFORMAT_ARGB8888);if(!image||SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,image->pixels,image->pitch))fail("renderer readback");char name[1200];snprintf(name,sizeof(name),"%s/%s.bmp",output,capture);if(SDL_SaveBMP(image,name))fail("save still");SDL_FreeSurface(image);
 }
 fprintf(trace,"%u\t%u\t%u\t%d\t%d\t%d\t%d\t%u\t%d\t%d\t%u\t%u\t%d\t%d\t%016llx\t%016llx\t%u\t%s\t%d\t%d\t%u\t%u\t%d\t%d\t%s\t%d\t%d\t%d\t%d\t%d\t%016llx\n",settings_present,frame,action,menu,selected,picker,pick_selected,scaler,scaling_mode,fullscreen_display,tyrMusicVolume,fxVolume,music_disabled,samples_disabled,(unsigned long long)mt_state_fingerprint(),(unsigned long long)writes,write_count,owner,lease_active,lease_frame,lease_commands,lease_generation,w,h,capture,mouse_x,mouse_y,mouseInactive,has_mouse,SDL_GetNumVideoDisplays(),(unsigned long long)framebuffer_hash);fflush(trace);
}
