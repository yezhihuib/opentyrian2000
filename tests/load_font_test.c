/* Source/core-only test. Reads local original data; never distributes it. */
#define _POSIX_C_SOURCE 200809L
#include <stdlib.h>
#include <limits.h>
static unsigned allocation_calls,fail_allocation=UINT_MAX;
static size_t allocated,peak_allocated;
static struct {void *p;size_t size;} allocations[4];
static void *lease_malloc(size_t n){if(allocation_calls++==fail_allocation)return NULL;void *p=malloc(n);if(p){unsigned i=0;while(i<4&&allocations[i].p)i++;if(i==4)abort();allocations[i].p=p;allocations[i].size=n;allocated+=n;if(allocated>peak_allocated)peak_allocated=allocated;}return p;}
static void lease_free(void *p){if(p){unsigned i=0;while(i<4&&allocations[i].p!=p)i++;if(i==4)abort();allocated-=allocations[i].size;allocations[i].p=NULL;free(p);}}
#define malloc lease_malloc
#define free lease_free
#include <assert.h>
#include <sys/stat.h>
#include <unistd.h>
#include "../src/load_font.c"
#undef malloc
#undef free
#include "../src/nortvars.h"
#include "../src/vga256d.h"
#include "../src/title_layers.h"
SDL_Surface *VGAScreen,*VGAScreenSeg,*VGAScreen2,*game_screen;
SDL_Window *main_window;SDL_PixelFormat *main_window_tex_format;
Palette palettes[24],colors;int palette_count=24;
Uint32 rgb_palette[256],yuv_palette[256];
ScalingMode scaling_mode=SCALE_INTEGER;
static unsigned checks,states,max_commands;
static uint64_t trace;static unsigned trace_count;
void render_mirror_pixel(SDL_Surface *s,Uint8 *p,Uint8 color,int style){(void)color;uintptr_t n=(uintptr_t)p-(uintptr_t)s->pixels;for(unsigned i=0;i<4;i++)trace=(trace^((n>>(i*8))&255))*UINT64_C(1099511628211);trace=(trace^*p)*UINT64_C(1099511628211);trace=(trace^style)*UINT64_C(1099511628211);++trace_count;load_font_pixel(s,p,style);settings_font_pixel(s,p,style);}
void render_mirror_rect(SDL_Surface *s,const SDL_Rect *r){load_font_rect(s,r);settings_font_rect(s,r);}
void render_mirror_text_glyph_begin(SDL_Surface *s,int x,int y,unsigned t,unsigned id,bool black,unsigned hue,int value){(void)s;(void)x;(void)y;(void)t;(void)id;(void)black;(void)hue;(void)value;}
void render_mirror_text_glyph_end(void){}
void title_layers_pixel(SDL_Surface *s,Uint8 *p,enum TitleWriter w){(void)s;(void)p;(void)w;}
void render_mirror_unsupported(const char *s){(void)s;}
void asset_debug_effect(SDL_Surface *s,Sprite2_array a,unsigned id,int x,int y){(void)s;(void)a;(void)id;(void)x;(void)y;}

