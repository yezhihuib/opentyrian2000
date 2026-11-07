/* SPDX-License-Identifier: GPL-2.0-or-later
 * One static capsule enemy from scheduled record545. Original calls, clipping,
 * acceleration/reversal events and destruction remain authoritative. No ordinary spriteSheet8 binding.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
static const struct {unsigned type,base,size;uint64_t record,rgba;} capsule545_pins[1]={
 {545,77,1,UINT64_C(0x61d596d8bffd5774),UINT64_C(0x16455d50d28008e8)},
};
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[1];} capsule545_resources;
static void capsule545_shutdown(void)
{
 for(unsigned i=0;i<1;i++)free(capsule545_resources.member[i].rgba);
 memset(&capsule545_resources,0,sizeof(capsule545_resources));
}
/* Current bytes are checked on every draw, including warm/address-reused banks.
 * The exact scheduled source record is pinned; there is only one image pose. */
static bool capsule545_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=42012)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!asteroid1_source_bytes_match(bank.data,bank.size))return false;
 for(unsigned i=0;i<1;i++)
  if(asteroid1_record_stamp(capsule545_pins[i].type)!=capsule545_pins[i].record)return false;
 return true;
}
static bool capsule545_load(unsigned k)
{
 Asset *a=&capsule545_resources.member[k];
 unsigned w=capsule545_pins[k].size?24:12,h=capsule545_pins[k].size?28:14;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshd-%u-8.hda",capsule545_resources.root,capsule545_pins[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1*10000+capsule545_pins[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==capsule545_pins[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1,(int)capsule545_pins[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* Coherent preflight and sticky failure for this selected-root cache lifetime.
 * Density4 and missing/corrupt/foreign-role resources never get partial HD. */
static bool capsule545_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(capsule545_resources.root))return false;
 if(!capsule545_resources.checked) {
  capsule545_resources.checked=true;capsule545_resources.valid=true;
  memcpy(capsule545_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<1;i++)if(!capsule545_load(i))capsule545_resources.valid=false;
 }
 if(!capsule545_resources.valid||strcmp(capsule545_resources.root,game_probe_assets))return false;
 /* Private payloads are immutable after load. Verify the whole family once
  * before the first original call each display frame, never 12 full scans. */
 if(capsule545_resources.frame_checked&&capsule545_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<1;i++) {
  Asset *a=&capsule545_resources.member[i];int w=capsule545_pins[i].size?24:12,h=capsule545_pins[i].size?28:14;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)capsule545_pins[i].base||
   a->w!=w||a->h!=h||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)w*h*8*8*4)!=capsule545_pins[i].rgba) {
   capsule545_resources.valid=false;return false;
  }
 }
 capsule545_resources.checked_tick=mirror_logic_tick;capsule545_resources.frame_checked=true;
 return true;
}
/* Original event10 pool75-99 and links1-9 only. Event19/20/27 may change
 * any motion/acceleration/reversal state; those fields remain authoritative.
 * This record has no source drop or applicable normal-campaign event33. */
static bool capsule545_actor(Sprite2_array bank,unsigned base,int x,int y,int part,int filter,const G101EnemyContext *c)
{
 if(!c||c->type!=545||!(c->pool_slot>=75&&c->pool_slot<100)||c->availability!=0||c->size!=1||
  c->score_item||c->damaged||!c->static_animation)return false;
 const struct JE_SingleEnemyType *e=&enemy[c->pool_slot];
 if(enemyAvail[c->pool_slot]!=0||e->enemytype!=545||e->enemydatofs!=&enemyDat[545]||
  e->size!=1||e->scoreitem||e->edamaged||!e->armorleft||
  !e->sprite2s||e->sprite2s->data!=bank.data||e->sprite2s->size!=bank.size||
  e->ani!=1||e->enemycycle!=1||e->aniactive||e->animin!=1||e->animax||e->aniwhenfire||
  e->filter!=filter)return false;
 if(e->linknum<1||e->linknum>9||e->enemydie)return false;
 if(c->independent_motion!=(bool)(e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel))return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=(i?0:77))return false;
 if(base!=77||e->tur[0]||e->tur[1]||e->tur[2]||e->freq[0]||e->freq[1]||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 return x-px==e->ex+e->mapoffset-6&&y-py==e->ey-7;
}
static bool capsule545_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||!capsule545_actor(bank,base,x,y,part,filter,c))return false;
 unsigned k=0;
 if(base!=capsule545_pins[k].base||c->size!=capsule545_pins[k].size||
  (c->size==0&&part!=0)||(c->size==1&&part!=0&&part!=1&&part!=19&&part!=20)||
  filter<0||filter>255)return false;
 if(!capsule545_source(bank)||!capsule545_family_ready()) {
  /* A dependency failure after an accepted quadrant rejects this entire frame.
   * Cold missing art stays an ordinary local classic fallback. */
  if(capsule545_resources.drew&&capsule545_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("capsule545-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 bool mirrored=draw_asset_filtered(x-px,y-py,&capsule545_resources.member[0],MIRROR_NORMAL,
  c->size?&quadrant:NULL,(Uint8)filter,NULL,NULL,NULL);
 if(mirrored){capsule545_resources.drew=true;capsule545_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
