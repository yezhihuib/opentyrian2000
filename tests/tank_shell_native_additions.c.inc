/* Finite ordinary macro-OFF native companion. No gameplay/ON-pixels claim.
 * Explicit --tank-shared retains 31 direct / 75 setups.
 * --tank-energy runs changed 2 direct + 44 focused only. No historical fault dispatch. */
static const unsigned tk_ids[2]={146,147};
static const unsigned tk_cells[2]={39,39},tk_nonzero[2]={1487,1855},tk_soft[2]={1487,1855},tk_halos[2]={80,11},tk_unions[2]={2576,2507};
static const char *tk_pack;
static Asset *tk_asset(unsigned k){CHECK(k<2);return &enemy_tank_shared_resources[k].member;}
static void tk_draw(unsigned k,int x,int y){blue_draw_bank(tk_ids[k],x,y,spriteSheet8);}
static void tk_oracle(unsigned k,int x,int y,const PulsesBefore *b,bool final)
{
 Uint8 src[168],mask[168];blue_decode(tk_ids[k],src,mask);const Uint8 *a=tk_asset(k)->rgba;CHECK(a);
 unsigned cells=0,nz=0,soft=0,halo=0,un=0;for(unsigned c=0;c<168;c++)cells+=mask[c]!=0;
 for(unsigned n=0;n<10752;n++) {
  unsigned c=n/96/8*12+n%96/8;const Uint8 *q=a+4*n;bool support=mask[c]||q[3];nz+=q[3]!=0;soft+=q[3]>0&&q[3]<255;halo+=q[3]&&!mask[c];un+=support;
  int px=x*8+n%96,py=y*8+(int)(n/96);if(px<0||px>=2560||py<0||py>=1600)continue;size_t pos=(size_t)py*2560+px;
  Uint32 want=support?alpha(b->under[n],q):b->canvas[n];
  CHECK(((Uint8 *)game_screen->pixels)[py/8*320+px/8]==(mask[c]?src[c]:b->native[c]));
  if(support){CHECK(global_projectile91_owner[pos]&&hd_owner[pos]);CHECK(global_projectile91_used_members&(536870912u<<k));}
  else CHECK(global_projectile91_owner[pos]==b->owned[n]);
  if(final){if(px<192||px>=2304||py>=1472)continue;CHECK(*at(output,px-192,py)==want);}else CHECK(*at(canvas,px,py)==want);
 }
 CHECK(cells==tk_cells[k]&&nz==tk_nonzero[k]&&soft==tk_soft[k]&&halo==tk_halos[k]&&un==tk_unions[k]);
}
static void tk_valid(unsigned k,int x,int y,PulsesBefore *b)
{pulses16694_snapshot(b,x,y);tk_draw(k,x,y);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);CHECK(global_projectile91_used_members&(536870912u<<k));bolts745_callbacks_seen(tk_ids[k],x,y);tk_oracle(k,x,y,b,false);}
static void tk_clear_begin(void){SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();}
static void tk_recover(unsigned k,int x,int y){PulsesBefore b;tk_clear_begin();tk_valid(k,x,y,&b);finish();CHECK(ready&&last_output_valid);tk_oracle(k,x,y,&b,true);}
static void tk_retire(unsigned k,int x,int y)
{
 Uint8 src[168],mask[168];blue_decode(tk_ids[k],src,mask);
 for(unsigned c=0;c<168;c++){bool yes=mask[c]!=0;for(unsigned n=0;n<64;n++)yes|=tk_asset(k)->rgba[4*((c/12*8+n/8)*96+c%12*8+n%8)+3]!=0;
  if(yes){Uint8 *p=(Uint8*)game_screen->pixels+(y+c/12)*320+x+c%12;*p=58;render_mirror_pixel(game_screen,p,58,MIRROR_NORMAL);}}
 for(unsigned n=0;n<10752;n++)CHECK(!global_projectile91_owner[(size_t)(y*8+n/96)*2560+x*8+n%96]);
 CHECK(global_projectile91_contributed&&(global_projectile91_used_members&(536870912u<<k)));
}
static void tk_old29(void){p244_old28_draw();p244_draw(0,220,80);CHECK(global_projectile91_used_members==536870911u);}
static void tk_direct2(void)
{for(unsigned k=0;k<2;k++){enemy70_setup();PulsesBefore b;tk_valid(k,110,80,&b);CHECK(global_projectile91_used_members==(536870912u<<k));finish();CHECK(ready&&last_output_valid);tk_oracle(k,110,80,&b,true);}}
static void tk_direct31(void){p244_direct29();tk_direct2();}
static void tk_files6(void)
{
 const char *saved=valid_root;const char *kind[] = {"missing","bad","header"};char path[1200];
 for(unsigned k=0;k<2;k++)for(unsigned m=0;m<3;m++){int n=snprintf(path,sizeof(path),"%s/%s%u",tk_pack,kind[m],tk_ids[k]);CHECK(n>0&&(size_t)n<sizeof(path));valid_root=path;enemy70_setup();tk_draw(k,110,80);CHECK(!global_projectile91_used_members&&!global_projectile91_fault&&!enemy_tank_shell_checked);PulsesBefore b;tk_valid(1-k,160,80,&b);CHECK(global_projectile91_used_members==(536870912u<<(1-k)));finish();CHECK(ready&&last_output_valid);tk_oracle(1-k,160,80,&b,true);}
 valid_root=saved;
}
static void tk_warm4(void)
{for(unsigned k=0;k<2;k++)for(unsigned cached=0;cached<2;cached++){enemy70_setup();PulsesBefore b;tk_valid(k,110,80,&b);if(cached){finish();CHECK(ready);}if(cached)tk_asset(k)->w=11;else tk_asset(k)->bank=8;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);}}
static unsigned tk_source_byte(unsigned k)
{unsigned p=livebank[(tk_ids[k]-1)*2]|(unsigned)livebank[(tk_ids[k]-1)*2+1]<<8;while(p<sizeof(livebank)){unsigned q=livebank[p++];CHECK(q!=15);if(q>>4)return p;}CHECK(false);return 0;}
static void tk_source2(void)
{for(unsigned k=0;k<2;k++){enemy70_setup();PulsesBefore b;tk_valid(k,110,80,&b);if(k){finish();CHECK(ready);}livebank[tk_source_byte(k)]^=1;if(k)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);}}
static void tk_palette4(void)
{
 for(unsigned k=0;k<2;k++)for(unsigned unused=0;unused<2;unused++){enemy70_setup();PulsesBefore b;tk_valid(k,110,80,&b);rgb_palette[unused?250:49]^=1;finish();if(!unused)CHECK(!ready&&!last_output_valid);else{CHECK(ready&&last_output_valid);tk_oracle(k,110,80,&b,true);rgb_palette[250]^=2;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);}}
}
static void tk_unused2(void)
{for(unsigned k=0;k<2;k++){enemy70_setup();CHECK(enemy_tank_shared_resource(valid_root,tk_ids[k]));tk_asset(k)->rgba[128]^=1;tk_old29();PulsesBefore b;tk_valid(1-k,240,130,&b);finish();CHECK(ready&&last_output_valid&&global_projectile91_used_members==(536870911u|(536870912u<<(1-k))));tk_oracle(1-k,240,130,&b,true);}}
static void tk_retired_resource2(void)
{for(unsigned k=0;k<2;k++){enemy70_setup();PulsesBefore b;tk_valid(k,110,80,&b);enemy70_draw(30,30);tk_retire(k,110,80);finish();CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_projectile91_used_members==((536870912u<<k)|131072u));tk_asset(k)->rgba[128]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);}}
static void tk_repeat3(void)
{
 for(unsigned k=0;k<2;k++){enemy70_setup();PulsesBefore b;tk_valid(k,110,80,&b);tk_valid(k,110,80,&b);finish();CHECK(ready&&last_output_valid);tk_oracle(k,110,80,&b,true);tk_recover(k,110,80);}
 enemy70_setup();PulsesBefore b;tk_valid(0,110,80,&b);tk_valid(1,110,80,&b);CHECK(global_projectile91_used_members==1610612736u);finish();CHECK(ready&&last_output_valid);tk_oracle(1,110,80,&b,true);tk_recover(0,110,80);CHECK(global_projectile91_used_members==536870912u);
}
static void tk_roots2(void)
{
 for(unsigned k=0;k<2;k++){enemy70_setup();int x,y;enemy70_player_birth(&x,&y);enemy70_player_draw(x,y);const Uint8 *player_payload=global_vulcan_rgba[1];CHECK(player_payload);char bad[1200];int n=snprintf(bad,sizeof(bad),"%s/missing%u",tk_pack,tk_ids[k]);CHECK(n>0&&(size_t)n<sizeof(bad));
  Asset *a=enemy_tank_shared_resource(valid_root,tk_ids[k]);CHECK(a);Uint8 *ptr=a->rgba;CHECK(enemy_tank_shared_resource(valid_root,tk_ids[k])==a&&a->rgba==ptr);CHECK(!enemy_tank_shared_resource(bad,tk_ids[k]));CHECK(enemy_tank_shared_resource(valid_root,tk_ids[k])==a&&a->rgba==ptr);
  enemy_tank_shared_shutdown();CHECK(!enemy_tank_shared_resource(bad,tk_ids[k])&&!enemy_tank_shared_resource(valid_root,tk_ids[k]));CHECK(enemy_tank_shared_resource(valid_root,tk_ids[1-k]));enemy_tank_shared_shutdown();CHECK(enemy_tank_shared_resource(valid_root,tk_ids[k]));CHECK(global_vulcan_rgba[1]==player_payload&&asteroid1_stamp(player_payload,43008)==UINT64_C(0x6c26e938d94472c2));finish();CHECK(ready&&last_output_valid);
 }
}
static void tk_background4(void)
{
 for(unsigned mode=0;mode<4;mode++){unsigned k=mode%2;enemy70_setup();PulsesBefore b;tk_valid(k,110,80,&b);Uint8 src[168],mask[168];blue_decode(tk_ids[k],src,mask);unsigned zero=10752,soft=10752;
  for(unsigned n=0;n<10752;n++){unsigned a=tk_asset(k)->rgba[4*n+3];if(mask[n/96/8*12+n%96/8]&&!a)zero=n;if(a>0&&a<255&&!mask[n/96/8*12+n%96/8])soft=n;}
  CHECK(zero<10752&&soft<10752&&global_projectile91_used_colors[27]);CHECK(*at(canvas,880+zero%96,640+zero/96)==(0xff000000u|(rgb_palette[27]&0xffffffu)));CHECK(*at(canvas,880+soft%96,640+soft/96)==alpha(0xff000000u|(rgb_palette[27]&0xffffffu),tk_asset(k)->rgba+4*soft));
  if(mode==1||mode==3){enemy70_draw(30,30);tk_retire(k,110,80);}if(mode>=2){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);}rgb_palette[27]^=1;if(mode>=2)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);tk_recover(k,110,80);
 }
}
/* Independently prechecked current alpha+caller original native support:
 * 146 cell28(shared2) -> Green214 cell8(22), origin offset (+4,-2).
 * 147 cell39(native full64) -> Green214 cell15(native full64), offset (0,-2).
 * 147 has11 halo texels, but THIS selected full-native cell exercises the
 * conservative used-bit30 retired-cell branch, not a halo-cell retirement.
 * Both members separately exercise fractional halo background dependencies.
 * Real allocator/move+draw owns retirement; no fabricated owner bits. */
