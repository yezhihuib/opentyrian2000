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
    return _project_sources(proof(root), source_inventory(Path(root)),
                            lambda name: body.regular(root, name, 4 * 1024 * 1024))


def _project_sources(p, actual, read_source):
    if (len(actual) != 331 or actual != p['source_sha256'] or
            source_manifest_digest(actual) != CURRENT_DIGEST):
        raise ValueError('Unreviewed body194 production epoch')
    result = dict(actual)
    restored = {}
    for name, pin in sorted(actual.items()):
        raw = read_source(name)
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
    return _project_runtime_rows(root, manifest, p, CURRENT_DIGEST, 1133,
                                 (body.REVISION,), (body.validate_runtime_rows,))


def _project_runtime_rows(root, manifest, p, current_digest, count, revisions, validators):
    if type(manifest) is not dict or manifest.get('schema') != 'opentyrian-runtime-package-v1':
        raise ValueError('Expected current body194 runtime manifest')
    rows = manifest.get('files')
    if type(rows) is not list or len(rows) != count or any(type(r) is not dict for r in rows):
        raise ValueError('Unreviewed body194 runtime row count')
    for validate in validators:
        validate(root, manifest, required=True)
    selected = [r for r in rows if r.get('revision') in revisions]
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
            type(revision) is not dict or revision.get('current_production_source_manifest_sha256') != current_digest or
            receipt.get('production_source_manifest_sha256') != current_digest or
            receipt.get('source_sha256') != p['source_sha256']):
        raise ValueError('Changed current body194 raw source binding')
    verify_binding(Path(root), receipt)
    projected = [copy.deepcopy(r) for r in rows if r not in selected]
    fixed = [r for r in projected if r['source_path'] != BINDING]
    if (len(projected) != 1131 or len(fixed) != 1130 or
            source_manifest_digest(fixed) != p['projected_nonbinding_rows_sha256']):
        raise ValueError('Unrelated runtime row changed')
    return projected


# A second named epoch, never selected by a failed v1 check.
EXTRA_MODE = 'current-tank-energy-body194-extra-poses-v1'
EXTRA_PROOF = 'packaging/tank194-authoring-extra-poses-epoch-v1.json'
EXTRA_PROOF_SHA256 = 'cb71001937265c24710218612d7dea359f29a97374c2b81b58f945f4b67ae51e'
EXTRA_CURRENT_DIGEST = '155c01a82f047251a49b358aa9cbbfde9abc2bb3695d29e98a744e90cc777aa8'


def extra_proof(root):
    raw = body.regular(root, EXTRA_PROOF, 2 * 1024 * 1024)
    if body.sha(raw) != EXTRA_PROOF_SHA256:
        raise ValueError('Unreviewed extra-pose authoring epoch proof')
    p = body.object_bytes(raw)
    if p['previous_proof_path'] != PROOF or p['previous_proof_sha256'] != PROOF_SHA256:
        raise ValueError('Changed previous body194 authority')
    proof(root)
    return p


def extra_input_paths(root):
    import current_tank194_extra_registration as extra
    extra_proof(root)
    return input_paths(root) | set(extra.input_paths(root)) | {EXTRA_PROOF}


def project_extra_sources(root):
    return _project_extra_sources(root, extra_proof(root), source_inventory(Path(root)),
                                  lambda name: body.regular(root, name, 4 * 1024 * 1024))


def _project_extra_sources(root, p, actual, read_source):
    if (len(actual) != 332 or actual != p['source_sha256'] or
            source_manifest_digest(actual) != EXTRA_CURRENT_DIGEST):
        raise ValueError('Unreviewed extra-pose production epoch')
    raw = {name: read_source(name) for name in actual}
    if any(body.sha(raw[name]) != pin for name, pin in actual.items()):
        raise ValueError('Changed extra-pose source bytes')
    inverse = p['core_inverse']
    core = p['core_path']
    if body.sha(raw[core]) != inverse['candidate_sha256']:
        raise ValueError('Changed extra-pose core')
    text = raw[core].decode('utf-8')
    for edit in reversed(inverse['edits']):
        if edit['count'] != 1 or text.count(edit['after']) != 1:
            raise ValueError('Missing unique extra-pose core inverse')
        text = text.replace(edit['after'], edit['before'], 1)
    raw[core] = text.encode('utf-8')
    if body.sha(raw[core]) != inverse['base_sha256']:
        raise ValueError('Unrelated extra-pose core change')
    header = p['extra_header_path']
    if body.sha(raw[header]) != p['extra_header_sha256']:
        raise ValueError('Changed extra-pose header before removal')
    del raw[header]
    previous = {name: body.sha(data) for name, data in raw.items()}
    if source_manifest_digest(previous) != CURRENT_DIGEST:
        raise ValueError('Unreviewed previous331 projection')
    return _project_sources(proof(root), previous, raw.__getitem__)


