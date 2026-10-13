#!/usr/bin/env python3
"""Bounded Load-only additions project to the exact published C token stream.
No game execution, profile/config access or original bitmap distribution.
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,xml.etree.ElementTree as ET,runpy
ROOT=Path(__file__).resolve().parents[1]
PORTABLE=runpy.run_path(str(ROOT/'tests/portable_font_projection.py'))
BASE='a4974da93ee75fb18c7ad5827ea42a6b02d1b74d'
CHANGED={'src/helptext.c','src/mainint.c','src/palette.c','src/params.c','src/picload.c','src/render_mirror.c','src/settings_font.c','src/settings_font.h','src/sprite.c','src/video.c','tests/run_settings_font_tests.sh','visualc/opentyrian.vcxproj'}
git=lambda *a:subprocess.check_output(['git','-C',str(ROOT),*a])
sha=lambda b:hashlib.sha256(b).hexdigest()
# Exact metadata-only discoverability additions, approved after runtime QA.
# Whole-file hashes and literal suffix removal must recover published bytes.
README_ADDITIONS={
    'README.md': ('ef945bb1082de27e25094e4c71f08faefb8cde43a6495a81623c36af52ed3c6c', '\nThe same `startup-title-settings-v1` pack now also supports bounded Load typography, with whole-frame classic fallback for unsupported names or scalers; see [Load usage](docs/load-font-v1/USAGE.txt).\n'),
    'README.zh-CN.md': ('552e86d45195207566eafe71b865a6e53fdf11b2430fc3ea94d5d96bb10d1fd5', '\n同一 `startup-title-settings-v1` 资源包现也支持有限范围的读档界面字体，遇到不支持的存档名或缩放方式时整帧回退至原版；详见[读档字体使用说明](docs/load-font-v1/USAGE.txt)。\n'),
}
def project_readme(name,raw):
    digest,suffix=README_ADDITIONS[name];suffix=suffix.encode('utf-8')
    assert sha(raw)==digest,(name,'unapproved README bytes')
    assert raw.endswith(suffix),(name,'exact README addition')
    return raw[:-len(suffix)]
def tokens(text):
    pattern=r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*[\s\S]*?\*/|//[^\n]*|\s+|[A-Za-z_]\w*|(?:0[xX][0-9a-fA-F]+|\d+)(?:[uUlLfF]*)|<<=?|>>=?|\+\+|--|->|&&|\|\||[+*/%&|^!=<>-]=|.'
    return [x for x in re.findall(pattern,text) if not x.isspace() and not x.startswith(('/*','//'))]
def project(name,text):
    text=text.replace('\r\n','\n').replace('#include "load_font.h"\n','')
    if name=='src/settings_font.c':
        text=text.replace('size_t settings_font_static_bytes(void){return sizeof(sf);}\n','').replace('bool settings_font_owns_display(void){return sf.active;}\n','')
        text=text.replace('sizeof(sf)+600000+SF_PAYLOAD','sizeof(sf)+SF_PAYLOAD').replace('load_font_static_bytes()>600000||','')
    if name=='src/settings_font.h':
        text=text.replace('size_t settings_font_static_bytes(void);\n','').replace('bool settings_font_owns_display(void);\n','')
    if name=='src/video.c':
        text='\n'.join(x for x in text.split('\n') if not x.strip().startswith('if(load_font_present('))
        text=text.replace(' || load_font_owns_display()','')
    # Remove only known dormant call statements, not arbitrary new code.
    allowed={'set_directory','begin','end','invalidate','table_reset','frame_begin','run_begin','run_end','glyph_begin','glyph_end','arrow_begin','arrow_sprite_begin','arrow_sprite_end','arrow_end','help_begin','help_line_begin','help_line_end','help_end','frame_end','pixel','rect','cursor_begin','cursor_done','cursor_sprite_begin','cursor_sprite_end','cursor_erased','fade_declare','fade_start','fade_step'}
    for m in reversed(list(re.finditer(r'\bload_font_(\w+)\(',text))):
        assert m[1] in allowed,(name,m[1]);start=m.start();pos=m.end();level=1
        while level:
            if text[pos]=='(':level+=1
            if text[pos]==')':level-=1
            pos+=1
        assert text[pos]==';',(name,text[start:pos+1]);text=text[:start]+text[pos+1:]
    if name=='src/sprite.c':
        a=text.index('void blit_sprite2(SDL_Surface');b=text.index('void blit_sprite2_clip(',a)
        middle=text[a:b].replace('{  return; }','return;');text=text[:a]+middle+text[b:]
    return tokens(text)
def main():
    PORTABLE['verify']()
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    pins=json.loads((ROOT/'docs/load-font-source-pins.json').read_text())
    changed=[];metadata_changed=[];unchanged=0;asset_bytes=0;token_proofs=0
    for line in git('ls-tree','-rz',BASE).split(b'\0'):
        if not line:continue
        metadata,name=line.split(b'\t',1);name=name.decode();mode,kind,blob=metadata.decode().split();path=ROOT/name
        assert path.is_file() and not path.is_symlink(),name
        raw=PORTABLE['project'](name,path.read_bytes());current=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if current==blob:
            unchanged+=1
            if name.startswith('assets/'):asset_bytes+=len(raw)
        elif name in README_ADDITIONS:
            assert project_readme(name,raw)==git('show',BASE+':'+name),(name,'published README prefix')
            metadata_changed.append(name)
        else:
            assert name in CHANGED,name;assert sha(raw)==pins[name],name;changed.append(name)
            if name.startswith('src/'):
                before=git('show',BASE+':'+name).decode();assert project(name,raw.decode())==tokens(before),(name,'projection');token_proofs+=1
    assert set(changed)==CHANGED
    assert set(metadata_changed)==set(README_ADDITIONS)
    for name,digest in pins.items():assert sha(PORTABLE['project'](name,(ROOT/name).read_bytes()))==digest,name
    negatives=0
    for name in CHANGED:
        raw=PORTABLE['project'](name,(ROOT/name).read_bytes())
        for off in {0,len(raw)//2,len(raw)-1}:
            bad=raw[:off]+bytes([raw[off]^1])+raw[off+1:];assert sha(bad)!=pins[name];negatives+=1
    metadata_negatives=0
    for name in README_ADDITIONS:
        raw=(ROOT/name).read_bytes()
        mutations=[raw[:off]+bytes([raw[off]^1])+raw[off+1:] for off in {0,len(raw)//2,len(raw)-1}]
        mutations.extend([raw+b'\n',raw[1:],raw[:-1]])
        for bad in mutations:
            try:project_readme(name,bad)
            except AssertionError:metadata_negatives+=1
            else:raise AssertionError((name,'accepted unrelated README mutation'))
    main_source=(ROOT/'src/mainint.c').read_text();a=main_source.index('bool JE_loadScreen');b=main_source.index('ulong JE_totalScore',a);load=main_source[a:b]
    assert load.count('load_font_begin(')==1 and load.count('load_font_end();')==2
    assert re.search(r'JE_operation\(saveFileIndex \+ 1\);\s*fade_black\(15\);\s*load_font_end\(\);\s*return gameLoaded;',load)
    assert re.search(r'fade_black\(15\);\s*load_font_end\(\);\s*return false;',load)
    assert not any(x in (ROOT/'src/load_font.c').read_text() for x in ['JE_loadGame(', 'JE_saveGame(', 'gameLoaded','performSave','twoPlayerMode'])
    # Actual classic helper and load action/input/state source are the projected original.
    ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'};tree=ET.parse(ROOT/'visualc/opentyrian.vcxproj')
    files=[x.attrib['Include'] for x in tree.findall('.//m:ClCompile',ns) if 'Include' in x.attrib]
    assert len(files)==len(set(files)) and {Path(x.replace('\\','/')).name for x in files}=={x.name for x in (ROOT/'src').glob('*.c')}
    headers=[x.attrib['Include'] for x in tree.findall('.//m:ClInclude',ns) if 'Include'in x.attrib];assert headers.count('..\\src\\load_font.h')==1
    report={'result':'PASS','baseline':BASE,'portable_parent':PORTABLE['BASE'],'unchanged_prior_files':unchanged,'unchanged_asset_bytes':asset_bytes,'exact_changed_files':sorted(changed),'exact_readme_additions':sorted(metadata_changed),'readme_published_prefixes_unchanged':True,'readme_hashes':{name:README_ADDITIONS[name][0] for name in metadata_changed},'readme_mutation_rejections':metadata_negatives,'published_C_token_stream_projections':token_proofs,'pinned_source_and_test_files':len(pins),'mutation_rejections':negatives,'successful_load_release_after_original_fade':True,'input_state_save_and_original_draw_semantics_preserved':True,'windows':'C source/header inventory only, no Windows runtime claim','runtime_or_user_save_access':False}
    args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
