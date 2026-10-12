# Poison Bomb parent103 finite binding oracle

This is a source/binder/compositor check, not a game run or an acceptance of the
actual collision chain. The production edits are asset capacity325→326, player spriteSheet8 TILE103→slot325
with the existing default anchor(0,0), and the exact HD_REGION_CAPACITY65536 array declaration.
No weapon, motion, origin compensation, child, trail, shadow, enemy or timing
code changes. Parent103 uses the ordinary physical-object alpha/shadow route;
it is not added to the green-head layer or the green shadow exception.

## Run

Requires Python3, Pillow and a C99 compiler. No network or original game data.
First use build-poison-parent-art.py to produce a new external rebuild directory;
pass that directory as --art, since the committed source folder intentionally
does not duplicate its generated runtime/output files.

```sh
python prototype/fixtures/test-poison-parent103.py \
  --source /path/to/candidate-source \
  --art /path/to/poison-parent103-v1 \
  --assets /path/to/candidate-pack334 \
  --baseline-assets /path/to/missing-parent-only333 \
  --sanitize --mutations --report /path/to/poison-parent103-result.json
```

The baseline pack must contain the333 unchanged assets from603176dbce9f2aacde93503028d309321009c029
and physically omit bullet-103-8.hda. The candidate adds exactly that one file.
The baseline argument remains a pinned parent-missing pack after production
integration; do not point it at a pack that now contains103.

The art input requires only candidate-manifest.json, the selected generated
master, exported RGBA PNG and HDA named in that manifest. No reference/, original
indexed pixels, source-table dumps, game binary or capture is required or copied
into these formal tests. Source and333 prior HDA hashes are frozen in
poison-parent103-contract.json. The approved parent HDA hash is independently
pinned as9e325d7cd9cc4e90c943ef921b9e80858dbcce926d124e4ce3ab8834b44c2ccb.

The107-file source-scope oracle allows only those three exact renderer edits.
Reversing them must recreate the baseline renderer bytes exactly. The65536-region
guard, overflow fail-closed behavior and frame reset are unchanged; the separate
test-hd-region-budget suite stresses the new bound. Private FIFO
capture hooks are not allowed in this production-scope test.

## Coverage

- Independent expected registry for six bank identities, three layouts and
  IDs0–599. All old slots and ID59(-1,0) remain fixed;103 cannot alias another bank.
- Actual approved master→crop→resize→placement RGBA reconstruction; exact PNG,
  RGBA and HDA hashes; header80103/8/12/14/0/0; all333 prior HDA files unchanged.
- Each of six wrong header words, wrong magic, short/trailing payload, actual
  missing file, explicit missing/invalid/1x gates, and8→4 authored fallback.
- Ordinary alpha and shadow math against independent per-channel oracles at
  output2x/4x/8x. Actual fractional RGBA plus synthetic alpha0/1/17/63/127/128/191/254/255,
  normal/clipped placement, padded pitch and ownership metadata.
- Existing59 and Pulse bindings; bank8:83 still unbound while explosion83 keeps
  slot180; enemy-shot route remains112/113 only, with positive actual controls.
- Physically missing103 alone, with both global missing/invalid flags false:
 103 falls back, then existing59/Pulse, all children214–217, all trail78–84
  (NORMAL and BLEND), and enemy112/113 still draw. Green shadow exceptions remain.

Thirteen mutations must reach an oracle failure: capacity, omitted binding,
wrong ID/bank/layout/slot/anchor, expanded enemy gate, opaque alpha, wrong shadow
alpha, expanded green-head scope, parent shadow bypass, and missing103 disabling
its descendants. No blanket renderer disable is used. The finite lookup sweep
uses the actual invalid flag solely to inspect slot initialization; positive
loads, pixel tests and parent-missing tests use normal renderer behavior.

All production helpers are extracted unmodified. The only harness shims are
the external trace callback and unsupported-reason recorder. ASan/UBSan are
available with --sanitize; only LeakSanitizer is disabled for executor ptrace.
Temporary synthetic files are retained and reported.

No runtime visibility, collision→shot71→child214–217→trail78–84 observation,
full gameplay parity, Windows acceptance or publication is claimed by this test.
