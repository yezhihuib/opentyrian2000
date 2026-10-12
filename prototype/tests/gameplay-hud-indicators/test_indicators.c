/* Entirely generated fixtures. No original indices, art, RGB or captures. */
#include "gameplay_hud_indicators.h"

#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define WIDTH 320
#define HEIGHT 200
#define TOP_BYTES 1344
#define MODE_BYTES 13824
#define PAYLOAD_BYTES (TOP_BYTES + 2 * MODE_BYTES)
#define FILE_BYTES (80 + PAYLOAD_BYTES)
#define COUNT(a) (sizeof(a) / sizeof((a)[0]))
#define CHECK(t) do { if (!(t)) { \
	fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #t); exit(1); } } while (0)

static uint8_t header[80], artwork[PAYLOAD_BYTES], source[WIDTH * HEIGHT];
static uint8_t screen[WIDTH * HEIGHT], padded[337 * HEIGHT];
static uint8_t sprites[2][80], opaque[2][80], mode_expected[2][216];
static uint32_t palette[256];
static char filepath[2048];
static const char *directory;
static size_t allocations, frees, opens, reads, closes, stats;
static void *live_pointer;
static int live_descriptor = -1, reject_allocation, reject_stat, reject_close;
static int fail_read_number, short_read_number, override_size = -1;
static unsigned fixture_cases, source_mutations, roi_mutations;

void *hud_indicators_test_malloc(size_t size)
{
	++allocations;
	CHECK(size == PAYLOAD_BYTES && live_pointer == NULL);
	if (reject_allocation) return NULL;
	live_pointer = malloc(size);
	CHECK(live_pointer != NULL);
	return live_pointer;
}

void hud_indicators_test_free(void *pointer)
{
	if (pointer)
	{
		CHECK(pointer == live_pointer);
		++frees;
		live_pointer = NULL;
	}
	free(pointer);
}

int hud_indicators_test_open(const char *path, int flags, ...)
{
	CHECK(live_descriptor == -1);
	++opens;
	live_descriptor = open(path, flags);
	return live_descriptor;
}

ssize_t hud_indicators_test_read(int descriptor, void *buffer, size_t count)
{
	CHECK(descriptor == live_descriptor && count <= PAYLOAD_BYTES);
	++reads;
	if (fail_read_number && --fail_read_number == 0)
	{
		errno = EIO;
		return -1;
	}
	if (short_read_number && --short_read_number == 0) return read(descriptor, buffer, count - 1);
	return read(descriptor, buffer, count);
}

int hud_indicators_test_fstat(int descriptor, struct stat *status)
{
	int result;
	CHECK(descriptor == live_descriptor);
	++stats;
	if (reject_stat) return -1;
	result = fstat(descriptor, status);
	if (!result && override_size >= 0) status->st_size = override_size;
	return result;
}

int hud_indicators_test_close(int descriptor)
{
	int result;
	CHECK(descriptor == live_descriptor);
	++closes;
	live_descriptor = -1;
	result = close(descriptor);
	return reject_close ? -1 : result;
}

static uint64_t reference_fnv(const uint8_t *data, size_t count)
{
	uint64_t hash = UINT64_C(0xcbf29ce484222325);
	while (count--) { hash ^= *data++; hash *= UINT64_C(0x100000001b3); }
	return hash;
}

static void put32(unsigned offset, uint32_t value)
{
	for (unsigned i = 0; i < 4; ++i) header[offset + i] = (uint8_t)(value >> (8 * i));
}

static void put64(unsigned offset, uint64_t value)
{
	for (unsigned i = 0; i < 8; ++i) header[offset + i] = (uint8_t)(value >> (8 * i));
}

