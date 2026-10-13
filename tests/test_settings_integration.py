#!/usr/bin/env python3
"""Exact dual-parent source/art preservation and finite coexistence checks."""
from pathlib import Path
import argparse,hashlib,json,stat,subprocess,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'prototype'))
from settings_font_coexistence import PINS,project_settings_source,verify_settings_sources
from settings_font_bundle import build_bundles
BASE='5629b3dda05b2aa77af3c624841320d05c0f7130'
TESTED='504b3d4723d382548c698a77ce5dae318ffa146b'
git=lambda *args:subprocess.check_output(['git','-C',str(ROOT),*args])
sha=lambda raw:hashlib.sha256(raw).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
source_count,addition_count=verify_settings_sources(ROOT)
bundles,family=build_bundles(ROOT)
# Each complete-file change is explicitly frozen; no wildcard source exemption.
approved=json.loads((ROOT/'docs/settings-font-v1/INTEGRATION_FILE_PINS.json').read_text())
expected=set(PINS)|{'README.md','README.zh-CN.md','assets/hd/manifest.json','prototype/build-hd-assets.py','prototype/test-type3-small-binding.py','prototype/tests/title-menu-font/test_source.py','prototype/tests/title-menu-font/test_package.py','prototype/tests/title-package/test_package.py','prototype/tests/startup-manufacturer/test_package.py'}
assert set(approved)==expected
count=asset_bytes=0;changed=[];sparse=0
for row in git('ls-tree','-rz',BASE).split(b'\0'):
    if not row:continue
    meta,name=row.split(b'\t',1);mode,kind,blob=meta.decode().split();name=name.decode();path=ROOT/name;assert kind=='blob'
    count+=1
    if not path.exists():
        marker=git('ls-files','-v','--',name).decode();assert marker.startswith('S '),name
        current=git('rev-parse','HEAD:'+name).decode().strip();assert current==blob,name;sparse+=1;continue
    assert path.is_file() and not path.is_symlink(),name
    assert ('100755' if stat.S_IMODE(path.stat().st_mode)&0o111 else '100644')==mode,name
    raw=path.read_bytes();same=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob
    if same:
        if name.startswith('assets/'):asset_bytes+=len(raw)
    else:
        assert name in approved,name
        pin=approved[name];assert sha(raw)==pin['current'] and sha(git('show',BASE+':'+name))==pin['previous'],name
        changed.append(name)
assert set(changed)==expected
# Every production source file used by actual acceptance remains exact except
# the separately tested type3 append, whose exact removal must recover504b3d4.
production=[]
for path in git('ls-tree','-r','--name-only',TESTED,'src').decode().splitlines():
    raw=(ROOT/path).read_bytes()
    if path=='src/render_mirror.c':
        assert project_settings_source(path,raw)==git('show',BASE+':'+path)
        s=raw.decode().replace('static Asset assets[422];','static Asset assets[416];')
        for first,last in [('/* Approved type3 six-member small bank1 family,','bool render_mirror_enemy_tile('),(' /* Type3/type16 use one small tile at the original top-left, not a composite.',' /* Existing ground201..209 and rotor210..217 remain unchanged. */')]:
            assert s.count(first)==s.count(last)==1;start=s.index(first);end=s.index(last,start);s=s[:start]+s[end:]
        raw=s.encode()
    assert raw==git('show',TESTED+':'+path),path;production.append(path)
# Mutation tests prove the projection cannot conceal arbitrary source changes.
negative=0
for path in PINS:
    raw=(ROOT/path).read_bytes()
    for offset in {0,len(raw)//2,len(raw)-1}:
        bad=raw[:offset]+bytes([raw[offset]^1])+raw[offset+1:]
        try:project_settings_source(path,bad)
        except AssertionError:negative+=1
        else:raise AssertionError(('mutation accepted',path,offset))
project=ROOT/'visualc/opentyrian.vcxproj';ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'};xml=ET.parse(project)
items=[x.attrib['Include'] for x in xml.findall('.//m:ClCompile',ns) if 'Include'in x.attrib];assert len(items)==len(set(items))
assert {Path(x.replace('\\','/')).name for x in items}=={x.name for x in (ROOT/'src').glob('*.c')}
headers=[x.attrib['Include'] for x in xml.findall('.//m:ClInclude',ns) if 'Include'in x.attrib];assert headers.count('..\\src\\settings_font.h')==1
for name in [*items,*headers]:assert (project.parent/name.replace('\\','/')).is_file(),name
manifest=json.loads((ROOT/'assets/hd/manifest.json').read_text());assert manifest.pop('startup_settings_font_v1')==family
assert (json.dumps(manifest,indent=2)+'\n').encode()==git('show',BASE+':assets/hd/manifest.json')
report={'result':'PASS','published_parent':BASE,'actual_tested_source':TESTED,'previous_files_checked':count,'sparse_git_identity_checks':sparse,'unchanged_prior_asset_bytes':asset_bytes,'exact_changed_previous_files':sorted(changed),'actual_tested_production_files_preserved':len(production),'type3_renderer_delta_exact_and_commuting':True,'coexistence_source_files':source_count,'new_runtime_source_resource_pins':addition_count,'projection_mutation_rejections':negative,'compatibility_files':len(bundles),'unchanged_title_compatibility_files':6,'all_prior_manifest_fields_exact':True,'windows':'Complete C source/header XML inventory only; no Windows build/runtime claim'}
a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
