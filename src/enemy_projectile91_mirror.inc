/* SPDX-License-Identifier: GPL-2.0-or-later
 * Shared enemy-only normal TYRIAN.SHP selector91. This display role does not
 * claim an emitter: original weapon24 and shared actors173/285 remain unchanged.
 * The original surviving-shot wrapper always executes one indexed tile blit.
 */
/* Independent from the NEWSHD body snapshot: authenticate all current32060
 * bytes, including offsets, unused sprites and the complete selector91 RLE.
 * Normal bank SHA256:9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68. */
static struct {bool valid;Uint8 bytes[32060];} projectile91_source_snapshot;
static struct {bool checked,valid,frame_checked,drew;uint64_t checked_tick,drawn_tick;char root[1024];Asset member;} projectile91_resources;
/* Deterministic selected master, contained by the original62 occupied cells. */
#include "current_projectile91_payload_pins.h"
static const uint64_t projectile91_rgba_pin=CURRENT_PROJECTILE91_PAYLOAD_FNV;
static void projectile91_shutdown(void)
{
 free(projectile91_resources.member.rgba);
 memset(&projectile91_resources,0,sizeof(projectile91_resources));
 projectile91_source_snapshot.valid=false;projectile91_draw_lease=NULL;
}
static bool projectile91_source(Sprite2_array bank,unsigned index)
{
 if(xmas||index!=91||!bank.data||bank.data!=spriteSheet8.data||
  bank.data==spriteSheet12.data||bank.size!=spriteSheet8.size||
  bank.size!=sizeof(projectile91_source_snapshot.bytes))return false;
 if(!projectile91_source_snapshot.valid) {
  /* Pin the copy, never a live hash followed by an unverified snapshot. */
  memcpy(projectile91_source_snapshot.bytes,bank.data,bank.size);
  projectile91_source_snapshot.valid=asteroid1_stamp(projectile91_source_snapshot.bytes,bank.size)==UINT64_C(0x2b63027f74aaa21e);
 }
 /* Every callback compares every current byte, including warm/reused memory. */
 return projectile91_source_snapshot.valid&&
  !memcmp(bank.data,projectile91_source_snapshot.bytes,bank.size);
}
static bool projectile91_load(void)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-projectile91-91-8.hda",projectile91_resources.root);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ENEMY_PROJECTILE91*10000+91&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==projectile91_rgba_pin;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 projectile91_resources.member=(Asset){true,true,ASSET_ENEMY_PROJECTILE91,91,12,14,0,0,8,rgba};
 return true;
}
/* One optional resource, independent from every enemy body family. Missing,
 * corrupt or foreign data fails only this role for the selected-root epoch.
 * A disk replacement becomes visible only after renderer cache shutdown. */
static bool projectile91_ready_at(const char *root)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !root||!root[0]||strlen(root)>=sizeof(projectile91_resources.root))return false;
 if(!projectile91_resources.checked) {
  projectile91_resources.checked=true;
  memcpy(projectile91_resources.root,root,strlen(root)+1);
  projectile91_resources.valid=projectile91_load();
 }
 if(!projectile91_resources.valid||strcmp(projectile91_resources.root,root))return false;
 /* Validate every callback: in-frame mutation must never reuse a warm lease. */
 Asset *a=&projectile91_resources.member;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ENEMY_PROJECTILE91||a->index!=91||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile91_rgba_pin) {
  projectile91_resources.valid=false;return false;
 }
 projectile91_resources.checked_tick=mirror_logic_tick;projectile91_resources.frame_checked=true;
 return true;
}
static bool projectile91_family_ready(void)
{return projectile91_ready_at(game_probe_assets);}
static Asset *projectile91_resource(const char *root)
{return projectile91_ready_at(root)?&projectile91_resources.member:NULL;}
static bool projectile91_palette_matches(void)
{
 static const unsigned indices[]={1,2,5,6,7,8,9,10,11,12,13,14,15};
 static const Uint32 colors[]={0x0c0c0c,0x181818,0x454545,0x515151,0x5d5d5d,0x696d69,0x797979,0x8e8e8e,0xa2a6a2,0xbababa,0xcfcfcf,0xe7e7e7,0xfbffff};
 for(unsigned i=0;i<sizeof(indices)/sizeof(*indices);i++)if((rgb_palette[indices[i]]&0xffffffu)!=colors[i])return false;
 return true;
}
static bool projectile91_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index)
{
 if(!active||reject_reason||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||index!=91)return false;
 /* Original RLE wraps horizontally; only geometrically equivalent tiles are
  * mirrored. Top/bottom clipping stays in the original indexed blitter. */
 if(!projectile91_source(bank,index)||!projectile91_palette_matches()||!projectile91_family_ready()) {
  if(projectile91_resources.drew&&projectile91_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("projectile91-integrity");
  return false;
 }
 projectile91_draw_lease=&projectile91_resources.member;
 bool mirrored=draw_asset_filtered(x,y,&projectile91_resources.member,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);
 projectile91_draw_lease=NULL;
 if(mirrored){projectile91_resources.drew=true;projectile91_resources.drawn_tick=mirror_logic_tick;}
 return mirrored;
}
