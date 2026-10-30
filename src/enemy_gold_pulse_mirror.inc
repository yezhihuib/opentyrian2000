/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional normal bank8 enemy168/169. Two frames of one original animated
 * shot, not two new shots. No coordinates, speed, state or RNG changes.
 * Each payload is independent; unused missing members do not gate others. */
#include "current_projectile_gold_pulse_payload_pins.h"
typedef struct {bool checked,valid;char root[1024];Asset member;} GoldPulseResource;
static GoldPulseResource projectile_gold_pulse_resources[2];
static const unsigned projectile_gold_pulse_indices[2]={168,169};
static const uint64_t projectile_gold_pulse_pins[2]={
 CURRENT_PROJECTILE_GOLD_PULSE_1530168_PAYLOAD_FNV,
 CURRENT_PROJECTILE_GOLD_PULSE_1530169_PAYLOAD_FNV};
static int projectile_gold_pulse_slot(unsigned index)
{return index==168?0:index==169?1:-1;}
static void projectile_gold_pulse_shutdown(void)
{
 for(unsigned i=0;i<2;i++)free(projectile_gold_pulse_resources[i].member.rgba);
 memset(projectile_gold_pulse_resources,0,sizeof(projectile_gold_pulse_resources));
}
/* Authenticate the complete normal bank, without loading optional91 art or
 * requiring its gray palette. Christmas has different source identities. */
static bool projectile_gold_pulse_source(Sprite2_array bank,unsigned index)
{return projectile_gold_pulse_slot(index)>=0&&projectile91_source(bank,91);}
static bool projectile_gold_pulse_load(unsigned slot)
{
 GoldPulseResource *r=&projectile_gold_pulse_resources[slot];
 unsigned index=projectile_gold_pulse_indices[slot];
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-projectile-gold-pulse-%u-8.hda",r->root,index);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ENEMY_GOLD_PULSE*10000+index&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==projectile_gold_pulse_pins[slot];
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 r->member=(Asset){true,true,ASSET_ENEMY_GOLD_PULSE,index,12,14,0,0,8,rgba};
 return true;
}
/* Per-member root epochs; disk replacement is observed only after shutdown.
 * Revalidate every callback and every used final/cache dependency in memory. */
static Asset *projectile_gold_pulse_resource(const char *root,unsigned index)
{
 int slot=projectile_gold_pulse_slot(index);
 if(slot<0||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !root||!root[0]||strlen(root)>=sizeof(projectile_gold_pulse_resources[0].root))return NULL;
 GoldPulseResource *r=&projectile_gold_pulse_resources[slot];
 if(!r->checked) {
  r->checked=true;memcpy(r->root,root,strlen(root)+1);
  r->valid=projectile_gold_pulse_load((unsigned)slot);
 }
 if(!r->valid||strcmp(r->root,root))return NULL;
 Asset *a=&r->member;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ENEMY_GOLD_PULSE||a->index!=index||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile_gold_pulse_pins[slot]) {
  r->valid=false;return NULL;
 }
 return a;
}
/* Validate only the original selected member's actual used colors at admission.
 * Existing underlay-used and cached full-palette guards remain unchanged. */
static bool projectile_gold_pulse_palette_matches(unsigned index)
{
 if(projectile_gold_pulse_slot(index)<0)return false;
 /* Both animation frames use this same five-color native identity. A change
  * affects both, and colors123/124 also belong to the existing61 dependency. */
 static const unsigned indices[]={123,124,125,126,127};
 static const Uint32 colors[]={0xf3ae24,0xfbcb30,0xffe73c,0xfffb96,0xfffff3};
 for(unsigned i=0;i<sizeof(indices)/sizeof(*indices);i++)if((rgb_palette[indices[i]]&0xffffffu)!=colors[i])return false;
 return true;
}
