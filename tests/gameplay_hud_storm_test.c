/* Synthetic fixtures only. Including the module makes cache poison an explicit
 * white-box test without adding a production test API. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "storm_test_pins.h"
#include "../src/gameplay_hud_storm.c"
static uint8_t indexed[200*336], raw[312], *rgb, *texture;
static uint32_t palette[256];
static HudStormView view;
static HudStormSource src;
static const char *directory;
static int density, rp, tp;
static void fixture(void)
{
 memset(indexed,17,sizeof(indexed));
 unsigned n=0;
 for(unsigned y=0;y<13;y++) {
  raw[n++]=255;raw[n++]=3;
  for(unsigned x=3;x<25;x++)raw[n++]=(uint8_t)(192+(x+y)%16);
 }
 assert(n==sizeof(raw));
 for(unsigned i=0;i<256;i++)palette[i]=(i<<16)|((255-i)<<8)|(i^0x55);
 view=(HudStormView){&indexed,&raw,indexed,320,200,336,8,1};
 src=(HudStormSource){raw,sizeof(raw),25,13,70};
}
static void begin(void){hud_storm_begin(&view,&src,1,9,38,284,82,true);}
static void clear(void)
{
 for(unsigned y=82;y<98;y++)memset(indexed+y*336+284,0,29);
 hud_storm_rect(&view,284,82,29,16);
}
static void paint(void)
{
 for(unsigned y=0;y<13;y++)for(unsigned x=3;x<25;x++) {
  uint8_t *p=indexed+(82+y)*336+284+x;*p=(uint8_t)(192+(x+y)%16);
  hud_storm_pixel(&view,p);
 }
}
static void draw(void)
{begin();clear();paint();hud_storm_rect(&view,284,95,2,2);hud_storm_end(&view,&src,1,true);}
static void start(void)
{fixture();assert(hud_storm_start(directory,&view,&src));draw();assert(state.recorded);}
static void base(void)
{
 rp=320*density*4+32;tp=320*density*4+48;
 free(rgb);free(texture);rgb=malloc((size_t)rp*200*density);texture=malloc((size_t)tp*200*density);
 assert(rgb&&texture);memset(rgb,0xa5,(size_t)rp*200*density);memset(texture,0x5a,(size_t)tp*200*density);
 for(int y=0;y<200*density;y++)for(int x=0;x<320*density;x++) {
  uint32_t c=color(palette[indexed[(y/density)*336+x/density]]);
  memcpy(rgb+(size_t)y*rp+x*4,&c,4);memcpy(texture+(size_t)y*tp+x*4,&c,4);
 }
}
static bool show(bool scope)
{return hud_storm_present(&view,&src,scope,palette,rgb,rp,texture,tp,320*density,200*density,density);}
static void assert_pristine(void)
{
 for(int y=0;y<200*density;y++)assert(!memcmp(rgb+(size_t)y*rp,texture+(size_t)y*tp,(size_t)320*density*4));
}
int main(int argc,char **argv)
{
 assert(argc==2);directory=argv[1];density=4;
 for(int d=4;d<=8;d+=4) {
  density=d;start();base();uint64_t before=stamp(indexed,sizeof(indexed)),rawbefore=stamp(raw,sizeof(raw));
  assert(show(true));unsigned changed=0;
  for(int y=0;y<200*d;y++)for(int x=0;x<320*d;x++) {
   uint32_t a,b;memcpy(&a,rgb+(size_t)y*rp+x*4,4);memcpy(&b,texture+(size_t)y*tp+x*4,4);
   bool owned=x>=284*d&&x<309*d&&y>=82*d&&y<87*d;
   if(!owned)assert(a==b);else {unsigned n=125*d*d,o=d==8?4000:0,i=(y-82*d)*25*d+x-284*d;assert(b==blend(palette[state.art[o+i]],palette[0],state.art[o+n+i]));if(a!=b)changed++;}
  }
  assert(changed&&stamp(indexed,sizeof(indexed))==before&&stamp(raw,sizeof(raw))==rawbefore);
  base();assert(show(true)); /* Successful repeated presentation is safe. */
 }
 density=4;
 start();base();hud_storm_begin(&view,&src,0,9,38,284,64,true);hud_storm_end(&view,&src,0,true);assert(show(true));
 start();base();assert(!show(false));assert_pristine();assert(!show(true)); /* equipment change cannot resurrect */
 start();base();begin();assert(!show(true));assert_pristine(); /* interrupted draw */
 start();base();begin();begin();clear();paint();hud_storm_end(&view,&src,1,true);assert(!show(true));
 start();base();begin();paint();hud_storm_end(&view,&src,1,true);assert(!show(true)); /* no verified clear */
 start();base();begin();clear();paint();hud_storm_pixel(&view,indexed+82*336+287);hud_storm_end(&view,&src,1,true);assert(!show(true)); /* duplicate raw pixel */
 start();base();hud_storm_pixel(&view,indexed+82*336+287);assert(!show(true));assert_pristine();draw();base();assert(show(true));
 start();base();hud_storm_rect(&view,284,82,25,5);assert(!show(true));assert_pristine();
 start();base();hud_storm_rect(&view,284,95,2,2);assert(show(true)); /* gauge is independent */
 start();base();indexed[94*336+308]^=1;assert(!show(true));indexed[94*336+308]^=1;assert(!show(true)); /* full lower icon guard */
 start();base();raw[2]^=1;assert(!show(true));raw[2]^=1;assert(!show(true));
 start();base();src.width=24;assert(!show(true));src.width=25;assert(!show(true));
 start();base();state.art[42]^=1;assert(!show(true));assert_pristine(); /* cache integrity */
 start();base();palette[0]^=1;assert(!show(true));palette[0]^=1;assert(!show(true));
 start();base();rgb[(82*4)*rp+(284*4)*4]^=1;assert(!show(true));rgb[(82*4)*rp+(284*4)*4]^=1;assert(!show(true)); /* same-index upper RGB */
 start();base();hud_storm_suspend();hud_storm_resume(&view,true);assert(!show(true));draw();base();assert(show(true));
 start();base();hud_storm_reset();assert(!show(true)); /* source free/reload uses same reset */
 start();base();HudStormView saved=view;view.format=&view;assert(!show(true));view=saved;assert(!show(true));
 start();base();view.pitch=335;assert(!show(true));
 start();base();view.format=&view;hud_storm_pixel(&view,indexed+82*336+287);view.format=&raw;assert(!show(true));
 start();base();view.pitch=335;hud_storm_rect(&view,284,82,25,5);view.pitch=336;assert(!show(true));
 start();base();hud_storm_begin(&view,&src,0,9,38,284,64,false);assert(!show(true));
 start();base();src.data=raw+1;assert(!show(true));
 start();base();hud_storm_resume(&view,false);assert(!show(true));
 start();base();for(unsigned i=0;i<256;i++)palette[i]=0;hud_storm_fade_palette(palette);base();assert(show(true));
 for(unsigned i=0;i<256;i++){palette[i]=0xffffff;}hud_storm_fade_palette(palette);base();assert(show(true));
 for(unsigned i=0;i<256;i++){palette[i]=(i<<16)|((255-i)<<8)|(i^0x55);}
 base();assert(show(true)); /* palette restoration */
 hud_storm_resume(&view,true);for(unsigned i=0;i<256;i++){palette[i]=0xffffff;}base();assert(!show(true)); /* old fade grant expired */
 start();base();int old=density;density=2;assert(!show(true));density=old;assert_pristine();
 start();base();assert(!hud_storm_present(&view,&src,true,palette,rgb,1,texture,tp,1280,800,4));assert_pristine();
 /* Disk is sampled at authenticated start, never on ordinary displays. */
 char file[1024],backup[1024],alternate[1024];
 snprintf(file,sizeof(file),"%s/gameplay-hud-storm-label-v1.hda",directory);
 snprintf(backup,sizeof(backup),"%s/saved-resource.hda",directory);
 snprintf(alternate,sizeof(alternate),"%s/alternate",directory);
 start();base();assert(!rename(file,backup));assert(show(true));
 fixture();assert(!hud_storm_start(directory,&view,&src));assert(!rename(backup,file));
 draw();base();assert(!show(true)); /* restored disk alone cannot reactivate missing cache */
 start();base();assert(!rename(file,backup));FILE *badfile=fopen(file,"wb");assert(badfile);assert(fputc(0,badfile)!=EOF);assert(!fclose(badfile));assert(show(true));
 fixture();assert(!hud_storm_start(directory,&view,&src));assert(!remove(file));assert(!rename(backup,file));
 fixture();assert(hud_storm_start(alternate,&view,&src));draw();base();assert(show(true));
 /* Missing, truncated, trailing, every header field, checksum/header forgery,
  * unsupported palette roles, and nonregular FIFO resources fail closed. */
 for(unsigned i=0;i<24;i++) {
  char bad[1024];snprintf(bad,sizeof(bad),"%s/bad%u",directory,i);fixture();assert(!hud_storm_start(bad,&view,&src));draw();base();assert(!show(true));assert_pristine();
 }
 fixture();src.size--;assert(!hud_storm_start(directory,&view,&src));
 fixture();src.height=14;assert(!hud_storm_start(directory,&view,&src));
 fixture();indexed[0]^=1;assert(!hud_storm_start(directory,&view,&src));
 fixture();view.bits=32;assert(!hud_storm_start(directory,&view,&src));
 hud_storm_shutdown();free(rgb);free(texture);puts("STORM synthetic loader/history/source/texture/lifecycle tests passed (4x/8x)");return 0;
}
