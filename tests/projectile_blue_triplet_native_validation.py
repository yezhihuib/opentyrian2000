#!/usr/bin/env python3
"""Pure source/input/fixture/schema helpers for the selected final blue epoch.

No compiler, subprocess, native process, old object/ELF or historical build
lookup lives here. Use projectile_blue_triplet_fresh_native_validation.py for
new qualification. Historical partial production-TU drivers remain immutable
in their evidence stages. Original264 source/stdin/stdout stay byte-exact;
new365 expectations select101V6+120V4+original139, not retroactive acceptance.
"""
from pathlib import Path
import ast,hashlib,re,struct
SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXPECTED_NEW_CASES=365
SELECTORS=(91,145,61,101,120,139)
BLUE=(101,120,139)
SAN=('-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie')
PRIOR61_DRIVER_SHA='68737e976c12cfa66eaf86c536cccd2ed2dc2a39e7a81740ecbd731d48699dc8'
COMPANION_SHA='5f80d681e84a6dff20873f7f05bb3a02e3fd0f22013edf2b5fbf133d36c51cfe'
LEGACY_SHA='8925fb11215446339f067124fa7223ec48dc7c86459e303d3803477773b2d9ac'
OLD91_HARNESS_SHA='4edcb186f10a47b8d331b6ecaefe15f12c620d7967145f5f9cdbf93c0e76ce89'
WRAPPER_SHA='59bfbe4d8e3bb8db4403eaabb199d8ff2f09b2eb2047769f39069c93dff7f4eb'
OLD_STDIN_SHA='7dedf7066696fc278f5fbb8dfb1462e7b6ac290cb5d08ae5260a6cdabc1ecca7'
NEW_STDIN_SHA='a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b'
DATA_SHA={'tyrian.shp': '80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0', 'tyrianc.shp': 'e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d', 'palette.dat': 'f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0'}
PACKS=(('valid', (), None), ('missing91', (91,), None), ('missing145', (145,), None), ('bad145', (), 145), ('bad91', (), 91), ('missing61', (61,), None), ('bad61', (), 61), ('only61', (91, 145), None))
PACK_NAMES=('valid', 'missing91', 'bad91', 'missing145', 'bad145', 'missing61', 'bad61', 'missing101', 'bad101', 'missing120', 'bad120', 'missing139', 'bad139', 'only101', 'only120', 'only139', 'old-only', 'header101', 'short101', 'trailing101', 'header120', 'short120', 'trailing120', 'header139', 'short139', 'trailing139')
SHIM='#include "accepted_projectile61_native_additions.c.inc"\n#define main inherited61_dispatch\n'
OUTER='#include "accepted61_wrapper.c"\n#undef main\n#include "projectile_blue_triplet_native_additions.c.inc"\nint main(int argc,char **argv)\n{\n if(argc>=2&&!strcmp(argv[1],"--blue-triplet"))return blue_triplet_main(argc,argv);\n return inherited61_dispatch(argc,argv);\n}\n'
BLUE_COMPANION_SHA='cf38a2c8582bf9c3299a84721d37dae83402b938c859a2489ad382844a9a6084'
LEGACY107_STDOUT='PASS inherited91 native lifecycle: 37 cases 81611 assertions\n145_TO_TALON copied=376 cached=0\n145_TO_TALON copied=376 cached=1\nPASS shared145 native lifecycle: 70 new cases 141992 new assertions; internal8 only; not gameplay/full build\n'
LEGACY61_STDOUT='61_TO_TALON copied=267 cached=0\n61_TO_TALON copied=267 cached=1\nPASS shared61 native lifecycle: 157 cases 822291 assertions; internal8 only; not gameplay/full build\n'
TRANSFER_PINS={101:(1756,1721),120:(1864,1864),139:(1481,1454)}
HDA_SHA={91:'2940279a66281c16838d4e070421a581ea0e4b5bb91cf85a1cbc532902933e4c',145:'e4863397d4d7e9874e96e642ce6596c90e99009014b746491016c0423e099c83',61:'3530c27302a2cb3d26830711cd4b94a01aacbfad748c91aea219bbc81b0c5c29',101:'4f1cb932fa0418f3236d8240a3012ec19d65ab3d33a862190a75f53302db8ac6',120:'e8935de840d09ed83e65206664ba3a4ddf25b11764ba2b6038ac752140dcb83b',139:'47a6941988a2e2a4835859dfc1cf12f2481b2bf29bab18be94307b408cf34942'}
HDA_ID={91:1490091,145:1500145,61:1510061,101:1520101,120:1520120,139:1520139}
HDA_NAMES={i:(f'enemy-projectile{i}-{i}-8.hda' if i in (91,145,61) else f'enemy-projectile-blue-triplet-{i}-8.hda') for i in SELECTORS}

