"""Bounded authoring/packaging tests; synthetic art, no game/data/profile activity."""
import contextlib
import copy
import hashlib
import io
import json
import os
import shutil
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
from PIL import Image
import build_current_craft267 as b
import build_current_art as global_builder
import package_runtime
from current_art_policy import PROFILES, profile
from current_craft267_compatibility import HEADER, SIZE
READ_ONLY = os.environ.get('CRAFT267_READ_ONLY_TESTS') == '1'
WRITE_SKIP = 'Actual fixture replacement blocked by WinError 5; no directory/tool workaround attempted'

# Independent test allowlist: never derive the expected view from its composer.
VIEW_CRAFT_NAME = 'enemy-newsh2-267-8.hda'
VIEW_SIDEKICKS = {
    1260152: 'option-marlo-bank9-152-8.hda',
    1290224: 'option-plasma-bank9-224-8.hda',
    1290243: 'option-plasma-bank9-243-8.hda',
    1290262: 'option-plasma-bank9-262-8.hda',
    1290281: 'option-plasma-bank9-281-8.hda',
    1290300: 'option-plasma-bank9-300-8.hda',
}
VIEW_FAMILIES = {
    'talon': 13, 'rotor': 8, 'green': 11, 'shield': 22, 'hitflare': 7,
    'white_smoke': 7, 'small_explosion': 12, 'pulse': 5, 'vulcan': 2,
    'cash25': 7, 'cash50': 7, 'cash75': 7, 'gem100': 6, 'gem250': 6,
    'tank-shell': 2, 'enemy-energy': 7, 'sidekick-body': 6, 'craft267': 1,
    'hud': 6, 'charge-body': 9, 'mint-front-body': 4, 'plasma-projectile': 6,
    'front-multi': 8, 'enemy-orb': 4, 'protron': 4,
}


def independent_current_overlays(case, root):
    """Read declared canonical bytes directly, never the production composer/loaders."""
    overlays = {}
    runtime = {r['destination']: r for r in json.loads((root/b.RUNTIME).read_bytes())['files']}
    for family, count in VIEW_FAMILIES.items():
        mapping = json.loads((root/f'packaging/current-{family}-compatibility.json').read_bytes())
        case.assertEqual(len(mapping['files']), count)
        for row in mapping['files']:
            if family == 'enemy-orb' and row['identity'] in (1420112,1420113):
                continue
            if family == 'protron' and row['identity'] == 1470227:
                continue
            destinations = row['destinations'] if family == 'hud' else [row['destination']]
            gameplay = [d for d in destinations if d.startswith('assets/gameplay/')]
            case.assertEqual(len(gameplay), 1)
            destination = gameplay[0]
            name = destination[len('assets/gameplay/'):]
            case.assertNotIn('/', name)
            case.assertNotIn(name, overlays)
            data = (root/row['source_path']).read_bytes()
            case.assertEqual(hashlib.sha256(data).hexdigest(), row['sha256'])
            case.assertEqual(runtime[destination]['source_path'], row['source_path'])
            case.assertEqual(runtime[destination]['sha256'], row['sha256'])
            overlays[name] = data
    case.assertEqual(len(overlays), 174)
    # Independent literal geometry and PNG decoding; no production converter.
    pulse = json.loads((root/'assets/hd/authoring/pulse-current.json').read_bytes())
    case.assertEqual([r['identity'] for r in pulse['resources']], [80058, 80059, 80060, 80062, 80165])
    for row in pulse['resources']:
        source = (root/row['source_png']).read_bytes()
        case.assertEqual(hashlib.sha256(source).hexdigest(), row['source_sha256'])
        with Image.open(io.BytesIO(source)) as image:
            case.assertEqual((image.mode, image.size), ('RGBA', (96, 112)))
            identity = row['identity']
            expected = struct.pack('<4s6I', b'HDR1', identity, 8, 12, 14,
                                   0xffffffff if identity == 80059 else 0, 0) + image.tobytes()
        case.assertEqual(overlays[f'bullet-{identity-80000}-8.hda'], expected)
    return overlays


def assert_current_view_bytes(case, actual, frozen, overlays):
    case.assertTrue({VIEW_CRAFT_NAME, *VIEW_SIDEKICKS.values()}.issubset(overlays))
    expected = dict(frozen)
    expected.update(overlays)
    case.assertEqual(actual, expected)


class InjectedReplaceFailure(OSError):
    def __init__(self, boundary):
        self.boundary = boundary
        super().__init__(f'injected replace failure at boundary {boundary}')


class ReplaceFault:
    def __init__(self, replace, boundary):
        self.replace = replace
        self.boundary = boundary
        self.calls = 0
        self.hits = []

    def __call__(self, source, target):
        self.calls += 1
        if self.calls == self.boundary:
            self.hits.append(self.calls)
            raise InjectedReplaceFailure(self.boundary)
        return self.replace(source, target)


def case_failed(case):
    """Fail closed if the runner cannot expose ordinary unittest outcomes."""
    result = getattr(getattr(case, '_outcome', None), 'result', None)
    if result is None or not all(hasattr(result, key) for key in ('errors', 'failures')):
        return True
    return (any(test is case or getattr(test, 'test_case', None) is case
                for test, _ in result.errors + result.failures)
            or case in getattr(result, 'unexpectedSuccesses', ()))


def png(mode='RGBA', size=(192, 224), animated=False):
    out = io.BytesIO()
    im = Image.new(mode, size, (37, 53, 71, 127) if mode == 'RGBA' else (37, 53, 71))
    if animated:
        im.save(out, format='PNG', save_all=True, append_images=[Image.new(mode, size, (19, 23, 29, 255))], duration=10)
    else:
        im.save(out, format='PNG')
    return out.getvalue()


def rgba16_png():
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind+data) & 0xffffffff)
    header = struct.pack('>IIBBBBB', 192, 224, 16, 6, 0, 0, 0)
    pixels = (b'\0' + struct.pack('>4H', 100, 200, 300, 65535)*192)*224
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b'')


