#include "current_enemy_orb_payload_pins.h"
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Shared enemy-only normal TYRIAN.SHP selectors112/113. The original engine
 * owns their phase, firing, motion and lifetime; this role claims no emitter.
 * Both optional resources are one atomic family, never generic/player role8.
 */
/* Independent from body and304 payload/lease identity. Authenticate all32060
 * current bytes, including offsets, unused sprites and terminal RLE data.
 * Normal bank SHA256:9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68. */
static struct {bool valid;Uint8 bytes[32060];} enemy_orb112113_source_snapshot;
static struct {bool checked,valid,frame_checked,drew;uint64_t checked_tick,drawn_tick;char root[1024];Asset members[2];} enemy_orb112113_resources;
/* Reviewed authored96x112 RGBA, registered to each original45-cell support. */
static const uint64_t enemy_orb112113_rgba_pins[2]={CURRENT_ENEMY_ORB_1420112_PAYLOAD_FNV,CURRENT_ENEMY_ORB_1420113_PAYLOAD_FNV};
static void enemy_orb112113_shutdown(void)
{
 for(unsigned k=0;k<2;k++)free(enemy_orb112113_resources.members[k].rgba);
 memset(&enemy_orb112113_resources,0,sizeof(enemy_orb112113_resources));
 enemy_orb112113_source_snapshot.valid=false;enemy_orb112113_draw_lease=NULL;
}
static bool enemy_orb112113_source(Sprite2_array bank,unsigned index)
{
 if(xmas||(index!=112&&index!=113)||!bank.data||bank.data!=spriteSheet8.data||
  bank.data==spriteSheet12.data||bank.size!=spriteSheet8.size||
  bank.size!=sizeof(enemy_orb112113_source_snapshot.bytes))return false;
 if(!enemy_orb112113_source_snapshot.valid) {
  /* Pin the copy, never a live hash followed by an unverified snapshot. */
  memcpy(enemy_orb112113_source_snapshot.bytes,bank.data,bank.size);
  enemy_orb112113_source_snapshot.valid=asteroid1_stamp(enemy_orb112113_source_snapshot.bytes,bank.size)==UINT64_C(0x2b63027f74aaa21e);
 }
 /* Every callback compares every current byte, including warm/reused memory. */
 return enemy_orb112113_source_snapshot.valid&&
  !memcmp(bank.data,enemy_orb112113_source_snapshot.bytes,bank.size);
}
static bool enemy_orb112113_load(unsigned k,Asset *result)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-orb112113-%u-8.hda",enemy_orb112113_resources.root,112+k);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1_ENEMY_ORB112113*10000+112+k&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==enemy_orb112113_rgba_pins[k];
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *result=(Asset){true,true,ASSET_ASTEROID1_ENEMY_ORB112113,(int)(112+k),12,14,0,0,8,rgba};
 return true;
}
/* No partial admission: missing/corrupt either phase disables both for the
 * selected-root epoch. Disk replacements require renderer cache shutdown. */
static bool enemy_orb112113_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(enemy_orb112113_resources.root))return false;
 if(!enemy_orb112113_resources.checked) {
  enemy_orb112113_resources.checked=true;
  memcpy(enemy_orb112113_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  Asset loaded[2]={{0},{0}};
  bool ok=enemy_orb112113_load(0,&loaded[0])&&enemy_orb112113_load(1,&loaded[1]);
  if(ok)memcpy(enemy_orb112113_resources.members,loaded,sizeof(loaded));
  else for(unsigned k=0;k<2;k++)free(loaded[k].rgba);
  enemy_orb112113_resources.valid=ok;
 }
 if(!enemy_orb112113_resources.valid||strcmp(enemy_orb112113_resources.root,game_probe_assets))return false;
 if(enemy_orb112113_resources.frame_checked&&enemy_orb112113_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned k=0;k<2;k++) {
  Asset *a=&enemy_orb112113_resources.members[k];
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_ENEMY_ORB112113||a->index!=(int)(112+k)||
   a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=enemy_orb112113_rgba_pins[k]) {
   enemy_orb112113_resources.valid=false;return false;
  }
 }
 enemy_orb112113_resources.checked_tick=mirror_logic_tick;enemy_orb112113_resources.frame_checked=true;
 return true;
}
static bool enemy_orb112113_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||(index!=112&&index!=113))return false;
 /* Original RLE wraps horizontally; mirror only equivalent tile geometry.
  * Original indexed writes still own top/bottom clipping, once per wrapper. */
 if(!enemy_orb112113_source(bank,index)||!enemy_orb112113_family_ready()) {
  if(enemy_orb112113_resources.drew&&enemy_orb112113_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("enemy-orb112113-integrity");
  return false;
 }
 Asset *a=&enemy_orb112113_resources.members[index-112];
 enemy_orb112113_draw_lease=a;
 bool mirrored=draw_asset_filtered(x,y,a,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);
 enemy_orb112113_draw_lease=NULL;
 if(mirrored){enemy_orb112113_resources.drew=true;enemy_orb112113_resources.drawn_tick=mirror_logic_tick;}
 return mirrored;
}
