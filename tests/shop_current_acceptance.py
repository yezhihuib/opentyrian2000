"""Fresh current SHOP gate. Does not assert recovery of any private commit."""
from pathlib import Path
import hashlib
import json
from shop_published_boundary import fixture, check_pin_assets, published_source

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / 'tests/fixtures/shop_current_acceptance/inventory.json'
PROJECTILE91_QUALIFIED = ROOT / 'tests/fixtures/shop_current_acceptance/projectile91-qualified-extension.json'
PROJECTILE91_QUALIFIED_SHA256 = 'cd2b80009795e1b106bbc64eded7f104bcdc6b38ee44779070941ec7eefd750b'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def verify_bytes(raw, wanted, name):
    assert sha(raw) == wanted, 'current identity drift: ' + name

def check_names(actual, expected):
    assert actual == {p for p in expected if p.startswith(('src/', 'assets/'))}, 'current path inventory drift'

def check_current_inventory(root=ROOT):
    raw = INVENTORY.read_bytes()
    assert sha(raw) == '26b7e3b33cba2adfe6fee1aa19f887ff09aa1ed6d438491a3f8c737b738fc102', 'current receipt changed'
    expected = json.loads(raw)['files']
    actual = {str(p.relative_to(root)) for top in ('src', 'assets')
              for p in (root / top).rglob('*') if p.is_file() or p.is_symlink()}
    # Validate the whole newest delta before excluding any path or rewriting a hash.
    from accepted_later_changes import (verified_current_projectile91, current_projectile91_ledger,
        CURRENT_PROJECTILE91_HEADER, project_current_projectile91_source)
    qualified_raw = PROJECTILE91_QUALIFIED.read_bytes()
    verify_bytes(qualified_raw, PROJECTILE91_QUALIFIED_SHA256, 'qualified projectile91 receipt')
    qualified = json.loads(qualified_raw)['files']
    # A coherent new master is editable, but does not inherit visual/native acceptance.
    for name, wanted in qualified.items():
        path = root / name
        assert path.is_file() and not path.is_symlink(), 'nonregular qualified file: ' + name
        verify_bytes(path.read_bytes(), wanted, name)
    proof = verified_current_projectile91(root)
    added = dict(proof['added_sources'])
    added[CURRENT_PROJECTILE91_HEADER] = proof['header_sha256']
    added.update({name: row['sha256'] for name, row in proof['assets'].items()})
    assert added == qualified, 'qualified projectile91 material drift'
    assert len(added) == 6 and not set(added) & set(expected), 'projectile91 extension scope drift'
    from linked_newshf_projection import verified as linked_verified
    linked = linked_verified(root)
    linked_added = dict(linked['added_sources'])
    linked_added.update({n:r['sha256'] for n,r in linked['assets'].items()})
    assert not set(linked_added)&(set(expected)|set(added)), 'linked extension overlaps existing paths'
    from shapesy_platform_projection import verified as shapesy_verified, project_asset as shapesy_asset
    shapesy = shapesy_verified(root)
    shapesy_added = dict(shapesy['added_sources'])
    shapesy_added.update({n:r['sha256'] for n,r in shapesy['assets'].items()})
    assert not set(shapesy_added)&(set(expected)|set(added)|set(linked_added)), 'ShapesY extension overlaps existing paths'
    from dualmissile_newshf_projection import verified as dual_verified
    dual = dual_verified(root)
    dual_added = dict(dual['added_sources'])
    dual_added.update({n:r['sha256'] for n,r in dual['assets'].items()})
    assert not set(dual_added)&(set(expected)|set(added)|set(linked_added)|set(shapesy_added))
    from turret_newshf_projection import verified as turret_verified
    turret = turret_verified(root)
    turret_added = dict(turret['added_sources'])
    turret_added.update({n:r['sha256'] for n,r in turret['assets'].items()})
    assert not set(turret_added)&(set(expected)|set(added)|set(linked_added)|set(shapesy_added)|set(dual_added))
    from large_newshi_projection import verified as large_verified
    large = large_verified(root)
    large_added = dict(large['added_sources'])
    large_added.update({n:r['sha256'] for n,r in large['assets'].items()})
    assert not set(large_added)&(set(expected)|set(added)|set(linked_added)|set(shapesy_added)|set(dual_added)|set(turret_added))
    from shapesy_cyan_projection import verified as cyan_verified
    cyan=cyan_verified(root)
    cyan_added=dict(cyan['added_sources'])
    cyan_added.update({n:r['sha256'] for n,r in cyan['assets'].items()})
    assert not set(cyan_added)&(set(expected)|set(added)|set(linked_added)|set(shapesy_added)|set(dual_added)|set(turret_added)|set(large_added))
    from shapesy_cyan_secondary_projection import verified as secondary_verified
    secondary=secondary_verified(root)
    secondary_added=dict(secondary['added_sources'])
    secondary_added.update({n:r['sha256'] for n,r in secondary['assets'].items()})
    assert not set(secondary_added)&(set(expected)|set(added)|set(linked_added)|set(shapesy_added)|set(dual_added)|set(turret_added)|set(large_added)|set(cyan_added))
    from scout164_newshf_projection import verified as scout_verified
    scout=scout_verified(root)
    scout_added=dict(scout['added_sources'])
    scout_added.update({n:r['sha256'] for n,r in scout['assets'].items()})
    assert not set(scout_added)&(set(expected)|set(added)|set(linked_added)|set(shapesy_added)|set(dual_added)|set(turret_added)|set(large_added)|set(cyan_added)|set(secondary_added))
    from fighter165_newshf_projection import verified as fighter_verified
    fighter=fighter_verified(root)
    fighter_added=dict(fighter['added_sources'])
    fighter_added.update({n:r['sha256'] for n,r in fighter['assets'].items()})
    assert not set(fighter_added)&(set(expected)|set(added)|set(linked_added)|set(shapesy_added)|set(dual_added)|set(turret_added)|set(large_added)|set(cyan_added)|set(secondary_added)|set(scout_added))
    check_names(actual, dict(expected, **added, **linked_added, **shapesy_added, **dual_added, **turret_added, **large_added, **cyan_added, **secondary_added, **scout_added, **fighter_added))
    for name, wanted in added.items():
        path = root / name
        assert path.is_file() and not path.is_symlink(), 'nonregular extension file: ' + name
        verify_bytes(path.read_bytes(), wanted, name)
    changed = current_projectile91_ledger()['files']
    for name, wanted in expected.items():
        path = root / name
        assert path.is_file() and not path.is_symlink(), 'nonregular current file: ' + name
        current = path.read_bytes()
        if name == 'src/newshf_identity_validation.inc':
            from linked_newshf_projection import project_source as linked_project
            current = linked_project(name,current)
        if name in changed:
            current = project_current_projectile91_source(name, current)
        else:
            from shapesy_platform_projection import project_source as shapesy_source
            current = shapesy_source(name,current)
        current = shapesy_asset(name,current)
        verify_bytes(current, wanted, name)

