#!/usr/bin/env python3
"""Pinned, portable Sonic73 extracted production tests. Never launches the game.

Original data and the source contract are caller-provided, private inputs. All
materialized original-data fixtures and compiler outputs stay outside Git.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = '1f5ab7398a6e0ed369644b50ffdf16bacdb7202d'
IDS = [73]
SHA = lambda b: hashlib.sha256(b).hexdigest()
RUN_COMMANDS = []


def extract(source, name):
    m = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert m, name
    end = source.index('{', m.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[m.start():end] + '\n'


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def source_scope(source):
    original = git('show', BASE + ':src/render_mirror.c').decode()
    # The exact scoped inverse is deliberately pinned to the candidate additions.
    helper = extract(source, 'sonic_upward_arch_source_matches')
    changes = [
        ('static Asset assets[549];', 'static Asset assets[548];'),
        ('/* Sonic Wave ID73: one normal upward arch; other identities stay independent.\n'
         ' * Validate current selected indices AND coverage before EVERY cold/warm lookup. */\n' + helper + '\n', ''),
        (' /* Sonic Wave ID73 only; original/Christmas/diagnostic fallbacks stay classic. */\n'
         ' if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index==73) {\n'
         '  if((game_probe_density!=4&&game_probe_density!=8)||game_probe_missing||game_probe_invalid||\n'
         '     game_probe_original_reference||!game_probe_assets||!sonic_upward_arch_source_matches(bank))return NULL;\n'
         '  slot=548;role=8;\n }\n', ''),
        (' /* Sonic Wave ID73 retains its original indexed shadow silhouette, origin and order. */\n'
         ' if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index==73&&style==MIRROR_SHADOW)return false;\n', ''),
    ]
    restored = source
    for before, after in changes:
        assert restored.count(before) == 1, 'Missing or ambiguous production inverse: ' + before[:100]
        restored = restored.replace(before, after)
    assert restored == original, 'Unexpected renderer change'
    names = git('ls-tree', '-r', '--name-only', BASE, '--', 'src').decode().splitlines()
    assert {str(p.relative_to(ROOT)) for p in (ROOT / 'src').rglob('*') if p.is_file()} == set(names)
    for name in names:
        if name != 'src/render_mirror.c':
            assert (ROOT / name).read_bytes() == git('show', BASE + ':' + name), name
    prior_tests = git('ls-tree','-r','--name-only',BASE,'--','prototype/test-sonic-six-pair-binding.py','prototype/test-sonic-six-pair-binding.c','prototype/test-sonic-six-pair-shots.c','prototype/test-sonic-six-pair-scope.py').decode().splitlines()
    for name in prior_tests:
        assert (ROOT/name).read_bytes() == git('show', BASE + ':' + name), name
    return original, {'baseline': BASE, 'exact_renderer_inverse': True,
                      'production_source_files_checked': len(names),
                      'prior_sonic6_44_tests_unchanged': prior_tests,
                      'only_changed_production_file': 'src/render_mirror.c',
                      'candidate_renderer_sha256': SHA(source.encode()),
                      'gameplay_input_shots_blitters_rng_unchanged': True}


def decode(bank, index):
    pos = struct.unpack_from('<H', bank, 2 * (index - 1))[0]
    cell, colors, coverage = 0, bytearray(168), bytearray(168)
    for _ in range(len(bank)):
        code = bank[pos]
        pos += 1
        if code == 15:
            return bytes(colors + coverage)
        cell += code & 15
        for _ in range(code >> 4):
            assert 0 <= cell < 168 and not coverage[cell]
            colors[cell], coverage[cell] = bank[pos], 255
            pos += 1
            cell += 1
    raise AssertionError('unterminated original RLE')


def bank_from(path, pin=None):
    raw = path.read_bytes()
    if pin:
        assert SHA(raw) == pin, path
    count = struct.unpack_from('<H', raw)[0]
    positions = list(struct.unpack_from('<' + str(count) + 'I', raw, 2)) + [len(raw)]
    assert count >= 8 and positions == sorted(positions)
    return raw[positions[7]:positions[8]], SHA(raw)


def header(index, density=8):
    return struct.pack('<4s6I', b'HDR1', 80000 + index, density, 12, 14, 0, 0)


def reduced(raw, index):
    rgba = raw[28:]
    return header(index, 4) + b''.join(rgba[(y*2*96+x*2)*4:(y*2*96+x*2)*4+4]
                                     for y in range(56) for x in range(48))


def mutate(raw, index, kind):
    raw = bytearray(raw)
    fields = {'role': (4, 1110000+index), 'identity': (4, 80044),
              'density': (8, 4), 'width': (12, 11), 'height': (16, 13),
              'anchor-x': (20, 1), 'anchor-y': (24, 1)}
    if kind in fields:
        struct.pack_into('<I', raw, *fields[kind])
    if kind == 'magic': raw[:4] = b'BAD!'
    if kind == 'short-header': raw = raw[:27]
    if kind == 'truncated': raw = raw[:-1]
    if kind == 'extra': raw += b'X'
    return bytes(raw)


def prepare_variants(work, art):
    raw8 = art[73]
    raw4 = reduced(raw8, 73)
    rows = []
    def add(name, a=None, b=None, valid8=False, valid4=False):
        folder = work / name
        folder.mkdir()
        if a is not None: (folder / 'bullet-73-8.hda').write_bytes(a)
        if b is not None: (folder / 'bullet-73-4.hda').write_bytes(b)
        rows.append([name, int(valid8 or valid4), 8 if valid8 else 4, int(valid4), 4])
    add('valid', a=raw8, valid8=True)
    add('both', a=raw8, b=raw4, valid8=True, valid4=True)
    add('missing')
    add('only4', b=raw4, valid4=True)
    for kind in ['magic', 'role', 'identity', 'density', 'width', 'height', 'anchor-x', 'anchor-y', 'short-header', 'truncated', 'extra']:
        bad8 = mutate(raw8, 73, kind)
        bad4 = mutate(raw4, 73, kind) if kind != 'density' else raw4[:8] + struct.pack('<I', 8) + raw4[12:]
        add(kind+'-8', a=bad8)
        add(kind+'-8-valid4', a=bad8, b=raw4, valid4=True)
        add(kind+'-4', b=bad4)
        add(kind+'-8-and4', a=bad8, b=bad4)
        add('valid8-'+kind+'-4', a=raw8, b=bad4, valid8=True)
    (work / 'variants.tsv').write_text(''.join(' '.join(map(str, r)) + '\n' for r in rows))
    return rows


def source_rows(contract, data, out):
    raw = data.read_bytes()
    assert SHA(raw) == contract['data_sha256']['tyrian.hdt']
    fields = ['drain','shotrepeat','multi','weapani','max','tx','ty','aim','attack','del','sx','sy','bx','by','sg','acceleration','accelerationx','circlesize','sound','trail','shipblastfilter']
    tokens = 'H B B H B B B B 8B 8B 8b 8b 8b 8b 8H b b B B B B'.split()
    fmt = {'u8':'B','s8':'b','u16':'H','s16':'h'}
    reader = (ROOT / 'src/episodes.c').read_text()
    schema = [(n, (count if count != '1' else '') + fmt[t]) for t,n,count in re.findall(r'fread_(u8|s8|u16|s16)_die\(\s*&?weapons\[i\]\.(\w+),\s*(\d+),\s*f\)', reader)]
    assert schema == list(zip(fields,tokens))
    pos = struct.unpack_from('<i', raw)[0] + 14
    records = {}
    for rid in list(range(819)) + list(range(1000,1819)):
        start, rec = pos, {}
        for field, token in zip(fields, tokens):
            values = list(struct.unpack_from('<'+token, raw, pos))
            pos += struct.calcsize('<'+token)
            rec[field] = values if len(values)>1 else values[0]
        if 276 <= rid <= 297: records[rid] = (rec, start, raw[start:pos])
    assert [(r['mode'],r['power'],r['shot_record']) for r in contract['power_mode_rows']] == [(1,p,275+p) for p in range(1,12)]+[(2,p,286+p) for p in range(1,12)]
    port=raw[pos+11*82:pos+12*82]
    assert port[1:1+min(port[0],30)].decode('ascii').rstrip()=='Sonic Wave' and port[31]==2
    assert list(struct.unpack_from('<11H',port,32))==list(range(276,287)) and list(struct.unpack_from('<11H',port,54))==list(range(287,298))
    assert struct.unpack_from('<H',port,76)[0]==950 and struct.unpack_from('<H',port,80)[0]==50
    rows, initializers = [], []
    def cval(v): return '{'+','.join(map(str,v))+'}' if isinstance(v,list) else str(v)
    for row in contract['power_mode_rows']:
        rid = row['shot_record'];rec,start,record_raw = records[rid]
        assert rec == row['full_original_record']
        assert start == row['record_span']['offset'] and SHA(record_raw) == row['record_span']['sha256']
        frame_ids = sorted(set(rec['sg'][:rec['max']]))
        assert frame_ids == row['frame_ids'] and all(rec['del'][n] in (98,100) for n in range(rec['max']))
        assert (73 in frame_ids) == ((row['mode'],row['power']) in {(1,8),(1,9),(1,10),(2,1),(2,2),(2,5),(2,7),(2,9)})
        rows.append({'mode':row['mode'],'power':row['power'],'record':rid,'ids':frame_ids})
        initializers.append(f' [{rid}]={{'+','.join('.'+f+'='+cval(rec[f]) for f in fields)+'},')
    family = sorted({i for r in rows for i in r['ids']})
    assert set(family) == set(map(int, contract['frames'])) and len(family) == 21
    unchanged = sorted(set(family) - {6,44,73})
    assert len(unchanged) == 18
    shot_source = (ROOT/'src/shots.c').read_text()
    funcs = {n:extract(shot_source,n) for n in ['player_shot_create','player_shot_move_and_draw']}
    original_shots = git('show', BASE+':src/shots.c').decode().replace('\r\n','\n')
    assert all(text == extract(original_shots,n) for n,text in funcs.items())
    assert not re.search(r'\b(?:rand|random|mt_rand|mt_rand_1)\s*\(', ''.join(funcs.values()))
    (out/'shot-functions.inc').write_text(''.join(funcs.values()))
    shot_type = re.search(r'typedef struct \{.*?\} PlayerShotDataType;', (ROOT/'src/shots.h').read_text(), re.S).group()
    weapon_type = re.search(r'typedef struct\s*\{.*?\} JE_WeaponType;', (ROOT/'src/episodes.h').read_text(), re.S).group()
    (out/'shot-types.inc').write_text(shot_type+'\n'+weapon_type+'\n')
    (out/'weapon-records.inc').write_text('static const JE_WeaponType weapons[WEAP_NUM+1]={\n'+'\n'.join(initializers)+'\n};\n')
    return {'normal_first_level_rows': rows, 'pilot_reuse_rows': [r for r in rows if 73 in r['ids']],
            'all_22_rows_verified': True, 'all_other_14_rows_exclude_id73': True, 'family_ids':family, 'other_18_ids_unchanged':unchanged, 'exact_original_shot_functions_and_no_rng_calls':True,'original_port11_mapping_cost950_power50_verified':True,
            'shot_function_sha256': {n:SHA(s.encode()) for n,s in funcs.items()}}


def run(cmd, log, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    RUN_COMMANDS.append({'argv':list(map(str,cmd)),'log':str(log),'returncode':result.returncode})
    log.write_text(result.stdout+result.stderr)
    if result.returncode:
        print(result.stdout+result.stderr)
        result.check_returncode()
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['data','contract','out']: p.add_argument('--'+name,type=Path,required=True)
    args = p.parse_args();out = args.out.resolve()
    assert not out.exists() and ROOT != out and ROOT not in out.parents
    source = (ROOT/'src/render_mirror.c').read_text()
    baseline, scope = source_scope(source)
    contract = json.loads(args.contract.read_text())
    banks, data_pins = [], {}
    for fn in ['tyrian.shp','tyrianc.shp']:
        bank,pin = bank_from(args.data/fn, contract['data_sha256'].get(fn, 'e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d'))
        banks.append(bank);data_pins[fn] = pin
    for i in IDS:
        decoded = decode(banks[0],i)
        assert SHA(decoded[:168]) == contract['frames'][str(i)]['decoded_indices_sha256']
        assert SHA(decoded[168:]) == contract['frames'][str(i)]['decoded_coverage_sha256']
    source_facts = {}
    for label,bank in zip(['normal','christmas'], banks):
        value=decode(bank,73); start=struct.unpack_from('<H',bank,144)[0];end=start
        while bank[end] != 15: end += 1+(bank[end]>>4)
        end += 1
        stamp=0xcbf29ce484222325
        for byte in value: stamp=((stamp^byte)*0x100000001b3)&0xffffffffffffffff
        source_facts[label]={'bank_bytes':len(bank),'encoded_offset':start,'encoded_bytes':end-start,'encoded_sha256':SHA(bank[start:end]),'decoded_indices_sha256':SHA(value[:168]),'decoded_coverage_sha256':SHA(value[168:]),'decoded_index_then_coverage_sha256':SHA(value),'fnv1a64':hex(stamp),'occupied_cells':sum(bool(v) for v in value[168:])}
    assert source_facts['normal']['fnv1a64']=='0x898413e19195c1be'
    assert source_facts['christmas']['fnv1a64']=='0x65261a1e407d7a98'
    assert decode(banks[0],73) != decode(banks[1],73)
    art = {i:(ROOT/f'assets/hd/artwork/player-sonic-upward-arch-v1/output/bullet-{i}-8.hda').read_bytes() for i in IDS}
    art_contract=json.loads((ROOT/'assets/hd/artwork/player-sonic-upward-arch-v1/contract.json').read_text())
    art_entries={e['id']:e for e in art_contract['entries']}
    assert set(art_entries)==set(IDS)
    for i,raw in art.items(): assert raw[:28] == header(i) and len(raw) == 43036 and SHA(raw)==art_entries[i]['HDA_sha256']
    manifest = json.loads((ROOT/'assets/hd/manifest.json').read_text())
    packs = {}
    for kind in ['preview','debug']:
        name = manifest['default_'+kind+'_pack'];packs[kind] = name
        for i in IDS:
            filename=f'bullet-{i}-8.hda'
            assert (ROOT/'assets/hd/packs'/name/filename).read_bytes() == art[i]
            assert manifest['packs'][name]['files'][filename]['sha256'] == SHA(art[i])
    out.mkdir(parents=True)
    for fn,bank in zip(['normal.bank8','christmas.bank8'],banks): (out/fn).write_bytes(bank)
    reference=b''.join(decode(b,i) for b in banks for i in IDS);(out/'reference.bin').write_bytes(reference)
    work=out/'fixtures';work.mkdir();variants=prepare_variants(work,art)
    previous_art = {}
    previous_contract=json.loads((ROOT/'assets/hd/artwork/player-sonic-six-pair-v1/contract.json').read_text())
    previous_entries={e['id']:e for e in previous_contract['entries']}
    for i in [6,44]:
        name=f'bullet-{i}-8.hda'; path='assets/hd/artwork/player-sonic-six-pair-v1/output/'+name
        value=(ROOT/path).read_bytes()
        assert value==git('show',BASE+':'+path) and SHA(value)==previous_entries[i]['HDA_sha256']
        for pack in packs.values(): assert (ROOT/'assets/hd/packs'/pack/name).read_bytes()==value
        (work/'valid'/name).write_bytes(value);previous_art[str(i)]=SHA(value)
    rows=source_rows(contract,args.data/'tyrian.hdt',out)
    sprite_type=re.search(r'typedef struct\s*\{\s*size_t size;\s*Uint8 \*data;\s*\}\s*Sprite2_array;', (ROOT/'src/sprite.h').read_text()).group()
    names=['decode_tile','read_asset','explosion_asset_slot','mint27_source_matches','get_asset','render_mirror_entity']
    patterns=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'static Asset assets\[\d+\];',r'enum \{ ASSET_NEWSH2=.*?\};']
    blits={n:extract((ROOT/'src/sprite.c').read_text(),n) for n in ['blit_sprite2','blit_sprite2_darken']}
    wrapper=extract((ROOT/'src/entity_draw.c').read_text(),'draw_entity_sprite2')
    builds={}
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    for label,rs in [('baseline',baseline),('candidate',source)]:
        folder=out/label;folder.mkdir();(folder/'sprite-type.inc').write_text(sprite_type)
        helpers={n:extract(rs,n) for n in names+['sonic_six_pair_member','sonic_six_pair_source_matches']+(['sonic_upward_arch_source_matches'] if label=='candidate' else [])}
        (folder/'types.inc').write_text('\n'.join(re.search(pattern,rs,re.S).group() for pattern in patterns))
        (folder/'functions.inc').write_text('\n'.join(s[:s.index('{')].strip()+';' for s in helpers.values())+'\n'+''.join(helpers.values()))
        (folder/'blitters.inc').write_text(''.join(s.replace('void '+n+'(', 'void production_'+n+'(',1) for n,s in blits.items()))
        (folder/'wrappers.inc').write_text(wrapper)
        builds[label]={'function_sha256':{n:SHA(s.encode()) for n,s in {**helpers,**blits,'draw_entity_sprite2':wrapper}.items()},'runs':{}}
        for name,flags in [('optimized',['-O2']),('sanitized',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
            cmd=[os.environ.get('CC','cc'),'-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',*flags,'-DBASELINE='+str(int(label=='baseline')),'-I'+str(folder),str(Path(__file__).with_suffix('.c')),'-o',str(folder/name)]
            run(cmd,folder/(name+'-compile.log'))
            result=run([str(folder/name),str(out/'normal.bank8'),str(out/'christmas.bank8'),str(work),str(out/'reference.bin')],folder/(name+'.log'),env=env,timeout=180)
            builds[label]['runs'][name]=json.loads(result.stdout);print(label+'/'+name+': '+result.stdout.strip(),flush=True)
    shot_runs={}
    for name,flags in [('optimized',['-O2']),('sanitized',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
        binary=out/('shots-'+name)
        cmd=[os.environ.get('CC','cc'),'-std=c99','-Wall','-Wextra','-Werror',*flags,'-I'+str(out),str(ROOT/'prototype/test-sonic-upward-arch-shots.c'),'-o',str(binary)]
        run(cmd,out/('shots-'+name+'-compile.log'))
        result=run([str(binary)],out/('shots-'+name+'.log'),env=env,timeout=180)
        shot_runs[name]=json.loads(result.stdout);print('shots/'+name+': '+result.stdout.strip(),flush=True)
    report={'status':'PASS','commands':RUN_COMMANDS,'test_file_sha256':{name:SHA((ROOT/'prototype'/name).read_bytes()) for name in ['test-sonic-upward-arch-binding.py','test-sonic-upward-arch-binding.c','test-sonic-upward-arch-shots.c']},'source_contract_sha256':SHA(args.contract.read_bytes()),'art_contract_sha256':SHA((ROOT/'assets/hd/artwork/player-sonic-upward-arch-v1/contract.json').read_bytes()),'previous_6_44_art_sha256':previous_art,'scope':scope,'art_sha256':{str(i):SHA(v) for i,v in art.items()},'default_packs':packs,'data_sha256':data_pins,'id73_source_facts':source_facts,'source_rows':rows,'shot_runs':shot_runs,'actual_christmas_selected_decoded_sources_equal_normal':all(decode(banks[0],i)==decode(banks[1],i) for i in IDS),'resource_variants':variants,'builds':builds,'game_runs':0,
            'limitations':['Focused extracted production source, loader, guard, wrapper and original RLE tests; RGBA head compositor is a metadata-checking stub.','Generic compositor integration, actual-play aesthetics, natural acquisition and full-engine runtime require separate acceptance.','LeakSanitizer disabled for executor compatibility; AddressSanitizer and UndefinedBehaviorSanitizer enabled.','Malformed original source is exercised at the HD guard only; original unchecked RLE is never executed against malformed data.']}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__': main()
