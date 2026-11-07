/* SPDX-License-Identifier: GPL-2.0-or-later
 * Scheduled record270: one three-state firing-triggered housing in bank8/NEWSHD.
 * Original allocation, ordered quadrants, animation, scrolling, firing, damage,
 * clipping, effects and RNG remain authoritative. No gameplay writes here.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
static const struct {unsigned type;uint64_t record;} firing270_pins[1]={
 {270,UINT64_C(0xeac063d6afea8edd)},
};
/* Three reviewed complete192x224 RGBA images; the six original cycles,
 * including repeated source127/129 entries, select the registered state. */
static const struct {unsigned base,size;uint64_t rgba;} firing270_images[3]={
 {127,1,UINT64_C(0x0a2074eb9f33bbd3)},
 {129,1,UINT64_C(0xf4b08c9c6c51bd06)},
 {131,1,UINT64_C(0x2eb71f422ec16550)},
};
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[3];} firing270_resources;
static void firing270_shutdown(void)
{
 for(unsigned i=0;i<3;i++)free(firing270_resources.member[i].rgba);
 memset(&firing270_resources,0,sizeof(firing270_resources));
 firing270_draw_lease=NULL;
 /* asteroid1_shutdown owns revocation of the shared NEWSHD byte snapshot. */
}
/* Authenticate both complete80-byte original weapons, including inactive
 * serialized fields, without struct padding. Body admission never mutates a
 * timer, aim, shot selector or source112/113 projectile. */
static uint64_t firing270_weapon_stamp(unsigned weapon)
{
 const JE_WeaponType *w=&weapons[weapon];Uint8 b[80];size_t n=0;
#define F270_BYTE(v) do{b[n++]=(Uint8)(v);}while(0)
#define F270_WORD(v) do{unsigned word_=(unsigned)(v);F270_BYTE(word_);F270_BYTE(word_>>8);}while(0)
 F270_WORD(w->drain);F270_BYTE(w->shotrepeat);F270_BYTE(w->multi);F270_WORD(w->weapani);
 F270_BYTE(w->max);F270_BYTE(w->tx);F270_BYTE(w->ty);F270_BYTE(w->aim);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->attack[i]);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->del[i]);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->sx[i]);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->sy[i]);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->bx[i]);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->by[i]);
 for(unsigned i=0;i<8;i++)F270_WORD(w->sg[i]);
 F270_BYTE(w->acceleration);F270_BYTE(w->accelerationx);F270_BYTE(w->circlesize);
 F270_BYTE(w->sound);F270_BYTE(w->trail);F270_BYTE(w->shipblastfilter);
#undef F270_WORD
#undef F270_BYTE
 return n==sizeof(b)?asteroid1_stamp(b,sizeof(b)):0;
}
/* Share only immutable NEWSHD bank-byte trust, never another family's record pin.
 * Check all42012 current bytes and this independent77-byte record every call. */
static bool firing270_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=42012)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!asteroid1_source_bytes_match(bank.data,bank.size))return false;
 return asteroid1_record_stamp(firing270_pins[0].type)==firing270_pins[0].record&&
  firing270_weapon_stamp(145)==UINT64_C(0x387b219ee9cab017)&&
  firing270_weapon_stamp(146)==UINT64_C(0x4623a676db5268a8);
}
static bool firing270_load(unsigned k)
{
 Asset *a=&firing270_resources.member[k];
 const unsigned w=24,h=28;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshd-%u-8.hda",firing270_resources.root,firing270_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1_FIRING270*10000+firing270_images[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==firing270_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1_FIRING270,(int)firing270_images[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* All three141 resources preflight before any original quadrant is replaced.
 * Missing/corrupt/foreign identities fail only this family, sticky until the
 * selected-root renderer cache resets. Other records and projectile roles stay separate. */
static bool firing270_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(firing270_resources.root))return false;
 if(!firing270_resources.checked) {
  firing270_resources.checked=true;firing270_resources.valid=true;
  memcpy(firing270_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<3;i++)if(!firing270_load(i))firing270_resources.valid=false;
 }
 if(!firing270_resources.valid||strcmp(firing270_resources.root,game_probe_assets))return false;
 /* Private immutable payloads are checked as a family before the first
  * original callback each display frame; source bytes stay every-call. */
 if(firing270_resources.frame_checked&&firing270_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<3;i++) {
  Asset *a=&firing270_resources.member[i];
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_FIRING270||a->index!=(int)firing270_images[i].base||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)24*28*8*8*4)!=firing270_images[i].rgba) {
   firing270_resources.valid=false;return false;
  }
 }
 firing270_resources.checked_tick=mirror_logic_tick;firing270_resources.frame_checked=true;
 return true;
}
/* The one event6 at6320 allocates in pool25..49. Animate2 starts on cycle1
 * idle2. A successful original shot allocation arms active1 AFTER rendering;
 * the next draw advances, stops at cycle6/idle2, then wraps to1 only following
 * another successful shot. Ice and full shot pools must retain engine behavior.
 * Accept only callback-reachable animation states, never synthetic idle poses.
 * Armor, ice, current countdowns/multiposition and backscroll stay engine-owned. */