def literal_assignment(path,name):
    tree=ast.parse(path.read_text())
    nodes=[node for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets)]
    assert len(nodes)==1
    return ast.literal_eval(nodes[0].value)

def legacy_harness(root):
    old=literal_assignment(root/'tests/test_projectile91_global_runtime.py','HARNESS')
    assert hashlib.sha256(old.encode()).hexdigest()==OLD91_HARNESS_SHA
    marker='int main(int argc,char **argv)\n{';assert old.count(marker)==1
    result=old.split(marker)[0].encode()+(root/'tests/projectile145_native_additions.c.inc').read_bytes()
    assert hashlib.sha256(result).hexdigest()==LEGACY_SHA
    return result

def accepted_wrapper(path):
    assert SHA(path)==PRIOR61_DRIVER_SHA
    raw=literal_assignment(path,'WRAPPER').encode()
    assert hashlib.sha256(raw).hexdigest()==WRAPPER_SHA
    return raw

def native_inputs(data):
    assert all(SHA(data/name)==pin for name,pin in DATA_SHA.items())
    raw=(data/'tyrian.shp').read_bytes();assert struct.unpack_from('<H',raw)[0]==13
    offsets=struct.unpack_from('<13I',raw,2);bank=raw[offsets[7]:offsets[8]];talon=raw[offsets[8]:offsets[9]]
    assert len(bank)==32060 and hashlib.sha256(bank).hexdigest()=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
    pal=(data/'palette.dat').read_bytes()[:768];assert len(pal)==768 and max(pal)<64
    rgb=bytes((v<<2)|(v>>4) for v in pal)
    old=bank+b''.join(struct.pack('<I',int.from_bytes(rgb[i:i+3],'big')) for i in range(0,768,3))+struct.pack('<I',len(talon))+talon
    raw=(data/'tyrianc.shp').read_bytes();assert struct.unpack_from('<H',raw)[0]==13
    offsets=struct.unpack_from('<13I',raw,2);xmas=raw[offsets[7]:offsets[8]]
    assert len(xmas)==32404 and hashlib.sha256(xmas).hexdigest()=='26eb4fe91672bcef4bc88d7162d5f531144ad98eba64f5c0314e35fec85241e4'
    new=old+struct.pack('<I',len(xmas))+xmas
    assert hashlib.sha256(old).hexdigest()==OLD_STDIN_SHA and hashlib.sha256(new).hexdigest()==NEW_STDIN_SHA
    return old,new

def fixture_bytes(raw,selector,leaf):
 assert type(selector) is int and selector in SELECTORS and leaf in PACK_NAMES
 if leaf=='old-only' and selector in BLUE:return None
 if leaf.startswith('only') and selector!=int(leaf[4:]):return None
 if leaf=='missing'+str(selector):return None
 b=bytearray(raw)
 if leaf=='bad'+str(selector):b[28+100]^=1
 if leaf=='header'+str(selector):b[4]^=1
 if leaf=='short'+str(selector):b=b[:-1]
 if leaf=='trailing'+str(selector):b+=b'!'
 return bytes(b)

