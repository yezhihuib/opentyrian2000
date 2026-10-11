#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8; typedef uint16_t Uint16; typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int w,h,pitch;void *pixels;} SDL_Surface;
typedef struct {size_t size;Uint8 *data;} Sprite2_array;
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
/* Asset enum is extracted verbatim from the candidate. */
#include "types.inc"
static SDL_Surface *canvas,*game_screen;
static int game_probe_density,game_probe_scene_assets=1;
static bool game_probe_original_reference,game_probe_local_blend=true,game_probe_known_blend;
static bool game_probe_missing,game_probe_invalid,active=true,suppress,suppress_green_smoke,suppress_cloud;
static const char *game_probe_assets,*reject_reason;
static Uint32 rgb_palette[256];
static Uint8 expected[320*200],selected[320*200],restored_mask[320*200];
static Uint8 *hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
static GreenHead green_heads[256];
static HdRegion regions[256];
static unsigned int green_head_count,region_count,local_entities,draws;
static unsigned int local_regions,local_blocks,expanded_regions,boundary_crossings,blend_source_index;
static Sprite2_array enemySpriteSheets[4];static unsigned int enemySpriteSheetIds[4];
static unsigned int scene_calls; static int logged_role,logged_index,logged_x,logged_y,logged_part,logged_style;static bool logged_mirrored;
static void render_mirror_unsupported(const char *reason){fprintf(stderr,"Unexpected rejection: %s\n",reason);abort();}
static void game_probe_restore_region(unsigned int s,SDL_Rect a,SDL_Rect b,unsigned int g,unsigned int c){(void)s;(void)a;(void)b;(void)g;(void)c;}
static void game_probe_scene_draw(int role,unsigned int index,int x,int y,int part,int style,bool mirrored){scene_calls++;logged_role=role;logged_index=(int)index;logged_x=x;logged_y=y;logged_part=part;logged_style=style;logged_mirrored=mirrored;}
#include "functions.inc"
static int LW=40,LH=44;
static Uint32 *oracle;static Uint8 *oracle_cloud;
static unsigned long long checks,quad_calls,guard_checks;
static char pack_path[2048];
static Uint8 actual_rgba[12][192*224*4];static bool use_actual;
static const int stone_ids[]={1,3,5,39,41,43,7,9,11,45,47,49};
static const int old_ids[]={77,79,115,117,85,87,123,125,191,193,195,197,199,201,203,205,229,231,233,235,237,239,241,243,81,83,119,121,267,269,271};
static int stone_index(int base){for(int i=0;i<12;i++)if(stone_ids[i]==base)return i;return -1;}
static int role_for(int base){return stone_index(base)>=0?110:101;}
static Sprite2_array bank_for(int base){return enemySpriteSheets[stone_index(base)>=0?1:0];}
static int slot_for(int base){if(stone_index(base)>=0)return 253+stone_index(base);const int ids[]={77,79,115,117,85,87,123,125,191,193,195,197,199,201,203,205,229,231,233,235,237,239,241,243,81,83,119,121,267,269,271};const int slots[]={6,7,8,9,15,16,17,18,23,24,25,26,27,28,29,30,210,211,212,213,214,215,216,217,231,232,233,234,243,244,245};for(int i=0;i<31;i++)if(ids[i]==base)return slots[i];return -1;}
static const char *pack_root;
static void select_pack(const char *name){snprintf(pack_path,sizeof(pack_path),"%s/%s",pack_root,name);game_probe_assets=pack_path;}
static void clear_assets(void){for(size_t i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);memset(&assets[i],0,sizeof(assets[i]));}}
static void synthetic(int base,int x,int y,Uint8 p[4]){if(use_actual){assert(stone_index(base)>=0);memcpy(p,actual_rgba[stone_index(base)]+4*(y*192+x),4);return;}static const Uint8 alpha[]={0,1,127,128,254,255};p[0]=(Uint8)(base*7+x*3+y);p[1]=(Uint8)(base*11+x+y*5);p[2]=(Uint8)(base*13+x*7+y*2);p[3]=alpha[(x+2*y+base)%6];}
static Uint32 palette_channel(unsigned i,int channel){return (rgb_palette[i]/(1u<<((2-channel)*8)))%256;}
static void filter_oracle(const Uint8 source[4],int filter,Uint8 out[4]){
 memcpy(out,source,4);if(!filter)return;
 unsigned peak=source[0];if(source[1]>peak)peak=source[1];if(source[2]>peak)peak=source[2];
 unsigned n=peak*3840u,value=n/255+(n%255>=128),lo=value/256,hi=lo<15?lo+1:15,f=value%256;
 for(int c=0;c<3;c++){unsigned sum=palette_channel(filter|lo,c)*(256-f)+palette_channel(filter|hi,c)*f;out[c]=(Uint8)(sum/256+(sum%256>=128));}
}
static Uint32 blend_oracle(Uint32 color,const Uint8 p[4]){Uint32 result=0xff000000u;for(int c=0;c<3;c++){unsigned shift=(2-c)*8,old=(color>>shift)&255,n=old*(255-p[3])+p[c]*p[3];result|=(n/255+(n%255>=128))<<shift;}return result;}
static void alloc_canvas(int d){game_probe_density=d;canvas->w=LW*d;canvas->h=LH*d;canvas->pitch=canvas->w*4+16;size_t count=(size_t)canvas->w*canvas->h;canvas->pixels=malloc((size_t)canvas->pitch*canvas->h);oracle=malloc(count*4);oracle_cloud=malloc(count);hd_owner=malloc(count);cloud_owner=malloc(count);green_first=malloc(count*2);green_under=malloc(count*4);green_under_owner=malloc(count);assert(canvas->pixels&&oracle&&hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);}
static void free_canvas(void){free(canvas->pixels);free(oracle);free(oracle_cloud);free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);}
static void reset_canvas(void){size_t n=(size_t)canvas->w*canvas->h;memset(canvas->pixels,0xcd,(size_t)canvas->pitch*canvas->h);memset(hd_owner,1,n);memset(cloud_owner,1,n);memset(oracle_cloud,1,n);for(size_t k=0;k<n;k++){green_first[k]=7;green_under[k]=0xabcdef01;green_under_owner[k]=2;}memset(selected,0,sizeof(selected));memset(expected,0,sizeof(expected));memset(game_screen->pixels,0,(size_t)game_screen->pitch*game_screen->h);region_count=green_head_count=draws=scene_calls=0;suppress=suppress_green_smoke=suppress_cloud=false;for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++){Uint32 c=0xff000000u|((x*7u+y*3u)%256)<<16|((x+y*11u)%256)<<8|((x*17u+y*5u)%256);oracle[y*canvas->w+x]=c;*(Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch+x*4)=c;}}
static void check_pixels(void){for(int y=0;y<canvas->h;y++){for(int x=0;x<canvas->w;x++){Uint32 got=*(Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch+x*4);if(got!=oracle[y*canvas->w+x]){fprintf(stderr,"pixel mismatch d=%d x=%d y=%d got%08x want%08x\n",game_probe_density,x,y,got,oracle[y*canvas->w+x]);abort();}assert(cloud_owner[y*canvas->w+x]==oracle_cloud[y*canvas->w+x]);assert(hd_owner[y*canvas->w+x]==1);assert(green_first[y*canvas->w+x]==(oracle_cloud[y*canvas->w+x]?7:0));assert(green_under[y*canvas->w+x]==0xabcdef01&&green_under_owner[y*canvas->w+x]==2);checks++;}for(int p=canvas->w*4;p<canvas->pitch;p++)assert(((Uint8 *)canvas->pixels)[y*canvas->pitch+p]==0xcd);}for(int i=0;i<game_screen->pitch*game_screen->h;i++)assert(!((Uint8 *)game_screen->pixels)[i]);}
static void expected_part(int base,int part,int origin_x,int origin_y,int ad,int filter){int d=game_probe_density,px=part==1||part==20?12:0,py=part==19||part==20?14:0;for(int y=py*d;y<(py+14)*d;y++)for(int x=px*d;x<(px+12)*d;x++){int dx=origin_x*d+x,dy=origin_y*d+y;if(dx<0||dy<0||dx>=canvas->w||dy>=canvas->h)continue;Uint8 src[4],color[4];synthetic(base,x*ad/d,y*ad/d,src);filter_oracle(src,filter,color);if(src[3])oracle_cloud[dy*canvas->w+dx]=0;oracle[dy*canvas->w+dx]=blend_oracle(oracle[dy*canvas->w+dx],color);}}
static void exercise_frame(int base,int ad,int filter,int x,int y,bool reverse_parts){static const int order[2][4]={{0,1,19,20},{20,0,19,1}};reset_canvas();for(int k=0;k<4;k++){int part=order[reverse_parts][k],px=part==1||part==20?12:0,py=part==19||part==20?14:0;assert(render_mirror_enemy_tile(game_screen,x+px,y+py,bank_for(base),base,part,filter));quad_calls++;assert(scene_calls==(unsigned)k+1&&logged_role==role_for(base)&&logged_index==base&&logged_part==part&&logged_x==x+px&&logged_y==y+py&&logged_style==(filter?3:0)&&logged_mirrored);Asset *a=&assets[slot_for(base)];assert(a->valid&&a->bank==role_for(base)&&a->index==base&&a->w==24&&a->h==28&&a->anchor_x==6&&a->anchor_y==7&&a->density==ad);expected_part(base,part,x,y,ad,filter);check_pixels();assert(region_count==1&&regions[0].rect.x==x&&regions[0].rect.y==y&&regions[0].rect.w==24&&regions[0].rect.h==28);render_mirror_entity_end();assert(!suppress&&!suppress_cloud&&!suppress_green_smoke);}}
static void guard_case(SDL_Surface *surface,Sprite2_array bank,int base,int part){reset_canvas();unsigned before=scene_calls;assert(!render_mirror_enemy_tile(surface,4,5,bank,base,part,0));assert(scene_calls==before);check_pixels();guard_checks++;}

