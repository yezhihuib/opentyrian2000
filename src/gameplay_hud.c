/* Finite, optional asset-only HUD replacement. Unsupported or corrupt assets
 * leave all classic rendering untouched. No allocation or I/O during sampling. */
#include "gameplay_hud.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#if defined(TARGET_WIN32) || defined(_WIN32)
#ifndef S_ISREG
#define S_ISREG(mode) (((mode) & _S_IFMT) == _S_IFREG)
#endif
#endif

enum {
	HUD_WIDTH = 320, HUD_HEIGHT = 200, HUD_DENSITY = 4,
	HUD_PIXELS = 64000, HUD_RGBA_WIDTH = 1280,
	HUD_RGBA_BYTES = 4096000, HUD_HEADER_BYTES = 64,
	HUD_PAYLOAD_BYTES = HUD_PIXELS + HUD_RGBA_BYTES,
	HUD_FILE_BYTES = HUD_HEADER_BYTES + HUD_PAYLOAD_BYTES,
	HUD_MAX_OWNED_PIXELS = 6667, HUD_CORNER_OWNED_PIXELS = 6853
};

/* Geometry only, not an artwork identity: V5 union [248,184,269,200).
 * 6853 cells; SHA256 of the 64000-byte 0/255 mask:
 * dfc1e98e0d25b1a45645fc572d42396cf0407db975e44b3aefe91662255811b8.
 * A different/partial mask never receives the corner exception. */
#define HUD_CORNER_MASK_FNV UINT64_C(0xb0f84ef16e11c6a2)
#ifndef HUD_CORNER_PIC3_FNV
#define HUD_CORNER_PIC3_FNV UINT64_C(0x14c1441f3d5dc0e2)
#endif
#ifndef HUD_CORNER_REGION_FNV
#define HUD_CORNER_REGION_FNV UINT64_C(0xca5548b4cdd8767a)
#endif

static bool attempted, captured, expansion, corner, corner_ready;
static uint8_t *payload;
static uint8_t source_indices[HUD_PIXELS];
static uint64_t source_fnv64;

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

uint64_t gameplay_hud_fnv64(const uint8_t *bytes, size_t count)
{
	return fnv_update(UINT64_C(14695981039346656037), bytes, count);
}

static bool corner_pixel(int x, int y)
{
	return x >= 248 && x < 269 && y >= 184 && y < 200;
}

static uint64_t corner_source_fnv(const uint8_t *indices, int pitch)
{
	uint64_t hash = UINT64_C(14695981039346656037);
	for (int y = 184; y < 200; ++y)
		hash = fnv_update(hash, indices + (size_t)y * (size_t)pitch + 248, 21);
	return hash;
}

/* Exact coordinate-only expansion: 310 approved rail/bevel pixels. Each
 * half-open rectangle is a span (adjacent identical spans are coalesced).
 * Reconstructed 64000-byte 0/255 mask SHA256:
 * 903328448558ea0a8b7ea1e895339602736664bad73b0828b8ace4b3732263d2.
 * No color or source-index predicate may enlarge this finite allowlist. */
