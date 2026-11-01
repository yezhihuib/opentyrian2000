"""Prepare new mode-bound execution protocol; no test execution or source writes.

Input full protocol must itself be independently captured for the live restored
source/runtime. This builder never relabels an old profile as a current run.
"""
from pathlib import Path
import argparse,ast,hashlib,json,sys
import tiered_selection as t

def once(text,old,new):
 if text.count(old)!=1:raise ValueError('Unexpected template occurrence: '+old[:120])
 return text.replace(old,new)
def read_checked(directory,name,manifest):
 if Path(name).name!=name:raise ValueError('Nonlocal manifest member')
 p=directory/name
 if p.is_symlink() or not p.is_file() or t.file_sha(p)!=manifest['files'][name]:raise ValueError('Full protocol input mismatch '+name)
 return p.read_text()
def build(full_dir,approved_full_manifest,profile_path,approved_selection,observed_binding_path,out,mode):
 full_dir=Path(full_dir).resolve();out=Path(out).resolve()
 if out.exists():raise ValueError('Output must be new; preserve prior attempts')
 if t.file_sha(full_dir/'protocol-manifest.json')!=approved_full_manifest:raise ValueError('Full protocol approval mismatch')
 manifest=json.loads((full_dir/'protocol-manifest.json').read_bytes())
 full=json.loads(read_checked(full_dir,'plan.json',manifest));profile=json.loads(Path(profile_path).read_bytes())
 binding=json.loads(Path(observed_binding_path).read_bytes())
 selected=t.select(full,profile,approved_selection,binding,mode)
 controller=read_checked(full_dir,'segment_controller.py',manifest)
 worker=read_checked(full_dir,'segment_worker.py',manifest)
 protocol=read_checked(full_dir,'segment_protocol.py',manifest)
 phases=read_checked(full_dir,'phase_functions.py',manifest)
 # Entire original suite is still freshly collected for provenance, while only
 # the explicitly selected original slices are executed. No unittest skip calls.
 worker=once(worker,"provenance['ordered_test_ids']!=plan['ordered_test_ids']", "provenance['ordered_test_ids']!=plan['full_ordered_test_ids']")
 replacement=profile.get('phase_replacement') if mode=='batch' else None
 batch_phase=Path(__file__).with_name('batch_phase_functions.py')
 if replacement:
  if t.file_sha(batch_phase)!=replacement['code_sha256']:raise ValueError('Unapproved current-state phase code')
  worker=once(worker,"  import phase_functions\n  phase_functions.configure(PROFILE.root)\n  receipt['phase_result']=getattr(phase_functions,segment['call'])()", "  if segment.get('phase_implementation')=='current-state-once/v1':\n   import batch_phase_functions as selected_phases\n  else:\n   import phase_functions as selected_phases\n  selected_phases.configure(PROFILE.root)\n  receipt['phase_result']=getattr(selected_phases,segment['call'])()")
 # A result never masquerades as the old complete gate, including resume checks.
 if controller.count("'SEGMENTED_VALIDATION_PASS'")!=3:raise ValueError('Unexpected controller status template')
 controller=controller.replace("'SEGMENTED_VALIDATION_PASS'",'p.SUCCESS_STATUS')
 controller=once(controller,"scope='Segmented multi-process qualification; NOT original single-process gate; no01/02 phase imported'", "scope=plan['scope'], tier_selection=plan['tier_selection']")
 controller=once(controller,"single_process_gate=False,old01_02_imported=False)","single_process_gate=False,old01_02_imported=False,tier_selection=plan['tier_selection'])")
 status='SEGMENTED_BATCH_VALIDATION_PASS' if mode=='batch' else 'SEGMENTED_FULL_VALIDATION_PASS'
 protocol=once(protocol,"return m,json.loads((HERE/'plan.json').read_bytes())", "plan=json.loads((HERE/'plan.json').read_bytes())\n verify_tier_selection(m,plan)\n return m,plan")
 protocol=once(protocol,"PROFILE.verify_full(PROFILE.root);integration.verify_bundle(PROFILE.root,BUNDLE_SHA)", "PROFILE.verify_full(PROFILE.root);integration.verify_bundle(PROFILE.root,BUNDLE_SHA)\n verify_actual_selection_binding(PROFILE,git,m)")
 protocol=once(protocol,"if c['method_provenance']!=expected_methods:raise ValueError('Changed method source/code provenance')", "if c['method_provenance']!=expected_methods:raise ValueError('Changed method source/code provenance')\n verify_additional_methods(c,plan,segment)")
 protocol += '''
# Explicit tier selection is bound to this new protocol, not an old PASS.
import tiered_selection as tier
SUCCESS_STATUS = STATUS_PLACEHOLDER

def verify_tier_selection(manifest,plan):
 full=json.loads((HERE/'full-plan.json').read_bytes())
 profile=json.loads((HERE/'selection-profile.json').read_bytes())
 binding=manifest['selection_binding']
 expected=tier.select(full,profile,manifest['selection_profile_sha256'],binding,manifest['validation_mode'])
 if expected!=plan:raise ValueError('Selection plan/profile/mode mismatch')
 if plan['tier_selection']['coverage_statement']!=manifest['coverage_statement']:raise ValueError('Scope disclosure mismatch')
 if SUCCESS_STATUS!=('SEGMENTED_BATCH_VALIDATION_PASS' if manifest['validation_mode']=='batch' else 'SEGMENTED_FULL_VALIDATION_PASS'):raise ValueError('Mode result mismatch')

def verify_additional_methods(candidate,plan,segment):
 if segment.get('phase_implementation')!='current-state-once/v1':return
 expected=plan['tier_selection']['additional_methods']
 result=candidate['phase_result']['additional_static_shop_guards']
 ids=[row['id'] for row in expected]
 if result['started_test_ids']!=ids or result['successful_test_ids']!=ids or result['method_provenance']!=expected:raise ValueError('Additional static guard coverage/provenance mismatch')

def verify_actual_selection_binding(profile,git,manifest):
 binding=manifest['selection_binding']
 # These fields are actual current state, not the historical qualification.
 if profile.parent_head!=binding['commit']:raise ValueError('Selection HEAD mismatch')
 if git(profile.root,'rev-parse','HEAD^{tree}').decode().strip()!=binding['tree']:raise ValueError('Selection source tree mismatch')
 if git(profile.root,'diff','--cached','--name-only'):raise ValueError('Tiered profile requires an explicitly reviewed clean candidate checkout')
 if len(profile.data['worktree'])!=binding['source_entries']:raise ValueError('Selection source membership count mismatch')
 if sha(canonical(profile.data['worktree']))!=binding['worktree_map_sha256']:raise ValueError('Selection working map mismatch')
 # verify_full above checked the complete map and raw/semantic index freshly.
'''.replace('STATUS_PLACEHOLDER',repr(status))
 if binding.get('worktree_map_sha256') is None:raise ValueError('Live binding requires captured worktree_map_sha256')
 for raw in (controller,worker,protocol,phases):ast.parse(raw)
 out.mkdir(parents=True)
 files={name:read_checked(full_dir,name,manifest).encode() for name in manifest['files']}
 files.update({'segment_controller.py':controller.encode(),'segment_worker.py':worker.encode(),'segment_protocol.py':protocol.encode(),'phase_functions.py':phases.encode(),
 'tiered_selection.py':Path(t.__file__).read_bytes(),'full-plan.json':t.canonical(full),'plan.json':t.canonical(selected),'selection-profile.json':t.canonical(profile)})
 if replacement:files['batch_phase_functions.py']=batch_phase.read_bytes()
 for name,raw in files.items():(out/name).write_bytes(raw)
 new=dict(manifest)
 new['files']={name:hashlib.sha256(raw).hexdigest() for name,raw in files.items()}
 new.update(validation_mode=mode,selection_profile_sha256=approved_selection,selection_binding=binding,coverage_statement=selected['scope'],original_full_protocol_sha256=approved_full_manifest)
 (out/'protocol-manifest.json').write_bytes(t.canonical(new))
 record={'status':'PREPARED_NOT_EXECUTED','mode':mode,'original_full_protocol_sha256':approved_full_manifest,'new_protocol_sha256':t.file_sha(out/'protocol-manifest.json'),
  'selected_methods':len(selected['ordered_test_ids']),'additional_methods':selected['tier_selection']['additional_count'],'total_methods':selected['tier_selection']['total_executed_method_count'],'deferred_methods':selected['tier_selection']['deferred_count'],'segments':len(selected['segments']),
  'preserved':'Original phase functions bytes (executed only in full or conservative mode), test method bodies, object slices, provenance; original failure, disk, atomic prefix, tool/source freshness guards.',
  'changed':'Full suite collection comparison uses full_ordered_test_ids; explicit selection verification and current reviewed checkout binding added; result/scope/receipts mode-bound.',
  'full_fallback':'Never automatic; unknown profile returns FULL_REQUIRED_OR_REVIEWED_PROFILE.'}
 return record

def main():
 a=argparse.ArgumentParser();a.add_argument('--full-protocol',type=Path,required=True);a.add_argument('--approved-full-manifest',required=True)
 a.add_argument('--profile',type=Path,required=True);a.add_argument('--approved-selection',required=True);a.add_argument('--observed-binding',type=Path,required=True)
 a.add_argument('--out',type=Path,required=True);a.add_argument('--mode',choices=('batch','full'),default='batch');x=a.parse_args()
 print(json.dumps(build(x.full_protocol,x.approved_full_manifest,x.profile,x.approved_selection,x.observed_binding,x.out,x.mode),sort_keys=True))
if __name__=='__main__':main()