static void hashes(void)
{
	uint8_t rgb[256 * 3], top[21];
	for (int i = 0; i < 256; ++i)
	{
		rgb[i * 3] = (uint8_t)(palette[i] >> 16);
		rgb[i * 3 + 1] = (uint8_t)(palette[i] >> 8);
		rgb[i * 3 + 2] = (uint8_t)palette[i];
	}
	for (int y = 0; y < 3; ++y) memcpy(top + y * 7, source + (y + 4) * WIDTH + 269, 7);
	for (int state = 0; state < 2; ++state)
		for (int y = 0; y < 8; ++y)
			for (int x = 0; x < 27; ++x)
				mode_expected[state][y * 27 + x] = x < 10 ? sprites[state][y * 10 + x] :
					x >= 17 ? sprites[1 - state][y * 10 + x - 17] : source[(44 + y) * WIDTH + 285 + x];
	put64(32, reference_fnv(source, sizeof(source)));
	put64(40, reference_fnv(rgb, sizeof(rgb)));
	put64(48, reference_fnv(top, sizeof(top)));
	put64(56, reference_fnv(mode_expected[0], 216));
	put64(64, reference_fnv(mode_expected[1], 216));
	put64(72, reference_fnv(artwork, PAYLOAD_BYTES));
}

static void fresh(void)
{
	memset(header, 0, sizeof(header));
	memcpy(header, "HUL1", 4);
	put32(4, 1); put32(8, 4); put32(12, 28); put32(16, 12);
	put32(20, 108); put32(24, 32); put32(28, PAYLOAD_BYTES);
	for (size_t i = 0; i < sizeof(source); ++i)
		source[i] = (uint8_t)((i * 29 + i / WIDTH * 13) % 256);
	for (int state = 0; state < 2; ++state)
		for (int i = 0; i < 80; ++i)
		{
			sprites[state][i] = (uint8_t)((i * 17 + state * 61) % 253);
			opaque[state][i] = 255;
		}
	for (size_t i = 0; i < sizeof(artwork); i += 4)
	{
		artwork[i] = (uint8_t)(i / 4);
		artwork[i + 1] = (uint8_t)(i / 1024);
		artwork[i + 2] = (uint8_t)(i / 4096);
		artwork[i + 3] = 255;
	}
	for (unsigned i = 0; i < 256; ++i)
		palette[i] = UINT32_C(0xab000000) | (i << 16) | ((255 - i) << 8) | (i ^ 0x5a);
	hashes();
}

static void write_bytes(size_t size)
{
	FILE *file = fopen(filepath, "wb");
	size_t head = size < sizeof(header) ? size : sizeof(header);
	CHECK(file != NULL);
	CHECK(fwrite(header, 1, head, file) == head);
	if (size > head)
	{
		size_t count = size - head;
		if (count > sizeof(artwork)) count = sizeof(artwork);
		CHECK(fwrite(artwork, 1, count, file) == count);
		if (size > FILE_BYTES) CHECK(fputc(1, file) == 1);
	}
	CHECK(fclose(file) == 0);
}

static bool capture(const uint8_t *pixels, int pitch)
{
	return hud_indicators_capture(pixels, pitch, (const uint8_t (*)[80])sprites,
	                              (const uint8_t (*)[80])opaque);
}

static bool verify_modes(void)
{
	return hud_indicators_verify_modes((const uint8_t (*)[80])sprites,
	                                   (const uint8_t (*)[80])opaque);
}

static void reset(void)
{
	hud_indicators_shutdown();
	CHECK(live_pointer == NULL && live_descriptor == -1);
	CHECK(!hud_indicators_ready() && !hud_indicators_mode_ready());
	CHECK(!verify_modes());
	reject_allocation = reject_stat = reject_close = fail_read_number = short_read_number = 0;
	override_size = -1;
}

static void rejected(void)
{
	size_t attempts;
	CHECK(!hud_indicators_load(directory));
	CHECK(live_pointer == NULL && live_descriptor == -1);
	attempts = opens;
	CHECK(!hud_indicators_load(directory));
	CHECK(opens == attempts);
	++fixture_cases;
	reset();
}

