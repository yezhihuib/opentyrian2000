/* SPDX-License-Identifier: GPL-2.0-or-later
 * Scheduled record285: one three-state firing-triggered housing in bank8/NEWSHD.
 * Original allocation, ordered quadrants, animation, scrolling, firing, damage,
 * clipping, effects and RNG remain authoritative. No gameplay writes here.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
static const struct {unsigned type;uint64_t record;} firing285_pins[1]={
 {285,UINT64_C(0x7329f43eb20aa601)},
};
/* Three reviewed complete192x224 RGBA images; the eight original cycles,
 * including repeated source157/159/161 entries, select the registered state. */
static const struct {unsigned base,size;uint64_t rgba;} firing285_images[3]={
 {157,1,UINT64_C(0x0c58a2dafde6eb24)},
 {159,1,UINT64_C(0x1ae853dcfabf351f)},
 {161,1,UINT64_C(0x13b2b824bfb62dfe)},
};
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[3];} firing285_resources;
static void firing285_shutdown(void)
{
 for(unsigned i=0;i<3;i++)free(firing285_resources.member[i].rgba);
 memset(&firing285_resources,0,sizeof(firing285_resources));
 firing285_draw_lease=NULL;
 /* asteroid1_shutdown owns revocation of the shared NEWSHD byte snapshot. */
}
/* Authenticate the complete80-byte original weapon24, including inactive
 * serialized fields, without struct padding. Body admission never mutates a
 * timer, aim, shot selector or source91 projectile. */
static uint64_t firing285_weapon_stamp(unsigned weapon)
{
 const JE_WeaponType *w=&weapons[weapon];Uint8 b[80];size_t n=0;
#define F285_BYTE(v) do{b[n++]=(Uint8)(v);}while(0)
#define F285_WORD(v) do{unsigned word_=(unsigned)(v);F285_BYTE(word_);F285_BYTE(word_>>8);}while(0)
 F285_WORD(w->drain);F285_BYTE(w->shotrepeat);F285_BYTE(w->multi);F285_WORD(w->weapani);
 F285_BYTE(w->max);F285_BYTE(w->tx);F285_BYTE(w->ty);F285_BYTE(w->aim);
 for(unsigned i=0;i<8;i++)F285_BYTE(w->attack[i]);
 for(unsigned i=0;i<8;i++)F285_BYTE(w->del[i]);
 for(unsigned i=0;i<8;i++)F285_BYTE(w->sx[i]);
 for(unsigned i=0;i<8;i++)F285_BYTE(w->sy[i]);
 for(unsigned i=0;i<8;i++)F285_BYTE(w->bx[i]);
 for(unsigned i=0;i<8;i++)F285_BYTE(w->by[i]);
 for(unsigned i=0;i<8;i++)F285_WORD(w->sg[i]);
 F285_BYTE(w->acceleration);F285_BYTE(w->accelerationx);F285_BYTE(w->circlesize);
 F285_BYTE(w->sound);F285_BYTE(w->trail);F285_BYTE(w->shipblastfilter);
#undef F285_WORD
#undef F285_BYTE
 return n==sizeof(b)?asteroid1_stamp(b,sizeof(b)):0;
}
/* Share only immutable NEWSHD bank-byte trust, never another family's record pin.
 * Check all42012 current bytes and this independent77-byte record every call. */
