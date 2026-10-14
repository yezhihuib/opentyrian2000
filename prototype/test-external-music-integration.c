/* Real LDS/OPL/decoder integration. GPL-2.0-or-later.
 * The runner supplies the unmodified historical callback from --baseline-ref.
 * Original music.mus is read privately; only sample/state hashes are reported.
 */
#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../src/loudness.c"
#include "../src/lds_play.c"
#include "integration-generated-bodies.h"

void JE_tyrianHalt(JE_byte code)
{
    fprintf(stderr, "Unexpected game halt: %u\n", code);
    exit(2);
}

typedef struct {
    uint64_t samples, lds;
    int next_rand;
    bool playing, looped;
} Result;

static uint64_t hash(uint64_t h, const void *bytes, size_t size)
{
    const unsigned char *p = bytes;
    while (size--) {
        h ^= *p++;
        h *= UINT64_C(1099511628211);
    }
    return h;
}
#define HASH_START UINT64_C(14695981039346656037)
#define HASH_FIELD(h, field) ((h) = hash((h), &(field), sizeof(field)))

static uint64_t lds_state(uint64_t h)
{
    HASH_FIELD(h, playing); HASH_FIELD(h, songlooped);
    HASH_FIELD(h, posplay); HASH_FIELD(h, pattplay);
    HASH_FIELD(h, tempo_now); HASH_FIELD(h, allvolume);
    HASH_FIELD(h, mainvolume); HASH_FIELD(h, fadeonoff);
    HASH_FIELD(h, samplesUntilLdsUpdate); HASH_FIELD(h, samplesUntilLdsUpdateFrac);
    h = hash(h, channel, sizeof channel);
    return hash(h, fmchip, sizeof fmchip);
}

static void reset_offline(void)
{
    assert(audioDevice == 0);
    deinit_audio();
    audio_disabled = music_disabled = samples_disabled = false;
    audioSampleRate = 44100;
    song_playing = UINT_MAX;
    samplesUntilLdsUpdate = samplesUntilLdsUpdateFrac = 0;
    samplesPerLdsUpdate = 2 * (audioSampleRate / ldsUpdate2Rate);
    samplesPerLdsUpdateFrac = 2 * (audioSampleRate % ldsUpdate2Rate);
    volumeFactorTable[0] = 0;
    for (size_t i = 1; i < 256; ++i)
        volumeFactorTable[i] = TO_FIXED(powf(10, (255 - i) * (-volumeRange / (20.0f * 255))));
    musicVolume = sampleVolume = 255;
    srand(0x5eed);
}

static Result run_song(unsigned int song, bool historical, unsigned int blocks)
{
    Sint16 output[1024];
    Result r = { HASH_START, HASH_START, 0, false, false };
    reset_offline();
    play_song(song);
    for (unsigned int i = 0; i < blocks; ++i) {
        size_t count = i % 3 == 0 ? 1 : i % 3 == 1 ? 255 : 1024;
        if (i == blocks / 3)
            set_volume(113, 255);
        if (i == blocks / 2)
            fade_song();
        if (historical)
            originalAudioCallback(NULL, (Uint8 *)output, (int)(count * sizeof *output));
        else
            audioCallback(NULL, (Uint8 *)output, (int)(count * sizeof *output));
        r.samples = hash(r.samples, output, count * sizeof *output);
        r.lds = lds_state(r.lds);
    }
    r.next_rand = rand();
    r.playing = playing;
    r.looped = songlooped;
    return r;
}

static void same_controls(Result a, Result b)
{
    assert(a.lds == b.lds && a.next_rand == b.next_rand);
    assert(a.playing == b.playing && a.looped == b.looped);
}

static void test_real_device(void)
{
    /* Real SDL dummy callbacks exercise activation/teardown ownership. This is
     * deliberately distinct from output-device listening or Windows testing. */
    assert(SDL_setenv("SDL_AUDIODRIVER", "dummy", 1) == 0);
    deinit_audio();
    for (unsigned int i = 0; i < 100; ++i) {
        audio_disabled = music_disabled = samples_disabled = false;
        assert(init_audio());
        play_song(17);
        SDL_Delay(30);
        SDL_LockAudioDevice(audioDevice);
        assert(externalMusic.samples != NULL && externalMusic.cursor > 0);
        SDL_UnlockAudioDevice(audioDevice);
        stop_song();
        SDL_LockAudioDevice(audioDevice);
        size_t cursor = externalMusic.cursor;
        SDL_UnlockAudioDevice(audioDevice);
        SDL_Delay(30);
        SDL_LockAudioDevice(audioDevice);
        assert(externalMusic.cursor == cursor);
        SDL_UnlockAudioDevice(audioDevice);
        play_song(17);
        restart_song();
        deinit_audio();
        assert(externalMusic.samples == NULL && audioDevice == 0);
        deinit_audio();
    }
    puts("PASS real SDL dummy device: 100 init/play/stop/resume/restart/close/repeated-teardown cycles");
}

int main(int argc, char **argv)
{
    assert(argc == 5);
    assert(SDL_Init(0) == 0);
    custom_data_dir = argv[1];
    load_music();
    assert(song_count == 41);
    /* All actual songs use actual OPL, not a fake sample generator. */
    for (unsigned int song = 0; song < song_count; ++song) {
        Result before = run_song(song, true, 300);
        Result after = run_song(song, false, 300);
        same_controls(before, after);
        assert(before.samples == after.samples);
    }
    puts("PASS real OPL: all 41 original songs are sample/state/RNG-identical without --music-dir");
    Result original = run_song(17, true, 600);
    assert(external_music_set_directory(argv[2])); /* Empty/missing directory. */
    Result missing = run_song(17, false, 600);
    same_controls(original, missing);
    assert(original.samples == missing.samples && externalMusic.samples == NULL);
    assert(external_music_set_directory(argv[3])); /* Corrupt track18.mp3. */
    Result rejected = run_song(17, false, 600);
    same_controls(original, rejected);
    assert(original.samples == rejected.samples && externalMusic.samples == NULL);
    assert(external_music_set_directory(argv[4])); /* Synthetic valid track18. */
    Result replacement = run_song(17, false, 600);
    same_controls(original, replacement);
    assert(original.samples != replacement.samples && externalMusic.samples != NULL);
    puts("PASS real integration: track18 missing/corrupt gives exact FM; valid MP3 changes samples while preserving LDS/RNG");
    /* A missing song after a valid replacement returns independently to FM. */
    Result mixed = run_song(2, false, 300);
    assert(externalMusic.samples == NULL);
    assert(external_music_set_directory(argv[2]));
    Result fallback = run_song(2, true, 300);
    same_controls(mixed, fallback);
    assert(mixed.samples == fallback.samples);
    assert(external_music_set_directory(argv[4]));
    test_real_device();
    fclose(music_file);
    music_file = NULL;
    free(song_offset);
    song_offset = NULL;
    SDL_Quit();
    puts("PASS all real integration checks; original music samples were not exported");
    return 0;
}
