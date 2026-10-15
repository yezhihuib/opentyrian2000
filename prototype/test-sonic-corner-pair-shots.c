/* Extracted, unchanged production player_shot_create/move coverage. This harness
 * never launches the game. Original records are supplied by private, generated
 * includes, not duplicated here. All 22 ordinary Sonic rows are exercised for
 * each of the three source item tables; only mode 1 P10/P11 use IDs 130/131.
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
static int corner_member(unsigned id)
{
    return id==130 ? 0 : id==131 ? 1 : -1;
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
    unsigned rid, initial_phase, next_phase, available, count, results;
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
    assert(w->del[p]==98 || w->del[p]==100);
    assert(s->shotX==130+w->bx[p] && s->shotY==100+w->by[p]);
    assert(s->shotXM==vx && s->shotYM==vy);
    assert(s->shotXC==w->accelerationx && s->shotYC==-w->acceleration);
    assert(s->shotGr==w->sg[p] && s->shotAni==0 && s->shotAniMax==1);
    assert(shotAvail[slot]==w->del[p] && s->shotDmg==w->attack[p]);
    assert(s->shotBlastFilter==w->shipblastfilter && s->playerNumber==1);
    assert(s->shotTrail==255 && !s->shotComplicated && !s->chainReaction);
    assert(!s->shotDevX && !s->shotDirX && !s->shotDevY && !s->shotDirY);
    assert(!s->shotCirSizeX && !s->shotCirSizeY && !s->aimAtEnemy);
    assert(!s->aimDelay && !s->aimDelayMax);
}
static unsigned game_probe_shot_begin(JE_word port, uint bay, JE_word wp,
                                     JE_byte p, JE_word px, JE_word py)
{
    assert(port==11 && bay==1 && wp==expected.rid && wp>=276 && wp<=297);
    assert(p==1 && px==130 && py==100);
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
    int member=corner_member(playerShotData[id].shotGr);
    if (member>=0) ++stats->selected_emits[member];
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
    expected.initial_phase=expected.next_phase=phase;
    expected.dx=dx; expected.dy=dy;
    expected.available=energy<50 ? 0 : available;
    for (unsigned slot=0,n=0; slot<MAX_PWEAPON && n<expected.available; ++slot)
        if (!shotAvail[slot]) expected.slots[n++]=slot;
    expected.reason=energy<50 ? "power" : available<w->multi ? "capacity" : "complete";
    expected.result=energy<50 || available<w->multi ? MAX_PWEAPON : (int)expected.slots[w->multi-1];
    power=(JE_word)energy;
    shotMultiPos[1]=(JE_byte)phase;
    memcpy(before,playerShotData,sizeof(before));
    memcpy(before_avail,shotAvail,sizeof(before_avail));
    int got=player_shot_create(11,1,130,100,(JE_word)(130-dx),(JE_word)(100-dy),(JE_word)rid,1);
    unsigned count=energy<50 ? 0 : available;
    assert(got==expected.result && expected.results==1 && expected.count==count);
    assert(power==(energy<50 ? energy : energy-50));
    assert(shotMultiPos[1]==expected.next_phase);
    assert(shotRepeat[1]==(count ? w->shotrepeat : 0));
    assert(soundQueue[2]==(energy<50 ? 0 : w->sound));
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
    unsigned masks[2]={0,0};
    for (unsigned rid=276; rid<=297; ++rid) {
        const JE_WeaponType *w=weapons+rid;
        assert(w->multi>0 && w->multi==w->max && w->max<=8);
        assert(w->weapani==0 && w->shotrepeat==6 && !w->circlesize && !w->aim);
        assert(!w->accelerationx && w->acceleration==(rid<287 ? 0 : 1));
        assert(w->trail==255 && w->shipblastfilter==(table_index==0 ? 208 : 192));
        unsigned counts[2]={0,0};
        for (unsigned p=0; p<w->max; ++p) {
            assert(w->sg[p]>0 && w->sg[p]<500 && (w->del[p]==98 || w->del[p]==100));
            assert(w->attack[p]<100);
            int member=corner_member(w->sg[p]);
            if (member>=0) { masks[member]|=1U<<(rid-276); ++counts[member]; }
        }
        unsigned wanted=rid==285 || rid==286 ? 1 : 0;
        assert(counts[0]==wanted && counts[1]==wanted);
    }
    /* Both IDs occur only in mode 1 P10/P11, among ordinary rows 276..297. */
    assert(masks[0]==((1U<<9)|(1U<<10)) && masks[1]==masks[0]);
}

