/* Isolated admission reproduction. Linker GC drops unrelated engine hooks. */
#include "../src/pregame_font.c"
int main(void)
{
 SDL_Surface *indexed=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 SDL_Surface *rgb332=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_RGB332);
 if(!indexed||!rgb332)return 2;
 bool a=geometry(indexed),b=geometry(rgb332);
 printf("INDEX8 geometry=%d; RGB332 geometry=%d; index_format=%u rgb332_format=%u\n",a,b,indexed->format->format,rgb332->format->format);
 SDL_FreeSurface(indexed);SDL_FreeSurface(rgb332);return a&&!b?0:1;
}
