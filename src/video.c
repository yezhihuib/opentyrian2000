/*
 * OpenTyrian: A modern cross-platform port of Tyrian
 * Copyright (C) 2007-2009  The OpenTyrian Development Team
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */
#include "data_text.h"
#include "data_frame.h"
#include "data_portrait.h"
#include "settings_font.h"
#include "load_font.h"
#include "selector_font.h"
#include "pregame_font.h"
#include "video.h"
#include "hd_cursor.h"
#include "render_mirror.h"
#include "common_pause.h"
#include "common_menu_config.h"
#include "asset_debug.h"
#include "startup_logos.h"
#include "title_layers.h"

#include "keyboard.h"
#include "opentyr.h"
#include "palette.h"
#include "video_scale.h"

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const char *const scaling_mode_names[ScalingMode_MAX] = {
	"Center",
	"Integer",
	"Fit 8:5",
	"Fit 4:3",
};

int fullscreen_display;
ScalingMode scaling_mode = SCALE_INTEGER;
static SDL_Rect last_output_rect = { 0, 0, vga_width, vga_height };

SDL_Surface *VGAScreen, *VGAScreenSeg;
SDL_Surface *VGAScreen2;
SDL_Surface *game_screen;

SDL_Window *main_window = NULL;
static SDL_Renderer *main_window_renderer = NULL;
static Uint64 output_renderer_generation;
SDL_PixelFormat *main_window_tex_format = NULL;
static SDL_Texture *main_window_texture = NULL;

static ScalerFunction scaler_function;

static void init_renderer(void);
static void deinit_renderer(void);
static void init_texture(void);
static void deinit_texture(void);

static int window_get_display_index(void);
static void window_center_in_display(int display_index);
static void calc_dst_render_rect(SDL_Surface *src_surface, SDL_Rect *dst_rect);
static void scale_and_flip(SDL_Surface *);

void init_video(void)
{
	if (SDL_WasInit(SDL_INIT_VIDEO))
		return;

	if (SDL_InitSubSystem(SDL_INIT_VIDEO) == -1)
	{
		fprintf(stderr, "error: failed to initialize SDL video: %s\n", SDL_GetError());
		exit(1);
	}

	// Create the software surfaces that the game renders to. These are all 320x200x8 regardless
	// of the window size or monitor resolution.
	VGAScreen = VGAScreenSeg = SDL_CreateRGBSurface(0, vga_width, vga_height, 8, 0, 0, 0, 0);
	VGAScreen2 = SDL_CreateRGBSurface(0, vga_width, vga_height, 8, 0, 0, 0, 0);
	game_screen = SDL_CreateRGBSurface(0, vga_width, vga_height, 8, 0, 0, 0, 0);

	// The game code writes to surface->pixels directly without locking, so make sure that we
	// indeed created software surfaces that support this.
	assert(!SDL_MUSTLOCK(VGAScreen));
	assert(!SDL_MUSTLOCK(VGAScreen2));
	assert(!SDL_MUSTLOCK(game_screen));

	JE_clr256(VGAScreen);

	// Create the window with a temporary initial size, hidden until we set up the
	// scaler and find the true window size
	main_window = SDL_CreateWindow(opentyrian_str,
		SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
		vga_width, vga_height, SDL_WINDOW_RESIZABLE | SDL_WINDOW_HIDDEN);

	if (main_window == NULL)
	{
		fprintf(stderr, "error: failed to create window: %s\n", SDL_GetError());
		exit(EXIT_FAILURE);
	}

	reinit_fullscreen(fullscreen_display);
	init_renderer();
	init_texture();
	init_scaler(scaler);

	SDL_ShowWindow(main_window);

	SDL_SetRenderDrawColor(main_window_renderer, 0, 0, 0, 255);
	SDL_RenderClear(main_window_renderer);
	SDL_RenderPresent(main_window_renderer);
	common_pause_snapshot_reset();
}

void deinit_video(void)
{
	render_mirror_global_reset();
	common_pause_invalidate();
	render_mirror_hud_shutdown();
	startup_logos_shutdown();
	title_layers_end();
	settings_font_end();
	load_font_end();
	selector_font_end();
	pregame_font_end();
	deinit_texture();
	deinit_renderer();

	SDL_DestroyWindow(main_window);

	SDL_FreeSurface(VGAScreenSeg);
	SDL_FreeSurface(VGAScreen2);
	SDL_FreeSurface(game_screen);

	SDL_QuitSubSystem(SDL_INIT_VIDEO);
}

