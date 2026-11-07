/* SPDX-License-Identifier: GPL-2.0-or-later
 * One source-bound ten-actor asteroid. Original calls, clipping, events and
 * linked destruction remain authoritative. No ordinary spriteSheet8 binding.
 * REAR_* is the existing portable nonblocking regular-file IO adapter above.
 */
static const struct {unsigned type,base,size;uint64_t record,rgba;} asteroid1_pins[10]={
 {444,31,0,UINT64_C(0xd18e2125a0b9297c),UINT64_C(0x70e3d713ffed571f)},
 {445,13,1,UINT64_C(0x8a32351e5452612d),UINT64_C(0x6e6aa81080fcfe5f)},
 {446,15,0,UINT64_C(0x9a4fc35bc0ebcf6c),UINT64_C(0x37ec021a26d0e1f3)},
 {447,34,0,UINT64_C(0x719eea10bb6124b1),UINT64_C(0xdff1f6ac6cf18cc2)},
 {448,49,1,UINT64_C(0xc8e432357d042f51),UINT64_C(0x0af7bccdee9a2294)},
 {449,51,1,UINT64_C(0xfdf4bd9c8d5ee513),UINT64_C(0xddf7d31f051f12a4)},
 {450,53,1,UINT64_C(0xd6b3c9a7f4f785d5),UINT64_C(0x09b4755dc441468e)},
 {451,88,0,UINT64_C(0x9e50bab241c4264b),UINT64_C(0xc76ea65dc798f04d)},
 {452,89,1,UINT64_C(0xe735acc407e868d9),UINT64_C(0x56b23c9956b508e1)},
 {453,91,1,UINT64_C(0x1c46382b18431e9b),UINT64_C(0x9de77bbe26715bd3)},
};
static struct {bool checked,valid,frame_checked;uint64_t checked_tick,drawn_tick;bool drew;char root[1024];Asset member[10];} asteroid1_resources;
static uint64_t asteroid1_stamp(const Uint8 *p,size_t n)
{
 uint64_t h=UINT64_C(0xcbf29ce484222325);
 while(n--){h^=*p++;h*=UINT64_C(0x100000001b3);}return h;
}
#include "asteroid1_source_snapshot.inc"
static void asteroid1_shutdown(void)
{
 /* Static storage needs no free; revoke trust for the next renderer epoch. */
 asteroid1_source_snapshot.valid=false;
 for(unsigned i=0;i<10;i++)free(asteroid1_resources.member[i].rgba);
 memset(&asteroid1_resources,0,sizeof(asteroid1_resources));
}
/* Serialize the exact original 77-byte record, without compiler padding. */
static uint64_t asteroid1_record_stamp(unsigned type)
{
 Uint8 b[77];size_t n=0;
#define AST_BYTE(v) do {b[n++]=(Uint8)(v);} while(0)
#define AST_WORD(v) do {unsigned word_=(unsigned)(v);AST_BYTE(word_);AST_BYTE(word_>>8);} while(0)
 AST_BYTE(enemyDat[type].ani);
 for(unsigned i=0;i<3;i++)AST_BYTE(enemyDat[type].tur[i]);
 for(unsigned i=0;i<3;i++)AST_BYTE(enemyDat[type].freq[i]);
 AST_BYTE(enemyDat[type].xmove);AST_BYTE(enemyDat[type].ymove);
 AST_BYTE(enemyDat[type].xaccel);AST_BYTE(enemyDat[type].yaccel);
 AST_BYTE(enemyDat[type].xcaccel);AST_BYTE(enemyDat[type].ycaccel);
 AST_WORD(enemyDat[type].startx);AST_WORD(enemyDat[type].starty);
 AST_BYTE(enemyDat[type].startxc);AST_BYTE(enemyDat[type].startyc);
 AST_BYTE(enemyDat[type].armor);AST_BYTE(enemyDat[type].esize);
 for(unsigned i=0;i<20;i++)AST_WORD(enemyDat[type].egraphic[i]);
 AST_BYTE(enemyDat[type].explosiontype);AST_BYTE(enemyDat[type].animate);
 AST_BYTE(enemyDat[type].shapebank);AST_BYTE(enemyDat[type].xrev);AST_BYTE(enemyDat[type].yrev);
 AST_WORD(enemyDat[type].dgr);AST_BYTE(enemyDat[type].dlevel);AST_BYTE(enemyDat[type].dani);
 AST_BYTE(enemyDat[type].elaunchfreq);AST_WORD(enemyDat[type].elaunchtype);
 AST_WORD(enemyDat[type].value);AST_WORD(enemyDat[type].eenemydie);
#undef AST_WORD
#undef AST_BYTE
 return n==sizeof(b)?asteroid1_stamp(b,sizeof(b)):0;
}
/* Current bytes are checked on every draw, including warm/address-reused banks.
 * All ten records are one dependency, even when only one actor is visible. */
