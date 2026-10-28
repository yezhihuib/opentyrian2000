#!/usr/bin/env python3
"""Six controlled actual-game boundary guards, not a rerun of historical97.

One derived build, E1 physical12 ticks356–358, internal8/output4. Only test-only
original map-pointer placement, identity selection, observation and post-borrow
corruption are injected. Production files, original data and shared objects stay
unchanged. These diagnostics do not claim natural state equality or sanitizer
coverage (the separately recorded direct-borrow probe supplies sanitizer proof).
"""
from pathlib import Path
import argparse, hashlib, json, os, shutil, signal, struct, subprocess, sys, threading, time

OLD_SHA='7cf0c6fc92d83c2aeb811a60098b492e984975a71840b58c220516f812fd2a27'
PEAK=128*1024**2
RESERVE=250*1024**2
MODES=('baseline-pose1','baseline-pose2','baseline-pose3','final-bronze-rgba','cached-bronze-rgba','cached-transfer-aircraft42')
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PACK_PINS={
 'terrain-shapesy-356-8.hda':(2020356,0,0,'cc19368ec441824fdb968c2e0da261894cf953528f48ddf7d3d0f98c65c39c42','f543cacf65a4898d7972aea568b7fee5226bd11357f1776a1edd86289dc57e7a'),
 'newshf-aircraft170/newshf-role2100040-8.hda':(2100040,6,7,'b0de03067a8f51baff70314762166428d7592c6b67f13147f42b88056353d830','4548608a4081c4aac0bbaf99a4eaf7758e579154821948d482990abe1aeb1434'),
 'newshf-aircraft170/newshf-role2100041-8.hda':(2100041,6,7,'adf2a88e69f22b96a5e23687dcbfdf3361903c0962a29b5f2549c88fe2a244ba','7458e7f9fb448472e6c21dc70ce1fb2fa483d075015ec4759c6a2485664666e9'),
 'newshf-aircraft170/newshf-role2100042-8.hda':(2100042,6,7,'16e52e0a3f6b1dd09907edd6a01910842861795a76b0121fec2732ecc9652319','bd839b411420e0773ade7af280af7eb4a94dce90883aba5f630162231a39646a'),
}

def verify_guard_pack(pack):
 for name,(role,ax,ay,file_sha,payload_sha) in PACK_PINS.items():
  b=(pack/name).read_bytes();assert len(b)==172060
  assert struct.unpack('<4s6I',b[:28])==(b'HDR1',role,8,24,28,ax,ay)
  assert hashlib.sha256(b).hexdigest()==file_sha
  assert hashlib.sha256(b[28:]).hexdigest()==payload_sha
  if role==2020356:assert all(a==255 for a in b[31::4])
 print('GUARD_PACK_VERIFIED role2020356 and170 phases40,41,42 exact header/file/payload SHA',flush=True)

def replace(s,old,new,count=1):
 assert s.count(old)==count,(old,s.count(old),count)
 return s.replace(old,new)