static void valid_load(void)
{
	write_bytes(FILE_BYTES);
	CHECK(hud_indicators_load(directory));
	CHECK(!hud_indicators_ready() && !hud_indicators_mode_ready());
	CHECK(verify_modes());
	CHECK(capture(source, WIDTH));
	CHECK(hud_indicators_ready() && !hud_indicators_mode_ready());
	CHECK(hud_indicators_palette_matches(palette));
	CHECK(hud_indicators_top_matches(source, WIDTH));
	++fixture_cases;
}

static void test_loader(void)
{
	static const size_t bad_sizes[] = {0, 1, 79, 80, 81, 1024, FILE_BYTES - 1, FILE_BYTES + 1};
	char overlong[1100];
	size_t before;
	reset(); fresh();
	CHECK(unlink(filepath) == 0 || errno == ENOENT);
	CHECK(!hud_indicators_load(NULL));
	write_bytes(FILE_BYTES);
	CHECK(!hud_indicators_load(directory));
	reset(); CHECK(!hud_indicators_load("")); reset();
	memset(overlong, 'a', sizeof(overlong) - 1); overlong[sizeof(overlong) - 1] = 0;
	CHECK(!hud_indicators_load(overlong)); reset();
	CHECK(unlink(filepath) == 0); rejected();
	CHECK(mkdir(filepath, 0700) == 0); rejected(); CHECK(rmdir(filepath) == 0);
	CHECK(mkfifo(filepath, 0600) == 0); rejected(); CHECK(unlink(filepath) == 0);
	for (size_t i = 0; i < COUNT(bad_sizes); ++i)
	{
		write_bytes(bad_sizes[i]); before = allocations; rejected(); CHECK(before == allocations);
	}
	/* File growth/truncation after fstat must still fail closed. */
	write_bytes(79); override_size = FILE_BYTES; rejected();
	write_bytes(FILE_BYTES - 1); override_size = FILE_BYTES; rejected();
	write_bytes(FILE_BYTES + 1); override_size = FILE_BYTES; rejected();
	for (unsigned i = 0; i < 72; ++i)
	{
		fresh(); header[i] ^= 0x80; write_bytes(FILE_BYTES);
		before = allocations; rejected(); CHECK(before == allocations);
	}
	for (unsigned i = 72; i < 80; ++i)
	{
		fresh(); header[i] ^= 1; write_bytes(FILE_BYTES); rejected();
	}
	for (int section = 0; section < 3; ++section)
	{
		size_t base = section ? TOP_BYTES + (size_t)(section - 1) * MODE_BYTES : 0;
		size_t end = section ? base + MODE_BYTES : TOP_BYTES;
		for (int channel = 0; channel < 4; ++channel)
		{
			fresh(); artwork[base + (size_t)channel] ^= 1;
			write_bytes(FILE_BYTES); rejected();
		}
		for (int alpha = 0; alpha <= 254; ++alpha)
		{
			fresh(); artwork[end - 1] = (uint8_t)alpha;
			hashes(); write_bytes(FILE_BYTES); rejected();
		}
	}
	fresh(); write_bytes(FILE_BYTES); reject_allocation = 1; rejected();
	reject_stat = 1; rejected(); reject_close = 1; rejected();
	for (int n = 1; n <= 3; ++n) { fail_read_number = n; rejected(); }
	for (int n = 1; n <= 2; ++n) { short_read_number = n; rejected(); }
	valid_load();
	before = opens;
	CHECK(unlink(filepath) == 0);
	CHECK(hud_indicators_load(NULL)); CHECK(hud_indicators_load("elsewhere"));
	CHECK(opens == before && hud_indicators_ready());
	reset();
}

