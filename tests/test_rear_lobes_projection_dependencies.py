"""The fifth shared Rear family extends proof inputs, never the cache lifetime."""
from pathlib import Path
import io
import tempfile
import unittest
from unittest.mock import patch
import accepted_later_changes as a
import current_rear_lobes_compatibility as c
from _projection_proof_context import _ProjectionProofContext
from test_single_projection_proof_context import copy_inputs, finite_paths, REJECTIONS

class RearLobesProjectionDependencies(unittest.TestCase):
    def test_aggregate_manual_verifiers_cover_every_current_family(self):
        # Keep the unchanged old-digest test complete when a new finite inverse is added.
        import ast
        helper=ast.parse((a.ROOT/'tests/accepted_later_changes.py').read_text())
        dispatch=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='_current_projection_proof')
        validators=next(n.value for n in dispatch.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='validators' for t in n.targets))
        expected={n.id for n in validators.values}
        suite=ast.parse((a.ROOT/'tests/test_accepted_later_changes.py').read_text())
        method=next(n for n in ast.walk(suite) if isinstance(n,ast.FunctionDef) and n.name=='test_old_asset_edits_and_digest_are_preserved')
        loop=next(n for n in method.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='verifier')
        self.assertIsInstance(loop.iter,ast.Tuple)
        actual={n.attr for n in loop.iter.elts if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id=='projection'}
        self.assertTrue(expected<=actual,sorted(expected-actual))

    def test_nine_asset_scope_and_eight_preimages_are_closed(self):
        ledger=a.current_rear_lobes_ledger()
        self.assertEqual(ledger['integration_base'],'46babac8cf030e6e4496a054a846713dc0d48ffd')
        self.assertEqual(ledger['files'],{})
        self.assertEqual({r['destination'] for r in ledger['runtime_before']},
            {'assets/gameplay/'+c.name(*pair) for pair in c.PAIRS})
        self.assertEqual(len(ledger['runtime_before']),8)
        with tempfile.TemporaryDirectory(prefix='rear_lobes-proof-files-') as temp:
            root=Path(temp);copy_inputs(root,finite_paths('rear_lobes'))
            # An actual copied data root is separate from module/ledger root.
            for name in (c.SELECTION,c.MAPPING,c.HEADER,c.INPUT_ROOT+'/master-203.json',c.INPUT_ROOT+'/master-43.json',*c.generated_paths()):
                target=root/name;raw=target.read_bytes();oldmode=target.stat().st_mode & 0o777
                for mutation in ('mode','missing','bytes'):
                    with self.subTest(name=name,mutation=mutation):
                        context=_ProjectionProofContext(root,a.ROOT)
                        try:
                            context.get('rear_lobes',lambda root:{'checked':'rear_lobes'})
                            if mutation=='mode':target.chmod(oldmode ^ 0o100)
                            elif mutation=='missing':target.unlink()
                            else:target.write_bytes(raw+b'!')
                            with self.assertRaises(REJECTIONS):
                                context.get('rear_lobes',lambda root:{'checked':'rear_lobes'})
                        finally:
                            target.write_bytes(raw);target.chmod(oldmode);context.close()
            context=_ProjectionProofContext(root,a.ROOT)
            try:
                self.assertEqual(context.get('rear_lobes',lambda root:{'restored':True}),{'restored':True})
                context.finish()
            finally:context.close()

if __name__=='__main__':unittest.main()
