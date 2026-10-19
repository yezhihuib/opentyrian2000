/* Focused PSS1 material regression harness. Reuses authentic external fixtures,
 * never changes a frozen projection or installs synthetic test artwork. */
#define main pregame_font_original_test_main
#include "pregame_font_test.c"
#undef main
#include <math.h>

static const int shield_values[12]={-10,-8,-7,-6,-5,-4,-3,-1,-3,0,2,4};
static const char *shield_name="shop-shield-option26-v1.hda";
static const char *shield_siblings[]={
 "settings-font-large-v1.hda","settings-font-medium-v1.hda","settings-font-tiny-v1.hda",
 "shop-frame-metal-v1.hda","shop-talon-option31-v1.hda",
 "shop-front-weapon00-v1.hda","shop-generator-weapon16-v1.hda"};
static const char *shield_menu_files[]={"shop-menu-run0-v1.hda","shop-menu-run1-v1.hda","shop-menu-run2-v1.hda","shop-menu-run3-v1.hda","shop-menu-run4-v1.hda","shop-menu-run5-v1.hda","shop-menu-run6-v1.hda"};
enum { SHIELD_TEST_FILES=15 };
static const char *shield_file_name(unsigned n)
{return n<7?shield_siblings[n]:n==7?shield_name:shield_menu_files[n-8];}
static unsigned material_states,parser_rejections;
static Uint32 prefix_output[SF_OW*SF_OH];
static Uint8 prefix_underlay[SF_N];

/* Deliberately copy the legacy Uint8 wrap, then its two saturation branches.
 * This is independent of the font's unsafe OR helper and of hv_tone(). */
