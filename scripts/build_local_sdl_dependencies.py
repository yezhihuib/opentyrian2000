#!/usr/bin/env python3
"""Build pinned official SDL dependencies in a fresh user-owned directory."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess

SOURCES = (
    ('SDL', 'https://github.com/libsdl-org/SDL.git', 'release-2.32.4',
     '2359383fc187386204c3bb22de89655a494cd128'),
    ('SDL_net', 'https://github.com/libsdl-org/SDL_net.git', 'release-2.2.0',
     '669e75b84632e2c6cc5c65974ec9e28052cb7a4e'),
)


def plan(output, jobs):
    output = Path(output).expanduser().resolve()
    if not 1 <= jobs <= 16:
        raise ValueError('jobs must be between 1 and 16')
    prefix = output / 'prefix'
    return {'schema': 'opentyrian-local-sdl-build-v1', 'output': str(output),
            'prefix': str(prefix), 'jobs': jobs,
            'sources': [{'name': n, 'url': u, 'tag': t, 'commit': c}
                        for n, u, t, c in SOURCES],
            'pkg_config_path': str(prefix / 'lib/pkgconfig'),
            'runtime_library_path': str(prefix / 'lib'),
            'system_install': False, 'game_executed': False}


def build(spec):
    """Never reuse or replace an existing dependency output."""
    root = Path(spec['output'])
    root.mkdir(parents=True, exist_ok=False)
    receipt = dict(spec, status='building')
    receipt_path = root / 'BUILD.json'

    def record():
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')

    def run(argv, cwd, log):
        with (root / log).open('w') as stream:
            subprocess.run(argv, cwd=cwd, stdout=stream,
                           stderr=subprocess.STDOUT, check=True)

    record()
    try:
        for source in spec['sources']:
            name = source['name']
            checkout = root / name
            run(['git', 'clone', '--depth', '1', '--branch', source['tag'],
                 source['url'], str(checkout)], root, name + '-clone.log')
            actual = subprocess.check_output(
                ['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
            if actual != source['commit']:
                raise ValueError('Official tag moved; refusing unpinned source: ' + name)
            # Git checkout timestamps can make shipped Autotools outputs look stale.
            # Refresh metadata only; no source/configuration bytes are changed.
            if name == 'SDL_net':
                for generated in ('aclocal.m4', 'configure', 'Makefile.in'):
                    os.utime(checkout / generated, None)
            stage = root / (name + '-build')
            stage.mkdir()
            configure = [str(checkout / 'configure'), '--prefix=' + spec['prefix'],
                         '--disable-static']
            if name == 'SDL':
                configure.append('--disable-test')
            else:
                configure.append('--with-sdl-prefix=' + spec['prefix'])
            run(configure, stage, name + '-configure.log')
            run(['make', '-j' + str(spec['jobs'])], stage, name + '-make.log')
            run(['make', 'install'], stage, name + '-install.log')
        receipt['status'] = 'built'
    except Exception as error:
        receipt['status'] = 'failed'
        receipt['error'] = str(error)
        raise
    finally:
        record()
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='fresh directory outside the checkout')
    parser.add_argument('--jobs', type=int, default=2, choices=range(1, 17))
    parser.add_argument('--build', action='store_true', help='download and compile; default only prints plan')
    args = parser.parse_args(argv)
    spec = plan(args.output, args.jobs)
    repo = Path(__file__).resolve().parents[1]
    if Path(spec['output']).is_relative_to(repo):
        parser.error('Keep dependencies outside the repository checkout')
    if args.build:
        if os.name != 'posix':
            parser.error('This source dependency build requires POSIX configure/make tools')
        spec = build(spec)
    print(json.dumps(spec, indent=2))
    if args.build:
        print('For builds: export PKG_CONFIG_PATH=' + shlex.quote(spec['pkg_config_path']))
        print('For runtime: export LD_LIBRARY_PATH=' + shlex.quote(spec['runtime_library_path']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
