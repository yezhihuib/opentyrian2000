/* SPDX-License-Identifier: GPL-2.0-or-later
 * ASTEROID1 display-only compatibility for finite original warm and shield effects.
 * Keep the indexed blitter and first-level known-blend policy authoritative.
 * Semantic source pins include both all168 palette bytes and168 coverage bytes;
 * re-decode each callback so same-address source changes cannot reuse trust.
 */
static const struct {unsigned index;uint64_t source;} asteroid1_effect_blend_pins[]={
 {3,UINT64_C(0x2e61f1f6070604fd)},
 {4,UINT64_C(0xdc3ceea1c5514aac)},
 {5,UINT64_C(0xa87af1558c7ae217)},
 {6,UINT64_C(0x504f70b78c0f7e6f)},
 {7,UINT64_C(0xb2e509202ff4ef90)},
 {8,UINT64_C(0x237bc8a7d4c52c32)},
 {9,UINT64_C(0xa280189c329992be)},
 {10,UINT64_C(0x8104ec386a150adf)},
 {11,UINT64_C(0xbd962696f9630124)},
 {12,UINT64_C(0xb795ca89afa634e3)},
 {13,UINT64_C(0x0441060b9b683c23)},
 {14,UINT64_C(0xf826f451f85f20c7)},
 {22,UINT64_C(0x2546b5275eaee713)},
 {23,UINT64_C(0x61ee66c056d671c9)},
 {24,UINT64_C(0x24c8048523afb137)},
 {25,UINT64_C(0x4f5a4eb8be8c2d8f)},
 {26,UINT64_C(0xfc5b591992cdb307)},
 {27,UINT64_C(0xd5b51e3cf5506897)},
 {28,UINT64_C(0x38514330b2dbac64)},
 {29,UINT64_C(0x292b7f61e358787f)},
 {30,UINT64_C(0x3bbcefcfa0fa372b)},
 {31,UINT64_C(0xcda87b3b811e213f)},
 {32,UINT64_C(0xe06accca495c2414)},
 {33,UINT64_C(0x7e0a84708189e78d)},
 {41,UINT64_C(0x41ef72ae6a360dda)},
 {42,UINT64_C(0x77277f09f0c8c68d)},
 {43,UINT64_C(0xfeb972e0c81552d7)},
 {44,UINT64_C(0xeafdd42a49dbb490)},
 {45,UINT64_C(0x2440342efcac933c)},
 {46,UINT64_C(0x341b507ce8fcdcef)},
 {47,UINT64_C(0x7606768aac814155)},
 {48,UINT64_C(0xa7a9a5d6a2f049df)},
 {49,UINT64_C(0xf0e4ddbbfb1b1886)},
 {50,UINT64_C(0x1e91155d230c2780)},
 {51,UINT64_C(0x5fc05ae03fa22e64)},
 {52,UINT64_C(0x9e0fc75d252b84c0)},
 {60,UINT64_C(0x7ce3e99e6bd945fd)},
 {61,UINT64_C(0x8914c27bad17de85)},
 {62,UINT64_C(0x5f62c5178b163e23)},
 {63,UINT64_C(0xec66c1fe8447fa0f)},
 {64,UINT64_C(0xd0b408e7c2602b2a)},
 {65,UINT64_C(0xacb4cad17d918134)},
 {66,UINT64_C(0x21e6abf813fd28d2)},
 {67,UINT64_C(0xba68108b442034fd)},
 {68,UINT64_C(0x1841e6670023a1e3)},
 {69,UINT64_C(0xb42351cea21b3ab7)},
 {70,UINT64_C(0xe74687ee6163f82c)},
 {71,UINT64_C(0x4a6b109344fc515b)},
 {122,UINT64_C(0x19b7637c1469f360)},
 {123,UINT64_C(0x18f02cc5cb8df708)},
 {124,UINT64_C(0x25792af6c594081b)},
 {125,UINT64_C(0x0a9bc24f99095a66)},
 {126,UINT64_C(0xca99f5c48782db68)},
 {127,UINT64_C(0x3967c31439aea00b)},
 {128,UINT64_C(0x37a292527580e81c)},
 {129,UINT64_C(0xba48bc2b6760813f)},
 {130,UINT64_C(0xf8a796418cb59a12)},
 {131,UINT64_C(0x1769e0a1c6fde96b)},
 {132,UINT64_C(0x0ee1f2c21d3ecff4)},
 {133,UINT64_C(0xf8ab18755d8866de)},
 {145,UINT64_C(0x7560c3259e9e9462)},
 {146,UINT64_C(0x728bd1411bf93862)},
 {147,UINT64_C(0xa194be258be5966d)},
 {148,UINT64_C(0x6862b82d59cc892e)},
 {149,UINT64_C(0x20c0c0769a07dad0)},
 {150,UINT64_C(0x08ac828d16156290)},
 {151,UINT64_C(0xaf6f6ea168572b9c)},
 {152,UINT64_C(0xe512543cd3019da8)},
 {154,UINT64_C(0x28b7539fa21528fe)},
 {155,UINT64_C(0x2b9ffbf9aa19d703)},
 {156,UINT64_C(0xa64d6bc11698dd88)},
 {157,UINT64_C(0x489c9fd07d33ebfa)},
 {158,UINT64_C(0x62a6ccc7c6908400)},
 {159,UINT64_C(0x4c7b197bff8d608e)},
 {160,UINT64_C(0x66b24ae52634a13f)},
 {161,UINT64_C(0xae193a08ac123853)},
 {162,UINT64_C(0x56c753414635ff56)},
 {163,UINT64_C(0x7385b7ba77b39b44)},
 {164,UINT64_C(0xaf96975f23fcb926)},
 {165,UINT64_C(0xc636cd657db93490)},
 {173,UINT64_C(0xcfada978853964a9)},
 {174,UINT64_C(0xb3ca93e234cc9a31)},
 {175,UINT64_C(0x2791696291d8b014)},
 {176,UINT64_C(0x8e31b37e90b8b4f3)},
 {177,UINT64_C(0x3e1350f3271bfc4b)},
 {178,UINT64_C(0xcc1cbc44b053ff27)},
 {179,UINT64_C(0x7b7c158e32e4deb1)},
 {180,UINT64_C(0x08547540c52ab520)},
 {181,UINT64_C(0xa5be976fefb3d385)},
 {182,UINT64_C(0x6ea86996ef2f24fb)},
 {183,UINT64_C(0x69f332915ce4ac12)},
 {184,UINT64_C(0x749f688542a9d50f)},
 {192,UINT64_C(0xd6381a5bbe45562e)},
 {193,UINT64_C(0x7c4b9ff864db30a1)},
 {194,UINT64_C(0x9c1cd08fdd712b82)},
 {195,UINT64_C(0x460ce65b4a4e902b)},
 {196,UINT64_C(0xa22dc2b68f879d4f)},
 {197,UINT64_C(0x3263f44ab7ecebe3)},
 {198,UINT64_C(0x0adc5dfe64b04ee2)},
 {199,UINT64_C(0xf37b88787b5feefc)},
 {200,UINT64_C(0xd61efe74f61c8896)},
 {201,UINT64_C(0x9b584abc77e86d58)},
 {202,UINT64_C(0xa7c7e3667be0cd95)},
 {203,UINT64_C(0x0df9157841dc77df)},
 {211,UINT64_C(0x95a5e9cf6438d632)},
 {212,UINT64_C(0x8dfaa790f57cf67d)},
 {213,UINT64_C(0x3b2c2627404768e5)},
 {214,UINT64_C(0xba2a29f9f517ba35)},
 {215,UINT64_C(0xcb0a8c38198633e8)},
 {216,UINT64_C(0x699541d8e035301b)},
 {217,UINT64_C(0xca9d3f88bdb4c2c4)},
 {218,UINT64_C(0x0538f7b1f6805f0a)},
 {219,UINT64_C(0x379fd93e2dde8d34)},
 {220,UINT64_C(0x1dcbd459786ac633)},
 {221,UINT64_C(0xe3ecf4834c445143)},
 {222,UINT64_C(0xcaa8e08819302202)},
};

