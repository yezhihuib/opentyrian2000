"""Bounded current HUD recipe: immutable geometry and source guards, selected art only.

Historical recipes and receipts are never rewritten. PNG assets are decoded
without resampling or encoding; meters replay the existing pinned material
recipe, including its original BOX downsampling, without a new conversion.
"""
import hashlib
import io
import json
import stat
import struct
from pathlib import Path
from PIL import Image
from package_runtime import contained_file, relative_path

CONTRACTS = {'static': {'filename': 'gameplay-hud-v1.hda',
            'header_hex': '485544310100000040010000c800000004000000000000000000000000fa000000803e00e2c05d3d1f44c114a2c6116ef14ef8b025e1a9e119eb3ea200000000',
            'source_sizes': [[1280, 800]],
            'source_modes': ['RGBA'],
            'baseline_sha256': '98cd6cfefa02a9ae79b75a65e02dd2566d3dec1492552f20b042b3c61c19cd17'},
 'font': {'filename': 'gameplay-hud-font-v1.hda',
          'header_hex': '48554631010000000400000000020000400100007f000000560000002000000028000000040000000080020007000000e2c05d3d1f44c1142729be9239e8805e66b4619693165b84e3a1f2cb85ca08093d6fce823d97d22e9aa07ebdb8decd850d3dc4b3bac2e8680000000000000000',
          'source_sizes': [[512, 320]],
          'source_modes': ['RGBA'],
          'baseline_sha256': '3c328c1537cf1e09529ae8805e98a8deb57a859ea80ba269cfea0b55cfae539e'},
 'components': {'filename': 'gameplay-hud-components-v1.hda',
                'header_hex': '48554331010000000400000004000000805700000e0000002400000008000000e2c05d3d1f44c114e8f0f947e48c4ec2ce234afe84e8b6202729be9239e8805e',
                'source_sizes': [[96, 20],
                                 [56, 20],
                                 [72, 20],
                                 [56, 20],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8],
                                 [36, 8]],
                'source_modes': ['RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA'],
                'baseline_sha256': 'c40c9ecf16a0d654876597195880deb484c17e36b1d1a17a9c1a241fb2b26d33'},
 'indicators': {'filename': 'gameplay-hud-indicators-v1.hda',
                'header_hex': '48554c3101000000040000001c0000000c0000006c0000002000000040710000e2c05d3d1f44c1142729be9239e8805e6022ce5ca7f08e325a49cea1158cf755185d041d527ca9f76e9cd65c2cd29694',
                'source_sizes': [[28, 12], [108, 32], [108, 32]],
                'source_modes': ['RGBA', 'RGBA', 'RGBA'],
                'baseline_sha256': 'c7e5925631cfeecb28a09b547702824af55ef3d9b5abe83f568dcf4672638631'},
 'fixed_text': {'filename': 'gameplay-hud-fixed-text-v1.hda',
                'header_hex': '4855543101000000040000000c00000072010000805c00000100000000000000e2c05d3d1f44c1142729be9239e8805ef463fcd12d5110b17338bd96e53d43a2',
                'source_sizes': [[76, 20],
                                 [20, 20],
                                 [20, 20],
                                 [20, 20],
                                 [20, 20],
                                 [20, 20],
                                 [20, 20],
                                 [20, 20],
                                 [20, 20],
                                 [20, 20],
                                 [20, 20],
                                 [20, 20]],
                'source_modes': ['RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA',
                                 'RGBA'],
                'baseline_sha256': '6d096f31085b22fb381761d3c8460bd06956c2bd039a1e0cc97481bc09819745'},
 'meters': {'filename': 'gameplay-hud-meters-v2.hda',
            'header_hex': '48554d3202000000700000000400000040010000c80000008010000080ca000000d80100f0c90600b0030000f8640300e2c05d3d1f44c1142729be9239e8805edb675fc6652ace922501ecda1038f133683841a5711723c434c1edc2239d121ddbc97088107cc7fc0000000000000000',
            'source_sizes': [],
            'source_modes': [],
            'baseline_sha256': '3f8d9c35a3a9791d554a3c46f3431289c8ecd68b57419747ce3a40c225dafa4c'}}
