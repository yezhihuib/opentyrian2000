/* Controlled synthetic/private-original-data qualification; not an ordinary
 * P5 acquisition or gameplay witness. The allocator itself is actual source. */
static bool test_member(unsigned power,unsigned k)
{
 if(power==8)return k==13||k==14||k==10||k==9||k==8;
 if(power==7)return k==15||k==16||k==8;
 if(power<2)return k<6;
 if(power==2)return k>=2&&k<8;
 if(power==3)return (k>=2&&k<6)||k==8;
 if(power==4)return k>=8&&k<=10;
 return (power==5&&(k==9||k==10||k==13||k==14))||(power==6&&(k==15||k==16));
}
static unsigned p5m2_member(unsigned p)
{static const unsigned members[4]={13,14,10,9};return members[p-1];}
static unsigned p5m2_phase(unsigned start,unsigned n){return (start+n-2)%4+1;}
static bool p5m2_expected(unsigned p,int d){return p<=2||d==8;}
static void p5m2_emit(uint64_t c,unsigned n,unsigned slot,unsigned p)
{unsigned k=p5m2_member(p);make_shot(k,slot);(render_mirror_rear_p1_emit)(c,n,slot,10,1,269,1,p,ids[k]);}
static void p5m2_check(unsigned slot,unsigned p,int d)
{
 CHECK(rear_p1_state.birth[slot].qualified&&rear_p1_state.birth[slot].record==269&&rear_p1_state.birth[slot].mode==2&&rear_p1_state.birth[slot].phase==p);
 unsigned before=role_opens;CHECK(checked_head(p5m2_member(p),slot)==p5m2_expected(p,d));
 if(!p5m2_expected(p,d))CHECK(role_opens==before);
}
static void test_p5_mode2_actual_allocations(void)
{
 unsigned coverage[4][4]={{0}};
 for(int d=4;d<=8;d+=4)for(unsigned start=0;start<=4;start++)for(unsigned prior=0;prior<4;prior++)for(unsigned cap=0;cap<=5;cap++) {
  defaults(d,full);allocation_defaults(0,start);for(unsigned i=0;i<prior;i++)shotAvail[40+i]=0;
  compare_create(10,269,4,1,true);unsigned phase=start;
  for(unsigned i=0;i<prior;i++){phase=phase==4?1:phase+1;p5m2_check(40+i,phase,d);}
  CHECK(shotMultiPos[1]==phase);unsigned previous=phase;
  memset(shotAvail,1,sizeof shotAvail);for(unsigned i=0;i<cap;i++)shotAvail[10+i]=0;
  compare_create(10,269,4,1,true);unsigned count=cap<4?cap:4;
  for(unsigned i=0;i<count;i++){phase=phase==4?1:phase+1;coverage[phase-1][i]++;p5m2_check(10+i,phase,d);}
  CHECK(shotMultiPos[1]==phase&&!rear_p1_state.birth[14].qualified);
  for(unsigned power_index=0;power_index<12;power_index++)for(unsigned mode=0;mode<2;mode++) {
   (render_mirror_rear_p1_call_begin)(10,1,power_index,mode,1,(mode?265:254)+power_index);render_mirror_rear_p1_call_end();
   for(unsigned i=0;i<count;i++)p5m2_check(10+i,(previous+i)%4+1,d);
  }
  phase=start;for(unsigned i=0;i<prior;i++){phase=phase==4?1:phase+1;p5m2_check(40+i,phase,d);}
  memset(shotAvail,1,sizeof shotAvail);for(unsigned i=0;i<4;i++)shotAvail[10+i]=0;
  compare_create(10,269,4,1,false);for(unsigned i=0;i<4;i++)CHECK(!rear_p1_state.birth[10+i].qualified);
 }
 for(unsigned p=0;p<4;p++)for(unsigned n=0;n<4;n++)CHECK(coverage[p][n]>0);
 defaults(8,full);allocation_defaults(4,0);compare_create(10,269,4,1,true);
 RearP1Birth before[REAR_P1_SLOTS];memcpy(before,rear_p1_state.birth,sizeof before);
 allocation_defaults(4,0);power=39;compare_create(10,269,4,1,true);CHECK(!memcmp(before,rear_p1_state.birth,sizeof before));
 for(unsigned kind=0;kind<4;kind++) {
  defaults(8,full);allocation_defaults(4,0);if(kind==0)power=39;
  compare_create(kind==1?PORT_NUM+1:10,kind==2?0:kind==3?WEAP_NUM+1:269,4,1,true);
  for(unsigned i=0;i<80;i++)CHECK(!rear_p1_state.birth[i].qualified);
 }
 for(unsigned start=0;start<4;start++)for(unsigned valid=0;valid<4;valid++) {
  defaults(8,full);allocation_defaults(0,start);for(unsigned i=80-valid;i<=80;i++)shotAvail[i]=0;
  compare_create(10,269,4,1,true);
  for(unsigned i=0;i<valid;i++)p5m2_check(80-valid+i,(start+i)%4+1,8);
  CHECK(shotAvail[80]==255&&shotMultiPos[1]==(start+valid)%4+1);
 }
 /* Recycle P4 pass-through and drawable slots; preserve distinct earlier births. */
 for(unsigned start=0;start<4;start++) {
  defaults(8,full);allocation_defaults(5,0);compare_create(10,268,3,1,true);
  allocation_defaults(4,start);compare_create(10,269,4,1,true);
  for(unsigned i=0;i<4;i++)p5m2_check(i,(start+i)%4+1,8);
  p4m2_check(4,5,8);
 }
 const unsigned excluded[]={258,259,260,261,262,263,264,268,270,271,272,273,274,275,1269,52,51,81,90,445,502,504,505,686};
 for(unsigned i=0;i<sizeof excluded/sizeof *excluded;i++)for(unsigned mode=0;mode<2;mode++) {
  defaults(8,full);weapons[excluded[i]]=weapons[269];allocation_defaults(4,0);compare_create(10,excluded[i],4,mode,true);
  CHECK(!rear_p1_table(excluded[i]));for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 for(unsigned p=0;p<12;p++)for(unsigned mode=0;mode<2;mode++)if(p!=4||mode!=1) {
  defaults(8,full);allocation_defaults(4,0);compare_create(10,269,p,mode,true);for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 const unsigned ports[]={0,2,19,22,27,32,36,37,60};
 for(unsigned i=0;i<sizeof ports/sizeof *ports;i++) {
  defaults(8,full);allocation_defaults(4,0);compare_create(ports[i],269,4,1,true);for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 const unsigned oldrecords[]={254,265,255,266,267,256,257,268};
 defaults(8,full);weaponPort[10].op[1][4]++;CHECK(!rear_p1_table(269));
 for(unsigned i=0;i<sizeof oldrecords/sizeof *oldrecords;i++)CHECK(rear_p1_table(oldrecords[i]));
 for(unsigned i=0;i<sizeof oldrecords/sizeof *oldrecords;i++) {
  unsigned r=oldrecords[i],k=r==256?6:r==257||r==268?8:r>=265?2:0;
  test_power=r==268?4:r==257?3:r==256||r==267?2:r==255||r==266?1:0;defaults(8,full);emit(k,0);CHECK(checked_head(k,0));
  weaponPort[10].op[1][4]++;CHECK(checked_head(k,0));weapons[269].attack[7]^=1;CHECK(checked_head(k,0));
 }
 test_power=1;
}
static void test_p5_mode2_adapter_protocol(void)
{
 for(unsigned start=1;start<=4;start++)for(unsigned bad=1;bad<=4;bad++)for(unsigned kind=0;kind<23;kind++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,4,1,1,269);uint64_t c=render_mirror_rear_p1_create_begin(10,1,269,1);
  for(unsigned n=1;n<bad;n++){unsigned p=p5m2_phase(start,n);p5m2_emit(c,n,n,p);p5m2_check(n,p,8);}
  unsigned phase=p5m2_phase(start,bad),k=p5m2_member(phase),slot=kind==2?80:kind==3?UINT_MAX:kind==17?81:bad;make_shot(k,bad);
  unsigned off=bankdata[2*(ids[k]-1)]|((unsigned)bankdata[2*(ids[k]-1)+1]<<8);
  if(kind==0)bankdata[off+1]^=1;
  if(kind==1)playerShotData[bad].shotXM++;
  if(kind==4)weapons[269].attack[7]^=1;
  if(kind==5)weaponPort[10].op[1][4]++;
  if(kind==6)twoPlayerMode=1;
  if(kind==7)mirror_logic_tick++;
  if(kind==16)active=false;
  (render_mirror_rear_p1_emit)(kind==8?c+1:kind==20?0:c,kind==9?bad+1:kind==21?0:bad,slot,kind==10?37:10,kind==11?0:1,kind==12?268:269,kind==13?2:1,kind==14?0:kind==18?5:kind==19?(phase%4+1):phase,kind==15?0:kind==22?ids[k]+1000:ids[k]);
  if(kind==0)bankdata[off+1]^=1;
  if(kind==4)weapons[269].attack[7]^=1;
  if(kind==5)weaponPort[10].op[1][4]--;
  if(kind==6)twoPlayerMode=0;
  if(kind==7)mirror_logic_tick--;
  if(kind==16)active=true;
  CHECK(!rear_p1_state.remaining&&!rear_p1_state.lease&&!rear_p1_state.call&&!rear_p1_state.birth[bad].qualified);
  for(unsigned n=1;n<bad;n++)p5m2_check(n,p5m2_phase(start,n),8);
  for(unsigned n=bad+1;n<=6;n++){p5m2_emit(c,n,n,p5m2_phase(start,n));CHECK(!rear_p1_state.birth[n].qualified);}
 }
 for(unsigned start=1;start<=4;start++)for(unsigned bad=2;bad<=5;bad++)for(unsigned reused=1;reused<bad;reused++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,4,1,1,269);uint64_t c=render_mirror_rear_p1_create_begin(10,1,269,1);
  for(unsigned n=1;n<bad;n++)p5m2_emit(c,n,n,p5m2_phase(start,n));
  p5m2_emit(c,bad,reused,p5m2_phase(start,bad));CHECK(!rear_p1_state.birth[reused].qualified&&!rear_p1_state.remaining);
  for(unsigned n=1;n<bad;n++)if(n!=reused)p5m2_check(n,p5m2_phase(start,n),8);
  for(unsigned n=bad+1;n<=7;n++){p5m2_emit(c,n,n,p5m2_phase(start,n));CHECK(!rear_p1_state.birth[n].qualified);}
 }
 for(unsigned start=1;start<=4;start++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,4,1,1,269);uint64_t c=render_mirror_rear_p1_create_begin(10,1,269,1);
  for(unsigned n=1;n<=4;n++) {
   unsigned p=p5m2_phase(start,n);p5m2_emit(c,n,n,p);p5m2_check(n,p,8);
   CHECK(rear_p1_state.remaining==4-n&&rear_p1_state.next_ordinal==n+1&&rear_p1_state.next_phase==p%4+1&&rear_p1_state.used_count==n&&rear_p1_state.used_slots[n-1]==n&&rear_p1_state.lease==(n<4));
  }
  p5m2_emit(c,5,5,start);CHECK(!rear_p1_state.birth[5].qualified&&!rear_p1_state.remaining);
  for(unsigned n=1;n<=4;n++)p5m2_check(n,p5m2_phase(start,n),8);
 }
 for(unsigned p=1;p<=4;p++)for(unsigned b=0;b<80;b++) {
  defaults(8,full);Uint8 altered[80];memcpy(altered,recordbytes+640,80);altered[b]^=1;parse_record(&weapons[269],altered);
  CHECK(!rear_p1_table(269));(render_mirror_rear_p1_call_begin)(10,1,4,1,1,269);uint64_t c=render_mirror_rear_p1_create_begin(10,1,269,1);
  p5m2_emit(c,1,0,p);CHECK(!rear_p1_state.birth[0].qualified&&!rear_p1_state.lease&&!rear_p1_state.remaining);
 }
 for(unsigned start=1;start<=4;start++)for(unsigned after=0;after<=4;after++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,4,1,1,269);uint64_t c=render_mirror_rear_p1_create_begin(10,1,269,1);
  for(unsigned n=1;n<=after;n++)p5m2_emit(c,n,n,p5m2_phase(start,n));
  uint64_t inner=render_mirror_rear_p1_create_begin(10,1,269,1);CHECK(inner!=c);
  p5m2_emit(inner,1,10,start);CHECK(!rear_p1_state.birth[10].qualified);render_mirror_rear_p1_create_end(inner);
  p5m2_emit(c,after+1,11,p5m2_phase(start,after+1));CHECK(!rear_p1_state.birth[11].qualified);
  for(unsigned n=1;n<=after;n++)p5m2_check(n,p5m2_phase(start,n),8);
 }
}
static void test_p5_mode2_resources(void)
{
 test_power=5;
 for(int d=4;d<=8;d+=4)for(unsigned p=1;p<=4;p++) {
  unsigned k=p5m2_member(p);defaults(d,full);emit(k,0);
  unsigned opens=role_opens,oldblits=blits,oldends=ends,oldprobes=probes,oldgenerics=generics;PlayerShotDataType saved=playerShotData[0];Uint8 before[64000];memcpy(before,pixels,sizeof before);
  draw_player_shot_sprite2(&surface,101,100,spriteSheet8,ids[k],0,ids[k]);bool expected=p5m2_expected(p,d);
  CHECK(last_mirrored==expected&&generics==oldgenerics+(unsigned)!expected&&blits==oldblits+1&&ends==oldends+1&&probes==oldprobes+1&&!suppress);
  CHECK(!memcmp(before,pixels,sizeof before)&&!memcmp(&saved,&playerShotData[0],sizeof saved));
  if(!expected)CHECK(role_opens==opens);
  if(p>=3&&d==4) {
   CHECK(!rear_p1_resources.cache[k][0].attempted&&!rear_p1_resources.cache[k][1].attempted);
   Asset fake={true,false,ASSET_REAR_MULTI_P1,(int)ids[k],12,14,0,0,4,NULL};CHECK(!rear_p1_load(&fake,4));CHECK(role_opens==opens);
  }
 }
 /* Shared 182/183 resources retain record-specific birth ownership. */
 for(unsigned k=9;k<=10;k++) {
  defaults(8,full);test_power=4;emit(k,0);CHECK(checked_head(k,0));test_power=5;emit(k,1);CHECK(checked_head(k,1));
  weapons[269].attack[7]^=1;CHECK(checked_head(k,0));CHECK(!checked_head(k,1));weapons[269].attack[7]^=1;CHECK(!checked_head(k,1));emit(k,1);
  weapons[268].attack[7]^=1;CHECK(checked_head(k,1));CHECK(!checked_head(k,0));weapons[268].attack[7]^=1;CHECK(!checked_head(k,0));
 }
 for(unsigned p=1;p<=4;p++)for(unsigned field=0;field<13;field++)for(unsigned warm=0;warm<2;warm++) {
  defaults(8,full);unsigned k=p5m2_member(p);emit(k,0);if(warm)CHECK(checked_head(k,0));
  PlayerShotDataType *q=&playerShotData[0],saved=*q;
  switch(field) {
   case 0:q->shotGr++;break;case 1:q->shotAni++;break;case 2:q->shotAniMax++;break;case 3:q->playerNumber++;break;
   case 4:q->shotTrail--;break;case 5:q->aimAtEnemy++;break;case 6:q->chainReaction++;break;case 7:q->shotComplicated=true;break;
   case 8:q->shotBlastFilter++;break;case 9:q->shotXM++;break;case 10:q->shotYM++;break;case 11:q->shotXC++;break;default:q->shotYC++;break;
  }
  bad_restore(k,0);*q=saved;CHECK(!checked_head(k,0));
 }
 /* New twins use their separate resource indexes; generic 163/164 never do. */
 CHECK(rear_p1_member(277)==11&&rear_p1_member(278)==12&&rear_p1_observed(277)==13&&rear_p1_observed(278)==14);
 CHECK(rear_p1_member(163)<0&&rear_p1_member(164)<0);
 test_power=1;
}
