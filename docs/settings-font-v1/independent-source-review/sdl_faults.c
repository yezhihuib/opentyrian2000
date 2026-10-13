#include <SDL.h>
#include <stdlib.h>
unsigned sf_test_fault, sf_test_live_textures, sf_test_sdl_cases;
SDL_Texture *__real_SDL_CreateTexture(SDL_Renderer *,Uint32,int,int,int);
void __real_SDL_DestroyTexture(SDL_Texture *);
int __real_SDL_SetTextureScaleMode(SDL_Texture *,SDL_ScaleMode);
int __real_SDL_SetTextureBlendMode(SDL_Texture *,SDL_BlendMode);
int __real_SDL_UpdateTexture(SDL_Texture *,const SDL_Rect *,const void *,int);
int __real_SDL_SetRenderDrawColor(SDL_Renderer *,Uint8,Uint8,Uint8,Uint8);
int __real_SDL_RenderClear(SDL_Renderer *);
int __real_SDL_RenderCopy(SDL_Renderer *,SDL_Texture *,const SDL_Rect *,const SDL_Rect *);
SDL_Texture *__wrap_SDL_CreateTexture(SDL_Renderer *r,Uint32 f,int a,int w,int h){if(sf_test_fault==1)return NULL;SDL_Texture *t=__real_SDL_CreateTexture(r,f,a,w,h);if(t)sf_test_live_textures++;return t;}
void __wrap_SDL_DestroyTexture(SDL_Texture *t){if(t){if(!sf_test_live_textures)abort();sf_test_live_textures--;}__real_SDL_DestroyTexture(t);}
int __wrap_SDL_SetTextureScaleMode(SDL_Texture *t,SDL_ScaleMode m){return sf_test_fault==2?-1:__real_SDL_SetTextureScaleMode(t,m);}
int __wrap_SDL_SetTextureBlendMode(SDL_Texture *t,SDL_BlendMode m){return sf_test_fault==3?-1:__real_SDL_SetTextureBlendMode(t,m);}
int __wrap_SDL_UpdateTexture(SDL_Texture *t,const SDL_Rect *r,const void *p,int pitch){return sf_test_fault==4?-1:__real_SDL_UpdateTexture(t,r,p,pitch);}
int __wrap_SDL_SetRenderDrawColor(SDL_Renderer *r,Uint8 a,Uint8 b,Uint8 c,Uint8 d){return sf_test_fault==5?-1:__real_SDL_SetRenderDrawColor(r,a,b,c,d);}
int __wrap_SDL_RenderClear(SDL_Renderer *r){return sf_test_fault==6?-1:__real_SDL_RenderClear(r);}
int __wrap_SDL_RenderCopy(SDL_Renderer *r,SDL_Texture *t,const SDL_Rect *s,const SDL_Rect *d){return sf_test_fault==7?-1:__real_SDL_RenderCopy(r,t,s,d);}
