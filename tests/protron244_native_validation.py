"""Finite244-only preparation; no compiler, process, generator or writes."""
from pathlib import Path
import hashlib,types,struct
ROOT=Path(__file__).resolve().parents[1]
ORB_HELPER_SHA='29a8a9c8c5f626ec32b2ad35dafe3c5659f2bcb028ce4d81ebc3204e01aa0d9d'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def old_helper(root):
 p=Path(root)/'tests/orb_protron_native_validation.py';raw=p.read_bytes()
 if sha(raw)!=ORB_HELPER_SHA:raise ValueError('Changed orb helper')
 m=types.ModuleType('approved_orb_native');m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__);return m
_old=old_helper(ROOT)
OLD_IDS=_old.IDS
IDS=OLD_IDS+(244,)
CANONICAL=dict(_old.CANONICAL);CANONICAL[244]='901b61b1da6f538d6aac9bbd06a2f7d34e5e9d1e4d9df50c3f3eb01b1cd7b452'
PACKS=('valid','missing244','bad244','header244')
TAIL=b'\n#include "protron244_native_additions.c.inc"\nint main(int argc,char **argv)\n{\n if(argc>=2&&!strcmp(argv[1],"--protron244"))return p244_main(argc,argv);\n return inherited_orb_protron_dispatch(argc,argv);\n}\n'
def source_bundle(root):
 sources,old=old_helper(root).source_bundle(root);return sources,outer_shim(old,root)
def outer_shim(raw,root):
 if raw!=old_helper(root).source_bundle(root)[1]or raw.count(b'int main(')!=1:raise ValueError('Changed eleven historical dispatches')
 return raw.replace(b'int main(',b'int inherited_orb_protron_dispatch(',1)+TAIL
def reverse_shim(raw,root):
 if not raw.endswith(TAIL):raise ValueError('Changed new tail')
 body=raw[:-len(TAIL)]
 if body.count(b'int inherited_orb_protron_dispatch(')!=1 or b'int main('in body:raise ValueError('Changed dispatcher')
 old=body.replace(b'int inherited_orb_protron_dispatch(',b'int main(',1)
 if old!=old_helper(root).source_bundle(root)[1]:raise ValueError('Changed old dispatch bytes')
 return old
def fixture_bytes(raw,index,leaf,wrong=None):
 if type(raw)is not bytes or len(raw)!=43036 or type(index)is not int or index not in IDS or leaf not in PACKS:raise ValueError('Invalid finite fixture')
 if index!=244 or leaf=='valid':return raw
 if leaf=='missing244':return None
 b=bytearray(raw)
 if leaf=='header244':struct.pack_into('<I',b,4,1470244)
 else:
  if type(wrong)is not bytes or sha(wrong)!=CANONICAL[227]:raise ValueError('Pinned actual227 material required')
  b=bytearray(wrong);struct.pack_into('<I',b,4,80244)
 return bytes(b)
def fixture_payloads(hdas,pins,names):
 if any(set(d)!=set(IDS)for d in (hdas,pins,names)):raise ValueError('Exact30 resources required')
 for i in IDS:
  if type(i)is not int or type(hdas[i])is not bytes or sha(hdas[i])!=pins[i]:raise ValueError('Changed approved bytes')
  p=Path(names[i])
  if p.is_absolute()or '..'in p.parts or not str(p).endswith('.hda'):raise ValueError('Invalid fixture path')
  if i in CANONICAL:
   if sha(hdas[i])!=CANONICAL[i]or str(p)!='content/'+CANONICAL[i]+'.hda':raise ValueError('Changed material identity/path')
  elif p.name!=str(p):raise ValueError('Old flat path changed')
 if len(set(names.values()))!=30:raise ValueError('Duplicate fixture paths')
 out={}
 for leaf in PACKS:
  for i in IDS:
   raw=fixture_bytes(hdas[i],i,leaf,hdas[227])
   if raw is not None:out['protron244-packs/'+leaf+'/'+names[i]]=raw
 if len(out)!=119:raise ValueError('Finite119 fixture count changed')
 return out
def native_input(base_stdin,hdt):return _old.native_input(base_stdin,hdt)
CASE_INVENTORY={'current29_complete_oracles':29,'missing_wrongmaterial_wrongidentity':3,'warm_identity_geometry':2,'root_epoch_independent_player_lease':2,'source_before_cache':2,'used_unused_live_palette_and_unused_cached_decline':3,'unused244_retains_old28_then_real_retired_used_resource':1,'static_repeated_sameposition_nextframe':1,'real_fade_step_and_source_decline':2,'real_player70_two_order_handoff':2,'full_native_cell_finalwrite_patch_recovery':1,'xmas_density_topclip':3,'bit28_all29_green_excluded':1,'background27_four_stages_recovery':4}
assert sum(CASE_INVENTORY.values())==56
SYNTAX_TUS=('src/render_mirror.c','src/tyrian2.c','src/entity_draw.c')
MACRO_ON_PIXEL_SCOPE='DEFERRED; tiny exact-source intent/routing/proof fixture only, not whole ON sessions/pixels; Green excluded'
def tiny_sources(root):
 """Reuse reviewed exact-production extraction, replace only its finite test
 driver. Never edit or paraphrase extracted production functions/branches."""
 root=Path(root);raw,pins=old_helper(root).tiny_sources(root);s=raw.decode()
 replacements={
  'unsigned ids[4]={112,113,226,227};':'unsigned ids[5]={112,113,226,227,244};',
  'for(unsigned k=0;k<4;k++) {':'for(unsigned k=0;k<5;k++) {',
  'unsigned prior[]={91,70,20,214,215,216,244,42};':'unsigned prior[]={91,70,20,214,215,216,125,42};',
  'bool old=enabled&&(j>=3&&j<=6||(j==2&&state));':'bool old=enabled&&(j>=3&&j<=5||((j==2||j==6)&&state));',
  'else if(!old)assert(ordinary==1||(j>=3&&j<=6&&classic==1));++cases;':'else if(!old)assert(ordinary==1||(j>=3&&j<=5&&classic==1));if(j>=3&&j<=5){clear_counts();assert(!render_mirror_enemy_shot(game_screen,0,0,spriteSheet8,prior[j]));assert(!shared_calls&&!atomic_calls&&!generic_reads&&!generic_draws);assert(global_projectile91_member(prior[j])==0);}++cases;',
  'assert(cases==320);printf("PASS Orb Protron exact-source routing proof: 320 cases; NOT full ON session/pixels\\n");':'assert(cases==384);printf("PASS Protron244 exact-source routing proof: 384 cases; Green excluded; NOT full ON session/pixels\\n");'
 }
 for old,new in replacements.items():
  if s.count(old)!=1:raise ValueError('Changed inherited test-driver anchor '+old)
  s=s.replace(old,new,1)
 shared=(root/'src/global_projectile91_mirror.inc').read_text();start=shared.index('static unsigned global_projectile91_member(unsigned index)');end=shared.index('\nstatic Asset *global_projectile91_member_resource',start);member=shared[start:end]
 anchor='static void clear_counts(void)'
 if s.count(anchor)!=1:raise ValueError('Changed fixture insertion')
 s=s.replace(anchor,member+'\n'+anchor,1)
 return s.encode(),pins
