#define main meter_unit_main
#include "test_meters.c"
#undef main
#include <math.h>
typedef unsigned int uint;
typedef uint8_t Uint8;
typedef uint8_t JE_byte;
typedef int JE_integer;
typedef struct {void *pixels;int pitch,h;} SDL_Surface;
typedef struct {int x,y,w,h;} SDL_Rect;
static SDL_Surface surface={screen,320,200},*VGAScreen=&surface,*VGAScreenSeg=&surface;
static bool twoPlayerMode,galagaMode,onePlayerAction;
static struct player_t {uint shield,armor;struct {struct {Uint8 power;} weapon[2];} items;} player[2];
static unsigned power,powerAdd,lastPower,temp,old_weapon_bar[2],begins,ends,rejections;
#define COUNTOF(x) (sizeof(x)/sizeof((x)[0]))
#define MIRROR_NORMAL 0
static void render_mirror_pixel(SDL_Surface *p,Uint8 *q,Uint8 c,int mode){(void)p;(void)q;(void)c;(void)mode;}
static void render_mirror_rect(SDL_Surface *p,const SDL_Rect *r){(void)p;(void)r;}
static int SDL_FillRect(SDL_Surface *p,const SDL_Rect *r,unsigned c){
 if(r->w<=0||r->h<=0)return 0;
 for(int y=0;y<p->h;y++)for(int x=0;x<320;x++)if(x>=r->x&&x-r->x<r->w&&y>=r->y&&y-r->y<r->h)((Uint8 *)p->pixels)[y*p->pitch+x]=(Uint8)c;
 return 0;
}
static void render_mirror_hud_shield_wiped(SDL_Surface *p){assert(p==VGAScreenSeg);}
static void render_mirror_hud_meter_begin(SDL_Surface *p,SDL_Surface *draw,unsigned kind,unsigned a,unsigned b){
 assert(p==VGAScreenSeg&&draw==VGAScreenSeg);begins++;hud_meters_write_begin(kind,a,b);
 if(kind<2&&a>11)assert(!(stamped&hud_meters_event_bits(kind)));
}
static void render_mirror_hud_meter_end(SDL_Surface *p,unsigned kind){assert(p==VGAScreenSeg);ends++;if(!hud_meters_write_end(kind,p->pixels,p->pitch))rejections++;}
static int clipped_warning(const char *format,...){(void)format;return 0;}
#define printf clipped_warning
#include "writers.inc"
#undef printf
static void pair(void (*base)(void),void (*candidate)(void)){
 uint8_t before[64000],after[64000];struct player_t players_before[2],players_after[2];
 unsigned globals[]={power,powerAdd,lastPower,temp,old_weapon_bar[0],old_weapon_bar[1]},expect[6];
 memcpy(before,screen,64000);memcpy(players_before,player,sizeof(player));base();memcpy(after,screen,64000);memcpy(players_after,player,sizeof(player));
 expect[0]=power;expect[1]=powerAdd;expect[2]=lastPower;expect[3]=temp;expect[4]=old_weapon_bar[0];expect[5]=old_weapon_bar[1];
 memcpy(screen,before,64000);memcpy(player,players_before,sizeof(player));power=globals[0];powerAdd=globals[1];lastPower=globals[2];temp=globals[3];old_weapon_bar[0]=globals[4];old_weapon_bar[1]=globals[5];
 candidate();assert(!memcmp(screen,after,64000)&&!memcmp(player,players_after,sizeof(player)));
 unsigned actual[]={power,powerAdd,lastPower,temp,old_weapon_bar[0],old_weapon_bar[1]};assert(!memcmp(actual,expect,sizeof(actual)));pairs++;
}
static void fresh(void){reset_screen();memset(player,0,sizeof(player));memset(old_weapon_bar,0,sizeof(old_weapon_bar));power=powerAdd=lastPower=temp=0;twoPlayerMode=galagaMode=onePlayerAction=false;}
int main(int argc,char **argv){
 assert(argc==2);directory=argv[1];snprintf(filename,sizeof(filename),"%s/gameplay-hud-meters-v2.hda",directory);fixture();load();
 for(unsigned f=0;f<2;f++)for(unsigned p=0;p<12;p++)for(unsigned q=0;q<12;q++){
  fresh();player[0].items.weapon[f].power=p;pair(baseline_weapon_display,weapon_display);player[0].items.weapon[f].power=q;pair(baseline_weapon_display,weapon_display);assert(hud_meters_prepare(screen,320)==60);
 }
 for(unsigned p=0;p<=90;p++)for(unsigned q=0;q<=90;q++){
  fresh();power=10*p;pair(baseline_generator_display,generator_display);power=10*q;pair(baseline_generator_display,generator_display);assert(hud_meters_prepare(screen,320)==60);
 }
 for(unsigned p=0;p<=28;p++)for(unsigned q=0;q<=28;q++){
  fresh();player[0].armor=p;pair(baseline_JE_drawArmor,JE_drawArmor);player[0].armor=q;pair(baseline_JE_drawArmor,JE_drawArmor);assert(hud_meters_prepare(screen,320)==60);
  pair(baseline_JE_wipeShieldArmorBars,JE_wipeShieldArmorBars);assert(hud_meters_prepare(screen,320)==60);pair(baseline_JE_drawArmor,JE_drawArmor);assert(hud_meters_prepare(screen,320)==60);
 }
 /* P12 genuinely paints extra columns while first11 segments alias P11. */
 for(unsigned p=12;p<=255;p+=243){fresh();player[0].items.weapon[0].power=p;pair(baseline_weapon_display,weapon_display);assert(screen[17*320+311]==127);assert(!(hud_meters_prepare(screen,320)&4));player[0].items.weapon[0].power=11;assert(!(hud_meters_prepare(screen,320)&4));pair(baseline_weapon_display,weapon_display);assert(hud_meters_prepare(screen,320)&4);assert(screen[17*320+311]==127);}
 fresh();player[0].armor=30;player[1].armor=UINT_MAX;pair(baseline_JE_wipeShieldArmorBars,JE_wipeShieldArmorBars);assert(!(hud_meters_prepare(screen,320)&32));pair(baseline_JE_drawArmor,JE_drawArmor);assert(player[0].armor==28&&player[1].armor==28&&(hud_meters_prepare(screen,320)&32));
 player[0].armor=0;assert(hud_meters_prepare(screen,320)&32);assert(screen[137*320+307]==239);pair(baseline_JE_drawArmor,JE_drawArmor);assert(screen[137*320+307]==239);
 pair(baseline_JE_wipeShieldArmorBars,JE_wipeShieldArmorBars);assert(hud_meters_prepare(screen,320)&32);for(unsigned y=137;y<195;y++)assert(!screen[y*320+307]);
 fresh();onePlayerAction=true;unsigned before=begins;pair(baseline_generator_display,generator_display);assert(power==900&&lastPower==0&&begins==before);for(unsigned y=12;y<104;y++)assert(!screen[y*320+269]);
 onePlayerAction=false;power=450;pair(baseline_generator_display,generator_display);uint8_t saved[64000];memcpy(saved,screen,64000);onePlayerAction=true;before=begins;pair(baseline_generator_display,generator_display);assert(power==900&&lastPower==45&&begins==before&&!memcmp(saved,screen,64000));
 fresh();power=99;pair(baseline_generator_display,generator_display);assert(lastPower==9);power=100;pair(baseline_generator_display,generator_display);assert(lastPower==10);lastPower=91;power=450;pair(baseline_generator_display,generator_display);assert(!(hud_meters_prepare(screen,320)&16));
 assert(begins==ends);hud_meters_shutdown();assert(!allocation&&descriptor==-1);
 printf("PASS source-extracted writer A/B=%u; notifications=%u; rejected=%u; P12/255 overflow, all transitions, arcade900/stale armor, both-player clamp; full indexed/state parity.\n",pairs,begins,rejections);return 0;
}
