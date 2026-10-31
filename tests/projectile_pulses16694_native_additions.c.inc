/* SPDX-License-Identifier: GPL-2.0-or-later
 * PREPARED ONLY: independent enemy166/94 production-TU companion.
 * The inherited six sources, gold/statics bodies, wrappers and five stdout contracts are
 * not edited. This mode is controlled internal8, never gameplay/full-build proof.
 * Each setup is one case. Expectations below are fixed-byte predictions until
 * a separately authorized fresh native run establishes actual observations.
 */
static const unsigned pulses16694_ids[12]={91,145,61,101,120,139,168,169,162,260,166,94};
static const unsigned pulses16694_new[2]={166,94};
static const char *pulses16694_root_names[]={"valid","missing91","bad91","missing145","bad145","missing61","bad61","missing101","bad101","missing120","bad120","missing139","bad139","missing168","bad168","missing169","bad169","missing162","bad162","missing260","bad260","missing166","bad166","missing94","bad94","only166","only94","old-only","header166","short166","trailing166","header94","short94","trailing94","magic166","density166","width166","height166","anchorx166","anchory166","magic94","density94","width94","height94","anchorx94","anchory94"};
static char pulses16694_roots[sizeof(pulses16694_root_names)/sizeof(*pulses16694_root_names)][1200];
static unsigned pulses16694_bit(unsigned id)
{for(unsigned k=0;k<12;k++)if(pulses16694_ids[k]==id)return 1u<<k;return 0u;}
static bool pulses16694_is_new(unsigned id){return id==166||id==94;}
static Asset *pulses16694_asset(unsigned id)
{
 if(!pulses16694_is_new(id))return statics_asset(id);
 int slot=projectile_pulses16694_slot(id);CHECK(slot>=0&&slot<2);
 return &projectile_pulses16694_resources[slot].member;
}
static void pulses16694_setup(void){setup(3,1);}
static void pulses16694_draw(unsigned id,int x,int y){blue_draw_bank(id,x,y,spriteSheet8);}
/* Full-tile arithmetic is independent of the production blending function.
 * A native-covered authored-alpha0 pixel owns the genuine underlay, while
 * outside-native alpha0 never introduces new ownership. */
