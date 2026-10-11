# Bounded 45–60-second visual closure

Code and art remain at commit **7021e78386e9c010eb6c56d65d369e9e7e2bd9b8**, on documentation checkpoint e6df63ac5af8536da1c4a121ff43fe1b50d556a0. No new assets or production changes were needed.

## Identity and runtime

Ticks 1566–2087 comprise 522 original ticks, or 15.0075 seconds. This is private survival replayed from tick 0, without weapon 71 injection or external hit/destroy controls. Ordinary gameplay ends at tick 1052.

All 54 observed material identities have accepted finite mappings and resources: 81,858 references, zero untreated. The breakdown is 21 ground tiles, 15 cloud tiles, 10 enemy bases, 7 effect tiles and 1 player base. The only new identities relative to this same trace's prefix are accepted purple bases 49/51/89. Enemy orbs 112/113 have 786 separately identified direct calls, outside the material denominator. Exact identities and machine-readable results accompany this document.

The older identity reference first receives a mutating control at tick 2119, after this window. The new logs-only and streamed runs contain no hit/destroy controls. Both match all 2,088 original state rows, 328,210 material rows and compatible collision, projectile, pose, fire and clock logs through tick 2087.

All 522 rendered frames are HD-ordered with zero coverage, RGB-classic, restoration or rejection errors. All 87,132 scene calls succeed: 63,830 terrain calls, 19,412 newsh2 enemy calls, 3,104 newshE enemy calls and 786 orb calls. All 1,044 player shadow/blend calls succeed. The renderer and 277-resource default-debug pack exactly match accepted source and art.

## Actual visual evidence

A native 2×, 640×400 SDL software-render readback stream covers all 522 frames. Every losslessly decoded frame equals the direct readback RGBA hash; state and RGB logs equal the separate no-capture run. Lossless H.264 RGB CRF 0 reduces storage while retaining exact pixels. The user preview is separately encoded lossy H.264, with a diagnostic label above the unscaled game view.

Only three native stills were retained, at ticks 1656, 1798 and 2087. No BMP or raw-frame files were written. Capture and delivery media total 29,222,310 bytes. Review boards add less than 0.6 MB, keeping the batch below 30 MB and the authorized 50 MB cap.

Independent visual review passes all 522 consecutive frames, with no old-sprite flash, dropped component, new seam flicker or ordering defect. All three representative native views also pass. Tick 2087 is still active, so this clip does not prove a clear tail.

## Limits and retained evidence

This closes accepted art in this bounded window. HUD/text, the bottom strip, uninstrumented paths, alternate inputs and modes, Windows, GPU/fullscreen and physical 2K performance remain outside scope. Seven effect resources and dispatch are verified, but a direct per-effect HD-success callback ledger is unavailable. Trigger-dependent blue stone remnants are absent here; their earlier bounded original-hit transition test remains separate. Pickup/drop families remain original and are not counted as newly accepted art.

Keep ordinary first-30-second coverage (222 nonempty plus 5 intentional empty identities), private 30–45-second coverage (86 identities), and this window (54 identities) separate. These are overlapping, differently scoped denominators. No new art requirement was found. Earth texture joins and repeated tiles remain visible.

The conservative image/video/raw total, excluding HDA, is 6.038 GiB, with over 15 GiB free. All .bin/.u8 data remain conservatively counted. An exact proposal identifies 12,688 redundant diagnostic BMPs totaling 1,687,493,024 bytes, each with an existing pixel-identical PNG. That proposal authorizes no deletion. Original references, generated source, formal HDA, videos, raw semantic buffers, PNG proofs, logs and rollback checkpoints remain retained.
