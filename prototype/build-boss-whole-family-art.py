#!/usr/bin/env python3
"""Verify and rebuild the immutable finite boss-body artwork; never run the game.

Only generated masters and technical structure/masks feed the frozen recipe.
Original source data is optional read-only evidence, never an artwork input.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
import tempfile
import shutil
import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter
from PIL import Image, ImageChops

IDS = [1,3,5,7,10,12,14,16,18,39,41,43,45,48,50,54,56,86,88,90,92,94,124,126,128,130,132,162,164,168,170,200,202,206,208,240,242,244,246,280]
EMPTY = [238,278,282]
ALL_IDS = sorted(IDS + EMPTY)
CENTER = [1,3,5,7,39,41,43,45]
PARTS = [0,1,19,20]
KEYS = {1020000 + base for base in ALL_IDS}
SOURCE = 'assets/hd/artwork/boss-whole-family-v2-inward-alpha'
V1_SOURCE = 'assets/hd/artwork/boss-whole-family-v1'
V1_FREEZE = '93cd781517e02fe339eada2e3d05fd9d8ba7baaedf3302a68ab728f284c31672'
FAMILY = 'boss_whole_family_v2_inward_alpha'
FREEZE = 'd82f610c48592b712907c0532fb50853bb2fc1e51a93f2fa8dc5511666612374'
CONTRACT_SHA = 'f1f81bf1ae9569d3d568065f0490aeac23c8f0beb360b7f1ab16a0a36dcf1bbc'
SOURCE_CONTRACT_SHA = 'c7a81e82119c98ae3a476c1c9201572bdaa57255ef06e0621d9b489446316b87'
REVIEW_HASHES = {'review/all21-inward-alpha-native2x.png': 'e32baf9db647cd673df2bdaaf376c5d15a1f30dd0b40f795aab7d7274004e3cd', 'review/all21-inward-alpha-native4x.png': '4070e629a8c1251ccefaa25968ac81337870745ad8020e4e2319d40353a76261', 'review/translated-states-native2x.png': '540254b21702ab27fff842fdc250a48c06002b1b93b5d672083b48cccdc0c120', 'review/translated-states-native4x.png': '9b365057f22471f23798dcb2e8961247b77212ddc30e4839bb2015ceb9a6437a'}
FROZEN_FILES = 250
FROZEN_INPUTS = 159
DEFAULTS = ['packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test',
            'packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test']
ORIGINAL_HASHES = {
    'newsh4.shp': 'ab8881b4a26e723650780b19d5aed4ebfe410ea450d4bf7b80840628d61fd89b',
    'tyrian.hdt': 'fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b',
    'tyrian1.lvl': '54cbb00b57b84aa992a70cfcb170cb1edeb59507873723630d60080ba8351352',
}
READERS = {'src/episodes.c': '640219b48d3081ee996ce66a66f61ad2fe185339fcfaf395808e02fcee0b29e0',
           'src/tyrian2.c': '0a042621d599fdba15f89012c9bb1007327cd6f5df0e0a41865ea61c08856d02',
           'src/sprite.c': 'b912773976c4b745f355d471b4da6a4ea25907e7bf80eb7356c9a59ae361237c',
           'src/varz.c': 'd4502557903eea9fc082b83385fee3448564124040ff27faa1a4af16c8e394c7'}
GENERATED_ONLY = ['rebuild.py', 'proof/source-contract.json', 'proof/intact-registration.json',
    'sources/generated-intact-v2.png', 'sources/generated-damage.png', 'sources/generated-center-lights.png',
    'masks/intact-alpha.png', 'masks/damage-alpha.png', 'masks/damage-change-mask8x.png',
    *[f'masks/mask-newsh4-{base}.png' for base in ALL_IDS]]

def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_regular(path):
    no_symlinks(path)
    require(path.is_file(), 'regular file required: ' + str(path))
    return path.read_bytes()


def load(path):
    return json.loads(read_regular(path).decode(), object_pairs_hook=unique_object)


def exact_json(actual, expected):
    # JSON booleans/floats must not masquerade as integer header/scope fields.
    return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)


def no_symlinks(path):
    require(not any(p.is_symlink() for p in [path, *path.parents]),
            'symlink path forbidden: ' + str(path))


def safe_relative(value):
    require(isinstance(value, str), 'unsafe manifest path type')
    path = PurePosixPath(value)
    require(value and value != '.' and not path.is_absolute() and '..' not in path.parts
            and path.as_posix() == value and '\\' not in value and '\0' not in value,
            'unsafe manifest path: ' + value)
    return path


def safe_output(value, repo):
    given = value.expanduser()
    require(given.is_absolute(), 'output must be absolute')
    require('..' not in given.parts, 'output traversal forbidden')
    no_symlinks(given)
    out = given.resolve()
    require(not out.exists(), 'output must be fresh')
    require(out.parent.is_dir(), 'output parent must exist')
    require(out != repo and repo not in out.parents and out not in repo.parents,
            'output must be outside repository')
    return out


def original_root(value, repo):
    given = value.expanduser()
    require(given.is_absolute(), 'original data must be absolute')
    require('..' not in given.parts, 'original data traversal forbidden')
    no_symlinks(given)
    root = given.resolve()
    require(root.is_dir(), 'original data directory missing')
    require(root != repo and repo not in root.parents and root not in repo.parents,
            'original data must stay outside repository')
    return root


def inventory(source):
    no_symlinks(source)
    nodes = list(source.rglob('*'))
    require(all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in nodes),
            'source symlink or special file forbidden')
    require(sha(read_regular(source / 'inventory.json')) == FREEZE, 'source inventory freeze mismatch')
    frozen = load(source / 'inventory.json')
    require(frozen['schema'] == 'boss-whole-family-v2-inward-alpha' and len(frozen['inputs']) == FROZEN_INPUTS and [r['base'] for r in frozen['outputs']] == ALL_IDS,
            'source inventory scope mismatch')
    expected = dict(frozen['inputs'], **{'inventory.json': FREEZE}, **REVIEW_HASHES)
    expected.update({f'output/enemy-newsh4-{r["base"]}-8.{ext}': r[ext.upper() + '_SHA256']
                     for r in frozen['outputs'] for ext in ['hda', 'png']})
    for name in expected:
        safe_relative(name)
    require({p.relative_to(source).as_posix() for p in nodes if p.is_file()} == set(expected),
            'source inventory differs: missing or unlisted file')
    expected_dirs = {str(p) for name in expected for p in PurePosixPath(name).parents if str(p) != '.'}
    require({p.relative_to(source).as_posix() for p in nodes if p.is_dir()} == expected_dirs,
            'source inventory differs: unlisted directory')
    for name, digest in expected.items():
        require(sha(read_regular(source / name)) == digest, 'source file mismatch: ' + name)
    require(frozen['inputs']['contract.json'] == CONTRACT_SHA and
            frozen['inputs']['base-v1/proof/source-contract.json'] == SOURCE_CONTRACT_SHA,
            'source contract freeze mismatch')
    require(load(source / 'alpha-proof.json')['outputs'] == frozen['outputs'],
            'frozen alpha proof output mismatch')
    return frozen


def fnv1a(data):
    stamp = 0xcbf29ce484222325
    for value in data:
        stamp = ((stamp ^ value) * 0x100000001b3) & 0xffffffffffffffff
    return f'{stamp:016x}'


def validate_hda(raw, base, row):
    require(len(raw) == 172060, 'HDR1 length/EOF mismatch')
    require(raw[:28] == b'HDR1' + struct.pack('<6I', 1020000 + base, 8, 24, 28, 6, 7),
            'HDR1 dimensions/anchor/key mismatch')
    require(sha(raw) == row['HDA_SHA256'] and sha(raw[28:]) == row['RGBA_SHA256'],
            'HDR1 frozen payload mismatch')
    return raw[28:]


def family_name(name, png=False):
    pattern = r'enemy-newsh4-(\d+)-.*\.png' if png else r'enemy-newsh4-(\d+)-(\d+)\.hda'
    match = re.fullmatch(pattern, name)
    return match is not None and int(match[1]) in ALL_IDS


def expected_family():
    # This exact finite contract is intentionally independent of the candidate manifest.
    return {'schema': 'boss-whole-family-v2-inward-alpha',
     'source': SOURCE,
     'source_inventory_sha256': FREEZE,
     'source_contract_sha256': CONTRACT_SHA,
     'density': 8,
     'logical_size': [24, 28],
     'anchor': [6, 7],
     'ids': [1,
             3,
             5,
             7,
             10,
             12,
             14,
             16,
             18,
             39,
             41,
             43,
             45,
             48,
             50,
             54,
             56,
             86,
             88,
             90,
             92,
             94,
             124,
             126,
             128,
             130,
             132,
             162,
             164,
             168,
             170,
             200,
             202,
             206,
             208,
             240,
             242,
             244,
             246,
             280],
     'slots': [422,
               423,
               424,
               425,
               426,
               427,
               428,
               429,
               430,
               431,
               432,
               433,
               434,
               435,
               436,
               437,
               438,
               439,
               440,
               441,
               442,
               443,
               444,
               445,
               446,
               447,
               448,
               449,
               450,
               451,
               452,
               453,
               454,
               455,
               456,
               457,
               458,
               459,
               460,
               461],
     'bank_id': 2,
     'bank_role': 102,
     'runtime_components': [0, 1, 19, 20],
     'source_records': [46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65],
     'record_bases': {'46': [10, 162],
                      '47': [12, 164],
                      '48': [14],
                      '49': [16, 168],
                      '50': [18, 170],
                      '51': [48, 200],
                      '52': [50, 202],
                      '53': [1, 3, 5, 7, 39, 41, 43, 45],
                      '54': [54, 206],
                      '55': [56, 208],
                      '56': [86, 238],
                      '57': [88, 240],
                      '58': [90, 242],
                      '59': [92, 244],
                      '60': [94, 246],
                      '61': [124],
                      '62': [126, 278],
                      '63': [128, 280],
                      '64': [130, 282],
                      '65': [132]},
     'intentional_empty_bases': [238, 278, 282],
     'equal_rgba_distinct_header_ids': [[128, 280]],
     'initial_assembly': [120, 112],
     'source_center_cycle': [1, 3, 5, 7, 39, 41, 43, 45],
     'original_alpha_support_subset': True,
     'RGB_byte_identical_to_v1': True,
     'alpha_editable_masks_exact': True,
     'fallback': 'All forty nonempty approved members required before any body replacement; '
                 'selected-pack8x-only family-local cached fallback; empty238/278/282 remain original '
                 'no-ops',
     'separate_dependencies': ['Published type3 ordinary acceptance; boss launch context pending',
                               'Weapon81 seven enemy-shot assets and bindings remain outside this body '
                               'patch',
                               'Original orb/effect routes and indexed bossbar preserved']}


def historical_v1(repo, source, frozen):
    """Keep the complete V1 import frozen and use its independently pinned RGB."""
    prior = repo / V1_SOURCE
    require(sha(read_regular(prior / 'inventory.json')) == V1_FREEZE, 'historical V1 inventory mismatch')
    old = load(prior / 'inventory.json')
    expected = dict(old['inputs'], **{'inventory.json': V1_FREEZE,
        'output/rebuild-receipt.json': 'b28fe7b72c7b7e7192ac682b3f37951a9f28e5ccb6c17e0e2c5dff9491691006'})
    expected.update({f'output/enemy-newsh4-{r["base"]}-8.{ext}': r[ext.upper() + '_SHA256']
                     for r in old['outputs'] for ext in ['hda', 'png']})
    nodes = list(prior.rglob('*'))
    require(all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in nodes), 'historical V1 special file')
    require({p.relative_to(prior).as_posix() for p in nodes if p.is_file()} == set(expected), 'historical V1 inventory differs')
    for name, digest in expected.items():
        safe_relative(name)
        require(sha(read_regular(prior / name)) == digest, 'historical V1 file mismatch: ' + name)
    for name in frozen['inputs']:
        if name.startswith('base-v1/'):
            require(read_regular(source / name) == read_regular(prior / name[len('base-v1/'):]),
                    'embedded V1 input differs: ' + name)
    return {r['base']: Image.frombytes('RGBA', (192,224),
                validate_hda(read_regular(prior / f'output/enemy-newsh4-{r["base"]}-8.hda'), r['base'], r))
            for r in old['outputs']}


def coverage_mask(source, name, base):
    with Image.open(source / f'coverage/{name}-{base}.png') as mask:
        require(mask.mode == 'L' and mask.size == (192,224) and set(mask.tobytes()) <= {0,255},
                'coverage mask shape or values mismatch')
        return np.asarray(mask).copy() != 0


def validate_coverage(source, base, image, logical, old, row):
    actual, previous = np.asarray(image), np.asarray(old)
    support = np.asarray(logical.resize((192,224), Image.Resampling.NEAREST)) != 0
    alpha, prior_alpha = actual[:,:,3], previous[:,:,3]
    editable, locked = coverage_mask(source, 'editable', base), coverage_mask(source, 'locked', base)
    require(np.array_equal(prior_alpha, support.astype('uint8') * 255), 'V1 nearest8 support mismatch')
    require(np.array_equal(actual[:,:,:3], previous[:,:,:3]), 'V2 RGB differs from V1 including transparent RGB')
    require(not np.any((alpha != 0) & ~support), 'V2 alpha expands original support')
    require(not np.any(editable & locked) and np.array_equal(editable | locked, support),
            'editable/locked support partition mismatch')
    require(np.array_equal(alpha[~editable], prior_alpha[~editable]), 'V2 alpha changed outside editable mask')
    require(np.array_equal(alpha[locked], prior_alpha[locked]), 'V2 protected alpha differs')
    stats = {'RGB_identical':True, 'outside_support':0, 'protected_interior_exact':True,
             'changed_alpha':int(np.count_nonzero(alpha != prior_alpha)),
             'fractional':int(np.count_nonzero((alpha > 0) & (alpha < 255))),
             'old_mass':int(prior_alpha.sum()), 'new_mass':int(alpha.sum())}
    require(exact_json({k:row[k] for k in stats}, stats), 'alpha proof statistics mismatch')


def validate_state_joins(source, images, logical):
    audit = load(source / 'base-v1/proof/source-contract.json')
    proof = load(source / 'state-join-proof.json')
    require(len(audit['states']) == len(proof['states']) == 21, 'whole-state count mismatch')
    components = {c['record']:c for c in audit['components']}
    for state, row in zip(audit['states'], proof['states']):
        assembled = Image.new('RGBA', (960,896))
        support = Image.new('L', (960,896))
        for record in audit['draw_order_if_all_allocations_succeed']:
            base = state['record_to_base'].get(str(record))
            if base is None:
                continue
            xy = tuple(v * 8 for v in components[record]['assembly_origin'])
            assembled.alpha_composite(images[base], xy)
            piece = Image.new('L', support.size)
            piece.paste(logical[base].resize((192,224), Image.Resampling.NEAREST), xy)
            support = ImageChops.lighter(support, piece)
        alpha = np.asarray(assembled.getchannel('A'))
        union = np.asarray(support) != 0
        locked = union & (distance_transform_edt(union) > 16)
        require(not np.any((alpha != 0) & ~union), 'whole-state support expanded')
        require(np.all(alpha[locked] == 255), 'whole-state protected interior changed')
        require(exact_json(row, {'state':state['name'], 'no_expansion':True,
                    'whole_state_protected_interior_exact':True, 'alpha_sha256':sha(alpha.tobytes())}),
                'whole-state alpha proof mismatch: ' + state['name'])
    first = images[CENTER[0]].getchannel('A').tobytes()
    require(all(images[b].getchannel('A').tobytes() == first for b in CENTER), 'center-eight alpha mismatch')


def reproduce_generated_only(source, work):
    """Independent recipe: only generated RGB masters and structural masks.

    No V1/V2 frozen output, original RGB/index/palette or claimed proof is an
    input to reconstruction. Frozen output bytes are used only for comparison.
    """
    generated = work / 'generated-only-source'
    generated.mkdir()
    for relative in GENERATED_ONLY:
        target = generated / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / 'base-v1' / relative, target)
        require(not target.samefile(source / 'base-v1' / relative), 'independent rebuild hardlink forbidden')
    rebuilt = work / 'generated-v1-output'
    result = subprocess.run([sys.executable,str(generated / 'rebuild.py'),str(rebuilt)],
                            capture_output=True,text=True,timeout=90)
    require(result.returncode == 0, 'independent V1 recipe failed: ' + result.stdout + result.stderr)
    audit = load(generated / 'proof/source-contract.json')
    registration = load(generated / 'proof/intact-registration.json')
    def registered(filename):
        with Image.open(generated / 'sources' / filename) as im:
            source_box, generated_box = registration['source_bbox'], registration['generated_bbox']
            result = Image.new('RGBA',(960,896))
            result.alpha_composite(im.convert('RGBA').crop(generated_box).resize(
                ((source_box[2]-source_box[0])*8,(source_box[3]-source_box[1])*8), Image.Resampling.LANCZOS),
                (source_box[0]*8,source_box[1]*8))
            return result
    intact = registered('generated-intact-v2.png')
    with Image.open(generated / 'masks/damage-change-mask8x.png') as mask:
        damaged = Image.composite(registered('generated-damage.png'), intact, mask.convert('L'))
    fields = {}
    for label, master in [('intact',intact),('damage',damaged)]:
        with Image.open(generated / f'masks/{label}-alpha.png') as im:
            support = np.asarray(im.resize((960,896), Image.Resampling.NEAREST)) != 0
        distance = distance_transform_edt(support)
        edge = np.clip((gaussian_filter(support.astype(float),4)-0.60)/0.15,0,1)
        transition = np.clip((distance-12)/4,0,1)
        coverage = np.minimum(np.asarray(master.getchannel('A'),dtype=float)/255,edge)
        alpha = np.where(support,np.round(255*(coverage*(1-transition)+transition)),0).astype('uint8')
        alpha[distance > 16] = 255
        fields[label] = (alpha,support & (distance <= 16),support & (distance > 16))
        require(Image.fromarray(alpha).tobytes() == Image.open(source / f'coverage/{label}-whole-alpha.png').tobytes(),
                'independent whole-field alpha differs')
    pieces = {}
    for component in audit['components']:
        x,y = component['assembly_origin']
        for label,base in [('intact',component['intact_base']),('damage',component.get('damage_base'))]:
            if base is not None and not (label == 'damage' and base == component['intact_base']):
                pieces[base] = tuple(a[y*8:(y+28)*8,x*8:(x+24)*8].copy() for a in fields[label])
    for base in CENTER[1:]: pieces[base] = pieces[1]
    pieces[280] = pieces[128]
    for base in EMPTY: pieces[base] = (np.zeros((224,192),dtype='uint8'),np.zeros((224,192),bool),np.zeros((224,192),bool))
    outputs = work / 'independent-v2-output'
    outputs.mkdir()
    for base in ALL_IDS:
        name = f'enemy-newsh4-{base}-8'
        with Image.open(rebuilt / (name+'.png')) as im:
            pixels = np.array(im)
        alpha,editable,locked = pieces[base]
        require(np.array_equal(editable,coverage_mask(source,'editable',base)) and
                np.array_equal(locked,coverage_mask(source,'locked',base)), 'independent editable/locked masks differ')
        pixels[:,:,3] = alpha
        image = Image.fromarray(pixels)
        image.save(outputs / (name+'.png'))
        (outputs / (name+'.hda')).write_bytes(b'HDR1'+struct.pack('<6I',1020000+base,8,24,28,6,7)+image.tobytes())
        for ext in ['png','hda']:
            require(read_regular(outputs / (name+'.'+ext)) == read_regular(source / 'output' / (name+'.'+ext)),
                    'independent V2 reconstruction differs: ' + name+'.'+ext)
    return {'generated_only_input_count':len(GENERATED_ONLY), 'exact_pairs':43,
            'original_RGB_inputs':False, 'frozen_output_inputs':False}


def validate_art_and_bindings(repo, source, manifest, frozen):
    family = manifest[FAMILY]
    require(exact_json({k: v for k, v in family.items() if k not in ['entries', 'runtime_status']},
                       expected_family()), 'family metadata mismatch')
    require(len(family['entries']) == 40, 'exact forty entries required')
    contract = load(source / 'contract.json')
    for key, value in {'schema': 'formal-boss-whole-family-v2-inward-alpha', 'bank': 'newsh4.shp', 'bank_id': 2,
        'asset_namespace': 102, 'bases': ALL_IDS, 'logical_part_size': [24, 28], 'pixel_part_size': [192, 224],
        'density': 8, 'anchor': [6, 7], 'runtime_quadrants': PARTS, 'nonempty_count': 40,
        'intentional_empty_bases': EMPTY, 'identical_pairs': [[128, 280]], 'center_cycle': CENTER,
        'center_patch8x': [78,166,114,202]}.items():
        require(exact_json(contract[key], value), 'source contract scope mismatch: ' + key)
    audit = load(source / 'base-v1/proof/source-contract.json')
    require([c['record'] for c in audit['components']] == list(range(46, 66)) and
            sorted({b for c in audit['components'] for b in c['all_bases']}) == ALL_IDS and
            audit['empty_bases'] == EMPTY, 'finite source-record map mismatch')
    require([manifest['default_preview_pack'], manifest['default_debug_pack']] == DEFAULTS,
            'two established default packs required')
    for pack_name, pack in manifest['packs'].items():
        require(len(safe_relative(pack_name).parts) == 1, 'unsafe pack name')
        for name, row in pack['files'].items():
            require(len(safe_relative(name).parts) == 1, 'unsafe pack filename')
            safe_relative(row['source_png'])
    v1 = historical_v1(repo, source, frozen)
    logical, images, canonical_paths, outputs = {}, {}, set(), []
    for row, proof in zip(frozen['outputs'], audit['frame_metadata']):
        base = row['base']
        require(proof['base'] == base, 'output scope mismatch')
        name = f'enemy-newsh4-{base}-8'
        raw = read_regular(source / 'output' / (name + '.hda'))
        rgba = validate_hda(raw, base, row)
        png = read_regular(source / 'output' / (name + '.png'))
        require(sha(png) == row['PNG_SHA256'], 'frozen PNG hash mismatch')
        with Image.open(source / 'output' / (name + '.png')) as im:
            require(im.mode == 'RGBA' and im.size == (192, 224) and im.tobytes() == rgba,
                    'PNG/RGBA/HDR1 disagreement')
            images[base] = im.copy()
        with Image.open(source / f'base-v1/masks/mask-newsh4-{base}.png') as mask:
            require(mask.mode == 'L' and mask.size == (24, 28) and set(mask.tobytes()) <= {0, 255},
                    'logical support mask mismatch')
            logical[base] = mask.copy()
        alpha = logical[base].tobytes()
        require(sha(alpha) == proof['mask_sha256'] and alpha.count(255) == proof['opaque_pixels']
                and (list(logical[base].getbbox()) if logical[base].getbbox() else None) == proof['bbox'],
                'source alpha proof mismatch')
        validate_coverage(source, base, images[base], logical[base], v1[base], row)
        require((alpha.count(255) == 0) == (base in EMPTY), 'forty nonempty / three empty mismatch')
        if base in EMPTY:
            require(rgba == bytes(len(rgba)), 'intentional empty RGBA mismatch')
            continue
        slot = 422 + IDS.index(base)
        entry = family['entries'][IDS.index(base)]
        require(exact_json(entry, {'id': base, 'slot': slot, 'HDA_sha256': sha(raw), 'RGBA_FNV1a64': fnv1a(rgba)}),
                'entry/FNV binding mismatch')
        canonical = f'assets/hd/source/{name}-{sha(raw)[:12]}.png'
        canonical_paths.add(canonical)
        require(read_regular(repo / canonical) == png, 'canonical PNG mismatch: ' + canonical)
        require(exact_json(manifest['source_pngs'][sha(raw)], {'path': canonical, 'sha256': sha(png), 'RGBA_sha256': sha(rgba)}),
                'source PNG index mismatch')
        for pack_name in DEFAULTS:
            packed = manifest['packs'][pack_name]['files'][name + '.hda']
            require(exact_json(packed, {'header_u32': [1020000 + base,8,24,28,6,7], 'sha256': sha(raw),
                                       'source_png': canonical, 'source_png_sha256': sha(png)}), 'packed metadata mismatch')
            validate_hda(read_regular(repo / 'assets/hd/packs' / pack_name / (name + '.hda')), base, row)
        outputs.append(dict(row, slot=slot, RGBA_FNV1a64=entry['RGBA_FNV1a64'], opaque_logical_cells=alpha.count(255)))
    require(images[128].tobytes() == images[280].tobytes() and
            read_regular(source / 'output/enemy-newsh4-128-8.png') == read_regular(source / 'output/enemy-newsh4-280-8.png'),
            '128/280 pixel alias mismatch')
    require(read_regular(source / 'output/enemy-newsh4-128-8.hda') != read_regular(source / 'output/enemy-newsh4-280-8.hda'),
            '128/280 distinct logical header identities required')
    for base in CENTER[1:]:
        difference = ImageChops.difference(images[1], images[base])
        difference.paste((0,0,0,0), (78,166,114,202))
        require(not any(difference.tobytes()), 'center common structure changed outside approved patch')
    validate_state_joins(source, images, logical)
    hashes = {r['HDA_SHA256'] for r in frozen['outputs']}
    png_hashes = {r['PNG_SHA256'] for r in frozen['outputs']}
    rgba_hashes = {r['RGBA_SHA256'] for r in frozen['outputs']}
    indexed = set()
    for digest, entry in manifest['source_pngs'].items():
        safe_relative(entry['path'])
        if (digest in hashes or entry['sha256'] in png_hashes or entry['RGBA_sha256'] in rgba_hashes
                or family_name(PurePosixPath(entry['path']).name, png=True)):
            indexed.add(digest)
    require(indexed == {r['HDA_SHA256'] for r in frozen['outputs'] if r['base'] not in EMPTY}, 'widened source PNG index')
    allowed = {f'enemy-newsh4-{base}-8.hda' for base in IDS}
    for pack_name, pack in manifest['packs'].items():
        require(type(pack['count']) is int and pack['count'] == len(pack['files']), 'pack count mismatch')
        relevant = {name for name, entry in pack['files'].items()
                    if family_name(name) or entry['header_u32'][0] in KEYS or entry['sha256'] in hashes}
        require(relevant == (allowed if pack_name in DEFAULTS else set()), 'widened pack alias or density')
    pack_root, actual = repo / 'assets/hd/packs', set()
    no_symlinks(pack_root)
    for path in pack_root.rglob('*'):
        require(not path.is_symlink() and (path.is_file() or path.is_dir()), 'pack inventory symlink or special file forbidden')
        if path.is_file():
            with path.open('rb') as handle:
                header = handle.read(8)
            key_matches = len(header) == 8 and header[:4] == b'HDR1' and struct.unpack('<I', header[4:])[0] in KEYS
            if family_name(path.name) or key_matches:
                actual.add(path.relative_to(pack_root).as_posix())
    require(actual == {f'{pack}/{name}' for pack in DEFAULTS for name in allowed}, 'widened on-disk pack inventory')
    source_root, actual_pngs = repo / 'assets/hd/source', set()
    no_symlinks(source_root)
    for path in source_root.rglob('*'):
        require(not path.is_symlink() and (path.is_file() or path.is_dir()), 'canonical source symlink or special file forbidden')
        if path.is_file() and (family_name(path.name, png=True) or sha(read_regular(path)) in png_hashes):
            actual_pngs.add(path.relative_to(repo).as_posix())
    require(actual_pngs == canonical_paths, 'widened canonical PNG inventory')
    return logical, outputs


def verify_originals(repo, source, root, logical):
    data = {}
    for name, digest in ORIGINAL_HASHES.items():
        path = root / name
        no_symlinks(path)
        require(path.is_file(), 'original data must be regular file: ' + name)
        data[name] = read_regular(path)
        require(sha(data[name]) == digest, 'original-data identity mismatch: ' + name)
    audit = load(source / 'base-v1/proof/source-contract.json')
    for name, digest in READERS.items():
        require(sha(read_regular(repo / name)) == digest, 'source reader pin mismatch: ' + name)
    original = data['newsh4.shp']
    cells = {}
    for proof in audit['frame_metadata']:
        mask, indices = Image.new('L', (24,28)), Image.new('L', (24,28))
        for cell in proof['cells']:
            tile_id = cell['id']
            start = struct.unpack_from('<H', original, 2 * (tile_id - 1))[0]
            pos, linear = start, 0
            alpha, index = bytearray(168), bytearray(168)
            while True:
                require(pos < len(original), 'RLE missing terminator')
                code = original[pos]
                pos += 1
                if code == 15:
                    break
                linear += code & 15
                count = code >> 4
                require(0 <= linear <= 168 and linear + count <= 168 and pos + count <= len(original),
                        'RLE exceeds 12x14/source')
                alpha[linear:linear + count] = b'\xff' * count
                index[linear:linear + count] = original[pos:pos + count]
                linear += count
                pos += count
            require(start == cell['offset'] and pos - start == cell['encoded_bytes'] and
                    sha(original[start:pos]) == cell['encoded_sha256'] and sha(alpha) == cell['mask_sha256'] and
                    sha(index) == cell['index_sha256'] and alpha.count(255) == cell['opaque_pixels'] and
                    all(i for a, i in zip(alpha, index) if a), 'RLE source cell mismatch')
            require(cell['part'] in PARTS and cell['id'] == proof['base'] + cell['part'], 'source quadrant mismatch')
            xy = (12 if cell['part'] in [1,20] else 0, 14 if cell['part'] in [19,20] else 0)
            require(list(xy) == cell['offset_xy'], 'source quadrant origin mismatch')
            mask.paste(Image.frombytes('L',(12,14),bytes(alpha)), xy)
            indices.paste(Image.frombytes('L',(12,14),bytes(index)), xy)
            cells[tile_id] = bytes(alpha)
        require(mask.tobytes() == logical[proof['base']].tobytes() and sha(mask.tobytes()) == proof['mask_sha256']
                and sha(indices.tobytes()) == proof['index_sha256'], 'RLE composite/source mask mismatch')
    require(len(cells) == audit['source_tile_count'] == 172, 'finite source tile inventory mismatch')
    reader = (repo / 'src/episodes.c').read_text()
    formats = {'u8':'B', 's8':'b', 'u16':'H', 's16':'h'}
    def schema(var):
        pattern = r'fread_(u8|s8|u16|s16)_die\(\s*&?' + var + r'\[i\]\.(\w+),\s*(\d+),\s*f\)'
        return [(m[2], formats[m[1]], int(m[3])) for m in re.finditer(pattern, reader)]
    ws, es = schema('weapons'), schema('enemyDat')
    require(len(es) == 28 and ws, 'HDT reader schema mismatch')
    hdt, pos = data['tyrian.hdt'], struct.unpack_from('<i', data['tyrian.hdt'])[0] + 14
    def decode(sc, ids):
        nonlocal pos
        records = {}
        for record_id in ids:
            record = {'id': record_id}
            for name, fmt, n in sc:
                values = list(struct.unpack_from('<' + str(n) + fmt, hdt, pos))
                pos += n * struct.calcsize(fmt)
                record[name] = values[0] if n == 1 else values
            records[record_id] = record
        return records
    weapons = decode(ws, list(range(819)) + list(range(1000,1819)))
    pos += 61 * 82 + sum(n * size for n, size in [(55,37),(7,37),(19,41),(38,86),(12,37)])
    records = decode(es, list(range(851)) + list(range(1001,1851)))
    require(len(records) == audit['decoded_record_count'] == 1701, 'HDT record count mismatch')
    def frame_set(record):
        bases = set(record['egraphic']) - {0,999}
        if record['dani'] == 0 and record['dgr']:
            bases.add(record['dgr'])
        return sorted(bases)
    for component in audit['components']:
        r = records[component['record']]
        require(r == component['source'] and frame_set(r) == component['all_bases'] and
                r['shapebank'] == 2 and r['esize'] == 1, 'source boss record/frame map mismatch')
    reuse = []
    for record_id, r in records.items():
        if r['shapebank'] != 2:
            continue
        bases = frame_set(r)
        used = {b + part for b in bases for part in (PARTS if r['esize'] == 1 else [0])}
        common = sorted(used & set(cells))
        if common:
            reuse.append({'record':record_id, 'boss_family':46 <= record_id <= 65,
                          'direct_base_matches':sorted(set(bases) & set(ALL_IDS)),
                          'raw_tile_matches':common,
                          'opaque_shared_tiles':[tile for tile in common if any(cells[tile])]})
    require(reuse == audit['raw_tile_reuse'], 'all-HDT raw tile reuse mismatch')
    require([r['record'] for r in reuse if not r['boss_family']] == [1,470,473], 'external source alias scope mismatch')
    require(all(weapons[int(k)] == v for k,v in audit['weapons'].items()) and
            records[3] == audit['launch_record'], 'source dependency records mismatch')
    level = data['tyrian1.lvl']
    n = struct.unpack_from('<H', level)[0]
    pos = struct.unpack_from('<' + str(n) + 'i', level, 2)[16] + 8
    n = struct.unpack_from('<H', level, pos)[0]
    pos += 2 + 2 * n
    n = struct.unpack_from('<H', level, pos)[0]
    pos += 2
    fields = ['eventtime','type','dat','dat2','dat3','dat5','dat6','dat4']
    events = [dict(zip(fields, struct.unpack_from('<HBhhbbbB', level, pos + i * 11)), index=i+1) for i in range(n)]
    require(n == 1010 and not [e for e in events if e['type'] in [49,50,51,52]], 'first-level source event scope mismatch')
    strip_prediction = lambda e: {k:v for k,v in e.items() if k != 'predicted_tick'}
    require([e for e in events if e['eventtime'] >= 5280] == [strip_prediction(e) for e in audit['events']],
            'source boss event sequence mismatch')
    spawn_types = [6,7,10,12,15,17,18,23,32,56]
    spawns = [e for e in events if e['type'] in spawn_types and 46 <= e['dat'] <= 65]
    require(len(spawns) == 20 and [e['dat'] for e in spawns] == audit['draw_order_if_all_allocations_succeed'],
            'source boss allocation order mismatch')
    for c in audit['components']:
        require(next(e for e in spawns if e['dat'] == c['record']) == strip_prediction(c['spawn_event']),
                'source spawn component mismatch')
    return {'data_hashes': ORIGINAL_HASHES, 'source_reader_hashes': READERS,
            'RLE_cells':len(cells), 'composites':43, 'finite_nonempty':40, 'intentional_empty':EMPTY,
            'HDT_records_audited':len(records), 'boss_records':20, 'all_raw_tile_reuse_verified':True,
            'external_alias_records':[1,470,473], 'first_level_events_decoded':len(events),
            'source_boss_spawn_order_verified':True, 'dependency_records_verified':[3,59,81,127],
            'predicted_tick_validation':False, 'original_RGB_art_inputs':False}


def validate(repo):
    """Read-only aggregate entrypoint; deterministic rebuild is the separate CLI gate."""
    repo = Path(repo).resolve()
    source = repo / SOURCE
    frozen = inventory(source)
    _, outputs = validate_art_and_bindings(repo, source, load(repo / 'assets/hd/manifest.json'), frozen)
    return {'status':'PASS', 'nonempty_members':len(outputs), 'audit_only_empty_members':3,
            'frozen_files':FROZEN_FILES, 'source_inventory_sha256':FREEZE,
            'exact_payloads_headers_masks_and_finite_bindings':True, 'game_runs':0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--original-data', type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    out = safe_output(args.output, repo)
    root = original_root(args.original_data, repo) if args.original_data else None
    if root:
        require(out != root and root not in out.parents and out not in root.parents, 'output must not overlap original data')
    source = repo / SOURCE
    frozen = inventory(source)
    logical, outputs = validate_art_and_bindings(repo, source, load(repo / 'assets/hd/manifest.json'), frozen)
    original_receipt = verify_originals(repo, source, root, logical) if root else None
    result = subprocess.run([sys.executable, str(source / 'rebuild.py'), str(out)], capture_output=True, text=True, timeout=90)
    require(result.returncode == 0, 'frozen rebuild failed: ' + result.stdout + result.stderr)
    expected = {p.name:read_regular(p) for p in (source / 'output').iterdir()}
    require({p.name for p in (out / 'output').iterdir()} == set(expected), 'rebuilt output inventory mismatch')
    for name, raw in expected.items():
        require(read_regular(out / 'output' / name) == raw, 'rebuilt frozen output mismatch: ' + name)
    for path in (source / 'coverage').iterdir():
        require(read_regular(out / 'coverage' / path.name) == read_regular(path), 'rebuilt coverage mismatch: ' + path.name)
    require(read_regular(out / 'alpha-proof.json') == read_regular(source / 'alpha-proof.json'), 'rebuilt alpha proof mismatch')
    with tempfile.TemporaryDirectory(prefix='boss-v2-independent-') as temporary:
        reproduce_generated_only(source, Path(temporary))
    print(json.dumps({'status':'PASS', 'source_inventory_sha256':FREEZE, 'art_contract_sha256':CONTRACT_SHA,
        'source_contract_sha256':SOURCE_CONTRACT_SHA, 'frozen_files':FROZEN_FILES, 'frozen_inputs':FROZEN_INPUTS,
        'closed_frozen_inventory':True, 'byte_exact_reproduction':True, 'exact_PNG_RGBA_HDR1_pairs':43,
        'finite_two_default_packs':True, 'finite_nonempty_slots':list(range(422,462)), 'audit_only_empty_bases':EMPTY,
        'alpha_anchors_RGBA_FNV_verified':True, 'transparent_RGB_preserved_exactly':True, 'all_RGB_exact_V1':True,
        'alpha_editable_locked_and_source_support_verified':True, 'independent_generated_only_reproduction':True,
        'whole_state_union_checks':21, 'prior_V1_receipts':'Historical only, not V2 runtime evidence',
        'center_structure_exact_outside_approved_patch':True, 'equal_128_280_pixels_distinct_HDR1_ids':True,
        'outputs':outputs, 'original_data':original_receipt, 'game_runs':0, 'captures':0, 'native_output':False,
        'runtime_acceptance':'Not established; body runtime, boss launch context and weapon81 closure remain separate.'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError,KeyError,TypeError,OSError,IndexError,struct.error,subprocess.SubprocessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
