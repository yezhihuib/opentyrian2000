#!/usr/bin/env python3
"""Stage/apply a finite shapesy_platform art bundle. Not a production-binding refresh.

Apply rederives every byte and preflights the complete plan before any writes;
handled write errors roll back. Process/power loss is not transactional.
"""
import argparse
from pathlib import Path
import current_shapesy_platform_compatibility as c
from build_current_art import encoded, fingerprint
from build_current_craft267 import external, replace_batch, SUFFIX
from current_craft267_compatibility import path


def derive(root,raw):
    selected,pngs,blobs,rows=c.generate(root,raw)
    catalog=c.json.loads(c.read(root,'assets/hd/manifest.json'))
    if (catalog['default_preview_pack'],catalog['default_debug_pack'])!=c.PACKS:
        raise ValueError('Unexpected Y destination packs')
    transports={}
    for pack in c.PACKS:
        files=catalog['packs'][pack]['files']
        for row in rows:
            i=row['base']; files[c.name(i)]=dict(sha256=row['sha256'],
                header_u32=[c.ROLE*10000+i,8,24,28,0,0],source_png=c.png(i),
                source_png_sha256=row['source_png_sha256'])
            transports['assets/hd/packs/'+pack+'/'+c.name(i)]=blobs[i]
        catalog['packs'][pack]['count']=len(files)
    return {c.SELECTION:encoded(selected),**pngs,**transports,
            c.HEADER:c.payload_header(rows),'assets/hd/manifest.json':encoded(catalog),
            c.MAPPING:encoded(dict(schema='opentyrian-shapesy-platform-compatibility-v1',selection=c.SELECTION,files=rows))}


def plan(root,raw,outputs):
    inputs=c.input_paths(root)|{'assets/hd/manifest.json','scripts/current_shapesy_platform_compatibility.py','scripts/build_current_shapesy_platform.py','scripts/current_guided_compatibility.py','scripts/build_newshf_hd.py','scripts/build_current_art.py','scripts/build_current_craft267.py','scripts/current_craft267_compatibility.py'}
    return dict(schema='opentyrian-shapesy-platform-stage-v1',request_sha256=c.sha(raw),inputs_sha256={p:fingerprint(root,p) for p in sorted(inputs)},files=[dict(path=p,before_sha256=fingerprint(root,p),after_sha256=c.sha(b),bytes=len(b)) for p,b in sorted(outputs.items())])

def stage(root,selected,destination):
    external(root,destination)
    if destination.exists(): raise ValueError('Stage destination must be new')
    raw=c.read(selected.absolute().parent,selected.name); outputs=derive(root,raw); receipt=plan(root,raw,outputs)
    destination.mkdir(parents=True)
    for p,b in outputs.items():
        target=destination/'files'/p; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(b)
    (destination/'request.json').write_bytes(raw); (destination/'plan.json').write_bytes(encoded(receipt))
    return receipt

def apply(root,destination):
    external(root,destination)
    raw=c.read(destination,'request.json'); outputs=derive(root,raw); receipt=plan(root,raw,outputs)
    if c.parse(c.read(destination,'plan.json'))!=receipt: raise ValueError('Stale or modified shapesy_platform plan; restage')
    for p,b in outputs.items():
        if c.read(destination,'files/'+p)!=b: raise ValueError('Modified staged shapesy_platform bytes')
        target=path(root,p); temporary=path(root,p+SUFFIX)
        if temporary.exists() or temporary.is_symlink(): raise ValueError('Unexpected temporary output')
        if target.exists() and not target.is_file(): raise ValueError('Nonregular output')
    replace_batch(root,outputs)
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--root',type=Path,required=True)
    sub=parser.add_subparsers(dest='action',required=True)
    s=sub.add_parser('stage'); s.add_argument('--selection',type=Path,required=True); s.add_argument('--destination',type=Path,required=True)
    a=sub.add_parser('apply'); a.add_argument('--destination',type=Path,required=True)
    args=parser.parse_args(); root=args.root.resolve(); destination=args.destination.resolve()
    result=stage(root,args.selection,destination) if args.action=='stage' else apply(root,destination)
    print(encoded(result).decode(),end='')
