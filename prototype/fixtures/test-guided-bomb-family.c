/* Extracted production functions, independent per-channel pixel oracle.
 * This executable is a bounded unit harness. It never starts the game or SDL. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;
typedef uint16_t Uint16;
typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int w,h,pitch;void *pixels;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef enum {ENTITY_TILE,ENTITY_QUAD} EntityDrawLayout;
typedef enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW} EntityDrawStyle;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ASSET_NEWSH2=101,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106};
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#include "production-types.inc"
static Uint8 bank_tokens[5];
static Sprite2_array spriteSheet8={bank_tokens,1},spriteSheet9={bank_tokens+1,1},spriteSheet12={bank_tokens+2,1},explosionSpriteSheet={bank_tokens+3,1};
static SDL_Surface storage,screen,other,*canvas=&storage,*game_screen=&screen;
static bool active=true,suppress,suppress_green_smoke,suppress_cloud;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference,game_probe_local_blend,game_probe_known_blend;
static const char *reject_reason,*game_probe_assets;
static int game_probe_density=8;
static Uint32 rgb_palette[256];
static Uint8 selected[320*200],restored_mask[320*200],*hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
static GreenHead green_heads[256];
static unsigned int green_head_count,region_count,draws,local_entities,local_regions,local_blocks,expanded_regions,boundary_crossings,blend_source_index;
static unsigned int banking_draw_player;
static uint64_t mirror_logic_tick;
static TalonBank talon_banks[2];
static const int original_visual_indices[5]={0,2,6,10,12};
static unsigned long long checks,pixels_checked;
#define CHECK(x) do {if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(3);}checks++;}while(0)
static void render_mirror_unsupported(const char *s){reject_reason=s;}
static void game_probe_restore_region(unsigned int n,SDL_Rect a,SDL_Rect b,unsigned int g,unsigned int k){(void)n;(void)a;(void)b;(void)g;(void)k;}
static unsigned classic_draws,classic_index,classic_style,classic_layout,classic_bank;static int classic_x,classic_y;
static void record_classic(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i,int style,int layout){CHECK(s==game_screen);classic_draws++;classic_x=x;classic_y=y;classic_index=i;classic_style=style;classic_layout=layout;classic_bank=b.data==spriteSheet8.data?8:b.data==spriteSheet12.data?12:0;}
#define STUB_BLIT(name,style,layout) static void name(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){record_classic(s,x,y,b,i,style,layout);}
STUB_BLIT(blit_sprite2,ENTITY_NORMAL,ENTITY_TILE)
STUB_BLIT(blit_sprite2_blend,ENTITY_BLEND,ENTITY_TILE)
STUB_BLIT(blit_sprite2_darken,ENTITY_SHADOW,ENTITY_TILE)
STUB_BLIT(blit_sprite2x2,ENTITY_NORMAL,ENTITY_QUAD)
STUB_BLIT(blit_sprite2x2_blend,ENTITY_BLEND,ENTITY_QUAD)
STUB_BLIT(blit_sprite2x2_darken,ENTITY_SHADOW,ENTITY_QUAD)
static void game_probe_draw(int role,unsigned index,int x,int y,int style,int layout,bool mirrored){(void)role;(void)index;(void)x;(void)y;(void)style;(void)layout;(void)mirrored;}
#include "production-helpers.inc"
#include "production-entity.inc"
static const unsigned int target_ids[4]={19,171,20,21};
#define TARGET_COUNT 4
static const char *baseline_pack;
static const unsigned int control_ids[5]={59,214,215,216,217};
static const char *full_pack;
static Uint8 actual[TARGET_COUNT][96*112*4];
static void reset(void)
{
 for(unsigned int i=0;i<sizeof(assets)/sizeof(*assets);i++)free(assets[i].rgba);
 memset(assets,0,sizeof(assets));active=true;reject_reason=NULL;game_probe_density=8;game_probe_assets=full_pack;
 game_probe_missing=game_probe_invalid=game_probe_original_reference=false;
 game_probe_local_blend=game_probe_known_blend=false;banking_draw_player=0;
 region_count=draws=green_head_count=0;suppress=suppress_green_smoke=suppress_cloud=false;
}
static int expected_slot(int bank,unsigned int id,int layout)
{
 if(bank==0&&layout==ENTITY_TILE){if(id==59)return 5;if(id==103)return 325;const unsigned int old_pulse[]={58,60,62,165};for(int j=0;j<4;j++)if(id==old_pulse[j])return 321+j;for(int j=0;j<TARGET_COUNT;j++)if(id==target_ids[j])return 326+j;if(id>=214&&id<=217)return 182+(int)id-214;}
 if(bank==1&&layout==ENTITY_QUAD&&id>=229&&id<=237&&id%2==1)return ((int)id-229)/2;
 /* Independently specified old newsh6 ranges, intentionally including83. */
 if(bank==3&&layout==ENTITY_TILE){const int ranges[][3]={{122,133,31},{3,14,43},{41,52,55},{22,33,67},{60,71,79},{146,152,91},{192,203,98},{154,165,110},{211,222,122},{173,184,134},{135,141,146},{78,84,175}};for(unsigned int j=0;j<sizeof(ranges)/sizeof(*ranges);j++)if(id>=(unsigned)ranges[j][0]&&id<=(unsigned)ranges[j][1])return ranges[j][2]+(int)id-ranges[j][0];const int shield[]={229,230,231,232,233,234,235,236,237,248,249,250,252,253,254,255,256,267,268,269,272,275};for(int j=0;j<22;j++)if(id==(unsigned)shield[j])return 153+j;}
 return -1;
}
static void finite_bindings(void)
{
 CHECK(sizeof(assets)/sizeof(*assets)==330);
 Sprite2_array banks[]={spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet,{bank_tokens+4,1},{NULL,0}};
 for(int b=0;b<6;b++)for(int layout=0;layout<3;layout++)for(unsigned int id=0;id<600;id++){
  reset();game_probe_invalid=true;CHECK(get_asset(banks[b],id,layout)==NULL);int slot=expected_slot(b,id,layout),found=-1;
  for(int j=0;j<330;j++)if(assets[j].initialized){CHECK(found==-1);found=j;}
  CHECK(found==slot);
  if(slot>=0){Asset *q=assets+slot;CHECK(q->bank==(b==0?8:b==1?9:106));CHECK(q->index==(int)id);CHECK(q->w==(layout==ENTITY_QUAD?24:12)&&q->h==(layout==ENTITY_QUAD?28:14));CHECK(q->anchor_x==(b==1?5:b==0&&id==59?-1:0));CHECK(q->anchor_y==(b==1?7:0));}
 }
 for(int b=0;b<6;b++)for(unsigned int id=0;id<600;id++){
  reset();bool got=render_mirror_enemy_shot(game_screen,0,0,banks[b],id);
  /* Reject everything except the existing exact112/113 path; positive pixels below. */
  if(!(b==0&&(id==112||id==113)))CHECK(!got&&draws==0);
 }
}
static void file_write(unsigned int id,int density,int bad)
{
 char name[80];snprintf(name,sizeof(name),"bullet-%u-%d.hda",id,density);FILE *f=fopen(name,"wb");CHECK(f);
 Uint8 magic[4]={'H','D','R','1'};if(bad==6)magic[0]='X';CHECK(fwrite(magic,1,4,f)==4);
 uint32_t words[]={80000+id,(uint32_t)density,12,14,0,0};if(bad>=0&&bad<6)words[bad]++;
 for(int j=0;j<6;j++)for(int k=0;k<4;k++)CHECK(fputc((words[j]>>(8*k))&255,f)!=EOF);
 size_t n=(size_t)12*14*density*density*4;if(bad==7)n--;if(bad==8)n++;
 for(size_t j=0;j<n;j++){CHECK(fputc((unsigned char)(j*17+id),f)!=EOF);}
 CHECK(!fclose(f));
}
static void retain_file(unsigned int id,int density)
{static unsigned serial;char name[80],save[120];snprintf(name,sizeof(name),"bullet-%u-%d.hda",id,density);snprintf(save,sizeof(save),"%s.retained-%u",name,++serial);CHECK(!rename(name,save));}
static void loader_cases(void)
{
 for(int j=0;j<TARGET_COUNT;j++){
  reset();Asset*a=get_asset(spriteSheet8,target_ids[j],ENTITY_TILE);CHECK(a==assets+326+j&&a->valid&&a->density==8);CHECK(!memcmp(a->rgba,actual[j],sizeof(actual[j])));CHECK(get_asset(spriteSheet8,target_ids[j],ENTITY_TILE)==a);
  for(int gate=0;gate<3;gate++){reset();if(gate==0)game_probe_density=1;if(gate==1)game_probe_missing=true;if(gate==2)game_probe_invalid=true;CHECK(!get_asset(spriteSheet8,target_ids[j],ENTITY_TILE));}
  reset();game_probe_assets=".";CHECK(!get_asset(spriteSheet8,target_ids[j],ENTITY_TILE));CHECK(assets[326+j].initialized&&!assets[326+j].valid);
  for(int bad=0;bad<9;bad++){file_write(target_ids[j],8,bad);reset();game_probe_assets=".";CHECK(!get_asset(spriteSheet8,target_ids[j],ENTITY_TILE));CHECK(!assets[326+j].valid);retain_file(target_ids[j],8);}
  file_write(target_ids[j],4,-1);reset();game_probe_assets=".";a=get_asset(spriteSheet8,target_ids[j],ENTITY_TILE);CHECK(a&&a->density==4);retain_file(target_ids[j],4);
  file_write(target_ids[j],8,6);file_write(target_ids[j],4,-1);reset();game_probe_assets=".";a=get_asset(spriteSheet8,target_ids[j],ENTITY_TILE);CHECK(a&&a->density==4);retain_file(target_ids[j],8);retain_file(target_ids[j],4);
 }
 /* Missing-parent isolation; positive descendant continuation is checked below. */
 for(int missing=0;missing<TARGET_COUNT;missing++){
  for(int j=0;j<TARGET_COUNT;j++)if(j!=missing)file_write(target_ids[j],8,-1);
  reset();game_probe_assets=".";for(int j=0;j<TARGET_COUNT;j++)CHECK((get_asset(spriteSheet8,target_ids[j],ENTITY_TILE)!=NULL)==(j!=missing));
  for(int j=0;j<TARGET_COUNT;j++)if(j!=missing)retain_file(target_ids[j],8);
 }
 for(int j=0;j<5;j++){reset();Asset*a=get_asset(spriteSheet8,control_ids[j],ENTITY_TILE);CHECK(a&&a==assets+(j?181+j:5)&&a->anchor_x==(j?0:-1)&&a->anchor_y==0&&a->density==8);}
 reset();CHECK(!get_asset(spriteSheet8,83,ENTITY_TILE));Asset *orb=get_asset(explosionSpriteSheet,83,ENTITY_TILE);CHECK(orb==assets+180&&orb->bank==106&&orb->index==83);
}
static Uint32 background(int x,int y){return 0xff000000u|((Uint32)((x*17+y*9)%256)<<16)|((Uint32)((x*3+y*23)%256)<<8)|(Uint32)((x*31+y*7)%256);}
static Uint32 oracle_alpha(Uint32 dst,const Uint8 *s,unsigned a)
{Uint32 o=0xff000000u;for(int c=0;c<3;c++){unsigned shift=(2-c)*8,old=(dst>>shift)&255,num=old*(255-a)+s[c]*a;o|=(num/255+(num%255>=128))<<shift;}return o;}
static Uint32 oracle_shadow(Uint32 dst,Uint8 alpha)
{Uint32 o=0xff000000u;for(int shift=0;shift<24;shift+=8){unsigned num=((dst>>shift)&255)*(510-alpha);o|=(num/510+(num%510>=255))<<shift;}return o;}
static void surface_start(int density)
{
 game_probe_density=density;canvas->w=20*density;canvas->h=20*density;canvas->pitch=canvas->w*4+12;
 screen.w=screen.h=20;screen.pitch=24;screen.pixels=calloc(24,20);canvas->pixels=malloc((size_t)canvas->pitch*canvas->h);
 size_t n=(size_t)canvas->w*canvas->h;hd_owner=malloc(n);cloud_owner=malloc(n);green_under_owner=malloc(n);green_first=malloc(n*2);green_under=malloc(n*4);CHECK(canvas->pixels&&screen.pixels&&hd_owner&&cloud_owner&&green_under_owner&&green_first&&green_under);
 for(int y=0;y<20;y++)for(int x=0;x<20;x++)((Uint8*)screen.pixels)[y*screen.pitch+x]=(Uint8)(x*13+y*17);
}
static void scene_reset(int owner)
{
 memset(canvas->pixels,0xcd,(size_t)canvas->pitch*canvas->h);memset(selected,0,sizeof(selected));memset(restored_mask,0,sizeof(restored_mask));
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++){int n=y*canvas->w+x;*((Uint32*)((Uint8*)canvas->pixels+y*canvas->pitch)+x)=background(x,y);hd_owner[n]=(Uint8)owner;cloud_owner[n]=1;green_first[n]=7;green_under[n]=0x12345678u;green_under_owner[n]=2;}
 region_count=draws=green_head_count=local_entities=0;suppress=suppress_cloud=suppress_green_smoke=false;reject_reason=NULL;game_probe_original_reference=false;
}
static void surface_end(void)
{free(canvas->pixels);free(screen.pixels);free(hd_owner);free(cloud_owner);free(green_under_owner);free(green_first);free(green_under);canvas->pixels=screen.pixels=NULL;}
static void pixel_cases(void)
{
 for(int k=0;k<3;k++){int d=(int[]){2,4,8}[k];surface_start(d);
  for(int j=0;j<TARGET_COUNT;j++)for(int shadow=0;shadow<2;shadow++)for(int owner=0;owner<2;owner++)for(int place=0;place<3;place++)for(int alpha_mode=0;alpha_mode<2;alpha_mode++){
   scene_reset(owner);int x=(int[]){3,-2,17}[place],y=(int[]){2,-1,18}[place];Uint8 rgba[96*112*4];memcpy(rgba,actual[j],sizeof(rgba));
   if(alpha_mode)for(int n=0;n<96*112;n++)rgba[n*4+3]=(Uint8[]){0,1,17,63,127,128,191,254,255}[n%9];
   Asset asset={true,true,8,(int)target_ids[j],12,14,0,0,8,rgba};CHECK(draw_asset(x,y,&asset,shadow?MIRROR_SHADOW:MIRROR_NORMAL,NULL));CHECK(draws==1&&region_count==1&&suppress&&!suppress_cloud&&!suppress_green_smoke&&!green_head_count);
   for(int py=0;py<canvas->h;py++)for(int px=0;px<canvas->w;px++){
    int n=py*canvas->w+px;bool in=px>=x*d&&px<(x+12)*d&&py>=y*d&&py<(y+14)*d;
    const Uint8*s=in?rgba+4*((py-y*d)*8/d*96+(px-x*d)*8/d):NULL;bool covered=s&&s[3];Uint32 want=background(px,py);
    if(covered){if(!shadow)want=oracle_alpha(want,s,s[3]);else if(owner)want=oracle_shadow(want,s[3]);else{Uint8 ix=((Uint8*)screen.pixels)[(py/d)*screen.pitch+px/d],di=(Uint8)((ix&0xf0)|((ix&15)/2));Uint32 color=rgb_palette[di];Uint8 dark[]={(color>>16)&255,(color>>8)&255,color&255};want=oracle_alpha(want,dark,s[3]);}}
    CHECK(*((Uint32*)((Uint8*)canvas->pixels+py*canvas->pitch)+px)==want);CHECK(hd_owner[n]==(covered?1:owner));CHECK(cloud_owner[n]==(covered?0:1));CHECK(green_first[n]==(covered?0:7));CHECK(green_under[n]==0x12345678u&&green_under_owner[n]==2);pixels_checked++;
   }
   for(int py=0;py<canvas->h;py++)for(int pad=canvas->w*4;pad<canvas->pitch;pad++)CHECK(((Uint8*)canvas->pixels)[py*canvas->pitch+pad]==0xcd);
  }
  surface_end();
 }
 /* Full entrypoints use actual assets, preserve per-ID shadow behavior. */
 reset();surface_start(8);
 for(int j=0;j<TARGET_COUNT;j++){scene_reset(1);CHECK(render_mirror_entity(game_screen,1,1,spriteSheet8,target_ids[j],MIRROR_NORMAL,ENTITY_TILE));CHECK(draws==1&&!green_head_count);scene_reset(1);CHECK(render_mirror_entity(game_screen,1,1,spriteSheet8,target_ids[j],MIRROR_SHADOW,ENTITY_TILE));CHECK(draws==1);scene_reset(1);CHECK(!render_mirror_entity(&other,1,1,spriteSheet8,target_ids[j],MIRROR_NORMAL,ENTITY_TILE));CHECK(!draws);scene_reset(1);game_probe_original_reference=true;CHECK(render_mirror_entity(game_screen,1,1,spriteSheet8,target_ids[j],MIRROR_NORMAL,ENTITY_TILE));CHECK(!green_head_count);}
 for(int j=0;j<5;j++){scene_reset(1);memset(green_first,0,(size_t)canvas->w*canvas->h*2);CHECK(render_mirror_entity(game_screen,1,1,spriteSheet8,control_ids[j],MIRROR_NORMAL,ENTITY_TILE));CHECK(green_head_count==(unsigned)(j!=0));scene_reset(1);CHECK(render_mirror_entity(game_screen,1,1,spriteSheet8,control_ids[j],MIRROR_SHADOW,ENTITY_TILE)==(j==0));CHECK(draws==(unsigned)(j==0));}
 for(unsigned id=112;id<=113;id++){scene_reset(1);CHECK(render_mirror_enemy_shot(game_screen,1,1,spriteSheet8,id));CHECK(draws==1&&assets[218+id-112].valid);}
 /* Existing assets survive all four absent, with no global override. */
 reset();game_probe_assets=baseline_pack;scene_reset(1);
 CHECK(!game_probe_missing&&!game_probe_invalid);
 for(int j=0;j<TARGET_COUNT;j++){CHECK(!render_mirror_entity(game_screen,1,1,spriteSheet8,target_ids[j],MIRROR_NORMAL,ENTITY_TILE));CHECK(!draws&&!suppress&&assets[326+j].initialized&&!assets[326+j].valid&&!reject_reason);}
 for(int j=0;j<5;j++) {scene_reset(1);memset(green_first,0,(size_t)canvas->w*canvas->h*2);CHECK(render_mirror_entity(game_screen,1,1,spriteSheet8,control_ids[j],MIRROR_NORMAL,ENTITY_TILE));CHECK(draws==1&&green_head_count==(unsigned)(j!=0));}
 for(int j=0;j<4;j++) {scene_reset(1);CHECK(render_mirror_entity(game_screen,1,1,spriteSheet8,(unsigned[]){58,60,62,165}[j],MIRROR_NORMAL,ENTITY_TILE));CHECK(draws==1&&assets[321+j].valid);}
 scene_reset(1);CHECK(render_mirror_entity(game_screen,1,1,spriteSheet8,103,MIRROR_NORMAL,ENTITY_TILE));CHECK(draws==1&&assets[325].valid);
 for(unsigned id=78;id<=84;id++)for(int style=0;style<2;style++){scene_reset(1);memset(green_first,0,(size_t)canvas->w*canvas->h*2);CHECK(render_mirror_entity(game_screen,1,1,explosionSpriteSheet,id,style,ENTITY_TILE));CHECK(draws==1&&suppress_green_smoke&&assets[175+id-78].valid&&!reject_reason);}
 for(unsigned id=122;id<=141;id++){if(id==134)continue;scene_reset(1);CHECK(render_mirror_entity(game_screen,1,1,explosionSpriteSheet,id,MIRROR_NORMAL,ENTITY_TILE));CHECK(draws==1);}
 for(unsigned id=112;id<=113;id++){scene_reset(1);CHECK(render_mirror_enemy_shot(game_screen,1,1,spriteSheet8,id));CHECK(draws==1);}
 CHECK(!game_probe_missing&&!game_probe_invalid&&!reject_reason);
 surface_end();reset();
}
static void boundary_cases(void)
{
 surface_start(8);
 /* Each physical omission is its own pack, not a renderer-disable flag. */
 for(int missing=0;missing<TARGET_COUNT;missing++){
  char dir[1024];CHECK(snprintf(dir,sizeof(dir),"%s/missing-%u",full_pack,target_ids[missing])<(int)sizeof(dir));reset();game_probe_assets=dir;
  for(int pass=0;pass<2;pass++)for(int j=0;j<TARGET_COUNT;j++)for(int style=0;style<2;style++){
   scene_reset(1);classic_draws=0;draw_entity_sprite2(game_screen,2,3,spriteSheet8,target_ids[j],style?ENTITY_SHADOW:ENTITY_NORMAL,ENTITY_TILE);
   CHECK(classic_draws==1&&classic_index==target_ids[j]&&classic_x==2&&classic_y==3&&classic_bank==8&&classic_layout==ENTITY_TILE&&classic_style==(unsigned)(style?ENTITY_SHADOW:ENTITY_NORMAL));
   CHECK(draws==(unsigned)(j!=missing)&&!suppress&&!reject_reason&&!game_probe_missing&&!game_probe_invalid);
  }
  scene_reset(1);CHECK(render_mirror_entity(game_screen,1,1,spriteSheet8,103,MIRROR_NORMAL,ENTITY_TILE));CHECK(draws==1&&assets[325].valid);
  for(int j=0;j<5;j++){scene_reset(1);CHECK(render_mirror_entity(game_screen,1,1,spriteSheet8,control_ids[j],MIRROR_NORMAL,ENTITY_TILE));}
  for(unsigned id=122;id<=141;id++){if(id==134)continue;scene_reset(1);CHECK(render_mirror_entity(game_screen,1,1,explosionSpriteSheet,id,MIRROR_NORMAL,ENTITY_TILE));CHECK(draws==1);}
 }
 /* Classic1x, explicit missing, invalid, and actual all-four absence each preserve indexed writes. */
 for(int mode=0;mode<4;mode++){
  reset();if(mode==0)game_probe_density=1;if(mode==1)game_probe_missing=true;if(mode==2)game_probe_invalid=true;if(mode==3)game_probe_assets=baseline_pack;
  for(int j=0;j<TARGET_COUNT;j++)for(int style=0;style<2;style++){scene_reset(1);classic_draws=0;draw_entity_sprite2(game_screen,2,3,spriteSheet8,target_ids[j],style?ENTITY_SHADOW:ENTITY_NORMAL,ENTITY_TILE);CHECK(classic_draws==1&&draws==0&&!suppress&&!reject_reason);}
 }
 /* Widget uses the identical shared tile binder;22 alone stays indexed. */
 reset();
 const unsigned widget_frames[][6]={{20,0,0,0,0,0},{20,20,0,0,0,0},{20,20,0,0,0,0},{20,20,21,0,0,0},{20,20,21,0,0,0},{20,20,21,21,0,0},{21,21,21,21,0,0},{22,22,21,0,0,0},{22,22,20,20,0,0},{22,22,22,22,20,0},{22,22,22,22,20,20}};
 for(int power=0;power<11;power++)for(int j=0;j<6;j++)if(widget_frames[power][j])for(int style=0;style<2;style++){
  scene_reset(1);classic_draws=0;unsigned id=widget_frames[power][j];draw_entity_sprite2(game_screen,2,3,spriteSheet8,id,style?ENTITY_SHADOW:ENTITY_NORMAL,ENTITY_TILE);CHECK(classic_draws==1&&classic_index==id&&draws==(unsigned)(id!=22)&&!reject_reason&&!suppress);
 }
 /* The unmapped22 draw does not poison an immediately following shared20/21 draw. */
 scene_reset(1);classic_draws=0;draw_entity_sprite2(game_screen,2,3,spriteSheet8,22,ENTITY_NORMAL,ENTITY_TILE);CHECK(draws==0&&!reject_reason);draw_entity_sprite2(game_screen,2,3,spriteSheet8,20,ENTITY_NORMAL,ENTITY_TILE);draw_entity_sprite2(game_screen,2,3,spriteSheet8,21,ENTITY_NORMAL,ENTITY_TILE);CHECK(classic_draws==3&&draws==2&&!reject_reason);
 surface_end();reset();
}
int main(int argc,char **argv)
{
 CHECK(argc==3);full_pack=argv[1];baseline_pack=argv[2];game_probe_assets=full_pack;
 for(int i=0;i<256;i++)rgb_palette[i]=((Uint32)((i*3)%256)<<16)|((Uint32)((i*7)%256)<<8)|((i*11)%256);
 for(int j=0;j<TARGET_COUNT;j++){char name[50];snprintf(name,sizeof(name),"actual-%u.rgba",target_ids[j]);FILE*f=fopen(name,"rb");CHECK(f);CHECK(fread(actual[j],1,sizeof(actual[j]),f)==sizeof(actual[j]));CHECK(fgetc(f)==EOF&&!fclose(f));}
 /* Finite enumeration is non-drawing, with actual112/113 positive cases below. */
 surface_start(8);scene_reset(1);finite_bindings();surface_end();loader_cases();pixel_cases();boundary_cases();
 printf("PASS: %llu assertions; %llu pixel oracles; finite banks/layouts/IDs0..599; exact slots and anchors; actual RGBA; all6 header words, magic, short/trailing data; missing each/all; density fallback; normal/shadow2x4x8x; clipping/pitch/ownership; each19/171/20/21 physically missing and all-four absent; classic indexed boundary preserved; shared Widget20/21 and unmapped22; old59/103/Pulse/green/trails and enemy112/113 scope.\n",checks,pixels_checked);return 0;
}
