#!/usr/bin/env python3
"""Prove C-v2's finite eight-stamp/asset transition preserves all other bytes."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
from type15_source_projection import audit_sources,rejection_tests
BASE='f3bcc061d8a136e257e9c36d40629b4f948a1708';IDS=[39,41,43,45,91,93,129,131]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--baseline',default=BASE);a=p.parse_args();repo=Path(__file__).resolve().parents[1]
if a.out.exists():p.error('Report must be new')
git=lambda *x:subprocess.check_output(['git','-C',str(repo),*x]);assert git('rev-parse',a.baseline+'^{commit}').decode().strip()==BASE
current,source_base,version=audit_sources(repo);assert version=='v2';negative=rejection_tests(source_base)
m=json.loads((repo/'assets/hd/manifest.json').read_text());prior=json.loads(git('show',BASE+':assets/hd/manifest.json'));restored=json.loads(json.dumps(m));allowed={'src/render_mirror.c','assets/hd/manifest.json','prototype/build-type15-art.py','prototype/test-type15-source-guards.py','prototype/test-type15-binding.py','prototype/test-type15-binding.c','prototype/test-type15-preservation.py','prototype/test-type4-binding.py','prototype/tests/startup-manufacturer/test_package.py','prototype/tests/title-package/test_package.py'}
for key in('default_preview_pack','default_debug_pack'):
 name=m[key];assert name==prior[key]and m['packs'][name]['count']==prior['packs'][name]['count']
 for i in IDS:
  filename=f'enemy-newsh2-{i}-8.hda';assert m['packs'][name]['files'][filename]!=prior['packs'][name]['files'][filename]
  restored['packs'][name]['files'][filename]=prior['packs'][name]['files'][filename];allowed.add(str(Path('assets/hd/packs')/name/filename))
added=set(m['source_pngs'])-set(prior['source_pngs']);assert len(added)==8
for h in added:restored['source_pngs'].pop(h)
restored['enemy_type15_eightheading_v1']=prior['enemy_type15_eightheading_v1'];assert restored==prior and(json.dumps(restored,indent=2)+'\n').encode()==git('show',BASE+':assets/hd/manifest.json')
# Sparse worktrees retain omitted immutable objects in the exact index. All
# materialized files are byte-checked; omitted paths must be skip-worktree at
# their original object, never interpreted as deletion or unchecked changes.
index={}
for line in git('ls-files','-sv').decode().splitlines():
 flag,mode,blob,stage_path=line.split(' ',3);stage,name=stage_path.split('\t',1);assert stage=='0';index[name]=(flag,blob)
changed=[];disk_checked=0;sparse_checked=0;identical_asset_bytes=0
for line in git('ls-tree','-r',BASE).decode().splitlines():
 meta,name=line.split('\t',1);mode,kind,blob=meta.split();assert kind=='blob';q=repo/name
 if q.is_file():
  assert not q.is_symlink(),name;raw=q.read_bytes();actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();disk_checked+=1
  if actual!=blob:changed.append(name)
  elif name.startswith('assets/'):identical_asset_bytes+=len(raw)
 else:
  assert index.get(name)==('S',blob),('missing non-sparse or changed index',name);sparse_checked+=1
assert set(changed)==allowed,('nonfinite changed set',sorted(set(changed)^allowed));assert not git('diff','--name-only','--diff-filter=D',BASE)
project=repo/'visualc/opentyrian.vcxproj';xml=ET.parse(project);ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'};items=[n.attrib['Include']for n in xml.findall('.//m:ClCompile',ns)if'Include'in n.attrib]
assert project.read_bytes()==git('show',BASE+':visualc/opentyrian.vcxproj');assert '..\\src\\render_mirror.c'in items
assert len(items)==len(set(items))and{Path(n.replace('\\','/')).name for n in items}=={q.name for q in(repo/'src').glob('*.c')}
for name in items:assert(project.parent/name.replace('\\','/')).is_file(),name
report={'status':'PASS','baseline':BASE,'exact_eight_pin_and_comment_reversal':True,'all_other_production_files_exact':len(current)-1,'source_negative_controls':len(negative),'previous_materialized_files_byte_checked':disk_checked,'omitted_sparse_files_original_index_checked':sparse_checked,'unchanged_materialized_asset_bytes':identical_asset_bytes,'changed_tracked_files':sorted(changed),'manifest_reversal_exact':True,'all_unaffected_B_and_neighbor_resources_preserved':True,'Windows_source_list_unchanged_and_valid':True,'Windows_build_runtime':False,'game_runs':0}
a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
