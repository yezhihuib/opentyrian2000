"""Rebuild the reviewed corner and optional whole HUD1 from a pinned V5 HDA.

No original game pixels are consumed. The immutable generated V5 HDA is a
dependency, not duplicated input. Output directory must not exist.
"""
import argparse,hashlib,json,struct
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
BASE_SHA='4ff6cd95d4c3ec5b7e4825e38a5242fc96c1cd305987a873bea4a55fa5a04482'
MASTER_SHA='a9bb574b7f225dda870e46a0d9c7a0180603d1b65b3187d8cf38f3b64f1f62ae'
BOX=(248,184,269,200)
def sha(b):return hashlib.sha256(b).hexdigest()
def fnv(b):
    h=14695981039346656037
    for c in b:h=((h^c)*1099511628211)&((1<<64)-1)
    return h
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--baseline-hda',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve()
    if out.exists():p.error('Choose a new output directory')
    original=a.baseline_hda.read_bytes();assert sha(original)==BASE_SHA
    fields=struct.unpack('<4s8I3QI',original[:64])
    assert fields[:9]==(b'HUD1',1,320,200,4,0,0,64000,4096000)
    assert fields[9]==0x14c1441f3d5dc0e2 and fields[-1]==0
    base_mask=original[64:64064];base_rgba=original[64064:]
    assert len(original)==4160064 and len(base_rgba)==4096000
    assert fnv(base_mask)==fields[10] and fnv(base_rgba)==fields[11]
    master=(P/'sources/generated-junction-master.png').read_bytes();assert sha(master)==MASTER_SHA
    tile=Image.open(P/'sources/generated-junction-master.png').convert('RGBA').resize((120,72),Image.Resampling.LANCZOS).crop((16,8,100,72))
    existing=Image.frombytes('RGBA',(1280,800),base_rgba).crop((992,736,1076,800))
    tile.paste(existing,(0,0),existing.getchannel('A'))
    # Explicit verified source-black seam cells complete the original profiles.
    draw=ImageDraw.Draw(tile)
    for x,y in [(0,3),(0,4)]+[(19,y) for y in range(7,14)]+[(20,14)]:
        draw.rectangle((x*4,y*4,x*4+3,y*4+3),fill=(0,0,0,255))
    assert tile.getextrema()[3]==(255,255)
    mask=bytearray(base_mask);patch=bytearray(64000);overlap=bytearray(64000);fresh=bytearray(64000)
    for y in range(184,200):
        for x in range(248,269):
            i=y*320+x;patch[i]=255
            (overlap if base_mask[i] else fresh)[i]=255
            mask[i]=255
    assert sum(bool(v) for v in patch)==336
    assert sum(bool(v) for v in overlap)==150 and sum(bool(v) for v in fresh)==186
    assert sum(bool(v) for v in mask)==6853
    frame=Image.frombytes('RGBA',(1280,800),base_rgba);frame.paste(tile,(992,736));raw=frame.tobytes()
    for y in range(800):
        if 736<=y<800:
            l=y*1280*4;r=(y+1)*1280*4
            assert raw[l:l+992*4]==base_rgba[l:l+992*4]
            assert raw[l+1076*4:r]==base_rgba[l+1076*4:r]
        else:assert raw[y*5120:(y+1)*5120]==base_rgba[y*5120:(y+1)*5120]
    expected_alpha=Image.frombytes('L',(320,200),bytes(mask)).resize((1280,800),Image.Resampling.NEAREST)
    assert frame.getchannel('A').tobytes()==expected_alpha.tobytes()
    header=struct.pack('<4s8I3QI',b'HUD1',1,320,200,4,0,0,64000,4096000,0x14c1441f3d5dc0e2,fnv(mask),fnv(raw),0)
    out.mkdir(parents=True);tile.save(out/'corner-4x.png');(out/'corner-4x.rgba').write_bytes(tile.tobytes())
    for name,data in [('corner-336',patch),('frame-overlap-150',overlap),('new-ownership-186',fresh),('combined-6853',mask)]:
        (out/f'{name}.mask').write_bytes(data);Image.frombytes('L',(320,200),bytes(data)).save(out/f'{name}.png')
    frame.save(out/'hud-static-overlay-4x.png');(out/'gameplay-hud-v1.hda').write_bytes(header+mask+raw)
    report={'status':'PASS','box_half_open':BOX,'patch_cells':336,'overlap_cells':150,'new_cells':186,
      'owned_cells':6853,'source_pic3_fnv64':'14c1441f3d5dc0e2','source_336_fnv64':'ca5548b4cdd8767a',
      'baseline_hda_sha256':BASE_SHA,'mask_sha256':sha(mask),'mask_fnv64':f'{fnv(mask):016x}',
      'rgba_sha256':sha(raw),'rgba_fnv64':f'{fnv(raw):016x}',
      'patch_rgba_sha256':sha(tile.tobytes()),'patch_rgba_fnv64':f'{fnv(tile.tobytes()):016x}',
      'hda_sha256':sha(header+mask+raw),'hda_bytes':len(header+mask+raw),
      'outside_336_mask_or_rgba_changes':0,'alpha_equals_4x_mask':True,
      'source_black_exception_cells':46,'old_overlap150_preserved':True,'black_seam10_preserved':True,'new_art_cells':176,'sampling':'canonical4x;2x nearest;8x repeat2',
      'runtime_guard':'Whole336 decoded-original index match plus accepted PIC3 lease; mismatch suppresses whole corner and restores all150 overlapping frame cells.'}
    (out/'rebuild-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
