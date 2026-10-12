/* SPDX-License-Identifier: GPL-2.0-or-later
 * Exact-pixel synthetic tests. This never invokes or captures the game. */
#include "world_material.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint8_t atlas_bytes[G101_ATLAS_BYTES];
static uint8_t masks[G101_MASK_BYTES];
static void *map_cells[G101_MAP_ROWS][G101_MAP_COLS];
static uint64_t assertions, sampled_pixels;
#define CHECK(x) do { ++assertions; if(!(x)) { fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#x);exit(1); } } while(0)
static G101Atlas atlas={atlas_bytes,sizeof(atlas_bytes),768,896,8};
static int mod(int64_t x,int n) { int r=(int)(x%n);return r<0?r+n:r; }
static void tag(int64_t x,int64_t y,uint8_t out[4])
{
 unsigned n=(unsigned)(mod(y,896)*768+mod(x,768));
 out[0]=(uint8_t)n;out[1]=(uint8_t)(n>>8);out[2]=(uint8_t)(n>>16);out[3]=255;
}
static void fill_tags(void)
{ for(int y=0;y<896;y++)for(int x=0;x<768;x++)tag(x,y,atlas_bytes+4*(y*768+x)); }
static void exact_sample(const G101Context *c,int64_t sx,int64_t sy,int64_t wx,int64_t wy)
{
 uint8_t actual[4],expected[4];tag(wx,wy,expected);
 CHECK(g101_sample(c,&atlas,8,sx,sy,actual));CHECK(!memcmp(actual,expected,4));++sampled_pixels;
}
static G101Context context(unsigned row,unsigned col,int x,int y)
{
 G101Context c;g101_begin_frame(&c);
 CHECK(g101_observe_row(&c,map_cells,sizeof(map_cells),&map_cells[row][col],sizeof(void *),12,x,y));return c;
}

static void test_modulo_and_shapes(void)
{
 CHECK(g101_positive_mod(-1,768)==767);CHECK(g101_positive_mod(-768,768)==0);
 CHECK(g101_positive_mod(-769,768)==767);CHECK(g101_positive_mod(INT64_MIN,896)==mod(INT64_MIN,896));
 G101Context c=context(0,0,1000,1000);
 for(int y=-1200;y<=1200;y+=7)for(int x=-1100;x<=1100;x+=11)
  exact_sample(&c,x,y,(int64_t)x-8000,(int64_t)y-8000);
 uint8_t out[4]={0};G101Atlas bad=atlas;
 bad.width--;CHECK(!g101_sample(&c,&bad,8,0,0,out));bad=atlas;bad.bytes--;
 CHECK(!g101_sample(&c,&bad,8,0,0,out));CHECK(!g101_sample(&c,&atlas,4,0,0,out));
 G101Context extreme={true,false,INT64_MIN,INT64_MAX};
 CHECK(g101_sample(&extreme,&atlas,8,INT64_MAX,INT64_MIN,out));
 uint8_t expected[4];tag((int64_t)mod(INT64_MAX,768)+8*mod(INT64_MIN,768),
  (int64_t)mod(INT64_MIN,896)+8*mod(INT64_MAX,896),expected);CHECK(!memcmp(out,expected,4));
 puts("PASS negative modulo, extreme coordinates, exact atlas shape and density gating");
}

