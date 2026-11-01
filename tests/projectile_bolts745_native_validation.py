"""Pure read-only 7/45 native preparation helpers. Import has no side effects.
No compiler, process, game or file writes. Current companion/launch approval is
external, never inferred from observing its own hash. Old source pins unchanged.
"""
from pathlib import Path
import hashlib,stat,struct,types
BOLTS=(7,45)
IDS=(91,145,61,101,120,139,168,169,162,260,166,94,7,45)
ENCODING='palette-index-r0-g0-binary-alpha-v1'
PULSES_HELPER_SHA='aef5a53ecfdbdd3bcdb4c8c84a42d84f9c5e3eb2ed24b90a294388688d3fd7f5'
PULSES_WRAPPER_SHA='80776b35739f5751f465af4329771dc9a8f3d7fd60572c536fd3266f0430536e'
PULSES_STDIN_SHA='723d7a7a431b202419c12cce25e7298c2db9e9c5d88ac42cb7dc95fe51fcb463'
PACK_NAMES=('valid',)+tuple(kind+str(i)for i in BOLTS for kind in ('missing','bad','header','short','trailing','magic','density','width','height','anchorx','anchory'))+tuple('missing'+str(i)for i in IDS[:12])
TAIL=(b'\n#include "projectile_bolts745_native_additions.c.inc"\n'
      b'int main(int argc,char **argv)\n{\n'
      b' if(argc>=2&&!strcmp(argv[1],"--enemy-bolts745"))return bolts745_main(argc,argv);\n'
      b' return inherited_pulses_dispatch(argc,argv);\n}\n')
OLD_HDA={91: {'path': 'assets/hd/current-compat/projectile91/enemy-projectile91-91-8.hda', 'sha256': '2940279a66281c16838d4e070421a581ea0e4b5bb91cf85a1cbc532902933e4c'}, 145: {'path': 'assets/hd/current-compat/projectile145/enemy-projectile145-145-8.hda', 'sha256': 'e4863397d4d7e9874e96e642ce6596c90e99009014b746491016c0423e099c83'}, 61: {'path': 'assets/hd/current-compat/projectile61/enemy-projectile61-61-8.hda', 'sha256': '3530c27302a2cb3d26830711cd4b94a01aacbfad748c91aea219bbc81b0c5c29'}, 101: {'path': 'assets/hd/current-compat/projectile-blue-triplet/enemy-projectile-blue-triplet-101-8.hda', 'sha256': '4f1cb932fa0418f3236d8240a3012ec19d65ab3d33a862190a75f53302db8ac6'}, 120: {'path': 'assets/hd/current-compat/projectile-blue-triplet/enemy-projectile-blue-triplet-120-8.hda', 'sha256': 'e8935de840d09ed83e65206664ba3a4ddf25b11764ba2b6038ac752140dcb83b'}, 139: {'path': 'assets/hd/current-compat/projectile-blue-triplet/enemy-projectile-blue-triplet-139-8.hda', 'sha256': '47a6941988a2e2a4835859dfc1cf12f2481b2bf29bab18be94307b408cf34942'}, 168: {'path': 'assets/hd/current-compat/projectile-gold-pulse/enemy-projectile-gold-pulse-168-8.hda', 'sha256': 'a453142d1d1d5e662a5c36053f5af42b719fa2a2d993e7b2384c5d4231cfdb14'}, 169: {'path': 'assets/hd/current-compat/projectile-gold-pulse/enemy-projectile-gold-pulse-169-8.hda', 'sha256': '1dc205caccc8320968389868f844cacd50046a285b2d1e90f5b9073fcfddc831'}, 162: {'path': 'assets/hd/current-compat/projectile-statics/enemy-projectile-statics-162-8.hda', 'sha256': '2d045f7fc472ed6e2f33f9d742072f3b7ea1c3a606d8f1909bbcd33b57ae0119'}, 260: {'path': 'assets/hd/current-compat/projectile-statics/enemy-projectile-statics-260-8.hda', 'sha256': '5545ee065fcf879eb306a6c25dc0b9be8ecf8dcaa5154cdbb69ae907e75adf8e'}, 166: {'path': 'assets/hd/current-compat/projectile-pulses16694/enemy-projectile-pulses16694-166-8.hda', 'sha256': 'e14f6cc59d8f0773fa20b840c4ea453bb6c2afebcc4e27806c927c2f9751fb89'}, 94: {'path': 'assets/hd/current-compat/projectile-pulses16694/enemy-projectile-pulses16694-94-8.hda', 'sha256': 'cf6f70641746a3b8eb91d61d5c414af7545e748f6583351972aa76c46f813f93'}}
HDA_NAMES={i:Path(row["path"]).name for i,row in OLD_HDA.items()}
HDA_NAMES.update({i:f"enemy-projectile-bolts745-{i}-8.hda"for i in BOLTS})

