"""Two independent data-only Rear lobe masters -> eight role131 transports; no eligibility changes."""
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

IDS = (1310203, 1310222, 1310043, 1310005)
SELECTORS = (203,43)
PAIRS = tuple((identity, density) for density in (4,8) for identity in IDS)
SELECTION = 'assets/hd/authoring/rear-lobes-current.json'
MAPPING = 'packaging/current-rear-lobes-compatibility.json'
HEADER = 'src/current_rear_multi_payload_pins.h'
ROOT = 'assets/hd/current-compat/rear-lobes'
INPUT_ROOT = 'authoring-inputs/rear-lobes-current'
SCHEMA = 'opentyrian-current-rear-lobes-authoring-v1'
CANDIDATE_SCHEMA = 'opentyrian-current-rear-lobes-candidate-v1'
RECIPE = {'schema': 'rear-lobes-fixed-recipe-v1', 'identities': [203, 43], 'canvas': {'logical_width': 12, 'logical_height': 14, 'anchor': [0, 0], 'svg_width': 96, 'svg_height': 112, 'densities': [4, 8]}, 'coverage': {'stroke_count': 32, 'outer_stroke_width': 0.6, 'minimum_factor': 0.62, 'factor_range': 0.38, 'round_linejoin': True}, 'derived': {'203': 'inner+outer+whole-vector-flipY', '222': 'fullcanvas-RGBA-flipX203', '43': 'outer+shoulder+whole-vector-flipY-pair+central-once', '5': 'fullcanvas-RGBA-flipX43'}, 'occupied_clipping_allowed': False}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate Rear lobes JSON key: ' + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('Non-finite Rear lobes JSON number: ' + value)

    if len(raw) > 128 * 1024:
        raise ValueError('Oversize Rear lobes JSON')
    text=raw.decode('utf-8',errors='strict')
    if '\x00' in text: raise ValueError('NUL in Rear lobes JSON')
    result=json.loads(text, object_pairs_hook=unique, parse_constant=invalid)
    def bounded(v, depth=0):
        if depth>16: raise ValueError('Deep Rear lobes JSON')
        if type(v) is float and not math.isfinite(v): raise ValueError('Nonfinite Rear lobes JSON')
        if isinstance(v,dict):
            for child in v.values(): bounded(child,depth+1)
        elif isinstance(v,list):
            for child in v: bounded(child,depth+1)
    bounded(result)
    return result


def read(root, name, limit=16 * 1024 * 1024):
    p = path(root, name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode) or p.stat().st_size > limit:
        raise ValueError('Missing/oversize regular Rear lobes input: ' + name)
    return p.read_bytes()


def name(identity, density):
    if type(identity) is not int or type(density) is not int or (identity, density) not in PAIRS:
        raise ValueError('Unknown Rear lobes projectile identity/density')
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
        raise ValueError('Invalid Rear lobes candidate/installed schema or fields')
    if not isinstance(selected['version'], str) or not 1 <= len(selected['version']) <= 128:
        raise ValueError('Invalid Rear lobes version')
    if not isinstance(selected['masters'], list) or len(selected['masters']) != 2:
        raise ValueError('Expected two independent Rear lobes masters')
    for selector, row in zip(SELECTORS, selected['masters']):
        if (not isinstance(row, dict) or set(row) != {'selector','source_json','source_sha256'} or
                type(row['selector']) is not int or row['selector'] != selector or
                row['source_json'] != INPUT_ROOT + f'/master-{selector}.json' or not is_hash(row['source_sha256'])):
            raise ValueError('Invalid Rear lobes master identity/path/hash/order')
        if sha(read(root, row['source_json'])) != row['source_sha256']:
            raise ValueError('Selected Rear lobes master changed')
    row = selected['recipe']
    if (not isinstance(row, dict) or set(row) != {'path','sha256'} or
            row['path'] != INPUT_ROOT + '/recipe.json' or not is_hash(row['sha256']) or
            sha(read(root, row['path'])) != row['sha256']):
        raise ValueError('Invalid/changed Rear lobes recipe record')
    if not candidate:
        if not isinstance(selected['resources'], list) or len(selected['resources']) != 8:
            raise ValueError('Expected eight derived Rear lobes pieces')
        for (identity, density), row in zip(PAIRS, selected['resources']):
            if (not isinstance(row, dict) or set(row) != {'identity', 'density', 'source_png', 'source_sha256'} or
                    type(row['identity']) is not int or type(row['density']) is not int or
                    (row['identity'], row['density']) != (identity, density) or
                    row['source_png'] != png(identity, density) or not is_hash(row['source_sha256'])):
                raise ValueError('Invalid derived Rear lobes identity/density/path/order/hash')
    return selected


