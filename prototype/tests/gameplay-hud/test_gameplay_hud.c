/* All inputs are generated here. No artwork, screenshots or game data needed. */
#include "gameplay_hud.h"
#include "allocation_probe.h"
#include "audit_fixtures.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define WIDTH 320
#define HEIGHT 200
#define PIXELS 64000
#define RGBA_BYTES 4096000
#define PAYLOAD_BYTES (PIXELS + RGBA_BYTES)
#define FILE_BYTES (64 + PAYLOAD_BYTES)
#define COUNT(array) (sizeof(array) / sizeof((array)[0]))
#define CHECK(test) do { if (!(test)) { \
 fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #test); exit(1); } } while (0)

static uint8_t header[64], mask[PIXELS], rgba[RGBA_BYTES];
static uint8_t original[PIXELS], padded[HEIGHT * 337];
static char filepath[2048];
static size_t allocation_calls, max_request, live_bytes, peak_live;
static void *live_pointer;
static int reject_allocation;
static unsigned cases;
static uint8_t mode_indices[2][80], mode_opaque[2][80];

void *gameplay_hud_test_malloc(size_t size)
{
	void *ptr;
	++allocation_calls;
	if (size > max_request) max_request = size;
	CHECK(size == PAYLOAD_BYTES);
	CHECK(live_pointer == NULL);
	if (reject_allocation) return NULL;
	ptr = malloc(size);
	CHECK(ptr != NULL);
	live_pointer = ptr;
	live_bytes = size;
	if (live_bytes > peak_live) peak_live = live_bytes;
	return ptr;
}

void gameplay_hud_test_free(void *ptr)
{
	if (ptr)
	{
		CHECK(ptr == live_pointer);
		live_pointer = NULL;
		live_bytes = 0;
	}
	free(ptr);
}

static uint64_t reference_fnv(const uint8_t *p, size_t n)
{
	uint64_t h = UINT64_C(0xcbf29ce484222325);
	while (n--) { h ^= *p++; h *= UINT64_C(0x100000001b3); }
	return h;
}

static void put32(unsigned offset, uint32_t value)
{
	for (unsigned i = 0; i < 4; ++i) header[offset + i] = (uint8_t)(value >> (8 * i));
}

static void put64(unsigned offset, uint64_t value)
{
	for (unsigned i = 0; i < 8; ++i) header[offset + i] = (uint8_t)(value >> (8 * i));
}

static size_t rgba_offset(int x, int y, int sx, int sy)
{
	return (size_t)((y * 4 + sy) * 1280 + x * 4 + sx) * 4;
}

static void mark_pixel(int x, int y, uint8_t value)
{
	mask[y * WIDTH + x] = value;
	for (int sy = 0; sy < 4; ++sy)
		for (int sx = 0; sx < 4; ++sx)
			rgba[rgba_offset(x, y, sx, sy) + 3] = value;
}

static void hashes(void)
{
	put64(36, reference_fnv(original, sizeof(original)));
	put64(44, reference_fnv(mask, sizeof(mask)));
	put64(52, reference_fnv(rgba, sizeof(rgba)));
}

static void fresh_fixture(void)
{
	memset(header, 0, sizeof(header));
	memcpy(header, "HUD1", 4);
	put32(4, 1); put32(8, WIDTH); put32(12, HEIGHT); put32(16, 4);
	put32(28, PIXELS); put32(32, RGBA_BYTES);
	memset(mask, 0, sizeof(mask));
	for (size_t i = 0; i < RGBA_BYTES; i += 4)
	{
		rgba[i] = (uint8_t)(i / 4);
		rgba[i + 1] = (uint8_t)(i / 5120);
		rgba[i + 2] = (uint8_t)(31 + i / 20);
		rgba[i + 3] = 0;
	}
	for (size_t i = 0; i < PIXELS; ++i) original[i] = (uint8_t)(1 + i % 251);
	original[0] = 0; /* Transparent original pixels outside ownership are allowed. */
	mark_pixel(264, 0, 255);
	mark_pixel(0, 184, 255);
	mark_pixel(319, 199, 255);
	hashes();
}

/* Independent coordinate fixtures are hash checked by the Python runner. */
static int approved_pixel(int x, int y)
{
	for (size_t i = 0; i < COUNT(approved_points); ++i)
		if (approved_points[i][0] == x && approved_points[i][1] == y) return 1;
	return 0;
}