#define REQUIRE(expr) do { ++checks;if(!(expr)){fprintf(stderr,"FAIL %s:%d: %s (stage=%d role=%u row=%u cmd=%u/%u pixel=%u active=%d frame=%d)\n",__FILE__,__LINE__,#expr,sf.stage,sf.run_next,sf.row,sf.next,sf.limit,sf.pixel,sf.active,sf.frame);abort();} } while(0)
static unsigned rd16(FILE *f){unsigned a=fgetc(f),b=fgetc(f);return a|(b<<8);}
static unsigned rd32(FILE *f){unsigned a=rd16(f),b=rd16(f);return a|(b<<16);}
static FILE *open_data(const char *d,const char *n){char p[1024];snprintf(p,sizeof(p),"%s/%s",d,n);FILE *f=fopen(p,"rb");REQUIRE(f);return f;}
static void fixtures(const char *d)
{
 FILE *f=open_data(d,"newsh1.shp");fseek(f,0,SEEK_END);shopSpriteSheet.size=ftell(f);rewind(f);shopSpriteSheet.data=malloc(shopSpriteSheet.size);REQUIRE(fread(shopSpriteSheet.data,1,shopSpriteSheet.size,f)==shopSpriteSheet.size);fclose(f);
 f=open_data(d,"tyrian.shp");unsigned n=rd16(f),offset[32];REQUIRE(n<32);for(unsigned i=0;i<n;i++)offset[i]=rd32(f);
 for(unsigned b=0;b<3;b++){fseek(f,offset[b],SEEK_SET);sprite_table[b].count=rd16(f);for(unsigned id=0;id<sprite_table[b].count;id++){REQUIRE(fgetc(f)==1);Sprite *s=sprite(b,id);s->width=rd16(f);s->height=rd16(f);s->size=rd16(f);s->data=malloc(s->size);REQUIRE(s->data&&fread(s->data,1,s->size,f)==s->size);}}fclose(f);
 f=open_data(d,"palette.dat");for(unsigned p=0;p<24;p++)for(unsigned i=0;i<256;i++){unsigned r=fgetc(f),g=fgetc(f),b=fgetc(f);palettes[p][i]=(SDL_Color){r*4+(r>>4),g*4+(g>>4),b*4+(b>>4),255};}fclose(f);memcpy(colors,palettes[7],sizeof(colors));
 f=open_data(d,"tyrian.pic");n=rd16(f);REQUIRE(n<32);for(unsigned i=0;i<n;i++)offset[i]=rd32(f);fseek(f,offset[1],SEEK_SET);unsigned p=0;while(p<SF_N){unsigned v=fgetc(f),count=1;if((v&192)==192){count=v&63;v=fgetc(f);}REQUIRE(p+count<=SF_N);memset((Uint8 *)VGAScreen2->pixels+p,v,count);p+=count;}fclose(f);memset((Uint8 *)VGAScreen2->pixels+192*320,0,8*320);
}
static void live_palette(const SDL_Color *p){for(unsigned i=0;i<256;i++)rgb_palette[i]=SDL_MapRGB(main_window_tex_format,p[i].r,p[i].g,p[i].b);}
static void acquire(const char *directory)
{load_font_set_directory(directory);memset(rgb_palette,0,sizeof(rgb_palette));load_font_begin(VGAScreen,VGAScreen2);REQUIRE(sf.active);}

