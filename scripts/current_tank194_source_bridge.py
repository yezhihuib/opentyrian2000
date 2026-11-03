"""One explicit body194 source/runtime epoch, never a generic fallback.

All authority is finite public code, hashes and two existing HDR1 materials.
No original game data, private receipts, artwork decoding or writes are used.
"""
import copy
from pathlib import Path

from verify_current_production import source_inventory, source_manifest_digest, verify as verify_binding
import current_tank194_body_registration as body

MODE = 'current-tank-energy-body194-v1'
PROOF = 'packaging/tank194-authoring-epoch-v1.json'
PROOF_SHA256 = '36643ec06cf9db739a5e5403b0949e5a4bea190c7c47265976237c0a8bbfe5b2'
BINDING = 'packaging/current-production-validation.json'
RUNTIME = 'packaging/runtime-assets-v1.json'
HEADER = 'src/current_tank_shell_payload_pins.h'
CURRENT_DIGEST = 'a656cba2dc28926be07507117d3c108e486c9cdf8495151a6dd32cf9cfd46d3a'
PUBLIC_DIGEST = 'c7a9aef504a5df334a179ba3591042e4c2a805d70e521fb6a775d3a5403015d0'
PUBLIC_NONHEADER_DIGEST = 'd25f72a41559656771d0ebf29439eb8e232cc799a70ecd65e44ebfb57f1e3384'


def proof(root):
    raw = body.regular(root, PROOF, 2 * 1024 * 1024)
    if body.sha(raw) != PROOF_SHA256:
        raise ValueError('Unreviewed body194 authoring epoch proof')
    return body.object_bytes(raw)


def input_paths(root):
    """Finite additional read inputs for the existing Tank staging closure."""
    proof(root)
    p, _ = body.authority(root)
    return {PROOF, body.PROOF} | {r['path'] for r in p['public_sources'].values()} | {
        r['manual_row']['source_path'] for r in p['resources']}


def project_sources(root):
    """Return exact public329 inventory and its 18 restored byte strings.

    Every actual current331 byte string is checked before any file is removed
    from the projected inventory. The two new files are never silently omitted.
    """
    p = proof(root)
    actual = source_inventory(Path(root))
    if (len(actual) != 331 or actual != p['source_sha256'] or
            source_manifest_digest(actual) != CURRENT_DIGEST):
        raise ValueError('Unreviewed body194 production epoch')
    result = dict(actual)
    restored = {}
    for name, pin in sorted(actual.items()):
        raw = body.regular(root, name, 4 * 1024 * 1024)
        if body.sha(raw) != pin:
            raise ValueError('Changed body194 source bytes: ' + name)
        if name in p['new_source_sha256']:
            if pin != p['new_source_sha256'][name]:
                raise ValueError('Changed new body194 source: ' + name)
            del result[name]
        elif name in p['changed_sources']:
            entry = p['changed_sources'][name]
            if pin != entry['current_sha256']:
                raise ValueError('Changed registered body194 source: ' + name)
            lines = raw.decode('utf-8').splitlines(keepends=True)
            for hunk in reversed(entry['inverse']):
                start = hunk['start_line']
                current = hunk['current'].splitlines(keepends=True)
                if lines[start:start + len(current)] != current:
                    raise ValueError('Missing exact body194 inverse: ' + name)
                lines[start:start + len(current)] = hunk['public'].splitlines(keepends=True)
            old = ''.join(lines).encode('utf-8')
            if body.sha(old) != entry['public_sha256'] or body.blob(old) != entry['public_git_blob']:
                raise ValueError('Unrelated projected body194 edit: ' + name)
            restored[name] = old
            result[name] = body.sha(old)
    if (len(restored) != 18 or len(result) != 329 or result != p['public_source_sha256'] or
            source_manifest_digest(result) != PUBLIC_DIGEST):
        raise ValueError('Unreviewed body194 projected source epoch')
    return result, restored


def project_runtime_rows(root, manifest):
    """Validate actual body materials/binding, then remove only two exact rows.

    The remaining 1130 nonbinding rows must equal the fixed public1131 epoch.
    The current binding stays current; this function never fabricates an older
    receipt, rewrites the manifest, or exempts unrelated asset byte validation.
    """
    p = proof(root)
    if type(manifest) is not dict or manifest.get('schema') != 'opentyrian-runtime-package-v1':
        raise ValueError('Expected current body194 runtime manifest')
    rows = manifest.get('files')
    if type(rows) is not list or len(rows) != 1133 or any(type(r) is not dict for r in rows):
        raise ValueError('Unreviewed body194 runtime row count')
    body.validate_runtime_rows(root, manifest, required=True)
    selected = [r for r in rows if r.get('revision') == body.REVISION]
    if sorted(selected, key=lambda r: r['destination']) != p['body_alias_rows']:
        raise ValueError('Unreviewed body194 alias rows')
    binding = [r for r in rows if any(
        isinstance(r.get(k), str) and r[k].casefold() == value.casefold()
        for k, value in (('source_path', BINDING), ('destination', 'CURRENT-PRODUCTION-VALIDATION.json'),
                         ('group', 'current-production-validation')))]
    if len(binding) != 1:
        raise ValueError('Expected exactly one current body194 binding row')
    row = binding[0]
    raw = body.regular(root, BINDING, 2 * 1024 * 1024)
    receipt = body.object_bytes(raw)
    revision = manifest.get('source_revision')
    if (row.get('source_path') != BINDING or row.get('destination') != 'CURRENT-PRODUCTION-VALIDATION.json' or
            row.get('group') != 'current-production-validation' or type(row.get('bytes')) is not int or
            row['bytes'] != len(raw) or row.get('sha256') != body.sha(raw) or row.get('git_blob') != body.blob(raw) or
            type(revision) is not dict or revision.get('current_production_source_manifest_sha256') != CURRENT_DIGEST or
            receipt.get('production_source_manifest_sha256') != CURRENT_DIGEST or
            receipt.get('source_sha256') != p['source_sha256']):
        raise ValueError('Changed current body194 raw source binding')
    verify_binding(Path(root), receipt)
    projected = [copy.deepcopy(r) for r in rows if r not in selected]
    fixed = [r for r in projected if r['source_path'] != BINDING]
    if (len(projected) != 1131 or len(fixed) != 1130 or
            source_manifest_digest(fixed) != p['projected_nonbinding_rows_sha256']):
        raise ValueError('Unrelated runtime row changed')
    return projected
