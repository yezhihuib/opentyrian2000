/* Private four-frame diagnostic, no permission recovery after a failed frame. */
#ifndef B313_V6_SEQUENCE_H
#define B313_V6_SEQUENCE_H
#include <stdbool.h>
#if defined(B313_V6_SEQUENCE_DIAGNOSTIC) && B313_V6_SEQUENCE_DIAGNOSTIC
bool b313_sequence_enabled(void);
void b313_sequence_begin(unsigned tick);
void b313_sequence_end(unsigned tick);
void b313_sequence_before_level_event(unsigned type);
/* Internal synchronous boundary companions. Never reset nonce serials. */
void b313_slice_sequence_frame(unsigned tick,bool select);
bool b313_v6_lock_frame_retire(void);
bool b313_v6_prefix_frame_retire(void);
bool b313_v6_transaction_frame_retire(void);
bool b313_precommit_frame_retire(void);
bool b313_final_frame_retire(void);
bool nws_sequence_frame_retire(void);
bool ohs_sequence_frame_retire(void);
bool b313_pause_sequence_retire(void);
bool b313_pause_sequence_capture(const char *path);
#else
#define b313_sequence_enabled() false
#define b313_sequence_begin(...) ((void)0)
#define b313_sequence_end(...) ((void)0)
#define b313_sequence_before_level_event(...) ((void)0)
#endif
#endif
