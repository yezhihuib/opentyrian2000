/* Newly regenerated private fixture. Original projectile helper owns creation. */
static void type3_require(bool ok,const char*why)
{if(!ok){fprintf(stderr,"type3 fixture guard tick%u: %s\n",game_probe_tick,why);exit(2);}}
static void type3_guard_pulse(void)
{
 if(!getenv("OT_TYPE3_LIFECYCLE")||!(game_probe_tick==6513||game_probe_tick==6515||game_probe_tick==6517))return;
 const int n=(game_probe_tick-6513)/2;struct JE_SingleEnemyType*e=&enemy[0];
 uint64_t rng=mt_state_fingerprint();
 type3_require(asset_debug_enabled&&enemyAvail[0]==0&&e->enemytype==3&&e->size==0&&e->linknum==0&&e->enemyground,"live original target");
 int bank=-1;if(e->sprite2s)for(int i=0;i<4;i++)if(e->sprite2s->data==enemySpriteSheets[i].data)bank=enemySpriteSheetIds[i];
 type3_require(bank==1&&e->enemycycle==3+2*n&&e->ex==111+2*n&&e->ey==116+12*n&&e->mapoffset==41,"live bank/cycle/position");
 type3_require(e->armorleft==(n==0?2:1)&&e->iced==(n==2?38:0)&&e->filter==(n==2?9:0),"live armor/ice/filter");
 type3_require(!e->edgr&&!e->edani&&!e->edlevel&&!e->edamaged&&!e->enemydie&&!e->explonum&&!e->scoreitem&&!e->special&&e->evalue==5,"original lifecycle");
 type3_require(!e->launchfreq&&!e->freq[0]&&!e->freq[1]&&!e->freq[2]&&!skyEnemyOverAll,"no own launch/turret or late sky lane");
 static const unsigned int cycle[12]={171,171,190,190,209,209,228,228,247,247,266,266};
 for(int i=0;i<12;i++)type3_require(e->egr[i]==cycle[i],"original animation table");
 for(int i=0;i<MAX_PWEAPON;i++)type3_require(!shotAvail[i],"player shot pool empty");
 type3_require(pending_slot<0&&shotMultiPos[SHOT_MISC]<=1&&weaponPort[1].poweruse==30&&power>=30,"original projectile capacity/power");
 for(unsigned int i=0;i<COUNTOF(boss_bar);i++)type3_require(boss_bar[i].link_num!=255,"unrelated sentinel boss link");
 int active=0;for(int i=0;i<MAX_EXPLOSIONS;i++)active+=explosions[i].ttl>0;
 type3_require(active==n&&active<MAX_EXPLOSIONS,"effect capacity and prior lifecycle");
 for(int i=0;i<MAX_REPEATING_EXPLOSIONS;i++)type3_require(!rep_explosions[i].ttl,"no unrelated repeater");
 int sx=e->ex+e->mapoffset,sy=e->ey-6,hits=0;
 type3_require(sx>=24&&sx<288&&sy>=0&&sy<184,"visible shot position");
 for(int i=0;i<100;i++){
  const struct JE_SingleEnemyType*q=&enemy[i];
  type3_require(!(i!=0&&enemyAvail[i]!=1&&q->enemyground&&q->linknum==255),"unrelated live ground link255 (original link0 sentinel)");
  bool hit=enemyAvail[i]==0&&((q->enemycycle==0&&abs(q->ex+q->mapoffset-sx)<25&&abs(q->ey-sy-12)<29)||(q->enemycycle>0&&abs(q->ex+q->mapoffset-sx)<13&&abs(q->ey-sy-6)<15));
  if(hit){type3_require(i==0,"other original collision target");hits++;}
 }
 type3_require(hits==1&&rng==mt_state_fingerprint(),"unique collision and read-only guard RNG");
 static FILE*f;if(!f){f=fopen("type3-pulse-guards.tsv","w");type3_require(f!=NULL,"guard log");fprintf(f,"tick\ttarget\ttype\tbank\tbase\tcycle\tarmor\ticed\tfilter\tshot_x\tshot_y\tunique_candidates\talias255\n");}
 fprintf(f,"%u\t0\t3\t%d\t%u\t%u\t%u\t%u\t%u\t%d\t%d\t0\t0\n",game_probe_tick,bank,e->egr[e->enemycycle-1],e->enemycycle,e->armorleft,e->iced,e->filter,sx,sy);fflush(f);
 pending_slot=0;pending_damage=n==0?1:n==1?99:0;
}
static void type3_check_shot(int shot,const PlayerShotDataType*s)
{
 if(!getenv("OT_TYPE3_LIFECYCLE"))return;
 type3_require(shot==0&&shot!=MAX_PWEAPON-1&&shotAvail[shot]==255&&s->shotGr==59&&s->shotAni==0&&s->shotAniMax==1&&s->shotTrail==255&&s->shotBlastFilter==208&&s->playerNumber==1&&!s->chainReaction&&!s->aimAtEnemy&&!s->shotXM&&!s->shotYM&&!s->shotXC&&!s->shotYC&&!s->shotComplicated,"original pulse with only approved overrides");
 type3_require(s->shotX==enemy[0].ex+enemy[0].mapoffset&&s->shotY==enemy[0].ey-6&&s->shotDmg==(game_probe_tick==6515?99:1),"live post-override position and damage");
 static FILE*f;if(!f){f=fopen("type3-pulse-shots.tsv","w");type3_require(f!=NULL,"shot log");fprintf(f,"tick\tshot\tdamage\tx\ty\txm\tym\txc\tyc\tframe\tani\tanimax\tfilter\ttrail\tttl\tplayer\tchain\taim\tcomplicated\tpower_after\n");}
 fprintf(f,"%u\t%d\t%u\t%d\t%d\t%d\t%d\t%d\t%d\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%u\t%d\t%u\n",game_probe_tick,shot,s->shotDmg,s->shotX,s->shotY,s->shotXM,s->shotYM,s->shotXC,s->shotYC,s->shotGr,s->shotAni,s->shotAniMax,s->shotBlastFilter,s->shotTrail,shotAvail[shot],s->playerNumber,s->chainReaction,s->aimAtEnemy,s->shotComplicated,power);fflush(f);
}
static void type3_effect_pool(void)
{
 if(!getenv("OT_TYPE3_LIFECYCLE")||game_probe_tick<6512||game_probe_tick>6531)return;
 static FILE*f;if(!f){f=fopen("type3-explosion-census.tsv","w");type3_require(f!=NULL,"effect log");fprintf(f,"tick\tslot\tttl\tsprite\tx\ty\tdeltaY\tfixed\tfollow\n");}
 for(int i=0;i<MAX_EXPLOSIONS;i++){const Explosion*e=&explosions[i];fprintf(f,"%u\t%d\t%u\t%u\t%d\t%d\t%d\t%d\t%d\n",game_probe_tick,i,e->ttl,e->sprite,e->x,e->y,e->deltaY,e->fixedPosition,e->followPlayer);}fflush(f);
}