static void init_renderer(void)
{
	main_window_renderer = SDL_CreateRenderer(main_window, -1, 0);

	if (main_window_renderer == NULL)
	{
		fprintf(stderr, "error: failed to create renderer: %s\n", SDL_GetError());
		exit(EXIT_FAILURE);
	}
	/* Pointer addresses may be reused after renderer recreation. */
	++output_renderer_generation;
}

static void deinit_renderer(void)
{
	common_pause_invalidate();
	common_pause_release_texture();
	if (main_window_renderer != NULL)
	{
		startup_logos_release_texture();
		title_layers_release_texture();
		settings_font_invalidate();
	load_font_invalidate();
	selector_font_invalidate();
	pregame_font_invalidate();
		render_mirror_release_texture();
		data_text_invalidate(); data_frame_invalidate(); data_portrait_invalidate();
		hd_cursor_release();
		SDL_DestroyRenderer(main_window_renderer);
		main_window_renderer = NULL;
	}
}

static void init_texture(void)
{
	assert(main_window_renderer != NULL);

	int bpp = 32; // TODOSDL2
	Uint32 format = bpp == 32 ? SDL_PIXELFORMAT_RGB888 : SDL_PIXELFORMAT_RGB565;
	int scaler_w = scalers[scaler].width;
	int scaler_h = scalers[scaler].height;

	main_window_tex_format = SDL_AllocFormat(format);

	main_window_texture = SDL_CreateTexture(main_window_renderer, format, SDL_TEXTUREACCESS_STREAMING, scaler_w, scaler_h);

	if (main_window_texture == NULL)
	{
		fprintf(stderr, "error: failed to create scaler texture %dx%dx%s: %s\n", scaler_w, scaler_h, SDL_GetPixelFormatName(format), SDL_GetError());
		exit(EXIT_FAILURE);
	}
}

static void deinit_texture(void)
{
	common_pause_invalidate();
	common_pause_release_texture();
	data_text_invalidate(); data_frame_invalidate(); data_portrait_invalidate();
	settings_font_invalidate();
	load_font_invalidate();
	selector_font_invalidate();
	pregame_font_invalidate();
	if (main_window_texture != NULL)
	{
		SDL_DestroyTexture(main_window_texture);
		main_window_texture = NULL;
	}

	if (main_window_tex_format != NULL)
	{
		SDL_FreeFormat(main_window_tex_format);
		main_window_tex_format = NULL;
	}
}

static int window_get_display_index(void)
{
	return SDL_GetWindowDisplayIndex(main_window);
}

static void window_center_in_display(int display_index)
{
	int win_w, win_h;
	SDL_GetWindowSize(main_window, &win_w, &win_h);

	SDL_Rect bounds;
	SDL_GetDisplayBounds(display_index, &bounds);

	SDL_SetWindowPosition(main_window, bounds.x + (bounds.w - win_w) / 2, bounds.y + (bounds.h - win_h) / 2);
}

void reinit_fullscreen(int new_display)
{
	settings_font_invalidate();
	load_font_invalidate();
	selector_font_invalidate();
	pregame_font_invalidate();
	fullscreen_display = new_display;

	if (fullscreen_display >= SDL_GetNumVideoDisplays())
	{
		fullscreen_display = 0;
	}

	SDL_SetWindowFullscreen(main_window, SDL_FALSE);
	SDL_SetWindowSize(main_window, scalers[scaler].width, scalers[scaler].height);

	if (fullscreen_display == -1)
	{
		window_center_in_display(window_get_display_index());
	}
	else
	{
		window_center_in_display(fullscreen_display);

		if (SDL_SetWindowFullscreen(main_window, SDL_WINDOW_FULLSCREEN_DESKTOP) != 0)
		{
			reinit_fullscreen(-1);
			return;
		}
	}
}

void video_on_win_resize(void)
{
	settings_font_invalidate();
	load_font_invalidate();
	selector_font_invalidate();
	pregame_font_invalidate();
	int w, h;
	int scaler_w, scaler_h;

	// Tell video to reinit if the window was manually resized by the user.
	// Also enforce a minimum size on the window.

	SDL_GetWindowSize(main_window, &w, &h);
	scaler_w = scalers[scaler].width;
	scaler_h = scalers[scaler].height;

	if (w < scaler_w || h < scaler_h)
	{
		w = w < scaler_w ? scaler_w : w;
		h = h < scaler_h ? scaler_h : h;

		SDL_SetWindowSize(main_window, w, h);
	}
}

