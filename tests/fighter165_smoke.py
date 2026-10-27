#!/usr/bin/env python3
"""Explicit SMOKE subset, not full qualification: projections and three row negatives.

Runs no 84-case historical inventory mutation sweep. Full tests remain required.
"""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'scripts')]
import fighter165_newshf_projection as p
import scout164_newshf_projection as scout
import shapesy_cyan_secondary_projection as secondary
import shapesy_cyan_projection as old
import shapesy_platform_projection as y
import dualmissile_newshf_projection as dual
import turret_newshf_projection as turret
import large_newshi_projection as large
from verify_current_production import source_inventory

def main():
 from accepted_later_changes import current_asset_inventory
 current_asset_inventory(ROOT)  # Exact Git-index modes/membership before costly gates.
 from accepted_later_changes import before_current_newshf_inventory, verified_enemy_probe_sources
 old_inventory=before_current_newshf_inventory(source_inventory(ROOT),ROOT)
 assert len(old_inventory)==268+len(verified_enemy_probe_sources(ROOT))
 proof=p.verified();assert len(proof['mapping'])==3
 inv=source_inventory(ROOT);before=p.before_inventory(inv)
 assert before==p.ledger()['base_source_inventory']
 rows=json.loads((ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files']
 restored=p.before_runtime(rows)
 assert len(rows)-len(restored)==3
 for kind in ('missing','duplicate','changed'):
  bad=copy.deepcopy(rows);row=next(r for r in bad if r['destination'] in proof['mapping'])
  if kind=='missing':bad.remove(row)
  elif kind=='duplicate':bad.append(row)
  else:row['group']='wrong'
  try:p.before_runtime(bad)
  except (AssertionError,ValueError,KeyError):pass
  else:raise AssertionError('SMOKE accepted '+kind+' runtime row')
 original=y.before_inventory(inv)
 assert original==y.ledger()['public_source_inventory']
 assert set(inv)-set(original)==y.ADDED|dual.ADDED|turret.ADDED|large.ADDED|old.ADDED|secondary.ADDED|scout.ADDED|p.ADDED
 assert len(rows)-len(y.before_runtime(rows))==56
 from test_dualmissile_newshf_projection import DualProjection
 DualProjection('test_projection_dispatch_orders').test_projection_dispatch_orders()
 print('SMOKE PASS: valid inventory/runtime, 3 row negatives, old ShapesY header/56-row assertions, actual dispatcher order; NOT full qualification',flush=True)
if __name__=='__main__':main()
