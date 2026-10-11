"""Independent test-only negative checks for the nine-entity renderer/wrapper.

Temporary extracted snippets alone are mutated. The authoritative full oracle
must pass first; these negatives reuse its retained payloads and assertions.
"""
from pathlib import Path
import argparse,json,os,resource,subprocess,tempfile,hashlib
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--work',required=True,type=Path)
p.add_argument('--report',type=Path,default=None)
a=p.parse_args();work=a.work
required=['types.inc','functions.inc','wrapper.inc','blitters.inc','test-installation9.c','test-installation9-wrapper.c','packs']
missing=[name for name in required if not (work/name).exists()]
if missing:p.error('full installation9 oracle must finish first; missing retained inputs: '+', '.join(missing))
mutations=[
 ('wrong-169-slot','renderer','functions.inc','base==169?303:','base==169?302:'),
 ('169-namespace-alias','renderer','functions.inc','base==169?303:','base==169?298:'),
 ('wrong-283-slot','renderer','functions.inc','base==283?311:','base==283?310:'),
 ('unreviewed-base-admitted','renderer','functions.inc','base==283?311:','base==284?311:'),
 ('byte-pointer-alias','renderer','functions.inc','bank.data==enemySpriteSheets[i].data','enemySpriteSheets[i].data&&*bank.data==*enemySpriteSheets[i].data'),
 ('bank9-new-family-admitted','renderer','functions.inc','if(role==ASSET_NEWSHE) {','if(role==ASSET_NEWSHE&&base<100) {'),
 ('wrong-anchor','renderer','functions.inc','scene_asset(slot,role,(int)base,6,7)','scene_asset(slot,role,(int)base,7,7)'),
 ('wrong-quadrant-origin','renderer','functions.inc','draw_asset_filtered(x-px,y-py,a,MIRROR_NORMAL','draw_asset_filtered(x,y-py,a,MIRROR_NORMAL'),
 ('filter-discarded','renderer','functions.inc','&quadrant,(Uint8)filter','&quadrant,0'),
 ('entire-frame-for-quadrant','renderer','functions.inc','&quadrant,(Uint8)filter','((void)&quadrant,NULL),(Uint8)filter'),
 ('role-cache-poison169','renderer','functions.inc','Asset *a=&assets[slot];','if(role==ASSET_SHAPESZ&&index==169){slot=303;}\n Asset *a=&assets[slot];'),
 ('original-filter-omitted','wrapper','wrapper.inc','if (enemy[i].filter != 0)','if (false && enemy[i].filter != 0)'),
 ('wrapper-original-blit-twice','wrapper','wrapper.inc','blit_sprite2_filter(surface, x, y, *enemy[i].sprite2s, index, enemy[i].filter);','{blit_sprite2_filter(surface, x, y, *enemy[i].sprite2s, index, enemy[i].filter);blit_sprite2_filter(surface, x, y, *enemy[i].sprite2s, index, enemy[i].filter);}'),
 ('wrapper-end-omitted','wrapper','wrapper.inc','render_mirror_entity_end();','(void)&render_mirror_entity_end;'),
 ('wrapper-end-twice','wrapper','wrapper.inc','render_mirror_entity_end();','render_mirror_entity_end();render_mirror_entity_end();'),
 ('wrapper-mutates-state','wrapper','wrapper.inc','render_mirror_entity_end();','enemy[i].filter=0;render_mirror_entity_end();'),
 ('wrapper-wrong-part','wrapper','wrapper.inc','sprite_offset,enemy[i].filter);','sprite_offset+1,enemy[i].filter);'),
]
root=Path(tempfile.mkdtemp(prefix='installation9-mutants-'));results=[]
for name,kind,filename,old,new in mutations:
 directory=root/name;directory.mkdir()
 for f in ['types.inc','functions.inc','wrapper.inc','blitters.inc']:
  text=(work/f).read_text()
  if f==filename:
   assert text.count(old)==1,(name,text.count(old));text=text.replace(old,new)
  (directory/f).write_text(text)
 harness='test-installation9'+('-wrapper'if kind=='wrapper'else'')+'.c'
 source=(work/harness).read_text()
 if kind=='renderer':
  # Use the unchanged native8 pass for fast fault rejection. Full density4
  #9x24x256 and all scale passes remain required by the authoritative oracle.
  old_loop='for(int mode=0;mode<3;mode++)'
  assert source.count(old_loop)==1
  source=source.replace(old_loop,'for(int mode=1;mode<2;mode++)')
 (directory/harness).write_text(source)
 command=['cc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(directory/harness),'-o',str(directory/'test')]
 build=subprocess.run(command,text=True,capture_output=True);(directory/'build.log').write_text(build.stdout+build.stderr);assert build.returncode==0,(name,build.stderr)
 run=subprocess.run([str(directory/'test'),str(work/'packs')],text=True,capture_output=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'),preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_CORE,(0,0)))
 assert run.returncode!=0,name+' escaped the negative oracle'
 assert any(x in run.stderr for x in ['Assertion','pixel mismatch','runtime error:','ERROR: AddressSanitizer:']),(name,run.stderr)
 (directory/'result.log').write_text(run.stdout+run.stderr)
 results.append({'name':name,'kind':kind,'rejected':True,'exit_code':run.returncode,'first_diagnostic':run.stderr.splitlines()[0],'mutation_before':old,'mutation_after':new,'compile_command':command})
 print('REJECTED:',name,flush=True)
report={'status':'passed','mutants_rejected':len(results),'work':str(root),'authoritative_work':str(work),'results':results,'inputs_sha256':{f:hashlib.sha256((work/f).read_bytes()).hexdigest()for f in ['types.inc','functions.inc','wrapper.inc','blitters.inc','test-installation9.c','test-installation9-wrapper.c']},'scope':'Only temporary snippets mutated. Renderer negatives run native8 subset of unchanged assertions; authoritative full9x24x256 and all scale tests are separate. No production edits/game/art/capture/deletion/publication.'}
out=a.report or root/'report.json';out.write_text(json.dumps(report,indent=2)+'\n');print('Report:',out)
