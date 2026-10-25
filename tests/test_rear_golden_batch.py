"""Differential transport tests; the serial oracle remains the production checkers."""
import importlib
import json
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import _rear_golden_batch as batch
from _projection_proof_context import _profile

MODULES = tuple(importlib.import_module('current_' + f + '_compatibility')
                for f in ('rear_p7', 'rear39', 'rear1', 'rear281', 'rear_lobes'))


def serial():
    for module in MODULES:
        module.check_tool()


def failure(call):
    try:
        call()
    except Exception as exc:
        return type(exc), str(exc)
    raise AssertionError('Expected rejection')


class RearGoldenBatch(unittest.TestCase):
    def test_all_original_goldens_and_fresh_process_each_check(self):
        serial()
        original = subprocess.Popen
        processes = []
        def observed(*args, **kwargs):
            proc = original(*args, **kwargs)
            processes.append(proc)
            return proc
        with patch.object(batch.subprocess, 'Popen', observed):
            batch.check_tools(MODULES)
            batch.check_tools(MODULES)
        self.assertEqual(len(processes), 2)
        self.assertNotEqual(processes[0].pid, processes[1].pid)
        self.assertTrue(all(p.poll() == 0 for p in processes))

    def test_late_worker_exit_and_trailing_output_are_rejected(self):
        statement = "process.stdout.write(JSON.stringify({out:Buffer.concat(out).toString('base64'),err:Buffer.concat(err).toString('base64'),code})+'\\n');"
        self.assertIn(statement, batch.DRIVER)
        base = batch.DRIVER.replace("const vm=require('vm'),readline=require('readline');",
                                    "const vm=require('vm'),readline=require('readline');let completed=0;")
        original = subprocess.Popen
        for action in ("process.exit(7)", "process.stdout.write('trailing')",
                       "process.stderr.write('trailing')"):
            processes = []
            def observed(*args, **kwargs):
                proc = original(*args, **kwargs)
                processes.append(proc)
                return proc
            replacement = statement[:-2] + ",()=>{if(++completed===6){" + action + ";}});"
            with self.subTest(action=action), patch.object(batch, 'DRIVER', base.replace(statement, replacement)), \
                 patch.object(subprocess, 'Popen', observed):
                with self.assertRaises((ValueError, OSError)):
                    batch.check_tools(MODULES)
            self.assertEqual(len(processes), 1)
            self.assertIsNotNone(processes[0].poll())
        batch.check_tools(MODULES)

    def test_worker_hang_after_eof_is_terminated_and_reaped(self):
        original_finish, original_popen = batch._Batch.finish, subprocess.Popen
        processes = []
        def short_shutdown(transport):
            import time
            transport.started = time.monotonic() - 179.8
            return original_finish(transport)
        def observed(*args, **kwargs):
            proc = original_popen(*args, **kwargs)
            processes.append(proc)
            return proc
        hanging = batch.DRIVER + "\nlines.on('close',()=>setInterval(()=>{},1000));"
        with patch.object(batch, 'DRIVER', hanging), \
             patch.object(batch._Batch, 'finish', short_shutdown), \
             patch.object(subprocess, 'Popen', observed):
            with self.assertRaisesRegex(ValueError, 'shutdown unavailable/timed out'):
                batch.check_tools(MODULES)
        self.assertEqual(len(processes), 1)
        self.assertIsNotNone(processes[0].poll())
        batch.check_tools(MODULES)

    def test_all_families_profiles_fail_in_same_order(self):
        for module in MODULES:
            for field, value in (('NODE_VERSION', 'wrong'), ('SHARP_VERSIONS', {}),
                                 ('GOLDEN_HASHES', {})):
                with self.subTest(module=module.__name__, field=field):
                    with patch.object(module, field, value):
                        self.assertEqual(failure(serial), failure(lambda: batch.check_tools(MODULES)))
        with patch.object(MODULES[0], 'GOLDEN_HASHES', {}), patch.object(MODULES[4], 'DRIVER', 'throw Error("later")'):
            self.assertEqual(failure(serial), failure(lambda: batch.check_tools(MODULES)))

    def test_all_families_renderer_failures_and_restore(self):
        for module in MODULES:
            for driver in ('process.exit(7)', 'process.stdout.write("not json")',
                           'throw Error("injected renderer failure")',
                           'process.stdout.write("x".repeat(1048577))'):
                with self.subTest(module=module.__name__, driver=driver):
                    with patch.object(module, 'DRIVER', driver):
                        self.assertEqual(failure(serial), failure(lambda: batch.check_tools(MODULES)))
        batch.check_tools(MODULES)

    def test_both_lobes_masters_and_svg_hashes_are_independent(self):
        module = MODULES[-1]
        before = _profile(module)
        for selector in (203, 43):
            hashes = dict(module.GOLDEN_SVG_HASHES)
            hashes[selector] = '0' * 64
            with patch.object(module, 'GOLDEN_SVG_HASHES', hashes):
                self.assertNotEqual(before, _profile(module))
                self.assertEqual(failure(serial), failure(lambda: batch.check_tools(MODULES)))
            masters = dict(module.GOLDEN_MASTERS)
            masters[selector] = b'{}'
            with patch.object(module, 'GOLDEN_MASTERS', masters):
                self.assertNotEqual(before, _profile(module))
                self.assertEqual(failure(serial), failure(lambda: batch.check_tools(MODULES)))
        self.assertEqual(before, _profile(module))
        batch.check_tools(MODULES)

    def test_reject_unexpected_order_callable_and_process_invocation(self):
        with self.assertRaises(ValueError):
            batch.check_tools(tuple(reversed(MODULES)))
        with patch.object(MODULES[0], 'check_tool', lambda: None):
            with self.assertRaises(ValueError):
                batch.check_tools(MODULES)
        transport = batch._Batch()
        try:
            with self.assertRaises(ValueError):
                transport.run(['anything'])
        finally:
            transport.close()

    def test_deadline_terminates_and_reaps_worker(self):
        original = batch._Batch.run
        processes = []
        def expiring(transport, *args, **kwargs):
            result = original(transport, *args, **kwargs)
            processes.append(transport.proc)
            transport.started -= 181
            return result
        with patch.object(batch._Batch, 'run', expiring):
            with self.assertRaisesRegex(ValueError, 'unavailable/timed out'):
                batch.check_tools(MODULES)
        self.assertEqual(len(processes), 1)
        self.assertIsNotNone(processes[0].poll())
        batch.check_tools(MODULES)

    def test_async_hung_driver_is_terminated_and_reaped(self):
        original_init, original_popen = batch._Batch.__init__, subprocess.Popen
        processes = []
        def short_budget(transport):
            original_init(transport)
            transport.started -= 179.8
        def observed(*args, **kwargs):
            proc = original_popen(*args, **kwargs)
            processes.append(proc)
            return proc
        with patch.object(batch._Batch, '__init__', short_budget), \
             patch.object(subprocess, 'Popen', observed), \
             patch.object(MODULES[0], 'DRIVER', '(async()=>{await new Promise(()=>{});})()'):
            with self.assertRaisesRegex(ValueError, 'unavailable/timed out'):
                batch.check_tools(MODULES)
        self.assertEqual(len(processes), 1)
        self.assertIsNotNone(processes[0].poll())

    def test_unknown_sharp_and_node_paths_reject_without_serial_fallback(self):
        for module in MODULES:
            with patch.object(module, 'SHARP', '/no/such/sharp.cjs'):
                self.assertEqual(failure(serial), failure(lambda: batch.check_tools(MODULES)))
            with patch.object(module, 'NODE', '/no/such/node'):
                with self.assertRaises((ValueError, OSError)):
                    batch.check_tools(MODULES)
        batch.check_tools(MODULES)