class Craft267AuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Same default temp location; no finalizer may silently chmod/remove a
        # failed fixture. Setup errors also leave the allocated tree intact.
        cls._preserve_fixture = True
        cls.base = Path(tempfile.mkdtemp(prefix='craft267-tests-'))
        print(f'Private fixture allocated: {cls.base}', flush=True)
        cls.root = cls.base/'repo'
        _, names = b.closure(ROOT)
        names.add(b.SELECTION)
        names.add('assets/hd/README.md')
        # Historical bootstrap evidence is not the editable current selection.
        names.add('assets/hd/source/enemy-newsh2-267-8-60d4dcf1f760.png')
        for f in PROFILES:
            select = profile(f)['selection']
            names.add(select)
            names.update(row['source_png'] for row in json.loads((ROOT/select).read_bytes())['resources'])
        for f in ('tank-shell', 'enemy-energy', 'craft267', 'sidekick-body'):
            select = f'assets/hd/authoring/{f}-current.json'
            names.add(select)
            names.update(row['source_png'] for row in json.loads((ROOT/select).read_bytes())['resources'])
        from current_enemy_energy_compatibility import MASK_POLICY
        names.update(row[0] for row in MASK_POLICY.values())
        import current_hud_recipe
        select = 'assets/hd/authoring/hud/current.json'
        names.add(select)
        hud = json.loads((ROOT/select).read_bytes())
        names.update(row['path'] for rows in hud['resources'].values() for row in rows)
        names.update(row['path'] for row in current_hud_recipe.FIXED_INPUTS.values())
        for name in b.BASES.values():
            names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'assets/hd/packs'/name).rglob('*') if p.is_file())
        cls.initial = {n:(ROOT/n).read_bytes() for n in sorted(names)}
        print(f'Private fixture: {len(names)} files, {sum(map(len, cls.initial.values()))} bytes', flush=True)
        for n, data in cls.initial.items():
            p = cls.root/n
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        print('Private fixture ready; no game/data/profile inputs', flush=True)
        cls._preserve_fixture = False

    @classmethod
    def tearDownClass(cls):
        if cls._preserve_fixture:
            print(f'Fixture retained after failure: {cls.base}', flush=True)
            return
        try:
            # Default rmtree raises on refusal; no permission-reset callback.
            shutil.rmtree(cls.base)
        except BaseException:
            cls._preserve_fixture = True
            print(f'Fixture cleanup stopped; retained: {cls.base}', flush=True)
            raise

    def setUp(self):
        if type(self)._preserve_fixture:
            self.skipTest('Prior failure retained the fixture; no further access')
        self.count = 0

    def tearDown(self):
        cls = type(self)
        if case_failed(self):
            cls._preserve_fixture = True
        if cls._preserve_fixture:
            print(f'Fixture retained without restoration: {cls.base}', flush=True)
            return
        try:
            self._restore_fixture()
        except BaseException:
            cls._preserve_fixture = True
            print(f'Fixture restoration stopped; retained: {cls.base}', flush=True)
            raise

    def _restore_fixture(self):
        # Only this class's private fixture tree; never source or user artifacts.
        for p in sorted(self.root.rglob('*'), reverse=True):
            n = p.relative_to(self.root).as_posix()
            if p.is_file():
                if n not in self.initial:
                    p.unlink()
                elif p.read_bytes() != self.initial[n]:
                    p.write_bytes(self.initial[n])
            elif p.is_dir() and not any(p.iterdir()):
                p.rmdir()
        for n, data in self.initial.items():
            p = self.root/n
            if not p.exists():
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
        for p in self.base.iterdir():
            if p == self.root:
                continue
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()

    def selected(self):
        return json.loads((self.root/b.SELECTION).read_bytes())

    def synthetic(self, data=None):
        j = self.selected()
        j['version'] = 'synthetic267-v2'
        source = 'assets/hd/authoring/synthetic-craft267.png'
        data = png() if data is None else data
        (self.root/source).write_bytes(data)
        j['resources'][0].update(source_png=source, source_sha256=b.sha(data))
        return j

    def stage(self, selected):
        self.count += 1
        draft = self.base/f'draft-{self.count}.json'
        draft.write_bytes(b.encoded(selected))
        destination = self.base/f'stage-{self.count}'
        b.stage(self.root, draft, destination)
        return destination

    def snapshot(self):
        return {p.relative_to(self.root).as_posix():b.sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}

    def test_historical_bootstrap_exact_pixels_and_header(self):
        # Fixed repository-local history: remains valid after approved art changes,
        # with no dependency on local/private Git commits or a second authoring copy.
        source = 'assets/hd/source/enemy-newsh2-267-8-60d4dcf1f760.png'
        raw = (self.root/'assets/hd/packs'/b.BASES['preview']/b.NAME).read_bytes()
        self.assertEqual(len(raw), SIZE)
        self.assertEqual(raw[:28], HEADER)
        self.assertEqual(b.sha(raw), '60d4dcf1f76046c7d8e9f1f56495fce5affc4d919294334173d4a232430487a9')
        self.assertEqual(b.sha((self.root/source).read_bytes()), '1bace298e65167bcc51f3db30c9faab807593ae6c56aa43a74579c7f7fa47487')
        with Image.open(self.root/source) as im:
            self.assertEqual((im.mode, im.size), ('RGBA', (192, 224)))
            self.assertEqual(raw[28:], im.tobytes())
        for base in b.BASES.values():
            self.assertEqual(raw, (self.root/'assets/hd/packs'/base/b.NAME).read_bytes())

    def test_current_selected_png_pixels_header_and_existing_runtime_set(self):
        self.assertEqual(b.check(self.root)['status'], 'PASS')
        row = self.selected()['resources'][0]
        source = self.root/row['source_png']
        self.assertEqual(b.sha(source.read_bytes()), row['source_sha256'])
        with Image.open(source) as im:
            self.assertEqual((im.mode, im.size), ('RGBA', (192, 224)))
            # Independent literal header and decoded PNG, not production source_blob.
            expected = struct.pack('<4s6I', b'HDR1', 1010267, 8, 24, 28, 6, 7) + im.tobytes()
        raw = (self.root/b.CANONICAL).read_bytes()
        self.assertEqual(len(raw), 172060)
        self.assertEqual(raw, expected)
        runtime = json.loads((self.root/b.RUNTIME).read_bytes())
        self.assertEqual(len(runtime['files']), 1024)
        self.assertEqual(len(json.loads((self.root/b.REGISTRY).read_bytes())['resources']), 120)
        self.assertEqual({r['destination']:r for r in runtime['files']}[b.DESTINATION]['source_path'], b.CANONICAL)

    @unittest.skipIf(READ_ONLY, WRITE_SKIP)
    def test_single_source_stage_apply_package_and_both_preview_views(self):
        j = self.synthetic()
        before = self.snapshot()
        old_runtime = json.loads((self.root/b.RUNTIME).read_bytes())
        stage = self.stage(j)
        self.assertEqual(before, self.snapshot())
        second = self.stage(j)
        self.assertEqual((stage/'plan.json').read_bytes(), (second/'plan.json').read_bytes())
        b.apply(self.root, stage)
        self.assertEqual(b.check(self.root)['status'], 'PASS')
        # Decode independently, with literal geometry and known synthetic pixels.
        with Image.open(self.root/j['resources'][0]['source_png']) as image:
            self.assertEqual((image.mode, image.size), ('RGBA', (192, 224)))
            pixels = image.tobytes()
        self.assertEqual(pixels, bytes((37, 53, 71, 127)) * (192 * 224))
        raw = struct.pack('<4s6I', b'HDR1', 1010267, 8, 24, 28, 6, 7) + pixels
        self.assertNotEqual(raw, self.initial[b.CANONICAL])
        self.assertEqual(raw, (self.root/b.CANONICAL).read_bytes())
        overlays = independent_current_overlays(self, self.root)
        self.assertEqual(overlays[VIEW_CRAFT_NAME], raw)
        sidekick_selection = 'assets/hd/authoring/sidekick-body-current.json'
        self.assertEqual((self.root/sidekick_selection).read_bytes(), self.initial[sidekick_selection])
        sidekicks = json.loads(self.initial[sidekick_selection])['resources']
        self.assertEqual([row['identity'] for row in sidekicks], list(VIEW_SIDEKICKS))
        for row in sidekicks:
            identity = row['identity']
            name = VIEW_SIDEKICKS[identity]
            source = row['source_png']
            self.assertEqual((self.root/source).read_bytes(), self.initial[source])
            with Image.open(io.BytesIO(self.initial[source])) as image:
                self.assertEqual((image.mode, image.size), ('RGBA', (96, 112)))
                body = struct.pack('<4s6I', b'HDR1', identity, 8, 12, 14, 0, 0) + image.tobytes()
            protected = 'assets/hd/current-compat/sidekick-body/' + name
            self.assertEqual(body, self.initial[protected])
            self.assertEqual((self.root/protected).read_bytes(), self.initial[protected])
            overlays[name] = body
        allowed = {b.SELECTION, b.CANONICAL, b.MAPPING, b.RUNTIME}
        after = self.snapshot()
        self.assertEqual({p for p in before if before[p] != after[p]}, allowed)
        runtime = json.loads((self.root/b.RUNTIME).read_bytes())
        self.assertEqual(len(runtime['files']), 1024)
        self.assertEqual([r for r in runtime['files'] if r['destination'] != b.DESTINATION],
                         [r for r in old_runtime['files'] if r['destination'] != b.DESTINATION])
        for kind, base in b.BASES.items():
            target = self.base/f'view-{kind}'
            report = b.view(self.root, kind, target)
            self.assertEqual(report['files'], 650)
            self.assertEqual(len(report['current_overlays']), 174)
            frozen = {p.relative_to(self.root/'assets/hd/packs'/base).as_posix():p.read_bytes()
                        for p in (self.root/'assets/hd/packs'/base).rglob('*') if p.is_file()}
            self.assertEqual(set(report['current_overlays']), set(overlays))
            actual = {p.relative_to(target).as_posix():p.read_bytes() for p in target.rglob('*') if p.is_file()}
            assert_current_view_bytes(self, actual, frozen, overlays)
            self.assertEqual(len(set(frozen) - set(overlays)), 478)
        # The task forbids permission changes. Exercise real package copying and
        # fingerprints, explicitly suppressing its unrelated chmod operation.
        with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(Path, 'chmod', return_value=None):
            code = package_runtime.main(['--source-root', str(self.root), '--build', '--output', str(self.base/'runtime')])
        self.assertEqual(code, 0)
        self.assertEqual((self.base/'runtime'/b.DESTINATION).read_bytes(), raw)
        self.assertEqual(after, self.snapshot())

    @unittest.skipIf(READ_ONLY, WRITE_SKIP)
    def test_other_public_authoring_closures_preserve_craft267(self):
        b.apply(self.root, self.stage(self.synthetic()))
        self.assertEqual(global_builder.check(self.root, 'pulse')['status'], 'PASS')
        import build_current_hud, build_current_tank_shell, build_current_enemy_energy, build_current_sidekick_body
        initial = self.snapshot()
        protected = {p: digest for p, digest in initial.items() if p.startswith("assets/hd/current-compat/sidekick-body/") or p == "src/current_sidekick_body_payload_pins.h"}
        for builder in (build_current_hud, build_current_tank_shell, build_current_enemy_energy, build_current_sidekick_body):
            self.assertEqual(builder.check(self.root)['status'], 'PASS')
        final = self.snapshot()
        self.assertEqual(protected, {p: final[p] for p in protected})

    def test_identity_scope_and_selection_fields(self):
        original = self.selected()
        for identity in (1010269, 1010271, 1010268, 1010286, 1010287, 1020267, 1060267, 267, True):
            j = copy.deepcopy(original)
            j['resources'][0]['identity'] = identity
            with self.subTest(identity=identity), self.assertRaises(ValueError):
                b.selection(self.root, b.encoded(j))
        for field in ('role', 'bank', 'density', 'anchor', 'size', 'order'):
            j = copy.deepcopy(original)
            j['resources'][0][field] = 1
            with self.subTest(field=field), self.assertRaises(ValueError):
                b.selection(self.root, b.encoded(j))
        for rows in ([], original['resources']*2):
            j = copy.deepcopy(original)
            j['resources'] = rows
            with self.assertRaises(ValueError):
                b.selection(self.root, b.encoded(j))
        with self.assertRaises(ValueError):
            b.parse(b'{"schema":1,"schema":2}')

    def test_bad_png_mode_dimensions_animation_truncation_crc_and_trailing(self):
        valid = png()
        for data in (png('RGB'), png(size=(191,224)), png(size=(192,223)), png(animated=True), rgba16_png(), valid[:-1], valid+b'junk', valid[:40]+b'BAD!'+valid[44:]):
            j = self.synthetic(data)
            before = self.snapshot()
            with self.subTest(length=len(data)), self.assertRaises((ValueError, OSError)):
                self.stage(j)
            self.assertEqual(before, self.snapshot())

    def test_bad_sha_and_unsafe_source_paths(self):
        j = self.selected()
        j['resources'][0]['source_sha256'] = '0'*64
        with self.assertRaises(ValueError):
            b.selection(self.root, b.encoded(j))
        for value in ('../outside.png', '/outside.png', 'C:/outside.png', 'assets\\bad.png', 'assets//bad.png', 'assets/CON.png'):
            j = self.selected()
            j['resources'][0]['source_png'] = value
            with self.subTest(path=value), self.assertRaises(ValueError):
                b.selection(self.root, b.encoded(j))
        with self.assertRaises(ValueError):
            b.stage(self.root, self.root/b.SELECTION, self.root/'stage')

    def test_staged_bytes_and_plan_tampering_refused_before_writes(self):
        j = self.synthetic()
        for name in (b.SELECTION, b.CANONICAL, b.MAPPING, b.RUNTIME):
            stage = self.stage(j)
            target = stage/'files'/name
            target.write_bytes(target.read_bytes()+b'junk')
            before = self.snapshot()
            with self.subTest(name=name), self.assertRaises(ValueError):
                b.apply(self.root, stage)
            self.assertEqual(before, self.snapshot())
        stage = self.stage(j)
        plan = json.loads((stage/'plan.json').read_bytes())
        plan['files'][0]['after_sha256'] = '0'*64
        (stage/'plan.json').write_bytes(b.encoded(plan))
        before = self.snapshot()
        with self.assertRaises(ValueError):
            b.apply(self.root, stage)
        self.assertEqual(before, self.snapshot())

    @unittest.skipIf(READ_ONLY, WRITE_SKIP)
    def test_changed_source_installed_selection_and_tool_closure_are_stale(self):
        j = self.synthetic()
        stage = self.stage(j)
        p = self.root/j['resources'][0]['source_png']
        original = p.read_bytes()
        p.write_bytes(original+b'changed')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            b.apply(self.root, stage)
        self.assertEqual(before, self.snapshot())
        p.write_bytes(original)
        other = self.selected()
        other['version'] = 'another-installed-version'
        b.apply(self.root, self.stage(other))
        before = self.snapshot()
        with self.assertRaises(ValueError):
            b.apply(self.root, stage)
        self.assertEqual(before, self.snapshot())
        stage = self.stage(j)
        p = self.root/'scripts/build_current_craft267.py'
        p.write_bytes(p.read_bytes()+b'\n# tool changed\n')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            b.apply(self.root, stage)
        self.assertEqual(before, self.snapshot())

    def test_temporary_conflict_preflights_all_outputs(self):
        stage = self.stage(self.synthetic())
        p = self.root/(b.RUNTIME+b.SUFFIX)
        p.write_bytes(b'occupied')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            b.apply(self.root, stage)
        self.assertEqual(before, self.snapshot())

    @unittest.skipIf(READ_ONLY, WRITE_SKIP)
    def test_handled_replace_failure_at_each_boundary_rolls_back_every_byte(self):
        j = self.synthetic()
        stage = self.stage(j)
        before = self.snapshot()
        real = os.replace
        for boundary in range(1,5):
            fault = ReplaceFault(real, boundary)
            # Unexpected OS errors propagate immediately; a subTest must not
            # swallow them and continue accessing the failed fixture.
            with mock.patch.object(b.os, 'replace', side_effect=fault), self.assertRaises(InjectedReplaceFailure) as error:
                b.apply(self.root, stage)
            self.assertEqual(error.exception.boundary, boundary)
            self.assertEqual(fault.hits, [boundary])
            self.assertEqual(before, self.snapshot())
        b.apply(self.root, stage)
        self.assertEqual(b.check(self.root)['status'], 'PASS')

    def test_bad_mapping_geometry_length_missing_and_wrong_consumer(self):
        original = (self.root/b.CANONICAL).read_bytes()
        mapping = json.loads((self.root/b.MAPPING).read_bytes())
        for offset, value in ((4,1020267),(8,4),(12,12),(16,14),(20,0),(24,0)):
            raw = bytearray(original)
            struct.pack_into('<I', raw, offset, value)
            (self.root/b.CANONICAL).write_bytes(raw)
            mapping['files'][0]['sha256'] = b.sha(raw)
            (self.root/b.MAPPING).write_bytes(b.encoded(mapping))
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                b.load(self.root)
        for raw in (original[:-1], original+b'junk'):
            (self.root/b.CANONICAL).write_bytes(raw)
            mapping['files'][0]['sha256'] = b.sha(raw)
            (self.root/b.MAPPING).write_bytes(b.encoded(mapping))
            with self.assertRaises(ValueError):
                b.load(self.root)
        (self.root/b.CANONICAL).unlink()
        with self.assertRaises(ValueError):
            b.load(self.root)

    def test_view_refuses_existing_internal_or_changed_frozen_base(self):
        existing = self.base/'existing'
        existing.mkdir()
        (existing/'sentinel').write_bytes(b'previous complete view')
        for destination in (existing, self.root/'view'):
            with self.assertRaises(ValueError):
                b.view(self.root, 'preview', destination)
        self.assertEqual((existing/'sentinel').read_bytes(), b'previous complete view')
        p = self.root/'assets/hd/packs'/b.BASES['preview']/b.NAME
        p.write_bytes(p.read_bytes()+b'drift')
        target = self.base/'bad-view'
        with self.assertRaises(ValueError):
            b.view(self.root, 'preview', target)
        self.assertFalse(target.exists())

    def assert_view_preflight_rejects(self):
        target = self.base/'unpublished-parent'/'view'
        with mock.patch.object(Path, 'mkdir', side_effect=AssertionError('Preflight must not write')), \
                self.assertRaises((ValueError, FileNotFoundError)):
            b.view(self.root, 'preview', target)
        self.assertFalse(target.parent.exists())

    def test_current_views_all_canonical_hashes_and_478_frozen_members(self):
        overlays = independent_current_overlays(self, self.root)
        before = self.snapshot()
        for kind, base in b.BASES.items():
            target = self.base/f'current-{kind}'
            report = b.view(self.root, kind, target)
            frozen_root = self.root/'assets/hd/packs'/base
            frozen = {p.relative_to(frozen_root).as_posix(): p.read_bytes()
                      for p in frozen_root.rglob('*') if p.is_file()}
            actual = {p.relative_to(target).as_posix(): p.read_bytes()
                      for p in target.rglob('*') if p.is_file()}
            self.assertEqual((len(actual), len(overlays), len(set(frozen) - set(overlays))), (650, 174, 476))
            self.assertEqual(set(report['current_overlays']), set(overlays))
            assert_current_view_bytes(self, actual, frozen, overlays)
        self.assertEqual(self.snapshot(), before)

    @unittest.skipIf(READ_ONLY, WRITE_SKIP)
    def test_new_shared_vulcan_png_propagates_to_both_views(self):
        # Vulcan was byte-identical to history but lacked a propagation edge.
        policy = profile('vulcan')
        selected = json.loads((self.root/policy['selection']).read_bytes())
        selected['version'] = 'synthetic-preview-propagation'
        source = 'assets/hd/authoring/synthetic-preview-vulcan.png'
        source_bytes = png(size=(96, 112))
        (self.root/source).write_bytes(source_bytes)
        selected['resources'][0].update(source_png=source, source_sha256=hashlib.sha256(source_bytes).hexdigest())
        draft = self.base/'vulcan-draft.json'; draft.write_bytes(b.encoded(selected))
        stage = self.base/'vulcan-stage'
        global_builder.stage(self.root, draft, stage, 'vulcan')
        global_builder.apply(self.root, stage, 'vulcan')
        expected = struct.pack('<4s6I', b'HDR1', 80067, 8, 12, 14, 0, 0) + bytes((37, 53, 71, 127)) * (96*112)
        overlays = independent_current_overlays(self, self.root)
        self.assertEqual(overlays['bullet-67-8.hda'], expected)
        for kind, base in b.BASES.items():
            frozen_root = self.root/'assets/hd/packs'/base
            self.assertNotEqual((frozen_root/'bullet-67-8.hda').read_bytes(), expected)
            target = self.base/f'vulcan-{kind}'
            b.view(self.root, kind, target)
            frozen = {p.relative_to(frozen_root).as_posix(): p.read_bytes()
                      for p in frozen_root.rglob('*') if p.is_file()}
            actual = {p.relative_to(target).as_posix(): p.read_bytes()
                      for p in target.rglob('*') if p.is_file()}
            assert_current_view_bytes(self, actual, frozen, overlays)
            self.assertEqual(actual['bullet-67-8.hda'], expected)

    def test_every_missing_or_version_stale_mapping_rejected_before_publication(self):
        for family in VIEW_FAMILIES:
            target = self.root/f'packaging/current-{family}-compatibility.json'
            original = target.read_bytes()
            target.unlink()
            with self.subTest(family=family, defect='missing'):
                self.assert_view_preflight_rejects()
            changed = json.loads(original); changed['version'] += '-stale'
            target.write_bytes(b.encoded(changed))
            with self.subTest(family=family, defect='version'):
                self.assert_view_preflight_rejects()
            target.write_bytes(original)

    def test_mapping_duplicate_wrong_target_hash_and_missing_canonical_rejected(self):
        for family in ('pulse', 'tank-shell', 'enemy-energy', 'sidekick-body', 'hud'):
            mapping_path = self.root/f'packaging/current-{family}-compatibility.json'
            original = mapping_path.read_bytes()
            mapping = json.loads(original)
            canonical = self.root/mapping['files'][0]['source_path']
            data = canonical.read_bytes()
            for defect in ('duplicate', 'target', 'hash', 'missing-canonical', 'stale-canonical', 'duplicate-key'):
                changed = copy.deepcopy(mapping)
                if defect == 'duplicate': changed['files'].append(copy.deepcopy(changed['files'][0]))
                if defect == 'target':
                    if family == 'hud': changed['files'][0]['destinations'][1] = b.DESTINATION
                    else: changed['files'][0]['destination'] = b.DESTINATION
                if defect == 'hash': changed['files'][0]['sha256'] = '0'*64
                if defect == 'missing-canonical': canonical.unlink()
                if defect == 'stale-canonical': canonical.write_bytes(data[:-1] + bytes((data[-1] ^ 1,)))
                raw = b.encoded(changed)
                if defect == 'duplicate-key': raw = raw.replace(b'{', b'{"version":"duplicate",', 1)
                mapping_path.write_bytes(raw)
                with self.subTest(family=family, defect=defect):
                    self.assert_view_preflight_rejects()
                mapping_path.write_bytes(original)
                canonical.write_bytes(data)

    def test_selected_sources_and_self_consistent_stale_selection_rejected(self):
        for family in ('pulse', 'tank-shell', 'enemy-energy', 'sidekick-body', 'craft267', 'hud'):
            selection_path = self.root/('assets/hd/authoring/hud/current.json' if family == 'hud'
                                       else f'assets/hd/authoring/{family}-current.json')
            original = selection_path.read_bytes()
            selected = json.loads(original)
            row = selected['resources']['static'][0] if family == 'hud' else selected['resources'][0]
            source = self.root/row['path' if family == 'hud' else 'source_png']
            data = source.read_bytes()
            # A source changed without its selection hash must fail, even warm.
            source.write_bytes(data + b'changed')
            with self.subTest(family=family, defect='stale-hash'):
                self.assert_view_preflight_rejects()
            source.write_bytes(data)
            if family != 'hud':
                with Image.open(io.BytesIO(data)) as image:
                    image = image.copy()
                r, g, blue, alpha = image.getpixel((0, 0))
                image.putpixel((0, 0), ((r+1) % 256, g, blue, alpha))
                out = io.BytesIO(); image.save(out, format='PNG'); changed = out.getvalue()
                source.write_bytes(changed)
                row['source_sha256'] = hashlib.sha256(changed).hexdigest()
                selection_path.write_bytes(b.encoded(selected))
                with self.subTest(family=family, defect='selected-pixels-not-installed'):
                    self.assert_view_preflight_rejects()
                source.write_bytes(data)
                selection_path.write_bytes(original)

    def test_overlay_collision_and_missing_frozen_consumer_refuse_before_write(self):
        import current_art_compatibility
        real = current_art_compatibility.load
        def collision(root, family):
            rows = real(root, family)
            if family == 'pulse': rows[b.DESTINATION] = next(iter(rows.values()))
            return rows
        with mock.patch.object(current_art_compatibility, 'load', side_effect=collision):
            self.assert_view_preflight_rejects()
        with mock.patch.object(b, 'current_overlays', return_value={b.NAME: b'current', 'absent.hda': b'new'}):
            self.assert_view_preflight_rejects()

    def test_hud_config_hash_and_version_checked_without_rasterizing(self):
        import build_current_hud as hud
        with mock.patch.object(hud, 'render_resource', side_effect=AssertionError('Preview must not rebuild HUD')):
            self.assertEqual(len(b.current_overlays(self.root)), 174)
            selected_path = self.root/hud.SELECTION
            selected = json.loads(selected_path.read_bytes())
            record = selected['resources']['meters'][0]
            config = self.root/record['path']
            original = config.read_bytes()
            config.write_bytes(original + b' ')
            self.assert_view_preflight_rejects()
            # A draft with refreshed hashes but an unapplied version also fails.
            record['sha256'] = hashlib.sha256(config.read_bytes()).hexdigest()
            selected['version'] += '-not-applied'
            selected_path.write_bytes(b.encoded(selected))
            self.assert_view_preflight_rejects()

    @unittest.skipIf(READ_ONLY, WRITE_SKIP)
    def test_new_output_and_directory_creation_are_rolled_back_on_write_failure(self):
        before = self.snapshot()
        real = os.replace
        fault = ReplaceFault(real, 2)
        outputs = {'new-craft267-test/deep/first.hda': b'first',
                   'new-craft267-test/deep/second.hda': b'second'}
        with mock.patch.object(b.os, 'replace', side_effect=fault), self.assertRaises(InjectedReplaceFailure) as error:
            b.replace_batch(self.root, outputs)
        self.assertEqual(error.exception.boundary, 2)
        self.assertEqual(fault.hits, [2])
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root/'new-craft267-test').exists())

    def test_mapping_scope_rejects_extra_missing_wrong_role_or_target(self):
        original = json.loads((self.root/b.MAPPING).read_bytes())
        for kind in ('extra', 'missing', 'role', 'target', 'source', 'schema'):
            j = copy.deepcopy(original)
            if kind == 'extra': j['files'] *= 2
            if kind == 'missing': j['files'] = []
            if kind == 'role': j['files'][0]['identity'] = 1020267
            if kind == 'target': j['files'][0]['destination'] = 'assets/gameplay/enemy-newsh2-269-8.hda'
            if kind == 'source': j['files'][0]['source_path'] = '../other.hda'
            if kind == 'schema': j['schema'] = 'opentyrian-current-tank-shell-compatibility-v1'
            (self.root/b.MAPPING).write_bytes(b.encoded(j))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                b.load(self.root)

    def test_staging_propagates_only267_without_applying(self):
        j = self.synthetic()
        before = self.snapshot()
        stage = self.stage(j)
        self.assertEqual(before, self.snapshot())
        plan = json.loads((stage/'plan.json').read_bytes())
        self.assertEqual({r['path'] for r in plan['files']}, {b.SELECTION,b.CANONICAL,b.MAPPING,b.RUNTIME})
        raw = b.source_blob(self.root, j['resources'][0])
        self.assertEqual((stage/'files'/b.CANONICAL).read_bytes(), raw)
        old = json.loads((self.root/b.RUNTIME).read_bytes())
        new = json.loads((stage/'files'/b.RUNTIME).read_bytes())
        self.assertEqual(len(new['files']), 1024)
        self.assertEqual([r for r in old['files'] if r['destination'] != b.DESTINATION],
                         [r for r in new['files'] if r['destination'] != b.DESTINATION])
        self.assertEqual(next(r for r in new['files'] if r['destination'] == b.DESTINATION)['sha256'], b.sha(raw))

    def test_stale_source_and_tool_preflight_has_no_replace_call(self):
        j = self.synthetic()
        stage = self.stage(j)
        p = self.root/j['resources'][0]['source_png']
        original = p.read_bytes()
        p.write_bytes(original+b'changed')
        before = self.snapshot()
        with mock.patch.object(b.os, 'replace', side_effect=AssertionError('Unexpected write')), self.assertRaises(ValueError):
            b.apply(self.root, stage)
        self.assertEqual(before, self.snapshot())
        p.write_bytes(original)
        stage = self.stage(j)
        p = self.root/'scripts/build_current_craft267.py'
        p.write_bytes(p.read_bytes()+b'\n# tool drift\n')
        before = self.snapshot()
        with mock.patch.object(b.os, 'replace', side_effect=AssertionError('Unexpected write')), self.assertRaises(ValueError):
            b.apply(self.root, stage)
        self.assertEqual(before, self.snapshot())

    @unittest.skip('Actual symlink/junction creation and permission changes are prohibited in this task; not verified')
    def test_actual_symlink_junction_filesystem_behavior(self):
        pass


