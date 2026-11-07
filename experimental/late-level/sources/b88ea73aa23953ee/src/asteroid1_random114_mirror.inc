/* SPDX-License-Identifier: GPL-2.0-or-later
 * One static random asteroid shared by records319–320 (motion variants). Original calls, clipping, events and
 * linked destruction remain authoritative. No ordinary spriteSheet8 binding.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
static const struct {unsigned type,base,size;uint64_t record,rgba;} asteroid_random114_pins[2]={
 {319,114,0,UINT64_C(0x438e34fc179d35fb),UINT64_C(0x2b3ea6044500ab20)},
 {320,114,0,UINT64_C(0xd4dd0adbd842dda9),UINT64_C(0x2b3ea6044500ab20)},
};
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[1];} asteroid_random114_resources;
static void asteroid_random114_shutdown(void)
{
 for(unsigned i=0;i<1;i++)free(asteroid_random114_resources.member[i].rgba);
 memset(&asteroid_random114_resources,0,sizeof(asteroid_random114_resources));
}
/* Current bytes are checked on every draw, including warm/address-reused banks.
 * All motion records are one dependency; there is only one image pose. */
static bool asteroid_random114_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=42012)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!asteroid1_source_bytes_match(bank.data,bank.size))return false;
 for(unsigned i=0;i<2;i++)
  if(asteroid1_record_stamp(asteroid_random114_pins[i].type)!=asteroid_random114_pins[i].record)return false;
 return true;
}
static bool asteroid_random114_load(unsigned k)
{
 Asset *a=&asteroid_random114_resources.member[k];
 unsigned w=asteroid_random114_pins[k].size?24:12,h=asteroid_random114_pins[k].size?28:14;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshd-%u-8.hda",asteroid_random114_resources.root,asteroid_random114_pins[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1*10000+asteroid_random114_pins[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==asteroid_random114_pins[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1,(int)asteroid_random114_pins[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* Coherent preflight and sticky failure for this selected-root cache lifetime.
 * Density4 and missing/corrupt/foreign-role resources never get partial HD. */
static bool asteroid_random114_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(asteroid_random114_resources.root))return false;
 if(!asteroid_random114_resources.checked) {
  asteroid_random114_resources.checked=true;asteroid_random114_resources.valid=true;
  memcpy(asteroid_random114_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<1;i++)if(!asteroid_random114_load(i))asteroid_random114_resources.valid=false;
 }
 if(!asteroid_random114_resources.valid||strcmp(asteroid_random114_resources.root,game_probe_assets))return false;
 /* Private payloads are immutable after load. Verify the whole family once
  * before the first original call each display frame, never 12 full scans. */
 if(asteroid_random114_resources.frame_checked&&asteroid_random114_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<1;i++) {
  Asset *a=&asteroid_random114_resources.member[i];int w=asteroid_random114_pins[i].size?24:12,h=asteroid_random114_pins[i].size?28:14;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)asteroid_random114_pins[i].base||
   a->w!=w||a->h!=h||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)w*h*8*8*4)!=asteroid_random114_pins[i].rgba) {
   asteroid_random114_resources.valid=false;return false;
  }
 }
 asteroid_random114_resources.checked_tick=mirror_logic_tick;asteroid_random114_resources.frame_checked=true;
 return true;
}
static bool asteroid_random114_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||!c||c->type<319||c->type>320||
  c->availability==1||c->availability>2||c->score_item||c->damaged||!c->static_animation)return false;
 unsigned k=c->type-319;
 if(base!=asteroid_random114_pins[k].base||c->size!=asteroid_random114_pins[k].size||
  (c->size==0&&part!=0)||(c->size==1&&part!=0&&part!=1&&part!=19&&part!=20)||
  filter<0||filter>255)return false;
 if(!asteroid_random114_source(bank)||!asteroid_random114_family_ready()) {
  /* A dependency failure after an accepted quadrant rejects this entire frame.
   * Cold missing art stays an ordinary local classic fallback. */
  if(asteroid_random114_resources.drew&&asteroid_random114_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("asteroid-random114-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 bool mirrored=draw_asset_filtered(x-px,y-py,&asteroid_random114_resources.member[0],MIRROR_NORMAL,
  c->size?&quadrant:NULL,(Uint8)filter,NULL,NULL,NULL);
 if(mirrored){asteroid_random114_resources.drew=true;asteroid_random114_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
