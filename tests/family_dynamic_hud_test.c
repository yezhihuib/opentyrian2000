/* Original-input integration oracle: actual loaders, current native indices,
 * real semantic notifications, and the production family output adapter. */
#define main static_hud_baseline_main
#include "family_static_hud_test.c"
#undef main
static void meter(unsigned kind,unsigned value)
{
 int top=kind==HUD_WRITE_FRONT?17:38;
 fdh_meter_begin(VGAScreenSeg,VGAScreenSeg,kind,value,0);
 for(int y=top;y<top+3;y++)for(int x=289;x<311;x++)
  ((Uint8 *)VGAScreenSeg->pixels)[y*320+x]=(x-289)/2<(int)value?116+(x-289)/2:0;
 fdh_meter_end(VGAScreenSeg,kind);
}
static void verify_dynamic(void)
{
 CHECK(fdh_prepare());unsigned cells=0;
 SDL_FillRect(output,NULL,0x12345678);
 family_static_hud_compose();
 for(int y=0;y<200;y++)for(int x=0;x<320;x++){
  Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[y*320+x];
  const Uint8 *p=fdh_sample(x,y,0,0,index);
  if(p)cells++;
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
   Uint32 actual=((Uint32 *)((Uint8 *)output->pixels+(y*8+sy)*output->pitch))[x*8+sx];
   const Uint8 *q=p?fdh_sample(x,y,sx,sy,index):NULL;
   Uint32 expected=q?(0xff000000u|((Uint32)q[0]<<16)|((Uint32)q[1]<<8)|q[2]):
    x<264&&y<184?0x12345678:sample_expected(x,y,sx,sy);
   CHECK(actual==expected);
  }
 }
 CHECK(cells>=741); /* 350 labels + 370 fixed text + 21 top lens. */
}
int main(int argc,char **argv)
{
 CHECK(argc==2);load_original();CHECK(SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 output=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);
 CHECK(VGAScreenSeg&&output);
 SDL_setenv("BUILDING313_FAMILY_HUD_ENABLE","1",1);
 SDL_setenv("BUILDING313_FAMILY_DYNAMIC_HUD_ENABLE","1",1);reset_source();
 CHECK(family_static_hud_current());
 if(strcmp(argv[1],"valid")){
  CHECK(!fdh_captured);SDL_FillRect(output,NULL,0);family_static_hud_compose();verify_border_and_scene(0);goto done;
 }
 CHECK(fdh_captured&&fdh_words&&fdh_meters&&fdh_text&&fdh_indicators);
 verify_dynamic();CHECK(fdh_meter_bits==HUD_METERS_ALL&&!fdh_mode&&!fdh_shield);
 for(unsigned n=0;n<=11;n++){meter(HUD_WRITE_FRONT,n);meter(HUD_WRITE_REAR,11-n);
  CHECK(fdh_prepare());CHECK((fdh_meter_bits&12)==12);}
 verify_dynamic();
 /* A changed field is retired independently, and restored plausible pixels do
  * not recreate its writer history. Only a fresh real notification can renew. */
 ((Uint8 *)VGAScreenSeg->pixels)[17*320+289]^=1;CHECK(fdh_prepare());CHECK(!(fdh_meter_bits&4)&&(fdh_meter_bits&8));
 ((Uint8 *)VGAScreenSeg->pixels)[17*320+289]^=1;CHECK(fdh_prepare());CHECK(!(fdh_meter_bits&4));
 meter(HUD_WRITE_FRONT,11);CHECK(fdh_prepare());CHECK(fdh_meter_bits&4);
 fdh_meter_begin(VGAScreenSeg,output,HUD_WRITE_FRONT,11,0);CHECK(fdh_prepare());CHECK(!(fdh_meter_bits&4));
 /* Exact original paired mode blits. */
 Uint8 mode[2][80],opaque[2][80];
 for(unsigned i=0;i<2;i++)CHECK(hud_sprite_decode(OPTION_SHAPES,18+i,10,8,mode[i],opaque[i]));
 for(unsigned n=1;n<=2;n++){
  for(int y=0;y<8;y++){
   memcpy((Uint8 *)VGAScreenSeg->pixels+(44+y)*320+285,mode[n-1]+y*10,10);
   memcpy((Uint8 *)VGAScreenSeg->pixels+(44+y)*320+302,mode[2-n]+y*10,10);
  }
  fdh_mode_drawn(VGAScreenSeg,n);CHECK(fdh_prepare());CHECK(fdh_mode);
 }
 for(unsigned n=0;n<=28;n++){
  fdh_shield_wiped(VGAScreenSeg);
  for(int y=137;y<195;y++){int z=(194-y)/2;Uint8 v=z>(int)n?0:146+(z>1?(z-1)/2:0);
   for(int x=270;x<279;x++)((Uint8 *)VGAScreenSeg->pixels)[y*320+x]=v;
  }
  fdh_shield_drawn(VGAScreenSeg,n,n);CHECK(fdh_prepare());CHECK(fdh_shield);
 }
 /* Generator endpoints preserve actual prior rows; armor wipe/draw retains
  * native zero baseline and original two-row gradient. */
 for(unsigned step=0;step<2;step++){
  unsigned a=step?90:0,b=step?0:90;
  fdh_meter_begin(VGAScreenSeg,VGAScreenSeg,HUD_WRITE_GENERATOR,a,b);
  for(int y=12;y<104;y++)for(int x=269;x<277;x++)((Uint8 *)VGAScreenSeg->pixels)[y*320+x]=b?125:0;
  fdh_meter_end(VGAScreenSeg,HUD_WRITE_GENERATOR);CHECK(fdh_prepare());CHECK(fdh_meter_bits&HUD_METER_GENERATOR);
 }
 for(unsigned n=0;n<=28;n++){
  fdh_meter_begin(VGAScreenSeg,VGAScreenSeg,HUD_WRITE_ARMOR_WIPE,0,0);
  for(int y=137;y<195;y++)for(int x=307;x<316;x++)((Uint8 *)VGAScreenSeg->pixels)[y*320+x]=0;
  fdh_meter_end(VGAScreenSeg,HUD_WRITE_ARMOR_WIPE);
  fdh_meter_begin(VGAScreenSeg,VGAScreenSeg,HUD_WRITE_ARMOR_DRAW,n,0);
  for(int y=193-2*(int)n;y<195;y++){int z=(194-y)/2;
   for(int x=307;x<316;x++)((Uint8 *)VGAScreenSeg->pixels)[y*320+x]=226+(z>1?(z-1)/2:0);
  }
  fdh_meter_end(VGAScreenSeg,HUD_WRITE_ARMOR_DRAW);CHECK(fdh_prepare());CHECK(fdh_meter_bits&HUD_METER_ARMOR);
 }
 verify_dynamic();
 rgb_palette[255]^=1;CHECK(fdh_prepare());CHECK(!fdh_labels&&!fdh_meter_bits&&!fdh_top&&!fdh_groups[0]);rgb_palette[255]^=1;
 ((Uint8 *)VGAScreenSeg->pixels)[54*320+284]^=1;CHECK(fdh_prepare());CHECK(!fdh_groups[0]&&fdh_groups[1]);
 fdh_shield_drawn(output,1,1);fdh_mode_drawn(output,1);CHECK(fdh_prepare());CHECK(!fdh_shield&&!fdh_mode);
 family_static_hud_suspend();SDL_FillRect(output,NULL,0x12345678);family_static_hud_compose();
 CHECK(((Uint32 *)output->pixels)[0]==0x12345678);family_static_hud_begin();
 SDL_setenv("BUILDING313_FAMILY_DYNAMIC_HUD_ENABLE","0",1);CHECK(!fdh_prepare());CHECK(!fdh_captured);
 SDL_setenv("BUILDING313_FAMILY_DYNAMIC_HUD_ENABLE","1",1);CHECK(!fdh_prepare());
 reset_source();CHECK(fdh_prepare());scope=false;CHECK(!fdh_prepare());scope=true;CHECK(!fdh_prepare());
done:
 family_static_hud_reset();CHECK(!fdh_captured);
 hud_components_shutdown();hud_meters_shutdown();hud_indicators_shutdown();hud_fixed_text_shutdown();gameplay_hud_shutdown();
 SDL_FreeSurface(VGAScreenSeg);SDL_FreeSurface(output);
 for(unsigned t=0;t<8;t++)for(unsigned i=0;i<sprite_table[t].count;i++)free(sprite_table[t].sprite[i].data);
 SDL_Quit();printf("PASS family dynamic HUD %s: %u checks\n",argv[1],checks);return 0;
}
