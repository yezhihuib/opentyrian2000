/* Extracted, unchanged production player_shot_create/move coverage. This harness
 * never launches the game. Original records are supplied by private, generated
 * includes, not duplicated here. All 22 ordinary Sonic rows and their +1000 copies are exercised for
 * all three source item tables. Only M1 P3/P5/P6/P7 use selected IDs223/224;
 * associated242/243 stay SOURCE/UNIT only. Original linked direction is tested
 * across all17 bins, for11/28/33, without any linked-HD claim.
 *
 * weapon-records.inc must define:
 *   static const JE_WeaponType weapon_tables[3][WEAP_NUM+1];
 * in tyrian.hdt, tyrian4.lvl, tyrian5.lvl order. The generated include contains
 * the initializer. shot-functions.inc contains the exact production functions.
 */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <float.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef uint8_t Uint8;
typedef uint8_t JE_byte;
typedef uint16_t JE_word;
typedef int16_t JE_integer;
typedef int8_t JE_shortint;
typedef bool JE_boolean;
typedef unsigned int uint;
typedef float JE_real;
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#ifndef M_PI_2
#define M_PI_2 1.57079632679489661923
#endif
#define WEAP_NUM 2000
#define PORT_NUM 60
#define MAX_PWEAPON 81
#include "shot-types.inc"
#include "weapon-records.inc"
static const JE_WeaponType *weapons;

static PlayerShotDataType playerShotData[MAX_PWEAPON+1];
static JE_byte shotAvail[MAX_PWEAPON], shotMultiPos[11], shotRepeat[11], soundQueue[8];
static struct { JE_word poweruse; } weaponPort[PORT_NUM+1];
static JE_word power;
static struct { int delta_x_shot_move, delta_y_shot_move; } player[2];
static struct { int scoreitem, ex, ey; } enemy[100];
static JE_byte enemyAvail[100];
static JE_word x, y;
static bool background2;
static int shadowYDist=9;
typedef struct { int unused; } SDL_Surface;
static SDL_Surface screen, *VGAScreen=&screen;
typedef struct { int tag; } Sprite2_array;
static Sprite2_array spriteSheet8={8}, spriteSheet12={12};
enum { ENTITY_NORMAL, ENTITY_BLEND, ENTITY_SHADOW, ENTITY_TILE };
#define OPTION_SHAPES 0
static struct { unsigned width, height; } unused_sprite;
static const void *unused_sprite_ptr(void)
{
    assert(!"unexpected special sprite");
    return &unused_sprite;
}
#define sprite(...) ((void)unused_sprite_ptr(), &unused_sprite)

typedef struct {
    unsigned requests, emits, draws, shadows, moves, offscreen_moves;
    unsigned drift_phase_cases, phase_cases, capacity_cases, power_cases, repeat_cases;
    unsigned boundary_cases, rng_calls;
    unsigned selected_emits[2], selected_moves[2], selected_shadow_orders[2];
    unsigned associated_emits[2], associated_moves[2], associated_shadow_orders[2];
    unsigned linked_cases, linked_center_cases, linked_boundary_cases;
    unsigned linked_bin_mask, linked_selected_cases[2], linked_associated_cases[2];
    uint64_t full_hash, normalized_hash;
} TableStats;
static TableStats table_stats[3], *stats;
static unsigned table_index;
static const char *const table_names[3]={"tyrian.hdt", "tyrian4.lvl", "tyrian5.lvl"};

/* Canonical little-endian 32-bit words, never struct bytes/padding or native
 * endian values. FNV-1a64 is a deterministic regression/parity digest, not a
 * cryptographic provenance claim. The normalized digest omits only the known
 * HDT=208 / episode4/5=192 blast-filter difference. Everything else, including
 * shot slots, source phases, failed/partial creates and actual draw order, is
 * common to both digests. */
static void hash_word_into(uint64_t *hash, uint32_t value)
{
    for (unsigned i=0; i<4; ++i) {
        *hash ^= value & 255U;
        *hash *= UINT64_C(1099511628211);
        value >>= 8;
    }
}
static void hash_word(int64_t value)
{
    hash_word_into(&stats->full_hash, (uint32_t)value);
    hash_word_into(&stats->normalized_hash, (uint32_t)value);
}
static void hash_blast(unsigned value)
{
    assert(value==(table_index==0 ? 208U : 192U));
    hash_word_into(&stats->full_hash, value);
    hash_word_into(&stats->normalized_hash, 0);
}
static void hash_shot(unsigned id)
{
    const PlayerShotDataType *s=playerShotData+id;
    hash_word(id); hash_word(shotAvail[id]);
    hash_word(s->shotX); hash_word(s->shotY);
    hash_word(s->shotXM); hash_word(s->shotYM);
    hash_word(s->shotXC); hash_word(s->shotYC);
    hash_word(s->shotComplicated);
    hash_word(s->shotDevX); hash_word(s->shotDirX);
    hash_word(s->shotDevY); hash_word(s->shotDirY);
    hash_word(s->shotCirSizeX); hash_word(s->shotCirSizeY);
    hash_word(s->shotTrail); hash_word(s->shotGr);
    hash_word(s->shotAni); hash_word(s->shotAniMax);
    hash_word(s->shotDmg); hash_blast(s->shotBlastFilter);
    hash_word(s->chainReaction); hash_word(s->playerNumber);
    hash_word(s->aimAtEnemy); hash_word(s->aimDelay); hash_word(s->aimDelayMax);
}
static int oblique_member(unsigned id)
{
    return id==223 ? 0 : id==224 ? 1 : -1;
}
static int associated_member(unsigned id)
{
    return id==242 ? 0 : id==243 ? 1 : -1;
}
static unsigned ordinary_id(unsigned rid)
{
    return rid>=1000 ? rid-1000 : rid;
}
static unsigned next_phase(unsigned previous, unsigned max)
{
    return previous==max || previous>8 ? 1 : previous+1;
}
static int clamp(int n, int lo, int hi)
{
    return n<lo ? lo : n>hi ? hi : n;
}

