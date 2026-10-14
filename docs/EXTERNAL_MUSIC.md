# External MP3 music

## Quick start

Original Tyrian 2000 data is still required separately, including `music.mus`.
That file supplies the original control timeline and each song's FM fallback.
Keep the data and your MP3s outside this repository and public packages.

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --music-dir=/absolute/path/to/my-music
```

Place replacements in that directory using the exact lowercase filenames below.
You can replace just one song; all other songs keep their original FM audio.
There is no filename/title matching, globbing, environment lookup, or automatic
search beside the executable, in `--data`, or in the working directory.

`--music-dir=DIR` is explicit opt-in. An empty value is rejected. A nonempty
unavailable directory, or a missing/rejected file in it, uses that song's original
FM audio. A relative directory is relative to the process's launch working
directory. Without this option there is no external lookup or decoder allocation,
and the original FM/SFX path, including its historical first-song behavior,
remains unchanged.

For the Windows manual launcher:

```powershell
& .\prototype\start-manual-hd.ps1 -DataDirectory 'C:\Games\Tyrian 2000' `
  -MusicDirectory 'C:\Music\我的配乐'
```

The launcher requires a nonempty existing absolute `-MusicDirectory`, resolves it
before changing to the profile directory, and quotes it with the existing Windows
argument helper. Spaces and Chinese characters are supported by the path plumbing;
real Windows path/device acceptance remains a separate check. Omitting the
parameter passes no music override. The music option does not require HD graphics;
it may also be passed directly to the game without the manual-HD launcher.

## Track names

This list is generated from `musicTitle` in [`src/musmast.c`](../src/musmast.c), in
source order. File numbers are **one-based**: `song_num + 1`, matching the jukebox's
displayed numbering. The table's source index is zero-based.

For example, level-song value 18 calls `play_song(17)` and therefore selects
`track18.mp3` (**Tyrian, The Level**). `play_song(18)` instead selects `track19.mp3`
(**The MusicMan**). With the override enabled, an explicit loaded-state check also
handles a first request for source index 0; the no-option path is left unchanged.

| Filename | Source index | Original title |
| --- | ---: | --- |
| `track01.mp3` | 0 | Asteroid Dance Part 2 |
| `track02.mp3` | 1 | Asteroid Dance Part 1 |
| `track03.mp3` | 2 | Buy/Sell Music |
| `track04.mp3` | 3 | CAMANIS |
| `track05.mp3` | 4 | CAMANISE |
| `track06.mp3` | 5 | Deli Shop Quartet |
| `track07.mp3` | 6 | Deli Shop Quartet No. 2 |
| `track08.mp3` | 7 | Ending Number 1 |
| `track09.mp3` | 8 | Ending Number 2 |
| `track10.mp3` | 9 | End of Level |
| `track11.mp3` | 10 | Game Over Solo |
| `track12.mp3` | 11 | Gryphons of the West |
| `track13.mp3` | 12 | Somebody pick up the Gryphone |
| `track14.mp3` | 13 | Gyges, Will You Please Help Me? |
| `track15.mp3` | 14 | I speak Gygese |
| `track16.mp3` | 15 | Halloween Ramble |
| `track17.mp3` | 16 | Tunneling Trolls |
| `track18.mp3` | 17 | Tyrian, The Level |
| `track19.mp3` | 18 | The MusicMan |
| `track20.mp3` | 19 | The Navigator |
| `track21.mp3` | 20 | Come Back to Me, Savara |
| `track22.mp3` | 21 | Come Back again to Savara |
| `track23.mp3` | 22 | Space Journey 1 |
| `track24.mp3` | 23 | Space Journey 2 |
| `track25.mp3` | 24 | The final edge |
| `track26.mp3` | 25 | START5 |
| `track27.mp3` | 26 | Parlance |
| `track28.mp3` | 27 | Torm - The Gathering |
| `track29.mp3` | 28 | TRANSON |
| `track30.mp3` | 29 | Tyrian: The Song |
| `track31.mp3` | 30 | ZANAC3 |
| `track32.mp3` | 31 | ZANACS |
| `track33.mp3` | 32 | Return me to Savara |
| `track34.mp3` | 33 | High Score Table |
| `track35.mp3` | 34 | One Mustn't Fall |
| `track36.mp3` | 35 | Sarah's Song |
| `track37.mp3` | 36 | A Field for Mag |
| `track38.mp3` | 37 | Rock Garden |
| `track39.mp3` | 38 | Quest for Peace |
| `track40.mp3` | 39 | Composition in Q |
| `track41.mp3` | 40 | BEER |

