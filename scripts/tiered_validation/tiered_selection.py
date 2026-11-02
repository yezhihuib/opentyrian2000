"""Explicit reviewed batch selection. Never guesses impact or launches full fallback."""
from pathlib import Path
import argparse,copy,hashlib,json

class FullRequired(ValueError):
    pass

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n').encode()
def digest(value): return hashlib.sha256(canonical(value)).hexdigest()
def file_sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(value,reason):
    if not value: raise FullRequired('FULL_REQUIRED_OR_REVIEWED_PROFILE: '+reason)
def unique(values,label):
    require(isinstance(values,list) and all(isinstance(x,str) for x in values),label+' type')
    require(len(values)==len(set(values)),label+' duplicate')

def validate_full(full):
    ids=full['ordered_test_ids']; unique(ids,'full IDs')
    names=[s['name'] for s in full['segments']]; unique(names,'segments')
    flat=[]
    for i,s in enumerate(full['segments']):
        require(s['index']==i,'full segment index')
        require(s['kind'] in ('phase','module'),'unknown segment kind')
        if s['kind']=='phase': require(s['test_ids']==[] and 'slice' not in s,'phase tests')
        else:
            lo,hi=s['slice']
            require(type(lo) is int and type(hi) is int and 0<=lo<hi<=len(ids),'slice bounds')
            require(s['test_ids']==ids[lo:hi],'original slice mismatch')
            flat.extend(s['test_ids'])
    require(flat==ids,'full order/coverage')
    return ids

def validate_execution_plan(plan):
    """Pure structural preflight for public module/phase selected plans.

    This is not approval, a live source check, or the private daily runner's
    methods/current_composite schema. Empty plans retain their existing meaning.
    Unknown tier-selection versions fail closed; extra metadata is preserved.
    """
    require(isinstance(plan,dict),'execution plan type')
    tier=plan.get('tier_selection')
    require(isinstance(tier,dict) and tier.get('schema')=='tier-selection-result/v1','execution selection schema')
    require(tier.get('mode') in ('batch','full'),'execution selection mode')
    require(tier.get('automatic_full_run') is False and tier.get('historical_pass_reused') is False,'execution fallback/history policy')
    require(isinstance(plan.get('scope'),str) and bool(plan['scope']),'execution scope')
    full=plan.get('full_ordered_test_ids');selected=plan.get('ordered_test_ids');deferred=tier.get('deferred_test_ids')
    for values,label in ((full,'execution full IDs'),(selected,'execution selected IDs'),(deferred,'execution deferred IDs')):
        unique(values,label)
        require(all(values),'empty test ID')
    require(not(set(selected)&set(deferred)) and set(selected)|set(deferred)==set(full),'execution method partition')
    segments=plan.get('segments')
    require(isinstance(segments,list),'execution segments type')
    names=[];flat=[]
    for index,segment in enumerate(segments):
        require(isinstance(segment,dict),'execution segment type')
        require(type(segment.get('index')) is int and segment['index']==index,'execution segment index')
        name=segment.get('name');kind=segment.get('kind');ids=segment.get('test_ids')
        require(isinstance(name,str) and bool(name),'execution segment name')
        names.append(name);unique(ids,'execution segment IDs')
        require(kind in ('module','phase'),'execution segment kind missing/unknown')
        if kind=='phase':
            require(ids==[] and 'slice' not in segment,'execution phase tests')
            require(isinstance(segment.get('call'),str) and bool(segment['call']),'execution phase call')
        else:
            bounds=segment.get('slice')
            require(isinstance(bounds,list) and len(bounds)==2,'execution original slice shape')
            lo,hi=bounds
            require(type(lo) is int and type(hi) is int and 0<=lo<hi<=len(full),'execution original slice bounds')
            require(ids==full[lo:hi],'execution original slice reference')
            flat.extend(ids)
    unique(names,'execution segment names')
    require(flat==selected,'execution selected order/coverage')
    additional=tier.get('additional_methods')
    require(isinstance(additional,list) and all(isinstance(row,dict) for row in additional),'execution additional methods')
    extra=[row.get('id') for row in additional];unique(extra,'execution additional IDs')
    require(all(extra) and not(set(extra)&set(full)),'execution additional overlap')
    require(all(isinstance(row.get('method_source_sha256'),str) and len(row['method_source_sha256'])==64 and all(c in '0123456789abcdef' for c in row['method_source_sha256']) for row in additional),'execution additional source pin')
    counts={'selected_count':len(selected),'full_count':len(full),'deferred_count':len(deferred),'additional_count':len(extra),'total_executed_method_count':len(selected)+len(extra)}
    for key,value in counts.items():
        require(type(tier.get(key)) is int and tier[key]==value,'execution count: '+key)
    if tier['mode']=='full':
        require(selected==full and deferred==[] and additional==[],'execution full selection')
    return {'segments':len(segments),'selected_count':len(selected),'additional_count':len(extra),'deferred_count':len(deferred)}

