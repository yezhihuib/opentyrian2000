"""One canonical data-only Rear281 geometry -> twenty role131 transports; no eligibility changes."""
import hashlib
import base64
import subprocess
import tempfile
import json
import math
import re
import stat
import struct

from current_craft267_compatibility import path

IDS = (1310281, 1310282, 1310300, 1310301, 1310277, 1310278, 1310296, 1310297, 1310298, 1310299)
SELECTORS = (281,)
PAIRS = tuple((identity, density) for density in (4,8) for identity in IDS)
SELECTION = 'assets/hd/authoring/rear281-current.json'
MAPPING = 'packaging/current-rear281-compatibility.json'
HEADER = 'src/current_rear_multi_payload_pins.h'
ROOT = 'assets/hd/current-compat/rear281'
INPUT_ROOT = 'authoring-inputs/rear281-current'
SCHEMA = 'opentyrian-current-rear281-authoring-v1'
CANDIDATE_SCHEMA = 'opentyrian-current-rear281-candidate-v1'
RECIPE = {'identity': {'source_bank': 8, 'source_id': 281, 'role': 131, 'key': 1310281}, 'canvas': {'logical_width': 12, 'logical_height': 14, 'anchor': [0, 0], 'svg_width': 96, 'svg_height': 112, 'densities': [4, 8]}, 'coverage': {'stroke_count': 32, 'outer_stroke_width': 0.6, 'minimum_factor': 0.62, 'factor_range': 0.38, 'round_linejoin': True}, 'derived': {'282': 'flipX281', '300': 'flipY281', '301': 'rotate180281', '277': 'lower-over-upper281-offset0,4', '278': 'lower-over-upper282-offset0,4', '296': 'flipY-finished277', '297': 'flipY-finished278', '298': 'x=y,y=14d-1-x-from-finished277', '299': 'x=12d-1-y,y=14d-1-x-from-finished277'}, 'compositing': 'encoded-rgb-exact-rational-source-over-half-up', 'occupied_clipping_allowed': False, 'schema': 'rear281-fixed-recipe-v1'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate Rear281 JSON key: ' + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('Non-finite Rear281 JSON number: ' + value)

    if len(raw) > 128 * 1024:
        raise ValueError('Oversize Rear281 JSON')
    text=raw.decode('utf-8',errors='strict')
    if '\x00' in text: raise ValueError('NUL in Rear281 JSON')
    result=json.loads(text, object_pairs_hook=unique, parse_constant=invalid)
    def bounded(v, depth=0):
        if depth>16: raise ValueError('Deep Rear281 JSON')
        if type(v) is float and not math.isfinite(v): raise ValueError('Nonfinite Rear281 JSON')
        if isinstance(v,dict):
            for child in v.values(): bounded(child,depth+1)
        elif isinstance(v,list):
            for child in v: bounded(child,depth+1)
    bounded(result)
    return result


def read(root, name, limit=16 * 1024 * 1024):
    p = path(root, name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode) or p.stat().st_size > limit:
        raise ValueError('Missing/oversize regular Rear281 input: ' + name)
    return p.read_bytes()


def name(identity, density):
    if type(identity) is not int or type(density) is not int or (identity, density) not in PAIRS:
        raise ValueError('Unknown Rear281 projectile identity/density')
    return f'rear-multicannon-p1-bank8-{identity - 1310000}-{density}.hda'


def png(identity, density):
    return INPUT_ROOT + '/derived/' + name(identity, density).removesuffix('.hda') + '.png'


def generated_paths():
    return {png(identity, density) for identity, density in PAIRS}


def is_hash(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def selection(root, raw, candidate=False):
    selected = parse(raw)
    keys = {'schema', 'version', 'masters', 'recipe'} | (set() if candidate else {'resources'})
    schema = CANDIDATE_SCHEMA if candidate else SCHEMA
    if not isinstance(selected, dict) or set(selected) != keys or selected['schema'] != schema:
        raise ValueError('Invalid Rear281 candidate/installed schema or fields')
    if not isinstance(selected['version'], str) or not 1 <= len(selected['version']) <= 128:
        raise ValueError('Invalid Rear281 version')
    if not isinstance(selected['masters'], list) or len(selected['masters']) != 1:
        raise ValueError('Expected one Rear281 master')
    for selector, row in zip(SELECTORS, selected['masters']):
        if (not isinstance(row, dict) or set(row) != {'selector','source_json','source_sha256'} or
                type(row['selector']) is not int or row['selector'] != selector or
                row['source_json'] != INPUT_ROOT + f'/master-{selector}.json' or not is_hash(row['source_sha256'])):
            raise ValueError('Invalid Rear281 master identity/path/hash/order')
        if sha(read(root, row['source_json'])) != row['source_sha256']:
            raise ValueError('Selected Rear281 master changed')
    row = selected['recipe']
    if (not isinstance(row, dict) or set(row) != {'path','sha256'} or
            row['path'] != INPUT_ROOT + '/recipe.json' or not is_hash(row['sha256']) or
            sha(read(root, row['path'])) != row['sha256']):
        raise ValueError('Invalid/changed Rear281 recipe record')
    if not candidate:
        if not isinstance(selected['resources'], list) or len(selected['resources']) != 20:
            raise ValueError('Expected twenty derived Rear281 pieces')
        for (identity, density), row in zip(PAIRS, selected['resources']):
            if (not isinstance(row, dict) or set(row) != {'identity', 'density', 'source_png', 'source_sha256'} or
                    type(row['identity']) is not int or type(row['density']) is not int or
                    (row['identity'], row['density']) != (identity, density) or
                    row['source_png'] != png(identity, density) or not is_hash(row['source_sha256'])):
                raise ValueError('Invalid derived Rear281 identity/density/path/order/hash')
    return selected


def recipe(raw):
    result = parse(raw)
    # JSON comparison distinguishes bool/float substitutions in fixed integers.
    if json.dumps(result, sort_keys=True) != json.dumps(RECIPE, sort_keys=True):
        raise ValueError('Fixed Rear281 recipe identity/geometry/resize changed')
    return result


def _assets(root):
    from build_current_art import fnv
    selected, _, blobs = generate(root, read(root, SELECTION, 128 * 1024))
    mapping = parse(read(root, MAPPING, 128 * 1024))
    rows, result, pins = [], {}, {}
    for (identity, density), blob in blobs.items():
        source = ROOT + '/' + name(identity, density)
        destination = 'assets/gameplay/' + name(identity, density)
        if read(root, source) != blob:
            raise ValueError('Rear281 HDA does not match master+fixed recipe: ' + source)
        row = dict(identity=identity, density=density, source_path=source, destination=destination, sha256=sha(blob))
        rows.append(row)
        result[destination] = row
        pins[(identity, density)] = fnv(blob[28:])
    expected = dict(schema='opentyrian-current-rear281-compatibility-v1', selection=SELECTION,
                    version=selected['version'], files=rows)
    if json.dumps(mapping, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Invalid/stale Rear281 compatibility mapping')
    return result, pins


def load_assets(root):
    """Validate own complete derivation; shared-header candidate replacement is separate."""
    return _assets(root)[0]


def load(root):
    result,pins=_assets(root)
    from current_rear_p7_compatibility import verified_pins as p7_pins
    from current_rear39_compatibility import verified_pins as rear39_pins
    from current_rear1_compatibility import verified_pins as rear1_pins
    from current_rear_lobes_compatibility import verified_pins as rear_lobes_pins
    if read(root, HEADER) != payload_header(pins,p7_pins(root),rear39_pins(root),rear1_pins(root),rear_lobes_pins(root)):
        raise ValueError('Stale Rear281 payload pins')
    return result

from current_rear_p7_compatibility import SHARP_VERSIONS, NODE, SHARP, NODE_VERSION

# Only this closed data grammar reaches the fixed JavaScript compiler. No SVG,
# script, URL, file reference or arbitrary expression is accepted from a master.
NUMBER = r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?'

def finite(value, low=-100, high=100):
    if type(value) not in (int,float) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError('Nonfinite/unbounded Rear281 geometry number')


def geometry(raw):
    value=parse(raw)
    if not isinstance(value,dict) or set(value)!={'schema','geometry','gradient'} or value['schema']!='rear281-data-only-geometry-v1':
        raise ValueError('Invalid Rear281 geometry schema')
    g=value['geometry']; grad=value['gradient']
    if not isinstance(g,dict) or set(g)!={'path','heat'} or not isinstance(g['heat'],dict) or set(g['heat'])!={'cx','cy','dx','dy','L','W'}:
        raise ValueError('Invalid Rear281 geometry fields')
    p=g['path']
    if not isinstance(p,str) or not 1 <= len(p) <= 4096 or re.search(r'nan|inf',p,re.I):
        raise ValueError('Invalid Rear281 path')
    tokens=re.findall(r'[MLCZ]|'+NUMBER,p)
    if re.sub(r'[MLCZ]|'+NUMBER+'|[ ,\t\r\n]','',p) or not tokens or tokens[0]!='M' or tokens[-1]!='Z':
        raise ValueError('Unsupported Rear281 path grammar')
    i=0; commands=0
    while i<len(tokens):
        command=tokens[i]; i+=1; commands+=1
        if command not in {'M','L','C','Z'} or (command=='M' and commands!=1) or (command=='Z' and i!=len(tokens)):
            raise ValueError('Invalid Rear281 path command order')
        count={'M':2,'L':2,'C':6,'Z':0}[command]
        if i+count>len(tokens): raise ValueError('Incomplete Rear281 path')
        for token in tokens[i:i+count]:
            if not re.fullmatch(NUMBER,token): raise ValueError('Incomplete Rear281 coordinate group')
            finite(float(token),0,14)
        i+=count
    if commands<3 or commands>128: raise ValueError('Rear281 path complexity')
    for key,n in g['heat'].items(): finite(n,.01 if key in {'L','W'} else -100,100)
    if not isinstance(grad,dict) or set(grad)!={'type','stops'} or grad['type']!='elliptical-radial' or not isinstance(grad['stops'],list) or not 2<=len(grad['stops'])<=16:
        raise ValueError('Invalid Rear281 gradient')
    last=-1
    for stop in grad['stops']:
        if (not isinstance(stop,list) or len(stop)!=2 or not isinstance(stop[0],str) or
                not re.fullmatch(NUMBER,stop[0]) or not isinstance(stop[1],str) or not re.fullmatch('#[0-9a-fA-F]{6}',stop[1])):
            raise ValueError('Invalid Rear281 gradient stop')
        n=float(stop[0]);finite(n,0,1)
        if n<=last: raise ValueError('Rear281 gradient offsets must increase')
        last=n
    if float(grad['stops'][0][0])!=0 or last!=1: raise ValueError('Rear281 gradient endpoint missing')
    return value


DRIVER = r'''
const fs=require('fs'), sharp=require(process.argv[1]);
const req=JSON.parse(fs.readFileSync(0,'utf8'));
if(process.version!==req.node || process.platform!=='linux' || process.arch!=='x64' || JSON.stringify(sharp.versions)!==JSON.stringify(req.versions)) throw Error('Exact renderer profile mismatch');
sharp.cache(false); sharp.concurrency(1);
const g=req.master.geometry, h=g.heat, stops=req.master.gradient.stops;
const gradient=`<defs><radialGradient id="streak" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="matrix(${h.L*h.dx} ${h.L*h.dy} ${-h.W*h.dy} ${h.W*h.dx} ${h.cx} ${h.cy})">${stops.map(([offset,color])=>`<stop offset="${offset}" stop-color="${color}"/>`).join('')}</radialGradient></defs>`;
const coverage=`<defs><mask id="edgeCoverage" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="0" y="0" width="12" height="14"><path d="${g.path}" fill="white"/>${Array.from({length:32},(_,i)=>{let t=(32-i)/32,a=.62+.38*(t*t*(3-2*t)),v=Math.round(255*a);return `<path d="${g.path}" fill="none" stroke="rgb(${v},${v},${v})" stroke-width="${.60*t}" stroke-linejoin="round"/>`;}).join('')}</mask></defs>`;
const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="96" height="112" viewBox="0 0 12 14">\n<!-- Rear Multi-Cannon 10 P1 art pilot. Original bank8 identity 281; this is not an HDA role or resource key. Static 12x14 canvas; anchor 0,0. -->\n\n${gradient}\n${coverage}\n<path d="${g.path}" fill="url(#streak)" mask="url(#edgeCoverage)"/>\n\n</svg>\n`;
const colorSvg=svg.replace(/<defs><mask id="edgeCoverage"[\s\S]*?<\/mask><\/defs>\n/,'').replace(' mask="url(#edgeCoverage)"','');
(async()=>{let out=[];for(const d of [4,8]) {
 const options={density:72*d/8,limitInputPixels:10752};
 const {data:masked,info}=await sharp(Buffer.from(svg),options).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const {data,info:base}=await sharp(Buffer.from(colorSvg),options).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 if(info.width!==12*d||info.height!==14*d||info.channels!==4||JSON.stringify(info)!==JSON.stringify(base)) throw Error('Geometry mismatch');
 for(let p=0;p<data.length;p+=4) {if(data[p+3]===0)data.fill(0,p,p+3);else data[p+3]=Math.max(1,Math.min(data[p+3],masked[p+3]));}
 for(const raw of [281,282,300,301]) {
 const output=Buffer.alloc(data.length),w=info.width,h=info.height;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++) {const xx=(raw===282||raw===301)?w-1-x:x,yy=(raw===300||raw===301)?h-1-y:y;data.copy(output,4*(yy*w+xx),4*(y*w+x),4*(y*w+x+1));}
 const png=await sharp(output,{raw:{width:w,height:h,channels:4}}).png().toBuffer();
 out.push({raw,d,rgba:output.toString('base64'),png:png.toString('base64')});}}
 process.stdout.write(JSON.stringify({svg,rows:out}));})().catch(e=>{process.stderr.write(String(e));process.exit(1)});
'''


def canonical_png(data,w,h):
    """Historical 2/3 exact stored-DEFLATE encoding, no platform compressor."""
    import zlib
    rows=b''.join(b'\0'+data[y*w*4:(y+1)*w*4] for y in range(h))
    stream=bytearray(b'\x78\x01')
    for start in range(0,len(rows),65535):
        block=rows[start:start+65535]
        stream+=bytes([int(start+len(block)==len(rows))])+struct.pack('<HH',len(block),65535-len(block))+block
    stream+=struct.pack('>I',zlib.adler32(rows)&0xffffffff)
    def chunk(kind,body):return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',stream)+chunk(b'IEND',b'')


def half_up(n,d):
    return (2*n+d)//(2*d)


def transform(data,d,kind):
    if type(d) is not int or d not in (4,8) or len(data)!=12*14*d*d*4 or kind not in ('flipX','flipY','rotate180',298,299):
        raise ValueError('Invalid Rear281 transform input')
    w,h=12*d,14*d;out=bytearray(len(data));clipped=0
    for y in range(h):
        for x in range(w):
            rgba=data[4*(y*w+x):4*(y*w+x+1)]
            if not rgba[3] and any(rgba):raise ValueError('Hidden Rear281 RGB')
            if kind=='flipX':xx,yy=w-1-x,y
            elif kind=='flipY':xx,yy=x,h-1-y
            elif kind=='rotate180':xx,yy=w-1-x,h-1-y
            elif kind==298:xx,yy=y,h-1-x
            else:xx,yy=w-1-y,h-1-x
            if not(0<=xx<w and 0<=yy<h):
                clipped+=1
                if any(rgba):raise ValueError('Rear281 occupied transform clipping forbidden')
            else:out[4*(yy*w+xx):4*(yy*w+xx+1)]=rgba
    return bytes(out),dict(transparent_clipped_samples=clipped,occupied_clipped_samples=0)


def twins(data,d):
    if type(d) is not int or d not in (4,8) or len(data)!=12*14*d*d*4:
        raise ValueError('Invalid Rear281 twin input')
    w,h=12*d,14*d;out=bytearray(data);overlap=0
    for y in range(h):
        for x in range(w):
            foreground=data[4*(y*w+x):4*(y*w+x+1)]
            if not foreground[3]:
                if any(foreground):raise ValueError('Hidden Rear281 RGB')
                continue
            yy=y+4*d
            if yy>=h:raise ValueError('Rear281 twin occupied clipping forbidden')
            i=4*(yy*w+x);background=out[i:i+4];af=foreground[3];ab=background[3]
            if not ab:out[i:i+4]=foreground;continue
            overlap+=1;den=255*af+ab*(255-af)
            out[i:i+4]=bytes([half_up(foreground[c]*af*255+background[c]*ab*(255-af),den) for c in range(3)]+[half_up(den,255)])
    return bytes(out),dict(overlap_samples=overlap,occupied_clipped_samples=0)


def compose(data,d,target):
    if type(target) is not int or target not in (282,300,301,277,278,296,297,298,299):
        raise ValueError('Invalid Rear281 target')
    if target in (282,300,301):return transform(data,d,{282:'flipX',300:'flipY',301:'rotate180'}[target])
    base=transform(data,d,'flipX')[0] if target in (278,297) else data
    result,metrics=twins(base,d)
    if target in (296,297):result,more=transform(result,d,'flipY');metrics.update(more)
    elif target in (298,299):result,more=transform(result,d,target);metrics.update(more)
    return result,metrics


def render(raw, include_svg=False):
    master=geometry(raw)
    request=json.dumps(dict(master=master,node=NODE_VERSION,versions=SHARP_VERSIONS)).encode()
    try:
        with tempfile.TemporaryDirectory(prefix='rear281-data-') as tmp:
            with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
                result=subprocess.run([NODE,'--max-old-space-size=128','-e',DRIVER,SHARP],input=request,stdout=out,stderr=err,cwd=tmp,env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},timeout=30)
                if out.tell()>1024*1024 or err.tell()>128*1024 or result.returncode:
                    raise ValueError('Rear281 fixed renderer failed/profile mismatch')
                out.seek(0); response=json.loads(out.read())
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise ValueError('Required Rear281 renderer unavailable/timed out') from exc
    rows=response['rows']
    if [(r['d'],r['raw']) for r in rows]!=[(d,r) for d in (4,8) for r in (281,282,300,301)]:raise ValueError('Unexpected Rear281 renderer outputs')
    direct={}
    for row in rows:
        d=row['d'];data=base64.b64decode(row['rgba'],validate=True);encoded=base64.b64decode(row['png'],validate=True)
        if len(data)!=12*14*d*d*4 or not any(data[3::4]):raise ValueError('Unexpected/empty Rear281 renderer bytes')
        if any(any(data[p:p+3]) for p in range(0,len(data),4) if data[p+3]==0):raise ValueError('Hidden Rear281 RGB')
        direct[(1310000+row['raw'],d)]=(encoded,data)
    result={}
    for d in (4,8):
        data=direct[(1310281,d)][1]
        for raw_id in (281,282,300,301,277,278,296,297,298,299):
            if raw_id in (281,282,300,301):
                pair=direct[(1310000+raw_id,d)]
                if raw_id!=281 and compose(data,d,raw_id)[0]!=pair[1]:raise ValueError('Rear281 direct transform mismatch')
            else:
                rgba,_=compose(data,d,raw_id);pair=(canonical_png(rgba,12*d,14*d),rgba)
            result[(1310000+raw_id,d)]=pair
    return (result,response['svg'].encode()) if include_svg else result


def generate(root, raw, candidate=False):
    selected=selection(root,raw,candidate)
    recipe(read(root,selected['recipe']['path'],128*1024))
    check_tool()
    rendered=render(read(root,selected['masters'][0]['source_json'],64*1024))
    pngs,blobs,rows={},{},[]
    for ordinal,((identity,density),(encoded,rgba)) in enumerate(rendered.items()):
        source=png(identity,density)
        if not candidate:
            if read(root,source)!=encoded or selected['resources'][ordinal]['source_sha256']!=sha(encoded):
                raise ValueError('Derived Rear281 PNG does not match canonical geometry')
        pngs[source]=encoded
        blobs[(identity,density)]=struct.pack('<4s6I',b'HDR1',identity,density,12,14,0,0)+rgba
        rows.append(dict(identity=identity,density=density,source_png=source,source_sha256=sha(encoded)))
    return dict(selected,schema=SCHEMA,resources=rows),pngs,blobs


def input_paths(root):
    selected=selection(root,read(root,SELECTION,128*1024))
    return {SELECTION,selected['recipe']['path'],selected['masters'][0]['source_json']} | generated_paths() | {ROOT+'/'+name(*p) for p in PAIRS}


def verified_pins(root):
    return _assets(root)[1]


def payload_header(pins, p7_pins, rear39_pins, rear1_pins, rear_lobes_pins=None):
    from current_rear_p7_compatibility import payload_header as compose_header
    return compose_header(p7_pins,rear39_pins,rear1_pins,pins,rear_lobes_pins)

GOLDEN_MASTER = b'{\n  "schema": "rear281-data-only-geometry-v1",\n  "geometry": {\n    "path": "M1.58 0 C.66 0 0 .72 0 1.73 C0 2.88 1.11 3.62 2.86 4.25 C5.15 5.07 8.16 5.7 11 6 C9.13 4.46 6.67 2.84 4.63 1.5 C3.33 .64 2.66 0 1.58 0Z",\n    "heat": {\n      "cx": 1.65,\n      "cy": 1.65,\n      "dx": 0.9015231,\n      "dy": 0.4327311,\n      "L": 9.1,\n      "W": 1.8\n    }\n  },\n  "gradient": {\n    "type": "elliptical-radial",\n    "stops": [\n      [\n        "0",\n        "#fffaa1"\n      ],\n      [\n        ".19",\n        "#fff06b"\n      ],\n      [\n        ".38",\n        "#ffd338"\n      ],\n      [\n        ".57",\n        "#ff9e1c"\n      ],\n      [\n        ".75",\n        "#ff680a"\n      ],\n      [\n        ".91",\n        "#ef3904"\n      ],\n      [\n        "1",\n        "#cd2102"\n      ]\n    ]\n  }\n}\n'
GOLDEN_HASHES = {(1310277, 4): ('96d2afe30ca79ad058e205e0783de8c9b6d50c2204c1f26734f82584271c4cec', '45ba353dbc163224e0b183e142f7a4c8ac1f71a36274dfb5524fed51443480ed'), (1310278, 4): ('3e65188e0c8fc823e60fa7e05809d672a87c481dda45dc0e58e33314f7e7725c', 'e111cb772f63599ee7588fd9bfd743b14c0dd27d04ea9be0fd90dd700ebc05c8'), (1310281, 4): ('82d2d3617af7930d54312c69995ca61b2a050a6bd6b63543128bd61ad95622b3', 'a31935a0bd297367138df393805d8ed2bfa856cebd09d9c3bea0a83dde89e1ad'), (1310282, 4): ('d00d177a50391351619d9d993715c7f55d67c7aae26e9b15da23289f538553c4', '344a4066d9f0f2316073f3d176b0956514b7af7b5c2888462ae61710af608ff3'), (1310296, 4): ('8926d54b2f02a1e754491f53101bd7f7e118f40c50456ec0abafa803cd4b6fc4', 'ade60e0e1defb9293f4e4b4abd2682457cc47198fa3198f4642c5f69abe7289b'), (1310297, 4): ('e3a0a1ef3799a3328664b635ef8bcdf39dfc5ecd0fb5dd4d9cbdab288f46ece7', 'a6d9272f8a901c0c2cdfd484a7884682c4aa3b42f5441ac53d0e4fc646096283'), (1310298, 4): ('f280f4f5a34ad0df5304629ed3e752baa2b31a7a76c36056917089828bd80c5d', '68371e142abd88d8961e6e74c2570ececcb6941b8e3f3b5eb079852c742ff3e6'), (1310299, 4): ('aada918ad735c7a8e7e1d6f076191560b436801a1167e201b2543a30c656187f', 'a7d20ba1245be896c8829d5828d274d953ab18dd38f40c67be1837885ac95604'), (1310300, 4): ('72ef064b4209888003aedd965eabc25e6ce4466ca229294f9b1ea072aaac8322', '7bb9490c9e4d678931f3702e155c73f707c4e806ef29b9d03cd38317a7cf9e7a'), (1310301, 4): ('ee603b3d436dbb2dae4913ed6bb4ba5b9da9909668e895672b91c75d471fcba9', '3a024a599f5adbb840dd60e10a5381842ed88fc1ea5b697da1e845ef6d56a865'), (1310277, 8): ('72721e9e06c9c6d268766f95d9ac65e28482a080fe9abef2ced08c8dced0463b', '75b03b20070976edcb7ad330aec1f8754ae47eef70c88f7307efacb92608fdf6'), (1310278, 8): ('e6a45a6bb6c877cae3ab8873e441575b3d64ce2feacf788c8950ee1111cfe41b', 'd9c8d8468785ac51d3d5d47c0a8069640225a01bf331501eaa004272746e0757'), (1310281, 8): ('511b8b0e8b2f9f6d38698c4315ef18e31c694db4e5ab3bcde52ba22a5206c761', 'f4dd85ab37ec9b703a552fbde77f84839294cffb669eea161883c200338569ea'), (1310282, 8): ('f315002d3f205aa610f5664a351eea863e89c7889d4c1f23ec6de697019779d2', '12b31ccd1cb7dd23408bdfe34a8bad8571d150f60b90b07182c38a19a4f1f0a0'), (1310296, 8): ('e63ca8bc67f8bf59e48f8c5b2424f267d783cc8dbdc643b5d11ef2bf4576139d', '45222a89e6a9bef2640d8f2b5d962874d425dfd5c0faa22a0f7a5c50435d885d'), (1310297, 8): ('0c9cea29b256e50b99a47c374bde2a62f65921a8563f8ba8e09eca238581b4f7', '4f2104cd14c9057b6a672c6ff226f9a57e15ec10fdd290f3e2dfd568456545d7'), (1310298, 8): ('49b27a424ff1240032c4c1321029fb96341ce552316dad7a0a0811983d29fb0b', '05c698812953ab0c654eb3a42c6d137894c1f65ddd9a0386182ecb70c7776440'), (1310299, 8): ('17d6741128448df90dc1e1524a1690078b3d4d2978865fd189e0dc6f0f52ad56', '1099a76516544a68807f9975090aacc90ee75fc472eca6a40f2bb925d106422f'), (1310300, 8): ('e4b5fe6a03f1ae27d961d4f20dab8b1fbb78afbf22729d19d1e9e1f035a5dd41', 'fe12d44888d91278bb40ab6a1964b74f170b69aa36ccade54b7880cb3bf862bc'), (1310301, 8): ('d18728090ecd307803939accfbc81e1d476984265747ca0abf70ae8796438599', '15d37d0f390ad90a2462fe7541f3b21d16e50bd298a726d1179039da41fecf8d')}
def check_tool():
    actual,svg=render(GOLDEN_MASTER,include_svg=True)
    if sha(svg)!='25910655d9fb34a483fff2cb7d751a355c07da975b070c7c8f5ae65636e1fef6':
        raise ValueError('Rear281 generated SVG golden mismatch')
    if {p:(sha(png),sha(rgba)) for p,(png,rgba) in actual.items()}!=GOLDEN_HASHES:
        raise ValueError('Rear281 renderer twenty-output golden mismatch')
