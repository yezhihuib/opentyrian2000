/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional normal bank8/145 enemy-only art. No weapon/gameplay mutations.
 * Used only by the finite shared91/145 owner at internal density8. */
static struct {bool checked,valid,frame_checked,drew;uint64_t checked_tick,drawn_tick;char root[1024];Asset member;} projectile145_resources;
/* Generated left-down master, contained by the original39 occupied cells. */
#include "current_projectile145_payload_pins.h"
static const uint64_t projectile145_rgba_pin=CURRENT_PROJECTILE145_PAYLOAD_FNV;
static void projectile145_shutdown(void)
{
 free(projectile145_resources.member.rgba);
 memset(&projectile145_resources,0,sizeof(projectile145_resources));
 
}
/* The original bank identity is shared, but the selected enemy role is not.
 * Authenticate the complete normal bank through the unchanged91 source guard;
 * this does not request91's optional payload or gray palette. */
static bool projectile145_source(Sprite2_array bank,unsigned index)
{return index==145&&projectile91_source(bank,91);}
static bool projectile145_load(void)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/enemy-projectile145-145-8.hda",projectile145_resources.root);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok) {
  for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==ASSET_ENEMY_PROJECTILE145*10000+145&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];
 }
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&
  asteroid1_stamp(rgba,bytes)==projectile145_rgba_pin;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 projectile145_resources.member=(Asset){true,true,ASSET_ENEMY_PROJECTILE145,145,12,14,0,0,8,rgba};
 return true;
}
/* One optional resource, independent from every enemy body family. Missing,
 * corrupt or foreign data fails only this role for the selected-root epoch.
 * A disk replacement becomes visible only after renderer cache shutdown. */
static bool projectile145_ready_at(const char *root)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !root||!root[0]||strlen(root)>=sizeof(projectile145_resources.root))return false;
 if(!projectile145_resources.checked) {
  projectile145_resources.checked=true;
  memcpy(projectile145_resources.root,root,strlen(root)+1);
  projectile145_resources.valid=projectile145_load();
 }
 if(!projectile145_resources.valid||strcmp(projectile145_resources.root,root))return false;
 /* Validate every callback: in-frame mutation must never reuse a warm lease. */
 Asset *a=&projectile145_resources.member;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ENEMY_PROJECTILE145||a->index!=145||
  a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile145_rgba_pin) {
  projectile145_resources.valid=false;return false;
 }
 projectile145_resources.checked_tick=mirror_logic_tick;projectile145_resources.frame_checked=true;
 return true;
}
static Asset *projectile145_resource(const char *root)
{return projectile145_ready_at(root)?&projectile145_resources.member:NULL;}
static bool projectile145_palette_matches(void)
{
 static const unsigned indices[]={49,84,85,86,87,88,89,91,93,95};
 static const Uint32 colors[]={0x000c14,0x30243c,0x3c2c45,0x493851,0x55415d,0x614d69,0x715971,0x967d92,0xc7b2ba,0xf7ebeb};
 for(unsigned i=0;i<sizeof(indices)/sizeof(*indices);i++)if((rgb_palette[indices[i]]&0xffffffu)!=colors[i])return false;
 return true;
}
