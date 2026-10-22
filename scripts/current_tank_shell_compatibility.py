"""Two legacy enemy-role consumers, deliberately outside the global registry."""
import hashlib,json,struct
from package_runtime import contained_file
IDS=(1220146,1220147)
SELECTION='assets/hd/authoring/tank-shell-current.json'
MAPPING='packaging/current-tank-shell-compatibility.json'
HEADER='src/current_tank_shell_payload_pins.h'
ROOT='assets/hd/current-compat/tank-shell'

def name(identity):
    if identity not in IDS:raise ValueError('Unknown tank-shell identity')
    return f'enemy-tank-shell-{identity-1220000}-8.hda'
def fnv(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&((1<<64)-1)
    return f'{value:016x}'
def payload_header(pins):
    text='/* Generated legacy enemy-shell art pins; role/source/geometry stay fixed. */\n#ifndef CURRENT_TANK_SHELL_PAYLOAD_PINS_H\n#define CURRENT_TANK_SHELL_PAYLOAD_PINS_H\n'
    for identity in IDS:text+=f'#define CURRENT_TANK_SHELL_{identity}_PAYLOAD_FNV UINT64_C(0x{pins[identity]})\n'
    return (text+'#endif\n').encode()
def load(root):
    j=json.loads(contained_file(root,MAPPING).read_bytes())
    if set(j)!={'schema','selection','version','files'} or j['schema']!='opentyrian-current-tank-shell-compatibility-v1' or j['selection']!=SELECTION:
        raise ValueError('Invalid tank-shell mapping authority')
    if not isinstance(j['version'],str) or not j['version'] or len(j['version'])>128:raise ValueError('Invalid tank-shell version')
    if not isinstance(j['files'],list) or len(j['files'])!=2:raise ValueError('Expected two tank-shell resources')
    result={};pins={}
    for identity,row in zip(IDS,j['files']):
        source=f'{ROOT}/{name(identity)}';destination=f'assets/gameplay/{name(identity)}'
        if set(row)!={'identity','source_path','destination','sha256'} or type(row['identity']) is not int or row['identity']!=identity or row['source_path']!=source or row['destination']!=destination:
            raise ValueError('Invalid tank-shell consumers')
        p=contained_file(root,source)
        if not p.is_file() or p.stat().st_size!=28+96*112*4:raise ValueError('Invalid tank-shell length')
        raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=row['sha256'] or raw[:28]!=b'HDR1'+struct.pack('<6I',identity,8,12,14,0,0):raise ValueError('Stale/malformed tank-shell output')
        pins[identity]=fnv(raw[28:]);result[destination]=row
    if contained_file(root,HEADER).read_bytes()!=payload_header(pins):raise ValueError('Stale tank-shell payload pins')
    return result