static void clear_ownership(void)
{
	memset(mask, 0, sizeof(mask));
	for (size_t i = 3; i < sizeof(rgba); i += 4) rgba[i] = 0;
}

static int glyph_moat(int x, int y)
{
	static const int labels[][3] = {{285, 138, 6}, {296, 138, 5}};
	for (size_t label = 0; label < COUNT(labels); ++label)
		for (int letter = 0; letter < labels[label][2]; ++letter)
		{
			int dx = x - labels[label][0];
			int dy = y - labels[label][1] - 6 * letter;
			if (dx >= -1 && dx <= 5 && dy >= -1 && dy <= 5 &&
			    (dx == -1 || dx == 5 || dy == -1 || dy == 5)) return 1;
		}
	return 0;
}

static void expanded_fixture(void)
{
	fresh_fixture();
	for (int y = 0; y < HEIGHT; ++y)
		for (int x = 0; x < WIDTH; ++x)
			if (glyph_moat(x, y)) original[y * WIDTH + x] = 0;
	for (int local = 0; local < 80; ++local)
	{
		/* Synthetic indices, deliberately shared by both mode positions. */
		uint8_t index = (uint8_t)(100 + local);
		original[(44 + local / 10) * WIDTH + 285 + local % 10] = index;
		original[(44 + local / 10) * WIDTH + 302 + local % 10] = index;
		mode_indices[0][local] = mode_indices[1][local] = index;
		mode_opaque[0][local] = mode_opaque[1][local] = 255;
	}
	for (size_t i = 0; i < COUNT(approved_points); ++i)
		mark_pixel(approved_points[i][0], approved_points[i][1], 255);
	hashes();
}

static bool verify_test_modes(void)
{
	return gameplay_hud_verify_modes((const uint8_t (*)[80])mode_indices,
	                                 (const uint8_t (*)[80])mode_opaque);
}

static void write_fixture(size_t bytes, int extra)
{
	FILE *file = fopen(filepath, "wb");
	size_t n = bytes < sizeof(header) ? bytes : sizeof(header);
	CHECK(file != NULL);
	CHECK(fwrite(header, 1, n, file) == n);
	bytes -= n;
	n = bytes < sizeof(mask) ? bytes : sizeof(mask);
	CHECK(fwrite(mask, 1, n, file) == n);
	bytes -= n;
	n = bytes < sizeof(rgba) ? bytes : sizeof(rgba);
	CHECK(fwrite(rgba, 1, n, file) == n);
	bytes -= n;
	CHECK(bytes == 0);
	if (extra) CHECK(fputc(0x77, file) == 0x77);
	CHECK(fclose(file) == 0);
}

static void expect_rejected(const char *directory)
{
	size_t calls;
	gameplay_hud_shutdown();
	CHECK(!gameplay_hud_load(directory));
	CHECK(!gameplay_hud_ready());
	CHECK(!gameplay_hud_has_expansion());
	CHECK(gameplay_hud_verify_modes(NULL, NULL));
	CHECK(!gameplay_hud_capture(original, WIDTH));
	CHECK(gameplay_hud_sample(264, 0, 0, 0, 4, original[264]) == NULL);
	CHECK(live_bytes == 0);
	calls = allocation_calls;
	CHECK(!gameplay_hud_load(directory));
	CHECK(allocation_calls == calls);
	++cases;
}

static void expect_ready(const char *directory)
{
	gameplay_hud_shutdown();
	CHECK(gameplay_hud_load(directory));
	CHECK(!gameplay_hud_ready());
	CHECK(gameplay_hud_capture(original, WIDTH));
	CHECK(gameplay_hud_ready());
	CHECK(live_bytes == PAYLOAD_BYTES);
	++cases;
}

static void test_header(const char *directory)
{
	static const unsigned offsets[] = {4, 8, 12, 16, 20, 24, 28, 32, 60};
	static const uint32_t invalid[] = {2, 321, 201, 8, UINT32_MAX, 1,
	                                  UINT32_MAX, UINT32_MAX, 1};
	fresh_fixture();
	header[0] = 'X'; write_fixture(FILE_BYTES, 0); expect_rejected(directory);
	for (size_t i = 0; i < sizeof(offsets) / sizeof(offsets[0]); ++i)
	{
		fresh_fixture();
		put32(offsets[i], invalid[i]);
		write_fixture(FILE_BYTES, 0);
		expect_rejected(directory);
	}
	/* Wrong endian numeric encoding is never host-native-decoded. */
	fresh_fixture(); put32(8, UINT32_C(0x40010000));
	write_fixture(FILE_BYTES, 0); expect_rejected(directory);
}

