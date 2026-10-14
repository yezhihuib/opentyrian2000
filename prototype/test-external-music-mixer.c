/* Offline mixer contracts. GPL-2.0-or-later, like the production source.
 * Run through test-external-music-mixer.py, which supplies exact historical
 * callback/control bodies and the exact current external PCM render body.
 * This includes the real LDS engine; only file preparation and OPL are fakes.
 * SDL device entry points below are local stubs. No SDL runtime is linked.
 */
#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../src/loudness.c"
/* load_song uses the observable fixture loader; the unused real file loader
 * is discarded by function-section garbage collection. */
#define lds_load unusedRealLdsLoad
#include "../src/lds_play.c"
#undef lds_load
#include "mixer-generated-bodies.h"

static bool callback_active, option_enabled, prepare_fails;
static unsigned int locks, load_calls, prepare_calls, free_calls;
static unsigned int opl_calls, opl_frames, opl_init_calls, opl_write_calls;
static unsigned int close_calls, pause_calls, quit_calls;
static unsigned int last_prepared_song;
static uint64_t opl_partition;
static int last_prepared_rate;
static bool require_closed_before_free;
static const Sint16 fixture_pcm[] = { 1000, -2000, 3000, -4000, 5000, -6000, 7000 };
static Uint32 fixture_offsets[] = { 0, 100, 200, 300 };
static Sint16 sfx_data[8][4096];

/* Any accidental device initialization is a hard test failure. */
int SDLCALL SDL_InitSubSystem(Uint32 flags)
{
    (void)flags;
    assert(!"The offline mixer harness must not initialize SDL audio");
    return -1;
}
SDL_AudioDeviceID SDLCALL SDL_OpenAudioDevice(const char *device, int capture,
        const SDL_AudioSpec *want, SDL_AudioSpec *got, int changes)
{
    (void)device; (void)capture; (void)want; (void)got; (void)changes;
    assert(!"The offline mixer harness must not open an audio device");
    return 0;
}
void SDLCALL SDL_LockAudioDevice(SDL_AudioDeviceID device)
{
    (void)device;
    assert(!callback_active && locks == 0);
    ++locks;
}
void SDLCALL SDL_UnlockAudioDevice(SDL_AudioDeviceID device)
{
    (void)device;
    assert(!callback_active && locks == 1);
    --locks;
}
void SDLCALL SDL_PauseAudioDevice(SDL_AudioDeviceID device, int pause)
{
    assert(!callback_active && device == 42 && pause == 1);
    ++pause_calls;
}
void SDLCALL SDL_CloseAudioDevice(SDL_AudioDeviceID device)
{
    assert(!callback_active && device == 42);
    ++close_calls;
}
void SDLCALL SDL_QuitSubSystem(Uint32 flags)
{
    assert(!callback_active && flags == SDL_INIT_AUDIO);
    ++quit_calls;
}
void adlib_init(Bit32u rate)
{
    assert(rate == 44100);
    ++opl_init_calls;
}
void adlib_write(Bitu reg, Bit8u value)
{
    (void)reg; (void)value;
    ++opl_write_calls;
}
void adlib_getsample(Bit16s *output, Bits count)
{
    assert(callback_active && count > 0);
    ++opl_calls;
    opl_frames += (unsigned int)count;
    opl_partition = opl_partition * 131u + (unsigned int)count;
    /* Deliberately consume the process RNG, matching OPL's observable shared
     * rand() dependency; values need no platform-specific rand() golden. */
    for (Bits i = 0; i < count; ++i)
        output[i] = (Sint16)(rand() % 60001 - 30000);
}
bool lds_load(FILE *file, unsigned int offset, unsigned int size)
{
    (void)file;
    assert(!callback_active && locks == 0 && music_stopped);
    assert(offset % 100 == 0 && size == 100);
    ++load_calls;
    lds_rewind();
    return true;
}
bool external_music_enabled(void)
{
    assert(!callback_active);
    return option_enabled;
}
ExternalMusic external_music_prepare(unsigned int song, int rate)
{
    ExternalMusic result = { 0 };
    assert(!callback_active && locks == 0 && music_stopped);
    ++prepare_calls;
    last_prepared_song = song;
    last_prepared_rate = rate;
    if (!prepare_fails) {
        result.samples = malloc(sizeof fixture_pcm);
        assert(result.samples != NULL);
        memcpy(result.samples, fixture_pcm, sizeof fixture_pcm);
        result.count = sizeof fixture_pcm / sizeof *fixture_pcm;
    }
    return result;
}
void external_music_free(ExternalMusic *music)
{
    assert(!callback_active && locks == 0);
    if (music->samples != NULL) {
        if (require_closed_before_free)
            assert(close_calls == 1 && audioDevice == 0);
        ++free_calls;
        free(music->samples);
    }
    memset(music, 0, sizeof *music);
}

