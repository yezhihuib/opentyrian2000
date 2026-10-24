#!/usr/bin/env python3
"""Paired actual-call diagnostic; temporary instrumented copies, no gameplay/FPS claim.
Domains: emitter-bank, enemy-record, weapon-record, shot-bank, RGBA, palette.
Uses the unchanged native P09 driver's verified original input and object reuse.
"""
import argparse, hashlib, json, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import portable_history_baselines as history
BASE='5109ebbd3f8a5c58075d6358e82e2e4459ac5460'
def sha(b): return hashlib.sha256(b).hexdigest()
def replace_once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b)
def prepare(dest,baseline):
 dest.mkdir(parents=True,exist_ok=True)
 (dest/'src').mkdir(exist_ok=True);(dest/'tests').mkdir(exist_ok=True)
 sources={}
 for p in (ROOT/'src').iterdir():
  if p.is_file():
   b=history.preimage(BASE, 'src/'+p.name, ROOT) if baseline else p.read_bytes()
   (dest/'src'/p.name).write_bytes(b);sources[p.name]=sha(b)
 for n in ('enemy_protron_reuse_validation.py','enemy_protron_reuse_validation.c','enemy_green_reuse_validation.c','enemy_reuse_validation.c','enemy_proof_dedup_diagnostics.inc'):
  shutil.copyfile(ROOT/'tests'/n,dest/'tests'/n)
 if not (dest/'assets').exists():(dest/'assets').symlink_to(ROOT/'assets',target_is_directory=True)
 header='''#ifndef ENEMY_PROOF_DIAG_H
#define ENEMY_PROOF_DIAG_H
#include <stdint.h>
extern uint64_t diag_calls[6],diag_bytes[6],diag_proofs,diag_visits;
static inline void diag_add(unsigned d,uint64_t n){diag_calls[d]++;diag_bytes[d]+=n;}
static inline void diag_reset(void){for(unsigned i=0;i<6;i++)diag_calls[i]=diag_bytes[i]=0;diag_proofs=diag_visits=0;}
#endif
'''
 (dest/'src/proof_diagnostic.h').write_text(header)
 p=dest/'src/enemy_reuse_identity.c';s=p.read_text();s='#include "proof_diagnostic.h"\nuint64_t diag_calls[6],diag_bytes[6],diag_proofs,diag_visits;\n'+s
 s=replace_once(s,'stamp(const unsigned char *b,unsigned n)','stamp(const unsigned char *b,unsigned n,unsigned domain)')
 s=replace_once(s,'{uint64_t v=UINT64_C(0xcbf29ce484222325);','{diag_add(domain,n);uint64_t v=UINT64_C(0xcbf29ce484222325);')
 assert s.count('stamp(b,n)')==2;s=s.replace('stamp(b,n)','stamp(b,n,2)',1).replace('stamp(b,n)','stamp(b,n,1)',1)
 s=replace_once(s,'stamp(b->data,b->size)','stamp(b->data,b->size,0)');p.write_text(s)
 p=dest/'src/enemy_reuse_mirror.inc';s=p.read_text();s='#include "proof_diagnostic.h"\n'+s
 s=replace_once(s,'enemy_reuse_hash(const void *data,size_t size)','enemy_reuse_hash(const void *data,size_t size,unsigned domain)')
 s=replace_once(s,'{const Uint8 *p=data;','{diag_add(domain,size);const Uint8 *p=data;')
 s=replace_once(s,'enemy_reuse_hash(bank.data,bank.size)','enemy_reuse_hash(bank.data,bank.size,3)')
 s=replace_once(s,'enemy_reuse_hash(rgba,bytes)','enemy_reuse_hash(rgba,bytes,4)')
 s=replace_once(s,'enemy_reuse_hash(a->rgba,12u*14u*8u*8u*4u)','enemy_reuse_hash(a->rgba,12u*14u*8u*8u*4u,4)')
 s=replace_once(s,'static bool enemy_reuse_scope(void)\n{','static bool enemy_reuse_scope(void)\n{\n diag_add(5,768);')
 s=replace_once(s,'static bool enemy_reuse_proof(void)\n{','static bool enemy_reuse_proof(void)\n{\n diag_proofs++;')
 s=replace_once(s,'if(enemy_reuse_frame.used[i]&&','if(enemy_reuse_frame.used[i]&&(diag_visits++,true)&&');p.write_text(s)
 p=dest/'tests/enemy_protron_reuse_validation.c';s=p.read_text();insert='\n#define DIAG_MULTIPLIER '+('2' if baseline else '1')+'\n'
 if baseline:insert+='static bool enemy_reuse_identity_live_generation(unsigned s,unsigned i,int x,int y,uint64_t expected){uint64_t g=enemy_reuse_identity_generation(s);return g&&g==expected&&enemy_reuse_identity_live(s,i,x,y);}\n'
 insert+='#include "enemy_proof_dedup_diagnostics.inc"\n'
 s=replace_once(s,'int main(int argc,char **argv)',insert+'int main(int argc,char **argv)')
 start=s.index(' p09_positive();p09_negatives();');end=s.index(' printf("PASS native P09',start)
 s=s[:start]+' diag_tests();\n'+s[end:]
 s=replace_once(s,'PASS native P09 + unchanged P05 matrix:','PASS targeted proof diagnostics (not full P09/P05 matrix):');p.write_text(s)
 p=dest/'tests/enemy_protron_reuse_validation.py';s=p.read_text();s=replace_once(s,'Native JE_drawEnemy with controlled firing timers; exact extracted native projectile/explosion update loops; real player shot creation/movement; not gameplay acceptance','Targeted proof diagnostics using native P09 fixture and exact native shot update loop; not the full P09/P05 matrix or gameplay acceptance');p.write_text(s)
 return sources

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ('original-data','sysroot','base-build','assets','out'):p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=True)
 result={'baseline_commit':BASE,'domains':['emitter-bank','enemy-record','weapon-record','shot-bank','RGBA','palette'],'runs':{}}
 for name,baseline in [('baseline',True),('candidate',False)]:
  dest=a.out/(name+'-source');sources=prepare(dest,baseline);out=a.out/name
  instrumented={str(p.relative_to(dest)):sha(p.read_bytes()) for d in ('src','tests') for p in (dest/d).iterdir() if p.is_file()}
  (a.out/(name+'-unmodified-source-pins.json')).write_text(json.dumps(sources,indent=2)+'\n')
  cmd=[sys.executable,str(dest/'tests/enemy_protron_reuse_validation.py')]
  for key in ('original_data','sysroot','base_build','assets'):cmd+=['--'+key.replace('_','-'),str(getattr(a,key).resolve())]
  cmd+=['--out',str(out)]
  with (a.out/(name+'.log')).open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
  counts=[]
  if (out/'harness.log').exists():
   counts=[json.loads(l[7:]) for l in (out/'harness.log').read_text().splitlines() if l.startswith('COUNTS ')]
  stable=all(sha((dest/p).read_bytes())==digest for p,digest in instrumented.items())
  result['runs'][name]={'returncode':r.returncode,'source_sha256':sources,'instrumented_source_sha256':instrumented,'instrumented_source_stable':stable,'counts':counts}
  assert stable, 'Diagnostic source changed during compile/execution'
  (a.out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
  print(name,r.returncode,flush=True)
  if r.returncode:raise SystemExit(r.returncode)
 old=result['runs']['baseline']['counts'];new=result['runs']['candidate']['counts'];assert len(old)==len(new)==14
 for b,c in zip(old,new):
  assert (b['case'],b['profile'],b['proof_calls'],b['used_slots'])==(c['case'],c['profile'],c['proof_calls'],c['used_slots'])
  if b['case'] in ('proof','repeat-proof'):
   for d in range(3):assert b['domains'][d]=={k:2*v for k,v in c['domains'][d].items()}
   assert b['domains'][3:]==c['domains'][3:]
  else:assert b==c
 result['status']='PASS';(a.out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS paired exact calls/bytes; no FPS inference')
if __name__=='__main__':main()
