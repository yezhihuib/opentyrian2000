"""Finite enemy70 native preparation only; no compiler, process or file writes."""
from pathlib import Path
import hashlib,struct,types
OLD_IDS=(91,145,61,101,120,139,168,169,162,260,166,94,7,45,153,154,155)
IDS=OLD_IDS+(70,67) # 67 is only the unchanged player's second resource.
KINDS=('missing','bad','header','magic','density','width','height','anchorx','anchory','short','trailing')
PACKS=('valid',)+tuple(k+'70'for k in KINDS)
ANIMATED_HELPER_SHA='933389576870b26afcad71a3cbfc546806d7f29ea653f237c21ad7a5aa8de690'
BOLTS_HELPER_SHA='158d5ef10020396f1aec1a03a4dc6791eee7c1944be127b868c67b89abf11cdc'
OLD_WRAPPER_SHA='5eaf0406f4449c46b03b83951d80758081e84d271a78d94ddfffad0e3358097c'
CANONICAL={70:'eebd525dab58f0fc6708f4f3c7b15a88e67270be877ff250e93c4bb2a2aeb8de',67:'96b975abbccf393464cf2444f72d63c8ad3f996d8cc5c153593ad16f476e30e0'}
TAIL=(b'\n#include "enemy_vulcan70_native_additions.c.inc"\n'
 b'int main(int argc,char **argv)\n{\n'
 b' if(argc>=2&&!strcmp(argv[1],"--enemy-vulcan70"))return enemy70_main(argc,argv);\n'
 b' return inherited_animated153_dispatch(argc,argv);\n}\n')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def checked_module(path,pin,name):
    raw=Path(path).read_bytes()
    if sha(raw)!=pin:raise ValueError('Changed pinned helper')
    m=types.ModuleType(name);m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__);return m

def source_bundle(root):
    root=Path(root);a=checked_module(root/'tests/projectile_animated153_native_validation.py',ANIMATED_HELPER_SHA,'approved_animated153_helper')
    b=a.old_helper(root,BOLTS_HELPER_SHA);sources,old=b.source_bundle(root)
    animated=a.outer_shim(old)
    return sources,outer_shim(animated)

def outer_shim(raw):
    if sha(raw)!=OLD_WRAPPER_SHA or raw.count(b'int main(')!=1:raise ValueError('Changed previous eight-dispatch wrapper')
    result=raw.replace(b'int main(',b'int inherited_animated153_dispatch(',1)+TAIL
    if reverse_shim(result)!=raw:raise ValueError('Irreversible dispatch shim')
    return result

def reverse_shim(raw):
    if not raw.endswith(TAIL):raise ValueError('Changed new tail')
    body=raw[:-len(TAIL)]
    if body.count(b'int inherited_animated153_dispatch(')!=1 or b'int main('in body:raise ValueError('Changed old dispatcher')
    out=body.replace(b'int inherited_animated153_dispatch(',b'int main(',1)
    if sha(out)!=OLD_WRAPPER_SHA:raise ValueError('Changed inherited wrapper bytes')
    return out

def fixture_bytes(raw,selector,leaf):
    if type(raw)is not bytes or len(raw)!=43036 or type(selector)is not int or selector not in IDS or leaf not in PACKS:raise ValueError('Invalid finite fixture')
    if selector!=70 or leaf=='valid':return raw
    kind=leaf[:-2]
    if kind=='missing':return None
    b=bytearray(raw)
    if kind=='bad':b[128]^=1
    elif kind=='header':b[4]^=1
    elif kind=='magic':b[0]^=1
    elif kind=='short':return bytes(b[:-1])
    elif kind=='trailing':return bytes(b)+b'!'
    else:
        off,value={'density':(8,4),'width':(12,11),'height':(16,13),'anchorx':(20,1),'anchory':(24,1)}[kind]
        struct.pack_into('<I',b,off,value)
    return bytes(b)

def fixture_payloads(hdas,approved_pins,names):
    if any(set(x)!=set(IDS)for x in (hdas,approved_pins,names)):raise ValueError('Exact old17 plus canonical70/67 required')
    for i in IDS:
        if type(i)is not int or type(hdas[i])is not bytes or sha(hdas[i])!=approved_pins[i]:raise ValueError('Changed approved HDA')
        name=Path(names[i])
        if name.is_absolute()or '..'in name.parts or not str(name).endswith('.hda'):raise ValueError('Invalid fixture path')
        if i in CANONICAL and (sha(hdas[i])!=CANONICAL[i] or str(name)!='content/'+CANONICAL[i]+'.hda'):raise ValueError('Canonical asset changed/renamed')
        if i in OLD_IDS and name.name!=str(name):raise ValueError('Old fixture name changed')
    if len(set(names.values()))!=19:raise ValueError('Duplicate fixture path')
    out={}
    for leaf in PACKS:
        for i in IDS:
            b=fixture_bytes(hdas[i],i,leaf)
            if b is not None:out['enemy70-packs/'+leaf+'/'+names[i]]=b
    if len(out)!=227:raise ValueError('Finite fixture cardinality changed')
    return out

def native_input(existing_input,hdt):
    if type(existing_input)is not bytes or len(existing_input)!=98980 or sha(existing_input)!='723d7a7a431b202419c12cce25e7298c2db9e9c5d88ac42cb7dc95fe51fcb463':raise ValueError('Changed old native input')
    if type(hdt)is not bytes or sha(hdt)!='fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b':raise ValueError('Changed original weapon data')
    start=21174+14;record=hdt[start+227*80:start+228*80];port_start=start+1638*80+7*82;port=hdt[port_start:port_start+82]
    if len(record)!=80 or len(port)!=82 or sha(port)!='2e25724292b2e1f2517e41ee0b48acccb5e9fb4e6c67ae9980123028fc72afc2':raise ValueError('Wrong original port bytes')
    return existing_input+record+port

# Counts setup() calls, not assertions, fixtures or gameplay runs.
CASE_INVENTORY={
 'old17_current_direct_full_oracles_not_historical_matrices':17,
 'ordinary_repeated_same_position_and_nextframe':1,'all18_mask':1,
 'malformed_cold_and_warm_old17':22,'used_resource_before_cache_after_handoff':3,
 'unused_resource_failure_old17':1,'background27_fourstages_and_recovery':4,
 'later_native_and_final_halo_cell_writes':2,'source_and_palette_used_before_cache':4,
 'cold_scope_density_variant_flags_bank_palette':7,'player_unclaimed_route_unchanged':1,
 'real_player_enemy_two_order_overlap':2,'independent_enemy_root_epoch_player_allocation_unchanged':1,
 'warm_identity_geometry_before_finish_and_cache':2,'clipped_top_and_horizontal_decline':2,
 'fade_exact_step_and_changed_source_failure':2,
 'cached_sparse_activefade_partial_player_and_full_player_handoff_decline':3,
}
assert sum(CASE_INVENTORY.values())==75