class AssetIndexEntrypointTests(unittest.TestCase):
    @staticmethod
    def original_data_fixture(base):
        data = base/'original-data'; data.mkdir()
        for name in ['tyrian1.lvl', 'tyrian.shp', 'newsh2.shp', 'shapesz.dat', 'palette.dat']:
            (data/name).write_bytes(b'synthetic external-data fingerprint; no game data read')
        return data

    def test_build_uses_current_view_unless_explicit_assets_are_selected(self):
        import runpy
        script = ROOT/'prototype/asset-index.py'
        with tempfile.TemporaryDirectory(prefix='preview-index-entry-') as temporary:
            base = Path(temporary); run = base/'trace'; run.mkdir()
            original_data = self.original_data_fixture(base)
            (run/'asset-debug-clock.tsv').write_text('tick\tstart_ms\tend_ms\n0\t0\t10\n')
            (run/'state.tsv').write_text('tick\n0\n')
            (run/'asset-debug-materials.tsv').write_text(
                'tick\tcategory\tsheet\tid\tx\ty\ttile_id\n0\tplayer-projectile\tshapes8.dat\t59\t0\t0\t59\n')
            (run/'asset-debug-run.json').write_text(json.dumps({'argv': [], 'exe_sha256': 'synthetic-no-engine'}))
            current = base/'current'; current.mkdir()
            name = 'bullet-59-8.hda'
            (current/name).write_bytes((ROOT/'assets/hd/current-compat/pulse'/name).read_bytes())
            historical = ROOT/'assets/hd/packs'/b.BASES['debug']
            original_read = Path.read_bytes
            def no_original_data(path):
                if path.parent == ROOT.parent/'runtime-data/tyrian2000':
                    return b'synthetic external-data fingerprint; no game data read'
                return original_read(path)
            for explicit in (None, historical):
                output = base/('explicit.json' if explicit else 'default.json')
                argv = [str(script), 'build', '--run', str(run), '--output', str(output), '--data', str(original_data)]
                if explicit: argv += ['--assets', str(explicit)]
                with mock.patch.object(sys, 'argv', argv), \
                        mock.patch.object(b, 'view', return_value={'path': str(current)}) as view, \
                        mock.patch.object(Path, 'read_bytes', no_original_data), \
                        contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as exited:
                    runpy.run_path(str(script), run_name='__main__')
                self.assertIsNone(exited.exception.code)
                if explicit:
                    view.assert_not_called()
                else:
                    view.assert_called_once()
                    self.assertEqual(view.call_args.args[:2], (ROOT, 'debug'))
                index = json.loads(output.read_bytes())
                self.assertEqual(index['replay']['data_sha256'], {name: hashlib.sha256((original_data/name).read_bytes()).hexdigest() for name in ['tyrian1.lvl', 'tyrian.shp', 'newsh2.shp', 'shapesz.dat', 'palette.dat']})
                chosen = explicit or current
                self.assertEqual(index['replay']['pack_directory'], str(chosen.resolve()))
                record = next(iter(index['segments'][0]['materials'].values()))['replacement_at_index_build']
                self.assertEqual(record['sha256'], hashlib.sha256((chosen/name).read_bytes()).hexdigest())

    def test_charge_default_build_discovers_all_nine_and_play_keeps_current_route(self):
        import runpy
        import subprocess
        script = ROOT/'prototype/asset-index.py'
        sprites = (258,259,260,277,278,279,296,297,298)
        with tempfile.TemporaryDirectory(prefix='charge-index-entry-') as temporary:
            base = Path(temporary); run = base/'trace'; run.mkdir()
            original_data = self.original_data_fixture(base)
            (run/'asset-debug-clock.tsv').write_text('tick\tstart_ms\tend_ms\n0\t0\t10\n')
            (run/'state.tsv').write_text('tick\n0\n')
            rows = 'tick\tcategory\tsheet\tid\tx\ty\ttile_id\n'
            rows += ''.join(f'0\tplayer\tshapes9.dat\t{sprite}\t0\t0\t{sprite}\n' for sprite in sprites)
            rows += '0\tplayer-projectile\tshapes9.dat\t258\t0\t0\t258\n0\tplayer\tshapes8.dat\t258\t0\t0\t258\n0\tplayer\tshapes9.dat\t257\t0\t0\t257\n'
            (run/'asset-debug-materials.tsv').write_text(rows)
            (run/'asset-debug-run.json').write_text(json.dumps({'argv': [], 'exe_sha256': 'synthetic-no-engine'}))
            original_read = Path.read_bytes; real_view = b.view
            def no_original_data(path):
                if path.parent == ROOT.parent/'runtime-data/tyrian2000': return b'synthetic external-data fingerprint; no game data read'
                return original_read(path)
            def current_view(root, kind, destination):
                self.assertEqual((root,kind),(ROOT,'debug'))
                return real_view(root,kind,base/'current-view')
            output = base/'index.json'
            with mock.patch.object(sys,'argv',[str(script),'build','--run',str(run),'--output',str(output),'--data',str(original_data)]), mock.patch.object(b,'view',side_effect=current_view), mock.patch.object(Path,'read_bytes',no_original_data), contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
                runpy.run_path(str(script),run_name='__main__')
            index=json.loads(output.read_bytes());view=Path(index['replay']['pack_directory'])
            self.assertEqual(len([path for path in view.rglob('*') if path.is_file()]),650)
            records=index['segments'][0]['materials']
            self.assertEqual(len(records),12)
            for key in ('player-projectile:tyrian.shp#spriteSheet9:258','player:tyrian.shp#spriteSheet8:258','player:tyrian.shp#spriteSheet9:257'):
                self.assertIsNone(records[key]['replacement_at_index_build']['file'])
            for sprite in sprites:
                record=records[f'player:tyrian.shp#spriteSheet9:{sprite}']['replacement_at_index_build']
                name=f'option-charge-bank9-{sprite}-8.hda'
                self.assertEqual(record['file'],name)
                self.assertEqual(record['header_values'],[1450000+sprite,8,12,14,0,0])
                self.assertEqual(record['sha256'],hashlib.sha256((ROOT/'assets/hd/current-compat/charge-body'/name).read_bytes()).hexdigest())
            argv=[str(script),'play','--index',str(output),'--sheet','tyrian.shp#spriteSheet9','--id','258','--category','player','--no-launch']
            with mock.patch.object(sys,'argv',argv), mock.patch.object(subprocess,'call',side_effect=AssertionError('Must not launch')) as launch, contextlib.redirect_stdout(io.StringIO()):
                result=runpy.run_path(str(script),run_name='__main__')
            launch.assert_not_called();self.assertNotIn('--assets',result['cmd'])
            self.assertEqual(result['cmd'][:2],[sys.executable,str(ROOT/'prototype/start-asset-debug.py')])

    def run_play_without_launch(self, assets=None):
        import runpy
        import subprocess
        script = ROOT/'prototype/asset-index.py'
        index = ROOT/'tests/no-launch-index-fixture.json'
        data = json.dumps({'segments': [{'number': 0, 'start_tick': 0}],
                           'materials': {}, 'replay': {'episode': 1, 'physical_level': 9}})
        def read_index(path, *args, **kwargs):
            self.assertEqual(path, index)
            return data
        argv = [str(script), 'play', '--index', str(index), '--segment', '0', '--no-launch']
        if assets is not None:
            argv += ['--assets', str(assets)]
        with mock.patch.object(sys, 'argv', argv), \
                mock.patch.object(Path, 'read_text', autospec=True, side_effect=read_index), \
                mock.patch.object(subprocess, 'call', side_effect=AssertionError('No-launch must not launch')) as launch, \
                contextlib.redirect_stdout(io.StringIO()):
            # Run the complete entrypoint in its own globals: no injected sys.
            namespace = runpy.run_path(str(script), run_name='__main__')
        launch.assert_not_called()
        return namespace['cmd']

    def test_default_play_reuses_running_interpreter_without_launch(self):
        cmd = self.run_play_without_launch()
        self.assertNotIn('--assets', cmd)
        self.assertEqual(cmd[:2], [sys.executable, str(ROOT/'prototype/start-asset-debug.py')])

    def test_explicit_assets_reuse_python_without_launch(self):
        with tempfile.TemporaryDirectory(prefix='explicit assets fixture ') as temporary:
            assets = Path(temporary)
            cmd = self.run_play_without_launch(assets)
            self.assertEqual(cmd[0], sys.executable)
            self.assertEqual(cmd[-2:], ['--assets', str(assets.resolve())])