def validate_profile(full,profile,approved_profile_sha,observed_binding):
    require(digest(profile)==approved_profile_sha,'reviewed profile approval mismatch')
    require(profile['schema'] in ('reviewed-batch-selection/v1','reviewed-batch-selection/v2'),'profile schema')
    require(profile['full_plan_digest']==digest(full),'full plan changed')
    require(profile['source_binding']==observed_binding,'source or baseline changed')
    require(profile['impact_review']['status']=='REVIEWED_EXPLICIT_SELECTION','impact review missing')
    require(bool(profile['impact_review']['justification']),'impact justification absent')
    require(profile['policy']['automatic_full_run'] is False,'automatic full fallback forbidden')
    require(profile['policy']['failure_fallback'] is False,'failure fallback forbidden')
    require(profile['policy']['unknown_binding']=='STOP_FULL_REQUIRED_OR_REVIEWED_PROFILE','unknown policy')
    validate_full(full)
    excluded=profile['deferred_segments']; unique(excluded,'deferred segments')
    required=profile['required_segments']; unique(required,'required segments')
    names={s['name'] for s in full['segments']}
    require(set(excluded)|set(required)==names and not(set(excluded)&set(required)),'segment partition')
    phases=[s['name'] for s in full['segments'] if s['kind']=='phase']
    if profile['schema']=='reviewed-batch-selection/v1':
        require('additional_methods' not in profile and 'phase_replacement' not in profile,'v1 must not claim unexecuted extras')
        require(all(n in required for n in phases),'common phase removed')
    else:
        replacement=profile['phase_replacement']
        require(replacement['original_phases']==phases,'phase replacement original IDs')
        require(all(n in excluded for n in phases),'replacement must explicitly defer original phases')
        require(replacement['implementation']=='current-state-once/v1','unknown replacement contract')
        require(replacement['name']=='current-state-once-v1' and replacement['call']=='current_state_once','replacement identity')
        require(isinstance(replacement['code_sha256'],str) and len(replacement['code_sha256'])==64,'replacement code pin')
        extra=profile['additional_methods']
        expected_extra=['test_shop_current_acceptance.ShopCurrentAcceptance.'+name for name in ('test_current_replay_masks_and_bounds','test_semantic_guard_mutations_rejected_without_hash_gate','test_current_compile_inventory')]
        require([row['id'] for row in extra]==expected_extra,'additional guard IDs')
        require(all(isinstance(row['method_source_sha256'],str) and len(row['method_source_sha256'])==64 for row in extra),'additional guard provenance')
        require(not(set(expected_extra)&set(full['ordered_test_ids'])),'additional guard overlap')
        require(bool(replacement['retained_guarantees']) and bool(replacement['lost_guarantees']) and bool(replacement['full_triggers']),'replacement disclosure missing')
    reasons=profile['deferral_reasons']
    require(set(reasons)==set(excluded),'deferral reasons incomplete')
    for name,row in reasons.items():
        require(bool(row['reason']) and bool(row['coverage_not_exercised']) and bool(row['full_triggers']),'missing risk disclosure: '+name)
    selected=[x for s in full['segments'] if s['name'] in required for x in s['test_ids']]
    deferred=[x for s in full['segments'] if s['name'] in excluded for x in s['test_ids']]
    unique(selected,'selected IDs');unique(deferred,'deferred IDs')
    require(not(set(selected)&set(deferred)) and set(selected)|set(deferred)==set(full['ordered_test_ids']),'method partition')
    require(selected==profile['selected_test_ids'] and deferred==profile['deferred_test_ids'],'explicit ID list mismatch')
    require(set(profile['new_test_ids']).issubset(selected),'new family test deferred')
    unique(profile['new_test_ids'],'new IDs')
    require(len(selected)==profile['expected_selected'] and len(deferred)==profile['expected_deferred'],'explicit counts mismatch')
    return selected,deferred

