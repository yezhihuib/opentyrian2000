"""Finite transport/metadata validation; NOT qualified artwork or production producer.
No load()/manifest writer exists until separately reviewed art provenance is pinned.
Test fixtures must remain under tests, never in assets or authoring-inputs.
"""
import struct
IDS=(1570153,1570154,1570155)
ENCODING='palette-index-r0-g0-binary-alpha-v1'
PALETTE={153:frozenset((112,120,121,122,123,124,125)),154:frozenset((112,119,120,121,122,123,124,125)),155:frozenset((112,119,120,121,122,123,124,125))}
def metadata(row):
    i=row.get('identity');d=row.get('density');e=row.get('encoding')
    if type(i)is not int or i not in IDS or type(d)is not int or d!=8 or e!=ENCODING:
        raise ValueError('Invalid finite animated153 identity/density/encoding')
    return {'identity':i,'density':d,'encoding':e}
def validate_transport(identity,blob,native_mask):
    """Structural check only: does NOT authenticate source, artwork, pins or coverage."""
    metadata({'identity':identity,'density':8,'encoding':ENCODING})
    if type(blob)is not bytes or len(blob)!=43036 or blob[:28]!=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0):
        raise ValueError('Invalid indexed HDR1 transport')
    if type(native_mask)is not bytes or len(native_mask)!=168 or any(x not in (0,1)for x in native_mask):
        raise ValueError('Invalid native mask')
    colors=PALETTE[identity-1570000];occupied=set()
    for n in range(10752):
        q=blob[28+n*4:32+n*4];cell=(n//96//8)*12+(n%96)//8
        if q[3]==0:
            if any(q):raise ValueError('Nonzero transparent texel')
        elif q[3]!=255 or q[1] or q[2] or q[0]not in colors or not native_mask[cell]:
            raise ValueError('Invalid indexed texel/support')
        else:occupied.add(cell)
    return frozenset(occupied)
