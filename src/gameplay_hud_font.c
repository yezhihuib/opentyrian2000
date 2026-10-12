/* Bounded optional HUF1 coverage. No original font or PIC3 bytes are shipped. */
#include "gameplay_hud_font.h"

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
/* Inspect the opened object. Nonblocking open keeps FIFO rejection bounded. */
#define HUD_OPEN(path) open(path, O_RDONLY | O_NONBLOCK)
#define HUD_READ read
#define HUD_CLOSE close
#define HUD_FSTAT fstat
#define HUD_STAT struct stat
#define HUD_REGULAR(mode) S_ISREG(mode)
#endif

/* Each pin is independently overridable by synthetic tests, never by the file. */
#ifndef HUD_FONT_PIC3_FNV
#define HUD_FONT_PIC3_FNV UINT64_C(0x14c1441f3d5dc0e2)
#endif
#ifndef HUD_FONT_PALETTE_FNV
#define HUD_FONT_PALETTE_FNV UINT64_C(0x5e80e83992be2927)
#endif
#ifndef HUD_FONT_MAP_FNV
#define HUD_FONT_MAP_FNV UINT64_C(0x845b16939661b466)
#endif
#ifndef HUD_FONT_METRICS_FNV
#define HUD_FONT_METRICS_FNV UINT64_C(0x0908ca85cbf2a1e3)
#endif
#ifndef HUD_FONT_ENCODED_FNV
#define HUD_FONT_ENCODED_FNV UINT64_C(0x2ed2973d82ce6f3d)
#endif
#ifndef HUD_FONT_ELIGIBLE_FNV
#define HUD_FONT_ELIGIBLE_FNV UINT64_C(0x68e8c2bab3c43d0d)
#endif

enum {
	SOURCE_WIDTH = 320, SOURCE_HEIGHT = 200,
	ATLAS_WIDTH = 512, ATLAS_HEIGHT = 320, DENSITY = 4,
	GLYPHS = 127, ELIGIBLE = 86, CELL_WIDTH = 32, CELL_HEIGHT = 40,
	INSET = 4, MAX_WIDTH = 6, MAX_HEIGHT = 8,
	HEADER_BYTES = 112, PAYLOAD_BYTES = 163840, FILE_BYTES = 163952
};

static bool attempted, captured;
static uint8_t *payload;
static uint8_t widths[GLYPHS], heights[GLYPHS];

