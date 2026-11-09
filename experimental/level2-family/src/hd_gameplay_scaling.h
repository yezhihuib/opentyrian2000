/* SPDX-License-Identifier: GPL-2.0-or-later
 * Final development-overlay gameplay/snapshot sampling only. The canonical
 * renderer and classic scaler remain independent and unchanged. */
#ifndef HD_GAMEPLAY_SCALING_H
#define HD_GAMEPLAY_SCALING_H
#include "video.h"
#include <math.h>

static inline int video_hd_set_texture_scale(SDL_Texture *texture, SDL_Renderer *renderer,
                               const SDL_Rect *destination)
{
	float scale_x, scale_y, output_x, output_y;
	double logical_x, logical_y;
	SDL_ScaleMode mode;
	SDL_RendererInfo info;

	if (!texture || !renderer || !destination ||
	    destination->w <= 0 || destination->h <= 0)
		return -1;
	SDL_RenderGetScale(renderer, &scale_x, &scale_y);
	if (!isfinite(scale_x) || !isfinite(scale_y) || scale_x <= 0 || scale_y <= 0)
		return -1;
	/* SDL applies its renderer scale after destination coordinates. Test the
	 * actual output footprint, not just the unscaled window rectangle. Separate
	 * integer axes also preserve the existing stretched-integer presentation. */
	/* Match SDL_RenderCopy's float multiplication before testing the ratio:
	 * e.g. a 960x600 destination at scale 2/3 is exactly 640x400 in SDL. */
	output_x = (float)destination->w * scale_x;
	output_y = (float)destination->h * scale_y;
	if (!isfinite(output_x) || !isfinite(output_y))
		return -1;
	if (SDL_GetRendererInfo(renderer, &info) != 0)
		return -1;
	/* SDL's software Copy queue stores integer destination extents. Match
	 * that truncation; accelerated renderers retain the float footprint. */
	if (info.flags & SDL_RENDERER_SOFTWARE)
	{
		output_x = floorf(output_x);
		output_y = floorf(output_y);
	}
	if (output_x < 1 || output_y < 1)
		return -1;
	logical_x = (double)output_x / vga_width;
	logical_y = (double)output_y / vga_height;
	mode = logical_x >= 1 && logical_y >= 1 &&
	       floor(logical_x) == logical_x && floor(logical_y) == logical_y
	       ? SDL_ScaleModeNearest : SDL_ScaleModeLinear;
	if (SDL_SetTextureScaleMode(texture, mode) == 0)
		return 0;
	/* An older backend may not support linear filtering. Keep the HD frame
	 * using its established nearest path rather than dropping to classic. */
	return mode == SDL_ScaleModeLinear
	       ? SDL_SetTextureScaleMode(texture, SDL_ScaleModeNearest) : -1;
}

#endif /* HD_GAMEPLAY_SCALING_H */
