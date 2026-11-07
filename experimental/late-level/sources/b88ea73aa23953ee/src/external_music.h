/* Optional external MP3 music. GPL-2.0-or-later; decoder separately licensed. */
#ifndef EXTERNAL_MUSIC_H
#define EXTERNAL_MUSIC_H
#include <SDL.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    Sint16 *samples;
    size_t count;
    size_t cursor;
} ExternalMusic;

/* Configure once, before starting audio. The argv string must remain alive. */
bool external_music_set_directory(const char *directory);
bool external_music_enabled(void);
/* Main thread only: complete bounded preparation, or empty result for FM fallback. */
ExternalMusic external_music_prepare(unsigned int song, int output_rate);
void external_music_free(ExternalMusic *music);
/* Audio callback only: bounded copy/wrap and Q8 gain; never allocates or decodes. */
void external_music_render(ExternalMusic *music, Sint16 *output, size_t count,
                           unsigned int volume_q8, bool playing);
#endif