static bool expanded_pixel(int x, int y)
{
	static const uint16_t spans[][4] = {
		{268, 10, 279, 11},
		{285, 44, 287, 45},
		{289, 44, 290, 45},
		{292, 44, 295, 45},
		{302, 44, 304, 45},
		{306, 44, 307, 45},
		{309, 44, 312, 45},
		{293, 45, 294, 46},
		{310, 45, 311, 46},
		{302, 49, 303, 50},
		{292, 50, 294, 51},
		{303, 50, 304, 51},
		{309, 50, 311, 51},
		{286, 51, 287, 52},
		{293, 51, 295, 52},
		{302, 51, 304, 52},
		{310, 51, 311, 52},
		{312, 59, 313, 60},
		{283, 63, 284, 64},
		{311, 63, 313, 64},
		{283, 79, 284, 80},
		{283, 80, 313, 81},
		{283, 81, 285, 82},
		{312, 81, 313, 82},
		{283, 98, 284, 99},
		{311, 98, 313, 99},
		{268, 105, 269, 107},
		{278, 105, 279, 106},
		{277, 106, 279, 107},
		{268, 107, 279, 108},
		{267, 115, 268, 116},
		{315, 115, 320, 116},
		{316, 116, 320, 118},
		{267, 126, 268, 127},
		{315, 126, 320, 127},
		{267, 127, 320, 128},
		{270, 134, 279, 136},
		{307, 134, 316, 136},
		{270, 136, 271, 137},
		{277, 136, 279, 137},
		{290, 136, 292, 137},
		{294, 136, 296, 137},
		{291, 137, 292, 175},
		{294, 137, 295, 175},
		{301, 174, 302, 175},
		{284, 175, 285, 176},
		{290, 175, 292, 176},
		{294, 175, 296, 176},
		{300, 175, 302, 176},
		{284, 176, 292, 177},
		{294, 176, 302, 177},
	};
	for (size_t i = 0; i < sizeof(spans) / sizeof(spans[0]); ++i)
		if (x >= spans[i][0] && y >= spans[i][1] &&
		    x < spans[i][2] && y < spans[i][3])
			return true;
	return false;
}

/* Half-open original-display coordinates for the unchanged base geometry.
 * Only the exact expanded_pixel allowlist may cross these holes; labels,
 * meters, changing icons and messages otherwise remain classic. */
static bool allowed_pixel(int x, int y)
{
	static const int holes[][4] = {
		{268, 10, 279, 108}, /* generator window */
		{284, 4, 312, 21},   /* front label and power */
		{284, 25, 312, 41},  /* rear label and power */
		{285, 44, 295, 52},  /* rear mode, left */
		{302, 44, 312, 52},  /* rear mode, right */
		{284, 53, 313, 60},  /* mode label */
		{283, 63, 313, 99},  /* sidekick icons and ammo */
		{267, 115, 320, 128},/* level name */
		{270, 134, 279, 195},/* shield window and capacity */
		{307, 134, 316, 195},/* armor window */
		{284, 136, 292, 177},/* static shield label */
		{294, 136, 302, 177},/* static armor label */
		{269, 3, 277, 8},    /* top red lamp */
		{16, 189, 264, 200}  /* message sprite and text */
	};
	if (x < 264 && y < 184)
		return false;
	for (size_t i = 0; i < sizeof(holes) / sizeof(holes[0]); ++i)
		if (x >= holes[i][0] && y >= holes[i][1] &&
		    x < holes[i][2] && y < holes[i][3])
			return false;
	return true;
}

static bool valid_header(const uint8_t header[HUD_HEADER_BYTES])
{
	return !memcmp(header, "HUD1", 4) && read_u32(header + 4) == 1 &&
	       read_u32(header + 8) == HUD_WIDTH &&
	       read_u32(header + 12) == HUD_HEIGHT &&
	       read_u32(header + 16) == HUD_DENSITY &&
	       read_u32(header + 20) == 0 && read_u32(header + 24) == 0 &&
	       read_u32(header + 28) == HUD_PIXELS &&
	       read_u32(header + 32) == HUD_RGBA_BYTES &&
	       read_u32(header + 60) == 0;
}

