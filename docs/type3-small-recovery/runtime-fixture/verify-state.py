#!/usr/bin/env python3
"""Regenerated source-backed state/lifecycle oracle; reads actual evidence only."""
from pathlib import Path
import csv,gzip,json,hashlib,collections
R=Path(__file__).resolve().parent;A=R/'candidate-census';B=R/'baseline-census';P=json.loads((R/'provenance.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rows(d,n):
 with gzip.open(d/(n+'.tsv.gz'),'rt')as f:return list(csv.DictReader(f,delimiter='\t'))
def ints(r):return {k:v if k in('phase','kind')else int(v)for k,v in r.items()}
for d in(A,B):
 s=json.loads((d/'run-summary.json').read_text());assert s['integrity_passed']and s['native_captures']==32 and s['logic_ticks']==[0,6531]
 rec=json.loads((d/'stream-receipts.json').read_text())
 for n,x in rec.items():
  assert sha(d/(n+'.tsv.gz'))==x['gzip_sha256']
  if x['retention']=='all':assert hashlib.sha256(gzip.decompress((d/(n+'.tsv.gz')).read_bytes())).hexdigest()==x['raw_sha256']
for n in('state','collisions','late-census','asset-debug-clock','type3-pulse-guards','type3-pulse-shots','type3-original-effects','type3-explosion-census','player-shot-requests','player-shot-emissions','player-shot-results'):
 assert rows(A,n)==rows(B,n),n
state=rows(A,'state');assert [int(r['tick'])for r in state]==list(range(6532));assert {(r['x'],r['y'])for r in state}=={('100','160')};assert len(rows(A,'fire-events'))==0
census=[ints(r)for r in rows(A,'late-census')];assert len(census)==38400
phases=['post-events','pre-ground-50','post-ground-50','pre-ground-100','post-ground-100','pre-sky-25','post-sky-25','pre-projectiles','post-projectiles','pre-body-collision','post-body-collision','end-tick']
by={(r['tick'],r['phase'],r['slot']):r for r in census};assert len(by)==38400
for tick in P['census_ticks']:
 assert [(r['phase'],r['slot'])for r in census if r['tick']==tick]==[(p,i)for p in phases for i in range(100)]
 assert all(r['difficulty']==2 for r in census if r['tick']==tick)
ids=[171,171,190,190,209,209,228,228,247,247,266,266];xs=[143,146,149,152,154,155,156,157,157,157,157,157];ys=[40,44,48,52,57,62,67,72,77,82,87,92]
materials=rows(A,'asset-debug-materials');cycle=[]
for k,tick in enumerate(range(6181,6193)):
 p=by[tick,'pre-sky-25',0];q=by[tick,'post-sky-25',0]
 assert (p['type'],p['bank'],p['avail'],p['armor'])==(3,1,0,2)
 assert (q['base'],q['cycle'])==(ids[k],k+1)
 draw=[r for r in materials if int(r['tick'])==tick and r['category']=='enemy'and int(r['id'])==ids[k]and int(r['x'])==xs[k]and int(r['y'])==ys[k]];assert len(draw)==1
 cycle.append({'tick':tick,'id':ids[k],'x':xs[k],'y':ys[k],'cycle':q['cycle']})
guards=[ints(r)for r in rows(A,'type3-pulse-guards')];assert [r['tick']for r in guards]==[6513,6515,6517]
for n,g in enumerate(guards):
 tick=g['tick'];assert (g['target'],g['type'],g['bank'],g['base'],g['cycle'],g['armor'],g['iced'],g['filter'],g['shot_x'],g['shot_y'],g['unique_candidates'],g['alias255'])==(0,3,1,[190,209,228][n],3+2*n,[2,1,1][n],[0,0,38][n],[0,0,9][n],152+2*n,110+12*n,0,0)
 before=by[tick,'pre-projectiles',0];after=by[tick,'post-projectiles',0]
 assert (after['armor'],after['iced'],after['filter'],after['avail'])==([1,1,1][n],[0,40,38][n],208,[0,0,1][n])
 assert after['cash0']-before['cash0']==(5 if n==2 else 0)and after['killed']-before['killed']==(1 if n==2 else 0)
 for i in range(1,100):
  a=by[tick,'pre-projectiles',i];b=by[tick,'post-projectiles',i];assert {k:v for k,v in a.items()if k not in('phase','cash0','cash1','killed')}=={k:v for k,v in b.items()if k not in('phase','cash0','cash1','killed')},(tick,i)
shots=[ints(r)for r in rows(A,'type3-pulse-shots')];assert [s['damage']for s in shots]==[1,99,1]
for s in shots:assert (s['shot'],s['xm'],s['ym'],s['xc'],s['yc'],s['frame'],s['ani'],s['animax'],s['filter'],s['trail'],s['ttl'],s['player'],s['chain'],s['aim'],s['complicated'])==(0,0,0,0,0,59,0,1,208,255,255,1,0,0,0)
effects=[ints(r)for r in rows(A,'type3-original-effects')];assert effects==[{'tick':6513,'slot':0,'enemytype':3,'effect_type':0,'x':152,'y':110},{'tick':6515,'slot':0,'enemytype':3,'effect_type':0,'x':154,'y':122},{'tick':6517,'slot':0,'enemytype':3,'effect_type':1,'x':156,'y':140}]
pool=[ints(r)for r in rows(A,'type3-explosion-census')];poolby={(r['tick'],r['slot']):r for r in pool}
for slot,start,finish,sprite,ttl,y in [(0,6513,6519,145,6,114),(1,6515,6521,145,6,126),(2,6517,6527,121,11,144)]:
 for t in range(start,finish+1):
  e=poolby[t,slot];k=t-start;assert (e['sprite'],e['ttl'],e['y'])==(sprite+k,ttl-k,y+4*k),(t,e)
assert (poolby[6528,2]['sprite'],poolby[6528,2]['ttl'],poolby[6528,2]['y'])==(132,0,188)
assert all(by[t,p,0]['avail']==1 for t in range(6518,6532)for p in phases)
assert all(not r['ttl']for r in pool if r['tick']>=6528)
assert not [r for r in materials if int(r['tick'])>=6527 and r['category']=='effect']
report={'status':'PASS_FRESH_PAIRED_ORIGINAL_STATE_AND_LIFECYCLE','baseline':P['baseline'],'candidate':P['candidate'],'state_rows_exact':len(state),'census_rows_exact':len(census),'phases':phases,'cycle':cycle,'pulse_guards':guards,'post_override_shots':shots,'original_effect_calls':effects,'first_absent_target_tick':6518,'last_visible_effect_tick':6526,'first_target_effect_clear_presentation_tick':6527,'first_empty_effect_pool_tick':6528,'clear_wording':'6527 has no target/effect presentation, while the final effect slot still has ttl1 at y184; 6528 culls the slot at y188. Sibling type3 actors remain. Pixel-level historical footprint restoration is independently checked.','qualification':'Private survival; no ram/body-hit coverage. Three artificial original projectiles. No actual type16, later boss53, whole-level, Windows or hardware GPU coverage.','provenance_sha256':sha(R/'provenance.json'),'verifier_sha256':sha(Path(__file__)),'capture_hashes':{d.name:sha(d/'frame-hashes.json')for d in(A,B)}}
(R/'state-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in('cycle','pulse_guards','post_override_shots')},indent=2))