def select(full,profile,approved_profile_sha,observed_binding,mode='batch'):
    require(mode in ('batch','full'),'unknown mode')
    chosen,deferred=validate_profile(full,profile,approved_profile_sha,observed_binding)
    required=set(profile['required_segments']) if mode=='batch' else {s['name'] for s in full['segments']}
    plan=copy.deepcopy(full)
    plan['full_ordered_test_ids']=list(full['ordered_test_ids'])
    plan['segments']=[]
    if mode=='batch' and profile['schema']=='reviewed-batch-selection/v2':
        r=profile['phase_replacement']
        plan['segments'].append(dict(index=0,name=r['name'],kind='phase',call=r['call'],test_ids=[],phase_implementation=r['implementation'],phase_code_sha256=r['code_sha256'],replaces_original_phases=r['original_phases']))
    for segment in full['segments']:
        if segment['name'] in required:
            s=copy.deepcopy(segment);s['original_segment_index']=s['index'];s['index']=len(plan['segments']);plan['segments'].append(s)
    plan['ordered_test_ids']=chosen if mode=='batch' else list(full['ordered_test_ids'])
    plan['tier_selection']={'schema':'tier-selection-result/v1','mode':mode,'profile_sha256':approved_profile_sha,'full_plan_digest':digest(full),
        'selected_count':len(plan['ordered_test_ids']),'full_count':len(full['ordered_test_ids']),
        'deferred_count':len(deferred) if mode=='batch' else 0,'deferred_test_ids':deferred if mode=='batch' else [],
        'deferred_segments':profile['deferred_segments'] if mode=='batch' else [],
        'coverage_statement':'BATCH_SCOPE_ONLY_NOT_FULL_QUALIFICATION' if mode=='batch' else 'FULL_SCOPE_FRESH_EXECUTION_REQUIRED',
        'historical_pass_reused':False,'automatic_full_run':False}
    plan['tier_selection']['additional_methods']=copy.deepcopy(profile.get('additional_methods',[])) if mode=='batch' else []
    plan['tier_selection']['additional_count']=len(plan['tier_selection']['additional_methods'])
    plan['tier_selection']['total_executed_method_count']=len(plan['ordered_test_ids'])+plan['tier_selection']['additional_count']
    plan['tier_selection']['phase_replacement']=copy.deepcopy(profile.get('phase_replacement')) if mode=='batch' else None
    plan['scope']=plan['tier_selection']['coverage_statement']
    # Preserve full-suite provenance and original slices; no method body is rewritten.
    require([i for s in plan['segments'] for i in s['test_ids']]==plan['ordered_test_ids'],'selected order')
    return plan

def main():
    a=argparse.ArgumentParser();a.add_argument('--full-plan',type=Path,required=True);a.add_argument('--profile',type=Path,required=True)
    a.add_argument('--approved-profile-sha',required=True);a.add_argument('--observed-binding',type=Path,required=True)
    a.add_argument('--mode',choices=('batch','full'),default='batch');a.add_argument('--out',type=Path,required=True);x=a.parse_args()
    result=select(json.loads(x.full_plan.read_bytes()),json.loads(x.profile.read_bytes()),x.approved_profile_sha,json.loads(x.observed_binding.read_bytes()),x.mode)
    with x.out.open('xb') as f: f.write(canonical(result))
    print(json.dumps(result['tier_selection'],sort_keys=True))
if __name__=='__main__': main()
