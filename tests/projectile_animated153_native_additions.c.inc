/* Controlled native renderer only, not gameplay/animation timing evidence.
 * Include after unchanged bolts745 companion and background companion. */
static const unsigned animated153_ids[3]={153,154,155};
static const char *animated153_pack;
static Asset *animated153_asset(unsigned id)
{int s=projectile_animated153_slot(id);CHECK(s>=0);return &projectile_animated153_resources[s].member;}
static void animated153_oracle(unsigned id,int x,int y,const PulsesBefore *b,bool final)
{
 Uint8 source[168],mask[168];blue_decode(id,source,mask);Asset *a=animated153_asset(id);CHECK(a->rgba);
 unsigned cells=0,covered=0,opaque=0;bool seen[168]={false};
 for(unsigned c=0;c<168;c++)cells+=mask[c]!=0;
 for(unsigned n=0;n<10752;n++) {
  unsigned c=(n/96/8)*12+(n%96)/8;const Uint8 *q=a->rgba+4*n;
  CHECK(!q[1]&&!q[2]&&(q[3]==0||q[3]==255));
  if(q[3]){CHECK(mask[c]);CHECK(q[0]==112||(q[0]>=120&&q[0]<=125)||(id!=153&&q[0]==119));opaque++;seen[c]=true;}
  else CHECK(!q[0]);
  int px=x*8+n%96,py=y*8+n/96;size_t p=(size_t)py*2560+px;
  Uint32 want=!mask[c]?b->canvas[n]:q[3]?(0xff000000u|(rgb_palette[q[0]]&0xffffffu)):b->under[n];
  if(mask[c]){CHECK(global_projectile91_owner[p]==1&&hd_owner[p]==1);CHECK(((Uint8 *)game_screen->pixels)[(y+n/96/8)*320+x+n%96/8]==source[c]);}
  CHECK(*at(final?output:canvas,px-(final?192:0),py)==want);
 }
 for(unsigned c=0;c<168;c++){covered+=seen[c];if(mask[c]&&!seen[c])CHECK(id==153&&c>=60&&c<=62);}
 CHECK(cells==(id==154?88u:76u));CHECK(covered==(id==153?73u:id==154?88u:76u));CHECK(opaque==(id==153?3424u:id==154?4944u:3777u));
}
static void animated153_valid(unsigned id,int x,int y,PulsesBefore *b)
{
 pulses16694_snapshot(b,x,y);bolts745_draw(id,x,y);
 CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
 CHECK(global_projectile91_used_members&global_projectile91_member(id));
 bolts745_callbacks_seen(id,x,y);animated153_oracle(id,x,y,b,false);
}
static void animated153_full_phase_and_masks(void)
{
 for(unsigned i=0;i<3;i++) {
  bolts745_setup();PulsesBefore b;animated153_valid(animated153_ids[i],110,80,&b);
  CHECK(global_projectile91_used_members==(16384u<<i));finish();CHECK(ready&&last_output_valid);
  animated153_oracle(animated153_ids[i],110,80,&b,true);global_projectile91_check_cache();CHECK(ready);
 }
 /* Four successive renderer frames, original observed phase ordering.
  * This tests renderer phase/cache identity, not engine animation scheduling. */
 const unsigned phases[4]={154,155,153,154};bolts745_setup();
 for(unsigned i=0;i<4;i++) {
  if(i){SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();}
  CHECK(!global_projectile91_used_members);PulsesBefore b;animated153_valid(phases[i],110,80,&b);
  CHECK(global_projectile91_used_members==global_projectile91_member(phases[i]));finish();CHECK(ready);animated153_oracle(phases[i],110,80,&b,true);
 }
 /* Multiple original phase identities at the same position in one frame. */
 bolts745_setup();unsigned bits=0;
 for(unsigned i=0;i<4;i++){PulsesBefore b;animated153_valid(phases[i],110,80,&b);bits|=global_projectile91_member(phases[i]);CHECK(global_projectile91_used_members==bits);}
 finish();CHECK(ready&&global_projectile91_used_members==114688u);
 bolts745_setup();
 for(unsigned i=0;i<14;i++)bolts745_draw(bolts745_ids[i],30+(i%7)*35,20+(i/7)*45);
 for(unsigned i=0;i<3;i++){PulsesBefore b;animated153_valid(animated153_ids[i],30+i*35,110,&b);}
 CHECK(global_projectile91_used_members==131071u);finish();CHECK(ready&&last_output_valid);global_projectile91_check_cache();CHECK(ready);
}
static void animated153_gaps(void)
{
 bolts745_setup();PulsesBefore b;animated153_valid(153,110,80,&b);
 Asset *a=animated153_asset(153);
 for(unsigned cx=0;cx<3;cx++)for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++) {
  unsigned ax=cx*8+sx,ay=40+sy,n=ay*96+ax;CHECK(!a->rgba[n*4+3]);
  CHECK(global_projectile91_call.mask[60+cx]);CHECK(global_projectile91_owner[(size_t)(640+ay)*2560+880+ax]);
  CHECK(*at(canvas,880+ax,640+ay)==(0xff000000u|(rgb_palette[27]&0xffffffu)));
 }
 finish();CHECK(ready);animated153_oracle(153,110,80,&b,true);
}
static void animated153_fixtures(void)
{
 static const char *kinds[11]={"missing","bad","header","magic","density","width","height","anchorx","anchory","short","trailing"};
 const char *saved=valid_root;char path[1200];
 for(unsigned s=0;s<3;s++)for(unsigned k=0;k<11;k++)for(unsigned warm=0;warm<2;warm++) {
  unsigned id=animated153_ids[s],other=animated153_ids[(s+1)%3];int n=snprintf(path,sizeof(path),"%s/%s%u",animated153_pack,kinds[k],id);CHECK(n>0&&(size_t)n<sizeof(path));valid_root=path;bolts745_setup();
  if(warm){PulsesBefore b;animated153_valid(other,110,80,&b);}
  bolts745_draw(id,180,80);CHECK(!global_projectile91_fault);CHECK(!(global_projectile91_used_members&global_projectile91_member(id)));
  finish();if(warm)CHECK(ready&&global_projectile91_used_members==global_projectile91_member(other));else CHECK(!ready&&!global_projectile91_contributed);
 }
 valid_root=saved;
}
static void animated153_dependencies(void)
{
 for(unsigned s=0;s<3;s++)for(unsigned cached=0;cached<2;cached++)for(unsigned used=0;used<2;used++) {
  bolts745_setup();unsigned id=animated153_ids[s],other=animated153_ids[(s+1)%3];PulsesBefore b;animated153_valid(id,110,80,&b);
  Asset *dep=projectile_animated153_resource(valid_root,used?id:other);CHECK(dep);if(cached){finish();CHECK(ready);}
  dep->rgba[128]^=1;
  if(cached)global_projectile91_check_cache();else finish();
  if(used)CHECK(!ready&&!last_output_valid);else CHECK(ready&&last_output_valid);
 }
 for(unsigned s=0;s<3;s++)for(unsigned mode=0;mode<3;mode++) {
  bolts745_setup();PulsesBefore b;animated153_valid(animated153_ids[s],110,80,&b);
  CHECK(global_projectile91_used_colors[125]);if(mode==1){finish();CHECK(ready);}rgb_palette[125]^=1;
  if(mode==1)global_projectile91_check_cache();else if(mode==2){bolts745_draw(animated153_ids[(s+1)%3],180,80);finish();}else finish();
  CHECK(!ready&&!last_output_valid);
 }
}
static void animated153_handoff_and_live_palette(void)
{
 for(unsigned s=0;s<3;s++) {
  bolts745_setup();unsigned id=animated153_ids[s];PulsesBefore b;animated153_valid(id,110,80,&b);finish();CHECK(ready);
  Uint8 src[168],mask[168];blue_decode(id,src,mask);
  for(unsigned c=0;c<168;c++)if(mask[c]) {
   int x=110+c%12,y=80+c/12;Uint8 *p=(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch+x-24;Uint8 old=*p;*p=58;render_mirror_pixel(VGAScreenSeg,p,old,MIRROR_NORMAL);
  }
  for(unsigned n=0;n<10752;n++)CHECK(!global_projectile91_owner[(size_t)(640+n/96)*2560+880+n%96]);
  CHECK(global_projectile91_contributed&&global_projectile91_used_members==global_projectile91_member(id));
  animated153_asset(id)->rgba[128]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 }
 for(unsigned s=0;s<3;s++) {
  bolts745_setup();for(unsigned i=112;i<=125;i++)rgb_palette[i]=((i*37u&255u)<<16)|((i*61u&255u)<<8)|(i*83u&255u);
  PulsesBefore b;animated153_valid(animated153_ids[s],110,80,&b);finish();CHECK(ready);animated153_oracle(animated153_ids[s],110,80,&b,true);
 }
}
static void animated153_scope(void)
{
 for(unsigned s=0;s<3;s++)for(unsigned mode=0;mode<6;mode++) {
  bolts745_setup();unsigned id=animated153_ids[s];
  if(mode==0)xmas=true;else if(mode==1)game_probe_density=4;else if(mode==2)game_probe_missing=true;else if(mode==3)game_probe_invalid=true;else if(mode==4)game_probe_original_reference=true;
  if(mode==5){Sprite2_array wrong={spriteSheet8.size,spriteSheet8.data+1};CHECK(!render_mirror_enemy_shot(game_screen,110,80,wrong,id));}
  else bolts745_draw(id,110,80);
  CHECK(!global_projectile91_contributed&&!global_projectile91_used_members);
 }
 for(unsigned s=0;s<3;s++) {
  bolts745_setup();unsigned id=animated153_ids[s];SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
  blit_sprite2(classic,110,80,spriteSheet8,id);draw_player_shot_sprite2(game_screen,110,80,spriteSheet8,id,0,id);
  CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(!global_projectile91_contributed);SDL_FreeSurface(classic);
  Asset generic={0};generic.bank=ASSET_ENEMY_ANIMATED153;generic.index=id;CHECK(!read_asset(&generic,8));
 }
}
static int animated153_main(int argc,char **argv)
{
 CHECK(argc==3&&!strcmp(argv[1],"--enemy-animated153"));animated153_pack=argv[2];
 static char root[1200];int n=snprintf(root,sizeof(root),"%s/valid",animated153_pack);CHECK(n>0&&(size_t)n<sizeof(root));valid_root=missing_root=root;
 read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));Uint32 count;read_exact(&count,4);CHECK(count==33484);spriteSheet9.size=count;spriteSheet9.data=malloc(count);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,count);
 Uint32 xn;read_exact(&xn,4);CHECK(xn==32404);Uint8 *xb=malloc(xn);CHECK(xb);read_exact(xb,xn);CHECK(fgetc(stdin)==EOF);free(xb);
 unsigned initial_cases=cases,initial_checks=checks;
 animated153_full_phase_and_masks();animated153_gaps();animated153_fixtures();animated153_dependencies();animated153_handoff_and_live_palette();animated153_scope();animated153_background_cases();
 printf("PASS enemy animated153 native: %u setup cases %u assertions; internal8 only; NOT gameplay\n",cases-initial_cases,checks-initial_checks);return 0;
}
