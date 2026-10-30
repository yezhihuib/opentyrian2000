/* SPDX-License-Identifier: GPL-2.0-or-later
 * NEW gold epoch2 implementation, NOT recovery of the unavailable 69d5 source.
 * Original629 helpers/source/oracles remain byte-exact in separate processes.
 * Controlled internal8 production-TU coverage, not JE_main/game/fullbuild.
 * Numeric art/overlap/transfer witnesses derive from GEOMETRY.json epoch2.
 */
static const unsigned gold_ids[8]={91,145,61,101,120,139,168,169};
static const unsigned gold_new[2]={168,169};
static char gold_roots[26][1200];
static const char *gold_root_names[26]={"valid","missing91","bad91","missing145","bad145","missing61","bad61","missing101","bad101","missing120","bad120","missing139","bad139","missing168","bad168","missing169","bad169","only168","only169","old-only","header168","short168","trailing168","header169","short169","trailing169"};
static unsigned gold_bit(unsigned id)
{for(unsigned i=0;i<8;i++)if(gold_ids[i]==id)return 1u<<i;return 0;}
static bool gold_is_new(unsigned id){return id==168||id==169;}
static Asset *gold_asset(unsigned id)
{
 if(!gold_is_new(id))return blue_asset(id);
 int slot=projectile_gold_pulse_slot(id);CHECK(slot>=0&&slot<2);
 return &projectile_gold_pulse_resources[slot].member;
}
static void gold_setup(void){setup(3,1);}
static void gold_draw(unsigned id,int x,int y){blue_draw_bank(id,x,y,spriteSheet8);}
/* Keep raw canvas outside support, but choose the exact actual production
 * underlay inside support: HD canvas when owned, otherwise native palette. */
typedef struct {Uint32 canvas[10752],under[10752];Uint8 owned[10752],native[168];} GoldBefore;
static void gold_snapshot(GoldBefore *b,int x,int y)
{
 memset(b,0,sizeof(*b));
 for(int cy=0;cy<14;cy++)for(int cx=0;cx<12;cx++)
  if(x+cx>=0&&x+cx<320&&y+cy>=0&&y+cy<200)b->native[cy*12+cx]=((Uint8 *)game_screen->pixels)[(y+cy)*320+x+cx];
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  int px=x*8+ax,py=y*8+ay;unsigned i=(unsigned)(ay*96+ax);
  if(px<0||px>=2560||py<0||py>=1600)continue;
  size_t n=(size_t)py*2560+px;b->canvas[i]=*at(canvas,px,py);b->owned[i]=global_projectile91_owner[n];
  b->under[i]=hd_owner[n]?b->canvas[i]:palette_rgb(b->native[(ay/8)*12+ax/8]);
 }
}
static unsigned gold_owned(unsigned id,int x,int y)
{
 Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned count=0,cells=0;
 for(unsigned c=0;c<168;c++)if(mask[c]) {
  ++cells;CHECK(x+(int)(c%12)>=0&&x+(int)(c%12)<320&&y+(int)(c/12)>=0&&y+(int)(c/12)<200);
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++) {
   size_t n=(size_t)((y+c/12)*8+sy)*2560+(x+c%12)*8+sx;
   CHECK(global_projectile91_owner[n]&&hd_owner[n]);++count;
  }
 }
 CHECK(count==cells*64&&count>0);if(id==168)CHECK(cells==97);if(id==169)CHECK(cells==69);return count;
}
static void gold_oracle(unsigned id,int x,int y,const GoldBefore *b,bool final_output)
{
 Asset *a=gold_asset(id);CHECK(a->rgba);Uint8 src[168],mask[168];blue_decode(id,src,mask);
 unsigned cells=0,soft=0,opaque=0,clear=0,zero_native=0,visible=0;
 for(unsigned c=0;c<168;c++)cells+=mask[c]!=0;
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  unsigned i=(unsigned)(ay*96+ax),c=(unsigned)((ay/8)*12+ax/8);const Uint8 *q=a->rgba+4*i;
  if(!q[3]){++clear;zero_native+=mask[c]!=0;CHECK(!q[0]&&!q[1]&&!q[2]);}else if(q[3]==255)++opaque;else ++soft;
  if(!mask[c])CHECK(!q[0]&&!q[1]&&!q[2]&&!q[3]);
  int px=x*8+ax,py=y*8+ay;if(px<0||px>=2560||py<0||py>=1600)continue;
  Uint32 want=mask[c]||q[3]?alpha(b->under[i],q):b->canvas[i];
  if(mask[c]) {
   ++visible;size_t n=(size_t)py*2560+px;
   CHECK(global_projectile91_owner[n]&&hd_owner[n]);
   CHECK(((Uint8 *)game_screen->pixels)[(y+ay/8)*320+x+ax/8]==src[c]);
  }
  if(final_output){if(px<24*8||px>=288*8||py>=184*8)continue;CHECK(*at(output,px-24*8,py)==want);}
  else CHECK(*at(canvas,px,py)==want);
 }
 CHECK(cells>0&&soft+opaque+clear==10752);
 if(id==168)CHECK(cells==97&&soft==5894&&opaque==0&&clear==4858&&zero_native==314);
 if(id==169)CHECK(cells==69&&soft==3575&&opaque==0&&clear==7177&&zero_native==841);
 if(visible)CHECK(global_projectile91_used_members&gold_bit(id));
}
/* Test all native-covered authored-alpha0 pixels, not a selected subset.
 * Only retain this before-image through final/cache when gold is last writer. */
