#!/usr/bin/env python3
"""Finite HUD writer oracle using source-bound domains and extracted C helpers.

No game data or artwork is read. Coordinates are pinned by the audit fixture
hashes; modeled writers are pinned by normalized source hashes, while the actual
segmented-gauge and dBar3 functions are compiled and exercised exhaustively.
A source drift failure requires reviewing the writer proof, not refreshing its
hash automatically. Runtime data, mode equality and lifecycle checks also have
separate loader/renderer tests; this proves their finite geometric premise.
"""
import argparse
import ast
import hashlib
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile

from run_tests import checked_points, check_production_allowlist

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
APPROVED_SHA = '903328448558ea0a8b7ea1e895339602736664bad73b0828b8ace4b3732263d2'
REJECTED_SHA = 'f318812df425dd11419446752272f32917ee97f2c4e8541893c7bc16ed0fe10e'

# Only modeled production functions need frozen hashes. The executable helpers
# below are extracted anew on every run. Ignore comments/whitespace, not tokens.
SOURCE_HASHES = {
    'varz.c:JE_drawOptions': '964dcf5b57743d7c755651cc7f4e42780200bf4343243a3b8ba92a57227ebd56',
    'varz.c:JE_wipeShieldArmorBars': '438e55796936968c7b744d1619a133354af4f9b0367f931ef2fb3ec9a56e8487',
    'varz.c:JE_drawShield': '78915a5416c2b27514821a271698a64c7824c0b85223e31dd0c1df036e65b468',
    'varz.c:JE_drawArmor': 'b3275dcb4c54359a0d19a9bd9768b6d21b59128f71af59ab8c30d8800d89dda7',
    'mainint.c:JE_drawPortConfigButtons': 'c9766cc8fd6cf251466d0d02891c637056e7a1fa8438b53aa122c2a28b13bd7b',
    'mainint.c:JE_playerMovement': 'a0a81df6996a2a101218c9032c87c9637c85d7aaf95eb8fdee5d12682cfa7fc1',
    'mainint.c:JE_mainGamePlayerFunctions': '9da3ef27089e1a02466dde475b3850ff647b4d88b2743a377366a2b1a3de78b6',
    'mainint.c:JE_drawTextWindow': '85b1521acfb78982c34ad2ba20ca8fe5d488abf4239e3f5172800f86ece447a4',
    'fonthand.c:JE_outText': 'aecc0b28194d1d5c7f625dfea6d4081134866e49aee3dff1c0506687db0adc9d',
    'sprite.c:blit_sprite_hv_unsafe': '16e9838664a7ea3649478373e79cf0c839e32d6e52d4376e08d540a93e1582e9',
    'vga256d.c:JE_rectangle': '26c2cde4820d0720ec282575f8ce8afe01838056e47dc1c34f6f5040a7f5202f',
    'vga256d.c:fill_rectangle_xy': '1964c91c0e41ebc55450bf78dff1dc3073f0a47747533268f008813554a1a37a',
    'vga256d.h:fill_rectangle_wh': 'ca89f5ae0366ddda814d41b7cfeca7816d256bd39b736886035d9088ad908bcd',
    'gameplay_hud.c:valid_glyph_moats': 'f8ab9a5ee292a559ad6d3c3f54a57f0952e0670589c6a065906834527cf60cdf',
    'gameplay_hud.c:gameplay_hud_verify_modes': 'a4304d0b838539579530415ae45c83aa24890272ef9be6c9853556ed4510a8cc',
    'tyrian2.c:weapon-display': '0c7c3afe748adb093efd51033a4ed60ec90fc2e24dac84dc9cebd6c380182e6f',
    'tyrian2.c:generator-display': '63bdccc334e8a53e052937cd8d7330de8b2634e7d6667ecd6aee5ea8779d0ed9',
}


def uncomment(source):
    return re.sub(r'/\*.*?\*/|//[^\n]*', '', source, flags=re.S)


def normalized(source):
    return re.sub(r'\s+', '', uncomment(source))


