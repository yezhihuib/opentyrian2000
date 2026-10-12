/* HUF1 helpers/writers are included unchanged except their original main. */
#include "huf_suite.inc"
static const int combined_boxes[4][4]={{289,17,311,20},{289,38,311,41},{269,12,277,104},{307,137,316,195}};
static void combined_start(const char *root,const char *variant,int d,bool font,bool meter)
{
 char path[1600];snprintf(path,sizeof(path),"%s/%s",root,variant);setup(d,path);
 /* setup retains the asset path until the next setup: use stable storage. */
 static char assets[1600];strcpy(assets,path);game_probe_assets=assets;
 read_fixture(assets,"source.bin",VGAScreenSeg->pixels,64000);memset(sprite_table,0,sizeof(sprite_table));
 char name[1700];snprintf(name,sizeof(name),"%s/map.bin",assets);FILE *f=fopen(name,"rb");assert(f);
 for(unsigned i=0;i<256;i++){Uint8 b[4];assert(fread(b,1,4,f)==4);font_ascii[i]=(int32_t)((Uint32)b[0]|(Uint32)b[1]<<8|(Uint32)b[2]<<16|(Uint32)b[3]<<24);}fclose(f);
 snprintf(name,sizeof(name),"%s/glyphs.bin",assets);f=fopen(name,"rb");assert(f);sprite_table[TINY_FONT].count=127;
 for(unsigned i=0;i<127;i++){Uint8 b[6];assert(fread(b,1,6,f)==6);unsigned w=b[0]|b[1]<<8,h=b[2]|b[3]<<8,n=b[4]|b[5]<<8;assert(n<=48&&fread(synthetic_glyphs[i],1,n,f)==n);sprite_table[TINY_FONT].sprite[i]=(Sprite){w,h,n,synthetic_glyphs[i]};}fclose(f);
 memset(message_erase_pixels,7,sizeof(message_erase_pixels));sprite_table[OPTION_SHAPES].count=37;sprite_table[OPTION_SHAPES].sprite[36]=(Sprite){228,9,sizeof(message_erase_pixels),message_erase_pixels};
 render_mirror_hud_start(VGAScreenSeg);assert(font_gameplay==font&&hud_meters_ready()==meter&&!hud_components_ready()&&!hud_gameplay);
 textErase=0;level("Tyrian",font);JE_drawTextWindow("Message gy");assert(textErase==100);
}
static void combined_meter(unsigned kind,unsigned a,unsigned b)
{
#ifndef COMBINED_BASELINE
 render_mirror_hud_meter_begin(VGAScreenSeg,VGAScreenSeg,kind,a,b);
#endif
 unsigned box=kind<2?kind:kind==2?2:3;
 for(int y=combined_boxes[box][1];y<combined_boxes[box][3];y++)for(int x=combined_boxes[box][0];x<combined_boxes[box][2];x++){
  Uint8 *p=(Uint8 *)VGAScreenSeg->pixels+y*320+x;
  if(kind<2)*p=x-289<2*(int)a?116+(x-289)/2:0;
  else if(kind==2){int lo=102-(int)(a>b?a:b),hi=103-(int)(a<b?a:b);if(y>=lo&&y<=hi)*p=b>a?113+b/7:0;}
  else if(kind==3){if(y<=194-2*(int)a)*p=0;}
  else if(y>=193-2*(int)a){int z=(194-y)/2;*p=226+(z<3?0:(z-1)/2);}
 }
#ifndef COMBINED_BASELINE
 render_mirror_hud_meter_end(VGAScreenSeg,kind);
#endif
}
static void combined_draw(bool font,bool meters)
{
 render_mirror_begin();if(meters){combined_meter(0,3,0);combined_meter(1,7,0);combined_meter(2,0,90);combined_meter(4,10,0);}
 draw_cash("0123",font);if(font)render_mirror_text_begin(game_screen,1,28,28,"Pilot gy",2,6);
 JE_textShade(game_screen,28,28,"Pilot gy",2,6,FULL_SHADE);if(font)render_mirror_text_end();finish_font();
}
static void combined_record(void)
{
 Snapshot s=snap();digest(s.bytes,s.size);free(s.bytes);digest(output->pixels,(size_t)output->pitch*output->h);
 if(have_fade_saved)digest(fade_saved->pixels,(size_t)fade_saved->pitch*fade_saved->h);
 digest(VGAScreenSeg->pixels,64000);digest(component_output_owner,sizeof(component_output_owner));digest(component_saved_owner,sizeof(component_saved_owner));
 digest(&textErase,sizeof(textErase));digest(&last_output_valid,sizeof(last_output_valid));digest(&have_fade_saved,sizeof(have_fade_saved));digest(&fade_mode,sizeof(fade_mode));
 if(font_history){digest(font_powner,FONT_PERSIST_CELLS);digest(font_psaved_owner,FONT_PERSIST_CELLS);
  for(unsigned r=0;r<2;r++)for(unsigned i=0;i<font_scenes[r].used;i++){unsigned k=font_scenes[r].offset+i;digest(font_owner+k,1);digest(font_saved_owner+k,1);if(font_owner[k]){digest(font_under+k,4);digest(font_lower_owner+k,1);}if(font_saved_owner[k]){digest(font_saved_under+k,4);digest(font_saved_lower_owner+k,1);}}
 }
 uint64_t rng=mt_state_fingerprint();digest(&rng,sizeof(rng));
}
static void combined_parity(const char *root)
{
 for(int d=4;d<=8;d+=4){
  combined_start(root,"no-meter",d,true,false);combined_draw(true,true);assert(font_owned()&&!components_owned());combined_record();
  for(unsigned op=0;op<3;op++){
   if(op==0)JE_drawTextWindow("Short");else if(op==1){erase_message(false);textErase=0;}else JE_drawTextWindow("Fresh gy");
   combined_draw(true,false);combined_record();
  }
  render_mirror_hud_suspend();combined_draw(true,false);combined_record();render_mirror_release_texture();combined_draw(true,false);combined_record();
  for(unsigned shade=0;shade<=255;shade+=255){fade_sequence(shade,3);combined_record();if(shade==255)break;}
 }
 printf("COMBINED_NO_HUM2 %016llx\n",(unsigned long long)aggregate);
}
#ifndef COMBINED_BASELINE
static void combined_removal(const char *root,int d,unsigned shade,unsigned phase,bool remove_font)
{
 combined_start(root,remove_font?"no-font":"no-meter",d,!remove_font,remove_font);combined_draw(!remove_font,true);fade_sequence(shade,phase);
 size_t bytes=(size_t)output->pitch*output->h;Uint8 *out=malloc(bytes),*saved=malloc(bytes);assert(out&&saved);memcpy(out,output->pixels,bytes);memcpy(saved,fade_saved->pixels,bytes);Uint8 indices[64000];memcpy(indices,VGAScreenSeg->pixels,64000);
 combined_start(root,"both",d,true,true);combined_draw(true,true);assert(font_owned()&&components_owned());fade_sequence(shade,phase);
 uint64_t fg=font_generation,cg=component_generation;
 if(remove_font){font_clear_cached(15);assert(!font_owned()&&components_owned()&&component_output_generation==cg&&component_saved_generation==cg);}
 else {components_clear_cached(60);assert(!components_owned()&&font_owned()&&font_output_generation==fg&&font_saved_generation==fg);}
 assert(last_output_valid&&have_fade_saved&&!memcmp(indices,VGAScreenSeg->pixels,64000));
 assert(!memcmp(out,output->pixels,bytes)&&!memcmp(saved,fade_saved->pixels,bytes));free(out);free(saved);
 if(remove_font)components_clear_cached(60);else font_clear_cached(15);
 assert(!font_owned()&&!components_owned()&&!last_output_valid&&!have_fade_saved&&!fade_mode);
}
static void combined_lifetime(const char *root,int d)
{
 combined_start(root,"both",d,true,true);combined_draw(true,true);
 JE_drawTextWindow("Short");combined_draw(true,false);assert(textErase==100&&font_persistent[1].valid&&components_owned()&&font_owned());
 erase_message(false);textErase=0;combined_draw(true,false);assert(!font_persistent[1].valid&&components_owned()&&font_owned());
 JE_drawTextWindow("Again gy");combined_draw(true,false);assert(textErase==100&&font_persistent[1].valid&&components_owned()&&font_owned());
 for(unsigned modal=0;modal<2;modal++){if(modal)render_mirror_release_texture();else render_mirror_hud_suspend();assert(!components_owned()&&!font_owned()&&hud_meters_ready()&&font_gameplay);combined_draw(true,false);assert(components_owned()&&font_owned());}
 ((Uint8 *)VGAScreenSeg->pixels)[100*320+270]^=1;combined_draw(true,false);assert(!(component_output_owner[100*320+270]&16)&&font_owned());
 combined_meter(2,0,90);combined_draw(true,false);assert(component_output_owner[100*320+270]==16&&font_owned());
 for(unsigned family=0;family<2;family++){
  combined_start(root,"both",d,true,true);combined_draw(true,true);SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);
  if(family)component_saved_generation=0;else font_saved_generation=0;
  assert(!render_mirror_present(NULL,VGAScreenSeg,NULL)&&!ready&&!last_output_valid);
  assert(hud_meters_ready()&&font_gameplay);combined_draw(true,false);assert(components_owned()&&font_owned()&&last_output_valid);
 }
}
#endif
int main(int argc,char **argv)
{
 assert(argc==3);materials();if(!strcmp(argv[2],"parity"))combined_parity(argv[1]);
#ifndef COMBINED_BASELINE
 else {for(int d=4;d<=8;d+=4){combined_lifetime(argv[1],d);for(unsigned shade=0;shade<=255;shade+=255){for(unsigned phase=0;phase<4;phase++)for(unsigned remove=0;remove<2;remove++)combined_removal(argv[1],d,shade,phase,remove);if(shade==255)break;}}puts("PASS combined HUF1/HUM2: 32 whole-output/saved fade-removal counterfactuals, independent last-owner/lifetime/mismatch/lease recovery at4+8.");}
#endif
 cleanup();return 0;
}
