"""Prepare archived weapon71 hooks with the CURRENT renderer and terrain binding.

Diagnostic source only; original game data and generated captures stay outside Git.
The archived prepare-effects command remains an exact historical reproduction.
"""
from pathlib import Path
import argparse, shutil, subprocess, sys

repo = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
subprocess.run([sys.executable, str(Path(__file__).with_name('prepare-effects.py')),
                '--family', 'green-trail', '--output', str(a.output)], check=True)
out = a.output.resolve()
archive = (repo / 'prototype/fixtures/effects/green-trail/overrides/src/render_mirror.c').read_text()
renderer = (repo / 'src/render_mirror.c').read_text()
start = archive.index('/* Private read-only green-trail matrix observer;')
end = archive.index('/* Display grouping requires', start)
observer = archive[start:end]
marker = '/* Display grouping requires'
assert renderer.count(marker) == 1
renderer = renderer.replace(marker, observer + marker, 1)
branch = 'bool green_blend=explosion_blend&&a->index>=78&&a->index<=84;'
assert renderer.count(branch) == 1
renderer = renderer.replace(branch, branch[:-1] + '&&!getenv("OT_GREEN_POINT_BASELINE");')
(out / 'src/render_mirror.c').write_text(renderer)
# Historical preparation strips the reviewed layer2 registration; current
# renderer review needs that exact current production registration restored.
shutil.copy2(repo / 'src/tyrian2.c', out / 'src/tyrian2.c')
entity = out / 'src/entity_draw.c'
s = entity.read_text()
s = '#include <stdio.h>\n#include <stdlib.h>\n' + s
marker = '\tgame_probe_draw(role,index,x,y,style,layout,mirrored);'
assert s.count(marker) == 1
s = s.replace(marker, marker + '''
	if (getenv("OT_FX_FIXTURE") && role == 8 && index >= 214 && index <= 217) {
		static FILE *head_trace;
		if (!head_trace) {
			head_trace = fopen("green-head-draws.tsv", "w");
			if (!head_trace) exit(2);
			fprintf(head_trace, "tick\\tindex\\tx\\ty\\tstyle\\tlayout\\tmirrored\\n");
		}
		fprintf(head_trace, "%u\\t%u\\t%d\\t%d\\t%d\\t%d\\t%d\\n",
		        game_probe_tick, index, x, y, style, layout, mirrored);
		fflush(head_trace);
	}
''')
entity.write_text(s)
print('Current renderer and terrain binding plus archived read-only observers installed:', out)
print('OT_FX_FIXTURE=1: original loaded weapon71; OT_FX_PROBE=1: smoke observer')
print('OT_GREEN_POINT_BASELINE=1: original point brightness, otherwise current smoothing')
