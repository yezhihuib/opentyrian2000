/* Controlled finite356 diagnostics; actual map/indexed blitter and role202 path.
 * Deliberate mutations live only in the standalone diagnostic process. */
static unsigned bronze_slot(void)
{for(unsigned s=0;s<72;s++)if(lookup[s]==356)return s;assert(0);return 0;}
static void bronze_frame(unsigned row,unsigned col,int phase,int scale)
{
 mock_geometry.scale=scale;mock_geometry.footprint=8/scale;mock_geometry.dst=(SDL_Rect){0,0,320*scale,200*scale};
 mock_geometry.window_w=mock_geometry.output_w=320*scale;mock_geometry.window_h=mock_geometry.output_h=200*scale;
 shapesy_frame_reset();mapXPos=0;backPos=phase;mapXbpPos=1;mapYPos=&megaData1.mainmap[row][col]+11;
 clear();render_mirror_shapesy_layer1(&surface,&megaData1.mainmap[row][col],0,phase-28);
}
static unsigned bronze_verify_row(unsigned row,unsigned col,int y,bool replaced)
{
 unsigned count=0;
 for(unsigned t=0;t<12;t++){
  const Uint8 *s=megaData1.mainmap[row][col+t];bool bronze=shapesy_id(s)==356;
  for(unsigned i=0;i<672;i++){
   int x=t*24+i%24,dy=y+i/24;if(dy<0||dy>=200)continue;
   assert(pixels[dy*320+x]==s[i]);
   if(!bronze)continue;
   count++;
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    unsigned at=(dy*8+sy)*2560+x*8+sx;
    if(!replaced){assert(canvas_pixels[at]==palette_rgb(s[i])&&!hd_owner[at]);continue;}
    const Uint8 *p=shapesy_bronze356.member.rgba+((i/24*8+sy)*192+(i%24*8+sx))*4;
    assert(p[3]==255&&canvas_pixels[at]==(0xff000000u|p[0]<<16|p[1]<<8|p[2])&&hd_owner[at]==1);
   }
  }
 }
 return count;
}
static void bronze_draw_eight(unsigned row,unsigned col,int phase,bool replaced)
{
 assert(shapesy_pass.live);
 for(unsigned r=0;r<8;r++){
  blit_background_row(&surface,0,(int)r*28+phase-28,&megaData1.mainmap[row+r][col]);
  bronze_verify_row(row+r,col,(int)r*28+phase-28,replaced);
 }
 render_mirror_shapesy_end();assert(!reject_reason&&shapesy_frame_check()&&shapesy_cache_valid());
}
static void bronze_controlled(void)
{
 registry();megaData1.mainmap[280][0]=megaData1.shapes[bronze_slot()].sh;
 bronze_frame(280,0,27,4);assert(shapesy_pass.live&&shapesy_pass.bronze356);
 bronze_draw_eight(280,0,27,true);assert(shapesy_bronze356.used&&shapesy_borrow_ready());
}
static void bronze_rejected_optional(void)
{
 registry();megaData1.mainmap[280][0]=megaData1.shapes[bronze_slot()].sh;
 bronze_frame(280,0,27,4);assert(shapesy_pass.live&&shapesy_pass.platform&&!shapesy_pass.bronze356);
 bronze_draw_eight(280,0,27,false);assert(shapesy_platform_used&&!shapesy_bronze356.used);
 puts("bronze356 rejected independently; old28 contribution and native356 preserved PASS");
}
static void bronze_only(void)
{
 bronze_controlled();assert(!shapesy_platform_used&&shapesy_bronze356.used);
 puts("bronze356 independent of missing old28 resources PASS");
}
static void checks(void)
{
 assert(shapesy_member(356)==-1);unsigned placements=0,visible=0;
 for(unsigned row=0;row<300;row++)for(unsigned col=0;col<14;col++)if(lookup[map_indices[row*14+col]]==356){
  placements++;
  for(int scale=2;scale<=4;scale+=2){
   registry();unsigned start=row?row-1:0;if(start>292)start=292;unsigned first=col>11?col-11:0;
   bronze_frame(start,first,27,scale);assert(shapesy_pass.live&&shapesy_pass.platform&&shapesy_pass.bronze356);
   assert(shapesy_world.members[row][col]==-1&&shapesy_world_plane(col*24,row*28)==-1);
   for(unsigned r=0;r<8;r++){
    blit_background_row(&surface,0,(int)r*28-1,&megaData1.mainmap[start+r][first]);
    visible+=bronze_verify_row(start+r,first,(int)r*28-1,true);
   }
   render_mirror_shapesy_end();assert(!reject_reason&&shapesy_frame_check()&&shapesy_cache_valid()&&shapesy_bronze356.used);
   assert(shapesy_borrow_ready());
   /* Contour reconstruction must never touch this whole generated tile. */
   for(unsigned r=0;r<8;r++)bronze_verify_row(start+r,first,(int)r*28-1,true);
  }
 }
 assert(placements==27&&visible);
 /* A bad optional source at initial binding never disables valid old28. */
 shapesy_map_reset();for(unsigned s=0;s<72;s++){
  memcpy(megaData1.shapes[s].sh,original_sources[s],672);if(lookup[s]==356)megaData1.shapes[s].sh[2]^=1;
  shapesy_bind(1,lookup[s],megaData1.shapes[s].sh);
 }
 for(unsigned y=0;y<300;y++)for(unsigned x=0;x<14;x++)megaData1.mainmap[y][x]=megaData1.shapes[map_indices[y*14+x]].sh;
 assert(shapesy_sources_valid()&&!shapesy_bronze356_sources_valid());
 bronze_frame(280,0,27,4);assert(shapesy_pass.platform&&!shapesy_pass.bronze356);
 for(unsigned r=0;r<8;r++)blit_background_row(&surface,0,(int)r*28-1,&megaData1.mainmap[280+r][0]);
 render_mirror_shapesy_end();assert(!reject_reason&&shapesy_platform_used&&!shapesy_bronze356.used&&shapesy_frame_check());
 /* Every356 alias, including offscreen duplicate slots, participates once used. */
 registry();shapesy_map_reset();for(unsigned s=0;s<72;s++){
  memcpy(megaData1.shapes[s].sh,original_sources[s==71?bronze_slot():s],672);
  shapesy_bind(1,s==71?356:lookup[s],megaData1.shapes[s].sh);
 }
 assert(shapesy_bronze356_sources_valid());megaData1.shapes[71].sh[671]^=1;
 assert(!shapesy_bronze356_sources_valid()&&shapesy_sources_valid());
 /* Resource/source/metadata/root mutations cannot survive final/cached proof. */
 const char *valid_root=game_probe_assets;
 for(unsigned kind=0;kind<11;kind++){
  bronze_controlled();assert(shapesy_bronze356_cache_valid()&&shapesy_borrow_check(shapesy_borrow.serial));
  if(kind==0)shapesy_bronze356.member.rgba[0]^=1;
  if(kind==1)megaData1.shapes[bronze_slot()].sh[2]^=1;
  if(kind==2)shapesy_bronze356.source[2]^=1;
  if(kind==3)shapesy_bronze356.member.index=355;
  if(kind==4)shapesy_bronze356.member.anchor_x=1;
  if(kind==5)shapesy_bronze356.member.density=4;
  if(kind==6)shapesy_bronze356.root[0]^=1;
  if(kind==7)game_probe_assets="";
  if(kind==8)shapesy_resources.generation++;
  if(kind==9)rgb_palette[22]^=1;
  if(kind==10)shapesy_bronze356.member.rgba[3]=0;
  assert(!shapesy_frame_check()&&!shapesy_borrow_check(shapesy_borrow.serial));
  game_probe_assets=valid_root;if(kind==9)rgb_palette[22]^=1;
 }
 /* Midpass source mutation is rejected by the real per-pixel lease. */
 registry();megaData1.mainmap[280][0]=megaData1.shapes[bronze_slot()].sh;
 bronze_frame(280,0,27,4);unsigned bits=shapesy_row(&surface,0,-1,&megaData1.mainmap[280][0],MIRROR_NORMAL);assert(bits&1);
 Uint8 *s=megaData1.shapes[bronze_slot()].sh;s[24]^=1;bool qualified=true;
 assert(!shapesy_native_water(&surface,pixels,s[24],MIRROR_NORMAL,true,&qualified)&&!qualified&&reject_reason);
 /* All inherited context gates remain classic before any356 contribution. */
 for(unsigned kind=0;kind<5;kind++){
  registry();megaData1.mainmap[280][0]=megaData1.shapes[bronze_slot()].sh;
  if(kind==0)game_probe_density=4;if(kind==1)rgb_palette[22]^=1;if(kind==2)smoothies[1]=true;if(kind==3)filterFade=true;if(kind==4)mock_geometry_available=false;
  bronze_frame(280,0,27,4);assert(!shapesy_pass.live);
  game_probe_density=8;if(kind==1)rgb_palette[22]^=1;smoothies[1]=false;filterFade=false;mock_geometry_available=true;
 }
 /* Every source-used bronze/earth palette entry is bound, including RGB only. */
 const unsigned used_indices[]={1,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31};
 for(unsigned n=0;n<sizeof(used_indices)/sizeof(used_indices[0]);n++){
  unsigned color=used_indices[n];bronze_controlled();rgb_palette[color]^=0x000100u;
  assert(!shapesy_frame_check()&&!shapesy_borrow_check(shapesy_borrow.serial));rgb_palette[color]^=0x000100u;
  registry();rgb_palette[color]^=0x000001u;bronze_frame(280,0,27,4);assert(!shapesy_pass.live);rgb_palette[color]^=0x000001u;
 }
 bronze_controlled();shapesy_map_reset();assert(!shapesy_bronze356.member.rgba&&!shapesy_bronze356.used&&!shapesy_borrow_ready());
 printf("bronze356 PASS placements=%u scales=2/4 visible_native_cells=%u cache_mutations=11; old28 contour domain unchanged; INDEX8 unchanged\n",placements,visible);
}
int main(int argc,char **argv)
{
 static SDL_PixelFormat argb={.format=SDL_PIXELFORMAT_ARGB8888,.BitsPerPixel=32,.BytesPerPixel=4};
 canvas->format=&argb;
 assert(argc==4);game_probe_assets=argv[2];surface.clip_rect=(SDL_Rect){0,0,320,200};asteroid_hd_enabled=false;
 FILE *f=fopen(argv[1],"rb");assert(f);assert(fread(lookup,2,72,f)==72);assert(fread(original_sources,672,72,f)==72);assert(fread(map_indices,1,4200,f)==4200);
 for(unsigned i=0;i<256;i++){Uint8 p[3];assert(fread(p,1,3,f)==3);rgb_palette[i]=p[0]<<16|p[1]<<8|p[2];}assert(fgetc(f)==EOF);fclose(f);
 if(!strcmp(argv[3],"reject"))bronze_rejected_optional();else if(!strcmp(argv[3],"bronze-only"))bronze_only();else checks();
 shapesy_shutdown();return 0;
}
