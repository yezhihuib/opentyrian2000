#!/usr/bin/env python3
"""Pin the finite Marlo152 production-source inverse. Never starts the game.

All 153 baseline src blobs are checked, including the original blitters. Only
five files may differ. Removing three frozen Marlo-only blocks, declarations,
one role/prefix/slot extension, and the one finite body-site branch
must restore the complete production source tree byte for byte. Assets, docs,
and focused tests are deliberately outside this source-only audit.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = 'cf2019726c1891e558df0959b415558ae598b386'
TREE = '72bafdfce4b2ac5d0efb2821534dec2816596489'
ENVELOPE = {'src/mainint.c', 'src/entity_draw.c', 'src/entity_draw.h',
            'src/render_mirror.c', 'src/render_mirror.h'}
SHA = lambda raw: hashlib.sha256(raw).hexdigest()
OLD_BODY_CALL = b'\t\t\t\t\tblit_sprite2(VGAScreen, x, y, spriteSheet9, sprite);'
NEW_BODY_BRANCH = (
    b'\t\t\t\telse if (this_player->items.sidekick[i] == 30 && this_player->sidekick[i].style == 4 &&\n'
    b'\t\t\t\t         this_player->sidekick[i].charge == 0 && sprite == 152)\n'
    b'\t\t\t\t\tdraw_sidekick_body_sprite2(VGAScreen, x, y, spriteSheet9, sprite,\n'
    b'\t\t\t\t\t                          this_player->items.sidekick[i],\n'
    b'\t\t\t\t\t                          this_player->sidekick[i].style, this_player->sidekick[i].charge);\n')
ENTITY_DECL = (
    b'/* Dedicated normal TILE body boundary; gameplay state is only inspected. */\n'
    b'void draw_sidekick_body_sprite2(SDL_Surface *,int x,int y,Sprite2_array,\n'
    b'                               unsigned int index,unsigned int option,\n'
    b'                               unsigned int sidekick_style,unsigned int charge);\n\n')
MIRROR_DECL = (
    b'bool render_mirror_marlo_body(SDL_Surface *,int x,int y,Sprite2_array,unsigned int index,\n'
    b'                              unsigned int option,unsigned int sidekick_style,unsigned int charge);\n')
MIRROR_MACRO = b'#define render_mirror_marlo_body(...) false\n'
BLOCKS = {
    'entity_wrapper': {
        'path': 'src/entity_draw.c',
        'start': b'\n/* Original sidekick body coordinates and indexed writes are never replaced. */',
        'end': None,
        'sha256': 'e134edd66638d87b545b4603fbd621f4f260f704d5650747df8865949aba67ee',
        'functions': ['draw_sidekick_body_sprite2'],
    },
    'source_and_asset': {
        'path': 'src/render_mirror.c',
        'start': b'/* Marlo30 is a separate role, never a Talon or generic bank9 binding.',
        'end': b'static Asset *get_asset(',
        'sha256': '8babc309bf522881ebe54d5483ca9e52b5cbfdd4c13fcead01901f4760cc406c',
        'functions': ['marlo152_source_matches', 'marlo152_asset'],
    },
    'body_route': {
        'path': 'src/render_mirror.c',
        'start': b'/* Only the existing Marlo30 normal body site can enter this finite route.',
        'end': b'/* Seven original static directions, including shared enemy58 uses.',
        'sha256': '9a345d1b428fc6b9e9876705829364b3e5cadc8f2dda7a4d9977b6f5939add7d',
        'functions': ['render_mirror_marlo_body'],
    },
}


def require(condition, explanation):
    # Deliberately effective under python -O, too.
    if not condition:
        raise AssertionError(explanation)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def replace_once(raw, before, after, label):
    require(raw.count(before) == 1, 'Missing or repeated inverse: ' + label)
    return raw.replace(before, after, 1)


def block(raw, spec):
    require(raw.count(spec['start']) == 1, 'Missing or repeated Marlo-only block')
    start = raw.index(spec['start'])
    if spec['end'] is None:
        end = len(raw)
    else:
        require(raw.count(spec['end']) == 1, 'Missing or repeated original block anchor')
        end = raw.index(spec['end'], start)
    addition = raw[start:end]
    require(SHA(addition) == spec['sha256'], 'Unreviewed/nonfinite Marlo block: ' + spec['path'])
    return raw[:start] + raw[end:], addition


def inverse_sources(current, baseline):
    require(set(current) == set(baseline), 'Production source inventory changed')
    changed = {name for name in baseline if current[name] != baseline[name]}
    require(changed == ENVELOPE, 'Production delta must be exactly five files: ' + str(sorted(changed)))
    restored = dict(current)
    additions = {}
    for label, spec in BLOCKS.items():
        restored[spec['path']], additions[label] = block(restored[spec['path']], spec)
    restored['src/mainint.c'] = replace_once(
        restored['src/mainint.c'], NEW_BODY_BRANCH, b'', 'one finite branch at the existing sidekick body site')
    restored['src/entity_draw.h'] = replace_once(
        restored['src/entity_draw.h'], ENTITY_DECL, b'', 'sidekick wrapper declaration')
    restored['src/render_mirror.h'] = replace_once(
        restored['src/render_mirror.h'], MIRROR_DECL, b'', 'Marlo mirror declaration')
    restored['src/render_mirror.h'] = replace_once(
        restored['src/render_mirror.h'], MIRROR_MACRO, b'', 'classic-disabled Marlo macro')
    for before, after, label in [
        (b', ASSET_MARLO_BODY=126', b'', 'independent role126'),
        (b'static Asset assets[537];', b'static Asset assets[536];', 'one added slot'),
        (b'a->bank==ASSET_MARLO_BODY?"option-marlo-bank9":', b'', 'read_asset filename prefix'),
    ]:
        restored['src/render_mirror.c'] = replace_once(restored['src/render_mirror.c'], before, after, label)
    for name, old in baseline.items():
        require(restored[name] == old, 'Byte-exact production inverse failed: ' + name)
    return restored, additions


def finite_contract(current, baseline, additions):
    """Make the frozen additions' small contract legible as well as hash-pinned."""
    source = additions['source_and_asset']
    wrapper = additions['entity_wrapper']
    route = additions['body_route']
    for literal in [
        b'if(xmas||!bank.data||bank.data!=spriteSheet9.data||bank.size!=spriteSheet9.size)',
        b'Uint8 source[12*14*2]={0};',
        b'decode_tile(bank,152,source,source+12*14,12,0,0)',
        b'UINT64_C(0x840f92ed11537363)',
        b'option!=30||sidekick_style!=4||charge!=0||index!=152',
        b'Asset *a=&assets[536];',
        b'a->initialized=true;a->bank=ASSET_MARLO_BODY;a->index=152;',
        b'a->w=12;a->h=14;a->anchor_x=0;a->anchor_y=0;',
        b'if(!a->valid&&game_probe_density==8)a->valid=read_asset(a,4);',
    ]:
        require(literal in source, 'Missing finite admission/identity/registration assertion')
    require(source.index(b'!marlo152_source_matches(bank)') < source.index(b'if(a->initialized)'),
            'Source semantics must be revalidated before every warm or cold cache lookup')
    for literal in [b'game_probe_missing', b'game_probe_invalid', b'game_probe_original_reference',
                    b'!game_probe_assets', b'(game_probe_density!=4&&game_probe_density!=8)']:
        require(literal in source, 'Missing resource diagnostic fallback')
    expected_wrapper = (
        b' (void)render_mirror_marlo_body(target,x,y,bank,index,option,sidekick_style,charge);\n'
        b' blit_sprite2(target,x,y,bank,index);\n'
        b' render_mirror_entity_end();')
    require(expected_wrapper in wrapper, 'Wrapper must preserve the original call once and end its lease')
    require(wrapper.count(b'blit_sprite2(') == 1, 'Original indexed body must execute exactly once')
    require(wrapper.count(b'render_mirror_marlo_body(') == 1, 'Exactly one HD attempt is permitted')
    require(wrapper.count(b'render_mirror_entity_end(') == 1, 'Exactly one mirror lease end is permitted')
    require(b'return a?draw_asset(x,y,a,MIRROR_NORMAL,NULL):false;' in route,
            'Only normal, full-tile rendering at the original x/y is allowed')
    require(b'x<0||x>308||y<-13||y>199' in route,
            'Original horizontal physical-row wrapping must remain indexed fallback')
    require(not any(token in b''.join(additions.values()) for token in
                    [b'is_alive', b'moveOK', b'moveOk', b'this_player', b'rand(', b'mt_rand']),
            'The new drawing boundary must not add gameplay/alive/movement/RNG control')
    require(current['src/mainint.c'].count(b'draw_sidekick_body_sprite2(') == 1,
            'The existing Marlo body site is the only production call site')
    require(baseline['src/mainint.c'].count(OLD_BODY_CALL) == 1, 'Baseline call site is ambiguous')
    require(current['src/mainint.c'].count(OLD_BODY_CALL) == 1,
            'All unrelated sidekicks must retain the original direct indexed blit')


