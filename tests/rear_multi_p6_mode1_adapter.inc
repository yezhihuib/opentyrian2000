/* Synthetic/public or private-original fixtures only. Actual allocator source,
 * controlled diagnostic qualification; no ordinary P6 acquisition claim. */
static unsigned p6m1_member(unsigned p){static const unsigned members[3]={15,16,8};return members[p-1];}
static unsigned p6m1_phase(unsigned start,unsigned n){return (start+n-2)%3+1;}
static void p6m1_emit(uint64_t c,unsigned n,unsigned slot,unsigned p)
{unsigned k=p6m1_member(p);make_shot(k,slot);(render_mirror_rear_p1_emit)(c,n,slot,10,1,259,1,p,ids[k]);}
static void p6m1_check(unsigned slot,unsigned p)
{
 CHECK(rear_p1_state.birth[slot].qualified&&rear_p1_state.birth[slot].record==259&&rear_p1_state.birth[slot].mode==1&&rear_p1_state.birth[slot].phase==p);
 CHECK(checked_head(p6m1_member(p),slot));
}
static void test_p6_mode1_actual_allocations(void)
{
 unsigned coverage[3][3]={{0}};
 for(int d=4;d<=8;d+=4)for(unsigned start=0;start<=3;start++)for(unsigned prior=0;prior<=3;prior++)for(unsigned cap=0;cap<=5;cap++) {
  defaults(d,full);allocation_defaults(0,start);for(unsigned i=0;i<prior;i++)shotAvail[40+i]=0;
  compare_create(10,259,5,0,true);unsigned phase=start;
  for(unsigned i=0;i<prior;i++){phase=phase==3?1:phase+1;p6m1_check(40+i,phase);}
  CHECK(shotMultiPos[1]==phase);unsigned previous=phase;
  memset(shotAvail,1,sizeof shotAvail);for(unsigned i=0;i<cap;i++)shotAvail[10+i]=0;
  compare_create(10,259,5,0,true);unsigned count=cap<3?cap:3;
  for(unsigned i=0;i<count;i++){phase=phase==3?1:phase+1;coverage[phase-1][i]++;p6m1_check(10+i,phase);}
  CHECK(shotMultiPos[1]==phase&&!rear_p1_state.birth[13].qualified);
  for(unsigned power_index=0;power_index<12;power_index++)for(unsigned mode=0;mode<2;mode++) {
   (render_mirror_rear_p1_call_begin)(10,1,power_index,mode,1,(mode?265:254)+power_index);render_mirror_rear_p1_call_end();
   for(unsigned i=0;i<count;i++)p6m1_check(10+i,(previous+i)%3+1);
  }
  phase=start;for(unsigned i=0;i<prior;i++){phase=phase==3?1:phase+1;p6m1_check(40+i,phase);}
  memset(shotAvail,1,sizeof shotAvail);for(unsigned i=0;i<3;i++)shotAvail[10+i]=0;
  compare_create(10,259,5,0,false);for(unsigned i=0;i<3;i++)CHECK(!rear_p1_state.birth[10+i].qualified);
 }
 for(unsigned p=0;p<3;p++)for(unsigned n=0;n<3;n++)CHECK(coverage[p][n]>0);
 /* Insufficient power and zero capacity must preserve old non-recycled births. */
 for(unsigned kind=0;kind<2;kind++) {
  defaults(8,full);allocation_defaults(3,0);compare_create(10,259,5,0,true);
  RearP1Birth before[REAR_P1_SLOTS];memcpy(before,rear_p1_state.birth,sizeof before);
  uint64_t seals[REAR_P1_SLOTS];memcpy(seals,rear_p1_state.birth_identity,sizeof seals);
  allocation_defaults(kind?0:3,0);if(!kind)power=39;compare_create(10,259,5,0,true);
  CHECK(!memcmp(before,rear_p1_state.birth,sizeof before)&&!memcmp(seals,rear_p1_state.birth_identity,sizeof seals));
 }
 for(unsigned kind=0;kind<4;kind++) {
  defaults(8,full);allocation_defaults(3,0);if(kind==0)power=39;
  compare_create(kind==1?PORT_NUM+1:10,kind==2?0:kind==3?WEAP_NUM+1:259,5,0,true);
  for(unsigned i=0;i<80;i++)CHECK(!rear_p1_state.birth[i].qualified);
 }
 for(unsigned start=0;start<3;start++)for(unsigned valid=0;valid<3;valid++) {
  defaults(8,full);allocation_defaults(0,start);for(unsigned i=80-valid;i<=80;i++)shotAvail[i]=0;
  compare_create(10,259,5,0,true);
  for(unsigned i=0;i<valid;i++)p6m1_check(80-valid+i,(start+i)%3+1);
  CHECK(shotAvail[80]==255&&shotMultiPos[1]==(start+valid)%3+1);
 }
 /* New grants recycle pass-through/owned slots; distinct old births survive. */
 for(unsigned start=0;start<3;start++) {
  defaults(8,full);allocation_defaults(5,0);compare_create(10,268,3,1,true);
  allocation_defaults(3,start);compare_create(10,259,5,0,true);
  for(unsigned i=0;i<3;i++)p6m1_check(i,(start+i)%3+1);
  for(unsigned i=3;i<5;i++)p4m2_check(i,i+1,8);
  allocation_defaults(4,0);compare_create(10,269,4,1,true);
  for(unsigned i=0;i<4;i++)p5m2_check(i,i+1,8);
  allocation_defaults(3,start);compare_create(10,259,5,0,true);
  for(unsigned i=0;i<3;i++)p6m1_check(i,(start+i)%3+1);
  for(unsigned i=3;i<4;i++)p5m2_check(i,i+1,8);
 }
 /* Physical aliases and all other shared-head records are not births259,
  * even if their synthetic records are byte-identical to admitted259. */
 const unsigned excluded[]={254,255,256,257,258,260,261,262,263,264,265,266,267,268,269,270,275,1258,1259,1262,3,41,52,51,81,90,445,451,502,504,505,686};
 for(unsigned i=0;i<sizeof excluded/sizeof *excluded;i++)for(unsigned mode=0;mode<2;mode++) {
  defaults(8,full);weapons[excluded[i]]=weapons[259];allocation_defaults(3,0);compare_create(10,excluded[i],5,mode,true);
  CHECK(!rear_p1_table(excluded[i]));for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 for(unsigned p=0;p<12;p++)for(unsigned mode=0;mode<2;mode++)if(p!=5||mode!=0) {
  defaults(8,full);allocation_defaults(3,0);compare_create(10,259,p,mode,true);for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 const unsigned ports[]={0,2,19,22,27,32,36,37,38,60};
 for(unsigned i=0;i<sizeof ports/sizeof *ports;i++) {
  defaults(8,full);allocation_defaults(3,0);compare_create(ports[i],259,5,0,true);for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 /* The new cell/record is conditional: no old admission or in-flight birth
  * gains a dependency on259. Both P5 modes are specifically included. */
 const unsigned oldrecords[]={254,265,255,266,267,256,257,268,269,258};
 defaults(8,full);weaponPort[10].op[0][5]++;CHECK(!rear_p1_table(259));
 for(unsigned i=0;i<sizeof oldrecords/sizeof *oldrecords;i++)CHECK(rear_p1_table(oldrecords[i]));
 for(unsigned i=0;i<sizeof oldrecords/sizeof *oldrecords;i++) {
  unsigned r=oldrecords[i],k=r==258?15:r==269?13:r==256?6:r==257||r==268?8:r>=265?2:0;
  test_power=r==258?6:r==269?5:r==268?4:r==257?3:r==256||r==267?2:r==255||r==266?1:0;defaults(8,full);emit(k,0);CHECK(checked_head(k,0));
  weaponPort[10].op[0][5]++;CHECK(checked_head(k,0));weapons[259].attack[7]^=1;CHECK(checked_head(k,0));
 }
 test_power=1;
}
static void test_p6_mode1_adapter_protocol(void)
{
 for(unsigned start=1;start<=3;start++)for(unsigned bad=1;bad<=4;bad++)for(unsigned kind=0;kind<23;kind++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,5,0,1,259);uint64_t c=render_mirror_rear_p1_create_begin(10,1,259,1);
  for(unsigned n=1;n<bad;n++){unsigned p=p6m1_phase(start,n);p6m1_emit(c,n,n,p);p6m1_check(n,p);}
  unsigned phase=p6m1_phase(start,bad),k=p6m1_member(phase),slot=kind==2?80:kind==3?UINT_MAX:kind==17?81:bad;make_shot(k,bad);
  unsigned off=bankdata[2*(ids[k]-1)]|((unsigned)bankdata[2*(ids[k]-1)+1]<<8);
  if(kind==0)bankdata[off+1]^=1;
  if(kind==1)playerShotData[bad].shotXM++;
  if(kind==4)weapons[259].attack[7]^=1;
  if(kind==5)weaponPort[10].op[0][5]++;
  if(kind==6)twoPlayerMode=1;
  if(kind==7)mirror_logic_tick++;
  if(kind==16)active=false;
  (render_mirror_rear_p1_emit)(kind==8?c+1:kind==20?0:c,kind==9?bad+1:kind==21?0:bad,slot,kind==10?37:10,kind==11?0:1,kind==12?258:259,kind==13?2:1,kind==14?0:kind==18?4:kind==19?(phase%3+1):phase,kind==15?0:kind==22?ids[k]+1000:ids[k]);
  if(kind==0)bankdata[off+1]^=1;
  if(kind==4)weapons[259].attack[7]^=1;
  if(kind==5)weaponPort[10].op[0][5]--;
  if(kind==6)twoPlayerMode=0;
  if(kind==7)mirror_logic_tick--;
  if(kind==16)active=true;
  CHECK(!rear_p1_state.remaining&&!rear_p1_state.lease&&!rear_p1_state.call&&!rear_p1_state.birth[bad].qualified);
  for(unsigned n=1;n<bad;n++)p6m1_check(n,p6m1_phase(start,n));
  for(unsigned n=bad+1;n<=6;n++){p6m1_emit(c,n,n,p6m1_phase(start,n));CHECK(!rear_p1_state.birth[n].qualified);}
 }
 for(unsigned start=1;start<=3;start++)for(unsigned bad=2;bad<=4;bad++)for(unsigned reused=1;reused<bad;reused++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,5,0,1,259);uint64_t c=render_mirror_rear_p1_create_begin(10,1,259,1);
  for(unsigned n=1;n<bad;n++)p6m1_emit(c,n,n,p6m1_phase(start,n));
  p6m1_emit(c,bad,reused,p6m1_phase(start,bad));CHECK(!rear_p1_state.birth[reused].qualified&&!rear_p1_state.remaining);
  for(unsigned n=1;n<bad;n++)if(n!=reused)p6m1_check(n,p6m1_phase(start,n));
  for(unsigned n=bad+1;n<=7;n++){p6m1_emit(c,n,n,p6m1_phase(start,n));CHECK(!rear_p1_state.birth[n].qualified);}
 }
 for(unsigned start=1;start<=3;start++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,5,0,1,259);uint64_t c=render_mirror_rear_p1_create_begin(10,1,259,1);
  for(unsigned n=1;n<=3;n++) {
   unsigned p=p6m1_phase(start,n);p6m1_emit(c,n,n,p);p6m1_check(n,p);
   CHECK(rear_p1_state.remaining==3-n&&rear_p1_state.next_ordinal==n+1&&rear_p1_state.next_phase==p%3+1&&rear_p1_state.used_count==n&&rear_p1_state.used_slots[n-1]==n&&rear_p1_state.lease==(n<3));
  }
  for(unsigned n=4;n<=6;n++){p6m1_emit(c,n,n,p6m1_phase(start,n));CHECK(!rear_p1_state.birth[n].qualified&&!rear_p1_state.remaining);}
  for(unsigned n=1;n<=3;n++)p6m1_check(n,p6m1_phase(start,n));
 }
 for(unsigned p=1;p<=3;p++)for(unsigned b=0;b<80;b++) {
  defaults(8,full);Uint8 altered[80];memcpy(altered,recordbytes+800,80);altered[b]^=1;parse_record(&weapons[259],altered);
  CHECK(!rear_p1_table(259));(render_mirror_rear_p1_call_begin)(10,1,5,0,1,259);uint64_t c=render_mirror_rear_p1_create_begin(10,1,259,1);
  p6m1_emit(c,1,0,p);CHECK(!rear_p1_state.birth[0].qualified&&!rear_p1_state.lease&&!rear_p1_state.remaining);
 }
 for(unsigned start=1;start<=3;start++)for(unsigned after=0;after<=3;after++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,5,0,1,259);uint64_t c=render_mirror_rear_p1_create_begin(10,1,259,1);
  for(unsigned n=1;n<=after;n++)p6m1_emit(c,n,n,p6m1_phase(start,n));
  uint64_t inner=render_mirror_rear_p1_create_begin(10,1,259,1);CHECK(inner!=c);
  p6m1_emit(inner,1,10,start);CHECK(!rear_p1_state.birth[10].qualified);render_mirror_rear_p1_create_end(inner);
  p6m1_emit(c,after+1,11,p6m1_phase(start,after+1));CHECK(!rear_p1_state.birth[11].qualified);
  for(unsigned n=1;n<=after;n++)p6m1_check(n,p6m1_phase(start,n));
 }
}
static void test_p6_mode1_resources(void)
{
 test_power=7;
 for(int d=4;d<=8;d+=4)for(unsigned p=1;p<=3;p++) {
  unsigned k=p6m1_member(p);defaults(d,full);emit(k,0);
  unsigned oldblits=blits,oldends=ends,oldprobes=probes,oldgenerics=generics;PlayerShotDataType saved=playerShotData[0];Uint8 before[64000];memcpy(before,pixels,sizeof before);
  draw_player_shot_sprite2(&surface,101,100,spriteSheet8,ids[k],0,ids[k]);
  CHECK(last_mirrored&&generics==oldgenerics&&blits==oldblits+1&&ends==oldends+1&&probes==oldprobes+1&&!suppress);
  CHECK(!memcmp(before,pixels,sizeof before)&&!memcmp(&saved,&playerShotData[0],sizeof saved));
  int member=rear_p1_member(ids[k]);CHECK(member==(p==3?8:(int)k-2));
  CHECK(rear_p1_resources.cache[member][d==8].attempted);
  CHECK(rear_p1_resources.cache[member][d==8].asset.index==(int)ids[k]);
 }
 for(unsigned p=1;p<=3;p++)for(unsigned field=0;field<13;field++)for(unsigned warm=0;warm<2;warm++) {
  defaults(8,full);unsigned k=p6m1_member(p);emit(k,0);if(warm)CHECK(checked_head(k,0));
  PlayerShotDataType *q=&playerShotData[0],saved=*q;
  switch(field) {
   case 0:q->shotGr++;break;case 1:q->shotAni++;break;case 2:q->shotAniMax++;break;case 3:q->playerNumber++;break;
   case 4:q->shotTrail--;break;case 5:q->aimAtEnemy++;break;case 6:q->chainReaction++;break;case 7:q->shotComplicated=true;break;
   case 8:q->shotBlastFilter++;break;case 9:q->shotXM++;break;case 10:q->shotYM++;break;case 11:q->shotXC++;break;default:q->shotYC++;break;
  }
  bad_restore(k,0);*q=saved;CHECK(!checked_head(k,0));
 }
 /* The same-mode shared phases must retain their original record identity.
  * Table validation of both records stays valid, so only the birth seal rejects. */
 for(unsigned p=1;p<=2;p++)for(unsigned origin=258;origin<=259;origin++) {
  defaults(8,full);unsigned k=p6m1_member(p);test_power=origin==258?6:7;emit(k,0);CHECK(checked_head(k,0));
  RearP1Birth saved=rear_p1_state.birth[0];rear_p1_state.birth[0].record=origin==258?259:258;bad_restore(k,0);
  rear_p1_state.birth[0]=saved;CHECK(!checked_head(k,0));
 }
 /* Corrupt259 must leave258 intact, and conversely; both may coexist. */
 for(unsigned p=1;p<=2;p++)for(unsigned broken=258;broken<=259;broken++) {
  defaults(8,full);unsigned k=p6m1_member(p);test_power=6;emit(k,0);test_power=7;emit(k,1);
  CHECK(checked_head(k,0)&&checked_head(k,1));weapons[broken].attack[7]^=1;
  CHECK(checked_head(k,0)==(broken!=258));CHECK(checked_head(k,1)==(broken!=259));
  weapons[broken].attack[7]^=1;CHECK(!checked_head(k,broken==258?0:1));
 }
 /* Shared resources are reused in place, while each conditional table cell
  * revokes only its own original record's birth. */
 for(int d=4;d<=8;d+=4)for(unsigned p=1;p<=2;p++)for(unsigned broken=258;broken<=259;broken++) {
  defaults(d,full);unsigned k=p6m1_member(p);test_power=6;emit(k,0);CHECK(checked_head(k,0));
  Asset *shared=&rear_p1_resources.cache[rear_p1_member(ids[k])][d==8].asset;
  Uint8 *payload=shared->rgba;unsigned opens=role_opens;test_power=7;emit(k,1);CHECK(checked_head(k,1));
  CHECK(role_opens==opens&&shared->rgba==payload&&shared->index==(int)ids[k]);
  weaponPort[10].op[0][broken-254]++;CHECK(checked_head(k,0)==(broken!=258));CHECK(checked_head(k,1)==(broken!=259));
  weaponPort[10].op[0][broken-254]--;CHECK(!checked_head(k,broken==258?0:1));
 }
 CHECK(rear_p1_member(41)==13&&rear_p1_member(3)==14&&rear_p1_observed(41)==15&&rear_p1_observed(3)==16);
 CHECK(rear_p1_member(163)<0&&rear_p1_member(164)<0);
 test_power=1;
}
/* All three source directional arrays are compiled above. This specifically
 * covers the second Multi-Cannon family, which earlier inventories omitted.
 * Record451's original linked route uses creator port0/player2;22/38 are the
 * selected weapon IDs passed to the actual direction remapper. */
