/* Controlled native renderer only; no gameplay witness or live scene claim.
 * New ninth mode; all eight inherited dispatch bodies/stdin remain unchanged. */
static const char *enemy70_pack;
static Uint8 enemy70_record[80],enemy70_port[82];
static Asset *enemy70_asset(void){return &enemy_vulcan70_resource_state.member;}
static void enemy70_setup(void){bolts745_setup();}
static void enemy70_draw(int x,int y){blue_draw_bank(70,x,y,spriteSheet8);}
static bool enemy70_union_cell(unsigned c)
{
 Uint8 source[168],mask[168];blue_decode(70,source,mask);if(mask[c])return true;
 const Uint8 *rgba=enemy70_asset()->rgba;CHECK(rgba);
 for(unsigned yy=0;yy<8;yy++)for(unsigned xx=0;xx<8;xx++)if(rgba[4*((c/12*8+yy)*96+c%12*8+xx)+3])return true;
 return false;
}
static unsigned enemy70_halo(void)
{
 Uint8 source[168],mask[168];blue_decode(70,source,mask);const Uint8 *rgba=enemy70_asset()->rgba;CHECK(rgba);
 for(unsigned n=0;n<10752;n++)if(rgba[n*4+3]&&rgba[n*4+3]<255&&!mask[(n/96/8)*12+n%96/8])return n;
 CHECK(false);return 0;
}
/* Independent integer RGBA alpha oracle: existing test alpha(), never the
 * renderer's blend_rgba. Native-only alpha0 restores saved background; halo
 * alpha blends the real pre-native underlay. No outside-mask clipping. */
static void enemy70_oracle(int x,int y,const PulsesBefore *b,bool final)
{
 Uint8 source[168],mask[168];blue_decode(70,source,mask);const Uint8 *rgba=enemy70_asset()->rgba;CHECK(rgba);
 unsigned cells=0,nonzero=0,soft=0,halo=0,halo_opaque=0,union_texels=0;
 for(unsigned c=0;c<168;c++)cells+=mask[c]!=0;
 for(unsigned n=0;n<10752;n++) {
  unsigned c=(n/96/8)*12+n%96/8;const Uint8 *q=rgba+4*n;bool support=mask[c]||q[3];
  nonzero+=q[3]!=0;soft+=q[3]!=0&&q[3]!=255;halo+=q[3]!=0&&!mask[c];halo_opaque+=q[3]==255&&!mask[c];union_texels+=support;
  int px=x*8+(int)(n%96),py=y*8+(int)(n/96);if(px<0||px>=2560||py<0||py>=1600)continue;
  size_t p=(size_t)py*2560+px;Uint32 want=support?alpha(b->under[n],q):b->canvas[n];
  if(support){CHECK(global_projectile91_owner[p]==1&&hd_owner[p]==1);CHECK(global_projectile91_used_members&131072u);}
  else CHECK(global_projectile91_owner[p]==b->owned[n]);
  CHECK(((Uint8 *)game_screen->pixels)[(py/8)*320+px/8]==(mask[c]?source[c]:b->native[c]));
  if(final){if(px<192||px>=2304||py>=1472)continue;CHECK(*at(output,px-192,py)==want);}
  else CHECK(*at(canvas,px,py)==want);
 }
 CHECK(cells==46&&nonzero==2674&&soft==400&&halo==110);CHECK(halo_opaque==36&&union_texels==3054);
}
static void enemy70_valid(int x,int y,PulsesBefore *b)
{
 pulses16694_snapshot(b,x,y);enemy70_draw(x,y);
 CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
 CHECK(global_projectile91_used_members&131072u);bolts745_callbacks_seen(70,x,y);enemy70_oracle(x,y,b,false);
}
static void enemy70_handoff(bool final)
{
 for(unsigned c=0;c<168;c++)if(enemy70_union_cell(c)) {
  SDL_Surface *s=final?VGAScreenSeg:game_screen;
  Uint8 *p=(Uint8 *)s->pixels+(80+c/12)*s->pitch+110+c%12-(final?24:0);Uint8 before=*p;*p=58;render_mirror_pixel(s,p,before,MIRROR_NORMAL);
 }
 for(unsigned n=0;n<10752;n++)CHECK(!global_projectile91_owner[(size_t)(640+n/96)*2560+880+n%96]);
 CHECK(global_projectile91_contributed&&global_projectile91_used_members==131072u);
}
/* Decline is intentional: the native INDEX8 cell, not a stale HD cache,
 * owns presentation. The direct shared hook must not patch any partial cell. */
