#!/usr/bin/env python3
"""Finite C-v2 compatibility projection; never masks arbitrary source text.

Only the exact, ordered eight approved FNV replacements and the exact adjacent
comment replacement are accepted. Every other byte and every src path must
match the immutable native-tested pregame baseline. This module also pins each lane's C artwork.
"""
from pathlib import Path
import hashlib
import re
import struct
import subprocess

BASE = 'c9232d59778c8689d85f9e87e8fee260b4c3187a'
IDS = [39, 41, 43, 45, 91, 93, 129, 131]
OLD = ['63fd993042755636','f6583f60603839a3','4cd47c32a4b23eaa','e9d34663cade254d',
       'baa804b312e1f561','0fcf5a0c3f773e03','047bb0296b21548b','6db63fa17b194c7e']
NEW = ['cc3d8be70ed2e620','80d5e7bb507fe084','3228caecc8f7abe8','33f828b2c95baa5a',
       '452516abee3a1d95','c8296a713b1af965','1f937a94539eb9cb','b01b2fcfaa46aaf0']
OLD_COMMENT = b' * integrity stamps also pin the exact original alpha support. Failure stays'
NEW_COMMENT = b' * integrity stamps pin approved fractional contours and apertures. Failure stays'
HDA_SHA256 = {
 'v1': ['05ef7518703365fb05f86ac746679c547a45f8a5b45070ccd0729ae56afdb789','d4163c85bdc7ee1939e9d660b740d6e2d55aa89782f3e3f5924e268023347858','a9ddb87c4e992f35f979bd72b74224e222391143685698a328c6ac232a782024','7d1b67817748f18a872e0fd3e7d406fcc9368ff24cd4d21821b4a9738b2742ed','b155c5acbd304177806891b3016b424b68cfaebfcb5d59e7859974a64cea4782','b4dc068e25d0de509ae4dee737846ae379e3ca73a7a10561b8c5e274620547a0','d8c12921aacc495d6185f8cb3675a7b6cee2203b44892196c77919152f530772','95b80dffe530d276e446bb3716afeb2799dd2fe9f5db4c0f2f867750a0dbdbb0'],
 'v2': ['faa362385a6b7f67e7926df162d9b5df4df41aa492709562841e410fd77e2d6d','8d2f73e32e39be13e440ba8639f471ca1877dc476ac03b5ee60771741c2f515f','5874d9c67472bb9afa8e6be64480d33b0502ad4c035f8c985bb77ef7cfa00d66','3a20918ae6fffb966c9fc857a04a9b75a5554c961e622f6f7851db2d871f8af5','e2c3aaa833db864ae73b4cd611305043ddcefd89dda19d22a1b1d5d577b2c29f','c816a59f906bbf63af3707d7b183c7be8c39136613f60c0a9f8b4423d2622164','0369d6e3fdbe602f8e5caa51fa3834a434a1abd28c267674d4b7aa98005e3e56','7590d16a0c2378bca3d2ffb66c0279ede2c73ffcbc61383e83d582cdd03ad904']}
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def approved_candidate(baseline):
    """Construct the sole permitted source variant from the fixed baseline."""
    start = baseline.index(b'/* Approved type15 eight-heading bank1 family, selected-pack and 8x only.')
    end = baseline.index(b'\n/* Approved late spike ', start)
    block = baseline[start:end]
    old_row = ('static const uint64_t rgba_stamps[8]={' + ','.join('UINT64_C(0x'+v+')' for v in OLD) + '};').encode()
    new_row = ('static const uint64_t rgba_stamps[8]={' + ','.join('UINT64_C(0x'+v+')' for v in NEW) + '};').encode()
    assert block.count(old_row) == 1 and block.count(OLD_COMMENT) == 1
    block = block.replace(old_row, new_row).replace(OLD_COMMENT, NEW_COMMENT)
    return baseline[:start] + block + baseline[end:]

def project_render(current, baseline):
    if current == baseline:
        return baseline, 'v1'
    expected = approved_candidate(baseline)
    assert current == expected, 'Production render_mirror.c is not the exact approved eight-C-pin/comment transition'
    return baseline, 'v2'

def validate_sources(current, baseline):
    assert set(current) == set(baseline), 'Added/removed production source paths'
    projected, version = project_render(current['src/render_mirror.c'], baseline['src/render_mirror.c'])
    for name in baseline:
        raw = projected if name == 'src/render_mirror.c' else current[name]
        assert raw == baseline[name], 'Production source changed: ' + name
    return version

def audit_sources(repo):
    git = lambda *a: subprocess.check_output(['git', '-C', str(repo), *a])
    tracked = git('ls-tree', '-r', '--name-only', BASE, 'src').decode().splitlines()
    assert tracked
    baseline = {name: git('show', BASE+':'+name) for name in tracked}
    actual = {str(q.relative_to(repo)) for q in (repo/'src').rglob('*') if q.is_file() or q.is_symlink()}
    assert actual == set(tracked), 'Added/removed source paths: ' + repr(actual ^ set(tracked))
    for name in tracked:
        assert (repo/name).is_file() and not (repo/name).is_symlink(), 'Nonregular production source: '+name
    # First restore only the exact qualified portable-font output delta.
    import runpy
    portable = runpy.run_path(str(repo/'tests/red250_font_projection.py'))
    portable['verify']()
    current = {name: portable['project'](name, (repo/name).read_bytes()) for name in tracked}
    return current, baseline, validate_sources(current, baseline)

