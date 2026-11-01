/* Current macro-OFF ordinary qualification only. Legacy ON intent/routing is
 * a separate exact-source diagnostic, never claimed as ON pixel execution. */
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE
#error "widget-sonic ordinary matrix is pinned to macro OFF"
#endif
static const unsigned ws_ids[6]={20,21,105,106,124,125};
static const unsigned ws_cells[6]={31,41,97,97,85,85},ws_nonzero[6]={2299,3131,5728,5728,4169,4169};
static const unsigned ws_soft[6]={2299,3129,5417,5417,4116,4116},ws_halos[6]={332,507,286,286,218,218},ws_unions[6]={2316,3131,6494,6494,5658,5658};
static const char *ws_pack;
static Asset *ws_asset(unsigned k){CHECK(k<6);return &enemy_widget_sonic_resources[k].member;}
static void ws_draw(unsigned k,int x,int y){blue_draw_bank(ws_ids[k],x,y,spriteSheet8);}
static void ws_oracle(unsigned k,int x,int y,const PulsesBefore *b,bool final)
{
 Uint8 src[168],mask[168];blue_decode(ws_ids[k],src,mask);const Uint8 *a=ws_asset(k)->rgba;CHECK(a);
 unsigned cells=0,nz=0,soft=0,halo=0,un=0;for(unsigned c=0;c<168;c++)cells+=mask[c]!=0;
 for(unsigned n=0;n<10752;n++) {
  unsigned c=n/96/8*12+n%96/8;const Uint8 *q=a+4*n;bool support=mask[c]||q[3];nz+=q[3]!=0;soft+=q[3]>0&&q[3]<255;halo+=q[3]&&!mask[c];un+=support;
  int px=x*8+n%96,py=y*8+(int)(n/96);if(px<0||px>=2560||py<0||py>=1600)continue;size_t pos=(size_t)py*2560+px;
  Uint32 want=support?alpha(b->under[n],q):b->canvas[n];
  CHECK(((Uint8 *)game_screen->pixels)[py/8*320+px/8]==(mask[c]?src[c]:b->native[c]));
  if(support){CHECK(global_projectile91_owner[pos]&&hd_owner[pos]);CHECK(global_projectile91_used_members&(262144u<<k));}
  else CHECK(global_projectile91_owner[pos]==b->owned[n]);
  if(final){if(px<192||px>=2304||py>=1472)continue;CHECK(*at(output,px-192,py)==want);}else CHECK(*at(canvas,px,py)==want);
 }
 CHECK(cells==ws_cells[k]&&nz==ws_nonzero[k]&&soft==ws_soft[k]&&halo==ws_halos[k]&&un==ws_unions[k]);
}
static void ws_valid(unsigned k,int x,int y,PulsesBefore *b)
{pulses16694_snapshot(b,x,y);ws_draw(k,x,y);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);CHECK(global_projectile91_used_members&(262144u<<k));bolts745_callbacks_seen(ws_ids[k],x,y);ws_oracle(k,x,y,b,false);}
static unsigned ws_halo(unsigned k)
{Uint8 src[168],mask[168];blue_decode(ws_ids[k],src,mask);for(unsigned n=0;n<10752;n++)if(!mask[n/96/8*12+n%96/8]&&ws_asset(k)->rgba[n*4+3]>0&&ws_asset(k)->rgba[n*4+3]<255)return n;CHECK(false);return 0;}
static void ws_retire(unsigned k,int x,int y)
{
 Uint8 src[168],mask[168];blue_decode(ws_ids[k],src,mask);
 for(unsigned c=0;c<168;c++) {bool support=mask[c]!=0;
  for(unsigned n=0;n<64;n++)support|=ws_asset(k)->rgba[4*((c/12*8+n/8)*96+c%12*8+n%8)+3]!=0;
  if(support){Uint8 *p=(Uint8 *)game_screen->pixels+(y+c/12)*game_screen->pitch+x+c%12;*p=58;render_mirror_pixel(game_screen,p,58,MIRROR_NORMAL);}
 }
 for(unsigned n=0;n<10752;n++)CHECK(!global_projectile91_owner[(size_t)(y*8+n/96)*2560+x*8+n%96]);
 CHECK(global_projectile91_contributed&&(global_projectile91_used_members&(262144u<<k)));
}
static void ws_old18_draw(void)
{for(unsigned i=0;i<14;i++)bolts745_draw(bolts745_ids[i],30+(i%7)*35,20+(i/7)*45);for(unsigned i=0;i<3;i++)bolts745_draw(animated153_ids[i],30+i*35,110);enemy70_draw(180,110);CHECK(global_projectile91_used_members==262143u);}
static void ws_direct24(void)
{
 enemy70_old17();enemy70_setup();PulsesBefore b;enemy70_valid(110,80,&b);finish();CHECK(ready&&last_output_valid);enemy70_oracle(110,80,&b,true);
 for(unsigned k=0;k<6;k++){enemy70_setup();ws_valid(k,110,80,&b);CHECK(global_projectile91_used_members==(262144u<<k));finish();CHECK(ready&&last_output_valid);ws_oracle(k,110,80,&b,true);}
}
static void ws_faults30(void)
{
 const char *saved=valid_root;char path[1200];PulsesBefore b;
 for(unsigned k=0;k<6;k++)for(unsigned mode=0;mode<5;mode++) {
  if(mode<2||mode==4){const char *kind=mode==0?"missing":mode==1?"bad":"header";int n=snprintf(path,sizeof(path),"%s/%s%u",ws_pack,kind,ws_ids[k]);CHECK(n>0&&(size_t)n<sizeof(path));valid_root=path;}
  else valid_root=saved;
  enemy70_setup();
  if(mode==0){ws_old18_draw();for(unsigned j=0;j<6;j++)if(j!=k)ws_draw(j,40+j*32,150);}
  if(mode<2||mode==4){ws_draw(k,220,80);CHECK(!(global_projectile91_used_members&(262144u<<k))&&!global_projectile91_fault);finish();if(mode==0)CHECK(ready&&last_output_valid&&global_projectile91_used_members==(16777215u^(262144u<<k)));else CHECK(!ready&&!last_output_valid);}
  else {ws_valid(k,110,80,&b);if(mode==3){enemy70_draw(30,30);ws_retire(k,110,80);}finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);ws_asset(k)->rgba[128]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);}
 }
 valid_root=saved;
}
static void ws_geometry2(void)
{
 const char *saved=valid_root;char root[1200];const char *leaves[]={"width20","density105"};unsigned ids[]={0,2};
 for(unsigned m=0;m<2;m++){int n=snprintf(root,sizeof(root),"%s/%s",ws_pack,leaves[m]);CHECK(n>0&&(size_t)n<sizeof(root));valid_root=root;enemy70_setup();ws_draw(ids[m],110,80);CHECK(!global_projectile91_contributed);finish();CHECK(!ready);}
 valid_root=saved;
}
static void ws_palette_source6(void)
{
 PulsesBefore b;
 for(unsigned family=0;family<2;family++)for(unsigned used=0;used<2;used++) {
  enemy70_setup();unsigned k=family?2:0;ws_valid(k,110,80,&b);rgb_palette[used?(family?194:118):250]^=1;finish();
  if(used)CHECK(!ready&&!last_output_valid);else {CHECK(ready&&last_output_valid);ws_oracle(k,110,80,&b,true);}
 }
 for(unsigned cached=0;cached<2;cached++){enemy70_setup();ws_valid(cached?2:0,110,80,&b);if(cached){finish();CHECK(ready);}livebank[7684]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);}
}
static void ws_background4(void)
{
 for(unsigned m=0;m<4;m++) {
  enemy70_setup();unsigned k=m%2?2:0;PulsesBefore b;ws_valid(k,110,80,&b);unsigned h=ws_halo(k);CHECK(global_projectile91_used_colors[27]);CHECK(*at(canvas,880+h%96,640+h/96)==alpha(0xff000000u|(rgb_palette[27]&0xffffffu),ws_asset(k)->rgba+h*4));
  if(m==1||m==3){enemy70_draw(30,30);ws_retire(k,110,80);}if(m>=2){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);}
  rgb_palette[27]^=1;if(m>=2)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
  SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();ws_valid(k,110,80,&b);finish();CHECK(ready);ws_oracle(k,110,80,&b,true);
 }
}
static void ws_overlap3(void)
{
 for(unsigned m=0;m<3;m++) {
  enemy70_setup();PulsesBefore b;unsigned last=0;int x=110,y=80;
  for(unsigned j=0;j<(m==0?6u:4u);j++){last=m==0?j:2+j;x=m==1?100+(j%2)*12:110;y=m==1?60+(j/2)*14:80;ws_valid(last,x,y,&b);}
  finish();CHECK(ready&&last_output_valid);ws_oracle(last,x,y,&b,true);
  CHECK((global_projectile91_used_members&16515072u)==(m==0?16515072u:15728640u));
 }
}
/* Direct shared hook snapshot is exact; later public family observers may retire
 * their own texels, but cannot re-enable a declined cached presentation. */
