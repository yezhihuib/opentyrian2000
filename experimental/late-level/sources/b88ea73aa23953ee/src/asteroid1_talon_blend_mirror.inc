/* SPDX-License-Identifier: GPL-2.0-or-later
 * Separate, finite normal Talon invulnerability role. This does not broaden
 * explosion-sheet admission or replace the original ship/indexed draw.
 */
static struct {
 bool valid,lease;
 Uint8 *bank;
 uint64_t tick;
 unsigned index;
 int x,y;
} asteroid1_talon_blend;
static const struct {unsigned index;uint64_t source;} asteroid1_talon_blend_pins[]={
 {229,UINT64_C(0x3039ccf24a3813c9)},
 {230,UINT64_C(0x635a7ba6a40cc3ce)},
 {231,UINT64_C(0x4671f4e4752bd3ce)},
 {232,UINT64_C(0xb8bda523f77d5ead)},
 {233,UINT64_C(0x9926ced363914e55)},
 {234,UINT64_C(0x05a23d411744639d)},
 {235,UINT64_C(0xc93fa9f51a911b4e)},
 {236,UINT64_C(0x369940597be73ebe)},
 {237,UINT64_C(0x8e9d59a9d052653d)},
 {238,UINT64_C(0x5ac8c78644eb7383)},
 {248,UINT64_C(0xc043a803bd7945bc)},
 {249,UINT64_C(0x0013f6e55ca29dad)},
 {250,UINT64_C(0xea5cf097dd8cf380)},
 {251,UINT64_C(0x7362348361652579)},
 {252,UINT64_C(0xb91fe403723a8017)},
 {253,UINT64_C(0x8fc0dca692bb9d1a)},
 {254,UINT64_C(0x86b2a02d4b7dbe10)},
 {255,UINT64_C(0xb7ab4cf95818a3da)},
 {256,UINT64_C(0x50d17fa4d559a5dc)},
 {257,UINT64_C(0x72aa5b104aa72411)},
};

static void asteroid1_talon_blend_reset(void)
{memset(&asteroid1_talon_blend,0,sizeof(asteroid1_talon_blend));}

static void asteroid1_talon_blend_pose(unsigned pnum,Sprite2_array bank,int base,int index,unsigned invulnerable,int x,int y)
{
 asteroid1_talon_blend_reset();
 if(!asteroid_hd_enabled||xmas||twoPlayerMode||galagaMode||twoPlayerLinked||pnum!=1||
    base!=233||index<229||index>237||!(index&1)||!invulnerable||
    !bank.data||bank.data!=spriteSheet9.data||bank.size!=33484||bank.size!=spriteSheet9.size||
    x<5||x>301||y<=-21||y>=207)return;
 asteroid1_talon_blend.valid=true;asteroid1_talon_blend.bank=bank.data;
 asteroid1_talon_blend.tick=mirror_logic_tick;asteroid1_talon_blend.index=(unsigned)index;
 asteroid1_talon_blend.x=x-5;asteroid1_talon_blend.y=y-7;
}

static void asteroid1_talon_blend_begin(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index,int style,int layout)
{
 asteroid1_talon_blend.lease=false;
 if(!asteroid1_talon_blend.valid||asteroid1_talon_blend.tick!=mirror_logic_tick||
    !asteroid_hd_enabled||xmas||twoPlayerMode||galagaMode||twoPlayerLinked||
    surface!=game_screen||style!=MIRROR_BLEND||layout!=ENTITY_QUAD||
    !bank.data||bank.data!=spriteSheet9.data||bank.data!=asteroid1_talon_blend.bank||
    bank.size!=33484||bank.size!=spriteSheet9.size||
    index!=asteroid1_talon_blend.index||x!=asteroid1_talon_blend.x||y!=asteroid1_talon_blend.y)return;
 asteroid1_talon_blend.lease=true;
}

static void asteroid1_talon_blend_end(void)
{asteroid1_talon_blend.lease=false;}

static bool asteroid1_talon_blend_source(Sprite2_array bank,unsigned index,Uint8 source,int ox,int oy,int x,int y)
{
 if(!asteroid1_talon_blend.lease||!asteroid1_talon_blend.valid||
    asteroid1_talon_blend.tick!=mirror_logic_tick||xmas||twoPlayerMode||galagaMode||twoPlayerLinked||
    !bank.data||bank.data!=spriteSheet9.data||bank.data!=asteroid1_talon_blend.bank||
    bank.size!=33484||bank.size!=spriteSheet9.size||(source&240)!=0x10||
    ox<0||ox>308||oy<=-14||oy>=200)return false;
 unsigned base=asteroid1_talon_blend.index;
 int dx=0,dy=0;
 if(index==base){}
 else if(index==base+1)dx=12;
 else if(index==base+19)dy=14;
 else if(index==base+20){dx=12;dy=14;}
 else return false;
 if(ox!=asteroid1_talon_blend.x+dx||oy!=asteroid1_talon_blend.y+dy)return false;
 int64_t lx=(int64_t)x-ox,ly=(int64_t)y-oy;
 if(lx<0||lx>=12||ly<0||ly>=14)return false;
 uint64_t wanted=0;
 for(unsigned i=0;i<sizeof(asteroid1_talon_blend_pins)/sizeof(*asteroid1_talon_blend_pins);i++)
  if(index==asteroid1_talon_blend_pins[i].index){wanted=asteroid1_talon_blend_pins[i].source;break;}
 if(!wanted)return false;
 Uint8 decoded[336]={0};
 if(!decode_tile(bank,index,decoded,decoded+168,12,0,0))return false;
 unsigned cell=(unsigned)(ly*12+lx);
 if(!decoded[168+cell]||decoded[cell]!=source)return false;
 uint64_t stamp=UINT64_C(0xcbf29ce484222325);
 for(size_t i=0;i<sizeof(decoded);i++){stamp^=decoded[i];stamp*=UINT64_C(0x100000001b3);}
 return stamp==wanted;
}
