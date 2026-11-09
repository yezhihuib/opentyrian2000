"""Execute native shell allocation/update blocks with the actual lifecycle hooks.

The engine blocks and record types are extracted without rewriting them; the
fixture supplies matching fixed-width integer aliases and a minimal Player.
Weapon records, actors and frame/event receipts are synthetic; source hashes,
body shape and outer level admission are stubbed. The real event259 cutoff runs.
Drawing, audio, RNG and damage effects are stubbed: this is not an original-data
replay, native RLE/display test, complete enemy constructor or game acceptance.
"""
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_smallrocks_family import ROOT, SRC


def block(source, marker):
    """Keep the marked statement/declaration and its balanced body verbatim."""
    start = source.index(marker)
    opening = source.index('{', start)
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


def function(source, name):
    match = re.search(r'^(?:static )?\w+ ' + re.escape(name) + r'\(', source, re.M)
    if match is None:
        raise AssertionError('Missing real function: ' + name)
    return block(source[match.start():], match.group())


class TankShellLifecycleTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'), 'requires C compiler')
    def test_native_allocation_motion_retirement(self):
        shell = (SRC / 'enemy_shot_family_mirror.inc').read_text()
        tank = (SRC / 'tank194_family_mirror.inc').read_text()
        engine = (SRC / 'tyrian2.c').read_text()
        varz = (ROOT / 'src/varz.h').read_text()
        episodes = (ROOT / 'src/episodes.h').read_text()
        declarations = shell[shell.index('static struct {unsigned checked'):
                             shell.index('static const char *es_root')]
        tank_declarations = tank[tank.index('typedef struct {'):
                                 tank.index('static const char *t194_root')]
        names = ('es_requested', 'es_scope', 'es_state', 'es_equal', 'es_fail',
                 'es_lose', 'es_tick', 'es_reset',
                 'render_mirror_enemy_shot_pool_begin',
                 'render_mirror_enemy_shot_actor_allocated',
                 'render_mirror_enemy_shot_allocated',
                 'render_mirror_enemy_shot_initialized', 'es_live', 'es_motion',
                 'render_mirror_enemy_shot_before_motion',
                 'render_mirror_enemy_shot_after_motion',
                 'render_mirror_enemy_shot_retired',
                 'render_mirror_enemy_shot_after_animation',
                 'render_mirror_enemy_shot_before_draw',
                 'render_mirror_enemy_shot_after_draw', 'es_draw_current')
        tank_names = ('t194_birth_index', 't194_event_matches',
                      't194_events_current', 't194_scope',
                      'render_mirror_tank194_family_retired', 't194_witness',
                      'render_mirror_tank194_family_event_before')
        records = (block(episodes, 'typedef struct\n{') + ' JE_WeaponType;\n' +
                   block(varz, 'struct JE_SingleEnemyType') + ';\n' +
                   block(varz, 'struct JE_EventRecType') + ';\n' +
                   block(varz[varz.index('typedef JE_byte JE_EnemyAvailType'):],
                         'typedef struct {') + ' EnemyShotType;\n')
        # Both blocks include the original callback ordering and pool writes.
        allocation = block(engine, 'for (int tempCount = weapons[temp3].multi;')
        motion = block(engine[engine.index('/* Draw Enemy Shots */'):],
                       'for (int z = 0; z < ENEMY_SHOT_MAX; z++)')
        harness = (ROOT / 'tests/fixtures/tank_shell_lifecycle.c').read_text()
        replacements = {
            'RECORDS': records, 'DECLARATIONS': declarations,
            'TANK_DECLARATIONS': tank_declarations,
            'FUNCTIONS': '\n'.join(function(shell, name) for name in names),
            'TANK_FUNCTIONS': '\n'.join(function(tank, name) for name in tank_names),
            'ALLOCATION': allocation, 'MOTION': motion,
        }
        for key, value in replacements.items():
            harness = harness.replace('\n' + key + '\n', '\n' + value + '\n')
        with tempfile.TemporaryDirectory() as temp:
            c, binary = Path(temp) / 'shell.c', Path(temp) / 'shell'
            c.write_text(harness)
            flags = shlex.split(os.environ.get('TANK_SHELL_TEST_CFLAGS', ''))
            subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror',
                            '-Wno-unused-variable', '-Wno-unused-function',
                            '-pedantic', '-I', str(SRC), *flags,
                            str(c), '-lm', '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    unittest.main()
