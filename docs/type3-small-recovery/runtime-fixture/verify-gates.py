#!/usr/bin/env python3
"""Newly regenerated finite controls state/configuration/family identity checks."""
from pathlib import Path
import json,hashlib,gzip,csv,subprocess
R=Path(__file__).resolve().parent;P=json.loads((R/'gates-provenance.json').read_text());F=R/'fixture-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rows(d,n):
 with gzip.open(d/(n+'.tsv.gz'),'rt')as f:return list(csv.DictReader(f,delimiter='\t'))
def selected(d,n):return [r for r in rows(d,n)if int(r.get('tick',0))in (6181,6182,6183)]
ids={171,190,209,228,247,266};summaries={};pins={};names=['native4-baseline','native4-candidate','missing266','corrupt209','density4-baseline','density4-candidate']
for name in names:
 d=R/(name+'-census'+('-4x'if name.startswith('native4')else''));s=json.loads((d/'run-summary.json').read_text());assert s['integrity_passed']and s['status']=='PASS'and s['logic_ticks']==[0,6183];assert s['capture_ticks']==([6181]if name.startswith('density4')else[6181,6182,6183]);assert s['native_captures']==len(s['capture_ticks']);assert s['commit']==P['builds'][name]['commit'];summaries[name]=s
 inv=json.loads((d/'invocation.json').read_text());assert sha(d/'home/.config/opentyrian2000/opentyrian.cfg')==inv['config_sha256'];assert inv['private_environment']['SDL_VIDEODRIVER']=='dummy'and inv['private_environment']['SDL_RENDER_DRIVER']=='software'
 rec=json.loads((d/'stream-receipts.json').read_text())
 for n,h in rec.items():
  assert sha(d/(n+'.tsv.gz'))==h['gzip_sha256']
  if h['retention']=='all':assert hashlib.sha256(gzip.decompress((d/(n+'.tsv.gz')).read_bytes())).hexdigest()==h['raw_sha256']
 assert rec['fire-events']['lines']==1 and rec['player-shot-emissions']['lines']==1 and all(r['kind']=='enemy-shot' for r in rows(d,'collisions'))
 assert [int(r['tick'])for r in rows(d,'state')]==list(range(6184))
 assert {(r['x'],r['y'])for r in rows(d,'state')}=={('100','160')}
 for n in ('type3-original-effects','type3-pulse-guards','type3-pulse-shots'):assert rec[n]['lines']==0
 pins[name]={n:sha(d/n)for n in ('run-summary.json','frame-hashes.json','stream-receipts.json','invocation.json')}
# Full selected-pack equality except the approved single finite failure.
candidate=F/'packs/candidate';base=F/'packs/baseline';missing=F/'packs/missing266';corrupt=F/'packs/corrupt209'
files={p.name:p.read_bytes()for p in candidate.iterdir()};assert {p.name for p in base.iterdir()}==set(files)-{f'enemy-newsh2-{i}-8.hda'for i in ids}
for p in base.iterdir():assert p.read_bytes()==files[p.name]
assert {p.name for p in missing.iterdir()}==set(files)-{'enemy-newsh2-266-8.hda'}
for p in missing.iterdir():assert p.read_bytes()==files[p.name]
assert {p.name for p in corrupt.iterdir()}==set(files)
for p in corrupt.iterdir():
 a=p.read_bytes();b=files[p.name]
 if p.name=='enemy-newsh2-209-8.hda':assert len(a)==len(b)and [i for i,(x,y)in enumerate(zip(a,b))if x!=y]==[28]and a[28]==b[28]^1
 else:assert a==b
mainbase=R/'baseline-census';subset=lambda n:[r for r in rows(mainbase,n)if int(r['tick'])<=6183]
for name in ('missing266','corrupt209'):
 d=R/(name+'-census');assert rows(d,'state')==subset('state');assert rows(d,'collisions')==subset('collisions')
 for n in ('asset-debug-materials','draw-commands','scene-draw-commands','late-census'):assert selected(d,n)==selected(mainbase,n),(name,n)
 assert not [r for r in rows(d,'scene-draw-commands')if r['role']=='101'and int(r['index'])in ids]
for prefix in ('density4','native4'):
 suffix='-census'+('-4x'if prefix=='native4'else'');a=R/(prefix+'-candidate'+suffix);b=R/(prefix+'-baseline'+suffix)
 for n in ('state','collisions','late-census','asset-debug-materials','draw-commands'):assert rows(a,n)==rows(b,n),(prefix,n)
 if prefix=='density4':assert rows(a,'scene-draw-commands')==rows(b,'scene-draw-commands')and not[r for r in rows(a,'scene-draw-commands')if r['role']=='101'and int(r['index'])in ids]
fp=json.loads((F/'provenance.json').read_text())
for n,h in fp['files'].items():assert sha(F/n)==h,n
for n,h in fp['data_files'].items():assert sha(Path(fp['data_root'])/n)==h,n
assert not subprocess.check_output(['git','status','--porcelain'],cwd=P['source_root'])
report={'status':'PASS_FRESH_FINITE_4X_AND_FALLBACK_GATES','superseded_check':'An initial regenerated verifier incorrectly required no collision telemetry. Original enemy-shot contacts occur before the capture window under private survival; the corrected check requires only original enemy-shot records and exact paired/prefix equality. No extra game run or changed fixture.','candidate':P['candidate'],'baseline':P['baseline'],'exact_runs':names,'fresh_run_count':6,'native_captures':sum(s['native_captures']for s in summaries.values()),'true4_ticks':[6181,6182,6183],'missing266_ticks':[6181,6182,6183],'corrupt209_ticks':[6181,6182,6183],'density4_ticks':[6181],'all_stopped_after_tick':6183,'all_state_and_original_calls_unchanged':True,'missing_and_corrupt_zero_small_family_draws':True,'density4_zero_small_family_draws':True,'original_game_data_unchanged':True,'same_shared_private_source_and_objects':True,'pack_mutations_exact_and_finite':True,'all_native_capture_hashes_pinned':pins,'pixel_receipts':{n:sha(R/n)for n in('native4-pixel-verification.json','fallback-pixel-verification.json')},'verifier_sha256':sha(Path(__file__)),'limits':['Private survival; no ram, type16, boss launch or full-level claim','True4× three-frame spot, not full4× cycle/lifecycle','Missing/corrupt coverage only first three frames; density4 only first frame','Cache lifetime/malformed allocation variants are separate source/unit evidence','No actual runtime pack swapping, Windows or hardware GPU acceptance']}
(R/'gates-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
