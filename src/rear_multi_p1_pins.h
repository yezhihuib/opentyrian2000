/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef REAR_MULTI_P1_PINS_H
#define REAR_MULTI_P1_PINS_H
/* The initial pilot admits only the original normal-data bank layout. */
#ifndef REAR_P1_BANK_SIZE
#define REAR_P1_BANK_SIZE 32060u
#endif
/* Only semantic hashes, never original decoded art or weapon-record payloads.
 * Observed order: 39, 1, 281, 282, 301, 300, 40, 2, 77, 182, 183, 163, 164, 277, 278, 41, 3, 296, 297, 294, 295, 298, 299, 203, 222.
 * 163/164 are validated pass-through only, never drawable rear members. */
#ifndef REAR_P1_SOURCE_PINS
#define REAR_P1_SOURCE_PINS {UINT64_C(0x33b06acfb919521e),UINT64_C(0x4a78399a66cb47d8),UINT64_C(0x486b3840e194bc22),UINT64_C(0x6d7fd5a152bbfbb8),UINT64_C(0x0a43ef168ae17e74),UINT64_C(0x79506a9365e83bc6),UINT64_C(0xc358ef0c1ae44355),UINT64_C(0xf0583eb1740dee8d),UINT64_C(0xebed26fe15a8012c),UINT64_C(0xfa7d3c380902fe1a),UINT64_C(0x0c869bb96a77ec7c),UINT64_C(0xa34174ba65a5e3b2),UINT64_C(0xd118e1292d0f1044),UINT64_C(0x8a17a7ff4818a9ed),UINT64_C(0x277737dd4fec9099),UINT64_C(0x1d88ff33b672801e),UINT64_C(0x5440d094c96199c8),UINT64_C(0x2821ccb10cacc7d9),UINT64_C(0x38cfeb724714aafd),UINT64_C(0xa6ebd49c4510740c),UINT64_C(0x48641f1f8205125e),UINT64_C(0x18d08a9488a5acf5),UINT64_C(0x78e9b7bf74645c6d),UINT64_C(0xc0e5401237db0a59),UINT64_C(0xfbe343f0a38153e9)}
#endif
/* Full 80-byte records in order: 254, 265, 255, 266, 267, 256, 257, 268, 269, 258, 259, 270, 260, 271, 261, 272, 262, 273, 263, 274, 275. */
#ifndef REAR_P1_RECORD_PINS
#define REAR_P1_RECORD_PINS {UINT64_C(0x2de0fd3d91a6b30f),UINT64_C(0xa46442c430279c89),UINT64_C(0xf92503c1cf7f8a67),UINT64_C(0x16186b7836a64d47),UINT64_C(0x9a813af3656072f5),UINT64_C(0x336df95c79ab07a6),UINT64_C(0xb2155699efbdb6e3),UINT64_C(0xb0d0e52cca9ff499),UINT64_C(0x5a43f51bab88be8b),UINT64_C(0x0a9404f2915a23c9),UINT64_C(0xf3c7e8dc12351dc8),UINT64_C(0xc779039b7362d0f6),UINT64_C(0xcd5735a99bbecb93),UINT64_C(0xfb03d1fdaa0f2c6e),UINT64_C(0x1987ab75603a42b9),UINT64_C(0x1bc76a0fe7b06f72),UINT64_C(0x5c8e78c68b542a04),UINT64_C(0xdf6661ef4d03f02b),UINT64_C(0xb1df50f478068705),UINT64_C(0x8680b14f3eaffcf6),UINT64_C(0x719bf3ad022a1918)}
#endif
/* Full straight-RGBA payload pins from six reviewed SVG masters, six reviewed assemblies, five reviewed rigid transforms two reviewed P7 twin diagonals and two exact P9 rotations, plus two reviewed P10 four-lobe heads.
 * Drawable order: 39, 1, 281, 282, 301, 300, 40, 2, 77, 182, 183, 277, 278, 41, 3, 296, 297, 294, 295, 298, 299, 203, 222.
 * This differs from observed/source order. Each pair is exact d4,d8.
 * Zero denotes intentionally unsupported d4 for 182/183. P10 horizontal
 * roles203/222 use exact parent-reviewed d4/d8 payloads; no density fallback. */
#ifndef REAR_P1_RGBA_PINS
#define REAR_P1_RGBA_PINS {{UINT64_C(0xd69e2fd8ed1cdb9a),UINT64_C(0xbc5d0f4e9ce3a2f5)},{UINT64_C(0xcdbad24a07cc4bcc),UINT64_C(0x9865a7591564a632)},{UINT64_C(0xbde3dec5a72e74ea),UINT64_C(0xfbe5d66e31b926c3)},{UINT64_C(0x9e771e4007d4d19a),UINT64_C(0x849cbdc14cf48e3f)},{UINT64_C(0x70952d574e97bd4e),UINT64_C(0xc4bee58c37788fcb)},{UINT64_C(0x07ea794dc7b7047e),UINT64_C(0x152002ea2a7ec6e7)},{UINT64_C(0xe282898d9cb39ce5),UINT64_C(0x27e07fd8d6be79d5)},{UINT64_C(0xec9c021ef9b7011d),UINT64_C(0x313c0fe52e7fa8e1)},{UINT64_C(0x218c1be6c8a3476c),UINT64_C(0x5f99f26278e7afb6)},{UINT64_C(0x0000000000000000),UINT64_C(0x888f7807cb7fb1b7)},{UINT64_C(0x0000000000000000),UINT64_C(0x79d684e2a12caa1f)},{UINT64_C(0xf03f8f745a244970),UINT64_C(0x3df2a878cda365e6)},{UINT64_C(0x3fae8a76be180e70),UINT64_C(0xb953b3abd4a3fcde)},{UINT64_C(0x5dfd9280619f61ea),UINT64_C(0x8b30be3de1092cad)},{UINT64_C(0xb46a6834350f7c50),UINT64_C(0x78180b46cf51908e)},{UINT64_C(0x470d7a694cb1ea34),UINT64_C(0x5f7e6c19434fbaca)},{UINT64_C(0xf6b1a647ab2530f4),UINT64_C(0x8e3a148548c298c2)},{UINT64_C(0xfe4f61938de0c031),UINT64_C(0x60735166b4a9ea50)},{UINT64_C(0x73bdb95e757a0f29),UINT64_C(0x826ac5b753ea8b84)},{UINT64_C(0x061487c852b091c4),UINT64_C(0xfe0fee22f015d496)},{UINT64_C(0xf997db7d88b22d04),UINT64_C(0xc832a79db1a7d312)},{UINT64_C(0xac10f74cff7c73e8),UINT64_C(0x625ed5d5dc2be74c)},{UINT64_C(0x10bb72f75e86c13c),UINT64_C(0xb1a39b640c2f3340)}}
#endif
#endif
