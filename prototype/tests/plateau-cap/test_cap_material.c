/* SPDX-License-Identifier: GPL-2.0-or-later
 * Synthetic cap oracle only: no game, SDL, asset pack, media, or captures. */
#include "world_material_fast.h"
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t assertions, blend_cases, coordinate_cases, allocation_calls;
static bool count_allocations;
#define CHECK(condition) do { ++assertions; if (!(condition)) { \
 fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #condition); \
 exit(EXIT_FAILURE); } } while (0)

/* Link-time traps cover allocation from the production objects under test. */
void *__real_malloc(size_t);
void *__real_calloc(size_t, size_t);
void *__real_realloc(void *, size_t);
void *__real_aligned_alloc(size_t, size_t);
void *__wrap_malloc(size_t n)
{ if (count_allocations) ++allocation_calls; return __real_malloc(n); }
void *__wrap_calloc(size_t n, size_t s)
{ if (count_allocations) ++allocation_calls; return __real_calloc(n, s); }
void *__wrap_realloc(void *p, size_t n)
{ if (count_allocations) ++allocation_calls; return __real_realloc(p, n); }
void *__wrap_aligned_alloc(size_t alignment, size_t n)
{ if (count_allocations) ++allocation_calls; return __real_aligned_alloc(alignment, n); }

static uint8_t lower_bytes[G101_ATLAS_BYTES];
static uint8_t cap_bytes[G101_ATLAS_BYTES];
static G101Atlas lower_atlas = {lower_bytes, sizeof(lower_bytes), 768, 896, 8};
static G101Atlas cap_atlas = {cap_bytes, sizeof(cap_bytes), 768, 896, 8};
static struct {
 uint64_t before;
 G101FastContext context;
 uint64_t after;
} guarded_fast;
static G101FastContext snapshot;
static void *map_cells[G101_MAP_ROWS][G101_MAP_COLS];
#define FAST (&guarded_fast.context)
#define CANARY UINT64_C(0xc89d3a7406e215bf)

/* Cap sampling must reuse the existing bounded lookup tables. */
_Static_assert(sizeof(((G101FastContext *)0)->columns) == 2560 * sizeof(uint16_t),
 "one existing full-canvas column lookup table");
_Static_assert(sizeof(((G101FastContext *)0)->rows) == 1600 * sizeof(uint32_t),
 "one existing full-canvas row lookup table");
_Static_assert(sizeof(G101FastContext) <= 2560 * sizeof(uint16_t) +
 1600 * sizeof(uint32_t) + 32, "no duplicate cap-coordinate lookup tables");

static unsigned positive_remainder(int64_t value, unsigned period)
{
 int64_t r = value % (int64_t)period;
 return (unsigned)(r < 0 ? r + period : r);
}

/* Deliberately independent of all production samplers and blend helpers. */
static size_t oracle_index(const G101Context *world, int64_t sx, int64_t sy)
{
 uint64_t x = positive_remainder(sx, 768) +
  UINT64_C(8) * positive_remainder(world->world_x, 768);
 uint64_t y = positive_remainder(sy, 896) +
  UINT64_C(8) * positive_remainder(world->world_y, 896);
 return (size_t)((y % 896) * 768 + x % 768);
}

static void tagged_pixel(size_t index, bool cap, uint8_t out[4])
{
 out[0] = (uint8_t)index ^ (cap ? 0xa5 : 0);
 out[1] = (uint8_t)(index >> 8) ^ (cap ? 0x6d : 0);
 out[2] = (uint8_t)(index >> 16) ^ (cap ? 0xf3 : 0);
 /* An atlas alpha byte is never allowed to replace accepted-source alpha. */
 out[3] = cap ? (uint8_t)(index * 73) : 255;
}

static void fill_atlases(void)
{
 for (size_t i = 0; i < G101_ATLAS_BYTES / 4; ++i) {
  tagged_pixel(i, false, lower_bytes + 4 * i);
  tagged_pixel(i, true, cap_bytes + 4 * i);
 }
}

