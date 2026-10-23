#!/usr/bin/env python3
"""Pure Pillow/stdlib Charge body recipe. Import performs no file I/O.

API: generate_frames(master: PIL.Image.Image, recipe: dict) -> dict[(phase,charge), PIL.Image.Image].
The only editable pixel source is the normalized master. This module never reads
original game art, V2 candidate sheets, generated frame inputs or private paths.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image, ImageFilter, __version__ as PIL_VERSION


def generate_frames(master, recipe):
    """Pure image transform: returns nine new RGBA images; does not mutate inputs or perform I/O."""
    P=recipe
    W,H=P['output_size']
    assert master.size==(W,H)==(96,112)
    assert P['logical_size']==[12,14] and P['anchor']==[0,0] and P['scale_factor']==8
    master=master.convert('RGBA')
    core=Image.new('L',(W,H),0);metal_gate=Image.new('L',(W,H),0)
    cx0,cy0,cx1,cy1=[v*8 for v in P['core_logical_region_xyxy']]
    for y in range(H):
        for x in range(W):
            r,g,b,a=master.getpixel((x,y))
            if a and cx0<=x<cx1 and cy0<=y<cy1 and r>b+6 and r>=g*.85:
                edge=min(1.,(x-cx0+1)/2,(cx1-x)/2,(y-cy0+1)/2,(cy1-y)/2)
                core.putpixel((x,y),round(255*edge))
            if a>=128 and b>=r+10 and g>=r+3 and r+g+b>60:
                metal_gate.putpixel((x,y),255)

    highlights=[];sparks=[]
    for phase in range(3):
        logical_weight=Image.new('L',(12,14),0)
        # Sparse effect-control coordinates/relative weights, not an original image.
        for x,y,amount in P['highlight_control_points'][phase]:
            logical_weight.putpixel((x,y),round(255*amount/P['highlight_weight_normalizer']))
        weight=logical_weight.resize((W,H),Image.Resampling.NEAREST)
        support=weight.point(lambda v:255 if v else 0).filter(ImageFilter.MaxFilter(3))
        weight=weight.filter(ImageFilter.GaussianBlur(P['highlight_blur_radius_px']))
        for y in range(H):
            for x in range(W):
                if not support.getpixel((x,y)) or not metal_gate.getpixel((x,y)) or core.getpixel((x,y)):
                    weight.putpixel((x,y),0)
        highlights.append(weight)
        spark=Image.new('RGBA',(W,H),(0,0,0,0))
        for lx,ly,palette_id in P['spark_control_points'][phase]:
            tx,ty=lx*8+4,ly*8+4
            rgb=tuple(P['spark_palette_rgb'][str(palette_id)])
            for dx,dy,alpha in P['spark_footprint']:
                assert 0<tx+dx<W-1 and 0<ty+dy<H-1
                spark.putpixel((tx+dx,ty+dy),(*rgb,alpha))
        sparks.append(spark)

    states={}
    for phase in range(3):
        zero=master.copy();delta=P['core_phase_rgb_add'][phase]
        for y in range(H):
            for x in range(W):
                weight=core.getpixel((x,y))/255
                if weight:
                    rgba=zero.getpixel((x,y))
                    zero.putpixel((x,y),tuple(min(255,round(rgba[k]+delta[k]*weight)) for k in range(3))+(rgba[3],))
        one=zero.copy()
        for y in range(H):
            for x in range(W):
                t=P['highlight_strength']*highlights[phase].getpixel((x,y))/255
                if t:
                    rgba=one.getpixel((x,y));target=P['highlight_target_rgb']
                    one.putpixel((x,y),tuple(round(rgba[k]*(1-t)+target[k]*t) for k in range(3))+(rgba[3],))
        two=Image.alpha_composite(one,sparks[phase])
        for charge,image in enumerate([zero,one,two]):
            states[(phase,charge)]=image

    # Fail closed on unintended shape, alpha, core or effect-region changes.
    base_alpha=master.getchannel('A').tobytes()
    for (phase,charge),image in states.items():
        if charge<2:assert image.getchannel('A').tobytes()==base_alpha
        for y in range(H):
            for x in range(W):
                pixel=image.getpixel((x,y));base=master.getpixel((x,y))
                if not pixel[3]:assert pixel==(0,0,0,0)
                if x in [0,W-1] or y in [0,H-1]:assert pixel[3]==0
                permitted=core.getpixel((x,y)) or (charge>=1 and highlights[phase].getpixel((x,y))) or (charge==2 and sparks[phase].getpixel((x,y))[3])
                if not permitted:assert pixel==base
                if core.getpixel((x,y)):assert pixel==states[(phase,0)].getpixel((x,y))
        if charge==2:
            diff=[(x,y) for y in range(H) for x in range(W) if image.getpixel((x,y))!=states[(phase,1)].getpixel((x,y))]
            assert len(diff)==4*len(P['spark_footprint']) and all(sparks[phase].getpixel((x,y))[3] for x,y in diff)

    return states


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(argv=None):
    here=Path(__file__).resolve().parent
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--master',type=Path,default=here/'master.png')
    parser.add_argument('--recipe',type=Path,default=here/'recipe.json')
    parser.add_argument('--output',type=Path,default=here/'generated')
    args=parser.parse_args(argv)
    recipe=json.loads(args.recipe.read_text())
    assert file_sha256(args.master)==recipe['master_sha256'], 'Master changed: review and explicitly update recipe SHA.'
    master=Image.open(args.master).convert('RGBA')
    states=generate_frames(master,recipe)
    args.output.mkdir(parents=True,exist_ok=True)
    files=[]
    for (phase,charge),image in states.items():
        sid=recipe['sprite_ids'][phase][charge]
        name=f'bank9-id{sid}-phase{phase}-charge{charge}.png'
        image.save(args.output/name,optimize=False)
        files.append({'phase':phase,'charge':charge,'sprite_id':sid,'file':name,'sha256':file_sha256(args.output/name)})
    manifest={'schema':'charge-nine-state-generated-v2','editable_image_source':'master.png ONLY',
              'master_sha256':file_sha256(args.master),'recipe_sha256':file_sha256(args.recipe),
              'generator_sha256':file_sha256(__file__),'pillow_version':PIL_VERSION,
              'size':[96,112],'logical_size':[12,14],'anchor':[0,0],
              'gr':recipe['gr'],'initial_draw_slot_order':recipe['initial_draw_slot_order'],
              'files':files,'all_invariants_passed':True,'runtime_integration':False}
    (args.output/'generated-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
