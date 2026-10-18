/* SPDX-License-Identifier: GPL-2.0-or-later
 * Actual record264 shadow preparation/epoch guards with synthetic fixtures.
 * This observer test makes no SDL/compositor or gameplay-runtime claim. */
#define main previous_adapter_main
#include "rear_multi_p1_adapter_test.c"
#undef main
#include "shadow_types.inc"
static VulcanShadowCall vulcan_shadow;
static unsigned regions[8],region_count;
static bool background2=true;
static const unsigned shadowYDist=10;
static void render_mirror_shadow_end(void){memset(&vulcan_shadow,0,sizeof vulcan_shadow);}
#include "rear_multi_p11_shadow.inc"
static const unsigned members[6]={13,14,18,17,25,26};
static bool shadow(unsigned p,unsigned slot){unsigned raw=ids[members[p]];return render_mirror_rear_p11_shadow(&surface,playerShotData[slot].shotX+1,playerShotData[slot].shotY+10,spriteSheet8,raw,slot,raw);}
static void prepare(unsigned p,unsigned slot,int d){defaults(d,full);region_count=0;background2=true;render_mirror_shadow_end();test_power=18;emit(members[p],slot);CHECK(rear_p1_state.birth[slot].qualified);}
static void check_no_write(const PlayerShotDataType *q,const Uint8 *before,unsigned slot){CHECK(!memcmp(q,playerShotData+slot,sizeof *q));CHECK(!memcmp(before,pixels,sizeof pixels));CHECK(!suppress);}
int main(int argc,char **argv){
 CHECK(argc==2);snprintf(work,sizeof work,"%s",argv[1]);snprintf(full,sizeof full,"%s/full",work);snprintf(path,sizeof path,"%s/bank.bin",work);FILE*f=fopen(path,"rb");CHECK(f);banksize=fread(originalbank,1,sizeof originalbank,f);CHECK(banksize>602&&banksize<sizeof originalbank);fclose(f);snprintf(path,sizeof path,"%s/records.bin",work);f=fopen(path,"rb");CHECK(f&&fread(recordbytes,1,sizeof recordbytes,f)==sizeof recordbytes);fclose(f);
 for(unsigned p=0;p<6;p++)for(unsigned slot=0;slot<80;slot++)for(int d=4;d<=8;d+=4){
  prepare(p,slot,d);PlayerShotDataType q=playerShotData[slot];Uint8 before[64000];memcpy(before,pixels,sizeof before);uint64_t seal=rear_p1_state.birth_identity[slot];CHECK(shadow(p,slot)==(d==8));check_no_write(&q,before,slot);CHECK(seal==rear_p1_state.birth_identity[slot]);
  if(d==8){CHECK(vulcan_shadow.live&&!vulcan_shadow.entered&&vulcan_shadow.rear&&vulcan_shadow.slot==slot&&vulcan_shadow.index==ids[members[p]]&&vulcan_shadow.birth_identity==seal);CHECK(rear_p11_shadow_birth(&vulcan_shadow));CHECK(rear_p11_shadow_current(&vulcan_shadow,&surface,101,110,spriteSheet8,ids[members[p]]));}
  render_mirror_shadow_end();CHECK(checked_head(members[p],slot));
 }
 for(unsigned p=0;p<6;p++)for(unsigned kind=0;kind<27;kind++){
  prepare(p,0,8);unsigned raw=ids[members[p]],index=raw,slot=0;int x0=101,y0=110;Sprite2_array bank=spriteSheet8;const char*root=game_probe_assets;Asset*a=rear_p1_asset(raw);CHECK(a);Asset saved=*a;Uint8 byte0=a->rgba[0];unsigned off=bank.data[2*(raw-1)]|((unsigned)bank.data[2*(raw-1)+1]<<8);Uint8 original=bank.data[off+1];
  if(kind==0)slot=80;
  if(kind==1)slot=UINT_MAX;
  if(kind==2)index++;
  if(kind==3)raw+=1000;
  if(kind==4)x0--;
  if(kind==5)y0--;
  if(kind==6)x0=-1;
  if(kind==7)x0=309;
  if(kind==8)y0=190;
  if(kind==9)background2=false;
  if(kind==10)lvlFileNum=15;
  if(kind==11)game_probe_assets="other-root";
  if(kind==12)game_probe_density=4;
  if(kind==13)game_probe_missing=true;
  if(kind==14)game_probe_invalid=true;
  if(kind==15)game_probe_original_reference=true;
  if(kind==16)game_probe_scene_assets=0;
  if(kind==17)region_count=8;
  if(kind==18)playerShotData[0].shotXM++;
  if(kind==19)rear_p1_state.birth_identity[0]^=1;
  if(kind==20)rear_p1_state.birth[0].record=1264;
  if(kind==21)bank.data[off+1]^=1;
  if(kind==22)weapons[264].attack[7]^=1;
  if(kind==23)weaponPort[10].op[0][10]++;
  if(kind==24)a->anchor_x=1;
  if(kind==25)a->rgba[0]^=1;
  if(kind==26)bank.data=originalbank;
  PlayerShotDataType q=playerShotData[0];Uint8 before[64000];memcpy(before,pixels,sizeof before);CHECK(!render_mirror_rear_p11_shadow(&surface,x0,y0,bank,index,slot,raw));check_no_write(&q,before,0);CHECK(!vulcan_shadow.live);
  a->rgba[0]=byte0;*a=saved;spriteSheet8.data[off+1]=original;game_probe_assets=root;
 }
 /* Every earlier route/source remains outside the new shadow role, including
  * shared277/278. Birth identity and its admitted old normal head survive. */
 static const unsigned old[]={254,265,255,266,267,256,257,268,269,258,259,270,260,271,261,272,262,273,263,274,275};
 for(unsigned i=0;i<sizeof old/sizeof *old;i++)for(unsigned p=0;p<weapons[old[i]].max;p++){
  defaults(8,full);unsigned record=old[i],raw=weapons[record].sg[p],k=(unsigned)rear_p1_observed(raw);CHECK(k<27);make_shot(k,0);unsigned mode=record>=265,power0=mode?record-265:record-254;
  (render_mirror_rear_p1_call_begin)(10,1,power0,mode,1,record);uint64_t c=render_mirror_rear_p1_create_begin(10,1,record,1);(render_mirror_rear_p1_emit)(c,1,0,10,1,record,1,p+1,raw);render_mirror_rear_p1_create_end(c);uint64_t seal=rear_p1_state.birth_identity[0];CHECK(!render_mirror_rear_p11_shadow(&surface,101,110,spriteSheet8,raw,0,raw));CHECK(seal==rear_p1_state.birth_identity[0]);if(rear_p1_member(raw)>=0)CHECK(checked_head(k,0));
 }
 /* Final drawn counter0 is legitimate: the original move decremented it
  * before drawing. Switching current equipment must retain that old birth. */
 for(unsigned p=0;p<6;p++){
  prepare(p,0,8);shotAvail[0]=0;(render_mirror_rear_p1_call_begin)(10,1,10,1,1,275);render_mirror_rear_p1_call_end();CHECK(shadow(p,0));VulcanShadowCall v=vulcan_shadow;rear_p1_reset(&rear_p1_state);CHECK(!rear_p11_shadow_birth(&v)&&!rear_p11_shadow_current(&v,&surface,101,110,spriteSheet8,ids[members[p]]));
 }
 rear_p1_shutdown();printf("Record264 shadow preparation PASS: %u checks; all6 phases/all80slots, d4fallback,27 negative families,21 older routes, retained births and reset epochs; synthetic only\n",checks);return 0;
}
