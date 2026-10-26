/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite shapesY gray platforms. Native water is an ordered indexed callback,
 * not transparency over a previous scene. No new indexed writes or owners. */
#include "current_shapesy_platform_source.h"
#include "current_shapesy_platform_hd_assets.h"
static struct { bool valid; unsigned ids[72]; bool seen[28]; Uint8 source[28][672]; } shapesy_registry;
static struct { bool checked,valid; char root[1024]; Asset members[28]; uint64_t generation; } shapesy_resources;
static struct { bool live,drew; SDL_Surface *surface; size_t first; unsigned row; int x,y; uint64_t generation; Uint32 palette[256]; const Uint8 *sources[8][12]; unsigned replaced[8]; VideoOutputGeometry geometry; } shapesy_pass;
static struct { bool live; SDL_Surface *surface; uint64_t generation; Uint32 palette[256]; VideoOutputGeometry geometry; } shapesy_frame;
static struct { bool live; unsigned replaced; int x,y; uint64_t generation; const Uint8 *sources[12]; } shapesy_row_lease;
/* Typed opaque values written only by the guarded ShapesY layer1/edge path.
 * Zero means untyped. Exact sampled-value equality prevents a later foreign
 * writer from lending changed RGB; a same-valued write is equivalent to this
 * still-proven terrain value. The sealed witness survives cached Present only
 * until a frame/map/root/reset, and never grants another owner by itself. */
