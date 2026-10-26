# Linked NEWSHF 171–173 compatibility boundary

The extension is additive: the original nine NEWSHF transports and their two
historical/generated headers are not repinned. `linked_newshf_projection.py`
checks exact qualified input bytes and independently regenerates the six linked
transports before removing their inventory/runtime entries. It restores only the
two reviewed NEWSHF includes, with exact current-file hashes, bounded inverse
hunks, and public `20f08096b32652b6f3b22a48826f5bcb4ff6f44a` preimage hashes.
Verification uses no Git subprocess or private historical object.

The old builder authority digest remains unchanged. Its authority check applies
the same finite inverse; it does not accept arbitrary new source bytes. Runtime
packaging requires precisely six new destinations with the linked revision and
`newshf-optin` group. Existing nine-resource validation remains separate.

## Qualification status

The production ledger now pins the approved registered final artwork and current
source delta. Native and natural-game acceptance remain separate evidence; the
ledger itself does not imply either. Synthetic tests never qualify production
artwork. The synthetic snapshot's header, art and ledger were not copied into
production.

The final ledger must qualify the two new headers, all registered master and
mask inputs, all six derived PNG/HDA files, selection/mapping, and the bounded
compatibility, builder and immutable-pin-checker scripts. Any source or recipe
change after freezing requires a fresh bounded review and receipt; do not
blindly update historical pins.
