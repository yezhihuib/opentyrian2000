"""ASan/UBSan pixel oracle for the unchanged real production terrain compositor."""
from pathlib import Path
import argparse, re, subprocess, tempfile, os, json, hashlib
TOOLS=Path(__file__).resolve().parent;ROOT=TOOLS.parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=ROOT);p.add_argument('--assets',type=Path,default=ROOT/'assets/hd/packs/packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test');p.add_argument('--report',type=Path);a=p.parse_args()
source=(a.source/'src/render_mirror.c').read_text()
def extract(name):
    m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^\n;]*\)\s*\{',source,re.M);assert m,name
    start=source.index('{',m.start());end=start+1;depth=1
    while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[m.start():end]+'\n'
asset=re.search(r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',source,re.S).group()
functions=['blend_rgba','cloud_asset','darken_rgba','draw_asset_filtered','draw_asset']

def prepare_assets(directory, assets):
    import struct
    expected = {111: ('ae597697acd4d720cf61b30d6e4d57e7c56e20355b9069a3abe8ba37736741d5', 5632, 5090), 114: ('2e5c9bd9bccf9146f60ec196571ee3677cc77b7f035ef1abe99ac65de03a8707', 576, 0), 113: ('241aabc9a7eeb983d4f96fa3a1680c08d3ba8746402bfeb2fbd87151d588c673', 448, 0), 341: ('b2f7b9bc8a076a5fa8450beeb92714981f13b321d057610fdf771e115f93e6a8', 0, 0), 342: ('cb3ca68e74d54c60541ff5ae2de864cfb813a2cd555885690e3730ac24a38f46', 0, 0), 343: ('d78d2c9c16db424d2e2c80071e1bd0d666bc5f98547b995a4d356137b09a2210', 0, 0), 351: ('8a148c7aebc32665ff1b6d8aa2839a777b2e82014e3f14e0eb70ff8e5155965d', 0, 0), 352: ('7c6c7ce14e5c0f455a6c987e67db32d6fd4d7502c20bf72bb3fd47d8cf14bcac', 0, 0), 353: ('441df0f51129c8a1d8287aa5f336c4bb185f12c139bfcc6c35056141deb1248c', 0, 0)}
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
    (directory/'original-masks.inc').write_text('/* Support derived from approved authored assets, not bundled game data. */\nstatic const Uint8 original_masks[9][672]={'+','.join('{'+','.join(map(str,m))+'}' for m in masks)+'};\n')
    return reports

with tempfile.TemporaryDirectory(prefix='terrain-next-seven-alpha-') as d:
    tmp=Path(d);(tmp/'production-asset.inc').write_text(asset+'\n');(tmp/'production-alpha.inc').write_text('\n'.join(extract(n) for n in functions))
    asset_report=prepare_assets(tmp,a.assets)
    cmd=['cc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(tmp),str(Path(__file__).with_suffix('.c')),'-o',str(tmp/'test')]
    subprocess.run(cmd,check=True)
    result=subprocess.run([str(tmp/'test')],cwd=tmp,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'),capture_output=True,text=True)
    print(result.stdout);print(result.stderr,end='');result.check_returncode()
    report={'status':'passed','sanitize':'address,undefined','source_renderer_sha256':hashlib.sha256(source.encode()).hexdigest(),'actual_extracted_production_functions':functions,'assets':asset_report,'result':result.stdout,'stderr':result.stderr,'scope':'Unchanged actual compositor including new113 and six opaque stone foundations; normal/shadow,2x/4x/8x, approved authored support, synthetic binary/fractional alpha, and actual selected fractional RGBA, normal/clipped placement, underlying RGBA/ownership preservation through all original111/114/113 holes and opaque stone foundations. Other effect branches deliberately stubbed and cannot execute in this oracle.','no_game_runtime':True}
    out=a.report or Path(tempfile.mkdtemp(prefix='terrain-holes-alpha-report-'))/'result.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