static void ws_final_decline(int gx,int gy,const Uint32 *restore,bool direct)
{
 Uint32 cv[64],out[64],fade[64];Uint8 own[64],hd[64];bool saved=have_fade_saved;unsigned cell=gy*320+gx-24;Uint8 oldindex=last_output_indices[cell];
 CHECK(ready&&last_output_valid&&global_projectile91_cached);
 for(unsigned n=0;n<64;n++){int px=gx*8+n%8,py=gy*8+n/8;size_t p=(size_t)py*2560+px;cv[n]=*at(canvas,px,py);out[n]=*at(output,px-192,py);own[n]=global_projectile91_owner[p];hd[n]=hd_owner[p];if(saved)fade[n]=*at(fade_saved,px-192,py);}
 Uint8 *p=(Uint8 *)VGAScreenSeg->pixels+gy*VGAScreenSeg->pitch+gx-24;*p=58;
 if(direct){global_projectile91_final_pixel(VGAScreenSeg,p);enemy70_declined();CHECK(last_output_indices[cell]==oldindex);
  for(unsigned n=0;n<64;n++){int px=gx*8+n%8,py=gy*8+n/8;size_t z=(size_t)py*2560+px;CHECK(*at(canvas,px,py)==cv[n]&&*at(output,px-192,py)==out[n]);CHECK(global_projectile91_owner[z]==own[n]&&hd_owner[z]==hd[n]);if(saved)CHECK(*at(fade_saved,px-192,py)==fade[n]);}}
 render_mirror_pixel(VGAScreenSeg,p,58,MIRROR_NORMAL);enemy70_declined();CHECK(*p==58);CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));enemy70_declined();
 if(restore)memcpy(rgb_palette,restore,sizeof(rgb_palette));SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();PulsesBefore b;ws_valid(0,110,80,&b);finish();CHECK(ready&&last_output_valid);ws_oracle(0,110,80,&b,true);
}
static void ws_sparse4(void)
{
 for(unsigned m=0;m<4;m++) {
  enemy70_setup();PulsesBefore b;int x=110,y=80;
  if(m>=2)enemy70_player_birth(&x,&y);
  int player_x=x;if(m==2)--x;
  unsigned k=m==0?0:2;ws_valid(k,x,y,&b);
  if(m>=2)enemy70_player_draw(player_x,y);
  finish();CHECK(ready&&last_output_valid);
  Uint32 restore[256];
  if(m==1){memcpy(restore,rgb_palette,sizeof(restore));SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(!ready&&last_output_valid&&have_fade_saved);
   for(unsigned i=0;i<256;i++){Uint32 old=rgb_palette[i],next=old&0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}rgb_palette[i]=next;}render_mirror_fade_step(7);CHECK(ready&&last_output_valid&&have_fade_saved&&fade_mode==1);}
  bool found=false;
  for(unsigned c=0;c<168&&!found;c++){unsigned shared=0,player_owned=0;int gx=x+c%12,gy=y+c/12;
   for(unsigned n=0;n<64;n++){size_t z=(size_t)(gy*8+n/8)*2560+gx*8+n%8;shared+=global_projectile91_owner[z]!=0;player_owned+=global_vulcan_owner[z]!=0;}
   if(m<2?(shared&&shared<64):m==2?(shared&&shared<64&&player_owned):(!shared&&player_owned)){ws_final_decline(gx,gy,m==1?restore:NULL,m<2);found=true;}}
  CHECK(found);
 }
}
static void ws_roots3(void)
{
 char bad[1200];int n=snprintf(bad,sizeof(bad),"%s/missing20",ws_pack);CHECK(n>0&&(size_t)n<sizeof(bad));
 enemy70_setup();Asset *a=enemy_widget_sonic_resource(valid_root,20);CHECK(a);Uint8 *p=a->rgba;CHECK(enemy_widget_sonic_resource(valid_root,20)==a&&a->rgba==p);CHECK(!enemy_widget_sonic_resource(bad,20));CHECK(enemy_widget_sonic_resource(valid_root,20)==a&&a->rgba==p);
 enemy70_setup();CHECK(!enemy_widget_sonic_resource(bad,20));CHECK(!enemy_widget_sonic_resource(valid_root,20));enemy_widget_sonic_shutdown();CHECK(enemy_widget_sonic_resource(valid_root,20));
 enemy70_setup();int x,y;enemy70_player_birth(&x,&y);enemy70_player_draw(x,y);p=global_vulcan_rgba[1];CHECK(p);CHECK(enemy_widget_sonic_resource(valid_root,20));enemy_widget_sonic_shutdown();CHECK(global_vulcan_rgba[1]==p&&asteroid1_stamp(p,43008)==UINT64_C(0x6c26e938d94472c2));finish();CHECK(ready&&last_output_valid);
}
static void ws_scope4(void)
{
 PulsesBefore b;enemy70_setup();ws_valid(0,110,-6,&b);finish();CHECK(ready);ws_oracle(0,110,-6,&b,true);
 enemy70_setup();xmas=true;ws_draw(0,110,80);CHECK(!global_projectile91_contributed);
 enemy70_setup();game_probe_density=4;ws_draw(2,110,80);CHECK(!global_projectile91_contributed);
 enemy70_setup();ws_valid(2,110,80,&b);final_copy();render_mirror_finish(MIRROR_OUTPUT_UNSUPPORTED,0,0);CHECK(!ready&&!last_output_valid);
}
static void ws_off_extras6(void)
{
 PulsesBefore b;enemy70_setup();ws_old18_draw();for(unsigned k=0;k<6;k++)ws_draw(k,30+k*35,150);CHECK(global_projectile91_used_members==16777215u);finish();CHECK(ready&&last_output_valid);
 enemy70_setup();ws_valid(0,110,80,&b);ws_valid(0,110,80,&b);finish();CHECK(ready);ws_oracle(0,110,80,&b,true);SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();ws_valid(0,110,80,&b);finish();CHECK(ready);ws_oracle(0,110,80,&b,true);
 for(unsigned cached=0;cached<2;cached++){enemy70_setup();ws_valid(cached?2:0,110,80,&b);if(cached){finish();CHECK(ready);}if(cached)ws_asset(2)->w=11;else ws_asset(0)->index=21;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);}
 enemy70_setup();CHECK(enemy_widget_sonic_resource(valid_root,20));ws_asset(0)->rgba[128]^=1;ws_old18_draw();finish();CHECK(ready&&last_output_valid&&global_projectile91_used_members==262143u);
 enemy70_setup();game_probe_enabled=true;CHECK(!widget_sonic_legacy_intent());ws_valid(0,110,80,&b);finish();CHECK(ready&&last_output_valid);ws_oracle(0,110,80,&b,true);
}
static int ws_main(int argc,char **argv)
{
 CHECK(argc==3&&!strcmp(argv[1],"--widget-sonic"));ws_pack=argv[2];static char root[1200];int n=snprintf(root,sizeof(root),"%s/valid",ws_pack);CHECK(n>0&&(size_t)n<sizeof(root));valid_root=missing_root=root;
 read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));Uint32 count;read_exact(&count,4);CHECK(count==33484);spriteSheet9.size=count;spriteSheet9.data=malloc(count);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,count);Uint32 xn;read_exact(&xn,4);CHECK(xn==32404);Uint8 *xb=malloc(xn);CHECK(xb);read_exact(xb,xn);free(xb);read_exact(enemy70_record,80);read_exact(enemy70_port,82);CHECK(fgetc(stdin)==EOF);
 unsigned initial=cases,assertions=checks;ws_direct24();ws_faults30();ws_geometry2();ws_palette_source6();ws_background4();ws_overlap3();ws_sparse4();ws_roots3();ws_scope4();ws_off_extras6();
 CHECK(cases-initial==86);printf("PASS Widget Sonic ordinary OFF native: %u setup cases %u assertions; 24 current direct members; NOT gameplay or ON pixels\n",cases-initial,checks-assertions);return 0;
}