def harness_sources(root,companion_bytes=None):
    """Return six source byte strings, never write or consult prior builds."""
    root=Path(root)
    inherited=legacy_harness(root)
    wrapper=accepted_wrapper(root/'tests/projectile61_native_validation.py')
    companion=(root/'tests/projectile61_native_additions.c.inc').read_bytes()
    assert hashlib.sha256(companion).hexdigest()==COMPANION_SHA
    if companion_bytes is None:companion_bytes=Path(__file__).with_name('projectile_blue_triplet_native_additions.c.inc').read_bytes()
    assert isinstance(companion_bytes,bytes) and hashlib.sha256(companion_bytes).hexdigest()==BLUE_COMPANION_SHA
    return {'inherited145_harness.c':inherited,'accepted_projectile61_native_additions.c.inc':companion,
            'accepted61_wrapper.c':wrapper,'projectile61_native_additions.c.inc':SHIM.encode(),
            'projectile_blue_triplet_native_additions.c.inc':companion_bytes,'harness.c':OUTER.encode()}


def verify_legacy_stdout(old,new):
    assert old==LEGACY107_STDOUT and new==LEGACY61_STDOUT,'Original264 stdout must remain byte-exact'
    return {'inherited_cases':107,'inherited_assertions':223603,'new_cases':157,'new_assertions':822291,'total_cases':264,'total_assertions':1045894}


def fixture_payloads(hdas):
    """Return relative file->bytes; caller creates pack content links/monitors writes.

    Keys comprise legacy264/{eight PACKS}/{HDA_NAMES} and
    blue-packs/{26 PACK_NAMES}/{HDA_NAMES}. No filesystem effects.
    """
    assert isinstance(hdas,dict) and set(hdas)==set(SELECTORS)
    for i,raw in hdas.items():
        assert type(i) is int and isinstance(raw,bytes) and len(raw)==43036
        assert hashlib.sha256(raw).hexdigest()==HDA_SHA[i]
        assert raw[:28]==struct.pack('<4s6I',b'HDR1',HDA_ID[i],8,12,14,0,0)
    result={}
    for name,missing,bad in PACKS:
        for i in (91,145,61):
            if i in missing:continue
            raw=bytearray(hdas[i])
            if i==bad:raw[128]^=1
            result[f'legacy264/{name}/{HDA_NAMES[i]}']=bytes(raw)
    for name in PACK_NAMES:
        for i in SELECTORS:
            raw=fixture_bytes(hdas[i],i,name)
            if raw is not None:result[f'blue-packs/{name}/{HDA_NAMES[i]}']=raw
    assert len(result)==151 and all(not Path(k).is_absolute() and '..' not in Path(k).parts for k in result)
    return result


def parse_blue_stdout(stdout):
    lines=stdout.splitlines()
    native=[f'BLUE101_ZERO_NATIVE pattern={p} draw=384 finish=384 cache=384' for p in (0,1)]
    hd='BLUE101_ZERO_HD prior=120 draw=384 finish=384 cache=384'
    assert len(lines)==10 and lines[:2]==native and lines[2]==hd,'Missing/duplicate/wrong384-underlay proof'
    observed=[]
    for i in BLUE:
        for cached in (0,1):
            line=lines[3+len(observed)];copied,soft=TRANSFER_PINS[i]
            assert line==f'BLUE_TO_TALON selector={i} copied={copied} soft={soft} cached={cached}'
            observed.append([str(i),str(copied),str(soft),str(cached)])
    match=re.fullmatch(r'PASS blue triplet native lifecycle: (\d+) cases (\d+) assertions; internal8 only; not gameplay/full build',lines[-1])
    assert match and int(match[1])==EXPECTED_NEW_CASES and int(match[2])>0
    return {'new_cases':int(match[1]),'new_assertions':int(match[2]),'actual_transfer_rows':observed,
            'native_zero_rows':native,'hd_zero_rows':[hd],'zero_samples_each_phase':384,
            'coverage_epoch':'101V6+120V4+139original'}


if __name__=='__main__':
    raise SystemExit('Input/schema helper only. Run projectile_blue_triplet_fresh_native_validation.py for a new authorized fresh qualification.')
