"""Pure finite enemy-statics source, registration, input, fixture and schema helpers.

Import is inert: no process, native test, compiler, game, producer, filesystem
write or main invocation. All HDA/fixture functions return bytes in RAM only.
The original six generated sources and gold companion are immutable; the new
outer compile consumer is a reversible derivation, never the original wrapper.
"""
from pathlib import Path
import hashlib
import io
import json
import re
import stat
import struct
import types

STATICS = (162, 260)
IDS = (91, 145, 61, 101, 120, 139, 168, 169, 162, 260)
GOLD = (168, 169)
HDA_NAMES = {i: (f'enemy-projectile{i}-{i}-8.hda' if i in (91, 145, 61) else
                f'enemy-projectile-blue-triplet-{i}-8.hda' if i in (101, 120, 139) else
                f'enemy-projectile-gold-pulse-{i}-8.hda' if i in GOLD else
                f'enemy-projectile-statics-{i}-8.hda') for i in IDS}
PACK_NAMES = (('valid',) + tuple(n + str(i) for i in IDS for n in ('missing', 'bad')) +
              ('only162', 'only260', 'old-only') +
              tuple(n + str(i) for i in STATICS for n in ('header', 'short', 'trailing')) +
              tuple(n + str(i) for i in STATICS for n in ('magic', 'density', 'width', 'height', 'anchorx', 'anchory')))
# Derived from companion case-creating branches; source-contract tests cross-check.
GROUPS = (
    ('full_tile_native_patterns', 4),
    ('full_tile_hd_underlay', 2),
    ('bounds', 22),
    ('pair_orders_zero_isolation', 34),
    ('all10_same_origin_dependency', 20),
    ('all10_two_row_dependency', 20),
    ('missing_bad', 40),
    ('singletons_oldonly', 4),
    ('malformed_headers_lengths', 18),
    ('readiness_root_epochs', 4),
    ('unused_memory_payload_ready', 8),
    ('palette_admission_shared', 24),
    ('palette_direct_final_cache', 38),
    ('palette_composite_preflight', 12),
    ('used_resource_direct_final_cache', 52),
    ('source_scope_direct_final_cache', 24),
    ('layout_direct_final_cache', 32),
    ('callbacks', 12),
    ('cold_warm_scope', 44),
    ('Talon_transfer', 4),
    ('Talon_underlay_direct', 8),
    ('lifecycle', 7),
    ('later_native_final_writers', 8),
    ('fade_high_bits', 8),
)
TRANSFER = {162: (526, 521, 35), 260: (1122, 1122, 6)}
TAIL = (b'\n#include "projectile_statics_native_additions.c.inc"\n'
        b'int main(int argc,char **argv)\n{\n'
        b' if(argc>=2&&!strcmp(argv[1],"--enemy-statics"))return statics_main(argc,argv);\n'
        b' return inherited_gold_dispatch(argc,argv);\n}\n')