static void enemy70_declined(void)
{CHECK(!ready&&!last_output_valid&&!global_projectile91_cached&&!have_fade_saved&&fade_mode==0);}
static void enemy70_final_decline(int gx,int gy,bool direct,const Uint32 *recovery_palette)
{
 Uint32 before_canvas[64],before_output[64],before_fade[64];Uint8 owner[64],hd[64],foreign[64];
 bool saved=have_fade_saved;unsigned index=(unsigned)gy*320+gx-24;Uint8 before_index=last_output_indices[index];
 CHECK(ready&&last_output_valid&&global_projectile91_cached);
 for(unsigned n=0;n<64;n++){int px=gx*8+n%8,py=gy*8+n/8;size_t k=(size_t)py*2560+px;
  before_canvas[n]=*at(canvas,px,py);before_output[n]=*at(output,px-192,py);if(saved)before_fade[n]=*at(fade_saved,px-192,py);
  owner[n]=global_projectile91_owner[k];hd[n]=hd_owner[k];foreign[n]=global_projectile91_foreign[k];}
 Uint8 *p=(Uint8 *)VGAScreenSeg->pixels+gy*VGAScreenSeg->pitch+gx-24;*p=58;
 if(direct){global_projectile91_final_pixel(VGAScreenSeg,p);enemy70_declined();CHECK(last_output_indices[index]==before_index);
 for(unsigned n=0;n<64;n++){int px=gx*8+n%8,py=gy*8+n/8;size_t k=(size_t)py*2560+px;
  CHECK(*at(canvas,px,py)==before_canvas[n]&&*at(output,px-192,py)==before_output[n]);
  if(saved)CHECK(*at(fade_saved,px-192,py)==before_fade[n]);
  CHECK(global_projectile91_owner[k]==owner[n]&&hd_owner[k]==hd[n]&&global_projectile91_foreign[k]==foreign[n]);}}
 /* Actual JE_pix protocol supplies the new index; later family hooks may retire
  * their own pixels, but cannot resurrect the invalid shared cached frame. */
 render_mirror_pixel(VGAScreenSeg,p,58,MIRROR_NORMAL);enemy70_declined();CHECK(*p==58);
 CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));enemy70_declined();
 /* Native INDEX8 remains authoritative for the entire expanded cell. This
  * proves fallback selection/index, not a GPU/native-present pixel capture. */
 CHECK(*p==58);
 /* Restore only after the faded write/decline was fully observed, so the new
  * epoch can independently re-admit the canonical enemy palette. */
 if(recovery_palette)memcpy(rgb_palette,recovery_palette,sizeof(rgb_palette));
 SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();
 PulsesBefore b;enemy70_valid(110,80,&b);finish();CHECK(ready&&last_output_valid);enemy70_oracle(110,80,&b,true);
}
/* Current old17 direct rendering regressions, not their historical fault matrices. */
static void enemy70_old17(void)
{
 for(unsigned i=0;i<14;i++) {
  enemy70_setup();PulsesBefore b;unsigned id=bolts745_ids[i];bolts745_valid(id,110,80,&b);
  CHECK(global_projectile91_used_members==(1u<<i));finish();CHECK(ready&&last_output_valid);bolts745_oracle(id,110,80,&b,true);
 }
 for(unsigned i=0;i<3;i++) {
  enemy70_setup();PulsesBefore b;unsigned id=animated153_ids[i];animated153_valid(id,110,80,&b);
  CHECK(global_projectile91_used_members==(16384u<<i));finish();CHECK(ready&&last_output_valid);animated153_oracle(id,110,80,&b,true);
 }
}
static void enemy70_basics(void)
{
 enemy70_setup();PulsesBefore b;enemy70_valid(110,80,&b);CHECK(global_projectile91_member(70)==131072u);
 enemy70_valid(110,80,&b);finish();CHECK(ready);enemy70_oracle(110,80,&b,true);global_projectile91_check_cache();CHECK(ready);
 SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();CHECK(!global_projectile91_used_members);
 enemy70_valid(110,80,&b);finish();CHECK(ready);enemy70_oracle(110,80,&b,true);
 enemy70_setup();
 for(unsigned i=0;i<14;i++)bolts745_draw(bolts745_ids[i],30+(i%7)*35,20+(i/7)*45);
 for(unsigned i=0;i<3;i++)bolts745_draw(animated153_ids[i],30+i*35,110);
 CHECK(global_projectile91_used_members==131071u);enemy70_valid(180,110,&b);
 CHECK(global_projectile91_used_members==262143u);finish();CHECK(ready&&last_output_valid);
}
static void enemy70_files(void)
{
 static const char *kinds[]={"missing","bad","header","magic","density","width","height","anchorx","anchory","short","trailing"};
 const char *saved=valid_root;char path[1200];
 for(unsigned k=0;k<11;k++)for(unsigned warm=0;warm<2;warm++) {
  int n=snprintf(path,sizeof(path),"%s/%s70",enemy70_pack,kinds[k]);CHECK(n>0&&(size_t)n<sizeof(path));valid_root=path;enemy70_setup();
  if(warm){for(unsigned i=0;i<14;i++)bolts745_draw(bolts745_ids[i],30+(i%7)*35,20+(i/7)*45);for(unsigned i=0;i<3;i++)bolts745_draw(animated153_ids[i],30+i*35,110);CHECK(global_projectile91_used_members==131071u);}
  enemy70_draw(200,110);CHECK(!(global_projectile91_used_members&131072u)&&!global_projectile91_fault);finish();
  if(warm)CHECK(ready&&global_projectile91_used_members==131071u);else CHECK(!ready&&!global_projectile91_contributed);
 }
 valid_root=saved;
}
static void enemy70_player_birth(int *x,int *y);
static void enemy70_player_draw(int x,int y);
/* Actual player allocation/draw retains an independently owned HD output while
 * the retired enemy contribution keeps its resource/background dependencies. */
