#ifndef B313_TAIL414_CONTROL_H
#define B313_TAIL414_CONTROL_H
#include <stdbool.h>
void b313_tail414_control_old_end(unsigned tick,bool success);
void b313_tail414_control_old_retire(bool success);
void b313_tail414_control_begin(unsigned tick);
void b313_tail414_control_end(unsigned tick);
bool b313_tail414_probe_tick(unsigned tick);
#endif
