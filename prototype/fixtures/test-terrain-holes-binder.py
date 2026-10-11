"""Extract the production finite binder and loader and test their actual C99 code."""
from pathlib import Path
import argparse,re,subprocess,tempfile,os,json,hashlib
TOOLS=Path(__file__).resolve().parent;ROOT=TOOLS.parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=ROOT);p.add_argument('--sanitize',action='store_true');p.add_argument('--report',type=Path);p.add_argument('--assets',type=Path,default=ROOT/'assets/hd/packs/packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test');a=p.parse_args();source=(a.source/'src/render_mirror.c').read_text()
def extract(name):
 match=re.search(r'^.*\b'+name+r'\([^\n]*\)\s*\{',source,re.M);assert match,name
 start=source.index('{',match.start());depth=1;end=start+1
 while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[match.start():end]+'\n'
types=re.search(r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',source,re.S).group()
arrays='\n'.join(re.search(p,source).group() for p in [r'static Asset assets\[\d+\];',r'static struct \{const Uint8 \*data;unsigned int id;\} terrain_sources\[\d+\];'])
funcs='\n'.join(extract(n) for n in ['read_asset','scene_asset','render_mirror_map_begin','cloud_terrain_slot','ground_terrain_slot','plateau_terrain_slot','underlay_terrain_slot','road_terrain_slot','terrain_holes_slot','stone_foundation_slot','layer3_gray_slot','render_mirror_bind_terrain','render_mirror_terrain_row'])

def prepare_assets(directory, assets):
    import struct
    expected = {111: ('ae597697acd4d720cf61b30d6e4d57e7c56e20355b9069a3abe8ba37736741d5', 5632, 5090),
                114: ('2e5c9bd9bccf9146f60ec196571ee3677cc77b7f035ef1abe99ac65de03a8707', 576, 0)}
    masks=[]; reports=[]
    for tile, (digest, zeros, fractional) in expected.items():
        path=assets/f'terrain-shapesz-{tile}-8.hda'; data=path.read_bytes()
        assert len(data)==172060 and data[:4]==b'HDR1'
        assert struct.unpack('<6I',data[4:28])==(2010000+tile,8,24,28,0,0)
        assert hashlib.sha256(data).hexdigest()==digest, str(path)
        rgba=data[28:]; alpha=rgba[3::4]
        assert alpha.count(0)==zeros and sum(0<x<255 for x in alpha)==fractional
        mask=[]
        for y in range(28):
            for x in range(24):
                support={alpha[(y*8+dy)*192+x*8+dx]>0 for dy in range(8) for dx in range(8)}
                assert len(support)==1
                mask.append(255 if support.pop() else 0)
        assert all(alpha[y*192+x]==255 for y in range(224) for x in range(192) if x in (0,191) or y in (0,223))
        masks.append(bytes(mask)); (directory/f'actual-{tile}.rgba').write_bytes(rgba)
        (directory/f'actual-{tile}.hda').write_bytes(data)
        reports.append({'id':tile,'hda_sha256':digest,'zero_alpha_texels':zeros,'fractional_alpha_texels':fractional})
    (directory/'original-masks.inc').write_text('/* Support derived from approved authored assets, not bundled game data. */\nstatic const Uint8 original_masks[2][672]={'+','.join('{'+','.join(map(str,m))+'}' for m in masks)+'};\n')
    return reports

with tempfile.TemporaryDirectory(prefix='terrain-holes-binder-') as tmp:
 d=Path(tmp);(d/'production-types.inc').write_text(types+'\n'+arrays+'\n');(d/'production-helpers.inc').write_text(funcs)
 asset_report=prepare_assets(d,a.assets)
 command=['cc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-I'+str(d),str(Path(__file__).with_suffix('.c')),'-o',str(d/'test')]
 if a.sanitize:command+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 subprocess.run(command,check=True);env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
 result=subprocess.run([str(d/'test')],cwd=d,env=env,text=True,capture_output=True);print(result.stdout);print(result.stderr,end='');result.check_returncode()
 report={'status':'passed','sanitize':a.sanitize,'source':str(a.source.resolve()),'renderer_sha256':hashlib.sha256(source.encode()).hexdigest(),'command':command,'assets':asset_report,'result':result.stdout,'stderr':result.stderr,'leak_sanitizer':'Disabled because runtime uses ptrace; ASan address checks and UBSan remain enabled.'}
 out=a.report or Path(tempfile.mkdtemp(prefix='terrain-holes-binder-report-'))/'result.json';out.write_text(json.dumps(report,indent=2)+'\n')
