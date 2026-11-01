/* SPDX-License-Identifier: GPL-2.0-or-later
 * New current-production companion. Inherited companions remain unchanged.
 * Controlled native renderer only: NOT natural gameplay or scene proof. */
static const unsigned bolts745_ids[14]={91,145,61,101,120,139,168,169,162,260,166,94,7,45};
static const unsigned bolts745_new[2]={7,45};
static const char *bolts745_pack;
static unsigned bolts745_bit(unsigned id)
{for(unsigned k=0;k<14;k++)if(bolts745_ids[k]==id)return 1u<<k;return 0;}
static Asset *bolts745_asset(unsigned id)
{if(id!=7&&id!=45)return pulses16694_asset(id);int s=projectile_bolts745_slot(id);CHECK(s>=0);return &projectile_bolts745_resources[s].member;}
static void bolts745_setup(void){setup(3,1);}
static void bolts745_draw(unsigned id,int x,int y){blue_draw_bank(id,x,y,spriteSheet8);}
static void bolts745_snapshot(PulsesBefore *b,int x,int y){pulses16694_snapshot(b,x,y);}
/* Binary index payload oracle: no call to production RGB resolver/blender. */
static Uint32 bolts745_alpha(Uint32 under,unsigned id,const Uint8 *q)
{
 if(id!=7&&id!=45)return alpha(under,q);
 CHECK(!q[1]&&!q[2]&&(q[3]==0||q[3]==255));
 if(!q[3]){CHECK(!q[0]);return under;}
 CHECK(q[0]>=112&&q[0]<=125&&q[0]!=118&&q[0]!=121&&q[0]!=124);
 return 0xff000000u|(rgb_palette[q[0]]&0xffffffu);
}
static void bolts745_oracle(unsigned id,int x,int y,const PulsesBefore *b,bool final_output)
{
 const Uint8 *rgba=bolts745_asset(id)->rgba;CHECK(rgba);Uint8 src[168],mask[168];blue_decode(id,src,mask);
 unsigned cells=0,soft=0,opaque=0,clear=0,zero_native=0,visible=0;
 for(unsigned c=0;c<168;c++)cells+=mask[c]!=0;
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  unsigned i=(unsigned)(ay*96+ax),c=(unsigned)((ay/8)*12+ax/8);const Uint8 *q=rgba+4*i;
  if(!q[3]){++clear;zero_native+=mask[c]!=0;CHECK(!q[0]&&!q[1]&&!q[2]);}else if(q[3]==255)++opaque;else ++soft;
  if(!mask[c])CHECK(!q[0]&&!q[1]&&!q[2]&&!q[3]);
  int px=x*8+ax,py=y*8+ay;if(px<0||px>=2560||py<0||py>=1600)continue;
  Uint32 want=mask[c]?bolts745_alpha(b->under[i],id,q):b->canvas[i];
  size_t n=(size_t)py*2560+px;
  CHECK(global_projectile91_owner[n]<=1&&global_projectile91_foreign[n]<=1);
  if(mask[c]) {
   ++visible;CHECK(global_projectile91_owner[n]==1&&hd_owner[n]==1);
   CHECK(((Uint8 *)game_screen->pixels)[(y+ay/8)*320+x+ax/8]==src[c]);
  }else CHECK(global_projectile91_owner[n]==b->owned[i]);
  if(final_output){if(px<24*8||px>=288*8||py>=184*8)continue;CHECK(*at(output,px-24*8,py)==want);
   if(!mask[c]&&!hd_owner[n]) {
    Uint8 actual=((Uint8 *)VGAScreenSeg->pixels)[(py/8)*VGAScreenSeg->pitch+px/8-24];
    CHECK(*at(output,px-24*8,py)==(0xff000000u|(rgb_palette[actual]&0xffffffu)));
   }
  }
  else CHECK(*at(canvas,px,py)==want);
 }
 CHECK(cells>0&&soft+opaque+clear==10752);
 if(id==7||id==45)CHECK(cells==70&&soft==0&&opaque==4029&&clear==6723&&zero_native==451);
 if(visible)CHECK(global_projectile91_used_members&bolts745_bit(id));
}
static void bolts745_callbacks_seen(unsigned id,int x,int y)
{
 Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned visible=0,seen=0;
 for(unsigned c=0;c<168;c++) {
  bool v=mask[c]&&x+(int)(c%12)>=0&&x+(int)(c%12)<320&&y+(int)(c/12)>=0&&y+(int)(c/12)<200;
  visible+=v;seen+=global_projectile91_call.seen[c]!=0;CHECK((global_projectile91_call.seen[c]!=0)==v);
 }
 CHECK(seen==visible&&!global_projectile91_call.left&&!global_projectile91_call.live);
 if(x==110&&y==80&&id==7)CHECK(seen==70);
 if(x==110&&y==80&&id==45)CHECK(seen==70);
}
static void bolts745_valid(unsigned id,int x,int y,PulsesBefore *b)
{
 bolts745_snapshot(b,x,y);bolts745_draw(id,x,y);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
 CHECK(global_projectile91_used_members&bolts745_bit(id));bolts745_callbacks_seen(id,x,y);bolts745_oracle(id,x,y,b,false);
}
static void bolts745_expected(Uint32 *want,unsigned id,const PulsesBefore *b)
{
 Uint8 src[168],mask[168];blue_decode(id,src,mask);const Uint8 *rgba=bolts745_asset(id)->rgba;
 for(unsigned i=0;i<10752;i++)want[i]=mask[(i/96/8)*12+(i%96)/8]?bolts745_alpha(b->under[i],id,rgba+4*i):b->canvas[i];
}
static void bolts745_output_expected(const Uint32 *want,int x,int y)
{
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  int px=x*8+ax,py=y*8+ay;if(px<192||px>=2304||py<0||py>=1472)continue;
  CHECK(*at(output,px-192,py)==want[ay*96+ax]);
 }
}
static void bolts745_bounds(void)
{
 const int accept[][2]={{0,80},{308,80},{110,-13},{110,-6},{110,180},{110,190},{110,199}};
 const int reject[][2]={{-1,80},{309,80},{110,-14},{110,200}};
 for(unsigned s=0;s<2;s++) {
  for(unsigned k=0;k<7;k++) {
   bolts745_setup();unsigned id=bolts745_new[s];int x=accept[k][0],y=accept[k][1];Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned visible=0,output_visible=0;
   for(unsigned c=0;c<168;c++)if(mask[c]){int cx=x+(int)(c%12),cy=y+(int)(c/12);visible+=cy>=0&&cy<200;output_visible+=cx>=24&&cx<288&&cy>=0&&cy<184;}
   PulsesBefore b;bolts745_snapshot(&b,x,y);bolts745_draw(id,x,y);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
   bolts745_callbacks_seen(id,x,y);CHECK(global_projectile91_used_members==(visible?bolts745_bit(id):0u));bolts745_oracle(id,x,y,&b,false);
   finish();if(output_visible){CHECK(ready&&last_output_valid);bolts745_oracle(id,x,y,&b,true);global_projectile91_check_cache();CHECK(ready&&last_output_valid);bolts745_oracle(id,x,y,&b,true);}else CHECK(!ready&&!last_output_valid);
  }
  for(unsigned k=0;k<4;k++){bolts745_setup();bolts745_draw(bolts745_new[s],reject[k][0],reject[k][1]);CHECK(!global_projectile91_used_members&&!global_projectile91_contributed&&!global_projectile91_fault);finish();CHECK(!ready&&!last_output_valid);}
 }
}
static void bolts745_used_resource_direct(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<13;mode++)for(unsigned cached=0;cached<2;cached++) {
  bolts745_setup();unsigned id=bolts745_new[s];PulsesBefore b;bolts745_valid(id,110,80,&b);if(cached)blue_accept();
  Asset *a=bolts745_asset(id);Uint8 *saved=a->rgba;
  switch(mode){case 0:a->rgba[100]^=1;break;case 1:a->initialized=false;break;case 2:a->valid=false;break;case 3:a->bank=ASSET_ENEMY_GOLD_PULSE;break;case 4:a->index=bolts745_new[1-s];break;case 5:a->w=11;break;case 6:a->h=13;break;case 7:a->anchor_x=1;break;case 8:a->anchor_y=1;break;case 9:a->density=4;break;case 10:a->rgba=NULL;break;case 11:projectile_bolts745_resources[s].valid=false;break;case 12:projectile_bolts745_resources[s].root[0]^=1;break;}
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);if(mode==10)a->rgba=saved;
 }
}
static void bolts745_layout_direct(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<8;mode++)for(unsigned cached=0;cached<2;cached++) {
  bolts745_setup();PulsesBefore b;bolts745_valid(bolts745_new[s],110,80,&b);if(cached)blue_accept();
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
static void bolts745_callbacks(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<6;mode++) {
  bolts745_setup();unsigned id=bolts745_new[s];CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,id));
  CHECK(global_projectile91_used_members==bolts745_bit(id)&&global_projectile91_call.live&&global_projectile91_call.left==70u);
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
static void bolts745_player_aliases(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned warm=0;warm<2;warm++)for(unsigned inverse=0;inverse<2;inverse++) {
  bolts745_setup();unsigned id=bolts745_new[s];PulsesBefore b;
  if(warm)bolts745_valid(id,110,80,&b);
  unsigned bits=global_projectile91_used_members;bool contributed=global_projectile91_contributed;
  bool checked[2]={projectile_bolts745_resources[0].checked,projectile_bolts745_resources[1].checked};
  SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
  uint64_t rng=mt_state_fingerprint();Uint32 pal[256];JE_MultiEnemyType actors;EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(pal,rgb_palette,sizeof(pal));memcpy(actors,enemy,sizeof(enemy));memcpy(shots,enemyShot,sizeof(shots));
  for(unsigned j=0;j<2;j++) {
   unsigned style=(j+inverse)%2;
   if(style){blit_sprite2_darken(classic,40,80,spriteSheet8,id);draw_player_shot_shadow_sprite2(game_screen,40,80,spriteSheet8,id,0,id);}
   else{blit_sprite2(classic,40,80,spriteSheet8,id);draw_player_shot_sprite2(game_screen,40,80,spriteSheet8,id,0,id);}
   CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(global_projectile91_used_members==bits&&global_projectile91_contributed==contributed&&!global_projectile91_call.live);
   for(unsigned k=0;k<2;k++)CHECK(projectile_bolts745_resources[k].checked==checked[k]);
  }
  CHECK(!get_asset(spriteSheet8,id,ENTITY_TILE));blit_sprite2(classic,60,80,spriteSheet8,id);draw_entity_sprite2(game_screen,60,80,spriteSheet8,id,ENTITY_NORMAL,ENTITY_TILE);
  CHECK(!memcmp(classic->pixels,game_screen->pixels,64000)&&rng==mt_state_fingerprint());CHECK(!memcmp(pal,rgb_palette,sizeof(pal))&&!memcmp(actors,enemy,sizeof(enemy))&&!memcmp(shots,enemyShot,sizeof(shots)));
  CHECK(global_projectile91_used_members==bits&&global_projectile91_contributed==contributed&&!global_projectile91_fault);SDL_FreeSurface(classic);
  if(!warm)bolts745_valid(id,110,80,&b);finish();CHECK(ready&&last_output_valid&&global_projectile91_used_members==bolts745_bit(id));bolts745_oracle(id,110,80,&b,true);
 }
}
static void bolts745_later_writers(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<4;mode++) {
  bolts745_setup();unsigned id=bolts745_new[s];PulsesBefore b;bolts745_valid(id,110,80,&b);Uint8 src[168],mask[168];blue_decode(id,src,mask);unsigned c=0;while(c<168&&!mask[c])++c;CHECK(c<168);
  int x=110+(int)(c%12),y=80+(int)(c/12);Uint8 *p;
  if(mode==0){p=(Uint8 *)game_screen->pixels+y*320+x;*p=58;render_mirror_pixel(game_screen,p,src[c],MIRROR_NORMAL);finish();}
  else{blue_accept();if(mode==3){
   /* Revoke every owned native cell by legitimate final writes, never by
    * clearing a private owner array. Provenance must outlive all pixel owners. */
   for(unsigned j=0;j<168;j++)if(mask[j]){int xx=110+(int)(j%12),yy=80+(int)(j/12);p=(Uint8 *)VGAScreenSeg->pixels+yy*320+xx-24;*p=58;render_mirror_pixel(VGAScreenSeg,p,src[j],MIRROR_NORMAL);}
   for(unsigned i=0;i<10752;i++)CHECK(!global_projectile91_owner[(size_t)(640+i/96)*2560+880+i%96]);
  }else{p=(Uint8 *)VGAScreenSeg->pixels+y*320+x-24;*p=58;if(mode==1)render_mirror_pixel(VGAScreenSeg,p,src[c],MIRROR_NORMAL);else{SDL_Rect r={x-24,y,1,1};render_mirror_rect(VGAScreenSeg,&r);}}}
  CHECK(ready&&last_output_valid&&global_projectile91_contributed&&global_projectile91_used_members==bolts745_bit(id));
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){size_t n=(size_t)(y*8+sy)*2560+x*8+sx;CHECK(!global_projectile91_owner[n]&&!global_projectile91_foreign[n]);CHECK(*at(output,(x-24)*8+sx,y*8+sy)==palette_rgb(58));}
  global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==bolts745_bit(id));
  bolts745_asset(id)->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
}
static void bolts745_fades(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<4;mode++) {
  bolts745_setup();PulsesBefore b;bolts745_valid(bolts745_new[s],110,80,&b);blue_accept();Uint32 want[10752];bolts745_expected(want,bolts745_new[s],&b);SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);
  CHECK(global_projectile91_cached&&have_fade_saved&&last_output_valid); /* This valid controlled fixture must exercise, not skip, the fade lease. */
  CHECK(have_fade_saved&&global_projectile91_used_members==bolts745_bit(bolts745_new[s]));
  if(mode==3){
   /* Real positive integer palette step; no float/rounded substitute. */
   for(unsigned i=0;i<256;i++){Uint32 old=rgb_palette[i],next=old&0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}rgb_palette[i]=next;}
   CHECK(global_projectile91_fade_step_valid(7));render_mirror_fade_step(7);
   CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_projectile91_used_members==bolts745_bit(bolts745_new[s]));
   for(unsigned i=0;i<10752;i++){Uint32 old=want[i],next=0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}want[i]=next;}
   bolts745_output_expected(want,110,80);global_projectile91_check_cache();CHECK(ready&&last_output_valid&&global_projectile91_used_members==bolts745_bit(bolts745_new[s]));
   bolts745_asset(bolts745_new[s])->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);continue;
  }
  if(mode==0){bolts745_asset(bolts745_new[s])->rgba[100]^=1;CHECK(!global_projectile91_fade_step_valid(7));}
  if(mode==1)CHECK(!global_projectile91_fade_step_valid(0));
  if(mode==2){rgb_palette[200]^=1;CHECK(!global_projectile91_fade_step_valid(7));}
  CHECK(!ready&&!last_output_valid&&!have_fade_saved);
 }
}
static void bolts745_full_and_palettes(void)
{
 for(unsigned s=0;s<2;s++)for(unsigned palette=0;palette<3;palette++) {
  bolts745_setup();unsigned id=bolts745_new[s];
  if(palette) {
   for(unsigned i=0;i<256;i++)rgb_palette[i]=palette==1?(i*0x010307u)&0xffffffu:0xffffffu;
   /* This is cold palette admission: establish its frame before snapshot.
    * Final unowned pixels resolve the current INDEX8 palette, not old canvas. */
   render_mirror_begin();
  }
  PulsesBefore b;bolts745_valid(id,110,80,&b);CHECK(global_projectile91_used_members==bolts745_bit(id));
  CHECK(bolts745_asset(id)->bank==156);finish();CHECK(ready&&last_output_valid);bolts745_oracle(id,110,80,&b,true);
  global_projectile91_check_cache();CHECK(ready&&last_output_valid);bolts745_oracle(id,110,80,&b,true);
 }
 /* Every contributed palette index is a temporal dependency, not fixed RGB. */
 const unsigned indices[]={112,113,114,115,116,117,119,120,122,123,125};
 for(unsigned s=0;s<2;s++)for(unsigned k=0;k<11;k++)for(unsigned cached=0;cached<2;cached++) {
  bolts745_setup();PulsesBefore b;bolts745_valid(bolts745_new[s],110,80,&b);if(cached)blue_accept();
  CHECK(global_projectile91_used_colors[indices[k]]);rgb_palette[indices[k]]^=1;
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned s=0;s<2;s++) {
  bolts745_setup();PulsesBefore b;bolts745_valid(bolts745_new[s],110,80,&b);blue_accept();
  render_mirror_begin();rgb_palette[125]^=0x121314;bolts745_valid(bolts745_new[s],110,80,&b);blue_accept();bolts745_oracle(bolts745_new[s],110,80,&b,true);
 }
}
static void bolts745_mixed(void)
{
 /* New vs all old and each other, both orders; per-pixel independent oracle. */
 for(unsigned a=0;a<14;a++)for(unsigned b=a+1;b<14;b++)if(a>=12||b>=12)for(unsigned reverse=0;reverse<2;reverse++) {
  bolts745_setup();unsigned first=bolts745_ids[reverse?b:a],last=bolts745_ids[reverse?a:b];PulsesBefore before;Uint32 want[10752];
  bolts745_valid(first,110,80,&before);bolts745_valid(last,110,80,&before);bolts745_expected(want,last,&before);
  CHECK(global_projectile91_used_members==(bolts745_bit(first)|bolts745_bit(last)));
  blue_accept();bolts745_output_expected(want,110,80);global_projectile91_check_cache();CHECK(ready);bolts745_output_expected(want,110,80);
  bolts745_asset(first)->rgba[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned damaged=0;damaged<14;damaged++)for(unsigned cached=0;cached<2;cached++) {
  bolts745_setup();PulsesBefore before;
  for(unsigned k=0;k<14;k++)bolts745_valid(bolts745_ids[k],40+35*(k%7),60+40*(k/7),&before);
  CHECK(global_projectile91_used_members==16383u);if(cached)blue_accept();
  bolts745_asset(bolts745_ids[damaged])->rgba[100]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void bolts745_source_scope(const Uint8 *xb,size_t xn)
{
 for(unsigned mode=0;mode<12;mode++)for(unsigned cached=0;cached<2;cached++) {
  bolts745_setup();PulsesBefore b;bolts745_valid(7,80,80,&b);bolts745_valid(45,140,80,&b);if(cached)blue_accept();
  switch(mode){case 0:livebank[100]^=1;break;case 1:livebank[0]^=1;break;case 2:spriteSheet8.size--;break;case 3:spriteSheet8.data=NULL;break;case 4:xmas=true;break;case 5:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};break;case 6:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};xmas=true;break;case 7:spriteSheet12=spriteSheet8;break;case 8:game_probe_original_reference=true;break;case 9:game_probe_missing=true;break;case 10:game_probe_invalid=true;break;case 11:game_probe_density=4;break;}
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);if(mode==11)game_probe_density=8;
 }
}
static void bolts745_cold_warm_scope(const Uint8 *xb,size_t xn)
{
 for(unsigned s=0;s<2;s++)for(unsigned mode=0;mode<11;mode++)for(unsigned warm=0;warm<2;warm++) {
  bolts745_setup();unsigned id=bolts745_new[s];Uint8 foreign[32060];memcpy(foreign,original,sizeof(foreign));Sprite2_array bank=spriteSheet8;
  /* Both selected Christmas shapes differ; normal whole-bank guard is required. */
  Uint8 ns[168]={0},nm[168]={0},xs[168]={0},xm[168]={0};CHECK(decode_tile(spriteSheet8,id,ns,nm,12,0,0));CHECK(decode_tile((Sprite2_array){xn,(Uint8 *)xb},id,xs,xm,12,0,0));CHECK(memcmp(ns,xs,168)&&memcmp(nm,xm,168));
  if(warm){PulsesBefore b;bolts745_valid(91,40,60,&b);}
  switch(mode){case 0:xmas=true;break;case 1:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};bank=spriteSheet8;break;case 2:spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb};bank=spriteSheet8;xmas=true;break;case 3:game_probe_density=4;break;case 4:bank=(Sprite2_array){sizeof(foreign),foreign};break;case 5:spriteSheet12=spriteSheet8;break;case 6:bank.size--;break;case 7:bank.data=NULL;break;case 8:game_probe_original_reference=true;break;case 9:game_probe_missing=true;break;case 10:game_probe_invalid=true;break;}
  CHECK(!render_mirror_enemy_shot(game_screen,110,80,bank,id));CHECK(!global_projectile91_call.live);
  if(mode==3)game_probe_density=8;
  if(warm&&(mode==4||mode==6||mode==7)){CHECK(global_projectile91_used_members==1u&&!global_projectile91_fault);blue_accept();}
  else{if(warm)CHECK(global_projectile91_fault);else CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);finish();CHECK(!ready&&!last_output_valid);}
 }
}

