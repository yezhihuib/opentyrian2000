/* Current Guided: full production renderer, wrapper, indexed blits and original
 * sprite bank. Controlled calls, not natural game-loop or Windows acceptance.
 * The frozen prior matrices are included unchanged by the pinned Python adapter. */
#include "native_p09_current_helpers.inc"
static const unsigned guided_ids_current[]={19,171,20,21};
static void guided_player_draw(unsigned id,bool shadow)
{
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);
 memcpy(classic->pixels,game_screen->pixels,64000);
 if(shadow)blit_sprite2_darken(classic,100,80,spriteSheet8,id);else blit_sprite2(classic,100,80,spriteSheet8,id);
 unsigned char saved[sizeof(playerShotData)];memcpy(saved,playerShotData,sizeof(saved));
 mt_srand(917);unsigned long expected=mt_rand();mt_srand(917);
 if(shadow)draw_player_shot_shadow_sprite2(game_screen,100,80,spriteSheet8,id,0,id);
 else draw_player_shot_sprite2(game_screen,100,80,spriteSheet8,id,0,id);
 CHECK(mt_rand()==expected);CHECK(!memcmp(saved,playerShotData,sizeof(saved)));
 CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));SDL_FreeSurface(classic);
 CHECK(!enemy_reuse_frame.contributed);
}
/* Cold-start loader fixture: production caches are process-lifetime; changing
 * the fixture path alone is not a production hot-reload API. Reset only these
 * four cache entries between independent test scenarios, never during a draw. */
static void guided_setup(unsigned id)
{
 for(unsigned k=0;k<4;k++){free(assets[326+k].rgba);memset(&assets[326+k],0,sizeof(Asset));}
 setup(id);
}
static void guided_players(void)
{
 render_mirror_set_global_assets(NULL);resource_root=valid_root;
 for(unsigned k=0;k<4;k++){
  unsigned id=guided_ids_current[k];guided_setup(20);guided_player_draw(id,false);CHECK(draws==1);
  Asset *a=&assets[326+k];CHECK(a->valid&&a->index==(int)id&&a->bank==8&&a->density==8);
  Uint32 expected[96*112];
  for(unsigned y=0;y<112;y++)for(unsigned x=0;x<96;x++){
   const Uint8 *p=a->rgba+4*(y*96+x);Uint32 bg=palette_rgb(0x1b),v=0xff000000u;
   for(unsigned s=0;s<24;s+=8)v|=(( ((bg>>s)&255)*(255-p[3])+p[2-s/8]*p[3]+127)/255)<<s;
   expected[y*96+x]=v;CHECK(*pixel(canvas,800+x,640+y)==v);
  }
  guided_player_draw(id,true);CHECK(draws==2);
  for(unsigned y=0;y<112;y++)for(unsigned x=0;x<96;x++){
   unsigned alpha=a->rgba[4*(y*96+x)+3];Uint32 bg=expected[y*96+x],v=0xff000000u;
   for(unsigned s=0;s<24;s+=8)v|=((((bg>>s)&255)*(510-alpha)+255)/510)<<s;
   CHECK(*pixel(canvas,800+x,640+y)==v);
  }
  finish();CHECK(last_output_valid&&!reject_reason);
  /* Later indexed ownership wins over the earlier Guided overlay. */
  guided_setup(20);guided_player_draw(id,false);Uint8 *p=(Uint8*)game_screen->pixels+85*320+105;*p=0x3a;render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);finish();
  CHECK(last_output_valid);for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++)CHECK(*pixel(output,(105-24)*8+x,85*8+y)==palette_rgb(0x3a));
  const char *modes[]={"missing","magic","header","short"};
  for(unsigned m=0;m<4;m++){
   char root[4096];snprintf(root,sizeof(root),"%s/player-%s-%u",valid_root,modes[m],id);resource_root=root;guided_setup(20);guided_player_draw(id,false);CHECK(draws==0&&!assets[326+k].valid);
  }
  resource_root=valid_root;
 }
 guided_setup(20);guided_player_draw(22,false);CHECK(draws==0);CHECK(!get_asset(spriteSheet8,22,ENTITY_TILE));
 /* Native P04 uses the same exact edited bytes, independently loaded. */
 for(unsigned k=2;k<4;k++){
  unsigned id=guided_ids_current[k];guided_setup(id);guided_player_draw(id,false);Asset *player_asset=&assets[326+k];
  birth(id,0,100,80);draw(id,0,100,80);CHECK(enemy_reuse_frame.contributed);CHECK(!memcmp(player_asset->rgba,enemy_reuse_resources.members[k+2].rgba,96*112*4));
 }
}
int main(int argc,char **argv)
{
 int status=current_guided_legacy_p09_main(argc,argv);CHECK(status==0);
 render_mirror_set_global_assets(NULL);resource_root=valid_root;
 positives();negatives();lifecycle();boundaries();identity_contracts();guided_players();
 printf("PASS CURRENT Guided native player ordinary/shadow, P04 shared payload, INDEX8/RNG/write order/fallback/22 exclusion: %u setups, %u assertions\n",cases,checks);return 0;
}
