#!/usr/bin/env python3
"""Bounded linked171 E1/physical12 density correction; no engine/state edits.
Requires Pillow and NumPy. Existing evidence verification is read-only.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
QUALIFIED_BINARY = 'b2685e56936f042c7daf2c678de0bf26d95fb4bb3bc875937660596f57e3b1d2'
# Fixed published identities, not hashes derived from user-supplied inputs.
DATA_SHA256 = {
    'tyrian1.lvl': '54cbb00b57b84aa992a70cfcb170cb1edeb59507873723630d60080ba8351352',
    'newshf.shp': '852c2fb552c9077a198be7902d8f58699ed070dabcd36c6e3acfe80dd3804cce',
    'tyrian.hdt': 'fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b',
    'palette.dat': 'f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0',
}
MASK_SHA256 = {
    'mask-43.png': '655aaa9efdf90fbebc84abc602fc31635453d4f389e456d566c8b5048cd7a3dc',
    'mask-81.png': '806b5a64666580a7cc9708ed0327e7ff468f097ab80da5374193886e56da9f84',
    'mask-119.png': 'c8ef6c1b536d37604b21f169b2c8572ea04e55252f19c12121a4799314cffe89',
    'mask-121.png': 'fa4fb2f9257d0d4af0e3a24a30d824bb96e7f19c97ebb5c32d99a8f50c71b775',
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def pinned_inputs(directory, expected):
    """Read only explicitly named inputs; never enumerate original-data folders."""
    result = {}
    for name, digest in expected.items():
        path = directory / name
        require(path.is_file(), 'Missing pinned input: ' + name)
        require(sha(path) == digest, 'Changed pinned input: ' + name)
        result[str(path)] = digest
    return result

def unchanged(inputs):
    require(all(Path(n).is_file() and sha(Path(n)) == h for n,h in inputs.items()),
            'Input bytes changed during run')

def actual_density(path, expected):
    audit = rows(path)
    require(len(audit) == 75, 'Expected exactly 75 RGB audit rows')
    require([int(r['tick']) for r in audit] == list(range(106, 181)), 'Unexpected RGB audit ticks')
    require({int(r['density']) for r in audit} == {expected}, 'Actual renderer density differs from requested density')
    return expected

def command(exe, data, assets, density):
    # The parser is intentionally order-sensitive: global-assets sets density8.
    # Explicit density MUST follow it; render-assets alone does not set density.
    return [str(exe), '--data=' + str(data), '--no-sound', '--no-joystick', '--no-xmas',
            '--asset-debug=custom', '--asset-debug-episode=1', '--asset-debug-level=12',
            '--asset-debug-tick=106', '--asset-debug-running', '--render-assets=' + str(assets),
            '--global-assets=' + str(assets), '--render-ticks=181',
            '--asset-debug-capture', '--asset-debug-capture-start=106',
            '--asset-debug-capture-count=75', '--asset-debug-window-only', '--render-test=' + str(density)]

def verify(out, density):
    import numpy as np
    from PIL import Image
    # This read-only mode verifies masks against published identities too.
    pinned_inputs(ROOT / 'authoring-inputs/newshf-linked', MASK_SHA256)
    present, missing = out / 'present', out / 'missing'
    for directory in (present, missing):
        actual_density(directory / 'rgb-audit.tsv', density)
        presentation = rows(directory / 'presentation.tsv')
        require(len(presentation) == 75 and all(int(r['present_calls']) == 1 and r['rng_before'] == r['rng_after'] for r in presentation), 'Unexpected Present/RNG')
    a, b = rows(present / 'state.tsv'), rows(missing / 'state.tsv')
    require(len(a) == len(b) == 181, 'Unexpected state length')
    require(all({k:v for k,v in x.items() if k != 'output_pixels'} == {k:v for k,v in y.items() if k != 'output_pixels'} for x,y in zip(a,b)), 'State/RNG mismatch')
    for name in ('enemy-projectiles.tsv', 'collisions.tsv', 'player-projectiles.tsv', 'player-shot-emissions.tsv', 'presentation.tsv'):
        require((present / name).read_bytes() == (missing / name).read_bytes(), 'Mismatch: ' + name)
    material = [r for r in rows(present / 'asset-debug-materials.tsv') if r['category'] == 'enemy' and r['sheet'] == 'newshf.shp' and r['id'] in ('43','45','81','83','119','121')]
    require({r['id'] for r in material} == {'43','81','119','121'}, 'Unexpected natural bases')
    require(all(r['coverage_mismatch'] == '0' for r in rows(present / 'frames.tsv')), 'Coverage mismatch')
    masks = {base:np.array(Image.open(ROOT / f'authoring-inputs/newshf-linked/mask-{base}.png')) > 0 for base in (43,81,119,121)}
    total = 0
    for tick in range(106,181):
        name = f'asset-debug-window-{tick:04d}.bmp'
        a, b = (np.array(Image.open(p / name).convert('RGB')) for p in (present, missing))
        require(a.shape == b.shape == (400,640,3), 'Expected native 640x400 window capture')
        diff = np.any(a != b, axis=2)
        allowed = np.zeros((200,320), bool)
        for row in material:
            if int(row['tick']) != tick:
                continue
            base = int(row['id']); part = int(row['tile_id']) - base
            require(part in (0,1,19,20), 'Unexpected native quadrant')
            dx = 12 if part in (1,20) else 0; dy = 14 if part in (19,20) else 0
            for yy,xx in np.argwhere(masks[base][dy:dy+14,dx:dx+12]):
                x = int(row['x']) - 24 + xx; y = int(row['y']) + yy
                if 0 <= x < 264 and 0 <= y < 184:
                    allowed[y,x] = True
        require(not np.any(diff & ~allowed.repeat(2,0).repeat(2,1)), 'Pixels outside same-tick native draw masks')
        total += int(diff.sum())
    require(total > 0, 'No HD difference observed')
    return dict(status='PASS', actual_density=density, window_pixels=[640,400], captured_frames_per_run=75,
                ticks=[106,180], changed_pixels=total, natural_bases=[43,81,119,121],
                state_rng_projectiles_collisions_presentation_equal=True, exact_native_support_only=True)

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--density', type=int, choices=(4,8), default=4)
    p.add_argument('--verify-existing', action='store_true', help='Read-only validation of an existing present/missing pair')
    for name in ('exe','data','assets','missing-assets','sdl-library-dir'):
        p.add_argument('--' + name, type=Path)
    p.add_argument('--expected-exe-sha256', default=QUALIFIED_BINARY)
    a = p.parse_args(argv); out = a.out.resolve()
    if a.verify_existing:
        print(json.dumps(verify(out,a.density), indent=2)); return
    require(all(getattr(a,n) is not None for n in ('exe','data','assets','missing_assets')), 'Run requires --exe/--data/--assets/--missing-assets')
    exe, data, assets, missing = (getattr(a,n).resolve() for n in ('exe','data','assets','missing_assets'))
    require(sha(exe) == a.expected_exe_sha256, 'Unexpected executable bytes')
    critical = pinned_inputs(data, DATA_SHA256)
    critical.update(pinned_inputs(ROOT / 'authoring-inputs/newshf-linked', MASK_SHA256))
    critical[str(Path(__file__).resolve())] = sha(Path(__file__).resolve())
    inventories = [{str(f.relative_to(d)):sha(f) for f in d.rglob('*') if f.is_file()} for d in (assets,missing)]
    extras = set(inventories[0]) - set(inventories[1])
    originals = ROOT / 'assets/hd/current-compat/newshf-linked'
    require(extras == {'newshf-linked/' + f.name for f in originals.glob('*.hda')}, 'Packs must differ only by six linked assets')
    require(all(inventories[0].get(n) == h for n,h in inventories[1].items()), 'Other pack bytes differ')
    require(all(sha(originals / Path(n).name) == inventories[0][n] for n in extras), 'Linked art differs from qualified source')
    inputs = {**critical, str(exe):sha(exe), **{str(d / n):h for d,inventory in zip((assets,missing),inventories) for n,h in inventory.items()}}
    out.mkdir(parents=True, exist_ok=False)
    (out / 'input-before.json').write_text(json.dumps(inputs,indent=2)+'\n')
    runs = []
    for variant,pack in (('present',assets),('missing',missing)):
        dest = out / variant; dest.mkdir()
        env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', SDL_RENDER_DRIVER='software', HOME=str(dest), XDG_CONFIG_HOME=str(dest / 'config'))
        if a.sdl_library_dir:
            env['LD_LIBRARY_PATH'] = str(a.sdl_library_dir.resolve())
        cmd = command(exe,data,pack,a.density)
        with (dest/'stdout.log').open('w') as stdout, (dest/'stderr.log').open('w') as stderr:
            result = subprocess.run(cmd,cwd=dest,env=env,stdout=stdout,stderr=stderr,timeout=240)
        require(result.returncode == 0, variant + ' run failed')
        actual_density(dest/'rgb-audit.tsv',a.density)
        captures = {f.name:sha(f) for f in dest.glob('*.bmp')}
        require(len(captures) == 75, 'Expected 75 captures')
        runs.append(dict(variant=variant,argv=cmd,exit=result.returncode,actual_density=a.density,captures=captures))
    receipt = verify(out,a.density)
    unchanged(inputs)
    receipt.update(binary_sha256=sha(exe),runs=runs,input_hashes_unchanged=True,
                   input_scope='Executable, both packs, four pinned critical original-data files, four published oracle masks, and this driver; not all original game files',
                   critical_original_data_sha256=DATA_SHA256, oracle_mask_sha256=MASK_SHA256,
                   driver_sha256=sha(Path(__file__).resolve()))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k != 'runs'},indent=2))

if __name__ == '__main__':
    main()
