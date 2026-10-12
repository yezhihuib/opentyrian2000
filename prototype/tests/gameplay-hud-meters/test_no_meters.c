/* Exact published56efa261 versus candidate, HUM2 absent, synthetic display only. */
#define main static_hud_legacy_main
#include "../gameplay-hud/test_renderer.c"
#undef main
static Uint8 no_meter_source[64000],no_meter_mode_data[160];
static void activate_all(const char *path,int d){
 setup(d,path);expanded_test=false;read_fixture(path,"indicator-source.indices",no_meter_source,64000);memcpy(VGAScreenSeg->pixels,no_meter_source,64000);read_fixture(path,"indicator-modes.indices",no_meter_mode_data,160);
 memset(sprite_table,0,sizeof(sprite_table));memset(font_ascii,255,sizeof(font_ascii));memset(options,0,sizeof(options));memset(shields,0,sizeof(shields));memset(player,0,sizeof(player));memset(levelName,0,sizeof(levelName));power=lastPower=0;
 sprite_table[OPTION_SHAPES].count=20;for(unsigned i=0;i<2;i++)sprite_table[OPTION_SHAPES].sprite[18+i]=(Sprite){10,8,80,no_meter_mode_data+i*80};
 render_mirror_hud_start(VGAScreenSeg);assert(hud_gameplay&&component_gameplay&&indicator_gameplay&&fixed_text_gameplay&&!hud_meters_ready());
 for(unsigned side=0;side<2;side++)for(unsigned y=0;y<8;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+(44+y)*320+285+17*side,no_meter_mode_data+80*side+10*y,10);render_mirror_hud_mode_drawn(VGAScreenSeg,1);
}
static void record(void){
 for(int y=0;y<output->h;y++)digest((Uint8 *)output->pixels+y*output->pitch,output->w*4);
 digest(VGAScreenSeg->pixels,64000);digest(game_screen->pixels,64000);digest(player,sizeof(player));digest(&power,sizeof(power));digest(&lastPower,sizeof(lastPower));
 digest(component_output_owner,sizeof(component_output_owner));digest(component_saved_owner,sizeof(component_saved_owner));digest(hud_output_owner,sizeof(hud_output_owner));digest(indicator_output_owner,sizeof(indicator_output_owner));digest(fixed_text_output_owner,sizeof(fixed_text_output_owner));
 digest(&last_output_valid,sizeof(last_output_valid));digest(&have_fade_saved,sizeof(have_fade_saved));digest(&fade_mode,sizeof(fade_mode));uint64_t rng=mt_state_fingerprint();digest(&rng,sizeof(rng));
 if(have_fade_saved)for(int y=0;y<fade_saved->h;y++)digest((Uint8 *)fade_saved->pixels+y*fade_saved->pitch,fade_saved->w*4);
}
int main(int argc,char **argv){assert(argc==2);for(int d=4;d<=8;d+=4){
 activate_all(argv[1],d);frame(true,true);record();
 for(unsigned q=0;q<4;q++){
  unsigned p[]={1,11,0,6},a[]={0,28,10,1};
  for(unsigned field=0;field<2;field++)for(int y=field?38:17;y<(field?41:20);y++)for(int x=289;x<311;x++)((Uint8 *)VGAScreenSeg->pixels)[320*y+x]=x<289+2*(int)p[q]?116+(x-289)/2:0;
  for(int y=137;y<195;y++)for(int x=307;x<316;x++){int z=(194-y)/2;((Uint8 *)VGAScreenSeg->pixels)[320*y+x]=z<=(int)a[q]?226+(z<3?0:(z-1)/2):0;}
  for(int y=12;y<104;y++)for(int x=269;x<277;x++)((Uint8 *)VGAScreenSeg->pixels)[320*y+x]=(unsigned)(y-12)<q*30?113+q:0;
  frame(true,true);record();render_mirror_hud_suspend();record();frame(true,true);record();
 }
 for(unsigned solid=0;solid<=255;solid+=255){
  Uint32 normal[256];memcpy(normal,rgb_palette,sizeof(normal));SDL_Color goal={solid,solid,solid,255};render_mirror_fade_start(NULL,&goal,0,255);
  for(int n=4;n;n--){palette_step(solid,n,NULL);render_mirror_fade_step(n);record();assert(render_mirror_present(NULL,VGAScreenSeg,NULL));}
  SDL_Color restore[256];for(unsigned i=0;i<256;i++)restore[i]=(SDL_Color){normal[i]>>16,normal[i]>>8,normal[i],255};render_mirror_fade_start(restore,NULL,0,255);for(int n=4;n;n--){palette_step(0,n,normal);render_mirror_fade_step(n);record();}
  if(solid==255)break;
 }
 render_mirror_release_texture();frame(true,true);record();frame(true,false);record();
 }cleanup();printf("NO_HUM2 %016llx\n",(unsigned long long)aggregate);return 0;}