typedef struct {Uint32 canvas[10752],under[10752];Uint8 owned[10752],native[168];} PulsesBefore;
static void pulses16694_snapshot(PulsesBefore *b,int x,int y)
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
static void pulses16694_oracle(unsigned id,int x,int y,const PulsesBefore *b,bool final_output)
{
 const Uint8 *rgba=pulses16694_asset(id)->rgba;CHECK(rgba);Uint8 src[168],mask[168];blue_decode(id,src,mask);
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
 if(id==166)CHECK(cells==97&&soft==5788&&opaque==0&&clear==4964&&zero_native==420);
 if(id==94)CHECK(cells==108&&soft==6448&&opaque==40&&clear==4264&&zero_native==424);
 if(visible)CHECK(global_projectile91_used_members&pulses16694_bit(id));
}
static void pulses16694_callbacks_seen(unsigned id,int x,int y)
{
 Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned visible=0,seen=0;
 for(unsigned c=0;c<168;c++) {
  bool v=mask[c]&&x+(int)(c%12)>=0&&x+(int)(c%12)<320&&y+(int)(c/12)>=0&&y+(int)(c/12)<200;
  visible+=v;seen+=global_projectile91_call.seen[c]!=0;CHECK((global_projectile91_call.seen[c]!=0)==v);
 }
 CHECK(seen==visible&&!global_projectile91_call.left&&!global_projectile91_call.live);
 if(x==110&&y==80&&id==166)CHECK(seen==97);
 if(x==110&&y==80&&id==94)CHECK(seen==108);
}
static void pulses16694_valid(unsigned id,int x,int y,PulsesBefore *b)
{
 pulses16694_snapshot(b,x,y);pulses16694_draw(id,x,y);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
 CHECK(global_projectile91_used_members&pulses16694_bit(id));pulses16694_callbacks_seen(id,x,y);pulses16694_oracle(id,x,y,b,false);
}
static void pulses16694_expected(Uint32 *want,unsigned id,const PulsesBefore *b)
{
 Uint8 src[168],mask[168];blue_decode(id,src,mask);const Uint8 *rgba=pulses16694_asset(id)->rgba;
 for(unsigned i=0;i<10752;i++)want[i]=mask[(i/96/8)*12+(i%96)/8]?alpha(b->under[i],rgba+4*i):b->canvas[i];
}
static void pulses16694_output_expected(const Uint32 *want,int x,int y)
{
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  int px=x*8+ax,py=y*8+ay;if(px<192||px>=2304||py<0||py>=1472)continue;
  CHECK(*at(output,px-192,py)==want[ay*96+ax]);
 }
}
static void pulses16694_good_mask(unsigned bits)
{
 CHECK(!(bits&~4095u));
 for(unsigned k=0;k<12;k++)if(bits&(1u<<k)) {
  PulsesBefore b;pulses16694_valid(pulses16694_ids[k],40+40*(int)(k%6),60+40*(int)(k/6),&b);
 }
 CHECK(global_projectile91_used_members==bits&&!global_projectile91_fault);
}
static void pulses16694_full(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned pattern=0;pattern<2;pattern++) {
  pulses16694_setup();unsigned id=pulses16694_new[s];
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++)((Uint8 *)game_screen->pixels)[(80+y)*320+110+x]=(Uint8)(27+(pattern?16*((x+y)%3):0));
  render_mirror_begin();CHECK(!get_asset(spriteSheet8,id,ENTITY_TILE));blue_player_classic(id);
  PulsesBefore b;pulses16694_valid(id,110,80,&b);CHECK(global_projectile91_used_members==pulses16694_bit(id));
  Asset *a=pulses16694_asset(id);CHECK(a->initialized&&a->valid&&a->bank==155&&a->index==id&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y&&a->density==8);
  CHECK(asteroid1_stamp(a->rgba,43008)==(s?UINT64_C(0x131a3be7ed56665d):UINT64_C(0x80c10783a6cabbe2)));
  CHECK(projectile_pulses16694_resources[s].checked&&projectile_pulses16694_resources[s].valid&&!strcmp(projectile_pulses16694_resources[s].root,valid_root));
  CHECK(global_projectile91_member(id)==(s?2048u:1024u));
  finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);pulses16694_oracle(id,110,80,&b,true);
  global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==pulses16694_bit(id));pulses16694_oracle(id,110,80,&b,true);
 }
}
static void pulses16694_hd_underlay(void)
{
 for(unsigned s=0;s<2;s++) {
  pulses16694_setup();PulsesBefore before,last;pulses16694_valid(120,110,80,&before);pulses16694_valid(pulses16694_new[s],110,80,&last);
  unsigned zero=0;Uint8 src[168],mask[168];blue_decode(pulses16694_new[s],src,mask);const Uint8 *rgba=pulses16694_asset(pulses16694_new[s])->rgba;
  for(unsigned i=0;i<10752;i++)if(mask[(i/96/8)*12+(i%96)/8]&&!rgba[4*i+3]){CHECK(last.owned[i]&&last.under[i]==last.canvas[i]);++zero;}
  CHECK(zero==(s?424u:420u));finish();CHECK(ready&&last_output_valid);pulses16694_oracle(pulses16694_new[s],110,80,&last,true);
  global_projectile91_check_cache();CHECK(ready&&last_output_valid);pulses16694_oracle(pulses16694_new[s],110,80,&last,true);
 }
}
static void pulses16694_bounds(void)
{
 const int accept[][2]={{0,80},{308,80},{110,-13},{110,-6},{110,180},{110,190},{110,199}};
 const int reject[][2]={{-1,80},{309,80},{110,-14},{110,200}};
 for(unsigned s=0;s<2;s++) {
  for(unsigned k=0;k<7;k++) {
   pulses16694_setup();unsigned id=pulses16694_new[s];int x=accept[k][0],y=accept[k][1];Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned visible=0,output_visible=0;
   for(unsigned c=0;c<168;c++)if(mask[c]){int cx=x+(int)(c%12),cy=y+(int)(c/12);visible+=cy>=0&&cy<200;output_visible+=cx>=24&&cx<288&&cy>=0&&cy<184;}
   PulsesBefore b;pulses16694_snapshot(&b,x,y);pulses16694_draw(id,x,y);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
   pulses16694_callbacks_seen(id,x,y);CHECK(global_projectile91_used_members==(visible?pulses16694_bit(id):0u));pulses16694_oracle(id,x,y,&b,false);
   finish();if(output_visible){CHECK(ready&&last_output_valid);pulses16694_oracle(id,x,y,&b,true);global_projectile91_check_cache();CHECK(ready&&last_output_valid);pulses16694_oracle(id,x,y,&b,true);}else CHECK(!ready&&!last_output_valid);
  }
  for(unsigned k=0;k<4;k++){pulses16694_setup();pulses16694_draw(pulses16694_new[s],reject[k][0],reject[k][1]);CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);}
 }
}
static unsigned pulses16694_pair_intersection(unsigned a,unsigned b)
{
 static const unsigned counts[2][12]={{2991,1527,2405,5774,5788,5261,5131,3561,1392,4206,5788,4988},{3229,1762,2468,6488,6488,5644,4985,3550,1392,4776,4988,6488}};
 if(!pulses16694_is_new(a)){unsigned t=a;a=b;b=t;}CHECK(pulses16694_is_new(a));
 for(unsigned k=0;k<12;k++)if(pulses16694_ids[k]==b)return counts[a==94][k];CHECK(false);return 0;
}
static void pulses16694_pairs(void)
{
 /* Twenty new-vs-old pairs plus166/94, each in both orders. Original
  * statics zero-overlap cases remain untouched in their inherited process. */
 for(unsigned a=0;a<12;a++)for(unsigned b=a+1;b<12;b++)if(a>=10||b>=10)for(unsigned reverse=0;reverse<2;reverse++) {
  pulses16694_setup();unsigned first=pulses16694_ids[reverse?b:a],last=pulses16694_ids[reverse?a:b];PulsesBefore fb,lb;Uint32 want[10752];
  pulses16694_valid(first,110,80,&fb);CHECK(global_projectile91_used_members==pulses16694_bit(first));pulses16694_valid(last,110,80,&lb);pulses16694_expected(want,last,&lb);
  const Uint8 *one=pulses16694_asset(first)->rgba,*two=pulses16694_asset(last)->rgba;unsigned intersection=0;
  for(unsigned i=0;i<10752;i++)if(one[4*i+3]&&two[4*i+3]){CHECK(lb.owned[i]);++intersection;}
  CHECK(intersection==pulses16694_pair_intersection(first,last));CHECK(intersection>0);
  CHECK(global_projectile91_used_members==(pulses16694_bit(first)|pulses16694_bit(last)));
  finish();CHECK(ready&&last_output_valid);pulses16694_output_expected(want,110,80);
  global_projectile91_check_cache();CHECK(ready&&last_output_valid);pulses16694_output_expected(want,110,80);
  pulses16694_asset(first)->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
}
static void pulses16694_all12_same_origin(void)
{
 for(unsigned first=0;first<12;first++)for(unsigned cached=0;cached<2;cached++) {
  pulses16694_setup();PulsesBefore b;Uint32 want[10752];
  for(unsigned k=0;k<12;k++){pulses16694_valid(pulses16694_ids[(first+k)%12],110,80,&b);pulses16694_expected(want,pulses16694_ids[(first+k)%12],&b);}
  unsigned alpha_common=0,native_common=0;Uint8 masks[12][168],src[168];
  for(unsigned k=0;k<12;k++)blue_decode(pulses16694_ids[k],src,masks[k]);
  for(unsigned c=0;c<168;c++){bool all=true;for(unsigned k=0;k<12;k++)all=all&&masks[k][c];native_common+=all;}
  for(unsigned i=0;i<10752;i++){bool all=true;for(unsigned k=0;k<12;k++)all=all&&pulses16694_asset(pulses16694_ids[k])->rgba[4*i+3]!=0;alpha_common+=all;}
  CHECK(alpha_common==0&&native_common==0&&global_projectile91_used_members==4095u&&(global_projectile91_used_members&3072u)==3072u);
  if(cached){finish();CHECK(ready&&last_output_valid);pulses16694_output_expected(want,110,80);global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==4095u);pulses16694_output_expected(want,110,80);}
  pulses16694_asset(pulses16694_ids[first])->rgba[100]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void pulses16694_all12_sentinels(void)
{
 /* Fixed two-row layout; no extending the inherited clipped x40+28*k row. */
 for(unsigned damaged=0;damaged<12;damaged++)for(unsigned cached=0;cached<2;cached++) {
  pulses16694_setup();PulsesBefore b;Uint32 want[12][10752];
  for(unsigned k=0;k<12;k++){int x=40+40*(int)(k%6),y=60+40*(int)(k/6);pulses16694_valid(pulses16694_ids[k],x,y,&b);pulses16694_expected(want[k],pulses16694_ids[k],&b);}
  CHECK(global_projectile91_used_members==4095u);
  if(cached){finish();CHECK(ready&&last_output_valid);for(unsigned k=0;k<12;k++)pulses16694_output_expected(want[k],40+40*(int)(k%6),60+40*(int)(k/6));global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==4095u);for(unsigned k=0;k<12;k++)pulses16694_output_expected(want[k],40+40*(int)(k%6),60+40*(int)(k/6));}
  pulses16694_asset(pulses16694_ids[damaged])->rgba[100]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void pulses16694_absence(void)
{
 for(unsigned k=0;k<12;k++)for(unsigned bad=0;bad<2;bad++)for(unsigned warm=0;warm<2;warm++) {
  valid_root=pulses16694_roots[1+2*k+bad];pulses16694_setup();unsigned bits=4095u&~(1u<<k);
  if(warm)pulses16694_good_mask(bits);pulses16694_draw(pulses16694_ids[k],280,140);CHECK(!global_projectile91_fault);
  if(!warm){CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);pulses16694_good_mask(bits);}
  CHECK(global_projectile91_used_members==bits);blue_accept();
 }
 valid_root=pulses16694_roots[0];
}
static void pulses16694_singletons(void)
{
 for(unsigned s=0;s<2;s++) {
  valid_root=pulses16694_roots[25+s];pulses16694_setup();
  for(unsigned k=0;k<12;k++)pulses16694_draw(pulses16694_ids[k],40+40*(int)(k%6),60+40*(int)(k/6));
  CHECK(global_projectile91_used_members==pulses16694_bit(pulses16694_new[s])&&!global_projectile91_fault);blue_accept();
 }
 for(unsigned warm=0;warm<2;warm++) {
  valid_root=pulses16694_roots[27];pulses16694_setup();if(warm)pulses16694_good_mask(1023u);
  pulses16694_draw(166,240,140);pulses16694_draw(94,280,140);
  if(!warm){CHECK(!global_projectile91_used_members);pulses16694_good_mask(1023u);}
  CHECK(global_projectile91_used_members==1023u&&!global_projectile91_fault);blue_accept();
 }
 valid_root=pulses16694_roots[0];
}
static void pulses16694_malformed(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<9;mode++) {
  unsigned root=mode<3?28+3*s+mode:34+6*s+(mode-3);
  valid_root=pulses16694_roots[root];pulses16694_setup();unsigned id=pulses16694_new[s],bits=4095u&~pulses16694_bit(id);
  pulses16694_good_mask(bits);pulses16694_draw(id,280,140);
  CHECK(projectile_pulses16694_resources[s].checked&&!projectile_pulses16694_resources[s].valid);
  CHECK(global_projectile91_used_members==bits&&!global_projectile91_fault);blue_accept();
 }
 valid_root=pulses16694_roots[0];
}
static void pulses16694_readiness(void)
{
 for(unsigned s=0;s<2;s++) {
  valid_root=pulses16694_roots[21+2*s];pulses16694_setup();unsigned id=pulses16694_new[s];
  unsigned char before[sizeof(projectile_pulses16694_resources)];memcpy(before,projectile_pulses16694_resources,sizeof(before));
  CHECK(projectile_pulses16694_slot(0)<0&&!projectile_pulses16694_resource(valid_root,0)&&!projectile_pulses16694_source(spriteSheet8,0)&&!projectile_pulses16694_palette_matches(0));
  CHECK(!memcmp(before,projectile_pulses16694_resources,sizeof(before)));
  CHECK(!projectile_pulses16694_resource(valid_root,id));CHECK(projectile_pulses16694_resources[s].checked&&!projectile_pulses16694_resources[s].valid&&!projectile_pulses16694_resources[1-s].checked);
  CHECK(!strcmp(projectile_pulses16694_resources[s].root,valid_root));
  memcpy(before,projectile_pulses16694_resources,sizeof(before));CHECK(render_mirror_set_global_assets(valid_root));CHECK(!memcmp(before,projectile_pulses16694_resources,sizeof(before)));
  CHECK(!projectile_pulses16694_resource(valid_root,id)&&!projectile_pulses16694_resource(pulses16694_roots[0],id));
  CHECK(!memcmp(before,projectile_pulses16694_resources,sizeof(before))); /* No implicit retry/new epoch. */
  CHECK(projectile_pulses16694_resource(valid_root,pulses16694_new[1-s]));
  CHECK(render_mirror_set_global_assets(pulses16694_roots[0]));CHECK(!projectile_pulses16694_resources[0].checked&&!projectile_pulses16694_resources[1].checked);
  render_mirror_begin();PulsesBefore b;pulses16694_valid(id,110,80,&b);blue_accept();
  CHECK(global_projectile91_used_members==pulses16694_bit(id));
  projectile_pulses16694_shutdown();CHECK(!projectile_pulses16694_resources[0].checked&&!projectile_pulses16694_resources[1].checked);
  CHECK(projectile_pulses16694_resource(pulses16694_roots[0],id));
 }
 valid_root=pulses16694_roots[0];
 for(unsigned s=0;s<2;s++) {
  pulses16694_setup();char longroot[1025];memset(longroot,'x',sizeof(longroot)-1);longroot[sizeof(longroot)-1]='\0';
  CHECK(!projectile_pulses16694_resource(NULL,pulses16694_new[s])&&!projectile_pulses16694_resource("",pulses16694_new[s])&&!projectile_pulses16694_resource(longroot,pulses16694_new[s]));
  CHECK(!projectile_pulses16694_resources[0].checked&&!projectile_pulses16694_resources[1].checked);
 }
}
static void pulses16694_unused(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<2;mode++)for(unsigned warm=0;warm<2;warm++) {
  pulses16694_setup();unsigned id=pulses16694_new[s],bits=4095u&~pulses16694_bit(id);PulsesBefore b;pulses16694_valid(id,110,80,&b);blue_accept();
  render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached);
  if(warm)pulses16694_good_mask(bits);if(mode)pulses16694_asset(id)->valid=false;else pulses16694_asset(id)->rgba[100]^=1;
  if(!warm)pulses16694_good_mask(bits);pulses16694_draw(id,280,140);
  CHECK(global_projectile91_used_members==bits&&!global_projectile91_fault);blue_accept();
 }
}
static const unsigned pulses16694_colors[30]={33,114,115,116,117,119,120,121,122,123,124,125,126,127,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159};
static const unsigned pulses16694_color_bits[30]={1024u,2052u,2052u,2564u,2564u,2564u,2564u,2564u,2820u,3012u,2756u,3008u,3008u,2496u,1056u,1080u,1064u,1064u,1064u,1080u,1064u,1064u,1064u,1080u,1064u,1064u,1080u,1064u,1056u,1080u};
static void pulses16694_palette_admission(void)
{
 /* Shared61/gold colors are real dependencies. Never label one as unused
  * after an affected member or a foreign-HD underlay has contributed. */
 for(unsigned c=0;c<30;c++)for(unsigned warm=0;warm<2;warm++) {
  pulses16694_setup();unsigned good=4095u&~pulses16694_color_bits[c];
  if(warm)pulses16694_good_mask(good);CHECK(!global_projectile91_used_colors[pulses16694_colors[c]]);
  rgb_palette[pulses16694_colors[c]]^=1;
  for(unsigned k=0;k<12;k++)if(pulses16694_color_bits[c]&(1u<<k))pulses16694_draw(pulses16694_ids[k],280,140);
  if(!warm){CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);pulses16694_good_mask(good);}
  CHECK(global_projectile91_used_members==good&&!global_projectile91_fault);blue_accept();
 }
}
static void pulses16694_palette_direct(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned c=0;c<30;c++)if(pulses16694_color_bits[c]&pulses16694_bit(pulses16694_new[s]))for(unsigned cached=0;cached<2;cached++) {
  pulses16694_setup();PulsesBefore b;unsigned id=pulses16694_new[s];pulses16694_valid(id,110,80,&b);if(cached)blue_accept();
  rgb_palette[pulses16694_colors[c]]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned s=0;s<2;s++)for(unsigned cached=0;cached<2;cached++) {
  pulses16694_setup();SDL_FillRect(game_screen,NULL,200);render_mirror_begin();PulsesBefore b;pulses16694_valid(pulses16694_new[s],110,80,&b);
  CHECK(global_projectile91_used_colors[200]);if(cached)blue_accept();rgb_palette[200]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned s=0;s<2;s++) {
  pulses16694_setup();PulsesBefore b;pulses16694_valid(pulses16694_new[s],110,80,&b);CHECK(!global_projectile91_used_colors[200]);blue_accept();
  rgb_palette[200]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid); /* Whole output palette cache, not member isolation. */
 }
}
static void pulses16694_palette_composite_preflight(void)
{
 for(unsigned c=1;c<30;c++) {
  unsigned k=0;while(k<10&&!(pulses16694_color_bits[c]&(1u<<k)))++k;CHECK(k<10);
  pulses16694_setup();unsigned first=pulses16694_ids[k];PulsesBefore b;pulses16694_valid(first,110,80,&b);
  CHECK(pulses16694_color_bits[c]&pulses16694_bit(first));rgb_palette[pulses16694_colors[c]]^=1;
  pulses16694_draw(166,240,140);pulses16694_draw(94,280,140);CHECK(global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);
 }
}
static void pulses16694_used_resource_direct(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<13;mode++)for(unsigned cached=0;cached<2;cached++) {
  pulses16694_setup();unsigned id=pulses16694_new[s];PulsesBefore b;pulses16694_valid(id,110,80,&b);if(cached)blue_accept();
  Asset *a=pulses16694_asset(id);Uint8 *saved=a->rgba;
  switch(mode){case 0:a->rgba[100]^=1;break;case 1:a->initialized=false;break;case 2:a->valid=false;break;case 3:a->bank=ASSET_ENEMY_GOLD_PULSE;break;case 4:a->index=pulses16694_new[1-s];break;case 5:a->w=11;break;case 6:a->h=13;break;case 7:a->anchor_x=1;break;case 8:a->anchor_y=1;break;case 9:a->density=4;break;case 10:a->rgba=NULL;break;case 11:projectile_pulses16694_resources[s].valid=false;break;case 12:projectile_pulses16694_resources[s].root[0]^=1;break;}
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);if(mode==10)a->rgba=saved;
 }
}
static void pulses16694_source_scope_direct(const Uint8 *xb,size_t xn)
{
 for(unsigned mode=0;mode<12;mode++)for(unsigned cached=0;cached<2;cached++) {
  pulses16694_setup();PulsesBefore b[2];pulses16694_valid(166,80,80,&b[0]);pulses16694_valid(94,140,80,&b[1]);CHECK(global_projectile91_used_members==3072u);if(cached)blue_accept();
  switch(mode){case 0:livebank[100]^=1;break;case 1:livebank[0]^=1;break;case 2:spriteSheet8.size--;break;case 3:spriteSheet8.data=NULL;break;case 4:xmas=true;break;case 5:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};break;case 6:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};xmas=true;break;case 7:spriteSheet12=spriteSheet8;break;case 8:game_probe_original_reference=true;break;case 9:game_probe_missing=true;break;case 10:game_probe_invalid=true;break;case 11:game_probe_density=4;break;}
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);if(mode==11)game_probe_density=8;
 }
}
static void pulses16694_layout_direct(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<8;mode++)for(unsigned cached=0;cached<2;cached++) {
  pulses16694_setup();PulsesBefore b;pulses16694_valid(pulses16694_new[s],110,80,&b);if(cached)blue_accept();
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
static void pulses16694_callbacks(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<6;mode++) {
  pulses16694_setup();unsigned id=pulses16694_new[s];CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,id));
  CHECK(global_projectile91_used_members==pulses16694_bit(id)&&global_projectile91_call.live&&global_projectile91_call.left==(s?108u:97u));
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
static void pulses16694_transfer(void)
{
 const unsigned expected[2]={1176,1081},soft_expected[2]={1176,1081},zeros[2]={133,56},wx[2]={56,56},wy[2]={8,16};
 const Uint8 witness[2][4]={{0,0,255,1},{248,121,15,84}};
 const Uint32 witness_rgb[2]={0xffa99166u,0xffc48a49u};
 for(unsigned s=0;s<2;s++)for(unsigned cached=0;cached<2;cached++) {
  pulses16694_setup();unsigned id=pulses16694_new[s];PulsesBefore b;pulses16694_valid(id,110,80,&b);CHECK(global_projectile91_used_members==pulses16694_bit(id));
  Uint8 prior[10752],zero[10752];Uint8 src[168],mask[168];blue_decode(id,src,mask);const Uint8 *rgba=pulses16694_asset(id)->rgba;
  for(unsigned i=0;i<10752;i++){size_t n=(size_t)(640+i/96)*2560+880+i%96;bool owned=global_projectile91_owner[n]!=0;prior[i]=owned&&rgba[4*i+3]>0;zero[i]=owned&&mask[(i/96/8)*12+(i%96)/8]&&rgba[4*i+3]==0;}
  unsigned wi=wy[s]*96+wx[s];CHECK(!memcmp(rgba+4*wi,witness[s],4));Uint32 want=alpha(palette_rgb(0x1b),witness[s]);CHECK(want==witness_rgb[s]);
  int px=880+(int)wx[s],py=640+(int)wy[s];CHECK(*at(canvas,px,py)==want);
  SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
  uint64_t rng=mt_state_fingerprint();Uint32 pal[256];JE_MultiEnemyType actors;EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(pal,rgb_palette,sizeof(pal));memcpy(actors,enemy,sizeof(enemy));memcpy(shots,enemyShot,sizeof(shots));
  /* Fixed geometry derived from new pinned bytes before native execution.
   * Talon is binary-alpha: pulses16694 soft RGB transfers through Talon native-alpha0. */
  blit_sprite2x2(classic,107,78,spriteSheet9,233);global_talon_pose(1,spriteSheet9,233,233,0);CHECK(global_talon_poses[0].visual==6);
  CHECK(render_mirror_global_player_ship(game_screen,107,78,spriteSheet9,233,MIRROR_NORMAL,1,233)==1);
  unsigned tx=wx[s]+24,ty=wy[s]+16;CHECK(global_talon_call.mask[(ty/8)*24+tx/8]&&global_talon_rgba[6][4*(ty*192+tx)+3]==0);
  blit_sprite2x2(game_screen,107,78,spriteSheet9,233);render_mirror_entity_end();CHECK(global_talon_contributed&&!global_talon_fault);
  CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(rng==mt_state_fingerprint());CHECK(!memcmp(pal,rgb_palette,sizeof(pal)));CHECK(!memcmp(actors,enemy,sizeof(enemy))&&!memcmp(shots,enemyShot,sizeof(shots)));SDL_FreeSurface(classic);
  unsigned copied=0,soft=0,az=0,transferred=0;for(unsigned i=0;i<10752;i++){size_t n=(size_t)(640+i/96)*2560+880+i%96;bool transfer=!global_projectile91_owner[n]&&global_talon_owner[n]&&global_talon_foreign[n];transferred+=transfer;if(prior[i]&&transfer){++copied;soft+=rgba[4*i+3]<255;}if(zero[i]&&transfer)++az;}
  CHECK(copied>0&&copied==expected[s]&&soft==soft_expected[s]&&az==zeros[s]&&transferred==copied+az);size_t wn=(size_t)py*2560+px;CHECK(!global_projectile91_owner[wn]&&global_talon_owner[wn]&&global_talon_foreign[wn]);CHECK(*at(canvas,px,py)==want);
  CHECK(global_projectile91_contributed&&global_projectile91_used_members==pulses16694_bit(id)&&!global_projectile91_fault);
  printf("PULSES16694_TO_TALON selector=%u copied=%u soft=%u alpha0=%u cached=%u\n",id,copied,soft,az,cached);
  if(cached){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_projectile91_used_members==pulses16694_bit(id));CHECK(*at(output,px-24*8,py)==want);global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==pulses16694_bit(id));CHECK(*at(output,px-24*8,py)==want);}
  pulses16694_asset(id)->rgba[100]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void pulses16694_talon_underlay(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<2;mode++)for(unsigned cached=0;cached<2;cached++) {
  pulses16694_setup();talon_tile();PulsesBefore b;Uint8 src[168],mask[168];blue_decode(pulses16694_new[s],src,mask);unsigned overlap=0;Uint8 talon_before[10752];for(unsigned i=0;i<10752;i++)talon_before[i]=global_talon_owner[(size_t)(640+i/96)*2560+880+i%96]!=0;
  for(unsigned i=0;i<10752;i++)if(mask[(i/96/8)*12+(i%96)/8])overlap+=global_talon_owner[(size_t)(640+i/96)*2560+880+i%96]!=0;
  CHECK(overlap==(s?3520u:3200u));pulses16694_valid(pulses16694_new[s],110,80,&b);CHECK(global_projectile91_talon_dependency&&global_projectile91_used_colors[200]);
  unsigned sf=0,az=0,op=0;const Uint8 *q=pulses16694_asset(pulses16694_new[s])->rgba;
  for(unsigned i=0;i<10752;i++)if(mask[(i/96/8)*12+(i%96)/8]){size_t p=(size_t)(640+i/96)*2560+880+i%96;
   if(global_projectile91_foreign[p]){sf+=q[4*i+3]>0;az+=q[4*i+3]==0;CHECK(q[4*i+3]<255);}else if(q[4*i+3]==255)op++;}
  CHECK(sf==(s?3255u:2966u)&&az==(s?248u:234u));CHECK(op==(s?40u:0u));unsigned clears=0;for(unsigned i=0;i<10752;i++)if(talon_before[i]&&mask[(i/96/8)*12+(i%96)/8]&&q[4*i+3]==255){CHECK(!global_projectile91_foreign[(size_t)(640+i/96)*2560+880+i%96]);++clears;}CHECK(clears==(s?17u:0u));
  if(cached){finish();CHECK(ready&&last_output_valid);pulses16694_oracle(pulses16694_new[s],110,80,&b,true);global_projectile91_check_cache();CHECK(ready&&last_output_valid);pulses16694_oracle(pulses16694_new[s],110,80,&b,true);}
  size_t saved=spriteSheet9.size;if(mode)spriteSheet9.size--;else rgb_palette[200]^=1;
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);spriteSheet9.size=saved;
 }
}
static void pulses16694_cold_warm_scope(const Uint8 *xb,size_t xn)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<11;mode++)for(unsigned warm=0;warm<2;warm++) {
  pulses16694_setup();unsigned id=pulses16694_new[s];Uint8 foreign[32060];memcpy(foreign,original,sizeof(foreign));Sprite2_array bank=spriteSheet8;
  /* Both selected Christmas shapes differ; normal whole-bank guard is required. */
  Uint8 ns[168]={0},nm[168]={0},xs[168]={0},xm[168]={0};CHECK(decode_tile(spriteSheet8,id,ns,nm,12,0,0));CHECK(decode_tile((Sprite2_array){xn,(Uint8 *)xb},id,xs,xm,12,0,0));CHECK(memcmp(ns,xs,168)&&memcmp(nm,xm,168));
  if(warm){PulsesBefore b;pulses16694_valid(91,40,60,&b);}
  switch(mode){case 0:xmas=true;break;case 1:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};bank=spriteSheet8;break;case 2:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};bank=spriteSheet8;xmas=true;break;case 3:game_probe_density=4;break;case 4:bank=(Sprite2_array){sizeof(foreign),foreign};break;case 5:spriteSheet12=spriteSheet8;break;case 6:bank.size--;break;case 7:bank.data=NULL;break;case 8:game_probe_original_reference=true;break;case 9:game_probe_missing=true;break;case 10:game_probe_invalid=true;break;}
  CHECK(!render_mirror_enemy_shot(game_screen,110,80,bank,id));CHECK(!global_projectile91_call.live);
  if(mode==3)game_probe_density=8;
  if(warm&&(mode==4||mode==6||mode==7)){CHECK(global_projectile91_used_members==1u&&!global_projectile91_fault);blue_accept();}
  else{if(warm)CHECK(global_projectile91_fault);else CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);finish();CHECK(!ready&&!last_output_valid);}
 }
}
static void pulses16694_lifecycle(void)
{
 for(unsigned s=0;s<2;s++) {
  pulses16694_setup();PulsesBefore b;unsigned id=pulses16694_new[s];pulses16694_valid(id,110,80,&b);blue_accept();render_mirror_begin();
  CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached);
  pulses16694_good_mask(1023u);CHECK(!(global_projectile91_used_members&3072u));blue_accept();render_mirror_global_reset();
  CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid&&!active);
  pulses16694_setup();pulses16694_valid(id,110,80,&b);blue_accept();CHECK(render_mirror_set_global_assets(pulses16694_roots[21+2*s]));
  CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
  render_mirror_begin();pulses16694_draw(id,280,140);CHECK(!global_projectile91_used_members&&!global_projectile91_fault);pulses16694_good_mask(1u);blue_accept();
  CHECK(render_mirror_set_global_assets(pulses16694_roots[0]));render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);pulses16694_valid(id,110,80,&b);blue_accept();
  CHECK(render_mirror_set_global_assets(""));CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!ready&&!last_output_valid);
 }
 pulses16694_setup();pulses16694_good_mask(4095u);blue_accept();render_mirror_hud_shutdown();
 CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_cached&&!global_projectile91_owner&&!global_projectile91_foreign&&!ready&&!last_output_valid);
 CHECK(!projectile_pulses16694_resources[0].checked&&!projectile_pulses16694_resources[1].checked);
 pulses16694_setup();pulses16694_good_mask(4095u);blue_accept();livebank[100]^=1;render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);
 for(unsigned k=0;k<12;k++)pulses16694_draw(pulses16694_ids[k],40+40*(int)(k%6),60+40*(int)(k/6));finish();CHECK(!ready&&!last_output_valid);
 pulses16694_setup();CHECK(render_mirror_set_global_assets(""));render_mirror_begin();pulses16694_draw(166,110,80);pulses16694_draw(94,160,80);
 CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);finish();CHECK(!ready&&!last_output_valid);
}
static void pulses16694_later_writers(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<4;mode++) {
  pulses16694_setup();unsigned id=pulses16694_new[s];PulsesBefore b;pulses16694_valid(id,110,80,&b);Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned c=0;while(c<168&&!mask[c])++c;CHECK(c<168);
  int x=110+(int)(c%12),y=80+(int)(c/12);Uint8 *p;
  if(mode==0){p=(Uint8 *)game_screen->pixels+y*320+x;*p=58;render_mirror_pixel(game_screen,p,src[c],MIRROR_NORMAL);finish();}
  else{blue_accept();if(mode==3){
   /* Revoke every owned native cell by legitimate final writes, never by
    * clearing a private owner array. Provenance must outlive all pixel owners. */
   for(unsigned j=0;j<168;j++)if(mask[j]){int xx=110+(int)(j%12),yy=80+(int)(j/12);p=(Uint8 *)VGAScreenSeg->pixels+yy*320+xx-24;*p=58;render_mirror_pixel(VGAScreenSeg,p,src[j],MIRROR_NORMAL);}
   for(unsigned i=0;i<10752;i++)CHECK(!global_projectile91_owner[(size_t)(640+i/96)*2560+880+i%96]);
  }else{p=(Uint8 *)VGAScreenSeg->pixels+y*320+x-24;*p=58;if(mode==1)render_mirror_pixel(VGAScreenSeg,p,src[c],MIRROR_NORMAL);else{SDL_Rect r={x-24,y,1,1};render_mirror_rect(VGAScreenSeg,&r);}}}
  CHECK(ready&&last_output_valid&&global_projectile91_contributed&&global_projectile91_used_members==pulses16694_bit(id));
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){size_t n=(size_t)(y*8+sy)*2560+x*8+sx;CHECK(!global_projectile91_owner[n]&&!global_projectile91_foreign[n]);CHECK(*at(output,(x-24)*8+sx,y*8+sy)==palette_rgb(58));}
  global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==pulses16694_bit(id));
  pulses16694_asset(id)->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
}
static void pulses16694_fades(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<4;mode++) {
  pulses16694_setup();PulsesBefore b;pulses16694_valid(pulses16694_new[s],110,80,&b);blue_accept();Uint32 want[10752];pulses16694_expected(want,pulses16694_new[s],&b);SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);
  CHECK(global_projectile91_cached&&have_fade_saved&&last_output_valid); /* This valid controlled fixture must exercise, not skip, the fade lease. */
  CHECK(have_fade_saved&&global_projectile91_used_members==pulses16694_bit(pulses16694_new[s]));
  if(mode==3){
   /* Real positive integer palette step; no float/rounded substitute. */
   for(unsigned i=0;i<256;i++){Uint32 old=rgb_palette[i],next=old&0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}rgb_palette[i]=next;}
   CHECK(global_projectile91_fade_step_valid(7));render_mirror_fade_step(7);
   CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_projectile91_used_members==pulses16694_bit(pulses16694_new[s]));
   for(unsigned i=0;i<10752;i++){Uint32 old=want[i],next=0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}want[i]=next;}
   pulses16694_output_expected(want,110,80);global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==pulses16694_bit(pulses16694_new[s]));
   pulses16694_asset(pulses16694_new[s])->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);continue;
  }
  if(mode==0){pulses16694_asset(pulses16694_new[s])->rgba[100]^=1;CHECK(!global_projectile91_fade_step_valid(7));}
  if(mode==1)CHECK(!global_projectile91_fade_step_valid(0));
  if(mode==2){rgb_palette[200]^=1;CHECK(!global_projectile91_fade_step_valid(7));}
  CHECK(!ready&&!last_output_valid&&!have_fade_saved);
 }
}
/* Static resources only; this controlled mode does not simulate natural emission. */
/* Explicit classic player main/shadow and generic wrappers, cold, warm, and
 * inverse order. Selector166's option25/weapon719 numeric alias is not an enemy
 * role grant. This invokes the real player wrapper, not a fabricated weapon. */
