#!/usr/bin/env python3
"""Bounded original-data normal-tank fallback A/B on SDL software.

Uses the existing deterministic ASTEROID2 bootstrap and sampled original input.
No probe/debug mode, gameplay change or original-data write. Native state hashes,
actual Present ownership and pixels are compared. Candidate-pixel readback is an
integration check, not an independent artwork oracle. Menus, physical controls,
full-level behavior, Windows/GPU and performance remain unqualified.
"""
from pathlib import Path
import argparse
import csv
import importlib.util
import json
import os
import struct
import subprocess
import sys
import check_family_static_hud_scene as common

ROOT = common.ROOT
STATE_FIELDS = common.STATE_FIELDS
CAPTURE_TICKS = (1,20,40,90,99,100,101,130,140,143,180,239,293,320,400,462,500,539)
MASK_RECORD_BYTES = 16 + 64000


def read_rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def compare(out, ticks, scale):
    states = {mode: read_rows(out/mode/'state.csv') for mode in ('on','off')}
    frames = {mode: read_rows(out/mode/'tank-present.csv') for mode in ('on','off')}
    slots = {mode: read_rows(out/mode/'tank-slots.csv') for mode in ('on','off')}
    if any(len(rows) != ticks for rows in (*states.values(), *frames.values())) or any(len(rows) != ticks*25 for rows in slots.values()):
        raise AssertionError('Incomplete state, slot or actual Present sequence.')
    local_frames, local_draws, qualified = 0, 0, []
    masks = (out/'on/ownership.bin').read_bytes()
    if len(masks) != ticks*MASK_RECORD_BYTES:
        raise AssertionError('Incomplete ownership evidence.')
    for tick in range(ticks):
        for rows in (*states.values(), *frames.values()):
            if int(rows[tick]['tick']) != tick:
                raise AssertionError('Out-of-order tick.')
        on, off = states['on'][tick], states['off'][tick]
        for field in (*STATE_FIELDS, 'family_presents', 'terrain_presents', 'player_presents', 'presents'):
            if on[field] != off[field]:
                raise AssertionError(f'Native state or existing admission changed at {tick}: {field}')
        on, off = frames['on'][tick], frames['off'][tick]
        for field in ('family','terrain','player_legacy','player_local','legacy_mask','inside_pixels','outside_hash'):
            if on[field] != off[field]:
                raise AssertionError(f'Existing admission or pixels outside tank cells changed at {tick}: {field}')
        active = int(on['local_mask'])
        if int(off['local_mask']) or int(on['candidate_mismatches']):
            raise AssertionError('Invalid independent tank output.')
        if active:
            if not int(on['terrain']) or int(on['family']) or active & int(on['legacy_mask']) or not int(on['local_cells']):
                raise AssertionError('Invalid independent tank admission.')
            if on['inside_hash'] == off['inside_hash']:
                raise AssertionError('No visible independent tank difference.')
            local_frames += 1
            local_draws += active.bit_count()
        elif on['inside_hash'] != off['inside_hash']:
            raise AssertionError('Unclaimed tank pixels changed.')
        start = tick*MASK_RECORD_BYTES
        index, bits, cells, size = struct.unpack_from('=IIII',masks,start)
        owners = masks[start+16:start+MASK_RECORD_BYTES]
        if index != tick or bits != active or size != 64000 or cells != int(on['local_cells']):
            raise AssertionError('Ownership header mismatch.')
        counted, actual_bits = 0, 0
        for pos, owner in enumerate(owners):
            if owner > 25:
                raise AssertionError('Invalid ownership value.')
            if owner:
                y,x = divmod(pos,320)
                if not (24 <= x < 288 and y < 184):
                    raise AssertionError('Ownership outside playfield crop.')
                row = slots['on'][tick*25+owner-1]
                if not (int(row['x']) <= x < int(row['x'])+24 and int(row['y']) <= y < int(row['y'])+28):
                    raise AssertionError('Ownership outside actual tank origin.')
                counted += 1
                actual_bits |= 1 << (owner-1)
        if counted != cells or actual_bits != bits or int(on['inside_pixels']) != cells*scale*scale:
            raise AssertionError('Ownership count or slot mismatch.')
        eligible_bits = 0
        for slot in range(25):
            a,b = slots['on'][tick*25+slot],slots['off'][tick*25+slot]
            if any(int(r['tick']) != tick or int(r['slot']) != slot+75 for r in (a,b)):
                raise AssertionError('Out-of-order slot evidence.')
            if a['legacy'] != b['legacy'] or int(b['local']) or bool(active & (1<<slot)) != bool(int(a['local'])):
                raise AssertionError('Slot admission mismatch.')
            if int(a['eligible']):
                if not int(a['token']) or not int(a['cells']) or int(a['denied']):
                    raise AssertionError('Invalid qualified lifetime.')
                eligible_bits |= 1<<slot
                qualified.append({'tick':tick,'slot':slot+75,'epoch':a['epoch'],'token':a['token'],'generation':a['generation'],
                                  'on':bool(int(a['legacy']) or int(a['local'])),'off':bool(int(b['legacy'])),'pose':int(a['pose'])})
            elif int(a['local']):
                raise AssertionError('Unqualified tank claimed display.')
        if eligible_bits != int(on['eligible_mask']):
            raise AssertionError('Eligible slot mask mismatch.')
    if not local_frames or int(states['on'][-1]['tank_presents']) != local_frames or int(states['off'][-1]['tank_presents']):
        raise AssertionError('Independent tank Present counter mismatch.')
    transitions = {'on':0,'off':0}
    previous = {}
    adjacent = 0
    for row in qualified:
        key = (row['slot'],row['epoch'],row['token'],row['generation'])
        old = previous.get(key)
        if old and old['tick']+1 == row['tick']:
            adjacent += 1
            for mode in transitions:
                transitions[mode] += old[mode] != row[mode]
        previous[key] = row
    captures = []
    expected = {f'frame-{tick:04d}.ppm' for tick in CAPTURE_TICKS if tick < ticks}
    from PIL import Image,ImageChops
    for mode in ('on','off'):
        if {p.name for p in (out/mode).glob('frame-*.ppm')} != expected:
            raise AssertionError('Missing or unexpected scheduled window capture.')
    for name in sorted(expected):
        tick = int(name[6:10]);start = tick*MASK_RECORD_BYTES
        owners = masks[start+16:start+MASK_RECORD_BYTES]
        with Image.open(out/'on'/name) as on,Image.open(out/'off'/name) as off:
            if on.size != (320*scale,200*scale) or off.size != on.size:
                raise AssertionError('Wrong window geometry.')
            diff = ImageChops.difference(on.convert('RGB'),off.convert('RGB'))
            bounds = diff.getbbox()
            for y in range(on.height):
                for x in range(on.width):
                    if diff.getpixel((x,y)) == (0,0,0):
                        continue
                    if not (x < 264*scale and y < 184*scale and owners[(y//scale)*320+x//scale+24]):
                        raise AssertionError('Captured pixel changed outside exact tank ownership.')
        captures.append({'tick':tick,'difference_bounds':bounds,'on_sha256':common.sha(out/'on'/name),'off_sha256':common.sha(out/'off'/name)})
    return {'native_state_comparisons':ticks*len(STATE_FIELDS),'independent_tank_frames':local_frames,
            'independent_tank_draws':local_draws,'qualified_tank_draws':len(qualified),'qualified_adjacent_pairs':adjacent,
            'qualified_tank_switches':transitions,'qualified_tank_native_draws':{mode:sum(not r[mode] for r in qualified) for mode in ('on','off')},
            'qualified_poses':sorted({r['pose'] for r in qualified}),
            'candidate_pixel_mismatches':0,'outside_owned_cell_hashes_equal':True,'captures':captures}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--scale', type=int, choices=(2,4), default=2)
    parser.add_argument('--ticks', type=int, choices=(240,540), default=540)
    parser.add_argument('--build-receipt', type=Path)
    args = parser.parse_args(argv)
    data, out = args.data.resolve(), args.out.resolve()
    common.validate_paths(data, out)
    before = {p.name:common.sha(p) for p in data.iterdir() if p.is_file()}
    env = dict(os.environ)
    if args.build_receipt:
        receipt = args.build_receipt.resolve()
        build = json.loads(receipt.read_text())
        stage = receipt.parent
        if stage != Path(build['stage']):
            raise ValueError('Build receipt moved from immutable stage.')
    else:
        plan = json.loads(subprocess.check_output([sys.executable,'scripts/build_level2_family.py','--check-only'],cwd=ROOT,env=env,text=True))
        stage = Path(plan['stage'])
        build = json.loads((stage/'BUILD.json').read_text())
        for key in ('source_sha256','asset_header_sha256','compiler','cppflags','cflags','ldflags','libs'):
            if build[key] != plan[key]:
                raise ValueError('Rebuild current source/toolchain before checking.')
    for field, folder in (('source_sha256','src'),('asset_header_sha256','assets'),('object_sha256','obj')):
        for name, digest in build[field].items():
            if common.sha(stage/folder/name) != digest:
                raise ValueError('Changed immutable stage input: '+name)
    out.mkdir(mode=0o700)
    (out/'src').mkdir()
    units = ('opentyr.c','mainint.c','tyrian2.c','game_probe.c')
    texts = common.instrument({name:(stage/'src'/name).read_text() for name in units})
    texts['observe.c'] = (ROOT/'tests/fixtures/tank_fallback_scene_observer.c').read_text()
    report = {'status':'RUNNING','scope':__doc__,'source_digest':build['source_digest'],
              'scale':args.scale,'ticks':args.ticks,'original_data_sha256':before,
              'build_receipt':str(stage/'BUILD.json'),'historical_snapshot':bool(args.build_receipt),
              'checker_sha256':common.sha(Path(__file__)),
              'observer_sha256':common.sha(ROOT/'tests/fixtures/tank_fallback_scene_observer.c'),
              'commands':[],'instrumented_source_sha256':{}}

    def save():
        (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')

    def run(command, label, environment=env, cwd=ROOT):
        report['commands'].append({'label':label,'argv':command,'cwd':str(cwd)})
        save()
        with (out/(label+'.stdout')).open('w') as stdout, (out/(label+'.stderr')).open('w') as stderr:
            result = subprocess.run(command,cwd=cwd,env=environment,stdout=stdout,stderr=stderr,timeout=240)
        if result.returncode:
            raise RuntimeError(label+' failed; retained stderr has details.')

    try:
        objects = [str(stage/'obj'/name) for name in build['object_sha256']
                   if name not in {Path(unit).stem+'.o' for unit in units}]
        for name, source in texts.items():
            path, obj = out/'src'/name, out/'src'/Path(name).with_suffix('.o')
            path.write_text(source)
            report['instrumented_source_sha256'][name] = common.sha(path)
            run(build['compiler']+build['cppflags']+build['cflags']+['-c',str(path),'-o',str(obj)],name+'-compile')
            objects.append(str(obj))
        exe = out/'observer'
        run(build['compiler']+build['ldflags']+objects+build['libs']+['-Wl,--wrap=SDL_RenderPresent','-o',str(exe)],'link')
        report['binary_sha256'] = common.sha(exe)
        spec = importlib.util.spec_from_file_location('launcher',ROOT/'scripts/launch_level2_family.py')
        launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher)
        for mode in ('on','off'):
            dest, profile = out/mode, out/mode/'profile'
            cfg = profile/'config/opentyrian2000'
            cfg.mkdir(parents=True)
            (dest/'assets').symlink_to(ROOT/'assets',target_is_directory=True)
            (cfg/'opentyrian.cfg').write_text(f'section video\nitem scaler {args.scale}x\nitem fullscreen -1\n')
            flags = ['--data',str(data),'--binary',str(exe),'--profile',str(profile),
                     '--hd','--public-candidates','--terrain-fallback','--static-hud','--player-fallback']
            if mode == 'on':
                flags.append('--tank-fallback')
            plan, runenv = launcher.build_plan(launcher.parser().parse_args(flags),env)
            runenv.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software',
                          ORIGINAL_TEST_OUT=str(dest),ORIGINAL_TEST_TICKS=str(args.ticks),
                          TANK_FALLBACK_REFERENCE_MASK=str(out/'on/ownership.bin'))
            (dest/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
            run([str(exe),'--data='+str(data),'--no-sound','--no-joystick','--no-xmas'],mode,runenv,dest)
            print('Finished '+mode,flush=True)
        report.update(compare(out,args.ticks,args.scale))
        if before != {p.name:common.sha(p) for p in data.iterdir() if p.is_file()}:
            raise AssertionError('Original data changed.')
        report['status'] = 'PASS_BOUNDED_TANK_FALLBACK_SCENE'
        save()
        print(json.dumps({key:report[key] for key in ('status','independent_tank_frames','independent_tank_draws','qualified_tank_switches')}))
        return 0
    except Exception as error:
        report.update(status='FAILED',error=str(error))
        save()
        raise


if __name__ == '__main__':
    raise SystemExit(main())
