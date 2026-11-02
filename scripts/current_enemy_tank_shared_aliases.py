"""Finite byte-identical global aliases; no image conversion or new material."""
from pathlib import Path,PurePosixPath
import hashlib,struct
from current_enemy_orb_protron_aliases import read_regular, git_blob
IDENTITIES = {146: 1220146, 147: 1220147}
CANONICAL_SOURCES = {146: 'assets/hd/current-compat/tank-shell/enemy-tank-shell-146-8.hda', 147: 'assets/hd/current-compat/tank-shell/enemy-tank-shell-147-8.hda'}
REVISION='canonical-enemy-tank-shared-aliases-v1'
ENCODING='rgba-straight-alpha-v1'
PREFIX='assets/hd/global-assets-v1/content/'
def canonical_source(index):return CANONICAL_SOURCES[index]
def specs(root):
 from current_tank_shell_compatibility import load as canonical_load
 rows=canonical_load(root)
 return {i:rows['assets/gameplay/'+Path(canonical_source(i)).name]['sha256'] for i in IDENTITIES}
def generate(root):
 result={}
 for i,pin in specs(root).items():
  raw=read_regular(root,canonical_source(i))
  if len(raw)!=43036 or hashlib.sha256(raw).hexdigest()!=pin or struct.unpack('<4s6I',raw[:28])!=(b'HDR1',IDENTITIES[i],8,12,14,0,0):raise ValueError('Canonical alias source changed')
  result[PREFIX+pin+'.hda']=raw
 return result
def rows_for(root):
 blobs=generate(root);rows=[]
 for i,pin in specs(root).items():
  source=PREFIX+pin+'.hda';raw=blobs[source]
  rows.append(dict(source_path=source,destination='assets/global/content/'+pin+'.hda',group='global-source-identity',revision=REVISION,identity=IDENTITIES[i],density=8,encoding=ENCODING,canonical_source=canonical_source(i),bytes=len(raw),sha256=pin,git_blob=git_blob(raw)))
 return sorted(rows,key=lambda x:x['destination'])
def load(root):
 expected=generate(root)
 for name,raw in expected.items():
  if read_regular(root,name)!=raw:raise ValueError('Global alias differs from canonical bytes')
 return {row['destination']:row for row in rows_for(root)}
def validate_runtime_rows(root,manifest,required=False):
 SPECS=specs(root)
 rows=manifest.get('files')
 if not isinstance(rows,list):raise ValueError('Expected finite runtime rows')
 identities={IDENTITIES[i] for i in SPECS};sources={PREFIX+s+'.hda'for s in SPECS.values()};destinations={'assets/global/content/'+s+'.hda'for s in SPECS.values()};selected=[]
 # Existing manual consumers stay exactly as they were; no relaxed old tank-shell
 # rules and no second player gate. Any other occurrence of these exact material
 # identities, including a hidden HDR1 header without metadata, is a collision.
 manual={canonical_source(i):('assets/gameplay/'+Path(canonical_source(i)).name,pin)for i,pin in SPECS.items()}
 for row in rows:
  if not isinstance(row,dict):raise ValueError('Expected runtime row object')
  source=row.get('source_path');dest=row.get('destination');identity=row.get('identity')
  known_manual=source in manual if isinstance(source,str)else False
  if known_manual:
   wanted,pin=manual[source]
   if dest!=wanted or row.get('sha256')!=pin or any(k in row for k in ('identity','density','encoding','canonical_source')):raise ValueError('Canonical manual identity collision')
   continue
  match=(source in sources if isinstance(source,str)else False)or(dest in destinations if isinstance(dest,str)else False)or (type(identity)is int and identity in identities) or row.get('revision')==REVISION or row.get('sha256')in SPECS.values()
  if isinstance(source,str)and source.endswith('.hda'):
   p=PurePosixPath(source)
   if p.is_absolute()or '..'in p.parts or '\\'in source:raise ValueError('Unsafe runtime source')
   q=Path(root)/source
   if q.is_file():
    if any(x.is_symlink()for x in (q,*q.parents)):raise ValueError('Symlink runtime source')
    with q.open('rb')as stream:header=stream.read(8)
    if len(header)==8 and header[:4]==b'HDR1'and struct.unpack('<I',header[4:])[0]in identities:match=True
  if match:selected.append(row)
 if not selected and not required:return
 expected=load(root)
 if len(selected)!=2 or {x.get('destination')for x in selected}!=set(expected):raise ValueError('Expected exactly two global tank aliases')
 for row in selected:
  if type(row.get('identity'))is not int or type(row.get('density'))is not int or row!=expected[row['destination']]:raise ValueError('Changed finite alias metadata')
