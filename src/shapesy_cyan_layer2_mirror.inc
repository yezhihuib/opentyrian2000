/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite ShapesY layer2 cyan motif. Separate pass, resources and typed values.
 * Native index0 is transparent; no layer1 black-zero policy is reused. */
#include "current_shapesy_cyan_source.h"
#include "current_shapesy_cyan_hd_assets.h"
#include "current_shapesy_cyan_secondary_source.h"
#include "current_shapesy_cyan_secondary_hd_assets.h"
/* Slot identity is structural; source bytes/readiness are optional per family. */
static struct { bool valid; unsigned ids[71],bound_ids[71]; bool source_valid[2],seen[9]; Uint8 source[9][672]; } cyan_registry;
typedef struct { bool checked,valid; char root[1024]; Asset members[5]; uint64_t generation; } CyanResources;
static CyanResources cyan_resources,cyan_secondary_resources;
static CyanResources *cyan_group(unsigned g){return g?&cyan_secondary_resources:&cyan_resources;}
static unsigned cyan_group_of(unsigned k){return k<4?0:1;}
static unsigned cyan_group_first(unsigned g){return g?4:0;}
static unsigned cyan_group_count(unsigned g){return g?5:4;}
static unsigned cyan_id_at(unsigned k){return k<4?cyan_ids[k]:cyan_secondary_ids[k-4];}
static uint64_t cyan_source_pin(unsigned k){return k<4?cyan_source_pins[k]:cyan_secondary_source_pins[k-4];}
static uint64_t cyan_rgba_pin(unsigned k){return k<4?cyan_rgba_pins[k]:cyan_secondary_rgba_pins[k-4];}
static Asset *cyan_asset(unsigned k){return &cyan_group(cyan_group_of(k))->members[k<4?k:k-4];}
static bool cyan_generations(unsigned mask,uint64_t first,uint64_t second)
{return (!(mask&1)||first==cyan_resources.generation)&&(!(mask&2)||second==cyan_secondary_resources.generation);}
static struct { bool live,drew; SDL_Surface *surface; size_t first; unsigned row; int x,y; uint64_t generation,secondary_generation; unsigned ready,used; Uint32 palette[256]; const Uint8 *sources[8][12]; unsigned replaced[8]; VideoOutputGeometry geometry; } cyan_pass;
static struct { bool live; SDL_Surface *surface; uint64_t generation,secondary_generation,borrow_serial; unsigned used; Uint32 palette[256]; VideoOutputGeometry geometry; } cyan_frame;
static bool cyan_attempted;
static uint64_t cyan_layer1_dependency;
static unsigned cyan_native_samples,cyan_platform_samples,cyan_unknown_samples;
static bool cyan_trace(void){return getenv("TYRIAN_CYAN_BORROW_TRACE")!=NULL;}
static bool cyan_borrow_layout(uint64_t serial);
static struct { bool live; unsigned left; Uint8 seen[12][672]; unsigned replaced; int x,y; uint64_t generation,secondary_generation; unsigned used; const Uint8 *sources[12]; } cyan_row_lease;
/* Typed opaque values written only by this guarded ShapesY layer2 path.
 * Zero means untyped. Exact sampled-value equality prevents a later foreign
 * writer from lending changed RGB; a same-valued write is equivalent to this
 * still-proven terrain value. The sealed witness survives cached Present only
 * until a frame/map/root/reset, and never grants another owner by itself. */
