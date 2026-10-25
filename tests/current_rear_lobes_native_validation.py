#!/usr/bin/env python3
"""Finite current Rear lobes + Rear281 + Rear1 + Rear39 + P7 real-payload native validation.
Linux/POSIX cc required. Run separately against bootstrap and independently staged
edited source roots. Uses production HDA/RGBA pins, synthetic bank/records, normal
draw observer and production shadow preparation only; no compositor pixel claim.
Historical scripts remain unchanged. Their missing unrelated observer hooks are
neutralized solely by the external include shim; no Rear observer is stubbed.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root',type=Path,default=HERE.parent)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--fixture',type=Path,help='Reuse actual fixture from a prior run with identical extracted source; verified hashes required')
parser.add_argument('--overlay',type=Path,help='Independently derived edited HDA directory')
parser.add_argument('--pin-header',type=Path,help='Independently derived combined production header')
parser.add_argument('--wrong-pins',choices=['lobes203','lobes43','rear281','rear1','rear39','p7'])
args=parser.parse_args();root=args.source_root.resolve();base=args.out.resolve()
if base.exists():raise SystemExit('Output must not already exist')
base.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
EXPECTED={'tests/run_rear_multi_p1_adapter_tests.py': '5afe01f572dd5c8eb3b3b3594a386d791ca327744d1e739dd376d5b791d1befb', 'tests/run_rear_multi_p11_shadow_tests.py': '7f1ce54f79b00f59836c9f14e1da504e358d541890c0b4fff363f83389fc5f27', 'tests/rear_multi_p1_adapter_test.c': '7525dd98e460fa3c0859a320a78be0eade88dd546e2617f41d319991d0afe1d9', 'tests/rear_multi_p11_shadow_test.c': '7be2f41c2c4869c250af6293bd2f7db3912f2d9c1dff8cccb3e3e3515c64cc72'}
for rel,wanted in EXPECTED.items():
 if sha(root/rel)!=wanted:raise SystemExit('Frozen harness changed; review adapter explicitly: '+rel)
cc=shutil.which('cc')
if not cc:raise SystemExit('POSIX C compiler cc required')
shim=HERE/'current_rear_p7_observer_shims.h'
# The old runner invokes cc from PATH. An external argv-safe Python wrapper adds
# only the finite missing observer shim, preserving every original test case.
bin_dir=base/'bin';bin_dir.mkdir();wrapper=bin_dir/'cc'
wrapper.write_text('#!'+sys.executable+'\nimport os,sys\nos.execv('+repr(cc)+', ['+repr(cc)+', "-Wno-unused-value", "-include", '+repr(str(shim))+']+sys.argv[1:])\n');wrapper.chmod(0o755)
env={**os.environ,'PATH':str(bin_dir)+os.pathsep+os.environ.get('PATH',''),'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1'}
def run(cmd,log):
 r=subprocess.run(list(map(str,cmd)),env=env,text=True,capture_output=True,timeout=1800)
 (base/log).write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(str(log)+' failed; see log')
out=base/'actual';out.mkdir()
if args.fixture:
 fixture=args.fixture.resolve()
 prior=json.loads((fixture.parent/'receipt.json').read_text())
 for rel,wanted in prior['fixture_source_sha256'].items():
  if sha(root/rel)!=wanted:raise SystemExit('Fixture source changed: '+rel)
 for name,wanted in prior['fixture_artifact_sha256'].items():
  if sha(fixture/name)!=wanted:raise SystemExit('Fixture artifact changed: '+name)
 synthetic_shadow=fixture
else:
 fixture=base/'synthetic';synthetic_shadow=base/'synthetic-shadow'
 run([sys.executable,root/'tests/run_rear_multi_p1_adapter_tests.py',fixture],'synthetic-adapter.log')
 run([sys.executable,root/'tests/run_rear_multi_p11_shadow_tests.py',fixture,synthetic_shadow],'synthetic-shadow.log')
for p in fixture.iterdir():
 if p.is_file() and (p.suffix=='.inc' or p.name in ('bank.bin','records.bin')):shutil.copy2(p,out/p.name)
(out/'fixture_pins.h').write_text((fixture/'fixture_pins.h').read_text().split('#ifdef REAR_P1_TEST_PENDING_ART')[0])
shutil.copy2(synthetic_shadow/'shadow_types.inc',out/'shadow_types.inc')
source_copy=base/'src';shutil.copytree(root/'src',source_copy)
if args.pin_header:shutil.copy2(args.pin_header,source_copy/'current_rear_multi_payload_pins.h')
full=out/'full';full.mkdir(exist_ok=True)
old=root/'assets/hd/packs/packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test'
for p in old.glob('rear-multicannon-p1-bank8-*.hda'):shutil.copy2(p,full/p.name)
for p in (root/'assets/hd/current-compat/rear-p7').glob('*.hda'):shutil.copy2(p,full/p.name)
for p in (root/'assets/hd/current-compat/rear39').glob('*.hda'):shutil.copy2(p,full/p.name)
for p in (root/'assets/hd/current-compat/rear1').glob('*.hda'):shutil.copy2(p,full/p.name)
for p in (root/'assets/hd/current-compat/rear281').glob('*.hda'):shutil.copy2(p,full/p.name)
for p in (root/'assets/hd/current-compat/rear-lobes').glob('*.hda'):shutil.copy2(p,full/p.name)
if args.overlay:
 for p in args.overlay.glob('*.hda'):shutil.copy2(p,full/p.name)
assert len(list(full.glob('*.hda')))==48
# Real HDA negative fixtures, not mismatched synthetic payloads.
for raw in (39,1,281,282,301,300,40,2,77,182,183,277,278,41,3,296,297,294,295,298,299,203,222,43,5):
 for d in (4,8):
  name=f'rear-multicannon-p1-bank8-{raw}-{d}.hda';src=full/name
  if not src.exists():continue
  for kind in ('missing','empty','magic','key','density','w','h','ax','ay','short','trunc','extra','payload','fifo','directory','device'):
   dest=out/f'{raw}-{d}-{kind}';dest.mkdir(exist_ok=True);f=dest/name;b=bytearray(src.read_bytes())
   if kind=='empty':b=bytearray()
   if kind=='magic':b[0]^=1
   if kind in ('key','density','w','h','ax','ay'):b[{'key':4,'density':8,'w':12,'h':16,'ax':20,'ay':24}[kind]]^=1
   if kind=='short':b=b[:27]
   if kind=='trunc':b=b[:-1]
   if kind=='extra':b+=b'!'
   if kind=='payload':b[-1]^=1
   if kind=='fifo':os.mkfifo(f)
   elif kind=='directory':f.mkdir()
   elif kind=='device':f.symlink_to('/dev/null')
   elif kind!='missing':f.write_bytes(b)

# Extra finite cache and file-byte checks share unchanged frozen test helpers.
shadow=(root/'tests/rear_multi_p11_shadow_test.c').read_text()
assert shadow.count('int main(int argc,char**argv)')==1
cache=base/'cache_test.c'
cache.write_text(shadow.replace('int main(int argc,char**argv)','int unused_shadow_main(int argc,char**argv)')+(HERE/'current_rear_lobes_cache_checks.c').read_text())
flags=['-std=c99','-Wall','-Wextra','-Werror','-pedantic','-O1','-g','-Wno-unused-value','-include',str(shim),'-I'+str(source_copy),'-I'+str(root/'tests'),'-I'+str(out)]
if args.wrong_pins:flags+=['-DEXPECT_WRONG_PINS','-DWRONG_'+args.wrong_pins.upper()]
for label,harness in ([('cache',cache)] if args.wrong_pins else [('shadow',root/'tests/rear_multi_p11_shadow_test.c'),('cache',cache)]):
 for mode in ('plain','sanitize'):
  exe=out/(label+'-'+mode);cmd=[cc,*flags,str(harness),str(source_copy/'rear_multi_p1.c'),'-lm','-o',str(exe)]
  if mode=='sanitize':cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
  run(cmd,label+'-'+mode+'-compile.log');run([exe,out],label+'-'+mode+'.log')
receipt={'schema':'current-rear-lobes-portable-native-v1','wrong_pins':args.wrong_pins,'fixture_source_sha256':{r:sha(root/r) for r in ['src/render_mirror.c','src/episodes.h','src/shots.h','src/shots.c','src/varz.c','src/entity_draw.c',*EXPECTED]},'fixture_artifact_sha256':{p.name:sha(p) for p in out.iterdir() if p.is_file() and (p.suffix=='.inc' or p.name in ('bank.bin','records.bin','fixture_pins.h'))},'runner_sha256':sha(Path(__file__)),'cache_helper_sha256':sha(HERE/'current_rear_lobes_cache_checks.c'),'source_root':str(root),'production_payload_pins':True,'real_loader':True,'synthetic_bank_and_records':True,'normal_draw_observer_only':True,'shadow_preparation_only':True,'no_compositor_pixels':True,'no_windows_gpu_campaign_claim':True,'missing_observer_shims_sha256':sha(shim),'historical_harness_sha256':EXPECTED,'current_pin_sha256':sha(source_copy/'current_rear_multi_payload_pins.h'),'real_hda_sha256':{p.name:sha(p) for p in full.glob('*.hda')},'log_sha256':{p.name:sha(p) for p in base.glob('*.log')}}
(base/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','receipt':str(base/'receipt.json')}))
