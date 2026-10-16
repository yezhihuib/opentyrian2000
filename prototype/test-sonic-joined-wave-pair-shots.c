/* Isolated source-only harness for unchanged production player_shot_create/move.
 * This file does not launch the game or provide a directional 143/144 witness.
 * Private generated inputs must define the exact original types/functions and:
 *   static const JE_WeaponType weapon_tables[3][WEAP_NUM+1];
 *   static const JE_word source_port_poweruse[3][PORT_NUM+1];
 * Populate all fields (including inactive tails) of 276..297, 756..766,
 * 465/467/468 and their byte-equal +1000 records, in HDT/episode4/episode5 order.
 * Source-byte provenance and full-record equality are also checked by the
 * generating driver. Only valid original phase cursors 0..max and reset values
 * 9/255 are executed. Values max+1..8 are not valid cursors for a shorter row;
 * they read inactive tails, and 8 can produce an out-of-bounds array index.
 *
 * Pair assertions follow original source-phase partners within one creation
 * cohort. They do not batch, reorder, repair, or join unrelated shot objects.
 * Canvas overlaps below are logical 24x14 AABB facts, not alpha/pixel claims.
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
enum { SHOT_FRONT=0, SHOT_REAR=1, SHOT_P2_CHARGE=5 };
#define OPTION_SHAPES 0
static struct { unsigned width, height; } unused_sprite;
static const void *unused_sprite_ptr(void)
{
    assert(!"unexpected special sprite");
    return &unused_sprite;
}
#define sprite(...) ((void)unused_sprite_ptr(), &unused_sprite)

typedef struct { unsigned rid, port, bay, owner; } SourceRow;
enum { REAR_ROWS=22, FRONT_ROWS=11, CHARGE_ROWS=3, SOURCE_ROWS=36 };
static SourceRow source_row(unsigned n, unsigned copy)
{
    assert(n<SOURCE_ROWS && copy<2);
    SourceRow r;
    if (n<REAR_ROWS) r=(SourceRow){276+n,11,SHOT_REAR,1};
    else if (n<REAR_ROWS+FRONT_ROWS) r=(SourceRow){756+n-REAR_ROWS,41,SHOT_FRONT,1};
    else r=(SourceRow){(unsigned[]){465,467,468}[n-REAR_ROWS-FRONT_ROWS],16,SHOT_P2_CHARGE,2};
    r.rid+=copy*1000;
    /* Both player ownership values are tested without changing the source row
     * or suggesting that a +1000 copy is a different natural acquisition. */
    if (copy && r.port!=16) r.owner=2;
    return r;
}
static unsigned primary_id(unsigned rid) { return rid>=1000 ? rid-1000 : rid; }
static int joined_wave_member(unsigned id) { return id==143 ? 0 : id==144 ? 1 : -1; }
static unsigned next_phase(unsigned previous, unsigned max)
{
    return previous==max || previous>8 ? 1 : previous+1;
}
static int clamp(int n, int lo, int hi) { return n<lo ? lo : n>hi ? hi : n; }

typedef struct {
    unsigned requests, emits, draws, shadows, moves, offscreen_moves, rng_calls;
    unsigned drift_phase_cases, phase_cases, capacity_cases, power_cases;
    unsigned repeat_cases, boundary_cases, lifetime_cases, slot80_ticks;
    unsigned seam_cases, seam_ticks, complete_pairs, selected_orphans[2];
    unsigned independent_removal_cases, canvas_overlap_cases, bank12_draws;
    unsigned selected_emits[2], selected_moves[2], selected_shadow_orders[2];
    unsigned valid_phase_mask, invalid_phase9_cases, invalid_phase255_cases;
    unsigned row_seams[SOURCE_ROWS], row_orphans[SOURCE_ROWS];
    unsigned maximum_lifetime_ticks;
    int movement_min_x, movement_max_x, movement_min_y, movement_max_y;
    uint64_t full_hash, normalized_hash;
} TableStats;
static TableStats table_stats[3], *stats;
static unsigned table_index, row_index;
static const char *const table_names[3]={"tyrian.hdt", "tyrian4.lvl", "tyrian5.lvl"};

/* Canonical little-endian words avoid struct padding and native endianness.
 * Only blast values are normalized. Front41 and charge468 remain208 in all
 * three tables; rear11 and charge465/467 use208 in HDT versus192 in ep4/5. */
static void hash_word_into(uint64_t *hash, uint32_t value)
{
    for (unsigned i=0; i<4; ++i) {
        *hash^=value&255U; *hash*=UINT64_C(1099511628211); value>>=8;
    }
}
static void hash_word(int64_t value)
{
    hash_word_into(&stats->full_hash,(uint32_t)value);
    hash_word_into(&stats->normalized_hash,(uint32_t)value);
}
static void hash_blast(unsigned value)
{
    hash_word_into(&stats->full_hash,value);
    hash_word_into(&stats->normalized_hash,0);
}
static void hash_shot(unsigned id)
{
    const PlayerShotDataType *s=playerShotData+id;
    hash_word(id); hash_word(shotAvail[id]);
    hash_word(s->shotX); hash_word(s->shotY); hash_word(s->shotXM); hash_word(s->shotYM);
    hash_word(s->shotXC); hash_word(s->shotYC); hash_word(s->shotComplicated);
    hash_word(s->shotDevX); hash_word(s->shotDirX); hash_word(s->shotDevY); hash_word(s->shotDirY);
    hash_word(s->shotCirSizeX); hash_word(s->shotCirSizeY); hash_word(s->shotTrail);
    hash_word(s->shotGr); hash_word(s->shotAni); hash_word(s->shotAniMax); hash_word(s->shotDmg);
    hash_blast(s->shotBlastFilter); hash_word(s->chainReaction); hash_word(s->playerNumber);
    hash_word(s->aimAtEnemy); hash_word(s->aimDelay); hash_word(s->aimDelayMax);
}

