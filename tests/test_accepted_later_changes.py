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
        for label in ('data','rear-p1','storm','render-boundaries','charge-body','plasma-projectile','front-multi','enemy-orb','newshf-identity','newshf-compositor'):
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
            self.assertEqual(projection.sha(projection.project_source('charge-body',name,raw)),pin['current_sha256'])
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

class ChargeSourceBoundary(unittest.TestCase):
    def test_exact_five_file_freeze_has_independent_provenance(self):
        ledger=projection.load('charge-body-source.json')
        self.assertEqual(ledger['schema'],'opentyrian-reviewed-charge-body-source-v1')
        self.assertEqual(ledger['integration_base'],'11a9c7f6eaf60ddb2607fe702b03d6ccadcfb6f4')
        self.assertEqual(ledger['supplied_patch_sha256'],'a9df9e940ba745f414a470cb534b98536d99c81c8f676378d4a7f306d460fbda')
        self.assertEqual(ledger['historical_source_inventory'],'current-source-inventory.json')
        self.assertEqual(set(ledger['files']),{'src/entity_draw.c','src/entity_draw.h','src/mainint.c','src/render_mirror.c','src/render_mirror.h'})
        self.assertEqual(set(projection.corrected_source_paths()),set(ledger['files'])|{'src/config.c','src/game_probe.c','src/opentyr.c','src/asset_debug.c'}|{'src/global_talon_mirror.inc','src/asteroid1_enemy_orb112113_mirror.inc','src/sprite.c','src/tyrian2.c','src/newshf_identity_validation.inc'}|{'src/global_'+family+'_mirror.inc' for family in ('shield','pulse','vulcan','hitflare','smoke','green','small_explosion','cash25','rotor')})
        for name,pin in ledger['files'].items():
            with self.subTest(path=name):
                raw=(projection.ROOT/name).read_bytes()
                self.assertEqual(projection.sha(projection.project_source('plasma-projectile',name,raw)),pin['current_sha256'])
                self.assertEqual(projection.sha(projection.project_source('charge-body',name,raw)),pin['previous_sha256'])

    def test_newest_then_render_then_feature_exactly_once_without_git(self):
        from unittest.mock import patch
        name='src/render_mirror.c';raw=(projection.ROOT/name).read_bytes()
        charge=projection.load('charge-body-source.json')['files'][name]
        render=projection.load('render-boundaries-source.json')['files'][name]
        self.assertEqual(charge['previous_sha256'],render['current_sha256'])
        with patch.object(projection.subprocess,'check_output',side_effect=AssertionError('Git history forbidden')):
            with patch.object(projection,'_project_source_once',wraps=projection._project_source_once) as once:
                old=projection.project_source('storm',name,raw)
                self.assertEqual([call.args[0] for call in once.call_args_list],['normal-observer-surface','enemy-controlled-probe','enemy-reuse-observe','enemy-proof-dedup','enemy-protron-reuse','enemy-green-reuse','enemy-reuse','newshf-compositor','newshf-identity','enemy-orb','front-multi','plasma-projectile','charge-body','render-boundaries','storm'])
                self.assertEqual(projection.sha(old),projection.load('storm-source.json')['files'][name]['previous_sha256'])
        intermediate=projection.project_source('charge-body',name,raw)
        with self.assertRaisesRegex(AssertionError,'unapproved current Guided source' if name in projection.current_guided_ledger()['files'] else 'unapproved current Sonic source' if name in projection.current_sonic_ledger()['files'] else ('unapproved current Protron source' if name in projection.current_protron_ledger()['files'] else 'not the accepted published current blob')):
            projection.project_source('charge-body',name,intermediate)

    def test_wrong_source_partial_inverse_and_extra_change_rejected(self):
        ledger=projection.load('charge-body-source.json')
        for name,pin in ledger['files'].items():
            raw=(projection.ROOT/name).read_bytes()
            wrong=next(path for path in ledger['files'] if path!=name)
            mutants=[('wrong-source',(projection.ROOT/wrong).read_bytes()),('extra-change',raw+b'\n/* unapproved */\n')]
            for index,hunk in enumerate(pin['hunks']):
                lines=projection.project_source('plasma-projectile',name,raw).splitlines(keepends=True);a,b=hunk['after_lines']
                self.assertEqual(b''.join(lines[a:b]),hunk['after'].encode())
                lines[a:b]=hunk['before'].encode().splitlines(keepends=True)
                mutants.append(('partial-inverse-%d'%index,b''.join(lines)))
            for case,mutant in mutants:
                with self.subTest(path=name,case=case),self.assertRaisesRegex(AssertionError,'unapproved current Guided source' if name in projection.current_guided_ledger()['files'] else 'unapproved current Sonic source' if name in projection.current_sonic_ledger()['files'] else ('unapproved current Protron source' if name in projection.current_protron_ledger()['files'] else 'not the accepted published current blob')):
                    projection.project_source('charge-body',name,mutant)

    def test_fixture_pin_hunk_and_result_are_all_fail_closed(self):
        from unittest.mock import patch
        ledger=projection.load('charge-body-source.json');name='src/mainint.c'
        raw=(projection.ROOT/name).read_bytes()
        for field,value in (('after_lines',[0,1]),('after','wrong\n'),('before','wrong\n')):
            mutant=copy.deepcopy(ledger);mutant['files'][name]['hunks'][0][field]=value
            with self.subTest(field=field),patch.object(projection,'load',return_value=mutant):
                with self.assertRaises(AssertionError):projection.project_source('charge-body',name,raw)
        fixture=(projection.FIXTURES/'charge-body-source.json').read_bytes()
        with patch.object(Path,'read_bytes',return_value=fixture+b' '):
            with self.assertRaisesRegex(AssertionError,'changed accepted-history ledger'):
                projection.load('charge-body-source.json')

class ChargeCurrentGenerationBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0,str(projection.ROOT/'scripts'))
        import current_sidekick_body_compatibility as compat
        import build_current_sidekick_body as builder
        cls.compat=compat;cls.builder=builder
        cls.temp=tempfile.TemporaryDirectory(prefix='charge-projection-fixture-',dir=projection.ROOT.parent)
        cls.root=Path(cls.temp.name)
        # The twelve declared inputs, nine HDAs, mapping and runtime plan,
        # plus fourteen Sonic inputs to prove the exact additive runtime quartet.
        # No original-game provenance image, historical Git object or full clone.
        paths=compat.charge_input_paths(projection.ROOT)|{compat.CHARGE_MAPPING,builder.RUNTIME}|{projection.CHARGE_ROOT+'/'+name for name in projection.CHARGE_NAMES}
        paths |= projection.sonic_runtime_input_paths(projection.ROOT) | projection.guided_runtime_input_paths(projection.ROOT)
        if len(paths)!=53:raise AssertionError('unexpected historical Charge fixture closure')
        paths |= projection.newshf_runtime_input_paths(projection.ROOT)
        cls.baseline={name:(projection.ROOT/name).read_bytes() for name in paths}
        if set(cls.baseline)!=paths:raise AssertionError('incomplete finite current fixture closure')

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def setUp(self):
        for name,raw in self.baseline.items():
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)

    def _runtime_row(self,row,blob):
        import hashlib
        row.update(bytes=len(blob),sha256=projection.sha(blob),git_blob=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest())

    def test_independent_master_recipe_png_hda_mapping_and_runtime_tampering(self):
        self.assertEqual(len(projection.verified_charge_current(self.root)['assets']),10)
        for name,raw in self.baseline.items():
            path=self.root/name
            try:
                path.write_bytes(raw+b'broken')
                with self.subTest(path=name),self.assertRaises((AssertionError,ValueError,OSError)):
                    projection.verified_charge_current(self.root)
            finally:path.write_bytes(raw)

    def test_rehashed_derived_png_hda_mapping_and_runtime_cannot_override_master(self):
        import io
        from PIL import Image
        selected=json.loads((self.root/projection.CHARGE_SELECTION).read_bytes());row=selected['resources'][0]
        path=self.root/row['source_png']
        with Image.open(path) as original:frame=original.copy()
        point=next((x,y) for y in range(112) for x in range(96) if frame.getpixel((x,y))[3]==255)
        r,g,b,a=frame.getpixel(point);frame.putpixel(point,(r^1,g,b,a))
        stream=io.BytesIO();frame.save(stream,format='PNG');path.write_bytes(stream.getvalue())
        row['source_sha256']=projection.sha(path.read_bytes())
        (self.root/projection.CHARGE_SELECTION).write_bytes(self.builder.encoded(selected))
        mapping=json.loads((self.root/self.compat.CHARGE_MAPPING).read_bytes());mapped=mapping['files'][0]
        path=self.root/mapped['source_path'];blob=path.read_bytes()[:28]+frame.tobytes();path.write_bytes(blob)
        mapped['sha256']=projection.sha(blob)
        (self.root/self.compat.CHARGE_MAPPING).write_bytes(self.builder.encoded(mapping))
        runtime=json.loads((self.root/self.builder.RUNTIME).read_bytes())
        self._runtime_row(next(r for r in runtime['files'] if r['destination']==mapped['destination']),blob)
        (self.root/self.builder.RUNTIME).write_bytes(self.builder.encoded(runtime))
        with self.assertRaisesRegex(ValueError,'Derived Charge PNG does not match master\\+recipe'):
            projection.verified_charge_current(self.root)

    def test_coherent_new_master_recipe_is_current_not_fixed_bootstrap_art(self):
        import io
        from PIL import Image
        before=projection.verified_charge_current(self.root)
        selected=json.loads((self.root/projection.CHARGE_SELECTION).read_bytes())
        master=self.root/selected['master']['source_png']
        with Image.open(master) as original:frame=original.copy()
        point=next((x,y) for y in range(112) for x in range(96) if frame.getpixel((x,y))[3]==255)
        r,g,b,a=frame.getpixel(point);frame.putpixel(point,(r^1,g,b,a))
        stream=io.BytesIO();frame.save(stream,format='PNG');master.write_bytes(stream.getvalue())
        selected['master']['source_sha256']=projection.sha(master.read_bytes())
        path=self.root/selected['recipe']['path'];recipe=json.loads(path.read_bytes())
        recipe['master_sha256']=selected['master']['source_sha256'];path.write_bytes(self.builder.encoded(recipe))
        selected['recipe']['sha256']=projection.sha(path.read_bytes())
        candidate={key:value for key,value in selected.items() if key!='resources'}
        candidate.update(schema=self.compat.CHARGE_CANDIDATE_SCHEMA,version='history-current-master-positive')
        installed,pngs,blobs=self.compat.charge_generate(self.root,self.builder.encoded(candidate),candidate=True)
        (self.root/projection.CHARGE_SELECTION).write_bytes(self.builder.encoded(installed))
        for name,raw in pngs.items():(self.root/name).write_bytes(raw)
        mapping=json.loads((self.root/self.compat.CHARGE_MAPPING).read_bytes());mapping['version']=installed['version']
        runtime=json.loads((self.root/self.builder.RUNTIME).read_bytes());runtime_rows={r['destination']:r for r in runtime['files']}
        for row in mapping['files']:
            blob=blobs[row['identity']];(self.root/row['source_path']).write_bytes(blob)
            row['sha256']=projection.sha(blob);self._runtime_row(runtime_rows[row['destination']],blob)
        (self.root/self.compat.CHARGE_MAPPING).write_bytes(self.builder.encoded(mapping))
        (self.root/self.builder.RUNTIME).write_bytes(self.builder.encoded(runtime))
        after=projection.verified_charge_current(self.root)
        self.assertNotEqual(before,after);self.assertEqual(set(before['assets']),set(after['assets']))
        self.setUp();self.assertEqual(projection.verified_charge_current(self.root),before)

class MintFrontCurrentGenerationBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0,str(projection.ROOT/'scripts'))
        import build_current_sidekick_body as builder
        cls.builder=builder
        cls.temp=tempfile.TemporaryDirectory(prefix='mint-front-projection-fixture-',dir=projection.ROOT.parent)
        cls.root=Path(cls.temp.name)
        selected=json.loads((projection.ROOT/projection.MF_SELECTION).read_bytes())
        paths={projection.MF_SELECTION,projection.MF_MAPPING,builder.RUNTIME}
        paths|={row['source_png'] for row in selected['resources']}
        paths|={projection.MF_ROOT+'/'+name for name in projection.MF_NAMES}
        # Four independent PNGs, selection, mapping, four HDAs and runtime plan,
        # plus fourteen Sonic inputs for the strict runtime projection.
        # No frozen art, source binding, historical Git or extracted game pixels.
        paths |= projection.sonic_runtime_input_paths(projection.ROOT) | projection.guided_runtime_input_paths(projection.ROOT)
        if len(paths)!=41:raise AssertionError('unexpected historical Mint/Front fixture closure')
        paths |= projection.newshf_runtime_input_paths(projection.ROOT)
        cls.baseline={name:(projection.ROOT/name).read_bytes() for name in paths}
        if set(cls.baseline)!=paths:raise AssertionError('incomplete finite current fixture closure')

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def setUp(self):
        for path in self.root.rglob('*'):
            if path.is_file() and path.relative_to(self.root).as_posix() not in self.baseline:path.unlink()
        for name,raw in self.baseline.items():
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)

    def rehash_runtime_row(self,row,blob):
        import hashlib
        row.update(bytes=len(blob),sha256=projection.sha(blob),git_blob=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest())

    def test_each_declared_input_transport_mapping_and_runtime_is_required(self):
        proof=projection.verified_mint_front_current(self.root)
        self.assertEqual(len(proof['assets']),5)
        self.assertEqual(len(proof['source_pngs']),4)
        self.assertTrue(all(name.startswith('authoring-inputs/') for name in proof['source_pngs']))
        for name,raw in self.baseline.items():
            path=self.root/name
            try:
                path.write_bytes(raw+b'broken')
                with self.subTest(path=name),self.assertRaises((AssertionError,ValueError,OSError)):
                    projection.verified_mint_front_current(self.root)
            finally:path.write_bytes(raw)

    def test_coherent_transport_metadata_cannot_replace_selected_png_authority(self):
        mapping=json.loads((self.root/projection.MF_MAPPING).read_bytes());row=mapping['files'][0]
        path=self.root/row['source_path'];old=path.read_bytes();blob=old[:28]+bytes([old[28]^1])+old[29:]
        path.write_bytes(blob);row['sha256']=projection.sha(blob)
        (self.root/projection.MF_MAPPING).write_bytes(self.builder.encoded(mapping))
        runtime=json.loads((self.root/self.builder.RUNTIME).read_bytes())
        self.rehash_runtime_row(next(r for r in runtime['files'] if r['destination']==row['destination']),blob)
        (self.root/self.builder.RUNTIME).write_bytes(self.builder.encoded(runtime))
        with self.assertRaises((AssertionError,ValueError)):
            projection.verified_mint_front_current(self.root)

    def test_each_independent_current_png_can_change_without_rebasing_history(self):
        import io,struct
        from PIL import Image
        before=projection.verified_mint_front_current(self.root)
        for ordinal,identity in enumerate(projection.MF_IDS):
            self.setUp()
            selected=json.loads((self.root/projection.MF_SELECTION).read_bytes());record=selected['resources'][ordinal]
            with Image.open(self.root/record['source_png']) as original:frame=original.copy()
            point=next((x,y) for y in range(frame.height) for x in range(frame.width) if frame.getpixel((x,y))[3])
            r,g,b,a=frame.getpixel(point);frame.putpixel(point,(r^1,g,b,a))
            stream=io.BytesIO();frame.save(stream,format='PNG');png=stream.getvalue()
            candidate=f'authoring-inputs/mint-front-projection-{identity}.png';(self.root/candidate).write_bytes(png)
            selected['version']=f'current-Mint-Front-{identity}'
            record.update(source_png=candidate,source_sha256=projection.sha(png))
            (self.root/projection.MF_SELECTION).write_bytes(self.builder.encoded(selected))
            w,h=(24,28) if identity==1280083 else (12,14)
            blob=struct.pack('<4s6I',b'HDR1',identity,8,w,h,0,0)+frame.tobytes()
            mapping=json.loads((self.root/projection.MF_MAPPING).read_bytes());mapping['version']=selected['version'];row=mapping['files'][ordinal]
            (self.root/row['source_path']).write_bytes(blob);row['sha256']=projection.sha(blob)
            (self.root/projection.MF_MAPPING).write_bytes(self.builder.encoded(mapping))
            runtime=json.loads((self.root/self.builder.RUNTIME).read_bytes())
            self.rehash_runtime_row(next(r for r in runtime['files'] if r['destination']==row['destination']),blob)
            (self.root/self.builder.RUNTIME).write_bytes(self.builder.encoded(runtime))
            after=projection.verified_mint_front_current(self.root)
            with self.subTest(identity=identity):
                self.assertEqual(set(before['assets']),set(after['assets']))
                self.assertEqual({name for name in before['assets'] if before['assets'][name]!=after['assets'][name]},
                                 {projection.MF_SELECTION,row['source_path']})
                self.assertEqual(after['source_pngs'][candidate],projection.sha(png))
        self.setUp();self.assertEqual(projection.verified_mint_front_current(self.root),before)

    def test_existing_runtime_consumers_keep_exact_count_identity_and_metadata(self):
        raw=self.baseline[self.builder.RUNTIME];baseline=json.loads(raw)
        destination='assets/gameplay/'+projection.MF_NAMES[0]
        for case in ('missing','duplicate','path','group','revision','sha','git_blob','bytes'):
            runtime=copy.deepcopy(baseline);row=next(r for r in runtime['files'] if r['destination']==destination)
            if case=='missing':runtime['files'].remove(row)
            elif case=='duplicate':runtime['files'].append(copy.deepcopy(row))
            elif case=='path':row['source_path']='assets/hd/packs/frozen/'+projection.MF_NAMES[0]
            elif case=='sha':row['sha256']='0'*64
            elif case=='git_blob':row['git_blob']='0'*40
            elif case=='bytes':row['bytes']+=1
            else:row[case]='unapproved'
            (self.root/self.builder.RUNTIME).write_bytes(self.builder.encoded(runtime))
            with self.subTest(case=case),self.assertRaises(AssertionError):
                projection.verified_mint_front_current(self.root)
        (self.root/self.builder.RUNTIME).write_bytes(raw)

    def test_shared_phase_paths_and_new_asset_inputs_never_receive_projection_waivers(self):
        raw=self.baseline[projection.MF_SELECTION];original=json.loads(raw)
        for case in ('shared','asset'):
            selected=copy.deepcopy(original)
            if case=='shared':selected['resources'][1].update({key:selected['resources'][0][key] for key in ('source_png','source_sha256')})
            else:
                source=selected['resources'][0];name='assets/hd/authoring/unapproved-mint.png'
                path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes((self.root/source['source_png']).read_bytes());source['source_png']=name
            (self.root/projection.MF_SELECTION).write_bytes(self.builder.encoded(selected))
            with self.subTest(case=case),self.assertRaises((AssertionError,ValueError)):
                projection.verified_mint_front_current(self.root)
        (self.root/projection.MF_SELECTION).write_bytes(raw)

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
        # Match the production finite inverse: validate and remove only these
        # exact newer families before checking the unchanged old digest.
        for verifier in (projection.verified_current_newshf, projection.verified_current_guided, projection.verified_current_sonic, projection.verified_current_protron, projection.verified_protron_current, projection.verified_newshf_current, projection.verified_enemy_orb_current):
            for name, row in verifier()['assets'].items():
                self.assertEqual(current.pop(name), row)
        for name in projection.verified_front_multi_current()['assets']:del current[name]
        for name in projection.verified_plasma_projectile_current()['assets']:del current[name]
        for name in projection.verified_mint_front_current()['assets']:del current[name]
        for name in projection.verified_charge_current()['assets']:del current[name]
        for name in ledger['verified_current_outputs']:del current[name]
        projection.project_craft267_readme(current,projection.ROOT,ledger)
        self.assertEqual(projection.sha(projection.canonical(current)),ledger['current_inventory_sha256'])
        old=next(n for n in current if n not in ledger['asset_edits'])
        for action in ('delete','change'):
            mutant=copy.deepcopy(self.inventory)
            if action=='delete':del mutant[old]
            else:mutant[old]['sha256']='0'*64
            with self.subTest(action=action),self.assertRaises(AssertionError):projection.project_p9_inventory(mutant)

    def test_exact_nine_front_multi_outputs_no_historical_input_waiver(self):
        proof=projection.verified_front_multi_current()['assets']
        expected={projection.FRONT_MULTI_SELECTION}|{projection.FRONT_MULTI_ROOT+'/'+name for name in projection.FRONT_MULTI_NAMES}
        self.assertEqual(set(proof),expected);self.assertEqual(len(proof),9)
        self.assertFalse(set(proof)&set(projection.load('p9-assets.json')['verified_current_outputs']))
        for name in proof:
            for action in ('delete','hash','mode'):
                mutant=copy.deepcopy(self.inventory)
                if action=='delete':del mutant[name]
                elif action=='hash':mutant[name]['sha256']='0'*64
                else:mutant[name]['mode']='100755'
                with self.subTest(path=name,action=action),self.assertRaisesRegex(AssertionError,'unverified Front Multi current output'):
                    projection.project_p9_inventory(mutant)
        extra=projection.FRONT_MULTI_ROOT+'/unapproved.hda'
        mutant=copy.deepcopy(self.inventory);mutant[extra]={'sha256':'0'*64,'mode':'100644'}
        with self.assertRaisesRegex(AssertionError,'unapproved current asset inventory'):
            projection.project_p9_inventory(mutant)

    def test_exact_seven_plasma_outputs_no_historical_input_waiver(self):
        proof=projection.verified_plasma_projectile_current()['assets']
        expected={projection.PLASMA_SELECTION}|{projection.PLASMA_ROOT+'/'+name for name in projection.PLASMA_NAMES}
        self.assertEqual(set(proof),expected);self.assertEqual(len(proof),7)
        self.assertFalse(set(proof)&set(projection.load('p9-assets.json')['verified_current_outputs']))
        for name in proof:
            for action in ('delete','hash','mode'):
                mutant=copy.deepcopy(self.inventory)
                if action=='delete':del mutant[name]
                elif action=='hash':mutant[name]['sha256']='0'*64
                else:mutant[name]['mode']='100755'
                with self.subTest(path=name,action=action),self.assertRaisesRegex(AssertionError,'unverified Plasma projectile current output'):
                    projection.project_p9_inventory(mutant)
        for name in (projection.PLASMA_ROOT+'/unapproved.hda','assets/hd/authoring/plasma-projectile-extra.png'):
            mutant=copy.deepcopy(self.inventory);mutant[name]={'sha256':'0'*64,'mode':'100644'}
            with self.subTest(path=name),self.assertRaisesRegex(AssertionError,'unapproved current asset inventory'):
                projection.project_p9_inventory(mutant)

    def test_exact_ten_charge_outputs_are_separate_from_old_nine(self):
        proof=projection.verified_charge_current()['assets']
        expected={projection.CHARGE_SELECTION}|{projection.CHARGE_ROOT+'/'+name for name in projection.CHARGE_NAMES}
        self.assertEqual(set(proof),expected);self.assertEqual(len(proof),10)
        self.assertFalse(set(proof)&set(projection.load('p9-assets.json')['verified_current_outputs']))
        for name in proof:
            for action in ('delete','hash','mode'):
                mutant=copy.deepcopy(self.inventory)
                if action=='delete':del mutant[name]
                elif action=='hash':mutant[name]['sha256']='0'*64
                else:mutant[name]['mode']='100755'
                with self.subTest(path=name,action=action),self.assertRaisesRegex(AssertionError,'unverified Charge current output'):
                    projection.project_p9_inventory(mutant)
        for name in (projection.CHARGE_ROOT+'/unapproved.hda','assets/hd/authoring/charge-body-extra.png'):
            mutant=copy.deepcopy(self.inventory);mutant[name]={'sha256':'0'*64,'mode':'100644'}
            with self.subTest(path=name),self.assertRaisesRegex(AssertionError,'unapproved current asset inventory'):
                projection.project_p9_inventory(mutant)

    def test_exact_five_mint_front_outputs_are_separate_from_frozen_assets(self):
        proof=projection.verified_mint_front_current()['assets']
        expected={projection.MF_SELECTION}|{projection.MF_ROOT+'/'+name for name in projection.MF_NAMES}
        self.assertEqual(set(proof),expected);self.assertEqual(len(proof),5)
        self.assertFalse(set(proof)&set(projection.load('p9-assets.json')['verified_current_outputs']))
        self.assertFalse(set(proof)&set(projection.verified_charge_current()['assets']))
        for name in proof:
            for action in ('delete','hash','mode'):
                mutant=copy.deepcopy(self.inventory)
                if action=='delete':del mutant[name]
                elif action=='hash':mutant[name]['sha256']='0'*64
                else:mutant[name]['mode']='100755'
                with self.subTest(path=name,action=action),self.assertRaisesRegex(AssertionError,'unverified Mint/Front current output'):
                    projection.project_p9_inventory(mutant)
        for name in (projection.MF_ROOT+'/unapproved.hda','assets/hd/authoring/mint-front-extra.png'):
            mutant=copy.deepcopy(self.inventory);mutant[name]={'sha256':'0'*64,'mode':'100644'}
            with self.subTest(path=name),self.assertRaisesRegex(AssertionError,'unapproved current asset inventory'):
                projection.project_p9_inventory(mutant)

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
        for name,reason in [('src/render_mirror.c','unapproved current Guided source'),('src/player.c','non-target source')]:
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
            payload_headers={projection.CURRENT_NEWSHF_HEADER,projection.CURRENT_GUIDED_HEADER,projection.CURRENT_PROTRON_HEADER,projection.CURRENT_SONIC_HEADER}
            self.assertTrue(payload_headers <= set(binding['source_sha256']))
            self.assertEqual(binding['source_sha256'][projection.CURRENT_NEWSHF_HEADER], projection.verified_current_newshf(self.root)['header_sha256'])
            self.assertEqual(len(binding['source_sha256'])-len(projection.verified_enemy_probe_sources(self.root))-len(payload_headers),265)
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