static bool move_case(unsigned slot, const JE_WeaponType *w, unsigned p,
                      unsigned tick, bool shadows_enabled)
{
    PlayerShotDataType *s=playerShotData+slot;
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
    assert(events[shadow].id==w->sg[p] && events[shadow].style==ENTITY_NORMAL && events[shadow].bank==8);
    if (shadow) {
        assert(events[0].x==ex+1 && events[0].y==ey+shadowYDist);
        assert(events[0].id==w->sg[p] && events[0].style==ENTITY_SHADOW && events[0].bank==8);
    }
    assert(!special && dmg==w->attack[p] && blast==w->shipblastfilter && !chain && owner==1);
    assert(rw==599 && rh==598 && s->shotAni==0 && s->shotAniMax==1 && s->shotGr==w->sg[p]);
    int member=corner_member(s->shotGr);
    if (member>=0) {
        ++stats->selected_moves[member];
        if (shadow) ++stats->selected_shadow_orders[member];
    }
    hash_word(dmg); hash_blast(blast); hash_word(chain); hash_word(owner);
    hash_word(rw); hash_word(rh);
    ++stats->moves;
    return true;
}

static void normal_rows(void)
{
    const int drift[]={-20,-6,-5,-4,-3,-1,0,1,3,4,5,6,20};
    for (unsigned rid=276; rid<=297; ++rid) {
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
    for (unsigned rid=276; rid<=297; ++rid) {
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
    for (unsigned rid=276; rid<=297; ++rid) {
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

static void print_table(unsigned index)
{
    const TableStats *s=table_stats+index;
    printf("{\"name\":\"%s\",\"ordinary_first_level_rows\":22,\"selected_rows\":[285,286],"
           "\"shipblastfilter\":%u,\"rng_calls\":%u,\"create_cases\":%u,\"emits\":%u,"
           "\"drift_phase_cases\":%u,\"volley_phase_cases\":%u,\"capacity_cases\":%u,"
           "\"power_cases\":%u,\"repeated_volley_cases\":%u,\"boundary_and_lifetime_cases\":%u,\"movement_ticks\":%u,"
           "\"offscreen_movement_ticks\":%u,\"draws\":%u,\"shadow_draws\":%u,"
           "\"corner_pair_emissions\":[%u,%u],\"corner_pair_movement_ticks\":[%u,%u],"
           "\"corner_pair_shadow_before_head_cases\":[%u,%u],"
           "\"shot_state_order_fnv1a64\":\"%016" PRIx64 "\","
           "\"blast_normalized_state_order_fnv1a64\":\"%016" PRIx64 "\"}",
           table_names[index],index==0 ? 208U : 192U,s->rng_calls,s->requests,s->emits,
           s->drift_phase_cases,s->phase_cases,s->capacity_cases,s->power_cases,s->repeat_cases,s->boundary_cases,
           s->moves,s->offscreen_moves,s->draws,s->shadows,
           s->selected_emits[0],s->selected_emits[1],s->selected_moves[0],s->selected_moves[1],
           s->selected_shadow_orders[0],s->selected_shadow_orders[1],s->full_hash,s->normalized_hash);
}
int main(void)
{
    unsigned creates=0, moves=0, emits=0, draws=0, shadows=0, capacity=0, phases=0;
    weaponPort[11].poweruse=50;
    for (table_index=0; table_index<3; ++table_index) {
        stats=table_stats+table_index;
        stats->full_hash=stats->normalized_hash=UINT64_C(14695981039346656037);
        weapons=weapon_tables[table_index];
        original_row_membership(); normal_rows(); capacity_and_power(); boundary_and_lifetime();
        assert(!stats->rng_calls && stats->offscreen_moves);
        for (unsigned i=0; i<2; ++i)
            assert(stats->selected_emits[i] && stats->selected_moves[i] && stats->selected_shadow_orders[i]);
        creates+=stats->requests; moves+=stats->moves; emits+=stats->emits;
        draws+=stats->draws; shadows+=stats->shadows;
        capacity+=stats->capacity_cases+stats->power_cases; phases+=stats->phase_cases;
    }
    assert(table_stats[0].normalized_hash==table_stats[1].normalized_hash);
    assert(table_stats[1].normalized_hash==table_stats[2].normalized_hash);
    assert(table_stats[0].full_hash!=table_stats[1].full_hash);
    assert(table_stats[1].full_hash==table_stats[2].full_hash);
    printf("{\"status\":\"PASS\",\"ordinary_first_level_rows\":22,\"source_item_tables\":3,"
           "\"corner_pair_ids\":[130,131],\"rng_calls\":0,\"create_cases\":%u,\"movement_ticks\":%u,"
           "\"capacity_and_power_cases\":%u,\"volley_phase_cases\":%u,\"emits\":%u,"
           "\"draws\":%u,\"shadow_draws\":%u,\"original_shadow_then_head_order_verified\":true,"
           "\"all_three_blast_normalized_state_order_hashes_equal\":true,"
           "\"hdt_vs_episode_blast_difference_preserved\":true,\"game_runs\":0,\"tables\":[",
           creates,moves,capacity,phases,emits,draws,shadows);
    for (unsigned i=0; i<3; ++i) { if (i) putchar(','); print_table(i); }
    puts("]}");
    return 0;
}
