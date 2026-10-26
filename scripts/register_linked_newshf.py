#!/usr/bin/env python3
"""Deterministic registration only; never generates or paints creative pixels.

The approved crop intentionally excludes AI silhouette rims. Original game
masks, logical canvas, anchors, and segment boundaries remain unchanged.
"""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageChops
from current_linked_newshf_compatibility import sha, INPUT_ROOT, encode_png
CROP=(80,250,646,1830)

def registered(raw):
    import io
    im=Image.open(io.BytesIO(raw)).convert('RGBA')
    if im.size not in ((725,2169),(725,2168),(725,2170)):
        raise ValueError('Unexpected AI raw canvas; inspect and approve a new registration')
    part=im.crop(CROP).resize((192,552),Image.Resampling.LANCZOS)
    part.putalpha(part.getchannel('A').point([0]*128+[255]*128))
    whole=Image.new('RGBA',(192,672));whole.paste(part,(0,0))
    return whole

def run(root,cold,bottom,destination,middle=None):
    if destination.exists(): raise ValueError('Registration destination must be new')
    inputs={'cold':cold,'bottom':bottom}
    if middle: inputs['middle']=middle
    raw={k:p.read_bytes() for k,p in inputs.items()}
    if sha(raw['cold'])!='825b8175fbe9da90b5e762593c97da1000d96c2d2050f11db2fd662fe8765b9d':
        raise ValueError('Cold raw is not the reviewed V2 registration source')
    images={k:registered(v) for k,v in raw.items()}
    outputs={'cold-whole.png':encode_png(images['cold'])}
    for key,base,start,name in [('bottom',121,448,'hot-bottom-overlay.png'),('middle',83,224,'alternate-middle-overlay.png')]:
        if key not in images: continue
        piece=images[key].crop((0,start,192,start+224))
        mask=Image.open(root/INPUT_ROOT/f'change-{base}.png').convert('L').resize((192,224),Image.Resampling.NEAREST)
        mask=ImageChops.multiply(mask,piece.getchannel('A'))
        piece.putalpha(mask); clean=Image.new('RGBA',piece.size);clean.paste(piece,(0,0),mask)
        outputs[name]=encode_png(clean)
    destination.mkdir(parents=True)
    for n,data in outputs.items(): (destination/n).write_bytes(data)
    receipt=dict(schema='linked-newshf-registration-v1',crop=list(CROP),body_size=[192,552],canvas=[192,672],resample='Pillow-LANCZOS',alpha='threshold128',original_mask='applied by finite art builder',raw_sha256={k:sha(v) for k,v in raw.items()},output_sha256={k:sha(v) for k,v in outputs.items()},scope='AI silhouette rims cropped; game geometry preserved; no creative pixel generation',cold_registration_metrics=dict(raw_alpha_mass=246946934,crop_excluded_alpha_mass=20698184,crop_excluded_alpha_fraction=0.08381632306477634,resized_opaque_pixels=105984,native_mask_clipped_pixels=3712,native_mask_clip_fraction=3712/105984,foreground_holes=0,top_opaque_pixels=192,seam_rows=[223,224,447,448],seam_opaque_pixels=[192,192,192,192]))
    (destination/'registration.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['root','cold','bottom','destination']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--middle',type=Path)
    a=p.parse_args(); print(json.dumps(run(a.root,a.cold,a.bottom,a.destination,a.middle),indent=2))
