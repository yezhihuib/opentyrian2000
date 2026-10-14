/* Optional external MP3 music. GPL-2.0-or-later.
 * dr_mp3 is independently licensed under MIT-0; see third_party notices.
 */
#include "external_music.h"

#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DR_MP3_IMPLEMENTATION
#define DR_MP3_NO_STDIO
#include "third_party/dr_mp3.h"

#define INPUT_LIMIT ((size_t)32 * 1024 * 1024)
#define PCM_LIMIT ((size_t)64 * 1024 * 1024)
#define TEMP_LIMIT ((size_t)256 * 1024 * 1024)
#define DURATION_LIMIT 600u
#define DECODE_CHUNK 1152u

static const char *musicDirectory;

typedef struct {
    size_t used, peak;
} MusicBudget;

/* Header alignment suffices for the decoder's ordinary C allocations. */
typedef union {
    struct { size_t size; } allocation;
    long double align_float;
    void *align_pointer;
    uint64_t align_integer;
} AllocationHeader;

#ifndef MUSIC_MALLOC
#define MUSIC_MALLOC malloc
#define MUSIC_FREE free
#endif

static void *music_alloc(size_t size, void *user)
{
    MusicBudget *budget = user;
    AllocationHeader *header;
    size_t total;
    if (size == 0 || size > SIZE_MAX - sizeof *header)
        return NULL;
    total = size + sizeof *header;
    if (total > TEMP_LIMIT - budget->used)
        return NULL;
    header = MUSIC_MALLOC(total);
    if (header == NULL)
        return NULL;
    header->allocation.size = total;
    budget->used += total;
    if (budget->used > budget->peak)
        budget->peak = budget->used;
    return header + 1;
}

static void music_free(void *ptr, void *user)
{
    if (ptr != NULL) {
        AllocationHeader *header = (AllocationHeader *)ptr - 1;
        MusicBudget *budget = user;
        if (budget != NULL)
            budget->used -= header->allocation.size;
        MUSIC_FREE(header);
    }
}

static void *music_realloc(void *ptr, size_t size, void *user)
{
    void *next;
    if (size == 0) {
        music_free(ptr, user);
        return NULL;
    }
    /* Account for both buffers during growth, including allocator headers. */
    next = music_alloc(size, user);
    if (next != NULL) {
        if (ptr != NULL) {
            size_t old = ((AllocationHeader *)ptr - 1)->allocation.size - sizeof(AllocationHeader);
            memcpy(next, ptr, old < size ? old : size);
        }
        music_free(ptr, user);
    }
    return next;
}

bool external_music_set_directory(const char *directory)
{
    if (directory == NULL || directory[0] == '\0')
        return false;
    musicDirectory = directory;
    return true;
}

bool external_music_enabled(void)
{
    return musicDirectory != NULL;
}

static uint32_t read_be32(const unsigned char *p)
{
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8) | p[3];
}

typedef struct {
    unsigned int rate, channels;
    size_t max_frames;
} Mp3Layout;

/* Conservative bounded framing check before invoking the tolerant decoder.
 * Supports complete MPEG Layer III frames with ID3v2, ID3v1 and zero padding.
 * Rejects free-format streams, junk, truncated frames and format changes.
 * This is not a CRC/content-integrity certificate for compressed audio.
 */
