/* SPDX-License-Identifier: GPL-2.0-or-later
 * SHOP-only Vulcan composition. No battle permission and no replacement draw:
 * the original blitter still writes every indexed sample, witnessed in order.
 */
static char shop_vulcan_directory[1024];
static struct {
 Uint8 *rgba[2];const void *bank;size_t bank_size;
 bool attempted,good,armed,blitting,contributed,frame_fault;unsigned slot,index;int x,y;
 uint64_t hits;
} shop_vulcan_art;
static size_t shop_vulcan_art_static_bytes(void)
{return sizeof(shop_vulcan_art)+sizeof(shop_vulcan_directory);}
static size_t shop_vulcan_art_bytes(void)
{size_t n=sizeof(shop_vulcan_art)+sizeof(shop_vulcan_directory);for(unsigned i=0;i<2;i++)if(shop_vulcan_art.rgba[i])n+=43008;return n;}
static void shop_vulcan_art_reset(void)
{for(unsigned i=0;i<2;i++)free(shop_vulcan_art.rgba[i]);memset(&shop_vulcan_art,0,sizeof(shop_vulcan_art));}
void pregame_shop_vulcan_set_directory(const char *path)
{
 size_t n=path?strlen(path):0;if(n<sizeof(shop_vulcan_directory)&&!strcmp(shop_vulcan_directory,path?path:""))return;
 /* Retire commands already contributed; a new root cannot revive this frame. */
 bool retired=shop_vulcan_art.contributed||shop_vulcan_art.frame_fault;
 if(shop_vulcan_art.armed||shop_vulcan_art.blitting)reject();
 shop_vulcan_art_reset();shop_vulcan_art.frame_fault=retired;shop_vulcan_reset();shop_vulcan_directory[0]=0;
 if(n&&n<sizeof(shop_vulcan_directory))memcpy(shop_vulcan_directory,path,n+1);
}
static bool shop_vulcan_requested(void)
{return shop_vulcan_directory[0]&&!game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid;}
static bool shop_vulcan_decode(unsigned index,Uint8 out[336])
{
 Sprite2_array bank=spriteSheet8;memset(out,0,336);
 if(!bank.data||bank.size!=GLOBAL_VULCAN_BANK_BYTES||!index||2u*index>bank.size)return false;
 size_t pos=bank.data[2*(index-1)]|((size_t)bank.data[2*(index-1)+1]<<8);int x=0,y=0;
 for(size_t guard=0;guard<bank.size&&pos<bank.size;guard++){
  unsigned code=bank.data[pos++];if(code==15)return true;x+=code&15;unsigned n=code>>4;
  if(!n){++y;x-=12;}
  else for(unsigned j=0;j<n;j++){
   if(pos>=bank.size||x<0||x>=12||y<0||y>=14)return false;
   out[y*12+x]=bank.data[pos++];out[168+y*12+x]=255;++x;
  }
 }
 return false;
}
static const GlobalAssetResource *shop_vulcan_resource(unsigned i)
{for(unsigned j=0;j<GLOBAL_ASSET_RESOURCE_COUNT;j++)if(global_asset_resources[j].identity==global_vulcan_resource_ids[i])return &global_asset_resources[j];return NULL;}
static bool shop_vulcan_source_valid(void)
{
 if(!spriteSheet8.data||spriteSheet8.size!=GLOBAL_VULCAN_BANK_BYTES)return false;
 if(shop_vulcan_art.bank&&(shop_vulcan_art.bank!=spriteSheet8.data||shop_vulcan_art.bank_size!=spriteSheet8.size))return false;
 for(unsigned i=0;i<2;i++){Uint8 decoded[336];if(!shop_vulcan_decode(global_vulcan_source[i].index,decoded)||hash(decoded,336)!=global_vulcan_source[i].fnv)return false;}
 for(unsigned i=0;i<sizeof(global_vulcan_palette)/sizeof(global_vulcan_palette[0]);i++){
  unsigned index=global_vulcan_palette[i].index;SDL_Color p=palettes[0][index];
  if((((Uint32)p.r<<16)|((Uint32)p.g<<8)|p.b)!=global_vulcan_palette[i].rgb)return false;
 }
 return true;
}
static void shop_vulcan_art_load(void)
{
 if(shop_vulcan_art.attempted)return;shop_vulcan_art.attempted=true;shop_vulcan_art.good=true;
 shop_vulcan_art.bank=spriteSheet8.data;shop_vulcan_art.bank_size=spriteSheet8.size;
 for(unsigned i=0;i<2;i++){
  const GlobalAssetResource *r=shop_vulcan_resource(i);char path[1200];
  if(!r||r->bytes!=43036||r->density!=8||r->width!=12||r->height!=14||r->anchor_x!=0||r->anchor_y||
   snprintf(path,sizeof(path),"%s/%s",shop_vulcan_directory,r->path)>=(int)sizeof(path)){shop_vulcan_art.good=false;break;}
  Uint8 *p=shared_asset_load_fd(path,r,false);
  if(!p){shop_vulcan_art.good=false;break;}shop_vulcan_art.rgba[i]=p;
 }
 if(!shop_vulcan_art.good)for(unsigned i=0;i<2;i++){free(shop_vulcan_art.rgba[i]);shop_vulcan_art.rgba[i]=NULL;}
}
static bool shop_vulcan_art_valid(void)
{
 if(shop_vulcan_art.frame_fault)return false;
 if(!shop_vulcan_requested()||!shop_vulcan_art.good||!shop_vulcan_source_valid()||!shop_vulcan_records_valid()){if(shop_vulcan_art.contributed)shop_vulcan_art.frame_fault=true;return false;}
 for(unsigned i=0;i<2;i++){const GlobalAssetResource *r=shop_vulcan_resource(i);if(!r||!shop_vulcan_art.rgba[i]||hash(shop_vulcan_art.rgba[i],43008)!=r->payload_fnv){if(shop_vulcan_art.contributed)shop_vulcan_art.frame_fault=true;return false;}}
 return true;
}
void pregame_shop_vulcan_preview_begin(void)
{
 shop_vulcan_art.armed=shop_vulcan_art.blitting=shop_vulcan_art.contributed=shop_vulcan_art.frame_fault=false;
 shop_vulcan_preview_begin(sf.product&&sf.category==3&&sf.updating&&sf.stage==S_BUILD&&exact()&&shop_vulcan_requested());
}
void pregame_shop_vulcan_preview_end(void)
{shop_vulcan_art.armed=false;shop_vulcan_preview_end();}
void pregame_shop_vulcan_head_begin(unsigned slot,unsigned index,int x,int y)
{
 shop_vulcan_art.armed=false;
 /* An observed loss must retire earlier commands even if this head fails early. */
 if(shop_vulcan_art.contributed)(void)shop_vulcan_art_valid();
 if(!shop_vulcan_head(slot,index,x,y)||!sf.product||sf.category!=3||!sf.updating||sf.stage!=S_BUILD||!exact()||
    !box(x,y,12,14)||x+12>154||y+14>185||!shop_vulcan_requested()||!shop_vulcan_source_valid())return;
 shop_vulcan_art_load();if(!shop_vulcan_art_valid())return;
 for(unsigned i=0;i<2;i++)if(global_vulcan_source[i].index==index){shop_vulcan_art.armed=true;shop_vulcan_art.slot=i;shop_vulcan_art.index=index;shop_vulcan_art.x=x;shop_vulcan_art.y=y;return;}
}
static void shop_vulcan_blit_begin(SDL_Surface *surface,int x,int y,const void *data,size_t size,unsigned index)
{
 if(shop_vulcan_art.contributed)(void)shop_vulcan_art_valid();
 if(!shop_vulcan_art.armed)return;shop_vulcan_art.armed=false;
 if(!shop_vulcan_art_valid())return;
 if(surface!=sf.screen||data!=spriteSheet8.data||size!=spriteSheet8.size||index!=shop_vulcan_art.index||x!=shop_vulcan_art.x||y!=shop_vulcan_art.y||!exact()||sf.stage!=S_BUILD)return;
 Uint8 decoded[336];if(!shop_vulcan_decode(index,decoded))return;
 struct SfCommand *c=append(C_VULCAN,x,y,8,shop_vulcan_art.slot,0,0);if(!c)return;c->w=12;c->h=14;
 for(unsigned yy=0;yy<14;yy++)for(unsigned xx=0;xx<12;xx++)if(decoded[168+yy*12+xx]&&!event(x+xx,y+yy,decoded[yy*12+xx],0))return;
 c->events=sf.event_count-c->first;sf.event_next=c->first;sf.event_limit=sf.event_count;sf.primitive=true;sf.stage=S_PRIMITIVE;shop_vulcan_art.blitting=shop_vulcan_art.contributed=true;
}
void pregame_shop_vulcan_head_end(void)
{
 if(shop_vulcan_art.blitting&&sf.frame&&sf.stage==S_BUILD&&sf.event_next==sf.event_limit)++shop_vulcan_art.hits;
 shop_vulcan_art.armed=shop_vulcan_art.blitting=false;
}

/* Alpha-weighted 2x2 area reduction of the accepted 8x resource to this
 * owner's fixed 4x canvas; anchor metadata is already baked into pixels. */
static Uint32 shop_vulcan_sample(const Uint8 *data,unsigned x,unsigned y,unsigned *alpha)
{
 unsigned a=0,c[3]={0,0,0};
 for(unsigned yy=0;yy<2;yy++)for(unsigned xx=0;xx<2;xx++){const Uint8 *v=data+((y*2+yy)*96+x*2+xx)*4;a+=v[3];for(unsigned k=0;k<3;k++)c[k]+=v[k]*v[3];}
 *alpha=(a+2)/4;if(!a)return 0;Uint32 color=0;
 for(unsigned k=0;k<3;k++)color|=(((c[k]+a/2)/a*sf.metal_gain+127)/255)<<(16-k*8);
 return color;
}
