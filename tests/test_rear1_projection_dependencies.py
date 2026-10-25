"""The third shared Rear family extends proof inputs, never the cache lifetime."""
from pathlib import Path
import io
import tempfile
import unittest
from unittest.mock import patch
import accepted_later_changes as a
import current_rear1_compatibility as c
from _projection_proof_context import _ProjectionProofContext
from test_single_projection_proof_context import copy_inputs, finite_paths, REJECTIONS

class Rear1ProjectionDependencies(unittest.TestCase):
    def test_all_four_rear_proofs_bind_pillow_profiles_and_package_bytes(self):
        import PIL.PngImagePlugin
        with tempfile.TemporaryDirectory(prefix='rear1-proof-tools-') as temp:
            root=Path(temp)
            copy_inputs(root,finite_paths('rear1'))
            for family in ('rear281','rear1','rear39','rear_p7'):
                for attribute in ('PILLOW_VERSION','PILLOW_ZLIB_VERSION','ZLIB_VERSION'):
                    with self.subTest(family=family,attribute=attribute):
                        context=_ProjectionProofContext(root,a.ROOT)
                        try:
                            context.get(family,lambda root:{'checked':family})
                            with patch.object(c,attribute,'changed-profile'),self.assertRaises(REJECTIONS):
                                context.get(family,lambda root:{'checked':family})
                        finally:context.close()
                target=Path(PIL.PngImagePlugin.__file__)
                original=Path.open
                def changed(path,*args,**kwargs):
                    stream=original(path,*args,**kwargs)
                    if path==target and (args[0] if args else kwargs.get('mode','r'))=='rb':
                        with stream:raw=stream.read()
                        return io.BytesIO(raw+b'!')
                    return stream
                with self.subTest(family=family,attribute='Pillow PNG implementation'):
                    context=_ProjectionProofContext(root,a.ROOT)
                    try:
                        context.get(family,lambda root:{'checked':family})
                        with patch.object(Path,'open',changed),self.assertRaises(REJECTIONS):
                            context.get(family,lambda root:{'checked':family})
                    finally:context.close()

    def test_nine_asset_scope_and_eight_preimages_are_closed(self):
        ledger=a.current_rear1_ledger()
        self.assertEqual(ledger['integration_base'],'8c3d9098a17c0793f7277c9d4302a923df006ec9')
        self.assertEqual(ledger['files'],{})
        self.assertEqual({r['destination'] for r in ledger['runtime_before']},
            {'assets/gameplay/'+c.name(*pair) for pair in c.PAIRS})
        self.assertEqual(len(ledger['runtime_before']),8)
        with tempfile.TemporaryDirectory(prefix='rear1-proof-files-') as temp:
            root=Path(temp);copy_inputs(root,finite_paths('rear1'))
            # An actual copied data root is separate from module/ledger root.
            for name in (c.SELECTION,c.MAPPING,c.HEADER,*c.generated_paths()):
                target=root/name;raw=target.read_bytes();oldmode=target.stat().st_mode & 0o777
                for mutation in ('mode','missing','bytes'):
                    with self.subTest(name=name,mutation=mutation):
                        context=_ProjectionProofContext(root,a.ROOT)
                        try:
                            context.get('rear1',lambda root:{'checked':'rear1'})
                            if mutation=='mode':target.chmod(oldmode ^ 0o100)
                            elif mutation=='missing':target.unlink()
                            else:target.write_bytes(raw+b'!')
                            with self.assertRaises(REJECTIONS):
                                context.get('rear1',lambda root:{'checked':'rear1'})
                        finally:
                            target.write_bytes(raw);target.chmod(oldmode);context.close()
            context=_ProjectionProofContext(root,a.ROOT)
            try:
                self.assertEqual(context.get('rear1',lambda root:{'restored':True}),{'restored':True})
                context.finish()
            finally:context.close()

if __name__=='__main__':unittest.main()
