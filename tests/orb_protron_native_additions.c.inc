/* Current macro-OFF ordinary qualification only. Legacy ON intent/routing is
 * a separate exact-source diagnostic, never claimed as ON pixel execution. */
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE
#error "orb-protron ordinary matrix is pinned to macro OFF"
#endif
static const unsigned op_ids[4]={112,113,226,227};
static const unsigned op_cells[4]={45,45,21,45},op_nonzero[4]={2819,2849,1263,2552};
static const unsigned op_soft[4]={2819,2849,1263,2552},op_halos[4]={0,0,0,2},op_unions[4]={2880,2880,1344,2882};
static const char *op_pack;
static Asset *op_asset(unsigned k){CHECK(k<4);return &enemy_orb_protron_resources[k].member;}
static void op_draw(unsigned k,int x,int y){blue_draw_bank(op_ids[k],x,y,spriteSheet8);}
static void op_oracle(unsigned k,int x,int y,const PulsesBefore *b,bool final)
{
 Uint8 src[168],mask[168];blue_decode(op_ids[k],src,mask);const Uint8 *a=op_asset(k)->rgba;CHECK(a);
 unsigned cells=0,nz=0,soft=0,halo=0,un=0;for(unsigned c=0;c<168;c++)cells+=mask[c]!=0;
 for(unsigned n=0;n<10752;n++) {
  unsigned c=n/96/8*12+n%96/8;const Uint8 *q=a+4*n;bool support=mask[c]||q[3];nz+=q[3]!=0;soft+=q[3]>0&&q[3]<255;halo+=q[3]&&!mask[c];un+=support;
  int px=x*8+n%96,py=y*8+(int)(n/96);if(px<0||px>=2560||py<0||py>=1600)continue;size_t pos=(size_t)py*2560+px;
  Uint32 want=support?alpha(b->under[n],q):b->canvas[n];
  CHECK(((Uint8 *)game_screen->pixels)[py/8*320+px/8]==(mask[c]?src[c]:b->native[c]));
  if(support){CHECK(global_projectile91_owner[pos]&&hd_owner[pos]);CHECK(global_projectile91_used_members&(16777216u<<k));}
  else CHECK(global_projectile91_owner[pos]==b->owned[n]);
  if(final){if(px<192||px>=2304||py>=1472)continue;CHECK(*at(output,px-192,py)==want);}else CHECK(*at(canvas,px,py)==want);
 }
 CHECK(cells==op_cells[k]&&nz==op_nonzero[k]&&soft==op_soft[k]&&halo==op_halos[k]&&un==op_unions[k]);
}
static void op_valid(unsigned k,int x,int y,PulsesBefore *b)
{pulses16694_snapshot(b,x,y);op_draw(k,x,y);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);CHECK(global_projectile91_used_members&(16777216u<<k));bolts745_callbacks_seen(op_ids[k],x,y);op_oracle(k,x,y,b,false);}
static unsigned op_halo(unsigned k)
{Uint8 src[168],mask[168];blue_decode(op_ids[k],src,mask);for(unsigned n=0;n<10752;n++)if(!mask[n/96/8*12+n%96/8]&&op_asset(k)->rgba[n*4+3]>0&&op_asset(k)->rgba[n*4+3]<255)return n;CHECK(false);return 0;}
static void op_retire(unsigned k,int x,int y)
{
 Uint8 src[168],mask[168];blue_decode(op_ids[k],src,mask);
 for(unsigned c=0;c<168;c++) {bool support=mask[c]!=0;
  for(unsigned n=0;n<64;n++)support|=op_asset(k)->rgba[4*((c/12*8+n/8)*96+c%12*8+n%8)+3]!=0;
  if(support){Uint8 *p=(Uint8 *)game_screen->pixels+(y+c/12)*game_screen->pitch+x+c%12;*p=58;render_mirror_pixel(game_screen,p,58,MIRROR_NORMAL);}
 }
 for(unsigned n=0;n<10752;n++)CHECK(!global_projectile91_owner[(size_t)(y*8+n/96)*2560+x*8+n%96]);
 CHECK(global_projectile91_contributed&&(global_projectile91_used_members&(16777216u<<k)));
}
static void op_old24_draw(void)
{ws_old18_draw();for(unsigned k=0;k<6;k++)ws_draw(k,30+k*35,150);CHECK(global_projectile91_used_members==16777215u);}
static void op_direct28(void)
{
 ws_direct24();PulsesBefore b;
 for(unsigned k=0;k<4;k++){enemy70_setup();op_valid(k,110,80,&b);CHECK(global_projectile91_used_members==(16777216u<<k));finish();CHECK(ready&&last_output_valid);op_oracle(k,110,80,&b,true);}
}
static void op_faults16(void)
{
 const char *saved=valid_root;char root[1200];PulsesBefore b;
 for(unsigned k=0;k<4;k++)for(unsigned m=0;m<4;m++) {
  if(m<3){const char *kind=m==0?"missing":m==1?"bad":"header";int n=snprintf(root,sizeof(root),"%s/%s%u",op_pack,kind,op_ids[k]);CHECK(n>0&&(size_t)n<sizeof(root));valid_root=root;}else valid_root=saved;
  enemy70_setup();
  if(m==0)op_old24_draw();
  if(m<3){op_draw(k,220,80);CHECK(!(global_projectile91_used_members&(16777216u<<k))&&!global_projectile91_fault);finish();if(!m)CHECK(ready&&last_output_valid&&global_projectile91_used_members==16777215u);else CHECK(!ready&&!last_output_valid);}
  else {op_valid(k,110,80,&b);enemy70_draw(30,30);op_retire(k,110,80);finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);op_asset(k)->rgba[128]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);}
 }
 valid_root=saved;
}
static void op_phases6(void)
{
 PulsesBefore b;
 for(unsigned f=0;f<2;f++) {
  enemy70_setup();unsigned first=f*2;
  /* Controlled phase/cache epochs only; native animation/emission remains game-owned. */
  for(unsigned step=0;step<3;step++) {unsigned k=first+(step==1);if(step){SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();CHECK(!global_projectile91_used_members);}op_valid(k,110,80,&b);finish();CHECK(ready&&last_output_valid);op_oracle(k,110,80,&b,true);}
 }
 const char *saved=valid_root;char root[1200];
 for(unsigned missing=0;missing<4;missing++) {
  int n=snprintf(root,sizeof(root),"%s/missing%u",op_pack,op_ids[missing]);CHECK(n>0&&(size_t)n<sizeof(root));valid_root=root;enemy70_setup();unsigned other=missing^1u;
  op_draw(missing,110,80);CHECK(!global_projectile91_used_members);op_valid(other,110,80,&b);finish();CHECK(ready&&last_output_valid&&global_projectile91_used_members==(16777216u<<other));op_oracle(other,110,80,&b,true);
 }
 valid_root=saved;
}
static void op_palette8(void)
{
 const unsigned used[4]={114,115,136,129},unused[4]={115,114,129,136};
 for(unsigned k=0;k<4;k++)for(unsigned mutation=0;mutation<2;mutation++) {
  enemy70_setup();PulsesBefore b;op_valid(k,110,80,&b);rgb_palette[mutation?unused[k]:used[k]]^=1;finish();
  if(!mutation)CHECK(!ready&&!last_output_valid);else{CHECK(ready&&last_output_valid);op_oracle(k,110,80,&b,true);}
 }
}
static void op_background4(void)
{
 for(unsigned m=0;m<4;m++) {
  enemy70_setup();PulsesBefore b;op_valid(m,110,80,&b);CHECK(global_projectile91_used_colors[27]);Uint8 src[168],mask[168];blue_decode(op_ids[m],src,mask);unsigned zero=10752,soft=10752;
  for(unsigned n=0;n<10752;n++){unsigned a=op_asset(m)->rgba[4*n+3];if(mask[n/96/8*12+n%96/8]&&!a)zero=n;if(a>0&&a<255)soft=n;}
  CHECK(zero<10752&&soft<10752);CHECK(*at(canvas,880+zero%96,640+zero/96)==(0xff000000u|(rgb_palette[27]&0xffffffu)));CHECK(*at(canvas,880+soft%96,640+soft/96)==alpha(0xff000000u|(rgb_palette[27]&0xffffffu),op_asset(m)->rgba+4*soft));
  if(m==1||m==3){enemy70_draw(30,30);op_retire(m,110,80);}if(m>=2){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);}
  rgb_palette[27]^=1;if(m>=2)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
  SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();op_valid(m,110,80,&b);finish();CHECK(ready&&last_output_valid);op_oracle(m,110,80,&b,true);
 }
}
static void op_halos4(void)
{
 const unsigned hx[2]={23,64},hy[2]={31,72},ha[2]={2,1},cell[2]={38,116};
 for(unsigned h=0;h<2;h++)for(unsigned faded=0;faded<2;faded++) {
  enemy70_setup();PulsesBefore b;op_valid(3,110,80,&b);Uint8 src[168],mask[168];blue_decode(227,src,mask);unsigned n=hy[h]*96+hx[h];CHECK(op_asset(3)->rgba[4*n+3]==ha[h]&&!mask[cell[h]]&&hy[h]/8*12+hx[h]/8==cell[h]);finish();CHECK(ready&&last_output_valid);
  Uint32 restore[256];if(faded){memcpy(restore,rgb_palette,sizeof(restore));SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(!ready&&last_output_valid&&have_fade_saved);
   for(unsigned i=0;i<256;i++){Uint32 old=rgb_palette[i],next=old&0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}rgb_palette[i]=next;}render_mirror_fade_step(7);CHECK(ready&&last_output_valid&&global_projectile91_cached&&have_fade_saved&&fade_mode==1);}
  /* Exact existing helper checks shared direct-hook whole-cell no mutation,
   * public callback/present decline, and nextbegin independent RGBA recovery. */
  ws_final_decline(110+hx[h]/8,80+hy[h]/8,faded?restore:NULL,true);
  SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();op_valid(3,110,80,&b);finish();CHECK(ready&&last_output_valid);op_oracle(3,110,80,&b,true);
 }
}
static void op_roots3(void)
{
 char bad[1200];int n=snprintf(bad,sizeof(bad),"%s/missing112",op_pack);CHECK(n>0&&(size_t)n<sizeof(bad));
 enemy70_setup();Asset *a=enemy_orb_protron_resource(valid_root,112);CHECK(a);Uint8 *p=a->rgba;CHECK(enemy_orb_protron_resource(valid_root,112)==a&&a->rgba==p);CHECK(!enemy_orb_protron_resource(bad,112));CHECK(enemy_orb_protron_resource(valid_root,112)==a&&a->rgba==p);
 enemy70_setup();CHECK(!enemy_orb_protron_resource(bad,112));CHECK(!enemy_orb_protron_resource(valid_root,112));CHECK(enemy_orb_protron_resource(valid_root,113));enemy_orb_protron_shutdown();CHECK(enemy_orb_protron_resource(valid_root,112));
 enemy70_setup();int x,y;enemy70_player_birth(&x,&y);enemy70_player_draw(x,y);p=global_vulcan_rgba[1];CHECK(p);CHECK(enemy_orb_protron_resource(valid_root,227));enemy_orb_protron_shutdown();CHECK(global_vulcan_rgba[1]==p&&asteroid1_stamp(p,43008)==UINT64_C(0x6c26e938d94472c2));finish();CHECK(ready&&last_output_valid);
}
static void op_bits1(void)
{enemy70_setup();op_old24_draw();for(unsigned k=0;k<4;k++)op_draw(k,40+k*40,70);CHECK(global_projectile91_member(227)==134217728u);CHECK(global_projectile91_used_members==268435455u);finish();CHECK(ready&&last_output_valid);}
static void op_scope4(void)
{
 PulsesBefore b;enemy70_setup();op_valid(0,110,-6,&b);finish();CHECK(ready);op_oracle(0,110,-6,&b,true);
 enemy70_setup();xmas=true;op_draw(0,110,80);CHECK(!global_projectile91_contributed);
 enemy70_setup();game_probe_density=4;op_draw(3,110,80);CHECK(!global_projectile91_contributed);
 enemy70_setup();asteroid_hd_enabled=true;op_draw(0,110,80);CHECK(!global_projectile91_contributed&&!enemy_orb_protron_resources[0].checked);CHECK(!enemy_orb112113_resources.checked); /* old scope rejects, ordinary must not substitute */
}
static void op_used_source6(void)
{
 PulsesBefore b;for(unsigned k=0;k<4;k++){enemy70_setup();op_valid(k,110,80,&b);finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);op_asset(k)->rgba[128]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);}
 for(unsigned cached=0;cached<2;cached++){enemy70_setup();op_valid(cached?3:0,110,80,&b);if(cached){finish();CHECK(ready);}livebank[7684]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);}
}
static void op_old_atomic2(void)
{
 for(unsigned missing=0;missing<2;missing++) {
  enemy70_setup();char bad[1200],good[1200];int n=snprintf(bad,sizeof(bad),"%s/legacy-missing%u",op_pack,112+missing);CHECK(n>0&&(size_t)n<sizeof(bad));n=snprintf(good,sizeof(good),"%s/legacy-valid",op_pack);CHECK(n>0&&(size_t)n<sizeof(good));
  const char *saved=game_probe_assets;game_probe_assets=bad;CHECK(!enemy_orb112113_family_ready()&&enemy_orb112113_resources.checked&&!enemy_orb112113_resources.valid);CHECK(!enemy_orb112113_resources.members[0].rgba&&!enemy_orb112113_resources.members[1].rgba);
  CHECK(enemy_orb_protron_resource(valid_root,112)&&enemy_orb_protron_resource(valid_root,113));game_probe_assets=good;CHECK(!enemy_orb112113_family_ready());enemy_orb112113_shutdown();CHECK(enemy_orb112113_family_ready());CHECK(enemy_orb112113_resources.members[0].rgba&&enemy_orb112113_resources.members[1].rgba);enemy_orb112113_shutdown();game_probe_assets=saved;
 }
}
/* One genuinely retired227 cell, not a claim of whole-sprite handoff. This
 * specifically requires bit27 in the finite sparse-contributor guard. */
