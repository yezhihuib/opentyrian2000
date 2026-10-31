/* SPDX-License-Identifier: GPL-2.0-or-later
 * PREPARED ONLY: independent static enemy162/260 production-TU companion.
 * The inherited six sources, gold body, wrappers and four stdout contracts are
 * not edited. This mode is controlled internal8, never gameplay/full-build proof.
 * Each setup is one case. Expectations below are fixed-byte predictions until
 * a separately authorized fresh native run establishes actual observations.
 */
static const unsigned statics_ids[10]={91,145,61,101,120,139,168,169,162,260};
static const unsigned statics_new[2]={162,260};
static const char *statics_root_names[]={"valid","missing91","bad91","missing145","bad145","missing61","bad61","missing101","bad101","missing120","bad120","missing139","bad139","missing168","bad168","missing169","bad169","missing162","bad162","missing260","bad260","only162","only260","old-only","header162","short162","trailing162","header260","short260","trailing260","magic162","density162","width162","height162","anchorx162","anchory162","magic260","density260","width260","height260","anchorx260","anchory260"};
static char statics_roots[sizeof(statics_root_names)/sizeof(*statics_root_names)][1200];
static unsigned statics_bit(unsigned id)
{for(unsigned k=0;k<10;k++)if(statics_ids[k]==id)return 1u<<k;return 0u;}
static bool statics_is_new(unsigned id){return id==162||id==260;}
static Asset *statics_asset(unsigned id)
{
 if(!statics_is_new(id))return gold_asset(id);
 int slot=projectile_statics_slot(id);CHECK(slot>=0&&slot<2);
 return &projectile_statics_resources[slot].member;
}
static void statics_setup(void){setup(3,1);}
static void statics_draw(unsigned id,int x,int y){blue_draw_bank(id,x,y,spriteSheet8);}
/* Full-tile arithmetic is independent of the production blending function.
 * A native-covered authored-alpha0 pixel owns the genuine underlay, while
 * outside-native alpha0 never introduces new ownership. */
