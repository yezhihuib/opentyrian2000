#!/usr/bin/env python3
"""Finite exact production shell proof, reusing the original energy C pixel oracle.
No game process/capture. --source-only performs no compilation or unit execution.
"""
import argparse,hashlib,importlib.util,json,os,re,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='916b7aa8a4a837c695d6cef4b1e9da133db27ef1'
SHA=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('energy',ROOT/'prototype/test-enemy-energy-seven.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old);extract=old.extract
IDS=[146,147,77,58,182,163,1,183,164,112,113,58]
FUNCS=['palette_rgb','blend_rgba','cloud_shadow_rgba','cloud_asset','darken_rgba','decode_tile','read_asset','cash25_family_ready','cash75_family_ready','cash50_family_ready','gem100_family_ready','gem250_family_ready','cash25_surface_ready','explosion_asset_slot','get_asset','talon_frame','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','draw_asset','render_mirror_entity','enemy_energy_slot','enemy_energy_family_ready','enemy_tank_shell_family_ready','render_mirror_enemy_shot','render_mirror_pixel','render_mirror_entity_end']
def previous(n):return subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+n])
def source_checks():
 files=['src/render_mirror.c','src/entity_draw.c','src/tyrian2.c'];src={n:(ROOT/n).read_bytes() for n in files};before={n:previous(n) for n in files};s=src[files[0]].decode();b=before[files[0]].decode()
 family=extract(s,'enemy_tank_shell_family_ready');comment='/* Two frozen ID-fixed shell headings, shared by enemy records15/194/195.\n * Startup-selected lifetime cache, independent of energy, orbs and players. */\n';p=s.replace(comment+'static bool enemy_tank_shell_checked,enemy_tank_shell_valid;\n'+family+'\n','')
 old_hook=extract(b,'render_mirror_enemy_shot');new_hook=extract(s,'render_mirror_enemy_shot');tail=old_hook.split('{',1)[1];assert new_hook.endswith(tail),'old energy/orb body changed';p=p.replace(new_hook,old_hook)
 for x,y in [(', ASSET_ENEMY_TANK_SHELL=122',''),('assets[507]','assets[505]'),('a->bank==ASSET_ENEMY_TANK_SHELL?"enemy-tank-shell":','')]:assert p.count(x)==1;p=p.replace(x,y)
 assert p.encode()==before[files[0]],'render source inverse'
 e=src[files[1]].decode();extra=' else if(bank.data==spriteSheet8.data&&(index==146||index==147))\n  game_probe_scene_draw(122,index,x,y,0,ENTITY_NORMAL,mirrored);\n';assert e.count(extra)==1 and e.replace(extra,'').encode()==before[files[1]]
 t=src[files[2]].decode();extra=' || sprite == 146 || sprite == 147';assert t.count(extra)==1 and t.replace(extra,'').encode()==before[files[2]]
 tracked=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only',BASE,'--','src'],text=True).splitlines()
 assert [n for n in tracked if (ROOT/n).read_bytes()!=previous(n)]==sorted(files)
 m=json.loads((ROOT/'assets/hd/manifest.json').read_text());base=json.loads(previous('assets/hd/manifest.json'));proj=json.loads(json.dumps(m));rows=proj.pop('enemy_tank_shell_pair_v1')['entries']
 for row in rows:
  del proj['source_pngs'][row['HDA_sha256']]
  for pack in [m['default_preview_pack'],m['default_debug_pack']]:del proj['packs'][pack]['files'][f"enemy-tank-shell-{row['id']}-8.hda"];proj['packs'][pack]['count']-=1
 assert proj==base,'manifest additive inverse'
 # Every prior pack payload remains byte identical; no source art is regenerated.
 for pack,data in base['packs'].items():
  for name,item in data['files'].items():assert SHA((ROOT/'assets/hd/packs'/pack/name).read_bytes())==item['sha256'],(pack,name)
 for n in ['prototype/test-enemy-energy-seven.py','prototype/test-enemy-energy-seven.c','src/shots.c','src/sprite.c','src/varz.c','src/render_mirror.h']:assert (ROOT/n).read_bytes()==previous(n),n
 return {'status':'PASS','baseline':BASE,'changed_production_files':files,'complete_source_inverse':True,'old_energy_orb_body_unchanged':True,'manifest_additive_inverse':True,'all_predecessor_pack_payloads_exact':True,'source_sha256':{n:SHA(v) for n,v in src.items()},'game_runs':0,'builds':0},s,m

