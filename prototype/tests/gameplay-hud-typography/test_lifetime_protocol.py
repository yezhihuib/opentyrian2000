#!/usr/bin/env python3
"""Reference history protocol only. No game hooks, resources, or renderer code."""
from dataclasses import dataclass
import unittest

STREAMS={'cash':('scene','cash-full-shade'), 'player-name':('scene','name-full-shade'),
         'level':('persistent','level-setup'), 'message':('persistent','message-window')}

@dataclass(frozen=True)
class Record:
 generation:int
 frame:int
 callsite:str
 text:bytes
 indexed_result:bytes

class HistoryModel:
 """Observer authority is separate from equal pixels and simulated game state."""
 def __init__(self):
  self.generation=0;self.frame=0;self.active=False;self.suspended=False;self.lease=None
  self.records={};self.poisoned=set()
 def grant_pic3(self,lease):
  self.revoke();self.lease=lease;self.active=True
 def revoke(self):
  self.generation+=1;self.active=False;self.suspended=False;self.lease=None
  self.records.clear();self.poisoned.clear()
 def validate(self,lease,mode='single'):
  if self.active and (lease!=self.lease or mode!='single'):self.revoke()
  return self.active
 def begin(self,lease,mode='single'):
  if not self.validate(lease,mode):return
  self.frame+=1;self.suspended=False
  for stream in tuple(self.records):
   if STREAMS[stream][0]=='scene':del self.records[stream]
 def suspend(self,lease):
  if self.validate(lease):self.suspended=True
 def draw_completed(self,stream,callsite,text,indexed_result,lease,*,supported=True,fits=True):
  if not self.validate(lease):return False
  if stream not in STREAMS or callsite!=STREAMS[stream][1]:return False
  if not supported or not fits:
   self.records.pop(stream,None)
   # Unknown persistent history cannot be repaired by future short strings.
   if STREAMS[stream][0]=='persistent':self.poisoned.add(stream)
   return False
  if stream in self.poisoned:return False
  self.records[stream]=Record(self.generation,self.frame,callsite,text,indexed_result)
  return True
 def erase_completed(self,stream,lease):
  if self.validate(lease):self.records.pop(stream,None)
  # Original rectangle erasure does not establish that out-of-bounds remnants
  # from an unsupported prior run disappeared. Poison needs a fresh PIC grant.
 def eligible(self,stream,current_indices,lease):
  if not self.validate(lease) or self.suspended or stream in self.poisoned:return False
  r=self.records.get(stream)
  return bool(r and r.generation==self.generation and
              (STREAMS[stream][0]!='scene' or r.frame==self.frame) and
              current_indices==r.indexed_result)

class OriginalMessageFixture:
 """Test-side original textErase clock; the observer never changes this state."""
 def __init__(self,observer,lease):self.observer=observer;self.lease=lease;self.text_erase=0;self.erase_count=0
 def draw(self,text,indexed_result,*,fits=True):
  if self.text_erase>0:self.erase()
  self.text_erase=100
  return self.observer.draw_completed('message','message-window',text,indexed_result,self.lease,fits=fits)
 def erase(self):self.erase_count+=1;self.observer.erase_completed('message',self.lease)
 def tick(self,end_level=False):
  if not end_level and self.text_erase>0:
   self.text_erase-=1
   if self.text_erase==0:self.erase()

