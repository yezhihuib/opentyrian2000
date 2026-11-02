"""Pure finite adapter tests; never compiles, launches native or loads game data."""
from pathlib import Path
import types,unittest
from unittest.mock import patch
import warning_muzzle_native_validation as m
class WarningMuzzleNativeAdapter(unittest.TestCase):
 def test_exact_twelve_scope(self):
  self.assertEqual(sum(m.CASE_INVENTORY.values()),12);self.assertIn('not old32/44',m.SCOPE);self.assertIn('nonoverlapping',m.SCOPE)
 def test_predecessor_pin(self):
  p=m.ROOT/'tests/tank_muzzle_native_validation.py';self.assertEqual(m.sha(p.read_bytes()),m.MUZZLE_HELPER_SHA)
  with patch.object(Path,'read_bytes',return_value=b'changed'),self.assertRaises(ValueError):m.predecessor(m.ROOT)
 def test_input_initialization_exact_prefix(self):
  raw=(m.ROOT/'tests/tank_muzzle_native_additions.c.inc').read_text();expected=raw.split('static int mu_main(int argc,char **argv)\n{\n',1)[1].split(' unsigned initial=cases,assertions=checks;',1)[0]
  generated=m.loader_prefix(m.ROOT).decode();self.assertEqual(generated,'static void cw_load(int argc,char **argv)\n{\n'+expected.replace('"--tank-muzzle"','"--warning-muzzle"',1)+'}\n');self.assertNotIn('mu_direct5()',generated);self.assertEqual(generated.count('CHECK(fgetc(stdin)==EOF);'),1)
 def test_changed_initialization_rejected(self):
  with patch.object(Path,'read_bytes',return_value=b'changed'),self.assertRaises(ValueError):m.loader_prefix(m.ROOT)
 def test_bundle_keeps_all_old_companions_and_entry(self):
  prior,old=m.predecessor(m.ROOT).source_bundle(m.ROOT);sources,raw=m.source_bundle(m.ROOT);self.assertEqual(len(sources),len(prior)+2)
  for name,value in prior.items():self.assertEqual(sources[name],value)
  self.assertTrue(raw.startswith(old.replace(b'int main(',b'int inherited_muzzle_dispatch(',1)));self.assertEqual(raw.count(b'int main('),1);self.assertIn(b'--warning-muzzle',raw)
 def test_one_corrupt_huf_fixture_no_other_material_change(self):
  huf=b'approved huf';base={'muzzle-font/gameplay-hud-font-v1.hda':huf,**{str(i):b'old'for i in range(53)}}
  old=types.SimpleNamespace(fixture_payloads=lambda *args:dict(base))
  with patch.object(m,'predecessor',return_value=old):result=m.fixture_payloads({}, {}, {},huf,m.ROOT)
  self.assertEqual(len(result),55)
  for k,v in base.items():self.assertEqual(result[k],v)
  bad=result['warning-bad/gameplay-hud-font-v1.hda'];self.assertEqual(bad[:-1],huf[:-1]);self.assertEqual(bad[-1],huf[-1]^1)
 def test_wrong_fixture_membership_rejected(self):
  with patch.object(m,'predecessor',return_value=types.SimpleNamespace(fixture_payloads=lambda *args:{})),self.assertRaises(ValueError):m.fixture_payloads({}, {}, {},b'x',m.ROOT)
 def test_changed_input_delegate_rejected(self):
  with patch.object(m,'predecessor',return_value=types.SimpleNamespace(native_input=lambda *args:b'x')),self.assertRaises(ValueError):m.native_input(*([b'']*6),root=m.ROOT)
 def test_real_owner_oracle_and_samevalue_not_changedvalue(self):
  s=(m.ROOT/'tests/warning_muzzle_native_additions.c.inc').read_text()
  for token in ('JE_outText(game_screen,140,178,"WARNING"','player_shot_move_and_draw','cw_decode','cw_atlas[','cw_same_write','value=*p','CHECK(*p==value)','cw_present(true,gx,gy)','cw_present(false,gx,gy)','render_mirror_fade_step(7)','cases-initial==12'):
   self.assertIn(token,s)
  self.assertNotIn('SDL stub',s);self.assertNotRegex(s,r'global_projectile91_owner\s*\[[^]]+\]\s*=(?!=)');self.assertRegex('global_projectile91_owner[n]=0;',r'global_projectile91_owner\s*\[[^]]+\]\s*=(?!=)')
 def test_decline_does_not_claim_stale_output_is_native(self):
  s=(m.ROOT/'tests/warning_muzzle_native_additions.c.inc').read_text();write=s.split('static void cw_same_write',1)[1].split('static void cw_orders2',1)[0]
  self.assertIn('enemy70_declined()',write);self.assertIn('cw_native64',write);self.assertNotIn('*at(output',write)
if __name__=='__main__':unittest.main()
