#!/usr/bin/env python3
"""Private original music.mus + real LDS/OPL/decoder + SDL dummy integration.

Requires separately obtained Tyrian 2000 data, ffmpeg/libmp3lame and SDL2 dev files.
No original audio is exported. This is not physical-device listening, a game run,
Windows acceptance, or complete malformed-input certification.
"""
from pathlib import Path
import argparse
import importlib.util
import os
import shlex
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--data', type=Path, required=True)
parser.add_argument('--work', type=Path)
parser.add_argument('--baseline-ref', default='4383e1b75248e7ed0910e89f8c0db05dec8d4281',
                    help='Immutable pre-MP3 Git tree or an equivalent baseline revision')
parser.add_argument('--sanitize', action='store_true', help='Enable ASan; decoder/mixer UBSan checks are separate')
args = parser.parse_args()
assert (args.data / 'music.mus').is_file()
work = (args.work or Path(tempfile.mkdtemp(prefix='external-music-integration-'))).resolve()
work.mkdir(parents=True, exist_ok=True)
for name in ['empty', 'corrupt', '音乐 tracks']:
    (work / name).mkdir(exist_ok=True)
(work / 'corrupt/track18.mp3').write_bytes(b'This is not an MP3.')
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-f', 'lavfi', '-i',
                'sine=frequency=523.25:duration=0.75', '-ar', '48000', '-ac', '2',
                '-c:a', 'libmp3lame', '-q:a', '3', '-y', str(work / '音乐 tracks/track18.mp3')], check=True)
spec = importlib.util.spec_from_file_location('mixer_tests', ROOT / 'prototype/test-external-music-mixer.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
baseline = subprocess.check_output(['git', 'show', f'{args.baseline_ref}:src/loudness.c'], cwd=ROOT, text=True)
old_callback = module.function(baseline, 'audioCallback').replace('audioCallback(', 'originalAudioCallback(', 1)
(work / 'integration-generated-bodies.h').write_text(old_callback + '\n')
flags = shlex.split(subprocess.check_output(['pkg-config', 'sdl2', '--cflags', '--libs'], text=True))
sanitize = ['-fsanitize=address', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie'] if args.sanitize else []
command = shlex.split(os.environ.get('CC', 'cc')) + [
    '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
    '-ffunction-sections', '-fdata-sections', '-DTYRIAN_DIR=""',
    '-I', str(work), '-I', str(ROOT / 'src'), *sanitize,
    str(ROOT / 'prototype/test-external-music-integration.c'),
    str(ROOT / 'src/opl.c'), str(ROOT / 'src/file.c'), str(ROOT / 'src/external_music.c'),
    '-Wl,--gc-sections', '-o', str(work / 'integration'), *flags, '-lm']
subprocess.run(command, check=True)
env = dict(os.environ, SDL_AUDIODRIVER='dummy')
env.setdefault('ASAN_OPTIONS', 'detect_leaks=0:halt_on_error=1')
with (work / 'integration.log').open('w') as log:
    subprocess.run([str(work / 'integration'), str(args.data.resolve()), str(work / 'empty'),
                    str(work / 'corrupt'), str(work / '音乐 tracks')],
                   stdout=log, stderr=log, env=env, check=True, timeout=180)
for line in (work / 'integration.log').read_text().splitlines():
    if line.startswith('PASS'):
        print(line)
print(work / 'integration.log')