static struct {
 Uint32 *values;size_t capacity;bool building,sealed,failed;
 uint64_t serial,generation,secondary_generation,tick; unsigned used;
 SDL_Surface *canvas_surface,*index_surface;void *pixels,*index_pixels;
 SDL_PixelFormat *format,*index_format;int w,h,pitch,index_pitch;
 VideoOutputGeometry geometry;
} cyan_borrow;
static uint64_t cyan_borrow_serial;
static void cyan_borrow_retire(void)
{cyan_borrow.building=cyan_borrow.sealed=false;}
static void cyan_borrow_begin(void)
{
 cyan_borrow_retire();cyan_borrow.failed=false;
 if(!canvas||!canvas->pixels||!canvas->format||canvas->w!=2560||canvas->h!=1600||
    canvas->pitch!=2560*4||(uintptr_t)canvas->pixels%sizeof(Uint32)||canvas->format->format!=SDL_PIXELFORMAT_ARGB8888||canvas->format->BitsPerPixel!=32||canvas->format->BytesPerPixel!=4)return;
 const size_t count=320u*200u*8u*8u;
 if(cyan_borrow.capacity!=count){
  Uint32 *values=calloc(count,sizeof(Uint32));if(!values)return;
  free(cyan_borrow.values);cyan_borrow.values=values;cyan_borrow.capacity=count;
 }
 memset(cyan_borrow.values,0,count*sizeof(Uint32));
 if(++cyan_borrow_serial==0)++cyan_borrow_serial;
 cyan_borrow.serial=cyan_borrow_serial;cyan_borrow.building=true;
}
static void cyan_borrow_mark(size_t n,Uint32 color)
{
 if(!cyan_borrow.building)return;
 if(n>=cyan_borrow.capacity||(color>>24)!=255){cyan_borrow.failed=true;return;}
 cyan_borrow.values[n]=color;
}
static void cyan_borrow_seal(void)
{
 if(!cyan_borrow.building||cyan_borrow.failed||!cyan_frame.live){cyan_borrow_retire();return;}
 cyan_borrow.building=false;cyan_borrow.sealed=true;
 cyan_borrow.generation=cyan_frame.generation;cyan_borrow.secondary_generation=cyan_frame.secondary_generation;cyan_borrow.used=cyan_frame.used;cyan_borrow.tick=mirror_logic_tick;
 cyan_borrow.canvas_surface=canvas;cyan_borrow.pixels=canvas->pixels;cyan_borrow.format=canvas->format;
 cyan_borrow.w=canvas->w;cyan_borrow.h=canvas->h;cyan_borrow.pitch=canvas->pitch;
 cyan_borrow.index_surface=game_screen;cyan_borrow.index_pixels=game_screen->pixels;
 cyan_borrow.index_format=game_screen->format;cyan_borrow.index_pitch=game_screen->pitch;
 cyan_borrow.geometry=cyan_frame.geometry;cyan_frame.borrow_serial=cyan_borrow.serial;
}
static int cyan_member(unsigned id)
{for(unsigned k=0;k<9;k++)if(id==cyan_id_at(k))return (int)k;return -1;}
static int cyan_source_slot(const Uint8 *data)
{
 uintptr_t base=(uintptr_t)&megaData2.shapes[0].sh,p=(uintptr_t)data;
 size_t stride=sizeof(megaData2.shapes[0]);
 if(!data||p<base||p-base>=sizeof(megaData2.shapes)||(p-base)%stride)return -1;
 unsigned slot=(unsigned)((p-base)/stride);
 return data==megaData2.shapes[slot].sh?(int)slot:-1;
}
void render_mirror_cyan_row_end(void)
{
 bool missing=cyan_row_lease.live&&cyan_row_lease.left;
 memset(&cyan_row_lease,0,sizeof(cyan_row_lease));
 if(missing){cyan_borrow.failed=true;render_mirror_unsupported("cyan-incomplete-native-row");}
}
static bool cyan_pass_active(void){return cyan_pass.live;}
static bool cyan_context(SDL_Surface *surface),cyan_cache_valid(void);
static bool cyan_group_sources_valid(unsigned g);
static bool cyan_geometry(VideoOutputGeometry *out)
{ return video_output_geometry(out) && (out->scale == 2 || out->scale == 4); }
static bool cyan_geometry_matches(const VideoOutputGeometry *expected_geometry)
{
 VideoOutputGeometry current;
 return cyan_geometry(&current) && video_output_geometry_equal(&current, expected_geometry);
}
static bool cyan_snapshot_valid(void)
{
 for(unsigned r=0;r<8;r++)for(unsigned t=0;t<12;t++){
  size_t at=cyan_pass.first+r*14+t;
  if(megaData2.mainmap[at/14][at%14]!=cyan_pass.sources[r][t])return false;
 }
 return true;
}
void render_mirror_cyan_end(void)
{
 render_mirror_cyan_row_end();
 bool had=cyan_pass.live, drew=cyan_pass.drew;
 bool ok=had&&cyan_pass.row==8&&!reject_reason&&cyan_context(cyan_pass.surface)&&
  cyan_generations(cyan_pass.used,cyan_pass.generation,cyan_pass.secondary_generation)&&cyan_cache_valid()&&cyan_snapshot_valid()&&
  (!cyan_layer1_dependency||shapesy_borrow_check(cyan_layer1_dependency));
 if(ok&&drew)cyan_borrow_seal();else if(had)cyan_borrow_retire();
 if(had&&cyan_trace())fprintf(stderr,"cyan-seal tick=%u logic_tick=%llu ok=%d drew=%d serial=%llu layer1=%llu rows=%u native=%u platform=%u unknown=%u\n",game_probe_tick,(unsigned long long)mirror_logic_tick,ok,drew,(unsigned long long)(cyan_borrow.sealed?cyan_borrow.serial:0),(unsigned long long)cyan_layer1_dependency,cyan_pass.row,cyan_native_samples,cyan_platform_samples,cyan_unknown_samples);
 cyan_pass.live=false;
 if(had&&drew&&!ok)render_mirror_unsupported("cyan-pass-final-integrity");
}
static void cyan_frame_reset(void)
{render_mirror_cyan_end();cyan_borrow_retire();memset(&cyan_frame,0,sizeof(cyan_frame));memset(&cyan_pass,0,sizeof(cyan_pass));cyan_attempted=false;cyan_layer1_dependency=0;cyan_native_samples=cyan_platform_samples=cyan_unknown_samples=0;}
static void cyan_map_reset(void)
{
 cyan_frame_reset();
 for(unsigned g=0;g<2;g++){CyanResources *r=cyan_group(g);for(unsigned k=0;k<cyan_group_count(g);k++)free(r->members[k].rgba);memset(r,0,sizeof(*r));}
 memset(&cyan_registry,0,sizeof(cyan_registry));cyan_registry.valid=true;cyan_registry.source_valid[0]=cyan_registry.source_valid[1]=true;
}
static void cyan_shutdown(void)
{cyan_map_reset();free(cyan_borrow.values);memset(&cyan_borrow,0,sizeof(cyan_borrow));}
static void cyan_bind(unsigned layer,unsigned id,const Uint8 *data)
{
 if((terrain_file!='Y'&&terrain_file!='y')||layer!=2)return;
 int slot=cyan_source_slot(data),k=cyan_member(id);
 if(slot<0||!id||id>600||cyan_registry.ids[slot]){cyan_registry.valid=false;return;}
 cyan_registry.ids[slot]=cyan_registry.bound_ids[slot]=id;
 if(k<0)return;
 unsigned g=cyan_group_of((unsigned)k);
 if(asteroid1_stamp(data,672)!=cyan_source_pin((unsigned)k))cyan_registry.source_valid[g]=false;
 if(cyan_registry.seen[k]&&memcmp(data,cyan_registry.source[k],672))cyan_registry.source_valid[g]=false;
 if(!cyan_registry.seen[k])memcpy(cyan_registry.source[k],data,672);
 cyan_registry.seen[k]=true;
}
static unsigned cyan_id(const Uint8 *data)
{int slot=cyan_source_slot(data);return slot<0?0:cyan_registry.ids[slot];}
static bool cyan_structure_valid(void)
{return cyan_registry.valid&&!memcmp(cyan_registry.ids,cyan_registry.bound_ids,sizeof(cyan_registry.ids));}
static bool cyan_group_sources_valid(unsigned g)
{
 if(!cyan_structure_valid()||!cyan_registry.source_valid[g]||(terrain_file!='Y'&&terrain_file!='y'))return false;
 unsigned first=cyan_group_first(g),count=cyan_group_count(g);
 for(unsigned k=first;k<first+count;k++)if(!cyan_registry.seen[k]||asteroid1_stamp(cyan_registry.source[k],672)!=cyan_source_pin(k))return false;
 /* Every actual alias of this family, including offscreen slots, is checked. */
 for(unsigned slot=0;slot<71;slot++) {
  int k=cyan_member(cyan_registry.ids[slot]);
  if(k>=0&&cyan_group_of((unsigned)k)==g&&memcmp(megaData2.shapes[slot].sh,cyan_registry.source[k],672))return false;
 }
 return true;
}
static bool cyan_sources_mask_valid(unsigned mask)
{for(unsigned g=0;g<2;g++)if((mask&(1u<<g))&&!cyan_group_sources_valid(g))return false;return cyan_structure_valid();}
/* Retained first-family diagnostic entry point; production uses explicit masks. */
static bool cyan_sources_valid(void){return cyan_sources_mask_valid(1);}
static bool cyan_palette(void)
{
 uint64_t h=UINT64_C(0xcbf29ce484222325);
 for(unsigned i=0;i<256;i++)for(int s=16;s>=0;s-=8){h^=(rgb_palette[i]>>s)&255;h*=UINT64_C(0x100000001b3);}
 return h==CYAN_PALETTE_FNV;
}
static bool cyan_context_base(SDL_Surface *surface)
{
 if((terrain_file!='Y'&&terrain_file!='y')||!cyan_registry.valid||asteroid_hd_enabled||!active||reject_reason||!(game_probe_scene_assets&2)||game_probe_density!=8||
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
static bool cyan_context(SDL_Surface *surface)
{return cyan_context_base(surface)&&cyan_palette()&&cyan_sources_mask_valid(cyan_pass.used)&&
 (!cyan_pass.live||cyan_geometry_matches(&cyan_pass.geometry));}
static bool cyan_rgba_valid(unsigned k,const Uint8 *rgba)
{
 if(!rgba||asteroid1_stamp(rgba,24*28*8*8*4)!=cyan_rgba_pin(k))return false;
 if(!cyan_registry.seen[k])return false;
 for(unsigned y=0;y<224;y++)for(unsigned x=0;x<192;x++) {
  unsigned v=cyan_registry.source[k][(y/8)*24+x/8];const Uint8 *p=rgba+(y*192+x)*4;
  if(!v&&(p[0]||p[1]||p[2]||p[3]))return false;
  if(!p[3]&&(p[0]||p[1]||p[2]))return false;
 }
 return true;
}
static bool cyan_load(unsigned k,Asset *result)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/terrain-shapesy-cyan-%u-8.hda",cyan_group(cyan_group_of(k))->root,cyan_id_at(k));
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)24*28*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_SHAPESY_CYAN*10000+cyan_id_at(k)&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&cyan_rgba_valid(k,rgba);
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *result=(Asset){true,true,ASSET_SHAPESY_CYAN,(int)cyan_id_at(k),24,28,0,0,8,rgba};return true;
}
static bool cyan_group_cache_valid(unsigned g)
{
 CyanResources *r=cyan_group(g);
 if(!r->valid||!game_probe_assets||strcmp(r->root,game_probe_assets))return false;
 for(unsigned j=0;j<cyan_group_count(g);j++) {
  unsigned k=cyan_group_first(g)+j;Asset *a=&r->members[j];
  if(!a->initialized||!a->valid||a->bank!=ASSET_SHAPESY_CYAN||a->index!=(int)cyan_id_at(k)||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!cyan_rgba_valid(k,a->rgba)){
   r->valid=false;return false;}
 }
 return true;
}
static bool cyan_group_ready(unsigned g)
{
 CyanResources *r=cyan_group(g);
 if(!game_probe_assets||strlen(game_probe_assets)>=sizeof(r->root)||!cyan_group_sources_valid(g))return false;
 if(!r->checked){
  r->checked=true;strcpy(r->root,game_probe_assets);
  Asset loaded[5]={{0}};bool ok=true;
  for(unsigned j=0;j<cyan_group_count(g);j++)if(!cyan_load(cyan_group_first(g)+j,&loaded[j])){ok=false;break;}
  if(ok)memcpy(r->members,loaded,sizeof(loaded));else for(unsigned j=0;j<5;j++)free(loaded[j].rgba);
  r->valid=ok;
 }
 if(!cyan_group_cache_valid(g))return false;
 if(++r->generation==0)++r->generation;
 return true;
}
/* Readiness and contribution differ: only families that wrote visible native
 * nonzero support remain dependencies, even after transfer or total occlusion. */
