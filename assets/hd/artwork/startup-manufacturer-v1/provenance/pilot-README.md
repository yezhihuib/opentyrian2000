# Manufacturer startup cards: reviewed offline pilot V1

Two bounded manufacturer cards, reviewed by root at native2x and frozen without
further aesthetic revision. These are offline assets, not actual runtime
captures. Original logical registration is320x200 full-screen. Title PIC4,
moving Tyrian/2000 logos and main-menu typography/layout are outside this pilot.

## Identity and artwork

PIC10 preserves the XSIV GAMES cut-geometric letter identities, small TM,
central outlined emblem, narrow white card and black/violet/white burst.
PIC12 preserves the ECLIPSE custom wordmark, metallic figure/hand, eclipse orb,
grid composition and muted gold/gray color roles. No extra wording, branding,
objects or intentional composition change is introduced.

Both complete originals were visually inspected before editing. Built-in
imagegen was used once per card, with each original as its edit target.
`prompts.json` contains the exact requests; `masters/` contains the selected
unmodified generated PNG bytes. Imagegen is not a deterministic regeneration
recipe, so preserve these selected masters as the source of truth.

This is newly reconstructed continuous artwork, not a claim of source-pixel or
vector-outline identity. Root reviewed original/pilot native2x comparisons and
approved the preserved identities and composition. The source geometry and
palette signatures in `source-compatibility.json` are compatibility data, not
claims that the new RGB image uses only the original palette colors.

## Exact registration and sampling

Imagegen returned1586x992 masters. The complete image is fitted to1280x800 with
Pillow LANCZOS, with no crop or translation. That is a documented approximately
0.076 percent aspect correction to the game's exact16:10 frame. The original
XSIV card's bright top-edge span is logical x68..263; the candidate antialiased
span measures x68..262.75. `registration-review.json` records this check.

Canonical density4 is1280x800 opaque RGB. Native2x review is640x400 sampled by
nearest from canonical4x, not independently downsampled from the master.
No transparency/alpha holes are required; a renderer needing RGBA can append
alpha255 to every pixel. Density8 can repeat canonical4x texels2x2. Full original
logical dimensions and placement remain320x200. There is no letterbox, new UI
layout, or gameplay-resolution change.

The exact reviewed PNG/RGB hashes are in `previews/validation.json`. Source
PIC10 uses palette20, decoded indexFNV720d8ce9dda3f5f4 and paletteRGBFNV
b50ac0b9e5f1a73d; PIC12 uses palette22, indexFNV98d7341da720b7ab and paletteRGBFNV
20261a06b61711d5. FullSHA256 values and original file identities are in the
source compatibility metadata.

## Deterministic derivative rebuild

Use CPython3.12 and Pillow12.3.0. `build_previews.py` reads only the selected
masters to reproduce both canonical4x and native2x PNGs, checking all four
frozen output hashes. Use a new external output directory:

```sh
python3 '/path/startup-manufacturer-pilot-v1/build_previews.py' \
  --output '/separate/new-preview-output'
```

Inputs resolve relative to the script, not current working directory. Existing
or inside-source output directories are rejected. Optional `--references`
creates labeled comparisons if the original decoded reference PNGs are supplied
externally; it is not needed for source-to-candidate reconstruction. The compact
archive excludes duplicate full-size original reference PNGs. The supplied
native2x comparisons are labeled offline and remain review-only.

A fresh relocated source-only rebuild without original game files or canonical
candidate inputs reproduces all four output hashes. See `reproduction-proof.json`.

## Future presentation contract

Artwork represents normal unfaded RGB. Preserve the original release startup
sequence, durations, input skip behavior and full-range palette fade timing.
PIC10 follows the original white transition and25-step target-palette fade;
PIC12 follows black and10-step target-palette fade. Both retain the original
200-delay-unit/input wait and10-step fade to black. Do not invent a fixed FPS
conversion or unskippable branding. No fade, gamma or original palette semantics
were implemented or tested by this offline pilot.

Use a separately reviewed, explicit manufacturer-intro context with exact PIC
and palette/source validation; a coincident PIC number or generic image loader
must not activate artwork elsewhere. Existing gameplay probes skip the intro,
so they cannot serve as actual startup validation. Actual release-flow fades,
skip, return/fallback and normal menu/title transitions need their own gate.
Missing/incompatible resources must restore classic presentation coherently.

No runtime resource format, renderer edit, game run or publication is included
here. The integration planner receives the exact frozen files, source identities
and this separation of artwork from future presentation behavior.
