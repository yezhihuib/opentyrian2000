/* Isolated exact-source sidecar protocol + current real renderer. This is not
 * an execution of JE_drawEnemy/JE_main: their callsites are statically guarded
 * and independently exercised by the later actual scene. No owner fabrication. */
#include "fonthand.h"
static const char *mu_packs,*mu_hudroot;
static Uint8 mu_weapon[80],mu_bank20[46204],mu_pic3[64000];
typedef struct {Uint32 canvas[12480],under[12480];Uint8 native[195],shared[12480],hd[12480];} MuBefore;
static const Uint8 *mu_rgba(void){return tk_asset(1)->rgba;}
static const Uint8 *mu_sample(int ax,int iy)
{static const Uint8 zero[4]={0};return ax>=8&&ax<104&&iy<112?mu_rgba()+4*(iy*96+ax-8):zero;}
static void mu_snapshot(MuBefore *b,int x,int y)
{
 memset(b,0,sizeof(*b));
 for(int cy=0;cy<15;cy++)for(int cx=0;cx<13;cx++)b->native[cy*13+cx]=((Uint8*)game_screen->pixels)[(y-1+cy)*320+x+cx];
 for(int iy=0;iy<120;iy++)for(int ax=0;ax<104;ax++){unsigned i=iy*104+ax;int px=x*8+ax,py=(y-1)*8+iy;size_t n=(size_t)py*2560+px;b->canvas[i]=*at(canvas,px,py);b->shared[i]=global_projectile91_owner[n];b->hd[i]=hd_owner[n];b->under[i]=hd_owner[n]?b->canvas[i]:palette_rgb(b->native[iy/8*13+ax/8]);}
}
static void mu_oracle(int x,int y,const MuBefore *b,bool final)
{
 Uint8 src[168],mask[168];blue_decode(147,src,mask);unsigned native=0,alpha_count=0,halo=0,un=0,outside=0;
 for(int iy=0;iy<120;iy++)for(int ax=0;ax<104;ax++){
  unsigned i=iy*104+ax;int cy=iy/8-1,cx=ax/8;bool nat=ax<96&&cy>=0&&mask[cy*12+cx];const Uint8 *q=mu_sample(ax,iy);bool owned=nat||q[3];native+=nat;alpha_count+=!!q[3];halo+=!!q[3]&&!nat;un+=owned;outside+=!!q[3]&&(ax>=96||iy<8||iy>=120);
  int px=x*8+ax,py=(y-1)*8+iy;size_t n=(size_t)py*2560+px;Uint32 want=owned?alpha(b->under[i],q):b->canvas[i];
  CHECK(((Uint8*)game_screen->pixels)[(y-1+iy/8)*320+x+ax/8]==(nat?src[cy*12+cx]:b->native[iy/8*13+ax/8]));
  CHECK(global_projectile91_owner[n]==(owned?1:b->shared[i]));if(owned)CHECK(hd_owner[n]);
  CHECK(*at(final?output:canvas,px-(final?192:0),py)==want);
 }
 CHECK(native==2496&&alpha_count==1855&&halo==804&&un==3300&&outside==103);
 CHECK(global_projectile91_used_members==1073741824u&&!global_projectile91_call.live&&!global_projectile91_fault);
}
static void mu_setup(void)
{enemy70_setup();mu_level_reset();pg_record(3,mu_weapon);enemySpriteSheets[0]=(Sprite2_array){sizeof(mu_bank20),mu_bank20};enemySpriteSheetIds[0]=20;}
static void mu_birth(int x,int y,unsigned actor_type,unsigned weapon)
{
 memset(&enemyShot[0],0,sizeof(enemyShot[0]));enemyShotAvail[0]=false;enemy[0].enemytype=actor_type;enemy[0].size=1;enemy[0].enemycycle=1;enemy[0].egr[0]=93;enemy[0].sprite2s=&enemySpriteSheets[0];
 enemyShot[0].sx=x-3;enemyShot[0].sy=y-3;enemyShot[0].sgr=147;enemyShot[0].sxm=enemyShot[0].sym=3;enemyShot[0].duration=255;
 tank_muzzle_allocate(0);tank_muzzle_birth(0,0,weapon,2,0);enemyShot[0].sx+=3;enemyShot[0].sy+=3;--enemyShot[0].duration;
}
static void mu_draw_checked(void)
{
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
 EnemyShotType shots[ENEMY_SHOT_MAX];JE_MultiEnemyType actors;memcpy(shots,enemyShot,sizeof(shots));memcpy(actors,enemy,sizeof(actors));uint64_t rng=mt_state_fingerprint();unsigned sprite=enemyShot[0].sgr+enemyShot[0].animate;
 blit_sprite2(classic,enemyShot[0].sx,enemyShot[0].sy,spriteSheet8,sprite);mu_actual_route(0);
 CHECK(!memcmp(classic->pixels,game_screen->pixels,64000)&&!memcmp(shots,enemyShot,sizeof(shots))&&!memcmp(actors,enemy,sizeof(actors))&&rng==mt_state_fingerprint());SDL_FreeSurface(classic);
}
static void mu_valid(int x,int y,MuBefore *b){mu_snapshot(b,x,y);mu_draw_checked();mu_oracle(x,y,b,false);}
static void mu_recover(int x,int y)
{SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();mu_birth(x,y,194,3);MuBefore b;mu_valid(x,y,&b);finish();CHECK(ready&&last_output_valid);mu_oracle(x,y,&b,true);}
/* Full native-only suppression remains a complete shared cell: unlike sparse
 * halo retirement, this existing path must patch all 64 cached samples. */
