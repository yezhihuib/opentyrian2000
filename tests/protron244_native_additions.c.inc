/* Current macro-OFF ordinary qualification only. Legacy ON intent/routing is
 * a separate exact-source diagnostic, never claimed as ON pixel execution. */
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE
#error "protron244 ordinary matrix is pinned to macro OFF"
#endif
static const unsigned p244_ids[1]={244};
static const unsigned p244_cells[1]={97},p244_nonzero[1]={6056};
static const unsigned p244_soft[1]={6056},p244_halos[1]={0},p244_unions[1]={6208};
static const char *p244_pack;
static Asset *p244_asset(unsigned k){CHECK(k==0);return &enemy_orb_protron_resources[4].member;}
static void p244_draw(unsigned k,int x,int y){blue_draw_bank(p244_ids[k],x,y,spriteSheet8);}
static void p244_oracle(unsigned k,int x,int y,const PulsesBefore *b,bool final)
{
 Uint8 src[168],mask[168];blue_decode(p244_ids[k],src,mask);const Uint8 *a=p244_asset(k)->rgba;CHECK(a);
 unsigned cells=0,nz=0,soft=0,halo=0,un=0;for(unsigned c=0;c<168;c++)cells+=mask[c]!=0;
 for(unsigned n=0;n<10752;n++) {
  unsigned c=n/96/8*12+n%96/8;const Uint8 *q=a+4*n;bool support=mask[c]||q[3];nz+=q[3]!=0;soft+=q[3]>0&&q[3]<255;halo+=q[3]&&!mask[c];un+=support;
  int px=x*8+n%96,py=y*8+(int)(n/96);if(px<0||px>=2560||py<0||py>=1600)continue;size_t pos=(size_t)py*2560+px;
  Uint32 want=support?alpha(b->under[n],q):b->canvas[n];
  CHECK(((Uint8 *)game_screen->pixels)[py/8*320+px/8]==(mask[c]?src[c]:b->native[c]));
  if(support){CHECK(global_projectile91_owner[pos]&&hd_owner[pos]);CHECK(global_projectile91_used_members&(268435456u<<k));}
  else CHECK(global_projectile91_owner[pos]==b->owned[n]);
  if(final){if(px<192||px>=2304||py>=1472)continue;CHECK(*at(output,px-192,py)==want);}else CHECK(*at(canvas,px,py)==want);
 }
 CHECK(cells==p244_cells[k]&&nz==p244_nonzero[k]&&soft==p244_soft[k]&&halo==p244_halos[k]&&un==p244_unions[k]);
}
static void p244_valid(unsigned k,int x,int y,PulsesBefore *b)
{pulses16694_snapshot(b,x,y);p244_draw(k,x,y);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);CHECK(global_projectile91_used_members&(268435456u<<k));bolts745_callbacks_seen(p244_ids[k],x,y);p244_oracle(k,x,y,b,false);}
static void p244_retire(unsigned k,int x,int y)
{
 Uint8 src[168],mask[168];blue_decode(p244_ids[k],src,mask);
 for(unsigned c=0;c<168;c++) {bool support=mask[c]!=0;
  for(unsigned n=0;n<64;n++)support|=p244_asset(k)->rgba[4*((c/12*8+n/8)*96+c%12*8+n%8)+3]!=0;
  if(support){Uint8 *p=(Uint8 *)game_screen->pixels+(y+c/12)*game_screen->pitch+x+c%12;*p=58;render_mirror_pixel(game_screen,p,58,MIRROR_NORMAL);}
 }
 for(unsigned n=0;n<10752;n++)CHECK(!global_projectile91_owner[(size_t)(y*8+n/96)*2560+x*8+n%96]);
 CHECK(global_projectile91_contributed&&(global_projectile91_used_members&(268435456u<<k)));
}
static void p244_old28_draw(void)
{op_old24_draw();for(unsigned k=0;k<4;k++)op_draw(k,40+k*40,70);CHECK(global_projectile91_used_members==268435455u);}
static void p244_direct29(void)
{op_direct28();enemy70_setup();PulsesBefore b;p244_valid(0,110,80,&b);CHECK(global_projectile91_used_members==268435456u);finish();CHECK(ready&&last_output_valid);p244_oracle(0,110,80,&b,true);}
static void p244_files3(void)
{
 const char *saved=valid_root;char path[1200];const char *kind[]={"missing244","bad244","header244"};
 for(unsigned m=0;m<3;m++){int n=snprintf(path,sizeof(path),"%s/%s",p244_pack,kind[m]);CHECK(n>0&&(size_t)n<sizeof(path));valid_root=path;enemy70_setup();if(!m)p244_old28_draw();p244_draw(0,220,80);CHECK(!(global_projectile91_used_members&268435456u)&&!global_projectile91_fault);finish();if(!m)CHECK(ready&&last_output_valid&&global_projectile91_used_members==268435455u);else CHECK(!ready&&!last_output_valid);}
 valid_root=saved;
}
static void p244_warm2(void)
{for(unsigned cached=0;cached<2;cached++){enemy70_setup();PulsesBefore b;p244_valid(0,110,80,&b);if(cached){finish();CHECK(ready);}if(cached)p244_asset(0)->w=11;else p244_asset(0)->index=227;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);}}
static void p244_roots2(void)
{
 char bad[1200];int n=snprintf(bad,sizeof(bad),"%s/missing244",p244_pack);CHECK(n>0&&(size_t)n<sizeof(bad));
 enemy70_setup();Asset *a=enemy_orb_protron_resource(valid_root,244);CHECK(a);Uint8 *ptr=a->rgba;CHECK(enemy_orb_protron_resource(valid_root,244)==a&&a->rgba==ptr);CHECK(!enemy_orb_protron_resource(bad,244));CHECK(enemy_orb_protron_resource(valid_root,244)==a&&a->rgba==ptr);
 enemy70_setup();int x,y;enemy70_player_birth(&x,&y);enemy70_player_draw(x,y);const Uint8 *player_payload=global_vulcan_rgba[1];CHECK(player_payload);CHECK(!enemy_orb_protron_resource(bad,244)&&!enemy_orb_protron_resource(valid_root,244));CHECK(enemy_orb_protron_resource(valid_root,227));enemy_orb_protron_shutdown();CHECK(enemy_orb_protron_resource(valid_root,244));CHECK(global_vulcan_rgba[1]==player_payload&&asteroid1_stamp(player_payload,43008)==UINT64_C(0x6c26e938d94472c2));finish();CHECK(ready&&last_output_valid);
}
static void p244_source2(void)
{for(unsigned cached=0;cached<2;cached++){enemy70_setup();PulsesBefore b;p244_valid(0,110,80,&b);if(cached){finish();CHECK(ready);}livebank[7684]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);}}
static void p244_palette3(void)
{
 for(unsigned m=0;m<3;m++){enemy70_setup();PulsesBefore b;p244_valid(0,110,80,&b);if(m==2){finish();CHECK(ready&&last_output_valid);}rgb_palette[m?250:128]^=1;if(m==2)global_projectile91_check_cache();else finish();if(m==1){CHECK(ready&&last_output_valid);p244_oracle(0,110,80,&b,true);}else CHECK(!ready&&!last_output_valid);}
}
static void p244_unused1(void)
{
 enemy70_setup();CHECK(enemy_orb_protron_resource(valid_root,244));p244_asset(0)->rgba[128]^=1;p244_old28_draw();finish();CHECK(ready&&last_output_valid&&global_projectile91_used_members==268435455u);
 /* A second frame in the same setup explicitly proves bit28 resource provenance
  * after full native retirement, with another legitimate HD owner retained. */
 SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();enemy_orb_protron_shutdown();PulsesBefore b;p244_valid(0,110,80,&b);enemy70_draw(30,30);p244_retire(0,110,80);finish();CHECK(ready&&last_output_valid&&global_projectile91_cached&&(global_projectile91_used_members&268435456u));p244_asset(0)->rgba[128]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
}
static void p244_repeat1(void)
{enemy70_setup();PulsesBefore b;p244_valid(0,110,80,&b);p244_valid(0,110,80,&b);finish();CHECK(ready);p244_oracle(0,110,80,&b,true);SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();p244_valid(0,110,80,&b);finish();CHECK(ready&&last_output_valid);p244_oracle(0,110,80,&b,true);}
static void p244_fade2(void)
{
 for(unsigned bad=0;bad<2;bad++){enemy70_setup();PulsesBefore b;p244_valid(0,110,80,&b);finish();CHECK(ready&&last_output_valid);SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(!ready&&last_output_valid&&have_fade_saved&&fade_mode==1&&global_projectile91_cached);
  if(bad){livebank[7684]^=1;CHECK(!global_projectile91_fade_step_valid(7));enemy70_declined();}
  else{for(unsigned i=0;i<256;i++){Uint32 old=rgb_palette[i],next=old&0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}rgb_palette[i]=next;}render_mirror_fade_step(7);CHECK(ready&&last_output_valid&&have_fade_saved);global_projectile91_check_cache();CHECK(ready&&last_output_valid);}
 }
}
static void p244_player2(void)
{
 for(unsigned order=0;order<2;order++){
  enemy70_setup();int x,y;enemy70_player_birth(&x,&y);PulsesBefore b;
  if(!order){enemy70_player_draw(x,y);p244_valid(0,x,y,&b);}else{p244_valid(0,x,y,&b);pulses16694_snapshot(&b,x,y);enemy70_player_draw(x,y);}
  CHECK(global_vulcan_contributed&&global_projectile91_contributed&&global_projectile91_used_members==268435456u);finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);
  if(!order)p244_oracle(0,x,y,&b,true);
  else{Uint8 src[168],mask[168];blue_decode(70,src,mask);for(unsigned n=0;n<10752;n++){unsigned c=n/96/8*12+n%96/8;const Uint8 *a=global_vulcan_rgba[1]+4*n;bool support=mask[c]||a[3];Uint32 want=support?alpha(b.under[n],a):b.canvas[n];CHECK(*at(output,x*8+n%96-192,y*8+n/96)==want);if(support){size_t z=(size_t)(y*8+n/96)*2560+x*8+n%96;CHECK(global_vulcan_owner[z]&&!global_projectile91_owner[z]);}}}
  if(order){p244_asset(0)->rgba[128]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);}else{weapons[227].sound^=1;global_vulcan_check_cache();CHECK(!ready&&!last_output_valid);}
 }
}
static void p244_final1(void)
{
 enemy70_setup();PulsesBefore b;p244_valid(0,110,80,&b);Uint8 src[168],mask[168];blue_decode(244,src,mask);unsigned c=0;while(c<168&&!mask[c])++c;CHECK(c<168);finish();CHECK(ready&&last_output_valid);
 int gx=110+c%12,gy=80+c/12;for(unsigned n=0;n<64;n++)CHECK(global_projectile91_owner[(size_t)(gy*8+n/8)*2560+gx*8+n%8]);
 Uint8 *p=(Uint8 *)VGAScreenSeg->pixels+gy*VGAScreenSeg->pitch+gx-24;*p=58;render_mirror_pixel(VGAScreenSeg,p,58,MIRROR_NORMAL);CHECK(ready&&last_output_valid&&global_projectile91_cached&&last_output_indices[gy*320+gx-24]==58);
 for(unsigned n=0;n<64;n++){CHECK(!global_projectile91_owner[(size_t)(gy*8+n/8)*2560+gx*8+n%8]);CHECK(*at(output,gx*8+n%8-192,gy*8+n/8)==(0xff000000u|(rgb_palette[58]&0xffffffu)));}
 SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();p244_valid(0,110,80,&b);finish();CHECK(ready&&last_output_valid);p244_oracle(0,110,80,&b,true);
}
static void p244_scope3(void)
{enemy70_setup();xmas=true;p244_draw(0,110,80);CHECK(!global_projectile91_contributed);enemy70_setup();game_probe_density=4;p244_draw(0,110,80);CHECK(!global_projectile91_contributed);enemy70_setup();PulsesBefore b;p244_valid(0,110,-6,&b);finish();CHECK(ready&&last_output_valid);p244_oracle(0,110,-6,&b,true);}
static void p244_bits1(void)
{enemy70_setup();p244_old28_draw();p244_draw(0,220,80);CHECK(global_projectile91_member(244)==268435456u&&global_projectile91_used_members==536870911u);CHECK(!(global_projectile91_sparse_rgba_members&268435456u));CHECK(global_projectile91_sparse_rgba_members==150863872u);CHECK(!global_projectile91_member(214)&&!global_projectile91_member(215)&&!global_projectile91_member(216));finish();CHECK(ready&&last_output_valid); /* each actual blue_draw helper compares full actors/shots/RNG: static244, not fabricated animation */}
static void p244_background4(void)
{
 for(unsigned m=0;m<4;m++){enemy70_setup();PulsesBefore b;p244_valid(0,110,80,&b);CHECK(global_projectile91_used_colors[27]);Uint8 src[168],mask[168];blue_decode(244,src,mask);unsigned zero=10752,soft=10752;
  for(unsigned n=0;n<10752;n++){unsigned a=p244_asset(0)->rgba[4*n+3];if(mask[n/96/8*12+n%96/8]&&!a)zero=n;if(a>0&&a<255)soft=n;}
  CHECK(zero<10752&&soft<10752);CHECK(*at(canvas,880+zero%96,640+zero/96)==(0xff000000u|(rgb_palette[27]&0xffffffu)));CHECK(*at(canvas,880+soft%96,640+soft/96)==alpha(0xff000000u|(rgb_palette[27]&0xffffffu),p244_asset(0)->rgba+4*soft));
  if(m==1||m==3){enemy70_draw(30,30);p244_retire(0,110,80);}if(m>=2){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);}rgb_palette[27]^=1;if(m>=2)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
  SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();p244_valid(0,110,80,&b);finish();CHECK(ready&&last_output_valid);p244_oracle(0,110,80,&b,true);
 }
}
static int p244_main(int argc,char **argv)
{
 CHECK(argc==3&&!strcmp(argv[1],"--protron244"));p244_pack=argv[2];static char root[1200];int n=snprintf(root,sizeof(root),"%s/valid",p244_pack);CHECK(n>0&&(size_t)n<sizeof(root));valid_root=missing_root=root;
 read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));Uint32 count;read_exact(&count,4);CHECK(count==33484);spriteSheet9.size=count;spriteSheet9.data=malloc(count);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,count);Uint32 xn;read_exact(&xn,4);CHECK(xn==32404);Uint8 *xb=malloc(xn);CHECK(xb);read_exact(xb,xn);free(xb);read_exact(enemy70_record,80);read_exact(enemy70_port,82);CHECK(fgetc(stdin)==EOF);
 unsigned initial=cases,assertions=checks;p244_direct29();p244_files3();p244_warm2();p244_roots2();p244_source2();p244_palette3();p244_unused1();p244_repeat1();p244_fade2();p244_player2();p244_final1();p244_scope3();p244_bits1();p244_background4();
 CHECK(cases-initial==56);printf("PASS Protron244 ordinary OFF native: %u setup cases %u assertions; 29 current direct members; NOT gameplay or ON pixels\n",cases-initial,checks-assertions);return 0;
}
