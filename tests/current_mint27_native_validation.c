/* Native Mint27 calls with full production renderer and original sprite data. */
#include "native_p09_current_helpers.inc"
static void mint_setup(void){free(assets[535].rgba);memset(&assets[535],0,sizeof(Asset));setup(20);}
static void mint_draw(bool shadow,unsigned slot)
{
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
 if(shadow)blit_sprite2_darken(classic,100,80,spriteSheet8,27);else blit_sprite2(classic,100,80,spriteSheet8,27);
 unsigned char saved[sizeof(playerShotData)];memcpy(saved,playerShotData,sizeof(saved));mt_srand(917);unsigned long expected=mt_rand();mt_srand(917);
 if(shadow)draw_player_shot_shadow_sprite2(game_screen,100,80,spriteSheet8,27,slot,27);else draw_player_shot_sprite2(game_screen,100,80,spriteSheet8,27,slot,27);
 CHECK(mt_rand()==expected);CHECK(!memcmp(saved,playerShotData,sizeof(saved)));CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));SDL_FreeSurface(classic);CHECK(!enemy_reuse_frame.contributed);
}
static void mint_positive(void)
{
 render_mirror_set_global_assets(NULL);resource_root=valid_root;
 /* Slots only test shared generic wrapper, not native sidekick firing attribution. */
 for(unsigned slot=0;slot<2;slot++){
  mint_setup();mint_draw(false,slot);CHECK(draws==1);Asset *a=&assets[535];CHECK(a->valid&&a->index==27&&a->bank==8&&a->density==8&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y);
  Uint32 expected[96*112];unsigned partial=0;
  for(unsigned y=0;y<112;y++)for(unsigned x=0;x<96;x++){
   const Uint8*p=a->rgba+4*(y*96+x);Uint32 bg=palette_rgb(0x1b),v=0xff000000u;partial+=p[3]>0&&p[3]<255;
   for(unsigned s=0;s<24;s+=8)v|=(( ((bg>>s)&255)*(255-p[3])+p[2-s/8]*p[3]+127)/255)<<s;
   expected[y*96+x]=v;CHECK(*pixel(canvas,800+x,640+y)==v);
  }CHECK(partial>0);
  Uint8 indexed_before[12*14],owner_before[96*112];
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++)indexed_before[y*12+x]=*((Uint8*)game_screen->pixels+(80+y)*game_screen->pitch+100+x);
  for(unsigned y=0;y<112;y++)for(unsigned x=0;x<96;x++)owner_before[y*96+x]=hd_owner[(640+y)*canvas->w+800+x];
  mint_draw(true,slot);CHECK(draws==2);
  for(unsigned y=0;y<112;y++)for(unsigned x=0;x<96;x++){
   unsigned alpha=a->rgba[4*(y*96+x)+3];Uint32 bg=expected[y*96+x],v=0xff000000u;
   Uint8 old=indexed_before[(y/8)*12+x/8],after=(old&0xf0)|((old&15)/2);Uint32 palette_dark=palette_rgb(after);
   for(unsigned s=0;s<24;s+=8){unsigned channel=(bg>>s)&255;unsigned dark=owner_before[y*96+x]?((channel+1)/2):((palette_dark>>s)&255);v|=((channel*(255-alpha)+dark*alpha+127)/255)<<s;}
   CHECK(*pixel(canvas,800+x,640+y)==v);
  }finish();CHECK(last_output_valid&&!reject_reason);
 }
 mint_setup();mint_draw(false,0);Uint8*p=(Uint8*)game_screen->pixels+85*320+105;*p=0x3a;render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);finish();CHECK(last_output_valid);for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++)CHECK(*pixel(output,(105-24)*8+x,85*8+y)==palette_rgb(0x3a));
}
static void mint_negative(void)
{
 const char*modes[]={"missing","magic","header","short","anchor","trailing"};
 for(unsigned i=0;i<6;i++){char root[4096];snprintf(root,sizeof(root),"%s/player-%s-27",valid_root,modes[i]);resource_root=root;mint_setup();mint_draw(false,0);CHECK(draws==0&&!assets[535].valid);}
 resource_root=valid_root;
 for(unsigned mode=0;mode<5;mode++){
  mint_setup();if(mode==0)xmas=true;if(mode==1)game_probe_density=1;if(mode==2)game_probe_missing=true;if(mode==3)game_probe_invalid=true;
  if(mode==4){size_t pos=bank_bytes[52]|((size_t)bank_bytes[53]<<8);while(!(bank_bytes[pos]>>4))pos++;Uint8 old=bank_bytes[pos+1];bank_bytes[pos+1]^=1;CHECK(!mint27_source_matches(spriteSheet8));mint_draw(false,0);CHECK(!draws);bank_bytes[pos+1]=old;continue;}
  mint_draw(false,0);CHECK(!draws);
 }
 /* Warm source revalidation rejects same-allocation reload. */
 mint_setup();mint_draw(false,0);CHECK(draws==1);size_t pos=bank_bytes[52]|((size_t)bank_bytes[53]<<8);while(!(bank_bytes[pos]>>4))pos++;Uint8 old=bank_bytes[pos+1];bank_bytes[pos+1]^=1;CHECK(!get_asset(spriteSheet8,27,ENTITY_TILE));bank_bytes[pos+1]=old;
 /* Changed transport pixels cannot obtain the pinned shadow lease. */
 mint_setup();mint_draw(false,0);assets[535].rgba[31]^=1;unsigned before=draws;mint_draw(true,0);CHECK(draws==before);assets[535].rgba[31]^=1;
 mint_setup();mint_draw(false,0);render_mirror_fade_start(NULL,NULL,0,255);CHECK(!ready&&!last_output_valid&&!vulcan_shadow.live);
}
int main(int argc,char**argv){int status=current_mint27_legacy_p09_main(argc,argv);CHECK(status==0);mint_positive();mint_negative();printf("PASS CURRENT Mint27 native ordinary/shadow, INDEX8/RNG/state/alpha/source/resource/lifetime: %u setups, %u assertions\n",cases,checks);return 0;}
