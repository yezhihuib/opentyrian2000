"""One canonical P7 SVG -> four role131 transports; no eligibility changes."""
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

IDS = (1310294, 1310295)
SELECTORS = (294,)
PAIRS = tuple((identity, density) for density in (4,8) for identity in IDS)
SELECTION = 'assets/hd/authoring/rear-p7-current.json'
MAPPING = 'packaging/current-rear-p7-compatibility.json'
HEADER = 'src/current_rear_multi_payload_pins.h'
ROOT = 'assets/hd/current-compat/rear-p7'
INPUT_ROOT = 'authoring-inputs/rear-p7-current'
SCHEMA = 'opentyrian-current-rear-p7-authoring-v1'
CANDIDATE_SCHEMA = 'opentyrian-current-rear-p7-candidate-v1'
RECIPE = {'schema': 'rear-p7-fixed-recipe-v1', 'logical_size': [12, 14], 'anchor': [0, 0], 'densities': [4, 8], 'canonical': 294, 'derived': 295, 'relationship': 'full-canvas-horizontal-RGBA-flip', 'alpha': 'zero-RGB-when-alpha-zero', 'renderer': 'independent-SVG-render-per-density', 'png': 'compression9-adaptiveFilteringfalse-palettefalse'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate Rear P7 JSON key: ' + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('Non-finite Rear P7 JSON number: ' + value)

    if len(raw) > 128 * 1024:
        raise ValueError('Oversize Rear P7 JSON')
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def read(root, name, limit=16 * 1024 * 1024):
    p = path(root, name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode) or p.stat().st_size > limit:
        raise ValueError('Missing/oversize regular Rear P7 input: ' + name)
    return p.read_bytes()


def name(identity, density):
    if type(identity) is not int or type(density) is not int or (identity, density) not in PAIRS:
        raise ValueError('Unknown Rear P7 projectile identity/density')
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
        raise ValueError('Invalid Rear P7 candidate/installed schema or fields')
    if not isinstance(selected['version'], str) or not 1 <= len(selected['version']) <= 128:
        raise ValueError('Invalid Rear P7 version')
    if not isinstance(selected['masters'], list) or len(selected['masters']) != 1:
        raise ValueError('Expected one Rear P7 master')
    for selector, row in zip(SELECTORS, selected['masters']):
        if (not isinstance(row, dict) or set(row) != {'selector','source_svg','source_sha256'} or
                type(row['selector']) is not int or row['selector'] != selector or
                row['source_svg'] != INPUT_ROOT + f'/master-{selector}.svg' or not is_hash(row['source_sha256'])):
            raise ValueError('Invalid Rear P7 master identity/path/hash/order')
        if sha(read(root, row['source_svg'])) != row['source_sha256']:
            raise ValueError('Selected Rear P7 master changed')
    row = selected['recipe']
    if (not isinstance(row, dict) or set(row) != {'path','sha256'} or
            row['path'] != INPUT_ROOT + '/recipe.json' or not is_hash(row['sha256']) or
            sha(read(root, row['path'])) != row['sha256']):
        raise ValueError('Invalid/changed Rear P7 recipe record')
    if not candidate:
        if not isinstance(selected['resources'], list) or len(selected['resources']) != 4:
            raise ValueError('Expected four derived Rear P7 pieces')
        for (identity, density), row in zip(PAIRS, selected['resources']):
            if (not isinstance(row, dict) or set(row) != {'identity', 'density', 'source_png', 'source_sha256'} or
                    type(row['identity']) is not int or type(row['density']) is not int or
                    (row['identity'], row['density']) != (identity, density) or
                    row['source_png'] != png(identity, density) or not is_hash(row['source_sha256'])):
                raise ValueError('Invalid derived Rear P7 identity/density/path/order/hash')
    return selected


def recipe(raw):
    result = parse(raw)
    # JSON comparison distinguishes bool/float substitutions in fixed integers.
    if json.dumps(result, sort_keys=True) != json.dumps(RECIPE, sort_keys=True):
        raise ValueError('Fixed Rear P7 recipe identity/geometry/resize changed')
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
            raise ValueError('Rear P7 HDA does not match master+fixed recipe: ' + source)
        row = dict(identity=identity, density=density, source_path=source, destination=destination, sha256=sha(blob))
        rows.append(row)
        result[destination] = row
        pins[(identity, density)] = fnv(blob[28:])
    expected = dict(schema='opentyrian-current-rear-p7-compatibility-v1', selection=SELECTION,
                    version=selected['version'], files=rows)
    if json.dumps(mapping, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Invalid/stale Rear P7 compatibility mapping')
    return result, pins


def load_assets(root):
    """Validate own complete derivation; shared-header candidate replacement is separate."""
    return _assets(root)[0]


def load(root):
    result,pins=_assets(root)
    from current_rear39_compatibility import verified_pins as rear39_pins
    from current_rear1_compatibility import verified_pins as rear1_pins
    if read(root, HEADER) != payload_header(pins,rear39_pins(root),rear1_pins(root)):
        raise ValueError('Stale Rear P7 payload pins')
    return result

SHARP_VERSIONS = {'aom': '3.15.1', 'archive': '3.8.9', 'cairo': '1.18.6', 'cgif': '0.5.4', 'exif': '0.6.26', 'expat': '2.8.5', 'ffi': '3.8.0', 'fontconfig': '2.18.3', 'freetype': '2.14.3', 'fribidi': '1.0.17', 'glib': '2.90.0', 'harfbuzz': '14.5.0', 'heif': '1.23.5', 'highway': '1.4.0', 'imagequant': '2.4.1', 'lcms': '2.19.1', 'mozjpeg': '0826579', 'pango': '1.58.2', 'pixman': '0.46.4', 'png': '1.6.58', 'proxy-libintl': '0.5', 'rsvg': '2.63.2', 'tiff': '4.7.2', 'uhdr': '2.0.2', 'vips': '8.18.7', 'webp': '1.6.0', 'xml2': '2.15.4', 'zlib-ng': '2.3.3', 'sharp': '0.35.5'}
FROZEN_PAYLOADS = ['d69e2fd8ed1cdb9a', 'bc5d0f4e9ce3a2f5', 'cdbad24a07cc4bcc', '9865a7591564a632', 'bde3dec5a72e74ea', 'fbe5d66e31b926c3', '9e771e4007d4d19a', '849cbdc14cf48e3f', '70952d574e97bd4e', 'c4bee58c37788fcb', '07ea794dc7b7047e', '152002ea2a7ec6e7', 'e282898d9cb39ce5', '27e07fd8d6be79d5', 'ec9c021ef9b7011d', '313c0fe52e7fa8e1', '218c1be6c8a3476c', '5f99f26278e7afb6', '0000000000000000', '888f7807cb7fb1b7', '0000000000000000', '79d684e2a12caa1f', 'f03f8f745a244970', '3df2a878cda365e6', '3fae8a76be180e70', 'b953b3abd4a3fcde', '5dfd9280619f61ea', '8b30be3de1092cad', 'b46a6834350f7c50', '78180b46cf51908e', '470d7a694cb1ea34', '5f7e6c19434fbaca', 'f6b1a647ab2530f4', '8e3a148548c298c2', 'fe4f61938de0c031', '60735166b4a9ea50', '73bdb95e757a0f29', '826ac5b753ea8b84', '061487c852b091c4', 'fe0fee22f015d496', 'f997db7d88b22d04', 'c832a79db1a7d312', 'ac10f74cff7c73e8', '625ed5d5dc2be74c', '10bb72f75e86c13c', 'b1a39b640c2f3340', 'ee810e2190d8d938', 'e208230d3c48d0f7', '16a1fd75aa93ab00', 'f475bf2a22b295b3']

NODE = '/opt/codex/runtimes/codex-primary-runtime/dependencies/node/bin/node'
SHARP = '/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs'
NODE_VERSION = 'v24.22.1'
DRIVER = r'''
const fs=require('fs'), sharp=require(process.argv[1]);
const req=JSON.parse(fs.readFileSync(0,'utf8'));
if(process.version!==req.node || JSON.stringify(sharp.versions)!==JSON.stringify(req.versions)) throw Error('Exact renderer profile mismatch');
sharp.cache(false); sharp.concurrency(1);
(async()=>{let out=[]; for(const d of [4,8]) {
const {data,info}=await sharp(Buffer.from(req.svg,'base64'),{density:72*d/8,limitInputPixels:10752}).ensureAlpha().raw().toBuffer({resolveWithObject:true});
if(info.width!==12*d||info.height!==14*d||info.channels!==4) throw Error('Geometry mismatch');
for(let p=0;p<data.length;p+=4) if(data[p+3]===0) data.fill(0,p,p+3);
for(const id of [294,295]) {let rgba=Buffer.from(data);
if(id===295) for(let y=0;y<info.height;y++) for(let x=0;x<info.width;x++) data.copy(rgba,(y*info.width+x)*4,(y*info.width+info.width-1-x)*4,(y*info.width+info.width-x)*4);
const png=await sharp(rgba,{raw:{width:info.width,height:info.height,channels:4}}).png({compressionLevel:9,adaptiveFiltering:false,palette:false}).toBuffer();
out.push({id,d,rgba:rgba.toString('base64'),png:png.toString('base64')});}}
process.stdout.write(JSON.stringify(out));})().catch(e=>{process.stderr.write(String(e));process.exit(1)});
'''


def svg(raw):
    """Bounded local vector grammar: no external resources, entities, CSS or code."""
    import xml.etree.ElementTree as ET
    try:
        text = raw.decode('utf-8', errors='strict')
    except UnicodeDecodeError as exc:
        raise ValueError('Rear P7 SVG must be UTF-8') from exc
    if len(raw)>64*1024 or '\x00' in text or '<!' in text.replace('<!--','') or '<?' in text:
        raise ValueError('Unsafe/oversize Rear P7 SVG')
    try:
        tree=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError('Malformed Rear P7 SVG') from exc
    ns='{http://www.w3.org/2000/svg}'
    attrs={'svg':{'width','height','viewBox'},'defs':set(),'radialGradient':{'id','cx','cy','r','gradientUnits','gradientTransform'},'stop':{'offset','stop-color','stop-opacity'},'path':{'d','fill','fill-opacity'},'g':{'transform','fill','opacity'}}
    if tree.tag != ns+'svg' or tree.attrib != {'width':'96','height':'112','viewBox':'0 0 12 14'}:
        raise ValueError('Fixed Rear P7 SVG geometry changed')
    nodes=list(tree.iter())
    if len(nodes)>256:
        raise ValueError('Too many Rear P7 SVG nodes')
    def depth(node, level=0):
        if level > 16:
            raise ValueError('Rear P7 SVG nesting too deep')
        for child in node:
            depth(child, level+1)
    depth(tree)
    for node in nodes:
        tag=node.tag.removeprefix(ns)
        if node.tag!=ns+tag or tag not in attrs or set(node.attrib)-attrs[tag]:
            raise ValueError('Unsupported Rear P7 SVG element/attribute')
        if (node.text or '').strip() or (node.tail or '').strip():
            raise ValueError('Unexpected SVG text')
        for key,value in node.attrib.items():
            if len(value)>8192 or not re.fullmatch(r'[A-Za-z0-9 #.,()+%\-]*',value):
                raise ValueError('Unsupported SVG value')
            if key in {'d','transform','gradientTransform','cx','cy','r','offset','stop-opacity','fill-opacity','opacity'}:
                if re.search(r'nan|inf(?:inity)?', value, re.IGNORECASE):
                    raise ValueError('Nonfinite Rear P7 SVG token')
                numbers = re.findall(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?', value)
                if any(not math.isfinite(float(n)) or abs(float(n)) > 10000 for n in numbers):
                    raise ValueError('Nonfinite/unbounded Rear P7 SVG number')
            if key=='fill' and value not in ('none','url(#streak)') and not re.fullmatch(r'#[0-9a-fA-F]{6}',value):
                raise ValueError('Nonlocal SVG fill')
            if key=='id' and value!='streak':
                raise ValueError('Unknown SVG gradient')
    return raw


def render(raw):
    svg(raw)
    request=json.dumps(dict(svg=base64.b64encode(raw).decode(),node=NODE_VERSION,versions=SHARP_VERSIONS)).encode()
    try:
        with tempfile.TemporaryDirectory(prefix='rear-p7-svg-') as tmp:
            with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
                result=subprocess.run([NODE,'--max-old-space-size=128','-e',DRIVER,SHARP],input=request,stdout=out,stderr=err,cwd=tmp,env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},timeout=30)
                if out.tell()>1024*1024 or err.tell()>128*1024 or result.returncode:
                    raise ValueError('Rear P7 fixed SVG renderer failed/profile mismatch')
                out.seek(0); rows=json.loads(out.read())
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise ValueError('Required Rear P7 renderer unavailable/timed out') from exc
    if [(x['id'],x['d']) for x in rows]!=[(294,4),(295,4),(294,8),(295,8)]:
        raise ValueError('Unexpected renderer outputs')
    result={}
    for row in rows:
        rgba=base64.b64decode(row['rgba'],validate=True); pngbytes=base64.b64decode(row['png'],validate=True)
        if len(rgba)!=12*14*row['d']**2*4:
            raise ValueError('Unexpected renderer byte length')
        result[(1310000+row['id'],row['d'])]=(pngbytes,rgba)
    return result


def generate(root, raw, candidate=False):
    selected=selection(root,raw,candidate)
    recipe(read(root,selected['recipe']['path'],128*1024))
    check_tool()
    rendered=render(read(root,selected['masters'][0]['source_svg'],64*1024))
    pngs,blobs,rows={},{},[]
    for ordinal,((identity,density),(encoded,rgba)) in enumerate(rendered.items()):
        source=png(identity,density)
        if not candidate:
            if read(root,source)!=encoded or selected['resources'][ordinal]['source_sha256']!=sha(encoded):
                raise ValueError('Derived Rear P7 PNG does not match canonical SVG')
        pngs[source]=encoded
        blobs[(identity,density)]=struct.pack('<4s6I',b'HDR1',identity,density,12,14,0,0)+rgba
        rows.append(dict(identity=identity,density=density,source_png=source,source_sha256=sha(encoded)))
    return dict(selected,schema=SCHEMA,resources=rows),pngs,blobs


def input_paths(root):
    selected=selection(root,read(root,SELECTION,128*1024))
    return {SELECTION,selected['recipe']['path'],selected['masters'][0]['source_svg']} | generated_paths() | {ROOT+'/'+name(*p) for p in PAIRS}


def payload_header(pins, rear39_pins=None, rear1_pins=None):
    if set(pins)!=set(PAIRS):
        raise ValueError('Expected four Rear P7 payload pins')
    values=list(FROZEN_PAYLOADS)
    for (identity,density),value in pins.items():
        if not isinstance(value,str) or re.fullmatch('[0-9a-f]{16}',value) is None:
            raise ValueError('Invalid Rear P7 payload pin')
        values[(17+identity-1310294)*2+(density==8)]=value
    if rear39_pins is not None:
        expected={(1310000+raw,d) for raw in (39,40,41) for d in (4,8)}
        if set(rear39_pins)!=expected:
            raise ValueError('Expected six Rear39 payload pins')
        for (identity,density),value in rear39_pins.items():
            if not isinstance(value,str) or re.fullmatch('[0-9a-f]{16}',value) is None:
                raise ValueError('Invalid Rear39 payload pin')
            values[{1310039:0,1310040:12,1310041:26}[identity]+(density==8)]=value
    if rear1_pins is not None:
        expected={(1310000+raw,d) for raw in (1,2,3,77) for d in (4,8)}
        if set(rear1_pins)!=expected:
            raise ValueError('Expected eight Rear1 payload pins')
        for (identity,density),value in rear1_pins.items():
            if not isinstance(value,str) or re.fullmatch('[0-9a-f]{16}',value) is None:
                raise ValueError('Invalid Rear1 payload pin')
            values[{1310001:2,1310002:14,1310003:28,1310077:16}[identity]+(density==8)]=value
    pairs=['{UINT64_C(0x'+values[i]+'),UINT64_C(0x'+values[i+1]+')}' for i in range(0,50,2)]
    return ('/* Generated Rear P7 payload-only override; all other Rear pins frozen. */\n#ifndef CURRENT_REAR_MULTI_PAYLOAD_PINS_H\n#define CURRENT_REAR_MULTI_PAYLOAD_PINS_H\n#ifndef REAR_P1_RGBA_PINS\n#define REAR_P1_RGBA_PINS {'+','.join(pairs)+'}\n#endif\n#endif\n').encode()

GOLDEN_SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="96" height="112" viewBox="0 0 12 14">\n<!-- OFFLINE P7 MODE2 CANDIDATE. 294: two down-left luminous streaks. New semantic geometry; no raster tracing. Canvas12x14 anchor0,0. -->\n<defs><radialGradient id="streak" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="matrix(5.515432893255071 -5.515432893255071 1.145512985522207 1.145512985522207 1.35 9.5)"><stop offset="0" stop-color="#fffaa1"/><stop offset=".19" stop-color="#fff06b"/><stop offset=".38" stop-color="#ffd338"/><stop offset=".57" stop-color="#ff9e1c"/><stop offset=".75" stop-color="#ff680a"/><stop offset=".91" stop-color="#ef3904"/><stop offset="1" stop-color="#cd2102"/></radialGradient></defs>\n\n<path d="M1.4 11 C.48 11 0 10.3 0 9.35 C0 7.85 1.14 6.65 2.60 5.39 C4.42 3.79 6.91 1.99 8.72 1.10 Q8.9 1 9 1 C8.14 3.42 6.33 5.75 4.60 7.77 C3.4 9.20 3.21 10.98 1.4 11Z" fill="url(#streak)"/>\n<g transform="translate(3 3)"><path d="M1.4 11 C.48 11 0 10.3 0 9.35 C0 7.85 1.14 6.65 2.60 5.39 C4.42 3.79 6.91 1.99 8.72 1.10 Q8.9 1 9 1 C8.14 3.42 6.33 5.75 4.60 7.77 C3.4 9.20 3.21 10.98 1.4 11Z" fill="url(#streak)"/></g>\n\n</svg>\n'
GOLDEN_HASHES = {(1310294, 4): ('a754cf589003cddd5aaabfc398e7fbf12438d0e9eadbd9df733f06a9f73348d0', '42c6f3610a278c66a0090a1c4aa004ae8787743886ba0196843f94f8814fe2d5'), (1310295, 4): ('ea3b8db552eb5eee6e18aa34a55637dbece437a3cf740dc10a4774a91ba6b74a', 'd01518043d39bc0650bd6ca10d3879f80d3b46027ccd2e2e55b2e2ca2aa117e3'), (1310294, 8): ('d0a8b9184afadc6dfbd36cbf21f4054045dd641c556d31c3320a1cd4cc8f5657', '84a2158c54290b0372fc8438ec37932415c861d9f4e82b95241d81dffd265b29'), (1310295, 8): ('62591001aac9d2e6401417f718195906afd216612b0002a2ec09c736f2444308', 'cb0538152adaeb2aecaa441ecf42459c66cd3b74bfaa99f314043a6f80de56a7')}


def check_tool():
    actual=render(GOLDEN_SVG)
    if {p:(sha(png),sha(rgba)) for p,(png,rgba) in actual.items()}!=GOLDEN_HASHES:
        raise ValueError('Rear P7 exact SVG renderer golden mismatch')


def verified_pins(root):
    return _assets(root)[1]
