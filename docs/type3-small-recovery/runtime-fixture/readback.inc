/* Native SDL output, finite tick list; no resizing, cropping, screenshots or BMP. */
static bool type3_capture_tick(void)
{
 const char*mode=getenv("OT_TYPE3_CAPTURE_MODE");if(!mode)return false;
 if(!strcmp(mode,"cycle"))return game_probe_tick>=6181&&game_probe_tick<=6183;
 if(!strcmp(mode,"density4"))return game_probe_tick==6181;
 if(!strcmp(mode,"main"))return (game_probe_tick>=6181&&game_probe_tick<=6192)||(game_probe_tick>=6512&&game_probe_tick<=6531);
 fprintf(stderr,"unknown private capture mode\n");exit(2);
}
void asset_debug_readback(SDL_Renderer *renderer)
{
 if(!getenv("OT_CAPTURE_RGBA_STREAM")||!type3_capture_tick()||game_probe_tick==last_capture)return;
 int w,h;if(SDL_GetRendererOutputSize(renderer,&w,&h))exit(2);
 if(!((w==640&&h==400)||(w==1280&&h==800))){fprintf(stderr,"unexpected native output %dx%d\n",w,h);exit(2);}
 SDL_Surface*s=SDL_CreateRGBSurfaceWithFormat(0,w,h,32,SDL_PIXELFORMAT_ARGB8888);if(!s||SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,s->pixels,s->pitch))exit(2);
 static FILE*f;if(!f){f=fopen(getenv("OT_CAPTURE_RGBA_STREAM"),"wb");if(!f)exit(2);}
 Uint32 header[4]={game_probe_tick,w,h,w*h*4};if(fwrite("ORF1",1,4,f)!=4||fwrite(header,4,4,f)!=4)exit(2);
 for(int y=0;y<h;y++)if(fwrite((Uint8*)s->pixels+y*s->pitch,1,w*4,f)!=(size_t)w*4)exit(2);
 fflush(f);SDL_FreeSurface(s);last_capture=game_probe_tick;
}
