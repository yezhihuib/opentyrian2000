# Original global-registry history fixtures

These are byte-for-byte `assets/hd/global-assets-v1/registry.json` blobs from the original commits named by each filename. They contain registry metadata only, not game data or image payloads. Original incremental Git bundles recovered the commit/tree/blob objects; extraction used `git show <original-commit>:assets/hd/global-assets-v1/registry.json`. No commit IDs or historical expectations were synthesized or replaced with current HEAD.

`tests/historical_global_fixtures.py` independently pins each original Git blob ID, SHA-256, and byte count. Tests retain their original historical comparisons and approved five-row Pulse projection. The six unchanged Pulse historical receipts are similarly checked against original-object anchors without copying their payloads. Missing, corrupt, edited, or unknown fixtures fail closed. No private Git objects, remote access, or archive credentials are required in a clean checkout.
