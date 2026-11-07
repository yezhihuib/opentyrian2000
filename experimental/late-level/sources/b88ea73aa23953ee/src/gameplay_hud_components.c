/* Bounded HUC1 components. Only metadata, authored RGBA, and 350 runtime-captured
 * source indices are retained. Unsupported input always leaves classic output. */
#include "gameplay_hud_components.h"

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
/* Nonblocking open prevents a named pipe from hanging before the descriptor's
 * regular-file check. fstat checks the actual opened object, not a prior path. */
#define HUD_OPEN(path) open(path, O_RDONLY | O_NONBLOCK)
#define HUD_READ read
#define HUD_CLOSE close
#define HUD_FSTAT fstat
#define HUD_STAT struct stat
#define HUD_REGULAR(mode) S_ISREG(mode)
#endif

enum {
	SOURCE_WIDTH = 320, SOURCE_HEIGHT = 200, DENSITY = 4,
	HEADER_BYTES = 64, LABEL_BYTES = 22400, BAND_BYTES = 16128,
	PAYLOAD_BYTES = LABEL_BYTES + BAND_BYTES,
	FILE_BYTES = HEADER_BYTES + PAYLOAD_BYTES,
	LABEL_COUNT = 4, LABEL_HEIGHT = 5, LABEL_SOURCE_BYTES = 350,
	BAND_COUNT = 14, BAND_WIDTH = 36, BAND_HEIGHT = 8,
	SHIELD_LEFT = 270, SHIELD_TOP = 137,
	SHIELD_RIGHT = 279, SHIELD_BOTTOM = 195
};

static const struct {
	int x, y, width;
	size_t source_offset;
} labels[LABEL_COUNT] = {
	{285, 5, 24, 0}, {285, 11, 14, 120},
	{285, 26, 18, 190}, {285, 32, 14, 280}
};

static bool attempted, captured, shield_stamped;
static uint8_t *payload;
static uint8_t label_indices[LABEL_SOURCE_BYTES];
static uint64_t source_hash, palette_hash;
static int recorded_shield, recorded_maximum;

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
	return !memcmp(header, "HUC1", 4) && read_u32(header + 4) == 1 &&
	       read_u32(header + 8) == DENSITY &&
	       read_u32(header + 12) == LABEL_COUNT &&
	       read_u32(header + 16) == LABEL_BYTES &&
	       read_u32(header + 20) == BAND_COUNT &&
	       read_u32(header + 24) == BAND_WIDTH &&
	       read_u32(header + 28) == BAND_HEIGHT;
}

static bool valid_payload(const uint8_t *data, const uint8_t *header)
{
	if (fnv64(data, LABEL_BYTES) != read_u64(header + 40) ||
	    fnv64(data + LABEL_BYTES, BAND_BYTES) != read_u64(header + 48))
		return false;
	for (size_t i = 3; i < PAYLOAD_BYTES; i += 4)
		if (data[i] != 255)
			return false;
	return true;
}

/* Every request is at most 38528 bytes, including on _read's unsigned-int API.
 * Interruptions and short reads fail closed; no unbounded retry loop. */
static bool read_exact(int file, uint8_t *data, unsigned count)
{
	return HUD_READ(file, data, count) == (long)count;
}

bool hud_components_load(const char *directory)
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
	length = snprintf(path, sizeof(path), "%s/gameplay-hud-components-v1.hda", directory);
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
	source_hash = read_u64(header + 32);
	palette_hash = read_u64(header + 56);
	return true;
}

static bool valid_source(const uint8_t *indices, int pitch)
{
	return indices && pitch >= SOURCE_WIDTH &&
	       (size_t)pitch <= (SIZE_MAX - SOURCE_WIDTH) / (SOURCE_HEIGHT - 1);
}

bool hud_components_capture(const uint8_t *indices, int pitch)
{
	uint64_t hash = UINT64_C(14695981039346656037);
	hud_components_forget_source();
	if (!payload || !valid_source(indices, pitch))
		return false;
	for (int y = 0; y < SOURCE_HEIGHT; ++y)
		hash = fnv_update(hash, indices + (size_t)y * (size_t)pitch, SOURCE_WIDTH);
	if (hash != source_hash)
		return false;
	for (int y = SHIELD_TOP; y < SHIELD_BOTTOM; ++y)
		for (int x = SHIELD_LEFT; x < SHIELD_RIGHT; ++x)
			if (indices[(size_t)y * (size_t)pitch + (size_t)x] != 0)
				return false;
	for (size_t i = 0; i < LABEL_COUNT; ++i)
		for (int y = 0; y < LABEL_HEIGHT; ++y)
			memcpy(label_indices + labels[i].source_offset + y * labels[i].width,
			       indices + (size_t)(labels[i].y + y) * (size_t)pitch + labels[i].x,
			       (size_t)labels[i].width);
	captured = true;
	return true;
}

