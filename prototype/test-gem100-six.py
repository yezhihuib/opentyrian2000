#!/usr/bin/env python3
"""Finite four-family extracted-production proof. Reuses the published 25 C oracle.
No game starts or images; one tiny six/27-file mutation fixture is reused.
The original 25 scripts and oracle remain byte-identical historical evidence.
"""
import argparse,hashlib,importlib.util,json,os,re,struct,subprocess,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PIN='641e4e7370c9f3542ba9d0daf1ebf2a1a988614e'
INV='4489265f4556f12fecfd1745e271dcbdb2776c52d419971eb998cddc1a40df6d'
SHA=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('prior',ROOT/'prototype/test-cash25-seven.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior);extract=prior.extract
FUNCS=['palette_rgb','blend_rgba','cloud_asset','darken_rgba','decode_tile','read_asset','cash25_family_ready','cash75_family_ready','cash50_family_ready','gem100_family_ready','cash25_surface_ready','render_mirror_coin25_value_begin','render_mirror_coin75_value_begin','render_mirror_coin50_value_begin','render_mirror_gem100_value_begin','explosion_asset_slot','get_asset','talon_frame','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','draw_asset','cash25_pickup','cash75_pickup','cash50_pickup','gem100_pickup','render_mirror_entity','enemy_energy_slot','enemy_energy_family_ready','render_mirror_enemy_shot','render_mirror_entity_end']
TYPES=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'static Asset assets\[\d+\];',r'static Asset talon_frames\[13\];',r'static bool enemy_energy_checked,enemy_energy_valid;',r'static bool cash25_checked,cash25_valid;',r'static bool cash75_checked,cash75_valid;',r'static bool cash25_fixed_value;',r'static bool cash75_fixed_value;',r'static bool cash50_checked,cash50_valid;',r'static bool cash50_fixed_value;',r'static bool gem100_checked,gem100_valid;',r'static bool gem100_fixed_value;']
def project(s):
 for n in ['gem100_family_ready','render_mirror_gem100_value_begin','gem100_pickup']:s=s.replace(extract(s,n)+'\n','')
 removes=['/* Independent five-state gem plus shared fixed100; never replaces moving169. */\n','static bool gem100_checked,gem100_valid;\n',"/* Only record394's original global bank11 small tile can enter this family. */\n",'static bool gem100_fixed_value;\n',' gem100_fixed_value=false;\n',' bool fixed_value100=gem100_fixed_value;gem100_fixed_value=false;\n',' bool gem100_value_blend=style==MIRROR_BLEND&&a->bank==ASSET_GEM100_VALUE&&a->index==169&&!game_probe_original_reference;\n']
 for line in removes:assert s.count(line)==1,line;s=s.replace(line,'')
 value=' if(fixed_value100&&bank.data&&bank.data==explosionSpriteSheet.data&&index==169&&\n    layout==ENTITY_TILE&&(style==MIRROR_NORMAL||style==MIRROR_BLEND)) {\n  bool mirrored=cash25_surface_ready(surface,x,y)&&gem100_family_ready()&&\n   draw_asset(x,y,&assets[498],style,NULL);\n  game_probe_scene_draw(ASSET_GEM100_VALUE,index,x,y,0,style,mirrored);\n  return mirrored;\n }\n'
 branch='  if(base>=32&&base<=36) {\n   bool mirrored=gem100_pickup(surface,x,y,bank,base,part,filter,material_context);\n   game_probe_scene_draw(ASSET_GEM100_BODY,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);\n   return mirrored;\n  }\n'
 for line in [value,branch]:assert s.count(line)==1;s=s.replace(line,'')
 for old,new in [(', ASSET_GEM100_BODY=118, ASSET_GEM100_VALUE=119',''),('assets[499]','assets[493]'),('a->bank==ASSET_GEM100_BODY?"gem100-bank11":a->bank==ASSET_GEM100_VALUE?"gem100-value-newsh6":',''),('&&!gem100_value_blend',''),('||gem100_value_blend',''),('cash50_fixed_value=false;gem100_fixed_value=false;','cash50_fixed_value=false;')]:assert s.count(old)==1,old;s=s.replace(old,new)
 return s