static void op_retired227_cell1(void)
{
 enemy70_setup();int x,y;enemy70_player_birth(&x,&y);PulsesBefore b;op_valid(3,x,y,&b);unsigned before[168]={0};
 CHECK(global_projectile91_used_members==134217728u);
 for(unsigned c=0;c<168;c++)for(unsigned n=0;n<64;n++){size_t z=(size_t)((y+c/12)*8+n/8)*2560+(x+c%12)*8+n%8;before[c]+=global_projectile91_owner[z]!=0;}
 enemy70_player_draw(x,y);finish();CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_projectile91_used_members==134217728u);
 bool found=false;
 for(unsigned c=0;c<168&&!found;c++) {
  unsigned shared=0,hd=0,player_owned=0;int gx=x+c%12,gy=y+c/12;
  for(unsigned n=0;n<64;n++){size_t z=(size_t)(gy*8+n/8)*2560+gx*8+n%8;shared+=global_projectile91_owner[z]!=0;hd+=hd_owner[z]!=0;player_owned+=global_vulcan_owner[z]!=0;}
  if(before[c]&&!shared&&hd&&player_owned){
   CHECK(global_projectile91_contributed&&global_vulcan_contributed&&global_projectile91_used_members==134217728u);
   Uint8 *p=(Uint8 *)VGAScreenSeg->pixels+gy*VGAScreenSeg->pitch+gx-24;*p=58;render_mirror_pixel(VGAScreenSeg,p,58,MIRROR_NORMAL);enemy70_declined();CHECK(*p==58);CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));enemy70_declined();found=true;
  }
 }
 CHECK(found);SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();op_valid(3,110,80,&b);finish();CHECK(ready&&last_output_valid&&global_projectile91_used_members==134217728u);op_oracle(3,110,80,&b,true);
}
static int op_main(int argc,char **argv)
{
 CHECK(argc==3&&!strcmp(argv[1],"--orb-protron"));op_pack=argv[2];static char root[1200];int n=snprintf(root,sizeof(root),"%s/valid",op_pack);CHECK(n>0&&(size_t)n<sizeof(root));valid_root=missing_root=root;
 read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));Uint32 count;read_exact(&count,4);CHECK(count==33484);spriteSheet9.size=count;spriteSheet9.data=malloc(count);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,count);Uint32 xn;read_exact(&xn,4);CHECK(xn==32404);Uint8 *xb=malloc(xn);CHECK(xb);read_exact(xb,xn);free(xb);read_exact(enemy70_record,80);read_exact(enemy70_port,82);CHECK(fgetc(stdin)==EOF);
 unsigned initial=cases,assertions=checks;op_direct28();op_faults16();op_phases6();op_palette8();op_background4();op_halos4();op_roots3();op_bits1();op_scope4();op_used_source6();op_old_atomic2();op_retired227_cell1();
 CHECK(cases-initial==83);printf("PASS Orb Protron ordinary OFF native: %u setup cases %u assertions; 28 current direct members; NOT gameplay or ON pixels\n",cases-initial,checks-assertions);return 0;
}