class RearGoldenContextClosure(unittest.TestCase):
    def test_five_family_real_files_modes_origins_and_final_boundary(self):
        import tempfile
        from test_single_projection_proof_context import copy_inputs, finite_paths
        from _projection_proof_context import _ProjectionProofContext
        with tempfile.TemporaryDirectory(prefix='rear-batch-closure-') as tmp:
            root = Path(tmp)
            copy_inputs(root, finite_paths('rear_p7'))
            for module in MODULES:
                family = module.__name__.removeprefix('current_').removesuffix('_compatibility')
                target = root / module.MAPPING
                original, mode = target.read_bytes(), target.stat().st_mode & 0o777
                for kind in ('missing', 'tamper', 'mode', 'origin', 'final', 'during'):
                    with self.subTest(family=family, kind=kind):
                        context = _ProjectionProofContext(root, ROOT)
                        try:
                            if kind == 'during':
                                def changed(_):
                                    target.write_bytes(original + b'!')
                                    return {'ok': family}
                                with self.assertRaises(ValueError):
                                    context.get(family, changed)
                                continue
                            expected = context.get(family, lambda _: {'ok': family})
                            deps = context._entries[family][0]
                            self.assertIn(ROOT / 'tests/_rear_golden_batch.py', deps.files)
                            if kind == 'origin':
                                with patch.object(module, '__file__', str(root / 'wrong.py')):
                                    with self.assertRaises(ValueError):
                                        context.get(family, lambda _: {})
                            else:
                                if kind == 'missing': target.unlink()
                                elif kind == 'mode': target.chmod(mode ^ 0o100)
                                else: target.write_bytes(original + b'!')
                                with self.assertRaises(ValueError):
                                    if kind == 'final': context.finish()
                                    else: context.get(family, lambda _: {})
                        finally:
                            context.close()
                            target.write_bytes(original)
                            target.chmod(mode)
                    fresh = _ProjectionProofContext(root, ROOT)
                    try:
                        self.assertEqual(fresh.get(family, lambda _: {'ok': family}), {'ok': family})
                    finally:
                        fresh.close()

    def test_post_renderer_snapshot_rejects_same_call_and_final_mutations(self):
        import tempfile
        from test_single_projection_proof_context import copy_inputs, finite_paths
        from _projection_proof_context import _ProjectionProofContext
        original_check = batch.check_tools
        with tempfile.TemporaryDirectory(prefix='rear-batch-post-render-') as tmp:
            root = Path(tmp)
            copy_inputs(root, finite_paths('rear_p7'))
            for module in MODULES:
                family = module.__name__.removeprefix('current_').removesuffix('_compatibility')
                target = root / module.MAPPING
                raw = target.read_bytes()
                for final in (False, True):
                    with self.subTest(family=family, final=final):
                        context = _ProjectionProofContext(root, ROOT)
                        context.get(family, lambda _: {'ok': family})
                        def mutate_after_render(modules):
                            original_check(modules)
                            target.write_bytes(raw + b'!')
                        try:
                            with patch.object(batch, 'check_tools', mutate_after_render):
                                with self.assertRaisesRegex(ValueError, 'during renderer check'):
                                    if final: context.finish()
                                    else: context.get(family, lambda _: {})
                            with self.assertRaisesRegex(ValueError, 'closed'):
                                context.get(family, lambda _: {})
                        finally:
                            context.close()
                            target.write_bytes(raw)

    def test_helper_origin_and_live_profile_are_bound_on_reuse(self):
        import tempfile
        from test_single_projection_proof_context import copy_inputs, finite_paths
        from _projection_proof_context import _ProjectionProofContext
        with tempfile.TemporaryDirectory(prefix='rear-batch-helper-') as tmp:
            root = Path(tmp)
            copy_inputs(root, finite_paths('rear_p7'))
            for attribute, changed in (('__file__', str(root / 'wrong.py')),
                                       ('DRIVER', batch.DRIVER + '// changed'),
                                       ('_ENV', dict(batch._ENV, EXTRA='changed'))):
                context = _ProjectionProofContext(root, ROOT)
                try:
                    context.get('rear_p7', lambda _: {'ok': True})
                    with patch.object(batch, attribute, changed):
                        with self.assertRaises(ValueError):
                            context.get('rear_p7', lambda _: {})
                finally:
                    context.close()


if __name__ == '__main__':
    unittest.main()
