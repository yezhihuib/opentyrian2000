/* Source/core-only test. Reads local original data; never distributes it. */
#define _POSIX_C_SOURCE 200809L
#include <stdlib.h>
#include <limits.h>
static unsigned allocation_calls,fail_allocation=UINT_MAX;
static size_t allocated,peak_allocated;
static struct {void *p;size_t size;} allocations[4];
static void *lease_malloc(size_t n){if(allocation_calls++==fail_allocation)return NULL;void *p=malloc(n);if(p){unsigned i=0;while(i<4&&allocations[i].p)i++;if(i==4)abort();allocations[i].p=p;allocations[i].size=n;allocated+=n;if(allocated>peak_allocated)peak_allocated=allocated;}return p;}
static void lease_free(void *p){if(p){unsigned i=0;while(i<4&&allocations[i].p!=p)i++;if(i==4)abort();allocated-=allocations[i].size;allocations[i].p=NULL;free(p);}}
#define malloc lease_malloc
#define free lease_free
#include <assert.h>
#include <sys/stat.h>
#include <unistd.h>
#include "../src/settings_font.c"
#undef malloc
#undef free
#include "../src/nortvars.h"
#include "../src/vga256d.h"
#include "../src/title_layers.h"
SDL_Surface *VGAScreen,*VGAScreenSeg,*VGAScreen2,*game_screen;
SDL_Window *main_window;SDL_PixelFormat *main_window_tex_format;
Palette palettes[24],colors;int palette_count=24;
Uint32 rgb_palette[256],yuv_palette[256];
uint scaler=1;ScalingMode scaling_mode=SCALE_INTEGER;
static unsigned checks,states,max_commands;
void render_mirror_pixel(SDL_Surface *s,Uint8 *p,Uint8 color,int style){(void)color;settings_font_pixel(s,p,style);}
void render_mirror_rect(SDL_Surface *s,const SDL_Rect *r){settings_font_rect(s,r);}
void render_mirror_text_glyph_begin(SDL_Surface *s,int x,int y,unsigned t,unsigned id,bool black,unsigned hue,int value){(void)s;(void)x;(void)y;(void)t;(void)id;(void)black;(void)hue;(void)value;}
void render_mirror_text_glyph_end(void){}
void title_layers_pixel(SDL_Surface *s,Uint8 *p,enum TitleWriter w){(void)s;(void)p;(void)w;}
void render_mirror_unsupported(const char *s){(void)s;}
void asset_debug_effect(SDL_Surface *s,Sprite2_array a,unsigned id,int x,int y){(void)s;(void)a;(void)id;(void)x;(void)y;}