static void test_lengths_and_hashes(const char *directory)
{
	static const size_t sizes[] = {0, 4, 63, 64, 64063, FILE_BYTES - 1};
	fresh_fixture();
	for (size_t i = 0; i < sizeof(sizes) / sizeof(sizes[0]); ++i)
	{
		size_t calls = allocation_calls;
		write_fixture(sizes[i], 0); expect_rejected(directory);
		CHECK(allocation_calls == calls);
	}
	write_fixture(FILE_BYTES, 1); expect_rejected(directory);
	for (int target = 0; target < 4; ++target)
	{
		fresh_fixture();
		if (target == 0) header[44] ^= 1;
		if (target == 1) header[52] ^= 1;
		if (target == 2) mask[264] = 0;
		if (target == 3) rgba[0] ^= 1;
		write_fixture(FILE_BYTES, 0); expect_rejected(directory);
	}
}

static const int protected_rectangles[][4] = {
	{0, 0, 264, 184}, {268, 10, 279, 108}, {284, 4, 312, 21},
	{284, 25, 312, 41}, {285, 44, 295, 52}, {302, 44, 312, 52},
	{284, 53, 313, 60}, {283, 63, 313, 99}, {267, 115, 320, 128},
	{270, 134, 279, 195}, {307, 134, 316, 195}, {284, 136, 292, 177},
	{294, 136, 302, 177}, {269, 3, 277, 8}, {16, 189, 264, 200}
};

static int protected_pixel(int x, int y)
{
	for (size_t i = 0; i < sizeof(protected_rectangles) / sizeof(protected_rectangles[0]); ++i)
	{
		const int *r = protected_rectangles[i];
		if (x >= r[0] && x < r[2] && y >= r[1] && y < r[3]) return 1;
	}
	return 0;
}

static void test_mask_and_alpha(const char *directory)
{
	fresh_fixture(); mark_pixel(264, 0, 1); hashes();
	write_fixture(FILE_BYTES, 0); expect_rejected(directory);
	fresh_fixture(); memset(mask, 0, sizeof(mask));
	for (size_t i = 3; i < sizeof(rgba); i += 4) rgba[i] = 0;
	hashes(); write_fixture(FILE_BYTES, 0); expect_rejected(directory);

	/* Check all four corners of the playfield and each of the fourteen holes. */
	for (size_t i = 0; i < sizeof(protected_rectangles) / sizeof(protected_rectangles[0]); ++i)
	{
		const int *r = protected_rectangles[i];
		for (int corner = 0; corner < 4; ++corner)
		{
			int x = (corner & 1) ? r[2] - 1 : r[0];
			int y = (corner & 2) ? r[3] - 1 : r[1];
			if (approved_pixel(x, y)) continue;
			fresh_fixture(); mark_pixel(x, y, 255); hashes();
			write_fixture(FILE_BYTES, 0); expect_rejected(directory);
		}
	}
	fresh_fixture();
	memset(mask, 0, sizeof(mask));
	for (size_t i = 3; i < sizeof(rgba); i += 4) rgba[i] = 0;
	unsigned owned = 0;
	for (int y = 0; y < HEIGHT; ++y)
		for (int x = 0; x < WIDTH; ++x)
			if (!protected_pixel(x, y))
			{
				mark_pixel(x, y, 255); ++owned;
			}
	CHECK(owned == 6768);
	hashes(); write_fixture(FILE_BYTES, 0); expect_rejected(directory); /* Former ceiling. */

	/* Every subpixel must match; both unwanted and missing alpha fail closed. */
	for (int subpixel = 0; subpixel < 16; ++subpixel)
	{
		fresh_fixture(); rgba[rgba_offset(264, 0, subpixel % 4, subpixel / 4) + 3] = 0;
		hashes(); write_fixture(FILE_BYTES, 0); expect_rejected(directory);
	}
	fresh_fixture(); rgba[3] = 255; hashes();
	write_fixture(FILE_BYTES, 0); expect_rejected(directory);
	fresh_fixture(); rgba[rgba_offset(264, 0, 0, 0) + 3] = 254; hashes();
	write_fixture(FILE_BYTES, 0); expect_rejected(directory);
	fresh_fixture(); /* Arbitrary hidden RGB, and opaque black, are both valid. */
	memset(rgba + rgba_offset(264, 0, 0, 0), 0, 3);
	hashes(); write_fixture(FILE_BYTES, 0); expect_ready(directory);
}

