/* P05 adds exact native spawn/update and green-owner interleaving proof.
 * The prior310 static suite is kept intact and run separately. */
#define main prior_enemy_reuse_main
#include "enemy_reuse_validation.c"
#undef main
#include "native_enemy_green_loops.inc"
static Uint8 p05_record[77],p05_weapon[80],player_green_weapons[2][80];
static Uint8 *p05_actor,*smoke_bank;static Uint32 p05_actor_size,smoke_bank_size;
static const char *valid_root;
static void p05_setup(bool global)
{
 render_mirror_set_global_assets(NULL);resource_root=valid_root;setup(105);
 current_record=379;record_load(p05_record);weapon_load(153,p05_weapon);weapon_load(71,player_green_weapons[0]);weapon_load(1071,player_green_weapons[1]);
 episodeNum=2;lvlFileNum=2;enemySpriteSheetIds[0]=18;enemySpriteSheets[0]=(Sprite2_array){p05_actor_size,p05_actor};explosionSpriteSheet=(Sprite2_array){smoke_bank_size,smoke_bank};
 memset(playerShotData,0,sizeof(playerShotData));memset(shotAvail,0,sizeof(shotAvail));memset(shotMultiPos,0,sizeof(shotMultiPos));memset(explosions,0,sizeof(explosions));
 memset(player,0,sizeof(player));player[0].x=150;player[0].y=160;player[0].is_alive=false;tempMapXOfs=0;tempBackMove=0;explodeMove=0;explosionTransparent=false;background2=false;
 difficultyLevel=DIFFICULTY_NORMAL;mt_srand(153);
 if(global){CHECK(render_mirror_set_global_assets(valid_root));render_mirror_begin();CHECK(global_green_frame);}
}
static void p05_spawn(unsigned bursts)
{
 CHECK(weapons[153].max==8&&weapons[153].multi==2&&weapons[153].weapani==3);
 for(unsigned i=0;i<8;i++)CHECK(weapons[153].sg[i]==214);
 enemyAvail[0]=JE_makeEnemy(enemy,379,0);CHECK(enemyAvail[0]==0);enemy[0].ex=110;enemy[0].ey=80;
 for(unsigned burst=0;burst<bursts;burst++){
  enemy[0].eshotwait[0]=1;JE_drawEnemy(25);CHECK(enemy[0].eshotmultipos[0]==2*(burst+1));
  for(unsigned i=burst*2;i<burst*2+2;i++){CHECK(!enemyShotAvail[i]);CHECK(enemyShot[i].sgr==214&&enemyShot[i].animate==0&&enemyShot[i].animax==3);CHECK(enemy_reuse_identity_generation(i));}
 }
}
static Uint32 alpha_over(Uint32 bg,const Uint8 *p)
{
 unsigned a=p[3],r=(((bg>>16)&255)*(255-a)+p[0]*a+127)/255,g=(((bg>>8)&255)*(255-a)+p[1]*a+127)/255,b=((bg&255)*(255-a)+p[2]*a+127)/255;
 return 0xff000000u|(r<<16)|(g<<8)|b;
}
static Uint32 *canvas_copy(void)
{size_t n=(size_t)canvas->w*canvas->h;Uint32 *copy=malloc(n*4);CHECK(copy);for(int y=0;y<canvas->h;y++)memcpy(copy+(size_t)y*canvas->w,(Uint8*)canvas->pixels+y*canvas->pitch,canvas->w*4);return copy;}
static void apply_enemy_oracle(Uint32 *expected_rgb,unsigned slot)
{
 EnemyShotType *s=&enemyShot[slot];if(enemyShotAvail[slot])return;unsigned index=s->sgr+s->animate;CHECK(index>=214&&index<=216);
 const Uint8 *rgba=enemy_reuse_resources.members[6+index-214].rgba;CHECK(rgba);
 for(int y=0;y<112;y++)for(int x=0;x<96;x++){int dx=s->sx*8+x,dy=s->sy*8+y;if(dx<0||dx>=canvas->w||dy<0||dy>=canvas->h)continue;size_t n=(size_t)dy*canvas->w+dx;expected_rgb[n]=alpha_over(expected_rgb[n],rgba+4*(y*96+x));}
}
static void p05_update(void)
{
 EnemyShotType before[ENEMY_SHOT_MAX],after[ENEMY_SHOT_MAX];Uint8 avail_before[ENEMY_SHOT_MAX],avail_after[ENEMY_SHOT_MAX];memcpy(before,enemyShot,sizeof(before));memcpy(avail_before,enemyShotAvail,sizeof(avail_before));
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
 uint64_t rng=mt_state_fingerprint();VGAScreen=classic;native_enemy_shots_classic();memcpy(after,enemyShot,sizeof(after));memcpy(avail_after,enemyShotAvail,sizeof(avail_after));CHECK(mt_state_fingerprint()==rng);
 memcpy(enemyShot,before,sizeof(before));memcpy(enemyShotAvail,avail_before,sizeof(avail_before));VGAScreen=game_screen;native_enemy_shots();
 CHECK(!memcmp(after,enemyShot,sizeof(after))&&!memcmp(avail_after,enemyShotAvail,sizeof(avail_after)));CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(mt_state_fingerprint()==rng);SDL_FreeSurface(classic);
}
static void verify_rgb(Uint32 *want)
{
 final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!reject_reason&&last_output_valid&&last_output_scene_hd);
 for(int y=0;y<184*8;y++)for(int x=24*8;x<288*8;x++)CHECK(*pixel(output,x-24*8,y)==want[(size_t)y*canvas->w+x]);
}
static void p05_positives(void)
{
 for(unsigned bursts=1;bursts<=4;bursts++){
  p05_setup(false);p05_spawn(bursts);
  for(unsigned tick=0;tick<6;tick++){
   if(tick){SDL_FillRect(game_screen,NULL,0x1b);render_mirror_begin();}
   Uint32 *want=canvas_copy();unsigned count=green_head_count;unsigned before_draws=draws;p05_update();CHECK(draws-before_draws==bursts*2);CHECK(green_head_count==count&&!global_green_contributed);
   for(unsigned i=0;i<bursts*2;i++){CHECK(enemyShot[i].animate==(tick+1)%3);apply_enemy_oracle(want,i);}verify_rgb(want);free(want);
  }
 }
}
static void p05_negatives(void)
{
 for(unsigned mode=0;mode<8;mode++){
  p05_setup(false);p05_spawn(1);unsigned old=draws;
  switch(mode){case 0:enemyShot[0].animate=1;break;case 1:enemyShot[0].animax=2;break;case 2:weapons[153].weapani=2;break;case 3:episodeNum=1;break;case 4:enemy_reuse_shot_retire(0);break;case 5:p05_actor[100]^=1;break;case 6:enemy_reuse_bank_changed(&enemySpriteSheets[0]);break;case 7:enemyShot[0].sgr=215;break;}
  enemy_reuse_shot_begin_draw(0);CHECK(!render_mirror_enemy_reuse_shot(game_screen,enemyShot[0].sx,enemyShot[0].sy,spriteSheet8,214+enemyShot[0].animate,0,enemyShot[0].sgr));CHECK(draws==old);
  if(mode==5)p05_actor[100]^=1;
 }
 p05_setup(false);p05_spawn(1);enemy_reuse_shot_before_animation(0);enemyShot[0].animate=2;enemy_reuse_shot_after_animation(0);enemy_reuse_shot_begin_draw(0);CHECK(!render_mirror_enemy_reuse_shot(game_screen,enemyShot[0].sx,enemyShot[0].sy,spriteSheet8,216,0,214));
}

