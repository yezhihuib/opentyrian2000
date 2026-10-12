/* Entirely generated fixtures; no original game data, RGB, artwork or captures. */
#include "gameplay_hud_components.h"
#include "allocation_probe.h"

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
#define LABEL_BYTES 22400
#define BAND_BYTES 16128
#define PAYLOAD_BYTES (LABEL_BYTES + BAND_BYTES)
#define FILE_BYTES (64 + PAYLOAD_BYTES)
#define COUNT(a) (sizeof(a) / sizeof((a)[0]))
#define CHECK(t) do { if (!(t)) { \
	fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #t); exit(1); } } while (0)

static uint8_t header[64], artwork[PAYLOAD_BYTES], source[WIDTH * HEIGHT];
static uint8_t screen[WIDTH * HEIGHT], padded[337 * HEIGHT];
static uint32_t palette[256];
static char filepath[2048];
static const char *directory;
static size_t allocations, frees, opens, reads, closes, stats;
static void *live_pointer;
static int live_descriptor = -1, reject_allocation, reject_stat, reject_close;
static int fail_read_number, override_size = -1;
static unsigned fixture_cases, shield_pairs, roi_mutations;

void *hud_components_test_malloc(size_t size)
{
	++allocations;
	CHECK(size == PAYLOAD_BYTES && live_pointer == NULL);
	if (reject_allocation) return NULL;
	live_pointer = malloc(size);
	CHECK(live_pointer != NULL);
	return live_pointer;
}

void hud_components_test_free(void *pointer)
{
	if (pointer)
	{
		CHECK(pointer == live_pointer);
		++frees;
		live_pointer = NULL;
	}
	free(pointer);
}

int hud_components_test_open(const char *path, int flags, ...)
{
	CHECK(live_descriptor == -1);
	++opens;
	live_descriptor = open(path, flags);
	return live_descriptor;
}

ssize_t hud_components_test_read(int descriptor, void *buffer, size_t count)
{
	CHECK(descriptor == live_descriptor && count <= PAYLOAD_BYTES);
	++reads;
	if (fail_read_number && --fail_read_number == 0)
	{
		errno = EIO;
		return -1;
	}
	return read(descriptor, buffer, count);
}

int hud_components_test_fstat(int descriptor, struct stat *status)
{
	int result;
	CHECK(descriptor == live_descriptor);
	++stats;
	if (reject_stat) return -1;
	result = fstat(descriptor, status);
	if (!result && override_size >= 0) status->st_size = override_size;
	return result;
}

int hud_components_test_close(int descriptor)
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
	uint8_t rgb[256 * 3];
	for (int i = 0; i < 256; ++i)
	{
		rgb[i * 3] = (uint8_t)(palette[i] >> 16);
		rgb[i * 3 + 1] = (uint8_t)(palette[i] >> 8);
		rgb[i * 3 + 2] = (uint8_t)palette[i];
	}
	put64(32, reference_fnv(source, sizeof(source)));
	put64(40, reference_fnv(artwork, LABEL_BYTES));
	put64(48, reference_fnv(artwork + LABEL_BYTES, BAND_BYTES));
	put64(56, reference_fnv(rgb, sizeof(rgb)));
}

