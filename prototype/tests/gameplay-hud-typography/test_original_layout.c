/* Synthetic-only command oracle for the original source-extracted text helpers.
 * This does not implement, change, or validate a proposed new renderer.
 */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "source_constants.inc"

typedef uint8_t Uint8;
typedef int8_t Sint8;
typedef struct { unsigned int identity; } SDL_Surface;
typedef struct {
    unsigned int width, height;
    bool exists;
    unsigned int ink_x, ink_y, ink_width, ink_height;
} Sprite;

enum { FONT_COUNT = 3, GLYPH_COUNT = 127, MAX_COMMANDS = 32768 };
enum { HUE_VALUE, DARK };
typedef struct {
    SDL_Surface *screen;
    int operation, x, y;
    unsigned int font, glyph;
    Uint8 hue;
    Sint8 value;
    bool black;
} Command;

static Sprite metadata[FONT_COUNT][GLYPH_COUNT];
static SDL_Surface surfaces[2] = {{17}, {29}};
static Command actual[MAX_COMMANDS], expected[MAX_COMMANDS];
static size_t actual_count, expected_count;
static unsigned long strings, width_cases, stream_cases, compared_commands;
static unsigned long map_checks, missing_cases, pixel_cases, metric_cases;

static Sprite *sprite(unsigned int font, unsigned int glyph)
{
    assert(font < FONT_COUNT && glyph < GLYPH_COUNT);
    return &metadata[font][glyph];
}

static bool sprite_exists(unsigned int font, unsigned int glyph)
{
    return sprite(font, glyph)->exists;
}

static void blit_sprite_hv_unsafe(SDL_Surface *screen, int x, int y,
                                  unsigned int font, unsigned int glyph,
                                  Uint8 hue, Sint8 value)
{
    assert(sprite_exists(font, glyph));
    assert(actual_count < MAX_COMMANDS);
    actual[actual_count++] = (Command){screen, HUE_VALUE, x, y, font, glyph, hue, value, false};
}

static void blit_sprite_dark(SDL_Surface *screen, int x, int y,
                             unsigned int font, unsigned int glyph, bool black)
{
    assert(sprite_exists(font, glyph));
    assert(actual_count < MAX_COMMANDS);
    actual[actual_count++] = (Command){screen, DARK, x, y, font, glyph, 0, 0, black};
}

/* DARKEN and TRICK route elsewhere. They are deliberately outside this oracle. */
static void JE_outTextAndDarken(SDL_Surface *screen, int x, int y, const char *s,
                               unsigned int color, unsigned int brightness, unsigned int font)
{
    (void)screen; (void)x; (void)y; (void)s; (void)color; (void)brightness; (void)font;
    assert(!"DARKEN is outside this oracle");
}

static void JE_outTextModify(SDL_Surface *screen, int x, int y, const char *s,
                            unsigned int color, unsigned int brightness, unsigned int font)
{
    (void)screen; (void)x; (void)y; (void)s; (void)color; (void)brightness; (void)font;
    assert(!"TRICK is outside this oracle");
}

#include "source_layout.inc"

/* An independent encoding specification, never consulting extracted font_ascii. */
static int expected_glyph(unsigned int byte)
{
    if (byte >= 'A' && byte <= 'Z') return (int)byte - 'A';
    if (byte >= 'a' && byte <= 'z') return (int)byte - 'a' + 34;
    if (byte >= '1' && byte <= '9') return (int)byte - '1' + 70;
    if (byte >= 128 && byte <= 168) return (int)byte - 128 + 86;
    switch (byte) {
    case '!': return 26; case '?': return 27; case '.': return 28;
    case ',': return 29; case ';': return 30; case ':': return 31;
    case '\'': return 32; case '"': return 33; case '#': return 60;
    case '$': return 61; case '%': return 62; case '*': return 63;
    case '(': return 64; case ')': return 65; case '{': return 66;
    case '}': return 67; case '[': return 68; case ']': return 69;
    case '0': return 79; case '/': return 80; case '|': return 81;
    case '\\': return 82; case '-': return 83; case '+': return 84;
    case '=': return 85; default: return -1;
    }
}

