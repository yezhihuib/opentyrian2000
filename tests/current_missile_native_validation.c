/* Native Missile calls with full production renderer and original sprite data. */
#include "native_p09_current_helpers.inc"
static unsigned missile_frame=31;
static unsigned missile_slot(void){return 333+missile_frame-31;}
static void missile_setup(void){for(unsigned i=333;i<=335;i++){free(assets[i].rgba);memset(&assets[i],0,sizeof(Asset));}setup(20);}
static void missile_draw(bool shadow,unsigned slot)
{
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
 if(shadow)blit_sprite2_darken(classic,100,80,spriteSheet8,missile_frame);else blit_sprite2(classic,100,80,spriteSheet8,missile_frame);
 unsigned char saved[sizeof(playerShotData)];memcpy(saved,playerShotData,sizeof(saved));mt_srand(917);unsigned long expected=mt_rand();mt_srand(917);
 if(shadow)draw_player_shot_shadow_sprite2(game_screen,100,80,spriteSheet8,missile_frame,slot,missile_frame);else draw_player_shot_sprite2(game_screen,100,80,spriteSheet8,missile_frame,slot,missile_frame);
 CHECK(mt_rand()==expected);CHECK(!memcmp(saved,playerShotData,sizeof(saved)));CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));SDL_FreeSurface(classic);CHECK(!enemy_reuse_frame.contributed);
}
static void missile_positive(void)
{
 render_mirror_set_global_assets(NULL);resource_root=valid_root;
 /* Slots only test shared generic wrapper, not native sidekick firing attribution. */
 for(unsigned slot=0;slot<2;slot++){
  missile_setup();missile_draw(false,slot);CHECK(draws==1);Asset *a=&assets[missile_slot()];CHECK(a->valid&&a->index==(int)missile_frame&&a->bank==8&&a->density==8&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y);
  Uint32 expected[96*112];unsigned partial=0;
  for(unsigned y=0;y<112;y++)for(unsigned x=0;x<96;x++){
   const Uint8*p=a->rgba+4*(y*96+x);Uint32 bg=palette_rgb(0x1b),v=0xff000000u;partial+=p[3]>0&&p[3]<255;
   for(unsigned s=0;s<24;s+=8)v|=(( ((bg>>s)&255)*(255-p[3])+p[2-s/8]*p[3]+127)/255)<<s;
   expected[y*96+x]=v;CHECK(*pixel(canvas,800+x,640+y)==v);
  }CHECK(partial>0);
  Uint8 indexed_before[12*14],owner_before[96*112];
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++)indexed_before[y*12+x]=*((Uint8*)game_screen->pixels+(80+y)*game_screen->pitch+100+x);
  for(unsigned y=0;y<112;y++)for(unsigned x=0;x<96;x++)owner_before[y*96+x]=hd_owner[(640+y)*canvas->w+800+x];
  missile_draw(true,slot);CHECK(draws==2);
  for(unsigned y=0;y<112;y++)for(unsigned x=0;x<96;x++){
   unsigned alpha=a->rgba[4*(y*96+x)+3];Uint32 bg=expected[y*96+x],v=0xff000000u;
   Uint8 old=indexed_before[(y/8)*12+x/8],after=(old&0xf0)|((old&15)/2);Uint32 palette_dark=palette_rgb(after);
   for(unsigned s=0;s<24;s+=8){unsigned channel=(bg>>s)&255;unsigned dark=owner_before[y*96+x]?((channel+1)/2):((palette_dark>>s)&255);v|=((channel*(255-alpha)+dark*alpha+127)/255)<<s;}
   CHECK(*pixel(canvas,800+x,640+y)==v);
  }finish();CHECK(last_output_valid&&!reject_reason);
 }
 missile_setup();missile_draw(false,0);Uint8*p=(Uint8*)game_screen->pixels+85*320+105;*p=0x3a;render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);finish();CHECK(last_output_valid);for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++)CHECK(*pixel(output,(105-24)*8+x,85*8+y)==palette_rgb(0x3a));
}
static size_t missile_source_pixel(void)
{
 unsigned off=(missile_frame-1)*2;size_t pos=bank_bytes[off]|((size_t)bank_bytes[off+1]<<8);
 while(!(bank_bytes[pos]>>4))pos++;return pos+1;
}
static void missile_negative(void)
{
 const char*modes[]={"missing","magic","header","short","anchor","trailing"};
 for(unsigned i=0;i<6;i++){char root[4096];snprintf(root,sizeof(root),"%s/player-%s-%u",valid_root,modes[i],missile_frame);resource_root=root;missile_setup();missile_draw(false,0);CHECK(draws==0&&!assets[missile_slot()].valid);}
 resource_root=valid_root;
 for(unsigned mode=0;mode<3;mode++){
  missile_setup();if(mode==0)game_probe_density=1;if(mode==1)game_probe_missing=true;if(mode==2)game_probe_invalid=true;
  missile_draw(false,0);CHECK(!draws);
 }
 /* Generic ordinary loader has no Mint27-specific source-pin gate. Preserve it. */
 missile_setup();missile_draw(false,0);CHECK(draws==1);size_t pos=missile_source_pixel();Uint8 old=bank_bytes[pos];bank_bytes[pos]^=1;
 CHECK(get_asset(spriteSheet8,missile_frame,ENTITY_TILE)==&assets[missile_slot()]);
 unsigned before=draws;missile_draw(true,0);CHECK(draws==before);bank_bytes[pos]=old;
 /* A changed ordinary RGBA payload cannot obtain the pinned shadow lease. */
 missile_setup();missile_draw(false,0);assets[missile_slot()].rgba[31]^=1;before=draws;missile_draw(true,0);CHECK(draws==before);assets[missile_slot()].rgba[31]^=1;
 /* Cold, structurally valid transport with changed payload loads ordinary, not shadow. */
 char payload_root[4096];snprintf(payload_root,sizeof(payload_root),"%s/player-payload-%u",valid_root,missile_frame);resource_root=payload_root;
 missile_setup();missile_draw(false,0);CHECK(draws==1);missile_draw(true,0);CHECK(draws==1);resource_root=valid_root;
 for(unsigned fault=0;fault<6;fault++){
  missile_setup();missile_draw(false,0);CHECK(draws==1);
  if(fault==0)xmas=true;if(fault==1)twoPlayerMode=true;if(fault==2)galagaMode=true;if(fault==3)twoPlayerLinked=true;if(fault==4)game_probe_original_reference=true;if(fault==5)game_probe_assets="changed-resource-root";
  before=draws;missile_draw(true,0);CHECK(draws==before);
 }
 missile_setup();missile_draw(false,0);render_mirror_fade_start(NULL,NULL,0,255);CHECK(!ready&&!last_output_valid&&!vulcan_shadow.live);
}
int main(int argc,char**argv){int status=current_missile_legacy_p09_main(argc,argv);CHECK(status==0);for(missile_frame=31;missile_frame<=33;missile_frame++){missile_positive();missile_negative();}printf("PASS CURRENT Missile native ordinary/shadow 31/32/33, INDEX8/RNG/state/alpha/source/resource/lifetime: %u setups, %u assertions\n",cases,checks);return 0;}
