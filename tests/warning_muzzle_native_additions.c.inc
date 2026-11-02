/* Combined real font / registered projectile owner oracle. No SDL or owner stubs.
 * Original glyph/RLE and direct HUF/HDA samples determine expected pixels. */
#define CW_X 128
#define CW_Y 169
#define CW_W 48
#define CW_H 16
#define CW_N (CW_W*CW_H*64)
static Uint32 cw_rgb[CW_N],cw_under[CW_N];
static Uint8 cw_native[CW_W*CW_H],cw_hd[CW_N],cw_shared[CW_N],cw_font[CW_N],cw_lower[CW_N],cw_atlas[163840];
static bool cw_live;
static const char *cw_badroot;
static unsigned cw_index(int px,int py){CHECK(px>=CW_X*8&&px<(CW_X+CW_W)*8&&py>=CW_Y*8&&py<(CW_Y+CW_H)*8);return(unsigned)((py-CW_Y*8)*(CW_W*8)+px-CW_X*8);}
static bool cw_inside(int px,int py){return px>=CW_X*8&&px<(CW_X+CW_W)*8&&py>=CW_Y*8&&py<(CW_Y+CW_H)*8;}
static void cw_snapshot(void)
{
 cw_live=false;memset(cw_font,0,sizeof(cw_font));
 for(unsigned y=0;y<CW_H;y++)for(unsigned x=0;x<CW_W;x++)cw_native[y*CW_W+x]=((Uint8*)game_screen->pixels)[(CW_Y+y)*320+CW_X+x];
 for(unsigned y=0;y<CW_H*8;y++)for(unsigned x=0;x<CW_W*8;x++){unsigned k=y*CW_W*8+x,n=(CW_Y*8+y)*2560+CW_X*8+x;cw_rgb[k]=*at(canvas,CW_X*8+x,CW_Y*8+y);cw_hd[k]=hd_owner[n];cw_shared[k]=global_projectile91_owner[n];}
}
static void cw_restart(const char *hudroot)
{
 memcpy(rgb_palette,palette0,sizeof(palette0));CHECK(render_mirror_set_hud_assets(hudroot));memcpy(VGAScreenSeg->pixels,mu_pic3,sizeof(mu_pic3));render_mirror_hud_start(VGAScreenSeg);SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();cw_snapshot();
}
static void cw_setup(void){mu_setup();cw_restart(mu_hudroot);CHECK(hud_font_ready()&&font_gameplay&&shared_hud_frame);}
static void cw_check(bool final)
{
 for(unsigned y=0;y<CW_H;y++)for(unsigned x=0;x<CW_W;x++)CHECK(((Uint8*)game_screen->pixels)[(CW_Y+y)*320+CW_X+x]==cw_native[y*CW_W+x]);
 for(unsigned y=0;y<CW_H*8;y++)for(unsigned x=0;x<CW_W*8;x++){
  unsigned k=y*CW_W*8+x,n=(CW_Y*8+y)*2560+CW_X*8+x;Uint32 want=final&&CW_Y*8+y>=184*8?palette_rgb(cw_native[(y/8)*CW_W+x/8]):cw_rgb[k];
  CHECK(*at(final?output:canvas,(CW_X-(final?24:0))*8+x,CW_Y*8+y)==want);CHECK(global_projectile91_owner[n]==cw_shared[k]);CHECK(hd_owner[n]==cw_hd[k]);
  int wx=(int)x+(CW_X-140)*8,wy=(int)y+(CW_Y-178)*8;if(wx>=0&&wx<34*8&&wy>=0&&wy<6*8&&font_scenes[2].used){unsigned q=font_scenes[2].offset+(unsigned)((wy/8*34+wx/8)*64+(wy%8)*8+wx%8);CHECK(font_owner[q]==cw_font[k]);}
 }
 CHECK(!global_projectile91_fault);
}
static void cw_strip_model(void)
{if(cw_live){for(unsigned k=0;k<CW_N;k++)if(cw_font[k]){cw_rgb[k]=cw_under[k];cw_hd[k]=cw_lower[k];cw_font[k]=0;}cw_live=false;}}
static void cw_tank(int x,int y)
{
 bool intersects=x<174&&x+13>140&&y-1<184&&y+14>178;if(intersects)cw_strip_model();
 Uint8 src[168],mask[168];blue_decode(147,src,mask);const Uint8 *rgba=tk_asset(1)->rgba;
 /* Read the asset through the real finite loader before using direct bytes. */
 if(!rgba){CHECK(enemy_tank_shared_resource(valid_root,147));rgba=tk_asset(1)->rgba;}CHECK(rgba);
 for(int ay=-8;ay<112;ay++)for(int ax=0;ax<104;ax++){
  int px=x*8+ax,py=y*8+ay;if(!cw_inside(px,py))continue;bool native=ax<96&&ay>=0&&mask[(ay/8)*12+ax/8];int rx=ax-8,ry=ay+8;static const Uint8 zero[4]={0};const Uint8 *q=rx>=0&&rx<96&&ry>=0&&ry<112?rgba+4*(ry*96+rx):zero;if(!native&&!q[3])continue;
  unsigned k=cw_index(px,py),cell=(unsigned)((py/8-CW_Y)*CW_W+px/8-CW_X);cw_rgb[k]=alpha(cw_hd[k]?cw_rgb[k]:palette_rgb(cw_native[cell]),q);cw_hd[k]=cw_shared[k]=1;
 }
 for(unsigned c=0;c<168;c++)if(mask[c]&&cw_inside((x+c%12)*8,(y+c/12)*8))cw_native[(y+c/12-CW_Y)*CW_W+x+c%12-CW_X]=src[c];
 mu_birth(x,y,194,3);mu_draw_checked();cw_check(false);CHECK(global_projectile91_used_members==1073741824u);
}
static void cw_decode(unsigned id,Uint8 values[48],Uint8 mask[48])
{
 Sprite *s=&sprite_table[TINY_FONT].sprite[id];CHECK(s->width&&s->height&&s->width<=6&&s->height<=8);memset(values,0,48);memset(mask,0,48);unsigned pos=0,col=0;
 for(unsigned j=0;j<s->size;j++){unsigned v=s->data[j];if(v==255){CHECK(++j<s->size);pos+=s->data[j];col+=s->data[j];}else if(v==254){pos+=s->width-col;col=s->width;}else if(v==253){++pos;++col;}else{CHECK(pos<s->width*s->height);values[pos]=v;mask[pos]=1;++pos;++col;}if(col>=s->width)col=0;CHECK(pos<=s->width*s->height);}
}
static void cw_warning(unsigned value,bool hd)
{
 cw_strip_model();render_mirror_text_warning_begin(game_screen,(int)value);CHECK((font_context==2)==hd);if(!hd)cw_check(false);unsigned advance=0,opaque=0;const char word[]="WARNING";
 memcpy(cw_under,cw_rgb,sizeof(cw_rgb));memcpy(cw_lower,cw_hd,sizeof(cw_hd));memset(cw_font,0,sizeof(cw_font));
 for(unsigned letter=0;letter<7;letter++){
  unsigned id=(unsigned)font_ascii[(unsigned char)word[letter]];Sprite *s=&sprite_table[TINY_FONT].sprite[id];Uint8 values[48],mask[48];cw_decode(id,values,mask);unsigned maxlow=0;
  for(unsigned j=0;j<s->width*s->height;j++)if(mask[j]&&(values[j]&15)>maxlow)maxlow=values[j]&15;CHECK(maxlow==7&&maxlow+value<16);Uint32 color=palette_rgb((7u<<4)|(maxlow+value));
  if(hd)for(unsigned y=0;y<s->height*8;y++)for(unsigned x=0;x<s->width*8;x++){
   unsigned a=cw_atlas[((id/16)*40+4+y/2)*512+(id%16)*32+4+x/2],k=cw_index((140+advance)*8+x,178*8+y);if(a){Uint8 q[4]={(color>>16)&255,(color>>8)&255,color&255,a};cw_rgb[k]=alpha(cw_rgb[k],q);cw_hd[k]=cw_font[k]=1;}
  }
  for(unsigned y=0;y<s->height;y++)for(unsigned x=0;x<s->width;x++)if(mask[y*s->width+x]){
   unsigned value_index=(7u<<4)|((values[y*s->width+x]&15)+value),cell=(178+y-CW_Y)*CW_W+140+advance+x-CW_X;CHECK((values[y*s->width+x]&15)+value<16);cw_native[cell]=value_index;++opaque;
   for(unsigned j=0;j<64;j++){unsigned k=cw_index((140+advance+x)*8+j%8,(178+y)*8+j/8);cw_shared[k]=0;if(hd){cw_under[k]=palette_rgb(value_index);cw_lower[k]=0;cw_font[k]=cw_hd[k]=1;}else{cw_rgb[k]=palette_rgb(value_index);cw_hd[k]=0;}}
  }
  advance+=s->width+1;
 }
 CHECK(advance==35&&opaque==108);JE_outText(game_screen,140,178,"WARNING",7,(int)value);render_mirror_text_end();cw_live=hd;cw_check(false);CHECK(font_scenes[2].canvas_live==hd);
}
static void cw_finish(void){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);cw_check(true);CHECK(font_scenes[2].output_live==cw_live);}
static void cw_read_huf(void)
{char path[1400];int n=snprintf(path,sizeof(path),"%s/gameplay-hud-font-v1.hda",mu_hudroot);CHECK(n>0&&(size_t)n<sizeof(path));FILE*f=fopen(path,"rb");CHECK(f);Uint8 header[112];CHECK(fread(header,1,112,f)==112&&!memcmp(header,"HUF1",4));CHECK(fread(cw_atlas,1,sizeof(cw_atlas),f)==sizeof(cw_atlas)&&fgetc(f)==EOF);CHECK(!fclose(f));}
static void cw_present(bool accepted,int gx,int gy)
{
 SDL_Surface*s=SDL_CreateRGBSurfaceWithFormat(0,output->w,output->h,32,SDL_PIXELFORMAT_ARGB8888);CHECK(s);SDL_Renderer*r=SDL_CreateSoftwareRenderer(s);CHECK(r);CHECK(render_mirror_present(r,VGAScreenSeg,NULL)==accepted);
 if(accepted){SDL_Rect box={(gx-24)*8,gy*8,8,8};Uint32 samples[64];CHECK(!SDL_RenderReadPixels(r,&box,SDL_PIXELFORMAT_ARGB8888,samples,8*4));for(unsigned j=0;j<64;j++)CHECK(samples[j]==*at(output,box.x+j%8,box.y+j/8));}
 if(texture){SDL_DestroyTexture(texture);texture=NULL;}SDL_DestroyRenderer(r);SDL_FreeSurface(s);
}
static void cw_fade(bool fade)
{if(fade){SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);for(unsigned i=0;i<256;i++){Uint32 c=rgb_palette[i],v=0;for(unsigned sh=0;sh<24;sh+=8){int q=(c>>sh)&255;q+=(0-q)/7;v|=(Uint32)q<<sh;}rgb_palette[i]=v;}render_mirror_fade_step(7);CHECK(ready&&last_output_valid&&global_projectile91_cached&&have_fade_saved);}}
static void cw_native64(int gx,int gy,Uint8 value)
{
 SDL_Color colors[256];for(unsigned i=0;i<256;i++)colors[i]=(SDL_Color){(rgb_palette[i]>>16)&255,(rgb_palette[i]>>8)&255,rgb_palette[i]&255,255};CHECK(!SDL_SetPaletteColors(VGAScreenSeg->format->palette,colors,0,256));SDL_Surface *s=SDL_ConvertSurfaceFormat(VGAScreenSeg,SDL_PIXELFORMAT_ARGB8888,0),*cell=SDL_CreateRGBSurfaceWithFormat(0,8,8,32,SDL_PIXELFORMAT_ARGB8888);CHECK(s&&cell);SDL_Rect box={gx-24,gy,1,1};CHECK(!SDL_BlitScaled(s,&box,cell,NULL));for(unsigned j=0;j<64;j++)CHECK(*at(cell,j%8,j/8)==palette_rgb(value));SDL_FreeSurface(cell);SDL_FreeSurface(s);
}
static void cw_same_write(int gx,int gy,bool rect)
{Uint8*p=(Uint8*)VGAScreenSeg->pixels+gy*320+gx-24,value=*p;if(rect){SDL_Rect box={gx-24,gy,1,1};render_mirror_rect(VGAScreenSeg,&box);}else render_mirror_pixel(VGAScreenSeg,p,value,MIRROR_NORMAL);CHECK(*p==value);enemy70_declined();cw_present(false,gx,gy);enemy70_declined();cw_native64(gx,gy,value);}
static void cw_orders2(void)
{
 for(unsigned order=0;order<2;order++){
  cw_setup();if(!order){cw_warning(3,true);CHECK(!font_intersects(font_scenes[2].rect,(SDL_Rect){128,170,12,14})&&font_intersects(font_scenes[2].rect,(SDL_Rect){128,169,13,15}));cw_tank(128,170);CHECK(!font_scenes[2].canvas_live);}else{cw_tank(128,170);cw_warning(7,true);cw_warning(3,true);cw_strip_model();render_mirror_text_warning_begin(game_screen,8);CHECK(font_context==-1&&!font_scenes[2].canvas_live);cw_check(false);cw_warning(3,true);}cw_finish();
  cw_restart(mu_hudroot);cw_tank(128,170);cw_finish();CHECK(!font_scenes[2].output_live);cw_restart(mu_hudroot);cw_tank(128,170);cw_warning(3,true);cw_finish();
  /* Missing/corrupt HUF loader/begin is not permission to erase a valid muzzle.
   * The following real classic glyph writes DO retire its original cells. */
  char missing[1400];int n=snprintf(missing,sizeof(missing),"%s/absent",cw_badroot);CHECK(n>0&&(size_t)n<sizeof(missing));cw_restart(order?cw_badroot:missing);CHECK(!hud_font_ready()&&!font_gameplay);cw_tank(128,170);cw_warning(3,false);cw_finish();cw_restart(mu_hudroot);cw_tank(128,170);cw_warning(3,true);cw_finish();
 }
}
static void cw_writes8(void)
{
 for(unsigned geometry=0;geometry<2;geometry++)for(unsigned fade=0;fade<2;fade++)for(unsigned rect=0;rect<2;rect++){
  cw_setup();int x=geometry?131:128,y=170,gx=geometry?142:140,gy=geometry?181:178;cw_tank(x,y);unsigned sc,gc,hc;pg_counts(gx,gy,&sc,&gc,&hc);CHECK(sc==(geometry?64u:10u)&&hc==sc&&!gc);cw_warning(3,true);pg_counts(gx,gy,&sc,&gc,&hc);CHECK(!sc&&!gc&&hc==64&&global_projectile91_used_members==1073741824u);cw_finish();cw_fade(fade);cw_present(true,gx,gy);cw_same_write(gx,gy,rect);cw_restart(mu_hudroot);cw_tank(x,y);cw_warning(3,true);cw_finish();
 }
}
static void cw_green2(void)
{
 for(unsigned mode=0;mode<2;mode++){
  cw_setup();int x,y;pg_birth(&x,&y);int gx=x+11,gy=y+1,ex=gx-12,ey=gy-8;CHECK(gy<178&&ex>=24&&ey>=1&&ey<=170);MuBefore b;mu_birth(ex,ey,194,3);mu_valid(ex,ey,&b);unsigned sc,gc,hc;pg_counts(gx,gy,&sc,&gc,&hc);CHECK(sc==10&&!gc&&hc==10);Uint32 under[64];for(unsigned j=0;j<64;j++)under[j]=hd_owner[(size_t)(gy*8+j/8)*2560+gx*8+j%8]?*at(canvas,gx*8+j%8,gy*8+j/8):palette_rgb(27);
  bool special=false;int sx=0,sy=0;JE_integer damage=0;JE_byte blast=0,chain=0,pnum=0;JE_word rw=0,rh=0;CHECK(player_shot_move_and_draw(0,&special,&sx,&sy,&damage,&blast,&chain,&pnum,&rw,&rh));CHECK(!special&&sx+1==x&&sy==y&&pnum==1);pg_counts(gx,gy,&sc,&gc,&hc);CHECK(!sc&&gc==40&&hc==40&&global_projectile91_used_members==1073741824u);cw_warning(3,true);cw_finish();
  for(unsigned j=0;j<64;j++){const Uint8*q=global_green_rgba[0]+4*((8+j/8)*96+88+j%8);CHECK(*at(output,(gx-24)*8+j%8,gy*8+j/8)==alpha(under[j],q));}
  cw_fade(mode);cw_present(true,gx,gy);Uint32 saved[34*6*64];for(unsigned yy=0;yy<48;yy++)for(unsigned xx=0;xx<272;xx++)saved[yy*272+xx]=*at(output,116*8+xx,178*8+yy);uint64_t owners=gameplay_hud_fnv64(font_owner+font_scenes[2].offset,font_scenes[2].used);cw_same_write(gx,gy,mode);CHECK(owners==gameplay_hud_fnv64(font_owner+font_scenes[2].offset,font_scenes[2].used));for(unsigned yy=0;yy<48;yy++)for(unsigned xx=0;xx<272;xx++)CHECK(saved[yy*272+xx]==*at(output,116*8+xx,178*8+yy));
  cw_restart(mu_hudroot);cw_tank(128,170);cw_warning(3,true);cw_finish();
 }
}
static int cw_main(int argc,char **argv)
{CHECK(argc==5);cw_badroot=argv[4];cw_load(4,argv);cw_read_huf();unsigned initial=cases,before=checks;cw_orders2();cw_writes8();cw_green2();CHECK(cases-initial==12);printf("PASS combined WARNING/muzzle real-owner native: 12 setups %u assertions; no old32/44 dispatch, not full gameplay\n",checks-before);return 0;}