static void reset_metadata(void)
{
    for (unsigned int font = 0; font < FONT_COUNT; ++font)
        for (unsigned int glyph = 0; glyph < GLYPH_COUNT; ++glyph) {
            Sprite *item = &metadata[font][glyph];
            item->width = 5 + (glyph * 7 + font * 3) % 9;
            item->height = 7 + (glyph + font) % 6;
            item->exists = true;
            item->ink_x = 1 + glyph % 2;
            item->ink_y = glyph % 3;
            item->ink_width = item->width - item->ink_x - 1;
            item->ink_height = item->height - item->ink_y - 1;
        }
    /* Deliberately unequal body/descender extents inside an allocated cell. */
    metadata[TINY_FONT][expected_glyph('A')].ink_y = 0;
    metadata[TINY_FONT][expected_glyph('g')].ink_y = 3;
    metadata[TINY_FONT][expected_glyph('j')].ink_y = 4;
    metadata[TINY_FONT][expected_glyph('p')].ink_y = 2;
    metadata[TINY_FONT][expected_glyph('q')].ink_y = 3;
    metadata[TINY_FONT][expected_glyph('y')].ink_y = 4;
    for (const char *p = "gjpqy"; *p; ++p) {
        Sprite *item = &metadata[TINY_FONT][expected_glyph((unsigned char)*p)];
        item->ink_height = item->height - item->ink_y;
    }
}

static void expect_command(SDL_Surface *screen, int operation, int x, int y,
                           unsigned int font, unsigned int glyph,
                           unsigned int hue, int value, bool black)
{
    assert(expected_count < MAX_COMMANDS);
    expected[expected_count++] = (Command){screen, operation, x, y, font, glyph,
                                          (Uint8)hue, (Sint8)value, black};
}

/* Scalar glyph-position list: controls alter state; only accepted cells advance. */
static void expect_line(SDL_Surface *screen, int x, int y, const char *text,
                        unsigned int font, unsigned int color, int brightness,
                        bool dstring)
{
    bool emphasized = false;
    for (const unsigned char *p = (const unsigned char *)text; *p; ++p) {
        if (*p == '~') {
            emphasized = !emphasized;
            continue;
        }
        if (*p == ' ') {
            x += 6;
            continue;
        }
        const int glyph = expected_glyph(*p);
        if (glyph < 0 || (!dstring && !metadata[font][glyph].exists)) continue;
        if (dstring) {
            expect_command(screen, DARK, x + 2, y + 2, font, (unsigned int)glyph, 0, 0, false);
            expect_command(screen, HUE_VALUE, x, y, font, (unsigned int)glyph, 15,
                           emphasized ? -1 : -3, false);
        } else if (brightness < 0) {
            expect_command(screen, DARK, x, y, font, (unsigned int)glyph, 0, 0, true);
        } else {
            expect_command(screen, HUE_VALUE, x, y, font, (unsigned int)glyph, color,
                           brightness + (emphasized ? 4 : 0), false);
        }
        x += (int)metadata[font][glyph].width + 1;
    }
}

static void compare_stream(void)
{
    if (actual_count != expected_count) {
        fprintf(stderr, "stream %lu: %zu commands, expected %zu\n",
                stream_cases, actual_count, expected_count);
        abort();
    }
    for (size_t i = 0; i < actual_count; ++i) {
        const Command *a = &actual[i], *e = &expected[i];
        if (a->screen != e->screen || a->operation != e->operation ||
            a->x != e->x || a->y != e->y || a->font != e->font ||
            a->glyph != e->glyph || a->hue != e->hue ||
            a->value != e->value || a->black != e->black) {
            fprintf(stderr, "stream %lu command %zu mismatch\n", stream_cases, i);
            abort();
        }
    }
    ++stream_cases;
    compared_commands += actual_count;
}

static int check_width(const char *text, unsigned int font)
{
    int width = 0;
    for (const unsigned char *p = (const unsigned char *)text; *p; ++p) {
        const int glyph = expected_glyph(*p);
        if (*p == ' ') width += 6;
        else if (glyph >= 0) width += (int)metadata[font][glyph].width + 1;
    }
    assert(JE_textWidth(text, font) == width);
    ++width_cases;
    return width;
}

static void check_out(const char *text, int x, int y, unsigned int color, int brightness)
{
    SDL_Surface *screen = &surfaces[stream_cases % 2];
    actual_count = expected_count = 0;
    expect_line(screen, x, y, text, TINY_FONT, color, brightness, false);
    JE_outText(screen, x, y, text, color, brightness);
    compare_stream();
}

