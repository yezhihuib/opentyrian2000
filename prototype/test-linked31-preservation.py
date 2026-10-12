#!/usr/bin/env python3
"""Exact finite source delta, previous tracked bytes, manifest and Windows XML."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,xml.etree.ElementTree as ET
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--baseline',default='1df1d87b49b478d0e8b2eb5c5a4778c3f20866a8');a=p.parse_args();repo=Path(__file__).resolve().parents[1]
if a.out.exists():p.error('Report must be new')
git=lambda *x:subprocess.check_output(['git','-C',str(repo),*x]);sha=lambda x:hashlib.sha256(x).hexdigest();baseline=git('show',a.baseline+':src/render_mirror.c').decode();current=(repo/'src/render_mirror.c').read_text();s=current
s=s.replace('static Asset assets[382];','static Asset assets[374];').replace('terrain_sources[199]','terrain_sources[195]').replace('terrain_source_count<199','terrain_source_count<195')
start=s.index('/* One coordinated selected-pack family.');end=s.index('bool render_mirror_enemy_tile(',start);s=s[:start]+s[end:]
start=s.index(' /* Linked31 four complete newsh2 composites;');end=s.index(' if(role==ASSET_NEWSHE)',start);s=s[:start]+s[end:]
start=s.index('/* Static linked31 remnants, strictly');end=s.index('void render_mirror_bind_terrain(',start);s=s[:start]+s[end:]
s=s.replace('||layer3_linked31_slot(id)>=0','').replace('  int linked31_slot=layer3_linked31_slot(id);\n','').replace('||linked31_slot>=0','').replace('  if(slot<0)slot=linked31_slot;\n','').replace('  if(linked31_slot>=0&&!linked31_family_ready())continue;\n','')
assert s==baseline,'Nonfinite renderer delta'
allowed={'src/render_mirror.c','assets/hd/manifest.json','prototype/build-hd-assets.py','prototype/tests/startup-manufacturer/test_package.py'};changed=[];checked=0;previous_asset_bytes=0
for line in git('ls-tree','-r',a.baseline).decode().splitlines():
 metadata,name=line.split('\t',1);mode,kind,blob=metadata.split();assert kind=='blob';q=repo/name
 assert q.is_file(),name
 raw=q.read_bytes();actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();checked+=1
 if actual!=blob:changed.append(name)
 elif name.startswith('assets/'):previous_asset_bytes+=len(raw)
assert set(changed)==allowed,changed
m=json.loads((repo/'assets/hd/manifest.json').read_text());prior=json.loads(git('show',a.baseline+':assets/hd/manifest.json'));restored=json.loads(json.dumps(m));family=restored.pop('linked31_installation_v1');assert len(family['entries'])==8
for e in family['entries']:
 name=('terrain-shapesz' if e['kind']=='terrain' else 'enemy-newsh2')+f"-{e['id']}-8.hda"
 for key in ['default_preview_pack','default_debug_pack']:
  pack=restored['packs'][restored[key]];entry=pack['files'].pop(name);pack['count']-=1;restored['source_pngs'].pop(entry['sha256'],None)
assert restored==prior,'Previous manifest changed'
project=repo/'visualc/opentyrian.vcxproj';xml=ET.parse(project);ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'};items=[n.attrib['Include'] for n in xml.findall('.//m:ClCompile',ns) if 'Include'in n.attrib];assert '..\\src\\render_mirror.c' in items
for name in items:assert (project.parent/name.replace('\\','/')).is_file(),name
assert project.read_bytes()==git('show',a.baseline+':visualc/opentyrian.vcxproj')
report={'status':'passed','baseline':a.baseline,'renderer_reverts_exactly_after_finite_family_removal':True,'previous_tracked_files_checked':checked,'previous_changed_files':changed,'previous_asset_payload_bytes_identical':previous_asset_bytes,'previous_manifest_restored_exactly':True,'all_gameplay_startup_sources_unchanged':True,'Windows_project_XML':'parsed; all compile references exist; unchanged existing renderer unit listed','Windows_compilation_runtime':False,'render_source_sha256':sha(current.encode()),'default_pack_counts':[m['packs'][m[k]]['count'] for k in ['default_preview_pack','default_debug_pack']]};a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