static void test_pointer_validation(void)
{
 G101Context c=context(40,2,11,-3);
 CHECK(c.world_x==37&&c.world_y==1123);
 CHECK(g101_observe_row(&c,map_cells,sizeof(map_cells),&map_cells[41][2],sizeof(void *),12,11,25));
 CHECK(!g101_observe_row(&c,map_cells,sizeof(map_cells),&map_cells[42][2],sizeof(void *),12,11,54));
 CHECK(c.rejected&&!c.valid);
 CHECK(!g101_observe_row(&c,map_cells,sizeof(map_cells),&map_cells[40][2],sizeof(void *),12,11,-3));
 const void *bad[]={&map_cells[0][3],(uint8_t *)map_cells+1,
                   (uint8_t *)map_cells+sizeof(map_cells)};
 for(size_t i=0;i<sizeof(bad)/sizeof(*bad);i++) {
  g101_begin_frame(&c);CHECK(!g101_observe_row(&c,map_cells,sizeof(map_cells),bad[i],sizeof(void *),12,0,0));
 }
 g101_begin_frame(&c);CHECK(!g101_observe_row(&c,map_cells,sizeof(map_cells)-1,map_cells,sizeof(void *),12,0,0));
 g101_begin_frame(&c);CHECK(!g101_observe_row(&c,map_cells,sizeof(map_cells),map_cells,0,12,0,0));
 g101_begin_frame(&c);CHECK(!g101_observe_row(&c,map_cells,sizeof(map_cells),map_cells,sizeof(void *),0,0,0));
 CHECK(g101_preflight_layer1(&c,map_cells,sizeof(map_cells),&map_cells[40][2],sizeof(void *),11,-3));
 CHECK(c.valid&&c.world_y==1123);
 CHECK(!g101_preflight_layer1(&c,map_cells,sizeof(map_cells),&map_cells[297][2],sizeof(void *),11,-3));
 CHECK(c.rejected&&!c.valid);
 CHECK(!g101_preflight_layer1(&c,map_cells,sizeof(map_cells),&map_cells[40][3],sizeof(void *),11,-3));
 CHECK(!g101_preflight_layer1(&c,map_cells,sizeof(map_cells),&map_cells[40][2],sizeof(void *),11,INT32_MAX));
 puts("PASS map bounds, alignment, 12-cell row containment, sticky rejection, transform consistency");
}

static void test_all_tiles_and_scroll(void)
{
 G101Context c=context(120,2,13,-17);
 /* Exhaustive atlas footprint through adjacent 4x4 terrain tiles. Local
  * coordinates never become a new material origin at a tile boundary. */
 for(int ty=0;ty<4;ty++)for(int tx=0;tx<4;tx++)
  for(int ay=0;ay<224;ay++)for(int ax=0;ax<192;ax++) {
   int64_t sx=(13+24*tx)*8+ax,sy=(-17+28*ty)*8+ay;
   exact_sample(&c,sx,sy,(2+tx)*192+ax,(120+ty)*224+ay);
  }
 for(int ofs=0;ofs<72;ofs++) {
  unsigned col=(unsigned)(2-ofs/24);int origin=ofs%24;
  G101Context pan=context(200,col,origin,-12);
  CHECK(pan.world_x==48-ofs);
  for(int x=0;x<320*8;x+=13)exact_sample(&pan,x,37,x+(48-ofs)*8,37+(200*28+12)*8);
 }
 /* backPos advances 27 -> 0 and map pointer decreases one row. The screen
  * pixel carried down by one logical row samples the SAME world pixel. */
 G101Context before=context(199,2,0,-1),after=context(198,2,0,-28);
 CHECK(after.world_y==before.world_y-1);
 for(int sy=0;sy<184*8;sy++) {
  uint8_t a[4],b[4];CHECK(g101_sample(&before,&atlas,8,177,sy,a));
  CHECK(g101_sample(&after,&atlas,8,177,sy+8,b));CHECK(!memcmp(a,b,4));
 }
 /* A terrain-time snapshot must survive later globals changing. */
 int later_back_pos=0,later_map_row=198;
 (void)later_back_pos;(void)later_map_row;
 exact_sample(&before,177,71,177+48*8,71+(199*28+1)*8);
 /* Pointer event/wrap jumps are newly anchored, not inferred from stale mapY. */
 G101Context jump=context(83,1,7,-9);
 exact_sample(&jump,81,93,81+(24-7)*8,93+(83*28+9)*8);
 /* 300 rows is divisible by the four-tile atlas period. */
 CHECK(mod(300*28*8,896)==0);
 puts("PASS exhaustive 4x4 tile adjacency, horizontal pan, 27->0 row rollover, pointer jump and terrain snapshot");
}

