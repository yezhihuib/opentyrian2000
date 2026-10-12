"""Frozen meter V2: coarse armor grouping, unchanged firepower/generator."""
import numpy as np
from PIL import Image
H=32

def profile(x,xs,ys):return np.interp(x,xs,ys)

def material(source,w,h,kind):
    """Continuous scalar shading at32 subpixels, boxed to canonical4x."""
    x=(np.arange(w*H)+.5)/H;y=(np.arange(h*H)+.5)/H
    if kind=='firepower':
        xf=profile(x,[0,.10,.32,.62,1.45,1.72,1.9,2],[.60,.76,1.07,1.11,1.01,.88,.58,.48])
        yf=profile(y,[0,.12,.38,1.0,2.5,2.76,3],[1.13,1.09,1.02,1,.93,.63,.45])
        exponent=.78
    elif kind=='armor':
        xf=profile(x,[0,.20,.52,.85,1.30,2.60,6.45,7.8,8.5,8.8,9],[.50,.69,1.02,1.16,1.11,1.01,.97,.84,.65,.52,.48])
        yf=profile(y,[0,.14,.40,max(.41,h-.36),h-.15,h],[1.08,1.06,1.02,.99,.93,.85])
        exponent=.70
    else:
        # One seam only at an existing original palette/history run boundary.
        xn=x/w
        xf=profile(xn,[0,.025,.065,.105,.16,.29,.72,.86,.945,.98,1],[.50,.69,1.02,1.13,1.08,1,.98,.88,.68,.54,.50])
        yf=profile(y,[0,.10,.30,max(.31,h-.36),h-.16,h],[1.10,1.06,1,.99,.72,.51])
        exponent=.78
    peak=float(source.max());body=source*(255*(peak/255)**exponent/peak)
    factor=xf[None,:]*yf[:,None];factor=np.minimum(factor,250/body.max())
    pix=np.uint8(np.clip(body[None,None,:]*factor[:,:,None],0,255))
    return Image.fromarray(pix).resize((w*4,h*4),Image.Resampling.BOX)
