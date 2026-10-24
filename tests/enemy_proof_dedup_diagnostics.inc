/* Diagnostic-only: included after the unchanged native P09 fixture helpers. */
static void diag_dump(const char *name,unsigned profile)
{
 printf("COUNTS {\"case\":\"%s\",\"profile\":%u,\"proof_calls\":%llu,\"used_slots\":%llu,\"domains\":[",name,profile,(unsigned long long)diag_proofs,(unsigned long long)diag_visits);
 for(unsigned i=0;i<6;i++)printf("%s{\"calls\":%llu,\"bytes\":%llu}",i?",":"",(unsigned long long)diag_calls[i],(unsigned long long)diag_bytes[i]);
 puts("]}");
}
static bool diag_live(unsigned slot,uint64_t expected)
{return enemy_reuse_identity_live_generation(slot,slot<ENEMY_SHOT_MAX?enemyShot[slot].sgr+enemyShot[slot].animate:0,slot<ENEMY_SHOT_MAX?enemyShot[slot].sx:0,slot<ENEMY_SHOT_MAX?enemyShot[slot].sy:0,expected);}
static void diag_tests(void)
{
 for(unsigned p=0;p<2;p++){
  p09_setup(p);p09_spawn();p05_update();CHECK(enemy_reuse_frame.contributed);
  unsigned count=p?3:1;
  for(unsigned repeat=0;repeat<2;repeat++){
   diag_reset();CHECK(enemy_reuse_proof());diag_dump(repeat?"repeat-proof":"proof",p);
   CHECK(diag_proofs==1&&diag_visits==count);
   CHECK(diag_calls[0]==DIAG_MULTIPLIER*count&&diag_bytes[0]==44079*DIAG_MULTIPLIER*count);
   CHECK(diag_calls[1]==DIAG_MULTIPLIER*count&&diag_bytes[1]==77*DIAG_MULTIPLIER*count);
   CHECK(diag_calls[2]==DIAG_MULTIPLIER*count&&diag_bytes[2]==80*DIAG_MULTIPLIER*count);
   CHECK(diag_calls[3]==1&&diag_bytes[3]==32060&&diag_calls[4]==3&&diag_bytes[4]==129024&&diag_calls[5]==1&&diag_bytes[5]==768);
  }
  uint64_t generation=enemy_reuse_identity_generation(0);CHECK(generation);
  for(unsigned repeat=0;repeat<2;repeat++){
   diag_reset();CHECK(enemy_reuse_identity_generation(0)==generation);diag_dump("independent-generation",p);CHECK(diag_calls[0]==1&&diag_bytes[0]==44079);
   diag_reset();CHECK(enemy_reuse_identity_live(0,enemyShot[0].sgr+enemyShot[0].animate,enemyShot[0].sx,enemyShot[0].sy));diag_dump("independent-live",p);CHECK(diag_calls[0]==1&&diag_bytes[0]==44079);
  }
  CHECK(diag_live(0,generation));CHECK(!diag_live(0,0));CHECK(!diag_live(0,generation+1));CHECK(!diag_live(ENEMY_SHOT_MAX,0));CHECK(!diag_live(~0u,generation));
  /* A pure failed proof does not revoke renderer state; the next boundary does. */
  Uint8 old=p09_actor[100];p09_actor[100]^=1;diag_reset();CHECK(!enemy_reuse_proof());diag_dump("mutated-proof-prefix",p);CHECK(diag_calls[0]==1&&diag_bytes[0]==44079);CHECK(!diag_live(0,generation));CHECK(!enemy_reuse_identity_generation(0));CHECK(!enemy_reuse_identity_live(0,enemyShot[0].sgr+enemyShot[0].animate,enemyShot[0].sx,enemyShot[0].sy));
  CHECK(!reject_reason);p09_actor[100]=old;CHECK(enemy_reuse_proof());
  enemy_reuse_shot_retire(0);CHECK(!diag_live(0,generation));CHECK(!diag_live(0,0));CHECK(!enemy_reuse_proof());
  p09_setup(p);p09_spawn();p05_update();generation=enemy_reuse_identity_generation(0);enemy_reuse_actor_allocated(enemy,p09_records_ids[p],0);CHECK(!diag_live(0,generation));CHECK(!enemy_reuse_proof());
  /* Native allocation/spawn reuse must not accept an old expected generation. */
  p09_setup(p);p09_spawn();generation=enemy_reuse_identity_generation(0);enemy_reuse_shot_spawn(0,0,p09_weapon_ids[p],1,0);uint64_t replacement=enemy_reuse_identity_generation(0);CHECK(replacement&&replacement!=generation);CHECK(diag_live(0,replacement));CHECK(!diag_live(0,generation));
  for(unsigned boundary=0;boundary<4;boundary++){
   p09_setup(p);p09_spawn();p05_update();CHECK(enemy_reuse_proof());
   if(boundary==2){finish();CHECK(last_output_valid);}
   /* Prove a fresh valid witness is not enough to bypass a changed bank.
    * Two individually witnessed native animation updates return profile0 to
    * its contributed phase; the valid witness must not authorize changed bytes. */
   if(boundary==3){
    if(!p)for(unsigned step=0;step<2;step++){enemy_reuse_shot_before_animation(0);enemyShot[0].animate=(enemyShot[0].animate+1)%2;enemy_reuse_shot_after_animation(0);}
    enemy_reuse_shot_begin_draw(0);CHECK(enemy_reuse_proof());
   }
   old=p09_actor[100];p09_actor[100]^=1;
   if(boundary==0){enemy_reuse_shot_begin_draw(0);CHECK(!render_mirror_enemy_reuse_shot(game_screen,enemyShot[0].sx,enemyShot[0].sy,spriteSheet8,enemyShot[0].sgr+enemyShot[0].animate,0,enemyShot[0].sgr));CHECK(reject_reason);}
   else if(boundary==3){CHECK(!render_mirror_enemy_reuse_shot(game_screen,enemyShot[0].sx,enemyShot[0].sy,spriteSheet8,enemyShot[0].sgr+enemyShot[0].animate,0,enemyShot[0].sgr));CHECK(reject_reason);}
   else if(boundary==1){finish();CHECK(!ready&&!last_output_valid&&!last_output_scene_hd);}
   else {CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!ready&&!last_output_valid&&!last_output_scene_hd);}
   p09_actor[100]=old;
   if(boundary==0||boundary==3){
    finish();CHECK(reject_reason&&!last_output_valid&&!last_output_scene_hd);
    /* The renderer may queue a wholly classic upscale after a rejected draw. */
    if(ready)for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++)CHECK(*pixel(output,x,y)==palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[(y/8)*VGAScreenSeg->pitch+x/8]));
   }else CHECK(!ready&&!last_output_valid&&!last_output_scene_hd);
   render_mirror_present(NULL,VGAScreenSeg,NULL);CHECK(!last_output_valid&&!last_output_scene_hd);
   printf("BOUNDARY profile=%u kind=%u rejected_no_hd_after_restore=1\n",p,boundary);
  }
 }
 puts("PASS proof diagnostics and independent/cross-proof mutation/lifecycle/fallback boundaries");
}