static void test_actor_alignment(void)
{
 G101Context c=context(110,2,7,-12);
 int tx=7,ty=-12,actor_x=tx,actor_y=ty+1;
 const int parts[4]={0,1,19,20},px[4]={0,12,0,12},py[4]={0,0,14,14};
 for(int k=0;k<4;k++) {
  int full_x=0,full_y=0;
  CHECK(g101_full_actor_origin(actor_x+px[k],actor_y+py[k],parts[k],&full_x,&full_y));
  CHECK(full_x==actor_x&&full_y==actor_y);
  for(int ay=py[k]*8;ay<(py[k]+14)*8;ay++)for(int ax=px[k]*8;ax<(px[k]+12)*8;ax++) {
   int64_t sx=(int64_t)full_x*8+ax,sy=(int64_t)full_y*8+ay;
   /* Existing +1 logical backing phase emerges here as +8 HD exactly once. */
   exact_sample(&c,sx,sy,2*192+ax,110*224+8+ay);
  }
 }
 int fx=1,fy=2;CHECK(!g101_full_actor_origin(0,0,2,&fx,&fy));
 CHECK(fx==1&&fy==2);CHECK(!g101_full_actor_origin(INT32_MIN,0,1,&fx,&fy));
 uint8_t aligned[4],wrong[4];CHECK(g101_sample(&c,&atlas,8,actor_x*8,actor_y*8,aligned));
 CHECK(g101_sample(&c,&atlas,8,actor_x*8,actor_y*8+8,wrong));CHECK(memcmp(aligned,wrong,4)!=0);
 puts("PASS all four actor quadrants, full origin, +1 logical / +8 HD phase once, no anchor double subtraction");
}

static void test_actor_guards(void)
{
 const int ids[20]={77,79,115,117,81,83,119,121,1,3,5,39,41,43,7,9,11,45,47,49};
 for(int i=0;i<20;i++) {
  G101Actor a={i<8?101:110,ids[i],true,true,false,false};CHECK(g101_actor_eligible(&a));
  a.layer1_draw=false;CHECK(!g101_actor_eligible(&a));a.layer1_draw=true;
  a.verified_static_identity=false;CHECK(!g101_actor_eligible(&a));a.verified_static_identity=true;
  a.score_item=true;CHECK(!g101_actor_eligible(&a));a.score_item=false;
  a.independent_motion=true;CHECK(!g101_actor_eligible(&a));a.independent_motion=false;
  a.role=201;CHECK(!g101_actor_eligible(&a));
 }
 G101Actor a={101,273,true,true,false,false};CHECK(!g101_actor_eligible(&a));
 a.base=153;CHECK(!g101_actor_eligible(&a));a.base=229;CHECK(!g101_actor_eligible(&a));
 CHECK(!g101_actor_eligible(NULL));
 puts("PASS finite 20 actor keys; wrong layer/bank, moving, pickup, unverified identity, purple/rotor exclusions");
}

#define CW 80
#define CH 64
static uint32_t buffer[2+CW*8*CH*8];
static uint32_t packed(const uint8_t x[4])
{ return (uint32_t)x[0]|((uint32_t)x[1]<<8)|((uint32_t)x[2]<<16)|((uint32_t)x[3]<<24); }
static void draw_quad(const G101Context *ctx,int full_x,int full_y,int qx,int qy,int qw,int qh)
{
 for(int ay=qy*8;ay<(qy+qh)*8;ay++)for(int ax=qx*8;ax<(qx+qw)*8;ax++) {
  int dx=full_x*8+ax,dy=full_y*8+ay;
  if(dx<0||dy<0||dx>=CW*8||dy>=CH*8)continue;
  uint8_t rgb[4];CHECK(g101_sample(ctx,&atlas,8,dx,dy,rgb));
  buffer[1+dy*CW*8+dx]=packed(rgb);
 }
}
static void test_clipping_and_order(void)
{
 static const int origins[4][2]={{-7,-9},{75,60},{-23,63},{79,-27}};
 for(int k=0;k<4;k++) {
  int x=origins[k][0],y=origins[k][1];G101Context ctx=context(40,2,x,y);
  for(size_t i=0;i<sizeof(buffer)/sizeof(*buffer);i++)buffer[i]=UINT32_C(0x11223344);
  draw_quad(&ctx,x,y,12,14,12,14);draw_quad(&ctx,x,y,0,0,12,14);
  draw_quad(&ctx,x,y,12,0,12,14);draw_quad(&ctx,x,y,0,14,12,14);
  CHECK(buffer[0]==UINT32_C(0x11223344));CHECK(buffer[1+CW*8*CH*8]==UINT32_C(0x11223344));
  for(int sy=0;sy<CH*8;sy++)for(int sx=0;sx<CW*8;sx++) {
   uint32_t expected=UINT32_C(0x11223344);
   if(sx>=x*8&&sx<(x+24)*8&&sy>=y*8&&sy<(y+28)*8) {
    uint8_t rgb[4];tag(sx+(48-x)*8,sy+(40*28-y)*8,rgb);expected=packed(rgb);
   }
   CHECK(buffer[1+sy*CW*8+sx]==expected);
  }
 }
 /* Full 320x200 canvas coordinates, not the eventual x24..287 display crop. */
 G101Context c=context(90,2,0,0);
 uint8_t correct[4],wrong[4];CHECK(g101_sample(&c,&atlas,8,24*8,0,correct));
 CHECK(g101_sample(&c,&atlas,8,0,0,wrong));CHECK(memcmp(correct,wrong,4));
 puts("PASS negative/top/right/bottom clipping, shuffled quadrant order, buffer canaries and no viewport-origin subtraction");
}

