/* Additive finite250 tests; use the unchanged historical original-engine oracle. */
static void test_red250(void)
{
 static const int sequence[]={14,14,15,15,16,16,17,17,18,18,17,17,16,16,15,15};
 const int numer[]={6,6,8,8,9,12,16,20,32,32,64,64};
 for(int difficulty=-1;difficulty<=10;difficulty++)for(int linked=0;linked<2;linked++)for(int who=1;who<=2;who++) {
  reset();difficultyLevel=difficulty;twoPlayerLinked=linked;seed_coin(395,150);int v=250*numer[difficulty+1]/8;
  CHECK(enemy[20].evalue==v && enemy[20].sprite2s==&spriteSheet11 && enemy[20].scoreitem && enemy[20].armorleft==255 && enemy[20].linknum==0 && enemy[20].enemycycle==0);
  CHECK(rng_calls==1 && enemy[20].egr[0]==14 && enemy[20].egr[15]==15);collect_scoreitem(20,(JE_byte)who);
  CHECK(player[0].cash==1000UL+(linked?v/2:(who==1?v:0)) && player[1].cash==2000UL+(linked?v/2:(who==2?v:0)));expect_popup(395,150);
  CHECK(enemyAvail[20]==1 && soundQueue[7]==S_ITEM);draw_candidate();check_gates(1);CHECK(gates250[0] && !gates100[0] && !gates25[0] && !gates50[0] && !gates75[0]);
  JE_makeEnemy(&enemy[30],17,0);CHECK(enemy[30].evalue==20*numer[difficulty+1]/8);scenarios++;
 }
 reset();seed_coin(395,-7);enemy[20].ex=130;tempMapXOfs=28;tempBackMove=0;
 for(int frame=0;frame<32;frame++){move_coin(20);CHECK(body_count==frame+1 && body_draws[frame].id==sequence[frame%16] && body_draws[frame].cycle==frame%16+1);CHECK(body_draws[frame].x==158 && body_draws[frame].y==-7+frame && enemy[20].ey==-6+frame && enemyAvail[20]==2);}
 CHECK(rng_calls==1);scenarios++;
 const int dxs[]={-12,-11,0,11,12},dys[]={-14,-13,0,13,14};
 for(size_t x=0;x<COUNTOF(dxs);x++)for(size_t y=0;y<COUNTOF(dys);y++){
  reset();seed_coin(395,150);player[0].x=98+dxs[x];player[0].y=150+dys[y];bool hit=abs(dxs[x])<12 && abs(dys[y])<14;collect_near(1);
  CHECK(enemyAvail[20]==(hit?1:2) && player[0].cash==1000UL+(hit?250:0) && explosions[0].ttl==(hit?8:0));scenarios++;
 }
 for(int style=0;style<2;style++)for(int fixed=0;fixed<2;fixed++) {
  Explosion history[12][MAX_EXPLOSIONS];struct Draw expected[256];int count=0;
  for(int candidate=0;candidate<2;candidate++) {
   reset();explosionTransparent=style;JE_setupExplosion(98,40,0,fixed?40:36,fixed,false);
   for(int frame=0;frame<12;frame++) {if(candidate){draw_candidate();CHECK(!memcmp(history[frame],explosions,sizeof(explosions)));}else{draw_original();memcpy(history[frame],explosions,sizeof(explosions));}}
   CHECK(draw_count==8);if(candidate){CHECK(draw_count==count && !memcmp(expected,draws,sizeof(expected)));check_gates(count);}else{count=draw_count;memcpy(expected,draws,sizeof(expected));}
  }
  for(int i=0;i<8;i++){CHECK(draws[i].id==(fixed?188:186+i) && draws[i].ttl==8-i);CHECK(gates250[i]==!!fixed && !gates25[i] && !gates50[i] && !gates75[i] && !gates100[i]);}scenarios++;
 }
 /* All five original fixed labels preserve ascending pool order and state. */
 for(int shift=0;shift<5;shift++)for(int style=0;style<2;style++) {
  int kinds[]={36,37,38,39,40},ordered[5];for(int i=0;i<5;i++)ordered[i]=kinds[(i+shift)%5];compare_effects(ordered,5,style,true);
 }
 const int ys[]={-17,-16,-15,0,186,187,188,189,190,191};
 for(size_t k=0;k<COUNTOF(ys);k++){reset();seed_coin(395,ys[k]);collect_scoreitem(20,1);bool admitted=ys[k]>-16 && ys[k]<190;CHECK((explosions[0].ttl!=0)==admitted && enemyAvail[20]==1 && player[0].cash==1250);draw_candidate();CHECK(draw_count==(admitted && ys[k]<=186));check_gates(draw_count);scenarios++;}
 for(int kind=0;kind<3;kind++){reset();JE_setupExplosion(98,40,0,40,true,false);if(kind==0)explosions[0].followPlayer=true;if(kind==1)explosions[0].deltaY=1;if(kind==2)explosions[0].ttl=9;draw_candidate();CHECK(draw_count==1 && !gates250[0]);check_gates(1);scenarios++;}
 reset();for(int i=0;i<MAX_EXPLOSIONS;i++)explosions[i]=(Explosion){.ttl=8,.x=(JE_integer)i,.y=33,.sprite=187,.fixedPosition=true};Explosion before[MAX_EXPLOSIONS];memcpy(before,explosions,sizeof(before));seed_coin(395,150);collect_scoreitem(20,1);CHECK(!memcmp(before,explosions,sizeof(before)) && enemyAvail[20]==1 && player[0].cash==1250);scenarios++;
 /* Original event15 is SKY0..24: carrier17 turret59/frequency0 is valid. */
 for(int vacant=0;vacant<2;vacant++) {
  reset();apply_event(&red_events[0]);CHECK(b==1 && enemyAvail[0]==0 && enemy[0].enemytype==17 && enemy[0].ex==130 && enemy[0].ey==-28 && enemy[0].eyc==3 && enemy[0].size==1 && enemy[0].tur[0]==59 && enemy[0].freq[0]==0 && enemy[0].armorleft==5 && enemy[0].evalue==20 && rng_calls==0);
  apply_event(&red_events[1]);CHECK(enemy[0].enemydie==395 && enemy[0].linknum==10);
  for(int i=1;i<25;i++){enemyAvail[i]=0;enemy[i].linknum=99;enemy[i].enemytype=10;}if(vacant)enemyAvail[23]=1;
  enemy[0].ey=-7;enemy[0].mapoffset=28;mode_control=true;unsigned prior=rng_calls;linked_death(0);mode_control=false;
  CHECK(enemyAvail[0]==1 && enemyKilled==1 && player[0].cash==1020 && release_calls==1 && rng_calls==prior+(unsigned)vacant);
  if(vacant){CHECK(enemyAvail[23]==2 && enemy[23].enemytype==395 && enemy[23].ex==130 && enemy[23].ey==-7 && enemy[23].sprite2s==&spriteSheet11 && enemy[23].enemycycle==0);collect_scoreitem(23,1);CHECK(player[0].cash==1270 && enemyAvail[23]==1);}
  else {for(int i=1;i<25;i++)CHECK(enemy[i].enemytype!=395);CHECK(JE_newEnemy(0,395,0)==1 && enemyAvail[0]==2 && enemy[0].enemytype==395);}
  scenarios++;
 }

 puts("PASS red250: source395 held16, original constructor/RNG/SKY pool, strict collection, difficulty/link splits, fixed40 eight188 draws, moving36 exclusion, five-family order, bounds/full effect pool and original/candidate state parity");
}