typedef struct {Uint32 canvas[10752],under[10752];Uint8 owned[10752],native[168];} StaticsBefore;
static void statics_snapshot(StaticsBefore *b,int x,int y)
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
static void statics_oracle(unsigned id,int x,int y,const StaticsBefore *b,bool final_output)
{
 const Uint8 *rgba=statics_asset(id)->rgba;CHECK(rgba);Uint8 src[168],mask[168];blue_decode(id,src,mask);
 unsigned cells=0,soft=0,opaque=0,clear=0,zero_native=0,visible=0;
 for(unsigned c=0;c<168;c++)cells+=mask[c]!=0;
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  unsigned i=(unsigned)(ay*96+ax),c=(unsigned)((ay/8)*12+ax/8);const Uint8 *q=rgba+4*i;
  if(!q[3]){++clear;zero_native+=mask[c]!=0;CHECK(!q[0]&&!q[1]&&!q[2]);}else if(q[3]==255)++opaque;else ++soft;
  if(!mask[c])CHECK(!q[0]&&!q[1]&&!q[2]&&!q[3]);
  int px=x*8+ax,py=y*8+ay;if(px<0||px>=2560||py<0||py>=1600)continue;
  Uint32 want=mask[c]?alpha(b->under[i],q):b->canvas[i];
  size_t n=(size_t)py*2560+px;
  CHECK(global_projectile91_owner[n]<=1&&global_projectile91_foreign[n]<=1);
  if(mask[c]) {
   ++visible;CHECK(global_projectile91_owner[n]==1&&hd_owner[n]==1);
   CHECK(((Uint8 *)game_screen->pixels)[(y+ay/8)*320+x+ax/8]==src[c]);
  }else CHECK(global_projectile91_owner[n]==b->owned[i]);
  if(final_output){if(px<24*8||px>=288*8||py>=184*8)continue;CHECK(*at(output,px-24*8,py)==want);}
  else CHECK(*at(canvas,px,py)==want);
 }
 CHECK(cells>0&&soft+opaque+clear==10752);
 if(id==162)CHECK(cells==24&&soft==1380&&opaque==12&&clear==9360&&zero_native==144);
 if(id==260)CHECK(cells==86&&soft==5216&&opaque==1&&clear==5535&&zero_native==287);
 if(visible)CHECK(global_projectile91_used_members&statics_bit(id));
}
static void statics_callbacks_seen(unsigned id,int x,int y)
{
 Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned visible=0,seen=0;
 for(unsigned c=0;c<168;c++) {
  bool v=mask[c]&&x+(int)(c%12)>=0&&x+(int)(c%12)<320&&y+(int)(c/12)>=0&&y+(int)(c/12)<200;
  visible+=v;seen+=global_projectile91_call.seen[c]!=0;CHECK((global_projectile91_call.seen[c]!=0)==v);
 }
 CHECK(seen==visible&&!global_projectile91_call.left&&!global_projectile91_call.live);
 if(x==110&&y==80&&id==162)CHECK(seen==24);
 if(x==110&&y==80&&id==260)CHECK(seen==86);
}
static void statics_valid(unsigned id,int x,int y,StaticsBefore *b)
{
 statics_snapshot(b,x,y);statics_draw(id,x,y);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
 CHECK(global_projectile91_used_members&statics_bit(id));statics_callbacks_seen(id,x,y);statics_oracle(id,x,y,b,false);
}
static void statics_expected(Uint32 *want,unsigned id,const StaticsBefore *b)
{
 Uint8 src[168],mask[168];blue_decode(id,src,mask);const Uint8 *rgba=statics_asset(id)->rgba;
 for(unsigned i=0;i<10752;i++)want[i]=mask[(i/96/8)*12+(i%96)/8]?alpha(b->under[i],rgba+4*i):b->canvas[i];
}
static void statics_output_expected(const Uint32 *want,int x,int y)
{
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  int px=x*8+ax,py=y*8+ay;if(px<192||px>=2304||py<0||py>=1472)continue;
  CHECK(*at(output,px-192,py)==want[ay*96+ax]);
 }
}
static void statics_good_mask(unsigned bits)
{
 CHECK(!(bits&~1023u));
 for(unsigned k=0;k<10;k++)if(bits&(1u<<k)) {
  StaticsBefore b;statics_valid(statics_ids[k],40+48*(int)(k%5),60+40*(int)(k/5),&b);
 }
 CHECK(global_projectile91_used_members==bits&&!global_projectile91_fault);
}
static void statics_full(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned pattern=0;pattern<2;pattern++) {
  statics_setup();unsigned id=statics_new[s];
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++)((Uint8 *)game_screen->pixels)[(80+y)*320+110+x]=(Uint8)(27+(pattern?16*((x+y)%3):0));
  render_mirror_begin();CHECK(!get_asset(spriteSheet8,id,ENTITY_TILE));blue_player_classic(id);
  StaticsBefore b;statics_valid(id,110,80,&b);CHECK(global_projectile91_used_members==statics_bit(id));
  Asset *a=statics_asset(id);CHECK(a->initialized&&a->valid&&a->bank==154&&a->index==id&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y&&a->density==8);
  CHECK(asteroid1_stamp(a->rgba,43008)==(s?UINT64_C(0xfa2ac27b3212b610):UINT64_C(0x97621110c318d6a5)));
  CHECK(projectile_statics_resources[s].checked&&projectile_statics_resources[s].valid&&!strcmp(projectile_statics_resources[s].root,valid_root));
  CHECK(global_projectile91_member(id)==(s?512u:256u));
  finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);statics_oracle(id,110,80,&b,true);
  global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==statics_bit(id));statics_oracle(id,110,80,&b,true);
 }
}
static void statics_hd_underlay(void)
{
 for(unsigned s=0;s<2;s++) {
  statics_setup();StaticsBefore before,last;statics_valid(120,110,80,&before);statics_valid(statics_new[s],110,80,&last);
  unsigned zero=0;Uint8 src[168],mask[168];blue_decode(statics_new[s],src,mask);const Uint8 *rgba=statics_asset(statics_new[s])->rgba;
  for(unsigned i=0;i<10752;i++)if(mask[(i/96/8)*12+(i%96)/8]&&!rgba[4*i+3]){CHECK(last.owned[i]&&last.under[i]==last.canvas[i]);++zero;}
  CHECK(zero==(s?287u:144u));finish();CHECK(ready&&last_output_valid);statics_oracle(statics_new[s],110,80,&last,true);
  global_projectile91_check_cache();CHECK(ready&&last_output_valid);statics_oracle(statics_new[s],110,80,&last,true);
 }
}
static void statics_bounds(void)
{
 const int accept[][2]={{0,80},{308,80},{110,-13},{110,-6},{110,180},{110,190},{110,199}};
 const int reject[][2]={{-1,80},{309,80},{110,-14},{110,200}};
 for(unsigned s=0;s<2;s++) {
  for(unsigned k=0;k<7;k++) {
   statics_setup();unsigned id=statics_new[s];int x=accept[k][0],y=accept[k][1];Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned visible=0,output_visible=0;
   for(unsigned c=0;c<168;c++)if(mask[c]){int cx=x+(int)(c%12),cy=y+(int)(c/12);visible+=cy>=0&&cy<200;output_visible+=cx>=24&&cx<288&&cy>=0&&cy<184;}
   StaticsBefore b;statics_snapshot(&b,x,y);statics_draw(id,x,y);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
   statics_callbacks_seen(id,x,y);CHECK(global_projectile91_used_members==(visible?statics_bit(id):0u));statics_oracle(id,x,y,&b,false);
   finish();if(output_visible){CHECK(ready&&last_output_valid);statics_oracle(id,x,y,&b,true);global_projectile91_check_cache();CHECK(ready&&last_output_valid);statics_oracle(id,x,y,&b,true);}else CHECK(!ready&&!last_output_valid);
  }
  for(unsigned k=0;k<4;k++){statics_setup();statics_draw(statics_new[s],reject[k][0],reject[k][1]);CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);}
 }
}
static unsigned statics_pair_intersection(unsigned a,unsigned b)
{
 static const unsigned counts[2][10]={{1392,539,0,1392,1392,1392,1392,1341,1392,1392},{3226,1558,1102,5216,5217,5163,4349,3240,1392,5217}};
 if(!statics_is_new(a)){unsigned t=a;a=b;b=t;}CHECK(statics_is_new(a));
 for(unsigned k=0;k<10;k++)if(statics_ids[k]==b)return counts[a==260][k];CHECK(false);return 0;
}
static void statics_pairs(void)
{
 /* 16 new-vs-old pairs plus162/260, each in both orders.162/61 has exactly
  * zero positive-alpha overlap: it is tested, not skipped or repositioned. */
 for(unsigned a=0;a<10;a++)for(unsigned b=a+1;b<10;b++)if(a>=8||b>=8)for(unsigned reverse=0;reverse<2;reverse++) {
  statics_setup();unsigned first=statics_ids[reverse?b:a],last=statics_ids[reverse?a:b];StaticsBefore fb,lb;Uint32 want[10752];
  statics_valid(first,110,80,&fb);CHECK(global_projectile91_used_members==statics_bit(first));statics_valid(last,110,80,&lb);statics_expected(want,last,&lb);
  const Uint8 *one=statics_asset(first)->rgba,*two=statics_asset(last)->rgba;unsigned intersection=0;
  for(unsigned i=0;i<10752;i++)if(one[4*i+3]&&two[4*i+3]){CHECK(lb.owned[i]);++intersection;}
  CHECK(intersection==statics_pair_intersection(first,last));if((first==162&&last==61)||(first==61&&last==162))CHECK(intersection==0);else CHECK(intersection>0);
  CHECK(global_projectile91_used_members==(statics_bit(first)|statics_bit(last)));
  finish();CHECK(ready&&last_output_valid);statics_output_expected(want,110,80);
  global_projectile91_check_cache();CHECK(ready&&last_output_valid);statics_output_expected(want,110,80);
  statics_asset(first)->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
}
static void statics_all10_same_origin(void)
{
 for(unsigned first=0;first<10;first++)for(unsigned cached=0;cached<2;cached++) {
  statics_setup();StaticsBefore b;Uint32 want[10752];
  for(unsigned k=0;k<10;k++){statics_valid(statics_ids[(first+k)%10],110,80,&b);statics_expected(want,statics_ids[(first+k)%10],&b);}
  unsigned alpha_common=0,native_common=0;Uint8 masks[10][168],src[168];
  for(unsigned k=0;k<10;k++)blue_decode(statics_ids[k],src,masks[k]);
  for(unsigned c=0;c<168;c++){bool all=true;for(unsigned k=0;k<10;k++)all=all&&masks[k][c];native_common+=all;}
  for(unsigned i=0;i<10752;i++){bool all=true;for(unsigned k=0;k<10;k++)all=all&&statics_asset(statics_ids[k])->rgba[4*i+3]!=0;alpha_common+=all;}
  CHECK(alpha_common==0&&native_common==0&&global_projectile91_used_members==1023u&&(global_projectile91_used_members&768u)==768u);
  if(cached){finish();CHECK(ready&&last_output_valid);statics_output_expected(want,110,80);global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==1023u);statics_output_expected(want,110,80);}
  statics_asset(statics_ids[first])->rgba[100]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void statics_all10_sentinels(void)
{
 /* Fixed two-row layout; no extending the inherited clipped x40+28*k row. */
 for(unsigned damaged=0;damaged<10;damaged++)for(unsigned cached=0;cached<2;cached++) {
  statics_setup();StaticsBefore b;Uint32 want[10][10752];
  for(unsigned k=0;k<10;k++){int x=40+48*(int)(k%5),y=60+40*(int)(k/5);statics_valid(statics_ids[k],x,y,&b);statics_expected(want[k],statics_ids[k],&b);}
  CHECK(global_projectile91_used_members==1023u);
  if(cached){finish();CHECK(ready&&last_output_valid);for(unsigned k=0;k<10;k++)statics_output_expected(want[k],40+48*(int)(k%5),60+40*(int)(k/5));global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==1023u);for(unsigned k=0;k<10;k++)statics_output_expected(want[k],40+48*(int)(k%5),60+40*(int)(k/5));}
  statics_asset(statics_ids[damaged])->rgba[100]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void statics_absence(void)
{
 for(unsigned k=0;k<10;k++)for(unsigned bad=0;bad<2;bad++)for(unsigned warm=0;warm<2;warm++) {
  valid_root=statics_roots[1+2*k+bad];statics_setup();unsigned bits=1023u&~(1u<<k);
  if(warm)statics_good_mask(bits);statics_draw(statics_ids[k],280,140);CHECK(!global_projectile91_fault);
  if(!warm){CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);statics_good_mask(bits);}
  CHECK(global_projectile91_used_members==bits);blue_accept();
 }
 valid_root=statics_roots[0];
}
static void statics_singletons(void)
{
 for(unsigned s=0;s<2;s++) {
  valid_root=statics_roots[21+s];statics_setup();
  for(unsigned k=0;k<10;k++)statics_draw(statics_ids[k],40+48*(int)(k%5),60+40*(int)(k/5));
  CHECK(global_projectile91_used_members==statics_bit(statics_new[s])&&!global_projectile91_fault);blue_accept();
 }
 for(unsigned warm=0;warm<2;warm++) {
  valid_root=statics_roots[23];statics_setup();if(warm)statics_good_mask(255u);
  statics_draw(162,240,140);statics_draw(260,280,140);
  if(!warm){CHECK(!global_projectile91_used_members);statics_good_mask(255u);}
  CHECK(global_projectile91_used_members==255u&&!global_projectile91_fault);blue_accept();
 }
 valid_root=statics_roots[0];
}
static void statics_malformed(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<9;mode++) {
  unsigned root=mode<3?24+3*s+mode:30+6*s+(mode-3);
  valid_root=statics_roots[root];statics_setup();unsigned id=statics_new[s],bits=1023u&~statics_bit(id);
  statics_good_mask(bits);statics_draw(id,280,140);
  CHECK(projectile_statics_resources[s].checked&&!projectile_statics_resources[s].valid);
  CHECK(global_projectile91_used_members==bits&&!global_projectile91_fault);blue_accept();
 }
 valid_root=statics_roots[0];
}
static void statics_readiness(void)
{
 for(unsigned s=0;s<2;s++) {
  valid_root=statics_roots[17+2*s];statics_setup();unsigned id=statics_new[s];
  unsigned char before[sizeof(projectile_statics_resources)];memcpy(before,projectile_statics_resources,sizeof(before));
  CHECK(projectile_statics_slot(0)<0&&!projectile_statics_resource(valid_root,0)&&!projectile_statics_source(spriteSheet8,0)&&!projectile_statics_palette_matches(0));
  CHECK(!memcmp(before,projectile_statics_resources,sizeof(before)));
  CHECK(!projectile_statics_resource(valid_root,id));CHECK(projectile_statics_resources[s].checked&&!projectile_statics_resources[s].valid&&!projectile_statics_resources[1-s].checked);
  CHECK(!strcmp(projectile_statics_resources[s].root,valid_root));
  memcpy(before,projectile_statics_resources,sizeof(before));CHECK(render_mirror_set_global_assets(valid_root));CHECK(!memcmp(before,projectile_statics_resources,sizeof(before)));
  CHECK(!projectile_statics_resource(valid_root,id)&&!projectile_statics_resource(statics_roots[0],id));
  CHECK(!memcmp(before,projectile_statics_resources,sizeof(before))); /* No implicit retry/new epoch. */
  CHECK(projectile_statics_resource(valid_root,statics_new[1-s]));
  CHECK(render_mirror_set_global_assets(statics_roots[0]));CHECK(!projectile_statics_resources[0].checked&&!projectile_statics_resources[1].checked);
  render_mirror_begin();StaticsBefore b;statics_valid(id,110,80,&b);blue_accept();
  CHECK(global_projectile91_used_members==statics_bit(id));
  projectile_statics_shutdown();CHECK(!projectile_statics_resources[0].checked&&!projectile_statics_resources[1].checked);
  CHECK(projectile_statics_resource(statics_roots[0],id));
 }
 valid_root=statics_roots[0];
 for(unsigned s=0;s<2;s++) {
  statics_setup();char longroot[1025];memset(longroot,'x',sizeof(longroot)-1);longroot[sizeof(longroot)-1]='\0';
  CHECK(!projectile_statics_resource(NULL,statics_new[s])&&!projectile_statics_resource("",statics_new[s])&&!projectile_statics_resource(longroot,statics_new[s]));
  CHECK(!projectile_statics_resources[0].checked&&!projectile_statics_resources[1].checked);
 }
}
static void statics_unused(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<2;mode++)for(unsigned warm=0;warm<2;warm++) {
  statics_setup();unsigned id=statics_new[s],bits=1023u&~statics_bit(id);StaticsBefore b;statics_valid(id,110,80,&b);blue_accept();
  render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached);
  if(warm)statics_good_mask(bits);if(mode)statics_asset(id)->valid=false;else statics_asset(id)->rgba[100]^=1;
  if(!warm)statics_good_mask(bits);statics_draw(id,280,140);
  CHECK(global_projectile91_used_members==bits&&!global_projectile91_fault);blue_accept();
 }
}
static const unsigned statics_colors[12]={113,116,117,119,120,121,122,123,124,125,126,127};
static const unsigned statics_color_bits[12]={516u,516u,516u,516u,516u,516u,772u,964u,708u,960u,960u,448u};
static void statics_palette_admission(void)
{
 /* Shared61/gold colors are real dependencies. Never label one as unused
  * after an affected member or a foreign-HD underlay has contributed. */
 for(unsigned c=0;c<12;c++)for(unsigned warm=0;warm<2;warm++) {
  statics_setup();unsigned good=1023u&~statics_color_bits[c];
  if(warm)statics_good_mask(good);CHECK(!global_projectile91_used_colors[statics_colors[c]]);
  rgb_palette[statics_colors[c]]^=1;
  for(unsigned k=0;k<10;k++)if(statics_color_bits[c]&(1u<<k))statics_draw(statics_ids[k],280,140);
  if(!warm){CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);statics_good_mask(good);}
  CHECK(global_projectile91_used_members==good&&!global_projectile91_fault);blue_accept();
 }
}
static void statics_palette_direct(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned c=0;c<12;c++)if(statics_color_bits[c]&statics_bit(statics_new[s]))for(unsigned cached=0;cached<2;cached++) {
  statics_setup();StaticsBefore b;unsigned id=statics_new[s];statics_valid(id,110,80,&b);if(cached)blue_accept();
  rgb_palette[statics_colors[c]]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned s=0;s<2;s++)for(unsigned cached=0;cached<2;cached++) {
  statics_setup();SDL_FillRect(game_screen,NULL,200);render_mirror_begin();StaticsBefore b;statics_valid(statics_new[s],110,80,&b);
  CHECK(global_projectile91_used_colors[200]);if(cached)blue_accept();rgb_palette[200]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned s=0;s<2;s++) {
  statics_setup();StaticsBefore b;statics_valid(statics_new[s],110,80,&b);CHECK(!global_projectile91_used_colors[200]);blue_accept();
  rgb_palette[200]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid); /* Whole output palette cache, not member isolation. */
 }
}
static void statics_palette_composite_preflight(void)
{
 for(unsigned c=0;c<12;c++) {
  statics_setup();unsigned first=(statics_color_bits[c]&4u)?61:168;StaticsBefore b;statics_valid(first,110,80,&b);
  CHECK(statics_color_bits[c]&statics_bit(first));rgb_palette[statics_colors[c]]^=1;
  statics_draw(162,240,140);statics_draw(260,280,140);CHECK(global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);
 }
}
static void statics_used_resource_direct(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<13;mode++)for(unsigned cached=0;cached<2;cached++) {
  statics_setup();unsigned id=statics_new[s];StaticsBefore b;statics_valid(id,110,80,&b);if(cached)blue_accept();
  Asset *a=statics_asset(id);Uint8 *saved=a->rgba;
  switch(mode){case 0:a->rgba[100]^=1;break;case 1:a->initialized=false;break;case 2:a->valid=false;break;case 3:a->bank=ASSET_ENEMY_GOLD_PULSE;break;case 4:a->index=statics_new[1-s];break;case 5:a->w=11;break;case 6:a->h=13;break;case 7:a->anchor_x=1;break;case 8:a->anchor_y=1;break;case 9:a->density=4;break;case 10:a->rgba=NULL;break;case 11:projectile_statics_resources[s].valid=false;break;case 12:projectile_statics_resources[s].root[0]^=1;break;}
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);if(mode==10)a->rgba=saved;
 }
}
static void statics_source_scope_direct(const Uint8 *xb,size_t xn)
{
 for(unsigned mode=0;mode<12;mode++)for(unsigned cached=0;cached<2;cached++) {
  statics_setup();StaticsBefore b[2];statics_valid(162,80,80,&b[0]);statics_valid(260,140,80,&b[1]);CHECK(global_projectile91_used_members==768u);if(cached)blue_accept();
  switch(mode){case 0:livebank[100]^=1;break;case 1:livebank[0]^=1;break;case 2:spriteSheet8.size--;break;case 3:spriteSheet8.data=NULL;break;case 4:xmas=true;break;case 5:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};break;case 6:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};xmas=true;break;case 7:spriteSheet12=spriteSheet8;break;case 8:game_probe_original_reference=true;break;case 9:game_probe_missing=true;break;case 10:game_probe_invalid=true;break;case 11:game_probe_density=4;break;}
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);if(mode==11)game_probe_density=8;
 }
}
static void statics_layout_direct(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<8;mode++)for(unsigned cached=0;cached<2;cached++) {
  statics_setup();StaticsBefore b;statics_valid(statics_new[s],110,80,&b);if(cached)blue_accept();
  if(!cached)final_copy();
  SDL_Surface *surfaces[4]={game_screen,VGAScreenSeg,canvas,output};SDL_Surface *target=surfaces[mode%4];int width=target->w;void *pixels=target->pixels;
  if(mode<4)target->w--;else target->pixels=surfaces[(mode%4+1)%4]->pixels;
  /* Each invalid layout is first observed by the direct final/cache guard. */
  if(cached)global_projectile91_check_cache();else {
   /* final_copy itself is a native copy, and aliasing it can write across an
    * RGB backing. Supply its unchanged valid bytes before the layout fault. */
   render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);
  }
  CHECK(!ready&&!last_output_valid);target->w=width;target->pixels=pixels;
 }
}
static void statics_callbacks(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<6;mode++) {
  statics_setup();unsigned id=statics_new[s];CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,id));
  CHECK(global_projectile91_used_members==statics_bit(id)&&global_projectile91_call.live&&global_projectile91_call.left==(s?86u:24u));
  if(mode==0)render_mirror_entity_end();else if(mode==1)CHECK(!render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,id));else {
   Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned c=0;while(c<168&&!mask[c])++c;CHECK(c<168);
   Uint8 *p=(Uint8 *)game_screen->pixels+(80+c/12)*320+110+c%12;
   if(mode==2){*p=src[c]^1;render_mirror_pixel(game_screen,p,27,MIRROR_NORMAL);}
   if(mode==3){*p=src[c];render_mirror_pixel(game_screen,p,27,MIRROR_NORMAL);render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);}
   if(mode==4){*p=src[c];render_mirror_pixel(game_screen,p,27,MIRROR_SHADOW);}
   if(mode==5){p=(Uint8 *)game_screen->pixels+79*320+110;*p=27;render_mirror_pixel(game_screen,p,27,MIRROR_NORMAL);}
  }
  CHECK(global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);
 }
}
static void statics_transfer(void)
{
 const unsigned expected[2]={526,1122},soft_expected[2]={521,1122},zeros[2]={35,6},wx[2]={58,59},wy[2]={36,17};
 const Uint8 witness[2][4]={{244,177,55,254},{231,62,14,253}};
 const Uint32 witness_rgb[2]={0xfff4b137u,0xffe73f0fu};
 for(unsigned s=0;s<2;s++)for(unsigned cached=0;cached<2;cached++) {
  statics_setup();unsigned id=statics_new[s];StaticsBefore b;statics_valid(id,110,80,&b);CHECK(global_projectile91_used_members==statics_bit(id));
  Uint8 prior[10752],zero[10752];Uint8 src[168],mask[168];blue_decode(id,src,mask);const Uint8 *rgba=statics_asset(id)->rgba;
  for(unsigned i=0;i<10752;i++){size_t n=(size_t)(640+i/96)*2560+880+i%96;bool owned=global_projectile91_owner[n]!=0;prior[i]=owned&&rgba[4*i+3]>0;zero[i]=owned&&mask[(i/96/8)*12+(i%96)/8]&&rgba[4*i+3]==0;}
  unsigned wi=wy[s]*96+wx[s];CHECK(!memcmp(rgba+4*wi,witness[s],4));Uint32 want=alpha(palette_rgb(0x1b),witness[s]);CHECK(want==witness_rgb[s]);
  int px=880+(int)wx[s],py=640+(int)wy[s];CHECK(*at(canvas,px,py)==want);
  SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
  uint64_t rng=mt_state_fingerprint();Uint32 pal[256];JE_MultiEnemyType actors;EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(pal,rgb_palette,sizeof(pal));memcpy(actors,enemy,sizeof(enemy));memcpy(shots,enemyShot,sizeof(shots));
  /* Fixed geometry derived from new pinned bytes before native execution.
   * Talon is binary-alpha: statics soft RGB transfers through Talon native-alpha0. */
  blit_sprite2x2(classic,107,78,spriteSheet9,233);global_talon_pose(1,spriteSheet9,233,233,0);CHECK(global_talon_poses[0].visual==6);
  CHECK(render_mirror_global_player_ship(game_screen,107,78,spriteSheet9,233,MIRROR_NORMAL,1,233)==1);
  unsigned tx=wx[s]+24,ty=wy[s]+16;CHECK(global_talon_call.mask[(ty/8)*24+tx/8]&&global_talon_rgba[6][4*(ty*192+tx)+3]==0);
  blit_sprite2x2(game_screen,107,78,spriteSheet9,233);render_mirror_entity_end();CHECK(global_talon_contributed&&!global_talon_fault);
  CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(rng==mt_state_fingerprint());CHECK(!memcmp(pal,rgb_palette,sizeof(pal)));CHECK(!memcmp(actors,enemy,sizeof(enemy))&&!memcmp(shots,enemyShot,sizeof(shots)));SDL_FreeSurface(classic);
  unsigned copied=0,soft=0,az=0,transferred=0;for(unsigned i=0;i<10752;i++){size_t n=(size_t)(640+i/96)*2560+880+i%96;bool transfer=!global_projectile91_owner[n]&&global_talon_owner[n]&&global_talon_foreign[n];transferred+=transfer;if(prior[i]&&transfer){++copied;soft+=rgba[4*i+3]<255;}if(zero[i]&&transfer)++az;}
  CHECK(copied>0&&copied==expected[s]&&soft==soft_expected[s]&&az==zeros[s]&&transferred==copied+az);size_t wn=(size_t)py*2560+px;CHECK(!global_projectile91_owner[wn]&&global_talon_owner[wn]&&global_talon_foreign[wn]);CHECK(*at(canvas,px,py)==want);
  CHECK(global_projectile91_contributed&&global_projectile91_used_members==statics_bit(id)&&!global_projectile91_fault);
  printf("STATICS_TO_TALON selector=%u copied=%u soft=%u alpha0=%u cached=%u\n",id,copied,soft,az,cached);
  if(cached){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_projectile91_used_members==statics_bit(id));CHECK(*at(output,px-24*8,py)==want);global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==statics_bit(id));CHECK(*at(output,px-24*8,py)==want);}
  statics_asset(id)->rgba[100]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void statics_talon_underlay(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<2;mode++)for(unsigned cached=0;cached<2;cached++) {
  statics_setup();talon_tile();StaticsBefore b;Uint8 src[168],mask[168];blue_decode(statics_new[s],src,mask);unsigned overlap=0;
  for(unsigned i=0;i<10752;i++)if(mask[(i/96/8)*12+(i%96)/8])overlap+=global_talon_owner[(size_t)(640+i/96)*2560+880+i%96]!=0;
  CHECK(overlap>0);statics_valid(statics_new[s],110,80,&b);CHECK(global_projectile91_talon_dependency&&global_projectile91_used_colors[200]);
  if(cached){finish();CHECK(ready&&last_output_valid);statics_oracle(statics_new[s],110,80,&b,true);global_projectile91_check_cache();CHECK(ready&&last_output_valid);statics_oracle(statics_new[s],110,80,&b,true);}
  size_t saved=spriteSheet9.size;if(mode)spriteSheet9.size--;else rgb_palette[200]^=1;
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);spriteSheet9.size=saved;
 }
}
static void statics_cold_warm_scope(const Uint8 *xb,size_t xn)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<11;mode++)for(unsigned warm=0;warm<2;warm++) {
  statics_setup();unsigned id=statics_new[s];Uint8 foreign[32060];memcpy(foreign,original,sizeof(foreign));Sprite2_array bank=spriteSheet8;
  /* Same selected decoded art in Christmas does not authenticate its bank. */
  Uint8 ns[168]={0},nm[168]={0},xs[168]={0},xm[168]={0};CHECK(decode_tile(spriteSheet8,id,ns,nm,12,0,0));CHECK(decode_tile((Sprite2_array){xn,(Uint8 *)xb},id,xs,xm,12,0,0));CHECK(!memcmp(ns,xs,168)&&!memcmp(nm,xm,168));
  if(warm){StaticsBefore b;statics_valid(91,40,60,&b);}
  switch(mode){case 0:xmas=true;break;case 1:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};bank=spriteSheet8;break;case 2:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};bank=spriteSheet8;xmas=true;break;case 3:game_probe_density=4;break;case 4:bank=(Sprite2_array){sizeof(foreign),foreign};break;case 5:spriteSheet12=spriteSheet8;break;case 6:bank.size--;break;case 7:bank.data=NULL;break;case 8:game_probe_original_reference=true;break;case 9:game_probe_missing=true;break;case 10:game_probe_invalid=true;break;}
  CHECK(!render_mirror_enemy_shot(game_screen,110,80,bank,id));CHECK(!global_projectile91_call.live);
  if(mode==3)game_probe_density=8;
  if(warm&&(mode==4||mode==6||mode==7)){CHECK(global_projectile91_used_members==1u&&!global_projectile91_fault);blue_accept();}
  else{if(warm)CHECK(global_projectile91_fault);else CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);finish();CHECK(!ready&&!last_output_valid);}
 }
}
static void statics_lifecycle(void)
{
 for(unsigned s=0;s<2;s++) {
  statics_setup();StaticsBefore b;unsigned id=statics_new[s];statics_valid(id,110,80,&b);blue_accept();render_mirror_begin();
  CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached);
  statics_good_mask(255u);CHECK(!(global_projectile91_used_members&768u));blue_accept();render_mirror_global_reset();
  CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid&&!active);
  statics_setup();statics_valid(id,110,80,&b);blue_accept();CHECK(render_mirror_set_global_assets(statics_roots[17+2*s]));
  CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
  render_mirror_begin();statics_draw(id,280,140);CHECK(!global_projectile91_used_members&&!global_projectile91_fault);statics_good_mask(1u);blue_accept();
  CHECK(render_mirror_set_global_assets(statics_roots[0]));render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);statics_valid(id,110,80,&b);blue_accept();
  CHECK(render_mirror_set_global_assets(""));CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
 }
 statics_setup();statics_good_mask(1023u);blue_accept();render_mirror_hud_shutdown();
 CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached&&!global_projectile91_owner&&!global_projectile91_foreign&&!ready&&!last_output_valid);
 CHECK(!projectile_statics_resources[0].checked&&!projectile_statics_resources[1].checked);
 statics_setup();statics_good_mask(1023u);blue_accept();livebank[100]^=1;render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);
 for(unsigned k=0;k<10;k++)statics_draw(statics_ids[k],40+48*(int)(k%5),60+40*(int)(k/5));finish();CHECK(!ready&&!last_output_valid);
 statics_setup();CHECK(render_mirror_set_global_assets(""));render_mirror_begin();statics_draw(162,110,80);statics_draw(260,160,80);
 CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);finish();CHECK(!ready&&!last_output_valid);
}
static void statics_later_writers(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<4;mode++) {
  statics_setup();unsigned id=statics_new[s];StaticsBefore b;statics_valid(id,110,80,&b);Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned c=0;while(c<168&&!mask[c])++c;CHECK(c<168);
  int x=110+(int)(c%12),y=80+(int)(c/12);Uint8 *p;
  if(mode==0){p=(Uint8 *)game_screen->pixels+y*320+x;*p=58;render_mirror_pixel(game_screen,p,src[c],MIRROR_NORMAL);finish();}
  else{blue_accept();if(mode==3){
   /* Revoke every owned native cell by legitimate final writes, never by
    * clearing a private owner array. Provenance must outlive all pixel owners. */
   for(unsigned j=0;j<168;j++)if(mask[j]){int xx=110+(int)(j%12),yy=80+(int)(j/12);p=(Uint8 *)VGAScreenSeg->pixels+yy*320+xx-24;*p=58;render_mirror_pixel(VGAScreenSeg,p,src[j],MIRROR_NORMAL);}
   for(unsigned i=0;i<10752;i++)CHECK(!global_projectile91_owner[(size_t)(640+i/96)*2560+880+i%96]);
  }else{p=(Uint8 *)VGAScreenSeg->pixels+y*320+x-24;*p=58;if(mode==1)render_mirror_pixel(VGAScreenSeg,p,src[c],MIRROR_NORMAL);else{SDL_Rect r={x-24,y,1,1};render_mirror_rect(VGAScreenSeg,&r);}}}
  CHECK(ready&&last_output_valid&&global_projectile91_contributed&&global_projectile91_used_members==statics_bit(id));
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){size_t n=(size_t)(y*8+sy)*2560+x*8+sx;CHECK(!global_projectile91_owner[n]&&!global_projectile91_foreign[n]);CHECK(*at(output,(x-24)*8+sx,y*8+sy)==palette_rgb(58));}
  global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==statics_bit(id));
  statics_asset(id)->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
}
static void statics_fades(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<4;mode++) {
  statics_setup();StaticsBefore b;statics_valid(statics_new[s],110,80,&b);blue_accept();Uint32 want[10752];statics_expected(want,statics_new[s],&b);SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);
  CHECK(global_projectile91_cached&&have_fade_saved&&last_output_valid); /* This valid controlled fixture must exercise, not skip, the fade lease. */
  CHECK(have_fade_saved&&global_projectile91_used_members==statics_bit(statics_new[s]));
  if(mode==3){
   /* Real positive integer palette step; no float/rounded substitute. */
   for(unsigned i=0;i<256;i++){Uint32 old=rgb_palette[i],next=old&0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}rgb_palette[i]=next;}
   CHECK(global_projectile91_fade_step_valid(7));render_mirror_fade_step(7);
   CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_projectile91_used_members==statics_bit(statics_new[s]));
   for(unsigned i=0;i<10752;i++){Uint32 old=want[i],next=0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}want[i]=next;}
   statics_output_expected(want,110,80);global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==statics_bit(statics_new[s]));
   statics_asset(statics_new[s])->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);continue;
  }
  if(mode==0){statics_asset(statics_new[s])->rgba[100]^=1;CHECK(!global_projectile91_fade_step_valid(7));}
  if(mode==1)CHECK(!global_projectile91_fade_step_valid(0));
  if(mode==2){rgb_palette[200]^=1;CHECK(!global_projectile91_fade_step_valid(7));}
  CHECK(!ready&&!last_output_valid&&!have_fade_saved);
 }
}
/* No controlled animation/emission fixture: both selectors are static. Actual
 *260 multi2 allocation/scheduling belongs only to the separate natural replay. */
