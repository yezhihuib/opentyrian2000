#!/usr/bin/env python3
"""Prove the opposite-family append preserves all prior bytes and renderer code."""
from pathlib import Path
import argparse,hashlib,json,subprocess,xml.etree.ElementTree as ET
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--baseline',default='67656d102a67cd1bd76c823a2b20f6023f7bb9f0');a=p.parse_args();repo=Path(__file__).resolve().parents[1]
if a.out.exists():p.error('Report must be new')
git=lambda *x:subprocess.check_output(['git','-C',str(repo),*x]);sha=lambda x:hashlib.sha256(x).hexdigest();baseline=git('show',a.baseline+':src/render_mirror.c').decode();current=(repo/'src/render_mirror.c').read_text();s=current
s=s.replace('static Asset assets[396];','static Asset assets[389];')
s=s.replace(' /* Explicit bank2 left-family allowlist; matching numbers never borrow\n  * newsh2 slots. The distinct opposite family is handled separately below. */',' /* Exactly the approved left seven-part bank2 family; never borrow newsh2\n  * slots for matching base numbers or bind the mirrored right-hand family. */')
start=s.index('/* Approved opposite newsh4 seven-part family,');end=s.index('bool render_mirror_enemy_tile(',start);s=s[:start]+s[end:]
start=s.index('  /* Distinct opposite/link2 composites have their own coherent fallback.');end=s.index('\n }\n if(role==ASSET_NEWSHE)',start);s=s[:start]+s[end:];s=s.replace('   slot=382+i;break;\n  }\n\n }','   slot=382+i;break;\n  }\n }')
assert s==baseline,'Nonfinite renderer delta'
allowed={'src/render_mirror.c','assets/hd/manifest.json','prototype/build-hd-assets.py','prototype/tests/startup-manufacturer/test_package.py','prototype/tests/title-package/test_package.py'};changed=[];checked=0;previous_asset_bytes=0
for line in git('ls-tree','-r',a.baseline).decode().splitlines():
 metadata,name=line.split('\t',1);mode,kind,blob=metadata.split();assert kind=='blob';q=repo/name
 assert q.is_file(),name
 raw=q.read_bytes();actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();checked+=1
 if actual!=blob:changed.append(name)
 elif name.startswith('assets/'):previous_asset_bytes+=len(raw)
assert set(changed)==allowed,changed
m=json.loads((repo/'assets/hd/manifest.json').read_text());prior=json.loads(git('show',a.baseline+':assets/hd/manifest.json'));restored=json.loads(json.dumps(m));family=restored.pop('newsh4_opposite7_v1');assert len(family['entries'])==7
for e in family['entries']:
 name=f"enemy-newsh4-{e['id']}-8.hda"
 for key in ['default_preview_pack','default_debug_pack']:
  pack=restored['packs'][restored[key]];entry=pack['files'].pop(name);pack['count']-=1;restored['source_pngs'].pop(entry['sha256'],None)
assert restored==prior,'Previous manifest changed'
assert (json.dumps(restored,indent=2)+'\n').encode()==git('show',a.baseline+':assets/hd/manifest.json')
project=repo/'visualc/opentyrian.vcxproj';xml=ET.parse(project);ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'};items=[n.attrib['Include'] for n in xml.findall('.//m:ClCompile',ns) if 'Include'in n.attrib];assert '..\\src\\render_mirror.c' in items
for name in items:assert (project.parent/name.replace('\\','/')).is_file(),name
assert project.read_bytes()==git('show',a.baseline+':visualc/opentyrian.vcxproj')
assert len(items)==len(set(items)) and {str(Path(n.replace('\\','/')).name) for n in items}=={q.name for q in (repo/'src').glob('*.c')}
assert 'terrain_sources[199]' in current and 'terrain_source_count<199' in current
report={'status':'passed','baseline':a.baseline,'renderer_reverts_exactly_after_finite_family_removal':True,'left_family_cache_and_route_unchanged':True,'previous_tracked_files_checked':checked,'previous_changed_files':changed,'previous_asset_payload_bytes_identical':previous_asset_bytes,'previous_manifest_restored_exactly':True,'all_gameplay_startup_sources_unchanged':True,'Windows_project_XML':'parsed; all compile references exist; unchanged existing renderer unit listed','Windows_compilation_runtime':False,'render_source_sha256':sha(current.encode()),'default_pack_counts':[m['packs'][m[k]]['count'] for k in ['default_preview_pack','default_debug_pack']]};a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
