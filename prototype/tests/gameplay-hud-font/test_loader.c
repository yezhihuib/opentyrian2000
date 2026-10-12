#include "gameplay_hud_font.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

enum { PAYLOAD_BYTES = 163840, FILE_BYTES = 163952 };

#ifdef HUD_FONT_TEST_IO

static size_t allocations, frees, opens, reads, closes, stats;
static void *live_pointer;
static int live_descriptor = -1, reject_allocation, reject_stat, reject_close;
static int fail_read_number, short_read_number, override_size = -1;

void *font_test_malloc(size_t size)
{
	++allocations;
	assert(size == PAYLOAD_BYTES && live_pointer == NULL);
	if (reject_allocation) return NULL;
	live_pointer = malloc(size);
	assert(live_pointer);
	return live_pointer;
}

void font_test_free(void *pointer)
{
	if (pointer)
	{
		assert(pointer == live_pointer);
		++frees;
		live_pointer = NULL;
	}
	free(pointer);
}

int font_test_open(const char *path, int flags, ...)
{
	assert(live_descriptor == -1);
	++opens;
	live_descriptor = open(path, flags);
	return live_descriptor;
}

ssize_t font_test_read(int descriptor, void *buffer, size_t count)
{
	assert(descriptor == live_descriptor && count <= PAYLOAD_BYTES);
	++reads;
	if (fail_read_number && --fail_read_number == 0)
	{
		errno = EIO;
		return -1;
	}
	if (short_read_number && --short_read_number == 0)
		return read(descriptor, buffer, count - 1);
	return read(descriptor, buffer, count);
}

int font_test_fstat(int descriptor, struct stat *status)
{
	int result;
	assert(descriptor == live_descriptor);
	++stats;
	if (reject_stat) return -1;
	result = fstat(descriptor, status);
	if (!result && override_size >= 0) status->st_size = override_size;
	return result;
}

int font_test_close(int descriptor)
{
	int result;
	assert(descriptor == live_descriptor);
	++closes;
	live_descriptor = -1;
	result = close(descriptor);
	return reject_close ? -1 : result;
}

static unsigned cases;
static void reject(const char *path)
{
	size_t opened = opens, closed = closes;
	assert(!hud_font_load(path));
	assert(!live_pointer && live_descriptor == -1);
	assert(opens == opened + 1 && closes == closed + 1);
	assert(!hud_font_load(path));
	assert(opens == opened + 1);
	hud_font_shutdown();
	assert(!live_pointer && live_descriptor == -1);
	reject_allocation = reject_stat = reject_close = 0;
	fail_read_number = short_read_number = 0;
	override_size = -1;
	++cases;
}

static void write_resource(const char *file, const unsigned char *raw, size_t size)
{
	FILE *f = fopen(file, "wb");
	assert(f && fwrite(raw, 1, size, f) == size);
	assert(!fclose(f));
}

int main(int argc, char **argv)
{
	char file[1200];
	unsigned char raw[FILE_BYTES + 1];
	assert(argc >= 2);
	snprintf(file, sizeof(file), "%s/gameplay-hud-font-v1.hda", argv[1]);
	FILE *f = fopen(file, "rb");
	assert(f && fread(raw, 1, FILE_BYTES, f) == FILE_BYTES);
	assert(!fclose(f));
	raw[FILE_BYTES] = 1;
	if (argc == 3)
	{
		reject(argv[1]);
		assert(allocations == 0);
		puts("HUF1 production pins reject the synthetic source before allocation.");
		return 0;
	}
	reject_allocation = 1; reject(argv[1]);
	reject_stat = 1; reject(argv[1]);
	reject_close = 1; reject(argv[1]);
	for (int n = 1; n <= 3; ++n) { fail_read_number = n; reject(argv[1]); }
	for (int n = 1; n <= 2; ++n) { short_read_number = n; reject(argv[1]); }
	size_t sizes[] = { 111, FILE_BYTES - 1, FILE_BYTES + 1 };
	for (unsigned i = 0; i < 3; ++i)
	{
		write_resource(file, raw, sizes[i]);
		override_size = FILE_BYTES;
		reject(argv[1]);
	}
	write_resource(file, raw, FILE_BYTES);
	assert(hud_font_load(argv[1]) && live_pointer && live_descriptor == -1);
	size_t o = opens, r = reads, a = allocations, s = stats;
	assert(hud_font_load(argv[1]));
	assert(opens == o && reads == r && allocations == a && stats == s);
	hud_font_shutdown();
	assert(!live_pointer && live_descriptor == -1);
	assert(allocations == frees + 1); /* One deliberate allocation failure. */
	assert(cases == 11);
	printf("HUF1 I/O PASS: %u failures, one attempt, no live allocation or descriptor.\n", cases);
	return 0;
}

#else

static uint8_t source[64000], padded[200 * 337], alpha[PAYLOAD_BYTES];
static uint8_t encoded[127][256];
static uint32_t palette[256];
static int mapping[256];
static HudFontGlyph glyphs[127];

