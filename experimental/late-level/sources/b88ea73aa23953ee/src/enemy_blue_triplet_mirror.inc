/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional normal bank8 enemy101/120/139. Three original independent shots,
 * not a new beam. No coordinates, speed, state or RNG changes.
 * Each payload is independent; unused missing members do not gate others. */
#include "current_projectile_blue_triplet_payload_pins.h"
typedef struct {bool checked,valid;char root[1024];Asset member;} BlueTripletResource;
static BlueTripletResource projectile_blue_triplet_resources[3];
static const unsigned projectile_blue_triplet_indices[3]={101,120,139};
static const uint64_t projectile_blue_triplet_pins[3]={
 CURRENT_PROJECTILE_BLUE_TRIPLET_1520101_PAYLOAD_FNV,
 CURRENT_PROJECTILE_BLUE_TRIPLET_1520120_PAYLOAD_FNV,
 CURRENT_PROJECTILE_BLUE_TRIPLET_1520139_PAYLOAD_FNV};
static int projectile_blue_triplet_slot(unsigned index)
{return index==101?0:index==120?1:index==139?2:-1;}
static void projectile_blue_triplet_shutdown(void)
{
 for(unsigned i=0;i<3;i++)free(projectile_blue_triplet_resources[i].member.rgba);
 memset(projectile_blue_triplet_resources,0,sizeof(projectile_blue_triplet_resources));
}
/* Authenticate the complete normal bank, without loading optional91 art or
 * requiring its gray palette. Christmas has different source identities. */
static bool projectile_blue_triplet_source(Sprite2_array bank,unsigned index)
{return projectile_blue_triplet_slot(index)>=0&&projectile91_source(bank,91);}
static bool projectile_blue_triplet_load(unsigned slot)
{
 BlueTripletResource *r=&projectile_blue_triplet_resources[slot];
 unsigned index=projectile_blue_triplet_indices[slot];
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-projectile-blue-triplet-%u-8.hda",r->root,index);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ENEMY_BLUE_TRIPLET*10000+index&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==projectile_blue_triplet_pins[slot];
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 r->member=(Asset){true,true,ASSET_ENEMY_BLUE_TRIPLET,index,12,14,0,0,8,rgba};
 return true;
}
/* Per-member root epochs; disk replacement is observed only after shutdown.
 * Revalidate every callback and every used final/cache dependency in memory. */
static Asset *projectile_blue_triplet_resource(const char *root,unsigned index)
{
 int slot=projectile_blue_triplet_slot(index);
 if(slot<0||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !root||!root[0]||strlen(root)>=sizeof(projectile_blue_triplet_resources[0].root))return NULL;
 BlueTripletResource *r=&projectile_blue_triplet_resources[slot];
 if(!r->checked) {
  r->checked=true;memcpy(r->root,root,strlen(root)+1);
  r->valid=projectile_blue_triplet_load((unsigned)slot);
 }
 if(!r->valid||strcmp(r->root,root))return NULL;
 Asset *a=&r->member;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ENEMY_BLUE_TRIPLET||a->index!=index||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile_blue_triplet_pins[slot]) {
  r->valid=false;return NULL;
 }
 return a;
}
/* Validate only the original selected member's actual used colors at admission.
 * Existing underlay-used and cached full-palette guards remain unchanged. */
static bool projectile_blue_triplet_palette_matches(unsigned index)
{
 switch(index) {
 case 101: {
  static const unsigned indices[]={138,140,141,142,143,145,146,147,148,149,150,151,152,153,154,155,156,157,159};
  static const Uint32 colors[]={0x9acbcf,0xbadfe3,0xcbebeb,0xdbf7f7,0xefffff,0x000034,0x000051,0x00006d,0x00008a,0x0000aa,0x0000c7,0x0810cf,0x1428db,0x1c3ce3,0x2851eb,0x3469f7,0x4986f3,0x599eef,0x79bee7};
  for(unsigned i=0;i<sizeof(indices)/sizeof(*indices);i++)if((rgb_palette[indices[i]]&0xffffffu)!=colors[i])return false;
  return true;
 }
 case 120: {
  static const unsigned indices[]={140,145,149,153,156,159};
  static const Uint32 colors[]={0xbadfe3,0x000034,0x0000aa,0x1c3ce3,0x4986f3,0x79bee7};
  for(unsigned i=0;i<sizeof(indices)/sizeof(*indices);i++)if((rgb_palette[indices[i]]&0xffffffu)!=colors[i])return false;
  return true;
 }
 case 139: {
  static const unsigned indices[]={138,140,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159};
  static const Uint32 colors[]={0x9acbcf,0xbadfe3,0x000018,0x000034,0x000051,0x00006d,0x00008a,0x0000aa,0x0000c7,0x0810cf,0x1428db,0x1c3ce3,0x2851eb,0x3469f7,0x4986f3,0x599eef,0x69aeeb,0x79bee7};
  for(unsigned i=0;i<sizeof(indices)/sizeof(*indices);i++)if((rgb_palette[indices[i]]&0xffffffu)!=colors[i])return false;
  return true;
 }
 default:return false;
 }
}