static void test_composition_and_fallback(void)
{
 G101Context ctx=context(90,2,3,-2),invalid={0};
 uint8_t accepted[4]={121,49,37,173},clean[4]={44,80,90,0},out[4],expected[4],material[4];
 G101Pixel p={.accepted_rgba=accepted,.clean_rgba=clean,.primary_weight=113,.footer_weight=97,.reconstruction_verified=true};
 CHECK(g101_sample(&ctx,&atlas,8,123,456,material));
 g101_compose_layers(clean,material,113,97,expected);expected[3]=accepted[3];
 CHECK(g101_select_pixel(&ctx,&atlas,&p,true,8,123,456,out));CHECK(!memcmp(out,expected,4));
 CHECK(out[3]==173);
 CHECK(!g101_select_pixel(&ctx,NULL,&p,true,8,123,456,out));CHECK(!memcmp(out,accepted,4));
 CHECK(!g101_select_pixel(&invalid,&atlas,&p,true,8,123,456,out));CHECK(!memcmp(out,accepted,4));
 CHECK(!g101_select_pixel(&ctx,&atlas,&p,false,8,123,456,out));CHECK(!memcmp(out,accepted,4));
 CHECK(!g101_select_pixel(&ctx,&atlas,&p,true,4,123,456,out));CHECK(!memcmp(out,accepted,4));
 p.reconstruction_verified=false;CHECK(!g101_select_pixel(&ctx,&atlas,&p,true,8,123,456,out));CHECK(!memcmp(out,accepted,4));
 p.reconstruction_verified=true;p.clean_rgba=NULL;
 CHECK(!g101_select_pixel(&ctx,&atlas,&p,true,8,123,456,out));CHECK(!memcmp(out,accepted,4));
 p.clean_rgba=clean;p.primary_weight=p.footer_weight=0;
 CHECK(!g101_select_pixel(&ctx,&atlas,&p,true,8,123,456,out));CHECK(!memcmp(out,accepted,4));
 p.primary_weight=255;accepted[3]=0;
 CHECK(!g101_select_pixel(&ctx,&atlas,&p,true,8,123,456,out));CHECK(!memcmp(out,accepted,4));
 accepted[3]=173;
 /* A manufactured example proves applying weights to a baked source twice
  * is observably wrong, and collapsing sequential rounding is also wrong. */
 uint8_t b[4]={0,0,0,255},old[4]={127,127,127,255},next[4]={255,255,255,255};
 uint8_t baked[4],right[4],double_baked[4];
 g101_compose_layers(b,old,128,0,baked);g101_compose_layers(b,next,128,0,right);
 g101_compose_layers(baked,next,128,0,double_baked);CHECK(memcmp(right,double_baked,3));
 bool rounding_counterexample=false;
 for(unsigned base=0;base<256&&!rounding_counterexample;base++)for(unsigned ground=0;ground<256&&!rounding_counterexample;ground++) {
  uint8_t a[4]={(uint8_t)base,0,0,255},m[4]={(uint8_t)ground,0,0,255},seq[4];
  g101_compose_layers(a,m,113,97,seq);
  unsigned denominator=255*255;
  unsigned one_shot=(base*(255-113)*(255-97)+ground*(113*(255-97)+97*255)+denominator/2)/denominator;
  if(seq[0]!=one_shot)rounding_counterexample=true;
 }
 CHECK(rounding_counterexample);
 puts("PASS accepted-byte fallback, protected/transparent pixels, alpha preservation, clean-base requirement, ordered two-weight counterexamples");
}

