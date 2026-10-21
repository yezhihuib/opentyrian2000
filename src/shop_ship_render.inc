/* SPDX-License-Identifier: GPL-2.0-or-later
 * Independent SHOP neutral Talon call role. No battle pose, level predicate,
 * or Pulse birth envelope grants this command. Original quad writes survive.
 */
static char shop_ship_directory[1024];
static struct {
 Uint8 *rgba;const void *bank;size_t bank_size;
 bool attempted,armed,blitting,contributed,fault,used;
 int x,y;unsigned item;uint64_t hits;
} shop_ship;
static size_t shop_ship_static_bytes(void)
{return sizeof(shop_ship)+sizeof(shop_ship_directory);}
static size_t shop_ship_bytes(void)
{return shop_ship_static_bytes()+(shop_ship.rgba?172032:0);}
static void shop_ship_reset(void)
{free(shop_ship.rgba);memset(&shop_ship,0,sizeof(shop_ship));}
void pregame_shop_ship_set_directory(const char *path)
{
 size_t n=path?strlen(path):0;
 if(n<sizeof(shop_ship_directory)&&!strcmp(shop_ship_directory,path?path:""))return;
 /* Existing commands cannot borrow a restored/new root in the same update. */
 bool retired=shop_ship.contributed||shop_ship.fault,used=shop_ship.used;
 if(shop_ship.armed||shop_ship.blitting)reject();
 shop_ship_reset();shop_ship.fault=retired;shop_ship.used=used;shop_ship_directory[0]=0;
 if(n&&n<sizeof(shop_ship_directory))memcpy(shop_ship_directory,path,n+1);
}
static void shop_ship_update(void)
{
 if(shop_ship.armed||shop_ship.blitting){reject();return;}
 shop_ship.armed=shop_ship.blitting=shop_ship.contributed=shop_ship.fault=shop_ship.used=false;
}
static bool shop_ship_requested(void)
{return shop_ship_directory[0]&&!game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid;}
static bool shop_ship_record(void)
{
 /* All 40 loaded fields, serialized without host padding. Talon and Fang
  * happen to share graphic 233; the latter is not this accepted ship role. */
 if(player[0].items.ship!=1||ships[1].name[30])return false;
 Uint8 b[40];memcpy(b,ships[1].name,30);unsigned n=30;
 unsigned words[2]={ships[1].shipgraphic,ships[1].itemgraphic};
 for(unsigned i=0;i<2;i++){b[n++]=words[i];b[n++]=words[i]>>8;}
 b[n++]=ships[1].ani;b[n++]=(Uint8)ships[1].spd;b[n++]=ships[1].dmg;
 b[n++]=ships[1].cost;b[n++]=ships[1].cost>>8;b[n++]=ships[1].bigshipgraphic;
 return n==40&&hash(b,n)==UINT64_C(0xb03fc6f5a4145aae);
}
static bool shop_ship_decode(Uint8 indices[672],Uint8 mask[672])
{
 const Uint8 *b=spriteSheet9.data;size_t size=spriteSheet9.size;
 static const unsigned ids[4]={233,234,252,253};memset(indices,0,672);memset(mask,0,672);
 if(!b||size!=GLOBAL_TALON_BANK_BYTES)return false;
 for(unsigned tile=0;tile<4;tile++){
  unsigned id=ids[tile];size_t at=b[2*(id-1)]|((size_t)b[2*(id-1)+1]<<8);unsigned x=0,y=0;bool end=false;Uint8 decoded[336]={0};
  while(at<size){unsigned code=b[at++];if(code==15){end=true;break;}unsigned count=code>>4;x+=code&15;
   if(!count){if(x!=12)return false;++y;x=0;continue;}
   if(y>=14||x+count>12||count>size-at)return false;
   while(count--){unsigned p=(y+(tile/2)*14)*24+x+(tile%2)*12;indices[p]=decoded[y*12+x]=b[at++];mask[p]=decoded[168+y*12+x]=255;++x;}
  }
  if(!end)return false;
  bool pinned=false;
  for(unsigned i=0;i<sizeof(global_talon_source)/sizeof(*global_talon_source);i++)if(global_talon_source[i].index==id)pinned=hash(decoded,336)==global_talon_source[i].fnv;
  if(!pinned)return false;
 }
 return true;
}
static bool shop_ship_source(void)
{
 Uint8 indices[672],mask[672];
 return (!shop_ship.bank||(shop_ship.bank==spriteSheet9.data&&shop_ship.bank_size==spriteSheet9.size))&&
  shop_ship_decode(indices,mask)&&palette_count>0&&palette_hash(palettes[0])==PF_PAL&&shop_ship_record();
}
static const GlobalAssetResource *shop_ship_resource(void)
{for(unsigned i=0;i<GLOBAL_ASSET_RESOURCE_COUNT;i++)if(global_asset_resources[i].identity==90233)return global_asset_resources+i;return NULL;}
static void shop_ship_load(void)
{
 if(shop_ship.attempted)return;
 shop_ship.attempted=true;
 if(!shop_ship_requested()||!shop_ship_source())return;
 const GlobalAssetResource *r=shop_ship_resource();char path[1200];Uint8 h[28],extra,*p=NULL;SF_STAT st;bool ok=false;
 if(!r||r->bytes!=172060||r->density!=8||r->width!=24||r->height!=28||r->anchor_x!=5||r->anchor_y!=7)return;
 int n=snprintf(path,sizeof(path),"%s/%s",shop_ship_directory,r->path);if(n<0||(size_t)n>=sizeof(path))return;
 int fd=SF_OPEN(path);if(fd<0)return;
 if(SF_FSTAT(fd,&st)||!SF_REGULAR(st.st_mode)||st.st_size!=172060||SF_READ(fd,h,28)!=28||memcmp(h,"HDR1",4)||
  u32(h+4)!=90233||u32(h+8)!=8||u32(h+12)!=24||u32(h+16)!=28||u32(h+20)!=5||u32(h+24)!=7)goto done;
 p=malloc(172032);if(!p)goto done;size_t at=0;
 while(at<172032){int got=SF_READ(fd,p+at,172032-at);if(got<=0)goto done;at+=(unsigned)got;}
 if(SF_READ(fd,&extra,1)!=0||hash(p,172032)!=r->payload_fnv)goto done;
 ok=true;
 done:if(SF_CLOSE(fd))ok=false;
 if(ok){shop_ship.rgba=p;shop_ship.bank=spriteSheet9.data;shop_ship.bank_size=spriteSheet9.size;}else free(p);
}
static bool shop_ship_valid(void)
{
 if(shop_ship.fault)return false;
 const GlobalAssetResource *r=shop_ship_resource();
 bool ok=shop_ship_requested()&&shop_ship_source()&&r&&shop_ship.rgba&&hash(shop_ship.rgba,172032)==r->payload_fnv;
 if(!ok&&shop_ship.contributed)shop_ship.fault=true;
 return ok;
}
void pregame_shop_ship_begin(unsigned item,int x,int y)
{
 if(shop_ship.armed||shop_ship.blitting){reject();return;}
 if(!sf.product||!sf.updating||sf.stage!=S_BUILD||!exact())return;
 if(shop_ship.used){reject();return;}shop_ship.used=true;
 if(item!=1||item!=player[0].items.ship||x!=player[0].x-5||y!=player[0].y-7||!box(x,y,24,28)||!shop_ship_requested()||!shop_ship_source())return;
 shop_ship_load();if(!shop_ship_valid())return;
 shop_ship.armed=true;shop_ship.item=item;shop_ship.x=x;shop_ship.y=y;
}
static void shop_ship_quad_begin(SDL_Surface *surface,int x,int y,const void *data,size_t size,unsigned quad)
{
 if(shop_ship.blitting){reject();return;}
 if(!shop_ship.armed)return;
 shop_ship.armed=false;
 if(!sf.product||!sf.updating||sf.stage!=S_BUILD||surface!=sf.screen||data!=spriteSheet9.data||size!=spriteSheet9.size||quad!=233||
  x!=shop_ship.x||y!=shop_ship.y||x!=player[0].x-5||y!=player[0].y-7||shop_ship.item!=player[0].items.ship||!exact()||!shop_ship_valid())return;
 Uint8 indices[672],mask[672];if(!shop_ship_decode(indices,mask))return;
 struct SfCommand *c=append(C_SHIP,x,y,9,0,0,0);if(!c)return;c->w=24;c->h=28;
 for(unsigned tile=0;tile<4;tile++)for(unsigned yy=0;yy<14;yy++)for(unsigned xx=0;xx<12;xx++){
  unsigned dx=xx+(tile%2)*12,dy=yy+(tile/2)*14,p=dy*24+dx;
  if(mask[p]&&!event(x+dx,y+dy,indices[p],0))return;
 }
 c->events=sf.event_count-c->first;sf.event_next=c->first;sf.event_limit=sf.event_count;sf.primitive=true;sf.stage=S_PRIMITIVE;
 shop_ship.blitting=shop_ship.contributed=true;
}
static void shop_ship_quad_end(void)
{
 if(!shop_ship.blitting)return;
 shop_ship.blitting=false;pregame_font_glyph_end();
 if(sf.frame&&sf.stage==S_BUILD&&sf.event_next==sf.event_limit)++shop_ship.hits;
}
void pregame_shop_ship_end(void)
{
 if(shop_ship.blitting)reject();
 shop_ship.armed=shop_ship.blitting=false;
}
void pregame_font_quad_begin(SDL_Surface *surface,int x,int y,const void *data,size_t size,unsigned quad)
{
 shop_ship_quad_begin(surface,x,y,data,size,quad);
 if(!shop_ship.blitting)shop_static_quad_begin(surface,x,y,data,size,quad);
}
void pregame_font_quad_end(void)
{if(shop_ship.blitting)shop_ship_quad_end();else shop_static_quad_end();}
