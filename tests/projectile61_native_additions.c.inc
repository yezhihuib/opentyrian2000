/* SPDX-License-Identifier: GPL-2.0-or-later
 * External controlled production-TU companion. The included inherited107
 * source, its entry point, stdin and stdout remain byte-exact and run in a
 * separate process. These cases exercise internal density8 only; they are not
 * natural gameplay, a fresh full game build, or a qualification gate.
 */
static void draw61_bank(int x,int y,Sprite2_array bank)
{
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
 uint64_t rng=mt_state_fingerprint();Uint32 saved_palette[256];
 memcpy(saved_palette,rgb_palette,sizeof(saved_palette));JE_MultiEnemyType actors;
 memcpy(actors,enemy,sizeof(enemy));EnemyShotType shots[ENEMY_SHOT_MAX];
 memcpy(shots,enemyShot,sizeof(shots));
 blit_sprite2(classic,x,y,bank,61);
 draw_enemy_shot_sprite2(game_screen,x,y,bank,61);
 CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));
 CHECK(rng==mt_state_fingerprint());CHECK(!memcmp(saved_palette,rgb_palette,sizeof(saved_palette)));CHECK(!memcmp(actors,enemy,sizeof(enemy)));
 CHECK(!memcmp(shots,enemyShot,sizeof(shots)));SDL_FreeSurface(classic);
}
static void draw61(int x,int y){draw61_bank(x,y,spriteSheet8);}
static void member61_draw(unsigned index,int x,int y)
{
 CHECK(index==91||index==145||index==61);
 if(index==91)draw(x,y);else if(index==145)draw145(x,y);else draw61(x,y);
}
static Uint8 *member61_rgba(unsigned index)
{
 CHECK(index==91||index==145||index==61);
 return index==91?projectile91_resources.member.rgba:
        index==145?projectile145_resources.member.rgba:projectile61_resources.member.rgba;
}
static unsigned member61_bit(unsigned index)
{return index==91?1u:index==145?2u:index==61?4u:0u;}
static void mask61(Uint8 *source,Uint8 *mask)
{
 CHECK(decode_tile(spriteSheet8,61,source,mask,12,0,0));
 unsigned occupied=0,left=0,right=0;
 for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++) {
  unsigned i=y*12+x;
  if(mask[i]){++occupied;if(x<4)++left;if(x>=8)++right;}
  if(x>=4&&x<8)CHECK(!mask[i]);
 }
 CHECK(occupied==74&&left==37&&right==37);
}
/* Complete image oracle, including alpha-zero occupied cells and the native
 * transparent gap. Inputs are captured native underlay, not renderer output. */
static void oracle61(int x,int y,const Uint8 *under,bool final_output)
{
 const Uint8 *rgba=projectile61_resources.member.rgba;CHECK(rgba);
 Uint8 source[168],mask[168];mask61(source,mask);
 unsigned soft=0,opaque=0,clear=0;
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  unsigned i=(unsigned)(ay*96+ax),cell=(unsigned)((ay/8)*12+ax/8);
  const Uint8 *a=rgba+4*i;
  if(!a[3])++clear;else if(a[3]==255)++opaque;else ++soft;
  if(!mask[cell])CHECK(!a[0]&&!a[1]&&!a[2]&&!a[3]);
  if(ax>=32&&ax<64)CHECK(!a[0]&&!a[1]&&!a[2]&&!a[3]);
  int px=x*8+ax,py=y*8+ay;
  if(px<0||px>=2560||py<0||py>=1600)continue;
  Uint32 want=alpha(palette_rgb(under[cell]),a);
  if(final_output) {
   if(px<24*8||px>=288*8||py>=184*8)continue;
   CHECK(*at(output,px-24*8,py)==want);
  }else CHECK(*at(canvas,px,py)==want);
  if(ax>=32&&ax<64) {
   CHECK(((Uint8 *)game_screen->pixels)[(y+ay/8)*320+x+ax/8]==under[cell]);
   CHECK(!global_projectile91_owner[(size_t)py*2560+px]);
  }
 }
 CHECK(soft==3499&&opaque==246&&clear==7007);
}
static void positive61(void)
{
 for(unsigned pattern=0;pattern<2;pattern++) {
  setup(2,9);Uint8 under[168];
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++) {
   unsigned i=y*12+x;under[i]=(Uint8)(0x1b+(pattern?16*((x+y)%3):0));
   ((Uint8 *)game_screen->pixels)[(80+y)*320+110+x]=under[i];
  }
  /* This is an explicit controlled framebuffer fixture before frame binding. */
  render_mirror_begin();CHECK(global_projectile91_frame);
  draw61(110,80);CHECK(global_projectile91_contributed&&global_projectile91_used_members==4u);
  CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
  oracle61(110,80,under,false);finish();
  CHECK(ready&&last_output_valid&&global_projectile91_cached);
  oracle61(110,80,under,true);output_oracle();
  global_projectile91_check_cache();CHECK(ready&&last_output_valid);
  oracle61(110,80,under,true);
 }
}
/* Pair and triple oracles are independent straight-alpha composition on the
 * prior canvas. Every selected member really overlaps an earlier member at
 * nonzero authored pixels; used-bit presence alone is not the witness. */