/* Original shield pieces:27 animation slots,22 nonempty. The five empty
 * slots251/270/271/273/274 produce no writes and receive no new admission. */
static const struct {unsigned index;uint64_t source;} asteroid1_shield_blend_pins[]={
 {229,UINT64_C(0x8c135499d13963be)},
 {230,UINT64_C(0x1bb9953e3b238540)},
 {231,UINT64_C(0xb5537a992563eb0d)},
 {232,UINT64_C(0x7305539d6b6b17d1)},
 {233,UINT64_C(0xe72e4a3d5818c55a)},
 {234,UINT64_C(0x4f656159fa007c86)},
 {235,UINT64_C(0x0aef691b1ca24a95)},
 {236,UINT64_C(0x7e42bb7eb832ac9d)},
 {237,UINT64_C(0xe91cc9956d4c7023)},
 {248,UINT64_C(0x2580739d6e2a343f)},
 {249,UINT64_C(0x552fe5439ccd6fdc)},
 {250,UINT64_C(0x07d477b0c0eedb40)},
 {252,UINT64_C(0xa4cfe017190810ca)},
 {253,UINT64_C(0x1b89e4401f5a0dae)},
 {254,UINT64_C(0x8d7cfcf03c183cd0)},
 {255,UINT64_C(0x16b217048c05fb49)},
 {256,UINT64_C(0xaac64f1476d44802)},
 {267,UINT64_C(0xd2f814b0b46162fb)},
 {268,UINT64_C(0xd2f814b0b46162fb)},
 {269,UINT64_C(0xd2f814b0b46162fb)},
 {272,UINT64_C(0xc22e38bed2cee2a5)},
 {275,UINT64_C(0xc3db252a0712543b)},
};