static void reset_fixture(void)
{
    assert(!callback_active && locks == 0);
    require_closed_before_free = false;
    external_music_free(&externalMusic);
    option_enabled = prepare_fails = false;
    load_calls = prepare_calls = free_calls = 0;
    opl_calls = opl_frames = opl_init_calls = opl_write_calls = 0;
    close_calls = pause_calls = quit_calls = 0;
    opl_partition = 0;
    last_prepared_song = UINT_MAX;
    last_prepared_rate = 0;
    audioSampleRate = 44100;
    audioDevice = 42;
    audio_disabled = music_disabled = samples_disabled = false;
    music_stopped = true;
    song_playing = 0;
    overrideSongLoaded = false;
    musicVolume = sampleVolume = 255;
    samplesPerLdsUpdate = 2 * (audioSampleRate / ldsUpdate2Rate);
    samplesPerLdsUpdateFrac = 2 * (audioSampleRate % ldsUpdate2Rate);
    samplesUntilLdsUpdate = samplesUntilLdsUpdateFrac = 0;
    song_count = 3;
    song_offset = fixture_offsets;
    music_file = NULL;
    memset(channelSamples, 0, sizeof channelSamples);
    memset(channelSampleCount, 0, sizeof channelSampleCount);
    memset(channelVolume, 0, sizeof channelVolume);
    volumeFactorTable[0] = 0;
    for (size_t i = 1; i < 256; ++i)
        volumeFactorTable[i] = TO_FIXED(powf(10, (255 - i) * (-volumeRange / (20.0f * 255))));
    /* The real LDS engine can tick with no loaded pattern. Synthetic command
     * tests install only finite, explicitly bounded position/pattern arrays. */
    positions = NULL;
    patterns = NULL;
    soundbank = NULL;
    regbd = tempo = pattlen = 0;
    memset(chandelay, 0, sizeof chandelay);
    lds_rewind();
    playing = false;
    opl_init_calls = opl_write_calls = 0;
    srand(0x5eed);
}

static void run_callback(void (*callback)(void *, Uint8 *, int), Sint16 *output, size_t count)
{
    assert(locks == 0 && !callback_active && count <= INT_MAX / sizeof *output);
    callback_active = true;
    callback(NULL, (Uint8 *)output, (int)(count * sizeof *output));
    callback_active = false;
}
static void render(Sint16 *output, size_t count)
{
    run_callback(audioCallback, output, count);
}
static void expect_silence(const Sint16 *output, size_t count)
{
    for (size_t i = 0; i < count; ++i)
        assert(output[i] == 0);
}
static void load_external(void)
{
    option_enabled = true;
    play_song(0);
    assert(externalMusic.samples != NULL && load_calls == 1 && prepare_calls == 1);
}
static void fill_sfx(bool varied)
{
    for (size_t c = 0; c < 8; ++c) {
        for (size_t i = 0; i < 4096; ++i)
            sfx_data[c][i] = varied ? (Sint16)((i * 613u + c * 991u) % 60001u - 30000) : 1024;
    }
}
static void start_all_sfx(size_t count, bool varied_lengths)
{
    static const size_t lengths[8] = { 1, 3, 19, 128, 257, 513, 1025, 4096 };
    for (size_t c = 0; c < 8; ++c)
        multiSamplePlay(sfx_data[c], varied_lengths ? lengths[c] : count, (Uint8)c, (Uint8)c);
}