def project_extra_runtime_rows(root, manifest):
    import current_tank194_extra_registration as extra
    p = extra_proof(root)
    closure = manifest.get('closure', {}) if type(manifest) is dict else {}
    if (type(closure) is not dict or type(closure.get('global_tank194_body_alias_files')) is not int or
            closure['global_tank194_body_alias_files'] != 4 or
            type(closure.get('global_content_hda_files')) is not int or closure['global_content_hda_files'] != 137):
        raise ValueError('Expected exact four-body-alias closure')
    return _project_runtime_rows(root, manifest, p, EXTRA_CURRENT_DIGEST, 1135,
                                 (body.REVISION, extra.REVISION),
                                 (body.validate_runtime_rows, extra.validate_runtime_rows))


# A third named epoch; the two earlier public modes remain exact and separate.
POSES15_17_MODE = 'current-tank-energy-body194-poses15-17-v1'
POSES15_17_PROOF = 'packaging/tank194-authoring-poses15-17-epoch-v1.json'
POSES15_17_PROOF_SHA256 = 'f147a0c73c3d20d8d83e44ceb0bfa899c3fe7c9a3bb3da28e873da1b5ab0ab3e'
POSES15_17_CURRENT_DIGEST = '4fc438e1a4431c2ebfe57e94e13dc9453e0708959b485466fa3b7c1c79d8ea12'


def poses15_17_proof(root):
    raw = body.regular(root, POSES15_17_PROOF, 2 * 1024 * 1024)
    if body.sha(raw) != POSES15_17_PROOF_SHA256:
        raise ValueError('Unreviewed poses15/17 authoring epoch proof')
    p = body.object_bytes(raw)
    if p['previous_proof_path'] != EXTRA_PROOF or p['previous_proof_sha256'] != EXTRA_PROOF_SHA256:
        raise ValueError('Changed previous extra-pose authority')
    extra_proof(root)
    return p


def poses15_17_input_paths(root):
    import current_tank194_poses15_17_registration as pair
    poses15_17_proof(root)
    return extra_input_paths(root) | set(pair.input_paths(root)) | {POSES15_17_PROOF}


def project_poses15_17_sources(root):
    return _project_poses15_17_sources(root, poses15_17_proof(root), source_inventory(Path(root)),
                                      lambda name: body.regular(root, name, 4 * 1024 * 1024))


def _project_poses15_17_sources(root, p, actual, read_source):
    if (len(actual) != 333 or actual != p['source_sha256'] or
            source_manifest_digest(actual) != POSES15_17_CURRENT_DIGEST):
        raise ValueError('Unreviewed poses15/17 production epoch')
    raw = {name: read_source(name) for name in actual}
    if any(body.sha(raw[name]) != pin for name, pin in actual.items()):
        raise ValueError('Changed poses15/17 source bytes')
    inverse = p['core_inverse']
    core = p['core_path']
    if body.sha(raw[core]) != inverse['candidate_sha256']:
        raise ValueError('Changed poses15/17 core')
    text = raw[core].decode('utf-8')
    for edit in reversed(inverse['edits']):
        if edit['count'] != 1 or text.count(edit['after']) != 1:
            raise ValueError('Missing unique poses15/17 core inverse')
        text = text.replace(edit['after'], edit['before'], 1)
    raw[core] = text.encode('utf-8')
    if body.sha(raw[core]) != inverse['base_sha256']:
        raise ValueError('Unrelated poses15/17 core change')
    header = p['extra_header_path']
    if body.sha(raw[header]) != p['extra_header_sha256']:
        raise ValueError('Changed poses15/17 header before removal')
    del raw[header]
    previous = {name: body.sha(data) for name, data in raw.items()}
    if source_manifest_digest(previous) != EXTRA_CURRENT_DIGEST:
        raise ValueError('Unreviewed previous332 projection')
    return _project_extra_sources(root, extra_proof(root), previous, raw.__getitem__)


