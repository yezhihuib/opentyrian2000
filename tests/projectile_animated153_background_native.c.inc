/* Preparation companion: include AFTER unchanged bolts745 native companion.
 * No entrypoint or automatic invocation. Future reviewed native adapter calls
 * animated153_background_cases() with qualified assets present in valid_root.
 * Background-only palette changes are regression oracles, NOT a known bug. */
static void animated153_background_cases(void)
{
 /* Old indexed pair exercises same owner; new three exercise accepted alpha0
  * edge gaps as well. No mutation of any authenticated production payload. */
 const unsigned ids[5]={7,45,153,154,155};
 for(unsigned s=0;s<5;s++)for(unsigned mode=0;mode<4;mode++) {
  unsigned id=ids[s];bolts745_setup();
  Asset *a=id==7||id==45?projectile_bolts745_resource(valid_root,id):projectile_animated153_resource(valid_root,id);
  CHECK(a&&a->rgba);Uint8 src[168],mask[168];blue_decode(id,src,mask);
  unsigned witness=10752;
  for(unsigned n=0;n<10752;n++)if(mask[(n/96/8)*12+(n%96)/8]&&!a->rgba[4*n+3]){witness=n;break;}
  CHECK(witness<10752);int wx=880+(int)(witness%96),wy=640+(int)(witness/96);
  CHECK(((Uint8 *)game_screen->pixels)[(wy/8)*320+wx/8]==27);
  Uint32 before=rgb_palette[27]&0xffffffu;
  bolts745_draw(id,110,80);CHECK(!global_projectile91_fault&&!global_projectile91_call.live);
  CHECK(global_projectile91_used_colors[27]&&global_projectile91_underlay_palette[27]==before);
  CHECK(*at(canvas,wx,wy)==(0xff000000u|before));
  if(mode>=2){finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);}
  if(mode==1||mode==3) {
   /* Legitimate later native writes revoke all remaining pixel ownership.
    * Never clear owner arrays directly to manufacture the handoff. */
   for(unsigned c=0;c<168;c++)if(mask[c]) {
    int x=110+c%12,y=80+c/12;SDL_Surface *dest=mode==3?VGAScreenSeg:game_screen;
    Uint8 *p=(Uint8 *)dest->pixels+y*dest->pitch+x-(mode==3?24:0);Uint8 old=*p;*p=58;
    render_mirror_pixel(dest,p,old,MIRROR_NORMAL);
   }
   for(unsigned n=0;n<10752;n++)CHECK(!global_projectile91_owner[(size_t)(640+n/96)*2560+880+n%96]);
   CHECK(global_projectile91_contributed&&global_projectile91_used_members==global_projectile91_member(id));
  }
  rgb_palette[27]^=1u;CHECK((rgb_palette[27]&0xffffffu)!=before);
  if(mode>=2)global_projectile91_check_cache();else finish();
  CHECK(!ready&&!last_output_valid);
  /* Same resource epoch, new frame, same location, changed palette retained. */
  SDL_FillRect(game_screen,NULL,27);SDL_FillRect(VGAScreenSeg,NULL,27);render_mirror_begin();
  CHECK(!global_projectile91_used_members&&!global_projectile91_contributed);
  bolts745_draw(id,110,80);CHECK(!global_projectile91_fault);
  CHECK(global_projectile91_underlay_palette[27]==(rgb_palette[27]&0xffffffu));
  CHECK(*at(canvas,wx,wy)==(0xff000000u|(rgb_palette[27]&0xffffffu)));
  finish();CHECK(ready&&last_output_valid);CHECK(*at(output,wx-192,wy)==(0xff000000u|(rgb_palette[27]&0xffffffu)));
 }
}
