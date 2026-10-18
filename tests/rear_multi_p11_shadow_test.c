/* SPDX-License-Identifier: GPL-2.0-or-later
 * Actual record254/255/256/257/258/259/260/261/262/263/264/265/266/267/268/269/270/271/272/273/274/275 shadow preparation/epoch guards with synthetic fixtures.
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
typedef struct {unsigned record,power,power_index,mode_index,offset,count,member[8];} ShadowRole;
static const ShadowRole roles[]={
 {264,18,10,0,1680,6,{13,14,18,17,25,26}},
 {275,17,10,1,1600,8,{13,14,20,19,21,22,6,7}},
 {263,15,9,0,1440,6,{13,14,18,17,23,24}},
 {274,16,9,1,1520,8,{13,14,20,19,21,22,0,1}},
 {262,13,8,0,1280,6,{13,14,18,17,15,16}},
 {273,14,8,1,1360,7,{13,14,20,19,8,21,22}},
 {261,11,7,0,1120,6,{13,14,18,17,0,1}},
 {272,12,7,1,1200,7,{13,14,20,19,8,0,1}},
 {260,9,6,0,960,4,{13,14,18,17}},
 {271,10,6,1,1040,5,{13,14,20,19,8}},
 {259,7,5,0,800,3,{15,16,8}},
 {270,8,5,1,880,5,{13,14,10,9,8}},
 {258,6,4,0,720,2,{15,16}},
 {269,5,4,1,640,4,{13,14,10,9}},
 {257,3,3,0,480,5,{2,3,4,5,8}},
 {268,4,3,1,560,3,{10,9,8}},
 {256,2,2,0,400,2,{6,7}},
 {267,2,2,1,320,4,{2,3,4,5}},
 {254,0,0,0,0,2,{0,1}},
 {265,0,0,1,80,4,{2,3,4,5}},
 {255,1,1,0,160,2,{0,1}},
 {266,1,1,1,240,4,{2,3,4,5}}
};
static bool shadow(const ShadowRole*r,unsigned p,unsigned slot){unsigned raw=ids[r->member[p]];return render_mirror_rear_p11_shadow(&surface,playerShotData[slot].shotX+1,playerShotData[slot].shotY+10,spriteSheet8,raw,slot,raw);}
static void prepare(const ShadowRole*r,unsigned p,unsigned slot,int d){defaults(d,full);region_count=0;background2=true;render_mirror_shadow_end();test_power=r->power;emit(r->member[p],slot);CHECK(rear_p1_state.birth[slot].qualified);}
static void check_no_write(const PlayerShotDataType*q,const Uint8*before,unsigned slot){CHECK(!memcmp(q,playerShotData+slot,sizeof *q));CHECK(!memcmp(before,pixels,sizeof pixels));}
static void test_phases(void){
 for(unsigned role=0;role<sizeof roles/sizeof *roles;role++){
  const ShadowRole*r=roles+role;
  for(unsigned p=0;p<r->count;p++)for(unsigned slot=0;slot<80;slot++)for(int d=4;d<=8;d+=4){
   prepare(r,p,slot,d);PlayerShotDataType q=playerShotData[slot];Uint8 before[64000];memcpy(before,pixels,sizeof before);uint64_t seal=rear_p1_state.birth_identity[slot];CHECK(shadow(r,p,slot)==(d==8));check_no_write(&q,before,slot);CHECK(!suppress&&seal==rear_p1_state.birth_identity[slot]);
   if(d==8){CHECK(vulcan_shadow.live&&!vulcan_shadow.entered&&vulcan_shadow.rear&&vulcan_shadow.slot==slot&&vulcan_shadow.index==ids[r->member[p]]&&vulcan_shadow.birth_identity==seal);CHECK(rear_p11_shadow_birth(&vulcan_shadow));CHECK(rear_p11_shadow_current(&vulcan_shadow,&surface,101,110,spriteSheet8,ids[r->member[p]]));}
   render_mirror_shadow_end();CHECK(checked_head(r->member[p],slot)==(d==8||(r->member[p]!=9&&r->member[p]!=10)));
  }
 }
}
static void test_negatives(void){
 for(unsigned role=0;role<sizeof roles/sizeof *roles;role++){
  const ShadowRole*r=roles+role;
  for(unsigned p=0;p<r->count;p++)for(unsigned kind=0;kind<96;kind++){
   prepare(r,p,0,8);unsigned raw=ids[r->member[p]],index=raw,slot=0;int x0=101,y0=110;Sprite2_array bank=spriteSheet8;const char*root=game_probe_assets;Asset*a=rear_p1_asset(raw);CHECK(a);Asset saved=*a;Uint8 byte0=a->rgba[0];unsigned off=bank.data[2*(raw-1)]|((unsigned)bank.data[2*(raw-1)+1]<<8);Uint8 original=bank.data[off+1];
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
   if(kind==20)rear_p1_state.birth[0].record=r->record+1000;
   if(kind==21)bank.data[off+1]^=1;
   if(kind==22)weapons[r->record].attack[7]^=1;
   if(kind==23)weaponPort[10].op[r->mode_index][r->power_index]++;
   if(kind==24)a->anchor_x=1;
   if(kind==25)a->rgba[0]^=1;
   if(kind==26)bank.data=originalbank;
   if(kind==27)rear_p1_state.birth[0].phase++;
   if(kind==28)rear_p1_state.birth[0].mode^=3;
   if(kind==29)rear_p1_state.birth[0].generation++;
   if(kind==30)rear_p1_state.birth[0].record=roles[role^1].record;
   if(kind==31)rear_p1_state.birth[0].qualified=false;
   if(kind==32)episodeNum=2;
   if(kind==33)initialDifficulty=DIFFICULTY_HARD;
   if(kind==34)xmas=1;
   if(kind==35)isNetworkGame=1;
   if(kind==36)twoPlayerMode=1;
   if(kind==37)twoPlayerLinked=1;
   if(kind==38)galagaMode=1;
   if(kind==39)play_demo=1;
   if(kind==40)record_demo=1;
   if(kind==41)onePlayerAction=1;
   if(kind==42)superTyrian=1;
   if(kind==43)superArcadeMode=1;
   if(kind==44)timedBattleMode=1;
   if(kind==45)bonusLevel=1;
   if(kind==46)normalBonusLevelCurrent=1;
   if(kind==47)bonusLevelCurrent=1;
   if(kind==48)active=false;
   if(kind==49)reject_reason="rejected";
   if(kind==50)suppress=true;
   if(kind==51)game_screen=NULL;
   if(kind==52)VGAScreen=NULL;
   if(kind==53)surface.pixels=NULL;
   if(kind==54)surface.format=NULL;
   if(kind==55)surface.w=319;
   if(kind==56)surface.h=199;
   if(kind==57)fmt.format=SDL_PIXELFORMAT_ARGB8888;
   if(kind==58)fmt.BitsPerPixel=32;
   if(kind==59)fmt.BytesPerPixel=4;
   if(kind==60)surface.pitch=319;
   if(kind==61)surface.pitch=INT_MAX;
   if(kind==62)canvas=NULL;
   if(kind==63)csurface.pixels=NULL;
   if(kind==64)csurface.format=NULL;
   if(kind==65)cfmt.format=SDL_PIXELFORMAT_INDEX8;
   if(kind==66)cfmt.BitsPerPixel=8;
   if(kind==67)cfmt.BytesPerPixel=1;
   if(kind==68)csurface.w--;
   if(kind==69)csurface.h--;
   if(kind==70)csurface.pitch--;
   if(kind==71)csurface.pitch=INT_MAX;
   if(kind==72)hd_owner=NULL;
   if(kind==73)cloud_owner=NULL;
   if(kind==74)green_first=NULL;
   if(kind==75)green_under=NULL;
   if(kind==76)green_under_owner=NULL;
   if(kind==77)csurface.pixels=(Uint8*)canvasstorage+1;
   if(kind==78)csurface.pixels=pixels;
   if(kind==79)bank.size--;
   if(kind==80)bank.data=NULL;
   if(kind==81)a->bank++;
   if(kind==82)a->index++;
   if(kind==83)a->w++;
   if(kind==84)a->h++;
   if(kind==85)a->anchor_y++;
   if(kind==86)a->density=4;
   if(kind==87)a->valid=false;
   if(kind==88)a->initialized=false;
   if(kind==89)a->rgba=NULL;
   if(kind==90)playerShotData[0].shotAni=1;
   if(kind==91)playerShotData[0].playerNumber=2;
   if(kind==92)playerShotData[0].shotTrail=0;
   if(kind==93)playerShotData[0].shotBlastFilter=0;
   if(kind==94)playerShotData[0].shotYM++;
   if(kind==95){lvlFileNum=15;initialDifficulty=DIFFICULTY_HARD;}
   PlayerShotDataType q=playerShotData[0];Uint8 before[64000];memcpy(before,pixels,sizeof before);bool was_suppress=suppress;CHECK(!render_mirror_rear_p11_shadow(&surface,x0,y0,bank,index,slot,raw));check_no_write(&q,before,0);CHECK(suppress==was_suppress&&!vulcan_shadow.live);
   *a=saved;a->rgba[0]=byte0;spriteSheet8.data[off+1]=original;game_probe_assets=root;
  }
  /* Every serialized byte, including inactive tails, participates in admission. */
  for(unsigned p=0;p<r->count;p++)for(unsigned byte_index=0;byte_index<80;byte_index++){
   prepare(r,p,0,8);Uint8 bytes[80];memcpy(bytes,recordbytes+r->offset,sizeof bytes);bytes[byte_index]^=1;parse_record(&weapons[r->record],bytes);CHECK(!shadow(r,p,0));CHECK(!vulcan_shadow.live);
  }
  static const char*bad[] = {"missing","empty","magic","key","density","w","h","ax","ay","short","trunc","extra","payload","fifo","directory","device"};
  for(unsigned p=0;p<r->count;p++)for(unsigned kind=0;kind<sizeof bad/sizeof *bad;kind++){
   char malformed[4096];snprintf(malformed,sizeof malformed,"%s/%u-8-%s",work,ids[r->member[p]],bad[kind]);defaults(8,malformed);test_power=r->power;emit(r->member[p],0);CHECK(rear_p1_state.birth[0].qualified);region_count=0;background2=true;CHECK(!shadow(r,p,0));CHECK(!vulcan_shadow.live);
  }
 }
}
static void test_observed_pass_throughs(void){
 /* SECOND268 phases1/2 consume the five-observation call without a rear
  * birth or alpha. The existing generic head/shadow paths retain these raws.
  * Exercise every cyclic start and slot without inventing a dedicated asset. */
 static const unsigned member[]={11,12,10,9,8};
 for(unsigned start=0;start<5;start++)for(unsigned first=0;first<80;first++){
  defaults(8,full);region_count=0;background2=true;render_mirror_shadow_end();
  (render_mirror_rear_p1_call_begin)(10,1,3,1,1,268);uint64_t c=render_mirror_rear_p1_create_begin(10,1,268,1);
  for(unsigned n=0;n<5;n++){
   unsigned p=(start+n)%5,k=member[p],slot=(first+n)%80;make_shot(k,slot);
   (render_mirror_rear_p1_emit)(c,n+1,slot,10,1,268,1,p+1,ids[k]);
   CHECK(rear_p1_state.remaining==4-n&&rear_p1_state.used_count==n+1&&rear_p1_state.next_ordinal==n+2&&rear_p1_state.next_phase==(p+1)%5+1&&rear_p1_state.lease==(n<4));
   CHECK(rear_p1_state.birth[slot].qualified==(p>=2));
   PlayerShotDataType q=playerShotData[slot];Uint8 before[64000];memcpy(before,pixels,sizeof before);uint64_t seal=rear_p1_state.birth_identity[slot];
   CHECK(render_mirror_rear_p11_shadow(&surface,101,110,spriteSheet8,ids[k],slot,ids[k])==(p>=2));check_no_write(&q,before,slot);CHECK(seal==rear_p1_state.birth_identity[slot]);
   if(p<2){CHECK(!seal&&!vulcan_shadow.live&&rear_p1_member(ids[k])<0&&!rear_p1_asset(ids[k]));CHECK(!checked_head(k,slot));}
   render_mirror_shadow_end();
  }
  render_mirror_rear_p1_create_end(c);render_mirror_rear_p1_call_end();CHECK(!rear_p1_state.lease&&!rear_p1_state.pending);
 }
}
static void test_p2_cyclic_observations(void){
 /* P2 emits exactly two allocations per call. SECOND266 still cycles over
  * four phases, including 4->1, and continues the cycle across calls.
  * Exercise genuine ordinal/phase sequences, never independent four-shot calls. */
 for(unsigned role=sizeof roles/sizeof *roles-2;role<sizeof roles/sizeof *roles;role++){
  const ShadowRole*r=roles+role;
  for(unsigned start=0;start<r->count;start++)for(unsigned first=0;first<80;first++)for(int d=4;d<=8;d+=4){
   defaults(d,full);region_count=0;background2=true;render_mirror_shadow_end();
   for(unsigned invocation=0;invocation<2;invocation++){
    (render_mirror_rear_p1_call_begin)(10,1,1,r->mode_index,1,r->record);CHECK(rear_p1_state.pending&&rear_p1_state.budget==2);
    uint64_t c=render_mirror_rear_p1_create_begin(10,1,r->record,1);CHECK(rear_p1_state.lease&&rear_p1_state.remaining==2&&!rear_p1_state.used_count&&rear_p1_state.next_ordinal==1&&!rear_p1_state.next_phase);
    uint64_t seals[2];
    for(unsigned n=0;n<2;n++){
     unsigned p=(start+2*invocation+n)%r->count,k=r->member[p],slot=(first+2*invocation+n)%80;make_shot(k,slot);
     (render_mirror_rear_p1_emit)(c,n+1,slot,10,1,r->record,1,p+1,ids[k]);
     CHECK(rear_p1_state.remaining==1-n&&rear_p1_state.used_count==n+1&&rear_p1_state.next_ordinal==n+2&&rear_p1_state.next_phase==(p+1)%r->count+1&&rear_p1_state.lease==(n==0));
     CHECK(rear_p1_state.birth[slot].qualified&&rear_p1_state.birth[slot].record==r->record&&rear_p1_state.birth[slot].mode==r->mode_index+1&&rear_p1_state.birth[slot].phase==p+1);
     seals[n]=rear_p1_state.birth_identity[slot];CHECK(seals[n]);
     PlayerShotDataType q=playerShotData[slot];Uint8 before[64000];memcpy(before,pixels,sizeof before);CHECK(shadow(r,p,slot)==(d==8));check_no_write(&q,before,slot);CHECK(seals[n]==rear_p1_state.birth_identity[slot]);render_mirror_shadow_end();CHECK(checked_head(k,slot));
    }
    /* A third observation cannot enlarge the two-allocation lease. */
    unsigned p=(start+2*invocation+2)%r->count,k=r->member[p],slot=(first+2*invocation+2)%80;make_shot(k,slot);
    (render_mirror_rear_p1_emit)(c,3,slot,10,1,r->record,1,p+1,ids[k]);CHECK(!rear_p1_state.lease&&!rear_p1_state.remaining&&!rear_p1_state.birth[slot].qualified&&!rear_p1_state.birth_identity[slot]);CHECK(!shadow(r,p,slot)&&!vulcan_shadow.live);CHECK(!checked_head(k,slot));
    for(unsigned n=0;n<2;n++){p=(start+2*invocation+n)%r->count;slot=(first+2*invocation+n)%80;CHECK(seals[n]==rear_p1_state.birth_identity[slot]);CHECK(shadow(r,p,slot)==(d==8));render_mirror_shadow_end();}
    render_mirror_rear_p1_create_end(c);render_mirror_rear_p1_call_end();CHECK(!rear_p1_state.lease&&!rear_p1_state.pending);
   }
  }
 }
}
static void test_p2_actual_allocations(void){
 /* The actual unmodified allocator and its observer-stripped baseline must
  * agree for partial/full capacity and every original cyclic start. */
 for(unsigned mode=0;mode<2;mode++){
  const ShadowRole*r=roles+sizeof roles/sizeof *roles-2+mode;
  for(unsigned start=0;start<=r->count;start++)for(unsigned free_slots=0;free_slots<4;free_slots++)for(int d=4;d<=8;d+=4){
   defaults(d,full);region_count=0;background2=true;render_mirror_shadow_end();allocation_defaults(free_slots,start);compare_create(10,r->record,1,mode,true);
   unsigned phase=start,n=free_slots<2?free_slots:2;
   for(unsigned slot=0;slot<n;slot++){
    phase=phase==r->count?1:phase+1;CHECK(rear_p1_state.birth[slot].qualified&&rear_p1_state.birth[slot].phase==phase&&rear_p1_state.birth[slot].record==r->record);CHECK(shadow(r,phase-1,slot)==(d==8));render_mirror_shadow_end();CHECK(checked_head(r->member[phase-1],slot));
   }
   for(unsigned slot=n;slot<80;slot++)CHECK(!rear_p1_state.birth[slot].qualified);
  }
 }
}
static void test_p1_cyclic_observations(void){
 /* P1 grants one native allocation per independent call. Accumulate a full
  * period over two/four calls; never enlarge either lease to its period. */
 for(unsigned role=sizeof roles/sizeof *roles-4;role<sizeof roles/sizeof *roles-2;role++){
  const ShadowRole*r=roles+role;
  for(unsigned start=0;start<r->count;start++)for(unsigned first=0;first<80;first++)for(int d=4;d<=8;d+=4){
   defaults(d,full);region_count=0;background2=true;render_mirror_shadow_end();CHECK(weapons[r->record].multi==1&&weapons[r->record].max==r->count);
   uint64_t seals[4]={0},previous_call=0;
   for(unsigned invocation=0;invocation<r->count;invocation++){
    (render_mirror_rear_p1_call_begin)(10,1,0,r->mode_index,1,r->record);CHECK(rear_p1_state.pending&&rear_p1_state.budget==1);
    uint64_t c=render_mirror_rear_p1_create_begin(10,1,r->record,1);CHECK(c&&c!=previous_call);previous_call=c;CHECK(rear_p1_state.lease&&rear_p1_state.remaining==1&&!rear_p1_state.used_count&&rear_p1_state.next_ordinal==1&&!rear_p1_state.next_phase);
    unsigned p=(start+invocation)%r->count,k=r->member[p],slot=(first+invocation)%80;make_shot(k,slot);
    (render_mirror_rear_p1_emit)(c,1,slot,10,1,r->record,1,p+1,ids[k]);
    CHECK(!rear_p1_state.remaining&&rear_p1_state.used_count==1&&rear_p1_state.next_ordinal==2&&rear_p1_state.next_phase==(p+1)%r->count+1&&!rear_p1_state.lease);
    CHECK(rear_p1_state.birth[slot].qualified&&rear_p1_state.birth[slot].record==r->record&&rear_p1_state.birth[slot].mode==r->mode_index+1&&rear_p1_state.birth[slot].phase==p+1);
    seals[invocation]=rear_p1_state.birth_identity[slot];CHECK(seals[invocation]);
    PlayerShotDataType q=playerShotData[slot];Uint8 before[64000];memcpy(before,pixels,sizeof before);CHECK(shadow(r,p,slot)==(d==8));check_no_write(&q,before,slot);CHECK(seals[invocation]==rear_p1_state.birth_identity[slot]);render_mirror_shadow_end();CHECK(checked_head(k,slot));
    /* A second observation cannot enlarge the single-allocation lease. */
    p=(start+invocation+1)%r->count;k=r->member[p];slot=(first+r->count+invocation)%80;make_shot(k,slot);
    (render_mirror_rear_p1_emit)(c,2,slot,10,1,r->record,1,p+1,ids[k]);CHECK(!rear_p1_state.lease&&!rear_p1_state.remaining&&!rear_p1_state.birth[slot].qualified&&!rear_p1_state.birth_identity[slot]);CHECK(!shadow(r,p,slot)&&!vulcan_shadow.live);CHECK(!checked_head(k,slot));
    for(unsigned n=0;n<=invocation;n++){p=(start+n)%r->count;slot=(first+n)%80;CHECK(seals[n]==rear_p1_state.birth_identity[slot]);CHECK(shadow(r,p,slot)==(d==8));render_mirror_shadow_end();}
    render_mirror_rear_p1_create_end(c);render_mirror_rear_p1_call_end();CHECK(!rear_p1_state.lease&&!rear_p1_state.pending);mirror_logic_tick++;
   }
  }
 }
}
static void test_p1_actual_allocations(void){
 /* Actual untouched allocator/baseline pairs cover every native cursor,
  * capacity0/1/2/3 and full cyclic continuation on independent calls. */
 for(unsigned mode=0;mode<2;mode++){
  const ShadowRole*r=roles+sizeof roles/sizeof *roles-4+mode;
  for(unsigned start=0;start<=r->count;start++)for(unsigned free_slots=0;free_slots<4;free_slots++)for(int d=4;d<=8;d+=4){
   defaults(d,full);region_count=0;background2=true;render_mirror_shadow_end();allocation_defaults(free_slots,start);CHECK(weapons[r->record].multi==1&&weapons[r->record].max==r->count);
   unsigned phase=start,phases[5]={0};
   for(unsigned invocation=0;invocation<=r->count;invocation++){
    if(invocation){memset(shotAvail,1,sizeof shotAvail);shotAvail[invocation]=0;mirror_logic_tick++;}
    compare_create(10,r->record,0,mode,true);
    if(invocation||free_slots){phase=phase==r->count?1:phase+1;phases[invocation]=phase;}
    CHECK(shotMultiPos[1]==phase);
    for(unsigned slot=0;slot<80;slot++){
     bool born=slot<5&&phases[slot];CHECK(rear_p1_state.birth[slot].qualified==born);
     if(born){unsigned p=phases[slot]-1;CHECK(rear_p1_state.birth[slot].phase==p+1&&rear_p1_state.birth[slot].record==r->record);CHECK(shadow(r,p,slot)==(d==8));render_mirror_shadow_end();CHECK(checked_head(r->member[p],slot));}
    }
   }
  }
 }
}
static void test_preservation(void){
 /* Every shared raw retains its original sealed physical record and mode.
  * P1 now receives the same full admission/negative guards as the old20. */
 for(unsigned role=0;role<sizeof roles/sizeof *roles;role++){
  const ShadowRole*r=roles+role;
  for(unsigned p=0;p<r->count;p++){
   /* A byte-identical physical alias cannot obtain the original route lease. */
   defaults(8,full);weapons[r->record+1000]=weapons[r->record];make_shot(r->member[p],0);(render_mirror_rear_p1_call_begin)(10,1,r->power_index,r->mode_index,1,r->record+1000);uint64_t c=render_mirror_rear_p1_create_begin(10,1,r->record+1000,1);(render_mirror_rear_p1_emit)(c,1,0,10,1,r->record+1000,1,p+1,ids[r->member[p]]);render_mirror_rear_p1_create_end(c);CHECK(!shadow(r,p,0));
   /* Final drawn counter0 and a current equipment switch retain the old birth. */
   prepare(r,p,0,8);shotAvail[0]=0;(render_mirror_rear_p1_call_begin)(10,1,r->power_index,roles[role^1].mode_index,1,roles[role^1].record);render_mirror_rear_p1_call_end();CHECK(shadow(r,p,0));VulcanShadowCall v=vulcan_shadow;rear_p1_reset(&rear_p1_state);CHECK(!rear_p11_shadow_birth(&v)&&!rear_p11_shadow_current(&v,&surface,101,110,spriteSheet8,ids[r->member[p]]));
   prepare(r,p,0,8);CHECK(shadow(r,p,0));v=vulcan_shadow;v.rear=false;CHECK(!rear_p11_shadow_birth(&v));v=vulcan_shadow;v.slot=80;CHECK(!rear_p11_shadow_birth(&v));
   /* Physical record pins remain independent. The original P1/P2 selector
    * gates are shared prerequisites, even for retained higher-power births. */
   for(unsigned other=0;other<sizeof roles/sizeof *roles;other++)if(other!=role){
    prepare(r,p,0,8);rear_p1_state.birth[0].record=roles[other].record;CHECK(!shadow(r,p,0));
    if(roles[other].power_index<=1){prepare(r,p,0,8);weapons[roles[other].record].attack[7]^=1;CHECK(shadow(r,p,0));}
    prepare(r,p,0,8);weapons[roles[other].record].attack[7]^=1;weaponPort[10].op[roles[other].mode_index][roles[other].power_index]++;CHECK(shadow(r,p,0)==(roles[other].power_index>1));
   }
   /* Opposite-mode records stay independent; mutating either original P1/P2
    * selector must still fail the shared table admission for those births. */
   prepare(r,p,0,8);weapons[roles[role^1].record].attack[7]^=1;weaponPort[10].op[roles[role^1].mode_index][r->power_index]++;CHECK(shadow(r,p,0)==(r->power_index>1));
  }
 }
}
int main(int argc,char**argv){
 CHECK(argc==2);snprintf(work,sizeof work,"%s",argv[1]);snprintf(full,sizeof full,"%s/full",work);snprintf(path,sizeof path,"%s/bank.bin",work);FILE*f=fopen(path,"rb");CHECK(f);banksize=fread(originalbank,1,sizeof originalbank,f);CHECK(banksize>602&&banksize<sizeof originalbank);fclose(f);snprintf(path,sizeof path,"%s/records.bin",work);f=fopen(path,"rb");CHECK(f&&fread(recordbytes,1,sizeof recordbytes,f)==sizeof recordbytes);fclose(f);
 test_phases();test_negatives();test_observed_pass_throughs();test_p2_cyclic_observations();test_p2_actual_allocations();test_p1_cyclic_observations();test_p1_actual_allocations();test_preservation();rear_p1_shutdown();printf("Record254/255/256/257/258/259/260/261/262/263/264/265/266/267/268/269/270/271/272/273/274/275 shadow preparation PASS: %u checks; all103 phases/all80slots, d4/Hard fallback,96 negative families/full80 bytes/16 malformed resources,all22 roles,P1 exact1-allocation independent cyclic calls/actual allocator baseline,P2 exact2-allocation cyclic observations/actual allocator baseline,268 observed-only cyclic pass-throughs, aliases, retained births and reset epochs; synthetic only\n",checks);return 0;
}