def project_poses15_17_runtime_rows(root, manifest):
    import current_tank194_extra_registration as extra
    import current_tank194_poses15_17_registration as pair
    p = poses15_17_proof(root)
    closure = manifest.get('closure', {}) if type(manifest) is dict else {}
    if (type(closure) is not dict or type(closure.get('global_tank194_body_alias_files')) is not int or
            closure['global_tank194_body_alias_files'] != 6 or
            type(closure.get('global_content_hda_files')) is not int or closure['global_content_hda_files'] != 139):
        raise ValueError('Expected exact six-body-alias closure')
    return _project_runtime_rows(root, manifest, p, POSES15_17_CURRENT_DIGEST, 1137,
                                 (body.REVISION, extra.REVISION, pair.REVISION),
                                 (body.validate_runtime_rows, extra.validate_runtime_rows, pair.validate_runtime_rows))


# A fourth named epoch, dependent on the exact unpublished333 source tree.
POSE89_MODE = 'current-tank-energy-body194-pose89-v1'
POSE89_PROOF = 'packaging/tank194-authoring-pose89-epoch-v1.json'
POSE89_PROOF_SHA256 = '0a85d3e6496433358dca5c6e048af31d06c99e47119a10b267216a6dd38884ab'
POSE89_CURRENT_DIGEST = '66d84b7ab6fc4fce626db07ac4833891d42e5643e4f06fac20b99f66d6081b6e'


def pose89_proof(root):
    raw = body.regular(root, POSE89_PROOF, 2 * 1024 * 1024)
    if body.sha(raw) != POSE89_PROOF_SHA256:
        raise ValueError('Unreviewed pose89 authoring epoch proof')
    p = body.object_bytes(raw)
    if p['previous_proof_path'] != POSES15_17_PROOF or p['previous_proof_sha256'] != POSES15_17_PROOF_SHA256:
        raise ValueError('Changed previous poses15/17 authority')
    poses15_17_proof(root)
    return p


def pose89_input_paths(root):
    import current_tank194_pose89_registration as single
    pose89_proof(root)
    return poses15_17_input_paths(root) | set(single.input_paths(root)) | {POSE89_PROOF}


def project_pose89_sources(root):
    return _project_pose89_sources(root, pose89_proof(root), source_inventory(Path(root)),
                                  lambda name: body.regular(root, name, 4 * 1024 * 1024))


def _project_pose89_sources(root, p, actual, read_source):
    if (len(actual) != 334 or actual != p['source_sha256'] or
            source_manifest_digest(actual) != POSE89_CURRENT_DIGEST):
        raise ValueError('Unreviewed pose89 production epoch')
    raw = {name: read_source(name) for name in actual}
    if any(body.sha(raw[name]) != pin for name, pin in actual.items()):
        raise ValueError('Changed pose89 source bytes')
    inverse = p['core_inverse']
    core = p['core_path']
    if body.sha(raw[core]) != inverse['candidate_sha256']:
        raise ValueError('Changed pose89 core')
    text = raw[core].decode('utf-8')
    for edit in reversed(inverse['edits']):
        if edit['count'] != 1 or text.count(edit['after']) != 1:
            raise ValueError('Missing unique pose89 core inverse')
        text = text.replace(edit['after'], edit['before'], 1)
    raw[core] = text.encode('utf-8')
    if body.sha(raw[core]) != inverse['base_sha256']:
        raise ValueError('Unrelated pose89 core change')
    header = p['extra_header_path']
    if body.sha(raw[header]) != p['extra_header_sha256']:
        raise ValueError('Changed pose89 header before removal')
    del raw[header]
    previous = {name: body.sha(data) for name, data in raw.items()}
    if source_manifest_digest(previous) != POSES15_17_CURRENT_DIGEST:
        raise ValueError('Unreviewed previous333 projection')
    return _project_poses15_17_sources(root, poses15_17_proof(root), previous, raw.__getitem__)


