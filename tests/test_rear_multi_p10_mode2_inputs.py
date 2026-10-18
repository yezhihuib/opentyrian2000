#!/usr/bin/env python3
"""Optional local authentic-input check. No game bytes are saved or bundled.
Usage: python3 tests/test_rear_multi_p10_mode2_inputs.py /path/to/tyrian2000
Synthetic core/adapter tests remain independent of this original-data check.
"""
from pathlib import Path
import hashlib,re,struct,sys
root=Path(__file__).resolve().parents[1]
if len(sys.argv)!=2:raise SystemExit(__doc__)
data=Path(sys.argv[1]);header=(root/'src/rear_multi_p1_pins.h').read_text()
def fnv(payload):
    value=14695981039346656037
    for byte in payload:value=((value^byte)*1099511628211)&((1<<64)-1)
    return value

def pins(name):
    line=re.search(r'^#define '+name+r' (.*)$',header,re.M)[1]
    return [int(x,0) for x in re.findall(r'UINT64_C\((0x[0-9a-f]+|0)\)',line)]

records=[254,265,255,266,267,256,257,268,269,258,259,270,260,271,261,272,262,273,263,274,275,264]
ids=[39,1,281,282,301,300,40,2,77,182,183,163,164,277,278,41,3,296,297,294,295,298,299,203,222,43,5]
hdt=(data/'tyrian.hdt').read_bytes();start=struct.unpack_from('<i',hdt)[0]+14
for record,pin in zip(records,pins('REAR_P1_RECORD_PINS'),strict=True):
    payload=hdt[start+record*80:start+(record+1)*80]
    assert len(payload)==80 and fnv(payload)==pin,record
payload=hdt[start+274*80:start+275*80]
assert hashlib.sha256(payload).hexdigest()=='7b29db63423a30c98587c8d66e7f725ea66f397e78e342b90e2e50b1d881c4b7'
assert payload==hdt[start+(819+1274-1000)*80:start+(819+1274-1000+1)*80]
port=start+(819+819)*80+10*82
assert hdt[port+31]==2 and struct.unpack_from('<H',hdt,port+32+9*2)[0]==263
assert struct.unpack_from('<H',hdt,port+54+9*2)[0]==274
assert (payload[2],payload[3],payload[6])==(6,8,8)
assert list(struct.unpack_from('<8H',payload,58))==[277,278,295,294,298,299,39,1]
assert list(struct.unpack_from('<8b',payload,26))==[-9,9,6,-6,-2,2,-10,10]
assert list(struct.unpack_from('<8b',payload,34))==[2,2,-6,-6,-9,-9,0,0]
assert list(struct.unpack_from('<8b',payload,42))==[-2,2,4,-4,-4,4,0,0]
assert list(payload[50:58])==[0]*8 and list(payload[10:18])==[2,2,2,2,2,2,1,1]
assert list(payload[18:26])==[255]*8
# Decode the bank using the original12x14 nibble-run semantics, including
# coverage as well as palette indices. No extracted tile is written to disk.
shp=(data/'tyrian.shp').read_bytes();count=struct.unpack_from('<H',shp)[0]
offsets=struct.unpack_from('<'+str(count)+'i',shp,2);bank=shp[offsets[7]:offsets[8]]
assert len(bank)==32060

def decode(raw):
    pos=struct.unpack_from('<H',bank,2*(raw-1))[0];x=y=0
    indices=bytearray(168);coverage=bytearray(168)
    for _ in range(len(bank)):
        assert pos<len(bank)
        code=bank[pos];pos+=1
        if code==15:return indices+coverage
        x+=code&15;run=code>>4
        if not run:y+=1;x-=12
        else:
            for _ in range(run):
                assert pos<len(bank) and 0<=x<12 and 0<=y<14
                indices[y*12+x]=bank[pos];coverage[y*12+x]=255;pos+=1;x+=1
    raise AssertionError('unterminated source tile')

for raw,pin in zip(ids,pins('REAR_P1_SOURCE_PINS'),strict=True):assert fnv(decode(raw))==pin,raw
print('P10 authentic-input PASS:22 full80 record pins,27 decoded source pins; exact274 tuple, eight phases, original coordinates/velocities/damage, and byte-identical1274 alias verified. No gameplay or art-acceptance claim.')