BRONZE_HELPERS=r'''
/* Test-only one-pointer placement, restored before the next controlled frame. */
static Uint8 **diagnostic_bronze_cell;
static Uint8 *diagnostic_bronze_original;
static void diagnostic_bronze_place(const void *first,int x,int y)
{
 memset(diagnostic_bronze_mask,0,sizeof(diagnostic_bronze_mask));
 memset(diagnostic_bronze_actor,0,sizeof(diagnostic_bronze_actor));
 if(diagnostic_bronze_cell){*diagnostic_bronze_cell=diagnostic_bronze_original;diagnostic_bronze_cell=NULL;shapesy_world_reset();}
 if(!getenv("CYAN_CONTROLLED_CHAIN")||game_probe_tick<DIAGNOSTIC_START||game_probe_tick>DIAGNOSTIC_END)return;
 Uint8 *source=NULL;for(unsigned i=0;i<72;i++)if(shapesy_registry.ids[i]==356){source=megaData1.shapes[i].sh;break;}
 diagnostic_assert(source&&shapesy_bronze356_sources_valid(),"original356 source binding before controlled placement");
 unsigned best=0,br=0,bt=0;
 for(unsigned r=0;r<8;r++)for(unsigned t=0;t<12;t++){
  unsigned score=0;
  for(unsigned iy=0;iy<28;iy++)for(unsigned ix=0;ix<24;ix++){
   int gx=x+t*24+ix,gy=y+r*28+iy;if(gx<0||gx>=320||gy<0||gy>=184)continue;
   for(unsigned a=0;a<100;a++)if(enemyAvail[a]==0&&enemy[a].enemytype==170){
    int ex=newshf_validation_slots[a].x,ey=enemy[a].ey;
    if(gx>=ex-6&&gx<ex+18&&gy>=ey-7&&gy<ey+21){++score;break;}
   }
  }
  if(score>best){best=score;br=r;bt=t;}
 }
 if(!best)return;
 diagnostic_bronze_cell=((Uint8 **)first)+br*14+bt;diagnostic_bronze_original=*diagnostic_bronze_cell;*diagnostic_bronze_cell=source;
 /* Rebuild only the controlled map's world witness before the real new pass;
  * source/resource bindings and later frame/borrow/cache checks stay intact. */
 shapesy_world_reset();
 fprintf(stderr,"CONTROLLED_BRONZE_PLACEMENT tick=%u row=%u tile=%u id=356 actor_cells=%u\n",game_probe_tick,br,bt,best);
}
/* Called only after actual id356 mirrored admission; never manufacture owners. */
static void diagnostic_bronze_mark(int x,int y,const Uint8 *rgba)
{
 if(game_probe_tick<DIAGNOSTIC_START||game_probe_tick>DIAGNOSTIC_END)return;
 for(unsigned iy=0;iy<224;iy++)for(unsigned ix=0;ix<192;ix++){
  int gx=x*8+ix,gy=y*8+iy;if(gx<0||gx>=canvas->w||gy<0||gy>=canvas->h)continue;
  size_t n=(size_t)gy*canvas->w+gx;const Uint8 *p=rgba+4*(iy*192+ix);
  Uint32 want=0xff000000u|(Uint32)p[0]<<16|(Uint32)p[1]<<8|p[2];
  diagnostic_assert(p[3]==255&&hd_owner[n]&&*((Uint32 *)((Uint8 *)canvas->pixels+gy*canvas->pitch)+gx)==want,"admitted356 exact opaque authored pixel");
  diagnostic_bronze_mask[n]=1;
 }
}
/* Select one real draw position analytically, without changing art or owners.
 * The previous169 same-origin fixture missed the clipped170 chain at tick356.
 * Match an actual170-owned chain pixel to an original-native Talon soft pixel;
 * the subsequent real draw/blit must still prove the ownership was copied. */
static void diagnostic_transfer_position(unsigned slot,int *x,int *y)
{
 diagnostic_assert(global_talon_family_ready(),"actual Talon family before controlled placement");
 Uint8 source[672]={0},mask[672]={0};const unsigned parts[4]={0,1,19,20};
 for(unsigned q=0;q<4;q++)diagnostic_assert(decode_tile(spriteSheet9,233+parts[q],source,mask,24,(q%2)*12,(q/2)*14),"original Talon mask for placement");
 const Uint8 *rgba=global_talon_rgba[global_talon_poses[0].visual];
 for(size_t n=0;n<global_newshf_capacity;n++){
  if(!global_newshf_owner[n]||diagnostic_actor_slot[n]!=slot+1||!diagnostic_chain_mask[n])continue;
  int gx=n%canvas->w,gy=n/canvas->w;
  for(unsigned ay=(unsigned)gy%8;ay<224;ay+=8)for(unsigned ax=(unsigned)gx%8;ax<192;ax+=8){
   if(!mask[(ay/8)*24+ax/8]||rgba[4*(ay*192+ax)+3]>=255)continue;
   int tx=(gx-(int)ax)/8,ty=(gy-(int)ay)/8;
   if(tx<0||tx>296||ty<-27||ty>=200)continue;
   *x=tx;*y=ty;
   fprintf(stderr,"CONTROLLED_TALON_CHAIN_POSITION slot=%u target=%d,%d local=%u,%u origin=%d,%d\n",slot,gx,gy,ax,ay,tx,ty);return;
  }
 }
 diagnostic_assert(false,"actual owned356cyan170 pixel matches original Talon soft pixel");
}
'''

