"""Cheap finite source/art-contract tests; not a compiled runtime or live scene proof."""
import hashlib,json,pathlib,re,struct,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
SHA='eebd525dab58f0fc6708f4f3c7b15a88e67270be877ff250e93c4bb2a2aeb8de'
PATH='assets/hd/current-compat/vulcan/bullet-70-8.hda'
CONTENT='assets/hd/global-assets-v1/content/'+SHA+'.hda'
OLD_IDS=(91,145,61,101,120,139,168,169,162,260,166,94,7,45,153,154,155)
PINNED_UNCHANGED={'src/global_vulcan_mirror.inc': '7f07c65ae3628e81a6b0c58f322c799fc9678679ed2f1a5619d6a6acfe652c1f', 'src/global_asset_registry.h': '0c96a8b30482ecc5224e73de98efbb4e2cf5bbaa3478f717bc9118cf86570b69', 'src/shared_asset_reader.h': '570ef567a70dd21f8fe0f0e8a8f6edba1e4949fcc03278d28c1d68abc442e82c', 'src/shots.c': 'c73b31130db3d8ee672aa2bcd1c702bc833a808a373e5670dd3a954816a56356', 'src/enemy_bolts745_mirror.inc': '5d45588a0ca92650daa90e42ee625505804ef2384ac9837b10a4c72e382f6c4f', 'src/enemy_animated153_mirror.inc': 'ce3635dfcc7dbd6818bb2f32dc136a1bc2559c325f42eef83ae23f71587840ae', 'assets/hd/current-compat/vulcan/bullet-67-8.hda': '96b975abbccf393464cf2444f72d63c8ad3f996d8cc5c153593ad16f476e30e0', 'assets/hd/current-compat/vulcan/bullet-70-8.hda': 'eebd525dab58f0fc6708f4f3c7b15a88e67270be877ff250e93c4bb2a2aeb8de'}
RLE=bytes.fromhex('147511750553757c767c750453767b777b760453787a787a780453767976797604537478757874045374777477740453737573757304537273727372041472117205147111710f')
def source70():
 mask=[0]*168;indices=[0]*168;p=o=0
 while RLE[o]!=15:
  c=RLE[o];o+=1;p+=c&15;n=c>>4
  for k in range(n):mask[p+k]=1;indices[p+k]=RLE[o+k]
  o+=n;p+=n
 if o+1!=len(RLE):raise ValueError('Trailing source RLE')
 return mask,indices
def function(text,name):
 start=text.index(name+'(');start=text.rfind('\n',0,start)+1;op=text.index('{',start);depth=0
 for end in range(op,len(text)):
  depth+=(text[end]=='{')-(text[end]=='}')
  if not depth:return text[start:end+1]
 raise ValueError('Unclosed C function')