class PlasmaProjectileSourceBoundary(unittest.TestCase):
    def test_exact_two_hunks_six_literals_and_separate_header_extension(self):
        import re
        ledger=projection.load('plasma-projectile-source.json')
        self.assertEqual(ledger['schema'],'opentyrian-reviewed-plasma-projectile-source-v1')
        self.assertEqual(ledger['integration_base'],'b32bc14adedd761f98b71a2638ee6b73b1b9faf3')
        self.assertEqual(set(ledger['files']),{'src/render_mirror.c'})
        self.assertEqual(ledger['generated_header'],projection.PLASMA_HEADER)
        name='src/render_mirror.c';pin=ledger['files'][name];raw=(projection.ROOT/name).read_bytes()
        raw=projection.project_source('front-multi',name,raw)
        self.assertEqual(projection.sha(raw),pin['current_sha256'])
        self.assertEqual(len(pin['hunks']),2)
        self.assertEqual(pin['hunks'][0]['before'],'')
        self.assertEqual(pin['hunks'][0]['after'],'#include "current_plasma_projectile_payload_pins.h"\n')
        before=pin['hunks'][1]['before'];after=pin['hunks'][1]['after']
        literals=re.findall(r'UINT64_C\(0x[0-9a-f]{16}\)',before)
        macros=re.findall(r'CURRENT_PLASMA_PROJECTILE_\d+_D[48]_PAYLOAD_FNV',after)
        self.assertEqual(len(literals),6)
        self.assertEqual(macros,[f'CURRENT_PLASMA_PROJECTILE_{i}_D{d}_PAYLOAD_FNV' for i,d in projection.PLASMA_PAIRS])
        for literal,macro in zip(literals,macros):after=after.replace(macro,literal,1)
        self.assertEqual(before,after)
        old=projection._project_source_once('plasma-projectile',name,raw)
        self.assertEqual(projection.sha(old),projection.load('charge-body-source.json')['files'][name]['current_sha256'])
        self.assertNotIn(projection.PLASMA_HEADER,projection.load('current-source-inventory.json')['files'])
        for hunk in pin['hunks']:
            lines=raw.splitlines(keepends=True);a,b=hunk['after_lines'];lines[a:b]=hunk['before'].encode().splitlines(keepends=True)
            with self.assertRaises(AssertionError):projection._project_source_once('plasma-projectile',name,b''.join(lines))
        with self.assertRaises(AssertionError):projection._project_source_once('plasma-projectile',name,raw+b'\n')

    def test_inverse_fixture_tampering_and_no_git_chain(self):
        from unittest.mock import patch
        name='src/render_mirror.c';raw=(projection.ROOT/name).read_bytes()
        with patch.object(projection.subprocess,'check_output',side_effect=AssertionError('Git history forbidden')):
            old=projection.project_source('storm',name,raw)
            self.assertEqual(projection.sha(old),projection.load('storm-source.json')['files'][name]['previous_sha256'])
        fixture=(projection.FIXTURES/'plasma-projectile-source.json').read_bytes()
        with patch.object(Path,'read_bytes',return_value=fixture+b' '):
            with self.assertRaisesRegex(AssertionError,'changed accepted-history ledger'):projection.load('plasma-projectile-source.json')

class PlasmaProjectileCurrentGenerationBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0,str(projection.ROOT/'scripts'))
        import current_plasma_projectile_compatibility as compat
        cls.compat=compat
        cls.temp=tempfile.TemporaryDirectory(prefix='plasma-projection-fixture-',dir=projection.ROOT.parent)
        cls.root=Path(cls.temp.name)
        paths=compat.input_paths(projection.ROOT)|{compat.MAPPING,compat.HEADER,'packaging/runtime-assets-v1.json'}|{compat.ROOT+'/'+compat.name(i,d) for i,d in compat.PAIRS}
        paths |= projection.sonic_runtime_input_paths(projection.ROOT) | projection.guided_runtime_input_paths(projection.ROOT)
        if len(paths)!=48:raise AssertionError('unexpected historical Plasma fixture closure')
        paths |= projection.newshf_runtime_input_paths(projection.ROOT)
        cls.baseline={name:(projection.ROOT/name).read_bytes()for name in paths}
        if set(cls.baseline)!=paths:raise AssertionError('incomplete finite current fixture closure')

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def setUp(self):
        for name,raw in self.baseline.items():
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)

    def test_all_fixed_inputs_outputs_mapping_header_and_runtime_tampering(self):
        self.assertEqual(len(projection.verified_plasma_projectile_current(self.root)['assets']),7)
        for name,raw in self.baseline.items():
            path=self.root/name
            try:
                path.write_bytes(raw+b'broken')
                with self.subTest(path=name),self.assertRaises((AssertionError,ValueError,OSError)):
                    projection.verified_plasma_projectile_current(self.root)
            finally:path.write_bytes(raw)

    def test_coherent_master_regeneration_changes_header_not_source_or_old_fixture(self):
        import io
        from PIL import Image
        before=projection.verified_plasma_projectile_current(self.root)
        source=(projection.ROOT/'src/render_mirror.c').read_bytes()
        frozen={p.name:projection.sha(p.read_bytes()) for p in projection.FIXTURES.iterdir() if p.is_file()}
        selected=json.loads((self.root/projection.PLASMA_SELECTION).read_bytes())
        master=self.root/selected['master']['source_png']
        with Image.open(master) as original:frame=original.copy()
        # Broad color edit survives filtering into both densities.
        for y in range(300,316):
            for x in range(560,576):frame.putpixel((x,y),(17,231,79,255))
        stream=io.BytesIO();frame.save(stream,format='PNG');master.write_bytes(stream.getvalue())
        selected['master']['source_sha256']=projection.sha(master.read_bytes())
        candidate={key:value for key,value in selected.items()if key!='resources'}
        candidate.update(schema=self.compat.CANDIDATE_SCHEMA,version='plasma-history-positive-control')
        encoded=lambda x:(json.dumps(x,indent=2)+'\n').encode()
        installed,pngs,blobs=self.compat.generate(self.root,encoded(candidate),candidate=True)
        (self.root/projection.PLASMA_SELECTION).write_bytes(encoded(installed))
        for name,raw in pngs.items():(self.root/name).write_bytes(raw)
        mapping=json.loads((self.root/projection.PLASMA_MAPPING).read_bytes());mapping['version']=installed['version']
        runtime_path=self.root/'packaging/runtime-assets-v1.json';runtime=json.loads(runtime_path.read_bytes())
        runtime_rows={r['destination']:r for r in runtime['files']};pins={}
        import hashlib
        from build_current_art import fnv
        for row in mapping['files']:
            blob=blobs[row['identity'],row['density']];(self.root/row['source_path']).write_bytes(blob)
            row['sha256']=projection.sha(blob)
            runtime_rows[row['destination']].update(bytes=len(blob),sha256=projection.sha(blob),git_blob=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest())
            pins[row['identity'],row['density']]=fnv(blob[28:])
        (self.root/projection.PLASMA_MAPPING).write_bytes(encoded(mapping));runtime_path.write_bytes(encoded(runtime))
        header=self.root/projection.PLASMA_HEADER;header.write_bytes(self.compat.payload_header(pins))
        after=projection.verified_plasma_projectile_current(self.root)
        self.assertNotEqual(before['header_sha256'],after['header_sha256'])
        self.assertEqual(set(before['assets']),set(after['assets']))
        self.assertEqual(source,(projection.ROOT/'src/render_mirror.c').read_bytes())
        self.assertEqual(frozen,{p.name:projection.sha(p.read_bytes())for p in projection.FIXTURES.iterdir()if p.is_file()})
        header.write_bytes(self.baseline[projection.PLASMA_HEADER])
        with self.assertRaisesRegex(ValueError,'payload pins'):projection.verified_plasma_projectile_current(self.root)



