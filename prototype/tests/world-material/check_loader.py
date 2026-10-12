#!/usr/bin/env python3
"""Two-part optional-loader tests. Synthetic by default; no game or captures."""
from pathlib import Path
import argparse,hashlib,json,struct,subprocess
p=argparse.ArgumentParser();p.add_argument('--validator',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
approved=p.add_mutually_exclusive_group();approved.add_argument('--approved-bundle',type=Path);approved.add_argument('--approved-pack',type=Path);p.add_argument('--rejected-bundle',type=Path)
a=p.parse_args();a.validator=a.validator.resolve();root=a.output.resolve();root.mkdir(parents=True,exist_ok=False)
CUT=8388608;SECOND=7998204;NAMES=('ground101-world-material.g101.0','ground101-world-material.g101.1')
fixture=root/'synthetic.g101';subprocess.run([str(a.validator),'--synthetic-bundle',str(fixture)],check=True)
blob=fixture.read_bytes();fixture.unlink();assert len(blob)==CUT+SECOND
shared=root/'mutated-input';shared.mkdir();receipt={}
def run(name,parts,expected=False,alloc=0,directory=None,legacy=None):
 out=root/name;out.mkdir()
 for file in list(shared.iterdir()):file.unlink()
 if parts is not None:
  for name0,data in zip(NAMES,parts):
   if data is not None:(shared/name0).write_bytes(data)
 if legacy is not None:(shared/'ground101-world-material.g101').write_bytes(legacy)
 result=subprocess.run([str(a.validator),str(shared) if directory is None else directory,str(int(expected)),str(alloc)],cwd=out,capture_output=True,text=True)
 assert result.returncode==0,(name,result.stdout,result.stderr);assert not list(out.glob('ground101*.tsv'))
 receipt[name]={'exit':result.returncode,'expected_enabled':expected,'expected_payload_allocations':alloc,'stdout':result.stdout,'stderr':result.stderr,'part_sizes':[len(x) if x is not None else None for x in parts] if parts is not None else None,'part_sha256':[hashlib.sha256(x).hexdigest() if x is not None else None for x in parts] if parts is not None else None,'no_default_trace_files':True}
def split(data):assert len(data)==CUT+SECOND;return data[:CUT],data[CUT:]
def flip(data,offset):return data[:offset]+bytes([data[offset]^1])+data[offset+1:]
p0,p1=split(blob)
run('missing-both',None);run('missing-part0',(None,p1));run('missing-part1',(p0,None))
run('empty-directory',None,directory='');run('overlong-path',None,directory='a'*1100)
run('legacy-single-file-ignored',None,legacy=blob)
run('truncated-part0-header',(p0[:8],p1));run('truncated-part0',(p0[:-1],p1));run('truncated-part1',(p0,p1[:-1]));run('truncated-both',(p0[:-1],p1[:-1]))
run('trailing-part0',(p0+b'\0',p1));run('trailing-part1',(p0,p1+b'\0'));run('trailing-both',(p0+b'\0',p1+b'\0'));run('swapped-parts',(p1,p0))
run('bad-magic',(b'X'+p0[1:],p1))
for name,offset,value in [('version',8,2),('count',12,62),('huge-count',12,0xffffffff),('width',16,767),('height',20,895),('density',24,4),('size-header',28,16386047),('huge-size-header',28,0xffffffff),('role',32,999),('footer-flag',40,1)]:
 run('bad-'+name,(p0[:offset]+struct.pack('<I',value)+p0[offset+4:],p1))
run('duplicate-inventory',(p0[:44]+p0[32:44]+p0[56:],p1))
run('synthetic-checksum-rejected',(p0,p1),alloc=1)
if a.rejected_bundle:run('unapproved-bundle-rejected',split(a.rejected_bundle.read_bytes()),alloc=1)
if a.approved_bundle or a.approved_pack:
 if a.approved_pack:
  q0=(a.approved_pack/NAMES[0]).read_bytes();q1=(a.approved_pack/NAMES[1]).read_bytes()
  assert len(q0)==CUT and len(q1)==SECOND,'approved pack part lengths are not exact'
  approved=q0+q1
 else:approved=a.approved_bundle.read_bytes();q0,q1=split(approved)
 assert q0+q1==approved
 run('valid-approved-reconstruction',(q0,q1),True,1)
 run('approved-corrupt-part0',(flip(q0,764),q1),alloc=1)
 run('approved-corrupt-part1',(q0,flip(q1,0)),alloc=1)
 run('approved-corrupt-both',(flip(q0,764),flip(q1,0)),alloc=1)
 run('mixed-approved0-synthetic1',(q0,p1),alloc=1)
 run('mixed-synthetic0-approved1',(p0,q1),alloc=1)
 # Sidecar replacement cannot make an incomplete pack partially active.
 run('approved-missing-part0',(None,q1));run('approved-missing-part1',(q0,None))
 receipt['reconstruction']={'full_bytes':len(approved),'full_sha256':hashlib.sha256(approved).hexdigest(),'parts':[{'file':NAMES[0],'offset':0,'bytes':len(q0),'sha256':hashlib.sha256(q0).hexdigest()},{'file':NAMES[1],'offset':CUT,'bytes':len(q1),'sha256':hashlib.sha256(q1).hexdigest()}],'byte_identical':True}
for file in shared.iterdir():file.unlink()
(root/'loader-checks.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(receipt)-int('reconstruction'in receipt),'split-loader cases; exact two-part lengths, bounded allocation, full-stream identity, coherent fallback and no default traces')
