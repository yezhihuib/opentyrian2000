#!/usr/bin/env python3
"""Generate synthetic MP3 fixtures and run finite, offline ASan/UBSan tests.
Requires existing ffmpeg (libmp3lame), C compiler, SDL2 development files.
Does not initialize audio or launch the game. No real song is stored in Git.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shlex
import subprocess
import tempfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--work', type=Path)
p.add_argument('--no-sanitize', action='store_true')
p.add_argument('--leak-check', action='store_true', help='Enable LSan only on a host supporting its process/thread scan')
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
work = a.work or Path(tempfile.mkdtemp(prefix='external-music-tests-'))
work.mkdir(parents=True, exist_ok=True)
fixtures = work / '音乐 tracks'
fixtures.mkdir(exist_ok=True)
def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)
for i, (rate, channels, vbr) in enumerate([(22050,1,False),(44100,1,True),(48000,1,False),
                                         (22050,2,True),(44100,2,False),(48000,2,True)], 1):
    run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i','sine=frequency=440:duration=0.75',
         '-ar',str(rate),'-ac',str(channels),'-c:a','libmp3lame',
         *(['-q:a','3'] if vbr else ['-b:a','96k']),'-y',str(fixtures / f'track{i:02}.mp3')])
run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i',
     'aevalsrc=0.2*sin(2*PI*440*t)|-0.2*sin(2*PI*440*t):s=44100:d=0.75',
     '-c:a','libmp3lame','-b:a','192k','-joint_stereo','0','-y',str(fixtures/'track07.mp3')])
# 08 missing, 09 empty, 10 noise, 11 incomplete frame, 12 impossible ID3,
# 13 over input cap, 14 huge Xing count, 15 mixed format, 16 over duration, 17 huge Xing bytes.
(fixtures/'track09.mp3').write_bytes(b'')
(fixtures/'track10.mp3').write_bytes(bytes(range(256))*4)
good = (fixtures/'track01.mp3').read_bytes()
(fixtures/'track11.mp3').write_bytes(good[:-50])
(fixtures/'track12.mp3').write_bytes(b'ID3\x04\x00\x00\x7f\x7f\x7f\x7f')
with (fixtures/'track13.mp3').open('wb') as f:
    f.truncate(32*1024*1024 + 1)
def without_id3(data):
    if data[:3] == b'ID3':
        size = sum(data[6+i] << (21-7*i) for i in range(4))
        return data[10+size:]
    return data
first = bytearray(without_id3(good))
xing = next((first.find(tag) for tag in (b'Xing',b'Info') if first.find(tag)>=0), None)
assert xing is not None
mutated = bytearray(first)
mutated[xing+4:xing+8] = b'\0\0\0\1'
mutated[xing+8:xing+12] = b'\xff'*4
(fixtures/'track14.mp3').write_bytes(mutated)
(fixtures/'track15.mp3').write_bytes(without_id3(good)+without_id3((fixtures/'track02.mp3').read_bytes()))
frame = b'\xff\xfb\x90\x00'+bytes(413)
(fixtures/'track16.mp3').write_bytes(frame*(44100*600//1152 + 1))
mutated = bytearray(first)
mutated[xing+4:xing+8] = b'\0\0\0\2'
mutated[xing+8:xing+12] = b'\xff'*4
(fixtures/'track17.mp3').write_bytes(mutated)
# Upper-duration preparation benchmark and inclusive input-cap boundary.
run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i',
     'sine=frequency=220:duration=599','-ar','44100','-ac','1',
     '-c:a','libmp3lame','-b:a','64k','-y',str(fixtures/'track18.mp3')])
with (fixtures/'track19.mp3').open('wb') as f:
    f.write(good)
    f.truncate(32*1024*1024)
# Matching and mismatched ID3v2.4 footer envelopes, and an older tag's reserved
# footer bit. The underlying audio remains our own synthetic tone.
header = b'ID3\x04\x00\x10\x00\x00\x00\x00'
footer = b'3DI' + header[3:]
(fixtures/'track20.mp3').write_bytes(header + footer + without_id3(good))
bad_footer = bytearray(footer)
bad_footer[4] = 1
(fixtures/'track21.mp3').write_bytes(header + bad_footer + without_id3(good))
(fixtures/'track22.mp3').write_bytes(b'ID3\x03\x00\x10\x00\x00\x00\x00' + without_id3(good))
flags = shlex.split(subprocess.check_output(['pkg-config','sdl2','--cflags','--libs'], text=True))
binary = work/'test-external-music'
cc = os.environ.get('CC', 'cc')
sanitize = [] if a.no_sanitize else ['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
run([cc,'-std=c99','-Wall','-Wextra','-Werror','-g','-O1',*sanitize,
     str(root/'prototype/test-external-music.c'),'-o',str(binary),*flags,'-lm'])
env = dict(os.environ, ASAN_OPTIONS=f'detect_leaks={int(a.leak_check)}:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
with (work/'decoder.log').open('w') as log:
    run([str(binary),str(fixtures)],env=env,stdout=log,stderr=log)
print((work/'decoder.log').read_text().splitlines()[-1])
report={'synthetic_only':True,'audio_device_opened':False,'sanitized':not a.no_sanitize,
        'leak_sanitizer':a.leak_check,'owned_allocation_balance_checked':True,
        'fixture_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in fixtures.glob('*.mp3')},
        'log':str(work/'decoder.log')}
(work/'decoder-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(work/'decoder-report.json')
