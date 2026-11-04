"""Finite tank shared-owner preparation; no original-data fixture or native run."""
from pathlib import Path
import copy,hashlib,json,re,shutil,struct,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_enemy_tank_shared_aliases as aliases
from current_tank_muzzle_source_bridge import INVERSE,restore
from current_tank194_source_bridge import project_topclip_sources as project_sources,project_topclip_runtime_rows as project_runtime_rows
OLD=(91,145,61,101,120,139,168,169,162,260,166,94,7,45,153,154,155,70,20,21,105,106,124,125,112,113,226,227,244)
PINS={146:'d7c88729cdc18e4fb90a4c46be89681e99b7cdcd43bb6421c639653355109afa',147:'fef0333704fd2afb69fc48a38555e2b892608d590054a9819064cf5cb7fecdbf'}
UNCHANGED={'src/tyrian2.c': '36b756eb60ccad63b76cf194fb9dc3f30dc5c536be07fc9aaa41c971ede48911', 'src/game_probe.c': '1821fc281c91d70a69e5dbcb6cf0292aa3cb57abfc85697e5aee67b17df9b34d', 'src/entity_draw.c': 'e16290b936f6212c7ce3b6a63d758c6b66ec9a0af269ebccd2cac889c83b4529', 'src/global_green_mirror.inc': '7992448caada923a3e7a4fcc59282c4d86603a503b36dc3ac321b1d84131ca60', 'src/global_vulcan_mirror.inc': '7f07c65ae3628e81a6b0c58f322c799fc9678679ed2f1a5619d6a6acfe652c1f', 'src/enemy_reuse_mirror.inc': 'ed4dce9e3183c7d5dd31962217849ecebfa46e3fa23cc5f8afd50bc06cf34858', 'src/enemy_orb_protron_mirror.inc': '08dc1f4df62e5ec7685235bf94a0b78d423a95f3db7e0a7e1f62e55c8ccba6f7', 'src/current_tank_shell_payload_pins.h': 'c474a33b8af08d772113a015fadca77f446cb49626a66bafbf7e24357326e5f6', 'src/global_asset_registry.h': '0c96a8b30482ecc5224e73de98efbb4e2cf5bbaa3478f717bc9118cf86570b69'}
LEGACY_LOADER='b76b417d68f4bd4294002d608f9eee7c3a36b2dcd9add077140ab3da855ba753'
LEGACY_BRANCH='5b45185ff46a2362853dc4ac2c150e408e5144e2abc8a0529c1b2cc9f5cc1abe'
SHARED_FUNCTIONS={'global_projectile91_draw': '5bd2a36e0fe5fa73a6f2430c186d896a9f5c505bbe2b703e8c59683edd7bab07', 'global_projectile91_pre_final_pixel': '00276c11074e6fe478fbabe7fa0a96e9de13db8eb8e54059cc0587d96394779d', 'global_projectile91_final_pixel': '92f062357aa21511d47f978d3e731ff761fd3f823d8dd3c23d721b31aefe8836', 'global_projectile91_final_rect_walk': 'a7336ba5d1d73df8b06e76a31cb0e5038163f3f9a649ac456bb621b0dbdb53f5'}
OLD_ROWS='0cbbff08c9a9128c0c64bfdf7d9fbb12807469ed0bf962e18e042900f396bb18'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def function(source,name):
 start=source.index(name+'(');start=source.index('{',start);end=start+1;depth=1
 while depth:
  depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[start:end]

def reverse_energy_header(raw):
 # Restore only the two selected payload values and their new SHA declarations.
 for identity,new,old in ((1220146,'a9af975b8a495cbd','8a02233c02993d45'),(1220147,'b09ba5d85f40456c','6786d727d8d42fbf')):
  declaration=f'#define CURRENT_TANK_SHELL_{identity}_HDA_SHA256 "{PINS[identity-1220000]}"\n'.encode()
  if raw.count(declaration)!=1:raise ValueError('Missing/duplicate selected SHA pin')
  raw=raw.replace(declaration,b'',1)
  before=f'#define CURRENT_TANK_SHELL_{identity}_PAYLOAD_FNV UINT64_C(0x{new})'.encode()
  after=f'#define CURRENT_TANK_SHELL_{identity}_PAYLOAD_FNV UINT64_C(0x{old})'.encode()
  if raw.count(before)!=1:raise ValueError('Missing/duplicate selected payload pin')
  raw=raw.replace(before,after,1)
 return raw

