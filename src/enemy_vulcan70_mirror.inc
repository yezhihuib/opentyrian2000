/* SPDX-License-Identifier: GPL-2.0-or-later
 * Enemy-only normal bank8/70 admission of exact canonical player asset80070.
 * No new artwork/encoding/namespace; no player role/cache or collision changes.
 * The independent lease never calls the player front-weapon witness gate.
 */
static struct {bool checked,valid;char root[1024];Asset member;} enemy_vulcan70_resource_state;
static const uint64_t enemy_vulcan70_payload_pin=UINT64_C(0x6c26e938d94472c2);
static void enemy_vulcan70_shutdown(void)
{
 free(enemy_vulcan70_resource_state.member.rgba);
 memset(&enemy_vulcan70_resource_state,0,sizeof(enemy_vulcan70_resource_state));
}
static bool enemy_vulcan70_source(Sprite2_array bank,unsigned index)
{return index==70&&projectile91_source(bank,91);}
/* All and only original70's used indices. Static canonical color contract;
 * admission requires the actual live palette, never an assumed scene number.
 * Any incompatible palette remains classic, including before a fade. */
static bool enemy_vulcan70_palette_matches(void)
{
 static const Uint32 colors[12]={0x380000,0x510000,0x6d0400,0x860400,0x9e0800,0xba0c00,
  0xd31400,0xdf3c00,0xe7610c,0xeb8a18,0xf3ae24,0xfbcb30};
 for(unsigned i=0;i<12;i++)if((rgb_palette[113+i]&0xffffffu)!=colors[i])return false;
 return true;
}
static bool enemy_vulcan70_load(void)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/content/eebd525dab58f0fc6708f4f3c7b15a88e67270be877ff250e93c4bb2a2aeb8de.hda",enemy_vulcan70_resource_state.root);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==80070&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==enemy_vulcan70_payload_pin;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 enemy_vulcan70_resource_state.member=(Asset){true,true,8,70,12,14,0,0,8,rgba};
 return true;
}
/* Same-root disk replacement requires shutdown, as for the other finite enemy
 * leases. Used in-memory identity/geometry/payload is checked every callback,
 * finish and cache proof. This owns a separate allocation from player Vulcan. */
static Asset *enemy_vulcan70_resource(const char *root)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||
  !root||!root[0]||strlen(root)>=sizeof(enemy_vulcan70_resource_state.root))return NULL;
 if(!enemy_vulcan70_resource_state.checked){enemy_vulcan70_resource_state.checked=true;
  memcpy(enemy_vulcan70_resource_state.root,root,strlen(root)+1);enemy_vulcan70_resource_state.valid=enemy_vulcan70_load();}
 if(!enemy_vulcan70_resource_state.valid||strcmp(enemy_vulcan70_resource_state.root,root))return NULL;
 Asset *a=&enemy_vulcan70_resource_state.member;
 if(!a->initialized||!a->valid||a->bank!=8||a->index!=70||a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=enemy_vulcan70_payload_pin){enemy_vulcan70_resource_state.valid=false;return NULL;}
 return a;
}
