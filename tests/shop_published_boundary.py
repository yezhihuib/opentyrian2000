"""Fail-closed projections to independently published SHOP stages.

Private stage commits are historical provenance, not clean-clone prerequisites.
Every present byte is validated BEFORE finite inverse edits are applied, including
bytes introduced after the stage. No path prefix or code substring is exempted.
"""
from pathlib import Path
import base64
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/shop_published_boundaries'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def fixture(name):
    receipt_bytes = (FIXTURES / 'provenance.json').read_bytes()
    assert sha(receipt_bytes) == 'b82270c5d65dcd44da0304f260fc8c115f0226ec743f8cec52bf2313957d7550', 'SHOP provenance receipt changed'
    receipt = json.loads(receipt_bytes)
    raw = (FIXTURES / name).read_bytes()
    assert sha(raw) == receipt['fixture_sha256'][name], name
    return raw

def stage_spec(stage):
    return json.loads(fixture(stage + '.json'))

def project_bytes(raw, spec):
    assert sha(raw) == spec['after_sha256'], 'unreviewed current source bytes'
    out = raw
    edits = spec['inverse_edits']
    previous = -1
    for edit in edits:
        start, end = edit['start'], edit['end']
        assert previous <= start <= end <= len(raw), 'invalid/overlapping inverse'
        previous = end
        assert sha(raw[start:end]) == edit['after_sha256'], 'inverse span drift'
    for edit in reversed(edits):
        out = out[:edit['start']] + base64.b64decode(edit['before_b64'], validate=True) + out[edit['end']:]
    assert sha(out) == spec['before_sha256'], 'published stage SHA256 mismatch'
    blob = b'blob ' + str(len(out)).encode() + b'\0' + out
    assert hashlib.sha1(blob).hexdigest() == spec['before_git_blob'], 'published Git blob mismatch'
    return out

def published_source(stage, name, root=ROOT):
    return project_bytes((root / name).read_bytes(), stage_spec(stage)['files'][name])

def check_inventory_names(actual, expected):
    assert actual == {p for p in expected if p.startswith(('src/', 'assets/'))}, 'source/asset inventory drift'

def check_inventory(root=ROOT):
    expected = json.loads(fixture('current-inventory.json'))['files']
    actual = {str(p.relative_to(root)) for top in ('src', 'assets')
              for p in (root / top).rglob('*') if p.is_file() or p.is_symlink()}
    check_inventory_names(actual, expected)
    for name, wanted in expected.items():
        p = root / name
        assert p.is_file() and not p.is_symlink(), name
        assert sha(p.read_bytes()) == wanted, name

def check_pin_assets(kind, root=ROOT):
    pin = json.loads((root / ('tests/shop_' + kind + '_source_delta.json')).read_text())
    for name, wanted in pin['accepted_sha256'].items():
        if name == 'src/pregame_font.c':
            continue  # separately reconstructed to the pinned published stage
        raw = published_source('generator', name, root) if name == 'tests/run_pregame_font_tests.sh' else (root / name).read_bytes()
        assert sha(raw) == wanted, name
        for at in {0, len(raw)//2, len(raw)-1}:
            bad = raw[:at] + bytes([raw[at] ^ 1]) + raw[at+1:]
            assert sha(bad) != wanted, name
    return pin

# These private history prerequisites remain separate from the newer live
# contracts. Absence is a counted failure, never a skip or an invented parent.
HISTORICAL = {
    'frame_integration': '8218c1f8a2ca046b6c461f3da1006ee76cf1b203',
    'front_boundary': 'ac64ee7d3f72dc07fac6a1454eefe4d95429e7b3',
    'generator_boundary': 'd97783b0ad24cce20d1cecfe0afc6890ac7943df',
    'menu_font_boundary': '1685561b2b5d6bd6264bd7756cc30cf7c7506c4f',
    'product_font_integration': '8ffe93fa4f991163fd4e6bb6842a1a1b21a46b0d',
}

def historical_readiness():
    import subprocess
    rows = {}
    for name, commit in HISTORICAL.items():
        result = subprocess.run(['git', '-C', str(ROOT), 'cat-file', '-e', commit+'^{commit}'],
                                capture_output=True, text=True)
        rows[name] = {'commit': commit, 'status': 'available' if result.returncode == 0 else 'unavailable',
                      'reason': result.stderr.strip()}
    return rows

def replay_original_historical_contract(name):
    row = historical_readiness()[name]
    assert row['status'] == 'available', (
        'HISTORICAL_PROOF_UNAVAILABLE: '+name+' requires exact private commit '+row['commit']+
        '; published-stage live checks do not substitute for this private-tree proof. '+row['reason'])
    filename = 'test_shop_'+name+'.py'
    # Compile the byte-exact original with its ORIGINAL pathname. __file__ and
    # relative ROOT therefore retain their real historical script semantics.
    original = fixture(filename+'.historical.txt')
    script = ROOT / 'tests' / filename
    namespace = {'__file__': str(script), '__name__': '__main__'}
    exec(compile(original, str(script), 'exec'), namespace)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--readiness', action='store_true')
    parser.add_argument('--historical', choices=sorted(HISTORICAL))
    args = parser.parse_args()
    if args.historical:
        replay_original_historical_contract(args.historical)
    else:
        rows = historical_readiness()
        print(json.dumps(rows, indent=2, sort_keys=True))
        raise SystemExit(0 if all(row['status']=='available' for row in rows.values()) else 1)
