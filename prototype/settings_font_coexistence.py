"""Finite settings-only coexistence view for older source-preservation tests.

Every complete input file is pinned BEFORE exact reverse line edits. No broad
pattern stripping, ignored delta, runtime mutation, or fixture allowance exists.
The projected result is pinned to published 5629b3d. Production tests compile the
real combined source, and tests/test_settings_integration.py independently checks
all original tracked bytes and modes plus both merge-parent source deltas.
"""
import base64,hashlib
PINS = {'src/opentyr.c': {'current': 'e832723fdcbf743035dede701a1a392f671e2168af64e1220e0eadc97ba0a71e',
                   'previous': 'ca0b39a0462dbfc1832464f8f898efc2509b75277ff13b12504937e640ba5dac',
                   'reverse_line_edits': [[18, 19, ''],
                                          [207, 208, ''],
                                          [212, 213, ''],
                                          [217, 218, ''],
                                          [219, 220, ''],
                                          [248, 249, ''],
                                          [250, 251, ''],
                                          [262, 263, ''],
                                          [264, 265, ''],
                                          [268, 269, ''],
                                          [270, 271, ''],
                                          [274, 275, ''],
                                          [276, 277, ''],
                                          [280, 281, ''],
                                          [283, 284, ''],
                                          [287, 288, ''],
                                          [290, 291, ''],
                                          [299, 300, ''],
                                          [301, 302, ''],
                                          [313, 314, ''],
                                          [318, 319, ''],
                                          [328, 329, ''],
                                          [330, 331, ''],
                                          [333, 335, ''],
                                          [347, 348, ''],
                                          [349, 350, ''],
                                          [352, 353, ''],
                                          [577, 578, ''],
                                          [589, 590, ''],
                                          [644, 645, ''],
                                          [769, 770, '']]},
 'src/palette.c': {'current': '5bbac8824c320b6c398fce427a13f676f6c84295661a0450a6e331fd2cfddf13',
                   'previous': 'c076602374cdac53e673af718dc7d0a7ad9e5c13aa353acfeae88d46f2674542',
                   'reverse_line_edits': [[18, 19, ''], [95, 96, ''], [109, 110, ''], [140, 141, '']]},
 'src/params.c': {'current': '4cb7868e6dcbac1489386db214093461c923405c1e072f9fc9beaa4fe5bb893a',
                  'previous': '05dc1ffcf56b0cb330ca3c9879f5724f1ad1a1dda78084fe6f312012e8e9295c',
                  'reverse_line_edits': [[18, 19, ''], [136, 137, '']]},
 'src/picload.c': {'current': 'a0c1eb3c819812568bfe0ce01c733d98686d0332d9a003bdb380b9bb7f4f0dbe',
                   'previous': '4b9abc38a65dcb000f1bcf5512763c9721fb7edd345a9097a8f3c2c8682ad6e4',
                   'reverse_line_edits': [[18, 19, ''], [37, 38, '']]},
 'src/render_mirror.c': {'current': 'dca16632259069a08b98788476163a9f5e681536c0e04edd8750bd540702841b',
                         'previous': '7a39ffd4959c307c23707ae63c41030cd92ef757375b95f680445ff4f3e85420',
                         'reverse_line_edits': [[5, 6, ''],
                                                [128, 129, ''],
                                                [1029, 1030, ''],
                                                [1083, 1084, '']]},
 'src/render_mirror.h': {'current': '5b0e97f7095f1eb60ec12e749b846c7d702127bd2373a98a4eb7d911b9d72e40',
                         'previous': '5d855c6c01621f061d669ac03d37e799aee6194a37c880102b2d3be7324d2ed6',
                         'reverse_line_edits': [[8, 9, ''], [53, 54, '']]},
 'src/sprite.c': {'current': '89e2d9cca65dc2f0ef0f785b94da5c75127b80822ccf8fd593cf442b08008d96',
                  'previous': 'b912773976c4b745f355d471b4da6a4ea25907e7bf80eb7356c9a59ae361237c',
                  'reverse_line_edits': [[18, 19, ''],
                                         [94, 95, ''],
                                         [235, 236, ''],
                                         [240,
                                          241,
                                          'CQl7IHJlbmRlcl9taXJyb3JfdGV4dF9nbHlwaF9lbmQoKTsgcmV0dXJuOyB9Cg=='],
                                         [280,
                                          281,
                                          'CQkJCXsgcmVuZGVyX21pcnJvcl90ZXh0X2dseXBoX2VuZCgpOyByZXR1cm47IH0K'],
                                         [295, 296, ''],
                                         [301, 302, ''],
                                         [305, 306, 'CQlyZXR1cm47Cg=='],
                                         [345, 346, 'CQkJCXJldHVybjsK'],
                                         [365, 366, ''],
                                         [439, 440, ''],
                                         [444,
                                          445,
                                          'CQl7IHJlbmRlcl9taXJyb3JfdGV4dF9nbHlwaF9lbmQoKTsgcmV0dXJuOyB9Cg=='],
                                         [482,
                                          483,
                                          'CQkJCXsgcmVuZGVyX21pcnJvcl90ZXh0X2dseXBoX2VuZCgpOyByZXR1cm47IH0K'],
                                         [497, 498, ''],
                                         [571, 572, ''],
                                         [580, 581, 'CQkJcmV0dXJuOwo='],
                                         [610, 611, '']]},
 'src/startup_logos.c': {'current': '6db4730cef41cda023fe854b39070af6a0b531b82009ec6bdd4a2504a3750128',
                         'previous': '114b09b922ddb752e8741a8839ef852849867856b31368fce9b62e263aeecb67',
                         'reverse_line_edits': [[59, 60, '']]},
 'src/startup_logos.h': {'current': '5ddd20f33596b526c6e12a2c8d5fefcdc7dc293464b1432bd43b561f1f5e9a43',
                         'previous': 'c6434face8b00574b868c76cec825725ff4f041016a99cf2d80d2c16b270d480',
                         'reverse_line_edits': [[7, 8, '']]},
 'src/title_layers.c': {'current': '96baba45f796e808b30a5ae571c727735e282fe23396c9579b992ca5187a3ce5',
                        'previous': '58691e41f8183e7f45c3c4b85ecb80cf835ae43413e9cf03ba10595d22eb6c5c',
                        'reverse_line_edits': [[93, 94, '']]},
 'src/title_layers.h': {'current': '96fcf5a15aa10928eb067e329d46be10effd685df19406a9d8c627fdf07328a7',
                        'previous': 'be304a77f1d244b192e631dde633c239ea64e0de0185ef7ae2b635afb57b41e4',
                        'reverse_line_edits': [[8, 9, '']]},
 'src/video.c': {'current': '696e307785cfdd26803539c8aa104e62d5d0f21b01efa4efab299472bacb5d4e',
                 'previous': '8b6e30c1829bdcad27f0107eed599838a51f61c626f31339e13daaee128a300f',
                 'reverse_line_edits': [[18, 19, ''],
                                        [122, 123, ''],
                                        [152, 153, ''],
                                        [181, 182, ''],
                                        [213, 214, ''],
                                        [242, 243, ''],
                                        [328, 329, ''],
                                        [414, 415, '']]},
 'visualc/opentyrian.vcxproj': {'current': 'baa2c8012c80838e3171632956f26a636e54f486754d6aea647b066646b23302',
                                'previous': '3b1980e5ae20ceec1d84613e25a24faf22567462091bfb835ecb1e4052ad6f6c',
                                'reverse_line_edits': [[152, 153, ''], [222, 223, '']]}}
