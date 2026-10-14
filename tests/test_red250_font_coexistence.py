#!/usr/bin/env python3
"""Source/art/proof composition and adversarial controls only; no game launch."""
from pathlib import Path
import argparse,copy,hashlib,json,subprocess
import red250_font_projection as co

def git(*args):return subprocess.check_output(['git','-C',str(co.ROOT),*args])
def reject(label,fn,controls):
 try:fn()
 except AssertionError:controls.append(label)
 else:raise AssertionError(('forbidden mutation accepted',label))
def equal(a,b):assert a==b

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path);args=p.parse_args()
 production=co.verify();controls=[]
 names=git('ls-tree','-r','--name-only',co.BASE,'src').decode().splitlines()
 actual={str(q.relative_to(co.ROOT)) for q in (co.ROOT/'src').rglob('*') if q.is_file() or q.is_symlink()}
 equal(actual,set(names));assert len(names)==148
 source_records={};font_names={n for n in co.PORTABLE['EDITS'] if n.startswith('src/')}
 for name in names:
  path=co.ROOT/name;assert path.is_file() and not path.is_symlink(),name
  raw=path.read_bytes();base=co.original(co.BASE,name)
  equal(co.outer(name,raw),co.original(co.FONT,name))
  equal(co.font_project(name,raw),co.red_original(name))
  equal(co.project(name,raw),base)
  reject(name+':unknown-source-byte',lambda:equal(co.project(name,raw+b'\n'),base),controls)
  source_records[name]=co.sha(raw)
 assert len(font_names)==9
 for top in ('src','assets'):
  expected=set(git('ls-tree','-r','--name-only',co.BASE,top).decode().splitlines()) | (co.RED_ASSETS if top=='assets' else set())
  actual={str(q.relative_to(co.ROOT)) for q in (co.ROOT/top).rglob('*') if q.is_file() or q.is_symlink()}
  equal(actual,expected)
  reject(top+':unlisted-path',lambda:equal(actual|{top+'/forbidden'},expected),controls)
  reject(top+':missing-path',lambda:equal(actual-{min(actual)},expected),controls)
 for group in (co.RED_EDITS,co.GUARDS):
  for name,pin in group.items():
   raw=(co.ROOT/name).read_bytes()
   for off in sorted({0,len(raw)//2,len(raw)-1}):
    bad=raw[:off]+bytes([raw[off]^1])+raw[off+1:]
    reject(name+':byte-'+str(off),lambda:co.qualify_current(name,bad),controls)
   for label,bad in [('append',raw+b'\n'),('truncate',raw[:-1]),('reversion',co.inverse(name,raw,pin,pin.get('parent',co.BASE)))]:
    reject(name+':'+label,lambda:co.qualify_current(name,bad),controls)
   if name in co.GUARDS and name in co.PORTABLE['EDITS']:
    intermediate=co.original(co.BASE,name)
    equal(co.project(name,intermediate),intermediate)
    reject(name+':normalized-parent-is-not-current',lambda:co.qualify_current(name,intermediate),controls)
   for index,hunk in enumerate(pin['hunks']):
    bad=copy.deepcopy(pin);bad['hunks'][index]['before']+=' '
    reject(name+':inverse-hunk-'+str(index),lambda:co.inverse(name,raw,bad,pin.get('parent',co.BASE)),controls)
 for name in sorted(co.RED_ASSETS):
  raw=(co.ROOT/name).read_bytes();bad=raw[:-1]+bytes([raw[-1]^1])
  reject(name+':asset-byte',lambda:co.qualify_asset(name,bad),controls)
  reject(name+':asset-truncation',lambda:co.qualify_asset(name,raw[:-1]),controls)
  reject(name+':asset-replaced-empty',lambda:co.qualify_asset(name,b''),controls)
 for name,digest in co.DATA['added_proof_files'].items():
  raw=(co.ROOT/name).read_bytes()
  reject(name+':proof-byte',lambda:equal(co.sha(raw+b'\n'),digest),controls)
 # The new proof layer cannot alter any frozen red receipt or existing art.
 red_added=co.RED_ADDED
 for name,pin in red_added.items():
  path=co.ROOT/name;assert path.is_file() and not path.is_symlink(),name
  raw=co.outer(name,path.read_bytes());equal(co.sha(raw),pin['sha256'])
  equal(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),pin['blob'])
  equal('100755' if path.stat().st_mode&0o111 else '100644',pin['mode'])
 for name in ('README.md','README.zh-CN.md'):equal((co.ROOT/name).read_bytes(),co.original(co.FONT,name))
 report=dict(result='PASS',font=co.FONT,red=co.RED,baseline=co.BASE,production_files=148,
  source_sha256=source_records,red_source_files=sorted(n for n in co.RED_EDITS if n.startswith('src/')),
  font_source_files=sorted(font_names),both_inverse_directions_byte_exact=True,
  red_existing_files=sorted(co.RED_EDITS),red_added_asset_paths=sorted(co.RED_ASSETS),
  red_added_receipts_and_art_preserved=len(red_added),proof_guard_files=sorted(co.GUARDS),
  immutable_portable_projection_and_pins=True,top_readmes_equal_font=True,
  required_git_ancestors=[co.BASE,co.FONT],unpublished_red_commit_is_provenance_only=True,
  negative_controls=controls,negative_control_count=len(controls),new_game_runs=0,
  accepted_runtime='Reused only: three simulations/four engine starts; 25 native2x and one native4x popup-only still; no new runtime or Windows claim.')
 if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