static void player_birth_and_move(int x,int y)
{
 weaponPort[0].poweruse=0;power=900;int last=player_shot_create(0,0,x,y,x,y,71,1);CHECK(last==7);
 for(unsigned i=0;i<8;i++)CHECK(global_green_shots[i].role&&shotAvail[i]==8);
 for(unsigned i=0;i<8;i++){
  bool special;int sx,sy;JE_integer damage;JE_byte filter,chain,pnum;JE_word rw,rh;
  CHECK(player_shot_move_and_draw(i,&special,&sx,&sy,&damage,&filter,&chain,&pnum,&rw,&rh));CHECK(!special&&shotAvail[i]==7);
  CHECK(global_green_shots[i].role&&global_green_shots[i].ttl==7);CHECK(global_green_slots[i].role&&explosions[i].ttl==7);
 }
 if(green_head_count!=8||!global_green_contributed||global_green_fault)fprintf(stderr,"green diagnostic heads=%u contributed=%d fault=%d identity=%d frame=%d source=%d palette=%d loaded=%d good=%d expbytes=%u\n",green_head_count,global_green_contributed,global_green_fault,global_green_identity_fault,global_green_frame,global_green_source_matches(spriteSheet8),global_green_palette_matches(),global_green_loaded,global_green_good,smoke_bank_size);CHECK(green_head_count==8&&global_green_contributed&&!global_green_fault);
}
static const Uint8 *sample_rgba(const Uint8 *rgba,int dx,int dy,int x,int y)
{int ax=dx-x*8,ay=dy-y*8;return ax>=0&&ax<96&&ay>=0&&ay<112?rgba+4*(ay*96+ax):NULL;}
static Uint32 smoke_over(Uint32 bg,const Uint8 *p,bool blend)
{
 if(!blend)return alpha_over(bg,p);Uint8 mapped[4];unsigned peak=p[0]>p[1]?p[0]:p[1];if(p[2]>peak)peak=p[2];unsigned dp=(bg>>16)&255;if(((bg>>8)&255)>dp)dp=(bg>>8)&255;if((bg&255)>dp)dp=bg&255;unsigned next=(peak+dp+1)/2;
 for(unsigned c=0;c<3;c++)mapped[c]=peak?(p[c]*next+peak/2)/peak:0;mapped[3]=p[3];return alpha_over(bg,mapped);
}
static void interleavings(void)
{
 unsigned fractional=0,outmask=0,blend_samples=0;
 for(unsigned phase=0;phase<3;phase++)for(unsigned order=0;order<2;order++)for(unsigned blend=0;blend<2;blend++){
  p05_setup(true);p05_spawn(1);
  for(unsigned t=0;t<phase;t++){p05_update();finish();SDL_FillRect(game_screen,NULL,0x1b);render_mirror_begin();}
  Uint32 *want=NULL;Uint8 *enemy_support=NULL;
  if(order==0){
   player_birth_and_move(110,80);explosionTransparent=blend;native_explosions();CHECK(!global_green_fault);
   unsigned heads=green_head_count;unsigned char slots[sizeof(global_green_slots)],shots[sizeof(global_green_shots)];memcpy(slots,global_green_slots,sizeof(slots));memcpy(shots,global_green_shots,sizeof(shots));
   want=canvas_copy();p05_update();CHECK(green_head_count==heads);CHECK(!memcmp(slots,global_green_slots,sizeof(slots))&&!memcmp(shots,global_green_shots,sizeof(shots)));
   apply_enemy_oracle(want,0);apply_enemy_oracle(want,1);verify_rgb(want);
  }else{
   p05_update();CHECK(!green_head_count&&!global_green_contributed);want=canvas_copy();enemy_support=calloc((size_t)canvas->w*canvas->h,1);CHECK(enemy_support);
   for(unsigned slot=0;slot<2;slot++){EnemyShotType *e=&enemyShot[slot];const Uint8 *rgba=enemy_reuse_resources.members[6+e->animate].rgba;Uint8 decoded[336];CHECK(decode_tile(spriteSheet8,214+e->animate,decoded,decoded+168,12,0,0));
    for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++){const Uint8 *a=rgba+4*(ay*96+ax);int dx=e->sx*8+ax,dy=e->sy*8+ay;if(dx<0||dx>=canvas->w||dy<0||dy>=canvas->h)continue;if(a[3])enemy_support[(size_t)dy*canvas->w+dx]=1;if(a[3]&&a[3]<255)fractional++;if(a[3]&&!decoded[168+(ay/8)*12+ax/8])outmask++;}
   }
   player_birth_and_move(110,80);explosionTransparent=blend;native_explosions();CHECK(!global_green_fault);
   /* Independent normal smoke-under-head algebra. Blend samples are limited
    * to authentic enemy-owned RGB, where classic brightness interpolation
    * is explicitly inapplicable; no renderer ownership array is the oracle. */
   for(int dy=0;dy<184*8;dy++)for(int dx=24*8;dx<288*8;dx++){
    size_t n=(size_t)dy*canvas->w+dx;if(blend&&!enemy_support[n])continue;Uint32 color=want[n];
    for(unsigned i=0;i<8;i++){const Uint8 *a=sample_rgba(global_green_rgba[4],dx,dy,explosions[i].x,explosions[i].y);if(a&&a[3]){color=smoke_over(color,a,blend);if(blend)blend_samples++;}}
    for(unsigned i=0;i<8;i++){const Uint8 *a=sample_rgba(global_green_rgba[0],dx,dy,playerShotData[i].shotX+1,playerShotData[i].shotY);if(a&&a[3])color=alpha_over(color,a);}
    want[n]=color;
   }
   final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!reject_reason&&last_output_valid&&!global_green_fault);
   for(int dy=0;dy<184*8;dy++)for(int dx=24*8;dx<288*8;dx++){size_t n=(size_t)dy*canvas->w+dx;if(!blend||enemy_support[n])CHECK(*pixel(output,dx-24*8,dy)==want[n]);}
  }
  free(want);free(enemy_support);
 }
 CHECK(fractional>0&&outmask>0&&blend_samples>0);
}

