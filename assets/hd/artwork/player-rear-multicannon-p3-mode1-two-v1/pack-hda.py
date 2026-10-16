#!/usr/bin/env python3
"""Wrap the four immutable derived RGBA payloads; no game data is read."""
from pathlib import Path
import hashlib,json,struct,sys
P=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Usage: python3 pack-hda.py NEW_OUTPUT_DIRECTORY')
O=Path(sys.argv[1]);assert not O.exists(),'Output directory must not exist'
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((P/'components/file-manifest.json').read_text())
for n,h in manifest['files'].items():assert sha((P/'components'/n).read_bytes())==h,n
bindings=json.loads((P/'binding-map.json').read_text());assert len(bindings)==4
seen=set();outputs=[]
for b in bindings:
 sid,d=b['source_id'],b['density'];assert sid in [2,40] and d in [4,8]
 assert (sid,d) not in seen;seen.add((sid,d))
 assert b['key']==1310000+sid and b['filename']==f'rear-multicannon-p1-bank8-{sid}-{d}.hda'
 n=f'output/rear-multi-{sid}-{d}.rgba';raw=(P/'components'/n).read_bytes()
 assert len(raw)==12*14*d*d*4 and sha(raw)==manifest['files'][n]
 data=struct.pack('<4s6I',b'HDR1',b['key'],d,12,14,0,0)+raw
 outputs.append((b,data))
O.mkdir(parents=True)
for b,data in outputs:(O/b['filename']).write_bytes(data)
print('Packed four exact component-derived HDR1 resources.')