MIXED=r"""
static void leases(bool a,bool b,bool c,bool d){render_mirror_coin25_value_begin(a);render_mirror_coin75_value_begin(b);render_mirror_coin50_value_begin(c);render_mirror_gem100_value_begin(d);}
static void cleared(void){CHECK(!cash25_fixed_value&&!cash75_fixed_value&&!cash50_fixed_value&&!gem100_fixed_value);}
static void mixed_checks(int mask){
 CHECK(cash25_family_ready()==!!(mask&1));CHECK(cash75_family_ready()==!!(mask&2));CHECK(cash50_family_ready()==!!(mask&4));CHECK(gem100_family_ready()==!!(mask&8));start();
 G101EnemyContext a={391,0,2,0,true,false,true,false},b={393,0,2,0,true,false,true,false},c={392,0,2,0,true,false,true,false},d={394,0,2,0,true,false,true,false};
 reset_area(98,100);CHECK(cash25_pickup(&screen,98,100,spriteSheet11,7,0,0,&a)==!!(mask&1));render_mirror_entity_end();
 reset_area(98,100);CHECK(cash75_pickup(&screen,98,100,spriteSheet11,20,0,0,&b)==!!(mask&2));render_mirror_entity_end();
 reset_area(98,100);CHECK(cash50_pickup(&screen,98,100,spriteSheet11,26,0,0,&c)==!!(mask&4));render_mirror_entity_end();
 reset_area(98,100);CHECK(gem100_pickup(&screen,98,100,spriteSheet11,32,0,0,&d)==!!(mask&8));render_mirror_entity_end();
 for(int wrong=0;wrong<6;wrong++){d.type=(int[]){391,393,392,509,390,30000}[wrong];CHECK(!gem100_pickup(&screen,98,100,spriteSheet11,32,0,0,&d));}d.type=394;
 CHECK(!cash25_pickup(&screen,98,100,spriteSheet11,7,0,0,&d));CHECK(!cash75_pickup(&screen,98,100,spriteSheet11,20,0,0,&d));CHECK(!cash50_pickup(&screen,98,100,spriteSheet11,26,0,0,&d));
 const unsigned ids4[4]={185,223,204,169};const int slots4[4]={472,479,486,493},counts4[4]={7,7,7,6};
 for(int first=0;first<4;first++)for(int second=0;second<4;second++){reset_area(98,100);leases(true,true,true,true);CHECK(render_mirror_entity(&screen,98,100,explosionSpriteSheet,ids4[first],MIRROR_NORMAL,ENTITY_TILE)==!!(mask&(1<<first)));cleared();CHECK(!render_mirror_entity(&screen,98,100,explosionSpriteSheet,ids4[second],MIRROR_NORMAL,ENTITY_TILE));cleared();}
 for(int which=0;which<4;which++)for(int mode=0;mode<10;mode++){reset_area(98,100);leases(true,true,true,true);if(mode==0)active=false;if(mode==1)reject_reason="mixed";Sprite2_array bank=mode==2?spriteSheet11:explosionSpriteSheet;SDL_Surface *surface=mode==3?NULL:&screen;int style=mode==4?MIRROR_SHADOW:MIRROR_NORMAL,layout=mode==5?ENTITY_QUAD:ENTITY_TILE;unsigned id=mode==6?168:ids4[which];if(mode==7)game_probe_missing=true;if(mode==8)game_probe_invalid=true;if(mode==9)game_probe_density=4;CHECK(!render_mirror_entity(surface,98,100,bank,id,style,layout));cleared();active=true;reject_reason=NULL;game_probe_missing=game_probe_invalid=false;game_probe_density=8;}
 for(int which=0;which<4;which++)for(int other=0;other<4;other++)if(which!=other){leases(which==0,which==1,which==2,which==3);CHECK(!render_mirror_entity(&screen,98,100,explosionSpriteSheet,ids4[other],MIRROR_NORMAL,ENTITY_TILE));cleared();}
 leases(true,true,true,true);render_mirror_entity_end();cleared();
 if(mask==15)for(int first=0;first<4;first++)for(int second=0;second<4;second++)for(int i=0;i<counts4[first];i++)for(int j=0;j<counts4[second];j++)for(int blend1=0;blend1<(i==counts4[first]-1?2:1);blend1++)for(int blend2=0;blend2<(j==counts4[second]-1?2:1);blend2++){
  reset_area(98,100);Asset *a=assets+slots4[first]+i,*b=assets+slots4[second]+j;CHECK(draw_asset(98,100,a,blend1?MIRROR_BLEND:MIRROR_NORMAL,NULL));CHECK(draw_asset(98,100,b,blend2?MIRROR_BLEND:MIRROR_NORMAL,NULL));
  for(int py=0;py<112;py++)for(int px=0;px<96;px++){int n=(100*8+py)*canvas->w+98*8+px;const Uint8 *ra=a->rgba+4*(py*96+px),*rb=b->rgba+4*(py*96+px);CHECK(((Uint32*)canvas->pixels)[n]==composed(composed(bg(n),ra,blend1),rb,blend2));CHECK(hd_owner[n]==1);CHECK(cloud_owner[n]==((ra[3]||rb[3])?0:1));CHECK(green_first[n]==((ra[3]||rb[3])?0:7));}
 }
 clear_assets();free(canvas->pixels);free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);free(screen.pixels);printf("PASS mixed families mask%d checks%llu\n",mask,(unsigned long long)checks);
}
"""
spec50=importlib.util.spec_from_file_location('prior50',ROOT/'prototype/test-cash50-seven.py');prior50=importlib.util.module_from_spec(spec50);spec50.loader.exec_module(prior50)
def driver(family):
 s=prior50.driver(family if family!=100 else 50)
 s=s.replace(prior50.MIXED,MIXED).replace('sizeof(assets)/sizeof(*assets)==493','sizeof(assets)/sizeof(*assets)==499')
 s=s.replace('ASSET_CASH50_VALUE=117,','ASSET_CASH50_VALUE=117,ASSET_GEM100_BODY=118,ASSET_GEM100_VALUE=119,')
 s=s.replace('enemy_energy_checked=enemy_energy_valid=false;','gem100_checked=gem100_valid=false;enemy_energy_checked=enemy_energy_valid=false;')
 if family==100:
  # Do not transform the four-family mixed oracle; only the reused per-family oracle.
  s=s.replace(MIXED,'GEM100_MIXED_PLACEHOLDER')
  for old,new in [('cash50','gem100'),('coin50','gem100'),('COIN50','GEM100'),('ASSET_CASH50','ASSET_GEM100'),('{26,27,28,29,30,31,204}','{32,33,34,35,36,169}'),('id<26||id>31','id<32||id>36'),('spriteSheet11,26,','spriteSheet11,32,'),('wrong,26,','wrong,32,'),('null,26,','null,32,')]:s=s.replace(old,new)
  changes={392:394,486:493,492:498,204:169,205:170}
  s=re.sub(r'\b(?:'+'|'.join(map(str,changes))+r')\b',lambda m:str(changes[int(m.group())]),s)
  # Restore the combined enum and clear flags after per-family mechanical substitutions.
  s=re.sub(r'enum \{ASSET_NEWSH2=.*?\};','enum {ASSET_NEWSH2=101,ASSET_NEWSH4=102,ASSET_NEWSHE=110,ASSET_ENEMY_ENERGY=111,ASSET_CASH25_BODY=112,ASSET_CASH25_VALUE=113,ASSET_CASH75_BODY=114,ASSET_CASH75_VALUE=115,ASSET_CASH50_BODY=116,ASSET_CASH50_VALUE=117,ASSET_GEM100_BODY=118,ASSET_GEM100_VALUE=119,ASSET_TALON_BANK=109,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106};',s)
  s=s.replace('cash75_checked=cash75_valid=false;gem100_checked=gem100_valid=false;','cash75_checked=cash75_valid=false;cash50_checked=cash50_valid=false;')
  for old,new in [('ids[7]','ids[6]'),('first<7','first<6'),('second<7','second<6'),('second==6','second==5'),('n==7*336','n==6*336'),('k<7','k<6'),('k==6','k==5'),('if(k<6)','if(k<5)'),('CHECK(k<6?','CHECK(k<5?'),('transactions==96','transactions==84')]:s=s.replace(old,new)
  s=s.replace('gem100_checked=gem100_valid=false;cash25_checked=', 'cash25_checked=')
  s=s.replace('GEM100_MIXED_PLACEHOLDER',MIXED)
 return s

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--original-data',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
 old=lambda name:subprocess.check_output(['git','-C',str(ROOT),'show',PIN+':'+name])
 src=(ROOT/'src/render_mirror.c').read_text();assert project(src).encode()==old('src/render_mirror.c')
 h=(ROOT/'src/render_mirror.h').read_text();assert h.replace('#define render_mirror_gem100_value_begin(...) ((void)0)\n','').replace('void render_mirror_gem100_value_begin(bool fixed);\n','').encode()==old('src/render_mirror.h')
 hook='\t\t\t\trender_mirror_gem100_value_begin(explosions[j].fixedPosition && !explosions[j].followPlayer &&\n\t\t\t\t                                explosions[j].deltaY == 0 && explosions[j].sprite == 168 && explosions[j].ttl <= 8);\n'
 ty=(ROOT/'src/tyrian2.c').read_text();assert ty.count(hook)==1 and ty.replace(hook,'').encode()==old('src/tyrian2.c')
 names=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only',PIN,'--','src'],text=True).splitlines();changed=[n for n in names if (ROOT/n).read_bytes()!=old(n)];assert set(changed)=={'src/render_mirror.c','src/render_mirror.h','src/tyrian2.c'}
 for n in ['prototype/test-cash25-seven.py','prototype/test-cash25-seven.c','prototype/test-cash25-mutations.py','prototype/build-cash25-seven-art.py','prototype/test-cash75-seven.py','prototype/test-cash75-mutations.py','prototype/test-cash75-original.py','prototype/test-cash75-original.c','prototype/test-cash75-original.h','prototype/build-cash75-seven-art.py','prototype/test-cash50-seven.py','prototype/test-cash50-mutations.py','prototype/test-cash50-original.py','prototype/test-cash50-original.c','prototype/test-cash50-original.h','prototype/build-cash50-seven-art.py']:assert (ROOT/n).read_bytes()==old(n)
 for family in [25,75,50,100]:
  entity=extract(src,'render_mirror_entity');assert entity.index(f'{"gem100" if family==100 else "cash"+str(family)}_fixed_value=false;')<entity.index('if(')
  assert f'{"gem100" if family==100 else "cash"+str(family)}_fixed_value=false;' in extract(src,'render_mirror_begin') and f'{"gem100" if family==100 else "cash"+str(family)}_fixed_value=false;' in extract(src,'render_mirror_entity_end')
 unchanged=['cash50_family_ready','cash50_pickup','render_mirror_coin50_value_begin','cash75_family_ready','cash75_pickup','render_mirror_coin75_value_begin','cash25_family_ready','cash25_surface_ready','cash25_pickup','render_mirror_coin25_value_begin','get_asset','explosion_asset_slot','render_mirror_enemy_shot','enemy_energy_family_ready','recognized_value_effect','recognized_contact_effect','render_mirror_sprite2_blend_pixel','explosion_asset_blend_rgba','render_mirror_pixel']
 for n in unchanged:assert extract(src,n)==extract(old('src/render_mirror.c').decode(),n)
 m=json.loads((ROOT/'assets/hd/manifest.json').read_text());base=json.loads(old('assets/hd/manifest.json'));packs=[m['default_preview_pack'],m['default_debug_pack']];raws={};both={}
 for family in [25,75,50,100]:
  art=ROOT/('assets/hd/artwork/gem100-six-v1' if family==100 else f'assets/hd/artwork/cash{family}-seven-v1');iv=json.loads((art/'inventory.json').read_text());assert family!=100 or SHA((art/'inventory.json').read_bytes())==INV
  for row in iv['outputs']:
   name=f"{row['prefix']}-{row['id']}-8.hda";raw=(art/'output'/name).read_bytes();both[name]=raw
   if family==100:raws[name]=raw
 for pack,data in base['packs'].items():
  assert m['packs'][pack]['count']==len(m['packs'][pack]['files'])
  assert set(m['packs'][pack]['files'])-set(data['files'])==(set(raws) if pack in packs else set())
  for name,entry in data['files'].items():assert m['packs'][pack]['files'][name]==entry and SHA((ROOT/'assets/hd/packs'/pack/name).read_bytes())==entry['sha256']
 physical=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only',PIN,'--','assets/hd/packs'],text=True).splitlines()
 for name in physical:assert SHA((ROOT/name).read_bytes())==SHA(old(name)),name
 projected=json.loads(json.dumps(m));del projected['gem100_six_v1']
 for pack in packs:
  for name in raws:del projected['packs'][pack]['files'][name]
  projected['packs'][pack]['count']-=6
 for raw in raws.values():del projected['source_pngs'][SHA(raw)]
 assert projected==base
 data=a.original_data.resolve();original=(data/'tyrian.shp').read_bytes();effects=(data/'newsh6.shp').read_bytes();assert SHA(original)=='80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0' and SHA(effects)=='49e3d08e122ea71d6a621d2de127da00ce8a26ff73a0fb40d0cdd7ca2909d075';count=struct.unpack_from('<H',original)[0];offsets=list(struct.unpack_from('<'+str(count)+'I',original,2))+[len(original)];bank=original[offsets[10]:offsets[11]]
 def decode(raw,idx):
  pos=struct.unpack_from('<H',raw,(idx-1)*2)[0];cell=0;values=bytearray(168);mask=bytearray(168)
  while raw[pos]!=15:
   code=raw[pos];pos+=1;cell+=code&15
   for _ in range(code>>4):assert 0<=cell<168;values[cell]=raw[pos];mask[cell]=255;pos+=1;cell+=1
  return values+mask
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');results={}
 for family in [25,75,50,100]:
  d=out/str(family);d.mkdir();(d/'bank11.bin').write_bytes(bank);(d/'newsh6.bin').write_bytes(effects);ids={25:range(7,13),75:range(20,26),50:range(26,32),100:range(32,37)}[family];(d/'index-reference.bin').write_bytes(b''.join(decode(bank,i) for i in ids)+decode(effects,{25:185,75:223,50:204,100:169}[family]))
  (d/'types.inc').write_text('\n'.join(re.search(p,src,re.S).group() for p in TYPES));(d/'functions.inc').write_text('\n'.join(extract(src,n) for n in FUNCS));(d/'driver.c').write_text(driver(family))
  sprite=(ROOT/'src/sprite.c').read_text();wrapper=(ROOT/'src/entity_draw.c').read_text();(d/'blitters.inc').write_text('\n'.join(extract(sprite,n) for n in ['blit_sprite2','blit_sprite2_blend','blit_sprite2_darken']));(d/'wrapper.inc').write_text(extract(wrapper,'draw_entity_sprite2'))
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(d),str(d/'driver.c'),'-o',str(d/'test')];r=subprocess.run(cmd,capture_output=True,text=True);(d/'compile.log').write_text(r.stdout+r.stderr);r.check_returncode()
  for pack in packs:
   r=subprocess.run([str(d/'test'),'render',str(ROOT/'assets/hd/packs'/pack),'1',str(d)],capture_output=True,text=True,env=env,timeout=120);assert r.returncode==0,(family,r.stdout,r.stderr);results[str(family)+'/'+pack]=r.stdout.strip();print(family,pack,r.stdout.strip(),flush=True)
 d=out/'100'
 def run(mode,pack,valid):
  r=subprocess.run([str(d/'test'),mode,str(pack),str(int(valid)),str(d)],capture_output=True,text=True,env=env,timeout=120);assert r.returncode==0,(mode,valid,r.stdout,r.stderr);return r.stdout.strip()
 cases=[];mixed=[]
 with tempfile.TemporaryDirectory(prefix='gem100-six-unit-') as tmp:
  pack=Path(tmp)
  for name,raw in raws.items():(pack/name).write_bytes(raw)
  run('loader',pack,True)
  for name,raw in raws.items():
   variants={'missing':None,'magic':b'BAD!'+raw[4:],'short-header':raw[:27],'truncated':raw[:-1],'trailing':raw+b'X','rgba':raw[:28]+bytes([raw[28]^1])+raw[29:],'alpha':raw[:31]+bytes([raw[31]^1])+raw[32:]}
   for label,offset,value in [('key',4,1),('density',8,4),('width',12,11),('height',16,13),('anchor-x',20,1),('anchor-y',24,1)]:bad=bytearray(raw);struct.pack_into('<I',bad,offset,value);variants[label]=bad
   for label,bad in variants.items():
    if bad is None:(pack/name).unlink()
    else:(pack/name).write_bytes(bad)
    run('loader',pack,False);cases.append([name,label]);(pack/name).write_bytes(raw)
  for name,raw in raws.items():
   (pack/name).unlink();rgba=raw[28:];(pack/name.replace('-8.','-4.')).write_bytes(raw[:8]+struct.pack('<I',4)+raw[12:28]+b''.join(rgba[(2*y*96+2*x)*4:(2*y*96+2*x)*4+4] for y in range(56) for x in range(48)))
  run('loader',pack,False);cases.append(['all','4x-only'])
  for name in raws:(pack/name).write_bytes(b'bad')
  run('loader',pack,False);cases.append(['all','invalid8-valid4'])
  for mask in range(16):
   for name,raw in both.items():
    if mask&(1 if name.startswith('coin25-') else 2 if name.startswith('coin75-') else 4 if name.startswith('coin50-') else 8):(pack/name).write_bytes(raw)
    elif (pack/name).exists():(pack/name).unlink()
   mixed.append(run('mixed',pack,mask))
 report={'status':'PASS','game_runs':0,'sanitizers':['ASan','UBSan'],'baseline_commit':PIN,'changed_production_files':changed,'full_additive_inverse':'all three production files byte-identical','unchanged_functions':unchanged,'historical_25_75_50_test_files':'byte-identical; new harness explicitly adjusts only capacity/selected family and adds mixed assertions','manifest_projection':'identical to baseline; every previous pack payload hashed','immutable_inventory_sha256':INV,'renderer_results':results,'mixed_family_results':mixed,'resource_rejections':cases,'extracted_functions_sha256':{n:SHA(extract(src,n).encode()) for n in FUNCS},'source_sha256':{n:SHA((ROOT/n).read_bytes()) for n in changed},'limitations':['No actual game/RGB evidence.','Per family/pair 84/96 indexed transactions use unchanged real blitters/wrapper; display pixel hooks isolated, RGBA tested separately.']};(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(cases),'resource cases; 16 mixed-family combinations')
if __name__=='__main__':main()