class ViewOracleTests(unittest.TestCase):
    def test_independent_current_bodies_and_unchanged_members(self):
        names = (VIEW_CRAFT_NAME, *VIEW_SIDEKICKS.values())
        frozen = {name: b'old:' + name.encode() for name in names}
        frozen['unrelated.hda'] = b'unchanged'
        overlays = {name: b'current:' + name.encode() for name in names}
        actual = dict(frozen); actual.update(overlays)
        assert_current_view_bytes(self, actual, frozen, overlays)

    def test_each_historical_body_substitution_is_rejected(self):
        names = (VIEW_CRAFT_NAME, *VIEW_SIDEKICKS.values())
        frozen = {name: b'old:' + name.encode() for name in names}
        frozen['unrelated.hda'] = b'unchanged'
        overlays = {name: b'current:' + name.encode() for name in names}
        actual = dict(frozen); actual.update(overlays)
        for name in names:
            stale = dict(actual); stale[name] = frozen[name]
            with self.subTest(body=name), self.assertRaises(AssertionError):
                assert_current_view_bytes(self, stale, frozen, overlays)
        changed = dict(actual); changed['unrelated.hda'] = b'changed'
        with self.assertRaises(AssertionError):
            assert_current_view_bytes(self, changed, frozen, overlays)


