#!/usr/bin/env python3
"""Focused extracted current Front Multi shadow proof, not a whole-game run.

Original bank8 input stays external. Current PNG/HDA/header are independently
checked before extraction; --changed-pins also runs one altered transport with
matching and stale generated headers in external test-only directories.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import run_sonic_quadrant_tests as base
import run_sonic_quadrant_shadow_tests as shadow


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--sanitize',action='store_true')
    parser.add_argument('--changed-pins',action='store_true')
    args=parser.parse_args();out=args.out.resolve()
    assert out!=base.ROOT and base.ROOT not in out.parents
    out.mkdir(parents=True,exist_ok=False)
    source=(base.ROOT/'src/render_mirror.c').read_text()
    shadow.verify_front_multi_rows(source)
    source_hashes,boundaries=shadow.units(out,source)
    base.IDS=tuple(i for i,_,_ in shadow.FRONT_MULTI_PINS)
    path=args.data/'tyrian.shp' if args.data.is_dir() else args.data
    normal,normal_sha=base.bank_from(path);christmas_path=path.with_name('tyrianc.shp')
    christmas,christmas_sha=base.bank_from(christmas_path) if christmas_path.exists() else (None,None)
    (out/'normal.bank8').write_bytes(normal)
    if christmas is not None:(out/'christmas.bank8').write_bytes(christmas)
    paths=[out/'normal.bank8',out/'christmas.bank8' if christmas is not None else '-']
    for i,slot,stamp in shadow.FRONT_MULTI_PINS:assert base.fnv(base.decode(normal,i))==stamp
    (out/'reference.bin').write_bytes(b''.join(base.decode(normal,i)for i in base.IDS))
    art={i:shadow.current_head_path(None,i).read_bytes()for i in base.IDS}
    pins=shadow.front_multi_payloads()
    for i,raw in art.items():assert raw[:28]==base.header(i,8) and len(raw)==43036 and base.fnv(raw[28:])==pins[i]
    full,variants,count=base.fixtures(out,art,normal)
    case=out/'front-multi-current-test.c';case.write_text('#define FRONT_MULTI_CURRENT_BATCH 1\n#include "'+str(base.ROOT/'tests/sonic_quadrant_shadow_test.c')+'"\n')
    shadow.CASE_SOURCE=case
    report=dict(status='PASS',scope='Eight current Front Multi extracted shadows only; disabled global-art/HUD collaborators; no full engine, Windows or visual acceptance',source_sha256=normal_sha,christmas_sha256=christmas_sha,production_sha256=source_hashes,unchanged_production_boundaries=boundaries,shadow_rows=45,front_multi_rows=8,resource_variants=count,runs={})
    report['runs']['optimized']=shadow.build_run(out,paths,full,variants)
    print('optimized: '+json.dumps(report['runs']['optimized']),flush=True)
    if args.sanitize:
        report['runs']['sanitized']=shadow.build_run(out,paths,full,variants,True)
        print('sanitized: '+json.dumps(report['runs']['sanitized']),flush=True)
    if args.changed_pins:
        changed=dict(art);raw=bytearray(changed[121]);raw[28+(56*96+48)*4+3]^=1;changed[121]=bytes(raw)
        header=(out/shadow.FRONT_MULTI_HEADER).read_text()
        edited_header=header.replace(f'0x{pins[121]:016x}',f'0x{base.fnv(changed[121][28:]):016x}',1)
        assert edited_header!=header
        for label,used_header in [('changed-pins',edited_header),('stale-header',header)]:
            folder=out/label;folder.mkdir()
            for name in ('types.inc','sprite-type.inc','blitters.inc','wrappers.inc','reference.bin','current_art_payload_pins.h','functions.inc'):
                shutil.copyfile(out/name,folder/name)
            (folder/shadow.FRONT_MULTI_HEADER).write_text(used_header)
            changed_full,changed_variants,_=base.fixtures(folder,changed,normal)
            report['runs'][label]=shadow.build_run(folder,paths,changed_full,changed_variants,expect_failure=label=='stale-header')
            print(label+': '+json.dumps(report['runs'][label]),flush=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: '+str(out/'report.json'),flush=True)


if __name__=='__main__':main()