def fail(message):raise ValueError(message)
def sha(raw):
    if type(raw)is not bytes:fail('Expected immutable bytes')
    return hashlib.sha256(raw).hexdigest()
def checked_file(path,pin=None,maximum=16*1024*1024):
    path=Path(path).absolute()
    for p in reversed((path,*path.parents)):
        s=p.lstat()
        if stat.S_ISLNK(s.st_mode) or getattr(s,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0):fail('Linked/reparse input')
    s=path.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_size>maximum:fail('Expected independent bounded regular input')
    raw=path.read_bytes();a=path.lstat()
    if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_nlink)!=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_nlink) or len(raw)!=s.st_size:fail('Changed input while reading')
    if pin is not None and sha(raw)!=pin:fail('Changed pinned input: '+str(path))
    return raw

def pulses_helper(root):
    path=Path(root)/'tests/projectile_pulses16694_native_validation.py';raw=checked_file(path,PULSES_HELPER_SHA)
    module=types.ModuleType('frozen_pulses16694_for_bolts745');module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module

def authoring_helper(root):
    # Current batch source bytes must be bound by the reviewed launch closure.
    # This loader does NOT self-approve its mutable companion or module hash.
    path=Path(root)/'scripts/current_projectile_bolts745_compatibility.py';raw=checked_file(path)
    module=types.ModuleType('current_bolts745_authoring');module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    if module.ENCODING!=ENCODING or module.IDS!=(1560007,1560045):fail('Changed finite authoring contract')
    return module

def outer_shim(raw):
    if sha(raw)!=PULSES_WRAPPER_SHA or raw.count(b'int main(')!=1 or b'inherited_pulses_dispatch' in raw:fail('Changed inherited pulses wrapper')
    result=raw.replace(b'int main(',b'int inherited_pulses_dispatch(',1)+TAIL
    if reverse_shim(result)!=raw:fail('Irreversible outer shim')
    return result

def reverse_shim(raw):
    if type(raw)is not bytes or not raw.endswith(TAIL):fail('Changed bolts wrapper tail')
    body=raw[:-len(TAIL)]
    if body.count(b'int inherited_pulses_dispatch(')!=1 or b'int main(' in body:fail('Changed outer dispatcher')
    result=body.replace(b'int inherited_pulses_dispatch(',b'int main(',1)
    if sha(result)!=PULSES_WRAPPER_SHA:fail('Changed inherited bytes beneath shim')
    return result

def source_bundle(root):
    old=pulses_helper(root);sources,pulses=old.source_bundle(root)
    if set(sources)!=set(old.SOURCE_PINS) or any(sha(raw)!=old.SOURCE_PINS[n]for n,raw in sources.items()):fail('Changed six inherited source bytes')
    wrapped=outer_shim(pulses)
    if reverse_shim(wrapped)!=pulses:fail('Source shim mismatch')
    return sources,wrapped

def companion_bytes(root,approved_sha256):
    if type(approved_sha256)is not str or len(approved_sha256)!=64 or any(c not in '0123456789abcdef'for c in approved_sha256):fail('Explicit reviewed companion SHA256 required')
    return checked_file(Path(root)/'tests/projectile_bolts745_native_additions.c.inc',approved_sha256)

def native_inputs(root,data):
    old=pulses_helper(root);legacy,new=old.native_inputs(root,data)
    current,metadata=old.pulses_native_input(root,data,new)
    if sha(current)!=PULSES_STDIN_SHA or len(current)!=98980:fail('Changed palette5 original native input')
    return legacy,new,current,dict(metadata,scope='bolts745 receives exact existing pulses16694 palette5 stream; bank8/bank9/Christmas bytes unchanged; not an executed native result')

