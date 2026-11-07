#!/usr/bin/env python3
"""Read-only offline fork284 input check. Does not enable or launch rendering."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / 'assets/hd/packs/asteroid1-ten-v1/enemy-newshd-121-8.hda'
ASSET_SHA256 = '65609c1c9d7cc981faecc914ada8e1100c550047733967ba7ae4b3635fdd1dad'
ASSET_FNV64 = 0x56eb78103f545e7e
STREAM_FNV64 = 0xa6df39659b2d348d
MAX_LEVEL_BYTES = 16 * 1024 * 1024
ORIGINS = ((12,140,70),(13,140,280),(14,160,120),(15,160,230))


def fnv64(data):
    h = 14695981039346656037
    for value in data:
        h = ((h ^ value) * 1099511628211) & ((1 << 64) - 1)
    return h


def read_bounded(path, limit):
    # The capped read also bounds memory if the file grows after stat().
    with path.open('rb') as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f'{path.name}: file exceeds {limit}-byte limit')
    return data


def parse_events(data):
    """Native lvlPos[(physical-1)*2], then <cc3H>, enemy list, <H> events."""
    if len(data) < 2:
        raise ValueError('tyrian1.lvl: truncated offset count')
    count = struct.unpack_from('<H', data)[0]
    header_end = 2 + count * 4
    if count < 4 or header_end > len(data):
        raise ValueError('tyrian1.lvl: incomplete offset table')
    offsets = struct.unpack_from(f'<{count}i', data, 2)
    if any(p < header_end or p > len(data) for p in offsets) or any(a >= b for a,b in zip(offsets,offsets[1:])):
        raise ValueError('tyrian1.lvl: invalid or unordered offsets')
    pos, end = offsets[2], offsets[3]

    def take(size):
        nonlocal pos
        if size < 0 or pos + size > end:
            raise ValueError('tyrian1.lvl: truncated physical-2 event section')
        result = data[pos:pos+size]
        pos += size
        return result

    if struct.unpack('<cc3H', take(8)) != (b'D', b'Z', 1, 1, 1):
        raise ValueError('tyrian1.lvl: physical-2 map/shape/origin mismatch')
    enemies = struct.unpack('<H', take(2))[0]
    take(enemies * 2)
    event_count = struct.unpack('<H', take(2))[0]
    if event_count != 731:
        raise ValueError('tyrian1.lvl: expected exactly 731 events')
    return take(event_count * 11)


def inspect_stream(raw):
    digest = fnv64(raw)
    if digest != STREAM_FNV64:
        raise ValueError('tyrian1.lvl: full 731-event stream hash mismatch')
    rows = list(struct.iter_unpack('<HBhhbbbB', raw))
    for number,time,x in ORIGINS:
        if rows[number-1] != (time,7,284,x,2,0,0,0):
            raise ValueError('tyrian1.lvl: fork284 origin fields mismatch')
    if [i+1 for i,r in enumerate(rows) if r[1] in (6,7) and r[2] == 284] != [r[0] for r in ORIGINS]:
        raise ValueError('tyrian1.lvl: unexpected fork284 creation origins')
    return {'event_count':731, 'stream_fnv64':f'{digest:016x}',
            'stream_sha256':hashlib.sha256(raw).hexdigest(),
            'four_origins_match':True, 'origin_numbers_one_based':[r[0] for r in ORIGINS]}


def inspect_asset(data):
    if len(data) != 172060 or data[:4] != b'HDR1':
        raise ValueError('fork284 asset: invalid size or HDR1 magic')
    if struct.unpack('<6I', data[4:28]) != (1080121,8,24,28,0,0):
        raise ValueError('fork284 asset: header mismatch')
    sha = hashlib.sha256(data).hexdigest()
    payload_hash = fnv64(data[28:])
    if sha != ASSET_SHA256 or payload_hash != ASSET_FNV64:
        raise ValueError('fork284 asset: SHA256 or payload FNV64 mismatch')
    alpha = data[31::4]
    return {'bytes':len(data), 'sha256':sha, 'payload_fnv64':f'{payload_hash:016x}',
            'alpha_pixels':{'transparent':alpha.count(0), 'opaque':alpha.count(255),
                            'partial':len(alpha)-alpha.count(0)-alpha.count(255)}}


def preflight(data_directory):
    level = read_bounded(Path(data_directory).expanduser().resolve() / 'tyrian1.lvl', MAX_LEVEL_BYTES)
    events = inspect_stream(parse_events(level))
    asset = inspect_asset(read_bounded(ASSET, 172060))
    return {'status':'PASS', 'scope':'Offline E1 physical-2 ASTEROID2 input check only',
            'level_file_sha256':hashlib.sha256(level).hexdigest(), 'events':events, 'asset':asset,
            'runtime_integrated':False, 'game_started':False, 'files_written':False,
            'limits':'No full level/map, runtime, visual, audio or gameplay validation.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True, help='Existing original data directory containing tyrian1.lvl')
    args = parser.parse_args(argv)
    try:
        result = preflight(args.data)
    except (OSError, ValueError, struct.error) as error:
        print(json.dumps({'status':'FAIL','error':str(error),'game_started':False,'files_written':False}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