def extract(source, name):
    # Blank comments and string/character literals for brace matching, while
    # retaining byte positions in the exact source returned to the C compiler.
    lexical = re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                     lambda match: ' ' * len(match.group()), source, flags=re.S)
    match = re.search(r'^(?:static\s+)?(?:inline\s+)?[\w *]+\b' + re.escape(name) +
                      r'\([^;{}]*\)\s*\{', lexical, re.M)
    assert match, 'Missing production function: ' + name
    start = lexical.index('{', match.start())
    end, depth = start + 1, 1
    while depth:
        depth += (lexical[end] == '{') - (lexical[end] == '}')
        end += 1
    return source[match.start():end].strip()


def snippets(sources):
    result = {}
    names = {
        'varz.c': ['JE_drawOptions', 'JE_wipeShieldArmorBars', 'JE_drawShield', 'JE_drawArmor'],
        'mainint.c': ['JE_drawPortConfigButtons', 'JE_playerMovement',
                      'JE_mainGamePlayerFunctions', 'JE_drawTextWindow'],
        'fonthand.c': ['JE_outText'],
        'sprite.c': ['blit_sprite_hv_unsafe'],
        'vga256d.c': ['JE_rectangle', 'fill_rectangle_xy'],
        'vga256d.h': ['fill_rectangle_wh'],
        'gameplay_hud.c': ['valid_glyph_moats', 'gameplay_hud_verify_modes'],
    }
    for filename, functions in names.items():
        for name in functions:
            result[filename + ':' + name] = extract(sources[filename], name)
    game = sources['tyrian2.c']
    weapon = game.index('/*---------------------Weapon Display')
    generator = game.index('/*------------------------Power Bar', weapon)
    end = game.index('oldMapX3Ofs = mapX3Ofs;', generator)
    result['tyrian2.c:weapon-display'] = game[weapon:generator]
    result['tyrian2.c:generator-display'] = game[generator:end]
    return result


def require(source, *expressions):
    compact = normalized(source)
    for expression in expressions:
        assert normalized(expression) in compact, 'Source bound changed: ' + expression


def original_geometry_body(name, source):
    # HUF1's additive observers are covered by its actual-writer renderer suite.
    # Keep these two original geometry hashes pinned: strip only exact reviewed
    # notification strings (including the two wrapped early returns), with counts.
    observers = {
        'mainint.c:JE_drawTextWindow': (
            ('render_mirror_text_message_begin(text,textErase>0);', 1, ''),
            ('render_mirror_text_message_backdrop();', 1, ''),
            ('render_mirror_text_message_end();', 1, '')),
        'sprite.c:blit_sprite_hv_unsafe': (
            ('render_mirror_text_glyph_begin(surface,x,y,table,index,false,hue,value);', 1, ''),
            ('{ render_mirror_text_glyph_end(); return; }', 2, 'return;'),
            ('render_mirror_text_glyph_end();', 1, '')),
    }
    for event, count, replacement in observers.get(name, ()):
        assert source.count(event) == count, 'Review changed HUF observer: ' + name
        source = source.replace(event, replacement)
    return source


def source_contract(sources, functions):
    assert functions.keys() == SOURCE_HASHES.keys(), 'Writer source hash coverage changed'
    for name, source in functions.items():
        actual = hashlib.sha256(normalized(original_geometry_body(name, source)).encode()).hexdigest()
        assert actual == SOURCE_HASHES[name], f'{name} drifted; review finite writer proof ({actual})'
    require(sources['tyrian2.c'],
            'JE_outText(VGAScreen, 268, twoPlayerMode ? 76 : 118, levelName, 12, 4);',
            'player[i].shield_max = player[i].shield * 2;')
    require(sources['player.c'], 'this_player->items.weapon[port].power < 11')
    require(sources['episodes.h'], 'JE_byte ammo;')
    require(sources['shots.c'], 'if (power < weaponPort[portNum].poweruse)',
            'power -= weaponPort[portNum].poweruse;')
    require(sources['config.c'], 'char lastLevelName[11], levelName[11];')
    require(sources['mainint.c'], "levelName[10] = '\\0';", 'fread_die(levelName, 1, 10, demo_file);')
    # These are the live compatibility bounds whose accepted domains this
    # oracle enumerates. Separate renderer tests exercise their fail-closed path.
    runtime = extract(sources['render_mirror.c'], 'hud_runtime_compatible')
    require(runtime,
            'hud_sprite_decode(TINY_FONT,(unsigned int)id,6,8,NULL,NULL)',
            'hud_sprite_decode(OPTION_SHAPES,icon,28,13,NULL,NULL)',
            'if((ammo+unit-1)/unit>10)return false;',
            'if(shields[i].mpwr>14)return false;',
            "if(!memchr(levelName,'\\0',sizeof(levelName)))return false;",
            'hud_sprite_decode(OPTION_SHAPES,18+i,10,8,mode_indices[i],mode_opaque[i])',
            'gameplay_hud_verify_modes((const Uint8 (*)[80])mode_indices,(const Uint8 (*)[80])mode_opaque)',
            'if(power>900||lastPower>90||player[0].shield>28||player[0].shield_max>28||player[0].armor>28)return false;',
            'if(player[0].items.weapon[i].power>11||player[0].items.sidekick[i]>OPTION_NUM)return false;',
            'if(ammo<0||maximum<0||ammo>maximum||maximum>255)return false;',
            'if(((unsigned int)maximum+unit-1)/unit>10)return false;')


