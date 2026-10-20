/* SPDX-License-Identifier: GPL-2.0-or-later
 * Scheduled installation records287/288: separate original allocations and
 * quadrant calls, with one coherent three-image family. Scrolling, animation,
 * clipping, RNG and linked destruction remain authoritative.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
/* Both record dependencies are mandatory even for an unpaired live actor. */
static const struct {unsigned type;uint64_t record;} paired287_288_pins[2]={
 {287,UINT64_C(0x7b520ef86aceb758)},
 {288,UINT64_C(0x0ca4ab6a0bd64091)},
};
/* Resource payload pins are filled from the reviewed generated art. */
static const struct {unsigned base,size;uint64_t rgba;} paired287_288_images[3]={
 {245,1,UINT64_C(0x3edfa524d0735809)},
 {281,1,UINT64_C(0x5255797c80e9952b)},
 {283,1,UINT64_C(0xe24410be52075d07)},
};
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[3];} paired287_288_resources;
static void paired287_288_shutdown(void)
{
 for(unsigned i=0;i<3;i++)free(paired287_288_resources.member[i].rgba);
 memset(&paired287_288_resources,0,sizeof(paired287_288_resources));
}
/* Current bytes are checked on every draw, including warm/address-reused banks.
 * Both full serialized records are pinned independently of actor presence. */
static bool paired287_288_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=42012)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!asteroid1_source_bytes_match(bank.data,bank.size))return false;
 for(unsigned i=0;i<2;i++)
  if(asteroid1_record_stamp(paired287_288_pins[i].type)!=paired287_288_pins[i].record)return false;
 return true;
}
static bool paired287_288_load(unsigned k)
{
 Asset *a=&paired287_288_resources.member[k];
 unsigned w=paired287_288_images[k].size?24:12,h=paired287_288_images[k].size?28:14;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshd-%u-8.hda",paired287_288_resources.root,paired287_288_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1*10000+paired287_288_images[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==paired287_288_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1,(int)paired287_288_images[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* Coherent preflight and sticky failure for this selected-root cache lifetime.
 * Density4 and missing/corrupt/foreign-role resources never get partial HD. */
static bool paired287_288_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(paired287_288_resources.root))return false;
 if(!paired287_288_resources.checked) {
  paired287_288_resources.checked=true;paired287_288_resources.valid=true;
  memcpy(paired287_288_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<3;i++)if(!paired287_288_load(i))paired287_288_resources.valid=false;
 }
 if(!paired287_288_resources.valid||strcmp(paired287_288_resources.root,game_probe_assets))return false;
 /* Private payloads are immutable after load. Verify the whole family once
  * before the first original call each display frame, never 12 full scans. */
 if(paired287_288_resources.frame_checked&&paired287_288_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<3;i++) {
  Asset *a=&paired287_288_resources.member[i];int w=paired287_288_images[i].size?24:12,h=paired287_288_images[i].size?28:14;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)paired287_288_images[i].base||
   a->w!=w||a->h!=h||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)w*h*8*8*4)!=paired287_288_images[i].rgba) {
   paired287_288_resources.valid=false;return false;
  }
 }
 paired287_288_resources.checked_tick=mirror_logic_tick;paired287_288_resources.frame_checked=true;
 return true;
}
/* Original event6 pool25-49, seven exact links, and no intrinsic motion.
 * No partner lookup: allocation, clipping and culling are per original actor.
 * Current armor/value and ice state remain simulation-authoritative. */
static bool paired287_288_actor(Sprite2_array bank,unsigned base,int x,int y,int part,int filter,const G101EnemyContext *c)
{
 if(!c||(c->type!=287&&c->type!=288)||c->pool_slot<25||c->pool_slot>=50||
  c->availability!=0||c->size!=1||c->score_item||c->damaged||c->independent_motion||
  c->static_animation!=(c->type==287))return false;
 const struct JE_SingleEnemyType *e=&enemy[c->pool_slot];
 if(enemyAvail[c->pool_slot]!=0||e->enemytype!=c->type||e->enemydatofs!=&enemyDat[c->type]||
  e->size!=1||e->scoreitem||e->edamaged||!e->armorleft||e->enemydie||
  !e->sprite2s||e->sprite2s->data!=bank.data||e->sprite2s->size!=bank.size||
  e->animin!=1||e->animax||e->aniwhenfire||e->filter!=filter||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=13)return false;
 switch(e->linknum) {
 case 24:case 25:case 28:case 30:case 31:case 34:case 35:break;
 default:return false;
 }
 static const unsigned lower[20]={283,283,283,283,283,283,281,283,283,281,
  283,283,283,283,283,283,283,283,283,283};
 if(c->type==287) {
  if(e->ani!=1||e->enemycycle!=1||e->aniactive||base!=245)return false;
  for(unsigned i=0;i<20;i++)if(e->egr[i]!=(i?0:245))return false;
 } else {
  if(e->ani!=20||e->enemycycle<1||e->enemycycle>20||e->aniactive!=1)return false;
  for(unsigned i=0;i<20;i++)if(e->egr[i]!=lower[i])return false;
  if(base!=lower[e->enemycycle-1])return false;
 }
 if(e->tur[0]||e->tur[1]||e->tur[2]||e->freq[0]||e->freq[1]||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 return x-px==e->ex+e->mapoffset-6&&y-py==e->ey-7;
}
static bool paired287_288_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||!paired287_288_actor(bank,base,x,y,part,filter,c))return false;
 unsigned k=base==245?0:base==281?1:2;
 if(base!=paired287_288_images[k].base||c->size!=paired287_288_images[k].size||
  (c->size==0&&part!=0)||(c->size==1&&part!=0&&part!=1&&part!=19&&part!=20)||
  filter<0||filter>255)return false;
 if(!paired287_288_source(bank)||!paired287_288_family_ready()) {
  /* A dependency failure after an accepted quadrant rejects this entire frame.
   * Cold missing art stays an ordinary local classic fallback. */
  if(paired287_288_resources.drew&&paired287_288_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("paired287_288-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 bool mirrored=draw_asset_filtered(x-px,y-py,&paired287_288_resources.member[k],MIRROR_NORMAL,
  c->size?&quadrant:NULL,(Uint8)filter,NULL,NULL,NULL);
 if(mirrored){paired287_288_resources.drew=true;paired287_288_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
