/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef COMMON_MENU_CONFIG_H
#define COMMON_MENU_CONFIG_H
#include <stdbool.h>
/* Explicit assembled runtime root: RFR/NFR filenames and settings-font-*.hda
 * reside together. No implicit sibling-directory search. Missing resources
 * fail independently in their consuming family. */
bool common_menu_configure(const char *directory);
/* Explicit assembled runtime root: RFR/NFR filenames and settings-font-*.hda
 * reside together. No implicit sibling-directory search. Missing resources
 * fail independently in their consuming family. */
bool common_menu_configured(void);
#endif