typedef struct {
    unsigned rid, port, owner, initial_phase, next_phase, available, count, results;
    unsigned slots[8];
    int dx, dy, result;
    const char *reason;
} CreateExpectation;
static CreateExpectation expected;
static struct { int x, y, style, bank; unsigned id; } events[2];
static unsigned event_count, probe_draw_count;
static int moving_shot;

static void assert_created(unsigned slot, unsigned phase)
{
    const JE_WeaponType *w=weapons+expected.rid;
    const PlayerShotDataType *s=playerShotData+slot;
    unsigned p=phase-1;
    int vx=w->sx[p]+(w->del[p]==98 ? clamp(expected.dx,-5,5) : 0);
    int vy=w->del[p]==100 ? clamp(expected.dy-w->sy[p],-4,4) : -w->sy[p];
    assert(w->del[p]==98 || w->del[p]==100 || (ordinary_id(expected.rid)==446 && w->del[p]==255));
    assert(s->shotX==130+w->bx[p] && s->shotY==100+w->by[p]);
    assert(s->shotXM==vx && s->shotYM==vy);
    assert(s->shotXC==w->accelerationx && s->shotYC==-w->acceleration);
    assert(s->shotGr==w->sg[p] && s->shotAni==0 && s->shotAniMax==1);
    assert(shotAvail[slot]==w->del[p] && s->shotDmg==w->attack[p]);
    assert(s->shotBlastFilter==w->shipblastfilter && s->playerNumber==expected.owner);
    assert(s->shotTrail==255 && !s->shotComplicated && !s->chainReaction);
    assert(!s->shotDevX && !s->shotDirX && !s->shotDevY && !s->shotDirY);
    assert(!s->shotCirSizeX && !s->shotCirSizeY && !s->aimAtEnemy);
    assert(!s->aimDelay && !s->aimDelayMax);
}
static unsigned game_probe_shot_begin(JE_word port, uint bay, JE_word wp,
                                     JE_byte p, JE_word px, JE_word py)
{
    assert(port==expected.port && bay==1 && wp==expected.rid);
    assert((ordinary_id(wp)>=276 && ordinary_id(wp)<=297) || ordinary_id(wp)==446);
    assert(p==expected.owner && px==130 && py==100);
    ++stats->requests;
    hash_word(0x10); hash_word(stats->requests); hash_word(wp);
    hash_word(expected.initial_phase); hash_word(expected.dx); hash_word(expected.dy);
    hash_word(power); hash_word(expected.available);
    return stats->requests;
}
static void game_probe_shot_emit(unsigned call, int multi, int phase, int id)
{
    assert(call==stats->requests && expected.count<expected.available);
    assert(multi==(int)expected.count+1 && id==(int)expected.slots[expected.count]);
    expected.next_phase=next_phase(expected.next_phase, weapons[expected.rid].max);
    assert(phase==(int)expected.next_phase && shotMultiPos[1]==phase);
    assert_created((unsigned)id, (unsigned)phase);
    ++expected.count; ++stats->emits;
    int member=oblique_member(playerShotData[id].shotGr);
    if (member>=0) ++stats->selected_emits[member];
    member=associated_member(playerShotData[id].shotGr);
    if (member>=0) ++stats->associated_emits[member];
    hash_word(0x11); hash_word(multi); hash_word(phase); hash_shot((unsigned)id);
}
static void game_probe_shot_result(unsigned call, const char *reason, int n, int id)
{
    assert(call==stats->requests && !expected.results);
    assert(strcmp(reason,expected.reason)==0 && n==(int)expected.count && id==expected.result);
    ++expected.results;
    hash_word(0x12); hash_word(strcmp(reason,"power")==0 ? 0 : strcmp(reason,"capacity")==0 ? 1 : 2);
    hash_word(n); hash_word(id); hash_word(power);
    hash_word(shotMultiPos[1]); hash_word(shotRepeat[1]); hash_word(soundQueue[2]);
}
static void game_probe_shot_draw(int shot, JE_word raw, int bank, int frame,
                                int px, int py, int style, int w, int h)
{
    assert(shot==moving_shot && bank==8 && raw==playerShotData[shot].shotGr);
    assert(frame==raw && frame>0 && px>-100 && py>-100);
    assert(w==12 && h==14 && (style==ENTITY_NORMAL || style==ENTITY_SHADOW));
    assert(probe_draw_count==event_count && probe_draw_count<2);
    ++probe_draw_count;
    hash_word(0x20); hash_word(shot); hash_word(raw); hash_word(bank);
    hash_word(frame); hash_word(px); hash_word(py); hash_word(style);
    hash_word(w); hash_word(h);
}
static void draw_entity_sprite2(SDL_Surface *s, int px, int py,
                                Sprite2_array bank, unsigned id, int style, int layout)
{
    assert(s==VGAScreen && bank.tag==8 && layout==ENTITY_TILE);
    assert(event_count<2 && probe_draw_count==event_count+1);
    events[event_count].x=px; events[event_count].y=py;
    events[event_count].id=id; events[event_count].style=style;
    events[event_count++].bank=bank.tag;
    ++stats->draws;
    if (style==ENTITY_SHADOW) ++stats->shadows;
    else assert(style==ENTITY_NORMAL);
    hash_word(0x21); hash_word(moving_shot); hash_word(px); hash_word(py);
    hash_word(bank.tag); hash_word(id); hash_word(style); hash_word(layout);
}
#define JE_setupExplosion(...) assert(!"unexpected trail")
#define JE_doSP(...) assert(!"unexpected special source")
#define blit_sprite_blend(...) assert(!"unexpected special blend")
/* A future RNG dependency in either extracted production function must fail. */
#define rand(...) (++stats->rng_calls, assert(!"unexpected gameplay RNG"), 0)
#define random(...) (++stats->rng_calls, assert(!"unexpected gameplay RNG"), 0)
#define mt_rand(...) (++stats->rng_calls, assert(!"unexpected gameplay RNG"), 0U)
#define mt_rand_1(...) (++stats->rng_calls, assert(!"unexpected gameplay RNG"), 0.0)
#define srand(...) (++stats->rng_calls, assert(!"unexpected gameplay RNG seed"))
#include "shot-functions.inc"