typedef struct {
    SourceRow row;
    unsigned initial_phase, next_phase, available, count, results;
    unsigned slots[8], phases[8];
    JE_byte former_aim_delay[8], former_aim_delay_max[8];
    int dx, dy, result;
    const char *reason;
} CreateExpectation;
static CreateExpectation expected;
static struct { int x, y, style, bank; unsigned id; } events[2];
static unsigned event_count, probe_draw_count;
static int moving_shot;
static const JE_byte original_sound_channel[11]={0,2,4,4,2,2,5,5,1,4,1};

static void assert_created(unsigned slot, unsigned phase, unsigned ordinal)
{
    const JE_WeaponType *w=weapons+expected.row.rid;
    const PlayerShotDataType *s=playerShotData+slot;
    unsigned p=phase-1;
    int vx=w->sx[p]+(w->del[p]==98 ? clamp(expected.dx,-5,5) : 0);
    int vy=w->del[p]==100 ? clamp(expected.dy-w->sy[p],-4,4) : -w->sy[p];
    assert(w->del[p]==98 || w->del[p]==100);
    assert(w->sx[p]<100 && w->sy[p]<100 && w->sg[p]>0 && w->sg[p]<1000);
    assert(s->shotX==130+w->bx[p] && s->shotY==100+w->by[p]);
    assert(s->shotXM==vx && s->shotYM==vy);
    assert(s->shotXC==w->accelerationx && s->shotYC==-w->acceleration);
    assert(s->shotGr==w->sg[p] && s->shotAni==0 && s->shotAniMax==1);
    assert(shotAvail[slot]==w->del[p] && s->shotDmg==w->attack[p]);
    assert(s->shotBlastFilter==w->shipblastfilter && s->playerNumber==expected.row.owner);
    assert(s->shotTrail==255 && !s->shotComplicated && !s->chainReaction);
    assert(!s->shotDevX && !s->shotDirX && !s->shotDevY && !s->shotDirY);
    assert(!s->shotCirSizeX && !s->shotCirSizeY && !s->aimAtEnemy);
    /* Production does not clear these two dormant guided-shot fields. */
    assert(s->aimDelay==expected.former_aim_delay[ordinal]);
    assert(s->aimDelayMax==expected.former_aim_delay_max[ordinal]);
}
static unsigned game_probe_shot_begin(JE_word port, uint bay, JE_word wp,
                                     JE_byte owner, JE_word px, JE_word py)
{
    assert(port==expected.row.port && bay==expected.row.bay && wp==expected.row.rid);
    assert(owner==expected.row.owner && px==130 && py==100);
    ++stats->requests;
    hash_word(0x10); hash_word(stats->requests); hash_word(port); hash_word(bay);
    hash_word(wp); hash_word(owner); hash_word(expected.initial_phase);
    hash_word(expected.dx); hash_word(expected.dy); hash_word(power); hash_word(expected.available);
    return stats->requests;
}
static void game_probe_shot_emit(unsigned call, int multi, int phase, int id)
{
    assert(call==stats->requests && expected.count<expected.available && expected.count<8);
    unsigned ordinal=expected.count;
    assert(multi==(int)ordinal+1 && id==(int)expected.slots[ordinal]);
    expected.next_phase=next_phase(expected.next_phase,weapons[expected.row.rid].max);
    assert(phase==(int)expected.next_phase && shotMultiPos[expected.row.bay]==phase);
    expected.phases[ordinal]=(unsigned)phase-1;
    assert_created((unsigned)id,(unsigned)phase,ordinal);
    ++expected.count; ++stats->emits;
    int member=joined_wave_member(playerShotData[id].shotGr);
    if (member>=0) ++stats->selected_emits[member];
    hash_word(0x11); hash_word(multi); hash_word(phase); hash_shot((unsigned)id);
}
static void game_probe_shot_result(unsigned call, const char *reason, int count, int id)
{
    assert(call==stats->requests && !expected.results);
    assert(strcmp(reason,expected.reason)==0 && count==(int)expected.count && id==expected.result);
    ++expected.results;
    hash_word(0x12); hash_word(strcmp(reason,"power")==0 ? 0 : strcmp(reason,"capacity")==0 ? 1 : 2);
    hash_word(count); hash_word(id); hash_word(power);
    hash_word(shotMultiPos[expected.row.bay]); hash_word(shotRepeat[expected.row.bay]);
    for (unsigned i=0; i<8; ++i) hash_word(soundQueue[i]);
}
static void game_probe_shot_draw(int shot, JE_word raw, int bank, int frame,
                                int px, int py, int style, int width, int height)
{
    assert(shot==moving_shot && raw==playerShotData[shot].shotGr);
    assert(bank==(raw>500 ? 12 : 8) && frame==(raw>500 ? raw-500 : raw));
    assert(frame>0 && width==12 && height==14);
    assert(style==ENTITY_NORMAL || style==ENTITY_SHADOW);
    assert(probe_draw_count==event_count && probe_draw_count<2);
    ++probe_draw_count;
    hash_word(0x20); hash_word(shot); hash_word(raw); hash_word(bank); hash_word(frame);
    hash_word(px); hash_word(py); hash_word(style); hash_word(width); hash_word(height);
}
static void draw_entity_sprite2(SDL_Surface *surface, int px, int py,
                                Sprite2_array bank, unsigned id, int style, int layout)
{
    assert(surface==VGAScreen && (bank.tag==8 || bank.tag==12) && layout==ENTITY_TILE);
    assert(event_count<2 && probe_draw_count==event_count+1);
    events[event_count].x=px; events[event_count].y=py; events[event_count].id=id;
    events[event_count].style=style; events[event_count++].bank=bank.tag;
    ++stats->draws;
    if (bank.tag==12) ++stats->bank12_draws;
    if (style==ENTITY_SHADOW) ++stats->shadows; else assert(style==ENTITY_NORMAL);
    hash_word(0x21); hash_word(moving_shot); hash_word(px); hash_word(py);
    hash_word(bank.tag); hash_word(id); hash_word(style); hash_word(layout);
}
#define JE_setupExplosion(...) assert(!"unexpected trail")
#define JE_doSP(...) assert(!"unexpected special source")
#define blit_sprite_blend(...) assert(!"unexpected special blend")
/* Any future gameplay RNG dependency in the extracted functions must fail. */
#define rand(...) (++stats->rng_calls, assert(!"unexpected gameplay RNG"), 0)
#define random(...) (++stats->rng_calls, assert(!"unexpected gameplay RNG"), 0)
#define mt_rand(...) (++stats->rng_calls, assert(!"unexpected gameplay RNG"), 0U)
#define mt_rand_1(...) (++stats->rng_calls, assert(!"unexpected gameplay RNG"), 0.0)
#define srand(...) (++stats->rng_calls, assert(!"unexpected gameplay RNG seed"))
#include "shot-functions.inc"