static void test_expansion_geometry(const char *directory)
{
	unsigned owned = 0, added = 0;
	expanded_fixture(); write_fixture(FILE_BYTES, 0); expect_ready(directory);
	CHECK(gameplay_hud_has_expansion());
	CHECK(COUNT(approved_points) == 310 && COUNT(rejected_points) == 261);
	for (size_t i = 0; i < COUNT(approved_points); ++i)
	{
		int x = approved_points[i][0], y = approved_points[i][1];
		CHECK(protected_pixel(x, y)); /* Every addition lies outside old geometry. */
		CHECK(!glyph_moat(x, y));
		CHECK(gameplay_hud_sample(x, y, 0, 0, 4, original[y * WIDTH + x]));
	}
	/* Reject each of the 261 individually, rather than one mixed mask. */
	for (size_t i = 0; i < COUNT(rejected_points); ++i)
	{
		int x = rejected_points[i][0], y = rejected_points[i][1];
		CHECK(protected_pixel(x, y) && !approved_pixel(x, y));
		fresh_fixture(); mark_pixel(x, y, 255); hashes();
		write_fixture(FILE_BYTES, 0); expect_rejected(directory);
	}
	/* Reject a point just outside every approved row run, unless base geometry
	 * or another approved span owns it. This catches broad rectangle widening. */
	for (size_t i = 0; i < COUNT(approved_points); ++i)
		for (int direction = -1; direction <= 1; direction += 2)
		{
			int x = approved_points[i][0] + direction, y = approved_points[i][1];
			if (x < 0 || x >= WIDTH || !protected_pixel(x, y) || approved_pixel(x, y)) continue;
			fresh_fixture(); mark_pixel(x, y, 255); hashes();
			write_fixture(FILE_BYTES, 0); expect_rejected(directory);
		}
	/* The unchanged base geometry has 6768 possible points. Finite expansion
	 * adds 310 possible coordinates, but TOTAL ownership is capped at 6667. */
	expanded_fixture(); clear_ownership();
	for (size_t i = 0; i < COUNT(approved_points); ++i)
	{
		mark_pixel(approved_points[i][0], approved_points[i][1], 255); ++owned;
	}
	for (int y = 0; y < HEIGHT; ++y)
		for (int x = 0; x < WIDTH; ++x)
			if (!protected_pixel(x, y) && owned < 6667)
			{
				CHECK(!mask[y * WIDTH + x]); mark_pixel(x, y, 255); ++owned;
			}
	CHECK(owned == 6667);
	hashes(); write_fixture(FILE_BYTES, 0); expect_ready(directory);
	CHECK(gameplay_hud_has_expansion());
	for (int y = 0; y < HEIGHT && !added; ++y)
		for (int x = 0; x < WIDTH && !added; ++x)
			if (!protected_pixel(x, y) && !mask[y * WIDTH + x])
			{
				mark_pixel(x, y, 255); added = 1;
			}
	CHECK(added); hashes(); write_fixture(FILE_BYTES, 0); expect_rejected(directory);
}

