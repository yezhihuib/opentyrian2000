#!/usr/bin/env python3
"""Exact portable-output reversal, unchanged artwork and adversarial controls.

This is source/asset qualification only, not a game run or pixel-quality claim.
The older Load and Settings historical failures are reported separately.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess
import portable_font_projection as pf
import red250_font_projection as co


def git(*args):return subprocess.check_output(['git','-C',str(pf.ROOT),*args])
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def reject(label,fn,controls):
    try:fn()
    except AssertionError:controls.append(label)
    else:raise AssertionError(('forbidden mutation admitted',label))
def same_paths(actual,expected):assert actual==expected,sorted(actual^expected)
def same_blob(raw,expected):assert blob(raw)==expected


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path);args=parser.parse_args()
    source_delta=co.verify();records={}
    for row in git('ls-tree','-rz',pf.BASE).split(b'\0'):
        if not row:continue
        meta,name=row.split(b'\t',1);mode,kind,oid=meta.decode().split();name=name.decode()
        assert kind=='blob' and mode in ('100644','100755'),name
        records[name]=(mode,oid)
    # Check every original tracked file, not just changed C files. Asset files
    # are read in place; their bytes are never serialized into the proof data.
    count=asset_bytes=0;changes=[]
    for name,(mode,oid) in records.items():
        path=pf.ROOT/name
        assert path.is_file() and not path.is_symlink(),name
        assert ('100755' if path.stat().st_mode&0o111 else '100644')==mode,name
        raw=path.read_bytes();projected=co.project(name,raw)
        assert blob(projected)==oid,(name,'not exact immutable parent')
        count+=1
        if raw!=projected:changes.append(name)
        if name.startswith('assets/'):asset_bytes+=len(projected)
    assert set(changes)==set(pf.EDITS)|set(co.RED_EDITS)
    # The native 2x/4x composition bodies remain literal byte copies. These
    # checks inspect actual current code, before applying the inverse layer.
    native=[]
    for name,signature in [('src/title_menu_font.inc',b'static bool tm_render(const SDL_Rect *destination)'),
      ('src/settings_font.c',b'static void render(void)'),('src/settings_font.c',b'static void reduce2(void)'),
      ('src/load_font.c',b'static void render(void)'),('src/load_font.c',b'static void reduce2(void)')]:
        def body(raw):
            start=raw.index(signature);return raw[start:raw.index(b'\n}\n',start)+3]
        assert body((pf.ROOT/name).read_bytes())==body(pf.original(name)),(name,signature)
        native.append(name+':'+signature.decode())
    video=(pf.ROOT/'src/video.c').read_bytes()
    for call in ('settings_font_present','load_font_present'):
        after=(call+'(main_window_renderer,main_window_texture,src_surface,').encode()
        before=(call+'(main_window_renderer,src_surface,').encode()
        assert video.count(after)==1,call
        video=video.replace(after,before)
    assert video==pf.original('src/video.c'),'video delta exceeds two reference-texture arguments'
    controls=[]
    for top in ('src','assets'):
        expected={name for name in records if name.startswith(top+'/')} | (co.RED_ASSETS if top=='assets' else set())
        actual={str(p.relative_to(pf.ROOT)) for p in (pf.ROOT/top).rglob('*') if p.is_file() or p.is_symlink()}
        same_paths(actual,expected)
        reject(top+':unlisted-path',lambda:same_paths(actual|{top+'/unlisted-portability-control'},expected),controls)
        reject(top+':missing-path',lambda:same_paths(actual-{min(actual)},expected),controls)
    # Hash plus exact inverse hunks rejects reversion, unrelated bytes, edits
    # within every admitted hunk, truncation and a trailing undocumented byte.
    for name,pin in pf.EDITS.items():
        raw=co.outer(name,(pf.ROOT/name).read_bytes())
        for off in sorted({0,len(raw)//2,len(raw)-1}):
            bad=raw[:off]+bytes([raw[off]^1])+raw[off+1:]
            reject(name+':byte-'+str(off),lambda:pf.project(name,bad),controls)
        for label,bad in [('append',raw+b'\n'),('truncate',raw[:-1])]:
            reject(name+':'+label,lambda:pf.project(name,bad),controls)
        # Baseline is permitted only as intermediate input to project(). It
        # must not count as the new approved current file during verification.
        old=pf.original(name)
        reject(name+':current-file-reversion',lambda:pf.qualify_current(name,old),controls)
        lines=raw.splitlines(keepends=True)
        for i,edit in enumerate(pin['hunks']):
            start,end=edit['after_lines'];off=sum(map(len,lines[:start]))
            off=min(off,len(raw)-1);bad=raw[:off]+bytes([raw[off]^1])+raw[off+1:]
            reject(name+':inverse-hunk-'+str(i),lambda:pf.project(name,bad),controls)
    for name,(_,oid) in records.items():
        if name.startswith('src/') and name not in source_delta:
            raw=(pf.ROOT/name).read_bytes()
            reject(name+':unchanged-source-byte',lambda:same_blob(pf.project(name,raw+b'\n'),oid),controls)
    assets=[]
    for name,(_,oid) in records.items():
        if name.startswith('assets/hd/packs/startup-title-settings-v1/'):
            raw=(pf.ROOT/name).read_bytes();bad=raw[:-1]+bytes([raw[-1]^1])
            reject(name+':font-or-title-resource-byte',lambda:same_blob(pf.project(name,bad),oid),controls)
            assets.append(name)
    report={'result':'PASS','baseline':pf.BASE,'original_tracked_files_exact_after_reversal':count,
      'exact_portable_source_delta':sorted(n for n in pf.EDITS if n.startswith('src/')),
      'exact_combined_source_delta':sorted(source_delta),'exact_changed_existing_files':sorted(changes),
      'original_asset_bytes_exact_after_reversal':asset_bytes,'source_and_asset_path_sets_exact_with_enumerated_red_assets':True,
      'red_added_asset_paths':sorted(co.RED_ASSETS),'coexisting_red_existing_files':sorted(co.RED_EDITS),
      'negative_control_count':len(controls),'negative_controls':controls,'targeted_unchanged_resources':assets,
      'native_composition_bodies_byte_exact':native,'video_delta_exactly_two_call_arguments':True,
      'historical_pin_data_modified':False,'historical_settings_lane':'pre-existing stale src/opentyr.c pin; separate result',
      'historical_load_lane':'pre-existing stale README.md pin; separate result',
      'game_runs':False,'pixel_quality_or_native_acceptance':False,
      'windows':'Source/header inventory is tested separately; no Windows build/runtime claim'}
    if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
