#!/usr/bin/env python3
"""Bounded original-data ASTEROID2 static-HUD comparison on SDL software.

This diagnostic executable bypasses menus with a deterministic scene bootstrap,
then supplies sampled keys to the original movement/firing code. It never enables
probe/debug or alters game/render admission, original data, damage, RNG, actor
births or weapon origins. Native menus, physical input, GPU and Windows are NOT
qualified. Run the normal family builder first with the same toolchain variables.
All output, including private game screenshots, must stay outside this checkout.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PINNED_DATA = {
    'tyrian.shp': '80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0',
    'newshd.shp': '08c7c81b4ed590609f97347b1a4ec60aba56925ecc7193a6718c34cb8d698adf',
}
CAPTURE_TICKS = (1, 20, 40, 90, 99, 100, 101, 130, 180, 239, 320, 400, 500)
STATE_FIELDS = ('players', 'enemies', 'shots', 'particles', 'globals', 'rng',
                'native', 'output', 'x', 'y', 'inv', 'armor', 'shield')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_paths(data, out):
    if not data.is_dir():
        raise ValueError('An existing original-data directory is required.')
    if out == ROOT or ROOT in out.parents:
        raise ValueError('Diagnostic output must be outside the repository.')
    if out == data or data in out.parents or out in data.parents:
        raise ValueError('Diagnostic output must be separate from original data.')
    if out.exists():
        raise ValueError('Diagnostic output must be a fresh directory.')
    for name, digest in PINNED_DATA.items():
        path = data/name
        if not path.is_file() or sha(path) != digest:
            raise ValueError('Original input fingerprint mismatch: ' + name)


def instrument(texts):
    """Only bootstrap, sampled-input, end-tick and read-only hash observers."""
    texts = dict(texts)

    def replace(name, before, after):
        if texts[name].count(before) != 1:
            raise ValueError('Source hook changed: ' + name)
        texts[name] = texts[name].replace(before, after)

    replace('opentyr.c', '#ifdef NDEBUG\n\tif (!isNetworkGame && !game_probe_enabled)', '''
 /* Diagnostic bootstrap: native loader, no menu or save-load qualification. */
 mt_srand(0x5eedUL); JE_initEpisode(1); JE_initPlayerData();
 mainLevel=6; initial_episode_num=1; difficultyLevel=DIFFICULTY_NORMAL;
 inputDevice[0]=1; play_demo=false; stopped_demo=false; gameLoaded=false; jumpSection=false;
 JE_main(); JE_tyrianHalt(0); return 0;
#ifdef NDEBUG
\tif (!isNetworkGame && !game_probe_enabled)''')
    replace('mainint.c', '\t\t\t\t/* keyboard input */',
            '\t\t\t\textern void original_test_input(void); original_test_input();\n'
            '\t\t\t\t/* keyboard input */')
    replace('tyrian2.c', '\tb313_facts_snapshot("tick_end",0);',
            '\tb313_facts_snapshot("tick_end",0);\n'
            ' extern bool original_test_end(void); if(original_test_end())'
            '{b313_family_observer_finish(4);render_mirror_family_report();return;}')
    texts['game_probe.c'] += '''
/* Observer only; game_probe_enabled stays false. */
void original_test_state(FILE *f) {
 fprintf(f,"%016llx,%016llx,%016llx,%016llx,%016llx,%016llx,%016llx,%016llx",
 (unsigned long long)players_hash(),(unsigned long long)enemies_hash(),
 (unsigned long long)shots_hash(),(unsigned long long)particles_hash(),
 (unsigned long long)globals_hash(),(unsigned long long)mt_state_fingerprint(),
 (unsigned long long)surface_hash(game_screen),(unsigned long long)surface_hash(VGAScreenSeg));
}
'''
    return texts


def compare(out, ticks, scale):
    from PIL import Image, ImageChops
    states={}
    presents={}
    for mode in ('on','off'):
        with (out/mode/'state.csv').open() as stream:states[mode]=list(csv.DictReader(stream))
        with (out/mode/'hud-present.csv').open() as stream:presents[mode]=list(csv.DictReader(stream))
    if any(len(rows)!=ticks for rows in states.values()):raise AssertionError('Incomplete bounded scene.')
    for tick,(on,off) in enumerate(zip(states['on'],states['off'])):
        if int(on['tick'])!=tick or int(off['tick'])!=tick:raise AssertionError('Out-of-order tick.')
        for field in STATE_FIELDS:
            if on[field]!=off[field]:raise AssertionError(f'Native state changed at {tick}: {field}')
        for field in ('family_presents','terrain_presents'):
            if on[field]!=off[field]:raise AssertionError('HUD changed scene admission: '+field)
    if len(presents['on'])!=ticks or len(presents['off'])!=ticks:raise AssertionError('Missing native Present.')
    for on,off in zip(presents['on'],presents['off']):
        for field in ('tick','scene_accepted','terrain_presenting','terrain_cells','playfield_hash'):
            if on[field]!=off[field]:raise AssertionError('HUD changed the actual playfield: '+field+' at '+on['tick'])
        if int(on['owned_pixels'])<20000 or int(on['hud_mismatches']) or int(on['unowned_mismatches']):
            raise AssertionError('Authored border missing or native HUD altered at '+on['tick']+': '+str(on))
        if int(off['owned_pixels']) or int(off['unowned_mismatches']):raise AssertionError('Feature-off HUD changed.')
    captures=[]
    for name in sorted(p.name for p in (out/'on').glob('frame-*.ppm')):
        with Image.open(out/'on'/name) as on,Image.open(out/'off'/name) as off:
            if on.size!=(320*scale,200*scale) or off.size!=on.size:raise AssertionError('Wrong scaling.')
            if ImageChops.difference(on.crop((0,0,264*scale,184*scale)),off.crop((0,0,264*scale,184*scale))).getbbox():
                raise AssertionError('Captured playfield changed.')
            bounds=ImageChops.difference(on,off).getbbox()
            if not bounds:raise AssertionError('Static border was not visible.')
        captures.append({'name':name,'difference_bounds':bounds,'on_sha256':sha(out/'on'/name),'off_sha256':sha(out/'off'/name)})
    modes=[]
    for row in presents['on']:
        family=bool(int(row['scene_accepted']));terrain=bool(int(row['terrain_presenting']))
        if family and terrain:raise AssertionError('Overlapping actual Present ownership.')
        modes.append('family' if family else 'terrain' if terrain else 'native')
    runs=[]
    for tick,mode in enumerate(modes):
        if runs and runs[-1]['mode']==mode:runs[-1]['last']=tick
        else:runs.append({'first':tick,'last':tick,'mode':mode})
    family_frames=modes.count('family');terrain_frames=modes.count('terrain')
    if int(states['on'][-1]['family_presents'])!=family_frames:raise AssertionError('Family Present counter mismatch.')
    if int(states['on'][-1]['terrain_presents'])!=terrain_frames:raise AssertionError('Terrain Present counter mismatch.')
    return {'native_state_comparisons':ticks*len(STATE_FIELDS),'hud_visible_frames':len(presents['on']),
            'scene_hd_frames':family_frames,'scene_family_hd_frames':family_frames,
            'terrain_only_hd_frames':terrain_frames,'combined_hd_frames':family_frames+terrain_frames,
            'scene_native_fallback_frames':modes.count('native'),
            'scene_mode_switches':sum(a!=b for a,b in zip(modes,modes[1:])),
            'hd_classic_switches':sum((a=='native')!=(b=='native') for a,b in zip(modes,modes[1:])),
            'scene_presentation_runs':runs,
            'minimum_hud_owned_native_pixels':min(int(r['owned_pixels']) for r in presents['on']),
            'hud_mismatches':0,'unowned_hud_mismatches':0,'playfield_hashes_equal':True,'captures':captures}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--scale', type=int, choices=(2, 4), default=2)
    parser.add_argument('--ticks', type=int, choices=(240, 540), default=540)
    parser.add_argument('--build-receipt', type=Path, help='Verified immutable staged build; default requires current source')
    parser.add_argument('--terrain-fallback', action='store_true', help='Enable identical independent terrain fallback in both HUD runs')
    args = parser.parse_args(argv)
    data, out = args.data.resolve(), args.out.resolve()
    validate_paths(data, out)
    data_before = {p.name: sha(p) for p in data.iterdir() if p.is_file()}
    env = dict(os.environ)
    if args.build_receipt:
        receipt_path=args.build_receipt.resolve()
        build=json.loads(receipt_path.read_text())
        stage=receipt_path.parent
        if stage!=Path(build['stage']):raise ValueError('Build receipt moved from its original stage.')
        plan=build
    else:
        plan = json.loads(subprocess.check_output(
            [sys.executable, 'scripts/build_level2_family.py', '--check-only'],
            cwd=ROOT, env=env, text=True))
        stage = Path(plan['stage'])
        build = json.loads((stage/'BUILD.json').read_text())
        if any(plan[key] != build[key] for key in ('source_sha256', 'asset_header_sha256', 'compiler', 'cppflags', 'cflags', 'ldflags', 'libs')):
            raise ValueError('Rebuild the family binary with the current source/toolchain first.')
    for name, digest in build['source_sha256'].items():
        if sha(stage/'src'/name) != digest:
            raise ValueError('Changed staged source: ' + name)
    for name, digest in build['asset_header_sha256'].items():
        if sha(stage/'assets'/name) != digest:
            raise ValueError('Changed staged header: ' + name)
    for name, digest in build['object_sha256'].items():
        if sha(stage/'obj'/name) != digest:
            raise ValueError('Changed object: ' + name)
    terrain_observer='b313_terrain_fallback.h' in build['source_sha256']
    if args.terrain_fallback and not terrain_observer:
        raise ValueError('This immutable build has no terrain fallback.')
    if sha(stage/'opentyrian2000-family')!=build['binary_sha256']:
        raise ValueError('Changed staged binary.')
    out.mkdir(mode=0o700)
    (out/'src').mkdir()
    units = ('opentyr.c', 'mainint.c', 'tyrian2.c', 'game_probe.c')
    texts = instrument({name: (stage/'src'/name).read_text() for name in units})
    texts['observe.c'] = (ROOT/'tests/fixtures/family_static_hud_scene_observer.c').read_text()
    report = {'status': 'RUNNING', 'scope': __doc__, 'source_digest': plan['source_digest'],
              'original_data_sha256': data_before, 'scale': args.scale, 'ticks': args.ticks,
              'terrain_fallback_enabled': args.terrain_fallback,
              'staged_binary_sha256': build['binary_sha256'],
              'instrumented_source_sha256': {}, 'commands': [],
              'checker_sha256': sha(Path(__file__)),
              'observer_template_sha256': sha(ROOT/'tests/fixtures/family_static_hud_scene_observer.c')}

    def save():
        (out/'receipt.json').write_text(json.dumps(report, indent=2)+'\n')

    def run(command, label, environment=env, cwd=ROOT):
        report['commands'].append({'label': label, 'argv': command, 'cwd': str(cwd)})
        save()
        with (out/(label+'.stdout')).open('w') as stdout, (out/(label+'.stderr')).open('w') as stderr:
            result = subprocess.run(command, cwd=cwd, env=environment, stdout=stdout,
                                    stderr=stderr, timeout=180)
        if result.returncode:
            raise RuntimeError(label + ' failed; see retained stderr.')

    try:
        objects = [str(stage/'obj'/name) for name in build['object_sha256']
                   if name not in {Path(unit).stem+'.o' for unit in units}]
        for name, source in texts.items():
            path, obj = out/'src'/name, out/'src'/Path(name).with_suffix('.o')
            path.write_text(source)
            report['instrumented_source_sha256'][name] = sha(path)
            extra=['-DTERRAIN_FALLBACK_OBSERVER=1'] if name=='observe.c' and terrain_observer else []
            run(build['compiler']+build['cppflags']+build['cflags']+extra+
                ['-c', str(path), '-o', str(obj)], name+'-compile')
            objects.append(str(obj))
        exe = out/'observer'
        run(build['compiler']+build['ldflags']+objects+build['libs']+
            ['-Wl,--wrap=SDL_RenderPresent', '-o', str(exe)], 'link')
        report['binary_sha256'] = sha(exe)
        spec = importlib.util.spec_from_file_location('launcher', ROOT/'scripts/launch_level2_family.py')
        launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher)
        for mode in ('on', 'off'):
            dest = out/mode
            profile = dest/'profile'
            cfg = profile/'config/opentyrian2000'
            cfg.mkdir(parents=True)
            # Terrain uses repository-relative paths. A read-only asset reference
            # allows native reports/saves to remain inside this isolated run.
            (dest/'assets').symlink_to(ROOT/'assets', target_is_directory=True)
            (cfg/'opentyrian.cfg').write_text(f'section video\nitem scaler {args.scale}x\nitem fullscreen -1\n')
            flags = ['--data', str(data), '--binary', str(exe), '--profile', str(profile),
                     '--hd', '--public-candidates']
            if args.terrain_fallback:
                flags.append('--terrain-fallback')
            if mode == 'on':
                flags.append('--static-hud')
            launch, runenv = launcher.build_plan(launcher.parser().parse_args(flags), env)
            runenv.update(SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', SDL_RENDER_DRIVER='software',
                          ORIGINAL_TEST_OUT=str(dest), ORIGINAL_TEST_TICKS=str(args.ticks))
            (dest/'plan.json').write_text(json.dumps(launch, indent=2)+'\n')
            run([str(exe), '--data='+str(data), '--no-sound', '--no-joystick', '--no-xmas'], mode, runenv, dest)
            print('Finished ' + mode, flush=True)
        report.update(compare(out, args.ticks, args.scale))
        if data_before != {p.name: sha(p) for p in data.iterdir() if p.is_file()}:
            raise AssertionError('Original data changed during the check.')
        report['status'] = 'PASS_BOUNDED_STATIC_HUD_SCENE'
        save()
        print(json.dumps({k: report[k] for k in ('status', 'scale', 'ticks', 'hud_visible_frames')}))
        return 0
    except Exception as error:
        report.update(status='FAILED', error=str(error))
        save()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
