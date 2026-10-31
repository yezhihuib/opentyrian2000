/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional normal bank8 enemy162/260: two distinct static visual families.
 * 162 is one shot with two separated lobes; 260 has native independent shots.
 * No animation, coordinates, speed, state, allocation or RNG changes.
 * Each payload is independent; unused missing members do not gate others. */
#include "current_projectile_statics_payload_pins.h"
typedef struct {bool checked,valid;char root[1024];Asset member;} StaticsResource;
static StaticsResource projectile_statics_resources[2];
static const unsigned projectile_statics_indices[2]={162,260};
static const uint64_t projectile_statics_pins[2]={
 CURRENT_PROJECTILE_STATICS_1540162_PAYLOAD_FNV,
 CURRENT_PROJECTILE_STATICS_1540260_PAYLOAD_FNV};
static int projectile_statics_slot(unsigned index)
{return index==162?0:index==260?1:-1;}
static void projectile_statics_shutdown(void)
{
 for(unsigned i=0;i<2;i++)free(projectile_statics_resources[i].member.rgba);
 memset(projectile_statics_resources,0,sizeof(projectile_statics_resources));
}
/* Keep the complete normal-bank guard even though these two selected native
 * Christmas tiles are identical. This loads neither91 art nor its palette. */
static bool projectile_statics_source(Sprite2_array bank,unsigned index)
{return projectile_statics_slot(index)>=0&&projectile91_source(bank,91);}
static bool projectile_statics_load(unsigned slot)
{
 StaticsResource *r=&projectile_statics_resources[slot];
 unsigned index=projectile_statics_indices[slot];
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-projectile-statics-%u-8.hda",r->root,index);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ENEMY_STATICS*10000+index&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==projectile_statics_pins[slot];
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 r->member=(Asset){true,true,ASSET_ENEMY_STATICS,index,12,14,0,0,8,rgba};
 return true;
}
/* Independent member root epochs. Disk replacement is observed only after
 * shutdown; same-root setup is not an epoch change. Recheck each used in-memory
 * dependency at callback/final/cache through the existing shared owner. */
static Asset *projectile_statics_resource(const char *root,unsigned index)
{
 int slot=projectile_statics_slot(index);
 if(slot<0||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !root||!root[0]||strlen(root)>=sizeof(projectile_statics_resources[0].root))return NULL;
 StaticsResource *r=&projectile_statics_resources[slot];
 if(!r->checked) {
  r->checked=true;memcpy(r->root,root,strlen(root)+1);
  r->valid=projectile_statics_load((unsigned)slot);
 }
 if(!r->valid||strcmp(r->root,root))return NULL;
 Asset *a=&r->member;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ENEMY_STATICS||a->index!=index||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile_statics_pins[slot]) {
  r->valid=false;return NULL;
 }
 return a;
}
/* Actual selected native colors, not a shared-family palette assumption.
 * These overlap real61 and gold168/169 dependencies. Existing used-underlay
 * and complete cached-output palette guards remain unchanged. */
static bool projectile_statics_palette_matches(unsigned index)
{
 switch(index) {
 case 162: {
  static const unsigned indices[]={122,123,125,126,127};
  static const Uint32 colors[]={0xeb8a18,0xf3ae24,0xffe73c,0xfffb96,0xfffff3};
  for(unsigned i=0;i<sizeof(indices)/sizeof(*indices);i++)if((rgb_palette[indices[i]]&0xffffffu)!=colors[i])return false;
  return true;
 }
 case 260: {
  static const unsigned indices[]={113,116,117,119,120,121,122,123,124,125,126};
  static const Uint32 colors[]={0x380000,0x860400,0x9e0800,0xd31400,0xdf3c00,0xe7610c,0xeb8a18,0xf3ae24,0xfbcb30,0xffe73c,0xfffb96};
  for(unsigned i=0;i<sizeof(indices)/sizeof(*indices);i++)if((rgb_palette[indices[i]]&0xffffffu)!=colors[i])return false;
  return true;
 }
 default:return false;
 }
}
