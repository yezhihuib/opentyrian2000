#!/usr/bin/env python3
"""Launch a reviewed, frozen protocol. Daily is default; full is explicit.

No profile discovery, impact inference, auto-approval, fallback, or auto-resume.
The original controller performs live source/tool/index checks and owns receipts.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys

def checked_plan(protocol,approved,mode,campaign):
 protocol=Path(protocol).resolve();campaign=Path(campaign).absolute()
 raw=(protocol/'protocol-manifest.json').read_bytes()
 if hashlib.sha256(raw).hexdigest()!=approved:raise ValueError('FULL_REQUIRED_OR_REVIEWED_PROFILE: protocol approval mismatch')
 manifest=json.loads(raw)
 wanted='batch' if mode=='daily' else 'full' if mode=='full' else None
 if wanted is None or manifest.get('validation_mode')!=wanted:raise ValueError('FULL_REQUIRED_OR_REVIEWED_PROFILE: requested mode has no matching approved protocol')
 for name,digest in manifest['files'].items():
  p=protocol/name
  if Path(name).name!=name or p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('Protocol member mismatch: '+name)
 plan=json.loads((protocol/'plan.json').read_bytes())
 if plan['tier_selection']['mode']!=wanted or plan['tier_selection']['automatic_full_run'] is not False:raise ValueError('Mode/fallback mismatch')
 if campaign.exists() or campaign.resolve()!=campaign or campaign==protocol or not campaign.is_relative_to(protocol):raise ValueError('A new, canonical campaign directory below protocol is required; existing attempts are never overwritten or auto-resumed')
 return protocol,plan,campaign

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mode',choices=('daily','full'),default='daily');parser.add_argument('--protocol',type=Path,required=True);parser.add_argument('--approved-manifest-sha',required=True);parser.add_argument('--campaign',type=Path,required=True);args=parser.parse_args()
 try:protocol,plan,campaign=checked_plan(args.protocol,args.approved_manifest_sha,args.mode,args.campaign)
 except (ValueError,OSError,KeyError,TypeError) as error:
  print(json.dumps({'status':'FULL_REQUIRED_OR_REVIEWED_PROFILE','reason':str(error),'tests_started':False}),file=sys.stderr);return 2
 print(json.dumps({'mode':args.mode,'coverage':plan['scope'],'original_selected_methods':len(plan['ordered_test_ids']),'additional_methods':plan['tier_selection']['additional_count'],'deferred_methods':plan['tier_selection']['deferred_count'],'segments':len(plan['segments']),'historical_results_imported':False}),flush=True)
 command=[sys.executable,'-B',str(protocol/'segment_controller.py'),'--campaign',str(campaign),'--approved-manifest-sha',args.approved_manifest_sha,'--max-new-segments',str(len(plan['segments']))]
 return subprocess.run(command,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0'),check=False).returncode
if __name__=='__main__':raise SystemExit(main())
