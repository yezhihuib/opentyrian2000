/* SPDX-License-Identifier: GPL-2.0-or-later
 * Two explicitly registered opaque startup cards. Original indexed writes,
 * palettes, waits, inputs, and RNG remain owned by the original engine.
 */
#include "startup_logos.h"
#include "palette.h"
#include "video.h"
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#if defined(TARGET_WIN32) || defined(_WIN32)
#include <io.h>
#define MFG_OPEN(path) _open(path, _O_RDONLY | _O_BINARY | _O_NOINHERIT)
#define MFG_READ _read
#define MFG_CLOSE _close
#define MFG_FSTAT _fstat
#define MFG_STAT struct _stat
#define MFG_REGULAR(mode) (((mode) & _S_IFMT) == _S_IFREG)
#else
#include <unistd.h>
/* Inspect the opened object; O_NONBLOCK keeps FIFO input bounded. */
#define MFG_OPEN(path) open(path, O_RDONLY | O_NONBLOCK)
#define MFG_READ read
#define MFG_CLOSE close
#define MFG_FSTAT fstat
#define MFG_STAT struct stat
#define MFG_REGULAR(mode) S_ISREG(mode)
#endif

#ifndef MFG_PIC10_INDEX_FNV
#define MFG_PIC10_INDEX_FNV UINT64_C(0x720d8ce9dda3f5f4)
#endif
#ifndef MFG_PIC10_PALETTE_FNV
#define MFG_PIC10_PALETTE_FNV UINT64_C(0xb50ac0b9e5f1a73d)
#endif
#ifndef MFG_PIC12_INDEX_FNV
#define MFG_PIC12_INDEX_FNV UINT64_C(0x98d7341da720b7ab)
#endif
#ifndef MFG_PIC12_PALETTE_FNV
#define MFG_PIC12_PALETTE_FNV UINT64_C(0x20261a06b61711d5)
#endif

enum { MFG_W=320, MFG_H=200, MFG_DENSITY=4, MFG_PIXELS=1024000,
       MFG_PAYLOAD=4096000, MFG_HEADER=64, MFG_FILE=4096064 };
enum { CARD_NONE, CARD_INITIAL, CARD_FADING_IN, CARD_HOLD, CARD_FADING_OUT, CARD_BLACK };
static const struct {
 unsigned int pic, palette;
 uint64_t indices, rgb;
 const char *filename;
} card_specs[2] = {
 {10,20,MFG_PIC10_INDEX_FNV,MFG_PIC10_PALETTE_FNV,"startup-pic10-v1.hda"},
 {12,22,MFG_PIC12_INDEX_FNV,MFG_PIC12_PALETTE_FNV,"startup-pic12-v1.hda"}
};
static const char *asset_directory;
static bool context;
bool startup_logos_owns_display(void) { return context; }
static unsigned int next_card, current_card;
static int phase, expected_remaining;
static Uint8 *card_rgba;
static Uint32 *card_output;
static Uint8 source_indices[MFG_W*MFG_H];
static SDL_Color expected_palette[256], fade_palette_target[256];
static SDL_Surface *source_surface;
static void *source_pixels;
static SDL_PixelFormat *source_format;
static int source_pitch;
static SDL_Texture *card_texture;

