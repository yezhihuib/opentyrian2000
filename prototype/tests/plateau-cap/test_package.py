#!/usr/bin/env python3
"""Read-only reproduction and fail-closed wrapper checks; never edit inputs."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
from unittest.mock import patch
here=Path(__file__).resolve();sys.path.insert(0,str(here.parents[2]))
from plateau_cap_bundle import build_bundle,render_header,INVENTORY_SHA256
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--selected-pack',type=Path,required=True);p.add_argument('--second-pack',type=Path);p.add_argument('--src',type=Path,required=True);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=a.output.resolve();root.mkdir(parents=True,exist_ok=False);package=a.package.resolve();selected=a.selected_pack.resolve();raw_read=Path.read_bytes
blob,records,receipt=build_bundle(package,selected)
assert raw_read(a.bundle)==blob and (a.src/'plateau_cap_bundle_index.h').read_text()==render_header(records,receipt)
checks={'exact_bundle_header':True}
if a.second_pack:
    other,other_records,other_receipt=build_bundle(package,a.second_pack)
    assert (other,other_records,other_receipt)==(blob,records,receipt);checks['both_selected_packs_exact']=True
bindings=json.loads((package/'contracts/cap-bindings.json').read_text())
def reject_mutation(name,path,change):
    path=path.resolve()
    def read(p):
        data=raw_read(p)
        return change(data) if p.resolve()==path else data
    with patch.object(Path,'read_bytes',read):
        try:build_bundle(package,selected)
        except (ValueError,FileNotFoundError):checks[name]=True
        else:raise AssertionError(name+' not rejected')
reject_mutation('modified-inventory',package/'inventory.json',lambda b:b+b' ')
reject_mutation('modified-bindings',package/'contracts/cap-bindings.json',lambda b:b+b' ')
reject_mutation('modified-atlas',package/'selected/atlas.png',lambda b:b[:-1]+bytes([b[-1]^1]))
reject_mutation('modified-mask108',package/'selected/cap-weights/terrain-shapesz-108-8.png',lambda b:b+b'\0')
for row in bindings['rows']:
    reject_mutation('selected-hda-'+str(row['id']),selected/f'terrain-shapesz-{row["id"]}-8.hda',lambda b:b[:28]+bytes([b[28]^1])+b[29:])
for suffix in ('0','1'):
    reject_mutation('lower-payload-'+suffix,selected/('ground101-world-material.g101.'+suffix),lambda b:b[:-1]+bytes([b[-1]^1]))
wrapper=here.parents[2]/'build-plateau-cap-world-material.py'
for name,contents in [('missing-inventory',None),('modified-inventory',b'{}')]:
    bad=root/name;bad.mkdir()
    if contents is not None:(bad/'inventory.json').write_bytes(contents)
    dest=root/(name+'-output')
    run=subprocess.run([sys.executable,str(wrapper),'--package',str(bad),'--selected-pack',str(selected),'--output',str(dest),'--rebuild-art'],capture_output=True,text=True)
    assert run.returncode!=0 and not dest.exists();checks[name+'-before-rebuilder']=True
# Protected destination checks occur before mkdir/rebuilder execution.
for name,dest in [('inside-package',package/'forbidden-cap-test-output'),('inside-selected',selected/'forbidden-cap-test-output'),('inside-repo',a.src.parent/'forbidden-cap-test-output'),('existing-output',root)]:
    assert name=='existing-output' or not dest.exists()
    run=subprocess.run([sys.executable,str(wrapper),'--package',str(package),'--selected-pack',str(selected),'--output',str(dest)],capture_output=True,text=True)
    assert run.returncode!=0 and (name=='existing-output' or not dest.exists());checks[name]=True
assert hashlib.sha256(raw_read(package/'inventory.json')).hexdigest()==INVENTORY_SHA256
(root/'package-checks.json').write_text(json.dumps({'status':'passed','checks':checks,'bundle_sha256':receipt['sha256'],'source_package_unchanged':True},indent=2)+'\n')
print('PASS',len(checks),'package/reproduction/fail-closed wrapper checks; immutable inputs unchanged')