static void reset(void)
{
    memset(playerShotData,0,sizeof(playerShotData));
    memset(shotAvail,0,sizeof(shotAvail));
    memset(shotMultiPos,0,sizeof(shotMultiPos));
    memset(shotRepeat,0,sizeof(shotRepeat));
    memset(soundQueue,0,sizeof(soundQueue));
    memset(player,0,sizeof(player));
    memset(&expected,0,sizeof(expected));
    event_count=probe_draw_count=0;
    power=500;
}

/* layout=-1: fully empty pool; 0: first N slots; 1: sparse odd slots;
 * 2: final N slots, including the unusual last slot. Occupied slots and the
 * extra non-pool entry must remain byte-for-byte unchanged by creation. */
static void create_case(unsigned rid, unsigned phase, int dx, int dy,
                        unsigned available, int layout, unsigned energy)
{
    const JE_WeaponType *w=weapons+rid;
    PlayerShotDataType before[MAX_PWEAPON+1];
    JE_byte before_avail[MAX_PWEAPON];
    bool written[MAX_PWEAPON]={false};
    reset();
    if (layout>=0) {
        memset(shotAvail,1,sizeof(shotAvail));
        for (unsigned i=0; i<=MAX_PWEAPON; ++i) playerShotData[i].shotGr=777;
        for (unsigned i=0; i<available; ++i) {
            unsigned slot=layout==0 ? i : layout==1 ? 2*i+1 : MAX_PWEAPON-available+i;
            shotAvail[slot]=0;
        }
    }
    expected.rid=rid;
    expected.port=ordinary_id(rid)==446 ? 0 : 11;
    expected.owner=ordinary_id(rid)==446 ? 2 : 1;
    expected.initial_phase=expected.next_phase=phase;
    expected.dx=dx; expected.dy=dy;
    unsigned cost=weaponPort[expected.port].poweruse;
    expected.available=energy<cost ? 0 : available;
    for (unsigned slot=0,n=0; slot<MAX_PWEAPON && n<expected.available; ++slot)
        if (!shotAvail[slot]) expected.slots[n++]=slot;
    expected.reason=energy<cost ? "power" : available<w->multi ? "capacity" : "complete";
    expected.result=energy<cost || available<w->multi ? MAX_PWEAPON : (int)expected.slots[w->multi-1];
    power=(JE_word)energy;
    shotMultiPos[1]=(JE_byte)phase;
    memcpy(before,playerShotData,sizeof(before));
    memcpy(before_avail,shotAvail,sizeof(before_avail));
    int got=player_shot_create((JE_word)expected.port,1,130,100,(JE_word)(130-dx),(JE_word)(100-dy),(JE_word)rid,(JE_byte)expected.owner);
    unsigned count=energy<cost ? 0 : available;
    assert(got==expected.result && expected.results==1 && expected.count==count);
    assert(power==(energy<cost ? energy : energy-cost));
    assert(shotMultiPos[1]==expected.next_phase);
    assert(shotRepeat[1]==(count ? w->shotrepeat : 0));
    assert(soundQueue[2]==(energy<cost ? 0 : w->sound));
    for (unsigned i=0; i<count; ++i) written[expected.slots[i]]=true;
    for (unsigned slot=0; slot<MAX_PWEAPON; ++slot) {
        if (!written[slot]) {
            assert(memcmp(before+slot,playerShotData+slot,sizeof(*before))==0);
            assert(before_avail[slot]==shotAvail[slot]);
        }
    }
    assert(memcmp(before+MAX_PWEAPON,playerShotData+MAX_PWEAPON,sizeof(*before))==0);
    for (unsigned i=0; i<11; ++i) if (i!=1) assert(!shotMultiPos[i] && !shotRepeat[i]);
    for (unsigned i=0; i<8; ++i) if (i!=2) assert(!soundQueue[i]);
}

