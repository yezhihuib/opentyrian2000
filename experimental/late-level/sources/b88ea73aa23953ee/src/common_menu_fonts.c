/* SPDX-License-Identifier: GPL-2.0-or-later
 * Reconstructed from baseline SFN1 contracts, not recovered source bytes. */
#include "common_menu_fonts.h"
#include "fonthand.h"
#include "sprite.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>
#if defined(TARGET_WIN32) || defined(_WIN32)
#include <io.h>
#define CF_OPEN(p) _open(p,_O_RDONLY|_O_BINARY|_O_NOINHERIT)
#define CF_READ _read
#define CF_CLOSE _close
#define CF_FSTAT _fstat
#define CF_STAT struct _stat
#define CF_REGULAR(m) (((m)&_S_IFMT)==_S_IFREG)
#else
#include <unistd.h>
#define CF_OPEN(p) open(p,O_RDONLY|O_NONBLOCK)
#define CF_READ read
#define CF_CLOSE close
#define CF_FSTAT fstat
#define CF_STAT struct stat
#define CF_REGULAR(m) S_ISREG(m)
#endif
#define CF_FNV UINT64_C(14695981039346656037)
#define CF_MAP UINT64_C(0x845b16939661b466)
#define CF_PAL UINT64_C(0x69f74bd2c5d2ad5b)
struct Spec {unsigned count,ink,mw,mh,aw,ah,cw,ch,plane;uint64_t metrics,encoded,eligibility,payload;const char *name;};
static const struct Spec specs[3]={
 {60,53,17,20,1216,384,76,96,466944,UINT64_C(0xb0a8226af36e025a),UINT64_C(0x5c12ed2dea448227),UINT64_C(0x5529cd3792b04378),UINT64_C(0x0501f2f573e8d9a5),"large"},
 {85,76,12,13,896,384,56,64,344064,UINT64_C(0xf0dec0f37828f1c4),UINT64_C(0x96f0e4e668876f23),UINT64_C(0xa3861b64f710cb1f),UINT64_C(0x08f9609583417c89),"medium"},
 {127,86,6,8,0,0,0,0,0,UINT64_C(0x0908ca85cbf2a1e3),UINT64_C(0x2ed2973d82ce6f3d),UINT64_C(0x68e8c2bab3c43d0d),0,NULL}
};
struct Source {const Uint8 *rle;unsigned size,w,h;Uint8 mask[17*20];bool ink;};
static struct {bool valid;struct Source glyph[127];Uint8 *payload;char directory[1024];} banks[3];
static uint64_t more(uint64_t h,const void *v,size_t n){const Uint8 *p=v;while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
static uint64_t h16(uint64_t h,unsigned v){Uint8 p[2]={(Uint8)v,(Uint8)(v>>8)};return more(h,p,2);}
static uint32_t u32(const Uint8 *p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t u64(const Uint8 *p){return u32(p)|((uint64_t)u32(p+4)<<32);}
static bool map_ok(void){uint64_t h=CF_FNV;for(unsigned i=0;i<256;i++){uint32_t v=(uint32_t)font_ascii[i];Uint8 p[4]={(Uint8)v,(Uint8)(v>>8),(Uint8)(v>>16),(Uint8)(v>>24)};h=more(h,p,4);}return h==CF_MAP;}
void common_menu_fonts_table_reset(unsigned b){if(b<3){free(banks[b].payload);memset(&banks[b],0,sizeof(banks[b]));}}
void common_menu_fonts_shutdown(void){for(unsigned b=0;b<3;b++)common_menu_fonts_table_reset(b);}
static bool source(unsigned b,bool capture)
{
 const struct Spec *s=&specs[b];uint64_t met=CF_FNV,enc=CF_FNV,eligible=CF_FNV;
 if(!map_ok()||sprite_table[b].count!=s->count)return false;
 if(b==2){const Uint8 p[4]={127,0,0,0};enc=more(enc,p,4);}
 for(unsigned id=0;id<s->count;id++){
  const Sprite *sp=sprite(b,id);struct Source *g=&banks[b].glyph[id];
  if(!sp->data||!sp->size||!sp->width||!sp->height||sp->width>s->mw||sp->height>s->mh||sp->size>2*s->mw*s->mh+s->mh)return false;
  if(!capture&&(g->rle!=sp->data||g->size!=sp->size||g->w!=sp->width||g->h!=sp->height))return false;
  met=h16(h16(h16(met,sp->width),sp->height),sp->width+1);enc=h16(h16(h16(enc,sp->width),sp->height),sp->size);enc=more(enc,sp->data,sp->size);
  if(capture){
   g->rle=sp->data;g->size=sp->size;g->w=sp->width;g->h=sp->height;g->ink=false;memset(g->mask,255,sizeof(g->mask));unsigned x=0,y=0;
   for(unsigned k=0;k<sp->size;k++){
    unsigned v=sp->data[k];if(y>=g->h)return false;
    if(v==255){if(++k>=sp->size)return false;x+=sp->data[k];}
    else if(v==254)x=g->w;else if(v==253)++x;
    else {if(x>=g->w)return false;g->mask[y*g->w+x]=(Uint8)(v&15);g->ink=true;++x;}
    if(x>g->w)return false;if(x==g->w){x=0;++y;}
   }
   if(x||y>g->h)return false;
  }
  Uint8 e=(b==2?id<86:g->ink)?255:0;eligible=more(eligible,&e,1);
 }
 return met==s->metrics&&enc==s->encoded&&eligible==s->eligibility;
}
static bool padding(unsigned b,const Uint8 *p)
{
 const struct Spec *s=&specs[b];unsigned inked=0;
 for(unsigned id=0;id<(s->aw/s->cw)*(s->ah/s->ch);id++){
  const struct Source *g=id<s->count?&banks[b].glyph[id]:NULL;bool ink=false;
  for(unsigned y=0;y<s->ch;y++)for(unsigned x=0;x<s->cw;x++){
   unsigned n=((id/16)*s->ch+y)*s->aw+(id%16)*s->cw+x;unsigned a=p[n],r=p[s->plane+n];
   bool allowed=g&&g->ink&&x>=4&&y>=4&&x<4+4*g->w&&y<4+4*g->h;
   if((!allowed&&(a||r))||(!a&&r)||(a&&(r<12||r>15)))return false;if(a)ink=true;
  }
  if(g&&ink!=g->ink)return false;inked+=ink;
 }
 return inked==s->ink;
}
static bool load(unsigned b,const char *directory)
{
 const struct Spec *s=&specs[b];char path[1100];Uint8 h[128],extra,*p=NULL;CF_STAT st;bool ok=false;
 if(!directory||!*directory||strlen(directory)>=sizeof(banks[b].directory))return false;
 if(banks[b].payload&&!strcmp(directory,banks[b].directory))return true;
 free(banks[b].payload);banks[b].payload=NULL;
 int n=snprintf(path,sizeof(path),"%s/settings-font-%s-v1.hda",directory,s->name);if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=CF_OPEN(path);if(fd<0)return false;
 unsigned fields[15]={1,b,4,s->aw,s->ah,s->cw,s->ch,4,s->count,s->ink,s->plane,s->plane,1,12,15};
 if(CF_FSTAT(fd,&st)||!CF_REGULAR(st.st_mode)||st.st_size!=(long)(128+2*s->plane)||CF_READ(fd,h,128)!=128||memcmp(h,"SFN1",4))goto done;
 for(unsigned i=0;i<15;i++)if(u32(h+4+4*i)!=fields[i])goto done;
 if(u64(h+64)!=CF_MAP||u64(h+72)!=s->metrics||u64(h+80)!=s->encoded||u64(h+88)!=s->eligibility||u64(h+96)!=CF_PAL||u64(h+104)!=s->payload||u64(h+112)||u64(h+120))goto done;
 p=malloc(2*s->plane);if(!p||CF_READ(fd,p,2*s->plane)!=(long)(2*s->plane)||CF_READ(fd,&extra,1)!=0||more(CF_FNV,p,2*s->plane)!=s->payload||!padding(b,p))goto done;ok=true;
 done:if(CF_CLOSE(fd))ok=false;if(ok){banks[b].payload=p;strcpy(banks[b].directory,directory);}else free(p);return ok;
}
bool common_menu_fonts_acquire(const char *directory,unsigned sources,unsigned resources)
{
 if((sources&~7u)||(resources&~3u)||(resources&~sources))return false;bool all=true;
 for(unsigned b=0;b<3;b++)if(sources&(1u<<b)){
  if(!banks[b].valid){banks[b].valid=source(b,true);}
  else if(!source(b,false)){common_menu_fonts_table_reset(b);}
  if(!banks[b].valid||((resources&(1u<<b))&&!load(b,directory)))all=false;
 }
 return all;
}
bool common_menu_fonts_validate(unsigned sources)
{
 if(sources&~7u)return false;bool all=true;
 for(unsigned b=0;b<3;b++)if(sources&(1u<<b))if(!banks[b].valid||!source(b,false)){common_menu_fonts_table_reset(b);all=false;}
 return all;
}
bool common_menu_fonts_glyph(unsigned b,unsigned id,CommonMenuGlyph *out)
{
 if(!out||b>=3||!banks[b].valid||id>=specs[b].count)return false;
 const struct Source *g=&banks[b].glyph[id];if(!g->ink)return false;const struct Spec *s=&specs[b];
 memset(out,0,sizeof(*out));out->width=g->w;out->height=g->h;out->advance=g->w+1;out->source=g->mask;
 if(banks[b].payload){unsigned n=((id/16)*s->ch+4)*s->aw+(id%16)*s->cw+4;out->alpha=banks[b].payload+n;out->roles=banks[b].payload+s->plane+n;out->atlas_pitch=s->aw;}
 return true;
}
size_t common_menu_fonts_retained_bytes(void){size_t n=sizeof(banks);for(unsigned b=0;b<2;b++)if(banks[b].payload)n+=2*specs[b].plane;return n;}