DEFAULT_SELECTION = {'static': [{'path': 'assets/hd/source/gameplay-hud-corner-v2-4x.png',
             'sha256': '6a0ee4b44791e70336b96ca39a401057e921461dd164b860f3746f0b4e6e1df3'}],
 'font': [{'path': 'assets/hd/artwork/gameplay-hud-font-v1/canonical/tiny-coverage-atlas-4x.png',
           'sha256': 'f81c31f85ec8646e5fd5e29e9cb9e6f03b8f51988e3dfc945bc2fa6821dfed92'}],
 'components': [{'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/label-FRONT-4x.png',
                 'sha256': 'f1644d33216ec424c8d00bb53121af319522dc06b288acc8fa66ebd9e3730f48'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/label-GUN_front-4x.png',
                 'sha256': '49bbae05ba1030b428573666e9dbae394519085a8a84350d89289526e6738803'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/label-REAR-4x.png',
                 'sha256': '0d4374b3d82a345ec970676099793d471c3dfae0621377e62bfdcf49cf30e8ce'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/label-GUN_rear-4x.png',
                 'sha256': '49bbae05ba1030b428573666e9dbae394519085a8a84350d89289526e6738803'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role146-4x.png',
                 'sha256': 'b2d162be5d263e5dec9eb9a492d0c04da577f8397a63788bbc39209caea1cced'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role147-4x.png',
                 'sha256': 'ed3195a22bcffba11fbf18fcf8da55e12a516b83a8fece57b9c9a5cfc85eb429'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role148-4x.png',
                 'sha256': '88157399c4b49a653336dcd4e4686ecf26ecfcab71faa251ad2e5f6e3a95e2ba'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role149-4x.png',
                 'sha256': 'f5e1b914f65b5ea0b3850d534d6bd42d1cc1ff655605c2d8ce4882c2d4c5b6eb'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role150-4x.png',
                 'sha256': 'a0d1ef7a34dfcd84460c0fcec000572437487f816cd24f3b174745625cab8a6c'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role151-4x.png',
                 'sha256': '7f77f01f5644dc382748b88b76cab6db1f491595a8a6710f4fc26b929b61b436'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role152-4x.png',
                 'sha256': 'd9b58d2ff5bba5af36fb944e2e278753208f919feb076b64a76c08818ceb5c69'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role153-4x.png',
                 'sha256': '99b4c8c4a980be9a58d41cb835ce46a518ef0d1fd447be137e1a595fa4b14434'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role154-4x.png',
                 'sha256': 'e9968e11e4835efefb25aa8997b22df58c77f5515474f26842983952e367c73b'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role155-4x.png',
                 'sha256': '701fa2df23a30bc6eca1fede09fb886498c1bd62c0cf313d15d078d54b197681'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role156-4x.png',
                 'sha256': 'abd68a8bea5f1fc3d0b5e72dbfef85c9bcee5c1e8a3c3f7c05260c610845a2ca'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role157-4x.png',
                 'sha256': '6925c22e3aa2e9a7db1cf8314c6897e91b3fcd29a34918ae0bcf6b276159c786'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role158-4x.png',
                 'sha256': '4d538271acdf9e6733a10804a1e860553d87f42414d02f968623ef00f1a0d914'},
                {'path': 'assets/hd/artwork/gameplay-hud-labels-shield-v1/tiles/shield-band-role159-4x.png',
                 'sha256': 'c720977435eb569ef1e864a99ca3b27da8c09fcab912546e2a7302e4c6f519bb'}],
 'indicators': [{'path': 'assets/hd/artwork/gameplay-hud-indicators-v1/lens-top-4x.png',
                 'sha256': '397b5af9da094f1aa1a8b3b7c8b3bf57222e4faf72f04b0b420c3960747bded9'},
                {'path': 'assets/hd/artwork/gameplay-hud-indicators-v1/assembly-mode1-4x.png',
                 'sha256': 'cc1f1ca62eaa72a728bff79e66bb9f73c7b3d439cec64b1a7c674ed2522b4a23'},
                {'path': 'assets/hd/artwork/gameplay-hud-indicators-v1/assembly-mode2-4x.png',
                 'sha256': 'a76fe10a443e8288fc1ddc997c81b62d10470baecc46d962790d08443b3549a8'}],
 'fixed_text': [{'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-MODE-4x.png',
                 'sha256': 'af06241d5b28f0e3c8565bafa672166848d1f977054be9efb5858671c2b5c5e3'},
                {'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-SHIELD_S0-4x.png',
                 'sha256': 'c5eac4ccd22ee40a4488de7ce16cdee2031907c8cc5f09607403670b83e52144'},
                {'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-SHIELD_H1-4x.png',
                 'sha256': '75b9df08d0c0dd5c72db0ecec1eed6b82e77b67b9d6a879acc4683db8ee351de'},
                {'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-SHIELD_I2-4x.png',
                 'sha256': '00a46a81ae2c49368ca2030ac234f03a4fdf877d9c877bf8bfd635367da6bba3'},
                {'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-SHIELD_E3-4x.png',
                 'sha256': '07641a1f66f1b45c2a2d19e872e70268f44a0c4d5d1fa637989f6824bd0da47e'},
                {'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-SHIELD_L4-4x.png',
                 'sha256': '28d34803591048545324ef5133961af873bc73b4957bb2dff068b789d061580e'},
                {'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-SHIELD_D5-4x.png',
                 'sha256': 'f8297dafd0d9062d8cf9cdf2cfa1bd22111e167ef7053a5da4ce0c37d87db6d5'},
                {'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-ARMOR_A0-4x.png',
                 'sha256': '594e8f2b0af2fe29c9102e0b596be26a47fb19437446d2e4793f5208e26133cc'},
                {'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-ARMOR_R1-4x.png',
                 'sha256': '8135bb08a0a0417415db56409bb360cc6807fb84ff891ad70c3192e648803089'},
                {'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-ARMOR_M2-4x.png',
                 'sha256': 'a6046e51be6b44d73d36aec3951659ada5bfb3618c25b0ccaa3e55697f19ed6c'},
                {'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-ARMOR_O3-4x.png',
                 'sha256': '71e2fb545e8ef03448df8d4cecc8121335c521efef7dc9ca741c30b190ab77bb'},
                {'path': 'assets/hd/artwork/gameplay-hud-fixed-text-v1/tiles/fixed-ARMOR_R4-4x.png',
                 'sha256': '8135bb08a0a0417415db56409bb360cc6807fb84ff891ad70c3192e648803089'}],
 'meters': [{'path': 'assets/hd/artwork/gameplay-hud-meters-v2/selected-rgb.json',
             'sha256': '98eb282953779812db0a1f2461e2a8c9701e57138638cabc550a4492c5b49e2e'}]}
