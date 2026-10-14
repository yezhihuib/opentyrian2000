/* Offline decoder/ownership tests. Synthetic tones only; no audio device. */
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

static int fail_after = -1;
static size_t allocations, outstanding;
static void *test_malloc(size_t size)
{
    void *ptr;
    if (fail_after == 0)
        return NULL;
    if (fail_after > 0)
        --fail_after;
    ++allocations;
    ptr = malloc(size);
    if (ptr != NULL)
        ++outstanding;
    return ptr;
}
static void test_free(void *ptr)
{
    if (ptr != NULL) {
        assert(outstanding > 0);
        --outstanding;
    }
    free(ptr);
}
#define MUSIC_MALLOC test_malloc
#define MUSIC_FREE test_free
#include "../src/external_music.c"

static void test_wrap(void)
{
    Sint16 values[] = { 1000, -1000, 32767, -32768 };
    Sint16 output[17];
    ExternalMusic m = { values, 4, 0 };
    external_music_render(&m, output, 17, 256, true);
    for (size_t i = 0; i < 17; ++i)
        assert(output[i] == values[i % 4]);
    assert(m.cursor == 1);
    external_music_render(&m, output, 17, 256, false);
    for (size_t i = 0; i < 17; ++i)
        assert(output[i] == 0);
    assert(m.cursor == 1);
    m.cursor = 0;
    external_music_render(&m, output, 4, 1, true);
    assert(output[0] == 3 && output[1] == -3 && output[2] == 127 && output[3] == -128);
    assert(m.cursor == 0);
    external_music_render(&m, output, 4, 255, true);
    assert(output[0] == 996 && output[1] == -996);
    m.count = 1;
    m.cursor = 0;
    external_music_render(&m, output, 17, 256, true);
    for (size_t i = 0; i < 17; ++i)
        assert(output[i] == 1000);
    assert(m.cursor == 0);
}

static void test_layout_limits(void)
{
    /* Newly synthesized MPEG1 Layer III framing, no copyrighted audio. */
    const unsigned char header[] = { 0xff, 0xfb, 0x90, 0x00 };
    Mp3Layout layout;
    size_t frames = 44100u * 600u / 1152u;
    unsigned char *bytes = calloc(frames + 1, 417);
    assert(bytes != NULL);
    for (size_t i = 0; i <= frames; ++i)
        memcpy(bytes + i * 417, header, 4);
    assert(mp3_layout(bytes, frames * 417, &layout));
    assert(layout.max_frames == frames * 1152);
    assert(!mp3_layout(bytes, (frames + 1) * 417, &layout));
    assert(!mp3_layout(bytes, 417 - 1, &layout));
    bytes[417 + 3] = 0xc0; /* Midstream mono/stereo change. */
    assert(!mp3_layout(bytes, 834, &layout));
    bytes[417 + 3] = 0;
    bytes[417 + 2] = 0x94; /* Midstream sample-rate change. */
    assert(!mp3_layout(bytes, 834, &layout));
    bytes[417 + 2] = 0x90;
    memcpy(bytes + 36, "Xing", 4);
    memset(bytes + 40, 0xff, 8); /* Impossible flags/frame count. */
    assert(!mp3_layout(bytes, 834, &layout));
    free(bytes);
    {
        unsigned char bad_tag[] = { 'I','D','3',4,0,0,127,127,127,127,0xff };
        assert(!mp3_layout(bad_tag, sizeof bad_tag, &layout));
        bad_tag[6] = 128;
        assert(!mp3_layout(bad_tag, sizeof bad_tag, &layout));
    }
    {
        unsigned char tagged[20 + 834] = { 'I', 'D', '3', 4, 0, 0 };
        memcpy(tagged + 10, header, 4);
        memcpy(tagged + 10 + 417, header, 4);
        for (unsigned int version = 2; version <= 4; ++version) {
            tagged[3] = (unsigned char)version;
            tagged[5] = 0;
            assert(mp3_layout(tagged, 10 + 834, &layout));
            tagged[5] = 1; /* Reserved in every supported ID3 version. */
            assert(!mp3_layout(tagged, 10 + 834, &layout));
        }
        tagged[3] = 3;
        tagged[5] = 16; /* v2.3 does not have a footer flag. */
        assert(!mp3_layout(tagged, 10 + 834, &layout));
        tagged[3] = 4;
        memcpy(tagged + 10, "3DI", 3);
        memcpy(tagged + 13, tagged + 3, 7);
        memset(tagged + 20, 0, 834);
        memcpy(tagged + 20, header, 4);
        memcpy(tagged + 20 + 417, header, 4);
        assert(mp3_layout(tagged, sizeof tagged, &layout));
        tagged[14] = 1; /* Footer revision differs from the header. */
        assert(!mp3_layout(tagged, sizeof tagged, &layout));
        tagged[14] = 0;
        tagged[19] = 1; /* Footer length differs from the header. */
        assert(!mp3_layout(tagged, sizeof tagged, &layout));
        assert(!mp3_layout(tagged, 19, &layout));
    }
    /* Finite deterministic fuzz coverage of all preflight branches. */
    uint32_t random = 1;
    unsigned char noise[4096];
    for (size_t t = 0; t < 1000; ++t) {
        size_t size = t * 31 % sizeof noise;
        for (size_t i = 0; i < size; ++i) {
            random = random * 1664525u + 1013904223u;
            noise[i] = (unsigned char)(random >> 24);
        }
        (void)mp3_layout(noise, size, &layout);
    }
}