typedef struct {
    unsigned int opl_calls, opl_frames, opl_write_calls;
    uint64_t opl_partition;
    size_t counts[8];
    const Sint16 *pointers[8];
    int until, fraction, next_rand;
    Uint8 tempo_now, allvolume;
    bool playing, looped;
} Observation;
static Observation observe(void)
{
    Observation state = { 0 };
    state.opl_calls = opl_calls;
    state.opl_frames = opl_frames;
    state.opl_write_calls = opl_write_calls;
    state.opl_partition = opl_partition;
    memcpy(state.counts, channelSampleCount, sizeof state.counts);
    memcpy(state.pointers, channelSamples, sizeof state.pointers);
    state.until = samplesUntilLdsUpdate;
    state.fraction = samplesUntilLdsUpdateFrac;
    state.next_rand = rand();
    state.tempo_now = tempo_now;
    state.allvolume = allvolume;
    state.playing = playing;
    state.looped = songlooped;
    return state;
}
static void same_observation(const Observation *a, const Observation *b)
{
    assert(a->opl_calls == b->opl_calls && a->opl_frames == b->opl_frames);
    assert(a->opl_partition == b->opl_partition && a->opl_write_calls == b->opl_write_calls);
    assert(memcmp(a->counts, b->counts, sizeof a->counts) == 0);
    assert(memcmp(a->pointers, b->pointers, sizeof a->pointers) == 0);
    assert(a->until == b->until && a->fraction == b->fraction && a->next_rand == b->next_rand);
    assert(a->tempo_now == b->tempo_now && a->allvolume == b->allvolume);
    assert(a->playing == b->playing && a->looped == b->looped);
}

static void test_original_callback_equivalence(void)
{
    static const Uint8 music_levels[] = { 0, 1, 128, 255 };
    static const Uint8 sample_levels[] = { 0, 93, 255 };
    static const size_t lengths[] = { 0, 1, 255, 1024, 4096 };
    Sint16 actual[4096], expected[4096];
    unsigned int cases = 0;
    fill_sfx(true);
    for (unsigned int mode = 0; mode < 16; ++mode)
    for (size_t m = 0; m < sizeof music_levels; ++m)
    for (size_t s = 0; s < sizeof sample_levels; ++s)
    for (size_t n = 0; n < sizeof lengths / sizeof *lengths; ++n) {
        Observation before_patch, after_patch;
        for (unsigned int pass = 0; pass < 2; ++pass) {
            reset_fixture();
            playing = true;
            /* Feed all eight channels before applying sample mute, so frozen
             * channel state is compared too. */
            if (mode & 8)
                start_all_sfx(4096, true);
            music_disabled = (mode & 1) != 0;
            samples_disabled = (mode & 2) != 0;
            music_stopped = (mode & 4) != 0;
            musicVolume = music_levels[m];
            sampleVolume = sample_levels[s];
            if (pass == 0) {
                run_callback(originalAudioCallback, expected, lengths[n]);
                before_patch = observe();
            } else {
                render(actual, lengths[n]);
                after_patch = observe();
            }
        }
        assert(memcmp(actual, expected, lengths[n] * sizeof *actual) == 0);
        same_observation(&before_patch, &after_patch);
        ++cases;
    }
    printf("PASS original callback: %u deterministic FM/SFX/mute/volume/buffer cases, byte-identical state and samples\n", cases);
}

static void test_song_controls(void)
{
    Sint16 output[32];
    reset_fixture();
    originalPlaySong(0);
    assert(load_calls == 0 && !music_stopped && !playing);
    reset_fixture();
    play_song(0);
    assert(load_calls == 0 && prepare_calls == 0 && !music_stopped && !playing);
    assert(externalMusic.samples == NULL && !overrideSongLoaded);
    play_song(1);
    assert(load_calls == 1 && prepare_calls == 0 && song_playing == 1 && playing);

    reset_fixture();
    load_external();
    assert(last_prepared_song == 0 && last_prepared_rate == 44100);
    assert(song_playing == 0 && overrideSongLoaded && externalMusic.cursor == 0);
    render(output, 3);
    assert(externalMusic.cursor == 3);
    Sint16 *saved = externalMusic.samples;
    stop_song();
    play_song(0);
    assert(load_calls == 1 && prepare_calls == 1 && free_calls == 0);
    assert(externalMusic.samples == saved && externalMusic.cursor == 3);
    render(output, 1);
    assert(output[0] == fixture_pcm[3]);
    songlooped = true;
    playing = false;
    allvolume = 73;
    int saved_until = samplesUntilLdsUpdate;
    restart_song();
    assert(externalMusic.cursor == 0 && playing && !songlooped && !music_stopped);
    assert(allvolume == 0 && samplesUntilLdsUpdate == saved_until);
    assert(load_calls == 1 && prepare_calls == 1 && free_calls == 0);
    render(output, 1);
    assert(output[0] == fixture_pcm[0]);
    play_song(1);
    assert(load_calls == 2 && prepare_calls == 2 && free_calls == 1);
    assert(song_playing == 1 && last_prepared_song == 1 && externalMusic.cursor == 0);

    reset_fixture();
    option_enabled = prepare_fails = true;
    play_song(0);
    assert(load_calls == 1 && prepare_calls == 1 && externalMusic.samples == NULL && playing);
    stop_song();
    play_song(0);
    assert(load_calls == 1 && prepare_calls == 1 && !music_stopped);
    puts("PASS controls: historical song zero, opted-in song zero, resume, restart, track replacement, and failed-prepare fallback");
}

