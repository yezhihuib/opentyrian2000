"""Deterministic packaging only: crop, resize, place, and preview generated artwork.

No painting, recoloring, alpha synthesis, source-pixel upscaling into HD assets,
engine changes, or original game data redistribution.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib, sys, struct
import numpy as np

ROOT = Path(__file__).resolve().parent
REF = ROOT.parent.parent / 'charge-cannon-readonly-audit' / 'reference'
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
SMALL = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
POINT = '--point' in sys.argv
(ROOT/'frames8x').mkdir(exist_ok=True)
(ROOT/'runtime').mkdir(exist_ok=True)
SPECS = [
    (0,252,[250,166,819,1289],[24,0,56,88]),
    (1,253,[15,137,835,1715],[16,0,56,88]),
    (2,254,[7,112,1060,1319],[0,0,80,112]),
]

def bounds(a, t):
    yy,xx=np.where(a>t)
    return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def measure(im):
    a=np.asarray(im).astype(float); alpha=a[:,:,3]; weight=alpha/255
    luma=a[:,:,:3]@[.2126,.7152,.0722]
    return {'bounds_alpha_gt0':bounds(alpha,0),'bounds_alpha_gt16':bounds(alpha,16),
            'bounds_alpha_gt128':bounds(alpha,128),'bounds_alpha_gt240':bounds(alpha,240),
            'edge_alpha_max':int(max(alpha[0].max(),alpha[-1].max(),alpha[:,0].max(),alpha[:,-1].max())),
            'alpha_coverage_logical_pixels':round(float(weight.sum()/64),3),
            'alpha_weighted_luminance_sum':round(float((luma*weight).sum()),3),
            'alpha_centroid_hd':[round(float((alpha*np.arange(96)[None,:]).sum()/alpha.sum()),3),round(float((alpha*np.arange(112)[:,None]).sum()/alpha.sum()),3)],
            'partial_alpha_pixels':int(((alpha>0)&(alpha<255)).sum()),
            'opaque_pixels':int((alpha==255).sum()),'transparent_pixels':int((alpha==0).sum())}

frames={}; metrics=[]
for stage,sid,crop,target in SPECS:
    source=ROOT/f'sources/stage{stage}-generated-soft-edge{"-v2" if stage==0 else ""}.png'
    art=Image.open(source).convert('RGBA').crop(crop)
    art=art.resize((target[2]-target[0],target[3]-target[1]),Image.Resampling.LANCZOS)
    frame=Image.new('RGBA',(96,112)); frame.paste(art,(target[0],target[1]))
    path=ROOT/f'frames8x/shapes8-id{sid}-96x112.png'; frame.save(path); frames[sid]=frame
    hda=ROOT/f'runtime/bullet-{sid}-8.hda'
    hda.write_bytes(struct.pack('<4sIIIIii',b'HDR1',80000+sid,8,12,14,0,0)+frame.tobytes())
    assert hda.read_bytes()[28:]==frame.tobytes()
    metrics.append({'stage':stage,'sheet':8,'sprite_id':sid,'shot_record':101+stage,
        'source':str(source.relative_to(ROOT)),'source_sha256':digest(source),
        'crop_xyxy_exclusive':crop,'crop_basis':'Generated alpha >1 bounds; only isolated alpha=1 noise outside retained crop is omitted.',
        'target_xyxy_exclusive':target,'logical_size':[12,14],'source_size':[96,112],
        'anchor':[0,0],'resampler':'Pillow Lanczos RGBA premultiplied-alpha resize; whole sprite only',
        'filename':str(path.relative_to(ROOT)),'sha256':digest(path),**measure(frame)})

(ROOT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
if '--no-preview' in sys.argv:
    print(json.dumps(metrics,indent=2))
    sys.exit(0)

for scale in [1,2,4]:
    # Output size is literal display pixels. Do not upscale the assembled sheet.
    width=790; rowheight=100 if scale<4 else 125; header=67
    canvas=Image.new('RGB',(width,header+4*rowheight+38),(26,30,36)); draw=ImageDraw.Draw(canvas)
    draw.text((14,10),f'Charge Cannon | ORIGINAL vs HD PILOT | literal {scale}x display',font=FONT,fill=(235,242,250))
    sample_label='nearest/point' if POINT else 'Lanczos'
    draw.text((14,32),f'Offline {sample_label} source-over; not an engine screenshot. Anchor (0,0), logical 12 x 14.',font=SMALL,fill=(185,195,207))
    bgs=[('dark',(13,20,34)),('mid',(62,70,81)),('light',(215,219,225)),('checker',None)]
    for row,(name,bg) in enumerate(bgs):
        y=header+row*rowheight
        draw.text((14,y+22),name,font=FONT,fill=(231,237,245))
        for col,sid in enumerate([252,253,254]):
            x=104+col*222
            for k,label in enumerate(['Original','HD pilot']):
                bx=x+k*98; by=y+24; tw,th=12*scale,14*scale
                draw.text((bx,y+4),f'{sid} {label}',font=SMALL,fill=(195,208,222))
                box=Image.new('RGBA',(tw+16,th+16),(*bg,255) if bg else (0,0,0,255))
                if bg is None:
                    bd=ImageDraw.Draw(box)
                    for yy in range(0,th+16,6):
                        for xx in range(0,tw+16,6):
                            v=75 if (xx//6+yy//6)%2 else 130; bd.rectangle([xx,yy,xx+5,yy+5],fill=(v,v,v,255))
                if k==0:
                    im=Image.open(REF/f'original-bank8-{sid}.png').convert('RGBA').resize((tw,th),Image.Resampling.NEAREST)
                else:
                    im=frames[sid].resize((tw,th),Image.Resampling.NEAREST if POINT else Image.Resampling.LANCZOS)
                box.alpha_composite(im,(8,8)); canvas.paste(box.convert('RGB'),(bx,by))
    draw.text((14,canvas.height-25),'Generated alpha preserved. Original pixels only in private reference comparisons; not runtime assets.',font=SMALL,fill=(162,179,197))
    canvas.save(ROOT/f'previews/comparison-{"point-" if POINT else ""}literal-{scale}x.png')

# Artwork-only transparent strips help downstream reviewers inspect exact frames.
strip=Image.new('RGBA',(3*112,128))
for i,sid in enumerate([252,253,254]): strip.alpha_composite(frames[sid],(i*112+8,8))
strip.save(ROOT/'previews/transparent-frames8x-strip.png')
(ROOT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics,indent=2))