def driver(s):
 c=(ROOT/'prototype/test-enemy-energy-seven.c').read_text()
 c=re.sub(r'enum \{ASSET_NEWSH2=.*?\};',re.search(r'enum \{ ASSET_NEWSH2=.*?\};',s).group(),c)
 c=c.replace('static bool active=true,','static bool xmas;\nstatic bool active=true,')
 c=c.replace('#define settings_font_pixel(...) ((void)0)','#define settings_font_pixel(...) ((void)0)\n#define selector_font_pixel(...) ((void)0)\n#define pregame_font_pixel(...) ((void)0)\n#define pregame_font_sprite2_begin(...) ((void)0)\n#define pregame_font_sprite2_end(...) ((void)0)')
 c=c.replace('#include "functions.inc"','static void game_probe_scene_draw(int,unsigned,int,int,int,int,bool);\n#include "functions.inc"')
 c=c.replace('static const unsigned ids[10]={77,58,182,163,1,183,164,112,113,58};','static const unsigned ids[12]={146,147,77,58,182,163,1,183,164,112,113,58};').replace('references[10][REF]','references[12][REF]')
 c=c.replace('enemy_energy_checked=enemy_energy_valid=false;','enemy_energy_checked=enemy_energy_valid=false;enemy_tank_shell_checked=enemy_tank_shell_valid=false;cash25_checked=cash25_valid=cash75_checked=cash75_valid=cash50_checked=cash50_valid=gem100_checked=gem100_valid=gem250_checked=gem250_valid=false;')
 replacements={
 'transaction':r'''static void transaction(unsigned k,int x,int y,bool accepted,bool player,bool shadow,bool reset){begin_area(x,y,reset);unsigned before=original_calls,ends=end_calls,logs=player?player_calls:scene_calls,old_draws=draws;Uint8 *bank=spriteSheet8.data;size_t bank_size=spriteSheet8.size;if(player)draw_entity_sprite2(&screen,x,y,spriteSheet8,ids[k],shadow?ENTITY_SHADOW:ENTITY_NORMAL,ENTITY_TILE);else draw_enemy_shot_sprite2(&screen,x,y,spriteSheet8,ids[k]);assert(original_calls==before+1&&end_calls==ends+1&&draws==old_draws+(unsigned)accepted);assert(!suppress&&!suppress_cloud&&!suppress_green_smoke);assert((player?player_calls:scene_calls)==logs+1&&log_id==ids[k]&&log_x==x&&log_y==y&&log_mirrored==accepted&&log_role==(player?8:k<2?122:k<9?111:108));assert(bank==spriteSheet8.data&&bank_size==spriteSheet8.size);if(accepted)oracle_asset(references[k]+336,x,y,shadow,assets[player?321:k<2?505+k:k<9?462+k-2:218+k-9].density);oracle_original(k,x,y,accepted,shadow);check_area();cases++;accepted_cases+=accepted;fallback_cases+=!accepted;player_cases+=player;if(!(cases%32))check_all();}''',
 'all_seven':r'''static void all_pair(bool accepted){for(unsigned k=0;k<2;k++)transaction(k,94,73,accepted,false,false,true);}''',
 'isolation':r'''static void isolation(void){for(unsigned i=0;i<2;i++){transaction(i,94,73,enemy_tank_shell_valid,false,false,true);transaction(11,94,73,true,true,false,false);transaction(i,94,73,enemy_tank_shell_valid,false,false,false);transaction(11,94,73,true,true,true,false);transaction(i,94,73,false,true,false,true);transaction(i,94,73,false,true,true,true);assert(!get_asset(spriteSheet8,ids[i],ENTITY_TILE));Asset *effect=get_asset(explosionSpriteSheet,ids[i],ENTITY_TILE);assert(effect&&effect->bank==ASSET_EXPLOSION&&effect->index==(int)ids[i]&&effect!=assets+505+i);}for(unsigned k=2;k<11;k++)transaction(k,94,73,true,false,false,true);assert(assets[321].valid&&assets[321].bank==8&&assets[321].index==58);assert(assets[463].valid&&assets[463].bank==111&&assets[463].index==58);assert(gem250_family_ready());for(unsigned k=499;k<=504;k++)assert(assets[k].valid);check_all();}''',
 'test_variants':r'''static void test_variants(void){for(unsigned i=0;i<sizeof(variants)/sizeof(*variants);i++){clear_assets();select_pack(variants[i]);all_pair(false);assert(enemy_tank_shell_checked&&!enemy_tank_shell_valid);isolation();game_probe_assets=full_pack;all_pair(false);}clear_assets();game_probe_assets=full_pack;all_pair(true);select_pack("missing-146");all_pair(true);clear_assets();all_pair(false);clear_assets();game_probe_assets=full_pack;all_pair(true);}''',
 'test_guards':r'''static void test_guards(void){production_end();SDL_Surface other=screen;Sprite2_array wrong={(Uint8*)&other,1},null={NULL,0};for(unsigned k=0;k<2;k++){unsigned id=ids[k];guard(NULL,3,4,spriteSheet8,id);guard(&other,3,4,spriteSheet8,id);guard(&screen,3,4,wrong,id);guard(&screen,3,4,null,id);Sprite2_array save=spriteSheet8;spriteSheet8=null;guard(&screen,3,4,null,id);spriteSheet8=save;VGAScreen=&other;guard(&screen,3,4,spriteSheet8,id);VGAScreen=&screen;SDL_PixelFormat *saved=screen.format;screen.format=NULL;guard(&screen,3,4,spriteSheet8,id);screen.format=saved;format.BitsPerPixel=32;guard(&screen,3,4,spriteSheet8,id);format.BitsPerPixel=8;format.BytesPerPixel=4;guard(&screen,3,4,spriteSheet8,id);format.BytesPerPixel=1;screen.pitch=321;guard(&screen,3,4,spriteSheet8,id);screen.pitch=320;screen.w=319;guard(&screen,3,4,spriteSheet8,id);screen.w=320;screen.h=199;guard(&screen,3,4,spriteSheet8,id);screen.h=200;active=false;guard(&screen,3,4,spriteSheet8,id);active=true;reject_reason="fixture";guard(&screen,3,4,spriteSheet8,id);reject_reason=NULL;const int xy[][2]={{INT_MIN,0},{INT_MAX,0},{0,INT_MIN},{0,INT_MAX},{-1,0},{309,0},{0,-14},{0,200}};for(unsigned j=0;j<sizeof(xy)/sizeof(*xy);j++)guard(&screen,xy[j][0],xy[j][1],spriteSheet8,id);}guard(&screen,3,4,spriteSheet8,145);guard(&screen,3,4,spriteSheet8,UINT_MAX);check_all();}''',
 'diagnostics':r'''static void diagnostics(void){for(unsigned mode=0;mode<4;mode++){clear_assets();game_probe_assets=mode==3?NULL:full_pack;game_probe_missing=mode==0;game_probe_invalid=mode==1;game_probe_original_reference=mode==2;all_pair(false);assert(!enemy_tank_shell_checked);game_probe_missing=game_probe_invalid=game_probe_original_reference=false;}game_probe_assets=full_pack;all_pair(true);game_probe_missing=true;all_pair(false);game_probe_missing=false;game_probe_invalid=true;all_pair(false);game_probe_invalid=false;game_probe_original_reference=true;all_pair(false);game_probe_original_reference=false;all_pair(true);}''',
 'geometry':r'''static void geometry(void){const int xy[][2]={{0,-13},{308,-13},{94,-1},{0,0},{308,0},{94,187},{0,199},{308,199},{-1,73},{309,73},{319,73},{320,73},{94,-14},{94,200}};for(unsigned k=0;k<2;k++)for(unsigned p=0;p<sizeof(xy)/sizeof(*xy);p++)transaction(k,xy[p][0],xy[p][1],p<8,false,false,true);check_all();}''',
 'main':r'''int main(int argc,char **argv){assert(argc==4);full_pack=game_probe_assets=argv[1];work=argv[2];xmas=!strcmp(argv[3],"xmas");char path[2048];size_t bytes;snprintf(path,sizeof(path),"%s/%s",work,xmas?"xmas-bank.bin":"bank.bin");spriteSheet8.data=read_file(path,&bytes);spriteSheet8.size=bytes;snprintf(path,sizeof(path),"%s/%s",work,xmas?"xmas-reference.bin":"reference.bin");void *ref=read_file(path,&bytes);assert(bytes==sizeof(references));memcpy(references,ref,bytes);free(ref);Uint8 tokens[3]={0};spriteSheet9=(Sprite2_array){tokens,1};spriteSheet12=(Sprite2_array){tokens+1,1};explosionSpriteSheet=(Sprite2_array){tokens+2,1};index_storage=malloc(SCREEN+2*PAD);assert(index_storage);memset(index_storage,0xa9,SCREEN+2*PAD);screen.pixels=index_storage+PAD;for(unsigned i=0;i<256;i++)rgb_palette[i]=((i*71)%256)<<16|((i*31)%256)<<8|((i*13)%256);assert(sizeof(assets)/sizeof(*assets)==507);allocate(8);all_pair(true);for(unsigned k=0;k<2;k++){Asset*a=assets+505+k;assert(a->valid&&a->bank==122&&a->index==(int)ids[k]&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y&&a->density==8);assert(!memcmp(a->rgba,references[k]+336,43008));}isolation();test_variants();test_guards();diagnostics();geometry();foreground_shadow();exact_alpha();clear_assets();release();for(int d=1;d<=4;d+=3){allocate(d);game_probe_assets=full_pack;all_pair(false);assert(!enemy_tank_shell_checked);check_all();clear_assets();release();}free(index_storage);free(spriteSheet8.data);printf("{\"status\":\"PASS\",\"transactions\":%u,\"accepted\":%u,\"fallback\":%u,\"player_cases\":%u,\"guard_cases\":%u,\"pixel_comparisons\":%llu,\"full_frame_checks\":%u,\"exact_alpha_cases\":%llu}\n",cases,accepted_cases,fallback_cases,player_cases,guard_cases,(unsigned long long)comparisons,full_comparisons,(unsigned long long)alpha_cases);return 0;}'''
 }
 for name,new in replacements.items():c=c.replace(extract(c,name).strip(),new)
 return c

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);ap.add_argument('--original-data',type=Path);ap.add_argument('--source-only',action='store_true');a=ap.parse_args()
 source,s,m=source_checks();spec=importlib.util.spec_from_file_location('art',ROOT/'prototype/build-enemy-tank-shell-pair-art.py');art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art);source['art']=art.validate()[0]
 if a.source_only:
  print(json.dumps(source,indent=2));return
 assert a.out and a.original_data,'--out and --original-data are required for units';out=a.out.resolve();assert not out.exists() and ROOT not in out.parents and out not in ROOT.parents
 assert os.statvfs(out.parent).f_bavail*os.statvfs(out.parent).f_frsize>4*1024**3+16*1024**2,'4GiB floor plus16MiB unit reserve'
 data=a.original_data.resolve();normal=(data/'tyrian.shp').read_bytes();xmas=(data/'tyrianc.shp').read_bytes()
 assert SHA(normal)=='80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0' and SHA(xmas)=='e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d'
 def bank(raw):
  n=struct.unpack_from('<H',raw)[0];off=list(struct.unpack_from('<'+str(n)+'I',raw,2))+[len(raw)];return raw[off[7]:off[8]]
 bank8=bank(normal);xbank=bank(xmas);assert SHA(bank8)=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
 for i in IDS[:2]:assert old.decode(bank8,i)==old.decode(xbank,i),'Xmas alias differs'
 packs=[ROOT/'assets/hd/packs'/m['default_'+p+'_pack'] for p in ['preview','debug']];names=[f'enemy-tank-shell-{i}-8.hda' for i in IDS[:2]]+[f'enemy-energy-{i}-8.hda' for i in IDS[2:9]]+[f'bullet-{i}-8.hda' for i in IDS[9:]]
 raw={n:(packs[0]/n).read_bytes() for n in names}
 reference=b''.join(old.decode(bank8,i)+raw[n][28:] for i,n in zip(IDS,names));out.mkdir();work=out/'fixtures';work.mkdir();(work/'bank.bin').write_bytes(bank8);(work/'xmas-bank.bin').write_bytes(xbank);(work/'reference.bin').write_bytes(reference);(work/'xmas-reference.bin').write_bytes(b''.join(old.decode(xbank,i)+raw[n][28:] for i,n in zip(IDS,names)))
 unaffected=['explosion-newsh6-146-8.hda','explosion-newsh6-147-8.hda']+names[2:]+[f'gem250-bank11-{i}-8.hda' for i in range(14,19)]+['gem250-value-newsh6-188-8.hda'];variants=[]
 for member in IDS[:2]:
  original=raw[f'enemy-tank-shell-{member}-8.hda'];changes={'missing':None,'magic':b'BAD!'+original[4:],'short-header':original[:27],'truncated':original[:-1],'trailing':original+b'X','rgb':original[:28]+bytes([original[28]^1])+original[29:],'alpha':original[:31]+bytes([original[31]^1])+original[32:]}
  for label,offset,value in [('role',4,80000+member),('id',4,1220000+(147 if member==146 else 146)),('density',8,4),('width',12,11),('height',16,13),('anchor-x',20,1),('anchor-y',24,1)]:bad=bytearray(original);struct.pack_into('<I',bad,offset,value);changes[label]=bytes(bad)
  for label,bad in changes.items():
   name=f'{label}-{member}';variants.append(name);d=work/name;d.mkdir()
   for n in set(unaffected):(d/n).symlink_to(packs[0]/n)
   for i in IDS[:2]:
    n=f'enemy-tank-shell-{i}-8.hda';content=bad if i==member else raw[n]
    if content is not None:(d/n).write_bytes(content)
 # The only4 case changes shell resources only, keeping all legacy families active.
 d=work/'only4';d.mkdir();variants.append('only4')
 for n in set(unaffected):(d/n).symlink_to(packs[0]/n)
 for n in names[:2]:
  rgba=raw[n][28:];hda=raw[n][:8]+struct.pack('<I',4)+raw[n][12:28]+b''.join(rgba[(y*2*96+x*2)*4:(y*2*96+x*2)*4+4] for y in range(56) for x in range(48));(d/n.replace('-8.','-4.')).write_bytes(hda)
 types=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'static Asset assets\[\d+\];',r'static Asset talon_frames\[13\];']
 for family in ['enemy_energy','enemy_tank_shell','cash25','cash75','cash50','gem100','gem250']:types.append(r'static bool '+family+r'_checked,'+family+r'_valid;')
 for family in ['cash25','cash75','cash50','gem100','gem250']:types.append(r'static bool '+family+r'_fixed_value;')
 (out/'types.inc').write_text('\n'.join(re.search(p,s,re.S).group() for p in types));(out/'functions.inc').write_text('\n'.join(extract(s,n) for n in FUNCS));sprite=(ROOT/'src/sprite.c').read_text();entity=(ROOT/'src/entity_draw.c').read_text();(out/'blitters.inc').write_text('\n'.join(extract(sprite,n) for n in ['blit_sprite2','blit_sprite2_darken']));(out/'wrappers.inc').write_text('\n'.join(extract(entity,n) for n in ['draw_enemy_shot_sprite2','draw_entity_sprite2']));(out/'variants.inc').write_text('static const char *variants[]={'+','.join(json.dumps(v) for v in variants)+'};\n');(out/'driver.c').write_text(driver(s))
 command=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(out),str(out/'driver.c'),'-o',str(out/'test')]
 result=subprocess.run(command,capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr);result.check_returncode()
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');results={}
 for label,pack in zip(['preview','debug'],packs):
  for mode in ['normal','xmas']:
   result=subprocess.run([str(out/'test'),str(pack),str(work),mode],capture_output=True,text=True,env=env,timeout=240);(out/f'{label}-{mode}.log').write_text(result.stdout+result.stderr);result.check_returncode();results[f'{label}-{mode}']=json.loads(result.stdout)
 header=(ROOT/'src/render_mirror.h').read_text();macros='\n'.join(re.search(r'^#define '+n+r'\(.*$',header,re.M).group() for n in ['render_mirror_enemy_shot','render_mirror_entity_end'])
 disabled='#include <assert.h>\n#include <stdbool.h>\n#include <stdio.h>\ntypedef int SDL_Surface;typedef int Sprite2_array;static unsigned calls;static void blit_sprite2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){assert(s&&x==3&&y==4&&b==1&&i);calls++;}\n#define RENDER_MIRROR_DISABLED\n'+macros+'\n'+extract(entity,'draw_enemy_shot_sprite2')+'\nint main(void){SDL_Surface s=0;unsigned ids[]={146,147,77,58,182,163,1,183,164,112,113,145};for(unsigned k=0;k<12;k++)draw_enemy_shot_sprite2(&s,3,4,1,ids[k]);assert(calls==12);puts("PASS twelve disabled-build original blits");}\n'
 (out/'disabled.c').write_text(disabled);result=subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(out/'disabled.c'),'-o',str(out/'disabled')],capture_output=True,text=True);(out/'disabled-compile.log').write_text(result.stdout+result.stderr);result.check_returncode();result=subprocess.run([str(out/'disabled')],capture_output=True,text=True);(out/'disabled.log').write_text(result.stdout+result.stderr);result.check_returncode()
 report={**source,'builds':2,'sanitizers':['ASan','UBSan'],'results':results,'disabled':result.stdout.strip(),'resource_variants':variants,'same_damaged_pack_isolation':['seven-energy','orb112/113','player58 normal/shadow','generic player146/147 classic','newsh6 146/147 preserve distinct existing role106','red250 family ready'],'cache':'sticky failures and successes; full fresh slot/flag reset cases','geometry':'x0/308, y-13/199 partial clips; row wraps/extreme coords decline','pixel_oracle':'full canonical RGBA, fractional alpha, later normal/shadow writes, exact original indexed RLE once per wrapper','limitations':['Extracted production proof; no game, actual presentation or native2/4 acceptance.','Unrelated font/material hooks use fail-if-entered or no-op stubs.','LeakSanitizer disabled; ASan/UBSan enabled.'],'function_sha256':{n:SHA(extract(s,n).encode()) for n in FUNCS}}
 assert source_checks()[0]['source_sha256']==source['source_sha256'];(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
