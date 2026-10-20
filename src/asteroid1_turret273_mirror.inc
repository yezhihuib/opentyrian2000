/* SPDX-License-Identifier: GPL-2.0-or-later
 * Scheduled record273: one nine-state animated firing turret in bank8/NEWSHD.
 * Original allocation, ordered quadrants, animation, scrolling, firing, damage,
 * clipping, effects and RNG remain authoritative. No gameplay writes here.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
static const struct {unsigned type;uint64_t record;} turret273_pins[1]={
 {273,UINT64_C(0xb66d58070227fe5a)},
};
/* Reviewed authored192x224 RGBA payloads share one registered housing
 * outside the original source-difference union. The original sequence,
 * rather than numeric image order, selects one of the nine body states. */
static const struct {unsigned base,size;uint64_t rgba;} turret273_images[9]={
 {169,1,UINT64_C(0x720d9cb016ec3e28)},
 {193,1,UINT64_C(0x2fb39062bb5c24de)},
 {195,1,UINT64_C(0x12253fe34772120e)},
 {197,1,UINT64_C(0x2bd687dd8f338d13)},
 {199,1,UINT64_C(0x8fa96ea4a676eaff)},
 {201,1,UINT64_C(0x714aea6bafce7767)},
 {203,1,UINT64_C(0x18504d943759cf36)},
 {205,1,UINT64_C(0x71ab31514ca997e5)},
 {207,1,UINT64_C(0xa31588c2dd1afc84)},
};
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[9];} turret273_resources;
static void turret273_shutdown(void)
{
 for(unsigned i=0;i<9;i++)free(turret273_resources.member[i].rgba);
 memset(&turret273_resources,0,sizeof(turret273_resources));
 turret273_draw_lease=NULL;
 /* asteroid1_shutdown owns revocation of the shared NEWSHD byte snapshot. */
}
/* Authenticate all 80 serialized original weapon144 bytes without padding.
 * This is a body admission dependency, never a projectile binding or a write.
 * Original multi=5/max=5 emits the five active selector304 entries unchanged. */
static uint64_t turret273_weapon_stamp(void)
{
 const JE_WeaponType *w=&weapons[144];Uint8 b[80];size_t n=0;
#define T273_BYTE(v) do{b[n++]=(Uint8)(v);}while(0)
#define T273_WORD(v) do{unsigned word_=(unsigned)(v);T273_BYTE(word_);T273_BYTE(word_>>8);}while(0)
 T273_WORD(w->drain);T273_BYTE(w->shotrepeat);T273_BYTE(w->multi);T273_WORD(w->weapani);
 T273_BYTE(w->max);T273_BYTE(w->tx);T273_BYTE(w->ty);T273_BYTE(w->aim);
 for(unsigned i=0;i<8;i++)T273_BYTE(w->attack[i]);
 for(unsigned i=0;i<8;i++)T273_BYTE(w->del[i]);
 for(unsigned i=0;i<8;i++)T273_BYTE(w->sx[i]);
 for(unsigned i=0;i<8;i++)T273_BYTE(w->sy[i]);
 for(unsigned i=0;i<8;i++)T273_BYTE(w->bx[i]);
 for(unsigned i=0;i<8;i++)T273_BYTE(w->by[i]);
 for(unsigned i=0;i<8;i++)T273_WORD(w->sg[i]);
 T273_BYTE(w->acceleration);T273_BYTE(w->accelerationx);T273_BYTE(w->circlesize);
 T273_BYTE(w->sound);T273_BYTE(w->trail);T273_BYTE(w->shipblastfilter);
#undef T273_WORD
#undef T273_BYTE
 return n==sizeof(b)?asteroid1_stamp(b,sizeof(b)):0;
}
/* Share only immutable NEWSHD bank-byte trust, never another family's record pin.
 * Check all42012 current bytes and this independent77-byte record every call. */