static void test_expansion_source(const char *directory)
{
	unsigned checked = 0;
	expanded_fixture(); write_fixture(FILE_BYTES, 0); expect_ready(directory);
	size_t calls = allocation_calls;
	CHECK(gameplay_hud_has_expansion());
	memset(padded, 0xab, sizeof(padded));
	for (int y = 0; y < HEIGHT; ++y) memcpy(padded + y * 337, original + y * WIDTH, WIDTH);
	CHECK(gameplay_hud_capture(padded, 337)); CHECK(gameplay_hud_ready());
	CHECK(allocation_calls == calls);
	/* Every unique one-pixel moat location must be zero, even if the asset's
	 * full-source checksum is updated to match a changed source package. */
	for (int y = 0; y < HEIGHT; ++y)
		for (int x = 0; x < WIDTH; ++x)
			if (glyph_moat(x, y))
			{
				original[y * WIDTH + x] = 1;
				CHECK(!gameplay_hud_capture(original, WIDTH)); CHECK(!gameplay_hud_ready());
				hashes(); write_fixture(FILE_BYTES, 0);
				gameplay_hud_shutdown(); CHECK(gameplay_hud_load(directory));
				CHECK(gameplay_hud_has_expansion());
				CHECK(!gameplay_hud_capture(original, WIDTH)); CHECK(!gameplay_hud_ready());
				original[y * WIDTH + x] = 0; ++checked; ++cases;
			}
	CHECK(checked == 201);
	expanded_fixture(); original[0] ^= 1; /* Unowned pixels remain source-bound. */
	write_fixture(FILE_BYTES, 0); gameplay_hud_shutdown(); CHECK(gameplay_hud_load(directory));
	CHECK(!gameplay_hud_capture(original, WIDTH)); CHECK(!gameplay_hud_ready()); ++cases;
	/* One approved pixel still requires every moat, including the other label. */
	expanded_fixture(); clear_ownership(); mark_pixel(268, 10, 255);
	original[137 * WIDTH + 301] = 1; hashes(); write_fixture(FILE_BYTES, 0);
	gameplay_hud_shutdown(); CHECK(gameplay_hud_load(directory));
	CHECK(gameplay_hud_has_expansion()); CHECK(!gameplay_hud_capture(original, WIDTH)); ++cases;
	/* Base assets remain compatible with arbitrary nonzero glyph moats. */
	fresh_fixture(); write_fixture(FILE_BYTES, 0); expect_ready(directory);
	CHECK(!gameplay_hud_has_expansion()); CHECK(gameplay_hud_verify_modes(NULL, NULL));
}

static void test_expansion_modes(const char *directory)
{
	expanded_fixture(); write_fixture(FILE_BYTES, 0);
	gameplay_hud_shutdown(); CHECK(gameplay_hud_load(directory));
	CHECK(gameplay_hud_has_expansion()); CHECK(!verify_test_modes());
	CHECK(gameplay_hud_capture(original, WIDTH)); CHECK(verify_test_modes());
	CHECK(!gameplay_hud_verify_modes(NULL, NULL));
	size_t calls = allocation_calls;
	unsigned checked = 0;
	for (int local = 0; local < 80; ++local)
	{
		int left = (44 + local / 10) * WIDTH + 285 + local % 10;
		int right = left + 17;
		bool owned = mask[left] || mask[right];
		for (int state = 0; state < 2; ++state)
		{
			mode_indices[state][local] ^= 1;
			CHECK(verify_test_modes() == !owned);
			mode_indices[state][local] ^= 1;
			mode_opaque[state][local] = 0;
			CHECK(verify_test_modes() == !owned);
			mode_opaque[state][local] = 254;
			CHECK(verify_test_modes() == !owned);
			mode_opaque[state][local] = 255;
		}
		/* Equal A/B indices still fail when they do not match captured PIC3. */
		mode_indices[0][local] ^= 1; mode_indices[1][local] ^= 1;
		CHECK(verify_test_modes() == !owned);
		mode_indices[0][local] ^= 1; mode_indices[1][local] ^= 1;
		if (owned) ++checked;
		CHECK(verify_test_modes());
	}
	CHECK(checked == 15); CHECK(allocation_calls == calls); ++cases;
	gameplay_hud_forget_source(); CHECK(gameplay_hud_has_expansion());
	CHECK(!verify_test_modes()); CHECK(gameplay_hud_capture(original, WIDTH));
	CHECK(verify_test_modes());
	/* A sparse mode mask must check only the one actually owned local point. */
	expanded_fixture(); clear_ownership(); mark_pixel(285, 44, 255); hashes();
	write_fixture(FILE_BYTES, 0); expect_ready(directory);
	mode_indices[1][1] ^= 1; CHECK(verify_test_modes());
	mode_indices[1][0] ^= 1; CHECK(!verify_test_modes());
	/* Bind each position independently, including when only the right owns it. */
	expanded_fixture(); clear_ownership(); mark_pixel(302, 44, 255);
	original[44 * WIDTH + 302] ^= 1; hashes();
	write_fixture(FILE_BYTES, 0); expect_ready(directory); CHECK(!verify_test_modes());
	/* Unrelated rails do not require any mode source arrays. */
	expanded_fixture(); clear_ownership(); mark_pixel(268, 10, 255); hashes();
	write_fixture(FILE_BYTES, 0); expect_ready(directory);
	CHECK(gameplay_hud_has_expansion()); CHECK(gameplay_hud_verify_modes(NULL, NULL));
	gameplay_hud_shutdown(); CHECK(!gameplay_hud_has_expansion());
	CHECK(gameplay_hud_verify_modes(NULL, NULL));
}

