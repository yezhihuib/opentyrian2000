/* Actual production module, synthetic sources and SDL software rendering only.
 * No original artwork, input injection, game entrypoint, or game execution.
 */
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "SDL.h"

static unsigned opens, reads, allocs, creates, destroys, presents;
static int fail_open, fail_stat, fail_read, short_read, fail_close, fail_alloc, fail_sdl;
static struct { void *p; size_t bytes; } allocations[16];
static size_t live_bytes, peak_bytes, gpu_live_bytes, gpu_peak_bytes;
static int checked_open(const char *p,int flags) { ++opens; return fail_open?-1:open(p,flags); }
static int checked_stat(int f,struct stat *s) { return fail_stat?-1:fstat(f,s); }
static ssize_t checked_read(int f,void *p,size_t n)
{
 assert(n<=4096000);++reads; if((int)reads==fail_read){errno=EINTR;return -1;}
 return read(f,p,n-((int)reads==short_read && n>0));
}
static int checked_close(int f) { int result=close(f); return fail_close?-1:result; }
static void *checked_malloc(size_t n)
{
 ++allocs; if((int)allocs==fail_alloc)return NULL;
 void *p=malloc(n);if(!p)return NULL;
 for(unsigned i=0;i<16;i++)if(!allocations[i].p){allocations[i].p=p;allocations[i].bytes=n;live_bytes+=n;if(live_bytes>peak_bytes)peak_bytes=live_bytes;return p;}
 assert(!"Production allocation ledger exhausted"); return NULL;
}
static void checked_free(void *p)
{
 if(!p)return;
 for(unsigned i=0;i<16;i++)if(allocations[i].p==p){live_bytes-=allocations[i].bytes;allocations[i].p=NULL;free(p);return;}
 assert(!"Free did not match production allocation");
}
static SDL_Texture *checked_create(SDL_Renderer *r,Uint32 f,int a,int w,int h)
{
 ++creates;if(fail_sdl==1)return NULL;
 SDL_Texture *t=SDL_CreateTexture(r,f,a,w,h);
 if(t){assert(!gpu_live_bytes);gpu_live_bytes=(size_t)w*h*4;if(gpu_live_bytes>gpu_peak_bytes)gpu_peak_bytes=gpu_live_bytes;}
 return t;
}
static int checked_scale(SDL_Texture *t,SDL_ScaleMode m){return fail_sdl==2?-1:SDL_SetTextureScaleMode(t,m);}
static int checked_blend(SDL_Texture *t,SDL_BlendMode m){return fail_sdl==3?-1:SDL_SetTextureBlendMode(t,m);}
static int checked_update(SDL_Texture *t,const SDL_Rect *r,const void *p,int pitch){return fail_sdl==4?-1:SDL_UpdateTexture(t,r,p,pitch);}
static int checked_color(SDL_Renderer *r,Uint8 a,Uint8 b,Uint8 c,Uint8 d){return fail_sdl==5?-1:SDL_SetRenderDrawColor(r,a,b,c,d);}
static int checked_clear(SDL_Renderer *r){return fail_sdl==6?-1:SDL_RenderClear(r);}
static int checked_copy(SDL_Renderer *r,SDL_Texture *t,const SDL_Rect *s,const SDL_Rect *d){return fail_sdl==7?-1:SDL_RenderCopy(r,t,s,d);}
static void checked_destroy(SDL_Texture *t){++destroys;assert(gpu_live_bytes);gpu_live_bytes=0;SDL_DestroyTexture(t);}
static void checked_present(SDL_Renderer *r){++presents;SDL_RenderPresent(r);}
#define open checked_open
#define fstat checked_stat
#define read checked_read
#define close checked_close
#define malloc checked_malloc
#define free checked_free
#define SDL_CreateTexture checked_create
#define SDL_SetTextureScaleMode checked_scale
#define SDL_SetTextureBlendMode checked_blend
#define SDL_UpdateTexture checked_update
#define SDL_SetRenderDrawColor checked_color
#define SDL_RenderClear checked_clear
#define SDL_RenderCopy checked_copy
#define SDL_DestroyTexture checked_destroy
#define SDL_RenderPresent checked_present
#include "title_layers.c"
#undef open
#undef fstat
#undef read
#undef close
#undef malloc
#undef free
#undef SDL_CreateTexture
#undef SDL_SetTextureScaleMode
#undef SDL_SetTextureBlendMode
#undef SDL_UpdateTexture
#undef SDL_SetRenderDrawColor
#undef SDL_RenderClear
#undef SDL_RenderCopy
#undef SDL_DestroyTexture
#undef SDL_RenderPresent
#define resources output_resources
#include "selector_font_output.c"
#undef resources

