#!/usr/bin/env python3
"""Sanitize the production green identity observer with exact runtime types.
Original records are read into memory and sent over stdin, never emitted.
"""
import argparse,json,pathlib,subprocess,os

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--original-data',required=True,type=pathlib.Path);p.add_argument('--out',required=True,type=pathlib.Path)
 a=p.parse_args();root=pathlib.Path(__file__).resolve().parents[1];a.out.mkdir(parents=True,exist_ok=True)
 ep=(root/'src/episodes.h').read_text();sh=(root/'src/shots.h').read_text()
 rec='typedef struct'+ep.split('typedef struct',1)[1].split('} JE_WeaponType;',1)[0]+'} JE_WeaponType;\n'
 shot='typedef struct'+sh.split('typedef struct',1)[1].split('} PlayerShotDataType;',1)[0]+'} PlayerShotDataType;\n'
 (a.out/'green_identity_types.h').write_text(rec+shot)
 registry=json.loads((root/'assets/hd/global-assets-v1/registry.json').read_text())
 fam=next(x for x in registry['families'] if 'green' in x['name'].lower())
 raw=(a.original_data/'tyrian.hdt').read_bytes()
 data=b''.join(raw[r['variants'][0]['offset']:r['variants'][0]['offset']+80] for r in fam['source_identity']['weapon_records'])
 exe=a.out/'identity'
 subprocess.run(['cc','-std=c99','-g','-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(a.out),str(root/'tests/global_green_identity.c'),'-o',str(exe)],check=True)
 r=subprocess.run([str(exe)],input=data,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'))
 (a.out/'identity.log').write_bytes(r.stdout);print(r.stdout.decode(),end='');r.check_returncode()
if __name__=='__main__':main()
