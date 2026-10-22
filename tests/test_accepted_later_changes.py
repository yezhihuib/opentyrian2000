"""Negative controls for the immutable historical projection boundary."""
import copy
import json
from pathlib import Path
import unittest
import accepted_later_changes as projection

class SourceBoundary(unittest.TestCase):
    def test_all_inverse_results_and_inside_outside_mutations(self):
        for label in ('data','rear-p1','storm'):
            for name,pin in projection.load(label+'-source.json')['files'].items():
                with self.subTest(label=label,path=name):
                    raw=(projection.ROOT/name).read_bytes()
                    old=projection.project_source(label,name,raw)
                    self.assertEqual(projection.sha(old),pin['previous_sha256'])
                    # Reverted old source is not a currently accepted implementation.
                    with self.assertRaises(AssertionError):projection.project_source(label,name,old)
                    # Every allowed hunk still rejects an arbitrary byte mutation.
                    lines=raw.splitlines(keepends=True)
                    for hunk in pin['hunks']:
                        offset=len(b''.join(lines[:hunk['after_lines'][0]]))
                        mutant=raw[:offset]+b'/* unauthorized logic */'+raw[offset:]
                        with self.assertRaises(AssertionError):projection.project_source(label,name,mutant)
                    with self.assertRaises(AssertionError):projection.project_source(label,name,raw+b'\n/* outside hunks */\n')
    def test_inventory_added_deleted_changed(self):
        rows=projection.load('current-source-inventory.json')['files']
        for action in ('add','delete','change'):
            mutant=dict(rows);name=next(iter(mutant))
            if action=='add':mutant['src/unapproved.c']=projection.sha(b'int injected;')
            elif action=='delete':del mutant[name]
            else:mutant[name]='0'*64
            with self.subTest(action=action),self.assertRaises(AssertionError):projection.validate_source_inventory(mutant)
    def test_sidekick_header_is_exact_and_keeps_strict_inventory(self):
        name='src/current_sidekick_body_payload_pins.h'
        digest='baa91d0eb1864fe13691d43adc148a13a96e16ef3adcda5a0eb6673e17d44571'
        rows=projection.load('current-source-inventory.json')['files']
        self.assertEqual(rows[name],digest)
        self.assertEqual(projection.sha((projection.ROOT/name).read_bytes()),digest)
        projection.validate_current_sources()
        for action in ('unknown','missing_header','changed_header'):
            mutant=dict(rows)
            if action=='unknown':mutant['src/current_sidekick_body_unapproved.h']=digest
            elif action=='missing_header':del mutant[name]
            else:mutant[name]='0'*64
            with self.subTest(action=action),self.assertRaises(AssertionError):projection.validate_source_inventory(mutant)
        from unittest.mock import patch
        raw=(projection.FIXTURES/'current-source-inventory.json').read_bytes()
        with patch.object(Path,'read_bytes',return_value=raw+b' '):
            with self.assertRaises(AssertionError):projection.load('current-source-inventory.json')
    def test_source_symlink_guard_with_portable_probe(self):
        # The native-link negative below stays intact; this probe needs no link permission.
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'src').mkdir();alias=root/'src/alias.c';alias.write_bytes(b'int fixture;')
            with patch.object(Path,'is_symlink',lambda path:path==alias):
                with self.assertRaisesRegex(AssertionError,'symlink'):projection.validate_current_sources(root)
    def test_source_symlink_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'src').mkdir()
            (root/'src/alias.c').symlink_to(projection.ROOT/'src/render_mirror.c')
            with self.assertRaisesRegex(AssertionError,'symlink'):projection.validate_current_sources(root)
    def test_ledger_is_immutable(self):
        from unittest.mock import patch
        with patch.object(Path,'read_bytes',return_value=b'{}'):
            with self.assertRaises(AssertionError):projection.load('data-source.json')

class AssetBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory={}
        for p in (projection.ROOT/'assets').rglob('*'):
            if p.is_file() and p.relative_to(projection.ROOT).as_posix()!='assets/hd/manifest.json':
                cls.inventory[p.relative_to(projection.ROOT).as_posix()]={'sha256':projection.sha(p.read_bytes()),'mode':'100755' if p.stat().st_mode&0o111 else '100644'}
    def test_catalog_mutations_inside_and_outside_later_changes(self):
        catalog=json.loads((projection.ROOT/'assets/hd/manifest.json').read_text())
        old=projection.project_p9_catalog(catalog)
        self.assertEqual(old,projection.load('p9-stage-catalog.json'))
        projection.validate_current_catalog(catalog)
        with self.assertRaises(AssertionError):projection.validate_current_catalog(old)
        without_p9=copy.deepcopy(old);del without_p9['player_rear_multicannon_p9_mode2_rotations_v1']
        with self.assertRaises(AssertionError):projection.validate_current_catalog(without_p9)
        for key in ('schema','player_rear_multicannon_p9_mode2_rotations_v1','unapproved'):
            mutant=copy.deepcopy(catalog);mutant[key]={'unauthorized':True}
            with self.subTest(key=key),self.assertRaises(AssertionError):projection.project_p9_catalog(mutant)
        mutant=copy.deepcopy(catalog);del mutant['player_rear_multicannon_p9_mode2_rotations_v1']
        with self.assertRaises(AssertionError):projection.project_p9_catalog(mutant)
    def test_inventory_added_deleted_modified_and_reverted(self):
        projection.project_p9_inventory(self.inventory)
        edits=projection.load('p9-assets.json')['asset_edits']
        changed=next(n for n,e in edits.items() if e['after'] and e['before'] and e['before']!=e['after'])
        for action in ('add','delete','modify','revert','mode'):
            mutant=copy.deepcopy(self.inventory)
            if action=='add':mutant['assets/unapproved.bin']={'sha256':'0'*64,'mode':'100644'}
            elif action=='delete':del mutant[changed]
            elif action=='modify':mutant[changed]['sha256']='0'*64
            elif action=='revert':mutant[changed]=edits[changed]['before']
            else:mutant[changed]['mode']='100755'
            with self.subTest(action=action),self.assertRaises(AssertionError):projection.project_p9_inventory(mutant)

if __name__=='__main__':unittest.main()