void toggle_fullscreen(void)
{
	if (fullscreen_display != -1)
		reinit_fullscreen(-1);
	else
		reinit_fullscreen(SDL_GetWindowDisplayIndex(main_window));
}

bool init_scaler(unsigned int new_scaler)
{
	int w = scalers[new_scaler].width,
	    h = scalers[new_scaler].height;
	int bpp = main_window_tex_format->BitsPerPixel; // TODOSDL2

	scaler = new_scaler;

	deinit_texture();
	init_texture();

	if (fullscreen_display == -1)
	{
		// Changing scalers, when not in fullscreen mode, forces the window
		// to resize to exactly match the scaler's output dimensions.
		SDL_SetWindowSize(main_window, w, h);
		window_center_in_display(window_get_display_index());
	}

	switch (bpp)
	{
	case 32:
		scaler_function = scalers[scaler].scaler32;
		break;
	case 16:
		scaler_function = scalers[scaler].scaler16;
		break;
	default:
		scaler_function = NULL;
		break;
	}

	if (scaler_function == NULL)
	{
		assert(false);
		return false;
	}

	return true;
}

bool set_scaling_mode_by_name(const char *name)
{
	for (int i = 0; i < ScalingMode_MAX; ++i)
	{
		 if (strcmp(name, scaling_mode_names[i]) == 0)
		 {
			 scaling_mode = i;
			 return true;
		 }
	}
	return false;
}

void JE_clr256(SDL_Surface *screen)
{
	hd_cursor_clear();
	data_text_end(); data_frame_end(); data_portrait_end();
	startup_logos_reset();
	title_layers_end();
	settings_font_end();
	load_font_end();
	selector_font_end();
	pregame_font_end();
	SDL_FillRect(screen, NULL, 0);
	render_mirror_rect(screen,NULL);
}

void JE_showVGA(void) 
{ 
	scale_and_flip(VGAScreen); 
}

static void calc_dst_render_rect(SDL_Surface *const src_surface, SDL_Rect *const dst_rect)
{
	// Decides how the logical output texture (after software scaling applied) will fit
	// in the window.

	int win_w, win_h;
	SDL_GetWindowSize(main_window, &win_w, &win_h);

	int maxh_width, maxw_height;

	switch (scaling_mode)
	{
	case SCALE_CENTER:
		SDL_QueryTexture(main_window_texture, NULL, NULL, &dst_rect->w, &dst_rect->h);
		break;
	case SCALE_INTEGER:
		dst_rect->w = src_surface->w;
		dst_rect->h = src_surface->h;
		while (dst_rect->w + src_surface->w <= win_w && dst_rect->h + src_surface->h <= win_h)
		{
			dst_rect->w += src_surface->w;
			dst_rect->h += src_surface->h;
		}
		break;
	case SCALE_ASPECT_8_5:
		maxh_width = win_h * (8.f / 5.f);
		maxw_height = win_w * (5.f / 8.f);

		if (maxh_width > win_w)
		{
			dst_rect->w = win_w;
			dst_rect->h = maxw_height;
		}
		else
		{
			dst_rect->w = maxh_width;
			dst_rect->h = win_h;
		}
		break;
	case SCALE_ASPECT_4_3:
		maxh_width = win_h * (4.f / 3.f);
		maxw_height = win_w * (3.f / 4.f);

		if (maxh_width > win_w)
		{
			dst_rect->w = win_w;
			dst_rect->h = maxw_height;
		}
		else
		{
			dst_rect->w = maxh_width;
			dst_rect->h = win_h;
		}
		break;
	case ScalingMode_MAX:
		assert(false);
		break;
	}

	dst_rect->x = (win_w - dst_rect->w) / 2;
	dst_rect->y = (win_h - dst_rect->h) / 2;
}