static void bolts745_fixture_path(char *out,size_t size,const char *kind,unsigned id)
{int n=snprintf(out,size,"%s/%s%u",bolts745_pack,kind,id);CHECK(n>0&&(size_t)n<size);}
static void bolts745_fixtures(void)
{
 char path[1200],good[1200];int n=snprintf(good,sizeof(good),"%s/valid",bolts745_pack);CHECK(n>0&&(size_t)n<sizeof(good));
 const char *kinds[]={"missing","bad","header","short","trailing","magic","density","width","height","anchorx","anchory"};
 for(unsigned s=0;s<2;s++)for(unsigned kind=0;kind<11;kind++)for(unsigned warm=0;warm<2;warm++) {
  unsigned id=bolts745_new[s],other=bolts745_new[1-s];bolts745_fixture_path(path,sizeof(path),kinds[kind],id);valid_root=path;bolts745_setup();PulsesBefore b;
  if(warm)bolts745_valid(other,110,80,&b);bolts745_draw(id,180,80);CHECK(!global_projectile91_fault&&!(global_projectile91_used_members&bolts745_bit(id)));
  if(!warm)bolts745_valid(other,110,80,&b);blue_accept();
 }
 for(unsigned s=0;s<2;s++) {
  unsigned id=bolts745_new[s];valid_root=good;bolts745_setup();PulsesBefore b;bolts745_valid(id,110,80,&b);blue_accept();
  bolts745_fixture_path(path,sizeof(path),"missing",id);CHECK(render_mirror_set_global_assets(path));render_mirror_begin();bolts745_draw(id,110,80);CHECK(!global_projectile91_used_members&&!global_projectile91_fault);finish();CHECK(!ready);
  CHECK(render_mirror_set_global_assets(good));render_mirror_begin();bolts745_valid(id,110,80,&b);blue_accept();
  CHECK(render_mirror_set_global_assets(good));CHECK(ready); /* same root is not epoch */
  render_mirror_hud_shutdown();CHECK(!projectile_bolts745_resources[0].checked&&!projectile_bolts745_resources[1].checked&&!ready);
 }
 /* Missing unused historical member cannot gate either new indexed member. */
 for(unsigned k=0;k<12;k++) {
  bolts745_fixture_path(path,sizeof(path),"missing",bolts745_ids[k]);valid_root=path;bolts745_setup();PulsesBefore before;
  bolts745_valid(7,110,80,&before);bolts745_valid(45,160,80,&before);CHECK(global_projectile91_used_members==12288u);blue_accept();
 }
 valid_root=good;bolts745_setup();PulsesBefore b;bolts745_valid(7,110,80,&b);bolts745_valid(45,160,80,&b);blue_accept();
 CHECK(render_mirror_set_global_assets(""));CHECK(!ready&&!last_output_valid&&!global_projectile91_used_members);
 /* valid_root must outlive this stack frame. */
 static char stable[1200];memcpy(stable,good,strlen(good)+1);valid_root=stable;
}
static void bolts745_temporal_and_layout(void)
{
 for(unsigned selector=0;selector<2;selector++) {
  unsigned id=bolts745_new[selector];PulsesBefore b;
  bolts745_setup();for(unsigned i=112;i<=125;i++)rgb_palette[i]=0x123456;
  bolts745_valid(id,110,80,&b);blue_accept();bolts745_oracle(id,110,80,&b,true);
  bolts745_setup();bolts745_valid(id,110,80,&b);CHECK(!global_projectile91_used_colors[200]);rgb_palette[200]^=1;
  blue_accept();global_projectile91_check_cache();CHECK(ready);rgb_palette[200]^=2;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
  /* Provenance survives complete legitimate final-surface owner handoff. */
  bolts745_setup();bolts745_valid(id,110,80,&b);blue_accept();Uint8 src[168],mask[168];blue_decode(id,src,mask);
  for(unsigned c=0;c<168;c++)if(mask[c]){int x=110+c%12,y=80+c/12;Uint8 *v=(Uint8 *)VGAScreenSeg->pixels+y*320+x-24;*v=58;render_mirror_pixel(VGAScreenSeg,v,src[c],MIRROR_NORMAL);}
  for(unsigned i=0;i<10752;i++)CHECK(!global_projectile91_owner[(size_t)(640+i/96)*2560+880+i%96]);
  CHECK(global_projectile91_contributed&&global_projectile91_used_members==bolts745_bit(id));rgb_palette[125]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned target=0;target<2;target++)for(unsigned mode=0;mode<4;mode++)for(unsigned warm=0;warm<4;warm++) {
  bolts745_setup();PulsesBefore b;if(warm)bolts745_valid(7,110,80,&b);
  if(warm>=2)blue_accept();
  if(warm==3){Uint8 src[168],mask[168];blue_decode(7,src,mask);for(unsigned c=0;c<168;c++)if(mask[c]){int x=110+c%12,y=80+c/12;Uint8 *q=(Uint8 *)VGAScreenSeg->pixels+y*320+x-24;*q=58;render_mirror_pixel(VGAScreenSeg,q,src[c],MIRROR_NORMAL);}}
  SDL_Surface *v=target?output:canvas;SDL_PixelFormat saved=*v->format;
  if(mode==0)v->format->format=SDL_PIXELFORMAT_ABGR8888;
  else if(mode==1)v->format->Rmask^=1;else if(mode==2)v->format->Rshift=0;else v->format->Rloss=1;
  if(warm){if(warm>=2)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);}else {CHECK(!render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,7));CHECK(!global_projectile91_contributed);}
  *v->format=saved;
 }
}

