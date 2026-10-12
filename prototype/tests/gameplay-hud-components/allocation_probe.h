#ifndef HUD_COMPONENTS_ALLOCATION_PROBE_H
#define HUD_COMPONENTS_ALLOCATION_PROBE_H
#include <stddef.h>
void *hud_components_test_malloc(size_t size);
void hud_components_test_free(void *pointer);
#endif