static Uint8 shield_tone_oracle(unsigned role,int value)
{
 Uint8 tone=(Uint8)((int)role+value);
 if(tone>15)tone=tone>=31?0:15;
 return tone;
}
static Uint32 shield_color_oracle(unsigned q4,int value)
{
 unsigned role=q4>>4,frac=q4&15;
 unsigned hi=role<15?role+1:15;
 SDL_Color a=sf.expected_palette[240|shield_tone_oracle(role,value)];
 SDL_Color b=sf.expected_palette[240|shield_tone_oracle(hi,value)];
 return ((Uint32)((a.r*(16-frac)+b.r*frac+8)/16)<<16)|
        ((Uint32)((a.g*(16-frac)+b.g*frac+8)/16)<<8)|
        ((a.b*(16-frac)+b.b*frac+8)/16);
}
static Uint32 shield_over_oracle(Uint32 old,Uint32 rgb,unsigned alpha)
{
 Uint32 out=(alpha+(((old>>24)*(255-alpha)+127)/255))<<24;
 for(unsigned shift=0;shift<24;shift+=8)
  out|=(((((rgb>>shift)&255)*alpha+((old>>shift)&255)*(255-alpha)+127)/255)<<shift);
 return out;
}
static unsigned shield_commands(void)
{unsigned count=0;for(unsigned i=0;i<sf.count;i++)count+=sf.commands[i].kind==C_SHIELD;return count;}
static unsigned shield_command(void)
{for(unsigned i=0;i<sf.count;i++)if(sf.commands[i].kind==C_SHIELD)return i;REQUIRE(false);return 0;}
static void shield_assembly(int value,unsigned mode)
{
 blit_sprite(VGAScreen,test_ship==31?35:31,test_ship==31?33:36,5,test_ship);
 draw_generator();blit_sprite(VGAScreen,test_front_x,test_front_y,6,test_front);
 blit_sprite(VGAScreen,41,92,6,test_rear);
 if(!sf.product){blit_sprite2x2(VGAScreen,3,84,shopSpriteSheet,1);blit_sprite2x2(VGAScreen,129,84,shopSpriteSheet,5);}
 if(mode==3)blit_sprite(VGAScreen,28,23,5,26); /* shared source, original mode */
 blit_sprite_hv(VGAScreen,mode==1?29:28,23,5,26,mode==2?14:15,value);
 if(mode==4)blit_sprite_hv(VGAScreen,28,23,5,26,15,value);
 if(mode==5)blit_sprite(VGAScreen,61,48,6,0); /* source reuse after terminal */
}
static void shield_root_draw(unsigned menu,int value,unsigned mode)
{
 memcpy(VGAScreen->pixels,raw_base,SF_N);trace=SF_FNV;trace_count=0;
 run(PREGAME_HEADING,0,234-JE_textWidth(menuInt[menu+1][0],0)/2,10,menuInt[menu+1][0],0,15,-3);
 for(unsigned row=2;row<=(menu?9u:7u);row++){
  char text[20];snprintf(text,sizeof(text),"%s%s",row==4?"~":"",menuInt[menu+1][row-1]);
  run(PREGAME_ROW,row,166,38+(row-2)*16+(!menu&&row==7?16:0),text,1,15,-3);
 }
 if(!menu){pregame_font_phase_begin(PREGAME_CUBES,0,0);for(unsigned i=1;i<=4;i++){blit_sprite_dark(VGAScreen,190+i*18+2,38,5,34,false);blit_sprite(VGAScreen,190+i*18,37,5,34);}pregame_font_phase_end();}
 run(PREGAME_CASH,0,65,173,"10000",2,1,6);
 pregame_font_phase_begin(PREGAME_BARS,15,10);JE_barDrawShadow(VGAScreen,42,152,3,14,15,2,13);JE_barDrawShadow(VGAScreen,104,152,2,14,10,2,13);pregame_font_phase_end();
 pregame_font_phase_begin(PREGAME_SHIP,0,0);shield_assembly(value,mode);pregame_font_phase_end();
 run(PREGAME_FOOTER,4,10,187,mainMenuHelp[menuHelp[menu][2]-1],2,14,1);pregame_font_frame_end();
}
static void shield_root(const char *dir,unsigned menu,int value)
{
 acquire(dir,menu,4,4);shield_root_draw(menu,value,0);
 REQUIRE(sf.active&&sf.frame&&sf.stage==S_READY&&sf.shop_shield&&shield_commands()==1);
 struct SfCommand *c=&sf.commands[shield_command()];
 REQUIRE(c->bank==5&&c->id==26&&c->x==28&&c->y==23&&c->w==99&&c->h==23&&c->hue==15&&c->value==value&&c->events>0);
 Uint8 expected[SF_N];memcpy(expected,sf.pixels,SF_N);uint64_t expected_trace=trace;unsigned n=trace_count;
 sf.active=false;shield_root_draw(menu,value,0);sf.active=true;
 REQUIRE(!memcmp(expected,sf.pixels,SF_N)&&trace==expected_trace&&trace_count==n&&exact());
 ++material_states;
}
static void shield_product(const char *dir,unsigned category,int value,unsigned mode)
{
 pregame_font_set_directory(dir);memcpy(VGAScreen->pixels,raw_base,SF_N);memcpy(VGAScreen2->pixels,raw_base,SF_N);live_palette(colors);
 pregame_font_product_begin(category,2,4,true,VGAScreen,VGAScreen2);REQUIRE(sf.active);
 trace=SF_FNV;trace_count=0;const char *title=menuInt[2][category-1];
 product_text(PREGAME_HEADING,0,234-JE_textWidth(title,0)/2,10,title,0,15,-3);
 const char *names[]={"Shield Low","Shield High","Done"};
 for(unsigned row=1;row<=3;row++){
  unsigned hue=row==1?0:1;int tone=row==1?7:4;
  product_text(PREGAME_PRODUCT_NAME,row,185,40+(row-1)*26,names[row-1],2,hue,tone);
  if(row<3){blit_sprite2x2(VGAScreen,160,36+(row-1)*26,shopSpriteSheet,1);product_text(PREGAME_PRODUCT_COST,row,187,50+(row-1)*26,"Cost: 500",2,hue,tone);}
 }
 product_text(PREGAME_CASH,0,65,173,"10000",2,1,6);shield_assembly(value,mode);
 product_text(PREGAME_FOOTER,2,10,187,mainMenuHelp[23],2,14,1);pregame_font_frame_end();
}
/* Render the exact scene twice, excluding only the new material the first
 * time. Its original indexed events are omitted with it. All other siblings,
 * glyphs, classic writes and footer commands remain in their true order. */
