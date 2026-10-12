#!/usr/bin/env python3
"""Rebuild the finite additive cap atlas and semantic masks into a NEW directory."""
from pathlib import Path
import argparse, hashlib, json, subprocess, struct
from PIL import Image, ImageDraw
import numpy as np
from scipy.ndimage import distance_transform_edt

P = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()

def run(*args):
    subprocess.run([str(a) for a in args], check=True)

def rgba(path):
    return Image.open(path).convert('RGBA')

def validate_record(record):
    p = P / record['path']
    assert sha(p.read_bytes()) == record['file_sha256'], f'file hash: {p}'
    im = Image.open(p).convert(record['decoded_mode'])
    assert list(im.size) == record['size'], f'size: {p}'
    assert sha(im.tobytes()) == record['decoded_sha256'], f'pixels: {p}'
    return np.array(im)

def checked_output(value):
    raw = Path(value).absolute()
    # Reject existing output and all symlink components before resolving paths.
    if raw.exists() or raw.is_symlink():
        raise SystemExit('Output must be a new, non-symlink directory.')
    for parent in raw.parents:
        if parent.is_symlink():
            raise SystemExit('Symlink output parents are not permitted.')
    dest = raw.resolve()
    if dest == P or P in dest.parents or dest in P.parents:
        raise SystemExit('Output must be outside the immutable source package.')
    # A workspace may itself be backed by an outer .git; never write inside a
    # closer repository/worktree (the production checkout, for example).
    if any((p / 'assets/hd/manifest.json').exists() for p in dest.parents):
        raise SystemExit('Output inside the game checkout is not permitted.')
    outer_roots = {p for p in P.parents if (p / '.git').exists()}
    for parent in dest.parents:
        if (parent / '.git').exists() and parent not in outer_roots:
            raise SystemExit('Output inside a different repository is not permitted.')
    if not dest.parent.is_dir():
        raise SystemExit('Output parent must already exist.')
    dest.mkdir()
    return dest

