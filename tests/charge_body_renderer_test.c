/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Bounded component test: full production renderer, loader, blitter and SDL.
 * Private bank inputs and deliberately synthetic HD art are supplied at runtime.
 * No gameplay data or original pixels are embedded in this test. */
#include "../src/render_mirror.c"

#define CHECK(x) do { if(!(x)){fprintf(stderr,"CHECK failed %s:%d: %s\n",__FILE__,__LINE__,#x);exit(1);} } while(0)
static unsigned checks, wrappers, dispatches, regressions, blit_calls;
static unsigned observed_id[16];
void __real_blit_sprite2(SDL_Surface *,int,int,Sprite2_array,unsigned);
void __wrap_blit_sprite2(SDL_Surface *s,int x,int y,Sprite2_array b,unsigned i)
{
 if(blit_calls<16)observed_id[blit_calls]=i;
 ++blit_calls;__real_blit_sprite2(s,x,y,b,i);
}
#include "charge_dispatch.inc"
static const unsigned charge_ids[9]={258,259,260,277,278,279,296,297,298};
static Uint8 *read_bytes(const char *path,size_t *size)
{
 FILE*f=fopen(path,"rb");CHECK(f);CHECK(!fseek(f,0,SEEK_END));long n=ftell(f);CHECK(n>0);rewind(f);
 Uint8*p=malloc((size_t)n);CHECK(p&&fread(p,1,(size_t)n,f)==(size_t)n);CHECK(!fclose(f));*size=(size_t)n;return p;
}
static void cache_clear(void)
{
 for(unsigned i=0;i<COUNTOF(assets);i++){free(assets[i].rgba);memset(&assets[i],0,sizeof(assets[i]));}
}
static void scene_reset(void)
{
 size_t n=(size_t)canvas->w*canvas->h;
 memset(game_screen->pixels,49,(size_t)game_screen->pitch*game_screen->h);memset(expected,49,sizeof(expected));
 SDL_FillRect(canvas,NULL,0xff313131u);memset(hd_owner,0,n);memset(cloud_owner,0,n);memset(green_first,0,n*sizeof(*green_first));memset(selected,0,sizeof(selected));
 active=true;reject_reason=NULL;draws=0;region_count=0;green_head_count=0;blit_calls=0;memset(observed_id,0,sizeof(observed_id));render_mirror_entity_end();
}
static void scene_create(unsigned d)
{
 game_probe_density=(int)d;
 if(canvas)SDL_FreeSurface(canvas);free(hd_owner);free(cloud_owner);free(green_first);
 canvas=SDL_CreateRGBSurfaceWithFormat(0,320*d,200*d,32,SDL_PIXELFORMAT_ARGB8888);CHECK(canvas);
 size_t n=(size_t)canvas->w*canvas->h;hd_owner=calloc(n,1);cloud_owner=calloc(n,1);green_first=calloc(n,sizeof(*green_first));CHECK(hd_owner&&cloud_owner&&green_first);scene_reset();
}
static Uint32 independent_blend(Uint32 dst,const Uint8*p)
{
 unsigned a=p[3],r=(((dst>>16)&255)*(255-a)+p[0]*a+127)/255,g=(((dst>>8)&255)*(255-a)+p[1]*a+127)/255,b=((dst&255)*(255-a)+p[2]*a+127)/255;
 return 0xff000000u|(r<<16)|(g<<8)|b;
}
static void wrapper_case(unsigned k,int x,int y,bool accepted)
{
 unsigned id=charge_ids[k],charge=k%3;size_t bytes=(size_t)game_screen->pitch*200,hdbytes=(size_t)canvas->pitch*canvas->h;
 Uint8*classic=malloc(bytes);Uint32*oracle=malloc(hdbytes);CHECK(classic&&oracle);scene_reset();
 active=false;__real_blit_sprite2(game_screen,x,y,spriteSheet9,id);memcpy(classic,game_screen->pixels,bytes);scene_reset();
 if(accepted){Asset*a=charge_body_asset(spriteSheet9,id,3,0,charge);CHECK(a&&a==&assets[567+k]&&a->density==8&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y);memcpy(oracle,canvas->pixels,hdbytes);
  int d=game_probe_density;
  for(int yy=0;yy<14*d;yy++)for(int xx=0;xx<12*d;xx++){int dx=x*d+xx,dy=y*d+yy;if(dx<0||dy<0||dx>=canvas->w||dy>=canvas->h)continue;const Uint8*p=a->rgba+((yy*8/d)*96+xx*8/d)*4;oracle[dy*canvas->w+dx]=independent_blend(oracle[dy*canvas->w+dx],p);}
 }
 draw_charge_body_sprite2(game_screen,x,y,spriteSheet9,id,3,0,charge);
 CHECK(blit_calls==1&&observed_id[0]==id&&!suppress&&draws==(accepted?1u:0u));CHECK(!memcmp(classic,game_screen->pixels,bytes));
 if(accepted)CHECK(!memcmp(oracle,canvas->pixels,hdbytes));
 else for(int yy=0;yy<canvas->h;yy++)for(int xx=0;xx<canvas->w;xx++)CHECK(((Uint32*)((Uint8*)canvas->pixels+yy*canvas->pitch))[xx]==palette_rgb(classic[(yy/game_probe_density)*game_screen->pitch+xx/game_probe_density]));
 free(classic);free(oracle);wrappers++;
}
static bool admission(unsigned id,unsigned option,unsigned style,unsigned charge)
{checks++;return charge_body_asset(spriteSheet9,id,option,style,charge)!=NULL;}
static void identities(void)
{
 for(unsigned warm=0;warm<2;warm++)for(unsigned k=0;k<9;k++){
  unsigned id=charge_ids[k],c=k%3;cache_clear();
  if(!warm){
   size_t cold=spriteSheet9.data[2*(id-1)]|((size_t)spriteSheet9.data[2*(id-1)+1]<<8);while(!(spriteSheet9.data[cold]>>4)&&spriteSheet9.data[cold]!=15)cold++;
   CHECK(spriteSheet9.data[cold]!=15);Uint8 value=spriteSheet9.data[cold+1];spriteSheet9.data[cold+1]^=1;CHECK(!admission(id,3,0,c));CHECK(!assets[567+k].initialized);wrapper_case(k,94,73,false);spriteSheet9.data[cold+1]=value;
   Uint8 code=spriteSheet9.data[cold];spriteSheet9.data[cold]=15;CHECK(!admission(id,3,0,c));CHECK(!assets[567+k].initialized);wrapper_case(k,94,73,false);spriteSheet9.data[cold]=code;
  }else CHECK(admission(id,3,0,c));
  CHECK(admission(id,3,0,c));CHECK(!admission(id,2,0,c));CHECK(!admission(id,3,1,c));CHECK(!admission(id,3,0,3));CHECK(!admission(id,3,0,(c+1)%3));CHECK(!admission(id+3,3,0,c));
  xmas=true;CHECK(!admission(id,3,0,c));xmas=false;
  Sprite2_array copy=spriteSheet9;copy.data=malloc(copy.size);CHECK(copy.data);memcpy(copy.data,spriteSheet9.data,copy.size);CHECK(!charge_body_asset(copy,id,3,0,c));free(copy.data);copy=spriteSheet9;copy.size--;CHECK(!charge_body_asset(copy,id,3,0,c));CHECK(!charge_body_asset(spriteSheet8,id,3,0,c));
  /* A source reload at the SAME pointer must not borrow an initialized asset.
   * Flip one actual indexed byte, then alter the RLE coverage, restoring each. */
  size_t pos=spriteSheet9.data[2*(id-1)]|((size_t)spriteSheet9.data[2*(id-1)+1]<<8);while(!(spriteSheet9.data[pos]>>4)&&spriteSheet9.data[pos]!=15)pos++;
  CHECK(spriteSheet9.data[pos]!=15);Uint8 saved=spriteSheet9.data[pos+1];spriteSheet9.data[pos+1]^=1;CHECK(!admission(id,3,0,c));wrapper_case(k,94,73,false);spriteSheet9.data[pos+1]=saved;CHECK(admission(id,3,0,c));
  saved=spriteSheet9.data[pos];spriteSheet9.data[pos]=15;CHECK(!admission(id,3,0,c));wrapper_case(k,94,73,false);spriteSheet9.data[pos]=saved;CHECK(admission(id,3,0,c));
  CHECK(!get_asset(spriteSheet9,id,ENTITY_TILE));
 }
 for(unsigned i=0;i<567;i++)CHECK(!assets[i].initialized);cache_clear();
}
static void resources(const char *root)
{
 const char*names[]={"valid","missing","truncated","wrong_identity","wrong_density","wrong_geometry","wrong_anchor","trailing","only4","mixed"};char path[2048];
 for(unsigned v=0;v<COUNTOF(names);v++){snprintf(path,sizeof(path),"%s/%s",root,names[v]);game_probe_assets=path;cache_clear();for(unsigned d=4;d<=8;d+=4){scene_create(d);for(unsigned k=0;k<9;k++){wrapper_case(k,94,73,v==0||(v==9&&k%2==0));wrapper_case(k,94,73,v==0||(v==9&&k%2==0));}}}
 snprintf(path,sizeof(path),"%s/valid",root);game_probe_assets=path;cache_clear();
 const int xy[][2]={{0,0},{308,0},{0,-13},{308,-1},{94,187},{0,199},{308,199},{-3,73},{315,73},{94,-14},{94,200}};
 for(unsigned d=4;d<=8;d+=4){scene_create(d);for(unsigned k=0;k<9;k++)for(unsigned i=0;i<COUNTOF(xy);i++){int x=xy[i][0],y=xy[i][1];wrapper_case(k,x,y,x>=0&&x<=308&&y>=-13&&y<=199);}}
 scene_reset();CHECK(!render_mirror_charge_body(NULL,90,70,spriteSheet9,258,3,0,0));
 CHECK(admission(258,3,0,0));asteroid_hd_enabled=true;CHECK(!render_mirror_charge_body(game_screen,90,70,spriteSheet9,258,3,0,0));asteroid_hd_enabled=false;
 active=false;CHECK(!render_mirror_charge_body(game_screen,90,70,spriteSheet9,258,3,0,0));active=true;
 reject_reason="test";CHECK(!render_mirror_charge_body(game_screen,90,70,spriteSheet9,258,3,0,0));reject_reason=NULL;SDL_Surface*other=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(other);CHECK(!render_mirror_charge_body(other,90,70,spriteSheet9,258,3,0,0));SDL_FreeSurface(other);
 int saved=game_screen->w;game_screen->w=319;CHECK(!render_mirror_charge_body(game_screen,90,70,spriteSheet9,258,3,0,0));game_screen->w=saved;
 saved=game_screen->h;game_screen->h=199;CHECK(!render_mirror_charge_body(game_screen,90,70,spriteSheet9,258,3,0,0));game_screen->h=saved;
 saved=game_screen->pitch;game_screen->pitch=319;CHECK(!render_mirror_charge_body(game_screen,90,70,spriteSheet9,258,3,0,0));game_screen->pitch=saved;
 void*pixels=game_screen->pixels;game_screen->pixels=NULL;CHECK(!render_mirror_charge_body(game_screen,90,70,spriteSheet9,258,3,0,0));game_screen->pixels=pixels;
 SDL_PixelFormat*format=game_screen->format;game_screen->format=NULL;CHECK(!render_mirror_charge_body(game_screen,90,70,spriteSheet9,258,3,0,0));game_screen->format=format;
 saved=format->BitsPerPixel;format->BitsPerPixel=32;CHECK(!render_mirror_charge_body(game_screen,90,70,spriteSheet9,258,3,0,0));format->BitsPerPixel=saved;
 saved=format->BytesPerPixel;format->BytesPerPixel=4;CHECK(!render_mirror_charge_body(game_screen,90,70,spriteSheet9,258,3,0,0));format->BytesPerPixel=saved;
 for(unsigned neg=0;neg<3;neg++){scene_reset();draw_charge_body_sprite2(game_screen,94,73,spriteSheet9,258,neg==0?2:3,neg==1?1:0,neg==2?1:0);CHECK(blit_calls==1&&!draws&&!suppress);}
 xmas=true;wrapper_case(0,94,73,false);xmas=false;
 unsigned flags=0;game_probe_missing=true;CHECK(!admission(258,3,0,0));game_probe_missing=false;flags++;game_probe_invalid=true;CHECK(!admission(258,3,0,0));game_probe_invalid=false;flags++;game_probe_original_reference=true;CHECK(!admission(258,3,0,0));game_probe_original_reference=false;flags++;CHECK(flags==3);cache_clear();
}
static void dispatch_cases(void)
{
 memset(options,0,sizeof(options));options[3].option=1;options[3].ani=9;options[3].pwr=2;
 for(unsigned j=0;j<9;j++)options[3].gr[j]=258+19*(j/3);
 Uint8 indexed[64000];unsigned base_ids[16];
 for(unsigned flags=0;flags<16;flags++)for(unsigned enabled=0;enabled<2;enabled++){
  Player a={0};a.is_alive=flags&1;a.items.sidekick[0]=a.items.sidekick[1]=3;
  for(unsigned j=0;j<2;j++){a.sidekick[j].x=94+15*j;a.sidekick[j].y=73;a.sidekick[j].animation_enabled=enabled;a.sidekick[j].charge_ticks=20;}
  Player b=a;twoPlayerMode=(flags&2)!=0;endLevel=(flags&4)!=0;unsigned pnum=(flags&8)?2:1;
  for(unsigned tick=0;tick<70;tick++){
   scene_reset();active=false;baseline_dispatch(&a,pnum);memcpy(indexed,game_screen->pixels,64000);unsigned bc=blit_calls;memcpy(base_ids,observed_id,sizeof(base_ids));
   scene_reset();candidate_dispatch(&b,pnum);CHECK(!memcmp(&a,&b,sizeof(a))&&!memcmp(indexed,game_screen->pixels,64000)&&bc==blit_calls&&!memcmp(base_ids,observed_id,sizeof(base_ids))&&!suppress);
   if((pnum==2||!twoPlayerMode)&&!endLevel){CHECK(draws==2);unsigned c=tick<20?0:tick<40?1:2;unsigned phase=enabled?((tick+1)%9)/3:0;CHECK(observed_id[0]==258+19*phase+c);}else CHECK(!draws&&!bc);dispatches++;
  }
 }
 twoPlayerMode=endLevel=false;
}
static void old_paths(const char *root)
{
 game_probe_assets=root;cache_clear();scene_reset();
 CHECK(marlo152_asset(spriteSheet9,152,30,4,0)==&assets[536]);
 CHECK(mint_body_asset(spriteSheet9,112,16,3,0)==&assets[537]);CHECK(mint_body_asset(spriteSheet9,131,16,3,0)==&assets[538]);CHECK(mint_body_asset(spriteSheet9,150,16,3,0)==&assets[539]);
 CHECK(frontblaster_body_asset(spriteSheet10,83,20,2,0)==&assets[540]);for(unsigned i=0;i<5;i++)CHECK(plasma_body_asset(spriteSheet9,224+19*i,9,0,0)==&assets[541+i]);
 /* All ten old body frames, including the six approved Marlo+Plasma images:
  * compare full canvas against direct old asset draw,
  * while observing the actual indexed wrapper (FrontBlaster uses four tiles). */
 const unsigned ids[]={152,112,131,150,83,224,243,262,281,300};
 size_t bytes=(size_t)canvas->pitch*canvas->h;Uint8*oracle=malloc(bytes);CHECK(oracle);
 for(unsigned k=0;k<COUNTOF(ids);k++){
  Asset*a=&assets[536+k];scene_reset();CHECK(draw_asset(94,73,a,MIRROR_NORMAL,NULL));memcpy(oracle,canvas->pixels,bytes);render_mirror_entity_end();scene_reset();
  if(!k)draw_sidekick_body_sprite2(game_screen,94,73,spriteSheet9,ids[k],30,4,0);
  else if(k<4)draw_mint_body_sprite2(game_screen,94,73,spriteSheet9,ids[k],16,3,0);
  else if(k==4)draw_frontblaster_body_sprite2(game_screen,94,73,spriteSheet10,ids[k],20,2,0);
  else draw_plasma_body_sprite2(game_screen,94,73,spriteSheet9,ids[k],9,0,0);
  CHECK(draws==1&&!suppress&&!memcmp(oracle,canvas->pixels,bytes));if(k!=4)CHECK(blit_calls==1);regressions++;
 }
 for(unsigned k=0;k<9;k++)CHECK(!get_asset(spriteSheet9,charge_ids[k],ENTITY_TILE));free(oracle);cache_clear();
}
int main(int argc,char**argv)
{
 CHECK(argc==3);CHECK(!SDL_Init(0));size_t n;Uint8*shp=read_bytes(argv[1],&n);CHECK(n>34);unsigned count=shp[0]|shp[1]<<8;CHECK(count>=12);Sprite2_array*banks[]={&spriteSheet8,&spriteSheet9,&spriteSheet10};
 for(unsigned k=0;k<3;k++){unsigned b=8+k;size_t start=0,end=0;for(unsigned j=0;j<4;j++){start|=(size_t)shp[2+4*(b-1)+j]<<(8*j);end|=(size_t)shp[2+4*b+j]<<(8*j);}CHECK(start<end&&end<=n);*banks[k]=(Sprite2_array){.data=shp+start,.size=end-start};}
 game_screen=VGAScreen=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(game_screen&&game_screen->pitch==320);for(unsigned i=0;i<256;i++)rgb_palette[i]=i*0x010101u;
 scene_create(8);char valid[2048],old[2048];snprintf(valid,sizeof(valid),"%s/valid",argv[2]);snprintf(old,sizeof(old),"%s/old",argv[2]);game_probe_assets=valid;
 identities();resources(argv[2]);game_probe_assets=valid;cache_clear();scene_create(4);dispatch_cases();scene_create(8);old_paths(old);
 cache_clear();free(shp);SDL_FreeSurface(canvas);SDL_FreeSurface(game_screen);free(hd_owner);free(cloud_owner);free(green_first);SDL_Quit();
 printf("{\"status\":\"PASS\",\"identity_checks\":%u,\"actual_wrapper_cases\":%u,\"dispatch_ticks\":%u,\"old_body_frames\":%u,\"game_runs\":0,\"mock_renderer\":false}\n",checks,wrappers,dispatches,regressions);return 0;
}
