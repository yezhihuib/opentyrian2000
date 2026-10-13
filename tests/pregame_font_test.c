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
#include "../src/pregame_font.c"
#undef malloc
#undef free
#include "../src/title_layers.h"
#include "../src/episodes.h"
#include "../src/nortvars.h"
#include "../src/vga256d.h"
SDL_Surface *VGAScreen,*VGAScreenSeg,*VGAScreen2,*game_screen;
SDL_Window *main_window;SDL_PixelFormat *main_window_tex_format;
Palette palettes[24],colors;int palette_count=24;
Uint32 rgb_palette[256],yuv_palette[256];
ScalingMode scaling_mode=SCALE_INTEGER;
char episode_name[6][31],difficulty_name[7][21],gameplay_name[6][26],timed_battle_name[4][23];
JE_boolean episodeAvail[EPISODE_AVAILABLE];
static unsigned checks,states;static uint64_t trace;static unsigned trace_count;
static Uint8 raw_base[64000];
void render_mirror_pixel(SDL_Surface *s,Uint8 *p,Uint8 color,int style){(void)color;uintptr_t n=(uintptr_t)p-(uintptr_t)s->pixels;for(unsigned i=0;i<4;i++)trace=(trace^((n>>(i*8))&255))*UINT64_C(1099511628211);trace=(trace^*p)*UINT64_C(1099511628211);trace=(trace^style)*UINT64_C(1099511628211);++trace_count;pregame_font_pixel(s,p,style);selector_font_pixel(s,p,style);load_font_pixel(s,p,style);settings_font_pixel(s,p,style);}
void render_mirror_rect(SDL_Surface *s,const SDL_Rect *r){pregame_font_rect(s,r);selector_font_rect(s,r);load_font_rect(s,r);settings_font_rect(s,r);}
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
 for(unsigned b=0;b<7;b++){if(b==3||b==4)continue;fseek(f,offset[b],SEEK_SET);sprite_table[b].count=rd16(f);for(unsigned id=0;id<sprite_table[b].count;id++){if(!fgetc(f))continue;Sprite *s=sprite(b,id);s->width=rd16(f);s->height=rd16(f);s->size=rd16(f);s->data=malloc(s->size);REQUIRE(s->data&&fread(s->data,1,s->size,f)==s->size);}}fclose(f);
 f=open_data(d,"palette.dat");for(unsigned p=0;p<24;p++)for(unsigned i=0;i<256;i++){unsigned r=fgetc(f),g=fgetc(f),b=fgetc(f);palettes[p][i]=(SDL_Color){r*4+(r>>4),g*4+(g>>4),b*4+(b>>4),255};}fclose(f);memcpy(colors,palettes[0],sizeof(colors));
 f=open_data(d,"tyrian.pic");n=rd16(f);REQUIRE(n<32);for(unsigned i=0;i<n;i++)offset[i]=rd32(f);fseek(f,offset[0],SEEK_SET);unsigned p=0;while(p<SF_N){unsigned v=fgetc(f),count=1;if((v&192)==192){count=v&63;v=fgetc(f);}REQUIRE(p+count<=SF_N);memset((Uint8 *)VGAScreen2->pixels+p,v,count);p+=count;}fclose(f);
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
  if(row>=190&&row<=226){out=mainMenuHelp[row-190];cap=66;}
  if(row>=229&&row<=235){out=menuInt[1][row-229];cap=18;}
  if(row>=238&&row<=246){out=menuInt[2][row-238];cap=18;}
  if(out){REQUIRE((size_t)n<cap);memcpy(out,s,n+1);}
 }
 fclose(f);
 FILE *items=open_data(dir,"tyrian.hdt");unsigned item_offset=rd32(items);
 /* Exact serialized field widths from episodes.c, no host-struct offsets. */
 unsigned options_offset=item_offset+14+1638*80+61*82+55*37+7*37+19*41;
 fseek(items,options_offset+86+32,SEEK_SET);REQUIRE(rd16(items)==1);
 fseek(items,options_offset+2*86+32,SEEK_SET);REQUIRE(rd16(items)==5);fseek(items,options_offset+13*86+32,SEEK_SET);REQUIRE(rd16(items)==283);fclose(items);
 REQUIRE(!strcmp(menuInt[1][0],"Game Menu")&&!strcmp(menuInt[2][8],"Done"));
}
static void acquire(const char *dir,unsigned menu,unsigned selected,unsigned cubes)
{
 memcpy(VGAScreen->pixels,raw_base,SF_N);memcpy(VGAScreen2->pixels,raw_base,SF_N);live_palette(colors);
 pregame_font_set_directory(dir);pregame_font_begin(menu,selected,menu?9:7,true,10000,cubes,VGAScreen,VGAScreen2);
 REQUIRE(sf.active&&sf.frame&&sf.next_role==PREGAME_HEADING);REQUIRE(sf.payload[0]&&sf.payload[1]&&sf.payload[2]);
}
static void run(unsigned role,unsigned row,int x,int y,const char *text,unsigned bank,unsigned hue,int value)
{
 pregame_font_run_begin(role,row,VGAScreen,x,y,text,bank,hue,value);
 if(bank==2)JE_textShade(VGAScreen,x,y,text,hue,value,DARKEN);else JE_dString(VGAScreen,x,y,text,bank);
 pregame_font_run_end();
}
static void frame(unsigned menu,unsigned selected,unsigned cubes,unsigned armor,unsigned shield)
{
 memcpy(VGAScreen->pixels,raw_base,SF_N);trace=SF_FNV;trace_count=0;
 run(PREGAME_HEADING,0,234-JE_textWidth(menuInt[menu+1][0],0)/2,10,menuInt[menu+1][0],0,15,-3);
 for(unsigned row=2;row<=(menu?9u:7u);row++){
  char text[20];snprintf(text,sizeof(text),"%s%s",row==selected?"~":"",menuInt[menu+1][row-1]);
  run(PREGAME_ROW,row,166,38+(row-2)*16+(!menu&&row==7?16:0),text,1,15,-3);
 }
 if(!menu){
  pregame_font_phase_begin(PREGAME_CUBES,0,0);
  for(unsigned i=1;i<=cubes;i++){blit_sprite_dark(VGAScreen,190+i*18+2,38,5,34,false);blit_sprite(VGAScreen,190+i*18,37,5,34);}
  pregame_font_phase_end();
 }
 run(PREGAME_CASH,0,65,173,"10000",2,1,6);
 pregame_font_phase_begin(PREGAME_BARS,armor,shield);
 JE_barDrawShadow(VGAScreen,42,152,3,14,armor,2,13);JE_barDrawShadow(VGAScreen,104,152,2,14,shield,2,13);
 pregame_font_phase_end();
 pregame_font_phase_begin(PREGAME_SHIP,0,0);
 blit_sprite(VGAScreen,31,36,5,27);blit_sprite(VGAScreen,62,84,6,16);blit_sprite(VGAScreen,61,48,6,0);blit_sprite(VGAScreen,41,92,6,9);
 /* Episode1 option1/2 itemgraphic1/5, independently decoded in fixtures. */
 blit_sprite2x2(VGAScreen,3,84,shopSpriteSheet,1);blit_sprite2x2(VGAScreen,129,84,shopSpriteSheet,selected==9?283:5);
 blit_sprite_hv(VGAScreen,28,23,5,26,15,(int)shield/2-10);
 pregame_font_phase_end();
 run(PREGAME_FOOTER,selected,10,187,mainMenuHelp[menuHelp[menu][selected-2]-1],2,14,1);
 pregame_font_frame_end();
}
static void frame_checks(const char *dir,unsigned menu,unsigned selected,unsigned cubes,unsigned armor,unsigned shield)
{
 acquire(dir,menu,selected,cubes);frame(menu,selected,cubes,armor,shield);
 REQUIRE(sf.active&&sf.frame&&sf.stage==S_READY);REQUIRE(sf.run_count==(menu?11u:9u));
 Uint8 expected[SF_N];memcpy(expected,sf.pixels,SF_N);uint64_t wanted=trace;unsigned count=trace_count;
 sf.active=false;frame(menu,selected,cubes,armor,shield);sf.active=true;
 REQUIRE(!memcmp(expected,sf.pixels,SF_N)&&trace==wanted&&trace_count==count);REQUIRE(exact());++states;
}
static int original_role(unsigned bank,unsigned id,unsigned tx,unsigned ty)
{
 const Sprite *s=sprite(bank,id);unsigned x=0,y=0;
 for(unsigned k=0;k<s->size;k++){unsigned v=s->data[k];if(v==255)x+=s->data[++k];else if(v==254)x=s->width;else if(v==253)x++;else{if(x==tx&&y==ty)return v&15;x++;}if(x==s->width){x=0;y++;}}
 return -1;
}
/* Independent per-sample ordered replay, including opaque same-index writes. */
static Uint32 oracle(unsigned x,unsigned y)
{
 unsigned p=(y/4)*320+x/4,index=sf.base[p];Uint32 color=0;
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];
  if(c->kind==C_CLASSIC){for(unsigned i=c->first;i<c->first+c->events;i++)if(sf.events[i].position==p){index=sf.events[i].index;color=0;}continue;}
  if(x<c->x*4u||x>=(c->x+c->w)*4u||y<c->y*4u||y>=(c->y+c->h)*4u)continue;
  unsigned gx=x-c->x*4u,gy=y-c->y*4u;const struct SfSpec *sp=&spec[c->bank];unsigned at=((c->id/16)*sp->ch+4+gy)*sp->aw+(c->id%16)*sp->cw+4+gx;
  unsigned a=sf.payload[c->bank][at],role=c->bank==2?7:sf.payload[c->bank][sp->plane+at];
  Uint8 ink=c->kind==C_DARK?(index&240)|((index&15)>>1):(Uint8)((c->hue<<4)|((int)role+c->value));
  SDL_Color rgb=sf.expected_palette[ink];unsigned channels[3]={rgb.b,rgb.g,rgb.r};Uint32 next=(a+(((color>>24)*(255-a)+127)/255))<<24;
  for(unsigned i=0;i<3;i++)next|=((channels[i]*a+((color>>(8*i))&255)*(255-a)+127)/255)<<(8*i);color=next;
  int original=original_role(c->bank,c->id,gx/4,gy/4);if(original>=0)index=c->kind==C_DARK?(index&240)|((index&15)>>1):(Uint8)((c->hue<<4)|(original+c->value));
 }
 return color;
}
static void render_checks(void)
{
 SDL_Rect support=render();REQUIRE(support.x>=0&&support.y>=0&&support.w>0&&support.h>0);REQUIRE(!memcmp(sf.replay,sf.expected,SF_N));
 for(unsigned k=0;k<200;k++){unsigned x=(k*71+states*11)%1280,y=(k*53+states*17)%800;REQUIRE(sf.output[y*1280+x]==oracle(x,y));}
 /* Inspect every canonical glyph point on a deterministic sparse grid. */
 for(unsigned k=0;k<sf.count;k++)if(sf.commands[k].kind!=C_CLASSIC){const struct SfCommand *c=&sf.commands[k];unsigned x=c->x*4+c->w*2,y=c->y*4+c->h*2;REQUIRE(sf.output[y*1280+x]==oracle(x,y));}
 for(unsigned p=0;p<SF_N;p++)if(!sf.owner[p]){REQUIRE(sf.underlay[p]==sf.expected[p]);REQUIRE(sf.output[(p/320)*4*1280+(p%320)*4]==0);}
}
static void cursor_checks(void)
{
 const int xy[][2]={{0,0},{208,38},{166,65},{66,174},{11,188},{309,188}};
 for(unsigned n=0;n<sizeof(xy)/sizeof(*xy);n++){
  Uint8 before[SF_N];memcpy(before,sf.pixels,SF_N);unsigned count=sf.count,events=sf.event_count;
  pregame_font_cursor_begin();blit_sprite2x2_clip(VGAScreen,xy[n][0],xy[n][1],shopSpriteSheet,273);pregame_font_cursor_done();
  REQUIRE(sf.frame&&sf.stage==S_CURSOR_DONE);render();REQUIRE(!memcmp(sf.replay,sf.expected,SF_N));
  memcpy(sf.pixels,before,SF_N);pregame_font_cursor_erased();REQUIRE(sf.frame&&sf.stage==S_READY&&sf.count==count&&sf.event_count==events);
 }
 for(unsigned n=0;n<16;n++){unsigned count=sf.count,events=sf.event_count;pregame_font_cursor_begin();pregame_font_cursor_done();pregame_font_cursor_erased();REQUIRE(sf.frame&&sf.count==count&&sf.event_count==events);}
}
static void present_checks(void)
{
 const SDL_Rect dimensions[]={{0,0,640,400},{0,0,1280,800},{70,0,1225,767},{7,11,913,599}};
 for(unsigned i=0;i<sizeof(dimensions)/sizeof(*dimensions);i++){
  SDL_Surface *out=SDL_CreateRGBSurfaceWithFormat(0,dimensions[i].x*2+dimensions[i].w,dimensions[i].y*2+dimensions[i].h,32,SDL_PIXELFORMAT_RGB888);REQUIRE(out);
  SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(out);REQUIRE(renderer);
  SDL_Texture *reference=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_RGB888,SDL_TEXTUREACCESS_STREAMING,640,400);REQUIRE(reference);
  REQUIRE(!SDL_SetTextureBlendMode(reference,SDL_BLENDMODE_NONE));scaler=1;scalers[1].scaler32(VGAScreen,reference);
  REQUIRE(pregame_font_present(renderer,reference,VGAScreen,&dimensions[i],false));REQUIRE(!memcmp(sf.pixels,sf.expected,SF_N));
  pregame_font_release_texture();SDL_DestroyTexture(reference);SDL_DestroyRenderer(renderer);SDL_FreeSurface(out);
 }
}
static void fades(const char *dir)
{
 frame_checks(dir,0,4,4,15,10);pregame_font_fade_declare(10);SDL_Color black={0,0,0,255};pregame_font_fade_start(NULL,&black,0,255);REQUIRE(sf.active&&sf.exiting);
 for(int n=10;n;n--){SDL_Color pal[256];memcpy(pal,sf.expected_palette,sizeof(pal));for(unsigned i=0;i<256;i++){pal[i].r+=(0-pal[i].r)/n;pal[i].g+=(0-pal[i].g)/n;pal[i].b+=(0-pal[i].b)/n;}live_palette(pal);pregame_font_fade_step(n,0,255);REQUIRE(sf.active&&sf.fade_remaining==n-1);render_checks();}
 pregame_font_end();memcpy(VGAScreen->pixels,raw_base,SF_N);pregame_font_begin(0,4,7,true,10000,4,VGAScreen,VGAScreen2);REQUIRE(sf.active);frame(0,4,4,15,10);
 pregame_font_fade_declare(10);pregame_font_fade_start(colors,NULL,0,255);
 for(int n=10;n;n--){SDL_Color pal[256];memcpy(pal,sf.expected_palette,sizeof(pal));for(unsigned i=0;i<256;i++){pal[i].r+=(colors[i].r-pal[i].r)/n;pal[i].g+=(colors[i].g-pal[i].g)/n;pal[i].b+=(colors[i].b-pal[i].b)/n;}live_palette(pal);pregame_font_fade_step(n,0,255);REQUIRE(sf.active&&sf.fade_remaining==n-1);}
 REQUIRE(!sf.exiting);present_checks();pregame_font_fade_declare(15);REQUIRE(!sf.active);
}
static void write_bytes(const char *path,const Uint8 *p,size_t n)
{FILE *f=fopen(path,"wb");REQUIRE(f);REQUIRE(fwrite(p,1,n,f)==n);REQUIRE(!fclose(f));}
static void failed_acquire(const char *d)
{
 Uint8 before[SF_N];memcpy(VGAScreen->pixels,raw_base,SF_N);memcpy(before,VGAScreen->pixels,SF_N);pregame_font_set_directory(d);memcpy(VGAScreen->pixels,raw_base,SF_N);pregame_font_begin(0,2,7,true,10000,4,VGAScreen,VGAScreen2);REQUIRE(!sf.active&&!sf.output&&allocated==0);REQUIRE(!memcmp(before,VGAScreen->pixels,SF_N));
}
static void resource_failures(const char *d)
{
 char temp[]="/tmp/settings-font-test-XXXXXX";REQUIRE(mkdtemp(temp));char paths[3][1024];Uint8 *files[3];size_t sizes[3];
 pregame_font_end();
 for(unsigned b=0;b<3;b++){char in[1024];snprintf(in,sizeof(in),"%s/settings-font-%s-v1.hda",d,spec[b].name);FILE *f=fopen(in,"rb");REQUIRE(f);sizes[b]=128+spec[b].plane*(spec[b].mode?2:1);files[b]=malloc(sizes[b]+1);REQUIRE(files[b]&&fread(files[b],1,sizes[b],f)==sizes[b]);fclose(f);snprintf(paths[b],sizeof(paths[b]),"%s/settings-font-%s-v1.hda",temp,spec[b].name);write_bytes(paths[b],files[b],sizes[b]);}
 for(unsigned b=0;b<3;b++){
  for(unsigned offset=0;offset<128;offset+=4){files[b][offset]^=128;write_bytes(paths[b],files[b],sizes[b]);failed_acquire(temp);files[b][offset]^=128;}
  const size_t lengths[]={0,127,sizes[b]-1,sizes[b]+1};for(unsigned i=0;i<4;i++){write_bytes(paths[b],files[b],lengths[i]);failed_acquire(temp);}
  files[b][128]^=1;write_bytes(paths[b],files[b],sizes[b]);failed_acquire(temp);files[b][128]^=1;
  REQUIRE(!unlink(paths[b]));failed_acquire(temp);REQUIRE(!mkdir(paths[b],0700));failed_acquire(temp);REQUIRE(!rmdir(paths[b]));REQUIRE(!mkfifo(paths[b],0600));failed_acquire(temp);REQUIRE(!unlink(paths[b]));write_bytes(paths[b],files[b],sizes[b]);
 }
 for(unsigned i=0;i<4;i++){pregame_font_end();fail_allocation=allocation_calls+i;pregame_font_set_directory(temp);memcpy(VGAScreen->pixels,raw_base,SF_N);pregame_font_begin(0,2,7,true,10000,4,VGAScreen,VGAScreen2);REQUIRE(!sf.active&&allocated==0);fail_allocation=UINT_MAX;}
 acquire(temp,0,2,4);for(unsigned b=0;b<3;b++){
  Uint8 *p=sf.payload[b];Uint8 old=p[0];p[0]=255;REQUIRE(!padding(b,p));p[0]=old;
  if(spec[b].mode){p[spec[b].plane]=12;REQUIRE(!padding(b,p));p[spec[b].plane]=0;unsigned ink=0;while(!p[ink])ink++;old=p[spec[b].plane+ink];p[spec[b].plane+ink]=11;REQUIRE(!padding(b,p));p[spec[b].plane+ink]=old;}
  REQUIRE(padding(b,p));
 }
 pregame_font_end();for(unsigned b=0;b<3;b++){REQUIRE(!unlink(paths[b]));free(files[b]);}REQUIRE(!rmdir(temp));
}
static void occlusion_checks(const char *dir)
{
 char saved[18];memcpy(saved,menuInt[1][1],18);strcpy(menuInt[1][1],"Data Data Data");
 frame_checks(dir,0,2,4,15,10);unsigned count=sf.count,overlap=0,same=0;
 for(unsigned k=0;k<count;k++)if(sf.commands[k].kind==C_CLASSIC){
  sf.count=k;render();const struct SfCommand *c=&sf.commands[k];
  for(unsigned i=c->first;i<c->first+c->events;i++){
   unsigned p=sf.events[i].position;bool authored=false;
   for(unsigned yy=0;yy<4;yy++)for(unsigned xx=0;xx<4;xx++)authored|=sf.output[((p/320)*4+yy)*1280+(p%320)*4+xx]!=0;
   if(!authored)continue;++overlap;if(sf.replay[p]==sf.events[i].index)++same;
   /* Replaying this actual original operation removes all 16 authored samples. */
   sf.count=k+1;render();for(unsigned yy=0;yy<4;yy++)for(unsigned xx=0;xx<4;xx++)REQUIRE(!sf.output[((p/320)*4+yy)*1280+(p%320)*4+xx]);sf.count=k;render();
  }
 }
 sf.count=count;REQUIRE(overlap>0);render_checks();
 /* A private primitive fixture explicitly repeats an existing index at an
  * authored sample. It does not assert that natural cube art has this color. */
 render();unsigned p=0;while(p<SF_N&&!sf.output[(p/320)*4*1280+(p%320)*4])p++;
 REQUIRE(p<SF_N);Uint8 index=sf.expected[p];struct SfCommand *c=append(C_CLASSIC,0,0,0,0,0,0);REQUIRE(c);
 REQUIRE(event(p%320,p/320,index,0));c->events=1;sf.event_next=c->first;sf.event_limit=sf.event_count;sf.stage=S_PRIMITIVE;sf.phase=PREGAME_SHIP;sf.primitive=true;
 ((Uint8 *)sf.pixels)[p]=index;pregame_font_pixel(VGAScreen,(Uint8 *)sf.pixels+p,0);REQUIRE(sf.frame&&sf.event_next==sf.event_limit&&sf.expected[p]==index);
 sf.primitive=false;sf.stage=S_READY;sf.next=sf.count;render();
 for(unsigned yy=0;yy<4;yy++)for(unsigned xx=0;xx<4;xx++)REQUIRE(!sf.output[((p/320)*4+yy)*1280+(p%320)*4+xx]);
 REQUIRE(sf.underlay[p]==index);(void)same;memcpy(menuInt[1][1],saved,18);pregame_font_end();
}
static void negatives(const char *dir)
{
 memcpy(VGAScreen->pixels,raw_base,SF_N);pregame_font_set_directory(dir);live_palette(colors);rgb_palette[0]^=1;
 pregame_font_begin(0,2,7,true,10000,4,VGAScreen,VGAScreen2);REQUIRE(!sf.active&&!allocated);live_palette(colors);
 for(unsigned menu=2;menu<15;menu++){memcpy(VGAScreen->pixels,raw_base,SF_N);pregame_font_begin(menu,2,7,true,10000,4,VGAScreen,VGAScreen2);REQUIRE(!sf.active);}
 for(unsigned selected=0;selected<11;selected++)if(selected<2||selected>7){pregame_font_begin(0,selected,7,true,10000,4,VGAScreen,VGAScreen2);REQUIRE(!sf.active);}
 pregame_font_begin(0,2,7,false,10000,4,VGAScreen,VGAScreen2);REQUIRE(!sf.active);
 acquire(dir,0,2,4);run(PREGAME_HEADING,0,234-JE_textWidth(menuInt[1][0],0)/2,11,menuInt[1][0],0,15,-3);REQUIRE(!sf.frame);
 acquire(dir,0,2,4);run(PREGAME_HEADING,0,234-JE_textWidth(menuInt[1][0],0)/2,10,"Wrong",0,15,-3);REQUIRE(!sf.frame);
 acquire(dir,0,2,4);pregame_font_run_begin(PREGAME_HEADING,0,VGAScreen,234-JE_textWidth(menuInt[1][0],0)/2,10,menuInt[1][0],0,15,-3);struct SfCommand c=sf.commands[sf.next];pregame_font_glyph_begin(VGAScreen,c.x,c.y,c.bank,c.id,PREGAME_FACE,15,-3);REQUIRE(!sf.frame);
 frame_checks(dir,1,9,4,16,11);pregame_font_pixel(VGAScreen,sf.pixels,0);REQUIRE(!sf.frame); /* same-index unknown writer */
 frame_checks(dir,0,4,4,15,10);((Uint8 *)sf.pixels)[100]^=1;pregame_font_cursor_begin();REQUIRE(!sf.frame);
 frame_checks(dir,0,4,4,15,10);pregame_font_cursor_begin();pregame_font_pixel(VGAScreen,sf.pixels,0);REQUIRE(!sf.frame);
 acquire(dir,0,2,4);char saved=menuInt[1][0][0];menuInt[1][0][0]^=1;REQUIRE(!exact()&&!sf.active);menuInt[1][0][0]=saved;
 acquire(dir,0,2,4);Uint8 v=sprite(5,34)->data[0];sprite(5,34)->data[0]^=1;REQUIRE(!exact()&&!sf.active);sprite(5,34)->data[0]=v;
 acquire(dir,0,2,4);v=palettes[0][12].r;palettes[0][12].r^=1;REQUIRE(!exact()&&!sf.active);palettes[0][12].r=v;
 acquire(dir,0,2,4);v=((Uint8 *)sf.backup_pixels)[22];((Uint8 *)sf.backup_pixels)[22]^=1;REQUIRE(!exact()&&!sf.active);((Uint8 *)VGAScreen2->pixels)[22]=v;
 acquire(dir,0,2,4);pregame_font_table_reset(5);REQUIRE(!sf.active);
 frame_checks(dir,0,4,4,15,10);SDL_Rect dst={0,0,640,400};REQUIRE(!pregame_font_present(NULL,NULL,VGAScreen,&dst,true));REQUIRE(!sf.frame);
 saved=menuInt[1][2][0];menuInt[1][2][0]=(char)255;acquire(dir,0,3,4);frame(0,3,4,15,10);REQUIRE(!sf.frame);menuInt[1][2][0]=saved;
 frame_checks(dir,0,3,4,15,10); /* clean next PIC1 acquisition after fallback */
 /* Unsafe arithmetic is deliberately neither saturated nor RGB-halved. */
 REQUIRE(face(0,15,-3)==253&&face(15,1,6)==21&&shade(239)==231);
}
int main(int argc,char **argv)
{
 REQUIRE(argc==3);REQUIRE(SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);REQUIRE(VGAScreen&&VGAScreen2);
 main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);REQUIRE(main_window_tex_format);
 fixtures(argv[1]);strings_fixture(argv[1]);memcpy(raw_base,VGAScreen2->pixels,SF_N);REQUIRE(hash(raw_base,SF_N)==PF_BASE);REQUIRE(classic_sources());
 for(unsigned menu=0;menu<2;menu++)for(unsigned selected=2;selected<=(menu?9u:7u);selected++)for(unsigned cubes=0;cubes<=4;cubes++){
  frame_checks(argv[2],menu,selected,cubes,15+cubes,10+cubes);render_checks();
 }
 frame_checks(argv[2],0,4,4,15,10);cursor_checks();present_checks();fades(argv[2]);occlusion_checks(argv[2]);negatives(argv[2]);resource_failures(argv[2]);pregame_font_end();REQUIRE(!allocated);
 for(unsigned b=0;b<7;b++)for(unsigned id=0;id<sprite_table[b].count;id++)free(sprite(b,id)->data);
 free(shopSpriteSheet.data);SDL_FreeSurface(VGAScreen);SDL_FreeSurface(VGAScreen2);SDL_FreeFormat(main_window_tex_format);SDL_Quit();
 printf("PASS pregame core: %u states, %u checks; static=%zu peak_owned=%zu output_static=%zu; no game runs\n",states,checks,sizeof(sf),peak_allocated,selector_font_output_static_bytes());return 0;
}
