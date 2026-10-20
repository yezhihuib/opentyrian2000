# Authenticated ASTEROID1 shield blends

This display-only extension preserves accepted HD rock/enemy detail beneath the
original cyan shield effect. It does not replace the shield artwork, change
collision, damage, invulnerability, event timing, RNG, or the indexed blitter.
The optional ASTEROID1 catalog remains 57 resources; no artwork is added.

## Finite admission

Only hue `0x80` from the normal explosion sheet is newly admitted, with semantic
pins covering all 168 decoded palette cells and 168 coverage cells of each of
22 nonempty frames: 229–237, 248–250, 252–256, 267–269, 272 and 275.
The five empty animation slots 251, 270, 271, 273 and 274 remain no-write slots.
Each callback re-decodes and verifies its entire source frame, its actual source
pixel, known sheet identity/size, original indexed result and current monotone
palette ramp. Same-address mutations cannot reuse cached trust.

All existing level, mode, source, layout, owner, suppression and font gates stay
in force. The original 116 warm/contact frames retain their separate admission
list. Unknown sheets/hues and incompatible layouts or palettes still restore
classic regions conservatively; this is not a universal blend fix.

## Verification

- Strict C99 renderer build with warnings treated as errors.
- Extracted current production helper/callback/indexed blitter tests pass in
  optimized and ASan/UBSan modes: 3,257,553 checks per mode, 534 resets,
  281 positive callbacks, 180 negative callbacks and 59 original indexed blits.
- All 22 shield sources receive independent same-address pixel/coverage
  corruption tests; all 27 animation slots and densities 4/8 are covered.
  First-level functions and callback tail are checked against their prior source.
- Native engine opening at 2× and 4×, 120 ticks each, seed `0x5eed`, stationary
  and no fire, compared against the pre-shield baseline. All 22 gameplay/draw
  trace files match byte-for-byte at each scale, including state/RNG and INDEX8
  hashes, original event clock, collision and projectile traces.
- Per scale, 2,556 authenticated shield writes include 1,154 over HD. No accepted
  shield callback restores a region. All six paired captures at ticks 101–103
  change only within previous fallback regions. Cyan shield visibility and
  retained underlying rock detail were visually inspected at both scales.
- Opening restore events decrease from 25 to 15. The remaining 15 are unchanged
  unknown-sheet hue `0x10` player/invulnerability blends, not this shield path;
  their conservative fallback is deliberately retained.
- Flag-off, entirely missing optional pack and corrupt-header optional pack
  controls at both scales retain byte-identical output and trace files.
- An assisted original-event warm-contact window at location 3940, seed 1,
  ordinary player fire (front port 1, power 11, x=74), 80 ticks at both scales,
  retains 70,660 warm RGBA writes per run and byte-identical traces/captures.

The accepted set consists of 20 engine runs, 2,240 total logic ticks,
266 exact trace-file comparisons and 52 capture files. Coverage and restoration
mismatch counts are zero. Two exploratory runs using an unsupported scaler
name produced 2× output; they are excluded from these counts and all 4× claims.

## Limits and reproduction

The runtime evidence uses headless SDL dummy/software rendering with external
read-only observers. The opening preserves original event progression; the
warm regression explicitly omits prefix spawns while replaying original setup.
Neither is a natural campaign, Windows/GPU, desktop-window or whole-level pass.
Native left/right clipping is not newly certified. Green, smoke/value,
unknown-sheet player/invulnerability blends and other unknown effects remain
out of scope. LeakSanitizer is disabled for executor compatibility; ASan and
UBSan are enabled. Runtime memory is bounded at 512 MiB, compilers at 1 GiB.

With independently installed original game data, run:

```
python tests/run_asteroid_effect_blend_tests.py --repo . \
  --source-sheet /path/to/original/newsh6.shp --output /path/to/test-output
```

No original data, decoded sprites, captures, executables or external QA scripts
are included in this change. See `validation.json` for the portable summary.

A later [finite Talon invulnerability extension](../asteroid1-talon-blend-v1/README.md)
addresses the separate bank9 player blend described above. The measurements
here remain the historical shield-only checkpoint.
