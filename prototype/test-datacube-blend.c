/* Real-source compositor units, with synthetic HD underlay ownership.
 * Never calls engine main or simulates a natural pickup. The original indexed
 * sprite decoder and actual newsh6.shp glyph bytes are used unmodified. */
#ifndef MIRROR_SOURCE
#define MIRROR_SOURCE "render_mirror.c"
#endif
#include MIRROR_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned checks;
#define CHECK(v) do { ++checks; if (!(v)) { fprintf(stderr,"FAIL %d: %s\n",__LINE__,#v); exit(1); } } while (0)
static unsigned char *read_file(const char *path,size_t *size)
{
 FILE *f=fopen(path,"rb");CHECK(f);CHECK(!fseek(f,0,SEEK_END));long n=ftell(f);CHECK(n>0);rewind(f);
 unsigned char *p=malloc((size_t)n);CHECK(p);CHECK(fread(p,1,(size_t)n,f)==(size_t)n);fclose(f);*size=(size_t)n;return p;
}

static void seed_underlay(bool talon)
{
 memset(game_screen->pixels,0x8b,(size_t)game_screen->pitch*200);
 render_mirror_begin();CHECK(active&&manual_hd_lease);
 /* Connected, overlapping HD background rectangles plus the supported ship.
  * This specifically exercises the existing local-restore overlap closure. */
 region_count=0;
 for(int y=0;y<200;y+=20)for(int x=0;x<320;x+=20)
  regions[region_count++]=(HdRegion){{x,y,21,21},ASSET_SHAPESZ,101,MIRROR_NORMAL,true};
 if(talon)regions[region_count++]=(HdRegion){{96,96,24,28},9,233,MIRROR_NORMAL,true};
 memset(hd_owner,1,(size_t)canvas->w*canvas->h);
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++)
  ((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch))[x]=0xff284060u+(unsigned)(x%game_probe_density)*0x030201u;
}

static void draw_case(SDL_Surface *reference,bool talon,bool known,bool wrong_sheet,bool nonmonotone,int x,int y,bool want_restore)
{
 seed_underlay(talon);game_probe_known_blend=known;
 Uint32 saved=rgb_palette[0x77];if(nonmonotone)rgb_palette[0x77]=0;
 Sprite2_array bank=explosionSpriteSheet;
 Uint8 *other=NULL;if(wrong_sheet){other=malloc(bank.size);CHECK(other);memcpy(other,bank.data,bank.size);bank.data=other;}
 memcpy(reference->pixels,game_screen->pixels,(size_t)game_screen->pitch*200);
 active=false;blit_sprite2_blend(reference,x,y,bank,266);active=true;
 blit_sprite2_blend(game_screen,x,y,bank,266);
 CHECK(memcmp(reference->pixels,game_screen->pixels,(size_t)game_screen->pitch*200)==0);
 CHECK(memcmp(expected,game_screen->pixels,320*200)==0);
 CHECK((local_regions>0)==want_restore);
 CHECK((local_blocks>0)==want_restore);
 if(want_restore)CHECK(local_blocks==320*200&&expanded_regions>0);
 else CHECK(memchr(hd_owner,0,(size_t)canvas->w*canvas->h)==NULL);
 CHECK(manual_hd_lease&&manual_hd_scope());
 CHECK(!reject_reason);CHECK(!game_probe_enabled&&!asset_debug_enabled&&game_probe_tick==0);
 free(other);game_probe_known_blend=true;
 for(int row=0;row<184;row++)memcpy((Uint8 *)VGAScreenSeg->pixels+row*VGAScreenSeg->pitch,
  (Uint8 *)game_screen->pixels+row*game_screen->pitch+24,264);
 render_mirror_finish(true);
 CHECK(ready&&manual_hd_lease);
 CHECK(nonmonotone ? reject_reason&&strstr(all_rejections,"hd-palette-change") : !reject_reason);
 CHECK(last_output_scene_hd==!want_restore);
 rgb_palette[0x77]=saved;
}

int main(int argc,char **argv)
{
 if(argc==2&&!strcmp(argv[1],"--predicate")) {
  for(unsigned i=0;i<400;i++)for(unsigned h=0;h<256;h++)putchar(recognized_contact_effect(i,h)?'1':'0');
  return 0;
 }
 CHECK(argc==5);int density=atoi(argv[3]);bool baseline=atoi(argv[4])!=0;
 CHECK(density==4||density==8);
 size_t n;explosionSpriteSheet.data=read_file(argv[1],&n);explosionSpriteSheet.size=n;
 unsigned char *pal=read_file(argv[2],&n);CHECK(n>=6*768);
 for(int i=0;i<256;i++){Uint8 *p=pal+5*768+3*i;rgb_palette[i]=0;for(int c=0;c<3;c++)rgb_palette[i]|=(Uint32)((p[c]<<2)|(p[c]>>4))<<((2-c)*8);}free(pal);
 CHECK(effect_ramp_monotone(0x70));CHECK(recognized_value_effect(266));
 CHECK(recognized_contact_effect(266,0x70)==!baseline);
 CHECK(!recognized_contact_effect(265,0x70));CHECK(!recognized_contact_effect(266,0x60));
 CHECK(recognized_contact_effect(145,0x70));CHECK(recognized_contact_effect(185,0x80));
 CHECK(recognized_contact_effect(204,0x90));CHECK(!recognized_contact_effect(226,0x70));
 manual_hd_enabled=true;game_probe_density=density;game_probe_local_blend=game_probe_known_blend=true;
 episodeNum=1;lvlFileNum=9;
 VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 game_screen=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 SDL_Surface *reference=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 CHECK(VGAScreenSeg&&game_screen&&reference&&game_screen->pitch==320);VGAScreen=game_screen;
 render_mirror_hud_start(VGAScreenSeg);CHECK(manual_hd_lease);
 for(int frame=0;frame<14;frame++)draw_case(reference,true,true,false,false,100,100,baseline);
 /* Existing fallback controls stay intact. The unrelated266 hues/IDs above
  * are rejected, as are missing Talon, unknown sheet and nonmonotone ramp. */
 draw_case(reference,false,true,false,false,100,100,true);
 draw_case(reference,true,false,false,false,100,100,true);
 draw_case(reference,true,true,true,false,100,100,true);
 draw_case(reference,true,true,false,true,100,100,true);
 draw_case(reference,true,true,false,false,0,0,baseline);
 draw_case(reference,true,true,false,false,308,186,baseline);
 render_mirror_hud_reset();CHECK(!manual_hd_lease);
 printf("PASS density=%d baseline=%d cases=20 checks=%u indexed-original-equal\n",density,baseline,checks);
 return 0;
}
