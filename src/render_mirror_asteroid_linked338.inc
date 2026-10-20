/* SPDX-License-Identifier: GPL-2.0-or-later
 * Original NEWSHP installation338..342: five independently allocated actors,
 * eight body images, three exact links, and one persistent availability2 wreck.
 * Original allocation, animation, clipping, damage, homing and RNG stay in charge.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
/* Every image depends on all five canonical77 source records, including actors
 * that allocation failure or ordinary scrolling has left absent. */
static const struct {unsigned type;uint64_t record;} linked338_pins[5]={
 {338,UINT64_C(0xcbad2cf90f5c58cf)},
 {339,UINT64_C(0x2ddda4009b77985a)},
 {340,UINT64_C(0xcf24bb2935688c70)},
 {341,UINT64_C(0x1dbea2914b901887)},
 {342,UINT64_C(0x68faea6f9286755d)},
};
/* Exact payload pins for the reviewed eight-image candidate art family. */
static const struct {unsigned base,size;uint64_t rgba;} linked338_images[8]={
 {115,1,UINT64_C(0xc0b78dd44cd89946)},
 {117,1,UINT64_C(0x5b0b645099512ebb)},
 {119,1,UINT64_C(0x66a4ac4dca62cc21)},
 {121,1,UINT64_C(0x61d0da97ca63d5a3)},
 {229,1,UINT64_C(0x96ff18660e0c7cc9)},
 {231,1,UINT64_C(0x14d5f39137379c69)},
 {267,1,UINT64_C(0x15939655f4c95b4e)},
 {269,1,UINT64_C(0x3d83539c08ac80ca)},
};
/* NEWSHP is a third independent trust boundary. Never alias, enlarge or make
 * either the42012-byte NEWSHD or46566-byte NEWSHS snapshot size-tolerant. */
static struct {bool valid;Uint8 bytes[46204];} linked338_source_snapshot;
static bool linked338_source_bytes_match(const Uint8 *p,size_t n)
{
 if(!p||n!=sizeof(linked338_source_snapshot.bytes))return false;
 if(!linked338_source_snapshot.valid) {
  memcpy(linked338_source_snapshot.bytes,p,n);
  linked338_source_snapshot.valid=asteroid1_stamp(linked338_source_snapshot.bytes,n)==UINT64_C(0xe2413e3aeab4d908);
 }
 /* The renderer-owned reference is immutable within an epoch. Revalidate the
  * entire current bank every call, including same-address reuse/reload/rebind. */
 return linked338_source_snapshot.valid&&!memcmp(p,linked338_source_snapshot.bytes,n);
}
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[8];} linked338_resources;
static void linked338_shutdown(void)
{
 linked338_source_snapshot.valid=false;
 for(unsigned i=0;i<8;i++)free(linked338_resources.member[i].rgba);
 memset(&linked338_resources,0,sizeof(linked338_resources));
}
static bool linked338_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=46204)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==20&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!linked338_source_bytes_match(bank.data,bank.size))return false;
 for(unsigned i=0;i<5;i++)
  if(asteroid1_record_stamp(linked338_pins[i].type)!=linked338_pins[i].record)return false;
 return true;
}
static bool linked338_load(unsigned k)
{
 Asset *a=&linked338_resources.member[k];
 const unsigned w=24,h=28;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshp-%u-8.hda",linked338_resources.root,linked338_images[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1_NEWSHP*10000+linked338_images[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==linked338_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1_NEWSHP,(int)linked338_images[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* Eager eight-member preflight owns material135. Generic read_asset cannot
 * load this namespace. Missing/foreign/corrupt members fail this family only
 * and remain sticky until the selected-root renderer cache is reset. */
static bool linked338_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(linked338_resources.root))return false;
 if(!linked338_resources.checked) {
  linked338_resources.checked=true;linked338_resources.valid=true;
  memcpy(linked338_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<8;i++)if(!linked338_load(i))linked338_resources.valid=false;
 }
 if(!linked338_resources.valid||strcmp(linked338_resources.root,game_probe_assets))return false;
 /* Private immutable payloads are checked as one family before the first
  * original callback each display frame, independently from source-bank trust. */
 if(linked338_resources.frame_checked&&linked338_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<8;i++) {
  Asset *a=&linked338_resources.member[i];
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_NEWSHP||a->index!=(int)linked338_images[i].base||
   a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)24*28*8*8*4)!=linked338_images[i].rgba) {
   linked338_resources.valid=false;return false;
  }
 }
 linked338_resources.checked_tick=mirror_logic_tick;linked338_resources.frame_checked=true;
 return true;
}
/* Event6/event12 allocate338/339/340/341/342 separately in pool25..49.
 * No neighbor lookup, contiguous-slot requirement or absolute position pin.
 * Current positive armor/value, ice and inactive countdowns stay authoritative. */
