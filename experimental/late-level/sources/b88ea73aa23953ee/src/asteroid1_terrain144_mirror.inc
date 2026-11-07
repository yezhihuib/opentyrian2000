/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional four-part map-E/shapes-Z fixture. Private terrain role144 only.
 * The engine retains all indexed writes, scroll, stars and game state.
 * FNV pins detect accidental source/resource changes, not hostile tampering.
 */
static const unsigned terrain144_ids[4]={429,430,439,440};
static const uint64_t terrain144_source_pins[4]={UINT64_C(0x893197763e81f4f4),UINT64_C(0xa87e4bf5a86a6912),UINT64_C(0x0783ab8f573aeba9),UINT64_C(0x5822b7fb5579332a)};
/* Reviewed density8 RGBA pins. No generic role201 or body asset admission. */
static const uint64_t terrain144_rgba_pins[4]={UINT64_C(0xfa971f5a0beca804),UINT64_C(0x1098b0243ce33365),UINT64_C(0xd45866b7c26097d5),UINT64_C(0x6b7a2f803d4f123a)};
static const unsigned terrain144_placements[5][2]={{6,107},{7,139},{8,158},{9,161},{6,163}};
static struct {
 char map,shape;bool valid;unsigned ids[72];
 bool source_valid[4];Uint8 source[4][672];
} terrain144_registry;
static struct {bool checked,valid,frame_checked;uint64_t checked_tick;char root[1024];Asset members[4];} terrain144_resources;
static struct {bool live,drew;SDL_Surface *surface;size_t first;unsigned row;int x,y;} terrain144_pass;
static int terrain144_member(unsigned id)
{for(unsigned k=0;k<4;k++)if(id==terrain144_ids[k])return (int)k;return -1;}
/* Only real loader slots qualify; clones and pointers into a tile do not. */
static int terrain144_source_slot(const Uint8 *data)
{
 uintptr_t base=(uintptr_t)&megaData1.shapes[0],p=(uintptr_t)data;
 size_t stride=sizeof(megaData1.shapes[0]);
 if(!data||p<base||p-base>=sizeof(megaData1.shapes)||(p-base)%stride)return -1;
 unsigned slot=(unsigned)((p-base)/stride);
 return data==megaData1.shapes[slot].sh?(int)slot:-1;
}
static void terrain144_map_reset(char map,char shape)
{
 memset(&terrain144_registry,0,sizeof(terrain144_registry));
 terrain144_registry.map=map;terrain144_registry.shape=shape;terrain144_registry.valid=true;
 memset(&terrain144_pass,0,sizeof(terrain144_pass));terrain144_draw_lease=NULL;
}
void render_mirror_asteroid_terrain_map(char map,char shape)
{terrain144_map_reset(map,shape);}
static void terrain144_shutdown(void)
{
 for(unsigned k=0;k<4;k++)free(terrain144_resources.members[k].rgba);
 memset(&terrain144_resources,0,sizeof(terrain144_resources));terrain144_map_reset(0,0);
}
static void terrain144_bind(unsigned layer,unsigned id,const Uint8 *data)
{
 if(terrain144_registry.map!='E'||terrain144_registry.shape!='Z'||layer!=1)return;
 int slot=terrain144_source_slot(data),member=terrain144_member(id);
 if(slot<0||!id||id>600||terrain144_registry.ids[slot]) {terrain144_registry.valid=false;return;}
 terrain144_registry.ids[slot]=id;
 if(member<0)return;
 if(!terrain144_registry.source_valid[member]) {
  memcpy(terrain144_registry.source[member],data,672);
  terrain144_registry.source_valid[member]=asteroid1_stamp(terrain144_registry.source[member],672)==terrain144_source_pins[member];
 }
 if(!terrain144_registry.source_valid[member]||memcmp(data,terrain144_registry.source[member],672))terrain144_registry.valid=false;
}
static unsigned terrain144_id(const Uint8 *data)
{int slot=terrain144_source_slot(data);return slot<0?0:terrain144_registry.ids[slot];}
static bool terrain144_sources_valid(void)
{
 if(!terrain144_registry.valid||terrain144_registry.map!='E'||terrain144_registry.shape!='Z'||terrain_file!='z')return false;
 for(unsigned k=0;k<4;k++)if(!terrain144_registry.source_valid[k])return false;
 /* Recheck every real registered duplicate, not just the selected map pointer. */
 for(unsigned slot=0;slot<72;slot++) {
  unsigned id=terrain144_registry.ids[slot];int k=terrain144_member(id);
  if(!id)return false;
  if(k>=0&&memcmp(megaData1.shapes[slot].sh,terrain144_registry.source[k],672))return false;
 }
 return true;
}
static bool terrain144_map_valid(void)
{
 /* Serialize all4200 identities in explicit little-endian order. This fixes
  * the original map, including blank cells and all twenty admitted positions. */
 uint64_t hash=UINT64_C(0xcbf29ce484222325);
 for(unsigned y=0;y<300;y++)for(unsigned x=0;x<14;x++) {
  unsigned id=terrain144_id(megaData1.mainmap[y][x]);if(!id)return false;
  hash^=id&255;hash*=UINT64_C(0x100000001b3);
  hash^=id>>8;hash*=UINT64_C(0x100000001b3);
 }
 if(hash!=UINT64_C(0x7307135aa8e8807d))return false;
 for(unsigned p=0;p<5;p++)for(unsigned k=0;k<4;k++) {
  unsigned x=terrain144_placements[p][0]+k%2,y=terrain144_placements[p][1]+k/2;
  if(terrain144_id(megaData1.mainmap[y][x])!=terrain144_ids[k])return false;
 }
 return true;
}
static bool terrain144_load(unsigned k,Asset *result)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/terrain-shapesz-%u-8.hda",terrain144_resources.root,terrain144_ids[k]);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)24*28*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1_TERRAIN144*10000+terrain144_ids[k]&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==terrain144_rgba_pins[k];
 /* All672 original indexed cells are covered. Opaque replacement support
  * must match that full support exactly, including each internal tile seam. */
 if(ok)for(size_t i=3;i<bytes;i+=4)if(rgba[i]!=255){ok=false;break;}
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *result=(Asset){true,true,ASSET_ASTEROID1_TERRAIN144,(int)terrain144_ids[k],24,28,0,0,8,rgba};return true;
}
static bool terrain144_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!*game_probe_assets||strlen(game_probe_assets)>=sizeof(terrain144_resources.root))return false;
 if(!terrain144_resources.checked) {
  terrain144_resources.checked=true;memcpy(terrain144_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  Asset loaded[4]={{0}};bool ok=true;
  for(unsigned k=0;k<4;k++)if(!terrain144_load(k,&loaded[k])){ok=false;break;}
  if(ok)memcpy(terrain144_resources.members,loaded,sizeof(loaded));else for(unsigned k=0;k<4;k++)free(loaded[k].rgba);
  terrain144_resources.valid=ok;
 }
 if(!terrain144_resources.valid||strcmp(terrain144_resources.root,game_probe_assets))return false;
 for(unsigned k=0;k<4;k++) {
  Asset *a=&terrain144_resources.members[k];
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_TERRAIN144||a->index!=(int)terrain144_ids[k]||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   ((!terrain144_resources.frame_checked||terrain144_resources.checked_tick!=mirror_logic_tick)&&
    asteroid1_stamp(a->rgba,(size_t)24*28*8*8*4)!=terrain144_rgba_pins[k])) {terrain144_resources.valid=false;return false;}
 }
 /* Like the existing finite families, current RGBA bytes are checked once per
  * logic tick. Source/map pointers and indexed bytes remain checked each row. */
 terrain144_resources.frame_checked=true;terrain144_resources.checked_tick=mirror_logic_tick;
 return true;
}
static bool terrain144_context(SDL_Surface *surface)
{
 return asteroid_hd_enabled&&asteroid1_level_scope()&&!play_demo&&
  (game_probe_enabled||(asteroid_hd_lease&&asteroid1_scope()))&&active&&!reject_reason&&
  (game_probe_scene_assets&2)&&surface&&surface==game_screen&&surface==VGAScreen&&
  surface->pixels&&surface->w==320&&surface->h==200&&surface->pitch==320&&surface->format&&
  surface->format->format==SDL_PIXELFORMAT_INDEX8&&surface->format->BitsPerPixel==8&&surface->format->BytesPerPixel==1;
}
/* Called only immediately before draw_background_1's eight ordered rows. */
void render_mirror_asteroid_terrain_layer1(SDL_Surface *surface,const void *first,int x,int y)
{
 memset(&terrain144_pass,0,sizeof(terrain144_pass));terrain144_draw_lease=NULL;
 if(!terrain144_context(surface)||x<0||x>32||y<-28||y>-1||x!=mapXPos||y!=(int)backPos-28)return;
 uintptr_t base=(uintptr_t)&megaData1.mainmap[0][0],p=(uintptr_t)first;
 if(p<base||p-base>=sizeof(megaData1.mainmap)||(p-base)%sizeof(JE_byte *))return;
 size_t cell=(p-base)/sizeof(JE_byte *);
 if(cell%14>2||cell/14>292||mapXbpPos<0||mapXbpPos>15||
  p!=(uintptr_t)mapYPos+(mapXbpPos-12)*(intptr_t)sizeof(JE_byte *))return;
 if(!terrain144_sources_valid()||!terrain144_map_valid())return;
 bool visible=false;
 for(unsigned row=0;row<8;row++)for(unsigned tile=0;tile<12;tile++) {
  size_t at=cell+row*14+tile;
  if(terrain144_member(terrain144_id(megaData1.mainmap[at/14][at%14]))>=0)visible=true;
 }
 if(!visible||!terrain144_family_ready())return;
 terrain144_pass.live=true;terrain144_pass.surface=surface;terrain144_pass.first=cell;terrain144_pass.x=x;terrain144_pass.y=y;
}
void render_mirror_asteroid_terrain_end(void)
{terrain144_pass.live=false;terrain144_draw_lease=NULL;}
static unsigned terrain144_row(SDL_Surface *surface,int x,int y,Uint8 **map,int style)
{
 if(!terrain144_pass.live)return 0;
 if(!terrain144_context(surface)||surface!=terrain144_pass.surface||style!=MIRROR_NORMAL||
  terrain144_pass.row>=8||x!=terrain144_pass.x||y!=terrain144_pass.y+(int)terrain144_pass.row*28||
  (uintptr_t)map!=(uintptr_t)&megaData1.mainmap[0][0]+(terrain144_pass.first+terrain144_pass.row*14)*sizeof(JE_byte *)||
  !terrain144_sources_valid()||!terrain144_map_valid()||!terrain144_family_ready()) {
  if(terrain144_pass.drew)render_mirror_unsupported("terrain144-pass-integrity");
  render_mirror_asteroid_terrain_end();return 0;
 }
 terrain144_pass.row++;unsigned replaced=0;
 for(unsigned tile=0;tile<12;tile++) {
  int k=terrain144_member(terrain144_id(map[tile]));if(k<0)continue;
  Asset *a=&terrain144_resources.members[k];terrain144_draw_lease=a;
  bool mirrored=draw_asset_filtered(x+(int)tile*24,y,a,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);
  terrain144_draw_lease=NULL;suppress=false;suppress_cloud=false;suppress_green_smoke=false;
  if(mirrored){replaced|=1u<<tile;terrain144_pass.drew=true;}
  game_probe_scene_draw(ASSET_ASTEROID1_TERRAIN144,terrain144_ids[k],x+(int)tile*24,y,0,MIRROR_NORMAL,mirrored);
 }
 return replaced;
}