#define REQUIRE(expr) do { ++checks;if(!(expr)){fprintf(stderr,"FAIL %s:%d: %s (stage=%d role=%u row=%u cmd=%u/%u pixel=%u active=%d frame=%d)\n",__FILE__,__LINE__,#expr,sf.stage,sf.next_role,sf.row,sf.next,sf.limit,sf.pixel,sf.active,sf.frame);abort();} } while(0)
static unsigned rd16(FILE *f){unsigned a=fgetc(f),b=fgetc(f);return a|(b<<8);}
static unsigned rd32(FILE *f){unsigned a=rd16(f),b=rd16(f);return a|(b<<16);}
static FILE *open_data(const char *d,const char *n){char p[1024];snprintf(p,sizeof(p),"%s/%s",d,n);FILE *f=fopen(p,"rb");REQUIRE(f);return f;}
static void fixtures(const char *d)
{
 FILE *f=open_data(d,"newsh1.shp");fseek(f,0,SEEK_END);shopSpriteSheet.size=ftell(f);rewind(f);shopSpriteSheet.data=malloc(shopSpriteSheet.size);REQUIRE(fread(shopSpriteSheet.data,1,shopSpriteSheet.size,f)==shopSpriteSheet.size);fclose(f);
 f=open_data(d,"tyrian.shp");unsigned n=rd16(f),offset[32];REQUIRE(n<32);for(unsigned i=0;i<n;i++)offset[i]=rd32(f);
 for(unsigned b=0;b<3;b++){fseek(f,offset[b],SEEK_SET);sprite_table[b].count=rd16(f);for(unsigned id=0;id<sprite_table[b].count;id++){REQUIRE(fgetc(f)==1);Sprite *s=sprite(b,id);s->width=rd16(f);s->height=rd16(f);s->size=rd16(f);s->data=malloc(s->size);REQUIRE(s->data&&fread(s->data,1,s->size,f)==s->size);}}fclose(f);
 f=open_data(d,"palette.dat");for(unsigned p=0;p<24;p++)for(unsigned i=0;i<256;i++){unsigned r=fgetc(f),g=fgetc(f),b=fgetc(f);palettes[p][i]=(SDL_Color){r*4+(r>>4),g*4+(g>>4),b*4+(b>>4),255};}fclose(f);memcpy(colors,palettes[7],sizeof(colors));
 f=open_data(d,"tyrian.pic");n=rd16(f);REQUIRE(n<32);for(unsigned i=0;i<n;i++)offset[i]=rd32(f);fseek(f,offset[1],SEEK_SET);unsigned p=0;while(p<SF_N){unsigned v=fgetc(f),count=1;if((v&192)==192){count=v&63;v=fgetc(f);}REQUIRE(p+count<=SF_N);memset((Uint8 *)VGAScreen2->pixels+p,v,count);p+=count;}fclose(f);memset((Uint8 *)VGAScreen2->pixels+192*320,0,8*320);
}
static void live_palette(const SDL_Color *p){for(unsigned i=0;i<256;i++)rgb_palette[i]=SDL_MapRGB(main_window_tex_format,p[i].r,p[i].g,p[i].b);}
static void acquire(const char *directory)
{settings_font_set_directory(directory);memset(rgb_palette,0,sizeof(rgb_palette));settings_font_begin(VGAScreen,VGAScreen2);REQUIRE(sf.active);}
static void text_run(unsigned role,unsigned row,int x,int y,const char *text,unsigned bank,int alignment,int value)
{
 settings_font_run_begin(role,row,VGAScreen,x,y,text,bank,alignment,15,value);REQUIRE(sf.frame);
 if(bank==2)JE_textShade(VGAScreen,x,y,text,15,value,PART_SHADE);else draw_font_hv_shadow(VGAScreen,x,y,text,bank,alignment,15,value,false,2);
 settings_font_run_end();REQUIRE(sf.frame);
}
static void bar(unsigned row,unsigned color,unsigned amount)
{
 settings_font_bar_begin(row,color,amount);REQUIRE(sf.frame);int y=37+21*row;
 JE_barDrawShadow(VGAScreen,180,y,1,color,amount,2,10);JE_rectangle(VGAScreen,178,y-2,276,y+11,242);settings_font_primitive_end();REQUIRE(sf.frame);
}
static const char *value(unsigned kind,unsigned item,char buf[20])
{if(kind==1){if(!item)return "Window";snprintf(buf,20,"Display %u",item);return buf;}return kind==2?scaler_names[item]:mode_names[item];}
static void frame(unsigned menu,unsigned selected,unsigned picker,unsigned count,unsigned picksel,unsigned volume)
{
 memcpy(VGAScreen->pixels,VGAScreen2->pixels,SF_N);settings_font_frame_begin(menu,selected,picker);REQUIRE(sf.frame);
 text_run(SETTINGS_HEADING,0,160,4,headings[menu-1],0,centered,-3);
 for(unsigned row=0;row<(menu==3?3u:4u);row++){
  int v=row==selected?-1:picker?-7:-3;int y=37+21*row;text_run(SETTINGS_LABEL,row,45,y,labels[menu-1][row],1,left_aligned,v);
  if(menu==2&&row<3){char buf[20];text_run(SETTINGS_VALUE,row,180,y,value(row+1,row==0?count-1:row==1?7:1,buf),1,left_aligned,v);}
  if(menu==3&&row<2)bar(row,row?170:174,volume);
 }
 text_run(SETTINGS_FOOTER,selected,45,190,footers[menu-1][selected],2,left_aligned,4);
 if(picker){int h=15*count-2,y=37+21*selected;if(y>183-h)y=183-h;settings_font_picker_begin(count,picksel,y);REQUIRE(sf.frame);JE_rectangle(VGAScreen,175,y-3,279,y+h+2,248);JE_rectangle(VGAScreen,176,y-4,278,y+h+3,250);JE_rectangle(VGAScreen,177,y-5,277,y+h+4,248);fill_rectangle_wh(VGAScreen,178,y-2,99,h+4,224);settings_font_primitive_end();REQUIRE(sf.frame);for(unsigned row=0;row<count;row++){char buf[20];text_run(SETTINGS_PICKER,row,180,y+15*row,value(picker,row,buf),1,left_aligned,row==picksel?-1:-3);}}
 settings_font_frame_end();REQUIRE(sf.frame&&sf.stage==S_READY);if(sf.count>max_commands)max_commands=sf.count;states++;
}
static int original_role(unsigned bank,unsigned id,unsigned tx,unsigned ty)
{
 const Sprite *s=sprite(bank,id);unsigned x=0,y=0;
 for(unsigned k=0;k<s->size;k++){unsigned v=s->data[k];if(v==255)x+=s->data[++k];else if(v==254)x=s->width;else if(v==253)x++;else{if(x==tx&&y==ty)return v&15;x++;}if(x==s->width){x=0;y++;}}
 return -1;
}
static Uint32 oracle_sample(unsigned x,unsigned y)
{
 unsigned p=(y/4)*320+x/4;Uint8 index=sf.base[p];Uint32 color=sf.palette[index];
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];if(x<c->x*4u||x>=(c->x+c->w)*4u||y<c->y*4u||y>=(c->y+c->h)*4u)continue;
  if(c->kind>=C_SOLID){index=c->kind==C_SOLID?(Uint8)c->value:(index&240)|((index&15)>>1);color=sf.palette[index];continue;}
  unsigned gx=x-c->x*4u,gy=y-c->y*4u;const struct SfSpec *sp=&spec[c->bank];unsigned off=((c->id/16)*sp->ch+4+gy)*sp->aw+(c->id%16)*sp->cw+4+gx;unsigned a=sf.payload[c->bank][off];
  unsigned role=c->bank==2?7:sf.payload[c->bank][sp->plane+off];int tone=(int)role+c->value;if(tone<0)tone=0;if(tone>15)tone=15;
  Uint8 ink=c->kind==C_DARK?(index&240)|((index&15)>>1):c->kind==C_BLACK?0:240|tone;Uint32 fg=sf.palette[ink],next=0xff000000;
  for(unsigned ch=0;ch<3;ch++){unsigned sh=ch*8;next|=((((fg>>sh)&255)*a+((color>>sh)&255)*(255-a)+127)/255)<<sh;}color=next;
  int original=original_role(c->bank,c->id,gx/4,gy/4);if(original>=0){tone=original+c->value;if(tone<0)tone=0;if(tone>15)tone=15;index=c->kind==C_DARK?(index&240)|((index&15)>>1):c->kind==C_BLACK?0:240|tone;}
 }
 return sf.cursor_mask[p]?sf.palette[sf.cursor_index[p]]:color;
}
static void render_checks(void)
{
 render();REQUIRE(!memcmp(sf.replay,sf.expected,SF_N));
 for(unsigned n=0;n<128;n++){unsigned x=(n*137+states*17)%1280,y=(n*79+states*29)%800;REQUIRE(sf.output[y*1280+x]==oracle_sample(x,y));}
 for(unsigned p=0;p<SF_N;p++)if(!sf.owner[p])for(unsigned dy=0;dy<4;dy++)for(unsigned dx=0;dx<4;dx++)REQUIRE(sf.output[((p/320)*4+dy)*1280+(p%320)*4+dx]==sf.palette[sf.expected[p]]);
 Uint32 pair_oracle[32];unsigned pair_x[32],pair_y[32];for(unsigned n=0;n<32;n++){unsigned x=(n*97+states*31)%640,y=(n*47+states*13)%400;pair_x[n]=x;pair_y[n]=y;Uint32 v=0xff000000,q[4]={oracle_sample(2*x,2*y),oracle_sample(2*x+1,2*y),oracle_sample(2*x,2*y+1),oracle_sample(2*x+1,2*y+1)};for(unsigned sh=0;sh<=16;sh+=8)v|=((((q[0]>>sh)&255)+((q[1]>>sh)&255)+((q[2]>>sh)&255)+((q[3]>>sh)&255)+2)/4)<<sh;pair_oracle[n]=v;}
 Uint32 expected[640];for(unsigned x=0;x<640;x++){Uint32 v=0xff000000;for(unsigned sh=0;sh<=16;sh+=8){unsigned p=2*x;unsigned sum=((sf.output[p]>>sh)&255)+((sf.output[p+1]>>sh)&255)+((sf.output[p+1280]>>sh)&255)+((sf.output[p+1281]>>sh)&255);v|=((sum+2)/4)<<sh;}expected[x]=v;}reduce2();REQUIRE(!memcmp(expected,sf.output,sizeof(expected)));for(unsigned n=0;n<32;n++)REQUIRE(sf.output[pair_y[n]*640+pair_x[n]]==pair_oracle[n]);
}
static void write_bytes(const char *path,const Uint8 *p,size_t n)
{FILE *f=fopen(path,"wb");REQUIRE(f);REQUIRE(fwrite(p,1,n,f)==n);REQUIRE(!fclose(f));}
static void failed_acquire(const char *d)
{
 Uint8 before[SF_N];memcpy(before,VGAScreen->pixels,SF_N);settings_font_set_directory(d);settings_font_begin(VGAScreen,VGAScreen2);REQUIRE(!sf.active&&!sf.output&&allocated==0);REQUIRE(!memcmp(before,VGAScreen->pixels,SF_N));
}
static void resource_failures(const char *d)
{
 char temp[]="/tmp/settings-font-test-XXXXXX";REQUIRE(mkdtemp(temp));char paths[3][1024];Uint8 *files[3];size_t sizes[3];
 settings_font_end();
 for(unsigned b=0;b<3;b++){char in[1024];snprintf(in,sizeof(in),"%s/settings-font-%s-v1.hda",d,spec[b].name);FILE *f=fopen(in,"rb");REQUIRE(f);sizes[b]=128+spec[b].plane*(spec[b].mode?2:1);files[b]=malloc(sizes[b]+1);REQUIRE(files[b]&&fread(files[b],1,sizes[b],f)==sizes[b]);fclose(f);snprintf(paths[b],sizeof(paths[b]),"%s/settings-font-%s-v1.hda",temp,spec[b].name);write_bytes(paths[b],files[b],sizes[b]);}
 for(unsigned b=0;b<3;b++){
  for(unsigned offset=0;offset<128;offset+=4){files[b][offset]^=128;write_bytes(paths[b],files[b],sizes[b]);failed_acquire(temp);files[b][offset]^=128;}
  const size_t lengths[]={0,127,sizes[b]-1,sizes[b]+1};for(unsigned i=0;i<4;i++){write_bytes(paths[b],files[b],lengths[i]);failed_acquire(temp);}
  files[b][128]^=1;write_bytes(paths[b],files[b],sizes[b]);failed_acquire(temp);files[b][128]^=1;
  REQUIRE(!unlink(paths[b]));failed_acquire(temp);REQUIRE(!mkdir(paths[b],0700));failed_acquire(temp);REQUIRE(!rmdir(paths[b]));REQUIRE(!mkfifo(paths[b],0600));failed_acquire(temp);REQUIRE(!unlink(paths[b]));write_bytes(paths[b],files[b],sizes[b]);
 }
 for(unsigned i=0;i<4;i++){settings_font_end();fail_allocation=allocation_calls+i;settings_font_set_directory(temp);settings_font_begin(VGAScreen,VGAScreen2);REQUIRE(!sf.active&&allocated==0);fail_allocation=UINT_MAX;}
 acquire(temp);for(unsigned b=0;b<3;b++){
  Uint8 *p=sf.payload[b];Uint8 old=p[0];p[0]=255;REQUIRE(!padding(b,p));p[0]=old;
  if(spec[b].mode){p[spec[b].plane]=12;REQUIRE(!padding(b,p));p[spec[b].plane]=0;unsigned ink=0;while(!p[ink])ink++;old=p[spec[b].plane+ink];p[spec[b].plane+ink]=11;REQUIRE(!padding(b,p));p[spec[b].plane+ink]=old;}
  REQUIRE(padding(b,p));
 }
 settings_font_end();for(unsigned b=0;b<3;b++){REQUIRE(!unlink(paths[b]));free(files[b]);}REQUIRE(!rmdir(temp));
}
static void begin_simple(void)
{memcpy(VGAScreen->pixels,VGAScreen2->pixels,SF_N);settings_font_frame_begin(1,0,0);REQUIRE(sf.frame);}
static void observer_failures(const char *d)
{
 acquire(d);begin_simple();settings_font_run_begin(SETTINGS_HEADING,0,VGAScreen,160,4,"Settings",0,centered,15,-3);REQUIRE(!sf.frame&&sf.active);
 begin_simple();settings_font_run_begin(SETTINGS_HEADING,0,VGAScreen,160,4,"Setup",1,centered,15,-3);REQUIRE(!sf.frame);
 begin_simple();settings_font_run_begin(SETTINGS_HEADING,0,VGAScreen,160,4,"Setup",0,centered,15,-3);settings_font_run_end();REQUIRE(!sf.frame);
 begin_simple();settings_font_run_begin(SETTINGS_HEADING,0,VGAScreen,160,4,"Setup",0,centered,15,-3);struct SfCommand c=sf.commands[sf.next];settings_font_glyph_begin(VGAScreen,c.x,c.y,c.bank,c.id,SETTINGS_FACE,15,-3);REQUIRE(!sf.frame);
 begin_simple();settings_font_run_begin(SETTINGS_HEADING,0,VGAScreen,160,4,"Setup",0,centered,15,-3);c=sf.commands[sf.next];sf.owner[c.y*320+c.x]=1;settings_font_glyph_begin(VGAScreen,c.x,c.y,c.bank,c.id,SETTINGS_DARK,0,0);REQUIRE(!sf.frame);
 frame(1,0,0,2,0,0);settings_font_pixel(VGAScreen,(Uint8 *)VGAScreen->pixels+10,0);REQUIRE(!sf.frame); /* same-index unknown writer */
 frame(1,0,0,2,0,0);((Uint8 *)VGAScreen->pixels)[100]^=1;settings_font_cursor_begin();REQUIRE(!sf.frame);
 frame(1,0,0,2,0,0);settings_font_cursor_begin();settings_font_pixel(VGAScreen,(Uint8 *)VGAScreen->pixels+10,0);REQUIRE(!sf.frame); /* unknown cursor writer */
 frame(1,0,0,2,0,0);settings_font_cursor_begin();settings_font_cursor_done();((Uint8 *)VGAScreen->pixels)[100]^=1;settings_font_cursor_erased();REQUIRE(!sf.frame);
 begin_simple();sf.count=SF_COMMANDS;settings_font_run_begin(SETTINGS_HEADING,0,VGAScreen,160,4,"Setup",0,centered,15,-3);REQUIRE(!sf.frame);
 begin_simple();sf.next_role=100;sf.picker=1;settings_font_picker_begin(13,0,0);REQUIRE(!sf.frame);
 begin_simple();Sprite *g=sprite(1,0);Uint16 width=g->width;g->width++;settings_font_frame_end();REQUIRE(!sf.active);g->width=width;
 acquire(d);begin_simple();g=sprite(2,0);Uint8 v=g->data[0];g->data[0]^=1;settings_font_frame_end();REQUIRE(!sf.active);g->data[0]=v;
 acquire(d);begin_simple();g=sprite(0,0);Uint8 *original=g->data,*copy=malloc(g->size);memcpy(copy,original,g->size);g->data=copy;settings_font_frame_end();REQUIRE(!sf.active);g->data=original;free(copy);
 acquire(d);begin_simple();Uint8 r=palettes[7][0].r;palettes[7][0].r^=1;settings_font_frame_end();REQUIRE(!sf.active);palettes[7][0].r=r;
 acquire(d);begin_simple();((Uint8 *)VGAScreen2->pixels)[0]^=1;settings_font_frame_end();REQUIRE(!sf.active);((Uint8 *)VGAScreen2->pixels)[0]^=1;
 acquire(d);begin_simple();int pitch=VGAScreen->pitch;VGAScreen->pitch++;settings_font_frame_end();REQUIRE(!sf.active);VGAScreen->pitch=pitch;
 acquire(d);frame(1,0,0,2,0,0);settings_font_fade_start(palettes[7],NULL,1,255);REQUIRE(!sf.active);
 acquire(d);frame(1,0,0,2,0,0);settings_font_fade_start(palettes[7],NULL,0,255);settings_font_fade_step(9,0,255);REQUIRE(!sf.active);
}
static void renderer_lifecycle(const char *d)
{
 acquire(d);sf.initial_done=true;memcpy(sf.expected_palette,palettes[7],sizeof(colors));live_palette(palettes[7]);
 SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,640,400,32,SDL_PIXELFORMAT_ARGB8888);SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(target);REQUIRE(target&&renderer);SDL_Rect destination={0,0,640,400};
 frame(2,0,1,12,11,0);unsigned allocations_before=allocation_calls;REQUIRE(settings_font_present(renderer,VGAScreen,&destination,false));REQUIRE(allocation_calls==allocations_before&&sf.texture);
 REQUIRE(!settings_font_present(renderer,VGAScreen,&destination,true));REQUIRE(!sf.frame&&!sf.texture);frame(1,0,0,2,0,0);REQUIRE(settings_font_present(renderer,VGAScreen,&destination,false));
 settings_font_invalidate();REQUIRE(!sf.frame&&!sf.texture);SDL_DestroyRenderer(renderer);SDL_FreeSurface(target);
 target=SDL_CreateRGBSurfaceWithFormat(0,1280,800,32,SDL_PIXELFORMAT_ARGB8888);renderer=SDL_CreateSoftwareRenderer(target);REQUIRE(target&&renderer);destination.w=1280;destination.h=800;scaler=7;frame(2,1,2,9,7,0);REQUIRE(settings_font_present(renderer,VGAScreen,&destination,false));
 scaler=2;REQUIRE(!settings_font_present(renderer,VGAScreen,&destination,false));REQUIRE(!sf.frame);scaler=7;frame(1,0,0,2,0,0);SDL_RenderSetLogicalSize(renderer,640,400);REQUIRE(!settings_font_present(renderer,VGAScreen,&destination,false));SDL_RenderSetLogicalSize(renderer,0,0);
 frame(1,0,0,2,0,0);SDL_RenderSetScale(renderer,2,2);REQUIRE(!settings_font_present(renderer,VGAScreen,&destination,false));SDL_RenderSetScale(renderer,1,1);
 frame(1,0,0,2,0,0);SDL_Rect viewport={1,0,1279,800};SDL_RenderSetViewport(renderer,&viewport);REQUIRE(!settings_font_present(renderer,VGAScreen,&destination,false));SDL_RenderSetViewport(renderer,NULL);
 frame(1,0,0,2,0,0);SDL_RenderSetClipRect(renderer,&destination);REQUIRE(!settings_font_present(renderer,VGAScreen,&destination,false));SDL_RenderSetClipRect(renderer,NULL);
 frame(1,0,0,2,0,0);scaling_mode=SCALE_ASPECT_8_5;REQUIRE(!settings_font_present(renderer,VGAScreen,&destination,false));scaling_mode=SCALE_INTEGER;
 frame(1,0,0,2,0,0);REQUIRE(settings_font_present(renderer,VGAScreen,&destination,false));settings_font_end();REQUIRE(!sf.texture&&allocated==0);SDL_DestroyRenderer(renderer);SDL_FreeSurface(target);scaler=1;
}

