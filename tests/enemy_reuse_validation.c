/* Production renderer TU and native SDL allocation, wrapper and blits.
 * Originals arrive on stdin; this is not a game-loop acceptance claim. */
#include "render_mirror.c"
#include "enemy_reuse_identity.h"
#include "tyrian2.h"
static unsigned checks,cases,current_record;
#define CHECK(x) do {if(!(x)){fprintf(stderr,"CHECK failed case %u %s:%d: %s\n",cases,__FILE__,__LINE__,#x);abort();}checks++;} while(0)
static Uint8 records[2][77],weap_bytes[2][80],bank_bytes[32060],actor_banks[2][46566];
static Uint32 normal_palette[256];
static const char *resource_root;
static const unsigned ids[]={105,106,124,125,20,21};
static void record_load(const Uint8 *b)
{
 size_t n=0;
#define RBYTE(v) do {(v)=b[n++];} while(0)
#define RWORD(v) do {(v)=(unsigned)b[n]|((unsigned)b[n+1]<<8);n+=2;} while(0)
 RBYTE(enemyDat[current_record].ani);
 for(unsigned i=0;i<3;i++)RBYTE(enemyDat[current_record].tur[i]);
 for(unsigned i=0;i<3;i++)RBYTE(enemyDat[current_record].freq[i]);
 RBYTE(enemyDat[current_record].xmove);RBYTE(enemyDat[current_record].ymove);RBYTE(enemyDat[current_record].xaccel);RBYTE(enemyDat[current_record].yaccel);
 RBYTE(enemyDat[current_record].xcaccel);RBYTE(enemyDat[current_record].ycaccel);RWORD(enemyDat[current_record].startx);RWORD(enemyDat[current_record].starty);
 RBYTE(enemyDat[current_record].startxc);RBYTE(enemyDat[current_record].startyc);RBYTE(enemyDat[current_record].armor);RBYTE(enemyDat[current_record].esize);
 for(unsigned i=0;i<20;i++)RWORD(enemyDat[current_record].egraphic[i]);
 RBYTE(enemyDat[current_record].explosiontype);RBYTE(enemyDat[current_record].animate);RBYTE(enemyDat[current_record].shapebank);
 RBYTE(enemyDat[current_record].xrev);RBYTE(enemyDat[current_record].yrev);RWORD(enemyDat[current_record].dgr);RBYTE(enemyDat[current_record].dlevel);
 RBYTE(enemyDat[current_record].dani);RBYTE(enemyDat[current_record].elaunchfreq);RWORD(enemyDat[current_record].elaunchtype);
 RWORD(enemyDat[current_record].value);RWORD(enemyDat[current_record].eenemydie);
#undef RBYTE
#undef RWORD
 CHECK(n==77);
}