bool hud_components_ready(void)
{
	return payload != NULL && captured;
}

bool hud_components_palette_matches(const uint32_t packed_rgb[256])
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
	return hash == palette_hash;
}

static bool valid_sample(int sx, int sy, int density)
{
	return (density == DENSITY || density == 2 * DENSITY) &&
	       sx >= 0 && sx < density && sy >= 0 && sy < density;
}

const uint8_t *hud_components_label_sample(int x, int y, int sx, int sy,
                                          int density, uint8_t current_index)
{
	if (!hud_components_ready() || !valid_sample(sx, sy, density))
		return NULL;
	for (size_t i = 0; i < LABEL_COUNT; ++i)
	{
		int dx, dy, divisor;
		size_t pixel;
		if (x < labels[i].x || x >= labels[i].x + labels[i].width ||
		    y < labels[i].y || y >= labels[i].y + LABEL_HEIGHT)
			continue;
		dx = x - labels[i].x;
		dy = y - labels[i].y;
		if (current_index != label_indices[labels[i].source_offset + dy * labels[i].width + dx])
			return NULL;
		divisor = density / DENSITY;
		pixel = labels[i].source_offset * DENSITY * DENSITY +
		        (size_t)(dy * DENSITY + sy / divisor) * labels[i].width * DENSITY +
		        (size_t)(dx * DENSITY + sx / divisor);
		return payload + pixel * 4;
	}
	return NULL;
}

void hud_components_shield_drawn(int shield, int maximum)
{
	shield_stamped = false;
	if (!hud_components_ready() || shield < 0 || maximum < shield || maximum > 28)
		return;
	recorded_shield = shield;
	recorded_maximum = maximum;
	shield_stamped = true;
}

void hud_components_shield_wiped(void)
{
	shield_stamped = false;
}

bool hud_components_shield_ready(void)
{
	return hud_components_ready() && shield_stamped;
}

static uint8_t shield_index(int y)
{
	int z = (194 - y) / 2;
	if (recorded_shield != recorded_maximum && y == 193 - 2 * recorded_maximum)
		return 68;
	if (z > recorded_shield)
		return 0;
	return (uint8_t)(146 + (z > 1 ? (z - 1) / 2 : 0));
}

bool hud_components_shield_matches(const uint8_t *indices, int pitch)
{
	if (!hud_components_shield_ready() || !valid_source(indices, pitch))
		return false;
	for (int y = SHIELD_TOP; y < SHIELD_BOTTOM; ++y)
	{
		uint8_t expected = shield_index(y);
		for (int x = SHIELD_LEFT; x < SHIELD_RIGHT; ++x)
			if (indices[(size_t)y * (size_t)pitch + (size_t)x] != expected)
				return false;
	}
	return true;
}

const uint8_t *hud_components_shield_sample(int x, int y, int sx, int sy,
                                           int density, uint8_t current_index)
{
	uint8_t expected;
	int divisor;
	size_t pixel;
	if (!hud_components_shield_ready() || !valid_sample(sx, sy, density) ||
	    x < SHIELD_LEFT || x >= SHIELD_RIGHT || y < SHIELD_TOP || y >= SHIELD_BOTTOM)
		return NULL;
	expected = shield_index(y);
	if (expected < 146 || expected > 159 || current_index != expected)
		return NULL;
	divisor = density / DENSITY;
	pixel = (size_t)(expected - 146) * BAND_WIDTH * BAND_HEIGHT +
	        (size_t)(((y - SHIELD_TOP) % 2) * DENSITY + sy / divisor) * BAND_WIDTH +
	        (size_t)((x - SHIELD_LEFT) * DENSITY + sx / divisor);
	return payload + LABEL_BYTES + pixel * 4;
}

void hud_components_forget_source(void)
{
	captured = false;
	shield_stamped = false;
}

void hud_components_shutdown(void)
{
	free(payload);
	payload = NULL;
	source_hash = palette_hash = 0;
	recorded_shield = recorded_maximum = 0;
	hud_components_forget_source();
	attempted = false;
}