static struct {
 Uint32 *values;size_t capacity;bool building,sealed,failed;
 uint64_t serial,generation,tick;
 SDL_Surface *canvas_surface,*index_surface;void *pixels,*index_pixels;
 SDL_PixelFormat *format,*index_format;int w,h,pitch,index_pitch;
 VideoOutputGeometry geometry;
} shapesy_borrow;
static uint64_t shapesy_borrow_serial;
static void shapesy_borrow_retire(void)
{shapesy_borrow.building=shapesy_borrow.sealed=false;}
static void shapesy_borrow_begin(void)
{
 shapesy_borrow_retire();shapesy_borrow.failed=false;
 if(!canvas||!canvas->pixels||!canvas->format||canvas->w!=2560||canvas->h!=1600||
    canvas->pitch<2560*4||canvas->pitch%4||canvas->format->format!=SDL_PIXELFORMAT_ARGB8888)return;
 const size_t count=320u*200u*8u*8u;
 if(shapesy_borrow.capacity!=count){
  Uint32 *values=calloc(count,sizeof(Uint32));if(!values)return;
  free(shapesy_borrow.values);shapesy_borrow.values=values;shapesy_borrow.capacity=count;
 }
 memset(shapesy_borrow.values,0,count*sizeof(Uint32));
 if(++shapesy_borrow_serial==0)++shapesy_borrow_serial;
 shapesy_borrow.serial=shapesy_borrow_serial;shapesy_borrow.building=true;
}
static void shapesy_borrow_mark(size_t n,Uint32 color)
{
 if(!shapesy_borrow.building)return;
 if(n>=shapesy_borrow.capacity||(color>>24)!=255){shapesy_borrow.failed=true;return;}
 shapesy_borrow.values[n]=color;
}
static void shapesy_borrow_seal(void)
{
 if(!shapesy_borrow.building||shapesy_borrow.failed||!shapesy_frame.live){shapesy_borrow_retire();return;}
 shapesy_borrow.building=false;shapesy_borrow.sealed=true;
 shapesy_borrow.generation=shapesy_resources.generation;shapesy_borrow.tick=mirror_logic_tick;
 shapesy_borrow.canvas_surface=canvas;shapesy_borrow.pixels=canvas->pixels;shapesy_borrow.format=canvas->format;
 shapesy_borrow.w=canvas->w;shapesy_borrow.h=canvas->h;shapesy_borrow.pitch=canvas->pitch;
 shapesy_borrow.index_surface=game_screen;shapesy_borrow.index_pixels=game_screen->pixels;
 shapesy_borrow.index_format=game_screen->format;shapesy_borrow.index_pitch=game_screen->pitch;
 shapesy_borrow.geometry=shapesy_frame.geometry;
}
static int shapesy_member(unsigned id)
{for(unsigned k=0;k<28;k++)if(id==shapesy_ids[k])return (int)k;return -1;}
static int shapesy_source_slot(const Uint8 *data)
{
 uintptr_t base=(uintptr_t)&megaData1.shapes[0],p=(uintptr_t)data;
 size_t stride=sizeof(megaData1.shapes[0]);
 if(!data||p<base||p-base>=sizeof(megaData1.shapes)||(p-base)%stride)return -1;
 unsigned slot=(unsigned)((p-base)/stride);
 return data==megaData1.shapes[slot].sh?(int)slot:-1;
}
void render_mirror_shapesy_row_end(void)
{memset(&shapesy_row_lease,0,sizeof(shapesy_row_lease));shapesy_draw_lease=NULL;}
static bool shapesy_context(SDL_Surface *surface),shapesy_cache_valid(void);
static bool shapesy_geometry(VideoOutputGeometry *out)
{ return video_output_geometry(out) && (out->scale == 2 || out->scale == 4); }
static bool shapesy_geometry_matches(const VideoOutputGeometry *expected_geometry)
{
 VideoOutputGeometry current;
 return shapesy_geometry(&current) && video_output_geometry_equal(&current, expected_geometry);
}
static const char *shapesy_edge_aa(void);
static void shapesy_world_reset(void);
static bool shapesy_world_prepare(void), shapesy_world_check(void);
void render_mirror_shapesy_end(void)
{
 /* Validate after the original callbacks and before any later layer/Present.
  * A mutation after HD drawing rejects the entire mirror frame, not INDEX8. */
 bool bad=shapesy_pass.live&&shapesy_pass.drew&&!reject_reason&&
  (!shapesy_context(shapesy_pass.surface)||shapesy_pass.generation!=shapesy_resources.generation||!shapesy_cache_valid()||!shapesy_world_check());
 const char *edge_bad=NULL;
 if(!bad&&!reject_reason&&shapesy_pass.live&&shapesy_pass.drew&&shapesy_pass.row==8)edge_bad=shapesy_edge_aa();
 bool had_pass=shapesy_pass.live,seal=had_pass&&shapesy_pass.drew&&shapesy_pass.row==8&&!bad&&!edge_bad&&!reject_reason;
 render_mirror_shapesy_row_end();memset(&shapesy_pass,0,sizeof(shapesy_pass));shapesy_clear_proof=false;
 if(seal)shapesy_borrow_seal();else if(had_pass)shapesy_borrow_retire();
 if(bad||edge_bad)render_mirror_unsupported(edge_bad?edge_bad:"shapesy-pass-final-integrity");
}
static void shapesy_frame_reset(void)
{render_mirror_shapesy_end();shapesy_borrow_retire();memset(&shapesy_frame,0,sizeof(shapesy_frame));}
static void shapesy_map_reset(void)
{
 shapesy_frame_reset();shapesy_world_reset();
 for(unsigned k=0;k<28;k++)free(shapesy_resources.members[k].rgba);
 memset(&shapesy_resources,0,sizeof(shapesy_resources));
 memset(&shapesy_registry,0,sizeof(shapesy_registry));shapesy_registry.valid=true;
}
static void shapesy_shutdown(void)
{shapesy_map_reset();free(shapesy_borrow.values);memset(&shapesy_borrow,0,sizeof(shapesy_borrow));}
static void shapesy_bind(unsigned layer,unsigned id,const Uint8 *data)
{
 if((terrain_file!='Y'&&terrain_file!='y')||layer!=1)return;
 int slot=shapesy_source_slot(data),k=shapesy_member(id);
 if(slot<0||!id||id>600||shapesy_registry.ids[slot]){shapesy_registry.valid=false;return;}
 shapesy_registry.ids[slot]=id;
 if(k<0)return;
 if(asteroid1_stamp(data,672)!=shapesy_source_pins[k]){shapesy_registry.valid=false;return;}
 if(shapesy_registry.seen[k]&&memcmp(data,shapesy_registry.source[k],672)){shapesy_registry.valid=false;return;}
 memcpy(shapesy_registry.source[k],data,672);shapesy_registry.seen[k]=true;
}
static unsigned shapesy_id(const Uint8 *data)
{int slot=shapesy_source_slot(data);return slot<0?0:shapesy_registry.ids[slot];}
static bool shapesy_sources_valid(void)
{
 if(!shapesy_registry.valid||(terrain_file!='Y'&&terrain_file!='y'))return false;
 /* Every actual alias is rechecked, including offscreen duplicate slots. */
 for(unsigned slot=0;slot<72;slot++) {
  int k=shapesy_member(shapesy_registry.ids[slot]);
  if(k>=0&&(!shapesy_registry.seen[k]||memcmp(megaData1.shapes[slot].sh,shapesy_registry.source[k],672)))return false;
 }
 return true;
}
static bool shapesy_palette(void)
{
 uint64_t h=UINT64_C(0xcbf29ce484222325);
 for(unsigned i=0;i<256;i++)for(int s=16;s>=0;s-=8){h^=(rgb_palette[i]>>s)&255;h*=UINT64_C(0x100000001b3);}
 return h==SHAPESY_PALETTE_FNV;
}
static bool shapesy_context_base(SDL_Surface *surface)
{
 if((terrain_file!='Y'&&terrain_file!='y')||!shapesy_registry.valid||asteroid_hd_enabled||!active||reject_reason||!(game_probe_scene_assets&2)||game_probe_density!=8||
    game_probe_missing||game_probe_invalid||game_probe_original_reference||!game_probe_assets||!*game_probe_assets||
    !surface||surface!=game_screen||surface!=VGAScreen||!surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||
    !surface->format||surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
    surface->clip_rect.x||surface->clip_rect.y||surface->clip_rect.w!=320||surface->clip_rect.h!=200||
    filterFade||levelFilter!=-99||levelBrightness!=-99)return false;
 /* The engine leaves filterActive=true after the opening fade. With both
  * sentinel parameters -99 and no fade, JE_filterScreen performs no work. */
 for(unsigned i=0;i<9;i++)if(smoothies[i])return false;
 return true;
}
static bool shapesy_context(SDL_Surface *surface)
{return shapesy_context_base(surface)&&shapesy_palette()&&shapesy_sources_valid()&&
 (!shapesy_pass.live||shapesy_geometry_matches(&shapesy_pass.geometry));}