static FILE *open_fixture(const char *base, const char *name)
{
	char path[1200];
	snprintf(path, sizeof(path), "%s/%s", base, name);
	FILE *file = fopen(path, "rb");
	assert(file);
	return file;
}

static void read_file(const char *base, const char *name, void *out, size_t n)
{
	FILE *file = open_fixture(base, name);
	assert(fread(out, 1, n, file) == n && fgetc(file) == EOF);
	assert(!fclose(file));
}

static unsigned read_u16(FILE *file)
{
	int lo = fgetc(file), hi = fgetc(file);
	assert(lo >= 0 && hi >= 0);
	return (unsigned)lo | ((unsigned)hi << 8);
}

static void read_sources(const char *base)
{
	uint8_t map_bytes[1024];
	read_file(base, "source.bin", source, sizeof(source));
	read_file(base, "alpha.bin", alpha, sizeof(alpha));
	read_file(base, "map.bin", map_bytes, sizeof(map_bytes));
	for (unsigned i = 0; i < 256; ++i)
	{
		const uint8_t *p = map_bytes + i * 4;
		uint32_t value = (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
		                 ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
		assert(value == UINT32_MAX || value < 127);
		mapping[i] = value == UINT32_MAX ? -1 : (int)value;
		palette[i] = 0xaa000000u | ((uint32_t)((i * 5) % 256) << 16) |
		             ((uint32_t)((i * 11) % 256) << 8) | (i * 17) % 256;
	}
	FILE *file = open_fixture(base, "glyphs.bin");
	for (unsigned i = 0; i < 127; ++i)
	{
		glyphs[i].width = (uint16_t)read_u16(file);
		glyphs[i].height = (uint16_t)read_u16(file);
		glyphs[i].size = (uint16_t)read_u16(file);
		assert(glyphs[i].size <= sizeof(encoded[i]));
		assert(fread(encoded[i], 1, glyphs[i].size, file) == glyphs[i].size);
		glyphs[i].data = encoded[i];
	}
	assert(fgetc(file) == EOF && !fclose(file));
}

int main(int argc, char **argv)
{
	char path[1200];
	assert(argc >= 2);
	const char *base = argv[1];
	read_sources(base);
	assert(!hud_font_ready() && !hud_font_source_matches(mapping, glyphs));
	assert(!hud_font_capture(source, 320, mapping, glyphs));
	assert(!hud_font_width(0) && !hud_font_height(0));
	assert(!hud_font_palette_matches(palette));
	assert(!hud_font_load(NULL));
	assert(!hud_font_load(base));
	hud_font_shutdown();
	assert(!hud_font_load(""));
	hud_font_shutdown();
	char long_path[1100]; memset(long_path, 'a', sizeof(long_path));
	long_path[sizeof(long_path) - 1] = '\0';
	assert(!hud_font_load(long_path));
	hud_font_shutdown();
	assert(hud_font_load(base) && !hud_font_ready());
	if (argc == 3 && !strcmp(argv[2], "source-reject"))
	{
		assert(!hud_font_source_matches(mapping, glyphs));
		assert(!hud_font_capture(source, 320, mapping, glyphs));
		assert(!hud_font_ready());
		hud_font_shutdown();
		puts("HUF1 bounded RLE rejects malformed source even with matching source pins.");
		return 0;
	}
	assert(hud_font_source_matches(mapping, glyphs));
	if (argc == 3 && !strcmp(argv[2], "capture-reject"))
	{
		assert(!hud_font_capture(source, 320, mapping, glyphs));
		assert(!hud_font_ready());
		hud_font_shutdown();
		puts("HUF1 capture rejects alpha outside actual verified glyph dimensions.");
		return 0;
	}
	assert(hud_font_palette_matches(palette));
	assert(!hud_font_palette_matches(NULL));
	palette[1] ^= 1;
	assert(!hud_font_palette_matches(palette));
	/* Capture is explicitly independent of the current normal palette. */
	assert(hud_font_capture(source, 320, mapping, glyphs) && hud_font_ready());
	palette[1] ^= 1;
	for (unsigned i = 0; i < 256; ++i)
	{
		palette[i] ^= 0x01000000u; /* Packed alpha is not part of RGB serialization. */
		assert(hud_font_palette_matches(palette));
		palette[i] ^= 1;
		assert(!hud_font_palette_matches(palette));
		palette[i] ^= 1;
	}
	unsigned long samples = 0;
	for (unsigned id = 0; id < 127; ++id)
	{
		assert(hud_font_width(id) == (id < 86 ? glyphs[id].width : 0));
		assert(hud_font_height(id) == (id < 86 ? glyphs[id].height : 0));
		for (int y = 0; y < glyphs[id].height * 4; ++y)
			for (int x = 0; x < glyphs[id].width * 4; ++x)
			{
				unsigned offset = ((id / 16) * 40 + 4 + (unsigned)y) * 512 +
				                  (id % 16) * 32 + 4 + (unsigned)x;
				uint8_t expected = id < 86 ? alpha[offset] : 0;
				assert(hud_font_alpha(id, x, y, 4) == expected); ++samples;
				for (int ry = 0; ry < 2; ++ry)
					for (int rx = 0; rx < 2; ++rx)
					{
						assert(hud_font_alpha(id, x * 2 + rx, y * 2 + ry, 8) == expected);
						++samples;
					}
			}
		for (int d = 4; d <= 8; d += 4)
		{
			assert(!hud_font_alpha(id, -1, 0, d) && !hud_font_alpha(id, 0, -1, d));
			assert(!hud_font_alpha(id, glyphs[id].width * d, 0, d));
			assert(!hud_font_alpha(id, 0, glyphs[id].height * d, d));
			assert(!hud_font_alpha(id, INT_MAX, INT_MAX, d));
		}
	}
	for (int d = -1; d < 16; ++d)
		if (d != 4 && d != 8) assert(!hud_font_alpha(0, 0, 0, d));
	assert(!hud_font_width(127) && !hud_font_height(UINT_MAX));
	assert(!hud_font_alpha(127, 0, 0, 4) && !hud_font_alpha(UINT_MAX, 0, 0, 8));
	unsigned mutations = 0;
	for (unsigned i = 0; i < 256; ++i)
	{
		int previous = mapping[i]; mapping[i] = previous == -1 ? 0 : -1;
		assert(!hud_font_source_matches(mapping, glyphs)); ++mutations;
		mapping[i] = previous;
	}
	mapping[0] = INT_MAX; assert(!hud_font_source_matches(mapping, glyphs));
	mapping[0] = INT_MIN; assert(!hud_font_source_matches(mapping, glyphs));
	mapping[0] = -1;
	for (unsigned id = 0; id < 127; ++id)
	{
		HudFontGlyph saved = glyphs[id];
		glyphs[id].width = 0; assert(!hud_font_source_matches(mapping, glyphs));
		glyphs[id] = saved; glyphs[id].height = 9;
		assert(!hud_font_source_matches(mapping, glyphs));
		glyphs[id] = saved; glyphs[id].size = UINT16_MAX;
		assert(!hud_font_source_matches(mapping, glyphs));
		glyphs[id] = saved; glyphs[id].data = NULL;
		assert(!hud_font_source_matches(mapping, glyphs));
		glyphs[id] = saved; mutations += 4;
		for (unsigned byte = 0; byte < glyphs[id].size; ++byte)
		{
			encoded[id][byte] ^= 1;
			assert(!hud_font_source_matches(mapping, glyphs)); ++mutations;
			encoded[id][byte] ^= 1;
		}
	}
	assert(hud_font_ready() && hud_font_source_matches(mapping, glyphs));
	assert(!hud_font_source_matches(NULL, glyphs) && !hud_font_source_matches(mapping, NULL));
	memset(padded, 0xe3, sizeof(padded));
	for (int y = 0; y < 200; ++y) memcpy(padded + y * 337, source + y * 320, 320);
	assert(hud_font_capture(padded, 337, mapping, glyphs));
	for (unsigned at = 0; at < 64000; at += 31999)
	{
		source[at] ^= 1;
		assert(!hud_font_capture(source, 320, mapping, glyphs) && !hud_font_ready());
		source[at] ^= 1;
	}
	assert(!hud_font_capture(source, 319, mapping, glyphs));
	assert(!hud_font_capture(NULL, 320, mapping, glyphs));
	assert(!hud_font_capture(source, 320, NULL, glyphs));
	assert(!hud_font_capture(source, 320, mapping, NULL));
	assert(hud_font_capture(source, 320, mapping, glyphs));
	/* Sampler owns dimensions/coverage only; subsequent source changes cannot
	 * change retained dimensions, and explicit revalidation detects them. */
	glyphs[0].width = 1; assert(hud_font_width(0) == 6);
	assert(!hud_font_source_matches(mapping, glyphs)); glyphs[0].width = 6;
	hud_font_forget_source();
	assert(!hud_font_ready() && !hud_font_width(0) && !hud_font_alpha(0, 4, 0, 4));
	assert(hud_font_source_matches(mapping, glyphs));
	assert(hud_font_capture(source, 320, mapping, glyphs));
	hud_font_shutdown(); hud_font_shutdown();
	unsigned invalid = 0;
	for (;; ++invalid)
	{
		snprintf(path, sizeof(path), "%s/bad-%u", base, invalid);
		char file[1300]; snprintf(file, sizeof(file), "%s/case", path);
		FILE *f = fopen(file, "rb"); if (!f) break; assert(!fclose(f));
		assert(!hud_font_load(path) && !hud_font_load(base));
		hud_font_shutdown();
	}
	assert(hud_font_load(base)); hud_font_shutdown();
	printf("HUF1 loader PASS: %u invalid resources, %u source mutations, %lu exact 4x/8x samples.\n",
	       invalid, mutations, samples);
	return 0;
}

#endif