bool video_output_geometry(VideoOutputGeometry *out)
{
	VideoOutputGeometry g = {0};
	SDL_Rect viewport;
	float sx = 0.0f, sy = 0.0f;
	int logical_w = 0, logical_h = 0, texture_w = 0, texture_h = 0;
	if (!out || !main_window || !main_window_renderer || !main_window_texture ||
	    !VGAScreenSeg || VGAScreenSeg->w != 320 || VGAScreenSeg->h != 200)
		return false;
	g.window = main_window;
	g.renderer = main_window_renderer;
	g.renderer_generation = output_renderer_generation;
	g.scaling_mode = scaling_mode;
	if (g.scaling_mode < SCALE_CENTER || g.scaling_mode >= ScalingMode_MAX)
		return false;
	SDL_GetWindowSize(g.window, &g.window_w, &g.window_h);
	if (g.window_w <= 0 || g.window_h <= 0 ||
	    SDL_GetRendererOutputSize(g.renderer, &g.output_w, &g.output_h) != 0 ||
	    g.output_w <= 0 || g.output_h <= 0 ||
	    SDL_QueryTexture(main_window_texture, NULL, NULL, &texture_w, &texture_h) != 0 ||
	    texture_w <= 0 || texture_h <= 0 || SDL_GetRenderTarget(g.renderer) != NULL)
		return false;
	SDL_RenderGetLogicalSize(g.renderer, &logical_w, &logical_h);
	SDL_RenderGetScale(g.renderer, &sx, &sy);
	SDL_RenderGetViewport(g.renderer, &viewport);
	/* The existing RenderCopy destination is physical only with this identity
	 * transform. Do not guess a window-to-output ratio on high-DPI backends. */
	if (logical_w || logical_h || sx != 1.0f || sy != 1.0f ||
	    viewport.x || viewport.y || viewport.w != g.output_w || viewport.h != g.output_h ||
	    SDL_RenderIsClipEnabled(g.renderer))
		return false;
	calc_dst_render_rect(VGAScreenSeg, &g.dst);
	if (g.dst.x < 0 || g.dst.y < 0 || g.dst.w <= 0 || g.dst.h <= 0 ||
	    g.dst.w > g.output_w - g.dst.x || g.dst.h > g.output_h - g.dst.y ||
	    g.dst.w % 320 || g.dst.h % 200)
		return false;
	g.scale = g.dst.w / 320;
	if (g.scale != g.dst.h / 200 ||
	    (g.scale != 1 && g.scale != 2 && g.scale != 4 && g.scale != 8))
		return false;
	g.footprint = 8 / g.scale;
	*out = g;
	return true;
}

bool video_output_geometry_equal(const VideoOutputGeometry *a,
                                 const VideoOutputGeometry *b)
{
	/* Fieldwise equality deliberately excludes uninitialized structure padding. */
	return a && b && a->window == b->window && a->renderer == b->renderer &&
	       a->renderer_generation == b->renderer_generation &&
	       a->dst.x == b->dst.x && a->dst.y == b->dst.y &&
	       a->dst.w == b->dst.w && a->dst.h == b->dst.h &&
	       a->window_w == b->window_w && a->window_h == b->window_h &&
	       a->output_w == b->output_w && a->output_h == b->output_h &&
	       a->scale == b->scale && a->footprint == b->footprint &&
	       a->scaling_mode == b->scaling_mode;
}