def registered_hdas(root):
    result={i:checked_file(Path(root)/row['path'],row['sha256'],43036)for i,row in OLD_HDA.items()}
    old=pulses_helper(root)
    if old.registered_hdas(root)!={i:result[i]for i in old.PULSES}:fail('Changed previous current166/94 resources')
    c=authoring_helper(root);rows=c.load(root)
    if len(rows)!=2:fail('Expected exact two indexed rows')
    for row in rows.values():
        if row.get('encoding')!=ENCODING:fail('Missing indexed representation')
        i=row['identity']-1560000;raw=checked_file(Path(root)/row['source_path'],row['sha256'],43036)
        c.validate_hda(root,1560000+i,raw);result[i]=raw
    if set(result)!=set(IDS):fail('Changed full14 finite payload set')
    return result

def fixture_bytes(raw,selector,leaf):
    if type(raw)is not bytes or len(raw)!=43036 or type(selector)is not int or selector not in IDS or type(leaf)is not str or leaf not in PACK_NAMES:fail('Invalid finite fixture arguments')
    if leaf=='missing'+str(selector):return None
    result=bytearray(raw)
    if leaf=='bad'+str(selector):result[128]^=1
    if leaf=='header'+str(selector):result[4]^=1
    if leaf=='magic'+str(selector):result[0]^=1
    for field,offset,value in (('density',8,4),('width',12,11),('height',16,13),('anchorx',20,1),('anchory',24,1)):
        if leaf==field+str(selector):struct.pack_into('<I',result,offset,value)
    if leaf=='short'+str(selector):result=result[:-1]
    if leaf=='trailing'+str(selector):result+=b'!'
    return bytes(result)

def fixture_schema():
    sentinel=bytes(43036)
    return {leaf:tuple(i for i in IDS if fixture_bytes(sentinel,i,leaf)is not None)for leaf in PACK_NAMES}

def validate_hdas(root,hdas):
    if type(hdas)is not dict or any(type(i)is not int for i in hdas) or set(hdas)!=set(IDS):fail('Expected all14 exact integer selectors')
    c=authoring_helper(root)
    for i,raw in hdas.items():
        if type(raw)is not bytes or len(raw)!=43036:fail('Invalid payload argument')
        if i in OLD_HDA:
            if sha(raw)!=OLD_HDA[i]['sha256']:fail('Changed old12 fixture payload')
        else:c.validate_hda(root,1560000+i,raw)
    return True

def fixture_payloads(root,hdas):
    """Return only new packs. Caller may request inherited fixtures separately."""
    validate_hdas(root,hdas)
    result={}
    for leaf in PACK_NAMES:
        for i in IDS:
            raw=fixture_bytes(hdas[i],i,leaf)
            if raw is not None:result[f'bolts745-packs/{leaf}/{HDA_NAMES[i]}']=raw
    if len(result)!=476 or len(PACK_NAMES)!=35:fail('Changed finite fixture count')
    return result

def inherited_fixture_payloads(root,hdas):
    """Delegate unchanged old fixture producer; no regeneration of old semantics."""
    validate_hdas(root,hdas);old=pulses_helper(root)
    result=old.fixture_payloads(root,{i:hdas[i]for i in old.IDS},old.registration(root))
    if len(result)!=1241:fail('Changed inherited fixture closure')
    return result

def preparation_metadata(root,hdas):
    validate_hdas(root,hdas);sources,wrapper=source_bundle(root)
    return {'schema':'bolts745-native-preparation-v1','status':'PREPARED_ONLY_NOT_EXECUTED','encoding':ENCODING,
        'old_helper_sha256':PULSES_HELPER_SHA,'old_wrapper_sha256':PULSES_WRAPPER_SHA,'outer_wrapper_sha256':sha(wrapper),
        'sources':{n:sha(raw)for n,raw in sources.items()},'payloads':{str(i):sha(raw)for i,raw in hdas.items()},
        'packs':{n:list(v)for n,v in fixture_schema().items()},'new_fixture_count':476,
        'companion_status':'not self-approved; caller must supply independently reviewed final SHA256',
        'scope':'pure source/fixture preparation, no compiler/process/game/launcher execution'}
