#ifndef GAMEPLAY_HUD_ALLOCATION_PROBE_H
#define GAMEPLAY_HUD_ALLOCATION_PROBE_H
#include <stddef.h>
void *gameplay_hud_test_malloc(size_t size);
void gameplay_hud_test_free(void *ptr);
#endif