static void p05_resource_failures(void)
{
 const char *modes[]={"missing","corrupt","header","anchor","trailing","short"};
 for(unsigned k=6;k<9;k++)for(unsigned m=0;m<6;m++){
  char root[4096];snprintf(root,sizeof(root),"%s/%s%u",valid_root,modes[m],k);
  p05_setup(false);game_probe_assets=root;p05_spawn(1);unsigned n=draws;p05_update();CHECK(draws==n&&!enemy_reuse_frame.contributed&&!enemy_reuse_resources.valid[1]);
  /* Old dependency remains valid despite failed green preflight. */
  resource_root=root;setup(105);birth(105,0,100,80);draw(105,0,100,80);CHECK(enemy_reuse_frame.contributed);CHECK(!enemy_reuse_family_ready(1));CHECK(!reject_reason);finish();CHECK(last_output_valid&&!reject_reason);
 }
 for(unsigned k=0;k<6;k++){
  char root[4096];snprintf(root,sizeof(root),"%s/missing%u",valid_root,k);p05_setup(false);game_probe_assets=root;p05_spawn(1);p05_update();CHECK(enemy_reuse_frame.contributed&&enemy_reuse_resources.valid[1]);CHECK(!enemy_reuse_family_ready(0));finish();CHECK(last_output_valid&&!reject_reason);
 }
}
static void p05_lifecycle(void)
{
 for(unsigned bad=0;bad<7;bad++){
  p05_setup(false);p05_spawn(1);p05_update();CHECK(enemy_reuse_frame.contributed);Uint8 b=bank_bytes[100];
  switch(bad){case 0:bank_bytes[100]^=1;break;case 1:enemy_reuse_bank_changed(&spriteSheet8);break;case 2:weapons[153].weapani++;break;case 3:enemyShot[0].animate=0;break;case 4:enemy_reuse_resources.members[7].rgba[31]^=1;break;case 5:game_probe_assets="other-root";break;case 6:rgb_palette[0]^=1;break;}
  finish();CHECK(!ready&&!last_output_valid&&!last_output_scene_hd);bank_bytes[100]=b;
 }
 p05_setup(false);p05_spawn(1);p05_update();finish();CHECK(last_output_valid);render_mirror_fade_start(NULL,NULL,0,255);CHECK(!ready&&!last_output_valid&&!have_fade_saved&&!last_output_scene_hd);
 p05_setup(false);p05_spawn(1);p05_update();finish();CHECK(last_output_valid);((Uint8*)game_screen->pixels)[0]^=1;CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!last_output_valid);
 p05_setup(false);p05_spawn(1);p05_update();Uint8 *px=(Uint8*)game_screen->pixels+85*320+110;*px=0x3a;render_mirror_pixel(game_screen,px,*px,MIRROR_NORMAL);finish();CHECK(last_output_valid);for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++)CHECK(*pixel(output,(110-24)*8+x,85*8+y)==palette_rgb(0x3a));
 /* Complete native transition cannot be borrowed across an unrelated pixel
  * write or a failed/direct renderer invocation. */
 for(unsigned bad=0;bad<3;bad++){
  p05_setup(false);p05_spawn(1);enemy_reuse_shot_before_animation(0);++enemyShot[0].animate;enemy_reuse_shot_after_animation(0);
  if(bad==0)blit_sprite2(game_screen,20,20,spriteSheet8,20);
  else CHECK(!render_mirror_enemy_reuse_shot(game_screen,enemyShot[0].sx,enemyShot[0].sy,spriteSheet8,bad==1?215:999,0,214));
  enemy_reuse_shot_begin_draw(0);CHECK(!render_mirror_enemy_reuse_shot(game_screen,enemyShot[0].sx,enemyShot[0].sy,spriteSheet8,215,0,214));
 }
}