static bool cyan_cache_valid(void)
{
 unsigned mask=cyan_frame.live?cyan_frame.used:cyan_pass.used;
 for(unsigned g=0;g<2;g++)if((mask&(1u<<g))&&!cyan_group_cache_valid(g))return false;
 return true;
}

void render_mirror_cyan_layer2(SDL_Surface *surface,const void *first,int x,int y)
{
 if(cyan_attempted){bool contributed=cyan_pass.drew||cyan_frame.live;render_mirror_cyan_end();if(contributed)render_mirror_unsupported("cyan-repeat-pass");return;}
 cyan_attempted=true;
 if(cyan_trace())fprintf(stderr,"cyan-entry tick=%u logic_tick=%llu normal=1 filter=%d brightness=%d fade=%d x=%d y=%d\n",game_probe_tick,(unsigned long long)mirror_logic_tick,levelFilter,levelBrightness,filterFade,x,y);
 if(!cyan_context(surface)||!background2||x<0||x>32||y<-28||y>-1||x!=mapX2Pos||y!=(int)backPos2-28)return;
 uintptr_t base=(uintptr_t)&megaData2.mainmap[0][0],p=(uintptr_t)first;
 if(p<base||p-base>=sizeof(megaData2.mainmap)||(p-base)%sizeof(JE_byte *))return;
 size_t cell=(p-base)/sizeof(JE_byte *);
 if(cell%14>2||cell/14>592||mapX2bpPos<0||mapX2bpPos>15||p!=(uintptr_t)mapY2Pos+(mapX2bpPos-12)*(intptr_t)sizeof(JE_byte *))return;
 for(unsigned row=0;row<8;row++)for(unsigned tile=0;tile<12;tile++){
  size_t at=cell+row*14+tile;const Uint8 *v=megaData2.mainmap[at/14][at%14];
  if(v&&!cyan_id(v))return;
  cyan_pass.sources[row][tile]=v;
 }
 VideoOutputGeometry geometry;unsigned candidates=0;
 if(!cyan_geometry(&geometry))return;
 for(unsigned row=0;row<8;row++)for(unsigned tile=0;tile<12;tile++){
  int k=cyan_member(cyan_id(cyan_pass.sources[row][tile]));if(k>=0)candidates|=1u<<cyan_group_of((unsigned)k);
 }
 for(unsigned g=0;g<2;g++)if((candidates&(1u<<g))&&cyan_group_ready(g))cyan_pass.ready|=1u<<g;
 if(!cyan_pass.ready)return;
 cyan_borrow_begin();if(!cyan_borrow.building)return;
 cyan_pass.geometry=geometry;cyan_pass.live=true;cyan_pass.surface=surface;cyan_pass.first=cell;cyan_pass.x=x;cyan_pass.y=y;
 cyan_pass.generation=cyan_resources.generation;cyan_pass.secondary_generation=cyan_secondary_resources.generation;memcpy(cyan_pass.palette,rgb_palette,sizeof(cyan_pass.palette));
}
/* Entire tile is preflighted before any writes. Only qualified layer1 values
 * may supply foreign HD under partial/zero alpha. Index0 never participates. */
