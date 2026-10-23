"""Independent source guards for the bounded NEWSHF compositor extension.

These checks do not substitute for actual native rendering tests. The immutable
identity prototype baseline remains the authority for old gameplay and scope.
"""
from pathlib import Path
import json
import subprocess
import unittest
import accepted_later_changes as projection
from test_newshf168_v4_selection import verify_assignments

ROOT = Path(__file__).resolve().parents[1]
BASE = '3ce35baa60db9d561fb946b16cfae14891d691d3'


def baseline(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def body(source, name):
    # These specific predicates have no string literals containing braces.
    start = source.index(f'static bool {name}(void)')
    opening = source.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


class BoundedCompositorGuards(unittest.TestCase):
    def test_native_gameplay_and_indexed_blits_unchanged(self):
        for path in ('src/tyrian2.c', 'src/sprite.c'):
            with self.subTest(path=path):
                self.assertEqual(projection.project_source("enemy-reuse", path, (ROOT / path).read_bytes()), baseline(path))

    def test_existing_scene_permissions_not_widened(self):
        path = 'src/render_mirror.c'
        old, new = baseline(path).decode(), (ROOT / path).read_text()
        for name in ('asteroid1_level_scope', 'asteroid1_scope',
                     'normal15_scope', 'manual_hd_scope', 'mirror_enabled'):
            with self.subTest(predicate=name):
                self.assertEqual(body(new, name), body(old, name))

    def test_prior_art_preserved_and_current_revision_explicit(self):
        directory = 'authoring-inputs/enemies/newshf-phase-a/'
        manifest = json.loads(baseline(directory + 'manifest.json'))
        self.assertEqual(len(manifest['art']), 9)
        paths = [directory + art['file'] for art in manifest['art']]
        paths += [directory + name for name in
                  ('manifest.json', 'provenance.json', 'report.json')]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual((ROOT / "docs/newshf-fine-v2-corrected-poses/historical-mislabeled-v1" / Path(path).name).read_bytes(), baseline(path))
        current = json.loads((ROOT / directory / "manifest.json").read_bytes())
        self.assertEqual(current["identity"], manifest["identity"])
        verify_assignments(current, {a["file"]: (ROOT / directory / a["file"]).read_bytes() for a in current["art"]})

    def test_original_identity_pins_not_redefined(self):
        path = 'src/newshf_prototype_pins.h'
        self.assertEqual((ROOT / path).read_bytes(), baseline(path))

    def test_original_source_contract_negative_tests_retained(self):
        for path in ('tests/test_newshf_phase_a.py',
                     'tests/test_newshf_prototype_pins.py'):
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_bytes(), baseline(path))


if __name__ == '__main__':
    unittest.main()