static bool turret273_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=42012)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!asteroid1_source_bytes_match(bank.data,bank.size))return false;
 return asteroid1_record_stamp(turret273_pins[0].type)==turret273_pins[0].record&&
  turret273_weapon_stamp()==UINT64_C(0xb054c3b3b09a2a5b);
}
static bool turret273_load(unsigned k)
{
 Asset *a=&turret273_resources.member[k];
 const unsigned w=24,h=28;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshd-%u-8.hda",turret273_resources.root,turret273_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1_TURRET273*10000+turret273_images[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==turret273_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1_TURRET273,(int)turret273_images[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* All nine139 resources preflight before any original quadrant is replaced.
 * Missing/corrupt/foreign identities fail only this family, sticky until the
 * selected-root renderer cache resets. Other banks and old325 stay separate. */
static bool turret273_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(turret273_resources.root))return false;
 if(!turret273_resources.checked) {
  turret273_resources.checked=true;turret273_resources.valid=true;
  memcpy(turret273_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<9;i++)if(!turret273_load(i))turret273_resources.valid=false;
 }
 if(!turret273_resources.valid||strcmp(turret273_resources.root,game_probe_assets))return false;
 /* Private immutable payloads are checked as a family before the first
  * original callback each display frame; source bytes stay every-call. */
 if(turret273_resources.frame_checked&&turret273_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<9;i++) {
  Asset *a=&turret273_resources.member[i];
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_TURRET273||a->index!=(int)turret273_images[i].base||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)24*28*8*8*4)!=turret273_images[i].rgba) {
   turret273_resources.valid=false;return false;
  }
 }
 turret273_resources.checked_tick=mirror_logic_tick;turret273_resources.frame_checked=true;
 return true;
}
/* Five original event6 allocations at3576,3632,3996(two),7244 use pool25..49.
 * The continuous20-cycle animation is independent of weapon144 firing.
 * Armor, ice, current shot countdowns/multiposition, and backscroll remain
 * simulation-owned. No renderer state is written into original actors. */
static bool turret273_actor(Sprite2_array bank,unsigned base,int x,int y,int part,int filter,const G101EnemyContext *c)
{
 if(!c||c->type!=273||c->pool_slot<25||c->pool_slot>=50||
  c->availability!=0||c->size!=1||c->score_item||c->damaged||c->independent_motion||
  c->static_animation)return false;
 const struct JE_SingleEnemyType *e=&enemy[c->pool_slot];
 /* Original construction binds the loaded slot object, not an alias copy. */
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&e->sprite2s==&enemySpriteSheets[i]&&
  bank.data==enemySpriteSheets[i].data&&bank.size==enemySpriteSheets[i].size)bound=true;
 if(!bound)return false;
 if(enemyAvail[c->pool_slot]!=0||e->enemytype!=273||e->enemydatofs!=&enemyDat[273]||
  e->size!=1||e->scoreitem||e->special||e->edamaged||!e->armorleft||e->evalue||e->linknum||e->enemydie||
  !e->sprite2s||e->sprite2s->data!=bank.data||e->sprite2s->size!=bank.size||
  e->ani!=20||e->animin!=1||e->animax||e->aniwhenfire||e->aniactive!=1||
  e->enemycycle<1||e->enemycycle>20||e->filter!=filter||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=2||
  e->tur[0]!=144||e->tur[1]||e->tur[2]||e->freq[0]!=20||e->freq[1]||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 static const unsigned sequence[20]={193,195,197,199,201,203,205,207,169,207,205,203,201,199,197,195,193,193,193,193};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 if(base!=sequence[e->enemycycle-1]||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 /* Preserve the original side and independent top/bottom-row guards. */
 if(e->ex+e->mapoffset<=-29||e->ex+e->mapoffset>=300||
  (!py&&e->ey<=-13)||(py&&(e->ey<=-26||e->ey>=182)))return false;
 return x-px==e->ex+e->mapoffset-6&&y-py==e->ey-7;
}
static bool turret273_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||filter<0||filter>255||!turret273_actor(bank,base,x,y,part,filter,c))return false;
 unsigned k=0;
 while(k<9&&base!=turret273_images[k].base)++k;
 if(k==9||c->size!=turret273_images[k].size)return false;
 if(!turret273_source(bank)||!turret273_family_ready()) {
  /* Cold fallback stays local. Losing a dependency after an accepted quadrant
   * rejects this whole HD frame, preserving ordered composition. */
  if(turret273_resources.drew&&turret273_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("turret273-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 turret273_draw_lease=&turret273_resources.member[k];
 bool mirrored=draw_asset_filtered(x-px,y-py,&turret273_resources.member[k],MIRROR_NORMAL,
  &quadrant,(Uint8)filter,NULL,NULL,NULL);
 turret273_draw_lease=NULL;
 if(mirrored){turret273_resources.drew=true;turret273_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1_TURRET273,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
