# Actual ASTEROID2 input inventory

Run `python scripts/audit_level2_inventory.py --data-dir /path/to/tyrian2000`.
The command reads original data locally and prints a derived JSON report. It
does not launch the game, edit the data, or publish original event streams,
map cells, lookup arrays, episode text, or sprite pixels. Four SHA-256 pins
reject a different input revision rather than silently auditing another game.

The committed JSON is a snapshot, not a completeness certificate. Regenerate
it after resource or adapter changes. `--require-complete` deliberately exits
1: this inventory cannot certify complete HD runtime presentation.

## Native decoding proof

- `src/tyrian2.c` loads physical level 2 from `lvlPos[2]`. Its event section
  ends at `lvlPos[3]`; its maps start there and end at `lvlPos[4]`. Treating the
  event-section end as the entire level end loses every map.
- `src/helptext.c` decrypts length-prefixed episode lines. Section 6 in
  `levels1.dat` resolves to ASTEROID2, physical level 2. This is checked rather
  than inferred from the filename or “second level” label.
- All 731 events are decoded and the existing full-stream hash is checked.
  There are 199 type-6, 8 type-7, 44 type-10 and 8 type-15 events. The 28
  type-12 events each create four consecutive enemy records. Total: **371
  scripted actor creation attempts**, not 371 guaranteed visible actors.
- All three 128-word map lookup arrays are decoded big-endian, matching the
  native little-endian read followed by `SDL_Swap16`. Every map cell is read:
  4,200 / 8,400 / 9,000. Layer 1 has 63 used shape identities, including blank
  shape 1. Layers 2 and 3 contain only slot 71, which the loader makes NULL.
- `src/episodes.c` reads fixed serialized table sizes, not padded C structs:
  1,638 weapon records of 80 bytes, then item tables, then 1,701 enemy records
  of 77 bytes in the two native index ranges. Damage frames, launch children,
  death/drop descendants, turret special behaviors and projectile animation
  indices are decoded from these records. Turrets 251–255 are behaviors,
  not ordinary weapon-table shots. Graphic 999 is disappearance, not artwork.
- The random table has 33 weighted entries, representing 17 distinct records.
  Repeated entries are retained as weights. Records 317–324 appear three
  times each. Records 135/136, 260/261, 263/265, 266/268 and 462 also occur.

## Reachability versus observation

Each record carries separate scopes: scripted, random candidate, normal
conditional drop, arcade-only event-45 drop, normal random-special drop, and
low-armor conditional supply ship. Closure edges retain their scope. There are
103 distinct records across these scopes and 12 ordinary enemy weapon IDs.

Event 33 appears 32 times; event 45 appears 48 times. Event 45 is mode-gated
and is **not evidence that arcade pickups appear in the ordinary preview**.
Normal drop 533 may randomly become one of 829–834. Low armor can create
560 and drops 561–563. These are conditional inputs, not recorded sightings.
The union is deliberately labeled as including conditional scopes. Arbitrary
player loadouts and SuperTyrian/superArcade remappings are not swept into the
baseline. No inventory entry claims it was observed in a runtime replay.

The scripted launcher 271 recursively reaches 463 (NEWSHD191); scripted 550
reaches 551 (NEWSHD171/190/209). Random 462 uses NEWSHD18/55/93. These are
real input relationships even when a short opening replay never shows them.

## Resource and adapter evidence stay separate

An exact HDA filename with an HDR1 header is only a resource candidate. It
does not prove source identity, correct art, valid full payload, integration,
or runtime admission. `no-valid-exact-per-tile-filename-found` means exactly
that; it does not prove artwork never existed or exclude alternate names.
Projectile filename matches are explicitly candidates needing identity review.

Building records 313–316 use three composed phase canvases under
`assets/hd/level2-family-v1/building/`. The report lists these independently
of per-base HDA lookup. These are NEWSHP **actor assemblies**, not SHAPESZ
terrain tiles; they must not be subtracted from the terrain list. Archived
compound, tall-structure, launcher and firing-rock pin tables are listed as
archived source only, not enabled adapters or packaged resources.

Every adapter status is source evidence, not a complete-rendering claim.
Existing guards may reject late births, damage, clipping, filters, unsupported
poses or missing parent leases. Source SHA-256 values identify the inspected
adapter revision. `runtime_full_coverage` remains false.

### Terrain grouping

- Reviewed per-tile terrain families: ground 367/368/372/376/378/380/386/387/
  388/390; cliff 361/362/363/364/365/371/373/374/375/381/382/383; corner 366;
  static 340. These are 24 identities.
- Red-vent pair: 339/348 has a guarded source adapter that requires an
  external asset directory. The snapshot has no matching packaged filenames.
- Other used nonblank identities without an exact per-tile filename in the
  snapshot: 299/300/306/307/309/310/316/317/318/319/320/328/329/330,
  347/357/358/359/384/385/389/400/410/416/417/418/419/420/421/422/423/424/
  431/432/433/434. These 36 remain unclassified for alternate-art or assembly
  coverage. Numeric adjacency alone is not enough to assign an assembly.
- Blank shape 1 needs no authored replacement. Layer-2/3 NULL cells need no
  tile replacement.

Thus the initial scan has **38 exact-name-unmatched nonblank terrain IDs**,
not a claim that 38 pieces of art are certainly absent in every representation.

## Tests and remaining gates

Run `python -m unittest discover -s tests -p test_level2_inventory.py -v`.
Synthetic tests need no original data. They cover malformed/truncated input,
offset ordering, lookup endian and bounds, all map dimensions, stream/hash
rejection, HDT serialized offsets and holes, script identity, launch-cycle
termination, disabled launch fields and damaged-animation indexing.

Set `TYRIAN_DATA=/path/to/tyrian2000` to run the additional pinned integration
test. The integration check asserts the real identity, counts, blank layers,
launcher descendants and separation of arcade-only records.

This is an exhaustive decode of the pinned level's event/map inputs and a
scoped enemy-table closure. It is not yet an exhaustive native draw inventory:
player loadout, HUD/fonts/warnings, explosions, hit/shield/trail effects and
their visibility/occlusion require separate inventories and runtime evidence.
Final completeness also requires identity-reviewed resource mapping, complete
natural-lifetime integration, boundary tests, and native-state parity.