GOLD_HELPER_SHA = '39082c80c9fd37f28ca76ad34e342024a18799902dbfb44429baddb4a32170f2'
GOLD_COMPANION_SHA = 'b00796c4d72265022da0e9e4e1c46acbbbff00ee754b5a51a61701aa778e6f46'
GOLD_WRAPPER_SHA = 'cf43c879e05018407aafb293116c0731ba9f87ea03f9097fca79a91016096792'
SOURCE_PINS = {'inherited145_harness.c': '8925fb11215446339f067124fa7223ec48dc7c86459e303d3803477773b2d9ac', 'accepted_projectile61_native_additions.c.inc': '5f80d681e84a6dff20873f7f05bb3a02e3fd0f22013edf2b5fbf133d36c51cfe', 'accepted61_wrapper.c': '59bfbe4d8e3bb8db4403eaabb199d8ff2f09b2eb2047769f39069c93dff7f4eb', 'projectile61_native_additions.c.inc': 'd894e392ce315b855d5a764fbb526b6d6568a14f223e7e577a4ebf303ecbf67a', 'projectile_blue_triplet_native_additions.c.inc': 'cf38a2c8582bf9c3299a84721d37dae83402b938c859a2489ad382844a9a6084', 'harness.c': 'd39e3b9633eff3abfc70604f96895f21184fa87ad7f344ffa64f2b7705b353e1'}
STDOUT_PINS = {'inherited107_stdout': ('56b267d7cf607164010655de7fbd79fa42d3dc4518865434c2c4b705280856b2', 236), 'inherited61_stdout': ('bbc4b539205c19faa66ec7ada0c755d80907950e9ab91b554633c77fe261bcf4', 165), 'new_blue_stdout': ('833b3944bde9933444f4102716403b9868e1cefec4a077daeecd8535bef5208e', 631), 'gold251_stdout': ('a1f762926d2fb3bbc2499c5d7dc87f94cd20e239189f69af3646dcc58c4459d5', 973)}
COVERAGE_PATH = 'authoring-inputs/projectile-statics-current/coverage-contract.json'
COVERAGE_SHA = 'ae3a53f15f38e27714d8ccb7a6b79c517a69a85814acfd6d4337f205506bc5e9'
ASSET_DIRECTORY = 'assets/hd/current-compat/projectile-statics'
STATICS_COMPANION_SHA = '6886018f5bc62216ae48797ae888fbd169fcdbee3d42107856872b536d4e866e'
NATIVE_CONSUMERS = {'authoring-inputs/projectile-gold-pulse-current/coverage-contract.json': 'ed516cc835d7858d27999c837160bd4a04d0f782e3affc9e803f87e1d83cd3cf', 'tests/projectile145_native_additions.c.inc': 'd1547e9c93f3edf28c942b13f1935cc2289df99f713461d6c1f2981c6b757e39', 'tests/projectile61_native_additions.c.inc': '5f80d681e84a6dff20873f7f05bb3a02e3fd0f22013edf2b5fbf133d36c51cfe', 'tests/projectile61_native_validation.py': '68737e976c12cfa66eaf86c536cccd2ed2dc2a39e7a81740ecbd731d48699dc8', 'tests/projectile_blue_triplet_native_additions.c.inc': 'cf38a2c8582bf9c3299a84721d37dae83402b938c859a2489ad382844a9a6084', 'tests/projectile_blue_triplet_native_validation.py': '38d904bf84c17ae9179c6c4bc4ca895f31393efcc774ac851d7db1bc6a23ef6d', 'tests/projectile_gold_pulse_native_additions.c.inc': 'b00796c4d72265022da0e9e4e1c46acbbbff00ee754b5a51a61701aa778e6f46', 'tests/projectile_gold_pulse_native_validation.py': '39082c80c9fd37f28ca76ad34e342024a18799902dbfb44429baddb4a32170f2', 'tests/test_projectile91_global_runtime.py': 'ca11e49865dc7b38a843d6133c9689e5dbc1be55e16f96cc12d89b5580566309'}
DATA_PINS = {'tyrian.shp': '80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0', 'tyrianc.shp': 'e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d', 'palette.dat': 'f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0'}
STATICS_STDOUT_PIN = ('fc00c7f5120d9670fc500e8692e418798b93029c7af261ae0f3629ce50f92aef', 1577)
STATICS_ASSERTIONS = 91342858
PINS = {162: {'png_sha256': 'bbccd58bd75664e17391498f40355fe31215373da684f5259178b01b80b763e1', 'rgba_sha256': '76f9b1ec5130119e20d11a64530dfcc3308be1df64f159ee32ba9f18b64845a4', 'hda_sha256': '2d045f7fc472ed6e2f33f9d742072f3b7ea1c3a606d8f1909bbcd33b57ae0119', 'fnv1a64': '97621110c318d6a5', 'native_cells': 24, 'nonzero': 1392, 'soft': 1380, 'opaque255': 12, 'native_alpha0': 144, 'high_ge200': 24, 'low_1_199': 0, 'zero': 0, 'native_mask': '000000000000000000000000000001100000000011110000000011110000000001100000000000000000000001100000000011110000000011110000000001100000000000000000000000000000000000000000', 'max_alpha_matrix': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 254, 254, 0, 0, 0, 0, 0], [0, 0, 0, 0, 254, 253, 253, 255, 0, 0, 0, 0], [0, 0, 0, 0, 255, 253, 253, 255, 0, 0, 0, 0], [0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 254, 254, 0, 0, 0, 0, 0], [0, 0, 0, 0, 254, 253, 253, 255, 0, 0, 0, 0], [0, 0, 0, 0, 255, 253, 253, 255, 0, 0, 0, 0], [0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], 'palette_indices': [122, 123, 125, 126, 127]}, 260: {'png_sha256': 'caaa44da1ee336a17b2959e94c17719d3fce929c34711bdbfae510995ebf6909', 'rgba_sha256': 'fe9fd61f0ef6c71769390f07ed1cfc2798482b2a1c1c98ddafc8b1aa2b162bb6', 'hda_sha256': '5545ee065fcf879eb306a6c25dc0b9be8ecf8dcaa5154cdbb69ae907e75adf8e', 'fnv1a64': 'fa2ac27b3212b610', 'native_cells': 86, 'nonzero': 5217, 'soft': 5216, 'opaque255': 1, 'native_alpha0': 287, 'high_ge200': 83, 'low_1_199': 3, 'zero': 0, 'native_mask': '000011100000000111110000001111111000001111111000001111111000001111111000001111111000001111111000001111111000001111111000001111111000001111111000000111110000000011100000', 'max_alpha_matrix': [[0, 0, 0, 0, 254, 255, 254, 0, 0, 0, 0, 0], [0, 0, 0, 252, 253, 253, 253, 252, 0, 0, 0, 0], [0, 0, 188, 252, 253, 253, 253, 253, 203, 0, 0, 0], [0, 0, 247, 253, 252, 253, 253, 253, 247, 0, 0, 0], [0, 0, 250, 253, 252, 253, 253, 253, 251, 0, 0, 0], [0, 0, 252, 253, 253, 253, 253, 253, 252, 0, 0, 0], [0, 0, 252, 253, 253, 253, 253, 253, 252, 0, 0, 0], [0, 0, 252, 253, 253, 253, 252, 253, 253, 0, 0, 0], [0, 0, 252, 253, 253, 253, 253, 253, 252, 0, 0, 0], [0, 0, 248, 253, 253, 253, 252, 253, 249, 0, 0, 0], [0, 0, 245, 253, 253, 253, 252, 253, 246, 0, 0, 0], [0, 0, 195, 253, 253, 253, 252, 253, 190, 0, 0, 0], [0, 0, 0, 252, 253, 253, 253, 253, 0, 0, 0, 0], [0, 0, 0, 0, 253, 253, 253, 0, 0, 0, 0, 0]], 'palette_indices': [113, 116, 117, 119, 120, 121, 122, 123, 124, 125, 126]}}