static void reset(void)
{
    memset(playerShotData,0,sizeof(playerShotData));
    memset(shotAvail,0,sizeof(shotAvail)); memset(shotMultiPos,0,sizeof(shotMultiPos));
    memset(shotRepeat,0,sizeof(shotRepeat)); memset(player,0,sizeof(player));
    memset(&expected,0,sizeof(expected));
    for (unsigned i=0; i<=MAX_PWEAPON; ++i) {
        playerShotData[i].shotGr=777;
        playerShotData[i].aimDelay=(JE_byte)(17+i%20);
        playerShotData[i].aimDelayMax=(JE_byte)(29+i%20);
    }
    for (unsigned i=0; i<8; ++i) soundQueue[i]=(JE_byte)(40+i);
    for (unsigned i=0; i<=PORT_NUM; ++i) weaponPort[i].poweruse=source_port_poweruse[table_index][i];
    event_count=probe_draw_count=0; background2=false; shadowYDist=9; power=500;
}

/* Execute one request against the existing pool/cursors. Capture exact lowest
 * free slots, preserve occupied slots and the non-pool entry81 byte-for-byte,
 * and preserve all other bays/sound channels on every failure/success path. */
static void request_case(SourceRow row, int dx, int dy)
{
    const JE_WeaponType *w=weapons+row.rid;
    PlayerShotDataType before[MAX_PWEAPON+1];
    JE_byte before_avail[MAX_PWEAPON], before_phases[11], before_repeat[11], before_sounds[8];
    bool written[MAX_PWEAPON]={false};
    unsigned energy=power, cost=weaponPort[row.port].poweruse, free_count=0;
    memset(&expected,0,sizeof(expected)); expected.row=row;
    expected.initial_phase=expected.next_phase=shotMultiPos[row.bay];
    assert(expected.initial_phase<=w->max || expected.initial_phase>8);
    expected.dx=dx; expected.dy=dy;
    for (unsigned i=0; i<MAX_PWEAPON; ++i) if (!shotAvail[i]) {
        if (free_count<w->multi && energy>=cost) {
            expected.slots[free_count]=i;
            expected.former_aim_delay[free_count]=playerShotData[i].aimDelay;
            expected.former_aim_delay_max[free_count]=playerShotData[i].aimDelayMax;
        }
        ++free_count;
    }
    expected.available=energy<cost ? 0 : free_count<w->multi ? free_count : w->multi;
    expected.reason=energy<cost ? "power" : free_count<w->multi ? "capacity" : "complete";
    expected.result=energy<cost || free_count<w->multi ? MAX_PWEAPON : (int)expected.slots[w->multi-1];
    memcpy(before,playerShotData,sizeof(before)); memcpy(before_avail,shotAvail,sizeof(before_avail));
    memcpy(before_phases,shotMultiPos,sizeof(before_phases)); memcpy(before_repeat,shotRepeat,sizeof(before_repeat));
    memcpy(before_sounds,soundQueue,sizeof(before_sounds));
    int got=player_shot_create((JE_word)row.port,row.bay,130,100,(JE_word)(130-dx),(JE_word)(100-dy),
                              (JE_word)row.rid,(JE_byte)row.owner);
    assert(got==expected.result && expected.results==1 && expected.count==expected.available);
    assert(power==(energy<cost ? energy : energy-cost));
    assert(shotMultiPos[row.bay]==expected.next_phase);
    assert(shotRepeat[row.bay]==(expected.count ? w->shotrepeat : before_repeat[row.bay]));
    for (unsigned i=0; i<8; ++i) {
        unsigned wanted=energy>=cost && w->sound && i==original_sound_channel[row.bay] ? w->sound : before_sounds[i];
        assert(soundQueue[i]==wanted);
    }
    for (unsigned i=0; i<11; ++i) if (i!=row.bay) {
        assert(shotMultiPos[i]==before_phases[i] && shotRepeat[i]==before_repeat[i]);
    }
    for (unsigned i=0; i<expected.count; ++i) written[expected.slots[i]]=true;
    for (unsigned slot=0; slot<MAX_PWEAPON; ++slot) if (!written[slot]) {
        assert(memcmp(before+slot,playerShotData+slot,sizeof(*before))==0);
        assert(before_avail[slot]==shotAvail[slot]);
    }
    assert(memcmp(before+MAX_PWEAPON,playerShotData+MAX_PWEAPON,sizeof(*before))==0);
}