## Playback and controls

- The selected MP3 is fully decoded before activation into signed 16-bit PCM.
  Stereo is downmixed with widened arithmetic; output stays **mono**, through the
  existing SDL audio device and callback. Conversion targets the actual device
  sample rate, which may differ from the requested 44.1 kHz. There is no second
  player/device and no SDL_mixer dependency.
- Only one replacement PCM buffer is active. Same-song calls reuse and resume it;
  they do not reopen a missing file every tick. Restart rewinds both PCM and the
  original LDS sequencer. Stop and music mute freeze both cursors while existing
  SFX behavior is preserved. Existing menus may call restart or resume on unmute;
  those choices remain in place. To pick up an edited file, change to another song
  and back, or relaunch.
- The original LDS sequencer and OPL rendering continue inaudibly while PCM
  plays. OPL output is overwritten by PCM, preserving the original renderer's
  shared C RNG advancement without another audio buffer. LDS owns `playing`,
  `songlooped`, original song-end/loop decisions, volume commands and public fades.
  MP3 EOF wraps its own cursor, without an inserted silent callback block; it does
  not set the game loop flag or extend a one-shot. A short replacement can wrap
  before the original loop point. A long replacement can be cut at an original
  one-shot's endpoint, with silence from the following output segment.
- PCM gain follows the original master envelope at LDS segment boundaries, then
  the existing user music volume. LDS master value 0 is the **full-volume sentinel
  256/256**, not silence; values 1–255 use their corresponding fraction of 256.
  Original `mainvolume` limits and fades keep controlling that trajectory. This
  reproduces the control trajectory, not the exact loudness of OPL instrument
  attenuation. A replacement already containing fades/dynamics may be attenuated
  again.
- PCM has unity source gain before the envelope and user volume. The historical
  additional 2× gain applies only to original OPL/FM audio. The existing eight SFX
  channels and saturating final mixer remain in use, so music and sound effects
  retain their separate controls.
- File I/O, decoding, resampling, allocations, frees and diagnostics occur outside
  the audio callback. Full-song preparation can briefly stall the game thread at
  a song change while SFX continue and music is stopped. This design does not
  promise seamless game-thread pacing; timing needs separate measurement.

## Resource limits and fallback

Limits apply per replacement. MiB means 1,048,576 bytes.

| Resource | Maximum |
| --- | ---: |
| Encoded input file | 32 MiB (33,554,432 bytes) |
| Decoded duration | 10 minutes (600 seconds) |
| Final mono S16 PCM | 64 MiB (67,108,864 bytes) |
| Explicitly tracked temporary allocations | 256 MiB (268,435,456 bytes) |

The duration bound counts complete MPEG frame samples, including a metadata frame
and any encoded delay/padding. A file advertised as exactly ten minutes can
therefore exceed the bound. Use a shorter file if it falls back for this reason.
The final-PCM bound also applies after resampling to the actual device rate.

These are loader limits, not a promise that the whole game's process memory stays
below 256 MiB. Resource limits are checked while reading/decoding/converting, not
accepted solely from untrusted duration tags. Temporary decoder/input/conversion
storage is released before activation. Unsupported channel/format changes,
failed initialization, zero decoded audio, detectable malformed tags/counts,
known truncation/short reads, limit violations, conversion errors and allocation
failures reject the replacement and retain that song's original FM path. A missing
file is also a normal per-song fallback; it does not disable valid files for other
songs. The loader does not modify or repair input files.

