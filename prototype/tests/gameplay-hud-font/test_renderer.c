#define FONT_ALLOCATION_ORACLE
#define main static_hud_legacy_main
#include "../gameplay-hud/test_renderer.c"
#undef main
static Uint8 synthetic_glyphs[127][48],message_erase_pixels[228*9];
static void activate_font(const char *path,int d)
{
 setup(d,path);memset(sprite_table,0,sizeof(sprite_table));
 FILE *f;char file[1200];snprintf(file,sizeof(file),"%s/map.bin",path);f=fopen(file,"rb");assert(f);
 for(unsigned i=0;i<256;i++){Uint8 b[4];assert(fread(b,1,4,f)==4);font_ascii[i]=(int32_t)((Uint32)b[0]|(Uint32)b[1]<<8|(Uint32)b[2]<<16|(Uint32)b[3]<<24);}fclose(f);
 snprintf(file,sizeof(file),"%s/glyphs.bin",path);f=fopen(file,"rb");assert(f);sprite_table[TINY_FONT].count=127;
 for(unsigned i=0;i<127;i++){Uint8 b[6];assert(fread(b,1,6,f)==6);unsigned w=b[0]|b[1]<<8,h=b[2]|b[3]<<8,n=b[4]|b[5]<<8;assert(n<=48);assert(fread(synthetic_glyphs[i],1,n,f)==n);sprite_table[TINY_FONT].sprite[i]=(Sprite){w,h,n,synthetic_glyphs[i]};}fclose(f);
 memset(message_erase_pixels,7,sizeof(message_erase_pixels));sprite_table[OPTION_SHAPES].count=37;sprite_table[OPTION_SHAPES].sprite[36]=(Sprite){228,9,sizeof(message_erase_pixels),message_erase_pixels};
 Uint32 old=rgb_palette[0];rgb_palette[0]^=1;render_mirror_hud_start(VGAScreenSeg);rgb_palette[0]=old;
 assert(font_gameplay&&hud_font_ready()&&font_history&&!hud_gameplay&&!component_gameplay&&!indicator_gameplay&&!fixed_text_gameplay);
}
static void draw_cash(const char *text,bool authored)
{
 if(authored)render_mirror_text_begin(game_screen,0,30,175,text,2,4);
 JE_textShade(game_screen,30,175,text,2,4,FULL_SHADE);
 if(authored)render_mirror_text_end();
}
static void crop_indices(void)
{for(int y=0;y<184;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,(Uint8 *)game_screen->pixels+y*game_screen->pitch+24,264);}
static void finish_font(void){crop_indices();render_mirror_finish(true);}
static void basic(const char *path,int d)
{
 activate_font(path,d);render_mirror_begin();draw_cash("0123",true);assert(font_scene_owned(font_scenes,font_owner));finish_font();assert(font_output_generation&&last_output_valid);
 font_clear_cached(15);assert(!font_owned());assert(!last_output_scene_hd&&!last_output_valid);
}
static Uint8 material_pixels[60*18*16*4],head_pixels[12*14*16*4],explosion_bytes[512];
static Asset material={true,true,42,1,60,18,0,0,4,material_pixels};
static Asset head={true,true,8,214,12,14,0,0,4,head_pixels};
static void materials(void)
{
 for(unsigned i=0;i<sizeof(material_pixels);i+=4){material_pixels[i]=(i*3)%256;material_pixels[i+1]=(i*7+53)%256;material_pixels[i+2]=(i*11+173)%256;material_pixels[i+3]=i%20?137:255;}
 for(unsigned i=0;i<sizeof(head_pixels);i+=4){head_pixels[i]=(i*3)%256;head_pixels[i+1]=(i*7+53)%256;head_pixels[i+2]=(i*11+173)%256;head_pixels[i+3]=i%20?137:255;}
 explosionSpriteSheet=(Sprite2_array){explosion_bytes,sizeof(explosion_bytes)};
}
static void seed(unsigned provenance)
{
 material.bank=42;material.index=1;draw_asset_filtered(180,70,&material,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);suppress=false;
 if(provenance==1){draw_asset_filtered(23,166,&material,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);suppress=false;}
 if(provenance==2){material.bank=ASSET_SHAPESZ;material.index=41;draw_asset_filtered(23,166,&material,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);suppress=false;}
 if(provenance==3){draw_asset_filtered(29,168,&head,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);suppress=false;}
 material.bank=42;material.index=1;
}
typedef struct {Uint8 *bytes;size_t size;unsigned count;HdRegion r[64];SDL_Rect restore;const char *reason;} Snapshot;
static Snapshot snap(void)
{
 size_t n=(size_t)canvas->w*canvas->h;Snapshot s={0};s.size=n*13+64000*4;s.bytes=malloc(s.size);assert(s.bytes);Uint8 *p=s.bytes;
 #define TAKE(a,z) do{memcpy(p,a,z);p+=(z);}while(0)
 TAKE(canvas->pixels,n*4);TAKE(hd_owner,n);TAKE(cloud_owner,n);TAKE(green_first,n*2);
 for(size_t i=0;i<n;i++){Uint32 v=green_first[i]?green_under[i]:0;memcpy(p,&v,4);p+=4;}
 for(size_t i=0;i<n;i++)*p++=green_first[i]?green_under_owner[i]:0;
 TAKE(selected,64000);TAKE(expected,64000);TAKE(game_screen->pixels,64000);TAKE(restored_mask,64000);
 #undef TAKE
 assert((size_t)(p-s.bytes)==s.size);s.count=region_count;assert(s.count<64);memcpy(s.r,regions,s.count*sizeof(HdRegion));s.restore=last_restore;s.reason=reject_reason;return s;
}
static void same_snapshot(Snapshot *a,unsigned prov,unsigned op)
{
 Snapshot b=snap();if(a->size!=b.size||memcmp(a->bytes,b.bytes,b.size)){
 size_t k=0;while(k<b.size&&a->bytes[k]==b.bytes[k])k++;
 fprintf(stderr,"writer mismatch d%d provenance%u op%u byte%zu expected%u actual%u\n",game_probe_density,prov,op,k,a->bytes[k],b.bytes[k]);abort();}
 assert(a->count==b.count);for(unsigned i=0;i<a->count;i++){assert(!memcmp(&a->r[i].rect,&b.r[i].rect,sizeof(SDL_Rect)));assert(a->r[i].live==b.r[i].live);}
 assert((!a->reason&&!b.reason)||(a->reason&&b.reason&&!strcmp(a->reason,b.reason)));
 assert(!memcmp(&a->restore,&b.restore,sizeof(SDL_Rect)));free(b.bytes);
}
static void write_at(int x,int y,Uint8 value,int style)
{Uint8 *p=(Uint8 *)game_screen->pixels+y*game_screen->pitch+x;*p=value;render_mirror_pixel(game_screen,p,value,style);}
static void operation(unsigned op)
{
 Uint8 *p=(Uint8 *)game_screen->pixels+175*game_screen->pitch+30;
 switch(op){
 case 0:break;
 case 1:write_at(30,175,*p,MIRROR_NORMAL);break;
 case 2:{SDL_Rect r={30,175,3,2};for(int y=175;y<177;y++)memset((Uint8 *)game_screen->pixels+y*320+30,93,3);render_mirror_rect(game_screen,&r);break;}
 case 3:write_at(30,175,(*p&240)|((*p&15)/2),MIRROR_SHADOW);break;
 case 4:*p=(*p&240)|MIN(15,(*p&15)+2);render_mirror_brightness_pixel(game_screen,p,2);break;
 case 5:*p=0x70|(((*p&15)+7)/2);render_mirror_sprite2_blend_pixel(game_screen,p,0x77,explosionSpriteSheet,122,30,175);break;
 case 6:write_at(30,175,82,MIRROR_BLEND);break;
 case 7:draw_asset_filtered(30,175,&head,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);suppress=false;break;
 case 8:case 9:case 14:case 15:case 16:{Asset a=head;a.bank=ASSET_EXPLOSION;a.index=78;
 int x=30,y=175;if(op==9)y=182;if(op==14)y=160;if(op==15)x=50;if(op==16)x=17;
 draw_asset_filtered(x,y,&a,MIRROR_BLEND,NULL,0,NULL,NULL,NULL);suppress=false;break;}
 case 10:restore_classic_rect((SDL_Rect){30,175,1,1});break;
 case 11:regions[region_count++]=(HdRegion){{20,173,12,3},42,12,MIRROR_NORMAL,true};restore_classic_rect((SDL_Rect){20,174,1,1});break;
 case 12:{Uint8 *map[12]={0};assert(render_mirror_terrain_row(game_screen,0,160,map,MIRROR_NORMAL)==0);break;}
 case 13:*p=89;render_mirror_terrain_pixel(game_screen,p,*p,MIRROR_NORMAL,false);break;
 case 17:JE_outText(game_screen,30,174,"Cheaters",3,4);break;
 }
}
static unsigned writer_cases,fade_cases,persistent_cases,scalar_cases,trust_cases,halo_cases;
static void writer_cases_run(const char *path,int d)
{
 for(unsigned prov=0;prov<4;prov++)for(unsigned op=0;op<18;op++){
 activate_font(path,d);render_mirror_begin();last_restore=(SDL_Rect){0};seed(prov);draw_cash("0123",false);operation(op);Snapshot baseline=snap();
 activate_font(path,d);render_mirror_begin();last_restore=(SDL_Rect){0};seed(prov);unsigned before=region_count;draw_cash("0123",true);assert(font_scene_owned(font_scenes,font_owner));assert(before==region_count);operation(op);font_strip_scene(0);same_snapshot(&baseline,prov,op);free(baseline.bytes);writer_cases++;
 }
}
static void abort_cases(const char *path,int d)
{
 for(unsigned fail=0;fail<20;fail++){
 activate_font(path,d);render_mirror_begin();seed(3);font_plan(30,175,"0123",2,4,20,true,&last_restore);
 FontCommand commands[100];unsigned count=font_command_count;memcpy(commands,font_commands,sizeof(commands));
 for(unsigned i=0;i<count;i++){FontCommand c=commands[i];if(i==fail)c.x++;if(c.black)blit_sprite_dark(game_screen,c.x,c.y,TINY_FONT,c.id,true);else blit_sprite_hv_unsafe(game_screen,c.x,c.y,TINY_FONT,c.id,c.hue,c.value);}Snapshot baseline=snap();
 activate_font(path,d);render_mirror_begin();seed(3);render_mirror_text_begin(game_screen,0,30,175,"0123",2,4);
 for(unsigned i=0;i<count;i++){FontCommand c=commands[i];if(i==fail)c.x++;if(c.black)blit_sprite_dark(game_screen,c.x,c.y,TINY_FONT,c.id,true);else blit_sprite_hv_unsafe(game_screen,c.x,c.y,TINY_FONT,c.id,c.hue,c.value);}render_mirror_text_end();
 assert(!font_scene_owned(font_scenes,font_owner));same_snapshot(&baseline,3,100+fail);free(baseline.bytes);writer_cases++;
 }
 activate_font(path,d);render_mirror_begin();seed(1);blit_sprite_dark(game_screen,29,175,TINY_FONT,font_ascii['0'],true);Snapshot b=snap();
 activate_font(path,d);render_mirror_begin();seed(1);render_mirror_text_begin(game_screen,0,30,175,"0123",2,4);blit_sprite_dark(game_screen,29,175,TINY_FONT,font_ascii['0'],true);render_mirror_text_end();same_snapshot(&b,1,121);free(b.bytes);writer_cases++;
 /* Defensive missing text_end: abort MUST precede copying canvas to output. */
 for(unsigned written=0;written<2;written++){
 activate_font(path,d);render_mirror_begin();seed(1);if(written)blit_sprite_dark(game_screen,29,175,TINY_FONT,font_ascii['0'],true);finish_font();size_t n=(size_t)output->pitch*output->h;Uint8 *out=malloc(n);memcpy(out,output->pixels,n);
 activate_font(path,d);render_mirror_begin();seed(1);render_mirror_text_begin(game_screen,0,30,175,"0123",2,4);if(written)blit_sprite_dark(game_screen,29,175,TINY_FONT,font_ascii['0'],true);finish_font();assert(font_context<0&&!font_owned());assert(!memcmp(out,output->pixels,n));free(out);writer_cases++;
 }
}
static void fade_sequence(unsigned shade,unsigned phase)
{
 SDL_Color solid={shade,shade,shade,255},restore[256];
 for(unsigned i=0;i<256;i++)restore[i]=(SDL_Color){initial_palette[i]>>16,initial_palette[i]>>8,initial_palette[i],255};
 render_mirror_fade_start(NULL,&solid,0,255);assert(fade_mode);
 for(int step=5;step>=1;step--){palette_step(shade,step,NULL);render_mirror_fade_step(step);if(phase==0&&step==3)return;}
 if(phase==1)return;
 render_mirror_fade_start(restore,NULL,0,255);assert(fade_mode==3);
 for(int step=7;step>=1;step--){palette_step(0,step,initial_palette);render_mirror_fade_step(step);if(phase==2&&step==4)return;}
}
static void fade_cases_run(const char *path,int d)
{
 for(unsigned prov=0;prov<4;prov++)for(unsigned shade=0;shade<=255;shade+=255)for(unsigned phase=0;phase<4;phase++){
 activate_font(path,d);render_mirror_begin();seed(prov);draw_cash("0123",false);operation(1);finish_font();fade_sequence(shade,phase);
 size_t n=(size_t)output->pitch*output->h;Uint8 *out=malloc(n),*saved=malloc(n);memcpy(out,output->pixels,n);memcpy(saved,fade_saved->pixels,n);
 activate_font(path,d);render_mirror_begin();seed(prov);draw_cash("0123",true);operation(1);finish_font();assert(font_output_generation);fade_sequence(shade,phase);
 font_clear_cached(12);assert(!font_owned());assert(last_output_valid&&last_output_scene_hd);
 if(memcmp(out,output->pixels,n)||memcmp(saved,fade_saved->pixels,n)){fprintf(stderr,"fade mismatch d%d provenance%u shade%u phase%u\n",d,prov,shade,phase);abort();}
 render_mirror_hud_suspend();render_mirror_hud_suspend();assert(!memcmp(out,output->pixels,n));assert(!memcmp(saved,fade_saved->pixels,n));
 free(out);free(saved);fade_cases++;
 }
}
static void level(const char *text,bool enabled)
{
 if(enabled)render_mirror_text_level_begin(VGAScreenSeg,text);JE_outText(VGAScreenSeg,268,118,text,12,4);if(enabled)render_mirror_text_level_end();
}
static void erase_message(bool help)
{
 render_mirror_text_message_erase_begin();blit_sprite(VGAScreenSeg,16,189,OPTION_SHAPES,36);render_mirror_text_message_erased(help);if(help)JE_outText(VGAScreenSeg,20,190,"Help prompt",0,4);
}
static void persistent_start(const char *path,int d,bool enabled)
{
 activate_font(path,d);textErase=0;if(!enabled)font_gameplay=false;
 level("Tyrian",enabled);JE_drawTextWindow("~Longer~ message gy");assert(textErase==100);
 if(enabled)assert(font_persistent[0].valid&&font_persistent[1].valid);
 render_mirror_begin();seed(0);finish_font();
}
static void persistent_action(unsigned op)
{
 switch(op){
 case 0:break;case 1:JE_drawTextWindow("gy");break;case 2:JE_drawTextWindow("");break;
 case 3:erase_message(false);textErase=0;break;case 4:erase_message(true);textErase=1;break;
 case 5:JE_drawTextWindow("\x80 extended");break;
 case 6:{char s[101];memset(s,'W',100);s[100]=0;JE_drawTextWindow(s);JE_drawTextWindow("short");break;}
 case 7:level("Again",true);break;case 8:((Uint8 *)VGAScreenSeg->pixels)[190*320+20]^=1;break;
 case 9:render_mirror_hud_suspend();render_mirror_hud_suspend();break;
 case 10:assert(textErase==100);break;
 }
 render_mirror_begin();seed(0);finish_font();
}
static void persistent_cases_run(const char *path,int d)
{
 for(unsigned op=0;op<11;op++)for(unsigned phase=0;phase<4;phase++){
 persistent_start(path,d,false);persistent_action(op);fade_sequence(0,phase);
 size_t n=(size_t)output->pitch*output->h;Uint8 *out=malloc(n),*saved=malloc(n);memcpy(out,output->pixels,n);memcpy(saved,fade_saved->pixels,n);
 persistent_start(path,d,true);persistent_action(op);
 if(op==5||op==6)assert(font_persistent[1].poison&&!memchr(font_powner+416,1,1792));
 if(op==3||op==4||op==8)assert(!memchr(font_powner+416,1,1792));if(op==7)assert(font_persistent[0].poison&&!memchr(font_powner,1,416));
 fade_sequence(0,phase);font_clear_cached(3);
 if(memcmp(out,output->pixels,n)||memcmp(saved,fade_saved->pixels,n)){fprintf(stderr,"persistent mismatch d%d op%u phase%u\n",d,op,phase);abort();}
 free(out);free(saved);persistent_cases++;
 }
 activate_font(path,d);textErase=0;JE_drawTextWindow("hello");erase_message(true);textErase=0;JE_drawTextWindow("new");assert(font_persistent[1].poison);
 activate_font(path,d);textErase=0;JE_drawTextWindow("hello");textErase=0;JE_drawTextWindow("new");assert(font_persistent[1].poison);
}
/* Independent alpha formula; does not use font_plan or the mirror compositor. */
static void scalar_run(const char *path,int d)
{
 const char *texts[]={"00000000000000000000","g~py~ ?\t_","AAAAAAAAAAAAAAAAAAAA","", "~~ ~~"};
 for(unsigned t=0;t<5;t++)for(unsigned prov=0;prov<4;prov++){
 activate_font(path,d);render_mirror_begin();seed(prov);size_t n=(size_t)canvas->pitch*canvas->h;Uint32 *want=malloc(n);memcpy(want,canvas->pixels,n);
 int x=t?28:30,y=t?28:175,hue=2,value=t?6:4;const char *text=texts[t];
 for(unsigned pass=0;pass<5;pass++){
  int px=x+(pass==0?-1:pass==1?1:0),py=y+(pass==2?-1:pass==3?1:0),bright=0;
  for(unsigned j=0;text[j];j++){
   unsigned ch=(unsigned char)text[j];if(ch==' '){px+=6;continue;}if(ch=='~'){bright=bright?0:4;continue;}
   int id=font_ascii[ch];if(id<0)continue;Sprite *g=&sprite_table[TINY_FONT].sprite[id];
   unsigned index=pass<4?0:(unsigned)((hue<<4)|(7+value+bright));Uint32 c=0xff000000u|rgb_palette[index];
   for(int yy=0;yy<g->height*d;yy++)for(int xx=0;xx<g->width*d;xx++){
    unsigned ax=xx/(d/4),ay=yy/(d/4),a=((ax/4+ay/4+(unsigned)id)%3==0)?0:((ax*29+ay*11+(unsigned)id*13)%255)+1;
    Uint32 *dst=want+(py*d+yy)*canvas->w+px*d+xx,out=0xff000000u;
    for(unsigned shift=0;shift<24;shift+=8)out|=((((*dst>>shift)&255)*(255-a)+((c>>shift)&255)*a+127)/255)<<shift;
    *dst=out;
   }px+=g->width+1;
  }
 }
 unsigned alloc=allocations;size_t font_alloc=font_alloc_calls;Uint8 *history=font_history;
 render_mirror_text_begin(game_screen,t?1:0,x,y,text,hue,value);JE_textShade(game_screen,x,y,text,hue,value,FULL_SHADE);render_mirror_text_end();
 if(t==0)assert(font_scenes[0].rect.w==101&&font_scenes[0].rect.h==8);
 if(t==2)assert(font_scenes[1].rect.w==141&&font_scenes[1].rect.h==10);
 assert(allocations==alloc&&font_alloc_calls==font_alloc&&font_history==history);assert(!memcmp(want,canvas->pixels,n));free(want);scalar_cases++;
 }
 assert(FONT_HISTORY_BYTES==2850090);
 size_t descriptor_bytes=sizeof(font_scenes)+sizeof(font_persistent)+sizeof(font_commands)+sizeof(font_command_count)+sizeof(font_command_next)+sizeof(font_context)+
  sizeof(font_glyph_active)+sizeof(font_gameplay)+sizeof(font_suspended)+sizeof(font_source_surface)+sizeof(font_source_pixels)+sizeof(font_source_format)+sizeof(font_source_pitch)+sizeof(font_density)+
  sizeof(font_generation)+sizeof(font_output_generation)+sizeof(font_saved_generation)+sizeof(font_output_palette)+sizeof(font_history)+sizeof(font_under)+sizeof(font_saved_under)+sizeof(font_green_under)+sizeof(font_green_first)+
  sizeof(font_lower_owner)+sizeof(font_saved_lower_owner)+sizeof(font_owner)+sizeof(font_saved_owner)+sizeof(font_cloud)+sizeof(font_green_owner)+sizeof(font_selected)+sizeof(font_pre)+sizeof(font_post)+sizeof(font_powner)+sizeof(font_psaved_owner)+sizeof(font_prects)+sizeof(font_poffset)+127*2+11*4+sizeof(void *)+2*sizeof(bool);
 assert(descriptor_bytes<=4096);
 printf("HUF1 finite memory: history=%u alpha=163840 retained descriptors=%zu total=%zu bytes\n",FONT_HISTORY_BYTES,descriptor_bytes,FONT_HISTORY_BYTES+163840+descriptor_bytes);
}
static void trust_run(const char *path,int d)
{
 for(unsigned fault=0;fault<18;fault++){
 activate_font(path,d);render_mirror_begin();seed(0);draw_cash("0123",true);finish_font();assert(font_output_generation);
 SDL_Surface *g=game_screen,*v=VGAScreenSeg;void *gp=g->pixels,*vp=v->pixels;int pitch=g->pitch,w=g->w;SDL_PixelFormat *fmt=g->format;int bits=fmt->BitsPerPixel;
 SDL_Surface gc=*g,vc=*v;SDL_PixelFormat gf=*g->format,vf=*v->format;SDL_PixelFormat *vfmt=v->format;Uint8 clone[64000];
 switch(fault){
 case 0:game_screen=NULL;break;case 1:g->pixels=NULL;break;case 2:g->pitch++;break;case 3:g->w--;break;case 4:g->format=NULL;break;case 5:fmt->BitsPerPixel=32;break;
 case 6:VGAScreenSeg=NULL;break;case 7:v->pixels=NULL;break;case 8:((Uint8 *)v->pixels)[3200]^=1;break;
 case 9:font_output_palette[0]^=1;break;case 10:font_output_generation++;break;
 case 12:game_screen=&gc;break;
 case 13:memcpy(clone,gp,64000);g->pixels=clone;break;
 case 14:g->format=&gf;break;
 case 15:VGAScreenSeg=&vc;break;
 case 16:memcpy(clone,vp,64000);v->pixels=clone;break;
 case 17:v->format=&vf;break;
 case 11:{FontScene *r=font_scenes;bool found=false;for(int y=0;y<r->rect.h&&!found;y++)for(int x=0;x<r->rect.w&&!found;x++)for(int sy=0;sy<d&&!found;sy++)for(int sx=0;sx<d;sx++){
 unsigned k=r->offset+(unsigned)((y*r->rect.w+x)*d*d+sy*d+sx);if(font_owner[k]){hd_owner[((r->rect.y+y)*d+sy)*canvas->w+(r->rect.x+x)*d+sx]=0;found=true;break;}}assert(found);break;}
 }
 font_clear_cached(15);assert(!last_output_valid&&!ready&&!have_fade_saved&&!font_owned());
 game_screen=g;VGAScreenSeg=v;g->pixels=gp;v->pixels=vp;g->pitch=pitch;g->w=w;g->format=fmt;v->format=vfmt;fmt->BitsPerPixel=bits;trust_cases++;
 }
 for(unsigned entry=0;entry<3;entry++)for(unsigned saved=0;saved<6;saved++){
 activate_font(path,d);render_mirror_begin();seed(0);draw_cash("0",true);finish_font();SDL_Color black={0,0,0,255};
 if(entry==2||saved>=3)render_mirror_fade_start(NULL,&black,0,255);
 if(saved==2)font_output_generation=font_saved_generation=0;
 else if(saved==3)font_saved_generation=0;
 else if(saved>=4){unsigned k=font_scenes[0].offset;while(!font_owner[k])k++;if(saved==4)font_saved_owner[k]=0;else font_owner[k]=0;}
 else if(saved)font_saved_generation=font_generation+1;else font_output_generation=font_generation+1;
 if(entry==0)assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));
 else if(entry==1)render_mirror_fade_start(NULL,&black,0,255);
 else {palette_step(0,5,NULL);render_mirror_fade_step(5);}
 assert(!last_output_valid&&!ready&&!fade_mode&&!font_owned());trust_cases++;
 }
 for(unsigned saved=0;saved<2;saved++){
 persistent_start(path,d,true);SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);
 unsigned k=0;while(!font_powner[k])k++;assert(k<FONT_PERSIST_CELLS);
 if(saved)font_psaved_owner[k]=0;else font_powner[k]=0;
 assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));assert(!last_output_valid&&!ready&&!font_owned());trust_cases++;
 }
 activate_font(path,d);render_mirror_begin();render_mirror_text_begin(game_screen,0,30,175,"0",2,4);assert(font_context==0);SDL_Surface *g=game_screen;game_screen=NULL;
 render_mirror_text_glyph_begin(g,29,175,TINY_FONT,font_ascii['0'],true,0,-1);assert(font_context<0&&reject_reason&&!font_scene_owned(font_scenes,font_owner));game_screen=g;
 for(unsigned bad=0;bad<6;bad++){
 activate_font(path,d);render_mirror_begin();seed(1);
 render_mirror_text_begin(bad==0?VGAScreenSeg:game_screen,bad==5?1:0,bad==1?31:30,175,bad==2?"\x80":bad==3?"123456789012345678901":"0",bad==4?8:2,4);
 assert(font_context<0);trust_cases++;
 }
 for(unsigned mode=0;mode<2;mode++){
 activate_font(path,d);render_mirror_begin();draw_cash("0",true);finish_font();if(mode)galagaMode=true;else twoPlayerMode=true;hud_check_mode();assert(!font_gameplay&&!font_owned());twoPlayerMode=galagaMode=false;render_mirror_begin();assert(!font_gameplay);trust_cases++;
 }
 activate_font(path,d);render_mirror_hud_suspend();assert(font_suspended);render_mirror_begin();assert(!font_suspended);draw_cash("0",true);assert(font_scene_owned(font_scenes,font_owner));
}
static void halo_run(const char *path,int d)
{
 activate_font(path,d);render_mirror_begin();draw_cash("0123",true);SDL_Rect box=font_scenes[0].rect;
 for(int y=box.y-15;y<=box.y+box.h;y++)for(int x=box.x-13;x<=box.x+box.w;x++){
 if(!font_intersects(box,(SDL_Rect){x-1,y-1,14,16})||font_intersects(box,(SDL_Rect){x,y,12,14}))continue;
 Asset a=head;a.bank=ASSET_EXPLOSION;a.index=78;
 activate_font(path,d);render_mirror_begin();last_restore=(SDL_Rect){0};seed(3);draw_cash("0123",false);draw_asset_filtered(x,y,&a,MIRROR_BLEND,NULL,0,NULL,NULL,NULL);suppress=false;Snapshot b=snap();
 activate_font(path,d);render_mirror_begin();last_restore=(SDL_Rect){0};seed(3);draw_cash("0123",true);draw_asset_filtered(x,y,&a,MIRROR_BLEND,NULL,0,NULL,NULL,NULL);suppress=false;
 assert(!font_scenes[0].canvas_live&&!font_scene_owned(font_scenes,font_owner));same_snapshot(&b,3,200);free(b.bytes);halo_cases++;
 }
}
static void both_maximal_records(const char *path,int d)
{
 activate_font(path,d);render_mirror_begin();seed(1);draw_cash("00000000000000000000",false);JE_textShade(game_screen,28,28,"AAAAAAAAAAAAAAAAAAAA",2,6,FULL_SHADE);Snapshot b=snap();
 activate_font(path,d);render_mirror_begin();seed(1);draw_cash("00000000000000000000",true);render_mirror_text_begin(game_screen,1,28,28,"AAAAAAAAAAAAAAAAAAAA",2,6);JE_textShade(game_screen,28,28,"AAAAAAAAAAAAAAAAAAAA",2,6,FULL_SHADE);render_mirror_text_end();
 assert(font_scenes[0].used==808u*d*d&&font_scenes[1].used==1410u*d*d);font_strip_scene(0);font_strip_scene(1);same_snapshot(&b,1,300);free(b.bytes);scalar_cases++;
}
static void allocation_failure(const char *path,int d)
{
 activate_font(path,d);font_shutdown();font_alloc_fail=true;font_start(VGAScreenSeg);
 assert(!font_history&&!font_gameplay);font_alloc_fail=false;font_start(VGAScreenSeg);
 assert(font_history&&font_gameplay);size_t count=font_alloc_calls;
 for(unsigned i=0;i<4;i++){render_mirror_begin();draw_cash("0",true);finish_font();render_mirror_hud_suspend();}
 assert(font_alloc_calls==count);
}
int main(int argc,char **argv)
{
 assert(argc==2||argc==3);bool quick=argc==3&&!strcmp(argv[2],"quick");materials();
 for(int d=4;d<=8;d+=4){basic(argv[1],d);if(!quick){writer_cases_run(argv[1],d);abort_cases(argv[1],d);fade_cases_run(argv[1],d);persistent_cases_run(argv[1],d);halo_run(argv[1],d);}scalar_run(argv[1],d);both_maximal_records(argv[1],d);trust_run(argv[1],d);allocation_failure(argv[1],d);}cleanup();
 assert(font_alloc_calls==font_free_calls+font_alloc_failed&&font_alloc_bytes==font_free_calls*FONT_HISTORY_BYTES);
 printf("HUF1 renderer source integration PASS: %u writer/abort, %u fade, %u persistent, %u scalar geometry, %u trust and %u halo-only counterfactuals; %zu history allocations freed, %zu safely failed\n",writer_cases,fade_cases,persistent_cases,scalar_cases,trust_cases,halo_cases,font_free_calls,font_alloc_failed);return 0;
}
