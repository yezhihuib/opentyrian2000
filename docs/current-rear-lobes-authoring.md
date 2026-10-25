# Current Rear lobe shared authoring

This closes duplicated authoring sources; it is not new art or expanded gameplay. Two **independent** JSON masters produce eight approved transports at d4/d8:

- `authoring-inputs/rear-lobes-current/master-203.json`: inner and outer upper lobes plus their vector full-canvas vertical reflections produce the four-head raw203. Raw222 reflects the finished RGBA canvas horizontally.
- `authoring-inputs/rear-lobes-current/master-43.json`: approved A2 outer and shoulder lobes plus their vertical reflections, then the central lobe **once, last**, produce the five-head raw43. Raw5 reflects the finished RGBA canvas horizontally.

These shapes do not share a geometry master. They share only a fixed coverage/profile compiler. Change the appropriate JSON master, update its SHA256 in a candidate copy of `assets/hd/authoring/rear-lobes-current.json`, set schema `opentyrian-current-rear-lobes-candidate-v1`, and omit installed `resources`. Both master identities must remain present and ordered. Use `scripts/build_current_rear_lobes.py stage --root ROOT --selection CANDIDATE --stage NEW_EXTERNAL_DIR`, review the plan, then `apply --root ROOT --stage DIR` and `check --root ROOT`.

The candidate rebuilds all eight transport outputs and composes their pins with independently verified P7, Rear39, Rear1 and Rear281 families. A genuine single-master edit affects four payloads, not the other master. The only permitted flat header payload cells are42–49; source indices and payload indices are not interchangeable. The other forty Rear outputs, unsupported zero cells18/20, original source/record predicates and draw eligibility remain fixed. Historical182/183 are frozen d8 snapshots of older Front art, not links to current Front masters.

The fixed 32-stroke inward coverage renderer validates finite data-only geometry, full control-point bounds, known path grammar, exact lobe identity/order, gradient fields, fixed12×14 canvas and occupied clipping. d4 and d8 render separately. It preserves canonical historical SVG bytes, uses the admitted Linux Node24.22.1/full Sharp0.35.5 profile, and requires fresh SVG/PNG/RGBA goldens. No arbitrary SVG, executable source or new Pillow dependency is introduced. Old Node24.19 strict rebuilds are not claimed to pass.

Stage binds a finite dependency inventory and writes externally. Apply rederives, rejects stale sources or staged-byte tampering, preflights the plan and rolls back handled replacement failures. It does not promise power-loss/crash atomicity or concurrent-writer isolation. Runtime export remains1029 files; previews explicitly register232 current outputs. Asset-only Linux/Windows package equality does not constitute Windows execution or campaign testing.

Receipts distinguish bootstrap, independent source/runtime audit, compiler review, real transactions, native probes and historical contexts. Qualification must be complete before publication; this document alone is not a release verdict.