static void oracle_blend(const uint8_t accepted[4], const uint8_t cap[4],
 uint8_t weight, uint8_t out[4])
{
 memcpy(out, accepted, 4);
 if (!accepted[3] || !weight) return;
 for (unsigned c = 0; c < 3; ++c) {
  uint64_t numerator = (uint64_t)accepted[c] * (255u - weight) +
   (uint64_t)cap[c] * weight + 127u;
  out[c] = (uint8_t)(numerator / 255u);
 }
}

static void prepare(const G101Context *world)
{
 CHECK(g101_fast_prepare(FAST, world, &lower_atlas, 8));
 CHECK(FAST->valid && FAST->rgba == lower_bytes);
 CHECK(guarded_fast.before == CANARY && guarded_fast.after == CANARY);
 for (int x = 0; x < G101_CANVAS_W_HD; ++x) {
  CHECK(FAST->columns[x] < 768 * 4 && FAST->columns[x] % 4 == 0);
  CHECK(FAST->columns[x] == 4 * (oracle_index(world, x, 0) % 768));
 }
 for (int y = 0; y < G101_CANVAS_H_HD; ++y) {
  CHECK(FAST->rows[y] < G101_ATLAS_BYTES && FAST->rows[y] % (768 * 4) == 0);
  CHECK(FAST->rows[y] == 4 * (oracle_index(world, 0, y) / 768) * 768);
 }
 memcpy(&snapshot, FAST, sizeof(snapshot));
}

static void check_unchanged(void)
{
 CHECK(!memcmp(&snapshot, FAST, sizeof(snapshot)));
 CHECK(guarded_fast.before == CANARY && guarded_fast.after == CANARY);
}

static void compare_pixel(const G101Context *world, int x, int y,
 const uint8_t accepted[4], uint8_t weight)
{
 uint8_t scalar[4], speedy[4], expected[4], cap[4];
 tagged_pixel(oracle_index(world, x, y), true, cap);
 oracle_blend(accepted, cap, weight, expected);
 bool want = accepted[3] != 0 && weight != 0;
 bool a = g101_select_cap_pixel(world, &cap_atlas, accepted, weight, 8, x, y, scalar);
 bool b = g101_fast_select_cap(FAST, cap_bytes, accepted, weight, x, y, speedy);
 CHECK(a == want && b == want);
 CHECK(!memcmp(scalar, expected, 4) && !memcmp(speedy, expected, 4));
 CHECK(scalar[3] == accepted[3] && speedy[3] == accepted[3]);
 ++coordinate_cases;
}

static void test_all_color_weight_combinations(void)
{
 G101Context world = {true, false, 0, 0};
 prepare(&world);
 for (unsigned accepted_value = 0; accepted_value < 256; ++accepted_value)
  for (unsigned cap_value = 0; cap_value < 256; ++cap_value)
   for (unsigned weight = 0; weight < 256; ++weight) {
    /* Each channel transformation is bijective, so EACH RGB channel sees
     * all 256^3 accepted/material/weight combinations, not just red. */
    uint8_t accepted[4] = {(uint8_t)accepted_value,
     (uint8_t)(accepted_value * 73 + 19), (uint8_t)(255 - accepted_value), 173};
    uint8_t expected[4], scalar[4], speedy[4];
    cap_bytes[0] = (uint8_t)cap_value;
    cap_bytes[1] = (uint8_t)(cap_value * 151 + 37);
    cap_bytes[2] = (uint8_t)(cap_value ^ 0xa5);
    cap_bytes[3] = (uint8_t)(accepted_value + cap_value + weight);
    oracle_blend(accepted, cap_bytes, (uint8_t)weight, expected);
    bool a = g101_select_cap_pixel(&world, &cap_atlas, accepted,
     (uint8_t)weight, 8, 0, 0, scalar);
    bool b = g101_fast_select_cap(FAST, cap_bytes, accepted,
     (uint8_t)weight, 0, 0, speedy);
    CHECK(a == (weight != 0) && b == a);
    CHECK(!memcmp(scalar, expected, 4) && !memcmp(speedy, expected, 4));
    if (weight == 255) CHECK(!memcmp(scalar, cap_bytes, 3));
    ++blend_cases;
   }
 check_unchanged();
 fill_atlases();
}

