
static unsigned test_quad=169;
#include "pregame_typography_reconstruction.c"
JE_byte shotAvail[MAX_PWEAPON];
PlayerShotDataType playerShotData[MAX_PWEAPON+1];
static void arm_draw(unsigned i,int x,int y){
 shop_vulcan_art.armed=true;shop_vulcan_art.slot=i;shop_vulcan_art.index=global_vulcan_source[i].index;shop_vulcan_art.x=x;shop_vulcan_art.y=y;
 blit_sprite2(VGAScreen,x,y,spriteSheet8,global_vulcan_source[i].index);pregame_shop_vulcan_head_end();
}
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
static void vulcan_page(const char *startup,const char *root){
 auth_page(startup,3,2,2,"10000",true);assert_page();pregame_shop_vulcan_set_directory(root);
 pregame_font_product_update_begin();pregame_shop_vulcan_preview_begin();fill_rectangle_xy(VGAScreen,8,8,143,182,0);shop_vulcan_art_load();REQUIRE(shop_vulcan_art_valid());
}
static void vulcan_finish(void){pregame_shop_vulcan_preview_end();product_text(PREGAME_CASH,0,65,173,"10000",2,1,6);pregame_font_product_update_end();REQUIRE(sf.frame);render();REQUIRE(replay_matches());}
static uint64_t vulcan_positive(const char *startup,const char *root){vulcan_page(startup,root);arm_draw(0,65,166);vulcan_finish();REQUIRE(shop_vulcan_art.contributed);return hash(sf.output,SF_OUT_BYTES);}
int main(int argc,char **argv){
 REQUIRE(argc==4);REQUIRE(SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);
 fixtures(argv[1]);strings_fixture(argv[1]);memcpy(raw_base,VGAScreen2->pixels,SF_N);strcpy(miscText[13],"DONE");strcpy(miscTextB[5],"POWER:");
 FILE *f=open_data(argv[1],"tyrian.shp");rd16(f);unsigned pos[13];for(unsigned i=0;i<13;i++)pos[i]=rd32(f);spriteSheet8.size=pos[8]-pos[7];spriteSheet8.data=malloc(spriteSheet8.size);fseek(f,pos[7],SEEK_SET);REQUIRE(fread(spriteSheet8.data,1,spriteSheet8.size,f)==spriteSheet8.size);fclose(f);
 REQUIRE(common_menu_runs_set_directory(argv[2]));item_fixture(argv[1],1);load_ship_fixture(argv[1]);player[0].items.ship=1;player[0].x=55;player[0].y=97;itemAvailMax[1]=2;itemAvail[1][0]=1;itemAvail[1][1]=2;player[0].cash=10000;player[0].items.weapon[0].id=1;player[0].items.weapon[0].power=1;
 auth_page(argv[2],3,2,2,"10000",true);assert_page();pregame_shop_vulcan_set_directory(argv[3]);REQUIRE(shop_vulcan_source_valid());shop_vulcan_art_load();REQUIRE(shop_vulcan_art_valid());
 for(unsigned i=0;i<2;i++){Uint8 old=shop_vulcan_art.rgba[i][0];shop_vulcan_art.rgba[i][0]^=1;REQUIRE(!shop_vulcan_art_valid());shop_vulcan_art.rgba[i][0]=old;REQUIRE(shop_vulcan_art_valid());}
 for(unsigned i=0;i<sizeof(global_vulcan_palette)/sizeof(*global_vulcan_palette);i++){unsigned p=global_vulcan_palette[i].index;palettes[0][p].r^=1;REQUIRE(!shop_vulcan_art_valid());palettes[0][p].r^=1;REQUIRE(shop_vulcan_art_valid());}
 Uint8 *original=spriteSheet8.data,*copy=malloc(spriteSheet8.size);memcpy(copy,original,spriteSheet8.size);spriteSheet8.data=copy;REQUIRE(!shop_vulcan_art_valid());spriteSheet8.data=original;free(copy);
 for(unsigned i=0;i<2;i++){unsigned n=global_vulcan_source[i].index,at=original[2*(n-1)]|(original[2*(n-1)+1]<<8);Uint8 old=original[at];original[at]=15;REQUIRE(!shop_vulcan_art_valid());original[at]=old;REQUIRE(shop_vulcan_art_valid());}
 game_probe_original_reference=true;REQUIRE(!shop_vulcan_art_valid());game_probe_original_reference=false;game_probe_missing=true;REQUIRE(!shop_vulcan_art_valid());game_probe_missing=false;game_probe_invalid=true;REQUIRE(!shop_vulcan_art_valid());game_probe_invalid=false;
 pregame_font_product_update_begin();pregame_shop_vulcan_preview_begin();fill_rectangle_xy(VGAScreen,8,8,143,182,0);for(unsigned i=0;i<2;i++)arm_draw(i,25+i*22,45);product_text(PREGAME_CASH,0,65,173,"10000",2,1,6);pregame_shop_vulcan_preview_end();pregame_font_product_update_end();REQUIRE(shop_vulcan_art.hits==2);Uint8 indexed[SF_N];memcpy(indexed,VGAScreen->pixels,SF_N);render();REQUIRE(replay_matches()&&!memcmp(indexed,VGAScreen->pixels,SF_N));uint64_t good=hash((Uint8*)sf.output,SF_OUT_BYTES);
 game_probe_original_reference=true;render();REQUIRE(replay_matches()&&!memcmp(indexed,VGAScreen->pixels,SF_N));REQUIRE(hash((Uint8*)sf.output,SF_OUT_BYTES)!=good);game_probe_original_reference=false;render();REQUIRE(hash((Uint8*)sf.output,SF_OUT_BYTES)!=good);
 /* Transfer sample must reduce exactly once, with no anchor shift, and gain fades color, not alpha. */
 for(unsigned i=0;i<2;i++)for(unsigned y=0;y<56;y++)for(unsigned x=0;x<48;x++){unsigned a,b;sf.metal_gain=255;Uint32 rgb=shop_vulcan_sample(shop_vulcan_art.rgba[i],x,y,&a);sf.metal_gain=0;REQUIRE(shop_vulcan_sample(shop_vulcan_art.rgba[i],x,y,&b)==0&&a==b);unsigned sum=0,c[3]={0,0,0};for(unsigned yy=0;yy<2;yy++)for(unsigned xx=0;xx<2;xx++){const Uint8 *v=shop_vulcan_art.rgba[i]+((y*2+yy)*96+x*2+xx)*4;sum+=v[3];for(unsigned k=0;k<3;k++)c[k]+=v[k]*v[3];}Uint32 expected=0;if(sum)for(unsigned k=0;k<3;k++)expected|=((c[k]+sum/2)/sum)<<(16-k*8);REQUIRE(rgb==expected&&a==(sum+2)/4);}sf.metal_gain=255;
 pregame_shop_vulcan_set_directory(NULL);REQUIRE(!shop_vulcan_art_valid()&&!shop_vulcan_art.attempted);render();REQUIRE(replay_matches());pregame_shop_vulcan_set_directory(argv[3]);shop_vulcan_art_load();REQUIRE(!shop_vulcan_art_valid());pregame_shop_vulcan_preview_begin();pregame_shop_vulcan_preview_end();REQUIRE(shop_vulcan_art_valid());


 /* Cold resources: each payload/header corruption is rejected; root reload is explicit. */

 for(unsigned fail=0;fail<2;fail++){pregame_shop_vulcan_set_directory(NULL);pregame_shop_vulcan_set_directory(argv[3]);fail_allocation=allocation_calls+fail;shop_vulcan_art_load();REQUIRE(!shop_vulcan_art_valid());for(unsigned j=0;j<2;j++)REQUIRE(!shop_vulcan_art.rgba[j]);fail_allocation=UINT_MAX;}
 const char *bad="bad-root";
 const unsigned corrupt_offsets[]={0,4,8,12,16,20,24,28,43035};
 for(unsigned i=0;i<2;i++)for(unsigned header=0;header<sizeof(corrupt_offsets)/sizeof(*corrupt_offsets);header++){
  char path[1200];snprintf(path,sizeof(path),"%s/%s",bad,shop_vulcan_resource(i)->path);FILE *f=fopen(path,"r+b");REQUIRE(f);unsigned at=corrupt_offsets[header];fseek(f,at,SEEK_SET);int old=fgetc(f);fseek(f,at,SEEK_SET);fputc(old^1,f);fclose(f);
  pregame_shop_vulcan_set_directory(NULL);pregame_shop_vulcan_set_directory(bad);shop_vulcan_art_load();REQUIRE(!shop_vulcan_art.good&&!shop_vulcan_art_valid());for(unsigned j=0;j<2;j++)REQUIRE(!shop_vulcan_art.rgba[j]);
  f=fopen(path,"r+b");REQUIRE(f);fseek(f,at,SEEK_SET);fputc(old,f);fclose(f);
  shop_vulcan_art_load();REQUIRE(!shop_vulcan_art.good); /* no failed-cache borrowing */
  pregame_shop_vulcan_set_directory(NULL);pregame_shop_vulcan_set_directory(bad);shop_vulcan_art_load();REQUIRE(shop_vulcan_art_valid());
 }
 for(unsigned i=0;i<2;i++){
  char path[1200],moved[1250];snprintf(path,sizeof(path),"bad-root/%s",shop_vulcan_resource(i)->path);snprintf(moved,sizeof(moved),"%s.missing",path);
  FILE *f=fopen(path,"ab");REQUIRE(f);fputc(0,f);fclose(f);pregame_shop_vulcan_set_directory(NULL);pregame_shop_vulcan_set_directory(bad);shop_vulcan_art_load();REQUIRE(!shop_vulcan_art_valid());REQUIRE(!truncate(path,43036));
  f=fopen(path,"rb");REQUIRE(f);fseek(f,43035,SEEK_SET);int tail=fgetc(f);fclose(f);REQUIRE(!truncate(path,43035));pregame_shop_vulcan_set_directory(NULL);pregame_shop_vulcan_set_directory(bad);shop_vulcan_art_load();REQUIRE(!shop_vulcan_art_valid());f=fopen(path,"ab");REQUIRE(f);fputc(tail,f);fclose(f);
  REQUIRE(!rename(path,moved));pregame_shop_vulcan_set_directory(NULL);pregame_shop_vulcan_set_directory(bad);shop_vulcan_art_load();REQUIRE(!shop_vulcan_art_valid());REQUIRE(!rename(moved,path));
 }
 pregame_shop_vulcan_set_directory("bad-root-missing");shop_vulcan_art_load();REQUIRE(!shop_vulcan_art_valid());pregame_shop_vulcan_set_directory(argv[3]);shop_vulcan_art_load();REQUIRE(shop_vulcan_art_valid());
 /* Later original writes must occlude all authored samples in that cell. */
 auth_page(argv[2],3,2,2,"10000",true);pregame_shop_vulcan_set_directory(argv[3]);shop_vulcan_art_load();pregame_font_product_update_begin();pregame_shop_vulcan_preview_begin();fill_rectangle_xy(VGAScreen,8,8,143,182,0);arm_draw(1,40,40);fill_rectangle_xy(VGAScreen,40,40,51,53,0);product_text(PREGAME_CASH,0,65,173,"10000",2,1,6);pregame_shop_vulcan_preview_end();pregame_font_product_update_end();render();REQUIRE(replay_matches());for(unsigned y=160;y<216;y++)for(unsigned x=160;x<208;x++)REQUIRE(sf.output[y*SF_OW+x]==0);

 /* A projectile below later antialiased cash text may be copied into its
  * underlay. Invalidating the owner still retires that copied contribution. */
 for(unsigned failure=0;failure<7;failure++){
  uint64_t positive=vulcan_positive(argv[2],argv[3]);Uint8 *oldbank=spriteSheet8.data;
  Uint8 oldbyte=0;unsigned at=oldbank[2*(67-1)]|(oldbank[2*(67-1)+1]<<8);
  if(failure==0)game_probe_original_reference=true;
  if(failure==1)game_probe_missing=true;
  if(failure==2)game_probe_invalid=true;
  if(failure==3)shop_vulcan_art.rgba[0][777]^=1;
  if(failure==4)palettes[0][113].r^=1;
  if(failure==5){oldbyte=oldbank[at];oldbank[at]=15;}
  if(failure==6)spriteSheet8.size--;
  render();REQUIRE(replay_matches()&&shop_vulcan_art.frame_fault);uint64_t retired=hash(sf.output,SF_OUT_BYTES);REQUIRE(retired!=positive);
  if(failure==0)game_probe_original_reference=false;
  if(failure==1)game_probe_missing=false;
  if(failure==2)game_probe_invalid=false;
  if(failure==3)shop_vulcan_art.rgba[0][777]^=1;
  if(failure==4)palettes[0][113].r^=1;
  if(failure==5)oldbank[at]=oldbyte;
  if(failure==6)spriteSheet8.size++;
  render();REQUIRE(replay_matches()&&hash(sf.output,SF_OUT_BYTES)==retired&&!shop_vulcan_art_valid());
 }
 /* A second failed candidate must retire an earlier contribution before
  * an early return. Restoring the witness before render is not revival. */
 for(unsigned hook=0;hook<2;hook++)for(unsigned failure=0;failure<4;failure++){
  vulcan_page(argv[2],argv[3]);arm_draw(0,65,166);
  if(failure==0)game_probe_original_reference=true;if(failure==1)game_probe_missing=true;if(failure==2)game_probe_invalid=true;if(failure==3)spriteSheet8.size--;
  if(!hook)pregame_shop_vulcan_head_begin(0,70,85,166);
  else {shop_vulcan_art.armed=true;shop_vulcan_art.slot=1;shop_vulcan_art.index=70;shop_vulcan_art.x=85;shop_vulcan_art.y=166;shop_vulcan_blit_begin(VGAScreen,85,166,spriteSheet8.data,spriteSheet8.size,70);}
  REQUIRE(shop_vulcan_art.frame_fault&&!shop_vulcan_art.armed);
  if(failure==0)game_probe_original_reference=false;if(failure==1)game_probe_missing=false;if(failure==2)game_probe_invalid=false;if(failure==3)spriteSheet8.size++;
  vulcan_finish();REQUIRE(!shop_vulcan_art_valid());
 }
 vulcan_positive(argv[2],argv[3]);pregame_shop_vulcan_set_directory(NULL);render();uint64_t retired=hash(sf.output,SF_OUT_BYTES);pregame_shop_vulcan_set_directory(argv[3]);shop_vulcan_art_load();render();REQUIRE(replay_matches()&&shop_vulcan_art.frame_fault&&hash(sf.output,SF_OUT_BYTES)==retired);
 /* Independent Pulse and Vulcan command streams share neither permission nor
  * fault; this synthetic compositor case is not a simultaneous item claim. */
 vulcan_page(argv[2],argv[3]);pregame_shop_pulse_set_directory(argv[3]);pregame_shop_pulse_preview_begin();shop_pulse_art_load();REQUIRE(shop_pulse_art_valid());
 arm_draw(0,40,40);shop_pulse_art.armed=true;shop_pulse_art.slot=0;shop_pulse_art.index=58;shop_pulse_art.x=44;shop_pulse_art.y=44;blit_sprite2(VGAScreen,44,44,spriteSheet8,58);pregame_shop_pulse_head_end();arm_draw(1,48,48);pregame_shop_ship_set_directory(argv[3]);pregame_shop_ship_begin(1,50,90);blit_sprite2x2(VGAScreen,50,90,spriteSheet9,233);pregame_shop_ship_end();vulcan_finish();
 unsigned vc=0,pc=0,sc=0,hc=0;for(unsigned i=0;i<sf.count;i++){vc+=sf.commands[i].kind==C_VULCAN;pc+=sf.commands[i].kind==C_PULSE;sc+=sf.commands[i].kind==C_STATIC;hc+=sf.commands[i].kind==C_SHIP;}REQUIRE(vc==2&&pc==1&&sc==2&&hc==1&&shop_pulse_art_valid());
 shop_vulcan_art.rgba[0][777]^=1;render();REQUIRE(replay_matches()&&!shop_vulcan_art_valid()&&shop_pulse_art_valid());shop_vulcan_art.rgba[0][777]^=1;
 REQUIRE(pregame_font_retained_bytes()<16*1024*1024);
 for(unsigned mode=0;mode<3;mode++){
 auth_page(argv[2],3,2,2,"10000",true);pregame_shop_vulcan_set_directory(argv[3]);shop_vulcan_art_load();pregame_font_product_update_begin();pregame_shop_vulcan_preview_begin();
 SDL_Surface *expected=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);memcpy(expected->pixels,VGAScreen->pixels,SF_N);blit_sprite2(expected,40,40,spriteSheet8,67);
 if(mode==0)sf.event_count=SF_EVENTS-1;else if(mode==1)sf.event_count=SF_EVENTS;else sf.count=SF_COMMANDS;
 arm_draw(0,40,40);REQUIRE(!sf.frame&&!memcmp(expected->pixels,VGAScreen->pixels,SF_N));SDL_FreeSurface(expected);
 }
 pregame_font_end();common_menu_runs_shutdown_all();REQUIRE(!allocated);printf("PASS independent composer %u checks; two sources/payloads, palette pins, bank identity, reference/operator, warm root and indexed replay; synthetic command arms (not birth evidence)\n",checks);return 0;
}