static void check_shade(const char *text, int x, int y, unsigned int color,
                        int brightness, unsigned int shade)
{
    SDL_Surface *screen = &surfaces[stream_cases % 2];
    actual_count = expected_count = 0;
    if (shade == FULL_SHADE) {
        /* These are whole-string passes, not four shadows beside each glyph. */
        static const int offsets[4][2] = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
        for (size_t pass = 0; pass < 4; ++pass)
            expect_line(screen, x + offsets[pass][0], y + offsets[pass][1],
                        text, TINY_FONT, 0, -1, false);
    } else if (shade == PART_SHADE) {
        expect_line(screen, x + 1, y + 1, text, TINY_FONT, 0, -1, false);
    }
    if (shade == FULL_SHADE || shade == PART_SHADE)
        expect_line(screen, x, y, text, TINY_FONT, color, brightness, false);
    JE_textShade(screen, x, y, text, color, brightness, shade);
    compare_stream();
}

static void check_dstring(const char *text, unsigned int font, int x, int y)
{
    SDL_Surface *screen = &surfaces[stream_cases % 2];
    actual_count = expected_count = 0;
    expect_line(screen, x, y, text, font, 15, -3, true);
    JE_dString(screen, x, y, text, font);
    compare_stream();
}

static void check_string(const char *text)
{
    ++strings;
    for (unsigned int font = 0; font < FONT_COUNT; ++font) {
        check_width(text, font);
        check_dstring(text, font, 311, 193);
    }
    check_out(text, 7, 11, 0, 0);
    check_out(text, 268, 118, 12, 4);
    check_out(text, -13, -7, 15, -1);
    check_out(text, 319, 199, 3, -9);
    check_shade(text, 2, 3, 5, 2, PART_SHADE);
    check_shade(text, 317, 197, 12, 4, FULL_SHADE);
    check_shade(text, -2, -3, 8, -1, FULL_SHADE);
    check_shade(text, 0, 0, 12, 4, NO_SHADE);
}

static void check_mapping_and_strings(void)
{
    bool covered[GLYPH_COUNT] = {false};
    for (unsigned int byte = 0; byte < 256; ++byte) {
        const int glyph = expected_glyph(byte);
        assert(font_ascii[byte] == glyph);
        if (glyph >= 0) covered[glyph] = true;
        ++map_checks;
    }
    for (unsigned int glyph = 0; glyph < GLYPH_COUNT; ++glyph) assert(covered[glyph]);
    for (unsigned int byte = 1; byte < 256; ++byte) {
        const char text[] = {(char)byte, 'A', '~', 'g', '~', 'j', '\0'};
        check_string(text);
    }
    /* Zero is checked as a terminator, never passed off as a drawable byte. */
    static const char embedded_zero[] = {'A', '\0', 'B', '~', 'g', '\0'};
    static const char leading_zero[] = {'\0', 'B', '~', 'g', '\0'};
    static const char *fixtures[] = {
        "", " ", "   ", "~", "~~", "~~~", "A~g~j~~p~q~y",
        "AaZz 019 !?.,:;'\"#$%*(){}[]/|\\-+=", "gjpqyAgjpqy",
        "A&<@>^_`\177\251\377g", " A ~ g ~ j ", "~A B~ C~D~",
        embedded_zero, leading_zero
    };
    for (size_t i = 0; i < sizeof(fixtures) / sizeof(fixtures[0]); ++i) check_string(fixtures[i]);
    char every_nonzero[256];
    for (unsigned int byte = 1; byte < 256; ++byte) every_nonzero[byte - 1] = (char)byte;
    every_nonzero[255] = '\0';
    check_string(every_nonzero);

    char long_text[1025];
    for (size_t i = 0; i < sizeof(long_text) - 1; ++i) long_text[i] = "Agj ~pqy"[i % 8];
    long_text[sizeof(long_text) - 1] = '\0';
    check_string(long_text);
    check_out(long_text, 311, 199, 12, 4);
    assert(actual_count > 320 && actual[actual_count - 1].x > 320);
    for (size_t i = 0; i < actual_count; ++i) assert(actual[i].y == 199);
}