def recipe(raw):
    result = parse(raw)
    # JSON comparison distinguishes bool/float substitutions in fixed integers.
    if json.dumps(result, sort_keys=True) != json.dumps(RECIPE, sort_keys=True):
        raise ValueError('Fixed Rear lobes recipe identity/geometry/resize changed')
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
            raise ValueError('Rear lobes HDA does not match master+fixed recipe: ' + source)
        row = dict(identity=identity, density=density, source_path=source, destination=destination, sha256=sha(blob))
        rows.append(row)
        result[destination] = row
        pins[(identity, density)] = fnv(blob[28:])
    expected = dict(schema='opentyrian-current-rear-lobes-compatibility-v1', selection=SELECTION,
                    version=selected['version'], files=rows)
    if json.dumps(mapping, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Invalid/stale Rear lobes compatibility mapping')
    return result, pins


def load_assets(root):
    """Validate own complete derivation; shared-header candidate replacement is separate."""
    return _assets(root)[0]


def load(root):
    result,pins=_assets(root)
    from current_rear_p7_compatibility import verified_pins as p7_pins
    from current_rear39_compatibility import verified_pins as rear39_pins
    from current_rear1_compatibility import verified_pins as rear1_pins
    from current_rear281_compatibility import verified_pins as rear281_pins
    if read(root, HEADER) != payload_header(pins,p7_pins(root),rear39_pins(root),rear1_pins(root),rear281_pins(root)):
        raise ValueError('Stale Rear lobes payload pins')
    return result

from current_rear_p7_compatibility import SHARP_VERSIONS, NODE, SHARP, NODE_VERSION

# Only this closed data grammar reaches the fixed JavaScript compiler. No SVG,
# script, URL, file reference or arbitrary expression is accepted from a master.
NUMBER = r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?'

def finite(value, low=-100, high=100):
    if type(value) not in (int,float) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError('Nonfinite/unbounded Rear lobes geometry number')


def geometry(raw):
    value=parse(raw)
    if not isinstance(value,dict) or set(value)!={'schema','selector','lobes','gradient'} or value['schema']!='rear-lobes-data-only-geometry-v1':
        raise ValueError('Invalid Rear lobes geometry schema')
    selector=value['selector']
    if type(selector) is not int or selector not in SELECTORS: raise ValueError('Invalid independent master selector')
    names=('inner','outer') if selector==203 else ('outer','shoulder','central')
    if not isinstance(value['lobes'],list) or len(value['lobes'])!=len(names): raise ValueError('Invalid lobe count')
    grad=value['gradient']
    for expected,g in zip(names,value['lobes']):
        if not isinstance(g,dict) or set(g)!={'name','path','heat'} or g['name']!=expected or not isinstance(g['heat'],dict) or set(g['heat'])!={'cx','cy','L','W'}:
            raise ValueError('Invalid lobe identity or heat fields')
        p=g['path']
        if not isinstance(p,str) or not 1 <= len(p) <= 4096 or re.search(r'nan|inf',p,re.I):
            raise ValueError('Invalid Rear lobes path')
        tokens=re.findall(r'[MLCZ]|'+NUMBER,p)
        if re.sub(r'[MLCZ]|'+NUMBER+'|[ ,\t\r\n]','',p) or not tokens or tokens[0]!='M' or tokens[-1]!='Z':
            raise ValueError('Unsupported Rear lobes path grammar')
        i=0; commands=0
        while i<len(tokens):
            command=tokens[i]; i+=1; commands+=1
            if command not in {'M','L','C','Z'} or (command=='M' and commands!=1) or (command=='Z' and i!=len(tokens)):
                raise ValueError('Invalid Rear lobes path command order')
            count={'M':2,'L':2,'C':6,'Z':0}[command]
            if i+count>len(tokens): raise ValueError('Incomplete Rear lobes path')
            for token in tokens[i:i+count]:
                if not re.fullmatch(NUMBER,token): raise ValueError('Incomplete Rear lobes coordinate group')
                finite(float(token),0,14)
            i+=count
        if commands<3 or commands>128: raise ValueError('Rear lobes path complexity')
        # Every Bezier control point stays within the fixed canvas; mirrored
        # counterparts are affine, so their entire curves remain bounded too.
        numeric=[float(t) for t in tokens if re.fullmatch(NUMBER,t)]
        if any(not 0<=n<=(12 if i%2==0 else 14) for i,n in enumerate(numeric)):
            raise ValueError('Occupied lobe geometry clipping forbidden')
        for key,n in g['heat'].items(): finite(n,.01 if key in {'L','W'} else -100,100)
    if not isinstance(grad,dict) or set(grad)!={'type','stops'} or grad['type']!='elliptical-radial' or not isinstance(grad['stops'],list) or not 2<=len(grad['stops'])<=16:
        raise ValueError('Invalid Rear lobes gradient')
    last=-1
    for stop in grad['stops']:
        if (not isinstance(stop,list) or len(stop)!=2 or not isinstance(stop[0],str) or
                not re.fullmatch(NUMBER,stop[0]) or not isinstance(stop[1],str) or not re.fullmatch('#[0-9a-fA-F]{6}',stop[1])):
            raise ValueError('Invalid Rear lobes gradient stop')
        n=float(stop[0]);finite(n,0,1)
        if n<=last: raise ValueError('Rear lobes gradient offsets must increase')
        last=n
    if float(grad['stops'][0][0])!=0 or last!=1: raise ValueError('Rear lobes gradient endpoint missing')
    return value


DRIVER = r'''
const fs=require('fs'), sharp=require(process.argv[1]);
const req=JSON.parse(fs.readFileSync(0,'utf8'));
if(process.version!==req.node || process.platform!=='linux' || process.arch!=='x64' || JSON.stringify(sharp.versions)!==JSON.stringify(req.versions)) throw Error('Exact renderer profile mismatch');
sharp.cache(false);sharp.concurrency(1);
const specs=req.master.lobes, stops=req.master.gradient.stops, selector=req.master.selector;
function defs(g,masked){let t=`<radialGradient id="heat-${g.name}" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="matrix(${g.heat.L} 0 0 ${g.heat.W} ${g.heat.cx} ${g.heat.cy})">${stops.map(([o,c])=>`<stop offset="${o}" stop-color="${c}"/>`).join('')}</radialGradient>`;if(masked)t+=`<mask id="edge-${g.name}" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="0" y="0" width="12" height="14"><path d="${g.path}" fill="white"/>${Array.from({length:32},(_,i)=>{const t=(32-i)/32,a=.62+.38*t*t*(3-2*t),v=Math.round(255*a);return `<path d="${g.path}" fill="none" stroke="rgb(${v},${v},${v})" stroke-width="${.60*t}" stroke-linejoin="round"/>`;}).join('')}</mask>`;return t;}
function svg(masked=true){const one=g=>`<path d="${g.path}" fill="url(#heat-${g.name})"${masked?` mask="url(#edge-${g.name})"`:''}/>`;
const pair=specs.slice(0,2).map(one).join('\n');
if(selector===203)return `<svg xmlns="http://www.w3.org/2000/svg" width="96" height="112" viewBox="0 0 12 14">\n<!-- NEW P10 MODE1 CANDIDATE, NOT FROZEN. 203. Four smooth cubic lobes;12x14 anchor0,0. -->\n<defs>${specs.map(g=>defs(g,masked)).join('')}</defs>\n\n${pair}\n<g transform="translate(0 14) scale(1 -1)">${pair}</g>\n\n</svg>\n`;
return `<svg xmlns="http://www.w3.org/2000/svg" width="96" height="112" viewBox="0 0 12 14">\n<!-- REVIEW-ONLY NEW P11 FIRST five-lobe candidate A2 raw43. Never frozen or admitted. -->\n<defs>${specs.map(g=>defs(g,masked)).join('')}</defs>\n\n${pair}\n<g transform="translate(0 14) scale(1 -1)">${pair}</g>\n${one(specs[2])}\n\n</svg>\n`;}
(async()=>{let rows=[];for(const d of [4,8]){const options={density:72*d/8,limitInputPixels:10752},w=12*d,h=14*d;
const {data,info}=await sharp(Buffer.from(svg(false)),options).ensureAlpha().raw().toBuffer({resolveWithObject:true});
const {data:soft,info:si}=await sharp(Buffer.from(svg()),options).ensureAlpha().raw().toBuffer({resolveWithObject:true});
if(info.width!==w||info.height!==h||info.channels!==4||JSON.stringify(si)!==JSON.stringify(info))throw Error('Geometry mismatch');
for(let i=0;i<data.length;i+=4){if(data[i+3])data[i+3]=Math.max(1,Math.min(data[i+3],soft[i+3]));else data.fill(0,i,i+4);}
for(const raw of [selector,selector===203?222:5]){const b=Buffer.alloc(data.length);for(let y=0;y<h;y++)for(let x=0;x<w;x++){const xx=raw===selector?x:w-1-x;data.copy(b,4*(y*w+x),4*(y*w+xx),4*(y*w+xx+1));}const png=await sharp(b,{raw:{width:w,height:h,channels:4}}).png().toBuffer();rows.push({raw,d,rgba:b.toString('base64'),png:png.toString('base64')});}}
process.stdout.write(JSON.stringify({svg:svg(),rows}));})().catch(e=>{process.stderr.write(String(e));process.exit(1)});
'''


def render(raw, include_svg=False):
    master=geometry(raw); selector=master['selector']
    request=json.dumps(dict(master=master,node=NODE_VERSION,versions=SHARP_VERSIONS)).encode()
    try:
        with tempfile.TemporaryDirectory(prefix='rear-lobes-data-') as tmp:
            with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
                result=subprocess.run([NODE,'--max-old-space-size=128','-e',DRIVER,SHARP],input=request,stdout=out,stderr=err,cwd=tmp,env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},timeout=30)
                if out.tell()>1024*1024 or err.tell()>128*1024 or result.returncode:raise ValueError('Rear lobes fixed renderer failed/profile mismatch')
                out.seek(0);response=json.loads(out.read())
    except (OSError,subprocess.TimeoutExpired) as exc:raise ValueError('Required Rear lobes renderer unavailable/timed out') from exc
    rows=response['rows'];mirror=222 if selector==203 else 5
    if [(r['d'],r['raw']) for r in rows]!=[(d,r) for d in (4,8) for r in (selector,mirror)]:raise ValueError('Unexpected Rear lobes renderer outputs')
    result={}
    for row in rows:
        d=row['d'];data=base64.b64decode(row['rgba'],validate=True);encoded=base64.b64decode(row['png'],validate=True)
        if len(data)!=12*14*d*d*4 or not any(data[3::4]):raise ValueError('Unexpected/empty Rear lobes renderer bytes')
        if any(any(data[p:p+3]) for p in range(0,len(data),4) if data[p+3]==0):raise ValueError('Hidden Rear lobes RGB')
        result[(1310000+row['raw'],d)]=(encoded,data)
    return (result,response['svg'].encode()) if include_svg else result