static void tk_green8(void)
{
 const unsigned tc[2]={28,39},gcells[2]={8,15},before_count[2]={2,64},after_count[2]={22,64};
 for(unsigned k=0;k<2;k++)for(unsigned mode=0;mode<4;mode++){
  pg_record(71,pg_records[0]);pg_record(1071,pg_records[1]);enemy70_setup();CHECK(global_green_source_matches(spriteSheet8)&&global_green_palette_matches());int x,y;pg_birth(&x,&y);
  int gx=x+gcells[k]%12,gy=y+gcells[k]/12,ex=gx-tc[k]%12,ey=gy-tc[k]/12;PulsesBefore b;tk_valid(k,ex,ey,&b);unsigned sc,gc,hc;pg_counts(gx,gy,&sc,&gc,&hc);CHECK(sc==before_count[k]&&hc==sc&&!gc);CHECK(global_green_family_ready());
  Uint32 under[64];for(unsigned j=0;j<64;j++){size_t n=(size_t)(gy*8+j/8)*2560+gx*8+j%8;under[j]=hd_owner[n]?*at(canvas,gx*8+j%8,gy*8+j/8):(0xff000000u|(rgb_palette[27]&0xffffffu));}
  bool special=false;int sx=0,sy=0;JE_integer damage=0;JE_byte blast=0,chain=0,pnum=0;JE_word rw=0,rh=0;
  CHECK(player_shot_move_and_draw(0,&special,&sx,&sy,&damage,&blast,&chain,&pnum,&rw,&rh));CHECK(!special&&sx+1==x&&sy==y&&pnum==1&&global_green_contributed&&!global_green_fault&&!global_green_identity_fault);
  pg_counts(gx,gy,&sc,&gc,&hc);CHECK(!sc&&gc==after_count[k]&&hc==gc);CHECK(global_projectile91_used_members==(536870912u<<k));finish();CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_green_cached);
  for(unsigned j=0;j<64;j++){const Uint8 *a=global_green_rgba[0]+4*((gcells[k]/12*8+j/8)*96+gcells[k]%12*8+j%8);CHECK(*at(output,(gx-24)*8+j%8,gy*8+j/8)==alpha(under[j],a));}
  Uint32 restore[256];memcpy(restore,rgb_palette,sizeof(restore));if(mode>=2){SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);for(unsigned i=0;i<256;i++){Uint32 c=rgb_palette[i],v=0;for(unsigned sh=0;sh<24;sh+=8){int q=(c>>sh)&255;q+=(0-q)/7;v|=(Uint32)q<<sh;}rgb_palette[i]=v;}render_mirror_fade_step(7);CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_green_cached&&have_fade_saved);}
  pg_counts(gx,gy,&sc,&gc,&hc);CHECK(!sc&&hc==after_count[k]);Uint8 *p=(Uint8*)VGAScreenSeg->pixels+gy*320+gx-24;*p=58;if(mode%2){SDL_Rect r={gx-24,gy,1,1};render_mirror_rect(VGAScreenSeg,&r);}else render_mirror_pixel(VGAScreenSeg,p,58,MIRROR_NORMAL);
  enemy70_declined();CHECK(*p==58);SDL_Surface *screen=SDL_CreateRGBSurfaceWithFormat(0,output->w,output->h,32,SDL_PIXELFORMAT_ARGB8888);CHECK(screen);SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(screen);CHECK(renderer);CHECK(!render_mirror_present(renderer,VGAScreenSeg,NULL));enemy70_declined();if(texture){SDL_DestroyTexture(texture);texture=NULL;}SDL_DestroyRenderer(renderer);SDL_FreeSurface(screen);
  SDL_Color colors[256];for(unsigned i=0;i<256;i++)colors[i]=(SDL_Color){(rgb_palette[i]>>16)&255,(rgb_palette[i]>>8)&255,rgb_palette[i]&255,255};CHECK(SDL_SetPaletteColors(VGAScreenSeg->format->palette,colors,0,256)==0);SDL_Surface *native=SDL_ConvertSurfaceFormat(VGAScreenSeg,SDL_PIXELFORMAT_ARGB8888,0),*cell=SDL_CreateRGBSurfaceWithFormat(0,8,8,32,SDL_PIXELFORMAT_ARGB8888);CHECK(native&&cell);SDL_Rect r={gx-24,gy,1,1};CHECK(SDL_BlitScaled(native,&r,cell,NULL)==0);for(unsigned j=0;j<64;j++)CHECK(*at(cell,j%8,j/8)==(0xff000000u|(rgb_palette[58]&0xffffffu)));SDL_FreeSurface(cell);SDL_FreeSurface(native);
  memcpy(rgb_palette,restore,sizeof(restore));tk_recover(k,ex,ey);CHECK(global_projectile91_used_members==(536870912u<<k));
 }
}
static void tk_bits1(void)
{enemy70_setup();tk_old29();tk_draw(0,60,130);tk_draw(1,160,130);CHECK(global_projectile91_member(146)==536870912u&&global_projectile91_member(147)==1073741824u&&global_projectile91_used_members==2147483647u);CHECK((global_projectile91_sparse_rgba_members&1610612736u)==1610612736u&&(global_projectile91_sparse_rgba_members&536870911u)==150863872u);finish();CHECK(ready&&last_output_valid);}
static void tk_scope2(void)
{enemy70_setup();PulsesBefore b;tk_valid(0,110,-6,&b);finish();CHECK(ready&&last_output_valid);tk_oracle(0,110,-6,&b,true);enemy70_setup();game_probe_density=4;tk_draw(1,110,80);CHECK(!global_projectile91_contributed&&!global_projectile91_used_members);}
static int tk_main(int argc,char **argv)
{
 CHECK(argc==3&&(!strcmp(argv[1],"--tank-shared")||!strcmp(argv[1],"--tank-energy")));bool energy=!strcmp(argv[1],"--tank-energy");tk_pack=argv[2];static char root[1200];int n=snprintf(root,sizeof(root),"%s/valid",tk_pack);CHECK(n>0&&(size_t)n<sizeof(root));valid_root=missing_root=root;
 read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));Uint32 count;read_exact(&count,4);CHECK(count==33484);spriteSheet9.size=count;spriteSheet9.data=malloc(count);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,count);read_exact(&count,4);CHECK(count==32404);Uint8 *unused=malloc(count);CHECK(unused);read_exact(unused,count);free(unused);read_exact(enemy70_record,80);read_exact(enemy70_port,82);read_exact(pg_records,160);explosionSpriteSheet.size=17810;explosionSpriteSheet.data=malloc(17810);CHECK(explosionSpriteSheet.data);read_exact(explosionSpriteSheet.data,17810);CHECK(fgetc(stdin)==EOF);
 unsigned initial=cases,assertions=checks;if(energy)tk_direct2();else tk_direct31();tk_files6();tk_warm4();tk_source2();tk_palette4();tk_unused2();tk_retired_resource2();tk_repeat3();tk_roots2();tk_background4();tk_green8();tk_bits1();tk_scope2();for(unsigned m=0;m<4;m++)pg_case(m);
 if(energy){CHECK(cases-initial==46);printf("PASS Tank energy ordinary OFF native: 46 setup cases %u assertions; 2 changed direct members + 44 focused; prior29 direct/tiny NOT rerun; NOT gameplay or ON pixels\n",checks-assertions);return 0;}
 CHECK(cases-initial==75);printf("PASS Tank shared ordinary OFF native: 75 setup cases %u assertions; 31 current direct members; NOT gameplay or ON pixels\n",checks-assertions);return 0;
}
