"""Finite pure preparation checks; no compiler/native/game, no original raw embeds."""
import importlib.util,pathlib,struct,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'tests/tank_shell_native_validation.py';spec=importlib.util.spec_from_file_location('tank_native',p);n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
class Adapter(unittest.TestCase):
 def inputs(self):
  h={i:bytes([i%256])*43036 for i in n.IDS if i not in n.CANONICAL};names={i:f'fixture-{i}.hda'for i in h}
  for i,pin in n.CANONICAL.items():names[i]='content/'+pin+'.hda';h[i]=(ROOT/'assets/hd/global-assets-v1'/names[i]).read_bytes()
  return h,{i:n.sha(b)for i,b in h.items()},names
 def test_inventory75_31direct_and_sparse8_green4(self):
  self.assertEqual(sum(n.CASE_INVENTORY.values()),75);self.assertEqual(n.CASE_INVENTORY['current31_full_oracles'],31);self.assertEqual(n.CASE_INVENTORY['two_highbits_real_Green_retirement_pixel_rect_normal_fade'],8);self.assertEqual(n.CASE_INVENTORY['retained_original_Green_prehook_cases'],4);self.assertEqual(len(n.IDS),43);self.assertEqual(len(n.PACKS),7)
 def test_source_bundle_reversible_and_old_entry_preserved(self):
  sources,raw=n.source_bundle(ROOT);prior=n.reverse_shim(raw,ROOT);self.assertEqual(len(sources),17);self.assertEqual(n.outer_shim(prior,ROOT),raw);self.assertIn(b'--protron244',prior);self.assertEqual(prior,n.green_helper(ROOT).source_bundle(ROOT)[1]);self.assertEqual(raw.count(b'int main('),1)
 def test_modified_entry_or_helper_rejected(self):
  for b in (b'',b'int main(){}',b'x'+n.TAIL):
   with self.assertRaises(ValueError):n.outer_shim(b,ROOT)
   with self.assertRaises(ValueError):n.reverse_shim(b,ROOT)
  with tempfile.TemporaryDirectory()as d:
   root=pathlib.Path(d);(root/'tests').mkdir();(root/'tests/player_green_cache_fix_native_validation.py').write_text('raise RuntimeError("injection must not execute")')
   with self.assertRaises(ValueError):n.green_helper(root)
 def test_exact53_fixtures_no_unrelated_faultpack_bytes(self):
  h,pins,names=self.inputs();out=n.fixture_payloads(h,pins,names);self.assertEqual(len(out),53)
  for i in n.IDS:self.assertEqual(out['tank-shared-packs/valid/'+names[i]],h[i])
  for leaf in n.PACKS[1:]:
   members=[p for p in out if p.startswith('tank-shared-packs/'+leaf+'/')];self.assertEqual(len(members),1 if leaf.startswith('missing')else 2)
   for i in n.NEW_IDS:
    if str(i)not in leaf:self.assertEqual(out['tank-shared-packs/'+leaf+'/'+names[i]],h[i])
 def test_identity_headers_and_payload_changes(self):
  h,pins,names=self.inputs();out=n.fixture_payloads(h,pins,names)
  for i in n.NEW_IDS:
   self.assertEqual(struct.unpack('<4s6I',h[i][:28]),(b'HDR1',1220000+i,8,12,14,0,0));bad=out[f'tank-shared-packs/header{i}/'+names[i]];self.assertEqual(struct.unpack('<I',bad[4:8])[0],80000+i);self.assertEqual(bad[28:],h[i][28:]);self.assertNotEqual(out[f'tank-shared-packs/bad{i}/'+names[i]],h[i])
 def test_membership_boolean_path_and_corruption_rejected(self):
  h,pins,names=self.inputs()
  for path in ('../bad.hda','/bad.hda','content/renamed.hda'):
   other=dict(names);other[146]=path
   with self.assertRaises(ValueError):n.fixture_payloads(h,pins,other)
  other=dict(h);other.pop(67)
  with self.assertRaises(ValueError):n.fixture_payloads(other,pins,names)
  other=dict(h);other[146]=bytes(43036)
  with self.assertRaises(ValueError):n.fixture_payloads(other,pins,names)
 def test_input_requires_caller_original_bytes(self):
  with self.assertRaises(ValueError):n.native_input(b'',b'',b'')
  self.assertEqual(n._green.RECORD_OFFSETS,(26868,92388));s=(ROOT/'tests/tank_shell_native_additions.c.inc').read_text();self.assertNotIn('bytes.fromhex',s);self.assertNotIn('static const Uint8 original',s)
 def test_alpha_retirement_preconditions_from_actual_hd(self):
  h,_,_=self.inputs();green=h[80214][28:]
  def cells(q,c):return {(y,x)for y in range(8)for x in range(8)if q[4*((c//12*8+y)*96+c%12*8+x)+3]}
  t=cells(h[146][28:],28);g=cells(green,8)
  self.assertEqual((len(t),len(g)),(2,22));self.assertLessEqual(t,g)
  self.assertEqual(sum(1<<(y*8+x) for y,x in t),0x8080000000000000)
  self.assertEqual(sum(1<<(y*8+x) for y,x in g),0xc0f0f0830f1e0400)
  # 147 has 49 alpha texels in cell39, Green15 has30; each native mask
  # owns the entire64. Do NOT call alpha-only sets a proof of full retirement.
  # Actual caller-bank C assertions independently prove full64 -> full64.
  self.assertEqual((len(cells(h[147][28:],39)),len(cells(green,15))),(49,30))
  for i,nz,soft in ((146,1487,1487),(147,1855,1855)):
   a=h[i][31::4];self.assertEqual(sum(v>0 for v in a),nz);self.assertEqual(sum(0<v<255 for v in a),soft)
  c=(ROOT/'tests/tank_shell_native_additions.c.inc').read_text()
  self.assertIn('tc[2]={28,39},gcells[2]={8,15},before_count[2]={2,64},after_count[2]={22,64}',c)
 def test_energy46_explicit_dispatch_retains_old75_and_exact_focused_scope(self):
  self.assertEqual(sum(n.ENERGY_CASE_INVENTORY.values()),46)
  self.assertEqual(n.ENERGY_CASE_INVENTORY['current_two_energy_full_oracles'],2)
  self.assertNotIn('current31_full_oracles',n.ENERGY_CASE_INVENTORY)
  self.assertEqual({k:v for k,v in n.ENERGY_CASE_INVENTORY.items() if k!='current_two_energy_full_oracles'}, {k:v for k,v in n.CASE_INVENTORY.items() if k!='current31_full_oracles'})
  self.assertIn(b'--tank-energy',n.TAIL);self.assertIn(b'--tank-shared',n.TAIL)
  c=(ROOT/'tests/tank_shell_native_additions.c.inc').read_text()
  self.assertIn('if(energy)tk_direct2();else tk_direct31();',c)
  self.assertIn('CHECK(cases-initial==46)',c);self.assertIn('CHECK(cases-initial==75)',c)
  direct=c.split('static void tk_direct2(void)',1)[1].split('static void tk_direct31',1)[0]
  self.assertNotIn('p244_direct29',direct)
  self.assertIn('if(a>0&&a<255&&!mask[n/96/8*12+n%96/8])soft=n;',c)
 def test_exact_tank_additive_inverse(self):
  raw=(ROOT/'src/render_mirror.c').read_bytes();self.assertEqual(n.sha(n.reverse_tank_render(raw)),n.RENDER_BASE_SHA)
  for addition in n.TANK_RENDER_ADDITIONS:
   for bad in (raw.replace(addition.encode(),b'',1),raw+addition.encode()):
    with self.assertRaises(ValueError):n.reverse_tank_render(bad)
  with self.assertRaises(ValueError):n.reverse_tank_render(raw+b'\n')
 def test_tiny_actual_production_bodies_and_policy_v2(self):
  raw,pins=n.tiny_sources(ROOT);text=raw.decode();self.assertEqual(len(pins),10);self.assertIn('assert(cases==320)',text);self.assertIn('assets_state<4',text);self.assertIn('enemy_tank_shared_policy.h',text)
  extract=n._old.old_helper(ROOT).function
  for file,fn in (('render_mirror.c','render_mirror_enemy_shot'),('global_projectile91_mirror.inc','global_projectile91_source_matches'),('global_projectile91_mirror.inc','global_projectile91_check_cache')):self.assertIn(extract((ROOT/'src'/file).read_text(),fn),text)
  header=(ROOT/'src/enemy_tank_shared_policy.h').read_text();self.assertIn('return game_probe_assets!=NULL||widget_sonic_legacy_intent();',header);self.assertNotIn('return game_probe_enabled||',header)
  for path,pin in pins.items():self.assertEqual(n.sha((ROOT/path).read_bytes()),pin)
 def test_native_real_allocator_fade_retirement_and_no_old_fault_dispatch(self):
  s=(ROOT/'tests/tank_shell_native_additions.c.inc').read_text()
  for needle in ('player_shot_move_and_draw(', 'CHECK(!sc&&gc==after_count[k]&&hc==gc)','global_projectile91_used_members==(536870912u<<k)','render_mirror_fade_step(7)','CHECK(!render_mirror_present','tk_recover(k,ex,ey)','for(unsigned m=0;m<4;m++)pg_case(m)','CHECK(cases-initial==75)'):self.assertIn(needle,s)
  self.assertNotIn('p244_main(',s);self.assertNotIn('op_main(',s);self.assertNotIn('global_green_owner[n]=',s);self.assertNotIn('global_projectile91_owner[n]=',s)
if __name__=='__main__':unittest.main()
