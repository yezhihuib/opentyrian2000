"""Cheap preparation checks only; never compiler/native/game execution."""
import importlib.util,pathlib,struct,unittest,json,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'tests/orb_protron_native_validation.py';spec=importlib.util.spec_from_file_location('op_native',p);n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
class Adapter(unittest.TestCase):
 def inputs(self):
  h={i:bytes([i%256])*43036 for i in n.IDS if i not in n.CANONICAL};names={i:f'fixture-{i}.hda'for i in h}
  for i,pin in n.CANONICAL.items():names[i]='content/'+pin+'.hda';h[i]=(ROOT/'assets/hd/global-assets-v1'/names[i]).read_bytes()
  return h,{i:n.sha(b)for i,b in h.items()},names
 def test_inventory_exact83(self):
  self.assertEqual(sum(n.CASE_INVENTORY.values()),83);self.assertEqual(n.CASE_INVENTORY['current28_complete_oracles'],28);self.assertEqual(len(n.IDS),29);self.assertEqual(len(n.PACKS),13)
 def test_ten_dispatches_reversible(self):
  sources,wrapped=n.source_bundle(ROOT);old=n.reverse_shim(wrapped,ROOT);self.assertEqual(len(sources),6);self.assertEqual(n.outer_shim(old,ROOT),wrapped);self.assertIn(b'--widget-sonic',old);self.assertNotIn(b'--orb-protron',old)
 def test_changed_dispatch_refused(self):
  for raw in (b'',b'int main(){}',b'x'+n.TAIL):
   with self.assertRaises(ValueError):n.outer_shim(raw,ROOT)
   with self.assertRaises(ValueError):n.reverse_shim(raw,ROOT)
 def test_fixture_exact377_and_old25_unchanged(self):
  h,pins,names=self.inputs();out=n.fixture_payloads(h,pins,names);self.assertEqual(len(out),377)
  for leaf in n.PACKS:
   for i in n.OLD_IDS:self.assertEqual(out['orb-protron-packs/'+leaf+'/'+names[i]],h[i])
  for i in n.NEW_IDS:self.assertNotIn('orb-protron-packs/missing'+str(i)+'/'+names[i],out)
  for missing in (112,113):
   prefix='orb-protron-packs/legacy-missing'+str(missing)+'/';self.assertEqual([p for p in out if p.startswith(prefix)],[prefix+'enemy-orb112113-'+str(225-missing)+'-8.hda'])
 def test_exact_material_identities(self):
  h,_,_=self.inputs()
  for i in n.NEW_IDS:self.assertEqual(struct.unpack('<4s6I',h[i][:28]),(b'HDR1',n.MATERIAL[i],8,12,14,0,0))
  self.assertEqual(n.MATERIAL,{112:1420112,113:1420113,226:80226,227:1470227})
 def test_real_wrong_material_not_fabricated80227(self):
  h,_,_=self.inputs();wrong=n.wrong_materials()
  for i in (112,227):
   b=n.fixture_bytes(h[i],i,'bad'+str(i),wrong);self.assertEqual(struct.unpack('<I',b[4:8])[0],n.MATERIAL[i]);self.assertEqual(b[28:],wrong[i][28:]);self.assertNotEqual(b[28:],h[i][28:])
  self.assertEqual(struct.unpack('<I',wrong[227][4:8])[0],80244)
 def test_mutations_target_one_member(self):
  h,_,_=self.inputs();wrong=n.wrong_materials()
  for leaf in n.PACKS:self.assertEqual(sum(n.fixture_bytes(h[i],i,leaf,wrong)!=h[i]for i in n.IDS),0 if leaf=='valid'else 1)
 def test_paths_membership_and_false_identity_rejected(self):
  h,pins,names=self.inputs()
  for bad in ('../bad.hda','/bad.hda','content/renamed.hda'):
   q=dict(names);q[112]=bad
   with self.assertRaises(ValueError):n.fixture_payloads(h,pins,q)
  q=dict(h);q.pop(67)
  with self.assertRaises(ValueError):n.fixture_payloads(q,pins,names)
  with self.assertRaises(ValueError):n.fixture_bytes(bytes(43036),True,'valid')
 def test_halo_two_exact_texels_and_native_cells(self):
  h,_,_=self.inputs();a=h[227][28:]
  rle=bytes.fromhex('0c0c0c53828b8a86820472828b8f8d8b868203728b8f8d8b8a878603728a8d8b8a8984850372898b8a89858284037282868583818482035382868584820f');self.assertEqual(n.sha(rle),'3ef2f3d9f3288e70ff509d64d520b9abf67080198a3e9aa45dccb10ce5722054')
  mask=[0]*168;offset=pos=0
  while rle[offset]!=15:
   c=rle[offset];offset+=1;pos+=c&15;count=c>>4
   for k in range(count):mask[pos+k]=1
   offset+=count;pos+=count
  self.assertEqual(n.sha(bytes(mask)),'bb57c00e6627b6a45ce95a099fc91ff5b7657f2d4d2be7d88b7fe4bdc35b3493');outside=[(z%96,z//96,a[z*4+3])for z in range(10752)if a[z*4+3]and not mask[z//96//8*12+z%96//8]]
  self.assertEqual(outside,[(23,31,2),(64,72,1)]);self.assertEqual((31//8*12+23//8,72//8*12+64//8),(38,116))
 def test_tiny_full_actual_route_and_cached_proof(self):
  raw,pins=n.tiny_sources(ROOT);self.assertEqual(len(pins),7);self.assertIn(b'#include "enemy_orb_protron_policy.h"',raw);self.assertIn(b'Asset *a=&assets[218+(int)index-112];',raw);self.assertIn(b'if(asteroid_hd_enabled&&(index==112||index==113))return enemy_orb112113_draw',raw);self.assertIn(b'orb_protron_ordinary_allowed(227)',raw);self.assertIn(b'global_projectile91_check_cache(void)',raw);self.assertIn(b'assert(cases==320)',raw)
  for p,pin in pins.items():self.assertEqual(n.sha((ROOT/p).read_bytes()),pin)
 def test_native_scope_no_fabricated_roles(self):
  raw=(ROOT/'tests/orb_protron_native_additions.c.inc').read_text();self.assertIn('CHECK(cases-initial==83)',raw);self.assertIn('ws_direct24();',raw);self.assertIn('enemy70_draw(30,30);op_retire',raw);self.assertIn('render_mirror_fade_step(7)',raw);self.assertIn('enemy_orb112113_family_ready()',raw);self.assertNotIn('global_vulcan_slots[0].role=true',raw);self.assertIn('if(before[c]&&!shared&&hd&&player_owned)',raw);self.assertIn('global_projectile91_used_members==134217728u',raw)
if __name__=='__main__':unittest.main()
