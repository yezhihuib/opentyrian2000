"""Pure portable adapter checks, never compiler/native/game or fixture writes."""
import importlib.util,json,pathlib,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'tests/player_green_cache_fix_native_validation.py';spec=importlib.util.spec_from_file_location('pg_cache_native',p);n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
class Adapter(unittest.TestCase):
 def materials(self):return {i:(ROOT/'assets/hd/global-assets-v1/content'/(pin+'.hda')).read_bytes()for i,pin in n.ASSETS.items()}
 def sources(self):return ((ROOT/'src/render_mirror.c').read_text(),(ROOT/'src/global_projectile91_mirror.inc').read_text())
 def test_inventory_and_real_routes(self):
  self.assertEqual(sum(n.CASE_INVENTORY.values()),4);self.assertEqual(n.RETAINED_SETUP_COUNT,56);s=n.companion(ROOT);self.assertIn(b'player_shot_create(',s);self.assertIn(b'player_shot_move_and_draw(',s);self.assertIn(b'inherited_p244_diagnostic_dispatch(argc,argv)',s);self.assertNotIn(b'render_mirror_green_trail_begin(',s)
 def test_bundle_and_exact_reverse(self):
  sources,raw=n.source_bundle(ROOT);old=n.reverse_shim(raw,ROOT);self.assertEqual(len(sources),16);self.assertEqual(n.outer_shim(old,ROOT),raw);self.assertEqual(raw.count(b'int main('),1)
  for name in n.COMPANIONS:self.assertEqual(sources[name],(ROOT/'tests'/name).read_bytes())
 def test_changed_dispatch_rejected(self):
  _,raw=n.source_bundle(ROOT)
  for bad in (b'',raw+b'!',raw.replace(b'inherited_p244_diagnostic_dispatch(',b'wrong(',1)):
   with self.assertRaises(ValueError):n.reverse_shim(bad,ROOT)
  with self.assertRaises(ValueError):n.outer_shim(b'int main(){}',ROOT)
 def test_injected_helper_rejected_before_execution(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'tests').mkdir();(root/'tests/protron244_native_validation.py').write_text('raise RuntimeError("must not execute")')
   with self.assertRaisesRegex(ValueError,'inherited adapter'):n.p244_helper(root)
 def test_original_input_contract_rejects_wrong_bytes_and_types(self):
  for args in ((b'',b'',b''),(bytearray(),b'',b''),(b'',bytes(152000),bytes(17810))):
   with self.assertRaises(ValueError):n.native_input(*args)
  self.assertEqual(n.RECORD_OFFSETS,(26868,92388));j=json.loads((ROOT/'assets/hd/global-assets-v1/registry.json').read_text());f=next(x for x in j['families']if x['name']=='green-energy-head-and-trail')
  rows=f['source_identity']['weapon_records'];self.assertEqual([r['packed_index']for r in rows],[71,890]);self.assertEqual(tuple(r['variants'][0]['offset']for r in rows),n.RECORD_OFFSETS);self.assertTrue(all(r['variants'][0]['record_sha256']==n.RECORD_SHA for r in rows))
 def test_exact12_canonical_payloads(self):
  h=self.materials();out=n.green_payloads(h);self.assertEqual(len(out),12)
  for i,b in h.items():self.assertEqual(out['content/'+n.ASSETS[i]+'.hda'],b)
 def test_material_membership_and_corruption_rejected(self):
  h=self.materials();bad=[];q=dict(h);q.pop(80214);bad.append(q);q=dict(h);q[123]=q[80214];bad.append(q);q=dict(h);q[80214]=q[80214][:-1]+b'!';bad.append(q);q=dict(h);q[True]=q.pop(80214);bad.append(q)
  for q in bad:
   with self.assertRaises(ValueError):n.green_payloads(q)
 def test_actual_preentry_predicate_and_clip_contract(self):self.assertTrue(n.validate_source_contract(*self.sources()))
 def test_delayed_or_missing_preentry_rejected(self):
  mirror,shared=self.sources()
  for call in ('global_projectile91_pre_final_pixel(surface,address);','global_projectile91_pre_final_rect(s,rect);'):
   for changed in (mirror.replace(call,'',1),mirror.replace(call,'data_frame_rect(s,rect);'+call,1)):
    with self.assertRaises(ValueError):n.validate_source_contract(changed,shared)
 def test_predicate_clip_surface_guard_negative(self):
  mirror,shared=self.sources()
  for old,new in [('shared_count<(unsigned)(d*d)','shared_count<(unsigned)(d*d-1)'),('right=MIN(MIN(right,','right=MAX(MIN(right,'),('!global_projectile91_final_surface_matches()))return;','false))return;')]:
   self.assertIn(old,shared)
   with self.assertRaises(ValueError):n.validate_source_contract(mirror,shared.replace(old,new,1))
if __name__=='__main__':unittest.main()
