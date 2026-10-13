#!/usr/bin/env python3
"""Fresh complete-file preservation check against exact published b2a6e4a.
Regenerated recovery test. No game, capture, Git mutation or Windows build.
"""
from pathlib import Path
import argparse,hashlib,json,stat,subprocess,unittest,xml.etree.ElementTree as ET
from type3_small_coexistence import project_type3_small_family
BASE='b2a6e4a1e924aed71630f9f63c0ba4648e920d6d'
ALLOWED={'src/render_mirror.c','assets/hd/manifest.json','prototype/build-hd-assets.py','prototype/test-newsh4-entry6-binding.py','prototype/tests/startup-manufacturer/test_package.py','prototype/tests/title-package/test_package.py','prototype/tests/title-menu-font/test_package.py','prototype/tests/title-menu-font/test_source.py'}
sha=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();R=Path(__file__).resolve().parents[1];out=a.out
assert out.is_absolute()and not out.exists()and out.parent.is_dir()and not any(x.is_symlink()for x in[out,*out.parents])and R not in out.parents and out not in R.parents
git=lambda *args:subprocess.check_output(['git','-C',str(R),*args]);assert git('rev-parse',BASE).decode().strip()==BASE
renderer=(R/'src/render_mirror.c').read_text();assert sha(renderer.encode())=='7a39ffd4959c307c23707ae63c41030cd92ef757375b95f680445ff4f3e85420'
restored=renderer.replace('static Asset assets[422];','static Asset assets[416];')
for first,last in [('/* Approved type3 six-member small bank1 family,','bool render_mirror_enemy_tile('),(' /* Type3/type16 use one small tile at the original top-left, not a composite.',' /* Existing ground201..209 and rotor210..217 remain unchanged. */')]:
 assert restored.count(first)==restored.count(last)==1;start=restored.index(first);end=restored.index(last,start);restored=restored[:start]+restored[end:]
assert restored.encode()==git('show',BASE+':src/render_mirror.c')
changed=[];count=assetbytes=0
for row in git('ls-tree','-rz',BASE).split(b'\0'):
 if not row:continue
 meta,name=row.split(b'\t',1);mode,kind,blob=meta.decode().split();name=name.decode();path=R/name
 assert kind=='blob'and mode in['100644','100755']and path.is_file()and not any(q.is_symlink()for q in[path,*path.parents]),name
 assert ('100755'if stat.S_IMODE(path.stat().st_mode)&0o111 else'100644')==mode,name
 raw=path.read_bytes();same=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob;count+=1
 if not same:changed.append(name)
 elif name.startswith('assets/'):assetbytes+=len(raw)
assert set(changed)==ALLOWED,changed
manifest=json.loads((R/'assets/hd/manifest.json').read_text());projected=json.loads(json.dumps(manifest));project_type3_small_family(unittest.TestCase(),projected);assert(json.dumps(projected,indent=2)+'\n').encode()==git('show',BASE+':assets/hd/manifest.json')
project=R/'visualc/opentyrian.vcxproj';assert project.read_bytes()==git('show',BASE+':visualc/opentyrian.vcxproj');xml=ET.parse(project);ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'};items=[x.attrib['Include']for x in xml.findall('.//m:ClCompile',ns)if'Include'in x.attrib];assert len(items)==len(set(items))
assert{Path(x.replace('\\','/')).name for x in items}=={x.name for x in(R/'src').glob('*.c')}
for item in items:assert(project.parent/item.replace('\\','/')).is_file()
# Exact portability identities, without inventing missing local Git objects.
historical=json.loads((R/'docs/NEWSH4_ENTRY6_SOURCE_VALIDATION.json').read_text())['binding']['renderer_source_sha256']['baseline'];entry=git('show','305c43a:src/render_mirror.c');assert sha(entry)==historical=='2d93ab3ed787acf6f31a0c96867e2057bd607971f1ac06a4545a3e98589ad69c'
longraw=git('show','67656d1:assets/hd/manifest.json');assert sha(longraw)=='c7ca4c55b65fc2d856b2eb85055626596cb7c35940a62bfe9e9a04a564b9559d';long=json.loads(longraw);family='newsh4_long7_v1';assert{k:v for k,v in manifest[family].items()if k!='runtime_status'}=={k:v for k,v in long[family].items()if k!='runtime_status'}
source=R/long[family]['source'];inventory=json.loads((source/'inventory.json').read_text());assert sha((source/'inventory.json').read_bytes())==long[family]['source_inventory_sha256']=='dd6c3f91282e98b9dc583701267ef4963833bbc7ec0dbaaa8ade450be2726fbb'
longpins={}
for key in ['default_preview_pack','default_debug_pack']:
 pack=manifest[key]
 for i in [153,155,157,159,191,193,195]:
  name=f'enemy-newsh4-{i}-8.hda';e=long['packs'][pack]['files'][name];assert manifest['packs'][pack]['files'][name]==e
  path='assets/hd/packs/'+pack+'/'+name;raw=(R/path).read_bytes();assert sha(raw)==e['sha256'];longpins[path]=sha(raw)
  q=manifest['source_pngs'][e['sha256']];assert q==long['source_pngs'][e['sha256']]and sha((R/q['path']).read_bytes())==q['sha256'];longpins[q['path']]=q['sha256']
report={'status':'PASS_FRESH_RECOVERY_PRESERVATION','baseline':BASE,'previous_files_checked':count,'previous_changed_files':changed,'prior_modes_unchanged':True,'prior_asset_bytes_identical':assetbytes,'renderer_sha256':sha(renderer.encode()),'renderer_restores_exact_published_parent':True,'manifest_restores_exact_published_parent':True,'menu_source_art_and_XML_unchanged':True,'test_portability':{'lost_entry_baseline':'fe5f5d7922105dccf67bfe2648ac366c3031bc66','published_entry_renderer':'305c43aae91f0a20cc4cd622fc0a99b1bb37a37c','exact_renderer_identity_sha256':historical,'lost_long_family_commit':'20cae6e06f5165b901e606ee7277091b0c40a59a','published_long_family_manifest':'67656d1','published_manifest_sha256':sha(longraw),'historically_pinned_frozen_inventory':long[family]['source_inventory_sha256'],'relevant_family_metadata_and_payloads_identical':longpins,'missing_full_commit_bytes_not_recovered':True},'Windows':'XML preservation only; no compile/runtime claim','game_runs':0}
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