static unsigned mixed61_step(unsigned index,unsigned previous)
{
 Uint32 before[96*112];Uint8 owned[96*112];
 for(int y=0;y<112;y++)for(int x=0;x<96;x++) {
  unsigned i=(unsigned)(y*96+x);size_t n=(size_t)(80*8+y)*2560+110*8+x;
  before[i]=*at(canvas,110*8+x,80*8+y);owned[i]=global_projectile91_owner[n];
 }
 member61_draw(index,110,80);const Uint8 *rgba=member61_rgba(index);CHECK(rgba);
 unsigned overlap=0;
 for(int y=0;y<112;y++)for(int x=0;x<96;x++) {
  unsigned i=(unsigned)(y*96+x);CHECK(*at(canvas,110*8+x,80*8+y)==alpha(before[i],rgba+4*i));
  if(owned[i]&&rgba[4*i+3]&&member61_rgba(previous)[4*i+3])++overlap;
 }
 CHECK(overlap>0);CHECK(!global_projectile91_fault);return overlap;
}
static void mixed61(void)
{
 const unsigned old[]={91,145};
 for(unsigned o=0;o<2;o++)for(unsigned reverse=0;reverse<2;reverse++)for(unsigned cached=0;cached<2;cached++) {
  setup(2,9);unsigned first=reverse?61:old[o],second=reverse?old[o]:61;
  member61_draw(first,110,80);CHECK(global_projectile91_used_members==member61_bit(first));
  CHECK(mixed61_step(second,first)>0);
  CHECK(global_projectile91_used_members==(member61_bit(first)|member61_bit(second)));
  if(cached){finish();CHECK(ready&&last_output_valid);output_oracle();}
  /* Invalidate the EARLIER actual contributor, not just the final draw. */
  member61_rgba(first)[100]^=1;
  if(cached)global_projectile91_check_cache();else finish();
  CHECK(!ready&&!last_output_valid);
 }
 const unsigned orders[3][3]={{61,91,145},{91,145,61},{145,61,91}};
 for(unsigned order=0;order<3;order++)for(unsigned cached=0;cached<2;cached++) {
  setup(2,9);member61_draw(orders[order][0],110,80);
  CHECK(mixed61_step(orders[order][1],orders[order][0])>0);
  CHECK(mixed61_step(orders[order][2],orders[order][1])>0);
  unsigned common=0;
  for(unsigned i=0;i<96*112;i++)if(member61_rgba(61)[4*i+3]&&member61_rgba(91)[4*i+3]&&member61_rgba(145)[4*i+3]) {
   size_t n=(size_t)(80*8+i/96)*2560+110*8+i%96;
   CHECK(global_projectile91_owner[n]);++common;
  }
  CHECK(common>0&&global_projectile91_used_members==7u&&!global_projectile91_fault);
  if(cached){finish();CHECK(ready&&last_output_valid);output_oracle();}
  member61_rgba(orders[order][0])[100]^=1;
  if(cached)global_projectile91_check_cache();else finish();
  CHECK(!ready&&!last_output_valid);
 }
}
static void absence61(const char *missing145,const char *bad145,const char *bad91,
                      const char *missing61,const char *bad61,const char *only61)
{
 const char *saved=valid_root;const char *newroots[]={missing61,bad61};
 for(unsigned root=0;root<2;root++)for(unsigned warm=0;warm<2;warm++) {
  valid_root=newroots[root];setup(2,9);
  if(warm){draw(40,80);draw145(80,80);CHECK(global_projectile91_used_members==3u);}
  draw61(200,80);CHECK(!global_projectile91_fault);
  if(!warm){CHECK(!global_projectile91_contributed&&!global_projectile91_used_members);draw(40,80);draw145(80,80);}
  CHECK(global_projectile91_used_members==3u&&!projectile61_resources.valid);
  finish();CHECK(ready&&last_output_valid);output_oracle();
 }
 const char *oldroots[]={missing_root,bad91,missing145,bad145};
 for(unsigned root=0;root<4;root++)for(unsigned warm=0;warm<2;warm++) {
  valid_root=oldroots[root];setup(2,9);
  if(warm){draw61(110,80);CHECK(global_projectile91_used_members==4u);}
  member61_draw(root<2?91:145,200,80);CHECK(!global_projectile91_fault);
  if(!warm){CHECK(!global_projectile91_contributed&&!global_projectile91_used_members);draw61(110,80);}
  CHECK(global_projectile91_used_members==4u);finish();CHECK(ready&&last_output_valid);output_oracle();
 }
 for(unsigned warm=0;warm<2;warm++) {
  valid_root=only61;setup(2,9);if(warm)draw61(110,80);
  draw(40,80);draw145(200,80);CHECK(!global_projectile91_fault);
  CHECK(!projectile91_resources.valid&&!projectile145_resources.valid);
  if(!warm){CHECK(!global_projectile91_used_members);draw61(110,80);}
  CHECK(global_projectile91_used_members==4u);finish();CHECK(ready&&last_output_valid);output_oracle();
 }
 valid_root=saved;
}
static void palette61(void)
{
 /* The declined61 native call is disjoint from the two admitted old members.
  * Its source colors are therefore not sampled by their native underlay. */
 for(unsigned color=113;color<=124;color++)for(unsigned warm=0;warm<2;warm++) {
  setup(2,9);if(warm){draw(40,80);draw145(80,80);}
  CHECK(!global_projectile91_used_colors[color]);rgb_palette[color]^=1;
  draw61(200,80);CHECK(!global_projectile91_fault);
  if(!warm){CHECK(!global_projectile91_used_members);draw(40,80);draw145(80,80);}
  CHECK(global_projectile91_used_members==3u);finish();CHECK(ready&&last_output_valid);
 }
 const unsigned oldcolors[]={1,84};
 for(unsigned old=0;old<2;old++)for(unsigned warm=0;warm<2;warm++) {
  setup(2,9);if(warm)draw61(110,80);
  CHECK(!global_projectile91_used_colors[oldcolors[old]]);rgb_palette[oldcolors[old]]^=1;
  member61_draw(old?145:91,200,80);CHECK(!global_projectile91_fault);
  if(!warm){CHECK(!global_projectile91_used_members);draw61(110,80);}
  CHECK(global_projectile91_used_members==4u);finish();CHECK(ready&&last_output_valid);
 }
 /* All12 used61 palette entries are dependencies at both finish and cache. */
 for(unsigned color=113;color<=124;color++)for(unsigned cached=0;cached<2;cached++) {
  setup(2,9);draw61(110,80);CHECK(global_projectile91_used_members==4u);
  if(cached){finish();CHECK(ready&&last_output_valid);}
  rgb_palette[color]^=1;
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
 /* An unused61 color is NOT exempt when an old member actually sampled it. */
 for(unsigned old=0;old<2;old++) {
  setup(2,9);SDL_FillRect(game_screen,NULL,113);render_mirror_begin();
  member61_draw(old?145:91,110,80);CHECK(global_projectile91_used_members==(old?2u:1u));
  CHECK(global_projectile91_used_colors[113]);rgb_palette[113]^=1;
  finish();CHECK(!ready&&!last_output_valid);
 }
 /* An actual foreign-HD borrow also establishes palette dependencies. */
 setup(2,9);talon_tile();draw(110,80);
 CHECK(global_projectile91_used_members==1u&&global_projectile91_talon_dependency);
 CHECK(global_projectile91_used_colors[113]);rgb_palette[113]^=1;finish();CHECK(!ready&&!last_output_valid);
 /* Cache comparison remains all768 RGB bytes, even if61 never contributed. */
 setup(2,9);draw(110,80);finish();CHECK(ready&&global_projectile91_used_members==1u);
 rgb_palette[113]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 setup(2,9);draw61(110,80);finish();CHECK(ready&&global_projectile91_used_members==4u);
 rgb_palette[200]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
}
static void mutations61(const Uint8 *christmas_bank,size_t christmas_bytes)
{
 for(unsigned cached=0;cached<2;cached++)for(unsigned k=0;k<22;k++) {
  setup(2,9);draw61(110,80);CHECK(global_projectile91_used_members==4u&&!global_projectile91_fault);
  if(cached){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);}
  Asset *a=&projectile61_resources.member;
  switch(k) {
   case 0:a->rgba[100]^=1;break;
   case 1:a->initialized=false;break;
   case 2:a->valid=false;break;
   case 3:a->bank=ASSET_ENEMY_PROJECTILE145;break;
   case 4:a->index=145;break;
   case 5:a->w=11;break;
   case 6:a->h=13;break;
   case 7:a->anchor_x=1;break;
   case 8:a->anchor_y=1;break;
   case 9:a->density=4;break;
   case 10:livebank[100]^=1;break;
   case 11:spriteSheet8.size--;break;
   case 12:spriteSheet8.data=NULL;break;
   case 13:xmas=true;break;
   case 14:game_probe_original_reference=true;break;
   case 15:game_probe_missing=true;break;
   case 16:game_probe_invalid=true;break;
   case 17:game_probe_density=4;break;
   case 18:spriteSheet8=(Sprite2_array){christmas_bytes,(Uint8 *)christmas_bank};break;
   case 19:game_screen->pitch=321;break;
   case 20:VGAScreenSeg->w=319;break;
   case 21:canvas->w=2559;break;
  }
  if(k==19&&!cached) {
   /* Never read through an invalid pitch. Observe the real preflight, restore
    * safe memory geometry, then demand that its rejection remains sticky. */
   global_projectile91_observed_preflight();CHECK(global_projectile91_fault);
   game_screen->pitch=320;finish();
  }else if(cached)global_projectile91_check_cache();else finish();
  CHECK(!ready&&!last_output_valid);
  /* Restore surface geometry before SDL frees/reuses the controlled fixture. */
  if(k==17)game_probe_density=8;
  if(k==19)game_screen->pitch=320;
  if(k==20)VGAScreenSeg->w=320;
  if(k==21)canvas->w=2560;
 }
}
static void callbacks61(void)
{
 for(unsigned mode=0;mode<4;mode++) {
  setup(2,9);CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,61));
  CHECK(global_projectile91_used_members==4u&&global_projectile91_call.live);
  if(mode==0)render_mirror_entity_end(); /* missing native callbacks */
  else if(mode==1)CHECK(!render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,61));
  else {
   Uint8 src[168],mask[168];mask61(src,mask);unsigned i=0;while(i<168&&!mask[i])++i;CHECK(i<168);
   Uint8 *p=(Uint8 *)game_screen->pixels+(80+i/12)*320+110+i%12;
   if(mode==2){*p=src[i]^1;render_mirror_pixel(game_screen,p,0x1b,MIRROR_NORMAL);}
   else{*p=src[i];render_mirror_pixel(game_screen,p,0x1b,MIRROR_NORMAL);render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);}
  }
  CHECK(global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);
 }
}
static void bounds61(const Uint8 *christmas_bank,size_t christmas_bytes)
{
 const int ys[]={-13,-12,-6,0,180,190,199};
 for(unsigned k=0;k<sizeof(ys)/sizeof(*ys);k++) {
  setup(2,9);Uint8 src[168],mask[168],under[168];mask61(src,mask);memset(under,0x1b,sizeof(under));
  unsigned visible=0,output_visible=0;
  for(unsigned i=0;i<168;i++)if(mask[i]) {
   int y=ys[k]+(int)(i/12);if(y>=0&&y<200)++visible;if(y>=0&&y<184)++output_visible;
  }
  draw61(110,ys[k]);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
  CHECK(global_projectile91_used_members==(visible?4u:0u));
  CHECK(global_projectile91_contributed==(visible!=0));oracle61(110,ys[k],under,false);
  finish();if(output_visible){CHECK(ready&&last_output_valid);oracle61(110,ys[k],under,true);}
  else CHECK(!ready&&!last_output_valid);
 }
 const int xy[][2]={{-1,80},{309,80},{110,-14},{110,200}};
 for(unsigned k=0;k<sizeof(xy)/sizeof(*xy);k++) {
  setup(2,9);draw61(xy[k][0],xy[k][1]);
  CHECK(!global_projectile91_contributed&&!global_projectile91_used_members&&!global_projectile91_fault);
  finish();CHECK(!ready&&!last_output_valid);
 }
 /* A declined horizontal-wrap call must not poison an earlier old member. */
 setup(2,9);draw(110,80);draw61(309,80);
 CHECK(global_projectile91_used_members==1u&&!global_projectile91_fault);finish();CHECK(ready);
 setup(2,9);game_probe_density=4;draw61(110,80);
 CHECK(!global_projectile91_contributed&&!global_projectile91_used_members);game_probe_density=8;finish();CHECK(!ready);
 /* Flag-only Christmas decline is distinct from actual alternate-bank proof. */
 setup(2,9);xmas=true;draw61(110,80);CHECK(!global_projectile91_contributed);finish();CHECK(!ready);
 CHECK(christmas_bank&&christmas_bytes==32404);
 for(unsigned flag=0;flag<2;flag++) {
  setup(2,9);xmas=flag!=0;spriteSheet8=(Sprite2_array){christmas_bytes,(Uint8 *)christmas_bank};
  CHECK(!projectile61_source(spriteSheet8,61));draw61(110,80);
  CHECK(!global_projectile91_contributed&&!global_projectile91_used_members);finish();CHECK(!ready);
 }
 /* Same contents in a different call argument are not a bank identity lease. */
 setup(2,9);draw(40,80);draw145(80,80);Uint8 foreign[32060];memcpy(foreign,original,sizeof(foreign));
 draw61_bank(200,80,(Sprite2_array){sizeof(foreign),foreign});
 CHECK(global_projectile91_used_members==3u&&!global_projectile91_fault);finish();CHECK(ready);
}
static void transfer61(void)
{
 for(unsigned cached=0;cached<2;cached++) {
  setup(2,9);draw61(110,80);CHECK(global_projectile91_used_members==4u);
  Uint8 prior[96*112];for(unsigned i=0;i<96*112;i++) {
   size_t n=(size_t)(80*8+i/96)*2560+110*8+i%96;
   prior[i]=global_projectile91_owner[n]&&projectile61_resources.member.rgba[4*i+3]>0;
  }
  SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);
  memcpy(classic->pixels,game_screen->pixels,64000);uint64_t rng=mt_state_fingerprint();
  Uint32 saved_palette[256];memcpy(saved_palette,rgb_palette,sizeof(saved_palette));
  JE_MultiEnemyType actors;EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(actors,enemy,sizeof(enemy));memcpy(shots,enemyShot,sizeof(shots));
  /* Fixed integer geometry from pinned native mask/HDA analysis, not a runtime
   * search. Talon is binary alpha:61 soft RGB survives native-covered alpha0. */
  Uint32 witness_rgb=*at(canvas,960,648);
  CHECK(projectile61_resources.member.rgba[4*(8*96+80)+3]==16);
  blit_sprite2x2(classic,107,78,spriteSheet9,233);
  global_talon_pose(1,spriteSheet9,233,233,0);CHECK(global_talon_poses[0].visual==6);
  CHECK(render_mirror_global_player_ship(game_screen,107,78,spriteSheet9,233,MIRROR_NORMAL,1,233)==1);
  CHECK(global_talon_call.mask[3*24+13]&&global_talon_rgba[6][4*(24*192+104)+3]==0);
  blit_sprite2x2(game_screen,107,78,spriteSheet9,233);render_mirror_entity_end();
  CHECK(global_talon_contributed&&!global_talon_fault);
  CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(rng==mt_state_fingerprint());
  CHECK(!memcmp(saved_palette,rgb_palette,sizeof(saved_palette)));
  CHECK(!memcmp(actors,enemy,sizeof(enemy))&&!memcmp(shots,enemyShot,sizeof(shots)));SDL_FreeSurface(classic);
  unsigned copied=0,soft_copied=0;
  for(unsigned i=0;i<96*112;i++) {
   size_t n=(size_t)(80*8+i/96)*2560+110*8+i%96;
   if(prior[i]&&!global_projectile91_owner[n]&&global_talon_owner[n]&&global_talon_foreign[n]) {
    ++copied;if(projectile61_resources.member.rgba[4*i+3]<255)++soft_copied;
   }
  }
  CHECK(copied>0);CHECK(copied==267&&soft_copied==231);
  size_t witness=(size_t)648*2560+960;
  CHECK(!global_projectile91_owner[witness]&&global_talon_owner[witness]&&global_talon_foreign[witness]);
  CHECK(*at(canvas,960,648)==witness_rgb);
  CHECK(global_projectile91_contributed&&global_projectile91_used_members==4u&&!global_projectile91_fault);
  printf("61_TO_TALON copied=%u cached=%u\n",copied,cached);
  if(cached){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);CHECK(*at(output,960-24*8,648)==witness_rgb);}
  projectile61_resources.member.rgba[100]^=1;
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void lifecycle61(const char *missing61)
{
 setup(2,9);draw61(110,80);finish();CHECK(ready&&global_projectile91_used_members==4u);
 render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached);
 draw(40,80);draw145(80,80);CHECK(global_projectile91_used_members==3u&&!global_projectile91_fault);
 finish();CHECK(ready&&last_output_valid);render_mirror_global_reset();
 CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached&&!ready&&!last_output_valid);
 setup(2,9);draw61(110,80);finish();CHECK(ready);
 CHECK(render_mirror_set_global_assets(missing61));
 CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
 render_mirror_begin();draw61(200,80);CHECK(!global_projectile91_used_members&&!global_projectile91_fault);
 draw(40,80);finish();CHECK(ready&&global_projectile91_used_members==1u);
 CHECK(render_mirror_set_global_assets(valid_root));render_mirror_begin();
 CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);
 draw61(110,80);CHECK(global_projectile91_used_members==4u&&!global_projectile91_fault);finish();CHECK(ready);
 CHECK(render_mirror_set_global_assets(""));CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
 setup(2,9);draw61(110,80);finish();CHECK(ready);livebank[100]^=1;render_mirror_begin();
 CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);draw61(110,80);finish();CHECK(!ready);
}
static void projectile61_cases(const char *missing145,const char *bad145,const char *bad91,
                               const char *missing61,const char *bad61,const char *only61,
                               const Uint8 *christmas_bank,size_t christmas_bytes)
{
 unsigned first_case=cases,first_check=checks;
 positive61();mixed61();absence61(missing145,bad145,bad91,missing61,bad61,only61);
 palette61();mutations61(christmas_bank,christmas_bytes);callbacks61();
 bounds61(christmas_bank,christmas_bytes);transfer61();lifecycle61(missing61);
 printf("PASS shared61 native lifecycle: %u cases %u assertions; internal8 only; not gameplay/full build\n",cases-first_case,checks-first_check);
}
