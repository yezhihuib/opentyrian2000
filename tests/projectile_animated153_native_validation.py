"""Pure finite native preparation, no compiler/process/game or implicit approval."""
from pathlib import Path
import hashlib,struct,types
IDS=(91,145,61,101,120,139,168,169,162,260,166,94,7,45,153,154,155)
NEW=(153,154,155)
KINDS=('missing','bad','header','magic','density','width','height','anchorx','anchory','short','trailing')
PACKS=('valid',)+tuple(k+str(i)for i in NEW for k in KINDS)
OLD_WRAPPER_SHA='c24cb2937f8b97279db5fe0cb6a56efd9551379c601cd8085409992751ff48ed'
TAIL=(b'\n#include "projectile_animated153_background_native.c.inc"\n'
      b'#include "projectile_animated153_native_additions.c.inc"\n'
      b'int main(int argc,char **argv)\n{\n'
      b' if(argc>=2&&!strcmp(argv[1],"--enemy-animated153"))return animated153_main(argc,argv);\n'
      b' return inherited_bolts_dispatch(argc,argv);\n}\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def old_helper(root,approved_sha256):
    p=Path(root)/'tests/projectile_bolts745_native_validation.py';b=p.read_bytes()
    if sha(b)!=approved_sha256:raise ValueError('Unreviewed old helper')
    m=types.ModuleType('reviewed_bolts745_native_helper');m.__file__=str(p);exec(compile(b,str(p),'exec'),m.__dict__);return m
def outer_shim(raw):
    if sha(raw)!=OLD_WRAPPER_SHA or raw.count(b'int main(')!=1:raise ValueError('Changed inherited wrapper')
    result=raw.replace(b'int main(',b'int inherited_bolts_dispatch(',1)+TAIL
    if reverse_shim(result)!=raw:raise ValueError('Irreversible current shim')
    return result
def reverse_shim(raw):
    if not raw.endswith(TAIL):raise ValueError('Changed current tail')
    body=raw[:-len(TAIL)]
    if body.count(b'int inherited_bolts_dispatch(')!=1 or b'int main('in body:raise ValueError('Changed dispatcher')
    original=body.replace(b'int inherited_bolts_dispatch(',b'int main(',1)
    if sha(original)!=OLD_WRAPPER_SHA:raise ValueError('Changed old dispatcher bytes')
    return original
def fixture_bytes(raw,selector,leaf):
    if type(raw)is not bytes or len(raw)!=43036 or type(selector)is not int or selector not in IDS or leaf not in PACKS:raise ValueError('Invalid fixture arguments')
    if leaf=='missing'+str(selector):return None
    b=bytearray(raw)
    if leaf=='bad'+str(selector):b[128]^=1
    if leaf=='header'+str(selector):b[4]^=1
    if leaf=='magic'+str(selector):b[0]^=1
    for k,off,value in (('density',8,4),('width',12,11),('height',16,13),('anchorx',20,1),('anchory',24,1)):
        if leaf==k+str(selector):struct.pack_into('<I',b,off,value)
    if leaf=='short'+str(selector):b=b[:-1]
    if leaf=='trailing'+str(selector):b+=b'!'
    return bytes(b)
def fixture_payloads(hdas,approved_hda_sha256,names):
    if set(hdas)!=set(IDS)or set(approved_hda_sha256)!=set(IDS)or set(names)!=set(IDS):raise ValueError('Exact seventeen reviewed inputs required')
    if any(type(i)is not int or sha(b)!=approved_hda_sha256[i]for i,b in hdas.items()):raise ValueError('Changed reviewed HDA')
    if len(set(names.values()))!=17 or any(Path(n).name!=n or not n.endswith('.hda')for n in names.values()):raise ValueError('Invalid fixture filenames')
    out={}
    for leaf in PACKS:
        for i,b in hdas.items():
            q=fixture_bytes(b,i,leaf)
            if q is not None:out['animated153-packs/'+leaf+'/'+names[i]]=q
    if len(out)!=575:raise ValueError('Changed finite fixture cardinality')
    return out
CASE_INVENTORY={
 'valid_exact_oracle_bit16':3,'four_frames_same_position':1,
 'four_draws_same_frame_same_position':1,'all17_mask':1,
 'three_empty_native_cells153':1,'permember_11malformations_cold_warm':66,
 'used_unused_resource_before_cached':12,'foreground_palette_before_cached_nextdraw':9,
 'resource_mutation_after_full_handoff':3,'asymmetric_live_palette3':3,
 'cold_scope6x3':18,'player_and_generic3':3,'background27_fourstages_fiveids':20,
}
# This counts setup() calls, not assertions, fixture packs or gameplay runs.
assert sum(CASE_INVENTORY.values())==141
