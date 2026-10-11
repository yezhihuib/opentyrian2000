"""Compile actual current renderer helpers against an independent bilinear oracle."""
from pathlib import Path
import argparse, os, shutil, subprocess, tempfile

# Test-only retention: keep synthetic inputs/executables instead of deleting them.
class RetainedDirectory:
    def __init__(self, *args, **kwargs):
        self.name = tempfile.mkdtemp(*args, **kwargs)
    def __enter__(self):
        return self.name
    def __exit__(self, *args):
        print('Retained synthetic work:', self.name)

repo = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--sanitize', action='store_true', help='enable compiler ASan/UBSan')
a = p.parse_args()
s = (repo / 'src/render_mirror.c').read_text()
start = s.index('typedef struct { Uint16 peak[16][14]; } GreenBackground;')
end = s.index('/* Rebuild from the head-free underlay', start)
with RetainedDirectory(prefix='green-background-test-') as directory:
 d = Path(directory)
 (d / 'green-background-under-test.inc').write_text(s[start:end])
 shutil.copy2(Path(__file__).with_suffix('.c'), d / 'test.c')
 exe = d / ('test.exe' if os.name == 'nt' else 'test')
 cmd = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g']
 if a.sanitize: cmd += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
 subprocess.run(cmd + [str(d / 'test.c'), '-lm', '-o', str(exe)], check=True)
 env = dict(os.environ)
 if a.sanitize: env.setdefault('ASAN_OPTIONS', 'detect_leaks=0')
 subprocess.run([str(exe)], check=True, env=env)
