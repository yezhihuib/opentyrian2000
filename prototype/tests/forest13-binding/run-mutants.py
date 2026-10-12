#!/usr/bin/env python3
"""Negative controls for the binding oracle; edits extracted copies only."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess

HERE = Path(__file__).resolve().parent
# Each mutation intentionally breaks one integration guarantee. Tests must reject
# every copy, making an accidentally vacuous recorder harness harder to pass.
MUTATIONS = [
    ('forest-slot-shift', 'return 336+i;', 'return 335+i;', 'suite'),
    ('forest-registry-loss-ignored', 'if(!found)forest_registry_ok=false;', 'if(!found)(void)0;', 'suite'),
    ('forest-map-reset-omitted', 'forest_registry_ok=true;render_mirror_reset_banking();', 'render_mirror_reset_banking();', 'suite'),
    ('forest-style-leak', 'if(forest_slot>=0&&style!=MIRROR_NORMAL)continue;', '/* deliberately omitted forest style guard */', 'suite'),
    ('declared-fixed-base-leak', 'if(forest_slot>=0&&forest13_declared()&&!forest)continue;', '/* deliberately omitted coupled fallback */', 'suite'),
    ('registry-readiness-bypassed', '&&forest_registry_ok&&style==MIRROR_NORMAL?forest13_record(id)', '&&style==MIRROR_NORMAL?forest13_record(id)', 'suite'),
    ('row-readiness-bypassed', 'a&&a->density==8&&material_row==1&&forest_registry_ok&&style==MIRROR_NORMAL?forest13_record(id)', 'a&&a->density==8&&forest_registry_ok&&style==MIRROR_NORMAL?forest13_record(id)', 'suite'),
    ('policy-detection-omitted', 'forest13_policy_check(game_probe_assets);', '/* deliberately omitted independent policy check */', 'lower-missing'),
    ('wrong-layer-forest-admitted', 'if(terrain_file==\'z\'&&((layer==1&&', 'if(terrain_file==\'z\'&&(((layer==1||layer==2)&&', 'suite'),
    ('circuit-slot-shift', 'return 349+i;', 'return 348+i;', 'suite'),
    ('circuit-191-admitted', 'ids[10]={181,182,184,185,192,193,194,195,201,202}', 'ids[10]={181,182,184,185,191,193,194,195,201,202}', 'suite'),
    ('circuit-style-leak', 'if((gray_slot>=0||purple_slot>=0||circuit_slot>=0||mechanical_slot>=0)&&style!=MIRROR_NORMAL)continue;', 'if((gray_slot>=0||purple_slot>=0||mechanical_slot>=0)&&style!=MIRROR_NORMAL)continue;', 'suite'),
    ('circuit-missing-art-trace-leak', '||circuit_slot>=0||mechanical_slot>=0||grass_slot>=0||forest_slot>=0)&&!a)continue;', '||grass_slot>=0||forest_slot>=0)&&!a)continue;', 'suite'),
    ('registry-old175-bound', 'terrain_source_count<193', 'terrain_source_count<175', 'suite'),
    ('registry-one-past-bound', 'terrain_source_count<193', 'terrain_source_count<=193', 'suite'),
    ('mechanical-slot-shift', 'return 359+i;', 'return 358+i;', 'suite'),
    ('mechanical-200-admitted', 'static int layer3_mechanical_slot(unsigned int id)\n{', 'static int layer3_mechanical_slot(unsigned int id)\n{\n if(id==200)return 362;', 'suite'),
    ('mechanical-left-slot-shift', 'return 359+i;', 'return 359+i+(i>=4);', 'suite'),
    ('mechanical-left-190-admitted', 'static int layer3_mechanical_slot(unsigned int id)\n{', 'static int layer3_mechanical_slot(unsigned int id)\n{\n if(id==190)return 363;', 'suite'),
    ('registry-previous189-bound', 'terrain_source_count<193', 'terrain_source_count<189', 'suite'),
    ('mechanical-style-leak', '||circuit_slot>=0||mechanical_slot>=0)&&style!=MIRROR_NORMAL', '||circuit_slot>=0)&&style!=MIRROR_NORMAL', 'suite'),
    ('mechanical-missing-art-trace-leak', '||mechanical_slot>=0||grass_slot>=0', '||grass_slot>=0', 'suite'),
    ('selected4-fallback-omitted', 'if(!a->valid&&game_probe_density==8)a->valid=read_asset(a,4);', '/* deliberately omitted selected4 fallback */', 'suite'),
    ('pointer-last-match-overwrite', 'id=terrain_sources[k].id;break;', 'id=terrain_sources[k].id;', 'suite'),

]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--run', type=Path, required=True, help='Successful run-oracle.py output')
    parser.add_argument('--out', type=Path, required=True, help='New directory for mutated extracted copies')
    args = parser.parse_args()
    candidate, run, out = args.candidate.resolve(), args.run.resolve(), args.out.resolve()
    if out.exists() or any(out == p or p in out.parents for p in (HERE, candidate, run)):
        parser.error('--out must be new and outside candidate, tests, and prior run')
    receipt = json.loads((run / 'result.json').read_text())
    assert receipt['status'] == 'passed'
    source_hash = hashlib.sha256((candidate / 'src' / 'render_mirror.c').read_bytes()).hexdigest()
    assert source_hash == receipt['source_sha256'], 'Candidate renderer changed after the successful oracle'
    for name, digest in receipt.get('test_package_sha256', {}).items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, 'Oracle test input changed: ' + name
    out.mkdir(parents=True)
    helpers = (run / 'production-helpers.inc').read_text()
    results = []
    for name, before, after, mode in MUTATIONS:
        assert helpers.count(before) == 1, (name, helpers.count(before))
        directory = out / name
        directory.mkdir()
        for copied in ('production-types.inc', 'production-loader.inc'):
            (directory / copied).write_bytes((run / copied).read_bytes())
        (directory / 'production-helpers.inc').write_text(helpers.replace(before, after))
        command = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                   '-Wno-misleading-indentation', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                   '-fno-pie', '-no-pie', '-I' + str(directory), '-I' + str(candidate / 'src'),
                   str(HERE / 'test-forest13-binding.c'), '-o', str(directory / 'oracle')]
        compiled = subprocess.run(command, capture_output=True, text=True, timeout=90)
        (directory / 'compile.log').write_text(compiled.stdout + compiled.stderr)
        compiled.check_returncode()
        environment = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                           UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        executed = subprocess.run([str(directory / 'oracle'), str(run / 'fixtures'), mode],
                                  capture_output=True, text=True, timeout=90, env=environment)
        (directory / 'run.log').write_text(executed.stdout + executed.stderr)
        assert executed.returncode != 0, 'Mutant unexpectedly passed: ' + name
        assert 'FAIL ' in executed.stderr or 'AddressSanitizer' in executed.stderr or 'runtime error:' in executed.stderr
        results.append(dict(name=name, rejected=True, compile_command=command, exit_code=executed.returncode,
                            diagnostic=executed.stderr.strip().splitlines()[0]))
        print(name + ': rejected', flush=True)
    assert hashlib.sha256((candidate / 'src' / 'render_mirror.c').read_bytes()).hexdigest() == source_hash, 'Candidate renderer changed during mutants'
    (out / 'result.json').write_text(json.dumps(dict(status='passed', source_sha256=source_hash,
                                                   oracle_receipt=str(run / 'result.json'),
                                                   test_package_sha256=receipt.get('test_package_sha256', {}),
                                                   mutation_runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                                   mutants=results,
                                                   scope='Only isolated extracted helper copies were mutated.'), indent=2)+'\n')
    print('Report: ' + str(out / 'result.json'))


if __name__ == '__main__':
    main()
