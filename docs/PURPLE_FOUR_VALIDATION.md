# Purple ten-piece formation: four static designs

Accepted bounded cloud-runtime review on 2026-10-11, based on2152db5b4befe23165105bd363d3407fb252feb3. Newsh2 bases49/51/89/127 map to slots265–268. Each retains logical24×28, anchor6,7 and the original ordered quadrants. Only the finite slot expression and asset-array capacity change in production.

## Complete family and original behavior

Types26/28 use49,27/29 use51,30 uses89,31 uses127. The ten-piece formation contains one nose, three bodies, three left arms and three right arms. Designs are static; objects move independently. Arms49/51 remain distinct, not forced mirrors. Original22-pixel body spacing and draw overlap remain. Types26/27 initially sit still but later original events set movement and acceleration.

Loaded-record closure checks all5,103 records across the HDT and episode4/5 tables, plus all1,010 level events. No other records share the sixteen source quadrants or launch/drop this family. Events33/45 assign future death drops; they do not remove the current object.

Supported original Pulse155 controls at1608 establish:
- Nose: hits1609/1611; removes nose and three linked bodies, leaves six independent arms, creates three391 drops.
- Body: removes three linked bodies, leaves nose and arms, creates three391 drops.
- Each moving arm: only the targeted arm is removed. All four designs show the original filter208 across every quadrant at1610.
- Later body type30/link182: hits2119/2121, original394 drop.
- Later arm type26/link11: hits2123/2125 after original separation; original repeating explosion tail retained. Starting this test before separation could hit the overlapping body first, so actual collision victims are verified.

The fixture uses original one-player full-game defaults. Event45 is gated off in this mode, so no623 nose drop is expected. Other original mode-dependent drops628/603/513 remain source-audited and unchanged, not newly redrawn or claimed runtime-tested in alternate modes. Explonum0 still invokes the original four explosion quadrants; it means no repeating tail, not no explosion.

## Validation

All replays start at0 with private survival and no injected weapon71. Ordinary play ends1052; no private survival/observer/control/capture code enters production.

Native2×/4×1555–1809 yields8,200 successful new HD quadrant calls:127=820;49/51/89=2,460 each. Full original state/indexed/RNG/collision traces agree. Missing all four assets is baseline-RGB-exact; cross-scale logical RGB agrees. Clear1771–1809 is baseline-exact. Actual120-frame native2× motion1608–1727 and4×1610 pass independent visual review; each lossless frame matches direct SDL readback, with no old-art flash, quad seam or lost independent arm motion.

The new ASan/UBSan oracle passes1,495,307,264 pixel comparisons,11,500 quadrant calls,2,211 source/part guards, all24 quadrant orders, all256 filters, and all47 old/new enemy bindings. Extracted original wrapper/RLE parity passes5,640 cases. All16 prior regression scripts pass (14 sanitized suites and2 pure-Python alpha checks). Newsh2 base49 and newshE base49 are explicitly isolated by source role and cache slot. Existing273 HDA files remain byte-identical. LeakSanitizer is disabled under the tracing environment; address and undefined-behavior checks are enabled.

## Reproduction and limits

`python prototype/build-purple-art.py --output NEW_DIRECTORY` reproduces all four authored PNGs and exact HDA bytes from the generated atlas. Numerical original bounds/draw positions are registration contracts; no original game pixels are included.

`python prototype/build-hd-assets.py` verifies18 packs,2786 HDA entries,285 formal PNGs and273/277 default entries. The complete source artwork, mapping and test scripts accompany this batch. The later reuse checks close this family only; unrelated later enemies, alternate game modes, Windows and full-level acceptance remain outside the visual claim.
