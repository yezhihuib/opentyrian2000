"""Six legacy body consumers; no global IDs or new runtime qualifications.

The generated header is read only by Python build/package consistency checks.
Production C does not include it or enforce these payload values. Existing C
raw-bank qualification and fallback gain no new check or failure condition.
"""
import hashlib,json,struct
from package_runtime import contained_file

IDS=(1260152,1290224,1290243,1290262,1290281,1290300)
SELECTION='assets/hd/authoring/sidekick-body-current.json'
MAPPING='packaging/current-sidekick-body-compatibility.json'
HEADER='src/current_sidekick_body_payload_pins.h'
ROOT='assets/hd/current-compat/sidekick-body'


def name(identity):
    if type(identity) is not int or identity not in IDS:raise ValueError('Unknown sidekick body identity')
    return 'option-marlo-bank9-152-8.hda' if identity==1260152 else f'option-plasma-bank9-{identity-1290000}-8.hda'


def fnv(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&((1<<64)-1)
    return f'{value:016x}'


def payload_header(pins):
    text='/* Generated six-body build/package consistency values; Python checks only.\n * Not included by production C; no runtime payload enforcement is added.\n * Existing raw-bank qualification and fallback remain unchanged. */\n#ifndef CURRENT_SIDEKICK_BODY_PAYLOAD_PINS_H\n#define CURRENT_SIDEKICK_BODY_PAYLOAD_PINS_H\n'
    for identity in IDS:text+=f'#define CURRENT_SIDEKICK_BODY_{identity}_PAYLOAD_FNV UINT64_C(0x{pins[identity]})\n'
    return (text+'#endif\n').encode()


def load(root):
    j=json.loads(contained_file(root,MAPPING).read_bytes())
    if not isinstance(j,dict) or set(j)!={'schema','selection','version','files'} or j['schema']!='opentyrian-current-sidekick-body-compatibility-v1' or j['selection']!=SELECTION:
        raise ValueError('Invalid sidekick body mapping authority')
    if not isinstance(j['version'],str) or not j['version'] or len(j['version'])>128:raise ValueError('Invalid sidekick body version')
    if not isinstance(j['files'],list) or len(j['files'])!=6:raise ValueError('Expected six sidekick body resources')
    result={};pins={}
    for identity,row in zip(IDS,j['files']):
        source=f'{ROOT}/{name(identity)}';destination=f'assets/gameplay/{name(identity)}'
        if not isinstance(row,dict) or set(row)!={'identity','source_path','destination','sha256'} or type(row['identity']) is not int or row['identity']!=identity or row['source_path']!=source or row['destination']!=destination:
            raise ValueError('Invalid sidekick body consumers')
        p=contained_file(root,source)
        if not p.is_file() or p.stat().st_size!=28+96*112*4:raise ValueError('Invalid sidekick body length')
        raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=row['sha256'] or raw[:28]!=b'HDR1'+struct.pack('<6I',identity,8,12,14,0,0):raise ValueError('Stale/malformed sidekick body output')
        pins[identity]=fnv(raw[28:]);result[destination]=row
    if contained_file(root,HEADER).read_bytes()!=payload_header(pins):raise ValueError('Stale sidekick body payload pins')
    return result
