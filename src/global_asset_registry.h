/* SPDX-License-Identifier: GPL-2.0-or-later
 * Generated from reviewed global-assets-v1/registry.json.
 * Regenerate with scripts/build_global_registry_header.py; do not edit pins.
 * Registry SHA256: f06217ef4e0ba443227b584d98e18df245d4014964a97573956b2c993f0a3ba3 */
#ifndef GLOBAL_ASSET_REGISTRY_H
#define GLOBAL_ASSET_REGISTRY_H
#include <stdint.h>
typedef struct { unsigned identity,bytes,density,width,height; int anchor_x,anchor_y; const char *path; uint64_t payload_fnv; } GlobalAssetResource;
typedef struct { unsigned index; uint64_t fnv; } GlobalAssetSourceTile;
typedef struct { unsigned index; uint32_t rgb; } GlobalAssetPaletteColor;
static const GlobalAssetResource global_asset_resources[] = {
 {90229u,172060u,8u,24u,28u,5,7,"content/5cfa025cce0d662d0d92f1f1371cd0153910175a5956e4ed02ae7dc6fc3bafc7.hda",UINT64_C(0x848cb484fb735309)},
 {1090001u,172060u,8u,24u,28u,5,7,"content/0e42426b54f2b56d29d446153361864aa9c18058f1ba6d61c0827d49aadb5869.hda",UINT64_C(0x85c60fdc8b6d4c66)},
 {90231u,172060u,8u,24u,28u,5,7,"content/ec6c662bc5a8f596a0e8b1023530636b3cdf1a9b608382c7d8ee37337d9cfefb.hda",UINT64_C(0x9294e8d8a9b88fea)},
 {1090003u,172060u,8u,24u,28u,5,7,"content/207239469f9c8a76fd2d63f30dfc537263742ecc7683a44d067519272430b691.hda",UINT64_C(0x2b1df2f4f48a32a3)},
 {1090004u,172060u,8u,24u,28u,5,7,"content/05e222ca3581e6718752ea0577c212f08729749cdcfc936d59b2218f393d660a.hda",UINT64_C(0xd140e691af6ed1e3)},
 {1090005u,172060u,8u,24u,28u,5,7,"content/173d815b5a3f641e7147de537cb5246ba1fad8a013b3d91d585fd67828a7b803.hda",UINT64_C(0xd85b10dbc41272a3)},
 {90233u,172060u,8u,24u,28u,5,7,"content/d1fe9bfe2dd84207fceb2f453c862eeaea802d9832fd14c1e1c3290622a53964.hda",UINT64_C(0xf2bdffb6d17e2d67)},
 {1090007u,172060u,8u,24u,28u,5,7,"content/2684439fb26d3ba4c0a1cadef9aba5c6baefc641dc8298493f4ea1b232bf9f2f.hda",UINT64_C(0x31170616344845c8)},
 {1090008u,172060u,8u,24u,28u,5,7,"content/b6a2fed82b69e624ea249868f584638345ffb0d21807c453d18e4d8af1d0be20.hda",UINT64_C(0x022a48b1690f1dc0)},
 {1090009u,172060u,8u,24u,28u,5,7,"content/b65b0524a05d1321131eea311f4e07f84841b895543def21f5f284b3ed6e7d8d.hda",UINT64_C(0x1c50760313d7ed2c)},
 {90235u,172060u,8u,24u,28u,5,7,"content/692b9a7cc8455798a1dda8a1dfe4aba10bb9872cacc790fd26ac5b246fa91350.hda",UINT64_C(0x8072730d59fdf877)},
 {1090011u,172060u,8u,24u,28u,5,7,"content/ce7e60e2a2f7df5290909a07655d432179c0ff3e204b4449d5e2ad637bdae1c1.hda",UINT64_C(0x043aee5d5850dc33)},
 {90237u,172060u,8u,24u,28u,5,7,"content/a375ba8f0cf276a2eb2e8be75165f96ea9b67edf37a6dca9f29fd8aef07bd7dc.hda",UINT64_C(0x667a4488e270e85d)},
 {1060229u,43036u,8u,12u,14u,0,0,"content/032b9a95b91fe76016e28cc4416ae965743088b238a6ef1b3119c368788b7fbb.hda",UINT64_C(0x4c8332f5396fc90f)},
 {1060230u,43036u,8u,12u,14u,0,0,"content/6affeaa882afe7ca48267f6303d5d809866f2c916729d1bfc533b9c32dbeaa49.hda",UINT64_C(0x2072fe2fe9998580)},
 {1060231u,43036u,8u,12u,14u,0,0,"content/50e521515f6929ffb5fa786a7ca19304eed782583087b1f768c24491d74c3f0d.hda",UINT64_C(0x33e7ccb4e1240985)},
 {1060232u,43036u,8u,12u,14u,0,0,"content/4cfd97f983844e5651d5b28778e414a1599f811a1475faa6ccde66cee8d696b7.hda",UINT64_C(0xdfc7f7473ec66f2b)},
 {1060233u,43036u,8u,12u,14u,0,0,"content/d4fdb95e09cec1c5a70a3a1c69ed322616c52bb16a3a3ecf50ddcdb6711cc034.hda",UINT64_C(0xa49f9ccff5f5eba4)},
 {1060234u,43036u,8u,12u,14u,0,0,"content/07f4b19c3630ecd061f0c5701e30ac2e9222a5180d889cd0339edbcd2bdaaef4.hda",UINT64_C(0xe3b67c600863d521)},
 {1060235u,43036u,8u,12u,14u,0,0,"content/f11918f94d45b0b4ceb193858e6cdc7a12fda2161d89da42ce68f98fd95070ee.hda",UINT64_C(0x2464105ae16bb36c)},
 {1060236u,43036u,8u,12u,14u,0,0,"content/88a24e24a1d715d0dea69085528d09baaa5a670494a854d4db58bf68d4b402b0.hda",UINT64_C(0x24c43d76779ed185)},
 {1060237u,43036u,8u,12u,14u,0,0,"content/b71609dd0caf8c545e1683328e47e9a1a26222e5f65d3774faafaa41ad36330f.hda",UINT64_C(0x9155c09987cc795e)},
 {1060248u,43036u,8u,12u,14u,0,0,"content/f31dc159a1fc519dc897afe2959bf1eab709ea9ac148c0f72ee78591e8629e7e.hda",UINT64_C(0xdfe305d22e00e808)},
 {1060249u,43036u,8u,12u,14u,0,0,"content/e4ea83cf45e3ab8c97f563e73337c16f28ec19f39de724b51d712bb6442d9b4b.hda",UINT64_C(0xe0345bbafb6daa68)},
 {1060250u,43036u,8u,12u,14u,0,0,"content/c21b09f637019168b208412849aff98a5e94b79b7910ec06bc835efbb5036303.hda",UINT64_C(0xcf0d39294e52b996)},
 {1060252u,43036u,8u,12u,14u,0,0,"content/ae97ccc3056b059c5e8e78da37c1c3cf1dede697fcaeef37d8c7f082b1f49902.hda",UINT64_C(0x9809bd2730735f56)},
 {1060253u,43036u,8u,12u,14u,0,0,"content/04e2163c6ae9fcca00b0ce6ef155d5680f2e36c710d898b8f5a1cf3611948e0e.hda",UINT64_C(0x98722410c61cf86e)},
 {1060254u,43036u,8u,12u,14u,0,0,"content/efa6886201d97f13f2f27a2dc8ea13f9d6bb7229488d52befdb60571142993da.hda",UINT64_C(0xceaec6dc08f4ff7d)},
 {1060255u,43036u,8u,12u,14u,0,0,"content/dd505a16d35d08ad736219fe75622f5ec0f0370298dce20f8c69f862be6ac270.hda",UINT64_C(0x9879fc41ab20d494)},
 {1060256u,43036u,8u,12u,14u,0,0,"content/e373dd69863cf6f741ac095ace46183a3af045dad42dc6fc292b00c9774bf612.hda",UINT64_C(0xf98a2a64840e796d)},
 {1060267u,43036u,8u,12u,14u,0,0,"content/1aaf6de91392988e89266e8f8c760ea00f74a2abdaf4ae5e59c592e5a64feebc.hda",UINT64_C(0x529e0c7741c9798d)},
 {1060268u,43036u,8u,12u,14u,0,0,"content/86956e4f8ba83188e38897eedb7fc7fef6823b331a1036d586cd0b7551c896a9.hda",UINT64_C(0x55196ad5642b4325)},
 {1060269u,43036u,8u,12u,14u,0,0,"content/ed46bd33c56712bfc3fbdeeb48a900fd5e21d8ea78f361392f18fdee0d761785.hda",UINT64_C(0xdcb93fdf92a6f4e7)},
 {1060272u,43036u,8u,12u,14u,0,0,"content/557cbe6ec20edcb1615942492c6feecc2d1cdf4d82565f2a63d773185739dc92.hda",UINT64_C(0xcaa03a63544d990c)},
 {1060275u,43036u,8u,12u,14u,0,0,"content/d06d24e14dc51657c392bf6b2fae142cf7209dea740495a30786231eefdb58ea.hda",UINT64_C(0xc60c9b4fb86dd6e8)},
 {80058u,43036u,8u,12u,14u,0,0,"content/571feee3e3a572c6178fad80ca8fe3ca12e2cde21438464fa916b68cab1b43b0.hda",UINT64_C(0x4acb84bfa5b4664c)},
 {80059u,43036u,8u,12u,14u,-1,0,"content/9b12eb865bcad5d13565106c1ecdaa464fea9469e424c5b4b970c84d7c0576ae.hda",UINT64_C(0xbb5ffa41cd02570b)},
 {80060u,43036u,8u,12u,14u,0,0,"content/e570776739129ff48f15aa5d4f5f809974e3420bf8bc55241429d419ce08f0d8.hda",UINT64_C(0x50ea36578382d3dd)},
 {80062u,43036u,8u,12u,14u,0,0,"content/0da3659e64942dfef38833193b19f5186586ca0f43b99f8fa5e31b7792a18ecf.hda",UINT64_C(0x3b7514e77675738f)},
 {80165u,43036u,8u,12u,14u,0,0,"content/255fa3dc879f33cb014f4393b56305bc118ef651c51f3ad6892f67922d959047.hda",UINT64_C(0x8a76e6547f1cfb41)},
 {1060146u,43036u,8u,12u,14u,0,0,"content/4ffc2b7596daf9da246c8c502e7d48a9c5a72271a3f4bd00aded691916eff5e3.hda",UINT64_C(0x816f0c7c46ce3e57)},
 {1060147u,43036u,8u,12u,14u,0,0,"content/babd7fd35c3e5d36b91f3e12fb4321f10710534365966650c0300b6d0fb7baa7.hda",UINT64_C(0x4a7f15f328f95dba)},
 {1060148u,43036u,8u,12u,14u,0,0,"content/5c264f1bcb8cd5ba90572f1f58fab27918d0d1422b08bf79c10475bb588f358e.hda",UINT64_C(0xe017ff97747afefb)},
 {1060149u,43036u,8u,12u,14u,0,0,"content/4320a1a0771cbbd6f9a58239fcb78adfc193501f6b3bcf4b148f82c15b964ee0.hda",UINT64_C(0x1ce381fbe3a34f5c)},
 {1060150u,43036u,8u,12u,14u,0,0,"content/7b68a29d3f1f765cfa830ca83dd2c348a4f13182f9c637f4baa9b1ac4ef3877c.hda",UINT64_C(0xf8a7a017f2b25431)},
 {1060151u,43036u,8u,12u,14u,0,0,"content/5f09994d08e87f4e7ce0ad95f247e477a7a92b957c9dc5f8f6c6188e75f0335c.hda",UINT64_C(0x35759aefcf8350f3)},
 {1060152u,43036u,8u,12u,14u,0,0,"content/6d6a2f0addecec74acd0d8e9b1cb3246b5b40e759c3b3f0e24c1dea43d4b2ad7.hda",UINT64_C(0x9cf81341ec3a6f03)},
 {80067u,43036u,8u,12u,14u,0,0,"content/96b975abbccf393464cf2444f72d63c8ad3f996d8cc5c153593ad16f476e30e0.hda",UINT64_C(0xaea83e10c9169380)},
 {80070u,43036u,8u,12u,14u,0,0,"content/eebd525dab58f0fc6708f4f3c7b15a88e67270be877ff250e93c4bb2a2aeb8de.hda",UINT64_C(0x6c26e938d94472c2)},
 {1060135u,43036u,8u,12u,14u,0,0,"content/5d2fc0b502900c0d9a18899acaf4cd9cc418d91f73ab6864ec35c9d4c38e78e2.hda",UINT64_C(0x05f600baacc46e91)},
 {1060136u,43036u,8u,12u,14u,0,0,"content/56edfc2111fd372c6466c69b7158e817c65f6f07bf73ef0a26ea83150a266ae9.hda",UINT64_C(0x16746d724eadc23a)},
 {1060137u,43036u,8u,12u,14u,0,0,"content/393d36c4f15a463f6799a967a71911fb0a7aa937bbcfc083497f42a138fd578a.hda",UINT64_C(0xde2537c5f8e6c348)},
 {1060138u,43036u,8u,12u,14u,0,0,"content/c7dfaef6bcdd206bf3f10b65b224a13e0f992bb69edf4f59d8001951985cf3e9.hda",UINT64_C(0xaeca5a9f45ca467c)},
 {1060139u,43036u,8u,12u,14u,0,0,"content/4486ad1625580b5947f00db6e580f9020775fc71a5815fb5fd2dbd226cfbed31.hda",UINT64_C(0xb4ddcd0117d2d2e4)},
 {1060140u,43036u,8u,12u,14u,0,0,"content/e68dcef338f42f0595ca85ae1340f4eff95b9352dc1b84b3e6eb91e252059f8c.hda",UINT64_C(0xf035d7c3b9bed804)},
 {1060141u,43036u,8u,12u,14u,0,0,"content/fb4f7ee942107321deba815538b903c23c43448320dbc44c6487fd744b7e0c08.hda",UINT64_C(0xd9a3a7c66cac92c0)},
 {1060122u,43036u,8u,12u,14u,0,0,"content/e5a1cff9818e876cd317cc78d34c206b859f6eb6beff695062eefa4ffb603336.hda",UINT64_C(0x8a0633c3cdfe6788)},
 {1060123u,43036u,8u,12u,14u,0,0,"content/53626aeff7d46c921c47a9acf4812948f4b09580cb1084efefa3a7677e9b68ea.hda",UINT64_C(0x5528c1fc6efbca8b)},
 {1060124u,43036u,8u,12u,14u,0,0,"content/c82beb74fa1313bde51335a0e29774cb2df03ec5b468018a63806545522055e8.hda",UINT64_C(0xe4fbd83972b3fdd6)},
 {1060125u,43036u,8u,12u,14u,0,0,"content/f0e953b8d9132b084aa5ead8389140aa933d95be1f9480e14488fa1aa78503d1.hda",UINT64_C(0x041f111cb4fdfdef)},
 {1060126u,43036u,8u,12u,14u,0,0,"content/2775f74601f7e3de25daafddf9a11115d0eefe1dbe56a332594c089051305392.hda",UINT64_C(0x8dbafafe6c4b6a38)},
 {1060127u,43036u,8u,12u,14u,0,0,"content/d37e797583e156913786bb4c617e059644a6e7ba4ab19b4c3b63e278c5a8fee7.hda",UINT64_C(0x0febdf5ed0ad0977)},
 {1060128u,43036u,8u,12u,14u,0,0,"content/6f4a71509dc1f0a91af3eb15449c7abb25d3506fadf731b45904322261eaf344.hda",UINT64_C(0xc0200936752d1146)},
 {1060129u,43036u,8u,12u,14u,0,0,"content/0378f90c069578635fe9f09f91100493156fda653757a191cfb1fade15d3d27c.hda",UINT64_C(0x84944853d8be654f)},
 {1060130u,43036u,8u,12u,14u,0,0,"content/32bd4b3cd65568c231f68de65e8b9e797f31ef2d2ad2c88aae8b8bf6dd07ad5d.hda",UINT64_C(0xc6c28cd9f987c964)},
 {1060131u,43036u,8u,12u,14u,0,0,"content/8206806e170690297a939c1075d2c18478f4bf3554332b0177d5c2c0d2ee0ddb.hda",UINT64_C(0x83101dd94db6795a)},
 {1060132u,43036u,8u,12u,14u,0,0,"content/749d65e85dc2772ae6ef7f3061ac02f287b6a780fa71f8745546446950beee79.hda",UINT64_C(0x503d5391202b0b7b)},
 {1060133u,43036u,8u,12u,14u,0,0,"content/6e1223b35eae0763a86bd58a31f11c757a93ad039475d5370d53c6ba699007bb.hda",UINT64_C(0xddba940b87be6844)},
};
enum { GLOBAL_ASSET_RESOURCE_COUNT = 68, GLOBAL_ASSET_FAMILY_COUNT = 7 };
enum { GLOBAL_TALON_BANK_BYTES = 33484 };
static const GlobalAssetSourceTile global_talon_source[] = {
 {229u,UINT64_C(0x3039ccf24a3813c9)},
 {230u,UINT64_C(0x635a7ba6a40cc3ce)},
 {231u,UINT64_C(0x4671f4e4752bd3ce)},
 {232u,UINT64_C(0xb8bda523f77d5ead)},
 {233u,UINT64_C(0x9926ced363914e55)},
 {234u,UINT64_C(0x05a23d411744639d)},
 {235u,UINT64_C(0xc93fa9f51a911b4e)},
 {236u,UINT64_C(0x369940597be73ebe)},
 {237u,UINT64_C(0x8e9d59a9d052653d)},
 {238u,UINT64_C(0x5ac8c78644eb7383)},
 {248u,UINT64_C(0xc043a803bd7945bc)},
 {249u,UINT64_C(0x0013f6e55ca29dad)},
 {250u,UINT64_C(0xea5cf097dd8cf380)},
 {251u,UINT64_C(0x7362348361652579)},
 {252u,UINT64_C(0xb91fe403723a8017)},
 {253u,UINT64_C(0x8fc0dca692bb9d1a)},
 {254u,UINT64_C(0x86b2a02d4b7dbe10)},
 {255u,UINT64_C(0xb7ab4cf95818a3da)},
 {256u,UINT64_C(0x50d17fa4d559a5dc)},
 {257u,UINT64_C(0x72aa5b104aa72411)},
};
static const GlobalAssetPaletteColor global_talon_palette[] = {
 {16u,UINT32_C(0x100800)},
 {17u,UINT32_C(0x1c1000)},
 {18u,UINT32_C(0x2c1804)},
 {19u,UINT32_C(0x382408)},
 {20u,UINT32_C(0x492c10)},
 {21u,UINT32_C(0x553c18)},
 {22u,UINT32_C(0x654920)},
 {23u,UINT32_C(0x71552c)},
 {24u,UINT32_C(0x7d6538)},
 {25u,UINT32_C(0x8e7145)},
 {26u,UINT32_C(0x9a8255)},
 {27u,UINT32_C(0xaa9265)},
 {28u,UINT32_C(0xb6a279)},
 {29u,UINT32_C(0xcfc39e)},
 {30u,UINT32_C(0xe7dfc7)},
 {31u,UINT32_C(0xfffff3)},
};
static const unsigned global_talon_resource_ids[] = {90229u,1090001u,90231u,1090003u,1090004u,1090005u,90233u,1090007u,1090008u,1090009u,90235u,1090011u,90237u};
enum { GLOBAL_SHIELD_BANK_BYTES = 17810 };
static const GlobalAssetSourceTile global_shield_source[] = {
 {229u,UINT64_C(0x8c135499d13963be)},
 {230u,UINT64_C(0x1bb9953e3b238540)},
 {231u,UINT64_C(0xb5537a992563eb0d)},
 {232u,UINT64_C(0x7305539d6b6b17d1)},
 {233u,UINT64_C(0xe72e4a3d5818c55a)},
 {234u,UINT64_C(0x4f656159fa007c86)},
 {235u,UINT64_C(0x0aef691b1ca24a95)},
 {236u,UINT64_C(0x7e42bb7eb832ac9d)},
 {237u,UINT64_C(0xe91cc9956d4c7023)},
 {248u,UINT64_C(0x2580739d6e2a343f)},
 {249u,UINT64_C(0x552fe5439ccd6fdc)},
 {250u,UINT64_C(0x07d477b0c0eedb40)},
 {251u,UINT64_C(0x51795983e22e1d65)},
 {252u,UINT64_C(0xa4cfe017190810ca)},
 {253u,UINT64_C(0x1b89e4401f5a0dae)},
 {254u,UINT64_C(0x8d7cfcf03c183cd0)},
 {255u,UINT64_C(0x16b217048c05fb49)},
 {256u,UINT64_C(0xaac64f1476d44802)},
 {267u,UINT64_C(0xd2f814b0b46162fb)},
 {268u,UINT64_C(0xd2f814b0b46162fb)},
 {269u,UINT64_C(0xd2f814b0b46162fb)},
 {270u,UINT64_C(0x51795983e22e1d65)},
 {271u,UINT64_C(0x51795983e22e1d65)},
 {272u,UINT64_C(0xc22e38bed2cee2a5)},
 {273u,UINT64_C(0x51795983e22e1d65)},
 {274u,UINT64_C(0x51795983e22e1d65)},
 {275u,UINT64_C(0xc3db252a0712543b)},
};
static const GlobalAssetPaletteColor global_shield_palette[] = {
 {128u,UINT32_C(0x24556d)},
 {129u,UINT32_C(0x2c5d75)},
 {130u,UINT32_C(0x38697d)},
 {131u,UINT32_C(0x41758a)},
 {132u,UINT32_C(0x4d8292)},
 {133u,UINT32_C(0x558e9e)},
 {134u,UINT32_C(0x619aa6)},
 {135u,UINT32_C(0x6da6b2)},
 {136u,UINT32_C(0x7db2ba)},
 {137u,UINT32_C(0x8abec7)},
 {138u,UINT32_C(0x9acbcf)},
 {139u,UINT32_C(0xa6d3d7)},
 {140u,UINT32_C(0xbadfe3)},
 {141u,UINT32_C(0xcbebeb)},
 {142u,UINT32_C(0xdbf7f7)},
 {143u,UINT32_C(0xefffff)},
};
static const unsigned global_shield_resource_ids[] = {1060229u,1060230u,1060231u,1060232u,1060233u,1060234u,1060235u,1060236u,1060237u,1060254u,1060255u,1060256u,1060248u,1060249u,1060250u,0u,1060252u,1060253u,1060267u,1060268u,1060269u,0u,0u,1060272u,0u,0u,1060275u};
static const unsigned global_shield_phase_indices[] = {229u,230u,231u,232u,233u,234u,235u,236u,237u,254u,255u,256u,248u,249u,250u,251u,252u,253u,267u,268u,269u,270u,271u,272u,273u,274u,275u};
static const unsigned global_shield_phase_ttl[] = {3u,2u,1u,3u,2u,1u,3u,2u,1u,3u,2u,1u,3u,2u,1u,3u,2u,1u,3u,2u,1u,3u,2u,1u,3u,2u,1u};
enum { GLOBAL_PULSE_BANK_BYTES = 32060 };
static const GlobalAssetSourceTile global_pulse_source[] = {
 {58u,UINT64_C(0xc81d2d4f1406ccd8)},
 {59u,UINT64_C(0x54248fce4a428cfb)},
 {60u,UINT64_C(0xaa7678e84837382e)},
 {62u,UINT64_C(0xa8a22449671b45c2)},
 {165u,UINT64_C(0x3ab7eacc37218895)},
};
static const GlobalAssetPaletteColor global_pulse_palette[] = {
 {113u,UINT32_C(0x380000)},
 {114u,UINT32_C(0x510000)},
 {115u,UINT32_C(0x6d0400)},
 {116u,UINT32_C(0x860400)},
 {117u,UINT32_C(0x9e0800)},
 {118u,UINT32_C(0xba0c00)},
 {119u,UINT32_C(0xd31400)},
 {120u,UINT32_C(0xdf3c00)},
 {121u,UINT32_C(0xe7610c)},
 {122u,UINT32_C(0xeb8a18)},
 {123u,UINT32_C(0xf3ae24)},
 {124u,UINT32_C(0xfbcb30)},
};
static const unsigned global_pulse_resource_ids[] = {80058u,80059u,80060u,80062u,80165u};
enum { GLOBAL_PULSE_PORT = 1, GLOBAL_PULSE_FIRST_RECORD = 155 };
#define GLOBAL_PULSE_PORT_FNV UINT64_C(0x95cfa13155109d97)
static const uint64_t global_pulse_record_fnv[11][3] = {
 {UINT64_C(0x3fe58ed27471f264),UINT64_C(0x0b0ba64e14d161c3),UINT64_C(0x4ccf793bf338e010)},
 {UINT64_C(0x9b5ea0704be3724b),UINT64_C(0x2b6e16b222ffe499),UINT64_C(0x3e1bd0350453737d)},
 {UINT64_C(0x3353f388011f61d6),UINT64_C(0x376764adda23e23c),UINT64_C(0xe1ba0723c31b3ea7)},
 {UINT64_C(0x3848494f3cd51468),UINT64_C(0x716ebe7da1edc91a),UINT64_C(0xd3697191e572d92f)},
 {UINT64_C(0x8fb2540acf28469b),UINT64_C(0x077b667442b0402e),UINT64_C(0xe4785ef6d4f4d814)},
 {UINT64_C(0x029adf2886282b82),UINT64_C(0x74f38c411099bb7c),UINT64_C(0xaf6eaac0fc23bb5e)},
 {UINT64_C(0x2eccb0e9abadc314),UINT64_C(0x875fd247e9d720e2),UINT64_C(0xd49f94b35cd6e774)},
 {UINT64_C(0x61ee7e432971e129),UINT64_C(0xedbbf539400b12aa),UINT64_C(0x5b8f8ed2e2b45902)},
 {UINT64_C(0xa95ef38fcf6a22ac),UINT64_C(0xabface4535e24b48),UINT64_C(0x05a7a388d00e3312)},
 {UINT64_C(0x86cc7aaa348a5acd),UINT64_C(0x23fdbafeced45b1b),UINT64_C(0xac6ddb2e210a74a0)},
 {UINT64_C(0xe33a916638f2275f),UINT64_C(0x5ce7d02d81ebc88d),UINT64_C(0x125d69cb06f8357c)},
};
enum { GLOBAL_HITFLARE_BANK_BYTES = 17810 };
static const GlobalAssetSourceTile global_hitflare_source[] = {
 {146u,UINT64_C(0x728bd1411bf93862)},
 {147u,UINT64_C(0xa194be258be5966d)},
 {148u,UINT64_C(0x6862b82d59cc892e)},
 {149u,UINT64_C(0x20c0c0769a07dad0)},
 {150u,UINT64_C(0x08ac828d16156290)},
 {151u,UINT64_C(0xaf6f6ea168572b9c)},
 {152u,UINT64_C(0xe512543cd3019da8)},
};
static const GlobalAssetPaletteColor global_hitflare_palette[] = {
 {112u,UINT32_C(0x200000)},
 {113u,UINT32_C(0x380000)},
 {114u,UINT32_C(0x510000)},
 {115u,UINT32_C(0x6d0400)},
 {116u,UINT32_C(0x860400)},
 {117u,UINT32_C(0x9e0800)},
 {118u,UINT32_C(0xba0c00)},
 {119u,UINT32_C(0xd31400)},
 {120u,UINT32_C(0xdf3c00)},
 {121u,UINT32_C(0xe7610c)},
 {122u,UINT32_C(0xeb8a18)},
 {123u,UINT32_C(0xf3ae24)},
 {124u,UINT32_C(0xfbcb30)},
 {125u,UINT32_C(0xffe73c)},
 {126u,UINT32_C(0xfffb96)},
 {127u,UINT32_C(0xfffff3)},
};
static const unsigned global_hitflare_resource_ids[] = {1060146u,1060147u,1060148u,1060149u,1060150u,1060151u,1060152u};
static const unsigned global_hitflare_phase_indices[] = {146u,147u,148u,149u,150u,151u,152u};
static const unsigned global_hitflare_phase_ttl[] = {7u,6u,5u,4u,3u,2u,1u};
enum { GLOBAL_VULCAN_BANK_BYTES = 32060 };
static const GlobalAssetSourceTile global_vulcan_source[] = {
 {67u,UINT64_C(0x9f5342ea1a7217ae)},
 {70u,UINT64_C(0xfb4ea1a99e585804)},
};
static const GlobalAssetPaletteColor global_vulcan_palette[] = {
 {113u,UINT32_C(0x380000)},
 {114u,UINT32_C(0x510000)},
 {115u,UINT32_C(0x6d0400)},
 {116u,UINT32_C(0x860400)},
 {117u,UINT32_C(0x9e0800)},
 {118u,UINT32_C(0xba0c00)},
 {119u,UINT32_C(0xd31400)},
 {120u,UINT32_C(0xdf3c00)},
 {121u,UINT32_C(0xe7610c)},
 {122u,UINT32_C(0xeb8a18)},
 {123u,UINT32_C(0xf3ae24)},
 {124u,UINT32_C(0xfbcb30)},
};
static const unsigned global_vulcan_resource_ids[] = {80067u,80070u};
enum { GLOBAL_VULCAN_PORT = 7, GLOBAL_VULCAN_FIRST_RECORD = 221 };
#define GLOBAL_VULCAN_PORT_FNV UINT64_C(0x58b8cf2abb575185)
static const uint64_t global_vulcan_record_fnv[11][3] = {
 {UINT64_C(0x23561552312b0b02),UINT64_C(0xc3f92901d88e7fbe),UINT64_C(0x3bcc72cbfb6d5953)},
 {UINT64_C(0x93ef5beb5e67c729),UINT64_C(0x0cb771bac9733abc),UINT64_C(0x54d209d68391dea1)},
 {UINT64_C(0xf55ea773124b2b83),UINT64_C(0xfbd7be20e6119a40),UINT64_C(0x2c24d2731c9f30e3)},
 {UINT64_C(0x4aab6619ddc5861e),UINT64_C(0x6c05b0c60eb86d43),UINT64_C(0x29180c4d36ac4693)},
 {UINT64_C(0xe5bbe98a53ca561f),UINT64_C(0xe5bb498a53c9463f),UINT64_C(0xe5bb498a53c9463f)},
 {UINT64_C(0xe5bbe98a53ca561f),UINT64_C(0xe5bb498a53c9463f),UINT64_C(0xe5bb498a53c9463f)},
 {UINT64_C(0xeb9614e50b3576c3),UINT64_C(0xef4b7798deff2c71),UINT64_C(0x45fc6a6079243b96)},
 {UINT64_C(0x3c6cce7b7049ef52),UINT64_C(0x7741f7cb05ff00ca),UINT64_C(0xca225c5d48caf9d6)},
 {UINT64_C(0x379904f5a37f31cc),UINT64_C(0x3799a4f5a38041ac),UINT64_C(0x3799a4f5a38041ac)},
 {UINT64_C(0x6029ca73a5d2fb47),UINT64_C(0x602a6a73a5d40b27),UINT64_C(0x602a6a73a5d40b27)},
 {UINT64_C(0x8afdcb780f83f14a),UINT64_C(0x8afd6b780f834e2a),UINT64_C(0x8afd6b780f834e2a)},
};
enum { GLOBAL_SMOKE_BANK_BYTES = 17810 };
static const GlobalAssetSourceTile global_smoke_source[] = {
 {135u,UINT64_C(0x834742a71f5082f1)},
 {136u,UINT64_C(0xf420c811c5342906)},
 {137u,UINT64_C(0x1b6be6a44ef2f7f9)},
 {138u,UINT64_C(0x6049d776579346e8)},
 {139u,UINT64_C(0x1a71d31e21f5dfaa)},
 {140u,UINT64_C(0xa87ef6923bf4e24b)},
 {141u,UINT64_C(0x912e4d02ec565943)},
};
static const GlobalAssetPaletteColor global_smoke_palette[] = {
 {9u,UINT32_C(0x797979)},
 {10u,UINT32_C(0x8e8e8e)},
 {11u,UINT32_C(0xa2a6a2)},
 {12u,UINT32_C(0xbababa)},
 {13u,UINT32_C(0xcfcfcf)},
 {14u,UINT32_C(0xe7e7e7)},
 {15u,UINT32_C(0xfbffff)},
};
static const unsigned global_smoke_resource_ids[] = {1060135u,1060136u,1060137u,1060138u,1060139u,1060140u,1060141u};
static const unsigned global_smoke_phase_indices[] = {135u,136u,137u,138u,139u,140u,141u};
static const unsigned global_smoke_phase_ttl[] = {7u,6u,5u,4u,3u,2u,1u};
enum { GLOBAL_SMALL_EXPLOSION_BANK_BYTES = 17810 };
static const GlobalAssetSourceTile global_small_explosion_source[] = {
 {122u,UINT64_C(0x19b7637c1469f360)},
 {123u,UINT64_C(0x18f02cc5cb8df708)},
 {124u,UINT64_C(0x25792af6c594081b)},
 {125u,UINT64_C(0x0a9bc24f99095a66)},
 {126u,UINT64_C(0xca99f5c48782db68)},
 {127u,UINT64_C(0x3967c31439aea00b)},
 {128u,UINT64_C(0x37a292527580e81c)},
 {129u,UINT64_C(0xba48bc2b6760813f)},
 {130u,UINT64_C(0xf8a796418cb59a12)},
 {131u,UINT64_C(0x1769e0a1c6fde96b)},
 {132u,UINT64_C(0x0ee1f2c21d3ecff4)},
 {133u,UINT64_C(0xf8ab18755d8866de)},
};
static const GlobalAssetPaletteColor global_small_explosion_palette[] = {
 {75u,UINT32_C(0xd7796d)},
 {76u,UINT32_C(0xe38e82)},
 {77u,UINT32_C(0xeba296)},
 {79u,UINT32_C(0xffcbc3)},
 {117u,UINT32_C(0x9e0800)},
 {118u,UINT32_C(0xba0c00)},
 {119u,UINT32_C(0xd31400)},
 {120u,UINT32_C(0xdf3c00)},
 {121u,UINT32_C(0xe7610c)},
 {122u,UINT32_C(0xeb8a18)},
 {123u,UINT32_C(0xf3ae24)},
 {124u,UINT32_C(0xfbcb30)},
 {125u,UINT32_C(0xffe73c)},
 {126u,UINT32_C(0xfffb96)},
 {127u,UINT32_C(0xfffff3)},
};
static const unsigned global_small_explosion_resource_ids[] = {1060122u,1060123u,1060124u,1060125u,1060126u,1060127u,1060128u,1060129u,1060130u,1060131u,1060132u,1060133u};
static const unsigned global_small_explosion_phase_indices[] = {122u,123u,124u,125u,126u,127u,128u,129u,130u,131u,132u,133u};
static const unsigned global_small_explosion_phase_ttl[] = {12u,11u,10u,9u,8u,7u,6u,5u,4u,3u,2u,1u};
#endif
