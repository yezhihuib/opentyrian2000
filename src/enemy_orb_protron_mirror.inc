#include "current_enemy_orb_payload_pins.h"
#include "current_protron_payload_pins.h"
/* Exact pre-existing materials; physical source bank8 is independent of material identity. */
static const struct {unsigned index,identity;const char *sha;uint64_t payload;} enemy_orb_protron_specs[4]={
 {112u,1420112u,"84546804885d7c602449fe0c4783d1873e60f30a8abde3e3095356fc3d8bd720",CURRENT_ENEMY_ORB_1420112_PAYLOAD_FNV},
 {113u,1420113u,"20a9b6480d91a324a4ca375e79f596504103a80f165512fa33d8c5ffeeac7fba",CURRENT_ENEMY_ORB_1420113_PAYLOAD_FNV},
 {226u,80226u,"231a78b2ebc6a2410da297d05703b4c548f38926e7bd6e6b28c4fe6c4fa7071c",CURRENT_PROTRON_80226_D8_PAYLOAD_FNV},
 {227u,1470227u,"9de332ec5d8d7f5c0e7eb56445aabebe22897b27a6fde1ee7f36da822076aac7",CURRENT_PROTRON_1470227_D8_PAYLOAD_FNV},
};
static struct {bool checked,valid;char root[1024];Asset member;} enemy_orb_protron_resources[4];
static int enemy_orb_protron_member(unsigned index)
{for(unsigned i=0;i<4;i++)if(enemy_orb_protron_specs[i].index==index)return (int)i;return -1;}
static void enemy_orb_protron_shutdown(void)
{for(unsigned i=0;i<4;i++)free(enemy_orb_protron_resources[i].member.rgba);memset(enemy_orb_protron_resources,0,sizeof(enemy_orb_protron_resources));}
static bool enemy_orb_protron_source(Sprite2_array bank,unsigned index)
{return orb_protron_member_index(index)&&orb_protron_ordinary_allowed(index)&&projectile91_source(bank,91);}
static bool enemy_orb_protron_palette_matches(unsigned index)
{
 if(index==112){
  static const unsigned indices[10]={112,114,117,118,119,121,122,123,124,127};
  static const Uint32 colors[10]={0x200000,0x510000,0x9e0800,0xba0c00,0xd31400,0xe7610c,0xeb8a18,0xf3ae24,0xfbcb30,0xfffff3};
  for(unsigned n=0;n<10;n++)if((rgb_palette[indices[n]]&0xffffffu)!=colors[n])return false;return true;}
 if(index==113){
  static const unsigned indices[10]={112,115,116,120,121,122,124,125,126,127};
  static const Uint32 colors[10]={0x200000,0x6d0400,0x860400,0xdf3c00,0xe7610c,0xeb8a18,0xfbcb30,0xffe73c,0xfffb96,0xfffff3};
  for(unsigned n=0;n<10;n++)if((rgb_palette[indices[n]]&0xffffffu)!=colors[n])return false;return true;}
 if(index==226){
  static const unsigned indices[8]={132,134,135,136,137,138,140,143};
  static const Uint32 colors[8]={0x4d8292,0x619aa6,0x6da6b2,0x7db2ba,0x8abec7,0x9acbcf,0xbadfe3,0xefffff};
  for(unsigned n=0;n<8;n++)if((rgb_palette[indices[n]]&0xffffffu)!=colors[n])return false;return true;}
 if(index==227){
  static const unsigned indices[12]={129,130,131,132,133,134,135,137,138,139,141,143};
  static const Uint32 colors[12]={0x2c5d75,0x38697d,0x41758a,0x4d8292,0x558e9e,0x619aa6,0x6da6b2,0x8abec7,0x9acbcf,0xa6d3d7,0xcbebeb,0xefffff};
  for(unsigned n=0;n<12;n++)if((rgb_palette[indices[n]]&0xffffffu)!=colors[n])return false;return true;}
 return false;
}
static bool enemy_orb_protron_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/content/%s.hda",enemy_orb_protron_resources[k].root,enemy_orb_protron_specs[k].sha);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==enemy_orb_protron_specs[k].identity&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==enemy_orb_protron_specs[k].payload;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 enemy_orb_protron_resources[k].member=(Asset){true,true,enemy_orb_protron_specs[k].identity/10000u,enemy_orb_protron_specs[k].index,12,14,0,0,8,rgba};return true;
}
static Asset *enemy_orb_protron_resource(const char *root,unsigned index)
{
 int k=enemy_orb_protron_member(index);
 if(k<0||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||!root||!root[0]||strlen(root)>=sizeof(enemy_orb_protron_resources[k].root))return NULL;
 if(!enemy_orb_protron_resources[k].checked){enemy_orb_protron_resources[k].checked=true;memcpy(enemy_orb_protron_resources[k].root,root,strlen(root)+1);enemy_orb_protron_resources[k].valid=enemy_orb_protron_load((unsigned)k);}
 if(!enemy_orb_protron_resources[k].valid||strcmp(enemy_orb_protron_resources[k].root,root))return NULL;
 Asset *a=&enemy_orb_protron_resources[k].member;
 if(!a->initialized||!a->valid||a->bank!=enemy_orb_protron_specs[k].identity/10000u||a->index!=index||a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=enemy_orb_protron_specs[k].payload){enemy_orb_protron_resources[k].valid=false;return NULL;}
 return a;
}