static void crossowner_failures(void)
{
 for(unsigned order=0;order<2;order++)for(unsigned fault=0;fault<3;fault++){
  p05_setup(true);p05_spawn(1);
  if(order==0){player_birth_and_move(110,80);native_explosions();p05_update();}
  else {p05_update();player_birth_and_move(110,80);native_explosions();}
  CHECK(enemy_reuse_frame.contributed&&global_green_contributed);
  if(fault==0){weapons[71].sound++;finish();CHECK(!ready&&!last_output_valid&&!last_output_scene_hd);}
  else if(fault==1){finish();CHECK(last_output_valid);enemy_reuse_shot_retire(0);CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!last_output_valid&&!last_output_scene_hd);}
  else{finish();CHECK(last_output_valid);render_mirror_fade_start(NULL,NULL,0,255);CHECK(!ready&&!last_output_valid&&!last_output_scene_hd&&!have_fade_saved);}
 }
}
static void p05_boundaries(void)
{
 const int positions[][2]={{1,80},{275,80},{100,-13},{100,190},{0,80},{276,80},{100,-14},{100,191}};
 for(unsigned j=0;j<8;j++){
  p05_setup(false);p05_spawn(1);enemyShotAvail[1]=true;enemy_reuse_shot_retire(1);
  enemyShot[0].sx=positions[j][0]-enemyShot[0].sxm-enemyShot[0].sxc;enemyShot[0].sy=positions[j][1]-enemyShot[0].sym-enemyShot[0].syc;
  Uint32 *want=canvas_copy();unsigned old=draws;p05_update();CHECK(enemyShot[0].sx==positions[j][0]&&enemyShot[0].sy==positions[j][1]);
  if(j<4){CHECK(!enemyShotAvail[0]&&draws==old+1);apply_enemy_oracle(want,0);verify_rgb(want);}else CHECK(enemyShotAvail[0]&&draws==old&&!enemy_reuse_identity_generation(0));free(want);
 }
 unsigned kinds[]={MIRROR_OUTPUT_NORMAL15_NIGHT,MIRROR_OUTPUT_NORMAL15_LOW_DETAIL,MIRROR_OUTPUT_UNSUPPORTED};
 for(unsigned j=0;j<3;j++){p05_setup(false);p05_spawn(1);p05_update();CHECK(enemy_reuse_frame.contributed);final_copy();render_mirror_finish(kinds[j],0,0);CHECK(!last_output_valid&&!last_output_scene_hd);}
 /* Pausing does not advance animation; declined rendering does not stop the
  * next legitimate production update from advancing the tracked phase. */
 p05_setup(false);p05_spawn(1);p05_update();finish();unsigned phase=enemyShot[0].animate;render_mirror_begin();CHECK(enemyShot[0].animate==phase);p05_update();CHECK(enemyShot[0].animate==2&&enemy_reuse_frame.contributed);finish();
 p05_setup(false);p05_spawn(1);game_probe_missing=true;p05_update();CHECK(enemyShot[0].animate==1&&!enemy_reuse_frame.contributed);game_probe_missing=false;render_mirror_begin();p05_update();CHECK(enemyShot[0].animate==2&&enemy_reuse_frame.contributed);finish();
 for(unsigned fault=0;fault<5;fault++){
  p05_setup(false);p05_spawn(1);uint64_t old=enemy_reuse_identity_generation(0);CHECK(old);
  enemy_reuse_shot_before_animation(0);++enemyShot[0].animate;enemy_reuse_shot_after_animation(0);
  if(fault==0){enemyAvail[0]=1;enemyAvail[0]=JE_makeEnemy(enemy,379,0);CHECK(!enemy_reuse_identity_generation(0));}
  if(fault==1){enemy_reuse_shot_spawn(0,0,153,1,0);CHECK(!enemy_reuse_identity_generation(0));}
  if(fault==2)enemyShot[0].sgr=217;
  if(fault==3)enemy_reuse_shot_spawn(0,0,110,1,0);
  if(fault==4){enemyDat[380]=enemyDat[379];enemyAvail[0]=1;enemyAvail[0]=JE_makeEnemy(enemy,380,0);}
  enemy_reuse_shot_begin_draw(0);CHECK(!render_mirror_enemy_reuse_shot(game_screen,enemyShot[0].sx,enemyShot[0].sy,spriteSheet8,215,0,214));
 }
 p05_setup(false);p05_spawn(1);uint64_t old=enemy_reuse_identity_generation(0);enemyShotAvail[0]=enemyShotAvail[1]=true;enemy_reuse_shot_retire(0);enemy_reuse_shot_retire(1);enemy[0].eshotwait[0]=1;JE_drawEnemy(25);CHECK(enemy_reuse_identity_generation(0)&&enemy_reuse_identity_generation(0)!=old);p05_update();CHECK(enemy_reuse_frame.contributed);
}

