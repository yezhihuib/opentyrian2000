"""Finite bank8/enemyshot91 render delta; authentic f586 preimages stay frozen."""
import copy
import json
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from unittest.mock import patch
import accepted_later_changes as a

class Projectile91Projection(unittest.TestCase):
 def test_exact_scope_and_full_inverse(self):
  ledger=a.current_projectile91_ledger()
  self.assertEqual(set(ledger['files']),{'src/global_cash25_mirror.inc', 'src/global_smoke_mirror.inc', 'src/global_small_explosion_mirror.inc', 'src/global_rotor_mirror.inc', 'src/global_green_mirror.inc', 'src/global_newshf_mirror.inc', 'src/tyrian2.c', 'src/render_mirror.c', 'src/global_pulse_mirror.inc', 'src/global_vulcan_mirror.inc', 'src/global_shield_mirror.inc', 'src/global_talon_mirror.inc', 'src/entity_draw.c', 'src/global_hitflare_mirror.inc'})
  self.assertEqual(ledger['integration_base'],'f58647e7ff74e2276a1413b3675e651f1232bb41')
  for name,pin in ledger['files'].items():
   raw=(a.ROOT/name).read_bytes();old=a.project_current_projectile91_source(name,raw)
   self.assertEqual(a.sha(old),pin['previous_sha256'])
   for invalid in (old,raw+b'\n',raw[:-1]):
    with self.subTest(name=name),self.assertRaises(AssertionError):a.project_current_projectile91_source(name,invalid)
   for hunk in pin['hunks']:
    lines=raw.splitlines(keepends=True);start,end=hunk['after_lines']
    lines[start:end]=hunk['before'].encode().splitlines(keepends=True)
    with self.assertRaises(AssertionError):a.project_current_projectile91_source(name,b''.join(lines))
   for key in ('after','before'):
    altered=copy.deepcopy(ledger);altered['files'][name]['hunks'][0][key]+='\n'
    with patch.object(a,'current_projectile91_ledger',return_value=altered),self.assertRaises(AssertionError):
     a.project_current_projectile91_source(name,raw)

 def test_source_inventory_requires_additions_before_removal(self):
  from verify_current_production import source_inventory
  actual=source_inventory(a.ROOT);previous=a.before_current_projectile91_inventory(actual)
  ledger=a.current_projectile91_ledger()
  for name,pin in ledger['files'].items():self.assertEqual(previous[name],pin['previous_sha256'])
  for name in set(ledger['files'])|set(ledger['added_sources'])|{a.CURRENT_PROJECTILE91_HEADER}:
   for action in ('missing','changed'):
    invalid=dict(actual)
    if action=='missing':invalid.pop(name)
    else:invalid[name]='0'*64
    with self.subTest(name=name,action=action),self.assertRaises((AssertionError,KeyError)):
     a.before_current_projectile91_inventory(invalid)

 def test_added_source_and_header_bytes_rechecked(self):
  import current_projectile91_compatibility as c
  original=c.read
  for name in set(a.current_projectile91_ledger()['added_sources'])|{c.HEADER}:
   with patch.object(c,'read',side_effect=lambda root,path,*args:original(root,path,*args)+(b'\n' if path==name else b'')):
    with self.subTest(name=name),self.assertRaises((AssertionError,ValueError)):a.verified_current_projectile91()

 def test_runtime_only_exact_new_row_removed(self):
  rows=json.loads((a.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files']
  previous=a.before_current_projectile91_runtime(rows)
  destination='assets/gameplay/enemy-projectile91-91-8.hda'
  from linked_newshf_projection import before_runtime
  from shapesy_platform_projection import before_runtime as shapesy_before_runtime
  self.assertEqual(previous,[r for r in before_runtime(shapesy_before_runtime(rows)) if r['destination']!=destination])
  self.assertEqual(len(previous),1029)
  for action in ('missing','changed','duplicate'):
   invalid=copy.deepcopy(rows);target=next(r for r in invalid if r['destination']==destination)
   if action=='missing':invalid.remove(target)
   elif action=='duplicate':invalid.append(target)
   else:target['sha256']='0'*64
   with self.subTest(action=action),self.assertRaises(AssertionError):a.before_current_projectile91_runtime(invalid)

 def test_ledger_bytes_not_rebaselined(self):
  original=a.Path.read_bytes
  with patch.object(a.Path,'read_bytes',lambda p:original(p)+(b'\n' if p.name=='current_projectile91_source_projection.json' else b'')):
   with self.assertRaises(AssertionError):a.current_projectile91_ledger()

if __name__=='__main__':unittest.main()