static bool firing270_actor(Sprite2_array bank,unsigned base,int x,int y,int part,int filter,const G101EnemyContext *c)
{
 if(!c||c->type!=270||c->pool_slot<25||c->pool_slot>=50||
  c->availability!=0||c->size!=1||c->score_item||c->damaged||c->independent_motion||
  c->static_animation)return false;
 const struct JE_SingleEnemyType *e=&enemy[c->pool_slot];
 /* Original construction binds the loaded slot object, not an alias copy. */
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&e->sprite2s==&enemySpriteSheets[i]&&
  bank.data==enemySpriteSheets[i].data&&bank.size==enemySpriteSheets[i].size)bound=true;
 if(!bound)return false;
 if(enemyAvail[c->pool_slot]!=0||e->enemytype!=270||e->enemydatofs!=&enemyDat[270]||
  e->size!=1||e->scoreitem||e->special||e->edamaged||!e->armorleft||e->evalue||e->linknum||e->enemydie||
  !e->sprite2s||e->sprite2s->data!=bank.data||e->sprite2s->size!=bank.size||
  e->ani!=6||e->animin!=1||e->animax!=6||e->aniwhenfire!=2||
  !((e->aniactive==1&&e->enemycycle>=1&&e->enemycycle<6)||
    (e->aniactive==2&&(e->enemycycle==1||e->enemycycle==6)))||e->filter!=filter||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=2||
  e->tur[0]!=145||e->tur[1]!=146||e->tur[2]||e->freq[0]!=40||e->freq[1]!=41||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 static const unsigned sequence[20]={127,129,131,129,129,127,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 if(base!=sequence[e->enemycycle-1]||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 /* Preserve the original side and independent top/bottom-row guards. */
 if(e->ex+e->mapoffset<=-29||e->ex+e->mapoffset>=300||
  (!py&&e->ey<=-13)||(py&&(e->ey<=-26||e->ey>=182)))return false;
 return x-px==e->ex+e->mapoffset-6&&y-py==e->ey-7;
}
static bool firing270_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||filter<0||filter>255||!firing270_actor(bank,base,x,y,part,filter,c))return false;
 unsigned k=0;
 while(k<3&&base!=firing270_images[k].base)++k;
 if(k==3||c->size!=firing270_images[k].size)return false;
 if(!firing270_source(bank)||!firing270_family_ready()) {
  /* Cold fallback stays local. Losing a dependency after an accepted quadrant
   * rejects this whole HD frame, preserving ordered composition. */
  if(firing270_resources.drew&&firing270_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("firing270-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 firing270_draw_lease=&firing270_resources.member[k];
 bool mirrored=draw_asset_filtered(x-px,y-py,&firing270_resources.member[k],MIRROR_NORMAL,
  &quadrant,(Uint8)filter,NULL,NULL,NULL);
 firing270_draw_lease=NULL;
 if(mirrored){firing270_resources.drew=true;firing270_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1_FIRING270,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