class MemoryRollbackTests(unittest.TestCase):
    def test_transaction_failure_boundaries_in_memory_only(self):
        """Algorithm witness only; does not certify OS rename/permission behavior."""
        from pathlib import PurePosixPath
        for boundary in (1,2,3,4,None):
            files = {'a/old': b'old-a', 'b/old': b'old-b'}
            dirs = {'.','a','b'}
            before = dict(files), set(dirs)
            class Stream(io.BytesIO):
                def __init__(self, key):
                    super().__init__()
                    self.key = key
                def write(self, data):
                    result = super().write(data)
                    files[self.key] = self.getvalue()
                    return result
                def fileno(self): return 0
            class P:
                def __init__(self, key): self.key = key
                @property
                def name(self): return PurePosixPath(self.key).name
                @property
                def parent(self): return P(str(PurePosixPath(self.key).parent))
                def exists(self): return self.key in files or self.key in dirs
                def with_name(self, name): return P(str(PurePosixPath(self.key).with_name(name)))
                def mkdir(self):
                    if self.exists() or not self.parent.exists(): raise OSError('invalid mkdir')
                    dirs.add(self.key)
                def rmdir(self):
                    if any(x.startswith(self.key+'/') for x in set(files)|dirs): raise OSError('nonempty')
                    dirs.remove(self.key)
                def open(self, mode):
                    if mode != 'xb' or self.exists() or not self.parent.exists(): raise OSError('invalid open')
                    files[self.key] = b''
                    return Stream(self.key)
                def unlink(self): del files[self.key]
            def replace(src, dst):
                files[dst.key] = files.pop(src.key)
            fault = ReplaceFault(replace, boundary)
            outputs = {'a/old':b'new-a','new/deep/one':b'new-one','b/old':b'new-b','new/deep/two':b'new-two'}
            with self.subTest(boundary=boundary), mock.patch.object(b,'path',side_effect=lambda root,name:P(name)), mock.patch.object(b,'read',side_effect=lambda root,name:files[name]), mock.patch.object(b.os,'replace',side_effect=fault), mock.patch.object(b.os,'fsync'):
                if boundary:
                    with self.assertRaises(InjectedReplaceFailure) as error: b.replace_batch(None, outputs)
                    self.assertEqual(error.exception.boundary, boundary)
                    self.assertEqual(fault.hits, [boundary])
                    self.assertEqual((files,dirs), before)
                else:
                    b.replace_batch(None, outputs)
                    self.assertEqual(fault.hits, [])
                    self.assertEqual(files, outputs)


