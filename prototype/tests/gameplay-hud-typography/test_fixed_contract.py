#!/usr/bin/env python3
"""Synthetic HUT1 protocol oracle only; no production loader or artwork."""
import struct,unittest
from dataclasses import dataclass

RECTS=((284,54,19,5),)+tuple((285,138+6*i,5,5) for i in range(6))+tuple((296,138+6*i,5,5) for i in range(5))
POINTS=tuple((x+dx,y+dy) for x,y,w,h in RECTS for dy in range(h) for dx in range(w))
GROUPS=(tuple(range(95)),tuple(range(95,245)),tuple(range(245,370)))
HEADER=struct.Struct('<4s7I4Q');PAYLOAD=370*4*4*4;TOTAL=HEADER.size+PAYLOAD

def fnv(b):
 h=14695981039346656037
 for x in b:h=((h^x)*1099511628211)&((1<<64)-1)
 return h

def select(source):return bytes(source[y*320+x] for x,y in POINTS)

def fixture():
 source=bytes(i%253 for i in range(64000));palette=bytes(i%256 for i in range(768));rgba=bytes(c for i in range(PAYLOAD//4) for c in ((i*7)%256,(i//13)%256,(i//37)%256,255))
 guards=(fnv(source),fnv(palette),fnv(select(source)))
 return source,palette,rgba,guards,HEADER.pack(b'HUT1',1,4,12,370,PAYLOAD,1,0,*guards,fnv(rgba))+rgba

@dataclass
class FixedContract:
 """Proposed bounded loader semantics; not linked to the game."""
 rgba:bytes
 guards:tuple
 captured:bytes|None=None
 @classmethod
 def parse(cls,raw,guards):
  if raw is None or len(raw)!=TOTAL:raise ValueError('exact finite length required')
  h=HEADER.unpack_from(raw)
  if h[:8]!=(b'HUT1',1,4,12,370,PAYLOAD,1,0) or h[8:11]!=guards:raise ValueError('unsupported header/source')
  rgba=raw[64:]
  if fnv(rgba)!=h[11] or any(v!=255 for v in rgba[3::4]):raise ValueError('corrupt/nonopaque payload')
  return cls(rgba,guards)
 def capture(self,source):
  self.captured=None
  if len(source)!=64000:return False
  if (fnv(source),fnv(select(source)))!=(self.guards[0],self.guards[2]):return False
  self.captured=select(source);return True
 def palette_matches(self,palette):
  return len(palette)==768 and fnv(palette)==self.guards[1]
 def allowed_groups(self,current):
  if self.captured is None or len(current)!=64000:return set()
  values=select(current)
  return {group for group,offsets in enumerate(GROUPS) if all(values[i]==self.captured[i] for i in offsets)}
 def sample(self,x,y,sx,sy,d,groups):
  if self.captured is None or d not in (4,8) or not(0<=sx<d and 0<=sy<d):return None
  source_offset=tile_offset=0
  for tile,(left,top,w,h) in enumerate(RECTS):
   if left<=x<left+w and top<=y<top+h:
    group=0 if tile==0 else 1 if tile<=6 else 2
    if group not in groups:return None
    i=tile_offset+(((y-top)*4+sy//(d//4))*w*4+(x-left)*4+sx//(d//4))*4
    return self.rgba[i:i+4]
   source_offset+=w*h;tile_offset+=w*h*64
  return None

class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.source,cls.palette,cls.rgba,cls.guards,cls.raw=fixture()
 def fresh(self):
  a=FixedContract.parse(self.raw,self.guards);self.assertTrue(a.capture(self.source));return a
 def test_exact_finite_geometry(self):
  self.assertEqual((len(POINTS),len(set(POINTS)),HEADER.size,PAYLOAD,TOTAL),(370,370,64,23680,23744))
  self.assertTrue(all(x>=264 and 0<=x<320 and 0<=y<200 for x,y in POINTS))
  self.assertFalse(any((285,y) in POINTS for y in (143,149,155,161,167)))
  a=self.fresh();groups=a.allowed_groups(self.source)
  self.assertEqual(groups,{0,1,2})
  actual={(x,y) for y in range(200) for x in range(320) if a.sample(x,y,0,0,4,groups)}
  self.assertEqual(actual,set(POINTS))
 def test_registration_and_density_repeat(self):
  a=self.fresh();groups={0,1,2};offset=0
  for x,y,w,h in RECTS:
   for dy in range(h):
    for dx in range(w):
     for sy in range(4):
      for sx in range(4):
       i=offset+((dy*4+sy)*w*4+dx*4+sx)*4;want=self.rgba[i:i+4]
       self.assertEqual(a.sample(x+dx,y+dy,sx,sy,4,groups),want)
       for ry in range(2):
        for rx in range(2):self.assertEqual(a.sample(x+dx,y+dy,sx*2+rx,sy*2+ry,8,groups),want)
   offset+=w*h*64
  for d in (-1,0,1,2,3,5,16):self.assertIsNone(a.sample(284,54,0,0,d,groups))
  for sx,sy in ((-1,0),(0,-1),(4,0),(0,4)):self.assertIsNone(a.sample(284,54,sx,sy,4,groups))
 def test_every_owned_index_coherent_group_fallback(self):
  a=self.fresh()
  for i,(x,y) in enumerate(POINTS):
   changed=bytearray(self.source);changed[y*320+x]^=1;group=0 if i<95 else 1 if i<245 else 2
   self.assertEqual(a.allowed_groups(changed),{0,1,2}-{group})
  self.assertEqual(a.allowed_groups(self.source),{0,1,2})
  a.captured=None;self.assertEqual(a.allowed_groups(self.source),set())
 def test_malformed_missing_and_source(self):
  for raw in (None,b'',self.raw[:63],self.raw[:-1],self.raw+b'\0',self.raw*2):
   with self.assertRaises(ValueError):FixedContract.parse(raw,self.guards)
  for offset in range(64):
   raw=bytearray(self.raw);raw[offset]^=1
   with self.assertRaises(ValueError):FixedContract.parse(raw,self.guards)
  for alpha in range(255):
   raw=bytearray(self.raw);raw[67]=alpha;struct.pack_into('<Q',raw,56,fnv(raw[64:]))
   with self.assertRaises(ValueError):FixedContract.parse(raw,self.guards)
  raw=bytearray(self.raw);raw[-4]^=1
  with self.assertRaises(ValueError):FixedContract.parse(raw,self.guards)
  a=self.fresh();source=bytearray(self.source);source[0]^=1;self.assertFalse(a.capture(source));self.assertIsNone(a.captured)
  palette=bytearray(self.palette);palette[0]^=1;self.assertFalse(a.palette_matches(palette))
  self.assertFalse(a.capture(self.source[:-1]));self.assertFalse(a.palette_matches(self.palette[:-1]))

if __name__=='__main__':unittest.main(verbosity=2)
