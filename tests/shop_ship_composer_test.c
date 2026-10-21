/* Exact public call and original quad; synthetic shop page, not native navigation. */
#include "pregame_typography_reconstruction.c"
JE_byte shotAvail[MAX_PWEAPON];
PlayerShotDataType playerShotData[MAX_PWEAPON+1];
static const char *startup,*global_root;
static unsigned ship_commands(void){unsigned n=0;for(unsigned i=0;i<sf.count;i++)n+=sf.commands[i].kind==C_SHIP;return n;}
static void load_ship_fixture(const char *dir)
{
 FILE *f=open_data(dir,"tyrian.hdt");unsigned at=rd32(f)+14+1638*80+61*82+55*37+7*37;fseek(f,at,SEEK_SET);
 for(unsigned i=0;i<19;i++){
  unsigned len=fgetc(f);REQUIRE(len<=30);REQUIRE(fread(ships[i].name,1,30,f)==30);ships[i].name[len]=0;
  ships[i].shipgraphic=rd16(f);ships[i].itemgraphic=rd16(f);ships[i].ani=fgetc(f);ships[i].spd=fgetc(f);ships[i].dmg=fgetc(f);ships[i].cost=rd16(f);ships[i].bigshipgraphic=fgetc(f);
 }fclose(f);
 f=open_data(dir,"tyrian.shp");unsigned count=rd16(f),offset[32];REQUIRE(count<32);for(unsigned i=0;i<count;i++)offset[i]=rd32(f);
 spriteSheet9.size=offset[9]-offset[8];spriteSheet9.data=malloc(spriteSheet9.size);fseek(f,offset[8],SEEK_SET);REQUIRE(fread(spriteSheet9.data,1,spriteSheet9.size,f)==spriteSheet9.size);fclose(f);
}
static void page(void)
{
 player[0].items.ship=1;player[0].x=55;player[0].y=97;
 auth_page(startup,3,2,2,"10000",true);assert_page();pregame_shop_ship_set_directory(global_root);
 pregame_font_product_update_begin();fill_rectangle_xy(VGAScreen,8,8,143,182,0);
}
static void draw_ship(void)
{
 pregame_shop_ship_begin(player[0].items.ship,player[0].x-5,player[0].y-7);
 blit_sprite2x2(VGAScreen,player[0].x-5,player[0].y-7,spriteSheet9,ships[player[0].items.ship].shipgraphic);
 pregame_shop_ship_end();
}
static void finish(void){product_text(PREGAME_CASH,0,65,173,"10000",2,1,6);pregame_font_product_update_end();REQUIRE(sf.frame&&sf.stage==S_READY);render();if(!replay_matches()){for(unsigned p=0;p<SF_N;p++)if(sf.replay[p]!=sf.expected[p]){fprintf(stderr,"MISMATCH %u,%u replay=%u expected=%u ship=%u valid=%d fault=%d\n",p%320,p/320,sf.replay[p],sf.expected[p],ship_commands(),shop_ship_valid(),shop_ship.fault);break;}}REQUIRE(replay_matches());}
static uint64_t positive(void){page();draw_ship();REQUIRE(ship_commands()==1&&shop_ship.rgba);finish();return hash(sf.output,SF_OUT_BYTES);}
static void mutate_record(unsigned i)
{
 if(i<30){ships[1].name[i]^=1;return;}
 switch(i){case 30:ships[1].shipgraphic^=1;break;case 31:ships[1].shipgraphic^=256;break;case 32:ships[1].itemgraphic^=1;break;case 33:ships[1].itemgraphic^=256;break;case 34:ships[1].ani^=1;break;case 35:ships[1].spd^=1;break;case 36:ships[1].dmg^=1;break;case 37:ships[1].cost^=1;break;case 38:ships[1].cost^=256;break;case 39:ships[1].bigshipgraphic^=1;break;case 40:ships[1].name[30]^=1;break;}
}
static void mutated_frame(void){render();REQUIRE(replay_matches());REQUIRE(shop_ship.fault);}
int main(int argc,char **argv)
{
 REQUIRE(argc==4);startup=argv[2];global_root=argv[3];REQUIRE(SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);
 fixtures(argv[1]);strings_fixture(argv[1]);memcpy(raw_base,VGAScreen2->pixels,SF_N);strcpy(miscText[13],"DONE");strcpy(miscTextB[5],"POWER:");
 REQUIRE(common_menu_runs_set_directory(startup));item_fixture(argv[1],1);load_ship_fixture(argv[1]);itemAvailMax[1]=2;itemAvail[1][0]=1;itemAvail[1][1]=2;player[0].cash=10000;player[0].items.weapon[0].id=1;player[0].items.weapon[0].power=1;
 /* Real quad runs exactly once; observer leaves every indexed pixel untouched. */
 page();SDL_Surface *reference=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);memcpy(reference->pixels,VGAScreen->pixels,SF_N);sf.active=false;blit_sprite2x2(reference,50,90,spriteSheet9,233);sf.active=true;draw_ship();REQUIRE(!memcmp(reference->pixels,VGAScreen->pixels,SF_N));REQUIRE(ship_commands()==1);finish();SDL_FreeSurface(reference);
 Uint8 indexed[SF_N];memcpy(indexed,VGAScreen->pixels,SF_N);uint64_t good=hash(sf.output,SF_OUT_BYTES);render();REQUIRE(hash(sf.output,SF_OUT_BYTES)==good&&!memcmp(indexed,VGAScreen->pixels,SF_N));
 for(unsigned y=0;y<112;y++)for(unsigned x=0;x<96;x++){
  unsigned a,b,sum=0,c[3]={0,0,0};sf.metal_gain=255;Uint32 rgb=shop_static_sample(shop_ship.rgba,x,y,&a);sf.metal_gain=0;REQUIRE(shop_static_sample(shop_ship.rgba,x,y,&b)==0&&a==b);
  for(unsigned yy=0;yy<2;yy++)for(unsigned xx=0;xx<2;xx++){const Uint8 *v=shop_ship.rgba+((y*2+yy)*192+x*2+xx)*4;sum+=v[3];for(unsigned k=0;k<3;k++)c[k]+=v[k]*v[3];}
  Uint32 expected=0;if(sum)for(unsigned k=0;k<3;k++)expected|=((c[k]+sum/2)/sum)<<(16-k*8);REQUIRE(rgb==expected&&a==(sum+2)/4);
 }sf.metal_gain=255;
 /* Once contributed, restoring an invalid witness must not revive the frame. */
 for(unsigned flag=0;flag<3;flag++){positive();bool *p=flag==0?&game_probe_original_reference:flag==1?&game_probe_missing:&game_probe_invalid;*p=true;mutated_frame();*p=false;mutated_frame();}
 positive();shop_ship.rgba[777]^=1;mutated_frame();shop_ship.rgba[777]^=1;mutated_frame();
 for(unsigned i=0;i<41;i++){positive();mutate_record(i);mutated_frame();mutate_record(i);mutated_frame();page();mutate_record(i);pregame_shop_ship_begin(1,50,90);REQUIRE(!shop_ship.armed);mutate_record(i);blit_sprite2x2(VGAScreen,50,90,spriteSheet9,233);pregame_shop_ship_end();REQUIRE(!ship_commands());finish();}
 positive();player[0].items.ship=9;mutated_frame();player[0].items.ship=1;mutated_frame();
 positive();palettes[0][99].r^=1;mutated_frame();palettes[0][99].r^=1;mutated_frame();
 positive();Uint8 *old=spriteSheet9.data,*copy=malloc(spriteSheet9.size);memcpy(copy,old,spriteSheet9.size);spriteSheet9.data=copy;mutated_frame();spriteSheet9.data=old;free(copy);mutated_frame();
 const unsigned tiles[]={233,234,252,253};for(unsigned i=0;i<4;i++){positive();unsigned n=tiles[i],at=old[2*(n-1)]|(old[2*(n-1)+1]<<8);Uint8 v=old[at];old[at]=15;mutated_frame();old[at]=v;mutated_frame();}
 positive();pregame_shop_ship_set_directory("bad-root");render();REQUIRE(replay_matches()&&shop_ship.fault);pregame_shop_ship_set_directory(global_root);render();REQUIRE(shop_ship.fault);
 positive();pregame_shop_ship_set_directory(NULL);render();REQUIRE(replay_matches());pregame_shop_ship_set_directory(global_root);render();REQUIRE(replay_matches()&&hash(sf.output,SF_OUT_BYTES)!=good);
 /* Explicit new authenticated update recovers; cached resources do not grant a role. */
 positive();pregame_font_product_update_begin();fill_rectangle_xy(VGAScreen,8,8,143,182,0);draw_ship();REQUIRE(ship_commands()==1);finish();
 page();blit_sprite2x2(VGAScreen,50,90,spriteSheet9,233);REQUIRE(!ship_commands());finish();
 page();player[0].items.ship=9;draw_ship();REQUIRE(!ship_commands());finish();
 page();ships[1].ani^=1;draw_ship();ships[1].ani^=1;REQUIRE(!ship_commands());finish();
 page();pregame_shop_ship_begin(1,51,90);blit_sprite2x2(VGAScreen,51,90,spriteSheet9,233);pregame_shop_ship_end();REQUIRE(!ship_commands());finish();
 positive();unsigned count=sf.count;pregame_shop_ship_begin(1,50,90);REQUIRE(sf.count==count&&!shop_ship.armed);pregame_shop_ship_end();
 /* Incomplete, repeated or foreign calls cannot mint a second owner. */
 page();pregame_shop_ship_begin(1,50,90);REQUIRE(shop_ship.armed);pregame_shop_ship_begin(1,50,90);REQUIRE(!sf.frame);pregame_shop_ship_end();
 page();draw_ship();pregame_shop_ship_begin(1,50,90);REQUIRE(!sf.frame);pregame_shop_ship_end();
 page();pregame_shop_ship_begin(1,50,90);pregame_shop_ship_end();REQUIRE(!shop_ship.armed&&!ship_commands());finish();
 page();pregame_shop_ship_begin(1,50,90);reference=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);blit_sprite2x2(reference,50,90,spriteSheet9,233);pregame_shop_ship_end();REQUIRE(!ship_commands());SDL_FreeSurface(reference);
 page();pregame_shop_ship_begin(1,50,90);blit_sprite2x2(VGAScreen,50,90,shopSpriteSheet,233);pregame_shop_ship_end();REQUIRE(!ship_commands());finish();
 page();fail_allocation=allocation_calls;draw_ship();fail_allocation=UINT_MAX;REQUIRE(!shop_ship.rgba&&!ship_commands());finish();
 /* Later original writes, including same-index writes, cover the entire authored support. */
 page();draw_ship();fill_rectangle_xy(VGAScreen,50,90,73,117,0);finish();for(unsigned y=360;y<472;y++)for(unsigned x=200;x<296;x++)REQUIRE(!sf.output[y*SF_OW+x]);
 /* Strict HDR header/payload/length and failed cold-cache behavior. */
 const GlobalAssetResource *r=NULL;for(unsigned i=0;i<GLOBAL_ASSET_RESOURCE_COUNT;i++)if(global_asset_resources[i].identity==90233)r=global_asset_resources+i;REQUIRE(r);
 char path[1200];snprintf(path,sizeof(path),"bad-root/%s",r->path);const char *saved_root=global_root;
 const unsigned offsets[]={0,4,8,12,16,20,24,28,172059};
 for(unsigned i=0;i<sizeof(offsets)/sizeof(*offsets);i++){
  FILE *f=fopen(path,"r+b");REQUIRE(f);fseek(f,offsets[i],SEEK_SET);int v=fgetc(f);fseek(f,offsets[i],SEEK_SET);fputc(v^1,f);fclose(f);
  global_root="bad-root";page();draw_ship();REQUIRE(!shop_ship.rgba&&!ship_commands());finish();
  f=fopen(path,"r+b");REQUIRE(f);fseek(f,offsets[i],SEEK_SET);fputc(v,f);fclose(f);
  pregame_font_product_update_begin();fill_rectangle_xy(VGAScreen,8,8,143,182,0);draw_ship();REQUIRE(!shop_ship.rgba&&!ship_commands());finish();
 }
 FILE *f=fopen(path,"ab");REQUIRE(f);fputc(0,f);fclose(f);page();draw_ship();REQUIRE(!shop_ship.rgba&&!ship_commands());finish();REQUIRE(!truncate(path,172060));
 f=fopen(path,"rb");REQUIRE(f);fseek(f,172059,SEEK_SET);int tail=fgetc(f);fclose(f);REQUIRE(!truncate(path,172059));page();draw_ship();REQUIRE(!shop_ship.rgba&&!ship_commands());finish();f=fopen(path,"ab");REQUIRE(f);fputc(tail,f);fclose(f);
 char moved[1250];snprintf(moved,sizeof(moved),"%s.missing",path);REQUIRE(!rename(path,moved));page();draw_ship();REQUIRE(!shop_ship.rgba&&!ship_commands());finish();REQUIRE(!rename(moved,path));global_root=saved_root;positive();
 for(unsigned mode=0;mode<3;mode++){
  page();reference=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);memcpy(reference->pixels,VGAScreen->pixels,SF_N);sf.active=false;blit_sprite2x2(reference,50,90,spriteSheet9,233);sf.active=true;
  if(mode==0)sf.event_count=SF_EVENTS-1;else if(mode==1)sf.event_count=SF_EVENTS;else sf.count=SF_COMMANDS;
  draw_ship();REQUIRE(!sf.frame&&!memcmp(reference->pixels,VGAScreen->pixels,SF_N));SDL_FreeSurface(reference);
 }
 REQUIRE(pregame_font_retained_bytes()<16*1024*1024);
 pregame_font_end();common_menu_runs_shutdown_all();REQUIRE(!allocated);
 printf("PASS SHOP ship composer %u checks; real ordered quad with synthetic authenticated shop page (not native navigation); exact INDEX8, RGBA, source, records, palette, warm/cold, root/reference, later occlusion, capacity\n",checks);return 0;
}