def adapt(old):
 """Hash-bound finite adaptation; historical driver and common assertions stay intact."""
 assert hashlib.sha256(old.encode()).hexdigest()==OLD_SHA
 s=replace(old,'169','170',20)
 s=replace(s,'profile==20','profile==21',6)
 s=replace(s,'phase>=37&&phase<=39','phase>=40&&phase<=42',2)
 s=replace(s,"'aircraft37','aircraft38','aircraft39'","'aircraft40','aircraft41','aircraft42'")
 s=replace(s,'(37,38,39)','(40,41,42)')
 s=replace(s,'shapesy_resources.members[0].rgba[0]^=1;','diagnostic_assert(shapesy_bronze356.used&&shapesy_borrow_check(cyan_layer1_dependency),"actual356 provider valid before recursive corruption");shapesy_bronze356.member.rgba[0]^=1;')
 s=replace(s,'!strcmp(which,"layer1-rgba")','!strcmp(which,"bronze-rgba")')
 s=replace(s,'static Uint8 diagnostic_chain_mask[320u*200u*8u*8u];\\n',
  'static Uint8 diagnostic_bronze_mask[320u*200u*8u*8u];\\nstatic unsigned diagnostic_bronze_actor[100];\\nstatic void diagnostic_bronze_place(const void *,int,int);\\nstatic void diagnostic_bronze_mark(int,int,const Uint8 *);\\nstatic void diagnostic_assert(bool,const char *);\\nstatic Uint8 diagnostic_chain_mask[320u*200u*8u*8u];\\n')
 needle=" (stage/'src/shapesy_cyan_layer2_mirror.inc').write_text(cyan)"
 injection='''
 bronze=(ROOT/'src/shapesy_platform_mirror.inc').read_text()
 bronze=bounded_replace(bronze,'void render_mirror_shapesy_layer1(SDL_Surface *surface,const void *first,int x,int y)\\n{','void render_mirror_shapesy_layer1(SDL_Surface *surface,const void *first,int x,int y)\\n{\\n diagnostic_bronze_place(first,x,y);')
 bronze=bounded_replace(bronze,'if(id==356)shapesy_bronze356.used=true;else shapesy_platform_used=true;','if(id==356){shapesy_bronze356.used=true;diagnostic_bronze_mark(x+(int)tile*24,y,a->rgba);}else shapesy_platform_used=true;')
 (stage/'src/shapesy_platform_mirror.inc').write_text(bronze)
'''
 s=replace(s,needle,needle+injection)
 s=replace(s,'  a.pack=pack',"""  bronze=sorted((ROOT/'assets/hd/current-compat/shapesy-bronze356').glob('*.hda'));assert len(bronze)==1
  bronze_target=pack/bronze[0].name
  if bronze_target.exists():assert SHA(bronze_target)==SHA(bronze[0])
  else:bronze_target.symlink_to(bronze[0].resolve())
  assert (pack/'terrain-shapesy-356-8.hda').is_file()
  verify_guard_pack(pack)
  a.pack=pack""")
 s=replace(s,'if(shapesy_borrow_sample(serial,n,color))','if(diagnostic_bronze_mask[n]&&shapesy_borrow_sample(serial,n,color))',2)
 s=replace(s,'diagnostic_assert(cyan_borrow_check(global_newshf_cyan_dependency),"genuine sealed cyan source before mutation");',
  'diagnostic_assert(cyan_borrow_check(global_newshf_cyan_dependency),"genuine sealed cyan source before mutation");\n  diagnostic_assert(shapesy_bronze356.used&&cyan_layer1_dependency&&shapesy_borrow_check(cyan_layer1_dependency)&&diagnostic_chain_pixels>0,"actual356 secondary cyan170 recursive intersection");\n  diagnostic_assert((global_newshf_used_resources&UINT64_C(0x70000000000))==UINT64_C(0x70000000000),"all40to42 resource bits retained");')
 s=replace(s,'if(n<sizeof(diagnostic_chain_mask)&&diagnostic_chain_mask[n])++diagnostic_chain_pixels;',
  'if(n<sizeof(diagnostic_chain_mask)&&diagnostic_chain_mask[n]){++diagnostic_chain_pixels;if(slot<100)++diagnostic_bronze_actor[slot];}')
 s=replace(s,'global_newshf_cyan_pixels[slot])break;','global_newshf_cyan_pixels[slot]&&diagnostic_bronze_actor[slot])break;')
 s=replace(s,'prior[i]&&diagnostic_actor_slot[i]==slot+1&&global_talon_owner[i]',
  'prior[i]&&diagnostic_actor_slot[i]==slot+1&&diagnostic_chain_mask[i]&&global_talon_owner[i]')
 s=replace(s,' global_talon_pose(1,spriteSheet9,233,233,0);',
  ' global_talon_pose(1,spriteSheet9,233,233,0);diagnostic_transfer_position(slot,&x,&y);')
 s=replace(s,'diagnostic_assert(copied>0,"actual copied ownership");',
  'diagnostic_assert(copied>0,"actual copied ownership");\n fprintf(stderr,"ACTUAL170_TALON_TRANSFER slot=%u pose=%u copied=%u mask=%llx\\n",slot,newshf_validation_slots[slot].pose,copied,(unsigned long long)global_newshf_used_resources);')
 s=replace(s," def tree_inputs(root):", " modes=list(APPROVED_MODES)\n def tree_inputs(root):")
 s=replace(s,"'AIRCRAFT170_CONTROLLED_POSE':str(a.pose)","'AIRCRAFT170_CONTROLLED_POSE':str(int(mode[-1]) if mode.startswith('baseline-pose') else 1)")
 s=replace(s,"result.append(run('baseline'))","result.append(run(modes[0]))")
 # Native per-case stdout/stderr and original argv are still captured by old code.
 return s