static void pulses16694_player_aliases(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned warm=0;warm<2;warm++)for(unsigned inverse=0;inverse<2;inverse++) {
  pulses16694_setup();unsigned id=pulses16694_new[s];PulsesBefore b;
  if(warm)pulses16694_valid(id,110,80,&b);
  unsigned bits=global_projectile91_used_members;bool contributed=global_projectile91_contributed;
  bool checked[2]={projectile_pulses16694_resources[0].checked,projectile_pulses16694_resources[1].checked};
  SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
  uint64_t rng=mt_state_fingerprint();Uint32 pal[256];JE_MultiEnemyType actors;EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(pal,rgb_palette,sizeof(pal));memcpy(actors,enemy,sizeof(enemy));memcpy(shots,enemyShot,sizeof(shots));
  for(unsigned j=0;j<2;j++) {
   unsigned style=(j+inverse)%2;
   if(style){blit_sprite2_darken(classic,40,80,spriteSheet8,id);draw_player_shot_shadow_sprite2(game_screen,40,80,spriteSheet8,id,0,id);}
   else{blit_sprite2(classic,40,80,spriteSheet8,id);draw_player_shot_sprite2(game_screen,40,80,spriteSheet8,id,0,id);}
   CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(global_projectile91_used_members==bits&&global_projectile91_contributed==contributed&&!global_projectile91_call.live);
   for(unsigned k=0;k<2;k++)CHECK(projectile_pulses16694_resources[k].checked==checked[k]);
  }
  CHECK(!get_asset(spriteSheet8,id,ENTITY_TILE));blit_sprite2(classic,60,80,spriteSheet8,id);draw_entity_sprite2(game_screen,60,80,spriteSheet8,id,ENTITY_NORMAL,ENTITY_TILE);
  CHECK(!memcmp(classic->pixels,game_screen->pixels,64000)&&rng==mt_state_fingerprint());CHECK(!memcmp(pal,rgb_palette,sizeof(pal))&&!memcmp(actors,enemy,sizeof(enemy))&&!memcmp(shots,enemyShot,sizeof(shots)));
  CHECK(global_projectile91_used_members==bits&&global_projectile91_contributed==contributed&&!global_projectile91_fault);SDL_FreeSurface(classic);
  if(!warm)pulses16694_valid(id,110,80,&b);finish();CHECK(ready&&last_output_valid&&global_projectile91_used_members==pulses16694_bit(id));pulses16694_oracle(id,110,80,&b,true);
 }
}
static void pulses16694_all12_fades(void)
{
 for(unsigned mode=0;mode<4;mode++) {
  pulses16694_setup();PulsesBefore b;Uint32 want[12][10752];
  for(unsigned k=0;k<12;k++){int x=40+40*(int)(k%6),y=60+40*(int)(k/6);pulses16694_valid(pulses16694_ids[k],x,y,&b);pulses16694_expected(want[k],pulses16694_ids[k],&b);}
  CHECK(global_projectile91_used_members==4095u);blue_accept();SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);
  CHECK(have_fade_saved&&global_projectile91_cached&&global_projectile91_used_members==4095u);
  if(mode<2){pulses16694_asset(pulses16694_new[mode])->rgba[100]^=1;CHECK(!global_projectile91_fade_step_valid(7));CHECK(!ready&&!last_output_valid&&!have_fade_saved);continue;}
  if(mode==2){SDL_Surface *saved=fade_saved;fade_saved=NULL;CHECK(!global_projectile91_fade_step_valid(7));CHECK(!ready&&!last_output_valid&&!have_fade_saved);fade_saved=saved;continue;}
  for(unsigned i=0;i<256;i++){Uint32 old=rgb_palette[i],next=old&0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}rgb_palette[i]=next;}
  CHECK(global_projectile91_fade_step_valid(7));render_mirror_fade_step(7);CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_projectile91_used_members==4095u);
  for(unsigned k=0;k<12;k++){for(unsigned i=0;i<10752;i++){Uint32 old=want[k][i],next=0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}want[k][i]=next;}pulses16694_output_expected(want[k],40+40*(int)(k%6),60+40*(int)(k/6));}
  global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==4095u);render_mirror_begin();CHECK(!global_projectile91_used_members&&!global_projectile91_cached);
 }
}
/* Controlled INTERNAL FontScene guard-state fixture; no font API draw/glyph,
 * natural scene grant, altered production predicate, or direct reject assignment.
 * Context1 isolates existing E1 manual-scope eligibility;0/2 retain E4 rejection.
 * Complete actual Talon owner is sampled (native OR authored alpha support). */
