"""Single-invocation proof reuse; no persistent cache or filesystem atomicity claim.

Fault injection below is test instrumentation, never the implementation mechanism.
Real-file mutation cases use finite private copies, not the accepted worktree.
"""
import copy
import importlib
import inspect
import io
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import accepted_later_changes as a
import _projection_proof_context as guarded
from _projection_proof_context import _ProjectionProofContext

FAMILIES = ('rear39', 'rear_p7', 'missile', 'mint27', 'newshf', 'guided', 'sonic', 'protron')
EXPECTED = '45ad4ff592f22934c23a4014708ad90fbc01518471144ea47aaef5f820dd583f'
REJECTIONS = (ValueError, AssertionError, RuntimeError, OSError)


def module(family):
    return importlib.import_module('current_' + family + '_compatibility')


def finite_paths(family):
    c = module(family)
    names = c.input_paths(ROOT) | {c.MAPPING, c.HEADER}
    if family == 'protron':
        names |= {c.ROOT + '/' + c.name(*pair) for pair in c.PAIRS}
    if family in ('rear39', 'rear_p7'):
        other = module('rear_p7' if family == 'rear39' else 'rear39')
        names |= other.input_paths(ROOT) | {other.MAPPING, other.HEADER}
    # Source inverse chains are separate from mapping paths; retain their exact
    # files in the private fixture. Module-root ledgers are deliberately NOT copied.
    for value in ('rear_p7', 'missile', 'mint27', 'newshf'):
        names |= set(getattr(a, 'current_' + value + '_ledger')()['files'])
    return names


def copy_inputs(destination, names):
    for name in names:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)


