#!/usr/bin/env python3
"""Verify source227 identity separately from art; original CAMANIS records/events.

Reads private original binaries but emits hashes/fields only. Static evidence is
not a claim that a live encounter fired or that production renderer was admitted.
"""
import argparse
import json
from pathlib import Path
import re
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_enemy_protron_p09 as b

PINS={
 'tyrian.shp':'80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0',
 'tyrian.hdt':'fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b',
 'tyrian3.lvl':'6a5b94a7d3e4f5a228bc0f702cfe035c8f9f03b20a3f02867d25e95b4249ce86',
 'newsh7.shp':'52c40a2438373f9fc9a7cd2d338ec149f4e81dda56d9c05061ee2264408f0b1a'}
PROFILES=[dict(record=133,enemy_offset=174256,enemy_fnv='9c877679a5ede691',weapon=141,weapon_offset=32468,weapon_fnv='11ebca5d1ae1dfeb',frequency=40,sg=[226],animation=2,multi=1,maximum=1,event_ordinal=37,event_time=210,event_offset=514,egraphic=[13,15,17,15]),dict(record=129,enemy_offset=173948,enemy_fnv='481af40b89888070',weapon=134,weapon_offset=31908,weapon_fnv='fdd291f76a044203',frequency=28,sg=[244,227,227],animation=0,multi=3,maximum=3,event_ordinal=150,event_time=960,event_offset=1757,egraphic=[51,89,127,89])]

def decode(bank,frame):
    indices=bytearray(168);mask=bytearray(168)
    p=struct.unpack_from('<H',bank,(frame-1)*2)[0];x=y=0
    while True:
        v=bank[p];p+=1
        if v==15:break
        x+=v&15;n=v>>4
        if not n:y+=1;x-=12
        for _ in range(n):
            assert 0<=x<12 and 0<=y<14
            indices[y*12+x]=bank[p];mask[y*12+x]=255;p+=1;x+=1
    return bytes(indices),bytes(mask)

def verify(data):
    raw={name:(data/name).read_bytes() for name in PINS}
    for name,pin in PINS.items(): assert b.sha(raw[name])==pin,name
    shp=raw['tyrian.shp'];offs=struct.unpack_from('<13I',shp,2);bank=shp[offs[7]:offs[8]]
    assert len(bank)==32060 and b.fnv(bank)==0x2b63027f74aaa21e
    indices,mask=decode(bank,227)
    assert b.sha(indices)==b.IDENTITY['source_indexed_sha256']
    assert b.sha(mask)==b.IDENTITY['source_coverage_sha256'] and mask.count(255)==45
    assert len(raw['newsh7.shp'])==44079 and b.fnv(raw['newsh7.shp'])==0x6da0d6176a1ddaae
    reader=b.read(b.ROOT,'src/episodes.c').decode()
    fmt={'u8':'B','s8':'b','u16':'H','s16':'h'}
    schema=[(m[2],fmt[m[1]],int(m[3])) for m in re.finditer(r'fread_(u8|s8|u16|s16)_die\(\s*&?enemyDat\[i\]\.(\w+),\s*(\d+),\s*f\)',reader)]
    assert sum(struct.calcsize('<'+str(n)+f) for _,f,n in schema)==77
    lvl=raw['tyrian3.lvl'];p=struct.unpack_from('<i',lvl,2)[0]+8;n=struct.unpack_from('<H',lvl,p)[0];p+=2+2*n
    count=struct.unpack_from('<H',lvl,p)[0];p+=2
    events=[struct.unpack_from('<HBhhbbbB',lvl,p+11*i) for i in range(count)]
    hdt=raw['tyrian.hdt'];result=[]
    for profile in PROFILES:
        e=profile['enemy_offset'];w=profile['weapon_offset'];rec={};pos=e
        assert '%016x'%b.fnv(hdt[e:e+77])==profile['enemy_fnv']
        assert '%016x'%b.fnv(hdt[w:w+80])==profile['weapon_fnv']
        for key,form,n in schema:
            v=list(struct.unpack_from('<'+str(n)+form,hdt,pos));pos+=n*struct.calcsize(form);rec[key]=v[0] if n==1 else v
        assert rec['tur'][0]==profile['weapon'] and rec['freq'][0]==profile['frequency']
        assert rec['shapebank']==3 and rec['egraphic'][:rec['ani']]==profile['egraphic']
        assert list(struct.unpack_from('<8H',hdt,w+58))[:hdt[w+6]]==profile['sg']
        assert hdt[w+3]==profile['multi'] and hdt[w+6]==profile['maximum']
        assert struct.unpack_from('<H',hdt,w+4)[0]==profile['animation']
        ordinal=profile['event_ordinal'];ev=events[ordinal-1]
        assert p+11*(ordinal-1)==profile['event_offset']
        assert ev[:3]==(profile['event_time'],15,profile['record'])
        loads=[]
        for ev in events[:ordinal]:
            if ev[1]==5:loads=[ev[2],ev[3],ev[4],ev[7]]
        assert loads==[3,6,15,8]
        result.append({**profile,'turret_slot':1,'episode':3,'physical_level':1,'actor_shape_bank':3,'preceding_event5_banks':loads,'enemy_sha256':b.sha(hdt[e:e+77]),'weapon_sha256':b.sha(hdt[w:w+80])})
    # This source is also used by records outside this finite scope. Matching227
    # cannot authorize them; confirm their native events and weapon selectors.
    excluded=[]
    for record,weapon,w,ordinal in [(216,38,24228,220),(218,37,24148,222),(134,135,31988,490),(224,37,24148,1072),(225,37,24148,1073)]:
        ev=events[ordinal-1];assert ev[2]==record
        sg=list(struct.unpack_from('<8H',hdt,w+58))[:hdt[w+6]];assert 227 in sg
        assert all(record!=q['record'] and weapon!=q['weapon'] for q in PROFILES)
        excluded.append(dict(record=record,weapon=weapon,event_ordinal=ordinal,event_time=ev[0],sg=sg,eligible=False))
    return dict(status='PASS',scope='static original-source proof only; no live gameplay claim',private_source_sha256=PINS,source227=dict(indexed_sha256=b.sha(indices),coverage_sha256=b.sha(mask),occupied_pixels=45,indices_plus_mask_fnv='%016x'%b.fnv(indices+mask)),profiles=result,excluded_same227=excluded,original_binary_bytes_persisted=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original-data',type=Path,required=True);p.add_argument('--receipt',type=Path)
    a=p.parse_args();report=verify(a.original_data);text=json.dumps(report,indent=2,sort_keys=True)+'\n'
    if a.receipt:a.receipt.write_text(text)
    print(text,end='')
if __name__=='__main__':main()