/* layout=-1: empty pool; 0: first N slots; 1: sparse odd slots; 2: final
 * N slots, deliberately including production's exceptional slot80. */
static void create_case(SourceRow row, unsigned phase, int dx, int dy,
                        unsigned available, int layout, unsigned energy)
{
    reset();
    if (layout>=0) {
        memset(shotAvail,7,sizeof(shotAvail));
        for (unsigned i=0; i<available; ++i) {
            unsigned slot=layout==0 ? i : layout==1 ? 2*i+1 : MAX_PWEAPON-available+i;
            assert(slot<MAX_PWEAPON); shotAvail[slot]=0;
        }
    }
    power=(JE_word)energy; shotMultiPos[row.bay]=(JE_byte)phase; shotRepeat[row.bay]=17;
    request_case(row,dx,dy);
}

static void assert_source_pair(const JE_WeaponType *w, unsigned left)
{
    assert(left+1<w->max && w->sg[left]==143 && w->sg[left+1]==144);
    assert(w->bx[left+1]-w->bx[left]==12 && w->by[left+1]==w->by[left]);
    assert(w->sx[left+1]==w->sx[left] && w->sy[left+1]==w->sy[left]);
    assert(w->del[left+1]==w->del[left] && w->attack[left+1]==w->attack[left]);
}
static void assert_seam(unsigned left, unsigned right)
{
    const PlayerShotDataType *a=playerShotData+left, *b=playerShotData+right;
    assert(a->shotGr==143 && b->shotGr==144);
    assert(b->shotX-a->shotX==12 && b->shotY==a->shotY);
    assert(a->shotXM==b->shotXM && a->shotYM==b->shotYM);
    assert(a->shotXC==b->shotXC && a->shotYC==b->shotYC);
    assert(a->shotAni==b->shotAni && a->shotAniMax==b->shotAniMax);
    assert(a->shotTrail==b->shotTrail && a->shotDmg==b->shotDmg);
    assert(a->shotBlastFilter==b->shotBlastFilter && a->playerNumber==b->playerNumber);
    ++stats->seam_ticks; ++stats->row_seams[row_index];
    hash_word(0x40); hash_word(left); hash_word(right);
    hash_word(a->shotX); hash_word(a->shotY); hash_word(b->shotX); hash_word(b->shotY);
}
static int emitted_partner(unsigned ordinal)
{
    const JE_WeaponType *w=weapons+expected.row.rid;
    unsigned p=expected.phases[ordinal]; int member=joined_wave_member(w->sg[p]);
    assert(member>=0);
    unsigned partner=member==0 ? p+1 : p-1;
    for (unsigned i=0; i<expected.count; ++i) if (expected.phases[i]==partner) return (int)i;
    return -1;
}
static void created_pairs_and_orphans(void)
{
    const JE_WeaponType *w=weapons+expected.row.rid;
    for (unsigned i=0; i<expected.count; ++i) {
        unsigned p=expected.phases[i]; int member=joined_wave_member(w->sg[p]);
        if (member<0) continue;
        int partner=emitted_partner(i);
        if (partner<0) {
            ++stats->selected_orphans[member]; ++stats->row_orphans[row_index];
            hash_word(0x41); hash_word(expected.slots[i]); hash_word(p);
        } else if (member==0) {
            assert_source_pair(w,p); assert_seam(expected.slots[i],expected.slots[partner]);
            ++stats->complete_pairs;
        }
    }
    ++stats->seam_cases;
}