class SingleProofContextUnits(unittest.TestCase):
    """Exercise real closure guards with a cheap, explicitly fake proof producer."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='single-proof-unit-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        copy_inputs(self.root, finite_paths('protron'))
        self.calls = 0

    def validator(self, root):
        self.assertEqual(Path(root), self.root)
        self.calls += 1
        return {'nested': {'items': [1, {'value': 'original'}]}, 'paths': {'x', 'y'}}

    def context(self):
        result = _ProjectionProofContext(self.root, ROOT)
        self.addCleanup(result.close)
        return result

    def test_context_implementation_cannot_claim_other_module_root(self):
        with self.assertRaisesRegex(ValueError, 'context implementation origin mismatch'):
            _ProjectionProofContext(self.root, self.root)

    def test_imported_implementation_origin_is_bound_on_first_use_and_reuse(self):
        for name in ('current_protron_compatibility', 'current_craft267_compatibility',
                     'package_runtime', 'build_current_art'):
            loaded = importlib.import_module(name)
            for reused in (False, True):
                with self.subTest(module=name, reused=reused):
                    context = self.context()
                    if reused:
                        context.get('protron', self.validator)
                    with patch.object(loaded, '__file__', str(self.root / 'other-worktree.py')):
                        with self.assertRaisesRegex(ValueError, 'implementation origin mismatch'):
                            context.get('protron', self.validator)
                    with self.assertRaisesRegex(ValueError, 'closed'):
                        context.get('protron', self.validator)
                    self.context().get('protron', self.validator)

    def test_one_proof_defensive_copy_and_no_reuse_after_close(self):
        context = self.context()
        one = context.get('protron', self.validator)
        one['nested']['items'][1]['value'] = 'contaminated'
        one['paths'].add('injected')
        two = context.get('protron', self.validator)
        self.assertEqual(two['nested']['items'][1]['value'], 'original')
        self.assertEqual(two['paths'], {'x', 'y'})
        self.assertEqual(self.calls, 1)
        context.finish()
        context.close()
        with self.assertRaises(REJECTIONS):
            context.get('protron', self.validator)

    def test_failure_discards_context_and_fresh_retry_works(self):
        context = self.context()
        def fails(root):
            raise ValueError('intentional original-proof failure')
        with self.assertRaisesRegex(ValueError, 'intentional'):
            context.get('protron', fails)
        with self.assertRaises(REJECTIONS):
            context.get('protron', self.validator)
        fresh = self.context()
        self.assertEqual(fresh.get('protron', self.validator)['paths'], {'x', 'y'})
        self.assertEqual(self.calls, 1)

    def test_each_dependency_missing_bytes_mode_rejects_and_restore_is_fresh(self):
        c = module('protron')
        names = (c.SELECTION, c.MAPPING, c.HEADER,
                 c.ROOT + '/' + c.name(*c.PAIRS[0]))
        for name in names:
            target = self.root / name
            raw, mode = target.read_bytes(), stat.S_IMODE(target.stat().st_mode)
            for action in ('missing', 'bytes', 'mode'):
                with self.subTest(name=name, action=action):
                    context = self.context()
                    context.get('protron', self.validator)
                    try:
                        if action == 'missing':
                            target.unlink()
                        elif action == 'bytes':
                            target.write_bytes(raw + b'!')
                        else:
                            target.chmod(mode ^ stat.S_IXUSR)
                        with self.assertRaises(REJECTIONS):
                            context.get('protron', self.validator)
                    finally:
                        target.write_bytes(raw)
                        target.chmod(mode)
                    with self.assertRaises(REJECTIONS):
                        context.get('protron', self.validator)
                    fresh = self.context()
                    fresh.get('protron', self.validator)
                    fresh.finish()

    def test_partial_success_then_failure_invalidates_all_entries(self):
        copy_inputs(self.root, finite_paths('guided'))
        context = self.context()
        context.get('protron', self.validator)
        def fails(root):
            raise ValueError('second-family failure')
        with self.assertRaisesRegex(ValueError, 'second-family'):
            context.get('guided', fails)
        with self.assertRaises(REJECTIONS):
            context.get('protron', self.validator)
        fresh = self.context()
        fresh.get('protron', self.validator)
        fresh.get('guided', self.validator)
        fresh.finish()

    def test_mutation_during_first_derivation_is_not_stored(self):
        context = self.context()
        target = self.root / module('protron').HEADER
        raw = target.read_bytes()
        def mutates(root):
            target.write_bytes(raw + b'!')
            return {'not': 'a stable proof'}
        try:
            with self.assertRaises(REJECTIONS):
                context.get('protron', mutates)
        finally:
            target.write_bytes(raw)
        with self.assertRaises(REJECTIONS):
            context.get('protron', self.validator)
        self.context().get('protron', self.validator)

    def test_relative_traversal_and_nonregular_dependency_are_rejected(self):
        for name in ('../outside', '/absolute', './a', 'a//b', 'a/../b', 'C:/a', 'a\\b'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                guarded._relative(self.root, name)
        target = self.root / module('protron').HEADER
        raw = target.read_bytes()
        target.unlink(); target.mkdir()
        try:
            with self.assertRaises(REJECTIONS):
                self.context().get('protron', self.validator)
        finally:
            target.rmdir(); target.write_bytes(raw)

    def test_external_executable_link_bytes_mode_and_tree_membership(self):
        tools = self.root / 'tool-fixture'
        tools.mkdir()
        executable = tools / 'executable'
        executable.write_bytes(b'fixed executable bytes')
        executable.chmod(0o755)
        link = tools / 'selected'
        link.symlink_to(executable)
        package = tools / 'package'
        package.mkdir(); (package / 'entry').write_bytes(b'package code')
        deps = guarded._Dependencies(external_files=(link,), external_trees=(package,))
        for action in ('bytes', 'mode', 'link', 'new-member', 'delete-member'):
            with self.subTest(action=action):
                context = self.context()
                with patch.object(context, '_discover', return_value=deps):
                    context.get('protron', self.validator)
                try:
                    if action == 'bytes':
                        executable.write_bytes(b'drift')
                    elif action == 'mode':
                        executable.chmod(0o644)
                    elif action == 'link':
                        alternate = tools / 'alternate'
                        alternate.write_bytes(executable.read_bytes()); alternate.chmod(0o755)
                        link.unlink(); link.symlink_to(alternate)
                    elif action == 'new-member':
                        (package / 'unexpected').write_bytes(b'')
                    else:
                        (package / 'entry').unlink()
                    with self.assertRaises(REJECTIONS):
                        context.get('protron', self.validator)
                finally:
                    executable.write_bytes(b'fixed executable bytes'); executable.chmod(0o755)
                    link.unlink(); link.symlink_to(executable)
                    (package / 'unexpected').unlink(missing_ok=True)
                    (package / 'entry').write_bytes(b'package code')

    def test_final_boundary_detects_change_after_last_reuse(self):
        context = self.context()
        context.get('protron', self.validator)
        target = self.root / module('protron').HEADER
        target.write_bytes(target.read_bytes() + b'!')
        with self.assertRaises(REJECTIONS):
            context.finish()

    def test_symlink_leaf_and_parent_rejected_not_followed(self):
        c = module('protron')
        target = self.root / c.SELECTION
        raw = target.read_bytes()
        context = self.context()
        context.get('protron', self.validator)
        target.unlink()
        target.symlink_to(ROOT / c.SELECTION)
        with self.assertRaises(REJECTIONS):
            context.get('protron', self.validator)
        target.unlink(); target.write_bytes(raw)
        context = self.context()
        context.get('protron', self.validator)
        parent = target.parent
        moved = parent.with_name(parent.name + '-real')
        parent.rename(moved)
        parent.symlink_to(moved, target_is_directory=True)
        try:
            with self.assertRaises(REJECTIONS):
                context.get('protron', self.validator)
        finally:
            parent.unlink(); moved.rename(parent)

    def test_symlink_root_is_not_normalized_away(self):
        alias = self.root / 'root-link'
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(REJECTIONS):
            context = _ProjectionProofContext(alias, ROOT)
            try:
                context.get('protron', lambda root: {})
            finally:
                context.close()

    def test_private_caller_root_mismatch_poisons_context(self):
        context = self.context()
        context.get('protron', self.validator)
        with self.assertRaisesRegex(ValueError, 'root mismatch'):
            a._current_projection_proof('protron', ROOT, context)
        with self.assertRaises(REJECTIONS):
            context.get('protron', self.validator)
        fresh = self.context()
        fresh.get('protron', self.validator)
        fresh.finish()

    def test_contexts_are_bound_to_separate_roots(self):
        other = self.root / 'other-root'
        copy_inputs(other, finite_paths('protron'))
        first = self.context()
        second = _ProjectionProofContext(other, ROOT)
        self.addCleanup(second.close)
        self.assertEqual(first.get('protron', lambda root: {'root': str(root)})['root'], str(self.root))
        self.assertEqual(second.get('protron', lambda root: {'root': str(root)})['root'], str(other))
        (other / module('protron').HEADER).write_bytes(b'changed second root')
        first.finish()
        with self.assertRaises(REJECTIONS):
            second.finish()

    def test_four_newshf_exact_directories_reject_new_members(self):
        copy_inputs(self.root, finite_paths('newshf'))
        directories = ('assets/hd/current-compat/newshf',
                       'authoring-inputs/newshf-current/derived',
                       'assets/hd/newshf-v1',
                       'authoring-inputs/enemies/newshf-phase-a')
        for directory in directories:
            with self.subTest(directory=directory):
                context = self.context()
                context.get('newshf', self.validator)
                added = self.root / directory / 'unexpected-member'
                added.write_bytes(b'')
                try:
                    with self.assertRaises(REJECTIONS):
                        context.get('newshf', self.validator)
                finally:
                    added.unlink()
                fresh = self.context()
                fresh.get('newshf', self.validator)
                fresh.finish()


class FreshFamilyClosureTests(unittest.TestCase):
    def test_all_eight_families_missing_tamper_restore_and_public_freshness(self):
        with tempfile.TemporaryDirectory(prefix='single-proof-family-') as temp:
            root = Path(temp)
            for family in FAMILIES:
                copy_inputs(root, finite_paths(family))
            for family in FAMILIES:
                with self.subTest(family=family):
                    validator = getattr(a, 'verified_current_' + family)
                    context = _ProjectionProofContext(root, ROOT)
                    try:
                        expected = context.get(family, validator)
                        target = root / module(family).MAPPING
                        raw = target.read_bytes()
                        target.unlink()
                        try:
                            with self.assertRaises(REJECTIONS):
                                context.get(family, validator)
                            # Public helper must not consult a prior context.
                            with self.assertRaises(REJECTIONS):
                                validator(root)
                        finally:
                            target.write_bytes(raw)
                        with self.assertRaises(REJECTIONS):
                            context.get(family, validator)
                        fresh = _ProjectionProofContext(root, ROOT)
                        try:
                            self.assertEqual(fresh.get(family, validator), expected)
                            target.write_bytes(raw + b'!')
                            try:
                                with self.assertRaises(REJECTIONS):
                                    fresh.finish()
                            finally:
                                target.write_bytes(raw)
                        finally:
                            fresh.close()
                        self.assertEqual(validator(root), expected)
                    finally:
                        context.close()

    def test_selected_actual_executable_bytes_and_renderer_profile_drift(self):
        with tempfile.TemporaryDirectory(prefix='single-proof-actual-tool-') as temp:
            root = Path(temp)
            for family, attribute, profile in (('rear_p7', 'NODE', 'NODE_VERSION'),
                                                ('rear_p7', 'SHARP', 'NODE_VERSION'),
                                                ('missile', 'MAGICK', 'MAGICK_VERSION')):
                copy_inputs(root, finite_paths(family))
                c = module(family)
                kinds = ('executable-bytes',) if attribute == 'SHARP' else ('executable-bytes', 'renderer-profile')
                for kind in kinds:
                    with self.subTest(family=family, attribute=attribute, kind=kind):
                        context = _ProjectionProofContext(root, ROOT)
                        try:
                            context.get(family, lambda root: {'checked': family})
                            if kind == 'renderer-profile':
                                with patch.object(c, profile, 'changed profile'):
                                    with self.assertRaises(REJECTIONS):
                                        context.get(family, lambda root: {'checked': family})
                            else:
                                target = Path(getattr(c, attribute)).resolve()
                                original_open = Path.open
                                class ChangedStream:
                                    def __init__(self, stream):
                                        self.stream, self.changed = stream, False
                                    def __enter__(self):
                                        return self
                                    def __exit__(self, *args):
                                        self.stream.close()
                                    def read(self, size=-1):
                                        raw = self.stream.read(size)
                                        if raw and not self.changed:
                                            self.changed = True
                                            raw = bytes([raw[0] ^ 1]) + raw[1:]
                                        return raw
                                def open_with_fault(path, *args, **kwargs):
                                    stream = original_open(path, *args, **kwargs)
                                    if path == target and (args[0] if args else kwargs.get('mode', 'r')) == 'rb':
                                        return ChangedStream(stream)
                                    return stream
                                with patch.object(Path, 'open', open_with_fault):
                                    with self.assertRaises(REJECTIONS):
                                        context.get(family, lambda root: {'checked': family})
                        finally:
                            context.close()

    def test_rear_proof_rejects_other_family_dependency_mutation(self):
        with tempfile.TemporaryDirectory(prefix='single-proof-rear-joint-') as temp:
            root = Path(temp)
            copy_inputs(root, finite_paths('rear39'))
            for family, other in (('rear39', 'rear_p7'), ('rear_p7', 'rear39')):
                with self.subTest(family=family, other=other):
                    context = _ProjectionProofContext(root, ROOT)
                    try:
                        context.get(family, lambda root: {'validated': family})
                        opposite = module(other)
                        target = root / (opposite.ROOT + '/' + opposite.name(*opposite.PAIRS[0]))
                        raw = target.read_bytes()
                        target.write_bytes(raw + b'!')
                        try:
                            with self.assertRaises(REJECTIONS):
                                context.get(family, lambda root: {'validated': family})
                        finally:
                            target.write_bytes(raw)
                    finally:
                        context.close()


class SingleProjectionIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = a.current_asset_inventory(ROOT)

    def test_exact_output_eight_proofs_once_and_next_call_fresh(self):
        # Counter wrappers are instrumentation only; each calls the unchanged
        # original validator. The context itself is never mocked.
        from contextlib import ExitStack
        with ExitStack() as stack:
            counters = {family: stack.enter_context(patch.object(
                a, 'verified_current_' + family,
                wraps=getattr(a, 'verified_current_' + family))) for family in FAMILIES}
            first = a.project_p9_inventory(self.inventory, ROOT)
            self.assertEqual(a.sha(a.canonical(first)), EXPECTED)
            self.assertEqual({k: v.call_count for k, v in counters.items()}, dict.fromkeys(FAMILIES, 1))
            second = a.project_p9_inventory(self.inventory, ROOT)
            self.assertEqual(second, first)
            self.assertEqual({k: v.call_count for k, v in counters.items()}, dict.fromkeys(FAMILIES, 2))

    def test_all_public_proof_signatures_are_fresh_not_context_capable(self):
        for family in FAMILIES:
            validator = getattr(a, 'verified_current_' + family)
            self.assertEqual(list(inspect.signature(validator).parameters), ['root'])
            with self.assertRaises(TypeError):
                validator(ROOT, _proofs=object())
        self.assertEqual(list(inspect.signature(a.project_p9_inventory).parameters), ['current', 'root'])
        with self.assertRaises(TypeError):
            a.project_p9_inventory(self.inventory, ROOT, _proofs=object())

    def test_same_invocation_mutation_before_second_reuse_rejects_then_restores(self):
        get = _ProjectionProofContext.get
        original_open = Path.open
        target = ROOT / 'src/current_rear_multi_payload_pins.h'
        seen = 0
        changed = False
        def counted(context, family, validator):
            nonlocal seen, changed
            if family == 'rear39':
                seen += 1
                if seen == 2:
                    changed = True
            return get(context, family, validator)
        def open_with_fault(path, *args, **kwargs):
            if changed and path == target and (args[0] if args else kwargs.get('mode', 'r')) == 'rb':
                with original_open(path, 'rb') as stream:
                    return io.BytesIO(stream.read() + b'!')
            return original_open(path, *args, **kwargs)
        with patch.object(_ProjectionProofContext, 'get', counted), patch.object(Path, 'open', open_with_fault):
            with self.assertRaises(REJECTIONS):
                a.project_p9_inventory(self.inventory, ROOT)
        self.assertGreaterEqual(seen, 2)
        self.assertEqual(a.sha(a.canonical(a.project_p9_inventory(self.inventory, ROOT))), EXPECTED)

    def test_final_projection_boundary_checks_after_last_consumer(self):
        finish = _ProjectionProofContext.finish
        original_open = Path.open
        target = ROOT / 'src/current_rear_multi_payload_pins.h'
        def corrupt_final(context):
            def open_with_fault(path, *args, **kwargs):
                if path == target and (args[0] if args else kwargs.get('mode', 'r')) == 'rb':
                    with original_open(path, 'rb') as stream:
                        return io.BytesIO(stream.read() + b'!')
                return original_open(path, *args, **kwargs)
            with patch.object(Path, 'open', open_with_fault):
                return finish(context)
        with patch.object(_ProjectionProofContext, 'finish', corrupt_final):
            with self.assertRaises(REJECTIONS):
                a.project_p9_inventory(self.inventory, ROOT)

    def test_caller_inventory_missing_hash_and_mode_still_reject(self):
        name = module('rear39').SELECTION
        for mutation in ('missing', 'hash', 'mode'):
            invalid = copy.deepcopy(self.inventory)
            if mutation == 'missing':
                invalid.pop(name)
            elif mutation == 'hash':
                invalid[name]['sha256'] = '0' * 64
            else:
                invalid[name]['mode'] = '100755'
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                a.project_p9_inventory(invalid, ROOT)


if __name__ == '__main__':
    unittest.main()
