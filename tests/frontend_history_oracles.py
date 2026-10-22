"""Historical oracle bodies with explicit snapshot and native-source inputs.

The assertions are the original public script assertions. Only argument/output
plumbing and missing-private-Git reads are replaced by explicit content APIs.
This worker is run in a fresh process with historical helper imports first.
"""
from pathlib import Path
import json
import sys
from frontend_history_support import NativeSources


def audit_native_sources(root, c, portable, native):
    tracked = native.paths()
    assert tracked
    baseline = {name: native.read(name) for name in tracked}
    actual = {str(q.relative_to(root)) for q in (root/'src').rglob('*')
              if q.is_file() or q.is_symlink()}
    assert actual == set(tracked), 'Added/removed historical source paths'
    for name in tracked:
        assert (root/name).is_file() and not (root/name).is_symlink(), name
    portable['verify']()
    current = {name: portable['project'](name, (root/name).read_bytes()) for name in tracked}
    return current, baseline, c['validate_sources'](current, baseline)

def test_pregame_coexistence(root, native):
    from pathlib import Path
    import argparse,hashlib,json,runpy
    import pregame_font_projection as pf
    pf.PORTABLE['verify']()
    root=pf.ROOT;git=pf.git;sha=lambda b:hashlib.sha256(b).hexdigest()
    assert git('rev-parse',pf.BASE+'^{tree}').decode().strip()=='cc1f5da9feeea8d12407bd7e5a079981ef711d13'
    assert git('show','-s','--format=%P',pf.BASE).decode().strip()=='f3bcc061d8a136e257e9c36d40629b4f948a1708'
    # The accepted C helper retains exact whole-source-map validation and every
    # adversarial constant/order/comment/source-path control, now on native fonts.
    c=runpy.run_path(str(root/'prototype/type15_source_projection.py'))
    assert c['BASE']==pf.NATIVE
    current,baseline,version=audit_native_sources(root,c,pf.PORTABLE,native);assert version=='v2'
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
     allowed={n for n in files if n.startswith(top+'/')} | (pf.ADDED_SOURCE if top=='src'else pf.PORTABLE['RED_ASSETS'])
     assert actual==allowed,(top,actual^allowed)
    # One single-byte mutation for every approved B/C asset is sufficient to show
    # that no accepted artistic delta became a blanket asset exception.
    asset_negatives=[];asset_reversions=[]
    for name in sorted(pf.published_delta()):
     if not name.startswith('assets/'):continue
     raw=pf.PORTABLE['outer'](name,(root/name).read_bytes());assert raw==git('show',pf.BASE+':'+name)
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
      name=str(q.relative_to(root));raw=q.read_bytes();assert sha(raw)==native.resource_sha256(name);resources[name]=sha(raw)
    report=dict(result='PASS',qualified_parent=pf.BASE,qualified_tree='cc1f5da9feeea8d12407bd7e5a079981ef711d13',native_tested_source=pf.NATIVE,production_files=len(current),exact_projected_production_difference='Eight C FNV pins and their one adjacent comment only',portable_parent=pf.PORTABLE['BASE'],production_mutation_rejections=len(rejections),whole_parent_files=len(files),exact_reverse_projection_files=changed,exact_parent_asset_bytes=asset_bytes,approved_asset_mutation_rejections=len(asset_negatives),approved_asset_paths=asset_negatives,old_asset_reversion_rejections=len(asset_reversions),startup_resources=resources,no_source_or_asset_path_wildcards=True,new_game_runs=0,windows='Source inventory is checked separately; no Windows compilation/runtime claim from this script')
    report['native_source_provenance']=native.provenance()
    return report

