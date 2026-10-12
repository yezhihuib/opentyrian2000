/* Bounded HUL1 indicators: only authored RGBA and 453 runtime-captured source
 * indices are retained. Unsupported input always leaves classic output. */
#include "gameplay_hud_indicators.h"

#include <fcntl.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#if defined(TARGET_WIN32) || defined(_WIN32)
#include <io.h>
#define HUD_OPEN(path) _open(path, _O_RDONLY | _O_BINARY | _O_NOINHERIT)
#define HUD_READ _read
#define HUD_CLOSE _close
#define HUD_FSTAT _fstat
#define HUD_STAT struct _stat
#define HUD_REGULAR(mode) (((mode) & _S_IFMT) == _S_IFREG)
#else
#include <unistd.h>
/* Check the opened object. Nonblocking open also keeps FIFOs bounded. */
#define HUD_OPEN(path) open(path, O_RDONLY | O_NONBLOCK)
#define HUD_READ read
#define HUD_CLOSE close
#define HUD_FSTAT fstat
#define HUD_STAT struct stat
#define HUD_REGULAR(mode) S_ISREG(mode)
#endif

/* These source guards are a separate, fixed integration contract. Synthetic
 * tests override constants at compile time without bundling original indices. */
#ifndef HUD_INDICATORS_PIC3_FNV
#define HUD_INDICATORS_PIC3_FNV UINT64_C(0x14c1441f3d5dc0e2)
#endif
#ifndef HUD_INDICATORS_PALETTE_FNV
#define HUD_INDICATORS_PALETTE_FNV UINT64_C(0x5e80e83992be2927)
#endif
#ifndef HUD_INDICATORS_TOP_FNV
#define HUD_INDICATORS_TOP_FNV UINT64_C(0x328ef0a75cce2260)
#endif
#ifndef HUD_INDICATORS_MODE1_FNV
#define HUD_INDICATORS_MODE1_FNV UINT64_C(0x55f78c15a1ce495a)
#endif
#ifndef HUD_INDICATORS_MODE2_FNV
#define HUD_INDICATORS_MODE2_FNV UINT64_C(0xf7a97c521d045d18)
#endif
#ifndef HUD_INDICATORS_OPTION18_FNV
#define HUD_INDICATORS_OPTION18_FNV UINT64_C(0xd36b9afd4df898cf)
#endif
#ifndef HUD_INDICATORS_OPTION19_FNV
#define HUD_INDICATORS_OPTION19_FNV UINT64_C(0xac3fca9154ec0310)
#endif

enum {
	SOURCE_WIDTH = 320, SOURCE_HEIGHT = 200, DENSITY = 4,
	HEADER_BYTES = 80, TOP_BYTES = 1344, MODE_BYTES = 13824,
	PAYLOAD_BYTES = TOP_BYTES + 2 * MODE_BYTES,
	FILE_BYTES = HEADER_BYTES + PAYLOAD_BYTES,
	TOP_LEFT = 269, TOP_TOP = 4, TOP_WIDTH = 7, TOP_HEIGHT = 3,
	MODE_LEFT = 285, MODE_TOP = 44, MODE_WIDTH = 27, MODE_HEIGHT = 8,
	TOP_SOURCE_BYTES = TOP_WIDTH * TOP_HEIGHT,
	MODE_SOURCE_BYTES = MODE_WIDTH * MODE_HEIGHT,
	SPRITE_WIDTH = 10, SPRITE_BYTES = 80
};

static bool attempted, captured;
static uint8_t *payload;
static uint8_t top_indices[TOP_SOURCE_BYTES], mode_indices[2][MODE_SOURCE_BYTES];
static int recorded_mode;

