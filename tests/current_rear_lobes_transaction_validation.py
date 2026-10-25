"""Finite real-data five-family transactions and asset-only exports; no game run.
Requires the admitted Linux Node/Sharp profile. Writes only a new external output.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
from unittest.mock import patch
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root',type=Path,default=Path(__file__).resolve().parents[1])
parser.add_argument('--out',type=Path,required=True)
a=parser.parse_args(); ROOT=a.source_root.resolve(); HERE=a.out.absolute()
if HERE.exists() or any(p.is_symlink() for p in (HERE,*HERE.parents)) or HERE.resolve().is_relative_to(ROOT):
    raise ValueError('Choose a new external output directory without symlink parents')
HERE.mkdir(parents=True);sys.path.insert(0,str(ROOT/'scripts'))
import build_current_rear_lobes as b
import current_rear_lobes_compatibility as c
import build_current_rear_p7 as p7b
import current_rear_p7_compatibility as p7
import build_current_rear39 as r39b
import current_rear39_compatibility as r39
import build_current_rear1 as r1b
import current_rear1_compatibility as r1
import build_current_rear281 as r281b
import current_rear281_compatibility as r281
import build_current_craft267 as craft
families=((c,b),(p7,p7b),(r39,r39b),(r1,r1b),(r281,r281b))
enc=lambda x:(json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
sha=lambda x:hashlib.sha256(x).hexdigest()
W=HERE/'full-pipeline-root';W.mkdir()
names=b.dependencies(ROOT,json.loads((ROOT/c.SELECTION).read_bytes()))
for manifest in (b.RUNTIME,'packaging/runtime-assets-public63a89b3.json'):
    names|={r['source_path'] for r in json.loads((ROOT/manifest).read_bytes())['files']}
for name in sorted(names):
    dest=W/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
print('copied',len(names),sum((W/n).stat().st_size for n in names),flush=True)
def snapshot():return {p.relative_to(W).as_posix():sha(p.read_bytes()) for p in W.rglob('*') if p.is_file()}
def payloads():return {r['destination']:sha((W/r['source_path']).read_bytes()) for r in json.loads((W/b.RUNTIME).read_bytes())['files']}
def edit(comp,old,new,index=0):
    req=json.loads((W/comp.SELECTION).read_bytes());field='source_svg' if comp is p7 else 'source_json'
    master=req['masters'][index];name=master[field];raw=(W/name).read_bytes();assert old in raw
    raw=raw.replace(old,new);(W/name).write_bytes(raw);master['source_sha256']=sha(raw)
    req['schema']=comp.CANDIDATE_SCHEMA;req.pop('resources')
    request=HERE/(comp.INPUT_ROOT.split('/')[-1]+'-'+str(index)+'-candidate.json');request.write_bytes(enc(req));return request
baseline=payloads();base_snapshot=snapshot();changed=set();receipts=[];stages=[];requests={}
steps=((c,b,b'C.63 4',b'C.66 4',0,{1310203,1310222}),
       (c,b,b'C3.66 1',b'C3.70 1',1,{1310043,1310005}),
       (p7,p7b,b'#fffaa1',b'#a1faff',0,set(p7.IDS)),
       (r39,r39b,b'11 5.25',b'10.9 5.25',0,set(r39.IDS)),
       (r1,r1b,b'C10.95 4',b'C10.85 4',0,set(r1.IDS)),
       (r281,r281b,b'11 6 C9.13',b'10.9 6 C9.13',0,set(r281.IDS)))
for step,(comp,builder,old,new,index,ids) in enumerate(steps):
    previous=payloads();request=edit(comp,old,new,index);requests[comp]=request
    for other,_ in families:
        try:other.load(W)
        except ValueError:pass
        else:raise AssertionError('Uninstalled source edit admitted by '+other.__name__)
    stage=HERE/('stage-'+str(step));plan=builder.stage(W,request,stage);before=snapshot()
    if step==0:
        real=craft.os.replace;calls=[]
        def failing(source,destination):
            calls.append(str(destination))
            if len(calls)==2:raise OSError('injected actual second replacement')
            return real(source,destination)
        with patch.object(craft.os,'replace',side_effect=failing):
            try:builder.apply(W,stage)
            except OSError:pass
            else:raise AssertionError('Injection did not fail')
        assert snapshot()==before and not list(W.rglob('*'+craft.SUFFIX))
        target=stage/'files'/comp.MAPPING;raw=target.read_bytes();target.write_bytes(raw+b'bad')
        try:builder.apply(W,stage)
        except ValueError:pass
        else:raise AssertionError('Tampered stage admitted')
        assert snapshot()==before;target.write_bytes(raw)
        print('actual rollback and staged tamper PASS',flush=True)
    builder.apply(W,stage)
    checks={other.__name__:otherbuilder.check(W) for other,otherbuilder in families}
    current=payloads();own={'assets/gameplay/'+comp.name(*pair) for pair in comp.PAIRS if pair[0] in ids}
    assert len(own)==(4 if step<3 else (6 if step==3 else (8 if step==4 else 20)))
    assert {n for n in previous if previous[n]!=current[n]}==own|{'CURRENT-PRODUCTION-VALIDATION.json'}
    changed|=own
    assert {n for n in baseline if baseline[n]!=current[n]}==changed|{'CURRENT-PRODUCTION-VALIDATION.json'}
    # Every older stage is stale after a new independently authored source revision.
    before=snapshot()
    for oldbuilder,oldstage in stages:
        try:oldbuilder.apply(W,oldstage)
        except ValueError:pass
        else:raise AssertionError('Stale stage admitted')
        assert snapshot()==before
    stages.append((builder,stage))
    receipts.append(dict(step=step,family=comp.__name__,master_index=index,changed=sorted(own),total_changed=len(changed),files=len(plan['files']),inputs=len(plan['inputs_sha256']),checks=checks))
    print('applied',step,'changed',len(own),'cumulative',len(changed),flush=True)
assert len(changed)==46
# All twenty directed cross-family corruption cases, with actual final candidate sources.
for broken,_ in families:
    target=W/broken.ROOT/broken.name(*broken.PAIRS[0]);saved=target.read_bytes();target.write_bytes(saved+b'bad')
    before=snapshot()
    for other,builder in families:
        if other is broken:continue
        try:builder.derive(W,requests[other].read_bytes())
        except ValueError:pass
        else:raise AssertionError('Broken other-family HDA admitted')
        assert snapshot()==before
    target.write_bytes(saved)
print('20 reciprocal corruptions rejected',flush=True)
for platform in ('linux','windows'):
    cmd=[sys.executable,str(W/'scripts/package_runtime.py'),'--source-root',str(W),'--platform',platform,'--build','--output',str(HERE/('export-'+platform)),'--report',str(HERE/('export-'+platform+'.json'))]
    result=subprocess.run(cmd,capture_output=True,text=True);(HERE/('export-'+platform+'.log')).write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('Export failed '+platform+result.stderr)
    print('export',platform,'PASS',flush=True)
exports=[]
for platform in ('linux','windows'):
    directory=HERE/('export-'+platform);exports.append({p.relative_to(directory).as_posix():sha(p.read_bytes()) for p in directory.rglob('*') if p.is_file()})
x,y=exports;destinations={r['destination'] for r in json.loads((W/b.RUNTIME).read_bytes())['files']}
assert len(destinations)==1029 and x.keys()==y.keys() and all(x[n]==y[n] for n in destinations)
assert {n for n in x if x[n]!=y[n]}=={'RUNTIME-STATUS.json'}
left=json.loads((HERE/'export-linux/RUNTIME-STATUS.json').read_bytes());right=json.loads((HERE/'export-windows/RUNTIME-STATUS.json').read_bytes())
assert left.pop('platform')=='linux' and right.pop('platform')=='windows' and left==right
receipt=dict(status='PASS',dependencies=len(names),steps=receipts,changed=sorted(changed),rollback='actual second os.replace; full snapshot identical',tamper='refused without mutation',stale_stages='all preceding stages refused after each later edit',cross_family_corruptions=20,export_files=1029,exports_equal=True,export_metadata_difference='RUNTIME-STATUS.json platform only',baseline_source_sha256=base_snapshot,final_snapshot=snapshot())
(HERE/'full-pipeline-receipt.json').write_bytes(enc(receipt));print('ALL PASS',flush=True)
