#!/usr/bin/env python3
"""Expand an explicit per-batch policy into a review draft, never infer impact.

An independently captured full plan and human-reviewed exact segment lists are
required. This command does not approve the draft, collect tests or run tests.
"""
from pathlib import Path
import argparse,copy,json
import tiered_selection as t

def prepare(full,policy,phase_path):
 t.validate_full(full);p=copy.deepcopy(policy)
 t.require(p['schema'] in ('reviewed-batch-selection/v1','reviewed-batch-selection/v2'),'schema')
 required=p['required_segments'];deferred=p['deferred_segments'];t.unique(required,'required');t.unique(deferred,'deferred')
 names={s['name'] for s in full['segments']};t.require(set(required)|set(deferred)==names and not(set(required)&set(deferred)),'explicit segment partition')
 p['full_plan_digest']=t.digest(full)
 p['selected_test_ids']=[i for s in full['segments'] if s['name'] in required for i in s['test_ids']]
 p['deferred_test_ids']=[i for s in full['segments'] if s['name'] in deferred for i in s['test_ids']]
 p['expected_selected']=len(p['selected_test_ids']);p['expected_deferred']=len(p['deferred_test_ids'])
 p['impact_review']['status']='DRAFT_REQUIRES_INDEPENDENT_REVIEW'
 if p['schema']=='reviewed-batch-selection/v2':
  p['phase_replacement']['original_phases']=[s['name'] for s in full['segments'] if s['kind']=='phase']
  p['phase_replacement']['code_sha256']=t.file_sha(phase_path)
 # Validate every other contract, without changing the emitted draft status.
 probe=copy.deepcopy(p);probe['impact_review']['status']='REVIEWED_EXPLICIT_SELECTION'
 t.select(full,probe,t.digest(probe),probe['source_binding'])
 return p

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--full-plan',type=Path,required=True);a.add_argument('--explicit-policy',type=Path,required=True);a.add_argument('--out',type=Path,required=True);x=a.parse_args()
 p=prepare(json.loads(x.full_plan.read_bytes()),json.loads(x.explicit_policy.read_bytes()),Path(__file__).with_name('batch_phase_functions.py'))
 with x.out.open('xb') as f:f.write(t.canonical(p))
 print(json.dumps({'status':'DRAFT_NOT_APPROVED_NOT_EXECUTED','draft_sha256':t.digest(p),'selected':p['expected_selected'],'deferred':p['expected_deferred']}))
if __name__=='__main__':main()