static void enemy70_retire_to_player(int x,int y)
{
 enemy70_player_draw(x,y);Uint8 src[168],mask[168];blue_decode(70,src,mask);
 for(unsigned n=0;n<10752;n++) {
  size_t k=(size_t)(y*8+n/96)*2560+x*8+n%96;
  CHECK(!global_projectile91_owner[k]);
  if(mask[n/96/8*12+n%96/8]||enemy70_asset()->rgba[n*4+3])CHECK(global_vulcan_owner[k]&&hd_owner[k]);
 }
 CHECK(global_projectile91_contributed&&global_projectile91_used_members==131072u&&global_vulcan_contributed);
 CHECK(global_vulcan_rgba[1]&&global_vulcan_rgba[1]!=enemy70_asset()->rgba);
 CHECK(!memcmp(global_vulcan_rgba[1],enemy70_asset()->rgba,43008));
}
static void enemy70_integrity(void)
{
 for(unsigned mode=0;mode<3;mode++) {
  enemy70_setup();PulsesBefore b;int x=110,y=80;if(mode==2)enemy70_player_birth(&x,&y);enemy70_valid(x,y,&b);
  if(mode==2)enemy70_retire_to_player(x,y);if(mode){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);}
  enemy70_asset()->rgba[128]^=1;if(mode)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
 enemy70_setup();CHECK(enemy_vulcan70_resource(valid_root));enemy70_asset()->rgba[128]^=1;
 for(unsigned i=0;i<14;i++)bolts745_draw(bolts745_ids[i],30+(i%7)*35,20+(i/7)*45);
 for(unsigned i=0;i<3;i++)bolts745_draw(animated153_ids[i],30+i*35,110);
 finish();CHECK(ready&&global_projectile91_used_members==131071u);
 for(unsigned mode=0;mode<4;mode++) {
  enemy70_setup();PulsesBefore b;int x=110,y=80;if(mode==3)enemy70_player_birth(&x,&y);enemy70_valid(x,y,&b);unsigned n=enemy70_halo();
  CHECK(global_projectile91_used_colors[27]);Uint32 before=*at(canvas,x*8+n%96,y*8+n/96);
  Uint8 src[168],mask[168];blue_decode(70,src,mask);unsigned transparent=10752;
  for(unsigned z=0;z<10752;z++)if(mask[z/96/8*12+z%96/8]&&!enemy70_asset()->rgba[z*4+3]){transparent=z;break;}
  CHECK(transparent<10752);CHECK(*at(canvas,x*8+transparent%96,y*8+transparent/96)==(0xff000000u|(rgb_palette[27]&0xffffffu)));
  CHECK(before==alpha(0xff000000u|(rgb_palette[27]&0xffffffu),enemy70_asset()->rgba+4*n));
  if(mode==1)enemy70_handoff(false);if(mode==3)enemy70_retire_to_player(x,y);if(mode>=2){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);}
  rgb_palette[27]^=1;if(mode>=2)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
  SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();
  enemy70_valid(110,80,&b);finish();CHECK(ready);enemy70_oracle(110,80,&b,true);
 }
 for(unsigned final=0;final<2;final++) {
  enemy70_setup();PulsesBefore b;enemy70_valid(110,80,&b);unsigned n=enemy70_halo(),cx=n%96/8,cy=n/96/8;
  if(final){finish();CHECK(ready);enemy70_final_decline(110+cx,80+cy,true,NULL);continue;}SDL_Surface *s=game_screen;
  Uint8 *p=(Uint8 *)s->pixels+(80+cy)*s->pitch+110+cx-(final?24:0);Uint8 old=*p;*p=58;render_mirror_pixel(s,p,old,MIRROR_NORMAL);
  for(unsigned yy=0;yy<8;yy++)for(unsigned xx=0;xx<8;xx++)CHECK(!global_projectile91_owner[(size_t)(640+cy*8+yy)*2560+880+cx*8+xx]);
  if(!final)finish();CHECK(ready);for(unsigned yy=0;yy<8;yy++)for(unsigned xx=0;xx<8;xx++)CHECK(*at(output,688+cx*8+xx,640+cy*8+yy)==(0xff000000u|(rgb_palette[58]&0xffffffu)));
 }
 for(unsigned mode=0;mode<4;mode++) {
  enemy70_setup();PulsesBefore b;enemy70_valid(110,80,&b);if(mode&1){finish();CHECK(ready);}
  if(mode<2)rgb_palette[113]^=1;else livebank[7684]^=1;
  if(mode&1)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void enemy70_scope(void)
{
 for(unsigned mode=0;mode<7;mode++) {
  enemy70_setup();if(mode==0)xmas=true;else if(mode==1)game_probe_density=4;else if(mode==2)game_probe_missing=true;else if(mode==3)game_probe_invalid=true;else if(mode==4)game_probe_original_reference=true;else if(mode==6)rgb_palette[113]^=1;
  if(mode==5){Sprite2_array other={spriteSheet8.size,spriteSheet8.data+1};CHECK(!render_mirror_enemy_shot(game_screen,110,80,other,70));}else enemy70_draw(110,80);
  CHECK(!global_projectile91_contributed&&!global_projectile91_used_members);
 }
 enemy70_setup();SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
 blit_sprite2(classic,110,80,spriteSheet8,70);draw_player_shot_sprite2(game_screen,110,80,spriteSheet8,70,0,70);
 CHECK(!memcmp(classic->pixels,game_screen->pixels,64000)&&!global_projectile91_contributed);SDL_FreeSurface(classic);
}
/* Decode only actual pinned record227 and port7, then use the unchanged real
 * allocator/public witness hooks. No synthetic owner or role grants. */
static unsigned enemy70_u16(const Uint8 **p){unsigned v=(*p)[0]+256u*(*p)[1];*p+=2;return v;}
static void enemy70_player_tables(void)
{
 const Uint8 *p=enemy70_record;JE_WeaponType *w=&weapons[227];memset(w,0,sizeof(*w));
 w->drain=enemy70_u16(&p);w->shotrepeat=*p++;w->multi=*p++;w->weapani=enemy70_u16(&p);w->max=*p++;w->tx=*p++;w->ty=*p++;w->aim=*p++;
 memcpy(w->attack,p,8);p+=8;memcpy(w->del,p,8);p+=8;memcpy(w->sx,p,8);p+=8;memcpy(w->sy,p,8);p+=8;memcpy(w->bx,p,8);p+=8;memcpy(w->by,p,8);p+=8;
 for(unsigned j=0;j<8;j++)w->sg[j]=enemy70_u16(&p);
 w->acceleration=(int8_t)*p++;w->accelerationx=(int8_t)*p++;w->circlesize=*p++;w->sound=*p++;w->trail=*p++;w->shipblastfilter=*p++;CHECK(p==enemy70_record+80);
 p=enemy70_port;unsigned length=*p++;memcpy(weaponPort[7].name,p,30);render_mirror_front_port_name(7,length,weaponPort[7].name);weaponPort[7].name[MIN(length,30)]=0;p+=30;weaponPort[7].opnum=*p++;
 for(unsigned j=0;j<2;j++)for(unsigned i=0;i<11;i++)weaponPort[7].op[j][i]=enemy70_u16(&p);
 weaponPort[7].cost=enemy70_u16(&p);weaponPort[7].itemgraphic=enemy70_u16(&p);weaponPort[7].poweruse=enemy70_u16(&p);CHECK(p==enemy70_port+82);render_mirror_front_port_loaded(7);CHECK(global_vulcan_table(227));
}
static void enemy70_player_birth(int *x,int *y)
{
 enemy70_player_tables();memset(playerShotData,0,sizeof(playerShotData));memset(shotAvail,0,sizeof(shotAvail));memset(shotMultiPos,0,sizeof(shotMultiPos));power=10000;galagaMode=false;
 player[0].items.weapon[0].id=7;player[0].items.weapon[0].power=7;player[0].weapon_mode=1;
 render_mirror_front_call_begin(7,0,6,0,1,227);int last=player_shot_create(7,0,120,90,120,90,227,1);render_mirror_front_call_end();
 CHECK(last==(int)weapons[227].multi-1&&shotAvail[0]&&global_vulcan_slots[0].role&&global_vulcan_slots[0].claimed);
 PlayerShotDataType *s=playerShotData;CHECK(s->shotGr==70&&s->shotAniMax==1);s->shotAni=0;*x=s->shotX+1;*y=s->shotY;
}
static void enemy70_player_draw(int x,int y)
{draw_player_shot_sprite2(game_screen,x,y,spriteSheet8,70,0,70);CHECK(global_vulcan_contributed&&!global_vulcan_fault&&!global_vulcan_call.live);}
static void enemy70_player_overlap(void)
{
 for(unsigned order=0;order<2;order++) {
  enemy70_setup();int x,y;enemy70_player_birth(&x,&y);PulsesBefore b;
  if(!order){enemy70_player_draw(x,y);pulses16694_snapshot(&b,x,y);enemy70_draw(x,y);enemy70_oracle(x,y,&b,false);}
  else {enemy70_valid(x,y,&b);pulses16694_snapshot(&b,x,y);enemy70_player_draw(x,y);
   CHECK(global_vulcan_rgba[1]&&global_vulcan_rgba[1]!=enemy70_asset()->rgba);
   Uint8 src[168],mask[168];blue_decode(70,src,mask);
   for(unsigned n=0;n<10752;n++){const Uint8 *q=global_vulcan_rgba[1]+4*n;unsigned c=n/96/8*12+n%96/8;if(!mask[c]&&!q[3])continue;
    size_t p=(size_t)(y*8+n/96)*2560+x*8+n%96;CHECK(global_vulcan_owner[p]&&!global_projectile91_owner[p]);CHECK(*at(canvas,x*8+n%96,y*8+n/96)==alpha(b.under[n],q));}
  }
  CHECK(global_vulcan_rgba[1]&&global_vulcan_rgba[1]!=enemy70_asset()->rgba);
  CHECK(!memcmp(global_vulcan_rgba[1],enemy70_asset()->rgba,43008));
  CHECK(global_vulcan_contributed&&global_projectile91_contributed);finish();CHECK(ready&&last_output_valid);
  if(!order)enemy70_oracle(x,y,&b,true);
  else {Uint8 src[168],mask[168];blue_decode(70,src,mask);
   for(unsigned n=0;n<10752;n++){const Uint8 *q=global_vulcan_rgba[1]+4*n;unsigned c=n/96/8*12+n%96/8;
    Uint32 want=(mask[c]||q[3])?alpha(b.under[n],q):b.canvas[n];CHECK(*at(output,x*8+n%96-192,y*8+n/96)==want);}}

  if(order){enemy70_asset()->rgba[128]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);}
  else {weapons[227].sound^=1;global_vulcan_check_cache();CHECK(!ready&&!last_output_valid);}
 }
}
/* Three actual-route sparse/foreign cached-write boundaries, not arbitrary
 * owner-bit synthesis or a claim about every historical foreign family. */
