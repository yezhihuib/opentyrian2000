"""Independent finite-layer3 oracle: extracted loader, binder, row and compositor.

No game runs or authored art. Synthetic HDA inputs and original lookup/blank
metadata are sufficient to exercise exact pointer ownership and fallback.
Temporary test inputs are retained, and no existing files are deleted.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
GRAY = [121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154]
OLD = [101,37,57,49,50,321,322,331,332,99,100,106,107,109,110,118,119,120,
       96,97,98,108,323,324,333,334,36,39,40,46,48,56,58,38,47,
       111,114,113,341,342,343,351,352,353]
CLOUD = [41,42,43,44,45,51,52,53,54,55,61,62,63,64,65]


def block(source, start):
    begin = source.index('{', start)
    depth, end = 1, begin + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end] + '\n'


def extract(source, name):
    m = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^\n;]*\)\s*\{', source, re.M)
    assert m, name
    return block(source, m.start())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, default=ROOT)
    p.add_argument('--sanitize', action='store_true')
    p.add_argument('--topology', type=Path, default=ROOT.parent/'tyrian-background-redraw/scene-analysis')
    p.add_argument('--data', type=Path, default=Path(os.environ.get('TYRIAN_DATA_DIR', ROOT.parent/'opentyrian-cloud-runtime/data/tyrian2000')))
    p.add_argument('--report', type=Path)
    a = p.parse_args()
    sources = {n:(a.source/'src'/n).read_text() for n in ['render_mirror.c','tyrian2.c','backgrnd.c']}
    source = sources['render_mirror.c']
    work = Path(tempfile.mkdtemp(prefix='layer3-gray-binder-'))
    patterns = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
                r'static Asset assets\[\d+\];',
                r'static struct \{const Uint8 \*data;unsigned int id;\} terrain_sources\[\d+\];']
    (work/'production-types.inc').write_text('\n'.join(re.search(q,source,re.S).group() for q in patterns))
    names = ['read_asset','scene_asset','render_mirror_map_begin','cloud_terrain_slot',
             'ground_terrain_slot','plateau_terrain_slot','underlay_terrain_slot','road_terrain_slot',
             'terrain_holes_slot','stone_foundation_slot','layer3_gray_slot',
             'render_mirror_bind_terrain','render_mirror_terrain_row']
    (work/'production-helpers.inc').write_text('\n'.join(extract(source,n) for n in names))
    ty = sources['tyrian2.c']
    loader = block(ty, ty.index('for (int z = 0; z < 600; z++)',ty.index('/* Read Shapes.DAT */')))
    assert loader.count('render_mirror_bind_terrain(3,z+1,megaData3.shapes[x].sh)') == 1, 'Missing or duplicate layer3 mirror hookup'
    (work/'production-loader.inc').write_text(loader)
    background = extract(sources['backgrnd.c'],'draw_background_3')
    assert 'blit_background_row(surface, mapX3Pos' in background and 'map += 15;' in background
    assert 'blit_background_row_blend' not in background
    assert 'render_mirror_terrain_row(surface,x,y,map,MIRROR_NORMAL)' in extract(sources['backgrnd.c'],'blit_background_row')
    # The hook stays in the original background3over branches. This is a source
    # topology assertion, not a claim about pixels from a runtime capture.
    positions = [m.start() for m in re.finditer(r'draw_background_3\(VGAScreen\)',ty)]
    assert len(positions) == 3
    for position in positions:
        assert 'background3over' in ty[max(0,position-200):position]
    metadata = []
    lookups = []
    for layer in [1,2,3]:
        f = a.topology/f'level9-layer{layer}-map.json'
        raw = f.read_bytes(); document = json.loads(raw)
        assert document['layer'] == layer
        assert (document['rows'],document['cols']) == ((300,14) if layer == 1 else (600,14 if layer == 2 else 15))
        assert len(document['lookup']) == 128
        lookups.append(document['lookup'])
        metadata.append({'path':str(f),'sha256':hashlib.sha256(raw).hexdigest()})
    # Verify the audit's lookup arrays directly against the immutable original
    # level bytes. The engine reads three128-word tables immediately before map1.
    level = (a.data/'tyrian1.lvl').read_bytes()
    assert hashlib.sha256(level).hexdigest() == '54cbb00b57b84aa992a70cfcb170cb1edeb59507873723630d60080ba8351352'
    first_map = json.loads((a.topology/'level9-layer1-map.json').read_bytes())['offset']
    for layer in range(3):
        offset = first_map - 3*256 + layer*256
        assert list(struct.unpack('>128H',level[offset:offset+256])) == lookups[layer]
    raw = (a.data/'shapesz.dat').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248'
    blank = []; offset = 0
    for _ in range(600):
        value = raw[offset]; offset += 1
        assert value in [0,1]
        blank.append(value)
        if not value: offset += 672
    assert offset <= len(raw)
    accepted = [set(OLD),set(CLOUD),set(GRAY)]
    counts = [sum(tile in accepted[layer] and (layer == 0 or not blank[tile-1])
                  for tile in lookups[layer][:72 if layer == 0 else 71 if layer == 1 else 70]) for layer in range(3)]
    assert counts == [45,15,18], counts
    (work/'original-map.inc').write_text('static const uint16_t actual_lookup[3][128]={' + ','.join('{'+','.join(map(str,v))+'}' for v in lookups) + '};\nstatic const bool actual_blank[600]={' + ','.join(map(str,blank)) + '};\n')
    # Pure test payloads, deliberately including alpha0/1/127/128/254/255.
    def write_pack(label, density, omit=(), bad=None):
        directory = work/label; directory.mkdir()
        for tile in OLD+CLOUD+GRAY:
            if tile in omit: continue
            header = [2010000+tile,density,24,28,0,0]
            rgba = bytes(v for y in range(28*density) for x in range(24*density)
                         for v in [(tile+x*3+y)%256,(tile*3+x+y*5)%256,(tile*7+x*11+y)%256,[0,1,127,128,254,255][(x+2*y+tile)%6]])
            data = struct.pack('<4s6I',b'HDR1',*header)+rgba
            if bad is not None and tile == GRAY[0]:
                if bad in range(6): header[bad] += 1; data = struct.pack('<4s6I',b'HDR1',*header)+rgba
                elif bad == 6: data += b'X'
                elif bad == 7: data = b'BAD1'+data[4:]
                elif bad == 8: data = data[:28]
                elif bad == 9: data = data[:-1]
                else: data = data[:bad-10]
            (directory/f'terrain-shapesz-{tile}-{density}.hda').write_bytes(data)
    write_pack('full8',8);write_pack('full4',4)
    # Invalid input packs need only one selected ID; avoid copying unrelated art.
    for bad in range(38): write_pack(f'bad{bad}',8,omit=set(OLD+CLOUD+GRAY[1:]),bad=bad)
    (work/'empty').mkdir()
    for tile in GRAY:
        directory = work/f'missing{tile}';directory.mkdir()
        for other in GRAY:
            if other != tile:
                os.link(work/'full8'/f'terrain-shapesz-{other}-8.hda',directory/f'terrain-shapesz-{other}-8.hda')
    command = [os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-I'+str(work),str(Path(__file__).with_suffix('.c')),'-o',str(work/'test')]
    if a.sanitize: command += ['-fsanitize=address,undefined','-fno-omit-frame-pointer']
    build = subprocess.run(command,text=True,capture_output=True)
    (work/'build.log').write_text(build.stdout+build.stderr)
    if build.returncode: raise RuntimeError(build.stderr)
    run = subprocess.run([str(work/'test'),str(work)],text=True,capture_output=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'))
    print(run.stdout,end='');print(run.stderr,end='')
    report = {'status':'passed' if run.returncode == 0 else 'failed','sanitize':a.sanitize,'exit_code':run.returncode,'command':command,'work':str(work),'stdout':run.stdout,'stderr':run.stderr,'source_sha256':{n:hashlib.sha256(s.encode()).hexdigest() for n,s in sources.items()},'source_stable':all(s==(a.source/'src'/n).read_text() for n,s in sources.items()),'metadata':metadata,'level9_registered_slots_by_layer':counts,'level9_registered_slots':sum(counts),'distinct_accepted_ids':len(OLD+CLOUD+GRAY),'registry_capacity':140,'synthetic_maximum_original_loop_slots':213,'scope':'Finite reviewed level9 bankZ family; original loader loops including duplicate351 and source pointers, no gameplay run, capture or authored art.'}
    out = a.report or work/'result.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print('Report:',out)
    run.check_returncode();assert report['source_stable']


if __name__ == '__main__': main()
