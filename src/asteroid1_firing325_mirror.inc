/* SPDX-License-Identifier: GPL-2.0-or-later
 * Scheduled record325: one three-state firing lamp in logical bank23/NEWSHS.
 * Original ordered quadrants, scrolling, firing-gated animation, shot emission,
 * clipping, RNG and unlinked destruction remain authoritative.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
/* The complete canonical source record is mandatory for every body state. */
static const struct {unsigned type;uint64_t record;} firing325_pins[1]={
 {325,UINT64_C(0x521b35b127dbdc53)},
};
/* One common industrial housing, selected only by the original firing cycle. */
static const struct {unsigned base,size;uint64_t rgba;} firing325_images[3]={
 {11,1,UINT64_C(0x88265ed397c18d7c)},
 {125,1,UINT64_C(0xec456f91753ce5b4)},
 {277,1,UINT64_C(0x698376c61e837dd6)},
};
/* NEWSHS is an independent trust boundary. Never alias or enlarge the shared
 * NEWSHD snapshot, and never reuse live-bank pointer identity as byte trust. */
static struct {bool valid;Uint8 bytes[46566];} firing325_source_snapshot;
static bool firing325_source_bytes_match(const Uint8 *p,size_t n)
{
 if(!p||n!=sizeof(firing325_source_snapshot.bytes))return false;
 if(!firing325_source_snapshot.valid) {
  /* Pin the renderer-owned copy before trusting the current source bytes. */
  memcpy(firing325_source_snapshot.bytes,p,n);
  firing325_source_snapshot.valid=asteroid1_stamp(firing325_source_snapshot.bytes,n)==UINT64_C(0xf22ec1295ced5d11);
 }
 /* The private reference stays immutable until renderer shutdown. Every call
  * compares all current bytes, including reload and same-address reuse. */
 return firing325_source_snapshot.valid&&!memcmp(p,firing325_source_snapshot.bytes,n);
}
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[3];} firing325_resources;
static void firing325_shutdown(void)
{
 /* Separate source trust is revoked at the same renderer epoch boundary. */
 firing325_source_snapshot.valid=false;
 for(unsigned i=0;i<3;i++)free(firing325_resources.member[i].rgba);
 memset(&firing325_resources,0,sizeof(firing325_resources));
}
/* Current bytes are checked on every draw, including warm/address-reused banks.
 * The full serialized record is pinned independently of the selected image. */
static bool firing325_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=46566)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==23&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!firing325_source_bytes_match(bank.data,bank.size))return false;
 for(unsigned i=0;i<1;i++)
  if(asteroid1_record_stamp(firing325_pins[i].type)!=firing325_pins[i].record)return false;
 return true;
}
static bool firing325_load(unsigned k)
{
 Asset *a=&firing325_resources.member[k];
 unsigned w=firing325_images[k].size?24:12,h=firing325_images[k].size?28:14;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshs-%u-8.hda",firing325_resources.root,firing325_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1*10000+firing325_images[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==firing325_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1,(int)firing325_images[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* Coherent preflight and sticky failure for this selected-root cache lifetime.
 * Density4 and missing/corrupt/foreign-role resources never get partial HD. */
static bool firing325_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(firing325_resources.root))return false;
 if(!firing325_resources.checked) {
  firing325_resources.checked=true;firing325_resources.valid=true;
  memcpy(firing325_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<3;i++)if(!firing325_load(i))firing325_resources.valid=false;
 }
 if(!firing325_resources.valid||strcmp(firing325_resources.root,game_probe_assets))return false;
 /* Private payloads are immutable after load. Verify the whole family once
  * before the first original call each display frame, never 12 full scans. */
 if(firing325_resources.frame_checked&&firing325_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<3;i++) {
  Asset *a=&firing325_resources.member[i];int w=firing325_images[i].size?24:12,h=firing325_images[i].size?28:14;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)firing325_images[i].base||
   a->w!=w||a->h!=h||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)w*h*8*8*4)!=firing325_images[i].rgba) {
   firing325_resources.valid=false;return false;
  }
 }
 firing325_resources.checked_tick=mirror_logic_tick;firing325_resources.frame_checked=true;
 return true;
}
/* Original event6 pool25-49 with link0 and no intrinsic motion. The source
 * animation is held at entry1 or entry8 until ordinary shot allocation succeeds.
 * Ice, current armor/value, shot waits and multiposition remain authoritative. */
static bool firing325_actor(Sprite2_array bank,unsigned base,int x,int y,int part,int filter,const G101EnemyContext *c)
{
 if(!c||c->type!=325||c->pool_slot<25||c->pool_slot>=50||
  c->availability!=0||c->size!=1||c->score_item||c->damaged||c->independent_motion||
  c->static_animation)return false;
 const struct JE_SingleEnemyType *e=&enemy[c->pool_slot];
 if(enemyAvail[c->pool_slot]!=0||e->enemytype!=325||e->enemydatofs!=&enemyDat[325]||
  e->size!=1||e->scoreitem||e->edamaged||!e->armorleft||e->linknum||e->enemydie||
  !e->sprite2s||e->sprite2s->data!=bank.data||e->sprite2s->size!=bank.size||
  e->ani!=8||e->animin!=1||e->animax!=8||e->aniwhenfire!=2||
  e->enemycycle<1||e->enemycycle>8||e->filter!=filter||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=12)return false;
 /* Draw precedes firing. Advancing to entry8 holds before that callback;
  * a successful later shot resumes after drawing and wraps on the next draw. */
 if(!((e->aniactive==1&&e->enemycycle<8)||
  (e->aniactive==2&&(e->enemycycle==1||e->enemycycle==8))))return false;
 static const unsigned sequence[20]={277,277,277,125,125,277,277,11};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 if(base!=sequence[e->enemycycle-1]||e->tur[0]!=145||e->tur[1]||e->tur[2]||
  e->freq[0]!=28||e->freq[1]||e->freq[2]||e->launchfreq||e->launchtype||
  e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 return x-px==e->ex+e->mapoffset-6&&y-py==e->ey-7;
}
static bool firing325_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||!firing325_actor(bank,base,x,y,part,filter,c))return false;
 unsigned k=base==11?0:base==125?1:2;
 if(base!=firing325_images[k].base||c->size!=firing325_images[k].size||
  (c->size==0&&part!=0)||(c->size==1&&part!=0&&part!=1&&part!=19&&part!=20)||
  filter<0||filter>255)return false;
 if(!firing325_source(bank)||!firing325_family_ready()) {
  /* A dependency failure after an accepted quadrant rejects this entire frame.
   * Cold missing art stays an ordinary local classic fallback. */
  if(firing325_resources.drew&&firing325_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("firing325-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 bool mirrored=draw_asset_filtered(x-px,y-py,&firing325_resources.member[k],MIRROR_NORMAL,
  c->size?&quadrant:NULL,(Uint8)filter,NULL,NULL,NULL);
 if(mirrored){firing325_resources.drew=true;firing325_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
