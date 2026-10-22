#!/usr/bin/env python3
'Optional local authentic-input check. No game bytes are saved or bundled.\nUsage: python3 tests/test_rear_multi_p11_mode1_inputs.py /path/to/tyrian2000\nSynthetic core/adapter tests remain independent of this original-data check.'
if __name__ != "__main__":
    from cli_test_support import cli_suite

    def load_tests(loader, tests, pattern):
        return cli_suite(__file__)
else:
    #!/usr/bin/env python3
    """Optional local authentic-input check. No game bytes are saved or bundled.
    Usage: python3 tests/test_rear_multi_p11_mode1_inputs.py /path/to/tyrian2000
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
    payload=hdt[start+264*80:start+265*80]
    assert fnv(payload)==0x88af50784f345394
    assert hashlib.sha256(payload).hexdigest()=='b1f371caa5d050fc279aa63b3dcccaefff3a1c00c7f8351edc5cccea83a43adb'
    assert payload==hdt[start+(819+1264-1000)*80:start+(819+1264-1000+1)*80]
    port=start+(819+819)*80+10*82
    assert hdt[port+31]==2 and struct.unpack_from('<H',hdt,port+32+10*2)[0]==264
    assert struct.unpack_from('<H',hdt,port+54+10*2)[0]==275
    assert (payload[2],payload[3],payload[6])==(6,6,6)
    assert list(struct.unpack_from('<6H',payload,58))==[277,278,297,296,43,5]
    assert list(struct.unpack_from('<6b',payload,26))==[-9,9,9,-9,-10,10]
    assert list(struct.unpack_from('<6b',payload,34))==[2,2,-2,-2,0,0]
    assert list(struct.unpack_from('<6b',payload,42))==[-2,2,2,-2,0,0]
    assert list(payload[50:56])==[0]*6 and list(payload[10:16])==[2,2,2,2,5,5]
    assert list(payload[18:24])==[255]*6
    # Slots7/8 are inactive, but their nonzero data still belongs to the full80
    # record stamp. An active-six-only or zero-filled-tail digest is insufficient.
    for offset,width in [(10,1),(18,1),(26,1),(34,1),(42,1),(50,1),(58,2)]:
        tail=payload[offset+6*width:offset+8*width]
        assert any(tail),offset
        altered=payload[:offset+6*width]+bytes(2*width)+payload[offset+8*width:]
        assert len(altered)==80 and fnv(altered)!=0x88af50784f345394
    # Ensure every byte participates in authentication, including the inactive tails.
    for offset in range(80):
        altered=payload[:offset]+bytes([payload[offset]^1])+payload[offset+1:]
        assert fnv(altered)!=0x88af50784f345394,offset
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

    assert pins('REAR_P1_SOURCE_PINS')[-2:]==[0x5f90f1067e584a9c,0x10e31f80f155aa82]
    for raw,pin in zip(ids,pins('REAR_P1_SOURCE_PINS'),strict=True):assert fnv(decode(raw))==pin,raw
    print('P11 FIRST authentic-input PASS:22 full80 record pins,27 decoded source pins; exact264 tuple, six phases, original coordinates/velocities/damage, authenticated nonzero inactive7/8 tails, and byte-identical1264 alias verified. No gameplay or art-acceptance claim.')