static bool firing285_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=42012)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!asteroid1_source_bytes_match(bank.data,bank.size))return false;
 return asteroid1_record_stamp(firing285_pins[0].type)==firing285_pins[0].record&&
  firing285_weapon_stamp(24)==UINT64_C(0x04c6cf64e3602dab);
}
static bool firing285_load(unsigned k)
{
 Asset *a=&firing285_resources.member[k];
 const unsigned w=24,h=28;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshd-%u-8.hda",firing285_resources.root,firing285_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1_FIRING285*10000+firing285_images[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==firing285_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1_FIRING285,(int)firing285_images[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* All three143 resources preflight before any original quadrant is replaced.
 * Missing/corrupt/foreign identities fail only this family, sticky until the
 * selected-root renderer cache resets. Other records and projectile roles stay separate. */
static bool firing285_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(firing285_resources.root))return false;
 if(!firing285_resources.checked) {
  firing285_resources.checked=true;firing285_resources.valid=true;
  memcpy(firing285_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<3;i++)if(!firing285_load(i))firing285_resources.valid=false;
 }
 if(!firing285_resources.valid||strcmp(firing285_resources.root,game_probe_assets))return false;
 /* Private immutable payloads are checked as a family before the first
  * original callback each display frame; source bytes stay every-call. */
 if(firing285_resources.frame_checked&&firing285_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<3;i++) {
  Asset *a=&firing285_resources.member[i];
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_FIRING285||a->index!=(int)firing285_images[i].base||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)24*28*8*8*4)!=firing285_images[i].rgba) {
   firing285_resources.valid=false;return false;
  }
 }
 firing285_resources.checked_tick=mirror_logic_tick;firing285_resources.frame_checked=true;
 return true;
}
/* The three event6 sites at3000/4000/5000 allocate in pool25..49. Animate2 starts on cycle1
 * idle2. A successful original shot allocation arms active1 AFTER rendering;
 * the next draw advances, stops at cycle8/idle2, then wraps to1 only following
 * another successful shot. Ice and full shot pools must retain engine behavior.
 * Accept only callback-reachable animation states, never synthetic idle poses.
 * Event d3=-2 cancels original ymove2; event33 binds link1 to original
 * death/drop512. Arcade event45 remains excluded by normal-mode scope.
 * Difficulty-scaled value and armor, ice, current countdowns/multiposition and backscroll stay engine-owned. */
static bool firing285_actor(Sprite2_array bank,unsigned base,int x,int y,int part,int filter,const G101EnemyContext *c)
{
 if(!c||c->type!=285||c->pool_slot<25||c->pool_slot>=50||
  c->availability!=0||c->size!=1||c->score_item||c->damaged||c->independent_motion||
  c->static_animation)return false;
 const struct JE_SingleEnemyType *e=&enemy[c->pool_slot];
 /* Original construction binds the loaded slot object, not an alias copy. */
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&e->sprite2s==&enemySpriteSheets[i]&&
  bank.data==enemySpriteSheets[i].data&&bank.size==enemySpriteSheets[i].size)bound=true;
 if(!bound)return false;
 if(enemyAvail[c->pool_slot]!=0||e->enemytype!=285||e->enemydatofs!=&enemyDat[285]||
  e->size!=1||e->scoreitem||e->special||e->edamaged||!e->armorleft||e->linknum!=1||e->enemydie!=512||
  !e->sprite2s||e->sprite2s->data!=bank.data||e->sprite2s->size!=bank.size||
  e->ani!=8||e->animin!=1||e->animax!=8||e->aniwhenfire!=2||
  !((e->aniactive==1&&e->enemycycle>=1&&e->enemycycle<8)||
    (e->aniactive==2&&(e->enemycycle==1||e->enemycycle==8)))||e->filter!=filter||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||!e->enemyground||e->explonum!=3||
  e->tur[0]!=24||e->tur[1]||e->tur[2]||e->freq[0]!=40||e->freq[1]||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 static const unsigned sequence[20]={157,159,159,161,161,159,159,157,0,0,0,0,0,0,0,0,0,0,0,0};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 if(base!=sequence[e->enemycycle-1]||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 /* Preserve the original side and independent top/bottom-row guards. */
 if(e->ex+e->mapoffset<=-29||e->ex+e->mapoffset>=300||
  (!py&&e->ey<=-13)||(py&&(e->ey<=-26||e->ey>=182)))return false;
 return x-px==e->ex+e->mapoffset-6&&y-py==e->ey-7;
}
static bool firing285_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||filter<0||filter>255||!firing285_actor(bank,base,x,y,part,filter,c))return false;
 unsigned k=0;
 while(k<3&&base!=firing285_images[k].base)++k;
 if(k==3||c->size!=firing285_images[k].size)return false;
 if(!firing285_source(bank)||!firing285_family_ready()) {
  /* Cold fallback stays local. Losing a dependency after an accepted quadrant
   * rejects this whole HD frame, preserving ordered composition. */
  if(firing285_resources.drew&&firing285_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("firing285-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 firing285_draw_lease=&firing285_resources.member[k];
 bool mirrored=draw_asset_filtered(x-px,y-py,&firing285_resources.member[k],MIRROR_NORMAL,
  &quadrant,(Uint8)filter,NULL,NULL,NULL);
 firing285_draw_lease=NULL;
 if(mirrored){firing285_resources.drew=true;firing285_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1_FIRING285,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