class EnemyVulcan70Preparation(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.loader=(ROOT/'src/enemy_vulcan70_mirror.inc').read_text();cls.shared=(ROOT/'src/global_projectile91_mirror.inc').read_text();cls.render=(ROOT/'src/render_mirror.c').read_text()
 def test_canonical_bytes_unmodified_both_locations(self):
  self.assertEqual((ROOT/PATH).read_bytes(),(ROOT/CONTENT).read_bytes());self.assertEqual(hashlib.sha256((ROOT/PATH).read_bytes()).hexdigest(),SHA)
 def test_exact_header_no_new_namespace(self):
  raw=(ROOT/PATH).read_bytes();self.assertEqual(len(raw),43036);self.assertEqual(struct.unpack('<4s6I',raw[:28]),(b'HDR1',80070,8,12,14,0,0));self.assertIn('(Asset){true,true,8,70,12,14,0,0,8,rgba}',self.loader)
 def test_actual_source70_mask_and_indices(self):
  mask,indices=source70();self.assertEqual(sum(mask),46);self.assertEqual(set(v for v,m in zip(indices,mask)if m),set(range(113,125)));self.assertEqual(hashlib.sha256(bytes(mask)).hexdigest(),'f5417b23bf6bbaa627fbc125d739081fc35378ad4487317091595f8f922411cc')
 def test_exact_halo_fractional_contract_not_mask_clipped(self):
  mask,_=source70();rgba=(ROOT/PATH).read_bytes()[28:];nz=soft=halo=0;union=0
  for n in range(10752):
   a=rgba[n*4+3];native=mask[(n//96//8)*12+(n%96)//8];nz+=a>0;soft+=0<a<255;halo+=bool(a and not native);union+=bool(a or native)
  self.assertEqual((nz,soft,halo,union),(2674,400,110,46*64+110))
 def test_palette_gate_is_exact_twelve_live_colors(self):
  f=function(self.loader,'enemy_vulcan70_palette_matches');colors=[int(x,16)for x in re.findall(r'0x[0-9a-f]{6}(?![0-9a-f])',f.split('colors[12]={',1)[1].split('};',1)[0])]
  self.assertEqual(colors,[0x380000,0x510000,0x6d0400,0x860400,0x9e0800,0xba0c00,0xd31400,0xdf3c00,0xe7610c,0xeb8a18,0xf3ae24,0xfbcb30]);self.assertIn('rgb_palette[113+i]',f);self.assertNotIn('episodeNum',f);self.assertNotIn('lvlFileNum',f)
 def test_append_only_18bit_members(self):
  pairs=[(int(a),int(b))for a,b in re.findall(r'index==(\d+)\?(\d+)u',function(self.shared,'global_projectile91_member'))]
  self.assertEqual(pairs,[(i,1<<k)for k,i in enumerate((*OLD_IDS,70))]);self.assertEqual(sum(x[1]for x in pairs[:17]),131071);self.assertEqual(sum(x[1]for x in pairs),262143)
 def test_width_guard_rejects_17bit_counterexample(self):
  self.assertEqual(131071&131072,0);self.assertIn('#if UINT_MAX < 262143u',self.shared);self.assertIn('at least 18 unsigned value bits',self.shared)
 def test_independent_lease_not_player_cache(self):
  self.assertIn('enemy_vulcan70_resource_state',self.loader);self.assertNotIn('global_vulcan_rgba',self.loader);self.assertNotIn('global_vulcan_family_ready',self.loader);self.assertNotIn('global_vulcan_front',self.loader)
 def test_player_and_existing_indexed_loaders_unchanged(self):
  for p,pin in PINNED_UNCHANGED.items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),pin,p)
 def test_full_bank_and_enemy_only_route(self):
  self.assertIn('return index==70&&projectile91_source(bank,91);',self.loader);self.assertIn('||index==153||index==154||index==155||index==70)',function(self.render,'render_mirror_enemy_shot'))
  entity=(ROOT/'src/entity_draw.c').read_text();self.assertIn('game_probe_scene_draw(8,index,x,y,0,ENTITY_NORMAL,mirrored);',function(entity,'draw_enemy_shot_sprite2'))
 def test_rgba_not_indexed_dispatch(self):
  f=function(self.shared,'global_projectile91_draw');self.assertIn('}else *p=blend_rgba(*p,a,(int)alpha);',f);self.assertNotIn('index==70',f);self.assertIn('if(!a[3]&&!native)continue;',f)
 def test_warm_payload_geometry_and_root_checks(self):
  f=function(self.loader,'enemy_vulcan70_resource')
  for token in ('strcmp(enemy_vulcan70_resource_state.root,root)','a->bank!=8','a->index!=70','a->w!=12','a->h!=14','a->anchor_x','a->anchor_y','a->density!=8','asteroid1_stamp(a->rgba,','enemy_vulcan70_payload_pin'):self.assertIn(token,f)
 def test_resource_header_regular_eof_and_pin(self):
  f=function(self.loader,'enemy_vulcan70_load')
  for token in ('v[0]==80070&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5]','REAR_REGULAR','st_size==(long)(28+bytes)','REAR_READ(fd,&extra,1)==0','asteroid1_stamp(rgba,bytes)==enemy_vulcan70_payload_pin','if(REAR_CLOSE(fd))ok=false;'):self.assertIn(token,f)
 def test_used_dependencies_and_shutdown_are_finite(self):
  self.assertIn('(!(global_projectile91_used_members&131072u)||enemy_vulcan70_palette_matches())',self.shared);self.assertIn('(!(global_projectile91_used_members&131072u)||enemy_vulcan70_resource(global_asset_directory)!=NULL)',self.shared);self.assertIn('enemy_vulcan70_shutdown();',self.shared)
if __name__=='__main__':unittest.main()