static void test_capture(const char *directory)
{
	fresh_fixture(); write_fixture(FILE_BYTES, 0); expect_ready(directory);
	size_t calls = allocation_calls;
	CHECK(!gameplay_hud_capture(NULL, WIDTH)); CHECK(!gameplay_hud_ready());
	CHECK(gameplay_hud_capture(original, WIDTH));
	CHECK(!gameplay_hud_capture(original, 319)); CHECK(!gameplay_hud_ready());
	CHECK(!gameplay_hud_capture(original, -1));
	CHECK(!gameplay_hud_capture(original, INT_MIN));
	CHECK(!gameplay_hud_capture(original, 0));
	CHECK(gameplay_hud_capture(original, WIDTH));
	original[0] ^= 1; /* Hash includes all unowned source pixels as well. */
	CHECK(!gameplay_hud_capture(original, WIDTH)); CHECK(!gameplay_hud_ready());
	original[0] ^= 1;
	memset(padded, 0xab, sizeof(padded));
	for (int y = 0; y < HEIGHT; ++y) memcpy(padded + y * 337, original + y * WIDTH, WIDTH);
	CHECK(gameplay_hud_capture(padded, 337)); CHECK(gameplay_hud_ready());
	CHECK(allocation_calls == calls);
	++cases;

	fresh_fixture(); header[36] ^= 1; write_fixture(FILE_BYTES, 0);
	gameplay_hud_shutdown(); CHECK(gameplay_hud_load(directory));
	CHECK(!gameplay_hud_capture(original, WIDTH)); CHECK(!gameplay_hud_ready());
	++cases;
	fresh_fixture(); original[264] = 0; hashes(); write_fixture(FILE_BYTES, 0);
	gameplay_hud_shutdown(); CHECK(gameplay_hud_load(directory));
	CHECK(!gameplay_hud_capture(original, WIDTH)); CHECK(!gameplay_hud_ready());
	++cases;
}

