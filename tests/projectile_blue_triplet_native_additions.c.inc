/* SPDX-License-Identifier: GPL-2.0-or-later
 * Controlled internal8 production-TU additions. Original264 remains byte-exact
 * and runs in separate modes. Not gameplay, physical-window or fullgate proof.
 */
static const unsigned blue_ids[6]={91,145,61,101,120,139};
static const unsigned blue_new[3]={101,120,139};
static char blue_roots[26][1200];
static const char *blue_root_names[26]={"valid","missing91","bad91","missing145","bad145","missing61","bad61","missing101","bad101","missing120","bad120","missing139","bad139","only101","only120","only139","old-only","header101","short101","trailing101","header120","short120","trailing120","header139","short139","trailing139"};
static unsigned blue_bit(unsigned id)
{for(unsigned i=0;i<6;i++)if(blue_ids[i]==id)return 1u<<i;return 0;}
static Asset *blue_asset(unsigned id)
{
 if(id==91)return &projectile91_resources.member;
 if(id==145)return &projectile145_resources.member;
 if(id==61)return &projectile61_resources.member;
 int slot=projectile_blue_triplet_slot(id);CHECK(slot>=0&&slot<3);return &projectile_blue_triplet_resources[slot].member;
}
static void blue_decode(unsigned id,Uint8 *src,Uint8 *mask)
{memset(src,0,168);memset(mask,0,168);CHECK(decode_tile(spriteSheet8,id,src,mask,12,0,0));}
static void blue_draw_bank(unsigned id,int x,int y,Sprite2_array bank)
{
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);
 memcpy(classic->pixels,game_screen->pixels,64000);uint64_t rng=mt_state_fingerprint();
 Uint32 pal[256];JE_MultiEnemyType actors;EnemyShotType shots[ENEMY_SHOT_MAX];
 memcpy(pal,rgb_palette,sizeof(pal));memcpy(actors,enemy,sizeof(enemy));memcpy(shots,enemyShot,sizeof(shots));
 blit_sprite2(classic,x,y,bank,id);draw_enemy_shot_sprite2(game_screen,x,y,bank,id);
 CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(rng==mt_state_fingerprint());
 CHECK(!memcmp(pal,rgb_palette,sizeof(pal)));CHECK(!memcmp(actors,enemy,sizeof(enemy)));CHECK(!memcmp(shots,enemyShot,sizeof(shots)));
 SDL_FreeSurface(classic);
}
static void blue_player_classic(unsigned id)
{
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);
 memcpy(classic->pixels,game_screen->pixels,64000);uint64_t rng=mt_state_fingerprint();
 Uint32 pal[256];JE_MultiEnemyType actors;EnemyShotType shots[ENEMY_SHOT_MAX];
 memcpy(pal,rgb_palette,sizeof(pal));memcpy(actors,enemy,sizeof(enemy));memcpy(shots,enemyShot,sizeof(shots));
 blit_sprite2(classic,40,80,spriteSheet8,id);draw_player_shot_sprite2(game_screen,40,80,spriteSheet8,id,0,id);
 CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(rng==mt_state_fingerprint());
 CHECK(!memcmp(pal,rgb_palette,sizeof(pal)));CHECK(!memcmp(actors,enemy,sizeof(enemy)));CHECK(!memcmp(shots,enemyShot,sizeof(shots)));
 CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_call.live);
 SDL_FreeSurface(classic);
}
static void blue_draw(unsigned id,int x,int y){blue_draw_bank(id,x,y,spriteSheet8);}
static void blue_setup(void){setup(3,1);}
static void blue_blank_under(Uint8 *under){memset(under,0x1b,168);}
static void blue_oracle(unsigned id,int x,int y,const Uint8 *under,bool final_output)
{
 const Uint8 *rgba=blue_asset(id)->rgba;CHECK(rgba);Uint8 src[168],mask[168];blue_decode(id,src,mask);
 unsigned occupied=0,soft=0,opaque=0,clear=0;
 for(unsigned c=0;c<168;c++)occupied+=mask[c]!=0;
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  unsigned i=(unsigned)(ay*96+ax),cell=(unsigned)((ay/8)*12+ax/8);const Uint8 *a=rgba+4*i;
  if(!a[3])++clear;else if(a[3]==255)++opaque;else ++soft;
  if(!mask[cell])CHECK(!a[0]&&!a[1]&&!a[2]&&!a[3]);
  int px=x*8+ax,py=y*8+ay;if(px<0||px>=2560||py<0||py>=1600)continue;
  Uint32 want=alpha(palette_rgb(under[cell]),a);
  if(final_output){if(px<24*8||px>=288*8||py>=184*8)continue;CHECK(*at(output,px-24*8,py)==want);}
  else CHECK(*at(canvas,px,py)==want);
 }
 if(id==101)CHECK(occupied==164&&soft==9240&&opaque==152&&clear==1360);
 else if(id==120)CHECK(occupied==168&&soft==10231&&opaque==0&&clear==521);
 else if(id==139)CHECK(occupied==130&&soft==7703&&opaque==159&&clear==2890);
}
/* New selected coverage epoch: these six native cells have exactly zero
 * authored RGBA. Their native callbacks and ownership remain mandatory. */
