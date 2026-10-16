/* Synthetic and private-authentic harness share these actual adapter checks.
 * No original record bytes or decoded art are embedded in public tests. */
static unsigned p4m2_member(unsigned p)
{static const unsigned members[5]={11,12,10,9,8};return members[p-1];}
static bool p4m2_drawable(unsigned p){return p>=3;}
static bool p4m2_expected(unsigned p,int d){return p==5||(p>=3&&d==8);}
static void p4m2_emit(uint64_t c,unsigned n,unsigned slot,unsigned p)
{unsigned k=p4m2_member(p);make_shot(k,slot);(render_mirror_rear_p1_emit)(c,n,slot,10,1,268,1,p,ids[k]);}
static void p4m2_check(unsigned slot,unsigned p,int d)
{
 CHECK(rear_p1_state.birth[slot].qualified==p4m2_drawable(p));
 if(p4m2_drawable(p))CHECK(rear_p1_state.birth[slot].record==268&&rear_p1_state.birth[slot].mode==2&&rear_p1_state.birth[slot].phase==p);
 else {RearP1Birth zero={0};CHECK(!memcmp(&rear_p1_state.birth[slot],&zero,sizeof zero));}
 unsigned before=role_opens;CHECK(checked_head(p4m2_member(p),slot)==p4m2_expected(p,d));
 if(!p4m2_expected(p,d))CHECK(role_opens==before);
}
static void test_p4_mode2_actual_allocations(void)
{
 unsigned coverage[5][5]={{0}};
 for(int d=4;d<=8;d+=4)for(unsigned start=0;start<=5;start++)for(unsigned prior=0;prior<5;prior++)for(unsigned cap=0;cap<=6;cap++) {
  defaults(d,full);allocation_defaults(0,start);for(unsigned i=0;i<prior;i++)shotAvail[40+i]=0;
  compare_create(10,268,3,1,true);unsigned phase=start;
  for(unsigned i=0;i<prior;i++){phase=phase==5?1:phase+1;p4m2_check(40+i,phase,d);}
  CHECK(shotMultiPos[1]==phase);unsigned previous=phase;
  memset(shotAvail,1,sizeof shotAvail);for(unsigned i=0;i<cap;i++)shotAvail[10+i]=0;
  compare_create(10,268,3,1,true);unsigned count=cap<5?cap:5;
  for(unsigned i=0;i<count;i++){phase=phase==5?1:phase+1;coverage[phase-1][i]++;p4m2_check(10+i,phase,d);}
  CHECK(shotMultiPos[1]==phase&&!rear_p1_state.birth[15].qualified);
  /* All retained new births are checked against their own record and mode. */
  for(unsigned power_index=0;power_index<12;power_index++)for(unsigned mode=0;mode<2;mode++) {
   (render_mirror_rear_p1_call_begin)(10,1,power_index,mode,1,(mode?265:254)+power_index);render_mirror_rear_p1_call_end();
   for(unsigned i=0;i<count;i++)p4m2_check(10+i,(previous+i)%5+1,d);
  }
  phase=start;for(unsigned i=0;i<prior;i++){phase=phase==5?1:phase+1;p4m2_check(40+i,phase,d);}
  memset(shotAvail,1,sizeof shotAvail);for(unsigned i=0;i<5;i++)shotAvail[10+i]=0;
  compare_create(10,268,3,1,false);for(unsigned i=0;i<5;i++)CHECK(!rear_p1_state.birth[10+i].qualified);
 }
 for(unsigned p=0;p<5;p++)for(unsigned n=0;n<5;n++)CHECK(coverage[p][n]>0);
 /* A failed-power call allocates nothing and must not clear an existing birth. */
 defaults(8,full);allocation_defaults(5,0);compare_create(10,268,3,1,true);
 RearP1Birth before[REAR_P1_SLOTS];memcpy(before,rear_p1_state.birth,sizeof before);
 allocation_defaults(5,0);power=39;compare_create(10,268,3,1,true);CHECK(!memcmp(before,rear_p1_state.birth,sizeof before));
 for(unsigned kind=0;kind<4;kind++) {
  defaults(8,full);allocation_defaults(5,0);if(kind==0)power=39;
  compare_create(kind==1?PORT_NUM+1:10,kind==2?0:kind==3?WEAP_NUM+1:268,3,1,true);
  for(unsigned i=0;i<80;i++)CHECK(!rear_p1_state.birth[i].qualified);
 }
 /* Real allocator slot80 is still gameplay-owned and cancels only the grant. */
 for(unsigned start=0;start<5;start++)for(unsigned valid=0;valid<5;valid++) {
  defaults(8,full);allocation_defaults(0,start);for(unsigned i=80-valid;i<=80;i++)shotAvail[i]=0;
  compare_create(10,268,3,1,true);
  for(unsigned i=0;i<valid;i++)p4m2_check(80-valid+i,(start+i)%5+1,8);
  CHECK(shotAvail[80]==255&&shotMultiPos[1]==(start+valid)%5+1);
 }
 /* Recycle all five old mode1 births with mode2, including its pass-throughs. */
 for(unsigned start=0;start<5;start++) {
  defaults(8,full);allocation_defaults(5,0);compare_create(10,257,3,0,true);
  allocation_defaults(5,start);compare_create(10,268,3,1,true);
  for(unsigned i=0;i<5;i++)p4m2_check(i,(start+i)%5+1,8);
 }
 const unsigned excluded[]={258,259,269,270,271,272,275,1268,1257,50,51,81,445,501,502,686,687,688,689,690};
 for(unsigned i=0;i<sizeof excluded/sizeof *excluded;i++)for(unsigned mode=0;mode<2;mode++) {
  defaults(8,full);weapons[excluded[i]]=weapons[268];allocation_defaults(5,0);compare_create(10,excluded[i],3,mode,true);
  CHECK(!rear_p1_table(excluded[i]));for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 for(unsigned p=0;p<12;p++)for(unsigned mode=0;mode<2;mode++)if(p!=3||mode!=1) {
  defaults(8,full);allocation_defaults(5,0);compare_create(10,268,p,mode,true);for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 const unsigned ports[]={0,2,19,22,27,32,36,37,60};
 for(unsigned i=0;i<sizeof ports/sizeof *ports;i++) {
  defaults(8,full);allocation_defaults(5,0);compare_create(ports[i],268,3,1,true);for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 /* New map gate is local to record268. Every old table gate stays independent. */
 const unsigned oldrecords[]={254,265,255,266,267,256,257};
 defaults(8,full);weaponPort[10].op[1][3]++;CHECK(!rear_p1_table(268));
 for(unsigned i=0;i<sizeof oldrecords/sizeof *oldrecords;i++)CHECK(rear_p1_table(oldrecords[i]));
 for(unsigned i=0;i<sizeof oldrecords/sizeof *oldrecords;i++) {
  unsigned r=oldrecords[i],k=r==256?6:r==257?8:r>=265?2:0;
  test_power=r==257?3:r==256||r==267?2:r==255||r==266?1:0;defaults(8,full);emit(k,0);CHECK(checked_head(k,0));
  weaponPort[10].op[1][3]++;CHECK(checked_head(k,0));weapons[268].attack[7]^=1;CHECK(checked_head(k,0));
 }
 test_power=1;
}
static void test_p4_mode2_adapter_protocol(void)
{
 for(unsigned start=1;start<=5;start++)for(unsigned bad=1;bad<=5;bad++)for(unsigned kind=0;kind<23;kind++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,3,1,1,268);uint64_t c=render_mirror_rear_p1_create_begin(10,1,268,1);
  for(unsigned n=1;n<bad;n++){unsigned p=p4_phase(start,n);p4m2_emit(c,n,n,p);p4m2_check(n,p,8);}
  unsigned phase=p4_phase(start,bad),k=p4m2_member(phase),slot=kind==2?80:kind==3?UINT_MAX:kind==17?81:bad;make_shot(k,bad);
  unsigned off=bankdata[2*(ids[k]-1)]|((unsigned)bankdata[2*(ids[k]-1)+1]<<8);
  if(kind==0)bankdata[off+1]^=1;
  if(kind==1)playerShotData[bad].shotXM++;
  if(kind==4)weapons[268].attack[7]^=1;
  if(kind==5)weaponPort[10].op[1][3]++;
  if(kind==6)twoPlayerMode=1;
  if(kind==7)mirror_logic_tick++;
  if(kind==16)active=false;
  (render_mirror_rear_p1_emit)(kind==8?c+1:kind==20?0:c,kind==9?bad+1:kind==21?0:bad,slot,kind==10?37:10,kind==11?0:1,kind==12?257:268,kind==13?2:1,kind==14?0:kind==18?6:kind==19?(phase%5+1):phase,kind==15?0:kind==22?ids[k]+1000:ids[k]);
  if(kind==0)bankdata[off+1]^=1;
  if(kind==4)weapons[268].attack[7]^=1;
  if(kind==5)weaponPort[10].op[1][3]--;
  if(kind==6)twoPlayerMode=0;
  if(kind==7)mirror_logic_tick--;
  if(kind==16)active=true;
  CHECK(!rear_p1_state.remaining&&!rear_p1_state.lease&&!rear_p1_state.call&&!rear_p1_state.birth[bad].qualified);
  for(unsigned n=1;n<bad;n++)p4m2_check(n,p4_phase(start,n),8);
  for(unsigned n=bad+1;n<=6;n++){p4m2_emit(c,n,n,p4_phase(start,n));CHECK(!rear_p1_state.birth[n].qualified);}
 }
 for(unsigned start=1;start<=5;start++)for(unsigned bad=2;bad<=6;bad++)for(unsigned reused=1;reused<bad;reused++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,3,1,1,268);uint64_t c=render_mirror_rear_p1_create_begin(10,1,268,1);
  for(unsigned n=1;n<bad;n++)p4m2_emit(c,n,n,p4_phase(start,n));
  p4m2_emit(c,bad,reused,p4_phase(start,bad));CHECK(!rear_p1_state.birth[reused].qualified&&!rear_p1_state.remaining);
  for(unsigned n=1;n<bad;n++)if(n!=reused)p4m2_check(n,p4_phase(start,n),8);
  for(unsigned n=bad+1;n<=7;n++){p4m2_emit(c,n,n,p4_phase(start,n));CHECK(!rear_p1_state.birth[n].qualified);}
 }
 /* Pass-throughs must consume every protocol field at every original ordinal. */
 for(unsigned start=1;start<=5;start++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,3,1,1,268);uint64_t c=render_mirror_rear_p1_create_begin(10,1,268,1);
  for(unsigned n=1;n<=5;n++) {
   unsigned p=p4_phase(start,n);p4m2_emit(c,n,n,p);p4m2_check(n,p,8);
   CHECK(rear_p1_state.remaining==5-n&&rear_p1_state.next_ordinal==n+1&&rear_p1_state.next_phase==p%5+1&&rear_p1_state.used_count==n&&rear_p1_state.used_slots[n-1]==n&&rear_p1_state.lease==(n<5));
  }
 }
 /* Exact 80-byte pins reject cold emissions even when the phase is pass-through. */
 for(unsigned p=1;p<=5;p++)for(unsigned b=0;b<80;b++) {
  defaults(8,full);Uint8 altered[80];memcpy(altered,recordbytes+560,80);altered[b]^=1;parse_record(&weapons[268],altered);
  CHECK(!rear_p1_table(268));(render_mirror_rear_p1_call_begin)(10,1,3,1,1,268);uint64_t c=render_mirror_rear_p1_create_begin(10,1,268,1);
  p4m2_emit(c,1,0,p);CHECK(!rear_p1_state.birth[0].qualified&&!rear_p1_state.lease&&!rear_p1_state.remaining);
 }
}
static void test_p4_mode2_resources(void)
{
 test_power=4;
 for(int d=4;d<=8;d+=4)for(unsigned p=1;p<=5;p++) {
  unsigned k=p4m2_member(p);defaults(d,full);emit(k,0);
  unsigned opens=role_opens,oldblits=blits,oldends=ends,oldprobes=probes,oldgenerics=generics;PlayerShotDataType saved=playerShotData[0];Uint8 before[64000];memcpy(before,pixels,sizeof before);
  draw_player_shot_sprite2(&surface,101,100,spriteSheet8,ids[k],0,ids[k]);
  bool expected=p4m2_expected(p,d);
  CHECK(last_mirrored==expected&&generics==oldgenerics+(unsigned)!expected&&blits==oldblits+1&&ends==oldends+1&&probes==oldprobes+1&&!suppress);
  CHECK(!memcmp(before,pixels,sizeof before)&&!memcmp(&saved,&playerShotData[0],sizeof saved));
  if(!expected)CHECK(role_opens==opens);
  if(p<=2) {
   CHECK(!rear_p1_state.birth[0].qualified&&rear_p1_member(ids[k])<0&&rear_p1_observed(ids[k])>=0);
   CHECK(!rear_p1_asset(ids[k]));Asset fake={true,false,ASSET_REAR_MULTI_P1,(int)ids[k],12,14,0,0,d,NULL};CHECK(!rear_p1_load(&fake,d));CHECK(role_opens==opens);
   /* Even a fabricated canonical-looking pass-through birth is revoked. */
   rear_p1_state.birth[0]=(RearP1Birth){true,268,2,p,ids[k],rear_p1_state.generation};
   CHECK(!checked_head(k,0)&&!rear_p1_state.birth[0].qualified&&role_opens==opens);
   for(unsigned m=0;m<REAR_P1_HEADS;m++)for(unsigned di=0;di<2;di++)CHECK(!rear_p1_resources.cache[m][di].attempted);
  }
  if((p==3||p==4)&&d==4) {
   CHECK(!rear_p1_resources.cache[k][0].attempted&&!rear_p1_resources.cache[k][1].attempted);
   Asset fake={true,false,ASSET_REAR_MULTI_P1,(int)ids[k],12,14,0,0,4,NULL};CHECK(!rear_p1_load(&fake,4));CHECK(role_opens==opens);
  }
 }
 /* Warm 77 remains valid through mode changes, using the owning birth record. */
 defaults(8,full);test_power=3;emit(8,0);CHECK(checked_head(8,0));test_power=4;emit(8,1);CHECK(checked_head(8,1));
 weapons[268].attack[7]^=1;CHECK(checked_head(8,0));CHECK(!checked_head(8,1));weapons[268].attack[7]^=1;CHECK(!checked_head(8,1));emit(8,1);
 weapons[257].attack[7]^=1;CHECK(checked_head(8,1));CHECK(!checked_head(8,0));weapons[257].attack[7]^=1;CHECK(!checked_head(8,0));
 /* Missing or corrupt new d8 never borrows any supplied d4 file. */
 for(unsigned k=9;k<=10;k++)for(unsigned kind=0;kind<2;kind++) {
  snprintf(path,sizeof path,"%s/%u-8-%s",work,ids[k],kind?"payload":"missing");defaults(8,path);emit(k,0);
  unsigned opens=role_opens;CHECK(!checked_head(k,0)&&role_opens==opens+1);CHECK(!checked_head(k,0)&&role_opens==opens+1);
  CHECK(rear_p1_resources.cache[k][1].attempted&&!rear_p1_resources.cache[k][0].attempted);
 }
 test_power=1;
}
