/* Newly regenerated private read-only observers. Never production. */
static bool type3_window(void)
{return (game_probe_tick>=6181&&game_probe_tick<=6192)||(game_probe_tick>=6512&&game_probe_tick<=6531);}
static void type3_census(const char *phase)
{
 if(!asset_debug_enabled||!getenv("OT_LATE_CENSUS")||!type3_window())return;
 uint64_t before=mt_state_fingerprint();
 static FILE*f;if(!f){f=fopen("late-census.tsv","w");if(!f)exit(2);fprintf(f,"tick\tphase\teventLoc\tcurLoc\tdifficulty\tbackground3over\ttopEnemyOver\tslot\tavail\ttype\tbank\tbase\tcycle\tlink\tx\ty\tmapoffset\txc\tyc\tfixedmovey\txcc\tycc\txccw\txccadd\txaccel\tyaccel\tarmor\tground\ticed\tfilter\texplonum\tdamaged\tdgr\tdani\tdlevel\tdrop\tvalue\tscoreitem\tcash0\tcash1\tkilled\n");}
 for(int i=0;i<100;i++){
  const struct JE_SingleEnemyType*e=&enemy[i];int bank=-1;
  if(e->sprite2s)for(int b=0;b<4;b++)if(e->sprite2s->data==enemySpriteSheets[b].data)bank=enemySpriteSheetIds[b];
  unsigned int base=e->enemycycle>0&&e->enemycycle<=COUNTOF(e->egr)?e->egr[e->enemycycle-1]:0;
  fprintf(f,"%u\t%s\t%u\t%u\t%d\t%d\t%d\t%d\t%u\t%u\t%d\t%u\t%u\t%u\t%d\t%d\t%u\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%u\t%u\t%u\t%d\t%u\t%u\t%u\t%d\t%u\t%d\t%d\t%u\t%d\t%d\t%lu\t%lu\t%u\n",game_probe_tick,phase,eventLoc,curLoc,difficultyLevel,background3over,topEnemyOver,i,enemyAvail[i],e->enemytype,bank,base,e->enemycycle,e->linknum,e->ex,e->ey,e->mapoffset,e->exc,e->eyc,e->fixedmovey,e->excc,e->eycc,e->exccw,e->exccadd,e->xaccel,e->yaccel,e->armorleft,e->enemyground,e->iced,e->filter,e->explonum,e->edamaged,e->edgr,e->edani,e->edlevel,e->enemydie,e->evalue,e->scoreitem,(unsigned long)player[0].cash,(unsigned long)player[1].cash,enemyKilled);
 }
 fflush(f);if(before!=mt_state_fingerprint()){fprintf(stderr,"census changed RNG\n");exit(2);}
}
static void type3_effect_witness(int slot,int x,int y,int type)
{
 if(!getenv("OT_TYPE3_LIFECYCLE")||game_probe_tick<6513||game_probe_tick>6517)return;
 if(slot!=0||enemy[slot].enemytype!=3||!((game_probe_tick==6513&&type==0)||(game_probe_tick==6515&&type==0)||(game_probe_tick==6517&&type==1))){fprintf(stderr,"unexpected original effect call\n");exit(2);}
 static FILE*f;if(!f){f=fopen("type3-original-effects.tsv","w");if(!f)exit(2);fprintf(f,"tick\tslot\tenemytype\teffect_type\tx\ty\n");}
 fprintf(f,"%u\t%d\t3\t%d\t%d\t%d\n",game_probe_tick,slot,type,x,y);fflush(f);
}