static void test_budget(void)
{
    MusicBudget budget = { 0 };
    void *ptr = music_alloc(64, &budget);
    assert(ptr != NULL && budget.used == 64 + sizeof(AllocationHeader));
    assert(music_alloc(SIZE_MAX, &budget) == NULL);
    assert(music_alloc(TEMP_LIMIT, &budget) == NULL);
    ptr = music_realloc(ptr, 128, &budget);
    assert(ptr != NULL && budget.used == 128 + sizeof(AllocationHeader));
    music_free(ptr, &budget);
    assert(budget.used == 0 && outstanding == 0);
    budget.used = TEMP_LIMIT - 64;
    assert(music_alloc(65, &budget) == NULL);
    budget.used = 0;
}

static void test_vendor_truncation(const char *directory)
{
    char path[4096];
    unsigned char data[8192];
    FILE *file;
    size_t size, skip = 0;
    snprintf(path, sizeof path, "%s/track01.mp3", directory);
    file = fopen(path, "rb");
    assert(file != NULL);
    size = fread(data, 1, sizeof data, file);
    fclose(file);
    if (memcmp(data, "ID3", 3) == 0)
        skip = 10 + ((size_t)data[6] << 21) + ((size_t)data[7] << 14) + ((size_t)data[8] << 7) + data[9];
    assert(skip < size && size - skip > 1024);
    /* Exercise upstream Xing/Info/LAME bounds on every short prefix directly,
     * independent of the application's stricter complete-frame preflight. */
    for (size_t length = 1; length <= 1024; ++length) {
        drmp3 decoder;
        MusicBudget budget = { 0 };
        drmp3_allocation_callbacks cb = { &budget, music_alloc, music_realloc, music_free };
        if (drmp3_init_memory(&decoder, data + skip, length, &cb)) {
            drmp3_int16 output[DECODE_CHUNK * 2];
            assert(drmp3_read_pcm_frames_s16(&decoder, DECODE_CHUNK, output) <= DECODE_CHUNK);
            drmp3_uninit(&decoder);
        }
        assert(budget.used == 0 && outstanding == 0);
    }
}

int main(int argc, char **argv)
{
    ExternalMusic music;
    size_t used_allocations;
    assert(argc == 2);
    test_wrap();
    test_layout_limits();
    test_budget();
    test_vendor_truncation(argv[1]);
    assert(!external_music_enabled());
    assert(!external_music_set_directory(NULL));
    assert(!external_music_set_directory(""));
    allocations = 0;
    music = external_music_prepare(17, 44100);
    assert(music.samples == NULL && allocations == 0);
    assert(external_music_set_directory(argv[1]));
    /* Matrix: synthetic mono/stereo, CBR/VBR, source rates and resampling. */
    for (unsigned int song = 0; song < 6; ++song) {
        for (unsigned int rate = 0; rate < 3; ++rate) {
            int target[] = { 22050, 44100, 48000 };
            double energy = 0;
            music = external_music_prepare(song, target[rate]);
            assert(music.samples != NULL && music.count > (size_t)target[rate] / 3);
            assert(music.count < (size_t)target[rate] * 2);
            for (size_t i = 0; i < music.count; ++i)
                energy += (double)music.samples[i] * music.samples[i];
            assert(sqrt(energy / music.count) > 500);
            external_music_free(&music);
            assert(outstanding == 0);
        }
    }
    /* Equal/opposite stereo channels must downmix nearly to silence. */
    music = external_music_prepare(6, 44100);
    assert(music.samples != NULL);
    {
        double sum = 0;
        for (size_t i = 0; i < music.count; ++i)
            sum += (double)music.samples[i] * music.samples[i];
        assert(sqrt(sum / music.count) < 10);
    }
    external_music_free(&music);
    /* Missing, empty, random, truncated, malformed, over-cap and format-change files. */
    for (unsigned int song = 7; song <= 16; ++song) {
        music = external_music_prepare(song, 44100);
        assert(music.samples == NULL && outstanding == 0);
    }
    music = external_music_prepare(0, INT_MAX);
    assert(music.samples == NULL && outstanding == 0);
    /* Fail every allocation in successful preparation, including conversion. */
    allocations = 0;
    music = external_music_prepare(0, 48000);
    assert(music.samples != NULL);
    used_allocations = allocations;
    external_music_free(&music);
    for (size_t i = 0; i < used_allocations; ++i) {
        fail_after = (int)i;
        music = external_music_prepare(0, 48000);
        external_music_free(&music);
        assert(outstanding == 0);
    }
    fail_after = -1;
    for (unsigned int i = 0; i < 100; ++i) {
        music = external_music_prepare(i % 6, i % 2 ? 44100 : 48000);
        assert(music.samples != NULL);
        external_music_free(&music);
        external_music_free(&music);
        assert(outstanding == 0);
    }
    music = external_music_prepare(17, 44100);
    assert(music.samples != NULL && music.count > 598u * 44100u);
    assert(music.count <= 600u * 44100u);
    external_music_free(&music);
    music = external_music_prepare(18, 44100);
    assert(music.samples != NULL); /* Exact 32 MiB input cap with zero padding. */
    external_music_free(&music);
    music = external_music_prepare(19, 44100); /* ID3v2.4 with matching footer. */
    assert(music.samples != NULL);
    external_music_free(&music);
    for (unsigned int song = 20; song <= 21; ++song) {
        music = external_music_prepare(song, 44100);
        assert(music.samples == NULL && outstanding == 0);
    }
    assert(outstanding == 0);
    printf("PASS: decoder matrix, stereo downmix, framing/limits/fuzz, allocator failures (%zu), 100 preparations, PCM wrap; no audio device\n", used_allocations);
    return 0;
}
