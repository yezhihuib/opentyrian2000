# GRAY325 later controlled window (candidate)

This recipe exposes existing GRAY325 unlit content in a later ASTEROID2 window.
It adds no family implementation or artwork. It remains an opt-in **candidate**:
the target-region checks below passed, but the extra whole-frame RGB comparison
failed and retains unexplained differences. Normal gameplay is unverified.

## Fixed inputs and arguments

The reviewed source baseline is
`54d40c6d4b45a6239b19897a1860df08f25c10df`, built as the separate 112-unit
family version with explicit UTF-8 source decoding. The corresponding Windows
candidate executable has SHA-256
`b12f284c5dffe9e3f619bb34fef6e4b1b8169f553eb3a94d7e3b7a5621fc7217`.
It is separate from the ordinary build; no executable or original data is bundled
with this document. See [Windows build staging](WINDOWS-BUILD-STAGE.md).

Use the unchanged 52 public assets listed in
[`assets/hd/level2-family-v1/MANIFEST.json`](../../assets/hd/level2-family-v1/MANIFEST.json)
and only the base 23 values returned by `hd_environment(asset_root)` in
[`scripts/launch_level2_family.py`](../../scripts/launch_level2_family.py).
Verify all 52 manifest hashes. The three existing GRAY325 assets have bases
11 (unlit), 125 (bright), and 277 (dim); their presence does not qualify all three
states. Do not select `--public-candidates`, other extension flags, or redvent.

The game argument recipe is:

```text
--data=<absolute-original-data-directory>
--asset-debug=custom
--asset-debug-episode=1
--asset-debug-level=2
--asset-debug-event=139
--asset-debug-running
--render-ticks=1260
--render-no-capture
```

Event 139 is the one-based origin for type 325 at original level time 1168.
The existing scope checks event array index 138 and the original event identity;
the recipe does not skip simulation or assign an enemy/level state. In the
recorded pair, fast-forward ended at logic tick 1169 with `eventLoc=140`.
`1260` is the **total logical-tick ceiling from the beginning of the controlled
run**, not 1260 additional ticks after reaching the event.

This is an argument specification for a separately reviewed bounded packager,
not a new launcher option. The existing `launch_level2_family.py` does not forward
these debug arguments, runs normal input without a timeout, and rejects Windows
launches; its check-only plan does not prove this recipe is launchable.

## Windows isolation and limits

Allocate a new, initially empty directory for each candidate preview. Refuse an
existing installation/profile or nonempty directory; do not clear it to make it
eligible. After that check, stage the 52 assets at their manifest-relative paths
under this new root, including `assets/hd/current-terrain23` and
`assets/hd/current-terrain24`. Resolve the base 23 asset paths against this root.
Start the child with **this root as its actual CWD**: `TARGET_WIN32` stores native
configuration and saves relative to CWD. APPDATA, USERPROFILE, or HOME redirection
alone does not isolate the native profile. Do not import existing saves/settings.

A fresh `opentyrian.cfg` may request windowed 4x/Integer display. This is a display
setting, not a claim that a native GUI or 4x window has been tested. Original data
remains external and read-only. Remove inherited family/test controls before
supplying exactly the base 23 values; do not mix ordinary-world, startup/menu,
manual-HD, or unsupported extension parameters into this controlled recipe.

The supervising packager must cap each process at 90 seconds and 64 MiB of output
as well as the 1260-tick game limit. These supervisory bounds are not provided by
the argument list alone. Stop on death, failed admission, or budget exhaustion;
retain the outcome without extending or automatically retrying. A forced stop
does not prove cache/ready retirement. P controls debug pause and ESC requests
debug quit; this is not a normal full-level entry or a qualified normal
pause/resume/return-to-title path.

## Bounded evidence and remaining failure

One paired no-window SDL software observation used the same original 112-unit
source/core, with read-only observation wrappers, and left renderer guards and
simulation unchanged. This was not a direct native GUI run of the pinned EXE.
The reviewed final software sample was logic tick 1203, actual Present serial 35
(first Present in that tick), family Present 25: type 325, slot 26, generation 3,
map epoch 58, resource epoch 2, origin event 139, **base 11 unlit only**.

- Independent HDR1 material decoding matched all **43,008 final target pixels**
  with zero mismatches. All 672 predeclared callback-owned logical cells survived
  in this sample; no target occlusion was observed. 42,902 target pixels differed
  from the paired family-off reference.
- At the same tick/Present, native INDEX8 (64,000 bytes), palette (1,024 bytes),
  all recorded state columns for ticks 0 through 1203, and collision records
  matched between the pair. Independent native palette/INDEX8 expansion matched
  the same 43,008 reference target pixels.
- Normal public debug quit cleared observed frame-active/ready, observer, and
  cache state. This only covers that debug exit, not a normal P/ESC/menu lifecycle.

The original extra whole-frame check remains **FAIL**: a Scale2x assumption gave
237,215 mismatches. The controlled path uses density 8 and the family-off path
can use a composed mirror, so that assumption was unsuitable. A subsequent
nearest-8x whole-frame comparison still had **16,730 unexplained differences**
outside the fixed GRAY325 target region. Their cause was not fully attributed;
the target-region pass must not be presented as a whole-frame RGB pass.

Bases 125 and 277, normal level completion, pause/resume, return to title,
re-entry, and native GUI/4x display remain untested. Keep the later-window entry
labelled candidate and separate from existing ordinary and early-preview entries.