def reject_constant(value):
    raise AssertionError(('Non-finite JSON constant', value))


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, ('Duplicate JSON key', key)
        result[key] = value
    return result


def no_link_path(path, leaf_file=True):
    """Reject symlink/reparse components without resolving to another root."""
    path = Path(path).absolute()
    for current in reversed((path, *path.parents)):
        info = current.lstat()
        assert not stat.S_ISLNK(info.st_mode), str(current)
        assert not getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0), str(current)
        if current != path or not leaf_file:
            assert stat.S_ISDIR(info.st_mode), str(current)
    return path


def installed_path(root, relative):
    """Closed consumers use canonical POSIX relative paths under an explicit root."""
    assert type(relative) is str and relative and '\\' not in relative and '\x00' not in relative
    assert not relative.startswith('/') and all(part not in ('', '.', '..') for part in relative.split('/'))
    base = no_link_path(root, leaf_file=False)
    path = base.joinpath(*relative.split('/'))
    no_link_path(path)
    assert path.is_relative_to(base)
    return path


def verify_native_consumers(root):
    """Exactly nine installed immutable old helper/AST/coverage consumers."""
    result = {}
    for relative, pin in NATIVE_CONSUMERS.items():
        raw = regular_bytes(installed_path(root, relative))
        assert SHA(raw) == pin, ('Frozen native consumer changed', relative)
        result[relative] = pin
    return result