static void test_sources(void)
{
	size_t initial_allocations, initial_reads;
	fresh(); valid_load();
	initial_allocations = allocations; initial_reads = reads;
	CHECK(!hud_indicators_palette_matches(NULL));
	for (int i = 0; i < 256; ++i)
	{
		for (unsigned shift = 0; shift <= 16; shift += 8)
		{
			palette[i] ^= UINT32_C(1) << shift;
			CHECK(!hud_indicators_palette_matches(palette));
			palette[i] ^= UINT32_C(1) << shift;
		}
		palette[i] ^= UINT32_C(0xff000000);
		CHECK(hud_indicators_palette_matches(palette));
	}
	CHECK(!capture(NULL, WIDTH)); CHECK(!hud_indicators_ready());
	CHECK(!capture(source, WIDTH - 1)); CHECK(!capture(source, -1));
	CHECK(!capture(source, INT_MIN)); CHECK(!capture(source, 0));
	CHECK(capture(source, WIDTH));
	CHECK(!hud_indicators_capture(source, WIDTH, NULL, (const uint8_t (*)[80])opaque));
	CHECK(!hud_indicators_ready());
	CHECK(capture(source, WIDTH));
	CHECK(!hud_indicators_capture(source, WIDTH, (const uint8_t (*)[80])sprites, NULL));
	CHECK(!hud_indicators_ready());
	CHECK(!hud_indicators_verify_modes(NULL, (const uint8_t (*)[80])opaque));
	CHECK(!hud_indicators_verify_modes((const uint8_t (*)[80])sprites, NULL));
	memset(padded, 0xa5, sizeof(padded));
	for (int y = 0; y < HEIGHT; ++y) memcpy(padded + y * 337, source + y * WIDTH, WIDTH);
	CHECK(capture(padded, 337));
	for (int y = 0; y < HEIGHT; ++y)
	{
		static const int columns[] = {0, 159, 263, 269, 285, 295, 302, 319};
		for (size_t i = 0; i < COUNT(columns); ++i)
		{
			padded[y * 337 + columns[i]] ^= 1;
			CHECK(!capture(padded, 337)); CHECK(!hud_indicators_ready());
			padded[y * 337 + columns[i]] ^= 1;
			++source_mutations;
		}
	}
	for (int state = 0; state < 2; ++state)
		for (int i = 0; i < 80; ++i)
		{
			sprites[state][i] ^= 1;
			CHECK(!verify_modes() && !capture(source, WIDTH));
			sprites[state][i] ^= 1;
			for (int alpha = 0; alpha < 255; ++alpha)
			{
				opaque[state][i] = (uint8_t)alpha;
				CHECK(!verify_modes() && !capture(source, WIDTH));
			}
			opaque[state][i] = 255;
			CHECK(verify_modes());
		}
	CHECK(capture(source, WIDTH));
	hud_indicators_mode_drawn(1); CHECK(hud_indicators_mode_ready());
	CHECK(capture(source, WIDTH)); CHECK(!hud_indicators_mode_ready());
	hud_indicators_mode_drawn(2); CHECK(!capture(NULL, WIDTH));
	CHECK(!hud_indicators_ready() && !hud_indicators_mode_ready());
	CHECK(capture(source, WIDTH));
	hud_indicators_mode_drawn(1); hud_indicators_forget_source();
	CHECK(!hud_indicators_ready() && !hud_indicators_mode_ready());
	CHECK(!hud_indicators_top_matches(source, WIDTH));
	CHECK(!hud_indicators_sample(269, 4, 0, 0, 4, source[4 * WIDTH + 269]));
	CHECK(allocations == initial_allocations && reads == initial_reads);
	reset();
}

static bool top_pixel(int x, int y)
{
	return x >= 269 && x < 276 && y >= 4 && y < 7;
}

static bool mode_pixel(int x, int y)
{
	return x >= 285 && x < 312 && y >= 44 && y < 52;
}

static void draw_reference(int mode)
{
	memcpy(screen, source, sizeof(screen));
	for (int y = 0; y < 8; ++y)
		memcpy(screen + (44 + y) * WIDTH + 285, mode_expected[mode - 1] + y * 27, 27);
}

static const uint8_t *reference_sample(int mode, int x, int y, int sx, int sy)
{
	if (top_pixel(x, y)) return artwork + ((y - 4) * 4 + sy) * 28 * 4 + ((x - 269) * 4 + sx) * 4;
	return artwork + TOP_BYTES + (mode - 1) * MODE_BYTES +
	       ((y - 44) * 4 + sy) * 108 * 4 + ((x - 285) * 4 + sx) * 4;
}