def self_test(current, baseline):
    """In-memory negative mutations prove this audit actually rejects scope creep."""
    cases = []

    def reject(label, path, before=None, after=None, extra=None, omit=False):
        mutation = dict(current)
        if omit:
            del mutation[path]
        elif extra is not None:
            mutation[path] = extra
        else:
            require(before in mutation[path], 'Mutation fixture did not apply: ' + label)
            mutation[path] = mutation[path].replace(before, after, 1)
        try:
            restored, additions = inverse_sources(mutation, baseline)
            finite_contract(mutation, baseline, additions)
        except (AssertionError, ValueError):
            cases.append(label)
        else:
            raise AssertionError('Scope guard incorrectly accepted mutation: ' + label)

    reject('mainint original branch change', 'src/mainint.c', b'if ((playerNum_ == 2 || !twoPlayerMode) && !endLevel)',
           b'if ((playerNum_ == 2 || !twoPlayerMode) && !endLevel && this_player->is_alive)')
    reject('mainint unrelated source byte', 'src/mainint.c', b'#include', b'/* scope creep */\n#include')
    reject('original indexed blitter byte', 'src/sprite.c', b'#include', b'/* changed blitter */\n#include')
    reject('unrelated production header', 'src/player.h', b'#include', b'/* changed player */\n#include')
    reject('new production file', 'src/unapproved_marlo.c', extra=b'void unapproved(void) {}\n')
    reject('deleted production file', 'src/xmas.h', omit=True)
    reject('generic Talon/Mint slot admission', 'src/render_mirror.c', b'int slot=-1,role=0;', b'int slot=536,role=126;')
    reject('generic pixel bridge', 'src/render_mirror.c', b'void render_mirror_pixel(', b'void changed_pixel_bridge(')
    reject('generic compositor', 'src/render_mirror.c', b'static bool draw_asset_filtered(', b'static bool changed_compositor(')
    reject('original source decoder', 'src/render_mirror.c', b'static bool decode_tile(', b'static bool changed_decoder(')
    reject('wrong independent role', 'src/render_mirror.c', b'ASSET_MARLO_BODY=126', b'ASSET_MARLO_BODY=9')
    reject('extra slot capacity', 'src/render_mirror.c', b'static Asset assets[537];', b'static Asset assets[538];')
    reject('wrong resource filename prefix', 'src/render_mirror.c', b'"option-marlo-bank9"', b'"ship"')
    reject('pointer-only source admission', 'src/render_mirror.c', b'!marlo152_source_matches(bank)', b'!bank.data')
    reject('wrong finite source ID', 'src/render_mirror.c', b'decode_tile(bank,152,', b'decode_tile(bank,151,')
    reject('warm cache bypass source identity', 'src/render_mirror.c', b'if(a->initialized)return a->valid?a:NULL;',
           b'if(a->initialized)return a;')
    reject('extra function in Marlo block', 'src/render_mirror.c',
           b'static Asset *marlo152_asset(', b'void sneak_gameplay_change(void) {}\nstatic Asset *marlo152_asset(')
    reject('additional original indexed body call', 'src/entity_draw.c',
           b' (void)render_mirror_marlo_body(target,x,y,bank,index,option,sidekick_style,charge);\n blit_sprite2(target,x,y,bank,index);',
           b' (void)render_mirror_marlo_body(target,x,y,bank,index,option,sidekick_style,charge);\n blit_sprite2(target,x,y,bank,index);\n blit_sprite2(target,x,y,bank,index);')
    reject('hidden original-function whitespace change', 'src/entity_draw.c', b'bool mirrored=render_mirror_entity(',
           b'bool mirrored =render_mirror_entity(')
    return cases