def expression(text, variables):
    """Evaluate only the integer arithmetic used in checked rectangle calls."""
    node = ast.parse(text.strip(), mode='eval').body
    def visit(item):
        if isinstance(item, ast.Constant) and type(item.value) is int:
            return item.value
        if isinstance(item, ast.Name):
            return variables[item.id]
        if isinstance(item, ast.BinOp):
            left, right = visit(item.left), visit(item.right)
            if isinstance(item.op, ast.Add): return left + right
            if isinstance(item.op, ast.Sub): return left - right
            if isinstance(item.op, ast.Mult): return left * right
            if isinstance(item.op, ast.Div): return left // right
        raise AssertionError('Unsupported writer expression: ' + text)
    return visit(node)


def calls(source, name):
    result = []
    for arguments in re.findall(r'\b' + name + r'\(([^;]*?)\)\s*;', uncomment(source)):
        fields = [part.strip() for part in arguments.split(',')]
        if name in ('fill_rectangle_xy', 'JE_rectangle'):
            assert len(fields) == 6
            result.append(fields[1:5])
    return result


def rectangle(x0, y0, x1, y1):
    assert 0 <= x0 <= x1 < 320 and 0 <= y0 <= y1 < 200, (x0, y0, x1, y1)
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}


def draw(arguments, **variables):
    return rectangle(*(expression(arg, variables) for arg in arguments))


def safe(name, domain, approved):
    overlap = domain & approved
    assert not overlap, (name, 'touches approved rails', sorted(overlap))
    return len(domain)