static void test_samples_and_stamps(void)
{
	size_t initial_allocations, initial_reads, initial_opens;
	unsigned black_samples = 0;
	fresh(); valid_load();
	initial_allocations = allocations; initial_reads = reads; initial_opens = opens;
	for (int mode = 1; mode <= 2; ++mode)
	{
		unsigned owned = 0;
		draw_reference(mode);
		CHECK(!hud_indicators_mode_matches(screen, WIDTH));
		CHECK(!hud_indicators_sample(285, 44, 0, 0, 4, screen[44 * WIDTH + 285]));
		hud_indicators_mode_drawn(mode);
		CHECK(hud_indicators_mode_matches(screen, WIDTH));
		CHECK(hud_indicators_top_matches(screen, WIDTH));
		CHECK(!hud_indicators_mode_matches(NULL, WIDTH));
		CHECK(!hud_indicators_top_matches(NULL, WIDTH));
		CHECK(!hud_indicators_mode_matches(screen, 319));
		CHECK(!hud_indicators_top_matches(screen, 319));
		for (int y = 0; y < HEIGHT; ++y)
			for (int x = 0; x < WIDTH; ++x)
			{
				bool top = top_pixel(x, y), assembly = mode_pixel(x, y);
				uint8_t index = screen[y * WIDTH + x];
				const uint8_t *sample = hud_indicators_sample(x, y, 0, 0, 4, index);
				CHECK((sample != NULL) == (top || assembly));
				if (!sample) continue;
				++owned;
				if (!index) ++black_samples;
				CHECK(!hud_indicators_sample(x, y, 0, 0, 4, (uint8_t)(index + 1)));
				screen[y * WIDTH + x] ^= 1;
				CHECK(hud_indicators_top_matches(screen, WIDTH) == !top);
				CHECK(hud_indicators_mode_matches(screen, WIDTH) == !assembly);
				screen[y * WIDTH + x] ^= 1;
				CHECK(hud_indicators_mode_ready()); /* Read-only checks retain the stamp. */
				++roi_mutations;
				for (int sy = 0; sy < 8; ++sy)
					for (int sx = 0; sx < 8; ++sx)
					{
						const uint8_t *p4 = hud_indicators_sample(x, y, sx / 2, sy / 2, 4, index);
						const uint8_t *p8 = hud_indicators_sample(x, y, sx, sy, 8, index);
						CHECK(p4 && p8 == p4);
						CHECK(!memcmp(p4, reference_sample(mode, x, y, sx / 2, sy / 2), 4));
					}
			}
		CHECK(owned == 237);
		for (int y = 0; y < HEIGHT; ++y) memcpy(padded + y * 337, screen + y * WIDTH, WIDTH);
		CHECK(hud_indicators_mode_matches(padded, 337) && hud_indicators_top_matches(padded, 337));
		/* The complete center and sprite rims are owned; neighbors/padding are not. */
		padded[44 * 337 + 284] ^= 1; padded[52 * 337 + 285] ^= 1;
		padded[4 * 337 + 268] ^= 1; padded[7 * 337 + 269] ^= 1; padded[4 * 337 + 320] ^= 1;
		CHECK(hud_indicators_mode_matches(padded, 337) && hud_indicators_top_matches(padded, 337));
		hud_indicators_mode_drawn(3 - mode); CHECK(!hud_indicators_mode_matches(screen, WIDTH));
		hud_indicators_mode_drawn(mode); CHECK(hud_indicators_mode_matches(screen, WIDTH));
		hud_indicators_mode_wiped();
		CHECK(!hud_indicators_mode_ready() && hud_indicators_ready());
		CHECK(!hud_indicators_mode_matches(screen, WIDTH));
		CHECK(hud_indicators_top_matches(screen, WIDTH));
		CHECK(!hud_indicators_sample(285, 44, 0, 0, 4, screen[44 * WIDTH + 285]));
		CHECK(hud_indicators_sample(269, 4, 0, 0, 4, screen[4 * WIDTH + 269]));
	}
	CHECK(black_samples > 0);
	hud_indicators_mode_drawn(1); draw_reference(1);
	for (int y = 0; y < 2; ++y)
	{
		int x0 = y ? 285 : 269, y0 = y ? 44 : 4;
		uint8_t index = screen[y0 * WIDTH + x0];
		for (int density = -1; density <= 16; ++density)
			if (density != 4 && density != 8)
				CHECK(!hud_indicators_sample(x0, y0, 0, 0, density, index));
		CHECK(!hud_indicators_sample(x0, y0, -1, 0, 4, index));
		CHECK(!hud_indicators_sample(x0, y0, 0, -1, 4, index));
		CHECK(!hud_indicators_sample(x0, y0, 4, 0, 4, index));
		CHECK(!hud_indicators_sample(x0, y0, 0, 8, 8, index));
	}
	CHECK(!hud_indicators_sample(INT_MIN, INT_MAX, 0, 0, 4, 0));
	CHECK(!hud_indicators_sample(INT_MAX, INT_MIN, 0, 0, 4, 0));
	{
		static const int invalid[] = {-1, 0, 3, INT_MIN, INT_MAX};
		for (size_t i = 0; i < COUNT(invalid); ++i)
		{
			hud_indicators_mode_drawn(1); CHECK(hud_indicators_mode_ready());
			hud_indicators_mode_drawn(invalid[i]);
			CHECK(!hud_indicators_mode_ready() && hud_indicators_ready());
		}
	}
	hud_indicators_forget_source(); hud_indicators_mode_drawn(1);
	CHECK(!hud_indicators_ready() && !hud_indicators_mode_ready());
	CHECK(allocations == initial_allocations && reads == initial_reads && opens == initial_opens);
	reset();
}

