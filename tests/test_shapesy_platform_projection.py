"""Exact PUBLIC7d inverse, finite resource scope, and mutation rejection."""
import copy
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
import shapesy_platform_projection as p
import dualmissile_newshf_projection as dual
import turret_newshf_projection as turret

class ShapesYInverseMechanism(unittest.TestCase):
    def test_exact_inverse_and_all_three_checks(self):
        old=b"first\nold\nlast\n";new=b"first\nnew-a\nnew-b\nlast\n"
        pin=dict(previous_sha256=p.sha(old),current_sha256=p.sha(new),hunks=[
            dict(after_lines=[1,3],before="old\n",after="new-a\nnew-b\n")])
        self.assertEqual(p.inverse('fixture',new,pin),old)
        for raw in (old,new+b'\n',new[:-1]):
            with self.assertRaises(AssertionError):p.inverse('fixture',raw,pin)
        for field in ('before','after'):
            bad=copy.deepcopy(pin);bad['hunks'][0][field]+='bad'
            with self.assertRaises(AssertionError):p.inverse('fixture',new,bad)
        bad=copy.deepcopy(pin);bad['previous_sha256']='0'*64
        with self.assertRaises(AssertionError):p.inverse('fixture',new,bad)


class ShapesYProjection(unittest.TestCase):
    def test_public_inverse_without_git_or_original_data(self):
        with patch.object(subprocess, 'Popen', side_effect=AssertionError('Git/private objects forbidden')):
            proof = p.verified()
            self.assertEqual(len(proof['mapping']), 28)
            self.assertEqual(set(proof['added_sources']), p.ADDED)
            for section, project in (('files',p.project_source), ('asset_edits',p.project_asset)):
                for name, pin in p.ledger()[section].items():
                    raw = (p.ROOT/name).read_bytes()
                    old = project(name,raw)
                    self.assertEqual(p.sha(old),pin['previous_sha256'])
                    for invalid in (raw+b'\n',raw[:-1],old):
                        with self.subTest(name=name), self.assertRaises(AssertionError):
                            project(name,invalid)
                    for h in pin['hunks']:
                        lines=raw.splitlines(True);a,b=h['after_lines']
                        lines[a:b]=h['before'].encode().splitlines(True)
                        with self.assertRaises(AssertionError):project(name,b''.join(lines))

    def test_every_qualified_input_is_rechecked(self):
        read=Path.read_bytes
        for name in p.ledger()['qualified']:
            def changed(path):
                raw=read(path)
                return raw+b'\n' if path==p.ROOT/name else raw
            with self.subTest(name=name),patch.object(Path,'read_bytes',changed),self.assertRaises((AssertionError,ValueError,OSError)):
                p.verified()

    def test_hunk_and_preimage_checks_are_independent(self):
        for section, project in (('files',p.project_source), ('asset_edits',p.project_asset)):
            for name in p.ledger()[section]:
                for key in ('before','after'):
                    altered=copy.deepcopy(p.ledger())
                    altered[section][name]['hunks'][0][key]+='\n'
                    with patch.object(p,'ledger',return_value=altered),self.assertRaises(AssertionError):
                        project(name,(p.ROOT/name).read_bytes())
                altered=copy.deepcopy(p.ledger());altered[section][name]['previous_sha256']='0'*64
                with patch.object(p,'ledger',return_value=altered),self.assertRaises(AssertionError):
                    project(name,(p.ROOT/name).read_bytes())

    # Early nested-family matrix: run this and test_catalog_and_non_y_assets_keep_public_identity.
    def test_exact_inventory_and_runtime_projection(self):
        import sys
        sys.path.insert(0,str(p.ROOT/'scripts'))
        from verify_current_production import source_inventory
        source=source_inventory(p.ROOT);old=p.before_inventory(source)
        self.assertEqual(set(source)-set(old),p.ADDED|dual.ADDED|turret.ADDED)
        self.assertEqual(old,p.ledger()['public_source_inventory'])
        binding=json.loads((p.ROOT/'packaging/current-production-validation.json').read_bytes())
        self.assertEqual(binding['source_sha256'],source)
        for name in p.FILES:self.assertEqual(old[name],p.ledger()['files'][name]['previous_sha256'])
        for name in p.FILES|p.ADDED:
            for action in ('missing','changed'):
                bad=dict(source)
                if action=='missing':del bad[name]
                else:bad[name]='0'*64
                with self.subTest(name=name,action=action),self.assertRaises((AssertionError,KeyError)):
                    p.before_inventory(bad)
        rows=json.loads((p.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files']
        mapping=p.verified()['mapping'];old=p.before_runtime(rows)
        self.assertEqual(old,[r for r in dual.before_runtime(rows) if r['destination'] not in mapping])
        self.assertEqual(len(rows)-len(old),31)  # 28 ShapesY + 1 dualmissile + 2 turret resources
        for destination in mapping:
            for action in ('missing','duplicate','changed'):
                bad=copy.deepcopy(rows);row=next(r for r in bad if r['destination']==destination)
                if action=='missing':bad.remove(row)
                elif action=='duplicate':bad.append(row)
                else:row['revision']='unreviewed'
                with self.subTest(destination=destination,action=action),self.assertRaises(AssertionError):
                    p.before_runtime(bad)

    def test_catalog_and_non_y_assets_keep_public_identity(self):
        current=json.loads((p.ROOT/p.CATALOG).read_bytes())
        before=p.project_catalog(current)
        self.assertEqual(p.sha(p.canonical(before)),p.ledger()['catalog_previous_sha256'])
        self.assertEqual(before,json.loads(p.project_asset(p.CATALOG,(p.ROOT/p.CATALOG).read_bytes())))
        for pack in before['packs']:
            self.assertEqual(len(current['packs'][pack]['files'])-len(before['packs'][pack]['files']),28)
            for name,row in before['packs'][pack]['files'].items():
                self.assertEqual(current['packs'][pack]['files'][name],row)
        with self.assertRaises(AssertionError):p.project_catalog(before)
        bad=copy.deepcopy(current);bad['packs'][bad['default_preview_pack']]['count']+=1
        with self.assertRaises(AssertionError):p.project_catalog(bad)

class ShapesYProofCacheDependencies(unittest.TestCase):
    def test_new_and_older_cached_proofs_bind_numpy_and_pillow(self):
        import numpy, PIL
        import _projection_proof_context as guarded
        for family in ('shapesy_platform','protron'):
            context=guarded._ProjectionProofContext(p.ROOT,p.ROOT)
            self.addCleanup(context.close)
            deps=context._discover(family)
            self.assertTrue({Path(numpy.__file__).parent,Path(PIL.__file__).parent} <= set(deps.external_trees))
            self.assertIn(numpy,deps.modules);self.assertIn(PIL,deps.modules)
            for module in (numpy,PIL):
                self.assertIn((module.__name__,Path(module.__file__).absolute()),deps.code_modules)
            context.get(family,lambda root:{'fake_unit_proof':True})
            with patch.object(numpy,'__version__','changed-test-profile'),self.assertRaisesRegex(ValueError,'dependency'):
                context.get(family,lambda root:self.fail('Cached proof must not rerun'))
            context=guarded._ProjectionProofContext(p.ROOT,p.ROOT)
            self.addCleanup(context.close)
            context.get(family,lambda root:{'fake_unit_proof':True})
            original=guarded._tree_stamp
            def drift(path):
                result=original(path)
                return result+(('test-injected-package-membership-drift',),) if path==Path(numpy.__file__).parent else result
            with patch.object(guarded,'_tree_stamp',drift),self.assertRaisesRegex(ValueError,'dependency'):
                context.get(family,lambda root:self.fail('Cached proof must not rerun'))


if __name__=='__main__':unittest.main()
