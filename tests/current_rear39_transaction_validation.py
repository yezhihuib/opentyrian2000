"""Portable real-data two-family authoring transactions and asset-only exports.
Requires the explicitly admitted Linux Node/Sharp profile. Creates a new
external output directory, no source checkout writes. Does not run the game.
"""
from pathlib import Path
import json,sys,hashlib,os,shutil,subprocess
from unittest.mock import patch
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root',type=Path,default=Path(__file__).resolve().parents[1])
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args()
ROOT=args.source_root.resolve();HERE=args.out.absolute()
if HERE.exists() or any(p.is_symlink() for p in (HERE,*HERE.parents)) or HERE.resolve().is_relative_to(ROOT):
    raise ValueError('Choose a new external output directory without symlink parents')
HERE.mkdir(parents=True)
sys.path.insert(0,str(ROOT/'scripts'))
import build_current_rear39 as b
import current_rear39_compatibility as c
import build_current_rear_p7 as p7b
import current_rear_p7_compatibility as p7
import build_current_craft267 as craft
from build_current_art import fnv
enc=lambda x:(json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
sha=lambda x:hashlib.sha256(x).hexdigest()
W=HERE/'full-pipeline-root';W.mkdir()
selected=json.loads((ROOT/c.SELECTION).read_bytes())
names=b.dependencies(ROOT,selected)
for manifest in (b.RUNTIME,'packaging/runtime-assets-public63a89b3.json'):
 names|={r['source_path'] for r in json.loads((ROOT/manifest).read_bytes())['files']}
for name in sorted(names):
 dest=W/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
print('copied',len(names),sum((W/n).stat().st_size for n in names),flush=True)
def snapshot():return {p.relative_to(W).as_posix():sha(p.read_bytes()) for p in W.rglob('*') if p.is_file()}
def write(name,raw):
 p=W/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
def payloads():return {r['destination']:sha((W/r['source_path']).read_bytes()) for r in json.loads((W/b.RUNTIME).read_bytes())['files']}
def edit(comp,old,new):
 req=json.loads((W/comp.SELECTION).read_bytes());field='source_json' if comp is c else 'source_svg';name=req['masters'][0][field]
 raw=(W/name).read_bytes();assert old in raw;raw=raw.replace(old,new);write(name,raw)
 req['masters'][0]['source_sha256']=sha(raw);req['schema']=comp.CANDIDATE_SCHEMA;req.pop('resources')
 request=HERE/(comp.INPUT_ROOT.split('/')[-1]+'-candidate.json');request.write_bytes(enc(req));return request
baseline=payloads();base_snapshot=snapshot()
request=edit(c,b'11 5.25',b'10.9 5.25')
# Fresh public loads must reject the uninstalled edited family.
for loader in (c.load,p7.load):
 try:loader(W)
 except ValueError:pass
 else:raise AssertionError('Uninstalled edit admitted')
stage=HERE/'stage39';plan=b.stage(W,request,stage);print('staged39',len(plan['files']),len(plan['inputs_sha256']),flush=True)
# Full derivation (not a mock), then actual replace failure and full rollback.
before=snapshot();real=craft.os.replace;calls=[]
def failing(source,destination):
 calls.append(str(destination))
 if len(calls)==2:raise OSError('injected actual second replacement')
 return real(source,destination)
with patch.object(craft.os,'replace',side_effect=failing):
 try:b.apply(W,stage)
 except OSError:pass
 else:raise AssertionError('Injection did not fail')
assert snapshot()==before;assert not list(W.rglob('*'+craft.SUFFIX));print('rollback exact',flush=True)
# Staged bytes tamper refusal on full derive, restoring before legitimate apply.
target=stage/'files'/c.MAPPING;original=target.read_bytes();target.write_bytes(original+b'bad')
try:b.apply(W,stage)
except ValueError:pass
else:raise AssertionError('Tampered stage admitted')
assert snapshot()==before;target.write_bytes(original)
b.apply(W,stage);check39=b.check(W);p7b.check(W)
after39=payloads();six={'assets/gameplay/'+c.name(*p) for p in c.PAIRS}
assert {n for n in baseline if baseline[n]!=after39[n]}==six|{'CURRENT-PRODUCTION-VALIDATION.json'}
print('applied39 and both checks; only six+binding changed',flush=True)
# Corrupt other family's HDA: candidate authority must fail closed.
other=p7.ROOT+'/'+p7.name(*p7.PAIRS[0]);saved=(W/other).read_bytes();write(other,saved+b'bad')
try:b.derive(W,request.read_bytes())
except ValueError:pass
else:raise AssertionError('Broken P7 HDA admitted')
write(other,saved)
# Opposite direction edit on top of legitimately changed39 retains six pins.
request7=edit(p7,b'#fffaa1',b'#a1faff');stage7=HERE/'stage-p7';plan7=p7b.stage(W,request7,stage7)
p7b.apply(W,stage7);check7=p7b.check(W);b.check(W)
after7=payloads();four={'assets/gameplay/'+p7.name(*p) for p in p7.PAIRS}
assert {n for n in after39 if after39[n]!=after7[n]}==four|{'CURRENT-PRODUCTION-VALIDATION.json'}
assert {n for n in baseline if baseline[n]!=after7[n]}==six|four|{'CURRENT-PRODUCTION-VALIDATION.json'}
print('applied reciprocal P7; ten total+binding only',flush=True)
# Earlier stage is stale after independent P7 authoring and must not roll it back.
unchanged=snapshot()
try:b.apply(W,stage)
except ValueError:pass
else:raise AssertionError('Stale pre-P7 stage admitted')
assert snapshot()==unchanged
other39=c.ROOT+'/'+c.name(*c.PAIRS[0]);saved39=(W/other39).read_bytes();write(other39,saved39+b'bad')
try:p7b.derive(W,request7.read_bytes())
except ValueError:pass
else:raise AssertionError('Broken Rear39 HDA admitted')
write(other39,saved39)

for platform in ('linux','windows'):
 cmd=[sys.executable,str(W/'scripts/package_runtime.py'),'--source-root',str(W),'--platform',platform,'--build','--output',str(HERE/('export-'+platform)),'--report',str(HERE/('export-'+platform+'.json'))]
 result=subprocess.run(cmd,capture_output=True,text=True);(HERE/('export-'+platform+'.log')).write_text(result.stdout+result.stderr)
 if result.returncode:raise RuntimeError('Export failed '+platform+result.stderr)
 print('export',platform,'PASS',flush=True)
a={p.relative_to(HERE/'export-linux').as_posix():sha(p.read_bytes()) for p in (HERE/'export-linux').rglob('*') if p.is_file()}
z={p.relative_to(HERE/'export-windows').as_posix():sha(p.read_bytes()) for p in (HERE/'export-windows').rglob('*') if p.is_file()}
manifest_destinations={r['destination'] for r in json.loads((W/b.RUNTIME).read_bytes())['files']}
assert len(manifest_destinations)==1029
assert all(a[n]==z[n] for n in manifest_destinations)
assert {n for n in a.keys()&z.keys() if a[n]!=z[n]}=={'RUNTIME-STATUS.json'}
assert a.keys()==z.keys()
left=json.loads((HERE/'export-linux/RUNTIME-STATUS.json').read_bytes())
right=json.loads((HERE/'export-windows/RUNTIME-STATUS.json').read_bytes())
assert left.pop('platform')=='linux';assert right.pop('platform')=='windows'
assert left==right
receipt=dict(status='PASS',dependencies=len(names),plan39_files=len(plan['files']),plan39_inputs=len(plan['inputs_sha256']),plan7_files=len(plan7['files']),plan7_inputs=len(plan7['inputs_sha256']),check39=check39,check7=check7,rollback='actual second os.replace; full snapshot identical',stage_tamper='refused without mutations',broken_other_family='P7 and Rear39 HDA corruption refused',stale_stage='earlier39 stage after P7 edit refused without writes',single39_changed=sorted(six),dual_family_changed=sorted(six|four),exports_equal=True,export_files=len(manifest_destinations),export_metadata_difference='RUNTIME-STATUS.json platform label only',baseline_source_sha256=base_snapshot,final_snapshot=snapshot())
(HERE/'full-pipeline-receipt.json').write_bytes(enc(receipt));print('ALL PASS',flush=True)
