#!/usr/bin/env python3
"""Independent current reader tests, no original data, no game/UI, no historical ref."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--no-leak-check', '--no-lsan',action='store_true',help='Disable unsupported LeakSanitizer only; retain ASan/UBSan');a=p.parse_args();repo=a.repo.resolve();out=a.out.resolve()
if out.exists() or repo==out or repo in out.parents:raise SystemExit('Use fresh external output')
source=Path(__file__).with_name('current_public_loader.c');tracked=['src/shared_asset_reader.h','src/shared_asset_fd_reader.inc','src/global_asset_registry.h','src/render_mirror.c']
h=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();before={name:h(repo/name) for name in tracked}
art=repo/'assets/hd/global-assets-v1';assets={f.relative_to(art).as_posix():h(f) for f in sorted((art/'content').glob('*.hda'))}
out.mkdir(parents=True);exe=out/'current-loader';cmd=['cc','-std=c99','-O1','-g','-Wall','-Wextra','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie','-I'+str(repo/'src'),str(source),'-o',str(exe)]
build=subprocess.run(cmd,text=True,capture_output=True);(out/'build.log').write_text(build.stdout+build.stderr);build.check_returncode()
run=subprocess.run([str(exe),str(art),str(out)],text=True,capture_output=True,timeout=120,env={**os.environ,'ASAN_OPTIONS':('detect_leaks=0' if a.no_leak_check else 'detect_leaks=1')+':halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
(out/'loader-cases.tsv').write_text(run.stdout);(out/'loader-stderr.log').write_text(run.stderr)
unchanged=all(h(repo/n)==v for n,v in before.items()) and all(h(art/n)==v for n,v in assets.items())
report={'status':'PASS' if run.returncode==0 and unchanged else 'FAIL','compile':cmd,'exit_code':run.returncode,'summary':run.stderr,'source_sha256':before,'asset_sha256':assets,'inputs_unchanged':unchanged,'leak_check_enabled':not a.no_leak_check,'harness_sha256':h(source),'scope':'Actual current stdio and fd readers on public global registry only; not all1163 inputs, source-identity admission, game simulation, Windows or GPU acceptance. Preview is decoded individual art over gray, NOT scene output.'}
(out/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('asset_sha256','source_sha256','compile')},indent=2));run.check_returncode();assert unchanged
