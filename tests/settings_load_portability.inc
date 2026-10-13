/* Shared Settings/Load test adapter. Independent command/layer and real-scaler
 * output oracles; original menu fixtures remain in their existing harnesses. */
#include <math.h>
static unsigned portable_layer_states,portable_renderer_cases,portable_geometry_states;
static Uint32 portable_oracle(unsigned x,unsigned y)
{
 unsigned p=(y/4)*320+x/4;Uint8 index=sf.base[p];unsigned v[4]={0,0,0,0};
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];
  if(x<c->x*4u||x>=(c->x+c->w)*4u||y<c->y*4u||y>=(c->y+c->h)*4u)continue;
  if(c->kind>=C_SOLID){index=c->kind==C_SOLID?(Uint8)c->value:(index&240)|((index&15)/2);memset(v,0,sizeof(v));continue;}
  unsigned gx=x-c->x*4u,gy=y-c->y*4u;const struct SfSpec *s=&spec[c->bank];
  unsigned off=((c->id/16)*s->ch+4+gy)*s->aw+(c->id%16)*s->cw+4+gx;
  unsigned a=sf.payload[c->bank][off],role=c->bank==2?7:sf.payload[c->bank][s->plane+off];
  Uint8 ink=c->kind==C_DARK?(index&240)|((index&15)/2):c->kind==C_BLACK?0:PORTABLE_FACE(role,c);
  SDL_Color color=sf.expected_palette[ink];unsigned rgb[3]={color.b,color.g,color.r};
  for(unsigned ch=0;ch<3;ch++)v[ch]=(rgb[ch]*a+v[ch]*(255-a)+127)/255;
  v[3]=a+(v[3]*(255-a)+127)/255;
  int original=original_role(c->bank,c->id,gx/4,gy/4);
  if(original>=0)index=c->kind==C_DARK?(index&240)|((index&15)/2):c->kind==C_BLACK?0:PORTABLE_FACE(original,c);
 }
 return (v[3]<<24)|(v[2]<<16)|(v[1]<<8)|v[0];
}
static void portable_checks(void)
{
 portable_layer_states++;
 Uint8 expected_underlay[SF_N];memcpy(expected_underlay,sf.base,SF_N);
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];if(c->kind<C_SOLID)continue;
  for(unsigned y=c->y;y<c->y+c->h;y++)for(unsigned x=c->x;x<c->x+c->w;x++){
   unsigned p=y*320+x;expected_underlay[p]=c->kind==C_SOLID?(Uint8)c->value:(expected_underlay[p]&240)|((expected_underlay[p]&15)/2);
  }
 }
 for(unsigned p=0;p<SF_N;p++)if(sf.cursor_mask[p])expected_underlay[p]=sf.cursor_index[p];
 uint64_t before=hash(VGAScreen->pixels,SF_N);SDL_Rect support;
 REQUIRE(render_portable(&support));REQUIRE(!memcmp(sf.replay,expected_underlay,SF_N));REQUIRE(hash(VGAScreen->pixels,SF_N)==before);
 for(unsigned n=0;n<96;n++){
  unsigned x=(n*137+states*17)%1280,y=(n*79+states*29)%800;REQUIRE(sf.output[y*1280+x]==portable_oracle(x,y));
 }
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];if(c->kind>=C_SOLID)continue;
  REQUIRE(support.x<=c->x*4&&support.y<=c->y*4&&support.x+support.w>=(c->x+c->w)*4&&support.y+support.h>=(c->y+c->h)*4);
  unsigned x=c->x*4+c->w*2,y=c->y*4+c->h*2;REQUIRE(sf.output[y*1280+x]==portable_oracle(x,y));
 }
}
static Uint32 portable_output_oracle(const SDL_Rect *d,int x,int y,Uint32 bg)
{
 long double l=(long double)(x-d->x)*1280/d->w,r=(long double)(x+1-d->x)*1280/d->w;
 long double t=(long double)(y-d->y)*800/d->h,b=(long double)(y+1-d->y)*800/d->h;
 bool mx=d->w>1280,my=d->h>800;long double center_x=(l+r)/2-0.5L,center_y=(t+b)/2-0.5L;
 int x0=mx?(int)floorl(center_x):(int)floorl(l),x1=mx?x0+2:(int)ceill(r);
 int y0=my?(int)floorl(center_y):(int)floorl(t),y1=my?y0+2:(int)ceill(b);
 long double area=(mx?1:r-l)*(my?1:b-t),sum[4]={0,0,0,0};
 for(int cy=MAX(0,y0);cy<MIN(800,y1);cy++)for(int cx=MAX(0,x0);cx<MIN(1280,x1);cx++){
  long double wx=mx?fmaxl(0,1-fabsl(cx-center_x)):fminl(r,cx+1)-fmaxl(l,cx);
  long double wy=my?fmaxl(0,1-fabsl(cy-center_y)):fminl(b,cy+1)-fmaxl(t,cy);
  Uint32 c=portable_oracle(cx,cy);for(unsigned ch=0;ch<4;ch++)sum[ch]+=wx*wy*((c>>(ch*8))&255);
 }
 Uint32 result=0xff000000;
 for(unsigned ch=0;ch<3;ch++){long double v=sum[ch]/area+((bg>>(ch*8))&255)*(1-sum[3]/(255*area));result|=(Uint32)fminl(255,fmaxl(0,floorl(v+0.5L)))<<(ch*8);}
 return result;
}
static bool portable_near(Uint32 a,Uint32 b)
{for(unsigned ch=0;ch<3;ch++)if(abs((int)((a>>(ch*8))&255)-(int)((b>>(ch*8))&255))>1)return false;return true;}
static void portable_draw(SDL_Renderer *r,SDL_Texture *t,SDL_Surface *source,const SDL_Rect *d,Uint32 *pixels,int width)
{
 scalers[scaler].scaler32(source,t);REQUIRE(!SDL_SetRenderDrawColor(r,0,0,0,255));REQUIRE(!SDL_RenderClear(r));REQUIRE(!SDL_RenderCopy(r,t,NULL,d));REQUIRE(!SDL_RenderReadPixels(r,NULL,SDL_PIXELFORMAT_ARGB8888,pixels,width*4));
}
static void portable_renderer_case(const char *directory,unsigned scale,int width,int height,SDL_Rect destination,bool legacy,bool cursor)
{
 portable_renderer_cases++;acquire(directory);sf.initial_done=true;memcpy(sf.expected_palette,palettes[7],sizeof(colors));live_palette(palettes[7]);scaler=scale;PORTABLE_FRAME();
 if(cursor){PORTABLE_FN(cursor_begin)();blit_sprite2x2_clip(VGAScreen,45,37,shopSpriteSheet,273);PORTABLE_FN(cursor_done)();REQUIRE(sf.frame);}
 SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,width,height,32,SDL_PIXELFORMAT_ARGB8888);REQUIRE(target);SDL_Renderer *r=SDL_CreateSoftwareRenderer(target);REQUIRE(r);
 SDL_Texture *reference=SDL_CreateTexture(r,SDL_PIXELFORMAT_RGB888,SDL_TEXTUREACCESS_STREAMING,scalers[scale].width,scalers[scale].height);REQUIRE(reference);
 Uint32 *base=malloc((size_t)width*height*4),*classic=malloc((size_t)width*height*4),*actual=malloc((size_t)width*height*4);REQUIRE(base&&classic&&actual);
 SDL_Rect support;REQUIRE(render_portable(&support));SDL_Surface underlay=*VGAScreen;underlay.pixels=sf.replay;
 portable_draw(r,reference,&underlay,&destination,base,width);portable_draw(r,reference,VGAScreen,&destination,classic,width);
 REQUIRE(PORTABLE_FN(present)(r,reference,VGAScreen,&destination,false));REQUIRE(!SDL_RenderReadPixels(r,NULL,SDL_PIXELFORMAT_ARGB8888,actual,width*4));
 if(legacy){REQUIRE(sf.texture);for(int y=0;y<height;y++)for(int x=0;x<width;x++)REQUIRE((actual[y*width+x]&0xffffff)==(sf.output[y*width+x]&0xffffff));}
 else{
  REQUIRE(!sf.texture);
  int pad=scale==0||scale==1||scale==4||scale==7?0:1;int cl=320,ct=200,cr=0,cb=0;
  for(int y=0;y<200;y++)for(int x=0;x<320;x++)if(sf.cursor_mask[y*320+x]){cl=MIN(cl,x);ct=MIN(ct,y);cr=MAX(cr,x+1);cb=MAX(cb,y+1);}
  cl=MAX(0,cl-pad);ct=MAX(0,ct-pad);cr=MIN(320,cr+pad);cb=MIN(200,cb+pad);
  int xl=destination.x+(int)floor((double)cl*destination.w/320),xt=destination.y+(int)floor((double)ct*destination.h/200);
  int xr=destination.x+(int)ceil((double)cr*destination.w/320),xb=destination.y+(int)ceil((double)cb*destination.h/200);
  for(unsigned n=0;n<600;n++){
   unsigned k=n%sf.count;const struct SfCommand *c=&sf.commands[k];
   int x=destination.x+(int)(((long long)c->x*4+(n*13)%(c->w*4))*destination.w/1280),y=destination.y+(int)(((long long)c->y*4+(n*19)%(c->h*4))*destination.h/800);
   if(x<0||y<0||x>=width||y>=height)continue;
   unsigned p=y*width+x;Uint32 expected=cursor&&x>=xl&&x<xr&&y>=xt&&y<xb?classic[p]:portable_output_oracle(&destination,x,y,base[p]);
   if(!portable_near(actual[p],expected))fprintf(stderr,"portable scaler=%u %dx%d at %d,%d got=%08x expected=%08x\n",scale,width,height,x,y,actual[p],expected);
   REQUIRE(portable_near(actual[p],expected));
  }
  /* Font-free pixels beyond conservative support retain the selected scaler. */
  for(int y=0;y<height;y++)for(int x=0;x<width;x++)if(x<destination.x||y<destination.y||x>=destination.x+destination.w||y>=destination.y+destination.h)REQUIRE(actual[y*width+x]==base[y*width+x]);
 }
 REQUIRE(PORTABLE_FN(present)(r,reference,VGAScreen,&destination,false));
 REQUIRE(!PORTABLE_FN(present)(r,reference,VGAScreen,&destination,true));REQUIRE(!sf.frame&&!sf.texture);
 PORTABLE_FRAME();scalers[scale].scaler32(VGAScreen,reference);REQUIRE(PORTABLE_FN(present)(r,reference,VGAScreen,&destination,false));
 PORTABLE_FN(invalidate)();REQUIRE(sf.active&&!sf.frame&&!sf.texture);PORTABLE_FRAME();REQUIRE(PORTABLE_FN(present)(r,reference,VGAScreen,&destination,false));
 PORTABLE_FN(end)();REQUIRE(allocated==0);free(base);free(classic);free(actual);SDL_DestroyTexture(reference);SDL_DestroyRenderer(r);SDL_FreeSurface(target);
}
static void portable_geometry_checks(const char *d)
{
 acquire(d);sf.initial_done=true;memcpy(sf.expected_palette,palettes[7],sizeof(colors));live_palette(palettes[7]);scaler=1;
 SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,1280,800,32,SDL_PIXELFORMAT_ARGB8888);REQUIRE(target);SDL_Renderer *r=SDL_CreateSoftwareRenderer(target);REQUIRE(r);
 SDL_Texture *reference=SDL_CreateTexture(r,SDL_PIXELFORMAT_RGB888,SDL_TEXTUREACCESS_STREAMING,640,400);REQUIRE(reference);
 SDL_Rect destination={0,0,640,400};
 for(unsigned kind=0;kind<5;kind++){
  PORTABLE_FN(invalidate)();REQUIRE(!SDL_RenderSetLogicalSize(r,0,0));REQUIRE(!SDL_RenderSetScale(r,1,1));REQUIRE(!SDL_RenderSetViewport(r,NULL));REQUIRE(!SDL_RenderSetClipRect(r,NULL));
  if(kind==0)REQUIRE(!SDL_RenderSetLogicalSize(r,640,400));
  if(kind==1)REQUIRE(!SDL_RenderSetScale(r,1.25f,1.5f));
  if(kind==2){SDL_Rect v={13,7,1200,760};REQUIRE(!SDL_RenderSetViewport(r,&v));}
  if(kind==3){SDL_Rect c={19,11,1170,740};REQUIRE(!SDL_RenderSetClipRect(r,&c));}
  if(kind==4)scaling_mode=SCALE_ASPECT_8_5;
  PORTABLE_FRAME();scalers[scaler].scaler32(VGAScreen,reference);
  SDL_Rect v,c,after_v,after_c;float sx,sy,after_sx,after_sy;int lw,lh,after_lw,after_lh;
  SDL_RenderGetViewport(r,&v);SDL_RenderGetClipRect(r,&c);SDL_RenderGetScale(r,&sx,&sy);SDL_RenderGetLogicalSize(r,&lw,&lh);
  uint64_t before=hash(VGAScreen->pixels,SF_N);REQUIRE(PORTABLE_FN(present)(r,reference,VGAScreen,&destination,false));REQUIRE(before==hash(VGAScreen->pixels,SF_N));
  SDL_RenderGetViewport(r,&after_v);SDL_RenderGetClipRect(r,&after_c);SDL_RenderGetScale(r,&after_sx,&after_sy);SDL_RenderGetLogicalSize(r,&after_lw,&after_lh);
  REQUIRE(!memcmp(&v,&after_v,sizeof(v))&&!memcmp(&c,&after_c,sizeof(c))&&sx==after_sx&&sy==after_sy&&lw==after_lw&&lh==after_lh);portable_geometry_states++;
 }
 scaling_mode=SCALE_INTEGER;PORTABLE_FN(invalidate)();PORTABLE_FRAME();REQUIRE(!PORTABLE_FN(present)(r,NULL,VGAScreen,&destination,false));REQUIRE(!sf.frame);
 PORTABLE_FRAME();scaler=2;REQUIRE(!PORTABLE_FN(present)(r,reference,VGAScreen,&destination,false));REQUIRE(!sf.frame);scaler=1;
 PORTABLE_FRAME();REQUIRE(!SDL_SetTextureColorMod(reference,254,255,255));REQUIRE(!PORTABLE_FN(present)(r,reference,VGAScreen,&destination,false));REQUIRE(!sf.frame);REQUIRE(!SDL_SetTextureColorMod(reference,255,255,255));
 PORTABLE_FRAME();REQUIRE(PORTABLE_FN(present)(r,reference,VGAScreen,&destination,false));PORTABLE_FN(end)();SDL_DestroyTexture(reference);SDL_DestroyRenderer(r);SDL_FreeSurface(target);
}
static void renderer_lifecycle(const char *d)
{
 portable_renderer_case(d,1,640,400,(SDL_Rect){0,0,640,400},true,false);
 portable_renderer_case(d,7,1280,800,(SDL_Rect){0,0,1280,800},true,false);
 portable_renderer_case(d,1,1920,1200,(SDL_Rect){0,0,1920,1200},false,false);
 portable_renderer_case(d,7,1365,853,(SDL_Rect){0,0,1365,853},false,false);
 portable_renderer_case(d,4,1920,1080,(SDL_Rect){96,0,1728,1080},false,true);
 portable_renderer_case(d,2,913,571,(SDL_Rect){17,9,880,550},false,true);
 portable_renderer_case(d,6,1279,801,(SDL_Rect){0,0,1279,801},false,true);
 portable_geometry_checks(d);
 acquire(d);memcpy(sf.expected_palette,palettes[7],sizeof(colors));live_palette(palettes[7]);scaler=1;PORTABLE_FRAME();
 SDL_Rect support;Uint8 old=sf.expected[0];sf.expected[0]^=1;REQUIRE(!render_portable(&support));REQUIRE(sf.replay[0]==old);sf.expected[0]=old;
 /* A same-index primitive must erase previous layer coverage at all 16 samples. */
 unsigned pos=0;REQUIRE(render_portable(&support));while(pos<SF_N&&(!sf.owner[pos]||!sf.output[(pos/320)*4*1280+(pos%320)*4]))pos++;REQUIRE(pos<SF_N);
 REQUIRE(PORTABLE_SOLID(pos));REQUIRE(render_portable(&support));
 for(unsigned y=0;y<4;y++)for(unsigned x=0;x<4;x++)REQUIRE(!sf.output[((pos/320)*4+y)*1280+(pos%320)*4+x]);
 PORTABLE_FN(end)();scaler=1;
 printf("PORTABLE PASS layer_states=%u renderer_cases=%u geometry_states=%u shared_output_static=%zu\n",portable_layer_states,portable_renderer_cases,portable_geometry_states,selector_font_output_static_bytes());
}