def generate(root, raw, candidate=False):
    selected=selection(root,raw,candidate)
    recipe(read(root,selected['recipe']['path'],128*1024))
    check_tool()
    rendered={}
    for row in selected['masters']:
        source=read(root,row['source_json'],64*1024)
        if geometry(source)['selector']!=row['selector']:raise ValueError('Independent master identity mismatch')
        rendered.update(render(source))
    rendered={pair:rendered[pair] for pair in PAIRS}
    pngs,blobs,rows={},{},[]
    for ordinal,((identity,density),(encoded,rgba)) in enumerate(rendered.items()):
        source=png(identity,density)
        if not candidate:
            if read(root,source)!=encoded or selected['resources'][ordinal]['source_sha256']!=sha(encoded):
                raise ValueError('Derived Rear lobes PNG does not match canonical geometry')
        pngs[source]=encoded
        blobs[(identity,density)]=struct.pack('<4s6I',b'HDR1',identity,density,12,14,0,0)+rgba
        rows.append(dict(identity=identity,density=density,source_png=source,source_sha256=sha(encoded)))
    return dict(selected,schema=SCHEMA,resources=rows),pngs,blobs


def input_paths(root):
    selected=selection(root,read(root,SELECTION,128*1024))
    return ({SELECTION,selected['recipe']['path']} | {r['source_json'] for r in selected['masters']}) | generated_paths() | {ROOT+'/'+name(*p) for p in PAIRS}