/* Reuse the same pool objects and phase cursor for a second volley. The
 * renderer must not influence creation phase, source parameters or power cost. */
static void repeat_volley(unsigned rid)
{
    const JE_WeaponType *w=weapons+rid;
    unsigned phase=shotMultiPos[1];
    assert(power==450);
    memset(shotAvail,0,sizeof(shotAvail));
    memset(&expected,0,sizeof(expected));
    expected.rid=rid;
    expected.port=ordinary_id(rid)==446 ? 0 : 11;
    expected.owner=ordinary_id(rid)==446 ? 2 : 1;
    expected.initial_phase=expected.next_phase=phase;
    expected.available=w->multi;
    expected.reason="complete";
    expected.result=w->multi-1;
    for (unsigned i=0; i<w->multi; ++i) expected.slots[i]=i;
    assert(player_shot_create(11,1,130,100,130,100,(JE_word)rid,1)==expected.result);
    assert(expected.results==1 && expected.count==w->multi && power==400);
    assert(shotMultiPos[1]==phase && shotRepeat[1]==6 && soundQueue[2]==w->sound);
    ++stats->repeat_cases;
}

static void original_row_membership(void)
{
    const unsigned selected_mask=(1U<<2)|(1U<<4)|(1U<<5)|(1U<<6);
    for (unsigned copy=0; copy<2; ++copy) {
        unsigned masks[2]={0,0}, associated_masks[2]={0,0};
        for (unsigned rid=276+1000*copy; rid<=297+1000*copy; ++rid) {
            unsigned base=ordinary_id(rid);
            const JE_WeaponType *w=weapons+rid;
            /* The primary/+1000 copies preserve complete records, including
             * inactive tails. Cross-table parity is intentionally normalized
             * only for the documented blast-filter field below. */
            assert(memcmp(weapons+base,weapons+base+1000,sizeof(*w))==0);
            assert(w->multi>0 && w->multi==w->max && w->max<=8);
            assert(w->weapani==0 && w->shotrepeat==6 && !w->circlesize && !w->aim);
            assert(!w->accelerationx && w->acceleration==(base<287 ? 0 : 1));
            assert(w->trail==255 && w->shipblastfilter==(table_index==0 ? 208 : 192));
            unsigned counts[2]={0,0}, associated_counts[2]={0,0};
            for (unsigned p=0; p<w->max; ++p) {
                assert(w->sg[p]>0 && w->sg[p]<500 && (w->del[p]==98 || w->del[p]==100));
                assert(w->attack[p]<100);
                int member=oblique_member(w->sg[p]);
                if (member>=0) {
                    unsigned left_phase=(base==278 || base==280) ? 2 : 4;
                    masks[member]|=1U<<(base-276); ++counts[member];
                    assert(base==278 || base==280 || base==281 || base==282);
                    assert(p==left_phase+(member==0 ? 1 : 0));
                    assert(w->bx[p]==(member==0 ? 4 : -4) && !w->by[p]);
                    assert(w->sx[p]==(member==0 ? 2 : -2) && w->sy[p]==13 && w->del[p]==98);
                }
                member=associated_member(w->sg[p]);
                if (member>=0) {
                    associated_masks[member]|=1U<<(base-276); ++associated_counts[member];
                    assert(base==284 && p==(member==0 ? 6U : 5U));
                    assert(w->bx[p]==(member==0 ? 4 : -4) && !w->by[p]);
                    assert(w->sx[p]==(member==0 ? 2 : -2) && w->sy[p]==-13 && w->del[p]==98);
                }
            }
            unsigned wanted=(selected_mask>>(base-276))&1U;
            assert(counts[0]==wanted && counts[1]==wanted);
            assert(associated_counts[0]==(base==284) && associated_counts[1]==(base==284));
        }
        assert(masks[0]==selected_mask && masks[1]==selected_mask);
        assert(associated_masks[0]==(1U<<8) && associated_masks[1]==(1U<<8));
    }
    assert(memcmp(weapons+446,weapons+1446,sizeof(*weapons))==0);
    for (unsigned copy=0; copy<2; ++copy) {
        const JE_WeaponType *w=weapons+446+1000*copy;
        assert(w->multi==1 && w->max==1 && w->shotrepeat==2 && w->sound==13);
        assert(!w->weapani && !w->circlesize && !w->aim && !w->acceleration && !w->accelerationx);
        assert(w->sg[0]==6 && w->del[0]==255 && w->attack[0]==1 && w->trail==255);
        assert(!w->bx[0] && !w->by[0] && !w->sx[0] && w->sy[0]==12);
        assert(w->shipblastfilter==(table_index==0 ? 208 : 192));
    }
}