static void test_alpha_and_weight_independence(void)
{
 G101Context world = {true, false, -93, 112};
 prepare(&world);
 for (unsigned alpha = 0; alpha < 256; ++alpha)
  for (unsigned weight = 0; weight < 256; ++weight) {
   uint8_t accepted[4] = {97, (uint8_t)(weight * 7), (uint8_t)(alpha * 13), (uint8_t)alpha};
   compare_pixel(&world, (int)weight * 10, (int)alpha * 6, accepted, (uint8_t)weight);
  }
 check_unchanged();
}

static void test_coordinates_and_distinct_atlases(void)
{
 static const int64_t origins[][2] = {
  {0, 0}, {48, 8009}, {37, 7919}, {37, 7918}, {-1, -1}, {-1000, -1000},
  {96, 112}, {-96, -112}, {24 * 299, 28 * 299},
  {INT64_MIN, INT64_MAX}, {INT64_MAX, INT64_MIN}, {47, -27}
 };
 static const int xs[] = {0, 1, 7, 8, 95, 96, 191, 192, 767, 768, 769, 1535, 1536, 2559};
 static const int ys[] = {0, 1, 7, 8, 111, 112, 223, 224, 895, 896, 897, 1599};
 static const uint8_t weights[] = {0, 1, 63, 127, 128, 254, 255};
 for (size_t n = 0; n < sizeof(origins) / sizeof(*origins); ++n) {
  G101Context world = {true, false, origins[n][0], origins[n][1]};
  prepare(&world);
  /* Every canvas pixel, including every wrap, for every transform. */
  for (int y = 0; y < G101_CANVAS_H_HD; ++y)
   for (int x = 0; x < G101_CANVAS_W_HD; ++x) {
    uint8_t accepted[4] = {(uint8_t)x, (uint8_t)y, (uint8_t)(x + 3 * y),
     (uint8_t)(x + y + n)};
    compare_pixel(&world, x, y, accepted, (uint8_t)(3 * x + 7 * y + n));
   }
  for (size_t yi = 0; yi < sizeof(ys) / sizeof(*ys); ++yi)
   for (size_t xi = 0; xi < sizeof(xs) / sizeof(*xs); ++xi) {
    uint8_t lower_expected[4], cap_expected[4], lower_actual[4], cap_actual[4];
    uint8_t accepted[4] = {31, 127, 229, 143};
    size_t i = oracle_index(&world, xs[xi], ys[yi]);
    tagged_pixel(i, false, lower_expected); tagged_pixel(i, true, cap_expected);
    CHECK(g101_fast_sample(FAST, xs[xi], ys[yi], lower_actual));
    CHECK(!memcmp(lower_actual, lower_expected, 4));
    CHECK(g101_fast_select_cap(FAST, cap_bytes, accepted, 255, xs[xi], ys[yi], cap_actual));
    CHECK(!memcmp(cap_actual, cap_expected, 3) && cap_actual[3] == accepted[3]);
    CHECK(memcmp(lower_actual, cap_actual, 3));
    /* Existing lower-material selection continues using the lower atlas. */
    G101Pixel source = {.accepted_rgba = accepted, .clean_rgba = accepted,
     .primary_weight = 255, .reconstruction_verified = true};
    CHECK(g101_fast_select_pixel(FAST, &source, true, xs[xi], ys[yi], lower_actual));
    CHECK(!memcmp(lower_actual, lower_expected, 3) && lower_actual[3] == accepted[3]);
    for (size_t wi = 0; wi < sizeof(weights) / sizeof(*weights); ++wi)
     compare_pixel(&world, xs[xi], ys[yi], accepted, weights[wi]);
   }
  check_unchanged();
 }
}

