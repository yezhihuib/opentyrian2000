# Sonic Wave 105/106/124/125

## Finite change

Normal bank 8 `ENTITY_TILE` 105/106/124/125 now use four generated green-energy
heads in slots 563–566. Together with the unchanged prior 17, this covers all 21
normal Sonic head identities. This does not complete Sonic shadow artwork or
prove every game mode, level, weapon combination or renderer.

105 and 106 are horizontal counterparts; 124 and 125 are another horizontal pair.
124 is not a vertical flip of 105. Two independently generated masters preserve
the separate upper-hook/flat-shelf and lower-crescent/top-cap profiles, bright
green cores and softer transparent energy edges. Native 24×28 and 48×56 reviews
passed. Density 8 source registration is proportional, with original logical
margins and unchanged 12×14/anchor 0 placement.

Original rear port 11, mode 1, powers 7–11 uses records 282–286. Every record emits
the same four simultaneous pieces, `weapani=0`, `trail=255`; 105/106 use `by=-7`,
124/125 use `by=7`, left/right `bx=-2/+2`, `sx=-13/+13`, `sy=0`, `del=100`.
They are neither animation frames nor the separate 143/144 joined-wave seam.

Only `src/render_mirror.c` changes production C: the four-member predicate, exact
decoded indices+coverage FNV guard, pre-cache gates and the finite shadow
extension below.
Guards run before every cold or warm lookup, including source reload at the same
address. Christmas, two-player, Galaga, linked, mismatched/null/truncated source,
unsupported density and explicit original/missing/invalid/no-assets contexts
retain classic drawing. No gameplay, shot tables, input, RNG or native blitter
code changes. The four additions take each default pack from 625 to 629 entries.
An inverse-catalog fingerprint proves all existing mappings remain unchanged.

## Verification

- Strict production build passed, using the established existing-warning
  suppression for misleading indentation.
- Frozen PNG/RGBA/HDR1 reconstruction passed twice in a relocated Git-free
  source subset. Source/runtime/catalog corruption and unsafe-output rejection
  tests passed.
- Authored-art optimized and ASAN/UBSAN tests each passed 12,048 extracted
  production NORMAL/BLEND/SHADOW wrapper cases and 790,348,800 native INDEX8 byte
  checks, with native callback order and libc RNG preserved.
- 236 malformed/missing/resource-fallback variants, 472 density cases, 128 mode
  states, 240 selected-source rejections, 528 poisoned-cache denials and 128 early
  shadow cases passed. All 14 meaningful weakened-guard mutants were rejected.
- Original records 282–286 and their +1000 copies were verified across all three
  original weapon tables. Prior 17 bindings coexist without payload changes.
- Two paired controlled game runs, P7 and P11, each completed 90 logic ticks in
  Episode 1/Normal/physical 9 with fixed existing seed 0x5eed and rear 11/mode 1.
  All full-state/RNG/input/projectile/collision/loadout/native-pixel traces match
  the baseline. Presentation RNG before/after matches at every tick. Each power
  retains six byte-identical classic PNGs and 556 unchanged classic quartet
  shadow draws. Exactly 556 normal quartet draw records become HD; geometry,
  order, style and every other draw record remain unchanged.
- Both powers have zero coverage mismatches and zero rendering rejections.
  Actual 640×400 software-renderer screenshots retain legible green crescent
  geometry. The surrounding original/previously accepted scene and HUD are not
  a claim of full-HD-scene validation.

The successful capture pass contains 72 decoded PNGs totaling 14,500,248 bytes;
peak game RSS was 111,919,104 bytes. Processes were capped at 512MiB, compilers
at 1GiB, PNGs at 128MiB, with a 5GB free-disk floor. A read-only dynamic interceptor
wrote existing export requests directly to PNG and captured the real 640×400
SDL framebuffer before the unchanged real presentation call. No BMP output was
written. An earlier capture-only attempt had an overly small internal-frame
size bound and empty display files; it is retained separately and is not
accepted visual evidence.

## Scope limits

These are controlled high-power loadout replays, not naturally purchased P7/P11
playthroughs. Windows, GPU rendering, later levels and multiplayer are untested.
Excluded quartet shadow contexts retain deliberate classic fallback. The other
28 explicitly excluded player-shadow identities and canonical older assets are unchanged;
the finite new-family verifier does not claim a fresh aggregate rebuild of all
historical asset families in a reduced checkout.

## Finite alpha-shadow extension

The same four canonical density-8 head resources now supply alpha to the
accepted per-command Vulcan/Multi/Protron smooth-shadow compositor. Head RGB
never colors the shadow, and no artwork, resource, manifest, logical rectangle,
anchor, indexed blitter, shot origin, visibility decision or gameplay data changes.
Every admitted command still runs its original indexed darkening once, with the
original palette-ramp floor and draw order. Full alpha applies the existing full
shadow strength; partial alpha blends that operation into the composed underlay.
Alpha-zero pixels retain their underlay, including authored HD and cloud detail.