def rejection_tests(baseline):
    """Adversarial in-memory source maps: no source files are ever modified."""
    good = dict(baseline)
    good['src/render_mirror.c'] = approved_candidate(baseline['src/render_mirror.c'])
    assert validate_sources(good, baseline) == 'v2'
    assert validate_sources(baseline, baseline) == 'v1'
    changes = {}
    render = good['src/render_mirror.c']
    for i, value in enumerate(NEW):
        token = ('UINT64_C(0x'+value+')').encode()
        assert render.count(token) == 1
        changes[f'C-{IDS[i]}-altered-pin'] = render.replace(token, ('UINT64_C(0x'+value[:-1]+('0' if value[-1]!='0' else '1')+')').encode())
        changes[f'C-{IDS[i]}-missing-pin'] = render.replace(token, b'')
        changes[f'C-{IDS[i]}-substituted-old-pin'] = render.replace(token, ('UINT64_C(0x'+OLD[i]+')').encode())
        changes[f'C-{IDS[i]}-substituted-other-C-pin'] = render.replace(token, ('UINT64_C(0x'+NEW[(i+1)%8]+')').encode())
        j = (i+1)%8
        other = ('UINT64_C(0x'+NEW[j]+')').encode()
        changes[f'C-{IDS[i]}-reordered-pins'] = render.replace(token,b'PIN_SWAP').replace(other,token).replace(b'PIN_SWAP',other)
    neighbor = re.search(rb'UINT64_C\(0x[0-9a-f]{16}\)', render).group()
    assert neighbor not in [('UINT64_C(0x'+v+')').encode() for v in NEW]
    changes['neighboring-family-stamp'] = render.replace(neighbor, b'UINT64_C(0x0000000000000000)', 1)
    changes['other-render-byte'] = render + b'\n'
    changes['comment-reversion-with-v2-pins'] = render.replace(NEW_COMMENT,OLD_COMMENT)
    changes['comment-altered'] = render.replace(NEW_COMMENT,NEW_COMMENT+b' ')
    v1_comment_only = render
    for old,new in zip(OLD,NEW):
        v1_comment_only = v1_comment_only.replace(('UINT64_C(0x'+new+')').encode(),('UINT64_C(0x'+old+')').encode())
    changes['v1-pins-with-v2-comment'] = v1_comment_only
    passed = []
    for label, raw in changes.items():
        bad = dict(good);bad['src/render_mirror.c'] = raw
        try: validate_sources(bad, baseline)
        except AssertionError: passed.append(label)
        else: raise AssertionError('Accepted forbidden source mutation: '+label)
    for name in baseline:
        if name == 'src/render_mirror.c': continue
        bad = dict(good);bad[name] += b'\n'
        try: validate_sources(bad, baseline)
        except AssertionError: passed.append('other-production-byte:'+name)
        else: raise AssertionError('Accepted forbidden source mutation: '+name)
    for label in ['missing-source-path','added-source-path']:
        bad = dict(good)
        if label.startswith('missing'):del bad[next(iter(bad))]
        else:bad['src/forbidden-new-source.c'] = b''
        try: validate_sources(bad, baseline)
        except AssertionError: passed.append(label)
        else: raise AssertionError('Accepted forbidden source paths')
    return passed

def validate_pack(pack, version):
    result = {}
    for i, sprite_id in enumerate(IDS):
        name = f'enemy-newsh2-{sprite_id}-8.hda'
        raw = (pack/name).read_bytes()
        assert len(raw)==28+24*28*8*8*4 and raw[:4]==b'HDR1'
        assert struct.unpack('<6I',raw[4:28]) == (1010000+sprite_id,8,24,28,6,7)
        assert sha(raw)==HDA_SHA256[version][i], 'C art/source lane mismatch: '+str(pack/name)
        value = 0xcbf29ce484222325
        for byte in raw[28:]:value=((value^byte)*0x100000001b3)&0xffffffffffffffff
        assert f'{value:016x}' == (OLD if version=='v1' else NEW)[i]
        result[name] = sha(raw)
    return result

def baseline_pack(repo, pack, destination):
    """Read-only links into v1 C and current unchanged non-C resources."""
    destination.mkdir()
    old = repo/'assets/hd/artwork/type15-eightheading-v1/output'
    validate_pack(old, 'v1')
    members = {f'enemy-newsh2-{i}-8.hda' for i in IDS}
    for path in sorted(pack.glob('*.hda')):
        (destination/path.name).symlink_to(old/path.name if path.name in members else path)
    validate_pack(destination, 'v1')
    return destination
