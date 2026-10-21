/* Fresh reconstruction checks. The legacy adapter is retained unchanged. */
#define main pregame_baseline_main
#include "pregame_font_test.c"
#undef main
#include "../src/common_pause.h"
/* Pause is a different owner; this fixture deliberately never enables it. */
void common_pause_glyph_begin(SDL_Surface *s,int x,int y,unsigned b,unsigned id,enum CommonPauseGlyph op,unsigned hue,int v){(void)s;(void)x;(void)y;(void)b;(void)id;(void)op;(void)hue;(void)v;}
void common_pause_glyph_end(void){}
void common_pause_cursor_sprite_begin(SDL_Surface *s,int x,int y,const void *d,size_t n,unsigned id){(void)s;(void)x;(void)y;(void)d;(void)n;(void)id;}
void common_pause_cursor_sprite_end(void){}
bool game_probe_original_reference,game_probe_missing,game_probe_invalid;
JE_WeaponType weapons[WEAP_NUM+1];
JE_WeaponPortType weaponPort;
JE_PowerType powerSys;
JE_ShipType ships;
JE_OptionType options[OPTION_NUM+1];
JE_ShieldType shields;
Player player[2];
JE_word upgradeCost,downgradeCost;
JE_byte itemAvail[9][10],itemAvailMax[9];
static const unsigned inventory_map[7]={0,1,2,8,3,5,6};
static unsigned reconstruction_states;
static void item_fixture(const char *dir,unsigned source)
{
 const char *filename=source==1?"tyrian.hdt":source==4?"tyrian4.lvl":"tyrian5.lvl";
 FILE *f=open_data(dir,filename);unsigned offset;
 if(source==1)offset=rd32(f);else{unsigned n=rd16(f);fseek(f,2+4*(n-1),SEEK_SET);offset=rd32(f);}
 offset+=14+1638*80;
 const unsigned counts[6]={61,55,7,19,38,12},strides[6]={82,37,37,41,86,37},costs[6]={76,0,35,38,34,35};
 for(unsigned table=0;table<6;table++)for(unsigned i=0;i<counts[table];i++,offset+=strides[table]){
  if(table==1)continue;char *name;JE_word *cost;
  if(table==0){name=weaponPort[i].name;cost=&weaponPort[i].cost;}
  else if(table==2){name=powerSys[i].name;cost=&powerSys[i].cost;}
  else if(table==3){name=ships[i].name;cost=&ships[i].cost;}
  else if(table==4){name=options[i].name;cost=&options[i].cost;}
  else{name=shields[i].name;cost=&shields[i].cost;}
  fseek(f,offset,SEEK_SET);REQUIRE(fgetc(f)==30);REQUIRE(fread(name,1,30,f)==30);name[30]=0;
  if(table==0)weaponPort[i].opnum=fgetc(f);
  fseek(f,offset+costs[table],SEEK_SET);*cost=rd16(f);
 }
 fclose(f);
}
static unsigned count_tags(unsigned first,unsigned end)
{unsigned count=0;for(unsigned k=0;k<sf.count;k++)count+=sf.commands[k].menu_run>=first&&sf.commands[k].menu_run<end;return count;}
static void auth_page(const char *dir,unsigned category,unsigned selected,unsigned rows,const char *cash,bool enabled)
{
 pregame_font_set_directory(dir);memcpy(VGAScreen->pixels,raw_base,SF_N);memcpy(VGAScreen2->pixels,raw_base,SF_N);live_palette(colors);
 pregame_font_product_begin(category,selected,rows+2,enabled,VGAScreen,VGAScreen2);trace=SF_FNV;trace_count=0;
 const char *title=menuInt[2][category-1];product_text(PREGAME_HEADING,0,234-JE_textWidth(title,0)/2,10,title,0,15,-3);
 for(unsigned row=1;row<=rows+1;row++){
  unsigned item=itemAvail[inventory_map[category-2]][row-1],table,cost=0;const char *name=miscText[13];
  char custom[32];
  if(row<=rows){
   if(category==2&&item>90){snprintf(custom,sizeof(custom),"Custom Ship %u",item-90);name=custom;cost=100;}
   else {unsigned save=sf.category;sf.category=category;REQUIRE(table_item(item,&table,&name,&cost));sf.category=save;}
  }
  unsigned hue=row+1==selected?0:1;int value=(row+1==selected?7:4)-(cost>player[0].cash?4:0),y=40+(row-1)*26;
  if(row==1){fill_rectangle_xy(VGAScreen,160,y+7,300,y+11,227);blit_sprite2(VGAScreen,298,y+2,shopSpriteSheet,247);}
  product_text(PREGAME_PRODUCT_NAME,row,185,y,name,2,hue,value);
  if(row<=rows){char text[20];blit_sprite2x2(VGAScreen,160,y-4,shopSpriteSheet,1);snprintf(text,sizeof(text),"Cost: %u",cost);product_text(PREGAME_PRODUCT_COST,row,187,y+10,text,2,hue,value);}
 }
 product_text(PREGAME_CASH,0,65,173,cash,2,1,6);
 product_text(PREGAME_FOOTER,selected,10,187,mainMenuHelp[selected==rows+2?11:23],2,14,1);pregame_font_frame_end();
}
static void assert_page(void)
{
 REQUIRE(sf.frame&&sf.stage==S_READY&&sf.fixed_ready&&sf.names_ready&&sf.numeric_ready);
 REQUIRE(count_tags(1,PF_NAME_TAG)&&count_tags(PF_NAME_TAG,PF_NUMERIC_TAG)&&count_tags(PF_NUMERIC_TAG,PF_NUMERIC_TAG+PF_NUMBERS));
 SDL_Rect support=render();REQUIRE(support.w>0&&support.h>0&&replay_matches());++reconstruction_states;
}
static void numeric_tick(const char *cash,unsigned power,bool mode,bool omit_down)
{
 player[0].items.weapon[sf.category-3].power=power;pregame_font_product_update_begin();
 fill_rectangle_xy(VGAScreen,8,8,143,182,0);blit_sprite(VGAScreen,0,0,5,12);
 char text[32];
 if(mode)product_text(PREGAME_POWER,3,28,137,miscText[70],2,1,4);
 else{
  if(power>1&&!omit_down){snprintf(text,sizeof(text),"%u",downgradeCost);product_text(PREGAME_POWER,0,26,137,text,2,1,4);}
  if(power<11){snprintf(text,sizeof(text),"%u",upgradeCost);product_text(PREGAME_POWER,1,108,137,text,2,7,4);}
  snprintf(text,sizeof(text),"POWER: %u",power);product_text(PREGAME_POWER,2,58,137,text,2,15,4);
 }
 /* Original cash calculation can overwrite these globals before Present. */
 upgradeCost=17;downgradeCost=23;
 product_text(PREGAME_CASH,0,65,173,cash,2,1,6);pregame_font_product_update_end();
}
static void root_tests(const char *legacy,const char *resources)
{
 const unsigned long amounts[]={0,10000,ULONG_MAX};
 for(unsigned i=0;i<3;i++){
  pregame_font_set_directory(legacy);memcpy(VGAScreen->pixels,raw_base,SF_N);live_palette(colors);
  pregame_font_begin(0,2,7,true,amounts[i],0,VGAScreen,VGAScreen2);char expected[20];int n=snprintf(expected,sizeof(expected),"%lu",amounts[i]);
  REQUIRE(sf.active&&!strcmp(sf.cash,expected)&&sf.root_cash_valid==(n<20));
 }

 REQUIRE(common_menu_runs_set_directory(resources));
 /* Matching 8-bit storage is not sufficient: RGB332 is not INDEX8. */
 Uint32 original_format=VGAScreen->format->format;REQUIRE(original_format==SDL_PIXELFORMAT_INDEX8);
 pregame_font_end();VGAScreen->format->format=SDL_PIXELFORMAT_RGB332;memcpy(VGAScreen->pixels,raw_base,SF_N);pregame_font_begin(0,2,7,true,10000,0,VGAScreen,VGAScreen2);REQUIRE(!sf.active);
 VGAScreen->format->format=original_format;frame_checks(legacy,0,2,0,15,10);REQUIRE(sf.active);
 VGAScreen->format->format=SDL_PIXELFORMAT_RGB332;REQUIRE(!exact()&&!sf.active);VGAScreen->format->format=original_format;
 frame_checks(legacy,0,2,0,15,10);REQUIRE(sf.active&&exact());
 for(unsigned menu=0;menu<2;menu++)for(unsigned selected=2;selected<=(menu?9u:7u);selected++){
  frame_checks(legacy,menu,selected,4,15,10);REQUIRE(sf.fixed_ready&&sf.fixed_count==(menu?9u:7u)&&sf.numeric_ready&&sf.number[5].active);
  SDL_Rect support=render();REQUIRE(replay_matches()&&support.w>0);++reconstruction_states;
 }
 /* Root changes retire borrowed views even if the new directory reloads. */
 REQUIRE(common_menu_runs_set_directory(NULL));REQUIRE(exact());REQUIRE(!sf.fixed_ready&&!sf.numeric_ready&&!count_tags(1,256));render();REQUIRE(replay_matches());
 REQUIRE(common_menu_runs_set_directory(resources));frame_checks(legacy,0,2,0,15,10);REQUIRE(sf.fixed_ready);cursor_checks();present_checks();
}
static void name_tests(const char *data,const char *legacy)
{
 for(unsigned source=1;source<=5;source+=(source==1?3:1)){
  item_fixture(data,source);
  for(unsigned category=2;category<=8;category++){
   unsigned bank=inventory_map[category-2];itemAvailMax[bank]=2;itemAvail[bank][0]=1;itemAvail[bank][1]=2;
   for(unsigned selected=2;selected<=4;selected++){
    player[0].cash=600;auth_page(legacy,category,selected,2,"-2147483648",true);assert_page();
    Uint8 original[SF_N];memcpy(original,sf.pixels,SF_N);uint64_t writes=trace;unsigned count=trace_count;
    auth_page(legacy,category,selected,2,"-2147483648",false);REQUIRE(!memcmp(original,VGAScreen->pixels,SF_N)&&writes==trace&&count==trace_count);
   }
  }
 }
 item_fixture(data,1);unsigned bank=inventory_map[1];itemAvailMax[bank]=5;for(unsigned i=0;i<5;i++)itemAvail[bank][i]=i+1;
 player[0].cash=10000;auth_page(legacy,3,2,5,"10000",true);assert_page();REQUIRE(sf.name_run[4].active&&sf.number[4].active);
 weaponPort[1].name[29]^=1;REQUIRE(exact()&&sf.fixed_ready&&!sf.names_ready&&!sf.numeric_ready);REQUIRE(!count_tags(PF_NAME_TAG,256));weaponPort[1].name[29]^=1;
 auth_page(legacy,3,2,5,"10000",true);assert_page();player[0].cash=0;REQUIRE(exact()&&sf.fixed_ready&&!sf.names_ready&&!sf.numeric_ready);
 player[0].cash=10000;auth_page(legacy,3,2,5,"10000",true);assert_page();itemAvail[bank][1]=3;REQUIRE(exact()&&sf.fixed_ready&&!sf.names_ready&&!sf.numeric_ready);itemAvail[bank][1]=2;
 /* A custom ship is not an OSIfont name but its original base cost is100. */
 itemAvailMax[0]=1;itemAvail[0][0]=91;auth_page(legacy,2,2,1,"999",true);REQUIRE(sf.frame&&sf.fixed_ready&&!sf.names_ready&&sf.numeric_ready&&sf.number[0].active);render();REQUIRE(replay_matches());
}
static void save_picture(const char *filename)
{
 const char *out=getenv("TYRIAN_TEST_OUTPUT");char resolved[1024];
 if(!out)return;
 const char *base=strrchr(filename,'/');base=base?base+1:filename;
 REQUIRE(snprintf(resolved,sizeof(resolved),"%s/%s",out,base)>0);filename=resolved;
 SDL_Surface *picture=SDL_CreateRGBSurfaceWithFormat(0,SF_OW,SF_OH,32,SDL_PIXELFORMAT_ARGB8888);REQUIRE(picture);
 for(unsigned y=0;y<SF_OH;y++)for(unsigned x=0;x<SF_OW;x++){
  Uint32 layer=sf.output[y*SF_OW+x],base=sf.palette[sf.underlay[(y/4)*SF_W+x/4]],pixel=0xff000000;
  for(unsigned shift=0;shift<=16;shift+=8)pixel|=(((layer>>shift)&255)+(((base>>shift)&255)*(255-(layer>>24))+127)/255)<<shift;
  ((Uint32 *)((Uint8 *)picture->pixels+y*picture->pitch))[x]=pixel;
 }
 REQUIRE(SDL_SaveBMP(picture,filename)==0);SDL_FreeSurface(picture);
}
static void ordered_support_tests(const char *legacy)
{
 itemAvailMax[1]=2;itemAvail[1][0]=1;itemAvail[1][1]=2;player[0].cash=10000;
 auth_page(legacy,3,2,2,"10000",true);assert_page();render();
 const struct PfRun *name=&sf.name_run[0];unsigned chosen=SF_N,marker_ink=0;
 for(unsigned y=0;y<name->run.height;y++)for(unsigned x=0;x<name->run.width;x++)if(name->run.alpha[y*name->run.pitch+x]){
  unsigned p=((name->y+y)/4)*SF_W+(name->x+x)/4;if(chosen==SF_N)chosen=p;
  unsigned sy=name->y+y+name->shadow,sp=(sy/4)*SF_W+(name->x+x+name->shadow)/4;
  if(sy/4>=47&&sy/4<=51&&sf.underlay[sp]==227)marker_ink++;
 }
 REQUIRE(chosen<SF_N&&marker_ink>0);
 /* Marker ink is earlier than the name; a later equal-index event is later
  * than both and must clear the entire logical cell, not only changed bits. */
 Uint8 same=((Uint8 *)sf.pixels)[chosen];sf.stage=S_BUILD;JE_pix(VGAScreen,chosen%SF_W,chosen/SF_W,same);sf.stage=S_READY;REQUIRE(exact());render();
 for(unsigned y=0;y<4;y++)for(unsigned x=0;x<4;x++)REQUIRE(!sf.output[((chosen/SF_W)*4+y)*SF_OW+(chosen%SF_W)*4+x]);
 REQUIRE(replay_matches());++reconstruction_states;
 /* The committed owner also survives native cursor draw/erase and Present. */
 auth_page(legacy,3,2,2,"10000",true);assert_page();cursor_checks();present_checks();render();REQUIRE(replay_matches());
 save_picture("../recovery-validation-20261020/pregame-typography/product-front-gun.bmp");
}
static void all_mapping_tests(const char *data)
{
 unsigned admitted=0;bool displays[113]={0};
 for(unsigned source=1;source<=5;source+=(source==1?3:1)){
  item_fixture(data,source);
  for(unsigned n=0;n<CMR3_NAME_SOURCE_COUNT;n++){
   const struct Cmr3NameSource *entry=&cmr3_name_sources[n];if(entry->source_bank!=source)continue;
   unsigned category=2;while(!(entry->category_mask&(1u<<category)))++category;
   unsigned bank=inventory_map[category-2];itemAvailMax[bank]=1;itemAvail[bank][0]=entry->item;
   sf.category=category;sf.last=3;struct PfNameProof p;REQUIRE(item_proof(1,&p,false));
   REQUIRE(p.item==entry->item&&p.cost==entry->base_cost&&cmr3_name_sources[p.source].run==entry->run);displays[entry->run]=true;++admitted;
  }
 }
 REQUIRE(admitted==411);for(unsigned i=0;i<113;i++)REQUIRE(displays[i]);pregame_font_end();item_fixture(data,1);
}
static void isolation_tests(const char *legacy,const char *resources)
{
 const char *family[6]={"esc","main","shop","category","product","names"};const unsigned counts[6]={16,7,7,9,19,113};
 char temp[]="/tmp/pregame-family-test-XXXXXX",source[2048],target[2048],root[2048],cwd[1024];REQUIRE(mkdtemp(temp));REQUIRE(getcwd(cwd,sizeof(cwd)));
 if(resources[0]=='/')snprintf(root,sizeof(root),"%s",resources);else snprintf(root,sizeof(root),"%s/%s",cwd,resources);
 for(unsigned f=0;f<6;f++)for(unsigned i=0;i<counts[f];i++){
  int a=snprintf(source,sizeof(source),"%s/%s-run-%02u.rfr",root,family[f],i),b=snprintf(target,sizeof(target),"%s/%s-run-%02u.rfr",temp,family[f],i);REQUIRE(a>0&&a<(int)sizeof(source)&&b>0&&b<(int)sizeof(target)&&!symlink(source,target));
 }
 REQUIRE(snprintf(source,sizeof(source),"%s/numeric-runs-v1.nfr",root)<(int)sizeof(source));snprintf(target,sizeof(target),"%s/numeric-runs-v1.nfr",temp);REQUIRE(!symlink(source,target));
 itemAvailMax[1]=2;itemAvail[1][0]=1;itemAvail[1][1]=2;player[0].cash=10000;
 const char *missing[3]={"names-run-00.rfr","numeric-runs-v1.nfr","product-run-00.rfr"};
 for(unsigned family_id=0;family_id<3;family_id++){
  snprintf(target,sizeof(target),"%s/%s",temp,missing[family_id]);REQUIRE(!unlink(target));
  for(unsigned corrupt=0;corrupt<2;corrupt++){
   if(corrupt)write_bytes(target,(const Uint8 *)"broken",6);
   REQUIRE(common_menu_runs_set_directory(NULL));REQUIRE(common_menu_runs_set_directory(temp));auth_page(legacy,3,2,2,"999",true);
   REQUIRE(sf.frame&&sf.fixed_ready==(family_id!=2)&&sf.names_ready==(family_id!=0)&&sf.numeric_ready==(family_id!=1));render();REQUIRE(replay_matches());++reconstruction_states;
  }
  REQUIRE(!unlink(target));REQUIRE(snprintf(source,sizeof(source),"%s/%s",root,missing[family_id])<(int)sizeof(source));REQUIRE(!symlink(source,target));
 }
 REQUIRE(common_menu_runs_set_directory(resources));
 for(unsigned f=0;f<6;f++)for(unsigned i=0;i<counts[f];i++){snprintf(target,sizeof(target),"%s/%s-run-%02u.rfr",temp,family[f],i);REQUIRE(!unlink(target));}
 snprintf(target,sizeof(target),"%s/numeric-runs-v1.nfr",temp);REQUIRE(!unlink(target)&&!rmdir(temp));
}
static void number_tests(const char *legacy)
{
 itemAvailMax[1]=2;itemAvail[1][0]=1;itemAvail[1][1]=2;player[0].cash=10000;player[0].items.weapon[0].id=1;
 const char *valid[]={"0","1","-1","2147483647","-2147483648"};
 const char *invalid[]={"-0","00","01","2147483648","-2147483649","999999999999999999999999"};
 for(unsigned i=0;i<sizeof(valid)/sizeof(*valid);i++){auth_page(legacy,3,2,2,valid[i],true);assert_page();}
 for(unsigned i=0;i<sizeof(invalid)/sizeof(*invalid);i++){auth_page(legacy,3,2,2,invalid[i],true);REQUIRE(sf.frame&&sf.fixed_ready&&sf.names_ready&&!sf.numeric_ready);render();REQUIRE(replay_matches());}
 for(unsigned power=1;power<=11;power++){
  player[0].items.weapon[0].power=power;auth_page(legacy,3,2,2,"10000",true);assert_page();upgradeCost=65535;downgradeCost=32768;
  numeric_tick("999",power,false,false);REQUIRE(sf.frame&&sf.fixed_ready&&sf.names_ready&&sf.numeric_ready);REQUIRE(sf.number[5].active&&sf.number[6].active==(power>1)&&sf.number[7].active==(power<11));
  char expected_power[32];snprintf(expected_power,sizeof(expected_power),"POWER: %u",power);REQUIRE(!strcmp(sf.fixed[sf.static_fixed].run.text,expected_power));render();REQUIRE(replay_matches());++reconstruction_states;
  unsigned count=sf.count;upgradeCost=1;downgradeCost=2;numeric_tick("9",power,false,false);
  REQUIRE(sf.frame&&sf.numeric_ready&&sf.count<count&&sf.number[6].active==(power>1)&&sf.number[7].active==(power<11)&&sf.fixed_count==sf.static_fixed+1);render();REQUIRE(replay_matches());
 }
 player[0].items.weapon[0].power=2;auth_page(legacy,3,2,2,"10000",true);numeric_tick("999",2,false,true);REQUIRE(sf.frame&&sf.fixed_ready&&sf.names_ready&&!sf.numeric_ready);
 /* Real non-simulation pages repeat Cash without a rectangle clear. */
 itemAvailMax[0]=1;itemAvail[0][0]=1;auth_page(legacy,2,2,1,"999",true);
 for(unsigned tick=0;tick<3;tick++){pregame_font_product_update_begin();product_text(PREGAME_CASH,0,65,173,"999",2,1,6);pregame_font_product_update_end();REQUIRE(sf.frame&&sf.numeric_ready&&!sf.number[6].active&&!sf.number[7].active&&sf.fixed_count==sf.static_fixed);render();REQUIRE(replay_matches());}
 /* A malformed callback may use SFN fallback, never the narrow numeric Cash
  * replay exception. Repeated original DARKEN must therefore fail replay. */
 auth_page(legacy,2,2,1,"ABC",true);REQUIRE(sf.frame&&sf.fixed_ready&&sf.names_ready&&!sf.numeric_ready);
 for(unsigned k=0;k<sf.count;k++)REQUIRE(!sf.commands[k].cash);
 pregame_font_product_update_begin();product_text(PREGAME_CASH,0,65,173,"ABC",2,1,6);pregame_font_product_update_end();REQUIRE(sf.frame);render();REQUIRE(!replay_matches());
 /* No forged rear-None numeric or POWER replacements. */
 itemAvailMax[2]=1;itemAvail[2][0]=0;player[0].items.weapon[1].id=0;player[0].items.weapon[1].power=2;auth_page(legacy,4,2,1,"999",true);numeric_tick("999",2,false,false);REQUIRE(sf.frame&&!sf.numeric_ready&&!sf.fixed_ready&&sf.names_ready);
}
static void reference_page(const char *legacy,unsigned page)
{
 if(page<2)frame_checks(legacy,page,2,0,15,10);
 else auth_page(legacy,3,2,2,"10000",true);
 REQUIRE(sf.active&&sf.frame&&exact());render();REQUIRE(replay_matches());
}
static void reference_tests(const char *data,const char *legacy,const char *resources)
{
 item_fixture(data,1);itemAvailMax[1]=2;itemAvail[1][0]=1;itemAvail[1][1]=2;player[0].cash=10000;
 for(unsigned page=0;page<3;page++){
  game_probe_original_reference=false;REQUIRE(common_menu_runs_set_directory(NULL));reference_page(legacy,page);
  uint64_t legacy_output=hash(sf.output,SF_OUT_BYTES),legacy_index=hash(sf.pixels,SF_N);
  for(unsigned warm=0;warm<2;warm++){
   REQUIRE(common_menu_runs_set_directory(NULL));REQUIRE(common_menu_runs_set_directory(resources));
   if(warm){for(unsigned f=COMMON_MENU_SHOP;f<COMMON_MENU_FAMILY_COUNT;f++)REQUIRE(common_menu_runs_load(f));REQUIRE(common_menu_numeric_runs_load());}
   game_probe_original_reference=true;reference_page(legacy,page);
   REQUIRE(!sf.fixed_ready&&!sf.names_ready&&!sf.numeric_ready&&!count_tags(1,256));
   REQUIRE(hash(sf.output,SF_OUT_BYTES)==legacy_output&&hash(sf.pixels,SF_N)==legacy_index);
   if(!warm){REQUIRE(!common_menu_runs_ready(page==0?COMMON_MENU_SHOP:page==1?COMMON_MENU_CATEGORY:COMMON_MENU_PRODUCT));REQUIRE(!common_menu_numeric_runs_ready());}
   ++reconstruction_states;
  }
  game_probe_original_reference=false;reference_page(legacy,page);REQUIRE(sf.fixed_ready&&sf.numeric_ready&&count_tags(1,256));if(page==2)REQUIRE(sf.names_ready);
  game_probe_original_reference=true;REQUIRE(exact()&&sf.active&&sf.frame);render();REQUIRE(replay_matches());
  REQUIRE(!sf.fixed_ready&&!sf.names_ready&&!sf.numeric_ready&&!count_tags(1,256)&&hash(sf.output,SF_OUT_BYTES)==legacy_output);
  game_probe_original_reference=false;REQUIRE(exact());render();REQUIRE(replay_matches()&&!count_tags(1,256)&&hash(sf.output,SF_OUT_BYTES)==legacy_output);
  reference_page(legacy,page);REQUIRE(sf.fixed_ready&&sf.numeric_ready&&count_tags(1,256));++reconstruction_states;
 }
 game_probe_original_reference=false;
}
int main(int argc,char **argv)
{
 if(argc==4&&!strcmp(argv[1],"--legacy"))return pregame_baseline_main(argc-1,argv+1);
 REQUIRE(argc==4);REQUIRE(SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);REQUIRE(VGAScreen&&VGAScreen2);main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);REQUIRE(main_window_tex_format);
 fixtures(argv[1]);strings_fixture(argv[1]);memcpy(raw_base,VGAScreen2->pixels,SF_N);strcpy(miscText[13],"DONE");strcpy(miscTextB[5],"POWER:");strcpy(miscText[70],"[/] Rear Weapon Mode");
 reference_tests(argv[1],argv[2],argv[3]);root_tests(argv[2],argv[3]);name_tests(argv[1],argv[2]);number_tests(argv[2]);ordered_support_tests(argv[2]);all_mapping_tests(argv[1]);
 itemAvailMax[6]=4;itemAvail[6][0]=9;itemAvail[6][1]=20;itemAvail[6][2]=30;itemAvail[6][3]=0;player[0].cash=10000;
 auth_page(argv[2],8,2,4,"500",true);assert_page();save_picture("../recovery-validation-20261020/pregame-typography/product-right-plasma-typography.bmp");
 isolation_tests(argv[2],argv[3]);
 for(unsigned family=0;family<COMMON_MENU_FAMILY_COUNT;family++)REQUIRE(common_menu_runs_load(family));REQUIRE(common_menu_numeric_runs_load());
 size_t retained=pregame_font_retained_bytes();REQUIRE(retained<16*1024*1024);
 printf("PASS reconstructed pregame: %u states %u checks; retained=%zu common_all=%zu numeric=%zu owner_static=%zu\n",reconstruction_states,checks,retained,common_menu_runs_retained_bytes(),common_menu_numeric_runs_retained_bytes(),pregame_font_static_bytes());
 pregame_font_end();common_menu_runs_shutdown_all();REQUIRE(!allocated);
 for(unsigned b=0;b<7;b++)for(unsigned id=0;id<sprite_table[b].count;id++)free(sprite(b,id)->data);free(shopSpriteSheet.data);SDL_FreeSurface(VGAScreen);SDL_FreeSurface(VGAScreen2);SDL_FreeFormat(main_window_tex_format);SDL_Quit();return 0;
}
