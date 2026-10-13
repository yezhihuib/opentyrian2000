# Finite green100 gem and shared fixed100

Source and bounded runtime checkpoint passed. Tested production/art/prototype commit:083bd54d269f982a9f2b863969f8a2246d263302. Three controlled actual runs completed with matching original state/RNG/indexed/input/collision traces. Author and independent technical/visual reviews passed; this finalization changes documentation only. Repository publication and Windows packaging are separate steps.

## Scope

- Record394, global `spriteSheet11` (original bank11/runtime21), body IDs32–36 only. One12×14 tile at anchor(0,0), density8.
- Five brightness states of the same faceted diamond, in the original16-draw sequence:32,32,33,33,34,34,35,35,36,36,35,35,34,34,33,33. Animation and movement stay in the original engine.
- Shared fixed `newsh6:169` blue100 symbol, stored168, at most eight original draws. The display-only lease requires fixed/no-follow/deltaY0/TTL1–8, the actual effect-sheet pointer, TILE and NORMAL/BLEND.
- Record509 intentionally shares this fixed symbol. Episodes1–3 keep its original nominal250 reward/body95 while displaying100. Episodes4/5 keep nominal100/body57. No509 body replacement or reward correction.
- Generic moving effect35 can reach169 and remains classic. No generic169 asset binding.

The independent six-file preflight uses roles118/119, slots493–498 and capacity499. Missing, malformed, wrong-density or hash-mismatched art keeps the whole100 family classic. Existing25/75/50 decisions remain independent. All four one-call leases are consumed before any entity return and cleared at frame begin/entity end.

Production changes are limited to `src/render_mirror.c`, `src/render_mirror.h` and one additive eligibility call in `src/tyrian2.c`. Removing precisely those additions restores published641e4e7370c9f3542ba9d0daf1ebf2a1a988614e byte-for-byte. Original constructors, RNG, allocation, event processing, collision/reward, source indexed blits and gameplay data are unchanged.

## Frozen art and provenance

`assets/hd/artwork/gem100-six-v1` is a byte-exact import of the approved generated-only package. Inventory SHA256:4489265f4556f12fecfd1745e271dcbdb2776c52d419971eb998cddc1a40df6d. It contains generated masters/prompts, original support masks and geometry/source hashes, deterministic rebuild code and six frozen outputs. No decoded original RGB is substituted into the generated assets.

The physical gem looks solid while retaining authored fractional alpha. All five bodies have identical alpha and registration. Each has4,309 nonzero samples,166 alpha255 samples and4,143 fractional samples, including near-opaque252–254 interiors and an inward contour. Do not interpret the frozen package's “opaque solid interiors” prose as a universal alpha255 guarantee. The separate, byte-pinned `art-opacity-clarification.json` records this clarification without changing frozen pixels or inventory.

Six canonical PNGs and six exact HDA files were added to each existing default preview/debug pack. Each manifest pack grows501→507 entries; physical HDA count507→513 includes six existing separately managed HUD bundles. All previous pack payloads and manifest entries are preserved. No new full pack copy is created.

## Source verification

- Exact frozen-art rebuild, HDA header/payload/EOF, PNG pixels, full RGBA hashes and FNV stamps; identical body alpha, monotonically increasing body brightness and original-support containment.
- All four families under ASan/UBSan in both default packs, reusing the published25 C oracle with explicit member-count/capacity adaptation. Each gem run checks2,936,929 assertions and844,032 RGBA sample cases; each old-family run retains its existing pixel/RLE checks.
-80 malformed-resource cases, including missing/header/key/density/geometry/anchor/payload/alpha/trailing data and4×-only fallback. One small six-file fixture is reused.
- All16 four-family availability masks use one27-file fixture. Full-valid mixed composition checks41,332,798 assertions, every ordered family pairing and NORMAL/BLEND, plus four-lease isolation and wrong/inactive/rejected paths.
-15 deliberately broken variants are killed, covering body bank/slot/record, lease eligibility/leak, authored alpha/blend, incomplete family, skipped indexed writes, and interfamily dependence/poisoning.
- Full optimized production build and disabled-renderer header/source/callsite compilation pass using the existing pinned SDL dependency environment. Plain environment lacks SDL; no dependency installation was performed.
- Original-source lifecycle tests use the exact original constructor/allocator/spawn, movement, collection, fixed-effect loop and lethal traversal. Their retained receipt records scenario/assertion counts and source-unit limitations. The separate three-run runtime proof and its bounded visual review also pass; source units retain their own narrower evidence category.

