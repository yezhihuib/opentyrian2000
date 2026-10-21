"""Exact active HUD consumers; historical gameplay bundles remain immutable."""
import hashlib,json,struct
from package_runtime import contained_file

SELECTION='assets/hd/authoring/hud/current.json'
MAPPING='packaging/current-hud-compatibility.json'
HEADER='src/current_hud_payload_pins.h'
NAMES=('gameplay-hud-v1.hda','gameplay-hud-meters-v2.hda','gameplay-hud-font-v1.hda',
       'gameplay-hud-components-v1.hda','gameplay-hud-indicators-v1.hda','gameplay-hud-fixed-text-v1.hda')

def payload_header(pins):
    text='/* Generated HUD material art pins; source/geometry/lookup remain fixed. */\n#ifndef CURRENT_HUD_PAYLOAD_PINS_H\n#define CURRENT_HUD_PAYLOAD_PINS_H\n'
    for key in ('FIRE','ARMOR','ROWS','PAYLOAD'):
        name='HUD_METERS_'+key+'_FNV'
        text+=f'#ifndef {name}\n#define {name} UINT64_C(0x{pins[name]:016x})\n#endif\n'
    return (text+'#endif\n').encode()


def load(root):
    path=contained_file(root,MAPPING)
    if not path.is_file():raise ValueError('Missing current HUD mapping')
    j=json.loads(path.read_bytes())
    if set(j)!={'schema','selection','version','files'} or j['schema']!='opentyrian-current-hud-compatibility-v1' or j['selection']!=SELECTION:
        raise ValueError('Invalid HUD mapping authority')
    if not isinstance(j['version'],str) or not j['version'] or len(j['version'])>128:raise ValueError('Invalid HUD version')
    if not isinstance(j['files'],list) or len(j['files'])!=6:raise ValueError('Expected six HUD resources')
    result={}
    for name,row in zip(NAMES,j['files']):
        if set(row)!={'source_path','destinations','sha256'} or row['source_path']!='assets/hd/shared-ui-v1/'+name or row['destinations']!=['assets/shared-ui/'+name,'assets/gameplay/'+name]:
            raise ValueError('Invalid HUD consumers')
        p=contained_file(root,row['source_path'])
        if not p.is_file() or p.stat().st_size>8*1024*1024 or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Stale/missing HUD consumer: '+name)
        for destination in row['destinations']:result[destination]=dict(source_path=row['source_path'],sha256=row['sha256'])
    meter=(contained_file(root,'assets/hd/shared-ui-v1/gameplay-hud-meters-v2.hda')).read_bytes()
    pins=dict(zip(('HUD_METERS_FIRE_FNV','HUD_METERS_ARMOR_FNV','HUD_METERS_ROWS_FNV','HUD_METERS_LOOKUP_FNV','HUD_METERS_PAYLOAD_FNV'),struct.unpack_from('<5Q',meter,64)))
    header=contained_file(root,HEADER)
    if not header.is_file() or header.read_bytes()!=payload_header(pins):
        raise ValueError('Unrelated HUD payload pins changed')
    return result
