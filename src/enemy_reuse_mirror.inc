/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite, default-off P02/P04/P05 enemy semantics. P09 has one private material identity;
 * rendering identity146 is private and never passes through player get_asset.
 * Probe and isolated normal-game observation share only the finite role146 lane.
 */
static const unsigned enemy_reuse_ids[12]={105,106,124,125,20,21,214,215,216,226,227,244};
static const uint64_t enemy_reuse_pins[12]={
 CURRENT_SONIC_80105_D8_PAYLOAD_FNV,CURRENT_SONIC_80106_D8_PAYLOAD_FNV,
 CURRENT_SONIC_80124_D8_PAYLOAD_FNV,CURRENT_SONIC_80125_D8_PAYLOAD_FNV,
 CURRENT_GUIDED_80020_D8_PAYLOAD_FNV,CURRENT_GUIDED_80021_D8_PAYLOAD_FNV,
 CURRENT_GREEN_80214_RGBA,CURRENT_GREEN_80215_RGBA,CURRENT_GREEN_80216_RGBA,
 CURRENT_PROTRON_80226_D8_PAYLOAD_FNV,CURRENT_PROTRON_1470227_D8_PAYLOAD_FNV,CURRENT_PROTRON_80244_D8_PAYLOAD_FNV};
static struct {bool checked[3],valid[3];char root[1024];Asset members[12];unsigned observed_candidates,observed_frames;} enemy_reuse_resources;
enum EnemyReuseSession {ENEMY_REUSE_LEGACY,ENEMY_REUSE_NORMAL,ENEMY_REUSE_CONTROLLED};
static struct {enum EnemyReuseSession session;uint64_t session_generation;bool output_phase,contributed,families[3];Sprite2_array bank;Uint32 palette[256];
 SDL_Surface *surface,*final_surface;void *pixels,*final_pixels;SDL_PixelFormat *format,*final_format;
 bool used[60];unsigned index[60];int x[60],y[60];uint64_t generation[60];
} enemy_reuse_frame;
static uint64_t enemy_reuse_hash(const void *data,size_t size)
{const Uint8 *p=data;uint64_t h=UINT64_C(0xcbf29ce484222325);while(size--){h^=*p++;h*=UINT64_C(0x100000001b3);}return h;}
static int enemy_reuse_member(unsigned index)
{for(unsigned i=0;i<12;i++)if(enemy_reuse_ids[i]==index)return (int)i;return -1;}
static bool enemy_reuse_source(Sprite2_array bank)
{return !xmas&&bank.data&&bank.data==spriteSheet8.data&&bank.data!=spriteSheet12.data&&
 bank.size==32060&&bank.size==spriteSheet8.size&&enemy_reuse_hash(bank.data,bank.size)==UINT64_C(0x2b63027f74aaa21e);}
static const char *enemy_reuse_asset_root(void)
{return enemy_reuse_observe_requested()?enemy_reuse_observe_assets():game_probe_assets;}
static bool enemy_reuse_scope(void)
{
 uint64_t h=UINT64_C(0xcbf29ce484222325);
 for(unsigned i=0;i<256;i++)for(int s=16;s>=0;s-=8){h^=(rgb_palette[i]>>s)&255;h*=UINT64_C(0x100000001b3);}
 return (game_probe_enabled||enemy_reuse_observe_active())&&!asteroid_hd_enabled&&!manual_hd_enabled&&
  !xmas&&!twoPlayerMode&&!galagaMode&&!twoPlayerLinked&&!isNetworkGame&&
  (!play_demo||enemy_reuse_probe_generation())&&!record_demo&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
  !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent&&
  game_probe_density==8&&!game_probe_missing&&!game_probe_invalid&&!game_probe_original_reference&&
  h==UINT64_C(0x5e80e83992be2927);
}
static void enemy_reuse_shutdown(void)
{
 for(unsigned i=0;i<12;i++)free(enemy_reuse_resources.members[i].rgba);
 memset(&enemy_reuse_resources,0,sizeof(enemy_reuse_resources));
 memset(&enemy_reuse_frame,0,sizeof(enemy_reuse_frame));enemy_reuse_draw_lease=NULL;enemy_reuse_reset();
}
static void enemy_reuse_frame_begin(void)
{
 memset(&enemy_reuse_frame,0,sizeof(enemy_reuse_frame));enemy_reuse_draw_lease=NULL;
 if(enemy_reuse_observe_requested()) {
  enemy_reuse_frame.session=ENEMY_REUSE_NORMAL;
  enemy_reuse_frame.session_generation=enemy_reuse_observe_generation();
 } else if(enemy_reuse_probe_requested()) {
  enemy_reuse_frame.session=ENEMY_REUSE_CONTROLLED;
  enemy_reuse_frame.session_generation=enemy_reuse_probe_generation();
 }
}
/* Session kinds cannot lend authority to each other, including empty caches.
 * Legacy native probes retain their original game-surface-only contract. */