static bool valid_payload(const uint8_t *data, const uint8_t *header)
{
	unsigned owned = 0;
	const uint8_t *rgba = data + HUD_PIXELS;
	uint64_t mask_hash = gameplay_hud_fnv64(data, HUD_PIXELS);
	bool corner_mask = mask_hash == HUD_CORNER_MASK_FNV;
	if (mask_hash != read_u64(header + 44) ||
	    gameplay_hud_fnv64(rgba, HUD_RGBA_BYTES) != read_u64(header + 52))
		return false;
	if (corner_mask && read_u64(header + 36) != HUD_CORNER_PIC3_FNV)
		return false;
	for (int y = 0; y < HUD_HEIGHT; ++y)
	{
		for (int x = 0; x < HUD_WIDTH; ++x)
		{
			uint8_t mask = data[y * HUD_WIDTH + x];
			if (mask != 0 && mask != 255)
				return false;
			if (corner_mask && corner_pixel(x, y) && mask != 255)
				return false;
			if (mask && ((!allowed_pixel(x, y) && !expanded_pixel(x, y) &&
			              !(corner_mask && corner_pixel(x, y))) ||
			             ++owned > (corner_mask ? HUD_CORNER_OWNED_PIXELS : HUD_MAX_OWNED_PIXELS)))
				return false;
			for (int sy = 0; sy < HUD_DENSITY; ++sy)
				for (int sx = 0; sx < HUD_DENSITY; ++sx)
				{
					size_t index = (size_t)((y * HUD_DENSITY + sy) * HUD_RGBA_WIDTH +
					                         x * HUD_DENSITY + sx) * 4;
					if (rgba[index + 3] != mask)
						return false;
				}
		}
	}
	return corner_mask ? owned == HUD_CORNER_OWNED_PIXELS : owned != 0;
}

bool gameplay_hud_load(const char *directory)
{
	char path[1024];
	uint8_t header[HUD_HEADER_BYTES];
	struct stat status;
	FILE *file;
	uint8_t *data = NULL;
	bool valid = false;
	int length;

	if (attempted)
		return payload != NULL;
	attempted = true;
	if (!directory || !*directory)
		return false;
	length = snprintf(path, sizeof(path), "%s/gameplay-hud-v1.hda", directory);
	if (length < 0 || (size_t)length >= sizeof(path))
		return false;
	/* Reject non-regular and oversized inputs before reading or allocating. */
	if (stat(path, &status) || !S_ISREG(status.st_mode) ||
	    status.st_size != HUD_FILE_BYTES)
		return false;
	file = fopen(path, "rb");
	if (!file)
		return false;
	if (fread(header, 1, sizeof(header), file) != sizeof(header) || !valid_header(header))
		goto done;
	data = malloc(HUD_PAYLOAD_BYTES);
	if (!data)
		goto done;
	if (fread(data, 1, HUD_PAYLOAD_BYTES, file) != HUD_PAYLOAD_BYTES ||
	    fgetc(file) != EOF || ferror(file))
		goto done;
	valid = valid_payload(data, header);

done:
	if (fclose(file))
		valid = false;
	if (!valid)
	{
		free(data);
		return false;
	}
	payload = data;
	corner = read_u64(header + 44) == HUD_CORNER_MASK_FNV;
	for (int y = 0; y < HUD_HEIGHT && !expansion; ++y)
		for (int x = 0; x < HUD_WIDTH && !expansion; ++x)
			expansion = data[y * HUD_WIDTH + x] && expanded_pixel(x, y);
	source_fnv64 = read_u64(header + 36);
	return true;
}

/* All original-index-zero moat pixels around the eleven 5x5 SHIELD/ARMOR
 * glyph boxes must stay empty. Checking the source (not palette colors) also
 * preserves antialias foreground, including in another palette bank. */
static bool valid_glyph_moats(const uint8_t *indices, int pitch)
{
	for (int label = 0; label < 2; ++label)
	{
		int left = label ? 296 : 285;
		int letters = label ? 5 : 6;
		for (int letter = 0; letter < letters; ++letter)
		{
			int top = 138 + 6 * letter;
			for (int y = top - 1; y <= top + 5; ++y)
				for (int x = left - 1; x <= left + 5; ++x)
					if ((x == left - 1 || x == left + 5 ||
					     y == top - 1 || y == top + 5) &&
					    indices[(size_t)y * (size_t)pitch + (size_t)x] != 0)
						return false;
		}
	}
	return true;
}