def calibrate(src, dest, factors):
    args = ['convert', str(src)]
    for channel, factor in zip('RGB', factors):
        args += ['-channel', channel, '-fx', f'floor(u*{factor:.17g}*255+0.5)/255']
    args += ['+channel', '-depth', '8', 'PNG32:' + str(dest)]
    run(*args)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    # Read-only validation is performed before any destination is created.
    inventory = P / 'inventory.json'
    if inventory.exists():
        entries = json.loads(inventory.read_text())['files']
        actual = {str(p.relative_to(P)) for p in P.rglob('*') if p.is_file() or p.is_symlink()}
        assert actual == set(entries) | {'inventory.json'}, 'Package inventory mismatch'
        for rel, digest in entries.items():
            assert not (P / rel).is_symlink(), f'package symlink: {rel}'
            assert sha((P / rel).read_bytes()) == digest, f'package file: {rel}'
    bindings = json.loads((P / 'contracts/cap-bindings.json').read_text())
    spec = json.loads((P / 'contracts/cap-domain-polygons.json').read_text())
    reg = json.loads((P / 'contracts/registration.json').read_text())
    for row in bindings['rows']:
        base = validate_record(row['base'])
        mask = validate_record(row['cap_weight'])
        assert base.shape == (224,192,4) and mask.shape == (224,192)
        assert sha(bytes.fromhex(row['header_hex']) + base.tobytes()) == row['source_hda_sha256']
        assert sha(base[:,:,3].tobytes()) == row['original_alpha_sha256']
        assert np.all(base[:,:,3] == 255)
        for guard in row['lower_guard_inputs']:
            lower = validate_record(guard)
            assert not np.any(mask[lower > 0]), f'lower overlap {row["id"]}'
        if row['id'] in (119,120):
            assert not np.any(mask[184:]), 'footer lower40 rows must be protected'
        assert bool(mask.any()) == row['enabled']
    out = checked_output(args.out)
    intermediates = out / 'registration'; intermediates.mkdir()
    files = {k: intermediates / (k + '.png') for k in
             ['clean_registered','clean_calibrated','offset','wrap_registered','wrap_calibrated']}
    run('convert', P/'source/generated-cleaned-cap-master.png', '-resize','768x896!', '-depth','8', 'PNG32:'+str(files['clean_registered']))
    calibrate(files['clean_registered'], files['clean_calibrated'], reg['clean_calibration'])
    run('convert', files['clean_calibrated'], '-roll','+384+448', 'PNG32:'+str(files['offset']))
    # Keep ImageMagick's resize precision before the exact recorded calibration.
    run('convert', P/'source/generated-wrap-repair.png', '-resize','768x896!', 'PNG32:'+str(files['wrap_registered']))
    calibrate(files['wrap_registered'], files['wrap_calibrated'], reg['wrap_calibration'])
    for key, path in files.items():
        assert sha(rgba(path).tobytes()) == reg[key]['rgba_sha256'], f'registration: {key}'
    run('g++','-O2','-std=c++17', P/'source/compose_wrap.cpp','-o',intermediates/'compose_wrap')
    for key in ['offset','wrap_calibrated']:
        run('convert', files[key], '-depth','8', 'RGBA:'+str(intermediates/(key+'.rgba')))
    run(intermediates/'compose_wrap', intermediates/'offset.rgba', intermediates/'wrap_calibrated.rgba', intermediates/'atlas.rgba', intermediates/'seam-weight.gray')
    run('convert','-size','768x896','-depth','8','RGBA:'+str(intermediates/'atlas.rgba'),'PNG32:'+str(out/'atlas.png'))
    atlas = rgba(out/'atlas.png')
    assert atlas.size == (768,896)
    assert sha(atlas.tobytes()) == reg['atlas']['rgba_sha256']
    assert atlas.tobytes() == rgba(P/'selected/atlas.png').tobytes()
    assert np.all(np.array(atlas)[:,:,3] == 255)
    weights = out/'cap-weights'; weights.mkdir()
    W,H,PAD=192,224,256
    mask_results=[]
    for row in bindings['rows']:
        ident=row['id']; polygon=spec['polygons'][str(ident)]
        if polygon == 'full':
            weight=np.full((H,W),255,np.uint8)
        elif not polygon:
            weight=np.zeros((H,W),np.uint8)
        else:
            canvas=Image.new('1',(W+2*PAD,H+2*PAD))
            ImageDraw.Draw(canvas).polygon([(x+PAD,y+PAD) for x,y in polygon],fill=1)
            # Additional geometric exclusions, when present, are semantic rock
            # bodies, never old indexed pixel masks or color thresholds.
            for exclusion in spec.get('excluded_polygons',{}).get(str(ident),[]):
                ImageDraw.Draw(canvas).polygon([(x+PAD,y+PAD) for x,y in exclusion],fill=0)
            distance=distance_transform_edt(np.array(canvas))[PAD:PAD+H,PAD:PAD+W]
            width=spec.get('feather_hd_pixels',{}).get(str(ident),8 if ident in (108,119,120) else 16)
            t=np.clip(distance/width,0,1)
            weight=np.rint((t*t*(3-2*t))*255).astype(np.uint8)
        profile = spec.get('profile_boundaries',{}).get(str(ident))
        if profile:
            points=np.array(profile['points'])
            boundary=np.interp(np.arange(H),points[:,1],points[:,0])
            xx=np.arange(W)[None,:]
            width=np.minimum(profile['maximum_inward_feather_hd'],profile['full_connector_start_x']+1-boundary[:,None])
            t=np.clip((xx-boundary[:,None]+1)/width,0,1)
            restricted=np.rint(t*t*(3-2*t)*255).astype(np.uint8)
            restricted[xx<boundary[:,None]]=0
            weight=np.minimum(weight,restricted)
        ceiling=spec.get('weight_ceiling',{}).get(str(ident))
        if ceiling:
            canvas=Image.new('1',(W+2*PAD,H+2*PAD))
            ImageDraw.Draw(canvas).polygon([(x+PAD,y+PAD) for x,y in ceiling['polygon']],fill=1)
            distance=distance_transform_edt(np.array(canvas))[PAD:PAD+H,PAD:PAD+W]
            t=np.clip(distance/ceiling['feather_hd_pixels'],0,1)
            weight=np.minimum(weight,np.rint(t*t*(3-2*t)*255).astype(np.uint8))
        for guard in row['lower_guard_inputs']:
            lower=np.array(Image.open(P/guard['path']).convert('L'))
            weight[lower>0]=0
        if ident in (119,120): weight[184:]=0
        assert sha(weight.tobytes()) == row['cap_weight']['decoded_sha256'], f'mask {ident}'
        destination=weights/f'terrain-shapesz-{ident}-8.png'
        Image.fromarray(weight).save(destination)
        mask_results.append({'id':ident,'decoded_sha256':sha(weight.tobytes()),'nonzero_pixels':int((weight>0).sum())})
    receipt={'status':'passed','atlas_rgba_sha256':sha(atlas.tobytes()),'atlas_size':list(atlas.size),
             'masks':mask_results,'enabled_ids':bindings['enabled_ids'],'guard_only_ids':bindings['guard_only_ids'],
             'source_bases_unchanged':True,'lower_footer_overlap_pixels':0,
             'note':'Exact decoded atlas/mask bytes; PNG encoder metadata is not a reproducibility promise. No HDA or game source is emitted.'}
    (out/'rebuild-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
if __name__=='__main__': main()