static void pulses16694_legacy_final(void)
{
 const unsigned kept_mixed[2]={3008,3409},dropped_mixed[2]={3200,3503};
 const char *reasons[3]={"normal15-output-scope","normal15-scene-font","normal15-output-scope|normal15-scene-font"};
 for(unsigned context=0;context<3;context++)for(unsigned s=0;s<2;s++)for(unsigned mixed=0;mixed<2;mixed++) {
  pulses16694_setup();unsigned id=pulses16694_new[s];
  JE_shortint old_initial=initialDifficulty;JE_byte old_arcade=superArcadeMode;char old_terrain=terrain_file;
  bool modes[]={isNetworkGame,twoPlayerMode,galagaMode,play_demo,record_demo,onePlayerAction,superTyrian,timedBattleMode,bonusLevel,normalBonusLevelCurrent,bonusLevelCurrent};
  isNetworkGame=twoPlayerMode=galagaMode=play_demo=record_demo=onePlayerAction=superTyrian=timedBattleMode=bonusLevel=normalBonusLevelCurrent=bonusLevelCurrent=false;superArcadeMode=SA_NONE;
  episodeNum=context==1?1:4;lvlFileNum=15;initialDifficulty=context==1?DIFFICULTY_NORMAL+1:0;terrain_file='z';manual_hd_enabled=manual_hd_lease=context==1;game_probe_enabled=true;
  render_mirror_begin();CHECK(active&&mirror_enabled()&&global_projectile91_frame&&normal15_palette());CHECK(normal15_scope()==(context==1));CHECK(!reject_reason&&!all_rejections[0]);
  if(context!=0){CHECK(font_allocate());font_context=-1;font_gameplay=false;font_suspended=false;font_density=8;
   FontScene *r=&font_scenes[0];r->rect=(SDL_Rect){0,0,0,0};r->surface=game_screen;r->pixels=game_screen->pixels;r->format=game_screen->format;r->pitch=game_screen->pitch;r->used=0;r->canvas_live=true;r->output_live=false;
   CHECK(font_history&&r->canvas_live&&!font_scene_owned(r,font_owner));}
  if(mixed)talon_tile();Uint8 prior_talon[10752];for(unsigned i=0;i<10752;i++)prior_talon[i]=mixed&&global_talon_owner[(size_t)(640+i/96)*2560+880+i%96];
  PulsesBefore b;pulses16694_valid(id,110,80,&b);const Uint8 *q=pulses16694_asset(id)->rgba;Uint8 src[168],mask[168];blue_decode(id,src,mask);Uint32 wanted[10752];pulses16694_expected(wanted,id,&b);
  unsigned kept=0,dropped=0,clears=0,kept_diff=0,dropped_diff=0;Uint8 foreign[10752];
  for(unsigned i=0;i<10752;i++){size_t n=(size_t)(640+i/96)*2560+880+i%96;bool native=mask[(i/96/8)*12+(i%96)/8];foreign[i]=native&&global_projectile91_foreign[n];if(!native)continue;
   CHECK(global_projectile91_owner[n]==1&&global_projectile91_foreign[n]<=1);CHECK(foreign[i]==(prior_talon[i]&&q[4*i+3]<255));clears+=prior_talon[i]&&q[4*i+3]==255;
   Uint32 classic=palette_rgb(src[(i/96/8)*12+(i%96)/8]);if(foreign[i]){++dropped;dropped_diff+=wanted[i]!=classic;}else{++kept;kept_diff+=wanted[i]!=classic;}}
  CHECK(kept==(mixed?kept_mixed[s]:(s?6912u:6208u))&&dropped==(mixed?dropped_mixed[s]:0u));CHECK(clears==(mixed&&s?17u:0u));CHECK(kept_diff==kept&&dropped_diff==dropped);
  Uint8 native_before[64000];memcpy(native_before,game_screen->pixels,64000);uint64_t rng=mt_state_fingerprint();Uint32 pal[256];JE_MultiEnemyType actors;EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(pal,rgb_palette,sizeof(pal));memcpy(actors,enemy,sizeof(enemy));memcpy(shots,enemyShot,sizeof(shots));
  finish();CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_projectile91_used_members==pulses16694_bit(id));CHECK(reject_reason&&!strcmp(all_rejections,reasons[context]));
  CHECK(!strcmp(reject_reason,context==1?"normal15-scene-font":"normal15-output-scope"));
  CHECK(!memcmp(native_before,game_screen->pixels,64000)&&rng==mt_state_fingerprint());CHECK(!memcmp(pal,rgb_palette,sizeof(pal))&&!memcmp(actors,enemy,sizeof(enemy))&&!memcmp(shots,enemyShot,sizeof(shots)));
  for(unsigned pass=0;pass<2;pass++) {
   if(pass){global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_projectile91_used_members==pulses16694_bit(id));}
   for(unsigned i=0;i<10752;i++){unsigned cell=(i/96/8)*12+(i%96)/8;size_t n=(size_t)(640+i/96)*2560+880+i%96;Uint32 classic=palette_rgb(native_before[(80+i/96/8)*320+110+i%96/8]);
    Uint32 want=mask[cell]?(foreign[i]?classic:wanted[i]):(prior_talon[i]?b.canvas[i]:classic);
    CHECK(*at(output,880+(int)(i%96)-192,640+(int)(i/96))==want);
    if(mask[cell])CHECK(global_projectile91_owner[n]==!foreign[i]);
   }
   if(mixed&&s){CHECK(*at(output,880+56-192,640+24)==UINT32_C(0xff860400));CHECK(*at(canvas,880+56,640+24)==UINT32_C(0xffbe1b01));CHECK(*at(output,880+85-192,640+61)==UINT32_C(0xffff9a1e));}
   if(mixed&&!s){CHECK(*at(output,880+64-192,640+8)==UINT32_C(0xff000051));CHECK(*at(canvas,880+64,640+8)==UINT32_C(0xffaa9265));}
  }
  printf("PULSES16694_LEGACY context=%u selector=%u mixed=%u kept=%u dropped=%u opaque_clears=%u\n",context,id,mixed,kept,dropped,clears);
  pulses16694_asset(id)->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
  initialDifficulty=old_initial;superArcadeMode=old_arcade;terrain_file=old_terrain;
  isNetworkGame=modes[0];twoPlayerMode=modes[1];galagaMode=modes[2];play_demo=modes[3];record_demo=modes[4];onePlayerAction=modes[5];superTyrian=modes[6];timedBattleMode=modes[7];bonusLevel=modes[8];normalBonusLevelCurrent=modes[9];bonusLevelCurrent=modes[10];
 }
}