static void scalar_fallback(const G101Context *world, const G101Atlas *atlas,
 int density, uint8_t weight, const uint8_t accepted[4])
{
 uint8_t out[4] = {0x5a, 0x5a, 0x5a, 0x5a};
 CHECK(!g101_select_cap_pixel(world, atlas, accepted, weight, density, INT64_MIN, INT64_MAX, out));
 CHECK(!memcmp(out, accepted, 4));
}

static void fast_fallback(const G101FastContext *fast, const uint8_t *cap,
 int x, int y, uint8_t weight, const uint8_t accepted[4])
{
 uint8_t out[4] = {0x5a, 0x5a, 0x5a, 0x5a};
 CHECK(!g101_fast_select_cap(fast, cap, accepted, weight, x, y, out));
 CHECK(!memcmp(out, accepted, 4));
}

static void test_fallback_and_invalidation(void)
{
 G101Context world = {true, false, 37, 7919}, invalid = {0};
 uint8_t accepted[4] = {121, 49, 37, 173};
 prepare(&world);
 scalar_fallback(&world, &cap_atlas, 8, 0, accepted);
 scalar_fallback(NULL, &cap_atlas, 8, 255, accepted);
 scalar_fallback(&invalid, &cap_atlas, 8, 255, accepted);
 invalid = world; invalid.rejected = true;
 scalar_fallback(&invalid, &cap_atlas, 8, 255, accepted);
 scalar_fallback(&world, NULL, 8, 255, accepted);
 const int densities[] = {INT_MIN, -8, 0, 1, 4, 7, 9, INT_MAX};
 for (size_t i = 0; i < sizeof(densities) / sizeof(*densities); ++i)
  scalar_fallback(&world, &cap_atlas, densities[i], 255, accepted);
 G101Atlas bad = cap_atlas;
 bad.rgba = NULL; scalar_fallback(&world, &bad, 8, 255, accepted);
 bad = cap_atlas; --bad.bytes; scalar_fallback(&world, &bad, 8, 255, accepted);
 bad = cap_atlas; ++bad.bytes; scalar_fallback(&world, &bad, 8, 255, accepted);
 bad = cap_atlas; --bad.width; scalar_fallback(&world, &bad, 8, 255, accepted);
 bad = cap_atlas; ++bad.height; scalar_fallback(&world, &bad, 8, 255, accepted);
 bad = cap_atlas; bad.density = 4; scalar_fallback(&world, &bad, 8, 255, accepted);
 fast_fallback(FAST, cap_bytes, 0, 0, 0, accepted);
 fast_fallback(NULL, cap_bytes, 0, 0, 255, accepted);
 fast_fallback(FAST, NULL, 0, 0, 255, accepted);
 const int outside[][2] = {{-1, 0}, {0, -1}, {2560, 0}, {0, 1600},
  {INT_MIN, INT_MAX}, {INT_MAX, INT_MIN}, {-1, -1}, {2560, 1600}};
 for (size_t i = 0; i < sizeof(outside) / sizeof(*outside); ++i)
  fast_fallback(FAST, cap_bytes, outside[i][0], outside[i][1], 255, accepted);
 accepted[3] = 0;
 scalar_fallback(&world, &cap_atlas, 8, 255, accepted);
 fast_fallback(FAST, cap_bytes, 0, 0, 255, accepted);
 accepted[3] = 173;
 check_unchanged();
 g101_fast_invalidate(FAST);
 CHECK(!FAST->valid && FAST->rgba == NULL);
 fast_fallback(FAST, cap_bytes, 0, 0, 255, accepted);
 /* Failed preparation must discard a previously valid frame. */
 for (unsigned why = 0; why < 6; ++why) {
  prepare(&world); invalid = world; bad = lower_atlas;
  const G101Context *w = &invalid;
  const G101Atlas *a = &bad;
  int density = 8;
  if (why == 0) invalid.valid = false;
  if (why == 1) invalid.rejected = true;
  if (why == 2) --bad.bytes;
  if (why == 3) density = 4;
  if (why == 4) w = NULL;
  if (why == 5) a = NULL;
  CHECK(!g101_fast_prepare(FAST, w, a, density));
  CHECK(!FAST->valid && FAST->rgba == NULL);
  fast_fallback(FAST, cap_bytes, 0, 0, 255, accepted);
 }
 prepare(&world); compare_pixel(&world, 2559, 1599, accepted, 255);
 check_unchanged();
}