static bool move_case(unsigned slot, const JE_WeaponType *w, unsigned p,
                      unsigned tick, bool shadows_enabled)
{
    PlayerShotDataType *s=playerShotData+slot;
    assert(slot<MAX_PWEAPON-1 && shotAvail[slot]>0);
    int ex=s->shotX+s->shotXM+w->accelerationx, ey=s->shotY+s->shotYM-w->acceleration;
    int vx=s->shotXM+w->accelerationx, vy=s->shotYM-w->acceleration;
    unsigned lifespan=shotAvail[slot], owner=s->playerNumber;
    bool special=true; int ox=-999, oy=-999; JE_integer damage=-999;
    JE_byte blast=0, chain=99, out_owner=99; JE_word rw=599, rh=598;
    unsigned olddraws=stats->draws, oldshadows=stats->shadows;
    background2=shadows_enabled; moving_shot=(int)slot; event_count=probe_draw_count=0;
    bool inside=ex>=-34 && ex<=290 && ey>=-15 && ey<=190;
    hash_word(0x30); hash_word(slot); hash_word(tick); hash_word(shadows_enabled);
    bool got=player_shot_move_and_draw((int)slot,&special,&ox,&oy,&damage,&blast,&chain,&out_owner,&rw,&rh);
    assert(got==inside && ox==ex && oy==ey && s->shotX==ex && s->shotY==ey);
    assert(s->shotXM==vx && s->shotYM==vy && s->shotXC==w->accelerationx && s->shotYC==-w->acceleration);
    assert(shotAvail[slot]==(inside ? lifespan-1 : 0));
    if (ex<stats->movement_min_x) stats->movement_min_x=ex;
    if (ex>stats->movement_max_x) stats->movement_max_x=ex;
    if (ey<stats->movement_min_y) stats->movement_min_y=ey;
    if (ey>stats->movement_max_y) stats->movement_max_y=ey;
    hash_word(got); hash_word(ox); hash_word(oy); hash_shot(slot);
    if (!inside) {
        assert(stats->draws==olddraws && stats->shadows==oldshadows && !event_count && !probe_draw_count);
        assert(special && damage==-999 && !blast && chain==99 && out_owner==99 && rw==599 && rh==598);
        ++stats->offscreen_moves; return false;
    }
    unsigned shadow=background2 && ey+shadowYDist<190 && vx<100;
    unsigned raw=w->sg[p], frame=raw>500 ? raw-500 : raw, bank=raw>500 ? 12 : 8;
    assert(stats->draws==olddraws+1+shadow && stats->shadows==oldshadows+shadow);
    assert(event_count==1+shadow && probe_draw_count==event_count);
    assert(events[shadow].x==ex+1 && events[shadow].y==ey && events[shadow].id==frame);
    assert(events[shadow].style==ENTITY_NORMAL && events[shadow].bank==(int)bank);
    if (shadow) {
        assert(events[0].x==ex+1 && events[0].y==ey+shadowYDist && events[0].id==frame);
        assert(events[0].style==ENTITY_SHADOW && events[0].bank==(int)bank);
    }
    assert(!special && damage==w->attack[p] && blast==w->shipblastfilter && !chain && out_owner==owner);
    assert(rw==599 && rh==598 && s->shotAni==0 && s->shotAniMax==1 && s->shotGr==raw);
    int member=joined_wave_member(raw);
    if (member>=0) { ++stats->selected_moves[member]; if (shadow) ++stats->selected_shadow_orders[member]; }
    hash_word(damage); hash_blast(blast); hash_word(chain); hash_word(out_owner); hash_word(rw); hash_word(rh);
    ++stats->moves; return true;
}
static void move_slot80(unsigned tick)
{
    const unsigned slot=MAX_PWEAPON-1;
    assert(shotAvail[slot]); PlayerShotDataType before=playerShotData[slot];
    unsigned duration=shotAvail[slot]; bool special=true; int ox=-999, oy=-999;
    JE_integer damage=-999; JE_byte blast=0, chain=99, owner=99; JE_word rw=599, rh=598;
    moving_shot=(int)slot; event_count=probe_draw_count=0;
    assert(player_shot_move_and_draw((int)slot,&special,&ox,&oy,&damage,&blast,&chain,&owner,&rw,&rh));
    assert(shotAvail[slot]==duration-1 && !memcmp(&before,playerShotData+slot,sizeof(before)));
    assert(!event_count && !probe_draw_count && special && ox==-999 && oy==-999);
    assert(damage==-999 && !blast && chain==99 && owner==99 && rw==599 && rh==598);
    hash_word(0x31); hash_word(tick); hash_shot(slot); ++stats->slot80_ticks;
}

/* Advance one cohort in original ascending pool-slot order, including rotated
 * phase order. Independent clipping and lifetime removal are left untouched. */
static void follow_created(unsigned limit)
{
    const JE_WeaponType *w=weapons+expected.row.rid;
    created_pairs_and_orphans();
    unsigned tick;
    for (tick=1; tick<=limit; ++tick) {
        bool active=false, moved[8]={false};
        for (unsigned i=0; i<expected.count; ++i) {
            unsigned slot=expected.slots[i];
            if (!shotAvail[slot]) continue;
            active=true; moved[i]=true;
            if (slot==MAX_PWEAPON-1) move_slot80(tick);
            else move_case(slot,w,expected.phases[i],tick,(tick&1)!=0);
        }
        if (!active) break;
        for (unsigned i=0; i<expected.count; ++i) if (w->sg[expected.phases[i]]==143) {
            int partner=emitted_partner(i);
            if (partner<0) continue;
            unsigned left=expected.slots[i], right=expected.slots[partner];
            if (left==MAX_PWEAPON-1 || right==MAX_PWEAPON-1) continue;
            if (moved[i] && moved[partner]) assert_seam(left,right);
            if (!!shotAvail[left]!=!!shotAvail[right]) ++stats->independent_removal_cases;
        }
    }
    if (limit==255) {
        assert(tick<=101);
        for (unsigned i=0; i<expected.count; ++i) assert(!shotAvail[expected.slots[i]]);
        if (tick-1>stats->maximum_lifetime_ticks) stats->maximum_lifetime_ticks=tick-1;
        ++stats->lifetime_cases;
    }
}

