#!/usr/bin/env python3
"""Strict qualified-parent and native-production coexistence; no game launch."""
from pathlib import Path
import argparse,hashlib,json,runpy
import pregame_font_projection as pf
p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args()
pf.PORTABLE['verify']()
root=pf.ROOT;git=pf.git;sha=lambda b:hashlib.sha256(b).hexdigest()
assert git('rev-parse',pf.BASE+'^{tree}').decode().strip()=='cc1f5da9feeea8d12407bd7e5a079981ef711d13'
assert git('show','-s','--format=%P',pf.BASE).decode().strip()=='f3bcc061d8a136e257e9c36d40629b4f948a1708'
# The accepted C helper retains exact whole-source-map validation and every
# adversarial constant/order/comment/source-path control, now on native fonts.
c=runpy.run_path(str(root/'prototype/type15_source_projection.py'))
assert c['BASE']==pf.NATIVE
current,baseline,version=c['audit_sources'](root);assert version=='v2'
rejections=c['rejection_tests'](baseline)
# Current additions project back to every byte of the whole qualified C tree.
# No manifest, asset, tooling or source exception is based on a path pattern.
files={};changed=[];asset_bytes=0
for row in git('ls-tree','-rz',pf.BASE).split(b'\0'):
 if not row:continue
 meta,name=row.split(b'\t',1);name=name.decode();mode,kind,blob=meta.decode().split();q=root/name
 assert kind=='blob' and mode in ('100644','100755') and q.is_file() and not q.is_symlink(),name
 raw=pf.PORTABLE['project'](name,q.read_bytes());expected=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob
 if not expected:
  assert name in pf.EDITS,name;pf.project(name,raw);changed.append(name)
 if name.startswith('assets/'):asset_bytes+=len(raw)
 files[name]=blob
assert set(changed)==set(pf.EDITS)
# Reject added/unlisted asset/source paths as well as changed existing bytes.
for top in ['src','assets']:
 actual={str(q.relative_to(root))for q in (root/top).rglob('*')if q.is_file() or q.is_symlink()}
 allowed={n for n in files if n.startswith(top+'/')} | (pf.ADDED_SOURCE if top=='src'else set())
 assert actual==allowed,(top,actual^allowed)
# One single-byte mutation for every approved B/C asset is sufficient to show
# that no accepted artistic delta became a blanket asset exception.
asset_negatives=[];asset_reversions=[]
for name in sorted(pf.published_delta()):
 if not name.startswith('assets/'):continue
 raw=(root/name).read_bytes();assert raw==git('show',pf.BASE+':'+name)
 bad=raw[:-1]+bytes([raw[-1]^1])
 try:pf.qualify_published_file(name,bad)
 except AssertionError:asset_negatives.append(name)
 else:raise AssertionError(('mutated approved asset accepted',name))
 if name in set(git('ls-tree','-r','--name-only',pf.LEGACY,'assets').decode().splitlines()):
  old=git('show',pf.LEGACY+':'+name);assert old!=raw
  try:pf.qualify_published_file(name,old)
  except AssertionError:asset_reversions.append(name)
  else:raise AssertionError(('old approved asset reversion accepted',name))
resources={}
for q in sorted((root/'assets/hd/packs/startup-title-settings-v1').iterdir()):
 if q.is_file():
  name=str(q.relative_to(root));raw=q.read_bytes();assert raw==git('show',pf.NATIVE+':'+name);resources[name]=sha(raw)
report=dict(result='PASS',qualified_parent=pf.BASE,qualified_tree='cc1f5da9feeea8d12407bd7e5a079981ef711d13',native_tested_source=pf.NATIVE,production_files=len(current),exact_projected_production_difference='Eight C FNV pins and their one adjacent comment only',portable_parent=pf.PORTABLE['BASE'],production_mutation_rejections=len(rejections),whole_parent_files=len(files),exact_reverse_projection_files=changed,exact_parent_asset_bytes=asset_bytes,approved_asset_mutation_rejections=len(asset_negatives),approved_asset_paths=asset_negatives,old_asset_reversion_rejections=len(asset_reversions),startup_resources=resources,no_source_or_asset_path_wildcards=True,new_game_runs=0,windows='Source inventory is checked separately; no Windows compilation/runtime claim from this script')
if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