static void gold_zero(unsigned id,int x,int y,const GoldBefore *b,bool final_output)
{
 CHECK(gold_is_new(id));Uint8 src[168],mask[168];blue_decode(id,src,mask);
 const Uint8 *rgba=gold_asset(id)->rgba;CHECK(rgba);unsigned count=0;
 CHECK(global_projectile91_contributed&&(global_projectile91_used_members&gold_bit(id))&&!global_projectile91_fault&&!global_projectile91_call.live);
 if(final_output)CHECK(ready&&last_output_valid&&global_projectile91_cached);
 for(unsigned ay=0;ay<112;ay++)for(unsigned ax=0;ax<96;ax++) {
  unsigned i=ay*96+ax,c=(ay/8)*12+ax/8;const Uint8 *q=rgba+4*i;
  if(!mask[c]||q[3])continue;
  CHECK(!q[0]&&!q[1]&&!q[2]);int px=x*8+(int)ax,py=y*8+(int)ay;
  CHECK(px>=24*8&&px<288*8&&py>=0&&py<184*8);
  size_t n=(size_t)py*2560+px;CHECK(global_projectile91_owner[n]&&hd_owner[n]);
  CHECK(((Uint8 *)game_screen->pixels)[(y+ay/8)*320+x+ax/8]==src[c]);
  CHECK(*(final_output?at(output,px-24*8,py):at(canvas,px,py))==b->under[i]);++count;
 }
 CHECK(count==(id==168?314u:841u));
}
static void gold_valid_draw(unsigned id,int x,int y,GoldBefore *b)
{
 gold_snapshot(b,x,y);gold_draw(id,x,y);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
 CHECK(global_projectile91_used_members&gold_bit(id));gold_oracle(id,x,y,b,false);gold_owned(id,x,y);
 if(gold_is_new(id))gold_zero(id,x,y,b,false);
}
static void gold_capture_rgb(Uint32 *rgb)
{for(int y=0;y<112;y++)for(int x=0;x<96;x++)rgb[y*96+x]=*at(canvas,110*8+x,80*8+y);}
static void gold_output_rgb(const Uint32 *rgb)
{for(int y=0;y<112;y++)for(int x=0;x<96;x++)CHECK(*at(output,(110-24)*8+x,80*8+y)==rgb[y*96+x]);}
static unsigned gold_pair_expected(unsigned a,unsigned b)
{
 static const unsigned pairs[2][8]={{2946,1662,2464,5865,5894,5302,5894,3575},{2601,1439,1157,3575,3575,3548,3575,3575}};
 if(!gold_is_new(a)){unsigned t=a;a=b;b=t;}CHECK(gold_is_new(a));
 for(unsigned k=0;k<8;k++)if(gold_ids[k]==b)return pairs[a==169][k];CHECK(false);return 0;
}
static unsigned gold_mix(unsigned id,unsigned previous,GoldBefore *b)
{
 gold_valid_draw(id,110,80,b);const Uint8 *a=gold_asset(id)->rgba,*p=gold_asset(previous)->rgba;CHECK(a&&p);unsigned count=0;
 for(unsigned i=0;i<10752;i++)if(b->owned[i]&&a[4*i+3]&&p[4*i+3])++count;
 CHECK(count>0);if(gold_is_new(id)||gold_is_new(previous))CHECK(count==gold_pair_expected(id,previous));return count;
}
static void gold_good_mask(unsigned bits)
{
 for(unsigned k=0;k<8;k++)if(bits&(1u<<k)){GoldBefore b;gold_valid_draw(gold_ids[k],40+(int)k*28,80,&b);}
 CHECK(global_projectile91_used_members==bits&&!global_projectile91_fault);
}
static void gold_full(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned pattern=0;pattern<2;pattern++) {
  gold_setup();unsigned id=gold_new[s];
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++)((Uint8 *)game_screen->pixels)[(80+y)*320+110+x]=(Uint8)(0x1b+(pattern?16*((x+y)%3):0));
  render_mirror_begin();CHECK(!get_asset(spriteSheet8,id,ENTITY_TILE));blue_player_classic(id);
  GoldBefore b;gold_valid_draw(id,110,80,&b);CHECK(global_projectile91_used_members==gold_bit(id));
  finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);gold_oracle(id,110,80,&b,true);gold_zero(id,110,80,&b,true);
  global_projectile91_check_cache();CHECK(ready&&last_output_valid);gold_oracle(id,110,80,&b,true);gold_zero(id,110,80,&b,true);
 }
}
static void gold_bounds(void)
{
 const int ys[]={-13,-6,180,190,199};const int reject[][2]={{-1,80},{309,80},{110,-14},{110,200}};
 for(unsigned s=0;s<2;s++) {
  for(unsigned k=0;k<5;k++) {
   gold_setup();unsigned id=gold_new[s];Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned visible=0,ov=0;
   for(unsigned i=0;i<168;i++)if(mask[i]){int y=ys[k]+(int)(i/12);visible+=y>=0&&y<200;ov+=y>=0&&y<184;}
   GoldBefore b;gold_snapshot(&b,110,ys[k]);gold_draw(id,110,ys[k]);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
   CHECK(global_projectile91_used_members==(visible?gold_bit(id):0));gold_oracle(id,110,ys[k],&b,false);
   finish();if(ov){CHECK(ready&&last_output_valid);gold_oracle(id,110,ys[k],&b,true);}else CHECK(!ready&&!last_output_valid);
  }
  for(unsigned k=0;k<4;k++){gold_setup();gold_draw(gold_new[s],reject[k][0],reject[k][1]);CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);}
 }
}
static void gold_pairs(void)
{
 for(unsigned a=0;a<8;a++)for(unsigned b=a+1;b<8;b++)if(a>=6||b>=6)for(unsigned rev=0;rev<2;rev++) {
  gold_setup();unsigned first=gold_ids[rev?b:a],last=gold_ids[rev?a:b];GoldBefore fb,lb;
  gold_valid_draw(first,110,80,&fb);CHECK(global_projectile91_used_members==gold_bit(first));
  if(first==120)CHECK(gold_owned(first,110,80)==10752);
  gold_mix(last,first,&lb);CHECK(global_projectile91_used_members==(gold_bit(first)|gold_bit(last)));
  Uint32 want[10752];gold_capture_rgb(want);finish();CHECK(ready&&last_output_valid);gold_output_rgb(want);if(gold_is_new(last))gold_zero(last,110,80,&lb,true);
  global_projectile91_check_cache();CHECK(ready&&last_output_valid);gold_output_rgb(want);if(gold_is_new(last))gold_zero(last,110,80,&lb,true);
  gold_asset(first)->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
}
static void gold_all8(void)
{
 for(unsigned first=0;first<8;first++)for(unsigned cached=0;cached<2;cached++) {
  gold_setup();GoldBefore b;gold_valid_draw(gold_ids[first],110,80,&b);
  for(unsigned k=1;k<8;k++)gold_mix(gold_ids[(first+k)%8],gold_ids[(first+k-1)%8],&b);
  unsigned common=0;for(unsigned i=0;i<10752;i++){bool all=true;for(unsigned k=0;k<8;k++)all=all&&gold_asset(gold_ids[k])->rgba[4*i+3]!=0;if(all){size_t n=(size_t)(640+i/96)*2560+880+i%96;CHECK(global_projectile91_owner[n]&&hd_owner[n]);++common;}}
  CHECK(common==100&&global_projectile91_used_members==255u&&(global_projectile91_used_members&128u)&&!global_projectile91_fault);
  Uint32 want[10752];gold_capture_rgb(want);if(cached){finish();CHECK(ready&&last_output_valid);gold_output_rgb(want);global_projectile91_check_cache();CHECK(ready&&last_output_valid);gold_output_rgb(want);}
  gold_asset(gold_ids[first])->rgba[100]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void gold_absence(void)
{
 for(unsigned k=0;k<8;k++)for(unsigned bad=0;bad<2;bad++)for(unsigned warm=0;warm<2;warm++) {
  valid_root=gold_roots[1+2*k+bad];gold_setup();unsigned bits=255u^(1u<<k);
  if(warm)gold_good_mask(bits);gold_draw(gold_ids[k],280,80);CHECK(!global_projectile91_fault);
  if(!warm){CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);gold_good_mask(bits);}
  CHECK(global_projectile91_used_members==bits);blue_accept();
 }
 valid_root=gold_roots[0];
}
static void gold_singletons(void)
{
 for(unsigned s=0;s<2;s++) {
  valid_root=gold_roots[17+s];gold_setup();for(unsigned k=0;k<8;k++)gold_draw(gold_ids[k],40+(int)k*28,80);
  CHECK(global_projectile91_used_members==gold_bit(gold_new[s])&&!global_projectile91_fault);gold_owned(gold_new[s],40+(int)(6+s)*28,80);blue_accept();
 }
 for(unsigned warm=0;warm<2;warm++) {
  valid_root=gold_roots[19];gold_setup();if(warm)gold_good_mask(63u);
  gold_draw(168,240,80);gold_draw(169,280,80);if(!warm){CHECK(!global_projectile91_used_members);gold_good_mask(63u);}
  CHECK(global_projectile91_used_members==63u&&!global_projectile91_fault);blue_accept();
 }
 valid_root=gold_roots[0];
}
static void gold_malformed(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<3;mode++) {
  valid_root=gold_roots[20+3*s+mode];gold_setup();unsigned bits=255u^gold_bit(gold_new[s]);gold_good_mask(bits);gold_draw(gold_new[s],280,80);
  CHECK(global_projectile91_used_members==bits&&!global_projectile91_fault);blue_accept();
 }
 valid_root=gold_roots[0];
}
static void gold_unused(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<2;mode++)for(unsigned warm=0;warm<2;warm++) {
  gold_setup();unsigned id=gold_new[s],bits=255u^gold_bit(id);GoldBefore b;gold_valid_draw(id,110,80,&b);blue_accept();
  render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached);
  if(warm)gold_good_mask(bits);if(mode)gold_asset(id)->valid=false;else gold_asset(id)->rgba[100]^=1;
  if(!warm)gold_good_mask(bits);gold_draw(id,280,80);CHECK(global_projectile91_used_members==bits&&!global_projectile91_fault);blue_accept();
 }
}
static void gold_palettes(void)
{
 /* Both gold members share123..127;123/124 are also real61 dependencies.
  * No invented per-gold palette isolation or whole-bank isolation. */
 for(unsigned c=123;c<=127;c++)for(unsigned warm=0;warm<2;warm++) {
  gold_setup();unsigned bits=c<=124?59u:63u;if(warm)gold_good_mask(bits);
  CHECK(!global_projectile91_used_colors[c]);rgb_palette[c]^=1;gold_draw(168,240,80);gold_draw(169,280,80);
  if(!warm){CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);gold_good_mask(bits);}
  CHECK(global_projectile91_used_members==bits&&!global_projectile91_fault);blue_accept();
 }
 for(unsigned s=0;s<2;s++)for(unsigned c=123;c<=127;c++)for(unsigned cached=0;cached<2;cached++) {
  gold_setup();GoldBefore b;unsigned id=gold_new[s];gold_valid_draw(id,110,80,&b);if(cached){blue_accept();gold_zero(id,110,80,&b,true);}
  rgb_palette[c]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned c=123;c<=124;c++)for(unsigned cached=0;cached<2;cached++) {
  gold_setup();GoldBefore b;gold_valid_draw(61,110,80,&b);CHECK(global_projectile91_used_members==4u);if(cached)blue_accept();
  rgb_palette[c]^=1;gold_draw(168,240,80);gold_draw(169,280,80);
  /* A later admission/preflight can already detect the used61 mutation.
   * This is composite rejection, NOT a claim cache was the first detector. */
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned s=0;s<2;s++) {
  gold_setup();SDL_FillRect(game_screen,NULL,200);render_mirror_begin();GoldBefore b;gold_valid_draw(gold_new[s],110,80,&b);
  CHECK(global_projectile91_used_colors[200]);rgb_palette[200]^=1;finish();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned s=0;s<2;s++) {
  gold_setup();talon_tile();unsigned overlap=0;for(unsigned i=0;i<10752;i++)overlap+=global_talon_owner[(size_t)(640+i/96)*2560+880+i%96]!=0;CHECK(overlap>0);
  GoldBefore b;gold_valid_draw(gold_new[s],110,80,&b);CHECK(global_projectile91_talon_dependency&&global_projectile91_used_colors[200]);
  rgb_palette[200]^=1;finish();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned s=0;s<2;s++) {
  gold_setup();GoldBefore b;gold_valid_draw(gold_new[s],110,80,&b);CHECK(!global_projectile91_used_colors[200]);blue_accept();
  rgb_palette[200]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
}
static void gold_mutations(const Uint8 *xb,size_t xn)
{
 for(unsigned s=0;s<2;s++)for(unsigned k=0;k<11;k++)for(unsigned cached=0;cached<2;cached++) {
  gold_setup();unsigned id=gold_new[s];GoldBefore b;gold_valid_draw(id,110,80,&b);CHECK(global_projectile91_used_members==gold_bit(id));if(cached){blue_accept();gold_zero(id,110,80,&b,true);}
  Asset *a=gold_asset(id);Uint8 *saved=a->rgba;
  switch(k){case 0:a->rgba[100]^=1;break;case 1:a->initialized=false;break;case 2:a->valid=false;break;case 3:a->bank=ASSET_ENEMY_BLUE_TRIPLET;break;case 4:a->index=gold_new[1-s];break;case 5:a->w=11;break;case 6:a->h=13;break;case 7:a->anchor_x=1;break;case 8:a->anchor_y=1;break;case 9:a->density=4;break;case 10:a->rgba=NULL;break;}
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);if(k==10)a->rgba=saved;
 }
 for(unsigned k=0;k<10;k++)for(unsigned cached=0;cached<2;cached++) {
  gold_setup();GoldBefore b[2];gold_valid_draw(168,80,80,&b[0]);gold_valid_draw(169,140,80,&b[1]);CHECK(global_projectile91_used_members==192u);
  if(cached){blue_accept();gold_zero(168,80,80,&b[0],true);gold_zero(169,140,80,&b[1],true);}
  switch(k){case 0:livebank[100]^=1;break;case 1:spriteSheet8.size--;break;case 2:spriteSheet8.data=NULL;break;case 3:xmas=true;break;case 4:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};break;case 5:game_probe_original_reference=true;break;case 6:game_probe_missing=true;break;case 7:game_probe_invalid=true;break;case 8:game_probe_density=4;break;case 9:game_screen->pitch=321;break;}
  if(k==9&&!cached){global_projectile91_observed_preflight();CHECK(global_projectile91_fault);game_screen->pitch=320;finish();}else if(cached)global_projectile91_check_cache();else finish();
  CHECK(!ready&&!last_output_valid);if(k==8)game_probe_density=8;if(k==9)game_screen->pitch=320;
 }
}
static void gold_callbacks(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<4;mode++) {
  gold_setup();unsigned id=gold_new[s];CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,id));CHECK(global_projectile91_used_members==gold_bit(id)&&global_projectile91_call.live);
  if(mode==0)render_mirror_entity_end();else if(mode==1)CHECK(!render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,id));else {
   Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned i=0;while(i<168&&!mask[i])++i;CHECK(i<168);Uint8 *p=(Uint8 *)game_screen->pixels+(80+i/12)*320+110+i%12;
   if(mode==2){*p=src[i]^1;render_mirror_pixel(game_screen,p,0x1b,MIRROR_NORMAL);}else{*p=src[i];render_mirror_pixel(game_screen,p,0x1b,MIRROR_NORMAL);render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);}
  }
  CHECK(global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);
 }
}
static void gold_cold(const Uint8 *xb,size_t xn)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<5;mode++) {
  gold_setup();unsigned id=gold_new[s];Uint8 foreign[32060];memcpy(foreign,original,sizeof(foreign));
  if(mode==0)xmas=true;if(mode==1||mode==2){spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};xmas=mode==2;CHECK(!projectile_gold_pulse_source(spriteSheet8,id));}if(mode==3)game_probe_density=4;
  if(mode==4){GoldBefore b;gold_valid_draw(91,40,80,&b);blue_draw_bank(id,200,80,(Sprite2_array){sizeof(foreign),foreign});CHECK(global_projectile91_used_members==1u&&!global_projectile91_fault);blue_accept();}
  else{gold_draw(id,110,80);CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);if(mode==3)game_probe_density=8;finish();CHECK(!ready&&!last_output_valid);}
 }
}
static void gold_transfer(void)
{
 const unsigned expected[2]={974,735},zeros[2]={86,85},wx[2]={41,44},wy[2]={50,50};
 const Uint8 witness[2][4]={{251,251,242,253},{251,251,252,253}};
 const Uint32 witness_rgb[2]={0xfffafaf1u,0xfffafafbu};
 for(unsigned s=0;s<2;s++)for(unsigned cached=0;cached<2;cached++) {
  gold_setup();unsigned id=gold_new[s];GoldBefore b;gold_valid_draw(id,110,80,&b);CHECK(global_projectile91_used_members==gold_bit(id));
  Uint8 prior[10752],zero[10752];Uint8 src[168],mask[168];blue_decode(id,src,mask);const Uint8 *rgba=gold_asset(id)->rgba;
  for(unsigned i=0;i<10752;i++){size_t n=(size_t)(640+i/96)*2560+880+i%96;bool owned=global_projectile91_owner[n]!=0;prior[i]=owned&&rgba[4*i+3]>0;zero[i]=owned&&mask[(i/96/8)*12+(i%96)/8]&&rgba[4*i+3]==0;}
  unsigned wi=wy[s]*96+wx[s];CHECK(!memcmp(rgba+4*wi,witness[s],4));Uint32 want=alpha(palette_rgb(0x1b),witness[s]);CHECK(want==witness_rgb[s]);
  int px=880+(int)wx[s],py=640+(int)wy[s];CHECK(*at(canvas,px,py)==want);
  SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
  uint64_t rng=mt_state_fingerprint();Uint32 pal[256];JE_MultiEnemyType actors;EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(pal,rgb_palette,sizeof(pal));memcpy(actors,enemy,sizeof(enemy));memcpy(shots,enemyShot,sizeof(shots));
  /* Fixed geometry derived from new pinned bytes before native execution.
   * Talon is binary-alpha: gold soft RGB transfers through Talon native-alpha0. */
  blit_sprite2x2(classic,107,78,spriteSheet9,233);global_talon_pose(1,spriteSheet9,233,233,0);CHECK(global_talon_poses[0].visual==6);
  CHECK(render_mirror_global_player_ship(game_screen,107,78,spriteSheet9,233,MIRROR_NORMAL,1,233)==1);
  unsigned tx=wx[s]+24,ty=wy[s]+16;CHECK(global_talon_call.mask[(ty/8)*24+tx/8]&&global_talon_rgba[6][4*(ty*192+tx)+3]==0);
  blit_sprite2x2(game_screen,107,78,spriteSheet9,233);render_mirror_entity_end();CHECK(global_talon_contributed&&!global_talon_fault);
  CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(rng==mt_state_fingerprint());CHECK(!memcmp(pal,rgb_palette,sizeof(pal)));CHECK(!memcmp(actors,enemy,sizeof(enemy))&&!memcmp(shots,enemyShot,sizeof(shots)));SDL_FreeSurface(classic);
  unsigned copied=0,soft=0,az=0;for(unsigned i=0;i<10752;i++){size_t n=(size_t)(640+i/96)*2560+880+i%96;bool transfer=!global_projectile91_owner[n]&&global_talon_owner[n]&&global_talon_foreign[n];if(prior[i]&&transfer){++copied;soft+=rgba[4*i+3]<255;}if(zero[i]&&transfer)++az;}
  CHECK(copied>0&&copied==expected[s]&&soft==expected[s]&&az==zeros[s]);size_t wn=(size_t)py*2560+px;CHECK(!global_projectile91_owner[wn]&&global_talon_owner[wn]&&global_talon_foreign[wn]);CHECK(*at(canvas,px,py)==want);
  CHECK(global_projectile91_contributed&&global_projectile91_used_members==gold_bit(id)&&!global_projectile91_fault);
  printf("GOLD_TO_TALON selector=%u copied=%u soft=%u alpha0=%u cached=%u\n",id,copied,soft,az,cached);
  if(cached){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);CHECK(*at(output,px-24*8,py)==want);global_projectile91_check_cache();CHECK(ready&&last_output_valid);CHECK(*at(output,px-24*8,py)==want);}
  gold_asset(id)->rgba[100]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void gold_lifecycle(void)
{
 for(unsigned s=0;s<2;s++) {
  gold_setup();GoldBefore b;unsigned id=gold_new[s];gold_valid_draw(id,110,80,&b);blue_accept();render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached);
  gold_good_mask(63u);CHECK(!(global_projectile91_used_members&192u));blue_accept();render_mirror_global_reset();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
  gold_setup();gold_valid_draw(id,110,80,&b);blue_accept();CHECK(render_mirror_set_global_assets(gold_roots[13+2*s]));CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
  render_mirror_begin();gold_draw(id,280,80);CHECK(!global_projectile91_used_members&&!global_projectile91_fault);gold_good_mask(1u);blue_accept();
  CHECK(render_mirror_set_global_assets(gold_roots[0]));render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);gold_valid_draw(id,110,80,&b);CHECK(global_projectile91_used_members==gold_bit(id));blue_accept();
  CHECK(render_mirror_set_global_assets(""));CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
 }
 gold_setup();gold_good_mask(255u);CHECK(global_projectile91_used_members==255u);blue_accept();livebank[100]^=1;render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);
 for(unsigned k=0;k<8;k++)gold_draw(gold_ids[k],40+(int)k*28,80);finish();CHECK(!ready&&!last_output_valid);
}
static void gold_animation(void)
{
 /* Test fixture step uses the literal animate increment/wrap rule, then real
  * wrapper calls across frames. JE_main/emission/movement/collision NOT run. */
 for(unsigned mode=0;mode<6;mode++) {
  valid_root=mode==0||mode==5?gold_roots[0]:gold_roots[12+mode];gold_setup();
  memset(&enemyShot[0],0,sizeof(enemyShot[0]));enemyShot[0].sgr=168;enemyShot[0].animax=mode==5?0:2;enemyShot[0].sx=110;enemyShot[0].sy=80;
  unsigned frames=mode==5?2u:3u;
  for(unsigned f=0;f<frames;f++) {
   if(f)render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached);
   if(enemyShot[0].animax!=0){if(++enemyShot[0].animate>=enemyShot[0].animax)enemyShot[0].animate=0;}
   unsigned id=enemyShot[0].sgr+enemyShot[0].animate;CHECK(id==(mode==5?168u:(f==1?168u:169u)));
   unsigned absent=mode==1||mode==2?168u:mode==3||mode==4?169u:0u;GoldBefore b;gold_snapshot(&b,110,80);gold_draw(id,110,80);
   if(id==absent){CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);}
   else{CHECK(global_projectile91_used_members==gold_bit(id)&&!global_projectile91_fault);gold_oracle(id,110,80,&b,false);gold_zero(id,110,80,&b,false);finish();CHECK(ready&&last_output_valid);gold_oracle(id,110,80,&b,true);gold_zero(id,110,80,&b,true);global_projectile91_check_cache();CHECK(ready&&last_output_valid);gold_zero(id,110,80,&b,true);}
  }
 }
 valid_root=gold_roots[0];
}
static void gold_group(const char *name,unsigned before,unsigned expected)
{CHECK(cases-before==expected);printf("GOLD_GROUP name=%s cases=%u\n",name,cases-before);}
static int gold_pulse_main(int argc,char **argv)
{
 CHECK(argc==3&&!strcmp(argv[1],"--gold-pulse"));for(unsigned i=0;i<26;i++){int n=snprintf(gold_roots[i],sizeof(gold_roots[i]),"%s/%s",argv[2],gold_root_names[i]);CHECK(n>0&&(size_t)n<sizeof(gold_roots[i]));}
 valid_root=gold_roots[0];missing_root=gold_roots[1];read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));
 Uint32 n;read_exact(&n,4);CHECK(n==33484);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);
 Uint32 xn;read_exact(&xn,4);CHECK(xn==32404);Uint8 *xb=malloc(xn);CHECK(xb);read_exact(xb,xn);CHECK(fgetc(stdin)==EOF);
 unsigned first_case=cases,first_check=checks,b;
 b=cases;gold_full();gold_group("full_tile_native_patterns",b,4);
 b=cases;gold_bounds();gold_group("bounds",b,18);
 b=cases;gold_pairs();gold_group("pair_orders",b,26);
 b=cases;gold_all8();gold_group("all8_early_dependency",b,16);
 b=cases;gold_absence();gold_group("missing_bad",b,32);
 b=cases;gold_singletons();gold_group("singletons_oldonly",b,4);
 b=cases;gold_malformed();gold_group("malformed_gold",b,6);
 b=cases;gold_unused();gold_group("unused_memory_payload_ready",b,8);
 b=cases;gold_palettes();gold_group("palette",b,40);
 b=cases;gold_mutations(xb,xn);gold_group("used_resource_shared",b,64);
 b=cases;gold_callbacks();gold_group("callbacks",b,8);
 b=cases;gold_cold(xb,xn);gold_group("cold_scope",b,10);
 b=cases;gold_transfer();gold_group("Talon_transfer",b,4);
 b=cases;gold_lifecycle();gold_group("lifecycle",b,5);
 b=cases;gold_animation();gold_group("controlled_animation",b,6);
 CHECK(cases-first_case==251);printf("PASS gold pulse native lifecycle: %u cases %u assertions; internal8 only; not gameplay/full build\n",cases-first_case,checks-first_check);free(xb);return 0;
}