static bool shapesy_rgba_valid(unsigned k,const Uint8 *rgba)
{
 if(!rgba||asteroid1_stamp(rgba,24*28*8*8*4)!=shapesy_rgba_pins[k])return false;
 /* Geometry is source semantics, never inferred from artwork colors. Missing
  * source members cannot validate alpha; first scope requires all28 bindings. */
 if(!shapesy_registry.seen[k])return false;
 for(unsigned y=0;y<224;y++)for(unsigned x=0;x<192;x++) {
  unsigned v=shapesy_registry.source[k][(y/8)*24+x/8];const Uint8 *p=rgba+(y*192+x)*4;
  if(v>=48&&v<=63){if(p[0]||p[1]||p[2]||p[3])return false;}
  else if(p[3]!=255||(!v&&(p[0]||p[1]||p[2])))return false;
 }
 return true;
}
static bool shapesy_load(unsigned k,Asset *result)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/terrain-shapesy-%u-8.hda",shapesy_resources.root,shapesy_ids[k]);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)24*28*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_SHAPESY_PLATFORM*10000+shapesy_ids[k]&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&shapesy_rgba_valid(k,rgba);
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *result=(Asset){true,true,ASSET_SHAPESY_PLATFORM,(int)shapesy_ids[k],24,28,0,0,8,rgba};return true;
}
static bool shapesy_family_ready(void)
{
 if(!game_probe_assets||strlen(game_probe_assets)>=sizeof(shapesy_resources.root))return false;
 for(unsigned k=0;k<28;k++)if(!shapesy_registry.seen[k])return false;
 if(!shapesy_resources.checked){
  shapesy_resources.checked=true;strcpy(shapesy_resources.root,game_probe_assets);
  Asset loaded[28]={{0}};bool ok=true;
  for(unsigned k=0;k<28;k++)if(!shapesy_load(k,&loaded[k])){ok=false;break;}
  if(ok)memcpy(shapesy_resources.members,loaded,sizeof(loaded));else for(unsigned k=0;k<28;k++)free(loaded[k].rgba);
  shapesy_resources.valid=ok;
 }
 if(!shapesy_resources.valid||strcmp(shapesy_resources.root,game_probe_assets))return false;
 if(!shapesy_cache_valid())return false;
 shapesy_resources.generation++;return true;
}
/* All resources revalidated before and after every real pass. No per-pixel
 * 4.8MB scans; cached mutation during a pass rejects it before presentation. */
static bool shapesy_cache_valid(void)
{
 if(!shapesy_resources.valid||!game_probe_assets||strcmp(shapesy_resources.root,game_probe_assets))return false;
 for(unsigned k=0;k<28;k++) {
  Asset *a=&shapesy_resources.members[k];
  if(!a->initialized||!a->valid||a->bank!=ASSET_SHAPESY_PLATFORM||a->index!=(int)shapesy_ids[k]||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!shapesy_rgba_valid(k,a->rgba)){
   shapesy_resources.valid=false;return false;}
 }
 return true;
}

