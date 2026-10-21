#!/usr/bin/env python3
"""Compile the real identity helper against current production struct definitions.
Original record bytes only pass through stdin, never into generated artifacts.
"""
import argparse
import pathlib
import subprocess
import os

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original-data',required=True,type=pathlib.Path)
    p.add_argument('--out',required=True,type=pathlib.Path)
    a=p.parse_args();root=pathlib.Path(__file__).resolve().parents[1]
    a.out.mkdir(parents=True,exist_ok=True)
    episodes=(root/'src/episodes.h').read_text();varz=(root/'src/varz.h').read_text();ctx=(root/'src/ground101_material.h').read_text()
    rec=episodes.split('/* EnemyData */',1)[1].split('extern JE_WeaponPortType',1)[0]
    body='struct JE_SingleEnemyType'+varz.split('struct JE_SingleEnemyType',1)[1].split('typedef struct JE_SingleEnemyType JE_MultiEnemyType[100];',1)[0]+'typedef struct JE_SingleEnemyType JE_MultiEnemyType[100];\n'
    context='typedef struct {\n unsigned type,pool_slot,availability,size;\n bool score_item,damaged,independent_motion,static_animation;\n} G101EnemyContext;\n'
    assert context.strip() in ctx
    (a.out/'cash25_identity_types.h').write_text(rec+body+context)
    data=(a.original_data/'tyrian.hdt').read_bytes()[164015+391*77:164015+396*77]
    exe=a.out/'identity'
    cmd=['cc','-std=c99','-g','-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(a.out),str(root/'tests/global_cash25_identity.c'),'-o',str(exe)]
    subprocess.run(cmd,check=True)
    r=subprocess.run([str(exe)],input=data,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=0"),check=True)
    (a.out/'identity.log').write_bytes(r.stdout);print(r.stdout.decode(),end='')
if __name__=='__main__':main()
