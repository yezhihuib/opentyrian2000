"""One canonical data-only Rear39 geometry -> six role131 transports; no eligibility changes."""
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

IDS = (1310039, 1310040, 1310041)
SELECTORS = (39,)
PAIRS = tuple((identity, density) for density in (4,8) for identity in IDS)
SELECTION = 'assets/hd/authoring/rear39-current.json'
MAPPING = 'packaging/current-rear39-compatibility.json'
HEADER = 'src/current_rear_multi_payload_pins.h'
ROOT = 'assets/hd/current-compat/rear39'
INPUT_ROOT = 'authoring-inputs/rear39-current'
SCHEMA = 'opentyrian-current-rear39-authoring-v1'
CANDIDATE_SCHEMA = 'opentyrian-current-rear39-candidate-v1'
RECIPE = {'identity': {'source_bank': 8, 'source_id': 39, 'role': 131, 'key': 1310039}, 'canvas': {'logical_width': 12, 'logical_height': 14, 'anchor': [0, 0], 'svg_width': 96, 'svg_height': 112, 'densities': [4, 8]}, 'coverage': {'stroke_count': 32, 'outer_stroke_width': 0.6, 'minimum_factor': 0.62, 'factor_range': 0.38, 'round_linejoin': True}, 'derived': {'40': {'parts': [[True, 0, -4], [False, 0, 4]], 'occupied_clipping_allowed': False}, '41': {'parts': [[False, 2, -3], [False, 0, 1], [True, 2, 3]], 'occupied_clipping_allowed': True}}, 'schema': 'rear39-fixed-recipe-v1'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate Rear39 JSON key: ' + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('Non-finite Rear39 JSON number: ' + value)

    if len(raw) > 128 * 1024:
        raise ValueError('Oversize Rear39 JSON')
    text=raw.decode('utf-8',errors='strict')
    if '\x00' in text: raise ValueError('NUL in Rear39 JSON')
    result=json.loads(text, object_pairs_hook=unique, parse_constant=invalid)
    def bounded(v, depth=0):
        if depth>16: raise ValueError('Deep Rear39 JSON')
        if type(v) is float and not math.isfinite(v): raise ValueError('Nonfinite Rear39 JSON')
        if isinstance(v,dict):
            for child in v.values(): bounded(child,depth+1)
        elif isinstance(v,list):
            for child in v: bounded(child,depth+1)
    bounded(result)
    return result


def read(root, name, limit=16 * 1024 * 1024):
    p = path(root, name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode) or p.stat().st_size > limit:
        raise ValueError('Missing/oversize regular Rear39 input: ' + name)
    return p.read_bytes()


def name(identity, density):
    if type(identity) is not int or type(density) is not int or (identity, density) not in PAIRS:
        raise ValueError('Unknown Rear39 projectile identity/density')
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
        raise ValueError('Invalid Rear39 candidate/installed schema or fields')
    if not isinstance(selected['version'], str) or not 1 <= len(selected['version']) <= 128:
        raise ValueError('Invalid Rear39 version')
    if not isinstance(selected['masters'], list) or len(selected['masters']) != 1:
        raise ValueError('Expected one Rear39 master')
    for selector, row in zip(SELECTORS, selected['masters']):
        if (not isinstance(row, dict) or set(row) != {'selector','source_json','source_sha256'} or
                type(row['selector']) is not int or row['selector'] != selector or
                row['source_json'] != INPUT_ROOT + f'/master-{selector}.json' or not is_hash(row['source_sha256'])):
            raise ValueError('Invalid Rear39 master identity/path/hash/order')
        if sha(read(root, row['source_json'])) != row['source_sha256']:
            raise ValueError('Selected Rear39 master changed')
    row = selected['recipe']
    if (not isinstance(row, dict) or set(row) != {'path','sha256'} or
            row['path'] != INPUT_ROOT + '/recipe.json' or not is_hash(row['sha256']) or
            sha(read(root, row['path'])) != row['sha256']):
        raise ValueError('Invalid/changed Rear39 recipe record')
    if not candidate:
        if not isinstance(selected['resources'], list) or len(selected['resources']) != 6:
            raise ValueError('Expected six derived Rear39 pieces')
        for (identity, density), row in zip(PAIRS, selected['resources']):
            if (not isinstance(row, dict) or set(row) != {'identity', 'density', 'source_png', 'source_sha256'} or
                    type(row['identity']) is not int or type(row['density']) is not int or
                    (row['identity'], row['density']) != (identity, density) or
                    row['source_png'] != png(identity, density) or not is_hash(row['source_sha256'])):
                raise ValueError('Invalid derived Rear39 identity/density/path/order/hash')
    return selected


def recipe(raw):
    result = parse(raw)
    # JSON comparison distinguishes bool/float substitutions in fixed integers.
    if json.dumps(result, sort_keys=True) != json.dumps(RECIPE, sort_keys=True):
        raise ValueError('Fixed Rear39 recipe identity/geometry/resize changed')
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
            raise ValueError('Rear39 HDA does not match master+fixed recipe: ' + source)
        row = dict(identity=identity, density=density, source_path=source, destination=destination, sha256=sha(blob))
        rows.append(row)
        result[destination] = row
        pins[(identity, density)] = fnv(blob[28:])
    expected = dict(schema='opentyrian-current-rear39-compatibility-v1', selection=SELECTION,
                    version=selected['version'], files=rows)
    if json.dumps(mapping, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Invalid/stale Rear39 compatibility mapping')
    return result, pins


def load_assets(root):
    """Validate own complete derivation; shared-header candidate replacement is separate."""
    return _assets(root)[0]


def load(root):
    result,pins=_assets(root)
    from current_rear_p7_compatibility import verified_pins as p7_pins
    from current_rear1_compatibility import verified_pins as rear1_pins
    from current_rear281_compatibility import verified_pins as rear281_pins
    from current_rear_lobes_compatibility import verified_pins as rear_lobes_pins
    if read(root, HEADER) != payload_header(pins,p7_pins(root),rear1_pins(root),rear281_pins(root),rear_lobes_pins(root)):
        raise ValueError('Stale Rear39 payload pins')
    return result

from current_rear_p7_compatibility import SHARP_VERSIONS, NODE, SHARP, NODE_VERSION

# Only this closed data grammar reaches the fixed JavaScript compiler. No SVG,
# script, URL, file reference or arbitrary expression is accepted from a master.
NUMBER = r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?'

def finite(value, low=-100, high=100):
    if type(value) not in (int,float) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError('Nonfinite/unbounded Rear39 geometry number')


def geometry(raw):
    value=parse(raw)
    if not isinstance(value,dict) or set(value)!={'schema','geometry','gradient'} or value['schema']!='rear39-data-only-geometry-v1':
        raise ValueError('Invalid Rear39 geometry schema')
    g=value['geometry']; grad=value['gradient']
    if not isinstance(g,dict) or set(g)!={'path','heat'} or not isinstance(g['heat'],dict) or set(g['heat'])!={'cx','cy','dx','dy','L','W'}:
        raise ValueError('Invalid Rear39 geometry fields')
    p=g['path']
    if not isinstance(p,str) or not 1 <= len(p) <= 4096 or re.search(r'nan|inf',p,re.I):
        raise ValueError('Invalid Rear39 path')
    tokens=re.findall(r'[MLCZ]|'+NUMBER,p)
    if re.sub(r'[MLCZ]|'+NUMBER+'|[ ,\t\r\n]','',p) or not tokens or tokens[0]!='M' or tokens[-1]!='Z':
        raise ValueError('Unsupported Rear39 path grammar')
    i=0; commands=0
    while i<len(tokens):
        command=tokens[i]; i+=1; commands+=1
        if command not in {'M','L','C','Z'} or (command=='M' and commands!=1) or (command=='Z' and i!=len(tokens)):
            raise ValueError('Invalid Rear39 path command order')
        count={'M':2,'L':2,'C':6,'Z':0}[command]
        if i+count>len(tokens): raise ValueError('Incomplete Rear39 path')
        for token in tokens[i:i+count]:
            if not re.fullmatch(NUMBER,token): raise ValueError('Incomplete Rear39 coordinate group')
            finite(float(token),0,14)
        i+=count
    if commands<3 or commands>128: raise ValueError('Rear39 path complexity')
    for key,n in g['heat'].items(): finite(n,.01 if key in {'L','W'} else -100,100)
    if not isinstance(grad,dict) or set(grad)!={'type','stops'} or grad['type']!='elliptical-radial' or not isinstance(grad['stops'],list) or not 2<=len(grad['stops'])<=16:
        raise ValueError('Invalid Rear39 gradient')
    last=-1
    for stop in grad['stops']:
        if (not isinstance(stop,list) or len(stop)!=2 or not isinstance(stop[0],str) or
                not re.fullmatch(NUMBER,stop[0]) or not isinstance(stop[1],str) or not re.fullmatch('#[0-9a-fA-F]{6}',stop[1])):
            raise ValueError('Invalid Rear39 gradient stop')
        n=float(stop[0]);finite(n,0,1)
        if n<=last: raise ValueError('Rear39 gradient offsets must increase')
        last=n
    if float(grad['stops'][0][0])!=0 or last!=1: raise ValueError('Rear39 gradient endpoint missing')
    return value


DRIVER = r'''
const fs=require('fs'), sharp=require(process.argv[1]);
const req=JSON.parse(fs.readFileSync(0,'utf8'));
if(process.version!==req.node || process.platform!=='linux' || process.arch!=='x64' || JSON.stringify(sharp.versions)!==JSON.stringify(req.versions)) throw Error('Exact renderer profile mismatch');
sharp.cache(false); sharp.concurrency(1);
const g=req.master.geometry, h=g.heat, stops=req.master.gradient.stops;
const gradient=`<defs><radialGradient id="streak" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="matrix(${h.L*h.dx} ${h.L*h.dy} ${-h.W*h.dy} ${h.W*h.dx} ${h.cx} ${h.cy})">${stops.map(([offset,color])=>`<stop offset="${offset}" stop-color="${color}"/>`).join('')}</radialGradient></defs>`;
const coverage=`<defs><mask id="edgeCoverage" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="0" y="0" width="12" height="14"><path d="${g.path}" fill="white"/>${Array.from({length:32},(_,i)=>{let t=(32-i)/32,a=.62+.38*(t*t*(3-2*t)),v=Math.round(255*a);return `<path d="${g.path}" fill="none" stroke="rgb(${v},${v},${v})" stroke-width="${.60*t}" stroke-linejoin="round"/>`;}).join('')}</mask></defs>`;
const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="96" height="112" viewBox="0 0 12 14">\n<!-- Rear Multi-Cannon 10 P1 art pilot. Original bank8 identity 39; this is not an HDA role or resource key. Static 12x14 canvas; anchor 0,0. -->\n\n${gradient}\n${coverage}\n<path d="${g.path}" fill="url(#streak)" mask="url(#edgeCoverage)"/>\n\n</svg>\n`;
const colorSvg=svg.replace(/<defs><mask id="edgeCoverage"[\s\S]*?<\/mask><\/defs>\n/,'').replace(' mask="url(#edgeCoverage)"','');
(async()=>{let out=[];for(const d of [4,8]) {
 const options={density:72*d/8,limitInputPixels:10752};
 const {data:masked,info}=await sharp(Buffer.from(svg),options).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const {data,info:base}=await sharp(Buffer.from(colorSvg),options).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 if(info.width!==12*d||info.height!==14*d||info.channels!==4||JSON.stringify(info)!==JSON.stringify(base)) throw Error('Geometry mismatch');
 for(let p=0;p<data.length;p+=4) {if(data[p+3]===0)data.fill(0,p,p+3);else data[p+3]=Math.max(1,Math.min(data[p+3],masked[p+3]));}
 const png=await sharp(data,{raw:{width:info.width,height:info.height,channels:4}}).png().toBuffer();
 out.push({d,rgba:data.toString('base64'),png:png.toString('base64')});}
 process.stdout.write(JSON.stringify({svg,rows:out}));})().catch(e=>{process.stderr.write(String(e));process.exit(1)});
'''


def canonical_png(data,w,h):
    """Historical 40/41 exact stored-DEFLATE encoding, no platform compressor."""
    import zlib
    rows=b''.join(b'\0'+data[y*w*4:(y+1)*w*4] for y in range(h))
    stream=bytearray(b'\x78\x01')
    for start in range(0,len(rows),65535):
        block=rows[start:start+65535]
        stream+=bytes([int(start+len(block)==len(rows))])+struct.pack('<HH',len(block),65535-len(block))+block
    stream+=struct.pack('>I',zlib.adler32(rows)&0xffffffff)
    def chunk(kind,body):return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',stream)+chunk(b'IEND',b'')


def compose(data,d,target):
    if type(d) is not int or d not in (4,8) or type(target) is not int or target not in (40,41) or len(data)!=12*14*d*d*4:
        raise ValueError('Invalid Rear39 composition input')
    w,h=12*d,14*d; occupied={}; clipped=0; clipped_alpha=0
    for flip,dx,dy in RECIPE['derived'][str(target)]['parts']:
        for p in range(w*h):
            rgba=data[4*p:4*p+4]
            if not rgba[3]:
                if any(rgba):raise ValueError('Hidden Rear39 RGB')
                continue
            x=p%w+dx*d;y=(h-1-p//w if flip else p//w)+dy*d
            if (x,y) in occupied:raise ValueError('Rear39 transformed supports overlap')
            occupied[x,y]=rgba
            if not (0<=x<w and 0<=y<h):clipped+=1;clipped_alpha+=rgba[3]
    if target==40 and clipped:raise ValueError('Rear40 occupied clipping forbidden')
    result=b''.join(occupied.get((x,y),b'\0'*4) for y in range(h) for x in range(w))
    return result,dict(clipped_samples=clipped,clipped_alpha=clipped_alpha)


def render(raw, include_svg=False):
    master=geometry(raw)
    request=json.dumps(dict(master=master,node=NODE_VERSION,versions=SHARP_VERSIONS)).encode()
    try:
        with tempfile.TemporaryDirectory(prefix='rear39-data-') as tmp:
            with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
                result=subprocess.run([NODE,'--max-old-space-size=128','-e',DRIVER,SHARP],input=request,stdout=out,stderr=err,cwd=tmp,env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},timeout=30)
                if out.tell()>1024*1024 or err.tell()>128*1024 or result.returncode:
                    raise ValueError('Rear39 fixed renderer failed/profile mismatch')
                out.seek(0); response=json.loads(out.read())
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise ValueError('Required Rear39 renderer unavailable/timed out') from exc
    rows=response['rows']
    if [r['d'] for r in rows]!=[4,8]:raise ValueError('Unexpected Rear39 renderer outputs')
    result={}
    for row in rows:
        d=row['d'];data=base64.b64decode(row['rgba'],validate=True);encoded=base64.b64decode(row['png'],validate=True)
        if len(data)!=12*14*d*d*4 or not any(data[3::4]):raise ValueError('Unexpected/empty Rear39 renderer bytes')
        if any(any(data[p:p+3]) for p in range(0,len(data),4) if data[p+3]==0):raise ValueError('Hidden Rear39 RGB')
        result[(1310039,d)]=(encoded,data)
        for target in (40,41):
            rgba,_=compose(data,d,target);result[(1310000+target,d)]=(canonical_png(rgba,12*d,14*d),rgba)
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
                raise ValueError('Derived Rear39 PNG does not match canonical geometry')
        pngs[source]=encoded
        blobs[(identity,density)]=struct.pack('<4s6I',b'HDR1',identity,density,12,14,0,0)+rgba
        rows.append(dict(identity=identity,density=density,source_png=source,source_sha256=sha(encoded)))
    return dict(selected,schema=SCHEMA,resources=rows),pngs,blobs


def input_paths(root):
    selected=selection(root,read(root,SELECTION,128*1024))
    return {SELECTION,selected['recipe']['path'],selected['masters'][0]['source_json']} | generated_paths() | {ROOT+'/'+name(*p) for p in PAIRS}


def verified_pins(root):
    return _assets(root)[1]


def payload_header(pins, p7_pins, rear1_pins=None, rear281_pins=None, rear_lobes_pins=None):
    from current_rear_p7_compatibility import payload_header as compose_header
    return compose_header(p7_pins,pins,rear1_pins,rear281_pins,rear_lobes_pins)

GOLDEN_MASTER = b'{\n  "schema": "rear39-data-only-geometry-v1",\n  "geometry": {\n    "path": "M2.25 4 C.91 4 0 4.8 0 6 C0 7.27 .86 8 2.24 8 C4.63 8 7.86 6.72 11 5.25 C8.34 4.57 5.44 4 2.25 4Z",\n    "heat": {\n      "cx": 1.68,\n      "cy": 5.92,\n      "dx": 0.9961947,\n      "dy": -0.0871557,\n      "L": 9.1,\n      "W": 1.8\n    }\n  },\n  "gradient": {\n    "type": "elliptical-radial",\n    "stops": [\n      [\n        "0",\n        "#fffaa1"\n      ],\n      [\n        ".19",\n        "#fff06b"\n      ],\n      [\n        ".38",\n        "#ffd338"\n      ],\n      [\n        ".57",\n        "#ff9e1c"\n      ],\n      [\n        ".75",\n        "#ff680a"\n      ],\n      [\n        ".91",\n        "#ef3904"\n      ],\n      [\n        "1",\n        "#cd2102"\n      ]\n    ]\n  }\n}\n'
GOLDEN_HASHES = {(1310039, 4): ('736bacd2ea86c5412f948ed0a402346f93a7b3339fc112f2a13bc84d938b2a57', '2fad980f6a45679df0b1baf368857b2b9ec70779ec41942fdb2ace813261e91d'), (1310039, 8): ('8887cdf07fac4091b24ad58a488b77396dffbfef2f94464e5ab8fd2e7af0d861', '88ff4e6f61145c05ed0a7d1ebcec38f06c7aaed4ae86100cc5065cc16d5f8374'), (1310040, 4): ('77a878e3461ff3a0d574eb009607f5f2fcf2705f25cf55289e0942df459a78fe', '13a2653e9542063430647c1d87f22981c5fb1b9176d6cfe77e8ca7e7f62e67fa'), (1310040, 8): ('c2ab24824895c6aa195cb7aa5a2738b35bdee46d475167184b51b6ae3e3ab103', '48e3f1d30dd8fa23ddda7067a17b72dc24926310a2c617248fa3db2c4ce9e874'), (1310041, 4): ('b09a9bb38ab53b357be8caadca6807586255368d56ee2677abd509b5895df68b', 'c832a1267614335d4807a48ad06c44708677ebd4cf69516652066aebe36ef575'), (1310041, 8): ('f142ac3eb4ddf0b54a7b70ef86d50daeda5fbd2a80f81403286f5add38e2bd79', '47040ee657bfc71fcd46e23348521d20c83e87a9177788164becde85c3295a55')}

def check_tool():
    actual,svg=render(GOLDEN_MASTER,include_svg=True)
    if sha(svg)!='cb7f4493d3b72280f04579632236a5f4a179473460a913ab1c4739593570e112':
        raise ValueError('Rear39 generated SVG golden mismatch')
    if {p:(sha(png),sha(rgba)) for p,(png,rgba) in actual.items()}!=GOLDEN_HASHES:
        raise ValueError('Rear39 renderer six-output golden mismatch')