void render_mirror_shapesy_layer1(SDL_Surface *surface,const void *first,int x,int y)
{
 bool cleared=shapesy_clear_proof;render_mirror_shapesy_end();shapesy_borrow_retire();
 if(cleared)memset(&shapesy_frame,0,sizeof(shapesy_frame));
 if(!cleared||!shapesy_context(surface)||x<0||x>32||y<-28||y>-1||x!=mapXPos||y!=(int)backPos-28)return;
 uintptr_t base=(uintptr_t)&megaData1.mainmap[0][0],p=(uintptr_t)first;
 if(p<base||p-base>=sizeof(megaData1.mainmap)||(p-base)%sizeof(JE_byte *))return;
 size_t cell=(p-base)/sizeof(JE_byte *);
 if(cell%14>2||cell/14>292||mapXbpPos<0||mapXbpPos>15||p!=(uintptr_t)mapYPos+(mapXbpPos-12)*(intptr_t)sizeof(JE_byte *))return;
 for(unsigned row=0;row<8;row++)for(unsigned tile=0;tile<12;tile++){
  size_t at=cell+row*14+tile;const Uint8 *s=megaData1.mainmap[at/14][at%14];
  if(s&&!shapesy_id(s))return;
 }
 VideoOutputGeometry geometry;
 if(!shapesy_geometry(&geometry)||!shapesy_family_ready()||!shapesy_world_prepare())return;
 shapesy_borrow_begin();
 shapesy_pass.geometry=geometry;
 shapesy_pass.live=true;shapesy_pass.surface=surface;shapesy_pass.first=cell;shapesy_pass.x=x;shapesy_pass.y=y;
 shapesy_pass.generation=shapesy_resources.generation;memcpy(shapesy_pass.palette,rgb_palette,sizeof(shapesy_pass.palette));
}
static bool shapesy_zero_underlay(const Uint8 *source,int x,int y)
{
 for(unsigned i=0;i<672;i++)if(!source[i]) {
  int dx=x+(int)(i%24),dy=y+(int)(i/24);if(dx<0||dx>=320||dy<0||dy>=200)continue;
  if(((Uint8 *)game_screen->pixels)[dy*game_screen->pitch+dx]||expected[dy*320+dx])return false;
  for(int yy=0;yy<8;yy++)for(int xx=0;xx<8;xx++){
   int at=(dy*8+yy)*canvas->w+dx*8+xx;
   Uint32 c=*((Uint32 *)((Uint8 *)canvas->pixels+(dy*8+yy)*canvas->pitch)+dx*8+xx);
   if(hd_owner[at]||cloud_owner[at]||c!=palette_rgb(0))return false;
  }
 }
 return true;
}
static unsigned shapesy_row(SDL_Surface *surface,int x,int y,Uint8 **map,int style)
{
 render_mirror_shapesy_row_end();if(!shapesy_pass.live)return 0;
 if(!shapesy_context(surface)||surface!=shapesy_pass.surface||style!=MIRROR_NORMAL||shapesy_pass.row>=8||x!=shapesy_pass.x||
  y!=shapesy_pass.y+(int)shapesy_pass.row*28||(uintptr_t)map!=(uintptr_t)&megaData1.mainmap[0][0]+(shapesy_pass.first+shapesy_pass.row*14)*sizeof(JE_byte *)){
  if(shapesy_pass.drew)render_mirror_unsupported("shapesy-pass-integrity");
  render_mirror_shapesy_end();return 0;}
 /* Reject clones/offsets and source mutation before any tile in this row. */
 for(unsigned tile=0;tile<12;tile++)if(map[tile]){
  unsigned id=shapesy_id(map[tile]);if(!id||(shapesy_member(id)>=0&&!shapesy_zero_underlay(map[tile],x+(int)tile*24,y))){
   if(shapesy_pass.drew)render_mirror_unsupported("shapesy-source-or-zero");
   render_mirror_shapesy_end();return 0;}
 }
 shapesy_pass.row++;unsigned replaced=0;
 for(unsigned tile=0;tile<12;tile++){
  int k=shapesy_member(shapesy_id(map[tile]));if(k<0)continue;
  Asset *a=&shapesy_resources.members[k];shapesy_draw_lease=a;
  bool mirrored=draw_asset_filtered(x+(int)tile*24,y,a,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);
  shapesy_draw_lease=NULL;suppress=false;suppress_cloud=false;suppress_green_smoke=false;
  /* Unsupported drawing can reset the pass (including its row ordinal). */
  if(!shapesy_pass.live||reject_reason)return 0;
  if(mirrored){
   replaced|=1u<<tile;shapesy_pass.drew=true;shapesy_frame.live=true;
   shapesy_frame.surface=surface;shapesy_frame.generation=shapesy_pass.generation;
   shapesy_frame.geometry=shapesy_pass.geometry;
   memcpy(shapesy_frame.palette,shapesy_pass.palette,sizeof(shapesy_frame.palette));
  }
  game_probe_scene_draw(ASSET_SHAPESY_PLATFORM,shapesy_ids[k],x+(int)tile*24,y,0,MIRROR_NORMAL,mirrored);
 }
 shapesy_pass.replaced[shapesy_pass.row-1]=replaced;
 for(unsigned t=0;t<12;t++)shapesy_pass.sources[shapesy_pass.row-1][t]=map[t];
 shapesy_row_lease.live=true;shapesy_row_lease.replaced=replaced;shapesy_row_lease.x=x;shapesy_row_lease.y=y;
 shapesy_row_lease.generation=shapesy_pass.generation;
 for(unsigned t=0;t<12;t++)shapesy_row_lease.sources[t]=map[t];
 return replaced;
}
static bool shapesy_native_water(SDL_Surface *surface,Uint8 *address,Uint8 source,int style,bool replaced,bool *qualified)
{
 if(qualified)*qualified=false;
 if(reject_reason||!replaced||!shapesy_pass.live||!shapesy_row_lease.live||surface!=shapesy_pass.surface||style!=MIRROR_NORMAL)return false;
 if(!shapesy_context_base(surface)||shapesy_pass.generation!=shapesy_resources.generation||
  shapesy_row_lease.generation!=shapesy_pass.generation||memcmp(shapesy_pass.palette,rgb_palette,sizeof(shapesy_pass.palette))){
  render_mirror_unsupported("shapesy-pixel-context");render_mirror_shapesy_end();return false;
 }
 intptr_t offset=(intptr_t)address-(intptr_t)surface->pixels;
 if(offset<0||offset>=surface->pitch*surface->h)return false;
 int x=(int)(offset%surface->pitch)-shapesy_row_lease.x,y=(int)(offset/surface->pitch)-shapesy_row_lease.y;
 if(x<0||x>=288||y<0||y>=28)return false;
 unsigned t=(unsigned)x/24;const Uint8 *s=shapesy_row_lease.sources[t];
 int k=shapesy_member(shapesy_id(s));
 if(!(shapesy_row_lease.replaced&(1u<<t))||k<0||!s||s[y*24+x%24]!=source||memcmp(s,shapesy_registry.source[k],672)){
  render_mirror_unsupported("shapesy-pixel-identity");render_mirror_shapesy_end();return false;}
 if(qualified)*qualified=true;
 return source>=48&&source<=63;
}