def blend(dst,rgb,alpha):return tuple((d*(255-alpha)+s*alpha+127)//255 for d,s in zip(dst,rgb))

def paint(canvas,origin,coverage,color):
 out=list(canvas)
 for local,alpha in enumerate(coverage):
  if 0<=origin+local<len(out):out[origin+local]=blend(out[origin+local],color,alpha)
 return out

class Tests(unittest.TestCase):
 def setUp(self):self.h=HistoryModel();self.lease=('surface','pixels','format',320,200,320,8);self.h.grant_pic3(self.lease);self.h.begin(self.lease)
 def test_equal_pixels_do_not_authorize_history(self):
  pixels=b'same indexed raster'
  for stream in STREAMS:self.assertFalse(self.h.eligible(stream,pixels,self.lease))
  self.assertTrue(self.h.draw_completed('cash','cash-full-shade',b'99',pixels,self.lease))
  self.assertTrue(self.h.eligible('cash',pixels,self.lease))
  self.h.begin(self.lease);self.assertFalse(self.h.eligible('cash',pixels,self.lease))
  self.h.draw_completed('level','level-setup',b'TYRIAN',pixels,self.lease);self.h.grant_pic3(self.lease)
  self.assertFalse(self.h.eligible('level',pixels,self.lease))
 def test_scene_draw_records_actual_formatted_value(self):
  self.h.draw_completed('cash','cash-full-shade',b'9',b'nine',self.lease)
  game_cash=10  # Later globals are irrelevant to the observer's recorded draw.
  self.assertEqual(self.h.records['cash'].text,b'9');self.assertEqual(game_cash,10)
  self.assertTrue(self.h.eligible('cash',b'nine',self.lease));self.assertFalse(self.h.eligible('cash',b'ten',self.lease))
  self.h.begin(self.lease);self.h.draw_completed('cash','cash-full-shade',b'10',b'ten',self.lease)
  self.assertTrue(self.h.eligible('cash',b'ten',self.lease))
 def test_callsite_context_and_lease_are_authority(self):
  for wrong in ('shop-score','menu-font','help-prompt','generic-JE_outText','results'):
   self.assertFalse(self.h.draw_completed('cash',wrong,b'0',b'0',self.lease))
  self.h.draw_completed('cash','cash-full-shade',b'0',b'0',self.lease)
  for field in range(len(self.lease)):
   self.setUp();self.h.draw_completed('cash','cash-full-shade',b'0',b'0',self.lease)
   replacement=tuple('replacement' if i==field else x for i,x in enumerate(self.lease))
   self.assertFalse(self.h.eligible('cash',b'0',replacement));self.assertFalse(self.h.active)
  for mode in ('two-player','galaga','shop','results'):
   self.setUp();self.assertFalse(self.h.validate(self.lease,mode))
 def test_persistent_message_clock_erase_and_endlevel(self):
  original=OriginalMessageFixture(self.h,self.lease);self.assertTrue(original.draw(b'First',b'first'))
  for _ in range(99):original.tick()
  self.assertEqual(original.text_erase,1);self.assertTrue(self.h.eligible('message',b'first',self.lease))
  for _ in range(200):original.tick(end_level=True)
  self.assertEqual(original.text_erase,1);self.assertTrue(self.h.eligible('message',b'first',self.lease))
  original.tick();self.assertFalse(self.h.eligible('message',b'first',self.lease));self.assertEqual(original.erase_count,1)
  original.draw(b'Longer text',b'longer');original.draw(b'Short',b'short')
  self.assertEqual(original.erase_count,2);self.assertEqual(original.text_erase,100)
  self.assertFalse(self.h.eligible('message',b'longer',self.lease));self.assertTrue(self.h.eligible('message',b'short',self.lease))
 def test_overflow_history_stays_coherent_classic(self):
  original=OriginalMessageFixture(self.h,self.lease)
  classic=bytearray(b'old indexed pixels outside erase box')
  before=bytes(classic)
  self.assertFalse(original.draw(b'X'*255,b'overflow raster',fits=False));self.assertIn('message',self.h.poisoned)
  self.assertFalse(original.draw(b'Short',b'short'));self.assertFalse(self.h.eligible('message',b'short',self.lease))
  for _ in range(100):original.tick()
  self.assertIn('message',self.h.poisoned);self.assertEqual(bytes(classic),before)
  self.assertTrue(self.h.draw_completed('level','level-setup',b'LEVEL',b'level',self.lease))
  self.assertTrue(self.h.eligible('level',b'level',self.lease))
  self.h.grant_pic3(self.lease);self.h.begin(self.lease);self.assertTrue(original.draw(b'Short',b'short'))
 def test_suspend_resume_and_help_expiry(self):
  original=OriginalMessageFixture(self.h,self.lease);original.draw(b'Good luck...',b'message')
  self.h.draw_completed('cash','cash-full-shade',b'0',b'cash',self.lease)
  self.h.suspend(self.lease);self.h.suspend(self.lease)
  self.assertFalse(self.h.eligible('message',b'message',self.lease))
  # A modal may restore its original backing raster, or leave a prompt to erase.
  self.h.begin(self.lease);self.assertTrue(self.h.eligible('message',b'message',self.lease));self.assertFalse(self.h.eligible('cash',b'cash',self.lease))
  self.assertFalse(self.h.eligible('message',b'press a key',self.lease))
  original.text_erase=1;original.tick();self.assertNotIn('message',self.h.records)
 def test_unsupported_role_is_whole_run_fallback(self):
  self.h.draw_completed('cash','cash-full-shade',b'99',b'99',self.lease)
  self.assertFalse(self.h.draw_completed('cash','cash-full-shade',b'99',b'99',self.lease,supported=False));self.assertFalse(self.h.eligible('cash',b'99',self.lease))
  self.h.begin(self.lease);self.assertTrue(self.h.draw_completed('cash','cash-full-shade',b'100',b'100',self.lease))
 def test_transparency_needs_real_lower_layer(self):
  lower=[(20+i*17,50+i*9,90+i*5) for i in range(8)]
  authored_coverage=[0,80,255,0,0,255,80,0];green=(125,158,89)
  desired=paint(lower,0,authored_coverage,green)
  self.assertEqual(desired[0],lower[0]);self.assertEqual(desired[3],lower[3]);self.assertNotEqual(desired[1],(0,0,0))
  # An opaque plate hides the scene; a final-classic overlay leaves old ink in
  # newly transparent holes. Neither is a valid general dynamic-text renderer.
  plate=paint([(0,0,0)]*8,0,authored_coverage,green);self.assertNotEqual(plate,desired)
  classic=paint(lower,0,[0,255,255,255,255,255,255,0],(39,89,28))
  overlay=paint(classic,0,authored_coverage,green);self.assertNotEqual(overlay,desired)
  # Exact captured pre-text underlay plus authored transparency preserves holes.
  recovered=paint(list(lower),0,authored_coverage,green);self.assertEqual(recovered,desired)

if __name__=='__main__':unittest.main(verbosity=2)