static void test_extreme_scalar_coordinates(void)
{
 static const int64_t values[] = {INT64_MIN, INT64_MIN + 1, -896, -769, -768,
  -1, 0, 1, 767, 768, 895, 896, INT64_MAX - 1, INT64_MAX};
 static const int64_t origins[][2] = {{INT64_MIN, INT64_MAX},
  {INT64_MAX, INT64_MIN}, {-1000, -1000}, {48, 8009}};
 uint8_t accepted[4] = {59, 117, 211, 137};
 for (size_t o = 0; o < sizeof(origins) / sizeof(*origins); ++o) {
  G101Context world = {true, false, origins[o][0], origins[o][1]};
  for (size_t y = 0; y < sizeof(values) / sizeof(*values); ++y)
   for (size_t x = 0; x < sizeof(values) / sizeof(*values); ++x)
    for (unsigned weight = 0; weight < 256; ++weight) {
     uint8_t cap[4], expected[4], actual[4];
     tagged_pixel(oracle_index(&world, values[x], values[y]), true, cap);
     oracle_blend(accepted, cap, (uint8_t)weight, expected);
     CHECK(g101_select_cap_pixel(&world, &cap_atlas, accepted, (uint8_t)weight,
      8, values[x], values[y], actual) == (weight != 0));
     CHECK(!memcmp(actual, expected, 4));
     ++coordinate_cases;
    }
 }
}

#define CLIP_W (80 * 8)
#define CLIP_H (64 * 8)
static uint32_t clipped[2 + CLIP_W * CLIP_H];
static uint32_t pack(const uint8_t rgba[4])
{ return (uint32_t)rgba[0] | (uint32_t)rgba[1] << 8 |
  (uint32_t)rgba[2] << 16 | (uint32_t)rgba[3] << 24; }

