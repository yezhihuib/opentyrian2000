/* SPDX-License-Identifier: GPL-2.0-or-later
 * Current production green compositor; identity boundary is explicitly stubbed.
 * Actual native allocator/identity and engine equivalence have separate tests. */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef struct{int x,y,w,h;}SDL_Rect;
typedef struct{unsigned format;int BitsPerPixel,BytesPerPixel;}SDL_PixelFormat;
typedef struct{int w,h,pitch;void*pixels;SDL_PixelFormat*format;SDL_Rect clip_rect;}SDL_Surface;
typedef struct{size_t size;Uint8*data;}Sprite2_array;
typedef struct{bool initialized,valid;int bank,index,w,h,anchor_x,anchor_y,density;Uint8*rgba;}Asset;
typedef struct{Asset*asset;int x,y;}GreenHead;
typedef struct{Uint16 peak[16][14];}GreenBackground;
enum{SDL_PIXELFORMAT_INDEX8=1,SDL_PIXELFORMAT_ARGB8888=2};
enum{MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
typedef enum{MIRROR_OUTPUT_UNSUPPORTED,MIRROR_OUTPUT_ORDINARY,MIRROR_OUTPUT_NORMAL15_NIGHT,MIRROR_OUTPUT_NORMAL15_LOW_DETAIL}MirrorOutputKind;
#define COUNTOF(x) (sizeof(x)/sizeof(*(x)))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX_EXPLOSIONS 200
typedef int16_t JE_integer;typedef uint16_t JE_word;
typedef struct{Uint8 ttl;JE_integer x,y;JE_word sprite;bool followPlayer,fixedPosition;JE_integer deltaY;}Explosion;
static Explosion explosions[MAX_EXPLOSIONS];static JE_word explodeMove;
static uint64_t checks,cases,alpha_zero_native;
#define CHECK(c) do{++checks;if(!(c)){fprintf(stderr,"CHECK %s:%d: %s\n",__FILE__,__LINE__,#c);abort();}}while(0)
static SDL_Surface *canvas,*output,*game_screen,*VGAScreenSeg,*fade_saved;
static Sprite2_array spriteSheet8,explosionSpriteSheet,spriteSheet9;
static Uint8 *hd_owner,*cloud_owner,*green_under_owner,*global_green_owner,*global_green_foreign;
static Uint8 *global_talon_owner,*global_talon_foreign,*global_shield_owner,*global_shield_foreign,*global_pulse_owner,*global_pulse_foreign,*global_vulcan_owner,*global_vulcan_foreign,*global_hitflare_owner,*global_hitflare_foreign,*global_smoke_owner,*global_smoke_foreign,*global_small_explosion_owner,*global_small_explosion_foreign,*global_cash25_owner,*global_cash25_foreign,*global_rotor_owner,*global_rotor_foreign;
static Uint16 *green_first;static Uint32 *green_under;
static GreenHead green_heads[256];static unsigned green_head_count;
static Uint32 rgb_palette[256],normal_palette[256],fade_saved_palette[256];
static Uint8 expected[64000],selected[64000],last_output_indices[64000];
static bool global_green_frame,global_green_fault,global_talon_fault,active,shared_hud_frame,ready,last_output_valid,last_output_scene_hd,have_fade_saved,suppress;
static bool game_probe_original_reference,game_probe_missing,game_probe_invalid;
static int game_probe_density,fade_mode;static unsigned draws;static uint64_t mirror_logic_tick;
static char global_asset_directory[1024];static const char*reject_reason;
static bool global_talon_source_matches(Sprite2_array b){(void)b;return true;}
static bool global_talon_palette_matches(void){return true;}
static bool normal15_palette(void){return false;}
static bool normal15_indices_match(MirrorOutputKind k,int x,int y){return false;}
static unsigned normal15_index(unsigned c,int x,int y,int lx,int ly){return c;}
static Uint32 normal15_rgba(Uint32 c,Uint8 b,Uint8 a,bool n){return c;}
static int normal15_branch(int x,int y,int lx,int ly){return 0;}
static void font_before_effect(SDL_Rect r){}
static void render_mirror_unsupported(const char*s){reject_reason=s;}
#include "global_asset_registry.h"
#include "primitives.inc"
#include "resource.inc"
#include "global_green_mirror.inc"
static Uint8 *bank_backup[2];static Uint8 *art[11];static const char*root,*fixtures;
static Uint32 *pixel(int x,int y){return (Uint32*)((Uint8*)canvas->pixels+y*canvas->pitch)+x;}
static SDL_Surface *surface(int w,int h,int bpp){SDL_Surface*s=calloc(1,sizeof(*s));CHECK(s);s->w=w;s->h=h;s->pitch=w*bpp/8;s->pixels=calloc(h,s->pitch);s->format=calloc(1,sizeof(*s->format));CHECK(s->pixels&&s->format);s->format->format=bpp==8?SDL_PIXELFORMAT_INDEX8:SDL_PIXELFORMAT_ARGB8888;s->format->BitsPerPixel=bpp;s->format->BytesPerPixel=bpp/8;s->clip_rect=(SDL_Rect){0,0,w,h};return s;}
static void destroy(SDL_Surface*s){if(s){free(s->pixels);free(s->format);free(s);}}
static void read_exact(void*p,size_t n){CHECK(fread(p,1,n,stdin)==n);}
static void load(void){Sprite2_array*b[2]={&spriteSheet8,&explosionSpriteSheet};for(int i=0;i<2;i++){Uint32 n;read_exact(&n,4);b[i]->data=malloc(n);b[i]->size=n;read_exact(b[i]->data,n);bank_backup[i]=malloc(n);memcpy(bank_backup[i],b[i]->data,n);}read_exact(normal_palette,sizeof(normal_palette));CHECK(fgetc(stdin)==EOF);
 for(unsigned i=0;i<11;i++){const GlobalAssetResource*r=NULL;for(unsigned j=0;j<GLOBAL_ASSET_RESOURCE_COUNT;j++)if(global_asset_resources[j].identity==global_green_resource_ids[i])r=global_asset_resources+j;CHECK(r);char p[2048];snprintf(p,sizeof(p),"%s/%s",root,r->path);FILE*f=fopen(p,"rb");CHECK(f);CHECK(!fseek(f,28,SEEK_SET));art[i]=malloc(43008);CHECK(fread(art[i],1,43008,f)==43008&&fgetc(f)==EOF);fclose(f);}}
static Uint32 alpha(Uint32 c,const Uint8*a){unsigned q=a[3],r=((c>>16)&255)*(255-q)+a[0]*q,g=((c>>8)&255)*(255-q)+a[1]*q,b=(c&255)*(255-q)+a[2]*q;return 0xff000000u|((r+127)/255<<16)|((g+127)/255<<8)|(b+127)/255;}
static Uint32 blend(Uint32 c,const Uint8*a,unsigned peak){unsigned s=MAX(a[0],MAX(a[1],a[2]));Uint8 b[4]={0,0,0,a[3]};if(s){unsigned target=(s+peak+1)/2;for(unsigned i=0;i<3;i++)b[i]=(a[i]*target+s/2)/s;}return alpha(c,b);}
static unsigned peak(Uint32 c){return MAX((c>>16)&255,MAX((c>>8)&255,c&255));}
static void setup(const char*path,int d){++cases;global_green_shutdown();destroy(canvas);destroy(output);destroy(game_screen);destroy(VGAScreenSeg);destroy(fade_saved);fade_saved=NULL;free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);game_probe_density=d;canvas=surface(320*d,200*d,32);output=surface(320*d,200*d,32);game_screen=surface(320,200,8);VGAScreenSeg=surface(320,200,8);size_t n=(size_t)canvas->w*canvas->h;hd_owner=calloc(n,1);cloud_owner=calloc(n,1);green_first=calloc(n,2);green_under=calloc(n,4);green_under_owner=calloc(n,1);CHECK(hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);green_head_count=0;memcpy(spriteSheet8.data,bank_backup[0],spriteSheet8.size);memcpy(explosionSpriteSheet.data,bank_backup[1],explosionSpriteSheet.size);memcpy(rgb_palette,normal_palette,sizeof(rgb_palette));memset(explosions,0,sizeof(explosions));game_probe_missing=game_probe_invalid=game_probe_original_reference=false;ready=last_output_valid=have_fade_saved=false;fade_mode=0;active=true;suppress=false;reject_reason=NULL;global_talon_fault=false;snprintf(global_asset_directory,sizeof(global_asset_directory),"%s",path);for(int y=0;y<200;y++)for(int x=0;x<320;x++){Uint8 v=(Uint8)(16+(x*3+y*5)%16);((Uint8*)game_screen->pixels)[y*320+x]=expected[y*320+x]=v;((Uint8*)VGAScreenSeg->pixels)[y*320+x]=v;for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)*pixel(x*d+sx,y*d+sy)=0xff000000u|rgb_palette[v];}++mirror_logic_tick;global_green_frame_begin();CHECK(global_green_frame);}
static void emit(int x,int y,Sprite2_array bank,unsigned index,int style){Uint8 c[168]={0},m[168]={0};CHECK(decode_tile(bank,index,c,m,12,0,0));for(int a=0;a<168;a++)if(m[a]){int px=x+a%12,py=y+a/12;if(px<0||py<0||px>=320||py>=200)continue;Uint8 *v=(Uint8*)game_screen->pixels+py*320+px,b=*v;*v=style==MIRROR_NORMAL?c[a]:(c[a]&240)|(((c[a]&15)+(b&15))/2);expected[py*320+px]=*v;CHECK(global_green_pixel(px,py,b,*v,style));}global_green_end();CHECK(!global_green_fault);}
static void draw(unsigned p,int x,int y,int style){CHECK(global_green_family_ready());CHECK(global_green_draw(x,y,p<4?spriteSheet8:explosionSpriteSheet,p<4?214+p:78+p-4,style,p,p<4)==1);emit(x,y,p<4?spriteSheet8:explosionSpriteSheet,p<4?214+p:78+p-4,style);}
/* Independent complete subpixel state, never reads production saved underlays. */
static Uint32 *oracle,*under;static Uint8 *owned,*uowned;static unsigned *first;static struct{unsigned phase;int x,y;} heads[256];static unsigned headn;
static void oracle_start(void){size_t n=(size_t)canvas->w*canvas->h;free(oracle);free(under);free(owned);free(uowned);free(first);oracle=malloc(n*4);under=calloc(n,4);owned=calloc(n,1);uowned=calloc(n,1);first=calloc(n,sizeof(*first));CHECK(oracle&&under&&owned&&uowned&&first);for(int y=0;y<canvas->h;y++)memcpy(oracle+(size_t)y*canvas->w,pixel(0,y),canvas->w*4);headn=0;}
static void oracle_draw(unsigned phase,int x,int y,int style){int d=game_probe_density,w=canvas->w;bool head=phase<4;unsigned grid[16][14];if(head){heads[headn].phase=phase;heads[headn].x=x;heads[headn++].y=y;}
 if(!head&&style==MIRROR_BLEND)for(int yy=0;yy<16;yy++)for(int xx=0;xx<14;xx++){int px=(x+xx-1)*d+d/2,py=(y+yy-1)*d+d/2;unsigned q=256;if(px>=0&&py>=0&&px<w&&py<canvas->h){size_t k=(size_t)py*w+px;if(!(first[k]?uowned[k]:owned[k]))q=peak(first[k]?under[k]:oracle[k]);}grid[yy][xx]=q;}
 Uint8 c[168]={0},m[168]={0};CHECK(decode_tile(head?spriteSheet8:explosionSpriteSheet,head?214+phase:74+phase,c,m,12,0,0));
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++){int px=x*d+ax,py=y*d+ay;if(px<0||py<0||px>=w||py>=canvas->h)continue;size_t n=(size_t)py*w+px;const Uint8*a=art[phase]+4*((ay*8/d)*96+ax*8/d);bool native=m[(ay/d)*12+ax/d];if(!a[3]&&!native)continue;if(!a[3]&&native)++alpha_zero_native;if(head&&a[3]&&!first[n]){first[n]=headn;under[n]=oracle[n];uowned[n]=owned[n];}bool protected=!head&&first[n];if(a[3]){Uint32 dst=protected?under[n]:oracle[n];unsigned brightness=peak(dst);if(!head&&style==MIRROR_BLEND&&!(protected?uowned[n]:owned[n])){int den=2*d,wx=2*(ax%d)+1-d,wy=2*(ay%d)+1-d,bx=ax/d+1,by=ay/d+1;if(wx<0){--bx;wx+=den;}if(wy<0){--by;wy+=den;}unsigned total=0;for(int j=0;j<2;j++)for(int i=0;i<2;i++){unsigned tap=grid[by+j][bx+i];if(tap==256)tap=brightness;total+=tap*(i?wx:den-wx)*(j?wy:den-wy);}brightness=(total+den*den/2)/(den*den);}Uint32 out=!head&&style==MIRROR_BLEND?blend(dst,a,brightness):alpha(dst,a);if(protected){under[n]=out;uowned[n]=1;for(unsigned i=first[n]-1;i<headn;i++){int hx=px-heads[i].x*d,hy=py-heads[i].y*d;if(hx>=0&&hy>=0&&hx<12*d&&hy<14*d)out=alpha(out,art[heads[i].phase]+4*((hy*8/d)*96+hx*8/d));}}oracle[n]=out;}if(protected&&native)uowned[n]=1;owned[n]=1;}}
static void compare(int x,int y,int ww,int hh){int d=game_probe_density;for(int yy=MAX(0,y*d);yy<MIN(canvas->h,(y+hh)*d);yy++)for(int xx=MAX(0,x*d);xx<MIN(canvas->w,(x+ww)*d);xx++){size_t n=(size_t)yy*canvas->w+xx;CHECK(*pixel(xx,yy)==oracle[n]);CHECK(hd_owner[n]==owned[n]);CHECK(green_first[n]==first[n]);if(first[n]){CHECK(green_under[n]==under[n]);CHECK(green_under_owner[n]==uowned[n]);}}}
static void composition(void){for(int d=4;d<=8;d+=4)for(int style=0;style<2;style++)for(int edge=0;edge<3;edge++){setup(root,d);oracle_start();int x=edge==1?-4:edge==2?313:105,y=edge==1?-6:edge==2?193:77;unsigned seq[]={0,1,4,5,2,6,7,3,8,9,10,4};for(unsigned i=0;i<COUNTOF(seq);i++){int ox=(i%3)-1,oy=(i%2);oracle_draw(seq[i],x+ox,y+oy,seq[i]<4?0:style);draw(seq[i],x+ox,y+oy,seq[i]<4?0:style);compare(x-2,y-1,18,18);}CHECK(global_green_finish_proof());}}
static void resources(void){char p[2048];const char*modes[]={"missing","corrupt","header","trailing"};for(unsigned mode=0;mode<4;mode++)for(unsigned phase=0;phase<11;phase++){snprintf(p,sizeof(p),"%s/%s%u",fixtures,modes[mode],phase);setup(p,4);CHECK(!global_green_family_ready());for(unsigned i=0;i<11;i++)CHECK(!global_green_rgba[i]);}}
static void final_copy(void){for(int y=0;y<184;y++)memcpy((Uint8*)VGAScreenSeg->pixels+y*320,(Uint8*)game_screen->pixels+y*320+24,264);memcpy(last_output_indices,VGAScreenSeg->pixels,64000);}
static void invalidation(void){for(unsigned bad=0;bad<10;bad++){setup(root,4);draw(0,105,77,0);CHECK(global_green_contributed);size_t n=(size_t)canvas->w*canvas->h;memset(global_green_owner,0,n);memset(global_green_foreign,0,n);Uint8*save=NULL;unsigned z=0;switch(bad){case 0:game_probe_missing=true;break;case 1:game_probe_invalid=true;break;case 2:game_probe_original_reference=true;break;case 3:rgb_palette[33]^=1;break;case 4:global_green_identity_fault=true;break;case 5:game_screen->pitch++;break;case 6:VGAScreenSeg->pitch++;break;case 7:canvas->pitch+=4;break;case 8:save=spriteSheet8.data;spriteSheet8.data=NULL;break;case 9:save=explosionSpriteSheet.data;explosionSpriteSheet.data=NULL;break;}global_green_preflight();switch(bad){case 0:game_probe_missing=false;break;case 1:game_probe_invalid=false;break;case 2:game_probe_original_reference=false;break;case 3:rgb_palette[33]^=1;break;case 4:global_green_identity_fault=false;break;case 5:game_screen->pitch--;break;case 6:VGAScreenSeg->pitch--;break;case 7:canvas->pitch-=4;break;case 8:spriteSheet8.data=save;break;case 9:explosionSpriteSheet.data=save;break;}CHECK(global_green_fault&&!global_green_finish_proof());}
 setup(root,4);draw(0,105,77,0);global_green_call.live=true;global_green_call.left=1;global_green_end();CHECK(global_green_fault&&!global_green_finish_proof());
 setup(root,4);draw(0,105,77,0);final_copy();CHECK(global_green_compose(MIRROR_OUTPUT_ORDINARY,0,0));CHECK(global_green_cached);rgb_palette[1]^=1;global_green_check_cache();CHECK(!global_green_cached&&!ready);
 setup(root,4);draw(0,105,77,0);final_copy();CHECK(global_green_compose(MIRROR_OUTPUT_ORDINARY,0,0));fade_saved=surface(320*4,200*4,32);fade_mode=1;CHECK(global_green_fade_capture());have_fade_saved=true;for(unsigned i=0;i<256;i++){Uint32 c=rgb_palette[i],o=0;for(int b=0;b<24;b+=8){int v=(c>>b)&255;o|=(Uint32)(v-v/3)<<b;}rgb_palette[i]=o;}CHECK(global_green_fade_step_valid(3));global_green_fade_palette();fade_saved->pitch+=4;CHECK(!global_green_fade_step_valid(3));fade_saved->pitch-=4;
}
static void smoke_slot_guards(void){
 setup(root,4);render_mirror_green_smoke_allocated(0,12,105,77,0,false,false);explosions[0]=(Explosion){7,105,77,76,false,false,0};render_mirror_green_smoke_initialized(0,12);CHECK(global_green_slots[0].role);
 for(unsigned ttl=7;ttl;ttl--){++mirror_logic_tick;explosions[0].ttl=ttl;explosions[0].sprite=84-ttl;CHECK(render_mirror_global_green_smoke(game_screen,105,77,explosionSpriteSheet,85-ttl,MIRROR_BLEND,0)==1);emit(105,77,explosionSpriteSheet,85-ttl,MIRROR_BLEND);}CHECK(global_green_finish_proof());
 CHECK(render_mirror_global_green_smoke(game_screen,105,77,explosionSpriteSheet,84,MIRROR_BLEND,0)==0);CHECK(global_green_fault);
 setup(root,4);render_mirror_green_smoke_allocated(0,6,105,77,0,false,false);explosions[0]=(Explosion){7,105,77,76,false,false,0};render_mirror_green_smoke_initialized(0,12);CHECK(!global_green_slots[0].role);CHECK(render_mirror_global_green_smoke(game_screen,105,77,explosionSpriteSheet,78,0,0)==-1);
 setup(root,4);render_mirror_green_smoke_allocated(0,12,105,77,0,false,false);explosions[0]=(Explosion){7,105,77,76,false,false,0};render_mirror_green_smoke_initialized(0,12);draw(0,105,77,0);++mirror_logic_tick;explosions[0].sprite=77;global_green_slots[0].generation++;CHECK(render_mirror_global_green_smoke(game_screen,105,77,explosionSpriteSheet,78,0,0)==0);CHECK(global_green_fault&&!global_green_finish_proof());
}
static void foreign_and_wrappers(void){
 setup(root,4);CHECK(render_mirror_global_green_head(game_screen,105,77,spriteSheet8,214,MIRROR_SHADOW,0,714)==0);CHECK(!global_green_contributed);
 CHECK(render_mirror_global_green_head(game_screen,105,77,spriteSheet8,214,MIRROR_NORMAL,0,714)==1);emit(105,77,spriteSheet8,214,0);
 int x=-1,y=-1;for(int yy=77;yy<91&&x<0;yy++)for(int xx=105;xx<117;xx++)if(green_first[(yy*4)*canvas->w+xx*4]){x=xx;y=yy;break;}CHECK(x>=0);
 Uint8 before=((Uint8*)game_screen->pixels)[y*320+x];CHECK(!global_green_pixel(x,y,before,(before&240)|((before&15)/2),MIRROR_SHADOW));CHECK(global_green_owner[(y*4)*canvas->w+x*4]);
 CHECK(!global_green_pixel(x,y,before,99,MIRROR_NORMAL));for(int yy=0;yy<4;yy++)for(int xx=0;xx<4;xx++){size_t n=(y*4+yy)*canvas->w+x*4+xx;CHECK(!global_green_owner[n]&&!green_first[n]);}
 setup(root,4);oracle_start();size_t n=(size_t)canvas->w*canvas->h;for(size_t i=0;i<n;i++){hd_owner[i]=owned[i]=1;((Uint32*)canvas->pixels)[i]=oracle[i]=0xffa731d2u;}oracle_draw(0,105,77,0);draw(0,105,77,0);oracle_draw(4,106,78,1);draw(4,106,78,1);compare(103,75,18,18);CHECK(global_green_finish_proof());bool foreign_seen=false;for(size_t i=0;i<n;i++)foreign_seen|=global_green_foreign[i]!=0;CHECK(foreign_seen);rgb_palette[240]^=1;global_green_preflight();rgb_palette[240]^=1;CHECK(global_green_fault&&!global_green_finish_proof());
}
int main(int argc,char**argv){CHECK(argc==3);root=argv[1];fixtures=argv[2];load();composition();resources();invalidation();smoke_slot_guards();foreign_and_wrappers();CHECK(alpha_zero_native>0);printf("Green renderer PASS: %llu cases, %llu checks\n",(unsigned long long)cases,(unsigned long long)checks);return 0;}