static void fresh(void)
{
	memset(header, 0, sizeof(header));
	memcpy(header, "HUC1", 4);
	put32(4, 1); put32(8, 4); put32(12, 4); put32(16, LABEL_BYTES);
	put32(20, 14); put32(24, 36); put32(28, 8);
	for (size_t i = 0; i < sizeof(source); ++i)
		source[i] = (uint8_t)((i * 29 + i / WIDTH * 13) % 256);
	for (int y = 137; y < 195; ++y)
		memset(source + y * WIDTH + 270, 0, 9);
	for (size_t i = 0; i < sizeof(artwork); i += 4)
	{
		artwork[i] = (uint8_t)(i / 4);
		artwork[i + 1] = (uint8_t)(i / 1024);
		artwork[i + 2] = (uint8_t)(i / 16384);
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

static void reset(void)
{
	hud_components_shutdown();
	CHECK(live_pointer == NULL && live_descriptor == -1);
	CHECK(!hud_components_ready() && !hud_components_shield_ready());
	reject_allocation = reject_stat = reject_close = fail_read_number = 0;
	override_size = -1;
}

static void rejected(void)
{
	size_t attempts;
	CHECK(!hud_components_load(directory));
	CHECK(live_pointer == NULL && live_descriptor == -1);
	attempts = opens;
	CHECK(!hud_components_load(directory));
	CHECK(opens == attempts);
	++fixture_cases;
	reset();
}

static void valid_load(void)
{
	write_bytes(FILE_BYTES);
	CHECK(hud_components_load(directory));
	CHECK(!hud_components_ready() && !hud_components_shield_ready());
	CHECK(hud_components_capture(source, WIDTH));
	CHECK(hud_components_ready() && !hud_components_shield_ready());
	CHECK(hud_components_palette_matches(palette));
	++fixture_cases;
}

static void test_loader(void)
{
	static const size_t bad_sizes[] = {0, 1, 63, 64, 65, 1024, FILE_BYTES - 1, FILE_BYTES + 1};
	char overlong[1100];
	size_t before;
	reset(); fresh();
	CHECK(unlink(filepath) == 0 || errno == ENOENT);
	CHECK(!hud_components_load(NULL));
	write_bytes(FILE_BYTES);
	CHECK(!hud_components_load(directory));
	reset(); CHECK(!hud_components_load("")); reset();
	memset(overlong, 'a', sizeof(overlong) - 1); overlong[sizeof(overlong) - 1] = 0;
	CHECK(!hud_components_load(overlong)); reset();
	CHECK(unlink(filepath) == 0); rejected();
	CHECK(mkdir(filepath, 0700) == 0); rejected(); CHECK(rmdir(filepath) == 0);
	CHECK(mkfifo(filepath, 0600) == 0); rejected(); CHECK(unlink(filepath) == 0);
	for (size_t i = 0; i < COUNT(bad_sizes); ++i)
	{
		write_bytes(bad_sizes[i]); before = allocations; rejected(); CHECK(before == allocations);
	}
	/* Independently exercise short reads and EOF after the descriptor length
	 * check, as if the file changed after fstat. */
	write_bytes(FILE_BYTES - 1); override_size = FILE_BYTES; rejected();
	write_bytes(FILE_BYTES + 1); override_size = FILE_BYTES; rejected();
	for (unsigned i = 0; i < 32; ++i)
	{
		fresh(); header[i] ^= 0x80; write_bytes(FILE_BYTES);
		before = allocations; rejected(); CHECK(before == allocations);
	}
	for (unsigned i = 40; i < 56; ++i)
	{
		fresh(); header[i] ^= 1; write_bytes(FILE_BYTES); rejected();
	}
	for (int section = 0; section < 2; ++section)
	{
		size_t base = section ? LABEL_BYTES : 0;
		for (int channel = 0; channel < 4; ++channel)
		{
			fresh(); artwork[base + (size_t)channel] ^= 1;
			write_bytes(FILE_BYTES); rejected();
		}
		for (int alpha = 0; alpha <= 254; ++alpha)
		{
			fresh(); artwork[base + (section ? BAND_BYTES : LABEL_BYTES) - 1] = (uint8_t)alpha;
			hashes(); write_bytes(FILE_BYTES); rejected();
		}
	}
	fresh(); write_bytes(FILE_BYTES); reject_allocation = 1; rejected();
	reject_stat = 1; rejected(); reject_close = 1; rejected();
	for (int n = 1; n <= 3; ++n) { fail_read_number = n; rejected(); }
	valid_load();
	before = opens;
	CHECK(unlink(filepath) == 0);
	CHECK(hud_components_load(NULL)); CHECK(hud_components_load("elsewhere"));
	CHECK(opens == before && hud_components_ready());
	reset();
}

static int label_number(int x, int y)
{
	if (x >= 285 && x < 309 && y >= 5 && y < 10) return 0;
	if (x >= 285 && x < 299 && y >= 11 && y < 16) return 1;
	if (x >= 285 && x < 303 && y >= 26 && y < 31) return 2;
	if (x >= 285 && x < 299 && y >= 32 && y < 37) return 3;
	return -1;
}

static const uint8_t *reference_label(int label, int x, int y, int sx, int sy)
{
	static const int widths[] = {96, 56, 72, 56}, tops[] = {5, 11, 26, 32};
	static const size_t offsets[] = {0, 7680, 12160, 17920};
	return artwork + offsets[label] +
	       (size_t)((4 * (y - tops[label]) + sy) * widths[label] + 4 * (x - 285) + sx) * 4;
}

static void test_labels(void)
{
	size_t initial_allocations, initial_reads, initial_opens;
	unsigned owned = 0;
	fresh(); valid_load();
	initial_allocations = allocations; initial_reads = reads; initial_opens = opens;
	for (int y = 0; y < HEIGHT; ++y)
		for (int x = 0; x < WIDTH; ++x)
		{
			int label = label_number(x, y);
			uint8_t index = source[y * WIDTH + x];
			const uint8_t *sample = hud_components_label_sample(x, y, 0, 0, 4, index);
			CHECK((sample != NULL) == (label >= 0));
			if (label < 0) continue;
			++owned;
			CHECK(!hud_components_label_sample(x, y, 0, 0, 4, (uint8_t)(index + 1)));
			for (int sy = 0; sy < 8; ++sy)
				for (int sx = 0; sx < 8; ++sx)
				{
					const uint8_t *p4 = hud_components_label_sample(x, y, sx / 2, sy / 2, 4, index);
					const uint8_t *p8 = hud_components_label_sample(x, y, sx, sy, 8, index);
					CHECK(p4 && p8 == p4);
					CHECK(!memcmp(p4, reference_label(label, x, y, sx / 2, sy / 2), 4));
				}
		}
	CHECK(owned == 350);
	for (int density = -1; density <= 16; ++density)
		if (density != 4 && density != 8)
			CHECK(!hud_components_label_sample(285, 5, 0, 0, density, source[5 * WIDTH + 285]));
	CHECK(!hud_components_label_sample(INT_MIN, INT_MAX, 0, 0, 4, 0));
	CHECK(!hud_components_label_sample(INT_MAX, INT_MIN, 0, 0, 4, 0));
	CHECK(!hud_components_label_sample(285, 5, -1, 0, 4, source[5 * WIDTH + 285]));
	CHECK(!hud_components_label_sample(285, 5, 0, -1, 4, source[5 * WIDTH + 285]));
	CHECK(!hud_components_label_sample(285, 5, 4, 0, 4, source[5 * WIDTH + 285]));
	CHECK(!hud_components_label_sample(285, 5, 0, 8, 8, source[5 * WIDTH + 285]));
	CHECK(allocations == initial_allocations && reads == initial_reads && opens == initial_opens);
	reset();
	/* All 350 captured zero indices are permitted, with no coordinate widening. */
	for (int y = 0; y < HEIGHT; ++y)
		for (int x = 0; x < WIDTH; ++x)
			if (label_number(x, y) >= 0) source[y * WIDTH + x] = 0;
	hashes(); valid_load();
	for (int y = 0; y < HEIGHT; ++y)
		for (int x = 0; x < WIDTH; ++x)
			CHECK((hud_components_label_sample(x, y, 0, 0, 4, 0) != NULL) == (label_number(x, y) >= 0));
	reset();
}

static void test_capture_palette(void)
{
	size_t initial_allocations, initial_reads;
	fresh(); valid_load();
	initial_allocations = allocations; initial_reads = reads;
	CHECK(!hud_components_palette_matches(NULL));
	for (int i = 0; i < 256; ++i)
	{
		for (unsigned shift = 0; shift <= 16; shift += 8)
		{
			palette[i] ^= UINT32_C(1) << shift;
			CHECK(!hud_components_palette_matches(palette));
			palette[i] ^= UINT32_C(1) << shift;
		}
		palette[i] ^= UINT32_C(0xff000000);
		CHECK(hud_components_palette_matches(palette));
	}
	CHECK(hud_components_palette_matches(palette));
	CHECK(!hud_components_capture(NULL, WIDTH)); CHECK(!hud_components_ready());
	CHECK(!hud_components_capture(source, WIDTH - 1));
	CHECK(!hud_components_capture(source, -1));
	CHECK(hud_components_capture(source, WIDTH));
	memset(padded, 0xa5, sizeof(padded));
	for (int y = 0; y < HEIGHT; ++y) memcpy(padded + y * 337, source + y * WIDTH, WIDTH);
	CHECK(hud_components_capture(padded, 337));
	for (int y = 0; y < HEIGHT; ++y)
	{
		static const int columns[] = {0, 159, 263, 319};
		for (size_t i = 0; i < COUNT(columns); ++i)
		{
			padded[y * 337 + columns[i]] ^= 1;
			CHECK(!hud_components_capture(padded, 337)); CHECK(!hud_components_ready());
			padded[y * 337 + columns[i]] ^= 1;
		}
	}
	CHECK(hud_components_capture(padded, 337));
	hud_components_shield_drawn(5, 10); CHECK(hud_components_shield_ready());
	CHECK(hud_components_capture(source, WIDTH)); CHECK(!hud_components_shield_ready());
	hud_components_shield_drawn(5, 10); CHECK(!hud_components_capture(NULL, WIDTH));
	CHECK(!hud_components_ready() && !hud_components_shield_ready());
	CHECK(allocations == initial_allocations && reads == initial_reads);
	reset();
	/* Hash fields are metadata gates, rather than an implicit asset identity. */
	for (unsigned offset = 32; offset < 40; ++offset)
	{
		fresh(); header[offset] ^= 1; write_bytes(FILE_BYTES);
		CHECK(hud_components_load(directory)); CHECK(!hud_components_capture(source, WIDTH)); reset();
	}
	for (unsigned offset = 56; offset < 64; ++offset)
	{
		fresh(); header[offset] ^= 1; write_bytes(FILE_BYTES);
		CHECK(hud_components_load(directory)); CHECK(hud_components_capture(source, WIDTH));
		CHECK(!hud_components_palette_matches(palette)); reset();
	}
	/* Every pristine ROI pixel is independently rejected even with its source
	 * checksum honestly recomputed; checking only a border is insufficient. */
	for (int y = 137; y < 195; ++y)
		for (int x = 270; x < 279; ++x)
		{
			fresh(); source[y * WIDTH + x] = 1; hashes(); write_bytes(FILE_BYTES);
			CHECK(hud_components_load(directory)); CHECK(!hud_components_capture(source, WIDTH));
			CHECK(!hud_components_ready()); ++roi_mutations; reset();
		}
}

/* Independent iterative rendition of the original JE_dBar3 + maximum marker:
 * no shared arithmetic with the production scalar expected-index function. */
static void draw_reference(int shield, int maximum)
{
	int bottom = 194, color = 146, wait = 2;
	memcpy(screen, source, sizeof(screen));
	for (int z = 0; z <= shield; ++z)
	{
		for (int y = bottom - 1; y <= bottom; ++y)
			for (int x = 270; x <= 278; ++x) screen[y * WIDTH + x] = (uint8_t)color;
		if (wait > 0) --wait;
		else { ++color; wait = 1; }
		bottom -= 2;
	}
	if (shield != maximum)
		memset(screen + (193 - 2 * maximum) * WIDTH + 270, 68, 9);
}

static void test_shield(void)
{
	size_t initial_allocations, initial_reads, initial_opens;
	fresh(); valid_load();
	initial_allocations = allocations; initial_reads = reads; initial_opens = opens;
	CHECK(!hud_components_shield_matches(source, WIDTH));
	CHECK(!hud_components_shield_sample(270, 194, 0, 0, 4, 146));
	for (int maximum = 0; maximum <= 28; ++maximum)
		for (int shield = 0; shield <= maximum; ++shield)
		{
			draw_reference(shield, maximum);
			hud_components_shield_drawn(shield, maximum);
			CHECK(hud_components_shield_ready());
			CHECK(hud_components_shield_matches(screen, WIDTH));
			CHECK(!hud_components_shield_matches(NULL, WIDTH));
			CHECK(!hud_components_shield_matches(screen, 319));
			for (int y = 137; y < 195; ++y)
				for (int x = 270; x < 279; ++x)
				{
					uint8_t index = screen[y * WIDTH + x];
					screen[y * WIDTH + x] ^= 1;
					CHECK(!hud_components_shield_matches(screen, WIDTH));
					screen[y * WIDTH + x] ^= 1;
					CHECK(hud_components_shield_ready());
					CHECK(!hud_components_shield_sample(x, y, 0, 0, 4, (uint8_t)(index + 1)));
					for (int sy = 0; sy < 8; ++sy)
						for (int sx = 0; sx < 8; ++sx)
						{
							const uint8_t *p4 = hud_components_shield_sample(x, y, sx / 2, sy / 2, 4, index);
							const uint8_t *p8 = hud_components_shield_sample(x, y, sx, sy, 8, index);
							CHECK(p4 == p8);
							CHECK((p4 != NULL) == (index >= 146 && index <= 159));
							if (p4)
							{
								size_t offset = LABEL_BYTES + (size_t)(index - 146) * 36 * 8 * 4;
								int row = (y % 2 ? 0 : 4) + sy / 2;
								offset += (size_t)(row * 36 + (x - 270) * 4 + sx / 2) * 4;
								CHECK(!memcmp(p4, artwork + offset, 4));
							}
						}
				}
			hud_components_shield_wiped();
			CHECK(!hud_components_shield_ready() && hud_components_ready());
			CHECK(!hud_components_shield_matches(screen, WIDTH));
			CHECK(!hud_components_shield_sample(270, 194, 0, 0, 4, 146));
			++shield_pairs;
		}
	draw_reference(28, 28); hud_components_shield_drawn(28, 28);
	for (int y = 0; y < HEIGHT; ++y)
		for (int x = 0; x < WIDTH; ++x)
		{
			bool owned = x >= 270 && x < 279 && y >= 137 && y < 195;
			CHECK((hud_components_shield_sample(x, y, 0, 0, 4, screen[y * WIDTH + x]) != NULL) == owned);
		}
	CHECK(!hud_components_shield_sample(INT_MIN, INT_MAX, 0, 0, 4, 146));
	CHECK(!hud_components_shield_sample(INT_MAX, INT_MIN, 0, 0, 4, 146));
	for (int density = -1; density <= 16; ++density)
		if (density != 4 && density != 8)
			CHECK(!hud_components_shield_sample(270, 194, 0, 0, density, 146));
	CHECK(!hud_components_shield_sample(270, 194, -1, 0, 4, 146));
	CHECK(!hud_components_shield_sample(270, 194, 0, -1, 4, 146));
	CHECK(!hud_components_shield_sample(270, 194, 4, 0, 4, 146));
	CHECK(!hud_components_shield_sample(270, 194, 0, 8, 8, 146));
	for (int y = 0; y < HEIGHT; ++y) memcpy(padded + y * 337, screen + y * WIDTH, WIDTH);
	CHECK(hud_components_shield_matches(padded, 337));
	/* Unowned neighbors and padding never enter the full-ROI comparison. */
	padded[137 * 337 + 269] ^= 1; padded[195 * 337 + 270] ^= 1; padded[137 * 337 + 320] ^= 1;
	CHECK(hud_components_shield_matches(padded, 337));
	{
		static const int invalid[][2] = {{-1,0}, {0,-1}, {1,0}, {29,29}, {0,29}, {INT_MAX,INT_MAX}, {INT_MIN,28}};
		for (size_t i = 0; i < COUNT(invalid); ++i)
		{
			hud_components_shield_drawn(28,28); CHECK(hud_components_shield_ready());
			hud_components_shield_drawn(invalid[i][0], invalid[i][1]);
			CHECK(!hud_components_shield_ready() && hud_components_ready());
		}
	}
	hud_components_forget_source(); hud_components_shield_drawn(28,28);
	CHECK(!hud_components_ready() && !hud_components_shield_ready());
	CHECK(!hud_components_label_sample(285,5,0,0,4,source[5 * WIDTH + 285]));
	CHECK(hud_components_capture(source, WIDTH)); CHECK(!hud_components_shield_ready());
	hud_components_shield_drawn(0,0); draw_reference(0,0);
	CHECK(hud_components_shield_matches(screen, WIDTH));
	CHECK(hud_components_shield_sample(270,193,0,0,4,146));
	CHECK(hud_components_shield_sample(270,194,0,0,4,146));
	hud_components_shield_wiped(); CHECK(!hud_components_shield_sample(270,194,0,0,4,146));
	CHECK(allocations == initial_allocations && reads == initial_reads && opens == initial_opens);
	reset();
}

int main(int argc, char **argv)
{
	CHECK(argc == 2);
	directory = argv[1];
	CHECK(snprintf(filepath, sizeof(filepath), "%s/gameplay-hud-components-v1.hda", directory) > 0);
	test_loader(); test_labels(); test_capture_palette(); test_shield();
	CHECK(shield_pairs == 435 && roi_mutations == 522);
	CHECK(live_pointer == NULL && live_descriptor == -1);
	CHECK(allocations == frees + 1); /* Exactly one deliberately refused allocation. */
	CHECK(closes == stats);
	printf("PASS HUC1: %u fixture cases, all %u shield pairs, %u pristine ROI mutations; "
	       "350 label pixels, 4x/8x samples, exact 38528-byte allocation, no runtime allocation/I/O.\n",
	       fixture_cases, shield_pairs, roi_mutations);
	return 0;
}