A conservative framing scan accepts complete MPEG Layer III frames with stable
sample rate, channel count and MPEG version; CBR and VBR bitrates are allowed.
It recognizes a leading ID3v2.2/v2.3/v2.4 tag, a final ID3v1 tag and trailing zero
padding in its supported positions. Reserved ID3 header flags and a v2.4 footer
that disagrees with its header are rejected; tag frame contents are not validated.
Free-format MP3s, arbitrary leading/trailing
junk, unsupported tag layouts (such as an APE tail), incomplete frames and
midstream format changes are rejected even if another music player can recover
them. Xing/Info frame/byte counts and recognized tag bounds are checked, but this
is not a CRC or compressed-payload integrity check.

MP3 decoding is tolerant: some damaged or partially decodable files can still
produce PCM. This feature does **not** certify file integrity or promise to detect
every changed byte, every truncated tail, or every audible defect. Use known-good
files; original data is necessary even when every track has an MP3 replacement.
On each preparation attempt, a `music: trackNN.mp3:` diagnostic reports whether
MP3 is active or original FM is used, plus preparation time and tracked peak heap.
Use those diagnostics to distinguish a rejected file from a volume setting; they
are emitted outside the audio callback.

## Loop quality

PCM wrapping needs no decoder restart or file I/O. It still cannot promise
universally gapless MP3 loops. Recognized encoder delay/padding metadata may help,
but absent or incorrect tags, encoded silence, mismatched waveform endpoints and
resampling edges can produce a pause or click. This version adds no automatic
silence trimming, crossfade or loop-point metadata. Choose or prepare a replacement
with suitable endpoints, and listen on the target device.

## Build, licensing and verification boundaries

The decoder is vendored in `src/third_party/dr_mp3.h`, compiled once by
`src/external_music.c`, using memory input via SDL's file/path support. Its pinned
revision, hash and upstream notices are recorded in
[`dr_mp3-PROVENANCE.md`](../src/third_party/dr_mp3-PROVENANCE.md) and
[`dr_mp3-LICENSE`](../src/third_party/dr_mp3-LICENSE). dr_mp3 uses the selected MIT-0
license; the game's GPL-2.0-or-later and OPL LGPL-2.1-or-later licensing remain
unchanged. No extra runtime decoder DLL or package/link flags are needed.

The Makefile includes the new C file through its existing wildcard. The Visual
Studio project explicitly lists the source and both new headers. Run
`python3 prototype/test-windows-project.py` for project XML/path/source inventory;
that test is not Windows compilation or runtime verification. See the
[Windows handoff](WINDOWS_HANDOFF.md) for the distinct build, path and listening
checks still required on Windows.

Synthetic test tones belong in external temporary test directories, with their
generation/provenance recorded. Do not commit private songs or original music.
Unit, malformed-input/sanitizer, no-option sample comparison and source inventory
checks are distinct from ordinary gameplay, physical output-device listening,
whole-game certification and real Windows acceptance. No Windows bundle or new
Windows runtime/listening pass is implied by these instructions.

On Linux with a C compiler, SDL2 development files and ffmpeg/libmp3lame available:

```sh
python3 prototype/test-external-music.py
python3 prototype/test-external-music-mixer.py --sanitize
python3 prototype/test-external-music-integration.py --data=/private/tyrian2000 --sanitize
python3 prototype/test-windows-project.py
```

The integration suite reads the separately supplied original `music.mus`, compares
all 41 songs using the real LDS and OPL engines, verifies per-song MP3/FM fallback
and runs 100 actual SDL dummy-device lifecycle cycles. It reports hashes/results
without exporting original music samples. It is separate from a game run and
physical-device listening. The baseline suites default to immutable pre-MP3 tree
`4383e1b75248e7ed0910e89f8c0db05dec8d4281` (published commit `f5d844b`), so committing
this feature does not silently change the reference. Use `--baseline-ref` only
when deliberately testing against another equivalent pre-feature revision.