static void assert_record_copy(const JE_WeaponType *a, const JE_WeaponType *b)
{
#define EQ(field) assert(a->field==b->field)
    EQ(drain); EQ(shotrepeat); EQ(multi); EQ(weapani); EQ(max); EQ(tx); EQ(ty); EQ(aim);
    EQ(acceleration); EQ(accelerationx); EQ(circlesize); EQ(sound); EQ(trail); EQ(shipblastfilter);
#undef EQ
    for (unsigned p=0; p<8; ++p) {
        assert(a->attack[p]==b->attack[p] && a->del[p]==b->del[p]);
        assert(a->sx[p]==b->sx[p] && a->sy[p]==b->sy[p]);
        assert(a->bx[p]==b->bx[p] && a->by[p]==b->by[p] && a->sg[p]==b->sg[p]);
    }
}
static void original_row_membership(void)
{
    const unsigned front_multi[11]={2,2,4,4,4,4,6,8,8,8,8};
    const unsigned front_max[11]={2,4,4,4,4,6,6,8,8,8,8};
    const unsigned front_selected[11]={1,2,2,0,2,3,3,4,4,4,2};
    const unsigned rear_selected[22]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,3,4};
    for (unsigned n=0; n<SOURCE_ROWS; ++n) {
        SourceRow row=source_row(n,0); const JE_WeaponType *w=weapons+row.rid;
        assert_record_copy(w,weapons+row.rid+1000);
        assert(w->multi>0 && w->multi<=w->max && w->max<=8);
        assert(w->weapani==0 && !w->circlesize && !w->aim && !w->accelerationx && w->trail==255);
        assert(w->shipblastfilter==((row.port==41 || row.rid==468 || table_index==0) ? 208 : 192));
        unsigned counts[2]={0,0};
        for (unsigned p=0; p<w->max; ++p) {
            assert(w->sg[p]>0 && w->sg[p]<1000 && (w->del[p]==98 || w->del[p]==100));
            assert(w->attack[p]<100 || w->attack[p]>=250);
            int member=joined_wave_member(w->sg[p]);
            if (member>=0) { ++counts[member]; assert_source_pair(w,p-(unsigned)member); }
        }
        unsigned wanted=n<REAR_ROWS ? rear_selected[n] : n<REAR_ROWS+FRONT_ROWS ?
                        front_selected[n-REAR_ROWS] : row.rid==467;
        assert(counts[0]==wanted && counts[1]==wanted);
        if (n<REAR_ROWS) {
            assert(w->multi==w->max && w->shotrepeat==6);
            assert(w->acceleration==(n<11 ? 0 : 1));
        } else if (n<REAR_ROWS+FRONT_ROWS) {
            unsigned p=n-REAR_ROWS;
            assert(w->multi==front_multi[p] && w->max==front_max[p]);
            assert(w->shotrepeat==((p==1 || p==5) ? 2 : 3));
            assert(w->acceleration==(p>=9));
            if (p==3 || p==10) for (unsigned k=0; k<4; ++k) assert(w->sg[k]==748+k);
            if (p==4) assert(w->by[2]-w->by[0]==14 && w->by[3]-w->by[1]==14);
        } else assert(w->shotrepeat==3 && w->acceleration==1 && w->multi==w->max);
    }
    assert(source_port_poweruse[table_index][11]==50 && source_port_poweruse[table_index][41]==50);
}

static void normal_rows(void)
{
    const int drift[]={-20,-6,-5,-4,-3,-1,0,1,3,4,5,6,20};
    for (row_index=0; row_index<SOURCE_ROWS; ++row_index) for (unsigned copy=0; copy<2; ++copy) {
        SourceRow row=source_row(row_index,copy); const JE_WeaponType *w=weapons+row.rid;
        for (unsigned phase=0; phase<=w->max; ++phase) {
            ++stats->phase_cases; stats->valid_phase_mask|=1U<<phase;
            for (unsigned dx=0; dx<sizeof(drift)/sizeof(*drift); ++dx)
                for (unsigned dy=0; dy<sizeof(drift)/sizeof(*drift); ++dy) {
                    create_case(row,phase,drift[dx],drift[dy],w->multi,-1,500);
                    follow_created(4); ++stats->drift_phase_cases;
                }
        }
        for (unsigned invalid=9; invalid<=255; invalid+=246) {
            create_case(row,invalid,1,1,w->multi,-1,500); follow_created(4);
            ++stats->phase_cases;
            if (invalid==9) ++stats->invalid_phase9_cases; else ++stats->invalid_phase255_cases;
        }
    }
}
static void capacity_and_power(void)
{
    for (row_index=0; row_index<SOURCE_ROWS; ++row_index) for (unsigned copy=0; copy<2; ++copy) {
        SourceRow row=source_row(row_index,copy); const JE_WeaponType *w=weapons+row.rid;
        unsigned cost=source_port_poweruse[table_index][row.port];
        const unsigned energies[]={0,1,cost ? cost-1 : 0,cost,cost+1,99,100,500};
        for (unsigned phase=0; phase<=w->max; ++phase) {
            for (unsigned available=0; available<=w->multi; ++available) for (int layout=0; layout<3; ++layout) {
                create_case(row,phase,-20,20,available,layout,500);
                created_pairs_and_orphans(); ++stats->capacity_cases;
            }
            for (unsigned e=0; e<sizeof(energies)/sizeof(*energies); ++e) {
                create_case(row,phase,20,-20,w->multi,-1,energies[e]);
                created_pairs_and_orphans(); ++stats->power_cases;
            }
        }
        /* A slot80 half is preserved as a distinct production exception. It
         * decrements duration without movement, outputs, probes or rendering. */
        for (unsigned phase=0; phase<=w->max; ++phase) {
            create_case(row,phase,0,0,1,2,500);
            assert(expected.count==1 && expected.slots[0]==MAX_PWEAPON-1);
            unsigned ticks=0; while (shotAvail[MAX_PWEAPON-1]) move_slot80(++ticks);
            assert(ticks==w->del[expected.phases[0]]);
        }
    }
}
static void boundary_and_lifetime(void)
{
    const int target_x[]={-35,-34,-33,289,290,291};
    const int target_y[]={-16,-15,-14,180,181,182,189,190,191};
    for (row_index=0; row_index<SOURCE_ROWS; ++row_index) for (unsigned copy=0; copy<2; ++copy) {
        SourceRow row=source_row(row_index,copy); const JE_WeaponType *w=weapons+row.rid;
        for (unsigned p=0; p<w->max; ++p) {
            for (unsigned i=0; i<sizeof(target_x)/sizeof(*target_x); ++i) {
                create_case(row,p,0,0,w->multi,-1,500); PlayerShotDataType *s=playerShotData;
                s->shotX=(JE_integer)(target_x[i]-s->shotXM-s->shotXC);
                move_case(0,w,p,1,true); ++stats->boundary_cases;
            }
            for (unsigned i=0; i<sizeof(target_y)/sizeof(*target_y); ++i) {
                create_case(row,p,0,0,w->multi,-1,500); PlayerShotDataType *s=playerShotData;
                s->shotY=(JE_integer)(target_y[i]-s->shotYM-s->shotYC);
                move_case(0,w,p,1,true); ++stats->boundary_cases;
            }
            /* Authentic entire cohorts, at both drift clamps and zero drift,
             * verify seams through original removal rather than four samples. */
            for (int drift=-20; drift<=20; drift+=20) {
                create_case(row,p,drift,0,w->multi,-1,500); follow_created(255);
            }
            /* Explicit duration-one terminal draw: no next-tick call is made. */
            create_case(row,p,0,0,w->multi,-1,500); shotAvail[0]=1;
            move_case(0,w,p,1,true); assert(!shotAvail[0]); ++stats->boundary_cases;
        }
    }
}

