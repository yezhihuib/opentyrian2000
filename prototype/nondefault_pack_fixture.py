"""Metadata-only nondefault pack fixtures for ownership rejection tests."""
import copy


NONDEFAULT_PACK = 'test-only-nondefault-pack'
ARCHIVED_RECIPE = 'packed-talon13-foundation-type10-explosion-v2-test'


def add_nondefault_pack_fixture(manifest):
    """Clone an archived recipe into a caller-owned mutation manifest.

    No retired installed directory is restored. The synthetic pack owns an
    independent copy so a negative test cannot mutate the retained recipe.
    """
    assert NONDEFAULT_PACK not in manifest['packs']
    assert NONDEFAULT_PACK not in manifest['retired_packs']
    assert NONDEFAULT_PACK not in (manifest['default_preview_pack'],
                                  manifest['default_debug_pack'])
    recipe = manifest['retired_packs'][ARCHIVED_RECIPE]
    assert recipe['count'] == len(recipe['files'])
    manifest['packs'][NONDEFAULT_PACK] = copy.deepcopy(recipe)
    return NONDEFAULT_PACK
