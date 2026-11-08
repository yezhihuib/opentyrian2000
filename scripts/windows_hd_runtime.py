#!/usr/bin/env python3
"""Isolated public HD preparation. Check-only by default. No unattended launch."""
import argparse,json,sys
from pathlib import Path
# Read-only CLI checks must not create unmanifested bytecode in the run profile.
sys.dont_write_bytecode=True
import windows_classic_runtime as core
import launch_level2_family as family
HERE=Path(__file__).absolute().parent
PINS_SHA='e3d7f645b19f23fac79fa007a85fb1e4c124bb7f5676af97e38ca131a2a2a92a'
FAMILY_SHA='62afbe480f354c42c6531a5763b2cdcc5cfcedefc44ecbd1deea9ac508b0cfe0'
TOOLS=('windows_hd_runtime.py','windows_classic_runtime.py','launch_level2_family.py','HD-ASSET-PINS.json')
FAMILY_MANIFEST='assets/hd/level2-family-v1/MANIFEST.json'

def pins():
 _,raw=core.read_trusted(HERE/'HD-ASSET-PINS.json',PINS_SHA)
 entries=core.json_bytes(raw)['files']
 result={}
 for item in entries:
  name=item['path'];p=core.PurePosixPath(name)
  if not name.startswith('assets/hd/') or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name or name.casefold() in {x.casefold() for x in result}:raise ValueError('Unsafe/duplicate pinned asset')
  result[name]={'sha256':core.valid_digest(item['sha256']),'bytes':item['bytes']}
 if len(result)!=81 or sum(x['bytes'] for x in result.values())!=15485064:raise ValueError('Wrong public resource set')
 return result

def exact_files():return core.ALLOWED_FILES|{'tools/'+x for x in TOOLS}|set(pins())|{FAMILY_MANIFEST}

def family_plan(assets,binary,data,public):
 args=family.parser().parse_args(['--hd','--data',str(data),'--binary',str(binary),'--profile',str(assets/'unused-profile')]+(['--public-candidates'] if public else []))
 return family.build_plan(args,inherited={},root=assets)[0]

def controls(plan,source,destination):
 values={}
 for key,value in plan['environment_overrides'].items():
  if not family.controlled_name(key):continue
  if key.endswith('_ASSET_DIR') or key.startswith('BUILDING313_V6_PHASE'):
   value=str(destination/Path(value).relative_to(source))
  values[key]=value
 return values

def prepare(args):
 if not args.hd:raise ValueError('Explicit --hd is required; use classic launcher otherwise')
 original=argparse.Namespace(**vars(args));original.hd=False;original.public_candidates=False
 output,receipt,inputs,sources=core.prepare_plan(original)
 assets=core.safe_path(args.assets)
 if not assets.is_dir() or output==assets or assets in output.parents or output in assets.parents:raise ValueError('New runroot must be outside resource package')
 for name,item in pins().items():
  path,raw=core.read_trusted(assets/name,item['sha256'])
  if len(raw)!=item['bytes']:raise ValueError('Wrong resource length: '+name)
  inputs[name]=raw;sources[name]=path
 path,raw=core.read_trusted(assets/FAMILY_MANIFEST,FAMILY_SHA)
 inputs[FAMILY_MANIFEST]=raw;sources[FAMILY_MANIFEST]=path
 plan=family_plan(assets,Path(args.exe),Path(args.data),args.public_candidates)
 for name in TOOLS:
  path=core.safe_path(HERE/name);relative='tools/'+name
  inputs[relative]=path.read_bytes();sources[relative]=path
 receipt.update(mode='hd',public_candidates=bool(args.public_candidates),observer_required=True,
  environment=controls(plan,assets,output),menu_assets='Native UI fallback; 81 pinned public world assets',
  files={name:{'bytes':len(raw),'sha256':core.sha(raw)} for name,raw in sorted(inputs.items())},
  launcher_sha256=core.sha(inputs[core.SCRIPT]))
 if set(inputs)!=exact_files():raise ValueError('Internal exact manifest mismatch')
 return core.materialize(args,output,receipt,inputs,sources)

def verify(args):
 if not args.hd:raise ValueError('Explicit --hd is required at launch/check too')
 root,receipt,data=core.verify_run(args.root,args.trust_sha256,mode='hd',allowed_files=exact_files(),script_path=HERE/'windows_classic_runtime.py')
 if receipt.get('observer_required') is not True or type(receipt.get('public_candidates')) is not bool:raise ValueError('Invalid HD policy')
 if args.public_candidates!=receipt['public_candidates']:raise ValueError('Explicit public-candidates choice must match preparation')
 for name in TOOLS:
  if core.sha(core.safe_path(HERE/name).read_bytes())!=receipt['files']['tools/'+name]['sha256']:raise ValueError('Active tool identity changed: '+name)
 for name,item in pins().items():
  if receipt['files'][name]!=item:raise ValueError('Asset differs from public pins')
 if receipt['files'][FAMILY_MANIFEST]['sha256']!=FAMILY_SHA:raise ValueError('Family manifest differs from trusted metadata')
 plan=family_plan(root,root/'bin/opentyrian2000-level2.exe',data,args.public_candidates)
 expected=controls(plan,root,root)
 if expected!=receipt.get('environment'):raise ValueError('Changed family environment or relocated profile')
 return root,receipt,data,expected

def run(args):
 root,receipt,data,env=verify(args)
 if args.launch and not args.observer_present:raise ValueError('Launch requires a person present to observe; no unattended acceptance')
 result=core.run_verified(args,root,receipt,data,environment_overrides=env)
 result.update(hd_enabled=True,public_candidates=receipt['public_candidates'],environment_overrides=env,observer_required=True)
 return result

def parser():
 p=core.parser()
 # Keep the classic parser and its default no-write/no-launch modes.
 commands=next(x for x in p._actions if isinstance(x,argparse._SubParsersAction)).choices
 commands['prepare'].add_argument('--assets',required=True,help='Root of verified public resource package')
 q=commands['run'];q.add_argument('--hd',action='store_true');q.add_argument('--public-candidates',action='store_true');q.add_argument('--observer-present',action='store_true')
 return p

if __name__=='__main__':
 try:
  a=parser().parse_args();result=prepare(a) if a.command=='prepare' else run(a);print(json.dumps(result,indent=2))
  if result.get('status')=='START_OR_WAIT_FAILED' or result.get('exit_code',0):sys.exit(2)
 except (OSError,ValueError,KeyError,TypeError) as exc:print('windows-hd-runtime: '+str(exc),file=sys.stderr);sys.exit(2)