static void enemy70_sparse_foreign_final(void)
{
 enemy70_setup();PulsesBefore b;enemy70_valid(110,80,&b);unsigned halo=enemy70_halo();finish();CHECK(ready);
 Uint32 recovery_palette[256];memcpy(recovery_palette,rgb_palette,sizeof(recovery_palette));
 SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);
 CHECK(!ready&&last_output_valid&&have_fade_saved&&fade_mode==1&&global_projectile91_cached);
 /* The actual engine changes the live palette before each integer fade step. */
 for(unsigned i=0;i<256;i++){Uint32 old=rgb_palette[i],next=old&0xff000000u;
  for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}rgb_palette[i]=next;}
 render_mirror_fade_step(7);CHECK(ready&&last_output_valid&&global_projectile91_cached&&have_fade_saved&&fade_mode==1);
 enemy70_final_decline(110+halo%96/8,80+halo/96/8,true,recovery_palette);
 for(unsigned full=0;full<2;full++) {
  enemy70_setup();int x,y;enemy70_player_birth(&x,&y);int ex=x-(full?0:1);
  enemy70_valid(ex,y,&b);enemy70_player_draw(x,y);finish();CHECK(ready&&last_output_valid);
  bool found=false;
  for(unsigned c=0;c<168&&!found;c++) {
   int gx=ex+c%12,gy=y+c/12;unsigned shared=0,player_owned=0;
   for(unsigned n=0;n<64;n++){size_t k=(size_t)(gy*8+n/8)*2560+gx*8+n%8;shared+=global_projectile91_owner[k]!=0;player_owned+=global_vulcan_owner[k]!=0;}
   if(full?(!shared&&player_owned):(shared&&shared<64&&player_owned)) {
    CHECK(global_projectile91_contributed&&(global_projectile91_used_members&131072u)&&global_vulcan_contributed);
    enemy70_final_decline(gx,gy,false,NULL);found=true;
   }
  }
  CHECK(found);
 }
}
/* A separate enemy lease must not reset or replace the established player
 * allocation. Root changes are explicit enemy-only shutdown epochs. */