static bool mp3_layout(const unsigned char *data, size_t size, Mp3Layout *layout)
{
    static const unsigned int rates[3] = { 44100, 48000, 32000 };
    static const unsigned int bitrate1[15] = { 0,32,40,48,56,64,80,96,112,128,160,192,224,256,320 };
    static const unsigned int bitrate2[15] = { 0,8,16,24,32,40,48,56,64,80,96,112,128,144,160 };
    size_t pos = 0, frames = 0, samples = 0;
    uint32_t declared_frames = 0;
    unsigned int first_version = 0;
    memset(layout, 0, sizeof *layout);
    if (size >= 10 && memcmp(data, "ID3", 3) == 0) {
        size_t tag;
        unsigned int reserved_flags;
        if (data[3] < 2 || data[3] > 4 || data[4] == 255 ||
            ((data[6] | data[7] | data[8] | data[9]) & 128))
            return false;
        /* Unknown flags can change tag layout. In particular, only v2.4 has
         * a footer bit; don't let the decoder skip audio for a reserved bit
         * in an older version. See ID3v2.2/2.3/2.4 header definitions. */
        reserved_flags = data[3] == 2 ? 0x3f : data[3] == 3 ? 0x1f : 0x0f;
        if (data[5] & reserved_flags)
            return false;
        tag = ((size_t)data[6] << 21) | ((size_t)data[7] << 14) |
              ((size_t)data[8] << 7) | data[9];
        if (tag > size - 10)
            return false;
        pos = 10 + tag;
        if (data[3] == 4 && (data[5] & 16)) {
            if (size - pos < 10 || memcmp(data + pos, "3DI", 3) != 0 ||
                memcmp(data + pos + 3, data + 3, 7) != 0)
                return false;
            pos += 10;
        }
    }
    while (pos < size) {
        uint32_t h;
        unsigned int version, bitrate, rate_index, rate, channels, frame_samples;
        size_t bytes;
        if (size - pos == 128 && memcmp(data + pos, "TAG", 3) == 0) {
            pos = size;
            break;
        }
        if (data[pos] == 0) {
            while (pos < size && data[pos] == 0)
                ++pos;
            if (pos != size)
                return false;
            break;
        }
        if (size - pos < 4)
            return false;
        h = read_be32(data + pos);
        version = (h >> 19) & 3;
        bitrate = (h >> 12) & 15;
        rate_index = (h >> 10) & 3;
        if ((h & 0xffe00000u) != 0xffe00000u || version == 1 ||
            ((h >> 17) & 3) != 1 || bitrate == 0 || bitrate == 15 || rate_index == 3)
            return false;
        rate = rates[rate_index] >> (version == 3 ? 0 : version == 2 ? 1 : 2);
        channels = ((h >> 6) & 3) == 3 ? 1 : 2;
        frame_samples = version == 3 ? 1152 : 576;
        bitrate = (version == 3 ? bitrate1[bitrate] : bitrate2[bitrate]) * 1000;
        bytes = (version == 3 ? 144u : 72u) * bitrate / rate + ((h >> 9) & 1);
        if (bytes < 4 || bytes > size - pos)
            return false;
        if (frames == 0) {
            size_t offset = 4 + ((h & 0x10000u) ? 0 : 2) +
                            (version == 3 ? (channels == 1 ? 17 : 32) : (channels == 1 ? 9 : 17));
            first_version = version;
            layout->rate = rate;
            layout->channels = channels;
            if (offset <= bytes && bytes - offset >= 4 &&
                (memcmp(data + pos + offset, "Xing", 4) == 0 || memcmp(data + pos + offset, "Info", 4) == 0)) {
                uint32_t flags;
                if (bytes - offset < 8)
                    return false;
                flags = read_be32(data + pos + offset + 4);
                offset += 8;
                if (flags & 1) {
                    if (bytes - offset < 4)
                        return false;
                    declared_frames = read_be32(data + pos + offset);
                    if (declared_frames == 0 || declared_frames > (uint64_t)rate * DURATION_LIMIT / frame_samples + 1)
                        return false;
                    offset += 4;
                }
                if (flags & 2) {
                    uint32_t declared_bytes;
                    if (bytes - offset < 4)
                        return false;
                    declared_bytes = read_be32(data + pos + offset);
                    if (declared_bytes > size - pos || declared_bytes < bytes)
                        return false;
                    offset += 4;
                }
                if (flags & 4) {
                    if (bytes - offset < 100)
                        return false;
                    offset += 100;
                }
                if (flags & 8) {
                    if (bytes - offset < 4)
                        return false;
                    offset += 4;
                }
                if (bytes - offset >= 4 && memcmp(data + pos + offset, "LAME", 4) == 0 && bytes - offset < 36)
                    return false;
            }
        } else if (rate != layout->rate || channels != layout->channels || version != first_version) {
            return false;
        }
        if (samples > (size_t)rate * DURATION_LIMIT - frame_samples)
            return false;
        samples += frame_samples;
        ++frames;
        pos += bytes;
    }
    if (frames == 0 || (declared_frames != 0 && declared_frames != frames && declared_frames != frames - 1))
        return false;
    layout->max_frames = samples;
    return true;
}

