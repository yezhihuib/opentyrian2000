#include <stdint.h>
#include <stddef.h>
uint64_t fnv64(const unsigned char *p,size_t n){uint64_t h=14695981039346656037ULL;while(n--){h^=*p++;h*=1099511628211ULL;}return h;}
