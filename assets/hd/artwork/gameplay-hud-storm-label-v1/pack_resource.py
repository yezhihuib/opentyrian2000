#!/usr/bin/env python3
"""Pack independently authored planes; no original game data is read."""
from pathlib import Path
import hashlib, json, struct
ROOT=Path(__file__).resolve().parent
fnv=lambda b:__import__('functools').reduce(lambda h,v:((h^v)*1099511628211)&((1<<64)-1),b,14695981039346656037)
def build():
    payload=b''.join((ROOT/'generated'/f'storm-heading-{d}x-{kind}.bin').read_bytes() for d in [4,8] for kind in ['index','coverage'])
    assert len(payload)==20000
    header=struct.pack('<4s9I7Q',b'HSI1',1,25,5,2,20000,25,13,230,0,0xe31bdc2ac030d21e,0x72f4faf812d18989,0xd6c645d37088c678,0x14c1441f3d5dc0e2,fnv(payload),0x5e80e83992be2927,0)
    result=header+payload
    assert len(header)==96
    (ROOT/'generated'/'gameplay-hud-storm-label-v1.hda').write_bytes(result)
    receipt={'schema':'storm-label-packed-resource-v1','file_bytes':len(result),'payload_fnv1a64':f'{fnv(payload):016x}','sha256':hashlib.sha256(result).hexdigest(),'payload_order':['4x index2000','4x coverage2000','8x index8000','8x coverage8000'],'source_payloads_included':False,'runtime_ownership':[284,82,309,87]}
    (ROOT/'generated'/'resource.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
if __name__=='__main__':build()
