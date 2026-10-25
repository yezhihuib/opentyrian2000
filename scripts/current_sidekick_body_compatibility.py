"""Finite six-body, Charge and Mint/Front authoring compatibility families.

No global IDs or new runtime qualifications. The original six-body API stays fixed.

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


# Independent Charge subfamily. None of these constants changes the six-body API.
CHARGE_SPRITES=(258,259,260,277,278,279,296,297,298)
CHARGE_IDS=tuple(1450000+sprite for sprite in CHARGE_SPRITES)
CHARGE_SELECTION='assets/hd/authoring/charge-body-current.json'
CHARGE_MAPPING='packaging/current-charge-body-compatibility.json'
CHARGE_ROOT='assets/hd/current-compat/charge-body'
CHARGE_INPUT_ROOT='authoring-inputs/charge-body-current'
CHARGE_AUTHORING_SCHEMA='opentyrian-current-charge-body-authoring-v1'
CHARGE_CANDIDATE_SCHEMA='opentyrian-current-charge-body-candidate-v1'


def charge_name(identity):
    if type(identity) is not int or identity not in CHARGE_IDS:
        raise ValueError('Unknown Charge body identity')
    return f'option-charge-bank9-{identity-1450000}-8.hda'


def charge_png(identity):
    charge_name(identity)
    return f'{CHARGE_INPUT_ROOT}/derived/bank9-id{identity-1450000}.png'


def _charge_parse(raw):
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Duplicate Charge JSON key: '+key)
            result[key]=value
        return result
    def invalid(value):raise ValueError('Non-finite Charge JSON number: '+value)
    if len(raw)>128*1024:raise ValueError('Oversize Charge JSON')
    return json.loads(raw,object_pairs_hook=unique,parse_constant=invalid)


def _charge_read(root,name,limit=16*1024*1024):
    import stat
    p=contained_file(root,name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode) or p.stat().st_size>limit:
        raise ValueError('Missing/oversize regular Charge input: '+name)
    return p.read_bytes()


def _charge_sha(raw):return hashlib.sha256(raw).hexdigest()


def _charge_hash(value):
    import re
    return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None


def charge_selection(root,raw,candidate=False):
    """Parse an explicit candidate OR a fully declared installed selection.

    Candidate documents cannot provide derived frames or hashes. Installed
    documents cannot omit them. No changed-master heuristic switches contracts.
    """
    j=_charge_parse(raw)
    expected={'schema','version','master','recipe'}| (set() if candidate else {'resources'})
    schema=CHARGE_CANDIDATE_SCHEMA if candidate else CHARGE_AUTHORING_SCHEMA
    if not isinstance(j,dict) or set(j)!=expected or j['schema']!=schema:
        raise ValueError('Invalid Charge candidate/installed schema or fields')
    if not isinstance(j['version'],str) or not 1<=len(j['version'])<=128:
        raise ValueError('Invalid Charge version')
    for key,path_key,hash_key,suffix in (('master','source_png','source_sha256','.png'),('recipe','path','sha256','.json')):
        record=j[key]
        if not isinstance(record,dict) or set(record)!={path_key,hash_key} or not _charge_hash(record[hash_key]):
            raise ValueError('Invalid Charge '+key+' record')
        name=record[path_key]
        if not isinstance(name,str) or not name.startswith('authoring-inputs/') or not name.endswith(suffix) or name.startswith(CHARGE_INPUT_ROOT+'/derived/'):
            raise ValueError('Expected independent Charge '+key+' input')
        from current_plasma_projectile_compatibility import generated_paths as plasma_generated_paths
        if name.casefold() in {p.casefold() for p in plasma_generated_paths()}:
            raise ValueError('Generated Plasma piece is not an independent Charge input')
        if _charge_sha(_charge_read(root,name))!=record[hash_key]:raise ValueError('Selected Charge '+key+' changed')
    if not candidate:
        if not isinstance(j['resources'],list) or len(j['resources'])!=9:raise ValueError('Expected nine derived Charge frames')
        for identity,row in zip(CHARGE_IDS,j['resources']):
            if not isinstance(row,dict) or set(row)!={'identity','source_png','source_sha256'} or type(row['identity']) is not int or row['identity']!=identity or row['source_png']!=charge_png(identity) or not _charge_hash(row['source_sha256']):
                raise ValueError('Invalid derived Charge identity/path/order/hash')
    return j


def _charge_image(raw):
    """Strict RGBA8 PNG decoding: bounded, CRC checked, no animation/trailing data."""
    import io,zlib
    from PIL import Image
    if len(raw)>16*1024*1024 or raw[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Expected bounded Charge PNG')
    offset=8;kinds=[]
    while offset<len(raw):
        if offset+12>len(raw):raise ValueError('Truncated Charge PNG chunk')
        length=struct.unpack('>I',raw[offset:offset+4])[0];end=offset+12+length
        if end>len(raw):raise ValueError('Truncated Charge PNG data')
        kind=raw[offset+4:offset+8];body=raw[offset+8:end-4]
        if zlib.crc32(kind+body)&0xffffffff!=struct.unpack('>I',raw[end-4:end])[0]:raise ValueError('Charge PNG CRC mismatch')
        if not kinds and (kind!=b'IHDR' or body!=struct.pack('>IIBBBBB',96,112,8,6,0,0,0)):
            raise ValueError('Expected 96x112 straight RGBA8 Charge PNG')
        kinds.append(kind);offset=end
        if kind==b'IEND':
            if length or offset!=len(raw):raise ValueError('Trailing Charge PNG data')
            break
    if kinds.count(b'IHDR')!=1 or kinds.count(b'IEND')!=1 or b'acTL' in kinds:raise ValueError('Expected one complete Charge PNG')
    try:
        with Image.open(io.BytesIO(raw)) as image:image.verify()
        with Image.open(io.BytesIO(raw)) as image:
            if image.format!='PNG' or image.mode!='RGBA' or image.size!=(96,112) or getattr(image,'n_frames',1)!=1:
                raise ValueError('Expected single 96x112 RGBA Charge PNG')
            return image.copy()
    except OSError as exc:raise ValueError('Malformed Charge PNG') from exc


def _charge_recipe(raw,master_sha):
    """Data-only bounded effect controls; identities/geometry never become inputs."""
    import math
    j=_charge_parse(raw)
    keys={'schema','master_sha256','identity','provenance_only','logical_size','scale_factor','output_size','anchor','core_logical_region_xyxy','core_phase_rgb_add','highlight_target_rgb','highlight_strength','highlight_blur_radius_px','spark_palette_rgb','spark_footprint','sprite_ids','gr','highlight_control_points','highlight_weight_normalizer','spark_control_points','initial_draw_slot_order','technical_version','spark_fix_scope'}
    if not isinstance(j,dict) or set(j)!=keys:raise ValueError('Invalid Charge recipe fields')
    fixed={'schema':'charge-single-master-recipe-v1','master_sha256':master_sha,'identity':{'option':3,'bank':9,'body':'Charge Cannon launcher'},'logical_size':[12,14],'scale_factor':8,'output_size':[96,112],'anchor':[0,0],'core_logical_region_xyxy':[3,6,9,8],'sprite_ids':[[258,259,260],[277,278,279],[296,297,298]],'gr':[258,258,258,277,277,277,296,296,296],'initial_draw_slot_order':[1,2,3,4,5,6,7,8,0]}
    # Canonical JSON distinguishes booleans/floats from integer identity fields.
    for key,value in fixed.items():
        if json.dumps(j[key],sort_keys=True)!=json.dumps(value,sort_keys=True):raise ValueError('Fixed Charge recipe identity/geometry changed: '+key)
    p=j['provenance_only']
    if not isinstance(p,dict) or set(p)!={'generated_v2_sha256','note'} or not _charge_hash(p['generated_v2_sha256']) or not isinstance(p['note'],str) or len(p['note'])>512:raise ValueError('Invalid provenance-only Charge metadata')
    for key in ('technical_version','spark_fix_scope'):
        if not isinstance(j[key],str) or not 1<=len(j[key])<=512:raise ValueError('Invalid Charge recipe metadata')
    def number(value,low,high):return type(value) in (int,float) and math.isfinite(value) and low<=value<=high
    def rgb(value):return isinstance(value,list) and len(value)==3 and all(type(v) is int and 0<=v<=255 for v in value)
    if not rgb(j['highlight_target_rgb']) or not isinstance(j['core_phase_rgb_add'],list) or len(j['core_phase_rgb_add'])!=3 or not all(rgb(v) for v in j['core_phase_rgb_add']) or j['core_phase_rgb_add'][0]!=[0,0,0]:raise ValueError('Invalid Charge core/highlight colors')
    for key,low,high in (('highlight_strength',0,1),('highlight_blur_radius_px',0,4),('highlight_weight_normalizer',0.001,10000)):
        if not number(j[key],low,high):raise ValueError('Invalid bounded Charge effect value: '+key)
    palette=j['spark_palette_rgb']
    if not isinstance(palette,dict) or set(palette)!={'151','154','157'} or not all(rgb(v) for v in palette.values()):raise ValueError('Invalid Charge spark palette')
    footprint=j['spark_footprint']
    if not isinstance(footprint,list) or not 1<=len(footprint)<=25:raise ValueError('Invalid Charge spark footprint')
    seen=set()
    for row in footprint:
        if not isinstance(row,list) or len(row)!=3 or any(type(v) is not int for v in row) or not -2<=row[0]<=2 or not -2<=row[1]<=2 or not 1<=row[2]<=255 or tuple(row[:2]) in seen:raise ValueError('Invalid Charge spark footprint point')
        seen.add(tuple(row[:2]))
    for key in ('highlight_control_points','spark_control_points'):
        phases=j[key]
        if not isinstance(phases,list) or len(phases)!=3:raise ValueError('Invalid Charge effect phase count')
        for phase in phases:
            if not isinstance(phase,list) or not (len(phase)==4 if key=='spark_control_points' else 1<=len(phase)<=168):raise ValueError('Invalid Charge effect point count')
            seen=set()
            for row in phase:
                if not isinstance(row,list) or len(row)!=3 or type(row[0]) is not int or type(row[1]) is not int or not 0<=row[0]<12 or not 0<=row[1]<14 or tuple(row[:2]) in seen:raise ValueError('Invalid Charge effect coordinate')
                seen.add(tuple(row[:2]))
                if key=='spark_control_points':
                    if type(row[2]) is not int or str(row[2]) not in palette:raise ValueError('Invalid Charge spark palette index')
                elif not number(row[2],0,j['highlight_weight_normalizer']):raise ValueError('Invalid Charge highlight weight')
    return j


def charge_generate(root,raw,candidate=False):
    """Recompute all nine states. Installed inputs must prove every derived PNG."""
    import io
    from current_charge_body_recipe import generate_frames
    selected=charge_selection(root,raw,candidate)
    master=_charge_image(_charge_read(root,selected['master']['source_png']))
    for y in range(112):
        for x in range(96):
            pixel=master.getpixel((x,y))
            if (not pixel[3] and pixel!=(0,0,0,0)) or ((x in (0,95) or y in (0,111)) and pixel[3]):
                raise ValueError('Charge master must have transparent border and clean transparent RGB')
    recipe=_charge_recipe(_charge_read(root,selected['recipe']['path'],128*1024),selected['master']['source_sha256'])
    try:frames=generate_frames(master,recipe)
    except (AssertionError,KeyError,IndexError,TypeError) as exc:raise ValueError('Charge recipe invariant failed') from exc
    if set(frames)!={(p,c) for p in range(3) for c in range(3)}:raise ValueError('Unexpected Charge generated states')
    pngs={};blobs={};rows=[]
    for ordinal,identity in enumerate(CHARGE_IDS):
        frame=frames[divmod(ordinal,3)]
        if frame.mode!='RGBA' or frame.size!=(96,112):raise ValueError('Invalid generated Charge geometry')
        pixels=frame.tobytes();png_path=charge_png(identity)
        if candidate:
            stream=io.BytesIO();frame.save(stream,format='PNG',optimize=False);png=stream.getvalue()
        else:
            row=selected['resources'][ordinal];png=_charge_read(root,png_path)
            if _charge_sha(png)!=row['source_sha256'] or _charge_image(png).tobytes()!=pixels:
                raise ValueError('Derived Charge PNG does not match master+recipe: '+png_path)
        pngs[png_path]=png;rows.append(dict(identity=identity,source_png=png_path,source_sha256=_charge_sha(png)))
        blobs[identity]=b'HDR1'+struct.pack('<6I',identity,8,12,14,0,0)+pixels
    installed=dict(selected,schema=CHARGE_AUTHORING_SCHEMA,resources=rows)
    return installed,pngs,blobs


def charge_input_paths(root):
    """Finite twelve-path closure, never a recursive artwork/provenance glob."""
    selected=charge_selection(root,_charge_read(root,CHARGE_SELECTION))
    paths={CHARGE_SELECTION,selected['master']['source_png'],selected['recipe']['path']}|{row['source_png'] for row in selected['resources']}
    if len(paths)!=12:raise ValueError('Charge input path collision')
    return paths


def charge_load(root):
    selected,_,blobs=charge_generate(root,_charge_read(root,CHARGE_SELECTION))
    mapping=_charge_parse(_charge_read(root,CHARGE_MAPPING))
    rows=[];result={}
    for identity in CHARGE_IDS:
        source=CHARGE_ROOT+'/'+charge_name(identity);destination='assets/gameplay/'+charge_name(identity)
        blob=blobs[identity]
        if _charge_read(root,source)!=blob:raise ValueError('Charge HDA does not match master+recipe: '+source)
        row=dict(identity=identity,source_path=source,destination=destination,sha256=_charge_sha(blob))
        rows.append(row);result[destination]=row
    expected=dict(schema='opentyrian-current-charge-body-compatibility-v1',selection=CHARGE_SELECTION,version=selected['version'],files=rows)
    if json.dumps(mapping,sort_keys=True)!=json.dumps(expected,sort_keys=True):raise ValueError('Invalid/stale Charge compatibility mapping')
    return result


def authoring_input_fingerprints(root):
    """Bind finite Charge, Mint/Front and Plasma inputs/tools in legacy plans."""
    paths=independent_input_paths(root)
    paths|={'scripts/current_charge_body_recipe.py','scripts/current_sidekick_body_compatibility.py','scripts/build_current_sidekick_body.py',
            'scripts/current_plasma_projectile_compatibility.py','scripts/build_current_plasma_projectile.py',
            'scripts/current_front_multi_compatibility.py','scripts/build_current_front_multi.py',
            'scripts/current_enemy_orb_compatibility.py','scripts/build_current_enemy_orb.py',
            'scripts/build_newshf_hd.py','scripts/check_newshf_phase_a.py',
            'scripts/current_newshf_compatibility.py','scripts/build_current_newshf.py'}
    return {name:_charge_sha(_charge_read(root,name)) for name in sorted(paths)}


# Independent Mint/FrontBlaster subfamily. No six-body or Charge API changes.
# These fixed identities describe existing consumers, never renderer grants.
MF_IDS=(1270112,1270131,1270150,1280083)
MF_SELECTION='assets/hd/authoring/mint-front-body-current.json'
MF_MAPPING='packaging/current-mint-front-body-compatibility.json'
MF_ROOT='assets/hd/current-compat/mint-front-body'
MF_SCHEMA='opentyrian-current-mint-front-body-authoring-v1'


def mf_name(identity):
    if type(identity) is not int or identity not in MF_IDS:
        raise ValueError('Unknown Mint/Front body identity')
    return ('option-frontblaster-bank10-83-8.hda' if identity==1280083 else
            f'option-mint-bank9-{identity-1270000}-8.hda')


def mf_parse(raw):
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('Duplicate Mint/Front JSON key: '+key)
            result[key]=value
        return result
    def invalid(value):raise ValueError('Non-finite Mint/Front JSON number: '+value)
    if len(raw)>128*1024:raise ValueError('Oversize Mint/Front JSON')
    return json.loads(raw,object_pairs_hook=unique,parse_constant=invalid)


def mf_read(root,name,limit=16*1024*1024):
    import stat
    from current_craft267_compatibility import path
    p=path(root,name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode) or p.stat().st_size>limit:
        raise ValueError('Missing/oversize regular Mint/Front input: '+name)
    return p.read_bytes()


def mf_selection(root,raw):
    selected=mf_parse(raw)
    if not isinstance(selected,dict) or set(selected)!={'schema','version','resources'} or selected['schema']!=MF_SCHEMA:
        raise ValueError('Invalid Mint/Front selection schema/fields')
    if not isinstance(selected['version'],str) or not 1<=len(selected['version'])<=128:
        raise ValueError('Invalid Mint/Front version')
    if not isinstance(selected['resources'],list) or len(selected['resources'])!=4:
        raise ValueError('Expected four independent Mint/Front sources')
    paths=set()
    for identity,row in zip(MF_IDS,selected['resources']):
        if not isinstance(row,dict) or set(row)!={'identity','source_png','source_sha256'} or type(row['identity']) is not int or row['identity']!=identity:
            raise ValueError('Invalid Mint/Front identity/fields/order')
        source=row['source_png']
        if not isinstance(source,str) or not source.startswith('authoring-inputs/') or not source.endswith('.png') or not _charge_hash(row['source_sha256']):
            raise ValueError('Expected independent authoring-inputs Mint/Front PNG and SHA256')
        # Charge's nine derived PNGs are generated outputs, never editable
        # Mint/Front sources. Keep this exclusion finite, not a directory glob.
        if source.casefold() in {charge_png(i).casefold() for i in CHARGE_IDS}:
            raise ValueError('Generated Charge frame is not an independent Mint/Front source')
        from current_plasma_projectile_compatibility import generated_paths as plasma_generated_paths
        if source.casefold() in {name.casefold() for name in plasma_generated_paths()}:
            raise ValueError('Generated Plasma piece is not an independent Mint/Front source')
        if source.casefold() in paths:raise ValueError('Mint/Front sources must have four independent paths')
        paths.add(source.casefold())
        if _charge_sha(mf_read(root,source))!=row['source_sha256']:
            raise ValueError('Selected Mint/Front source changed')
    return selected


def mf_image(raw,identity):
    """Bounded complete straight RGBA8 PNG; never resample or merge phases."""
    import io,zlib
    from PIL import Image
    mf_name(identity)
    size=(192,224) if identity==1280083 else (96,112)
    if len(raw)>16*1024*1024 or raw[:8]!=b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected bounded Mint/Front PNG')
    offset=8;kinds=[]
    while offset<len(raw):
        if offset+12>len(raw):raise ValueError('Truncated Mint/Front PNG chunk')
        length=struct.unpack('>I',raw[offset:offset+4])[0];end=offset+12+length
        if end>len(raw):raise ValueError('Truncated Mint/Front PNG data')
        kind=raw[offset+4:offset+8];body=raw[offset+8:end-4]
        if zlib.crc32(kind+body)&0xffffffff!=struct.unpack('>I',raw[end-4:end])[0]:
            raise ValueError('Mint/Front PNG CRC mismatch')
        if not kinds and (kind!=b'IHDR' or body!=struct.pack('>IIBBBBB',*size,8,6,0,0,0)):
            raise ValueError('Unexpected Mint/Front PNG dimensions/straight RGBA8 encoding')
        if kind in (b'acTL',b'fcTL',b'fdAT') or (kind not in (b'IHDR',b'PLTE',b'IDAT',b'IEND') and not kind[0]&32):
            raise ValueError('Animated/unknown critical Mint/Front PNG chunk')
        kinds.append(kind);offset=end
        if kind==b'IEND':
            if length or offset!=len(raw):raise ValueError('Trailing Mint/Front PNG data')
            break
    if kinds.count(b'IHDR')!=1 or kinds.count(b'IEND')!=1 or b'IDAT' not in kinds:
        raise ValueError('Expected complete Mint/Front PNG')
    try:
        with Image.open(io.BytesIO(raw)) as image:image.verify()
        with Image.open(io.BytesIO(raw)) as image:
            if image.format!='PNG' or image.mode!='RGBA' or image.size!=size or getattr(image,'n_frames',1)!=1:
                raise ValueError('Expected single straight RGBA Mint/Front PNG')
            return image.copy()
    except (OSError,SyntaxError) as exc:raise ValueError('Malformed Mint/Front PNG') from exc


def mf_generate(root,raw):
    selected=mf_selection(root,raw);blobs={}
    for row in selected['resources']:
        identity=row['identity'];image=mf_image(mf_read(root,row['source_png']),identity)
        width,height=(24,28) if identity==1280083 else (12,14)
        blobs[identity]=b'HDR1'+struct.pack('<6I',identity,8,width,height,0,0)+image.tobytes()
    return selected,blobs


def mf_input_paths(root):
    selected=mf_selection(root,mf_read(root,MF_SELECTION,128*1024))
    return {MF_SELECTION}|{row['source_png'] for row in selected['resources']}


def mf_load(root):
    selected,blobs=mf_generate(root,mf_read(root,MF_SELECTION,128*1024))
    mapping=mf_parse(mf_read(root,MF_MAPPING,128*1024));rows=[];result={}
    for identity,blob in blobs.items():
        source=MF_ROOT+'/'+mf_name(identity);destination='assets/gameplay/'+mf_name(identity)
        if mf_read(root,source)!=blob:raise ValueError('Mint/Front HDA does not match selected PNG: '+source)
        row=dict(identity=identity,source_path=source,destination=destination,sha256=_charge_sha(blob))
        rows.append(row);result[destination]=row
    expected=dict(schema='opentyrian-current-mint-front-body-compatibility-v1',selection=MF_SELECTION,version=selected['version'],files=rows)
    if json.dumps(mapping,sort_keys=True)!=json.dumps(expected,sort_keys=True):
        raise ValueError('Invalid/stale Mint/Front compatibility mapping')
    return result


def independent_input_paths(root):
    """Finite current dependency closure shared by every authoring workflow."""
    from current_plasma_projectile_compatibility import input_paths as plasma_input_paths, MAPPING as PLASMA_MAPPING
    from current_front_multi_compatibility import input_paths as front_multi_input_paths, MAPPING as FRONT_MULTI_MAPPING
    from current_enemy_orb_compatibility import input_paths as orb_input_paths, MAPPING as ORB_MAPPING
    from current_newshf_compatibility import input_paths as newshf_input_paths
    from build_enemy_protron_p09 import DIRECTORY as P09, MASTER as P09_MASTER
    from current_protron_compatibility import input_paths as protron_input_paths, MAPPING as PROTRON_MAPPING
    p09={P09_MASTER}|{P09+'/'+n for n in ('identity.json','recipe.json','source227.png','enemy-protron-p09-227-8.hda')}
    from current_sonic_compatibility import input_paths as sonic_input_paths, MAPPING as SONIC_MAPPING
    from current_guided_compatibility import input_paths as guided_input_paths, MAPPING as GUIDED_MAPPING
    from current_mint27_compatibility import input_paths as mint27_input_paths, MAPPING as MINT27_MAPPING
    from current_missile_compatibility import input_paths as missile_input_paths, MAPPING as MISSILE_MAPPING
    from current_rear_p7_compatibility import input_paths as rear_p7_input_paths, MAPPING as REAR_P7_MAPPING
    from current_rear39_compatibility import input_paths as rear39_input_paths, MAPPING as REAR39_MAPPING
    from current_rear1_compatibility import input_paths as rear1_input_paths, MAPPING as REAR1_MAPPING
    return rear1_input_paths(root)|{REAR1_MAPPING}|rear39_input_paths(root)|{REAR39_MAPPING}|rear_p7_input_paths(root)|{REAR_P7_MAPPING}|missile_input_paths(root)|{MISSILE_MAPPING}|mint27_input_paths(root)|{MINT27_MAPPING}|guided_input_paths(root)|{GUIDED_MAPPING}|sonic_input_paths(root)|{SONIC_MAPPING}|protron_input_paths(root)|{PROTRON_MAPPING}|p09|newshf_input_paths(root)|charge_input_paths(root)|mf_input_paths(root)|plasma_input_paths(root)|front_multi_input_paths(root)|orb_input_paths(root)|{CHARGE_MAPPING,MF_MAPPING,PLASMA_MAPPING,FRONT_MULTI_MAPPING,ORB_MAPPING}
