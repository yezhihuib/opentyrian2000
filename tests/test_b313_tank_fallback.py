#!/usr/bin/env python3
"""Real tank/terrain/player includes, native RLE, writer and SDL ASan/UBSan.

Expected callbacks come from the frozen 03c5968bda89ae17 archive, independently
encoded into a synthetic 46204-byte NEWSHP bank. The original bank hash and
record194 digest are explicit fixture substitutions; the real source binding,
palette, scope/event, witness and live-shape predicates otherwise run unchanged.
Constructor/event execution is not simulated: raw lifetime receipts are declared
fixture inputs. Eight real authored tank files and five player files are loaded.
This is isolated renderer acceptance, not original-game or full-level acceptance.
"""
from pathlib import Path
import os
import re
import shlex
import subprocess
import tempfile
import unittest
from test_b313_player_fallback import function, ROOT, SRC, ARCHIVE

TANK_ART = ROOT / 'assets/hd/artwork/type15-eightheading-smooth-contour-v2/output'


def lifetime_fixture():
    source = (SRC / 'tank194_family_mirror.inc').read_text()
    names = ('t194_root', 't194_enabled', 't194_geometry', 't194_birth_index', 't194_event_matches',
             't194_events_current', 't194_scope', 't194_source', 't194_colors',
             't194_script', 't194_script_equal', 't194_constructor_stats',
             't194_shape', 't194_witness')
    functions = '\n'.join(function(source, name) for name in names)
    assert functions.count('UINT64_C(0xe2413e3aeab4d908)') == 1
    functions = functions.replace('UINT64_C(0xe2413e3aeab4d908)', 'synthetic_tank_bank_pin')
    fields = set(re.findall(r'e->(\w+)', functions))
    fields -= {'sprite2s', 'enemydatofs', 'freq', 'tur', 'egr', 'eshotmultipos', 'eshotwait'}
    declarations = source[source.index('typedef struct {'):source.index('static struct {bool checked')]
    return '''/* Exact current pure admission predicates with documented fixtures. */
#define COUNTOF(a) (sizeof(a)/sizeof((a)[0]))
static uint64_t synthetic_tank_bank_pin;
static bool tank_scope_ok=true;
static int enemyDat[256],difficultyLevel=2,terrain_file='z';
static unsigned maxEvent=731,curLoc=100;
static unsigned enemyAvail[100],enemySpriteSheetIds[4];
static Sprite2_array enemySpriteSheets[4],spriteSheet8;
struct JE_SingleEnemyType {Sprite2_array *sprite2s;int *enemydatofs;
 unsigned freq[3],tur[3],egr[20],eshotmultipos[3],eshotwait[3];
''' + ' int ' + ','.join(sorted(fields-{'enemycycle','armorleft','linknum'})) + '; unsigned enemycycle,armorleft,linknum;\n} ;\n' + '''
static struct JE_SingleEnemyType enemy[100];
struct JE_EventRecType {unsigned eventtime,eventtype;int eventdat,eventdat2,eventdat3,eventdat4,eventdat5,eventdat6;};
static struct JE_EventRecType fixture_events[731];
static uint64_t asteroid1_record_stamp(unsigned record)
{return record==194?UINT64_C(0xa9beba644b307039):0;}
static bool t194_level_scope(void)
{const char *p=getenv("TANK194_FAMILY_ENABLE");return tank_scope_ok&&p&&!strcmp(p,"1");}
#include "tank194_native.inc"
''' + declarations + functions