static bool enemy_reuse_session_valid(void)
{
 switch(enemy_reuse_frame.session) {
  case ENEMY_REUSE_NORMAL:
   return enemy_reuse_observe_requested()&&!enemy_reuse_probe_requested()&&
    enemy_reuse_frame.session_generation&&enemy_reuse_frame.session_generation==enemy_reuse_observe_generation();
  case ENEMY_REUSE_CONTROLLED:
   return !enemy_reuse_observe_requested()&&enemy_reuse_probe_requested()&&
    enemy_reuse_frame.session_generation&&enemy_reuse_frame.session_generation==enemy_reuse_probe_generation();
  default:return !enemy_reuse_observe_requested()&&!enemy_reuse_probe_requested();
 }
}
static bool enemy_reuse_load(unsigned k,Asset *result)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),k==10?"%s/enemy-protron-p09-%u-8.hda":"%s/bullet-%u-8.hda",enemy_reuse_resources.root,enemy_reuse_ids[k]);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=12u*14u*8u*8u*4u;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==(k==10?1470000:80000)+enemy_reuse_ids[k]&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&enemy_reuse_hash(rgba,bytes)==enemy_reuse_pins[k];
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *result=(Asset){true,true,146,(int)enemy_reuse_ids[k],12,14,0,0,8,rgba};return true;
}
/* The old six, P05 three and P09 three are independent atomic dependencies. A
 * missing green resource must never turn an already admitted old shot classic. */
static bool enemy_reuse_assets_valid(unsigned family)
{
 if(family>2||!enemy_reuse_resources.valid[family]||!enemy_reuse_asset_root()||strcmp(enemy_reuse_asset_root(),enemy_reuse_resources.root))return false;
 unsigned first=family==2?9:family?6:0,end=family==2?12:family?9:6;
 for(unsigned i=first;i<end;i++){
  Asset *a=&enemy_reuse_resources.members[i];
  if(!a->initialized||!a->valid||a->bank!=146||a->index!=(int)enemy_reuse_ids[i]||
   a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   enemy_reuse_hash(a->rgba,12u*14u*8u*8u*4u)!=enemy_reuse_pins[i])return false;
 }return true;
}
static bool enemy_reuse_family_ready(unsigned family)
{
 if(family>2||!enemy_reuse_asset_root()||!enemy_reuse_asset_root()[0]||strlen(enemy_reuse_asset_root())>=sizeof(enemy_reuse_resources.root))return false;
 /* A root change cannot free resources still referenced by this frame. It
  * declines until the explicit renderer shutdown, just like the orb cache. */
 if(enemy_reuse_resources.root[0]&&strcmp(enemy_reuse_asset_root(),enemy_reuse_resources.root))return false;
 if(!enemy_reuse_resources.checked[family]){
  enemy_reuse_resources.checked[family]=true;strcpy(enemy_reuse_resources.root,enemy_reuse_asset_root());
  Asset loaded[12]={{0}};bool ok=true;unsigned first=family==2?9:family?6:0,end=family==2?12:family?9:6;
  for(unsigned i=first;i<end&&ok;i++)ok=enemy_reuse_load(i,&loaded[i]);
  if(ok)for(unsigned i=first;i<end;i++)enemy_reuse_resources.members[i]=loaded[i];
  else for(unsigned i=first;i<end;i++)free(loaded[i].rgba);
  enemy_reuse_resources.valid[family]=ok;
 }return enemy_reuse_assets_valid(family);
}
static bool enemy_reuse_layout_matches(void)
{
 SDL_Surface *s=game_screen,*f=VGAScreenSeg;
 /* Original game output switches VGAScreen to the final indexed surface.
  * Only a live captured normal or controlled session admits that transition; both
  * captured owners, pixels and formats below must still be unchanged. */
 bool owner=s==VGAScreen||(enemy_reuse_frame.output_phase&&enemy_reuse_frame.session!=ENEMY_REUSE_LEGACY&&
  enemy_reuse_session_valid()&&f==VGAScreen);
 return s&&f&&owner&&s==enemy_reuse_frame.surface&&f==enemy_reuse_frame.final_surface&&
  s->pixels==enemy_reuse_frame.pixels&&f->pixels==enemy_reuse_frame.final_pixels&&
  s->format==enemy_reuse_frame.format&&f->format==enemy_reuse_frame.final_format&&
  s->w==320&&s->h==200&&s->pitch==320&&f->w==320&&f->h==200&&f->pitch==320&&
  s->format&&f->format&&s->format->format==SDL_PIXELFORMAT_INDEX8&&f->format->format==SDL_PIXELFORMAT_INDEX8&&
  s->format->BytesPerPixel==1&&f->format->BytesPerPixel==1&&s->format->BitsPerPixel==8&&f->format->BitsPerPixel==8;
}
static bool enemy_reuse_proof(void)
{
 if(!enemy_reuse_session_valid())return false;
 if(!enemy_reuse_frame.contributed)return true;
 if(!enemy_reuse_layout_matches()||!enemy_reuse_scope()||!enemy_reuse_source(enemy_reuse_frame.bank)||
  (enemy_reuse_frame.families[0]&&!enemy_reuse_assets_valid(0))||
  (enemy_reuse_frame.families[1]&&!enemy_reuse_assets_valid(1))||
  (enemy_reuse_frame.families[2]&&!enemy_reuse_assets_valid(2))||
  memcmp(enemy_reuse_frame.palette,rgb_palette,sizeof(enemy_reuse_frame.palette)))return false;
 for(unsigned i=0;i<60;i++)if(enemy_reuse_frame.used[i]&&
  !enemy_reuse_identity_live_generation(i,enemy_reuse_frame.index[i],enemy_reuse_frame.x[i],enemy_reuse_frame.y[i],
   enemy_reuse_frame.generation[i]))return false;
 return true;
}
static bool enemy_reuse_cache_check(void)
{
 bool valid=enemy_reuse_proof();
 if(valid&&enemy_reuse_frame.contributed&&last_output_valid){
  valid=!memcmp(last_output_palette,rgb_palette,sizeof(last_output_palette));
  for(int y=0;y<200&&valid;y++)valid=!memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)&&
   !memcmp(expected+y*320,(Uint8 *)game_screen->pixels+y*game_screen->pitch,320);
 }
 if(valid)return true;
 render_mirror_unsupported("enemy-reuse-provenance");
 ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;return false;
}
/* Bounded stderr diagnostics are read-only; no setup, replay, tick limit or
 * game state/RNG writes. A candidate is not an accepted output frame. */