FIXED_INPUTS = {'mask': {'path': 'assets/hd/artwork/gameplay-hud-corner-v2/combined-6853.mask',
          'sha256': 'dfc1e98e0d25b1a45645fc572d42396cf0407db975e44b3aefe91662255811b8'},
 'metrics': {'path': 'assets/hd/artwork/gameplay-hud-font-v1/sources/source-font-metrics.json',
             'sha256': '46d34fabd3014be2ef53282ffb2162fc16c75f0196054794cad500b57819f41a'},
 'meter_baseline': {'path': 'assets/hd/artwork/gameplay-hud-meters-v2/canonical/gameplay-hud-meters-v2.hda',
                    'sha256': '3f8d9c35a3a9791d554a3c46f3431289c8ecd68b57419747ce3a40c225dafa4c'},
 'meter_recipe': {'path': 'assets/hd/artwork/gameplay-hud-meters-v2/materials.py',
                  'sha256': '967f9d54b043b8e6cfcc209c3630485eee51f2e69cdeec1e003bf75bf4af3b22'}}

def require(ok, message):
    if not ok:
        raise ValueError(message)


def fnv(data):
    result = 14695981039346656037
    for b in data:
        result = ((result ^ b) * 1099511628211) & 0xffffffffffffffff
    return result


def checked(root, record):
    require(isinstance(record, dict) and set(record) == {'path', 'sha256'}, 'Invalid source record')
    digest = record['sha256']
    require(isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest), 'Invalid SHA256')
    rel = relative_path(record['path'])
    root = Path(root).resolve()
    target = contained_file(root, rel)
    require(target.is_file() and stat.S_ISREG(target.stat().st_mode), 'Missing or nonregular source')
    require(target.stat().st_size <= 16 * 1024 * 1024, 'Oversized source')
    with target.open('rb') as stream:
        data = stream.read(16 * 1024 * 1024 + 1)
    require(len(data) <= 16 * 1024 * 1024, 'Source grew beyond limit')
    require(hashlib.sha256(data).hexdigest() == record['sha256'], 'Source hash mismatch: ' + rel)
    return data


def default_selection(root=None):
    """Return independently mutable selection records with frozen initial hashes."""
    return json.loads(json.dumps(DEFAULT_SELECTION))