def source_scope(root=ROOT):
    root = Path(root).resolve()
    require(git(ROOT, 'rev-parse', BASE).decode().strip() == BASE, 'Baseline commit not present')
    require(git(ROOT, 'rev-parse', BASE + '^{tree}').decode().strip() == TREE, 'Unpinned baseline tree')
    names = git(ROOT, 'ls-tree', '-r', '--name-only', BASE, '--', 'src').decode().splitlines()
    require(len(names) == len(set(names)) == 153, 'Unexpected baseline production inventory')
    actual = {str(p.relative_to(root)) for p in (root / 'src').rglob('*') if p.is_file() or p.is_symlink()}
    require(actual == set(names), 'Added/deleted production source: ' + str(sorted(actual ^ set(names))))
    for name in names:
        require(not (root / name).is_symlink(), 'Production source became a symlink: ' + name)
    # git object reads, not another working tree, establish all baseline bytes.
    baseline = {name: git(ROOT, 'show', BASE + ':' + name) for name in names}
    current = {name: (root / name).read_bytes() for name in names}
    restored, additions = inverse_sources(current, baseline)
    finite_contract(current, baseline, additions)
    mutations = self_test(current, baseline)
    changed = sorted(name for name in names if current[name] != baseline[name])
    report = {
        'status': 'PASS', 'baseline_commit': BASE, 'baseline_tree': TREE,
        'production_files_checked': len(names), 'production_files_changed': changed,
        'whole_source_byte_inverse': True,
        'mainint_complete_byte_inverse_after_one_finite_body_branch_removal': True,
        'unrelated_sidekicks_keep_original_direct_blit': True,
        'original_loops_state_orbits_order_preserved': True,
        'original_branches_preserved_outside_finite_body_admission': True,
        'generic_talon_mint_get_asset_compositor_pixel_bridge_decoder_blitters_preserved': True,
        'read_asset_only_change': 'independent role126 option-marlo-bank9 filename prefix',
        'new_role': 126, 'new_slot': 536, 'capacity_before': 536, 'capacity_after': 537,
        'active_option': 30, 'active_source_bank': 9, 'active_body_id': 152,
        'active_sidekick_style': 4, 'active_charge': 0,
        'source_fnv1a64': '840f92ed11537363',
        'cold_and_warm_source_semantics_guard': True, 'normal_xmas_rejection_present': True,
        'original_indexed_body_calls_in_wrapper': 1, 'hd_attempts_in_wrapper': 1,
        'registration': {'logical_size': [12, 14], 'anchor': [0, 0], 'original_x_y': True},
        'horizontal_physical_row_wrapping': 'new HD route rejects; exact original indexed path still executes',
        'added_functions': [name for spec in BLOCKS.values() for name in spec['functions']],
        'new_blocks': {label: {'sha256': SHA(raw), 'bytes': len(raw)} for label, raw in additions.items()},
        'source_sha256': {name: {'baseline': SHA(baseline[name]), 'candidate': SHA(current[name]),
                                 'inverse': SHA(restored[name])} for name in names},
        'negative_scope_mutations_rejected': mutations,
        'source_only_audit': True, 'assets_and_docs_scope': 'verified separately by the parent',
        'game_runs': 0, 'commit_or_publish_actions': 0,
        'verification_limit': 'static byte inverse and source-guard mutation tests; no runtime behavior claim',
        'harness_sha256': SHA(Path(__file__).read_bytes()),
    }
    return {'baseline': baseline, 'candidate': current}, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    require(not output.exists(), 'Report must be a new file')
    require(ROOT not in output.parents and output != ROOT, 'Keep reports outside the candidate tree')
    _, report = source_scope(args.root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: all 153 production files pinned; exact five-file Marlo-only byte inverse; '
          + str(len(report['negative_scope_mutations_rejected'])) + ' forbidden mutations rejected; no game run')


if __name__ == '__main__':
    main()