static void pulses16694_group(const char *name,unsigned before,unsigned expected)
{CHECK(cases-before==expected);printf("PULSES16694_GROUP name=%s cases=%u\n",name,cases-before);}
static int pulses16694_main(int argc,char **argv)
{
 CHECK(argc==3&&!strcmp(argv[1],"--enemy-pulses16694"));
 for(unsigned i=0;i<sizeof(pulses16694_root_names)/sizeof(*pulses16694_root_names);i++){int n=snprintf(pulses16694_roots[i],sizeof(pulses16694_roots[i]),"%s/%s",argv[2],pulses16694_root_names[i]);CHECK(n>0&&(size_t)n<sizeof(pulses16694_roots[i]));}
 valid_root=pulses16694_roots[0];missing_root=pulses16694_roots[1];read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));
 Uint32 n;read_exact(&n,4);CHECK(n==33484);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);
 Uint32 xn;read_exact(&xn,4);CHECK(xn==32404);Uint8 *xb=malloc(xn);CHECK(xb);read_exact(xb,xn);CHECK(fgetc(stdin)==EOF);
 unsigned first_case=cases,first_check=checks,b;
 b=cases;pulses16694_full();pulses16694_group("full_tile_native_patterns",b,4);
 b=cases;pulses16694_hd_underlay();pulses16694_group("full_tile_hd_underlay",b,2);
 b=cases;pulses16694_bounds();pulses16694_group("bounds",b,22);
 b=cases;pulses16694_pairs();pulses16694_group("pair_orders_zero_isolation",b,42);
 b=cases;pulses16694_all12_same_origin();pulses16694_group("all12_same_origin_dependency",b,24);
 b=cases;pulses16694_all12_sentinels();pulses16694_group("all12_two_row_dependency",b,24);
 b=cases;pulses16694_absence();pulses16694_group("missing_bad",b,48);
 b=cases;pulses16694_singletons();pulses16694_group("singletons_oldonly",b,4);
 b=cases;pulses16694_malformed();pulses16694_group("malformed_headers_lengths",b,18);
 b=cases;pulses16694_readiness();pulses16694_group("readiness_root_epochs",b,4);
 b=cases;pulses16694_unused();pulses16694_group("unused_memory_payload_ready",b,8);
 b=cases;pulses16694_palette_admission();pulses16694_group("palette_admission_shared",b,60);
 b=cases;pulses16694_palette_direct();pulses16694_group("palette_direct_final_cache",b,66);
 b=cases;pulses16694_palette_composite_preflight();pulses16694_group("palette_composite_preflight",b,29);
 b=cases;pulses16694_used_resource_direct();pulses16694_group("used_resource_direct_final_cache",b,52);
 b=cases;pulses16694_source_scope_direct(xb,xn);pulses16694_group("source_scope_direct_final_cache",b,24);
 b=cases;pulses16694_layout_direct();pulses16694_group("layout_direct_final_cache",b,32);
 b=cases;pulses16694_callbacks();pulses16694_group("callbacks",b,12);
 b=cases;pulses16694_cold_warm_scope(xb,xn);pulses16694_group("cold_warm_scope",b,44);
 b=cases;pulses16694_transfer();pulses16694_group("Talon_transfer",b,4);
 b=cases;pulses16694_talon_underlay();pulses16694_group("Talon_underlay_direct",b,8);
 b=cases;pulses16694_lifecycle();pulses16694_group("lifecycle",b,7);
 b=cases;pulses16694_later_writers();pulses16694_group("later_native_final_writers",b,8);
 b=cases;pulses16694_fades();pulses16694_group("fade_high_bits",b,8);
 b=cases;pulses16694_player_aliases();pulses16694_group("player_generic_aliases",b,8);
 b=cases;pulses16694_all12_fades();pulses16694_group("all12_fade_lease",b,4);
 b=cases;pulses16694_legacy_final();pulses16694_group("legacy_reject_own_foreign",b,12);
 CHECK(cases>first_case&&checks>first_check);printf("PASS enemy pulses16694 native lifecycle: %u cases %u assertions; internal8 only; not gameplay/full build\n",cases-first_case,checks-first_check);free(xb);return 0;
}
