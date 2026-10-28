/* Actual full renderer TU/provider, production background blitter and170 borrower.
 * One test-only map pointer selects original356 under a controlled real170 actor.
 * No source pixels, payloads or production controls are changed in positives. */
#include "backgrnd.h"
#include "video_scale.h"
static Uint16 cross_lookup[72];
static Uint8 cross_sources[72][672],cross_map[4200];
static unsigned cross_slot,cross_samples,cross_soft,cross_empty;
static uint64_t cross_provider(unsigned output_scale)
{
 s_setup(8);set_scaler_by_name(output_scale==2?"2x":"4x");CHECK(init_scaler(scaler));
 SDL_PumpEvents();SDL_Renderer *renderer=SDL_GetRenderer(main_window);CHECK(renderer);
 CHECK(SDL_RenderSetViewport(renderer,NULL)==0);
 game_probe_enabled=true;game_probe_scene_assets=2;game_probe_assets=resource_root;
 terrain_file='Y';filterFade=false;levelFilter=levelBrightness=-99;memset(smoothies,0,sizeof(smoothies));
 shapesy_map_reset();
 for(unsigned i=0;i<72;i++){memcpy(megaData1.shapes[i].sh,cross_sources[i],672);shapesy_bind(1,cross_lookup[i],megaData1.shapes[i].sh);if(cross_lookup[i]==356)cross_slot=i;}
 CHECK(shapesy_sources_valid()&&shapesy_bronze356_sources_valid());
 for(unsigned y=0;y<300;y++)for(unsigned x=0;x<14;x++)megaData1.mainmap[y][x]=megaData1.shapes[cross_map[y*14+x]].sh;
 /* Positionworld96,55 exactly matchesactor102,62 minusnativeanchor6,7. */
 megaData1.mainmap[282][4]=megaData1.shapes[cross_slot].sh;
 render_mirror_begin();CHECK(active&&global_newshf_frame);
 CHECK(SDL_FillRect(game_screen,NULL,0)==0);render_mirror_rect(game_screen,NULL);CHECK(shapesy_clear_proof);
 mapXPos=0;backPos=27;mapXbpPos=1;mapYPos=&megaData1.mainmap[280][0]+11;
 render_mirror_shapesy_layer1(game_screen,&megaData1.mainmap[280][0],0,-1);
 CHECK(shapesy_pass.live&&shapesy_pass.bronze356&&!shapesy_pass.platform);
 for(unsigned r=0;r<8;r++)blit_background_row(game_screen,0,(int)r*28-1,&megaData1.mainmap[280+r][0]);
 render_mirror_shapesy_end();CHECK(!reject_reason&&shapesy_bronze356.used&&!shapesy_platform_used);
 uint64_t serial=shapesy_borrow_ready();CHECK(serial&&shapesy_borrow_check(serial));
 VideoOutputGeometry geometry;CHECK(video_output_geometry(&geometry)&&geometry.scale==(int)output_scale);
 for(unsigned y=0;y<224;y++)for(unsigned x=0;x<192;x++){
  size_t n=(size_t)(55*8+y)*canvas->w+96*8+x;const Uint8 *p=shapesy_bronze356.member.rgba+4*(y*192+x);
  Uint32 color=*pixel(canvas,96*8+x,55*8+y),want=0xff000000u|(Uint32)p[0]<<16|(Uint32)p[1]<<8|p[2];
  CHECK(p[3]==255&&color==want&&hd_owner[n]);CHECK(shapesy_borrow_sample(serial,n,color));
  CHECK(!shapesy_borrow_sample(serial,n,color^1u)&&!shapesy_borrow_sample(serial+1,n,color));++cross_samples;
 }
 return serial;
}
static void cross_draw(unsigned pose,uint64_t serial)
{
 s_birth(0,pose,102,62,0);quartet();
 CHECK(global_newshf_dual_preflight_state[0]==2&&global_newshf_dual_shapesy_serial[0]==serial);
 CHECK(global_newshf_shapesy_dependency==serial&&!global_newshf_cyan_dependency);
 CHECK(global_newshf_contributed&&!global_newshf_fault&&global_newshf_used_resources==UINT64_C(0x70000000000));
 unsigned local_soft=0,local_empty=0;Uint8 native[4][336]={{0}};const unsigned parts[]={0,1,19,20};
 for(unsigned q=0;q<4;q++)CHECK(decode_tile(enemySpriteSheets[0],newshf_profiles[21].bases[pose-1]+parts[q],native[q],native[q]+168,12,0,0));
 for(unsigned y=0;y<224;y++)for(unsigned x=0;x<192;x++){
  const Uint8 *under=shapesy_bronze356.member.rgba+4*(y*192+x),*art=global_newshf_rgba[39+pose]+4*(y*192+x);
  Uint32 color=0xff000000u|(Uint32)under[0]<<16|(Uint32)under[1]<<8|under[2];
  CHECK(*pixel(canvas,96*8+x,55*8+y)==alpha_oracle(color,art));
  unsigned nx=x/8,ny=y/8,q=(ny>=14?2u:0u)+(nx>=12?1u:0u);bool covered=native[q][168+(ny%14)*12+nx%12]!=0;
  if(covered&&art[3]<255){++local_soft;if(!art[3])++local_empty;}
 }
 CHECK(local_soft>0&&local_empty>0);cross_soft+=local_soft;cross_empty+=local_empty;
 CHECK(shapesy_borrow_check(serial));
}
static void cross_output_oracle(unsigned pose)
{
 for(unsigned y=0;y<224;y++)for(unsigned x=0;x<192;x++){
  const Uint8 *under=shapesy_bronze356.member.rgba+4*(y*192+x),*art=global_newshf_rgba[39+pose]+4*(y*192+x);
  Uint32 color=0xff000000u|(Uint32)under[0]<<16|(Uint32)under[1]<<8|under[2];
  CHECK(*pixel(output,(96-24)*8+x,55*8+y)==alpha_oracle(color,art));
 }
}
int main(int argc,char **argv)
{
 CHECK(argc==2);resource_root=argv[1];
 read_exact(bank_original,sizeof(bank_original));read_exact(original_records,sizeof(original_records));
 read_exact(aircraft_record,sizeof(aircraft_record));read_exact(neighbor165_record,sizeof(neighbor165_record));read_exact(neighbor166_record,sizeof(neighbor166_record));read_exact(neighbor169_record,sizeof(neighbor169_record));read_exact(large_bank,sizeof(large_bank));read_exact(large_record,sizeof(large_record));
 read_exact(normal_palette,sizeof(normal_palette));Uint32 n;read_exact(&n,4);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);
 read_exact(cross_lookup,sizeof(cross_lookup));read_exact(cross_sources,sizeof(cross_sources));read_exact(cross_map,sizeof(cross_map));CHECK(fgetc(stdin)==EOF);
 fullscreen_display=-1;set_scaler_by_name("4x");init_video();CHECK(set_scaling_mode_by_name("Integer"));
 unsigned positives=0,negatives=0;
 for(unsigned scale=2;scale<=4;scale+=2)for(unsigned pose=1;pose<=3;pose++){
  uint64_t serial=cross_provider(scale);cross_draw(pose,serial);finish_valid();
  CHECK(global_newshf_cached&&shapesy_borrow_check(serial));cross_output_oracle(pose);global_newshf_check_cache();CHECK(ready&&last_output_valid);cross_output_oracle(pose);
  ++positives;printf("POSITIVE pose=%u output=%u provider_serial=%llu samples=43008 actual_soft_preflight_draw_final_cache=PASS\n",pose,scale,(unsigned long long)serial);
 }
 for(unsigned cached=0;cached<2;cached++)for(unsigned pose=1;pose<=3;pose++){
  uint64_t serial=cross_provider(4);cross_draw(pose,serial);if(cached)finish_valid();
  CHECK(global_newshf_shapesy_dependency==serial&&shapesy_borrow_check(serial));shapesy_bronze356.member.rgba[0]^=1;
  CHECK(!shapesy_borrow_check(serial));
  if(cached){global_newshf_check_cache();CHECK(!ready&&!last_output_valid);}else finish_invalid();
  ++negatives;printf("NEGATIVE pose=%u cached=%u provider_payload_rejected_by_consumer=PASS\n",pose,cached);
 }
 printf("BRONZE356_AIRCRAFT170_BORROW PASS positives=%u negatives=%u provider_samples=%u soft_subpixels=%u empty_native_subpixels=%u checks=%u; actual provider/borrower, controlled notnatural\n",positives,negatives,cross_samples,cross_soft,cross_empty,checks);
 return 0;
}
