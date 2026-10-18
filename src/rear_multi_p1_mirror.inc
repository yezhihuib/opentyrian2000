/* SPDX-License-Identifier: GPL-2.0-or-later
 * Dedicated normal-head adapter. No generic bank8 binding or shadow changes. */
#include "rear_multi_p1_pins.h"
#include <limits.h>
#include <fcntl.h>
#include <sys/stat.h>
#if defined(TARGET_WIN32) || defined(_WIN32)
#include <io.h>
#define REAR_OPEN(p) _open(p, _O_RDONLY | _O_BINARY | _O_NOINHERIT)
#define REAR_READ _read
#define REAR_CLOSE _close
#define REAR_FSTAT _fstat
#define REAR_STAT struct _stat
#define REAR_REGULAR(m) (((m) & _S_IFMT) == _S_IFREG)
#else
#include <unistd.h>
#define REAR_OPEN(p) open(p, O_RDONLY | O_NONBLOCK)
#define REAR_READ read
#define REAR_CLOSE close
#define REAR_FSTAT fstat
#define REAR_STAT struct stat
#define REAR_REGULAR(m) S_ISREG(m)
#endif
static RearP1State rear_p1_state;
static struct {
 bool started,valid;int density;char root[1024];
 struct {Asset asset;Uint8 *payload;bool attempted;} cache[REAR_P1_HEADS][2];
} rear_p1_resources;
static bool rear_p1_scope(void)
{
 return episodeNum==1&&((lvlFileNum==9&&initialDifficulty==DIFFICULTY_NORMAL)||
  (lvlFileNum==15&&initialDifficulty==DIFFICULTY_HARD))&&!xmas&&!isNetworkGame&&
  !twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!play_demo&&!record_demo&&
  !onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&!timedBattleMode&&
  !bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
/* Capture the selected root/density once per renderer session, before births.
 * Warm disk replacement is intentionally invisible until process restart. */
static void rear_p1_frame(void)
{
 rear_p1_call_end(&rear_p1_state);
 if(!rear_p1_scope())rear_p1_reset(&rear_p1_state);
 if(rear_p1_resources.started)return;
 rear_p1_resources.started=true;rear_p1_resources.density=game_probe_density;
 if(!game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(rear_p1_resources.root))return;
 memcpy(rear_p1_resources.root,game_probe_assets,strlen(game_probe_assets)+1);
 rear_p1_resources.valid=game_probe_density==4||game_probe_density==8;
}
void render_mirror_rear_p1_reset(void){rear_p1_reset(&rear_p1_state);}
static void rear_p1_shutdown(void)
{
 for(unsigned k=0;k<REAR_P1_HEADS;k++)for(unsigned d=0;d<2;d++)free(rear_p1_resources.cache[k][d].payload);
 memset(&rear_p1_resources,0,sizeof(rear_p1_resources));rear_p1_reset(&rear_p1_state);
}
/* Serialize ALL 80 original loader fields, including unused nonzero tails.
 * Word order and signed-byte conversion are explicit; struct padding is absent. */
static uint64_t rear_p1_record_stamp(const JE_WeaponType *w)
{
 Uint8 b[80];size_t n=0;
#define REAR_BYTE(v) do {b[n++]=(Uint8)(v);} while(0)
#define REAR_WORD(v) do {unsigned value_=(unsigned)(v);REAR_BYTE(value_);REAR_BYTE(value_>>8);} while(0)
 REAR_WORD(w->drain);REAR_BYTE(w->shotrepeat);REAR_BYTE(w->multi);REAR_WORD(w->weapani);
 REAR_BYTE(w->max);REAR_BYTE(w->tx);REAR_BYTE(w->ty);REAR_BYTE(w->aim);
 for(unsigned i=0;i<8;i++)REAR_BYTE(w->attack[i]);
 for(unsigned i=0;i<8;i++)REAR_BYTE(w->del[i]);
 for(unsigned i=0;i<8;i++)REAR_BYTE(w->sx[i]);
 for(unsigned i=0;i<8;i++)REAR_BYTE(w->sy[i]);
 for(unsigned i=0;i<8;i++)REAR_BYTE(w->bx[i]);
 for(unsigned i=0;i<8;i++)REAR_BYTE(w->by[i]);
 for(unsigned i=0;i<8;i++)REAR_WORD(w->sg[i]);
 REAR_BYTE(w->acceleration);REAR_BYTE(w->accelerationx);REAR_BYTE(w->circlesize);
 REAR_BYTE(w->sound);REAR_BYTE(w->trail);REAR_BYTE(w->shipblastfilter);
#undef REAR_WORD
#undef REAR_BYTE
 return n==sizeof(b)?rear_p1_stamp(b,sizeof(b)):0;
}
static bool rear_p1_table(unsigned record)
{
 static const uint64_t pins[22]=REAR_P1_RECORD_PINS;
 unsigned k;
 switch(record){case 254:k=0;break;case 265:k=1;break;case 255:k=2;break;case 266:k=3;break;case 267:k=4;break;case 256:k=5;break;case 257:k=6;break;case 268:k=7;break;case 269:k=8;break;case 258:k=9;break;case 259:k=10;break;case 270:k=11;break;case 260:k=12;break;case 271:k=13;break;case 261:k=14;break;case 272:k=15;break;case 262:k=16;break;case 273:k=17;break;case 263:k=18;break;case 274:k=19;break;case 275:k=20;break;case 264:k=21;break;default:return false;}
 return weaponPort[10].opnum==2&&
  weaponPort[10].op[0][0]==254&&weaponPort[10].op[1][0]==265&&
  weaponPort[10].op[0][1]==255&&weaponPort[10].op[1][1]==266&&weaponPort[10].poweruse==40&&
  (record!=267||weaponPort[10].op[1][2]==267)&&(record!=256||weaponPort[10].op[0][2]==256)&&
  (record!=257||weaponPort[10].op[0][3]==257)&&(record!=268||weaponPort[10].op[1][3]==268)&&
  (record!=269||weaponPort[10].op[1][4]==269)&&(record!=258||weaponPort[10].op[0][4]==258)&&
  (record!=259||weaponPort[10].op[0][5]==259)&&(record!=270||weaponPort[10].op[1][5]==270)&&
  (record!=260||weaponPort[10].op[0][6]==260)&&(record!=271||weaponPort[10].op[1][6]==271)&&
  (record!=261||weaponPort[10].op[0][7]==261)&&(record!=272||weaponPort[10].op[1][7]==272)&&
  (record!=262||weaponPort[10].op[0][8]==262)&&(record!=273||weaponPort[10].op[1][8]==273)&&
  (record!=263||weaponPort[10].op[0][9]==263)&&(record!=274||weaponPort[10].op[1][9]==274)&&
  (record!=275||weaponPort[10].op[1][10]==275)&&(record!=264||weaponPort[10].op[0][10]==264)&&
  rear_p1_record_stamp(&weapons[record])==pins[k];
}
static bool rear_p1_source(Sprite2_array bank,unsigned raw)
{
 static const uint64_t pins[REAR_P1_OBSERVED]=REAR_P1_SOURCE_PINS;
 int k=rear_p1_observed(raw);Uint8 decoded[REAR_P1_CELLS*2]={0};
 return k>=0&&bank.data&&spriteSheet8.data&&bank.data==spriteSheet8.data&&bank.size==spriteSheet8.size&&bank.size==REAR_P1_BANK_SIZE&&
  decode_tile(bank,raw,decoded,decoded+REAR_P1_CELLS,12,0,0)&&
  rear_p1_stamp(decoded,sizeof(decoded))==pins[k];
}
static RearP1Shot rear_p1_shot(unsigned slot)
{
 const PlayerShotDataType *s=&playerShotData[slot];
 return (RearP1Shot){s->shotGr,s->shotAni,s->shotAniMax,s->playerNumber,s->shotTrail,
  s->aimAtEnemy,s->chainReaction,s->shotComplicated,s->shotBlastFilter,s->shotXM,s->shotYM,s->shotXC,s->shotYC};
}
void render_mirror_rear_p1_call_begin(unsigned port,unsigned bay,unsigned power_index,
 unsigned mode_index,unsigned pnum,unsigned record)
{
 rear_p1_call_begin(&rear_p1_state,mirror_logic_tick,port,bay,power_index,mode_index,pnum,record,
  active&&rear_p1_scope(),rear_p1_table(record));
}
void render_mirror_rear_p1_call_end(void){rear_p1_call_end(&rear_p1_state);}
uint64_t render_mirror_rear_p1_create_begin(unsigned port,unsigned bay,unsigned record,unsigned pnum)
{return rear_p1_create_begin(&rear_p1_state,mirror_logic_tick,port,bay,record,pnum);}
void render_mirror_rear_p1_create_end(uint64_t call){rear_p1_create_end(&rear_p1_state,call);}
void render_mirror_rear_p1_emit(uint64_t call,unsigned ordinal,unsigned slot,unsigned port,unsigned bay,unsigned record,
 unsigned pnum,unsigned phase,unsigned raw)
{
 RearP1Shot shot={0};if(slot<REAR_P1_SLOTS)shot=rear_p1_shot(slot);
 rear_p1_emit(&rear_p1_state,mirror_logic_tick,call,ordinal,slot,port,bay,record,pnum,phase,raw,&shot,
  active&&rear_p1_scope(),rear_p1_table(record),rear_p1_source(spriteSheet8,raw));
}
/* A valid-format alias must never turn optional RGBA output into INDEX8 writes.
 * Called only after positive, bounded pitch/height checks for both surfaces. */
static bool rear_p1_disjoint(const SDL_Surface *a,const SDL_Surface *b)
{
 uintptr_t ap=(uintptr_t)a->pixels,bp=(uintptr_t)b->pixels;
 size_t an=(size_t)a->pitch*a->h,bn=(size_t)b->pitch*b->h;
 if(an>UINTPTR_MAX-ap||bn>UINTPTR_MAX-bp)return false;
 return ap+an<=bp||bp+bn<=ap;
}
static bool rear_p1_view(SDL_Surface *surface,int x,int y)
{
 int d=game_probe_density;
 return active&&!reject_reason&&!suppress&&surface&&surface==game_screen&&surface==VGAScreen&&
  surface->pixels&&surface->format&&surface->w==320&&surface->h==200&&
  surface->format->format==SDL_PIXELFORMAT_INDEX8&&surface->format->BitsPerPixel==8&&surface->format->BytesPerPixel==1&&
  surface->pitch>=320&&surface->pitch<=INT_MAX/200&&(d==4||d==8)&&
  canvas&&canvas->pixels&&canvas->format&&canvas->format->format==SDL_PIXELFORMAT_ARGB8888&&
  canvas->format->BitsPerPixel==32&&canvas->format->BytesPerPixel==4&&
  canvas->w==320*d&&canvas->h==200*d&&canvas->pitch>=canvas->w*4&&canvas->pitch%4==0&&
  canvas->pitch<=INT_MAX/canvas->h&&hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner&&
  (uintptr_t)canvas->pixels%sizeof(Uint32)==0&&(uintptr_t)green_first%sizeof(Uint16)==0&&(uintptr_t)green_under%sizeof(Uint32)==0&&
  rear_p1_disjoint(surface,canvas)&&
  x>=0&&x<=308&&y>=-13&&y<200;
}
/* Finite new-role loader: optional files must never block gameplay (FIFO,
 * directory or device). Generic read_asset and every older role stay unchanged. */
static bool rear_p1_load(Asset *a,int d)
{
 char path[1200];Uint8 h[28],extra;REAR_STAT st;
 if((d!=4&&d!=8)||!a||a->bank!=ASSET_REAR_MULTI_P1||rear_p1_member((unsigned)a->index)<0||
  ((a->index==182||a->index==183)&&d!=8)||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y)return false;
 int n=snprintf(path,sizeof(path),"%s/rear-multicannon-p1-bank8-%d-%d.hda",rear_p1_resources.root,a->index,d);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 size_t size=(size_t)REAR_P1_CELLS*d*d*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+size)&&
  REAR_READ(fd,h,sizeof(h))==(int)sizeof(h)&&!memcmp(h,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned b=0;b<4;b++)v[i]|=(uint32_t)h[4+i*4+b]<<(8*b);
  ok=v[0]==(uint32_t)(ASSET_REAR_MULTI_P1*10000+a->index)&&v[1]==(unsigned)d&&
   v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(size);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,size)==(int)size&&REAR_READ(fd,&extra,1)==0;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 a->density=d;a->rgba=rgba;return true;
}
static Asset *rear_p1_asset(unsigned raw)
{
 static const uint64_t pins[REAR_P1_HEADS][2]=REAR_P1_RGBA_PINS;
 int k=rear_p1_member(raw),d=game_probe_density;
 /* No d4 resource, resampling or upward-density fallback for 182/183.
  * Reject before touching either cache slot or opening any role file. */
 if(k<0||((raw==182||raw==183)&&d!=8)||(d!=4&&d!=8)||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !(game_probe_scene_assets&1)||!game_probe_assets||!rear_p1_resources.valid||
  rear_p1_resources.density!=d||strcmp(game_probe_assets,rear_p1_resources.root))return NULL;
 unsigned di=d==8;
 /* A zero pin is an intentionally unavailable role, never a payload hash.
  * Unsupported d4 for182/183 stays closed before any role file is opened. */
 if(!pins[k][di])return NULL;
 Asset *a=&rear_p1_resources.cache[k][di].asset;
 if(!rear_p1_resources.cache[k][di].attempted) {
  /* A warm slot whose control bit was changed is not a new cold cache. */
  if(rear_p1_resources.cache[k][di].payload||a->initialized||a->valid||a->bank||a->index||
   a->w||a->h||a->anchor_x||a->anchor_y||a->density||a->rgba)return NULL;
  rear_p1_resources.cache[k][di].attempted=true;
  *a=(Asset){true,false,ASSET_REAR_MULTI_P1,(int)raw,12,14,0,0,d,NULL};
  a->valid=rear_p1_load(a,d);rear_p1_resources.cache[k][di].payload=a->rgba;
 }
 /* Identity and bounded layout precede hashing, including all warm calls. */
 if(!a->initialized||!a->valid||a->bank!=ASSET_REAR_MULTI_P1||a->index!=(int)raw||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=d||!a->rgba||
  a->rgba!=rear_p1_resources.cache[k][di].payload||
  rear_p1_stamp(a->rgba,(size_t)REAR_P1_CELLS*d*d*4)!=pins[k][di])return NULL;
 return a;
}
bool render_mirror_rear_p1_head(SDL_Surface *surface,int x,int y,Sprite2_array bank,
 unsigned index,unsigned slot,unsigned raw)
{
 if(slot>=REAR_P1_SLOTS)return false;
 RearP1Shot shot=rear_p1_shot(slot);
 unsigned record=rear_p1_state.birth[slot].record;
 /* Source/record/live-shot invalidity revokes this birth, even after warming.
  * Moving off-screen or a temporarily unavailable resource never creates birth. */
 if(!rear_p1_current(&rear_p1_state,slot,index,raw,&shot,rear_p1_scope(),rear_p1_table(record),rear_p1_source(bank,raw)))return false;
 if(!rear_p1_view(surface,x,y)||x!=(int)playerShotData[slot].shotX+1||y!=playerShotData[slot].shotY)return false;
 Asset *a=rear_p1_asset(raw);if(!a)return false;
 return draw_asset(x,y,a,MIRROR_NORMAL,NULL);
}