def SHA(raw):
    assert type(raw) is bytes
    return hashlib.sha256(raw).hexdigest()


def regular_bytes(path, maximum=16 * 1024 * 1024):
    """Read one independent regular input, reject symlinks and hardlinks."""
    assert type(maximum) is int and maximum >= 0
    path = no_link_path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and not path.is_symlink(), str(path)
    assert 0 <= before.st_size <= maximum
    raw = path.read_bytes()
    no_link_path(path)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_mode, before.st_nlink) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_mode, after.st_nlink), str(path)
    assert len(raw) == before.st_size
    return raw


def pinned_json(path, pin):
    raw = regular_bytes(path)
    assert SHA(raw) == pin, str(path)
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)


def gold_helper(root):
    verify_native_consumers(root)
    path = installed_path(root, 'tests/projectile_gold_pulse_native_validation.py')
    raw = regular_bytes(path)
    assert SHA(raw) == GOLD_HELPER_SHA, 'Frozen gold helper changed'
    module = types.ModuleType('frozen_gold_native_helpers')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def outer_shim(raw):
    assert type(raw) is bytes and SHA(raw) == GOLD_WRAPPER_SHA
    assert raw.count(b'int main(') == 1 and b'inherited_gold_dispatch' not in raw
    result = raw.replace(b'int main(', b'int inherited_gold_dispatch(', 1) + TAIL
    assert reverse_shim(result) == raw
    return result


def reverse_shim(raw):
    assert type(raw) is bytes and raw.endswith(TAIL)
    body = raw[:-len(TAIL)]
    assert body.count(b'int inherited_gold_dispatch(') == 1 and b'int main(' not in body
    result = body.replace(b'int inherited_gold_dispatch(', b'int main(', 1)
    assert SHA(result) == GOLD_WRAPPER_SHA, 'Non-exact gold inverse'
    return result


def source_bundle(root):
    """Reconstruct from pinned current source only; return old6 and new shim."""
    gold = gold_helper(root)
    sources, old_gold = gold.source_bundle(Path(root))
    assert type(sources) is dict and set(sources) == set(SOURCE_PINS)
    for name, raw in sources.items():
        assert SHA(raw) == SOURCE_PINS[name], name
    assert len(sources['harness.c']) == 262
    assert SHA(regular_bytes(installed_path(root, 'tests/projectile_statics_native_additions.c.inc'))) == STATICS_COMPANION_SHA
    companion = regular_bytes(installed_path(root, 'tests/projectile_gold_pulse_native_additions.c.inc'))
    assert SHA(companion) == GOLD_COMPANION_SHA
    derived = outer_shim(old_gold)
    assert gold.reverse_shim(reverse_shim(derived)) == sources['harness.c']
    return sources, derived


def native_inputs(root, data):
    """Exactly inherited old/new stdin derivations; no process or write."""
    for name, pin in DATA_PINS.items():
        assert SHA(regular_bytes(installed_path(data, name))) == pin
    old, new = gold_helper(root).native_inputs(Path(root), Path(data))
    assert SHA(old) == '7dedf7066696fc278f5fbb8dfb1462e7b6ac290cb5d08ae5260a6cdabc1ecca7'
    assert SHA(new) == 'a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b'
    return old, new


def fnv1a64(raw):
    assert type(raw) is bytes
    value = 0xcbf29ce484222325
    for byte in raw:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return value