def inventory(root):
 return {str(p):SHA(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('source-root','native-build','pack','original-data','sysroot','primary-freeze','out'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});r=a.source_root;q=a.out
 assert not q.exists();free=shutil.disk_usage(q.parent).free;assert free>=PEAK+RESERVE,(free,PEAK+RESERVE)
 old=r/'tests/aircraft169_aircraft_diagnostics.py';producer=Path(__file__).resolve();test=producer.with_name('test_shared170_bronze356_game_guards.py')
 source=inventory(r/'src');objects=inventory(a.native_build/'obj');data=inventory(a.original_data);assets=inventory(a.pack)
 consumed=json.loads(a.primary_freeze.read_text());closure={}
 for group in ('source_sha256','native_test_sha256','script_snapshot_sha256','asset_sha256'):
  for name,h in consumed[group].items():
   f=Path(name);f=f if f.is_absolute() else r/f;assert SHA(f)==h;closure[str(f)]=h
 index=Path(subprocess.check_output(['git','-C',str(r),'rev-parse','--git-path','index'],text=True).strip());index_before=SHA(index)
 text=adapt(old.read_text());ns={'__name__':'bound_six_guard_adapter','__file__':str(producer),'bounded_replace':replace,'APPROVED_MODES':MODES,'verify_guard_pack':verify_guard_pack}
 exec(compile(text,str(old)+' [finite170356 adaptation]','exec'),ns)
 ns['ROOT']=r
 ns['CONTROLLED']=BRONZE_HELPERS+ns['CONTROLLED']
 # No inherited actor/pose-only or diagnostic control is allowed to weaken a case.
 removed={k:os.environ.pop(k) for k in list(os.environ) if k.startswith(('AIRCRAFT169_','AIRCRAFT170_')) or k in ('CYAN_CONTROLLED_CHAIN','CYAN_AIRCRAFT_DIAGNOSTIC')}
 argv=[str(producer),'--original-data',str(a.original_data),'--sysroot',str(a.sysroot),'--native-build',str(a.native_build),'--pack',str(a.pack),'--out',str(q),'--density','8','--start','356','--end','358','--episode','1','--level','12','--controlled-actor','--controlled-chain','--jobs','1']
 binding=dict(status='RUNNING',scope=__doc__,approved_modes=MODES,source_sha256=source,objects_sha256=objects,data_sha256=data,pack_target_sha256=assets,primary_closure_sha256=closure,producer_sha256={str(producer):SHA(producer),str(test):SHA(test),str(old):SHA(old)},adapted_program_sha256=hashlib.sha256(text.encode()).hexdigest(),bronze_helpers_sha256=hashlib.sha256(BRONZE_HELPERS.encode()).hexdigest(),index_before_sha256=index_before,original_driver_sha256=OLD_SHA,argv=argv,removed_parent_control_environment=removed,peak_budget_bytes=PEAK,reserve_bytes=RESERVE,free_before=free,sanitizer_claim=False)
 freeze=q.with_name(q.name+'-input-freeze.json');freeze.write_text(json.dumps(binding,indent=2)+'\n')
 # Dedicated process group makes the floor monitor capable of stopping its own
 # compiler/game descendants without touching other agents' processes.
 if os.getpgrp()!=os.getpid():os.setsid()
 assert os.getpgrp()==os.getpid()
 stop=threading.Event();samples=[];violations=[]
 def monitor():
  while not stop.is_set():
   available=shutil.disk_usage(q.parent).free;samples.append([time.time(),available])
   if available<RESERVE:
    violations.append(available);freeze.with_name(q.name+'-budget-abort.json').write_text(json.dumps({'free':available,'reserve':RESERVE})+'\n');os.killpg(os.getpgrp(),signal.SIGTERM)
   stop.wait(0.5)
 thread=threading.Thread(target=monitor,daemon=True);thread.start();start=time.monotonic();code=1;error=None
 try:
  sys.argv=argv;ns['main']();code=0
 except SystemExit as e:code=int(e.code or 0)
 except BaseException as e:error=repr(e)
 finally:
  stop.set();thread.join()
  for k,v in removed.items():os.environ[k]=v
 checks=dict(source_unchanged=source==inventory(r/'src'),objects_unchanged=objects==inventory(a.native_build/'obj'),data_unchanged=data==inventory(a.original_data),pack_unchanged=assets==inventory(a.pack),primary_closure_unchanged=all(SHA(Path(n))==h for n,h in closure.items()),producer_unchanged=all(SHA(Path(n))==h for n,h in binding['producer_sha256'].items()),index_unchanged=SHA(index)==index_before)
 allocated=sum(f.lstat().st_blocks*512 for f in q.rglob('*')) if q.exists() else 0
 receipt=json.loads((q/'receipt.json').read_text()) if (q/'receipt.json').exists() else {}
 passed=code==0 and not error and not violations and all(checks.values()) and receipt.get('status')=='PASS' and len(receipt.get('results',[]))==6 and allocated<=PEAK
 binding.update(status='PASS' if passed else 'FAIL',exit_code=code,error=error,checks=checks,seconds=time.monotonic()-start,allocated_bytes=allocated,free_after=shutil.disk_usage(q.parent).free,minimum_sampled_free=min(v for _,v in samples),free_samples=samples,native_receipt_sha256=SHA(q/'receipt.json') if receipt else None,original97_rerun=False)
 q.mkdir(exist_ok=True);(q/'six-guard-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
 print(json.dumps({k:binding[k] for k in ('status','exit_code','error','checks','seconds','allocated_bytes','minimum_sampled_free','free_after')},indent=2));raise SystemExit(not passed)

if __name__=='__main__':main()
