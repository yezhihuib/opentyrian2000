"""Run isolated fixture-preparation regression tests with the standard library."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest


PREPARE = Path(__file__).with_name('prepare-effects.py')
BASE = b'int x = 1;\nint y = 2;\n'
OVERRIDE = b'/* exact archived override */\r\n'
BINDING = b'\t\t\t\trender_mirror_bind_terrain(2,z+1,megaData2.shapes[x].sh);\n'

ENEMY_BRANCH = b'\t\t\t\t\t\t{\n\t\t\t\t\t\t\tunsigned int sprite = enemyShot[z].sgr + enemyShot[z].animate;\n\t\t\t\t\t\t\tif (sprite == 112 || sprite == 113)\n\t\t\t\t\t\t\t\tdraw_enemy_shot_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);\n\t\t\t\t\t\t\telse\n\t\t\t\t\t\t\t\tblit_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);\n\t\t\t\t\t\t}\n'
ORIGINAL_ENEMY_DRAW = b'\t\t\t\t\t\t\tblit_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, enemyShot[z].sgr + enemyShot[z].animate);\n'
ENEMY_DECLARATION = b'/* Dedicated surviving enemy-shot normal tile; no player-shadow binding. */\nvoid draw_enemy_shot_sprite2(SDL_Surface *, int x, int y, Sprite2_array, unsigned int index);\n\n'


class PrepareEffectsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='prepare-effects-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.script = self.repo / 'prototype/fixtures/prepare-effects.py'
        self.script.parent.mkdir(parents=True)
        shutil.copy2(PREPARE, self.script)
        (self.repo / 'src').mkdir()
        (self.repo / 'visualc').mkdir()
        (self.repo / 'Makefile').write_bytes(b'# test build file\n')
        (self.repo / 'prototype/build-game.ps1').write_bytes(b'# test build file\n')
        self.fixture = self.script.parent / 'effects/green-trail'
        (self.fixture / 'overrides/src').mkdir(parents=True)
        self.configure()
        self.builder = self.repo / 'prototype/rebuild_retired_hd_pack.py'
        self.builder.write_text(
            "from pathlib import Path\nimport json\n"
            "def build_pack(repo, pack_name, output):\n"
            "    assert isinstance(repo, Path) and isinstance(output, Path)\n"
            "    if pack_name != 'test-pack':\n"
            "        raise ValueError('Unknown retired pack: ' + pack_name)\n"
            "    output.mkdir(parents=True)\n"
            "    (output / 'build-call.json').write_text(json.dumps({\n"
            "        'repo': str(repo), 'pack': pack_name, 'output': str(output)}))\n"
            "    (output / 'frozen.hda').write_bytes(b'archived pack bytes')\n"
        )

    def configure(self, production=BASE, expected=None, override=OVERRIDE,
                  rel='src/base.c'):
        if expected is None:
            expected = BASE.replace(b'\n', b'\r\n')
        (self.repo / rel).write_bytes(production)
        (self.fixture / 'overrides/src/override.c').write_bytes(override)
        manifest = {
            'same_other_production_src_sha256': {
                rel: hashlib.sha256(expected).hexdigest(),
            },
            'tested_exact_source_overrides': {
                'src/override.c': hashlib.sha256(OVERRIDE).hexdigest(),
            },
            'test_resource_pack': 'test-pack',
        }
        (self.fixture / 'manifest.json').write_text(json.dumps(manifest))

    def prepare(self, output=None, assets_output=None):
        if output is None:
            output = self.root / 'output'
        command = [sys.executable, str(self.script), '--family', 'green-trail',
                   '--output', str(output)]
        if assets_output is not None:
            command += ['--assets-output', str(assets_output)]
        return subprocess.run(command, capture_output=True, text=True)

    def test_source_only_prints_exact_historical_rebuild_command(self):
        self.builder.write_text("raise AssertionError('unexpected asset rebuild')\n")
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Required historical asset pack: test-pack', result.stdout)
        self.assertIn('prototype/rebuild_retired_hd_pack.py test-pack --output ABS_NEW_EXTERNAL_DIRECTORY', result.stdout)
        self.assertIn('--assets-output ABS_NEW_EXTERNAL_DIRECTORY', result.stdout)
        self.assertFalse((self.repo / 'assets').exists())

    def test_optional_assets_rebuild_uses_exact_recipe_and_external_path(self):
        assets = self.root / 'historical-assets'
        result = self.prepare(assets_output=assets)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((assets / 'build-call.json').read_text()), {
            'repo': str(self.repo), 'pack': 'test-pack', 'output': str(assets),
        })
        self.assertEqual((assets / 'frozen.hda').read_bytes(), b'archived pack bytes')
        self.assertEqual((self.root / 'output/src/override.c').read_bytes(), OVERRIDE)
        self.assertIn('Rebuilt exact archived asset pack: ' + str(assets), result.stdout)
        self.assertFalse((self.repo / 'assets').exists())

    def test_asset_output_rejects_relative_existing_checkout_and_overlap(self):
        existing = self.root / 'existing-assets'
        existing.mkdir()
        (existing / 'keep').write_bytes(b'unchanged')
        cases = (
            ('relative', Path('relative-assets'), self.root / 'relative-sources', 'absolute'),
            ('existing', existing, self.root / 'existing-sources', 'new resource-pack output'),
            ('checkout', self.repo / 'retired-assets', self.root / 'checkout-sources', 'outside'),
            ('same', self.root / 'same', self.root / 'same', 'separate'),
            ('child', self.root / 'sources/pack', self.root / 'sources', 'separate'),
            ('parent', self.root / 'pack', self.root / 'pack/sources', 'separate'),
        )
        for label, assets, output, error in cases:
            with self.subTest(case=label):
                result = self.prepare(output, assets)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(error, result.stderr)
                self.assertFalse(output.exists())
                if assets != existing:
                    self.assertFalse(assets.exists())
        self.assertEqual((existing / 'keep').read_bytes(), b'unchanged')

    def test_asset_output_rejects_symlink_into_checkout(self):
        link = self.root / 'external-link'
        try:
            link.symlink_to(self.repo / 'new-assets', target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('Directory symlinks unavailable')
        result = self.prepare(assets_output=link)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Keep resource-pack output outside', result.stderr)
        self.assertFalse((self.repo / 'new-assets').exists())
        self.assertFalse((self.root / 'output').exists())

    def test_invalid_sources_do_not_start_asset_reconstruction(self):
        self.builder.write_text("raise AssertionError('unexpected asset rebuild')\n")
        cases = (
            ('production', BASE.replace(b'1', b'3'), OVERRIDE, 'Production base changed'),
            ('override', BASE, OVERRIDE + b'changed', 'AssertionError'),
        )
        for label, production, override, error in cases:
            with self.subTest(case=label):
                self.configure(production=production, override=override)
                assets = self.root / (label + '-assets')
                output = self.root / (label + '-sources')
                result = self.prepare(output, assets)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(error, result.stderr)
                self.assertNotIn('unexpected asset rebuild', result.stderr)
                self.assertFalse(assets.exists())
                self.assertFalse(output.exists())

    def test_unknown_historical_pack_fails_without_modern_fallback(self):
        manifest_path = self.fixture / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['test_resource_pack'] = 'missing-frozen-pack'
        manifest_path.write_text(json.dumps(manifest))
        assets = self.root / 'assets'
        result = self.prepare(assets_output=assets)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Historical resource-pack rebuild failed: Unknown retired pack: missing-frozen-pack', result.stderr)
        self.assertFalse(assets.exists())
        self.assertFalse((self.root / 'output').exists())

    def assert_prepares_unchanged(self, production, expected):
        self.configure(production=production, expected=expected)
        output = self.root / hashlib.sha256(production + expected).hexdigest()
        result = self.prepare(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((output / 'src/base.c').read_bytes(), production)
        self.assertEqual((output / 'src/override.c').read_bytes(), OVERRIDE)

    def test_raw_lf_hash(self):
        self.assert_prepares_unchanged(BASE, BASE)

    def test_raw_crlf_hash(self):
        crlf = BASE.replace(b'\n', b'\r\n')
        self.assert_prepares_unchanged(crlf, crlf)

    def test_lf_checkout_against_windows_manifest(self):
        self.assert_prepares_unchanged(BASE, BASE.replace(b'\n', b'\r\n'))

    def test_crlf_checkout_against_lf_manifest(self):
        self.assert_prepares_unchanged(BASE.replace(b'\n', b'\r\n'), BASE)

    def test_mixed_line_endings_against_windows_manifest(self):
        mixed = BASE.replace(b'\n', b'\r\n', 1)
        self.assert_prepares_unchanged(mixed, BASE.replace(b'\n', b'\r\n'))

    def test_reviewed_binding_restores_archived_source(self):
        for label, newline, expected_newline in (
            ('lf-checkout', b'\n', b'\r\n'),
            ('crlf-checkout', b'\r\n', b'\r\n'),
            ('lf-manifest', b'\n', b'\n'),
        ):
            with self.subTest(case=label):
                archived = BASE.replace(b'\n', newline)
                production = (BASE + BINDING).replace(b'\n', newline)
                self.configure(production=production,
                               expected=BASE.replace(b'\n', expected_newline),
                               rel='src/tyrian2.c')
                output = self.root / label
                result = self.prepare(output)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((output / 'src/tyrian2.c').read_bytes(), archived)
                self.assertEqual((self.repo / 'src/tyrian2.c').read_bytes(), production)
                self.assertEqual((output / 'src/override.c').read_bytes(), OVERRIDE)

    def test_binding_allowlist_rejects_duplicates_and_other_changes(self):
        changes = {
            'duplicate': BASE + BINDING * 2,
            'mixed-ending-duplicate': BASE + BINDING + BINDING.replace(b'\n', b'\r\n'),
            'content-edit': BASE.replace(b'1', b'3') + BINDING,
            'other-added-line': BASE + b'int z = 3;\n' + BINDING,
            'wrong-indent': BASE + BINDING[1:],
            'trailing-space': BASE + BINDING.replace(b';\n', b'; \n'),
            'missing-newline': BASE + BINDING.rstrip(b'\n'),
            'bare-cr': (BASE + BINDING).replace(b'\n', b'\r'),
            'bom': b'\xef\xbb\xbf' + BASE + BINDING,
        }
        for label, production in changes.items():
            with self.subTest(case=label):
                self.configure(production=production, rel='src/tyrian2.c')
                output = self.root / label
                result = self.prepare(output)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Production base changed', result.stderr)
                self.assertFalse(output.exists())

    def test_binding_allowlist_does_not_apply_to_other_files(self):
        self.configure(production=BASE + BINDING)
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Production base changed', result.stderr)

    def test_enemy_hooks_restore_exact_archival_bytes(self):
        cases = (
            ('enemy-only', 'src/tyrian2.c', BASE + ENEMY_BRANCH,
             BASE + ORIGINAL_ENEMY_DRAW),
            ('cloud-and-enemy', 'src/tyrian2.c', BASE + BINDING + ENEMY_BRANCH,
             BASE + ORIGINAL_ENEMY_DRAW),
            ('enemy-declaration', 'src/entity_draw.h', BASE + ENEMY_DECLARATION, BASE),
        )
        for label, rel, production, archived in cases:
            for newline in (b'\n', b'\r\n'):
                with self.subTest(case=label, newline=newline):
                    data = production.replace(b'\n', newline)
                    self.configure(production=data, expected=archived, rel=rel)
                    output = self.root / (label + ('-lf' if newline == b'\n' else '-crlf'))
                    result = self.prepare(output)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual((output / rel).read_bytes(), archived.replace(b'\n', newline))
                    self.assertEqual((self.repo / rel).read_bytes(), data)
                    self.assertEqual((output / 'src/override.c').read_bytes(), OVERRIDE)

    def test_enemy_hook_allowlist_rejects_unknown_or_duplicate_changes(self):
        cases = (
            ('duplicate-branch', 'src/tyrian2.c', BASE + ENEMY_BRANCH * 2,
             BASE + ORIGINAL_ENEMY_DRAW),
            ('mixed-duplicate-branch', 'src/tyrian2.c', BASE + ENEMY_BRANCH + ENEMY_BRANCH.replace(b'\n', b'\r\n'),
             BASE + ORIGINAL_ENEMY_DRAW),
            ('changed-index', 'src/tyrian2.c', BASE + ENEMY_BRANCH.replace(b'113', b'114'),
             BASE + ORIGINAL_ENEMY_DRAW),
            ('changed-existing-code', 'src/tyrian2.c', BASE.replace(b'1', b'3') + BINDING + ENEMY_BRANCH,
             BASE + ORIGINAL_ENEMY_DRAW),
            ('duplicate-declaration', 'src/entity_draw.h', BASE + ENEMY_DECLARATION * 2, BASE),
            ('changed-declaration', 'src/entity_draw.h', BASE + ENEMY_DECLARATION.replace(b'unsigned int', b'int'), BASE),
            ('extra-header-edit', 'src/entity_draw.h', BASE + ENEMY_DECLARATION + b'int extra;\n', BASE),
            ('wrong-file', 'src/base.c', BASE + ENEMY_DECLARATION, BASE),
        )
        for label, rel, production, archived in cases:
            with self.subTest(case=label):
                self.configure(production=production, expected=archived, rel=rel)
                output = self.root / label
                result = self.prepare(output)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Production base changed', result.stderr)
                self.assertFalse(output.exists())

    def test_green_review_restores_current_production_binding(self):
        production = BASE + BINDING + ENEMY_BRANCH
        self.configure(production=production, expected=BASE + ORIGINAL_ENEMY_DRAW,
                       rel='src/tyrian2.c')
        renderer = b'/* CURRENT */\n/* Display grouping requires */\nbool green_blend=explosion_blend&&a->index>=78&&a->index<=84;\n'
        archive = b'/* Private read-only green-trail matrix observer; */\n/* OBSERVER */\n/* Display grouping requires */\n'
        (self.repo / 'src/render_mirror.c').write_bytes(renderer)
        (self.fixture / 'overrides/src/render_mirror.c').write_bytes(archive)
        manifest_path = self.fixture / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['tested_exact_source_overrides']['src/render_mirror.c'] = hashlib.sha256(archive).hexdigest()
        archive_header = b'void ae_before(SDL_Surface*,int,int,Sprite2_array,unsigned int,int);\nvoid ae_after_mirror(bool);\nvoid ae_after_original(void);\n'
        (self.fixture / 'overrides/src/render_mirror.h').write_bytes(archive_header)
        manifest['tested_exact_source_overrides']['src/render_mirror.h'] = hashlib.sha256(archive_header).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
        current_entity = ('\tbool mirrored=render_mirror_entity(target,x,y,bank,index,style,layout);\n'
                          '\tgame_probe_draw(role,index,x,y,style,layout,mirrored);\n'
                          '\tif (layout == ENTITY_QUAD)\n'
                          '\trender_mirror_entity_end();\n'
                          'void draw_enemy_shot_sprite2(void) { render_mirror_enemy_shot(); }\n')
        (self.repo / 'src/entity_draw.c').write_text(current_entity)
        (self.repo / 'src/entity_draw.h').write_bytes(BASE + ENEMY_DECLARATION)
        current_render_header = b'bool render_mirror_enemy_shot(void);\n'
        (self.repo / 'src/render_mirror.h').write_bytes(current_render_header)
        review = self.script.with_name('prepare-green-review.py')
        shutil.copy2(PREPARE.with_name(review.name), review)
        output = self.root / 'review'
        result = subprocess.run([sys.executable, str(review), '--output', str(output)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((output / 'src/tyrian2.c').read_bytes(), production)
        prepared_renderer = (output / 'src/render_mirror.c').read_text()
        self.assertIn('/* CURRENT */', prepared_renderer)
        self.assertIn('/* OBSERVER */', prepared_renderer)
        self.assertIn('OT_GREEN_POINT_BASELINE', prepared_renderer)
        self.assertEqual((output / 'src/entity_draw.h').read_bytes(), BASE + ENEMY_DECLARATION)
        self.assertIn(current_render_header.decode(), (output / 'src/render_mirror.h').read_text())
        prepared_entity = (output / 'src/entity_draw.c').read_text()
        self.assertIn('void draw_enemy_shot_sprite2(void) { render_mirror_enemy_shot(); }', prepared_entity)
        for hook in ('ae_before(target', 'ae_after_mirror(mirrored)', 'ae_after_original()', 'green-head-draws.tsv'):
            self.assertEqual(prepared_entity.count(hook), 1)

    def test_content_changes_are_rejected_before_creating_output(self):
        changes = {
            'value': BASE.replace(b'1', b'3'),
            'whitespace': BASE.replace(b'int x', b'int  x'),
            'trailing_space': BASE.replace(b';\n', b'; \n'),
            'missing_final_newline': BASE.rstrip(b'\n'),
            'bom': b'\xef\xbb\xbf' + BASE,
            'bare_cr': BASE.replace(b'\n', b'\r'),
            'extra_cr': BASE.replace(b'\n', b'\r\r\n'),
        }
        for label, production in changes.items():
            with self.subTest(change=label):
                self.configure(production=production)
                output = self.root / label
                result = self.prepare(output)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Production base changed', result.stderr)
                self.assertFalse(output.exists())

    def test_override_hashes_stay_byte_exact(self):
        for label, override in {
            'line_endings': OVERRIDE.replace(b'\r\n', b'\n'),
            'content': OVERRIDE.replace(b'exact', b'changed'),
            'reviewed_binding': OVERRIDE + BINDING,
            'reviewed_enemy_declaration': OVERRIDE + ENEMY_DECLARATION,
        }.items():
            with self.subTest(change=label):
                self.configure(override=override)
                result = self.prepare(self.root / label)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('AssertionError', result.stderr)

    def test_existing_output_is_rejected(self):
        output = self.root / 'existing'
        output.mkdir()
        result = self.prepare(output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Choose a new fixture output directory', result.stderr)

    def test_output_inside_checkout_is_rejected(self):
        output = self.repo / 'fixture-output'
        result = self.prepare(output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Keep fixture output outside', result.stderr)
        self.assertFalse(output.exists())


class ArchivedResourceManifestTests(unittest.TestCase):
    def test_frozen_family_pack_names_and_reconstruction_contract(self):
        prefix = 'packed-blue-four-foundation-type10-death-effects-'
        expected = {
            'white-smoke-v1': prefix + 'white-smoke-v1-test',
            'shield-v1': prefix + 'white-smoke-shield-v1-test',
            'green-trail': prefix + 'white-smoke-shield-green-v1-test',
        }
        for family, pack in expected.items():
            with self.subTest(family=family):
                manifest = json.loads((PREPARE.parent / 'effects' / family / 'manifest.json').read_text())
                self.assertEqual(manifest['test_resource_pack'], pack)
                rebuild = manifest['test_resource_pack_rebuild']
                self.assertEqual(rebuild['recipe_manifest'], 'assets/hd/manifest.json')
                self.assertEqual(rebuild['recipe_section'], 'retired_packs')
                self.assertEqual(rebuild['builder'], 'prototype/rebuild_retired_hd_pack.py')
                self.assertEqual(rebuild['output_policy'], 'new_absolute_directory_outside_checkout')
                self.assertTrue(manifest['diagnostic_only_never_installed'])


if __name__ == '__main__':
    unittest.main()
