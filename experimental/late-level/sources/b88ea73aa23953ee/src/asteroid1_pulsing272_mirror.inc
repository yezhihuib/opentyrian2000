/* SPDX-License-Identifier: GPL-2.0-or-later
 * Scheduled record272: one four-state continuous pulse in bank23/NEWSHS.
 * Original allocation, ordered quadrants, animation, scrolling, damage,
 * clipping, effects and RNG remain authoritative. No gameplay writes here.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
static const struct {unsigned type;uint64_t record;} pulsing272_pins[1]={
 {272,UINT64_C(0x2f2c9491d2030153)},
};
/* Reviewed imagegen-authored192x224 RGBA payloads. One registered housing
 * is common outside the original288-cell source-difference union. The original
 * sequence, rather than numeric image order, selects each state. */
static const struct {unsigned base,size;uint64_t rgba;} pulsing272_images[4]={
 {229,1,UINT64_C(0x380d60ca088b66cb)},
 {231,1,UINT64_C(0xa93168621d007ae5)},
 {233,1,UINT64_C(0xfd9c43c2ba04eef7)},
 {235,1,UINT64_C(0x9301528dceb12189)},
};
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[4];} pulsing272_resources;
static void pulsing272_shutdown(void)
{
 for(unsigned i=0;i<4;i++)free(pulsing272_resources.member[i].rgba);
 memset(&pulsing272_resources,0,sizeof(pulsing272_resources));
 pulsing272_draw_lease=NULL;
 /* firing325_shutdown owns revocation of the shared NEWSHS byte snapshot. */
}
/* Share only immutable NEWSHS bank-byte trust, never firing325's record pin.
 * Check all46566 current bytes and this independent77-byte record every call. */
static bool pulsing272_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=46566)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==23&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!firing325_source_bytes_match(bank.data,bank.size))return false;
 return asteroid1_record_stamp(pulsing272_pins[0].type)==pulsing272_pins[0].record;
}
static bool pulsing272_load(unsigned k)
{
 Asset *a=&pulsing272_resources.member[k];
 const unsigned w=24,h=28;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshs-%u-8.hda",pulsing272_resources.root,pulsing272_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1_NEWSHS*10000+pulsing272_images[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==pulsing272_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1_NEWSHS,(int)pulsing272_images[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* All four136 resources preflight before any original quadrant is replaced.
 * Missing/corrupt/foreign identities fail only this family, sticky until the
 * selected-root renderer cache resets. Other banks and old325 stay separate. */
static bool pulsing272_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(pulsing272_resources.root))return false;
 if(!pulsing272_resources.checked) {
  pulsing272_resources.checked=true;pulsing272_resources.valid=true;
  memcpy(pulsing272_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<4;i++)if(!pulsing272_load(i))pulsing272_resources.valid=false;
 }
 if(!pulsing272_resources.valid||strcmp(pulsing272_resources.root,game_probe_assets))return false;
 /* Private immutable payloads are checked as a family before the first
  * original callback each display frame; source bytes stay every-call. */
 if(pulsing272_resources.frame_checked&&pulsing272_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<4;i++) {
  Asset *a=&pulsing272_resources.member[i];
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_NEWSHS||a->index!=(int)pulsing272_images[i].base||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)24*28*8*8*4)!=pulsing272_images[i].rgba) {
   pulsing272_resources.valid=false;return false;
  }
 }
 pulsing272_resources.checked_tick=mirror_logic_tick;pulsing272_resources.frame_checked=true;
 return true;
}
/* Event6 allocates each actor independently in pool25..49. Check the live
 * original actor as well as its context. Positive difficulty-scaled/hit-reduced
 * armor, ice, inactive countdowns and backscroll remain simulation-owned. */
static bool pulsing272_actor(Sprite2_array bank,unsigned base,int x,int y,int part,int filter,const G101EnemyContext *c)
{
 if(!c||c->type!=272||c->pool_slot<25||c->pool_slot>=50||
  c->availability!=0||c->size!=1||c->score_item||c->damaged||c->independent_motion||
  c->static_animation)return false;
 const struct JE_SingleEnemyType *e=&enemy[c->pool_slot];
 /* Original construction binds the loaded slot object, not an alias copy. */
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==23&&e->sprite2s==&enemySpriteSheets[i]&&
  bank.data==enemySpriteSheets[i].data&&bank.size==enemySpriteSheets[i].size)bound=true;
 if(!bound)return false;
 if(enemyAvail[c->pool_slot]!=0||e->enemytype!=272||e->enemydatofs!=&enemyDat[272]||
  e->size!=1||e->scoreitem||e->special||e->edamaged||!e->armorleft||e->evalue||e->linknum||e->enemydie||
  !e->sprite2s||e->sprite2s->data!=bank.data||e->sprite2s->size!=bank.size||
  e->ani!=18||e->animin!=1||e->animax||e->aniwhenfire||e->aniactive!=1||
  e->enemycycle<1||e->enemycycle>18||e->filter!=filter||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=2||
  e->tur[0]||e->tur[1]||e->tur[2]||e->freq[0]||e->freq[1]||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 static const unsigned sequence[20]={229,229,229,233,233,233,235,235,235,233,233,233,231,231,231,229,229,229,0,0};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 if(base!=sequence[e->enemycycle-1]||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 /* Preserve the original side and independent top/bottom-row guards. */
 if(e->ex+e->mapoffset<=-29||e->ex+e->mapoffset>=300||
  (!py&&e->ey<=-13)||(py&&(e->ey<=-26||e->ey>=182)))return false;
 return x-px==e->ex+e->mapoffset-6&&y-py==e->ey-7;
}
static bool pulsing272_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||filter<0||filter>255||!pulsing272_actor(bank,base,x,y,part,filter,c))return false;
 unsigned k=0;
 while(k<4&&base!=pulsing272_images[k].base)++k;
 if(k==4||c->size!=pulsing272_images[k].size)return false;
 if(!pulsing272_source(bank)||!pulsing272_family_ready()) {
  /* Cold fallback stays local. Losing a dependency after an accepted quadrant
   * rejects this whole HD frame, preserving ordered composition. */
  if(pulsing272_resources.drew&&pulsing272_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("pulsing272-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 pulsing272_draw_lease=&pulsing272_resources.member[k];
 bool mirrored=draw_asset_filtered(x-px,y-py,&pulsing272_resources.member[k],MIRROR_NORMAL,
  &quadrant,(Uint8)filter,NULL,NULL,NULL);
 pulsing272_draw_lease=NULL;
 if(mirrored){pulsing272_resources.drew=true;pulsing272_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1_NEWSHS,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