def test_pregame_font_integration(root, native):
    from pathlib import Path
    import argparse,hashlib,json,subprocess,xml.etree.ElementTree as ET
    from pregame_font_projection import ROOT,BASE,EDITS,ADDED_SOURCE,git,project,verify,PORTABLE
    production=verify();unchanged=0;asset_bytes=0;changed=[];negative=0
    # A frozen exact reverse projection admits only the finite observer edits.
    for row in git('ls-tree','-rz',BASE).split(b'\0'):
     if not row:continue
     meta,name=row.split(b'\t',1);name=name.decode();mode,kind,blob=meta.decode().split();path=ROOT/name
     assert kind=='blob' and path.is_file() and not path.is_symlink(),name
     raw=PORTABLE['project'](name,path.read_bytes());same=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob
     if same:
      unchanged+=1
      if name.startswith('assets/'):asset_bytes+=len(raw)
     else:
      assert name in EDITS,name;project(name,raw);changed.append(name)
    assert set(changed)==set(EDITS)
    for name in EDITS:
     raw=(ROOT/name).read_bytes()
     for offset in {0,len(raw)//2,len(raw)-1}:
      try:project(name,raw[:offset]+bytes([raw[offset]^1])+raw[offset+1:])
      except AssertionError:negative+=1
      else:raise AssertionError((name,'unrelated mutation admitted',offset))
    menu=(ROOT/'src/game_menu.c').read_text()
    assert menu.count('pregame_font_begin(')==1
    assert '!twoPlayerMode && !onePlayerAction && !isNetworkGame && !superTyrian && superArcadeMode == SA_NONE && !constantPlay && !timedBattleMode' in menu
    assert menu.index('pregame_font_begin(')>menu.index('memcpy(VGAScreen->pixels, VGAScreen2->pixels, VGAScreen->pitch * VGAScreen->h);')
    assert 'fade_black(10);\n\t\t\t\t\tpregame_font_end();\n\t\t\t\t\tJE_helpSystem(2);' in menu
    for name in ('src/fonthand.c','src/selector_font.c','src/selector_font_output.c','src/settings_font.c','src/load_font.c','src/menus.c','src/title_menu_font.inc','src/player.c','src/config.c','src/tyrian2.c'):
     assert PORTABLE['project'](name,(ROOT/name).read_bytes())==git('show',BASE+':'+name),name
    ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'};tree=ET.parse(ROOT/'visualc/opentyrian.vcxproj')
    c=[x.attrib['Include']for x in tree.findall('.//m:ClCompile',ns)if 'Include'in x.attrib]
    h=[x.attrib['Include']for x in tree.findall('.//m:ClInclude',ns)if 'Include'in x.attrib]
    assert len(c)==len(set(c)) and c.count('..\\src\\pregame_font.c')==1 and h.count('..\\src\\pregame_font.h')==1
    assert {Path(x.replace('\\','/')).name for x in c}=={x.name for x in (ROOT/'src').glob('*.c')}
    report={'result':'PASS','base':BASE,'exact_existing_file_projections':sorted(changed),'unchanged_prior_files':unchanged,'unchanged_asset_bytes':asset_bytes,'mutation_rejections':negative,'production_delta':sorted(production),'two_context_only':True,'original_draw_input_state_save_sound_tokens_and_bytes_preserved':True,'selector_output_and_existing_fonts_exact_after_portability_projection':True,'portable_parent':PORTABLE['BASE'],'windows':'source inventory only; no Windows build/runtime claim','game_runs':False}
    report['native_source_provenance']=native.provenance()
    return report

def test_settings_integration(root, native):
    from pathlib import Path
    import argparse,hashlib,json,stat,subprocess,sys,xml.etree.ElementTree as ET
    ROOT=root;sys.path.insert(0,str(ROOT/'prototype'))
    from settings_font_coexistence import PINS,project_settings_source,verify_settings_sources
    from settings_font_bundle import build_bundles
    BASE='5629b3dda05b2aa77af3c624841320d05c0f7130'
    TESTED='504b3d4723d382548c698a77ce5dae318ffa146b'
    git=lambda *args:subprocess.check_output(['git','-C',str(ROOT),*args])
    sha=lambda raw:hashlib.sha256(raw).hexdigest()
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
    for path in native.paths():
        raw=(ROOT/path).read_bytes()
        if path=='src/render_mirror.c':
            assert project_settings_source(path,raw)==git('show',BASE+':'+path)
            s=raw.decode().replace('static Asset assets[422];','static Asset assets[416];')
            for first,last in [('/* Approved type3 six-member small bank1 family,','bool render_mirror_enemy_tile('),(' /* Type3/type16 use one small tile at the original top-left, not a composite.',' /* Existing ground201..209 and rotor210..217 remain unchanged. */')]:
                assert s.count(first)==s.count(last)==1;start=s.index(first);end=s.index(last,start);s=s[:start]+s[end:]
            raw=s.encode()
        assert raw==native.read(path),path;production.append(path)
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
    report['native_source_provenance']=native.provenance()
    return report

if __name__ == '__main__':
    root = Path(sys.argv[1]).resolve()
    name = sys.argv[2]
    source_repo = Path(sys.argv[3]).resolve()
    output = Path(sys.argv[4]).resolve()
    sys.path.insert(0, str(root/'tests'))
    sys.path.insert(0, str(root/'prototype'))
    native = NativeSources('settings' if name == 'test_settings_integration.py' else 'pregame', source_repo)
    result = globals()[name.removesuffix('.py')](root, native)
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