static void weapon_load(unsigned id,const Uint8 *b)
{
 JE_WeaponType *w=&weapons[id];unsigned n=0;
#define B(v) do{(v)=b[n++];}while(0)
#define W(v) do{(v)=b[n]|((unsigned)b[n+1]<<8);n+=2;}while(0)
 W(w->drain);B(w->shotrepeat);B(w->multi);W(w->weapani);B(w->max);B(w->tx);B(w->ty);B(w->aim);
 for(unsigned i=0;i<8;i++)B(w->attack[i]);for(unsigned i=0;i<8;i++)B(w->del[i]);
 for(unsigned i=0;i<8;i++)B(w->sx[i]);for(unsigned i=0;i<8;i++)B(w->sy[i]);
 for(unsigned i=0;i<8;i++)B(w->bx[i]);for(unsigned i=0;i<8;i++)B(w->by[i]);for(unsigned i=0;i<8;i++)W(w->sg[i]);
 B(w->acceleration);B(w->accelerationx);B(w->circlesize);B(w->sound);B(w->trail);B(w->shipblastfilter);CHECK(n==80);
#undef B
#undef W
}
static void restore(void)
{
 current_record=550;record_load(records[0]);current_record=240;record_load(records[1]);weapon_load(76,weap_bytes[0]);weapon_load(143,weap_bytes[1]);memcpy(rgb_palette,normal_palette,sizeof(normal_palette));
}
static void setup(unsigned frame)
{
 ++cases;if(cases%50==0)fprintf(stderr,"case %u\n",cases);render_mirror_hud_shutdown();
 if(canvas)SDL_FreeSurface(canvas);if(output)SDL_FreeSurface(output);if(game_screen)SDL_FreeSurface(game_screen);if(VGAScreenSeg)SDL_FreeSurface(VGAScreenSeg);if(fade_saved)SDL_FreeSurface(fade_saved);
 canvas=output=fade_saved=NULL;free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);hd_owner=cloud_owner=green_under_owner=NULL;green_first=NULL;green_under=NULL;
 game_screen=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);VGAScreen=game_screen;VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(game_screen&&VGAScreenSeg);
 game_probe_density=8;game_probe_tick=1000;game_probe_enabled=true;game_probe_missing=game_probe_invalid=game_probe_original_reference=false;game_probe_assets=resource_root;game_probe_scene_assets=0;
 manual_hd_enabled=asteroid_hd_enabled=false;shared_hud_lease=false;episodeNum=1;lvlFileNum=frame<100?5:2;xmas=isNetworkGame=twoPlayerMode=galagaMode=twoPlayerLinked=play_demo=record_demo=false;
 memset(enemy,0,sizeof(enemy));memset(enemyAvail,1,sizeof(enemyAvail));memset(enemyShot,0,sizeof(enemyShot));memset(enemyShotAvail,1,sizeof(enemyShotAvail));
 memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));restore();
 spriteSheet8=(Sprite2_array){sizeof(bank_bytes),bank_bytes};spriteSheet12=(Sprite2_array){0,NULL};
 enemySpriteSheetIds[0]=enemyDat[frame<100?240:550].shapebank;enemySpriteSheets[0]=(Sprite2_array){frame<100?40714:46566,actor_banks[frame<100?1:0]};
 SDL_FillRect(game_screen,NULL,0x1b);SDL_FillRect(VGAScreenSeg,NULL,0x1b);
 /* Observer fixtures grant PIC3 only after installing their final level data. */
 if(!enemy_reuse_observe_requested()){render_mirror_begin();CHECK(active&&!reject_reason);}
}
static void birth(unsigned frame,unsigned slot,int x,int y)
{
 unsigned record=frame<100?240:550,weapon=frame<100?143:76,phase=0;
 while(phase<8&&weapons[weapon].sg[phase]!=frame)phase++;CHECK(phase<8);
 unsigned avail=JE_makeEnemy(enemy,record,0);enemyAvail[0]=avail;CHECK(avail==0);
 EnemyShotType *s=&enemyShot[slot];JE_WeaponType *w=&weapons[weapon];
 s->sx=x;s->sy=y;s->sdmg=w->attack[phase];s->tx=w->tx;s->ty=w->ty;s->duration=w->del[phase];s->animate=0;s->animax=w->weapani;s->sgr=w->sg[phase];s->sxc=w->accelerationx;s->syc=w->acceleration;s->sxm=w->sx[phase];s->sym=w->sy[phase];enemyShotAvail[slot]=0;
 enemy_reuse_shot_spawn(slot,0,weapon,1,phase);
}
static void draw(unsigned frame,unsigned slot,int x,int y)
{
 EnemyShotType saved[ENEMY_SHOT_MAX];memcpy(saved,enemyShot,sizeof(saved));
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);blit_sprite2(classic,x,y,spriteSheet8,frame);
 enemy_reuse_shot_begin_draw(slot);draw_enemy_reuse_shot_sprite2(game_screen,x,y,spriteSheet8,frame,slot,frame);
 CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(!memcmp(saved,enemyShot,sizeof(saved)));SDL_FreeSurface(classic);
}
static void final_copy(void){for(int y=0;y<184;y++)memcpy((Uint8*)VGAScreenSeg->pixels+y*320,(Uint8*)game_screen->pixels+y*320+24,264);}
static Uint32 *pixel(SDL_Surface *s,int x,int y){return (Uint32*)((Uint8*)s->pixels+y*s->pitch)+x;}
static void finish(void){final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);}
static void oracle(unsigned k,int x,int y)
{
 const Uint8 *rgba=enemy_reuse_resources.members[k].rgba;CHECK(rgba);
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++){
  int dx=x*8+ax,dy=y*8+ay;if(dx<24*8||dx>=288*8||dy<0||dy>=184*8)continue;
  const Uint8 *p=rgba+4*(ay*96+ax);Uint32 before=palette_rgb(0x1b),want=before;
  if(p[3]){unsigned a=p[3],r=(((before>>16)&255)*(255-a)+p[0]*a+127)/255,g=(((before>>8)&255)*(255-a)+p[1]*a+127)/255,b=((before&255)*(255-a)+p[2]*a+127)/255;want=0xff000000u|(r<<16)|(g<<8)|b;}
  CHECK(*pixel(output,dx-24*8,dy)==want);
 }
}
static void positives(void)
{
 for(unsigned k=0;k<6;k++){setup(ids[k]);birth(ids[k],0,100,80);draw(ids[k],0,100,80);CHECK(draws==1);finish();CHECK(ready&&last_output_valid&&last_output_scene_hd&&!reject_reason);oracle(k,100,80);}
 int xs[]={0,308,-1,309};int ys[]={-14,-13,0,199,200};
 for(unsigned k=0;k<6;k++)for(unsigned xi=0;xi<4;xi++)for(unsigned yi=0;yi<5;yi++){
  setup(ids[k]);birth(ids[k],0,xs[xi],ys[yi]);draw(ids[k],0,xs[xi],ys[yi]);bool accepted=xi<2&&yi>0&&yi<4;CHECK((draws>0)==accepted);
 }
}
static void negatives(void)
{
 for(unsigned k=0;k<6;k++)for(unsigned fault=0;fault<14;fault++){
  setup(ids[k]);birth(ids[k],0,100,80);Uint8 saved=bank_bytes[100];
  switch(fault){case 0:bank_bytes[100]^=1;break;case 1:spriteSheet8.size--;break;case 2:xmas=true;break;case 3:twoPlayerMode=true;break;case 4:galagaMode=true;break;case 5:twoPlayerLinked=true;break;case 6:game_probe_missing=true;break;case 7:game_probe_invalid=true;break;case 8:game_probe_original_reference=true;break;case 9:enemyShotAvail[0]=1;break;case 10:enemyShot[0].sgr++;break;case 11:weapons[ids[k]<100?143:76].sound++;break;case 12:enemy_reuse_shot_retire(0);break;case 13:rgb_palette[0]^=1;break;}
  draw(ids[k],0,100,80);CHECK(draws==0);bank_bytes[100]=saved;
 }
 const char *valid=resource_root;const char *modes[]={"missing","corrupt","header","anchor","trailing","short"};
 for(unsigned k=0;k<6;k++)for(unsigned f=0;f<6;f++){
  char root[4096];snprintf(root,sizeof(root),"%s/%s%u",valid,modes[f],k);resource_root=root;setup(ids[k]);birth(ids[k],0,100,80);draw(ids[k],0,100,80);CHECK(draws==0);
 }resource_root=valid;
}
static void lifecycle(void)
{
 for(unsigned fault=0;fault<8;fault++){
  setup(105);birth(105,0,100,80);draw(105,0,100,80);CHECK(draws==1);Uint8 saved=bank_bytes[100];
  switch(fault){case 0:bank_bytes[100]^=1;break;case 1:rgb_palette[0]^=1;break;case 2:game_probe_assets="changed-root";break;case 3:enemy_reuse_shot_retire(0);break;case 4:enemy_reuse_resources.members[0].rgba[31]^=1;break;case 5:weapons[76].sound++;break;case 6:enemy_reuse_actor_allocated(enemy,550,0);break;case 7:spriteSheet8.size--;break;}
  finish();CHECK(!last_output_valid&&!last_output_scene_hd);bank_bytes[100]=saved;
 }
 unsigned kinds[]={MIRROR_OUTPUT_NORMAL15_NIGHT,MIRROR_OUTPUT_NORMAL15_LOW_DETAIL,MIRROR_OUTPUT_UNSUPPORTED};
 for(unsigned ki=0;ki<3;ki++){unsigned kind=kinds[ki];
  setup(105);birth(105,0,100,80);draw(105,0,100,80);final_copy();render_mirror_finish(kind,0,0);CHECK(!last_output_valid&&!last_output_scene_hd);
 }
 setup(105);birth(105,0,100,80);draw(105,0,100,80);finish();CHECK(last_output_valid);render_mirror_fade_start(NULL,NULL,0,255);CHECK(!ready&&!last_output_valid&&!last_output_scene_hd&&!have_fade_saved);
 /* Later original pixel writes must occlude the HD owner. */
 setup(105);birth(105,0,100,80);draw(105,0,100,80);Uint8 *p=(Uint8*)game_screen->pixels+85*320+105;*p=0x3a;render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);finish();CHECK(last_output_valid);for(int y=0;y<8;y++)for(int x=0;x<8;x++)CHECK(*pixel(output,(105-24)*8+x,85*8+y)==palette_rgb(0x3a));
}