def project_pose89_runtime_rows(root, manifest):
    import current_tank194_extra_registration as extra
    import current_tank194_poses15_17_registration as pair
    import current_tank194_pose89_registration as single
    p = pose89_proof(root)
    closure = manifest.get('closure', {}) if type(manifest) is dict else {}
    if (type(closure) is not dict or type(closure.get('global_tank194_body_alias_files')) is not int or
            closure['global_tank194_body_alias_files'] != 7 or
            type(closure.get('global_content_hda_files')) is not int or closure['global_content_hda_files'] != 140):
        raise ValueError('Expected exact seven-body-alias closure')
    return _project_runtime_rows(root, manifest, p, POSE89_CURRENT_DIGEST, 1138,
                                 (body.REVISION, extra.REVISION, pair.REVISION, single.REVISION),
                                 (body.validate_runtime_rows, extra.validate_runtime_rows, pair.validate_runtime_rows,
                                  single.validate_runtime_rows))


# Deliberate13 adaptation has its own exact epoch; it is not a native alias.
POSE13_MODE = 'current-tank-energy-body194-pose13-adaptation-v1'
POSE13_PROOF = 'packaging/tank194-authoring-pose13-adaptation-epoch-v1.json'
POSE13_PROOF_SHA256 = 'a05d8f34f181a1fbe5e5736dd2ba44c48f3e98fb2104fbbfdeb8c098d607a243'
POSE13_CURRENT_DIGEST = 'fe9ca37a4c9026b2f5655fe58d7e017f5bbb9deee71f804733af034626639428'


def pose13_proof(root):
    raw = body.regular(root, POSE13_PROOF, 2 * 1024 * 1024)
    if body.sha(raw) != POSE13_PROOF_SHA256:
        raise ValueError('Unreviewed pose13 adaptation authoring epoch proof')
    p = body.object_bytes(raw)
    if p['previous_proof_path'] != POSE89_PROOF or p['previous_proof_sha256'] != POSE89_PROOF_SHA256:
        raise ValueError('Changed previous pose89 authority')
    pose89_proof(root)
    return p


def pose13_input_paths(root):
    import current_tank194_pose13_registration as single
    pose13_proof(root)
    return pose89_input_paths(root) | set(single.input_paths(root)) | {POSE13_PROOF}


def project_pose13_sources(root):
    return _project_pose13_sources(root, pose13_proof(root), source_inventory(Path(root)),
                                  lambda name: body.regular(root, name, 4 * 1024 * 1024))


def _project_pose13_sources(root, p, actual, read_source):
    if (len(actual) != 335 or actual != p['source_sha256'] or
            source_manifest_digest(actual) != POSE13_CURRENT_DIGEST):
        raise ValueError('Unreviewed pose13 production epoch')
    raw = {name: read_source(name) for name in actual}
    if any(body.sha(raw[name]) != pin for name, pin in actual.items()):
        raise ValueError('Changed pose13 source bytes')
    inverse = p['core_inverse']
    core = p['core_path']
    if body.sha(raw[core]) != inverse['candidate_sha256']:
        raise ValueError('Changed pose13 core')
    text = raw[core].decode('utf-8')
    for edit in reversed(inverse['edits']):
        if edit['count'] != 1 or text.count(edit['after']) != 1:
            raise ValueError('Missing unique pose13 core inverse')
        text = text.replace(edit['after'], edit['before'], 1)
    raw[core] = text.encode('utf-8')
    if body.sha(raw[core]) != inverse['base_sha256']:
        raise ValueError('Unrelated pose13 core change')
    header = p['extra_header_path']
    if body.sha(raw[header]) != p['extra_header_sha256']:
        raise ValueError('Changed pose13 header before removal')
    del raw[header]
    previous = {name: body.sha(data) for name, data in raw.items()}
    if source_manifest_digest(previous) != POSE89_CURRENT_DIGEST:
        raise ValueError('Unreviewed previous334 projection')
    return _project_pose89_sources(root, pose89_proof(root), previous, raw.__getitem__)


