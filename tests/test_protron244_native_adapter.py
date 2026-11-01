"""Pure finite adapter preparation; no compiler/native/game execution."""
import importlib.util,pathlib,struct,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'tests/protron244_native_validation.py';spec=importlib.util.spec_from_file_location('p244_native',p);n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
class Adapter(unittest.TestCase):
 def inputs(self):
  h={i:bytes([i%256])*43036 for i in n.IDS if i not in n.CANONICAL};names={i:f'fixture-{i}.hda'for i in h}
  for i,pin in n.CANONICAL.items():names[i]='content/'+pin+'.hda';h[i]=(ROOT/'assets/hd/global-assets-v1'/names[i]).read_bytes()
  return h,{i:n.sha(b)for i,b in h.items()},names
 def test_inventory_exact56(self):
  self.assertEqual(sum(n.CASE_INVENTORY.values()),56);self.assertEqual(n.CASE_INVENTORY['current29_complete_oracles'],29);self.assertEqual(len(n.IDS),30);self.assertEqual(len(n.PACKS),4);self.assertIn('Green excluded',n.MACRO_ON_PIXEL_SCOPE)
 def test_eleven_dispatches_reversible(self):
  sources,wrapped=n.source_bundle(ROOT);old=n.reverse_shim(wrapped,ROOT);self.assertEqual(len(sources),6);self.assertEqual(n.outer_shim(old,ROOT),wrapped);self.assertIn(b'--orb-protron',old);self.assertNotIn(b'--protron244',old)
 def test_bad_dispatches_fail_closed(self):
  for raw in (b'',b'int main(){}',b'x'+n.TAIL):
   with self.assertRaises(ValueError):n.outer_shim(raw,ROOT)
   with self.assertRaises(ValueError):n.reverse_shim(raw,ROOT)
 def test_fixture119_old29_unchanged(self):
  h,pins,names=self.inputs();out=n.fixture_payloads(h,pins,names);self.assertEqual(len(out),119)
  for leaf in n.PACKS:
   for i in n.OLD_IDS:self.assertEqual(out['protron244-packs/'+leaf+'/'+names[i]],h[i])
  self.assertNotIn('protron244-packs/missing244/'+names[244],out)
 def test_material_pin_identity_and_wrong_material(self):
  h,_,_=self.inputs();self.assertEqual(struct.unpack('<4s6I',h[244][:28]),(b'HDR1',80244,8,12,14,0,0));bad=n.fixture_bytes(h[244],244,'bad244',h[227]);self.assertEqual(struct.unpack('<I',bad[4:8])[0],80244);self.assertEqual(bad[28:],h[227][28:]);self.assertNotEqual(bad[28:],h[244][28:]);self.assertEqual(struct.unpack('<I',n.fixture_bytes(h[244],244,'header244')[4:8])[0],1470244)
 def test_only244_mutations(self):
  h,_,_=self.inputs()
  for leaf in n.PACKS:self.assertEqual(sum(n.fixture_bytes(h[i],i,leaf,h[227])!=h[i]for i in n.IDS),0 if leaf=='valid'else 1)
 def test_paths_membership_boolean_and_unpinned_input_rejected(self):
  h,pins,names=self.inputs()
  for name in ('../bad.hda','/bad.hda','content/renamed.hda'):
   q=dict(names);q[244]=name
   with self.assertRaises(ValueError):n.fixture_payloads(h,pins,q)
  q=dict(h);q.pop(67)
  with self.assertRaises(ValueError):n.fixture_payloads(q,pins,names)
  with self.assertRaises(ValueError):n.fixture_bytes(bytes(43036),True,'valid')
  with self.assertRaises(ValueError):n.native_input(bytes(99142),b'')
 def test_pinned_original97_cells_and_zero_halo(self):
  rle=bytes.fromhex('0c5382838382810472838889898783810391828a8c8c8c8b87818102b080868c8e8f8e8c8a85818401b080888c8f8f8f8c8b86838501b081878c8e8f8e8c8a86848701b081848b8c8c8c8a8884898901b08281868989898784888c8b0191838185868484888d8b0272848283888c8d8b0353888a8d8c8b0f');self.assertEqual(n.sha(rle),'ea34efd52444ed3a95f60951b0b98d004662ab595021ebcd4aac55d3fca9e2db');mask=[0]*168;offset=pos=0;colors=set()
  while rle[offset]!=15:
   c=rle[offset];offset+=1;pos+=c&15;count=c>>4
   for k in range(count):mask[pos+k]=1;colors.add(rle[offset+k])
   offset+=count;pos+=count
  self.assertEqual(n.sha(bytes(mask)),'d06bc1ca3bf019d538ab0f7acb77cb5dcd8e915a6c1124e93801a416826a6d99');self.assertEqual(colors,set(range(128,144)));h,_,_=self.inputs();rgba=h[244][28:];nz=soft=halo=zero=0
  for z in range(10752):
   a=rgba[z*4+3];native=bool(mask[z//96//8*12+z%96//8]);nz+=a>0;soft+=0<a<255;halo+=bool(a and not native);zero+=native and not a
  self.assertEqual((sum(mask),nz,soft,halo,zero),(97,6056,6056,0,152))
 def test_actual_source_tiny_and_green_exclusion(self):
  raw,pins=n.tiny_sources(ROOT);self.assertEqual(len(pins),7);self.assertIn(b'unsigned ids[5]={112,113,226,227,244}',raw);self.assertIn(b'assert(cases==384)',raw);self.assertIn(b'global_projectile91_member(prior[j])==0',raw);self.assertIn(b'Asset *a=&assets[218+(int)index-112];',raw);self.assertIn(b'orb_protron_ordinary_allowed(244)',raw);self.assertIn(b'Green excluded',raw)
  for p,pin in pins.items():self.assertEqual(n.sha((ROOT/p).read_bytes()),pin)
 def test_main_no_historical_matrix_or_green_scope(self):
  raw=(ROOT/'tests/protron244_native_additions.c.inc').read_text();self.assertIn('op_direct28();',raw);self.assertNotIn('op_main(',raw);self.assertIn('CHECK(cases-initial==56)',raw);self.assertIn('render_mirror_fade_step(7)',raw);self.assertIn('global_projectile91_sparse_rgba_members&268435456u',raw);self.assertNotIn('global_vulcan_slots[0].role=true',raw)
if __name__=='__main__':unittest.main()
