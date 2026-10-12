"""Bounded independent guided-bomb family19/171/20/21 binder/real-RGBA/source-scope tests.

No game process, screenshots, renderer disable, source writes, or art edits.
Extracts and compiles the actual supplied production helpers unchanged. Pass
--mutations to require targeted wrong implementations to fail the oracle.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, struct, subprocess, tempfile
from PIL import Image
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BINDING_BLOCK = """ if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE) {
  static const unsigned int guided_ids[4]={19,171,20,21};
  for(int i=0;i<4;i++)if(index==guided_ids[i]){slot=326+i;role=8;break;}
 }
"""
TARGET_IDS = [19,171,20,21]
REGION_BLOCK = '/* Fixed presentation bookkeeping budget; gameplay pools are unchanged. */\n#define HD_REGION_CAPACITY 65536\nstatic HdRegion regions[HD_REGION_CAPACITY];'
FUNCTIONS = ['palette_rgb', 'complete_turret_group', 'restore_classic_rect',
             'blend_rgba', 'cloud_asset', 'darken_rgba', 'decode_tile', 'read_asset',
             'explosion_asset_slot', 'get_asset', 'talon_frame',
             'enemy_filter_rgba', 'explosion_asset_blend_rgba',
             'green_background_snapshot', 'green_background_peak',
             'green_head_composite', 'draw_asset_filtered', 'draw_asset',
             'render_mirror_entity', 'render_mirror_enemy_shot', 'render_mirror_entity_end']
TYPE_PATTERNS = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
                 r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',
                 r'typedef struct \{ Asset \*asset; int x,y; \} GreenHead;',
                 r'typedef struct \{ Uint16 peak\[16\]\[14\]; \} GreenBackground;',
                 r'typedef struct \{ SDL_Rect rect; int bank,index,style; bool live; \} HdRegion;',
                 r'static Asset assets\[\d+\];', r'static Asset talon_frames\[13\];',
                 r'#define HD_REGION_CAPACITY 65536', r'static HdRegion regions\[HD_REGION_CAPACITY\];']
def sha(data): return hashlib.sha256(data).hexdigest()
def extract(source, name):
    m = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert m, name
    start = source.index('{', m.start()); end = start + 1; depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}'); end += 1
    return source[m.start():end] + '\n'
def source_scope(source_dir, contract):
    contents = {str(p.relative_to(source_dir)): p.read_bytes() for p in sorted((source_dir/'src').rglob('*')) if p.is_file()}
    baseline = contract['baseline_files']
    assert set(contents) == set(baseline), 'Source/header inventory changed'
    changed = [name for name, data in contents.items() if sha(data) != baseline[name]]
    assert changed == ['src/render_mirror.c'], changed
    source = contents['src/render_mirror.c'].decode()
    assert source.count('static Asset assets[330];') == 1
    assert source.count(BINDING_BLOCK) == 1
    assert source.count(REGION_BLOCK) == 1
    reversed_source = source.replace('static Asset assets[330];', 'static Asset assets[326];').replace(BINDING_BLOCK, '')
    assert sha(reversed_source.encode()) == baseline['src/render_mirror.c'], 'Out-of-scope renderer changes'
    return source, {'changed_files':changed,'source_files_checked':len(contents),
        'candidate_renderer_sha256':sha(contents['src/render_mirror.c']), 'baseline_renderer_sha256':baseline['src/render_mirror.c'],
        'exact_renderer_changes':['capacity326-to330','finite-player-bank8-TILE19/171/20/21-slots326/327/328/329'],
        'region_budget_unchanged':65536, 'private_capture_hooks_permitted':False,
        'unchanged':['all gameplay/weapon/player/enemy source and headers','indexed draw always executes','20/21 shared Widget identity semantics','22 unmapped and ordinary indexed fallback','origin12x14 anchor0,0','all existing bank/anchor/shadow/alpha/filter routes']}
def art_contract(art, pack, baseline_pack, contract, work):
    manifest_data=(art/'candidate-manifest.json').read_bytes()
    assert sha(manifest_data)==contract['manifest_sha256'], 'Frozen candidate manifest changed'
    manifest=json.loads(manifest_data); result=[]
    assert [f['sprite_id'] for f in manifest['frames']]==TARGET_IDS
    old={p.name:sha(p.read_bytes()) for p in baseline_pack.glob('*.hda')}
    actual={p.name:sha(p.read_bytes()) for p in pack.glob('*.hda')}
    assert old==contract['baseline_pack_files'], 'Baseline pack changed'
    assert len(old)==334 and len(actual)==338
    assert set(actual)-set(old)=={f'bullet-{i}-8.hda' for i in TARGET_IDS}
    assert all(actual[name]==digest for name,digest in old.items()), 'Existing pack file changed'
    for frame in manifest['frames']:
        sprite=frame['sprite_id']; hda=(art/frame['hda']).read_bytes(); png=(art/frame['source_png']).read_bytes()
        assert sha(hda)==frame['hda_sha256']==actual[Path(frame['hda']).name]==contract['required_hda_sha256'][str(sprite)]
        assert sha(png)==frame['source_png_sha256']
        assert sha((art/frame['master']).read_bytes())==frame['master_sha256']
        assert hda[:4]==b'HDR1' and len(hda)==28+96*112*4
        header=struct.unpack('<6I', hda[4:28]); assert header==(80000+sprite,8,12,14,0,0)
        assert frame['header_u32']==list(header) and frame['anchor']==[0,0] and frame['runtime_role']=='player_projectile_only'
        with Image.open(art/frame['source_png']) as im:
            assert im.mode=='RGBA' and im.size==(96,112)
            rgba=im.tobytes()
        assert rgba==hda[28:]
        # Independently reconstruct only the approved whole-canvas transform.
        t=frame['transform']
        with Image.open(art/frame['master']) as master:
            rendered=master.convert('RGBA').crop(t['crop']).resize(tuple(t['resize']),Image.Resampling.LANCZOS)
        reproduced=Image.new('RGBA',tuple(t['canvas']));reproduced.paste(rendered,tuple(t['paste']))
        assert reproduced.tobytes()==rgba
        alpha=rgba[3::4]
        assert 0 in alpha and any(0<a<255 for a in alpha)
        (work/f'actual-{sprite}.rgba').write_bytes(rgba)
        result.append({'id':sprite, 'header':list(header), 'hda_sha256':sha(hda), 'source_png_sha256':sha(png),
                       'rgba_sha256':sha(rgba), 'zero_alpha':alpha.count(0),
                       'fractional_alpha':sum(0<a<255 for a in alpha), 'opaque_alpha':alpha.count(255)})
    return {'frames':result, 'unchanged_pack_files':len(old), 'candidate_pack_files':len(actual),
            'accepted59_hda_sha256':old['bullet-59-8.hda'], 'manifest_sha256':sha(manifest_data)}
def build_and_run(source, entity_source, directory, pack, baseline_pack, sanitize):
    directory.mkdir(parents=True, exist_ok=True)
    defs=[]
    for pattern in TYPE_PATTERNS:
        m=re.search(pattern,source,re.S);assert m,pattern;defs.append(m.group())
    (directory/'production-types.inc').write_text('\n'.join(defs))
    (directory/'production-helpers.inc').write_text('\n'.join(extract(source,n) for n in FUNCTIONS))
    (directory/'production-entity.inc').write_text(extract(entity_source,'draw_entity_sprite2'))
    cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-I'+str(directory),str(HERE/'test-guided-bomb-family.c'),'-o',str(directory/'test')]
    if sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
    compiled=subprocess.run(cmd,capture_output=True,text=True)
    if compiled.returncode:raise RuntimeError(compiled.stderr)
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    return subprocess.run([str(directory/'test'),str(pack),str(baseline_pack)],cwd=directory,env=env,capture_output=True,text=True,timeout=90)
def mutate_once(source, old, new):
    assert source.count(old)==1, old
    return source.replace(old,new)
def make_runtime_packs(pack, work):
    dest=work/'runtime-packs';dest.mkdir()
    for p in pack.glob('*.hda'):(dest/p.name).symlink_to(p)
    for missing in TARGET_IDS:
        sub=dest/f'missing-{missing}';sub.mkdir()
        for p in pack.glob('*.hda'):
            if p.name!=f'bullet-{missing}-8.hda':(sub/p.name).symlink_to(p)
    return dest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=ROOT);p.add_argument('--art',type=Path,required=True)
    p.add_argument('--assets',type=Path,required=True);p.add_argument('--baseline-assets',type=Path,required=True)
    p.add_argument('--source-closure',type=Path,help='Optional external original-data audit; never copied into the fixture or output')
    p.add_argument('--sanitize',action='store_true');p.add_argument('--mutations',action='store_true');p.add_argument('--report',type=Path)
    a=p.parse_args();contract=json.loads((HERE/'guided-bomb-family-contract.json').read_text())
    source,scope=source_scope(a.source.resolve(),contract)
    entity_source=(a.source/'src/entity_draw.c').read_text()
    work=Path(tempfile.mkdtemp(prefix='guided-bomb-family-oracle-'))
    art=art_contract(a.art.resolve(),a.assets.resolve(),a.baseline_assets.resolve(),contract,work)
    runtime_pack=make_runtime_packs(a.assets.resolve(),work)
    result=build_and_run(source,entity_source,work,runtime_pack,a.baseline_assets.resolve(),a.sanitize)
    print(result.stdout,end='');print(result.stderr,end='');result.check_returncode()
    negatives=[]
    if a.mutations:
        mutations=[
          ('capacity326','static Asset assets[330];','static Asset assets[326];'),
          ('removed-family-binding',BINDING_BLOCK,''),
          ('wrong-bank8-to12',BINDING_BLOCK,BINDING_BLOCK.replace('spriteSheet8','spriteSheet12')),
          ('wrong-layout-QUAD',BINDING_BLOCK,BINDING_BLOCK.replace('ENTITY_TILE','ENTITY_QUAD')),
          ('wrong-slot325',BINDING_BLOCK,BINDING_BLOCK.replace('slot=326+i','slot=325+i')),
          ('ID21-overbound-to22','guided_ids[4]={19,171,20,21}','guided_ids[4]={19,171,20,22}'),
          ('fragment-ID20-21-swapped','guided_ids[4]={19,171,20,21}','guided_ids[4]={19,171,21,20}'),
          ('anchor-wrong','role==8&&index==59?-1:0','role==8&&index==59?-1:index==19?1:0'),
          ('enemy-gate-expanded','(index!=112&&index!=113)','(index!=112&&index!=113&&index!=20)'),
          ('opaque-alpha','talon_blend?(src[3]+1)/2:src[3]','talon_blend?(src[3]+1)/2:255'),
          ('wrong-shadow-alpha','darken_rgba(*p,src[3])','darken_rgba(*p,255)'),
          ('green-head-scope-expanded','a->index>=214&&a->index<=217&&style==MIRROR_NORMAL','a->index>=19&&a->index<=217&&style==MIRROR_NORMAL'),
          ('family-shadow-bypassed','if(bank.data==spriteSheet8.data&&index>=214&&index<=217&&style==MIRROR_SHADOW)return false;','if(bank.data==spriteSheet8.data&&(index==19||(index>=214&&index<=217))&&style==MIRROR_SHADOW)return false;'),
          ('missing-ID19-disables-descendants','if(!a->valid&&game_probe_density==8) a->valid=read_asset(a,4);','if(!a->valid&&game_probe_density==8) a->valid=read_asset(a,4);\n  if(index==19&&!a->valid)game_probe_missing=true;'),
          ('unmapped22-poisons-frame','if(slot<0||game_probe_density==1','if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index==22){render_mirror_unsupported("wrong-22-disable");return NULL;}\n if(slot<0||game_probe_density==1'),
        ]
        for label,old,new in mutations:
            candidate=mutate_once(source,old,new);directory=work/label;directory.mkdir()
            for f in work.glob('actual-*.rgba'):shutil.copy2(f,directory/f.name)
            r=build_and_run(candidate,entity_source,directory,runtime_pack,a.baseline_assets.resolve(),False)
            assert r.returncode!=0, 'MUTATION ESCAPED: '+label
            assert 'FAIL line ' in r.stderr, (label,r.returncode,r.stderr)
            negatives.append({'name':label,'exit_code':r.returncode,'diagnostic':r.stderr.strip()[:800]})
            print('KILLED:',label)
        label='HD-skips-indexed-original';directory=work/label;directory.mkdir()
        for f in work.glob('actual-*.rgba'):shutil.copy2(f,directory/f.name)
        bad_entity=entity_source.replace('if (layout == ENTITY_QUAD)','if(mirrored){render_mirror_entity_end();return;}\n\tif (layout == ENTITY_QUAD)')
        r=build_and_run(source,bad_entity,directory,runtime_pack,a.baseline_assets.resolve(),False)
        assert r.returncode and 'FAIL line ' in r.stderr
        negatives.append({'name':label,'exit_code':r.returncode,'diagnostic':r.stderr.strip()[:800]});print('KILLED:',label)
    from guided_bomb_source_oracle import source_equations
    equations=source_equations(a.source.resolve(),contract,a.source_closure,a.mutations)
    report={'status':'passed','sanitize':a.sanitize,'baseline_commit':contract['baseline_commit'],
            'source_scope':scope,'art_contract':art,'source_equations':equations,'extracted_production_functions':FUNCTIONS+['draw_entity_sprite2'],
            'oracle_result':result.stdout.strip(),'negative_controls':negatives,'retained_test_work':str(work),
            'limitations':['No game run or capture. These checks do not establish in-game visibility or visual acceptance.',
                           'Original indexed drawing is byte-unchanged and its real entity boundary is exercised with recorder blits; this unit harness does not decode original game art.',
                           'Optional source-closure audit is read-only external evidence; no original data, decoded raw records or captures are embedded in this portable suite.',
                           'ASan leak detection is disabled for executor ptrace; address and undefined-behavior checks remain enabled.']}
    out=a.report or work/'result.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
    print('Report:',out)
if __name__=='__main__':main()