int main(int argc,char **argv)
{
 REQUIRE(argc==3);main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);REQUIRE(VGAScreen&&VGAScreen2&&main_window_tex_format);fixtures(argv[1]);acquire(argv[2]);
 REQUIRE(sizeof(sf)+SF_PAYLOAD+SF_OUT_BYTES+384+2048<=SF_CAP);memcpy(sf.expected_palette,palettes[7],sizeof(colors));live_palette(palettes[7]);sf.initial_done=true;
 unsigned steady_allocations=allocation_calls;
 for(unsigned displays=1;displays<=11;displays++)for(unsigned menu=1;menu<=3;menu++)for(unsigned selected=0;selected<(menu==3?3u:4u);selected++){
  frame(menu,selected,0,displays+1,0,selected%2?32:0);render_checks();
  if(menu==2&&selected<3){unsigned n=selected==0?displays+1:selected==1?9:4;for(unsigned ps=0;ps<n;ps++){frame(menu,selected,selected+1,n,ps,0);render_checks();}}
 }
 REQUIRE(allocation_calls==steady_allocations);
 frame(3,0,0,2,0,32);
 for(unsigned edge=0;edge<5;edge++){
  int x=edge==0?0:edge==1?45:edge==2?180:edge==3?319:-5,y=edge==0?0:edge==1?37:edge==2?190:edge==3?199:-7;
  settings_font_cursor_begin();REQUIRE(sf.frame);blit_sprite2x2_clip(VGAScreen,x,y,shopSpriteSheet,273);settings_font_cursor_done();REQUIRE(sf.frame&&sf.cursor_quad==4);render();REQUIRE(!memcmp(sf.replay,sf.expected,SF_N));
  memcpy(VGAScreen->pixels,sf.pre_cursor,SF_N);settings_font_cursor_erased();REQUIRE(sf.frame);render_checks();
 }
 /* A same-index cursor write must still erase authored ownership. */
 settings_font_cursor_begin();unsigned pos=40*320+48;Uint8 old=((Uint8 *)VGAScreen->pixels)[pos];sf.cursor_sprite=true;sf.cursor_events=1;sf.cursor_next=0;sf.cursor_event[0].position=pos;sf.cursor_event[0].index=old;
 settings_font_pixel(VGAScreen,(Uint8 *)VGAScreen->pixels+pos,0);REQUIRE(sf.cursor_mask[pos]);sf.cursor_sprite=false;sf.cursor_quad=4;settings_font_cursor_done();REQUIRE(sf.frame);render();REQUIRE(sf.output[160*1280+192]==sf.palette[old]);memcpy(VGAScreen->pixels,sf.pre_cursor,SF_N);settings_font_cursor_erased();REQUIRE(sf.frame&&!sf.cursor_mask[pos]);render_checks();
 settings_font_invalidate();REQUIRE(sf.active&&!sf.frame);frame(1,0,0,2,0,0);settings_font_table_reset(3);REQUIRE(sf.active);settings_font_table_reset(2);REQUIRE(!sf.active);
 acquire(argv[2]);frame(1,0,0,2,0,0);settings_font_fade_start(palettes[7],NULL,0,255);for(int step=10;step;step--){for(unsigned i=0;i<256;i++){SDL_Color c=sf.expected_palette[i],t=palettes[7][i];c.r+=(int)(t.r-c.r)/step;c.g+=(int)(t.g-c.g)/step;c.b+=(int)(t.b-c.b)/step;rgb_palette[i]=SDL_MapRGB(main_window_tex_format,c.r,c.g,c.b);}settings_font_fade_step(step,0,255);REQUIRE(sf.active&&sf.frame);render_checks();}REQUIRE(sf.initial_done);SDL_Color black={0,0,0,255};settings_font_fade_start(NULL,&black,0,255);for(int step=10;step;step--){for(unsigned i=0;i<256;i++){SDL_Color c=sf.expected_palette[i];c.r-=(int)c.r/step;c.g-=(int)c.g/step;c.b-=(int)c.b/step;rgb_palette[i]=SDL_MapRGB(main_window_tex_format,c.r,c.g,c.b);}settings_font_fade_step(step,0,255);REQUIRE(sf.active&&sf.frame);render_checks();}REQUIRE(sf.exiting);
 resource_failures(argv[2]);observer_failures(argv[2]);renderer_lifecycle(argv[2]);
 settings_font_end();REQUIRE(!sf.active&&!sf.output&&!sf.texture&&allocated==0);for(unsigned b=0;b<3;b++)for(unsigned id=0;id<sprite_table[b].count;id++)free(sprite(b,id)->data);free(shopSpriteSheet.data);SDL_FreeSurface(VGAScreen);SDL_FreeSurface(VGAScreen2);SDL_FreeFormat(main_window_tex_format);
 printf("PASS checks=%u states=%u max_commands=%u CPU_bound=%zu cap=%u peak_owned_alloc=%zu allocation_calls=%u\n",checks,states,max_commands,sizeof(sf)+SF_PAYLOAD+SF_OUT_BYTES+384+2048,SF_CAP,peak_allocated,allocation_calls);return 0;
}