static void test_freeze_and_mixer(void)
{
    Sint16 output[32];
    reset_fixture();
    load_external();
    fill_sfx(false);
    render(output, 2);
    for (unsigned int muted = 0; muted < 2; ++muted) {
        size_t cursor = externalMusic.cursor;
        unsigned int previous_frames = opl_frames;
        int until = samplesUntilLdsUpdate;
        Uint8 previous_tempo = tempo_now;
        start_all_sfx(3, false);
        if (muted)
            music_disabled = true;
        else
            stop_song();
        render(output, 3);
        for (size_t i = 0; i < 3; ++i)
            assert(output[i] == 4608); /* 1024 * (1 + ... + 8) / 8 */
        assert(externalMusic.cursor == cursor && opl_frames == previous_frames);
        assert(samplesUntilLdsUpdate == until && tempo_now == previous_tempo);
        for (size_t c = 0; c < 8; ++c)
            assert(channelSampleCount[c] == 0);
        music_disabled = false;
        play_song(0);
    }
    restart_song();
    start_all_sfx(3, false);
    set_volume(0, 255);
    render(output, 3);
    for (size_t i = 0; i < 3; ++i)
        assert(output[i] == 4608);
    assert(externalMusic.cursor == 3); /* Volume zero remains time-continuous. */
    restart_song();
    start_all_sfx(3, false);
    set_volume(255, 0);
    render(output, 3);
    for (size_t i = 0; i < 3; ++i)
        assert(output[i] == fixture_pcm[i]);
    for (size_t c = 0; c < 8; ++c)
        assert(channelSampleCount[c] == 0);
    set_volume(0, 0);
    render(output, 2);
    expect_silence(output, 2);
    assert(externalMusic.cursor == 5);

    restart_song();
    set_volume(255, 255);
    start_all_sfx(3, false);
    samples_disabled = true;
    render(output, 3);
    for (size_t i = 0; i < 3; ++i)
        assert(output[i] == fixture_pcm[i]);
    for (size_t c = 0; c < 8; ++c)
        assert(channelSampleCount[c] == 3);
    samples_disabled = false;
    for (size_t c = 0; c < 8; ++c) {
        sfx_data[c][0] = INT16_MAX;
        sfx_data[c][1] = INT16_MIN;
        multiSamplePlay(sfx_data[c], 2, (Uint8)c, 7);
    }
    externalMusic.samples[0] = INT16_MAX;
    externalMusic.samples[1] = INT16_MIN;
    externalMusic.cursor = 0;
    render(output, 2);
    assert(output[0] == INT16_MAX && output[1] == INT16_MIN);
    for (size_t c = 0; c < 8; ++c)
        assert(channelSampleCount[c] == 0);
    puts("PASS mix: stop/mute freeze music while all eight SFX run; zero volumes, unity PCM gain, SFX mute, both clipping limits");
}

static void test_opl_rng_and_lds(void)
{
    Sint16 output[32];
    Observation fm, pcm;
    for (unsigned int pass = 0; pass < 2; ++pass) {
        reset_fixture();
        if (pass)
            load_external();
        else {
            play_song(1);
            song_playing = 0;
        }
        samplesPerLdsUpdate = 5;
        samplesPerLdsUpdateFrac = 37;
        render(output, 32);
        if (pass)
            pcm = observe();
        else
            fm = observe();
    }
    same_observation(&fm, &pcm);
    assert(pcm.opl_frames == 32 && pcm.opl_calls > 1);

    reset_fixture();
    load_external();
    samplesUntilLdsUpdate = 100;
    allvolume = 128;
    render(output, 3);
    for (size_t i = 0; i < 3; ++i)
        assert(output[i] == fixture_pcm[i] / 2);
    allvolume = 0;
    assert(lds_get_master_volume_q8() == 256 && allvolume == 0);
    allvolume = 1;
    assert(lds_get_master_volume_q8() == 1 && allvolume == 1);
    allvolume = 255;
    assert(lds_get_master_volume_q8() == 255 && allvolume == 255);
    size_t cursor = externalMusic.cursor;
    playing = false;
    render(output, 3);
    expect_silence(output, 3);
    assert(externalMusic.cursor == cursor);
    assert(opl_frames == 6); /* Original OPL still advances after LDS stop. */

    /* Exercise the actual LDS hard-fade path, not an equivalent fake. */
    restart_song();
    samplesUntilLdsUpdate = samplesUntilLdsUpdateFrac = 0;
    samplesPerLdsUpdate = 1;
    samplesPerLdsUpdateFrac = 0;
    allvolume = 2;
    hardfade = 1;
    fade_song();
    render(output, 2);
    assert(output[0] == fixture_pcm[0] / 256 && output[1] == 0);
    assert(!playing && hardfade == 0 && externalMusic.cursor == 1);
    puts("PASS timing: OPL call partitions/shared RNG preserved; actual LDS gain, stop and hard-fade silence PCM");
}