class HarnessCalibrationTests(unittest.TestCase):
    """Pure mocks only: never allocate a fixture or call OS replacement/cleanup."""
    def test_injected_type_and_exact_boundary(self):
        for boundary in range(1,5):
            real = mock.Mock()
            fault = ReplaceFault(real, boundary)
            for _ in range(boundary-1):
                fault('symbolic-source', 'symbolic-target')
            with self.assertRaises(InjectedReplaceFailure) as error:
                fault('symbolic-source', 'symbolic-target')
            self.assertEqual(error.exception.boundary, boundary)
            self.assertEqual(fault.hits, [boundary])
            self.assertEqual(real.call_count, boundary-1)

    def test_permission_error_cannot_satisfy_injected_failure(self):
        fault = ReplaceFault(mock.Mock(side_effect=PermissionError('pure mock refusal')), 2)
        with self.assertRaises(PermissionError):
            with self.assertRaises(InjectedReplaceFailure):
                fault('symbolic-source', 'symbolic-target')
        self.assertEqual(fault.hits, [])
        self.assertEqual(fault.calls, 1)

    def probe(self, restore):
        body = mock.Mock()
        class Probe(Craft267AuthoringTests):
            _preserve_fixture = False
            base = Path('__pure_mock_fixture_never_allocated__')
            @classmethod
            def setUpClass(cls):
                raise AssertionError('Calibration must not allocate a fixture')
            def _restore_fixture(self): restore()
            def test_ok(self): body()
            def test_error(self): raise PermissionError('pure mock body refusal')
            def test_subtest(self):
                with self.subTest(kind='pure mock'):
                    self.fail('pure mock subtest failure')
        return Probe, body

    def test_error_and_subtest_preserve_without_restore_or_following_access(self):
        for method in ('test_error', 'test_subtest'):
            restore = mock.Mock()
            probe, body = self.probe(restore)
            with mock.patch('builtins.print'), mock.patch.object(shutil, 'rmtree', side_effect=AssertionError('No real cleanup')) as cleanup:
                result = unittest.TestResult()
                probe(method).run(result)
                self.assertFalse(result.wasSuccessful())
                self.assertTrue(probe._preserve_fixture)
                restore.assert_not_called()
                following = unittest.TestResult()
                probe('test_ok').run(following)
                self.assertEqual(len(following.skipped), 1)
                body.assert_not_called()
                probe.tearDownClass()
                cleanup.assert_not_called()

    def test_restore_failure_preserves_without_final_cleanup(self):
        restore = mock.Mock(side_effect=PermissionError('pure mock restore refusal'))
        probe, _ = self.probe(restore)
        with mock.patch('builtins.print'), mock.patch.object(shutil, 'rmtree', side_effect=AssertionError('No real cleanup')) as cleanup:
            result = unittest.TestResult()
            probe('test_ok').run(result)
            self.assertEqual(len(result.errors), 1)
            self.assertTrue(probe._preserve_fixture)
            restore.assert_called_once_with()
            probe.tearDownClass()
            cleanup.assert_not_called()

    def test_success_cleanup_has_no_permission_callback_and_refusal_is_not_retried(self):
        probe, _ = self.probe(mock.Mock())
        with mock.patch('builtins.print'), mock.patch.object(os, 'chmod', side_effect=AssertionError('No permission changes')) as chmod:
            result = unittest.TestResult()
            probe('test_ok').run(result)
            self.assertTrue(result.wasSuccessful())
            with mock.patch.object(shutil, 'rmtree') as cleanup:
                probe.tearDownClass()
                cleanup.assert_called_once_with(probe.base)
            with mock.patch.object(shutil, 'rmtree', side_effect=PermissionError('pure mock cleanup refusal')) as cleanup:
                with self.assertRaises(PermissionError): probe.tearDownClass()
                self.assertTrue(probe._preserve_fixture)
                probe.tearDownClass()
                cleanup.assert_called_once_with(probe.base)
            chmod.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
