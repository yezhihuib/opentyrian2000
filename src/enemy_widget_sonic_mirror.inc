/* SPDX-License-Identifier: GPL-2.0-or-later
 * Exact existing Widget Beam20/21 and Sonic quadrants; enemy-only independent
 * leases. Content aliases are byte copies, not new artwork or player roles. */
static const struct {unsigned index;const char *sha;uint64_t payload;} enemy_widget_sonic_specs[6]={
 {20u,"328f9831389399fa7c8d623889732bbc1574dac458a30b97511e2d031dd7aed8",CURRENT_GUIDED_80020_D8_PAYLOAD_FNV},
 {21u,"a8fbcb2952ec4a4b3f84388f1b410ec70648052cbaff35487d2ed930c9b5dc55",CURRENT_GUIDED_80021_D8_PAYLOAD_FNV},
 {105u,"d12fde24b67f6b57ede3483e07a155b95cd5f538cf9f96c64e0d80fc2e0eba78",CURRENT_SONIC_80105_D8_PAYLOAD_FNV},
 {106u,"1a47b5701ecbdef673251cd1de7b975e42291cef29ab9a0bfd10f1c48facb2ba",CURRENT_SONIC_80106_D8_PAYLOAD_FNV},
 {124u,"b37e9664609365b53a250c0a711b6ae863ab55299904794051091b206aeef158",CURRENT_SONIC_80124_D8_PAYLOAD_FNV},
 {125u,"11ffdf82296ed985ec9534ba19a555eb22594c14e5fc92414531a47e36383752",CURRENT_SONIC_80125_D8_PAYLOAD_FNV}
};
static struct {bool checked,valid;char root[1024];Asset member;} enemy_widget_sonic_resources[6];
static int enemy_widget_sonic_member(unsigned index)
{for(unsigned i=0;i<6;i++)if(enemy_widget_sonic_specs[i].index==index)return (int)i;return -1;}
static void enemy_widget_sonic_shutdown(void)
{for(unsigned i=0;i<6;i++)free(enemy_widget_sonic_resources[i].member.rgba);memset(enemy_widget_sonic_resources,0,sizeof(enemy_widget_sonic_resources));}
static bool enemy_widget_sonic_source(Sprite2_array bank,unsigned index)
{return widget_sonic_member_index(index)&&!widget_sonic_legacy_intent()&&projectile91_source(bank,91);}
static bool enemy_widget_sonic_palette_matches(unsigned index)
{
 static const unsigned warm_indices[7]={118,120,121,123,125,126,127};
 static const Uint32 warm[7]={0xba0c00,0xdf3c00,0xe7610c,0xf3ae24,0xffe73c,0xfffb96,0xfffff3};
 static const Uint32 sonic[14]={0x005100,0x005d00,0x006d00,0x007d00,0x008e00,0x009a04,0x04a60c,0x08b614,0x0cc320,0x10cf30,0x18db3c,0x20e749,0x24f359,0x2cff69};
 if(index==20||index==21){for(unsigned i=0;i<7;i++)if((rgb_palette[warm_indices[i]]&0xffffffu)!=warm[i])return false;return true;}
 if(index==105||index==106||index==124||index==125){for(unsigned i=0;i<14;i++)if((rgb_palette[194+i]&0xffffffu)!=sonic[i])return false;return true;}
 return false;
}
static bool enemy_widget_sonic_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra;REAR_STAT st;
 int n=snprintf(path,sizeof(path),"%s/content/%s.hda",enemy_widget_sonic_resources[k].root,enemy_widget_sonic_specs[k].sha);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=(size_t)12*14*8*8*4;Uint8 *rgba=NULL;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&REAR_READ(fd,header,sizeof(header))==(int)sizeof(header)&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  ok=v[0]==80000u+enemy_widget_sonic_specs[k].index&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==enemy_widget_sonic_specs[k].payload;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 enemy_widget_sonic_resources[k].member=(Asset){true,true,8,enemy_widget_sonic_specs[k].index,12,14,0,0,8,rgba};return true;
}
static Asset *enemy_widget_sonic_resource(const char *root,unsigned index)
{
 int k=enemy_widget_sonic_member(index);
 if(k<0||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||!root||!root[0]||strlen(root)>=sizeof(enemy_widget_sonic_resources[k].root))return NULL;
 if(!enemy_widget_sonic_resources[k].checked){enemy_widget_sonic_resources[k].checked=true;memcpy(enemy_widget_sonic_resources[k].root,root,strlen(root)+1);enemy_widget_sonic_resources[k].valid=enemy_widget_sonic_load((unsigned)k);}
 if(!enemy_widget_sonic_resources[k].valid||strcmp(enemy_widget_sonic_resources[k].root,root))return NULL;
 Asset *a=&enemy_widget_sonic_resources[k].member;
 if(!a->initialized||!a->valid||a->bank!=8||a->index!=index||a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=enemy_widget_sonic_specs[k].payload){enemy_widget_sonic_resources[k].valid=false;return NULL;}
 return a;
}