/* Keep a lightweight contributed-frame witness after the Layer1 pass ends.
 * VGAScreen legitimately switches to VGAScreenSeg before finish; do not reuse
 * the draw-site surface equality there. No extra per-pixel ownership map. */
static bool shapesy_frame_check(void)
{
 if(!shapesy_frame.live)return true;
 if(!shapesy_geometry_matches(&shapesy_frame.geometry)||!shapesy_world_check()||shapesy_pass.live||shapesy_row_lease.live||shapesy_frame.surface!=game_screen||
  asteroid_hd_enabled||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !(game_probe_scene_assets&2)||!game_probe_assets||!shapesy_resources.valid||
  strcmp(game_probe_assets,shapesy_resources.root)||shapesy_frame.generation!=shapesy_resources.generation||
  filterFade||levelFilter!=-99||levelBrightness!=-99||
  memcmp(shapesy_frame.palette,rgb_palette,sizeof(shapesy_frame.palette))||!shapesy_sources_valid())return false;
 for(unsigned i=0;i<9;i++)if(smoothies[i])return false;
 return true;
}

static bool shapesy_borrow_layout(uint64_t serial)
{
 return serial&&shapesy_borrow.sealed&&!shapesy_borrow.building&&!shapesy_borrow.failed&&
  serial==shapesy_borrow.serial&&shapesy_borrow.values&&shapesy_borrow.capacity==320u*200u*8u*8u&&
  shapesy_borrow.tick==mirror_logic_tick&&shapesy_borrow.generation==shapesy_resources.generation&&
  shapesy_frame.live&&shapesy_frame.generation==shapesy_borrow.generation&&
  canvas&&canvas==shapesy_borrow.canvas_surface&&canvas->pixels==shapesy_borrow.pixels&&
  canvas->format==shapesy_borrow.format&&canvas->w==shapesy_borrow.w&&canvas->h==shapesy_borrow.h&&
  canvas->pitch==shapesy_borrow.pitch&&canvas->format&&canvas->format->format==SDL_PIXELFORMAT_ARGB8888&&
  game_screen&&game_screen==shapesy_borrow.index_surface&&game_screen->pixels==shapesy_borrow.index_pixels&&
  game_screen->format==shapesy_borrow.index_format&&game_screen->pitch==shapesy_borrow.index_pitch&&
  game_probe_density==8&&!reject_reason;
}
static uint64_t shapesy_borrow_ready(void)
{
 uint64_t serial=shapesy_borrow.serial;
 return shapesy_borrow_layout(serial)&&shapesy_frame_check()&&shapesy_geometry_matches(&shapesy_borrow.geometry)?serial:0;
}
static bool shapesy_borrow_sample(uint64_t serial,size_t n,Uint32 color)
{
 return shapesy_borrow_layout(serial)&&n<shapesy_borrow.capacity&&
  (color>>24)==255&&shapesy_borrow.values[n]==color;
}
static bool shapesy_borrow_check(uint64_t serial)
{
 /* Final/cached checks rehash mutable asset payloads, not merely frame flags.
  * No resource scans happen inside the per-pixel borrowed-value test. */
 return shapesy_borrow_layout(serial)&&shapesy_frame_check()&&
  shapesy_geometry_matches(&shapesy_borrow.geometry)&&shapesy_cache_valid();
}
static bool shapesy_present_geometry(SDL_Renderer *renderer, const SDL_Rect *dst)
{
 if (!shapesy_frame.live) return true;
 const VideoOutputGeometry *g = &shapesy_frame.geometry;
 return renderer == g->renderer && dst && dst->x == g->dst.x && dst->y == g->dst.y && dst->w == g->dst.w && dst->h == g->dst.h;
}