static uint32_t read_u32(const uint8_t *p)
{
	return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
	       ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint64_t read_u64(const uint8_t *p)
{
	return (uint64_t)read_u32(p) | ((uint64_t)read_u32(p + 4) << 32);
}

static uint64_t fnv_update(uint64_t hash, const uint8_t *data, size_t size)
{
	for (size_t i = 0; i < size; ++i)
		hash = (hash ^ data[i]) * UINT64_C(1099511628211);
	return hash;
}

static uint64_t fnv_u16(uint64_t hash, uint16_t value)
{
	uint8_t bytes[2] = { (uint8_t)value, (uint8_t)(value >> 8) };
	return fnv_update(hash, bytes, sizeof(bytes));
}

static uint64_t fnv_u32(uint64_t hash, uint32_t value)
{
	uint8_t bytes[4] = { (uint8_t)value, (uint8_t)(value >> 8),
	                     (uint8_t)(value >> 16), (uint8_t)(value >> 24) };
	return fnv_update(hash, bytes, sizeof(bytes));
}

static bool valid_header(const uint8_t *header)
{
	static const uint32_t fields[11] = {
		1, DENSITY, ATLAS_WIDTH, ATLAS_HEIGHT, GLYPHS, ELIGIBLE,
		CELL_WIDTH, CELL_HEIGHT, INSET, PAYLOAD_BYTES, 7
	};
	if (memcmp(header, "HUF1", 4))
		return false;
	for (unsigned i = 0; i < 11; ++i)
		if (read_u32(header + 4 + i * 4) != fields[i])
			return false;
	return read_u64(header + 48) == HUD_FONT_PIC3_FNV &&
	       read_u64(header + 56) == HUD_FONT_PALETTE_FNV &&
	       read_u64(header + 64) == HUD_FONT_MAP_FNV &&
	       read_u64(header + 72) == HUD_FONT_METRICS_FNV &&
	       read_u64(header + 80) == HUD_FONT_ENCODED_FNV &&
	       read_u64(header + 96) == HUD_FONT_ELIGIBLE_FNV &&
	       read_u64(header + 104) == 0;
}

/* All 128 cells are checked. Before capture only the fixed maximum box is
 * known; capture additionally checks padding against each verified metric. */
static bool valid_padding(const uint8_t *data, const HudFontGlyph *glyphs)
{
	for (unsigned id = 0; id < 128; ++id)
	{
		unsigned w = id == GLYPHS ? 0 : glyphs ? glyphs[id].width : MAX_WIDTH;
		unsigned h = id == GLYPHS ? 0 : glyphs ? glyphs[id].height : MAX_HEIGHT;
		unsigned left = (id % 16) * CELL_WIDTH;
		unsigned top = (id / 16) * CELL_HEIGHT;
		for (unsigned y = 0; y < CELL_HEIGHT; ++y)
			for (unsigned x = 0; x < CELL_WIDTH; ++x)
				if ((x < INSET || y < INSET || x >= INSET + w * DENSITY ||
				     y >= INSET + h * DENSITY) &&
				    data[(top + y) * ATLAS_WIDTH + left + x])
					return false;
	}
	return true;
}

/* Short reads and interruptions fail closed, without unbounded retry loops. */
static bool read_exact(int file, uint8_t *data, unsigned size)
{
	return HUD_READ(file, data, size) == (long)size;
}

bool hud_font_load(const char *directory)
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
	length = snprintf(path, sizeof(path), "%s/gameplay-hud-font-v1.hda", directory);
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
	valid = fnv_update(UINT64_C(14695981039346656037), data, PAYLOAD_BYTES) ==
	        read_u64(header + 88) && valid_padding(data, NULL);

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

/* This models the original row-boundary commands without drawing or retaining
 * pixels. The stream may end early (implicit transparent tail); every command
 * and count byte must be in bounds. The independently pinned hash still has
 * to match the complete original encoded stream. */
static bool valid_glyph(const HudFontGlyph *glyph)
{
	unsigned x = 0, y = 0;
	if (!glyph->width || glyph->width > MAX_WIDTH || !glyph->height ||
	    glyph->height > MAX_HEIGHT || !glyph->size || !glyph->data ||
	    glyph->size > 2 * glyph->width * glyph->height + glyph->height)
		return false;
	for (unsigned i = 0; i < glyph->size; ++i)
	{
		unsigned step = 1;
		if (y >= glyph->height)
			return false;
		if (glyph->data[i] == 255)
		{
			if (++i >= glyph->size)
				return false;
			step = glyph->data[i];
		}
		else if (glyph->data[i] == 254)
			step = glyph->width - x;
		if (step > glyph->width - x)
			return false;
		x += step;
		if (x == glyph->width)
		{
			x = 0;
			++y;
		}
	}
	return true;
}

bool hud_font_source_matches(const int map[256], const HudFontGlyph glyphs[127])
{
	uint64_t map_hash = UINT64_C(14695981039346656037);
	uint64_t metrics_hash = UINT64_C(14695981039346656037);
	uint64_t encoded_hash = fnv_u32(UINT64_C(14695981039346656037), GLYPHS);
	uint64_t eligible_hash = UINT64_C(14695981039346656037);
	if (!payload || !map || !glyphs)
		return false;
	for (unsigned i = 0; i < 256; ++i)
	{
		if (map[i] < -1 || map[i] >= GLYPHS)
			return false;
		map_hash = fnv_u32(map_hash, (uint32_t)map[i]);
	}
	if (map_hash != HUD_FONT_MAP_FNV)
		return false;
	for (unsigned id = 0; id < GLYPHS; ++id)
	{
		const HudFontGlyph *glyph = &glyphs[id];
		uint8_t eligible = id < ELIGIBLE ? 255 : 0;
		if (!valid_glyph(glyph))
			return false;
		metrics_hash = fnv_u16(metrics_hash, glyph->width);
		metrics_hash = fnv_u16(metrics_hash, glyph->height);
		metrics_hash = fnv_u16(metrics_hash, glyph->width + 1);
		encoded_hash = fnv_u16(encoded_hash, glyph->width);
		encoded_hash = fnv_u16(encoded_hash, glyph->height);
		encoded_hash = fnv_u16(encoded_hash, glyph->size);
		encoded_hash = fnv_update(encoded_hash, glyph->data, glyph->size);
		eligible_hash = fnv_update(eligible_hash, &eligible, 1);
	}
	return metrics_hash == HUD_FONT_METRICS_FNV &&
	       encoded_hash == HUD_FONT_ENCODED_FNV &&
	       eligible_hash == HUD_FONT_ELIGIBLE_FNV;
}

bool hud_font_capture(const uint8_t *indices, int pitch, const int map[256],
                      const HudFontGlyph glyphs[127])
{
	uint64_t hash = UINT64_C(14695981039346656037);
	hud_font_forget_source();
	if (!indices || pitch < SOURCE_WIDTH ||
	    (size_t)pitch > (SIZE_MAX - SOURCE_WIDTH) / (SOURCE_HEIGHT - 1) ||
	    !hud_font_source_matches(map, glyphs))
		return false;
	for (int y = 0; y < SOURCE_HEIGHT; ++y)
		hash = fnv_update(hash, indices + (size_t)y * (size_t)pitch, SOURCE_WIDTH);
	if (hash != HUD_FONT_PIC3_FNV || !valid_padding(payload, glyphs))
		return false;
	for (unsigned id = 0; id < GLYPHS; ++id)
	{
		widths[id] = (uint8_t)glyphs[id].width;
		heights[id] = (uint8_t)glyphs[id].height;
	}
	captured = true;
	return true;
}

bool hud_font_palette_matches(const uint32_t packed_rgb[256])
{
	uint64_t hash = UINT64_C(14695981039346656037);
	if (!payload || !packed_rgb)
		return false;
	for (unsigned i = 0; i < 256; ++i)
	{
		uint8_t rgb[3] = { (uint8_t)(packed_rgb[i] >> 16),
		                   (uint8_t)(packed_rgb[i] >> 8), (uint8_t)packed_rgb[i] };
		hash = fnv_update(hash, rgb, sizeof(rgb));
	}
	return hash == HUD_FONT_PALETTE_FNV;
}

bool hud_font_ready(void)
{
	return payload && captured;
}

void hud_font_forget_source(void)
{
	captured = false;
	memset(widths, 0, sizeof(widths));
	memset(heights, 0, sizeof(heights));
}

void hud_font_shutdown(void)
{
	hud_font_forget_source();
	free(payload);
	payload = NULL;
	attempted = false;
}

int hud_font_width(unsigned id)
{
	return hud_font_ready() && id < ELIGIBLE ? widths[id] : 0;
}

int hud_font_height(unsigned id)
{
	return hud_font_ready() && id < ELIGIBLE ? heights[id] : 0;
}

uint8_t hud_font_alpha(unsigned id, int xsub, int ysub, int density)
{
	if (!hud_font_ready() || id >= ELIGIBLE || (density != 4 && density != 8) ||
	    xsub < 0 || ysub < 0 || xsub >= widths[id] * density ||
	    ysub >= heights[id] * density)
		return 0;
	unsigned x = (id % 16) * CELL_WIDTH + INSET + (unsigned)(xsub / (density / 4));
	unsigned y = (id / 16) * CELL_HEIGHT + INSET + (unsigned)(ysub / (density / 4));
	return payload[y * ATLAS_WIDTH + x];
}
