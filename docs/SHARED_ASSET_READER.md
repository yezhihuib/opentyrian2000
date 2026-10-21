# Shared HDR1 byte reader

This is a behavior-preserving refactor of the accepted green-family base
`76757030842b19397353152c6ea326f95ef50c33`, not another resource eligibility
expansion or storage migration.

`shared_asset_reader.h` contains little-endian HDR1 field decoding, signed
anchor comparison, payload FNV-1a, and the existing global stdio adapter.
`shared_asset_fd_reader.inc` contains the regular-file SHOP fd adapter, using
its caller's existing platform-specific `SF_*` operations. Talon/Pulse/Vulcan
SHOP resource loads share that adapter; every global-family load reaches the
same HDR1 field and payload validation through the global adapter.

## Deliberately preserved policy distinctions

- Global loading still uses `fopen`/`fread`, one header and payload read, and an
  `EOF` sentinel. It does not acquire SHOP's `fstat` regular-file restriction,
  does not add an `ferror` predicate, and ignores close status as before.
- SHOP loading retains nonblocking POSIX or binary/noninheriting Windows open
  flags, exact regular-file length, one header read, a partial-payload read
  loop, and a trailing read that must return zero (not an error).
- SHOP Talon rejects a close error. SHOP Pulse and Vulcan ignore close errors.
  This is an explicit adapter parameter, not an accidental unification.
- Existing caller geometry, resource ID lookup, negative/truncated path rules,
  bank/record/palette checks, attempted/cache flags, same-frame fault latches,
  family-wide failure policies and RGBA allocation ownership are unchanged.
- A decoded payload grants no semantic role, lifetime, contribution ownership,
  render command, palette eligibility or cached frame. Those remain independent
  in each existing owner.

The shared adapters require a non-null resource descriptor already validated by
the existing caller (in particular its byte count and geometry). They are not
an API for arbitrary untrusted descriptors: adding descriptor policy here
would change the existing callers' behavior and is not part of this refactor.

No resource paths, pixels, metadata, registry entries, originals, or duplicate
files are changed or removed. General original-sprite decoding and other file
formats are intentionally outside this extraction.

## Verification

Independent differential loader tests compare the old committed readers with
these adapters using fault-injected IO and real accepted HDR1 assets. Existing
battle-family, shared HUD and SHOP tests remain required. Native baseline versus
candidate comparisons cover battle and SHOP 2x/4x presentation with full,
missing, corrupt and reference resources. Production source binding, a clean
build, deterministic package reconstruction, exact payload hashes and a
relocated Linux startup are checked separately.

These are bounded Linux/software tests, not Windows/GPU, full-campaign or
acoustic validation. No claim is made that file IO failures now have stronger
semantics than the old readers; preserving those semantics is the goal here.

Accepted local evidence for this refactor: differential tests exercised all 120
registry assets in 10,880 cases / 1,237,919 checks; 18 family/UI regression gates
and 40 package tests passed. The bounded native comparison has 16 before/after
pairs (24 new processes, with eight verified preserved battle baselines), 3,704
paired frames, and 2,133,030,064 decompressed capture bytes exactly equal. No
state, indexed buffer, RNG, input, audio-call or owner-log differences occurred.
The 247-source-file binding and 1,007 packaged payloads were verified separately.