class NewshfIdentityProjectionBoundary(unittest.TestCase):
    def test_exact_default_off_identity_only_source_scope(self):
        ledger=projection.load('newshf-identity-source.json')
        self.assertEqual(ledger['integration_base'],'b62a2b00cd2311bc215caa9807c0c85cbd901164')
        self.assertEqual(set(ledger['files']),{'src/render_mirror.c','src/render_mirror.h','src/sprite.c','src/tyrian2.c'})
        self.assertEqual(set(projection.verified_newshf_identity_sources()),{'src/newshf_identity_validation.inc','src/newshf_prototype_pins.h'})
        for name,pin in ledger['files'].items():
            raw=(projection.ROOT/name).read_bytes()
            self.assertEqual(projection.sha(projection.project_source('newshf-identity',name,raw)),pin['previous_sha256'])

    def test_added_module_mutation_missing_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'src').mkdir()
            files=projection.verified_newshf_identity_sources()
            for name in files:(root/name).write_bytes((projection.ROOT/name).read_bytes())
            self.assertEqual(projection.verified_newshf_identity_sources(root),files)
            for name in files:
                p=root/name;raw=p.read_bytes()
                p.write_bytes(raw+b'\n/* unrelated */\n')
                with self.assertRaisesRegex(AssertionError,'prototype module'):projection.verified_newshf_identity_sources(root)
                p.unlink()
                with self.assertRaisesRegex(AssertionError,'prototype module'):projection.verified_newshf_identity_sources(root)
                p.write_bytes(raw)
                from unittest.mock import patch
                with patch.object(Path,'is_symlink',lambda path:path==p):
                    with self.assertRaisesRegex(AssertionError,'prototype module'):projection.verified_newshf_identity_sources(root)

    def test_authoring_authority_keeps_both_prototype_modules_fixed(self):
        from unittest.mock import patch
        sys.path.insert(0,str(projection.ROOT/'scripts'))
        import build_current_art as builder
        from verify_current_production import source_inventory
        registry=json.loads((projection.ROOT/builder.REGISTRY).read_bytes())
        source=source_inventory(projection.ROOT)
        for name in ('src/newshf_identity_validation.inc','src/newshf_prototype_pins.h'):
            for action in ('missing','changed'):
                mutant=dict(source)
                if action=='missing':del mutant[name]
                else:mutant[name]='0'*64
                with self.subTest(path=name,action=action),patch.object(builder,'source_inventory',return_value=mutant):
                    with self.assertRaisesRegex(ValueError,'Unrelated gameplay source changed'):
                        builder.verify_authority(projection.ROOT,registry)

    def test_ledger_scope_and_partial_inverse_reject(self):
        from unittest.mock import patch
        ledger=projection.load('newshf-identity-source.json')
        mutant=copy.deepcopy(ledger);mutant['added_sources']['src/unapproved.inc']='0'*64
        with patch.object(projection,'load',return_value=mutant):
            with self.assertRaisesRegex(AssertionError,'module scope'):projection.verified_newshf_identity_sources()
        for name,pin in ledger['files'].items():
            raw=(projection.ROOT/name).read_bytes()
            for edit in pin['hunks']:
                lines=raw.splitlines(keepends=True);a,b=edit['after_lines'];lines[a:b]=edit['before'].encode().splitlines(keepends=True)
                with self.assertRaisesRegex(AssertionError,'unapproved current Guided source' if name in projection.current_guided_ledger()['files'] else 'unapproved current Sonic source' if name in projection.current_sonic_ledger()['files'] else ('unapproved current Protron source' if name in projection.current_protron_ledger()['files'] else 'not the accepted published current blob')):
                    projection.project_source('newshf-identity',name,b''.join(lines))
        raw=(projection.FIXTURES/'newshf-identity-source.json').read_bytes()
        with patch.object(Path,'read_bytes',return_value=raw+b' '):
            with self.assertRaisesRegex(AssertionError,'changed accepted-history ledger'):projection.load('newshf-identity-source.json')



