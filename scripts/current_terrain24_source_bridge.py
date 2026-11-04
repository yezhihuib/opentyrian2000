"""Strict private terrain24 epoch; old alias policy is not current source identity.

Validate actual339 files and actual new binding, then project exact bytes to the
fixed335 TOPCLIP authority in memory. Never fabricate an old receipt, change old
source-mode permissions, or exempt any old package payload from its validators.
"""
import copy
from pathlib import Path

import current_tank194_body_registration as checked
import current_terrain24_registration as terrain
from verify_current_production import source_inventory, source_manifest_digest, verify

CURRENT_DIGEST = '90ba617c3827677b5d550e407791819e288765f649691a0626d30caff2d37541'
TOPCLIP_DIGEST = '48411cd0be1e370a19a09e7711b868e854a7c6338733932356d3695cd31aa6f9'
BINDING = 'packaging/current-production-validation.json'
BINDING_DESTINATION = 'CURRENT-PRODUCTION-VALIDATION.json'
ROOT_MARKERS = ('src/private_static340.inc', terrain.PROOF)


def requires_terrain(root, manifest=None, current=None):
    """Include actual-root markers so metadata stripping cannot downgrade339."""
    root = Path(root)
    if any((root / name).exists() or (root / name).is_symlink() for name in ROOT_MARKERS):
        return True
    if terrain.epoch_marked_rows(manifest):
        return True
    revision = manifest.get('source_revision', {}) if type(manifest) is dict else {}
    if type(revision) is dict and revision.get('current_production_source_manifest_sha256') == CURRENT_DIGEST:
        return True
    return (type(current) is dict and
            (current.get('production_source_manifest_sha256') == CURRENT_DIGEST or
             'terrain24_binding' in current))


def _project_sources(proof, raw):
    """Exact position/context inverse over an already authenticated byte map."""
    inverse = proof['inverse']
    core = 'src/render_mirror.c'
    if checked.sha(raw[core]) != inverse['planned_renderer_sha256']:
        raise ValueError('Changed terrain24 renderer before projection')
    original = raw[core].decode('utf-8').splitlines(keepends=True)
    edits = inverse['inverse_hunks']
    if type(edits) is not list or len(edits) != 8:
        raise ValueError('Expected 8 exact terrain24 inverse hunks')
    previous_end = 0
    for edit in edits:
        start = edit['start_line_zero_based']
        count = len(edit['candidate'].splitlines(keepends=True))
        if type(start) is not int or count < 1 or start < previous_end:
            raise ValueError('Duplicate, unordered or overlapping terrain24 inverse')
        previous_end = start + count
    for edit in edits:
        start = edit['start_line_zero_based']
        count = len(edit['candidate'].splitlines(keepends=True))
        if (type(start) is not int or start < 0 or
                ''.join(original[start:start + count]) != edit['candidate'] or
                ''.join(original[max(0, start - 3):start]) != edit['context_before'] or
                ''.join(original[start + count:start + count + 3]) != edit['context_after']):
            raise ValueError('Changed terrain24 inverse position/context')
        if edit['candidate'].strip() and ''.join(original).count(edit['candidate']) != 1:
            raise ValueError('Nonunique terrain24 inverse')
    lines = original[:]
    for edit in reversed(edits):
        start = edit['start_line_zero_based']
        count = len(edit['candidate'].splitlines(keepends=True))
        lines[start:start + count] = edit['public'].splitlines(keepends=True)
    projected_raw = dict(raw)
    projected_raw[core] = ''.join(lines).encode('utf-8')
    if checked.sha(projected_raw[core]) != inverse['public_renderer_sha256']:
        raise ValueError('Unrelated renderer change in terrain24 projection')
    for name, digest in proof['include_sha256'].items():
        if checked.sha(projected_raw.get(name, b'')) != digest:
            raise ValueError('Changed projected terrain24 include')
        del projected_raw[name]
    projected = {name: checked.sha(data) for name, data in projected_raw.items()}
    if (len(projected) != 335 or projected != proof['projected_source_sha256'] or
            source_manifest_digest(projected) != TOPCLIP_DIGEST):
        raise ValueError('Unreviewed terrain24 projected335 source')
    return projected