static uint32_t mfg_u32(const uint8_t *p)
{
 return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static uint64_t mfg_u64(const uint8_t *p)
{
 return (uint64_t)mfg_u32(p)|((uint64_t)mfg_u32(p+4)<<32);
}
static uint64_t mfg_hash(uint64_t hash,const uint8_t *p,size_t count)
{
 for(size_t i=0;i<count;i++)hash=(hash^p[i])*UINT64_C(1099511628211);
 return hash;
}
static uint64_t mfg_palette_hash(const SDL_Color *p)
{
 uint64_t h=UINT64_C(14695981039346656037);
 for(unsigned int i=0;i<256;i++) {
  const uint8_t rgb[3]={p[i].r,p[i].g,p[i].b};
  h=mfg_hash(h,rgb,3);
 }
 return h;
}

bool startup_logos_set_directory(const char *directory)
{
 /* argv storage remains alive for the process; no filesystem work at parse. */
 if(!directory||!*directory)return false;
 asset_directory=directory;
 return true;
}
bool startup_logos_configured(void) {return asset_directory!=NULL;}

void startup_logos_release_texture(void)
{
 if(card_texture)SDL_DestroyTexture(card_texture);
 card_texture=NULL;
}
void startup_logos_reset(void)
{
 startup_logos_release_texture();
 free(card_rgba);card_rgba=NULL;
 free(card_output);card_output=NULL;
 source_surface=NULL;source_pixels=NULL;source_format=NULL;source_pitch=0;
 phase=CARD_NONE;expected_remaining=0;
}
void startup_logos_end(void)
{
 startup_logos_reset();context=false;next_card=0;
}
void startup_logos_shutdown(void) {startup_logos_end();}
void startup_logos_begin(void)
{
 startup_logos_end();context=startup_logos_configured();
}

static bool mfg_read_exact(int file,uint8_t *p,unsigned int count)
{
 /* Short reads and interruptions fail closed; no retry or per-frame I/O. */
 return MFG_READ(file,p,count)==(long)count;
}
static bool mfg_load(unsigned int card)
{
 char path[1024];uint8_t header[MFG_HEADER],extra;MFG_STAT status;
 uint8_t *payload=NULL;bool valid=false;
 int length=snprintf(path,sizeof(path),"%s/%s",asset_directory,card_specs[card].filename);
 if(length<0||(size_t)length>=sizeof(path))return false;
 int file=MFG_OPEN(path);
 if(file<0)return false;
 if(MFG_FSTAT(file,&status)||!MFG_REGULAR(status.st_mode)||status.st_size!=MFG_FILE||
    !mfg_read_exact(file,header,sizeof(header)))goto done;
 if(memcmp(header,"MFG1",4)||mfg_u32(header+4)!=1||mfg_u32(header+8)!=MFG_DENSITY||
    mfg_u32(header+12)!=card_specs[card].pic||mfg_u32(header+16)!=card_specs[card].palette||
    mfg_u32(header+20)!=MFG_W||mfg_u32(header+24)!=MFG_H||mfg_u32(header+28)!=MFG_PAYLOAD||
    mfg_u64(header+32)!=card_specs[card].indices||mfg_u64(header+40)!=card_specs[card].rgb||
    mfg_u64(header+56)!=0)goto done;
 payload=malloc(MFG_PAYLOAD);
 if(!payload||!mfg_read_exact(file,payload,MFG_PAYLOAD)||MFG_READ(file,&extra,1)!=0)goto done;
 if(mfg_hash(UINT64_C(14695981039346656037),payload,MFG_PAYLOAD)!=mfg_u64(header+48))goto done;
 for(size_t i=3;i<MFG_PAYLOAD;i+=4)if(payload[i]!=255)goto done;
 valid=true;
done:
 if(MFG_CLOSE(file))valid=false;
 if(!valid){free(payload);return false;}
 card_rgba=payload;
 return true;
}

static bool mfg_source_matches(void)
{
 if(!source_surface||source_surface!=VGAScreen||source_surface!=VGAScreenSeg||
    source_surface->pixels!=source_pixels||source_surface->format!=source_format||
    !source_format||source_format->BitsPerPixel!=8||source_format->BytesPerPixel!=1||
    source_surface->pitch!=source_pitch||source_surface->w!=MFG_W||source_surface->h!=MFG_H)return false;
 for(unsigned int y=0;y<MFG_H;y++)
  if(memcmp((const uint8_t *)source_pixels+(size_t)y*source_pitch,source_indices+y*MFG_W,MFG_W))return false;
 return true;
}
static bool mfg_palette_matches(void)
{
 if(!main_window_tex_format)return false;
 for(unsigned int i=0;i<256;i++)
  if(rgb_palette[i]!=SDL_MapRGB(main_window_tex_format,expected_palette[i].r,expected_palette[i].g,expected_palette[i].b))return false;
 return true;
}
static bool mfg_live(void)
{
 if(!phase)return false;
 if(!context||!card_rgba||!card_output||!mfg_source_matches()||!mfg_palette_matches()) {
  startup_logos_reset();return false;
 }
 return true;
}

void startup_logos_bind(SDL_Surface *source,unsigned int pic,const SDL_Color *target)
{
 startup_logos_reset();
 if(!context||next_card>=2)return;
 unsigned int card=next_card++;
 /* A failed card still advances the explicit sequence, so PIC12 is independent. */
 if(pic!=card_specs[card].pic||!source||source!=VGAScreen||source!=VGAScreenSeg||
    !source->pixels||!source->format||source->format->BitsPerPixel!=8||source->format->BytesPerPixel!=1||
    source->w!=MFG_W||source->h!=MFG_H||source->pitch!=MFG_W||
    !target||!main_window_tex_format)return;
 if(mfg_palette_hash(target)!=card_specs[card].rgb)return;
 uint64_t hash=UINT64_C(14695981039346656037);
 for(unsigned int y=0;y<MFG_H;y++)hash=mfg_hash(hash,(const uint8_t *)source->pixels+(size_t)y*source->pitch,MFG_W);
 if(hash!=card_specs[card].indices)return;
 Uint8 initial=card==0?255:0;
 for(unsigned int i=0;i<256;i++) {
  expected_palette[i]=(SDL_Color){initial,initial,initial,255};
  if(rgb_palette[i]!=SDL_MapRGB(main_window_tex_format,initial,initial,initial))return;
 }
 if(!mfg_load(card))return;
 card_output=malloc(MFG_PAYLOAD);
 if(!card_output){startup_logos_reset();return;}
 for(size_t i=0;i<MFG_PIXELS;i++)card_output[i]=initial?UINT32_C(0xffffffff):UINT32_C(0xff000000);
 for(unsigned int y=0;y<MFG_H;y++)memcpy(source_indices+y*MFG_W,(const Uint8 *)source->pixels+(size_t)y*source->pitch,MFG_W);
 source_surface=source;source_pixels=source->pixels;source_format=source->format;source_pitch=source->pitch;
 current_card=card;phase=CARD_INITIAL;
}

void startup_logos_fade_start(const SDL_Color *target,const SDL_Color *solid,unsigned int first,unsigned int last)
{
 if(!mfg_live())return;
 if(first!=0||last!=255){startup_logos_reset();return;}
 if(phase==CARD_INITIAL&&target&&!solid&&mfg_palette_hash(target)==card_specs[current_card].rgb) {
  memcpy(fade_palette_target,target,sizeof(fade_palette_target));
  phase=CARD_FADING_IN;expected_remaining=current_card==0?25:10;
 } else if(phase==CARD_HOLD&&!target&&solid&&!solid->r&&!solid->g&&!solid->b) {
  memset(fade_palette_target,0,sizeof(fade_palette_target));
  phase=CARD_FADING_OUT;expected_remaining=10;
 } else startup_logos_reset();
}

void startup_logos_fade_step(int remaining,unsigned int first,unsigned int last)
{
 if(!phase)return;
 /* The engine palette has already advanced; validate our independently
  * predicted original step before changing any display-only pixels. */
 if(!context||!mfg_source_matches()||first!=0||last!=255||remaining!=expected_remaining||remaining<=0||
    (phase!=CARD_FADING_IN&&phase!=CARD_FADING_OUT)) {startup_logos_reset();return;}
 for(unsigned int i=0;i<256;i++) {
  expected_palette[i].r+=(int)(fade_palette_target[i].r-expected_palette[i].r)/remaining;
  expected_palette[i].g+=(int)(fade_palette_target[i].g-expected_palette[i].g)/remaining;
  expected_palette[i].b+=(int)(fade_palette_target[i].b-expected_palette[i].b)/remaining;
 }
 if(!mfg_palette_matches()){startup_logos_reset();return;}
 for(size_t i=0;i<MFG_PIXELS;i++) {
  Uint32 old=card_output[i],value=UINT32_C(0xff000000);
  for(unsigned int channel=0;channel<3;channel++) {
   unsigned int shift=16-channel*8;
   int before=(old>>shift)&255,want=phase==CARD_FADING_IN?card_rgba[4*i+channel]:0;
   value|=(Uint32)(before+(want-before)/remaining)<<shift;
  }
  card_output[i]=value;
 }
 --expected_remaining;
 if(!expected_remaining)phase=phase==CARD_FADING_IN?CARD_HOLD:CARD_BLACK;
}

bool startup_logos_present(SDL_Renderer *renderer,SDL_Surface *source,const SDL_Rect *destination)
{
 if(!mfg_live())return false;
 if(source!=source_surface||!renderer||!destination){startup_logos_reset();return false;}
 if(!card_texture) {
  card_texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,MFG_W*MFG_DENSITY,MFG_H*MFG_DENSITY);
  if(!card_texture||SDL_SetTextureScaleMode(card_texture,SDL_ScaleModeNearest)!=0||
     SDL_SetTextureBlendMode(card_texture,SDL_BLENDMODE_NONE)!=0)goto failed;
 }
 if(SDL_UpdateTexture(card_texture,NULL,card_output,MFG_W*MFG_DENSITY*4)!=0||
    SDL_SetRenderDrawColor(renderer,0,0,0,255)!=0||SDL_RenderClear(renderer)!=0||
    SDL_RenderCopy(renderer,card_texture,NULL,destination)!=0)goto failed;
 SDL_RenderPresent(renderer);
 return true;
failed:
 startup_logos_reset();return false;
}
