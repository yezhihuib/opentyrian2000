/* SPDX-License-Identifier: GPL-2.0-or-later
 * Shared enemy-only normal TYRIAN.SHP selector304. This display role does not
 * claim an emitter: original weapons142/144 and their actors remain unchanged.
 * The original surviving-shot wrapper always executes one indexed tile blit.
 */
/* Independent from the NEWSHD body snapshot: authenticate all current32060
 * bytes, including offsets, unused sprites and the complete terminal304 RLE.
 * Normal bank SHA256:9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68. */
static struct {bool valid;Uint8 bytes[32060];} projectile304_source_snapshot;
static struct {bool checked,valid,frame_checked,drew;uint64_t checked_tick,drawn_tick;char root[1024];Asset member;} projectile304_resources;
/* Reviewed authored96x112 RGBA, registered to the original13 occupied cells. */
static const uint64_t projectile304_rgba_pin=UINT64_C(0xd03f12e69b2f4417);
static void projectile304_shutdown(void)
{
 free(projectile304_resources.member.rgba);
 memset(&projectile304_resources,0,sizeof(projectile304_resources));
 projectile304_source_snapshot.valid=false;projectile304_draw_lease=NULL;
}
static bool projectile304_source(Sprite2_array bank,unsigned index)
{
 if(xmas||index!=304||!bank.data||bank.data!=spriteSheet8.data||
  bank.data==spriteSheet12.data||bank.size!=spriteSheet8.size||
  bank.size!=sizeof(projectile304_source_snapshot.bytes))return false;
 if(!projectile304_source_snapshot.valid) {
  /* Pin the copy, never a live hash followed by an unverified snapshot. */
  memcpy(projectile304_source_snapshot.bytes,bank.data,bank.size);
  projectile304_source_snapshot.valid=asteroid1_stamp(projectile304_source_snapshot.bytes,bank.size)==UINT64_C(0x2b63027f74aaa21e);
 }
 /* Every callback compares every current byte, including warm/reused memory. */
 return projectile304_source_snapshot.valid&&
  !memcmp(bank.data,projectile304_source_snapshot.bytes,bank.size);
}
static bool projectile304_load(void)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-projectile304-304-8.hda",projectile304_resources.root);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1_PROJECTILE304*10000+304&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==projectile304_rgba_pin;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 projectile304_resources.member=(Asset){true,true,ASSET_ASTEROID1_PROJECTILE304,304,12,14,0,0,8,rgba};
 return true;
}
/* One optional resource, independent from every enemy body family. Missing,
 * corrupt or foreign data fails only this role for the selected-root epoch.
 * A disk replacement becomes visible only after renderer cache shutdown. */
static bool projectile304_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(projectile304_resources.root))return false;
 if(!projectile304_resources.checked) {
  projectile304_resources.checked=true;
  memcpy(projectile304_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  projectile304_resources.valid=projectile304_load();
 }
 if(!projectile304_resources.valid||strcmp(projectile304_resources.root,game_probe_assets))return false;
 if(projectile304_resources.frame_checked&&projectile304_resources.checked_tick==mirror_logic_tick)return true;
 Asset *a=&projectile304_resources.member;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_PROJECTILE304||a->index!=304||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile304_rgba_pin) {
  projectile304_resources.valid=false;return false;
 }
 projectile304_resources.checked_tick=mirror_logic_tick;projectile304_resources.frame_checked=true;
 return true;
}
static bool projectile304_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||index!=304)return false;
 /* Original RLE wraps horizontally; only geometrically equivalent tiles are
  * mirrored. Top/bottom clipping stays in the original indexed blitter. */
 if(!projectile304_source(bank,index)||!projectile304_family_ready()) {
  if(projectile304_resources.drew&&projectile304_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("projectile304-integrity");
  return false;
 }
 projectile304_draw_lease=&projectile304_resources.member;
 bool mirrored=draw_asset_filtered(x,y,&projectile304_resources.member,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);
 projectile304_draw_lease=NULL;
 if(mirrored){projectile304_resources.drew=true;projectile304_resources.drawn_tick=mirror_logic_tick;}
 return mirrored;
}
