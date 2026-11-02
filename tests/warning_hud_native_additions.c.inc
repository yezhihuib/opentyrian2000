/* Finite WARNING oracle. Actual JE_outText + unsafe blit above perform writes.
 * Expected RGBA uses direct HUF bytes + independently decoded original RLE,
 * never font_commands, hud_font_alpha, font_blend or production decoder. */
static unsigned warning_cases;
static Uint8 warning_atlas[163840],warning_native[204],warning_alpha[204*64];
static Uint32 warning_expected[204*64],warning_ring[38*7*64];
static void warning_copy_world(void)
{for(unsigned y=0;y<184;y++)memcpy((Uint8*)VGAScreenSeg->pixels+y*320,(Uint8*)game_screen->pixels+y*320+24,264);}
static Uint32 warning_mix(Uint32 bg,Uint32 fg,unsigned a)
{Uint32 out=0xff000000u;for(unsigned sh=0;sh<24;sh+=8){unsigned b=(bg>>sh)&255,f=(fg>>sh)&255;out|=((f*a+b*(255-a)+127)/255)<<sh;}return out;}
static void warning_decode(unsigned id,Uint8 values[48],Uint8 mask[48])
{
 Sprite *s=&sprite_table[TINY_FONT].sprite[id];CHECK(s->width<=6&&s->height<=8&&s->width&&s->height);memset(values,0,48);memset(mask,0,48);
 unsigned pos=0,col=0;for(unsigned j=0;j<s->size;j++){unsigned v=s->data[j];if(v==255){CHECK(++j<s->size);unsigned n=s->data[j];pos+=n;col+=n;}else if(v==254){pos+=s->width-col;col=s->width;}else if(v==253){++pos;++col;}else{CHECK(pos<s->width*s->height);values[pos]=(Uint8)v;mask[pos]=1;++pos;++col;}if(col>=s->width)col=0;CHECK(pos<=s->width*s->height);}
}
static void warning_read_atlas(const char *root)
{char path[2048];int n=snprintf(path,sizeof(path),"%s/gameplay-hud-font-v1.hda",root);CHECK(n>0&&(size_t)n<sizeof(path));FILE*f=fopen(path,"rb");CHECK(f);Uint8 h[112];CHECK(fread(h,1,112,f)==112&&!memcmp(h,"HUF1",4));CHECK(fread(warning_atlas,1,sizeof(warning_atlas),f)==sizeof(warning_atlas)&&fgetc(f)==EOF);CHECK(fclose(f)==0);}
static void warning_snapshot_ring(void)
{unsigned d=game_probe_density;for(unsigned y=0;y<7*d;y++)for(unsigned x=0;x<38*d;x++)warning_ring[y*38*d+x]=*pixel(output,(138-24)*d+x,178*d+y);}
static void warning_check_ring(void)
{unsigned d=game_probe_density;for(unsigned y=0;y<7*d;y++)for(unsigned x=0;x<38*d;x++)if(x<2*d||x>=36*d||y>=6*d)CHECK(*pixel(output,(138-24)*d+x,178*d+y)==warning_ring[y*38*d+x]);}
static void warning_setup(const char*root,unsigned d)
{++warning_cases;setup(root,(int)d);grant();all_ready();warning_copy_world();frame(MIRROR_OUTPUT_ORDINARY);CHECK(ready&&last_output_valid);warning_snapshot_ring();render_mirror_begin();CHECK(shared_hud_frame&&font_gameplay&&!active);}
static void warning_expected_begin(unsigned value)
{
 unsigned d=game_probe_density;memset(warning_alpha,0,sizeof(warning_alpha));
 for(unsigned y=0;y<6;y++)for(unsigned x=0;x<34;x++){warning_native[y*34+x]=*((Uint8*)game_screen->pixels+(178+y)*320+140+x);for(unsigned sy=0;sy<d;sy++)for(unsigned sx=0;sx<d;sx++)warning_expected[(y*d+sy)*34*d+x*d+sx]=*pixel(canvas,(140+x)*d+sx,(178+y)*d+sy);}
 const char word[]="WARNING";unsigned advance=0,opaque=0;for(unsigned letter=0;letter<7;letter++){
  unsigned id=(unsigned)font_ascii[(unsigned char)word[letter]];CHECK(id<86);Sprite*s=&sprite_table[TINY_FONT].sprite[id];Uint8 v[48],mask[48];warning_decode(id,v,mask);unsigned color=0;bool found=false;
  for(unsigned y=0;y<s->height;y++)for(unsigned x=0;x<s->width;x++)if(mask[y*s->width+x]){unsigned low=v[y*s->width+x]&15;CHECK(low+value<16);if(low>color)color=low;found=true;CHECK(advance+x<34&&y<6);warning_native[y*34+advance+x]=(Uint8)((7u<<4)|(low+value));++opaque;}
  CHECK(found&&color==7);color=(7u<<4)|(color+value);Uint32 rgb=0xff000000u|(rgb_palette[color]&0xffffffu);
  for(unsigned y=0;y<s->height*d;y++)for(unsigned x=0;x<s->width*d;x++){unsigned ax=(id%16)*32+4+x/(d/4),ay=(id/16)*40+4+y/(d/4),a=warning_atlas[ay*512+ax];CHECK(advance*d+x<34*d&&y<6*d);unsigned pos=y*34*d+advance*d+x;warning_alpha[pos]=(Uint8)a;warning_expected[pos]=warning_mix(warning_expected[pos],rgb,a);}
  advance+=s->width+1;
 }
 CHECK(advance==35&&opaque>0);
}
static void warning_draw(unsigned value)
{
 render_mirror_text_warning_begin(game_screen,(int)value);CHECK(font_context==2&&font_command_count==7&&font_scenes[2].rect.x==140&&font_scenes[2].rect.y==178&&font_scenes[2].rect.w==34&&font_scenes[2].rect.h==6);
 for(unsigned i=0;i<7;i++)CHECK(!font_commands[i].black&&font_commands[i].hue==7&&font_commands[i].value==(int)value);
 warning_expected_begin(value);JE_outText(game_screen,140,178,"WARNING",7,(int)value);CHECK(font_command_next==7&&!font_glyph_active);render_mirror_text_end();CHECK(font_context==-1&&font_scenes[2].canvas_live);
 unsigned d=game_probe_density;for(unsigned y=0;y<6;y++)for(unsigned x=0;x<34;x++)CHECK(*((Uint8*)game_screen->pixels+(178+y)*320+140+x)==warning_native[y*34+x]);
 for(unsigned y=0;y<6*d;y++)for(unsigned x=0;x<34*d;x++)CHECK(*pixel(canvas,140*d+x,178*d+y)==warning_expected[y*34*d+x]);warning_copy_world();
}
static void warning_finish(void)
{render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready&&last_output_valid&&font_scenes[2].output_live&&font_output_generation);unsigned d=game_probe_density;for(unsigned y=0;y<6*d;y++)for(unsigned x=0;x<34*d;x++)CHECK(*pixel(output,116*d+x,178*d+y)==warning_expected[y*34*d+x]);warning_check_ring();}
static void warning_no_live(void)
{CHECK(!font_scenes[2].canvas_live&&!font_scenes[2].output_live&&!font_scene_owned(font_scenes+2,font_owner));}
static void warning_native_rectangle(void)
{unsigned d=game_probe_density;for(unsigned y=0;y<6;y++)for(unsigned x=0;x<34;x++){Uint8 index=*((Uint8*)VGAScreenSeg->pixels+(178+y)*320+116+x);for(unsigned sy=0;sy<d;sy++)for(unsigned sx=0;sx<d;sx++)CHECK(*pixel(output,(116+x)*d+sx,(178+y)*d+sy)==(0xff000000u|(rgb_palette[index]&0xffffffu)));}}
static void warning_valid16(const char*root)
{for(unsigned d=4;d<=8;d+=4)for(unsigned v=0;v<8;v++){warning_setup(root,d);warning_draw(v);warning_finish();}}
static void warning_lifecycle2(const char*root)
{for(unsigned d=4;d<=8;d+=4){warning_setup(root,d);warning_draw(0);warning_draw(7);warning_finish();memset(game_screen->pixels,7,64000);warning_copy_world();render_mirror_begin();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);warning_no_live();warning_native_rectangle();render_mirror_begin();warning_draw(3);warning_finish();}}
static void warning_writes8(const char*root)
{
 for(unsigned d=4;d<=8;d+=4)for(unsigned fade=0;fade<2;fade++)for(unsigned rect=0;rect<2;rect++){
  warning_setup(root,d);warning_draw(4);warning_finish();CHECK(!font_scenes[0].output_live&&!font_scenes[1].output_live&&!memchr(font_powner,1,FONT_PERSIST_CELLS));
  if(fade){SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(have_fade_saved&&fade_mode==1);for(unsigned i=0;i<256;i++)rgb_palette[i]=channel_step(rgb_palette[i],0,7)&0xffffffu;render_mirror_fade_step(7);CHECK(ready&&last_output_valid&&have_fade_saved);}
  unsigned cell=0;while(cell<204&&warning_native[cell]==7)++cell;CHECK(cell<204);unsigned x=116+cell%34,y=178+cell/34;Uint8 *p=(Uint8*)VGAScreenSeg->pixels+y*320+x,value=*p;
  if(rect){SDL_Rect r={116,178,34,6};render_mirror_rect(VGAScreenSeg,&r);}else render_mirror_pixel(VGAScreenSeg,p,value,MIRROR_NORMAL);
  CHECK(*p==value);warning_no_live();CHECK(font_shared_rejected&4u);CHECK(hud_output_generation&&last_output_valid);warning_native_rectangle();
  if(fade){CHECK(have_fade_saved);for(unsigned sy=0;sy<d;sy++)for(unsigned sx=0;sx<d;sx++)CHECK(*pixel(fade_saved,x*d+sx,y*d+sy)==(0xff000000u|(normal_palette[value]&0xffffffu)));}
  memcpy(rgb_palette,normal_palette,sizeof(rgb_palette));memset(game_screen->pixels,7,64000);warning_copy_world();render_mirror_begin();warning_draw(4);warning_finish();
 }
}
static void warning_failures12(const char*root)
{
 for(unsigned mode=0;mode<12;mode++){
  warning_setup(root,8);warning_draw(3);if(mode==1||mode==3)warning_finish();
  if(mode<=1){rgb_palette[119]^=1;if(mode==0){render_mirror_text_warning_begin(game_screen,3);warning_no_live();}else{CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));warning_no_live();}memcpy(rgb_palette,normal_palette,sizeof(rgb_palette));}
  else if(mode<=3){Uint8 *p=sprite_table[TINY_FONT].sprite[font_ascii['W']].data;*p^=1;if(mode==2){render_mirror_text_warning_begin(game_screen,3);warning_no_live();}else{(void)render_mirror_present(NULL,VGAScreenSeg,NULL);warning_no_live();}*p^=1;}
  else if(mode==4){void *saved=game_screen->pixels;Uint8 replacement[64000];memcpy(replacement,saved,64000);game_screen->pixels=replacement;render_mirror_text_warning_begin(game_screen,3);warning_no_live();game_screen->pixels=saved;}
  else if(mode==5){game_probe_density=3;render_mirror_begin();CHECK(!font_gameplay);game_probe_density=8;}
  else if(mode==6){render_mirror_text_warning_begin(VGAScreenSeg,3);warning_no_live();}
  else if(mode==7||mode==8){render_mirror_text_warning_begin(game_screen,mode==7?-1:8);warning_no_live();}
  else if(mode==9){render_mirror_text_warning_begin(game_screen,3);render_mirror_text_glyph_begin(game_screen,140,178,TINY_FONT,(unsigned)font_ascii['W'],false,7,3);CHECK(font_glyph_active);render_mirror_text_end();warning_no_live();}
  else if(mode==10){render_mirror_text_warning_begin(game_screen,3);render_mirror_text_glyph_begin(game_screen,140,178,TINY_FONT,(unsigned)font_ascii['A'],false,7,3);warning_no_live();render_mirror_text_end();}
  else {render_mirror_text_warning_begin(game_screen,3);JE_outText(game_screen,140,178,"WARNIN",7,3);CHECK(font_command_next==6);render_mirror_text_end();warning_no_live();}
 }
}
static void warning_isolation2(const char*root)
{
 for(unsigned d=4;d<=8;d+=4){warning_setup(root,d);draw_scene_text(0);draw_scene_text(1);
  render_mirror_text_level_begin(VGAScreenSeg,"TEST");CHECK(font_persistent[0].inflight);JE_outText(VGAScreenSeg,268,118,"TEST",12,4);render_mirror_text_level_end();
  render_mirror_text_message_begin("TEST",false);CHECK(font_persistent[1].inflight);render_mirror_text_message_backdrop();JE_outText(VGAScreenSeg,20,190,"TEST",0,4);render_mirror_text_message_end();
  warning_draw(2);warning_finish();CHECK(font_scenes[0].output_live&&font_scenes[1].output_live&&memchr(font_powner,1,416)&&memchr(font_powner+416,1,1792));
  uint64_t scene0=gameplay_hud_fnv64(font_owner+font_scenes[0].offset,font_scenes[0].used),scene1=gameplay_hud_fnv64(font_owner+font_scenes[1].offset,font_scenes[1].used),persistent=gameplay_hud_fnv64(font_powner,FONT_PERSIST_CELLS);
  font_clear_cached(16);warning_no_live();CHECK(font_scenes[0].output_live&&font_scenes[1].output_live&&font_persistent[0].valid&&font_persistent[1].valid);CHECK(scene0==gameplay_hud_fnv64(font_owner+font_scenes[0].offset,font_scenes[0].used)&&scene1==gameplay_hud_fnv64(font_owner+font_scenes[1].offset,font_scenes[1].used)&&persistent==gameplay_hud_fnv64(font_powner,FONT_PERSIST_CELLS));
 }
}
static void warning_reset2(const char*root)
{for(unsigned d=4;d<=8;d+=4){warning_setup(root,d);warning_draw(5);warning_finish();CHECK(!font_saved_generation&&!font_scenes[0].output_live&&!font_scenes[1].output_live&&!memchr(font_powner,1,FONT_PERSIST_CELLS));font_output_generation=0;CHECK(font_cached()&&!font_cached_indices_match());CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));warning_no_live();memset(game_screen->pixels,7,64000);warning_copy_world();render_mirror_begin();warning_draw(5);warning_finish();render_mirror_hud_suspend();warning_no_live();CHECK(font_suspended);render_mirror_hud_reset();CHECK(!font_gameplay&&!ready&&!last_output_valid);warning_no_live();}}
static void warning_missing2(const char*root,const char*fixtures)
{(void)root;for(unsigned mode=0;mode<2;mode++){++warning_cases;char path[2048];int n=snprintf(path,sizeof(path),"%s/%s",fixtures,mode?"corrupt":"missing");CHECK(n>0&&(size_t)n<sizeof(path));setup(path,4);grant();CHECK(!hud_font_ready());CHECK(gameplay_hud_ready()&&hud_components_ready()&&hud_meters_ready()&&hud_indicators_ready()&&hud_fixed_text_ready());render_mirror_begin();render_mirror_text_warning_begin(game_screen,3);CHECK(font_context==-1&&!font_gameplay);JE_outText(game_screen,140,178,"WARNING",7,3);render_mirror_text_end();warning_copy_world();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready&&last_output_valid);warning_native_rectangle();}}
int main(int argc,char**argv)
{CHECK(argc==3);load_original();warning_read_atlas(argv[1]);warning_valid16(argv[1]);warning_lifecycle2(argv[1]);warning_writes8(argv[1]);warning_failures12(argv[1]);warning_isolation2(argv[1]);warning_reset2(argv[1]);warning_missing2(argv[1],argv[2]);CHECK(warning_cases==44);cleanup();for(unsigned t=0;t<8;t++)for(unsigned i=0;i<sprite_table[t].count;i++)free(sprite_table[t].sprite[i].data);printf("PASS WARNING HUF extracted native: 44 setups %u checks; SDL stub; NOT gameplay/window/other-owner qualification\n",checks);return 0;}
