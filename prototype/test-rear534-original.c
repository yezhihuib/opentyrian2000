/* Rear534-only bounded cases; exact extracted original source is above. */
static void test_rear_reward(void)
{
 const int ids[]={0,15},powers[]={1,10,11};
 for(size_t id=0;id<COUNTOF(ids);id++)for(size_t pw=0;pw<COUNTOF(powers);pw++)for(int two=0;two<2;two++)for(int who=1;who<=2;who++)for(int linked=0;linked<2;linked++) {
  reset();twoPlayerMode=two;twoPlayerLinked=linked;int target=two?1:0;
  for(int p=0;p<2;p++){player[p].items.weapon[REAR_WEAPON].id=ids[id];player[p].items.weapon[REAR_WEAPON].power=powers[pw];player[p].purple_balls_needed=77;}
  memset(shotMultiPos,7,sizeof(shotMultiPos));seed_coin(534,147);collect_scoreitem(20,(JE_byte)who);
  bool up=ids[id]!=0 && powers[pw]<11;
  CHECK(enemyAvail[20]==1 && text_calls==1 && soundQueue[7]==S_POWERUP);
  CHECK(!strcmp(last_text,two?"P2 rear power":"rear power"));
  for(int p=0;p<2;p++){
   CHECK(player[p].cash==(p?2000UL:1000UL)+((p==target && !up)?1000UL:0));
   CHECK(player[p].items.weapon[REAR_WEAPON].id==ids[id] && player[p].items.weapon[REAR_WEAPON].power==powers[pw]+(p==target && up));
   CHECK(player[p].purple_balls_needed==(p==target && up?4:77));
  }
  CHECK(shotMultiPos[REAR_WEAPON]==(up?0:7) && shotMultiPos[FRONT_WEAPON]==7);
  CHECK(explosions[0].ttl==7 && explosions[0].sprite==144 && explosions[0].x==98 && explosions[0].y==147 && explosions[0].fixedPosition && !explosions[0].followPlayer && explosions[0].deltaY==0);
  scenarios++;
 }
 for(int difficulty=-1;difficulty<=10;difficulty++){
  reset();difficultyLevel=difficulty;seed_coin(534,147);CHECK(enemy[20].evalue==-2 && enemyAvail[20]==2 && enemy[20].armorleft==255 && enemy[20].size==1 && enemy[20].sprite2s==&spriteSheet11 && enemy[20].scoreitem && enemy[20].enemycycle==0 && enemy[20].ani==12 && rng_calls==1);
  collect_scoreitem(20,1);CHECK(player[0].cash==2000 && player[0].items.weapon[REAR_WEAPON].id==0);scenarios++;
 }
 puts("PASS original rear reward: equipped powers1/10 increment/reset/purple; None/max11 cash1000; two-player target, collector/linked isolation; all12 difficulty values preserve-2");
}
static void test_rear_collection_bounds(void)
{
 const int dx[]={-12,-11,0,11,12},dy[]={-14,-13,0,13,14};
 for(size_t x=0;x<COUNTOF(dx);x++)for(size_t y=0;y<COUNTOF(dy);y++){
  reset();seed_coin(534,147);player[0].x=98+dx[x];player[0].y=147+dy[y];bool hit=abs(dx[x])<12 && abs(dy[y])<14;collect_near(1);
  CHECK(enemyAvail[20]==(hit?1:2) && player[0].cash==(hit?2000UL:1000UL) && text_calls==hit && explosions[0].ttl==(hit?7:0));scenarios++;
 }
 reset();seed_coin(534,95);enemy[20].ex=106;enemy[20].mapoffset=0;player[0].x=133;player[0].y=95;collect_near(1);CHECK(enemyAvail[20]==2 && text_calls==0 && enemy[20].mapoffset==0);scenarios++;
 puts("PASS exact collection envelope strictdx12/dy14; newborn mapoffset0 preserved");
}
static void test_rear_effects(void)
{
 for(int style=0;style<2;style++)for(int fixed=0;fixed<2;fixed++){
  Explosion history[9][MAX_EXPLOSIONS];struct Draw expected[256];int count=0;
  for(int candidate=0;candidate<2;candidate++){
   reset();explosionTransparent=style;JE_setupExplosion(140,147,0,0,fixed,false);
   for(int frame=0;frame<9;frame++){
    if(candidate){draw_candidate();CHECK(!memcmp(history[frame],explosions,sizeof(explosions)));}
    else {draw_original();memcpy(history[frame],explosions,sizeof(explosions));}
    CHECK(draw_count==(frame<7?frame+1:7));
   }
   CHECK(draw_count==7);
   if(candidate){CHECK(draw_count==count && !memcmp(expected,draws,sizeof(expected)));check_gates(count);}
   else {count=draw_count;memcpy(expected,draws,sizeof(expected));}
  }
  for(int i=0;i<7;i++)CHECK(draws[i].id==(fixed?145:146+i) && draws[i].ttl==7-i && draws[i].x==140 && draws[i].y==(fixed?147:147+3*(i+1)) && draws[i].style==style);
  scenarios++;
 }
 const int ys[]={-17,-16,-15,0,186,187,188,189,190,191};
 for(size_t k=0;k<COUNTOF(ys);k++)for(int style=0;style<2;style++){
  reset();explosionTransparent=style;seed_coin(534,ys[k]);collect_scoreitem(20,1);bool admitted=ys[k]>-16 && ys[k]<190;
  CHECK(enemyAvail[20]==1 && player[0].cash==2000 && text_calls==1 && (explosions[0].ttl!=0)==admitted);draw_candidate();CHECK(draw_count==(admitted && ys[k]<=186));check_gates(draw_count);scenarios++;
 }
 reset();for(int i=0;i<MAX_EXPLOSIONS;i++)explosions[i]=(Explosion){.ttl=7,.x=(JE_integer)i,.y=33,.sprite=144,.fixedPosition=true};Explosion before[MAX_EXPLOSIONS];memcpy(before,explosions,sizeof(before));seed_coin(534,147);collect_scoreitem(20,1);CHECK(!memcmp(before,explosions,sizeof(before)) && enemyAvail[20]==1 && player[0].cash==2000 && text_calls==1);scenarios++;
 puts("PASS fixed145 seven draws plus two clear steps, moving146..152 exclusion, NORMAL/BLEND; y admission/cancellation and full200 effect pool preserve reward");
}
static void test_rear_motion(void)
{
 static const int seq[]={203,203,203,205,205,205,207,207,207,205,205,205};
 static const int part[]={0,1,19,20},ox[]={-6,6,-6,6},oy[]={-7,-7,7,7};
 reset();seed_coin(534,95);enemy[20].ex=106;tempMapXOfs=34;tempBackMove=0;
 for(int f=0;f<24;f++){
  enemy[20].filter=9;move_coin(20);CHECK(body_count==(f+1)*4 && enemy[20].enemycycle==f%12+1 && enemy[20].ey==96+f && enemy[20].filter==0);
  for(int q=0;q<4;q++){struct BodyDraw *d=&body_draws[f*4+q];CHECK(d->id==seq[f%12]+part[q] && d->x==140+ox[q] && d->y==95+f+oy[q] && d->filter==9 && d->cycle==f%12+1);}
 }
 CHECK(rng_calls==1);scenarios++;
 const int xs[]={-63,-62,265,266},ys[]={-27,-26,-25,-14,-13,-12,181,182};
 for(size_t x=0;x<COUNTOF(xs);x++)for(size_t y=0;y<COUNTOF(ys);y++){
  reset();seed_coin(534,ys[y]);enemy[20].ex=xs[x];tempMapXOfs=34;tempBackMove=0;enemy[20].filter=9;move_coin(20);bool gate=xs[x]+34>-29 && xs[x]+34<300;int n=gate?2*(ys[y]>-13)+2*(ys[y]>-26 && ys[y]<182):0;
  CHECK(body_count==n && enemy[20].enemycycle==(gate?1:0) && enemy[20].filter==(gate?0:9));scenarios++;
 }
 reset();seed_coin(534,190);tempBackMove=3;move_coin(20);CHECK(enemyAvail[20]==1 && enemy[20].ey==191);scenarios++;
 puts("PASS24 held draws/96 ordered quadrants, exact origin/filter, x-gate cycle pause, vertical quadrant gates and removal before background movement");
}
static void test_rear_pool_modes(void)
{
 for(int vacant=0;vacant<2;vacant++){
  reset();apply_event(&rear_events[0]);CHECK(b==1 && enemy[0].enemytype==10 && enemy[0].ex==10 && enemy[0].ey==-28 && enemy[0].eyc==3 && enemy[0].armorleft==3 && enemy[0].evalue==15 && enemy[0].enemydie==0 && rng_calls==1);
  apply_event(&rear_events[1]);CHECK(enemy[0].excc==12 && enemy[0].eycc==-6 && enemy[0].exccw==12 && enemy[0].eyccw==6);
  apply_event(&rear_events[2]);CHECK(enemy[0].enemydie==534 && enemy[0].linknum==1);
  for(int i=1;i<25;i++){enemyAvail[i]=0;enemy[i].linknum=99;enemy[i].enemytype=10;}if(vacant)enemyAvail[7]=1;
  enemy[0].ex=106;enemy[0].ey=95;enemy[0].mapoffset=34;carrier_count=1;carriers[0]=(struct Carrier){0,10,106,95,false,0};unsigned prior=rng_calls;observe_pair=true;linked_death(0);observe_pair=false;
  CHECK(allocation_calls==1 && release_calls==1 && enemyAvail[0]==1 && enemyKilled==1 && player[0].cash==1015 && rng_calls==prior+(unsigned)vacant && carriers[0].cash_at_release==1015);
  CHECK(allocations[0].offset==0 && allocations[0].type==534 && allocations[0].first_free==(vacant?7:-1) && allocations[0].result==(vacant?8:0));
  if(vacant){CHECK(enemy[7].enemytype==534 && enemyAvail[7]==2 && enemy[7].ex==106 && enemy[7].ey==95 && enemy[7].mapoffset==0 && enemy[7].sprite2s==&spriteSheet11);collect_scoreitem(7,1);CHECK(player[0].cash==2015 && enemyAvail[7]==1);}
  else {CHECK(JE_newEnemy(0,534,0)==1 && enemyAvail[0]==2 && enemy[0].enemytype==534);}
  scenarios++;
 }
 /* Early death retains the unassigned table drop0. */
 reset();apply_event(&rear_events[0]);mode_control=true;linked_death(0);mode_control=false;CHECK(enemyKilled==1 && factory_calls==1 && player[0].cash==1015 && rng_calls==1 && enemyAvail[1]==1);scenarios++;
 for(int st=0;st<2;st++)for(int two=0;two<2;two++)for(int action=0;action<2;action++)for(int arcade=0;arcade<2;arcade++){
  reset();apply_event(&rear_events[0]);superTyrian=st;twoPlayerMode=two;onePlayerAction=action;superArcadeMode=arcade;unsigned prior=rng_calls;apply_event(&rear_events[2]);int expected=arcade?827:st?828+superTyrianSpecials[rng_stream[prior%COUNTOF(rng_stream)]%4]:534;
  CHECK(enemy[0].enemydie==expected && rng_calls-prior==(unsigned)(!arcade && st));scenarios++;
 }
 for(int arcade=0;arcade<2;arcade++){
  reset();superArcadeMode=arcade;seed_coin(534,147);CHECK(enemy[20].enemytype==(arcade?533:534) && enemy[20].evalue==(arcade?-1:-2) && rng_calls==1);scenarios++;
 }
 puts("PASS exact event6 spawn/event16 acceleration/event17 assignment; early death no drop; allocation before release, fullpool omission/reuse and RNG;16 mode combinations plus constructor arcade remap");
}
int main(void)
{
 test_rear_reward();test_rear_collection_bounds();test_rear_effects();test_rear_motion();test_rear_pool_modes();
 printf("RESULT {\"status\":\"PASS\",\"scenarios\":%u,\"checks\":%u,\"evidence_kind\":\"source-unit-only\",\"gameplay_runs\":0}\n",scenarios,checks);return 0;
}