static void mu_native_only_write(int x,int y)
{
 Uint8 src[168],mask[168];blue_decode(147,src,mask);unsigned c=168;
 for(unsigned q=0;q<168;q++){if(!mask[q])continue;bool clear=true;for(unsigned j=0;j<64;j++)if(mu_sample((q%12)*8+j%8,(q/12+1)*8+j/8)[3])clear=false;if(clear){c=q;break;}}
 CHECK(c<168);int gx=x+c%12,gy=y+c/12;unsigned sc,gc,hc;pg_counts(gx,gy,&sc,&gc,&hc);CHECK(sc==64&&hc==64&&!gc&&ready&&last_output_valid&&global_projectile91_cached);
 Uint8 *p=(Uint8*)VGAScreenSeg->pixels+gy*320+gx-24;*p=58;render_mirror_pixel(VGAScreenSeg,p,58,MIRROR_NORMAL);CHECK(ready&&last_output_valid&&global_projectile91_cached);
 for(unsigned j=0;j<64;j++)CHECK(*at(output,(gx-24)*8+j%8,gy*8+j/8)==palette_rgb(58));
}
static void mu_direct5(void)
{
 mu_setup();mu_birth(110,80,194,3);MuBefore b;mu_valid(110,80,&b);mu_valid(110,80,&b);uint64_t gen=tank_muzzle_shots[0].generation;enemyShot[0].sx+=3;enemyShot[0].sy+=3;--enemyShot[0].duration;mu_valid(113,83,&b);CHECK(tank_muzzle_shots[0].generation==gen);finish();CHECK(ready&&last_output_valid);mu_oracle(113,83,&b,true);mu_native_only_write(113,83);mu_recover(110,80);
 const unsigned actors[3]={15,195,194},weapons_ids[3]={3,3,7};
 for(unsigned i=0;i<3;i++){mu_setup();mu_birth(110,80,actors[i],weapons_ids[i]);CHECK(!tank_muzzle_shots[0].valid&&tank_muzzle_draw(0,147)==0);PulsesBefore old;pulses16694_snapshot(&old,110,80);mu_draw_checked();tk_oracle(1,110,80,&old,false);finish();CHECK(ready&&last_output_valid);tk_oracle(1,110,80,&old,true);}
 mu_setup();PulsesBefore old,indexed;tk_valid(0,110,80,&old);bolts745_valid(7,160,80,&indexed);finish();CHECK(ready&&last_output_valid);tk_oracle(0,110,80,&old,true);bolts745_oracle(7,160,80,&indexed,true);
}
/* Finite permission negatives within the existing lifecycle setup; these are
 * actual extracted functions, not tiny diagnostic registration stubs. */