def model_writers(sources, functions, approved):
    counts = {}
    # All 901 power values map to the 91 finite temp values. Every old/new pair
    # executes the exact production rectangle expressions, including both paths.
    # The charge indicator would overwrite an approved generator rail at
    # chargeLevel=1, but all three writes are inside the player2-only branch.
    # Pin and inspect both that branch and its single-player dispatch caller.
    movement = uncomment(functions['mainint.c:JE_playerMovement'])
    start = movement.index('if (playerNum_ == 2)')
    begin = movement.index('{', start)
    end, depth = begin + 1, 1
    while depth:
        depth += (movement[end] == '{') - (movement[end] == '}')
        end += 1
    charge_calls = [call for call in calls(movement, 'fill_rectangle_xy')
                    if any('chargeLevel' in argument for argument in call)]
    branch_calls = [call for call in calls(movement[begin:end], 'fill_rectangle_xy')
                    if any('chargeLevel' in argument for argument in call)]
    assert len(charge_calls) == 3 and branch_calls == charge_calls
    assert draw(charge_calls[0], chargeLevel=1) & approved
    require(functions['mainint.c:JE_mainGamePlayerFunctions'],
            'else { JE_playerMovement(&player[0], 0, 1, shipGr, shipGrPtr, &mouseX, &mouseY); }')
    generator = functions['tyrian2.c:generator-display']
    require(generator, 'temp = power / 10;', 'if (power > 900) power = 900;')
    power_levels = {power // 10 for power in range(901)}
    assert power_levels == set(range(91))
    rectangles = calls(generator, 'fill_rectangle_xy')
    assert len(rectangles) == 2
    domain = set()
    for temp in power_levels:
        for last_power in power_levels:
            if temp != last_power:
                domain |= draw(rectangles[0 if temp > last_power else 1],
                               temp=temp, lastPower=last_power)
    assert domain == rectangle(269, 12, 276, 103)
    counts['generator (901 powers, 8281 temp pairs)'] = safe('generator', domain, approved)

    weapon = functions['tyrian2.c:weapon-display']
    require(weapon, 'int x = twoPlayerMode ? 286 : 289,',
            'y = (i == 0) ? (twoPlayerMode ? 6 : 17) : (twoPlayerMode ? 100 : 38);',
            'j <= item_power', 'x += 2;')
    clear, = calls(weapon, 'fill_rectangle_xy')
    segment, = calls(weapon, 'JE_rectangle')
    domain = set()
    for y in (17, 38):
        for power in range(12):
            domain |= draw(clear, x=289, y=y)
            for index in range(power):
                domain |= draw(segment, x=289 + 2 * index, y=y)
    assert domain == rectangle(289, 17, 310, 19) | rectangle(289, 38, 310, 40)
    counts['weapon power 0..11'] = safe('weapon bars', domain, approved)

    options = functions['varz.c:JE_drawOptions']
    ys = re.search(r'hud_sidekick_y\[2\]\[2\]\s*=\s*\{(.*?)\};',
                   uncomment(sources['varz.h']), re.S)
    assert ys
    values = list(map(int, re.findall(r'\d+', ys.group(1))))
    assert values == [64, 82, 108, 126]
    clear, = calls(options, 'fill_rectangle_xy')
    domain = set()
    for y in values[:2]:
        domain |= draw(clear, y=y)
        # Full opaque boxes conservatively cover every valid decoded icon,
        # regardless of its RLE transparency, shape, palette or item identity.
        for width in range(1, 29):
            for height in range(1, 14):
                domain |= rectangle(284, y, 284 + width - 1, y + height - 1)
        discharge = ['284', 'y', '312', 'y + 2']
        require(functions['mainint.c:JE_playerMovement'],
                'fill_rectangle_xy(VGAScreenSeg, 284, y, 312, y + 2, 0);',
                'const int y = hud_sidekick_y[twoPlayerMode ? 1 : 0][i] + 13;')
        domain |= draw(discharge, y=y + 13)
    assert domain == rectangle(284, 64, 312, 79) | rectangle(284, 82, 312, 97)
    counts['sidekick clear/icon/discharge'] = safe('sidekick', domain, approved)

    wipe = calls(functions['varz.c:JE_wipeShieldArmorBars'], 'fill_rectangle_xy')
    assert len(wipe) == 6
    domain = set()
    # The parsed player member expressions are replaced only by their scalar
    # test-state names; all coordinate arithmetic remains production text.
    for index, member in ((0, 'shield'), (3, 'armor')):
        args = [arg.replace('player[0].' + member, 'level') for arg in wipe[index]]
        for level in range(29):
            domain |= draw(args, level=level)
    shield = functions['varz.c:JE_drawShield']
    marker, = calls(shield, 'JE_rectangle')
    require(shield, 'const uint y = 193 - (player[0].shield_max * 2);',
            'JE_dBar3(VGAScreen, 270, 194, player[0].shield, 144);')
    require(functions['varz.c:JE_drawArmor'],
            'JE_dBar3(VGAScreen, 307, 194, player[0].armor, 224);',
            'if (player[i].armor > 28) player[i].armor = 28;')
    for maximum in range(29):
        domain |= draw(marker, y=193 - maximum * 2)
    assert min(y for _, y in domain) == 137
    counts['shield/armor wipe and capacity 0..28'] = safe('shield/armor', domain, approved)

    # JE_outText advances by width+1 (2..7), spaces by 6, or 0 for control/
    # missing characters. Dynamic programming exhausts all reachable prefixes,
    # including mixed widths; a full 6x8 box conservatively covers every glyph.
    text = functions['fonthand.c:JE_outText']
    require(text, 'x += 6;', 'x += sprite(TINY_FONT, sprite_id)->width + 1;',
            'blit_sprite_hv_unsafe(screen, x, y, TINY_FONT, sprite_id, colorbank, brightness + bright);')
    starts, domain = {268}, set()
    prefix_states = 0
    for _ in range(10):
        prefix_states += len(starts)
        for start in starts:
            for dy in range(8):
                for dx in range(6):
                    address = (118 + dy) * 320 + start + dx
                    domain.add((address % 320, address // 320))
        starts = {x + advance for x in starts for advance in (0, 2, 3, 4, 5, 6, 7)}
    assert max(starts) == 338  # Last origin is at most331, last opaque column336.
    assert {(x, y) for x, y in domain if y == 126} == {(x, 126) for x in range(17)}
    counts[f'level-name 10-character prefix states ({prefix_states})'] = safe('level name including wrap', domain, approved)
    # A ninth glyph row reaches approved right-rail pixels: this is an effective
    # bound, not an accidental assertion on one short level name.
    assert (rectangle(315, 118, 319, 126) & approved) - domain
    return counts


def semantic_exclusions(functions, approved, rejected):
    mode_calls = re.findall(r'blit_sprite\(VGAScreenSeg,\s*(\d+),\s*(\d+),\s*OPTION_SHAPES,\s*(18|19)\)',
                            functions['mainint.c:JE_drawPortConfigButtons'])
    assert sorted(map(tuple, mode_calls)) == [('285', '44', '18'), ('285', '44', '19'),
                                             ('302', '44', '18'), ('302', '44', '19')]
    mode_area = rectangle(285, 44, 294, 51) | rectangle(302, 44, 311, 51)
    guarded = approved & mode_area
    assert len(guarded) == 26 and len(approved - guarded) == 284
    assert len(guarded & rectangle(285, 44, 294, 51)) == 12
    assert len(guarded & rectangle(302, 44, 311, 51)) == 14
    # All mode points need decoded opaque A/B + captured PIC3 equality. The
    # actual loader test exercises every owned/unowned local offset and failure.
    require(functions['gameplay_hud.c:gameplay_hud_verify_modes'],
            'opaque[0][local] != 255', 'opaque[1][local] != 255',
            'indices[0][local] != indices[1][local]',
            'indices[0][local] != source_indices[source]', 'if (!captured) return false;')
    glyphs, moats = set(), set()
    for x, letters in ((285, 6), (296, 5)):
        for index in range(letters):
            y = 138 + 6 * index
            box = rectangle(x, y, x + 4, y + 4)
            glyphs |= box
            moats |= rectangle(x - 1, y - 1, x + 5, y + 5) - box
    assert len(glyphs) == 275 and len(moats) == 201
    safe('all eleven full glyph boxes', glyphs, approved)
    safe('all glyph moats', moats, approved)
    for name, area in (
        ('FRONT semantic window', rectangle(284, 4, 311, 20)),
        ('REAR semantic window', rectangle(284, 25, 311, 40)),
        ('complete red lamp/lens', rectangle(269, 3, 276, 7)),
        ('bottom message ribs/text', rectangle(16, 189, 263, 199)),
    ):
        safe(name, area, approved)
    assert len(rejected) == 261 and not approved & rejected
    return approved - guarded


HELPER_HARNESS = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
typedef unsigned int uint;
typedef uint8_t Uint8;
typedef uint8_t JE_byte;
typedef int JE_integer;
typedef struct { int unused; } SDL_Surface;
static unsigned char approved[64000], written[64000];
static unsigned long calls;
static const char *group;
static void record(int x, int y, int x2, int y2)
{
    assert(x >= 0 && x <= x2 && x2 < 320 && y >= 0 && y <= y2 && y2 < 200);
    ++calls;
    for (int yy = y; yy <= y2; ++yy)
        for (int xx = x; xx <= x2; ++xx) {
            if (approved[yy * 320 + xx]) {
                fprintf(stderr, "%s overlaps approved rail at %d,%d\n", group, xx, yy);
                exit(1);
            }
            written[yy * 320 + xx] = 1;
        }
}
/* Inclusive filled rectangles conservatively cover JE_rectangle's outline.
 * Its production body and coordinate semantics are independently source-pinned. */
static void JE_rectangle(SDL_Surface *surface, int x, int y, int x2, int y2, int color)
{ (void)surface; (void)color; record(x,y,x2,y2); }
static void fill_rectangle_wh(SDL_Surface *surface, int x, int y, uint w, uint h, Uint8 color)
{ (void)surface; (void)color; record(x,y,x+(int)w-1,y+(int)h-1); }
/*EXTRACTED_HELPERS*/
int main(void)
{
    /*APPROVED_INITIALIZATION*/
    SDL_Surface surface = {0};
    group = "extracted JE_dBar3";
    for (int level = 0; level <= 28; ++level) {
        JE_dBar3(&surface,270,194,level,144);
        JE_dBar3(&surface,307,194,level,224);
    }
    unsigned pixels = 0;
    for (int i=0;i<64000;++i) if(written[i]) {
        assert(i/320 >= 137 && i/320 <= 194);
        assert((i%320 >= 270 && i%320 <= 278) || (i%320 >= 307 && i%320 <= 315));
        ++pixels;
    }
    assert(pixels == 2u*9u*58u);
    for (int i=0;i<64000;++i) written[i]=0;
    group = "extracted draw_segmented_gauge";
    unsigned ammo_states = 0;
    /* Original ammo fields are bytes. Enumerate all table values accepted by
     * the runtime ceiling, and every legal remaining-ammo value including
     * partial segments, at both single-player origins. */
    for (uint maximum=0;maximum<=255;++maximum) {
        uint unit=maximum/10; if(!unit)unit=1;
        if((maximum+unit-1)/unit>10)continue;
        for (uint value=0;value<=maximum;++value) {
            ++ammo_states;
            draw_segmented_gauge(&surface,284,77,112,2,2,unit,value);
            draw_segmented_gauge(&surface,284,95,112,2,2,unit,value);
        }
    }
    pixels=0;
    for(int i=0;i<64000;++i) if(written[i]) {
        assert((i/320>=77&&i/320<=78)||(i/320>=95&&i/320<=96));
        assert(i%320>=284&&i%320<=312&&(i%320-284)%3<2);
        ++pixels;
    }
    assert(pixels==80);
    printf("PASS extracted C writers: 58 shield/armor states; %u accepted ammo states; %lu rectangle calls\n",ammo_states,calls);
    return 0;
}
'''


def run_helpers(sources, approved, args):
    source = HELPER_HARNESS.replace('/*EXTRACTED_HELPERS*/',
        extract(sources['nortvars.c'], 'JE_dBar3') + '\n' +
        extract(sources['vga256d.c'], 'draw_segmented_gauge'))
    source = source.replace('/*APPROVED_INITIALIZATION*/', '\n'.join(
        f'approved[{y * 320 + x}]=1;' for x, y in sorted(approved)))
    with tempfile.TemporaryDirectory(prefix='hud-writer-oracle-') as temporary:
        path = Path(temporary)
        (path / 'writer.c').write_text(source)
        command = shlex.split(args.cc) + ['-std=c99', '-O1', '-g', '-Wall', '-Wextra',
                                         '-Werror', '-Wpedantic']
        if args.sanitize:
            command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-no-pie']
        subprocess.run(command + [str(path / 'writer.c'), '-o', str(path / 'writer')], check=True)
        environment = os.environ.copy()
        if args.sanitize:
            environment['ASAN_OPTIONS'] = 'detect_leaks=0:halt_on_error=1'
            environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
        subprocess.run([str(path / 'writer')], check=True, env=environment)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sanitize', action='store_true')
    parser.add_argument('--cc', default=os.environ.get('CC', 'cc'))
    args = parser.parse_args()
    approved = set(checked_points(HERE / 'approved-rails.spans', 310, APPROVED_SHA))
    rejected = set(checked_points(HERE / 'rejected-candidates.spans', 261, REJECTED_SHA))
    check_production_allowlist(ROOT, HERE)
    filenames = ('varz.c', 'varz.h', 'mainint.c', 'fonthand.c', 'sprite.c', 'vga256d.c',
                 'vga256d.h', 'nortvars.c', 'tyrian2.c', 'shots.c', 'player.c', 'config.c',
                 'gameplay_hud.c', 'render_mirror.c', 'episodes.h')
    sources = {name: (ROOT / 'src' / name).read_text() for name in filenames}
    functions = snippets(sources)
    source_contract(sources, functions)
    unguarded = semantic_exclusions(functions, approved, rejected)
    counts = model_writers(sources, functions, approved)
    run_helpers(sources, approved, args)
    assert len(unguarded) == 284
    print('PASS finite writer oracle: exact 310 approved / 261 excluded; 284 disjoint rails + 26 mode-equality guarded points; 11 glyph boxes / 201 moat points')
    for name, count in counts.items():
        print(f'  {name}: {count} possible write pixels, zero approved intersections')


if __name__ == '__main__':
    main()
