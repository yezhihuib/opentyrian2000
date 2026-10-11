"""Require independent grass/sand9 plus prior purple/gray oracles to reject temporary, narrowly scoped faults.

Only extracted test snippets are changed. No production source is modified.
Run the binder and alpha fixtures first, then provide their successful reports.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import resource
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--binder-report', required=True, type=Path)
p.add_argument('--alpha-report', required=True, type=Path)
p.add_argument('--report', type=Path)
a = p.parse_args()
bases = {kind: json.loads(path.read_text()) for kind, path in [('binder', a.binder_report), ('alpha', a.alpha_report)]}
assert all(base['status'] == 'passed' and base['source_stable'] for base in bases.values())
assert all(bases['binder']['source_sha256'][key] == value for key, value in bases['alpha']['source_sha256'].items())
mutations = [
 ('grass-wrong-layer', 'binder', 'helpers', 'layer==1&&(grass_sand_slot(id)>=0||', 'layer==4&&(grass_sand_slot(id)>=0||'),
 ('grass-first-slot-aliases-entity311', 'binder', 'helpers', 'return 312+i;', 'return 311+i;'),
 ('grass-last-slot-out-of-bounds', 'binder', 'helpers', 'return 312+i;', 'return 313+i;'),
 ('grass-contiguous-range-admitted', 'binder', 'helpers', 'for(int i=0;i<9;i++)if(id==ids[i])return 312+i;', 'for(int i=0;i<9;i++)if(id>=66&&id<=90){(void)ids;return 312+i;}'),
 ('grass-forest211-admitted', 'binder', 'helpers', '66,67,69,76,78,79,80,89,90', '66,67,69,76,78,79,80,89,211'),
 ('grass-member80-omitted', 'binder', 'helpers', '66,67,69,76,78,79,80,89,90', '66,67,69,76,78,79,81,89,90'),
 ('grass-selector-omitted', 'binder', 'helpers', 'if(slot<0)slot=grass_slot;', '(void)grass_slot;'),
 ('grass-missing-art-traced', 'binder', 'helpers', '||purple_slot>=0||grass_slot>=0)&&!a', '||purple_slot>=0)&&!a'),
 ('grass-loader-hook-removed', 'binder', 'loader', 'render_mirror_bind_terrain(1,z+1,megaData1.shapes[x].sh);', '(void)0;'),
 ('grass-alias-same-id-uses-other-slot', 'binder', 'helpers', 'if(slot<0)slot=grass_slot;', 'if(slot<0&&grass_slot>=0)slot=312;'),
 ('grass-layer1-normal-forced-shadow', 'alpha', 'helpers', 'draw_asset(x+tile*24,y,a,style,NULL)', 'draw_asset(x+tile*24,y,a,grass_slot>=0?MIRROR_SHADOW:style,NULL)'),
 ('grass-replacement-bit-shifted', 'binder', 'helpers', 'replaced|=1u<<tile;', 'replaced|=1u<<(tile+1);'),

 ('wrong-layer', 'binder', 'helpers', 'layer==3&&(layer3_gray_slot(id)>=0||layer3_purple_slot(id)>=0)', 'layer==4&&(layer3_gray_slot(id)>=0||layer3_purple_slot(id)>=0)'),
 ('wrong-bank', 'binder', 'helpers', "terrain_file=='z'&&", 'true&&'),
 ('wrong-slot', 'binder', 'helpers', 'return 290+i;', 'return 289+i;'),
 ('future-entity-slot-used', 'binder', 'helpers', 'return 290+i;', 'return 303+i;'),
 ('whitelist-widened', 'binder', 'helpers', '150,156,157,158,159,160,166,168,169,170,176,177,178', '150,156,157,158,159,160,166,168,169,170,176,177,179'),
 ('cross-reuse-id-omitted', 'binder', 'helpers', '150,156,157,158,159,160,166,168,169,170,176,177,178', '150,156,157,158,161,160,166,168,169,170,176,177,178'),
 ('purple-shadow-not-guarded', 'binder', 'helpers', '(gray_slot>=0||purple_slot>=0)&&style!=MIRROR_NORMAL', 'gray_slot>=0&&style!=MIRROR_NORMAL'),
 ('unknown-styles-not-guarded', 'binder', 'helpers', '(gray_slot>=0||purple_slot>=0)&&style!=MIRROR_NORMAL', '(gray_slot>=0||purple_slot>=0)&&(style==MIRROR_BLEND||style==MIRROR_SHADOW)'),
 ('missing-art-traced', 'binder', 'helpers', '||gray_slot>=0||purple_slot>=0||grass_slot>=0)&&!a', '||gray_slot>=0||grass_slot>=0)&&!a'),
 ('map-reset-removed', 'binder', 'helpers', 'terrain_source_count=0;', 'terrain_source_count=terrain_source_count;'),
 ('overflow-guard-one-too-late', 'binder', 'helpers', 'terrain_source_count<162', 'terrain_source_count<163'),
 ('loader-hook-removed', 'binder', 'loader', 'render_mirror_bind_terrain(3,z+1,megaData3.shapes[x].sh);', '(void)0;'),
 ('byte-equality-alias', 'binder', 'helpers', 'map[tile]==terrain_sources[k].data', 'terrain_sources[k].data&&memcmp(map[tile],terrain_sources[k].data,672)==0'),
 ('null-pointer-admitted', 'binder', 'helpers', 'if(map[tile]&&map[tile]==terrain_sources[k].data)', 'if(map[tile]==terrain_sources[k].data)'),
 ('alias-last-wins', 'binder', 'helpers', 'id=terrain_sources[k].id;break;', 'id=terrain_sources[k].id;'),
 ('opaque-holes-filled', 'alpha', 'helpers', 'if(!src[3])continue;', 'if(!src[3]){* ((Uint32 *)((Uint8 *)canvas->pixels+dy*canvas->pitch)+dx)=0xff010203u;continue;}'),
 ('alpha-fraction-discarded', 'alpha', 'helpers', 'talon_blend?(src[3]+1)/2:src[3]', 'talon_blend?(src[3]+1)/2:255'),
 ('original-indexed-write-removed', 'alpha', 'helpers', '*pixels = *data; render_mirror_terrain_pixel', '*pixels = *pixels; render_mirror_terrain_pixel'),
 ('original-holes-written', 'alpha', 'helpers', 'pixels >= pixels_ll && *data != 0', 'pixels >= pixels_ll'),
 ('replacement-bit-dropped', 'alpha', 'helpers', '(hd_tiles&(1u<<tile))!=0', '((void)hd_tiles,false)'),
 ('transparent-cloud-owner-cleared', 'alpha', 'helpers', 'suppress_cloud=replaced;', 'suppress_cloud=false;'),
 ('hd-owner-not-preserved', 'alpha', 'helpers', 'memset(hd_owner+(y*d+sy)*canvas->w+x*d,game_probe_original_reference?2:1,(size_t)d);', 'memset(hd_owner+(y*d+sy)*canvas->w+x*d,0,(size_t)d);'),
 ('opaque-cloud-provenance-preserved', 'alpha', 'helpers', 'cloud_owner[owner_index]=cloud?1:0;', 'cloud_owner[owner_index]=1;'),
]
root = Path(tempfile.mkdtemp(prefix='grass-sand-mutations-'))
results = []
for name, kind, target, old, new in mutations:
    work = Path(bases[kind]['work'])
    directory = root/name
    directory.mkdir()
    helper = (work/'production-helpers.inc').read_text()
    loader = (work/'production-loader.inc').read_text() if kind == 'binder' else ''
    text = helper if target == 'helpers' else loader
    assert text.count(old) == 1, (name, text.count(old))
    for filename in ['production-types.inc'] + (['original-map.inc'] if kind == 'binder' else []):
        (directory/filename).write_bytes((work/filename).read_bytes())
    (directory/'production-helpers.inc').write_text(helper.replace(old, new) if target == 'helpers' else helper)
    if kind == 'binder':
        (directory/'production-loader.inc').write_text(loader.replace(old, new) if target == 'loader' else loader)
    command = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-I'+str(directory), str(HERE/f'test-grass-sand-{kind}.c'), '-o', str(directory/'test')]
    build = subprocess.run(command, text=True, capture_output=True)
    (directory/'build.log').write_text(build.stdout+build.stderr)
    assert build.returncode == 0, (name, build.stderr)
    run = subprocess.run([str(directory/'test')]+([str(work)] if kind == 'binder' else []), text=True, capture_output=True, env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'), preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_CORE, (0, 0)))
    assert run.returncode != 0, name+' escaped the independent oracle'
    assert any(marker in run.stderr for marker in ['FAIL ', 'runtime error:', 'ERROR: AddressSanitizer:']), (name, run.stderr)
    (directory/'result.log').write_text(run.stdout+run.stderr)
    results.append({'mutation': name, 'oracle': kind, 'exit_code': run.returncode, 'rejected': True, 'first_diagnostic': run.stderr.splitlines()[0], 'command': command, 'mutation_before': old, 'mutation_after': new})
    print('REJECTED:', name, flush=True)
report = {'status': 'passed', 'mutants_rejected': len(results), 'work': str(root), 'results': results, 'source_sha256': bases['binder']['source_sha256'], 'oracle_sha256': {kind: hashlib.sha256((HERE/f'test-grass-sand-{kind}.c').read_bytes()).hexdigest() for kind in bases}, 'scope': 'Only temporary extracted snippets mutated; candidate source and fixture inputs unchanged. Unexpected process failures cannot count as a rejected mutation.'}
out = a.report or root/'result.json'
out.write_text(json.dumps(report, indent=2)+'\n')
print('Report:', out)