static void mu_sidecar_gate_table(void)
{
 for(unsigned k=0;k<4;k++){
  mu_birth(110,80,194,3);enemyShot[0].sx-=3;enemyShot[0].sy-=3;enemyShot[0].duration=255;tank_muzzle_allocate(0);
  if(k==0)enemySpriteSheetIds[0]=19;if(k==1)enemy[0].egr[0]=92;
  tank_muzzle_birth(0,0,3,k==2?1:2,k==3?1:0);CHECK(!tank_muzzle_shots[0].valid&&!tank_muzzle_shots[0].rejected&&tank_muzzle_draw(0,147)==0);enemySpriteSheetIds[0]=20;enemy[0].egr[0]=93;
 }
 for(unsigned k=0;k<3;k++){
  mu_birth(110,80,194,3);uint64_t generation=tank_muzzle_shots[0].generation;
  if(k==0)enemyShot[0].sxm=4;if(k==1)enemyShot[0].duration=255;if(k==2)++tank_muzzle_shots[0].generation;
  CHECK(tank_muzzle_draw(0,147)==-1&&tank_muzzle_shots[0].rejected);
  enemyShot[0].sxm=3;enemyShot[0].duration=254;tank_muzzle_shots[0].generation=generation;CHECK(tank_muzzle_draw(0,147)==-1);
  mu_birth(110,80,194,3);CHECK(tank_muzzle_draw(0,147)==1);
 }
 tank_muzzle_shots[0].generation=UINT64_MAX-1;tank_muzzle_allocate(0);CHECK(tank_muzzle_shots[0].generation==UINT64_MAX);mu_birth(110,80,194,3);CHECK(tank_muzzle_shots[0].generation==UINT64_MAX&&!tank_muzzle_shots[0].valid&&tank_muzzle_draw(0,147)==0);mu_level_reset();mu_birth(110,80,194,3);CHECK(tank_muzzle_shots[0].generation==1&&tank_muzzle_draw(0,147)==1);
}
static void mu_lifecycle6(void)
{
 for(unsigned mode=0;mode<6;mode++){
  mu_setup();mu_birth(110,80,194,3);CHECK(tank_muzzle_draw(0,147)==1);uint64_t g=tank_muzzle_shots[0].generation;
  if(mode==0){enemy[0].enemytype=15;enemy[0].egr[0]=91;enemy[0].sprite2s=NULL;CHECK(tank_muzzle_draw(0,147)==1);MuBefore b;mu_valid(110,80,&b);}
  if(mode==1){mu_birth(110,80,194,3);CHECK(tank_muzzle_shots[0].generation==g+1&&tank_muzzle_draw(0,147)==1);mu_sidecar_gate_table();}
  if(mode==2){mu_birth(110,80,195,3);CHECK(tank_muzzle_shots[0].generation==g+1&&tank_muzzle_draw(0,147)==0);}
  if(mode==3||mode==4){enemyShotAvail[0]=true;tank_muzzle_retire(0);CHECK(!tank_muzzle_shots[0].valid&&!tank_muzzle_shots[0].rejected&&tank_muzzle_draw(0,147)==0);}
  if(mode==5){
   enemyShot[0].sgr=647;CHECK(tank_muzzle_draw(0,647)==-1);enemyShot[0].sgr=147;CHECK(tank_muzzle_draw(0,147)==-1);
   char saved[1024];memcpy(saved,global_asset_directory,sizeof(saved));global_asset_directory[0]=0;CHECK(!render_mirror_tank147_muzzle_lane()&&tank_muzzle_draw(0,147)==-1);memcpy(global_asset_directory,saved,sizeof(saved));
   game_probe_assets="";CHECK(!render_mirror_tank147_muzzle_lane()&&tank_muzzle_draw(0,147)==-1);game_probe_assets=NULL;CHECK(render_mirror_tank147_muzzle_lane());mu_draw_checked();CHECK(!global_projectile91_contributed);
   mu_level_reset();CHECK(!tank_muzzle_shots[0].generation&&!tank_muzzle_shots[0].valid&&!tank_muzzle_shots[0].rejected);mu_birth(110,80,194,3);CHECK(tank_muzzle_draw(0,147)==1);
  }
 }
}
static void mu_bounds7(void)
{
 const int xy[6][2]={{24,1},{275,170},{23,80},{276,80},{110,0},{110,171}};
 for(unsigned i=0;i<6;i++){mu_setup();mu_birth(xy[i][0],xy[i][1],194,3);if(i<2){MuBefore b;mu_valid(xy[i][0],xy[i][1],&b);finish();CHECK(ready&&last_output_valid);mu_oracle(xy[i][0],xy[i][1],&b,true);}else{mu_draw_checked();CHECK(!global_projectile91_used_members&&!global_projectile91_fault);}}
 mu_setup();mu_birth(110,80,194,3);game_probe_density=4;mu_draw_checked();CHECK(!global_projectile91_contributed&&!global_projectile91_used_members);
}
static void mu_dependencies6(void)
{
 const char *save=valid_root;char path[1200];
 for(unsigned i=0;i<2;i++){int n=snprintf(path,sizeof(path),"%s/%s147",mu_packs,i?"bad":"missing");CHECK(n>0&&(size_t)n<sizeof(path));valid_root=path;mu_setup();mu_birth(110,80,194,3);CHECK(render_mirror_tank147_muzzle_lane());mu_draw_checked();CHECK(!global_projectile91_contributed&&!global_projectile91_used_members&&tank_muzzle_shots[0].valid);}valid_root=save;
 for(unsigned mode=0;mode<4;mode++){mu_setup();mu_birth(110,80,194,3);MuBefore b;mu_valid(110,80,&b);if(mode==0){finish();CHECK(ready&&last_output_valid);tk_asset(1)->rgba[128]^=1;global_projectile91_check_cache();}else if(mode==1){rgb_palette[49]^=1;finish();}else{CHECK(global_projectile91_used_colors[27]);if(mode==3){finish();CHECK(ready&&last_output_valid);}rgb_palette[27]^=1;if(mode==3)global_projectile91_check_cache();else finish();}CHECK(!ready&&!last_output_valid);if(mode>=2)mu_recover(110,80);}
}
static void mu_final_write(int gx,int gy,bool rect,bool fade,int recover_x,int recover_y)
{
 Uint32 restore[256];memcpy(restore,rgb_palette,sizeof(restore));CHECK(ready&&last_output_valid&&global_projectile91_cached);
 if(fade){SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);for(unsigned i=0;i<256;i++){Uint32 c=rgb_palette[i],v=0;for(unsigned sh=0;sh<24;sh+=8){int q=(c>>sh)&255;q+=(0-q)/7;v|=(Uint32)q<<sh;}rgb_palette[i]=v;}render_mirror_fade_step(7);CHECK(ready&&last_output_valid&&global_projectile91_cached&&have_fade_saved);}
 Uint8 *p=(Uint8*)VGAScreenSeg->pixels+gy*320+gx-24;*p=58;if(rect){SDL_Rect r={gx-24,gy,1,1};render_mirror_rect(VGAScreenSeg,&r);}else render_mirror_pixel(VGAScreenSeg,p,58,MIRROR_NORMAL);enemy70_declined();CHECK(*p==58);
 SDL_Surface *screen=SDL_CreateRGBSurfaceWithFormat(0,output->w,output->h,32,SDL_PIXELFORMAT_ARGB8888);CHECK(screen);SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(screen);CHECK(renderer&&!render_mirror_present(renderer,VGAScreenSeg,NULL));enemy70_declined();if(texture){SDL_DestroyTexture(texture);texture=NULL;}SDL_DestroyRenderer(renderer);SDL_FreeSurface(screen);
 SDL_Color colors[256];for(unsigned i=0;i<256;i++)colors[i]=(SDL_Color){(rgb_palette[i]>>16)&255,(rgb_palette[i]>>8)&255,rgb_palette[i]&255,255};CHECK(!SDL_SetPaletteColors(VGAScreenSeg->format->palette,colors,0,256));SDL_Surface *native=SDL_ConvertSurfaceFormat(VGAScreenSeg,SDL_PIXELFORMAT_ARGB8888,0),*cell=SDL_CreateRGBSurfaceWithFormat(0,8,8,32,SDL_PIXELFORMAT_ARGB8888);CHECK(native&&cell);SDL_Rect r={gx-24,gy,1,1};CHECK(!SDL_BlitScaled(native,&r,cell,NULL));for(unsigned j=0;j<64;j++)CHECK(*at(cell,j%8,j/8)==palette_rgb(58));SDL_FreeSurface(cell);SDL_FreeSurface(native);
 memcpy(rgb_palette,restore,sizeof(restore));mu_recover(recover_x,recover_y);
}
static void mu_green4(void)
{
 for(unsigned mode=0;mode<4;mode++){
  pg_record(71,pg_records[0]);pg_record(1071,pg_records[1]);mu_setup();CHECK(global_green_source_matches(spriteSheet8)&&global_green_palette_matches());int x,y;pg_birth(&x,&y);int gx=x+11,gy=y+1,ex=gx-12,ey=gy-8;mu_birth(ex,ey,194,3);MuBefore b;mu_valid(ex,ey,&b);unsigned sc,gc,hc;pg_counts(gx,gy,&sc,&gc,&hc);CHECK(sc==10&&hc==10&&!gc&&global_green_family_ready());Uint32 under[64];for(unsigned j=0;j<64;j++){size_t n=(size_t)(gy*8+j/8)*2560+gx*8+j%8;under[j]=hd_owner[n]?*at(canvas,gx*8+j%8,gy*8+j/8):palette_rgb(27);}
  bool special=false;int sx=0,sy=0;JE_integer damage=0;JE_byte blast=0,chain=0,pnum=0;JE_word rw=0,rh=0;CHECK(player_shot_move_and_draw(0,&special,&sx,&sy,&damage,&blast,&chain,&pnum,&rw,&rh));CHECK(!special&&sx+1==x&&sy==y&&pnum==1&&global_green_contributed&&!global_green_fault&&!global_green_identity_fault);pg_counts(gx,gy,&sc,&gc,&hc);CHECK(!sc&&gc==40&&hc==40&&global_projectile91_used_members==1073741824u);finish();CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_green_cached);
  for(unsigned j=0;j<64;j++){const Uint8 *q=global_green_rgba[0]+4*((8+j/8)*96+88+j%8);CHECK(*at(output,(gx-24)*8+j%8,gy*8+j/8)==alpha(under[j],q));}
  mu_final_write(gx,gy,mode%2,mode>=2,ex,ey);
 }
}
static void mu_fonts2(void)
{
 for(unsigned mode=0;mode<2;mode++){
  mu_setup();CHECK(render_mirror_set_hud_assets(mu_hudroot));memcpy(VGAScreenSeg->pixels,mu_pic3,64000);render_mirror_hud_start(VGAScreenSeg);CHECK(hud_font_ready()&&font_gameplay);SDL_FillRect(game_screen,NULL,27);render_mirror_begin();CHECK(font_gameplay&&shared_hud_frame);
  render_mirror_text_begin(game_screen,1,28,28,"TEST",2,6);CHECK(font_context==1);JE_textShade(game_screen,28,28,"TEST",2,6,FULL_SHADE);render_mirror_text_end();CHECK(font_scenes[1].canvas_live&&memchr(font_owner+font_scenes[1].offset,1,font_scenes[1].used));
  int x=28,y=mode?28:font_scenes[1].rect.y+font_scenes[1].rect.h;CHECK(x>=24&&x<=275&&y>=1&&y<=170);if(!mode)CHECK(!font_intersects(font_scenes[1].rect,(SDL_Rect){x,y,12,14})&&font_intersects(font_scenes[1].rect,(SDL_Rect){x,y-1,13,15}));
  MuBefore b;mu_snapshot(&b,x,y);for(unsigned i=0;i<12480;i++){/* Native glyph writes replace the saved lower cell color; alpha-only HUF samples retain the initial 27, which is also the untouched native index. */b.canvas[i]=b.under[i]=palette_rgb(b.native[i/104/8*13+(i%104)/8]);CHECK(!b.shared[i]);}mu_birth(x,y,194,3);mu_draw_checked();CHECK(!font_scenes[1].canvas_live&&!memchr(font_owner+font_scenes[1].offset,1,font_scenes[1].used));mu_oracle(x,y,&b,false);finish();CHECK(ready&&last_output_valid);mu_oracle(x,y,&b,true);CHECK(render_mirror_set_hud_assets(NULL));
 }
}
static void mu_partial2(void)
{for(unsigned rect=0;rect<2;rect++){mu_setup();mu_birth(110,80,194,3);MuBefore b;mu_valid(110,80,&b);unsigned sc,gc,hc;pg_counts(122,88,&sc,&gc,&hc);CHECK(sc==10&&hc==10&&!gc);finish();CHECK(ready&&last_output_valid);mu_final_write(122,88,rect,false,110,80);}}
static int mu_main(int argc,char **argv)
{
 CHECK(argc==4&&!strcmp(argv[1],"--tank-muzzle"));mu_packs=argv[2];mu_hudroot=argv[3];static char root[1200];int n=snprintf(root,sizeof(root),"%s/valid",mu_packs);CHECK(n>0&&(size_t)n<sizeof(root));valid_root=missing_root=root;
 read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));Uint32 count;read_exact(&count,4);CHECK(count==33484);spriteSheet9.size=count;spriteSheet9.data=malloc(count);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,count);read_exact(&count,4);CHECK(count==32404);Uint8 *unused=malloc(count);CHECK(unused);read_exact(unused,count);free(unused);read_exact(enemy70_record,80);read_exact(enemy70_port,82);read_exact(pg_records,160);explosionSpriteSheet.size=17810;explosionSpriteSheet.data=malloc(17810);CHECK(explosionSpriteSheet.data);read_exact(explosionSpriteSheet.data,17810);
 read_exact(mu_weapon,sizeof(mu_weapon));read_exact(mu_bank20,sizeof(mu_bank20));read_exact(mu_pic3,sizeof(mu_pic3));Uint16 glyphs;read_exact(&glyphs,2);CHECK(glyphs==127);sprite_table[TINY_FONT].count=glyphs;for(unsigned i=0;i<glyphs;i++){Sprite *s=&sprite_table[TINY_FONT].sprite[i];read_exact(&s->width,2);read_exact(&s->height,2);read_exact(&s->size,2);s->data=s->size?malloc(s->size):NULL;if(s->size){CHECK(s->data);read_exact(s->data,s->size);}}CHECK(fgetc(stdin)==EOF);
 unsigned initial=cases,assertions=checks;mu_direct5();mu_lifecycle6();mu_bounds7();mu_dependencies6();mu_green4();mu_fonts2();mu_partial2();CHECK(cases-initial==32);printf("PASS Tank muzzle OFF native: 32 setup cases %u assertions; isolated exact-source sidecar + renderer, NOT full gameplay or ON pixels\n",checks-assertions);return 0;
}