static bool linked338_actor(Sprite2_array bank,unsigned base,int x,int y,int part,int filter,const G101EnemyContext *c)
{
 if(!c||c->type<338||c->type>342||c->pool_slot<25||c->pool_slot>=50||
  c->size!=1||c->score_item||c->independent_motion)return false;
 bool wreck=c->type==338&&c->availability==2;
 if(c->availability!=(wreck?2:0)||c->damaged!=wreck||
  c->static_animation!=(wreck||c->type!=338))return false;
 const struct JE_SingleEnemyType *e=&enemy[c->pool_slot];
 /* The original constructor binds the live slot object itself. A copied
  * Sprite2_array that merely aliases its bytes is not an original actor. */
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==20&&e->sprite2s==&enemySpriteSheets[i]&&
  bank.data==enemySpriteSheets[i].data&&bank.size==enemySpriteSheets[i].size)bound=true;
 if(!bound)return false;
 if(enemyAvail[c->pool_slot]!=(wreck?2:0)||e->enemytype!=c->type||e->enemydatofs!=&enemyDat[c->type]||
  e->size!=1||e->scoreitem||e->special||e->edamaged!=wreck||!e->armorleft||e->enemydie||
  !e->sprite2s||e->sprite2s->data!=bank.data||e->sprite2s->size!=bank.size||
  e->animin!=1||e->animax||e->aniwhenfire||e->filter!=filter||
  e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
  e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=12||
  e->tur[0]||e->tur[1]||e->tur[2]||e->freq[0]||e->freq[1]||e->freq[2]||
  e->launchfreq||e->launchtype||e->launchspecial)return false;
 if(e->linknum!=23&&e->linknum!=29&&e->linknum!=33)return false;
 static const unsigned cap[20]={115,115,115,117,117,117,119,119,119,117,117,117};
 static const unsigned support_base[4]={267,269,229,231};
 static const unsigned support_tail[20]={0,0,0,125,125,277,277,11};
 if(c->type==338) {
  if(e->edgr!=121||e->edlevel!=(wreck?0:-1)||e->edani)return false;
  for(unsigned i=0;i<20;i++)if(e->egr[i]!=(wreck&&i==0?121:cap[i]))return false;
  if(wreck) {
   if(e->ani!=1||e->aniactive||e->enemycycle!=1||base!=121)return false;
  } else {
   if(e->ani!=12||e->aniactive!=1||e->enemycycle<1||e->enemycycle>12||
    base!=cap[e->enemycycle-1])return false;
  }
 } else {
  unsigned expected=support_base[c->type-339];
  if(e->ani!=1||e->aniactive||e->enemycycle!=1||base!=expected||e->edgr||e->edlevel||e->edani)return false;
  for(unsigned i=0;i<20;i++)if(e->egr[i]!=(i?support_tail[i]:expected))return false;
 }
 /* Match each original quadrant and its original horizontal/row eligibility.
  * Whole-image roots remain actor-relative as scrolling changes mapoffset. */
 if(part!=0&&part!=1&&part!=19&&part!=20)return false;
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 if(e->ex+e->mapoffset<=-29||e->ex+e->mapoffset>=300||
  (!py&&e->ey<=-13)||(py&&(e->ey<=-26||e->ey>=182)))return false;
 return x-px==e->ex+e->mapoffset-6&&y-py==e->ey-7;
}
static bool linked338_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||filter<0||filter>255||!linked338_actor(bank,base,x,y,part,filter,c))return false;
 unsigned k=0;
 while(k<8&&base!=linked338_images[k].base)++k;
 if(k==8||c->size!=linked338_images[k].size)return false;
 if(!linked338_source(bank)||!linked338_family_ready()) {
  /* Cold fallback is local. A later dependency failure after a successful
   * quadrant rejects the whole HD frame, preserving ordered composition. */
  if(linked338_resources.drew&&linked338_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("linked338-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 bool mirrored=draw_asset_filtered(x-px,y-py,&linked338_resources.member[k],MIRROR_NORMAL,
  &quadrant,(Uint8)filter,NULL,NULL,NULL);
 if(mirrored){linked338_resources.drew=true;linked338_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1_NEWSHP,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
