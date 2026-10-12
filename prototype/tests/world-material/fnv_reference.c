/* Exact existing project hash, extracted only for standalone loader tests. */
#include <stdint.h>
#include <stddef.h>
uint64_t game_probe_hash(uint64_t h, const void *data, size_t size)
{
 const unsigned char *p = data;
 while (size--) { h ^= *p++; h *= UINT64_C(1099511628211); }
 return h;
}