static void test_production_guards(void)
{
	static const uint64_t guards[] = {
		UINT64_C(0x14c1441f3d5dc0e2), UINT64_C(0x5e80e83992be2927),
		UINT64_C(0x328ef0a75cce2260), UINT64_C(0x55f78c15a1ce495a), UINT64_C(0xf7a97c521d045d18)
	};
	fresh(); write_bytes(FILE_BYTES); rejected(); /* Synthetic source cannot widen production guards. */
	for (size_t i = 0; i < COUNT(guards); ++i) put64(32 + (unsigned)i * 8, guards[i]);
	write_bytes(FILE_BYTES); CHECK(hud_indicators_load(directory));
	CHECK(!capture(source, WIDTH) && !hud_indicators_ready());
	CHECK(!verify_modes() && !hud_indicators_palette_matches(palette));
	hud_indicators_mode_drawn(1); CHECK(!hud_indicators_mode_ready());
	reset();
	for (unsigned i = 32; i < 72; ++i)
	{
		header[i] ^= 1; write_bytes(FILE_BYTES); rejected(); header[i] ^= 1;
	}
	printf("PASS HUL1 production guards: five pinned header hashes, synthetic source/sprites/palette rejected.\n");
}

int main(int argc, char **argv)
{
	CHECK(argc == 2 || (argc == 3 && !strcmp(argv[2], "production")));
	directory = argv[1];
	CHECK(snprintf(filepath, sizeof(filepath), "%s/gameplay-hud-indicators-v1.hda", directory) > 0);
	if (argc == 3)
	{
		test_production_guards();
		CHECK(live_pointer == NULL && live_descriptor == -1 && allocations == frees);
		return 0;
	}
	test_loader(); test_sources(); test_samples_and_stamps();
	CHECK(source_mutations == 1600 && roi_mutations == 474);
	CHECK(live_pointer == NULL && live_descriptor == -1);
	CHECK(allocations == frees + 1); /* Exactly one deliberately refused allocation. */
	CHECK(closes == stats);
	printf("PASS HUL1: %u fixture cases, %u whole-source and %u ROI mutations; "
	       "both modes and 237 pixels, 4x/8x samples, exact 28992-byte allocation, no runtime allocation/I/O.\n",
	       fixture_cases, source_mutations, roi_mutations);
	return 0;
}