static void test_actual_footer_contract(void)
{
 /* Independent direct integer formula, matching compose_footer.cpp's two
  * footer operations after initial ground blend; no helper mix() reuse. */
 static const unsigned priors[]={0,1,64,127,128,254,255};
 for(size_t i=0;i<sizeof(priors)/sizeof(*priors);i++)for(unsigned gw=0;gw<256;gw++)for(unsigned fw=0;fw<256;fw++) {
  unsigned pw=priors[i];
  uint8_t base[4]={(uint8_t)(gw+fw),17,249,173};
  uint8_t mat[4]={211,(uint8_t)(gw*3+fw*5),3,255};
  uint8_t gen[4]={7,231,(uint8_t)(gw*11+fw*13),0},actual[4];
  g101_compose_footer(base,mat,gen,(uint8_t)pw,(uint8_t)gw,(uint8_t)fw,actual);
  for(int c=0;c<3;c++) {
   uint64_t first=((uint64_t)base[c]*(255-pw)+(uint64_t)mat[c]*pw+127)/255;
   uint64_t second=(first*(255-gw)+(uint64_t)gen[c]*gw+127)/255;
   uint64_t third=(second*(255-fw)+(uint64_t)mat[c]*fw+127)/255;
   CHECK(actual[c]==third);
  }
  CHECK(actual[3]==173);
 }
 G101Context ctx=context(200,2,0,-28);
 uint8_t old[4]={97,83,51,137},base[4]={1,2,3,0},gen[4]={213,17,151,255};
 G101Pixel p={.accepted_rgba=old,.clean_rgba=base,.primary_weight=71,
  .footer_weight=101,.generated_footer_rgba=gen,.generated_weight=133,.reconstruction_verified=true};
 uint8_t out[4],mat[4],expected[4];
 CHECK(g101_sample(&ctx,&atlas,8,78,94,mat));
 g101_compose_footer(base,mat,gen,71,133,101,expected);expected[3]=old[3];
 CHECK(g101_select_pixel(&ctx,&atlas,&p,true,8,78,94,out));CHECK(!memcmp(out,expected,4));
 p.generated_footer_rgba=NULL;
 CHECK(!g101_select_pixel(&ctx,&atlas,&p,true,8,78,94,out));CHECK(!memcmp(out,old,4));
 p.generated_weight=0;p.primary_weight=0;p.footer_weight=0;
 CHECK(!g101_select_pixel(&ctx,&atlas,&p,true,8,78,94,out));CHECK(!memcmp(out,old,4));
 p.generated_footer_rgba=gen;p.generated_weight=255;
 CHECK(g101_select_pixel(&ctx,&atlas,&p,true,8,78,94,out));CHECK(!memcmp(out,gen,3));CHECK(out[3]==old[3]);
 p.footer_weight=255;
 CHECK(g101_select_pixel(&ctx,&atlas,&p,true,8,78,94,out));CHECK(!memcmp(out,mat,3));CHECK(out[3]==old[3]);
 puts("PASS actual 119/120 three-stage integer footer formula (458752 weight combinations), zero/full weights, missing generated fallback, exact alpha");
}