static void statics_group(const char *name,unsigned before,unsigned expected)
{CHECK(cases-before==expected);printf("STATICS_GROUP name=%s cases=%u\n",name,cases-before);}
static int statics_main(int argc,char **argv)
{
 CHECK(argc==3&&!strcmp(argv[1],"--enemy-statics"));
 for(unsigned i=0;i<sizeof(statics_root_names)/sizeof(*statics_root_names);i++){int n=snprintf(statics_roots[i],sizeof(statics_roots[i]),"%s/%s",argv[2],statics_root_names[i]);CHECK(n>0&&(size_t)n<sizeof(statics_roots[i]));}
 valid_root=statics_roots[0];missing_root=statics_roots[1];read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));
 Uint32 n;read_exact(&n,4);CHECK(n==33484);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);
 Uint32 xn;read_exact(&xn,4);CHECK(xn==32404);Uint8 *xb=malloc(xn);CHECK(xb);read_exact(xb,xn);CHECK(fgetc(stdin)==EOF);
 unsigned first_case=cases,first_check=checks,b;
 b=cases;statics_full();statics_group("full_tile_native_patterns",b,4);
 b=cases;statics_hd_underlay();statics_group("full_tile_hd_underlay",b,2);
 b=cases;statics_bounds();statics_group("bounds",b,22);
 b=cases;statics_pairs();statics_group("pair_orders_zero_isolation",b,34);
 b=cases;statics_all10_same_origin();statics_group("all10_same_origin_dependency",b,20);
 b=cases;statics_all10_sentinels();statics_group("all10_two_row_dependency",b,20);
 b=cases;statics_absence();statics_group("missing_bad",b,40);
 b=cases;statics_singletons();statics_group("singletons_oldonly",b,4);
 b=cases;statics_malformed();statics_group("malformed_headers_lengths",b,18);
 b=cases;statics_readiness();statics_group("readiness_root_epochs",b,4);
 b=cases;statics_unused();statics_group("unused_memory_payload_ready",b,8);
 b=cases;statics_palette_admission();statics_group("palette_admission_shared",b,24);
 b=cases;statics_palette_direct();statics_group("palette_direct_final_cache",b,38);
 b=cases;statics_palette_composite_preflight();statics_group("palette_composite_preflight",b,12);
 b=cases;statics_used_resource_direct();statics_group("used_resource_direct_final_cache",b,52);
 b=cases;statics_source_scope_direct(xb,xn);statics_group("source_scope_direct_final_cache",b,24);
 b=cases;statics_layout_direct();statics_group("layout_direct_final_cache",b,32);
 b=cases;statics_callbacks();statics_group("callbacks",b,12);
 b=cases;statics_cold_warm_scope(xb,xn);statics_group("cold_warm_scope",b,44);
 b=cases;statics_transfer();statics_group("Talon_transfer",b,4);
 b=cases;statics_talon_underlay();statics_group("Talon_underlay_direct",b,8);
 b=cases;statics_lifecycle();statics_group("lifecycle",b,7);
 b=cases;statics_later_writers();statics_group("later_native_final_writers",b,8);
 b=cases;statics_fades();statics_group("fade_high_bits",b,8);
 CHECK(cases>first_case&&checks>first_check);printf("PASS enemy statics native lifecycle: %u cases %u assertions; internal8 only; not gameplay/full build\n",cases-first_case,checks-first_check);free(xb);return 0;
}
