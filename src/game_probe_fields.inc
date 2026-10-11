/* Generated explicit-field hashing: excludes struct padding and address values. */
static uint64_t enemies_hash(void)
{
 uint64_t h=HASH_START; H(enemyAvail);
 for(int i=0;i<100;i++) {
  const struct JE_SingleEnemyType *p=&enemy[i];
  F(p,fillbyte); F(p,ex); F(p,ey); F(p,exc); F(p,eyc); F(p,exca); F(p,eyca); F(p,excc); F(p,eycc); F(p,exccw); F(p,eyccw); F(p,armorleft); F(p,eshotwait); F(p,eshotmultipos); F(p,enemycycle); F(p,ani); F(p,egr); F(p,size); F(p,linknum); F(p,aniactive); F(p,animax); F(p,aniwhenfire); F(p,exrev); F(p,eyrev); F(p,exccadd); F(p,eyccadd); F(p,exccwmax); F(p,eyccwmax); F(p,edamaged); F(p,enemytype); F(p,animin); F(p,edgr); F(p,edlevel); F(p,edani); F(p,fill1); F(p,filter); F(p,evalue); F(p,fixedmovey); F(p,freq); F(p,launchwait); F(p,launchtype); F(p,launchfreq); F(p,xaccel); F(p,yaccel); F(p,tur); F(p,enemydie); F(p,enemyground); F(p,explonum); F(p,mapoffset); F(p,scoreitem); F(p,special); F(p,flagnum); F(p,setto); F(p,iced); F(p,launchspecial); F(p,xminbounce); F(p,xmaxbounce); F(p,yminbounce); F(p,ymaxbounce); F(p,fill);
 }
 for(int i=0;i<100;i++) {
  int role=-1;
  for(int j=0;j<4;j++) if(enemy[i].sprite2s==&enemySpriteSheets[j]) role=j;
  if(enemy[i].sprite2s==&spriteSheet8) role=8; if(enemy[i].sprite2s==&spriteSheet9) role=9;
  if(enemy[i].sprite2s==&spriteSheet10) role=10; if(enemy[i].sprite2s==&spriteSheet11) role=11;
  if(enemy[i].sprite2s==&spriteSheet12) role=12; H(role);
  intptr_t offset=enemy[i].enemydatofs?(intptr_t)enemy[i].enemydatofs-(intptr_t)enemyDat:-1; H(offset);
 }
 H(enemySpriteSheetIds); return h;
}
static uint64_t shots_hash(void)
{
 uint64_t h=HASH_START; H(shotAvail); H(enemyShotAvail);
 for(int i=0;i<MAX_PWEAPON+1;i++) {
  const PlayerShotDataType *p=&playerShotData[i];
  F(p,shotX); F(p,shotY); F(p,shotXM); F(p,shotYM); F(p,shotXC); F(p,shotYC); F(p,shotComplicated); F(p,shotDevX); F(p,shotDirX); F(p,shotDevY); F(p,shotDirY); F(p,shotCirSizeX); F(p,shotCirSizeY); F(p,shotTrail); F(p,shotGr); F(p,shotAni); F(p,shotAniMax); F(p,shotDmg); F(p,shotBlastFilter); F(p,chainReaction); F(p,playerNumber); F(p,aimAtEnemy); F(p,aimDelay); F(p,aimDelayMax);
 }
 for(int i=0;i<ENEMY_SHOT_MAX;i++) {
  const EnemyShotType *p=&enemyShot[i];
  F(p,sx); F(p,sy); F(p,sxm); F(p,sym); F(p,sxc); F(p,syc); F(p,tx); F(p,ty); F(p,sgr); F(p,sdmg); F(p,duration); F(p,animate); F(p,animax); F(p,fill);
 }
 return h;
}
static uint64_t particles_hash(void)
{
 uint64_t h=HASH_START;
 for(int i=0;i<MAX_EXPLOSIONS;i++) {
  const Explosion *p=&explosions[i];
  F(p,ttl); F(p,x); F(p,y); F(p,sprite); F(p,followPlayer); F(p,fixedPosition); F(p,deltaY);
 }
 for(int i=0;i<MAX_REPEATING_EXPLOSIONS;i++) {
  const rep_explosion_type *p=&rep_explosions[i];
  F(p,delay); F(p,ttl); F(p,x); F(p,y); F(p,big);
 }
 for(int i=0;i<MAX_SUPERPIXELS;i++) {
  const superpixel_type *p=&superpixels[i];
  F(p,x); F(p,y); F(p,z); F(p,delta_x); F(p,delta_y); F(p,color);
 }
 return h;
}
