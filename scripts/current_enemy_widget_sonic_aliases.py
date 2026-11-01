"""Finite byte-identical global aliases; no image conversion or new material."""
from pathlib import Path,PurePosixPath
import hashlib,struct
SPECS = {20: '328f9831389399fa7c8d623889732bbc1574dac458a30b97511e2d031dd7aed8', 21: 'a8fbcb2952ec4a4b3f84388f1b410ec70648052cbaff35487d2ed930c9b5dc55', 105: 'd12fde24b67f6b57ede3483e07a155b95cd5f538cf9f96c64e0d80fc2e0eba78', 106: '1a47b5701ecbdef673251cd1de7b975e42291cef29ab9a0bfd10f1c48facb2ba', 124: 'b37e9664609365b53a250c0a711b6ae863ab55299904794051091b206aeef158', 125: '11ffdf82296ed985ec9534ba19a555eb22594c14e5fc92414531a47e36383752'}
REVISION='canonical-enemy-widget-sonic-aliases-v1'
ENCODING='rgba-straight-alpha-v1'
PREFIX='assets/hd/global-assets-v1/content/'
def canonical_source(index):
 return 'assets/hd/current-compat/'+('guided'if index in (20,21)else'sonic')+'/bullet-%d-8.hda'%index
def read_regular(root,name):
 p=PurePosixPath(name)
 if p.is_absolute()or '..'in p.parts or '\\'in name:raise ValueError('Unsafe finite alias source')
 q=Path(root)/name
 if any(x.is_symlink()for x in (q,*q.parents))or not q.is_file():raise ValueError('Missing/nonregular finite alias input')
 return q.read_bytes()
def git_blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def generate(root):
 result={}
 for i,pin in SPECS.items():
  raw=read_regular(root,canonical_source(i))
  if len(raw)!=43036 or hashlib.sha256(raw).hexdigest()!=pin or struct.unpack('<4s6I',raw[:28])!=(b'HDR1',80000+i,8,12,14,0,0):raise ValueError('Canonical alias source changed')
  result[PREFIX+pin+'.hda']=raw
 return result
def rows_for(root):
 blobs=generate(root);rows=[]
 for i,pin in SPECS.items():
  source=PREFIX+pin+'.hda';raw=blobs[source]
  rows.append(dict(source_path=source,destination='assets/global/content/'+pin+'.hda',group='global-source-identity',revision=REVISION,identity=80000+i,density=8,encoding=ENCODING,canonical_source=canonical_source(i),bytes=len(raw),sha256=pin,git_blob=git_blob(raw)))
 return sorted(rows,key=lambda x:x['destination'])
def load(root):
 expected=generate(root)
 for name,raw in expected.items():
  if read_regular(root,name)!=raw:raise ValueError('Global alias differs from canonical bytes')
 return {row['destination']:row for row in rows_for(root)}
def validate_runtime_rows(root,manifest,required=False):
 rows=manifest.get('files')
 if not isinstance(rows,list):raise ValueError('Expected finite runtime rows')
 identities={80000+i for i in SPECS};sources={PREFIX+s+'.hda'for s in SPECS.values()};destinations={'assets/global/content/'+s+'.hda'for s in SPECS.values()};selected=[]
 # Existing manual consumers stay exactly as they were; no relaxed guided/sonic
 # rules and no second player gate. Any other occurrence of these exact material
 # identities, including a hidden HDR1 header without metadata, is a collision.
 manual={canonical_source(i):('assets/gameplay/bullet-%d-8.hda'%i,pin)for i,pin in SPECS.items()}
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
 if len(selected)!=6 or {x.get('destination')for x in selected}!=set(expected):raise ValueError('Expected exactly six global canonical aliases')
 for row in selected:
  if type(row.get('identity'))is not int or type(row.get('density'))is not int or row!=expected[row['destination']]:raise ValueError('Changed finite alias metadata')