static bool cyan_tile_preflight(unsigned k,int x,int y,uint64_t serial,bool *borrowed)
{
 const Uint8 *rgba=cyan_asset(k)->rgba,*source=cyan_registry.source[k];
 *borrowed=false;
 for(int cy=0;cy<28;cy++)for(int cx=0;cx<24;cx++){
  if(!source[cy*24+cx])continue;
  int dx=x+cx,dy=y+cy;if(dx<0||dx>=320||dy<0||dy>=200)continue;
  Uint8 native=((Uint8 *)game_screen->pixels)[dy*320+dx];if(native!=expected[dy*320+dx])return false;
  for(int py=0;py<8;py++)for(int px=0;px<8;px++){
   size_t n=(size_t)(dy*8+py)*canvas->w+dx*8+px;
   const Uint8 *a=rgba+4*((cy*8+py)*192+cx*8+px);
   Uint32 color=*((Uint32 *)((Uint8 *)canvas->pixels+(dy*8+py)*canvas->pitch)+dx*8+px);
   if(a[3]<255){
    if(hd_owner[n]||cloud_owner[n]){
     if(!shapesy_borrow_sample(serial,n,color)){cyan_unknown_samples++;return false;}*borrowed=true;cyan_platform_samples++;
    }else {if(color!=palette_rgb(native)){cyan_unknown_samples++;return false;}cyan_native_samples++;}
   }
  }
 }
 return true;
}
static bool cyan_tile_draw(unsigned k,int x,int y)
{
 bool visible=false;
 for(int cy=0;cy<28&&!visible;cy++)for(int cx=0;cx<24;cx++)if(cyan_registry.source[k][cy*24+cx]&&x+cx>=0&&x+cx<320&&y+cy>=0&&y+cy<200){visible=true;break;}
 if(!visible)return false;
 uint64_t serial=shapesy_borrow_ready();bool borrowed=false;
 if(!cyan_tile_preflight(k,x,y,serial,&borrowed))return false;
 if(borrowed&&cyan_layer1_dependency&&cyan_layer1_dependency!=serial)return false;
 if(borrowed)cyan_layer1_dependency=serial;
 const Uint8 *rgba=cyan_asset(k)->rgba,*source=cyan_registry.source[k];
 render_mirror_shadow_end();font_before_effect((SDL_Rect){x,y,24,28});
 for(int cy=0;cy<28;cy++)for(int cx=0;cx<24;cx++){
  if(!source[cy*24+cx])continue;
  int dx=x+cx,dy=y+cy;if(dx<0||dx>=320||dy<0||dy>=200)continue;
  for(int py=0;py<8;py++)for(int px=0;px<8;px++){
   size_t n=(size_t)(dy*8+py)*canvas->w+dx*8+px;
   const Uint8 *a=rgba+4*((cy*8+py)*192+cx*8+px);
   Uint32 *dst=(Uint32 *)((Uint8 *)canvas->pixels+(dy*8+py)*canvas->pitch)+dx*8+px;
   if(!hd_owner[n]&&!cloud_owner[n])*dst=palette_rgb(((Uint8 *)game_screen->pixels)[dy*320+dx]);
   *dst=blend_rgba(*dst,a,a[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
   cyan_borrow_mark(n,*dst);
  }
  selected[dy*320+dx]=1;
 }
 ++draws;return true;
}
static unsigned cyan_row(SDL_Surface *surface,int x,int y,Uint8 **map,int style)
{
 render_mirror_cyan_row_end();if(!cyan_pass.live)return 0;
 if(!cyan_context(surface)||surface!=cyan_pass.surface||style!=MIRROR_NORMAL||cyan_pass.row>=8||x!=cyan_pass.x||
  y!=cyan_pass.y+(int)cyan_pass.row*28||(uintptr_t)map!=(uintptr_t)&megaData2.mainmap[0][0]+(cyan_pass.first+cyan_pass.row*14)*sizeof(JE_byte *)){
  if(cyan_pass.drew)render_mirror_unsupported("cyan-pass-integrity");
  render_mirror_cyan_end();return 0;}
 /* Reject clones/offsets and source mutation before any tile in this row. */
 for(unsigned tile=0;tile<12;tile++)if(map[tile]){
  unsigned id=cyan_id(map[tile]);if(!id||map[tile]!=cyan_pass.sources[cyan_pass.row][tile]){
   if(cyan_pass.drew)render_mirror_unsupported("cyan-source-or-zero");
   render_mirror_cyan_end();return 0;}
 }
 for(unsigned g=0;g<2;g++)if((cyan_pass.ready&(1u<<g))&&!cyan_group_sources_valid(g))cyan_pass.ready&=~(1u<<g);
 cyan_pass.row++;unsigned replaced=0;
 for(unsigned tile=0;tile<12;tile++){
  int k=cyan_member(cyan_id(map[tile]));if(k<0||!(cyan_pass.ready&(1u<<cyan_group_of((unsigned)k))))continue;
  bool mirrored=cyan_tile_draw((unsigned)k,x+(int)tile*24,y);
  /* Unsupported drawing can reset the pass (including its row ordinal). */
  if(!cyan_pass.live||reject_reason)return 0;
  if(mirrored){
   replaced|=1u<<tile;cyan_pass.used|=1u<<cyan_group_of((unsigned)k);cyan_pass.drew=true;cyan_frame.live=true;
   cyan_frame.surface=surface;cyan_frame.generation=cyan_pass.generation;cyan_frame.secondary_generation=cyan_pass.secondary_generation;cyan_frame.used=cyan_pass.used;
   cyan_frame.geometry=cyan_pass.geometry;
   memcpy(cyan_frame.palette,cyan_pass.palette,sizeof(cyan_frame.palette));
  }
  if(cyan_trace())fprintf(stderr,"cyan-tile tick=%u logic_tick=%llu id=%u x=%d y=%d hd=%d row=%u\n",game_probe_tick,(unsigned long long)mirror_logic_tick,cyan_id_at((unsigned)k),x+(int)tile*24,y,mirrored,cyan_pass.row-1);
  game_probe_scene_draw(ASSET_SHAPESY_CYAN,cyan_id_at((unsigned)k),x+(int)tile*24,y,0,MIRROR_NORMAL,mirrored);
 }
 cyan_pass.replaced[cyan_pass.row-1]=replaced;

 cyan_row_lease.live=true;cyan_row_lease.replaced=replaced;cyan_row_lease.x=x;cyan_row_lease.y=y;
 cyan_row_lease.generation=cyan_pass.generation;cyan_row_lease.secondary_generation=cyan_pass.secondary_generation;cyan_row_lease.used=cyan_pass.used;
 for(unsigned t=0;t<12;t++){
  cyan_row_lease.sources[t]=map[t];if(!(replaced&(1u<<t)))continue;
  for(unsigned i=0;i<672;i++){
   int dx=x+t*24+i%24,dy=y+i/24;
   if(dx>=0&&dx<320&&dy>=0&&dy<200&&map[t][i])cyan_row_lease.left++;
  }
 }
 return replaced;
}
static bool cyan_native_pixel(SDL_Surface *surface,Uint8 *address,Uint8 source,int style,bool replaced,bool *qualified)
{
 if(qualified)*qualified=false;
 if(reject_reason||!replaced||!cyan_pass.live||!cyan_row_lease.live||surface!=cyan_pass.surface||style!=MIRROR_NORMAL)return false;
 if(!cyan_context_base(surface)||!cyan_generations(cyan_pass.used,cyan_pass.generation,cyan_pass.secondary_generation)||
  cyan_row_lease.used!=cyan_pass.used||!cyan_generations(cyan_row_lease.used,cyan_row_lease.generation,cyan_row_lease.secondary_generation)||memcmp(cyan_pass.palette,rgb_palette,sizeof(cyan_pass.palette))){
  render_mirror_unsupported("cyan-pixel-context");render_mirror_cyan_end();return false;
 }
 intptr_t offset=(intptr_t)address-(intptr_t)surface->pixels;
 if(offset<0||offset>=surface->pitch*surface->h)return false;
 int x=(int)(offset%surface->pitch)-cyan_row_lease.x,y=(int)(offset/surface->pitch)-cyan_row_lease.y;
 if(x<0||x>=288||y<0||y>=28)return false;
 unsigned t=(unsigned)x/24;const Uint8 *s=cyan_row_lease.sources[t];
 int k=cyan_member(cyan_id(s));
 if(!(cyan_row_lease.replaced&(1u<<t))||k<0||!s||s[y*24+x%24]!=source||memcmp(s,cyan_registry.source[k],672)){
  render_mirror_unsupported("cyan-pixel-identity");render_mirror_cyan_end();return false;}
 unsigned i=(unsigned)y*24+(unsigned)x%24;
 if(!source||cyan_row_lease.seen[t][i]||!cyan_row_lease.left){
  render_mirror_unsupported("cyan-pixel-duplicate");return false;}
 cyan_row_lease.seen[t][i]=1;cyan_row_lease.left--;
 if(qualified)*qualified=true;
 return false;
}

/* Keep the contributed-frame witness after the layer2 pass ends.
 * VGAScreen legitimately switches to VGAScreenSeg before finish; do not reuse
 * the draw-site surface equality there. No extra per-pixel ownership map. */
static bool cyan_frame_check(void)
{
 if(!cyan_frame.live)return true;
 if(!cyan_borrow_layout(cyan_frame.borrow_serial)||!cyan_geometry_matches(&cyan_frame.geometry)||!cyan_snapshot_valid()||cyan_pass.live||cyan_row_lease.live||cyan_frame.surface!=game_screen||
  asteroid_hd_enabled||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !(game_probe_scene_assets&2)||!game_probe_assets||cyan_frame.used!=cyan_pass.used||
  !cyan_generations(cyan_frame.used,cyan_frame.generation,cyan_frame.secondary_generation)||
  filterFade||levelFilter!=-99||levelBrightness!=-99||
  memcmp(cyan_frame.palette,rgb_palette,sizeof(cyan_frame.palette))||!cyan_sources_mask_valid(cyan_frame.used)||!cyan_cache_valid()||
  (cyan_layer1_dependency&&!shapesy_borrow_check(cyan_layer1_dependency)))return false;
 for(unsigned i=0;i<9;i++)if(smoothies[i])return false;
 return true;
}

static bool cyan_borrow_layout(uint64_t serial)
{
 return serial&&cyan_borrow.sealed&&!cyan_borrow.building&&!cyan_borrow.failed&&
  serial==cyan_borrow.serial&&cyan_borrow.values&&cyan_borrow.capacity==320u*200u*8u*8u&&
  cyan_borrow.tick==mirror_logic_tick&&cyan_borrow.used&&cyan_generations(cyan_borrow.used,cyan_borrow.generation,cyan_borrow.secondary_generation)&&
  cyan_frame.live&&cyan_frame.used==cyan_borrow.used&&
  (!(cyan_borrow.used&1)||cyan_frame.generation==cyan_borrow.generation)&&
  (!(cyan_borrow.used&2)||cyan_frame.secondary_generation==cyan_borrow.secondary_generation)&&
  canvas&&canvas==cyan_borrow.canvas_surface&&canvas->pixels==cyan_borrow.pixels&&
  canvas->format==cyan_borrow.format&&canvas->w==cyan_borrow.w&&canvas->h==cyan_borrow.h&&
  canvas->pitch==cyan_borrow.pitch&&canvas->pitch==2560*4&&((uintptr_t)canvas->pixels%sizeof(Uint32)==0)&&canvas->format&&canvas->format->format==SDL_PIXELFORMAT_ARGB8888&&
  canvas->format->BitsPerPixel==32&&canvas->format->BytesPerPixel==4&&
  game_screen&&game_screen==cyan_borrow.index_surface&&game_screen->pixels==cyan_borrow.index_pixels&&
  game_screen->format==cyan_borrow.index_format&&game_screen->pitch==cyan_borrow.index_pitch&&
  game_screen->w==320&&game_screen->h==200&&game_screen->pitch==320&&game_screen->format&&
  game_screen->format->format==SDL_PIXELFORMAT_INDEX8&&game_screen->format->BitsPerPixel==8&&game_screen->format->BytesPerPixel==1&&
  !game_screen->clip_rect.x&&!game_screen->clip_rect.y&&game_screen->clip_rect.w==320&&game_screen->clip_rect.h==200&&
  game_probe_density==8&&!reject_reason;
}
static uint64_t cyan_borrow_ready(void)
{
 uint64_t serial=cyan_borrow.serial;
 return cyan_borrow_layout(serial)&&cyan_frame_check()&&cyan_geometry_matches(&cyan_borrow.geometry)?serial:0;
}
static bool cyan_borrow_sample(uint64_t serial,size_t n,Uint32 color)
{
 return cyan_borrow_layout(serial)&&n<cyan_borrow.capacity&&
  (color>>24)==255&&cyan_borrow.values[n]==color;
}
static bool cyan_borrow_check(uint64_t serial)
{
 /* Final/cached checks rehash mutable asset payloads, not merely frame flags.
  * No resource scans happen inside the per-pixel borrowed-value test. */
 return cyan_borrow_layout(serial)&&cyan_frame_check()&&
  cyan_geometry_matches(&cyan_borrow.geometry)&&cyan_cache_valid();
}
static bool cyan_present_geometry(SDL_Renderer *renderer, const SDL_Rect *dst)
{
 if (!cyan_frame.live) return true;
 const VideoOutputGeometry *g = &cyan_frame.geometry;
 return renderer == g->renderer && dst && dst->x == g->dst.x && dst->y == g->dst.y && dst->w == g->dst.w && dst->h == g->dst.h;
}
