/* Appended to the byte-exact old91 harness prefix. Controlled native evidence. */
static unsigned cases145,checks145_start;
static void draw145(int x,int y)
{
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
 uint64_t rng=mt_state_fingerprint();JE_MultiEnemyType actors;memcpy(actors,enemy,sizeof(enemy));EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(shots,enemyShot,sizeof(shots));
 blit_sprite2(classic,x,y,spriteSheet8,145);draw_enemy_shot_sprite2(game_screen,x,y,spriteSheet8,145);
 CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(rng==mt_state_fingerprint());CHECK(!memcmp(actors,enemy,sizeof(enemy)));CHECK(!memcmp(shots,enemyShot,sizeof(shots)));SDL_FreeSurface(classic);
}
static void oracle145(int x,int y)
{
 const Uint8 *rgba=projectile145_resources.member.rgba;CHECK(rgba);
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++){
  int px=x*8+ax,py=y*8+ay;if(px<0||px>=2560||py<0||py>=1600)continue;
  CHECK(*at(canvas,px,py)==alpha(palette_rgb(0x1b),rgba+4*(ay*96+ax)));
 }
}
static void positive145(void)
{
 for(unsigned i=0;i<3;i++){
  setup(i+1,12);draw145(110,80);CHECK(global_projectile91_used_members==2u&&!global_projectile91_fault);
  oracle145(110,80);finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);output_oracle();
  global_projectile91_check_cache();CHECK(ready&&last_output_valid);output_oracle();
 }
 int ys[]={-13,-6,0,180,190,199};for(unsigned i=0;i<sizeof(ys)/sizeof(*ys);i++){
  setup(1,12);CHECK(!global_projectile91_used_members);draw145(110,ys[i]);CHECK(!global_projectile91_fault);oracle145(110,ys[i]);
  if(ys[i]==-13||ys[i]==199)CHECK(!global_projectile91_used_members);finish();
 }
 int xs[]={-1,309};for(unsigned i=0;i<2;i++){setup(1,12);draw145(xs[i],80);CHECK(!global_projectile91_contributed&&!global_projectile91_used_members);finish();CHECK(!ready);}
 setup(1,12);xmas=true;draw145(110,80);CHECK(!global_projectile91_contributed);finish();CHECK(!ready);
 setup(1,12);game_probe_density=4;draw145(110,80);CHECK(!global_projectile91_contributed);finish();CHECK(!ready);
}
static void independent145(const char *missing145,const char *bad145,const char *bad91)
{
 const char *saved=valid_root;const char *roots[]={missing145,bad145};
 for(unsigned i=0;i<2;i++)for(unsigned order=0;order<2;order++){
  valid_root=roots[i];setup(1,12);if(order)draw(110,80);draw145(200,80);CHECK(!global_projectile91_fault);
  if(!order){CHECK(!global_projectile91_contributed);draw(110,80);}CHECK(global_projectile91_used_members==1u);finish();CHECK(ready);output_oracle();
 }
 const char *oldroots[]={missing_root,bad91};for(unsigned i=0;i<2;i++)for(unsigned order=0;order<2;order++){
  valid_root=oldroots[i];setup(1,12);if(order)draw145(110,80);draw(200,80);CHECK(!global_projectile91_fault);
  if(!order){CHECK(!global_projectile91_contributed);draw145(110,80);}CHECK(global_projectile91_used_members==2u);finish();CHECK(ready);output_oracle();
 }
 valid_root=saved;
 /* These colors are NOT used by the untouched other member or its0x1b underlay.
  * This is not a palette exemption: any actual sampled/cache dependency stays. */
 unsigned indices[]={49,84,85,86,87,88,89,91,93,95};for(unsigned i=0;i<10;i++)for(unsigned order=0;order<2;order++){
  setup(1,12);if(order)draw(110,80);rgb_palette[indices[i]]^=1;draw145(200,80);
  if(!order){CHECK(!global_projectile91_contributed);draw(110,80);}CHECK(global_projectile91_used_members==1u&&!global_projectile91_fault);finish();CHECK(ready);
 }
 setup(1,12);rgb_palette[1]^=1;draw(200,80);CHECK(!global_projectile91_contributed);
 draw145(110,80);CHECK(global_projectile91_used_members==2u&&!global_projectile91_fault);finish();CHECK(ready);
 setup(1,12);draw145(110,80);rgb_palette[1]^=1;draw(200,80);CHECK(global_projectile91_used_members==2u&&!global_projectile91_fault);finish();CHECK(ready);
 setup(1,12);draw(110,80);Uint8 foreign[32060];memcpy(foreign,original,sizeof(foreign));
 CHECK(!render_mirror_enemy_shot(game_screen,200,80,(Sprite2_array){32060,foreign},145));render_mirror_entity_end();
 CHECK(global_projectile91_used_members==1u&&!global_projectile91_fault);finish();CHECK(ready);
}
static void mixed145(void)
{
 for(unsigned order=0;order<2;order++){
  setup(1,12);if(order)draw145(110,80);else draw(110,80);
  Uint32 before[96*112];for(int y=0;y<112;y++)for(int x=0;x<96;x++)before[y*96+x]=*at(canvas,110*8+x,80*8+y);
  if(order)draw(110,80);else draw145(110,80);
  const Uint8 *rgba=order?projectile91_resources.member.rgba:projectile145_resources.member.rgba;
  for(int y=0;y<112;y++)for(int x=0;x<96;x++)CHECK(*at(canvas,110*8+x,80*8+y)==alpha(before[y*96+x],rgba+4*(y*96+x)));
  CHECK(global_projectile91_used_members==3u&&!global_projectile91_fault);finish();CHECK(ready);output_oracle();
  /* The first contributor remains a dependency even after opaque/soft overwrite. */
  (order?projectile145_resources.member.rgba:projectile91_resources.member.rgba)[100]^=1;
  global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
}
static void mutation145(void)
{
 for(unsigned cached=0;cached<2;cached++)for(unsigned k=0;k<8;k++){
  setup(1,12);draw145(110,80);CHECK(global_projectile91_used_members==2u);
  if(cached){finish();CHECK(ready&&last_output_valid);}
  switch(k){case 0:livebank[100]^=1;break;case 1:rgb_palette[84]^=1;break;case 2:projectile145_resources.member.rgba[100]^=1;break;case 3:xmas=true;break;case 4:game_probe_original_reference=true;break;case 5:projectile145_resources.member.anchor_x=1;break;case 6:spriteSheet8.size--;break;case 7:projectile145_resources.member.density=4;break;}
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
 setup(1,12);CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,145));render_mirror_entity_end();CHECK(global_projectile91_fault);finish();CHECK(!ready);
 setup(1,12);CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,145));CHECK(!render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,145));CHECK(global_projectile91_fault);
 setup(1,12);CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,145));Uint8 src[168],mask[168];CHECK(decode_tile(spriteSheet8,145,src,mask,12,0,0));unsigned i=0;while(!mask[i])++i;
 Uint8 *p=(Uint8*)game_screen->pixels+(80+i/12)*320+110+i%12;*p=src[i]^1;render_mirror_pixel(game_screen,p,0x1b,MIRROR_NORMAL);CHECK(global_projectile91_fault);
 setup(1,12);CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,145));CHECK(decode_tile(spriteSheet8,145,src,mask,12,0,0));i=0;while(!mask[i])++i;
 p=(Uint8*)game_screen->pixels+(80+i/12)*320+110+i%12;*p=src[i];render_mirror_pixel(game_screen,p,0x1b,MIRROR_NORMAL);render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);CHECK(global_projectile91_fault);
 setup(1,12);draw145(110,80);finish();CHECK(ready);rgb_palette[200]^=1;global_projectile91_check_cache();CHECK(!ready); /* cached768 guard */
 setup(1,12);draw145(110,80);finish();CHECK(ready);render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);
 draw(110,80);CHECK(global_projectile91_used_members==1u);render_mirror_global_reset();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);
}
static void transfer145(void)
{
 for(unsigned cached=0;cached<2;cached++){
  setup(1,12);draw145(110,80);CHECK(global_projectile91_used_members==2u);
  Uint8 prior[96*112];for(int y=0;y<112;y++)for(int x=0;x<96;x++)prior[y*96+x]=global_projectile91_owner[(80*8+y)*2560+110*8+x]&&projectile145_resources.member.rgba[4*(y*96+x)+3]>0;
  talon_tile();unsigned copied=0;
  for(int y=0;y<112;y++)for(int x=0;x<96;x++){
   size_t n=(80*8+y)*2560+110*8+x;
   if(prior[y*96+x]&&!global_projectile91_owner[n]&&global_talon_owner[n]&&global_talon_foreign[n])copied++;
  }
  CHECK(copied>0);CHECK(global_projectile91_contributed&&global_projectile91_used_members==2u);
  printf("145_TO_TALON copied=%u cached=%u\n",copied,cached);
  if(cached){finish();CHECK(ready&&last_output_valid);}
  projectile145_resources.member.rgba[100]^=1;
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
int main(int argc,char **argv)
{
 CHECK(argc==6);valid_root=argv[1];missing_root=argv[2];read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));Uint32 n;read_exact(&n,4);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);CHECK(fgetc(stdin)==EOF);
 /* These eight old functions and every assertion are retained byte-for-byte. */
 positives();mutations();witnesses();foreign_writes();independent_absence();cross_owner();fades();retained();
 printf("PASS inherited91 native lifecycle: %u cases %u assertions\n",cases,checks);
 cases145=cases;checks145_start=checks;
 positive145();independent145(argv[3],argv[4],argv[5]);mixed145();mutation145();transfer145();
 printf("PASS shared145 native lifecycle: %u new cases %u new assertions; internal8 only; not gameplay/full build\n",cases-cases145,checks-checks145_start);
 return 0;
}