static bool move_case(unsigned slot, const JE_WeaponType *w, unsigned p,
                      unsigned tick, bool shadows_enabled)
{
    PlayerShotDataType *s=playerShotData+slot;
    JE_word frame=s->shotGr;
    assert(slot<MAX_PWEAPON-1 && shotAvail[slot]>0);
    int ex=s->shotX+s->shotXM+w->accelerationx;
    int ey=s->shotY+s->shotYM-w->acceleration;
    int vx=s->shotXM+w->accelerationx, vy=s->shotYM-w->acceleration;
    unsigned lifespan=shotAvail[slot];
    bool special=true;
    int ox=-999, oy=-999;
    JE_integer dmg=-999;
    JE_byte blast=0, chain=99, owner=99;
    JE_word rw=599, rh=598;
    unsigned olddraws=stats->draws, oldshadows=stats->shadows;
    background2=shadows_enabled;
    moving_shot=(int)slot;
    event_count=probe_draw_count=0;
    bool inside=ex>=-34 && ex<=290 && ey>=-15 && ey<=190;
    hash_word(0x30); hash_word(slot); hash_word(tick); hash_word(shadows_enabled);
    bool got=player_shot_move_and_draw((int)slot,&special,&ox,&oy,&dmg,&blast,&chain,&owner,&rw,&rh);
    assert(got==inside && ox==ex && oy==ey && s->shotX==ex && s->shotY==ey);
    assert(s->shotXM==vx && s->shotYM==vy);
    assert(s->shotXC==w->accelerationx && s->shotYC==-w->acceleration);
    assert(shotAvail[slot]==(inside ? lifespan-1 : 0));
    hash_word(got); hash_word(ox); hash_word(oy); hash_shot(slot);
    if (!inside) {
        assert(stats->draws==olddraws && stats->shadows==oldshadows);
        assert(!event_count && !probe_draw_count && special);
        assert(dmg==-999 && blast==0 && chain==99 && owner==99 && rw==599 && rh==598);
        ++stats->offscreen_moves;
        return false;
    }
    unsigned shadow=background2 && ey+shadowYDist<190 && vx<100;
    assert(stats->draws==olddraws+1+shadow && stats->shadows==oldshadows+shadow);
    assert(event_count==1+shadow && probe_draw_count==event_count);
    assert(events[shadow].x==ex+1 && events[shadow].y==ey);
    assert(events[shadow].id==frame && events[shadow].style==ENTITY_NORMAL && events[shadow].bank==8);
    if (shadow) {
        assert(events[0].x==ex+1 && events[0].y==ey+shadowYDist);
        assert(events[0].id==frame && events[0].style==ENTITY_SHADOW && events[0].bank==8);
    }
    assert(!special && dmg==w->attack[p] && blast==w->shipblastfilter && !chain && owner==s->playerNumber);
    assert(rw==599 && rh==598 && s->shotAni==0 && s->shotAniMax==1 && s->shotGr==frame);
    int member=oblique_member(s->shotGr);
    if (member>=0) {
        ++stats->selected_moves[member];
        if (shadow) ++stats->selected_shadow_orders[member];
    }
    member=associated_member(s->shotGr);
    if (member>=0) {
        ++stats->associated_moves[member];
        if (shadow) ++stats->associated_shadow_orders[member];
    }
    hash_word(dmg); hash_blast(blast); hash_word(chain); hash_word(owner);
    hash_word(rw); hash_word(rh);
    ++stats->moves;
    return true;
}

static void normal_rows(void)
{
    const int drift[]={-20,-6,-5,-4,-3,-1,0,1,3,4,5,6,20};
    for (unsigned copy=0; copy<2; ++copy)
    for (unsigned rid=276+1000*copy; rid<=297+1000*copy; ++rid) {
        const JE_WeaponType *w=weapons+rid;
        for (unsigned phase=0; phase<=w->max; ++phase) {
            ++stats->phase_cases;
            for (unsigned dx=0; dx<sizeof(drift)/sizeof(*drift); ++dx)
                for (unsigned dy=0; dy<sizeof(drift)/sizeof(*drift); ++dy) {
                    create_case(rid,phase,drift[dx],drift[dy],w->multi,-1,500);
                    ++stats->drift_phase_cases;
                    for (unsigned n=0; n<w->multi; ++n) {
                        unsigned p=(phase+n)%w->max;
                        for (unsigned tick=1; tick<=4; ++tick)
                            if (!move_case(n,w,p,tick,tick%2==1)) break;
                    }
                }
        }
        /* Production also resets phase values greater than eight. */
        for (unsigned invalid=9; invalid<=255; invalid+=246) {
            create_case(rid,invalid,1,1,w->multi,-1,500);
            ++stats->phase_cases;
        }
        repeat_volley(rid);
    }
}