/* Four original requests share the live pool and phase cursor. Shorter
 * multi/max cycles (frontP2 2/4, frontP6 4/6), distinct cohort ages, intentional
 * canvas overlap, and lowest-free-slot reuse are preserved. This is creation
 * and motion coverage, not a claim to execute the whole input/cadence caller. */
static void repeated_live_volleys(void)
{
    for (row_index=0; row_index<SOURCE_ROWS; ++row_index) for (unsigned copy=0; copy<2; ++copy) {
        SourceRow row=source_row(row_index,copy); const JE_WeaponType *w=weapons+row.rid;
        int phase_by_slot[MAX_PWEAPON], cohort_by_slot[MAX_PWEAPON];
        for (unsigned i=0; i<MAX_PWEAPON; ++i) phase_by_slot[i]=cohort_by_slot[i]=-1;
        reset();
        unsigned cursor=0;
        for (unsigned volley=0; volley<4; ++volley) {
            assert(shotMultiPos[row.bay]==cursor); request_case(row,0,0);
            assert(expected.count==w->multi && !strcmp(expected.reason,"complete"));
            created_pairs_and_orphans();
            for (unsigned i=0; i<expected.count; ++i) {
                unsigned slot=expected.slots[i]; phase_by_slot[slot]=(int)expected.phases[i];
                cohort_by_slot[slot]=(int)volley;
                cursor=next_phase(cursor,w->max);
            }
            assert(shotMultiPos[row.bay]==cursor);
            for (unsigned tick=0; tick<3; ++tick) {
                for (unsigned slot=0; slot<MAX_PWEAPON-1; ++slot) if (shotAvail[slot]) {
                    assert(phase_by_slot[slot]>=0);
                    move_case(slot,w,(unsigned)phase_by_slot[slot],1+volley*3+tick,(tick&1)==0);
                }
                unsigned lefts[16], rights[16], pairs=0;
                for (unsigned a=0; a<MAX_PWEAPON-1; ++a) if (shotAvail[a] && playerShotData[a].shotGr==143)
                    for (unsigned b=0; b<MAX_PWEAPON-1; ++b) if (shotAvail[b] &&
                            playerShotData[b].shotGr==144 && cohort_by_slot[a]==cohort_by_slot[b] &&
                            phase_by_slot[b]==phase_by_slot[a]+1) {
                        assert_seam(a,b); assert(pairs<16); lefts[pairs]=a; rights[pairs++]=b;
                    }
                for (unsigned a=0; a<pairs; ++a) for (unsigned b=a+1; b<pairs; ++b) {
                    const PlayerShotDataType *u=playerShotData+lefts[a], *v=playerShotData+lefts[b];
                    bool overlap=u->shotX<v->shotX+24 && v->shotX<u->shotX+24 &&
                                 u->shotY<v->shotY+14 && v->shotY<u->shotY+14;
                    if (overlap) {
                        ++stats->canvas_overlap_cases; hash_word(0x42);
                        hash_word(lefts[a]); hash_word(rights[a]); hash_word(lefts[b]); hash_word(rights[b]);
                    }
                }
            }
            ++stats->repeat_cases;
        }
        assert(power==500-4*source_port_poweruse[table_index][row.port]);
    }
}

