#!/usr/bin/env python3
"""Portable exact-source front Multi and finite reuse units. Never launches a game.
Original item data and generated fixtures remain outside the checkout.
"""
import argparse, hashlib, json, os, re, struct, subprocess, zlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = '7df8368acb90a73b170b1238b3161eefddb7a8e1'
CONTRACT_SHA = 'dc4bbc3ad75913f7701eb7e9e21546c84c28f53941880599e606cb6b7689a23c'
SHA = lambda b: hashlib.sha256(b).hexdigest()
TARGET = {121,122,163,164,201,202,279,280}
EXTRAS = [268,461,573,574,575,684,685,686,687,688,689,690,727,729,445,451]

def extract(source, name):
    m = re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',source,re.M)
    assert m, name
    end=source.index('{',m.start())+1; depth=1
    while depth: depth+=(source[end]=='{')-(source[end]=='}'); end+=1
    return source[m.start():end]+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['original-data','contract','out']: p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args(); O=a.out.resolve()
    assert not O.exists() and ROOT not in O.parents, 'Use a fresh output outside Git'
    cr=a.contract.read_bytes(); assert SHA(cr)==CONTRACT_SHA
    c=json.loads(cr); assert c['baseline']==BASE
    files=['src/shots.c','src/shots.h','src/mainint.c','src/episodes.c','src/episodes.h','src/lvlmast.h','src/varz.c']
    src={n:(ROOT/n).read_bytes() for n in files}
    for n,b in src.items(): assert b==subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+n]), n
    O.mkdir(); extracted={}
    def write(name,raw):
        if isinstance(raw,str): raw=raw.encode()
        (O/name).write_bytes(raw); extracted[name]=SHA(raw)
    for name in ['player_shot_create','player_shot_move_and_draw','player_shot_set_direction']:
        write(name+'.inc',extract(src['src/shots.c'].decode(),name))
    for file,start,end,out in [('src/episodes.h','typedef struct\n{\n\tJE_word     drain;','} JE_WeaponType;','weapon_type.inc'),('src/episodes.h','typedef struct\n{\n\tchar    name[31];','} JE_WeaponPortType[PORT_NUM + 1];','port_type.inc'),('src/shots.h','typedef struct {','} PlayerShotDataType;','shot_type.inc')]:
        text=src[file].decode(); b=text.index(start); e=text.index(end,b)+len(end);write(out,text[b:e]+'\n')
    text=src['src/mainint.c'].decode(); b=text.index('if (!(twoPlayerLinked && playerNum_ == 2))'); e=text.index('{',b)+1;depth=1
    while depth:depth+=(text[e]=='{')-(text[e]=='}');e+=1
    write('cadence.inc',text[b:e]+'\n')
    arrays={}
    for name,file,count in [('linkMultiGr','src/shots.c',17),('linkMult2Gr','src/shots.c',17),('linkSonicGr','src/shots.c',17),('linkGunWeapons','src/varz.c',38),('chargeGunWeapons','src/varz.c',38)]:
        m=re.search(r'(?:static )?const JE_word '+name+r'\['+str(count)+r'\][^=]*=\s*\{([^}]+)\};',src[file].decode(),re.S);assert m
        arrays[name]=[int(x) for x in m.group(1).split(',') if x.strip()]
        write(name+'.inc',m.group()+'\n')
    for name,r in c['directional_reuse'].items():assert arrays[name]==r['table']
    # Independent fixed schema, cross-checked against the unchanged production loader.
    fields=['drain','shotrepeat','multi','weapani','max','tx','ty','aim','attack','del','sx','sy','bx','by','sg','acceleration','accelerationx','circlesize','sound','trail','shipblastfilter']
    tokens='H B B H B B B B 8B 8B 8b 8b 8b 8b 8H b b B B B B'.split()
    fmt={'u8':'B','s8':'b','u16':'H','s16':'h'}
    prod=[(name,(n if n!='1' else '')+fmt[code]) for code,name,n in re.findall(r'fread_(u8|s8|u16|s16)_die\(\s*&?weapons\[i\]\.(\w+),\s*(\d+),\s*f\)',src['src/episodes.c'].decode())]
    assert prod==list(zip(fields,tokens)) and struct.calcsize('<'+''.join(tokens))==80
    bounds={k:int(v)for k,v in re.findall(r'#define\s+(\w+)\s+(\d+)',src['src/lvlmast.h'].decode())}
    assert (bounds['WEAP_END1'],bounds['WEAP_START2'],bounds['WEAP_NUM'])==(818,1000,1818)
    def used(r):return {k:v[:r['max']]if isinstance(v,list)else v for k,v in r.items()}
    def hits(r):
        fs=set()
        for phase in range(r['max']):
            for f in range(r['del'][phase]-99 if 100<r['del'][phase]<120 else r['weapani']+1):
                s=r['sg'][phase]+f
                if s>60000:continue
                if s>1000:s%=1000
                if 0<s<=500:fs.add(s)
        return fs&TARGET
    tables=[];extra=[];spans=[];decoded={}; data_pins={}; port_power=[]
    for filename in ['tyrian.hdt','tyrian4.lvl','tyrian5.lvl']:
        raw=(a.original_data/filename).read_bytes(); assert SHA(raw)==c['data_sha256'][filename]
        data_pins[filename]={'sha256':SHA(raw),'crc32':f'{zlib.crc32(raw):08x}','bytes':len(raw)}
        pos=(struct.unpack_from('<i',raw)[0]if filename.endswith('.hdt')else struct.unpack_from('<i',raw,2+4*(struct.unpack_from('<H',raw)[0]-1))[0])+14; records={}
        for rid in list(range(819))+list(range(1000,1819)):
            start=pos;r={}
            for field,tok in zip(fields,tokens):
                vals=list(struct.unpack_from('<'+tok,raw,pos));pos+=struct.calcsize('<'+tok);r[field]=vals if len(vals)>1 else vals[0]
            records[rid]=r
            if rid in list(range(166,177))+EXTRAS:spans.append({'table':filename,'record':rid,'offset':start,'bytes':pos-start,'sha256':SHA(raw[start:pos])})
        ports=[]
        for i in range(61):
            b=raw[pos:pos+82];pos+=82;ports.append({'id':i,'opnum':b[31],'ops':[list(struct.unpack_from('<11H',b,32)),list(struct.unpack_from('<11H',b,54))],'poweruse':struct.unpack_from('<H',b,80)[0]})
        assert ports[2]['opnum']==1 and ports[2]['ops'][0]==list(range(166,177)) and ports[2]['poweruse']==40
        pos+=(bounds['SPECIAL_NUM']+1)*37+(bounds['POWER_NUM']+1)*37+(bounds['SHIP_NUM']+1)*41
        options=[]
        for i in range(bounds['OPTION_NUM']+1):
            b=raw[pos:pos+86];pos+=86;options.append({'id':i,'pwr':b[31],'wport':b[80],'wpnum':struct.unpack_from('<H',b,81)[0]})
        for rid in range(166,177):assert used(records[rid])==c['tables'][filename]['front_rows'][str(rid)]
        for rid in EXTRAS[:-2]:assert used(records[rid])==c['tables'][filename]['additional_referenced_records'][str(rid)]
        raw_hits=sorted(rid for rid,r in records.items()if hits(r));assert raw_hits==c['tables'][filename]['raw_record_hits']
        port_hits=[(p['id'],m+1,k+1,rid) for p in ports for m in range(min(2,p['opnum'])) for k,rid in enumerate(p['ops'][m]) if rid in records and hits(records[rid])]
        assert {q[0]for q in port_hits}=={2,10,27,37}
        assert [(q[1],q[2],q[3])for q in port_hits if q[0]==10]==[(2,4,268)]
        assert [q[3]for q in port_hits if q[0]==27]==[573,574,575]
        assert [q[3]for q in port_hits if q[0]==37]==list(range(684,691))
        option_hits=[dict(o,records=[rid for rid in range(o['wpnum'],o['wpnum']+o['pwr']+1)if rid in records and hits(records[rid])])for o in options if o['wport']and any(rid in records and hits(records[rid])for rid in range(o['wpnum'],o['wpnum']+o['pwr']+1))]
        assert [(o['id'],o['wport'],o['wpnum'],o['pwr'],o['records'])for o in option_hits]==[(20,16,727,0,[727]),(22,16,729,0,[729])]
        charge_hits=[dict(port=p,base=base,stage=stage,record=base+stage,ids=sorted(hits(records[base+stage])))for p,base in enumerate(arrays['chargeGunWeapons'],1)if base for stage in range(6)if hits(records[base+stage])]
        assert charge_hits==c['tables'][filename]['charge_hits']
        assert {q['record']for q in charge_hits}=={461} and all(q['base']==458 and q['stage']==3 for q in charge_hits)
        assert [arrays['linkGunWeapons'][p-1]for p in [10,27,32,22,38]]==[445,445,445,451,451]
        tables.append([records[i]for i in range(166,177)]);extra.append([records[i]for i in EXTRAS]);port_power.append([p['poweruse']for p in ports]);decoded[filename]={'raw_record_hits':raw_hits,'ordinary_reuse':port_hits,'option_reuse':option_hits,'charge_reuse':charge_hits}
    # Pin the untouched actual caller expressions, not just array memberships.
    for needle in ['player_shot_set_direction(b, this_player->items.weapon[REAR_WEAPON].id, linkGunDirec);','chargeGunWeapons[player[1].items.weapon[REAR_WEAPON].id-1] + chargeLevel','player_shot_create(this_option->wport, shot_i,','this_option->wpnum + this_player->sidekick[i].charge']:
        assert needle in src['src/mainint.c'].decode(),needle
    def literal(v):return '{'+','.join(map(str,v))+'}'if isinstance(v,list)else str(v)
    def record(r):return '{'+','.join('.'+k+'='+literal(v)for k,v in r.items())+'}'
    write('records.inc','static const JE_WeaponType fixture[3][11]={\n'+',\n'.join('{'+',\n'.join(map(record,rows))+'}'for rows in tables)+'};\nstatic const JE_WeaponType reuse_fixture[3][16]={\n'+',\n'.join('{'+',\n'.join(map(record,rows))+'}'for rows in extra)+'};\nstatic const int reuse_records[16]='+literal(EXTRAS)+';\nstatic const int fixture_power[3][61]={'+','.join(literal(v)for v in port_power)+'};\n')
    common=[os.environ.get('CC','cc'),'-std=c99','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I'+str(O),str(Path(__file__).with_suffix('.c'))];results={};commands={}
    for label,flags in [('optimized',['-O2']),('sanitized',['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
        cmd=common+flags+['-lm','-o',str(O/label)];commands[label]=cmd;r=subprocess.run(cmd,capture_output=True,text=True);(O/(label+'-compile.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
        env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');r=subprocess.run([str(O/label)],capture_output=True,text=True,env=env,timeout=120);(O/(label+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr;results[label]=json.loads(r.stdout);print(label+': '+r.stdout)
    assert results['optimized']==results['sanitized']
    for n,b in src.items():assert (ROOT/n).read_bytes()==b
    report={'status':'PASS','baseline':BASE,'game_runs':0,'source_sha256':{n:SHA(b)for n,b in src.items()},'data':data_pins,'contract_sha256':SHA(cr),'record_spans':spans,'decoded_reuse':decoded,'extracted_sha256':extracted,'compile_commands':commands,'results':results,'limitations':['Isolated exact production shot functions and ordinary cadence; fixtures supply caller-owned state and read-only observers. No engine execution or live-game acceptance.','Original data, decoded records and unit outputs remain outside Git.','Shared option/charge/directional routes are source/unit closure, not completion of those larger weapons.','LeakSanitizer disabled; AddressSanitizer and UndefinedBehaviorSanitizer enabled.'],'harness_sha256':{q.name:SHA(q.read_bytes())for q in [Path(__file__),Path(__file__).with_suffix('.c')]}}
    (O/'result.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
