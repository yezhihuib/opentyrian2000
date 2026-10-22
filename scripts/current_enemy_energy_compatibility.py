"""Seven legacy enemy-energy consumers, deliberately outside the global registry."""
import hashlib,json,struct
from package_runtime import contained_file
IDS=(1110077,1110058,1110182,1110163,1110001,1110183,1110164)
SELECTION='assets/hd/authoring/enemy-energy-current.json'
MAPPING='packaging/current-enemy-energy-compatibility.json'
HEADER='src/current_enemy_energy_payload_pins.h'
ROOT='assets/hd/current-compat/enemy-energy'

# Frozen original bank8 support, not selected art or user-editable geometry.
MASK_POLICY={1110077: ('assets/hd/artwork/enemy-energy-seven-v1/masks/mask-bank8-77.png', 'f3b92a91c9f22d955b0551e6887720916619ddd8a8b4a8405e14009eea91a89d', '000000000000000000000000000000000000000001000000000001100000000011110000000011110000000011110000000011110000000011110000000011110000000011110000000011110000000001100000'), 1110058: ('assets/hd/artwork/enemy-energy-seven-v1/masks/mask-bank8-58.png', 'a67b2e1eb2a27c81101a84a89bb4cad7a4e8ecc87a82e19d829f6001f8a8ad94', '000001100000000011110000000011110000000011110000000011110000000011110000000011110000000011110000000011110000000001100000000001000000000000000000000000000000000000000000'), 1110182: ('assets/hd/artwork/enemy-energy-seven-v1/masks/mask-bank8-182.png', 'e1f53e947aa1bd9523d4a5b5c57bfec0a5abd70efb9b6650769b232b101497ff', '000000000000000000000000000000000000000000000010000000001100000000011100000001111000000011110000000111110000001111100000111111000000111110000000111100000000111100000000'), 1110163: ('assets/hd/artwork/enemy-energy-seven-v1/masks/mask-bank8-163.png', 'f5899583e24dfed722f9e726a1df0afc850e390e4c8e49799ff16aed492489c0', '111100000000111100000000111110000000111111000000001111100000000111110000000011110000000001111000000000011100000000001100000000000010000000000000000000000000000000000000'), 1110001: ('assets/hd/artwork/enemy-energy-seven-v1/masks/mask-bank8-1.png', '71a9fbb28449fc06350fdda3f1bb92f86a929bb3512b1e1a50c1b8fdebe330c1', '000000000000000000000000000000000000000000000000000111111110001111111111011111111111000111111110000000000000000000000000000000000000000000000000000000000000000000000000'), 1110183: ('assets/hd/artwork/enemy-energy-seven-v1/masks/mask-bank8-183.png', 'e8129b810c6ba00c6592c49a08ab41c6d3109fa148237b53b12fb36a0d1dd956', '000000000000000000000000000000000000010000000000001100000000001110000000000111100000000011110000000011111000000001111100000000111111000000011111000000001111000000001111'), 1110164: ('assets/hd/artwork/enemy-energy-seven-v1/masks/mask-bank8-164.png', '46ec70c004b45dc457911d26ae947992140a07a2d5c404b385622c26e113b510', '000000001111000000001111000000011111000000111111000001111100000011111000000011110000000111100000001110000000001100000000010000000000000000000000000000000000000000000000')}

def validate_support(identity,payload):
    support=MASK_POLICY[identity][2]
    if len(payload)!=96*112*4:raise ValueError('Invalid energy RGBA length')
    for y in range(112):
        for x in range(96):
            if payload[(y*96+x)*4+3] and support[(y//8)*12+x//8]!='1':
                raise ValueError('Energy alpha extends beyond original source support')

def name(identity):
    if identity not in IDS:raise ValueError('Unknown enemy-energy identity')
    return f'enemy-energy-{identity-1110000}-8.hda'
def fnv(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&((1<<64)-1)
    return f'{value:016x}'
def payload_header(pins):
    text='/* Generated legacy enemy-energy art pins; role/source/geometry stay fixed. */\n#ifndef CURRENT_ENEMY_ENERGY_PAYLOAD_PINS_H\n#define CURRENT_ENEMY_ENERGY_PAYLOAD_PINS_H\n'
    for identity in IDS:text+=f'#define CURRENT_ENEMY_ENERGY_{identity}_PAYLOAD_FNV UINT64_C(0x{pins[identity]})\n'
    return (text+'#endif\n').encode()
def load(root):
    j=json.loads(contained_file(root,MAPPING).read_bytes())
    if set(j)!={'schema','selection','version','files'} or j['schema']!='opentyrian-current-enemy-energy-compatibility-v1' or j['selection']!=SELECTION:
        raise ValueError('Invalid enemy-energy mapping authority')
    if not isinstance(j['version'],str) or not j['version'] or len(j['version'])>128:raise ValueError('Invalid enemy-energy version')
    if not isinstance(j['files'],list) or len(j['files'])!=7:raise ValueError('Expected seven enemy-energy resources')
    result={};pins={}
    for identity,row in zip(IDS,j['files']):
        source=f'{ROOT}/{name(identity)}';destination=f'assets/gameplay/{name(identity)}'
        if set(row)!={'identity','source_path','destination','sha256'} or type(row['identity']) is not int or row['identity']!=identity or row['source_path']!=source or row['destination']!=destination:
            raise ValueError('Invalid enemy-energy consumers')
        p=contained_file(root,source)
        if not p.is_file() or p.stat().st_size!=28+96*112*4:raise ValueError('Invalid enemy-energy length')
        raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=row['sha256'] or raw[:28]!=b'HDR1'+struct.pack('<6I',identity,8,12,14,0,0):raise ValueError('Stale/malformed enemy-energy output')
        validate_support(identity,raw[28:])
        pins[identity]=fnv(raw[28:]);result[destination]=row
    if contained_file(root,HEADER).read_bytes()!=payload_header(pins):raise ValueError('Stale enemy-energy payload pins')
    return result
