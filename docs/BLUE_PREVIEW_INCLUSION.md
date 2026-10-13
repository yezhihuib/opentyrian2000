# Include accepted blue-v4 resources in the current HD preview

The current opt-in HD preview now includes the four already accepted blue-v4 resources: enemy-newsh2-85-8.hda, enemy-newsh2-87-8.hda, enemy-newsh2-123-8.hda and enemy-newsh2-125-8.hda. The preview count changes from 476 to 480. Resource bytes and source PNGs are unchanged; the existing debug pack, pack names, launchers and historical rollback packs are preserved.

The generic asset verifier now asserts that these four exact resources remain in both current default packs. There are no renderer or gameplay changes.

Verified against base d01fb20e5eebe805ce2818166dc0d369795b55a6:

- Production build and full resource verification passed: 18 packs, 3,196 HDA entries, 492 exact source PNGs.
- All 487 previously common files are byte-identical; the two current packs now have identical 491-file trees.
- Two actual-preview runs of 880 ticks each preserved identical state, RNG, collision, original shot/control and indexed-output logs. Display RNG changes and coverage mismatches are zero.
- At ticks 872 and 876, only the four accepted blue resources changed from original-pixel fallback to HD mirroring. Native 640×400 SDL readbacks differ by 40 and 1,239 pixels respectively; all remaining pixels are identical.

The selected stills show top-edge ingress, not a complete whole-body art review. They are SDL software-renderer readbacks at native 2x, not physical desktop screenshots. This bounded check does not claim Windows-native, later damage/death, full-level or all-context acceptance.

Exactly four resources, four manifest entries/count and a small verifier guard changed. The private capture observer is excluded from production. The patch was checked forward on the base and in reverse on the candidate. No additional art, resources or gameplay changes are required for this inclusion.
