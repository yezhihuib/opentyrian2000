#!/usr/bin/env python3
"""Native actual NEWSHF observer/JE_makeEnemy harness, not whole-game or HD proof.
Private originals are SHA-checked and piped to child stdin; never persisted.
"""
import argparse
import hashlib
import json
import os
import resource
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
from global_talon_reconstruction import extract
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from check_newshf_phase_a import check, IDENTITY

def no_core():
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original-data',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--negative-control',action='store_true',help='Temporary removal of whole-bank check must be caught by native mutation test')
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    check(ROOT/'authoring-inputs/enemies/newshf-phase-a',a.original_data)
    paths=['src/newshf_identity_validation.inc','src/newshf_prototype_pins.h','src/render_mirror.c','src/render_mirror.h','src/tyrian2.c','src/sprite.c','src/episodes.h','src/varz.h','src/config.h','src/ground101_material.h','tests/newshf_identity_validation.c','tests/newshf_identity_validation.py']
    snap={n:(ROOT/n).read_bytes() for n in paths}
    bank=(a.original_data/'newshf.shp').read_bytes();raw=(a.original_data/'tyrian.hdt').read_bytes()
    pal=(a.original_data/'palette.dat').read_bytes()
    assert hashlib.sha256(pal).hexdigest()=='f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0'
    rgb=bytes((v<<2)|(v>>4) for v in pal[5*768:6*768])
    payload=bank+b''.join(raw[r['offset']:r['offset']+77] for r in IDENTITY['records'])+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big')) for n in range(0,768,3))
    with tempfile.TemporaryDirectory(prefix='newshf-identity-') as tmp:
        d=Path(tmp)
        episodes=snap['src/episodes.h'].decode();varz=snap['src/varz.h'].decode()
        rec=episodes.split('/* EnemyData */',1)[1].split('extern JE_WeaponPortType',1)[0]
        body='struct JE_SingleEnemyType'+varz.split('struct JE_SingleEnemyType',1)[1].split('typedef struct JE_SingleEnemyType JE_MultiEnemyType[100];',1)[0]+'typedef struct JE_SingleEnemyType JE_MultiEnemyType[100];\n'
        context='typedef struct {\n unsigned type,pool_slot,availability,size;\n bool score_item,damaged,independent_motion,static_animation;\n} G101EnemyContext;\n'
        assert context.strip() in snap['src/ground101_material.h'].decode()
        (d/'newshf_identity_types.h').write_text(rec+body+context)
        (d/'decode.inc').write_text(extract(snap['src/render_mirror.c'].decode(),'decode_tile'))
        for fn,operation in [('free_sprite2s','free(sprite2s->data)'),('JE_loadCompShapesB','malloc(sprite2s->size)')]:
            body_text=extract(snap['src/sprite.c'].decode(),fn)
            hook='render_mirror_newshf_validation_bank_changed(sprite2s);'
            assert body_text.count(hook)==1 and body_text.index(hook)<body_text.index(operation)
        begin=extract(snap['src/render_mirror.c'].decode(),'render_mirror_begin')
        assert begin.split('{',1)[1].lstrip().startswith('render_mirror_newshf_validation_frame();')
        if a.negative_control:
            altered=snap['src/newshf_identity_validation.inc'].decode()
            guard='&&global_bytes_hash(b->data,b->size)==NEWSHF_PROTOTYPE_BANK_FNV'
            assert altered.count(guard)==1
            (d/'newshf_identity_validation.inc').write_text(altered.replace(guard,''))

        make=extract(snap['src/tyrian2.c'].decode(),'JE_makeEnemy')
        assert make.count('render_mirror_newshf_validation_')==2
        old='\n'.join(line for line in make.splitlines() if 'render_mirror_newshf_validation_' not in line).replace('JE_makeEnemy(', 'baseline_makeEnemy(',1)
        (d/'make_enemy.inc').write_text(make+'\n'+old+'\n')
        cfg=snap['src/config.h'].decode();start=cfg.index('enum\n{\n\tDIFFICULTY_WIMP')
        (d/'difficulty.inc').write_text(cfg[start:cfg.index('};',start)+2])
        off='''#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
typedef struct SDL_Surface SDL_Surface;
typedef struct SDL_Renderer SDL_Renderer;
typedef struct SDL_Rect SDL_Rect;
typedef struct SDL_Color SDL_Color;
typedef struct G101EnemyContext G101EnemyContext;
typedef struct {size_t size;void *data;} Sprite2_array;
typedef uint8_t Uint8;
#define SPRITE_H
#define GROUND101_MATERIAL_H
#define GAMEPLAY_HUD_METERS_H
#include "render_mirror.h"
int main(void){int touched=0;
render_mirror_newshf_validation_reset(++touched);
render_mirror_newshf_validation_bank_changed(++touched);
render_mirror_newshf_validation_frame(++touched);
render_mirror_newshf_validation_allocated(++touched);
render_mirror_newshf_validation_initialized(++touched);
render_mirror_newshf_validation_observe(++touched);
if(render_mirror_newshf_validation_tile(++touched))return 2;
return touched;
}
'''
        (d/'off.c').write_text(off)
        for name,flags in [('default',[]),('flag_zero',['-DNEWSHF_IDENTITY_VALIDATION=0']),('mirror_disabled',['-DNEWSHF_IDENTITY_VALIDATION=1','-DRENDER_MIRROR_DISABLED'])]:
            exe=d/name
            subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',*flags,'-I'+str(ROOT/'src'),str(d/'off.c'),'-o',str(exe)],check=True,capture_output=True)
            subprocess.run([str(exe)],check=True)
        exe=d/'identity'
        cmd=['cc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-function','-Wno-unused-variable','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie','-I'+str(d),'-I'+str(ROOT/'src'),str(ROOT/'tests/newshf_identity_validation.c'),'-o',str(exe)]
        c=subprocess.run(cmd,text=True,capture_output=True)
        (a.out/'identity-compile.log').write_text(c.stdout+c.stderr)
        if c.returncode:print(c.stdout+c.stderr);raise SystemExit(c.returncode)
        run=subprocess.run([str(exe)],input=payload,capture_output=True,timeout=120,preexec_fn=no_core,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
        log=run.stdout.decode()+run.stderr.decode();(a.out/'identity.log').write_text(log);print(log,end='')
        unchanged=all((ROOT/n).read_bytes()==b for n,b in snap.items())
        bank_line=next(i for i,line in enumerate(snap['tests/newshf_identity_validation.c'].decode().splitlines(),1) if 'for(unsigned b=0;b<NEWSHF_PROTOTYPE_BANK_BYTES' in line)
        expected_failure=f'newshf_identity_validation.c:{bank_line}: !newshf_validation_slots[0].role'
        accepted=(run.returncode!=0 and expected_failure in run.stderr.decode() and 'NEGATIVE-CONTROL bank-byte mutation' in run.stderr.decode() and 'CHECK failed' in run.stderr.decode() and 'AddressSanitizer' not in run.stderr.decode() and 'runtime error:' not in run.stderr.decode()) if a.negative_control else run.returncode==0
        receipt={'status':'PASS' if accepted and unchanged else 'FAIL','negative_control':a.negative_control,'scope':'Actual identity include, production structs/decode_tile/JE_makeEnemy with bounded SDL/RNG shim; not whole-game or HD rendering acceptance','returncode':run.returncode,'source_unchanged':unchanged,'source_sha256':{n:hashlib.sha256(b).hexdigest() for n,b in snap.items()},'private_original_bytes_persisted':False,'feature_off_modes':['default','flag_zero','mirror_disabled'],'sanitizers':'ASan+UBSan','leak_detection':'disabled: LeakSanitizer unsupported under container ptrace','stdout':run.stdout.decode(),'stderr':run.stderr.decode()}
        (a.out/'identity-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        raise SystemExit(0 if receipt['status']=='PASS' else 1)
if __name__=='__main__':main()
