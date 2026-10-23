/* Full native SDL renderer TU plus production-linked allocation and sprite writes.
 * Private originals enter only over stdin. Not a game-loop acceptance test. */
#include "render_mirror.c"
#include "tyrian2.h"
static unsigned checks,cases,current_record=163,current_slot;
#define CHECK(x) do {if(!(x)){fprintf(stderr,"CHECK failed case %u %s:%d: %s\n",cases,__FILE__,__LINE__,#x);abort();}checks++;} while(0)
static Uint8 original_records[3][77],bank_original[NEWSHF_PROTOTYPE_BANK_BYTES];
static Uint32 normal_palette[256];
static const char *resource_root;
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

static void read_exact(void *p,size_t n){CHECK(fread(p,1,n,stdin)==n);}
static void records_restore(void){for(unsigned i=0;i<3;i++){current_record=newshf_prototype_record_ids[i];record_load(original_records[i]);}}
static void setup(int density)
{
 ++cases;current_slot=0;render_mirror_hud_shutdown();
 if(canvas)SDL_FreeSurface(canvas);if(output)SDL_FreeSurface(output);if(game_screen)SDL_FreeSurface(game_screen);if(VGAScreenSeg)SDL_FreeSurface(VGAScreenSeg);if(fade_saved)SDL_FreeSurface(fade_saved);
 canvas=output=fade_saved=NULL;free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);hd_owner=cloud_owner=green_under_owner=NULL;green_first=NULL;green_under=NULL;
 game_screen=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);VGAScreen=game_screen;VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(game_screen&&VGAScreenSeg);
 game_probe_density=density;game_probe_enabled=game_probe_missing=game_probe_invalid=game_probe_original_reference=false;
 manual_hd_enabled=asteroid_hd_enabled=false;shared_hud_lease=false;
 memset(enemy,0,sizeof(enemy));memset(enemyAvail,1,sizeof(enemyAvail));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));
 enemySpriteSheetIds[0]=10;enemySpriteSheets[0]=(Sprite2_array){NEWSHF_PROTOTYPE_BANK_BYTES,bank_original};records_restore();memcpy(rgb_palette,normal_palette,sizeof(normal_palette));tempMapXOfs=0;
 SDL_FillRect(game_screen,NULL,0x1b);SDL_FillRect(VGAScreenSeg,NULL,0x1b);CHECK(render_mirror_set_global_assets(resource_root));render_mirror_begin();CHECK(global_newshf_frame);CHECK(!active);
}
static void birth_at(unsigned slot,unsigned profile,unsigned pose,int x,int y,int filter)
{
 current_slot=slot;current_record=newshf_prototype_record_ids[profile];unsigned avail=JE_makeEnemy(enemy+slot,current_record,0);CHECK(avail==0);enemyAvail[slot]=avail;CHECK(newshf_validation_slots[slot].role);
 enemy[slot].ex=x;enemy[slot].ey=y;enemy[slot].enemycycle=pose;enemy[slot].filter=filter;render_mirror_newshf_validation_observe(slot);
}
static void birth(unsigned profile,unsigned pose,int x,int y,int filter)
{birth_at(0,profile,pose,x,y,filter);}
static void tile(unsigned part)
{
 struct JE_SingleEnemyType *e=enemy+current_slot;int x=e->ex+(part==1||part==20?6:-6),y=e->ey+(part>=19?7:-7);unsigned base=e->egr[e->enemycycle-1];
 G101EnemyContext c={e->enemytype,current_slot,enemyAvail[current_slot],e->size,e->scoreitem,e->edamaged,e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel,e->ani==1&&e->enemycycle==1&&e->aniactive==0};
 render_mirror_enemy_tile(game_screen,x,y,*e->sprite2s,base,part,e->filter,&c);
 if(e->filter)blit_sprite2_filter(game_screen,x,y,*e->sprite2s,base+part,e->filter);else blit_sprite2(game_screen,x,y,*e->sprite2s,base+part);
 render_mirror_entity_end();
}
static void quartet(void){
 static const unsigned parts[]={0,1,19,20};JE_MultiEnemyType saved;memcpy(saved,enemy,sizeof(enemy));
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
 for(unsigned q=0;q<4;q++){if(q<2?enemy[current_slot].ey<=-13:enemy[current_slot].ey<=-26||enemy[current_slot].ey>=182)continue;unsigned part=parts[q];int x=enemy[current_slot].ex+(q%2?6:-6),y=enemy[current_slot].ey+(q>=2?7:-7);unsigned index=enemy[current_slot].egr[enemy[current_slot].enemycycle-1]+part;
  if(enemy[current_slot].filter)blit_sprite2_filter(classic,x,y,*enemy[current_slot].sprite2s,index,enemy[current_slot].filter);else blit_sprite2(classic,x,y,*enemy[current_slot].sprite2s,index);tile(part);
 }
 CHECK(!memcmp(saved,enemy,sizeof(enemy)));CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));SDL_FreeSurface(classic);
}
static void final_copy(void){for(int y=0;y<184;y++)memcpy((Uint8*)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,(Uint8*)game_screen->pixels+y*320+24,264);}
static Uint32 *pixel(SDL_Surface *s,int x,int y){return (Uint32*)((Uint8*)s->pixels+y*s->pitch)+x;}
/* Independent straight-alpha arithmetic, not production blend_rgba. */
static Uint32 alpha_oracle(Uint32 under,const Uint8 *a)
{
 unsigned r=(((under>>16)&255)*(255-a[3])+a[0]*a[3]+127)/255;
 unsigned g=(((under>>8)&255)*(255-a[3])+a[1]*a[3]+127)/255;
 unsigned b=((under&255)*(255-a[3])+a[2]*a[3]+127)/255;
 return 0xff000000u|(r<<16)|(g<<8)|b;
}
static void filtered_oracle(const Uint8 *a,int filter,Uint8 *f)
{
 memcpy(f,a,4);if(!filter)return;
 unsigned peak=a[0]>a[1]?a[0]:a[1];if(a[2]>peak)peak=a[2];unsigned v=(peak*15*256+127)/255,lo=v/256,hi=lo<15?lo+1:15,frac=v%256;Uint32 l=rgb_palette[(Uint8)(filter|lo)],h=rgb_palette[(Uint8)(filter|hi)];
 for(int c=0;c<3;c++){unsigned sh=16-c*8;f[c]=(((l>>sh)&255)*(256-frac)+((h>>sh)&255)*frac+128)/256;}
}
static void oracle(unsigned profile,unsigned pose)
{
 const Uint8 *rgba=global_newshf_rgba[profile*3+pose-1];if(!rgba){CHECK(enemy[0].ey+21<=0);CHECK(!global_newshf_contributed);return;}CHECK(rgba);int d=game_probe_density;struct JE_SingleEnemyType *e=enemy+current_slot;
 for(int ay=0;ay<28*d;ay++)for(int ax=0;ax<24*d;ax++){
  int x=(e->ex-6)*d+ax,y=(e->ey-7)*d+ay;if(x<0||x>=canvas->w||y<0||y>=canvas->h)continue;
  if((ay/d<14&&e->ey<=-13)||(ay/d>=14&&(e->ey<=-26||e->ey>=182)))continue;
  const Uint8 *a=rgba+4*((ay*8/d)*192+ax*8/d);Uint8 f[4];memcpy(f,a,4);
  if(e->filter){unsigned peak=a[0]>a[1]?a[0]:a[1];if(a[2]>peak)peak=a[2];unsigned v=(peak*15*256+127)/255,lo=v/256,hi=lo<15?lo+1:15,frac=v%256;Uint32 l=rgb_palette[(Uint8)(e->filter|lo)],h=rgb_palette[(Uint8)(e->filter|hi)];for(int c=0;c<3;c++){unsigned sh=16-c*8;f[c]=(((l>>sh)&255)*(256-frac)+((h>>sh)&255)*frac+128)/256;}}
  Uint32 want=alpha_oracle(palette_rgb(0x1b),f);CHECK(*pixel(canvas,x,y)==want);
 }
}
static void output_oracle(MirrorOutputKind kind,int lightx,int lighty)
{
 unsigned count=0;int d=game_probe_density;
 for(int y=0;y<184*d;y++)for(int x=24*d;x<288*d;x++)if(global_newshf_owner[(size_t)y*canvas->w+x]){
  Uint32 want=*pixel(canvas,x,y);
  if(kind==MIRROR_OUTPUT_NORMAL15_NIGHT){Uint8 before=((Uint8*)game_screen->pixels)[(y/d)*320+x/d],after=((Uint8*)VGAScreenSeg->pixels)[(y/d)*320+x/d-24];want=normal15_rgba(want,before,after,normal15_branch(x/d-24,y/d,lightx,lighty)<0);}
  CHECK(*pixel(output,x-24*d,y)==want);count++;
 }
 CHECK(count>0);
}
static void positives(void)
{
 int filters[]={0,0x70,0x80,9};int ys[]={80,-25,-20,-13,-12,-6,0,181,182,195};
 for(int d=4;d<=8;d+=4)for(unsigned p=0;p<3;p++)for(unsigned pose=1;pose<=3;pose++)for(unsigned f=0;f<4;f++){
  setup(d);birth(p,pose,110,80,filters[f]);quartet();CHECK(global_newshf_contributed&&!global_newshf_fault);oracle(p,pose);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready&&last_output_valid);CHECK(global_newshf_cached);output_oracle(MIRROR_OUTPUT_ORDINARY,0,0);
 }
 for(unsigned y=0;y<COUNTOF(ys);y++){setup(4);birth(y%3,1,110,ys[y],0);quartet();CHECK(!global_newshf_fault);oracle(y%3,1);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);}
}
static void negatives(void)
{
 for(unsigned k=0;k<11;k++){
  setup(4);birth(0,1,110,80,0);tile(0);CHECK(global_newshf_contributed);Uint8 saved=bank_original[100];
  switch(k){case 0:bank_original[100]^=1;break;case 1:enemySpriteSheetIds[0]=1;break;case 2:enemySpriteSheetIds[1]=10;enemySpriteSheets[1]=enemySpriteSheets[0];break;case 3:rgb_palette[0]^=1;break;case 4:enemyDat[163].value++;break;case 5:render_mirror_newshf_validation_bank_changed(&enemySpriteSheets[0]);break;case 6:render_mirror_newshf_validation_allocated(enemy,5,0);break;case 7:enemy[0].enemycycle=2;break;case 8:enemy[0].sprite2s=&enemySpriteSheets[1];break;case 9:enemy[0].ex++;break;case 10:enemy[0].filter=0x70;break;}
  final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready&&!last_output_valid);bank_original[100]=saved;
 }
 setup(4);birth(0,1,110,80,0);tile(1);tile(0);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready);
 setup(4);birth(0,1,110,80,0);quartet();final_copy();render_mirror_finish(MIRROR_OUTPUT_UNSUPPORTED,0,0);CHECK(!ready);
}
static void talon(void)
{
 global_talon_pose(1,spriteSheet9,233,233,0);CHECK(render_mirror_global_player_ship(game_screen,104,73,spriteSheet9,233,MIRROR_NORMAL,1,233)==1);blit_sprite2x2(game_screen,104,73,spriteSheet9,233);render_mirror_entity_end();CHECK(global_talon_contributed&&!global_talon_fault);
}
static void additional(void)
{
 setup(4);birth(0,1,310,80,0);quartet();final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready);
 setup(4);birth(0,1,110,80,0);quartet();talon();CHECK(global_newshf_contributed);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);
 setup(4);birth(0,1,110,80,0);quartet();talon();Uint8 bank_saved=bank_original[100];bank_original[100]^=1;final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready&&!last_output_valid);bank_original[100]=bank_saved;
 /* The conservative NEWSHF transparent-over-foreign policy rejects all HD. */
 setup(4);talon();birth(0,1,110,80,0);quartet();final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready);
 setup(4);birth(0,1,110,80,0);quartet();final_copy();((Uint8*)VGAScreenSeg->pixels)[80*320+86]^=1;render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready);
 setup(4);birth(0,1,110,80,0);quartet();final_copy();render_mirror_finish(MIRROR_OUTPUT_NORMAL15_LOW_DETAIL,0,0);CHECK(ready);output_oracle(MIRROR_OUTPUT_NORMAL15_LOW_DETAIL,0,0);

 for(int light=0;light<3;light++){
  int lx=light==0?264:light==1?170:0,ly=light==0?0:light==1?80:200;
  setup(4);birth(light,2,110,80,0);quartet();
  for(int y=0;y<184;y++)for(int x=0;x<264;x++)((Uint8*)VGAScreenSeg->pixels)[y*320+x]=normal15_index(((Uint8*)game_screen->pixels)[y*320+x+24],x,y,lx,ly);
  render_mirror_finish(MIRROR_OUTPUT_NORMAL15_NIGHT,lx,ly);CHECK(ready&&last_output_valid);output_oracle(MIRROR_OUTPUT_NORMAL15_NIGHT,lx,ly);
 }
 /* Complete submission first: these must fail on the proof itself, not merely
  * because an interrupted quartet already causes fallback. */
 for(unsigned k=0;k<7;k++){
  setup(4);birth(0,1,110,80,0);quartet();CHECK(global_newshf_contributed&&!global_newshf_fault);Uint8 saved=bank_original[100];
  if(k==0)fprintf(stderr,"NEGATIVE-CONTROL completed bank mutation\n");
  switch(k){case 0:bank_original[100]^=1;break;case 1:enemySpriteSheetIds[0]=1;break;case 2:enemySpriteSheetIds[1]=10;enemySpriteSheets[1]=enemySpriteSheets[0];break;case 3:rgb_palette[0]^=1;break;case 4:enemyDat[163].value++;break;case 5:render_mirror_newshf_validation_bank_changed(&enemySpriteSheets[0]);break;case 6:render_mirror_newshf_validation_allocated(enemy,5,0);break;}
  final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready&&!last_output_valid);bank_original[100]=saved;
 }

 setup(4);birth(0,1,110,80,0);quartet();global_newshf_rgba[0][31]^=1;final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready);
 setup(4);birth(0,1,110,80,0);quartet();final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);rgb_palette[0]^=1;global_newshf_check_cache();CHECK(!ready&&!last_output_valid);
 setup(4);birth(0,1,110,80,0);quartet();final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);((Uint8*)game_screen->pixels)[0]^=1;global_newshf_check_cache();CHECK(!ready&&!last_output_valid);
 /* Native JE_drawEnemy moves actors and clears filters AFTER valid draw. */
 setup(4);birth(1,2,110,80,0x70);quartet();enemy[0].ex+=3;enemy[0].ey+=2;enemy[0].filter=0;final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);
 /* Ordinary later native writes occlude the true-color owner. */
 setup(4);birth(2,3,110,80,0);quartet();Uint8 *p=(Uint8*)game_screen->pixels+80*320+110;*p=0x3a;render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);for(int y=0;y<4;y++)for(int x=0;x<4;x++)CHECK(*pixel(output,(110-24)*4+x,80*4+y)==palette_rgb(0x3a));
 /* Cache bank ABA cannot survive its pre-free notification. */
 setup(4);birth(0,1,110,80,0);quartet();final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);render_mirror_newshf_validation_bank_changed(&enemySpriteSheets[0]);CHECK(!ready&&!last_output_valid);
 setup(4);birth(0,1,110,80,0);quartet();final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);render_mirror_fade_start(NULL,NULL,0,255);CHECK(!ready&&!have_fade_saved);
 /* Reallocating a completed contributor must revoke its old frame proof. */
 setup(4);birth(0,1,110,80,0);quartet();render_mirror_newshf_validation_allocated(enemy,163,0);CHECK(!ready);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready);
 const char *valid=resource_root;const char *modes[]={"missing","corrupt","header","trailing"};
 for(unsigned i=0;i<9;i++)for(unsigned mode=0;mode<4;mode++){char root[4096];snprintf(root,sizeof(root),"%s/%s%u",valid,modes[mode],i);resource_root=root;setup(4);birth(i/3,i%3+1,110,80,0);quartet();CHECK(!global_newshf_good&&!global_newshf_contributed);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready);}
 resource_root=valid;
}
/* Test-only authored samples: loader/payload integrity is proven first; then
 * an explicitly restamped in-memory fixture exercises every alpha endpoint.
 * No production pin or loader bypass is used for real packaged art checks. */