/* Ordered source-semantic contour reconstruction after all Layer1 rows.
 * Only the declared contour/bevel/coverage band may change, including water
 * inside that band. INDEX8, expected indices and all outside-band pixels remain
 * untouched. This reuses the existing canvas and ownership buffers. */
static int shapesy_edge_cell(int x,int y)
{
 int xx=x-shapesy_pass.x,yy=y-shapesy_pass.y;
 if(x<0||x>=320||y<0||y>=200||xx<0||xx>=288||yy<0||yy>=224)return -1;
 size_t cell=shapesy_pass.first+(unsigned)(yy/28)*14+(unsigned)(xx/24);
 const Uint8 *s=megaData1.mainmap[cell/14][cell%14];
 if(!s||s!=shapesy_pass.sources[yy/28][xx/24]||!(shapesy_pass.replaced[yy/28]&(1u<<(xx/24)))||shapesy_member(shapesy_id(s))<0)return -1;
 return s[(yy%28)*24+xx%24];
}
static bool shapesy_edge_water(int x,int y)
{int v=shapesy_edge_cell(x,y);return v>=48&&v<=63;}
static bool shapesy_edge_tap(int x,int y)
{
 int v=shapesy_edge_cell(x,y);
 if(v<48||v>63||((Uint8 *)game_screen->pixels)[y*game_screen->pitch+x]!=v||expected[y*320+x]!=v)return false;
 Uint32 color=palette_rgb(v);
 for(int py=0;py<8;py++)for(int px=0;px<8;px++){
  int at=(y*8+py)*canvas->w+x*8+px;
  Uint32 c=*((Uint32 *)((Uint8 *)canvas->pixels+(y*8+py)*canvas->pitch)+x*8+px);
  if(hd_owner[at]||cloud_owner[at]||c!=color)return false;
 }
 return true;
}
static bool shapesy_edge_center(int x,int y)
{
 int value = shapesy_edge_cell(x, y);
 if (value < 0 || ((Uint8 *)game_screen->pixels)[y * game_screen->pitch + x] != value || expected[y * 320 + x] != value) return false;
 int xx=x-shapesy_pass.x,yy=y-shapesy_pass.y;
 int k=shapesy_member(shapesy_id(shapesy_pass.sources[yy/28][xx/24]));
 if(k<0)return false;
 const Asset *a=&shapesy_resources.members[k];
 for(int py=0;py<8;py++)for(int px=0;px<8;px++){
  int at=(y*8+py)*canvas->w+x*8+px;
  const Uint8 *p=a->rgba+(((yy%28)*8+py)*192+(xx%24)*8+px)*4;
  Uint32 c=*((Uint32 *)((Uint8 *)canvas->pixels+(y*8+py)*canvas->pitch)+x*8+px);
  if(hd_owner[at]!=1||cloud_owner[at]||c!=(0xff000000u|p[0]<<16|p[1]<<8|p[2]))return false;
 }
 return true;
}
#include "current_shapesy_contour_materials.h"
typedef struct { short x0, y0, x1, y1; Uint8 type; } ShapesYContourLine;
static struct {
 bool checked, valid;
 uint64_t map_stamp;
 signed char members[300][14];
 unsigned count;
 ShapesYContourLine lines[512];
} shapesy_world;
static void shapesy_world_reset(void)
{ memset(&shapesy_world, 0, sizeof(shapesy_world)); }
static uint64_t shapesy_world_stamp(void)
{
 uint64_t h = UINT64_C(0xcbf29ce484222325);
 for (unsigned y = 0; y < 300; y++) for (unsigned x = 0; x < 14; x++) {
  uintptr_t p = (uintptr_t)megaData1.mainmap[y][x];
  for (unsigned b = 0; b < sizeof(p); b++) { h ^= (p >> (b * 8)) & 255; h *= UINT64_C(0x100000001b3); }
 }
 return h;
}
static bool shapesy_world_check(void)
{ return shapesy_world.valid && shapesy_world.map_stamp == shapesy_world_stamp(); }
static int shapesy_world_plane(int x, int y)
{
 if (x < 0 || x >= 336 || y < 0 || y >= 8400) return -1;
 int k = shapesy_world.members[y / 28][x / 24];
 return k < 0 ? -1 : shapesy_contour_semantic[k * 672 + (y % 28) * 24 + x % 24];
}
static bool shapesy_world_deck(int x, int y)
{ int p = shapesy_world_plane(x, y); return p == 1 || p == 6 || p == 8; }
static int shapesy_world_boundary(int x, int y)
{
 if (!shapesy_world_deck(x - 1, y) || shapesy_world_deck(x, y)) return 0;
 for (int d = 0; d < 3; d++) {
  int p = shapesy_world_plane(x + d, y);
  if (p == 4 || p == 5) return 2;
  if (p == 0) return 1;
  if (p != 7) break;
 }
 return 0;
}
typedef struct { bool live, overflow; int y0, y1, last, type; short x[256]; } ShapesYRun;
static bool shapesy_world_finish_run(const ShapesYRun *r)
{
 if (!r->live || r->overflow) return true;
 int dy = r->y1 - r->y0, dx = r->last - r->x[0];
 if (dy < 9 || (r->type == 1 ? dx <= 0 : dx >= 0) || abs(dx) * 10 < dy * 6 || abs(dx) * 10 > dy * 11) return true;
 for (int y = 0; y <= dy; y++) if (abs((r->x[y] - r->x[0]) * dy - dx * y) > 3 * dy) return true;
 if (shapesy_world.count == 512) return false;
 shapesy_world.lines[shapesy_world.count++] = (ShapesYContourLine){r->x[0], r->y0, r->last, r->y1, r->type};
 return true;
}
static bool shapesy_world_prepare(void)
{
 if (shapesy_world.checked) return shapesy_world_check();
 shapesy_world.checked = true;
 shapesy_world.map_stamp = shapesy_world_stamp();
 for (unsigned y = 0; y < 300; y++) for (unsigned x = 0; x < 14; x++)
  shapesy_world.members[y][x] = (signed char)shapesy_member(shapesy_id(megaData1.mainmap[y][x]));
 ShapesYRun runs[64] = {{0}};
 for (int y = 0; y < 8400; y++) {
  for (int x = 1; x < 336; x++) {
   int type = shapesy_world_boundary(x, y);
   if (!type) continue;
   int chosen = -1, best = 5;
   for (unsigned i = 0; i < 64; i++) if (runs[i].live && runs[i].type == type && runs[i].y1 == y - 1) {
    int d = abs(runs[i].last - x); if (d < best) { best = d; chosen = (int)i; }
   }
   if (chosen < 0) {
    for (unsigned i = 0; i < 64; i++) if (!runs[i].live) { chosen = (int)i; break; }
    if (chosen < 0) return false;
    memset(&runs[chosen], 0, sizeof(runs[chosen]));
    runs[chosen].live = true; runs[chosen].y0 = y; runs[chosen].type = type;
   }
   ShapesYRun *r = &runs[chosen]; r->last = x; r->y1 = y;
   if (y - r->y0 < 256) r->x[y - r->y0] = (short)x; else r->overflow = true;
  }
  for (unsigned i = 0; i < 64; i++) if (runs[i].live && runs[i].y1 < y) {
   if (!shapesy_world_finish_run(&runs[i])) return false; runs[i].live = false;
  }
 }
 for (unsigned i = 0; i < 64; i++) if (!shapesy_world_finish_run(&runs[i])) return false;
 shapesy_world.valid = shapesy_world.map_stamp == shapesy_world_stamp();
 return shapesy_world.valid;
}