static void guard_tests(void)
{
 Uint8 wrong_bytes=9;Sprite2_array wrong={1,&wrong_bytes};SDL_Surface other=*game_screen;
 for(unsigned base=0;base<600;base++){
  if(stone_index((int)base)<0)guard_case(game_screen,enemySpriteSheets[1],(int)base,0);
  if(slot_for((int)base)<0||stone_index((int)base)>=0)guard_case(game_screen,enemySpriteSheets[0],(int)base,0);
 }
 guard_case(game_screen,enemySpriteSheets[1],(int)UINT32_MAX,0);
 for(int j=0;j<12;j++){
  int base=stone_ids[j];
  for(int p=-2;p<=22;p++)if(p!=0&&p!=1&&p!=19&&p!=20)guard_case(game_screen,bank_for(base),base,p);
  guard_case(game_screen,wrong,base,0);guard_case(&other,bank_for(base),base,0);
  guard_case(game_screen,(Sprite2_array){0,NULL},base,0);
  /* Matching bytes and size do not establish sheet pointer identity. */
  Uint8 same=*bank_for(base).data;guard_case(game_screen,(Sprite2_array){1,&same},base,0);
  /* Loading any wrong numeric bank cannot authorize the new source family. */
  for(unsigned id=0;id<=12;id++)if(id!=9){enemySpriteSheetIds[1]=id;guard_case(game_screen,enemySpriteSheets[1],base,0);}
  enemySpriteSheetIds[1]=9;
 }
 Sprite2_array saved=enemySpriteSheets[1];enemySpriteSheets[1]=(Sprite2_array){0,NULL};
 guard_case(game_screen,enemySpriteSheets[1],1,0);enemySpriteSheets[1]=saved;
 game_probe_scene_assets=0;guard_case(game_screen,bank_for(1),1,0);
 game_probe_scene_assets=2;guard_case(game_screen,bank_for(1),1,0);game_probe_scene_assets=1;
 active=false;guard_case(game_screen,bank_for(1),1,0);active=true;
 reject_reason="test";guard_case(game_screen,bank_for(1),1,0);reject_reason=NULL;
}
static void absent_frame(int base)
{
 reset_canvas();for(int p=0;p<4;p++){
  int part=(int[]){0,1,19,20}[p];
  assert(!render_mirror_enemy_tile(game_screen,5,7,bank_for(base),base,part,0));
  assert(scene_calls==(unsigned)p+1&&logged_role==110&&logged_index==base&&logged_part==part&&!logged_mirrored);
  assert(!suppress&&!draws&&!region_count);render_mirror_entity_end();
 }check_pixels();
}
static void loader_tests(void)
{
 for(int j=0;j<12;j++)for(int bad=-1;bad<16;bad++){
  char name[64];snprintf(name,sizeof(name),"invalid-%d-%d",stone_ids[j],bad);
  clear_assets();select_pack(name);absent_frame(stone_ids[j]);
  assert(assets[253+j].initialized&&!assets[253+j].valid&&!assets[253+j].rgba);
  /* Failure is cached per component, not per bank or six-part assembly. */
  for(int k=0;k<12;k++)if(k!=j){
   reset_canvas();int base=stone_ids[k];
   assert(render_mirror_enemy_tile(game_screen,5,7,bank_for(base),base,0,0));
   expected_part(base,0,5,7,8,0);check_pixels();render_mirror_entity_end();
   assert(assets[253+k].valid&&assets[253+k].bank==110&&assets[253+k].index==base);
  }
 }
 for(int flag=0;flag<5;flag++){
  clear_assets();select_pack(flag==0?"empty":"full8");int d=game_probe_density;
  if(flag==1)game_probe_assets=NULL;
  if(flag==2)game_probe_missing=true;
  if(flag==3)game_probe_invalid=true;
  if(flag==4)game_probe_density=1;
  for(int j=0;j<12;j++)absent_frame(stone_ids[j]);
  game_probe_missing=game_probe_invalid=false;game_probe_density=d;
 }
 /* Intact and remnant are each independent complete six-component states. */
 for(int side=0;side<2;side++){
  clear_assets();select_pack(side?"intact-only":"remnant-only");
  for(int j=0;j<12;j++)if((j<6)==(side!=0))exercise_frame(stone_ids[j],8,0,5,7,false);else absent_frame(stone_ids[j]);
 }
 /* Misleading ship/Talon/newsh2/terrain names never substitute for newshE. */
 clear_assets();select_pack("wrong-prefixes");for(int j=0;j<12;j++)absent_frame(stone_ids[j]);
}
static void subset_tests(int base,int filter)
{
 const int parts[]={0,1,19,20};for(unsigned mask=1;mask<16;mask++){
  reset_canvas();for(int k=0;k<4;k++)if(mask&(1u<<k)){
   int part=parts[k],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
   assert(render_mirror_enemy_tile(game_screen,5+px,7+py,bank_for(base),base,part,filter));quad_calls++;
   expected_part(base,part,5,7,8,filter);check_pixels();render_mirror_entity_end();
   assert(!suppress&&!suppress_cloud&&!suppress_green_smoke);
  }
 }
}
static void overlay_frame(int base,int x,int y,int filter)
{
 for(int k=0;k<4;k++){
  int part=(int[]){0,1,19,20}[k],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
  assert(render_mirror_enemy_tile(game_screen,x+px,y+py,bank_for(base),base,part,filter));quad_calls++;
  expected_part(base,part,x,y,8,filter);render_mirror_entity_end();
 }
 check_pixels();assert(!suppress&&!suppress_cloud&&!suppress_green_smoke);
}
static void overlap_and_clear(void)
{
 clear_assets();select_pack("full8");
 for(int j=0;j<12;j++){
  reset_canvas();overlay_frame(stone_ids[j],2,3,0);overlay_frame(stone_ids[(j+1)%12],7,10,0xd0);
  overlay_frame(stone_ids[j],2,3,0x09); /* intentional repeated translucent calls */
  assert(region_count==2);
  reset_canvas();check_pixels();assert(!region_count&&!draws&&!scene_calls);
 }
}
static void actual_tests(void)
{
 clear_assets();select_pack("actual8");use_actual=true;
 for(int j=0;j<12;j++){
  char name[2048];snprintf(name,sizeof(name),"%s/actual-%d.rgba",pack_root,stone_ids[j]);
  FILE*f=fopen(name,"rb");assert(f);assert(fread(actual_rgba[j],1,sizeof(actual_rgba[j]),f)==sizeof(actual_rgba[j]));assert(fgetc(f)==EOF);assert(!fclose(f));
  for(size_t p=3;p<sizeof(actual_rgba[j]);p+=4)assert(actual_rgba[j][p]==255);
  for(int fi=0;fi<3;fi++){
   int filter=(int[]){0,0xd0,0x09}[fi];
   exercise_frame(stone_ids[j],8,filter,5,7,false);
   exercise_frame(stone_ids[j],8,filter,-11,-13,true);
   exercise_frame(stone_ids[j],8,filter,LW-4,LH-3,false);
   subset_tests(stone_ids[j],filter);
  }
  Asset*a=&assets[253+j];assert(a->valid&&memcmp(a->rgba,actual_rgba[j],sizeof(actual_rgba[j]))==0);
 }
 use_actual=false;clear_assets();
}
static void assembly_tests(void)
{
 free_canvas();LW=80;LH=64;alloc_canvas(8);clear_assets();select_pack("actual8");use_actual=true;
 /* Registered entire six-component canvas, original component call order. */
 for(int side=0;side<2;side++)for(int reverse=0;reverse<2;reverse++){
  reset_canvas();for(int k=0;k<6;k++){
   int cell=(int[]){1,2,3,4,5,0}[reverse?5-k:k],base=stone_ids[6*side+cell];
   overlay_frame(base,4+(cell%3)*24,4+(cell/3)*28,0);
  }
  assert(region_count==6);
  /* Six independently drawn remnants fully replace intact source registration. */
  if(side==0)for(int cell=0;cell<6;cell++)overlay_frame(stone_ids[6+cell],4+(cell%3)*24,4+(cell/3)*28,0);
  reset_canvas();check_pixels(); /* frame-clear ownership is explicitly clean */
 }
 use_actual=false;clear_assets();free_canvas();LW=40;LH=44;alloc_canvas(8);
}
static void other_bindings(void)
{
 clear_assets();select_pack("all-bindings");
 for(int i=0;i<31;i++)exercise_frame(old_ids[i],8,0,5,7,false);
 for(int i=0;i<12;i++)exercise_frame(stone_ids[i],8,0,5,7,false);
 for(size_t slot=0;slot<sizeof(assets)/sizeof(*assets);slot++){
  bool wanted=slot>=253;for(int i=0;i<31;i++)if(slot_for(old_ids[i])==(int)slot)wanted=true;
  assert(assets[slot].initialized==wanted);
 }
 /* Warm bank1 and bank9 caches cannot widen either source's finite whitelist. */
 for(int i=0;i<31;i++)guard_case(game_screen,enemySpriteSheets[1],old_ids[i],0);
 for(int i=0;i<12;i++)guard_case(game_screen,enemySpriteSheets[0],stone_ids[i],0);
 clear_assets();
}
static void relocated_sheet_tests(void)
{
 clear_assets();select_pack("full8");
 Sprite2_array sheets[4];unsigned ids[4];memcpy(sheets,enemySpriteSheets,sizeof(sheets));memcpy(ids,enemySpriteSheetIds,sizeof(ids));
 for(int slot=0;slot<4;slot++){
  for(int k=0;k<4;k++){enemySpriteSheets[k]=sheets[k];enemySpriteSheetIds[k]=2;}
  enemySpriteSheets[slot]=sheets[1];enemySpriteSheetIds[slot]=9;
  for(int j=0;j<12;j++)exercise_frame(stone_ids[j],8,0,5,7,false);
 }
 memcpy(enemySpriteSheets,sheets,sizeof(sheets));memcpy(enemySpriteSheetIds,ids,sizeof(ids));clear_assets();
}
int main(int argc,char **argv)
{
 assert(argc==2);pack_root=argv[1];SDL_Surface c={0},g={80,64,80,NULL};canvas=&c;game_screen=&g;
 g.pixels=calloc(80*64,1);Uint8 bank_bytes[4]={1,9,3,4};
 for(int k=0;k<4;k++){enemySpriteSheets[k]=(Sprite2_array){1,&bank_bytes[k]};enemySpriteSheetIds[k]=k==0?1:k==1?9:2;}
 for(int i=0;i<256;i++)rgb_palette[i]=((i*71u)%256)<<16|((i*31u)%256)<<8|((i*13u)%256);
 assert(ASSET_NEWSHE==110&&ASSET_TALON_BANK==109&&ASSET_NEWSH2==101);
 assert(sizeof(assets)/sizeof(*assets)==265);
 const int filters[]={0,0x70,0x80,0x09,0xd0};
 for(int mode=0;mode<3;mode++){
  int d=mode==0?4:8,ad=mode==1?8:4;alloc_canvas(d);clear_assets();select_pack(ad==8?"full8":"full4");
  for(int rev=0;rev<2;rev++)for(int i=0;i<12;i++)for(int f=0;f<5;f++)exercise_frame(stone_ids[rev?11-i:i],ad,filters[f],5,7,rev);
  for(int i=0;i<12;i++){
   exercise_frame(stone_ids[i],ad,0,-11,-13,false);
   exercise_frame(stone_ids[i],ad,0xd0,LW-4,LH-3,true);
   exercise_frame(stone_ids[i],ad,0,-1000,1000,false);
  }
  guard_tests();for(int i=0;i<253;i++)assert(!assets[i].initialized);
  printf("PASS density%d source%d: all48 stone quadrants, reverse/order, five filters, clipping, source-bank/part/null/collision guards\n",d,ad);
  if(mode==1){loader_tests();actual_tests();assembly_tests();overlap_and_clear();other_bindings();relocated_sheet_tests();
   puts("PASS: missing each/all/state; malformed every header word/magic/trailing/truncated/empty payload; cross-role/prefix isolation; classic/flags; actual opaque RGBA and15 quadrant subsets; registered six-part assemblies; overlap/reset;43 simultaneous bindings");}
  clear_assets();free_canvas();
 }
 free(g.pixels);printf("PASS %llu pixel comparisons; %llu successful quadrant calls; %llu rejected-source/part guards\n",checks,quad_calls,guard_checks);return 0;
}