static void capacity_and_power(void)
{
    const unsigned energies[]={0,1,49,50,51,99,100,500};
    for (unsigned copy=0; copy<2; ++copy)
    for (unsigned rid=276+1000*copy; rid<=297+1000*copy; ++rid) {
        const JE_WeaponType *w=weapons+rid;
        for (unsigned phase=0; phase<=w->max; ++phase) {
            for (unsigned available=0; available<=w->multi; ++available)
                for (int layout=0; layout<3; ++layout) {
                    create_case(rid,phase,-20,20,available,layout,500);
                    ++stats->capacity_cases;
                }
            for (unsigned e=0; e<sizeof(energies)/sizeof(*energies); ++e) {
                create_case(rid,phase,20,-20,w->multi,-1,energies[e]);
                ++stats->power_cases;
            }
        }
    }
}

static void boundary_and_lifetime(void)
{
    /* Each shot starts from an authentic create. Only the placement is changed
     * to land exactly on, immediately inside, or immediately outside the move
     * bounds and the strict shadow cutoff. Velocities/graphics are untouched. */
    const int target_x[]={-35,-34,-33,289,290,291};
    const int target_y[]={-16,-15,-14,180,181,182,189,190,191};
    for (unsigned copy=0; copy<2; ++copy)
    for (unsigned rid=276+1000*copy; rid<=297+1000*copy; ++rid) {
        const JE_WeaponType *w=weapons+rid;
        for (unsigned p=0; p<w->max; ++p) {
            for (unsigned i=0; i<sizeof(target_x)/sizeof(*target_x); ++i) {
                create_case(rid,p,0,0,w->multi,-1,500);
                PlayerShotDataType *s=playerShotData;
                s->shotX=(JE_integer)(target_x[i]-s->shotXM-s->shotXC);
                move_case(0,w,p,1,true); ++stats->boundary_cases;
            }
            for (unsigned i=0; i<sizeof(target_y)/sizeof(*target_y); ++i) {
                create_case(rid,p,0,0,w->multi,-1,500);
                PlayerShotDataType *s=playerShotData;
                s->shotY=(JE_integer)(target_y[i]-s->shotYM-s->shotYC);
                move_case(0,w,p,1,true); ++stats->boundary_cases;
            }
            /* Follow one unmodified trajectory to its original pool removal
             * condition; never invoke the function after duration becomes zero. */
            create_case(rid,p,0,0,w->multi,-1,500);
            unsigned tick=0;
            while (shotAvail[0]) {
                ++tick;
                if (!move_case(0,w,p,tick,tick%2==1)) break;
            }
            assert(tick<=w->del[p] && !shotAvail[0]);
            ++stats->boundary_cases;
        }
    }
}

/* The original expression passes a double product to roundf, which first
 * converts that product to float. Compare that representable scaled value to
 * exact half-integer thresholds, independently of roundf itself. Mathematical
 * pi/16 boundaries alone do not describe all float-adjacent behavior. */
static unsigned reference_bin(float direction)
{
    float scaled=(float)((double)direction*(16/(2*M_PI)));
    assert(scaled>=0.0f && scaled<=16.0f);
    for (unsigned bin=0; bin<16; ++bin)
        if (scaled<(float)bin+0.5f) return bin;
    return 16;
}
static int reference_round(float value)
{
    /* Promote before adding 0.5 so no second float rounding changes a tie. */
    return value<0 ? -(int)floor(-(double)value+0.5) : (int)floor((double)value+0.5);
}
static uint32_t float_bits(float value)
{
    uint32_t bits;
    memcpy(&bits,&value,sizeof(bits));
    return bits;
}
static const JE_word expected_link_sonic[17]={85,242,131,303,47,284,150,223,66,224,149,283,9,302,130,243,85};
static float transition_last_lower[16], transition_first_upper[16];

static void linked_direction_case(unsigned rid, unsigned weapon_id, float direction,
                                  unsigned bin, bool boundary)
{
    const JE_WeaponType *w=weapons+rid;
    assert(reference_bin(direction)==bin && bin<=16);
    /* This is the original source446/1446 mechanism: cost0, rear bay1,
     * player2, then original direction selection. No renderer or HD binding
     * is linked into this harness. Origins are fixed only for unit isolation. */
    create_case(rid,0,0,0,1,-1,0);
    PlayerShotDataType before[MAX_PWEAPON+1];
    JE_byte avail_before[MAX_PWEAPON], multi_before[11], repeat_before[11], sound_before[8];
    memcpy(before,playerShotData,sizeof(before));
    memcpy(avail_before,shotAvail,sizeof(avail_before));
    memcpy(multi_before,shotMultiPos,sizeof(multi_before));
    memcpy(repeat_before,shotRepeat,sizeof(repeat_before));
    memcpy(sound_before,soundQueue,sizeof(sound_before));
    PlayerShotDataType wanted=before[0];
    wanted.shotXM=(JE_integer)-reference_round(sinf(direction)*before[0].shotYM);
    wanted.shotYM=(JE_integer)-reference_round(cosf(direction)*before[0].shotYM);
    wanted.shotGr=expected_link_sonic[bin];
    player_shot_set_direction(0,weapon_id,direction);
    assert(memcmp(playerShotData,&wanted,sizeof(wanted))==0);
    assert(memcmp(playerShotData+1,before+1,sizeof(before)-sizeof(*before))==0);
    assert(memcmp(avail_before,shotAvail,sizeof(avail_before))==0);
    assert(memcmp(multi_before,shotMultiPos,sizeof(multi_before))==0);
    assert(memcmp(repeat_before,shotRepeat,sizeof(repeat_before))==0);
    assert(memcmp(sound_before,soundQueue,sizeof(sound_before))==0);
    assert(!power && shotMultiPos[1]==1 && shotRepeat[1]==2 && soundQueue[2]==13);
    ++stats->linked_cases;
    if (boundary) ++stats->linked_boundary_cases;
    else { ++stats->linked_center_cases; stats->linked_bin_mask|=1U<<bin; }
    int member=oblique_member(wanted.shotGr);
    if (member>=0) ++stats->linked_selected_cases[member];
    member=associated_member(wanted.shotGr);
    if (member>=0) ++stats->linked_associated_cases[member];
    hash_word(0x40); hash_word(rid); hash_word(weapon_id);
    hash_word(float_bits(direction)); hash_word(bin); hash_word(boundary); hash_shot(0);
    for (unsigned tick=1; tick<=4; ++tick) {
        assert(move_case(0,w,0,tick,tick%2==1));
        assert(playerShotData[0].shotGr==expected_link_sonic[bin]);
    }
}