ExternalMusic external_music_prepare(unsigned int song, int output_rate)
{
    ExternalMusic result = { 0 };
    MusicBudget budget = { 0 };
    drmp3 decoder;
    drmp3_allocation_callbacks callbacks = { &budget, music_alloc, music_realloc, music_free };
    bool initialized = false;
    unsigned char *input = NULL;
    Sint16 *mono = NULL;
    char *path = NULL;
    SDL_RWops *file = NULL;
    SDL_AudioCVT cvt;
    Mp3Layout layout;
    size_t input_size, read_total = 0, count = 0, capacity;
    const char *reason = "resource or conversion failure";
    Uint64 started, frequency;
    if (!external_music_enabled())
        return result;
    started = SDL_GetPerformanceCounter();
    frequency = SDL_GetPerformanceFrequency();
    memset(&cvt, 0, sizeof cvt);
    memset(&decoder, 0, sizeof decoder);
    if (output_rate <= 0 || song == UINT_MAX)
        goto done;
    {
        size_t length = strlen(musicDirectory);
        int written;
        if (length > SIZE_MAX - 32)
            goto done;
        path = music_alloc(length + 32, &budget);
        if (path == NULL)
            goto done;
        written = snprintf(path, length + 32, "%s/track%02u.mp3", musicDirectory, song + 1);
        if (written < 0 || (size_t)written >= length + 32)
            goto done;
    }
    file = SDL_RWFromFile(path, "rb"); /* UTF-8 paths, including on Windows. */
    if (file == NULL) {
        reason = "missing or unreadable file";
        goto done;
    }
    {
        Sint64 bytes = SDL_RWsize(file);
        if (bytes <= 0 || bytes > (Sint64)INPUT_LIMIT) {
            reason = "empty or over 32 MiB file";
            goto done;
        }
        input_size = (size_t)bytes;
    }
    input = music_alloc(input_size, &budget);
    if (input == NULL)
        goto done;
    while (read_total < input_size) {
        size_t chunk = input_size - read_total;
        size_t got;
        if (chunk > 65536)
            chunk = 65536;
        got = SDL_RWread(file, input + read_total, 1, chunk);
        if (got == 0 || got > chunk) {
            reason = "short file read";
            goto done;
        }
        read_total += got;
    }
    {
        unsigned char extra;
        if (SDL_RWread(file, &extra, 1, 1) != 0) {
            reason = "file changed during read";
            goto done;
        }
    }
    SDL_RWclose(file);
    file = NULL;
    if (!mp3_layout(input, input_size, &layout)) {
        reason = "unsupported, truncated, inconsistent or over 10 minute MP3";
        goto done;
    }
    if (layout.max_frames > PCM_LIMIT / sizeof(Sint16) ||
        ((uint64_t)layout.max_frames * (unsigned int)output_rate + layout.rate - 1) / layout.rate > PCM_LIMIT / sizeof(Sint16)) {
        reason = "PCM exceeds 64 MiB";
        goto done;
    }
    capacity = layout.max_frames;
    mono = music_alloc(capacity * sizeof *mono, &budget);
    if (mono == NULL)
        goto done;
    if (!drmp3_init_memory(&decoder, input, input_size, &callbacks)) {
        reason = "decoder initialization failed";
        goto done;
    }
    initialized = true;
    if (decoder.channels != layout.channels || decoder.sampleRate != layout.rate) {
        reason = "decoder format mismatch";
        goto done;
    }
    for (;;) {
        drmp3_int16 chunk[DECODE_CHUNK * 2];
        drmp3_uint64 got = drmp3_read_pcm_frames_s16(&decoder, DECODE_CHUNK, chunk);
        size_t i;
        if (got > DECODE_CHUNK || got > capacity - count ||
            decoder.channels != layout.channels || decoder.sampleRate != layout.rate) {
            reason = "decoded frame or format limit";
            goto done;
        }
        if (got == 0)
            break;
        for (i = 0; i < (size_t)got; ++i)
            mono[count + i] = layout.channels == 1 ? chunk[i] :
                (Sint16)(((Sint32)chunk[2 * i] + (Sint32)chunk[2 * i + 1]) / 2);
        count += (size_t)got;
    }
    if (count == 0) {
        reason = "no decoded PCM";
        goto done;
    }
    drmp3_uninit(&decoder);
    initialized = false;
    music_free(input, &budget);
    input = NULL;
    if (SDL_BuildAudioCVT(&cvt, AUDIO_S16SYS, 1, (int)layout.rate,
                         AUDIO_S16SYS, 1, output_rate) < 0)
        goto done;
    if (count > INT_MAX / sizeof *mono || cvt.len_mult < 1 ||
        (size_t)cvt.len_mult > SIZE_MAX / (count * sizeof *mono))
        goto done;
    cvt.len = (int)(count * sizeof *mono);
    if (cvt.needed) {
        size_t bytes = (size_t)cvt.len * (size_t)cvt.len_mult;
        if (bytes > INT_MAX)
            goto done;
        cvt.buf = music_alloc(bytes, &budget);
        if (cvt.buf == NULL)
            goto done;
        memcpy(cvt.buf, mono, (size_t)cvt.len);
        if (SDL_ConvertAudio(&cvt) != 0 || cvt.len_cvt <= 0 ||
            (size_t)cvt.len_cvt > bytes || (size_t)cvt.len_cvt > PCM_LIMIT ||
            (size_t)cvt.len_cvt % sizeof *mono != 0)
            goto done;
        music_free(mono, &budget);
        mono = NULL;
        /* Keep only exact final PCM, not the converter's worst-case capacity. */
        mono = music_alloc((size_t)cvt.len_cvt, &budget);
        if (mono == NULL)
            goto done;
        memcpy(mono, cvt.buf, (size_t)cvt.len_cvt);
        count = (size_t)cvt.len_cvt / sizeof *mono;
    }
    result.samples = mono;
    result.count = count;
    mono = NULL;
    reason = "MP3 active";
done:
    if (initialized)
        drmp3_uninit(&decoder);
    if (file != NULL)
        SDL_RWclose(file);
    music_free(cvt.buf, &budget);
    music_free(mono, &budget);
    music_free(input, &budget);
    music_free(path, &budget);
    fprintf(stderr, "music: track%02u.mp3: %s%s; prepare %.1f ms, peak heap %zu bytes\n",
            song == UINT_MAX ? song : song + 1, reason,
            result.samples == NULL ? "; using original FM" : "",
            frequency ? 1000.0 * (double)(SDL_GetPerformanceCounter() - started) / (double)frequency : 0.0,
            budget.peak);
    return result;
}

void external_music_free(ExternalMusic *music)
{
    music_free(music->samples, NULL);
    memset(music, 0, sizeof *music);
}

void external_music_render(ExternalMusic *music, Sint16 *output, size_t count,
                           unsigned int volume_q8, bool playing)
{
    size_t i;
    if (!playing || music->samples == NULL || music->count == 0) {
        memset(output, 0, count * sizeof *output);
        return;
    }
    for (i = 0; i < count; ++i) {
        output[i] = (Sint16)((Sint32)music->samples[music->cursor] * (Sint32)volume_q8 / 256);
        if (++music->cursor == music->count)
            music->cursor = 0;
    }
}