static const unsigned blue_zero_cells[6][2]={{12,0},{12,11},{13,0},{13,1},{13,10},{13,11}};
static void blue_zero_native(const Uint8 *under,Uint32 *want)
{
 unsigned n=0;for(unsigned c=0;c<6;c++)for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)
  want[n++]=palette_rgb(under[blue_zero_cells[c][0]*12+blue_zero_cells[c][1]]);
 CHECK(n==384);
}
static void blue_zero_tile(const Uint32 *tile,Uint32 *want)
{
 unsigned n=0;for(unsigned c=0;c<6;c++)for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)
  want[n++]=tile[(blue_zero_cells[c][0]*8+sy)*96+blue_zero_cells[c][1]*8+sx];
 CHECK(n==384);
}
static void blue_zero_owned(int x,int y)
{
 unsigned count=0;for(unsigned c=0;c<6;c++)for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(size_t)((y+blue_zero_cells[c][0])*8+sy)*2560+(x+blue_zero_cells[c][1])*8+sx;
  CHECK(global_projectile91_owner[n]==1&&hd_owner[n]==1);++count;
 }
 CHECK(count==384);
}
static void blue_zero_verify(int x,int y,const Uint32 *want,bool final_output)
{
 Uint8 source[168],mask[168];blue_decode(101,source,mask);const Uint8 *rgba=blue_asset(101)->rgba;CHECK(rgba);
 CHECK(global_projectile91_contributed&&(global_projectile91_used_members&8u)&&!global_projectile91_fault&&!global_projectile91_call.live);
 if(final_output)CHECK(ready&&last_output_valid&&global_projectile91_cached);
 unsigned count=0;for(unsigned c=0;c<6;c++)for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  unsigned cy=blue_zero_cells[c][0],cx=blue_zero_cells[c][1],cell=cy*12+cx,ay=cy*8+sy,ax=cx*8+sx;
  const Uint8 *a=rgba+4*(ay*96+ax);CHECK(mask[cell]&&!a[0]&&!a[1]&&!a[2]&&!a[3]);
  CHECK(((Uint8 *)game_screen->pixels)[(y+cy)*320+x+cx]==source[cell]);
  int px=x*8+(int)ax,py=y*8+(int)ay;size_t n=(size_t)py*2560+px;
  CHECK(global_projectile91_owner[n]==1&&hd_owner[n]==1);
  CHECK(*(final_output?at(output,px-24*8,py):at(canvas,px,py))==want[count]);++count;
 }
 CHECK(count==384);
}
static void blue_zero_blank(Uint32 *want)
{Uint8 under[168];blue_blank_under(under);blue_zero_native(under,want);}
static void blue_accept(void)
{finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);output_oracle();global_projectile91_check_cache();CHECK(ready&&last_output_valid);output_oracle();}
static void blue_positive(void)
{
 for(unsigned s=0;s<3;s++)for(unsigned pattern=0;pattern<2;pattern++) {
  blue_setup();Uint8 under[168];Uint32 zero_want[384];
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++){unsigned i=y*12+x;under[i]=(Uint8)(0x1b+(pattern?16*((x+y)%3):0));((Uint8 *)game_screen->pixels)[(80+y)*320+110+x]=under[i];}
  if(blue_new[s]==101)blue_zero_native(under,zero_want);
  render_mirror_begin();CHECK(!get_asset(spriteSheet8,blue_new[s],ENTITY_TILE));blue_player_classic(blue_new[s]);blue_draw(blue_new[s],110,80);CHECK(global_projectile91_used_members==blue_bit(blue_new[s])&&!global_projectile91_fault&&!global_projectile91_call.live);
  blue_oracle(blue_new[s],110,80,under,false);if(blue_new[s]==101)blue_zero_verify(110,80,zero_want,false);
  finish();CHECK(ready&&last_output_valid);blue_oracle(blue_new[s],110,80,under,true);if(blue_new[s]==101)blue_zero_verify(110,80,zero_want,true);
  global_projectile91_check_cache();CHECK(ready&&last_output_valid);blue_oracle(blue_new[s],110,80,under,true);
  if(blue_new[s]==101){blue_zero_verify(110,80,zero_want,true);printf("BLUE101_ZERO_NATIVE pattern=%u draw=384 finish=384 cache=384\n",pattern);}
 }
}
static void blue_bounds(void)
{
 const int ys[]={-13,-6,180,190,199};const int reject[][2]={{-1,80},{309,80},{110,-14},{110,200}};
 for(unsigned s=0;s<3;s++) {
  for(unsigned k=0;k<5;k++) {
   blue_setup();Uint8 src[168],mask[168],under[168];blue_decode(blue_new[s],src,mask);blue_blank_under(under);unsigned visible=0,output_visible=0;
   for(unsigned i=0;i<168;i++)if(mask[i]){int y=ys[k]+(int)(i/12);visible+=y>=0&&y<200;output_visible+=y>=0&&y<184;}
   blue_draw(blue_new[s],110,ys[k]);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);CHECK(global_projectile91_used_members==(visible?blue_bit(blue_new[s]):0));
   blue_oracle(blue_new[s],110,ys[k],under,false);finish();if(output_visible){CHECK(ready&&last_output_valid);blue_oracle(blue_new[s],110,ys[k],under,true);}else CHECK(!ready&&!last_output_valid);
  }
  for(unsigned k=0;k<4;k++){blue_setup();blue_draw(blue_new[s],reject[k][0],reject[k][1]);CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);}
 }
}
static void blue_canvas_snapshot(Uint32 *rgb)
{for(int y=0;y<112;y++)for(int x=0;x<96;x++)rgb[y*96+x]=*at(canvas,110*8+x,80*8+y);}
static void blue_output_expected(const Uint32 *rgb)
{for(int y=0;y<112;y++)for(int x=0;x<96;x++)CHECK(*at(output,(110-24)*8+x,80*8+y)==rgb[y*96+x]);}
static unsigned blue_mix_step(unsigned id,unsigned previous)
{
 Uint32 before[96*112];Uint8 owned[96*112];blue_canvas_snapshot(before);
 for(unsigned i=0;i<96*112;i++){size_t n=(size_t)(80*8+i/96)*2560+110*8+i%96;owned[i]=global_projectile91_owner[n];}
 blue_draw(id,110,80);const Uint8 *rgba=blue_asset(id)->rgba,*prior=blue_asset(previous)->rgba;CHECK(rgba&&prior);unsigned overlap=0;
 for(unsigned i=0;i<96*112;i++){CHECK(*at(canvas,110*8+i%96,80*8+i/96)==alpha(before[i],rgba+4*i));if(owned[i]&&rgba[4*i+3]&&prior[4*i+3])++overlap;}
 CHECK(overlap>0&&!global_projectile91_fault);
 if(id==101){Uint32 zero_want[384];blue_zero_tile(before,zero_want);blue_zero_verify(110,80,zero_want,false);}
 return overlap;
}
static void blue_mixed(void)
{
 /* Exactly12 unordered pairs containing a blue member, both real draw orders. */
 for(unsigned a=0;a<6;a++)for(unsigned b=a+1;b<6;b++)if(a>=3||b>=3)for(unsigned reverse=0;reverse<2;reverse++) {
  blue_setup();unsigned first=blue_ids[reverse?b:a],second=blue_ids[reverse?a:b];blue_draw(first,110,80);CHECK(global_projectile91_used_members==blue_bit(first));
  Uint32 zero_want[384];if(second==101){Uint32 before[96*112];blue_canvas_snapshot(before);blue_zero_tile(before,zero_want);if(first==120)blue_zero_owned(110,80);}
  CHECK(blue_mix_step(second,first)>0);CHECK(global_projectile91_used_members==(blue_bit(first)|blue_bit(second)));
  Uint32 want[96*112];blue_canvas_snapshot(want);finish();CHECK(ready&&last_output_valid);blue_output_expected(want);if(second==101)blue_zero_verify(110,80,zero_want,true);
  global_projectile91_check_cache();CHECK(ready&&last_output_valid);blue_output_expected(want);if(second==101)blue_zero_verify(110,80,zero_want,true);
  if(first==120&&second==101)printf("BLUE101_ZERO_HD prior=120 draw=384 finish=384 cache=384\n");
  blue_asset(first)->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
 /* Every member is an EARLIER contributor in one order; the blue subsequences
  * cover all6 permutations, including native volley101,139,120. Full63 bits
  * must survive at100 actual common authored pixels before dependency damage. */
 static const unsigned orders[6][6]={
  {91,145,61,120,139,101},{145,91,61,101,120,139},{61,91,145,139,120,101},
  {101,91,145,61,139,120},{120,91,145,61,101,139},{139,91,145,61,101,120}
 };
 for(unsigned first=0;first<6;first++)for(unsigned cached=0;cached<2;cached++) {
  blue_setup();CHECK(orders[first][0]==blue_ids[first]);blue_draw(orders[first][0],110,80);
  for(unsigned k=1;k<6;k++)CHECK(blue_mix_step(orders[first][k],orders[first][k-1])>0);
  unsigned common=0;for(unsigned i=0;i<96*112;i++){bool all=true;for(unsigned k=0;k<6;k++)all=all&&blue_asset(blue_ids[k])->rgba[4*i+3]!=0;if(all){size_t n=(size_t)(80*8+i/96)*2560+110*8+i%96;CHECK(global_projectile91_owner[n]);++common;}}
  CHECK(common==100&&global_projectile91_used_members==63u&&!global_projectile91_fault);
  Uint32 want[96*112];blue_canvas_snapshot(want);
  if(cached){finish();CHECK(ready&&last_output_valid);blue_output_expected(want);global_projectile91_check_cache();CHECK(ready&&last_output_valid);blue_output_expected(want);}
  blue_asset(blue_ids[first])->rgba[100]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void blue_good_disjoint(unsigned exclude)
{
 Uint8 under[168];blue_blank_under(under);
 for(unsigned k=0;k<6;k++)if(blue_ids[k]!=exclude){blue_draw(blue_ids[k],40+(int)k*32,80);CHECK(global_projectile91_used_members&blue_bit(blue_ids[k]));blue_oracle(blue_ids[k],40+(int)k*32,80,under,false);}
}
static void blue_absence(void)
{
 for(unsigned k=0;k<6;k++)for(unsigned corrupt=0;corrupt<2;corrupt++)for(unsigned warm=0;warm<2;warm++) {
  valid_root=blue_roots[1+2*k+corrupt];blue_setup();if(warm)blue_good_disjoint(blue_ids[k]);
  blue_draw(blue_ids[k],240,80);CHECK(!global_projectile91_fault);
  if(!warm){CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);blue_good_disjoint(blue_ids[k]);}
  CHECK(global_projectile91_used_members==(63u^blue_bit(blue_ids[k])));blue_accept();
 }
 for(unsigned s=0;s<3;s++) {
  valid_root=blue_roots[13+s];blue_setup();for(unsigned k=0;k<6;k++)blue_draw(blue_ids[k],40+(int)k*32,80);
  CHECK(global_projectile91_used_members==blue_bit(blue_new[s])&&!global_projectile91_fault);blue_accept();
 }
 for(unsigned warm=0;warm<2;warm++) {
  valid_root=blue_roots[16];blue_setup();if(warm)for(unsigned k=0;k<3;k++)blue_draw(blue_ids[k],40+(int)k*32,80);
  for(unsigned s=0;s<3;s++)blue_draw(blue_new[s],140+(int)s*32,80);
  if(!warm){CHECK(!global_projectile91_used_members);for(unsigned k=0;k<3;k++)blue_draw(blue_ids[k],40+(int)k*32,80);}
  CHECK(global_projectile91_used_members==7u&&!global_projectile91_fault);blue_accept();
 }
 for(unsigned s=0;s<3;s++)for(unsigned mode=0;mode<3;mode++) {
  valid_root=blue_roots[17+3*s+mode];blue_setup();blue_good_disjoint(blue_new[s]);blue_draw(blue_new[s],240,80);
  CHECK(global_projectile91_used_members==(63u^blue_bit(blue_new[s]))&&!global_projectile91_fault);blue_accept();
 }
 valid_root=blue_roots[0];
}
static bool blue_color_used(unsigned id,unsigned color)
{
 static const unsigned a[]={138,140,141,142,143,145,146,147,148,149,150,151,152,153,154,155,156,157,159};
 static const unsigned b[]={140,145,149,153,156,159};
 static const unsigned c[]={138,140,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159};
 const unsigned *p=id==101?a:id==120?b:c;unsigned n=id==101?19:id==120?6:18;
 for(unsigned i=0;i<n;i++)if(p[i]==color)return true;return false;
}
static void blue_palettes(void)
{
 /* Real21-color union;120 has NO exclusive palette index. Good members remain
  * eligible only when their actual subset and sampled underlay are untouched. */
 const unsigned colors[]={138,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159};
 for(unsigned c=0;c<21;c++)for(unsigned reverse=0;reverse<2;reverse++) {
  blue_setup();if(reverse)for(unsigned k=0;k<3;k++)blue_draw(blue_ids[k],40+(int)k*32,80);
  CHECK(!global_projectile91_used_colors[colors[c]]);rgb_palette[colors[c]]^=1;unsigned want=7u;
  for(unsigned j=0;j<3;j++){unsigned s=reverse?2-j:j,id=blue_new[s];blue_draw(id,140+(int)s*32,80);if(!blue_color_used(id,colors[c]))want|=blue_bit(id);}
  if(!reverse)for(unsigned k=0;k<3;k++)blue_draw(blue_ids[k],40+(int)k*32,80);
  CHECK(global_projectile91_used_members==want&&!global_projectile91_fault);blue_accept();
 }
 for(unsigned s=0;s<3;s++)for(unsigned c=0;c<21;c++)if(blue_color_used(blue_new[s],colors[c]))for(unsigned cached=0;cached<2;cached++) {
  blue_setup();blue_draw(blue_new[s],110,80);CHECK(global_projectile91_used_members==blue_bit(blue_new[s]));Uint32 zero_want[384];if(blue_new[s]==101){blue_zero_blank(zero_want);blue_zero_verify(110,80,zero_want,false);}if(cached){blue_accept();if(blue_new[s]==101)blue_zero_verify(110,80,zero_want,true);}
  rgb_palette[colors[c]]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
 blue_setup();SDL_FillRect(game_screen,NULL,144);render_mirror_begin();blue_draw(101,110,80);CHECK(!blue_color_used(101,144)&&global_projectile91_used_colors[144]);rgb_palette[144]^=1;finish();CHECK(!ready&&!last_output_valid);
 blue_setup();talon_tile();blue_draw(101,110,80);CHECK(global_projectile91_talon_dependency&&global_projectile91_used_colors[200]);rgb_palette[200]^=1;finish();CHECK(!ready&&!last_output_valid);
 blue_setup();blue_draw(120,110,80);blue_accept();CHECK(!blue_color_used(120,200));rgb_palette[200]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
}
static void blue_mutations(const Uint8 *xb,size_t xn)
{
 for(unsigned s=0;s<3;s++)for(unsigned k=0;k<11;k++)for(unsigned cached=0;cached<2;cached++) {
  blue_setup();blue_draw(blue_new[s],110,80);CHECK(global_projectile91_used_members==blue_bit(blue_new[s]));Uint32 zero_want[384];if(blue_new[s]==101){blue_zero_blank(zero_want);blue_zero_verify(110,80,zero_want,false);}if(cached){blue_accept();if(blue_new[s]==101)blue_zero_verify(110,80,zero_want,true);}Asset *a=blue_asset(blue_new[s]);Uint8 *saved=a->rgba;
  switch(k){case 0:a->rgba[100]^=1;break;case 1:a->initialized=false;break;case 2:a->valid=false;break;case 3:a->bank=ASSET_ENEMY_PROJECTILE61;break;case 4:a->index=blue_new[(s+1)%3];break;case 5:a->w=11;break;case 6:a->h=13;break;case 7:a->anchor_x=1;break;case 8:a->anchor_y=1;break;case 9:a->density=4;break;case 10:a->rgba=NULL;break;}
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);if(k==10)a->rgba=saved;
 }
 for(unsigned k=0;k<10;k++)for(unsigned cached=0;cached<2;cached++) {
  blue_setup();for(unsigned s=0;s<3;s++)blue_draw(blue_new[s],80+(int)s*40,80);CHECK(global_projectile91_used_members==56u);Uint32 zero_want[384];blue_zero_blank(zero_want);blue_zero_verify(80,80,zero_want,false);if(cached){blue_accept();blue_zero_verify(80,80,zero_want,true);}
  switch(k){case 0:livebank[100]^=1;break;case 1:spriteSheet8.size--;break;case 2:spriteSheet8.data=NULL;break;case 3:xmas=true;break;case 4:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};break;case 5:game_probe_original_reference=true;break;case 6:game_probe_missing=true;break;case 7:game_probe_invalid=true;break;case 8:game_probe_density=4;break;case 9:game_screen->pitch=321;break;}
  if(k==9&&!cached){global_projectile91_observed_preflight();CHECK(global_projectile91_fault);game_screen->pitch=320;finish();}else if(cached)global_projectile91_check_cache();else finish();
  CHECK(!ready&&!last_output_valid);if(k==8)game_probe_density=8;if(k==9)game_screen->pitch=320;
 }
}
static void blue_callbacks(void)
{
 for(unsigned s=0;s<3;s++)for(unsigned mode=0;mode<4;mode++) {
  blue_setup();CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,blue_new[s]));CHECK(global_projectile91_used_members==blue_bit(blue_new[s])&&global_projectile91_call.live);
  if(mode==0)render_mirror_entity_end();else if(mode==1)CHECK(!render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,blue_new[s]));else {
   Uint8 src[168],mask[168];blue_decode(blue_new[s],src,mask);unsigned i=0;while(i<168&&!mask[i])++i;CHECK(i<168);Uint8 *p=(Uint8 *)game_screen->pixels+(80+i/12)*320+110+i%12;
   if(mode==2){*p=src[i]^1;render_mirror_pixel(game_screen,p,0x1b,MIRROR_NORMAL);}else{*p=src[i];render_mirror_pixel(game_screen,p,0x1b,MIRROR_NORMAL);render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);}
  }
  CHECK(global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);
 }
}
static void blue_cold_scope(const Uint8 *xb,size_t xn)
{
 for(unsigned s=0;s<3;s++)for(unsigned mode=0;mode<5;mode++) {
  blue_setup();Uint8 foreign[32060];memcpy(foreign,original,sizeof(foreign));
  if(mode==0)xmas=true;
  if(mode==1||mode==2){spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};xmas=mode==2;CHECK(!projectile_blue_triplet_source(spriteSheet8,blue_new[s]));}
  if(mode==3)game_probe_density=4;
  if(mode==4){blue_draw(91,40,80);blue_draw_bank(blue_new[s],200,80,(Sprite2_array){sizeof(foreign),foreign});CHECK(global_projectile91_used_members==1u&&!global_projectile91_fault);blue_accept();}
  else{blue_draw(blue_new[s],110,80);CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);if(mode==3)game_probe_density=8;finish();CHECK(!ready&&!last_output_valid);}
 }
 blue_setup();blue_draw(92,110,80);CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);finish();CHECK(!ready&&!last_output_valid);
}
static void blue_transfer(void)
{
 const unsigned expected[]={1756,1864,1481},soft_expected[]={1721,1864,1454};
 const Uint8 witness_rgba[3][4]={{1,76,235,253},{17,79,228,29},{0,53,212,253}};
 for(unsigned s=0;s<3;s++)for(unsigned cached=0;cached<2;cached++) {
  blue_setup();unsigned id=blue_new[s];blue_draw(id,110,80);CHECK(global_projectile91_used_members==blue_bit(id));Uint8 prior[96*112];
  for(unsigned i=0;i<96*112;i++){size_t n=(size_t)(80*8+i/96)*2560+110*8+i%96;prior[i]=global_projectile91_owner[n]&&blue_asset(id)->rgba[4*i+3]>0;}
  CHECK(!memcmp(blue_asset(id)->rgba+4*(8*96+80),witness_rgba[s],4));Uint32 want=alpha(palette_rgb(0x1b),witness_rgba[s]);CHECK(*at(canvas,960,648)==want);
  SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
  uint64_t rng=mt_state_fingerprint();Uint32 pal[256];JE_MultiEnemyType actors;EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(pal,rgb_palette,sizeof(pal));memcpy(actors,enemy,sizeof(enemy));memcpy(shots,enemyShot,sizeof(shots));
  /* Predetermined prior61 geometry, no runtime search. Talon alpha is binary;
   * blue soft RGB is retained through native-covered transparent Talon pixels. */
  blit_sprite2x2(classic,107,78,spriteSheet9,233);global_talon_pose(1,spriteSheet9,233,233,0);CHECK(global_talon_poses[0].visual==6);
  CHECK(render_mirror_global_player_ship(game_screen,107,78,spriteSheet9,233,MIRROR_NORMAL,1,233)==1);CHECK(global_talon_call.mask[3*24+13]&&global_talon_rgba[6][4*(24*192+104)+3]==0);
  blit_sprite2x2(game_screen,107,78,spriteSheet9,233);render_mirror_entity_end();CHECK(global_talon_contributed&&!global_talon_fault);
  CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(rng==mt_state_fingerprint());CHECK(!memcmp(pal,rgb_palette,sizeof(pal)));CHECK(!memcmp(actors,enemy,sizeof(enemy))&&!memcmp(shots,enemyShot,sizeof(shots)));SDL_FreeSurface(classic);
  unsigned copied=0,soft=0;for(unsigned i=0;i<96*112;i++){size_t n=(size_t)(80*8+i/96)*2560+110*8+i%96;if(prior[i]&&!global_projectile91_owner[n]&&global_talon_owner[n]&&global_talon_foreign[n]){++copied;soft+=blue_asset(id)->rgba[4*i+3]<255;}}
  CHECK(copied>0&&copied==expected[s]&&soft==soft_expected[s]);size_t witness=(size_t)648*2560+960;CHECK(!global_projectile91_owner[witness]&&global_talon_owner[witness]&&global_talon_foreign[witness]);CHECK(*at(canvas,960,648)==want);
  CHECK(global_projectile91_contributed&&global_projectile91_used_members==blue_bit(id)&&!global_projectile91_fault);
  printf("BLUE_TO_TALON selector=%u copied=%u soft=%u cached=%u\n",id,copied,soft,cached);
  if(cached){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);CHECK(*at(output,960-24*8,648)==want);global_projectile91_check_cache();CHECK(ready&&last_output_valid);CHECK(*at(output,960-24*8,648)==want);}
  blue_asset(id)->rgba[100]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void blue_lifecycle(void)
{
 for(unsigned s=0;s<3;s++) {
  blue_setup();blue_draw(blue_new[s],110,80);blue_accept();render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached);
  blue_draw(91,40,80);blue_draw(145,80,80);blue_draw(61,120,80);CHECK(global_projectile91_used_members==7u);blue_accept();render_mirror_global_reset();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
  blue_setup();blue_draw(blue_new[s],110,80);blue_accept();CHECK(render_mirror_set_global_assets(blue_roots[7+2*s]));CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
  render_mirror_begin();blue_draw(blue_new[s],200,80);CHECK(!global_projectile91_used_members&&!global_projectile91_fault);blue_draw(91,40,80);blue_accept();
  CHECK(render_mirror_set_global_assets(blue_roots[0]));render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);blue_draw(blue_new[s],110,80);CHECK(global_projectile91_used_members==blue_bit(blue_new[s]));blue_accept();
  CHECK(render_mirror_set_global_assets(""));CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
 }
 blue_setup();for(unsigned s=0;s<3;s++)blue_draw(blue_new[s],80+(int)s*40,80);blue_accept();livebank[100]^=1;render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);
 for(unsigned s=0;s<3;s++)blue_draw(blue_new[s],80+(int)s*40,80);finish();CHECK(!ready&&!last_output_valid);
}
static int blue_triplet_main(int argc,char **argv)
{
 CHECK(argc==3&&!strcmp(argv[1],"--blue-triplet"));for(unsigned i=0;i<26;i++){int n=snprintf(blue_roots[i],sizeof(blue_roots[i]),"%s/%s",argv[2],blue_root_names[i]);CHECK(n>0&&(size_t)n<sizeof(blue_roots[i]));}
 valid_root=blue_roots[0];missing_root=blue_roots[1];read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));
 Uint32 n;read_exact(&n,4);CHECK(n==33484);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);
 Uint32 xn;read_exact(&xn,4);CHECK(xn==32404);Uint8 *xb=malloc(xn);CHECK(xb);read_exact(xb,xn);CHECK(fgetc(stdin)==EOF);
 unsigned first_case=cases,first_check=checks;
 blue_positive();blue_bounds();blue_mixed();blue_absence();blue_palettes();blue_mutations(xb,xn);blue_callbacks();blue_cold_scope(xb,xn);blue_transfer();blue_lifecycle();
 CHECK(cases-first_case==365);printf("PASS blue triplet native lifecycle: %u cases %u assertions; internal8 only; not gameplay/full build\n",cases-first_case,checks-first_check);free(xb);return 0;
}