int main(int argc,char **argv)
{
 CHECK(argc==2);resource_root=valid_root=argv[1];CHECK(fread(bank_bytes,1,sizeof(bank_bytes),stdin)==sizeof(bank_bytes));CHECK(fread(records,1,sizeof(records),stdin)==sizeof(records));CHECK(fread(weap_bytes,1,sizeof(weap_bytes),stdin)==sizeof(weap_bytes));CHECK(fread(normal_palette,1,sizeof(normal_palette),stdin)==sizeof(normal_palette));CHECK(fread(actor_banks[0],1,46566,stdin)==46566);CHECK(fread(actor_banks[1],1,40714,stdin)==40714);
 CHECK(fread(p05_record,1,77,stdin)==77);CHECK(fread(p05_weapon,1,80,stdin)==80);CHECK(fread(player_green_weapons,1,160,stdin)==160);CHECK(fread(&p05_actor_size,4,1,stdin)==1&&fread(&smoke_bank_size,4,1,stdin)==1);p05_actor=malloc(p05_actor_size);smoke_bank=malloc(smoke_bank_size);CHECK(p05_actor&&smoke_bank);CHECK(fread(p05_actor,1,p05_actor_size,stdin)==p05_actor_size&&fread(smoke_bank,1,smoke_bank_size,stdin)==smoke_bank_size);CHECK(fgetc(stdin)==EOF);
 const char *mutant=getenv("ENEMY_GREEN_NEGATIVE_CONTROL");if(mutant&&!strcmp(mutant,"animation-witness")){p05_lifecycle();return 0;}if(mutant&&!strcmp(mutant,"family-isolation")){p05_resource_failures();return 0;}
 p05_positives();p05_negatives();interleavings();p05_resource_failures();p05_lifecycle();crossowner_failures();p05_boundaries();printf("PASS native P05: %u setups, %u assertions; controlled fire scheduling and exact native update extraction, not gameplay acceptance\n",cases,checks);return 0;
}