SDL_Surface *VGAScreen,*VGAScreenSeg,*VGAScreen2;
SDL_PixelFormat *main_window_tex_format;
Uint32 rgb_palette[256];
Sprite_array sprite_table[SPRITE_TABLES_MAX];
#ifndef TITLE_MENU_TEST_FONT
const int font_ascii[256]={0}; /* This suite never supplies the optional font. */
#endif
static SDL_Surface *display;
static SDL_Renderer *renderer;
static SDL_Rect destination={0,0,1280,800};
static const char *directory;
static char paths[3][2048];
static Uint8 pic_source[64000], logo_indices[2][304*121], logo_masks[2][304*121], logo_rle[2][65535];
static Uint8 *resources[3];
static const unsigned ids[3]={4,146,151}, widths[3]={320,304,162}, heights[3]={200,121,64};
static const char *names[3]={"title-pic4-v1.hda","title-planet146-v1.hda","title-planet151-v1.hda"};
static size_t sizes[3];
static SDL_Color target_palette[256], engine_palette[256];
static Uint8 oracle_lut[256], plane_value[3][64000],plane_mask[3][64000], saved_menu_value[64000],saved_menu_mask[64000];
static int pose_x[2],pose_y[2];
static unsigned visible_logos, available=7;
static const uint64_t fnv_seed=UINT64_C(14695981039346656037);
static uint64_t hash_bytes(const void *data,size_t n)
{ const Uint8 *p=data;uint64_t h=fnv_seed;for(size_t i=0;i<n;i++)h=(h^p[i])*UINT64_C(1099511628211);return h; }
static void put32(Uint8 *p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(Uint8)(v>>(8*i));}
static void put64(Uint8 *p,uint64_t v){for(unsigned i=0;i<8;i++)p[i]=(Uint8)(v>>(8*i));}
static void reset_faults(void){fail_open=fail_stat=fail_read=short_read=fail_close=fail_alloc=fail_sdl=0;opens=reads=allocs=0;}
static void write_resource(unsigned k,const void *data,size_t n)
{FILE *f=fopen(paths[k],"wb");assert(f);assert(fwrite(data,1,n,f)==n);assert(!fclose(f));}
static void rehash(Uint8 *data,size_t n){put64(data+72,hash_bytes(data+80,n-80));}
static void make_fixture(unsigned l)
{
 unsigned id=ids[l+1],w=widths[l+1],h=heights[l+1],n=0;
 for(unsigned y=0;y<h;y++) {
  if(y<2||y>=h-2){logo_rle[l][n++]=254;continue;}
  logo_rle[l][n++]=255;logo_rle[l][n++]=2;
  for(unsigned x=2;x<w-2;x++) {
   unsigned p=y*w+x;
   if((x+y)%19==0)logo_rle[l][n++]=253;
   else {logo_indices[l][p]=(Uint8)((x*7+y*11+id)%239);logo_masks[l][p]=255;logo_rle[l][n++]=logo_indices[l][p];}
  }
  logo_rle[l][n++]=254;
 }
 sprite_table[PLANET_SHAPES].sprite[id]=(Sprite){(Uint16)w,(Uint16)h,(Uint16)n,logo_rle[l]};
}
static void pack_resource(unsigned k)
{
 unsigned w=widths[k],h=heights[k];size_t pixels=(size_t)w*h*16;sizes[k]=80+pixels*4;
 Uint8 *p=resources[k]=calloc(1,sizes[k]);assert(p);memcpy(p,"TLV1",4);
 const uint32_t fields[11]={1,4,ids[k],w,h,8,k?1:0,(uint32_t)(pixels*4),0,0,0};
 for(unsigned i=0;i<11;i++)put32(p+4+4*i,fields[i]);
 put64(p+48,k?hash_bytes(logo_indices[k-1],w*h):hash_bytes(pic_source,64000));
 if(k)put64(p+56,hash_bytes(logo_masks[k-1],w*h));
 else {Uint8 mask[64000];memset(mask,255,sizeof(mask));put64(p+56,hash_bytes(mask,sizeof(mask)));}
 Uint8 palette[768];for(unsigned i=0;i<256;i++){palette[3*i]=target_palette[i].r;palette[3*i+1]=target_palette[i].g;palette[3*i+2]=target_palette[i].b;}
 put64(p+64,hash_bytes(palette,sizeof(palette)));
 for(unsigned y=0;y<4*h;y++)for(unsigned x=0;x<4*w;x++) {
  Uint8 *q=p+80+4*((size_t)y*4*w+x);unsigned alpha=255;
  if(k){unsigned border=k==1?4:8;alpha=x<border||y<border||x>=4*w-border||y>=4*h-border?0:((x+y)%7==0?0:((const unsigned[]){1,64,127,128,254,255})[(x+2*y)%6]);}
  q[3]=(Uint8)alpha;if(alpha){q[0]=(Uint8)(x*3+y+k*17);q[1]=(Uint8)(x+y*5+k*29);q[2]=(Uint8)(x*7+y*11+k*43);}
 }
 rehash(p,sizes[k]);write_resource(k,p,sizes[k]);
}
static void apply_palette(void)
{for(unsigned i=0;i<256;i++)rgb_palette[i]=SDL_MapRGB(main_window_tex_format,engine_palette[i].r,engine_palette[i].g,engine_palette[i].b);}
static void begin_epoch(bool animate)
{
 title_layers_end();assert(live_bytes==0&&!gpu_live_bytes);reset_faults();
 memcpy(VGAScreen->pixels,pic_source,64000);memset(VGAScreen2->pixels,0xcc,64000);
 for(unsigned i=0;i<256;i++)engine_palette[i]=i<240?(SDL_Color){0,0,0,255}:(SDL_Color){(Uint8)(i+1),(Uint8)(i+2),(Uint8)(i+3),255};
 apply_palette();memset(plane_mask,0,sizeof(plane_mask));memset(oracle_lut,0,sizeof(oracle_lut));visible_logos=0;
 title_layers_begin(VGAScreen,target_palette,animate);
}
static void write_pixel(unsigned plane,unsigned x,unsigned y,Uint8 value,enum TitleWriter writer)
{
 unsigned previous_allocs=allocs,previous_opens=opens,previous_reads=reads;
 unsigned p=y*320+x;assert(p<64000);((Uint8 *)VGAScreen->pixels)[p]=value;
 title_layers_pixel(VGAScreen,(Uint8 *)VGAScreen->pixels+p,writer);
 assert(allocs==previous_allocs&&opens==previous_opens&&reads==previous_reads);
 plane_value[plane][p]=value;plane_mask[plane][p]=1;
}
static void version(void)
{
 /* The first shadow writes the same index: coverage must not be a diff mask. */
 Uint8 same=((Uint8 *)VGAScreen->pixels)[193*320+3];
 write_pixel(0,3,193,same,TITLE_WRITE_SHADOW);
 write_pixel(0,4,193,(Uint8)(((Uint8 *)VGAScreen->pixels)[193*320+4]&0xf0),TITLE_WRITE_SHADOW);
 write_pixel(0,2,192,240,TITLE_WRITE_FONT);write_pixel(0,3,192,255,TITLE_WRITE_FONT);
 title_layers_version_done();
}
static void save_checkpoint(enum TitleCheckpoint checkpoint)
{title_layers_save_before(checkpoint);memcpy(VGAScreen2->pixels,VGAScreen->pixels,64000);title_layers_save_after(checkpoint);}
static void restore_checkpoint(enum TitleCheckpoint checkpoint)
{
 title_layers_restore_before(checkpoint);memcpy(VGAScreen->pixels,VGAScreen2->pixels,64000);title_layers_restore_after(checkpoint);
 if(checkpoint==TITLE_BACKGROUND)visible_logos=0;
 else {memcpy(plane_value[1],saved_menu_value,64000);memcpy(plane_mask[1],saved_menu_mask,64000);memset(plane_mask[2],0,64000);}
}
static void logo(unsigned l,int x,int y)
{
 unsigned w=widths[l+1],h=heights[l+1];title_layers_logo(ids[l+1],x,y);
 for(unsigned j=0;j<h;j++)for(unsigned i=0;i<w;i++)if(logo_masks[l][j*w+i]) {
  unsigned p=(unsigned)(y+(int)j)*320+(unsigned)(x+(int)i);assert(p<64000);
  ((Uint8 *)VGAScreen->pixels)[p]=logo_indices[l][j*w+i];
  title_layers_pixel(VGAScreen,(Uint8 *)VGAScreen->pixels+p,TITLE_WRITE_LOGO);
 }
 pose_x[l]=x;pose_y[l]=y;visible_logos|=1u<<l;
}
static Uint32 palette_pixel(unsigned index)
{return UINT32_C(0xff000000)|((Uint32)engine_palette[index].r<<16)|((Uint32)engine_palette[index].g<<8)|engine_palette[index].b;}
static Uint32 blend_pixel(Uint32 dest,const Uint8 *rgba)
{
 Uint32 value=UINT32_C(0xff000000);unsigned a=rgba[3];
 for(unsigned c=0;c<3;c++){unsigned shift=16-8*c;unsigned s=oracle_lut[rgba[c]],d=(dest>>shift)&255;value|=((s*a+d*(255-a)+127)/255)<<shift;}
 return value;
}
static Uint32 expected_pixel(unsigned x,unsigned y)
{
 unsigned p=(y/4)*320+x/4;Uint32 value;
 if(available&1)value=blend_pixel(UINT32_C(0xff000000),resources[0]+80+4*((size_t)y*1280+x));
 else value=palette_pixel(pic_source[p]);
 if(plane_mask[0][p])value=palette_pixel(plane_value[0][p]);
 for(unsigned l=0;l<2;l++)if(visible_logos&(1u<<l)) {
  int lx=(int)x-pose_x[l]*4,ly=(int)y-pose_y[l]*4;unsigned w=widths[l+1],h=heights[l+1];
  if(lx>=0&&ly>=0&&(unsigned)lx<w*4&&(unsigned)ly<h*4) {
   if(available&(2u<<l))value=blend_pixel(value,resources[l+1]+80+4*((size_t)ly*w*4+(unsigned)lx));
   else {unsigned q=((unsigned)ly/4)*w+(unsigned)lx/4;if(logo_masks[l][q])value=palette_pixel(logo_indices[l][q]);}
  }
 }
 for(unsigned plane=1;plane<3;plane++)if(plane_mask[plane][p])value=palette_pixel(plane_value[plane][p]);
 return value;
}
static void check_present(bool full)
{
 Uint8 screen[64000],checkpoint[64000];Uint32 palette[256];
 memcpy(screen,VGAScreen->pixels,64000);memcpy(checkpoint,VGAScreen2->pixels,64000);memcpy(palette,rgb_palette,sizeof(palette));
 unsigned allocations_before=allocs,reads_before=reads,opens_before=opens,presents_before=presents;
 assert(title_layers_present(renderer,VGAScreen,&destination));
 assert(allocs==allocations_before&&reads==reads_before&&opens==opens_before&&presents==presents_before+1);
 assert(!memcmp(screen,VGAScreen->pixels,64000)&&!memcmp(checkpoint,VGAScreen2->pixels,64000)&&!memcmp(palette,rgb_palette,sizeof(palette)));
 for(unsigned y=0;y<800;y+=full?1:23)for(unsigned x=0;x<1280;x+=full?1:19){
  Uint32 got=((Uint32 *)((Uint8 *)display->pixels+(size_t)y*display->pitch))[x];Uint32 want=expected_pixel(x,y);
  if(got!=want){fprintf(stderr,"Pixel mismatch x=%u y=%u got=%08x expected=%08x available=%u\n",x,y,got,want,available);abort();}
 }
}
static void advance_fade(bool outgoing,int steps,unsigned first,unsigned last)
{
 SDL_Color black={0,0,0,255};title_layers_fade_start(outgoing?NULL:target_palette,outgoing?&black:NULL,first,last);
 for(int remaining=steps;remaining>0;--remaining) {
  for(unsigned i=first;i<=last;i++){
   SDL_Color t=outgoing?black:target_palette[i];
   engine_palette[i].r+=(int)(t.r-engine_palette[i].r)/remaining;
   engine_palette[i].g+=(int)(t.g-engine_palette[i].g)/remaining;
   engine_palette[i].b+=(int)(t.b-engine_palette[i].b)/remaining;
  }
  if(outgoing||first==0)for(unsigned i=0;i<256;i++)oracle_lut[i]+=(int)((outgoing?0:(int)i)-oracle_lut[i])/remaining;
  apply_palette();title_layers_fade_step(remaining,first,last);
  if(!outgoing||remaining>1)assert(!memcmp(state.channel,oracle_lut,sizeof(oracle_lut)));
  if(!outgoing||remaining>1)check_present(remaining==1);
 }
 if(outgoing){assert(!title_layers_present(renderer,VGAScreen,&destination));assert(live_bytes==0&&!gpu_live_bytes);}
}
static void initial(bool animate)
{
 begin_epoch(animate);version();if(animate)save_checkpoint(TITLE_BACKGROUND);
 logo(0,11,animate?62:4);logo(1,155,animate?41:73);title_layers_art_ready();advance_fade(false,10,0,239);
}
static void menu(void)
{
 title_layers_menu_begin();
 write_pixel(1,120,104,242,TITLE_WRITE_FONT);write_pixel(1,121,104,249,TITLE_WRITE_FONT);
 write_pixel(1,150,117,240,TITLE_WRITE_FONT);write_pixel(1,152,118,255,TITLE_WRITE_FONT);
 title_layers_menu_done();memcpy(saved_menu_value,plane_value[1],64000);memcpy(saved_menu_mask,plane_mask[1],64000);
 save_checkpoint(TITLE_MENU);advance_fade(false,20,240,255);
}
static void live_cursor(unsigned location,bool restore_full)
{
 restore_checkpoint(TITLE_MENU);
 write_pixel(1,120+(location%2),104,254,TITLE_WRITE_FONT);title_layers_highlight_done();
 Uint8 before[64000];memcpy(before,VGAScreen->pixels,64000);title_layers_cursor_begin();
 unsigned positions[4]={location,location+1,location+320,63999};
 for(unsigned i=0;i<4;i++)if(positions[i]<64000)write_pixel(2,positions[i]%320,positions[i]/320,(Uint8)(240+i),TITLE_WRITE_CURSOR);
 title_layers_cursor_done();check_present(true);
 if(restore_full)memcpy(VGAScreen->pixels,before,64000);
 else {memcpy(VGAScreen->pixels,before,64000);((Uint8 *)VGAScreen->pixels)[5]^=1;}
 title_layers_cursor_erased();memset(plane_mask[2],0,64000);
 if(restore_full)check_present(true);else assert(!title_layers_present(renderer,VGAScreen,&destination));
}
static void test_sequence(void)
{
 available=7;initial(true);
 for(int k=0;k<29;k++){restore_checkpoint(TITLE_BACKGROUND);logo(0,11,60-2*k);logo(1,155,45+k);title_layers_art_ready();check_present(true);}
 menu();live_cursor(100*320+319,true);live_cursor(199*320+318,true);advance_fade(true,10,0,255);
 initial(false);menu();live_cursor(90*320+150,true);advance_fade(true,15,0,255);
 puts("All29poses, direct restart, same-index/shadow UI, source-over, split10/20 and full10/15 fades passed");
}
static size_t expected_cpu(unsigned mask)
{size_t n=4096000;for(unsigned k=0;k<3;k++)if(mask&(1u<<k))n+=sizes[k]-80;return mask?n:0;}
static void test_missing(void)
{
 for(unsigned mask=0;mask<7;mask++) {
  for(unsigned k=0;k<3;k++){if(mask&(1u<<k))write_resource(k,resources[k],sizes[k]);else assert(!unlink(paths[k])||errno==ENOENT);}
  available=mask;begin_epoch(false);assert(live_bytes==expected_cpu(mask));
  if(mask){version();logo(0,11,4);logo(1,155,73);title_layers_art_ready();advance_fade(false,10,0,239);menu();check_present(true);}
  else assert(!title_layers_present(renderer,VGAScreen,&destination));
  title_layers_end();assert(!live_bytes);
 }
 for(unsigned k=0;k<3;k++)write_resource(k,resources[k],sizes[k]);
 available=7;
 puts("All seven independently missing resource combinations preserve available parts");
}
static void rejected_resource(unsigned k,const void *data,size_t n)
{
 write_resource(k,data,n);begin_epoch(false);assert(live_bytes==expected_cpu(7u&~(1u<<k)));
 title_layers_end();assert(!live_bytes);write_resource(k,resources[k],sizes[k]);
}
static void test_loader(void)
{
 for(unsigned k=0;k<3;k++) {
  Uint8 *bad=malloc(sizes[k]+1);assert(bad);
  /* Every byte of the exact 80-byte header is covered, including all u64 IDs. */
  for(unsigned offset=0;offset<80;offset++) {memcpy(bad,resources[k],sizes[k]);bad[offset]^=1;rejected_resource(k,bad,sizes[k]);}
  const size_t lengths[]={0,3,47,79,80};
  for(unsigned i=0;i<sizeof(lengths)/sizeof(*lengths);i++)rejected_resource(k,resources[k],lengths[i]);
  rejected_resource(k,resources[k],sizes[k]-1);memcpy(bad,resources[k],sizes[k]);bad[sizes[k]]=0;rejected_resource(k,bad,sizes[k]+1);
  memcpy(bad,resources[k],sizes[k]);bad[sizes[k]-9]^=1;rejected_resource(k,bad,sizes[k]);
  memcpy(bad,resources[k],sizes[k]);
  if(k){bad[80+3]=1;rehash(bad,sizes[k]);rejected_resource(k,bad,sizes[k]);
   memcpy(bad,resources[k],sizes[k]);bad[80]=1;rehash(bad,sizes[k]);rejected_resource(k,bad,sizes[k]);
   /* Transparent RGB inside the permitted support box must still be zero. */
   memcpy(bad,resources[k],sizes[k]);size_t p=80+4*((size_t)12*4*widths[k]+12);bad[p]=1;bad[p+3]=0;rehash(bad,sizes[k]);rejected_resource(k,bad,sizes[k]);
  }else for(unsigned a=0;a<255;a+=17){memcpy(bad,resources[k],sizes[k]);bad[83]=(Uint8)a;rehash(bad,sizes[k]);rejected_resource(k,bad,sizes[k]);}
  if(k) {
   const unsigned bounds[2][4]={{4,4,1216,484},{8,8,644,252}};const unsigned *b=bounds[k-1];
   const unsigned points[8][2]={{b[0],b[1]},{b[2]-1,b[1]},{b[0],b[3]-1},{b[2]-1,b[3]-1},{b[0]-1,b[1]},{b[0],b[1]-1},{b[2],b[1]},{b[0],b[3]}};
   for(unsigned corner=0;corner<8;corner++) {
    unsigned x=points[corner][0],y=points[corner][1];if(x>=widths[k]*4||y>=heights[k]*4)continue;
    memcpy(bad,resources[k],sizes[k]);size_t p=80+4*((size_t)y*widths[k]*4+x);bad[p]=91;bad[p+1]=123;bad[p+2]=207;bad[p+3]=127;rehash(bad,sizes[k]);
    if(corner<4){write_resource(k,bad,sizes[k]);begin_epoch(false);assert(state.active&&state.rgba[k]&&live_bytes==expected_cpu(7));title_layers_end();write_resource(k,resources[k],sizes[k]);}
    else rejected_resource(k,bad,sizes[k]);
   }
  }
  assert(!unlink(paths[k]));assert(!mkdir(paths[k],0700));begin_epoch(false);assert(live_bytes==expected_cpu(7u&~(1u<<k)));title_layers_end();assert(!rmdir(paths[k]));
  assert(!mkfifo(paths[k],0600));begin_epoch(false);assert(live_bytes==expected_cpu(7u&~(1u<<k)));title_layers_end();assert(!unlink(paths[k]));
  write_resource(k,resources[k],sizes[k]);free(bad);
 }
 puts("Exact80-byte TLV1, every header byte, lengths, hash, alpha, support bounds, transparent RGB, directories and FIFOs rejected safely");
}
static void assert_dead(void)
{
 assert(!title_layers_present(renderer,VGAScreen,&destination));assert(!live_bytes&&!gpu_live_bytes);
 unsigned old_opens=opens,old_allocs=allocs;assert(!title_layers_present(renderer,VGAScreen,&destination));assert(opens==old_opens&&allocs==old_allocs);
}
static void test_registration(void)
{
 for(unsigned mode=0;mode<18;mode++) {
  begin_epoch(false);title_layers_end();reset_faults();
  SDL_Surface old=*VGAScreen,old2=*VGAScreen2;SDL_PixelFormat oldformat=*VGAScreen->format;SDL_Surface *screen2=VGAScreen2;
  SDL_Color changed[256];memcpy(changed,target_palette,sizeof(changed));const SDL_Color *target=target_palette;SDL_Surface *source=VGAScreen;
  Sprite saved=sprite_table[PLANET_SHAPES].sprite[146];unsigned count=sprite_table[PLANET_SHAPES].count;
  switch(mode){
   case 0:((Uint8 *)VGAScreen->pixels)[63111]^=1;break;
   case 1:changed[7].r^=1;target=changed;break;
   case 2:rgb_palette[17]^=1;break;
   case 3:VGAScreen->w=319;break;
   case 4:VGAScreen->h=199;break;
   case 5:VGAScreen->pitch=2147483647;break;
   case 6:VGAScreen->format->BitsPerPixel=16;break;
   case 7:VGAScreen->format->BytesPerPixel=2;break;
   case 8:VGAScreen->pixels=NULL;break;
   case 9:VGAScreen->format=NULL;break;
   case 10:source=NULL;break;
   case 11:target=NULL;break;
   case 12:VGAScreen2=VGAScreen;break;
   case 13:VGAScreen2->pitch=321;break;
   case 14:sprite_table[PLANET_SHAPES].sprite[146].width=303;break;
   case 15:sprite_table[PLANET_SHAPES].sprite[146].size--;break;
   case 16:logo_rle[0][13]^=1;break;
   case 17:sprite_table[PLANET_SHAPES].count=150;break;
  }
  title_layers_begin(source,target,false);assert_dead();assert(opens==0&&allocs==0);
  *VGAScreen=old;*old.format=oldformat;VGAScreen2=screen2;*VGAScreen2=old2;
  sprite_table[PLANET_SHAPES].sprite[146]=saved;sprite_table[PLANET_SHAPES].count=count;if(mode==16)logo_rle[0][13]^=1;
 }
 puts("PIC4, palette, RLE, dimensions, layout, companion surface and original sprite identity registration gates passed");
}
static void test_lease(void)
{
 for(unsigned mode=0;mode<12;mode++) {
  initial(false);SDL_Surface old=*VGAScreen,old2=*VGAScreen2;SDL_PixelFormat oldformat=*VGAScreen->format;SDL_Surface *oldseg=VGAScreenSeg;
  switch(mode){
   case 0:((Uint8 *)VGAScreen->pixels)[63111]^=1;break;
   case 1:rgb_palette[7]^=1;break;
   case 2:VGAScreen->pitch++;break;
   case 3:VGAScreen->format->BitsPerPixel=16;break;
   case 4:VGAScreen->pixels=pic_source;break;
   case 5:VGAScreen->format=NULL;break;
   case 6:VGAScreenSeg=NULL;break;
   case 7:logo_rle[0][13]^=1;break;
   case 8:title_layers_logo(151,155,73);break;
   case 9:title_layers_logo(146,12,4);break;
   case 10:VGAScreen2->pixels=pic_source;break;
   case 11:VGAScreen2->format=NULL;break;
  }
  assert_dead();*VGAScreen=old;*VGAScreen2=old2;*old.format=oldformat;VGAScreenSeg=oldseg;if(mode==7)logo_rle[0][13]^=1;
 }
 begin_epoch(false);title_layers_pixel(VGAScreen,(Uint8 *)((uintptr_t)VGAScreen->pixels-1),TITLE_WRITE_FONT);assert_dead();
 begin_epoch(false);title_layers_pixel(VGAScreen,(Uint8 *)VGAScreen->pixels+64000,TITLE_WRITE_FONT);assert_dead();
 begin_epoch(false);title_layers_pixel(VGAScreen2,(Uint8 *)VGAScreen2->pixels,TITLE_WRITE_FONT);assert_dead();
 begin_epoch(false);title_layers_pixel(VGAScreen,(Uint8 *)(uintptr_t)INTPTR_MIN,TITLE_WRITE_FONT);assert_dead();
 begin_epoch(false);title_layers_pixel(VGAScreen,(Uint8 *)(uintptr_t)UINTPTR_MAX,TITLE_WRITE_FONT);assert_dead();
 begin_epoch(false);title_layers_pixel(VGAScreen,NULL,TITLE_WRITE_FONT);assert_dead();
 initial(true);((Uint8 *)VGAScreen2->pixels)[63999]^=1;title_layers_restore_before(TITLE_BACKGROUND);assert_dead();
 initial(false);menu();((Uint8 *)VGAScreen2->pixels)[7]^=1;title_layers_restore_before(TITLE_MENU);assert_dead();
 initial(false);menu();live_cursor(100*320+319,false);assert_dead();
 initial(false);menu();assert(state.stage==ST_NONE);
 title_layers_pixel(VGAScreen,(Uint8 *)VGAScreen->pixels+104*320+120,TITLE_WRITE_FONT);assert_dead();
 initial(false);menu();title_layers_fade_start(target_palette,NULL,0,255);assert_dead();
 initial(false);menu();title_layers_fade_start(target_palette,NULL,240,255);title_layers_fade_step(19,240,255);assert_dead();
 begin_epoch(false);version();logo(0,11,4);logo(1,155,73);title_layers_art_ready();title_layers_fade_start(target_palette,NULL,0,239);title_layers_fade_step(10,0,239);assert_dead();
 puts("Full64k indexed lease/checkpoints/cursor restore, palette tamper, wrong sequence and recurrence fail the whole epoch without retries");
}
static void test_checkpoint_enums(void)
{
 const int invalid[]={-1,-2,2,2147483647};
 for(unsigned k=0;k<sizeof(invalid)/sizeof(invalid[0]);k++)for(unsigned op=0;op<4;op++) {
  begin_epoch(true);version();
  if(op>=2)save_checkpoint(TITLE_BACKGROUND);
  if(op==0)title_layers_save_before((enum TitleCheckpoint)invalid[k]);
  if(op==1){memcpy(VGAScreen2->pixels,VGAScreen->pixels,64000);title_layers_save_after((enum TitleCheckpoint)invalid[k]);}
  if(op==2)title_layers_restore_before((enum TitleCheckpoint)invalid[k]);
  if(op==3){memcpy(VGAScreen->pixels,VGAScreen2->pixels,64000);title_layers_restore_after((enum TitleCheckpoint)invalid[k]);}
  assert_dead();
 }
 begin_epoch(true);version();memcpy(VGAScreen2->pixels,VGAScreen->pixels,64000);
 title_layers_save_after(TITLE_BACKGROUND);assert_dead();
 begin_epoch(true);version();save_checkpoint(TITLE_BACKGROUND);
 title_layers_restore_after(TITLE_BACKGROUND);assert_dead();
 puts("18 invalid checkpoint enum/no-before regressions fail closed, including negative sentinel collisions");
}
static void test_failures(void)
{
 for(int allocation=1;allocation<=4;allocation++) {
  begin_epoch(false);title_layers_end();reset_faults();fail_alloc=allocation;title_layers_begin(VGAScreen,target_palette,false);assert_dead();
 }
 for(int fault=0;fault<10;fault++) {
  begin_epoch(false);title_layers_end();reset_faults();
  switch(fault){case 0:fail_open=1;break;case 1:fail_stat=1;break;case 2:fail_read=1;break;case 3:fail_read=2;break;case 4:short_read=1;break;case 5:short_read=2;break;case 6:fail_close=1;break;case 7:title_layers_set_directory("");break;case 8:title_layers_set_directory(NULL);break;case 9:{static char too_long[4096];memset(too_long,'x',sizeof(too_long)-1);title_layers_set_directory(too_long);break;}}
  title_layers_begin(VGAScreen,target_palette,false);
  /* Individual file read faults fall back independently; whole-path faults have no output. */
  if(fault==2||fault==3||fault==4||fault==5)assert(live_bytes==expected_cpu(6));else assert_dead();
  title_layers_end();title_layers_set_directory(directory);
 }
 for(int fault=1;fault<=7;fault++) {
  initial(false);title_layers_release_texture();fail_sdl=fault;assert_dead();
 }
 initial(false);title_layers_sprite_table_reset(SMALL_FONT_SHAPES);check_present(false);title_layers_sprite_table_reset(PLANET_SHAPES);assert_dead();
 initial(false);assert(!title_layers_present(NULL,VGAScreen,&destination));assert_dead();
 initial(false);assert(!title_layers_present(renderer,NULL,&destination));assert_dead();
 initial(false);assert(!title_layers_present(renderer,VGAScreen,NULL));assert_dead();
 reset_faults();puts("All four allocator failures, bounded I/O failures and seven SDL failures have checked lifetimes");
}
static void test_renderer(void)
{
 initial(false);menu();size_t cpu=live_bytes;unsigned oldallocs=allocs,oldreads=reads,oldopens=opens,oldcreates=creates;
 for(unsigned i=0;i<8;i++)check_present(false);
 assert(live_bytes==cpu&&allocs==oldallocs&&reads==oldreads&&opens==oldopens&&creates==oldcreates);
 title_layers_release_texture();assert(!gpu_live_bytes&&live_bytes==cpu);SDL_DestroyRenderer(renderer);
 renderer=SDL_CreateSoftwareRenderer(display);assert(renderer);check_present(true);assert(live_bytes==cpu&&allocs==oldallocs&&opens==oldopens&&reads==oldreads);
 destination=(SDL_Rect){0,0,640,400};assert(title_layers_present(renderer,VGAScreen,&destination));
 for(unsigned y=0;y<400;y++)for(unsigned x=0;x<640;x++)assert(((Uint32 *)((Uint8 *)display->pixels+y*display->pitch))[x]==expected_pixel(2*x+1,2*y+1));
 destination=(SDL_Rect){0,0,1280,800};title_layers_end();title_layers_end();assert_dead();
 puts("Texture recreation preserves CPU/source lease, exact2x nearest sampling, and presentation performs no heap allocation or resource I/O");
}
int main(int argc,char **argv)
{
 setvbuf(stdout,NULL,_IOLBF,0);assert(argc==2);directory=argv[1];assert(!SDL_Init(0));
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);assert(VGAScreen);
 VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);assert(VGAScreen2);
 main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);assert(main_window_tex_format);
 display=SDL_CreateRGBSurfaceWithFormat(0,1280,800,32,SDL_PIXELFORMAT_ARGB8888);assert(display);
 renderer=SDL_CreateSoftwareRenderer(display);assert(renderer);
 for(unsigned i=0;i<64000;i++)pic_source[i]=(Uint8)((i*7)%239);
 for(unsigned i=0;i<256;i++)target_palette[i]=(SDL_Color){(Uint8)(i*3),(Uint8)(i*7),(Uint8)(i*13),255};
 sprite_table[PLANET_SHAPES].count=152;make_fixture(0);make_fixture(1);
 for(unsigned k=0;k<3;k++){snprintf(paths[k],sizeof(paths[k]),"%s/%s",directory,names[k]);pack_resource(k);}
 begin_epoch(false);assert_dead();assert(!opens&&!allocs);title_layers_set_directory(directory);
 test_sequence();test_missing();test_loader();test_registration();test_lease();test_checkpoint_enums();test_failures();test_renderer();
 title_layers_end();title_layers_pixel(NULL,NULL,TITLE_WRITE_FONT);assert(!live_bytes&&!gpu_live_bytes);assert(peak_bytes==11209728&&gpu_peak_bytes==4096000);assert(destroys<=creates);
 printf("Exact dynamic ledger: CPU peak=%zu; nominal texture peak=%zu; combined=%zu bytes\n",peak_bytes,gpu_peak_bytes,peak_bytes+gpu_peak_bytes);
 const size_t fixed_images=sizeof(state.pic4)+sizeof(state.i146)+sizeof(state.m146)+sizeof(state.i151)+sizeof(state.m151)+sizeof(state.expected)+sizeof(state.checkpoint)+sizeof(state.pre_cursor)+sizeof(state.version)+sizeof(state.menu)+sizeof(state.menu_base)+sizeof(state.cursor);
 const size_t fixed_palette=sizeof(state.expected_palette)+sizeof(state.target_palette)+sizeof(state.fade_target)+sizeof(state.channel);
 assert(fixed_images==862304&&fixed_palette==3328);
 printf("Fixed ledger: indexed/mask/checkpoint/planes=%zu; palette/LUT=%zu; state metadata/padding=%zu; state=%zu; specs+directory=%zu bytes\n",fixed_images,fixed_palette,sizeof(state)-fixed_images-fixed_palette,sizeof(state),sizeof(specs)+sizeof(asset_directory));
 printf("Production presentations=%u; all resources, renderer handles and tracked allocations released\n",presents);
 for(unsigned k=0;k<3;k++)free(resources[k]);
 SDL_DestroyRenderer(renderer);SDL_FreeSurface(display);SDL_FreeSurface(VGAScreen);SDL_FreeSurface(VGAScreen2);SDL_FreeFormat(main_window_tex_format);SDL_Quit();
 puts("TLV1 production-module synthetic runtime suite passed");return 0;
}