static void check_missing_glyphs(void)
{
    for (unsigned int byte = 1; byte < 256; ++byte) {
        const int glyph = expected_glyph(byte);
        if (glyph < 0) continue;
        reset_metadata();
        metadata[TINY_FONT][glyph].exists = false;
        const char text[] = {'A', (char)byte, '~', (char)byte, 'g', '\0'};
        check_width(text, TINY_FONT);
        check_out(text, 17, 23, 12, 4);
        check_out(text, 17, 23, 12, -1);
        check_shade(text, 17, 23, 12, 4, FULL_SHADE);
        ++missing_cases;
    }
    reset_metadata();
    metadata[TINY_FONT][expected_glyph('A')].exists = false;
    assert(check_width("Ag", TINY_FONT) == (int)(metadata[TINY_FONT][0].width +
                                               metadata[TINY_FONT][40].width + 2));
    check_out("Ag", 17, 23, 12, 4);
    assert(actual_count == 1 && actual[0].glyph == 40 && actual[0].x == 17);
    ++missing_cases;
    for (unsigned int glyph = 0; glyph < GLYPH_COUNT; ++glyph) metadata[TINY_FONT][glyph].exists = false;
    assert(check_width("A ~gjpqy", TINY_FONT) > 6);
    check_out("A ~gjpqy", 17, 23, 12, 4);
    assert(actual_count == 0);
    ++missing_cases;
    reset_metadata();
}

static void check_allocated_metrics(void)
{
    const char *text = "AgjpqyAa .,";
    check_out(text, 31, 41, 12, 4);
    Command before[32];
    const size_t count = actual_count;
    assert(count <= sizeof(before) / sizeof(before[0]));
    memcpy(before, actual, count * sizeof(*before));
    const int width = check_width(text, TINY_FONT);
    /* Moving/shrinking every synthetic ink rectangle cannot change advances,
     * baseline origins, or alignment; only allocated sprite width matters. */
    for (unsigned int glyph = 0; glyph < GLYPH_COUNT; ++glyph) {
        Sprite *item = &metadata[TINY_FONT][glyph];
        item->ink_x = item->width - 1;
        item->ink_y = item->height - 1;
        item->ink_width = item->ink_height = 1;
    }
    check_out(text, 31, 41, 12, 4);
    assert(actual_count == count && check_width(text, TINY_FONT) == width);
    for (size_t i = 0; i < count; ++i) {
        assert(actual[i].x == before[i].x && actual[i].y == before[i].y);
        ++metric_cases;
    }
    reset_metadata();
    const unsigned int a_width = metadata[TINY_FONT][0].width;
    check_out("AA", 31, 41, 12, 4);
    assert(actual_count == 2 && actual[1].x - actual[0].x == (int)a_width + 1);
    metadata[TINY_FONT][0].width += 7;
    check_out("AA", 31, 41, 12, 4);
    assert(actual[1].x - actual[0].x == (int)a_width + 8);
    metric_cases += 2;
    reset_metadata();
}

static Uint8 original_unsafe_pixel(Uint8 source, Uint8 hue, Sint8 value)
{
    Uint8 result = 0, *pixels = &result;
    const Uint8 *data = &source;
#include "source_pixel.inc"
    return result;
}

static void check_unsafe_pixel(void)
{
    for (unsigned int hue = 0; hue < 16; ++hue)
        for (unsigned int low = 0; low < 16; ++low)
            for (int value = -128; value <= 127; ++value) {
                const unsigned int wrapped = (unsigned int)((int)low + value + 256) % 256;
                const Uint8 expected_pixel = (Uint8)((hue * 16) | wrapped);
                assert(original_unsafe_pixel((Uint8)(0xa0 + low), (Uint8)hue,
                                             (Sint8)value) == expected_pixel);
                ++pixel_cases;
            }
    assert(original_unsafe_pixel(15, 12, 4) == 0xd3); /* low overflow enters hue */
    assert(original_unsafe_pixel(0, 15, -3) == 0xfd); /* negative wraps, no clamp */
}

int main(void)
{
    assert(FONT_SHAPES == 0 && SMALL_FONT_SHAPES == 1 && TINY_FONT == 2);
    assert(PART_SHADE == 0 && FULL_SHADE == 1 && DARKEN == 2 && TRICK == 3 && NO_SHADE == 255);
    reset_metadata();
    check_mapping_and_strings();
    check_missing_glyphs();
    check_allocated_metrics();
    check_unsafe_pixel();
    printf("PASS original layout: %lu byte mappings; %lu string fixtures; "
           "%lu width cases; %lu ordered streams; %lu compared blit commands; "
           "%lu missing-sprite cases; %lu metric checks; %lu unsafe pixel cases\n",
           map_checks, strings, width_cases, stream_cases, compared_commands,
           missing_cases, metric_cases, pixel_cases);
    puts("PASS zero termination, space +6, unmapped +0, emphasis +4/+2, allocated-width +1, "
         "full-string L/R/U/D shadow order, negative-brightness black, dString dim shadow, "
         "original screen/coordinate/color arguments, and no layout clipping/reflow");
    return 0;
}
