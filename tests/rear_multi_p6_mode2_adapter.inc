/* Exact P6 mode2 controlled adapter coverage. Original allocator state is
 * compared to its observer-stripped source; no ordinary P6 purchase claim. */
static unsigned p6m2_member(unsigned p){static const unsigned members[5]={13,14,10,9,8};return members[p-1];}
static unsigned p6m2_phase(unsigned start,unsigned n){return (start+n-2)%5+1;}
static bool p6m2_expected(unsigned p,int d){return p<=2||p==5||d==8;}
static void p6m2_emit(uint64_t c,unsigned n,unsigned slot,unsigned p)
{unsigned k=p6m2_member(p);make_shot(k,slot);(render_mirror_rear_p1_emit)(c,n,slot,10,1,270,1,p,ids[k]);}
static void p6m2_check(unsigned slot,unsigned p,int d)
{
 CHECK(rear_p1_state.birth[slot].qualified&&rear_p1_state.birth[slot].record==270&&rear_p1_state.birth[slot].mode==2&&rear_p1_state.birth[slot].phase==p);
 unsigned k=p6m2_member(p),opens=role_opens;CHECK(checked_head(k,slot)==p6m2_expected(p,d));
 if(!p6m2_expected(p,d)){int m=rear_p1_member(ids[k]);CHECK(role_opens==opens&&!rear_p1_resources.cache[m][0].attempted&&!rear_p1_resources.cache[m][1].attempted);}
}
static void test_p6_mode2_actual_allocations(void)
{
 unsigned coverage[5][5]={{0}};
 /* Includes all 180 cyclic continuation designs, plus sentinel last-phase0
  * and a sixth free slot to establish five-allocation saturation. */
 for(int d=4;d<=8;d+=4)for(unsigned start=0;start<=5;start++)for(unsigned prior=0;prior<=5;prior++)for(unsigned cap=0;cap<=6;cap++) {
  defaults(d,full);allocation_defaults(0,start);for(unsigned i=0;i<prior;i++)shotAvail[40+i]=0;
  compare_create(10,270,5,1,true);unsigned phase=start;
  for(unsigned i=0;i<prior;i++){phase=phase==5?1:phase+1;p6m2_check(40+i,phase,d);}
  CHECK(shotMultiPos[1]==phase);unsigned previous=phase;
  memset(shotAvail,1,sizeof shotAvail);for(unsigned i=0;i<cap;i++)shotAvail[10+i]=0;
  compare_create(10,270,5,1,true);unsigned count=cap<5?cap:5;
  for(unsigned i=0;i<count;i++){phase=phase==5?1:phase+1;coverage[phase-1][i]++;p6m2_check(10+i,phase,d);}
  CHECK(shotMultiPos[1]==phase&&!rear_p1_state.birth[15].qualified);
  for(unsigned pi=0;pi<12;pi++)for(unsigned mode=0;mode<2;mode++) {
   (render_mirror_rear_p1_call_begin)(10,1,pi,mode,1,(mode?265:254)+pi);render_mirror_rear_p1_call_end();
   for(unsigned i=0;i<count;i++)p6m2_check(10+i,(previous+i)%5+1,d);
  }
  phase=start;for(unsigned i=0;i<prior;i++){phase=phase==5?1:phase+1;p6m2_check(40+i,phase,d);}
  memset(shotAvail,1,sizeof shotAvail);for(unsigned i=0;i<5;i++)shotAvail[10+i]=0;
  compare_create(10,270,5,1,false);for(unsigned i=0;i<5;i++)CHECK(!rear_p1_state.birth[10+i].qualified);
 }
 for(unsigned p=0;p<5;p++)for(unsigned n=0;n<5;n++)CHECK(coverage[p][n]>0);
 for(unsigned kind=0;kind<2;kind++) {
  defaults(8,full);allocation_defaults(5,0);compare_create(10,270,5,1,true);
  RearP1Birth before[REAR_P1_SLOTS];memcpy(before,rear_p1_state.birth,sizeof before);
  uint64_t seals[REAR_P1_SLOTS];memcpy(seals,rear_p1_state.birth_identity,sizeof seals);
  allocation_defaults(kind?0:5,0);
  if(!kind)power=39;
  compare_create(10,270,5,1,true);
  CHECK(!memcmp(before,rear_p1_state.birth,sizeof before)&&!memcmp(seals,rear_p1_state.birth_identity,sizeof seals));
 }
 for(unsigned kind=0;kind<4;kind++) {
  defaults(8,full);allocation_defaults(5,0);
  if(kind==0)power=39;
  compare_create(kind==1?PORT_NUM+1:10,kind==2?0:kind==3?WEAP_NUM+1:270,5,1,true);
  for(unsigned i=0;i<80;i++)CHECK(!rear_p1_state.birth[i].qualified);
 }
 for(unsigned start=0;start<5;start++)for(unsigned valid=0;valid<5;valid++) {
  defaults(8,full);allocation_defaults(0,start);for(unsigned i=80-valid;i<=80;i++)shotAvail[i]=0;
  compare_create(10,270,5,1,true);
  for(unsigned i=0;i<valid;i++)p6m2_check(80-valid+i,(start+i)%5+1,8);
  CHECK(shotAvail[80]==255&&shotMultiPos[1]==(start+valid)%5+1);
 }
 /* All physical aliases, shared sources, wrong power/mode and ports remain
  * unowned even when their payload is byte-identical to the admitted record. */
 const unsigned excluded[]={254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,271,275,1270,1269,1268,1259,3,41,52,51,81,90,445,451,502,504,505,686};
 for(unsigned i=0;i<sizeof excluded/sizeof *excluded;i++)for(unsigned mode=0;mode<2;mode++) {
  defaults(8,full);weapons[excluded[i]]=weapons[270];allocation_defaults(5,0);compare_create(10,excluded[i],5,mode,true);
  CHECK(!rear_p1_table(excluded[i]));for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 for(unsigned p=0;p<12;p++)for(unsigned mode=0;mode<2;mode++)if(p!=5||mode!=1) {
  defaults(8,full);allocation_defaults(5,0);compare_create(10,270,p,mode,true);for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 const unsigned ports[]={0,2,19,22,27,32,36,37,38,60};
 for(unsigned i=0;i<sizeof ports/sizeof *ports;i++) {
  defaults(8,full);allocation_defaults(5,0);compare_create(ports[i],270,5,1,true);for(unsigned n=0;n<80;n++)CHECK(!rear_p1_state.birth[n].qualified);
 }
 /* Every prior route keeps record-local validation and retained ownership. */
 const unsigned oldrecords[]={254,265,255,266,267,256,257,268,269,258,259};
 for(unsigned i=0;i<sizeof oldrecords/sizeof *oldrecords;i++) {
  unsigned r=oldrecords[i],mode=r>=265,pi=mode?r-265:r-254;
  defaults(8,full);allocation_defaults(5,0);compare_create(10,r,pi,mode,true);
  weaponPort[10].op[1][5]++;weapons[270].attack[7]^=1;CHECK(!rear_p1_table(270)&&rear_p1_table(r));
  for(unsigned slot=0;slot<5;slot++)if(rear_p1_state.birth[slot].qualified)CHECK(checked_head((unsigned)rear_p1_observed(rear_p1_state.birth[slot].raw),slot));
  allocation_defaults(5,0);compare_create(10,r,pi,mode,true);
  CHECK(rear_p1_state.birth[r==268?2:0].qualified);
 }
 test_power=1;
}
static void test_p6_mode2_adapter_protocol(void)
{
 for(unsigned start=1;start<=5;start++)for(unsigned bad=1;bad<=6;bad++)for(unsigned kind=0;kind<23;kind++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,5,1,1,270);uint64_t c=render_mirror_rear_p1_create_begin(10,1,270,1);
  for(unsigned n=1;n<bad;n++){unsigned p=p6m2_phase(start,n);p6m2_emit(c,n,n,p);p6m2_check(n,p,8);}
  unsigned phase=p6m2_phase(start,bad),k=p6m2_member(phase),slot=kind==2?80:kind==3?UINT_MAX:kind==17?81:bad;make_shot(k,bad);
  unsigned off=bankdata[2*(ids[k]-1)]|((unsigned)bankdata[2*(ids[k]-1)+1]<<8);
  if(kind==0)bankdata[off+1]^=1;
  if(kind==1)playerShotData[bad].shotXM++;
  if(kind==4)weapons[270].attack[7]^=1;
  if(kind==5)weaponPort[10].op[1][5]++;
  if(kind==6)twoPlayerMode=1;
  if(kind==7)mirror_logic_tick++;
  if(kind==16)active=false;
  (render_mirror_rear_p1_emit)(kind==8?c+1:kind==20?0:c,kind==9?bad+1:kind==21?0:bad,slot,kind==10?37:10,kind==11?0:1,kind==12?269:270,kind==13?2:1,kind==14?0:kind==18?6:kind==19?(phase%5+1):phase,kind==15?0:kind==22?ids[k]+1000:ids[k]);
  if(kind==0)bankdata[off+1]^=1;
  if(kind==4)weapons[270].attack[7]^=1;
  if(kind==5)weaponPort[10].op[1][5]--;
  if(kind==6)twoPlayerMode=0;
  if(kind==7)mirror_logic_tick--;
  if(kind==16)active=true;
  CHECK(!rear_p1_state.remaining&&!rear_p1_state.lease&&!rear_p1_state.call&&!rear_p1_state.birth[bad].qualified);
  for(unsigned n=1;n<bad;n++)p6m2_check(n,p6m2_phase(start,n),8);
  for(unsigned n=bad+1;n<=7;n++){p6m2_emit(c,n,n,p6m2_phase(start,n));CHECK(!rear_p1_state.birth[n].qualified);}
 }
 /* Every physical slot can be the duplicate, including a duplicate sixth.
  * Distinct earlier allocations survive; only the reused slot is cleared. */
 for(unsigned base=0;base<80;base++)for(unsigned start=1;start<=5;start++)for(unsigned bad=2;bad<=6;bad++)for(unsigned reused=1;reused<bad;reused++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,5,1,1,270);uint64_t c=render_mirror_rear_p1_create_begin(10,1,270,1);
  for(unsigned n=1;n<bad;n++)p6m2_emit(c,n,(base+n-1)%80,p6m2_phase(start,n));
  unsigned slot=(base+reused-1)%80;p6m2_emit(c,bad,slot,p6m2_phase(start,bad));CHECK(!rear_p1_state.birth[slot].qualified&&!rear_p1_state.birth_identity[slot]&&!rear_p1_state.remaining);
  for(unsigned n=1;n<bad;n++)if(n!=reused)CHECK(rear_p1_state.birth[(base+n-1)%80].qualified);
 }
 for(unsigned start=1;start<=5;start++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,5,1,1,270);uint64_t c=render_mirror_rear_p1_create_begin(10,1,270,1);
  for(unsigned n=1;n<=5;n++) {
   unsigned p=p6m2_phase(start,n);p6m2_emit(c,n,n,p);p6m2_check(n,p,8);
   CHECK(rear_p1_state.remaining==5-n&&rear_p1_state.next_ordinal==n+1&&rear_p1_state.next_phase==p%5+1&&rear_p1_state.used_count==n&&rear_p1_state.used_slots[n-1]==n&&rear_p1_state.lease==(n<5));
  }
  p6m2_emit(c,6,6,start);CHECK(!rear_p1_state.birth[6].qualified&&!rear_p1_state.remaining);
  for(unsigned n=1;n<=5;n++)p6m2_check(n,p6m2_phase(start,n),8);
 }
 /* All640 individual record-bit changes, every start phase, admission and
  * warm draw revocation; every older table remains valid throughout. */
 const unsigned oldrecords[]={254,265,255,266,267,256,257,268,269,258,259};
 for(unsigned p=1;p<=5;p++)for(unsigned bit=0;bit<640;bit++) {
  defaults(8,full);test_power=8;unsigned k=p6m2_member(p);emit(k,0);CHECK(checked_head(k,0));
  Uint8 altered[80];memcpy(altered,recordbytes+880,80);altered[bit/8]^=(Uint8)(1u<<(bit%8));parse_record(&weapons[270],altered);
  CHECK(!rear_p1_table(270));for(unsigned i=0;i<11;i++)CHECK(rear_p1_table(oldrecords[i]));bad_restore(k,0);
  (render_mirror_rear_p1_call_begin)(10,1,5,1,1,270);uint64_t c=render_mirror_rear_p1_create_begin(10,1,270,1);
  p6m2_emit(c,1,1,p);CHECK(!rear_p1_state.birth[1].qualified&&!rear_p1_state.lease&&!rear_p1_state.remaining);
  parse_record(&weapons[270],recordbytes+880);CHECK(!checked_head(k,0));p6m2_emit(c,2,2,p%5+1);CHECK(!rear_p1_state.birth[2].qualified);
 }
 for(unsigned start=1;start<=5;start++)for(unsigned after=0;after<=5;after++) {
  defaults(8,full);(render_mirror_rear_p1_call_begin)(10,1,5,1,1,270);uint64_t c=render_mirror_rear_p1_create_begin(10,1,270,1);
  for(unsigned n=1;n<=after;n++)p6m2_emit(c,n,n,p6m2_phase(start,n));
  uint64_t inner=render_mirror_rear_p1_create_begin(10,1,270,1);CHECK(inner!=c);
  p6m2_emit(inner,1,10,start);CHECK(!rear_p1_state.birth[10].qualified);render_mirror_rear_p1_create_end(inner);
  p6m2_emit(c,after+1,11,p6m2_phase(start,after+1));CHECK(!rear_p1_state.birth[11].qualified);
  for(unsigned n=1;n<=after;n++)p6m2_check(n,p6m2_phase(start,n),8);
 }
 test_power=1;
}
static void test_p6_mode2_resources(void)
{
 test_power=8;
 for(int d=4;d<=8;d+=4)for(unsigned p=1;p<=5;p++) {
  unsigned k=p6m2_member(p);defaults(d,full);emit(k,0);unsigned opens=role_opens,oldblits=blits,oldends=ends,oldprobes=probes,oldgenerics=generics;
  PlayerShotDataType saved=playerShotData[0];Uint8 before[64000];memcpy(before,pixels,sizeof before);
  draw_player_shot_sprite2(&surface,101,100,spriteSheet8,ids[k],0,ids[k]);bool expected=p6m2_expected(p,d);
  CHECK(last_mirrored==expected&&generics==oldgenerics+(unsigned)!expected&&blits==oldblits+1&&ends==oldends+1&&probes==oldprobes+1&&!suppress);
  CHECK(!memcmp(before,pixels,sizeof before)&&!memcmp(&saved,&playerShotData[0],sizeof saved));
  if(!expected) {
   int m=rear_p1_member(ids[k]);CHECK(role_opens==opens&&!rear_p1_resources.cache[m][0].attempted&&!rear_p1_resources.cache[m][1].attempted);
   Asset fake={true,false,ASSET_REAR_MULTI_P1,(int)ids[k],12,14,0,0,4,NULL};CHECK(!rear_p1_load(&fake,4)&&role_opens==opens);
  }
 }
 /* Both seal directions270/269 phases1–4 and270/268 phases3–5,
  * at every retained physical slot, with valid tables on both sides. */
 for(unsigned other=268;other<=269;other++)for(unsigned p=1;p<=5;p++)if((other==268&&p>=3)||(other==269&&p<=4))for(unsigned slot=0;slot<80;slot++)for(unsigned direction=0;direction<2;direction++) {
  defaults(8,full);unsigned k=p6m2_member(p);test_power=direction?8:other==269?5:4;emit(k,slot);CHECK(checked_head(k,slot));
  RearP1Birth saved=rear_p1_state.birth[slot];rear_p1_state.birth[slot].record=direction?other:270;bad_restore(k,slot);
  rear_p1_state.birth[slot]=saved;CHECK(!checked_head(k,slot));
 }
 /* Shared-cache bytes depend on raw/density; three simultaneous records
  * retain separate table-cell and record-payload validation. */
 for(unsigned p=1;p<=5;p++)for(unsigned broken=268;broken<=270;broken++)for(unsigned cell=0;cell<2;cell++) {
  unsigned k=p6m2_member(p);defaults(8,full);
  for(unsigned r=268;r<=270;r++)if(r==270||(r==268&&p>=3)||(r==269&&p<=4)){test_power=r==270?8:r==269?5:4;emit(k,r-268);CHECK(checked_head(k,r-268));}
  Asset *shared=&rear_p1_resources.cache[rear_p1_member(ids[k])][1].asset;Uint8 *payload=shared->rgba;unsigned opens=role_opens;
  if(cell)weaponPort[10].op[1][broken-265]++;else weapons[broken].attack[7]^=1;
  for(unsigned r=268;r<=270;r++)if(r==270||(r==268&&p>=3)||(r==269&&p<=4))CHECK(checked_head(k,r-268)==(r!=broken));
  CHECK(role_opens==opens&&shared->rgba==payload);
  if(cell)weaponPort[10].op[1][broken-265]--;else weapons[broken].attack[7]^=1;
  if(broken==270||(broken==268&&p>=3)||(broken==269&&p<=4))CHECK(!checked_head(k,broken-268));
 }
 for(unsigned p=1;p<=5;p++) {
  unsigned k=p6m2_member(p);defaults(8,full);
  for(unsigned r=268;r<=270;r++)if(r==270||(r==268&&p>=3)||(r==269&&p<=4)){test_power=r==270?8:r==269?5:4;emit(k,r-268);CHECK(checked_head(k,r-268));}
  Asset *shared=&rear_p1_resources.cache[rear_p1_member(ids[k])][1].asset;shared->rgba[0]^=1;
  for(unsigned r=268;r<=270;r++)if(r==270||(r==268&&p>=3)||(r==269&&p<=4))CHECK(!checked_head(k,r-268));
  shared->rgba[0]^=1;
  for(unsigned r=268;r<=270;r++)if(r==270||(r==268&&p>=3)||(r==269&&p<=4))CHECK(checked_head(k,r-268));
 }
 /* Mode1 down77 births survive independently; copied slot seals never do. */
 for(unsigned r=257;r<=259;r+=2)for(unsigned broken=0;broken<2;broken++) {
  defaults(8,full);test_power=r==257?3:7;emit(8,0);test_power=8;emit(8,1);CHECK(checked_head(8,0)&&checked_head(8,1));
  weapons[broken?270:r].attack[7]^=1;CHECK(checked_head(8,0)==(broken!=0));CHECK(checked_head(8,1)==(broken!=1));
 }
 for(unsigned p=1;p<=5;p++)for(unsigned slot=0;slot<80;slot++) {
  defaults(8,full);test_power=8;unsigned k=p6m2_member(p),copy=(slot+1)%80;emit(k,slot);CHECK(checked_head(k,slot));
  make_shot(k,copy);rear_p1_state.birth[copy]=rear_p1_state.birth[slot];rear_p1_state.birth_identity[copy]=rear_p1_state.birth_identity[slot];bad_restore(k,copy);CHECK(checked_head(k,slot));
 }
 CHECK(REAR_P1_HEADS==19&&REAR_P1_OBSERVED==21&&REAR_P1_MAX_BUDGET==7&&rear_p1_member(163)<0&&rear_p1_member(164)<0);
 test_power=1;
}
static void p6m2_linked_case(unsigned weapon,unsigned dir,unsigned route)
{
 unsigned k=dir==5?14:13;test_power=8;emit(k,0);CHECK(checked_head(k,0));
 CHECK(linkGunWeapons[weapon-1]==451&&linkMult2Gr[dir]==ids[k]);
 allocation_defaults(8,0);twoPlayerMode=twoPlayerLinked=route==0;
 unsigned port=route==0?0:route==1?weapon:10,pnum=route==0?2:1;
 GameState initial,observed,baseline;save_game(&initial);
 if(route)(render_mirror_rear_p1_call_begin)(port,1,5,1,pnum,451);
 JE_integer a=player_shot_create(port,1,100,100,100,100,451,pnum);CHECK(a>=0&&a<80);
 JE_real angle=(JE_real)(dir*(2*M_PI)/16);player_shot_set_direction(a,weapon,angle);save_game(&observed);CHECK(playerShotData[a].shotGr==ids[k]);
 load_game(&initial);JE_integer b=baseline_shot_create(port,1,100,100,100,100,451,pnum);CHECK(a==b);
 player_shot_set_direction(b,weapon,angle);save_game(&baseline);same_game(&observed,&baseline);load_game(&observed);
 CHECK(!rear_p1_state.birth[0].qualified&&!rear_p1_state.birth_identity[0]);for(unsigned slot=0;slot<80;slot++)CHECK(!rear_p1_state.birth[slot].qualified);
 CHECK(!rear_p1_state.pending&&!rear_p1_state.lease&&!rear_p1_state.remaining&&!rear_p1_state.call&&!rear_p1_table(451));
 unsigned opens=role_opens,before=generics;CHECK(!checked_head(k,(unsigned)a));
 draw_player_shot_sprite2(&surface,playerShotData[a].shotX+1,playerShotData[a].shotY,spriteSheet8,ids[k],(unsigned)a,ids[k]);
 CHECK(!last_mirrored&&generics==before+1&&role_opens==opens&&!suppress);test_power=1;
}
static void test_p6_mode2_linked_negatives(void)
{
 const unsigned ports[]={22,38},directions[]={5,11};
 for(int d=4;d<=8;d+=4)for(unsigned w=0;w<2;w++)for(unsigned a=0;a<2;a++)for(unsigned route=0;route<3;route++) {
  defaults(d,full);weapons[451]=weapons[270];weapons[451].multi=weapons[451].max=1;p6m2_linked_case(ports[w],directions[a],route);
 }
}