static void enemy70_player_lease_unchanged(const Uint8 *saved,uint64_t generation)
{
 CHECK(global_vulcan_rgba[1]==saved&&saved);
 CHECK(asteroid1_stamp(saved,43008)==UINT64_C(0x6c26e938d94472c2));
 CHECK(global_vulcan_slots[0].role&&global_vulcan_slots[0].generation==generation);
}
static void enemy70_root_and_warm_identity(void)
{
 enemy70_setup();int x,y;enemy70_player_birth(&x,&y);enemy70_player_draw(x,y);
 const Uint8 *player_payload=global_vulcan_rgba[1];uint64_t generation=global_vulcan_slots[0].generation;
 enemy70_player_lease_unchanged(player_payload,generation);
 Asset *first=enemy_vulcan70_resource(valid_root);CHECK(first&&first->rgba!=player_payload);
 Uint8 *enemy_payload=first->rgba;CHECK(!memcmp(enemy_payload,player_payload,43008));
 CHECK(enemy_vulcan70_resource(valid_root)==first&&first->rgba==enemy_payload);
 char badroot[1200];int n=snprintf(badroot,sizeof(badroot),"%s/missing70",enemy70_pack);CHECK(n>0&&(size_t)n<sizeof(badroot));
 CHECK(!enemy_vulcan70_resource(badroot));CHECK(enemy_vulcan70_resource(valid_root)==first&&first->rgba==enemy_payload);
 CHECK(!memcmp(enemy_payload,player_payload,43008));enemy70_player_lease_unchanged(player_payload,generation);
 enemy_vulcan70_shutdown();enemy70_player_lease_unchanged(player_payload,generation);
 CHECK(!enemy_vulcan70_resource(badroot)&&enemy_vulcan70_resource_state.checked&&!enemy_vulcan70_resource_state.valid);
 CHECK(!enemy_vulcan70_resource(valid_root));enemy70_player_lease_unchanged(player_payload,generation);
 enemy_vulcan70_shutdown();Asset *recovered=enemy_vulcan70_resource(valid_root);CHECK(recovered&&recovered->rgba!=player_payload);
 CHECK(!memcmp(recovered->rgba,player_payload,43008));enemy70_player_lease_unchanged(player_payload,generation);
 CHECK(!global_projectile91_contributed&&!global_projectile91_used_members);finish();CHECK(ready&&last_output_valid);
 enemy70_player_lease_unchanged(player_payload,generation);
 for(unsigned cached=0;cached<2;cached++) {
  enemy70_setup();PulsesBefore b;enemy70_valid(110,80,&b);if(cached){finish();CHECK(ready);}
  if(cached)enemy70_asset()->w=11;else enemy70_asset()->bank=9;
  if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid);
 }
}
static void enemy70_bounds_and_fades(void)
{
 enemy70_setup();PulsesBefore b;enemy70_valid(110,-6,&b);finish();CHECK(ready);enemy70_oracle(110,-6,&b,true);
 enemy70_setup();enemy70_draw(-1,80);CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);
 for(unsigned bad=0;bad<2;bad++) {
  enemy70_setup();enemy70_valid(110,80,&b);finish();CHECK(ready);SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(have_fade_saved&&global_projectile91_cached);
  if(bad){livebank[7684]^=1;CHECK(!global_projectile91_fade_step_valid(7));CHECK(!ready&&!last_output_valid);}
  else {for(unsigned i=0;i<256;i++){Uint32 old=rgb_palette[i],next=old&0xff000000u;for(int sh=0;sh<24;sh+=8){int v=(old>>sh)&255;next|=(Uint32)(v+(0-v)/7)<<sh;}rgb_palette[i]=next;}
   CHECK(global_projectile91_fade_step_valid(7));render_mirror_fade_step(7);CHECK(ready&&last_output_valid);global_projectile91_check_cache();CHECK(ready&&last_output_valid);}
 }
}
static int enemy70_main(int argc,char **argv)
{
 CHECK(argc==3&&!strcmp(argv[1],"--enemy-vulcan70"));enemy70_pack=argv[2];static char root[1200];int n=snprintf(root,sizeof(root),"%s/valid",enemy70_pack);CHECK(n>0&&(size_t)n<sizeof(root));valid_root=missing_root=root;
 read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));Uint32 count;read_exact(&count,4);CHECK(count==33484);spriteSheet9.size=count;spriteSheet9.data=malloc(count);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,count);
 Uint32 xn;read_exact(&xn,4);CHECK(xn==32404);Uint8 *xb=malloc(xn);CHECK(xb);read_exact(xb,xn);free(xb);read_exact(enemy70_record,80);read_exact(enemy70_port,82);CHECK(fgetc(stdin)==EOF);
 unsigned initial_cases=cases,initial_checks=checks;enemy70_old17();enemy70_basics();enemy70_files();enemy70_integrity();enemy70_scope();enemy70_player_overlap();enemy70_root_and_warm_identity();enemy70_bounds_and_fades();enemy70_sparse_foreign_final();
 CHECK(cases-initial_cases==75);printf("PASS enemy Vulcan70 native: %u setup cases %u assertions; canonical RGBA internal8 only; NOT gameplay\n",cases-initial_cases,checks-initial_checks);return 0;
}
