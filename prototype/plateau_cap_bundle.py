"""Finite additive plateau-cap bundle; immutable lower/HDA inputs are read-only."""
from pathlib import Path
import hashlib
import json
import struct
from PIL import Image, ImageDraw
from world_material_bundle import checked_path, finite_slots, fnv64

INVENTORY_SHA256 = '2ed570352eabad2f9e552635bf1602eac47cfcfe5ebe008de26ef2e1503d7f91'
BINDINGS_SHA256 = '65768cfccd83ce505492d8356a8342c1a516d9605806ef55cf8cfa536b9eb582'
ATLAS_SHA256 = 'c5350695a3b35db652c9820d3262cf9d8c54659acf9a9e5203f7a2999de1fe33'
LOWER_SHA256 = '5d62aca342fb5b6038a82bd719086f6e6691107f6e03786511fc65b4b43fccc5'
IDS = [96,97,98,99,100,106,107,108,109,110,118,119,120]
ENABLED = [96,97,99,100,106,107,108,109,110,119,120]
PIXELS = 192*224
ATLAS_BYTES = 768*896*4
PAYLOAD_BYTES = ATLAS_BYTES + 11*PIXELS + PIXELS*4
FILENAME = 'plateau-cap-world-material.pcap'

def sha(data): return hashlib.sha256(data).hexdigest()
def require(test, message):
    if not test: raise ValueError(message)

def lower_records(selected_pack):
    p0=(selected_pack/'ground101-world-material.g101.0').read_bytes()
    p1=(selected_pack/'ground101-world-material.g101.1').read_bytes()
    require(len(p0)==8388608 and len(p1)==7998204, 'Lower transport lengths')
    blob=p0+p1
    require(sha(blob)==LOWER_SHA256, 'Frozen lower bundle mismatch')
    require(blob[:8]==b'G101AT1\0' and struct.unpack_from('<6I',blob,8)==(1,61,768,896,8,16386048),'Lower header')
    payload=memoryview(blob)[764:]; offset=ATLAS_BYTES; records={}
    for i in range(61):
        role,identity,footer=struct.unpack_from('<3I',blob,32+12*i)
        base=bytes(payload[offset:offset+4*PIXELS]); offset+=4*PIXELS
        weights={'primary':bytes(payload[offset:offset+PIXELS])}; offset+=PIXELS
        if footer:
            require(role==201 and identity in (119,120),'Lower footer identity')
            offset+=PIXELS*4
            for key in ['generated_weight','ground_weight']:
                weights[key]=bytes(payload[offset:offset+PIXELS]); offset+=PIXELS
        require((role,identity) not in records,'Duplicate lower record')
        records[role,identity]=(base,weights)
    require(offset==16386048,'Lower layout')
    return records