static int shapesy_plane(int x,int y)
{
 int xx=x-shapesy_pass.x,yy=y-shapesy_pass.y;
 if(shapesy_edge_cell(x,y)<0)return -1;
 int k=shapesy_member(shapesy_id(shapesy_pass.sources[yy/28][xx/24]));
 return shapesy_contour_semantic[k*672+(yy%28)*24+xx%24];
}
/* Analytic coverage of the witnessed 2x or 4x destination footprint.
 * Integer positive-part integral; no global texture filtering. */
static int shapesy_line_coverage(int a,int b,int c,int x,int y)
{
 int footprint=shapesy_pass.geometry.footprint;
 x=(x/footprint)*footprint;y=(y/footprint)*footprint;int bb=b<0?-b:b;
 int t=b<0?c-a*x-b*(y+footprint):c-a*x-b*y;
 int aw=footprint*a,bh=footprint*bb;if(t<=0)return 0;if(t>=aw+bh)return 255;
 long long q=t,n=q*q; q=t-aw;if(q>0)n-=q*q;q=t-bh;if(q>0)n-=q*q;q=t-aw-bh;if(q>0)n+=q*q;
 long long den=2LL*a*bb*footprint*footprint;return (int)((n*255+den/2)/den);
}
static const char *shapesy_edge_aa(void)
{
 if (!shapesy_world_check()) return "shapesy-contour-map-witness";
 for(unsigned row=0;row<8;row++)for(unsigned t=0;t<12;t++){
  size_t at=shapesy_pass.first+row*14+t;
  if(megaData1.mainmap[at/14][at%14]!=shapesy_pass.sources[row][t])return "shapesy-edge-map-witness";
 }
 int xoff = shapesy_pass.x - (int)(shapesy_pass.first % 14) * 24;
 int yoff = shapesy_pass.y - (int)(shapesy_pass.first / 14) * 28;
 for(unsigned i=0;i<shapesy_world.count;i++){
  const ShapesYContourLine *r=&shapesy_world.lines[i];
  int dy=r->y1-r->y0,dx=r->x1-r->x0;
  int a=dy,b=-dx,c=8*dy*(r->x0+xoff)-dx*(8*(r->y0+yoff)+4);
  int top=r->y0+yoff,bottom=r->y1+yoff;
  if(top<0)top=0;if(bottom>199)bottom=199;
  if(bottom>=shapesy_pass.y+224)bottom=shapesy_pass.y+223;
  for(int y=top;y<=bottom;y++){
   int wy=y-yoff;
   int predicted=(dy*r->x0+dx*(wy-r->y0)+dy/2)/dy,old_world=-1;
   for(int wx=predicted-4;wx<=predicted+4;wx++)if(shapesy_world_boundary(wx,wy)==r->type){old_world=wx;break;}
   if(old_world<0)return "shapesy-contour-world-edge";
   int old=old_world+xoff;
   if(old<1||old>314||old<shapesy_pass.x||old>=shapesy_pass.x+288)continue;
   int water_x=-1;
   if(r->type==1){for(int xx=old;xx<old+7&&xx<320;xx++)if(shapesy_edge_water(xx,y)){water_x=xx;break;}
    if(water_x<0)continue;
    if(!shapesy_edge_tap(water_x,y))return "shapesy-contour-water-witness";}
   for(int x=old-4;x<=old+4;x++){
    int source=shapesy_edge_cell(x,y),plane=shapesy_plane(x,y);
    if(source<0||!source||plane==6||plane==8)continue;
    bool native_water=source>=48&&source<=63;
    if(r->type==2&&plane!=1&&plane!=4&&plane!=5)continue;
    int xx=x-shapesy_pass.x,yy=y-shapesy_pass.y;
    int k=shapesy_member(shapesy_id(shapesy_pass.sources[yy/28][xx/24]));
    if(native_water){if(!shapesy_edge_tap(x,y))return "shapesy-contour-native-center";}
    else if(!shapesy_edge_center(x,y))return "shapesy-contour-art-center";
    for(int py=0;py<8;py++)for(int px=0;px<8;px++){
     int gx=x*8+px,gy=y*8+py;
     int deck=shapesy_line_coverage(a,b,c,gx,gy),outer=shapesy_line_coverage(a,b,c+8*a,gx,gy);
     /* Leave exact original pixels outside the old/new contour transition. */
     if(r->type==1&&plane==1&&deck==255)continue;
     if(r->type==1&&native_water&&!outer)continue;
     if(r->type==2&&((plane==1&&deck==255)||(plane==4&&!outer)))continue;
     int lx=(xx%24)*8+px,ly=(yy%28)*8+py,v=ly+lx+shapesy_contour_wall_offset[k]*8;
     if(v<0)v=0;if(v>455)v=455;
     const Uint8 *d=shapesy_contour_deck+(ly*192+lx)*3;
     const Uint8 *middle=r->type==1?shapesy_contour_shadow+(ly*192+lx)*3:shapesy_contour_bevel+((ly%16)*192+lx)*3;
     const Uint8 *wall=shapesy_contour_right+(v*192+lx)*3;
     Uint32 water=0;if(r->type==1)water=palette_rgb(native_water?source:shapesy_edge_cell(water_x,y));
     Uint32 color=0xff000000u;for(int ch=0;ch<3;ch++){
      unsigned bg=r->type==1?((water>>(16-8*ch))&255):wall[ch];
      unsigned value=(d[ch]*deck+middle[ch]*(outer-deck)+bg*(255-outer)+127)/255;color|=value<<(16-8*ch);
     }
     Uint32 *dst=(Uint32 *)((Uint8 *)canvas->pixels+gy*canvas->pitch)+gx;*dst=color;
     shapesy_borrow_mark((size_t)gy*canvas->w+gx,color);
     if(!native_water||outer){hd_owner[gy*canvas->w+gx]=1;selected[y*320+x]=1;}
    }
   }
  }
 }
 return NULL;
}
