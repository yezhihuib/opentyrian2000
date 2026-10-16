/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef REAR_MULTI_P1_PINS_H
#define REAR_MULTI_P1_PINS_H
/* The initial pilot admits only the original normal-data bank layout. */
#ifndef REAR_P1_BANK_SIZE
#define REAR_P1_BANK_SIZE 32060u
#endif
/* Only semantic hashes, never original decoded art or weapon-record payloads.
 * Observed order: 39, 1, 281, 282, 301, 300, 40, 2, 77, 182, 183, 163, 164.
 * The last two are validated pass-through only, never drawable rear members. */
#ifndef REAR_P1_SOURCE_PINS
#define REAR_P1_SOURCE_PINS {UINT64_C(0x33b06acfb919521e),UINT64_C(0x4a78399a66cb47d8),UINT64_C(0x486b3840e194bc22),UINT64_C(0x6d7fd5a152bbfbb8),UINT64_C(0x0a43ef168ae17e74),UINT64_C(0x79506a9365e83bc6),UINT64_C(0xc358ef0c1ae44355),UINT64_C(0xf0583eb1740dee8d),UINT64_C(0xebed26fe15a8012c),UINT64_C(0xfa7d3c380902fe1a),UINT64_C(0x0c869bb96a77ec7c),UINT64_C(0xa34174ba65a5e3b2),UINT64_C(0xd118e1292d0f1044)}
#endif
/* Full 80-byte records in order: 254, 265, 255, 266, 267, 256, 257, 268. */
#ifndef REAR_P1_RECORD_PINS
#define REAR_P1_RECORD_PINS {UINT64_C(0x2de0fd3d91a6b30f),UINT64_C(0xa46442c430279c89),UINT64_C(0xf92503c1cf7f8a67),UINT64_C(0x16186b7836a64d47),UINT64_C(0x9a813af3656072f5),UINT64_C(0x336df95c79ab07a6),UINT64_C(0xb2155699efbdb6e3),UINT64_C(0xb0d0e52cca9ff499)}
#endif
/* Full straight-RGBA payload pins from six reviewed SVG masters, two reviewed assemblies and three reviewed rigid transforms.
 * Drawable order is the first eleven observed IDs. Each pair is exact d4,d8.
 * Zero denotes intentionally unsupported d4 for 182/183. No resampling/fallback. */
#ifndef REAR_P1_RGBA_PINS
#define REAR_P1_RGBA_PINS {{UINT64_C(0xd69e2fd8ed1cdb9a),UINT64_C(0xbc5d0f4e9ce3a2f5)},{UINT64_C(0xcdbad24a07cc4bcc),UINT64_C(0x9865a7591564a632)},{UINT64_C(0xbde3dec5a72e74ea),UINT64_C(0xfbe5d66e31b926c3)},{UINT64_C(0x9e771e4007d4d19a),UINT64_C(0x849cbdc14cf48e3f)},{UINT64_C(0x70952d574e97bd4e),UINT64_C(0xc4bee58c37788fcb)},{UINT64_C(0x07ea794dc7b7047e),UINT64_C(0x152002ea2a7ec6e7)},{UINT64_C(0xe282898d9cb39ce5),UINT64_C(0x27e07fd8d6be79d5)},{UINT64_C(0xec9c021ef9b7011d),UINT64_C(0x313c0fe52e7fa8e1)},{UINT64_C(0x218c1be6c8a3476c),UINT64_C(0x5f99f26278e7afb6)},{UINT64_C(0x0000000000000000),UINT64_C(0x888f7807cb7fb1b7)},{UINT64_C(0x0000000000000000),UINT64_C(0x79d684e2a12caa1f)}}
#endif
#endif