def rgba_statistics(rgba, native_mask):
    """Inspect all10752 pixels, including native-alpha0 and outside support."""
    assert type(rgba) is bytes and len(rgba) == 43008
    assert type(native_mask) is str and len(native_mask) == 168 and set(native_mask) <= {'0', '1'}
    result = dict(nonzero=0, soft=0, opaque255=0, native_alpha0=0,
                  outside_nonzero=0, alpha0_rgb_nonzero=0,
                  native_cells=native_mask.count('1'), high_ge200=0, low_1_199=0, zero=0)
    maxima = [0] * 168
    for index in range(10752):
        r, g, b, a = rgba[4 * index:4 * index + 4]
        cell = (index // 96 // 8) * 12 + (index % 96) // 8
        maxima[cell] = max(maxima[cell], a)
        result['nonzero'] += a != 0
        result['soft'] += 0 < a < 255
        result['opaque255'] += a == 255
        result['native_alpha0'] += native_mask[cell] == '1' and a == 0
        result['outside_nonzero'] += native_mask[cell] == '0' and any((r, g, b, a))
        result['alpha0_rgb_nonzero'] += a == 0 and any((r, g, b))
    for cell, alpha in enumerate(maxima):
        if native_mask[cell] == '1':
            result['high_ge200' if alpha >= 200 else 'low_1_199' if alpha else 'zero'] += 1
    result['max_alpha_matrix'] = [maxima[y * 12:(y + 1) * 12] for y in range(14)]
    return result


def registered_rgba(selector, root):
    import PIL
    from PIL import Image
    assert PIL.__version__ == '12.3.0', 'Pinned Pillow12.3.0 required'
    assert type(selector) is int and selector in STATICS
    path = installed_path(root, f'{ASSET_DIRECTORY}/projectile-statics-{selector}-registered.png')
    raw = regular_bytes(path, 128 * 1024)
    assert SHA(raw) == PINS[selector]['png_sha256']
    with Image.open(io.BytesIO(raw)) as image:
        assert image.format == 'PNG' and image.mode == 'RGBA' and image.size == (96, 112)
        assert getattr(image, 'n_frames', 1) == 1
        image.load()
        rgba = image.tobytes()
    assert len(rgba) == 43008 and SHA(rgba) == PINS[selector]['rgba_sha256']
    assert f'{fnv1a64(rgba):016x}' == PINS[selector]['fnv1a64']
    return rgba


def registration(root):
    """Verify installed fixed art/coverage only. No receipt, backup or fallback."""
    contract = pinned_json(installed_path(root, COVERAGE_PATH), COVERAGE_SHA)
    assert type(contract) is dict and set(contract) == {'schema', 'members'}
    assert contract['schema'] == 'enemy-statics-selected-coverage-v1'
    assert type(contract['members']) is dict and set(contract['members']) == {'162', '260'}
    members = []
    for selector in STATICS:
        pin = PINS[selector]
        record = contract['members'][str(selector)]
        expected = {
            'native_mask': pin['native_mask'], 'native_occupied_cells': pin['native_cells'],
            'max_alpha_matrix': pin['max_alpha_matrix'],
            'cell_distribution': {k: pin[k] for k in ('high_ge200', 'low_1_199', 'zero')},
            'pixels': {**{k: pin[k] for k in ('nonzero', 'soft', 'opaque255', 'native_alpha0')},
                       'max_alpha': 255, 'outside_nonzero': 0, 'alpha0_rgb_nonzero': 0},
            'png_sha256': pin['png_sha256'], 'hda_sha256': pin['hda_sha256'],
            'payload_sha256': pin['rgba_sha256'], 'payload_fnv': pin['fnv1a64'],
            'palette_indices': pin['palette_indices'],
        }
        assert record == expected
        assert type(record['native_occupied_cells']) is int
        assert all(type(v) is int for v in record['cell_distribution'].values())
        assert all(type(v) is int for v in record['pixels'].values())
        assert type(record['max_alpha_matrix']) is list and len(record['max_alpha_matrix']) == 14
        assert all(type(row) is list and len(row) == 12 and all(type(v) is int and 0 <= v <= 255 for v in row)
                   for row in record['max_alpha_matrix'])
        assert all(type(v) is int for v in record['palette_indices'])
        rgba = registered_rgba(selector, root)
        stats = rgba_statistics(rgba, pin['native_mask'])
        for key in ('native_cells', 'nonzero', 'soft', 'opaque255', 'native_alpha0', 'high_ge200', 'low_1_199', 'zero'):
            assert stats[key] == pin[key], (selector, key)
        assert stats['outside_nonzero'] == stats['alpha0_rgb_nonzero'] == 0
        assert stats['max_alpha_matrix'] == pin['max_alpha_matrix']
        assert max(rgba[3::4]) == 255
        payload = regular_bytes(installed_path(root, f'{ASSET_DIRECTORY}/{HDA_NAMES[selector]}'), 43036)
        validate_hda(payload, selector)
        assert payload[28:] == rgba
        members.append(dict(pin, selector=selector, statistics=stats))
    return {'schema': 'enemy-statics-fixed-registration-v1', 'members': members,
            'coverage_sha256': COVERAGE_SHA,
            'scope': 'Installed fixed art contract only; no new native/fresh/gameplay qualification.'}


def hda_payload(selector, rgba):
    assert type(selector) is int and selector in STATICS
    assert type(rgba) is bytes and len(rgba) == 43008
    assert SHA(rgba) == PINS[selector]['rgba_sha256']
    assert f'{fnv1a64(rgba):016x}' == PINS[selector]['fnv1a64']
    result = struct.pack('<4s6I', b'HDR1', 1540000 + selector, 8, 12, 14, 0, 0) + rgba
    validate_hda(result, selector)
    return result


def validate_hda(raw, selector):
    assert type(selector) is int and selector in STATICS
    assert type(raw) is bytes and len(raw) == 43036
    assert raw[:28] == struct.pack('<4s6I', b'HDR1', 1540000 + selector, 8, 12, 14, 0, 0)
    assert SHA(raw) == PINS[selector]['hda_sha256']
    assert SHA(raw[28:]) == PINS[selector]['rgba_sha256']
    assert f'{fnv1a64(raw[28:]):016x}' == PINS[selector]['fnv1a64']
    return True


def registered_hdas(root):
    """Read the exact two installed HDAs after complete registration checks."""
    registration(root)
    result = {}
    for selector in STATICS:
        raw = regular_bytes(installed_path(root, f'{ASSET_DIRECTORY}/{HDA_NAMES[selector]}'), 43036)
        validate_hda(raw, selector)
        result[selector] = raw
    return result


def fixture_bytes(raw, selector, leaf):
    assert type(raw) is bytes and len(raw) == 43036
    assert type(selector) is int and selector in IDS and leaf in PACK_NAMES
    if leaf == 'old-only' and selector in STATICS:
        return None
    if leaf.startswith('only') and selector != int(leaf[4:]):
        return None
    if leaf == 'missing' + str(selector):
        return None
    result = bytearray(raw)
    if leaf == 'bad' + str(selector):
        result[128] ^= 1
    if leaf == 'header' + str(selector):
        result[4] ^= 1
    if leaf == 'magic' + str(selector):
        result[0] ^= 1
    for field, offset, value in (('density', 8, 4), ('width', 12, 11), ('height', 16, 13),
                                 ('anchorx', 20, 1), ('anchory', 24, 1)):
        if leaf == field + str(selector):
            struct.pack_into('<I', result, offset, value)
    if leaf == 'short' + str(selector):
        result = result[:-1]
    if leaf == 'trailing' + str(selector):
        result += b'!'
    return bytes(result)


def fixture_schema():
    """Exact finite new pack membership, independent of payload production."""
    sentinel = bytes(43036)
    return {leaf: tuple(i for i in IDS if fixture_bytes(sentinel, i, leaf) is not None) for leaf in PACK_NAMES}


def fixture_payloads(root, hdas, registration_metadata):
    """Return old335 unchanged plus finite new files; caller owns all writes."""
    assert type(hdas) is dict and set(hdas) == set(IDS) and all(type(i) is int for i in hdas)
    assert type(registration_metadata) is dict and set(registration_metadata) == {'schema', 'members', 'coverage_sha256', 'scope'}
    assert registration_metadata['coverage_sha256'] == COVERAGE_SHA
    assert type(registration_metadata['members']) is list and len(registration_metadata['members']) == 2
    assert tuple(member['selector'] for member in registration_metadata['members']) == STATICS
    assert all(type(member['selector']) is int for member in registration_metadata['members'])
    assert registration_metadata['schema'] == 'enemy-statics-fixed-registration-v1'
    members = {member['selector']: member for member in registration_metadata['members']}
    assert set(members) == set(STATICS)
    for selector in STATICS:
        validate_hda(hdas[selector], selector)
        assert set(members[selector]) == set(PINS[selector]) | {'selector', 'statistics'}
        assert all(members[selector][key] == value for key, value in PINS[selector].items())
    gold = gold_helper(root)
    old = gold.fixture_payloads(Path(root), {i: hdas[i] for i in gold.IDS}, gold.registration(root))
    assert len(old) == 335
    new = {}
    for leaf in PACK_NAMES:
        for selector in IDS:
            raw = fixture_bytes(hdas[selector], selector, leaf)
            if raw is not None:
                new[f'statics-packs/{leaf}/{HDA_NAMES[selector]}'] = raw
    assert len(new) == sum(map(len, fixture_schema().values()))
    assert not set(old) & set(new)
    result = {**old, **new}
    assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in result)
    assert all(type(value) is bytes for value in result.values())
    return result


