/* Isolated real quad calls; synthetic shop fixture, not native navigation. */
static unsigned test_quad=169;
static int test_occlude;
#include "pregame_typography_reconstruction.c"
JE_byte shotAvail[MAX_PWEAPON];
PlayerShotDataType playerShotData[MAX_PWEAPON+1];
static unsigned static_commands(void){unsigned n=0;for(unsigned i=0;i<sf.count;i++)n+=sf.commands[i].kind==C_STATIC;return n;}
static void page(const char *root,unsigned slot){test_quad=shop_static_spec[slot].quad;auth_page(root,8,2,2,"10000",true);REQUIRE(sf.frame&&sf.stage==S_READY);render();REQUIRE(replay_matches());}
int main(int argc,char **argv){
 REQUIRE(argc==3);REQUIRE(SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);
 fixtures(argv[1]);strings_fixture(argv[1]);memcpy(raw_base,VGAScreen2->pixels,SF_N);strcpy(miscText[13],"DONE");strcpy(miscTextB[5],"POWER:");
 REQUIRE(common_menu_runs_set_directory(argv[2]));item_fixture(argv[1],1);itemAvailMax[6]=2;itemAvail[6][0]=20;itemAvail[6][1]=26;player[0].cash=10000;
 for(unsigned slot=0;slot<3;slot++){
  page(argv[2],slot);REQUIRE(static_commands()==2&&shop_static_valid(slot));
  Uint8 indexed[SF_N];memcpy(indexed,VGAScreen->pixels,SF_N);uint64_t out=hash(sf.output,SF_OUT_BYTES);
  render();REQUIRE(hash(sf.output,SF_OUT_BYTES)==out&&!memcmp(indexed,VGAScreen->pixels,SF_N));
  REQUIRE(pregame_font_retained_bytes()<16*1024*1024);
  for(unsigned y=0;y<112;y++)for(unsigned x=0;x<96;x++){
   unsigned a,b,sum=0,c[3]={0,0,0};sf.metal_gain=255;Uint32 rgb=shop_static_sample(shop_static.rgba[slot],x,y,&a);sf.metal_gain=0;REQUIRE(shop_static_sample(shop_static.rgba[slot],x,y,&b)==0&&a==b);
   for(unsigned yy=0;yy<2;yy++)for(unsigned xx=0;xx<2;xx++){const Uint8 *v=shop_static.rgba[slot]+((y*2+yy)*192+x*2+xx)*4;sum+=v[3];for(unsigned k=0;k<3;k++)c[k]+=v[k]*v[3];}
   Uint32 expected=0;if(sum)for(unsigned k=0;k<3;k++)expected|=((c[k]+sum/2)/sum)<<(16-k*8);REQUIRE(rgb==expected&&a==(sum+2)/4);
  }sf.metal_gain=255;
  /* All three operator controls retire contributed art and cannot revive it. */
  for(unsigned flag=0;flag<3;flag++){
   page(argv[2],slot);bool *p=flag==0?&game_probe_original_reference:flag==1?&game_probe_missing:&game_probe_invalid;*p=true;render();REQUIRE(!shop_static_valid(slot)&&replay_matches());*p=false;render();REQUIRE(!shop_static_valid(slot)&&replay_matches());
  }
  page(argv[2],slot);shop_static.rgba[slot][777]^=1;REQUIRE(!shop_static_valid(slot));shop_static.rgba[slot][777]^=1;REQUIRE(!shop_static_valid(slot));
  page(argv[2],slot);palettes[0][99].r^=1;REQUIRE(!shop_static_valid(slot));palettes[0][99].r^=1;REQUIRE(!shop_static_valid(slot));
  page(argv[2],slot);Uint8 *old=shopSpriteSheet.data,*copy=malloc(shopSpriteSheet.size);memcpy(copy,old,shopSpriteSheet.size);shopSpriteSheet.data=copy;REQUIRE(!shop_static_valid(slot));shopSpriteSheet.data=old;free(copy);REQUIRE(!shop_static_valid(slot));
  page(argv[2],slot);shopSpriteSheet.data[1000]^=1;REQUIRE(!shop_static_valid(slot));shopSpriteSheet.data[1000]^=1;REQUIRE(!shop_static_valid(slot));
  /* Exact header fields, reserved bytes, payload and EOF are independently pinned. */
  const unsigned offsets[]={0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,72,80,88,96,104,112,120,128,172159};
  char path[1200];snprintf(path,sizeof(path),"bad-root/%s",shop_static_spec[slot].name);
  for(unsigned k=0;k<sizeof(offsets)/sizeof(*offsets);k++){
   FILE *f=fopen(path,"r+b");REQUIRE(f);fseek(f,offsets[k],SEEK_SET);int v=fgetc(f);fseek(f,offsets[k],SEEK_SET);fputc(v^1,f);fclose(f);
   page("bad-root",slot);REQUIRE(!shop_static.rgba[slot]&&!static_commands());
   f=fopen(path,"r+b");REQUIRE(f);fseek(f,offsets[k],SEEK_SET);fputc(v,f);fclose(f);shop_static_load(slot);REQUIRE(!shop_static.rgba[slot]);
  }
  FILE *eof=fopen(path,"ab");REQUIRE(eof);fputc(0,eof);fclose(eof);page("bad-root",slot);REQUIRE(!shop_static.rgba[slot]&&!static_commands());REQUIRE(!truncate(path,172160));
  eof=fopen(path,"rb");REQUIRE(eof);fseek(eof,172159,SEEK_SET);int last=fgetc(eof);fclose(eof);REQUIRE(!truncate(path,172159));page("bad-root",slot);REQUIRE(!shop_static.rgba[slot]&&!static_commands());eof=fopen(path,"ab");REQUIRE(eof);fputc(last,eof);fclose(eof);
  page(argv[2],slot);shop_static_reset();fail_allocation=allocation_calls;shop_static_load(slot);REQUIRE(!shop_static.rgba[slot]);fail_allocation=UINT_MAX;shop_static_load(slot);REQUIRE(!shop_static.rgba[slot]);
  char moved[1250];snprintf(moved,sizeof(moved),"%s.missing",path);REQUIRE(!rename(path,moved));page("bad-root",slot);REQUIRE(!shop_static.rgba[slot]&&!static_commands());REQUIRE(!rename(moved,path));page("bad-root",slot);REQUIRE(static_commands()==2);
  test_occlude=1;page(argv[2],slot);test_occlude=0;for(unsigned y=144;y<256;y++)for(unsigned x=640;x<736;x++)REQUIRE(!sf.output[y*SF_OW+x]);
 }
 /* Out-of-owner, wrong surface and update contexts never arm canonical art. */
 page(argv[2],0);unsigned count=sf.count;pregame_font_quad_begin(VGAScreen,160,36,shopSpriteSheet.data,shopSpriteSheet.size,169);REQUIRE(sf.count==count&&!shop_static.blitting);
 SDL_Surface *foreign=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);pregame_font_quad_begin(foreign,160,36,shopSpriteSheet.data,shopSpriteSheet.size,169);REQUIRE(sf.count==count&&!shop_static.blitting);SDL_FreeSurface(foreign);
 pregame_font_product_update_begin();count=sf.count;pregame_font_quad_begin(VGAScreen,160,36,shopSpriteSheet.data,shopSpriteSheet.size,169);REQUIRE(sf.count==count&&!shop_static.blitting);
 pregame_font_set_directory("absent-static-root");REQUIRE(!shop_static.rgba[0]&&!shop_static.rgba[1]&&!shop_static.rgba[2]&&!sf.active);shop_static_load(0);REQUIRE(!shop_static.rgba[0]);
 pregame_font_end();common_menu_runs_shutdown_all();REQUIRE(!allocated);
 printf("PASS static canonical composer %u checks; exact resources/source/palette, fail-closed cache, 4-tile indexed replay, sampling/fade, repeated render, later occlusion; synthetic fixture, not native navigation\n",checks);return 0;
}
