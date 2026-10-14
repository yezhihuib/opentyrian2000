/* Finite extracted-production data513 proof; no game entry point. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <ctype.h>
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef struct {int unused;} G101Record,PCapRecord,Forest13Record;
typedef enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW} EntityDrawStyle;
typedef enum {ENTITY_TILE,ENTITY_QUAD} EntityDrawLayout;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#include "types.inc"
static bool xmas,active=true,suppress,suppress_green_smoke,suppress_cloud,game_probe_missing,game_probe_invalid,game_probe_original_reference,game_probe_local_blend;
static const char *game_probe_assets,*reject_reason,*full_pack,*legacy_pack;
static int game_probe_density=8,game_probe_scene_assets=3,game_probe_tick;
static SDL_PixelFormat format={8,1};
static SDL_Surface screen={320,200,320,NULL,&format},display,*game_screen=&screen,*VGAScreen=&screen,*canvas=&display;
static Sprite2_array spriteSheet11,spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet,enemySpriteSheets[4];static int enemySpriteSheetIds[4];
static Uint32 rgb_palette[256];static Uint8 selected[64000],*hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;static Uint32 *green_under;
typedef struct {Asset *asset;int x,y;} GreenHead;static GreenHead green_heads[256];
typedef struct {Uint16 peak[16][14];} GreenBackground;
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;static HdRegion regions[256];
static unsigned green_head_count,region_count,draws,occlusions,local_entities;
static TalonBank talon_banks[2];static unsigned banking_draw_player;static uint64_t mirror_logic_tick;
static const int original_visual_indices[5]={0,2,6,10,12};
static unsigned original_calls,scene_calls,font_calls;static unsigned log_id;static int log_role;static bool log_mirrored;
static uint64_t checks,pixels,transactions;static bool bounded;
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL line%d: %s\n",__LINE__,#x);exit(3);}checks++;}while(0)
#define ground101_select(...) assert(0)
#define plateau_cap_select(...) assert(0)
#define forest13_select(...) assert(0)
#define ground101_enemy_eligible(...) false
#define ground101_record(...) NULL
#define ground101_actor_trace(...) ((void)0)
#define ground101_note_draw(...) ((void)0)
#define load_font_arrow_sprite_begin(...) ((void)0)
#define load_font_arrow_sprite_end(...) ((void)0)
#define pregame_font_sprite2_begin(...) ((void)0)
#define pregame_font_sprite2_end(...) ((void)0)
static void font_before_effect(SDL_Rect r){(void)r;font_calls++;}
static void restore_classic_rect(SDL_Rect r){(void)r;assert(0);}
static void render_mirror_unsupported(const char*s){fprintf(stderr,"Unexpected rejection: %s\n",s);abort();}
static Uint16 SDL_SwapLE16(Uint16 v){Uint8 b[2];memcpy(b,&v,2);return (Uint16)(b[0]|(unsigned)b[1]<<8);}
typedef struct {unsigned type,pool_slot,availability,size;bool score_item,damaged,independent_motion,static_animation;} G101EnemyContext;
static void game_probe_scene_draw(int r,unsigned id,int x,int y,int part,int style,bool mirrored){(void)x;(void)y;(void)part;(void)style;scene_calls++;log_role=r;log_id=id;log_mirrored=mirrored;}
/* Old, unrelated composite families are unreachable in these selected tests. */
#define type3_small_family_ready() (assert(0),false)
#define type15_eightheading_family_ready() (assert(0),false)
#define late_spike_family_ready() (assert(0),false)
#define linked31_family_ready() (assert(0),false)
#define newsh4_long7_family_ready() (assert(0),false)
#define newsh4_opposite7_family_ready() (assert(0),false)
#define boss_whole_family_ready() (assert(0),false)
#define newsh4_entry6_family_ready() (assert(0),false)
static bool boss_whole_base_allowed(const G101EnemyContext*c,unsigned b){(void)c;(void)b;return false;}
/* New resources resolve only against the selected tiny candidate/negative pack.
 * Prior resources resolve directly to their hash-verified immutable main pack. */