def project_pose13_runtime_rows(root, manifest):
    import current_tank194_extra_registration as extra
    import current_tank194_poses15_17_registration as pair
    import current_tank194_pose89_registration as prior_single
    import current_tank194_pose13_registration as single
    p = pose13_proof(root)
    closure = manifest.get('closure', {}) if type(manifest) is dict else {}
    if (type(closure) is not dict or type(closure.get('global_tank194_body_alias_files')) is not int or
            closure['global_tank194_body_alias_files'] != 8 or
            type(closure.get('global_content_hda_files')) is not int or closure['global_content_hda_files'] != 141):
        raise ValueError('Expected exact eight-body-alias closure')
    return _project_runtime_rows(root, manifest, p, POSE13_CURRENT_DIGEST, 1139,
                                 (body.REVISION, extra.REVISION, pair.REVISION, prior_single.REVISION, single.REVISION),
                                 (body.validate_runtime_rows, extra.validate_runtime_rows, pair.validate_runtime_rows,
                                  prior_single.validate_runtime_rows, single.validate_runtime_rows))


# Top-only clipping is a distinct same-count source epoch, not a material epoch.
TOPCLIP_MODE = 'current-tank-energy-body194-topclip-v1'
TOPCLIP_PROOF = 'packaging/tank194-authoring-topclip-epoch-v1.json'
TOPCLIP_PROOF_SHA256 = 'f643a6fbefaa29c1700873475c1759aa4c8565805e973d9f0c7e488b0bd646a0'
TOPCLIP_CURRENT_DIGEST = '48411cd0be1e370a19a09e7711b868e854a7c6338733932356d3695cd31aa6f9'


def topclip_proof(root):
    raw = body.regular(root, TOPCLIP_PROOF, 2 * 1024 * 1024)
    if body.sha(raw) != TOPCLIP_PROOF_SHA256:
        raise ValueError('Unreviewed topclip authoring epoch proof')
    p = body.object_bytes(raw)
    if p['previous_proof_path'] != POSE13_PROOF or p['previous_proof_sha256'] != POSE13_PROOF_SHA256:
        raise ValueError('Changed previous pose13 authority')
    pose13_proof(root)
    return p


def topclip_input_paths(root):
    topclip_proof(root)
    return pose13_input_paths(root) | {TOPCLIP_PROOF}


def project_topclip_sources(root):
    p = topclip_proof(root)
    actual = source_inventory(Path(root))
    if (len(actual) != 335 or actual != p['source_sha256'] or
            source_manifest_digest(actual) != TOPCLIP_CURRENT_DIGEST):
        raise ValueError('Unreviewed topclip production epoch')
    raw = {name: body.regular(root, name, 4 * 1024 * 1024) for name in actual}
    if any(body.sha(raw[name]) != pin for name, pin in actual.items()):
        raise ValueError('Changed topclip source bytes')
    inverse = p['core_inverse']
    core = p['core_path']
    if body.sha(raw[core]) != inverse['candidate_sha256']:
        raise ValueError('Changed topclip core')
    text = raw[core].decode('utf-8')
    for edit in reversed(inverse['edits']):
        if edit['count'] != 1 or text.count(edit['after']) != 1:
            raise ValueError('Missing unique topclip core inverse')
        text = text.replace(edit['after'], edit['before'], 1)
    raw[core] = text.encode('utf-8')
    if body.sha(raw[core]) != inverse['base_sha256']:
        raise ValueError('Unrelated topclip core change')
    previous = {name: body.sha(data) for name, data in raw.items()}
    if source_manifest_digest(previous) != POSE13_CURRENT_DIGEST:
        raise ValueError('Unreviewed previous335 pose13 projection')
    return _project_pose13_sources(root, pose13_proof(root), previous, raw.__getitem__)


def project_topclip_runtime_rows(root, manifest):
    import current_tank194_extra_registration as extra
    import current_tank194_poses15_17_registration as pair
    import current_tank194_pose89_registration as prior_single
    import current_tank194_pose13_registration as single
    p = topclip_proof(root)
    closure = manifest.get('closure', {}) if type(manifest) is dict else {}
    if (type(closure) is not dict or type(closure.get('global_tank194_body_alias_files')) is not int or
            closure['global_tank194_body_alias_files'] != 8 or
            type(closure.get('global_content_hda_files')) is not int or closure['global_content_hda_files'] != 141):
        raise ValueError('Expected exact eight-body-alias closure')
    return _project_runtime_rows(root, manifest, p, TOPCLIP_CURRENT_DIGEST, 1139,
                                 (body.REVISION, extra.REVISION, pair.REVISION, prior_single.REVISION, single.REVISION),
                                 (body.validate_runtime_rows, extra.validate_runtime_rows, pair.validate_runtime_rows,
                                  prior_single.validate_runtime_rows, single.validate_runtime_rows))