static void test_samples_and_lifecycle(const char *directory)
{
	expanded_fixture(); write_fixture(FILE_BYTES, 0); expect_ready(directory);
	size_t calls = allocation_calls;
	for (int density = 4; density <= 8; density += 4)
		for (int y = 0; y < HEIGHT; ++y)
			for (int x = 0; x < WIDTH; ++x)
				for (int sy = 0; sy < density; ++sy)
					for (int sx = 0; sx < density; ++sx)
					{
						const uint8_t *p = gameplay_hud_sample(x, y, sx, sy, density, original[y * WIDTH + x]);
						if (mask[y * WIDTH + x])
							CHECK(p && !memcmp(p, rgba + rgba_offset(x, y, sx / (density / 4), sy / (density / 4)), 4));
						else CHECK(p == NULL);
					}
	CHECK(gameplay_hud_sample(264, 0, 0, 0, 4, (uint8_t)(original[264] ^ 1)) == NULL);
	CHECK(gameplay_hud_sample(264, 0, 0, 0, 4, 0) == NULL);
	CHECK(gameplay_hud_sample(264, 0, 0, 0, 4, original[264]) != NULL);
	/* Captured memory is independent of the caller's subsequently mutated buffer. */
	original[264] ^= 1;
	CHECK(gameplay_hud_sample(264, 0, 0, 0, 4, original[264]) == NULL);
	CHECK(gameplay_hud_sample(264, 0, 0, 0, 4, (uint8_t)(original[264] ^ 1)) != NULL);
	original[264] ^= 1;
	static const int invalid[][5] = {
		{-1, 0, 0, 0, 4}, {320, 0, 0, 0, 4}, {264, -1, 0, 0, 4}, {264, 200, 0, 0, 4},
		{264, 0, -1, 0, 4}, {264, 0, 4, 0, 4}, {264, 0, 0, -1, 4}, {264, 0, 0, 4, 4},
		{264, 0, 8, 0, 8}, {264, 0, 0, 8, 8}, {264, 0, 0, 0, 0}, {264, 0, 0, 0, 1},
		{264, 0, 0, 0, 2}, {264, 0, 0, 0, 3}, {264, 0, 0, 0, 5}, {264, 0, 0, 0, 16},
		{INT_MAX, INT_MIN, INT_MAX, INT_MIN, INT_MAX}
	};
	for (size_t i = 0; i < sizeof(invalid) / sizeof(invalid[0]); ++i)
		CHECK(gameplay_hud_sample(invalid[i][0], invalid[i][1], invalid[i][2], invalid[i][3], invalid[i][4], original[264]) == NULL);
	CHECK(allocation_calls == calls);
	/* Subsequent calls cannot switch packs or cause another allocation or read. */
	CHECK(remove(filepath) == 0);
	CHECK(gameplay_hud_load(NULL)); CHECK(gameplay_hud_ready());
	CHECK(gameplay_hud_load("/nonexistent-selected-pack"));
	CHECK(allocation_calls == calls);
	gameplay_hud_forget_source(); CHECK(!gameplay_hud_ready());
	CHECK(gameplay_hud_sample(264, 0, 0, 0, 4, original[264]) == NULL);
	CHECK(gameplay_hud_load(directory)); CHECK(!gameplay_hud_ready());
	CHECK(gameplay_hud_capture(original, WIDTH)); CHECK(gameplay_hud_ready());
	gameplay_hud_shutdown(); CHECK(!gameplay_hud_ready()); CHECK(live_bytes == 0);
	CHECK(!gameplay_hud_capture(original, WIDTH));
	CHECK(gameplay_hud_sample(264, 0, 0, 0, 4, original[264]) == NULL);
	gameplay_hud_shutdown();
	++cases;
}

int main(int argc, char **argv)
{
	CHECK(argc == 2);
	CHECK(snprintf(filepath, sizeof(filepath), "%s/gameplay-hud-v1.hda", argv[1]) > 0);
	CHECK(gameplay_hud_fnv64(NULL, 0) == UINT64_C(0xcbf29ce484222325));
	CHECK(gameplay_hud_fnv64((const uint8_t *)"a", 1) == UINT64_C(0xaf63dc4c8601ec8c));
	CHECK(gameplay_hud_fnv64((const uint8_t *)"foobar", 6) == UINT64_C(0x85944171f73967e8));
	CHECK(!gameplay_hud_ready());
	CHECK(!gameplay_hud_capture(NULL, WIDTH));
	CHECK(gameplay_hud_sample(264, 0, 0, 0, 4, 1) == NULL);
	expect_rejected(NULL); expect_rejected(""); expect_rejected(argv[1]);
	char longpath[2048]; memset(longpath, 'a', sizeof(longpath)); longpath[sizeof(longpath) - 1] = '\0';
	expect_rejected(longpath);
	CHECK(allocation_calls == 0);
	/* An initial missing-asset attempt remains immutable after the file appears. */
	expect_rejected(argv[1]); fresh_fixture(); write_fixture(FILE_BYTES, 0);
	CHECK(!gameplay_hud_load(argv[1])); CHECK(allocation_calls == 0);
	gameplay_hud_shutdown(); reject_allocation = 1; expect_rejected(argv[1]); reject_allocation = 0;
	CHECK(!gameplay_hud_load(argv[1])); /* Allocation failure is also immutable. */
	expect_ready(argv[1]);
	test_header(argv[1]);
	test_lengths_and_hashes(argv[1]);
	test_mask_and_alpha(argv[1]);
	test_capture(argv[1]);
	test_expansion_geometry(argv[1]);
	test_expansion_source(argv[1]);
	test_expansion_modes(argv[1]);
	test_samples_and_lifecycle(argv[1]);
	CHECK(live_pointer == NULL); CHECK(peak_live == PAYLOAD_BYTES); CHECK(max_request == PAYLOAD_BYTES);
	printf("PASS: %u synthetic cases; exact 310 additions / 261 rejections; 5,120,000 full-frame samples; peak loader heap %zu bytes; no game-data or artwork inputs\n", cases, peak_live);
	return 0;
}