static FILE *asset_fopen(const char *p,const char *m){const char*n=strrchr(p,'/');n=n?n+1:p;if(!strncmp(n,"data513-",8))return fopen(p,m);char q[2048];CHECK(snprintf(q,sizeof(q),"%s/%s",legacy_pack,n)<(int)sizeof(q));return fopen(q,m);}
#define fopen asset_fopen
#include "functions.inc"
#undef fopen
static void asset_debug_effect(SDL_Surface*s,Sprite2_array b,unsigned id,int x,int y){(void)s;(void)b;(void)id;(void)x;(void)y;original_calls++;}
static void render_mirror_pixel(SDL_Surface*s,Uint8*p,Uint8 v,int style){(void)s;(void)p;(void)v;(void)style;}
#include "blitters.inc"
static bool asset_debug_enabled;static char shapeFile[256];
#define asset_debug_reference(...) ((void)0)
static struct {Sprite2_array*sprite2s;int ex,ey,egr[20],enemycycle,filter,enemytype,size,scoreitem,edamaged,exc,eyc,fixedmovey,excc,eycc,xaccel,yaccel,ani,aniactive;} enemy[1];static int enemyAvail[1],tempMapXOfs;
#include "wrapper.inc"
static const unsigned ids[12]={159,161,163,197,199,201,235,237,239,273,275,277};static const int parts[4]={0,1,19,20};static Uint8 refs[48][336];
static void clear_assets(void){for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);memset(assets+i,0,sizeof(*assets));}data513_checked=data513_valid=false;cash25_checked=cash25_valid=cash75_checked=cash75_valid=cash50_checked=cash50_valid=gem100_checked=gem100_valid=gem250_checked=gem250_valid=enemy_energy_checked=enemy_energy_valid=enemy_tank_shell_checked=enemy_tank_shell_valid=false;}
static Uint32 bg(int n){return 0xff000000u|((n*2654435761u+0x594123u)&0xffffffu);}
static void start(void){int d=8;canvas->w=320*d;canvas->h=200*d;canvas->pitch=canvas->w*4;size_t n=canvas->w*canvas->h;canvas->pixels=calloc(n,4);hd_owner=calloc(n,1);cloud_owner=calloc(n,1);green_first=calloc(n,2);green_under=calloc(n,4);green_under_owner=calloc(n,1);screen.pixels=calloc(64000,1);CHECK(canvas->pixels&&hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner&&screen.pixels);}
static void reset_area(int x,int y){region_count=draws=green_head_count=0;reject_reason=NULL;render_mirror_entity_end();for(int py=0;py<224;py++)for(int px=0;px<192;px++){int dx=x*8+px,dy=y*8+py;if(dx<0||dx>=canvas->w||dy<0||dy>=canvas->h)continue;int n=dy*canvas->w+dx;((Uint32*)canvas->pixels)[n]=bg(n);hd_owner[n]=1;cloud_owner[n]=1;green_first[n]=7;}}
static Uint32 alpha_oracle(Uint32 dst,const Uint8*s){Uint32 out=0xff000000u;for(int c=0;c<3;c++){int sh=16-8*c;unsigned n=((dst>>sh)&255)*(255-s[3])+s[c]*s[3];out|=(n/255+(n%255>=128))<<sh;}return out;}
static void filter_oracle(const Uint8*s,int f,Uint8*out){memcpy(out,s,4);if(!f)return;unsigned peak=MAX(s[0],MAX(s[1],s[2])),value=(peak*15*256+127)/255,lo=value/256,hi=MIN(15,lo+1),v=value%256;for(int c=0;c<3;c++){int sh=16-8*c;out[c]=((((rgb_palette[f|lo]>>sh)&255)*(256-v)+((rgb_palette[f|hi]>>sh)&255)*v+128)/256);}}
static void check_pixels(const Asset*a,int x,int y,int part,int f){int ox=(part==1||part==20)?96:0,oy=(part==19||part==20)?112:0;for(int py=0;py<224;py++)for(int px=0;px<192;px++){if(bounded&&f%16&&px%23&&py%29)continue;int dx=x*8+px,dy=y*8+py;if(dx<0||dx>=canvas->w||dy<0||dy>=canvas->h)continue;int n=dy*canvas->w+dx;const Uint8*s=a->rgba+4*(py*192+px);bool hit=px>=ox&&px<ox+96&&py>=oy&&py<oy+112&&s[3];Uint8 rgba[4];filter_oracle(s,f,rgba);CHECK(((Uint32*)canvas->pixels)[n]==(hit?alpha_oracle(bg(n),rgba):bg(n)));CHECK(hd_owner[n]==1);CHECK(cloud_owner[n]==(hit?0:1));CHECK(green_first[n]==(hit?0:7));pixels++;}}
static void isolation(void){G101EnemyContext c={513,0,2,1,true,false,true,false};CHECK(cash25_family_ready()&&cash75_family_ready()&&cash50_family_ready()&&gem100_family_ready()&&gem250_family_ready()&&enemy_energy_family_ready()&&enemy_tank_shell_family_ready());
 for(unsigned k=0;k<3;k++){unsigned base=235+2*k;reset_area(98,100);CHECK(render_mirror_enemy_tile(&screen,98,100,enemySpriteSheets[0],base,0,0,&c));CHECK(log_role==101&&log_id==base&&log_mirrored);Asset*a=&assets[213+k];CHECK(a->valid&&a->bank==101&&a->index==(int)base);render_mirror_entity_end();}
 for(unsigned k=0;k<12;k++)for(unsigned p=0;p<4;p++){reset_area(98,100);CHECK(render_mirror_enemy_tile(&screen,98,100,spriteSheet11,ids[k],parts[p],0,&c)==data513_valid);CHECK(log_role==124&&log_id==ids[k]&&log_mirrored==data513_valid);render_mirror_entity_end();}
 CHECK(!get_asset(explosionSpriteSheet,266,ENTITY_TILE));
 for(unsigned p=0;p<4;p++){c.type=512;reset_area(98,100);unsigned before=draws;CHECK(!render_mirror_enemy_tile(&screen,98,100,spriteSheet11,273,parts[p],0,&c));CHECK(draws==before&&!suppress&&log_role==124&&!log_mirrored);render_mirror_entity_end();}c.type=513;
 for(unsigned i=507;i<510;i++)CHECK(!assets[i].initialized);
}
static void guards(void){G101EnemyContext c={513,0,2,1,true,false,true,false};Sprite2_array wrong={(Uint8*)&c,1},null={NULL,0};SDL_Surface other=screen;unsigned saved=draws;
 for(unsigned id=0;id<500;id++)if(data513_base_slot(id)<0)CHECK(!data513_pickup(&screen,98,100,spriteSheet11,id,0,0,&c));
 for(unsigned id=0;id<1701;id++)if(id!=513){c.type=id;CHECK(!data513_pickup(&screen,98,100,spriteSheet11,159,0,0,&c));}c.type=513;
 for(int p=-5;p<25;p++)if(p!=0&&p!=1&&p!=19&&p!=20)CHECK(!data513_pickup(&screen,98,100,spriteSheet11,159,p,0,&c));
 CHECK(!data513_pickup(&screen,98,100,wrong,159,0,0,&c));CHECK(!data513_pickup(&screen,98,100,null,159,0,0,&c));Sprite2_array savedbank=spriteSheet11;spriteSheet11=null;CHECK(!data513_pickup(&screen,98,100,null,159,0,0,&c));CHECK(!render_mirror_enemy_tile(&screen,98,100,null,159,0,0,&c));spriteSheet11=savedbank;CHECK(!data513_pickup(&screen,98,100,spriteSheet11,159,0,0,NULL));c.size=0;CHECK(!data513_pickup(&screen,98,100,spriteSheet11,159,0,0,&c));c.size=2;CHECK(!data513_pickup(&screen,98,100,spriteSheet11,159,0,0,&c));c.size=1;
 CHECK(!data513_pickup(NULL,98,100,spriteSheet11,159,0,0,&c));CHECK(!data513_pickup(&other,98,100,spriteSheet11,159,0,0,&c));active=false;CHECK(!data513_pickup(&screen,98,100,spriteSheet11,159,0,0,&c));active=true;reject_reason="guard";CHECK(!data513_pickup(&screen,98,100,spriteSheet11,159,0,0,&c));reject_reason=NULL;
 const int xy[][2]={{-1,0},{309,0},{0,-14},{0,200},{INT_MIN,INT_MAX},{INT_MAX,INT_MIN}};for(unsigned i=0;i<6;i++)for(unsigned p=0;p<4;p++)CHECK(!data513_pickup(&screen,xy[i][0],xy[i][1],spriteSheet11,159,parts[p],0,&c));
 for(int mode=0;mode<8;mode++){SDL_Surface old=screen;SDL_Surface*vg=VGAScreen;if(mode==0)screen.w=319;if(mode==1)screen.h=199;if(mode==2)screen.pitch=328;if(mode==3)screen.format=NULL;if(mode==4)format.BitsPerPixel=32;if(mode==5)format.BytesPerPixel=4;if(mode==6)VGAScreen=&other;if(mode==7)VGAScreen=NULL;CHECK(!data513_pickup(&screen,98,100,spriteSheet11,159,0,0,&c));screen=old;format.BitsPerPixel=8;format.BytesPerPixel=1;VGAScreen=vg;}
 for(int mode=0;mode<6;mode++){game_probe_density=mode==0?1:mode==1?4:8;game_probe_missing=mode==2;game_probe_invalid=mode==3;game_probe_original_reference=mode==4;game_probe_assets=mode==5?NULL:full_pack;CHECK(!data513_pickup(&screen,98,100,spriteSheet11,159,0,0,&c));}game_probe_density=8;game_probe_missing=game_probe_invalid=game_probe_original_reference=false;game_probe_assets=full_pack;CHECK(draws==saved);
 game_probe_scene_assets=0;CHECK(!render_mirror_enemy_tile(&screen,98,100,spriteSheet11,159,0,0,&c));game_probe_scene_assets=3;
}
static void *read_file(const char*p,size_t*n){FILE*f=fopen(p,"rb");CHECK(f&&!fseek(f,0,SEEK_END));long s=ftell(f);CHECK(s>0&&!fseek(f,0,SEEK_SET));void*b=malloc(s);CHECK(b&&fread(b,1,s,f)==(size_t)s&&!fclose(f));*n=s;return b;}
static void indexed_cases(void){Uint8 want[64000];const int xy[][2]={{98,100},{0,-13},{308,-1},{0,199},{-1,100},{309,100}};enemy[0].sprite2s=&spriteSheet11;enemy[0].enemytype=513;enemy[0].size=1;enemy[0].scoreitem=1;enemy[0].eyc=1;enemy[0].enemycycle=1;enemyAvail[0]=2;tempMapXOfs=28;
 for(int accepted=0;accepted<2;accepted++)for(int k=0;k<12;k++)for(int part=0;part<4;part++)for(int filter=0;filter<256;filter++)for(int p=0;p<(filter%16?1:6);p++){int x=xy[p][0],y=xy[p][1];for(int i=0;i<64000;i++)want[i]=((Uint8*)screen.pixels)[i]=(Uint8)(i*29+23);reset_area(x,y);game_probe_missing=!accepted;const Uint8*r=refs[k*4+part];for(int py=0;py<14;py++)for(int px=0;px<12;px++){int i=py*12+px,a=(y+py)*320+x+px;if(r[168+i]&&a>=0&&a<64000)want[a]=filter?(filter|(r[i]&15)):r[i];}unsigned before=original_calls,old=draws;enemy[0].ex=x-28;enemy[0].ey=y;enemy[0].egr[0]=ids[k];enemy[0].filter=filter;blit_enemy(&screen,0,0,0,parts[part]);CHECK(original_calls==before+1);CHECK(draws==old+(unsigned)(accepted&&p<4));CHECK(!memcmp(want,screen.pixels,64000));CHECK(!suppress);transactions++;}game_probe_missing=false;
}
static void indexed_held_cycle(void){
 const unsigned held[20]={159,161,163,161,159,197,199,201,199,197,235,237,239,237,235,273,275,277,275,273};Uint8 want[64000];
 for(int accepted=0;accepted<2;accepted++)for(int frame=0;frame<20;frame++){
  int k=data513_base_slot(held[frame]);for(int i=0;i<64000;i++)want[i]=((Uint8*)screen.pixels)[i]=(Uint8)(i*29+23);reset_area(98,100);game_probe_missing=!accepted;
  enemy[0].ex=98-28;enemy[0].ey=100;enemy[0].egr[0]=held[frame];enemy[0].filter=frame%2?0xe0:0;
  for(int p=0;p<4;p++){int x=98+p%2*12,y=100+p/2*14;const Uint8*r=refs[k*4+p];for(int py=0;py<14;py++)for(int px=0;px<12;px++){int i=py*12+px,a=(y+py)*320+x+px;if(r[168+i])want[a]=enemy[0].filter?(enemy[0].filter|(r[i]&15)):r[i];}unsigned before=original_calls,old=draws;blit_enemy(&screen,0,p%2*12,p/2*14,parts[p]);CHECK(original_calls==before+1&&draws==old+(unsigned)accepted);CHECK(!memcmp(want,screen.pixels,64000)&&!suppress);transactions++;}
 }game_probe_missing=false;
}
static void shared_and_alias_negatives(void){
 G101EnemyContext c={513,0,2,1,true,false,true,false};Sprite2_array alias={malloc(spriteSheet11.size),spriteSheet11.size};CHECK(alias.data);memcpy(alias.data,spriteSheet11.data,alias.size);CHECK(alias.data!=spriteSheet11.data&&!memcmp(alias.data,spriteSheet11.data,alias.size));
 for(unsigned k=0;k<12;k++)for(unsigned p=0;p<4;p++){reset_area(98,100);CHECK(!data513_pickup(&screen,98,100,alias,ids[k],parts[p],0,&c));CHECK(!render_mirror_enemy_tile(&screen,98,100,alias,ids[k],parts[p],0,&c));CHECK(draws==0&&!suppress);}free(alias.data);
 Uint8 want[64000];enemy[0].enemytype=512;enemy[0].ex=98-28;enemy[0].ey=100;enemy[0].egr[0]=273;
 for(int filter=0;filter<256;filter++)for(int part=0;part<4;part++){
  for(int i=0;i<64000;i++)want[i]=((Uint8*)screen.pixels)[i]=(Uint8)(i*29+23);reset_area(98,100);enemy[0].filter=filter;const Uint8*r=refs[9*4+part];
  for(int py=0;py<14;py++)for(int px=0;px<12;px++){int i=py*12+px,a=(100+py)*320+98+px;if(r[168+i])want[a]=filter?(filter|(r[i]&15)):r[i];}
  unsigned before=original_calls;blit_enemy(&screen,0,0,0,parts[part]);CHECK(original_calls==before+1&&draws==0&&!suppress);CHECK(!memcmp(want,screen.pixels,64000));transactions++;
 }enemy[0].enemytype=513;
}
static void overlap_and_alpha(void){for(int first=0;first<12;first++)for(int second=0;second<12;second++){reset_area(98,100);CHECK(draw_asset(98,100,assets+510+first,MIRROR_NORMAL,NULL));CHECK(draw_asset(98,100,assets+510+second,MIRROR_NORMAL,NULL));for(int py=0;py<224;py++)for(int px=0;px<192;px++){int n=(100*8+py)*canvas->w+98*8+px;const Uint8*a=assets[510+first].rgba+4*(py*192+px),*b=assets[510+second].rgba+4*(py*192+px);CHECK(((Uint32*)canvas->pixels)[n]==alpha_oracle(alpha_oracle(bg(n),a),b));pixels++;}}
 Uint8*rgba=malloc(192*224*4);CHECK(rgba);for(int k=0;k<12;k++){Asset a=assets[510+k];memcpy(rgba,a.rgba,192*224*4);a.rgba=rgba;for(int i=0;i<192*224;i++)rgba[4*i+3]=(Uint8[]){0,1,63,127,128,191,254,255}[i%8];for(int p=0;p<4;p++){reset_area(98,100);SDL_Rect q={(p%2)*12,(p/2)*14,12,14};CHECK(draw_asset_filtered(98,100,&a,MIRROR_NORMAL,&q,0,NULL,NULL,NULL));check_pixels(&a,98,100,parts[p],0);}}
 free(rgba);
}
static void ordered_quadrants(void){const unsigned held[]={159,161,163,161,159,197,199,201,199,197,235,237,239,237,235,273,275,277,275,273};G101EnemyContext c={513,0,2,1,true,false,true,false};for(int frame=0;frame<20;frame++){int k=data513_base_slot(held[frame]);reset_area(98,100);for(int p=0;p<4;p++){CHECK(render_mirror_enemy_tile(&screen,98+p%2*12,100+p/2*14,spriteSheet11,held[frame],parts[p],0,&c));render_mirror_entity_end();CHECK(draws==(unsigned)p+1);for(int py=0;py<224;py++)for(int px=0;px<192;px++){int n=(800+py)*canvas->w+784+px;const Uint8*r=assets[510+k].rgba+4*(py*192+px);bool touched=(py/112*2+px/96)<=p;CHECK(((Uint32*)canvas->pixels)[n]==(touched?alpha_oracle(bg(n),r):bg(n)));pixels++;}}}}
static void boundary_matrix(void){G101EnemyContext c={513,0,2,1,true,false,true,false};const int xs[]={-13,-1,0,1,296,297,307,308,309,319,320},ys[]={-28,-14,-13,-1,0,181,182,186,187,198,199,200};
 for(unsigned k=0;k<12;k++)for(unsigned p=0;p<4;p++)for(unsigned ix=0;ix<sizeof(xs)/sizeof(*xs);ix++)for(unsigned iy=0;iy<sizeof(ys)/sizeof(*ys);iy++){
  int x=xs[ix],y=ys[iy],px=p%2*12,py=p/2*14;bool wanted=x>=0&&x<=308&&y>=-13&&y<=199;reset_area(x-px,y-py);unsigned before=draws;CHECK(render_mirror_enemy_tile(&screen,x,y,spriteSheet11,ids[k],parts[p],0,&c)==wanted);CHECK(draws==before+(unsigned)wanted);if(wanted)check_pixels(assets+510+k,x-px,y-py,parts[p],0);render_mirror_entity_end();
 }
}
static void cache_checks(bool valid,const char*good){const char*saved=game_probe_assets;game_probe_assets=valid?"/nonexistent-data513-unit":good;CHECK(data513_family_ready()==valid);game_probe_assets=saved;clear_assets();for(int mode=0;mode<6;mode++){game_probe_density=mode==0?1:mode==1?4:8;game_probe_missing=mode==2;game_probe_invalid=mode==3;game_probe_original_reference=mode==4;game_probe_assets=mode==5?NULL:good;CHECK(!data513_family_ready()&&!data513_checked);}game_probe_density=8;game_probe_missing=game_probe_invalid=game_probe_original_reference=false;game_probe_assets=good;CHECK(data513_family_ready()&&data513_checked);game_probe_assets=saved;}
static void cache_mutation(void){
 char path[2048];CHECK(strstr(full_pack,"data513-negative-")!=NULL);CHECK(snprintf(path,sizeof(path),"%s/data513-bank11-159-8.hda",full_pack)<(int)sizeof(path));
 FILE*f=fopen(path,"r+b");CHECK(f&&fwrite("BAD!",1,4,f)==4&&!fclose(f));CHECK(data513_family_ready());clear_assets();CHECK(!data513_family_ready());
 f=fopen(path,"r+b");CHECK(f&&fwrite("HDR1",1,4,f)==4&&!fclose(f));CHECK(!data513_family_ready());clear_assets();CHECK(data513_family_ready());
}
int main(int argc,char**argv){CHECK(argc==7);bounded=!strcmp(argv[1],"bounded");game_probe_assets=full_pack=argv[2];legacy_pack=argv[3];bool valid=atoi(argv[4])!=0;Uint8 tokens[6]={0};spriteSheet8=(Sprite2_array){tokens,1};spriteSheet9=(Sprite2_array){tokens+1,1};spriteSheet11=(Sprite2_array){tokens+2,1};spriteSheet12=(Sprite2_array){tokens+3,1};explosionSpriteSheet=(Sprite2_array){tokens+4,1};enemySpriteSheets[0]=(Sprite2_array){tokens+5,1};enemySpriteSheetIds[0]=1;
 CHECK(sizeof(assets)/sizeof(*assets)==522);CHECK(data513_family_ready()==valid);CHECK(data513_checked&&data513_valid==valid);CHECK(data513_family_ready()==valid);for(int i=0;i<510;i++)CHECK(!assets[i].initialized);start();for(int i=0;i<256;i++)rgb_palette[i]=(i*71%256)<<16|(i*31%256)<<8|(i*13%256);isolation();
 if(!strcmp(argv[1],"cache"))cache_mutation();
 if(strcmp(argv[1],"loader")&&strcmp(argv[1],"cache")){CHECK(valid);G101EnemyContext c={513,0,2,1,true,false,true,false};const int xy[][2]={{98,100},{0,-13},{308,-1},{0,199},{308,199},{0,0}};
  for(int k=0;k<12;k++)for(int p=0;p<4;p++)for(int f=0;f<256;f++)for(int j=0;j<(f%16?1:6);j++){int x=xy[j][0],y=xy[j][1],px=p%2*12,py=p/2*14;reset_area(x-px,y-py);CHECK(render_mirror_enemy_tile(&screen,x,y,spriteSheet11,ids[k],parts[p],f,&c));CHECK(draws==1&&suppress&&log_role==124);check_pixels(assets+510+k,x-px,y-py,parts[p],f);render_mirror_entity_end();}
  reset_area(98,100);guards();boundary_matrix();ordered_quadrants();overlap_and_alpha();char path[2048];size_t n;snprintf(path,sizeof(path),"%s/%s",argv[5],!strcmp(argv[1],"xmas")?"xmas-bank11.bin":"bank11.bin");spriteSheet11.data=read_file(path,&n);spriteSheet11.size=n;snprintf(path,sizeof(path),"%s/index-reference.bin",argv[5]);void*r=read_file(path,&n);CHECK(n==sizeof(refs));memcpy(refs,r,n);free(r);indexed_cases();indexed_held_cycle();shared_and_alias_negatives();free(spriteSheet11.data);
 }
 cache_checks(valid,argv[6]);clear_assets();free(canvas->pixels);free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);free(screen.pixels);printf("{\"status\":\"PASS\",\"checks\":%llu,\"pixel_checks\":%llu,\"indexed_transactions\":%llu}\n",(unsigned long long)checks,(unsigned long long)pixels,(unsigned long long)transactions);return 0;}