static bool asteroid1_source(Sprite2_array bank)
{
 if(!bank.data||bank.data==spriteSheet8.data||bank.size!=42012)return false;
 bool loaded=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank.data==enemySpriteSheets[i].data&&
   bank.size==enemySpriteSheets[i].size)loaded=true;
 if(!loaded||!asteroid1_source_bytes_match(bank.data,bank.size))return false;
 for(unsigned i=0;i<10;i++)
  if(asteroid1_record_stamp(asteroid1_pins[i].type)!=asteroid1_pins[i].record)return false;
 return true;
}
static bool asteroid1_load(unsigned k)
{
 Asset *a=&asteroid1_resources.member[k];
 unsigned w=asteroid1_pins[k].size?24:12,h=asteroid1_pins[k].size?28:14;
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-newshd-%u-8.hda",asteroid1_resources.root,asteroid1_pins[k].base);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t bytes=(size_t)w*h*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ASTEROID1*10000+asteroid1_pins[k].base&&v[1]==8&&v[2]==w&&v[3]==h&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==asteroid1_pins[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 *a=(Asset){true,true,ASSET_ASTEROID1,(int)asteroid1_pins[k].base,(int)w,(int)h,0,0,8,rgba};
 return true;
}
/* Coherent preflight and sticky failure for this selected-root cache lifetime.
 * Density4 and missing/corrupt/foreign-role resources never get partial HD. */
static bool asteroid1_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(asteroid1_resources.root))return false;
 if(!asteroid1_resources.checked) {
  asteroid1_resources.checked=true;asteroid1_resources.valid=true;
  memcpy(asteroid1_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
  for(unsigned i=0;i<10;i++)if(!asteroid1_load(i))asteroid1_resources.valid=false;
 }
 if(!asteroid1_resources.valid||strcmp(asteroid1_resources.root,game_probe_assets))return false;
 /* Private payloads are immutable after load. Verify the whole family once
  * before the first original call each display frame, never 28 full scans. */
 if(asteroid1_resources.frame_checked&&asteroid1_resources.checked_tick==mirror_logic_tick)return true;
 for(unsigned i=0;i<10;i++) {
  Asset *a=&asteroid1_resources.member[i];int w=asteroid1_pins[i].size?24:12,h=asteroid1_pins[i].size?28:14;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)asteroid1_pins[i].base||
   a->w!=w||a->h!=h||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
   asteroid1_stamp(a->rgba,(size_t)w*h*8*8*4)!=asteroid1_pins[i].rgba) {
   asteroid1_resources.valid=false;return false;
  }
 }
 asteroid1_resources.checked_tick=mirror_logic_tick;asteroid1_resources.frame_checked=true;
 return true;
}
static bool asteroid1_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!asteroid_hd_enabled||!asteroid1_level_scope()||
  (!game_probe_enabled&&(!asteroid_hd_lease||!asteroid1_scope()))||
  !active||reject_reason||!(game_probe_scene_assets&1)||!surface||surface!=game_screen||surface!=VGAScreen||
  !surface->pixels||surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
  surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
  x<0||x>308||y<-13||y>199||!c||c->type<444||c->type>453||
  c->availability==1||c->availability>2||c->score_item||c->damaged||!c->static_animation)return false;
 unsigned k=c->type-444;
 if(base!=asteroid1_pins[k].base||c->size!=asteroid1_pins[k].size||
  (c->size==0&&part!=0)||(c->size==1&&part!=0&&part!=1&&part!=19&&part!=20)||
  filter<0||filter>255)return false;
 if(!asteroid1_source(bank)||!asteroid1_family_ready()) {
  /* A dependency failure after an accepted quadrant rejects this entire frame.
   * Cold missing art stays an ordinary local classic fallback. */
  if(asteroid1_resources.drew&&asteroid1_resources.drawn_tick==mirror_logic_tick)
   render_mirror_unsupported("asteroid1-family-integrity");
  return false;
 }
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 SDL_Rect quadrant={px,py,12,14};
 bool mirrored=draw_asset_filtered(x-px,y-py,&asteroid1_resources.member[k],MIRROR_NORMAL,
  c->size?&quadrant:NULL,(Uint8)filter,NULL,NULL,NULL);
 if(mirrored){asteroid1_resources.drew=true;asteroid1_resources.drawn_tick=mirror_logic_tick;}
 game_probe_scene_draw(ASSET_ASTEROID1,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
 return mirrored;
}