def verify_source_epoch(root):
    root = Path(root)
    proof = terrain.authority(root)
    actual = source_inventory(root)
    if (len(actual) != 339 or actual != proof['source_sha256'] or
            source_manifest_digest(actual) != CURRENT_DIGEST):
        raise ValueError('Unreviewed terrain24 actual339 source epoch')
    pin = proof['current_receipt']
    receipt_raw = checked.regular(root, BINDING, 2 * 1024 * 1024)
    if (len(receipt_raw) != pin['bytes'] or checked.sha(receipt_raw) != pin['sha256'] or
            checked.blob(receipt_raw) != pin['git_blob']):
        raise ValueError('Changed terrain24 actual current receipt')
    receipt = checked.object_bytes(receipt_raw)
    if (receipt.get('production_source_manifest_sha256') != CURRENT_DIGEST or
            receipt.get('source_sha256') != actual or
            receipt.get('build_input_sha256') != proof['source_build_input_sha256'] or
            receipt.get('historical_validation_sha256') != proof['historical_validation_sha256'] or
            receipt.get('production_commit') is not None):
        raise ValueError('Changed terrain24 source binding')
    for name, digest in {**proof['source_build_input_sha256'],
                         **proof['historical_validation_sha256']}.items():
        if checked.sha(checked.regular(root, name, 4 * 1024 * 1024)) != digest:
            raise ValueError('Changed terrain24 external source input: ' + name)
    verify(root, receipt)
    raw = {name: checked.regular(root, name, 4 * 1024 * 1024) for name in actual}
    if any(checked.sha(raw[name]) != digest for name, digest in actual.items()):
        raise ValueError('Terrain24 source changed during validation')
    _project_sources(proof, raw)
    return {'status': 'PASS', 'scope': 'exact source binding and finite ancestry only',
            'actual_source_manifest_sha256': CURRENT_DIGEST, 'source_files': 339,
            'projected_body_policy_epoch': TOPCLIP_DIGEST,
            'full_package_acceptance': False}


def validate_runtime_rows(root, manifest, required=False):
    if not required and not requires_terrain(root, manifest):
        return None
    epoch = verify_source_epoch(root)
    proof = terrain.authority(root)
    if type(manifest) is not dict or manifest.get('schema') != 'opentyrian-runtime-package-v1':
        raise ValueError('Expected terrain24 runtime manifest')
    rows = manifest.get('files')
    if type(rows) is not list or len(rows) != 1163 or any(type(row) is not dict for row in rows):
        raise ValueError('Expected exact1163 terrain24 rows')
    metadata = {key: value for key, value in manifest.items() if key != 'files'}
    # Canonical JSON retains JSON types: Python equality alone accepts True == 1.
    if source_manifest_digest(metadata) != source_manifest_digest(proof['candidate_metadata']):
        raise ValueError('Changed terrain24 runtime metadata/closure')
    destinations = set()
    for row in rows:
        # Existing pinned rows legitimately reuse a source at different destinations.
        # Exact old-row digest below preserves those aliases, never a generic waiver.
        checked.relative(row.get('source_path'))
        value = row.get('destination')
        checked.relative(value)
        folded = value.casefold()
        if folded in destinations:
            raise ValueError('Duplicate terrain24 runtime destination')
        destinations.add(folded)
        if type(row.get('bytes')) is not int or row['bytes'] < 0:
            raise ValueError('Invalid terrain24 runtime size')
    selected_binding = [row for row in rows if any(
        isinstance(row.get(key), str) and row[key].casefold() == value.casefold()
        for key, value in (('source_path', BINDING), ('destination', BINDING_DESTINATION),
                           ('group', 'current-production-validation')))]
    if len(selected_binding) != 1:
        raise ValueError('Expected unique actual terrain24 binding row')
    binding = selected_binding[0]
    raw = checked.regular(root, BINDING, 2 * 1024 * 1024)
    expected_binding = dict(source_path=BINDING, destination=BINDING_DESTINATION,
                            group='current-production-validation', revision='reconstructed-local-unpublished',
                            bytes=len(raw),
                            sha256=checked.sha(raw), git_blob=checked.blob(raw))
    if binding != expected_binding:
        raise ValueError('Changed actual terrain24 binding row')
    terrain.validate_runtime_rows(root, manifest, required=True)
    expected_new = proof['rows']
    fixed = sorted([row for row in rows if row is not binding and row not in expected_new],
                   key=lambda row: row['destination'])
    if (len(fixed) != 1138 or
            source_manifest_digest(fixed) != proof['base_nonbinding_rows_sha256']):
        raise ValueError('Changed old1138 nonbinding runtime rows')
    previous = sorted([row for row in rows if row is not binding and
                       row.get('destination') != 'assets/gameplay/terrain-shapesz-340-8.hda'],
                      key=lambda row: row['destination'])
    predecessor = proof['predecessor23']
    if (len(previous) != 1161 or
            source_manifest_digest(previous) != predecessor['nonbinding_rows_sha256']):
        raise ValueError('Changed original1161 terrain23 nonbinding rows')
    return dict(epoch, scope='exact source,1163 metadata and24 actual HDA only',
                runtime_rows=1163, old_nonbinding_rows=1138, terrain_payloads=24,
                old_payloads_revalidated=False)
