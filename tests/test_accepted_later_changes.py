"""Negative controls for the immutable historical projection boundary."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import accepted_later_changes as projection

class SourceBoundary(unittest.TestCase):
    def test_historical_249_and_current_extension_have_separate_provenance(self):
        ledger=projection.load('current-source-inventory.json')
        self.assertNotIn('published_current',ledger)
        self.assertEqual(ledger['historical_current'],'775b6b77163723c6cae727bafce1d53746a5bd60')
        self.assertEqual(ledger['historical_source_count'],249)
        self.assertEqual(set(ledger['current_extensions']),{projection.SIDEKICK_HEADER})
        self.assertEqual(ledger['current_extensions'][projection.SIDEKICK_HEADER]['introduced_by'],'0ded81a95d854f30a4f4a4117fee96f28232039b')
        self.assertEqual(len(ledger['files']),250)
        self.assertEqual(ledger['files'][projection.SIDEKICK_HEADER],ledger['current_extensions'][projection.SIDEKICK_HEADER]['baseline_sha256'])

    def test_all_inverse_results_and_inside_outside_mutations(self):
        for label in ('data','rear-p1','storm','render-boundaries'):
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

    def test_render_correction_has_separate_current_and_historical_provenance(self):
        ledger=projection.load('render-boundaries-source.json')
        self.assertEqual(ledger['integration_base'],'6ada526fa11c633e3ae02facb5f498bbfdacd1d9')
        self.assertEqual(set(ledger['files']),{'src/render_mirror.c','src/global_talon_mirror.inc'})
        historical=projection.load('current-source-inventory.json')
        self.assertEqual(historical['historical_current'],'775b6b77163723c6cae727bafce1d53746a5bd60')
        for name,pin in ledger['files'].items():
            raw=(projection.ROOT/name).read_bytes()
            self.assertEqual(projection.sha(raw),pin['current_sha256'])
            self.assertNotEqual(pin['current_sha256'],historical['files'][name])
            self.assertEqual(projection.sha(projection.project_source('render-boundaries',name,raw)),historical['files'][name])
        from unittest.mock import patch
        raw=(projection.FIXTURES/'render-boundaries-source.json').read_bytes()
        with patch.object(Path,'read_bytes',return_value=raw+b' '):
            with self.assertRaises(AssertionError):projection.load('render-boundaries-source.json')
    def test_sidekick_header_is_exact_and_keeps_strict_inventory(self):
        name='src/current_sidekick_body_payload_pins.h'
        digest='baa91d0eb1864fe13691d43adc148a13a96e16ef3adcda5a0eb6673e17d44571'
        rows=projection.load('current-source-inventory.json')['files']
        self.assertEqual(rows[name],digest)
        self.assertEqual(projection.sha((projection.ROOT/name).read_bytes()),projection.verified_sidekick_current()['header_sha256'])
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
        cls.inventory=projection.current_asset_inventory()
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

    def test_exact_nine_current_outputs_reject_missing_hash_mode_and_unknown(self):
        proof=dict(projection.verified_sidekick_current()['assets'])
        proof.update(projection.verified_craft267_current()['assets'])
        reviewed=projection.load('p9-assets.json')['verified_current_outputs']
        self.assertEqual(set(proof),set(reviewed));self.assertEqual(len(proof),9)
        for name in proof:
            for action in ('delete','hash','mode'):
                mutant=copy.deepcopy(self.inventory)
                if action=='delete':del mutant[name]
                elif action=='hash':mutant[name]['sha256']='0'*64
                else:mutant[name]['mode']='100755'
                with self.subTest(path=name,action=action),self.assertRaises(AssertionError):projection.project_p9_inventory(mutant)
        mutant=copy.deepcopy(self.inventory)
        mutant[projection.SIDEKICK_ROOT+'/unapproved.hda']={'sha256':'0'*64,'mode':'100644'}
        with self.assertRaises(AssertionError):projection.project_p9_inventory(mutant)

    def test_old_asset_edits_and_digest_are_preserved(self):
        ledger=projection.load('p9-assets.json')
        self.assertEqual(ledger['current_inventory_sha256'],'3f819ca1f9ac2b9ef4de53cfe4fb948bc0d347bd0f1f7b539dbb7bfd2915ae34')
        self.assertEqual(len(ledger['asset_edits']),3259)
        current=copy.deepcopy(self.inventory)
        for name in ledger['verified_current_outputs']:del current[name]
        projection.project_craft267_readme(current,projection.ROOT,ledger)
        self.assertEqual(projection.sha(projection.canonical(current)),ledger['current_inventory_sha256'])
        old=next(n for n in current if n not in ledger['asset_edits'])
        for action in ('delete','change'):
            mutant=copy.deepcopy(self.inventory)
            if action=='delete':del mutant[old]
            else:mutant[old]['sha256']='0'*64
            with self.subTest(action=action),self.assertRaises(AssertionError):projection.project_p9_inventory(mutant)

    def test_asset_ledger_pin_rejects_byte_changes(self):
        from unittest.mock import patch
        raw=(projection.FIXTURES/'p9-assets.json').read_bytes()
        with patch.object(Path,'read_bytes',return_value=raw+b' '):
            with self.assertRaises(AssertionError):projection.load('p9-assets.json')

    def test_asset_symlink_guards_without_native_link_creation(self):
        from unittest.mock import patch
        for target in (projection.ROOT/'assets',projection.ROOT/projection.SIDEKICK_SELECTION):
            with self.subTest(path=str(target)),patch.object(Path,'is_symlink',lambda p:p==target):
                with self.assertRaisesRegex(AssertionError,'symlink'):projection.current_asset_inventory()

class GitModeBoundary(unittest.TestCase):
    def test_index_parser_is_exact_and_fail_closed(self):
        oid=b'0'*40
        def row(mode=b'100644',stage=b'0',name=b'assets/x'):
            return mode+b' '+oid+b' '+stage+b'\t'+name+b'\0'
        self.assertEqual(projection.parse_git_asset_modes(row()+row(b'100755',name=b'assets/y')),{'assets/x':'100644','assets/y':'100755'})
        for raw in (row()+row(),row(stage=b'1'),row(mode=b'120000'),row(mode=b'160000'),row(name=b'src/x')):
            with self.subTest(raw=raw),self.assertRaises(AssertionError):projection.parse_git_asset_modes(raw)

    def test_windows_git_mode_and_posix_working_mode_are_separate(self):
        from types import SimpleNamespace
        class PlainFile:
            def stat(self):return SimpleNamespace(st_mode=0o100644)
        path=PlainFile();modes={'assets/x':'100755'}
        self.assertEqual(projection.asset_file_mode(path,'assets/x',modes,windows=True),'100755')
        with self.assertRaises(AssertionError):projection.asset_file_mode(path,'assets/x',modes,windows=False)
        with self.assertRaises(AssertionError):projection.asset_file_mode(path,'assets/missing',modes,windows=True)

    def test_real_git_index_is_fresh_and_unknown_assets_rejected(self):
        with tempfile.TemporaryDirectory(prefix='sidekick-mode-fixture-',dir=projection.ROOT.parent) as directory:
            root=Path(directory);(root/'assets').mkdir();p=root/'assets/script';p.write_bytes(b'fixture')
            self.assertTrue(root.resolve().is_relative_to(projection.ROOT.parent.resolve()))
            def git(*args):
                result=subprocess.run(['git','-C',str(root),*args],capture_output=True)
                self.assertEqual(result.returncode,0,(result.stdout+result.stderr).decode(errors='replace'))
                return result.stdout
            git('init','--quiet');git('add','--','assets/script');original=p.stat().st_mode
            git('update-index','--chmod=+x','--','assets/script')
            self.assertEqual(projection.git_asset_modes(root),{'assets/script':'100755'})
            self.assertEqual(p.stat().st_mode,original)
            git('update-index','--chmod=-x','--','assets/script')
            self.assertEqual(projection.current_asset_inventory(root)['assets/script']['mode'],'100644')
            (root/'assets/unknown').write_bytes(b'new')
            with self.assertRaisesRegex(AssertionError,'absent from Git'):projection.current_asset_inventory(root)
            (root/'assets/unknown').unlink();p.unlink()
            with self.assertRaisesRegex(AssertionError,'path mismatch'):projection.current_asset_inventory(root)

class CurrentGenerationBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Reuse the existing isolated authoring fixture, not the source checkout.
        from test_current_sidekick_body_authoring import CurrentSidekickBodyTests
        cls.fixture_class=CurrentSidekickBodyTests
        cls.fixture_class.setUpClass();cls.fixture=CurrentSidekickBodyTests()
        cls.root=cls.fixture_class.root;cls.inventory=projection.current_asset_inventory()

    @classmethod
    def tearDownClass(cls):cls.fixture_class.tearDownClass()

    def setUp(self):self.fixture.setUp()

    def test_cli_candidate_png_regeneration_accepts_both_inventories_and_restores(self):
        from test_current_sidekick_body_authoring import png
        import build_current_sidekick_body as builder
        before=projection.verified_sidekick_current(self.root)
        old_generated={n:(self.root/n).read_bytes()for n in (builder.BINDING,builder.RUNTIME)}
        selected=json.loads((self.root/builder.SELECTION).read_bytes())
        # Historical PNG assets stay immutable. Select a new independent candidate
        # outside assets; only the seven admitted generated assets are projected.
        candidate='sidekick-candidate-input.png';raw=png(73);(self.root/candidate).write_bytes(raw)
        selected['version']='projection-cli-positive-control'
        selected['resources'][0].update(source_png=candidate,source_sha256=projection.sha(raw))
        draft=self.fixture_class.base/'projection-draft.json';draft.write_bytes(builder.encoded(selected))
        stage=self.fixture_class.base/'projection-cli-stage'
        results=[]
        for args in (['stage','--selection',str(draft),'--stage',str(stage)],['apply','--stage',str(stage)],['check']):
            result=subprocess.run([sys.executable,str(projection.ROOT/'scripts/build_current_sidekick_body.py'),'--root',str(self.root),*args],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            results.append(dict(mode=args[0],exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr))
        current=projection.verified_sidekick_current(self.root)
        self.assertNotEqual(current['header_sha256'],before['header_sha256'])
        projection.validate_current_sources(self.root)
        inventory=copy.deepcopy(self.inventory);inventory.update(current['assets'])
        projected=projection.project_p9_inventory(inventory,self.root)
        self.assertEqual(projected,projection.project_p9_inventory(self.inventory))
        for name,old in old_generated.items():
            path=self.root/name;regenerated=path.read_bytes()
            try:
                path.write_bytes(old)
                with self.subTest(stale=name),self.assertRaises((AssertionError,ValueError)):
                    projection.verified_sidekick_current(self.root)
            finally:path.write_bytes(regenerated)
        # A new unreviewed path inside assets remains rejected, even when selected.
        extra='assets/hd/authoring/unapproved-candidate.png';(self.root/extra).write_bytes(raw)
        selection_path=self.root/builder.SELECTION;regenerated=selection_path.read_bytes()
        try:
            selected['resources'][0]['source_png']=extra;selection_path.write_bytes(builder.encoded(selected))
            extra_proof=projection.verified_sidekick_current(self.root)
            extra_inventory=copy.deepcopy(inventory);extra_inventory.update(extra_proof['assets'])
            extra_inventory[extra]={'sha256':projection.sha(raw),'mode':'100644'}
            with self.assertRaisesRegex(AssertionError,'unapproved current asset inventory'):projection.project_p9_inventory(extra_inventory,self.root)
        finally:selection_path.write_bytes(regenerated);(self.root/extra).unlink()
        self.fixture.setUp()
        self.assertEqual(projection.verified_sidekick_current(self.root),before)
        projection.validate_current_sources(self.root);projection.project_p9_inventory(self.inventory,self.root)
        evidence=os.environ.get('SIDEKICK_PROJECTION_EVIDENCE')
        if evidence:
            Path(evidence).write_text(json.dumps(dict(status='PASS',candidate_path=candidate,source_sha256=projection.sha(raw),before_header=before['header_sha256'],after_header=current['header_sha256'],projected_paths=sorted(current['assets']),cli=results,restored=True),indent=2)+'\n')

    def test_current_chain_rejects_independent_tampering(self):
        import build_current_sidekick_body as builder
        names=[projection.SIDEKICK_SELECTION,projection.SIDEKICK_HEADER,builder.MAPPING,builder.BINDING,builder.RUNTIME]
        selected=json.loads((self.root/builder.SELECTION).read_bytes())
        names+=[r['source_png'] for r in selected['resources']]
        names+=[projection.SIDEKICK_ROOT+'/'+n for n in projection.SIDEKICK_NAMES]
        for name in names:
            p=self.root/name;raw=p.read_bytes()
            try:
                p.write_bytes(raw+b'broken')
                with self.subTest(path=name),self.assertRaises((AssertionError,ValueError,OSError)):
                    projection.verified_sidekick_current(self.root)
            finally:p.write_bytes(raw)

    def test_self_consistent_hda_header_mapping_still_must_match_png(self):
        import build_current_sidekick_body as builder
        import current_sidekick_body_compatibility as compat
        mapping=json.loads((self.root/builder.MAPPING).read_bytes());row=mapping['files'][0]
        p=self.root/row['source_path'];raw=p.read_bytes();p.write_bytes(raw[:28]+bytes([raw[28]^1])+raw[29:])
        row['sha256']=projection.sha(p.read_bytes());(self.root/builder.MAPPING).write_bytes(builder.encoded(mapping))
        pins={r['identity']:compat.fnv((self.root/r['source_path']).read_bytes()[28:])for r in mapping['files']}
        (self.root/builder.HEADER).write_bytes(compat.payload_header(pins))
        with self.assertRaisesRegex(AssertionError,'PNG/HDA mismatch'):projection.verified_sidekick_current(self.root)

    def test_selection_identity_size_and_path_constraints_remain_exact(self):
        import build_current_sidekick_body as builder
        from test_current_sidekick_body_authoring import png
        path=self.root/builder.SELECTION;raw=path.read_bytes();selected=json.loads(raw)
        for case in ('identity','missing','order','escape','size'):
            mutated=copy.deepcopy(selected)
            if case=='identity':mutated['resources'][0]['identity']=1290224
            elif case=='missing':mutated['resources'].pop()
            elif case=='order':mutated['resources'].reverse()
            elif case=='escape':mutated['resources'][0]['source_png']='../outside.png'
            else:
                bad=png(17,width=95);(self.root/'bad-size.png').write_bytes(bad)
                mutated['resources'][0].update(source_png='bad-size.png',source_sha256=projection.sha(bad))
            try:
                path.write_bytes(builder.encoded(mutated))
                with self.subTest(case=case),self.assertRaises((AssertionError,ValueError,OSError)):projection.verified_sidekick_current(self.root)
            finally:path.write_bytes(raw)

    def test_source_scope_unknown_missing_and_old_non_target_still_fail(self):
        header=self.root/projection.SIDEKICK_HEADER;raw=header.read_bytes();header.unlink()
        try:
            with self.assertRaisesRegex(AssertionError,'source paths'):projection.validate_current_sources(self.root)
        finally:header.write_bytes(raw)
        extra=self.root/'src/unapproved-current.h';extra.write_bytes(b'new')
        try:
            with self.assertRaisesRegex(AssertionError,'source paths'):projection.validate_current_sources(self.root)
        finally:extra.unlink()
        for name,reason in [('src/render_mirror.c','not the accepted published current blob'),('src/player.c','non-target source')]:
            old=self.root/name;raw=old.read_bytes();old.write_bytes(raw+b'\n')
            try:
                with self.subTest(path=name),self.assertRaisesRegex(AssertionError,reason):projection.validate_current_sources(self.root)
            finally:old.write_bytes(raw)

    def test_rebinding_changed_or_replaced_non_code_cannot_bless_same_count(self):
        import build_current_sidekick_body as builder
        import verify_current_production as production
        for case in ('changed','replaced'):
            self.fixture.setUp()
            old=self.root/'src/third_party/dr_mp3-LICENSE'
            if case=='changed':old.write_bytes(old.read_bytes()+b'bad')
            else:old.unlink();(self.root/'src/unapproved.txt').write_bytes(b'new')
            binding=json.loads((self.root/builder.BINDING).read_bytes())
            binding['source_sha256']=production.source_inventory(self.root)
            binding['production_source_manifest_sha256']=production.source_manifest_digest(binding['source_sha256'])
            self.assertEqual(len(binding['source_sha256']),252)
            (self.root/builder.BINDING).write_bytes(builder.encoded(binding))
            with self.subTest(case=case),self.assertRaisesRegex(AssertionError,'non-target production source binding'):
                projection.verified_sidekick_current(self.root)

class Craft267ProjectionBoundary(unittest.TestCase):
    def test_readme_inverse_is_exact_complete_blob_and_one_hunk(self):
        ledger=projection.load('p9-assets.json')
        current={projection.CRAFT267_README:{'sha256':projection.sha((projection.ROOT/projection.CRAFT267_README).read_bytes()),'mode':'100644'}}
        projection.project_craft267_readme(current,projection.ROOT,ledger)
        self.assertEqual(current[projection.CRAFT267_README],{'sha256':'793620871ba918511cb9af808f9f298edbdc3e6d66524a12706c08ba84520aaf','mode':'100644'})
        from unittest.mock import patch
        raw=(projection.ROOT/projection.CRAFT267_README).read_bytes()
        bad={projection.CRAFT267_README:{'sha256':projection.sha(raw),'mode':'100644'}}
        with patch.object(Path,'read_bytes',return_value=raw+b'changed'):
            with self.assertRaisesRegex(AssertionError,'README blob'):projection.project_craft267_readme(bad,projection.ROOT,ledger)
        for field,value in (('path','assets/other.md'),('mode','100755'),('after_lines',[20,22]),('before','wrong\n'),('after','wrong\n')):
            mutant=copy.deepcopy(ledger);mutant['craft267_readme_inverse'][field]=value
            with self.subTest(field=field),self.assertRaises(AssertionError):projection.project_craft267_readme(copy.deepcopy(bad),projection.ROOT,mutant)

class Craft267CurrentGenerationBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_current_craft267_authoring import Craft267AuthoringTests
        cls.fixture_class=Craft267AuthoringTests;cls.fixture_class.setUpClass()
        cls.fixture=Craft267AuthoringTests();cls.root=Craft267AuthoringTests.root
        cls.inventory=projection.current_asset_inventory()
    @classmethod
    def tearDownClass(cls):cls.fixture_class.tearDownClass()
    def setUp(self):self.fixture.setUp()
    def tearDown(self):
        from test_current_craft267_authoring import case_failed
        if case_failed(self):self.fixture_class._preserve_fixture=True
        else:
            try:self.fixture._restore_fixture()
            except BaseException:
                self.fixture_class._preserve_fixture=True
                raise
    def test_craft267_candidate_projects_and_preserves_sidekick_and_sources(self):
        import build_current_craft267 as builder
        from test_current_craft267_authoring import png
        before=projection.verified_craft267_current(self.root)
        sidekick=projection.verified_sidekick_current(self.root)
        raw=png();candidate='craft267-projection-candidate.png';(self.root/candidate).write_bytes(raw)
        selected=self.fixture.selected();selected['version']='projection-craft267-positive'
        selected['resources'][0].update(source_png=candidate,source_sha256=projection.sha(raw))
        stage=self.fixture.stage(selected);builder.apply(self.root,stage)
        self.assertEqual(builder.check(self.root)['status'],'PASS')
        after=projection.verified_craft267_current(self.root);self.assertNotEqual(before,after)
        self.assertEqual(sidekick,projection.verified_sidekick_current(self.root))
        projection.validate_current_sources(self.root)
        inventory=copy.deepcopy(self.inventory);inventory.update(after['assets'])
        self.assertEqual(projection.project_p9_inventory(inventory,self.root),projection.project_p9_inventory(self.inventory))
        extra='assets/hd/authoring/unapproved-craft267.png';inventory[extra]={'sha256':projection.sha(raw),'mode':'100644'}
        with self.assertRaisesRegex(AssertionError,'unapproved current asset inventory'):projection.project_p9_inventory(inventory,self.root)
    def test_craft267_chain_rejects_independent_tampering(self):
        import build_current_craft267 as builder
        selected=self.fixture.selected()
        names=[builder.SELECTION,builder.CANONICAL,builder.MAPPING,builder.RUNTIME,selected['resources'][0]['source_png']]
        for name in names:
            p=self.root/name;raw=p.read_bytes()
            try:
                p.write_bytes(raw+b'changed')
                with self.subTest(path=name),self.assertRaises((AssertionError,ValueError,OSError)):projection.verified_craft267_current(self.root)
            finally:p.write_bytes(raw)


if __name__=='__main__':unittest.main()