def strict_stdout_lines(stdout):
    assert type(stdout) is bytes and stdout.endswith(b'\n') and b'\r' not in stdout
    text = stdout.decode('ascii', errors='strict')
    assert '\x00' not in text
    return text[:-1].split('\n')


def verify_legacy_stdout(actual):
    assert type(actual) is dict and set(actual) == set(STDOUT_PINS)
    for name, raw in actual.items():
        assert type(raw) is bytes
        pin, size = STDOUT_PINS[name]
        assert len(raw) == size and SHA(raw) == pin, ('Original880 stdout bytes changed', name)
        strict_stdout_lines(raw)
    return {'cases': 880, 'assertions': 50255790, 'process_cases': [107, 157, 365, 251],
            'scope': 'Four inherited byte-exact controlled native process contracts.'}


def parse_statics_stdout(stdout):
    assert GROUPS and len(set(name for name, _ in GROUPS)) == len(GROUPS), 'Unfrozen companion schema'
    assert all(type(count) is int and count > 0 for _, count in GROUPS)
    lines = strict_stdout_lines(stdout)
    assert len(lines) == len(GROUPS) + 5, 'Exact groups + four transfers + summary required'
    position = 0
    observed = []
    for name, count in GROUPS:
        if name == 'Talon_transfer':
            for selector in STATICS:
                copied, soft, zero = TRANSFER[selector]
                for cached in (0, 1):
                    expected = (f'STATICS_TO_TALON selector={selector} copied={copied} soft={soft} '
                                f'alpha0={zero} cached={cached}')
                    assert lines[position] == expected, ('Actual transfer schema/count', lines[position])
                    observed.append(expected)
                    position += 1
        assert lines[position] == f'STATICS_GROUP name={name} cases={count}', ('Group missing/order/count', name)
        position += 1
    assert len(observed) == 4
    match = re.fullmatch(r'PASS enemy statics native lifecycle: ([1-9][0-9]*) cases ([1-9][0-9]*) assertions; internal8 only; not gameplay/full build', lines[position])
    assert match and int(match[1]) == sum(count for _, count in GROUPS)
    assert int(match[2]) == STATICS_ASSERTIONS
    assert (SHA(stdout), len(stdout)) == STATICS_STDOUT_PIN
    return {'cases': int(match[1]), 'assertions': int(match[2]),
            'groups': [{'name': name, 'cases': count} for name, count in GROUPS],
            'transfers': observed,
            'scope': 'Controlled internal8 production-TU probe; no game/fresh-fullbuild/fullgate claim.'}