static void scale_and_flip(SDL_Surface *src_surface)
{
	if(asset_debug_fast_forward())return;
	assert(src_surface->format->BitsPerPixel == 8);

	// Do software scaling
	assert(scaler_function != NULL);
	SDL_Rect dst_rect;
	calc_dst_render_rect(src_surface, &dst_rect);
	if(common_pause_owns_display() || render_mirror_owns_display() || startup_logos_owns_display())hd_cursor_clear();
	hd_cursor_prepare(main_window_renderer,src_surface,&dst_rect,rgb_palette,main_window_tex_format);
	const bool cursor_replaced=hd_cursor_active();
	scaler_function(hd_cursor_underlay(src_surface), main_window_texture);
	if(selector_font_owns_display() && (common_pause_owns_display() || startup_logos_owns_display() || title_layers_owns_display() || render_mirror_owns_display() || settings_font_owns_display() || load_font_owns_display())) selector_font_end();
	if(pregame_font_owns_display() && (common_pause_owns_display() || startup_logos_owns_display() || title_layers_owns_display() || render_mirror_owns_display() || settings_font_owns_display() || load_font_owns_display() || selector_font_owns_display())) pregame_font_end();
	if (!common_menu_configured()) common_pause_invalidate();
	if(common_pause_present(main_window_renderer,main_window_texture,src_surface,&dst_rect, startup_logos_owns_display() || title_layers_owns_display() || settings_font_owns_display() || load_font_owns_display() || selector_font_owns_display() || pregame_font_owns_display())) { last_output_rect=dst_rect; return; }
	if(startup_logos_present(main_window_renderer,src_surface,&dst_rect)) { common_pause_snapshot_reset(); last_output_rect=dst_rect; return; }
	if(title_layers_present(main_window_renderer,src_surface,&dst_rect)) { common_pause_snapshot_reset(); last_output_rect=dst_rect; return; }
	if(settings_font_present(main_window_renderer,main_window_texture,src_surface,&dst_rect, startup_logos_owns_display() || title_layers_owns_display() || render_mirror_owns_display() || load_font_owns_display() || selector_font_owns_display())) { common_pause_snapshot_reset(); last_output_rect=dst_rect; return; }
	if(load_font_present(main_window_renderer,main_window_texture,src_surface,&dst_rect, startup_logos_owns_display() || title_layers_owns_display() || render_mirror_owns_display() || settings_font_owns_display() || selector_font_owns_display())) { common_pause_snapshot_reset(); last_output_rect=dst_rect; return; }
	if(selector_font_present(main_window_renderer,main_window_texture,src_surface,&dst_rect, startup_logos_owns_display() || title_layers_owns_display() || render_mirror_owns_display() || settings_font_owns_display() || load_font_owns_display())) { common_pause_snapshot_reset(); last_output_rect=dst_rect; return; }
	if(pregame_font_present(main_window_renderer,main_window_texture,src_surface,&dst_rect, startup_logos_owns_display() || title_layers_owns_display() || render_mirror_owns_display() || settings_font_owns_display() || load_font_owns_display() || selector_font_owns_display())) { common_pause_snapshot_reset(); last_output_rect=dst_rect; return; }
	if(render_mirror_present(main_window_renderer,src_surface,&dst_rect)) { last_output_rect=dst_rect; return; }

	// A late optional-presenter failure may have retired the cursor lease.
	if(cursor_replaced&&!hd_cursor_active())scaler_function(src_surface,main_window_texture);
	// Clear the window and blit the output texture to it
	SDL_SetRenderDrawColor(main_window_renderer, 0, 0, 0, 255);
	SDL_RenderClear(main_window_renderer);
	SDL_RenderCopy(main_window_renderer, main_window_texture, NULL, &dst_rect);
	data_frame_present(main_window_renderer, src_surface, &dst_rect, rgb_palette, main_window_tex_format);
	data_portrait_present(main_window_renderer, src_surface, &dst_rect, rgb_palette, main_window_tex_format);
	data_text_present(main_window_renderer, src_surface, &dst_rect);
	data_text_cursor_present(main_window_renderer, src_surface, &dst_rect, rgb_palette, main_window_tex_format);
	if(!hd_cursor_present(main_window_renderer,&dst_rect)) {
		// Retry the complete native-backed presentation, including native cursor.
		scaler_function(src_surface,main_window_texture);
		SDL_SetRenderDrawColor(main_window_renderer,0,0,0,255);
		SDL_RenderClear(main_window_renderer);
		SDL_RenderCopy(main_window_renderer,main_window_texture,NULL,&dst_rect);
		data_frame_present(main_window_renderer,src_surface,&dst_rect,rgb_palette,main_window_tex_format);
		data_portrait_present(main_window_renderer,src_surface,&dst_rect,rgb_palette,main_window_tex_format);
		data_text_present(main_window_renderer,src_surface,&dst_rect);
		data_text_cursor_present(main_window_renderer,src_surface,&dst_rect,rgb_palette,main_window_tex_format);
	}
	asset_debug_readback(main_window_renderer);
	SDL_RenderPresent(main_window_renderer);
	common_pause_snapshot_reset();

	// Save output rect to be used by mouse functions
	last_output_rect = dst_rect;
}

/** Maps a specified point in game screen coordinates to window coordinates. */
void mapScreenPointToWindow(Sint32 *const inout_x, Sint32 *const inout_y)
{
	*inout_x = (2 * *inout_x + 1) * last_output_rect.w / (2 * VGAScreen->w) + last_output_rect.x;
	*inout_y = (2 * *inout_y + 1) * last_output_rect.h / (2 * VGAScreen->h) + last_output_rect.y;
}

/** Maps a specified point in window coordinates to game screen coordinates. */
void mapWindowPointToScreen(Sint32 *const inout_x, Sint32 *const inout_y)
{
	*inout_x = (2 * (*inout_x - last_output_rect.x) + 1) * VGAScreen->w / (2 * last_output_rect.w);
	*inout_y = (2 * (*inout_y - last_output_rect.y) + 1) * VGAScreen->h / (2 * last_output_rect.h);
}

/** Scales a distance in window coordinates to game screen coordinates. */
void scaleWindowDistanceToScreen(Sint32 *const inout_x, Sint32 *const inout_y)
{
	*inout_x = (2 * *inout_x + 1) * VGAScreen->w / (2 * last_output_rect.w);
	*inout_y = (2 * *inout_y + 1) * VGAScreen->h / (2 * last_output_rect.h);
}
