# Second bounded HD milestone: ticks1044–1565

Accepted resource/code checkpoint: **7021e78386e9c010eb6c56d65d369e9e7e2bd9b8**. This is a private-survival replay from0 with original events/scrolling and no injected weapon71. The522-tick window lasts15.0075 seconds. Ordinary play ends1052; this is not ordinary survival or full-level acceptance.

## Result

All **86 observed nonempty identities** have verified finite HD mappings and exact resources:78,368 ordered references, zero unresolved and zero intentional-empty identities in this window. Identity means(category,sheet,ID), not a global numeric ID or PNG count.

- Layer1 terrain:38 identities,47,184 references
- Layer2 clouds:14 identities,9,937 references
- Enemy bases:26 identities,20,024 references
- Effect tiles:7 identities,179 references
- Player base:1 identity,1,044 references

The17 newly observed identities relative to this private trace's own prefix are three craft, seven terrain tiles, six intact stone components and purple127. The complete shared families were integrated, including later stone remnants and the other three purple designs; those additional designs are separate bounded evidence, not extra identities in this window.

The committed [identity ledger](NEXT15_HD_IDENTITIES.tsv) gives exact resource hashes, counts, source category and first/last ticks. All enemy assets include their complete24×28 geometry. Purple127 only enters through its lower two original quadrants during1561–1565; its complete formation and lifecycle are covered by [PURPLE_FOUR_VALIDATION](PURPLE_FOUR_VALIDATION.md).

## Final combined runtime

A logs-only native2× replay using all277 current default-debug resources passes all522 frames with zero coverage, RGB-classic, restore or rejection errors. All1,566 original state rows and full material/collision/projectile/pose/fire/clock files are byte-identical to the no-injection reference.

All82,415 scene HD attempts succeed: terrain60,474; newsh2 enemies15,776; newshE enemies4,932; enemy orbs1,233. All1,044 player shadow/blend calls succeed. Orb112/113 directly logged612/621 attempts are separate from the material ledger's86 identities.

Effects146–152 have exact accepted resources and verified finite dispatch. The effect logger does not expose direct HD-success callbacks, so the179 material references are not mislabeled as179 callback successes; their ledger field says `not_logged`. Integrated frame audits still pass.

No new full-window video was captured. Existing native family previews, independent continuous reviews and the combined logs support this milestone. Final package totals:18 packs,2,786 HDA entries,285 formal PNGs; default preview/debug273/277.

## Checkpoints and remaining limits

- Three craft: e66aa422bad36908ca6fd812ab42805cc0ab512f
- Seven terrain tiles: cb3eca69d2e873baef28b210ec957ecedeea819b
- Complete stone family:492b83baf5ac6c592d5c539aebdca1c94be4e941, fixture docs2152db5b4befe23165105bd363d3407fb252feb3
- Complete purple family:7021e78386e9c010eb6c56d65d369e9e7e2bd9b8

The ordinary [first30 milestone](FIRST30_HD_COVERAGE.md) remains222 nonempty +5 empty =227 identities /172,635 references. This private trace's own0–1043 prefix instead has88 identities /167,984 references. These denominators must not be added or substituted.

HUD/text, the bottom strip y≥184, arbitrary uninstrumented blitters, original indexed gameplay writes and missing/unsupported fallbacks are outside the identity closure. Empty original shield IDs251/270/271/273/274 were verified but do not occur here. Cloud palette-BLEND fallback and original green shadows are intentional. Pickup/drop banks and alternate modes remain original. Earth texture joins and repeated tiles remain visible; no seamless-world claim.

Later stone remnants are right-edge clipped in runtime; full geometry comes from source/oracle evidence. Purple lifecycle tail checks close that shared family only. Other inputs, modes, later scenes, GPU/fullscreen, physical2K performance and Windows acceptance remain unverified. Windows build/launch instructions remain in WINDOWS_HANDOFF.md; `python prototype/build-hd-assets.py` verifies current resources on either host.

## Retained evidence budget

At the2026-10-11 audit, images/video/raw buffers excluding formalHDA total6.010GiB; HDA resources separately total1.391GiB. The raw upper bound includes all.bin/.u8 files, not only screenshots. Disk has15.354GiB free. New capture batches are paused; no files were deleted. An exact redundant-BMP proposal with retained-PNG pixel proof is kept separately and requires specific approval before deletion.
