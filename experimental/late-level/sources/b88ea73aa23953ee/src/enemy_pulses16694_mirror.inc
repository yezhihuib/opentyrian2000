/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional normal bank8 enemy166/94: two independent static resources.
 * No animation, coordinates, speed, state, allocation or RNG changes.
 * Player166 option25/weapon719 alias and all player paths remain classic.
 * Each resource is independent; unused missing payloads do not gate others. */
#include "current_projectile_pulses16694_payload_pins.h"
typedef struct {bool checked,valid;char root[1024];Asset member;} Pulses16694Resource;
static Pulses16694Resource projectile_pulses16694_resources[2];
static const unsigned projectile_pulses16694_indices[2]={166,94};
static const uint64_t projectile_pulses16694_pins[2]={
 CURRENT_PROJECTILE_PULSES16694_1550166_PAYLOAD_FNV,
 CURRENT_PROJECTILE_PULSES16694_1550094_PAYLOAD_FNV};
static int projectile_pulses16694_slot(unsigned index)
{return index==166?0:index==94?1:-1;}
static void projectile_pulses16694_shutdown(void)
{
 for(unsigned i=0;i<2;i++)free(projectile_pulses16694_resources[i].member.rgba);
 memset(projectile_pulses16694_resources,0,sizeof(projectile_pulses16694_resources));
}
/* Authenticate the complete normal bank8, including unused sprites/offsets.
 * Both selected Christmas originals differ and stay classic; the shared guard
 * also rejects warm normal state under xmas. Loads neither91 art nor palette. */
static bool projectile_pulses16694_source(Sprite2_array bank,unsigned index)
{return projectile_pulses16694_slot(index)>=0&&projectile91_source(bank,91);}
static bool projectile_pulses16694_load(unsigned slot)
{
 Pulses16694Resource *r=&projectile_pulses16694_resources[slot];
 unsigned index=projectile_pulses16694_indices[slot];
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-projectile-pulses16694-%u-8.hda",r->root,index);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ENEMY_PULSES16694*10000+index&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==projectile_pulses16694_pins[slot];
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 r->member=(Asset){true,true,ASSET_ENEMY_PULSES16694,index,12,14,0,0,8,rgba};
 return true;
}
/* Independent member root epochs. Disk replacement is observed only after
 * shutdown; same-root setup is not an epoch change. Recheck each used in-memory
 * dependency at callback/final/cache through the existing shared owner. */
static Asset *projectile_pulses16694_resource(const char *root,unsigned index)
{
 int slot=projectile_pulses16694_slot(index);
 if(slot<0||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !root||!root[0]||strlen(root)>=sizeof(projectile_pulses16694_resources[0].root))return NULL;
 Pulses16694Resource *r=&projectile_pulses16694_resources[slot];
 if(!r->checked) {
  r->checked=true;memcpy(r->root,root,strlen(root)+1);
  r->valid=projectile_pulses16694_load((unsigned)slot);
 }
 if(!r->valid||strcmp(r->root,root))return NULL;
 Asset *a=&r->member;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ENEMY_PULSES16694||a->index!=index||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile_pulses16694_pins[slot]) {
  r->valid=false;return NULL;
 }
 return a;
}
/* Native source palette5 dependencies, independently selected for each member.
 * 166 overlaps old blue101/120/139;94 overlaps61/gold168/169/statics162/260.
 * Foreign-underlay and full cached-output palette checks remain shared. */
static bool projectile_pulses16694_palette_matches(unsigned index)
{
 switch(index) {
 case 166: {
  static const unsigned indices[]={33,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159};
  static const Uint32 colors[]={0x001404,0x000018,0x000034,0x000051,0x00006d,0x00008a,0x0000aa,0x0000c7,0x0810cf,0x1428db,0x1c3ce3,0x2851eb,0x3469f7,0x4986f3,0x599eef,0x69aeeb,0x79bee7};
  for(unsigned i=0;i<sizeof(indices)/sizeof(*indices);i++)if((rgb_palette[indices[i]]&0xffffffu)!=colors[i])return false;
  return true;
 }
 case 94: {
  static const unsigned indices[]={114,115,116,117,119,120,121,122,123,124,125,126,127};
  static const Uint32 colors[]={0x510000,0x6d0400,0x860400,0x9e0800,0xd31400,0xdf3c00,0xe7610c,0xeb8a18,0xf3ae24,0xfbcb30,0xffe73c,0xfffb96,0xfffff3};
  for(unsigned i=0;i<sizeof(indices)/sizeof(*indices);i++)if((rgb_palette[indices[i]]&0xffffffu)!=colors[i])return false;
  return true;
 }
 default:return false;
 }
}
