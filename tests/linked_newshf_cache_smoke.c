/* Two-case cached Present/root switch smoke. Frozen full matrix remains separate. */
#define main historical_newshf_main
#include "newshf_compositor_validation.c"
#undef main
int main(int argc,char **argv)
{
 CHECK(argc==2);resource_root=argv[1];read_exact(bank_original,sizeof(bank_original));read_exact(original_records,sizeof(original_records));
 for(unsigned p=0;p<3;p++){Uint8 r[77];read_exact(r,77);current_record=171+p;record_load(r);}
 read_exact(normal_palette,sizeof(normal_palette));Uint32 bank_size;read_exact(&bank_size,4);spriteSheet9.size=bank_size;spriteSheet9.data=malloc(bank_size);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,bank_size);CHECK(fgetc(stdin)==EOF);
 setup(4);current_record=173;current_slot=0;unsigned avail=JE_makeEnemy(enemy,current_record,0);CHECK(avail==0);enemyAvail[0]=avail;
 CHECK(newshf_validation_slots[0].role);enemy[0].ex=110;enemy[0].ey=80;enemy[0].enemycycle=2;render_mirror_newshf_validation_observe(0);
 quartet();final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);
 CHECK(ready&&last_output_valid&&global_newshf_cached&&global_newshf_linked_loaded&&global_newshf_linked_good&&global_newshf_used_resources==0x7e00u);
 SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,1280,800,32,SDL_PIXELFORMAT_ARGB8888);CHECK(target);
 SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(target);CHECK(renderer);CHECK(!game_probe_skip);
 CHECK(render_mirror_present(renderer,VGAScreenSeg,NULL));CHECK(last_output_valid&&global_newshf_cached);
 global_newshf_rgba[14][0]^=1;
 CHECK(!render_mirror_present(renderer,VGAScreenSeg,NULL));CHECK(!ready&&!last_output_valid&&!global_newshf_cached);
 char oldonly[4096];snprintf(oldonly,sizeof(oldonly),"%s/old-only",resource_root);
 CHECK(render_mirror_set_global_assets(oldonly));
 CHECK(!global_newshf_loaded&&!global_newshf_good&&!global_newshf_linked_loaded&&!global_newshf_linked_good&&!global_newshf_used_resources);
 for(unsigned i=0;i<GLOBAL_NEWSHF_RESOURCE_COUNT;i++)CHECK(!global_newshf_rgba[i]);
 ++cases;SDL_FillRect(game_screen,NULL,0x1b);SDL_FillRect(VGAScreenSeg,NULL,0x1b);enemyAvail[0]=1;render_mirror_begin();
 birth(0,1,110,80,0);quartet();final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);
 CHECK(ready&&last_output_valid&&global_newshf_cached&&global_newshf_used_resources==0x1ffu);
 CHECK(!global_newshf_linked_loaded&&!global_newshf_linked_good);CHECK(render_mirror_present(renderer,VGAScreenSeg,NULL));CHECK(last_output_valid&&global_newshf_cached);
 render_mirror_release_texture();SDL_DestroyRenderer(renderer);SDL_FreeSurface(target);
 printf("PASS linked cache smoke: %u cases %u assertions; actual SDL software Present, post-Present phase14 corruption, actual root switch and old-only Present\n",cases,checks);return 0;
}