class NewshfCompositorProjectionBoundary(unittest.TestCase):
    def test_exact_additive_source_scope(self):
        ledger=projection.load('newshf-compositor-source.json')
        self.assertEqual(ledger['integration_base'],'3ce35baa60db9d561fb946b16cfae14891d691d3')
        self.assertEqual(set(ledger['files']),{'src/render_mirror.c','src/render_mirror.h','src/newshf_identity_validation.inc'}|{'src/global_'+family+'_mirror.inc' for family in ('talon','shield','pulse','vulcan','hitflare','smoke','green','small_explosion','cash25','rotor')})
        self.assertEqual(ledger['generated_sources'],['src/newshf_hd_assets.h'])
        self.assertEqual(set(projection.verified_newshf_compositor_sources()),{'src/global_newshf_mirror.inc'})
        for name,pin in ledger['files'].items():
            raw=(projection.ROOT/name).read_bytes()
            self.assertEqual(projection.sha(projection.project_source('newshf-compositor',name,raw)),pin['previous_sha256'])

    def test_executable_module_mutation_missing_and_symlink_rejected(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'src').mkdir()
            name='src/global_newshf_mirror.inc';p=root/name
            raw=(projection.ROOT/name).read_bytes();p.write_bytes(raw)
            self.assertEqual(projection.verified_newshf_compositor_sources(root),projection.verified_newshf_compositor_sources())
            p.write_bytes(raw+b'\n/* unauthorized */\n')
            with self.assertRaisesRegex(AssertionError,'compositor module'):projection.verified_newshf_compositor_sources(root)
            p.unlink()
            with self.assertRaisesRegex(AssertionError,'compositor module'):projection.verified_newshf_compositor_sources(root)
            p.write_bytes(raw)
            with patch.object(Path,'is_symlink',lambda path:path==p):
                with self.assertRaisesRegex(AssertionError,'compositor module'):projection.verified_newshf_compositor_sources(root)

    def test_generated_assets_are_derived_and_extra_consumers_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ('authoring-inputs/enemies/newshf-phase-a','assets/hd/newshf-v1'):
                shutil.copytree(projection.ROOT/name,root/name)
            for name in ('src/newshf_hd_assets.h','src/enemy_reuse_probe.h','src/enemy_reuse_probe.inc','packaging/runtime-assets-v1.json','packaging/current-production-validation.json'):
                (root/name).parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(projection.ROOT/name,root/name)
            for name in (projection.sonic_runtime_input_paths(projection.ROOT) | (projection.guided_runtime_input_paths(projection.ROOT) | projection.newshf_runtime_input_paths(projection.ROOT))):
                (root/name).parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(projection.ROOT/name,root/name)
            baseline=projection.verified_newshf_current(root)
            self.assertEqual(len(baseline['assets']),10)
            for name in (projection.NEWSHF_HEADER,projection.NEWSHF_ROOT+'/'+projection.NEWSHF_NAMES[0]):
                path=root/name;raw=path.read_bytes();path.write_bytes(raw+b'\n')
                with self.assertRaises((ValueError,AssertionError)):projection.verified_newshf_current(root)
                path.write_bytes(raw)
            runtime=root/'packaging/runtime-assets-v1.json';raw=runtime.read_bytes();obj=json.loads(raw)
            extra=dict(obj['files'][-1]);extra['destination']='assets/global/newshf/unapproved.hda';obj['files'].append(extra)
            runtime.write_text(json.dumps(obj))
            with self.assertRaisesRegex(AssertionError,'runtime scope'):projection.verified_newshf_current(root)
            runtime.write_bytes(raw)
            self.assertEqual(projection.verified_newshf_current(root),baseline)

    def test_unrelated_module_cannot_enter_finite_ledger(self):
        from unittest.mock import patch
        ledger=copy.deepcopy(projection.load('newshf-compositor-source.json'))
        ledger['added_sources']['src/unapproved.inc']='0'*64
        with patch.object(projection,'load',return_value=ledger):
            with self.assertRaisesRegex(AssertionError,'module scope'):projection.verified_newshf_compositor_sources()

if __name__=='__main__':unittest.main()