static int bolts745_main(int argc,char **argv)
{
 CHECK(argc==3&&!strcmp(argv[1],"--enemy-bolts745"));bolts745_pack=argv[2];
 static char root[1200];int n=snprintf(root,sizeof(root),"%s/valid",bolts745_pack);CHECK(n>0&&(size_t)n<sizeof(root));valid_root=root;missing_root=root;
 read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));
 Uint32 count;read_exact(&count,4);CHECK(count==33484);spriteSheet9.size=count;spriteSheet9.data=malloc(count);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,count);
 Uint32 xn;read_exact(&xn,4);CHECK(xn==32404);Uint8 *xb=malloc(xn);CHECK(xb);read_exact(xb,xn);CHECK(fgetc(stdin)==EOF);
 unsigned initial_cases=cases,initial_checks=checks;
 bolts745_full_and_palettes();bolts745_mixed();bolts745_bounds();bolts745_used_resource_direct();bolts745_layout_direct();bolts745_callbacks();bolts745_player_aliases();bolts745_later_writers();bolts745_fades();bolts745_source_scope(xb,xn);bolts745_cold_warm_scope(xb,xn);bolts745_temporal_and_layout();bolts745_fixtures();
 printf("PASS enemy bolts745 native lifecycle: %u cases %u assertions; internal8 only; NOT gameplay\n",cases-initial_cases,checks-initial_checks);free(xb);return 0;
}