static bool asteroid1_effect_blend_layout(SDL_Surface *surface)
{
 int d=game_probe_density;
 if((d!=4&&d!=8)||!surface||surface!=game_screen||surface!=VGAScreen||
    !surface->pixels||!surface->format||surface->w!=320||surface->h!=200||surface->pitch!=320||
    surface->format->format!=SDL_PIXELFORMAT_INDEX8||surface->format->BitsPerPixel!=8||
    surface->format->BytesPerPixel!=1||!canvas||!canvas->pixels||!canvas->format||
    canvas->w!=320*d||canvas->h!=200*d||canvas->pitch<canvas->w*4||canvas->pitch%4||
    (uintptr_t)canvas->pixels%sizeof(Uint32)||canvas->format->format!=SDL_PIXELFORMAT_ARGB8888||
    canvas->format->BitsPerPixel!=32||canvas->format->BytesPerPixel!=4||
    !hd_owner||!cloud_owner||!green_first)return false;
 uintptr_t a=(uintptr_t)surface->pixels,b=(uintptr_t)canvas->pixels;
 return a<b?b-a>=(size_t)surface->pitch*surface->h:a-b>=(size_t)canvas->pitch*canvas->h;
}

static bool asteroid1_effect_blend_source(Sprite2_array bank,unsigned int index,Uint8 source,int ox,int oy,int x,int y)
{
 /* The native un-clipped blitter may wrap horizontally through its pitch.
  * Admit only conventional origins; preserve its old fallback everywhere else.
  * Widen before subtraction so hostile origin coordinates cannot overflow. */
 if(xmas||!bank.data||bank.data!=explosionSpriteSheet.data||bank.size!=17810||
    bank.size!=explosionSpriteSheet.size||ox<0||ox>308||oy<=-14||oy>=200||
    ((source&240)!=0x70&&(source&240)!=0x40&&(source&240)!=0x80))return false;
 int64_t lx=(int64_t)x-ox,ly=(int64_t)y-oy;
 if(lx<0||lx>=12||ly<0||ly>=14)return false;
 uint64_t wanted=0;
 if((source&240)==0x80) {
  for(unsigned i=0;i<sizeof(asteroid1_shield_blend_pins)/sizeof(*asteroid1_shield_blend_pins);i++)
   if(index==asteroid1_shield_blend_pins[i].index){wanted=asteroid1_shield_blend_pins[i].source;break;}
 } else {
  for(unsigned i=0;i<sizeof(asteroid1_effect_blend_pins)/sizeof(*asteroid1_effect_blend_pins);i++)
   if(index==asteroid1_effect_blend_pins[i].index){wanted=asteroid1_effect_blend_pins[i].source;break;}
 }
 if(!wanted)return false;
 Uint8 decoded[12*14*2]={0};
 if(!decode_tile(bank,index,decoded,decoded+12*14,12,0,0))return false;
 unsigned cell=(unsigned)(ly*12+lx);
 if(!decoded[12*14+cell]||decoded[cell]!=source)return false;
 uint64_t stamp=UINT64_C(0xcbf29ce484222325);
 for(size_t i=0;i<sizeof(decoded);i++){stamp^=decoded[i];stamp*=UINT64_C(0x100000001b3);}
 return stamp==wanted;
}

