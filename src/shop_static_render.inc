/* SPDX-License-Identifier: GPL-2.0-or-later
 * Shared NEWSH1 quad identities in the authenticated shop owner only.
 * The four original tile calls and every INDEX8 write remain untouched.
 */
#include "shop_static_pins.h"
static struct {
 Uint8 *rgba[3];const void *bank;size_t bank_size;
 bool attempted[3],fault[3],contributed[3],blitting;
} shop_static;
static size_t shop_static_static_bytes(void)
{return sizeof(shop_static)+sizeof(shop_static_spec);}
static size_t shop_static_bytes(void)
{size_t n=shop_static_static_bytes();for(unsigned i=0;i<3;i++)if(shop_static.rgba[i])n+=172032;return n;}
static void shop_static_reset(void)
{for(unsigned i=0;i<3;i++)free(shop_static.rgba[i]);memset(&shop_static,0,sizeof(shop_static));}
static bool shop_static_requested(void)
{return directory&&*directory&&!game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid;}
static bool shop_static_source(void)
{
 return shopSpriteSheet.data&&shopSpriteSheet.size==SHOP_STATIC_BANK_BYTES&&
  (!shop_static.bank||(shop_static.bank==shopSpriteSheet.data&&shop_static.bank_size==shopSpriteSheet.size))&&
  hash(shopSpriteSheet.data,shopSpriteSheet.size)==SHOP_STATIC_BANK_HASH&&palette_count>0&&palette_hash(palettes[0])==PF_PAL;
}
static bool shop_static_decode(unsigned quad,Uint8 indices[672],Uint8 mask[672])
{
 const Uint8 *b=shopSpriteSheet.data;size_t size=shopSpriteSheet.size;
 static const unsigned delta[4]={0,1,19,20};memset(indices,0,672);memset(mask,0,672);
 if(!b)return false;
 for(unsigned tile=0;tile<4;tile++){
  unsigned id=quad+delta[tile];if(!id||2u*id>size)return false;
  size_t at=b[2*(id-1)]|((size_t)b[2*(id-1)+1]<<8);unsigned x=0,y=0;bool end=false;
  while(at<size){unsigned code=b[at++];if(code==15){end=true;break;}unsigned count=code>>4;x+=code&15;
   if(!count){if(x!=12)return false;++y;x=0;continue;}
   if(y>=14||x+count>12||count>size-at)return false;
   while(count--){unsigned p=(y+(tile/2)*14)*24+x+(tile%2)*12;indices[p]=b[at++];mask[p]=255;++x;}
  }
  if(!end)return false;
 }
 return true;
}
static void shop_static_load(unsigned slot)
{
 if(shop_static.attempted[slot])return;shop_static.attempted[slot]=true;
 const struct ShopStaticSpec *s=&shop_static_spec[slot];Uint8 indices[672],mask[672];
 if(!shop_static_requested()||!shop_static_source()||!shop_static_decode(s->quad,indices,mask)||hash(indices,672)!=s->indices||hash(mask,672)!=s->mask)return;
 shop_static.bank=shopSpriteSheet.data;shop_static.bank_size=shopSpriteSheet.size;
 char path[1200];int n=snprintf(path,sizeof(path),"%s/%s",directory,s->name);if(n<0||(size_t)n>=sizeof(path))return;
 int fd=SF_OPEN(path);if(fd<0)return;SF_STAT st;Uint8 h[128],extra,*p=NULL;bool ok=false;
 const unsigned fields[15]={1,s->quad,24,28,8,192,224,0,0,172032,4,1,1,0,0};
 if(SF_FSTAT(fd,&st)||!SF_REGULAR(st.st_mode)||st.st_size!=172160||SF_READ(fd,h,128)!=128||memcmp(h,"SQC1",4))goto done;
 for(unsigned i=0;i<15;i++)if(u32(h+4+i*4)!=fields[i])goto done;
 if(u64(h+64)!=PF_BASE||u64(h+72)!=PF_PAL||u64(h+80)!=SHOP_STATIC_BANK_HASH||u64(h+88)!=s->indices||u64(h+96)!=s->mask||u64(h+104)!=s->payload||u64(h+112)||u64(h+120))goto done;
 p=malloc(172032);if(!p)goto done;size_t at=0;
 while(at<172032){int got=SF_READ(fd,p+at,172032-at);if(got<=0)goto done;at+=(unsigned)got;}
 if(SF_READ(fd,&extra,1)!=0||hash(p,172032)!=s->payload)goto done;ok=true;
 done:if(SF_CLOSE(fd))ok=false;if(ok)shop_static.rgba[slot]=p;else free(p);
}
static bool shop_static_valid(unsigned slot)
{
 if(shop_static.fault[slot])return false;
 bool ok=shop_static_requested()&&shop_static_source()&&shop_static.rgba[slot]&&hash(shop_static.rgba[slot],172032)==shop_static_spec[slot].payload;
 if(!ok&&shop_static.contributed[slot])shop_static.fault[slot]=true;return ok;
}
static void shop_static_quad_begin(SDL_Surface *surface,int x,int y,const void *data,size_t size,unsigned quad)
{
 if(shop_static.blitting){reject();return;}
 if(!sf.active||!sf.frame||surface!=sf.screen||data!=shopSpriteSheet.data||size!=shopSpriteSheet.size||!box(x,y,24,28))return;
 /* Product list and original ship assembly are authenticated owner scopes;
  * no item number, category whitelist or battle eligibility is borrowed. */
 if(sf.product?(sf.updating||sf.stage!=S_BUILD):(sf.stage!=S_PRIMITIVE||sf.phase!=PREGAME_SHIP||sf.primitive||sf.ship_shield||sf.phase_count<2))return;
 int slot=-1;for(unsigned i=0;i<3;i++)if(shop_static_spec[i].quad==quad)slot=(int)i;
 if(slot<0||!exact())return;shop_static_load(slot);if(!shop_static_valid(slot))return;
 Uint8 indices[672],mask[672];if(!shop_static_decode(quad,indices,mask))return;
 struct SfCommand *c=append(C_STATIC,x,y,0,slot,0,0);if(!c)return;c->w=24;c->h=28;
 for(unsigned tile=0;tile<4;tile++)for(unsigned yy=0;yy<14;yy++)for(unsigned xx=0;xx<12;xx++){
  unsigned dx=xx+(tile%2)*12,dy=yy+(tile/2)*14,p=dy*24+dx;
  if(mask[p]&&!event(x+dx,y+dy,indices[p],0))return;
 }
 c->events=sf.event_count-c->first;sf.event_next=c->first;sf.event_limit=sf.event_count;sf.primitive=true;sf.stage=S_PRIMITIVE;
 shop_static.blitting=shop_static.contributed[slot]=true;
}
static void shop_static_quad_end(void)
{
 if(!shop_static.blitting)return;shop_static.blitting=false;pregame_font_glyph_end();
}
static Uint32 shop_static_sample(const Uint8 *data,unsigned x,unsigned y,unsigned *alpha)
{
 unsigned a=0,c[3]={0,0,0};
 for(unsigned yy=0;yy<2;yy++)for(unsigned xx=0;xx<2;xx++){const Uint8 *v=data+((y*2+yy)*192+x*2+xx)*4;a+=v[3];for(unsigned k=0;k<3;k++)c[k]+=v[k]*v[3];}
 *alpha=(a+2)/4;if(!a)return 0;Uint32 color=0;
 for(unsigned k=0;k<3;k++)color|=(((c[k]+a/2)/a*sf.metal_gain+127)/255)<<(16-k*8);
 return color;
}
