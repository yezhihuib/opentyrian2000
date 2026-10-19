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
#include "settings_font.h"
#include "load_font.h"
#include "selector_font.h"
#include "pregame_font.h"
#include "params.h"
#include "data_text.h"
#include "data_frame.h"
#include "data_portrait.h"
#include "startup_logos.h"
#include "title_layers.h"

#include "arg_parse.h"
#include "file.h"
#include "joystick.h"
#include "loudness.h"
#include "external_music.h"
#include "network.h"
#include "opentyr.h"
#include "varz.h"
#include "xmas.h"

#include <assert.h>
#include <ctype.h>
#include <errno.h>
#include <stdint.h>
#include <string.h>

JE_boolean richMode = false, constantPlay = false, constantDie = false;

/* YKS: Note: LOOT cheat had non letters removed. */
const char pars[][9] = {
	"LOOT", "RECORD", "NOJOY", "CONSTANT", "DEATH", "NOSOUND", "NOXMAS", "YESXMAS"
};

void JE_paramCheck(int argc, char *argv[])
{
	const Options options[] =
	{
		{ 'h', 'h', "help",              false },
		
		{ 's', 's', "no-sound",          false },
		{ 'j', 'j', "no-joystick",       false },
		{ 'x', 'x', "no-xmas",           false },
		
		{ 't', 't', "data",              true },
		{ 258, 0,   "startup-assets",    true },
		{ 259, 0,   "music-dir",         true },
		{ 260, 0,   "data-text-assets",  true },
		{ 261, 0,   "data-frame-assets", true },
		{ 262, 0,   "data-portrait-assets", true },
		
		{ 'n', 'n', "net",               true },
		{ 256, 0,   "net-player-name",   true }, // TODO: no short codes because there should
		{ 257, 0,   "net-player-number", true }, //       be a menu for entering these in the future
		{ 'p', 'p', "net-port",          true },
		{ 'd', 'd', "net-delay",         true },
		
		{ 'X', 'X', "xmas",              false },
		{ 'c', 'c', "constant",          false },
		{ 'k', 'k', "death",             false },
		{ 'r', 'r', "record",            false },
		{ 'l', 'l', "loot",              false },
		
		{ 0, 0, NULL, false}
	};
	
	Option option;
	
	for (; ; )
	{
		option = parse_args(argc, (const char **)argv, options);
		
		if (option.value == NOT_OPTION)
			break;
		
		switch (option.value)
		{
		case INVALID_OPTION:
		case AMBIGUOUS_OPTION:
		case OPTION_MISSING_ARG:
			fprintf(stderr, "Try `%s --help' for more information.\n", argv[0]);
			exit(EXIT_FAILURE);
			break;
			
		case 'h':
			printf("Usage: %s [OPTION...]\n\n"
			       "Options:\n"
			       "  -h, --help                   Show help about options\n\n"
			       "  -s, --no-sound               Disable audio\n"
			       "  -j, --no-joystick            Disable joystick/gamepad input\n"
			       "  -x, --no-xmas                Disable Christmas mode\n\n"
			       "  -t, --data=DIR               Set Tyrian data directory\n"
			       "  --music-dir=DIR             Optional MP3 replacements: track01.mp3, track02.mp3, ...\n"
			       "  --data-text-assets=DIR      Optional Data-only Chinese text and font resources\n"
			       "  --data-frame-assets=DIR     Optional Data-only static HD frame resource\n"
			       "  --data-portrait-assets=DIR  Optional source-bound HD Data portraits\n"
			       "  --startup-assets=DIR        Optional HD manufacturer/title art (release, local startup only)\n"
			       "  --manual-hd-assets=DIR      Display-only HD for local single-player Episode 1 / level 9\n"
			       "                               Native menus and controls; classic outside this first level\n\n"
			       "  -n, --net=HOST[:PORT]        Start a networked game\n"
			       "  --net-player-name=NAME       Sets local player name in a networked game\n"
			       "  --net-player-number=NUMBER   Sets local player number in a networked game\n"
			       "                               (1 or 2)\n"
			       "  -p, --net-port=PORT          Local port to bind (default is 1333)\n"
			       "  -d, --net-delay=FRAMES       Set lag-compensation delay (default is 1)\n", argv[0]);
			exit(0);
			break;
			
		case 's':
			// Disables sound/music usage
			audio_disabled = true;
			break;
			
		case 'j':
			// Disables joystick detection
			ignore_joystick = true;
			break;
			
		case 'x':
			override_xmas = true;
			xmas = false;
			break;
			
		// set custom Tyrian data directory
		case 't':
			custom_data_dir = option.arg;
			break;
			
		case 259: // --music-dir
			if (!external_music_set_directory(option.arg))
			{
				fprintf(stderr, "Music override requires a nonempty directory\n");
				exit(EXIT_FAILURE);
			}
			break;

		case 262: // --data-portrait-assets
			if (!option.arg || !*option.arg) { fprintf(stderr, "Data portrait assets require a nonempty directory\n"); exit(EXIT_FAILURE); }
			data_portrait_set_directory(option.arg);
			break;

		case 261: // --data-frame-assets
			if (!option.arg || !*option.arg) { fprintf(stderr, "Data frame assets require a nonempty directory\n"); exit(EXIT_FAILURE); }
			data_frame_set_directory(option.arg);
			break;

		case 260: // --data-text-assets
			if (!option.arg || !*option.arg) { fprintf(stderr, "Data text assets require a nonempty directory\n"); exit(EXIT_FAILURE); }
			data_text_set_directory(option.arg);
			break;

		case 258: // --startup-assets
			if (!startup_logos_set_directory(option.arg))
			{
				fprintf(stderr, "Startup assets require a nonempty directory\n");
				exit(EXIT_FAILURE);
			}
			title_layers_set_directory(option.arg);
			settings_font_set_directory(option.arg);
			load_font_set_directory(option.arg);
			selector_font_set_directory(option.arg);
			pregame_font_set_directory(option.arg);
			break;

		case 'n':
			isNetworkGame = true;
			
			intptr_t temp = (intptr_t)strchr(option.arg, ':');
			if (temp)
			{
				temp -= (intptr_t)option.arg;
				
				int temp_port = atoi(&option.arg[temp + 1]);
				if (temp_port > 0 && temp_port < 49152)
					network_opponent_port = temp_port;
				else
				{
					fprintf(stderr, "%s: error: invalid network port number\n", argv[0]);
					exit(EXIT_FAILURE);
				}
				
				network_opponent_host = malloc(temp + 1);
				SDL_strlcpy(network_opponent_host, option.arg, temp + 1);
			}
			else
			{
				network_opponent_host = malloc(strlen(option.arg) + 1);
				strcpy(network_opponent_host, option.arg);
			}
			break;
			
		case 256: // --net-player-name
			network_player_name = malloc(strlen(option.arg) + 1);
			strcpy(network_player_name, option.arg);
			break;
			
		case 257: // --net-player-number
		{
			int temp = atoi(option.arg);
			if (temp >= 1 && temp <= 2)
				thisPlayerNum = temp;
			else
			{
				fprintf(stderr, "%s: error: invalid network player number\n", argv[0]);
				exit(EXIT_FAILURE);
			}
			break;
		}
		case 'p':
		{
			int temp = atoi(option.arg);
			if (temp > 0 && temp < 49152)
				network_player_port = temp;
			else
			{
				fprintf(stderr, "%s: error: invalid network port number\n", argv[0]);
				exit(EXIT_FAILURE);
			}
			break;
		}
		case 'd':
		{
			int temp;
			if (sscanf(option.arg, "%d", &temp) == 1)
				network_delay = 1 + temp;
			else
			{
				fprintf(stderr, "%s: error: invalid network delay value\n", argv[0]);
				exit(EXIT_FAILURE);
			}
			break;
		}
		case 'X':
			override_xmas = true;
			xmas = true;
			break;
			
		case 'c':
			/* Constant play for testing purposes (C key activates invincibility)
			   This might be useful for publishers to see everything - especially
			   those who can't play it */
			constantPlay = true;
			break;
			
		case 'k':
			constantDie = true;
			break;
			
		case 'r':
			record_demo = true;
			break;
			
		case 'l':
			// Gives you mucho bucks
			richMode = true;
			break;
			
		default:
			assert(false);
			break;
		}
	}
	
	// legacy parameter support
	for (int i = option.argn; i < argc; ++i)
	{
		for (uint j = 0; j < strlen(argv[i]); ++j)
			argv[i][j] = toupper((unsigned char)argv[i][j]);
		
		for (uint j = 0; j < COUNTOF(pars); ++j)
		{
			if (strcmp(argv[i], pars[j]) == 0)
			{
				switch (j)
				{
				case 0:
					richMode = true;
					break;
				case 1:
					record_demo = true;
					break;
				case 2:
					ignore_joystick = true;
					break;
				case 3:
					constantPlay = true;
					break;
				case 4:
					constantDie = true;
					break;
				case 5:
					audio_disabled = true;
					break;
				case 6:
					override_xmas = true;
					xmas = false;
					break;
				case 7:
					override_xmas = true;
					xmas = true;
					break;
					
				default:
					assert(false);
					break;
				}
			}
		}
	}
}
