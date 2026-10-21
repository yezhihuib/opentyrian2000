# Verified frontend-only recovery

This update restores the shared HUD, MAIN and pause/settings menus, and shop headings, item names, prices and Cash. It excludes unfinished global aircraft/effect/weapon owners. Existing public aircraft/gameplay behavior remains unchanged.

Menus use DejaVu Sans Condensed Bold with natural advances. Product names and amounts use the approved lighter OSIfont. Original strings, indexed blits, input hitboxes and economy remain original; padding normalization is display-only after source authentication. Logo, prose and Chinese text are unchanged.

RFR3 complete-run resources are explicitly reconstructed, not represented as byte-identical recovered RFR1/RFR2 files. The numeric NFR pack and shared HUD files retain verified original bytes. Font notices and OSIfont corresponding source are included.

See packaging/frontend-validation.json for the exact source hash closure, fresh isolated checks and bounded native evidence. The Linux/software checks do not establish whole-campaign, Windows/GPU or audio-playback acceptance.

Rebuild the runtime allowlist with `python3 scripts/rebuild_recovered_runtime_manifest.py --output packaging/runtime-assets-v1.json`; its pinned public input is retained separately. Then use scripts/package_runtime.py as documented. Original Tyrian data is external and never bundled.
