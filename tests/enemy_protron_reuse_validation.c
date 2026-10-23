/* Independent P09 native-production fixture. P05 helper bytes are extracted
 * unchanged by the runner; controlled scheduling is not a gameplay capture. */
#include "native_p05_helpers.inc"
static Uint8 p09_records[7][77],p09_weapons[5][80],p09_actor[44079],p09_actor6[39025];
static const unsigned p09_records_ids[]={133,129,134,216,218,224,225};
static const unsigned p09_weapon_ids[]={141,134,135,38,37};
static unsigned p09_profile;
static void p09_setup(unsigned profile)
{
 p05_setup(false);p09_profile=profile;
 for(unsigned i=0;i<7;i++){current_record=p09_records_ids[i];record_load(p09_records[i]);}
 for(unsigned i=0;i<5;i++)weapon_load(p09_weapon_ids[i],p09_weapons[i]);
 episodeNum=3;lvlFileNum=1;enemySpriteSheetIds[0]=3;enemySpriteSheets[0]=(Sprite2_array){sizeof(p09_actor),p09_actor};enemySpriteSheetIds[1]=6;enemySpriteSheets[1]=(Sprite2_array){sizeof(p09_actor6),p09_actor6};
}
static void p09_spawn(void)
{
 unsigned rec=p09_records_ids[p09_profile],w=p09_weapon_ids[p09_profile],count=p09_profile?3:1;
 CHECK(enemyDat[rec].tur[0]==w&&enemyDat[rec].freq[0]==(p09_profile?28:40)&&enemyDat[rec].shapebank==3);
 CHECK(weapons[w].max==count&&weapons[w].multi==count&&weapons[w].weapani==(p09_profile?0:2));
 CHECK(weapons[w].sg[0]==(p09_profile?244:226));if(p09_profile)CHECK(weapons[w].sg[1]==227&&weapons[w].sg[2]==227);
 enemyAvail[0]=JE_makeEnemy(enemy,rec,0);CHECK(!enemyAvail[0]);enemy[0].ex=110;enemy[0].ey=80;enemy[0].eshotwait[0]=1;JE_drawEnemy(25);
 for(unsigned i=0;i<count;i++){CHECK(!enemyShotAvail[i]);CHECK(enemyShot[i].sgr==weapons[w].sg[i]);CHECK(!enemyShot[i].animate&&enemyShot[i].animax==(p09_profile?0:2));CHECK(enemy_reuse_identity_generation(i));}
}
static void p09_oracle(Uint32 *want,unsigned slot)
{
 EnemyShotType *s=&enemyShot[slot];unsigned f=s->sgr+s->animate;CHECK(f==226||f==227||f==244);unsigned member=f==226?9:f==227?10:11;const Uint8 *rgba=enemy_reuse_resources.members[member].rgba;CHECK(rgba);
 for(int y=0;y<112;y++)for(int x=0;x<96;x++){int dx=s->sx*8+x,dy=s->sy*8+y;if(dx<0||dx>=canvas->w||dy<0||dy>=canvas->h)continue;size_t n=(size_t)dy*canvas->w+dx;want[n]=alpha_over(want[n],rgba+4*(y*96+x));}
}
static void p09_positive(void)
{
 for(unsigned p=0;p<2;p++){
  p09_setup(p);p09_spawn();
  for(unsigned tick=0;tick<6;tick++){
   if(tick){SDL_FillRect(game_screen,NULL,0x1b);render_mirror_begin();}
   Uint32 *want=canvas_copy();unsigned n=draws;p05_update();CHECK(draws-n==(p?3:1));CHECK(!green_head_count&&!global_green_contributed);
   for(unsigned i=0;i<(p?3:1);i++){CHECK(enemyShot[i].animate==(p?0:(tick+1)%2));CHECK(enemyShot[i].sgr==(p?(i?227:244):226));p09_oracle(want,i);}verify_rgb(want);free(want);
  }
 }
 p09_setup(0);p09_spawn();p05_update();const Uint8 *rgba=enemy_reuse_resources.members[10].rgba;Uint8 dec[336];CHECK(decode_tile(spriteSheet8,227,dec,dec+168,12,0,0));unsigned partial=0,outside=0;
 for(unsigned y=0;y<112;y++)for(unsigned x=0;x<96;x++){unsigned a=rgba[4*(y*96+x)+3];partial+=a>0&&a<255;outside+=a&&!dec[168+(y/8)*12+x/8];}CHECK(partial==2552&&outside==2);
}
static void p09_negatives(void)
{
 for(unsigned p=0;p<2;p++)for(unsigned bad=0;bad<19;bad++){
  p09_setup(p);p09_spawn();unsigned w=p09_weapon_ids[p];Uint8 old=p09_actor[100];
  switch(bad){case 0:enemyShot[0].sgr=227;break;case 1:enemyShot[0].animax++;break;case 2:enemyShot[0].animate=1;break;case 3:enemyShot[0].sdmg++;break;case 4:weapons[w].sg[0]=227;break;case 5:episodeNum=2;break;case 6:lvlFileNum=2;break;case 7:enemy_reuse_shot_retire(0);break;case 8:p09_actor[100]^=1;break;case 9:enemy_reuse_bank_changed(&enemySpriteSheets[0]);break;case 10:enemySpriteSheetIds[0]=6;break;case 11:enemy_reuse_shot_spawn(0,0,w,2,0);break;case 12:enemy_reuse_shot_spawn(0,0,w,1,p?1:1);break;case 13:enemyAvail[0]=1;enemyAvail[0]=JE_makeEnemy(enemy,p09_records_ids[p],0);break;case 14:enemy_reuse_shot_spawn(0,0,135,1,0);break;case 15:game_probe_density=4;break;case 16:xmas=true;break;case 17:rgb_palette[0]^=1;break;case 18:enemyShotAvail[0]=1;break;}
  if(p==0){enemy_reuse_shot_before_animation(0);enemyShot[0].animate=(enemyShot[0].animate+1)%2;enemy_reuse_shot_after_animation(0);}
  enemy_reuse_shot_begin_draw(0);CHECK(!render_mirror_enemy_reuse_shot(game_screen,enemyShot[0].sx,enemyShot[0].sy,spriteSheet8,enemyShot[0].sgr+enemyShot[0].animate,0,enemyShot[0].sgr));p09_actor[100]=old;
 }
 /* Swapping the independent static selector positions cannot authenticate. */
 p09_setup(1);p09_spawn();EnemyShotType temp=enemyShot[0];enemyShot[0]=enemyShot[1];enemyShot[1]=temp;for(unsigned s=0;s<2;s++){enemy_reuse_shot_begin_draw(s);CHECK(!render_mirror_enemy_reuse_shot(game_screen,enemyShot[s].sx,enemyShot[s].sy,spriteSheet8,enemyShot[s].sgr,s,enemyShot[s].sgr));}
 /* Excluded original records, including those sharing frame227, remain unproven. */
 for(unsigned r=2;r<7;r++){p09_setup(1);enemyAvail[0]=JE_makeEnemy(enemy,p09_records_ids[r],0);enemy[0].ex=110;enemy[0].ey=80;enemy[0].eshotwait[0]=enemy[0].eshotwait[1]=1;JE_drawEnemy(25);unsigned fired=0;for(unsigned s=0;s<ENEMY_SHOT_MAX;s++){CHECK(!enemy_reuse_identity_generation(s));fired+=!enemyShotAvail[s];}CHECK(fired>0);}
}
static void p09_interleavings(void)
{
 for(unsigned p=0;p<2;p++)for(unsigned order=0;order<2;order++){
  p09_setup(p);CHECK(render_mirror_set_global_assets(valid_root));render_mirror_begin();CHECK(global_green_frame);p09_spawn();Uint32 *want;
  if(!order){
   player_birth_and_move(110,80);native_explosions();want=canvas_copy();unsigned heads=green_head_count;p05_update();CHECK(heads==green_head_count);
   for(unsigned i=0;i<(p?3:1);i++)p09_oracle(want,i);
  }else{
   p05_update();want=canvas_copy();player_birth_and_move(110,80);native_explosions();
   for(int dy=0;dy<184*8;dy++)for(int dx=24*8;dx<288*8;dx++){
    size_t n=(size_t)dy*canvas->w+dx;Uint32 color=want[n];
    for(unsigned i=0;i<8;i++){const Uint8 *a=sample_rgba(global_green_rgba[4],dx,dy,explosions[i].x,explosions[i].y);if(a&&a[3])color=smoke_over(color,a,false);}
    for(unsigned i=0;i<8;i++){const Uint8 *a=sample_rgba(global_green_rgba[0],dx,dy,playerShotData[i].shotX+1,playerShotData[i].shotY);if(a&&a[3])color=alpha_over(color,a);}want[n]=color;
   }
  }
  CHECK(enemy_reuse_frame.contributed&&global_green_contributed&&!global_green_fault);verify_rgb(want);free(want);
  enemy_reuse_shot_retire(0);CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!last_output_valid&&!last_output_scene_hd);
 }
}
static void p09_boundaries(void)
{
 const int positions[][2]={{1,80},{275,80},{100,-13},{100,190},{0,80},{276,80},{100,-14},{100,191}};
 for(unsigned p=0;p<2;p++)for(unsigned j=0;j<8;j++){
  p09_setup(p);p09_spawn();for(unsigned i=1;i<3;i++){enemyShotAvail[i]=true;enemy_reuse_shot_retire(i);}
  enemyShot[0].sx=positions[j][0]-enemyShot[0].sxm-enemyShot[0].sxc;enemyShot[0].sy=positions[j][1]-enemyShot[0].sym-enemyShot[0].syc;
  Uint32 *want=canvas_copy();unsigned old=draws;p05_update();CHECK(enemyShot[0].sx==positions[j][0]&&enemyShot[0].sy==positions[j][1]);
  if(j<4){CHECK(!enemyShotAvail[0]&&draws==old+1);p09_oracle(want,0);
   unsigned f=enemyShot[0].sgr+enemyShot[0].animate;const Uint8 *rgba=enemy_reuse_resources.members[f==226?9:f==227?10:11].rgba;bool visible=false;
   for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++){int dx=enemyShot[0].sx*8+ax,dy=enemyShot[0].sy*8+ay;if(dx>=0&&dx<canvas->w&&dy>=0&&dy<canvas->h&&rgba[4*(ay*96+ax)+3])visible=true;}
   finish();CHECK(!reject_reason&&last_output_valid==visible&&last_output_scene_hd==visible);
   for(int y=0;y<184*8;y++)for(int x=24*8;x<288*8;x++)CHECK(*pixel(output,x-24*8,y)==want[(size_t)y*canvas->w+x]);
  }else CHECK(enemyShotAvail[0]&&draws==old&&!enemy_reuse_identity_generation(0));free(want);
 }
 for(unsigned p=0;p<2;p++)for(unsigned bad=0;bad<5;bad++){
  p09_setup(p);p09_spawn();unsigned slot=p?1:0;
  if(!p){enemy_reuse_shot_before_animation(slot);++enemyShot[slot].animate;enemy_reuse_shot_after_animation(slot);}
  enemy_reuse_shot_begin_draw(slot);unsigned f=enemyShot[slot].sgr+enemyShot[slot].animate;unsigned n=draws;
  if(bad==0)CHECK(!render_mirror_enemy_reuse_shot(game_screen,enemyShot[slot].sx,enemyShot[slot].sy,spriteSheet8,f,slot,p?226:227));
  if(bad==1)draw_player_shot_sprite2(game_screen,enemyShot[slot].sx,enemyShot[slot].sy,spriteSheet8,f,0,f);
  if(bad==2)draw_enemy_shot_sprite2(game_screen,enemyShot[slot].sx,enemyShot[slot].sy,spriteSheet8,f);
  if(bad==3)CHECK(!draw_asset_filtered(100,80,&(Asset){true,true,146,227,12,14,0,0,8,NULL},MIRROR_BLEND,NULL,0,NULL,NULL,NULL));
  if(bad==4){blit_sprite2(game_screen,20,20,spriteSheet8,20);CHECK(!render_mirror_enemy_reuse_shot(game_screen,enemyShot[slot].sx,enemyShot[slot].sy,spriteSheet8,f,slot,enemyShot[slot].sgr));}
  CHECK(draws==n&&!enemy_reuse_frame.contributed);
 }
}
static void p09_resources(void)
{
 const char *modes[]={"missing","corrupt","header","anchor","trailing","short"};
 for(unsigned k=9;k<12;k++)for(unsigned m=0;m<6;m++){
  char root[4096];snprintf(root,sizeof(root),"%s/%s%u",valid_root,modes[m],k);p09_setup(0);game_probe_assets=root;p09_spawn();unsigned n=draws;p05_update();CHECK(draws==n&&!enemy_reuse_frame.contributed&&!enemy_reuse_resources.valid[2]);
  resource_root=root;setup(105);birth(105,0,100,80);draw(105,0,100,80);CHECK(enemy_reuse_frame.contributed&&!enemy_reuse_family_ready(2));finish();CHECK(last_output_valid&&!reject_reason);
  p05_setup(false);game_probe_assets=root;p05_spawn(1);p05_update();CHECK(enemy_reuse_frame.contributed&&enemy_reuse_resources.valid[1]&&!enemy_reuse_family_ready(2));finish();CHECK(last_output_valid&&!reject_reason);
 }
 for(unsigned k=0;k<9;k++){char root[4096];snprintf(root,sizeof(root),"%s/missing%u",valid_root,k);p09_setup(0);game_probe_assets=root;p09_spawn();p05_update();CHECK(enemy_reuse_frame.contributed&&enemy_reuse_resources.valid[2]);CHECK(!enemy_reuse_family_ready(k<6?0:1));finish();CHECK(last_output_valid&&!reject_reason);}
}
static void p09_lifecycle(void)
{
 for(unsigned p=0;p<2;p++)for(unsigned bad=0;bad<10;bad++){
  p09_setup(p);p09_spawn();p05_update();CHECK(enemy_reuse_frame.contributed);Uint8 saved=bank_bytes[100];
  switch(bad){case 0:bank_bytes[100]^=1;break;case 1:enemy_reuse_bank_changed(&spriteSheet8);break;case 2:weapons[p09_weapon_ids[p]].sound++;break;case 3:enemyShot[0].animate++;break;case 4:enemy_reuse_resources.members[10].rgba[31]^=1;break;case 5:game_probe_assets="other-root";break;case 6:rgb_palette[0]^=1;break;case 7:enemy_reuse_actor_allocated(enemy,p09_records_ids[p],0);break;case 8:enemyShot[0].sgr++;break;case 9:enemy_reuse_shot_retire(0);break;}
  finish();CHECK(!ready&&!last_output_valid&&!last_output_scene_hd);bank_bytes[100]=saved;
 }
 for(unsigned p=0;p<2;p++){
  p09_setup(p);p09_spawn();p05_update();finish();CHECK(last_output_valid);render_mirror_fade_start(NULL,NULL,0,255);CHECK(!ready&&!last_output_valid&&!have_fade_saved);
  p09_setup(p);p09_spawn();p05_update();finish();CHECK(last_output_valid);((Uint8*)game_screen->pixels)[0]^=1;CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!last_output_valid);
  p09_setup(p);p09_spawn();p05_update();Uint8 *px=(Uint8*)game_screen->pixels+85*320+110;*px=0x3a;render_mirror_pixel(game_screen,px,*px,MIRROR_NORMAL);finish();CHECK(last_output_valid);for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++)CHECK(*pixel(output,(110-24)*8+x,85*8+y)==palette_rgb(0x3a));
 }
}
int main(int argc,char **argv)
{
 CHECK(argc==2);resource_root=valid_root=argv[1];
 CHECK(fread(bank_bytes,1,sizeof(bank_bytes),stdin)==sizeof(bank_bytes));CHECK(fread(records,1,sizeof(records),stdin)==sizeof(records));CHECK(fread(weap_bytes,1,sizeof(weap_bytes),stdin)==sizeof(weap_bytes));CHECK(fread(normal_palette,1,sizeof(normal_palette),stdin)==sizeof(normal_palette));CHECK(fread(actor_banks[0],1,46566,stdin)==46566);CHECK(fread(actor_banks[1],1,40714,stdin)==40714);
 CHECK(fread(p05_record,1,77,stdin)==77);CHECK(fread(p05_weapon,1,80,stdin)==80);CHECK(fread(player_green_weapons,1,160,stdin)==160);CHECK(fread(&p05_actor_size,4,1,stdin)==1&&fread(&smoke_bank_size,4,1,stdin)==1);p05_actor=malloc(p05_actor_size);smoke_bank=malloc(smoke_bank_size);CHECK(p05_actor&&smoke_bank);CHECK(fread(p05_actor,1,p05_actor_size,stdin)==p05_actor_size&&fread(smoke_bank,1,smoke_bank_size,stdin)==smoke_bank_size);
 CHECK(fread(p09_records,1,sizeof(p09_records),stdin)==sizeof(p09_records));CHECK(fread(p09_weapons,1,sizeof(p09_weapons),stdin)==sizeof(p09_weapons));CHECK(fread(p09_actor,1,sizeof(p09_actor),stdin)==sizeof(p09_actor));CHECK(fread(p09_actor6,1,sizeof(p09_actor6),stdin)==sizeof(p09_actor6));CHECK(fgetc(stdin)==EOF);
 p09_positive();p09_negatives();p09_resources();p09_lifecycle();p09_boundaries();p09_interleavings();
 p05_positives();p05_negatives();interleavings();p05_resource_failures();p05_lifecycle();crossowner_failures();p05_boundaries();
 printf("PASS native P09 + unchanged P05 matrix: %u setups, %u assertions; controlled fire scheduling, not original-event gameplay acceptance\n",cases,checks);return 0;
}