static void shield_render_check(void)
{
 REQUIRE(sf.frame&&shield_commands()==1);unsigned k=shield_command();struct SfCommand saved=sf.commands[k];
 sf.commands[k].kind=C_CLASSIC;sf.commands[k].events=0;render();
 memcpy(prefix_output,sf.output,SF_OUT_BYTES);memcpy(prefix_underlay,sf.underlay,SF_N);
 sf.commands[k]=saved;render();REQUIRE(replay_matches()&&!memcmp(sf.replay,sf.expected,SF_N));
 REQUIRE(!memcmp(prefix_underlay,sf.underlay,SF_N));sprite_underlay_checks();
 for(unsigned y=0;y<SF_OH;y++)for(unsigned x=0;x<SF_OW;x++){
  unsigned out=y*SF_OW+x;Uint32 wanted=prefix_output[out];
  if(x>=112&&x<508&&y>=92&&y<184){unsigned at=(y-92)*396+x-112;wanted=shield_over_oracle(wanted,shield_color_oracle(sf.shop_shield[PF_SHIELD_PLANE+at],saved.value),sf.shop_shield[at]);}
  REQUIRE(sf.output[out]==wanted);
 }
 for(unsigned i=saved.first;i<saved.first+saved.events;i++)REQUIRE(sf.owner[sf.events[i].position]);
}
static void shield_math_checks(const char *dir)
{
 shield_root(dir,0,-5);render();
 for(int value=-128;value<=127;value++)for(unsigned role=0;role<=15;role++)REQUIRE(hv_tone(role,value)==shield_tone_oracle(role,value));
 for(int value=-128;value<=127;value++)for(unsigned q4=0;q4<=240;q4++)REQUIRE(shield_color(q4,value)==shield_color_oracle(q4,value));
 REQUIRE(hv_tone(0,-128)==0&&hv_tone(15,127)==0&&hv_tone(15,1)==15&&hv_tone(0,-1)==0);
 REQUIRE(face(0,15,-3)==253); /* font's unsafe behavior remains separate */
 uint64_t same=0;
 for(unsigned id=0;id<12;id++){
  shield_root(dir,id%2,shield_values[id]);shield_render_check();
  if(id==6)same=hash(sf.output,SF_OUT_BYTES);
  if(id==8){/* compare material, because root text selection differs by menu */
   shield_root(dir,0,shield_values[6]);shield_render_check();REQUIRE(hash(sf.output,SF_OUT_BYTES)==same);
  }
 }
 for(unsigned n=0;n<4;n++){int value=n==0?-128:n==1?-127:n==2?126:127;shield_root(dir,0,value);shield_render_check();}
 shield_root(dir,0,-5);uint64_t output=hash(sf.output,SF_OUT_BYTES);render();output=hash(sf.output,SF_OUT_BYTES);
 for(unsigned n=0;n<20;n++){render();REQUIRE(hash(sf.output,SF_OUT_BYTES)==output);}
 cursor_checks();REQUIRE(exact());render();REQUIRE(replay_matches());present_checks();
}
static void shield_gate_checks(const char *dir)
{
 shield_root(dir,0,-5);unsigned stage=sf.stage,illustration=sf.illustration;bool terminal=sf.ship_shield;
 sf.stage=S_PRIMITIVE;sf.phase=PREGAME_SHIP;sf.illustration=3;sf.ship_shield=false;
 REQUIRE(shop_shield_match(28,23,5,26,PREGAME_FACE,15,-5));
 REQUIRE(!shop_shield_match(29,23,5,26,PREGAME_FACE,15,-5));REQUIRE(!shop_shield_match(28,24,5,26,PREGAME_FACE,15,-5));
 REQUIRE(!shop_shield_match(28,23,6,26,PREGAME_FACE,15,-5));REQUIRE(!shop_shield_match(28,23,5,25,PREGAME_FACE,15,-5));
 REQUIRE(!shop_shield_match(28,23,5,26,PREGAME_ORIGINAL,15,-5));REQUIRE(!shop_shield_match(28,23,5,26,PREGAME_DARK,15,-5));
 REQUIRE(!shop_shield_match(28,23,5,26,PREGAME_FACE,14,-5));
 REQUIRE(!shop_shield_match(28,23,5,26,PREGAME_FACE,15,-129));REQUIRE(!shop_shield_match(28,23,5,26,PREGAME_FACE,15,128));
 for(unsigned i=0;i<3;i++){sf.illustration=i;REQUIRE(!shop_shield_match(28,23,5,26,PREGAME_FACE,15,-5));}
 sf.illustration=3;sf.ship_shield=true;REQUIRE(!shop_shield_match(28,23,5,26,PREGAME_FACE,15,-5));sf.ship_shield=false;
 sf.phase=PREGAME_CUBES;REQUIRE(!shop_shield_match(28,23,5,26,PREGAME_FACE,15,-5));sf.phase=PREGAME_SHIP;
 sf.stage=stage;sf.illustration=illustration;sf.ship_shield=terminal;
 for(unsigned mode=1;mode<=5;mode++){
  acquire(dir,0,4,4);shield_root_draw(0,-5,mode);
  if(mode==3){REQUIRE(sf.frame&&shield_commands()==1);shield_render_check();}
  else REQUIRE(!sf.frame);
 }
 test_ship=27;acquire(dir,0,4,4);shield_root_draw(0,-5,0);REQUIRE(sf.frame&&!shield_commands());test_ship=31;
 test_generator_x=63;acquire(dir,0,4,4);shield_root_draw(0,-5,0);REQUIRE(sf.frame&&!shield_commands());test_generator_x=-1;
 for(unsigned category=2;category<=8;category++){
  shield_product(dir,category,-5,0);REQUIRE(sf.frame&&shield_commands()==(unsigned)(category==2||category==5));render();REQUIRE(replay_matches());
  if(category==2||category==5){shield_render_check();for(unsigned n=0;n<5;n++){pregame_font_product_update_begin();product_text(PREGAME_CASH,0,65,173,"10000",2,1,6);pregame_font_product_update_end();REQUIRE(sf.frame&&shield_commands()==1);render();REQUIRE(replay_matches());}}
 }
 for(unsigned category=2;category<=5;category+=3)for(unsigned mode=1;mode<=5;mode++){
  shield_product(dir,category,-5,mode);REQUIRE(sf.frame);render();REQUIRE(replay_matches());
  REQUIRE(shield_commands()==(unsigned)(mode>=3));
 }
 shield_root(dir,0,-5);Sprite *s=sprite(5,26);Uint8 old=s->data[0];s->data[0]^=1;REQUIRE(!exact()&&!sf.active);s->data[0]=old;
 shield_root(dir,0,-5);((Uint8 *)sf.pixels)[20]^=1;pregame_font_cursor_begin();REQUIRE(!sf.frame);
 shield_root(dir,0,-5);pregame_font_table_reset(5);REQUIRE(!sf.active&&!allocated);
}
static void shield_source_padding_checks(const char *dir)
{
 shield_root(dir,0,-5);Uint8 mask[PF_SHIELD_W*PF_SHIELD_H];REQUIRE(shop_shield_source(mask));REQUIRE(hash(mask,sizeof(mask))==UINT64_C(0xb3481df839c0dec8));
 REQUIRE(shop_shield_padding(sf.shop_shield,mask));unsigned ink=0,clear=0,outside=0,unguarded=PF_SHIELD_PLANE;
 for(unsigned y=0;y<92;y++)for(unsigned x=0;x<396;x++){
  unsigned p=y*396+x;if(sf.shop_shield[p]){ink=p;if(!mask[(y/4)*99+x/4])outside++;}else clear=p;
  bool near=false;for(int yy=(int)y/4-1;yy<=(int)y/4+1;yy++)for(int xx=(int)x/4-1;xx<=(int)x/4+1;xx++)if(xx>=0&&xx<99&&yy>=0&&yy<23&&mask[yy*99+xx])near=true;
  if(!near)unguarded=p;
 }
 REQUIRE(outside>0&&unguarded<PF_SHIELD_PLANE);
 Uint8 old=sf.shop_shield[PF_SHIELD_PLANE+ink];sf.shop_shield[PF_SHIELD_PLANE+ink]=241;REQUIRE(!shop_shield_padding(sf.shop_shield,mask));sf.shop_shield[PF_SHIELD_PLANE+ink]=old;
 old=sf.shop_shield[PF_SHIELD_PLANE+clear];sf.shop_shield[PF_SHIELD_PLANE+clear]=1;REQUIRE(!shop_shield_padding(sf.shop_shield,mask));sf.shop_shield[PF_SHIELD_PLANE+clear]=old;
 old=sf.shop_shield[unguarded];sf.shop_shield[unguarded]=1;REQUIRE(!shop_shield_padding(sf.shop_shield,mask));sf.shop_shield[unguarded]=old;REQUIRE(shop_shield_padding(sf.shop_shield,mask));
 Sprite *s=sprite(5,26);Uint16 oldw=s->width,oldh=s->height,olds=s->size;Uint8 *olddata=s->data;
 s->width--;REQUIRE(!shop_shield_source(mask));s->width=oldw;s->height--;REQUIRE(!shop_shield_source(mask));s->height=oldh;s->size--;REQUIRE(!shop_shield_source(mask));s->size=olds;s->data=NULL;REQUIRE(!shop_shield_source(mask));s->data=olddata;
 Uint8 byte=s->data[0];s->data[0]^=1;REQUIRE(!shop_shield_source(mask));s->data[0]=byte;REQUIRE(shop_shield_source(mask));pregame_font_end();
}
static void shield_fade_checks(const char *dir)
{
 for(unsigned incoming=0;incoming<2;incoming++){
  shield_root(dir,0,incoming?4:-8);
  if(incoming){for(unsigned i=0;i<256;i++)sf.expected_palette[i]=(SDL_Color){0,0,0,255};live_palette(sf.expected_palette);sf.metal_gain=0;}
  pregame_font_fade_declare(10);SDL_Color black={0,0,0,255};pregame_font_fade_start(incoming?colors:NULL,incoming?NULL:&black,0,255);REQUIRE(sf.active);
  for(int n=10;n;n--){SDL_Color pal[256];memcpy(pal,sf.expected_palette,sizeof(pal));for(unsigned i=0;i<256;i++){pal[i].r+=((incoming?colors[i].r:0)-pal[i].r)/n;pal[i].g+=((incoming?colors[i].g:0)-pal[i].g)/n;pal[i].b+=((incoming?colors[i].b:0)-pal[i].b)/n;}live_palette(pal);pregame_font_fade_step(n,0,255);REQUIRE(sf.active&&sf.fade_remaining==n-1);shield_render_check();}
  REQUIRE(sf.metal_gain==(incoming?255u:0u));
 }
 shield_root(dir,0,-5);rgb_palette[240]^=1;REQUIRE(!palette_matches());
 SDL_Surface *out=SDL_CreateRGBSurfaceWithFormat(0,640,400,32,SDL_PIXELFORMAT_RGB888);REQUIRE(out);SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(out);REQUIRE(renderer);SDL_Texture *reference=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_RGB888,SDL_TEXTUREACCESS_STREAMING,640,400);REQUIRE(reference);SDL_Rect dst={0,0,640,400};
 REQUIRE(!pregame_font_present(renderer,reference,VGAScreen,&dst,false)&&!sf.frame);pregame_font_release_texture();SDL_DestroyTexture(reference);SDL_DestroyRenderer(renderer);SDL_FreeSurface(out);live_palette(colors);
 pregame_font_set_directory(dir);memcpy(VGAScreen->pixels,raw_base,SF_N);memcpy(VGAScreen2->pixels,raw_base,SF_N);rgb_palette[240]^=1;pregame_font_begin(0,4,7,true,10000,4,VGAScreen,VGAScreen2);REQUIRE(!sf.active&&!allocated);live_palette(colors);
 shield_root(dir,0,-5);pregame_font_fade_declare(10);SDL_Color black={0,0,0,255};pregame_font_fade_start(NULL,&black,240,255);REQUIRE(!sf.active&&!allocated);
}
static void shield_occlusion_checks(const char *dir)
{
 shield_root(dir,0,-5);present_checks();render();unsigned k=shield_command();const struct SfCommand *c=&sf.commands[k];unsigned p=0;
 for(unsigned i=c->first;i<c->first+c->events;i++){unsigned q=sf.events[i].position;if(sf.shop_shield[((q/SF_W-23)*4)*396+(q%SF_W-28)*4]){p=q;break;}}
 REQUIRE(p);unsigned x=p%SF_W*4,y=p/SF_W*4;
 /* An earlier original same-index write is retained as the true underlay. */
 REQUIRE(sf.count+1<SF_COMMANDS);memmove(sf.commands+k+1,sf.commands+k,(sf.count-k)*sizeof(*sf.commands));sf.count++;
 struct SfCommand *early=&sf.commands[k];memset(early,0,sizeof(*early));early->kind=C_CLASSIC;early->first=sf.event_count;early->events=1;REQUIRE(event(p%SF_W,p/SF_W,77,0));
 render();REQUIRE(sf.underlay[p]==77);shield_render_check();
 struct SfCommand *late=append(C_CLASSIC,0,0,0,0,0,0);REQUIRE(late&&event(p%SF_W,p/SF_W,sf.expected[p],0));late->events=1;render();
 for(unsigned yy=0;yy<4;yy++)for(unsigned xx=0;xx<4;xx++)REQUIRE(!sf.output[(y+yy)*SF_OW+x+xx]);REQUIRE(sf.underlay[p]==sf.expected[p]&&sf.metal_blocked[p]);
 /* Authored text after the original erasure remains visible in its own order. */
 REQUIRE(append(C_FACE,p%SF_W,p/SF_W,2,font_ascii['A'],1,6));render();REQUIRE(sf.frame);
}
static Uint8 *read_resource(const char *dir,const char *name,size_t *size)
{
 FILE *f=open_data(dir,name);REQUIRE(!fseek(f,0,SEEK_END));long n=ftell(f);REQUIRE(n>=0);rewind(f);*size=(size_t)n;Uint8 *data=malloc(*size+1);REQUIRE(data&&fread(data,1,*size,f)==*size&&!fclose(f));data[*size]=0;return data;
}
static void shield_temp_links(char *temp,char paths[SHIELD_TEST_FILES][1024],const char *dir)
{
 REQUIRE(mkdtemp(temp));for(unsigned i=0;i<SHIELD_TEST_FILES;i++){const char *name=shield_file_name(i);REQUIRE(snprintf(paths[i],1024,"%s/%s",temp,name)<1024);if(i!=7){char source[1024];REQUIRE(snprintf(source,sizeof(source),"%s/%s",dir,name)<(int)sizeof(source));REQUIRE(!symlink(source,paths[i]));}}
}
static void shield_optional_rejected(const char *dir)
{
 acquire(dir,0,4,4);REQUIRE(sf.active&&sf.frame&&sf.metal&&sf.shop_sprite&&sf.shop_front&&sf.shop_generator&&!sf.shop_shield);for(unsigned r=0;r<7;r++)REQUIRE(sf.menu_run[r]);++parser_rejections;pregame_font_end();REQUIRE(!allocated);
}
static void shield_parser_checks(const char *dir)
{
 pregame_font_end();char temp[]="/tmp/shop-shield-parser-XXXXXX",paths[SHIELD_TEST_FILES][1024];shield_temp_links(temp,paths,dir);size_t size;Uint8 *data=read_resource(dir,shield_name,&size);REQUIRE(size==128+PF_SHIELD_BYTES&&hash(data+128,PF_SHIELD_BYTES)==PF_SHIELD_HASH);
 shield_optional_rejected(temp);
 for(unsigned offset=0;offset<128;offset++){data[offset]^=128;write_bytes(paths[7],data,size);shield_optional_rejected(temp);data[offset]^=128;}
 const size_t sizes[]={0,3,63,127,128,128+PF_SHIELD_PLANE-1,size-1,size+1};for(unsigned i=0;i<sizeof(sizes)/sizeof(*sizes);i++){write_bytes(paths[7],data,sizes[i]);shield_optional_rejected(temp);}
 const unsigned mutations[]={128,128+PF_SHIELD_PLANE-1,128+PF_SHIELD_PLANE,128+PF_SHIELD_BYTES-1};
 for(unsigned i=0;i<sizeof(mutations)/sizeof(*mutations);i++){data[mutations[i]]^=1;write_bytes(paths[7],data,size);shield_optional_rejected(temp);data[mutations[i]]^=1;}
 write_bytes(paths[7],data,size);acquire(temp,0,4,4);REQUIRE(sf.shop_shield);pregame_font_end();
 /* Isolate the optional loader allocation rather than assuming sibling order. */
 acquire(temp,0,4,4);lease_free(sf.shop_shield);sf.shop_shield=NULL;fail_allocation=allocation_calls;load_shop_shield();fail_allocation=UINT_MAX;REQUIRE(sf.active&&!sf.shop_shield&&sf.shop_sprite&&sf.shop_front&&sf.shop_generator);pregame_font_end();REQUIRE(!allocated);
 REQUIRE(!unlink(paths[7]));REQUIRE(!mkdir(paths[7],0700));shield_optional_rejected(temp);REQUIRE(!rmdir(paths[7]));REQUIRE(!mkfifo(paths[7],0600));shield_optional_rejected(temp);REQUIRE(!unlink(paths[7]));
 /* Corrupt and absent material have exactly the same sibling presentation. */
 acquire(temp,0,4,4);shield_root_draw(0,-5,0);REQUIRE(sf.frame&&!shield_commands());render();uint64_t classic=hash(sf.output,SF_OUT_BYTES),indexed=hash(sf.pixels,SF_N),underlay=hash(sf.underlay,SF_N);pregame_font_end();
 data[128]^=1;write_bytes(paths[7],data,size);acquire(temp,0,4,4);shield_root_draw(0,-5,0);render();REQUIRE(sf.frame&&!shield_commands()&&hash(sf.output,SF_OUT_BYTES)==classic&&hash(sf.pixels,SF_N)==indexed&&hash(sf.underlay,SF_N)==underlay);data[128]^=1;pregame_font_end();
 for(unsigned i=0;i<SHIELD_TEST_FILES;i++)REQUIRE(!unlink(paths[i]));REQUIRE(!rmdir(temp));free(data);
}
static void shield_independence_checks(const char *dir)
{
 pregame_font_end();char temp[]="/tmp/shop-shield-siblings-XXXXXX",paths[SHIELD_TEST_FILES][1024];shield_temp_links(temp,paths,dir);char source[1024];REQUIRE(snprintf(source,sizeof(source),"%s/%s",dir,shield_name)<(int)sizeof(source));REQUIRE(!symlink(source,paths[7]));
 for(unsigned sibling=3;sibling<SHIELD_TEST_FILES;sibling++){
  if(sibling==7)continue;
  REQUIRE(!unlink(paths[sibling]));shield_root(temp,0,-5);shield_render_check();REQUIRE(sf.shop_shield);
  REQUIRE((sf.metal!=NULL)==(sibling!=3));REQUIRE((sf.shop_sprite!=NULL)==(sibling!=4));REQUIRE((sf.shop_front!=NULL)==(sibling!=5));REQUIRE((sf.shop_generator!=NULL)==(sibling!=6));for(unsigned r=0;r<7;r++)REQUIRE((sf.menu_run[r]!=NULL)==(sibling!=r+8));pregame_font_end();
  size_t size;Uint8 *bad=read_resource(dir,shield_file_name(sibling),&size);bad[128]^=1;write_bytes(paths[sibling],bad,size);free(bad);shield_root(temp,0,-5);shield_render_check();REQUIRE(sf.shop_shield);pregame_font_end();
  REQUIRE(!unlink(paths[sibling]));REQUIRE(snprintf(source,sizeof(source),"%s/%s",dir,shield_file_name(sibling))<(int)sizeof(source));REQUIRE(!symlink(source,paths[sibling]));
 }
 for(unsigned sibling=3;sibling<SHIELD_TEST_FILES;sibling++)if(sibling!=7)REQUIRE(!unlink(paths[sibling]));shield_root(temp,0,-5);shield_render_check();REQUIRE(sf.shop_shield&&!sf.metal&&!sf.shop_sprite&&!sf.shop_front&&!sf.shop_generator&&sprite_commands()==0);for(unsigned r=0;r<7;r++)REQUIRE(!sf.menu_run[r]);present_checks();pregame_font_end();
 for(unsigned i=0;i<3;i++)REQUIRE(!unlink(paths[i]));REQUIRE(!unlink(paths[7])&&!rmdir(temp));
}
static void shield_large_present_checks(const char *dir)
{
 shield_root(dir,0,4);const unsigned widths[]={640,1280,2560};Uint8 index[SF_N];memcpy(index,sf.pixels,SF_N);
 for(unsigned i=0;i<3;i++){
  unsigned w=widths[i],h=w*5/8;SDL_Surface *out=SDL_CreateRGBSurfaceWithFormat(0,w,h,32,SDL_PIXELFORMAT_RGB888);REQUIRE(out);SDL_Renderer *r=SDL_CreateSoftwareRenderer(out);REQUIRE(r);
  SDL_Texture *ref=SDL_CreateTexture(r,SDL_PIXELFORMAT_RGB888,SDL_TEXTUREACCESS_STREAMING,640,400);REQUIRE(ref);REQUIRE(!SDL_SetTextureBlendMode(ref,SDL_BLENDMODE_NONE));scaler=1;scalers[1].scaler32(VGAScreen,ref);SDL_Rect dst={0,0,w,h};
  REQUIRE(pregame_font_present(r,ref,VGAScreen,&dst,false));REQUIRE(!memcmp(index,sf.pixels,SF_N)&&replay_matches());
  /* Independent output sampler at 2x, native material density and smooth 8x.
   * Sparse shield points retain exact original nearest-neighbour underlay. */
  for(unsigned sample=0;sample<100;sample++){
   unsigned px=(112+(sample*71)%396)*w/SF_OW,py=(92+(sample*37)%92)*h/SF_OH;
   unsigned logical=(py*SF_H/h)*SF_W+px*SF_W/w;REQUIRE(!sf.metal_blocked[logical]);
   double sum[4]={0,0,0,0};
   if(w<=1280){unsigned scale=SF_OW/w;for(unsigned yy=0;yy<scale;yy++)for(unsigned xx=0;xx<scale;xx++){Uint32 v=sf.output[(py*scale+yy)*SF_OW+px*scale+xx];for(unsigned ch=0;ch<4;ch++)sum[ch]+=((v>>(ch*8))&255)/(double)(scale*scale);}}
   else {double sx=(px+0.5)*SF_OW/w-0.5,sy=(py+0.5)*SF_OH/h-0.5;unsigned x0=(unsigned)floor(sx),y0=(unsigned)floor(sy);double fx=sx-x0,fy=sy-y0;for(unsigned yy=0;yy<2;yy++)for(unsigned xx=0;xx<2;xx++){double weight=(xx?fx:1-fx)*(yy?fy:1-fy);Uint32 v=sf.output[(y0+yy)*SF_OW+x0+xx];for(unsigned ch=0;ch<4;ch++)sum[ch]+=((v>>(ch*8))&255)*weight;}}
   Uint32 base=sf.palette[sf.underlay[logical]],actual=((Uint32 *)((Uint8 *)out->pixels+py*out->pitch))[px];Uint8 rr,gg,bb;SDL_GetRGB(actual,out->format,&rr,&gg,&bb);unsigned channel[3]={bb,gg,rr};
   for(unsigned ch=0;ch<3;ch++){unsigned wanted=(unsigned)floor(sum[ch]+((base>>(ch*8))&255)*(1-sum[3]/255)+0.5);REQUIRE(channel[ch]==MIN(wanted,255u));}
  }
  pregame_font_release_texture();SDL_DestroyTexture(ref);SDL_DestroyRenderer(r);SDL_FreeSurface(out);
 }
}
int main(int argc,char **argv)
{
 REQUIRE(argc==3);REQUIRE(SDL_Init(SDL_INIT_VIDEO)==0);VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);REQUIRE(VGAScreen&&VGAScreen2);main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);REQUIRE(main_window_tex_format);
 fixtures(argv[1]);strings_fixture(argv[1]);memcpy(raw_base,VGAScreen2->pixels,SF_N);REQUIRE(hash(raw_base,SF_N)==PF_BASE&&classic_sources());test_ship=31;test_rear=16;
 fprintf(stderr,"shield math\n");shield_math_checks(argv[2]);fprintf(stderr,"shield gates\n");shield_gate_checks(argv[2]);fprintf(stderr,"shield padding\n");shield_source_padding_checks(argv[2]);fprintf(stderr,"shield fades\n");shield_fade_checks(argv[2]);fprintf(stderr,"shield occlusion\n");shield_occlusion_checks(argv[2]);fprintf(stderr,"shield parser\n");shield_parser_checks(argv[2]);fprintf(stderr,"shield independence\n");shield_independence_checks(argv[2]);fprintf(stderr,"shield large present\n");shield_large_present_checks(argv[2]);pregame_font_end();REQUIRE(!allocated&&peak_allocated<11*1024*1024);
 for(unsigned b=0;b<7;b++)for(unsigned id=0;id<sprite_table[b].count;id++)free(sprite(b,id)->data);free(shopSpriteSheet.data);SDL_FreeSurface(VGAScreen);SDL_FreeSurface(VGAScreen2);SDL_FreeFormat(main_window_tex_format);SDL_Quit();
 printf("PASS shield core: %u material states, %u parser rejections, %u checks; peak_owned=%zu; authentic INDEX8/trace unchanged; no game runs\n",material_states,parser_rejections,checks,peak_allocated);return 0;
}
