"""Rebuild the four finite Pulse-Cannon textures and review sheets from imagegen masters.

Pillow only. No procedural repaint, recolor, alpha remask, independent lobe shift,
extra animation, or game-data dependency. This writes only beside this script.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, struct, zipfile

ROOT = Path(__file__).resolve().parent
IDS = [58, 60, 62, 165]
TRANSFORMS = {
    58: {'crop': None, 'resize': [96, 104], 'reason': 'Whole-sprite height registered to accepted59 family; transparent last8 source pixels.'},
    60: {'crop': None, 'resize': [96, 112], 'reason': 'Whole generated canvas registered to original12x14 tile.'},
    62: {'crop': [126, 0, 1215, 1173], 'resize': [96, 112], 'reason': 'Whole-sprite horizontal registration restores original broad five-lobe spread after generation narrowed it; no individual-lobe change.'},
    165: {'crop': None, 'resize': [96, 112], 'reason': 'Whole generated canvas registered to original12x14 tile.'},
}
SHA = lambda data: hashlib.sha256(data).hexdigest()
for sub in ['exports', 'runtime', 'review']:
    (ROOT / sub).mkdir(exist_ok=True)

def bbox(alpha, threshold):
    return alpha.point(lambda value: 255 if value > threshold else 0).getbbox()

metrics = {}
frames = []
for sprite in IDS:
    source = ROOT / 'selected-masters' / f'pulse{sprite}-master.png'
    master = Image.open(source).convert('RGBA')
    transform = TRANSFORMS[sprite]
    rendered = master.crop(transform['crop']) if transform['crop'] else master
    rendered = rendered.resize(tuple(transform['resize']), Image.Resampling.LANCZOS)
    out = Image.new('RGBA', (96, 112))
    out.paste(rendered, (0, 0))
    png_path = ROOT / 'exports' / f'shapes8-id{sprite}-96x112.png'
    out.save(png_path)
    header = [80000 + sprite, 8, 12, 14, 0, 0]
    raw = b'HDR1' + struct.pack('<6I', *header) + out.tobytes()
    hda_path = ROOT / 'runtime' / f'bullet-{sprite}-8.hda'
    hda_path.write_bytes(raw)
    alpha = out.getchannel('A')
    histogram = alpha.histogram()
    edge = list(alpha.crop((0, 0, 96, 1)).getdata()) + list(alpha.crop((0, 111, 96, 112)).getdata()) + list(alpha.crop((0, 0, 1, 112)).getdata()) + list(alpha.crop((95, 0, 96, 112)).getdata())
    metrics[str(sprite)] = {
        'master_size': list(master.size), 'output_size': [96, 112],
        'alpha_bbox_gt16': bbox(alpha, 16), 'alpha_bbox_gt128': bbox(alpha, 128),
        'alpha_bbox_gt240': bbox(alpha, 240), 'max_outer_edge_alpha': max(edge),
        'alpha_effective_area_logical_pixels': round(sum(a * count for a, count in enumerate(histogram)) / 255 / 64, 4),
        'pixels_alpha1_to239': sum(histogram[1:240]), 'pixels_alpha240_to255': sum(histogram[240:]),
        'rgba_sha256': SHA(out.tobytes()), 'hda_rgba_exact': raw[28:] == out.tobytes(),
    }
    frames.append({
        'runtime_role': 'player_projectile_only', 'sprite_sheet': 8, 'sprite_id': sprite,
        'binding_key': f'8:{sprite}', 'runtime_asset_key': 80000 + sprite,
        'logical_size': [12, 14], 'anchor': [0, 0], 'density': 8,
        'master': str(source.relative_to(ROOT)), 'master_sha256': SHA(source.read_bytes()),
        'transform': dict(transform, paste=[0, 0], canvas=[96, 112], resampler='Lanczos'),
        'source_png': str(png_path.relative_to(ROOT)), 'source_png_sha256': SHA(png_path.read_bytes()),
        'hda': str(hda_path.relative_to(ROOT)), 'hda_sha256': SHA(raw), 'header_u32': header,
    })

accepted = ROOT / 'review' / 'accepted59-unchanged.png'
assert SHA(accepted.read_bytes()) == 'b95925b600464c12244b292d14c5c3b0d05fa8ed125b111459c479360afa3304'
manifest = {
    'identity': 'pulse-cannon-four-missing-heads-v1',
    'status': 'Root approved offline actual2x/4x revision for runtime trial; in-game acceptance pending.',
    'scope': 'Exactly four new static spriteSheet8 player heads58/60/62/165. Accepted59 untouched. No animation or weapon-table changes.',
    'tool': 'Built-in image_gen; prompt set in prompts/. Selected output masters retained.',
    'alpha': 'Straight RGBA preserved from generated masters; only whole-canvas crop/resample/placement during export.',
    'accepted59': {'preserved': True, 'anchor': [-1, 0], 'source_png_sha256': SHA(accepted.read_bytes()), 'included_as_runtime_binding': False},
    'frames': frames,
    'runtime_checks_required': ['Legal Pulse-Cannon front-port1 powers1,2,6,11', 'Integer2x and4x, classic control, HD, missing and invalid fallback', 'Observed identities58,59,60,62,165 with correct source bank and anchor', 'Real in-game color, nucleus, halo, tail, origin and occlusion review', 'State/RNG/collision parity and no weapon timing changes'],
    'coverage_limit': 'Completes only Pulse-Cannon static head artwork after runtime acceptance; not all player weapons or upgrades.',
}
(ROOT / 'candidate-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(ROOT / 'validation-metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')

# Native output review: each sprite is shown at actual4x and2x, without magnification.
board = Image.new('RGB', (900, 390), (20, 20, 20))
draw = ImageDraw.Draw(board)
draw.text((8, 7), 'Pulse-Cannon / true4x and2x / offline source-over / accepted59 unchanged', fill='white')
alpha_board = Image.new('RGB', (900, 180), (20, 20, 20))
ad = ImageDraw.Draw(alpha_board)
ad.text((8, 7), 'Actual alpha at4x and2x / broad translucent shoulder / not a runtime capture', fill='white')
for n, sprite in enumerate([58, 59, 60, 62, 165]):
    x = n * 180
    im = Image.open(accepted if sprite == 59 else ROOT / 'exports' / f'shapes8-id{sprite}-96x112.png')
    label = f'8:{sprite}' + (' accepted' if sprite == 59 else ' new')
    draw.text((x + 8, 29), label, fill='white')
    ad.text((x + 8, 29), label, fill='white')
    for row, bg in enumerate([(0, 0, 0), (215, 215, 215), (84, 105, 69)]):
        y = 48 + row * 110
        draw.rectangle((x, y, x + 179, y + 109), fill=bg)
        for scale, offset in [(4, 24), (2, 110)]:
            small = im.resize((12 * scale, 14 * scale), Image.Resampling.NEAREST)
            board.paste(small, (x + offset, y + 28), small)
            if row == 0:
                a = small.getchannel('A').convert('RGB')
                alpha_board.paste(a, (x + offset, 65))
board.save(ROOT / 'review' / 'contact-true4x2x.png')
alpha_board.save(ROOT / 'review' / 'alpha-true4x2x.png')

# Packages intentionally omit original game bitmap references and rejected masters.
common = [ROOT / name for name in ['candidate-manifest.json', 'validation-metrics.json', 'README.txt']]
runtime_files = common + list((ROOT / 'exports').glob('*.png')) + list((ROOT / 'runtime').glob('*.hda')) + [ROOT / 'review' / 'contact-true4x2x.png', ROOT / 'review' / 'alpha-true4x2x.png']
source_files = common + [ROOT / 'export_final.py'] + list((ROOT / 'selected-masters').glob('*.png')) + list((ROOT / 'prompts').glob('*.txt')) + list((ROOT / 'review').glob('*.png'))
for name, files in [('pulse-cannon-four-heads-v1-runtime.zip', runtime_files), ('pulse-cannon-four-heads-v1-source.zip', source_files)]:
    with zipfile.ZipFile(ROOT / name, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(ROOT))
print(json.dumps({'frames': IDS, 'runtime_count': len(IDS), 'accepted59_unchanged': True, 'runtime_acceptance': 'pending', 'artifacts': ['pulse-cannon-four-heads-v1-runtime.zip', 'pulse-cannon-four-heads-v1-source.zip']}, indent=2))
