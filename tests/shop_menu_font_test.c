/* Independent whole-run composition and per-resource fallback tests. */
#define main pregame_legacy_main
#include "pregame_font_test.c"
#undef main

static Uint32 menu_over(Uint32 dst,Uint32 rgb,unsigned a)
{
 Uint32 out=(a+(((dst>>24)*(255-a)+127)/255))<<24;
 for(unsigned c=0;c<3;c++)out|=(((((rgb>>(8*c))&255)*a)+((dst>>(8*c))&255)*(255-a)+127)/255)<<(8*c);
 return out;
}
static Uint32 menu_sample(Uint32 color,unsigned x,unsigned y,unsigned r,bool dark,unsigned index)
{
 const struct PfMenuSpec *s=&menu_spec[r];unsigned dx=s->x+(dark?8:0),dy=s->y+(dark?8:0);
 if(x<dx||y<dy||x>=dx+s->w||y>=dy+s->h)return color;
 unsigned at=(y-dy)*s->w+x-dx,a=sf.menu_run[r][at];
 unsigned role=sf.menu_run[r][s->w*s->h+at];
 unsigned ink=dark?(index&240)|((index&15)>>1):(Uint8)((15<<4)|(role-3+(r&&sf.selected==r+1?2:0)));
 SDL_Color rgb=sf.expected_palette[ink];return menu_over(color,((Uint32)rgb.r<<16)|(rgb.g<<8)|rgb.b,a);
}
/* One-point oracle executes indexed and authored operations in source order,
 * sampling shadow before old glyph writes and face before later classic. */