static void boundaries(void)
{
 for(unsigned k=0;k<6;k++){
  setup(ids[k]);birth(ids[k],0,100,80);enemy_reuse_shot_begin_draw(0);
  draw_enemy_shot_sprite2(game_screen,100,80,spriteSheet8,ids[k]);CHECK(!enemy_reuse_frame.contributed);
  setup(ids[k]);birth(ids[k],0,100,80);enemy_reuse_shot_begin_draw(0);
  draw_player_shot_sprite2(game_screen,100,80,spriteSheet8,ids[k],0,ids[k]);CHECK(!enemy_reuse_frame.contributed);
  setup(ids[k]);birth(ids[k],0,100,80);enemy_reuse_shot_begin_draw(0);
  draw_entity_sprite2(game_screen,100,80,spriteSheet8,ids[k],ENTITY_NORMAL,ENTITY_TILE);CHECK(!enemy_reuse_frame.contributed);CHECK(!enemy_reuse_identity_matches(0,ids[k],100,80));
  setup(ids[k]);birth(ids[k],0,100,80);Sprite2_array other=spriteSheet8;Uint8 copy[32060];memcpy(copy,bank_bytes,sizeof(copy));other.data=copy;enemy_reuse_shot_begin_draw(0);
  CHECK(!render_mirror_enemy_reuse_shot(game_screen,100,80,other,ids[k],0,ids[k]));CHECK(!enemy_reuse_frame.contributed);
  enemy_reuse_shot_begin_draw(0);other.data=NULL;CHECK(!render_mirror_enemy_reuse_shot(game_screen,100,80,other,ids[k],0,ids[k]));
  enemy_reuse_shot_begin_draw(0);CHECK(!render_mirror_enemy_reuse_shot(game_screen,100,80,spriteSheet8,ids[k],1,ids[k]));
  enemy_reuse_shot_begin_draw(0);CHECK(!render_mirror_enemy_reuse_shot(game_screen,100,80,spriteSheet8,ids[k],0,ids[k]+1));
 }
 for(unsigned fault=0;fault<8;fault++){
  setup(105);birth(105,0,100,80);draw(105,0,100,80);finish();CHECK(last_output_valid);Uint8 saved=bank_bytes[100];void *old=VGAScreenSeg->pixels;
  switch(fault){case 0:((Uint8*)VGAScreenSeg->pixels)[0]^=1;break;case 1:rgb_palette[0]^=1;break;case 2:VGAScreenSeg->pitch++;break;case 3:VGAScreenSeg->pixels=NULL;break;case 4:bank_bytes[100]^=1;break;case 5:enemy_reuse_bank_changed(&spriteSheet8);break;case 6:enemy_reuse_shot_retire(0);break;case 7:((Uint8*)game_screen->pixels)[0]^=1;break;}
  CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!ready&&!last_output_valid&&!last_output_scene_hd&&!have_fade_saved);VGAScreenSeg->pixels=old;VGAScreenSeg->pitch=320;bank_bytes[100]=saved;
 }
 /* Real player sprite followed by enemy art preserves ordered RGB blending.
  * Generic/player source identities cannot acquire the enemy role. */
 setup(105);draw_entity_sprite2(game_screen,100,80,spriteSheet8,105,ENTITY_NORMAL,ENTITY_TILE);CHECK(!enemy_reuse_frame.contributed);
 Uint32 before[112*96];for(int y=0;y<112;y++)for(int x=0;x<96;x++)before[y*96+x]=*pixel(canvas,100*8+x,80*8+y);
 birth(105,0,100,80);draw(105,0,100,80);finish();CHECK(last_output_valid);
 const Uint8 *rgba=enemy_reuse_resources.members[0].rgba;
 for(int y=0;y<112;y++)for(int x=0;x<96;x++){const Uint8 *p=rgba+4*(y*96+x);Uint32 bg=before[y*96+x];unsigned a=p[3],r=(((bg>>16)&255)*(255-a)+p[0]*a+127)/255,g=(((bg>>8)&255)*(255-a)+p[1]*a+127)/255,b=((bg&255)*(255-a)+p[2]*a+127)/255;CHECK(*pixel(output,(100-24)*8+x,80*8+y)==(0xff000000u|(r<<16)|(g<<8)|b));}
}

