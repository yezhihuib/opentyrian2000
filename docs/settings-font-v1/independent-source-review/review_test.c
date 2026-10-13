#define main upstream_test_main
#include "/tmp/settings-font-independent-504b3d4/review_harness_base.c"
#undef main
#include "/workspace/scratch/f67dd347fa0a/settings-font-implementation-20261013/src/mouse.h"
#include "/workspace/scratch/f67dd347fa0a/settings-font-implementation-20261013/src/keyboard.h"
JE_boolean mousedown;
Uint8 lastmouse_but;
Sint32 mouse_x,mouse_y;
void service_SDL_events(JE_boolean clear_new){(void)clear_new;}
static unsigned dense_frames,output_frames,cursor_cases,inline_cases,volume_cases,production_fade_steps;
void startup_logos_fade_start(const SDL_Color *a,const SDL_Color *b,unsigned c,unsigned d){(void)a;(void)b;(void)c;(void)d;}
void startup_logos_fade_step(int a,unsigned b,unsigned c){(void)a;(void)b;(void)c;}
void title_layers_fade_start(const SDL_Color *a,const SDL_Color *b,unsigned c,unsigned d){(void)a;(void)b;(void)c;(void)d;}
void title_layers_fade_step(int a,unsigned b,unsigned c){(void)a;(void)b;(void)c;}
void render_mirror_fade_start(const SDL_Color *a,const SDL_Color *b,unsigned c,unsigned d){(void)a;(void)b;(void)c;(void)d;}
void render_mirror_fade_step(int a){(void)a;}
extern unsigned sf_test_fault,sf_test_live_textures,sf_test_sdl_cases;
static void sdl_failures(void){
 settings_font_invalidate();scaler=1;SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,640,400,32,SDL_PIXELFORMAT_ARGB8888);SDL_Renderer *r=SDL_CreateSoftwareRenderer(target);REQUIRE(target&&r);SDL_Rect dst={0,0,640,400};
 for(unsigned fault=1;fault<=7;fault++){
  frame(1,0,0,2,0,0);sf_test_fault=fault;REQUIRE(!settings_font_present(r,VGAScreen,&dst,false));REQUIRE(!sf.frame&&!sf.texture&&!sf_test_live_textures);sf_test_fault=0;
  frame(1,0,0,2,0,0);REQUIRE(settings_font_present(r,VGAScreen,&dst,false));REQUIRE(sf_test_live_textures==1);settings_font_invalidate();REQUIRE(!sf_test_live_textures);sf_test_sdl_cases++;
 }
 SDL_DestroyRenderer(r);SDL_FreeSurface(target);
}
static void inline_values(void){
 for(unsigned kind=0;kind<3;kind++)for(unsigned item=0;item<(kind==0?12u:kind==1?9u:4u);item++){
  memcpy(VGAScreen->pixels,VGAScreen2->pixels,SF_N);settings_font_frame_begin(2,kind,0);text_run(SETTINGS_HEADING,0,160,4,"Graphics",0,centered,-3);
  for(unsigned row=0;row<4;row++){int y=37+21*row,v=row==kind?-1:-3;text_run(SETTINGS_LABEL,row,45,y,labels[1][row],1,left_aligned,v);if(row<3){char buf[20];text_run(SETTINGS_VALUE,row,180,y,value(row+1,row==kind?item:0,buf),1,left_aligned,v);}}
  text_run(SETTINGS_FOOTER,kind,45,190,footers[1][kind],2,left_aligned,4);settings_font_frame_end();REQUIRE(sf.frame);render();REQUIRE(!memcmp(sf.replay,sf.expected,SF_N));inline_cases++;
 }
 for(unsigned amount=1;amount<32;amount++)for(unsigned mute=0;mute<2;mute++){
  memcpy(VGAScreen->pixels,VGAScreen2->pixels,SF_N);settings_font_frame_begin(3,0,0);text_run(SETTINGS_HEADING,0,160,4,"Sound",0,centered,-3);
  for(unsigned row=0;row<3;row++){text_run(SETTINGS_LABEL,row,45,37+21*row,labels[2][row],1,left_aligned,row?-3:-1);if(row<2)bar(row,mute?170:174,amount);}
  text_run(SETTINGS_FOOTER,0,45,190,footers[2][0],2,left_aligned,4);settings_font_frame_end();REQUIRE(sf.frame);render();REQUIRE(!memcmp(sf.replay,sf.expected,SF_N));volume_cases++;
 }
}
static Uint32 *independent;
static void independent_frame(void){
 render();
 for(unsigned i=0;i<256;i++){Uint8 r,g,b;SDL_GetRGB(rgb_palette[i],main_window_tex_format,&r,&g,&b);Uint32 expected=UINT32_C(0xff000000)|((Uint32)r<<16)|((Uint32)g<<8)|b;REQUIRE(sf.palette[i]==expected);}
 for(unsigned y=0;y<800;y++)for(unsigned x=0;x<1280;x++){
  unsigned p=(y/4)*320+x/4;
  Uint32 wanted=sf.owner[p]?oracle_sample(x,y):sf.palette[sf.expected[p]];
  if(sf.output[y*1280+x]!=wanted){fprintf(stderr,"DENSE x=%u y=%u got=%08x wanted=%08x\n",x,y,sf.output[y*1280+x],wanted);abort();}
  independent[y*1280+x]=wanted;
 }
 dense_frames++;
}
static Uint32 independent2(unsigned x,unsigned y){
 unsigned p=2*y*1280+2*x;Uint32 out=0xff000000;
 for(unsigned sh=0;sh<=16;sh+=8){unsigned sum=((independent[p]>>sh)&255)+((independent[p+1]>>sh)&255)+((independent[p+1280]>>sh)&255)+((independent[p+1281]>>sh)&255);out|=((sum+2)/4)<<sh;}return out;
}
static void output_test(unsigned scale){
 settings_font_invalidate();scaler=scale==2?1:7;
 frame(2,0,1,12,11,0);independent_frame();
 SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,320*scale,200*scale,32,SDL_PIXELFORMAT_ARGB8888);
 SDL_Renderer *r=SDL_CreateSoftwareRenderer(target);REQUIRE(target&&r);SDL_Rect dst={0,0,320*scale,200*scale};
 REQUIRE(settings_font_present(r,VGAScreen,&dst,false));
 for(unsigned y=0;y<200*scale;y++)for(unsigned x=0;x<320*scale;x++){
  Uint32 got=*(Uint32 *)((Uint8*)target->pixels+y*target->pitch+x*4),wanted=scale==2?independent2(x,y):independent[y*1280+x];
  if(got!=wanted){fprintf(stderr,"OUTPUT scale=%u x=%u y=%u got=%08x wanted=%08x\n",scale,x,y,got,wanted);abort();}
 }
 output_frames++;settings_font_invalidate();SDL_DestroyRenderer(r);SDL_FreeSurface(target);
}
static void production_fades(const char *dir){
 SDL_Color black={0,0,0,255};set_colors(black,0,255);acquire(dir);frame(1,0,0,2,0,0);int diff[256][3];init_step_fade_palette(diff,palettes[7],0,255);
 for(int step=10;step;step--){step_fade_palette(diff,step,0,255);REQUIRE(sf.active&&sf.frame);independent_frame();production_fade_steps++;}
 REQUIRE(sf.initial_done);init_step_fade_solid(diff,black,0,255);
 for(int step=10;step;step--){step_fade_palette(diff,step,0,255);REQUIRE(sf.active&&sf.frame);independent_frame();production_fade_steps++;}
 REQUIRE(sf.exiting);
}
int main(int argc,char **argv){
 REQUIRE(argc==3);main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);REQUIRE(VGAScreen&&VGAScreen2&&main_window_tex_format);fixtures(argv[1]);palette_count=24;acquire(argv[2]);
 independent=malloc(SF_OUT_BYTES);REQUIRE(independent);memcpy(sf.expected_palette,palettes[7],sizeof(colors));live_palette(palettes[7]);sf.initial_done=true;
 for(unsigned menu=1;menu<=3;menu++)for(unsigned sel=0;sel<(menu==3?3u:4u);sel++){frame(menu,sel,0,12,0,sel%2?32:0);independent_frame();}
 frame(2,0,1,12,11,0);independent_frame();frame(2,1,2,9,3,0);independent_frame();frame(2,2,3,4,3,0);independent_frame();
 const int coords[][2]={{0,0},{45,37},{180,190},{319,199},{-5,-7},{309,184},{319,0},{0,199}};
 for(unsigned mode=0;mode<3;mode++)for(unsigned i=0;i<sizeof(coords)/sizeof(coords[0]);i++){
  frame(3,0,0,2,0,32);has_mouse=mode!=2;mouseInactive=mode==1;mouseCursor=MOUSE_POINTER_NORMAL;mouse_x=coords[i][0];mouse_y=coords[i][1];
  settings_font_cursor_begin();JE_mouseStart();settings_font_cursor_done();REQUIRE(sf.frame&&sf.stage==S_CURSOR_DONE);independent_frame();JE_mouseReplace();settings_font_cursor_erased();REQUIRE(sf.frame&&sf.stage==S_READY);REQUIRE(!memcmp(VGAScreen->pixels,sf.pre_cursor,SF_N));independent_frame();cursor_cases++;
 }
 output_test(2);output_test(4);inline_values();sdl_failures();production_fades(argv[2]);
 settings_font_end();REQUIRE(allocated==0);for(unsigned b=0;b<3;b++)for(unsigned id=0;id<sprite_table[b].count;id++)free(sprite(b,id)->data);free(shopSpriteSheet.data);free(independent);SDL_FreeSurface(VGAScreen);SDL_FreeSurface(VGAScreen2);SDL_FreeFormat(main_window_tex_format);
 printf("INDEPENDENT PASS dense_frames=%u all_output_frames=%u real_cursor_cases=%u inline_values=%u volume_cases=%u SDL_failures=%u production_fade_steps=%u live_textures=%u checks=%u allocations_balanced=%zu\n",dense_frames,output_frames,cursor_cases,inline_cases,volume_cases,sf_test_sdl_cases,production_fade_steps,sf_test_live_textures,checks,allocated);return 0;
}
