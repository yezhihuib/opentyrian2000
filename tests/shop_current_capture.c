/* Fresh current-source SDL software harness, not a game-loop recording. */
#include "shop_current_fixture.inc"
JE_byte shotAvail[MAX_PWEAPON];
PlayerShotDataType playerShotData[MAX_PWEAPON+1];
static void capture(const char *name,const char *outdir,unsigned w,unsigned h,bool hd){
 SDL_Surface *out=SDL_CreateRGBSurfaceWithFormat(0,w,h,32,SDL_PIXELFORMAT_RGB888);REQUIRE(out);
 SDL_Renderer *r=SDL_CreateSoftwareRenderer(out);REQUIRE(r);
 SDL_Texture *t=SDL_CreateTexture(r,SDL_PIXELFORMAT_RGB888,SDL_TEXTUREACCESS_STREAMING,640,400);REQUIRE(t);
 SDL_Rect d={0,0,w,h};REQUIRE(!SDL_SetTextureBlendMode(t,SDL_BLENDMODE_NONE));scaler=1;scalers[1].scaler32(VGAScreen,t);
 REQUIRE(!SDL_SetRenderDrawColor(r,0,0,0,255));REQUIRE(!SDL_RenderClear(r));
 if(hd)REQUIRE(pregame_font_present(r,t,VGAScreen,&d,false));else REQUIRE(!SDL_RenderCopy(r,t,NULL,&d));
 SDL_RenderPresent(r);char p[2048];snprintf(p,sizeof p,"%s/%s-%ux%u-%s.bmp",outdir,name,w,h,hd?"hd":"classic");REQUIRE(SDL_SaveBMP(out,p)==0);
 pregame_font_release_texture();SDL_DestroyTexture(t);SDL_DestroyRenderer(r);SDL_FreeSurface(out);
}
int main(int argc,char **argv){
 REQUIRE(argc==9&&SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);REQUIRE(VGAScreen&&VGAScreen2);
 main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);REQUIRE(main_window_tex_format);fixtures(argv[1]);strings_fixture(argv[1]);memcpy(raw_base,VGAScreen2->pixels,SF_N);test_ship=31;
 const char *names[]={"fonts","metal","talon","front","generator","menu"};Uint8 expected[SF_N];
 for(unsigned i=0;i<6;i++){
  REQUIRE(common_menu_runs_set_directory(i==5?argv[7]:NULL));frame_checks(argv[i+2],0,4,4,15,10);render();REQUIRE(replay_matches());
  if(i==0)memcpy(expected,sf.pixels,SF_N);else REQUIRE(!memcmp(expected,sf.pixels,SF_N));
  unsigned sizes[][2]={{640,400},{1280,800},{913,599}};
  for(unsigned j=0;j<3;j++){capture(names[i],argv[8],sizes[j][0],sizes[j][1],false);capture(names[i],argv[8],sizes[j][0],sizes[j][1],true);}
  char p[2048];snprintf(p,sizeof p,"%s/%s.index8",argv[8],names[i]);write_bytes(p,sf.pixels,SF_N);pregame_font_end();
 }
 test_product_ship=true;
 for(unsigned cat=2;cat<=8;cat++){
  product_page(argv[6],cat,2,"10000",true);REQUIRE(sf.frame);render();REQUIRE(replay_matches());char n[64];snprintf(n,sizeof n,"product-%u",cat);
  capture(n,argv[8],640,400,false);capture(n,argv[8],640,400,true);pregame_font_end();
 }
 REQUIRE(!allocated);printf("PASS fresh SDL software captures: 6 root resource combinations at 3 dimensions, 7 product grammars; INDEX8 roots exact; not game-loop coverage; checks=%u\n",checks);return 0;
}