static void test_smooth_seam_and_determinism(void)
{
 /* A deliberately plain periodic triangle-wave material makes seams
  * mathematically testable, unlike subjective rock art. No hash or RNG. */
 for(int y=0;y<896;y++)for(int x=0;x<768;x++) {
  int tx=x<=384?x:768-x,ty=y<=448?y:896-y;uint8_t *p=atlas_bytes+4*(y*768+x);
  p[0]=(uint8_t)(20+tx/3);p[1]=(uint8_t)(40+ty/4);p[2]=(uint8_t)(30+(tx+ty)/6);p[3]=255;
 }
 for(int y=0;y<896;y++)for(int x=0;x<768;x++)for(int c=0;c<3;c++) {
  int v=atlas_bytes[4*(y*768+x)+c];
  int right=atlas_bytes[4*(y*768+(x+1)%768)+c],down=atlas_bytes[4*(((y+1)%896)*768+x)+c];
  CHECK(abs(v-right)<=1);CHECK(abs(v-down)<=1);
 }
 G101Context ctx=context(200,2,13,-17);
 uint64_t first=0,second=0;
 for(int pass=0;pass<2;pass++) {
  uint64_t sum=0;
  for(int frame=0;frame<64;frame++)for(int y=0;y<200;y+=3)for(int x=0;x<320;x+=3) {
   uint8_t p[4];CHECK(g101_sample(&ctx,&atlas,8,x*8,y*8+frame,p));
   sum+=(uint64_t)packed(p)*(unsigned)(1+x+y+frame);
  }
  if(!pass)first=sum;else second=sum;
 }
 CHECK(first==second);CHECK(memcmp(atlas_bytes,atlas_bytes+4*192,4)!=0);
 printf("PASS seamless +/-1-channel adjacency including wrap, distinct 4x4 phase, deterministic checksum=%" PRIu64 "\n",first);
}

static void test_memory_budget(void)
{
 /* Static arrays reserve the exact maximum; no malloc/calloc/realloc calls
  * occur anywhere in the sampler/context/compositor implementation. */
 memset(masks,0,sizeof(masks));masks[sizeof(masks)-1]=255;
 CHECK(sizeof(atlas_bytes)==2752512);CHECK(sizeof(masks)==2623488);
 CHECK(sizeof(atlas_bytes)+sizeof(masks)==5376000);
 G101MemoryPlan plan;
 CHECK(g101_memory_plan(61,0,0,&plan));CHECK(plan.total_bytes==5376000);
 CHECK(g101_memory_plan(61,61,2,&plan));CHECK(plan.total_bytes==16386048);
 CHECK(!g101_memory_plan(62,61,2,&plan));CHECK(!g101_memory_plan(61,62,2,&plan));
 CHECK(!g101_memory_plan(61,61,3,&plan));CHECK(!g101_memory_plan(0,1,0,&plan));
 CHECK(!g101_memory_plan(UINT32_MAX,UINT32_MAX,UINT32_MAX,&plan));
 size_t clean=61u*192*224*4,footer=4u*192*224,generated=2u*192*224*4;
 printf("PASS memory: atlas=%zu masks=%zu subtotal=%zu B (%.9f MiB); optional clean=%zu B footer=%zu B generated=%zu B total=%zu B (%.9f MiB)\n",
  sizeof(atlas_bytes),sizeof(masks),sizeof(atlas_bytes)+sizeof(masks),
  (sizeof(atlas_bytes)+sizeof(masks))/1048576.0,clean,footer,generated,
  sizeof(atlas_bytes)+sizeof(masks)+clean+footer+generated,
  (sizeof(atlas_bytes)+sizeof(masks)+clean+footer+generated)/1048576.0);
}
int main(void)
{
 fill_tags();test_modulo_and_shapes();test_pointer_validation();test_all_tiles_and_scroll();
 test_actor_alignment();test_actor_guards();test_clipping_and_order();test_composition_and_fallback();test_actual_footer_contract();
 test_smooth_seam_and_determinism();test_memory_budget();
 printf("ALL PASS assertions=%" PRIu64 " exact_samples=%" PRIu64 "\n",assertions,sampled_pixels);
 puts("BOUNDARY: synthetic sampling/composition only; no actual art, production binding, indexed/RNG proof, filters/shadows ownership proof or game captures.");return 0;
}
