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
#ifndef PARAMS_H
#define PARAMS_H

#include "opentyr.h"

extern JE_boolean richMode, constantPlay, constantDie;

/* Direct native single-session preview; never enables a render/probe mode. */
extern bool level2_preview_requested;
void level2_preview_parse(int *argc, char *argv[]);

void JE_paramCheck(int argc, char *argv[]);

#endif /* PARAMS_H */