bool gameplay_hud_capture(const uint8_t *indices, int pitch)
{
	uint64_t hash = UINT64_C(14695981039346656037);
	captured = corner_ready = false;
	if (!payload || !indices || pitch < HUD_WIDTH ||
	    (size_t)pitch > (SIZE_MAX - HUD_WIDTH) / (HUD_HEIGHT - 1))
		return false;
	for (int y = 0; y < HUD_HEIGHT; ++y)
	{
		const uint8_t *row = indices + (size_t)y * (size_t)pitch;
		hash = fnv_update(hash, row, HUD_WIDTH);
		for (int x = 0; x < HUD_WIDTH; ++x)
			if (payload[y * HUD_WIDTH + x] && row[x] == 0 &&
			    !(corner && corner_pixel(x, y)))
				return false;
	}
	if (hash != source_fnv64 || (expansion && !valid_glyph_moats(indices, pitch)) ||
	    (corner && corner_source_fnv(indices, pitch) != HUD_CORNER_REGION_FNV))
		return false;
	for (int y = 0; y < HUD_HEIGHT; ++y)
		memcpy(source_indices + y * HUD_WIDTH, indices + (size_t)y * (size_t)pitch,
		       HUD_WIDTH);
	captured = true;
	return true;
}

bool gameplay_hud_prepare_corner(const uint8_t *indices, int pitch)
{
	corner_ready = false;
	if (!payload || !captured || !corner || !indices || pitch < HUD_WIDTH ||
	    (size_t)pitch > (SIZE_MAX - HUD_WIDTH) / (HUD_HEIGHT - 1))
		return false;
	/* Atomic ownership: even one overlong message pixel revokes all 336 cells,
	 * including V5's 150 old frame cells. Never erase lingering message tails.
	 * Exact byte equality is checked anew at every ordinary composition. */
	for (int y = 184; y < 200; ++y)
		if (memcmp(indices + (size_t)y * (size_t)pitch + 248,
		           source_indices + y * HUD_WIDTH + 248, 21) != 0)
			return false;
	corner_ready = true;
	return true;
}

bool gameplay_hud_has_expansion(void)
{
	return payload != NULL && expansion;
}

bool gameplay_hud_verify_modes(const uint8_t indices[2][80],
                               const uint8_t opaque[2][80])
{
	static const int origins[] = {285, 302};
	if (!gameplay_hud_has_expansion())
		return true;
	if (!captured)
		return false;
	for (size_t button = 0; button < sizeof(origins) / sizeof(origins[0]); ++button)
		for (int local = 0; local < 80; ++local)
		{
			int x = origins[button] + local % 10;
			int y = 44 + local / 10;
			size_t source = (size_t)y * HUD_WIDTH + (size_t)x;
			/* Every allowed point inside these protected boxes belongs to the
			 * expansion. Unowned sprite pixels cannot revoke unrelated rails. */
			if (payload[source] &&
			    (!indices || !opaque || opaque[0][local] != 255 ||
			     opaque[1][local] != 255 || indices[0][local] != indices[1][local] ||
			     indices[0][local] != source_indices[source]))
				return false;
		}
	return true;
}

const uint8_t *gameplay_hud_sample(int x, int y, int sx, int sy, int density,
                                 uint8_t current_index)
{
	size_t index;
	int divisor;
	if (!payload || !captured || (density != 4 && density != 8) ||
	    x < 0 || x >= HUD_WIDTH || y < 0 || y >= HUD_HEIGHT ||
	    sx < 0 || sx >= density || sy < 0 || sy >= density)
		return NULL;
	index = (size_t)y * HUD_WIDTH + (size_t)x;
	if (!payload[index] || current_index != source_indices[index] ||
	    (corner && corner_pixel(x, y) && !corner_ready))
		return NULL;
	divisor = density / HUD_DENSITY;
	index = ((size_t)(y * HUD_DENSITY + sy / divisor) * HUD_RGBA_WIDTH +
	         (size_t)(x * HUD_DENSITY + sx / divisor)) * 4;
	return payload + HUD_PIXELS + index;
}

bool gameplay_hud_ready(void)
{
	return payload != NULL && captured;
}

void gameplay_hud_forget_source(void)
{
	captured = corner_ready = false;
}

void gameplay_hud_shutdown(void)
{
	free(payload);
	payload = NULL;
	source_fnv64 = 0;
	captured = false;
	expansion = false;
	corner = corner_ready = false;
	attempted = false;
}