static void test_clipped_quadrants_and_phase(void)
{
 static const int origins[][2] = {{-7, -9}, {75, 60}, {-23, 63}, {79, -27}};
 static const int parts[][2] = {{12, 14}, {0, 0}, {12, 0}, {0, 14}};
 uint8_t accepted[4] = {67, 131, 193, 157};
 for (size_t n = 0; n < sizeof(origins) / sizeof(*origins); ++n) {
  int ox = origins[n][0], oy = origins[n][1];
  G101Context world;
  g101_begin_frame(&world);
  CHECK(g101_observe_row(&world, map_cells, sizeof(map_cells), &map_cells[40][2],
   sizeof(void *), 12, ox, oy));
  prepare(&world);
  for (size_t i = 0; i < sizeof(clipped) / sizeof(*clipped); ++i) clipped[i] = UINT32_C(0x11223344);
  for (size_t q = 0; q < sizeof(parts) / sizeof(*parts); ++q)
   for (int ay = parts[q][1] * 8; ay < (parts[q][1] + 14) * 8; ++ay)
    for (int ax = parts[q][0] * 8; ax < (parts[q][0] + 12) * 8; ++ax) {
     int x = ox * 8 + ax, y = oy * 8 + ay;
     if (x < 0 || y < 0 || x >= CLIP_W || y >= CLIP_H) continue;
     uint8_t actual[4];
     CHECK(g101_fast_select_cap(FAST, cap_bytes, accepted, 127, x, y, actual));
     clipped[1 + y * CLIP_W + x] = pack(actual);
    }
  CHECK(clipped[0] == UINT32_C(0x11223344));
  CHECK(clipped[1 + CLIP_W * CLIP_H] == UINT32_C(0x11223344));
  for (int y = 0; y < CLIP_H; ++y)
   for (int x = 0; x < CLIP_W; ++x) {
    uint32_t expected = UINT32_C(0x11223344);
    if (x >= ox * 8 && x < (ox + 24) * 8 && y >= oy * 8 && y < (oy + 28) * 8) {
     uint8_t cap[4], rgba[4];
     tagged_pixel(oracle_index(&world, x, y), true, cap);
     oracle_blend(accepted, cap, 127, rgba); expected = pack(rgba);
    }
    CHECK(clipped[1 + y * CLIP_W + x] == expected);
   }
  check_unchanged();
 }
 /* The 27->0 terrain row rollover carries a screen pixel down eight HD
  * pixels while preserving its material phase; no second cap origin. */
 G101Context before = {true, false, 48, 199 * 28 + 1};
 G101Context after = {true, false, 48, 198 * 28 + 28};
 CHECK(after.world_y == before.world_y - 1);
 for (int y = 0; y < G101_CANVAS_H_HD - 8; ++y) {
  uint8_t a[4], b[4];
  CHECK(g101_select_cap_pixel(&before, &cap_atlas, accepted, 255, 8, 177, y, a));
  CHECK(g101_select_cap_pixel(&after, &cap_atlas, accepted, 255, 8, 177, y + 8, b));
  CHECK(!memcmp(a, b, 4));
 }
 /* Existing actor +1 logical backing phase is exactly +8 HD once. */
 G101Context actor = {true, false, 48 - 7, 110 * 28 + 12};
 uint8_t actual[4], expected[4], wrong[4];
 CHECK(g101_select_cap_pixel(&actor, &cap_atlas, accepted, 255, 8, 7 * 8, -11 * 8, actual));
 tagged_pixel((size_t)(110 * 224 + 8) % 896 * 768 + 2 * 192, true, expected);
 CHECK(!memcmp(actual, expected, 3) && actual[3] == accepted[3]);
 CHECK(g101_select_cap_pixel(&actor, &cap_atlas, accepted, 255, 8, 7 * 8, -10 * 8, wrong));
 CHECK(memcmp(actual, wrong, 3));
}

int main(void)
{
 guarded_fast.before = guarded_fast.after = CANARY;
 fill_atlases(); count_allocations = true;
 test_all_color_weight_combinations();
 test_alpha_and_weight_independence();
 test_coordinates_and_distinct_atlases();
 test_fallback_and_invalidation();
 test_extreme_scalar_coordinates();
 test_clipped_quadrants_and_phase();
 count_allocations = false;
 CHECK(allocation_calls == 0);
 CHECK(guarded_fast.before == CANARY && guarded_fast.after == CANARY);
 printf("PASS cap integer oracle: %" PRIu64 " exhaustive color/weight cases per RGB channel\n", blend_cases);
 printf("PASS cap scalar/fast, all alpha bytes, distinct atlases, phase/wrap/extremes/clipping: %" PRIu64 " pixel cases\n", coordinate_cases);
 printf("PASS exact accepted fallback, invalidation/recovery, full-weight identity, lower-atlas isolation\n");
 printf("PASS zero allocations; existing lookup payload=%zu bytes, context=%zu bytes; %" PRIu64 " assertions\n",
  sizeof(FAST->columns) + sizeof(FAST->rows), sizeof(*FAST), assertions);
 return EXIT_SUCCESS;
}
