# dr_mp3 provenance

- Official project: <https://github.com/mackron/dr_libs>
- Pinned revision: `51e61d308dde6b437fce0c5fabb32cd86b40f4d7` (2026-08-31).
- Header: <https://raw.githubusercontent.com/mackron/dr_libs/51e61d308dde6b437fce0c5fabb32cd86b40f4d7/dr_mp3.h>
- Upstream license: <https://raw.githubusercontent.com/mackron/dr_libs/51e61d308dde6b437fce0c5fabb32cd86b40f4d7/LICENSE>
- Acquired from the official repository through the GitHub connector on 2026-10-14. No floating branch is used for the vendored files.
- Header size: 209166 bytes; SHA-256: `997b7ee18de6e6b81e2a83f1ea9fc62aef25c62b28d48db95635f49e65de0a2f`.
- License size: 2598 bytes; SHA-256: `dd1c647e6f767f8ff4b2dfae0fed314726600a01e0cf1ef556afddd5fa96ff15`.
- Local Git blob hashes were independently matched to the official pinned files:
  header `a631ae40f066076e41f2f655ffd2891b41ca3772`; license `16dfbdfda2b761d1ec2ed57266dbdc777349ad25`.
- Both files are unmodified upstream text. The header identifies its development version as 0.7.4; this is a commit pin, not a claimed 0.7.4 release.

This project selects **MIT No Attribution (MIT-0)**, upstream's alternative 2. The full upstream license and embedded notices are retained, including minimp3's public-domain dedication. Existing OpenTyrian GPL-2.0-or-later and OPL LGPL-2.1-or-later licensing is unchanged.

## Security-related revision selection

Official `dr_mp3.h` history was checked on 2026-10-14. This was the newest header-affecting commit returned by that history. It includes the April validation changes (`ea24c1f`, `0b12cb5`), July overflow fix (`6d78776`) and the later August fix:

<https://github.com/mackron/dr_libs/commit/51e61d308dde6b437fce0c5fabb32cd86b40f4d7>

The August change bounds Xing/Info/LAME reads without unsigned subtraction underflow and adds the missing check before probing a LAME header. The July-only revision and older 0.7.3 release are therefore not used. The application additionally bounds file size, frame format/duration, all owned heap allocations and conversion sizes; finite sanitizer tests are not a guarantee that all malformed inputs are safe.

`DR_MP3_IMPLEMENTATION` and `DR_MP3_NO_STDIO` are defined only in `src/external_music.c`. No decoder DLL or new link dependency is required.