static void identity_contracts(void)
{
 static const unsigned order76[]={105,124,106,125},order143[]={21,20};restore();
 CHECK(weapons[76].max==4&&weapons[76].multi==4&&!weapons[76].weapani);CHECK(weapons[143].max==2&&weapons[143].multi==1&&!weapons[143].weapani);
 for(unsigned p=0;p<4;p++)CHECK(weapons[76].sg[p]==order76[p]);for(unsigned p=0;p<2;p++)CHECK(weapons[143].sg[p]==order143[p]);
 for(unsigned k=0;k<6;k++){
  setup(ids[k]);birth(ids[k],0,100,80);uint64_t gen=enemy_reuse_identity_generation(0);CHECK(gen);
  enemy_reuse_shot_begin_draw(0);CHECK(enemy_reuse_identity_matches(0,ids[k],100,80));CHECK(!enemy_reuse_identity_matches(0,ids[k],100,80));
  enemy_reuse_reset();CHECK(!enemy_reuse_identity_generation(0));enemyAvail[0]=1;birth(ids[k],0,100,80);CHECK(enemy_reuse_identity_generation(0)&&enemy_reuse_identity_generation(0)!=gen);
  enemy_reuse_shot_begin_draw(0);enemyShot[0].sx++;CHECK(!enemy_reuse_identity_matches(0,ids[k],101,80));enemyShot[0].sx--;
  enemy_reuse_shot_begin_draw(0);enemy_reuse_bank_changed(&enemySpriteSheets[0]);CHECK(!enemy_reuse_identity_matches(0,ids[k],100,80));CHECK(!enemy_reuse_identity_generation(0));
  setup(ids[k]);birth(ids[k],0,100,80);unsigned b=ids[k]<100?1:0;actor_banks[b][100]^=1;draw(ids[k],0,100,80);CHECK(!enemy_reuse_frame.contributed);actor_banks[b][100]^=1;
  setup(ids[k]);unsigned record=ids[k]<100?240:550;enemyAvail[0]=JE_makeEnemy(enemy,record,enemyDat[record].shapebank);CHECK(enemyAvail[0]==0);
  enemy_reuse_shot_spawn(0,0,ids[k]<100?143:76,1,0);CHECK(!enemy_reuse_identity_generation(0));
 }
}
int main(int argc,char **argv)
{
 CHECK(argc==2);resource_root=argv[1];CHECK(fread(bank_bytes,1,sizeof(bank_bytes),stdin)==sizeof(bank_bytes));CHECK(fread(records,1,sizeof(records),stdin)==sizeof(records));CHECK(fread(weap_bytes,1,sizeof(weap_bytes),stdin)==sizeof(weap_bytes));CHECK(fread(normal_palette,1,sizeof(normal_palette),stdin)==sizeof(normal_palette));CHECK(fread(actor_banks[0],1,46566,stdin)==46566);CHECK(fread(actor_banks[1],1,40714,stdin)==40714);CHECK(fgetc(stdin)==EOF);
 positives();negatives();lifecycle();boundaries();identity_contracts();printf("PASS native enemy reuse: %u cases, %u assertions; actual renderer/wrapper/indexed blits; not gameplay acceptance\n",cases,checks);return 0;
}
