/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef REAR_MULTI_P1_PINS_H
#define REAR_MULTI_P1_PINS_H
/* The initial pilot admits only the original normal-data bank layout. */
#ifndef REAR_P1_BANK_SIZE
#define REAR_P1_BANK_SIZE 32060u
#endif
/* Only semantic hashes, never original decoded art or weapon-record payloads.
 * Member order: 39, 1, 281, 282, 301, 300. */
#ifndef REAR_P1_SOURCE_PINS
#define REAR_P1_SOURCE_PINS {UINT64_C(0x33b06acfb919521e),UINT64_C(0x4a78399a66cb47d8),UINT64_C(0x486b3840e194bc22),UINT64_C(0x6d7fd5a152bbfbb8),UINT64_C(0x0a43ef168ae17e74),UINT64_C(0x79506a9365e83bc6)}
#endif
/* Full 80-byte records in order: 254, 265, 255, 266, 267 (P3 mode2 only). */
#ifndef REAR_P1_RECORD_PINS
#define REAR_P1_RECORD_PINS {UINT64_C(0x2de0fd3d91a6b30f),UINT64_C(0xa46442c430279c89),UINT64_C(0xf92503c1cf7f8a67),UINT64_C(0x16186b7836a64d47),UINT64_C(0x9a813af3656072f5)}
#endif
/* Full straight-RGBA payload pins from the six reviewed SVG masters.
 * Each pair is exact d4,d8. No fallback or runtime resampling. */
#ifndef REAR_P1_RGBA_PINS
#define REAR_P1_RGBA_PINS {{UINT64_C(0xd69e2fd8ed1cdb9a),UINT64_C(0xbc5d0f4e9ce3a2f5)},{UINT64_C(0xcdbad24a07cc4bcc),UINT64_C(0x9865a7591564a632)},{UINT64_C(0xbde3dec5a72e74ea),UINT64_C(0xfbe5d66e31b926c3)},{UINT64_C(0x9e771e4007d4d19a),UINT64_C(0x849cbdc14cf48e3f)},{UINT64_C(0x70952d574e97bd4e),UINT64_C(0xc4bee58c37788fcb)},{UINT64_C(0x07ea794dc7b7047e),UINT64_C(0x152002ea2a7ec6e7)}}
#endif
#endif