static void linked_directions(void)
{
    const unsigned ports[]={11,28,33};
    assert(sizeof(float)==sizeof(uint32_t) && FLT_RADIX==2 && FLT_MANT_DIG==24 && FLT_MAX_EXP==128);
    assert(float_bits(1.0f)==UINT32_C(0x3f800000));
    for (unsigned bin=0; bin<17; ++bin) assert(linkSonicGr[bin]==expected_link_sonic[bin]);
    assert(linkSonicGr[7]==223 && linkSonicGr[9]==224 && linkSonicGr[1]==242 && linkSonicGr[15]==243);
    for (unsigned k=0; k<16; ++k) {
        float boundary=(float)((2*k+1)*M_PI/16.0);
        float lo=boundary, hi=boundary;
        unsigned steps=0;
        if (reference_bin(boundary)==k) {
            hi=nextafterf(lo,INFINITY);
            while (reference_bin(hi)==k) { lo=hi; hi=nextafterf(hi,INFINITY); assert(++steps<16); }
        } else {
            assert(reference_bin(boundary)==k+1);
            lo=nextafterf(hi,-INFINITY);
            while (reference_bin(lo)==k+1) { hi=lo; lo=nextafterf(lo,-INFINITY); assert(++steps<16); }
        }
        assert(reference_bin(lo)==k && reference_bin(hi)==k+1);
        assert(nextafterf(lo,INFINITY)==hi && nextafterf(hi,-INFINITY)==lo);
        transition_last_lower[k]=lo; transition_first_upper[k]=hi;
    }
    for (unsigned copy=0; copy<2; ++copy) {
        unsigned rid=446+1000*copy;
        /* Both full and empty pools preserve original zero-cost creation,
         * sound/phase behavior and the sentinel entry. Never direct a failed
         * create: the original caller's exhausted-pool path is out of scope. */
        for (unsigned available=0; available<=1; ++available)
            for (int layout=0; layout<3; ++layout) {
                create_case(rid,0,0,0,available,layout,0);
                ++stats->capacity_cases;
            }
        for (unsigned port=0; port<sizeof(ports)/sizeof(*ports); ++port) {
            for (unsigned bin=0; bin<17; ++bin) {
                float center=(float)(bin*(2*M_PI)/16.0);
                linked_direction_case(rid,ports[port],center,bin,false);
            }
            for (unsigned k=0; k<16; ++k) {
                float boundary=(float)((2*k+1)*M_PI/16.0);
                const float inputs[]={nextafterf(boundary,-INFINITY),boundary,nextafterf(boundary,INFINITY),
                    nextafterf(transition_last_lower[k],-INFINITY),transition_last_lower[k],
                    transition_first_upper[k],nextafterf(transition_first_upper[k],INFINITY)};
                for (unsigned i=0; i<sizeof(inputs)/sizeof(*inputs); ++i) {
                    unsigned bin=reference_bin(inputs[i]);
                    assert(bin==k || bin==k+1);
                    linked_direction_case(rid,ports[port],inputs[i],bin,true);
                }
            }
        }
    }
    assert(stats->linked_bin_mask==((1U<<17)-1));
    assert(stats->linked_center_cases==2*3*17 && stats->linked_boundary_cases==2*3*16*7);
    for (unsigned member=0; member<2; ++member)
        assert(stats->linked_selected_cases[member] && stats->linked_associated_cases[member]);
}

