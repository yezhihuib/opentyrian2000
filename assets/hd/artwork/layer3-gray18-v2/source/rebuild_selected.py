#!/usr/bin/env python3
"""Rebuild gray18 v1 generated sources, then apply only four frozen authored fringe crops."""
from pathlib import Path
from PIL import Image, __version__ as pillow_version
import argparse, hashlib, json, platform, runpy, shutil, struct, subprocess, sys
IDS=[121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154]
OVERRIDES=[134,141,142,143]
def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)
def snapshot(root):return {p.relative_to(root).as_posix():sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file()}
def read_rgba(p):
    with Image.open(p) as im:
        require(im.size==(192,224),'Invalid image dimensions: '+str(p));return im.convert('RGBA').tobytes()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-root',required=True,type=Path);args=parser.parse_args()
    package=Path(__file__).resolve().parent.parent;source=package/'source';output=args.output_root.resolve()
    require(not output.exists(),'Output root must not already exist')
    require(output!=package and package not in output.parents,'Output root must be outside immutable source package')
    require(not any(p.is_symlink() for p in package.rglob('*')),'Package cannot contain symlinks')
    before=snapshot(package);c=json.loads((source/'rebuild-contract.json').read_text())
    require(c['ids']==IDS and c['override_ids']==OVERRIDES,'Finite ID oracle mismatch')
    require([r['id'] for r in c['items']]==IDS and [r['slot'] for r in c['items']]==list(range(272,290)),'Finite slot oracle mismatch')
    for path,key in [('baseline-v1-contract.json','baseline_contract_sha256'),('baseline-v1-manifest.json','baseline_manifest_sha256'),('frozen-four-rim-manifest.json','frozen_four_manifest_sha256'),('feather_occupied_alpha.cpp','native_helper_sha256'),('compose_rim_fringe.cpp','native_fringe_helper_sha256')]:
        require(sha((source/path).read_bytes())==c[key],'Frozen input hash mismatch: '+path)
    require(sha((package/'runtime-overlay/manifest.json').read_bytes())==c['selected_manifest_sha256'],'Selected manifest mismatch')
    b=json.loads((source/'baseline-v1-contract.json').read_text());fm=json.loads((source/'frozen-four-rim-manifest.json').read_text())
    require(b['ids']==IDS and sorted(map(int,fm))==OVERRIDES,'Upstream source scope mismatch')
    expected_png={f'terrain-shapesz-{i}-8.png' for i in IDS};expected_fringe={f'terrain-shapesz-{i}-8.png' for i in OVERRIDES}
    require({p.name for p in (source/'generated-crops').iterdir()}==expected_png,'Source crop scope mismatch')
    require({p.name for p in (source/'generated-fringe-crops').iterdir()}==expected_fringe,'Fringe crop scope mismatch')
    require({p.name for p in (package/'output').iterdir()}==expected_png,'Committed PNG scope mismatch')
    require({p.name for p in (package/'runtime-overlay').iterdir()}=={'manifest.json'}|{f'terrain-shapesz-{i}-8.hda' for i in IDS},'Committed HDA scope mismatch')
    inventory_verified=False
    inventory_path=package/'handoff-inventory.json'
    if inventory_path.exists():
        inv=json.loads(inventory_path.read_text());require({r['path'] for r in inv['files']}==set(before)-{'handoff-inventory.json'},'Inventory file scope mismatch')
        for r in inv['files']:
            p=package/r['path'];require(p.stat().st_size==r['bytes'] and sha(p.read_bytes())==r['sha256'],'Inventory hash or size mismatch: '+r['path'])
        inventory_verified=True
    for name in ['work','output','runtime-overlay']:(output/name).mkdir(parents=True)
    compiler=shutil.which('c++');require(compiler is not None,'A C++17 compiler (c++) is required')
    compiler_version=subprocess.run([compiler,'--version'],check=True,text=True,capture_output=True).stdout.splitlines()[0]
    for name in ['feather_occupied_alpha','compose_rim_fringe']:
        subprocess.run([compiler,'-O2','-std=c++17',str(source/(name+'.cpp')),'-o',str(output/'work'/name)],check=True)
    logs=[];results=[];fringes={r['id']:r for r in c['fringe_crops']}
    for row,base in zip(c['items'],b['items']):
        i=row['id'];stem=f'terrain-shapesz-{i}-8';src=source/'generated-crops'/(stem+'.png')
        require(sha(src.read_bytes())==row['source_png_sha256']==base['source_png_sha256'],'Source PNG changed')
        raw=read_rgba(src);alpha=raw[3::4]
        require(sha(raw)==row['source_rgba_sha256']==base['source_rgba_sha256'],'Source RGBA changed')
        require(sha(alpha)==row['source_alpha_sha256'] and set(alpha)<={0,255},'Source alpha changed')
        require(all(raw[p:p+4]==bytes(4) for p in range(0,len(raw),4) if raw[p+3]==0),'Source hidden RGB not zero')
        for y in range(0,224,8):
            for x in range(0,192,8):
                require(all(alpha[(y+dy)*192+x+dx]==alpha[y*192+x] for dy in range(8) for dx in range(8)),'Source logical support not 8x replicated')
        input_path=output/f'work/{i}-binary.rgba';base_path=output/f'work/{i}-baseline.rgba';input_path.write_bytes(raw)
        if 0 in alpha:
            run=subprocess.run([str(output/'work/feather_occupied_alpha'),str(input_path),str(base_path)],check=True,text=True,capture_output=True)
            logs.append({'id':i,'stage':'baseline alpha','stdout':run.stdout.strip()})
            baseline=base_path.read_bytes()
        else:baseline=raw;base_path.write_bytes(baseline)
        require(sha(baseline)==base['selected_rgba_sha256'],'Baseline reconstruction differs from v1')
        require(all(raw[p:p+3]==baseline[p:p+3] for p in range(0,len(raw),4)),'Baseline helper changed RGB')
        require(all((a>0)==(z>0) for a,z in zip(alpha,baseline[3::4])),'Baseline support changed')
        if i in OVERRIDES:
            crop=source/'generated-fringe-crops'/(stem+'.png');f=fringes[i]
            require(sha(crop.read_bytes())==f['png_sha256'],'Fringe source PNG changed')
            authored=read_rgba(crop);require(sha(authored)==f['rgba_sha256'],'Fringe source RGBA changed')
            gp=output/f'work/{i}-fringe.rgba';gp.write_bytes(authored);out=output/f'work/{i}-selected.rgba'
            run=subprocess.run([str(output/'work/compose_rim_fringe'),str(base_path),str(gp),str(out)],check=True,text=True,capture_output=True)
            logs.append({'id':i,'stage':'fringe composition','stdout':run.stdout.strip(),'stderr':run.stderr.strip()})
            regenerated=out.read_bytes()
            require(row['selected_png_sha256']==fm[str(i)]['png_sha256'] and row['selected_rgba_sha256']==fm[str(i)]['rgba_sha256'] and row['selected_hda_sha256']==fm[str(i)]['hda_sha256'],'Frozen four override differs')
        else:
            regenerated=baseline
            for key in ['selected_png_sha256','selected_rgba_sha256','selected_hda_sha256']:require(row[key]==base[key],'Preserved14 hash changed')
        committed_png=package/'output'/(stem+'.png');committed_hda=package/'runtime-overlay'/(stem+'.hda')
        require(sha(committed_png.read_bytes())==row['selected_png_sha256'],'Committed selected PNG hash mismatch')
        require(read_rgba(committed_png)==regenerated and sha(regenerated)==row['selected_rgba_sha256'],'Rebuilt decoded RGBA mismatch')
        require(all((a>0)==(z>0) for a,z in zip(alpha,regenerated[3::4])),'Selected source support mismatch')
        require(regenerated[3::4].count(0)==row['zero_alpha_hd_pixels'] and sum(0<a<255 for a in regenerated[3::4])==row['partial_alpha_hd_pixels'],'Selected alpha counts mismatch')
        png=output/'output'/(stem+'.png');hda=output/'runtime-overlay'/(stem+'.hda')
        if i in c['fullyopaque_ids']:
            shutil.copyfile(src,png);require(png.read_bytes()==committed_png.read_bytes(),'Opaque PNG file identity changed')
        else:Image.frombytes('RGBA',(192,224),regenerated).save(png)
        payload=b'HDR1'+struct.pack('<6I',2010000+i,8,24,28,0,0)+regenerated;hda.write_bytes(payload)
        require(len(payload)==172060 and payload==committed_hda.read_bytes() and sha(payload)==row['selected_hda_sha256'],'Selected HDA mismatch')
        results.append({'id':i,'slot':row['slot'],'source_png_and_rgba_hashes_verified':True,'baseline_v1_rgba_exact':True,'committed_selected_png_hash_verified':True,'regenerated_png_sha256':sha(png.read_bytes()),'selected_png_sha256':row['selected_png_sha256'],'regenerated_png_file_exact':png.read_bytes()==committed_png.read_bytes(),'rgba_sha256':sha(regenerated),'rgba_exact':True,'hda_sha256':sha(payload),'hda_exact':True,'rim_v2_override':i in OVERRIDES,'partial_alpha_hd_pixels':row['partial_alpha_hd_pixels']})
    shutil.copyfile(package/'runtime-overlay/manifest.json',output/'runtime-overlay/manifest.json')
    verify=runpy.run_path(str(source/'verify_scope.py'))['verify'];scope=verify(package,output)
    (output/'scope-verification.json').write_text(json.dumps(scope,indent=2)+'\n')
    require(snapshot(package)==before,'Source package mutated during rebuild')
    report={'status':'PASS','tiles':18,'override_ids':OVERRIDES,'preserved14_exact':True,'baseline_v1_reconstructed_exact_count':18,'decoded_rgba_exact_count':18,'hda_file_exact_count':18,'committed_selected_png_hashes_verified_count':18,'regenerated_png_file_exact_count':sum(r['regenerated_png_file_exact'] for r in results),'fringe_source_crops_verified_count':4,'native_helpers_built_fresh':True,'source_package_unchanged':True,'package_inventory_verified':inventory_verified,'scope_oracle_passed':True,'frozen144_exact':True,'runtime_approval':'Bounded actual visual accepted separately; formal engineering integration gate remains engineer-owned','environment':{'python':platform.python_version(),'pillow':pillow_version,'compiler':compiler_version,'platform':platform.platform()},'items':results,'native_helper_log':logs}
    (output/'rebuild-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('items','native_helper_log')},indent=2))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as e:
        print('Rebuild failed: '+str(e),file=sys.stderr);sys.exit(1)