ADDITIONS = {'assets/hd/artwork/settings-font-v1/canonical/manifest.json': '02eb238970f464e90ae08ef335dc02ab129133f78d096e62732e93a3eec192db',
 'assets/hd/artwork/settings-font-v1/canonical/settings-font-large-v1.hda': '7827555a736375ff45bd78dc2c05c5651e65d3b024527e8dba525d3beff721e5',
 'assets/hd/artwork/settings-font-v1/canonical/settings-font-medium-v1.hda': '51852f5d54516de70a5729e991fb14104871b9ad58991f0352899ab4502bd484',
 'assets/hd/artwork/settings-font-v1/canonical/settings-font-tiny-v1.hda': '888b635af0c123dc77fecf2f50a2e603f85a0fb6ad74a1c4215b29affc28a35c',
 'src/settings_font.c': 'e56c3aa886b1a8440582729e656017e213b2ca56592d387f0ab7401dd186f875',
 'src/settings_font.h': 'c4c6791adb92be4c650123f6034ebb8103fa841f9e79a7eff450ec8e6245195d'}
def project_settings_source(path,raw):
    pin=PINS.get(path)
    if pin is None:return raw
    digest=hashlib.sha256(raw).hexdigest()
    if digest==pin['previous']:return raw # Historical fixture without SFN1.
    assert digest==pin['current'],'Unreviewed settings/source coexistence bytes: '+path
    lines=raw.splitlines(keepends=True)
    for start,end,previous in reversed(pin['reverse_line_edits']):
        lines[start:end]=base64.b64decode(previous).splitlines(keepends=True)
    result=b''.join(lines)
    assert hashlib.sha256(result).hexdigest()==pin['previous'],path
    return result

def verify_settings_sources(root):
    for path,pin in PINS.items():
        raw=(root/path).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==pin['current'],path
        project_settings_source(path,raw)
    for path,digest in ADDITIONS.items():
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
    return len(PINS),len(ADDITIONS)


def project_settings_family(test,manifest):
    from pathlib import Path
    from settings_font_bundle import build_bundles
    root=Path(__file__).resolve().parents[1]
    _,family=build_bundles(root)
    test.assertEqual(manifest.pop('startup_settings_font_v1'),family)
    from startup_manufacturer_bundle import project_retired_resources_for_historical_checks
    try:project_retired_resources_for_historical_checks(manifest)
    except ValueError as error:test.fail(str(error))
    test.assertEqual(hashlib.sha256((__import__('json').dumps(manifest,indent=2)+'\n').encode()).hexdigest(),'aebd2582950fa2c1d9b25ce4f0a1ec649f2dd6ff382432238624c9634e697d80')
