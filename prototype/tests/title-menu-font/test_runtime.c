/* Synthetic original glyphs and authored alpha/roles; uses the actual title
 * compositor plus its existing fixture. No game startup or captured artwork. */
#define TITLE_MENU_TEST_FONT
#define main classic_fixture_main
#include "../title-layers/test_runtime.c"
#undef main

static Uint8 font_rle[85][64];
static Uint8 *font_resource;
static char font_path[2048];
static struct Run { int x,y,value;char text[64]; } oracle_runs[36];
static unsigned oracle_count;
static bool portable_fade_probe;
static void check_portable(SDL_Rect dst,int w,int h);
static Uint32 oracle_output[1024000];
static const char *rows[7]={"Start New Game","Load Game","High Scores","Instructions","Setup","Demo","Quit"};
static bool blank_glyph(unsigned id)
{return id==60||(id>=63&&id<=69)||id==84;}
static void make_font(void)
{
 sprite_table[SMALL_FONT_SHAPES].count=85;
 for(unsigned id=0;id<85;id++) {
  unsigned w=2+id%3,h=3+id%2,n=0;
  for(unsigned y=0;y<h;y++) {
   if(blank_glyph(id)){font_rle[id][n++]=254;continue;}
   for(unsigned x=0;x<w;x++)font_rle[id][n++]=(id+x+y)%5==0?253:(Uint8)(3+(id+x+3*y)%13);
  }
  sprite_table[1].sprite[id]=(Sprite){(Uint16)w,(Uint16)h,(Uint16)n,font_rle[id]};
 }
}
static void write_font(const Uint8 *data,size_t size)
{FILE *f=fopen(font_path,"wb");assert(f);assert(fwrite(data,1,size,f)==size);assert(!fclose(f));}
static void font_rehash(Uint8 *data)
{put64(data+104,hash_bytes(data+128,688128));}
static void pack_font(void)
{
 font_resource=calloc(1,128+688128);assert(font_resource);memcpy(font_resource,"TMF1",4);
 const unsigned fields[15]={1,4,896,384,85,76,56,64,4,1,344064,344064,12,15,0};
 for(unsigned i=0;i<15;i++)put32(font_resource+4+4*i,fields[i]);
 const uint64_t pins[5]={TITLE_MENU_MAP_FNV,TITLE_MENU_METRICS_FNV,TITLE_MENU_ENCODED_FNV,TITLE_MENU_INK_FNV,TITLE_PAL_FNV};
 for(unsigned i=0;i<5;i++)put64(font_resource+64+8*i,pins[i]);
 for(unsigned id=0;id<85;id++)if(!blank_glyph(id)) {
  const Sprite *s=&sprite_table[1].sprite[id];
  for(unsigned y=0;y<s->height*4;y++)for(unsigned x=0;x<s->width*4;x++) {
   unsigned p=((id/16)*64+4+y)*896+(id%16)*56+4+x;
   /* Shapes deliberately differ from original logical blocks and include
    * partial coverage, holes and four authored palette roles. */
   unsigned a=(x+y+id)%7?((const unsigned[]){1,64,127,128,254,255})[(x+2*y)%6]:0;
   font_resource[128+p]=(Uint8)a;font_resource[128+344064+p]=a?(Uint8)(12+(x+3*y)%4):0;
  }
 }
 font_rehash(font_resource);write_font(font_resource,128+688128);
}
static int text_width(const char *text)
{
 int result=0;
 for(;*text;text++) {
  unsigned ch=(unsigned char)*text;
  if(ch==' ')result+=6;
  else if(ch!='~'&&font_ascii[ch]>=0)result+=get_sprite_width(1,font_ascii[ch])+1;
 }
 return result;
}
static void draw_original(int x,int y,const char *text,int alignment,int value,bool record)
{
 title_layers_menu_text_begin(VGAScreen,x,y,text,normal_font,alignment,15,(Sint8)value);
 if(alignment==centered)x-=text_width(text)/2;
 if(record){assert(oracle_count<36);oracle_runs[oracle_count]=(struct Run){x,y,value,{0}};snprintf(oracle_runs[oracle_count++].text,64,"%s",text);}
 bool highlighted=false;
 for(;*text;text++) {
  unsigned ch=(unsigned char)*text;
  if(ch==' '){x+=6;continue;}
  if(ch=='~'){highlighted=!highlighted;value+=highlighted?4:-4;continue;}
  int id=font_ascii[ch];if(id<0||id>=85)continue;
  const Sprite *s=&sprite_table[1].sprite[id];unsigned sx=0,sy=0;
  for(unsigned k=0;k<s->size;k++) {
   unsigned v=s->data[k];
   if(v==255)sx+=s->data[++k];
   else if(v==254)sx=s->width;
   else if(v==253)++sx;
   else {
    int level=(v&15)+value;if(level<0)level=0;if(level>15)level=15;
    write_pixel(1,(unsigned)x+sx,(unsigned)y+sy,(Uint8)(240+level),TITLE_WRITE_FONT);++sx;
   }
   if(sx>=s->width){sx=0;++sy;}
  }
  x+=s->width+1;
 }
 title_layers_menu_text_done();
}
static void check_menu_output(void)
{
 Uint8 original[64000],checkpoint[64000];Uint32 pal[256];
 memcpy(original,VGAScreen->pixels,64000);memcpy(checkpoint,VGAScreen2->pixels,64000);memcpy(pal,rgb_palette,sizeof(pal));
 unsigned nalloc=allocs,nread=reads,nopen=opens;
 assert(title_layers_present(renderer,VGAScreen,&destination));
 assert(allocs==nalloc&&reads==nread&&opens==nopen);
 assert(!memcmp(original,VGAScreen->pixels,64000)&&!memcmp(checkpoint,VGAScreen2->pixels,64000)&&!memcmp(pal,rgb_palette,sizeof(pal)));
 Uint8 menu_mask[64000],cursor_mask[64000];memcpy(menu_mask,plane_mask[1],64000);memcpy(cursor_mask,plane_mask[2],64000);
 memset(plane_mask[1],0,64000);memset(plane_mask[2],0,64000);
 for(unsigned y=0;y<800;y++)for(unsigned x=0;x<1280;x++)oracle_output[y*1280+x]=expected_pixel(destination.w==640?(x|1):x,destination.w==640?(y|1):y);
 memcpy(plane_mask[1],menu_mask,64000);memcpy(plane_mask[2],cursor_mask,64000);
 for(unsigned r=0;r<oracle_count;r++) {
  const struct Run *run=&oracle_runs[r];int ox=run->x,brightness=run->value;bool highlight=false;
  for(const char *text=run->text;*text;text++) {
   unsigned ch=(unsigned char)*text;
   if(ch==' '){ox+=6;continue;}
   if(ch=='~'){highlight=!highlight;brightness+=highlight?4:-4;continue;}
   int id=font_ascii[ch];assert(id>=0&&id<85);const Sprite *s=&sprite_table[1].sprite[id];
   for(unsigned y=0;y<s->height*4;y++)for(unsigned x=0;x<s->width*4;x++) {
    unsigned p=((id/16)*64+4+y)*896+(id%16)*56+4+x,a=font_resource[128+p];if(!a)continue;
    int role=font_resource[128+344064+p]+brightness;if(role<0)role=0;if(role>15)role=15;
    const SDL_Color color=engine_palette[240+role];
    unsigned pos=(run->y*4+y)*1280+ox*4+x;Uint32 dst=oracle_output[pos],result=0xff000000;
    const unsigned components[3]={color.b,color.g,color.r};
    for(unsigned k=0;k<3;k++)result|=((components[k]*a+((dst>>(8*k))&255)*(255-a)+127)/255)<<(8*k);
    oracle_output[pos]=result;
   }
   ox+=s->width+1;
  }
 }
 for(unsigned y=0;y<800;y++)for(unsigned x=0;x<1280;x++) {
  unsigned p=(y/4)*320+x/4;if(cursor_mask[p])oracle_output[y*1280+x]=palette_pixel(plane_value[2][p]);
  if(destination.w==1280)assert(state.output[y*1280+x]==oracle_output[y*1280+x]);
 }
 unsigned scale=destination.w==640?2:1;
 for(unsigned y=0;y<(unsigned)destination.h;y++)for(unsigned x=0;x<(unsigned)destination.w;x++) {
  unsigned sx=x*scale+(scale==2),sy=y*scale+(scale==2);Uint32 expected=oracle_output[sy*1280+sx];
  if(scale==2) {
   expected=UINT32_C(0xff000000);
   for(unsigned shift=0;shift<=16;shift+=8) {
    unsigned sum=0;
    for(unsigned dy=0;dy<2;dy++)for(unsigned dx=0;dx<2;dx++)sum+=(oracle_output[(y*2+dy)*1280+x*2+dx]>>shift)&255;
    expected|=((sum+2)/4)<<shift;
   }
  }
  assert(((Uint32 *)((Uint8 *)display->pixels+y*display->pitch))[x]==expected);
 }
}
static void menu_fade(bool outgoing,int steps)
{
 SDL_Color black={0,0,0,255};unsigned first=outgoing?0:240;
 title_layers_fade_start(outgoing?NULL:target_palette,outgoing?&black:NULL,first,255);
 for(int remaining=steps;remaining;--remaining) {
  for(unsigned i=first;i<256;i++) {
   SDL_Color target=outgoing?black:target_palette[i];
   engine_palette[i].r+=(int)(target.r-engine_palette[i].r)/remaining;
   engine_palette[i].g+=(int)(target.g-engine_palette[i].g)/remaining;
   engine_palette[i].b+=(int)(target.b-engine_palette[i].b)/remaining;
  }
  if(outgoing)for(unsigned i=0;i<256;i++)oracle_lut[i]+=(0-(int)oracle_lut[i])/remaining;
  apply_palette();title_layers_fade_step(remaining,first,255);
  if(!outgoing||remaining>1)check_menu_output();
  if(portable_fade_probe&&remaining==steps/2)check_portable((SDL_Rect){0,0,1920,1200},1920,1200);
 }
 if(outgoing)assert(!state.active&&!menu_font.payload&&!live_bytes);
}
static void build_menu(void)
{
 oracle_count=0;title_layers_menu_begin();
 static const int dx[5]={-1,1,1,-1,0},dy[5]={-1,1,-1,1,0};
 for(unsigned r=0;r<7;r++)for(unsigned pass=0;pass<5;pass++)draw_original(160-text_width(rows[r])/2+dx[pass],104+13*r+dy[pass],rows[r],left_aligned,pass==4?-3:-10,true);
 assert(menu_font.payload&&menu_font.runs==35);title_layers_menu_done();
 memcpy(saved_menu_value,plane_value[1],64000);memcpy(saved_menu_mask,plane_mask[1],64000);save_checkpoint(TITLE_MENU);
 assert(menu_font.count==menu_font.base_count&&menu_font.phase==TM_SAVED);menu_fade(false,20);
}
static void select_row(unsigned row,bool cursor)
{
 restore_checkpoint(TITLE_MENU);oracle_count=35;
 draw_original(160,104+13*row,rows[row],centered,-1,true);title_layers_highlight_done();
 assert(menu_font.payload&&menu_font.count>menu_font.base_count);check_menu_output();
 if(cursor) {
  Uint8 before[64000];memcpy(before,VGAScreen->pixels,64000);title_layers_cursor_begin();
  for(unsigned i=0;i<20;i++)write_pixel(2,145+i%5,104+13*row+i/5,(Uint8)(240+i%16),TITLE_WRITE_CURSOR);
  title_layers_cursor_done();check_menu_output();memcpy(VGAScreen->pixels,before,64000);title_layers_cursor_erased();memset(plane_mask[2],0,64000);check_menu_output();
 }
}
static void test_text_sequence(void)
{
 initial(false);assert(menu_font.payload);build_menu();
 for(unsigned row=0;row<7;row++)select_row(row,true);
 destination=(SDL_Rect){0,0,640,400};
 for(unsigned row=0;row<7;row++)select_row(row,true);
 destination=(SDL_Rect){0,0,1280,800};check_menu_output();
 destination=(SDL_Rect){0,0,960,600};assert(title_layers_present(renderer,VGAScreen,&destination));
 assert(menu_font.payload&&menu_font.samples[0]==0); /* portable layer is transparent outside text */
 destination=(SDL_Rect){0,0,1280,800};check_menu_output();
 title_layers_release_texture();check_menu_output();menu_fade(true,10);
 initial(false);destination=(SDL_Rect){0,0,640,400};build_menu();select_row(4,true);menu_fade(true,15);destination=(SDL_Rect){0,0,1280,800};
 /* Controls, nine blank glyph slots and their original advances remain valid. */
 rows[0]="A #*(){}[]+ ~A~";initial(false);destination=(SDL_Rect){0,0,640,400};build_menu();select_row(0,true);assert(tm_index(15,3)==255);menu_fade(true,10);destination=(SDL_Rect){0,0,1280,800};rows[0]="Start New Game";
 puts("Ordered outlines/base/selection, all seven selections, cursor erase, restart, UI/outgoing fades, blanks, tilde255 and exact2x/4x pass");
}

