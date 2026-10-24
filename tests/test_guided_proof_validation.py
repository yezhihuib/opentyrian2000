"""Fresh finite Guided proofs, with one derivation per invocation.

The selection-change guard is deliberately narrower than an atomic filesystem
snapshot. Mutations happen between calls except for the explicit injected guard
case. No synthetic edit here qualifies artwork or changes a historical oracle.
"""
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import current_guided_compatibility as c
import accepted_later_changes as a


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()


def previous_proof(root):
    """Exact pre-optimization algorithm, kept only as an output comparator."""
    mapping = c.load(root)
    selected, pngs, _ = c.generate(root, c.read(root, c.SELECTION))
    names = {c.SELECTION, c.MAPPING, selected['recipe']['path']} | set(pngs)
    names |= {v['source_path'] for v in mapping.values()}
    names |= {row['source_png'] for row in selected['masters']}
    assets = {n: {'sha256': a.sha(c.read(root, n)), 'mode': '100644'}
              for n in names if n.startswith('assets/')}
    return dict(assets=assets, paths=names-{c.MAPPING}, mapping=mapping,
                header_sha256=a.sha(c.read(root, c.HEADER)))


class GuidedProofValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='guided-proof-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        paths = c.input_paths(ROOT) | {c.MAPPING, c.HEADER}
        for name in paths:
            self.write(name, (ROOT/name).read_bytes())

    def write(self, name, raw):
        path = self.root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def proof(self):
        return a.verified_current_guided(self.root)

    def test_exact_previous_proof_and_finite_paths(self):
        proof = self.proof()
        self.assertEqual(proof, previous_proof(self.root))
        expected = {c.SELECTION, c.INPUT_ROOT+'/recipe.json'}
        expected |= {c.INPUT_ROOT+f'/master-{i}.png' for i in (19, 171, 20, 21)}
        expected |= {c.INPUT_ROOT+f'/derived/bullet-{i}-8.png' for i in (19, 171, 20, 21)}
        expected |= {c.ROOT+f'/bullet-{i}-8.hda' for i in (19, 171, 20, 21)}
        self.assertEqual(proof['paths'], expected)
        self.assertEqual(len(proof['assets']), 5)
        self.assertEqual(set(proof['mapping']),
                         {f'assets/gameplay/bullet-{i}-8.hda' for i in (19,171,20,21)})
        self.assertEqual(proof['header_sha256'], c.sha(c.read(self.root,c.HEADER)))

    def test_one_derivation_each_call_without_cache(self):
        with patch.object(c, 'generate', wraps=c.generate) as generate:
            first = self.proof()
            self.assertEqual(generate.call_count, 1)
            self.assertEqual(self.proof(), first)
            self.assertEqual(generate.call_count, 2)

    def assert_fresh_rejection(self, names):
        before = self.proof()
        for name in names:
            with self.subTest(path=name):
                original = c.read(self.root, name)
                try:
                    self.write(name, original+b'broken')
                    with self.assertRaises((ValueError, AssertionError)):
                        self.proof()
                finally:
                    self.write(name, original)
                self.assertEqual(self.proof(), before)

    def test_master_and_recipe_mutations_are_fresh(self):
        self.assert_fresh_rejection([c.INPUT_ROOT+f'/master-{i}.png' for i in c.SELECTORS]
                                    + [c.INPUT_ROOT+'/recipe.json'])

    def test_derived_png_mutations_are_fresh(self):
        self.assert_fresh_rejection(sorted(c.generated_paths()))

    def test_hda_mutations_are_fresh(self):
        self.assert_fresh_rejection([c.ROOT+'/'+c.name(*pair) for pair in c.PAIRS])

    def test_mapping_header_selection_mutations_are_fresh(self):
        self.assert_fresh_rejection([c.MAPPING, c.HEADER, c.SELECTION])

    def test_coherent_changed_master_and_png_still_reject_stale_hda(self):
        original = {p.relative_to(self.root).as_posix(): p.read_bytes()
                    for p in self.root.rglob('*') if p.is_file()}
        before = self.proof()
        selected = json.loads(c.read(self.root, c.SELECTION))
        row = selected['masters'][0]
        with Image.open(io.BytesIO(c.read(self.root, row['source_png']))) as im:
            r,g,b,alpha = im.split()
            changed = Image.merge('RGBA', (r.point(lambda x: (x+37)%256),g,b,alpha))
        stream = io.BytesIO(); changed.save(stream, format='PNG')
        self.write(row['source_png'], stream.getvalue())
        row['source_sha256'] = c.sha(stream.getvalue())
        candidate = copy.deepcopy(selected)
        candidate.pop('resources'); candidate['schema'] = c.CANDIDATE_SCHEMA
        updated, pngs, blobs = c.generate(self.root, encode(candidate), candidate=True)
        self.assertNotEqual(blobs[c.PAIRS[0]], c.read(self.root,c.ROOT+'/'+c.name(*c.PAIRS[0])))
        for name, raw in pngs.items(): self.write(name, raw)
        self.write(c.SELECTION, encode(updated))
        with self.assertRaisesRegex(ValueError, 'Guided HDA does not match'):
            self.proof()
        for name, raw in original.items(): self.write(name, raw)
        self.assertEqual(self.proof(), before)

    def test_selection_change_during_load_is_rejected(self):
        raw = c.read(self.root,c.SELECTION)
        load = c.load
        def changing_load(root):
            result = load(root)
            self.write(c.SELECTION, raw+b' ')
            return result
        with patch.object(c, 'load', side_effect=changing_load):
            with self.assertRaisesRegex(ValueError, 'selection changed during current proof'):
                self.proof()
        self.write(c.SELECTION, raw)
        self.assertEqual(self.proof(), previous_proof(self.root))


if __name__ == '__main__':
    unittest.main()