def build_bundle(package, selected_pack):
    package=Path(package).resolve(); selected_pack=Path(selected_pack).resolve()
    inventory_path=checked_path(package,'inventory.json')
    require(sha(inventory_path.read_bytes())==INVENTORY_SHA256,'Frozen cap inventory mismatch')
    inventory=json.loads(inventory_path.read_text())
    actual={str(p.relative_to(package)) for p in package.rglob('*') if p.is_file() or p.is_symlink()}
    require(actual==set(inventory['files'])|{'inventory.json'},'Unexpected package files')
    for name,digest in inventory['files'].items():
        require(sha(checked_path(package,name).read_bytes())==digest,'Frozen file mismatch: '+name)
    bindings_path=checked_path(package,'contracts/cap-bindings.json')
    require(sha(bindings_path.read_bytes())==BINDINGS_SHA256,'Frozen binding mismatch')
    bindings=json.loads(bindings_path.read_text())
    require(bindings['ids']==IDS and bindings['enabled_ids']==ENABLED and bindings['guard_only_ids']==[98,118] and bindings['mask_revision']==3,'Finite cap inventory')
    require([r['id'] for r in bindings['rows']]==IDS,'Finite source order')
    lower=lower_records(selected_pack)
    def decode(record, mode):
        data_path=checked_path(package,record['path'])
        require(record['decoded_mode']==mode and record['size']==[192,224],'Decoded source contract')
        require(sha(data_path.read_bytes())==record['file_sha256'],'Source PNG identity')
        with Image.open(data_path) as image:
            require(image.size==(192,224),'Source dimensions')
            raw=image.convert(mode).tobytes()
        require(sha(raw)==record['decoded_sha256'],'Decoded source identity')
        return raw
    with Image.open(checked_path(package,'selected/atlas.png')) as image:
        require(image.size==(768,896),'Atlas dimensions')
        atlas=image.convert('RGBA').tobytes()
    require(sha(atlas)==ATLAS_SHA256 and all(v==255 for v in atlas[3::4]),'Opaque cap atlas identity')
    geometry=json.loads((package/'contracts/cap-domain-polygons.json').read_text())
    parts=[atlas]; records=[]; offset=ATLAS_BYTES; base109=None; source_checks=[]
    for row in bindings['rows']:
        ident=row['id']; base=decode(row['base'],'RGBA'); mask=decode(row['cap_weight'],'L')
        expected_header=b'HDR1'+struct.pack('<6I',2010000+ident,8,24,28,0,0)
        require(bytes.fromhex(row['header_hex'])==expected_header,'Source HDA header')
        hda=expected_header+base
        require(sha(hda)==row['source_hda_sha256'],'Source HDA identity')
        require((selected_pack/f'terrain-shapesz-{ident}-8.hda').read_bytes()==hda,'Selected-pack base mismatch: '+str(ident))
        require(sha(base[3::4])==row['original_alpha_sha256'],'Source alpha')
        require(row['bank']=='shapesZ.dat' and row['layer']==1 and row['style']=='NORMAL','Source binding')
        require(bool(any(mask))==row['enabled']==(ident in ENABLED),'Mask enable/guard')
        require(sum(v!=0 for v in mask)==row['nonzero_weight_pixels'] and mask.count(255)==row['full_weight_pixels'],'Mask support counts')
        if ident==109:
            require((201,ident) not in lower and not row['lower_guard_inputs'] and all(v==255 for v in mask),'109 independent baseline')
            base109=base
        else:
            require((201,ident) in lower and lower[201,ident][0]==base,'Shared lower baseline mismatch')
            weights=lower[201,ident][1]
            require(set(weights)=={g['role'] for g in row['lower_guard_inputs']},'Lower guard inventory')
            for guard in row['lower_guard_inputs']:
                lower_mask=decode(guard,'L')
                require(lower_mask==weights[guard['role']],'Accepted lower weight mismatch')
                require(not any(a and b for a,b in zip(mask,lower_mask)),'Lower/footer overlap')
        # Separate geometric protection oracle, not the inverse of lower masks.
        polygon=geometry['polygons'][str(ident)]
        if polygon!='full':
            domain=Image.new('1',(192,224))
            if polygon: ImageDraw.Draw(domain).polygon([tuple(p) for p in polygon],fill=1)
            require(not any(w and not inside for w,inside in zip(mask,domain.getdata())),'Cap outside semantic polygon')
        if ident==108:
            points=geometry['profile_boundaries']['108']['points']
            for y in range(224):
                k=next((k for k in range(len(points)-1) if points[k][1]<=y<=points[k+1][1]),len(points)-2)
                x0,y0=points[k]; x1,y1=points[k+1]
                # Rational boundary oracle avoids the author's numpy interpolation.
                require(not any(mask[y*192+x] and x*(y1-y0)<x0*(y1-y0)+(x1-x0)*(y-y0) for x in range(192)),'108 projecting rim support')
            require(all(mask[y*192+x]==255 for y in range(224) for x in (190,191)),'108 connector')
        if ident==110: require(all(mask[y*192]==255 for y in range(224)),'110 connector')
        if ident in (119,120): require(not any(mask[184*192:]),'Footer protected lower40')
        record={'index':ident,'slot':finite_slots()[201][ident],'mask_offset':offset if row['enabled'] else 0}
        if row['enabled']: parts.append(mask); offset+=PIXELS
        records.append(record)
        source_checks.append({'id':ident,'source_hda_sha256':sha(hda),'cap_weight_sha256':sha(mask),'selected_base_exact':True,'lower_footer_overlap':0,'semantic_domain_checked':True})
    require(base109 is not None,'Missing109 baseline')
    base_offset=offset; parts.append(base109); offset+=len(base109)
    require(offset==PAYLOAD_BYTES,'Finite payload budget')
    header=b'PCAPAT1\0'+struct.pack('<6I',1,13,768,896,8,PAYLOAD_BYTES)
    header+=b''.join(struct.pack('<3I',201,r['index'],int(r['mask_offset']!=0)) for r in records)
    blob=header+b''.join(parts)
    receipt={'file':FILENAME,'sha256':sha(blob),'fnv64':f'{fnv64(blob):016x}','bytes':len(blob),'header_bytes':len(header),'payload_bytes':PAYLOAD_BYTES,'atlas_bytes':ATLAS_BYTES,'mask_bytes':11*PIXELS,'base109_bytes':4*PIXELS,'base109_offset':base_offset,'records':13,'enabled_masks':11,'guard_ids':[98,118],'additional_lookup_bytes':0,'source_inventory_sha256':INVENTORY_SHA256,'cap_bindings_sha256':BINDINGS_SHA256,'atlas_rgba_sha256':ATLAS_SHA256,'lower_bundle_sha256':LOWER_SHA256,'sources':source_checks,'checksum_purpose':'accidental corruption only; not authentication'}
    return blob,records,receipt

def render_header(records,receipt):
    return '\n'.join([
        '/* Generated finite plateau-cap contract; corruption detection, not authentication. */',
        '#define PCAP_BUNDLE_RECORD_COUNT 13u',
        f'#define PCAP_BUNDLE_HEADER_BYTES {receipt["header_bytes"]}u',
        f'#define PCAP_BUNDLE_PAYLOAD_BYTES {receipt["payload_bytes"]}u',
        f'#define PCAP_BUNDLE_FILE_BYTES {receipt["bytes"]}u',
        f'#define PCAP_BASE109_OFFSET {receipt["base109_offset"]}u',
        '#define PCAP_BUNDLE_FNV64 UINT64_C(0x'+receipt['fnv64']+')',
        'static const PCapRecord pcap_records[13]={',
        *[' {'+','.join(str(r[k]) for k in ['index','slot','mask_offset'])+'},' for r in records],
        '};',''])