def meter_payload(root, data):
    import numpy as np
    colors = json.loads(data)
    ranges = {'firepower': range(116, 127), 'armor': range(226, 240), 'generator': range(113, 126)}
    require(isinstance(colors, dict) and set(colors) == set(ranges), 'Invalid meter roles')
    rgb = {}
    for role, indices in ranges.items():
        require(isinstance(colors[role], dict) and set(colors[role]) == {str(i) for i in indices}, 'Invalid meter indices')
        rgb[role] = {}
        for index in indices:
            color = colors[role][str(index)]
            require(isinstance(color, list) and len(color) == 3 and all(type(v) is int and 0 <= v <= 255 for v in color) and max(color) > 0, 'Invalid RGB color')
            rgb[role][index] = np.array(color, dtype=float)
    # Only the immutable, hash-checked recipe can execute; selected JSON is data.
    namespace = {'__name__': '_pinned_current_hud_materials'}
    exec(compile(checked(root, FIXED_INPUTS['meter_recipe']), '<pinned HUD materials>', 'exec'), namespace)
    material = namespace['material']
    sections = []
    for role, specs, width in (
        ('firepower', [(i, 3) for i in range(116,127)], 2),
        ('armor', [(226,h) for h in (2,4,6)] + [(i,h) for i in range(227,240) for h in (2,4)], 9)):
        sections.append(b''.join(material(rgb[role][i], width, h, role).convert('RGBA').tobytes() for i,h in specs))
    rows, ids, lookup = [], {}, []
    for index in range(113,126):
        for height in range(1,93):
            image = material(rgb['generator'][index], 8, height, 'generator').convert('RGBA').tobytes()
            for off in range(0,len(image),128):
                row = image[off:off+128]
                if row not in ids:
                    ids[row] = len(rows)
                    rows.append(row)
                lookup.append(ids[row])
    require(len(rows) == 944 and len(lookup) == 222456, 'Meter row structure changed')
    table = struct.pack('<222456H', *lookup)
    baseline = checked(root, FIXED_INPUTS['meter_baseline'])
    require(table == baseline[177008:], 'Meter lookup changed')
    sections += [b''.join(rows), table]
    require([len(s) for s in sections] == [4224,51840,120832,444912], 'Meter section size changed')
    require(all(set(s[3::4]) == {255} for s in sections[:3]), 'Nonopaque meter')
    return sections


def render_resource(root, key, sources):
    """Return (HDA bytes, generated meter macro values); never write any files."""
    require(key in CONTRACTS, 'Unknown HUD key')
    contract = CONTRACTS[key]
    require(isinstance(sources, list) and len(sources) == len(DEFAULT_SELECTION[key]), 'Source count changed')
    data = [checked(root, record) for record in sources]
    header = bytearray.fromhex(contract['header_hex'])
    pins = {}
    if key == 'meters':
        sections = meter_payload(root, data[0])
        payload = b''.join(sections)
        stamps = [fnv(s) for s in sections] + [fnv(payload)]
        for i, value in enumerate(stamps):
            struct.pack_into('<Q', header, 64 + i*8, value)
        pins = dict(zip(('HUD_METERS_FIRE_FNV','HUD_METERS_ARMOR_FNV','HUD_METERS_ROWS_FNV','HUD_METERS_LOOKUP_FNV','HUD_METERS_PAYLOAD_FNV'), stamps))
    else:
        images = []
        for raw, size, mode in zip(data, contract['source_sizes'], contract['source_modes']):
            with Image.open(io.BytesIO(raw)) as image:
                require(image.format == 'PNG' and getattr(image, 'n_frames', 1) == 1 and list(image.size) == size and image.mode == mode, 'PNG geometry or mode changed')
                image.load()
                images.append(image.copy())
        if key == 'static':
            mask = checked(root, FIXED_INPUTS['mask'])
            rgba = images[0].convert('RGBA').tobytes()
            alpha = images[0].getchannel('A').tobytes()
            # Equivalent to fixed 4x nearest ownership expansion, no conversion.
            expected = bytes(mask[(y//4)*320+x//4] for y in range(800) for x in range(1280))
            require(alpha == expected, 'HUD ownership alpha changed')
            payload = mask + rgba
            struct.pack_into('<Q', header, 52, fnv(rgba))
        elif key == 'font':
            payload = images[0].getchannel('A').tobytes()
            metrics = json.loads(checked(root, FIXED_INPUTS['metrics']))
            # Metric schema is pinned; canvas validation is supplied below.
            validate_font(payload, metrics)
            struct.pack_into('<Q', header, 88, fnv(payload))
        else:
            pieces = [im.convert('RGBA').tobytes() for im in images]
            require(all(set(p[3::4]) == {255} for p in pieces), 'Nonopaque HUD tile')
            payload = b''.join(pieces)
            if key == 'components':
                struct.pack_into('<QQ', header, 40, fnv(payload[:22400]), fnv(payload[22400:]))
            else:
                struct.pack_into('<Q', header, 72 if key == 'indicators' else 56, fnv(payload))
    return bytes(header) + payload, pins


def validate_font(payload, metrics):
    glyphs = metrics['tiny_font']['glyphs']
    require(len(glyphs) == 127 and len(payload) == 163840, 'Font geometry changed')
    for sid in range(128):
        width = glyphs[sid]['width'] * 4 if sid < 127 else 0
        height = glyphs[sid]['height'] * 4 if sid < 127 else 0
        left, top = (sid % 16)*32, (sid // 16)*40
        for y in range(40):
            for x in range(32):
                if not (4 <= x < 4+width and 4 <= y < 4+height):
                    require(payload[(top+y)*512+left+x] == 0, 'Font padding changed')
