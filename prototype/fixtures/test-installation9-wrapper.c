/* Indexed call contract from unmodified production wrapper and RLE blitters.
 * Sprite bytes below are synthetic; no original game assets are required. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef struct {int BitsPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
typedef struct {size_t size;Uint8 *data;} Sprite2_array;
#define SDL_SwapLE16(x) (x)
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
static SDL_Surface *VGAScreen;
static Sprite2_array enemySpriteSheets[4];static unsigned enemySpriteSheetIds[4];
static const char shapeFile[]="2abcdefghijk";
static struct Enemy {Sprite2_array *sprite2s;int ex,ey,egr[20],enemycycle,filter;} enemy[1];
static int tempMapXOfs;
static bool asset_debug_enabled,mirror_result,suppressed;
static unsigned mirror_calls,original_calls,end_calls,pixel_calls;
static int want_x,want_y,want_base,want_part,want_filter;
static const int installation_phases[9]={169,207,245,273,275,277,279,281,283};
static int phase_under_test=-1;
static void asset_debug_reference(const char*a,const char*b,int c,unsigned d,int e,int f,int g,int h)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;(void)h;abort();}
static bool render_mirror_enemy_tile(SDL_Surface*surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter)
{
 assert(surface==VGAScreen&&bank.data==enemy[0].sprite2s->data);
 assert(x==want_x&&y==want_y&&(int)base==want_base&&part==want_part&&filter==want_filter);
 assert(mirror_calls==0&&original_calls==0&&end_calls==0);mirror_calls++;suppressed=mirror_result;return mirror_result;
}
static void asset_debug_effect(SDL_Surface*surface,Sprite2_array bank,unsigned index,int x,int y)
{
 assert(surface==VGAScreen&&bank.data==enemy[0].sprite2s->data);
 assert(index==(unsigned)(want_base+want_part)&&x==want_x&&y==want_y);
 assert(mirror_calls==1&&original_calls==0&&end_calls==0);original_calls++;
}
static void render_mirror_pixel(SDL_Surface*surface,Uint8*address,Uint8 value,int style)
{assert(surface==VGAScreen&&*address==value&&style==MIRROR_NORMAL);assert(original_calls==1&&end_calls==0&&suppressed==mirror_result);pixel_calls++;}
static void render_mirror_entity_end(void)
{assert(mirror_calls==1&&original_calls==1&&end_calls==0);end_calls++;suppressed=false;}
#include "blitters.inc"
#include "wrapper.inc"
static unsigned long long checks;
static void exercise(int base,int part,int filter,int x,int y,bool mirrored)
{
 Uint8 expected[64*64];memset(expected,17,sizeof(expected));memset(VGAScreen->pixels,17,sizeof(expected));
 want_x=x;want_y=y;want_base=base;want_part=part;want_filter=filter;
 mirror_calls=original_calls=end_calls=pixel_calls=0;mirror_result=mirrored;suppressed=false;
 enemy[0].ex=x+6-3;enemy[0].ey=y+7;tempMapXOfs=3;
 if(phase_under_test<0){enemy[0].enemycycle=4;enemy[0].egr[3]=base;}
 else {memcpy(enemy[0].egr,installation_phases,sizeof(installation_phases));enemy[0].enemycycle=phase_under_test+1;assert(base==installation_phases[phase_under_test]);}
 enemy[0].filter=filter;
 struct Enemy before=enemy[0];
 unsigned expected_writes=0;
 for(int ay=0;ay<14;ay++)for(int ax=0;ax<12;ax++){
  int dy=y+ay,dx=x+ax,id=base+part;
  if(dy<0||dy>=64||(ax+ay+id)%5==0)continue;
  Uint8 value=(Uint8)((id+3*ax+7*ay)%240+1);
  expected[dy*64+dx]=filter?(Uint8)(filter|(value&15)):value;expected_writes++;
 }
 blit_enemy(VGAScreen,0,-6,-7,part);
 assert(!memcmp(&before,&enemy[0],sizeof(before)));
 assert(mirror_calls==1&&original_calls==1&&end_calls==1&&!suppressed&&pixel_calls==expected_writes);
 assert(!memcmp(expected,VGAScreen->pixels,sizeof(expected)));checks++;
}
int main(int argc,char**argv)
{
 assert(argc==2);char path[2048];snprintf(path,sizeof(path),"%s/synthetic-original-bank.bin",argv[1]);
 FILE*f=fopen(path,"rb");assert(f);fseek(f,0,SEEK_END);long len=ftell(f);rewind(f);
 Sprite2_array bank={(size_t)len,malloc((size_t)len)};assert(bank.data);assert(fread(bank.data,1,bank.size,f)==bank.size);fclose(f);
 SDL_PixelFormat format={8};SDL_Surface screen={64,64,64,calloc(64*64,1),&format};VGAScreen=&screen;
 enemy[0].sprite2s=&bank;enemySpriteSheets[0]=bank;enemySpriteSheetIds[0]=9;
 const int ids[]={49,51,89,127,1,3,5,39,41,43,7,9,11,45,47,49,77,79,115,117,85,87,123,125,191,193,195,197,199,201,203,205,229,231,233,235,237,239,241,243,81,83,119,121,267,269,271,153,155,157,169,207,245,273,275,277,279,281,283};
 for(unsigned j=0;j<sizeof(ids)/sizeof(*ids);j++)for(int k=0;k<4;k++)for(int filter=0;filter<256;filter++)for(int mirrored=0;mirrored<2;mirrored++){
  enemySpriteSheetIds[0]=(j>=4&&j<16)?9:1;
  int part=(int[]){0,1,19,20}[k],hue=filter;
  exercise(ids[j],part,hue,5,7,mirrored);exercise(ids[j],part,hue,5,60,mirrored);exercise(ids[j],part,hue,5,-10,mirrored);
 }
 enemySpriteSheetIds[0]=1;
 for(phase_under_test=0;phase_under_test<9;phase_under_test++)for(int k=0;k<4;k++)for(int filter=0;filter<256;filter++)for(int mirrored=0;mirrored<2;mirrored++)
  exercise(installation_phases[phase_under_test],(int[]){0,1,19,20}[k],filter,5,7,mirrored);
 free(bank.data);free(screen.pixels);
 printf("PASS %llu production wrapper cases: all59 bindings/all quadrants/all256 filters and caller-selected nine-base wrapper sequence; original indexed filtered/unfiltered bytes exact, HD success/fallback, upper/lower-edge clipping, original blit once, end once, no enemy-state mutation\n",checks);return 0;
}
