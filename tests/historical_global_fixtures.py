"""Immutable original registry bytes: independent anchors, no local Git history needed."""
import hashlib
import json
from pathlib import Path

FIXTURES = Path(__file__).parent / 'fixtures/historical-global-registry-v1'
# These anchors are extracted from original Git objects, never from current files.
REGISTRY_ANCHORS = {'ee1e98cfc6b8c00cb9a1837e4aa2c3a9aca2b0e5': {'git_blob': '09299e928ffeb52f5472423443961547a43b8cf1',
                                              'sha256': 'f06217ef4e0ba443227b584d98e18df245d4014964a97573956b2c993f0a3ba3',
                                              'bytes': 101238},
 '42453a546c79bcb0de6fc4c09b8370adf90660f8': {'git_blob': '8fb05f8a20f23d7f94e0d69df4d91d1871b28cbf',
                                              'sha256': '70d76c54559838eec3be124476c5cfb4a715fad80d8d2d9d73e82a84d8fe811c',
                                              'bytes': 112999},
 '983c34f14aac9f8586f6c8d466439c06e7a3b389': {'git_blob': '91606aa5734e4c1bc33138f5191f0f4a81f2fa36',
                                              'sha256': 'ed2a7e43270e37fc87ce7c4acef022bef252a5d96c9cdf67f16d161f90bfb090',
                                              'bytes': 136649},
 'd5b08f5d9cde1dea43819daaa8a52bc8f211e20b': {'git_blob': '544d7e0789bd751340ea8a5078dacbe2e239a75b',
                                              'sha256': 'a8fcabb6b2b3d377f4dc3c21e1d39a2debb7db48531c9d4ee6c890c0dfac0d01',
                                              'bytes': 181290},
 'd418bc85e3033936a1f8d263679aeaba0e3640b7': {'git_blob': 'e64d5db5fd5082e6769f35e7f1c9b4cc7c49c435',
                                              'sha256': 'ea4379fc7c3486a950c0862b0589083a2663acd0533cc26e0b99af097aedf5a9',
                                              'bytes': 159377},
 'c94acb347c610a0320386dc3a2ee83c1f273a776': {'git_blob': '8303cc996c9c2921191a87fc067f9ecce95863da',
                                              'sha256': 'bb9163a9de3026ce91eabe5be3b74bf4ef53eba42c7991276a55c33bc6ae598f',
                                              'bytes': 85028},
 'bdea6e3d726c544e36198f08e9d8ca055642d940': {'git_blob': 'f612a6e145d1ae8990ae96bd92aa4ee017283cdb',
                                              'sha256': 'efd9ab269b20bb4d2c84345019928095f9f174ccc7ee9b7ac0a4054265b7e39d',
                                              'bytes': 204009}}
PULSE_BASELINE = 'bdea6e3d726c544e36198f08e9d8ca055642d940'
RECEIPT_ANCHORS = {'packaging/global-validation.json': {'git_blob': '770601794086f7ee3050316feb0d6f2e06d4a663',
                                      'sha256': '9b0706f0b8baaa7823f1c61b04230999c2edb1b47e2312eac33f493fe255e036',
                                      'bytes': 23743},
 'packaging/frontend-validation.json': {'git_blob': 'ed568f2f6da98eecca93a947e8c2904790b3a3dd',
                                        'sha256': '85fbbfaa5e14288c07664448106732508b617cb38ebddb5145d490416670cd1f',
                                        'bytes': 23514},
 'assets/hd/manifest.json': {'git_blob': '57e983b6860771983e1851297f29e801ed3575b0',
                             'sha256': '24b2a920f2c889c56ce3d29811679228bcb9ddf45067fc9488e1aef414527f9a',
                             'bytes': 2108708},
 'docs/PULSE_UPGRADE_VALIDATION.json': {'git_blob': 'e20e3e924611c656378c8862bcb94f2cda231c76',
                                        'sha256': 'ebe8369951ffd7bb0e72a2a2aa5d7784a0cbac5b2781c22c4dbd93c0116ea97e',
                                        'bytes': 10115},
 'docs/PULSE_UPGRADE_VALIDATION.md': {'git_blob': '8237462b9b2910237d713b6a92abc73f23404c91',
                                      'sha256': 'b46bce45a66179dc66fb0c583a2d5b3781f8c2b44af3d26afaaf2bb56b223d94',
                                      'bytes': 2765},
 'tests/global_talon_validation.json': {'git_blob': 'fc9c224843d6b942697e3876e119c99297aca464',
                                        'sha256': 'f292f64f1d6cf0f40396ea5c1b54ae1a32052d9a723d49e8a1fee2719f760061',
                                        'bytes': 15254}}

def verify_original_bytes(data, anchor):
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
    if len(data) != anchor['bytes'] or hashlib.sha256(data).hexdigest() != anchor['sha256'] or blob != anchor['git_blob']:
        raise ValueError('Historical bytes do not match independently pinned original Git object')
    return data

def registry_at(commit, directory=FIXTURES):
    anchor = REGISTRY_ANCHORS[commit]
    return json.loads(verify_original_bytes((Path(directory) / (commit + '.json')).read_bytes(), anchor))

def verify_historical_receipt(commit, path, data):
    if commit != PULSE_BASELINE:
        raise ValueError('Unapproved historical baseline')
    verify_original_bytes(data, RECEIPT_ANCHORS[path])