The units use extracted production functions and unchanged real RLE blitters/wrapper with independent RGBA/indexed oracles. They do not demonstrate actual game visibility, natural play, or cross-mode/episode exposure. Existing historical25/75/50 tests and art packages remain byte-identical.

## Reproduce without gameplay

Use fresh output directories:

    python3 prototype/build-gem100-six-art.py
    python3 prototype/test-gem100-six.py --out /tmp/gem100-unit-new --original-data /path/to/original/tyrian2000
    python3 prototype/test-gem100-mutations.py --units /tmp/gem100-unit-new --out /tmp/gem100-mutations-new
    python3 prototype/test-gem100-original.py --out /tmp/gem100-original-new

The original asset data path is only needed by the renderer's exact native RLE oracle. Other compact source fixtures are self-contained and hash-pinned. Generated art rebuild requires Pillow, NumPy and SciPy. C tests use a C compiler, ASan and UBSan; LeakSanitizer is disabled for executor compatibility.

## Completed bounded actual review

Exactly three actual runs reached tick2154 (2,155 logic ticks from0): one no-image baseline and two candidates using identical controlled input and survival instrumentation. This is Episode1 physical level9, Normal, ordinary story, original starting loadout, seed0x5eed. Original LEFT input runs on ticks20–21, then neutral. One artificial original Pulse155 is created at2106, with an alive-only invulnerability floor2 after events. The original collection path remains in force. This is controlled survival evidence, not unassisted play.

The first assigned record30 carrier occupies slot51. The original allocator creates record394 in slot54 before releasing the carrier, retains its constructor RNG draw, then copies the carrier position. Carrier death awards15. At2145 the gem is collected at(90,149) and independently awards100. Fixed stored168/draw169 occupies effect slot0, draws eight times2145–2152 in actual BLEND mode, and is clear at2153 and2154. The run then stops. NORMAL rendering is source/unit coverage.

The runtime artifact contains exactly25 consecutive native640×400 frames for2129–2153 and one native1280×800 still for2146. The16 pre-collection phases are7..16,1..6, with bodies35,35,36,36,35,35,34,34,33,33,32,32,33,33,34,34. Each frame records81/81 matching original source-index cells. This is qualified final-index evidence: equal-colour overdraw cannot be distinguished, and it is not a hidden-layer or whole-frame RGB oracle. No baseline RGB was retained. Nearby original actor overlap is preserved.

Author and independent review found stable registration/facets, the expected held brightness cycle, no unexpected cycle-boundary pop or aura, readable dark green facets on the observed brown-rock background, and a legible blue100 with clean disappearance. The4× still proves the popup only; it does not establish4× gem-body animation. Shared509 fixed100 is source/unit coverage only. Other backgrounds, difficulties, modes and episodes have no new actual visual coverage.

## Portable proof index

- `runtime-verification.json`: three-run parity and lifecycle results with qualified visibility counts.
- `frozen-schedule.json`: observed collection/terminal ticks and exact capture schedule.
- `capture-index.json`: all26 PNG and decoded-RGBA hashes, with paths relative to the separate runtime evidence archive.
- `author-receipt.json` and `technical-review.json`: bounded visual and technical acceptance.
- `paired-build-receipt.json`: tested source/fixture/binary pins and display-only inverse check.
- `evidence-archive-receipt.json` and `evidence-manifest.json`: separate compact runtime archive and file hashes. Images and traces are stored once there, not duplicated in the repository.

`PLAN.md` is the unchanged historical source-only plan, intentionally kept for its original hash pin. Its predictions and prelaunch gates are superseded by the observed runtime receipts. `contract.json` changes only execution-local path presentation; `source_contract_sha256` preserves the original contract identity. Source and mutation receipts retain their original test-only limitations.

This checkpoint closes the100-gem scope. No next artwork batch was started; the next requested deliverable is a Windows test package.