static uint32_t read_u32(const uint8_t *p)
{
	return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
	       ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint64_t read_u64(const uint8_t *p)
{
	return (uint64_t)read_u32(p) | ((uint64_t)read_u32(p + 4) << 32);
}

static uint64_t fnv_update(uint64_t hash, const uint8_t *bytes, size_t count)
{
	for (size_t i = 0; i < count; ++i)
		hash = (hash ^ bytes[i]) * UINT64_C(1099511628211);
	return hash;
}

static uint64_t fnv64(const uint8_t *bytes, size_t count)
{
	return fnv_update(UINT64_C(14695981039346656037), bytes, count);
}

static bool valid_header(const uint8_t *header)
{
	return !memcmp(header, "HUL1", 4) && read_u32(header + 4) == 1 &&
	       read_u32(header + 8) == DENSITY &&
	       read_u32(header + 12) == TOP_WIDTH * DENSITY &&
	       read_u32(header + 16) == TOP_HEIGHT * DENSITY &&
	       read_u32(header + 20) == MODE_WIDTH * DENSITY &&
	       read_u32(header + 24) == MODE_HEIGHT * DENSITY &&
	       read_u32(header + 28) == PAYLOAD_BYTES &&
	       read_u64(header + 32) == HUD_INDICATORS_PIC3_FNV &&
	       read_u64(header + 40) == HUD_INDICATORS_PALETTE_FNV &&
	       read_u64(header + 48) == HUD_INDICATORS_TOP_FNV &&
	       read_u64(header + 56) == HUD_INDICATORS_MODE1_FNV &&
	       read_u64(header + 64) == HUD_INDICATORS_MODE2_FNV;
}

static bool valid_payload(const uint8_t *data, const uint8_t *header)
{
	if (fnv64(data, PAYLOAD_BYTES) != read_u64(header + 72))
		return false;
	for (size_t i = 3; i < PAYLOAD_BYTES; i += 4)
		if (data[i] != 255)
			return false;
	return true;
}

/* Each request fits _read's unsigned count. Short reads and interruptions fail
 * closed rather than introducing an unbounded retry loop. */
static bool read_exact(int file, uint8_t *data, unsigned count)
{
	return HUD_READ(file, data, count) == (long)count;
}

bool hud_indicators_load(const char *directory)
{
	char path[1024];
	uint8_t header[HEADER_BYTES], extra;
	HUD_STAT status;
	uint8_t *data = NULL;
	bool valid = false;
	int length, file;

	if (attempted)
		return payload != NULL;
	attempted = true;
	if (!directory || !*directory)
		return false;
	length = snprintf(path, sizeof(path), "%s/gameplay-hud-indicators-v1.hda", directory);
	if (length < 0 || (size_t)length >= sizeof(path))
		return false;
	file = HUD_OPEN(path);
	if (file < 0)
		return false;
	if (HUD_FSTAT(file, &status) || !HUD_REGULAR(status.st_mode) ||
	    status.st_size != FILE_BYTES ||
	    !read_exact(file, header, sizeof(header)) || !valid_header(header))
		goto done;
	data = malloc(PAYLOAD_BYTES);
	if (!data || !read_exact(file, data, PAYLOAD_BYTES) ||
	    HUD_READ(file, &extra, 1) != 0)
		goto done;
	valid = valid_payload(data, header);

done:
	if (HUD_CLOSE(file))
		valid = false;
	if (!valid)
	{
		free(data);
		return false;
	}
	payload = data;
	return true;
}

static bool valid_source(const uint8_t *indices, int pitch)
{
	return indices && pitch >= SOURCE_WIDTH &&
	       (size_t)pitch <= (SIZE_MAX - SOURCE_WIDTH) / (SOURCE_HEIGHT - 1);
}

bool hud_indicators_verify_modes(const uint8_t sprites[2][80],
                                 const uint8_t opaque[2][80])
{
	if (!payload || !sprites || !opaque ||
	    fnv64(sprites[0], SPRITE_BYTES) != HUD_INDICATORS_OPTION18_FNV ||
	    fnv64(sprites[1], SPRITE_BYTES) != HUD_INDICATORS_OPTION19_FNV)
		return false;
	for (int mode = 0; mode < 2; ++mode)
		for (int i = 0; i < SPRITE_BYTES; ++i)
			if (opaque[mode][i] != 255)
				return false;
	return true;
}

bool hud_indicators_capture(const uint8_t *indices, int pitch,
                            const uint8_t sprites[2][80],
                            const uint8_t opaque[2][80])
{
	uint64_t hash = UINT64_C(14695981039346656037);

	hud_indicators_forget_source();
	if (!valid_source(indices, pitch) || !hud_indicators_verify_modes(sprites, opaque))
		return false;
	for (int y = 0; y < SOURCE_HEIGHT; ++y)
		hash = fnv_update(hash, indices + (size_t)y * (size_t)pitch, SOURCE_WIDTH);
	if (hash != HUD_INDICATORS_PIC3_FNV)
		return false;
	for (int y = 0; y < TOP_HEIGHT; ++y)
		memcpy(top_indices + y * TOP_WIDTH,
		       indices + (size_t)(TOP_TOP + y) * (size_t)pitch + TOP_LEFT, TOP_WIDTH);
	if (fnv64(top_indices, sizeof(top_indices)) != HUD_INDICATORS_TOP_FNV)
		return false;
	for (int mode = 0; mode < 2; ++mode)
		for (int y = 0; y < MODE_HEIGHT; ++y)
		{
			uint8_t *row = mode_indices[mode] + y * MODE_WIDTH;
			memcpy(row, indices + (size_t)(MODE_TOP + y) * (size_t)pitch + MODE_LEFT, MODE_WIDTH);
			memcpy(row, sprites[mode] + y * SPRITE_WIDTH, SPRITE_WIDTH);
			memcpy(row + MODE_WIDTH - SPRITE_WIDTH, sprites[1 - mode] + y * SPRITE_WIDTH, SPRITE_WIDTH);
		}
	if (fnv64(mode_indices[0], MODE_SOURCE_BYTES) != HUD_INDICATORS_MODE1_FNV ||
	    fnv64(mode_indices[1], MODE_SOURCE_BYTES) != HUD_INDICATORS_MODE2_FNV)
		return false;
	captured = true;
	return true;
}

bool hud_indicators_ready(void)
{
	return payload != NULL && captured;
}

bool hud_indicators_palette_matches(const uint32_t packed_rgb[256])
{
	uint64_t hash = UINT64_C(14695981039346656037);
	if (!payload || !packed_rgb)
		return false;
	for (int i = 0; i < 256; ++i)
	{
		uint8_t rgb[3] = {(uint8_t)(packed_rgb[i] >> 16),
		                  (uint8_t)(packed_rgb[i] >> 8), (uint8_t)packed_rgb[i]};
		hash = fnv_update(hash, rgb, sizeof(rgb));
	}
	return hash == HUD_INDICATORS_PALETTE_FNV;
}

void hud_indicators_mode_drawn(int mode)
{
	recorded_mode = hud_indicators_ready() && (mode == 1 || mode == 2) ? mode : 0;
}

void hud_indicators_mode_wiped(void)
{
	recorded_mode = 0;
}

bool hud_indicators_mode_ready(void)
{
	return hud_indicators_ready() && recorded_mode != 0;
}

static bool rectangle_matches(const uint8_t *indices, int pitch,
                               const uint8_t *expected, int x, int y,
                               int width, int height)
{
	if (!valid_source(indices, pitch))
		return false;
	for (int row = 0; row < height; ++row)
		if (memcmp(indices + (size_t)(y + row) * (size_t)pitch + x,
		           expected + row * width, (size_t)width))
			return false;
	return true;
}

bool hud_indicators_mode_matches(const uint8_t *indices, int pitch)
{
	return hud_indicators_mode_ready() &&
	       rectangle_matches(indices, pitch, mode_indices[recorded_mode - 1],
	                         MODE_LEFT, MODE_TOP, MODE_WIDTH, MODE_HEIGHT);
}

bool hud_indicators_top_matches(const uint8_t *indices, int pitch)
{
	return hud_indicators_ready() &&
	       rectangle_matches(indices, pitch, top_indices,
	                         TOP_LEFT, TOP_TOP, TOP_WIDTH, TOP_HEIGHT);
}

const uint8_t *hud_indicators_sample(int x, int y, int sx, int sy,
                                    int density, uint8_t current_index)
{
	int dx, dy, width, divisor;
	size_t offset, pixel;
	const uint8_t *expected;
	if (!hud_indicators_ready() || (density != DENSITY && density != 2 * DENSITY) ||
	    sx < 0 || sx >= density || sy < 0 || sy >= density)
		return NULL;
	if (x >= TOP_LEFT && x < TOP_LEFT + TOP_WIDTH &&
	    y >= TOP_TOP && y < TOP_TOP + TOP_HEIGHT)
	{
		dx = x - TOP_LEFT; dy = y - TOP_TOP; width = TOP_WIDTH;
		expected = top_indices; offset = 0;
	}
	else if (hud_indicators_mode_ready() &&
	         x >= MODE_LEFT && x < MODE_LEFT + MODE_WIDTH &&
	         y >= MODE_TOP && y < MODE_TOP + MODE_HEIGHT)
	{
		dx = x - MODE_LEFT; dy = y - MODE_TOP; width = MODE_WIDTH;
		expected = mode_indices[recorded_mode - 1];
		offset = TOP_BYTES + (size_t)(recorded_mode - 1) * MODE_BYTES;
	}
	else
		return NULL;
	if (current_index != expected[dy * width + dx])
		return NULL;
	divisor = density / DENSITY;
	pixel = (size_t)(dy * DENSITY + sy / divisor) * width * DENSITY +
	        (size_t)(dx * DENSITY + sx / divisor);
	return payload + offset + pixel * 4;
}

void hud_indicators_forget_source(void)
{
	captured = false;
	recorded_mode = 0;
}

void hud_indicators_shutdown(void)
{
	free(payload);
	payload = NULL;
	hud_indicators_forget_source();
	attempted = false;
}