static void print_table(unsigned index)
{
    const TableStats *s=table_stats+index;
    printf("{\"name\":\"%s\",\"ordinary_first_level_rows\":22,\"ordinary_record_copies\":44,"
           "\"selected_rows\":[278,280,281,282],\"selected_secondary_rows\":[1278,1280,1281,1282],"
           "\"associated_source_unit_rows\":[284,1284],"
           "\"shipblastfilter\":%u,\"rng_calls\":%u,\"create_cases\":%u,\"emits\":%u,"
           "\"drift_phase_cases\":%u,\"volley_phase_cases\":%u,\"capacity_cases\":%u,"
           "\"power_cases\":%u,\"repeated_volley_cases\":%u,\"boundary_and_lifetime_cases\":%u,\"movement_ticks\":%u,"
           "\"offscreen_movement_ticks\":%u,\"draws\":%u,\"shadow_draws\":%u,"
           "\"oblique_pair_emissions\":[%u,%u],\"oblique_pair_movement_ticks\":[%u,%u],"
           "\"oblique_pair_shadow_before_head_cases\":[%u,%u],"
           "\"associated_source_unit_emissions\":[%u,%u],\"associated_source_unit_movement_ticks\":[%u,%u],"
           "\"associated_source_unit_shadow_before_head_cases\":[%u,%u],"
           "\"linked_direction_cases\":%u,\"linked_center_cases\":%u,\"linked_float_boundary_cases\":%u,"
           "\"linked_bin_mask\":%u,\"linked_selected_cases\":[%u,%u],\"linked_associated_cases\":[%u,%u],"
           "\"shot_state_order_fnv1a64\":\"%016" PRIx64 "\","
           "\"blast_normalized_state_order_fnv1a64\":\"%016" PRIx64 "\"}",
           table_names[index],index==0 ? 208U : 192U,s->rng_calls,s->requests,s->emits,
           s->drift_phase_cases,s->phase_cases,s->capacity_cases,s->power_cases,s->repeat_cases,s->boundary_cases,
           s->moves,s->offscreen_moves,s->draws,s->shadows,
           s->selected_emits[0],s->selected_emits[1],s->selected_moves[0],s->selected_moves[1],
           s->selected_shadow_orders[0],s->selected_shadow_orders[1],
           s->associated_emits[0],s->associated_emits[1],s->associated_moves[0],s->associated_moves[1],
           s->associated_shadow_orders[0],s->associated_shadow_orders[1],
           s->linked_cases,s->linked_center_cases,s->linked_boundary_cases,s->linked_bin_mask,
           s->linked_selected_cases[0],s->linked_selected_cases[1],s->linked_associated_cases[0],s->linked_associated_cases[1],
           s->full_hash,s->normalized_hash);
}
int main(void)
{
    unsigned creates=0, moves=0, emits=0, draws=0, shadows=0, capacity=0, phases=0;
    weaponPort[11].poweruse=50;
    assert(!weaponPort[0].poweruse);
    for (table_index=0; table_index<3; ++table_index) {
        stats=table_stats+table_index;
        stats->full_hash=stats->normalized_hash=UINT64_C(14695981039346656037);
        weapons=weapon_tables[table_index];
        original_row_membership(); normal_rows(); capacity_and_power(); boundary_and_lifetime(); linked_directions();
        assert(!stats->rng_calls && stats->offscreen_moves);
        for (unsigned i=0; i<2; ++i) {
            assert(stats->selected_emits[i] && stats->selected_moves[i] && stats->selected_shadow_orders[i]);
            assert(stats->associated_emits[i] && stats->associated_moves[i] && stats->associated_shadow_orders[i]);
        }
        creates+=stats->requests; moves+=stats->moves; emits+=stats->emits;
        draws+=stats->draws; shadows+=stats->shadows;
        capacity+=stats->capacity_cases+stats->power_cases; phases+=stats->phase_cases;
    }
    assert(table_stats[0].normalized_hash==table_stats[1].normalized_hash);
    assert(table_stats[1].normalized_hash==table_stats[2].normalized_hash);
    assert(table_stats[0].full_hash!=table_stats[1].full_hash);
    assert(table_stats[1].full_hash==table_stats[2].full_hash);
    printf("{\"status\":\"PASS\",\"ordinary_first_level_rows\":22,\"ordinary_record_copies_per_table\":44,\"source_item_tables\":3,"
           "\"oblique_pair_ids\":[223,224],\"associated_source_unit_only_ids\":[242,243],"
           "\"linked_source_unit_only_records\":[446,1446],\"linked_direction_weapon_ids\":[11,28,33],"
           "\"all17_linked_direction_bins_verified\":true,\"linked_hd_acceptance_claimed\":false,"
           "\"rng_calls\":0,\"create_cases\":%u,\"movement_ticks\":%u,"
           "\"capacity_and_power_cases\":%u,\"volley_phase_cases\":%u,\"emits\":%u,"
           "\"draws\":%u,\"shadow_draws\":%u,\"original_shadow_then_head_order_verified\":true,"
           "\"all_three_blast_normalized_state_order_hashes_equal\":true,"
           "\"hdt_vs_episode_blast_difference_preserved\":true,\"game_runs\":0,\"tables\":[",
           creates,moves,capacity,phases,emits,draws,shadows);
    for (unsigned i=0; i<3; ++i) { if (i) putchar(','); print_table(i); }
    printf("],\"representable_direction_transitions\":[");
    for (unsigned k=0; k<16; ++k) {
        if (k) putchar(',');
        printf("{\"last_lower_bin\":%u,\"first_upper_bin\":%u,\"last_lower_float32_hex\":\"%08" PRIx32 "\","
               "\"first_upper_float32_hex\":\"%08" PRIx32 "\",\"nextafterf_adjacent\":true}",
               k,k+1,float_bits(transition_last_lower[k]),float_bits(transition_first_upper[k]));
    }
    puts("]}");
    return 0;
}