static void p6m1_linked_case(unsigned weapon,unsigned dir,unsigned route)
{
 unsigned k=dir==5?14:13;test_power=5;emit(k,0);CHECK(checked_head(k,0));
 CHECK(linkGunWeapons[weapon-1]==451&&linkMult2Gr[dir]==ids[k]);
 allocation_defaults(8,0);twoPlayerMode=twoPlayerLinked=route==0;
 unsigned port=route==0?0:route==1?weapon:10,pnum=route==0?2:1;
 GameState initial,observed,baseline;save_game(&initial);
 if(route)(render_mirror_rear_p1_call_begin)(port,1,5,0,pnum,451);
 JE_integer a=player_shot_create(port,1,100,100,100,100,451,pnum);CHECK(a>=0&&a<80);
 JE_real angle=(JE_real)(dir*(2*M_PI)/16);player_shot_set_direction(a,weapon,angle);save_game(&observed);
 CHECK(playerShotData[a].shotGr==ids[k]);
 load_game(&initial);JE_integer b=baseline_shot_create(port,1,100,100,100,100,451,pnum);CHECK(a==b);
 player_shot_set_direction(b,weapon,angle);save_game(&baseline);same_game(&observed,&baseline);load_game(&observed);
 CHECK(!rear_p1_state.birth[0].qualified&&!rear_p1_state.birth_identity[0]);
 for(unsigned slot=0;slot<80;slot++)CHECK(!rear_p1_state.birth[slot].qualified);
 CHECK(!rear_p1_state.pending&&!rear_p1_state.lease&&!rear_p1_state.remaining&&!rear_p1_state.call&&!rear_p1_table(451));
 unsigned opens=role_opens,before=generics;CHECK(!checked_head(k,(unsigned)a));
 draw_player_shot_sprite2(&surface,playerShotData[a].shotX+1,playerShotData[a].shotY,spriteSheet8,ids[k],(unsigned)a,ids[k]);
 CHECK(!last_mirrored&&generics==before+1&&role_opens==opens&&!suppress);
 test_power=1;
}
static void test_p6_mode1_linked_negatives(void)
{
 const unsigned ports[]={22,38},directions[]={5,11};
 for(int d=4;d<=8;d+=4)for(unsigned w=0;w<2;w++)for(unsigned a=0;a<2;a++)for(unsigned route=0;route<3;route++) {
  defaults(d,full);weapons[451]=weapons[259];weapons[451].multi=weapons[451].max=1;
  p6m1_linked_case(ports[w],directions[a],route);
 }
}
