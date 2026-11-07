/* SPDX-License-Identifier: GPL-2.0-or-later
 * One source-bound record282 fire-triggered jewel pulse. Original calls, clipping, events and
 * original firing remain authoritative. No ordinary spriteSheet8 binding.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
static const struct {unsigned type,base,size;uint64_t record,rgba;} goldwing_pins[3]={
 {282,79,1,UINT64_C(0x8ccd3e8ca782f6f9),UINT64_C(0xf619d245a72b703a)},
 {282,81,1,UINT64_C(0x8ccd3e8ca782f6f9),UINT64_C(0xa88b0d99fdf38be4)},
 {282,83,1,UINT64_C(0x8ccd3e8ca782f6f9),UINT64_C(0x1cfd7f39ed3fe704)},
};
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[3];} goldwing_resources;
static void goldwing_shutdown(void)
{
 for(unsigned i=0;i<3;i++)free(goldwing_resources.member[i].rgba);
 memset(&goldwing_resources,0,sizeof(goldwing_resources));
}
/* Current bytes are checked on every draw, including warm/address-reused banks.
 * The exact source record is pinned; all three poses form one dependency. */
static bool goldwing_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=42012)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!asteroid1_source_bytes_match(bank.data,bank.size))return false;
 if(asteroid1_record_stamp(282)!=goldwing_pins[0].record)return false;
 return true;
}
static bool goldwing_load(unsigned k)
{
 Asset *a=&goldwing_resources.member[k];
 unsigned w=goldwing_pins[k].size?24:12,h=goldwing_pins[k].size?28:14;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshd-%u-8.hda",goldwing_resources.root,goldwing_pins[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1*10000+goldwing_pins[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==goldwing_pins[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1,(int)goldwing_pins[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* Coherent three-pose preflight and sticky failure for this selected-root cache lifetime.
 * Density4 and missing/corrupt/foreign-role resources never get partial HD. */
static bool goldwing_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(goldwing_resources.root))return false;
 if(!goldwing_resources.checked) {
  goldwing_resources.checked=true;goldwing_resources.valid=true;
  memcpy(goldwing_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<3;i++)if(!goldwing_load(i))goldwing_resources.valid=false;
 }
 if(!goldwing_resources.valid||strcmp(goldwing_resources.root,game_probe_assets))return false;
 /* Private payloads are immutable after load. Verify the whole family once
  * before the first original call each display frame, never repeated whole-payload scans. */
 if(goldwing_resources.frame_checked&&goldwing_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<3;i++) {
  Asset *a=&goldwing_resources.member[i];int w=goldwing_pins[i].size?24:12,h=goldwing_pins[i].size?28:14;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)goldwing_pins[i].base||
   a->w!=w||a->h!=h||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)w*h*8*8*4)!=goldwing_pins[i].rgba) {
   goldwing_resources.valid=false;return false;
  }
 }
 goldwing_resources.checked_tick=mirror_logic_tick;goldwing_resources.frame_checked=true;
 return true;
}
/* The current ordered call must belong to the original sky actor, not another
 * record sharing these shapes. No game field or timer is changed here. */
static bool goldwing_actor(Sprite2_array bank,unsigned base,int x,int y,int part,int filter,const G101EnemyContext *c)
{
 if(!c||c->type!=282||c->pool_slot>=25||c->availability!=0||c->size!=1||
  c->score_item||c->damaged||c->static_animation||!c->independent_motion)return false;
 const struct JE_SingleEnemyType *e=&enemy[c->pool_slot];
 if(enemyAvail[c->pool_slot]!=0||e->enemytype!=282||e->enemydatofs!=&enemyDat[282]||
  e->size!=1||e->scoreitem||e->edamaged||e->linknum!=40||e->enemydie!=535||
  !e->sprite2s||e->sprite2s->data!=bank.data||e->sprite2s->size!=bank.size||
  !e->armorleft||e->ani!=6||e->animin!=1||e->animax!=6||e->aniwhenfire!=2||
  e->enemycycle<1||e->enemycycle>6||e->filter!=filter)return false;
 if(!((e->aniactive==1&&e->enemycycle<6)||
  (e->aniactive==2&&(e->enemycycle==1||e->enemycycle==6))))return false;
 static const unsigned sequence[20]={79,81,83,81,81,79};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 if(base!=sequence[e->enemycycle-1]||e->tur[0]!=59||e->tur[1]||e->tur[2]||
  e->freq[0]!=50||e->freq[1]||e->freq[2]||e->launchfreq||e->launchtype||e->launchspecial||
  e->edgr||e->edlevel||e->edani||e->exc||e->eyc!=2||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel)return false;
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 return x-px==e->ex+e->mapoffset-6&&y-py==e->ey-7;
}
static bool goldwing_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||!goldwing_actor(bank,base,x,y,part,filter,c))return false;
 unsigned k=base==79?0:base==81?1:2;
 if(base!=goldwing_pins[k].base||c->size!=goldwing_pins[k].size||
  (c->size==0&&part!=0)||(c->size==1&&part!=0&&part!=1&&part!=19&&part!=20)||
  filter<0||filter>255)return false;
 if(!goldwing_source(bank)||!goldwing_family_ready()) {
  /* A dependency failure after an accepted quadrant rejects this entire frame.
   * Cold missing art stays an ordinary local classic fallback. */
  if(goldwing_resources.drew&&goldwing_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("goldwing-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 bool mirrored=draw_asset_filtered(x-px,y-py,&goldwing_resources.member[k],MIRROR_NORMAL,
  c->size?&quadrant:NULL,(Uint8)filter,NULL,NULL,NULL);
 if(mirrored){goldwing_resources.drew=true;goldwing_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