class TankSharedPreparation(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.body_inventory,cls.body_restored=project_sources(ROOT)
 def source_bytes(self,path):
  return self.body_restored[path]if path in self.body_restored else(ROOT/path).read_bytes()
 def src(self,name):
  path='src/'+name;text=self.source_bytes(path).decode()
  return restore(path,text)if path in INVERSE else text
 def test_append_only31_unsigned(self):
  source=self.src('global_projectile91_mirror.inc');pairs=[(int(a),int(b))for a,b in re.findall(r'index==(\d+)\?(\d+)u',function(source,'global_projectile91_member'))]
  self.assertEqual(pairs,[(i,1<<n)for n,i in enumerate(OLD+(146,147))]);self.assertEqual(sum(b for i,b in pairs),2147483647);self.assertIn('UINT_MAX < 2147483647u',source);self.assertNotIn('1u<<32',source)
 def test_exact_sparse_append_boolean_owners(self):
  source=self.src('global_projectile91_mirror.inc');line=next(l for l in source.splitlines()if l.startswith('static const unsigned global_projectile91_sparse_rgba_members='));self.assertEqual(list(map(int,re.findall(r'(\d+)u',line))),[1<<n for n in range(17,24)]+[1<<27,1<<29,1<<30]);self.assertIn('static Uint8 *global_projectile91_owner',self.src('render_mirror.c'));self.assertNotIn('268435456',line)
 def test_two_exact_canonical_aliases(self):
  for index,pin in PINS.items():
   raw=(ROOT/aliases.canonical_source(index)).read_bytes();self.assertEqual(digest(raw),pin);self.assertEqual(struct.unpack('<4s6I',raw[:28]),(b'HDR1',1220000+index,8,12,14,0,0));self.assertEqual(len(raw),43036);self.assertEqual(raw,(ROOT/(aliases.PREFIX+pin+'.hda')).read_bytes())
 def test_independent_strict_leases(self):
  source=self.src('enemy_tank_shared_mirror.inc')
  for token in ('resources[2]','i<2;i++)free','REAR_REGULAR','REAR_READ(fd,&extra,1)==0','a->bank!=enemy_tank_shared_specs[k].identity/10000u','a->index!=index','a->w!=12||a->h!=14','a->density!=8','strcmp(enemy_tank_shared_resources[k].root,root)','asteroid1_stamp(a->rgba','projectile91_source(bank,91)'):self.assertIn(token,source)
 def test_per_member_palette_not_family_union(self):
  source=self.src('enemy_tank_shared_mirror.inc')
  for index,want in ((146,[49,84,85,86,87,88,89,90,91,93,95]),(147,[49,84,85,86,87,88,89,91,93,95])):
   part=source.split('if(index=='+str(index)+'){',1)[1].split('return true;}',1)[0];actual=list(map(int,re.search(r'indices\[\d+\]=\{([^}]+)',part)[1].split(',')));self.assertEqual(actual,want);self.assertIn('rgb_palette[indices[n]]',part)
 def test_used_resource_and_palette_each_bit(self):
  source=self.src('global_projectile91_mirror.inc')
  for index,bit in ((146,536870912),(147,1073741824)):
   self.assertIn(f'(!(global_projectile91_used_members&{bit}u)||enemy_tank_shared_palette_matches({index}))',source);self.assertIn(f'(!(global_projectile91_used_members&{bit}u)||(tank_shared_ordinary_allowed({index})&&enemy_tank_shared_resource(global_asset_directory,{index})!=NULL))',source)
 def test_resource_intent_not_generic_debug_flag(self):
  policy=self.src('enemy_tank_shared_policy.h');body=function(policy,'tank_shared_legacy_intent');self.assertEqual(body,'{return game_probe_assets!=NULL||widget_sonic_legacy_intent();}');self.assertIn('return game_probe_enabled||enemy_reuse_observe_requested()||enemy_reuse_probe_requested();',self.src('enemy_widget_sonic_policy.h'))
 def test_global_failure_does_not_fall_through_legacy(self):
  render=self.src('render_mirror.c');part=render.split('if(tank_shared_member_index(index)&&global_asset_directory[0]&&tank_shared_ordinary_allowed(index)) {',1)[1].split('}',1)[0];self.assertIn('return global_projectile91_draw(surface,x,y,bank,index)>0;',part);self.assertLess(render.index('if(tank_shared_member_index(index)&&'),render.index(' if(index==146||index==147) {'))
 def test_old_gameplay_and_player_files_exact(self):
  pins=UNCHANGED
  for path,pin in pins.items():
   raw=self.source_bytes(path)
   if path in INVERSE:raw=restore(path,raw.decode()).encode()
   if path=='src/current_tank_shell_payload_pins.h':raw=reverse_energy_header(raw)
   self.assertEqual(digest(raw),pin,path)
 def test_energy_header_inverse_rejects_missing_duplicate_and_unrelated(self):
  raw=(ROOT/'src/current_tank_shell_payload_pins.h').read_bytes();line=f'#define CURRENT_TANK_SHELL_1220146_HDA_SHA256 "{PINS[146]}"\n'.encode()
  for bad in (raw.replace(line,b'',1),raw+line):
   with self.assertRaises(ValueError):reverse_energy_header(bad)
  self.assertNotEqual(digest(reverse_energy_header(raw+b'\n')),UNCHANGED['src/current_tank_shell_payload_pins.h'])
 def test_original_legacy_loader_and_branch_exact(self):
  render=self.src('render_mirror.c');start=render.index('static bool enemy_tank_shell_checked,enemy_tank_shell_valid;');end=render.index('\n#if defined(ENEMY_REUSE_HD_PROTOTYPE)',start);self.assertEqual(digest(render[start:end].encode()),LEGACY_LOADER)
  start=render.index(' if(index==146||index==147) {');end=render.index('\n int energy_slot=',start);self.assertEqual(digest(render[start:end].encode()),LEGACY_BRANCH)
 def test_shared_renderer_and_prefinal_fix_exact(self):
  source=self.src('global_projectile91_mirror.inc')
  for name,pin in SHARED_FUNCTIONS.items():self.assertEqual(digest(function(source,name).encode()),pin,name)
 def test_old_package_rows_unchanged_except_binding(self):
  rows=project_runtime_rows(ROOT,json.loads((ROOT/'packaging/runtime-assets-v1.json').read_bytes()));old=[r for r in rows if r.get('revision')!=aliases.REVISION and r['source_path']!='packaging/current-production-validation.json'];self.assertEqual(len(old),1128)
  for index,oldsha,oldblob in ((146,'18cbd40ee58fb30f19c6447d9e144a682ff25f26080c9fd85238447c2071d196','7f1215d5d6980014b7c59fd724ae69cd25c91b76'),(147,'4bc2df967eff050ef7823eacd130b7c924fc2a72b60d6a7288460595866c90da','b706c69c2cfb4e1d9ec61a5404368491cbaedf78')):
   matches=[r for r in old if r['source_path']==aliases.canonical_source(index)];self.assertEqual(len(matches),1);row=matches[0];raw=(ROOT/row['source_path']).read_bytes()
   self.assertEqual(digest(raw),PINS[index]);self.assertEqual(row['sha256'],PINS[index]);self.assertEqual(row['git_blob'],hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest());self.assertEqual(row['bytes'],43036)
   row['sha256']=oldsha;row['git_blob']=oldblob
  self.assertEqual(digest(json.dumps(old,sort_keys=True,separators=(',',':')).encode()),OLD_ROWS)

class TankAliasValidation(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  for index,pin in PINS.items():
   for name in (aliases.canonical_source(index),aliases.PREFIX+pin+'.hda'):
    q=self.root/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,q)
  import current_tank_shell_compatibility as compatibility
  selected=json.loads((ROOT/compatibility.SELECTION).read_bytes())
  for name in (compatibility.SELECTION,compatibility.MAPPING,compatibility.HEADER,*[r['source_png']for r in selected['resources']]):
   q=self.root/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,q)
  self.rows=aliases.rows_for(self.root)
 def check(self,rows=None,required=True):return aliases.validate_runtime_rows(self.root,{'files':self.rows if rows is None else rows},required)
 def test_valid_and_deterministic(self):
  self.check();self.assertEqual(aliases.generate(self.root),aliases.generate(self.root));self.assertEqual(self.rows,aliases.rows_for(self.root))
 def test_missing_duplicate_extra(self):
  for rows in (self.rows[:1],self.rows+[self.rows[0]],self.rows+[dict(self.rows[0],destination='assets/global/content/extra.hda')]):
   with self.subTest(rows=len(rows)),self.assertRaises(ValueError):self.check(rows)
 def test_optional_absent_and_required_absent(self):
  self.check([],False)
  with self.assertRaises(ValueError):self.check([])
 def test_metadata_missing_wrong_boolean(self):
  for key in ('identity','density','encoding','canonical_source','revision','source_path','destination','sha256','bytes','git_blob'):
   for value in (None,True,'wrong'):
    rows=copy.deepcopy(self.rows)
    if value is None:del rows[0][key]
    else:rows[0][key]=value
    with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.check(rows)
 def test_alias_corruption_and_missing(self):
  path=self.root/self.rows[0]['source_path'];raw=path.read_bytes();path.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
  with self.assertRaises(ValueError):self.check()
  path.unlink()
  with self.assertRaises(ValueError):self.check()
 def test_canonical_corruption(self):
  path=self.root/aliases.canonical_source(146);path.write_bytes(b'bad')
  with self.assertRaises(ValueError):self.check()
 def test_hidden_identity_collision(self):
  hidden=self.root/'hidden.hda';hidden.write_bytes((self.root/aliases.canonical_source(146)).read_bytes())
  with self.assertRaises(ValueError):self.check(self.rows+[{'source_path':'hidden.hda','destination':'assets/other.hda'}])
 def test_manual_rows_remain_original_contract(self):
  original=json.loads((ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files'];manual=[r for r in original if r['source_path']in aliases.CANONICAL_SOURCES.values()];self.assertEqual(len(manual),2);self.check(self.rows+manual)
  bad=copy.deepcopy(manual);bad[0]['identity']=1220146
  with self.assertRaises(ValueError):self.check(self.rows+bad)

if __name__=='__main__':unittest.main()
