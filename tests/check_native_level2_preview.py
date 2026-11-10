#!/usr/bin/env python3
"""Bounded native opt-in entry and SDL-event smoke test, not physical-input qualification.

Links unmodified, hash-verified native objects with test-only Present/menu wrappers.
Does not replace startup, RNG, gameplay, admission or player state. Test-only SDL
key events exercise move/fire/Esc/Quit. No event injection is in the shipped build.
Private original data, profiles and receipts stay outside the checkout.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--scale',type=int,choices=(2,4),default=2)
    parser.add_argument('--frames',type=int,choices=(240,540),default=540)
    args=parser.parse_args()
    data,out=args.data.resolve(),args.out.resolve()
    if not data.is_dir() or out.exists() or out==ROOT or ROOT in out.parents or out==data or data in out.parents or out in data.parents:
        raise ValueError('Require existing original data and a new separate output outside the checkout.')
    before={p.name:sha(p) for p in data.iterdir() if p.is_file()}
    plan=json.loads(subprocess.check_output([sys.executable,str(ROOT/'scripts/build_level2_family.py'),'--check-only'],text=True))
    stage=Path(plan['stage']);build=json.loads((stage/'BUILD.json').read_text())
    for field in ('source_sha256','asset_header_sha256','compiler','cppflags','cflags','ldflags','libs'):
        if plan[field]!=build[field]:raise ValueError('Rebuild current source with the current toolchain.')
    for field,subdir in (('source_sha256','src'),('asset_header_sha256','assets'),('object_sha256','obj')):
        for name,digest in build[field].items():
            if sha(stage/subdir/name)!=digest:raise ValueError('Changed staged input: '+name)
    if sha(stage/'opentyrian2000-family')!=build['binary_sha256']:raise ValueError('Changed staged executable.')
    out.mkdir(mode=0o700)
    observer=ROOT/'tests/fixtures/native_level2_preview_observer.c';obj=out/'observer.o';exe=out/'native-preview-check'
    report={'status':'RUNNING','scope':__doc__,'source_digest':build['source_digest'],'native_binary_sha256':build['binary_sha256'],
            'observer_sha256':sha(observer),'original_data_sha256':before,'scale':args.scale,'frames_requested':args.frames}
    receipt=out/'receipt.json'
    def save():receipt.write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        subprocess.run(build['compiler']+build['cppflags']+build['cflags']+['-c',str(observer),'-o',str(obj)],check=True,capture_output=True)
        subprocess.run(build['compiler']+build['ldflags']+[str(stage/'obj'/n) for n in build['object_sha256']]+[str(obj)]+build['libs']+
                       ['-Wl,--wrap=SDL_RenderPresent','-Wl,--wrap=JE_doInGameSetup','-o',str(exe)],check=True,capture_output=True)
        profile=out/'profile';cfg=profile/'config/opentyrian2000';cfg.mkdir(parents=True)
        (cfg/'opentyrian.cfg').write_text(f'section video\nitem scaler {args.scale}x\nitem fullscreen -1\n')
        (out/'assets').symlink_to(ROOT/'assets',target_is_directory=True)
        spec=importlib.util.spec_from_file_location('launcher',ROOT/'scripts/launch_level2_family.py')
        launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)
        flags=['--data',str(data),'--binary',str(exe),'--profile',str(profile),'--hd','--public-candidates',
               '--terrain-fallback','--player-fallback','--tank-fallback','--static-hud']
        launch,env=launcher.build_plan(launcher.parser().parse_args(flags),os.environ)
        env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software',NATIVE_PREVIEW_TEST_FRAMES=str(args.frames))
        command=[str(exe),'--level2-preview=asteroid2-v1','--data='+str(data),'--no-sound','--no-joystick','--no-xmas']
        report.update(argv=command,launch=launch,test_binary_sha256=sha(exe));save()
        with (out/'stdout.log').open('w') as stdout,(out/'stderr.log').open('w') as stderr:
            run=subprocess.run(command,cwd=out,env=env,stdout=stdout,stderr=stderr,timeout=600)
        if run.returncode:raise RuntimeError('Native preview test failed; inspect stderr.log.')
        with (out/'native-preview.csv').open() as f:rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader(f)]
        if not args.frames<=len(rows)<=args.frames+2:raise AssertionError('Unexpected gameplay frame count.')
        if 'NATIVE_PREVIEW_TEST_MENU_ABANDON_OK' not in (out/'stderr.log').read_text() or 'Native ASTEROID2 preview session ended.' not in (out/'stdout.log').read_text():
            raise AssertionError('Native Esc/Quit did not return through the single-session boundary.')
        if not(rows[60]['x']<rows[29]['x'] and rows[145]['x']>rows[89]['x'] and rows[170]['y']<rows[149]['y']):
            raise AssertionError('SDL arrow events did not move the native player.')
        if not any(r['shots'] for r in rows[12:]):raise AssertionError('SDL Space did not fire native shots.')
        if not(rows[0]['invulnerable']>0 and any(r['invulnerable']==0 for r in rows)):
            raise AssertionError('Native spawn invulnerability did not expire.')
        for field in ('family_presents','terrain_presents','player_presents','tank_presents'):
            if rows[-1][field]<=0:raise AssertionError('No actual display coverage for '+field)
        if any(r['hud_owned']<20000 or r['hud_mismatches'] or r['native_hud_mismatches'] for r in rows):
            raise AssertionError('Actual Present static/dynamic HUD verification failed.')
        if before!={p.name:sha(p) for p in data.iterdir() if p.is_file()}:raise AssertionError('Original data changed.')
        report.update(status='PASS_BOUNDED_NATIVE_ENTRY_SDL_EVENTS',frames=len(rows),physical_input_qualified=False,
                      single_session_abandon=True,source_units_modified_for_test=0,final=rows[-1])
        save();print(json.dumps(report['final'],indent=2))
    except Exception as error:
        report.update(status='FAILED',error=str(error));save()
        if isinstance(error,subprocess.CalledProcessError):print(error.stderr.decode(),file=sys.stderr)
        raise
if __name__=='__main__':main()
