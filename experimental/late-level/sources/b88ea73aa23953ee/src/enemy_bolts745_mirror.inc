/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional normal bank8 enemy7/45: one canonical index-coded source, full-canvas mirror.
 * No animation, coordinates, speed, state, allocation or RNG changes.
 * All player paths remain classic; encoded indices resolve through the live palette.
 * Each resource is independent; unused missing payloads do not gate others. */
#include "current_projectile_bolts745_payload_pins.h"
typedef struct {bool checked,valid;char root[1024];Asset member;} Bolts745Resource;
static Bolts745Resource projectile_bolts745_resources[2];
static const unsigned projectile_bolts745_indices[2]={7,45};
static const uint64_t projectile_bolts745_pins[2]={
 CURRENT_PROJECTILE_BOLTS745_1560007_PAYLOAD_FNV,
 CURRENT_PROJECTILE_BOLTS745_1560045_PAYLOAD_FNV};
static int projectile_bolts745_slot(unsigned index)
{return index==7?0:index==45?1:-1;}
static void projectile_bolts745_shutdown(void)
{
 for(unsigned i=0;i<2;i++)free(projectile_bolts745_resources[i].member.rgba);
 memset(projectile_bolts745_resources,0,sizeof(projectile_bolts745_resources));
}
/* Authenticate the complete normal bank8, including unused sprites/offsets.
 * Both selected Christmas originals differ and stay classic; the shared guard
 * also rejects warm normal state under xmas. Loads neither91 art nor palette. */
static bool projectile_bolts745_source(Sprite2_array bank,unsigned index)
{return projectile_bolts745_slot(index)>=0&&projectile91_source(bank,91);}
static bool projectile_bolts745_load(unsigned slot)
{
 Bolts745Resource *r=&projectile_bolts745_resources[slot];
 unsigned index=projectile_bolts745_indices[slot];
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-projectile-bolts745-%u-8.hda",r->root,index);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ENEMY_BOLTS745*10000+index&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==projectile_bolts745_pins[slot];
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 r->member=(Asset){true,true,ASSET_ENEMY_BOLTS745,index,12,14,0,0,8,rgba};
 return true;
}
/* Independent member root epochs. Disk replacement is observed only after
 * shutdown; same-root setup is not an epoch change. Recheck each used in-memory
 * dependency at callback/final/cache through the existing shared owner. */
static Asset *projectile_bolts745_resource(const char *root,unsigned index)
{
 int slot=projectile_bolts745_slot(index);
 if(slot<0||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !root||!root[0]||strlen(root)>=sizeof(projectile_bolts745_resources[0].root))return NULL;
 Bolts745Resource *r=&projectile_bolts745_resources[slot];
 if(!r->checked) {
  r->checked=true;memcpy(r->root,root,strlen(root)+1);
  r->valid=projectile_bolts745_load((unsigned)slot);
 }
 if(!r->valid||strcmp(r->root,root))return NULL;
 Asset *a=&r->member;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ENEMY_BOLTS745||a->index!=index||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile_bolts745_pins[slot]) {
  r->valid=false;return NULL;
 }
 return a;
}
/* No observed scene RGB is baked into this family. Contribution-time indexed
 * colors are snapshotted by the shared owner and checked at callback/final/cache.
 * Exact payload pins above authenticate [index,0,0,binary alpha] representation. */
static bool projectile_bolts745_palette_matches(unsigned index)
{return projectile_bolts745_slot(index)>=0;}
