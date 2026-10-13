/* Source/core-only tests. Original data remains external; no game loop. */
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <limits.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>
static unsigned allocation_calls,fail_allocation=UINT_MAX;
static size_t allocated,peak_allocated;
static struct {void *p;size_t size;} allocations[4];
static void *lease_malloc(size_t n){if(allocation_calls++==fail_allocation)return NULL;void *p=malloc(n);if(p){unsigned i=0;while(i<4&&allocations[i].p)i++;if(i==4)abort();allocations[i].p=p;allocations[i].size=n;allocated+=n;if(allocated>peak_allocated)peak_allocated=allocated;}return p;}
static void lease_free(void *p){if(p){unsigned i=0;while(i<4&&allocations[i].p!=p)i++;if(i==4)abort();allocated-=allocations[i].size;allocations[i].p=NULL;free(p);}}
#define malloc lease_malloc
#define free lease_free
#include "../src/selector_font.c"
#undef malloc
#undef free
#include "../src/title_layers.h"
SDL_Surface *VGAScreen,*VGAScreenSeg,*VGAScreen2,*game_screen;
SDL_Window *main_window;SDL_PixelFormat *main_window_tex_format;
Palette palettes[24],colors;int palette_count=24;
Uint32 rgb_palette[256],yuv_palette[256];
ScalingMode scaling_mode=SCALE_INTEGER;
char episode_name[6][31],difficulty_name[7][21],gameplay_name[6][26],timed_battle_name[4][23];
JE_boolean episodeAvail[EPISODE_AVAILABLE];
static unsigned checks,states;static uint64_t trace;static unsigned trace_count;
static Uint8 raw_base[64000];
void render_mirror_pixel(SDL_Surface *s,Uint8 *p,Uint8 color,int style){(void)color;uintptr_t n=(uintptr_t)p-(uintptr_t)s->pixels;for(unsigned i=0;i<4;i++)trace=(trace^((n>>(i*8))&255))*UINT64_C(1099511628211);trace=(trace^*p)*UINT64_C(1099511628211);trace=(trace^style)*UINT64_C(1099511628211);++trace_count;selector_font_pixel(s,p,style);load_font_pixel(s,p,style);settings_font_pixel(s,p,style);}
void render_mirror_rect(SDL_Surface *s,const SDL_Rect *r){selector_font_rect(s,r);load_font_rect(s,r);settings_font_rect(s,r);}
void render_mirror_text_glyph_begin(SDL_Surface *s,int x,int y,unsigned t,unsigned id,bool black,unsigned hue,int value){(void)s;(void)x;(void)y;(void)t;(void)id;(void)black;(void)hue;(void)value;}
void render_mirror_text_glyph_end(void){}
void title_layers_pixel(SDL_Surface *s,Uint8 *p,enum TitleWriter w){(void)s;(void)p;(void)w;}
void render_mirror_unsupported(const char *s){(void)s;}
void asset_debug_effect(SDL_Surface *s,Sprite2_array a,unsigned id,int x,int y){(void)s;(void)a;(void)id;(void)x;(void)y;}
#define REQUIRE(expr) do {++checks;if(!(expr)){fprintf(stderr,"FAIL %s:%d: %s (stage=%d row=%u command=%u/%u pixel=%u active=%d frame=%d)\n",__FILE__,__LINE__,#expr,sf.stage,sf.row,sf.next,sf.limit,sf.pixel,sf.active,sf.frame);abort();}}while(0)
static unsigned rd16(FILE *f){unsigned a=fgetc(f),b=fgetc(f);return a|(b<<8);}
static unsigned rd32(FILE *f){unsigned a=rd16(f),b=rd16(f);return a|(b<<16);}
static FILE *open_data(const char *d,const char *n){char p[1024];snprintf(p,sizeof(p),"%s/%s",d,n);FILE *f=fopen(p,"rb");REQUIRE(f);return f;}
static void fixtures(const char *d)
{
 FILE *f=open_data(d,"newsh1.shp");fseek(f,0,SEEK_END);shopSpriteSheet.size=ftell(f);rewind(f);shopSpriteSheet.data=malloc(shopSpriteSheet.size);REQUIRE(fread(shopSpriteSheet.data,1,shopSpriteSheet.size,f)==shopSpriteSheet.size);fclose(f);
 f=open_data(d,"tyrian.shp");unsigned n=rd16(f),offset[32];REQUIRE(n<32);for(unsigned i=0;i<n;i++)offset[i]=rd32(f);
 for(unsigned b=0;b<3;b++){fseek(f,offset[b],SEEK_SET);sprite_table[b].count=rd16(f);for(unsigned id=0;id<sprite_table[b].count;id++){REQUIRE(fgetc(f)==1);Sprite *s=sprite(b,id);s->width=rd16(f);s->height=rd16(f);s->size=rd16(f);s->data=malloc(s->size);REQUIRE(s->data&&fread(s->data,1,s->size,f)==s->size);}}fclose(f);
 f=open_data(d,"palette.dat");for(unsigned p=0;p<24;p++)for(unsigned i=0;i<256;i++){unsigned r=fgetc(f),g=fgetc(f),b=fgetc(f);palettes[p][i]=(SDL_Color){r*4+(r>>4),g*4+(g>>4),b*4+(b>>4),255};}fclose(f);memcpy(colors,palettes[7],sizeof(colors));
 f=open_data(d,"tyrian.pic");n=rd16(f);REQUIRE(n<32);for(unsigned i=0;i<n;i++)offset[i]=rd32(f);fseek(f,offset[1],SEEK_SET);unsigned p=0;while(p<SF_N){unsigned v=fgetc(f),count=1;if((v&192)==192){count=v&63;v=fgetc(f);}REQUIRE(p+count<=SF_N);memset((Uint8 *)VGAScreen2->pixels+p,v,count);p+=count;}fclose(f);
}
static void live_palette(const SDL_Color *p){for(unsigned i=0;i<256;i++)rgb_palette[i]=SDL_MapRGB(main_window_tex_format,p[i].r,p[i].g,p[i].b);}
static void strings_fixture(const char *dir)
{
 FILE *f=open_data(dir,"tyrian.hdt");fseek(f,4,SEEK_SET);
 static const Uint8 key[]={204,129,63,255,71,19,25,62,1,99};
 for(unsigned row=0;row<=505;row++){
  int n=fgetc(f);REQUIRE(n>=0);char s[256];REQUIRE(fread(s,1,n,f)==(size_t)n);
  for(int i=n-1;i>=0;i--)s[i]^=key[i%10]^(i?s[i-1]:0);s[n]=0;
  char *out=NULL;size_t cap=0;
  if(row>=283&&row<=288){out=episode_name[row-283];cap=31;}
  if(row>=291&&row<=297){out=difficulty_name[row-291];cap=21;}
  if(row>=300&&row<=305){out=gameplay_name[row-300];cap=26;}
  if(row>=502&&row<=505){out=timed_battle_name[row-502];cap=23;}
  if(out){REQUIRE((size_t)n<cap);memcpy(out,s,n+1);}
 }
 fclose(f);
 REQUIRE(!strcmp(difficulty_name[6],"Lord of Game")); /* display label differs from enum */
}
static void run(unsigned role,unsigned row,SDL_Surface *surface,int x,int y,const char *text,unsigned bank,int align,int value)
{
 selector_font_run_begin(role,row,surface,x,y,text,bank,align,15,value);
 draw_font_hv_shadow(surface,x,y,text,bank,align,15,value,false,2);
 selector_font_run_end();
}
static void acquire(const char *dir,unsigned context)
{
 selector_font_end();memcpy(VGAScreen2->pixels,raw_base,SF_N);memset(rgb_palette,0,sizeof(rgb_palette));
 selector_font_set_directory(dir);selector_font_begin(context,VGAScreen,VGAScreen2);
 REQUIRE(sf.active&&!sf.header_done&&sf.frame);REQUIRE(sf.payload[0]&&sf.payload[1]);
 run(SELECTOR_HEADING,0,VGAScreen2,160,20,sf.text[0],large_font,centered,-3);
 REQUIRE(sf.active&&sf.header_done&&!sf.frame&&sf.header_count>0);
 REQUIRE(!memcmp(sf.cached_header,VGAScreen2->pixels,SF_N));
}
static void frame(unsigned selected,unsigned visible)
{
 memcpy(VGAScreen->pixels,VGAScreen2->pixels,SF_N);trace=SF_FNV;trace_count=0;
 selector_font_frame_begin(selected,visible);
 REQUIRE(sf.frame&&sf.count==sf.header_count);
 for(unsigned row=0;row<visible;row++){
  int x=sf.context==SELECTOR_EPISODE?20:160-JE_textWidth(sf.text[row+1],normal_font)/2;
  int y=sf.context==SELECTOR_EPISODE?50+30*row:54+24*row;
  int value=-4+(row==selected?2:0)-((sf.disabled&(1u<<row))?4:0);
  run(SELECTOR_ROW,row,VGAScreen,x,y,sf.text[row+1],normal_font,left_aligned,value);
 }
 selector_font_frame_end();REQUIRE(sf.frame&&sf.stage==S_READY);states++;
}
static int original_role(unsigned bank,unsigned id,unsigned tx,unsigned ty)
{
 const Sprite *s=sprite(bank,id);unsigned x=0,y=0;
 for(unsigned k=0;k<s->size;k++){unsigned v=s->data[k];if(v==255)x+=s->data[++k];else if(v==254)x=s->width;else if(v==253)x++;else{if(x==tx&&y==ty)return v&15;x++;}if(x==s->width){x=0;y++;}}
 return -1;
}
static Uint32 oracle(unsigned x,unsigned y)
{
 unsigned p=(y/4)*320+x/4;unsigned index=sf.base[p];Uint32 color=0;
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];if(x<c->x*4u||x>=(c->x+c->w)*4u||y<c->y*4u||y>=(c->y+c->h)*4u)continue;
  unsigned gx=x-c->x*4u,gy=y-c->y*4u;const struct SfSpec *sp=&spec[c->bank];unsigned at=((c->id/16)*sp->ch+4+gy)*sp->aw+(c->id%16)*sp->cw+4+gx;
  unsigned a=sf.payload[c->bank][at],role=sf.payload[c->bank][sp->plane+at];int tone=(int)role+c->value;if(tone<0)tone=0;if(tone>15)tone=15;
  unsigned ink=c->kind==C_DARK?(index&240)|((index&15)>>1):240u|(unsigned)tone;
  SDL_Color rgb=sf.expected_palette[ink];unsigned channels[3]={rgb.b,rgb.g,rgb.r};Uint32 next=(a+(((color>>24)*(255-a)+127)/255))<<24;
  for(unsigned i=0;i<3;i++)next|=((channels[i]*a+((color>>(8*i))&255)*(255-a)+127)/255)<<(8*i);color=next;
  int original=original_role(c->bank,c->id,gx/4,gy/4);if(original>=0){tone=original+c->value;if(tone<0)tone=0;if(tone>15)tone=15;index=c->kind==C_DARK?(index&240)|((index&15)>>1):240u|(unsigned)tone;}
 }
 return color;
}
static void render_checks(void)
{
 SDL_Rect support=render();REQUIRE(support.w>0&&support.h>0&&support.x>=0&&support.y>=0);
 REQUIRE(!memcmp(sf.replay,sf.expected,SF_N));REQUIRE(!memcmp(sf.backup_pixels,sf.cached_header,SF_N));
 for(unsigned n=0;n<1000;n++){unsigned x=(n*137+states*17)%1280,y=(n*79+states*29)%800;REQUIRE(sf.output[y*1280+x]==oracle(x,y));}
 for(unsigned p=0;p<SF_N;p++)if(!sf.owner[p]){REQUIRE(sf.replay[p]==sf.base[p]);for(unsigned dy=0;dy<4;dy++)for(unsigned dx=0;dx<4;dx++)REQUIRE(sf.output[((p/320)*4+dy)*1280+(p%320)*4+dx]==0);}
}
static void original_frame_compare(unsigned selected,unsigned visible)
{
 Uint8 expected[SF_N];memcpy(expected,sf.pixels,SF_N);uint64_t expected_trace=trace;unsigned expected_count=trace_count;
 bool active=sf.active;sf.active=false;memcpy(sf.pixels,sf.cached_header,SF_N);trace=SF_FNV;trace_count=0;
 for(unsigned row=0;row<visible;row++){
  int x=sf.context==SELECTOR_EPISODE?20:160-JE_textWidth(sf.text[row+1],normal_font)/2;
  int y=sf.context==SELECTOR_EPISODE?50+30*row:54+24*row;
  int value=-4+(row==selected?2:0)-((sf.disabled&(1u<<row))?4:0);
  draw_font_hv_shadow(VGAScreen,x,y,sf.text[row+1],normal_font,left_aligned,15,value,false,2);
 }
 sf.active=active;REQUIRE(!memcmp(expected,sf.pixels,SF_N));REQUIRE(trace==expected_trace&&trace_count==expected_count);
}
static void fade(unsigned steps,bool enter)
{
 SDL_Color black={0,0,0,255};selector_font_fade_declare(steps);selector_font_fade_start(enter?colors:NULL,enter?NULL:&black,0,255);REQUIRE(sf.active&&sf.fade_remaining==(int)steps);
 for(int left=steps;left>0;left--){
  SDL_Color palette[256];for(unsigned i=0;i<256;i++){
   SDL_Color t=enter?colors[i]:black,c=sf.expected_palette[i];c.r+=(int)(t.r-c.r)/left;c.g+=(int)(t.g-c.g)/left;c.b+=(int)(t.b-c.b)/left;palette[i]=c;
  }
  live_palette(palette);selector_font_fade_step(left,0,255);REQUIRE(sf.active&&sf.fade_remaining==left-1&&palette_matches());render_checks();
 }
 REQUIRE(sf.initial_done);
}
static void present_checks(void);
static void cursor_checks(void)
{
 const int places[][2]={{150,54},{-12,-14},{315,195},{-24,40},{100,-28}};
 for(unsigned n=0;n<sizeof(places)/sizeof(*places);n++){
  selector_font_cursor_begin();REQUIRE(sf.stage==S_CURSOR);
  blit_sprite2x2_clip(VGAScreen,places[n][0],places[n][1],shopSpriteSheet,273);
  selector_font_cursor_done();REQUIRE(sf.frame&&sf.stage==S_CURSOR_DONE);render();REQUIRE(!memcmp(sf.replay,sf.expected,SF_N));if(n==0)present_checks();
  memcpy(sf.pixels,sf.pre_cursor,SF_N);selector_font_cursor_erased();REQUIRE(sf.frame&&sf.stage==S_READY);
 }
}
static void negatives(const char *directory)
{
 acquire(directory,SELECTOR_GAMEPLAY);frame(0,5);
 Uint8 *p=sf.pixels;*p=*p;selector_font_pixel(VGAScreen,p,0);REQUIRE(!sf.frame);frame(1,5); /* same-index foreign write rejected */
 sf.backup_pixels=((Uint8 *)sf.backup_pixels);((Uint8 *)sf.backup_pixels)[0]^=1;selector_font_frame_begin(0,5);REQUIRE(!sf.active);
 acquire(directory,SELECTOR_GAMEPLAY);memcpy(sf.pixels,sf.cached_header,SF_N);selector_font_frame_begin(9,5);REQUIRE(!sf.frame);frame(0,5);
 selector_font_invalidate();REQUIRE(sf.active&&!sf.frame);frame(0,5); /* geometry invalidation reacquires */
 memcpy(sf.pixels,sf.cached_header,SF_N);selector_font_frame_begin(0,5);sf.count=SF_COMMANDS;
 selector_font_run_begin(SELECTOR_ROW,0,VGAScreen,160-JE_textWidth(sf.text[1],normal_font)/2,54,sf.text[1],normal_font,left_aligned,15,-2);REQUIRE(!sf.frame);frame(0,5);
 Uint8 saved=sprite(0,0)->data[0];sprite(0,0)->data[0]^=1;selector_font_frame_begin(0,5);REQUIRE(!sf.active);sprite(0,0)->data[0]=saved;acquire(directory,SELECTOR_GAMEPLAY);frame(0,5);
 selector_font_cursor_begin();selector_font_cursor_sprite_begin(VGAScreen,0,0,shopSpriteSheet.data,shopSpriteSheet.size,274);REQUIRE(!sf.frame);frame(0,5);
 selector_font_fade_declare(15);REQUIRE(!sf.active); /* first fade must stay10 */
 acquire(directory,SELECTOR_GAMEPLAY);frame(0,5);fade(10,true);selector_font_fade_declare(11);REQUIRE(!sf.active);
 char save=gameplay_name[1][0];gameplay_name[1][0]=(char)128;
 acquire(directory,SELECTOR_GAMEPLAY);memcpy(sf.pixels,sf.cached_header,SF_N);selector_font_frame_begin(0,5);
 selector_font_run_begin(SELECTOR_ROW,0,VGAScreen,160-JE_textWidth(sf.text[1],normal_font)/2,54,sf.text[1],normal_font,left_aligned,15,-2);REQUIRE(!sf.frame);gameplay_name[1][0]=save;
 selector_font_set_directory("/no-such-selector-pack");memcpy(VGAScreen2->pixels,raw_base,SF_N);selector_font_begin(SELECTOR_GAMEPLAY,VGAScreen,VGAScreen2);REQUIRE(!sf.active);
}
static void owner_checks(const char *directory)
{
 acquire(directory,SELECTOR_GAMEPLAY);settings_font_begin(VGAScreen,VGAScreen2);REQUIRE(!sf.active);
 settings_font_set_directory(directory);memcpy(VGAScreen2->pixels,raw_base,SF_N);memset((Uint8 *)VGAScreen2->pixels+192*320,0,8*320);memset(rgb_palette,0,sizeof(rgb_palette));
 settings_font_begin(VGAScreen,VGAScreen2);REQUIRE(settings_font_owns_display());
 memcpy(VGAScreen2->pixels,raw_base,SF_N);selector_font_set_directory(directory);selector_font_begin(SELECTOR_GAMEPLAY,VGAScreen,VGAScreen2);REQUIRE(sf.active&&!settings_font_owns_display());
 selector_font_end();load_font_set_directory(directory);memcpy(VGAScreen2->pixels,raw_base,SF_N);memset((Uint8 *)VGAScreen2->pixels+192*320,0,8*320);
 load_font_begin(VGAScreen,VGAScreen2);REQUIRE(load_font_owns_display());
 memcpy(VGAScreen2->pixels,raw_base,SF_N);selector_font_begin(SELECTOR_GAMEPLAY,VGAScreen,VGAScreen2);REQUIRE(sf.active&&!load_font_owns_display());selector_font_end();
}
static void write_file(const char *path,const void *bytes,size_t size)
{FILE *f=fopen(path,"wb");REQUIRE(f);REQUIRE(fwrite(bytes,1,size,f)==size);REQUIRE(!fclose(f));}
static void failed_acquire(const char *directory)
{
 selector_font_end();memcpy(VGAScreen2->pixels,raw_base,SF_N);selector_font_set_directory(directory);selector_font_begin(SELECTOR_GAMEPLAY,VGAScreen,VGAScreen2);
 REQUIRE(!sf.active&&!sf.output&&allocated==0);REQUIRE(!memcmp(VGAScreen2->pixels,raw_base,SF_N));
}
static void resource_checks(const char *directory)
{
 selector_font_end();char tmp[]="/tmp/selector-resources-XXXXXX";REQUIRE(mkdtemp(tmp));
 char path[2][1024];Uint8 *bytes[2];size_t size[2];
 for(unsigned b=0;b<2;b++){
  char source_path[1024];snprintf(source_path,sizeof(source_path),"%s/settings-font-%s-v1.hda",directory,spec[b].name);
  FILE *f=fopen(source_path,"rb");REQUIRE(f);size[b]=128+2*spec[b].plane;bytes[b]=malloc(size[b]+1);REQUIRE(bytes[b]);REQUIRE(fread(bytes[b],1,size[b],f)==size[b]);fclose(f);
  snprintf(path[b],sizeof(path[b]),"%s/settings-font-%s-v1.hda",tmp,spec[b].name);write_file(path[b],bytes[b],size[b]);
 }
 acquire(tmp,SELECTOR_GAMEPLAY);REQUIRE(sf.active);selector_font_end(); /* tiny is intentionally absent */
 for(unsigned b=0;b<2;b++){
  for(unsigned offset=0;offset<128;offset+=4){bytes[b][offset]^=128;write_file(path[b],bytes[b],size[b]);failed_acquire(tmp);bytes[b][offset]^=128;}
  const size_t lengths[]={0,127,size[b]-1,size[b]+1};for(unsigned i=0;i<4;i++){write_file(path[b],bytes[b],lengths[i]);failed_acquire(tmp);}
  bytes[b][128]^=1;write_file(path[b],bytes[b],size[b]);failed_acquire(tmp);bytes[b][128]^=1;
  REQUIRE(!unlink(path[b]));failed_acquire(tmp);REQUIRE(!mkdir(path[b],0700));failed_acquire(tmp);REQUIRE(!rmdir(path[b]));REQUIRE(!mkfifo(path[b],0600));failed_acquire(tmp);REQUIRE(!unlink(path[b]));write_file(path[b],bytes[b],size[b]);
 }
 for(unsigned i=0;i<3;i++){fail_allocation=allocation_calls+i;failed_acquire(tmp);fail_allocation=UINT_MAX;}
 acquire(tmp,SELECTOR_DIFFICULTY);frame(5,6);selector_font_end();REQUIRE(allocated==0);
 for(unsigned b=0;b<2;b++){free(bytes[b]);REQUIRE(!unlink(path[b]));}REQUIRE(!rmdir(tmp));
}
static void present_checks(void)
{
 const SDL_Rect dimensions[]={{0,0,640,400},{7,11,1280,736},{-13,-17,960,600}};
 for(unsigned i=0;i<3;i++){
  int w=i==0?640:i==1?1365:800,h=i==0?400:i==1?767:500;
  SDL_Surface *out=SDL_CreateRGBSurfaceWithFormat(0,w,h,32,SDL_PIXELFORMAT_ARGB8888);REQUIRE(out);
  SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(out);REQUIRE(renderer);
  SDL_Texture *reference=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_RGB888,SDL_TEXTUREACCESS_STREAMING,640,400);REQUIRE(reference);
  REQUIRE(!SDL_SetTextureBlendMode(reference,SDL_BLENDMODE_NONE));scaler=1;scalers[1].scaler32(VGAScreen,reference);
  REQUIRE(selector_font_present(renderer,reference,VGAScreen,&dimensions[i],false));REQUIRE(!memcmp(sf.pixels,sf.expected,SF_N));
  selector_font_release_texture();SDL_DestroyTexture(reference);SDL_DestroyRenderer(renderer);SDL_FreeSurface(out);
 }
}
int main(int argc,char **argv)
{
 REQUIRE(argc==3);REQUIRE(SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);REQUIRE(VGAScreen&&VGAScreen2);
 main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);REQUIRE(main_window_tex_format);
 fixtures(argv[1]);strings_fixture(argv[1]);memcpy(raw_base,VGAScreen2->pixels,SF_N);REQUIRE(hash(raw_base,SF_N)==SF_BASE);
 for(unsigned context=0;context<4;context++){
  unsigned masks=context==SELECTOR_EPISODE?32:1;
  for(unsigned mask=0;mask<masks;mask++){
   for(unsigned i=0;i<5;i++)episodeAvail[i]=(mask&(1u<<i))!=0;
   acquire(argv[2],context);
   unsigned min=context==SELECTOR_DIFFICULTY?3:row_count();
   for(unsigned visible=min;visible<=row_count();visible++)for(unsigned selected=0;selected<visible;selected++){
    frame(selected,visible);original_frame_compare(selected,visible);render_checks();
   }
  }
  for(unsigned exit_steps=10;exit_steps<=15;exit_steps+=5){acquire(argv[2],context);frame(0,context==SELECTOR_DIFFICULTY?6:row_count());fade(10,true);present_checks();cursor_checks();fade(exit_steps,false);REQUIRE(sf.active&&sf.exiting);selector_font_end();REQUIRE(!sf.active);}
 }
 negatives(argv[2]);resource_checks(argv[2]);owner_checks(argv[2]);selector_font_end();REQUIRE(allocated==0);
 for(unsigned b=0;b<3;b++)for(unsigned id=0;id<sprite_table[b].count;id++)free(sprite(b,id)->data);
 free(shopSpriteSheet.data);SDL_FreeSurface(VGAScreen);SDL_FreeSurface(VGAScreen2);SDL_FreeFormat(main_window_tex_format);SDL_Quit();
 printf("PASS selector core: %u states, %u checks; selector_static=%zu peak_owned=%zu output_static=%zu; no game runs\n",states,checks,sizeof(sf),peak_allocated,selector_font_output_static_bytes());return 0;
}
