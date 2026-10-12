# Gameplay dynamic typography (HUF1)

This finite stage refines the tiny gameplay font used for single-player cash,
level name, bottom messages and the supported arcade-name call site. It retains
original text, color/highlight roles, glyph advances, coordinates and writer
order. Shared font tables, menus, shop text and the large INSERT COIN lettering
are unchanged. Fixed green labels remain the separately validated HUC1/HUT1 art.

## Resource and compatibility

HUF1 contains a 112-byte header and 163,840 bytes of canonical 4× alpha coverage
(512×320). SHA256 is
`3c328c1537cf1e09529ae8805e98a8deb57a859ea80ba269cfea0b55cfae539e`.
It supports 86 reviewed mapped ASCII glyphs using role 7 and exact original
metrics. A run with unsupported or extended/accented bytes remains entirely
classic. The original caller chooses the palette color, brightness and shadow.
Canonical 4× coverage is nearest-sampled at native 2× and repeated at density 8.

The loader separately validates fixed sizes, bounds, padding, map/metrics,
encoded source identities and palette compatibility. Its dependency-free 64-bit
checksums detect accidental corruption; they are not authentication or a
substitute for parsing safety. Missing or invalid HUF1 leaves the selected scene
and other HUD resources active with the original tiny font.

Rendering observes original draw/erase events rather than recomputing text from
current game values. Bottom OPTION36 erasure, long-to-short replacement, message
expiry and stale displayed ending text retain their original history. Persistent
and transient regions have source/owner generations; invalid history fails back
instead of retaining a stale overlay. An unfinished write is aborted before the
output copy. Saved fade owners must match the current valid generation.

The retained allocation bound measured by the source harness is 3,016,953 bytes.
There is no per-frame allocation. Bounded maximal capture/fade work is documented
in the source tests; it is not an FPS or whole-game performance claim.

## Reproduction

The formal source package is `assets/hd/artwork/gameplay-hud-font-v1`. Its 19-file
inventory contains vector/metric metadata, standalone builders and exact output
receipts, without original game bitmap payloads. A fresh relocated build without
canonical images or a resource available as input reproduces PNG, alpha, SVG and
HUF1 exactly. Two audit-only source-path strings were normalized for portability;
glyph geometry and runtime bytes remain identical to the reviewed recovery.

Run `python prototype/build-gameplay-hud-font.py --output /absolute/fresh/path`.
The wrapper rejects existing, in-repository, ancestor and symlink output paths.
The central asset builder verifies the resource in both default HD packs.

## Actual bounded validation

The baseline is published `a50d25799105962e9100eaffa0c1949227ff7b89`; the tested
production candidate is `280e100a7204c907709a04f4186ec3b72d5542f2` plus only formal
packaging and test/documentation changes. The trial used 265 original logic ticks,
with approved private original-routine message/end-level controls, front weapon
17/power 11 and the existing deterministic input fixture. There was no cash
mutation or private survival alteration.

- All 265 original state/indexed-pixel rows and 22 shared ledgers match, including
  38 actual collisions and original indexed blend hashes.
- Original awards produce cash 15 at tick 186, 35 at 252 and 55 at 259, each checked
  against the actual formatted cash writer.
- Long message replacement at 22, natural expiry at 122 and the original end-level
  event after 256 pass. The ending message retains textErase 97 through 264.
- All 21 selected internal 8× A/B comparisons have zero changed subpixels outside
  exact logged font-owner runs. Native 2× also has zero differences outside a
  conservatively sampled ownership mask; that native mask is not claimed exact.
- Six native 2× stills, all 17 ordered transition frames and one true native 4×
  spot were reviewed. Same-scale readbacks are hashed. The 4× run's full internal
  RGB/owner history equals the 2× candidate; different-size native frames are not
  claimed identical.
- All frames have zero renderer coverage/classic-RGB/restoration errors.
- Fresh 120-tick missing and one-byte-corrupt HUF cases exactly match the
  published baseline state/indexed pixels and full HD RGB. Other HD assets remain
  active; font ownership is zero. Their collision traces are header-only. The
  private font-generation diagnostic differs from the baseline stub as expected.

Private controls, observers and FIFO readback hooks are excluded from production.
The 17-frame delivery clip is a lossy, slowed 12 fps review of actual frames, not
an original-speed performance proof. Only compact stills, one lossless transition
stream and summary evidence were retained; internal 8× frames were streamed.

## Source tests and limits

Independent ASan/UBSan tests cover malformed resources and I/O faults, source and
palette mutations, whole-run eligibility, erase/abort history, maximum writes,
fade owner loss and allocation failure. The exact source tests include 190
writer/abort, 64 fade, 88 persistent, 42 scalar/maximal, 92 trust and 216 halo cases;
1,268 history allocations were released. LeakSanitizer is unavailable in this
executor; explicit allocation accounting and ASan/UBSan remain the stated proof.

Actual arcade-name rendering, actual modal transitions and unsupported-byte
fallback are source-test coverage here, not new gameplay visual acceptance.
This bounded original-control fixture does not certify every first-level scene,
all typography, CI or current Windows runtime. Large lettering, remaining meters
and startup/logo work are separate stages.