static Uint32 whole_run_oracle(unsigned x,unsigned y)
{
 unsigned p=(y/4)*SF_W+x/4,index=sf.base[p];Uint32 color=0;
 if(metal_visible()){
  unsigned off=0,target=y*SF_OW+x;
  for(unsigned n=0;n<PF_METAL_RUNS;n++){
   unsigned first=u32(sf.metal+off),count=u32(sf.metal+off+4);off+=8;
   if(target>=first&&target<first+count){const Uint8 *v=sf.metal+off+(target-first)*4;Uint32 rgb=0;for(unsigned c=0;c<3;c++)rgb|=((v[c]*sf.metal_gain+127)/255)<<(16-c*8);color=menu_over(0,rgb,v[3]);break;}
   off+=count*4;
  }
 }
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];
  if(c->menu_run&&(!k||sf.commands[k-1].menu_run!=c->menu_run))color=menu_sample(color,x,y,c->menu_run-1,true,index);
  if(c->kind==C_CLASSIC||c->kind==C_SPRITE){
   for(unsigned i=c->first;i<c->first+c->events;i++)if(sf.events[i].position==p){index=sf.events[i].index;if(c->kind==C_CLASSIC)color=0;}
   if(c->kind==C_SPRITE&&x>=c->x*4u&&y>=c->y*4u&&x<(c->x+c->w)*4u&&y<(c->y+c->h)*4u){
    int slot=shop_sprite_slot(c->bank,c->id);const Uint8 *v=shop_sprite_payload(slot)+((y-c->y*4)*c->w*4+x-c->x*4)*4;Uint32 rgb=0;
    for(unsigned ch=0;ch<3;ch++)rgb|=((v[ch]*sf.metal_gain+127)/255)<<(16-ch*8);
    color=menu_over(color,rgb,v[3]);
   }
   continue;
  }
  if(x>=c->x*4u&&y>=c->y*4u&&x<(c->x+c->w)*4u&&y<(c->y+c->h)*4u){
   unsigned gx=x-c->x*4u,gy=y-c->y*4u;
   if(!c->menu_run){
    const struct SfSpec *s=&spec[c->bank];unsigned at=((c->id/16)*s->ch+4+gy)*s->aw+(c->id%16)*s->cw+4+gx;
    unsigned a=sf.payload[c->bank][at],role=c->bank==2?7:sf.payload[c->bank][s->plane+at];
    unsigned ink=c->kind==C_DARK?(index&240)|((index&15)>>1):(Uint8)((c->hue<<4)|(role+c->value));
    SDL_Color rgb=sf.expected_palette[ink];color=menu_over(color,((Uint32)rgb.r<<16)|(rgb.g<<8)|rgb.b,a);
   }
   int original=original_role(c->bank,c->id,gx/4,gy/4);
   if(original>=0)index=c->kind==C_DARK?(index&240)|((index&15)>>1):(Uint8)((c->hue<<4)|(original+c->value));
  }
  if(c->menu_run&&(k+1==sf.count||sf.commands[k+1].menu_run!=c->menu_run))color=menu_sample(color,x,y,c->menu_run-1,false,index);
 }
 return color;
}
static void whole_run_render_checks(void)
{
 render();REQUIRE(replay_matches());
 for(unsigned r=0;r<7;r++)if(sf.menu_run[r]){
  const struct PfMenuSpec *s=&menu_spec[r];
  for(unsigned y=0;y<s->h+8;y+=3)for(unsigned x=0;x<s->w+8;x+=3){unsigned ox=s->x+x,oy=s->y+y;REQUIRE(sf.output[oy*SF_OW+ox]==whole_run_oracle(ox,oy));}
 }
 for(unsigned n=0;n<300;n++){unsigned x=(n*131)%SF_OW,y=(n*89)%SF_OH;REQUIRE(sf.output[y*SF_OW+x]==whole_run_oracle(x,y));}
}
static void menu_loaded(int absent)
{
 REQUIRE(sf.active&&sf.frame&&sf.metal&&sf.shop_sprite);
 for(unsigned r=0;r<7;r++)REQUIRE((sf.menu_run[r]!=NULL)==((int)r!=absent));
}
static void menu_failures(const char *dir)
{
 char temp[]="/tmp/shop-menu-font-XXXXXX";REQUIRE(mkdtemp(temp));char paths[12][1024],in[1024];
 const char *names[]={"settings-font-large-v1.hda","settings-font-medium-v1.hda","settings-font-tiny-v1.hda","shop-frame-metal-v1.hda","shop-talon-option31-v1.hda"};
 for(unsigned i=0;i<12;i++){
  if(i<5)snprintf(in,sizeof(in),"%s/%s",dir,names[i]);else snprintf(in,sizeof(in),"%s/shop-menu-run%u-v1.hda",dir,i-5);
  if(i<5)snprintf(paths[i],sizeof(paths[i]),"%s/%s",temp,names[i]);else snprintf(paths[i],sizeof(paths[i]),"%s/shop-menu-run%u-v1.hda",temp,i-5);
  REQUIRE(!symlink(in,paths[i]));
 }
 for(unsigned r=0;r<7;r++){
  snprintf(in,sizeof(in),"%s/shop-menu-run%u-v1.hda",dir,r);FILE *f=fopen(in,"rb");REQUIRE(f);
  size_t bytes=128+menu_spec[r].w*menu_spec[r].h*2;Uint8 *file=malloc(bytes+1);REQUIRE(file&&fread(file,1,bytes,f)==bytes);fclose(f);file[bytes]=0;
  REQUIRE(!unlink(paths[r+5]));acquire(temp,0,2,4);menu_loaded(r);pregame_font_end();
  for(unsigned offset=0;offset<128;offset+=4){file[offset]^=128;write_bytes(paths[r+5],file,bytes);acquire(temp,0,2,4);menu_loaded(r);pregame_font_end();file[offset]^=128;}
  const size_t lengths[]={0,127,bytes-1,bytes+1};for(unsigned n=0;n<4;n++){write_bytes(paths[r+5],file,lengths[n]);acquire(temp,0,2,4);menu_loaded(r);pregame_font_end();}
  file[128]^=1;write_bytes(paths[r+5],file,bytes);acquire(temp,0,2,4);menu_loaded(r);pregame_font_end();file[128]^=1;
  write_bytes(paths[r+5],file,bytes);fail_allocation=allocation_calls+6+r;acquire(temp,0,2,4);menu_loaded(r);pregame_font_end();fail_allocation=UINT_MAX;
  REQUIRE(!unlink(paths[r+5]));REQUIRE(!mkdir(paths[r+5],0700));acquire(temp,0,2,4);menu_loaded(r);pregame_font_end();REQUIRE(!rmdir(paths[r+5]));
  REQUIRE(!mkfifo(paths[r+5],0600));acquire(temp,0,2,4);menu_loaded(r);pregame_font_end();REQUIRE(!unlink(paths[r+5]));
  REQUIRE(!symlink(in,paths[r+5]));free(file);
 }
 for(unsigned i=0;i<12;i++)REQUIRE(!unlink(paths[i]));REQUIRE(!rmdir(temp));
}
int main(int argc,char **argv)
{
 REQUIRE(argc==3&&SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);VGAScreen2=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);REQUIRE(VGAScreen&&VGAScreen2);
 main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);REQUIRE(main_window_tex_format);
 fixtures(argv[1]);strings_fixture(argv[1]);memcpy(raw_base,VGAScreen2->pixels,SF_N);test_ship=31;
 for(unsigned selected=2;selected<=7;selected++)for(unsigned cubes=0;cubes<=4;cubes+=4){
  frame_checks(argv[2],0,selected,cubes,15,10);menu_loaded(-1);unsigned starts=0;
  for(unsigned k=0;k<sf.count;k++)if(sf.commands[k].menu_run&&(!k||sf.commands[k-1].menu_run!=sf.commands[k].menu_run))starts++;
  REQUIRE(starts==7);whole_run_render_checks();present_checks();cursor_checks();
 }
 /* A real later same-index operation must occlude all authored subpixels. */
 frame_checks(argv[2],0,2,4,15,10);render();unsigned p=SF_N;
 for(unsigned r=0;r<7&&p==SF_N;r++){
  const struct PfMenuSpec *s=&menu_spec[r];
  for(unsigned y=0;y<s->h&&p==SF_N;y++)for(unsigned x=0;x<s->w&&p==SF_N;x++)if(sf.menu_run[r][y*s->w+x]>=128){
   unsigned px=(s->x+x)/4,py=(s->y+y)/4;bool old_box=false;
   for(unsigned k=0;k<sf.count;k++){const struct SfCommand *v=&sf.commands[k];if(v->menu_run==r+1&&px>=v->x&&py>=v->y&&px<v->x+v->w&&py<v->y+v->h)old_box=true;}
   if(!old_box&&sf.output[(s->y+y)*SF_OW+s->x+x])p=py*SF_W+px;
  }
 }
 REQUIRE(p<SF_N); /* New natural ink beyond every old glyph rectangle. */
 struct SfCommand *c=append(C_CLASSIC,0,0,0,0,0,0);REQUIRE(c&&event(p%SF_W,p/SF_W,sf.expected[p],0));c->events=1;render();
 for(unsigned y=0;y<4;y++)for(unsigned x=0;x<4;x++)REQUIRE(!sf.output[((p/SF_W)*4+y)*SF_OW+(p%SF_W)*4+x]);
 /* Same text outside root and mutated/unknown labels keep shared SFN1. */
 frame_checks(argv[2],1,2,4,15,10);for(unsigned k=0;k<sf.count;k++)REQUIRE(!sf.commands[k].menu_run);for(unsigned r=0;r<7;r++)REQUIRE(!sf.menu_run[r]);render_checks();
 char saved[18];memcpy(saved,menuInt[1][1],18);strcpy(menuInt[1][1],"Data Data");frame_checks(argv[2],0,2,4,15,10);
 for(unsigned k=0;k<sf.count;k++)REQUIRE(sf.commands[k].menu_run!=2);memcpy(menuInt[1][1],saved,18);
 frame_checks(argv[2],0,4,4,15,10);pregame_font_fade_declare(10);SDL_Color black={0,0,0,255};pregame_font_fade_start(NULL,&black,0,255);
 for(int n=10;n;n--){SDL_Color pal[256];memcpy(pal,sf.expected_palette,sizeof(pal));for(unsigned i=0;i<256;i++){pal[i].r+=(0-pal[i].r)/n;pal[i].g+=(0-pal[i].g)/n;pal[i].b+=(0-pal[i].b)/n;}live_palette(pal);pregame_font_fade_step(n,0,255);whole_run_render_checks();}
 pregame_font_end();REQUIRE(!allocated);memcpy(colors,palettes[0],sizeof(colors));menu_failures(argv[2]);
 REQUIRE(sizeof(sf)+1800000+70000+peak_allocated+2048<=SF_CAP);
 for(unsigned b=0;b<7;b++)for(unsigned id=0;id<sprite_table[b].count;id++)free(sprite(b,id)->data);free(shopSpriteSheet.data);
 SDL_FreeSurface(VGAScreen);SDL_FreeSurface(VGAScreen2);SDL_FreeFormat(main_window_tex_format);SDL_Quit();
 printf("PASS shop whole-run: %u states %u checks; static=%zu peak_owned=%zu reserved_peak=%zu cap=%u\n",states,checks,sizeof(sf),peak_allocated,sizeof(sf)+1800000+70000+peak_allocated+2048,SF_CAP);return 0;
}
