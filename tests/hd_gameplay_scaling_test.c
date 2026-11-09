/* SPDX-License-Identifier: GPL-2.0-or-later
 * Real SDL software-renderer checks with synthetic HD pixels, not game data. */
#include "hd_gameplay_scaling.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { OW = 2048, OH = 1600 };
static unsigned checks, cases, changed_cases;
static int reject_linear, reject_nearest;
static unsigned mode_calls;
static SDL_ScaleMode call_mode[4];
#define CHECK(x) do { ++checks; if (!(x)) { fprintf(stderr,"%s:%d: %s: %s\n",__FILE__,__LINE__,#x,SDL_GetError()); exit(1); } } while (0)
int __real_SDL_SetTextureScaleMode(SDL_Texture *, SDL_ScaleMode);
int __wrap_SDL_SetTextureScaleMode(SDL_Texture *texture, SDL_ScaleMode mode)
{
    if (mode_calls < 4) call_mode[mode_calls] = mode;
    ++mode_calls;
    if ((mode == SDL_ScaleModeLinear && reject_linear) ||
        (mode == SDL_ScaleModeNearest && reject_nearest)) return -1;
    return __real_SDL_SetTextureScaleMode(texture, mode);
}
static void output(SDL_Renderer *renderer, SDL_Texture *texture,
                   const SDL_Rect *destination, Uint32 *pixels)
{
    CHECK(SDL_SetRenderDrawColor(renderer, 9, 11, 17, 255) == 0);
    CHECK(SDL_RenderClear(renderer) == 0);
    CHECK(SDL_RenderCopy(renderer, texture, NULL, destination) == 0);
    SDL_RenderPresent(renderer);
    CHECK(SDL_RenderReadPixels(renderer, NULL, SDL_PIXELFORMAT_ARGB8888, pixels, OW*4) == 0);
}
static void save(const char *directory, const char *name, const Uint32 *pixels)
{
    char path[2048];
    if (!directory) return;
    CHECK(snprintf(path, sizeof(path), "%s/%s.ppm", directory, name) < (int)sizeof(path));
    FILE *file = fopen(path, "wb"); CHECK(file);
    fprintf(file, "P6\n1001 633\n255\n");
    for (int y=0; y<633; ++y) for (int x=0; x<1001; ++x) {
        Uint32 p = pixels[(y+13)*OW+x+17];
        unsigned char rgb[3] = { (unsigned char)(p>>16), (unsigned char)(p>>8), (unsigned char)p };
        CHECK(fwrite(rgb, 1, 3, file) == 3);
    }
    CHECK(fclose(file) == 0);
}
static void check_mode(SDL_Renderer *renderer, SDL_Texture *texture,
                       SDL_Rect destination, SDL_ScaleMode expected)
{
    SDL_Rect viewport_before, viewport_after, clip_before, clip_after;
    float sx, sy, after_x, after_y;
    SDL_ScaleMode actual;
    SDL_BlendMode blend;
    SDL_RenderGetViewport(renderer, &viewport_before);
    SDL_RenderGetClipRect(renderer, &clip_before);
    SDL_bool clipping = SDL_RenderIsClipEnabled(renderer);
    SDL_RenderGetScale(renderer, &sx, &sy);
    mode_calls = 0;
    CHECK(video_hd_set_texture_scale(texture, renderer, &destination) == 0);
    CHECK(mode_calls == 1 && call_mode[0] == expected);
    CHECK(SDL_GetTextureScaleMode(texture, &actual) == 0 && actual == expected);
    CHECK(SDL_GetTextureBlendMode(texture, &blend) == 0 && blend == SDL_BLENDMODE_NONE);
    SDL_RenderGetViewport(renderer, &viewport_after);
    SDL_RenderGetClipRect(renderer, &clip_after);
    SDL_RenderGetScale(renderer, &after_x, &after_y);
    CHECK(memcmp(&viewport_before, &viewport_after, sizeof(SDL_Rect)) == 0);
    CHECK(memcmp(&clip_before, &clip_after, sizeof(SDL_Rect)) == 0);
    CHECK(SDL_RenderIsClipEnabled(renderer) == clipping);
    CHECK(sx == after_x && sy == after_y);
}
int main(int argc, char **argv)
{
    CHECK(SDL_Init(SDL_INIT_VIDEO) == 0);
    SDL_Surface *canvas = SDL_CreateRGBSurfaceWithFormat(0, OW, OH, 32, SDL_PIXELFORMAT_ARGB8888);
    CHECK(canvas);
    SDL_Renderer *renderer = SDL_CreateSoftwareRenderer(canvas); CHECK(renderer);
    Uint32 *old = malloc((size_t)OW*OH*4), *actual = malloc((size_t)OW*OH*4), *linear = malloc((size_t)OW*OH*4);
    CHECK(old && actual && linear);
    const int sizes[][2] = {{320,200},{640,400},{960,600},{1280,800},{1920,1200},{1280,600},
        {1001,633},{1365,767},{1280,720},{320,201},{641,400},{640,401},{160,100}};
    for (unsigned density=4; density<=8; density+=4) {
        int width=320*(int)density, height=200*(int)density;
        Uint32 *source = malloc((size_t)width*height*4); CHECK(source);
        for (int y=0;y<height;y++) for (int x=0;x<width;x++) {
            /* Fine sloping edges and highlights, deliberately synthetic. */
            unsigned v = ((x+2*y)/7)%2 ? 0xe4 : 0x21;
            if ((x-3*y+height*3)%97 < 3) v=0xff;
            source[y*width+x]=0xff000000u|(v<<16)|((v/2+40)<<8)|(255-v/2);
        }
        SDL_Texture *texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_ARGB8888,
                                                 SDL_TEXTUREACCESS_STREAMING,width,height);
        CHECK(texture);
        CHECK(SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_NONE)==0);
        CHECK(SDL_UpdateTexture(texture,NULL,source,width*4)==0);
        for (unsigned i=0;i<sizeof(sizes)/sizeof(sizes[0]);i++) {
            SDL_Rect destination={17,13,sizes[i][0],sizes[i][1]};
            SDL_ScaleMode expected=destination.w%320==0 && destination.h%200==0
                                  ? SDL_ScaleModeNearest : SDL_ScaleModeLinear;
            CHECK(SDL_RenderSetScale(renderer,1,1)==0);
            CHECK(SDL_RenderSetViewport(renderer,NULL)==0);
            CHECK(SDL_RenderSetClipRect(renderer,NULL)==0);
            CHECK(__real_SDL_SetTextureScaleMode(texture,SDL_ScaleModeNearest)==0);
            output(renderer,texture,&destination,old);
            CHECK(__real_SDL_SetTextureScaleMode(texture,SDL_ScaleModeLinear)==0);
            output(renderer,texture,&destination,linear);
            check_mode(renderer,texture,destination,expected);
            output(renderer,texture,&destination,actual);
            CHECK(memcmp(actual,expected==SDL_ScaleModeNearest ? old : linear,(size_t)OW*OH*4)==0);
            size_t differences=0;
            for(int y=0;y<OH;y++) for(int x=0;x<OW;x++) {
                if(actual[y*OW+x]!=old[y*OW+x]) {
                    ++differences;
                    CHECK(x>=destination.x && x<destination.x+destination.w &&
                          y>=destination.y && y<destination.y+destination.h);
                }
            }
            if(expected==SDL_ScaleModeLinear) { CHECK(differences>0); ++changed_cases; }
            else CHECK(differences==0);
            if(density==4 && i==6 && argc==2) {
                save(argv[1],"synthetic-nearest",old);
                save(argv[1],"synthetic-smooth",actual);
            }
            ++cases;
        }
        /* Fractional renderer scale is part of the physical output footprint. */
        SDL_Rect destination={7,9,640,400}, viewport={5,7,1000,700}, clip={3,4,800,600};
        CHECK(SDL_RenderSetViewport(renderer,&viewport)==0);
        CHECK(SDL_RenderSetScale(renderer,1.25f,1.25f)==0);
        CHECK(SDL_RenderSetClipRect(renderer,&clip)==0);
        check_mode(renderer,texture,destination,SDL_ScaleModeLinear);
        CHECK(SDL_RenderSetScale(renderer,2,2)==0);
        check_mode(renderer,texture,destination,SDL_ScaleModeNearest);
        CHECK(SDL_RenderSetScale(renderer,.5f,.5f)==0);
        check_mode(renderer,texture,destination,SDL_ScaleModeNearest);
        CHECK(SDL_RenderSetScale(renderer,1.001f,1.001f)==0);
        check_mode(renderer,texture,destination,SDL_ScaleModeNearest);
        destination.w=960;destination.h=600;
        CHECK(SDL_RenderSetScale(renderer,2.0f/3.0f,2.0f/3.0f)==0);
        check_mode(renderer,texture,destination,SDL_ScaleModeNearest);
        destination.w=1280;destination.h=800;
        CHECK(SDL_RenderSetScale(renderer,1.25f,1.25f)==0);
        check_mode(renderer,texture,destination,SDL_ScaleModeNearest);
        CHECK(SDL_RenderSetScale(renderer,1,1)==0);
        CHECK(SDL_RenderSetViewport(renderer,NULL)==0);
        CHECK(SDL_RenderSetClipRect(renderer,NULL)==0);
        /* Repeated fractional/integer resizes must replace the prior mode. */
        for(unsigned repeat=0;repeat<10;repeat++) {
            destination.w=1001; destination.h=633;
            check_mode(renderer,texture,destination,SDL_ScaleModeLinear);
            destination.w=640; destination.h=400;
            check_mode(renderer,texture,destination,SDL_ScaleModeNearest);
        }
        destination.w=1001; destination.h=633;
        reject_linear=1;mode_calls=0;
        CHECK(video_hd_set_texture_scale(texture,renderer,&destination)==0);
        CHECK(mode_calls==2 && call_mode[0]==SDL_ScaleModeLinear && call_mode[1]==SDL_ScaleModeNearest);
        output(renderer,texture,&destination,actual);
        CHECK(__real_SDL_SetTextureScaleMode(texture,SDL_ScaleModeNearest)==0);
        output(renderer,texture,&destination,old);
        CHECK(memcmp(actual,old,(size_t)OW*OH*4)==0);
        reject_nearest=1;
        CHECK(video_hd_set_texture_scale(texture,renderer,&destination)!=0);
        destination.w=640;destination.h=400;mode_calls=0;
        CHECK(video_hd_set_texture_scale(texture,renderer,&destination)!=0);
        CHECK(mode_calls==1 && call_mode[0]==SDL_ScaleModeNearest);
        reject_linear=reject_nearest=0;
        destination.w=0;mode_calls=0;
        CHECK(video_hd_set_texture_scale(texture,renderer,&destination)!=0 && mode_calls==0);
        CHECK(video_hd_set_texture_scale(NULL,renderer,&destination)!=0);
        CHECK(video_hd_set_texture_scale(texture,NULL,&destination)!=0);
        CHECK(video_hd_set_texture_scale(texture,renderer,NULL)!=0);
        SDL_DestroyTexture(texture);free(source);
    }
    free(old);free(actual);free(linear);
    SDL_DestroyRenderer(renderer);SDL_FreeSurface(canvas);SDL_Quit();
    printf("PASS: %u output cases (%u fractional), %u checks; synthetic SDL software output, no game run\n",cases,changed_cases,checks);
    return 0;
}
