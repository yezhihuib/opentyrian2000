#!/usr/bin/env python3
"""Opt-in original-data audit; never installs or publishes game assets.

Run with --data /private/game-data --out /fresh/private/output, outside this
checkout. The report contains hashes and test results, never original bytes.
The real compositor, scope, palette and display admission remain untested.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'experimental/level2-family/src'
BANK_SHA256 = '6e783ccf58eb55a4fad82cd1fb600968e1397f297d30398ac935c7f81dfd9cff'
BANK_FNV64 = 0x3c9578d713f73930
LIMITS = [
    'Synthetic backdrop and player state; SDL surface representation is stubbed.',
    'Scope, palette, source-surface geometry, writer/display preparation, asset loading and central family_pixel bridge are stubbed.',
    'Real original-bank RLE, production ps_source, ship callbacks and half-alpha writer are exercised.',
    'Neutral normal comparison uses direct indexed stores from frozen callback records, not the normal native RLE loop.',
    'No gameplay, full compositor admission, collision/damage simulation, real palette admission, final Present or visible-scene acceptance.',
    'Sanitizer availability is environment-dependent; this checker makes no independent leak-check claim.',
]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def validate_output(path):
    """Resolve symlinks before rejecting all checkout-contained destinations."""
    path = Path(path)
    resolved = path.resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError('--out must be outside the repository')
    if path.exists() or path.is_symlink():
        raise ValueError('--out must be a fresh, nonexistent directory')
    if not resolved.parent.is_dir():
        raise ValueError('--out parent must already be an existing private directory')
    return resolved


def load_bank(directory):
    path = Path(directory) / 'tyrian.shp'
    if not path.is_file():
        raise ValueError('missing original input: tyrian.shp')
    shp = path.read_bytes()
    if len(shp) < 54 or struct.unpack_from('<H', shp)[0] != 13:
        raise ValueError('invalid tyrian.shp offset header')
    positions = struct.unpack_from('<13I', shp, 2)
    if not all(54 <= value <= len(shp) for value in positions) or list(positions) != sorted(positions):
        raise ValueError('invalid tyrian.shp offset ranges')
    bank = shp[positions[8]:positions[9]]
    if len(bank) != 33484 or sha256(bank) != BANK_SHA256:
        raise ValueError('spriteSheet9 fingerprint mismatch: unsupported or corrupted original data')
    stamp = 0xcbf29ce484222325
    for byte in bank:
        stamp = ((stamp ^ byte) * 1099511628211) & ((1 << 64) - 1)
    if stamp != BANK_FNV64:
        raise ValueError('spriteSheet9 production FNV fingerprint mismatch')
    return shp, bank


def run_checks(shp, bank, out, report):
    spec = importlib.util.spec_from_file_location('original_harness', ROOT/'tests/test_player_ship_invulnerability.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    source = (SRC/'player_ship_family_mirror.inc').read_text()
    report['poses'] = []
    native = (SRC/'player_ship_native.inc').read_text()
    # Independently decode original four RLE tiles and compare full ordered records.
    for pose in (229,231,233,235,237):
        records=[]; ends=[]
        for part, delta in enumerate((0,1,19,20)):
            p, = struct.unpack_from('<H', bank, (pose+delta-1)*2)
            x=y=0
            while bank[p] != 15:
                code=bank[p]; p+=1; x+=code&15; n=code>>4
                if not n: y+=1; x-=12
                else:
                    for _ in range(n):
                        assert 0<=x<12 and 0<=y<14
                        records.append((x+12*(part%2),y+14*(part//2),bank[p])); x+=1;p+=1
            ends.append(len(records))
        table=re.search(r'ps_native_'+str(pose)+r'\[\d+\]=\{(.*?)\n\};',native,re.S).group(1)
        wanted=[tuple(map(int,v)) for v in re.findall(r'\{(\d+),(\d+),(\d+)\}',table)]
        assert records==wanted, pose
        declared=re.search(r'\{'+str(pose)+r',\d+,\{([^}]+)\}',native).group(1)
        assert ends==list(map(int,declared.split(',')))
        report['poses'].append({'pose': pose, 'callbacks': len(records), 'part_ends': ends})
    oracle=(m.ARCHIVE/'player_ship_native.inc').read_text()
    oracle=oracle[:oracle.index('static const PlayerShipSpec *ps_spec')]
    oracle=oracle[oracle.index('static const PlayerShipWrite'):]
    oracle=re.sub(r'typedef struct \{.*?\} PlayerShipSpec;', '', oracle, flags=re.S)
    oracle=oracle.replace('ps_native_','oracle_native_').replace('ps_specs','oracle_specs')
    names=('ps_fail','ps_reset','ps_art_current','ps_sample','ps_pose','ps_current','ps_body','ps_pixel','ps_end','ps_finish','ps_sprite2_blend_pixel')
    replacements={
    'NATIVE':native,
    'DECLARATIONS':source[source.index('static struct {PlayerShipDraw'):source.index('static const char *ps_root')],
    'REQUESTED':'#define B313_FAMILY_CANVAS_DIAGNOSTIC 1\n'+m.function(source,'ps_requested')+'\n'+m.function(source,'ps_invulnerable_requested'),
    'FUNCTIONS':m.function(source,'ps_source')+'\n'+'\n'.join(m.function(source,n) for n in names),
    'BLEND':m.function((SRC/'render_mirror.c').read_text(),'blend_rgba'),
    'STAMP':m.function((ROOT/'src/asteroid1_ten_mirror.inc').read_text(),'asteroid1_stamp'),
    'NATIVE_BLIT':m.function((ROOT/'src/sprite.c').read_text(),'blit_sprite2_blend'),
    'ORACLE':oracle}
    h=(ROOT/'tests/player_ship_invulnerability_harness.c.in').read_text()
    h=h.replace('static bool ps_source(Sprite2_array bank){return source_ok&&bank.data==spriteSheet9.data&&bank.size==spriteSheet9.size;}','')
    start=h.index('static Uint16 encoded[16742];'); end=h.index('static void start(',start)
    h=h[:start]+'''static Uint16 authentic[16742];
    static void make_bank(unsigned pose){(void)pose;spriteSheet9=(Sprite2_array){(Uint8 *)authentic,sizeof authentic};}
    '''+h[end:]
    h=h.replace('assert(argc==6);','''assert(argc==7);
     FILE *original=fopen(argv[6],"rb");assert(original);
     assert(fread(authentic,1,sizeof authentic,original)==sizeof authentic&&fgetc(original)==EOF);assert(!fclose(original));
     make_bank(0);assert(ps_source(spriteSheet9));
     Sprite2_array bad=spriteSheet9;bad.size--;assert(!ps_source(bad));
     bad=spriteSheet9;bad.data++;assert(!ps_source(bad));
     ((Uint8 *)authentic)[1000]^=1;assert(!ps_source(spriteSheet9));
     ((Uint8 *)authentic)[1000]^=1;assert(ps_source(spriteSheet9));''')
    h=h.replace('Synthetic bank, no authentic game data or gameplay.','Authentic original bank and real ps_source; admission/compositor stubs; no gameplay.')
    h=re.sub(r'\b('+'|'.join(replacements)+r')\b',lambda v:replacements[v[0]],h)
    assets=[ROOT/'assets/hd/current-compat/talon'/f'ship-{i}-8.hda' for i in (229,231,233,235,237)]
    report['inputs'] = {
        'tyrian.shp': {'sha256': sha256(shp), 'bytes': len(shp)},
        'spriteSheet9': {'sha256': sha256(bank), 'bytes': len(bank), 'fnv64': hex(BANK_FNV64)},
        'hda': {path.name: {'sha256': sha256(path.read_bytes()), 'bytes': path.stat().st_size} for path in assets},
    }
    report['harness_sha256'] = sha256(h.encode())
    flags = shlex.split(os.environ.get('SANITIZER_FLAGS', ''))
    report['sanitizer_flags'] = flags
    report['asan_options'] = os.environ.get('ASAN_OPTIONS', '')
    with tempfile.TemporaryDirectory(prefix='original-data-', dir=out) as temporary:
        temp = Path(temporary)
        (temp/'bank.bin').write_bytes(bank)
        (temp/'test.c').write_text(h)
        command = ['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-unused-variable', '-pedantic', '-I', str(SRC), str(temp/'test.c'), '-o', str(temp/'test')] + flags + ['-UNDEBUG']
        compile_result = subprocess.run(command, cwd=temp, capture_output=True, text=True)
        report['compile'] = {'returncode': compile_result.returncode, 'stdout': compile_result.stdout, 'stderr': compile_result.stderr}
        if compile_result.returncode:
            raise RuntimeError('C harness compilation failed; see report')
        env = dict(os.environ)
        env.pop('PLAYER_SHIP_TEST_PREVIEW_DIR', None)
        result = subprocess.run([str(temp/'test'), *map(str, assets), str(temp/'bank.bin')], env=env, cwd=temp, capture_output=True, text=True)
        report['execution'] = {'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
        if result.returncode:
            raise RuntimeError('C harness failed; see report')
    report['coverage'] = {'native_blend_callbacks': 2372, 'invulnerability_ticks': [1, 2], 'callback_rejection_modes': 14, 'source_rejections': ['pointer', 'length', 'byte corruption'], 'additional_rejections': ['incomplete draw', 'replayed callback', 'live opt-out']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(argv)
    if not __debug__:
        parser.error('run without Python -O: this audit relies on assertions')
    try:
        out = validate_output(args.out)
        out.mkdir(mode=0o700)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    report = {'schema_version': 1, 'status': 'failed', 'limits': LIMITS, 'checker_sha256': sha256(Path(__file__).read_bytes())}
    try:
        shp, bank = load_bank(args.data)
        run_checks(shp, bank, out, report)
        report['status'] = 'passed'
    except (OSError, ValueError, RuntimeError, AssertionError) as error:
        report['error'] = str(error) or type(error).__name__
    (out/'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"{report['status'].upper()}: {out/'report.json'}")
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
