#!/usr/bin/env python3
"""Finite source-boundary proof, no game execution or repository mutation."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TREE='2a60deb74b1a677e3d3cd6c5ea0c251e8ac54028'
PUBLIC_COMMIT='06a935e9b6995b4d11e96e6e6d8385325c85f1e5'
CHRISTMAS_ADDITION=''' /* These nine enemy IDs use different Christmas originals. Decline before
  * even a warm normal-art cache; byte-identical shell146/147 stay eligible. */
 if(xmas&&bank.data==spriteSheet8.data&&
    (enemy_energy_slot(index)>=0||index==112||index==113))return false;
'''
NIGHT_PINS={
 'src/render_mirror.c':'7bcd99a433733794e3f384f3b485b60219a251adfad7bf1f7412f29abf5687e2',
 'src/render_mirror.h':'ffff0a989ec27ec710426dba1ae0ebaf0d8c027aca77721c5813aae7b86cd6fe',
 'src/tyrian2.c':'33ad04c16c53861a956608f91dd2edd0c25d1d63e4921f1266abdba5f054ba48',
}
sha=lambda b:hashlib.sha256(b).hexdigest()
def fn(s,n):
 m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+n+r'\([^;{}]*\)\s*\{',s,re.M);assert m,n
 e=s.index('{',m.start())+1;d=1
 while d:d+=(s[e]=='{')-(s[e]=='}');e+=1
 return s[m.start():e]+'\n'

def verify_source(root=ROOT):
 root=Path(root).resolve()
 def git(*args):return subprocess.check_output(['git','-C',str(root),*args])
 assert git('cat-file','-t',TREE).decode().strip()=='tree'
 names=git('ls-tree','-r','--name-only',TREE,'--','src').decode().splitlines()
 assert {str(path.relative_to(root)) for path in (root/'src').rglob('*') if path.is_file()}==set(names),'Unexpected production inventory'
 old={n:git('show',TREE+':'+n) for n in names}
 new={n:(root/n).read_bytes() for n in names}
 changed=[n for n in names if new[n]!=old[n]]
 assert changed==['src/render_mirror.c','src/render_mirror.h','src/tyrian2.c'],changed
 combined=new['src/render_mirror.c'].decode();b=old['src/render_mirror.c'].decode()
 assert combined.count(CHRISTMAS_ADDITION)==1,'Exact Christmas guard missing or duplicated'
 r=combined.replace(CHRISTMAS_ADDITION,'',1)
 assert sha(r.encode())==NIGHT_PINS['src/render_mirror.c'],'Not the approved night renderer plus exact Christmas guard'
 for n in ['src/render_mirror.h','src/tyrian2.c']:
  assert sha(new[n])==NIGHT_PINS[n],'Not the approved night source: '+n
 assert fn(combined,'render_mirror_enemy_shot').replace(CHRISTMAS_ADDITION,'',1)==fn(b,'render_mirror_enemy_shot'),'Christmas hook inverse'

 added=['normal15_scope','normal15_palette','normal15_disjoint','normal15_layout','normal15_branch','normal15_index','normal15_channel','normal15_rgba','normal15_indices_match','normal15_compose']
 rest=r.replace(fn(r,'normal15_scope'),'')
 rest=rest.replace(fn(r,'manual_hd_scope'),fn(b,'manual_hd_scope'))
 start=rest.index('/* Palette5 identity in index order, R then G then B bytes; independent of')
 end=rest.index('void render_mirror_finish(',start)
 rest=rest[:start]+rest[end:]
 rest=rest.replace(fn(rest,'render_mirror_finish'),fn(b,'render_mirror_finish'))
 assert rest==b,'Unexpected renderer change outside finite scope'
 # Exact inverse strips only the display annotation/call changes. This proves
 # original indexed loops, event/difficulty/player/state logic byte-identical.
 t=new['src/tyrian2.c'].decode();bt=old['src/tyrian2.c'].decode();tr=t
 for line in [
  '\tMirrorOutputKind mirror_output = MIRROR_OUTPUT_UNSUPPORTED;\n',
  '\tint mirror_lightx = 0, mirror_lighty = 0;\n',
  '\t\t\tmirror_output = MIRROR_OUTPUT_NORMAL15_NIGHT;\n',
  '\t\t\tmirror_lightx = lightx;\n','\t\t\tmirror_lighty = lighty;\n',
  '\t\t\tif (starShowVGASpecialCode == 0) mirror_output = MIRROR_OUTPUT_ORDINARY;\n',
  '\t\t\telse if (starShowVGASpecialCode == 2 && processorType < 2) mirror_output = MIRROR_OUTPUT_NORMAL15_LOW_DETAIL;\n']:
  assert tr.count(line)==1,line;tr=tr.replace(line,'')
 tr=tr.replace('render_mirror_finish(mirror_output,mirror_lightx,mirror_lighty);','render_mirror_finish(starShowVGASpecialCode==0);').replace('render_mirror_finish(MIRROR_OUTPUT_UNSUPPORTED,0,0);','render_mirror_finish(false);')
 assert tr==bt,'Original indexed/gameplay code changed'
 header=new['src/render_mirror.h'].decode();oldheader=old['src/render_mirror.h'].decode()
 block=('/* The original indexed branch that actually ran, not the requested effect. */\n'
        'typedef enum {\n'
        ' MIRROR_OUTPUT_UNSUPPORTED, MIRROR_OUTPUT_ORDINARY,\n'
        ' MIRROR_OUTPUT_NORMAL15_NIGHT, MIRROR_OUTPUT_NORMAL15_LOW_DETAIL\n'
        '} MirrorOutputKind;\n')
 assert header.replace(block,'').replace('#define render_mirror_finish(kind,lightx,lighty) ((void)(kind),(void)(lightx),(void)(lighty))','#define render_mirror_finish(...) ((void)0)').replace('void render_mirror_finish(MirrorOutputKind kind,int lightx,int lighty);','void render_mirror_finish(bool ordinary_crop);')==oldheader
 crop=r'  int d=game_probe_density;\n  for\(int y=0;y<184\*d;y\+\+\) memcpy\([^\n]+;'
 assert re.search(crop,fn(r,'render_mirror_finish')).group()==re.search(crop,fn(b,'render_mirror_finish')).group()
 unchanged_names=re.findall(r'^(?:static\s+)?(?:bool|void|int|Uint32|unsigned int|Asset\s*\*)\s+(\w+)\([^;{}]*\)\s*\{',b,re.M)
 unchanged_names=[n for n in unchanged_names if n not in ['manual_hd_scope','render_mirror_finish']]
 for n in unchanged_names:assert fn(b,n)==fn(r,n),n
 assert not git('diff','--name-only',TREE,'--','assets').strip()
 result={'status':'PASS','public_baseline_commit':PUBLIC_COMMIT,'baseline_tree':TREE,'exact_approved_night_pins':NIGHT_PINS,'christmas_guard_exact':True,'combined_delta_inverse_exact':True,'production_files_checked':len(names),'changed_files':changed,'all_other_production_files_exact':True,'renderer_complete_inverse_exact':True,'tyrian2_complete_inverse_exact':True,'header_complete_inverse_exact':True,'original_indexed_loops_events_difficulty_player_updates_exact':True,'ordinary_crop_excerpt_exact':True,'unchanged_renderer_functions':unchanged_names,'new_functions':added,'source_sha256':{n:sha(v) for n,v in new.items()},'new_function_sha256':{n:sha(fn(r,n).encode()) for n in added},'game_runs':0,'publication':False}
 return result


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();result=verify_source()
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','unchanged_renderer_functions','new_function_sha256']},indent=2))

if __name__=='__main__':main()