JE_SaveFilesType saveFiles;
static const struct {const char *name;struct {unsigned level,episode;const char *name,*level_name;} slots[22];} profiles[]={
{"\141\154\154\137\145\155\160\164\171",{{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""}}},
{"\155\151\170\145\144",{{1,1,"\101","\124\131\122\111\101\116"},{1,2,"\101\103\105\040\061","\102\125\102\102\114\105\123"},{1,3,"\154\157\167\145\162\143\141\163\145","\101\123\124\105\122\117\111\104"},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{1,5,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,1,"\060\061\062\063\064\065\066\067\070\071","\103\157\155\160\154\145\164\145\144"},{1,2,"\041\042\043\044\045\047\050\051\052\053\054\055\056\057","\104\105\114\111\101\116\111"},{1,3,"\072\073\077\075\133\135\173\175\134\174",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{1,5,"\103\157\155\160\154\145\164\145\144","\115\111\116\105\123"},{1,1,"\114\101\123\124\040\114\105\126\105\114\040\040\040\040","\124\131\122\111\101\116"},{1,2,"\101","\124\131\122\111\101\116"},{1,3,"\101\103\105\040\061","\102\125\102\102\114\105\123"},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{1,5,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\123\101\126\101\122\101"},{1,1,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,2,"\060\061\062\063\064\065\066\067\070\071","\103\157\155\160\154\145\164\145\144"},{1,3,"\041\042\043\044\045\047\050\051\052\053\054\055\056\057","\104\105\114\111\101\116\111"},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{1,5,"\040\040\040\120\101\104\104\105\104\040\040\040\040\040","\101"},{1,1,"\103\157\155\160\154\145\164\145\144","\115\111\116\105\123"},{1,2,"\114\101\123\124\040\114\105\126\105\114\040\040\040\040","\124\131\122\111\101\116"}}},
{"\167\151\144\145\163\164",{{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"},{1,255,"\127\127\127\127\127\127\127\127\127\127\127\127\127\127","\127\127\127\127\127\127\127\127\127"}}},
{"\155\141\170\137\143\157\155\155\141\156\144\163",{{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"},{1,255,"\101\102\103\104\105\106\107\110\111\112\113\114\115\116","\101\102\103\104\105\106\107\110\111\112"}}},
{"\146\141\154\154\142\141\143\153\137\164\151\154\144\145",{{1,1,"\101\176\102","\124\131\122\111\101\116"},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""}}},
{"\146\141\154\154\142\141\143\153\137\165\156\155\141\160\160\145\144",{{1,1,"\101\046\102","\124\131\122\111\101\116"},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""}}},
{"\146\141\154\154\142\141\143\153\137\145\170\164\145\156\144\145\144",{{1,1,"\101\200\102","\124\131\122\111\101\116"},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""}}},
{"\146\141\154\154\142\141\143\153\137\143\157\156\164\162\157\154",{{1,1,"\101\001\102","\124\131\122\111\101\116"},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""},{0,0,"\040\040\040\040\040\040\040\040\040\040\040\040\040\040",""}}},
};

static void strings(void)
{
 strcpy(miscText[38],"One Player Saved Games");strcpy(miscText[39],"Two Player Saved Games");strcpy(miscText[2],"EMPTY SLOT");strcpy(miscText[33],"Exit to Main Menu");strcpy(miscTextB[2],"Last Level");strcpy(miscTextB[1],"Episode");strcpy(miscText[55],"~Left~ or ~right~ for 1 or 2 player game.");helpBoxColor=12;helpBoxBrightness=1;helpBoxShadeType=FULL_SHADE;verticalHeight=7;
}
static void profile(unsigned p)
{memset(saveFiles,0,sizeof(saveFiles));for(unsigned i=0;i<22;i++){saveFiles[i].level=profiles[p].slots[i].level;saveFiles[i].episode=profiles[p].slots[i].episode;strcpy(saveFiles[i].name,profiles[p].slots[i].name);strcpy(saveFiles[i].levelName,profiles[p].slots[i].level_name);}}
static void text_run(unsigned role,unsigned row,int x,int y,const char *text,unsigned bank,int alignment,unsigned hue,int value)
{
 load_font_run_begin(role,row,VGAScreen,x,y,text,bank,alignment,hue,value);
 if(bank==2)JE_textShade(VGAScreen,x,y,text,hue,value,FULL_SHADE);else draw_font_hv_shadow(VGAScreen,x,y,text,bank,alignment,hue,value,false,2);
 load_font_run_end();
}
static void frame(unsigned page,unsigned selected)
{
 memcpy(VGAScreen->pixels,VGAScreen2->pixels,SF_N);trace=SF_FNV;trace_count=0;load_font_frame_begin(page,selected);
 text_run(LOAD_HEADING,0,160,5,miscText[38+page],0,centered,15,-3);
 for(unsigned row=0;row<12;row++){
  int y=30+13*row;if(row==11){text_run(LOAD_EXIT,row,10,y,miscText[33],2,left_aligned,13,row==selected?6:2);continue;}
  const JE_SaveFileType *slot=&saveFiles[page*11+row];bool empty=slot->level==0;int v=row==selected?6:empty?0:2;char buf[22];
  text_run(LOAD_NAME,row,10,y,empty?miscText[2]:slot->name,2,left_aligned,13,v);
  snprintf(buf,sizeof(buf),"%s %s",miscTextB[2],empty?"-----":slot->levelName);text_run(LOAD_LEVEL,row,120,y,buf,2,left_aligned,5,v);
  if(!empty){snprintf(buf,sizeof(buf),"%s %u",miscTextB[1],slot->episode);text_run(LOAD_EPISODE,row,250,y,buf,2,left_aligned,5,v);}
 }
 load_font_arrow_begin();blit_sprite2x2(VGAScreen,page?83:213,179,shopSpriteSheet,page?279:281);load_font_arrow_end();
 helpBoxColor=15;load_font_help_begin(VGAScreen,103,182,miscText[55],25);JE_helpBox(VGAScreen,103,182,miscText[55],25);load_font_help_end();load_font_frame_end();
 if(sf.frame){REQUIRE(sf.stage==S_READY&&sf.run_count<=37&&sf.arrow_writes==204);if(sf.count>max_commands)max_commands=sf.count;}states++;
}
static int original_role(unsigned bank,unsigned id,unsigned tx,unsigned ty)
{
 const Sprite *s=sprite(bank,id);unsigned x=0,y=0;
 for(unsigned k=0;k<s->size;k++){unsigned v=s->data[k];if(v==255)x+=s->data[++k];else if(v==254)x=s->width;else if(v==253)x++;else{if(x==tx&&y==ty)return v&15;x++;}if(x==s->width){x=0;y++;}}
 return -1;
}
static Uint32 oracle_sample(unsigned x,unsigned y)
{
 unsigned p=(y/4)*320+x/4;Uint8 index=sf.base[p];Uint32 color=sf.palette[index];
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];if(x<c->x*4u||x>=(c->x+c->w)*4u||y<c->y*4u||y>=(c->y+c->h)*4u)continue;
  if(c->kind>=C_SOLID){index=c->kind==C_SOLID?(Uint8)c->value:(index&240)|((index&15)>>1);color=sf.palette[index];continue;}
  unsigned gx=x-c->x*4u,gy=y-c->y*4u;const struct SfSpec *sp=&spec[c->bank];unsigned off=((c->id/16)*sp->ch+4+gy)*sp->aw+(c->id%16)*sp->cw+4+gx;unsigned a=sf.payload[c->bank][off];
  unsigned role=c->bank==2?7:sf.payload[c->bank][sp->plane+off];int tone=(int)role+c->value;if(c->bank!=2){if(tone<0)tone=0;if(tone>15)tone=15;}
  Uint8 ink=c->kind==C_DARK?(index&240)|((index&15)>>1):c->kind==C_BLACK?0:(c->hue<<4)|tone;Uint32 fg=sf.palette[ink],next=0xff000000;
  for(unsigned ch=0;ch<3;ch++){unsigned sh=ch*8;next|=((((fg>>sh)&255)*a+((color>>sh)&255)*(255-a)+127)/255)<<sh;}color=next;
  int original=original_role(c->bank,c->id,gx/4,gy/4);if(original>=0){tone=original+c->value;if(c->bank!=2){if(tone<0)tone=0;if(tone>15)tone=15;}index=c->kind==C_DARK?(index&240)|((index&15)>>1):c->kind==C_BLACK?0:(c->hue<<4)|tone;}
 }
 return sf.cursor_mask[p]?sf.palette[sf.cursor_index[p]]:color;
}
/* Independently rebuild each footer line's original-or-authored support, then
 * check all 16 canonical samples at every overlap pixel against the oracle. */
static void footer_overlap_checks(void)
{
 Uint8 coverage[2][64000]={{0}};
 for(unsigned line=0;line<2;line++)for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];if(c->bank!=2||c->hue!=15||c->y<181)continue;
  bool belongs=line==0?c->y<=183:c->y>=188;if(!belongs)continue;
  const struct SfSpec *sp=&spec[2];
  for(unsigned y=0;y<c->h;y++)for(unsigned x=0;x<c->w;x++){
   bool ink=original_role(2,c->id,x,y)>=0;
   for(unsigned dy=0;dy<4&&!ink;dy++)for(unsigned dx=0;dx<4;dx++){
    unsigned a=((c->id/16)*sp->ch+4+4*y+dy)*sp->aw+(c->id%16)*sp->cw+4+4*x+dx;if(sf.payload[2][a]){ink=true;break;}
   }
   if(ink)coverage[line][(c->y+y)*320+c->x+x]=1;
  }
 }
 unsigned overlaps=0;for(unsigned p=0;p<64000;p++)if(coverage[0][p]&&coverage[1][p]){++overlaps;for(unsigned dy=0;dy<4;dy++)for(unsigned dx=0;dx<4;dx++){unsigned x=(p%320)*4+dx,y=(p/320)*4+dy;REQUIRE(sf.output[y*1280+x]==oracle_sample(x,y));}}
 REQUIRE(overlaps==4);
}
static void portable_checks(void);
static void render_checks(void)
{
 render();REQUIRE(!memcmp(sf.replay,sf.expected,SF_N));footer_overlap_checks();
 for(unsigned n=0;n<128;n++){unsigned x=(n*137+states*17)%1280,y=(n*79+states*29)%800;REQUIRE(sf.output[y*1280+x]==oracle_sample(x,y));}
 for(unsigned p=0;p<SF_N;p++)if(!sf.owner[p])for(unsigned dy=0;dy<4;dy++)for(unsigned dx=0;dx<4;dx++)REQUIRE(sf.output[((p/320)*4+dy)*1280+(p%320)*4+dx]==sf.palette[sf.expected[p]]);
 Uint32 pair_oracle[32];unsigned pair_x[32],pair_y[32];for(unsigned n=0;n<32;n++){unsigned x=(n*97+states*31)%640,y=(n*47+states*13)%400;pair_x[n]=x;pair_y[n]=y;Uint32 v=0xff000000,q[4]={oracle_sample(2*x,2*y),oracle_sample(2*x+1,2*y),oracle_sample(2*x,2*y+1),oracle_sample(2*x+1,2*y+1)};for(unsigned sh=0;sh<=16;sh+=8)v|=((((q[0]>>sh)&255)+((q[1]>>sh)&255)+((q[2]>>sh)&255)+((q[3]>>sh)&255)+2)/4)<<sh;pair_oracle[n]=v;}
 Uint32 expected[640];for(unsigned x=0;x<640;x++){Uint32 v=0xff000000;for(unsigned sh=0;sh<=16;sh+=8){unsigned p=2*x;unsigned sum=((sf.output[p]>>sh)&255)+((sf.output[p+1]>>sh)&255)+((sf.output[p+1280]>>sh)&255)+((sf.output[p+1281]>>sh)&255);v|=((sum+2)/4)<<sh;}expected[x]=v;}reduce2();REQUIRE(!memcmp(expected,sf.output,sizeof(expected)));for(unsigned n=0;n<32;n++)REQUIRE(sf.output[pair_y[n]*640+pair_x[n]]==pair_oracle[n]);
 portable_checks();
}
static void write_bytes(const char *path,const Uint8 *p,size_t n)
{FILE *f=fopen(path,"wb");REQUIRE(f);REQUIRE(fwrite(p,1,n,f)==n);REQUIRE(!fclose(f));}
static void failed_acquire(const char *d)
{
 Uint8 before[SF_N];memcpy(before,VGAScreen->pixels,SF_N);load_font_set_directory(d);load_font_begin(VGAScreen,VGAScreen2);REQUIRE(!sf.active&&!sf.output&&allocated==0);REQUIRE(!memcmp(before,VGAScreen->pixels,SF_N));
}
static void resource_failures(const char *d)
{
 char temp[]="/tmp/settings-font-test-XXXXXX";REQUIRE(mkdtemp(temp));char paths[3][1024];Uint8 *files[3];size_t sizes[3];
 load_font_end();
 for(unsigned b=0;b<3;b+=2){char in[1024];snprintf(in,sizeof(in),"%s/settings-font-%s-v1.hda",d,spec[b].name);FILE *f=fopen(in,"rb");REQUIRE(f);sizes[b]=128+spec[b].plane*(spec[b].mode?2:1);files[b]=malloc(sizes[b]+1);REQUIRE(files[b]&&fread(files[b],1,sizes[b],f)==sizes[b]);fclose(f);snprintf(paths[b],sizeof(paths[b]),"%s/settings-font-%s-v1.hda",temp,spec[b].name);write_bytes(paths[b],files[b],sizes[b]);}
 for(unsigned b=0;b<3;b+=2){
  for(unsigned offset=0;offset<128;offset+=4){files[b][offset]^=128;write_bytes(paths[b],files[b],sizes[b]);failed_acquire(temp);files[b][offset]^=128;}
  const size_t lengths[]={0,127,sizes[b]-1,sizes[b]+1};for(unsigned i=0;i<4;i++){write_bytes(paths[b],files[b],lengths[i]);failed_acquire(temp);}
  files[b][128]^=1;write_bytes(paths[b],files[b],sizes[b]);failed_acquire(temp);files[b][128]^=1;
  REQUIRE(!unlink(paths[b]));failed_acquire(temp);REQUIRE(!mkdir(paths[b],0700));failed_acquire(temp);REQUIRE(!rmdir(paths[b]));REQUIRE(!mkfifo(paths[b],0600));failed_acquire(temp);REQUIRE(!unlink(paths[b]));write_bytes(paths[b],files[b],sizes[b]);
 }
 for(unsigned i=0;i<3;i++){load_font_end();fail_allocation=allocation_calls+i;load_font_set_directory(temp);load_font_begin(VGAScreen,VGAScreen2);REQUIRE(!sf.active&&allocated==0);fail_allocation=UINT_MAX;}
 /* Medium is neither read nor required by this owner. */
 acquire(temp);REQUIRE(sf.payload[1]==NULL);for(unsigned b=0;b<3;b+=2){
  Uint8 *p=sf.payload[b];Uint8 old=p[0];p[0]=255;REQUIRE(!padding(b,p));p[0]=old;
  if(spec[b].mode){p[spec[b].plane]=12;REQUIRE(!padding(b,p));p[spec[b].plane]=0;unsigned ink=0;while(!p[ink])ink++;old=p[spec[b].plane+ink];p[spec[b].plane+ink]=11;REQUIRE(!padding(b,p));p[spec[b].plane+ink]=old;}
  REQUIRE(padding(b,p));
 }
 load_font_end();for(unsigned b=0;b<3;b+=2){REQUIRE(!unlink(paths[b]));free(files[b]);}REQUIRE(!rmdir(temp));
}

static void begin_simple(void)
{memcpy(VGAScreen->pixels,VGAScreen2->pixels,SF_N);load_font_frame_begin(0,0);REQUIRE(sf.frame);}
static void observer_failures(const char *d)
{
 acquire(d);profile(0);strings();begin_simple();load_font_run_begin(LOAD_HEADING,0,VGAScreen,160,5,"Settings",0,centered,15,-3);REQUIRE(!sf.frame&&sf.active);
 begin_simple();load_font_run_begin(LOAD_HEADING,0,VGAScreen,160,5,headings[0],1,centered,15,-3);REQUIRE(!sf.frame);
 begin_simple();load_font_run_begin(LOAD_HEADING,0,VGAScreen,160,5,headings[0],0,centered,15,-3);load_font_run_end();REQUIRE(!sf.frame);
 begin_simple();load_font_run_begin(LOAD_HEADING,0,VGAScreen,160,5,headings[0],0,centered,15,-3);struct SfCommand c=sf.commands[sf.next];load_font_glyph_begin(VGAScreen,c.x,c.y,c.bank,c.id,LOAD_FACE,15,-3);REQUIRE(!sf.frame);
 begin_simple();sf.count=SF_COMMANDS;load_font_run_begin(LOAD_HEADING,0,VGAScreen,160,5,headings[0],0,centered,15,-3);REQUIRE(!sf.frame);
 frame(0,0);REQUIRE(sf.frame);load_font_pixel(VGAScreen,VGAScreen->pixels,0);REQUIRE(!sf.frame);
 frame(0,0);load_font_cursor_begin();load_font_pixel(VGAScreen,VGAScreen->pixels,0);REQUIRE(!sf.frame);
 frame(0,0);load_font_cursor_begin();load_font_cursor_done();((Uint8 *)VGAScreen->pixels)[100]^=1;load_font_cursor_erased();REQUIRE(!sf.frame);
 helpBoxBrightness=2;frame(0,0);REQUIRE(!sf.frame);strings();verticalHeight=8;frame(0,0);REQUIRE(!sf.frame);strings();helpBoxShadeType=PART_SHADE;frame(0,0);REQUIRE(!sf.frame);strings();miscTextB[2][0]='X';frame(0,0);REQUIRE(!sf.frame);strings();
 profile(1);saveFiles[0].level=1;memset(saveFiles[0].name,'W',15);memcpy(VGAScreen->pixels,VGAScreen2->pixels,SF_N);load_font_frame_begin(0,0);REQUIRE(!sf.frame); /* Never execute original unterminated draw. */
 strcpy(saveFiles[0].name,"OK");memset(saveFiles[0].levelName,'W',11);memcpy(VGAScreen->pixels,VGAScreen2->pixels,SF_N);load_font_frame_begin(0,0);REQUIRE(!sf.frame);
 profile(0);saveFiles[0].level=1;strcpy(saveFiles[0].name,"");strcpy(saveFiles[0].levelName,"");frame(0,0);REQUIRE(sf.frame);strcpy(saveFiles[0].name,"              ");strcpy(saveFiles[0].levelName,"          ");frame(0,0);REQUIRE(sf.frame);
 for(unsigned ch=33;ch<127;ch++)if(ch!='~'&&font_ascii[ch]>=0&&font_ascii[ch]<86){saveFiles[0].name[0]=ch;saveFiles[0].name[1]=0;frame(0,0);REQUIRE(sf.frame);}
 /* All bad visible bytes fail without normalizing either field. */
 for(unsigned field=0;field<2;field++)for(unsigned ch=1;ch<256;ch++){
  bool allowed=ch==' '||(ch>=33&&ch<127&&ch!='~'&&font_ascii[ch]>=0&&font_ascii[ch]<86);if(allowed)continue;
  profile(0);saveFiles[0].level=1;char *text=field?saveFiles[0].levelName:saveFiles[0].name;text[0]=ch;text[1]=0;memcpy(VGAScreen->pixels,VGAScreen2->pixels,SF_N);load_font_frame_begin(0,0);REQUIRE(!sf.frame);frame(1,0);REQUIRE(sf.frame);
 }
 profile(0);frame(0,0);load_font_cursor_begin();load_font_cursor_sprite_begin(VGAScreen,0,0,shopSpriteSheet.data,shopSpriteSheet.size,274);REQUIRE(!sf.frame);
 frame(0,0);load_font_cursor_begin();unsigned pos=40*320+48;Uint8 old=((Uint8 *)VGAScreen->pixels)[pos];sf.cursor_sprite=true;sf.cursor_events=1;sf.cursor_next=0;sf.cursor_event[0].position=pos;sf.cursor_event[0].index=old;
 load_font_pixel(VGAScreen,(Uint8 *)VGAScreen->pixels+pos,0);REQUIRE(sf.cursor_mask[pos]);sf.cursor_sprite=false;sf.cursor_quad=4;load_font_cursor_done();REQUIRE(sf.frame);render();REQUIRE(sf.output[160*1280+192]==sf.palette[old]);memcpy(VGAScreen->pixels,sf.pre_cursor,SF_N);load_font_cursor_erased();REQUIRE(sf.frame&&!sf.cursor_mask[pos]);
 profile(0);begin_simple();Sprite *g=sprite(2,0);Uint8 *original=g->data,*copy=malloc(g->size);memcpy(copy,original,g->size);g->data=copy;load_font_frame_end();REQUIRE(!sf.active);g->data=original;free(copy);
 acquire(d);begin_simple();Uint8 r=palettes[7][0].r;palettes[7][0].r^=1;load_font_frame_end();REQUIRE(!sf.active);palettes[7][0].r=r;
 acquire(d);begin_simple();((Uint8 *)VGAScreen2->pixels)[0]^=1;load_font_frame_end();REQUIRE(!sf.active);((Uint8 *)VGAScreen2->pixels)[0]^=1;
 acquire(d);begin_simple();int pitch=VGAScreen->pitch;VGAScreen->pitch++;load_font_frame_end();REQUIRE(!sf.active);VGAScreen->pitch=pitch;
 acquire(d);frame(0,0);load_font_fade_declare(9);REQUIRE(!sf.active);
 acquire(d);frame(0,0);load_font_fade_start(palettes[7],NULL,0,255);REQUIRE(!sf.active);
 acquire(d);frame(0,0);load_font_fade_declare(10);load_font_fade_start(palettes[7],NULL,0,255);load_font_fade_step(9,0,255);REQUIRE(!sf.active);
}

#define PORTABLE_FN(name) load_font_##name
#define PORTABLE_FACE(role,c) face(role,(c)->value,(c)->hue,(c)->bank==2)
#define PORTABLE_SOLID(p) append(C_SOLID,(p)%320,(p)/320,1,1,0,0,0,sf.expected[p])
#define PORTABLE_FRAME() do{profile(1);frame(1,3);}while(0)
#include "settings_load_portability.inc"

int main(int argc,char **argv)
{
 REQUIRE(argc==3);scaler=1;main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);REQUIRE(VGAScreen&&VGAScreen2&&main_window_tex_format);fixtures(argv[1]);strings();acquire(argv[2]);
 size_t both_static=sizeof(sf)+settings_font_static_bytes();REQUIRE(both_static+1785856+SF_OUT_BYTES+384+2048<=SF_CAP);memcpy(sf.expected_palette,palettes[7],sizeof(colors));live_palette(palettes[7]);sf.initial_done=true;
 unsigned steady_allocations=allocation_calls,eligible=0,fallback=0;Uint8 classic[SF_N];
 for(unsigned p=0;p<8;p++){profile(p);for(unsigned page=0;page<2;page++)for(unsigned selected=0;selected<12;selected++){
  sf.active=false;frame(page,selected);memcpy(classic,VGAScreen->pixels,SF_N);uint64_t classic_trace=trace;unsigned classic_count=trace_count;sf.active=true;
  frame(page,selected);REQUIRE(!memcmp(classic,VGAScreen->pixels,SF_N)&&classic_trace==trace&&classic_count==trace_count);
  bool valid=p<4||page==1;REQUIRE(sf.frame==valid);if(valid){eligible++;render_checks();}else fallback++;
 }}
 REQUIRE(eligible==144&&fallback==48&&max_commands==2822&&allocation_calls==steady_allocations);
 profile(1);frame(0,0);
 for(unsigned edge=0;edge<7;edge++){
  const int xs[]={0,10,120,250,103,319,-5},ys[]={0,30,160,160,189,199,-7};int x=xs[edge],y=ys[edge];
  load_font_cursor_begin();REQUIRE(sf.frame);blit_sprite2x2_clip(VGAScreen,x,y,shopSpriteSheet,273);load_font_cursor_done();REQUIRE(sf.frame&&sf.cursor_quad==4);render();REQUIRE(!memcmp(sf.replay,sf.expected,SF_N));portable_checks();
  memcpy(VGAScreen->pixels,sf.pre_cursor,SF_N);load_font_cursor_erased();REQUIRE(sf.frame);render_checks();
 }
 load_font_cursor_begin();load_font_cursor_done();REQUIRE(sf.frame&&sf.cursor_quad==0);memcpy(VGAScreen->pixels,sf.pre_cursor,SF_N);load_font_cursor_erased();REQUIRE(sf.frame);
 load_font_invalidate();REQUIRE(sf.active&&!sf.frame);frame(0,0);load_font_table_reset(3);REQUIRE(sf.active);load_font_table_reset(1);REQUIRE(!sf.active);
 acquire(argv[2]);frame(0,0);load_font_fade_declare(10);load_font_fade_start(palettes[7],NULL,0,255);
 for(int step=10;step;step--){for(unsigned i=0;i<256;i++){SDL_Color c=sf.expected_palette[i],t=palettes[7][i];c.r+=(int)(t.r-c.r)/step;c.g+=(int)(t.g-c.g)/step;c.b+=(int)(t.b-c.b)/step;rgb_palette[i]=SDL_MapRGB(main_window_tex_format,c.r,c.g,c.b);}load_font_fade_step(step,0,255);REQUIRE(sf.active&&sf.frame);render_checks();}
 REQUIRE(sf.initial_done);SDL_Color black={0,0,0,255};load_font_fade_declare(15);load_font_fade_start(NULL,&black,0,255);
 for(int step=15;step;step--){for(unsigned i=0;i<256;i++){SDL_Color c=sf.expected_palette[i];c.r-=(int)c.r/step;c.g-=(int)c.g/step;c.b-=(int)c.b/step;rgb_palette[i]=SDL_MapRGB(main_window_tex_format,c.r,c.g,c.b);}load_font_fade_step(step,0,255);REQUIRE(sf.active&&sf.frame);render_checks();}REQUIRE(sf.exiting);
 resource_failures(argv[2]);observer_failures(argv[2]);renderer_lifecycle(argv[2]);
 /* Real sibling owner exclusivity: old payload/output released before new allocation. */
 settings_font_set_directory(argv[2]);settings_font_begin(VGAScreen,VGAScreen2);REQUIRE(settings_font_owns_display()&&!load_font_owns_display()&&allocated==0);load_font_begin(VGAScreen,VGAScreen2);REQUIRE(load_font_owns_display()&&!settings_font_owns_display());settings_font_begin(VGAScreen,VGAScreen2);REQUIRE(settings_font_owns_display()&&!load_font_owns_display()&&allocated==0);settings_font_end();
 load_font_end();REQUIRE(!sf.active&&!sf.output&&!sf.texture&&allocated==0);for(unsigned b=0;b<3;b++)for(unsigned id=0;id<sprite_table[b].count;id++)free(sprite(b,id)->data);free(shopSpriteSheet.data);SDL_FreeSurface(VGAScreen);SDL_FreeSurface(VGAScreen2);SDL_FreeFormat(main_window_tex_format);
 printf("PASS checks=%u source_layouts=192 eligible=%u fallback=%u total_draws=%u max_glyph_commands=%u max_with_arrows=%u max_runs=37 command_bytes=%zu load_static=%zu settings_static=%zu CPU_bound=%zu cap=%u peak_owned_alloc=%zu allocation_calls=%u\n",checks,eligible,fallback,states,max_commands-204,max_commands,sizeof(struct SfCommand),sizeof(sf),settings_font_static_bytes(),both_static+1785856+SF_OUT_BYTES+384+2048,SF_CAP,peak_allocated,allocation_calls);return 0;
}
