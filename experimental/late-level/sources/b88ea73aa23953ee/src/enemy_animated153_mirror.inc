/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional normal bank8 enemy153/154/155: three independent indexed phases, full-canvas mirror.
 * No changes to animation, coordinates, speed, state, allocation or RNG changes.
 * All player paths remain classic; encoded indices resolve through the live palette.
 * Each resource is independent; unused missing payloads do not gate others. */
#include "current_projectile_animated153_payload_pins.h"
#if CURRENT_PROJECTILE_ANIMATED153_ART_QUALIFIED
typedef struct {bool checked,valid;char root[1024];Asset member;} Animated153Resource;
static Animated153Resource projectile_animated153_resources[3];
static const unsigned projectile_animated153_indices[3]={153,154,155};
static const uint64_t projectile_animated153_pins[3]={
 CURRENT_PROJECTILE_ANIMATED153_1570153_PAYLOAD_FNV,
 CURRENT_PROJECTILE_ANIMATED153_1570154_PAYLOAD_FNV,
 CURRENT_PROJECTILE_ANIMATED153_1570155_PAYLOAD_FNV};
static int projectile_animated153_slot(unsigned index)
{return index==153?0:index==154?1:index==155?2:-1;}
static void projectile_animated153_shutdown(void)
{
 for(unsigned i=0;i<3;i++)free(projectile_animated153_resources[i].member.rgba);
 memset(projectile_animated153_resources,0,sizeof(projectile_animated153_resources));
}
/* Full normal bank8 authentication; Christmas and wrong bank stay classic.
 * This does not load91 art or require a fixed scene RGB palette. */
static bool projectile_animated153_source(Sprite2_array bank,unsigned index)
{return projectile_animated153_slot(index)>=0&&projectile91_source(bank,91);}
static bool projectile_animated153_load(unsigned slot)
{
 Animated153Resource *r=&projectile_animated153_resources[slot];
 unsigned index=projectile_animated153_indices[slot];
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-projectile-animated153-%u-8.hda",r->root,index);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ENEMY_ANIMATED153*10000+index&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==projectile_animated153_pins[slot];
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 r->member=(Asset){true,true,ASSET_ENEMY_ANIMATED153,index,12,14,0,0,8,rgba};
 return true;
}
/* Independent member root epochs. Disk replacement is observed only after
 * shutdown; same-root setup is not an epoch change. Recheck each used in-memory
 * dependency at callback/final/cache through the existing shared owner. */
static Asset *projectile_animated153_resource(const char *root,unsigned index)
{
 int slot=projectile_animated153_slot(index);
 if(slot<0||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !root||!root[0]||strlen(root)>=sizeof(projectile_animated153_resources[0].root))return NULL;
 Animated153Resource *r=&projectile_animated153_resources[slot];
 if(!r->checked) {
  r->checked=true;memcpy(r->root,root,strlen(root)+1);
  r->valid=projectile_animated153_load((unsigned)slot);
 }
 if(!r->valid||strcmp(r->root,root))return NULL;
 Asset *a=&r->member;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ENEMY_ANIMATED153||a->index!=index||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile_animated153_pins[slot]) {
  r->valid=false;return NULL;
 }
 return a;
}
/* No observed scene RGB is baked into this family. Contribution-time indexed
 * colors are snapshotted by the shared owner and checked at callback/final/cache.
 * Exact payload pins above authenticate [index,0,0,binary alpha] representation. */
static bool projectile_animated153_palette_matches(unsigned index)
{return projectile_animated153_slot(index)>=0;}

#else
/* Preparation only: no placeholder pins or synthetic production payloads. */
static bool projectile_animated153_source(Sprite2_array bank,unsigned index)
{(void)bank;(void)index;return false;}
static bool projectile_animated153_palette_matches(unsigned index)
{(void)index;return false;}
static Asset *projectile_animated153_resource(const char *root,unsigned index)
{(void)root;(void)index;return NULL;}
static void projectile_animated153_shutdown(void) {}
#endif
