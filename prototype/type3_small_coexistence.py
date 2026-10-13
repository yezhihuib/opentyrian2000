"""Finite test-only projection of the six small sprites to published b2a6e4a.
Newly regenerated during recovery; delegates source-byte validation to the exact
recovered strict builder, then pins the complete remaining serialized manifest.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('type3_small_strict_builder',ROOT/'prototype/build-type3-small-art.py')
strict=importlib.util.module_from_spec(spec);spec.loader.exec_module(strict)
PARENT_SHA256='b99c5454f9c2e4d1edbed0356cfeecd60978f71b746855b1193daa12179f0f7a'

def project_type3_small_family(test,manifest):
    try:
        source=ROOT/strict.SOURCE
        frozen=strict.inventory(source)
        strict.validate_art_and_bindings(ROOT,source,manifest,frozen)
    except (ValueError,KeyError,TypeError,OSError) as error:
        test.fail(str(error))
    family=manifest.pop('type3_small_six_v1')
    for entry in family['entries']:
        name=f"enemy-newsh2-{entry['id']}-8.hda"
        for pack in [manifest['default_preview_pack'],manifest['default_debug_pack']]:
            manifest['packs'][pack]['files'].pop(name)
            manifest['packs'][pack]['count']-=1
        manifest['source_pngs'].pop(entry['HDA_sha256'])
    test.assertEqual(hashlib.sha256((json.dumps(manifest,indent=2)+'\n').encode()).hexdigest(),PARENT_SHA256)
