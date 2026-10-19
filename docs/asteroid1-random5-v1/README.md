# ASTEROID1 optional static random rock

This fifth bounded family adds one image for three original motion variants.
The previous21 image identities and four families remain byte-identical, and
the global manual-HD manifest remains629 assets. This is not a completed second
stage, a Windows package, or broader physical-level admission.

## Compatible opt-in

```
./opentyrian2000 --data=/path/to/original/tyrian2000 --no-xmas \
  --asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1
```

The historical runtime directory now contains22 regular HDA files across five
independent families. This option does not choose or skip a level. Normal-data
Episode1 physical1 (ASTEROID1, campaign section5) and the existing incompatible-
mode guards are unchanged. Physical2, title demos, Christmas data, multiplayer,
linked/Galaga, arcade/action, SuperTyrian, timed, bonus, network and recording
modes remain excluded. Normal-data does not mean Normal difficulty only.

Older packs remain compatible. A missing, corrupt, wrong-role, wrong-anchor,
malformed or unsupported-density new image leaves all three motion variants
classic while the previous21 identities remain independently eligible. No
ordinary spriteSheet8 or global manual-HD registration is added.

## Exact source relationship

Original records135,136,137 use the same static enemy bankD/newshd.shp base5,
size1 (24x28) image. Its four original tile calls are5,6,24,25, with offsets
0,1,19,20 and the original top-left(ex-6,ey-7). All three have ani1/animate0,
armor3 and no turrets, drops, launch children or damage alternate. Their original
y-speeds are1,2,3. These are three motion records sharing one pose, not an
animation or rotation. No other original bankD record references this base.

Each record has one entry in physical1's active21-entry random table, for a
combined3/21 design weight, tied for the highest static-design weight. The
original engine attempts a random spawn on3/100 active frames, then chooses a
table entry and requires an available slot in0–24. Those probabilities are
source properties, not measured on-screen frequency. The existing level-start
enable and original event13/14 toggles remain authoritative.

One built-in imagegen master redraws the source asymmetric grey rock, broad
surface forms and dark recesses. The prior common4 master is a material/style
reference only. The exporter globally aligns the image to the original support
and uses inward-only contour smoothing; no HD alpha extends outside original
coverage. Parent review includes the actual2x size. Original game data stays
external and is not packaged in the repository.

The private cache loads one image and validates all three complete serialized
77-byte source records on every draw, along with exact loaded bank bytes,
actor/type/base/size/static-pose, surface, mode, clipping, filter and resource
identity. The one density8 zero-anchor payload is preflighted and checked before
the first call each display frame. Sticky cache failure and whole-frame rejection
after a same-frame accepted quadrant follow the existing family pattern.
Original indexed writes, RNG, movement, armor, collisions, damage and destruction
remain authoritative.

## Bounded validation

See validation.json for exact source, unit, engine and preservation receipts.
Optimized and ASan/UBSan extracted-production tests cover one valid resource and
13 invalid fixtures, all three full record pins including speed-byte mutation,
12 ordered quadrant calls, clipping/filter/surface/mode exclusions and warm
corruption. The four earlier families are rerun in both modes. LeakSanitizer is
unavailable in this executor; AddressSanitizer and UndefinedBehaviorSanitizer
remain enabled. The independent source/resource review reports no substantive
defects and reproduces the packaged image byte-for-byte.

Actual-engine observations use an external physical1 selection/export-only
diagnostic. Random tables, event data, actor creation, health and input are
unmodified. Fixed-seed selection is explicitly diagnostic and does not establish
natural campaign progression or survival. Requested tick counts and actual
observed counts are recorded separately, including early unprotected death.
The first seed0x5eed pair ended after168 observations following death without a
base5 spawn; this is retained as a preflight rather than new-family evidence.
Seeds1–3 also showed no new family in120-tick selection diagnostics. Seed4
produced record135 through the original random spawner at tick31, slot1, armor3.
Fresh120-tick baseline/candidate pairs at native2x and4x each accepted352 new
quadrant calls, including original partial top clipping, with no coverage
mismatch or rejected HD frames. All14 gameplay/state/RNG/INDEX8 traces and
classic captures are exact. Record136/137 motion variants have full-record and
geometry unit coverage; the actual-engine witness is record135 only.

The missing5 pair retains all21 prior identities and6115 prior-family calls,
with exact traces and all captures. A separate60-tick flag-off physical9 pair
also remains exact. Parent source-contact and native640x400 tick60 review pass.
Native visible-*.png captures are the actual2x/4x output; display-*.png is the
internal density8 canvas. No full-level clear, Windows/GPU/fullscreen or
performance acceptance is claimed. No GitHub push or package is part of this
batch. Only explicit named inputs were read; forbidden paths were untouched.

Final combined new output is about41.1MB, including14.44MB of PNGs, with more
than5GB free. PNG output briefly reached17.54MB before this batch's internal
display captures were losslessly recompressed with unchanged pixel hashes; the
transient16MiB-cap overage is disclosed in validation.json. No old output was
deleted or modified. Runtime and compiler address-space limits are512MiB and
1GiB respectively.

Rebuild: prototype/build-asteroid1-random5-art.py --data ORIGINAL --out OUTPUT.
Tests: tests/test_asteroid1_random5_assets.py --data ORIGINAL --out OUTPUT
--sanitize. Add --sdl-include directories when pkg-config is unavailable.