Only normal bank 8 TILE 105/106/124/125 are added. Source indices and coverage,
frozen canonical RGBA, selected bank identity/size, resource path/pointer and
matching command epoch are checked independently of head order, including a cold
shadow before its head. Two-player, Galaga and linked contexts are denied before
cache access and rechecked at shadow begin and native-write consumption. Other
existing density/source/resource/INDEX8/canvas guards remain in force. Density 4,
negative or wrapping horizontal origins, out-of-range vertical origins, changed
source data, missing or malformed resources and wrong warm-resource roots keep
the original shadow. Matching padded INDEX8 pitch and ordinary vertical clipping
remain supported. The other 28 explicit classic-shadow identities are unchanged.

Fresh paired P7 and P11 controlled actual-engine checks each finish 90 ticks.
Each comparison admits 490 quartet shadow draws; 66 negative-x calls deliberately
stay classic. All 556 already accepted HD head commands remain unchanged. Original
state, RNG, input, projectile, collision, loadout, palette and native INDEX8 traces
are byte-exact, as are all six classic PNG captures per power. Every other ordered
draw command is unchanged, with zero coverage mismatches or renderer rejections.
The 72 decoded runtime PNGs total 14,933,720 bytes; peak game RSS is 111,845,376
bytes. Native 640x400 parent review accepts the aligned smoother contours with
stable heads and surroundings. This is bounded Linux dummy/software-renderer
acceptance, not a naturally purchased loadout, full-level clear, Windows or GPU
claim. Existing resource limits and PNG-only capture rules remain in force.

The prior head binding/resource regression still passes optimized and ASAN/UBSAN
runs (12,048 extracted wrapper cases and 790,348,800 INDEX8 bytes each), including
all 14 weakened-guard mutants. Its shadow-operator stub is intentionally only a
head-isolation test; the dedicated compositor test below exercises real production
preparation, begin, pixel consumption and end. Its compositor arithmetic oracle is
independent, while decoding and frozen alpha inputs are shared and protected by
separate source/reference checks. Unit normal-head drawing and font hooks remain
stubs, and those units do not claim HD-head blending, font restoration or complete
later-command integration. The actual-engine pairs cover the documented bounded
head/shadow interaction.

The dedicated optimized and ASAN/UBSAN compositor suites each pass 25,440 geometry
cases, 1,659,772,800 native INDEX8 bytes and 363,266,048 RGB samples. It includes
456 early guard denials, 212 source cases, 616 resource cases, 137 begin
identity/epoch cases, 116 pixel/mode cases, 24 later original normal-write/shadow
checks, 84 unchanged classic-route cases and 169 positive prior-thirteen cases.
All alpha-zero, partial and full coverage categories are observed across classic,
HD and cloud underlays. This establishes compositor math and ordered native-write
handling within the explicit unit scope above. LeakSanitizer alone is unavailable
under this executor's ptrace restriction; ASAN/UBSAN halt-on-error checks remain
enabled, with the same memory ceilings and no findings. All six dedicated shadow
guard mutants are rejected by the intended assertions. Peak child RSS is
390,956 KiB, below the 512 MiB ceiling.

## Reproduce

```sh
python3 prototype/build-sonic-quadrant-art.py
python3 tests/test_sonic_quadrant_art.py
python3 tests/run_sonic_quadrant_tests.py --data ORIGINAL_DATA_DIR \
  --out NEW_EXTERNAL_RESULTS --sanitize --mutants
python3 tests/run_sonic_quadrant_shadow_tests.py --data ORIGINAL_DATA_DIR \
  --pack COMPLETE_CURRENT_PACK --out NEW_EXTERNAL_SHADOW_RESULTS --sanitize --mutants
```

The existing controlled replay accepts:

```sh
opentyrian2000 --data=ORIGINAL_DATA_DIR --render-test=local \
  --render-front-port=0 --render-rear-port=11 --render-rear-power=7 \
  --render-rear-mode=1 --render-assets=COMPLETE_CURRENT_PACK --render-ticks=90
```

Use power 11 for the second endpoint. Its built-in exporter normally uses BMP;
the bounded validation used the PNG-only capture interceptor described above.

## Subsequent finite extension

The later [remaining Sonic17 and shared Mint27 shadow batch](sonic-mint-shadows.md)
extends the same guarded compositor while preserving these four heads and
shadows. The ten Regular Missile, Charge and green214–217 classic exclusions
remain; earlier28-exclusion counts above describe this quartet checkpoint.
