# Seven next-segment terrain assets

Accepted bounded cloud-runtime validation on 2026-10-11, based on craft commit e66aa422bad36908ca6fd812ab42805cc0ab512f. See the adjacent JSON for exact counts.

## Scope and identity

- ShapesZ layer1 ID113: two gray rocks, logical24×28, anchor0,0, density8. All seven original holes remain exact:448 transparent HD subpixels. Existing111/114 alpha is unchanged.
- IDs341/342/343 above351/352/353: complete opaque72×56 embedded stone foundation, six24×28 tiles with anchor0,0. The standing newshE entities remain original. Their original +1 logical y registration and linked-removal reveal are preserved.
- Slots246–252, capacity253, terrain pointer registry122. Existing craft and all other production functions are unchanged. No new shadow, blend or gameplay behavior.

## Verification

Replay starts at0 with a private survival flag and no injected weapon71. The ordinary run ends1052; this is explicitly a diagnostic continuation. Full1566-row original state, material, projectile and collision logs agree with baseline. Native2×/4× render1228–1565:1,782 new NORMAL/HD calls, zero coverage/rejection errors, identical cross-scale logical RGB. Missing all seven resources yields baseline-identical RGB.

Wild preserves all9,767 prior restore rows and adds607 restores precisely on new terrain rectangles. All per-frame restore counts agree.577 overlaps have directly logged layer2 cloud evidence;30 bottom-strip cases use source-supported inference because the material logger excludes y≥184. Indexed blend arithmetic is unchanged.

Supported original Pulse155 controls hit at1349 and1351. All six link29 members become unavailable at1351, their last overlay draw is1351, and all six foundations persist through1411 with366 post-destruction NORMAL/HD calls. This synthetic control is separately labeled, not a natural encounter claim.

Fifteen ASan/UBSan suites pass:449,259,220 binder assertions,94,059,984 compositor assertions and280,755,200 craft pixel comparisons. All59 real terrain resources remain resident;531 full/partial rows tested. LeakSanitizer is disabled for the existing tracing environment; address and undefined-behavior sanitizers are enabled.

Actual native2× streams cover60 frames1260–1319 and60 frames1348–1407 per side. Every decoded frame matches direct readback hashes; HUD/bottom agree and all visual differences are confined to the seven tile rectangles. Native4× spot checks and independent continuous review pass. Clouds stay enabled. An additional90-frame aligned113 review finds no hole-edge changes. Whole-level acceptance and Windows acceptance remain outstanding; external earth texture joins are not claimed seamless.

## Reproduction and source ownership

Run `python prototype/build-hd-assets.py` to verify18 packs,2754 HDA entries and269 PNGs; default packs have257/261 entries. `python prototype/build-next-terrain-art.py --help` describes the fresh-directory generated-art rebuild. All seven PNG/RGBA/HDA outputs reproduce exactly. Formal source contains generated target crops, prompts, alpha already baked into the selected crop and numerical accepted-neighbor perimeter constraints. No original game references, masks as separate original files, context masters, diagnostic hooks or captures are included.

Existing first30 coverage remains as documented in FIRST30_HD_COVERAGE.md. This batch does not extend that ordinary-play coverage claim.