static void install_command(Uint16 command, bool backwards)
{
    static Position command_positions[18];
    static Uint16 command_patterns[2];
    memset(command_positions, 0, sizeof command_positions);
    for (size_t i = 0; i < 18; ++i)
        command_positions[i].patnum = (i % 9 == 0) ? 0 : 1;
    command_patterns[0] = command;
    command_patterns[1] = 0;
    positions = command_positions;
    patterns = command_patterns;
    tempo_now = 0;
    tempo = 255;
    pattlen = 64;
    posplay = backwards ? 1 : 0;
    samplesUntilLdsUpdate = samplesUntilLdsUpdateFrac = 0;
}
static void test_real_lds_commands_and_looping(void)
{
    Sint16 output[32];
    reset_fixture();
    load_external();
    render(output, 16);
    assert(externalMusic.cursor == 2 && !songlooped); /* PCM wrapping alone. */
    install_command(0xf900, true); /* Backward LDS jump sets the original flag. */
    render(output, 1);
    assert(songlooped && playing && posplay == 0 && externalMusic.cursor == 3);
    assert(output[0] == fixture_pcm[2]);
    positions = NULL;
    patterns = NULL;

    restart_song();
    install_command(0xfc00, false); /* Actual LDS stop command. */
    render(output, 2);
    expect_silence(output, 2);
    assert(!playing && externalMusic.cursor == 0);
    positions = NULL;
    patterns = NULL;

    restart_song();
    install_command(0xf480, false); /* Actual LDS master-volume command. */
    render(output, 2);
    assert(allvolume == 128 && output[0] == fixture_pcm[0] / 2 && output[1] == fixture_pcm[1] / 2);
    positions = NULL;
    patterns = NULL;
    puts("PASS LDS commands: PCM wrapping preserves songlooped; real backward jump, stop and master-volume commands retain semantics");
}

static void test_teardown_and_disabled_controls(void)
{
    reset_fixture();
    load_external();
    audio_disabled = true;
    size_t cursor = externalMusic.cursor;
    play_song(1);
    stop_song();
    restart_song();
    fade_song();
    set_volume(0, 0);
    assert(song_playing == 0 && !music_stopped && externalMusic.cursor == cursor);
    assert(load_calls == 1 && prepare_calls == 1 && musicVolume == 255 && sampleVolume == 255);
    require_closed_before_free = true;
    deinit_audio();
    assert(close_calls == 1 && pause_calls == 1 && free_calls == 1);
    assert(externalMusic.samples == NULL && externalMusic.count == 0 && externalMusic.cursor == 0);
    assert(audioDevice == 0 && music_stopped && !overrideSongLoaded);
    deinit_audio();
    assert(close_calls == 1 && free_calls == 1 && quit_calls == 2);
    reset_fixture();
    audioDevice = 0;
    audio_disabled = true;
    deinit_audio();
    assert(close_calls == 0 && free_calls == 0);
    puts("PASS teardown: disabled controls, close-before-free ownership, repeated cleanup and failed-init cleanup");
}

int main(void)
{
    test_original_callback_equivalence();
    test_song_controls();
    test_freeze_and_mixer();
    test_opl_rng_and_lds();
    test_real_lds_commands_and_looping();
    test_teardown_and_disabled_controls();
    assert(locks == 0 && !callback_active);
    puts("PASS all offline mixer contracts (no SDL audio initialization/device, no game run)");
    return 0;
}