def check_live_guards(source):
    for value in ('SF_EVENTS=65536', 'SF_CAP=16*1024*1024', 'sf.event_count==SF_EVENTS',
                  'sf.count>sf.static_count', 'if(!replay_matches())', 'p/SF_W>=185',
                  'sf.product&&sf.run_role==PREGAME_CASH',
                  'sf.metal&&(!sf.product||sf.category==2||sf.category==5)'):
        assert value in source, 'missing current guard: '+value
    assert source.count('sf.metal_blocked[p]=1') == 1
    assert 'sf.metal_blocked[p]=0' not in source

def check_original_menu_lease(source):
    for value in ('static void load_menu_run(unsigned r)', 'sf.menu_run[r]',
                  'if(!menu)for(unsigned r=0;r<7;r++)load_menu_run(r);',
                  'if(r<7&&sf.menu_run[r]&&!strcmp(plain,menu_spec[r].text))',
                  'memcmp(h,"SMR1",4)', 'hash(data,size)!=s->payload_hash'):
        assert value in source, 'missing menu lease: '+value

def check_menu_lease(source):
    for value in ('common_menu_runs_generation(sf.fixed_family)!=sf.fixed_generation',
                  'common_menu_runs_generation(COMMON_MENU_NAMES)!=sf.names_generation',
                  'common_menu_numeric_runs_generation()!=sf.numeric_generation',
                  'sf.fixed_count==PF_FIXED_SLOTS', 'strcmp(plain,run.text)',
                  'p->x+(int)p->run.width+(int)p->shadow>SF_OW',
                  'p->y+(int)p->run.height+(int)p->shadow>SF_OH',
                  'retire_typography(0)', 'retire_typography(1)', 'retire_typography(2)'):
        assert value in source, 'missing current menu lease: '+value

# Exact public 775b -> f586 additions reviewed in public-owner-delta.patch.
# These are not historical private tree restorations. After removing ONLY these
# finite additions the existing independently pinned public projection must pass.
OWNER_ADDITIONS = {
    'src/sprite.c': [
        '#include "enemy_reuse_identity.h"\n',
        '\trender_mirror_newshf_validation_bank_changed(sprite2s);\n#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)\n\tenemy_reuse_bank_changed(sprite2s);\n#endif\n',
    ],
    'visualc/opentyrian.vcxproj': [
        '    <ClCompile Include="..\\src\\enemy_reuse_identity.c" />\n',
        '    <ClInclude Include="..\\src\\enemy_reuse_identity.h" />\n',
    ],
}

def reviewed_frame_owner(name, raw):
    from shop_published_boundary import project_bytes, stage_spec
    spec=stage_spec('frame')['files'][name]
    if name in OWNER_ADDITIONS:
        expected=json.loads(INVENTORY.read_bytes())['files'][name]
        verify_bytes(raw,expected,name)
        for addition in OWNER_ADDITIONS[name]:
            encoded=addition.encode()
            assert raw.count(encoded)==(2 if addition.startswith('\trender_') else 1), 'owner delta span drift'
            raw=raw.replace(encoded,b'')
    return project_bytes(raw,spec)
