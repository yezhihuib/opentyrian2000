"""Extract actual renderer helpers and test the finite65536-region proposal.
No game, SDL runtime, capture or main/fixture source edit. Synthetic inputs only.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,tempfile
HERE=Path(__file__).resolve().parent
FUNCTIONS=['palette_rgb','complete_turret_group','restore_classic_rect','blend_rgba','cloud_shadow_rgba','cloud_asset','darken_rgba','decode_tile','read_asset','explosion_asset_slot','get_asset','talon_frame','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','draw_asset','render_mirror_entity','render_mirror_enemy_shot','upscale','render_mirror_begin','render_mirror_unsupported','render_mirror_pixel','render_mirror_entity_end']
PATTERNS=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'typedef struct \{ Asset \*asset; int x,y; \} GreenHead;',r'typedef struct \{ Uint16 peak\[16\]\[14\]; \} GreenBackground;',r'typedef struct \{ SDL_Rect rect; int bank,index,style; bool live; \} HdRegion;',r'static Asset assets\[\d+\];',r'static Asset talon_frames\[13\];']
CAPACITY='''/* Fixed presentation bookkeeping budget; gameplay pools are unchanged. */
#define HD_REGION_CAPACITY 65536
static HdRegion regions[HD_REGION_CAPACITY];'''
LEGACY_CAPACITY='static HdRegion regions[256];'
def capacity_sources(source):
 assert source.count(LEGACY_CAPACITY)+source.count(CAPACITY)==1,'expected exact legacy256 declaration or production65536 block'
 baseline=source.replace(CAPACITY,LEGACY_CAPACITY,1)
 assert 'HD_REGION_CAPACITY' not in baseline,'unexpected capacity macro or reference outside the exact production block'
 assert re.findall(r'\bstatic\s+HdRegion\s+regions\s*\[[^\]]*\]\s*;',baseline)==[LEGACY_CAPACITY],'expected exactly one legacy256 region declaration'
 candidate=baseline.replace(LEGACY_CAPACITY,CAPACITY,1)
 assert candidate.count(CAPACITY)==1 and candidate.count(LEGACY_CAPACITY)==0,'candidate must contain the exact production65536 block'
 assert candidate.replace(CAPACITY,LEGACY_CAPACITY,1)==baseline
 return baseline,candidate
def extract(s,n):
 m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+n+r'\([^\n;]*\)\s*\{',s,re.M);assert m,n
 start=s.index('{',m.start());end=start+1;depth=1
 while depth:depth+=(s[end]=='{')-(s[end]=='}');end+=1
 return s[m.start():end]+'\n'
def run(s,out,mode,sanitize=True):
 out.mkdir();definitions=[]
 for pat in PATTERNS:
  m=re.search(pat,s,re.S);assert m,pat;definitions.append(m.group())
 macro=re.search(r'^#define HD_REGION_CAPACITY \d+$',s,re.M)
 if macro:definitions.append(macro.group())
 definitions.append(re.search(r'static HdRegion regions\[(?:\d+|HD_REGION_CAPACITY)\];',s).group())
 (out/'production-types.inc').write_text('\n'.join(definitions));(out/'production-helpers.inc').write_text('\n'.join(extract(s,n) for n in FUNCTIONS))
 cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-I'+str(out),str(HERE/'test-hd-region-budget.c'),'-o',str(out/'test')]
 if sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 subprocess.run(cmd,check=True);r=subprocess.run([str(out/'test'),mode],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'),timeout=90)
 return r
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--report',type=Path);a=p.parse_args();source=(a.source/'src/render_mirror.c').read_text();s,candidate=capacity_sources(source)
assert 'static unsigned int region_count,local_entities,local_regions,local_blocks;' in s
assert 'memset(regions' not in s and 'malloc(sizeof(regions' not in s
work=Path(tempfile.mkdtemp(prefix='hd-region-budget-'))
results={}
for name,src,mode in [('old-composition',s,'composition'),('interim1024-composition',candidate.replace('HD_REGION_CAPACITY 65536','HD_REGION_CAPACITY 1024'),'composition'),('new-composition',candidate,'composition'),('new-stress',candidate,'stress')]:
 r=run(src,work/name,mode);print(name);print(r.stdout,end='');print(r.stderr,end='');r.check_returncode();results[name]=r.stdout
old=[x for x in results['old-composition'].splitlines() if x.startswith('composition ')];new=[x for x in results['new-composition'].splitlines() if x.startswith('composition ')];assert old==new,(old,new)
assert old==[x for x in results['interim1024-composition'].splitlines() if x.startswith('composition ')]
negative=[]
for name,src in [('off-by-one-guard',candidate.replace('region_count>=sizeof(regions)/sizeof(regions[0])','region_count>sizeof(regions)/sizeof(regions[0])')),('missing-region-reset',candidate.replace('region_count=local_entities=local_regions=local_blocks=0;','local_entities=local_regions=local_blocks=0;')),('missing-green-reset',candidate.replace('green_head_count=0;memset(green_first,0,(size_t)canvas->w*canvas->h*sizeof(*green_first));','green_head_count=0;')),('old-capacity',s)]:
 r=run(src,work/name,'stress');assert r.returncode!=0,(name,r.stdout);assert 'FAIL line' in r.stderr or 'runtime error' in r.stderr or 'AddressSanitizer' in r.stderr,(name,r.stderr);negative.append({'name':name,'returncode':r.returncode,'diagnostic':r.stderr[:1400]});print('KILLED',name)
report={'status':'passed','source_renderer_sha256':hashlib.sha256(source.encode()).hexdigest(),'source_capacity':65536 if CAPACITY in source else 256,'base_renderer_sha256':hashlib.sha256(s.encode()).hexdigest(),'candidate_renderer_sha256':hashlib.sha256(candidate.encode()).hexdigest(),'only_source_change':CAPACITY,'capacity':65536,'region_size':32,'static_bytes':2097152,'additional_bytes':2088960,'conservative_wrapper_call_bound':1122,'current_deduplicated_bound':822,'headroom_over_call_bound':64414,'unchanged_composition':old,'results':results,'negative_controls':negative,'sanitizers':'address,undefined','work':str(work),'game_runs':0,'captures':0};out=a.report or work/'result.json';out.write_text(json.dumps(report,indent=2)+'\n');print('Report',out)
