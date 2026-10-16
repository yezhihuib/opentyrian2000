/* Synthetic/public or private-original fixtures only. Actual allocator source,
 * controlled diagnostic qualification; no ordinary P5 acquisition claim. */
static unsigned p5m1_member(unsigned p){return p+14;}
static unsigned p5m1_phase(unsigned start,unsigned n){return (start+n-2)%2+1;}
static void p5m1_emit(uint64_t c,unsigned n,unsigned slot,unsigned p)
{unsigned k=p5m1_member(p);make_shot(k,slot);(render_mirror_rear_p1_emit)(c,n,slot,10,1,258,1,p,ids[k]);}
static void p5m1_check(unsigned slot,unsigned p)
{
 CHECK(rear_p1_state.birth[slot].qualified&&rear_p1_state.birth[slot].record==258&&rear_p1_state.birth[slot].mode==1&&rear_p1_state.birth[slot].phase==p);
 CHECK(checked_head(p5m1_member(p),slot));
}
static void test_p5_mode1_actual_allocations(void)
{
 unsigned coverage[2][2]={{0}};
 for(int d=4;d<=8;d+=4)for(unsigned start=0;start<=2;start++)for(unsigned prior=0;prior<=2;prior++)for(unsigned cap=0;cap<=5;cap++) {
  defaults(d,full);allocation_defaults(0,start);for(unsigned i=0;i<prior;i++)shotAvail[40+i]=0;
  compare_create(10,258,4,0,true);unsigned phase=start;
  for(unsigned i=0;i<prior;i++){phase=phase==2?1:phase+1;p5m1_check(40+i,phase);}
  CHECK(shotMultiPos[1]==phase);unsigned previous=phase;
  memset(shotAvail,1,sizeof shotAvail);for(unsigned i=0;i<cap;i++)shotAvail[10+i]=0;
  compare_create(10,258,4,0,true);unsigned count=cap<2?cap:2;
  for(unsigned i=0;i<count;i++){phase=phase==2?1:phase+1;coverage[phase-1][i]++;p5m1_check(10+i,phase);}
  CHECK(shotMultiPos[1]==phase&&!rear_p1_state.birth[12].qualified);
  for(unsigned power_index=0;power_index<12;power_index++)for(unsigned mode=0;mode<2;mode++) {
   (render_mirror_rear_p1_call_begin)(10,1,power_index,mode,1,(mode?265:254)+power_index);render_mirror_rear_p1_call_end();
   for(unsigned i=0;i<count;i++)p5m1_check(10+i,(previous+i)%2+1);
  }
  phase=start;for(unsigned i=0;i<prior;i++){phase=phase==2?1:phase+1;p5m1_check(40+i,phase);}
  memset(shotAvail,1,sizeof shotAvail);for(unsigned i=0;i<2;i++)shotAvail[10+i]=0;
  compare_create(10,258,4,0,false);for(unsigned i=0;i<2;i++)CHECK(!rear_p1_state.birth[10+i].qualified);
 }
 for(unsigned p=0;p<2;p++)for(unsigned n=0;n<2;n++)CHECK(coverage[p][n]>0);
 /* Insufficient power and zero capacity must preserve old non-recycled births. */
 for(unsigned kind=0;kind<2;kind++) {
  defaults(8,full);allocation_defaults(2,0);compare_create(10,258,4,0,true);
  RearP1Birth before[REAR_P1_SLOTS];memcpy(before,rear_p1_state.birth,sizeof before);
  uint64_t seals[REAR_P1_SLOTS];memcpy(seals,rear_p1_state.birth_identity,sizeof seals);
  allocation_defaults(kind?0:2,0);if(!kind)power=39;compare_create(10,258,4,0,true);
  CHECK(!memcmp(before,rear_p1_state.birth,sizeof before)&&!memcmp(seals,rear_p1_state.birth_identity,sizeof seals));
 }
 for(unsigned kind=0;kind<4;kind++) {
  defaults(8,full);allocation_defaults(2,0);if(kind==0)power=39;
  compare_create(kind==1?PORT_NUM+1:10,kind==2?0:kind==3?WEAP_NUM+1:258,4,0,true);
  for(unsigned i=0;i<80;i++)CHECK(!rear_p1_state.birth[i].qualified);
 }
 for(unsigned start=0;start<2;start++)for(unsigned valid=0;valid<2;valid++) {
  defaults(8,full);allocation_defaults(0,start);for(unsigned i=80-valid;i<=80;i++)shotAvail[i]=0;
  compare_create(10,258,4,0,true);
  for(unsigned i=0;i<valid;i++)p5m1_check(80-valid+i,(start+i)%2+1);
  CHECK(shotAvail[80]==255&&shotMultiPos[1]==(start+valid)%2+1);
 }
 /* New grants recycle pass-through/owned slots; distinct old births survive. */
 for(unsigned start=0;start<2;start++) {
  defaults(8,full);allocation_defaults(5,0);compare_create(10,268,3,1,true);
  allocation_defaults(2,start);compare_create(10,258,4,0,true);
  for(unsigned i=0;i<2;i++)p5m1_check(i,(start+i)%2+1);
  for(unsigned i=2;i<5;i++)p4m2_check(i,i+1,8);
  allocation_defaults(4,0);compare_create(10,269,4,1,true);
  for(unsigned i=0;i<4;i++)p5m2_check(i,i+1,8);
  allocation_defaults(2,start);compare_create(10,258,4,0,true);
  for(unsigned i=0;i<2;i++)p5m1_check(i,(start+i)%2+1);
  for(unsigned i=2;i<4;i++)p5m2_check(i,i+1,8);
 }
 /* Physical aliases and shared-head P6/P9 source records are not births258,
  * even if their synthetic records are byte-identical to admitted258. */
 const unsigned excluded[]={254,255,256,257,259,260,261,262,263,264,265,266,267,268,269,270,275,1258,1259,1262,3,41,52,51,81,90,445,502,504,505,686};
 for(unsigned i=0;i<sizeof excluded/sizeof *excluded;i++)for(unsigned mode=0;mode<2;mode++) {
  defaults(8,full);weapons[excluded[i]]=weapons[258];allocation_defaults(2,0);compare_create(10,excluded[i],4,mode,true);
  CHECK(!rear_p1_table(excluded[i]));for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 for(unsigned p=0;p<12;p++)for(unsigned mode=0;mode<2;mode++)if(p!=4||mode!=0) {
  defaults(8,full);allocation_defaults(2,0);compare_create(10,258,p,mode,true);for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 const unsigned ports[]={0,2,19,22,27,32,36,37,60};
 for(unsigned i=0;i<sizeof ports/sizeof *ports;i++) {
  defaults(8,full);allocation_defaults(2,0);compare_create(ports[i],258,4,0,true);for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 /* The new cell/record is conditional: no old admission or in-flight birth
  * gains a dependency on258. P5mode2 is specifically included. */
 const unsigned oldrecords[]={254,265,255,266,267,256,257,268,269};
 defaults(8,full);weaponPort[10].op[0][4]++;CHECK(!rear_p1_table(258));
 for(unsigned i=0;i<sizeof oldrecords/sizeof *oldrecords;i++)CHECK(rear_p1_table(oldrecords[i]));
 for(unsigned i=0;i<sizeof oldrecords/sizeof *oldrecords;i++) {
  unsigned r=oldrecords[i],k=r==269?13:r==256?6:r==257||r==268?8:r>=265?2:0;
  test_power=r==269?5:r==268?4:r==257?3:r==256||r==267?2:r==255||r==266?1:0;defaults(8,full);emit(k,0);CHECK(checked_head(k,0));
  weaponPort[10].op[0][4]++;CHECK(checked_head(k,0));weapons[258].attack[7]^=1;CHECK(checked_head(k,0));
 }
 test_power=1;
}
static void test_p5_mode1_adapter_protocol(void)
{
 for(unsigned start=1;start<=2;start++)for(unsigned bad=1;bad<=2;bad++)for(unsigned kind=0;kind<23;kind++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,4,0,1,258);uint64_t c=render_mirror_rear_p1_create_begin(10,1,258,1);
  for(unsigned n=1;n<bad;n++){unsigned p=p5m1_phase(start,n);p5m1_emit(c,n,n,p);p5m1_check(n,p);}
  unsigned phase=p5m1_phase(start,bad),k=p5m1_member(phase),slot=kind==2?80:kind==3?UINT_MAX:kind==17?81:bad;make_shot(k,bad);
  unsigned off=bankdata[2*(ids[k]-1)]|((unsigned)bankdata[2*(ids[k]-1)+1]<<8);
  if(kind==0)bankdata[off+1]^=1;
  if(kind==1)playerShotData[bad].shotXM++;
  if(kind==4)weapons[258].attack[7]^=1;
  if(kind==5)weaponPort[10].op[0][4]++;
  if(kind==6)twoPlayerMode=1;
  if(kind==7)mirror_logic_tick++;
  if(kind==16)active=false;
  (render_mirror_rear_p1_emit)(kind==8?c+1:kind==20?0:c,kind==9?bad+1:kind==21?0:bad,slot,kind==10?37:10,kind==11?0:1,kind==12?259:258,kind==13?2:1,kind==14?0:kind==18?3:kind==19?(phase%2+1):phase,kind==15?0:kind==22?ids[k]+1000:ids[k]);
  if(kind==0)bankdata[off+1]^=1;
  if(kind==4)weapons[258].attack[7]^=1;
  if(kind==5)weaponPort[10].op[0][4]--;
  if(kind==6)twoPlayerMode=0;
  if(kind==7)mirror_logic_tick--;
  if(kind==16)active=true;
  CHECK(!rear_p1_state.remaining&&!rear_p1_state.lease&&!rear_p1_state.call&&!rear_p1_state.birth[bad].qualified);
  for(unsigned n=1;n<bad;n++)p5m1_check(n,p5m1_phase(start,n));
  for(unsigned n=bad+1;n<=6;n++){p5m1_emit(c,n,n,p5m1_phase(start,n));CHECK(!rear_p1_state.birth[n].qualified);}
 }
 for(unsigned start=1;start<=2;start++)for(unsigned bad=2;bad<=3;bad++)for(unsigned reused=1;reused<bad;reused++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,4,0,1,258);uint64_t c=render_mirror_rear_p1_create_begin(10,1,258,1);
  for(unsigned n=1;n<bad;n++)p5m1_emit(c,n,n,p5m1_phase(start,n));
  p5m1_emit(c,bad,reused,p5m1_phase(start,bad));CHECK(!rear_p1_state.birth[reused].qualified&&!rear_p1_state.remaining);
  for(unsigned n=1;n<bad;n++)if(n!=reused)p5m1_check(n,p5m1_phase(start,n));
  for(unsigned n=bad+1;n<=7;n++){p5m1_emit(c,n,n,p5m1_phase(start,n));CHECK(!rear_p1_state.birth[n].qualified);}
 }
 for(unsigned start=1;start<=2;start++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,4,0,1,258);uint64_t c=render_mirror_rear_p1_create_begin(10,1,258,1);
  for(unsigned n=1;n<=2;n++) {
   unsigned p=p5m1_phase(start,n);p5m1_emit(c,n,n,p);p5m1_check(n,p);
   CHECK(rear_p1_state.remaining==2-n&&rear_p1_state.next_ordinal==n+1&&rear_p1_state.next_phase==p%2+1&&rear_p1_state.used_count==n&&rear_p1_state.used_slots[n-1]==n&&rear_p1_state.lease==(n<2));
  }
  for(unsigned n=3;n<=6;n++){p5m1_emit(c,n,n,p5m1_phase(start,n));CHECK(!rear_p1_state.birth[n].qualified&&!rear_p1_state.remaining);}
  for(unsigned n=1;n<=2;n++)p5m1_check(n,p5m1_phase(start,n));
 }
 for(unsigned p=1;p<=2;p++)for(unsigned b=0;b<80;b++) {
  defaults(8,full);Uint8 altered[80];memcpy(altered,recordbytes+720,80);altered[b]^=1;parse_record(&weapons[258],altered);
  CHECK(!rear_p1_table(258));(render_mirror_rear_p1_call_begin)(10,1,4,0,1,258);uint64_t c=render_mirror_rear_p1_create_begin(10,1,258,1);
  p5m1_emit(c,1,0,p);CHECK(!rear_p1_state.birth[0].qualified&&!rear_p1_state.lease&&!rear_p1_state.remaining);
 }
 for(unsigned start=1;start<=2;start++)for(unsigned after=0;after<=2;after++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,4,0,1,258);uint64_t c=render_mirror_rear_p1_create_begin(10,1,258,1);
  for(unsigned n=1;n<=after;n++)p5m1_emit(c,n,n,p5m1_phase(start,n));
  uint64_t inner=render_mirror_rear_p1_create_begin(10,1,258,1);CHECK(inner!=c);
  p5m1_emit(inner,1,10,start);CHECK(!rear_p1_state.birth[10].qualified);render_mirror_rear_p1_create_end(inner);
  p5m1_emit(c,after+1,11,p5m1_phase(start,after+1));CHECK(!rear_p1_state.birth[11].qualified);
  for(unsigned n=1;n<=after;n++)p5m1_check(n,p5m1_phase(start,n));
 }
}
static void test_p5_mode1_resources(void)
{
 test_power=6;
 for(int d=4;d<=8;d+=4)for(unsigned p=1;p<=2;p++) {
  unsigned k=p5m1_member(p);defaults(d,full);emit(k,0);
  unsigned oldblits=blits,oldends=ends,oldprobes=probes,oldgenerics=generics;PlayerShotDataType saved=playerShotData[0];Uint8 before[64000];memcpy(before,pixels,sizeof before);
  draw_player_shot_sprite2(&surface,101,100,spriteSheet8,ids[k],0,ids[k]);
  CHECK(last_mirrored&&generics==oldgenerics&&blits==oldblits+1&&ends==oldends+1&&probes==oldprobes+1&&!suppress);
  CHECK(!memcmp(before,pixels,sizeof before)&&!memcmp(&saved,&playerShotData[0],sizeof saved));
  int member=rear_p1_member(ids[k]);CHECK(member==(int)k-2);
  CHECK(rear_p1_resources.cache[member][d==8].attempted);
  CHECK(rear_p1_resources.cache[member][d==8].asset.index==(int)ids[k]);
 }
 for(unsigned p=1;p<=2;p++)for(unsigned field=0;field<13;field++)for(unsigned warm=0;warm<2;warm++) {
  defaults(8,full);unsigned k=p5m1_member(p);emit(k,0);if(warm)CHECK(checked_head(k,0));
  PlayerShotDataType *q=&playerShotData[0],saved=*q;
  switch(field) {
   case 0:q->shotGr++;break;case 1:q->shotAni++;break;case 2:q->shotAniMax++;break;case 3:q->playerNumber++;break;
   case 4:q->shotTrail--;break;case 5:q->aimAtEnemy++;break;case 6:q->chainReaction++;break;case 7:q->shotComplicated=true;break;
   case 8:q->shotBlastFilter++;break;case 9:q->shotXM++;break;case 10:q->shotYM++;break;case 11:q->shotXC++;break;default:q->shotYC++;break;
  }
  bad_restore(k,0);*q=saved;CHECK(!checked_head(k,0));
 }
 /* Exact source consumers remain separate from original admitted birth. */
 for(unsigned p=1;p<=2;p++)for(unsigned record=259;record<=262;record+=3) {
  defaults(8,full);unsigned k=p5m1_member(p);emit(k,0);CHECK(checked_head(k,0));
  RearP1Birth saved=rear_p1_state.birth[0];rear_p1_state.birth[0].record=record;bad_restore(k,0);
  rear_p1_state.birth[0]=saved;CHECK(!checked_head(k,0));
 }
 CHECK(rear_p1_member(41)==13&&rear_p1_member(3)==14&&rear_p1_observed(41)==15&&rear_p1_observed(3)==16);
 CHECK(rear_p1_member(163)<0&&rear_p1_member(164)<0);
 test_power=1;
}