static void print_table(unsigned index)
{
    const TableStats *s=table_stats+index;
    printf("{\"name\":\"%s\",\"source_rows\":36,\"record_copies\":2,\"rng_calls\":%u,"
           "\"create_cases\":%u,\"emits\":%u,\"drift_phase_cases\":%u,\"volley_phase_cases\":%u,"
           "\"valid_initial_phase_mask\":%u,\"invalid_phase9_cases\":%u,\"invalid_phase255_cases\":%u,"
           "\"capacity_cases\":%u,\"power_cases\":%u,\"repeated_live_volley_cases\":%u,"
           "\"boundary_cases\":%u,\"full_cohort_lifetime_cases\":%u,\"maximum_lifetime_ticks\":%u,"
           "\"movement_ticks\":%u,\"offscreen_movement_ticks\":%u,\"slot80_duration_only_ticks\":%u,"
           "\"draws\":%u,\"shadow_draws\":%u,\"bank12_draws\":%u,\"seam_cases\":%u,"
           "\"complete_original_pairs\":%u,\"equal_age_12px_seam_checks\":%u,"
           "\"original_selected_orphans\":[%u,%u],\"independent_removal_cases\":%u,"
           "\"original_logical_canvas_overlap_cases\":%u,\"joined_wave_emissions\":[%u,%u],"
           "\"joined_wave_movement_ticks\":[%u,%u],\"shadow_before_head_cases\":[%u,%u],"
           "\"movement_extent\":[%d,%d,%d,%d],\"charge468_blastfilter\":208,"
           "\"shot_state_order_fnv1a64\":\"%016" PRIx64 "\","
           "\"blast_normalized_state_order_fnv1a64\":\"%016" PRIx64 "\"}",
           table_names[index],s->rng_calls,s->requests,s->emits,s->drift_phase_cases,s->phase_cases,
           s->valid_phase_mask,s->invalid_phase9_cases,s->invalid_phase255_cases,
           s->capacity_cases,s->power_cases,s->repeat_cases,s->boundary_cases,s->lifetime_cases,
           s->maximum_lifetime_ticks,s->moves,s->offscreen_moves,s->slot80_ticks,s->draws,s->shadows,
           s->bank12_draws,s->seam_cases,s->complete_pairs,s->seam_ticks,
           s->selected_orphans[0],s->selected_orphans[1],s->independent_removal_cases,s->canvas_overlap_cases,
           s->selected_emits[0],s->selected_emits[1],s->selected_moves[0],s->selected_moves[1],
           s->selected_shadow_orders[0],s->selected_shadow_orders[1],
           s->movement_min_x,s->movement_max_x,s->movement_min_y,s->movement_max_y,
           s->full_hash,s->normalized_hash);
}
int main(void)
{
    for (table_index=0; table_index<3; ++table_index) {
        stats=table_stats+table_index; stats->full_hash=stats->normalized_hash=UINT64_C(14695981039346656037);
        stats->movement_min_x=stats->movement_min_y=32767;
        stats->movement_max_x=stats->movement_max_y=-32768; weapons=weapon_tables[table_index];
        original_row_membership(); normal_rows(); capacity_and_power(); boundary_and_lifetime(); repeated_live_volleys();
        assert(!stats->rng_calls && stats->offscreen_moves && stats->bank12_draws && stats->slot80_ticks);
        assert(stats->valid_phase_mask==511 && stats->invalid_phase9_cases && stats->invalid_phase255_cases);
        assert(stats->seam_ticks && stats->canvas_overlap_cases && stats->independent_removal_cases);
        for (unsigned i=0; i<2; ++i)
            assert(stats->selected_emits[i] && stats->selected_moves[i] && stats->selected_shadow_orders[i] && stats->selected_orphans[i]);
        for (unsigned n=0; n<SOURCE_ROWS; ++n) {
            SourceRow row=source_row(n,0); unsigned rid=primary_id(row.rid);
            bool selected=(rid>=292 && rid<=297) || (rid>=756 && rid<=766 && rid!=759) || rid==467;
            assert(!!stats->row_seams[n]==selected);
            if (selected) assert(stats->row_orphans[n]);
        }
    }
    assert(table_stats[0].normalized_hash==table_stats[1].normalized_hash);
    assert(table_stats[1].normalized_hash==table_stats[2].normalized_hash);
    assert(table_stats[0].full_hash!=table_stats[1].full_hash && table_stats[1].full_hash==table_stats[2].full_hash);
    printf("{\"status\":\"PASS\",\"rear_rows\":22,\"front41_rows\":11,\"charge_records\":[465,467,468],"
           "\"source_rows_per_table\":36,\"source_item_tables\":3,\"primary_plus1000_copies\":2,"
           "\"joined_wave_ids\":[143,144],\"rng_calls\":0,\"directional_selected_witness\":false,"
           "\"dormant118_1118_executed_as_reachable\":false,\"original_shadow_then_head_order_verified\":true,"
           "\"original_partial_capacity_orphans_preserved\":true,\"original_independent_clipping_preserved\":true,"
           "\"equal_age_pairs_retain_12px_seam\":true,\"inter_wave_overlap_is_logical_canvas_only\":true,"
           "\"all_three_blast_normalized_state_order_hashes_equal\":true,\"game_runs\":0,\"tables\":[");
    for (unsigned i=0; i<3; ++i) { if (i) putchar(','); print_table(i); }
    puts("]}"); return 0;
}