static void fixture_alpha(unsigned phase,int ax,int ay,unsigned alpha,bool solid)
{
 CHECK(global_newshf_family_ready());Uint8 *rgba=global_newshf_rgba[phase];
 if(solid)for(unsigned n=0;n<192u*224u;n++){rgba[4*n]=73;rgba[4*n+1]=149;rgba[4*n+2]=211;rgba[4*n+3]=255;}
 Uint8 *p=rgba+4*(ay*192+ax);p[0]=73;p[1]=149;p[2]=211;p[3]=(Uint8)alpha;
 global_newshf_rgba_stamp[phase]=global_bytes_hash(rgba,192u*224u*4u);
}
static void sample_coordinate(bool native,int *ax,int *ay)
{
 Uint8 src[168],mask[168];CHECK(decode_tile(global_newshf_bank(),55,src,mask,12,0,0));
 for(int y=1;y<13;y++)for(int x=1;x<11;x++)if((mask[y*12+x]!=0)==native){*ax=x*8;*ay=y*8;return;}
 CHECK(false);
}
static void soft_alpha(void)
{
 const unsigned alphas[]={0,2,1,127,254,255};
 for(int d=4;d<=8;d+=4)for(unsigned filtered=0;filtered<2;filtered++)for(unsigned native=0;native<2;native++)for(unsigned k=0;k<COUNTOF(alphas);k++){
  setup(d);birth(2,1,110,80,filtered?0x70:0);int ax,ay;sample_coordinate(native,&ax,&ay);fixture_alpha(6,ax,ay,alphas[k],false);
  quartet();CHECK(global_newshf_contributed&&!global_newshf_fault);oracle(2,1);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready&&last_output_valid);output_oracle(MIRROR_OUTPUT_ORDINARY,0,0);
 }
 for(int d=4;d<=8;d+=4)for(unsigned filtered=0;filtered<2;filtered++)for(unsigned native=0;native<2;native++)for(unsigned k=0;k<COUNTOF(alphas);k++){
  setup(d);birth(2,1,110,80,filtered?0x70:0);int ax,ay;sample_coordinate(native,&ax,&ay);fixture_alpha(6,ax,ay,alphas[k],true);
  int x=104*d+ax*d/8,y=73*d+ay*d/8;size_t n=(size_t)y*canvas->w+x;hd_owner[n]=1;*pixel(canvas,x,y)=0xff3864a2u;
  quartet();bool reject=alphas[k]<255&&(alphas[k]!=0||native);
  CHECK(global_newshf_fault==reject);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);
  if(reject){CHECK(!ready&&!last_output_valid);CHECK(global_newshf_rejected_frame);}else {CHECK(ready);if(alphas[k]==255){Uint8 f[4];filtered_oracle(global_newshf_rgba[6]+4*(ay*192+ax),filtered?0x70:0,f);CHECK(*pixel(output,x-24*d,y)==alpha_oracle(0xff3864a2u,f));}else CHECK(!global_newshf_owner[n]);}
 }
 /* Same-owner overlap uses the prior proven NEWSHF RGB exactly once. */
 for(int d=4;d<=8;d+=4)for(unsigned filtered=0;filtered<2;filtered++)for(unsigned native=0;native<2;native++)for(unsigned k=0;k<COUNTOF(alphas);k++){
  setup(d);birth(2,1,110,80,filtered?0x70:0);int ax,ay;sample_coordinate(native,&ax,&ay);fixture_alpha(6,ax,ay,alphas[k],true);quartet();CHECK(!global_newshf_fault);
  int x=104*d+ax*d/8,y=73*d+ay*d/8;Uint32 before=*pixel(canvas,x,y);const Uint8 *a=global_newshf_rgba[6]+4*(ay*192+ax);Uint8 f[4];filtered_oracle(a,filtered?0x70:0,f);Uint32 want=alpha_oracle(before,f);
  birth_at(1,2,1,110,80,filtered?0x70:0);quartet();CHECK(!global_newshf_fault);CHECK(*pixel(canvas,x,y)==want);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);CHECK(*pixel(output,x-24*d,y)==want);
 }
 /* A foreign partial sample must revoke NEWSHF RGB copied to another owner. */
 setup(4);birth(2,1,110,80,0);int ax,ay;sample_coordinate(true,&ax,&ay);fixture_alpha(6,ax,ay,255,true);quartet();Uint8 *prior_owner=malloc(global_newshf_capacity);CHECK(prior_owner);memcpy(prior_owner,global_newshf_owner,global_newshf_capacity);talon();CHECK(global_newshf_contributed);unsigned copied=0;for(size_t i=0;i<global_newshf_capacity;i++)if(prior_owner[i]&&global_talon_owner[i]&&global_talon_foreign[i]&&!global_newshf_owner[i])copied++;free(prior_owner);CHECK(copied>0);
 fixture_alpha(6,ax,ay,2,true);int x=104*4+ax/2,y=73*4+ay/2;size_t n=(size_t)y*canvas->w+x;hd_owner[n]=1;global_newshf_owner[n]=0;
 birth_at(1,2,1,110,80,0);quartet();CHECK(global_newshf_fault&&global_newshf_rejected_frame);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready&&!last_output_valid);
 /* Soft source corruption, cached corruption, and fade retirement remain closed. */
 for(unsigned mode=0;mode<3;mode++){
  setup(4);birth(2,1,110,80,0);sample_coordinate(true,&ax,&ay);fixture_alpha(6,ax,ay,127,false);quartet();final_copy();
  if(mode==0){global_newshf_rgba[6][4*(ay*192+ax)+3]^=1;render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready);}
  else {render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);if(mode==1){global_newshf_rgba[6][4*(ay*192+ax)+3]^=1;global_newshf_check_cache();CHECK(!ready&&!last_output_valid);}else {render_mirror_fade_start(NULL,NULL,0,255);CHECK(!ready&&!have_fade_saved);}}
 }
 /* A later native write still wins over soft true-color ownership. */
 setup(4);birth(2,1,110,80,0);sample_coordinate(true,&ax,&ay);fixture_alpha(6,ax,ay,127,false);quartet();int lx=104+ax/8,ly=73+ay/8;Uint8 *index=(Uint8*)game_screen->pixels+ly*320+lx;*index=0x3a;render_mirror_pixel(game_screen,index,*index,MIRROR_NORMAL);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);for(int sy=0;sy<4;sy++)for(int sx=0;sx<4;sx++)CHECK(*pixel(output,(lx-24)*4+sx,ly*4+sy)==palette_rgb(0x3a));
}
int main(int argc,char **argv)
{
 CHECK(argc==2);resource_root=argv[1];read_exact(bank_original,sizeof(bank_original));read_exact(original_records,sizeof(original_records));read_exact(normal_palette,sizeof(normal_palette));Uint32 bank_size;read_exact(&bank_size,4);spriteSheet9.size=bank_size;spriteSheet9.data=malloc(bank_size);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,bank_size);CHECK(fgetc(stdin)==EOF);positives();negatives();additional();soft_alpha();printf("PASS native NEWSHF compositor: %u cases, %u assertions; actual production allocation and sprite blits; not E1 gameplay acceptance\n",cases,checks);return 0;
}
