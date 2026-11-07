/* Private fact logger only. No admission, renderer write or recovery APIs. */
#ifndef B313_FRAME_FACTS_H
#define B313_FRAME_FACTS_H
void b313_facts_snapshot(const char *stage,unsigned event_entry);
void b313_facts_allocate(const void *object);
void b313_facts_resource(unsigned pool,unsigned operation);
void b313_facts_draw(const char *stage,unsigned slot,unsigned part,int x,int y,const void *surface);
void b313_facts_attempt(const char *stage,unsigned family,unsigned offset,unsigned type,int result);
#endif