static void asteroid1_sprite2_blend_pixel(SDL_Surface *surface,Uint8 *address,Uint8 source,Sprite2_array bank,unsigned int index,int ox,int oy)
{
 /* Fallbacks retain complete-region restoration and now identify the actual
  * Sprite2 command. No global known-blend toggle or asset admission is changed. */
 bool measurable=active&&surface==game_screen&&surface&&surface->pixels&&surface->pitch>0;
 intptr_t off=measurable?(intptr_t)address-(intptr_t)surface->pixels:-1;
 measurable=measurable&&off>=0&&off<(intptr_t)surface->pitch*surface->h;
 int x=measurable?(int)(off%surface->pitch):-1,y=measurable?(int)(off/surface->pitch):-1;
 measurable=measurable&&x<320&&y<200;
 bool known=bank.data&&bank.data==explosionSpriteSheet.data&&bank.size==explosionSpriteSheet.size&&
            index&&2*(size_t)index<=bank.size;
 Uint8 before=measurable?expected[y*320+x]:0;
 unsigned old_blocks=local_blocks,subpixels=0;
 bool layout=measurable&&asteroid1_effect_blend_layout(surface);
 int d=game_probe_density;
 if(layout)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)
  if(hd_owner[(y*d+sy)*canvas->w+x*d+sx]==1)++subpixels;
 bool rgba=layout&&asteroid_hd_enabled&&asteroid1_level_scope()&&
  (game_probe_enabled||(asteroid_hd_lease&&asteroid1_scope()))&&
  !game_probe_original_reference&&!suppress&&!reject_reason&&
  (asteroid1_effect_blend_source(bank,index,source,ox,oy,x,y)||
   asteroid1_talon_blend_source(bank,index,source,ox,oy,x,y))&&effect_ramp_monotone(source&240)&&
  *address==(Uint8)((source&240)|(((before&15)+(source&15))/2));
 if(rgba){font_before_effect((SDL_Rect){x,y,1,1});rgba=!reject_reason;}
 if(rgba) {
  expected[y*320+x]=*address;
  if(selected[y*320+x]){++occlusions;selected[y*320+x]=0;}
  for(int sy=0;sy<d;sy++) {
   Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+(y*d+sy)*canvas->pitch)+x*d;
   const Uint8 *owner=hd_owner+(y*d+sy)*canvas->w+x*d;
   for(int sx=0;sx<d;sx++) {
    size_t n=(size_t)(y*d+sy)*canvas->w+x*d+sx;
    green_first[n]=0;cloud_owner[n]=0;
    /* Indexed or original-reference copies stay exact. Only authored color is
     * mapped continuously to the verified current palette ramp, in draw order. */
    p[sx]=owner[sx]==1?explosion_blend_rgba(p[sx],source):palette_rgb(*address);
   }
  }
 } else {
  unsigned previous=blend_source_index;blend_source_index=index;
  render_mirror_pixel(surface,address,source,MIRROR_BLEND);blend_source_index=previous;
 }
 if(measurable)game_probe_blend_write(known,index,ox,oy,x,y,before,source,*address,subpixels,local_blocks-old_blocks,rgba);
}