class TankFallbackTests(unittest.TestCase):
    def test_real_hooks_and_independence(self):
        terrain = (SRC / 'b313_terrain_fallback_mirror.inc').read_text()
        tank = (SRC / 'b313_tank_fallback_mirror.inc').read_text()
        code = re.sub(r'/\*.*?\*/', '', tank, flags=re.S)
        self.assertNotRegex(code, r'\bt194_(?:frame|ready|fail|resources)\b')
        self.assertNotIn('b313_family_writer_pixel(', code)
        pixel = function(terrain, 'tf_pixel')
        self.assertEqual(pixel.count('b313_family_writer_pixel('), 1)
        self.assertLess(pixel.index('b313_family_writer_pixel('), pixel.index('kf_pixel('))
        self.assertLess(pixel.index('kf_pixel('), pixel.index('tf.expected[off]=*address'))
        self.assertLess(pixel.index('pf_pixel('), pixel.index('tf.expected[off]=*address'))
        present = function(terrain, 'tf_present')
        self.assertLess(present.index('if(!current)'), present.index('kf_compose()'))
        self.assertLess(present.index('kf_present_begin('), present.index('asset_debug_readback('))
        self.assertLess(present.index('SDL_RenderPresent('), present.index('kf_present_end()'))
        canvas = (SRC / 'b313_family_canvas_mirror.inc').read_text()
        self.assertIn('kf_end()', function(canvas, 'family_entity_end'))
        tyrian = (SRC / 'tyrian2.c').read_text()
        genuine = function(tyrian[re.search(r'inline static void blit_enemy\([^;\n]+\)\n\{', tyrian).start():], 'blit_enemy')
        self.assertLess(genuine.index('render_mirror_tank_fallback_tile_begin('), genuine.index('render_mirror_family_tile('))
        self.assertIn('render_mirror_tank_fallback_phase_begin()', tyrian)
        self.assertIn('render_mirror_tank_fallback_phase_end()', tyrian)
        for name, hook in [('tf_fail','kf_shared_fail()'),('tf_reset','kf_reset()'),('tf_release','kf_release()')]:
            self.assertIn(hook,function(terrain,name))

    def test_real_assets_native_writer_and_software_present(self):
        pkg = shlex.split(os.environ.get('PKG_CONFIG', 'pkg-config'))
        flags = shlex.split(subprocess.check_output(pkg + ['--cflags', 'sdl2'], text=True))
        libs = shlex.split(subprocess.check_output(pkg + ['--libs', 'sdl2'], text=True))
        with tempfile.TemporaryDirectory(prefix='b313-tank-fallback-') as temp:
            directory = Path(temp)
            oracle = (ARCHIVE / 'tank194_native.inc').read_text().replace('t194_', 'oracle_tank_')
            (directory / 'tank_fallback_oracle.inc').write_text(oracle)
            (directory / 'tank_fallback_lifetime.inc').write_text(lifetime_fixture())
            oracle = (ARCHIVE / 'player_ship_native.inc').read_text()
            oracle = oracle[:oracle.index('static const PlayerShipSpec *ps_spec')]
            oracle = oracle[oracle.index('static const PlayerShipWrite'):]
            oracle = re.sub(r'typedef struct \{.*?\} PlayerShipSpec;', '', oracle, flags=re.S)
            oracle = oracle.replace('ps_native_', 'oracle_native_').replace('ps_specs', 'oracle_specs')
            (directory / 'player_fallback_oracle.inc').write_text(oracle)
            (directory / 'player_fallback_native.inc').write_text('\n'.join(function((SRC / 'sprite.c').read_text(), name) for name in ('blit_sprite2','blit_sprite2_blend','blit_sprite2_darken','blit_sprite2_filter')))
            (directory / 'player_fallback_helpers.inc').write_text(
                function((ROOT / 'src/asteroid1_ten_mirror.inc').read_text(), 'asteroid1_stamp') + '\n' +
                function((SRC / 'render_mirror.c').read_text(), 'blend_rgba'))
            bad_roots = [str(directory / 'absent'), '']
            for kind in ('missing', 'magic', 'dimensions', 'truncated', 'payload', 'trailing'):
                bad = directory / kind
                bad.mkdir()
                for index in (91,45,93,39,43,129,41,131):
                    data = bytearray((TANK_ART / f'enemy-newsh2-{index}-8.hda').read_bytes())
                    if index == 131:
                        if kind == 'missing': continue
                        if kind == 'magic': data[0] ^= 1
                        elif kind == 'dimensions': data[12] ^= 1
                        elif kind == 'truncated': data.pop()
                        elif kind == 'payload': data[-17] ^= 1
                        elif kind == 'trailing': data.append(0)
                    (bad / f'enemy-newsh2-{index}-8.hda').write_bytes(data)
                bad_roots.append(str(bad))
            executable = directory / 'test'
            command = shlex.split(os.environ.get('CC', 'cc')) + [
                '-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
                '-DB313_FAMILY_CANVAS_DIAGNOSTIC=1',
                '-fsanitize=address,undefined','-fno-sanitize-recover=all',
                '-fno-omit-frame-pointer','-no-pie',
                '-I'+str(directory),'-I'+str(SRC),'-I'+str(ROOT/'src'),
            ] + flags + [str(ROOT/'tests/test_b313_tank_fallback.c'),
                         str(SRC/'b313_family_writer.c'),'-o',str(executable)] + libs
            subprocess.run(command,check=True)
            subprocess.run([str(executable),str(ROOT/'assets/hd/current-compat/talon'),str(TANK_ART)]+bad_roots,
                           check=True,env={**os.environ,'SDL_VIDEODRIVER':'dummy',
                                          'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1',
                                          'UBSAN_OPTIONS':'halt_on_error=1'})


if __name__ == '__main__':
    unittest.main()
