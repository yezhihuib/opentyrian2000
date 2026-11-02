#include "current_tank_shell_payload_pins.h"
/* Exact existing role122 materials; two independent ordinary leases.
 * Uses the established shared RGBA compositor and common checked I/O helpers. */
static const struct {unsigned index,identity;const char *sha;uint64_t payload;} enemy_tank_shared_specs[2]={
 {146u,1220146u,CURRENT_TANK_SHELL_1220146_HDA_SHA256,CURRENT_TANK_SHELL_1220146_PAYLOAD_FNV},
 {147u,1220147u,CURRENT_TANK_SHELL_1220147_HDA_SHA256,CURRENT_TANK_SHELL_1220147_PAYLOAD_FNV},
};
static struct {bool checked,valid;char root[1024];Asset member;} enemy_tank_shared_resources[2];
static int enemy_tank_shared_member(unsigned index)
{for(unsigned i=0;i<2;i++)if(enemy_tank_shared_specs[i].index==index)return (int)i;return -1;}
static void enemy_tank_shared_shutdown(void)
{for(unsigned i=0;i<2;i++)free(enemy_tank_shared_resources[i].member.rgba);memset(enemy_tank_shared_resources,0,sizeof(enemy_tank_shared_resources));}
static bool enemy_tank_shared_source(Sprite2_array bank,unsigned index)
{return tank_shared_ordinary_allowed(index)&&projectile91_source(bank,91);}
static bool enemy_tank_shared_palette_matches(unsigned index)
{
 if(index==146){
  static const unsigned indices[11]={49,84,85,86,87,88,89,90,91,93,95};
  static const Uint32 colors[11]={0x000c14,0x30243c,0x3c2c45,0x493851,0x55415d,0x614d69,0x715971,0x7d657d,0x967d92,0xc7b2ba,0xf7ebeb};
  for(unsigned n=0;n<11;n++)if((rgb_palette[indices[n]]&0xffffffu)!=colors[n])return false;return true;}
 if(index==147){
  static const unsigned indices[10]={49,84,85,86,87,88,89,91,93,95};
  static const Uint32 colors[10]={0x000c14,0x30243c,0x3c2c45,0x493851,0x55415d,0x614d69,0x715971,0x967d92,0xc7b2ba,0xf7ebeb};
  for(unsigned n=0;n<10;n++)if((rgb_palette[indices[n]]&0xffffffu)!=colors[n])return false;return true;}
 return false;
}
static bool enemy_tank_shared_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/content/%s.hda",enemy_tank_shared_resources[k].root,enemy_tank_shared_specs[k].sha);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==enemy_tank_shared_specs[k].identity&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==enemy_tank_shared_specs[k].payload;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 enemy_tank_shared_resources[k].member=(Asset){true,true,enemy_tank_shared_specs[k].identity/10000u,enemy_tank_shared_specs[k].index,12,14,0,0,8,rgba};return true;
}
static Asset *enemy_tank_shared_resource(const char *root,unsigned index)
{
 int k=enemy_tank_shared_member(index);
 if(k<0||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||!root||!root[0]||strlen(root)>=sizeof(enemy_tank_shared_resources[k].root))return NULL;
 if(!enemy_tank_shared_resources[k].checked){enemy_tank_shared_resources[k].checked=true;memcpy(enemy_tank_shared_resources[k].root,root,strlen(root)+1);enemy_tank_shared_resources[k].valid=enemy_tank_shared_load((unsigned)k);}
 if(!enemy_tank_shared_resources[k].valid||strcmp(enemy_tank_shared_resources[k].root,root))return NULL;
 Asset *a=&enemy_tank_shared_resources[k].member;
 if(!a->initialized||!a->valid||a->bank!=enemy_tank_shared_specs[k].identity/10000u||a->index!=index||a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=enemy_tank_shared_specs[k].payload){enemy_tank_shared_resources[k].valid=false;return NULL;}
 return a;
}
