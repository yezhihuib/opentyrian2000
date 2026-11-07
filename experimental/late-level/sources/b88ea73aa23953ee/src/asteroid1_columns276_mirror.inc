/* SPDX-License-Identifier: GPL-2.0-or-later
 * Scheduled record276: one six-state three-column sequence in bank23/NEWSHS.
 * Original allocation, ordered quadrants, animation, scrolling, damage,
 * clipping, effects and RNG remain authoritative. No gameplay writes here.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
static const struct {unsigned type;uint64_t record;} columns276_pins[1]={
 {276,UINT64_C(0x5ef5beadaa8fd4df)},
};
/* Reviewed authored192x224 RGBA payloads share one registered housing
 * outside the original source-difference union. The original sequence,
 * rather than numeric image order, selects one of the six body states. */
static const struct {unsigned base,size;uint64_t rgba;} columns276_images[6]={
 {191,1,UINT64_C(0xb69c4a8ec6643b32)},
 {193,1,UINT64_C(0x733140ca91947918)},
 {195,1,UINT64_C(0xd943c48b354d2346)},
 {197,1,UINT64_C(0xb9eccb9750b19435)},
 {199,1,UINT64_C(0x0da564da8ec607ac)},
 {201,1,UINT64_C(0x495b36de8b07fad2)},
};
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[6];} columns276_resources;
static void columns276_shutdown(void)
{
 for(unsigned i=0;i<6;i++)free(columns276_resources.member[i].rgba);
 memset(&columns276_resources,0,sizeof(columns276_resources));
 columns276_draw_lease=NULL;
 /* firing325_shutdown owns revocation of the shared NEWSHS byte snapshot. */
}
/* Share only immutable NEWSHS bank-byte trust, never firing325's record pin.
 * Check all46566 current bytes and this independent77-byte record every call. */
static bool columns276_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=46566)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==23&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!firing325_source_bytes_match(bank.data,bank.size))return false;
 return asteroid1_record_stamp(columns276_pins[0].type)==columns276_pins[0].record;
}
static bool columns276_load(unsigned k)
{
 Asset *a=&columns276_resources.member[k];
 const unsigned w=24,h=28;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshs-%u-8.hda",columns276_resources.root,columns276_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1_COLUMNS276*10000+columns276_images[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==columns276_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1_COLUMNS276,(int)columns276_images[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* All six138 resources preflight before any original quadrant is replaced.
 * Missing/corrupt/foreign identities fail only this family, sticky until the
 * selected-root renderer cache resets. Other banks and old325 stay separate. */
static bool columns276_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(columns276_resources.root))return false;
 if(!columns276_resources.checked) {
  columns276_resources.checked=true;columns276_resources.valid=true;
  memcpy(columns276_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<6;i++)if(!columns276_load(i))columns276_resources.valid=false;
 }
 if(!columns276_resources.valid||strcmp(columns276_resources.root,game_probe_assets))return false;
 /* Private immutable payloads are checked as a family before the first
  * original callback each display frame; source bytes stay every-call. */
 if(columns276_resources.frame_checked&&columns276_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<6;i++) {
  Asset *a=&columns276_resources.member[i];
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_COLUMNS276||a->index!=(int)columns276_images[i].base||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)24*28*8*8*4)!=columns276_images[i].rgba) {
   columns276_resources.valid=false;return false;
  }
 }
 columns276_resources.checked_tick=mirror_logic_tick;columns276_resources.frame_checked=true;
 return true;
}
/* Original event6 at5676 and6040 allocates one actor each in pool25..49.
 * Check the live
 * original actor as well as its context. Positive difficulty-scaled/hit-reduced
 * armor, ice, inactive countdowns and backscroll remain simulation-owned. */
static bool columns276_actor(Sprite2_array bank,unsigned base,int x,int y,int part,int filter,const G101EnemyContext *c)
{
 if(!c||c->type!=276||c->pool_slot<25||c->pool_slot>=50||
  c->availability!=0||c->size!=1||c->score_item||c->damaged||c->independent_motion||
  c->static_animation)return false;
 const struct JE_SingleEnemyType *e=&enemy[c->pool_slot];
 /* Original construction binds the loaded slot object, not an alias copy. */
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==23&&e->sprite2s==&enemySpriteSheets[i]&&
  bank.data==enemySpriteSheets[i].data&&bank.size==enemySpriteSheets[i].size)bound=true;
 if(!bound)return false;
 if(enemyAvail[c->pool_slot]!=0||e->enemytype!=276||e->enemydatofs!=&enemyDat[276]||
  e->size!=1||e->scoreitem||e->special||e->edamaged||!e->armorleft||e->evalue||e->linknum||e->enemydie||
  !e->sprite2s||e->sprite2s->data!=bank.data||e->sprite2s->size!=bank.size||
  e->ani!=18||e->animin!=1||e->animax||e->aniwhenfire||e->aniactive!=1||
  e->enemycycle<1||e->enemycycle>18||e->filter!=filter||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=2||
  e->tur[0]||e->tur[1]||e->tur[2]||e->freq[0]||e->freq[1]||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 static const unsigned sequence[20]={191,191,193,193,191,191,195,195,197,197,195,195,199,199,201,201,199,199,0,0};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 if(base!=sequence[e->enemycycle-1]||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 /* Preserve the original side and independent top/bottom-row guards. */
 if(e->ex+e->mapoffset<=-29||e->ex+e->mapoffset>=300||
  (!py&&e->ey<=-13)||(py&&(e->ey<=-26||e->ey>=182)))return false;
 return x-px==e->ex+e->mapoffset-6&&y-py==e->ey-7;
}
static bool columns276_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||filter<0||filter>255||!columns276_actor(bank,base,x,y,part,filter,c))return false;
 unsigned k=0;
 while(k<6&&base!=columns276_images[k].base)++k;
 if(k==6||c->size!=columns276_images[k].size)return false;
 if(!columns276_source(bank)||!columns276_family_ready()) {
  /* Cold fallback stays local. Losing a dependency after an accepted quadrant
   * rejects this whole HD frame, preserving ordered composition. */
  if(columns276_resources.drew&&columns276_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("columns276-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 columns276_draw_lease=&columns276_resources.member[k];
 bool mirrored=draw_asset_filtered(x-px,y-py,&columns276_resources.member[k],MIRROR_NORMAL,
  &quadrant,(Uint8)filter,NULL,NULL,NULL);
 columns276_draw_lease=NULL;
 if(mirrored){columns276_resources.drew=true;columns276_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1_COLUMNS276,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
