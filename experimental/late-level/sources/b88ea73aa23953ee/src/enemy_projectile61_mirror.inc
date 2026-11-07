/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional normal bank8/61 enemy-only art. No weapon/gameplay mutations.
 * Used only by the finite shared91/145 owner at internal density8. */
static struct {bool checked,valid,frame_checked,drew;uint64_t checked_tick,drawn_tick;char root[1024];Asset member;} projectile61_resources;
/* Generated parallel downward energy lobes, contained by the original74 occupied cells. */
#include "current_projectile61_payload_pins.h"
static const uint64_t projectile61_rgba_pin=CURRENT_PROJECTILE61_PAYLOAD_FNV;
static void projectile61_shutdown(void)
{
 free(projectile61_resources.member.rgba);
 memset(&projectile61_resources,0,sizeof(projectile61_resources));
 
}
/* The original bank identity is shared, but the selected enemy role is not.
 * Authenticate the complete normal bank through the unchanged91 source guard;
 * this does not request91's optional payload or gray palette. */
static bool projectile61_source(Sprite2_array bank,unsigned index)
{return index==61&&projectile91_source(bank,91);}
static bool projectile61_load(void)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-projectile61-61-8.hda",projectile61_resources.root);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ENEMY_PROJECTILE61*10000+61&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==projectile61_rgba_pin;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 projectile61_resources.member=(Asset){true,true,ASSET_ENEMY_PROJECTILE61,61,12,14,0,0,8,rgba};
 return true;
}
/* One optional resource, independent from every enemy body family. Missing,
 * corrupt or foreign data fails only this role for the selected-root epoch.
 * A disk replacement becomes visible only after renderer cache shutdown. */
static bool projectile61_ready_at(const char *root)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !root||!root[0]||strlen(root)>=sizeof(projectile61_resources.root))return false;
 if(!projectile61_resources.checked) {
  projectile61_resources.checked=true;
  memcpy(projectile61_resources.root,root,strlen(root)+1);
  projectile61_resources.valid=projectile61_load();
 }
 if(!projectile61_resources.valid||strcmp(projectile61_resources.root,root))return false;
 /* Validate every callback: in-frame mutation must never reuse a warm lease. */
 Asset *a=&projectile61_resources.member;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ENEMY_PROJECTILE61||a->index!=61||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile61_rgba_pin) {
  projectile61_resources.valid=false;return false;
 }
 projectile61_resources.checked_tick=mirror_logic_tick;projectile61_resources.frame_checked=true;
 return true;
}
static Asset *projectile61_resource(const char *root)
{return projectile61_ready_at(root)?&projectile61_resources.member:NULL;}
static bool projectile61_palette_matches(void)
{
 static const unsigned indices[]={113,114,115,116,117,118,119,120,121,122,123,124};
 static const Uint32 colors[]={0x380000,0x510000,0x6d0400,0x860400,0x9e0800,0xba0c00,0xd31400,0xdf3c00,0xe7610c,0xeb8a18,0xf3ae24,0xfbcb30};
 for(unsigned i=0;i<sizeof(indices)/sizeof(*indices);i++)if((rgb_palette[indices[i]]&0xffffffu)!=colors[i])return false;
 return true;
}
