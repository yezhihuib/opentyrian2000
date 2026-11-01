/* Private fix regression: actual allocator/movement/draw; four public writes.
 * Cached decline + native-cell expansion + next-frame RGBA recovery only. */
static Uint8 pg_records[2][80];
static void pg_record(unsigned id,const Uint8 *data)
{
 const Uint8 *p=data;JE_WeaponType *w=&weapons[id];memset(w,0,sizeof(*w));
 w->drain=enemy70_u16(&p);w->shotrepeat=*p++;w->multi=*p++;w->weapani=enemy70_u16(&p);w->max=*p++;w->tx=*p++;w->ty=*p++;w->aim=*p++;
 memcpy(w->attack,p,8);p+=8;memcpy(w->del,p,8);p+=8;memcpy(w->sx,p,8);p+=8;memcpy(w->sy,p,8);p+=8;memcpy(w->bx,p,8);p+=8;memcpy(w->by,p,8);p+=8;
 for(unsigned j=0;j<8;j++)w->sg[j]=enemy70_u16(&p);
 w->acceleration=(int8_t)*p++;w->accelerationx=(int8_t)*p++;w->circlesize=*p++;w->sound=*p++;w->trail=*p++;w->shipblastfilter=*p++;CHECK(p==data+80);
}
static void pg_birth(int *x,int *y)
{
 pg_record(71,pg_records[0]);pg_record(1071,pg_records[1]);CHECK(global_green_record_valid(71)&&global_green_record_valid(1071));
 memset(playerShotData,0,sizeof(playerShotData));memset(shotAvail,0,sizeof(shotAvail));memset(shotMultiPos,0,sizeof(shotMultiPos));power=10000;galagaMode=false;
 int last=player_shot_create(0,0,120,90,120,90,71,1);CHECK(last>=0&&shotAvail[0]&&global_green_shots[0].role&&global_green_shots[0].claimed);
 ++mirror_logic_tick;global_green_identity_frame_begin();const PlayerShotDataType *s=playerShotData;
 CHECK(s->shotGr+s->shotAni==214&&!s->shotComplicated&&!s->aimAtEnemy&&s->shotXM+s->shotXC<100&&s->shotYM+s->shotYC<100);
 /* Prediction only: the actual shots.o routine performs every mutation and draw. */
 *x=(JE_integer)(s->shotX+(JE_integer)(s->shotXM+s->shotXC))+1;*y=(JE_integer)(s->shotY+(JE_integer)(s->shotYM+s->shotYC));
 background2=false;memset(explosions,0,sizeof(explosions));
}
static void pg_counts(int x,int y,unsigned *shared,unsigned *green,unsigned *hd)
{*shared=*green=*hd=0;for(unsigned j=0;j<64;j++){size_t n=(size_t)(y*8+j/8)*2560+x*8+j%8;*shared+=!!global_projectile91_owner[n];*green+=!!global_green_owner[n];*hd+=!!hd_owner[n];}}
static void pg_case(unsigned mode)
{
 pg_record(71,pg_records[0]);pg_record(1071,pg_records[1]);enemy70_setup();CHECK(global_green_source_matches(spriteSheet8)&&global_green_palette_matches());int x,y;pg_birth(&x,&y);CHECK(x>=30&&x<275&&y>=4&&y<170);
 PulsesBefore before;op_valid(3,x-2,y-3,&before);unsigned sc,gc,hc;pg_counts(x,y,&sc,&gc,&hc);CHECK(sc==1&&hc==1&&!gc);
 CHECK(global_green_family_ready());Uint8 src[168],mask[168];blue_decode(214,src,mask);CHECK(!mask[0]);Uint32 under[64];for(unsigned j=0;j<64;j++)under[j]=hd_owner[(size_t)(y*8+j/8)*2560+x*8+j%8]?*at(canvas,x*8+j%8,y*8+j/8):(0xff000000u|(rgb_palette[27]&0xffffffu));
 bool special=false;int shotx=0,shoty=0;JE_integer damage=0;JE_byte blast=0,chain=0,pnum=0;JE_word rw=0,rh=0;
 CHECK(player_shot_move_and_draw(0,&special,&shotx,&shoty,&damage,&blast,&chain,&pnum,&rw,&rh));CHECK(!special&&shotx+1==x&&shoty==y&&pnum==1);
 CHECK(global_green_contributed&&!global_green_fault&&!global_green_identity_fault&&global_green_shots[0].step&&!global_green_trail.live);
 pg_counts(x,y,&sc,&gc,&hc);CHECK(!sc&&gc==3&&hc==3);CHECK(global_projectile91_used_members==134217728u);
 for(unsigned j=0;j<64;j++){const Uint8 *a=global_green_rgba[0]+4*(j/8*96+j%8);Uint32 want=a[3]?alpha(under[j],a):under[j];if(a[3])CHECK(*at(canvas,x*8+j%8,y*8+j/8)==want);}
 CHECK(!global_projectile91_cached);global_projectile91_pre_final_rect(VGAScreenSeg,NULL);CHECK(!global_projectile91_cached&&global_projectile91_contributed);pg_counts(x,y,&sc,&gc,&hc);CHECK(!sc&&gc==3&&hc==3);
 finish();CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_green_cached);
 for(unsigned j=0;j<64;j++){const Uint8 *a=global_green_rgba[0]+4*(j/8*96+j%8);CHECK(*at(output,(x-24)*8+j%8,y*8+j/8)==(a[3]?alpha(under[j],a):under[j]));}
 Uint32 restore[256];memcpy(restore,rgb_palette,sizeof(restore));
 if(mode>=2){SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);for(unsigned i=0;i<256;i++){Uint32 c=rgb_palette[i],v=0;for(unsigned sh=0;sh<24;sh+=8){int q=(c>>sh)&255;q+=(0-q)/7;v|=(Uint32)q<<sh;}rgb_palette[i]=v;}render_mirror_fade_step(7);CHECK(ready&&last_output_valid&&global_projectile91_cached&&global_green_cached&&have_fade_saved);}
 pg_counts(x,y,&sc,&gc,&hc);CHECK(!sc&&gc==3&&hc==3);
 /* New preflight entrypoint boundaries, no fabricated ownership/cache states. */
 bool saved_before=have_fade_saved;int fade_before=fade_mode;Uint8 index_before=last_output_indices[y*320+x-24];
 SDL_Rect none[4]={{x-24,y,0,1},{x-24,y,-1,1},{-100,-100,1,1},{300,190,1,1}};
 for(unsigned j=0;j<4;j++)global_projectile91_pre_final_rect(VGAScreenSeg,&none[j]);
 SDL_Rect clip=VGAScreenSeg->clip_rect;VGAScreenSeg->clip_rect=(SDL_Rect){0,0,1,1};SDL_Rect target={x-24,y,1,1};global_projectile91_pre_final_rect(VGAScreenSeg,&target);VGAScreenSeg->clip_rect=clip;
 global_projectile91_pre_final_rect(game_screen,&target);CHECK(global_projectile91_pre_final_pixel(game_screen,(Uint8*)game_screen->pixels+y*320+x));
 int pitch=VGAScreenSeg->pitch;VGAScreenSeg->pitch=pitch+1;global_projectile91_pre_final_rect(VGAScreenSeg,&target);VGAScreenSeg->pitch=pitch;
 CHECK(ready&&last_output_valid&&global_projectile91_cached&&have_fade_saved==saved_before&&fade_mode==fade_before&&last_output_indices[y*320+x-24]==index_before);pg_counts(x,y,&sc,&gc,&hc);CHECK(!sc&&gc==3&&hc==3);
 Uint8 *p=(Uint8*)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch+x-24;*p=58;
 if(mode%2){SDL_Rect r={x-24,y,1,1};render_mirror_rect(VGAScreenSeg,&r);}else render_mirror_pixel(VGAScreenSeg,p,58,MIRROR_NORMAL);
 CHECK(!ready&&!last_output_valid&&!global_projectile91_cached&&!have_fade_saved&&fade_mode==0);CHECK(*p==58);
 /* Invalidated output/fade RGB is deliberately not required to be repainted.
  * Real HD presenter must refuse it; native INDEX8 owns the replacement. */
 SDL_Surface *screen=SDL_CreateRGBSurfaceWithFormat(0,output->w,output->h,32,SDL_PIXELFORMAT_ARGB8888);CHECK(screen);SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(screen);CHECK(renderer);
 CHECK(!render_mirror_present(renderer,VGAScreenSeg,NULL));CHECK(!ready&&!last_output_valid&&!global_projectile91_cached&&!have_fade_saved&&fade_mode==0);CHECK(*p==58);
 if(texture){SDL_DestroyTexture(texture);texture=NULL;}SDL_DestroyRenderer(renderer);SDL_FreeSurface(screen);
 /* Independent native cell expansion through SDL palette conversion/scaling,
  * not a claim that a gameplay window's presentation loop was exercised. */
 SDL_Color colors[256];for(unsigned i=0;i<256;i++){colors[i]=(SDL_Color){(rgb_palette[i]>>16)&255,(rgb_palette[i]>>8)&255,rgb_palette[i]&255,255};}
 CHECK(SDL_SetPaletteColors(VGAScreenSeg->format->palette,colors,0,256)==0);
 SDL_Surface *native=SDL_ConvertSurfaceFormat(VGAScreenSeg,SDL_PIXELFORMAT_ARGB8888,0);CHECK(native);SDL_Surface *cell=SDL_CreateRGBSurfaceWithFormat(0,8,8,32,SDL_PIXELFORMAT_ARGB8888);CHECK(cell);
 SDL_Rect native_cell={x-24,y,1,1};CHECK(SDL_BlitScaled(native,&native_cell,cell,NULL)==0);Uint32 want=0xff000000u|(rgb_palette[58]&0xffffffu);for(unsigned j=0;j<64;j++)CHECK(*at(cell,j%8,j/8)==want);SDL_FreeSurface(cell);SDL_FreeSurface(native);
 printf("DECLINE mode=%u native64=1 presenter_rejected=1 saved=0\n",mode);
 /* Fresh frame independently recovers predecessor's complete RGBA oracle. */
 memcpy(rgb_palette,restore,sizeof(restore));SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();op_valid(3,x-2,y-3,&before);finish();CHECK(ready&&last_output_valid);op_oracle(3,x-2,y-3,&before,true);
 printf("RECOVERY mode=%u exact227=1\n",mode);
}
int main(int argc,char **argv)
{
 if(argc>=2&&!strcmp(argv[1],"--protron244"))return inherited_p244_diagnostic_dispatch(argc,argv);
 CHECK(argc==2);valid_root=missing_root=argv[1];read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));Uint32 n;read_exact(&n,4);CHECK(n==33484);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);read_exact(&n,4);CHECK(n==32404);Uint8 *unused=malloc(n);CHECK(unused);read_exact(unused,n);free(unused);read_exact(enemy70_record,80);read_exact(enemy70_port,82);read_exact(pg_records,160);explosionSpriteSheet.size=17810;explosionSpriteSheet.data=malloc(17810);CHECK(explosionSpriteSheet.data);read_exact(explosionSpriteSheet.data,17810);CHECK(fgetc(stdin)==EOF);
 for(unsigned mode=0;mode<4;mode++)pg_case(mode);CHECK(cases==4);puts("PASS player-green cache fix: 4 setups; decline/native64/recovery; NOT gameplay");return 0;
}
