#!/usr/bin/env python3
"""Pinned, portable Sonic143/144 extracted production tests. Never launches the game.

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
BASE = 'cb06b76ba45bb78afa4b50338472c6b160d9f358'
IDS = [143, 144]
FAMILY = [6,16,44,54,63,73,82,105,106,124,125,130,131,143,144,149,150,223,224,242,243]
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
    original=git('show',BASE+':src/render_mirror.c').decode()
    changes=[('static Asset assets[561];', 'static Asset assets[563];'), ('/* Sonic Wave inverted corner pair149/150:', '/* Sonic Wave joined wave pair143/144: two normal single-player heads only.\n * Validate current selected indices AND coverage before EVERY cold/warm lookup. */\nstatic int sonic_joined_wave_pair_member(unsigned int index)\n{\n return index==143?0:index==144?1:-1;\n}\n\nstatic bool sonic_joined_wave_pair_source_matches(Sprite2_array bank,unsigned int index)\n{\n if(xmas||!bank.data||bank.data!=spriteSheet8.data||bank.size!=spriteSheet8.size)return false;\n uint64_t wanted;\n switch(index) {\n  case 143:wanted=UINT64_C(0x9d732d4562f86474);break;\n  case 144:wanted=UINT64_C(0xa9ede9c9164a8044);break;\n  default:return false;\n }\n Uint8 source[12*14*2]={0};\n if(!decode_tile(bank,index,source,source+12*14,12,0,0))return false;\n uint64_t stamp=UINT64_C(0xcbf29ce484222325);\n for(size_t i=0;i<sizeof(source);i++){stamp^=source[i];stamp*=UINT64_C(0x100000001b3);}\n return stamp==wanted;\n}\n\n/* Sonic Wave inverted corner pair149/150:'), (' /* Sonic Wave inverted corner pair149/150 only;', ' /* Sonic Wave joined wave pair143/144 only; all multiplayer/link contexts stay classic.\n  * Keep these local mode/source gates before every cold or warm cache access. */\n if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&sonic_joined_wave_pair_member(index)>=0) {\n  if(twoPlayerMode||galagaMode||twoPlayerLinked||\n     (game_probe_density!=4&&game_probe_density!=8)||game_probe_missing||game_probe_invalid||\n     game_probe_original_reference||!game_probe_assets||!sonic_joined_wave_pair_source_matches(bank,index))return NULL;\n  slot=561+sonic_joined_wave_pair_member(index);role=8;\n }\n /* Sonic Wave inverted corner pair149/150 only;'), (' /* Sonic Wave inverted corner pair149/150 retain original indexed shadow', ' /* Sonic Wave joined wave pair143/144 retain original indexed shadow silhouettes, origin and order. */\n if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&sonic_joined_wave_pair_member(index)>=0&&style==MIRROR_SHADOW)return false;\n /* Sonic Wave inverted corner pair149/150 retain original indexed shadow')]
    restored=source
    for before,after in reversed(changes):
        assert restored.count(after)==1,'Missing/ambiguous exact renderer inverse'
        restored=restored.replace(after,before)
    assert restored==original,'Unexpected renderer change'
    names=git('ls-tree','-r','--name-only',BASE,'--','src').decode().splitlines()
    assert len(names)==153 and {str(p.relative_to(ROOT)) for p in (ROOT/'src').rglob('*') if p.is_file()}==set(names)
    for name in names:
        if name!='src/render_mirror.c':assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
    prior_tests=[f'prototype/test-sonic-{family}-{suffix}' for family in ['six-pair','upward-arch','shallow-pair','fat-pair','corner-pair','inverted-corner-pair','oblique-pair','inverted-oblique-pair'] for suffix in ['binding.py','binding.c','shots.c','scope.py']]
    for name in prior_tests:assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
    return original,{'baseline':BASE,'exact_renderer_inverse':True,'production_source_files_checked':len(names),'prior_thirtytwo_sonic_tests_unchanged':prior_tests,'only_changed_production_file':'src/render_mirror.c','candidate_renderer_sha256':SHA(source.encode()),'gameplay_input_shots_blitters_rng_unchanged':True}

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


def source_physical_oracle(bank,index):
    pos=struct.unpack_from('<H',bank,2*(index-1))[0];physical=0
    colors,coverage=bytearray(168),bytearray(168)
    while bank[pos]!=15:
        op=bank[pos];pos+=1;physical+=op&15;run=op>>4
        if not run:physical+=320-12
        for value in bank[pos:pos+run]:
            y,x=divmod(physical,320)
            assert 0<=x<12 and 0<=y<14 and not coverage[y*12+x]
            colors[y*12+x]=value;coverage[y*12+x]=255;physical+=1
        pos+=run
    return bytes(colors+coverage)


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
    fields = {'role': (4, 1110000+index), 'identity': (4, 80000+IDS[1-IDS.index(index)]),
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
    rows=[]
    def add(name, resources):
        folder=work/name;folder.mkdir()
        valid8=[];density8=[];valid4=[];density4=[]
        for i in IDS:
            spec=resources.get(i,{})
            for d in [8,4]:
                kind=spec.get(d)
                if kind is None:continue
                raw=art[i] if d==8 else reduced(art[i],i)
                if kind!='valid':
                    raw=mutate(raw,i,kind)
                    if kind=='density':raw=raw[:8]+struct.pack('<I',4 if d==8 else 8)+raw[12:]
                (folder/f'bullet-{i}-{d}.hda').write_bytes(raw)
            ok8=spec.get(8)=='valid';ok4=spec.get(4)=='valid'
            valid8.append(int(ok8 or ok4));density8.append(8 if ok8 else 4)
            valid4.append(int(ok4));density4.append(4)
        rows.append([name,*valid8,*density8,*valid4,*density4])
    add('valid',{i:{8:'valid'} for i in IDS})
    add('both',{i:{8:'valid',4:'valid'} for i in IDS})
    add('missing',{})
    add('only4',{i:{4:'valid'} for i in IDS})
    for i in IDS:
        other=IDS[1-IDS.index(i)]
        add(f'missing-{i}',{other:{8:'valid'}})
        add(f'only4-{i}',{i:{4:'valid'},other:{8:'valid'}})
        for kind in ['magic','role','identity','density','width','height','anchor-x','anchor-y','short-header','truncated','extra']:
            for suffix,spec in [('-8',{8:kind}),('-8-valid4',{8:kind,4:'valid'}),('-4',{4:kind}),('-8-and4',{8:kind,4:kind}),('valid8-bad4',{8:'valid',4:kind})]:
                add(f'{kind}{suffix}-{i}',{i:spec,other:{8:'valid',4:'valid'}})
    (work/'variants.tsv').write_text(''.join(' '.join(map(str,r))+'\n' for r in rows))
    return rows

def source_rows(contract, audit, data, out):
    fields=['drain','shotrepeat','multi','weapani','max','tx','ty','aim','attack','del','sx','sy','bx','by','sg','acceleration','accelerationx','circlesize','sound','trail','shipblastfilter']
    tokens='H B B H B B B B 8B 8B 8b 8b 8b 8b 8H b b B B B B'.split()
    fmt={'u8':'B','s8':'b','u16':'H','s16':'h'}
    reader=(ROOT/'src/episodes.c').read_text()
    schema=[(n,(count if count!='1' else '')+fmt[t]) for t,n,count in re.findall(r'fread_(u8|s8|u16|s16)_die\(\s*&?weapons\[i\]\.(\w+),\s*(\d+),\s*f\)',reader)]
    assert schema==list(zip(fields,tokens)) and struct.calcsize('<'+''.join(tokens))==80
    primary=[*range(276,298),*range(756,767),465,467,468]
    wanted=sorted(primary+[i+1000 for i in primary])
    tables,initializers,port_initializers,first_records=[],[],[],None
    cval=lambda v:'{'+','.join(map(str,v))+'}' if isinstance(v,list) else str(v)
    for table,expected in enumerate(audit['tables']):
        name=expected['file'];raw=(data/name).read_bytes()
        assert SHA(raw)==expected['file_sha256']==audit['data_sha256'][name]
        if table==0:start=struct.unpack_from('<i',raw)[0]
        else:
            count=struct.unpack_from('<H',raw)[0]
            start=struct.unpack_from('<I',raw,2+4*(count-1))[0]
        assert start==expected['item_table_offset'] and struct.unpack_from('<7H',raw,start)==(818,60,6,18,37,11,850)
        pos=start+14;records={};spans={};record_bytes={}
        for rid in [*range(819),*range(1000,1819)]:
            begin=pos;rec={}
            for field,token in zip(fields,tokens):
                values=list(struct.unpack_from('<'+token,raw,pos));pos+=struct.calcsize('<'+token)
                rec[field]=values if len(values)>1 else values[0]
            records[rid]=rec;record_bytes[rid]=raw[begin:pos];spans[rid]={'offset':begin,'bytes':80,'sha256':SHA(raw[begin:pos])}
        ports=[]
        for port in range(61):
            p=raw[pos:pos+82];pos+=82
            ports.append({'id':port,'name':p[1:1+min(p[0],30)].decode('ascii').rstrip(),'mode_count':p[31],
                          'shots':[list(struct.unpack_from('<11H',p,32)),list(struct.unpack_from('<11H',p,54))],
                          'cost':struct.unpack_from('<H',p,76)[0],'poweruse':struct.unpack_from('<H',p,80)[0]})
        assert ports[11]==expected['port11'] and ports[41]==expected['port41']
        assert ports[11]['shots']==[list(range(276,287)),list(range(287,298))] and ports[11]['poweruse']==50
        assert ports[41]['shots'][0]==list(range(756,767)) and not any(ports[41]['shots'][1]) and ports[41]['poweruse']==50
        audited={r.get('id',r.get('record',r.get('shot_record'))):r for r in expected['all_audited_weapon_records']+expected['all22_sonic_rows']+expected['all11_port41_rows']}
        for rid,row in audited.items():
            assert records[rid]==row['full_original_record'] and spans[rid]==row['record_span'],(name,rid)
        for rid in primary:
            assert record_bytes[rid]==record_bytes[rid+1000],(name,rid,'+1000 copy differs')
            assert 0<records[rid]['multi']<=8 and 0<records[rid]['max']<=8
        selected_rear=[rid for rid in range(276,298) if set(IDS)&set(records[rid]['sg'][:records[rid]['max']])]
        selected_front=[rid for rid in range(756,767) if set(IDS)&set(records[rid]['sg'][:records[rid]['max']])]
        assert selected_rear==list(range(292,298)) and selected_front==[756,757,758,*range(760,767)]
        assert set(IDS)<=set(records[467]['sg'][:records[467]['max']])
        assert not set(IDS)&set(records[465]['sg'][:records[465]['max']]) and not set(IDS)&set(records[468]['sg'][:records[468]['max']])
        assert records[118]==records[1118] and set(IDS)<=set(records[118]['sg'][:records[118]['max']])
        pair_rows={r['record']:r for r in expected['selected_active_pair_motion_rows']}
        pairs=[]
        for rid in [*selected_rear,*selected_front,467]:
            rec=records[rid];row=pair_rows[rid]
            assert spans[rid]==row['record_span'] and rec['multi']==row['multi'] and rec['max']==row['max']
            matched=set()
            for pair in row['pairs']:
                left,right=[i-1 for i in pair['ordinals']]
                assert rec['sg'][left]==143 and rec['sg'][right]==144 and rec['bx'][right]-rec['bx'][left]==12
                assert all(rec[f][left]==rec[f][right] for f in ['by','sx','sy','del'])
                assert pair['seam_separation_during_equal_age_motion']==12
                matched|={left,right}
            assert matched=={i for i in range(rec['max']) if rec['sg'][i] in IDS}
            pairs.append({'record':rid,'pairs':len(row['pairs']),'max':rec['max'],'multi':rec['multi']})
        if first_records is None:first_records=records
        else:
            for rid in wanted:
                for field in fields:
                    if field=='shipblastfilter':continue
                    a,b=records[rid][field],first_records[rid][field]
                    if isinstance(a,list):a,b=a[:records[rid]['max']],b[:first_records[rid]['max']]
                    assert a==b,(name,rid,field)
        family=sorted({i for rid in range(276,298) for i in records[rid]['sg'][:records[rid]['max']]})
        assert family==FAMILY and family==sorted(map(int,contract['frames']))
        rows=[{'record':rid,'offset':spans[rid]['offset'],'sha256':spans[rid]['sha256'],'max':records[rid]['max'],'multi':records[rid]['multi'],
               'active_ids':records[rid]['sg'][:records[rid]['max']],'shipblastfilter':records[rid]['shipblastfilter']} for rid in wanted]
        tables.append({'file':name,'file_sha256':SHA(raw),'item_table_offset':start,'all22_rear_rows_verified':True,'all11_front_rows_verified':True,
                       'charge465_467_468_verified':True,'all36_primary_plus1000_byte_equal':True,'rows':rows,'selected_pair_rows':pairs,
                       'charge_caller_port16_poweruse':ports[16]['poweruse'],'dormant118_1118_unchanged_source_only':True})
        initializers.append(' {'+'\n'.join(f' [{rid}]={{'+','.join('.'+f+'='+cval(records[rid][f]) for f in fields)+'},' for rid in wanted)+'\n },')
        port_initializers.append(' {'+','.join(str(p['poweruse']) for p in ports)+'},')
    shot_source=(ROOT/'src/shots.c').read_text()
    funcs={n:extract(shot_source,n) for n in ['player_shot_create','player_shot_move_and_draw']}
    original=git('show',BASE+':src/shots.c').decode().replace('\r\n','\n')
    assert all(value==extract(original,n) for n,value in funcs.items())
    assert not re.search(r'\b(?:rand|random|mt_rand|mt_rand_1)\s*\(',''.join(funcs.values()))
    (out/'shot-functions.inc').write_text(''.join(funcs.values()))
    shot_type=re.search(r'typedef struct \{.*?\} PlayerShotDataType;',(ROOT/'src/shots.h').read_text(),re.S).group()
    weapon_type=re.search(r'typedef struct\s*\{.*?\} JE_WeaponType;',(ROOT/'src/episodes.h').read_text(),re.S).group()
    (out/'shot-types.inc').write_text(shot_type+'\n'+weapon_type+'\n')
    (out/'weapon-records.inc').write_text('static const JE_WeaponType weapon_tables[3][WEAP_NUM+1]={\n'+'\n'.join(initializers)+'\n};\nstatic const JE_word source_port_poweruse[3][PORT_NUM+1]={\n'+'\n'.join(port_initializers)+'\n};\n')
    remaining=sorted(set(FAMILY)-{6,16,44,54,63,73,82,130,131,143,144,149,150,223,224,242,243});assert len(remaining)==4
    return {'tables':tables,'all216_full_authentic_runtime_records_verified':True,'all22_rear_and11_front_and3_charge_rows_each_plus1000':True,
            'full_records_equal_across_tables':False,'active_patterns_equal_across_tables':True,'all_selected_pairs_equal_motion_and12px_seam':True,
            'family_ids':FAMILY,'other4_ids_unchanged':remaining,'exact_original_shot_functions_and_no_rng_calls':True,
            'no_selected_linked_direction_witness':True,'dormant118_1118_source_only_not_called':True,'shot_function_sha256':{n:SHA(v.encode()) for n,v in funcs.items()}}


def run(cmd, log, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    RUN_COMMANDS.append({'argv':list(map(str,cmd)),'log':str(log),'returncode':result.returncode})
    log.write_text(result.stdout+result.stderr)
    if result.returncode:
        print(result.stdout+result.stderr)
        result.check_returncode()
    return result


def guard_mutations(out, source, banks, work, packs, env):
    s=(out/'candidate/functions.inc').read_text()
    # These replacements each weaken exactly one independently required predicate.
    route_start=s.index(' /* Sonic Wave joined wave pair143/144 only;')
    route_end=s.index(' /* Sonic Wave inverted corner pair149/150 only;',route_start)
    route=s[route_start:route_end]
    mutations={}
    for label,before,after in [
     ('omit-twoPlayerMode','if(twoPlayerMode||galagaMode||twoPlayerLinked||','if(galagaMode||twoPlayerLinked||'),
     ('omit-galagaMode','if(twoPlayerMode||galagaMode||twoPlayerLinked||','if(twoPlayerMode||twoPlayerLinked||'),
     ('omit-twoPlayerLinked','if(twoPlayerMode||galagaMode||twoPlayerLinked||','if(twoPlayerMode||galagaMode||'),
    ]:
     assert route.count(before)==1
     mutations[label]=(route,route.replace(before,after,1))
    # Restrict source mutants to the new helper, leaving all prior helpers identical.
    a=s.index('static bool sonic_joined_wave_pair_source_matches(Sprite2_array bank,unsigned int index)\n{')
    b=s.index('\n}\n',a)+3
    helper=s[a:b]
    mutations['omit-explicit-xmas']=(helper,helper.replace('if(xmas||','if(',1))
    mutations['trust-warm-source']=(helper,helper.replace(' uint64_t wanted;',' if(assets[561+sonic_joined_wave_pair_member(index)].initialized)return true;\n uint64_t wanted;',1))
    def fnv(data):
     h=0xcbf29ce484222325
     for v in data:h=((h^v)*0x100000001b3)&0xffffffffffffffff
     return f'0x{h:016x}'
    F=[6,16,44,54,63,73,82,105,106,124,125,130,131,143,144,149,150,223,224,242,243]
    ref=(out/'reference.bin').read_bytes()
    for label,start in [('indices-only',0),('coverage-only',168)]:
     changed=helper
     for i,old in [(143,'0x9d732d4562f86474'),(144,'0xa9ede9c9164a8044')]:
      off=F.index(i)*336
      changed=changed.replace(old,fnv(ref[off+start:off+start+168]))
     changed=changed.replace('for(size_t i=0;i<sizeof(source);i++)',f'for(size_t i={start};i<{start+168};i++)')
     mutations[label]=(helper,changed)
    # Any omission of the early shadow escape would enter the poisoned cache.
    line=' if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&sonic_joined_wave_pair_member(index)>=0&&style==MIRROR_SHADOW)return false;\n'
    mutations['omit-early-indexed-shadow']=(line,'')
    report={}
    for label,(before,after)in mutations.items():
     assert s.count(before)==1 and before!=after,label
     folder=out/'guard-mutants'/label;folder.mkdir(parents=True,exist_ok=True)
     for name in ['sprite-type.inc','types.inc','blitters.inc','wrappers.inc']:(folder/name).write_bytes((out/'candidate'/name).read_bytes())
     (folder/'functions.inc').write_text(s.replace(before,after,1))
     binary=folder/'test'
     cmd=['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-function','-Wno-unused-variable','-O2','-DBASELINE=0','-I'+str(folder),str(Path(__file__).with_suffix('.c')),'-Wl,--wrap=fopen','-Wl,--wrap=malloc','-o',str(binary)]
     q=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(folder/'compile.log').write_text(q.stdout+q.stderr);RUN_COMMANDS.append({'argv':cmd,'log':str(folder/'compile.log'),'returncode':q.returncode});q.check_returncode()
     cmd=[str(binary),str(out/'normal.bank8'),str(out/'christmas.bank8'),str(work),str(out/'reference.bin'),*[str(ROOT/'assets/hd/packs'/packs[k]) for k in ['preview','debug']]]
     q=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(folder/'run.log').write_text(q.stdout+q.stderr);RUN_COMMANDS.append({'argv':cmd,'log':str(folder/'run.log'),'returncode':q.returncode,'expected_test_rejection':True})
     assert q.returncode!=0,label+' mutant incorrectly survived'
     report[label]={'status':'EXPECTED_TEST_REJECTION','returncode':q.returncode,'first_failure':q.stderr[:1200],'changed_extracted_functions_sha256':hashlib.sha256((folder/'functions.inc').read_bytes()).hexdigest()}
     print(label+': REJECTED',flush=True)
    # A read-only premature cache access leaves bytes unchanged; the poisoned-cache
    # sanitizer fixture must still reject it. This is distinct from predicate loss.
    label='read-cache-before-mode-gates'
    before=' if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&sonic_joined_wave_pair_member(index)>=0) {\n'
    after=before+'  volatile bool premature_cache_read=assets[561+sonic_joined_wave_pair_member(index)].initialized;\n  (void)premature_cache_read;\n'
    assert s.count(before)==1
    folder=out/'guard-mutants'/label;folder.mkdir(parents=True,exist_ok=True)
    for name in ['sprite-type.inc','types.inc','blitters.inc','wrappers.inc']:(folder/name).write_bytes((out/'candidate'/name).read_bytes())
    (folder/'functions.inc').write_text(s.replace(before,after,1))
    binary=folder/'sanitized'
    cmd=['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-function','-Wno-unused-variable','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-DSANITIZED=1','-DBASELINE=0','-I'+str(folder),str(Path(__file__).with_suffix('.c')),'-Wl,--wrap=fopen','-Wl,--wrap=malloc','-o',str(binary)]
    q=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(folder/'compile.log').write_text(q.stdout+q.stderr);RUN_COMMANDS.append({'argv':cmd,'log':str(folder/'compile.log'),'returncode':q.returncode});q.check_returncode()
    q=subprocess.run([str(binary),str(out/'normal.bank8'),str(out/'christmas.bank8'),str(work),str(out/'reference.bin'),*[str(ROOT/'assets/hd/packs'/packs[k]) for k in ['preview','debug']]],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'),timeout=180)
    (folder/'run.log').write_text(q.stdout+q.stderr)
    assert q.returncode!=0 and 'use-after-poison' in q.stderr,label+' mutant incorrectly survived'
    report[label]={'status':'EXPECTED_ASAN_USE_AFTER_POISON','returncode':q.returncode,'first_failure':q.stderr[:1400],'changed_extracted_functions_sha256':hashlib.sha256((folder/'functions.inc').read_bytes()).hexdigest()}
    print(label+': ASAN REJECTED READ-ONLY CACHE ACCESS',flush=True)
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['data','contract','audit-facts','out']: p.add_argument('--'+name,type=Path,required=True)
    args = p.parse_args();out = args.out.resolve()
    assert not out.exists() and ROOT != out and ROOT not in out.parents
    assert SHA(args.contract.read_bytes()) == 'a3b891c3b11e33f46c38199befc01712a65bd006f1a3d8e0c1b6c2d7f62f42c3'
    frozen_test_pins={name:SHA((ROOT/'prototype'/name).read_bytes()) for name in ['test-sonic-joined-wave-pair-binding.py','test-sonic-joined-wave-pair-binding.c','test-sonic-joined-wave-pair-shots.c','test-sonic-joined-wave-pair-scope.py']}
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
    encoded={}
    for label,bank in zip(['normal','christmas'],banks):
        source_facts[label]={};encoded[label]={}
        for i in IDS:
            value=decode(bank,i);start=struct.unpack_from('<H',bank,2*(i-1))[0];end=start
            while bank[end]!=15:end+=1+(bank[end]>>4)
            end+=1;encoded[label][i]=bank[start:end]
            stamp=0xcbf29ce484222325
            for byte in value:stamp=((stamp^byte)*0x100000001b3)&0xffffffffffffffff
            source_facts[label][str(i)]={'bank_bytes':len(bank),'encoded_offset':start,'encoded_bytes':end-start,'encoded_sha256':SHA(bank[start:end]),'decoded_indices_sha256':SHA(value[:168]),'decoded_coverage_sha256':SHA(value[168:]),'decoded_index_then_coverage_sha256':SHA(value),'fnv1a64':hex(stamp),'occupied_cells':sum(bool(v) for v in value[168:])}
    audit_raw=args.audit_facts.read_bytes()
    assert SHA(audit_raw)=='50729524b5a7b69f20c7dcdefbc05f39a98f8b575f6321df9bdca93c47008331'
    audit=json.loads(audit_raw)
    for label,key in [('normal','normal_selected_facts'),('christmas','christmas_selected_facts')]:
        audited={r['id']:r for r in audit[key]}
        for i in IDS:
            actual=source_facts[label][str(i)];expected=audited[i]
            for field in ['encoded_bytes','encoded_sha256','decoded_indices_sha256','decoded_coverage_sha256','decoded_index_then_coverage_sha256','fnv1a64','occupied_cells']:
                assert actual[field]==expected[field],(label,i,field)
    for i in IDS:
        assert encoded['normal'][i]!=encoded['christmas'][i]
        assert decode(banks[0],i)[:168]!=decode(banks[1],i)[:168]
        assert decode(banks[0],i)[168:]!=decode(banks[1],i)[168:]
    assert [source_facts['normal'][str(i)]['occupied_cells'] for i in IDS]==[87,98]
    normal_halves=[decode(banks[0],i) for i in IDS]
    for value in normal_halves:
        assert not any(value[13*12:14*12]) and not any(value[168+13*12:336]), 'Bottom logical row must remain empty'
    flipped_left=b''.join(bytes(normal_halves[0][base+y*12+x] for y in range(14) for x in range(11,-1,-1)) for base in [0,168])
    assert flipped_left!=normal_halves[1], 'Independent source halves cannot be mirrored'
    seam_rows=[y for y in range(14) if normal_halves[0][168+y*12+11] and normal_halves[1][168+y*12]]
    assert seam_rows==list(range(9)), 'Original seam support changed'
    source_geometry={'logical_half_size':[12,14],'logical_whole_size':[24,14],'split_x':12,
                     'source_offsets':[-6,6],'bottom_empty_rows':1,'mirror_alias':False,'both_seam_cells_occupied_rows':seam_rows}
    for bank in banks:
        for i in range(1,305):
            assert decode(bank,i)==source_physical_oracle(bank,i),'literal original physical pointer oracle mismatch'
    for i in FAMILY:
        value=decode(banks[0],i);frame=contract['frames'][str(i)]
        assert SHA(value[:168])==frame['decoded_indices_sha256'] and SHA(value[168:])==frame['decoded_coverage_sha256']
        assert value == (args.contract.parent/f'bank8-{i}-indices-coverage.bin').read_bytes()
    art = {i:(ROOT/f'assets/hd/artwork/player-sonic-joined-wave-pair-v1/output/bullet-{i}-8.hda').read_bytes() for i in IDS}
    art_contract_path=ROOT/'assets/hd/artwork/player-sonic-joined-wave-pair-v1/contract.json'
    assert SHA(art_contract_path.read_bytes())=='0a62bb9c579986902ed09eb72ae588f2d33102d079834232899996d68224091e'
    art_contract=json.loads(art_contract_path.read_text())
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
    reference=b''.join(decode(b,i) for b in banks for i in FAMILY);(out/'reference.bin').write_bytes(reference)
    work=out/'fixtures';work.mkdir();variants=prepare_variants(work,art)
    previous_art = {}
    for package,old_ids in [('player-sonic-six-pair-v1',[6,44]),('player-sonic-upward-arch-v1',[73]),('player-sonic-shallow-pair-v1',[63,82]),('player-sonic-fat-pair-v1',[16,54]),('player-sonic-corner-pair-v1',[130,131]),('player-sonic-inverted-corner-pair-v1',[149,150]),('player-sonic-oblique-pair-v1',[223,224]),('player-sonic-inverted-oblique-pair-v1',[242,243])]:
        previous_contract=json.loads((ROOT/'assets/hd/artwork'/package/'contract.json').read_text())
        previous_entries={e['id']:e for e in previous_contract['entries']}
        for i in old_ids:
            name=f'bullet-{i}-8.hda';path='assets/hd/artwork/'+package+'/output/'+name
            value=(ROOT/path).read_bytes()
            assert value==git('show',BASE+':'+path) and SHA(value)==previous_entries[i]['HDA_sha256']
            for pack in packs.values():assert (ROOT/'assets/hd/packs'/pack/name).read_bytes()==value
            (work/'valid'/name).write_bytes(value);previous_art[str(i)]=SHA(value)
    rows=source_rows(contract,audit,args.data,out)
    sprite_type=re.search(r'typedef struct\s*\{\s*size_t size;\s*Uint8 \*data;\s*\}\s*Sprite2_array;', (ROOT/'src/sprite.h').read_text()).group()
    names=['decode_tile','read_asset','explosion_asset_slot','mint27_source_matches','get_asset','render_mirror_entity']
    patterns=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'static Asset assets\[\d+\];',r'enum \{ ASSET_NEWSH2=.*?\};']
    blits={n:extract((ROOT/'src/sprite.c').read_text(),n) for n in ['blit_sprite2','blit_sprite2_blend','blit_sprite2_darken']}
    wrapper=extract((ROOT/'src/entity_draw.c').read_text(),'draw_entity_sprite2')
    builds={}
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    for label,rs in [('baseline',baseline),('candidate',source)]:
        folder=out/label;folder.mkdir();(folder/'sprite-type.inc').write_text(sprite_type)
        helpers={n:extract(rs,n) for n in names+['sonic_six_pair_member','sonic_six_pair_source_matches','sonic_upward_arch_source_matches','sonic_shallow_pair_member','sonic_shallow_pair_source_matches','sonic_fat_pair_member','sonic_fat_pair_source_matches','sonic_corner_pair_member','sonic_corner_pair_source_matches','sonic_inverted_corner_pair_member','sonic_inverted_corner_pair_source_matches','sonic_oblique_pair_member','sonic_oblique_pair_source_matches','sonic_inverted_oblique_pair_member','sonic_inverted_oblique_pair_source_matches']+(['sonic_joined_wave_pair_member','sonic_joined_wave_pair_source_matches'] if label=='candidate' else [])}
        (folder/'types.inc').write_text('\n'.join(re.search(pattern,rs,re.S).group() for pattern in patterns))
        (folder/'functions.inc').write_text('\n'.join(s[:s.index('{')].strip()+';' for s in helpers.values())+'\n'+''.join(helpers.values()))
        (folder/'blitters.inc').write_text(''.join(s.replace('void '+n+'(', 'void production_'+n+'(',1) for n,s in blits.items()))
        (folder/'wrappers.inc').write_text(wrapper)
        builds[label]={'function_sha256':{n:SHA(s.encode()) for n,s in {**helpers,**blits,'draw_entity_sprite2':wrapper}.items()},'runs':{}}
        for name,flags in [('optimized',['-O2']),('sanitized',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
            cmd=[os.environ.get('CC','cc'),'-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-function','-Wno-unused-variable',*flags,*(['-DSANITIZED=1'] if name=='sanitized' else []),'-DBASELINE='+str(int(label=='baseline')),'-I'+str(folder),str(Path(__file__).with_suffix('.c')),'-Wl,--wrap=fopen','-Wl,--wrap=malloc','-o',str(folder/name)]
            run(cmd,folder/(name+'-compile.log'))
            result=run([str(folder/name),str(out/'normal.bank8'),str(out/'christmas.bank8'),str(work),str(out/'reference.bin'),*[str(ROOT/'assets/hd/packs'/packs[k]) for k in ['preview','debug']]],folder/(name+'.log'),env=env,timeout=180)
            builds[label]['runs'][name]=json.loads(result.stdout);print(label+'/'+name+': '+result.stdout.strip(),flush=True)
    shot_runs={}
    for label in ['baseline','candidate']:
        shot_runs[label]={}
        for name,flags in [('optimized',['-O2']),('sanitized',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
            binary=out/(label+'-shots-'+name)
            cmd=[os.environ.get('CC','cc'),'-std=c99','-Wall','-Wextra','-Werror',*flags,'-DBASELINE='+str(int(label=='baseline')),'-I'+str(out),str(ROOT/'prototype/test-sonic-joined-wave-pair-shots.c'),'-o',str(binary)]
            run(cmd,out/(label+'-shots-'+name+'-compile.log'))
            result=run([str(binary)],out/(label+'-shots-'+name+'.log'),env=env,timeout=180)
            shot_runs[label][name]=json.loads(result.stdout);print(label+'/shots/'+name+': '+result.stdout.strip(),flush=True)
    assert shot_runs['baseline']['optimized'] == shot_runs['baseline']['sanitized'] == shot_runs['candidate']['optimized'] == shot_runs['candidate']['sanitized'], 'Original shot state/order parity failed'
    mutations=guard_mutations(out,source,banks,work,packs,env)
    assert (ROOT/'src/render_mirror.c').read_text() == source, 'Renderer changed during test'
    assert all(SHA((ROOT/'prototype'/name).read_bytes()) == digest for name,digest in frozen_test_pins.items()), 'Harness changed during test'
    report={'status':'PASS','commands':RUN_COMMANDS,'test_file_sha256':frozen_test_pins,'guard_mutants':mutations,'source_contract_sha256':SHA(args.contract.read_bytes()),'art_contract_sha256':SHA((ROOT/'assets/hd/artwork/player-sonic-joined-wave-pair-v1/contract.json').read_bytes()),'previous_fifteen_art_sha256':previous_art,'scope':scope,'art_sha256':{str(i):SHA(v) for i,v in art.items()},'default_packs':packs,'data_sha256':data_pins,'selected_pair_source_facts':source_facts,'source_geometry':source_geometry,'all21_private_source_fixture_bytes_verified':True,'literal_original_physical_pointer_oracle_all608_tiles_equal':True,'source_rows':rows,'shot_runs':shot_runs,'actual_christmas_selected_encoded_sources_equal_normal':all(encoded['normal'][i]==encoded['christmas'][i] for i in IDS),'explicit_xmas_guard_tested_with_normal_selected_bytes':True,'actual_christmas_selected_decoded_sources_equal_normal':all(decode(banks[0],i)==decode(banks[1],i) for i in IDS),'resource_variants':variants,'builds':builds,'both_default_packs_loaded_independently':True,'actual_christmas143_144_selected_encoded_indices_and_coverage_different':True,'all_three_mode_flags_eight_combinations_cold_warm_both_densities':True,'prior_fifteen_cached_metadata_pointer_rgba_bytes_unchanged':True,'unselected105_106_124_125_remain_classic':True,'exact_baseline_candidate_shot_parity':True,'normal_blend_shadow_indexed_wrappers':True,'game_runs':0,
            'limitations':['Focused extracted production source, loader, guard, wrapper and original RLE tests; RGBA head compositor is a metadata-checking stub.','Source guards validate selected decoded identity, not whole-bank provenance; no root-epoch guarantee is added.','Generic compositor integration, actual-play aesthetics, natural acquisition and full-engine runtime require separate acceptance.','LeakSanitizer disabled for executor compatibility; AddressSanitizer and UndefinedBehaviorSanitizer enabled.','Malformed original source is exercised at the HD guard only; original unchecked RLE is never executed against malformed data.']}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__': main()