static void enemy_reuse_observe_frame_result(bool accepted,const char *reason)
{
 if(!enemy_reuse_observe_requested()||!enemy_reuse_frame.contributed||enemy_reuse_resources.observed_frames>=16)return;
 ++enemy_reuse_resources.observed_frames;
 fprintf(stderr,"Enemy reuse observation: frame episode=%u physical=%u event-next=%u role=146 accepted=%u reason=%s\n",
  (unsigned)episodeNum,(unsigned)lvlFileNum,(unsigned)eventLoc,accepted?1u:0u,reason?reason:"none");
}
bool render_mirror_enemy_reuse_shot(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index,unsigned slot,unsigned raw)
{
 render_mirror_shadow_end();int k=enemy_reuse_member(index);
 bool identity=enemy_reuse_identity_matches(slot,index,x,y);
 if(enemy_reuse_observe_requested()&&identity&&k>=0&&enemy_reuse_resources.observed_candidates<16) {
  ++enemy_reuse_resources.observed_candidates;
  fprintf(stderr,"Enemy reuse observation: candidate episode=%u physical=%u event-next=%u slot=%u index=%u generation=%llu\n",
   (unsigned)episodeNum,(unsigned)lvlFileNum,(unsigned)eventLoc,slot,index,(unsigned long long)enemy_reuse_identity_generation(slot));
 }
 if(((enemy_reuse_observe_requested()||enemy_reuse_probe_requested())&&enemy_reuse_frame.output_phase)||!enemy_reuse_scope()||!active||reject_reason||k<0||(k<6?raw!=index:k<9?raw!=214:k==9?raw!=226:k==10?(raw!=226&&raw!=227):raw!=244)||slot>=60||(k>=9&&raw!=enemyShot[slot].sgr)||
  !surface||surface!=game_screen||surface!=VGAScreen||!surface->pixels||
  surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BytesPerPixel!=1||surface->format->BitsPerPixel!=8||
  x<0||x>308||y<-13||y>199)return false;
 if(!enemy_reuse_source(bank)||!identity||!enemy_reuse_proof()){
  if(enemy_reuse_frame.contributed)render_mirror_unsupported("enemy-reuse-integrity");return false;
 }
 unsigned family=k<6?0:k<9?1:2;
 if(!enemy_reuse_family_ready(family))return false;
 Asset *a=&enemy_reuse_resources.members[k];enemy_reuse_draw_lease=a;
 bool mirrored=draw_asset_filtered(x,y,a,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);enemy_reuse_draw_lease=NULL;
 if(mirrored){enemy_reuse_frame.contributed=true;enemy_reuse_frame.families[family]=true;enemy_reuse_frame.bank=bank;
  enemy_reuse_frame.surface=surface;enemy_reuse_frame.pixels=surface->pixels;enemy_reuse_frame.format=surface->format;
  enemy_reuse_frame.final_surface=VGAScreenSeg;enemy_reuse_frame.final_pixels=VGAScreenSeg?VGAScreenSeg->pixels:NULL;
  enemy_reuse_frame.final_format=VGAScreenSeg?VGAScreenSeg->format:NULL;
  memcpy(enemy_reuse_frame.palette,rgb_palette,sizeof(enemy_reuse_frame.palette));
  enemy_reuse_frame.used[slot]=true;enemy_reuse_frame.index[slot]=index;
  enemy_reuse_frame.x[slot]=x;enemy_reuse_frame.y[slot]=y;
  enemy_reuse_frame.generation[slot]=enemy_reuse_identity_generation(slot);
 }return mirrored;
}