/* Independent ordered premultiplied-layer oracle from the observed original
 * run text, not production TmCommands or tm_render_portable. */
static void portable_layer(Uint32 *layer)
{
 memset(layer,0,1024000*4);
 for(unsigned r=0;r<oracle_count;r++) {
  const struct Run *run=&oracle_runs[r];int ox=run->x,value=run->value;bool hi=false;
  for(const char *t=run->text;*t;t++) {
   unsigned ch=(unsigned char)*t;if(ch==' '){ox+=6;continue;}
   if(ch=='~'){hi=!hi;value+=hi?4:-4;continue;}
   unsigned id=font_ascii[ch];const Sprite *g=&sprite_table[1].sprite[id];
   for(unsigned y=0;y<g->height*4;y++)for(unsigned x=0;x<g->width*4;x++) {
    unsigned p=((id/16)*64+4+y)*896+(id%16)*56+4+x,a=font_resource[128+p];
    int role=font_resource[128+344064+p]+value;if(role<0)role=0;if(role>15)role=15;
    const SDL_Color c=engine_palette[240+role];unsigned channels[4]={c.b,c.g,c.r,255};
    unsigned out=(run->y*4+y)*1280+ox*4+x;Uint32 old=layer[out],v=0;
    for(unsigned k=0;k<4;k++)v|=((channels[k]*a+((old>>(k*8))&255)*(255-a)+127)/255)<<(k*8);
    layer[out]=v;
   }
   ox+=g->width+1;
  }
 }
}
static Uint32 portable_sample(const Uint32 *layer,int px,int py,Uint32 base)
{
 long double l=(long double)(px-destination.x)*1280/destination.w;
 long double r=(long double)(px+1-destination.x)*1280/destination.w;
 long double t=(long double)(py-destination.y)*800/destination.h;
 long double b=(long double)(py+1-destination.y)*800/destination.h;
 bool mx=destination.w>1280,my=destination.h>800;long double fx=0,fy=0;
 if(mx){long double center=(l+r)/2-0.5L;l=floorl(center);fx=center-l;r=l+2;}
 if(my){long double center=(t+b)/2-0.5L;t=floorl(center);fy=center-t;b=t+2;}
 long double area=(mx?1:r-l)*(my?1:b-t),sum[4]={0,0,0,0};
 for(int y=MAX(0,(int)floorl(t));y<MIN(800,(int)ceill(b));y++)for(int x=MAX(0,(int)floorl(l));x<MIN(1280,(int)ceill(r));x++) {
  long double weight=(mx?(x==l?1-fx:fx):fminl(r,x+1)-fmaxl(l,x))*(my?(y==t?1-fy:fy):fminl(b,y+1)-fmaxl(t,y));
  Uint32 v=layer[y*1280+x];for(unsigned c=0;c<4;c++)sum[c]+=((v>>(8*c))&255)*weight;
 }
 if(sum[3]==0)return base;
 Uint32 result=0xff000000;
 for(unsigned c=0;c<3;c++)result|=(unsigned)fminl(255,fmaxl(0,floorl(sum[c]/area+((base>>(c*8))&255)*(1-sum[3]/(255*area))+0.5L)))<<(c*8);
 return result;
}
static void portable_display(int w,int h)
{
 title_layers_release_texture();SDL_DestroyRenderer(renderer);SDL_FreeSurface(display);
 display=SDL_CreateRGBSurfaceWithFormat(0,w,h,32,SDL_PIXELFORMAT_ARGB8888);assert(display);
 renderer=SDL_CreateSoftwareRenderer(display);assert(renderer);
}
static void check_portable(SDL_Rect dst,int w,int h)
{
 portable_display(w,h);destination=dst;
 Uint32 *layer=malloc(1024000*4),*actual=malloc((size_t)w*h*4),*base=malloc((size_t)w*h*4);assert(layer&&actual&&base);
 portable_layer(layer);
 Uint8 old_menu[64000],old_cursor[64000],indexed[64000],backup[64000];Uint32 palette[256];
 memcpy(old_menu,plane_mask[1],64000);memcpy(old_cursor,plane_mask[2],64000);
 memset(plane_mask[1],0,64000);memset(plane_mask[2],0,64000);
 for(unsigned y=0;y<800;y++)for(unsigned x=0;x<1280;x++)oracle_output[y*1280+x]=expected_pixel(x,y);
 memcpy(plane_mask[1],old_menu,64000);memcpy(plane_mask[2],old_cursor,64000);
 SDL_Texture *tex=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,1280,800);assert(tex);
 assert(!SDL_SetTextureScaleMode(tex,SDL_ScaleModeNearest));assert(!SDL_SetTextureBlendMode(tex,SDL_BLENDMODE_NONE));
 assert(!SDL_UpdateTexture(tex,NULL,oracle_output,1280*4));assert(!SDL_SetRenderDrawColor(renderer,0,0,0,255));assert(!SDL_RenderClear(renderer));assert(!SDL_RenderCopy(renderer,tex,NULL,&destination));
 assert(!SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,base,w*4));
 memcpy(indexed,VGAScreen->pixels,64000);memcpy(backup,VGAScreen2->pixels,64000);memcpy(palette,rgb_palette,1024);
 unsigned na=allocs,nr=reads,no=opens;assert(title_layers_present(renderer,VGAScreen,&destination));assert(na==allocs&&nr==reads&&no==opens);
 assert(!memcmp(indexed,VGAScreen->pixels,64000)&&!memcmp(backup,VGAScreen2->pixels,64000)&&!memcmp(palette,rgb_palette,1024));
 assert(!memcmp(layer,menu_font.samples,1024000*4));assert(!SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,actual,w*4));
 for(int y=0;y<h;y++)for(int x=0;x<w;x++)base[y*w+x]=portable_sample(layer,x,y,base[y*w+x]);
 SDL_Texture *expected=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,w,h);assert(expected);
 assert(!SDL_UpdateTexture(expected,NULL,base,w*4));assert(!SDL_RenderCopy(renderer,expected,NULL,NULL));
 memset(oracle_output,0,sizeof(oracle_output));
 for(unsigned y=0;y<800;y++)for(unsigned x=0;x<1280;x++){unsigned p=(y/4)*320+x/4;if(old_cursor[p])oracle_output[y*1280+x]=palette_pixel(plane_value[2][p]);}
 assert(!SDL_UpdateTexture(tex,NULL,oracle_output,1280*4));assert(!SDL_SetTextureBlendMode(tex,SDL_BLENDMODE_BLEND));assert(!SDL_RenderCopy(renderer,tex,NULL,&destination));
 assert(!SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,base,w*4));
 unsigned changed=0;
 for(int y=0;y<h;y++)for(int x=0;x<w;x++)for(unsigned c=0;c<3;c++){
  int d=(int)((actual[y*w+x]>>(c*8))&255)-(int)((base[y*w+x]>>(c*8))&255);
  if(abs(d)>1){fprintf(stderr,"portable oracle %dx%d at%d,%d c%u actual%08x expected%08x\n",w,h,x,y,c,actual[y*w+x],base[y*w+x]);abort();}changed+=d!=0;
 }
 assert(changed<(unsigned)(w*h));
 SDL_DestroyTexture(tex);SDL_DestroyTexture(expected);free(layer);free(actual);free(base);
 portable_display(1280,800);destination=(SDL_Rect){0,0,1280,800};
}
static void test_portable(void)
{
 const SDL_Rect rects[]={{0,0,1920,1200},{171,0,1023,767},{8,5,977,603}};
 const int sizes[][2]={{1920,1200},{1365,767},{997,613}};
 initial(false);portable_fade_probe=true;build_menu();
 for(unsigned k=0;k<3;k++) {
  select_row(k*3,false);check_portable(rects[k],sizes[k][0],sizes[k][1]);
  Uint8 before[64000];memcpy(before,VGAScreen->pixels,64000);title_layers_cursor_begin();
  for(unsigned i=0;i<24;i++)if(i%3)write_pixel(2,145+i%6,104+13*k*3+i/6,(Uint8)(240+i%16),TITLE_WRITE_CURSOR);
  title_layers_cursor_done();check_portable(rects[k],sizes[k][0],sizes[k][1]);
  memcpy(VGAScreen->pixels,before,64000);title_layers_cursor_erased();memset(plane_mask[2],0,64000);
  check_menu_output();
 }
 menu_fade(true,10);portable_fade_probe=false;assert(!live_bytes&&!gpu_live_bytes);
 title_layers_end();puts("Portable UI/outgoing fades,1920x1200, odd letterbox and anisotropic reduction: ordered independent layer/output oracle, exact indexed/palette state, sparse cursor holes and renderer recreation pass");
}
static void test_font_loader(void)
{
 Uint8 *bad=malloc(128+688128+1);assert(bad);
 for(unsigned byte=0;byte<128;byte++) {
  memcpy(bad,font_resource,128+688128);bad[byte]^=1;write_font(bad,128+688128);tm_load(directory);assert(!menu_font.payload);
 }
 const size_t lengths[]={0,3,127,128,128+688128-1,128+688128+1};
 for(unsigned i=0;i<6;i++){memcpy(bad,font_resource,128+688128);write_font(bad,lengths[i]);tm_load(directory);assert(!menu_font.payload);}
 unsigned points[]={0,4*896+4,4*896+4+2*4,((60/16)*64+4)*896+(60%16)*56+4,((85/16)*64+4)*896+(85%16)*56+4};
 for(unsigned i=0;i<5;i++) {
  memcpy(bad,font_resource,128+688128);bad[128+points[i]]=255;bad[128+344064+points[i]]=i==1?11:13;font_rehash(bad);write_font(bad,128+688128);tm_load(directory);assert(!menu_font.payload);
 }
 memcpy(bad,font_resource,128+688128);bad[128]=0;bad[128+344064]=13;font_rehash(bad);write_font(bad,128+688128);tm_load(directory);assert(!menu_font.payload);
 memcpy(bad,font_resource,128+688128);bad[128+4*896+4]^=1;write_font(bad,128+688128);tm_load(directory);assert(!menu_font.payload);
 assert(!unlink(font_path));assert(!mkdir(font_path,0700));tm_load(directory);assert(!menu_font.payload);assert(!rmdir(font_path));
 assert(!mkfifo(font_path,0600));tm_load(directory);assert(!menu_font.payload);assert(!unlink(font_path));
 write_font(font_resource,128+688128);
 for(unsigned mode=0;mode<8;mode++) {
  reset_faults();if(mode==0)fail_open=1;if(mode==1)fail_stat=1;if(mode==2)fail_read=1;if(mode==3)fail_read=2;if(mode==4)short_read=2;if(mode==5)fail_alloc=1;if(mode==6)fail_close=1;if(mode==7)fail_alloc=2;
  tm_load(directory);assert(!menu_font.payload);
 }
 reset_faults();free(bad);puts("TMF1 every header byte, lengths/hash, roles/padding/blank/unused, regular files, bounded I/O and allocation failures pass");
}
static void test_fallback(void)
{
 /* Missing font, corrupt font, source mismatch and allocator failure do not
  * retire title art. The unchanged classic plane remains authoritative. */
 assert(!unlink(font_path));initial(false);assert(state.active&&!menu_font.payload);menu();live_cursor(104*320+160,true);title_layers_end();
 write_font(font_resource,128+688128);font_rle[0][0]^=1;initial(false);assert(state.active&&!menu_font.payload);menu();check_present(true);title_layers_end();font_rle[0][0]^=1;
 initial(false);build_menu();select_row(2,false);title_layers_sprite_table_reset(SMALL_FONT_SHAPES);assert(state.active&&!menu_font.payload);check_present(true);title_layers_end();
 initial(false);build_menu();select_row(1,false);font_rle[1][1]^=1;assert(tl_check()&&state.active&&!menu_font.payload);check_present(true);font_rle[1][1]^=1;title_layers_end();
 const char *bad_text[]={"A=","A&","A\200"};
 for(unsigned i=0;i<3;i++) {initial(false);title_layers_menu_begin();draw_original(159,103,bad_text[i],left_aligned,-10,false);assert(state.active&&!menu_font.payload);title_layers_end();}
 initial(false);title_layers_menu_begin();title_layers_menu_text_begin(VGAScreen,159,103,"A",normal_font,left_aligned,15,-10);assert(state.active&&!menu_font.payload);title_layers_end();
 initial(false);title_layers_menu_begin();int x=160-text_width(rows[0])/2;
 title_layers_menu_text_begin(VGAScreen,x-1,103,rows[0],normal_font,left_aligned,15,-10);title_layers_menu_text_done();assert(state.active&&!menu_font.payload);title_layers_end();
 initial(false);title_layers_menu_begin();write_pixel(1,100,104,250,TITLE_WRITE_FONT);assert(state.active&&!menu_font.payload);title_layers_end();
 initial(false);title_layers_menu_begin();title_layers_menu_text_begin(VGAScreen,x-1,103,rows[0],normal_font,left_aligned,15,-10);write_pixel(1,100,104,250,TITLE_WRITE_FONT);assert(state.active&&!menu_font.payload);title_layers_end();
 initial(false);title_layers_menu_begin();title_layers_menu_done();assert(state.active&&!menu_font.payload);title_layers_end();
 for(int failed=5;failed<=6;failed++) {
  begin_epoch(false);title_layers_end();reset_faults();fail_alloc=failed;title_layers_begin(VGAScreen,target_palette,false);
  assert(state.active&&!menu_font.payload&&!menu_font.samples&&live_bytes==expected_cpu(7));title_layers_end();reset_faults();
 }
 puts("Whole-menu fallback retains valid title art for missing font, source/reload/protocol mismatch, unsupported runs and allocation failure");
}
int main(int argc,char **argv)
{
 setvbuf(stdout,NULL,_IOLBF,0);assert(argc==2);directory=argv[1];assert(!SDL_Init(0));
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);assert(VGAScreen&&VGAScreen2);
 main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);assert(main_window_tex_format);
 display=SDL_CreateRGBSurfaceWithFormat(0,1280,800,32,SDL_PIXELFORMAT_ARGB8888);assert(display);renderer=SDL_CreateSoftwareRenderer(display);assert(renderer);
 for(unsigned i=0;i<64000;i++)pic_source[i]=(Uint8)((i*7)%239);
 for(unsigned i=0;i<256;i++)target_palette[i]=(SDL_Color){(Uint8)(i*3),(Uint8)(i*7),(Uint8)(i*13),255};
 sprite_table[PLANET_SHAPES].count=152;make_fixture(0);make_fixture(1);make_font();
 for(unsigned k=0;k<3;k++){snprintf(paths[k],sizeof(paths[k]),"%s/%s",directory,names[k]);pack_resource(k);}
 snprintf(font_path,sizeof(font_path),"%s/title-menu-font-v1.hda",directory);pack_font();title_layers_set_directory(directory);
 test_text_sequence();test_portable();test_font_loader();test_fallback();title_layers_end();assert(!live_bytes&&!gpu_live_bytes);
 printf("TMF1 fixed state=%zu; optional payload=%u; sampler scratch=%u; combined title dynamic peak=%zu; presentations=%u; allocation ledger empty\n",sizeof(menu_font),TM_PAYLOAD,TM_SAMPLE_BYTES,peak_bytes,presents);
 for(unsigned k=0;k<3;k++)free(resources[k]);
 free(font_resource);
 SDL_DestroyRenderer(renderer);SDL_FreeSurface(display);SDL_FreeSurface(VGAScreen);SDL_FreeSurface(VGAScreen2);SDL_FreeFormat(main_window_tex_format);SDL_Quit();
 puts("TMF1 production-module synthetic suite passed");return 0;
}