def verified_pins(root):
    return _assets(root)[1]


def payload_header(pins, p7_pins, rear39_pins, rear1_pins, rear281_pins):
    from current_rear_p7_compatibility import payload_header as compose_header
    return compose_header(p7_pins,rear39_pins,rear1_pins,rear281_pins,pins)

GOLDEN_MASTERS = {203: b'{\n  "schema": "rear-lobes-data-only-geometry-v1",\n  "selector": 203,\n  "lobes": [\n    {\n      "name": "inner",\n      "path": "M1.65 4 C.63 4 0 4.62 0 5.5 C0 6.35 .67 7 1.72 7 C4.28 7 7.73 6.5 11 5.55 C8.21 4.8 4.67 4 1.65 4Z",\n      "heat": {\n        "cx": 1.45,\n        "cy": 5.48,\n        "L": 9.1,\n        "W": 1.35\n      }\n    },\n    {\n      "name": "outer",\n      "path": "M4.65 1 C3.63 1 3 1.62 3 2.5 C3 3.35 3.67 4 4.72 4 C6.9 4 9.61 3.5 12 2.55 C9.94 1.8 7.08 1 4.65 1Z",\n      "heat": {\n        "cx": 4.45,\n        "cy": 2.48,\n        "L": 7.1,\n        "W": 1.35\n      }\n    }\n  ],\n  "gradient": {\n    "type": "elliptical-radial",\n    "stops": [\n      [\n        "0",\n        "#fffaa1"\n      ],\n      [\n        ".19",\n        "#fff06b"\n      ],\n      [\n        ".38",\n        "#ffd338"\n      ],\n      [\n        ".57",\n        "#ff9e1c"\n      ],\n      [\n        ".75",\n        "#ff680a"\n      ],\n      [\n        ".91",\n        "#ef3904"\n      ],\n      [\n        "1",\n        "#cd2102"\n      ]\n    ]\n  }\n}\n', 43: b'{\n  "schema": "rear-lobes-data-only-geometry-v1",\n  "selector": 43,\n  "lobes": [\n    {\n      "name": "outer",\n      "path": "M4.65 1 C3.66 1 3 1.57 3 2.36 C3 3.12 3.66 3.5 4.7 3.5 C7.05 3.5 9.67 3.02 12 2.45 C9.48 1.7 6.89 1 4.65 1Z",\n      "heat": {\n        "cx": 4.45,\n        "cy": 2.38,\n        "L": 7.2,\n        "W": 1.15\n      }\n    },\n    {\n      "name": "shoulder",\n      "path": "M2.65 3.5 C1.66 3.5 1 3.94 1 4.57 C1 5.3 1.69 5.75 2.72 5.75 C5.62 5.75 8.85 5.1 12 4.62 C8.86 4.07 5.61 3.5 2.65 3.5Z",\n      "heat": {\n        "cx": 2.45,\n        "cy": 4.55,\n        "L": 9.3,\n        "W": 1.01\n      }\n    },\n    {\n      "name": "central",\n      "path": "M1.7 5.75 C.66 5.75 0 6.25 0 7 C0 7.76 .68 8.25 1.73 8.25 C4.59 8.25 7.95 7.67 11.05 7 C7.88 6.35 4.59 5.75 1.7 5.75Z",\n      "heat": {\n        "cx": 1.45,\n        "cy": 6.98,\n        "L": 9.2,\n        "W": 1.3\n      }\n    }\n  ],\n  "gradient": {\n    "type": "elliptical-radial",\n    "stops": [\n      [\n        "0",\n        "#fffaa1"\n      ],\n      [\n        ".19",\n        "#fff06b"\n      ],\n      [\n        ".38",\n        "#ffd338"\n      ],\n      [\n        ".57",\n        "#ff9e1c"\n      ],\n      [\n        ".75",\n        "#ff680a"\n      ],\n      [\n        ".91",\n        "#ef3904"\n      ],\n      [\n        "1",\n        "#cd2102"\n      ]\n    ]\n  }\n}\n'}
GOLDEN_HASHES = {(1310203, 4): ('ba4d0730a7114f898f408cc58b3c2344822407bc61f7efef3fc89240a57304f0', 'a4fd9f5a611ec83a7ddec97ed672363c1f732c2aaf167d8013f3b6366c23ac07'), (1310222, 4): ('2725e53f13992d4d13c48e41d49b0856ca8b1db05ee5fe62f9c4dde0f4daa7b6', '8efb472f5b2d2caa21cfba1dfed09e3d55b531d0013bf0e43eba086528dfde2f'), (1310203, 8): ('9755e8122ecfe855db53e47d042543b5c12d5e428c3259bccec3eba7a3cc8504', '5204aa4d56d39e3fc963e8dbeafac2160a041dfedce848aa64efea562bb7cddc'), (1310222, 8): ('c7db44414b8c42699d2e8fe4e16218491083c0ddc7751744f7130e945f19ec18', '55ac245902845a6c948ca2c7f2496b43a1fb264701ffcdce16a11244c419b3d8'), (1310043, 4): ('003bb36141804fcb852714bed9c110eb150d1986e29168e692afaac9e94d4cab', '12841f6d5426de3634430634c78b931040a894cf471172e014ae96715b9fd85f'), (1310043, 8): ('35ec8f2e72bafec3a6de8d103b845ad48371c7962f6c9eb9c1bd7c11aad0baf0', '885c3e1fdaa19e6fb77d84fb32bb67fc1bc1ac67c9c37684c8e21846eb5ee34f'), (1310005, 4): ('de4790bedb60f7c824e859aa799d769153c4a1c37c2f45ba064bf9bb413e5b8f', 'f0d3dbb1189bfc399699640d634052967667ec4d1f3d92c907af3b6886faf720'), (1310005, 8): ('1846255e2115759c348f4d87abb14ae3044a537037c3efe0a1810e27c0770be0', '9d45728c323f6f9b5bb6cf8c619219f48104aeec1ff7ac503854f180ed01df5e')}
GOLDEN_SVG_HASHES = {203: 'a28bc94d1e0de5aef6cba45955b351397b4178c16fc4c81f4e643561afdbc43c', 43: '3179e9413dcd5daa2bac09c1783555c94dc171ece76cf4f36ea2632dffaf3f34'}

def check_tool():
    actual={}
    for selector,raw in GOLDEN_MASTERS.items():
        rendered,svg=render(raw,include_svg=True)
        if sha(svg)!=GOLDEN_SVG_HASHES[selector]:raise ValueError('Rear lobes generated SVG golden mismatch')
        actual.update({p:(sha(png),sha(rgba)) for p,(png,rgba) in rendered.items()})
    if actual!=GOLDEN_HASHES:raise ValueError('Rear lobes renderer eight-output golden mismatch')
