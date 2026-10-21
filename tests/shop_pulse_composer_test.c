
#include "pregame_typography_reconstruction.c"
JE_byte shotAvail[MAX_PWEAPON];
PlayerShotDataType playerShotData[MAX_PWEAPON+1];
static void arm_draw(unsigned i,int x,int y){
 shop_pulse_art.armed=true;shop_pulse_art.slot=i;shop_pulse_art.index=global_pulse_source[i].index;shop_pulse_art.x=x;shop_pulse_art.y=y;
 blit_sprite2(VGAScreen,x,y,spriteSheet8,global_pulse_source[i].index);pregame_shop_pulse_head_end();
}
int main(int argc,char **argv){
 REQUIRE(argc==4);REQUIRE(SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);
 fixtures(argv[1]);strings_fixture(argv[1]);memcpy(raw_base,VGAScreen2->pixels,SF_N);strcpy(miscText[13],"DONE");strcpy(miscTextB[5],"POWER:");
 FILE *f=open_data(argv[1],"tyrian.shp");rd16(f);unsigned pos[13];for(unsigned i=0;i<13;i++)pos[i]=rd32(f);spriteSheet8.size=pos[8]-pos[7];spriteSheet8.data=malloc(spriteSheet8.size);fseek(f,pos[7],SEEK_SET);REQUIRE(fread(spriteSheet8.data,1,spriteSheet8.size,f)==spriteSheet8.size);fclose(f);
 REQUIRE(common_menu_runs_set_directory(argv[2]));item_fixture(argv[1],1);itemAvailMax[1]=2;itemAvail[1][0]=1;itemAvail[1][1]=2;player[0].cash=10000;player[0].items.weapon[0].id=1;player[0].items.weapon[0].power=1;
 auth_page(argv[2],3,2,2,"10000",true);assert_page();pregame_shop_pulse_set_directory(argv[3]);REQUIRE(shop_pulse_source_valid());shop_pulse_art_load();REQUIRE(shop_pulse_art_valid());
 for(unsigned i=0;i<5;i++){Uint8 old=shop_pulse_art.rgba[i][0];shop_pulse_art.rgba[i][0]^=1;REQUIRE(!shop_pulse_art_valid());shop_pulse_art.rgba[i][0]=old;REQUIRE(shop_pulse_art_valid());}
 for(unsigned i=0;i<sizeof(global_pulse_palette)/sizeof(*global_pulse_palette);i++){unsigned p=global_pulse_palette[i].index;palettes[0][p].r^=1;REQUIRE(!shop_pulse_art_valid());palettes[0][p].r^=1;REQUIRE(shop_pulse_art_valid());}
 Uint8 *original=spriteSheet8.data,*copy=malloc(spriteSheet8.size);memcpy(copy,original,spriteSheet8.size);spriteSheet8.data=copy;REQUIRE(!shop_pulse_art_valid());spriteSheet8.data=original;free(copy);
 for(unsigned i=0;i<5;i++){unsigned n=global_pulse_source[i].index,at=original[2*(n-1)]|(original[2*(n-1)+1]<<8);Uint8 old=original[at];original[at]=15;REQUIRE(!shop_pulse_art_valid());original[at]=old;REQUIRE(shop_pulse_art_valid());}
 game_probe_original_reference=true;REQUIRE(!shop_pulse_art_valid());game_probe_original_reference=false;game_probe_missing=true;REQUIRE(!shop_pulse_art_valid());game_probe_missing=false;game_probe_invalid=true;REQUIRE(!shop_pulse_art_valid());game_probe_invalid=false;
 pregame_font_product_update_begin();fill_rectangle_xy(VGAScreen,8,8,143,182,0);for(unsigned i=0;i<5;i++)arm_draw(i,25+i*22,45);product_text(PREGAME_CASH,0,65,173,"10000",2,1,6);pregame_font_product_update_end();REQUIRE(shop_pulse_art.hits==5);Uint8 indexed[SF_N];memcpy(indexed,VGAScreen->pixels,SF_N);render();REQUIRE(replay_matches()&&!memcmp(indexed,VGAScreen->pixels,SF_N));uint64_t good=hash((Uint8*)sf.output,SF_OUT_BYTES);
 game_probe_original_reference=true;render();REQUIRE(replay_matches()&&!memcmp(indexed,VGAScreen->pixels,SF_N));REQUIRE(hash((Uint8*)sf.output,SF_OUT_BYTES)!=good);game_probe_original_reference=false;render();REQUIRE(hash((Uint8*)sf.output,SF_OUT_BYTES)!=good);
 /* Transfer sample must reduce exactly once, with no anchor shift, and gain fades color, not alpha. */
 for(unsigned i=0;i<5;i++)for(unsigned y=0;y<56;y++)for(unsigned x=0;x<48;x++){unsigned a,b;sf.metal_gain=255;Uint32 rgb=shop_pulse_sample(shop_pulse_art.rgba[i],x,y,&a);sf.metal_gain=0;REQUIRE(shop_pulse_sample(shop_pulse_art.rgba[i],x,y,&b)==0&&a==b);unsigned sum=0,c[3]={0,0,0};for(unsigned yy=0;yy<2;yy++)for(unsigned xx=0;xx<2;xx++){const Uint8 *v=shop_pulse_art.rgba[i]+((y*2+yy)*96+x*2+xx)*4;sum+=v[3];for(unsigned k=0;k<3;k++)c[k]+=v[k]*v[3];}Uint32 expected=0;if(sum)for(unsigned k=0;k<3;k++)expected|=((c[k]+sum/2)/sum)<<(16-k*8);REQUIRE(rgb==expected&&a==(sum+2)/4);}sf.metal_gain=255;
 pregame_shop_pulse_set_directory(NULL);REQUIRE(!shop_pulse_art_valid()&&!shop_pulse_art.attempted);render();REQUIRE(replay_matches());pregame_shop_pulse_set_directory(argv[3]);shop_pulse_art_load();REQUIRE(shop_pulse_art_valid());


 /* Cold resources: each payload/header corruption is rejected; root reload is explicit. */

 for(unsigned fail=0;fail<5;fail++){pregame_shop_pulse_set_directory(NULL);pregame_shop_pulse_set_directory(argv[3]);fail_allocation=allocation_calls+fail;shop_pulse_art_load();REQUIRE(!shop_pulse_art_valid());for(unsigned j=0;j<5;j++)REQUIRE(!shop_pulse_art.rgba[j]);fail_allocation=UINT_MAX;}
 const char *bad="bad-root";
 for(unsigned i=0;i<5;i++)for(unsigned header=0;header<2;header++){
  char path[1200];snprintf(path,sizeof(path),"%s/%s",bad,shop_pulse_resource(i)->path);FILE *f=fopen(path,"r+b");REQUIRE(f);unsigned at=header?4:28;fseek(f,at,SEEK_SET);int old=fgetc(f);fseek(f,at,SEEK_SET);fputc(old^1,f);fclose(f);
  pregame_shop_pulse_set_directory(NULL);pregame_shop_pulse_set_directory(bad);shop_pulse_art_load();REQUIRE(!shop_pulse_art.good&&!shop_pulse_art_valid());for(unsigned j=0;j<5;j++)REQUIRE(!shop_pulse_art.rgba[j]);
  f=fopen(path,"r+b");REQUIRE(f);fseek(f,at,SEEK_SET);fputc(old,f);fclose(f);
  shop_pulse_art_load();REQUIRE(!shop_pulse_art.good); /* no failed-cache borrowing */
  pregame_shop_pulse_set_directory(NULL);pregame_shop_pulse_set_directory(bad);shop_pulse_art_load();REQUIRE(shop_pulse_art_valid());
 }
 pregame_shop_pulse_set_directory("bad-root-missing");shop_pulse_art_load();REQUIRE(!shop_pulse_art_valid());pregame_shop_pulse_set_directory(argv[3]);shop_pulse_art_load();REQUIRE(shop_pulse_art_valid());
 /* Later original writes must occlude all authored samples in that cell. */
 auth_page(argv[2],3,2,2,"10000",true);pregame_shop_pulse_set_directory(argv[3]);shop_pulse_art_load();pregame_font_product_update_begin();fill_rectangle_xy(VGAScreen,8,8,143,182,0);arm_draw(1,40,40);fill_rectangle_xy(VGAScreen,40,40,51,53,0);product_text(PREGAME_CASH,0,65,173,"10000",2,1,6);pregame_font_product_update_end();render();REQUIRE(replay_matches());for(unsigned y=160;y<216;y++)for(unsigned x=160;x<208;x++)REQUIRE(sf.output[y*SF_OW+x]==0);
 REQUIRE(pregame_font_retained_bytes()<16*1024*1024);
 for(unsigned mode=0;mode<3;mode++){
 auth_page(argv[2],3,2,2,"10000",true);pregame_shop_pulse_set_directory(argv[3]);shop_pulse_art_load();pregame_font_product_update_begin();
 SDL_Surface *expected=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);memcpy(expected->pixels,VGAScreen->pixels,SF_N);blit_sprite2(expected,40,40,spriteSheet8,58);
 if(mode==0)sf.event_count=SF_EVENTS-1;else if(mode==1)sf.event_count=SF_EVENTS;else sf.count=SF_COMMANDS;
 arm_draw(0,40,40);REQUIRE(!sf.frame&&!memcmp(expected->pixels,VGAScreen->pixels,SF_N));SDL_FreeSurface(expected);
 }
 pregame_font_end();common_menu_runs_shutdown_all();REQUIRE(!allocated);printf("PASS independent composer %u checks; five sources/payloads, palette pins, bank identity, reference/operator, warm root and indexed replay; synthetic command arms (not birth evidence)\n",checks);return 0;
}
